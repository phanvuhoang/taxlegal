"""Admin routes: users, agent settings, sample advices, autotest."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, EmailStr
from typing import Optional
from backend.database import get_db
from backend.models import User, AgentSetting, SampleAdvice, AutoTestCase, AutoTestRun, Matter
from backend.auth import get_current_admin, get_current_user, hash_password
from backend.config import get_available_models

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    user_count = (await db.execute(select(func.count(User.id)))).scalar()
    matter_count = (await db.execute(select(func.count(Matter.id)))).scalar()
    completed = (await db.execute(
        select(func.count(Matter.id)).where(Matter.status == "completed")
    )).scalar()
    avg_score = (await db.execute(
        select(func.avg(Matter.quality_score)).where(Matter.quality_score.isnot(None))
    )).scalar()
    sample_count = (await db.execute(
        select(func.count(Matter.id)).where(Matter.is_sample == True)
    )).scalar()
    return {
        "users": user_count,
        "matters": matter_count,
        "completed": completed,
        "avg_quality_score": round(avg_score, 1) if avg_score else None,
        "sample_advices": sample_count,
    }


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/users")
async def list_users(admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [
        {
            "id": u.id, "email": u.email, "full_name": u.full_name,
            "role": u.role, "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""
    role: str = "user"


@router.post("/users")
async def create_user(req: CreateUserRequest, admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email đã tồn tại")
    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "email": user.email, "role": user.role}


@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    data: dict,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    if "is_active" in data:
        user.is_active = data["is_active"]
    if "role" in data:
        user.role = data["role"]
    if "full_name" in data:
        user.full_name = data["full_name"]
    if "password" in data and data["password"]:
        user.password_hash = hash_password(data["password"])
    await db.commit()
    return {"id": user.id, "email": user.email, "role": user.role, "is_active": user.is_active}


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Not found")
    if user.role == "admin":
        raise HTTPException(400, "Cannot delete admin")
    await db.delete(user)
    await db.commit()
    return {"message": "Deleted"}


# ── Agent Settings ─────────────────────────────────────────────────────────────

@router.get("/agent-settings")
async def get_agent_settings(admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentSetting).order_by(AgentSetting.agent_key))
    settings = result.scalars().all()
    return {
        "settings": [
            {
                "id": s.id, "agent_key": s.agent_key, "model_id": s.model_id,
                "provider": s.provider, "temperature": s.temperature,
                "max_tokens": s.max_tokens, "system_prompt_override": s.system_prompt_override,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in settings
        ],
        "available_models": get_available_models(),
    }


@router.put("/agent-settings/{agent_key}")
async def update_agent_setting(
    agent_key: str,
    data: dict,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AgentSetting).where(AgentSetting.agent_key == agent_key))
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(404, "Agent setting not found")
    for field in ("model_id", "provider", "temperature", "max_tokens", "system_prompt_override"):
        if field in data:
            setattr(setting, field, data[field])
    setting.updated_by = admin.id
    await db.commit()
    return {"message": f"Agent {agent_key} updated"}


# ── Sample Advices ────────────────────────────────────────────────────────────

@router.get("/sample-advices")
async def list_sample_advices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SampleAdvice).where(SampleAdvice.is_active == True).order_by(SampleAdvice.created_at.desc())
    )
    advices = result.scalars().all()
    return [
        {
            "id": a.id, "title": a.title, "practice_area": a.practice_area,
            "tags": a.tags or [], "client_question": a.client_question,
            "quality_score": a.quality_score,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in advices
    ]


@router.get("/sample-advices/{advice_id}")
async def get_sample_advice(
    advice_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SampleAdvice).where(SampleAdvice.id == advice_id))
    advice = result.scalar_one_or_none()
    if not advice:
        raise HTTPException(404, "Not found")
    return {
        "id": advice.id, "title": advice.title, "practice_area": advice.practice_area,
        "tags": advice.tags or [], "client_question": advice.client_question,
        "content_markdown": advice.content_markdown, "quality_score": advice.quality_score,
    }


class CreateSampleAdviceRequest(BaseModel):
    title: str
    practice_area: str = "tax"
    tags: list[str] = []
    client_question: str = ""
    content_markdown: str
    quality_score: Optional[float] = None


@router.post("/sample-advices")
async def create_sample_advice(
    req: CreateSampleAdviceRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    advice = SampleAdvice(
        title=req.title,
        practice_area=req.practice_area,
        tags=req.tags,
        client_question=req.client_question,
        content_markdown=req.content_markdown,
        quality_score=req.quality_score,
        created_by=admin.id,
    )
    db.add(advice)
    await db.commit()
    await db.refresh(advice)
    return {"id": advice.id, "title": advice.title}


@router.delete("/sample-advices/{advice_id}")
async def delete_sample_advice(
    advice_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SampleAdvice).where(SampleAdvice.id == advice_id))
    advice = result.scalar_one_or_none()
    if not advice:
        raise HTTPException(404, "Not found")
    await db.delete(advice)
    await db.commit()
    return {"message": "Deleted"}


# ── AutoTest ──────────────────────────────────────────────────────────────────

@router.get("/autotest/cases")
async def list_test_cases(admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AutoTestCase).where(AutoTestCase.is_active == True).order_by(AutoTestCase.id)
    )
    cases = result.scalars().all()
    return [
        {
            "id": c.id, "name": c.name, "description": c.description,
            "practice_area": c.practice_area, "complexity": c.complexity,
            "baseline_score": c.baseline_score,
            "baseline_locked_at": c.baseline_locked_at.isoformat() if c.baseline_locked_at else None,
        }
        for c in cases
    ]


@router.post("/autotest/cases")
async def create_test_case(
    data: dict,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    tc = AutoTestCase(
        name=data["name"],
        description=data.get("description", ""),
        client_request=data["client_request"],
        practice_area=data.get("practice_area", "tax"),
        complexity=data.get("complexity", "standard"),
        expected_topics=data.get("expected_topics", []),
        forbidden_topics=data.get("forbidden_topics", []),
        scoring_criteria=data.get("scoring_criteria", {}),
    )
    db.add(tc)
    await db.commit()
    await db.refresh(tc)
    return {"id": tc.id, "name": tc.name}


@router.post("/autotest/run/{case_id}")
async def run_autotest(
    case_id: int,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Run an autotest case against current pipeline (simplified scoring)."""
    result = await db.execute(select(AutoTestCase).where(AutoTestCase.id == case_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(404, "Test case not found")

    # Create a test matter and run it
    matter = Matter(
        user_id=admin.id,
        title=f"[AUTOTEST] {tc.name}",
        client_request=tc.client_request,
        practice_area=tc.practice_area,
        pipeline_mode="auto",
        status="draft",
    )
    db.add(matter)
    await db.commit()
    await db.refresh(matter)

    return {
        "message": f"AutoTest '{tc.name}' started. Matter ID: {matter.id}",
        "matter_id": matter.id,
        "test_case_id": case_id,
    }


@router.get("/autotest/runs")
async def list_test_runs(admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AutoTestRun).order_by(AutoTestRun.created_at.desc()).limit(50)
    )
    runs = result.scalars().all()
    return [
        {
            "id": r.id, "test_case_id": r.test_case_id, "matter_id": r.matter_id,
            "score_total": r.score_total, "delta_from_baseline": r.delta_from_baseline,
            "passed": r.passed, "reason_codes_triggered": r.reason_codes_triggered or [],
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in runs
    ]
