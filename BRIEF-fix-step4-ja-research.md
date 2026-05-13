# BRIEF: Fix Step 4 (JA Research) Pipeline Failure

**Date:** 2026-05-12  
**Status:** 1/3 bugs fixed, 2 remaining for Claude Code  
**Priority:** HIGH — blocks Module 1 pipeline beyond step 3

---

## Summary

Step 4 (JA Research — Jurisdictional Analysis) in Module 1 fails consistently. Steps 1-3 work fine. Steps 5-7 are NOT affected (different code path — no retrieval service calls).

**Root causes identified:**

| # | Bug | Status | Fix Location |
|---|-----|--------|--------------|
| 1 | `_log_retrieval_query` INSERT wrong column name | ✅ FIXED (commit 56f8976) | `backend/retrieval/service.py` |
| 2 | Missing `db.rollback()` in except block → cascading tx failure | ✅ FIXED (commit 56f8976) | `backend/retrieval/service.py` |
| 3 | Greenlet not spawned in background task context → MissingGreenlet | ⬜ FOR CLAUDE CODE | `backend/routes/matters.py` |

---

## Bug #1: Wrong Column in _log_retrieval_query INSERT (FIXED ✅)

### What happened
`_log_retrieval_query` tried to INSERT column `web_results_count` which doesn't exist in `retrieval_queries` table. The real table has `results_summary` (jsonb).

### Chain of failure
```
1. Step 4 starts → retrieve chunk 1 → _log_retrieval_query INSERT fails
   (column "web_results_count" doesn't exist)
2. PostgreSQL aborts the transaction → InFailedSQLTransactionError
3. Except block in _log_retrieval_query catches the error (DEBUG log only)
   BUT does NOT rollback → transaction stays aborted
4. call_ai() for chunk 1 SUCCEEDS (HTTP call, doesn't touch DB)
5. db.add(db_chunk) → ORM operation (no SQL yet)
6. Loop to chunk 2 → query_internal_db() → InFailedSQLTransactionError
   → caught with rollback → transaction reset
7. _log_retrieval_query for chunk 2 → same INSERT failure → abort again
8. ... repeats for all chunks ...
9. await db.flush() at end → InFailedSQLTransactionError → exception
10. execute_pipeline_step except block → sets status "failed"
11. PipelineStep record is rolled back (disappears from DB)
```

### Fix applied
```python
# OLD (BROKEN):
INSERT INTO taxlegal.retrieval_queries (
    ..., web_results_count, ...
) VALUES (
    ..., :web_results_count, ...
)

# NEW (FIXED):
INSERT INTO taxlegal.retrieval_queries (
    ..., results_summary, ...
) VALUES (
    ..., :results_summary, ...
)
# Where results_summary = json.dumps({"web_results_count": N, "total_results": M})

# Also added:
except Exception as e:
    logger.debug(...)
    try:
        await db.rollback()  # ← CRITICAL: prevent cascading tx failure
    except Exception:
        pass
```

---

## Bug #2: Missing Rollback in _log_retrieval_query (FIXED ✅)

The except block caught the error but didn't rollback, causing the PostgreSQL transaction to stay in aborted state. All subsequent DB operations fail with `InFailedSQLTransactionError`.

**Fix:** Added `await db.rollback()` in except block. Also added outer try/catch in `retrieve()` method as extra safety (commit 05ece78).

---

## Bug #3: Greenlet MissingGreenlet in Background Tasks (FOR CLAUDE CODE ⬜)

### What happens
After fixing bugs #1 and #2, step 4 still fails. The error is:
```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called;
can't call await_only() here.
```

Error chain (from traceback):
```
asyncpg execute → self._adapt_connection.await_()
→ sqlalchemy.util._concurrency_py3k.await_only()
→ MissingGreenlet: greenlet_spawn has not been called
```

### Why it happens
SQLAlchemy's async engine uses `greenlet` to bridge async-to-sync. The `greenlet_spawn()` function must be called before any `await_only()` calls. In FastAPI's `BackgroundTasks`, the async context may not properly initialize the greenlet bridge.

**Steps 1-3 work** because they do a SINGLE DB cycle (retrieve → AI call → commit) within the same greenlet window. The greenlet bridge is still active when commit runs.

