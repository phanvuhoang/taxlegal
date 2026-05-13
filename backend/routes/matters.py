"""
Matters API — CRUD for client advisory requests.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
from backend.database import get_db
from backend.models import Matter, PipelineStep, ResearchChunk, User
from backend.auth import get_current_user
from backend.agents.pipeline import execute_pipeline_step

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/matters", tags=["matters"])


class CreateMatterRequest(BaseModel):
    title: str
    client_request: str
    practice_area: str = "tax"
    pipeline_mode: str = "manual"  # manual | auto
    output_language: str = "vi"  # vi | en
    model_override: Optional[str] = None
    pipeline_template_id: Optional[int] = None


class MatterSummary(BaseModel):
    id: int
    title: str
    practice_area: str
    pipeline_mode: str
    status: str
    current_step: int
    quality_score: Optional[float]
    word_count_floor: Optional[int]
    created_at: str
    is_sample: bool

    class Config:
        from_attributes = True


@router.get("/")
async def list_matters(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Matter).order_by(desc(Matter.created_at))
    if current_user.role != "admin":
        query = query.where(Matter.user_id == current_user.id)
    if status:
        query = query.where(Matter.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    matters = result.scalars().all()
    return [
        {
            "id": m.id,
            "title": m.title,
            "practice_area": m.practice_area,
            "pipeline_mode": m.pipeline_mode,
            "status": m.status,
            "current_step": m.current_step,
            "quality_score": m.quality_score,
            "word_count_floor": m.word_count_floor,
            "is_sample": m.is_sample,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "reason_codes": m.reason_codes or [],
        }
        for m in matters
    ]


@router.post("/")
async def create_matter(
    req: CreateMatterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    matter = Matter(
        user_id=current_user.id,
        title=req.title,
        client_request=req.client_request,
        practice_area=req.practice_area,
        pipeline_mode=req.pipeline_mode,
        output_language=req.output_language,
        status="draft",
        current_step=0,
        pipeline_template_id=req.pipeline_template_id,
    )
    db.add(matter)
    await db.commit()
    await db.refresh(matter)

    # Run step 1 (Intake) inline within the request context.
    # Background tasks broke SQLAlchemy's greenlet bridge during multi-loop
    # retrievals (step 4), so all step execution now runs inline.
    step_status = "pending"
    try:
        step = await _run_pipeline_step_inline(db, matter.id, 1, req.model_override)
        step_status = step.status
    except Exception as e:
        logger.error(f"Intake step failed for matter {matter.id}: {e}")
        step_status = "failed"

    return {
        "id": matter.id,
        "status": "intake_started",
        "step_status": step_status,
        "message": f"Matter created. Step 1 finished with status: {step_status}",
    }


@router.get("/{matter_id}")
async def get_matter(
    matter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    matter = await _get_matter_or_404(db, matter_id, current_user)
    steps_result = await db.execute(
        select(PipelineStep)
        .where(PipelineStep.matter_id == matter_id)
        .order_by(PipelineStep.step_number)
    )
    steps = steps_result.scalars().all()

    return {
        "id": matter.id,
        "title": matter.title,
        "client_request": matter.client_request,
        "practice_area": matter.practice_area,
        "pipeline_mode": matter.pipeline_mode,
        "output_language": getattr(matter, "output_language", "vi"),
        "status": matter.status,
        "current_step": matter.current_step,
        "verified_facts": matter.verified_facts or [],
        "applicable_laws": matter.applicable_laws or [],
        "completeness_matrix": matter.completeness_matrix or [],
        "word_count_floor": matter.word_count_floor,
        "partner_brief": matter.partner_brief,
        "sa_blueprint": matter.sa_blueprint,
        "final_content": matter.final_content,
        "quality_score": matter.quality_score,
        "reason_codes": matter.reason_codes or [],
        "verification_chain_status": matter.verification_chain_status,
        "total_tokens": matter.total_tokens,
        "is_sample": matter.is_sample,
        "created_at": matter.created_at.isoformat() if matter.created_at else None,
        "steps": [
            {
                "id": s.id,
                "step_number": s.step_number,
                "step_name": s.step_name,
                "agent": s.agent,
                "status": s.status,
                "model_used": s.model_used,
                "output_markdown": s.output_markdown,
                "output_data": s.output_data,
                "word_count": s.word_count,
                "reason_codes_found": s.reason_codes_found or [],
                "prompt_tokens": s.prompt_tokens,
                "completion_tokens": s.completion_tokens,
                "duration_ms": s.duration_ms,
                "user_notes": s.user_notes,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                "approved_at": s.approved_at.isoformat() if s.approved_at else None,
                "error_message": s.error_message,
            }
            for s in steps
        ],
    }


@router.post("/{matter_id}/approve-step/{step_number}")
async def approve_step(
    matter_id: int,
    step_number: int,
    body: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a completed step and run the next one inline."""
    await _get_matter_or_404(db, matter_id, current_user)
    notes = body.get("notes", "")
    model_override = body.get("model_override")

    # Mark step approved
    step_result = await db.execute(
        select(PipelineStep).where(
            PipelineStep.matter_id == matter_id,
            PipelineStep.step_number == step_number,
        )
    )
    step = step_result.scalar_one_or_none()
    if not step:
        raise HTTPException(404, f"Step {step_number} not found")
    if step.status not in ("waiting", "completed"):
        raise HTTPException(400, f"Step is {step.status}, cannot approve")

    from datetime import datetime
    step.status = "approved"
    step.user_notes = notes
    step.approved_at = datetime.utcnow()
    step.approved_by = current_user.id
    await db.commit()

    next_step = step_number + 1
    if next_step > 7:
        return {"message": "Pipeline completed!"}

    next_status = "pending"
    try:
        next_step_obj = await _run_pipeline_step_inline(db, matter_id, next_step, model_override)
        next_status = next_step_obj.status
    except Exception as e:
        logger.error(f"Step {next_step} failed for matter {matter_id}: {e}")
        next_status = "failed"

    return {
        "message": f"Step {step_number} approved. Step {next_step} finished with status: {next_status}",
        "next_step": next_step,
        "next_status": next_status,
    }


