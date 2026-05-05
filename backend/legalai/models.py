"""
SQLAlchemy models for the LegalAI module.
All tables live in the 'public' schema of the 'legalai' database.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime, Integer, JSON, Date, Boolean,
    ForeignKey, func
)
from sqlalchemy.dialects.postgresql import UUID as pgUUID, ARRAY, TSVECTOR
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .database import LegalAIBase


class LawDocument(LegalAIBase):
    """Master law document record."""
    __tablename__ = "law_documents"

    id = Column(
        pgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    title = Column(Text, nullable=False)
    law_number = Column(Text, nullable=False)
    # luat | nghi_dinh | thong_tu | quyet_dinh | nghi_quyet | cong_van | other
    law_type = Column(String(50), nullable=True)
    issuer = Column(Text, nullable=False)
    issued_date = Column(Date, nullable=True)
    effective_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    # active | expired | amended | repealed
    status = Column(String(20), nullable=False, default="active", server_default="active")
    domains = Column(ARRAY(Text), nullable=True)  # e.g. ['thue', 'cit', 'vat']
    full_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    crawled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now(),
                        onupdate=func.now())

    # Relationship
    chunks = relationship("LawChunk", back_populates="law_document", cascade="all, delete-orphan")


class LawChunk(LegalAIBase):
    """Chunked paragraphs for RAG retrieval."""
    __tablename__ = "law_chunks"

    id = Column(
        pgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    law_id = Column(
        pgUUID(as_uuid=True),
        ForeignKey("law_documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    article = Column(Text, nullable=True)         # e.g. "Điều 5"
    clause = Column(Text, nullable=True)          # e.g. "Khoản 2"
    point = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    parent_context = Column(Text, nullable=True)  # article title/heading above chunk
    embedding = Column(Vector(1024), nullable=True)
    domains = Column(ARRAY(Text), nullable=True)
    keywords = Column(ARRAY(Text), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    tsv = Column(TSVECTOR, nullable=True)         # full-text search vector

    # Relationship
    law_document = relationship("LawDocument", back_populates="chunks")


class ChatSession(LegalAIBase):
    """Chat sessions for Legal Agent."""
    __tablename__ = "chat_sessions"

    id = Column(
        pgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    user_email = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    # qa | tax_research | compliance
    agent_type = Column(String(20), nullable=False, default="qa", server_default="qa")
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now(),
                        onupdate=func.now())

    # Relationship
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(LegalAIBase):
    """Messages within a chat session."""
    __tablename__ = "chat_messages"

    id = Column(
        pgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    session_id = Column(
        pgUUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    # user | assistant | system
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=False, default=list, server_default="[]")
    model = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())

    # Relationship
    session = relationship("ChatSession", back_populates="messages")


class LegalDocument(LegalAIBase):
    """User-uploaded documents (contracts, invoices, etc.)."""
    __tablename__ = "legal_documents"

    id = Column(
        pgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    user_email = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(Text, nullable=True)
    doc_type = Column(String(50), nullable=False, default="other", server_default="other")
    status = Column(String(20), nullable=False, default="uploaded", server_default="uploaded")
    extracted_text = Column(Text, nullable=True)
    analysis = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())


class CrawlJob(LegalAIBase):
    """Tracking records for crawl jobs."""
    __tablename__ = "crawl_jobs"

    id = Column(
        pgUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
    url = Column(Text, nullable=False)
    # pending | running | done | failed
    status = Column(String(20), nullable=False, default="pending", server_default="pending")
    result_count = Column(Integer, nullable=False, default=0, server_default="0")
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
