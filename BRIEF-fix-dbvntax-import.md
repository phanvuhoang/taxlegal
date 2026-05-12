# BRIEF: Fix taxlegal "Import dbvntax" — Multiple Bugs

**Date:** 2026-05-12
**Priority:** HIGH — feature hoàn toàn không hoạt động
**Repo:** `phanvuhoang/taxlegal`
**Target:** Fix để admin có thể import văn bản từ dbvntax vào taxlegal

---

## Database Layout (for context)

| Container | DB | Schema | Table | Rows | Purpose |
|-----------|-----|--------|-------|------|---------|
| `i11456c94loppyu9vzmgyb44` (pgvector:pg16) | `postgres` | `public` | `documents` | **186** | dbvntax store — SOURCE of truth |
| Same | `taxlegal` | `taxlegal` | `law_documents` | 0 | taxlegal local cache — TARGET for import |

### dbvntax.documents columns (relevant)
```sql
id, so_hieu, ten, loai, co_quan, ngay_ban_hanh, hieu_luc_tu, tinh_trang,
noi_dung, link_tvpl, sac_thue TEXT[], importance SMALLINT, is_anchor BOOLEAN
```
- `loai` values are CODES: `Luat, ND, TT, VBHN, QD, NQ, Khac` (NOT Vietnamese names)

### taxlegal.law_documents columns (target table)
```sql
id, so_hieu, ten, loai, co_quan, ngay_ban_hanh, hieu_luc_tu, het_hieu_luc_tu,
tinh_trang, replaced_by, practice_areas TEXT[], content_text, link_tvpl,
dbvntax_id, source, created_at, updated_at
```
- `dbvntax_id` tracks imported docs (no unique constraint)
- `source` = `'manual'` by default, should be `'dbvntax_sync'` for imports

---

## Bug 1: `_DBVNTAX_LEGAL_TYPES` uses Vietnamese names that don't match dbvntax codes

**File:** `backend/routes/laws_admin.py` ~line 359-362
**Impact:** This is used in the WHERE clause to filter docs. Since names don't match, **0 documents are returned**.

```python
# CURRENT (WRONG — 0 matches):
_DBVNTAX_LEGAL_TYPES = [
    'Luật', 'Nghị định', 'Thông tư', 'Thông tư liên tịch',
    'Văn bản hợp nhất', 'Pháp lệnh', 'Nghị quyết', 'Quyết định'
]
# SQL: loai = ANY(ARRAY['Luật', 'Nghị định', ...]::varchar[])
# Result: 0 rows ❌

# FIX (CORRECT — 186 matches):
_DBVNTAX_LEGAL_TYPES = ['Luat', 'ND', 'TT', 'VBHN', 'QD', 'NQ', 'Khac']
# SQL: loai = ANY(ARRAY['Luat','ND','TT','VBHN','QD','NQ','Khac']::varchar[])
# Result: 186 rows ✅
```

**Verified via psql:**
```sql
-- Wrong (returns 0):
SELECT COUNT(*) FROM documents WHERE loai = ANY(ARRAY['Luật','Nghị định','Thông tư']::varchar[]);
-- count: 0

-- Correct (returns 186):
SELECT COUNT(*) FROM documents WHERE loai = ANY(ARRAY['Luat','ND','TT','VBHN','QD','NQ','Khac']::varchar[]);
-- count: 186
```

---

## Bug 2: Frontend dropdown + backend ILIKE filter also mismatched

**File:** `frontend/src/pages/AdminLawDocuments.tsx` ~lines 460-475 (dbDocType dropdown) AND `backend/routes/laws_admin.py` ~line 402 (ILIKE filter)

The frontend sends Vietnamese names (e.g., `Luật`) but backend does `loai ILIKE '%Luật%'` against db codes like `Luat`. ILIKE with accents won't match without accent.

### Fix — Add a mapping dict in the backend:

```python
# In backend/routes/laws_admin.py, add:
_DBVNTAX_LOAI_MAP = {
    'Luật': 'Luat',
    'Nghị định': 'ND',
    'Thông tư': 'TT',
    'Thông tư liên tịch': 'TT',
    'Văn bản hợp nhất': 'VBHN',
    'Nghị quyết': 'NQ',
    'Quyết định': 'QD',
    'Khác': 'Khac',
}
```

Then in the `list_dbvntax_documents` function, change the doc_type filter:
```python
# CURRENT (doesn't work):
if doc_type:
    params.append(f"%{doc_type}%")
    conditions.append(f"loai ILIKE ${len(params)}")

# FIX:
if doc_type:
    mapped = _DBVNTAX_LOAI_MAP.get(doc_type)
    if mapped:
        conditions.append(f"loai = '{mapped}'")
```

**ALTERNATIVELY** (simpler): Change the frontend dropdown to use codes instead of names:
```tsx
// CURRENT:
<option value="Luật">Luật</option>
// FIX:
<option value="Luat">Luật</option>
<option value="ND">Nghị định</option>
<option value="TT">Thông tư</option>
<option value="VBHN">Văn bản hợp nhất</option>
<option value="QD">Quyết định</option>
<option value="NQ">Nghị quyết</option>
<option value="Khac">Khác</option>
```

