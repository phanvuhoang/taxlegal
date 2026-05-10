"""
Document-to-Skill Draft API

POST /api/skills/from-document   — draft from URL of already-uploaded file
POST /api/skills/from-upload     — multipart upload PDF/PPTX/DOCX
GET  /api/skills/drafts          — list user's drafts
GET  /api/skills/draft/{id}      — get draft (full content)
PATCH /api/skills/draft/{id}     — update draft before saving
POST /api/skills/draft/{id}/save — promote draft to skill
DELETE /api/skills/draft/{id}    — discard draft (soft delete)
GET  /api/skills/{id}/source-lineage — provenance for a skill

NOTE: Register this router BEFORE skills_v4_router in main.py so FastAPI
      does not try to parse "draft" / "drafts" / "from-upload" as integer IDs.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.database import get_db
from backend.auth import get_current_user
from backend.models import User
from backend.services.skill_drafter import (
    extract_text,
    detect_topic,
    create_draft_from_document,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["skill_drafts"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".pptx", ".ppt"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


# ── Pydantic schemas ────────────────────────────────────────────────────────

class DraftFromDocumentRequest(BaseModel):
    """Draft a skill from a URL pointing to an already-uploaded file."""
    file_url: str
    filename: str
    topic_hint: Optional[str] = None


class DraftPatch(BaseModel):
    """Partial update on a draft before saving."""
    draft_content: Optional[str] = None
    suggested_slug: Optional[str] = None
    topic_slug: Optional[str] = None
    topic_label: Optional[str] = None


class DraftSaveRequest(BaseModel):
    """Finalize a draft as a new skill."""
    slug: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = "tax"
    tags: Optional[list[str]] = None
    applicable_bots: Optional[list[str]] = None


# ── Helpers ─────────────────────────────────────────────────────────────────

def _ext(filename: str) -> str:
    from pathlib import Path
    return Path(filename).suffix.lower()


def _serialize_draft(row: dict) -> dict:
    out = dict(row)
    for k in ("created_at", "updated_at"):
        if out.get(k) and hasattr(out[k], "isoformat"):
            out[k] = out[k].isoformat()
    return out


async def _get_draft_or_404(db: AsyncSession, draft_id: int, user_id: int) -> dict:
    try:
        result = await db.execute(
            text("SELECT * FROM taxlegal.skill_drafts WHERE id = :id"),
            {"id": draft_id},
        )
        row = result.mappings().one_or_none()
    except Exception as e:
        logger.warning(f"skill_drafts query error: {e}")
        raise HTTPException(status_code=404, detail="Draft not found")
    if not row:
        raise HTTPException(status_code=404, detail="Draft not found")
    if row["created_by"] is not None and row["created_by"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return dict(row)


async def _insert_draft(db: AsyncSession, *, filename: str, original_size_bytes: int,
                        extracted_text: str, topic_slug: str, topic_label: str,
                        draft_content: str, suggested_slug: str, created_by: int) -> dict:
    now = datetime.utcnow()
    try:
        result = await db.execute(
            text("""
                INSERT INTO taxlegal.skill_drafts
                    (filename, original_size_bytes, extracted_text,
                     topic_slug, topic_label, draft_content, suggested_slug,
                     status, created_by, created_at, updated_at)
                VALUES
                    (:filename, :size, :text,
                     :topic_slug, :topic_label, :draft_content, :suggested_slug,
                     'draft', :created_by, :now, :now)
                RETURNING *
            """),
            {
                "filename": filename,
                "size": original_size_bytes,
                "text": extracted_text,
                "topic_slug": topic_slug,
                "topic_label": topic_label,
                "draft_content": draft_content,
                "suggested_slug": suggested_slug,
                "created_by": created_by,
                "now": now,
            },
        )
        row = result.mappings().one()
        await db.commit()
        return dict(row)
    except Exception as e:
        logger.error(f"skill_drafts insert failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create draft: {e}")


async def _process_document(data: bytes, filename: str, topic_hint: Optional[str]) -> dict:
    """
    Extract text, detect topic, and generate draft via skill_drafter.create_draft_from_document.
    Returns the result dict from create_draft_from_document.
    """
    # create_draft_from_document handles extraction + topic detection + LLM draft
    result = await create_draft_from_document(
        filename=filename,
        data=data,
        ai_provider=None,   # not used — generate_draft_skill calls call_ai() directly
        use_llm=True,
    )

    if result.get("error"):
        raise HTTPException(status_code=422, detail=result["error"])
    if not result.get("extracted_text", "").strip():
        raise HTTPException(status_code=422, detail="No text could be extracted from the document")

    # Apply topic_hint override if provided
    if topic_hint:
        from backend.services.skill_drafter import TOPIC_PATTERNS
        hint_lower = topic_hint.lower()
        for _pattern, slug, label in TOPIC_PATTERNS:
            if hint_lower in slug or hint_lower in label.lower():
                result["topic_slug"] = slug
                result["topic_label"] = label
                break

    return result


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/api/skills/from-upload", status_code=201)
async def draft_skill_from_upload(
    file: UploadFile = File(...),
    topic_hint: Optional[str] = Query(None, description="Optional topic hint: pit, vat, customs, cit, fct"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a PDF, DOCX, or PPTX and generate a draft skill from its content.
    Returns a skill_draft record with editable draft_content and suggested_slug.
    """
    filename = file.filename or "upload.pdf"
    if _ext(filename) not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{_ext(filename)}'. Allowed: pdf, docx, pptx",
        )

    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 20 MB)")

    result = await _process_document(data, filename, topic_hint)

    row = await _insert_draft(
        db,
        filename=filename,
        original_size_bytes=len(data),
        extracted_text=result["extracted_text"][:50000],
        topic_slug=result["topic_slug"],
        topic_label=result["topic_label"],
        draft_content=result["draft_content"],
        suggested_slug=result["suggested_slug"],
        created_by=current_user.id,
    )
    return _serialize_draft(row)


