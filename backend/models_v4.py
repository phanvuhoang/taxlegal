"""
SQLAlchemy v4 models for TaxLegal v4 architecture upgrade.
All new tables live in the 'taxlegal' schema on the shared VPS PostgreSQL instance.
Uses UUID primary keys throughout.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float, DateTime, ForeignKey,
    func, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class CaseStatus(str, enum.Enum):
    draft = "draft"
    intake = "intake"
    researching = "researching"
    drafting = "drafting"
    sa_review = "sa_review"
    partner_review = "partner_review"
    human_approval = "human_approval"
    delivered = "delivered"
    archived = "archived"
    failed = "failed"


class WorkflowRunStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    paused = "paused"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class AgentRunStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


class SourceType(str, enum.Enum):
    internal_db = "internal_db"          # trusted taxlegal DB
    dbvntax = "dbvntax"                  # trusted tax law DB
    external_search = "external_search"  # fallback Perplexity
    user_uploaded = "user_uploaded"


class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    skipped = "skipped"


# ── Case ──────────────────────────────────────────────────────────────────────

class Case(Base):
    __tablename__ = "cases"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matter_id = Column(Integer, ForeignKey("taxlegal.matters.id"), nullable=True)  # backward compat
    title = Column(String(500), nullable=False)
    client_request = Column(Text, nullable=False)
    practice_area = Column(String(100), default="tax")
    status = Column(String(50), default="draft", index=True)
    workflow_definition_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.workflow_definitions.id"), nullable=True)
    current_node = Column(String(100), nullable=True)
    output_language = Column(String(2), default="vi")
    priority = Column(String(20), default="normal")  # low/normal/high/urgent
    metadata = Column(JSONB, default=dict)
    final_output = Column(Text, nullable=True)
    quality_score = Column(Float, nullable=True)
    created_by = Column(Integer, ForeignKey("taxlegal.users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("taxlegal.users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    events = relationship("CaseEvent", back_populates="case", cascade="all, delete-orphan")
    versions = relationship("CaseVersion", back_populates="case", cascade="all, delete-orphan")
    workflow_runs = relationship("WorkflowRun", back_populates="case")
    agent_runs = relationship("AgentRun", back_populates="case")
    draft_opinions = relationship("DraftOpinion", back_populates="case", cascade="all, delete-orphan")
    review_decisions = relationship("ReviewDecision", back_populates="case", cascade="all, delete-orphan")
    human_approvals = relationship("HumanApproval", back_populates="case", cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="case", cascade="all, delete-orphan")
    retrieval_queries = relationship("RetrievalQuery", back_populates="case", cascade="all, delete-orphan")


# ── CaseEvent ─────────────────────────────────────────────────────────────────

class CaseEvent(Base):
    __tablename__ = "case_events"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.cases.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)  # node_started, node_completed, human_approval_requested, etc.
    node_name = Column(String(100), nullable=True)
    actor = Column(String(100), nullable=True)  # bot slug or user email
    data = Column(JSONB, default=dict)
    created_at = Column(DateTime, server_default=func.now())

    case = relationship("Case", back_populates="events")


# ── CaseVersion ───────────────────────────────────────────────────────────────

class CaseVersion(Base):
    __tablename__ = "case_versions"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.cases.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    snapshot = Column(JSONB, nullable=False)  # full case state snapshot
    change_summary = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("taxlegal.users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    case = relationship("Case", back_populates="versions")


# ── WorkflowDefinition ────────────────────────────────────────────────────────

class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    practice_area = Column(String(50), default="tax")
    graph_definition = Column(JSONB, nullable=False, default=dict)  # stores nodes, edges, conditions
    entry_node = Column(String(100), nullable=True)
    metadata = Column(JSONB, default=dict)
    created_by = Column(Integer, ForeignKey("taxlegal.users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    nodes = relationship("WorkflowNode", back_populates="workflow_definition", cascade="all, delete-orphan")
    edges = relationship("WorkflowEdge", back_populates="workflow_definition", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="workflow_definition", foreign_keys=[Case.workflow_definition_id])
    workflow_runs = relationship("WorkflowRun", back_populates="workflow_definition")
    approval_policies = relationship("ApprovalPolicy", back_populates="workflow_definition")


# Back-reference fix for Case.workflow_definition
Case.workflow_definition = relationship("WorkflowDefinition", back_populates="cases", foreign_keys=[Case.workflow_definition_id])


# ── WorkflowNode ──────────────────────────────────────────────────────────────

class WorkflowNode(Base):
    __tablename__ = "workflow_nodes"
    __table_args__ = (
        UniqueConstraint("workflow_id", "node_id", name="uq_workflow_node"),
        {"schema": "taxlegal"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.workflow_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(String(100), nullable=False)  # logical node name like "intake", "research"
    node_type = Column(String(50), default="agent")  # agent/human_gate/condition/start/end
    label = Column(String(200), nullable=True)
    bot_definition_id = Column(Integer, ForeignKey("taxlegal.bot_variants.id"), nullable=True)
    skill_ids = Column(JSONB, default=list)
    config = Column(JSONB, default=dict)  # timeout, retries, conditions, branching rules
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    workflow_definition = relationship("WorkflowDefinition", back_populates="nodes")


# ── WorkflowEdge ──────────────────────────────────────────────────────────────

class WorkflowEdge(Base):
    __tablename__ = "workflow_edges"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.workflow_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    from_node = Column(String(100), nullable=False)
    to_node = Column(String(100), nullable=False)
    condition = Column(String(200), nullable=True)  # "missing_facts", "sa_approved", "high_risk", "default"
    label = Column(String(200), nullable=True)
    metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime, server_default=func.now())

    workflow_definition = relationship("WorkflowDefinition", back_populates="edges")


# ── WorkflowRun ───────────────────────────────────────────────────────────────

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.cases.id"), nullable=False, index=True)
    workflow_definition_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.workflow_definitions.id"), nullable=False)
    workflow_version = Column(Integer, default=1)
    status = Column(String(50), default="pending", index=True)
    current_node = Column(String(100), nullable=True)
    state = Column(JSONB, default=dict)  # full LangGraph state snapshot
    temporal_workflow_id = Column(String(200), nullable=True)
    temporal_run_id = Column(String(200), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    case = relationship("Case", back_populates="workflow_runs")
    workflow_definition = relationship("WorkflowDefinition", back_populates="workflow_runs")
    agent_runs = relationship("AgentRun", back_populates="workflow_run", cascade="all, delete-orphan")
    human_approvals = relationship("HumanApproval", back_populates="workflow_run")
    task_states = relationship("TaskState", back_populates="workflow_run", cascade="all, delete-orphan")


# ── AgentRun ──────────────────────────────────────────────────────────────────

class AgentRun(Base):
    __tablename__ = "agent_runs"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.workflow_runs.id"), nullable=False, index=True)
    case_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.cases.id"), nullable=False, index=True)
    node_name = Column(String(100), nullable=False)
    bot_variant_slug = Column(String(100), nullable=True)
    model_used = Column(String(200), nullable=True)
    provider_used = Column(String(50), nullable=True)
    status = Column(String(50), default="pending", index=True)
    input_state = Column(JSONB, default=dict)
    output_state = Column(JSONB, default=dict)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    retrieval_queries = Column(JSONB, default=list)  # list of RetrievalQuery records
    citations_used = Column(JSONB, default=list)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    workflow_run = relationship("WorkflowRun", back_populates="agent_runs")
    case = relationship("Case", back_populates="agent_runs")
    draft_opinions = relationship("DraftOpinion", back_populates="agent_run")
    review_decisions = relationship("ReviewDecision", back_populates="agent_run")
    citations = relationship("Citation", back_populates="agent_run")
    retrieval_query_records = relationship("RetrievalQuery", back_populates="agent_run")


# ── SkillVersion ──────────────────────────────────────────────────────────────

class SkillVersion(Base):
    __tablename__ = "skill_versions"
    __table_args__ = (
        UniqueConstraint("skill_id", "version_number", name="uq_skill_version"),
        {"schema": "taxlegal"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_id = Column(Integer, ForeignKey("taxlegal.skills.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    content_markdown = Column(Text, nullable=False)
    change_notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("taxlegal.users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# ── BotSkillAssignment ────────────────────────────────────────────────────────

class BotSkillAssignment(Base):
    __tablename__ = "bot_skill_assignments"
    __table_args__ = (
        UniqueConstraint("bot_variant_id", "skill_id", name="uq_bot_skill"),
        {"schema": "taxlegal"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot_variant_id = Column(Integer, ForeignKey("taxlegal.bot_variants.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("taxlegal.skills.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_version = Column(Integer, nullable=True)  # null = always use latest
    is_active = Column(Boolean, default=True)
    assigned_at = Column(DateTime, server_default=func.now())
    assigned_by = Column(Integer, ForeignKey("taxlegal.users.id"), nullable=True)


# ── DraftOpinion ──────────────────────────────────────────────────────────────

class DraftOpinion(Base):
    __tablename__ = "draft_opinions"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.cases.id"), nullable=False, index=True)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.agent_runs.id"), nullable=True)
    version_number = Column(Integer, default=1)
    content_markdown = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)
    word_count = Column(Integer, nullable=True)
    citations = Column(JSONB, default=list)
    assumptions = Column(JSONB, default=list)
    open_questions = Column(JSONB, default=list)
    source_coverage_score = Column(Float, nullable=True)
    has_insufficient_coverage = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    case = relationship("Case", back_populates="draft_opinions")
    agent_run = relationship("AgentRun", back_populates="draft_opinions")


# ── ReviewDecision ────────────────────────────────────────────────────────────

class ReviewDecision(Base):
    __tablename__ = "review_decisions"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.cases.id"), nullable=False, index=True)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.agent_runs.id"), nullable=True)
    reviewer_role = Column(String(50), nullable=True)  # sa/partner/human
    reviewer_id = Column(Integer, ForeignKey("taxlegal.users.id"), nullable=True)
    decision = Column(String(50), nullable=True)  # approved/rejected/revision_required
    technical_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    issues_found = Column(JSONB, default=list)
    corrections_required = Column(JSONB, default=list)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    case = relationship("Case", back_populates="review_decisions")
    agent_run = relationship("AgentRun", back_populates="review_decisions")


# ── HumanApproval ─────────────────────────────────────────────────────────────

class HumanApproval(Base):
    __tablename__ = "human_approvals"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.cases.id"), nullable=False, index=True)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.workflow_runs.id"), nullable=True)
    requested_by = Column(String(100), nullable=True)  # bot slug
    reason = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending/approved/rejected/skipped
    approved_by = Column(Integer, ForeignKey("taxlegal.users.id"), nullable=True)
    decision_notes = Column(Text, nullable=True)
    requested_at = Column(DateTime, server_default=func.now())
    decided_at = Column(DateTime, nullable=True)

    case = relationship("Case", back_populates="human_approvals")
    workflow_run = relationship("WorkflowRun", back_populates="human_approvals")


# ── Citation ──────────────────────────────────────────────────────────────────

class Citation(Base):
    __tablename__ = "citations"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.cases.id"), nullable=False, index=True)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.agent_runs.id"), nullable=True)
    source_type = Column(String(50), nullable=True)  # internal_db/dbvntax/external_search/user_uploaded
    trust_level = Column(String(20), default="high")  # high/medium/low/unverified
    law_identifier = Column(String(300), nullable=True)  # e.g. "TT 80/2021/TT-BTC"
    article_reference = Column(String(300), nullable=True)
    excerpt_text = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    retrieval_method = Column(String(100), nullable=True)  # db_query/vector_search/web_search
    relevance_score = Column(Float, nullable=True)
    is_verified = Column(Boolean, default=False)
    metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime, server_default=func.now())

    case = relationship("Case", back_populates="citations")
    agent_run = relationship("AgentRun", back_populates="citations")


# ── RetrievalQuery ────────────────────────────────────────────────────────────

class RetrievalQuery(Base):
    __tablename__ = "retrieval_queries"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.cases.id"), nullable=True, index=True)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.agent_runs.id"), nullable=True, index=True)
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50), nullable=True)  # law_lookup/fact_check/general
    db_results_count = Column(Integer, default=0)
    used_fallback = Column(Boolean, default=False)
    fallback_reason = Column(Text, nullable=True)
    insufficient_coverage = Column(Boolean, default=False)
    results_summary = Column(JSONB, default=dict)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    case = relationship("Case", back_populates="retrieval_queries")
    agent_run = relationship("AgentRun", back_populates="retrieval_query_records")


# ── ApprovalPolicy ────────────────────────────────────────────────────────────

class ApprovalPolicy(Base):
    __tablename__ = "approval_policies"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    workflow_definition_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.workflow_definitions.id"), nullable=True)
    trigger_conditions = Column(JSONB, nullable=False)  # e.g. {"risk_score_above": 7, "practice_area": "tax"}
    required_approvers = Column(JSONB, default=list)    # roles/users required
    timeout_hours = Column(Integer, default=48)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    workflow_definition = relationship("WorkflowDefinition", back_populates="approval_policies")


# ── TaskState ─────────────────────────────────────────────────────────────────
# For Redis-less durability fallback

class TaskState(Base):
    __tablename__ = "task_states"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("taxlegal.workflow_runs.id"), nullable=False, index=True)
    task_key = Column(String(200), nullable=False, unique=True)
    state_data = Column(JSONB, default=dict)
    expires_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    workflow_run = relationship("WorkflowRun", back_populates="task_states")
