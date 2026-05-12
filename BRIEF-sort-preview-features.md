# BRIEF: Sort + Preview Features for TaxLegal Văn Bản Luật

**Date:** 2026-05-12
**Priority:** HIGH
**Repo:** `phanvuhoang/taxlegal`
**Depends on:** BRIEF-fix-dbvntax-import.md + BRIEF-fix-pipeline-draft-tax-types.md (fix `law_documents_v2` table first!)

---

## Feature 3: Sort cho tab "Import dbvntax"

### Backend: `backend/routes/laws_admin.py` — `list_dbvntax_documents`

Thêm 2 query params: `sort_by` và `sort_dir`.

```python
@router.get("/api/admin/dbvntax/list")
async def list_dbvntax_documents(
    ...
    sort_by: Optional[str] = None,    # so_hieu | ten | loai | ngay_ban_hanh
    sort_dir: Optional[str] = "desc", # asc | desc
    ...
):
```

**Sortable columns mapping:**
```python
SORT_COLUMNS = {
    "so_hieu": "so_hieu",
    "ten": "ten",
    "loai": "loai",
    "ngay_ban_hanh": "ngay_ban_hanh",
}
```

**Build ORDER BY dynamically:**
```python
order_clause = "ORDER BY importance ASC NULLS LAST, ngay_ban_hanh DESC NULLS LAST"  # default

if sort_by and sort_by in SORT_COLUMNS:
    col = SORT_COLUMNS[sort_by]
    direction = "ASC" if sort_dir == "asc" else "DESC"
    nulls = "NULLS LAST" if direction == "ASC" else "NULLS LAST"
    order_clause = f"ORDER BY {col} {direction} {nulls}, ngay_ban_hanh DESC NULLS LAST"
```

### Frontend: `AdminLawDocuments.tsx` — dbvntax table headers

Add sort state:
```typescript
const [dbSortBy, setDbSortBy] = useState<string>("ngay_ban_hanh");
const [dbSortDir, setDbSortDir] = useState<string>("desc");
```

Make table headers clickable with sort indicators:
```tsx
<th className="p-2 text-left cursor-pointer hover:bg-gray-100" onClick={() => toggleSort("so_hieu")}>
  Số hiệu {sortIndicator("so_hieu")}
</th>
<th className="p-2 text-left cursor-pointer hover:bg-gray-100" onClick={() => toggleSort("ten")}>
  Tên văn bản {sortIndicator("ten")}
</th>
<th className="p-2 text-left cursor-pointer hover:bg-gray-100" onClick={() => toggleSort("loai")}>
  Loại {sortIndicator("loai")}
</th>
<th className="p-2 text-left">Sắc thuế</th>
<th className="p-2 text-left cursor-pointer hover:bg-gray-100" onClick={() => toggleSort("ngay_ban_hanh")}>
  Ngày BH {sortIndicator("ngay_ban_hanh")}
</th>
```

Sort toggle function:
```typescript
const toggleSort = (field: string) => {
  if (dbSortBy === field) {
    setDbSortDir(dbSortDir === "asc" ? "desc" : "asc");
  } else {
    setDbSortBy(field);
    setDbSortDir("desc");
  }
};

const sortIndicator = (field: string) => {
  if (dbSortBy !== field) return null;
  return dbSortDir === "asc" ? " ▲" : " ▼";
};
```

Add sort params to `loadDbvntaxDocs`:
```typescript
if (dbSortBy) params.set("sort_by", dbSortBy);
if (dbSortDir) params.set("sort_dir", dbSortDir);
```

---

## Feature 4: Preview cho tab "Danh sách" + Sort

### Issue: "Danh sách" tab không hiển thị văn bản

**Root cause:** `GET /api/admin/law-documents` queries `taxlegal.law_documents_v2` — table doesn't exist.
**Fix:** Once `law_documents_v2` is created (from Brief fix-pipeline-draft-tax-types), this will work automatically.

### 4a: Add preview for imported documents

