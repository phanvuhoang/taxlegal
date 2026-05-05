"""
Law document CRUD endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy import text
from backend.auth import get_current_user, get_current_admin
from backend.legalai.database import LegalAISession

router = APIRouter(prefix="/api/legalai/laws", tags=["Law Documents"])


@router.get("")
async def list_laws(
    law_type: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    status: Optional[str] = Query("active"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
):
    """List law documents with optional filters."""
    conditions = []
    params: dict = {"limit": limit, "offset": offset}

    if law_type:
        conditions.append("law_type = :law_type")
        params["law_type"] = law_type
    if domain:
        conditions.append(":domain = ANY(domains)")
        params["domain"] = domain
    if status:
        conditions.append("status = :status")
        params["status"] = status

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    async with LegalAISession() as session:
        result = await session.execute(
            text(f"""
                SELECT id, title, law_number, law_type, issuer,
                       issued_date, effective_date, status, domains,
                       summary, source_url, created_at
                FROM law_documents
                {where}
                ORDER BY effective_date DESC NULLS LAST, created_at DESC
                LIMIT :limit OFFSET :offset
            """),
            params,
        )
        rows = result.mappings().all()

        count_result = await session.execute(
            text(f"SELECT COUNT(*) FROM law_documents {where}"),
            params,
        )
        total = count_result.scalar()

    return {"laws": [dict(r) for r in rows], "total": total}


@router.get("/{law_id}")
async def get_law(law_id: str, current_user=Depends(get_current_user)):
    """Get a single law document including its chunks."""
    async with LegalAISession() as session:
        result = await session.execute(
            text("""
                SELECT id, title, law_number, law_type, issuer,
                       issued_date, effective_date, status, domains,
                       full_text, summary, source_url, crawled_at, created_at
                FROM law_documents
                WHERE id = :id
            """),
            {"id": law_id},
        )
        law = result.mappings().fetchone()
        if not law:
            raise HTTPException(404, "Law not found")

        chunks_result = await session.execute(
            text("""
                SELECT id, article, clause, content, parent_context, domains
                FROM law_chunks
                WHERE law_id = :law_id
                ORDER BY id
            """),
            {"law_id": law_id},
        )
        chunks = chunks_result.mappings().all()

    return {**dict(law), "chunks": [dict(c) for c in chunks]}