@router.post("/{matter_id}/run-step/{step_number}")
async def run_step_manual(
    matter_id: int,
    step_number: int,
    body: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run a specific step synchronously within the request context (admin/retry)."""
    await _get_matter_or_404(db, matter_id, current_user)
    model_override = body.get("model_override")
    try:
        step = await _run_pipeline_step_inline(db, matter_id, step_number, model_override)
    except Exception as e:
        logger.error(f"Manual run of step {step_number} failed for matter {matter_id}: {e}")
        return {"message": f"Step {step_number} failed", "status": "failed"}
    return {"message": f"Step {step_number} completed", "status": step.status}


@router.get("/{matter_id}/chunks")
async def get_chunks(
    matter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_matter_or_404(db, matter_id, current_user)
    result = await db.execute(
        select(ResearchChunk)
        .where(ResearchChunk.matter_id == matter_id)
        .order_by(ResearchChunk.chunk_number)
    )
    chunks = result.scalars().all()
    return [
        {
            "id": c.id,
            "chunk_number": c.chunk_number,
            "section_title": c.section_title,
            "depth_level": c.depth_level,
            "content_markdown": c.content_markdown,
            "depth_markers": c.depth_markers or [],
            "depth_marker_count": c.depth_marker_count,
            "citations": c.citations or [],
            "word_count": c.word_count,
        }
        for c in chunks
    ]


@router.patch("/{matter_id}/mark-sample")
async def mark_as_sample(
    matter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")
    matter = await _get_matter_or_404(db, matter_id, current_user)
    matter.is_sample = not matter.is_sample
    await db.commit()
    return {"is_sample": matter.is_sample}


@router.delete("/{matter_id}")
async def delete_matter(
    matter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    matter = await _get_matter_or_404(db, matter_id, current_user)
    if current_user.role != "admin" and matter.user_id != current_user.id:
        raise HTTPException(403, "Access denied")
    await db.delete(matter)
    await db.commit()
    return {"message": "Deleted"}


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_matter_or_404(db: AsyncSession, matter_id: int, user: User) -> Matter:
    result = await db.execute(select(Matter).where(Matter.id == matter_id))
    matter = result.scalar_one_or_none()
    if not matter:
        raise HTTPException(404, "Matter not found")
    if user.role != "admin" and matter.user_id != user.id:
        raise HTTPException(403, "Access denied")
    return matter


async def _run_pipeline_step_inline(
    db: AsyncSession,
    matter_id: int,
    step_number: int,
    model_override: Optional[str] = None,
) -> PipelineStep:
    """
    Execute a pipeline step inline using the caller's DB session.

    Replaces the previous BackgroundTasks-based runner that created its own
    AsyncSessionLocal. FastAPI background tasks broke SQLAlchemy's greenlet
    bridge during long retrieval loops (step 4 / JA Research), surfacing as
    `MissingGreenlet: greenlet_spawn has not been called`. Running inside the
    request handler's session keeps the greenlet alive for the entire step.
    """
    step = await execute_pipeline_step(db, matter_id, step_number, model_override)

    # Auto mode: if the step is waiting for approval (not final), auto-approve
    # and continue to the next step within the same session.
    matter_result = await db.execute(select(Matter).where(Matter.id == matter_id))
    matter = matter_result.scalar_one_or_none()
    if matter and matter.pipeline_mode == "auto" and step_number < 7 and step.status == "waiting":
        await _auto_approve_and_continue(db, matter_id, step_number, model_override)

    return step


async def _auto_approve_and_continue(db, matter_id, step_number, model_override):
    """Auto approve current step and run the next one inline."""
    from datetime import datetime
    step_result = await db.execute(
        select(PipelineStep).where(
            PipelineStep.matter_id == matter_id,
            PipelineStep.step_number == step_number,
        )
    )
    step = step_result.scalar_one_or_none()
    if step:
        step.status = "approved"
        step.approved_at = datetime.utcnow()
        await db.commit()
    next_step = step_number + 1
    if next_step <= 7:
        await execute_pipeline_step(db, matter_id, next_step, model_override)
