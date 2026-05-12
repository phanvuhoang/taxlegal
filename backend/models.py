"""
SQLAlchemy models for taxlegal schema.
All tables live in the 'taxlegal' schema on the shared VPS PostgreSQL instance.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, SmallInteger, String, Text, Boolean, DateTime, Float,
    ForeignKey, ARRAY, func, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"

class MatterStatus(str, enum.Enum):
    draft = "draft"
    intake = "intake"
    partner_p1 = "partner_p1"
    sa_blueprint = "sa_blueprint"
    ja_research = "ja_research"
    sa_review = "sa_review"
    partner_p2 = "partner_p2"
    partner_p3 = "partner_p3"
    completed = "completed"
    failed = "failed"

class PipelineMode(str, enum.Enum):
    manual = "manual"   # user approves each step
    auto = "auto"       # runs automatically

class StepStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    waiting = "waiting"   # waiting for user approval
    approved = "approved"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"

class DepthLevel(str, enum.Enum):
    standard = "STANDARD"
    deep = "DEEP"

class FactStatus(str, enum.Enum):
    verified = "VERIFIED"
    client_stated = "CLIENT-STATED"
    unverified = "UNVERIFIED"
    conflicting = "CONFLICTING"


# ── Users ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String(200))
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    matters = relationship("Matter", back_populates="user", cascade="all, delete-orphan")


# ── Agent Settings (per agent model override) ─────────────────────────────────

class AgentSetting(Base):
    __tablename__ = "agent_settings"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    agent_key = Column(String(50), unique=True, nullable=False)  # intake|partner|sa|ja
    model_id = Column(String(200), nullable=False)
    provider = Column(String(50), nullable=False)  # anthropic|openai|deepseek|openrouter
    temperature = Column(Float, default=0.3)
    max_tokens = Column(Integer, default=8000)
    system_prompt_override = Column(Text)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("taxlegal.users.id"))


# ── Matters (client advisory requests) ───────────────────────────────────────

class Matter(Base):
    __tablename__ = "matters"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("taxlegal.users.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    client_request = Column(Text, nullable=False)   # raw client input
    practice_area = Column(String(100), default="tax")  # tax|legal|both
    pipeline_mode = Column(String(20), default="manual")
    status = Column(String(50), default="draft", index=True)
    current_step = Column(Integer, default=0)       # 0-7

    # Enriched data from Intake
    verified_facts = Column(JSONB, default=list)    # [{fact, status, sources}]
    applicable_laws = Column(JSONB, default=list)   # [{law_id, name, status, last_checked}]
    completeness_matrix = Column(JSONB, default=list)  # [{issue, depth, covered}]
    word_count_floor = Column(Integer, default=3000)

    # Partner brief
    partner_brief = Column(JSONB)

    # SA blueprint
    sa_blueprint = Column(JSONB)

    # Final output
    final_content = Column(Text)
    final_content_html = Column(Text)

    # Quality scores
    quality_score = Column(Float)
    reason_codes = Column(JSONB, default=list)     # [{"code": "R16", "severity": "CRITICAL", "step": "ja", "detail": "..."}]
    verification_chain_status = Column(String(50))  # COMPLETE|GAPS_FOUND

    # Meta
    model_used_intake = Column(String(200))
    model_used_partner = Column(String(200))
    model_used_sa = Column(String(200))
    model_used_ja = Column(String(200))
    total_tokens = Column(Integer, default=0)
    duration_ms = Column(Integer)
    is_sample = Column(Boolean, default=False)     # bài mẫu cho tham khảo
    pipeline_template_id = Column(Integer, ForeignKey("taxlegal.pipeline_templates.id"), nullable=True)
    bot_variant_overrides = Column(JSONB, default=dict)  # per-matter override map {step: bot_variant_slug}
    output_language = Column(String(2), default="vi")  # "vi" or "en"
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="matters")
    steps = relationship("PipelineStep", back_populates="matter", cascade="all, delete-orphan", order_by="PipelineStep.step_number")
    chunks = relationship("ResearchChunk", back_populates="matter", cascade="all, delete-orphan")


# ── Pipeline Steps ────────────────────────────────────────────────────────────

class PipelineStep(Base):
    __tablename__ = "pipeline_steps"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    matter_id = Column(Integer, ForeignKey("taxlegal.matters.id"), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)  # 1-7
    step_name = Column(String(100), nullable=False)  # e.g. "intake", "partner_p1", "sa_blueprint"...
    agent = Column(String(50), nullable=False)        # intake|partner|sa|ja
    status = Column(String(30), default="pending")
    model_used = Column(String(200))
    provider_used = Column(String(50))

    # Input/output
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    output_markdown = Column(Text)

    # Verification tables
    verified_facts = Column(JSONB, default=list)
    legal_verification = Column(JSONB, default=list)
    assertion_verification = Column(JSONB, default=list)

    # Quality
    reason_codes_found = Column(JSONB, default=list)
    word_count = Column(Integer)
    search_queries = Column(JSONB, default=list)   # web searches performed
    search_results_summary = Column(JSONB, default=list)

    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)

    # User interaction
    user_notes = Column(Text)      # notes when approving/rejecting
    approved_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey("taxlegal.users.id"))

    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    matter = relationship("Matter", back_populates="steps")


# ── Research Chunks (JA output) ───────────────────────────────────────────────

class ResearchChunk(Base):
    __tablename__ = "research_chunks"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    matter_id = Column(Integer, ForeignKey("taxlegal.matters.id"), nullable=False, index=True)
    chunk_number = Column(Integer, nullable=False)
    section_title = Column(String(500))
    depth_level = Column(String(20), default="STANDARD")  # DEEP|STANDARD
    content_markdown = Column(Text)

    # Phase outputs
    evidence_collected = Column(JSONB, default=list)   # Phase A
    practical_research = Column(JSONB, default=list)   # Phase B1
    legal_verification = Column(JSONB, default=list)   # Phase B2
    assertion_verification = Column(JSONB, default=list)  # Phase B2.5

    # Depth markers found
    depth_markers = Column(JSONB, default=list)  # [{"type": "PRACTICAL", "text": "..."}]
    depth_marker_count = Column(Integer, default=0)

    # Citations
    citations = Column(JSONB, default=list)  # [{law_id, article, status, sources}]

    word_count = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    matter = relationship("Matter", back_populates="chunks")


# ── Sample Advices (reference library) ───────────────────────────────────────

class SampleAdvice(Base):
    __tablename__ = "sample_advices"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    practice_area = Column(String(100), default="tax")
    tags = Column(ARRAY(Text), default=list)
    client_question = Column(Text)
    content_markdown = Column(Text, nullable=False)
    content_html = Column(Text)
    quality_score = Column(Float)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("taxlegal.users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ── AutoTest Cases ────────────────────────────────────────────────────────────

class AutoTestCase(Base):
    __tablename__ = "autotest_cases"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    description = Column(Text)
    client_request = Column(Text, nullable=False)
    practice_area = Column(String(100), default="tax")
    complexity = Column(String(20), default="standard")  # simple|standard|complex
    expected_topics = Column(JSONB, default=list)   # topics that MUST appear
    forbidden_topics = Column(JSONB, default=list)  # topics that must NOT appear
    scoring_criteria = Column(JSONB, default=dict)  # {practicality: 20, structure: 20, ...}
    baseline_score = Column(Float)
    baseline_locked_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    runs = relationship("AutoTestRun", back_populates="test_case", cascade="all, delete-orphan")


class AutoTestRun(Base):
    __tablename__ = "autotest_runs"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    test_case_id = Column(Integer, ForeignKey("taxlegal.autotest_cases.id"), nullable=False)
    matter_id = Column(Integer, ForeignKey("taxlegal.matters.id"))
    run_by = Column(Integer, ForeignKey("taxlegal.users.id"))
    score_total = Column(Float)
    score_breakdown = Column(JSONB, default=dict)
    reason_codes_triggered = Column(JSONB, default=list)
    delta_from_baseline = Column(Float)
    mutation_description = Column(Text)   # what changed from baseline
    passed = Column(Boolean)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    test_case = relationship("AutoTestCase", back_populates="runs")


# ── Law Documents (local cache / taxlegal-specific) ───────────────────────────

class LawDocument(Base):
    __tablename__ = "law_documents"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    so_hieu = Column(String(200), index=True)
    ten = Column(Text, nullable=False)
    loai = Column(String(20))        # Luat|ND|TT|VBHN|CV
    co_quan = Column(String(100))
    ngay_ban_hanh = Column(String(30))
    hieu_luc_tu = Column(String(30))
    het_hieu_luc_tu = Column(String(30))
    tinh_trang = Column(String(50), default="con_hieu_luc")
    replaced_by = Column(String(200))
    practice_areas = Column(ARRAY(Text), default=list)  # tax|labor|investment|...
    content_text = Column(Text)
    link_tvpl = Column(Text)
    dbvntax_id = Column(Integer)  # reference to dbvntax if synced
    source = Column(String(50), default="manual")  # manual|dbvntax_sync
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class LawDocumentV2(Base):
    __tablename__ = "law_documents_v2"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    doc_number = Column(String(200))
    doc_type = Column(String(50))
    issuer = Column(String(200))
    issued_date = Column(String(30))
    effective_date = Column(String(30))
    source_url = Column(Text)
    tags = Column(ARRAY(Text), default=list)
    tax_types = Column(ARRAY(Text), default=list)
    is_priority = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    ai_tagged = Column(Boolean, default=False)
    imported_from = Column(String(50))
    dbvntax_id = Column(Integer)
    content_html = Column(Text)
    content_text = Column(Text)
    effective_status = Column(String(50), default="con_hieu_luc")
    importance = Column(SmallInteger, default=4)
    created_by = Column(Integer, ForeignKey("taxlegal.users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ── Skills ────────────────────────────────────────────────────────────────────

class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)   # e.g. "tax-strategy"
    version = Column(String(20), default="1.0.0")
    description = Column(Text)
    category = Column(String(50), default="tax")   # tax|legal|advisory|compliance
    tags = Column(ARRAY(Text), default=list)        # ["cit", "transfer-pricing"]
    # Which bot roles this skill applies to (comma-separated or ARRAY)
    applicable_bots = Column(ARRAY(Text), default=list)  # ["partner", "ja", "sa", "intake"] or empty = all
    content_markdown = Column(Text, nullable=False)  # full .md content (body only, no frontmatter)
    frontmatter = Column(JSONB, default=dict)         # parsed YAML frontmatter as JSON
    is_active = Column(Boolean, default=True)
    is_builtin = Column(Boolean, default=False)       # True = seeded from repo /skills/ folder
    version_number = Column(Integer, default=1)        # v4: integer version counter
    parent_skill_id = Column(Integer, ForeignKey("taxlegal.skills.id"), nullable=True)  # v4: version chain
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("taxlegal.users.id"), nullable=True)


# ── BotVariants ───────────────────────────────────────────────────────────────

class BotVariant(Base):
    __tablename__ = "bot_variants"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)          # e.g. "JA-Advisory", "Partner-CIT"
    slug = Column(String(100), unique=True, nullable=False, index=True)  # e.g. "ja-advisory"
    role = Column(String(20), nullable=False)            # intake|partner|sa|ja
    description = Column(Text)
    system_prompt_base = Column(Text)                    # Override base system prompt (null = use default from prompts.py)
    skill_ids = Column(ARRAY(Integer), default=list)     # list of Skill.id assigned to this bot
    model_override = Column(String(200))                 # if set, override agent_settings model
    provider_override = Column(String(50))               # if set, override provider
    is_active = Column(Boolean, default=True)
    is_builtin = Column(Boolean, default=False)          # True = seeded defaults
    node_type = Column(String(50), default="agent")      # v4: workflow node type (agent/human_gate/condition/start/end)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ── PipelineTemplates ─────────────────────────────────────────────────────────

class PipelineTemplate(Base):
    __tablename__ = "pipeline_templates"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)           # e.g. "CIT Advisory", "VAT Compliance Check"
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    practice_area = Column(String(50), default="tax")    # tax|legal|both
    # Step configuration: maps step number (1-7) to BotVariant slug (or null = use default)
    step_config = Column(JSONB, default=dict)
    # Example:
    # {
    #   "1": {"bot_variant_slug": "intake-default", "label": "Intake Enhancer"},
    #   "2": {"bot_variant_slug": "partner-cit", "label": "Partner Brief (CIT)"},
    #   "4": {"bot_variant_slug": "ja-advisory", "label": "JA Research (Advisory)"},
    # }
    # Steps not in step_config use the system default for that step
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)          # Only one template can be default
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
