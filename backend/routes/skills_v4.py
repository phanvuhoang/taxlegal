"""
Skills v4 API — Extended skill management with versioning and bot assignments.

GET    /api/skills/search                   — search skills by name/tag/category
GET    /api/skills/{skill_id}/versions      — list version history
POST   /api/skills/{skill_id}/versions      — create new version (snapshot + increment)
GET    /api/skills/{skill_id}/versions/{v}  — get specific version content
POST   /api/skills/{skill_id}/assign        — assign skill to bot
DELETE /api/skills/{skill_id}/assign/{bot_id} — unassign skill from bot
PATCH  /api/skills/{skill_id}               — update skill (if not in existing skills.py)

NOTE: /api/skills/search MUST be declared BEFORE /api/skills/{skill_id} routes
to avoid FastAPI treating "search" as a skill_id integer.
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.database import get_db
from backend.auth import get_current_user
from backend.models import User

logger = logging.getLogger(__name__)
router = APIRouter(tags=["skills_v4"])


# ── Pydantic schemas ───────────────────────────────────────────────────────────

class SkillVersionCreate(BaseModel):
    content_markdown: str
    change_notes: Optional[str] = None


class SkillAssignToBot(BaseModel):
    bot_id: int


class SkillPatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    applicable_bots: Optional[List[str]] = None
    content_markdown: Optional[str] = None
    is_active: Optional[bool] = None


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _get_skill_or_404(db: AsyncSession, skill_id: int) -> dict:
    try:
        result = await db.execute(
            text("SELECT * FROM taxlegal.skills WHERE id = :id"),
            {"id": skill_id},
        )
        row = result.mappings().one_or_none()
    except Exception as e:
        logger.warning(f"skills query error: {e}")
        raise HTTPException(status_code=404, detail="Skill not found")

    if not row:
        raise HTTPException(status_code=404, detail="Skill not found")
    return dict(row)


def _serialize_skill(row: dict) -> dict:
    out = dict(row)
    for k in ("created_at", "updated_at"):
        if out.get(k) and hasattr(out[k], "isoformat"):
            out[k] = out[k].isoformat()
    return out


# ── Routes — search MUST come before {skill_id} path params ───────────────────

@router.get("/api/skills/search")
async def search_skills(
    q: Optional[str] = Query(None, description="Search query (name/description)"),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search skills by name, tag, or category."""
    try:
        filters = []
        params: dict = {"skip": skip, "limit": limit}

        if q:
            filters.append("(name ILIKE :q OR description ILIKE :q)")
            params["q"] = f"%{q}%"
        if category:
            filters.append("category = :category")
            params["category"] = category
        if tag:
            filters.append(":tag = ANY(tags)")
            params["tag"] = tag
        if is_active is not None:
            filters.append("is_active = :is_active")
            params["is_active"] = is_active

        where = "WHERE " + " AND ".join(filters) if filters else ""
        result = await db.execute(
            text(f"""
                SELECT id, name, version, description, category, tags,
                       applicable_bots, is_active, is_builtin, created_at
                FROM taxlegal.skills
                {where}
                ORDER BY name
                LIMIT :limit OFFSET :skip
            """),
            params,
        )
        rows = result.mappings().all()
    except Exception as e:
        logger.warning(f"skills search error: {e}")
        return []

    return [_serialize_skill(dict(r)) for r in rows]


