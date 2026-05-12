# BRIEF: Fix Pipeline Draft + Missing Tax Types in TaxLegal

**Date:** 2026-05-12
**Priority:** CRITICAL — Pipeline hoàn toàn không hoạt động
**Repo:** `phanvuhoang/taxlegal`

---

## Issue 1: Pipeline luôn stuck ở "Draft" dù chọn Manual hay Auto

### Root Cause

**`taxlegal.law_documents_v2` table DOES NOT EXIST.** Code reference table này khắp nơi nhưng chưa bao giờ được tạo.

**Chain of failure:**
1. User tạo Matter → status = "draft" → background task `_run_step_bg` chạy step 1 (intake)
2. `execute_pipeline_step` → tạo PipelineStep + set matter.status = "intake" → flush (chưa commit)
3. `run_intake_step` → gọi `query_internal_db` → tries to query `taxlegal.law_documents_v2` → **SQL ERROR: relation does not exist**
4. PostgreSQL marks the transaction as **ABORTED** (InFailedSQLTransactionError)
5. AI call (DeepSeek) vẫn chạy và thành công (200 OK)
6. Sau AI call, code tries to `db.commit()` → **FAILS** vì transaction đã bị abort
7. `except` block tries to set status="failed" + commit → **FAILS AGAIN** (transaction still aborted)
8. Transaction rollback → **matter status reverts to "draft"**, PipelineStep record bị xóa

**Evidence from logs:**
```
05:44:15,193 WARNING — FTS query on law_documents_v2 failed: relation does not exist
05:44:15,194 WARNING — ILIKE query on law_documents_v2 failed: InFailedSQLTransactionError
05:44:42,512 INFO — DeepSeek API call 200 OK
05:46:37,043 ERROR — Pipeline step 1 failed: InFailedSQLTransactionError
```

### Fix Required

#### Fix 1a: Create `taxlegal.law_documents_v2` table

Run on DB container (`i11456c94loppyu9vzmgyb44`):

```sql
CREATE TABLE IF NOT EXISTS taxlegal.law_documents_v2 (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    doc_number VARCHAR(200),
    doc_type VARCHAR(50),
    issuer VARCHAR(200),
    issued_date VARCHAR(30),
    effective_date VARCHAR(30),
    source_url TEXT,
    tags TEXT[] DEFAULT '{}',
    tax_types TEXT[] DEFAULT '{}',
    is_priority BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    ai_tagged BOOLEAN DEFAULT FALSE,
    imported_from VARCHAR(50),
    dbvntax_id INTEGER,
    content_html TEXT,
    content_text TEXT,
    effective_status VARCHAR(50) DEFAULT 'con_hieu_luc',
    importance SMALLINT DEFAULT 4,
    created_by INTEGER REFERENCES taxlegal.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_law_docs_v2_type ON taxlegal.law_documents_v2(doc_type);
CREATE INDEX IF NOT EXISTS idx_law_docs_v2_priority ON taxlegal.law_documents_v2(is_priority);
CREATE INDEX IF NOT EXISTS idx_law_docs_v2_active ON taxlegal.law_documents_v2(is_active);
CREATE INDEX IF NOT EXISTS idx_law_docs_v2_dbvntax_id ON taxlegal.law_documents_v2(dbvntax_id);
CREATE INDEX IF NOT EXISTS idx_law_docs_v2_title ON taxlegal.law_documents_v2 USING gin(to_tsvector('simple', title));
CREATE INDEX IF NOT EXISTS idx_law_docs_v2_tax_types ON taxlegal.law_documents_v2 USING gin(tax_types);
```

**Add to `backend/models.py`** (or create in `backend/models_v4.py` based on app conventions):

```python
class LawDocumentV2(Base):
    __tablename__ = "law_documents_v2"
    __table_args__ = {"schema": "taxlegal"}

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    doc_number = Column(String(200))
    doc_type = Column(String(50))
    issuer = Column(String(200))
    issued_date = Column(String(30))
    effective_date = Column(String(30))
    source_url = Column(Text)
    tags = Column(ARRAY(Text), default=list)
    tax_types = Column(ARRAY(Text), default=list)
    is_priority = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    ai_tagged = Column(Boolean, default=False)
    imported_from = Column(String(50))
    dbvntax_id = Column(Integer)
    content_html = Column(Text)
    content_text = Column(Text)
    effective_status = Column(String(50), default="con_hieu_luc")
    importance = Column(SmallInteger, default=4)
    created_by = Column(Integer, ForeignKey("taxlegal.users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

#### Fix 1b: Add error resilience in `backend/retrieval/service.py`

The current code lets SQL errors abort the entire transaction. Add rollback on error:

In `query_internal_db` function (lines ~280-380 in `service.py`), wrap each query attempt in try/except with explicit rollback:

```python
# Before each query attempt:
try:
    # Try query on law_documents_v2
    ...
