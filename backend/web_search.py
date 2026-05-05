"""
Perplexity Sonar API — web search for fact/legal verification.
Used by all agents for chain-of-custody verification.
"""
import httpx
import logging
from backend.config import PERPLEXITY_API_KEY, PERPLEXITY_SEARCH_MODEL

logger = logging.getLogger(__name__)

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"


async def web_search(query: str, context: str = "") -> dict:
    """
    Perform a web search via Perplexity Sonar.
    Returns: {"answer": str, "citations": list[str], "query": str}
    """
    if not PERPLEXITY_API_KEY:
        logger.warning("PERPLEXITY_API_KEY not set — web search disabled")
        return {"answer": "[Web search unavailable — no API key]", "citations": [], "query": query}

    messages = []
    if context:
        messages.append({
            "role": "system",
            "content": (
                "Bạn là trợ lý pháp lý chuyên tra cứu luật Việt Nam. "
                "Hãy tìm kiếm và cung cấp thông tin chính xác, có dẫn nguồn. "
                f"Context: {context}"
            )
        })
    messages.append({"role": "user", "content": query})

    payload = {
        "model": PERPLEXITY_SEARCH_MODEL,
        "messages": messages,
        "return_citations": True,
        "search_recency_filter": "month",
    }

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(PERPLEXITY_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            answer = data["choices"][0]["message"]["content"]
            citations = data.get("citations", [])
            return {"answer": answer, "citations": citations, "query": query}
    except Exception as e:
        logger.error(f"Perplexity search error for '{query}': {e}")
        return {"answer": f"[Search error: {e}]", "citations": [], "query": query}


async def verify_law_currency(law_identifier: str, article: str = "") -> dict:
    """
    Verify if a specific law/article is still in effect (legal currency check).
    Returns: {"is_current": bool, "status": str, "replaced_by": str|None, "sources": list}
    """
    query = (
        f"Văn bản pháp lý '{law_identifier}'"
        + (f" Điều {article}" if article else "")
        + " còn hiệu lực không? Đã bị sửa đổi, thay thế hay bãi bỏ chưa?"
        + " Văn bản thay thế (nếu có) là gì? Nguồn: thuvienphapluat.vn, luatvietnam.vn"
    )
    result = await web_search(query, context="legal currency verification")
    answer_lower = result["answer"].lower()

    is_current = any(w in answer_lower for w in ["còn hiệu lực", "đang có hiệu lực", "chưa bị thay thế"])
    replaced = any(w in answer_lower for w in ["thay thế", "bãi bỏ", "hết hiệu lực", "replaced"])

    return {
        "law": law_identifier,
        "article": article,
        "is_current": is_current and not replaced,
        "status": "CURRENT" if (is_current and not replaced) else "POSSIBLY_SUPERSEDED",
        "answer": result["answer"],
        "sources": result["citations"],
    }


async def verify_fact(fact: str) -> dict:
    """
    Verify a client-stated fact via web search.
    Returns: {"status": str, "sources": list, "answer": str}
    VERIFIED | CLIENT-STATED | UNVERIFIED | CONFLICTING
    """
    query = f"Xác minh thông tin: {fact} — Nguồn chính thức Việt Nam"
    result = await web_search(query)

    if len(result["citations"]) >= 2:
        status = "VERIFIED"
    elif len(result["citations"]) == 1:
        status = "UNVERIFIED"
    elif "[Search error" in result["answer"]:
        status = "CLIENT-STATED"
    else:
        status = "UNVERIFIED"

    return {
        "fact": fact,
        "status": status,
        "answer": result["answer"],
        "sources": result["citations"],
    }


async def search_practical_guidance(topic: str, law_area: str = "") -> dict:
    """
    Search for practical guidance, best practices, pitfalls from practitioners.
    """
    query = (
        f"Hướng dẫn thực tiễn, lưu ý khi thực hiện: {topic}"
        + (f" theo quy định {law_area}" if law_area else "")
        + " — kinh nghiệm thực tế, cạm bẫy cần tránh, tips từ chuyên gia"
    )
    return await web_search(query, context="practical legal guidance Vietnam")