Then the backend doc_type filter becomes exact match:
```python
if doc_type:
    conditions.append(f"loai = '{doc_type}'")
```
(This is simpler and avoids mappings entirely — recommended approach)

---

## Bug 3: Import inserts into wrong table `taxlegal.law_documents_v2`

**File:** `backend/routes/laws_admin.py` ~lines 576-583
**Impact:** The table `taxlegal.law_documents_v2` **does not exist**. Import would fail with "relation does not exist".

The actual table is `taxlegal.law_documents`.

### Fix: Change table name AND column mapping

```python
# CURRENT (WRONG — table doesn't exist):
INSERT INTO taxlegal.law_documents_v2
    (title, doc_number, doc_type, issuer, issued_date,
     content_html, content_text, is_priority, importance,
     tax_types, link_tvpl, effective_status,
     imported_from, dbvntax_id, created_by)
VALUES (...)

# FIX (match actual table schema):
INSERT INTO taxlegal.law_documents
    (ten, so_hieu, loai, co_quan, ngay_ban_hanh,
     hieu_luc_tu, tinh_trang,
     practice_areas, content_text, link_tvpl,
     dbvntax_id, source)
VALUES (:ten, :so_hieu, :loai, :co_quan, :ngay_ban_hanh,
        :hieu_luc_tu, :tinh_trang,
        :practice_areas, :content_text, :link_tvpl,
        :dbvntax_id, 'dbvntax_sync')
```

And update the params dict:
```python
{
    "ten": row.get("ten") or "Untitled",
    "so_hieu": row.get("so_hieu"),
    "loai": row.get("loai"),  # use original code: Luat, ND, TT, etc.
    "co_quan": row.get("co_quan"),
    "ngay_ban_hanh": str(row.get("ngay_ban_hanh")) if row.get("ngay_ban_hanh") else None,
    "hieu_luc_tu": str(row.get("hieu_luc_tu")) if row.get("hieu_luc_tu") else None,
    "tinh_trang": row.get("tinh_trang") or "con_hieu_luc",
    "practice_areas": sac_thue,  # sac_thue array → practice_areas
    "content_text": content_text[:100000],
    "link_tvpl": row.get("link_tvpl"),
    "dbvntax_id": row.get("id"),
}
```

**Note:** The current `law_documents` table doesn't have `content_html`, `is_priority`, `importance`, `effective_status`, `imported_from`, `created_by` columns. Those were from `law_documents_v2` schema that was never created. The import should only populate columns that EXIST in `law_documents`.

---

## Bug 4: ON CONFLICT won't work because no unique constraint

**Issue:** `ON CONFLICT DO NOTHING` is in the current INSERT but:
1. It targets the wrong table
2. Even if the table were correct, there's no unique constraint on `dbvntax_id` in `law_documents`

### Fix: Check before insert instead

```python
# Before INSERT, check if already imported
for row in rows:
    # Check existing
    existing = await db.execute(
        text("SELECT id FROM taxlegal.law_documents WHERE dbvntax_id = :dbvntax_id"),
        {"dbvntax_id": row.get("id")}
    )
    if existing.fetchone():
        continue  # Skip already imported
    
    # INSERT ...
```

---

## Bug 5: No "already imported" marking in dbvntax list

**File:** `backend/routes/laws_admin.py` ~lines 430-456 (list query)
**Impact:** Admin can import the same doc multiple times without knowing

### Fix: Add LEFT JOIN to show import status

In the `list_dbvntax_documents` function, modify the main query:

```python
data_query = f"""
    SELECT
        d.id, d.so_hieu, d.ten, d.loai, d.co_quan,
        d.ngay_ban_hanh::text AS ngay_ban_hanh,
        d.hieu_luc_tu::text AS hieu_luc_tu,
        d.tinh_trang, d.sac_thue, d.importance,
        d.is_anchor, d.link_tvpl,
        CASE WHEN ld.id IS NOT NULL THEN TRUE ELSE FALSE END AS is_imported
    FROM documents d
    LEFT JOIN dblink('host={dbvntax_host} port={dbvntax_port} dbname=taxlegal user={dbvntax_user} password={dbvntax_pass}',
        'SELECT id, dbvntax_id FROM taxlegal.law_documents') AS ld(id int, dbvntax_id int)
        ON d.id = ld.dbvntax_id
    WHERE {where}
    ORDER BY importance ASC NULLS LAST, ngay_ban_hanh DESC NULLS LAST
    LIMIT ${limit_idx} OFFSET ${offset_idx}
"""
```

**HOWEVER** — since dbvntax and taxlegal are in the SAME PostgreSQL instance (`i11456c94loppyu9vzmgyb44`), you don't need dblink. Use a cross-database query:

```sql
SELECT d.*, 
       CASE WHEN ld.id IS NOT NULL THEN TRUE ELSE FALSE END AS is_imported
FROM documents d
LEFT JOIN taxlegal.law_documents ld ON d.id = ld.dbvntax_id
WHERE ...
```

