"""
Hybrid search engine: semantic (pgvector cosine) + full-text (tsvector).
Weighted combination: 60% semantic + 40% full-text by default.
Falls back to keyword-only search when no embedding is available.
"""
import logging
from dataclasses import dataclass
from typing import Optional
from sqlalchemy import text
from .database import LegalAISession

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    chunk_id: str
    law_id: str
    law_title: str
    law_number: str
    article: Optional[str]
    clause: Optional[str]
    content: str
    parent_context: Optional[str]
    semantic_score: float
    keyword_score: float
    combined_score: float
    law_status: str
    domains: list
    source_url: Optional[str]


async def hybrid_search(
    query_text: str,
    query_embedding: Optional[list] = None,
    domains: Optional[list] = None,
    limit: int = 10,
    semantic_weight: float = 0.6,
) -> list[SearchResult]:
    """
    Hybrid semantic + keyword search over law_chunks.
    Returns results ranked by combined score.
    """
    async with LegalAISession() as session:
        if query_embedding:
            # Full hybrid search: semantic + keyword
            domain_filter = ""
            params: dict = {
                "embedding": str(query_embedding),
                "query": query_text,
                "limit": limit,
                "sem_weight": semantic_weight,
                "kw_weight": 1 - semantic_weight,
            }
            if domains:
                domain_filter = "AND ld.domains && :domains"
                params["domains"] = domains

            sql = text(f"""
                WITH semantic AS (
                    SELECT
                        lc.id, lc.law_id, lc.article, lc.clause, lc.content,
                        lc.parent_context, lc.domains,
                        1 - (lc.embedding <=> :embedding::vector) AS score
                    FROM law_chunks lc
                    JOIN law_documents ld ON ld.id = lc.law_id
                    WHERE lc.embedding IS NOT NULL
                    {domain_filter}
                    ORDER BY lc.embedding <=> :embedding::vector
                    LIMIT 50
                ),
                keyword AS (
                    SELECT
                        lc.id,
                        ts_rank(lc.tsv, plainto_tsquery('simple', :query)) AS score
                    FROM law_chunks lc
                    JOIN law_documents ld ON ld.id = lc.law_id
                    WHERE lc.tsv @@ plainto_tsquery('simple', :query)
                    {domain_filter}
                    LIMIT 50
                ),
                combined AS (
                    SELECT
                        COALESCE(s.id, k.id) AS chunk_id,
                        COALESCE(s.score, 0) * :sem_weight
                            + COALESCE(k.score, 0) * :kw_weight AS combined_score,
                        COALESCE(s.score, 0) AS semantic_score,
                        COALESCE(k.score, 0) AS keyword_score
                    FROM semantic s
                    FULL OUTER JOIN keyword k ON k.id = s.id
                )
                SELECT
                    c.chunk_id, c.combined_score, c.semantic_score, c.keyword_score,
                    lc.article, lc.clause, lc.content, lc.parent_context, lc.domains,
                    ld.id AS law_id, ld.title AS law_title, ld.law_number,
                    ld.status AS law_status, ld.source_url
                FROM combined c
                JOIN law_chunks lc ON lc.id = c.chunk_id
                JOIN law_documents ld ON ld.id = lc.law_id
                ORDER BY c.combined_score DESC
                LIMIT :limit
            """)
        else:
            # Keyword-only fallback
            domain_filter = ""
            params = {"query": query_text, "limit": limit}
            if domains:
                domain_filter = "AND ld.domains && :domains"
                params["domains"] = domains

            sql = text(f"""
                SELECT
                    lc.id AS chunk_id,
                    ts_rank(lc.tsv, plainto_tsquery('simple', :query)) AS combined_score,
                    0 AS semantic_score,
                    ts_rank(lc.tsv, plainto_tsquery('simple', :query)) AS keyword_score,
                    lc.article, lc.clause, lc.content, lc.parent_context, lc.domains,
                    ld.id AS law_id, ld.title AS law_title, ld.law_number,
                    ld.status AS law_status, ld.source_url
                FROM law_chunks lc
                JOIN law_documents ld ON ld.id = lc.law_id
                WHERE lc.tsv @@ plainto_tsquery('simple', :query)
                {domain_filter}
                ORDER BY combined_score DESC
                LIMIT :limit
            """)

        result = await session.execute(sql, params)
        rows = result.mappings().all()

        return [
            SearchResult(
                chunk_id=str(r["chunk_id"]),
                law_id=str(r["law_id"]),
                law_title=r["law_title"],
                law_number=r["law_number"],
                article=r.get("article"),
                clause=r.get("clause"),
                content=r["content"],
                parent_context=r.get("parent_context"),
                semantic_score=float(r.get("semantic_score") or 0),
                keyword_score=float(r.get("keyword_score") or 0),
                combined_score=float(r.get("combined_score") or 0),
                law_status=r.get("law_status", "active"),
                domains=r.get("domains") or [],
                source_url=r.get("source_url"),
            )
            for r in rows
        ]


async def search_law_documents(
    query: str,
    domains: Optional[list] = None,
    limit: int = 20,
) -> list:
    """
    Search law_documents table (title + summary level) by full-text.
    Returns a list of dicts.
    """
    async with LegalAISession() as session:
        domain_filter = "AND domains && :domains" if domains else ""
        params: dict = {"query": query, "limit": limit}
        if domains:
            params["domains"] = domains

        sql = text(f"""
            SELECT
                id, title, law_number, law_type, issuer,
                issued_date, effective_date, status, domains,
                summary, source_url
            FROM law_documents
            WHERE to_tsvector('simple', title || ' ' || COALESCE(summary,''))
                  @@ plainto_tsquery('simple', :query)
            {domain_filter}
            ORDER BY
                ts_rank(
                    to_tsvector('simple', title || ' ' || COALESCE(summary,'')),
                    plainto_tsquery('simple', :query)
                ) DESC
            LIMIT :limit
        """)
        result = await session.execute(sql, params)
        return [dict(r) for r in result.mappings().all()]
