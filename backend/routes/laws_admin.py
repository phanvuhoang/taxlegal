"""
Law Documents admin routes — Văn bản Luật management.
/api/admin/law-documents/*
/api/admin/dbvntax/*

DB-FIRST POLICY: All admin endpoints write to and read from taxlegal.law_documents_v2
(internal DB). Documents are imported from dbvntax or uploads — never from web search.
Confirmed compliant: no web_search() calls in this module.
"""
import logging
import os
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.database import get_db
from backend.models import User
from backend.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["laws-admin"])

DBVNTAX_URL = os.getenv("DBVNTAX_DATABASE_URL", "")


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    return current_user


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class LawDocCreate(BaseModel):
    title: str
    doc_number: Optional[str] = None
    doc_type: str = "thong_tu"
    issuer: Optional[str] = None
    issued_date: Optional[str] = None
    effective_date: Optional[str] = None
    content_html: Optional[str] = None
    content_text: Optional[str] = None
    source_url: Optional[str] = None
    tags: Optional[List[str]] = []
    is_priority: bool = False
    imported_from: str = "paste"


class LawDocOut(BaseModel):
    id: int
    title: str
    doc_number: Optional[str]
    doc_type: str
    issuer: Optional[str]
    issued_date: Optional[str]
    effective_date: Optional[str]
    source_url: Optional[str]
    tags: Optional[List[str]]
    is_priority: bool
    is_active: bool
    ai_tagged: bool
    imported_from: Optional[str]
    content_length: Optional[int]
    created_at: Optional[str]


# ── Law Documents CRUD ────────────────────────────────────────────────────────

