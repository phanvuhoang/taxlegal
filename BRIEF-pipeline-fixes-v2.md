# BRIEF: Fix Pipeline — Greenlet Bug + Background + Stop/Resume

**Date:** 2026-05-13  
**Status:** For Claude Code implementation  
**Priority:** CRITICAL — pipeline stuck at step 4

---

## Tổng quan

Pipeline Module 1 có 3 vấn đề cần fix:

| # | Vấn đề | Mức độ |
|---|--------|--------|
| 1 | Step 4 (JA Research) luôn fail với `MissingGreenlet` | CRITICAL |
| 2 | Background tasks mất khi close tab hoặc worker restart | HIGH |
| 3 | Không có nút stop/resume pipeline | MEDIUM |

---

## Vấn đề 1: MissingGreenlet ở Step 4

### Root Cause

SQLAlchemy async engine dùng `greenlet` để bridge async-to-sync. Trong background task (BackgroundTasks của FastAPI), greenlet bridge bị timeout khi có gap dài giữa các DB operation.

**Steps 1-3 chạy OK** vì mỗi step là 1 chu kỳ ngắn:
```
retrieve (optional) → AI call (~10s) → DB write → commit → done
```
Greenlet bridge sống đủ lâu trong ~15-20 giây.

**Step 4 fail** vì có LOOP 6 chunks, mỗi chunk:
```
retrieve → AI call (~24s) → DB write(chunk) → next iteration
```
Khoảng cách 24s giữa `db.flush()` chunk 1 và `retrieve` chunk 2 → greenlet bridge đã timeout → `await_only()` throw `MissingGreenlet`.

**Steps 5-7 an toàn** (không dùng retrieval service, chỉ AI call).

### Giải pháp khuyến nghị: Run pipeline steps synchronously trong event loop

Thay vì chạy step trong BackgroundTasks, chạy TRỰC TIẾP trong request handler. Request handler có event loop chính → greenlet hoạt động bình thường.

**Cách làm:**

```python
# File: backend/routes/matters.py

# 1. Xoá _run_step_bg hoàn toàn
# 2. Sửa approve_step để chạy step tiếp theo INLINE:

@router.post("/{matter_id}/approve-step/{step_number}")
async def approve_step(
    matter_id: int,
    step_number: int,
    body: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    matter = await _get_matter_or_404(db, matter_id, current_user)
    await approve_pipeline_step(db, matter_id, step_number)  # existing

    next_step = step_number + 1
    if next_step <= 7:
        # Chạy step trực tiếp trong request handler (DÙNG DB session của request)
        step = await execute_pipeline_step(db, matter_id, next_step, None)
        
        # Auto-advance nếu auto mode
        if matter.pipeline_mode == "auto" and next_step < 7 and step.status == "waiting":
            # Không chain ở đây — frontend poll và tự gọi lại
            pass
        
        return {"message": f"Step {next_step} completed", "status": step.status}
    
    return {"message": "Pipeline completed!"}
```

**Trade-off:** Client phải chờ response lâu hơn (30-180s cho step 4). Nhưng pipeline chạy ổn định, không lỗi greenlet.

**Để tránh timeout:** Trả về ngay response "triggered", rồi chạy step trong `asyncio.create_task()` NHƯNG dùng cùng DB session của request (không tạo session mới):

```python
# APPROACH: Copy connection, use in task
# Tại đầu approve_step:
conn = await db.connection()  # lấy raw async connection
# Trong task:
async def run_with_conn(conn, matter_id, step_number):
    async with AsyncSession(bind=conn) as task_db:
        await execute_pipeline_step(task_db, matter_id, step_number, None)

asyncio.create_task(run_with_conn(conn, matter_id, next_step))
```

Nhưng cái này phức tạp. Đơn giản nhất: **chạy sync trong request, set client timeout dài**.

### Giải pháp thay thế: BGE-M3 retrieval ASYNC without DB logging

Nếu không muốn chạy sync, có thể bỏ qua `_log_retrieval_query` trong step 4 (vì đó là step DUY NHẤT gây greenlet). Nhưng đây là workaround tạm thời.

