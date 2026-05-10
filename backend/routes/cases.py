"""
Cases API — TaxLegal v4 case management with workflow integration.

POST   /api/cases                           — create case
GET    /api/cases                           — list cases (paginated, filter by status)
GET    /api/cases/{case_id}                 — get case detail
POST   /api/cases/{case_id}/attachments     — upload attachment
POST   /api/cases/{case_id}/start           — start workflow execution
GET    /api/cases/{case_id}/state           — get current workflow state
GET    /api/cases/{case_id}/events          — list case events
GET    /api/cases/{case_id}/versions        — list case versions
POST   /api/cases/{case_id}/human-approval  — submit human approval decision
GET    /api/cases/{case_id}/final           — get final output
"""
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Optional, List, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.database import get_db
from backend.auth import get_current_user
from backend.models import User

logger = logging.getLogger(__name__)
router = APIRouter(tags=["cases"])


# ── Pydantic schemas ───────────────────────────────────────────────────────────

class CaseCreate(BaseModel):
    title: str
    client_request: str
    practice_area: str = "tax"
    output_language: str = "vi"
    priority: str = "normal"
    workflow_definition_id: Optional[str] = None
    use_legacy_pipeline: bool = True  # default to legacy for backward compat
    pipeline_mode: str = "manual"
    pipeline_template_id: Optional[int] = None


class CaseStartRequest(BaseModel):
    model_override: Optional[str] = None
    use_legacy_pipeline: bool = True


class HumanApprovalDecision(BaseModel):
    decision: str  # approved | rejected
    notes: str = ""


# ── Helper ─────────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.utcnow().isoformat()


