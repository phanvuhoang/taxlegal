"""
Law search endpoints — hybrid semantic + keyword.
"""
from fastapi import APIRouter, Query, Depends
from typing import Optional
from backend.auth import get_current_user
from backend.legalai.search import hybrid_search, search_law_documents
from backend.legalai.embedder import get_embedder

router = APIRouter(prefix="/api/legalai/search", tags=["Legal Search"])


@router.get("/laws")
async def search_laws(
    q: str = Query(..., min_length=2, description="Từ khóa tìm kiếm"),
    domains: Optional[str] = Query(
        None, description="Domains phân cách bằng dấu phẩy: thue,cit,vat"
    ),
    limit: int = Query(10, ge=1, le=50),
    current_user=Depends(get_current_user),
):
    """Search law documents at title/summary level."""
    domain_list = [d.strip() for d in domains.split(",")] if domains else None
    results = await search_law_documents(q, domains=domain_list, limit=limit)
    return {"results": results, "query": q, "total": len(results)}


@router.get("/chunks")
async def search_chunks(
    q: str = Query(..., min_length=2),
    domains: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=30),
    current_user=Depends(get_current_user),
):
    """Search law chunks using hybrid semantic + keyword search."""
    domain_list = [d.strip() for d in domains.split(",")] if domains else None

    embedder = get_embedder()
    embedding = await embedder.embed(q) if embedder.available else None

    results = await hybrid_search(
        query_text=q,
        query_embedding=embedding,
        domains=domain_list,
        limit=limit,
    )

    return {
        "results": [
            {
                "chunk_id": r.chunk_id,
                "law_id": r.law_id,
                "law_title": r.law_title,
                "law_number": r.law_number,
                "article": r.article,
                "clause": r.clause,
                "content": r.content,
                "parent_context": r.parent_context,
                "score": r.combined_score,
                "law_status": r.law_status,
                "domains": r.domains,
                "source_url": r.source_url,
            }
            for r in results
        ],
        "query": q,
        "total": len(results),
        "search_type": "hybrid" if embedding else "keyword",
    }