Cross-database queries work in the same PG instance when using fully-qualified `schema.table` references.

**OR — Simpler approach:** Query the `taxlegal.law_documents` table first to get the set of already-imported `dbvntax_id`s, then pass them to the frontend to filter/hide.

---

## Bug 6: Frontend should filter out already-imported docs by default

**File:** `frontend/src/pages/AdminLawDocuments.tsx`
**Change:** Add a toggle "Ẩn đã import" (checked by default). Add `is_imported` field to `DbvntaxDoc` interface.

```typescript
interface DbvntaxDoc {
  id: number;
  so_hieu: string;
  ten: string;
  loai: string;
  // ... existing fields
  is_imported?: boolean;  // NEW
}
```

```tsx
// Add toggle next to search bar:
<label className="flex items-center gap-1 text-sm">
  <input
    type="checkbox"
    checked={hideImported}
    onChange={e => setHideImported(e.target.checked)}
  />
  Ẩn đã import
</label>

// Filter in render:
{dbDocs.filter(d => !hideImported || !d.is_imported).map(doc => (...))}
```

Also change `dbDocType` dropdown values to use codes:

```tsx
<select value={dbDocType} onChange={e => setDbDocType(e.target.value)}>
  <option value="">Tất cả loại</option>
  <option value="Luat">Luật</option>
  <option value="ND">Nghị định</option>
  <option value="TT">Thông tư</option>
  <option value="VBHN">Văn bản hợp nhất</option>
  <option value="NQ">Nghị quyết</option>
  <option value="QD">Quyết định</option>
  <option value="Khac">Khác</option>
</select>
```

---

## Summary of All Changes Needed

### Backend (`backend/routes/laws_admin.py`):

1. **Line 359:** Fix `_DBVNTAX_LEGAL_TYPES` to use actual db codes:
   ```python
   _DBVNTAX_LEGAL_TYPES = ['Luat', 'ND', 'TT', 'VBHN', 'QD', 'NQ', 'Khac']
   ```

2. **Line 402:** Fix `doc_type` filter to use exact match (frontend now sends codes):
   ```python
   if doc_type:
       conditions.append(f"loai = '{doc_type}'")
   ```

3. **Line 332:** In the main query, add cross-DB LEFT JOIN to get import status:
   ```sql
   LEFT JOIN taxlegal.law_documents ld ON documents.id = ld.dbvntax_id
   ```
   Add `CASE WHEN ld.id IS NOT NULL THEN TRUE ELSE FALSE END AS is_imported` to SELECT.

4. **Lines 576-600:** Fix import INSERT — use `law_documents` table (not `law_documents_v2`), map columns correctly.

5. **Line 560-570:** Check for already-imported docs before INSERT (replace broken `ON CONFLICT DO NOTHING`).

6. **Remove** the `tax_types`, `is_priority`, `importance`, `effective_status`, `imported_from`, `created_by` columns from INSERT — they don't exist in `law_documents`.

### Frontend (`frontend/src/pages/AdminLawDocuments.tsx`):

7. **Add `is_imported` field** to `DbvntaxDoc` interface.

8. **Change `dbDocType` dropdown** values from Vietnamese names to db codes.

9. **Add "Ẩn đã import" toggle** — checked by default.

10. **Disable import button** for already-imported rows (or hide them).

### Database:

11. **Add unique index** on `taxlegal.law_documents.dbvntax_id` (optional but recommended):
    ```sql
    CREATE UNIQUE INDEX IF NOT EXISTS idx_law_docs_dbvntax_id
    ON taxlegal.law_documents(dbvntax_id) WHERE dbvntax_id IS NOT NULL;
    ```

---

## Expected Behavior After Fix

1. User opens "Văn bản Luật" → tab "Import dbvntax" → sees **186 documents** (or filtered subset)
2. User can filter by: text search (so_hieu/ten), document type (Luat/ND/TT/VBHN/QD/NQ/Khac), tax type (sac_thue)
3. Already-imported docs are **hidden by default** (toggle "Ẩn đã import")
4. User selects docs → clicks "Import" → docs appear in "Danh sách" tab
5. After import, imported docs disappear from the dbvntax list (if "Ẩn đã import" is ON)

---

## Files to Modify

| File | Changes |
|------|---------|
| `backend/routes/laws_admin.py` | Lines 359-467 (list), 509-606 (import) — 6 fixes |
| `frontend/src/pages/AdminLawDocuments.tsx` | DbvntaxDoc interface, dropdown, toggle, table rendering |

**No new files needed. No migrations needed** (table already exists, just empty).

## Testing

After fix, deploy via Coolify and test:
1. Go to https://taxlegal.gpt4vn.com → Admin → Văn bản Luật → Import dbvntax
2. Should see 186 documents immediately
3. Filter by: search "320", doc_type "Nghị định", sac_thue "Thuế GTGT" — each should narrow results
4. Select some docs → Import → verify they appear in "Danh sách" tab
5. Switch back to dbvntax tab → imported docs should be hidden