**Step 4 fails** because it has a LOOP (6 chunks × retrieve → AI call → DB write). The first retrieve+AI works, but the greenlet bridge times out during the long AI call (~24s). When the next DB operation tries to execute, `await_only()` fails.

### The BackgroundTasks Mechanism
```python
# In routes/matters.py:
background_tasks.add_task(_run_step_bg, matter_id, step_number, ...)

# _run_step_bg creates its OWN session:
async with AsyncSessionLocal() as db:
    step = await execute_pipeline_step(db, matter_id, step_number, ...)
```

### Attempted fixes (all failed)
- ❌ `pool_pre_ping=False` — shifted error from do_ping to do_execute
- ❌ `asyncio.create_task()` — broke even step 1 (worse than BackgroundTasks)
- ❌ `asyncio.ensure_future()` — same as create_task

### Recommended Fix (Option A): Run pipeline in request handler context

Instead of spawning a background task, run the step WITHIN the request handler's DB session. The client triggers the step, and the server processes it in the same event loop where greenlet is properly initialized.

```python
# In routes/matters.py — run_step_manual:
@router.post("/{matter_id}/run-step/{step_number}")
async def run_step_manual(matter_id, step_number, body, db=Depends(get_db), ...):
    """Run step SYNCHRONOUSLY within request context."""
    model_override = body.get("model_override")
    
    # Execute inline (uses request handler's DB session)
    step = await execute_pipeline_step(db, matter_id, step_number, model_override)
    
    return {"message": f"Step {step_number} completed", "status": step.status}
```

**Pros:** No greenlet issues, uses existing working DB session  
**Cons:** Client waits for step completion (30-180 seconds depending on chunks/AI calls)  
**Mitigation:** Set longer timeout on client side, show loading indicator in UI

### Recommended Fix (Option B): Use sync SQLAlchemy engine

Replace async engine with sync engine + `asyncio.to_thread()`:

```python
# In backend/database.py:
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL, pool_pre_ping=True, ...)
SessionLocal = sessionmaker(engine)

# In _run_step_bg:
import asyncio

def _run_step_sync(matter_id, step_number, model_override):
    """Synchronous version runnable in thread."""
    db = SessionLocal()
    try:
        # Convert execute_pipeline_step to sync or use run_sync
        ...
    finally:
        db.close()

async def _run_step_bg(matter_id, step_number, model_override):
    await asyncio.to_thread(_run_step_sync, matter_id, step_number, model_override)
```

**Pros:** No greenlet dependency at all  
**Cons:** Major refactor of execute_pipeline_step and all step functions

### Recommended Fix (Option C): DB ping before each retrieval loop iteration

Add a quick "SELECT 1" before each retrieval in the loop to keep greenlet alive:

```python
# In run_ja_research_step, before each chunk:
await db.execute(text("SELECT 1"))  # Re-establish greenlet bridge
```

**Pros:** Minimal code change  
**Cons:** Not guaranteed to work (greenlet bridge might not reinitialize)

---

## Steps 5, 6, 7 — NO ISSUES ✅

Steps 5 (SA Review), 6 (Partner P2), 7 (Partner P3) do NOT use `_retrieval_svc.retrieve()`:

| Step | DB operations | Retrieval | Risk |
|------|--------------|-----------|------|
| 5 — SA Review | Read PipelineStep (async) | No | ✅ Safe |
| 6 — Partner P2 | Read PipelineStep (async) | No | ✅ Safe |
| 7 — Partner P3 | Read PipelineStep (async) | No | ✅ Safe |

They only do DB reads + AI calls + DB writes (handled by execute_pipeline_step's generic code). They follow the same safe pattern as steps 1-3.

---

## Implementation Priority

1. **Fix Bug #3 (greenlet)** — blocks step 4
   - Recommendation: **Option A** (run inline in request handler)
   - Fallback: **Option C** (DB ping before each loop)
   
2. **Test full pipeline** (steps 1→7) after fix
   - Create new matter → approve each step → verify final output

---

## Verification Checklist

After implementing fix for Bug #3:
- [ ] matter 7: approve step 3 → step 4 runs → status "waiting" (not "failed")
- [ ] matter 7: approve step 4 → step 5 runs → verify SA review output
- [ ] matter 7: approve steps 5, 6, 7 → final content generated
- [ ] New matter: auto-create → step 1 completes → approve → full pipeline to step 7
