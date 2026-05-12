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

**Side panel approach (preferred over modal):**
- Slide-in panel from right, full-height, width ~60vw (or 800px)
- Rendered **full HTML content** (toàn văn) in an iframe or shadow-DOM container
- Header: document number + title + close button
- Stays open while browsing the list (non-blocking)
- Also add a "Mở tab mới" link that opens `/api/admin/law-documents/{id}/view` in a separate browser tab

**Side panel JSX pattern:**
```tsx
{/* Side Panel for toàn văn preview */}
{listPreviewDoc && (
  <div className="fixed inset-y-0 right-0 z-50 w-[60vw] min-w-[600px] max-w-[900px] bg-white shadow-2xl flex flex-col transform transition-transform" onClick={e => e.stopPropagation()}>
    {/* Header bar */}
    <div className="flex items-center justify-between px-4 py-3 border-b shrink-0">
      <div className="min-w-0">
        <p className="text-xs text-gray-500 font-mono">{listPreviewDoc.doc_number}</p>
        <p className="text-sm font-semibold text-gray-900 truncate">{listPreviewDoc.title}</p>
      </div>
      <div className="flex items-center gap-2">
        <a href={`/api/admin/law-documents/${listPreviewDoc.id}/view`} target="_blank" className="text-xs text-[#028a39] hover:underline">Mở tab mới ↗</a>
        <button onClick={closeListPreview} className="p-1.5 rounded hover:bg-gray-100 text-gray-400"><X size={18}/></button>
      </div>
    </div>
    {/* Content: rendered full HTML */}
    <div className="flex-1 overflow-y-auto p-4 bg-white">
      {listPreviewLoading ? (
        <div className="flex items-center justify-center h-full text-gray-400"><Loader2 className="animate-spin"/></div>
      ) : (
        <div className="prose prose-sm max-w-none law-document-content" dangerouslySetInnerHTML={{ __html: listPreviewHtml }} />
      )}
    </div>
  </div>
)}
{/* Backdrop */}
{listPreviewDoc && <div className="fixed inset-0 z-40 bg-black/30" onClick={closeListPreview} />}
```

**Backdrop overlay** (z-40) behind the side panel to dim the rest of the page.

**Same side panel for dbvntax tab** — unify into one `<DocumentSidePanel>` reusable component used by both tabs.

**CSS for law-document-content** — add to `index.css`:
```css
.law-document-content table { border-collapse: collapse; width: 100%; }
.law-document-content td, .law-document-content th { border: 1px solid #d1d5db; padding: 6px 10px; }
.law-document-content img { max-width: 100%; height: auto; }
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
| List preview | Eye button → side panel slide-in từ phải, hiển thị toàn văn HTML + link "Mở tab mới" |
| `DocumentSidePanel` | Reusable component dùng chung cho cả tab dbvntax và tab Danh sách |
| CSS | `.law-document-content` styles for rendered HTML tables, images |
| `loadDbvntaxDocs()` | Append sort params to API call |
| `loadDocs()` (list) | Append sort params to API call |

---

## Testing

1. **Sort dbvntax**: Click column headers → list re-sorts; arrow indicator updates
2. **Sort list**: Same behavior
3. **Preview list doc**: Click Eye button → side panel slides in from right with full rendered HTML → can scroll toàn văn → "Mở tab mới" opens in separate browser tab
4. **Import → list**: Import from dbvntax → doc appears in list tab → can preview via side panel
