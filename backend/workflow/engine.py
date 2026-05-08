"""
LangGraph workflow engine for TaxLegal v4.
Builds and runs the tax advisory workflow graph.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional, AsyncIterator

logger = logging.getLogger(__name__)

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.info("LangGraph not installed — graph features disabled. Run: pip install langgraph")

from backend.workflow.state import WorkflowState
from backend.workflow.nodes import WorkflowNodes


# ── Graph builder ──────────────────────────────────────────────────────────────

def build_tax_advisory_graph(nodes: WorkflowNodes):
    """
    Build the LangGraph StateGraph for the tax advisory workflow.

    Graph structure:
    START → intake → [missing_facts?] → clarification → intake (max 2 iterations)
                  ↓ (facts complete)
              research → draft → sa_review → [approved?] → partner_review
                                           ↓ (revision)
                                         research (rework loop)

    partner_review → [human_approval_required?] → human_gate → [approved?] → delivery
                   ↓ (not required / approved)                              ↓ (rejected)
                 delivery ← ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ draft (rework)
                   ↓
                 audit → END
    """
    if not LANGGRAPH_AVAILABLE:
        raise RuntimeError(
            "LangGraph not installed. Run: pip install langgraph"
        )

    workflow = StateGraph(WorkflowState)

    # ── Register nodes ─────────────────────────────────────────────────────────
    workflow.add_node("intake", nodes.node_intake)
    workflow.add_node("clarification", nodes.node_clarification)
    workflow.add_node("research", nodes.node_research)
    workflow.add_node("draft", nodes.node_draft)
    workflow.add_node("sa_review", nodes.node_sa_review)
    workflow.add_node("partner_review", nodes.node_partner_review)
    workflow.add_node("human_gate", nodes.node_human_gate)
    workflow.add_node("delivery", nodes.node_delivery)
    workflow.add_node("audit", nodes.node_audit)

    # ── Entry point ────────────────────────────────────────────────────────────
    workflow.set_entry_point("intake")

    # ── Conditional routing functions ──────────────────────────────────────────

    def route_after_intake(state: WorkflowState) -> str:
        """After intake: clarify if missing facts, else research."""
        missing = state.get("missing_facts") or []
        iterations_done = state.get("clarification_iterations", 0)
        if missing and iterations_done < 2:
            return "clarification"
        return "research"

    def route_after_sa_review(state: WorkflowState) -> str:
        """After SA review: rework if revision required (safety cap at 20 total iters)."""
        if (
            state.get("sa_decision") == "revision_required"
            and state.get("iterations", 0) < 20
        ):
            return "research"
        return "partner_review"

    def route_after_partner_review(state: WorkflowState) -> str:
        """After partner review: gate if human approval needed."""
        if state.get("human_approval_required"):
            return "human_gate"
        return "delivery"

    def route_after_human_gate(state: WorkflowState) -> str:
        """After human gate: proceed, rework, or wait."""
        status = state.get("human_approval_status")
        if status == "approved":
            return "delivery"
        elif status == "rejected":
            return "draft"  # rework
        # "pending" or None — stay in gate
        return "human_gate"

    # ── Wire edges ─────────────────────────────────────────────────────────────
    workflow.add_conditional_edges(
        "intake",
        route_after_intake,
        {"clarification": "clarification", "research": "research"},
    )
    workflow.add_edge("clarification", "intake")
    workflow.add_edge("research", "draft")
    workflow.add_edge("draft", "sa_review")
    workflow.add_conditional_edges(
        "sa_review",
        route_after_sa_review,
        {"research": "research", "partner_review": "partner_review"},
    )
    workflow.add_conditional_edges(
        "partner_review",
        route_after_partner_review,
        {"human_gate": "human_gate", "delivery": "delivery"},
    )
    workflow.add_conditional_edges(
        "human_gate",
        route_after_human_gate,
        {"delivery": "delivery", "draft": "draft", "human_gate": "human_gate"},
    )
    workflow.add_edge("delivery", "audit")
    workflow.add_edge("audit", END)

    # ── Compile with checkpointing ─────────────────────────────────────────────
    memory = MemorySaver()
    graph = workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_gate"],  # pause before human gate for external signal
    )
    return graph


# ── Run helpers ────────────────────────────────────────────────────────────────

async def run_workflow(
    case_id: str,
    initial_state: WorkflowState,
    db,
    dbvntax_db=None,
) -> Optional[WorkflowState]:
    """
    Run the full tax advisory workflow graph.
    Returns final state dict (last event from graph.astream).
    """
    if not LANGGRAPH_AVAILABLE:
        logger.warning("LangGraph not available — running linear fallback.")
        return await _run_linear_fallback(case_id, initial_state, db, dbvntax_db)

    nodes = WorkflowNodes(db=db, dbvntax_db=dbvntax_db)
    graph = build_tax_advisory_graph(nodes)
    config = {"configurable": {"thread_id": case_id}}

    final_state = None
    try:
        async for event in graph.astream(initial_state, config=config):
            node_names = list(event.keys())
            logger.info(f"Workflow event nodes: {node_names}")
            # astream yields {node_name: partial_state} per step
            # Merge into final_state accumulation
            if final_state is None:
                final_state = dict(initial_state)
            for node_name, node_output in event.items():
                if isinstance(node_output, dict):
                    final_state.update(node_output)
    except Exception as e:
        logger.error(f"Workflow run error for case {case_id}: {e}")
        raise

    return final_state


async def resume_workflow_after_approval(
    case_id: str,
    db,
    dbvntax_db=None,
) -> Optional[WorkflowState]:
    """
    Resume the workflow graph after a human approval signal has been set.
    Passes None as input (uses checkpointed state) to continue from human_gate.
    """
    if not LANGGRAPH_AVAILABLE:
        logger.warning("LangGraph not available — cannot resume workflow.")
        return None

    nodes = WorkflowNodes(db=db, dbvntax_db=dbvntax_db)
    graph = build_tax_advisory_graph(nodes)
    config = {"configurable": {"thread_id": case_id}}

    final_state = None
    try:
        async for event in graph.astream(None, config=config):
            logger.info(f"Resume event nodes: {list(event.keys())}")
            if final_state is None:
                final_state = {}
            for node_name, node_output in event.items():
                if isinstance(node_output, dict):
                    final_state.update(node_output)
    except Exception as e:
        logger.error(f"Workflow resume error for case {case_id}: {e}")
        raise

    return final_state


# ── Linear fallback (no LangGraph) ────────────────────────────────────────────

async def _run_linear_fallback(
    case_id: str,
    initial_state: WorkflowState,
    db,
    dbvntax_db=None,
) -> WorkflowState:
    """
    Simple sequential execution of all nodes without LangGraph.
    Used as fallback when langgraph is not installed.
    """
    logger.info(f"Running linear fallback pipeline for case {case_id}")
    nodes = WorkflowNodes(db=db, dbvntax_db=dbvntax_db)
    state = dict(initial_state)

    # Ensure required defaults
    state.setdefault("iterations", 0)
    state.setdefault("max_iterations", 50)
    state.setdefault("clarification_iterations", 0)
    state.setdefault("completed_nodes", [])
    state.setdefault("audit_events", [])
    state.setdefault("citations", [])
    state.setdefault("retrieval_queries", [])
    state.setdefault("used_fallback_search", False)
    state.setdefault("has_insufficient_coverage", False)

    pipeline = [
        ("intake", nodes.node_intake),
        ("research", nodes.node_research),
        ("draft", nodes.node_draft),
        ("sa_review", nodes.node_sa_review),
        ("partner_review", nodes.node_partner_review),
        ("delivery", nodes.node_delivery),
        ("audit", nodes.node_audit),
    ]

    for node_name, node_fn in pipeline:
        if state.get("iterations", 0) >= state.get("max_iterations", 50):
            logger.warning(f"Max iterations reached at {node_name}")
            break
        try:
            logger.info(f"[linear_fallback] Running {node_name}")
            update = await node_fn(state)
            if update:
                # Merge audit_events (append-only)
                if "audit_events" in update:
                    existing = state.get("audit_events") or []
                    update["audit_events"] = existing + update["audit_events"]
                state.update(update)
        except Exception as e:
            logger.error(f"[linear_fallback] Node {node_name} failed: {e}")
            state["error"] = str(e)
            break

    return state
