"""
WorkflowState TypedDict for TaxLegal v4 LangGraph workflow.
"""
from __future__ import annotations

import operator
from typing import Annotated, Optional

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


class WorkflowState(TypedDict, total=False):
    # Case identification
    case_id: str                    # UUID string
    matter_id: Optional[int]        # backward compat
    workflow_run_id: str            # UUID string

    # Input
    client_request: str
    title: str
    practice_area: str
    output_language: str            # "vi" or "en"

    # Pipeline state
    current_node: str
    completed_nodes: list[str]

    # Facts and laws
    verified_facts: list[dict]
    applicable_laws: list[dict]
    completeness_matrix: list[dict]
    missing_facts: list[str]        # triggers clarification loop
    clarification_iterations: int   # prevent infinite loops (max 2)

    # Research
    partner_brief: Optional[dict]
    sa_blueprint: Optional[dict]
    research_chunks: list[dict]

    # Drafts
    draft_opinion: Optional[str]
    draft_version: int

    # Reviews
    sa_decision: Optional[str]       # "approved" | "revision_required"
    sa_issues: list[dict]
    partner_decision: Optional[str]  # "approved" | "revision_required" | "escalate"
    partner_issues: list[dict]
    risk_score: float                # 0-10, above 7 triggers human approval

    # Human approval
    human_approval_required: bool
    human_approval_status: Optional[str]  # "pending" | "approved" | "rejected"

    # Retrieval tracking
    retrieval_queries: list[dict]
    citations: list[dict]
    used_fallback_search: bool
    has_insufficient_coverage: bool

    # Output
    final_output: Optional[str]
    quality_score: Optional[float]

    # Meta
    error: Optional[str]
    iterations: int                  # total node executions (safety counter)
    max_iterations: int              # default 50

    # Audit — append-only via operator.add
    audit_events: Annotated[list[dict], operator.add]