---

## Vấn đề 2: Background execution survives tab close

### Hiện trạng
- Pipeline steps chạy qua `BackgroundTasks.add_task()` — chạy SAU KHI response gửi đi
- Task die nếu: Uvicorn worker restart, container restart, hoặc process kill
- Khi close tab → browser ngừng polling → user không biết step đã fail hay chưa

### Yêu cầu
- **Auto mode:** Close tab → pipeline tiếp tục chạy đến step 7
- **Manual mode:** Step đang chạy → hoàn thành rồi dừng (chờ approve), kể cả khi close tab

### Giải pháp: DB-backed Job Queue + Background Worker

**Thêm bảng `pipeline_jobs`:**

```sql
CREATE TABLE taxlegal.pipeline_jobs (
    id SERIAL PRIMARY KEY,
    matter_id INTEGER NOT NULL REFERENCES taxlegal.matters(id),
    step_number INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, running, completed, failed, paused
    model_override VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3
);
CREATE INDEX idx_pipeline_jobs_status ON taxlegal.pipeline_jobs(status);
CREATE INDEX idx_pipeline_jobs_matter ON taxlegal.pipeline_jobs(matter_id);
```

**Background Worker (chạy trong FastAPI lifespan):**

```python
# File mới: backend/workers/pipeline_worker.py

import asyncio
import logging
from backend.database import AsyncSessionLocal
from backend.models import PipelineJob, Matter
from backend.agents.pipeline import execute_pipeline_step
from sqlalchemy import select

logger = logging.getLogger(__name__)

async def pipeline_worker_loop():
    """Poll pipeline_jobs table, execute pending jobs."""
    while True:
        try:
            async with AsyncSessionLocal() as db:
                # Find next pending job
                result = await db.execute(
                    select(PipelineJob)
                    .where(PipelineJob.status == 'pending')
                    .order_by(PipelineJob.created_at)
                    .limit(1)
                )
                job = result.scalar_one_or_none()
                
                if job:
                    job.status = 'running'
                    job.started_at = datetime.utcnow()
                    await db.commit()
                    
                    try:
                        step = await execute_pipeline_step(
                            db, job.matter_id, job.step_number, job.model_override
                        )
                        job.status = 'completed'
                        job.completed_at = datetime.utcnow()
                        await db.commit()
                        
                        # Auto-advance: check if auto mode
                        matter_result = await db.execute(
                            select(Matter).where(Matter.id == job.matter_id)
                        )
                        matter = matter_result.scalar_one_or_none()
                        if (matter and matter.pipeline_mode == 'auto' 
                            and job.step_number < 7 and step.status == 'waiting'):
                            # Queue next step
                            next_job = PipelineJob(
                                matter_id=job.matter_id,
                                step_number=job.step_number + 1,
                                status='pending'
                            )
                            db.add(next_job)
                            await db.commit()
                            
                    except Exception as e:
                        job.status = 'failed'
                        job.error_message = str(e)[:500]
                        job.retry_count += 1
                        if job.retry_count < job.max_retries:
                            job.status = 'pending'  # retry
                        await db.commit()
                        logger.error(f"Job {job.id} failed: {e}")
        except Exception as e:
            logger.error(f"Pipeline worker error: {e}")
        
        await asyncio.sleep(2)  # Poll every 2 seconds
```

**Start worker in lifespan:**

```python
# File: main.py — trong lifespan()
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing startup ...
    
    # Start pipeline background worker
    worker_task = asyncio.create_task(pipeline_worker_loop())
    
    yield
    
    # Shutdown
    worker_task.cancel()
```

**Sửa routes để queue job thay vì chạy trực tiếp:**

