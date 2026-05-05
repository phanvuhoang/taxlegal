"""
Document upload and management endpoints.
"""
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy import text
from backend.auth import get_current_user
from backend.legalai.database import LegalAISession
from backend.legalai.document_processor import save_upload, extract_text, UPLOAD_DIR

router = APIRouter(prefix="/api/legalai/documents", tags=["Legal Documents"])

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "application/msword",
}
MAX_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    """Upload a document (PDF/DOCX/TXT) for storage and text extraction."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type not supported: {file.content_type}")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(413, "File too large (max 20 MB)")

    # Persist file to disk
    rel_path, size = save_upload(content, file.filename or "document", current_user.email)
    full_path = UPLOAD_DIR / rel_path

    # Extract text
    extracted_text, page_count = extract_text(full_path, file.content_type or "")

    # Store record in DB
    doc_id = str(uuid.uuid4())
    async with LegalAISession() as session:
        await session.execute(
            text("""
                INSERT INTO legal_documents
                    (id, user_email, name, file_path, file_size, mime_type,
                     doc_type, status, extracted_text)
                VALUES
                    (:id, :email, :name, :path, :size, :mime,
                     'other', 'uploaded', :text)
            """),
            {
                "id": doc_id,
                "email": current_user.email,
                "name": file.filename,
                "path": rel_path,
                "size": size,
                "mime": file.content_type,
                "text": extracted_text[:100000] if extracted_text else None,
            },
        )
        await session.commit()

    return {
        "document_id": doc_id,
        "name": file.filename,
        "size": size,
        "pages": page_count,
        "text_extracted": bool(extracted_text),
        "text_length": len(extracted_text) if extracted_text else 0,
    }


@router.get("")
async def list_documents(
    limit: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
):
    """List documents uploaded by the current user."""
    async with LegalAISession() as session:
        result = await session.execute(
            text("""
                SELECT id, name, file_size, mime_type, doc_type, status, created_at
                FROM legal_documents
                WHERE user_email = :email
                ORDER BY created_at DESC
                LIMIT :limit
            """),
            {"email": current_user.email, "limit": limit},
        )
        rows = result.mappings().all()
    return {"documents": [dict(r) for r in rows]}


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, current_user=Depends(get_current_user)):
    """Delete a document (user must own it)."""
    async with LegalAISession() as session:
        result = await session.execute(
            text("""
                DELETE FROM legal_documents
                WHERE id = :id AND user_email = :email
                RETURNING id, file_path
            """),
            {"id": doc_id, "email": current_user.email},
        )
        row = result.fetchone()
        if not row:
            raise HTTPException(404, "Document not found")

        # Best-effort file removal
        try:
            file_path = UPLOAD_DIR / row[1]
            if file_path.exists():
                file_path.unlink()
        except Exception:
            pass

        await session.commit()
    return {"deleted": True}
