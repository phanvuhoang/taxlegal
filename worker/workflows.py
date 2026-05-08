"""
Temporal workflow definitions for TaxLegal v4.
"""
from __future__ import annotations

import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

try:
    from temporalio import workflow
    from temporalio.common import RetryPolicy
    TEMPORAL_AVAILABLE = True
except ImportError:
    TEMPORAL_AVAILABLE = False
    logger.info("temporalio not installed — Temporal workflows disabled. Run: pip install temporalio")

    # Stub decorators so the class definition works without temporalio
    class workflow:  # noqa: N801
        @staticmethod
        def defn(cls):
            return cls

        @staticmethod
        def run(func):
            return func

        @staticmethod
        def signal(func):
            return func

        @staticmethod
        def query(func):
            return func

        # Stub for execute_activity — returns a coroutine that yields the fallback
        @staticmethod
        async def execute_activity(activity_fn, *args, **kwargs):
            if args:
                arg = args[0]
                case_id = getattr(arg, "case_id", str(arg)) if not isinstance(arg, str) else arg
            else:
                case_id = "unknown"
            return {"status": "completed", "case_id": case_id}

        @staticmethod
        async def wait_condition(condition_fn, *, timeout=None):
            pass


from worker.activities import (
    run_intake_activity,
    run_research_activity,
    run_draft_activity,
    run_sa_review_activity,
    run_partner_review_activity,
    await_human_approval_activity,
    run_delivery_activity,
    run_audit_archive_activity,
    IntakeInput,
    ResearchInput,
    ReviewInput,
    ApprovalInput,
)


# ── TaxAdvisoryWorkflow ────────────────────────────────────────────────────────

@workflow.defn
class TaxAdvisoryWorkflow:
    """
    Durable Temporal workflow for the full tax advisory pipeline.
    Handles retries, human approval signals, and rework loops.
    """

    def __init__(self):
        self._human_approval: str | None = None
        self._state: dict = {"current_node": "pending"}

    @workflow.signal
    async def submit_human_approval(self, decision: str) -> None:
        """
        Signal method — called via external API when a human approves or rejects.
        Accepted values: "approved" | "rejected"
        """
        self._human_approval = decision
        logger.info(f"[TaxAdvisoryWorkflow] Human approval signal received: {decision}")

    @workflow.query
    def get_current_state(self) -> dict:
        """Query method — return current workflow progress snapshot."""
        return self._state

    @workflow.run
    async def run(
        self,
        case_id: str,
        client_request: str,
        practice_area: str = "tax",
        output_language: str = "vi",
    ) -> dict:
        logger.info(f"[TaxAdvisoryWorkflow] Starting workflow for case {case_id}")

        # ── Step 1: Intake ─────────────────────────────────────────────────────
        self._state["current_node"] = "intake"
        intake_result = await workflow.execute_activity(
            run_intake_activity,
            IntakeInput(
                case_id=case_id,
                client_request=client_request,
                practice_area=practice_area,
                output_language=output_language,
            ),
            schedule_to_close_timeout=timedelta(minutes=10),
        ) if TEMPORAL_AVAILABLE else {"status": "completed"}

        # ── Step 2: Research ───────────────────────────────────────────────────
        self._state["current_node"] = "research"
        research_result = await workflow.execute_activity(
            run_research_activity,
            ResearchInput(
                case_id=case_id,
                verified_facts=intake_result.get("verified_facts", []),
                applicable_laws=intake_result.get("applicable_laws", []),
            ),
            schedule_to_close_timeout=timedelta(minutes=30),
        ) if TEMPORAL_AVAILABLE else {"status": "completed"}

        # ── Step 3: Draft ──────────────────────────────────────────────────────
        self._state["current_node"] = "draft"
        draft_result = await workflow.execute_activity(
            run_draft_activity,
            case_id,
            schedule_to_close_timeout=timedelta(minutes=15),
        ) if TEMPORAL_AVAILABLE else {"status": "completed"}

        # ── Step 4: SA Review ──────────────────────────────────────────────────
        self._state["current_node"] = "sa_review"
        sa_result = await workflow.execute_activity(
            run_sa_review_activity,
            ReviewInput(
                case_id=case_id,
                draft_content=draft_result.get("draft_content", ""),
                reviewer_role="sa",
            ),
            schedule_to_close_timeout=timedelta(minutes=10),
        ) if TEMPORAL_AVAILABLE else {"status": "completed"}

        # ── Step 5: Partner Review ─────────────────────────────────────────────
        self._state["current_node"] = "partner_review"
        partner_result = await workflow.execute_activity(
            run_partner_review_activity,
            ReviewInput(
                case_id=case_id,
                draft_content=draft_result.get("draft_content", ""),
                reviewer_role="partner",
            ),
            schedule_to_close_timeout=timedelta(minutes=10),
        ) if TEMPORAL_AVAILABLE else {"status": "completed"}

        # ── Step 6: Human Approval Gate (conditional) ──────────────────────────
        if partner_result.get("human_approval_required"):
            self._state["current_node"] = "human_gate"
            logger.info(f"[TaxAdvisoryWorkflow] Awaiting human approval for case {case_id}")

            if TEMPORAL_AVAILABLE:
                await workflow.wait_condition(
                    lambda: self._human_approval is not None,
                    timeout=timedelta(hours=48),
                )

            if self._human_approval == "rejected":
                self._state["current_node"] = "rejected"
                return {"status": "rejected", "case_id": case_id}

        # ── Step 7: Delivery ───────────────────────────────────────────────────
        self._state["current_node"] = "delivery"
        await workflow.execute_activity(
            run_delivery_activity,
            case_id,
            schedule_to_close_timeout=timedelta(minutes=5),
        ) if TEMPORAL_AVAILABLE else {"status": "completed"}

        # ── Step 8: Audit ──────────────────────────────────────────────────────
        self._state["current_node"] = "audit"
        await workflow.execute_activity(
            run_audit_archive_activity,
            case_id,
            schedule_to_close_timeout=timedelta(minutes=5),
        ) if TEMPORAL_AVAILABLE else {"status": "completed"}

        self._state["current_node"] = "completed"
        logger.info(f"[TaxAdvisoryWorkflow] Completed for case {case_id}")
        return {"status": "completed", "case_id": case_id}
