"""
Prompt guards to prevent AI from fabricating tax law.
"""
from __future__ import annotations

DB_FIRST_SYSTEM_ADDENDUM = '''
## CRITICAL: SOURCE INTEGRITY RULES

You MUST follow these rules without exception:
1. Only cite laws and regulations that appear in the RETRIEVED SOURCES section below.
2. If a legal question is not covered by the retrieved sources, explicitly state: 
   "Không đủ nguồn để kết luận về vấn đề này (insufficient source coverage)."
3. Never invent, guess, or hallucinate article numbers, effective dates, or legal provisions.
4. Every legal assertion must be traceable to a specific source in the RETRIEVED SOURCES.
5. If retrieved sources conflict, present both and note the conflict — do not resolve it arbitrarily.
6. Sources from internal database (DB) are more trusted than web search results.
7. If only web search results are available, preface conclusions with "Theo kết quả tìm kiếm web (chưa xác minh từ DB):"

Violation of these rules constitutes a CRITICAL ERROR (code R16/R17).
'''


def build_retrieval_context_block(retrieval_result: "RetrievalResult") -> str:
    """Build the RETRIEVED SOURCES block to inject into prompts."""
    # Import here to avoid circular imports at module load time
    from backend.retrieval.service import RetrievalResult  # noqa: F401

    if retrieval_result.insufficient_coverage:
        return (
            "\n## RETRIEVED SOURCES\n"
            "[INSUFFICIENT SOURCE COVERAGE — No relevant sources found in DB or web search. "
            "Do NOT fabricate any legal provisions.]\n"
        )

    lines = ["\n## RETRIEVED SOURCES"]
    all_results = retrieval_result.db_results + retrieval_result.web_results

    if not all_results:
        lines.append("\n[No sources retrieved — do not fabricate legal provisions.]\n")
        return "\n".join(lines)

    for i, result in enumerate(all_results, 1):
        trust = result.get("trust_level", "medium").upper()
        source_type = result.get("source_type", "unknown")
        lines.append(f"\n### Source {i} [{trust} TRUST — {source_type}]")
        if result.get("doc_number"):
            lines.append(f"Document: {result['doc_number']}")
        if result.get("title"):
            lines.append(f"Title: {result['title']}")
        # Prefer 'content_text', fall back to 'answer' for web results
        excerpt = result.get("content_text") or result.get("answer") or ""
        lines.append(f"Excerpt: {excerpt[:1000]}")
        if result.get("source_url"):
            lines.append(f"Source URL: {result['source_url']}")

    return "\n".join(lines)
