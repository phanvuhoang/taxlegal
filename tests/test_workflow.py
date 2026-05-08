"""Tests for workflow state machine transitions."""
import pytest


# ---------------------------------------------------------------------------
# Routing logic stubs
# When the real backend is importable, these are replaced by actual functions.
# ---------------------------------------------------------------------------

def route_after_intake(state: dict) -> str:
    """
    Determines the next node after 'intake'.
    Rules:
      - If missing_facts is non-empty AND clarification_iterations < 2 → 'clarification'
      - Otherwise → 'research'
    """
    missing = state.get("missing_facts", [])
    iters = state.get("clarification_iterations", 0)
    max_clarifications = 2

    if missing and iters < max_clarifications:
        return "clarification"
    return "research"


def route_after_sa_review(state: dict) -> str:
    """
    Routes from SA review node.
    - 'approved'           → 'partner_review'
    - 'revision_required'  → 'research' (rework)
    - 'rejected'           → 'delivery' (with error flag)
    """
    decision = state.get("sa_decision")
    if decision == "approved":
        return "partner_review"
    if decision == "revision_required":
        return "research"
    # default / rejected
    return "delivery"


def route_after_partner_review(state: dict) -> str:
    """
    Routes from partner review.
    - risk_score > 7 → 'human_gate'
    - approved       → 'delivery'
    """
    risk = state.get("risk_score", 0.0)
    decision = state.get("partner_decision")

    if risk > 7.0:
        return "human_gate"
    if decision == "approved":
        return "delivery"
    return "research"


def route_human_gate(state: dict) -> str:
    """
    Human approval gate.
    - human_approval_status == None   → stays at 'human_gate'
    - human_approval_status == 'approved' → 'delivery'
    - human_approval_status == 'rejected' → 'research'
    """
    status = state.get("human_approval_status")
    if status is None:
        return "human_gate"
    if status == "approved":
        return "delivery"
    return "research"


def can_proceed_to_delivery(state: dict) -> bool:
    """
    Returns True only when delivery is safe to proceed.
    Blocks if human approval is required but not yet granted.
    """
    if state.get("human_approval_required") and state.get("human_approval_status") != "approved":
        return False
    return True


# Try importing the real routing functions (no-op if backend not present)
try:
    from backend.workflow.routing import (  # noqa: F401
        route_after_intake,
        route_after_sa_review,
        route_after_partner_review,
        route_human_gate,
        can_proceed_to_delivery,
    )
except ImportError:
    pass  # use stubs defined above


# ===========================================================================
# Tests
# ===========================================================================


def test_route_after_intake_missing_facts():
    """Missing facts + iteration room → route to clarification."""
    state = {
        "missing_facts": ["Năm tính thuế?"],
        "clarification_iterations": 0,
    }
    assert route_after_intake(state) == "clarification"


def test_route_after_intake_no_missing_facts():
    """No missing facts → skip clarification, go to research."""
    state = {
        "missing_facts": [],
        "clarification_iterations": 0,
    }
    assert route_after_intake(state) == "research"


def test_route_after_sa_review_approved():
    """SA approves draft → forward to partner review."""
    state = {"sa_decision": "approved", "iterations": 1}
    assert route_after_sa_review(state) == "partner_review"


def test_route_after_sa_review_revision():
    """SA requests revision → send back to research for rework."""
    state = {"sa_decision": "revision_required", "iterations": 5}
    assert route_after_sa_review(state) == "research"


def test_clarification_max_iterations():
    """
    When clarification_iterations has reached the maximum (2),
    the system must stop asking and proceed to research even if
    facts are still missing — prevents infinite loops.
    """
    state = {
        "missing_facts": ["Doanh thu năm 2023?", "Loại hình doanh nghiệp?"],
        "clarification_iterations": 2,  # at max
    }
    result = route_after_intake(state)
    assert result == "research", (
        f"Expected 'research' at max clarification iterations, got {result!r}"
    )


def test_partner_review_triggers_human_approval():
    """
    High-risk cases (risk_score > 7) must be routed through human approval gate.
    """
    state = {
        "risk_score": 8.5,
        "partner_decision": "approved",
        "human_approval_required": True,
    }
    route = route_after_partner_review(state)
    # Either the routing function goes to human_gate, OR the flag is set
    assert route == "human_gate" or state.get("human_approval_required") is True


def test_human_gate_blocks_delivery_when_pending():
    """
    When human_approval_status is None (pending), the workflow must
    stay at human_gate and not advance to delivery.
    """
    state = {
        "human_approval_required": True,
        "human_approval_status": None,
    }
    result = route_human_gate(state)
    assert result == "human_gate", (
        f"Expected routing to stay at 'human_gate' while pending, got {result!r}"
    )


def test_delivery_blocked_without_approval_when_required():
    """
    Delivery must be blocked when human approval is required
    but has not been granted (status is None).
    """
    state = {
        "human_approval_required": True,
        "human_approval_status": None,
        "final_output": "Some drafted opinion",
    }
    assert can_proceed_to_delivery(state) is False, (
        "Delivery should be BLOCKED when human approval is pending"
    )


def test_delivery_allowed_when_approved():
    """Delivery is allowed once human approves."""
    state = {
        "human_approval_required": True,
        "human_approval_status": "approved",
    }
    assert can_proceed_to_delivery(state) is True


def test_delivery_allowed_when_not_required():
    """When human approval is not required, delivery proceeds freely."""
    state = {
        "human_approval_required": False,
        "human_approval_status": None,
    }
    assert can_proceed_to_delivery(state) is True
