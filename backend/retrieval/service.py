"""
DB-First Retrieval Service — TaxLegal v4

CRITICAL BUSINESS RULE:
1. ALWAYS query internal DB first (taxlegal.law_documents_v2 + dbvntax)
2. ONLY if DB returns no results, use Perplexity fallback
3. NEVER fabricate tax law
4. ALWAYS record source_type, trust_level, citation, retrieval_method
5. If coverage is insufficient, return "insufficient source coverage"
"""
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)


# ── Dataclasses ────────────────────────────────────────────────────────────────

@dataclass
class RetrievalResult:
    query: str
    db_results: list = field(default_factory=list)
    web_results: list = field(default_factory=list)
    used_fallback: bool = False
    insufficient_coverage: bool = False
    answer: str = ""
    citations: list = field(default_factory=list)
    total_results: int = 0


# ── Internal DB query ──────────────────────────────────────────────────────────

async def query_internal_db(query: str, db: AsyncSession, limit: int = 10) -> list[dict]:
    """
    Query taxlegal.law_documents_v2 using full-text search + ILIKE fallback.
    Returns list of result dicts with trust metadata.
    """
    results = []

    # Full-text search using PostgreSQL tsvector
    try:
        fts_sql = text("""
            SELECT
                id,
                title,
                doc_number,
                doc_type,
                LEFT(content_text, 8000) AS content_text
            FROM taxlegal.law_documents_v2
            WHERE
                to_tsvector('simple',
                    coalesce(title, '') || ' ' || coalesce(content_text, ''))
                @@ plainto_tsquery('simple', :query)
            ORDER BY
                ts_rank(
                    to_tsvector('simple',
                        coalesce(title, '') || ' ' || coalesce(content_text, '')),
                    plainto_tsquery('simple', :query)
                ) DESC
            LIMIT :limit
        """)
        rows = await db.execute(fts_sql, {"query": query, "limit": limit})
        for row in rows.mappings():
            results.append({
                "id": row["id"],
                "title": row["title"],
                "doc_number": row["doc_number"],
                "doc_type": row["doc_type"],
                "content_text": row["content_text"] or "",
                "source_type": "internal_db",
                "trust_level": "high",
                "retrieval_method": "db_fulltext",
            })
    except Exception as e:
        logger.warning(f"FTS query on law_documents_v2 failed: {e}")

    # ILIKE fallback on title / doc_number
    if len(results) < limit:
        try:
            ilike_sql = text("""
                SELECT
                    id,
                    title,
                    doc_number,
                    doc_type,
                    LEFT(content_text, 8000) AS content_text
                FROM taxlegal.law_documents_v2
                WHERE
                    title ILIKE :pattern
                    OR doc_number ILIKE :pattern
                ORDER BY id DESC
                LIMIT :limit
            """)
            pattern = f"%{query[:100]}%"
            rows = await db.execute(ilike_sql, {"pattern": pattern, "limit": limit - len(results)})
            seen_ids = {r["id"] for r in results}
            for row in rows.mappings():
                if row["id"] not in seen_ids:
                    results.append({
                        "id": row["id"],
                        "title": row["title"],
                        "doc_number": row["doc_number"],
                        "doc_type": row["doc_type"],
                        "content_text": row["content_text"] or "",
                        "source_type": "internal_db",
                        "trust_level": "high",
                        "retrieval_method": "db_ilike",
                    })
        except Exception as e:
            logger.warning(f"ILIKE query on law_documents_v2 failed: {e}")

    logger.info(f"query_internal_db: {len(results)} results for '{query[:60]}'")
    return results


# ── dbvntax DB query ───────────────────────────────────────────────────────────

_DBVNTAX_TABLE_CACHE: Optional[str] = None