@router.post("/api/skills/from-document", status_code=201)
async def draft_skill_from_document_url(
    req: DraftFromDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Draft a skill from a file URL (already uploaded to object storage or any public URL).
    Fetches the URL, extracts text, and generates draft skill content.
    """
    import httpx

    filename = req.filename
    if _ext(filename) not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type for '{filename}'")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(req.file_url)
            resp.raise_for_status()
            data = resp.content
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to fetch document: {e}")

    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 20 MB)")

    result = await _process_document(data, filename, req.topic_hint)

    row = await _insert_draft(
        db,
        filename=filename,
        original_size_bytes=len(data),
        extracted_text=result["extracted_text"][:50000],
        topic_slug=result["topic_slug"],
        topic_label=result["topic_label"],
        draft_content=result["draft_content"],
        suggested_slug=result["suggested_slug"],
        created_by=current_user.id,
    )
    return _serialize_draft(row)


@router.get("/api/skills/drafts")
async def list_drafts(
    status: Optional[str] = Query(None, description="Filter by status: draft | saved | discarded"),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List skill drafts created by the current user."""
    try:
        params: dict = {"user_id": current_user.id, "skip": skip, "limit": limit}
        where_extra = ""
        if status:
            where_extra = " AND status = :status"
            params["status"] = status
        result = await db.execute(
            text(f"""
                SELECT id, filename, original_size_bytes, topic_slug, topic_label,
                       suggested_slug, status, saved_skill_id, created_at, updated_at
                FROM taxlegal.skill_drafts
                WHERE created_by = :user_id{where_extra}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :skip
            """),
            params,
        )
        rows = result.mappings().all()
    except Exception as e:
        logger.warning(f"skill_drafts list error: {e}")
        return []
    return [_serialize_draft(dict(r)) for r in rows]


@router.get("/api/skills/draft/{draft_id}")
async def get_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a skill draft by ID (includes full draft_content)."""
    row = await _get_draft_or_404(db, draft_id, current_user.id)
    return _serialize_draft(row)


@router.patch("/api/skills/draft/{draft_id}")
async def update_draft(
    draft_id: int,
    req: DraftPatch,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Partially update a draft — edit content or slug before saving."""
    await _get_draft_or_404(db, draft_id, current_user.id)

    updates = req.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    now = datetime.utcnow()
    set_parts = [f"{k} = :{k}" for k in updates]
    set_parts.append("updated_at = :now")
    updates["now"] = now
    updates["draft_id"] = draft_id

    try:
        await db.execute(
            text(f"UPDATE taxlegal.skill_drafts SET {', '.join(set_parts)} WHERE id = :draft_id"),
            updates,
        )
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {e}")

    row = await _get_draft_or_404(db, draft_id, current_user.id)
    return _serialize_draft(row)


@router.post("/api/skills/draft/{draft_id}/save", status_code=201)
async def save_draft_as_skill(
    draft_id: int,
    req: DraftSaveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Promote a draft to a real skill.
    Creates a new record in taxlegal.skills and marks the draft as 'saved'.
    """
    draft = await _get_draft_or_404(db, draft_id, current_user.id)

    if draft["status"] == "saved":
        raise HTTPException(status_code=409, detail="Draft already saved as a skill")
    if draft["status"] == "discarded":
        raise HTTPException(status_code=409, detail="Draft has been discarded")

    slug = req.slug or draft.get("suggested_slug") or f"doc-skill-{draft_id}"
    name = req.name or (draft.get("topic_label") or slug).replace("-", " ").title()
    category = req.category or "tax"
    tags_val = req.tags or ([draft["topic_slug"]] if draft.get("topic_slug") else [])
    applicable_bots_val = req.applicable_bots or []
    content = draft.get("draft_content") or ""
    now = datetime.utcnow()

    # Check slug uniqueness
    try:
        existing = await db.execute(
            text("SELECT id FROM taxlegal.skills WHERE slug = :slug"),
            {"slug": slug},
        )
        if existing.one_or_none():
            raise HTTPException(
                status_code=409,
                detail=f"A skill with slug '{slug}' already exists. Provide a different slug.",
            )
    except HTTPException:
        raise
    except Exception:
        pass

    # Insert skill
    try:
        result = await db.execute(
            text("""
                INSERT INTO taxlegal.skills
                    (name, slug, version, version_number, description, category, tags,
                     applicable_bots, content_markdown, is_builtin, is_active,
                     created_at, updated_at)
                VALUES
                    (:name, :slug, '1.0.0', 1, :description, :category, :tags,
                     :applicable_bots, :content, FALSE, TRUE,
                     :now, :now)
                RETURNING id
            """),
            {
                "name": name,
                "slug": slug,
                "description": f"Drafted from document: {draft['filename']}",
                "category": category,
                "tags": tags_val,
                "applicable_bots": applicable_bots_val,
                "content": content,
                "now": now,
            },
        )
        skill_id = result.one()[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"skill insert failed when saving draft: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create skill: {e}")

    # Mark draft as saved
    try:
        await db.execute(
            text("""
                UPDATE taxlegal.skill_drafts
                SET status = 'saved', saved_skill_id = :skill_id, updated_at = :now
                WHERE id = :draft_id
            """),
            {"skill_id": skill_id, "now": now, "draft_id": draft_id},
        )
        await db.commit()
    except Exception as e:
        logger.warning(f"skill_drafts status update failed: {e}")

    return {
        "skill_id": skill_id,
        "slug": slug,
        "name": name,
        "draft_id": draft_id,
        "saved_at": now.isoformat(),
    }


@router.delete("/api/skills/draft/{draft_id}", status_code=204)
async def discard_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a draft as discarded (soft delete)."""
    await _get_draft_or_404(db, draft_id, current_user.id)
    now = datetime.utcnow()
    try:
        await db.execute(
            text("""
                UPDATE taxlegal.skill_drafts
                SET status = 'discarded', updated_at = :now
                WHERE id = :draft_id
            """),
            {"now": now, "draft_id": draft_id},
        )
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discard failed: {e}")


@router.get("/api/skills/{skill_id}/source-lineage")
async def get_skill_source_lineage(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return provenance information for a skill — originating draft + source document metadata."""
    try:
        skill_result = await db.execute(
            text("SELECT id, name, slug, version, created_at FROM taxlegal.skills WHERE id = :id"),
            {"id": skill_id},
        )
        skill_row = skill_result.mappings().one_or_none()
    except Exception:
        raise HTTPException(status_code=404, detail="Skill not found")

    if not skill_row:
        raise HTTPException(status_code=404, detail="Skill not found")

    draft_info = None
    try:
        draft_result = await db.execute(
            text("""
                SELECT id, filename, original_size_bytes, topic_slug, topic_label, created_at
                FROM taxlegal.skill_drafts
                WHERE saved_skill_id = :skill_id
                LIMIT 1
            """),
            {"skill_id": skill_id},
        )
        draft_row = draft_result.mappings().one_or_none()
        if draft_row:
            draft_info = {
                "draft_id": draft_row["id"],
                "filename": draft_row["filename"],
                "original_size_bytes": draft_row["original_size_bytes"],
                "topic_slug": draft_row["topic_slug"],
                "topic_label": draft_row["topic_label"],
                "drafted_at": draft_row["created_at"].isoformat() if draft_row["created_at"] else None,
            }
    except Exception as e:
        logger.warning(f"lineage draft lookup error: {e}")

    return {
        "skill_id": skill_id,
        "skill_name": skill_row["name"],
        "skill_slug": skill_row["slug"],
        "skill_version": skill_row["version"],
        "created_at": skill_row["created_at"].isoformat() if skill_row["created_at"] else None,
        "source_type": "document_draft" if draft_info else "manual_seed",
        "source_document": draft_info,
    }
