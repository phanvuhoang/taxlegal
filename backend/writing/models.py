"""
Writing module SQLAlchemy models — uses taxlegal schema.
Tables: writing_jobs, writing_sections, priority_docs, sample_writings
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMPTZ
from sqlalchemy.sql import func
from backend.models import Base


class WritingJob(Base):
    __tablename__ = "writing_jobs"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    content_type = Column(String(50), default="analysis")  # analysis, advisory, press, scenario
    topic = Column(Text, nullable=False)
    context = Column(Text)
    output_language = Column(String(2), default="vi")  # vi or en
    bot_variant_id = Column(Integer)
    skill_ids = Column(ARRAY(Integer), default=[])
    status = Column(String(50), default="draft")  # draft, generating, done, error
    word_count_target = Column(Integer, default=2000)
    sections = Column(JSON, default=[])
    final_content = Column(Text)
    docx_path = Column(String(500))
    gamma_url = Column(String(500))
    review_bot_variant_id = Column(Integer)
    review_content = Column(Text)
    review_status = Column(String(50), default="none")  # none|pending|reviewing|done|error
    created_by = Column(Integer, ForeignKey("taxlegal.users.id"))
    created_at = Column(TIMESTAMPTZ, server_default=func.now())
    updated_at = Column(TIMESTAMPTZ, server_default=func.now(), onupdate=func.now())


class WritingSection(Base):
    __tablename__ = "writing_sections"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("taxlegal.writing_jobs.id", ondelete="CASCADE"), nullable=False)
    section_order = Column(Integer, nullable=False)
    section_title = Column(String(300))
    prompt = Column(Text)
    content = Column(Text)
    token_count = Column(Integer)
    status = Column(String(50), default="pending")
    created_at = Column(TIMESTAMPTZ, server_default=func.now())
    updated_at = Column(TIMESTAMPTZ, server_default=func.now(), onupdate=func.now())


class PriorityDoc(Base):
    __tablename__ = "priority_docs"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    doc_type = Column(String(100))  # law, decree, circular, official_letter, treaty
    source_url = Column(String(1000))
    content = Column(Text, nullable=False)
    priority_level = Column(Integer, default=1)  # 1=highest priority
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("taxlegal.users.id"))
    created_at = Column(TIMESTAMPTZ, server_default=func.now())
    updated_at = Column(TIMESTAMPTZ, server_default=func.now(), onupdate=func.now())


class SampleWriting(Base):
    __tablename__ = "sample_writings"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    content_type = Column(String(50))
    language = Column(String(2), default="vi")
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(String), default=[])
    is_active = Column(Boolean, default=True)
    category = Column(String(100))
    topic = Column(String(300))
    created_by = Column(Integer, ForeignKey("taxlegal.users.id"))
    created_at = Column(TIMESTAMPTZ, server_default=func.now())
