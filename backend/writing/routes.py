"""
Writing module API routes.
/api/writing/* — authenticated users
/api/admin/writing/* — admin only
/api/admin/priority-docs/* — admin only  
/api/admin/sample-writings/* — admin only
"""
import json
import logging
import os
from pathlib import Path
from typing import Optional, List, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, text

from backend.database import get_db
from backend.models import User
from backend.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["writing"])

DOCX_OUTPUT_DIR = Path("/tmp/taxlegal_writing_docs")
DOCX_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Dependency: require admin ──────────────────────────────────────────────────

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ── Pydantic schemas ───────────────────────────────────────────────────────────

class WritingJobCreate(BaseModel):
    title: str
    content_type: str = "analysis"
    topic: str
    context: Optional[str] = None
    output_language: str = "vi"
    bot_variant_id: Optional[int] = None
    skill_ids: Optional[List[int]] = []
    word_count_target: int = 2000
    review_bot_variant_id: Optional[int] = None


class WritingJobOut(BaseModel):
    id: int
    title: str
    content_type: str
    topic: str
    context: Optional[str]
    output_language: str
    bot_variant_id: Optional[int]
    skill_ids: Optional[List[int]]
    status: str
    word_count_target: int
    final_content: Optional[str]
    docx_path: Optional[str]
    gamma_url: Optional[str]
    created_at: Optional[str]


class PriorityDocCreate(BaseModel):
    title: str
    doc_type: str = "law"
    source_url: Optional[str] = None
    content: str
    priority_level: int = 1
    is_active: bool = True


class PriorityDocOut(BaseModel):
    id: int
    title: str
    doc_type: str
    source_url: Optional[str]
    content: str
    priority_level: int
    is_active: bool
    created_at: Optional[str]


class SampleWritingCreate(BaseModel):
    title: str
    content_type: str = "analysis"
    language: str = "vi"
    content: str
    tags: Optional[List[str]] = []
    is_active: bool = True


class SampleWritingOut(BaseModel):
    id: int
    title: str
    content_type: str
    language: str
    content: str
    tags: Optional[List[str]]
    is_active: bool
    created_at: Optional[str]


# ── Writing Jobs ───────────────────────────────────────────────────────────────

