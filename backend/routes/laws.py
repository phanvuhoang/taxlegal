"""Law documents API — search local cache + dbvntax reference.

DB-FIRST POLICY: All search endpoints query taxlegal.law_documents_v2 (internal DB)
and/or dbvntax first. There is NO web search in this module. Confirmed compliant.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, text
from typing import Optional
from backend.database import get_db, get_dbvntax_db
from backend.models import LawDocument, User
from backend.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/laws", tags=["laws"])


@router.get("/")
async def search_laws(
    q: str = Query("", description="Search query"),
    practice_area: Optional[str] = None,
    loai: Optional[str] = None,
    tinh_trang: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(LawDocument).order_by(LawDocument.created_at.desc())
    if q:
        query = query.where(
            or_(
                LawDocument.ten.ilike(f"%{q}%"),
                LawDocument.so_hieu.ilike(f"%{q}%"),
            )
        )
    if loai:
        query = query.where(LawDocument.loai == loai)
    if tinh_trang:
        query = query.where(LawDocument.tinh_trang == tinh_trang)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    laws = result.scalars().all()
    return [
        {
            "id": l.id, "so_hieu": l.so_hieu, "ten": l.ten,
            "loai": l.loai, "co_quan": l.co_quan,
            "hieu_luc_tu": l.hieu_luc_tu, "het_hieu_luc_tu": l.het_hieu_luc_tu,
            "tinh_trang": l.tinh_trang, "practice_areas": l.practice_areas or [],
            "link_tvpl": l.link_tvpl, "source": l.source,
        }
        for l in laws
    ]


@router.get("/{law_id}")
async def get_law(
    law_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(LawDocument).where(LawDocument.id == law_id))
    law = result.scalar_one_or_none()
    if not law:
        raise HTTPException(404, "Law not found")
    return {
        "id": law.id, "so_hieu": law.so_hieu, "ten": law.ten,
        "loai": law.loai, "co_quan": law.co_quan,
        "ngay_ban_hanh": law.ngay_ban_hanh, "hieu_luc_tu": law.hieu_luc_tu,
        "het_hieu_luc_tu": law.het_hieu_luc_tu, "tinh_trang": law.tinh_trang,
        "replaced_by": law.replaced_by, "practice_areas": law.practice_areas or [],
        "content_text": law.content_text, "link_tvpl": law.link_tvpl,
        "source": law.source,
    }


@router.post("/")
async def add_law(
    data: dict,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    law = LawDocument(
        so_hieu=data.get("so_hieu"),
        ten=data["ten"],
        loai=data.get("loai"),
        co_quan=data.get("co_quan"),
        ngay_ban_hanh=data.get("ngay_ban_hanh"),
        hieu_luc_tu=data.get("hieu_luc_tu"),
        het_hieu_luc_tu=data.get("het_hieu_luc_tu"),
        tinh_trang=data.get("tinh_trang", "con_hieu_luc"),
        practice_areas=data.get("practice_areas", []),
        content_text=data.get("content_text"),
        link_tvpl=data.get("link_tvpl"),
        source="manual",
    )
    db.add(law)
    await db.commit()
    await db.refresh(law)
    return {"id": law.id, "so_hieu": law.so_hieu, "ten": law.ten}


@router.get("/dbvntax/search")
async def search_dbvntax(
    q: str = Query(..., description="Search query"),
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    dbvntax: AsyncSession = Depends(get_dbvntax_db),
):
    """Search the existing dbvntax database for laws."""
    try:
        result = await dbvntax.execute(
            text("""
                SELECT id, so_hieu, ten, loai, co_quan, hieu_luc_tu, het_hieu_luc_tu, tinh_trang, link_tvpl
                FROM van_ban
                WHERE ten ILIKE :q OR so_hieu ILIKE :q
                ORDER BY hieu_luc_tu DESC NULLS LAST
                LIMIT :limit
            """),
            {"q": f"%{q}%", "limit": limit}
        )
        rows = result.mappings().all()
        return [dict(r) for r in rows]
    except Exception as e:
        raise HTTPException(500, f"Database error: {e}")