async def _get_case_or_404(db: AsyncSession, case_id: str, user: User) -> dict:
    try:
        result = await db.execute(
            text("SELECT * FROM taxlegal.cases WHERE id = :id"),
            {"id": case_id},
        )
        row = result.mappings().one_or_none()
    except Exception as e:
        logger.warning(f"cases table query error: {e}")
        raise HTTPException(status_code=404, detail="Case not found")

    if not row:
        raise HTTPException(status_code=404, detail="Case not found")

    case = dict(row)
    # Access control: admins see all, others only their own
    if user.role != "admin" and str(case.get("created_by")) != str(user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    return case


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post("/api/cases", status_code=201)
async def create_case(
    req: CaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new case and a corresponding matters row for backward compatibility."""
    case_id = str(uuid.uuid4())
    now = datetime.utcnow()

    # Insert into taxlegal.cases
    try:
        await db.execute(
            text("""
                INSERT INTO taxlegal.cases
                    (id, title, client_request, practice_area, output_language,
                     priority, workflow_definition_id, use_legacy_pipeline,
                     pipeline_mode, pipeline_template_id, status, created_by, created_at, updated_at)
                VALUES
                    (:id, :title, :client_request, :practice_area, :output_language,
                     :priority, :workflow_definition_id, :use_legacy_pipeline,
                     :pipeline_mode, :pipeline_template_id, 'draft', :created_by, :now, :now)
            """),
            {
                "id": case_id,
                "title": req.title,
                "client_request": req.client_request,
                "practice_area": req.practice_area,
                "output_language": req.output_language,
                "priority": req.priority,
                "workflow_definition_id": req.workflow_definition_id,
                "use_legacy_pipeline": req.use_legacy_pipeline,
                "pipeline_mode": req.pipeline_mode,
                "pipeline_template_id": req.pipeline_template_id,
                "created_by": current_user.id,
                "now": now,
            },
        )
    except Exception as e:
        logger.error(f"Failed to insert case: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create case: {e}")

    # Create corresponding matters row for backward compatibility
    # and store the returned matter_id back into taxlegal.cases.
    try:
        matter_result = await db.execute(
            text("""
                INSERT INTO taxlegal.matters
                    (user_id, title, client_request, practice_area, pipeline_mode,
                     output_language, status, current_step, pipeline_template_id,
                     is_sample, created_at)
                VALUES
                    (:user_id, :title, :client_request, :practice_area, :pipeline_mode,
                     :output_language, 'draft', 0, :pipeline_template_id,
                     FALSE, :now)
                RETURNING id
            """),
            {
                "user_id": current_user.id,
                "title": req.title,
                "client_request": req.client_request,
                "practice_area": req.practice_area,
                "pipeline_mode": req.pipeline_mode,
                "output_language": req.output_language,
                "pipeline_template_id": req.pipeline_template_id,
                "now": now,
            },
        )
        matter_row = matter_result.one_or_none()
        if matter_row:
            new_matter_id = matter_row[0]
            # Store matter_id back into taxlegal.cases for legacy pipeline lookup
            try:
                await db.execute(
                    text("""
                        UPDATE taxlegal.cases
                        SET matter_id = :matter_id
                        WHERE id = :case_id
                    """),
                    {"matter_id": new_matter_id, "case_id": case_id},
                )
            except Exception as update_err:
                logger.warning(
                    f"Could not set matter_id={new_matter_id} on case {case_id}: {update_err}"
                )
        else:
            logger.warning(f"matters INSERT returned no id for case {case_id}")
    except Exception as e:
        logger.warning(f"Could not create backward-compat matter row: {e}")

    await db.commit()

    return {
        "id": case_id,
        "title": req.title,
        "client_request": req.client_request,
        "practice_area": req.practice_area,
        "output_language": req.output_language,
        "priority": req.priority,
        "status": "draft",
        "pipeline_mode": req.pipeline_mode,
        "use_legacy_pipeline": req.use_legacy_pipeline,
        "created_by": current_user.id,
        "created_at": now.isoformat(),
    }


@router.get("/api/cases")
async def list_cases(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List cases with pagination and optional status filter."""
    try:
        if current_user.role == "admin":
            if status:
                result = await db.execute(
                    text("""
                        SELECT id, title, practice_area, status, priority,
                               pipeline_mode, created_by, created_at, updated_at
                        FROM taxlegal.cases
                        WHERE status = :status
                        ORDER BY created_at DESC
                        LIMIT :limit OFFSET :skip
                    """),
                    {"status": status, "limit": limit, "skip": skip},
                )
            else:
                result = await db.execute(
                    text("""
                        SELECT id, title, practice_area, status, priority,
                               pipeline_mode, created_by, created_at, updated_at
                        FROM taxlegal.cases
                        ORDER BY created_at DESC
                        LIMIT :limit OFFSET :skip
                    """),
                    {"limit": limit, "skip": skip},
                )
        else:
            if status:
                result = await db.execute(
                    text("""
                        SELECT id, title, practice_area, status, priority,
                               pipeline_mode, created_by, created_at, updated_at
                        FROM taxlegal.cases
                        WHERE created_by = :uid AND status = :status
                        ORDER BY created_at DESC
                        LIMIT :limit OFFSET :skip
                    """),
                    {"uid": current_user.id, "status": status, "limit": limit, "skip": skip},
                )
            else:
                result = await db.execute(
                    text("""
                        SELECT id, title, practice_area, status, priority,
                               pipeline_mode, created_by, created_at, updated_at
                        FROM taxlegal.cases
                        WHERE created_by = :uid
                        ORDER BY created_at DESC
                        LIMIT :limit OFFSET :skip
                    """),
                    {"uid": current_user.id, "limit": limit, "skip": skip},
                )

        rows = result.mappings().all()
        return [
            {
                "id": str(r["id"]),
                "title": r["title"],
                "practice_area": r["practice_area"],
                "status": r["status"],
                "priority": r["priority"],
                "pipeline_mode": r["pipeline_mode"],
                "created_by": r["created_by"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "updated_at": r["updated_at"].isoformat() if r["updated_at"] else None,
            }
            for r in rows
        ]
    except Exception as e:
        logger.warning(f"list_cases error (table may not exist): {e}")
        return []


@router.get("/api/cases/{case_id}")
async def get_case(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get case detail."""
    case = await _get_case_or_404(db, case_id, current_user)
    # Serialize datetimes
    for k in ("created_at", "updated_at"):
        if case.get(k) and hasattr(case[k], "isoformat"):
            case[k] = case[k].isoformat()
    case["id"] = str(case["id"])
    return case


@router.post("/api/cases/{case_id}/attachments", status_code=201)
async def upload_attachment(
    case_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload an attachment to a case."""
    await _get_case_or_404(db, case_id, current_user)

    content = await file.read()
    file_size = len(content)
    attachment_id = str(uuid.uuid4())
    now = datetime.utcnow()

    # Store in uploads directory if configured, else just record metadata
    upload_dir = os.getenv("UPLOAD_DIR", "/tmp/taxlegal_uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{attachment_id}_{file.filename}")
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.warning(f"Could not write attachment to disk: {e}")
        file_path = None

    try:
        await db.execute(
            text("""
                INSERT INTO taxlegal.case_attachments
                    (id, case_id, filename, content_type, file_size, file_path,
                     uploaded_by, created_at)
                VALUES
                    (:id, :case_id, :filename, :content_type, :file_size, :file_path,
                     :uploaded_by, :now)
            """),
            {
                "id": attachment_id,
                "case_id": case_id,
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": file_size,
                "file_path": file_path,
                "uploaded_by": current_user.id,
                "now": now,
            },
        )
        await db.commit()
    except Exception as e:
        logger.warning(f"Could not persist attachment metadata: {e}")

    return {
        "id": attachment_id,
        "case_id": case_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size": file_size,
        "created_at": now.isoformat(),
    }


@router.post("/api/cases/{case_id}/start")
async def start_workflow(
    case_id: str,
    req: CaseStartRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start workflow execution for a case."""
    case = await _get_case_or_404(db, case_id, current_user)

    run_id = str(uuid.uuid4())
    now = datetime.utcnow()

    # Create workflow_runs row
    try:
        await db.execute(
            text("""
                INSERT INTO taxlegal.workflow_runs
                    (id, case_id, status, state, started_at, created_at)
                VALUES
                    (:id, :case_id, 'running', '{}', :now, :now)
                ON CONFLICT (case_id) DO UPDATE SET
                    status = 'running',
                    started_at = :now
            """),
            {"id": run_id, "case_id": case_id, "now": now},
        )
    except Exception as e:
        logger.warning(f"workflow_runs insert failed: {e}")

    # Update case status
    try:
        await db.execute(
            text("UPDATE taxlegal.cases SET status = 'running', updated_at = :now WHERE id = :id"),
            {"now": now, "id": case_id},
        )
    except Exception as e:
        logger.warning(f"Could not update case status: {e}")

    await db.commit()

    # Try LangGraph workflow unless legacy requested
    use_legacy = req.use_legacy_pipeline or case.get("use_legacy_pipeline", True)
    engine_used = "legacy_pipeline"

    if not use_legacy:
        try:
            from backend.workflow.engine import run_workflow  # noqa: F401
            background_tasks.add_task(run_workflow, case_id, run_id, req.model_override)
            engine_used = "langgraph"
            logger.info(f"Started LangGraph workflow for case {case_id}, run {run_id}")
        except Exception as e:
            logger.warning(f"LangGraph unavailable, falling back to legacy pipeline: {e}")
            use_legacy = True

    if use_legacy:
        background_tasks.add_task(_run_legacy_pipeline_bg, case_id, req.model_override)
        logger.info(f"Started legacy pipeline for case {case_id}")

    # Create initial case_events row
    event_id = str(uuid.uuid4())
    try:
        await db.execute(
            text("""
                INSERT INTO taxlegal.case_events
                    (id, case_id, event_type, node_name, data, created_at)
                VALUES
                    (:id, :case_id, 'workflow_started',
                     'start', :data::jsonb, :now)
            """),
            {
                "id": event_id,
                "case_id": case_id,
                "data": json.dumps({"run_id": run_id, "engine": engine_used}),
                "user_id": current_user.id,
                "now": now,
            },
        )
        await db.commit()
    except Exception as e:
        logger.warning(f"Could not create case_events row: {e}")

    return {
        "run_id": run_id,
        "case_id": case_id,
        "status": "running",
        "engine": engine_used,
        "started_at": now.isoformat(),
    }


@router.get("/api/cases/{case_id}/state")
async def get_case_state(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current workflow state from workflow_runs.state JSONB."""
    await _get_case_or_404(db, case_id, current_user)

    try:
        result = await db.execute(
            text("""
                SELECT id, case_id, status, state, started_at, completed_at
                FROM taxlegal.workflow_runs
                WHERE case_id = :case_id
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"case_id": case_id},
        )
        row = result.mappings().one_or_none()
    except Exception as e:
        logger.warning(f"workflow_runs query error: {e}")
        row = None

    if not row:
        return {"case_id": case_id, "status": "not_started", "state": {}}

    return {
        "run_id": str(row["id"]),
        "case_id": case_id,
        "status": row["status"],
        "state": row["state"] or {},
        "started_at": row["started_at"].isoformat() if row["started_at"] else None,
        "completed_at": row["completed_at"].isoformat() if row["completed_at"] else None,
    }


@router.get("/api/cases/{case_id}/events")
async def list_case_events(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all case events ordered by created_at."""
    await _get_case_or_404(db, case_id, current_user)

    try:
        result = await db.execute(
            text("""
                SELECT id, case_id, event_type, node_name, data, created_at
                FROM taxlegal.case_events
                WHERE case_id = :case_id
                ORDER BY created_at ASC
            """),
            {"case_id": case_id},
        )
        rows = result.mappings().all()
    except Exception as e:
        logger.warning(f"case_events query error: {e}")
        return []

    return [
        {
            "id": str(r["id"]),
            "case_id": str(r["case_id"]),
            "event_type": r["event_type"],
            "node_name": r["node_name"],
            "data": r["data"] or {},
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
        }
        for r in rows
    ]


@router.get("/api/cases/{case_id}/versions")
async def list_case_versions(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List case versions from taxlegal.case_versions."""
    await _get_case_or_404(db, case_id, current_user)

    try:
        result = await db.execute(
            text("""
                SELECT id, case_id, version_number, snapshot, created_by, created_at
                FROM taxlegal.case_versions
                WHERE case_id = :case_id
                ORDER BY version_number ASC
            """),
            {"case_id": case_id},
        )
        rows = result.mappings().all()
    except Exception as e:
        logger.warning(f"case_versions query error: {e}")
        return []

    return [
        {
            "id": str(r["id"]),
            "case_id": str(r["case_id"]),
            "version_number": r["version_number"],
            "snapshot": r["snapshot"] or {},
            "created_by": r["created_by"],
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
        }
        for r in rows
    ]


@router.post("/api/cases/{case_id}/human-approval")
async def submit_human_approval(
    case_id: str,
    req: HumanApprovalDecision,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a human approval decision for a case."""
    await _get_case_or_404(db, case_id, current_user)

    now = datetime.utcnow()
    decision = req.decision.lower()
    if decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="decision must be 'approved' or 'rejected'")

    # Update human_approvals row if it exists
    try:
        result = await db.execute(
            text("""
                UPDATE taxlegal.human_approvals
                SET decision = :decision,
                    notes = :notes,
                    decided_by = :decided_by,
                    decided_at = :now,
                    updated_at = :now
                WHERE case_id = :case_id AND decision IS NULL
                RETURNING id
            """),
            {
                "decision": decision,
                "notes": req.notes,
                "decided_by": current_user.id,
                "now": now,
                "case_id": case_id,
            },
        )
        updated = result.rowcount
    except Exception as e:
        logger.warning(f"human_approvals update failed: {e}")
        updated = 0

    if not updated:
        # Insert a new record if none pending
        approval_id = str(uuid.uuid4())
        try:
            await db.execute(
                text("""
                    INSERT INTO taxlegal.human_approvals
                        (id, case_id, decision, notes, decided_by, decided_at, created_at, updated_at)
                    VALUES
                        (:id, :case_id, :decision, :notes, :decided_by, :now, :now, :now)
                """),
                {
                    "id": approval_id,
                    "case_id": case_id,
                    "decision": decision,
                    "notes": req.notes,
                    "decided_by": current_user.id,
                    "now": now,
                },
            )
        except Exception as e:
            logger.warning(f"human_approvals insert failed: {e}")

    # Try to signal Temporal workflow (graceful fail)
    try:
        from temporalio.client import Client as TemporalClient  # noqa: F401
        logger.info(f"Would signal Temporal workflow for case {case_id} with decision {decision}")
        # In production: await temporal_client.get_workflow_handle(case_id).signal(...)
    except Exception as e:
        logger.warning(f"Temporal signal skipped (not available): {e}")

    # Update case status based on decision
    # 'approved' → 'delivered' (fully approved, output ready)
    # 'rejected' → 'failed'
    new_status = "delivered" if decision == "approved" else "failed"
    try:
        await db.execute(
            text("UPDATE taxlegal.cases SET status = :status, updated_at = :now WHERE id = :id"),
            {"status": new_status, "now": now, "id": case_id},
        )
    except Exception as e:
        logger.warning(f"Could not update case status after approval: {e}")

    # Record event
    event_id = str(uuid.uuid4())
    try:
        await db.execute(
            text("""
                INSERT INTO taxlegal.case_events
                    (id, case_id, event_type, node_name, data, created_at)
                VALUES
                    (:id, :case_id, 'human_approval_decision', 'human_approval', :data::jsonb, :now)
            """),
            {
                "id": event_id,
                "case_id": case_id,
                "data": json.dumps({"decision": decision, "notes": req.notes}),
                "user_id": current_user.id,
                "now": now,
            },
        )
    except Exception as e:
        logger.warning(f"Could not create approval event: {e}")

    await db.commit()

    return {
        "case_id": case_id,
        "decision": decision,
        "notes": req.notes,
        "decided_by": current_user.id,
        "decided_at": now.isoformat(),
        "case_status": new_status,  # 'delivered' if approved, 'failed' if rejected
    }


@router.get("/api/cases/{case_id}/final")
async def get_final_output(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the final output for a completed case."""
    from fastapi.responses import JSONResponse
    case = await _get_case_or_404(db, case_id, current_user)

    current_status = case.get("status")

    # Status gate: only return final output if the case is delivered
    if current_status != "delivered":
        return JSONResponse(
            status_code=202,
            content={
                "status": "not_ready",
                "message": "Workflow chưa hoàn tất",
                "current_status": current_status,
            },
        )

    final_output = case.get("final_output")
    return {
        "case_id": case_id,
        "status": current_status,
        "final_output": final_output,
    }


# ── Background helpers ─────────────────────────────────────────────────────────

async def _log_case_event(
    case_id: str,
    event_type: str,
    node_name: str,
    data: dict,
    db,
) -> None:
    """Insert a case_event audit record. Non-fatal — wrapped in try/except."""
    try:
        await db.execute(
            text("""
                INSERT INTO taxlegal.case_events (id, case_id, event_type, node_name, data, created_at)
                VALUES (gen_random_uuid(), :case_id, :event_type, :node, :data::jsonb, NOW())
            """),
            {
                "case_id": case_id,
                "event_type": event_type,
                "node": node_name,
                "data": json.dumps(data),
            },
        )
        await db.commit()
    except Exception as e:
        logger.debug(f"_log_case_event failed (table may not exist yet): {e}")


async def _run_legacy_pipeline_bg(case_id: str, model_override: Optional[str] = None):
    """Run legacy pipeline in background for a case."""
    from backend.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        # Look up case
        try:
            result = await db.execute(
                text("SELECT id, matter_id FROM taxlegal.cases WHERE id = :id"),
                {"id": case_id},
            )
            row = result.mappings().one_or_none()
            if not row:
                logger.warning(f"Case {case_id} not found for legacy pipeline")
                return
        except Exception as e:
            logger.error(f"Legacy pipeline: case lookup failed for {case_id}: {e}")
            return

        logger.info(f"Legacy pipeline started for case {case_id}")

        # Import pipeline lazily
        try:
            from backend.agents.pipeline import execute_pipeline_step
        except ImportError as e:
            logger.warning(f"Could not import pipeline: {e}")
            await _log_case_event(case_id, "pipeline_error", "import",
                                  {"error": str(e)}, db)
            return

        # Run all 7 steps
        final_output = None
        run_failed = False
        for step_number in range(1, 8):
            step_info_map = {
                1: "intake", 2: "partner_p1", 3: "sa_blueprint",
                4: "ja_research", 5: "sa_review", 6: "partner_p2", 7: "partner_p3",
            }
            node_name = step_info_map.get(step_number, f"step_{step_number}")
            try:
                # Retrieve matter_id from case row
                matter_id = row.get("matter_id")
                if not matter_id:
                    logger.warning(f"Case {case_id} has no matter_id — cannot run legacy pipeline")
                    run_failed = True
                    break

                step = await execute_pipeline_step(
                    db=db,
                    matter_id=matter_id,
                    step_number=step_number,
                    model_override=model_override,
                )

                # Log step completion event
                await _log_case_event(
                    case_id,
                    "step_completed",
                    node_name,
                    {
                        "step_number": step_number,
                        "step_name": node_name,
                        "status": step.status if step else "unknown",
                        "word_count": step.word_count if step else 0,
                    },
                    db,
                )

                # Capture final output from step 7
                if step_number == 7 and step:
                    final_output = step.output_markdown

            except Exception as e:
                logger.error(f"Legacy pipeline step {step_number} failed for case {case_id}: {e}")
                await _log_case_event(
                    case_id,
                    "step_failed",
                    node_name,
                    {"step_number": step_number, "error": str(e)},
                    db,
                )
                run_failed = True
                break

        # Update case and workflow_run status
        final_case_status = "failed" if run_failed else "delivered"
        now = __import__('datetime').datetime.utcnow()

        try:
            update_params: dict = {"status": final_case_status, "now": now, "id": case_id}
            if final_output and not run_failed:
                await db.execute(
                    text("UPDATE taxlegal.cases SET status = :status, final_output = :final_output, updated_at = :now WHERE id = :id"),
                    {"status": final_case_status, "final_output": final_output, "now": now, "id": case_id},
                )
            else:
                await db.execute(
                    text("UPDATE taxlegal.cases SET status = :status, updated_at = :now WHERE id = :id"),
                    update_params,
                )
            await db.commit()
        except Exception as e:
            logger.error(f"Could not update case status after pipeline: {e}")

        # Update workflow_run status
        wr_status = "failed" if run_failed else "completed"
        try:
            await db.execute(
                text("""
                    UPDATE taxlegal.workflow_runs
                    SET status = :status, completed_at = :now
                    WHERE case_id = :case_id
                """),
                {"status": wr_status, "now": now, "case_id": case_id},
            )
            await db.commit()
        except Exception as e:
            logger.debug(f"workflow_runs update failed (non-fatal): {e}")

        # Log pipeline completion event
        await _log_case_event(
            case_id,
            "pipeline_completed" if not run_failed else "pipeline_failed",
            "legacy_pipeline",
            {"status": final_case_status, "steps_run": 7 if not run_failed else "partial"},
            db,
        )

        logger.info(f"Legacy pipeline {'completed' if not run_failed else 'FAILED'} for case {case_id}")
