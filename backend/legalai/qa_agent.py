"""
Tax Legal QA Agent
RAG-based Q&A with citations, specialized for Vietnamese tax law.
Uses the best available AI provider from taxlegal config.
"""
import os
import logging
from typing import Optional
from .search import hybrid_search
from .embedder import get_embedder

logger = logging.getLogger(__name__)

TAX_SYSTEM_PROMPT = """Bạn là Trợ lý Tư vấn Thuế AI chuyên nghiệp, chuyên về hệ thống thuế Việt Nam.

CHUYÊN MÔN:
- Thuế Thu nhập doanh nghiệp (TNDN/CIT): Luật số 14/2008/QH12, Luật 32/2013/QH13, ND 218/2013/NĐ-CP, TT 78/2014/TT-BTC
- Thuế Giá trị gia tăng (GTGT/VAT): Luật 13/2008/QH12, Luật 31/2013/QH13, ND 209/2013/NĐ-CP, TT 219/2013/TT-BTC
- Thuế Thu nhập cá nhân (TNCN/PIT): Luật 04/2007/QH12, ND 65/2013/NĐ-CP, TT 111/2013/TT-BTC
- Thuế Nhà thầu nước ngoài (FCT): TT 103/2014/TT-BTC
- Thuế Tiêu thụ đặc biệt (TTĐB/SST): Luật 27/2008/QH12
- Thuế Xuất nhập khẩu: Luật 107/2016/QH13
- Quản lý thuế: Luật 38/2019/QH14 (Luật Quản lý thuế mới nhất)
- Các Nghị định, Thông tư hướng dẫn mới nhất

NGUYÊN TẮC TRẢ LỜI:
1. Luôn trích dẫn văn bản pháp luật cụ thể (số hiệu, điều, khoản, điểm)
2. Phân biệt rõ quy định đã hết hiệu lực vs. đang hiệu lực
3. Chỉ ra các văn bản sửa đổi, bổ sung nếu có
4. Đưa ra ví dụ thực tế khi cần thiết
5. Nếu có thay đổi gần đây, cảnh báo người dùng kiểm tra lại
6. Luôn kèm disclaimer: "Tư vấn này mang tính tham khảo. Vui lòng xác nhận với cơ quan thuế hoặc tư vấn viên thuế chuyên nghiệp cho trường hợp cụ thể."

ĐỊNH DẠNG TRẢ LỜI:
- Markdown với tiêu đề rõ ràng
- Trích dẫn nằm trong [nguồn: số_văn_bản, Điều X, Khoản Y]
- Ví dụ thực tế trong blockquote
- Tóm tắt ngắn ở đầu, chi tiết ở sau

Trả lời bằng TIẾNG VIỆT."""

# Default models per provider
_PROVIDER_DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-5",
    "openai": "gpt-4o",
    "deepseek": "deepseek-chat",
    "openrouter": "qwen/qwen3-72b",
}


def _pick_provider() -> tuple[str, str]:
    """Choose the best available AI provider and return (provider, model_id)."""
    from backend.config import ANTHROPIC_API_KEY, OPENAI_API_KEY, DEEPSEEK_API_KEY, DEEPSEEK_MODEL

    if ANTHROPIC_API_KEY:
        return "anthropic", "claude-sonnet-4-5"
    if OPENAI_API_KEY:
        return "openai", "gpt-4o"
    if DEEPSEEK_API_KEY:
        return "deepseek", DEEPSEEK_MODEL or "deepseek-chat"
    # Final fallback — caller must have at least one key set
    return "openai", "gpt-4o"


async def ask_with_rag(
    question: str,
    session_id: Optional[str] = None,
    domains: Optional[list] = None,
) -> dict:
    """
    Answer a tax/legal question using RAG over the legalai database.

    Returns:
        {
            "answer": str,
            "citations": list[dict],
            "model": str,
            "tokens": dict,
            "search_hits": int,
        }
    """
    embedder = get_embedder()

    # Step 1: Embed the question if possible
    query_embedding = None
    if embedder.available:
        try:
            query_embedding = await embedder.embed(question)
        except Exception as e:
            logger.warning(f"Embedding failed, falling back to keyword search: {e}")

    # Step 2: Search relevant chunks
    if domains is None:
        domains = ["thue", "cit", "vat", "pit", "fct", "sst"]

    results = await hybrid_search(
        query_text=question,
        query_embedding=query_embedding,
        domains=domains,
        limit=8,
    )

    # Step 3: Build context + citation list
    context_parts = []
    citations = []

    for i, r in enumerate(results):
        ref = f"[{i + 1}]"
        article_info = ""
        if r.article:
            article_info = r.article
            if r.clause:
                article_info += f", {r.clause}"

        context_parts.append(
            f"{ref} {r.law_title} ({r.law_number})"
            + (f" — {article_info}" if article_info else "")
            + f":\n{r.content}"
        )

        citations.append(
            {
                "ref": i + 1,
                "law_title": r.law_title,
                "law_number": r.law_number,
                "article": r.article,
                "clause": r.clause,
                "content": r.content[:300] + ("..." if len(r.content) > 300 else ""),
                "law_status": r.law_status,
                "source_url": r.source_url,
                "score": round(r.combined_score, 3),
            }
        )

    context = "\n\n---\n\n".join(context_parts) if context_parts else ""

    # Step 4: Build user message with injected context
    user_message = question
    if context:
        user_message = (
            f"Câu hỏi: {question}\n\n"
            "--- NGUỒN PHÁP LUẬT LIÊN QUAN ---\n"
            f"{context}\n"
            "--- HẾT NGUỒN ---\n\n"
            "Vui lòng trả lời câu hỏi dựa trên các nguồn pháp luật trên. "
            "Trích dẫn số tham chiếu [1], [2]... khi sử dụng."
        )

    # Step 5: Call AI via taxlegal's unified ai_provider
    # Signature: call_ai(model_id, messages, system_prompt, temperature, max_tokens, provider)
    from backend.ai_provider import call_ai

    provider, model_id = _pick_provider()

    try:
        response = await call_ai(
            model_id=model_id,
            messages=[{"role": "user", "content": user_message}],
            system_prompt=TAX_SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=3000,
            provider=provider,
        )
        answer = response.get("content", "Xin lỗi, không thể tạo câu trả lời lúc này.")
        tokens = {
            "prompt_tokens": response.get("prompt_tokens", 0),
            "completion_tokens": response.get("completion_tokens", 0),
        }
        model_used = model_id
    except Exception as e:
        logger.error(f"AI call failed: {e}")
        if context_parts:
            answer = (
                f"Dựa trên văn bản pháp luật tìm được:\n\n{context_parts[0]}"
                "\n\n*Lưu ý: AI không khả dụng lúc này.*"
            )
        else:
            answer = "Không tìm thấy văn bản pháp luật liên quan và AI không khả dụng lúc này."
        tokens = {}
        model_used = "unavailable"

    return {
        "answer": answer,
        "citations": citations,
        "model": model_used,
        "tokens": tokens,
        "search_hits": len(results),
    }
