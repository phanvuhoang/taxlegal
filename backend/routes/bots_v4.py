"""
Bots API v4 — TaxLegal v4 bot definition management.

POST   /api/bots                            — create bot definition
PATCH  /api/bots/{bot_id}                   — update bot (model, prompt, skills)
GET    /api/bots                            — list all bots
GET    /api/bots/{bot_id}                   — get bot detail with skill assignments
POST   /api/bots/{bot_id}/skills            — assign skill to bot
DELETE /api/bots/{bot_id}/skills/{skill_id} — remove skill from bot
GET    /api/bots/{bot_id}/preview-prompt    — preview assembled system prompt
"""
import json
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.database import get_db
from backend.auth import get_current_user
from backend.models import User

logger = logging.getLogger(__name__)
router = APIRouter(tags=["bots"])


# ── Pydantic schemas ───────────────────────────────────────────────────────────

class BotDefinitionCreate(BaseModel):
    name: str
    slug: str
    role: str
    description: Optional[str] = None
    system_prompt_base: Optional[str] = None
    model_override: Optional[str] = None
    provider_override: Optional[str] = None
    is_active: bool = True


class BotDefinitionUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    system_prompt_base: Optional[str] = None
    model_override: Optional[str] = None
    provider_override: Optional[str] = None
    is_active: Optional[bool] = None


class SkillAssignRequest(BaseModel):
    skill_id: int


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _get_bot_or_404(db: AsyncSession, bot_id: int) -> dict:
    try:
        result = await db.execute(
            text("SELECT * FROM taxlegal.bot_variants WHERE id = :id"),
            {"id": bot_id},
        )
        row = result.mappings().one_or_none()
    except Exception as e:
        logger.warning(f"bot_variants query error: {e}")
        raise HTTPException(status_code=404, detail="Bot not found")

    if not row:
        raise HTTPException(status_code=404, detail="Bot not found")
    return dict(row)


