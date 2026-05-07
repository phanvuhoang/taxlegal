"""
Regulations routes — attach law docs to matters/writing jobs.
Doc Analysis routes — Phân tích văn bản.
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.database import get_db
from backend.models import User
from backend.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["regulations", "doc-analysis"])


# ── Matter Regulations ────────────────────────────────────────────────────────

@router.get("/api/matters/{matter_id}/regulations")
async def get_matter_regulations(
    matter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        text("""
            SELECT mr.id, mr.law_doc_id, mr.uploaded_filename, mr.uploaded_content,
                   ld.title as law_title, ld.doc_number, ld.doc_type
            FROM taxlegal.matter_regulations mr
            LEFT JOIN taxlegal.law_documents_v2 ld ON ld.id = mr.law_doc_id
            WHERE mr.matter_id = :mid
        """),
        {"mid": matter_id}
    )
    rows = result.fetchall()
    return [
        {
            "id": r.id, "law_doc_id": r.law_doc_id,
            "uploaded_filename": r.uploaded_filename,
            "has_upload": bool(r.uploaded_content),
            "law_title": r.law_title, "doc_number": r.doc_number, "doc_type": r.doc_type,
        }
        for r in rows
    ]


@router.post("/api/matters/{matter_id}/regulations")
async def add_matter_regulation(
    matter_id: int,
    law_doc_id: Optional[int] = None,
    uploaded_content: Optional[str] = None,
    uploaded_filename: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.execute(
        text("""
            INSERT INTO taxlegal.matter_regulations
                (matter_id, law_doc_id, uploaded_content, uploaded_filename)
            VALUES (:mid, :ldid, :uc, :uf)
        """),
        {"mid": matter_id, "ldid": law_doc_id, "uc": uploaded_content, "uf": uploaded_filename}
    )
    await db.commit()
    return {"status": "added"}


@router.post("/api/matters/{matter_id}/regulations/upload")
async def upload_matter_regulation(
    matter_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content_bytes = await file.read()
    filename = file.filename or "regulation.txt"
    ext = filename.rsplit(".", 1)[-1].lower()

    content_text = ""
    try:
        if ext == "txt":
            content_text = content_bytes.decode("utf-8", errors="ignore")
        elif ext == "pdf":
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(content_bytes))
            parts = [page.extract_text() for page in reader.pages if page.extract_text()]
            content_text = "\n".join(parts)
        elif ext in ("docx", "doc"):
            import io, docx as docxlib
            doc = docxlib.Document(io.BytesIO(content_bytes))
            content_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        else:
            content_text = content_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        content_text = content_bytes.decode("utf-8", errors="ignore")

    await db.execute(
        text("""
            INSERT INTO taxlegal.matter_regulations
                (matter_id, uploaded_content, uploaded_filename)
            VALUES (:mid, :uc, :uf)
        """),
        {"mid": matter_id, "uc": content_text, "uf": filename}
    )
    await db.commit()
    return {"status": "uploaded", "filename": filename, "length": len(content_text)}


@router.delete("/api/matters/{matter_id}/regulations/{reg_id}", status_code=204)
async def remove_matter_regulation(
    matter_id: int, reg_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.execute(
        text("DELETE FROM taxlegal.matter_regulations WHERE id=:id AND matter_id=:mid"),
        {"id": reg_id, "mid": matter_id}
    )
    await db.commit()


# ── Writing Regulations ───────────────────────────────────────────────────────

@router.get("/api/writing/{job_id}/regulations")
async def get_writing_regulations(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        text("""
            SELECT wr.id, wr.law_doc_id, wr.uploaded_filename,
                   ld.title as law_title, ld.doc_number, ld.doc_type
            FROM taxlegal.writing_regulations wr
            LEFT JOIN taxlegal.law_documents_v2 ld ON ld.id = wr.law_doc_id
            WHERE wr.job_id = :jid
        """),
        {"jid": job_id}
    )
    rows = result.fetchall()
    return [
        {
            "id": r.id, "law_doc_id": r.law_doc_id,
            "uploaded_filename": r.uploaded_filename,
            "law_title": r.law_title, "doc_number": r.doc_number, "doc_type": r.doc_type,
        }
        for r in rows
    ]


@router.post("/api/writing/{job_id}/regulations")
async def add_writing_regulation(
    job_id: int,
    law_doc_id: Optional[int] = None,
    uploaded_content: Optional[str] = None,
    uploaded_filename: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.execute(
        text("""
            INSERT INTO taxlegal.writing_regulations
                (job_id, law_doc_id, uploaded_content, uploaded_filename)
            VALUES (:jid, :ldid, :uc, :uf)
        """),
        {"jid": job_id, "ldid": law_doc_id, "uc": uploaded_content, "uf": uploaded_filename}
    )
    await db.commit()
    return {"status": "added"}


@router.post("/api/writing/{job_id}/regulations/upload")
async def upload_writing_regulation(
    job_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content_bytes = await file.read()
    filename = file.filename or "regulation.txt"
    ext = filename.rsplit(".", 1)[-1].lower()
    content_text = ""
    try:
        if ext == "txt":
            content_text = content_bytes.decode("utf-8", errors="ignore")
        elif ext == "pdf":
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(content_bytes))
            content_text = "\n".join(p.extract_text() for p in reader.pages if p.extract_text())
        elif ext in ("docx", "doc"):
            import io, docx as docxlib
            doc = docxlib.Document(io.BytesIO(content_bytes))
            content_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        else:
            content_text = content_bytes.decode("utf-8", errors="ignore")
    except Exception:
        content_text = content_bytes.decode("utf-8", errors="ignore")

    await db.execute(
        text("INSERT INTO taxlegal.writing_regulations (job_id, uploaded_content, uploaded_filename) VALUES (:jid, :uc, :uf)"),
        {"jid": job_id, "uc": content_text, "uf": filename}
    )
    await db.commit()
    return {"status": "uploaded", "filename": filename}


@router.delete("/api/writing/{job_id}/regulations/{reg_id}", status_code=204)
async def remove_writing_regulation(
    job_id: int, reg_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.execute(
        text("DELETE FROM taxlegal.writing_regulations WHERE id=:id AND job_id=:jid"),
        {"id": reg_id, "jid": job_id}
    )
    await db.commit()


# ── Document Analysis (Phân tích văn bản) ────────────────────────────────────

DOC_ANALYSIS_ACTIONS = [
    {"slug": "review", "label": "Rà soát văn bản", "description": "Kiểm tra tính đầy đủ, hợp lệ của văn bản"},
    {"slug": "applicable_regulations", "label": "Tư vấn quy định áp dụng", "description": "Xác định các quy định pháp luật liên quan"},
    {"slug": "legal_risk", "label": "Tư vấn rủi ro pháp luật", "description": "Phân tích các rủi ro pháp lý tiềm ẩn"},
    {"slug": "tax_risk", "label": "Tư vấn rủi ro thuế", "description": "Phân tích nghĩa vụ và rủi ro thuế"},
    {"slug": "draft", "label": "Soạn thảo văn bản", "description": "Hỗ trợ soạn thảo hoặc chỉnh sửa văn bản"},
]

@router.get("/api/doc-analysis/actions")
async def list_doc_analysis_actions(_user: User = Depends(get_current_user)):
    return DOC_ANALYSIS_ACTIONS


@router.get("/api/doc-analysis")
async def list_doc_analysis_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        text("""
            SELECT id, title, uploaded_filename, output_language, actions,
                   status, created_at
            FROM taxlegal.doc_analysis_jobs
            WHERE created_by = :uid
            ORDER BY created_at DESC LIMIT 50
        """),
        {"uid": current_user.id}
    )
    rows = result.fetchall()
    return [
        {
            "id": r.id, "title": r.title, "uploaded_filename": r.uploaded_filename,
            "output_language": r.output_language, "actions": r.actions,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


class DocAnalysisCreate(BaseModel):
    title: str
    output_language: str = "vi"
    actions: List[dict]  # [{"slug": "review", "custom_prompt": ""}, ...]
    regulation_ids: Optional[List[int]] = []
    bot_variant_id: Optional[int] = None


@router.post("/api/doc-analysis", status_code=201)
async def create_doc_analysis_job(
    title: str = Form(...),
    output_language: str = Form("vi"),
    actions: str = Form("[]"),  # JSON string
    regulation_ids: str = Form("[]"),  # JSON string
    bot_variant_id: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import json
    actions_list = json.loads(actions)
    reg_ids = json.loads(regulation_ids)

    uploaded_content = ""
    uploaded_filename = None

    if file:
        content_bytes = await file.read()
        uploaded_filename = file.filename or "document"
        ext = (uploaded_filename.rsplit(".", 1)[-1] if "." in uploaded_filename else "txt").lower()
        try:
            if ext == "txt":
                uploaded_content = content_bytes.decode("utf-8", errors="ignore")
            elif ext == "pdf":
                from pypdf import PdfReader
                import io
                reader = PdfReader(io.BytesIO(content_bytes))
                uploaded_content = "\n".join(p.extract_text() for p in reader.pages if p.extract_text())
            elif ext in ("docx", "doc"):
                import io, docx as docxlib
                doc = docxlib.Document(io.BytesIO(content_bytes))
                uploaded_content = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            else:
                uploaded_content = content_bytes.decode("utf-8", errors="ignore")
        except Exception:
            uploaded_content = content_bytes.decode("utf-8", errors="ignore")

    result = await db.execute(
        text("""
            INSERT INTO taxlegal.doc_analysis_jobs
                (title, uploaded_filename, uploaded_content, output_language,
                 actions, regulation_ids, bot_variant_id, status, created_by)
            VALUES
                (:title, :filename, :content, :lang,
                 :actions, :reg_ids, :bot_id, 'pending', :uid)
            RETURNING id, title, status, created_at
        """),
        {
            "title": title, "filename": uploaded_filename,
            "content": uploaded_content, "lang": output_language,
            "actions": json.dumps(actions_list), "reg_ids": reg_ids,
            "bot_id": bot_variant_id, "uid": current_user.id,
        }
    )
    row = result.fetchone()
    await db.commit()
    return {"id": row.id, "title": row.title, "status": row.status,
            "created_at": row.created_at.isoformat() if row.created_at else None}


@router.get("/api/doc-analysis/{job_id}")
async def get_doc_analysis_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        text("SELECT * FROM taxlegal.doc_analysis_jobs WHERE id=:id AND created_by=:uid"),
        {"id": job_id, "uid": current_user.id}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return dict(row._mapping)


@router.post("/api/doc-analysis/{job_id}/analyze")
async def run_doc_analysis(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run AI analysis for each selected action."""
    result = await db.execute(
        text("SELECT * FROM taxlegal.doc_analysis_jobs WHERE id=:id AND created_by=:uid"),
        {"id": job_id, "uid": current_user.id}
    )
    job = result.fetchone()
    if not job:
        raise HTTPException(status_code=404, detail="Not found")

    # Mark as analyzing
    await db.execute(
        text("UPDATE taxlegal.doc_analysis_jobs SET status='analyzing', updated_at=NOW() WHERE id=:id"),
        {"id": job_id}
    )
    await db.commit()

    try:
        from backend.ai_provider import call_ai
        from backend.config import DEEPSEEK_MODEL
        import json

        # Get regulation context
        reg_context = ""
        if job.regulation_ids:
            reg_result = await db.execute(
                text("""
                    SELECT title, doc_number, content_text
                    FROM taxlegal.law_documents_v2
                    WHERE id = ANY(:ids) AND is_active = TRUE
                """),
                {"ids": job.regulation_ids}
            )
            reg_rows = reg_result.fetchall()
            if reg_rows:
                parts = ["## QUY ĐỊNH ÁP DỤNG\n"]
                for r in reg_rows:
                    parts.append(f"### {r.title} ({r.doc_number or ''})\n{(r.content_text or '')[:3000]}\n")
                reg_context = "\n".join(parts)

        # Also get priority docs as fallback context
        if not reg_context:
            pd_result = await db.execute(
                text("""
                    SELECT title, content
                    FROM taxlegal.priority_docs
                    WHERE is_active = TRUE
                    ORDER BY priority_level ASC
                    LIMIT 3
                """)
            )
            pd_rows = pd_result.fetchall()
            if pd_rows:
                parts = ["## TÀI LIỆU THAM KHẢO ƯU TIÊN\n"]
                for r in pd_rows:
                    parts.append(f"### {r.title}\n{(r.content or '')[:2000]}\n")
                reg_context = "\n".join(parts)

        lang = job.output_language or "vi"
        doc_content = (job.uploaded_content or "")[:15000]

        action_prompts = {
            "review": "Rà soát văn bản: kiểm tra tính đầy đủ, hợp lệ về mặt pháp lý và hình thức. Nêu các điểm thiếu sót, không rõ ràng, mâu thuẫn.",
            "applicable_regulations": "Xác định TẤT CẢ các quy định pháp luật Việt Nam áp dụng cho văn bản này. Trích dẫn cụ thể số điều, khoản. Ưu tiên các quy định trong phần 'Quy định áp dụng' bên trên.",
            "legal_risk": "Phân tích rủi ro pháp luật: các điều khoản bất lợi, không rõ ràng, vi phạm pháp luật tiềm ẩn, rủi ro tranh chấp.",
            "tax_risk": "Phân tích nghĩa vụ thuế và rủi ro thuế: VAT, CIT, PIT, FCT, thuế chuyển nhượng tài sản v.v. Áp dụng conservative defaults.",
            "draft": "Hỗ trợ soạn thảo: đề xuất cách chỉnh sửa, bổ sung điều khoản. Cung cấp bản thảo cải tiến nếu có thể.",
        }

        if lang == "en":
            system_prompt = "You are a Vietnam tax and legal expert. Analyze the provided document with citation-first approach. Always cite specific legal provisions (Law/Decree/Circular + article number)."
        else:
            system_prompt = "Bạn là chuyên gia thuế và pháp luật Việt Nam. Phân tích văn bản với nguyên tắc citation-first. Luôn trích dẫn cụ thể quy định (Luật/Nghị định/Thông tư + số điều)."

        actions = job.actions if isinstance(job.actions, list) else json.loads(job.actions or "[]")
        results_dict = {}

        for action in actions:
            slug = action.get("slug", "")
            custom_prompt = action.get("custom_prompt", "")
            base_prompt = action_prompts.get(slug, custom_prompt or f"Thực hiện action: {slug}")
            final_prompt = custom_prompt if custom_prompt else base_prompt

            if lang == "vi":
                user_msg = f"""## VĂN BẢN CẦN PHÂN TÍCH
{doc_content}

{reg_context}

## YÊU CẦU
{final_prompt}

Viết bằng TIẾNG VIỆT chuyên nghiệp. Mỗi nhận định phải có căn cứ pháp lý."""
            else:
                user_msg = f"""## DOCUMENT TO ANALYZE
{doc_content}

{reg_context}

## TASK
{final_prompt}

Write in professional ENGLISH. Every finding must include legal citations."""

            try:
                response = await call_ai(
                    model_id=DEEPSEEK_MODEL or "deepseek-chat",
                    messages=[{"role": "user", "content": user_msg}],
                    system_prompt=system_prompt,
                    max_tokens=8000,
                    temperature=0.3,
                )
                results_dict[slug] = response.get("content", "") if isinstance(response, dict) else str(response)
            except Exception as e:
                results_dict[slug] = f"Lỗi khi phân tích: {str(e)}"

        await db.execute(
            text("""
                UPDATE taxlegal.doc_analysis_jobs
                SET results=:results, status='done', updated_at=NOW()
                WHERE id=:id
            """),
            {"results": json.dumps(results_dict, ensure_ascii=False), "id": job_id}
        )
        await db.commit()
        return {"status": "done", "results": results_dict}

    except Exception as e:
        await db.execute(
            text("UPDATE taxlegal.doc_analysis_jobs SET status='error', updated_at=NOW() WHERE id=:id"),
            {"id": job_id}
        )
        await db.commit()
        logger.error(f"Doc analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/doc-analysis/{job_id}", status_code=204)
async def delete_doc_analysis_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.execute(
        text("DELETE FROM taxlegal.doc_analysis_jobs WHERE id=:id AND created_by=:uid"),
        {"id": job_id, "uid": current_user.id}
    )
    await db.commit()
