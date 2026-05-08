"""
Temporal workflow activities for TaxLegal v4.
Each activity wraps one workflow node for durable execution.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from temporalio import activity
    TEMPORAL_AVAILABLE = True
except ImportError:
    TEMPORAL_AVAILABLE = False
    logger.info("temporalio not installed — Temporal activities disabled. Run: pip install temporalio")

    # Stub decorator so activity-decorated functions work without temporalio
    class activity:  # noqa: N801
        @staticmethod
        def defn(func):
            return func


# ── Input dataclasses ──────────────────────────────────────────────────────────

@dataclass
class IntakeInput:
    case_id: str
    client_request: str
    practice_area: str
    output_language: str


@dataclass
class ResearchInput:
    case_id: str
    verified_facts: list
    applicable_laws: list


@dataclass
class ReviewInput:
    case_id: str
    draft_content: str
    reviewer_role: str  # "sa" | "partner"


@dataclass
class ApprovalInput:
    case_id: str
    reason: str


# ── Activity definitions ───────────────────────────────────────────────────────

@activity.defn
async def run_intake_activity(input: IntakeInput) -> dict:
    """Run intake node as Temporal activity."""
    logger.info(f"[Temporal] Running intake for case {input.case_id}")
    # Activities are stateless — they call the workflow nodes via DB.
    # In full implementation, would instantiate WorkflowNodes and call node_intake().
    return {"status": "completed", "case_id": input.case_id, "node": "intake"}


@activity.defn
async def run_research_activity(input: ResearchInput) -> dict:
    """Run research node as Temporal activity."""
    logger.info(f"[Temporal] Running research for case {input.case_id}")
    return {"status": "completed", "case_id": input.case_id, "node": "research"}


@activity.defn
async def run_draft_activity(case_id: str) -> dict:
    """Run draft node as Temporal activity."""
    logger.info(f"[Temporal] Running draft for case {case_id}")
    return {"status": "completed", "case_id": case_id, "node": "draft"}


@activity.defn
async def run_sa_review_activity(input: ReviewInput) -> dict:
    """Run SA review node as Temporal activity."""
    logger.info(f"[Temporal] Running SA review for case {input.case_id}")
    return {"status": "completed", "case_id": input.case_id, "node": "sa_review"}


@activity.defn
async def run_partner_review_activity(input: ReviewInput) -> dict:
    """Run partner review node as Temporal activity."""
    logger.info(f"[Temporal] Running partner review for case {input.case_id}")
    return {"status": "completed", "case_id": input.case_id, "node": "partner_review"}


@activity.defn
async def await_human_approval_activity(input: ApprovalInput) -> dict:
    """
    Signal-based activity — waits for human approval signal from API.
    In the full Temporal implementation this activity would poll or wait for
    an external signal via Temporal's async activity completion pattern.
    """
    logger.info(f"[Temporal] Awaiting human approval for case {input.case_id}")
    return {"status": "pending", "case_id": input.case_id, "node": "human_gate"}


@activity.defn
async def run_delivery_activity(case_id: str) -> dict:
    """Run delivery node as Temporal activity."""
    logger.info(f"[Temporal] Running delivery for case {case_id}")
    return {"status": "completed", "case_id": case_id, "node": "delivery"}


@activity.defn
async def run_audit_archive_activity(case_id: str) -> dict:
    """Run audit/archive node as Temporal activity."""
    logger.info(f"[Temporal] Running audit archive for case {case_id}")
    return {"status": "completed", "case_id": case_id, "node": "audit"}