async def _detect_dbvntax_table(dbvntax_db: AsyncSession) -> Optional[str]:
    """Auto-detect which table exists in dbvntax. Tries common names."""
    global _DBVNTAX_TABLE_CACHE
    if _DBVNTAX_TABLE_CACHE:
        return _DBVNTAX_TABLE_CACHE

    candidate_tables = ["van_ban", "vanban", "documents", "laws"]
    for table in candidate_tables:
        try:
            await dbvntax_db.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
            _DBVNTAX_TABLE_CACHE = table
            logger.info(f"dbvntax table detected: {table}")
            return table
        except Exception:
            continue
    logger.warning("dbvntax: no known table found (van_ban, vanban, documents, laws)")
    return None


async def query_dbvntax(query: str, dbvntax_db: AsyncSession, limit: int = 10) -> list[dict]:
    """
    Query dbvntax PostgreSQL. Auto-detect table, ILIKE on title/ten columns.
    Returns list of result dicts with trust metadata.
    """
    table = await _detect_dbvntax_table(dbvntax_db)
    if not table:
        return []

    results = []
    pattern = f"%{query[:100]}%"

    # Try common column names for title: ten, title, tieu_de, name
    title_columns_attempts = [
        ("ten", "noi_dung"),
        ("title", "content"),
        ("tieu_de", "noi_dung"),
        ("name", "content"),
        ("ten_van_ban", "noi_dung"),
    ]

    for title_col, content_col in title_columns_attempts:
        try:
            sql = text(f"""
                SELECT *
                FROM {table}
                WHERE {title_col} ILIKE :pattern
                LIMIT :limit
            """)
            rows = await dbvntax_db.execute(sql, {"pattern": pattern, "limit": limit})
            mappings = rows.mappings().all()
            if not mappings and not results:
                continue
            for row in mappings:
                row_dict = dict(row)
                results.append({
                    "id": row_dict.get("id"),
                    "title": row_dict.get(title_col, ""),
                    "doc_number": row_dict.get("so_hieu", row_dict.get("so_van_ban", "")),
                    "doc_type": row_dict.get("loai_van_ban", row_dict.get("doc_type", "")),
                    "content_text": str(row_dict.get(content_col, ""))[:8000],
                    "source_type": "dbvntax",
                    "trust_level": "high",
                    "retrieval_method": "dbvntax_query",
                })
            if results:
                break
        except Exception:
            continue

    logger.info(f"query_dbvntax: {len(results)} results for '{query[:60]}'")
    return results


# ── Web search fallback ────────────────────────────────────────────────────────

async def fallback_web_search(query: str) -> list[dict]:
    """
    Call existing web_search() from backend.web_search.
    Returns results with external_search metadata.
    """
    try:
        from backend.web_search import web_search
        result = await web_search(query, context="legal research Vietnam tax law")
        answer = result.get("answer", "")
        citations = result.get("citations", [])

        results = [{
            "id": None,
            "title": f"Web search: {query[:80]}",
            "doc_number": None,
            "doc_type": "web_result",
            "content_text": answer[:2000],
            "answer": answer,
            "source_type": "external_search",
            "trust_level": "medium",
            "retrieval_method": "perplexity_sonar",
            "source_url": citations[0] if citations else None,
            "citations": citations,
        }]
        return results
    except Exception as e:
        logger.error(f"fallback_web_search failed: {e}")
        return []


# ── RetrievalService ───────────────────────────────────────────────────────────

