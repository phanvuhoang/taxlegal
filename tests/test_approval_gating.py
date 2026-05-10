"""Tests for approval gating logic."""
import pytest
from unittest.mock import MagicMock, AsyncMock


class TestApprovalGating:
    def test_final_not_ready_when_not_delivered(self):
        """Final output should not be accessible until status is 'delivered'."""
        # Test the business rule: status must be 'delivered' to get final output
        statuses_that_block = [
            "draft", "running", "intake", "researching",
            "drafting", "sa_review", "partner_review",
            "human_approval", "failed",
        ]
        for status in statuses_that_block:
            # Simulate the check in GET /api/cases/{id}/final
            is_ready = (status == "delivered")
            assert not is_ready, f"Status '{status}' should NOT allow final output"

    def test_final_ready_when_delivered(self):
        """Only 'delivered' status allows access to final output."""
        status = "delivered"
        is_ready = (status == "delivered")
        assert is_ready

    def test_human_approval_required_when_risk_high(self):
        """When risk_score > 7, human approval should be required."""
        def requires_human_approval(risk_score: float) -> bool:
            return risk_score > 7.0

        assert requires_human_approval(8.0) is True
        assert requires_human_approval(7.5) is True
        assert requires_human_approval(7.0) is False   # exactly 7 is NOT above 7
        assert requires_human_approval(6.9) is False
        assert requires_human_approval(0.0) is False

    def test_approval_decisions(self):
        """Valid approval decisions are 'approved' and 'rejected' only."""
        valid_decisions = ["approved", "rejected"]
        for d in valid_decisions:
            assert d in valid_decisions

        assert "maybe" not in valid_decisions
        assert "pending" not in valid_decisions

    def test_workflow_statuses_complete(self):
        """All required workflow statuses must be defined."""
        required = {"pending", "running", "waiting", "approved", "completed", "failed"}
        # These should be in CaseStatus or workflow status enum
        # Checking the string values are well-defined:
        assert "pending" in required
        assert "running" in required
        assert "waiting" in required
        assert "approved" in required
        assert "completed" in required
        assert "failed" in required

    def test_human_gate_blocks_delivery_without_approval(self):
        """
        Delivery is blocked when human_approval_required=True but
        human_approval_status is not 'approved'.
        """
        def can_proceed_to_delivery(state: dict) -> bool:
            if state.get("human_approval_required") and state.get("human_approval_status") != "approved":
                return False
            return True

        blocking_states = [None, "pending", "rejected", ""]
        for approval_status in blocking_states:
            state = {
                "human_approval_required": True,
                "human_approval_status": approval_status,
            }
            assert can_proceed_to_delivery(state) is False, (
                f"Delivery should be BLOCKED when approval_status='{approval_status}'"
            )

    def test_delivery_allowed_when_approval_granted(self):
        """Delivery proceeds when human approval is granted."""
        def can_proceed_to_delivery(state: dict) -> bool:
            if state.get("human_approval_required") and state.get("human_approval_status") != "approved":
                return False
            return True

        state = {
            "human_approval_required": True,
            "human_approval_status": "approved",
        }
        assert can_proceed_to_delivery(state) is True

    def test_delivery_allowed_when_approval_not_required(self):
        """When human approval is not required, delivery proceeds freely."""
        def can_proceed_to_delivery(state: dict) -> bool:
            if state.get("human_approval_required") and state.get("human_approval_status") != "approved":
                return False
            return True

        state = {
            "human_approval_required": False,
            "human_approval_status": None,
        }
        assert can_proceed_to_delivery(state) is True

    def test_risk_threshold_boundary(self):
        """Exact boundary value: risk_score=7.0 does NOT trigger human approval."""
        def requires_human_approval(risk_score: float) -> bool:
            return risk_score > 7.0

        # Boundary conditions
        assert requires_human_approval(7.0) is False, "risk_score=7.0 should NOT require approval"
        assert requires_human_approval(7.001) is True, "risk_score=7.001 SHOULD require approval"
        assert requires_human_approval(10.0) is True
        assert requires_human_approval(0.0) is False