```python
# File: backend/routes/matters.py

@router.post("/{matter_id}/approve-step/{step_number}")
async def approve_step(matter_id, step_number, body, db=Depends(get_db), ...):
    matter = await _get_matter_or_404(db, matter_id, current_user)
    
    # Approve current step
    await approve_pipeline_step(db, matter_id, step_number)
    
    next_step = step_number + 1
    if next_step <= 7:
        # Queue job instead of running directly
        job = PipelineJob(
            matter_id=matter_id,
            step_number=next_step,
            model_override=body.get("model_override"),
            status='pending'
        )
        db.add(job)
        await db.commit()
        return {"message": f"Step {next_step} queued", "job_id": job.id}
    
    return {"message": "Pipeline completed!"}


@router.post("/")
async def create_matter(req, db=Depends(get_db), ...):
    # Create matter
    ...
    # Queue step 1
    job = PipelineJob(matter_id=matter.id, step_number=1, status='pending')
    db.add(job)
    await db.commit()
    return {"id": matter.id, "status": "queued"}
```

**Frontend polling:**
- Frontend gọi `GET /api/matters/{id}` mỗi 3-5 giây để check status
- Khi status thay đổi → update UI
- Khi step status = "waiting" (manual) → hiện nút Approve
- Khi step status = "completed" (step 7) → hiện final output
- UI nên có indicator "⏳ Processing..." khi pipeline_jobs có status=running

---

## Vấn đề 3: Stop & Resume Pipeline

### Yêu cầu
- Nút **Stop** trên UI để pause pipeline đang chạy
- Nút **Resume** để tiếp tục
- Hoạt động cho cả auto và manual mode

### Giải pháp: Thêm trường `pipeline_action` vào Matter

```sql
ALTER TABLE taxlegal.matters ADD COLUMN pipeline_action VARCHAR(20) DEFAULT NULL;
-- NULL = normal, 'pause' = pause after current step, 'resume' = continue
```

**Sửa background worker:**

```python
# Trong pipeline_worker_loop, trước khi execute step:
matter_result = await db.execute(
    select(Matter).where(Matter.id == job.matter_id)
)
matter = matter_result.scalar_one_or_none()
if matter and matter.pipeline_action == 'pause':
    job.status = 'paused'
    await db.commit()
    continue  # skip this job, check again later
```

**API endpoints:**

```python
# File: backend/routes/matters.py

@router.post("/{matter_id}/pause")
async def pause_pipeline(matter_id, db=Depends(get_db), ...):
    matter = await _get_matter_or_404(db, matter_id, current_user)
    matter.pipeline_action = 'pause'
    await db.commit()
    return {"message": "Pipeline sẽ pause sau step hiện tại"}

@router.post("/{matter_id}/resume")
async def resume_pipeline(matter_id, db=Depends(get_db), ...):
    matter = await _get_matter_or_404(db, matter_id, current_user)
    matter.pipeline_action = None
    await db.commit()
    
    # Re-queue current step nếu matter đang ở trạng thái chờ
    job = PipelineJob(
        matter_id=matter_id,
        step_number=matter.current_step + 1,
        status='pending'
    )
    db.add(job)
    await db.commit()
    return {"message": "Pipeline resumed"}
```

---

## Tối ưu tốc độ

### Các điểm có thể tăng tốc

1. **Step 4 (JA Research): Giảm số chunks hoặc xử lý song song**
   - Hiện tại: 6 chunks × sequential (retrieve + AI ~30s each) = ~3 phút
   - Có thể: giảm còn 3 chunks cho mode "quick", hoặc parallel 2 chunks cùng lúc
   - Thêm field `pipeline_speed` vào Matter: "standard" (6 chunks) | "fast" (3 chunks)

2. **Giảm max_tokens cho DeepSeek**
   - Hiện tại: max_tokens=8000 cho mỗi step
   - Có thể giảm còn 4000 cho step 2, 5, 6, 7 (các step đơn giản hơn)
   - Step 4 giữ 8000 (cần output dài)

3. **Cache system prompt**
   - System prompt được build mỗi lần gọi → cache trong memory/Redis
   - Tiết kiệm 1 DB query mỗi step

4. **Parallel law verification trong step 4**
   - Hiện tại: `verify_law_currency` chạy sequential cho từng law (trong loop)
   - Có thể: `asyncio.gather()` để verify 3 laws cùng lúc (15s → 5s)