@router.get("/api/admin/law-documents")
async def list_law_documents(
    doc_type: Optional[str] = None,
    is_priority: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    conditions = ["is_active = TRUE"]
    params: dict = {"skip": skip, "limit": limit}
    if doc_type:
        conditions.append("doc_type = :doc_type")
        params["doc_type"] = doc_type
    if is_priority is not None:
        conditions.append("is_priority = :is_priority")
        params["is_priority"] = is_priority
    if search:
        conditions.append("(title ILIKE :search OR doc_number ILIKE :search)")
        params["search"] = f"%{search}%"

    where = " AND ".join(conditions)
    result = await db.execute(
        text(f"""
            SELECT id, title, doc_number, doc_type, issuer, issued_date, effective_date,
                   source_url, tags, is_priority, is_active, ai_tagged, imported_from,
                   LENGTH(COALESCE(content_text,'')) as content_length, created_at
            FROM taxlegal.law_documents_v2
            WHERE {where}
            ORDER BY is_priority DESC, created_at DESC
            LIMIT :limit OFFSET :skip
        """),
        params
    )
    rows = result.fetchall()
    return [
        {
            "id": r.id, "title": r.title, "doc_number": r.doc_number,
            "doc_type": r.doc_type, "issuer": r.issuer,
            "issued_date": str(r.issued_date) if r.issued_date else None,
            "effective_date": str(r.effective_date) if r.effective_date else None,
            "source_url": r.source_url, "tags": r.tags or [],
            "is_priority": r.is_priority, "is_active": r.is_active,
            "ai_tagged": r.ai_tagged, "imported_from": r.imported_from,
            "content_length": r.content_length,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.post("/api/admin/law-documents", status_code=201)
async def create_law_document(
    req: LawDocCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    # Strip HTML for content_text if not provided
    content_text = req.content_text
    if not content_text and req.content_html:
        import re
        content_text = re.sub(r'<[^>]+>', ' ', req.content_html)
        content_text = re.sub(r'\s+', ' ', content_text).strip()

    result = await db.execute(
        text("""
            INSERT INTO taxlegal.law_documents_v2
                (title, doc_number, doc_type, issuer, issued_date, effective_date,
                 content_html, content_text, source_url, tags, is_priority,
                 imported_from, created_by)
            VALUES
                (:title, :doc_number, :doc_type, :issuer, :issued_date, :effective_date,
                 :content_html, :content_text, :source_url, :tags, :is_priority,
                 :imported_from, :created_by)
            RETURNING id, title, doc_number, doc_type, issuer, is_priority, created_at
        """),
        {
            "title": req.title, "doc_number": req.doc_number, "doc_type": req.doc_type,
            "issuer": req.issuer,
            "issued_date": req.issued_date or None,
            "effective_date": req.effective_date or None,
            "content_html": req.content_html, "content_text": content_text,
            "source_url": req.source_url, "tags": req.tags or [],
            "is_priority": req.is_priority, "imported_from": req.imported_from,
            "created_by": admin.id,
        }
    )
    row = result.fetchone()
    await db.commit()
    return {"id": row.id, "title": row.title, "doc_number": row.doc_number,
            "doc_type": row.doc_type, "is_priority": row.is_priority,
            "created_at": row.created_at.isoformat() if row.created_at else None}


@router.get("/api/admin/law-documents/{doc_id}")
async def get_law_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(
        text("SELECT * FROM taxlegal.law_documents_v2 WHERE id = :id"),
        {"id": doc_id}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return dict(row._mapping)


@router.put("/api/admin/law-documents/{doc_id}")
async def update_law_document(
    doc_id: int,
    req: LawDocCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    content_text = req.content_text
    if not content_text and req.content_html:
        import re
        content_text = re.sub(r'<[^>]+>', ' ', req.content_html)
        content_text = re.sub(r'\s+', ' ', content_text).strip()

    await db.execute(
        text("""
            UPDATE taxlegal.law_documents_v2 SET
                title=:title, doc_number=:doc_number, doc_type=:doc_type,
                issuer=:issuer, issued_date=:issued_date, effective_date=:effective_date,
                content_html=:content_html, content_text=:content_text,
                source_url=:source_url, tags=:tags, is_priority=:is_priority,
                updated_at=NOW()
            WHERE id=:id
        """),
        {
            "title": req.title, "doc_number": req.doc_number, "doc_type": req.doc_type,
            "issuer": req.issuer,
            "issued_date": req.issued_date or None,
            "effective_date": req.effective_date or None,
            "content_html": req.content_html, "content_text": content_text,
            "source_url": req.source_url, "tags": req.tags or [],
            "is_priority": req.is_priority, "id": doc_id,
        }
    )
    await db.commit()
    return {"id": doc_id, "status": "updated"}


@router.delete("/api/admin/law-documents/{doc_id}", status_code=204)
async def delete_law_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    await db.execute(
        text("UPDATE taxlegal.law_documents_v2 SET is_active=FALSE WHERE id=:id"),
        {"id": doc_id}
    )
    await db.commit()


@router.post("/api/admin/law-documents/upload")
async def upload_law_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    doc_type: str = Form("thong_tu"),
    doc_number: str = Form(None),
    is_priority: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Upload PDF, DOCX, or TXT file as a law document."""
    import re
    content_bytes = await file.read()
    filename = file.filename or "document"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"

    content_text = ""
    content_html = ""

    try:
        if ext == "txt":
            content_text = content_bytes.decode("utf-8", errors="ignore")
            content_html = "<pre>" + content_text + "</pre>"
        elif ext == "pdf":
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(content_bytes))
            parts = [page.extract_text() for page in reader.pages if page.extract_text()]
            content_text = "\n".join(parts)
            content_html = "<pre>" + content_text + "</pre>"
        elif ext in ("docx", "doc"):
            import io
            import docx as docxlib
            doc = docxlib.Document(io.BytesIO(content_bytes))
            parts = [p.text for p in doc.paragraphs if p.text.strip()]
            content_text = "\n".join(parts)
            content_html = "".join(f"<p>{p}</p>" for p in parts)
        else:
            content_text = content_bytes.decode("utf-8", errors="ignore")
            content_html = "<pre>" + content_text + "</pre>"
    except Exception as e:
        logger.warning(f"Text extraction failed: {e}")
        content_text = content_bytes.decode("utf-8", errors="ignore")
        content_html = "<pre>" + content_text + "</pre>"

    result = await db.execute(
        text("""
            INSERT INTO taxlegal.law_documents_v2
                (title, doc_number, doc_type, content_html, content_text,
                 is_priority, imported_from, created_by)
            VALUES (:title, :doc_number, :doc_type, :content_html, :content_text,
                    :is_priority, 'upload', :created_by)
            RETURNING id, title
        """),
        {
            "title": title, "doc_number": doc_number, "doc_type": doc_type,
            "content_html": content_html, "content_text": content_text,
            "is_priority": is_priority, "created_by": admin.id,
        }
    )
    row = result.fetchone()
    await db.commit()
    return {"id": row.id, "title": row.title, "status": "imported"}


@router.post("/api/admin/law-documents/{doc_id}/ai-tag")
async def ai_tag_law_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Use AI (DeepSeek → fallback OpenAI) to auto-tag a law document."""
    result = await db.execute(
        text("SELECT id, title, content_text FROM taxlegal.law_documents_v2 WHERE id=:id"),
        {"id": doc_id}
    )
    doc = result.fetchone()
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")

    from backend.ai_provider import call_ai
    from backend.config import DEEPSEEK_MODEL

    system_prompt = """Bạn là chuyên gia thuế Việt Nam. Phân tích văn bản pháp luật và trả về JSON:
{
  "tags": ["tag1", "tag2", ...],
  "doc_type_suggestion": "luat|nghi_dinh|thong_tu|van_ban_hop_nhat|cong_van|hiep_dinh",
  "issuer": "Tên cơ quan ban hành",
  "summary": "Tóm tắt 1-2 câu nội dung chính"
}
Tags nên là các từ khóa thuế/pháp luật ngắn gọn (VD: "vat", "cit", "fct", "transfer-pricing", "invoice", "penalty").
Chỉ trả về JSON thuần túy."""

    content_preview = (doc.content_text or "")[:8000]
    try:
        result_text = await call_ai(
            model_id=DEEPSEEK_MODEL or "deepseek-chat",
            messages=[{"role": "user", "content": f"Văn bản: {doc.title}\n\nNội dung:\n{content_preview}"}],
            system_prompt=system_prompt,
            max_tokens=500,
            temperature=0.2,
        )
        import json, re
        text_content = result_text.get("content", "") if isinstance(result_text, dict) else str(result_text)
        # Clean markdown code blocks
        text_content = re.sub(r'```json\s*', '', text_content)
        text_content = re.sub(r'```\s*', '', text_content)
        parsed = json.loads(text_content.strip())
        tags = parsed.get("tags", [])
        issuer = parsed.get("issuer", "")

        await db.execute(
            text("UPDATE taxlegal.law_documents_v2 SET tags=:tags, issuer=COALESCE(issuer,:issuer), ai_tagged=TRUE, updated_at=NOW() WHERE id=:id"),
            {"tags": tags, "issuer": issuer, "id": doc_id}
        )
        await db.commit()
        return {"id": doc_id, "tags": tags, "issuer": issuer, "ai_tagged": True}
    except Exception as e:
        logger.error(f"AI tagging failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI tagging failed: {str(e)}")


# ── dbvntax Import ────────────────────────────────────────────────────────────
# dbvntax schema (confirmed): table=documents, columns:
#   id, so_hieu, ten, loai, co_quan, ngay_ban_hanh, hieu_luc_tu, het_hieu_luc_tu,
#   tinh_trang, noi_dung (HTML full text), link_tvpl, sac_thue TEXT[],
#   importance SMALLINT, is_anchor BOOLEAN
# Legal doc types: Luật, Nghị định, Thông tư, Thông tư liên tịch,
#                  Văn bản hợp nhất, Pháp lệnh, Nghị quyết (NOT: Công văn, Thông báo)
_DBVNTAX_LEGAL_TYPES = [
    'Luật', 'Nghị định', 'Thông tư', 'Thông tư liên tịch',
    'Văn bản hợp nhất', 'Pháp lệnh', 'Nghị quyết', 'Quyết định'
]


async def _dbvntax_connect():
    """Return an asyncpg connection to dbvntax. Caller must close."""
    if not DBVNTAX_URL:
        raise HTTPException(status_code=503, detail="DBVNTAX_DATABASE_URL not configured")
    import asyncpg
    db_url = DBVNTAX_URL.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql+psycopg2://", "postgresql://")
    return await asyncpg.connect(db_url)


@router.get("/api/admin/dbvntax/list")
async def list_dbvntax_documents(
    doc_type: Optional[str] = None,
    sac_thue: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    _admin: User = Depends(require_admin),
):
    """
    List tax law documents from dbvntax — only legal docs (not Công văn/Thông báo).
    Supports filtering by doc_type, sac_thue (tax type), and text search.
    """
    conn = await _dbvntax_connect()
    try:
        try:
            # Confirmed: dbvntax uses 'documents' table
            tables_to_try = ["documents", "van_ban", "vanbans", "tax_documents", "laws"]
            table_name = None
            for tbl in tables_to_try:
                try:
                    await conn.fetchrow(f"SELECT 1 FROM {tbl} LIMIT 1")
                    table_name = tbl
                    break
                except Exception:
                    continue

            if not table_name:
                rows = await conn.fetch("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """)
                return {"error": "Could not find document table", "available_tables": [r["table_name"] for r in rows]}

            # Build WHERE clause — exclude Công văn, Thông báo
            conditions = []
            params: list = []

            # Legal types filter (escaped as literals — asyncpg positional params)
            types_literal = ", ".join(f"'{t}'" for t in _DBVNTAX_LEGAL_TYPES)
            conditions.append(f"loai = ANY(ARRAY[{types_literal}]::text[])")

            if doc_type:
                params.append(f"%{doc_type}%")
                conditions.append(f"loai ILIKE ${len(params)}")

            if sac_thue:
                # sac_thue is a TEXT[] column in dbvntax
                sac_thue_esc = sac_thue.replace("'", "''")
                conditions.append(f"sac_thue && ARRAY['{sac_thue_esc}']::text[]")

            if search:
                params.append(f"%{search}%")
                conditions.append(f"(ten ILIKE ${len(params)} OR so_hieu ILIKE ${len(params)})")

            where = " AND ".join(conditions) if conditions else "1=1"
            params.extend([limit, skip])
            query = f"""
                SELECT
                    id,
                    so_hieu,
                    ten,
                    loai,
                    co_quan,
                    ngay_ban_hanh::text AS ngay_ban_hanh,
                    hieu_luc_tu::text AS hieu_luc_tu,
                    tinh_trang,
                    sac_thue,
                    importance,
                    is_anchor,
                    link_tvpl
                FROM {table_name}
                WHERE {where}
                ORDER BY importance ASC NULLS LAST, ngay_ban_hanh DESC NULLS LAST
                LIMIT ${len(params)-1} OFFSET ${len(params)}
            """
            rows = await conn.fetch(query, *params)

            # Count total (without limit/offset)
            count_params = params[:-2]
            cnt = await conn.fetchrow(
                f"SELECT COUNT(*) FROM {table_name} WHERE {where}",
                *count_params
            )
            total = cnt[0] if cnt else len(rows)

            items = []
            for r in rows:
                d = dict(r)
                # sac_thue may be asyncpg List type
                if isinstance(d.get("sac_thue"), (list, tuple)):
                    d["sac_thue"] = list(d["sac_thue"])
                items.append(d)

            return {"items": items, "total": total}
        finally:
            await conn.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"dbvntax list query failed: {e}")
        raise HTTPException(status_code=500, detail=f"dbvntax connection failed: {str(e)}")


@router.get("/api/admin/dbvntax/preview/{doc_id}")
async def preview_dbvntax_document(
    doc_id: int,
    _admin: User = Depends(require_admin),
):
    """
    Return full HTML content of a dbvntax document for preview.
    Used by the 'Import from dbvntax' tab when admin clicks on a row.
    """
    conn = await _dbvntax_connect()
    try:
        row = await conn.fetchrow(
            "SELECT id, so_hieu, ten, loai, co_quan, "
            "ngay_ban_hanh::text, noi_dung, link_tvpl, sac_thue "
            "FROM documents WHERE id = $1",
            doc_id,
        )
        if not row:
            raise HTTPException(status_code=404, detail="Document not found in dbvntax")
        d = dict(row)
        if isinstance(d.get("sac_thue"), (list, tuple)):
            d["sac_thue"] = list(d["sac_thue"])
        return {
            "id": d["id"],
            "so_hieu": d["so_hieu"],
            "ten": d["ten"],
            "loai": d["loai"],
            "co_quan": d["co_quan"],
            "ngay_ban_hanh": d["ngay_ban_hanh"],
            "sac_thue": d["sac_thue"] or [],
            "link_tvpl": d["link_tvpl"],
            "noi_dung_html": d["noi_dung"] or "",
        }
    finally:
        await conn.close()


@router.post("/api/admin/dbvntax/import")
async def import_from_dbvntax(
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    Import selected documents from dbvntax into taxlegal.law_documents_v2.
    Copies sac_thue → tax_types, is_anchor → is_priority.
    body: {"ids": [1, 2, 3], "is_priority": false}
    """
    ids = body.get("ids", [])
    is_priority = body.get("is_priority", False)
    if not ids:
        raise HTTPException(status_code=400, detail="No IDs provided")

    conn = await _dbvntax_connect()
    try:
        id_placeholders = ", ".join([f"${i+1}" for i in range(len(ids))])
        rows = await conn.fetch(
            f"""SELECT id, so_hieu, ten, loai, co_quan,
                       ngay_ban_hanh::text, hieu_luc_tu::text, tinh_trang,
                       noi_dung, link_tvpl, sac_thue, importance, is_anchor
                FROM documents WHERE id = ANY(ARRAY[{id_placeholders}]::integer[])""",
            *ids
        )
    finally:
        await conn.close()

    imported = []
    import re
    for row in rows:
        content_html = row.get("noi_dung") or ""
        content_text = re.sub(r'<[^>]+>', ' ', content_html)
        content_text = re.sub(r'\s+', ' ', content_text).strip()

        # Map loai → doc_type slug
        raw_type = (row.get("loai") or "").lower()
        if "luật" in raw_type:
            doc_type = "luat"
        elif "nghị định" in raw_type:
            doc_type = "nghi_dinh"
        elif "thông tư" in raw_type:
            doc_type = "thong_tu"
        elif "hợp nhất" in raw_type:
            doc_type = "van_ban_hop_nhat"
        elif "pháp lệnh" in raw_type:
            doc_type = "phap_lenh"
        elif "nghị quyết" in raw_type:
            doc_type = "nghi_quyet"
        elif "quyết định" in raw_type:
            doc_type = "quyet_dinh"
        else:
            doc_type = "van_ban_khac"

        # sac_thue → tax_types
        sac_thue = list(row.get("sac_thue") or [])
        # is_anchor OR is_priority param
        doc_is_priority = is_priority or bool(row.get("is_anchor"))
        # importance: 1=Luật, 2=NĐ, 3=TT, etc.
        importance = row.get("importance") or (
            1 if doc_type == "luat" else
            2 if doc_type == "nghi_dinh" else
            3 if doc_type in ("thong_tu", "van_ban_hop_nhat") else 4
        )

        try:
            res = await db.execute(
                text("""
                    INSERT INTO taxlegal.law_documents_v2
                        (title, doc_number, doc_type, issuer, issued_date,
                         content_html, content_text, is_priority, importance,
                         tax_types, link_tvpl, effective_status,
                         imported_from, dbvntax_id, created_by)
                    VALUES
                        (:title, :doc_number, :doc_type, :issuer, :issued_date,
                         :content_html, :content_text, :is_priority, :importance,
                         :tax_types, :link_tvpl, :effective_status,
                         'dbvntax', :dbvntax_id, :created_by)
                    ON CONFLICT DO NOTHING
                    RETURNING id, title
                """),
                {
                    "title": row.get("ten") or "Untitled",
                    "doc_number": row.get("so_hieu"),
                    "doc_type": doc_type,
                    "issuer": row.get("co_quan"),
                    "issued_date": row.get("ngay_ban_hanh"),
                    "content_html": content_html,
                    "content_text": content_text[:100000],
                    "is_priority": doc_is_priority,
                    "importance": importance,
                    "tax_types": sac_thue,
                    "link_tvpl": row.get("link_tvpl"),
                    "effective_status": row.get("tinh_trang") or "con_hieu_luc",
                    "dbvntax_id": row.get("id"),
                    "created_by": admin.id,
                }
            )
            inserted = res.fetchone()
            if inserted:
                imported.append({"id": inserted.id, "title": inserted.title})
        except Exception as e:
            logger.warning(f"Failed to import doc {row.get('id')}: {e}")
            continue

    await db.commit()
    return {"imported": len(imported), "items": imported}


# ── Public API: Search law documents (for regulation picker) ─────────────────

@router.get("/api/law-documents/search")
async def search_law_documents_public(
    q: str = "",
    doc_type: Optional[str] = None,
    is_priority: Optional[bool] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Public search endpoint for regulation picker in matters/writing."""
    conditions = ["is_active = TRUE"]
    params: dict = {"limit": limit}

    if q:
        conditions.append("(title ILIKE :q OR doc_number ILIKE :q OR content_text ILIKE :q)")
        params["q"] = f"%{q}%"
    if doc_type:
        conditions.append("doc_type = :doc_type")
        params["doc_type"] = doc_type
    if is_priority is not None:
        conditions.append("is_priority = :is_priority")
        params["is_priority"] = is_priority

    where = " AND ".join(conditions)
    result = await db.execute(
        text(f"""
            SELECT id, title, doc_number, doc_type, issuer, is_priority, tags
            FROM taxlegal.law_documents_v2
            WHERE {where}
            ORDER BY is_priority DESC, created_at DESC
            LIMIT :limit
        """),
        params
    )
    rows = result.fetchall()
    return [
        {
            "id": r.id, "title": r.title, "doc_number": r.doc_number,
            "doc_type": r.doc_type, "issuer": r.issuer,
            "is_priority": r.is_priority, "tags": r.tags or [],
        }
        for r in rows
    ]


# ── Crawl URL via CrawlKit / direct fetch ────────────────────────────────────


@router.post("/api/admin/law-documents/crawl")
async def crawl_law_document(
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    Crawl a URL from thuvienphapluat.vn (or any legal site) and save as law document.
    body: {"url": "https://...", "is_priority": false, "doc_type": "Thông tư"}
    Uses CrawlKit API if CRAWLKIT_API_KEY is set, otherwise fetches directly.
    """
    url = body.get("url", "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="url required")
    is_priority = body.get("is_priority", False)
    forced_doc_type = body.get("doc_type")

    from backend.services.tvpl_parser import crawl_via_crawlkit, fetch_and_parse_tvpl

    crawlkit_key = os.getenv("CRAWLKIT_API_KEY", "")
    if crawlkit_key:
        parsed = await crawl_via_crawlkit(url, crawlkit_key)
    else:
        parsed = await fetch_and_parse_tvpl(url)

    if parsed.get("error"):
        raise HTTPException(status_code=422, detail=f"Crawl failed: {parsed['error']}")
    if not parsed.get("title") and not parsed.get("content_html"):
        raise HTTPException(status_code=422, detail="No content extracted from URL")

    title = parsed.get("title") or url
    doc_type = forced_doc_type or parsed.get("loai") or "Văn bản khác"

    result = await db.execute(text("""
        INSERT INTO taxlegal.law_documents_v2
            (title, doc_number, doc_type, issuer, issued_date,
             content_html, content_text, source_url, tags,
             is_priority, imported_from, is_active, created_by)
        VALUES
            (:title, :doc_number, :doc_type, :issuer, :issued_date,
             :content_html, :content_text, :source_url, :tags,
             :is_priority, 'crawl', TRUE, :created_by)
        ON CONFLICT (source_url) DO UPDATE SET
            title = EXCLUDED.title,
            content_html = EXCLUDED.content_html,
            content_text = EXCLUDED.content_text,
            updated_at = NOW()
        RETURNING id, title, doc_number, is_priority
    """), {
        "title": title,
        "doc_number": parsed.get("so_hieu", ""),
        "doc_type": doc_type,
        "issuer": parsed.get("co_quan_ban_hanh", ""),
        "issued_date": parsed.get("ngay_ban_hanh") or None,
        "content_html": parsed.get("content_html", ""),
        "content_text": parsed.get("content_text", ""),
        "source_url": url,
        "tags": [],
        "is_priority": is_priority,
        "created_by": admin.id,
    })
    row = result.fetchone()
    await db.commit()
    return {
        "id": row.id, "title": row.title,
        "doc_number": row.doc_number, "is_priority": row.is_priority,
        "status": "crawled"
    }


# ── Laws-to-Skill ─────────────────────────────────────────────────────────────


@router.post("/api/admin/skills/from-laws")
async def create_skill_from_laws(
    body: dict,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    Generate a skill draft from selected law documents.
    body: {"law_ids": [1,2,3], "skill_name": "Optional name", "category": "tax"}
    """
    law_ids = body.get("law_ids", [])
    if not law_ids or len(law_ids) > 10:
        raise HTTPException(status_code=400, detail="Provide 1–10 law_ids")

    from backend.ai_provider import call_ai

    # Fetch law documents
    placeholders = ", ".join([f":id{i}" for i in range(len(law_ids))])
    params = {f"id{i}": lid for i, lid in enumerate(law_ids)}
    result = await db.execute(
        text(f"""
            SELECT id, title, doc_number, doc_type, content_text
            FROM taxlegal.law_documents_v2
            WHERE id IN ({placeholders}) AND is_active = TRUE
        """),
        params
    )
    rows = result.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No law documents found for given IDs")

    # Build context from laws
    law_context = ""
    doc_titles = []
    for row in rows:
        doc_titles.append(f"{row.doc_number or ''} {row.title}".strip())
        excerpt = (row.content_text or "")[:3000]
        law_context += f"\n\n### {row.doc_number or row.title}\n{excerpt}"

    # Detect category from doc types
    all_text = law_context.lower()
    if "tncn" in all_text or "thu nhập cá nhân" in all_text:
        auto_category = "pit"
    elif "tndn" in all_text or "thu nhập doanh nghiệp" in all_text:
        auto_category = "cit"
    elif "gtgt" in all_text or "giá trị gia tăng" in all_text:
        auto_category = "vat"
    elif "hải quan" in all_text or "xuất nhập khẩu" in all_text:
        auto_category = "customs"
    elif "nhà thầu" in all_text or "fct" in all_text:
        auto_category = "fct"
    else:
        auto_category = body.get("category", "tax")

    skill_name = body.get("skill_name") or f"Skill từ {', '.join(doc_titles[:2])}"

    system_prompt = """Bạn là chuyên gia thuế Việt Nam. Tạo một skill file cho AI assistant dựa trên các văn bản pháp luật được cung cấp.

Output PHẢI có format YAML frontmatter + Markdown:
```yaml
---
name: <tên skill>
version: "1.0.0"  
description: <mô tả ngắn>
category: <tax|customs|process>
tags: [tag1, tag2]
applicable_bots: [ja-advisory, ja-compliance]
editable: true
---
```

Sau frontmatter là nội dung markdown với:
1. Tóm tắt quy định chính (bullet points)
2. Các điều khoản quan trọng cần trích dẫn
3. Anti-hallucination rules (KHÔNG bịa đặt)
4. Ví dụ áp dụng thực tế
Viết hoàn toàn bằng tiếng Việt."""

    user_prompt = f"""Tạo skill từ các văn bản pháp luật sau:

Tên skill gợi ý: {skill_name}
Category: {auto_category}

Văn bản pháp luật:
{law_context}

Tạo skill file đầy đủ và chi tiết."""

    try:
        response = await call_ai(
            model_id="deepseek-chat",
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=system_prompt,
            max_tokens=4096,
            temperature=0.3,
        )
        draft_content = response.get("content", "")
    except Exception as e:
        logger.error(f"LLM skill-from-laws failed: {e}")
        draft_content = f"""---
name: {skill_name}
version: "1.0.0"
description: Skill tự động từ {len(rows)} văn bản pháp luật
category: {auto_category}
tags: [{auto_category}]
applicable_bots: [ja-advisory, ja-compliance]
editable: true
---

## Nguồn văn bản
{chr(10).join(f'- {t}' for t in doc_titles)}

## Nội dung chính
[Vui lòng bổ sung nội dung thủ công]
"""

    # Save as skill_draft
    import re as _re
    from datetime import datetime as _dt
    now = _dt.utcnow()
    # Build suggested slug
    suggested_slug = _re.sub(r"[^a-z0-9]+", "-", auto_category + "-from-laws").strip("-")

    draft_result = await db.execute(text("""
        INSERT INTO taxlegal.skill_drafts
            (filename, original_size_bytes, extracted_text, topic_slug, topic_label,
             draft_content, suggested_slug, status, created_by, created_at, updated_at)
        VALUES
            (:filename, :size, :text, :topic_slug, :topic_label,
             :draft_content, :suggested_slug, 'draft', :created_by, :now, :now)
        RETURNING id
    """), {
        "filename": f"from-laws-{'-'.join(str(i) for i in law_ids)}.md",
        "size": len(draft_content),
        "text": law_context[:50000],
        "topic_slug": auto_category,
        "topic_label": auto_category.upper(),
        "draft_content": draft_content,
        "suggested_slug": suggested_slug,
        "created_by": admin.id,
        "now": now,
    })
    draft_row = draft_result.fetchone()
    await db.commit()

    return {
        "draft_id": draft_row[0],
        "suggested_slug": suggested_slug,
        "law_count": len(rows),
        "doc_titles": doc_titles,
        "draft_content": draft_content,
        "message": f"Skill draft created from {len(rows)} law documents. Review and save via /api/skills/draft/{draft_row[0]}/save"
    }
