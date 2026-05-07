"""
Writing content generator — citation-first prompting, priority docs injection,
multi-section generation, language toggle, SSE streaming support.
Max tokens: 16,000 to avoid truncation.
"""
import asyncio
import logging
from typing import Optional, List, AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

logger = logging.getLogger(__name__)

# Content type descriptions
CONTENT_TYPES = {
    "analysis": {
        "vi": "bài phân tích thuế chi tiết",
        "en": "detailed tax analysis article",
    },
    "advisory": {
        "vi": "tư vấn thuế chuyên nghiệp",
        "en": "professional tax advisory memo",
    },
    "press": {
        "vi": "bài báo/thông cáo thuế",
        "en": "tax press release / article",
    },
    "scenario": {
        "vi": "phân tích tình huống thuế",
        "en": "tax scenario analysis",
    },
}

SYSTEM_PROMPT_VI = """Bạn là chuyên gia thuế Việt Nam với 30 năm kinh nghiệm, chuyên về thuế quốc tế và thuế nội địa.

## NGUYÊN TẮC VIẾT BÀI
1. **Citation-first**: Trước khi viết luận điểm nào, xác định rõ điều khoản pháp lý cụ thể (Luật, Nghị định, Thông tư + số điều).
2. **Conservative defaults**: Khi có ambiguity → chọn phương án an toàn hơn (nộp thuế nhiều hơn để tránh vi phạm).
3. **3-state contract**:
   - Rõ ràng → trình bày position với citation
   - Không chắc → ghi chú "Thận trọng: áp dụng mức cao hơn" 
   - Thiếu thông tin → yêu cầu làm rõ trước khi đưa kết luận
4. **Cấu trúc**: Tiêu đề → Tóm tắt → Cơ sở pháp lý → Phân tích → Kết luận → Khuyến nghị
5. **Ngôn ngữ**: Tiếng Việt chuyên nghiệp, thuật ngữ chính xác.
"""

SYSTEM_PROMPT_EN = """You are a Vietnam tax expert with 30 years of experience in domestic and international tax.

## WRITING PRINCIPLES
1. **Citation-first**: Before stating any position, identify the specific legal provision (Law/Decree/Circular + article number).
2. **Conservative defaults**: When uncertain → choose the option that costs more tax (protects client from underpayment).
3. **3-state contract**:
   - Clear law + clear facts → state position with citation
   - Uncertain → note "Conservative: applying higher rate/stricter interpretation"
   - Insufficient facts → request clarification before concluding
4. **Structure**: Title → Executive Summary → Legal Framework → Analysis → Conclusion → Recommendations
5. **Language**: Professional English with precise tax terminology.
"""


async def get_priority_docs_context(db: AsyncSession, topic: str, limit: int = 5) -> str:
    """Fetch highest-priority anchor documents relevant to the topic."""
    try:
        result = await db.execute(
            text("""
                SELECT title, doc_type, content, priority_level
                FROM taxlegal.priority_docs
                WHERE is_active = TRUE
                ORDER BY priority_level ASC, created_at DESC
                LIMIT :limit
            """),
            {"limit": limit}
        )
        docs = result.fetchall()
        if not docs:
            return ""

        context_parts = ["## TÀI LIỆU ƯU TIÊN CAO (ANCHOR DOCUMENTS)\n"]
        for doc in docs:
            context_parts.append(f"### {doc.title} [{doc.doc_type}]\n{doc.content[:2000]}\n")
        return "\n".join(context_parts)
    except Exception as e:
        logger.warning(f"Failed to fetch priority docs: {e}")
        return ""


async def get_skills_context(db: AsyncSession, skill_ids: List[int]) -> str:
    """Fetch skill markdown content for injection."""
    if not skill_ids:
        return ""
    try:
        placeholders = ", ".join([f":s{i}" for i in range(len(skill_ids))])
        params = {f"s{i}": sid for i, sid in enumerate(skill_ids)}
        result = await db.execute(
            text(f"SELECT name, content_markdown FROM taxlegal.skills WHERE id IN ({placeholders}) AND is_active = TRUE"),
            params
        )
        skills = result.fetchall()
        if not skills:
            return ""
        parts = ["## SKILLS ACTIVATED\n"]
        for skill in skills:
            parts.append(f"### {skill.name}\n{skill.content_markdown}\n")
        return "\n".join(parts)
    except Exception as e:
        logger.warning(f"Failed to fetch skills: {e}")
        return ""


