"""
Skills, BotVariants, and PipelineTemplates API routes.

Admin routes (require admin role):
  GET/POST/PUT/DELETE /api/admin/skills
  GET/POST/PUT/DELETE /api/admin/bot-variants
  GET/POST/PUT/DELETE /api/admin/pipeline-templates

Public routes (authenticated users):
  GET /api/pipeline-templates  — list active templates for matter creation
"""
import json
import logging
from typing import Optional, List, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.database import get_db
from backend.models import Skill, BotVariant, PipelineTemplate, User
from backend.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["skills"])


# ── Dependency: require admin ─────────────────────────────────────────────────

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class SkillCreate(BaseModel):
    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    category: str = "tax"
    tags: Optional[List[str]] = []
    applicable_bots: Optional[List[str]] = []
    content_markdown: str
    frontmatter: Optional[Any] = {}
    is_active: bool = True


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    applicable_bots: Optional[List[str]] = None
    content_markdown: Optional[str] = None
    frontmatter: Optional[Any] = None
    is_active: Optional[bool] = None


class SkillOut(BaseModel):
    id: int
    name: str
    version: str
    description: Optional[str]
    category: str
    tags: Optional[List[str]]
    applicable_bots: Optional[List[str]]
    content_markdown: str
    frontmatter: Optional[Any]
    is_active: bool
    is_builtin: bool
    created_at: Optional[str]

    class Config:
        from_attributes = True


class BotVariantCreate(BaseModel):
    name: str
    slug: str
    role: str
    description: Optional[str] = None
    system_prompt_base: Optional[str] = None
    skill_ids: Optional[List[int]] = []
    model_override: Optional[str] = None
    provider_override: Optional[str] = None
    is_active: bool = True


class BotVariantUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    system_prompt_base: Optional[str] = None
    skill_ids: Optional[List[int]] = None
    model_override: Optional[str] = None
    provider_override: Optional[str] = None
    is_active: Optional[bool] = None


class BotVariantOut(BaseModel):
    id: int
    name: str
    slug: str
    role: str
    description: Optional[str]
    system_prompt_base: Optional[str]
    skill_ids: Optional[List[int]]
    model_override: Optional[str]
    provider_override: Optional[str]
    is_active: bool
    is_builtin: bool
    created_at: Optional[str]

    class Config:
        from_attributes = True


class PipelineTemplateCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    practice_area: str = "tax"
    step_config: Optional[Any] = {}
    is_active: bool = True
    is_default: bool = False


class PipelineTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    practice_area: Optional[str] = None
    step_config: Optional[Any] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class PipelineTemplateOut(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    practice_area: str
    step_config: Optional[Any]
    is_active: bool
    is_default: bool
    created_at: Optional[str]

    class Config:
        from_attributes = True


def _dt_str(dt) -> Optional[str]:
    return dt.isoformat() if dt else None


def _skill_out(s: Skill) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "version": s.version or "1.0.0",
        "description": s.description,
        "category": s.category or "tax",
        "tags": s.tags or [],
        "applicable_bots": s.applicable_bots or [],
        "content_markdown": s.content_markdown,
        "frontmatter": s.frontmatter or {},
        "is_active": s.is_active,
        "is_builtin": s.is_builtin,
        "created_at": _dt_str(s.created_at),
    }


def _bv_out(b: BotVariant) -> dict:
    return {
        "id": b.id,
        "name": b.name,
        "slug": b.slug,
        "role": b.role,
        "description": b.description,
        "system_prompt_base": b.system_prompt_base,
        "skill_ids": b.skill_ids or [],
        "model_override": b.model_override,
        "provider_override": b.provider_override,
        "is_active": b.is_active,
        "is_builtin": b.is_builtin,
        "created_at": _dt_str(b.created_at),
    }


def _pt_out(p: PipelineTemplate) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "slug": p.slug,
        "description": p.description,
        "practice_area": p.practice_area or "tax",
        "step_config": p.step_config or {},
        "is_active": p.is_active,
        "is_default": p.is_default,
        "created_at": _dt_str(p.created_at),
    }


# ── Skills routes ─────────────────────────────────────────────────────────────

