"""
Extended health check endpoint — TaxLegal v4.

GET /api/health/detailed  — detailed component health status
"""
import logging
import os

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/api/health/detailed")
async def health_detailed(db: AsyncSession = Depends(get_db)):
    """
    Returns detailed health status for all components:
    - postgres: database connectivity
    - langgraph: LangGraph library availability
    - temporal: Temporal workflow library availability
    - redis: Redis connectivity (if configured)
    """
    checks: dict[str, str] = {}

    # DB check
    try:
        await db.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {e}"

    # LangGraph check
    try:
        import langgraph
        checks["langgraph"] = f"ok (v{langgraph.__version__})"
    except ImportError:
        checks["langgraph"] = "not_installed"

    # Temporal check
    try:
        import temporalio
        checks["temporal"] = f"ok (v{temporalio.__version__})"
    except ImportError:
        checks["temporal"] = "not_installed"

    # Redis check
    redis_url = os.getenv("REDIS_URL", "")
    if redis_url:
        try:
            import redis.asyncio as aioredis
            r = aioredis.from_url(redis_url)
            await r.ping()
            checks["redis"] = "ok"
            await r.aclose()
        except Exception as e:
            checks["redis"] = f"error: {e}"
    else:
        checks["redis"] = "not_configured"

    overall = (
        "ok"
        if all(v == "ok" or "not_" in v for v in checks.values())
        else "degraded"
    )

    return {"status": overall, "checks": checks, "version": "4.0.0"}