@router.get("/api/skills/{skill_id}/versions")
async def list_skill_versions(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List version history for a skill."""
    await _get_skill_or_404(db, skill_id)

    try:
        result = await db.execute(
            text("""
                SELECT id, skill_id, version_number, content_markdown,
                       change_notes, created_by, created_at
                FROM taxlegal.skill_versions
                WHERE skill_id = :skill_id
                ORDER BY version_number DESC
            """),
            {"skill_id": skill_id},
        )
        rows = result.mappings().all()
    except Exception as e:
        logger.warning(f"skill_versions query error: {e}")
        return []

    return [
        {
            "id": str(r["id"]) if r["id"] else None,
            "skill_id": r["skill_id"],
            "version_number": r["version_number"],
            "change_notes": r["change_notes"],
            "created_by": r["created_by"],
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            # Omit full content_markdown in list for brevity
        }
        for r in rows
    ]


@router.post("/api/skills/{skill_id}/versions", status_code=201)
async def create_skill_version(
    skill_id: int,
    req: SkillVersionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new version of a skill:
    1. Snapshot the CURRENT version into taxlegal.skill_versions
    2. Update the skill's version_number += 1 and content_markdown with new content
    """
    skill = await _get_skill_or_404(db, skill_id)
    now = datetime.utcnow()

    current_version = skill.get("version_number") or 1
    current_content = skill.get("content_markdown") or ""
    version_id = str(uuid.uuid4())

    # Step 1: Snapshot CURRENT version
    try:
        await db.execute(
            text("""
                INSERT INTO taxlegal.skill_versions
                    (id, skill_id, version_number, content_markdown,
                     change_notes, created_by, created_at)
                VALUES
                    (:id, :skill_id, :version_number, :content_markdown,
                     :change_notes, :created_by, :now)
            """),
            {
                "id": version_id,
                "skill_id": skill_id,
                "version_number": current_version,
                "content_markdown": current_content,
                "change_notes": f"Snapshot before version {current_version + 1}",
                "created_by": current_user.id,
                "now": now,
            },
        )
    except Exception as e:
        logger.warning(f"skill_versions snapshot insert failed: {e}")

    # Step 2: Update skill with new content and incremented version
    new_version = current_version + 1
    try:
        await db.execute(
            text("""
                UPDATE taxlegal.skills
                SET version_number = :new_version,
                    content_markdown = :new_content,
                    updated_at = :now
                WHERE id = :skill_id
            """),
            {
                "new_version": new_version,
                "new_content": req.content_markdown,
                "now": now,
                "skill_id": skill_id,
            },
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to update skill version: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update skill: {e}")

    return {
        "skill_id": skill_id,
        "previous_version": current_version,
        "new_version": new_version,
        "snapshot_id": version_id,
        "created_at": now.isoformat(),
    }


@router.get("/api/skills/{skill_id}/versions/{version_number}")
async def get_skill_version(
    skill_id: int,
    version_number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get specific version content for a skill."""
    await _get_skill_or_404(db, skill_id)

    try:
        result = await db.execute(
            text("""
                SELECT id, skill_id, version_number, content_markdown,
                       change_notes, created_by, created_at
                FROM taxlegal.skill_versions
                WHERE skill_id = :skill_id AND version_number = :version_number
                LIMIT 1
            """),
            {"skill_id": skill_id, "version_number": version_number},
        )
        row = result.mappings().one_or_none()
    except Exception as e:
        logger.warning(f"skill_versions fetch error: {e}")
        raise HTTPException(status_code=404, detail="Version not found")

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Version {version_number} not found for skill {skill_id}",
        )

    return {
        "id": str(row["id"]) if row["id"] else None,
        "skill_id": row["skill_id"],
        "version_number": row["version_number"],
        "content_markdown": row["content_markdown"],
        "change_notes": row["change_notes"],
        "created_by": row["created_by"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
    }


@router.post("/api/skills/{skill_id}/assign", status_code=201)
async def assign_skill_to_bot(
    skill_id: int,
    req: SkillAssignToBot,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Assign a skill to a bot."""
    await _get_skill_or_404(db, skill_id)
    now = datetime.utcnow()

    # Verify bot exists
    try:
        bot_result = await db.execute(
            text("SELECT id, skill_ids FROM taxlegal.bot_variants WHERE id = :id"),
            {"id": req.bot_id},
        )
        bot_row = bot_result.mappings().one_or_none()
        if not bot_row:
            raise HTTPException(status_code=404, detail=f"Bot {req.bot_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"bot lookup error: {e}")
        raise HTTPException(status_code=404, detail="Bot not found")

    # Insert into bot_skill_assignments
    try:
        await db.execute(
            text("""
                INSERT INTO taxlegal.bot_skill_assignments (bot_id, skill_id, assigned_at)
                VALUES (:bot_id, :skill_id, :now)
                ON CONFLICT (bot_id, skill_id) DO NOTHING
            """),
            {"bot_id": req.bot_id, "skill_id": skill_id, "now": now},
        )
    except Exception as e:
        logger.warning(f"bot_skill_assignments insert failed: {e}")

    # Also update skill_ids array on bot_variants
    try:
        current_ids = bot_row.get("skill_ids") or []
        if isinstance(current_ids, str):
            current_ids = json.loads(current_ids)
        if skill_id not in current_ids:
            current_ids.append(skill_id)
            await db.execute(
                text("""
                    UPDATE taxlegal.bot_variants
                    SET skill_ids = :ids, updated_at = :now
                    WHERE id = :bot_id
                """),
                {"ids": current_ids, "now": now, "bot_id": req.bot_id},
            )
    except Exception as e:
        logger.warning(f"skill_ids array update failed: {e}")

    await db.commit()

    return {
        "skill_id": skill_id,
        "bot_id": req.bot_id,
        "assigned_at": now.isoformat(),
    }


@router.delete("/api/skills/{skill_id}/assign/{bot_id}", status_code=204)
async def unassign_skill_from_bot(
    skill_id: int,
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unassign a skill from a bot."""
    await _get_skill_or_404(db, skill_id)
    now = datetime.utcnow()

    try:
        result = await db.execute(
            text("""
                DELETE FROM taxlegal.bot_skill_assignments
                WHERE bot_id = :bot_id AND skill_id = :skill_id
            """),
            {"bot_id": bot_id, "skill_id": skill_id},
        )
        rows_deleted = result.rowcount
    except Exception as e:
        logger.warning(f"bot_skill_assignments delete error: {e}")
        rows_deleted = 0

    # Also remove from skill_ids array on bot_variants
    try:
        bot_result = await db.execute(
            text("SELECT skill_ids FROM taxlegal.bot_variants WHERE id = :id"),
            {"id": bot_id},
        )
        bot_row = bot_result.mappings().one_or_none()
        if bot_row:
            current_ids = bot_row.get("skill_ids") or []
            if isinstance(current_ids, str):
                current_ids = json.loads(current_ids)
            if skill_id in current_ids:
                current_ids = [x for x in current_ids if x != skill_id]
                await db.execute(
                    text("""
                        UPDATE taxlegal.bot_variants
                        SET skill_ids = :ids, updated_at = :now
                        WHERE id = :bot_id
                    """),
                    {"ids": current_ids, "now": now, "bot_id": bot_id},
                )
    except Exception as e:
        logger.warning(f"skill_ids array cleanup failed: {e}")

    await db.commit()

    if rows_deleted == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Skill {skill_id} is not assigned to bot {bot_id}",
        )


@router.patch("/api/skills/{skill_id}")
async def patch_skill(
    skill_id: int,
    req: SkillPatch,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Partial update of a skill.
    (This endpoint exists in skills_v4 — existing skills.py has PUT /api/admin/skills/{id}.)
    """
    await _get_skill_or_404(db, skill_id)

    updates = req.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    now = datetime.utcnow()
    set_clauses = ", ".join([f"{k} = :{k}" for k in updates])
    set_clauses += ", updated_at = :now"
    updates["now"] = now
    updates["skill_id"] = skill_id

    try:
        await db.execute(
            text(f"UPDATE taxlegal.skills SET {set_clauses} WHERE id = :skill_id"),
            updates,
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to patch skill {skill_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Update failed: {e}")

    skill = await _get_skill_or_404(db, skill_id)
    return _serialize_skill(skill)
