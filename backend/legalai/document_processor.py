"""
Document processor — extract text from PDF/DOCX uploads.
"""
import os
import uuid
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/taxlegal-uploads"))
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


def extract_text_from_pdf(file_path: Path) -> tuple[str, int]:
    """Extract text from a PDF file. Returns (text, page_count)."""
    try:
        import pypdf

        reader = pypdf.PdfReader(str(file_path))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages), len(reader.pages)
    except ImportError:
        logger.warning("pypdf not installed — PDF extraction unavailable")
        return "", 0
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return "", 0


def extract_text_from_docx(file_path: Path) -> str:
    """Extract text from a DOCX file."""
    try:
        import docx

        doc = docx.Document(str(file_path))
        return "\n".join([para.text for para in doc.paragraphs if para.text])
    except ImportError:
        logger.warning("python-docx not installed — DOCX extraction unavailable")
        return ""
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return ""


def save_upload(content: bytes, filename: str, user_email: str) -> tuple[str, int]:
    """
    Save an uploaded file to disk.
    Returns (relative_path_from_UPLOAD_DIR, file_size_bytes).
    """
    safe_email = user_email.replace("@", "_").replace(".", "_")
    user_dir = UPLOAD_DIR / safe_email
    user_dir.mkdir(exist_ok=True, parents=True)

    unique_name = f"{uuid.uuid4().hex}_{filename[-50:]}"
    file_path = user_dir / unique_name

    with open(file_path, "wb") as f:
        f.write(content)

    return str(file_path.relative_to(UPLOAD_DIR)), len(content)


def extract_text(file_path: Path, mime_type: str) -> tuple[str, int]:
    """
    Dispatch text extraction based on mime type.
    Returns (extracted_text, page_count).  page_count is 0 for non-PDF types.
    """
    if "pdf" in mime_type:
        return extract_text_from_pdf(file_path)
    elif "word" in mime_type or str(file_path).endswith(".docx"):
        return extract_text_from_docx(file_path), 0
    elif "text" in mime_type:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(), 0
        except Exception as e:
            logger.error(f"Plain-text read error: {e}")
            return "", 0
    return "", 0
