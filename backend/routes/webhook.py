"""
POST /internal/dbvntax-webhook

Receives document events from dbvntax (document.created, document.updated, document.deleted).
Verifies HMAC-SHA256 signature if DBVNTAX_WEBHOOK_SECRET is set.
Upserts documents into taxlegal.law_documents_v2.
"""
import hashlib
import hmac
import logging
import os
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["webhook"])

WEBHOOK_SECRET = os.getenv("DBVNTAX_WEBHOOK_SECRET", "")


def _verify_signature(body: bytes, sig_header: str) -> bool:
    if not WEBHOOK_SECRET:
        return True  # No secret configured — accept all
    expected = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig_header or "")


@router.post("/internal/dbvntax-webhook", status_code=200)
async def dbvntax_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    body = await request.body()
    sig = request.headers.get("X-Webhook-Signature", "")
    event = request.headers.get("X-Webhook-Event", "")

    if not _verify_signature(body, sig):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    import json
    try:
        payload = json.loads(body)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    doc = payload.get("data", payload)
    now = datetime.utcnow()

    if event in ("document.created", "document.updated"):
        # Upsert into law_documents_v2
        content_html = doc.get("noi_dung") or doc.get("html_source") or ""
        import re
        content_text = re.sub(r"<[^>]+>", " ", content_html)
        content_text = re.sub(r"\s+", " ", content_text).strip()

        try:
            await db.execute(text("""
                INSERT INTO taxlegal.law_documents_v2
                    (title, doc_number, doc_type, issuer, issued_date,
                     content_html, content_text, source_url,
                     imported_from, is_active, created_at, updated_at)
                VALUES
                    (:title, :doc_number, :doc_type, :issuer, :issued_date,
                     :content_html, :content_text, :source_url,
                     'dbvntax_webhook', TRUE, :now, :now)
                ON CONFLICT (source_url) DO UPDATE SET
                    title = EXCLUDED.title,
                    content_html = EXCLUDED.content_html,
                    content_text = EXCLUDED.content_text,
                    updated_at = EXCLUDED.updated_at
                WHERE taxlegal.law_documents_v2.source_url IS NOT NULL
            """), {
                "title": doc.get("ten") or doc.get("title") or "Untitled",
                "doc_number": doc.get("so_hieu") or doc.get("so_ky_hieu", ""),
                "doc_type": doc.get("loai") or doc.get("loai_vb", ""),
                "issuer": doc.get("co_quan_ban_hanh") or doc.get("co_quan_bh", ""),
                "issued_date": doc.get("ngay_ban_hanh"),
                "content_html": content_html,
                "content_text": content_text[:100000],
                "source_url": doc.get("source_url") or doc.get("tvpl_url"),
                "now": now,
            })
            await db.commit()
        except Exception as e:
            logger.error(f"webhook upsert failed: {e}")
            # Still return 200 so dbvntax doesn't retry

    elif event == "document.deleted":
        so_hieu = doc.get("so_hieu") or doc.get("so_ky_hieu")
        if so_hieu:
            try:
                await db.execute(
                    text("UPDATE taxlegal.law_documents_v2 SET is_active=FALSE WHERE doc_number=:sn"),
                    {"sn": so_hieu}
                )
                await db.commit()
            except Exception as e:
                logger.warning(f"webhook delete failed: {e}")

    return {"ok": True, "event": event}