@router.get("/api/writing")
async def list_writing_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        text("""
            SELECT id, title, content_type, topic, output_language, status, 
                   word_count_target, docx_path, gamma_url, created_at
            FROM taxlegal.writing_jobs
            WHERE created_by = :user_id
            ORDER BY created_at DESC
            LIMIT 50
        """),
        {"user_id": current_user.id}
    )
    rows = result.fetchall()
    return [
        {
            "id": r.id, "title": r.title, "content_type": r.content_type,
            "topic": r.topic, "output_language": r.output_language,
            "status": r.status, "word_count_target": r.word_count_target,
            "docx_path": r.docx_path, "gamma_url": r.gamma_url,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.post("/api/writing", status_code=201)
async def create_writing_job(
    req: WritingJobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        text("""
            INSERT INTO taxlegal.writing_jobs
                (title, content_type, topic, context, output_language, bot_variant_id,
                 skill_ids, status, word_count_target, review_bot_variant_id, created_by)
            VALUES
                (:title, :content_type, :topic, :context, :output_language, :bot_variant_id,
                 :skill_ids, 'draft', :word_count_target, :review_bot_variant_id, :created_by)
            RETURNING id, title, content_type, topic, context, output_language,
                      bot_variant_id, skill_ids, status, word_count_target, created_at
        """),
        {
            "title": req.title,
            "content_type": req.content_type,
            "topic": req.topic,
            "context": req.context,
            "output_language": req.output_language,
            "bot_variant_id": req.bot_variant_id,
            "skill_ids": req.skill_ids or [],
            "word_count_target": req.word_count_target,
            "review_bot_variant_id": req.review_bot_variant_id,
            "created_by": current_user.id,
        }
    )
    row = result.fetchone()
    await db.commit()
    return {
        "id": row.id, "title": row.title, "content_type": row.content_type,
        "topic": row.topic, "context": row.context, "output_language": row.output_language,
        "bot_variant_id": row.bot_variant_id, "skill_ids": row.skill_ids,
        "status": row.status, "word_count_target": row.word_count_target,
        "final_content": None, "docx_path": None, "gamma_url": None,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/api/writing/{job_id}")
async def get_writing_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        text("""
            SELECT id, title, content_type, topic, context, output_language,
                   bot_variant_id, skill_ids, status, word_count_target,
                   final_content, docx_path, gamma_url,
                   review_bot_variant_id, review_content, review_status,
                   created_at
            FROM taxlegal.writing_jobs
            WHERE id = :job_id AND created_by = :user_id
        """),
        {"job_id": job_id, "user_id": current_user.id}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Writing job not found")
    return {
        "id": row.id, "title": row.title, "content_type": row.content_type,
        "topic": row.topic, "context": row.context, "output_language": row.output_language,
        "bot_variant_id": row.bot_variant_id, "skill_ids": row.skill_ids,
        "status": row.status, "word_count_target": row.word_count_target,
        "final_content": row.final_content, "docx_path": row.docx_path,
        "gamma_url": row.gamma_url,
        "review_bot_variant_id": row.review_bot_variant_id,
        "review_content": row.review_content,
        "review_status": row.review_status,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.post("/api/writing/{job_id}/generate")
async def generate_writing(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate content for a writing job (non-streaming)."""
    # Get job
    result = await db.execute(
        text("SELECT * FROM taxlegal.writing_jobs WHERE id = :id AND created_by = :uid"),
        {"id": job_id, "uid": current_user.id}
    )
    job = result.fetchone()
    if not job:
        raise HTTPException(status_code=404, detail="Writing job not found")

    # Mark as generating
    await db.execute(
        text("UPDATE taxlegal.writing_jobs SET status = 'generating', updated_at = NOW() WHERE id = :id"),
        {"id": job_id}
    )
    await db.commit()

    try:
        from backend.writing.content_generator import generate_writing_content

        content = await generate_writing_content(
            topic=job.topic,
            context=job.context or "",
            content_type=job.content_type,
            output_language=job.output_language,
            db=db,
            skill_ids=job.skill_ids or [],
            word_count_target=job.word_count_target,
        )

        # Save content
        await db.execute(
            text("""
                UPDATE taxlegal.writing_jobs 
                SET final_content = :content, status = 'done', updated_at = NOW()
                WHERE id = :id
            """),
            {"content": content, "id": job_id}
        )
        await db.commit()

        # Trigger review if review bot is configured
        if job.review_bot_variant_id:
            try:
                await db.execute(
                    text("UPDATE taxlegal.writing_jobs SET review_status='reviewing' WHERE id=:id"),
                    {"id": job_id}
                )
                await db.commit()

                # Get review bot's system prompt / skills
                rev_bot_result = await db.execute(
                    text("SELECT name, system_prompt_base FROM taxlegal.bot_variants WHERE id=:id"),
                    {"id": job.review_bot_variant_id}
                )
                rev_bot = rev_bot_result.fetchone()

                lang = job.output_language or "vi"
                if lang == "vi":
                    review_prompt = f"""Bạn là reviewer chuyên nghiệp. Hãy review bài viết sau và đưa ra nhận xét chi tiết:

## BÀI VIẾT CẦN REVIEW
{content[:12000]}

## YÊU CẦU REVIEW
1. Đánh giá tổng thể: độ chính xác pháp lý, tính đầy đủ, cấu trúc
2. Kiểm tra citations: mỗi nhận định có trích dẫn luật không?
3. Rủi ro và điểm cần bổ sung
4. Điểm mạnh của bài viết
5. Kết luận: Chấp nhận / Cần chỉnh sửa / Từ chối

Viết bằng TIẾNG VIỆT."""
                else:
                    review_prompt = f"""You are a professional reviewer. Review the following article:

## ARTICLE TO REVIEW
{content[:12000]}

## REVIEW CRITERIA
1. Overall assessment: legal accuracy, completeness, structure
2. Citation check: does every finding cite specific legal provisions?
3. Risks and gaps
4. Strengths
5. Conclusion: Accept / Needs revision / Reject

Write in ENGLISH."""

                review_sys = (rev_bot.system_prompt_base if rev_bot and rev_bot.system_prompt_base
                             else "You are an expert tax law reviewer with 30 years experience." if lang == "en"
                             else "Bạn là chuyên gia review văn bản thuế với 30 năm kinh nghiệm.")

                from backend.ai_provider import call_ai
                from backend.config import DEEPSEEK_MODEL

                review_result = await call_ai(
                    model_id=DEEPSEEK_MODEL or "deepseek-chat",
                    messages=[{"role": "user", "content": review_prompt}],
                    system_prompt=review_sys,
                    max_tokens=4000,
                    temperature=0.3,
                )
                review_text = review_result.get("content", "") if isinstance(review_result, dict) else str(review_result)

                await db.execute(
                    text("""
                        UPDATE taxlegal.writing_jobs
                        SET review_content=:rc, review_status='done'
                        WHERE id=:id
                    """),
                    {"rc": review_text, "id": job_id}
                )
                await db.commit()
            except Exception as review_err:
                logger.warning(f"Review failed (non-fatal): {review_err}")
                await db.execute(
                    text("UPDATE taxlegal.writing_jobs SET review_status='error' WHERE id=:id"),
                    {"id": job_id}
                )
                await db.commit()

        return {"status": "done", "content": content, "job_id": job_id}

    except Exception as e:
        await db.execute(
            text("UPDATE taxlegal.writing_jobs SET status = 'error', updated_at = NOW() WHERE id = :id"),
            {"id": job_id}
        )
        await db.commit()
        logger.error(f"Writing generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/writing/{job_id}/stream")
async def stream_writing(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """SSE streaming content generation."""
    result = await db.execute(
        text("SELECT * FROM taxlegal.writing_jobs WHERE id = :id AND created_by = :uid"),
        {"id": job_id, "uid": current_user.id}
    )
    job = result.fetchone()
    if not job:
        raise HTTPException(status_code=404, detail="Writing job not found")

    from backend.writing.content_generator import generate_writing_content_stream

    async def event_generator():
        full_content = []
        async for chunk in generate_writing_content_stream(
            topic=job.topic,
            context=job.context or "",
            content_type=job.content_type,
            output_language=job.output_language,
            db=db,
            skill_ids=job.skill_ids or [],
            word_count_target=job.word_count_target,
        ):
            full_content.append(chunk)
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

        # Save final content
        content = "".join(full_content)
        await db.execute(
            text("UPDATE taxlegal.writing_jobs SET final_content = :c, status = 'done' WHERE id = :id"),
            {"c": content, "id": job_id}
        )
        await db.commit()
        yield f"data: {json.dumps({'done': True, 'job_id': job_id})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/api/writing/{job_id}/export-docx")
async def export_docx(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export writing job as DOCX."""
    result = await db.execute(
        text("SELECT id, title, final_content, output_language FROM taxlegal.writing_jobs WHERE id = :id AND created_by = :uid"),
        {"id": job_id, "uid": current_user.id}
    )
    job = result.fetchone()
    if not job:
        raise HTTPException(status_code=404, detail="Writing job not found")
    if not job.final_content:
        raise HTTPException(status_code=400, detail="Content not generated yet")

    from backend.writing.docx_exporter import markdown_to_docx

    output_path = str(DOCX_OUTPUT_DIR / f"writing_{job_id}_{job.output_language}.docx")
    try:
        markdown_to_docx(job.final_content, job.title, output_path)

        # Update docx_path in DB
        await db.execute(
            text("UPDATE taxlegal.writing_jobs SET docx_path = :path WHERE id = :id"),
            {"path": output_path, "id": job_id}
        )
        await db.commit()

        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"{job.title[:50]}.docx"
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="python-docx not installed")


@router.post("/api/writing/{job_id}/create-slides")
async def create_gamma_slides_endpoint(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create Gamma slides from writing content."""
    result = await db.execute(
        text("SELECT id, title, final_content, output_language FROM taxlegal.writing_jobs WHERE id = :id AND created_by = :uid"),
        {"id": job_id, "uid": current_user.id}
    )
    job = result.fetchone()
    if not job:
        raise HTTPException(status_code=404, detail="Writing job not found")
    if not job.final_content:
        raise HTTPException(status_code=400, detail="Content not generated yet")

    from backend.writing.gamma_client import create_gamma_slides

    url = await create_gamma_slides(job.title, job.final_content, job.output_language)

    if url:
        await db.execute(
            text("UPDATE taxlegal.writing_jobs SET gamma_url = :url WHERE id = :id"),
            {"url": url, "id": job_id}
        )
        await db.commit()
        return {"gamma_url": url}
    else:
        raise HTTPException(status_code=503, detail="Gamma API not available — check GAMMA_API_KEY")


@router.delete("/api/writing/{job_id}", status_code=204)
async def delete_writing_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.execute(
        text("DELETE FROM taxlegal.writing_jobs WHERE id = :id AND created_by = :uid"),
        {"id": job_id, "uid": current_user.id}
    )
    await db.commit()


# ── Admin: Priority Docs ───────────────────────────────────────────────────────

@router.get("/api/admin/priority-docs")
async def list_priority_docs(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(
        text("SELECT id, title, doc_type, source_url, content, priority_level, is_active, created_at FROM taxlegal.priority_docs ORDER BY priority_level ASC, created_at DESC")
    )
    rows = result.fetchall()
    return [
        {
            "id": r.id, "title": r.title, "doc_type": r.doc_type,
            "source_url": r.source_url, "content": r.content,
            "priority_level": r.priority_level, "is_active": r.is_active,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.post("/api/admin/priority-docs", status_code=201)
async def create_priority_doc(
    req: PriorityDocCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(
        text("""
            INSERT INTO taxlegal.priority_docs
                (title, doc_type, source_url, content, priority_level, is_active, created_by)
            VALUES (:title, :doc_type, :source_url, :content, :priority_level, :is_active, :created_by)
            RETURNING id, title, doc_type, source_url, content, priority_level, is_active, created_at
        """),
        {
            "title": req.title, "doc_type": req.doc_type, "source_url": req.source_url,
            "content": req.content, "priority_level": req.priority_level,
            "is_active": req.is_active, "created_by": admin.id,
        }
    )
    row = result.fetchone()
    await db.commit()
    return {
        "id": row.id, "title": row.title, "doc_type": row.doc_type,
        "source_url": row.source_url, "content": row.content,
        "priority_level": row.priority_level, "is_active": row.is_active,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.put("/api/admin/priority-docs/{doc_id}")
async def update_priority_doc(
    doc_id: int,
    req: PriorityDocCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    await db.execute(
        text("""
            UPDATE taxlegal.priority_docs
            SET title=:title, doc_type=:doc_type, source_url=:source_url,
                content=:content, priority_level=:priority_level, is_active=:is_active,
                updated_at=NOW()
            WHERE id=:id
        """),
        {"title": req.title, "doc_type": req.doc_type, "source_url": req.source_url,
         "content": req.content, "priority_level": req.priority_level,
         "is_active": req.is_active, "id": doc_id}
    )
    await db.commit()
    return {"id": doc_id, "status": "updated"}


@router.delete("/api/admin/priority-docs/{doc_id}", status_code=204)
async def delete_priority_doc(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    await db.execute(text("DELETE FROM taxlegal.priority_docs WHERE id = :id"), {"id": doc_id})
    await db.commit()


# ── Public: Sample Writings (for users) ────────────────────────────────────────

@router.get("/api/sample-writings")
async def list_sample_writings_public(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Public list of sample writings for all authenticated users."""
    result = await db.execute(
        text("""
            SELECT id, title, content_type, language, content, tags, is_active,
                   category, topic, created_at
            FROM taxlegal.sample_writings
            WHERE is_active = TRUE
            ORDER BY created_at DESC
        """)
    )
    rows = result.fetchall()
    return [
        {
            "id": r.id, "title": r.title, "content_type": r.content_type,
            "language": r.language, "content": r.content, "tags": r.tags,
            "category": r.category, "topic": r.topic,
            "is_active": r.is_active,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


# ── Admin: Sample Writings ────────────────────────────────────────────────────

@router.get("/api/admin/sample-writings")
async def list_sample_writings(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(
        text("SELECT id, title, content_type, language, content, tags, is_active, created_at FROM taxlegal.sample_writings ORDER BY created_at DESC")
    )
    rows = result.fetchall()
    return [
        {
            "id": r.id, "title": r.title, "content_type": r.content_type,
            "language": r.language, "content": r.content, "tags": r.tags,
            "is_active": r.is_active,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.post("/api/admin/sample-writings", status_code=201)
async def create_sample_writing(
    req: SampleWritingCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = await db.execute(
        text("""
            INSERT INTO taxlegal.sample_writings
                (title, content_type, language, content, tags, is_active, created_by)
            VALUES (:title, :content_type, :language, :content, :tags, :is_active, :created_by)
            RETURNING id, title, content_type, language, content, tags, is_active, created_at
        """),
        {
            "title": req.title, "content_type": req.content_type, "language": req.language,
            "content": req.content, "tags": req.tags or [], "is_active": req.is_active,
            "created_by": admin.id,
        }
    )
    row = result.fetchone()
    await db.commit()
    return {
        "id": row.id, "title": row.title, "content_type": row.content_type,
        "language": row.language, "content": row.content, "tags": row.tags,
        "is_active": row.is_active,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.delete("/api/admin/sample-writings/{writing_id}", status_code=204)
async def delete_sample_writing(
    writing_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    await db.execute(text("DELETE FROM taxlegal.sample_writings WHERE id = :id"), {"id": writing_id})
    await db.commit()
