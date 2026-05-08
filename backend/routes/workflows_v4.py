"""
Workflow Definitions API — TaxLegal v4.

POST   /api/workflows                        — create workflow definition
PATCH  /api/workflows/{workflow_id}          — update workflow definition
GET    /api/workflows                        — list workflow definitions
GET    /api/workflows/{workflow_id}          — get detail with nodes and edges
POST   /api/workflows/{workflow_id}/validate — validate graph structure
POST   /api/workflows/{workflow_id}/nodes    — add a node
POST   /api/workflows/{workflow_id}/edges    — add an edge
DELETE /api/workflows/{workflow_id}/nodes/{node_id} — remove node
"""
import json
import logging
import uuid
from collections import deque
from datetime import datetime
from typing import Optional, List, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.database import get_db
from backend.auth import get_current_user
from backend.models import User

logger = logging.getLogger(__name__)
router = APIRouter(tags=["workflows"])


# ── Pydantic schemas ───────────────────────────────────────────────────────────

class WorkflowDefinitionCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    practice_area: str = "tax"
    entry_node: Optional[str] = None


class WorkflowDefinitionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    practice_area: Optional[str] = None
    entry_node: Optional[str] = None
    is_active: Optional[bool] = None


class WorkflowNodeCreate(BaseModel):
    node_id: str
    node_type: str = "agent"  # agent|human_gate|condition|start|end
    label: str
    bot_definition_id: Optional[int] = None
    skill_ids: list[int] = []
    config: dict = {}
    position_x: Optional[float] = None
    position_y: Optional[float] = None


class WorkflowEdgeCreate(BaseModel):
    from_node: str
    to_node: str
    condition: Optional[str] = None
    label: Optional[str] = None


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _get_workflow_or_404(db: AsyncSession, workflow_id: str) -> dict:
    try:
        result = await db.execute(
            text("SELECT * FROM taxlegal.workflow_definitions WHERE id = :id"),
            {"id": workflow_id},
        )
        row = result.mappings().one_or_none()
    except Exception as e:
        logger.warning(f"workflow_definitions query error: {e}")
        raise HTTPException(status_code=404, detail="Workflow not found")

    if not row:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return dict(row)