async def generate_writing_content(
    topic: str,
    context: str,
    content_type: str,
    output_language: str,
    db: AsyncSession,
    skill_ids: List[int] = None,
    word_count_target: int = 2000,
    regulation_ids: List[int] = None,
) -> str:
    """
    Generate full writing content with citation-first prompting.
    Uses priority docs + skills injection + max 16,000 tokens.
    """
    from backend.ai_provider import call_ai
    from backend.config import DEFAULT_AGENT_MODELS

    lang = output_language if output_language in ("vi", "en") else "vi"
    system_prompt = SYSTEM_PROMPT_VI if lang == "vi" else SYSTEM_PROMPT_EN

    # Build context from priority docs + skills
    priority_context = await get_priority_docs_context(db, topic)
    skills_context = await get_skills_context(db, skill_ids or [])

    # Load regulation context if provided
    regulation_context = ""
    if regulation_ids:
        try:
            placeholders = ", ".join([f":r{i}" for i in range(len(regulation_ids))])
            reg_params = {f"r{i}": rid for i, rid in enumerate(regulation_ids)}
            reg_result = await db.execute(
                text(f"""
                    SELECT title, doc_number, content_text
                    FROM taxlegal.law_documents_v2
                    WHERE id IN ({placeholders}) AND is_active = TRUE
                """),
                reg_params
            )
            reg_rows = reg_result.fetchall()
            if reg_rows:
                parts = ["## QUY ĐỊNH ÁP DỤNG (ĐỌC TRƯỚC KHI VIẾT)\n"]
                for r in reg_rows:
                    parts.append(f"### {r.title} ({r.doc_number or ''})\n{(r.content_text or '')[:4000]}\n")
                regulation_context = "\n".join(parts)
        except Exception as e:
            logger.warning(f"Failed to load regulations: {e}")

    content_desc = CONTENT_TYPES.get(content_type, CONTENT_TYPES["analysis"])[lang]

    if lang == "vi":
        user_prompt = f"""Viết {content_desc} về chủ đề sau:

## CHỦ ĐỀ
{topic}

## THÔNG TIN BỔ SUNG
{context or 'Không có thông tin bổ sung.'}

{priority_context}

{skills_context}

{regulation_context}

## YÊU CẦU
- Độ dài mục tiêu: khoảng {word_count_target} từ
- Mỗi luận điểm phải có citation cụ thể (Tên văn bản + số điều)
- Áp dụng conservative defaults khi có ambiguity
- Kết luận rõ ràng với khuyến nghị thực tế
- Format Markdown với đầy đủ heading, sub-heading
"""
    else:
        user_prompt = f"""Write a {content_desc} on the following topic:

## TOPIC
{topic}

## ADDITIONAL CONTEXT
{context or 'No additional context provided.'}

{priority_context}

{skills_context}

{regulation_context}

## REQUIREMENTS
- Target length: approximately {word_count_target} words
- Every legal position must have a specific citation (document name + article number)
- Apply conservative defaults when uncertain
- Clear conclusion with practical recommendations
- Full Markdown format with headings and sub-headings
"""

    # Use JA model (highest quality) with max_tokens=16000
    model_id = DEFAULT_AGENT_MODELS.get("ja", "deepseek-chat")

    result = await call_ai(
        model_id=model_id,
        messages=[{"role": "user", "content": user_prompt}],
        system_prompt=system_prompt,
        max_tokens=16000,
        temperature=0.3,
    )

    return result["content"]


async def generate_writing_content_stream(
    topic: str,
    context: str,
    content_type: str,
    output_language: str,
    db: AsyncSession,
    skill_ids: List[int] = None,
    word_count_target: int = 2000,
) -> AsyncIterator[str]:
    """SSE streaming version of content generation."""
    # For now, generate full content then stream in chunks
    # TODO: implement true streaming when AI provider supports it
    content = await generate_writing_content(
        topic=topic,
        context=context,
        content_type=content_type,
        output_language=output_language,
        db=db,
        skill_ids=skill_ids,
        word_count_target=word_count_target,
    )

    # Stream in chunks of ~200 chars
    chunk_size = 200
    for i in range(0, len(content), chunk_size):
        yield content[i:i + chunk_size]
        await asyncio.sleep(0.01)
