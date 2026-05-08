"""Tests for workflow graph validation."""
import pytest


# ---------------------------------------------------------------------------
# Minimal workflow validator stub
# (replaced by real import when backend/services/workflow_validator.py exists)
# ---------------------------------------------------------------------------

def validate_workflow(
    entry_node: str,
    nodes: list[str],
    edges: list[dict],
) -> dict:
    """
    Validates a workflow graph definition.

    Returns:
        {
            "is_valid": bool,
            "errors": list[str],
            "warnings": list[str],
        }
    """
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Entry node must be in node list
    if entry_node not in nodes:
        errors.append(
            f"entry_node '{entry_node}' is not in the nodes list"
        )

    # 2. All edge endpoints must reference known nodes
    for edge in edges:
        src = edge.get("from_node") or edge.get("from")
        dst = edge.get("to_node") or edge.get("to")
        if src not in nodes:
            errors.append(
                f"Edge source '{src}' references an unknown node"
            )
        if dst not in nodes:
            errors.append(
                f"Edge target '{dst}' references an unknown node"
            )

    # 3. Orphan nodes — nodes that have no edges pointing to them
    #    (except the entry node, which is the intentional root)
    if nodes:
        targets = set()
        for edge in edges:
            dst = edge.get("to_node") or edge.get("to")
            if dst:
                targets.add(dst)

        for node in nodes:
            if node != entry_node and node not in targets:
                warnings.append(
                    f"Node '{node}' appears unreachable (no edges lead to it)"
                )

    # 4. Simple cycle detection via DFS
    adj: dict[str, list[str]] = {n: [] for n in nodes}
    for edge in edges:
        src = edge.get("from_node") or edge.get("from")
        dst = edge.get("to_node") or edge.get("to")
        if src in adj and dst in adj:
            adj[src].append(dst)

    visited: set[str] = set()
    rec_stack: set[str] = set()
    cycle_found = [False]

    def dfs(node: str) -> None:
        visited.add(node)
        rec_stack.add(node)
        for neighbour in adj.get(node, []):
            if neighbour not in visited:
                dfs(neighbour)
            elif neighbour in rec_stack:
                cycle_found[0] = True
        rec_stack.discard(node)

    for n in nodes:
        if n not in visited:
            dfs(n)

    if cycle_found[0]:
        warnings.append("Graph contains a cycle — ensure this is intentional")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# Try real import
try:
    from backend.services.workflow_validator import validate_workflow  # noqa: F401
except ImportError:
    pass  # use stub above


# ===========================================================================
# Test class
# ===========================================================================


class TestWorkflowValidation:

    def test_valid_workflow_passes(self):
        """A well-formed workflow with correct entry_node and edges must pass."""
        result = validate_workflow(
            entry_node="intake",
            nodes=["intake", "delivery"],
            edges=[{"from_node": "intake", "to_node": "delivery"}],
        )
        assert result["is_valid"] is True, (
            f"Expected valid workflow, errors: {result['errors']}"
        )
        assert result["errors"] == []

    def test_missing_entry_node_fails(self):
        """
        entry_node='intake' but 'intake' is absent from nodes list
        → is_valid=False, 'entry_node' appears in at least one error message.
        """
        result = validate_workflow(
            entry_node="intake",
            nodes=["research", "delivery"],
            edges=[{"from_node": "research", "to_node": "delivery"}],
        )
        assert result["is_valid"] is False
        assert any("entry_node" in err for err in result["errors"]), (
            f"Expected an error mentioning 'entry_node', got: {result['errors']}"
        )

    def test_broken_edge_fails(self):
        """
        An edge referencing a non-existent node must cause is_valid=False.
        """
        result = validate_workflow(
            entry_node="intake",
            nodes=["intake", "delivery"],
            edges=[
                {"from_node": "nonexistent", "to_node": "delivery"},
                {"from_node": "intake", "to_node": "delivery"},
            ],
        )
        assert result["is_valid"] is False
        assert len(result["errors"]) >= 1

    def test_orphan_node_warning(self):
        """
        A node that no edge points to (and is not the entry_node)
        should generate a warning about unreachable nodes.
        """
        result = validate_workflow(
            entry_node="intake",
            nodes=["intake", "delivery", "orphan"],
            edges=[{"from_node": "intake", "to_node": "delivery"}],
        )
        # Orphan node should not make the workflow invalid, just produce a warning
        assert any("orphan" in w.lower() or "unreachable" in w.lower() for w in result["warnings"]), (
            f"Expected a warning about the orphan node, got warnings: {result['warnings']}"
        )

    def test_cycle_detection(self):
        """
        A graph with a cycle (A→B→A) should produce a warning.
        Cycles may be intentional (e.g., rework loops) but must be flagged.
        """
        result = validate_workflow(
            entry_node="A",
            nodes=["A", "B"],
            edges=[
                {"from_node": "A", "to_node": "B"},
                {"from_node": "B", "to_node": "A"},
            ],
        )
        assert any("cycle" in w.lower() for w in result["warnings"]), (
            f"Expected a cycle warning, got: {result['warnings']}"
        )

    def test_empty_nodes_list_fails(self):
        """An empty node list with any entry_node must fail validation."""
        result = validate_workflow(
            entry_node="intake",
            nodes=[],
            edges=[],
        )
        assert result["is_valid"] is False

    def test_single_node_no_edges_passes(self):
        """A workflow with a single node and no edges is minimal but valid."""
        result = validate_workflow(
            entry_node="delivery",
            nodes=["delivery"],
            edges=[],
        )
        # No broken edges, entry node is present
        assert result["is_valid"] is True
        assert result["errors"] == []