def _serialize_wf(row: dict) -> dict:
    out = dict(row)
    for k in ("created_at", "updated_at"):
        if out.get(k) and hasattr(out[k], "isoformat"):
            out[k] = out[k].isoformat()
    out["id"] = str(out["id"])
    return out


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post("/api/workflows", status_code=201)
async def create_workflow_definition(
    req: WorkflowDefinitionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new workflow definition."""
    wf_id = str(uuid.uuid4())
    now = datetime.utcnow()

    try:
        await db.execute(
            text("""
                INSERT INTO taxlegal.workflow_definitions
                    (id, name, slug, description, practice_area, entry_node,
                     version, is_active, is_default, graph_definition,
                     created_by, created_at, updated_at)
                VALUES
                    (:id, :name, :slug, :description, :practice_area, :entry_node,
                     1, TRUE, FALSE, '{}',
                     :created_by, :now, :now)
            """),
            {
                "id": wf_id,
                "name": req.name,
                "slug": req.slug,
                "description": req.description,
                "practice_area": req.practice_area,
                "entry_node": req.entry_node,
                "created_by": current_user.id,
                "now": now,
            },
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to create workflow definition: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {e}")

    return {
        "id": wf_id,
        "name": req.name,
        "slug": req.slug,
        "description": req.description,
        "practice_area": req.practice_area,
        "entry_node": req.entry_node,
        "version": 1,
        "is_active": True,
        "is_default": False,
        "created_at": now.isoformat(),
    }


@router.patch("/api/workflows/{workflow_id}")
async def update_workflow_definition(
    workflow_id: str,
    req: WorkflowDefinitionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing workflow definition."""
    await _get_workflow_or_404(db, workflow_id)

    now = datetime.utcnow()
    updates = req.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clauses = ", ".join([f"{k} = :{k}" for k in updates])
    set_clauses += ", updated_at = :now"
    updates["now"] = now
    updates["workflow_id"] = workflow_id

    try:
        await db.execute(
            text(f"UPDATE taxlegal.workflow_definitions SET {set_clauses} WHERE id = :workflow_id"),
            updates,
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to update workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Update failed: {e}")

    # Return updated record
    wf = await _get_workflow_or_404(db, workflow_id)
    return _serialize_wf(wf)


@router.get("/api/workflows")
async def list_workflow_definitions(
    practice_area: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List workflow definitions."""
    try:
        filters = []
        params: dict = {}
        if practice_area:
            filters.append("practice_area = :practice_area")
            params["practice_area"] = practice_area
        if is_active is not None:
            filters.append("is_active = :is_active")
            params["is_active"] = is_active

        where = "WHERE " + " AND ".join(filters) if filters else ""
        result = await db.execute(
            text(f"""
                SELECT id, name, slug, description, practice_area, entry_node,
                       version, is_active, is_default, created_at, updated_at
                FROM taxlegal.workflow_definitions
                {where}
                ORDER BY is_default DESC, created_at DESC
            """),
            params,
        )
        rows = result.mappings().all()
    except Exception as e:
        logger.warning(f"workflow_definitions list error: {e}")
        return []

    return [_serialize_wf(dict(r)) for r in rows]


@router.get("/api/workflows/{workflow_id}")
async def get_workflow_definition(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get workflow definition detail with nodes and edges."""
    wf = await _get_workflow_or_404(db, workflow_id)
    result = _serialize_wf(wf)

    # Fetch nodes
    try:
        nodes_result = await db.execute(
            text("""
                SELECT id, workflow_id, node_id, node_type, label,
                       bot_definition_id, skill_ids, config,
                       position_x, position_y, created_at
                FROM taxlegal.workflow_nodes
                WHERE workflow_id = :wf_id
                ORDER BY created_at ASC
            """),
            {"wf_id": workflow_id},
        )
        nodes = [dict(r) for r in nodes_result.mappings().all()]
        for n in nodes:
            if n.get("created_at") and hasattr(n["created_at"], "isoformat"):
                n["created_at"] = n["created_at"].isoformat()
            n["id"] = str(n["id"])
    except Exception as e:
        logger.warning(f"workflow_nodes query error: {e}")
        nodes = []

    # Fetch edges
    try:
        edges_result = await db.execute(
            text("""
                SELECT id, workflow_id, from_node, to_node, condition, label, created_at
                FROM taxlegal.workflow_edges
                WHERE workflow_id = :wf_id
                ORDER BY created_at ASC
            """),
            {"wf_id": workflow_id},
        )
        edges = [dict(r) for r in edges_result.mappings().all()]
        for e in edges:
            if e.get("created_at") and hasattr(e["created_at"], "isoformat"):
                e["created_at"] = e["created_at"].isoformat()
            e["id"] = str(e["id"])
    except Exception as e:
        logger.warning(f"workflow_edges query error: {e}")
        edges = []

    result["nodes"] = nodes
    result["edges"] = edges
    return result


@router.post("/api/workflows/{workflow_id}/validate")
async def validate_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Validate the workflow graph structure:
    - entry_node exists in nodes
    - all edge from_node/to_node reference existing nodes
    - all bot_definition_id references exist in taxlegal.bot_variants
    - no orphan nodes (every node reachable from entry_node)
    - no missing end node (at least one node has no outgoing edges)
    """
    wf = await _get_workflow_or_404(db, workflow_id)
    errors: list[str] = []
    warnings: list[str] = []

    entry_node = wf.get("entry_node")

    # Load nodes
    try:
        nodes_result = await db.execute(
            text("SELECT node_id, node_type, bot_definition_id FROM taxlegal.workflow_nodes WHERE workflow_id = :wf_id"),
            {"wf_id": workflow_id},
        )
        nodes = [dict(r) for r in nodes_result.mappings().all()]
    except Exception as e:
        logger.warning(f"Could not load nodes for validation: {e}")
        nodes = []

    node_ids = {n["node_id"] for n in nodes}

    # Load edges
    try:
        edges_result = await db.execute(
            text("SELECT from_node, to_node FROM taxlegal.workflow_edges WHERE workflow_id = :wf_id"),
            {"wf_id": workflow_id},
        )
        edges = [dict(r) for r in edges_result.mappings().all()]
    except Exception as e:
        logger.warning(f"Could not load edges for validation: {e}")
        edges = []

    # Check 1: entry_node exists
    if not entry_node:
        errors.append("entry_node is not set on this workflow definition")
    elif entry_node not in node_ids:
        errors.append(f"entry_node '{entry_node}' does not exist in nodes")

    # Check 2: edge references valid nodes
    for edge in edges:
        if edge["from_node"] not in node_ids:
            errors.append(f"Edge references unknown from_node: '{edge['from_node']}'")
        if edge["to_node"] not in node_ids:
            errors.append(f"Edge references unknown to_node: '{edge['to_node']}'")

    # Check 3: bot_definition_id references valid bot_variants
    bot_ids = {n["bot_definition_id"] for n in nodes if n.get("bot_definition_id")}
    if bot_ids:
        try:
            placeholders = ", ".join([f":b{i}" for i in range(len(bot_ids))])
            params = {f"b{i}": bid for i, bid in enumerate(bot_ids)}
            result = await db.execute(
                text(f"SELECT id FROM taxlegal.bot_variants WHERE id IN ({placeholders})"),
                params,
            )
            found_bot_ids = {row[0] for row in result.fetchall()}
            missing_bots = bot_ids - found_bot_ids
            for bid in missing_bots:
                errors.append(f"bot_definition_id {bid} not found in taxlegal.bot_variants")
        except Exception as e:
            warnings.append(f"Could not validate bot_definition_ids: {e}")

    # Check 4: no orphan nodes — BFS from entry_node
    if entry_node and entry_node in node_ids and not errors:
        adjacency: dict[str, list[str]] = {nid: [] for nid in node_ids}
        for edge in edges:
            if edge["from_node"] in adjacency:
                adjacency[edge["from_node"]].append(edge["to_node"])

        visited: set[str] = set()
        queue = deque([entry_node])
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for neighbor in adjacency.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)

        orphans = node_ids - visited
        for orphan in sorted(orphans):
            warnings.append(f"Node '{orphan}' is not reachable from entry_node '{entry_node}'")

    # Check 5: at least one end node (no outgoing edges)
    nodes_with_outgoing = {e["from_node"] for e in edges}
    end_nodes = node_ids - nodes_with_outgoing
    if not end_nodes and node_ids:
        errors.append("No end node found — at least one node must have no outgoing edges")

    is_valid = len(errors) == 0
    return {"is_valid": is_valid, "errors": errors, "warnings": warnings}


@router.post("/api/workflows/{workflow_id}/nodes", status_code=201)
async def add_workflow_node(
    workflow_id: str,
    req: WorkflowNodeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a node to a workflow definition."""
    await _get_workflow_or_404(db, workflow_id)

    node_row_id = str(uuid.uuid4())
    now = datetime.utcnow()

    try:
        await db.execute(
            text("""
                INSERT INTO taxlegal.workflow_nodes
                    (id, workflow_id, node_id, node_type, label,
                     bot_definition_id, skill_ids, config,
                     position_x, position_y, created_at, updated_at)
                VALUES
                    (:id, :workflow_id, :node_id, :node_type, :label,
                     :bot_definition_id, :skill_ids, :config,
                     :position_x, :position_y, :now, :now)
                ON CONFLICT (workflow_id, node_id) DO UPDATE SET
                    node_type = EXCLUDED.node_type,
                    label = EXCLUDED.label,
                    bot_definition_id = EXCLUDED.bot_definition_id,
                    skill_ids = EXCLUDED.skill_ids,
                    config = EXCLUDED.config,
                    position_x = EXCLUDED.position_x,
                    position_y = EXCLUDED.position_y,
                    updated_at = EXCLUDED.updated_at
            """),
            {
                "id": node_row_id,
                "workflow_id": workflow_id,
                "node_id": req.node_id,
                "node_type": req.node_type,
                "label": req.label,
                "bot_definition_id": req.bot_definition_id,
                "skill_ids": req.skill_ids,
                "config": json.dumps(req.config),
                "position_x": req.position_x,
                "position_y": req.position_y,
                "now": now,
            },
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to add node to workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add node: {e}")

    return {
        "id": node_row_id,
        "workflow_id": workflow_id,
        "node_id": req.node_id,
        "node_type": req.node_type,
        "label": req.label,
        "bot_definition_id": req.bot_definition_id,
        "skill_ids": req.skill_ids,
        "config": req.config,
        "position_x": req.position_x,
        "position_y": req.position_y,
        "created_at": now.isoformat(),
    }


@router.post("/api/workflows/{workflow_id}/edges", status_code=201)
async def add_workflow_edge(
    workflow_id: str,
    req: WorkflowEdgeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add an edge to a workflow definition."""
    await _get_workflow_or_404(db, workflow_id)

    edge_id = str(uuid.uuid4())
    now = datetime.utcnow()

    try:
        await db.execute(
            text("""
                INSERT INTO taxlegal.workflow_edges
                    (id, workflow_id, from_node, to_node, condition, label, created_at, updated_at)
                VALUES
                    (:id, :workflow_id, :from_node, :to_node, :condition, :label, :now, :now)
            """),
            {
                "id": edge_id,
                "workflow_id": workflow_id,
                "from_node": req.from_node,
                "to_node": req.to_node,
                "condition": req.condition,
                "label": req.label,
                "now": now,
            },
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to add edge to workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add edge: {e}")

    return {
        "id": edge_id,
        "workflow_id": workflow_id,
        "from_node": req.from_node,
        "to_node": req.to_node,
        "condition": req.condition,
        "label": req.label,
        "created_at": now.isoformat(),
    }


@router.delete("/api/workflows/{workflow_id}/nodes/{node_id}", status_code=204)
async def remove_workflow_node(
    workflow_id: str,
    node_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a node from a workflow definition."""
    await _get_workflow_or_404(db, workflow_id)

    try:
        result = await db.execute(
            text("""
                DELETE FROM taxlegal.workflow_nodes
                WHERE workflow_id = :workflow_id AND node_id = :node_id
            """),
            {"workflow_id": workflow_id, "node_id": node_id},
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found in workflow")

        # Also remove edges referencing this node
        await db.execute(
            text("""
                DELETE FROM taxlegal.workflow_edges
                WHERE workflow_id = :workflow_id
                  AND (from_node = :node_id OR to_node = :node_id)
            """),
            {"workflow_id": workflow_id, "node_id": node_id},
        )
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove node '{node_id}' from workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to remove node: {e}")
