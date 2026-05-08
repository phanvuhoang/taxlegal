"""pytest fixtures for TaxLegal v4 tests."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_db():
    """Mock AsyncSession for unit tests."""
    db = AsyncMock(spec=AsyncSession)
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.flush = AsyncMock()
    db.add = MagicMock()
    return db

@pytest.fixture
def sample_case_state():
    return {
        "case_id": "test-case-123",
        "matter_id": None,
        "workflow_run_id": "test-run-456",
        "client_request": "Công ty tôi muốn hỏi về thuế TNDN năm 2024",
        "title": "Tư vấn thuế TNDN",
        "practice_area": "tax",
        "output_language": "vi",
        "current_node": "intake",
        "completed_nodes": [],
        "verified_facts": [],
        "applicable_laws": [],
        "completeness_matrix": [],
        "missing_facts": [],
        "clarification_iterations": 0,
        "partner_brief": None,
        "sa_blueprint": None,
        "research_chunks": [],
        "draft_opinion": None,
        "draft_version": 0,
        "sa_decision": None,
        "sa_issues": [],
        "partner_decision": None,
        "partner_issues": [],
        "risk_score": 0.0,
        "human_approval_required": False,
        "human_approval_status": None,
        "retrieval_queries": [],
        "citations": [],
        "used_fallback_search": False,
        "has_insufficient_coverage": False,
        "final_output": None,
        "quality_score": None,
        "error": None,
        "iterations": 0,
        "max_iterations": 50,
        "audit_events": [],
    }

@pytest.fixture
def sample_db_result():
    """A typical internal DB result from law_documents_v2."""
    return {
        "id": 1,
        "title": "Thông tư 80/2021/TT-BTC",
        "doc_number": "80/2021/TT-BTC",
        "doc_type": "Thông tư",
        "content_text": "Điều 1. Phạm vi điều chỉnh — Thông tư này hướng dẫn về thuế GTGT...",
        "source_type": "internal_db",
        "trust_level": "high",
        "retrieval_method": "db_fulltext",
    }