5. **Switch model cho step nhẹ**
   - Step 2 (partner_p1): output ngắn → dùng haiku hoặc model rẻ hơn
   - Step 5, 6, 7: tương tự

---

## Implementation Plan

### Phase 1: Fix greenlet (unblock pipeline) ⚡
1. Xoá `_run_step_bg` và `_auto_approve_and_continue`
2. Sửa `approve_step` và `run_step_manual` để chạy step INLINE với DB session của request
3. Thêm timeout config cho client (frontend set timeout dài cho các request approve)
4. **File thay đổi:** `backend/routes/matters.py`

### Phase 2: Background worker (survive tab close) 🔄
1. Tạo bảng `pipeline_jobs` (thêm vào `backend/models.py` + migration)
2. Tạo `backend/workers/pipeline_worker.py`
3. Start worker trong `main.py` lifespan
4. Sửa routes để queue job thay vì chạy trực tiếp
5. **File thay đổi:** `backend/models.py`, `backend/workers/pipeline_worker.py`, `main.py`, `backend/routes/matters.py`

### Phase 3: Stop/Resume ⏯️
1. Thêm `pipeline_action` vào Matter model
2. Thêm endpoints `/{id}/pause` và `/{id}/resume`
3. Sửa worker để check `pipeline_action`
4. **File thay đổi:** `backend/models.py`, `backend/routes/matters.py`, `backend/workers/pipeline_worker.py`

### Phase 4: Tối ưu tốc độ 🚀
1. Cache system prompt
2. Parallel law verification
3. Configurable chunk count
4. Giảm max_tokens cho step nhẹ

---

## Verification Checklist

Sau khi implement mỗi phase:

**Phase 1:**
- [ ] Tạo matter mới → step 1 chạy OK
- [ ] Approve step 1 → step 2 chạy OK
- [ ] Approve step 2 → step 3 chạy OK
- [ ] Approve step 3 → step 4 chạy OK (KHÔNG greenlet error!)
- [ ] Approve step 4 → step 5 chạy OK
- [ ] Approve step 5 → step 6 chạy OK
- [ ] Approve step 6 → step 7 chạy OK → final output generated
- [ ] Auto mode: tạo matter → tự chạy step 1→2→3 (step 4 manual trigger vì auto bị greenlet trước đây)

**Phase 2:**
- [ ] Tạo matter auto mode → close tab → mở lại → pipeline đã chạy xong
- [ ] Container restart → pipeline_jobs pending vẫn còn → worker pick up và chạy
- [ ] Manual mode: approve step → close tab → mở lại → step completed, thấy nút Approve

**Phase 3:**
- [ ] Đang chạy step 4 → bấm Pause → step hiện tại hoàn thành → dừng
- [ ] Bấm Resume → step tiếp theo chạy
- [ ] Pause trong auto mode → không auto-advance → Resume → tiếp tục auto

---

## Files hiện tại cần biết

| File | Vai trò |
|------|---------|
| `backend/routes/matters.py` | API endpoints — create, approve, run-step |
| `backend/agents/pipeline.py` | execute_pipeline_step, 7 step functions, auto-approve |
| `backend/models.py` | Matter, PipelineStep, ResearchChunk models |
| `backend/database.py` | AsyncSessionLocal, engine |
| `backend/retrieval/service.py` | _retrieval_svc.retrieve(), _log_retrieval_query |
| `main.py` | FastAPI app, lifespan |

## Ghi chú

- Bug `_log_retrieval_query` (wrong column `web_results_count` → `results_summary`) **đã được fix** commit `56f8976` — không cần sửa lại
- `pool_pre_ping` đang để `True` (mặc định) — không cần đổi
- BackgroundTasks của FastAPI **vẫn dùng được** cho step 1-3 (single-cycle) — nhưng recommend chuyển hết qua DB job queue cho consistent
- Nếu muốn nhanh nhất: chỉ cần Phase 1 (fix greenlet) là pipeline chạy được ngay