def _serialize_bot(row: dict) -> dict:
    out = dict(row)
    for k in ("created_at", "updated_at"):
        if out.get(k) and hasattr(out[k], "isoformat"):
            out[k] = out[k].isoformat()
    return out


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post("/api/bots", status_code=201)
async def create_bot(
    req: BotDefinitionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new bot definition."""
    # Check for slug conflict
    try:
        existing = await db.execute(
            text("SELECT id FROM taxlegal.bot_variants WHERE slug = :slug"),
            {"slug": req.slug},
        )
        if existing.one_or_none():
            raise HTTPException(status_code=409, detail=f"Bot with slug '{req.slug}' already exists")
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"slug check error: {e}")

    now = datetime.utcnow()
    try:
        result = await db.execute(
            text("""
                INSERT INTO taxlegal.bot_variants
                    (name, slug, role, description, system_prompt_base,
                     skill_ids, model_override, provider_override,
                     is_active, is_builtin, created_at, updated_at)
                VALUES
                    (:name, :slug, :role, :description, :system_prompt_base,
                     '[]', :model_override, :provider_override,
                     :is_active, FALSE, :now, :now)
                RETURNING id
            """),
            {
                "name": req.name,
                "slug": req.slug,
                "role": req.role,
                "description": req.description,
                "system_prompt_base": req.system_prompt_base,
                "model_override": req.model_override,
                "provider_override": req.provider_override,
                "is_active": req.is_active,
                "now": now,
            },
        )
        row = result.one_or_none()
        bot_id = row[0] if row else None
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create bot: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create bot: {e}")

    return {
        "id": bot_id,
        "name": req.name,
        "slug": req.slug,
        "role": req.role,
        "description": req.description,
        "system_prompt_base": req.system_prompt_base,
        "model_override": req.model_override,
        "provider_override": req.provider_override,
        "is_active": req.is_active,
        "is_builtin": False,
        "skill_ids": [],
        "created_at": now.isoformat(),
    }


@router.patch("/api/bots/{bot_id}")
async def update_bot(
    bot_id: int,
    req: BotDefinitionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a bot definition (model, prompt, skills, etc.)."""
    await _get_bot_or_404(db, bot_id)

    now = datetime.utcnow()
    updates = req.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clauses = ", ".join([f"{k} = :{k}" for k in updates])
    set_clauses += ", updated_at = :now"
    updates["now"] = now
    updates["bot_id"] = bot_id

    try:
        await db.execute(
            text(f"UPDATE taxlegal.bot_variants SET {set_clauses} WHERE id = :bot_id"),
            updates,
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to update bot {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Update failed: {e}")

    bot = await _get_bot_or_404(db, bot_id)
    return _serialize_bot(bot)


@router.get("/api/bots")
async def list_bots(
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all bot definitions."""
    try:
        filters = []
        params: dict = {}
        if role:
            filters.append("role = :role")
            params["role"] = role
        if is_active is not None:
            filters.append("is_active = :is_active")
            params["is_active"] = is_active

        where = "WHERE " + " AND ".join(filters) if filters else ""
        result = await db.execute(
            text(f"""
                SELECT id, name, slug, role, description, system_prompt_base,
                       skill_ids, model_override, provider_override,
                       is_active, is_builtin, created_at, updated_at
                FROM taxlegal.bot_variants
                {where}
                ORDER BY role, name
            """),
            params,
        )
        rows = result.mappings().all()
    except Exception as e:
        logger.warning(f"bot_variants list error: {e}")
        return []

    return [_serialize_bot(dict(r)) for r in rows]


@router.get("/api/bots/{bot_id}")
async def get_bot(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get bot detail with skill assignments."""
    bot = await _get_bot_or_404(db, bot_id)
    result = _serialize_bot(bot)

    # Fetch skill assignments from bot_skill_assignments table
    try:
        assignments_result = await db.execute(
            text("""
                SELECT bsa.skill_id, s.name, s.description, s.category, s.version
                FROM taxlegal.bot_skill_assignments bsa
                JOIN taxlegal.skills s ON s.id = bsa.skill_id
                WHERE bsa.bot_id = :bot_id
                ORDER BY s.name
            """),
            {"bot_id": bot_id},
        )
        assignments = [dict(r) for r in assignments_result.mappings().all()]
        result["skill_assignments"] = assignments
    except Exception as e:
        logger.warning(f"skill_assignments query error: {e}")
        result["skill_assignments"] = []

    return result


@router.post("/api/bots/{bot_id}/skills", status_code=201)
async def assign_skill_to_bot(
    bot_id: int,
    req: SkillAssignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Assign a skill to a bot."""
    bot = await _get_bot_or_404(db, bot_id)
    now = datetime.utcnow()

    # Verify skill exists
    try:
        skill_result = await db.execute(
            text("SELECT id, name FROM taxlegal.skills WHERE id = :id"),
            {"id": req.skill_id},
        )
        skill_row = skill_result.one_or_none()
        if not skill_row:
            raise HTTPException(status_code=404, detail=f"Skill {req.skill_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"skill lookup error: {e}")
        raise HTTPException(status_code=404, detail="Skill not found")

    # Insert into bot_skill_assignments
    try:
        await db.execute(
            text("""
                INSERT INTO taxlegal.bot_skill_assignments (bot_id, skill_id, assigned_at)
                VALUES (:bot_id, :skill_id, :now)
                ON CONFLICT (bot_id, skill_id) DO NOTHING
            """),
            {"bot_id": bot_id, "skill_id": req.skill_id, "now": now},
        )
    except Exception as e:
        logger.warning(f"bot_skill_assignments insert failed: {e}")

    # Also update bot_variants.skill_ids array
    try:
        current_ids = bot.get("skill_ids") or []
        if isinstance(current_ids, str):
            current_ids = json.loads(current_ids)
        if req.skill_id not in current_ids:
            current_ids.append(req.skill_id)
            await db.execute(
                text("""
                    UPDATE taxlegal.bot_variants
                    SET skill_ids = :ids, updated_at = :now
                    WHERE id = :bot_id
                """),
                {"ids": current_ids, "now": now, "bot_id": bot_id},
            )
    except Exception as e:
        logger.warning(f"skill_ids update failed: {e}")

    await db.commit()

    return {
        "bot_id": bot_id,
        "skill_id": req.skill_id,
        "assigned_at": now.isoformat(),
    }


@router.delete("/api/bots/{bot_id}/skills/{skill_id}", status_code=204)
async def remove_skill_from_bot(
    bot_id: int,
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a skill assignment from a bot."""
    bot = await _get_bot_or_404(db, bot_id)
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

    # Also remove from skill_ids array
    try:
        current_ids = bot.get("skill_ids") or []
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
        logger.warning(f"skill_ids array update failed: {e}")

    await db.commit()

    if rows_deleted == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Skill {skill_id} is not assigned to bot {bot_id}",
        )


@router.get("/api/bots/{bot_id}/preview-prompt")
async def preview_bot_prompt(
    bot_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Preview the assembled system prompt for a bot.
    Loads the bot's system_prompt_base, fetches all assigned skills,
    and assembles the final prompt (NOT sending to AI — just assembly).
    """
    bot = await _get_bot_or_404(db, bot_id)

    base_prompt = bot.get("system_prompt_base") or ""

    # Load all assigned skills via bot_skill_assignments
    skill_sections: list[str] = []
    try:
        assignments_result = await db.execute(
            text("""
                SELECT s.name, s.description, s.content_markdown
                FROM taxlegal.bot_skill_assignments bsa
                JOIN taxlegal.skills s ON s.id = bsa.skill_id
                WHERE bsa.bot_id = :bot_id AND s.is_active = TRUE
                ORDER BY s.name
            """),
            {"bot_id": bot_id},
        )
        skill_rows = assignments_result.mappings().all()
    except Exception as e:
        logger.warning(f"skill fetch for preview failed: {e}")
        skill_rows = []

    # Fallback: load via skill_ids array
    if not skill_rows:
        try:
            skill_ids = bot.get("skill_ids") or []
            if isinstance(skill_ids, str):
                skill_ids = json.loads(skill_ids)
            if skill_ids:
                placeholders = ", ".join([f":s{i}" for i in range(len(skill_ids))])
                params = {f"s{i}": sid for i, sid in enumerate(skill_ids)}
                result = await db.execute(
                    text(f"""
                        SELECT name, description, content_markdown
                        FROM taxlegal.skills
                        WHERE id IN ({placeholders}) AND is_active = TRUE
                        ORDER BY name
                    """),
                    params,
                )
                skill_rows = result.mappings().all()
        except Exception as e:
            logger.warning(f"skill_ids fallback fetch failed: {e}")
            skill_rows = []

    # Assemble prompt
    for skill in skill_rows:
        section = f"\n\n## Skill: {skill['name']}"
        if skill.get("description"):
            section += f"\n_{skill['description']}_"
        section += f"\n\n{skill['content_markdown']}"
        skill_sections.append(section)

    assembled_prompt = base_prompt
    if skill_sections:
        assembled_prompt += "\n\n---\n# Injected Skills\n" + "\n".join(skill_sections)

    return {
        "bot_id": bot_id,
        "bot_name": bot.get("name"),
        "skill_count": len(skill_rows),
        "assembled_prompt": assembled_prompt,
        "base_prompt_length": len(base_prompt),
        "total_length": len(assembled_prompt),
    }
