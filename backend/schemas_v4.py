"""
Pydantic v2 schemas for TaxLegal v4 architecture.
All schemas use model_config = ConfigDict(from_attributes=True) for ORM compatibility.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


# ── Case ──────────────────────────────────────────────────────────────────────

class CaseCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., max_length=500)
    client_request: str
    practice_area: str = "tax"
    status: str = "draft"
    workflow_definition_id: Optional[uuid.UUID] = None
    output_language: str = "vi"
    priority: str = "normal"
    matter_id: Optional[int] = None
    assigned_to: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    matter_id: Optional[int] = None
    title: str
    client_request: str
    practice_area: str
    status: str
    workflow_definition_id: Optional[uuid.UUID] = None
    current_node: Optional[str] = None
    output_language: str
    priority: str
    metadata: dict[str, Any]
    final_output: Optional[str] = None
    quality_score: Optional[float] = None
    created_by: int
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class CaseUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = Field(None, max_length=500)
    client_request: Optional[str] = None
    practice_area: Optional[str] = None
    status: Optional[str] = None
    workflow_definition_id: Optional[uuid.UUID] = None
    current_node: Optional[str] = None
    output_language: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    metadata: Optional[dict[str, Any]] = None
    final_output: Optional[str] = None
    quality_score: Optional[float] = None


# ── WorkflowDefinition ────────────────────────────────────────────────────────

class WorkflowDefinitionCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None
    version: int = 1
    is_active: bool = True
    is_default: bool = False
    practice_area: str = "tax"
    graph_definition: dict[str, Any] = Field(default_factory=dict)
    entry_node: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowDefinitionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    version: int
    is_active: bool
    is_default: bool
    practice_area: str
    graph_definition: dict[str, Any]
    entry_node: Optional[str] = None
    metadata: dict[str, Any]
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class WorkflowDefinitionUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    version: Optional[int] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    practice_area: Optional[str] = None
    graph_definition: Optional[dict[str, Any]] = None
    entry_node: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


# ── WorkflowNode ──────────────────────────────────────────────────────────────

class WorkflowNodeCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workflow_id: uuid.UUID
    node_id: str = Field(..., max_length=100)
    node_type: str = "agent"  # agent/human_gate/condition/start/end
    label: Optional[str] = Field(None, max_length=200)
    bot_definition_id: Optional[int] = None
    skill_ids: list[Any] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)
    position_x: Optional[float] = None
    position_y: Optional[float] = None


class WorkflowNodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workflow_id: uuid.UUID
    node_id: str
    node_type: str
    label: Optional[str] = None
    bot_definition_id: Optional[int] = None
    skill_ids: list[Any]
    config: dict[str, Any]
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    created_at: datetime


# ── WorkflowEdge ──────────────────────────────────────────────────────────────

class WorkflowEdgeCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workflow_id: uuid.UUID
    from_node: str = Field(..., max_length=100)
    to_node: str = Field(..., max_length=100)
    condition: Optional[str] = Field(None, max_length=200)
    label: Optional[str] = Field(None, max_length=200)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowEdgeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workflow_id: uuid.UUID
    from_node: str
    to_node: str
    condition: Optional[str] = None
    label: Optional[str] = None
    metadata: dict[str, Any]
    created_at: datetime


# ── WorkflowRun ───────────────────────────────────────────────────────────────

class WorkflowRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    workflow_definition_id: uuid.UUID
    workflow_version: int
    status: str
    current_node: Optional[str] = None
    state: dict[str, Any]
    temporal_workflow_id: Optional[str] = None
    temporal_run_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime


# ── AgentRun ──────────────────────────────────────────────────────────────────

class AgentRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workflow_run_id: uuid.UUID
    case_id: uuid.UUID
    node_name: str
    bot_variant_slug: Optional[str] = None
    model_used: Optional[str] = None
    provider_used: Optional[str] = None
    status: str
    input_state: dict[str, Any]
    output_state: dict[str, Any]
    prompt_tokens: int
    completion_tokens: int
    retrieval_queries: list[Any]
    citations_used: list[Any]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime


# ── SkillVersion ──────────────────────────────────────────────────────────────

class SkillVersionCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: int
    version_number: int
    content_markdown: str
    change_notes: Optional[str] = None


class SkillVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    skill_id: int
    version_number: int
    content_markdown: str
    change_notes: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime


# ── HumanApproval ─────────────────────────────────────────────────────────────

class HumanApprovalCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: uuid.UUID
    workflow_run_id: Optional[uuid.UUID] = None
    requested_by: Optional[str] = Field(None, max_length=100)  # bot slug
    reason: Optional[str] = None


class HumanApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    workflow_run_id: Optional[uuid.UUID] = None
    requested_by: Optional[str] = None
    reason: Optional[str] = None
    status: str
    approved_by: Optional[int] = None
    decision_notes: Optional[str] = None
    requested_at: datetime
    decided_at: Optional[datetime] = None


class HumanApprovalDecision(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str  # approved/rejected/skipped
    decision_notes: Optional[str] = None
    approved_by: Optional[int] = None


# ── ReviewDecision ────────────────────────────────────────────────────────────

class ReviewDecisionCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: uuid.UUID
    agent_run_id: Optional[uuid.UUID] = None
    reviewer_role: Optional[str] = Field(None, max_length=50)  # sa/partner/human
    reviewer_id: Optional[int] = None
    decision: Optional[str] = Field(None, max_length=50)  # approved/rejected/revision_required
    technical_score: Optional[float] = None
    risk_score: Optional[float] = None
    issues_found: list[Any] = Field(default_factory=list)
    corrections_required: list[Any] = Field(default_factory=list)
    notes: Optional[str] = None


class ReviewDecisionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    agent_run_id: Optional[uuid.UUID] = None
    reviewer_role: Optional[str] = None
    reviewer_id: Optional[int] = None
    decision: Optional[str] = None
    technical_score: Optional[float] = None
    risk_score: Optional[float] = None
    issues_found: list[Any]
    corrections_required: list[Any]
    notes: Optional[str] = None
    created_at: datetime


# ── Citation ──────────────────────────────────────────────────────────────────

class CitationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    agent_run_id: Optional[uuid.UUID] = None
    source_type: Optional[str] = None  # internal_db/dbvntax/external_search/user_uploaded
    trust_level: str
    law_identifier: Optional[str] = None
    article_reference: Optional[str] = None
    excerpt_text: Optional[str] = None
    source_url: Optional[str] = None
    retrieval_method: Optional[str] = None
    relevance_score: Optional[float] = None
    is_verified: bool
    metadata: dict[str, Any]
    created_at: datetime


# ── RetrievalQuery ────────────────────────────────────────────────────────────

class RetrievalQueryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: Optional[uuid.UUID] = None
    agent_run_id: Optional[uuid.UUID] = None
    query_text: str
    query_type: Optional[str] = None
    db_results_count: int
    used_fallback: bool
    fallback_reason: Optional[str] = None
    insufficient_coverage: bool
    results_summary: dict[str, Any]
    duration_ms: Optional[int] = None
    created_at: datetime


# ── Composite / Response Schemas ──────────────────────────────────────────────

class WorkflowValidationResult(BaseModel):
    """Result of validating a workflow definition graph."""
    model_config = ConfigDict(from_attributes=True)

    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CaseFinalOutput(BaseModel):
    """Represents the final delivered output of a completed case."""
    model_config = ConfigDict(from_attributes=True)

    case_id: uuid.UUID
    final_content: str
    citations: list[CitationRead] = Field(default_factory=list)
    quality_score: Optional[float] = None
    retrieval_summary: dict[str, Any] = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    """Result returned from a retrieval operation."""
    model_config = ConfigDict(from_attributes=True)

    query: str
    db_results: list[Any] = Field(default_factory=list)
    used_fallback: bool = False
    insufficient_coverage: bool = False
    citations: list[CitationRead] = Field(default_factory=list)
    answer: str = ""


# ── DraftOpinion ──────────────────────────────────────────────────────────────

class DraftOpinionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    agent_run_id: Optional[uuid.UUID] = None
    version_number: int
    content_markdown: str
    content_html: Optional[str] = None
    word_count: Optional[int] = None
    citations: list[Any]
    assumptions: list[Any]
    open_questions: list[Any]
    source_coverage_score: Optional[float] = None
    has_insufficient_coverage: bool
    created_at: datetime


# ── BotSkillAssignment ────────────────────────────────────────────────────────

class BotSkillAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    bot_variant_id: int
    skill_id: int
    skill_version: Optional[int] = None
    is_active: bool
    assigned_at: datetime
    assigned_by: Optional[int] = None


class BotSkillAssignmentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bot_variant_id: int
    skill_id: int
    skill_version: Optional[int] = None
    is_active: bool = True


# ── ApprovalPolicy ────────────────────────────────────────────────────────────

class ApprovalPolicyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    workflow_definition_id: Optional[uuid.UUID] = None
    trigger_conditions: dict[str, Any]
    required_approvers: list[Any]
    timeout_hours: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ApprovalPolicyCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., max_length=200)
    workflow_definition_id: Optional[uuid.UUID] = None
    trigger_conditions: dict[str, Any]
    required_approvers: list[Any] = Field(default_factory=list)
    timeout_hours: int = 48
    is_active: bool = True


# ── CaseEvent ─────────────────────────────────────────────────────────────────

class CaseEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    event_type: str
    node_name: Optional[str] = None
    actor: Optional[str] = None
    data: dict[str, Any]
    created_at: datetime


# ── CaseVersion ───────────────────────────────────────────────────────────────

class CaseVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    version_number: int
    snapshot: dict[str, Any]
    change_summary: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