@router.get("/api/admin/skills")
async def list_skills(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    q = select(Skill).order_by(desc(Skill.created_at))
    if category:
        q = q.where(Skill.category == category)
    if is_active is not None:
        q = q.where(Skill.is_active == is_active)
    result = await db.execute(q)
    skills = result.scalars().all()
    return [_skill_out(s) for s in skills]


@router.get("/api/admin/skills/{skill_id}")
async def get_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return _skill_out(skill)


@router.post("/api/admin/skills", status_code=201)
async def create_skill(
    req: SkillCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    # Check uniqueness
    existing = await db.execute(select(Skill).where(Skill.name == req.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Skill with name '{req.name}' already exists")

    skill = Skill(
        name=req.name,
        version=req.version,
        description=req.description,
        category=req.category,
        tags=req.tags or [],
        applicable_bots=req.applicable_bots or [],
        content_markdown=req.content_markdown,
        frontmatter=req.frontmatter or {},
        is_active=req.is_active,
        is_builtin=False,
        created_by=admin.id,
    )
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return _skill_out(skill)


@router.put("/api/admin/skills/{skill_id}")
async def update_skill(
    skill_id: int,
    req: SkillUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    update_data = req.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(skill, key, val)

    await db.commit()
    await db.refresh(skill)
    return _skill_out(skill)


@router.delete("/api/admin/skills/{skill_id}", status_code=204)
async def delete_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    await db.delete(skill)
    await db.commit()


# ── BotVariant routes ─────────────────────────────────────────────────────────

@router.get("/api/admin/bot-variants")
async def list_bot_variants(
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    q = select(BotVariant).order_by(BotVariant.role, BotVariant.name)
    if role:
        q = q.where(BotVariant.role == role)
    if is_active is not None:
        q = q.where(BotVariant.is_active == is_active)
    result = await db.execute(q)
    variants = result.scalars().all()
    return [_bv_out(v) for v in variants]


@router.get("/api/admin/bot-variants/{variant_id}")
async def get_bot_variant(
    variant_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(select(BotVariant).where(BotVariant.id == variant_id))
    variant = result.scalar_one_or_none()
    if not variant:
        raise HTTPException(status_code=404, detail="BotVariant not found")
    return _bv_out(variant)


@router.post("/api/admin/bot-variants", status_code=201)
async def create_bot_variant(
    req: BotVariantCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    existing = await db.execute(select(BotVariant).where(BotVariant.slug == req.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"BotVariant with slug '{req.slug}' already exists")

    variant = BotVariant(
        name=req.name,
        slug=req.slug,
        role=req.role,
        description=req.description,
        system_prompt_base=req.system_prompt_base,
        skill_ids=req.skill_ids or [],
        model_override=req.model_override,
        provider_override=req.provider_override,
        is_active=req.is_active,
        is_builtin=False,
    )
    db.add(variant)
    await db.commit()
    await db.refresh(variant)
    return _bv_out(variant)


@router.put("/api/admin/bot-variants/{variant_id}")
async def update_bot_variant(
    variant_id: int,
    req: BotVariantUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(select(BotVariant).where(BotVariant.id == variant_id))
    variant = result.scalar_one_or_none()
    if not variant:
        raise HTTPException(status_code=404, detail="BotVariant not found")

    update_data = req.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(variant, key, val)

    await db.commit()
    await db.refresh(variant)
    return _bv_out(variant)


@router.delete("/api/admin/bot-variants/{variant_id}", status_code=204)
async def delete_bot_variant(
    variant_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(select(BotVariant).where(BotVariant.id == variant_id))
    variant = result.scalar_one_or_none()
    if not variant:
        raise HTTPException(status_code=404, detail="BotVariant not found")
    if variant.is_builtin:
        raise HTTPException(status_code=400, detail="Cannot delete a builtin BotVariant")
    await db.delete(variant)
    await db.commit()


# ── PipelineTemplate routes ───────────────────────────────────────────────────

@router.get("/api/pipeline-templates")
async def list_pipeline_templates_public(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """List active pipeline templates — for use in matter creation UI."""
    q = select(PipelineTemplate).where(PipelineTemplate.is_active == True).order_by(
        desc(PipelineTemplate.is_default), PipelineTemplate.name
    )
    result = await db.execute(q)
    templates = result.scalars().all()
    return [_pt_out(t) for t in templates]


@router.get("/api/admin/pipeline-templates")
async def list_pipeline_templates(
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    q = select(PipelineTemplate).order_by(desc(PipelineTemplate.is_default), PipelineTemplate.name)
    if is_active is not None:
        q = q.where(PipelineTemplate.is_active == is_active)
    result = await db.execute(q)
    templates = result.scalars().all()
    return [_pt_out(t) for t in templates]


@router.get("/api/admin/pipeline-templates/{template_id}")
async def get_pipeline_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(select(PipelineTemplate).where(PipelineTemplate.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="PipelineTemplate not found")
    return _pt_out(template)


@router.post("/api/admin/pipeline-templates", status_code=201)
async def create_pipeline_template(
    req: PipelineTemplateCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    existing = await db.execute(select(PipelineTemplate).where(PipelineTemplate.slug == req.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"PipelineTemplate with slug '{req.slug}' already exists")

    template = PipelineTemplate(
        name=req.name,
        slug=req.slug,
        description=req.description,
        practice_area=req.practice_area,
        step_config=req.step_config or {},
        is_active=req.is_active,
        is_default=req.is_default,
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return _pt_out(template)


@router.put("/api/admin/pipeline-templates/{template_id}")
async def update_pipeline_template(
    template_id: int,
    req: PipelineTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(select(PipelineTemplate).where(PipelineTemplate.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="PipelineTemplate not found")

    update_data = req.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(template, key, val)

    await db.commit()
    await db.refresh(template)
    return _pt_out(template)


@router.delete("/api/admin/pipeline-templates/{template_id}", status_code=204)
async def delete_pipeline_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(select(PipelineTemplate).where(PipelineTemplate.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="PipelineTemplate not found")
    if template.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete the default PipelineTemplate")
    await db.delete(template)
    await db.commit()
