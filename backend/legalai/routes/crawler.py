"""
Crawler management endpoints (mostly admin-only).
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List
from sqlalchemy import text
from backend.auth import get_current_user, get_current_admin
from backend.legalai.database import LegalAISession
from backend.legalai.crawler import TaxCrawler, PRIORITY_TAX_URLS, TAX_SOURCES

router = APIRouter(prefix="/api/legalai/crawler", tags=["Tax Crawler"])


class CrawlRequest(BaseModel):
    url: str


class BatchCrawlRequest(BaseModel):
    urls: List[str]


async def _do_crawl(url: str, job_id: str):
    """Background task: run one crawl job and update its status."""
    crawler = TaxCrawler()
    try:
        async with LegalAISession() as session:
            await session.execute(
                text("UPDATE crawl_jobs SET status='running' WHERE id=:id"),
                {"id": job_id},
            )
            await session.commit()

        result = await crawler.crawl_and_index(url, job_id=job_id)

        async with LegalAISession() as session:
            if result.get("success"):
                await session.execute(
                    text("""
                        UPDATE crawl_jobs
                        SET status='done', result_count=:count, completed_at=NOW()
                        WHERE id=:id
                    """),
                    {"id": job_id, "count": result.get("chunks_indexed", 0)},
                )
            else:
                await session.execute(
                    text("""
                        UPDATE crawl_jobs
                        SET status='failed', error=:error, completed_at=NOW()
                        WHERE id=:id
                    """),
                    {"id": job_id, "error": result.get("error", "Unknown error")},
                )
            await session.commit()
    except Exception as e:
        async with LegalAISession() as session:
            await session.execute(
                text("""
                    UPDATE crawl_jobs
                    SET status='failed', error=:error, completed_at=NOW()
                    WHERE id=:id
                """),
                {"id": job_id, "error": str(e)},
            )
            await session.commit()


@router.get("/sources")
async def list_sources(current_user=Depends(get_current_user)):
    """List available tax law sources and configuration status."""
    import os

    return {
        "sources": TAX_SOURCES,
        "priority_urls": PRIORITY_TAX_URLS,
        "crawlkit_configured": bool(os.getenv("CRAWLKIT_API_KEY")),
    }


@router.post("/crawl")
async def crawl_url(
    req: CrawlRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_admin),
):
    """Trigger a crawl job for a single URL (admin only)."""
    job_id = str(uuid.uuid4())
    async with LegalAISession() as session:
        await session.execute(
            text("INSERT INTO crawl_jobs (id, url, status) VALUES (:id, :url, 'pending')"),
            {"id": job_id, "url": req.url},
        )
        await session.commit()

    background_tasks.add_task(_do_crawl, req.url, job_id)
    return {"job_id": job_id, "url": req.url, "status": "started"}


@router.post("/crawl-priority")
async def crawl_priority_urls(
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_admin),
):
    """Crawl all priority tax law URLs (admin only)."""
    jobs = []
    for url in PRIORITY_TAX_URLS:
        job_id = str(uuid.uuid4())
        async with LegalAISession() as session:
            await session.execute(
                text("""
                    INSERT INTO crawl_jobs (id, url, status)
                    VALUES (:id, :url, 'pending')
                    ON CONFLICT DO NOTHING
                """),
                {"id": job_id, "url": url},
            )
            await session.commit()
        background_tasks.add_task(_do_crawl, url, job_id)
        jobs.append({"job_id": job_id, "url": url})

    return {"started": len(jobs), "jobs": jobs}


@router.get("/jobs")
async def list_crawl_jobs(current_user=Depends(get_current_admin)):
    """List crawl jobs (admin only)."""
    async with LegalAISession() as session:
        result = await session.execute(
            text("""
                SELECT id, url, status, result_count, error, created_at, completed_at
                FROM crawl_jobs
                ORDER BY created_at DESC
                LIMIT 100
            """)
        )
        rows = result.mappings().all()
    return {"jobs": [dict(r) for r in rows]}


@router.get("/stats")
async def get_stats(current_user=Depends(get_current_user)):
    """Get law database statistics."""
    async with LegalAISession() as session:
        docs = await session.execute(text("SELECT COUNT(*) FROM law_documents"))
        chunks = await session.execute(text("SELECT COUNT(*) FROM law_chunks"))
        chunks_with_emb = await session.execute(
            text("SELECT COUNT(*) FROM law_chunks WHERE embedding IS NOT NULL")
        )
        domains_result = await session.execute(
            text("""
                SELECT UNNEST(domains) AS d, COUNT(*)
                FROM law_chunks
                GROUP BY d
                ORDER BY COUNT(*) DESC
            """)
        )
        domain_rows = domains_result.all()

    return {
        "law_documents": docs.scalar(),
        "law_chunks": chunks.scalar(),
        "chunks_with_embeddings": chunks_with_emb.scalar(),
        "by_domain": {r[0]: r[1] for r in domain_rows},
    }