except Exception as e:
    logger.warning(f"Query on law_documents_v2 failed: {e}")
    await db.rollback()  # CRITICAL: prevent InFailedSQLTransactionError
    # Fall through to next query method
```

Apply this pattern to ALL fallback queries in the function. This is the root fix for the cascading pipeline failure.

#### Fix 1c: Add rollback in `execute_pipeline_step` except block

In `backend/agents/pipeline.py`, the except block around line 698:

```python
except Exception as e:
    logger.error(f"Pipeline step {step_number} failed for matter {matter_id}: {e}")
    # CRITICAL: Rollback aborted transaction before trying to save error status
    await db.rollback()
    # Now set error state on a fresh transaction
    step.status = "failed"
    step.error_message = str(e)[:500]
    matter.status = MatterStatus.failed.value
    await db.commit()
    raise
```

---

## Issue 2: Thiếu sắc thuế trong dropdown "Import dbvntax"

### Current vs Required

**Database** (`SELECT DISTINCT unnest(sac_thue) FROM documents`):
```
FCT, GDLK, GTGT, HKD, HOA_DON, QLT, THUE_QT, TNCN, TNDN, TTDB, XNK
```

**Frontend dropdown hiện tại** (6 items):
| Value | Label |
|-------|-------|
| GTGT | Thuế GTGT |
| TNDN | Thuế TNDN |
| TNCN | Thuế TNCN |
| FCT | Nhà thầu nước ngoài |
| TTDB | Thuế TTDB |
| XNK | Thuế XNK / Hải quan |

**Cần thêm** (5 items):
| Value | Label |
|-------|-------|
| HKD | Hộ Kinh Doanh |
| HOA_DON | Hóa đơn |
| QLT | Quản Lý Thuế |
| THUE_QT | Thuế Quốc Tế |
| GDLK | Giao dịch liên kết / Chuyển giá |

### Fix

**File:** `frontend/src/pages/AdminLawDocuments.tsx`, ~lines 36-43

Replace SAC_THUE_OPTIONS:

```tsx
const SAC_THUE_OPTIONS = [
  { value: "", label: "Tất cả sắc thuế" },
  { value: "GTGT", label: "Thuế GTGT" },
  { value: "TNDN", label: "Thuế TNDN" },
  { value: "TNCN", label: "Thuế TNCN" },
  { value: "FCT", label: "Nhà thầu nước ngoài" },
  { value: "TTDB", label: "Thuế TTDB" },
  { value: "XNK", label: "Thuế XNK / Hải quan" },
  { value: "HKD", label: "Hộ Kinh Doanh" },
  { value: "HOA_DON", label: "Hóa đơn" },
  { value: "QLT", label: "Quản Lý Thuế" },
  { value: "THUE_QT", label: "Thuế Quốc Tế" },
  { value: "GDLK", label: "Giao dịch liên kết" },
];
```

**(Optional)** Nếu muốn đồng bộ tự động từ DB, thay vì hardcode, lấy danh sách qua API:
```
GET /api/admin/sac-thue/list → returns DISTINCT unnest(sac_thue) FROM documents
```

---

## Summary of All Changes

| File | Change | Priority |
|------|--------|----------|
| **DB Migration** | Create `taxlegal.law_documents_v2` table | CRITICAL |
| `backend/models.py` or `models_v4.py` | Add `LawDocumentV2` model class | CRITICAL |
| `backend/retrieval/service.py` | Add `await db.rollback()` after each failed query | CRITICAL |
| `backend/agents/pipeline.py` | Add `await db.rollback()` before commit in except block | CRITICAL |
| `frontend/.../AdminLawDocuments.tsx` | Add 5 missing sac_thue options | HIGH |

---

## Expected Behavior After Fix

1. Tạo Matter → status chuyển từ "draft" → "intake" → chạy intake enhancer
2. Pipeline steps được lưu trong `pipeline_steps` table
3. Auto mode: steps tự động approve và continue
4. Manual mode: steps chờ user approve
5. Tab "Import dbvntax": hiển thị đủ 11 loại sắc thuế để lọc

---

## Files to Modify (detailed)

1. **`backend/retrieval/service.py`** — add rollback on every fallback query failure (~5 locations)
2. **`backend/agents/pipeline.py`** — add rollback in except block (~line 698)
3. **`backend/models.py`** — add `LawDocumentV2` class (~after line 317)
4. **`frontend/src/pages/AdminLawDocuments.tsx`** — update SAC_THUE_OPTIONS (~line 36)

## Database Migration

Run on VPS via:
```bash
docker exec i11456c94loppyu9vzmgyb44 psql -U legaldb_user -d taxlegal -c "...CREATE TABLE..."
```

After migration, restart taxlegal container for model registration.