**Backend:** The existing `GET /api/admin/law-documents/{doc_id}` already returns `SELECT *` including `content_html`. Just need to update the frontend.

**Frontend: Add to `AdminLawDocuments.tsx`**

Add state for list preview:
```typescript
const [listPreviewDoc, setListPreviewDoc] = useState<LawDoc | null>(null);
const [listPreviewHtml, setListPreviewHtml] = useState<string>("");
const [listPreviewLoading, setListPreviewLoading] = useState(false);
```

Add preview button to each row in the list:
```tsx
<button
  onClick={() => openListPreview(doc)}
  title="Xem nội dung"
  className="p-1.5 rounded hover:bg-[#028a39]/10 text-gray-400 hover:text-[#028a39]"
>
  <Eye size={14} />
</button>
```

Preview handler:
```typescript
const openListPreview = async (doc: LawDoc) => {
  setListPreviewDoc(doc);
  setListPreviewHtml("");
  setListPreviewLoading(true);
  try {
    const res = await fetch(`/api/admin/law-documents/${doc.id}`, { headers });
    if (res.ok) {
      const data = await res.json();
      setListPreviewHtml(data.content_html || data.content_text || "<p class='text-gray-400 italic'>Không có nội dung</p>");
    } else {
      setListPreviewHtml("<p class='text-red-400'>Không thể tải nội dung</p>");
    }
  } catch {
    setListPreviewHtml("<p class='text-red-400'>Lỗi kết nối</p>");
  } finally {
    setListPreviewLoading(false);
  }
};
```

**Reuse the existing preview modal** — the component already has one for dbvntax docs. Make it generic or create a second one for list docs, using the same Modal pattern:

```tsx
{/* Preview Modal for list documents */}
{listPreviewDoc && (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={closeListPreview}>
    <div className="bg-white rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col mx-4" onClick={e => e.stopPropagation()}>
      {/* Header, Body, Footer — same pattern as dbvntax preview */}
    </div>
  </div>
)}
```

### 4b: Add sort to "Danh sách" tab

Add sort params to `GET /api/admin/law-documents`:

```python
sort_by: Optional[str] = None,  # title | doc_number | doc_type | created_at
sort_dir: Optional[str] = "desc",
```

Sortable columns:
```python
SORT_COLUMNS = {
    "title": "title",
    "doc_number": "doc_number", 
    "doc_type": "doc_type",
    "created_at": "created_at",
    "issued_date": "issued_date",
}
```

Frontend: Add sort state + clickable headers + sort indicators (same pattern as dbvntax tab).

---

## Summary of Changes

### Backend — `backend/routes/laws_admin.py`

| Change | Description |
|--------|-------------|
| `list_dbvntax_documents` | Add `sort_by`, `sort_dir` params; dynamic ORDER BY |
| `list_law_documents` | Add `sort_by`, `sort_dir` params; dynamic ORDER BY |

### Frontend — `frontend/src/pages/AdminLawDocuments.tsx`

| Change | Description |
|--------|-------------|
| State: `dbSortBy`, `dbSortDir` | Sort state for dbvntax table |
| State: `listSortBy`, `listSortDir` | Sort state for list table |
| State: `listPreviewDoc`, `listPreviewHtml`, `listPreviewLoading` | Preview state for list |
| `toggleSort()` | Generic sort toggle function |
| `sortIndicator()` | Sort arrow indicator |
| Table headers: dbvntax | Make clickable, show sort arrows |
| Table headers: list | Make clickable, show sort arrows |
| List row actions | Add Eye button for preview |
| List preview modal | Copy from dbvntax preview modal pattern |
| `loadDbvntaxDocs()` | Append sort params to API call |
| `loadDocs()` (list) | Append sort params to API call |

---

## Testing

1. **Sort dbvntax**: Click column headers → list re-sorts; arrow indicator updates
2. **Sort list**: Same behavior
3. **Preview list doc**: Click Eye button → modal with HTML content
4. **Import → list**: Import from dbvntax → doc appears in list tab → can preview
