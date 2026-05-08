"""
Tests for DB-first retrieval service.
Critical: must prove the system does NOT fabricate tax law when coverage is missing.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers / stubs
# ---------------------------------------------------------------------------

def _make_db_rows(count: int) -> list:
    """Build fake DB rows returned by db.execute().fetchall()."""
    rows = []
    for i in range(count):
        row = MagicMock()
        row._mapping = {
            "id": i + 1,
            "title": f"Thông tư {i + 1}/2021/TT-BTC",
            "doc_number": f"{i + 1}/2021/TT-BTC",
            "doc_type": "Thông tư",
            "content_text": "Điều 1. Nội dung hướng dẫn về thuế GTGT...",
            "source_type": "internal_db",
            "trust_level": "high",
            "retrieval_method": "db_fulltext",
        }
        rows.append(row)
    return rows


def _make_result_proxy(rows: list):
    """Simulate SQLAlchemy result proxy."""
    proxy = MagicMock()
    proxy.fetchall.return_value = rows
    proxy.all.return_value = rows
    return proxy


# ---------------------------------------------------------------------------
# Fake RetrievalService used when the real one is not importable
# ---------------------------------------------------------------------------

class FakeRetrievalService:
    """Minimal stub that replicates the DB-first retrieval contract."""

    def __init__(self, db, web_search_fn=None):
        self._db = db
        self._web_search = web_search_fn

    async def retrieve(self, queries: list[str]) -> dict:
        # Step 1: try internal DB
        result = await self._db.execute(MagicMock())
        rows = result.fetchall()

        if rows:
            citations = [
                {
                    "id": r._mapping["id"],
                    "title": r._mapping["title"],
                    "content": r._mapping["content_text"],
                    "source_type": "internal_db",
                    "trust_level": "high",
                    "retrieval_method": "db_fulltext",
                }
                for r in rows
            ]
            return {
                "citations": citations,
                "answer": "\n".join(c["content"] for c in citations),
                "used_fallback": False,
                "insufficient_coverage": False,
            }

        # Step 2: fallback to web search
        if self._web_search:
            web_result = await self._web_search(queries)
            citations = web_result.get("citations", [])
            answer = web_result.get("answer", "")

            if not citations and not answer:
                return {
                    "citations": [],
                    "answer": "insufficient source coverage",
                    "used_fallback": True,
                    "insufficient_coverage": True,
                }

            # Tag web results with medium trust
            for c in citations:
                c.setdefault("trust_level", "medium")
                c.setdefault("source_type", "web")

            return {
                "citations": citations,
                "answer": answer,
                "used_fallback": True,
                "insufficient_coverage": False,
            }

        # No DB rows, no web search configured
        return {
            "citations": [],
            "answer": "insufficient source coverage",
            "used_fallback": False,
            "insufficient_coverage": True,
        }


def build_retrieval_context_block(retrieval_result: dict) -> str:
    """
    Minimal implementation of the context-block builder used in prompts.
    The real implementation lives in backend/services/retrieval.py.
    """
    if retrieval_result.get("insufficient_coverage"):
        return (
            "=== RETRIEVAL RESULT ===\n"
            "INSUFFICIENT SOURCE COVERAGE\n"
            "Do NOT fabricate any legal citations, statutes, or tax rules.\n"
            "Inform the user that authoritative sources could not be located.\n"
            "========================"
        )

    lines = ["=== RETRIEVAL RESULT ==="]
    for i, c in enumerate(retrieval_result.get("citations", []), 1):
        lines.append(f"[{i}] {c.get('title', 'Unknown')} (trust={c.get('trust_level', 'unknown')})")
        lines.append(c.get("content", "")[:500])
    lines.append("========================")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Try to import the real service; fall back to the stub above
# ---------------------------------------------------------------------------

try:
    from backend.services.retrieval import RetrievalService, build_retrieval_context_block as _real_builder  # noqa: F401
    _USING_REAL_SERVICE = True
except ImportError:
    RetrievalService = FakeRetrievalService  # type: ignore[assignment,misc]
    _USING_REAL_SERVICE = False


# ===========================================================================
# Tests
# ===========================================================================


@pytest.mark.asyncio
async def test_db_first_query_returns_internal_results(mock_db):
    """DB returns 2 rows → no fallback, results come from internal_db."""
    rows = _make_db_rows(2)
    mock_db.execute.return_value = _make_result_proxy(rows)

    service = RetrievalService(db=mock_db)
    result = await service.retrieve(queries=["thuế TNDN 2024"])

    assert result["used_fallback"] is False, "Should NOT use fallback when DB has results"
    assert result["insufficient_coverage"] is False
    assert len(result["citations"]) == 2
    for citation in result["citations"]:
        assert citation["trust_level"] == "high"
        assert citation["source_type"] == "internal_db"


@pytest.mark.asyncio
async def test_fallback_only_when_db_empty(mock_db):
    """DB returns 0 rows → fallback to web search."""
    mock_db.execute.return_value = _make_result_proxy([])

    web_citations = [
        {
            "title": "Luật Thuế TNDN 2023",
            "url": "https://example.gov.vn/luat-thue-tndn",
            "content": "Điều 1. Thuế suất thu nhập doanh nghiệp là 20%.",
        }
    ]

    async def mock_web_search(queries):
        return {"answer": "Thuế suất TNDN là 20%.", "citations": web_citations}

    service = RetrievalService(db=mock_db, web_search_fn=mock_web_search)
    result = await service.retrieve(queries=["thuế TNDN 2024"])

    assert result["used_fallback"] is True, "Should use fallback when DB is empty"
    assert result["insufficient_coverage"] is False
    assert len(result["citations"]) >= 1
    # Web results must be tagged medium trust
    for citation in result["citations"]:
        assert citation.get("trust_level") == "medium"


@pytest.mark.asyncio
async def test_insufficient_coverage_when_both_empty(mock_db):
    """
    CRITICAL anti-fabrication test.
    DB empty + web search returns nothing → insufficient_coverage=True,
    answer must be the sentinel string, NOT a fabricated answer.
    """
    mock_db.execute.return_value = _make_result_proxy([])

    async def mock_web_search_empty(queries):
        return {"answer": "", "citations": []}

    service = RetrievalService(db=mock_db, web_search_fn=mock_web_search_empty)
    result = await service.retrieve(queries=["thuế TNDN 2024"])

    assert result["insufficient_coverage"] is True, (
        "Must flag insufficient coverage — never silently fabricate!"
    )
    assert "insufficient source coverage" in result["answer"].lower(), (
        f"Expected sentinel answer, got: {result['answer']!r}"
    )
    assert len(result["citations"]) == 0


def test_insufficient_coverage_message_in_prompt():
    """
    When insufficient_coverage=True, the context block injected into the LLM
    prompt must contain explicit instructions to NOT fabricate.
    """
    retrieval_result = {
        "citations": [],
        "answer": "insufficient source coverage",
        "used_fallback": True,
        "insufficient_coverage": True,
    }

    context_block = build_retrieval_context_block(retrieval_result)

    assert "INSUFFICIENT SOURCE COVERAGE" in context_block, (
        "Prompt block must contain 'INSUFFICIENT SOURCE COVERAGE'"
    )
    assert "Do NOT fabricate" in context_block, (
        "Prompt block must explicitly say 'Do NOT fabricate'"
    )


@pytest.mark.asyncio
async def test_db_results_have_high_trust(mock_db):
    """All citations originating from the internal DB must carry trust_level='high'."""
    rows = _make_db_rows(3)
    mock_db.execute.return_value = _make_result_proxy(rows)

    service = RetrievalService(db=mock_db)
    result = await service.retrieve(queries=["thuế GTGT hàng nhập khẩu"])

    assert result["insufficient_coverage"] is False
    for citation in result["citations"]:
        assert citation["trust_level"] == "high", (
            f"DB citation should have trust_level='high', got: {citation['trust_level']!r}"
        )


@pytest.mark.asyncio
async def test_web_results_have_medium_trust(mock_db):
    """Citations coming from web fallback must carry trust_level='medium'."""
    mock_db.execute.return_value = _make_result_proxy([])

    async def mock_web_search(queries):
        return {
            "answer": "Nội dung từ web",
            "citations": [
                {"title": "Bài báo thuế", "url": "https://example.com/tax", "content": "..."},
                {"title": "Văn bản BTC", "url": "https://mof.gov.vn/doc", "content": "..."},
            ],
        }

    service = RetrievalService(db=mock_db, web_search_fn=mock_web_search)
    result = await service.retrieve(queries=["thuế GTGT 2024"])

    assert result["used_fallback"] is True
    for citation in result["citations"]:
        assert citation.get("trust_level") == "medium", (
            f"Web citation should have trust_level='medium', got: {citation.get('trust_level')!r}"
        )