class RetrievalService:
    """
    DB-First Retrieval Service.
    Always queries internal DB(s) first. Only falls back to web if DB yields nothing.
    """

    async def retrieve(
        self,
        query: str,
        db: AsyncSession,
        dbvntax_db: Optional[AsyncSession] = None,
        min_db_results: int = 1,
        case_id: Optional[str] = None,
        agent_run_id: Optional[str] = None,
    ) -> RetrievalResult:
        """
        Main retrieval entry point.

        Logic:
        1. Query internal DB (law_documents_v2)
        2. If still short, query dbvntax (if available)
        3. If total DB results >= min_db_results: used_fallback=False
        4. Otherwise: fallback to web search
        5. If web also empty: insufficient_coverage=True
        6. Log retrieval_queries record to DB
        7. Return RetrievalResult
        """
        db_results: list[dict] = []
        web_results: list[dict] = []
        used_fallback = False
        insufficient_coverage = False

        # Step 1: Internal DB
        try:
            internal = await query_internal_db(query, db)
            db_results.extend(internal)
        except Exception as e:
            logger.error(f"Internal DB query failed: {e}")

        # Step 2: dbvntax (if provided and still need more results)
        if len(db_results) < min_db_results and dbvntax_db is not None:
            try:
                dbvntax_results = await query_dbvntax(query, dbvntax_db)
                db_results.extend(dbvntax_results)
            except Exception as e:
                logger.error(f"dbvntax query failed: {e}")

        # Step 3: Check if DB coverage sufficient
        if len(db_results) >= min_db_results:
            used_fallback = False
        else:
            # Step 4: Web search fallback
            used_fallback = True
            try:
                web_results = await fallback_web_search(query)
            except Exception as e:
                logger.error(f"Fallback web search failed: {e}")
                web_results = []

            # Step 5: Check if still no results
            if not web_results or (
                len(web_results) == 1
                and "[Web search unavailable" in web_results[0].get("content_text", "")
            ):
                insufficient_coverage = True

        # Build citations
        citations = []
        for r in db_results + web_results:
            if r.get("doc_number"):
                citations.append({
                    "doc_number": r["doc_number"],
                    "title": r.get("title", ""),
                    "source_type": r.get("source_type", ""),
                    "trust_level": r.get("trust_level", ""),
                    "retrieval_method": r.get("retrieval_method", ""),
                    "source_url": r.get("source_url"),
                })
            elif r.get("source_url"):
                citations.append({
                    "doc_number": None,
                    "title": r.get("title", ""),
                    "source_type": r.get("source_type", ""),
                    "trust_level": r.get("trust_level", ""),
                    "retrieval_method": r.get("retrieval_method", ""),
                    "source_url": r["source_url"],
                })

        answer = ""
        if insufficient_coverage:
            answer = "insufficient source coverage"
        elif web_results and not db_results:
            answer = web_results[0].get("answer", "")

        result = RetrievalResult(
            query=query,
            db_results=db_results,
            web_results=web_results,
            used_fallback=used_fallback,
            insufficient_coverage=insufficient_coverage,
            answer=answer,
            citations=citations,
            total_results=len(db_results) + len(web_results),
        )

        # Step 6: Log retrieval query to DB
        await self._log_retrieval_query(
            db=db,
            query=query,
            result=result,
            case_id=case_id,
            agent_run_id=agent_run_id,
        )

        return result

    async def _log_retrieval_query(
        self,
        db: AsyncSession,
        query: str,
        result: RetrievalResult,
        case_id: Optional[str] = None,
        agent_run_id: Optional[str] = None,
    ) -> None:
        """Insert a retrieval_queries log record (raw SQL, fire-and-forget)."""
        try:
            log_sql = text("""
                INSERT INTO taxlegal.retrieval_queries (
                    id,
                    case_id,
                    agent_run_id,
                    query_text,
                    db_results_count,
                    web_results_count,
                    used_fallback,
                    insufficient_coverage,
                    created_at
                ) VALUES (
                    :id,
                    :case_id,
                    :agent_run_id,
                    :query_text,
                    :db_results_count,
                    :web_results_count,
                    :used_fallback,
                    :insufficient_coverage,
                    :created_at
                )
                ON CONFLICT DO NOTHING
            """)
            await db.execute(log_sql, {
                "id": str(uuid.uuid4()),
                "case_id": str(case_id) if case_id else None,
                "agent_run_id": str(agent_run_id) if agent_run_id else None,
                "query_text": query[:500],
                "db_results_count": len(result.db_results),
                "web_results_count": len(result.web_results),
                "used_fallback": result.used_fallback,
                "insufficient_coverage": result.insufficient_coverage,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            await db.flush()
        except Exception as e:
            # Non-fatal — logging failure must not break retrieval
            logger.debug(f"Could not log retrieval_query (table may not exist yet): {e}")
