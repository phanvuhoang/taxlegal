import { useState, useEffect, useRef } from "react";
import { Upload, Link2, Database, FileText, Search, Tag, Trash2, Plus, RefreshCw, CheckCircle, XCircle, Star, Loader2, ExternalLink, X, Eye } from "lucide-react";

interface LawDoc {
  id: number;
  doc_number: string;
  title: string;
  doc_type: string;
  issued_date: string | null;
  is_active: boolean;
  is_priority: boolean;
  tags: string[];
  imported_from: string;
  created_at: string;
}

interface DbvntaxDoc {
  id: number;
  so_hieu: string;
  ten: string;
  loai: string;
  co_quan: string;
  ngay_ban_hanh: string | null;
  hieu_luc_tu: string | null;
  tinh_trang: string | null;
  sac_thue: string[];
  importance: number;
  is_anchor: boolean;
  link_tvpl: string | null;
  is_imported?: boolean;
}

const DOC_TYPES = ["Luật", "Nghị định", "Thông tư", "Quyết định", "Công văn", "Nghị quyết", "Thông báo", "Khác"];
const SAC_THUE_OPTIONS = [
  { value: "", label: "Tất cả sắc thuế" },
  { value: "GTGT", label: "Thuế GTGT" },
  { value: "TNDN", label: "Thuế TNDN" },
  { value: "TNCN", label: "Thuế TNCN" },
  { value: "FCT", label: "Nhà thầu nước ngoài" },
  { value: "TTDB", label: "Thuế TTDB" },
  { value: "XNK", label: "Thuế XNK / Hải quan" },
];

// dbvntax `loai` is stored as codes (Luat, ND, TT, ...). Map to display labels + colors.
const DBVNTAX_LOAI_OPTIONS = [
  { value: "Luat", label: "Luật" },
  { value: "ND", label: "Nghị định" },
  { value: "TT", label: "Thông tư" },
  { value: "VBHN", label: "Văn bản hợp nhất" },
  { value: "NQ", label: "Nghị quyết" },
  { value: "QD", label: "Quyết định" },
  { value: "Khac", label: "Khác" },
];

const LOAI_LABELS: Record<string, string> = Object.fromEntries(
  DBVNTAX_LOAI_OPTIONS.map(o => [o.value, o.label])
);

const LOAI_COLORS: Record<string, string> = {
  "Luat": "bg-indigo-50 text-indigo-700",
  "ND": "bg-blue-50 text-blue-700",
  "TT": "bg-cyan-50 text-cyan-700",
  "VBHN": "bg-purple-50 text-purple-700",
  "NQ": "bg-amber-50 text-amber-700",
  "QD": "bg-green-50 text-green-700",
  "Khac": "bg-gray-100 text-gray-600",
};

export default function AdminLawDocuments() {
  const [activeTab, setActiveTab] = useState<"list" | "upload" | "crawler" | "dbvntax">("list");
  const [docs, setDocs] = useState<LawDoc[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState("");
  const [msg, setMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Upload/Paste tab state
  const [uploadMode, setUploadMode] = useState<"file" | "paste">("file");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [pasteTitle, setPasteTitle] = useState("");
  const [pasteDocNumber, setPasteDocNumber] = useState("");
  const [pasteDocType, setPasteDocType] = useState("Thông tư");
  const [pasteContent, setPasteContent] = useState("");
  const [pasteIsHtml, setPasteIsHtml] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  // Crawler tab state
  const [crawlUrl, setCrawlUrl] = useState("");
  const [crawlTitle, setCrawlTitle] = useState("");
  const [crawlDocNumber, setCrawlDocNumber] = useState("");
  const [crawlDocType, setCrawlDocType] = useState("Thông tư");
  const [crawling, setCrawling] = useState(false);

  // dbvntax tab state
  const [dbDocs, setDbDocs] = useState<DbvntaxDoc[]>([]);
  const [dbSearch, setDbSearch] = useState("");
  const [dbSacThue, setDbSacThue] = useState("");
  const [dbDocType, setDbDocType] = useState("");
  const [dbLoading, setDbLoading] = useState(false);
  const [selected, setSelected] = useState<number[]>([]);
  const [importPriority, setImportPriority] = useState(false);
  const [importing, setImporting] = useState(false);
  const [dbTotal, setDbTotal] = useState(0);
  const [hideImported, setHideImported] = useState(true);

  // HTML preview modal state
  const [previewDoc, setPreviewDoc] = useState<DbvntaxDoc | null>(null);
  const [previewHtml, setPreviewHtml] = useState<string>("");
  const [previewLoading, setPreviewLoading] = useState(false);
  const [importingId, setImportingId] = useState<number | null>(null);

  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}` };

  const showMsg = (type: "success" | "error", text: string) => {
    setMsg({ type, text });
    setTimeout(() => setMsg(null), 4000);
  };

  // Load law docs
  const loadDocs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set("q", search);
      if (filterType) params.set("doc_type", filterType);
      const res = await fetch(`/api/admin/law-documents?${params}`, { headers });
      if (res.ok) setDocs(await res.json());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadDocs(); }, []);
  useEffect(() => { if (activeTab === "list") loadDocs(); }, [search, filterType]);
  // Auto-load dbvntax docs when switching to that tab
  useEffect(() => { if (activeTab === "dbvntax" && dbDocs.length === 0) loadDbvntaxDocs(); }, [activeTab]);

  // AI Tag
  const aiTag = async (id: number) => {
    try {
      const res = await fetch(`/api/admin/law-documents/${id}/ai-tag`, { method: "POST", headers });
      if (res.ok) { showMsg("success", "AI tagging xong"); loadDocs(); }
      else showMsg("error", "Lỗi AI tag");
    } catch { showMsg("error", "Lỗi kết nối"); }
  };

  // Delete
  const deletDoc = async (id: number) => {
    if (!confirm("Xóa văn bản này?")) return;
    try {
      const res = await fetch(`/api/admin/law-documents/${id}`, { method: "DELETE", headers });
      if (res.ok) { showMsg("success", "Đã xóa"); loadDocs(); }
      else showMsg("error", "Lỗi xóa");
    } catch { showMsg("error", "Lỗi kết nối"); }
  };

  // Toggle priority
  const togglePriority = async (doc: LawDoc) => {
    try {
      const res = await fetch(`/api/admin/law-documents/${doc.id}`, {
        method: "PUT",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ is_priority: !doc.is_priority }),
      });
      if (res.ok) loadDocs();
    } catch { /* noop */ }
  };

  // Upload file
  const handleUpload = async () => {
    if (uploadMode === "file" && !uploadFile) { showMsg("error", "Chọn file trước"); return; }
    if (uploadMode === "paste" && !pasteTitle) { showMsg("error", "Nhập tiêu đề"); return; }
    setUploading(true);
    try {
      if (uploadMode === "file" && uploadFile) {
        const fd = new FormData();
        fd.append("file", uploadFile);
        if (pasteDocNumber) fd.append("doc_number", pasteDocNumber);
        fd.append("doc_type", pasteDocType);
        const res = await fetch("/api/admin/law-documents/upload", { method: "POST", headers, body: fd });
        if (res.ok) { showMsg("success", "Upload thành công"); setUploadFile(null); if (fileRef.current) fileRef.current.value = ""; loadDocs(); }
        else showMsg("error", (await res.json()).detail || "Lỗi upload");
      } else {
        const res = await fetch("/api/admin/law-documents", {
          method: "POST",
          headers: { ...headers, "Content-Type": "application/json" },
          body: JSON.stringify({
            title: pasteTitle, doc_number: pasteDocNumber, doc_type: pasteDocType,
            content_html: pasteIsHtml ? pasteContent : undefined,
            content_text: !pasteIsHtml ? pasteContent : undefined,
            imported_from: "paste",
          }),
        });
        if (res.ok) { showMsg("success", "Lưu thành công"); setPasteTitle(""); setPasteDocNumber(""); setPasteContent(""); loadDocs(); }
        else showMsg("error", (await res.json()).detail || "Lỗi lưu");
      }
    } finally { setUploading(false); }
  };

  // Crawl URL (Crawler tab)
  const handleCrawlTab = async () => {
    if (!crawlUrl) { showMsg("error", "Nhập URL"); return; }
    setCrawling(true);
    try {
      const res = await fetch("/api/admin/law-documents/crawl", {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ url: crawlUrl, title: crawlTitle, doc_number: crawlDocNumber, doc_type: crawlDocType }),
      });
      if (res.ok) { showMsg("success", "Crawl thành công"); setCrawlUrl(""); setCrawlTitle(""); loadDocs(); }
      else showMsg("error", (await res.json()).detail || "Lỗi crawl");
    } finally { setCrawling(false); }
  };

  // ===== DBVNTAX HANDLERS =====

  const loadDbvntaxDocs = async () => {
    setDbLoading(true);
    try {
      const params = new URLSearchParams();
      if (dbSearch) params.set("search", dbSearch);
      if (dbSacThue) params.set("sac_thue", dbSacThue);
      if (dbDocType) params.set("doc_type", dbDocType);
      params.set("limit", "100");
      const res = await fetch(`/api/admin/dbvntax/list?${params}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setDbDocs(data.items || data || []);
        setDbTotal(data.total || 0);
        setSelected([]);
      } else {
        const err = await res.json().catch(() => ({}));
        showMsg("error", err.detail || "Không thể kết nối dbvntax");
      }
    } finally {
      setDbLoading(false);
    }
  };

  const handleImport = async (ids?: number[]) => {
    const idsToImport = ids || selected;
    if (!idsToImport.length) return;
    if (ids) setImportingId(ids[0]);
    else setImporting(true);
    try {
      const res = await fetch("/api/admin/dbvntax/import", {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ ids: idsToImport, is_priority: importPriority }),
      });
      if (res.ok) {
        const data = await res.json();
        const skippedNote = data.skipped ? ` (${data.skipped} đã import từ trước)` : "";
        showMsg("success", `Đã import ${data.imported} văn bản${skippedNote}`);
        if (!ids) setSelected([]);
        loadDocs();
        loadDbvntaxDocs();
      } else {
        const err = await res.json();
        showMsg("error", err.detail || "Import thất bại");
      }
    } finally {
      setImporting(false);
      setImportingId(null);
    }
  };

  // Open preview modal: fetch HTML content
  const openPreview = async (doc: DbvntaxDoc) => {
    setPreviewDoc(doc);
    setPreviewHtml("");
    setPreviewLoading(true);
    try {
      const res = await fetch(`/api/admin/dbvntax/preview/${doc.id}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setPreviewHtml(data.noi_dung_html || "<p class='text-gray-400 italic'>Không có nội dung HTML</p>");
      } else {
        setPreviewHtml("<p class='text-red-400'>Không thể tải nội dung</p>");
      }
    } catch {
      setPreviewHtml("<p class='text-red-400'>Lỗi kết nối</p>");
    } finally {
      setPreviewLoading(false);
    }
  };

  const closePreview = () => {
    setPreviewDoc(null);
    setPreviewHtml("");
  };

  // Computed for dbvntax tab
  const visibleDbDocs = dbDocs.filter(d => !hideImported || !d.is_imported);
  const hiddenImportedCount = dbDocs.filter(d => d.is_imported).length;

  const tabs = [
    { id: "list", label: "Danh sách", icon: FileText },
    { id: "upload", label: "Upload / Paste", icon: Upload },
    { id: "crawler", label: "Crawler URL", icon: Link2 },
    { id: "dbvntax", label: "Import dbvntax", icon: Database },
  ] as const;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Văn bản Luật</h1>
          <p className="text-sm text-gray-500 mt-1">Quản lý kho văn bản pháp luật — dùng cho RAG và phân tích</p>
        </div>
      </div>

      {/* Message */}
      {msg && (
        <div className={`mb-4 flex items-center gap-2 p-3 rounded-lg text-sm font-medium ${msg.type === "success" ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
          {msg.type === "success" ? <CheckCircle size={16} /> : <XCircle size={16} />}
          {msg.text}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg mb-6 w-fit">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === t.id ? "bg-white text-[#028a39] shadow-sm" : "text-gray-600 hover:text-gray-900"}`}
          >
            <t.icon size={15} />
            {t.label}
          </button>
        ))}
      </div>

      {/* ===== TAB: DANH SÁCH ===== */}
      {activeTab === "list" && (
        <div>
          <div className="flex gap-3 mb-4">
            <div className="relative flex-1 max-w-xs">
              <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm"
                placeholder="Tìm tiêu đề, số hiệu..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <select
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              <option value="">Tất cả loại</option>
              {DOC_TYPES.map((t) => <option key={t}>{t}</option>)}
            </select>
            <button onClick={loadDocs} className="flex items-center gap-2 px-3 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50">
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            </button>
          </div>

          {loading ? (
            <div className="text-center py-12 text-gray-400">Đang tải...</div>
          ) : docs.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <FileText size={40} className="mx-auto mb-3 opacity-30" />
              <p>Chưa có văn bản nào</p>
              <p className="text-sm mt-1">Upload, paste, crawl, hoặc import từ dbvntax</p>
            </div>
          ) : (
            <div className="space-y-2">
              {docs.map((doc) => (
                <div key={doc.id} className="border border-gray-200 rounded-lg p-4 hover:border-[#028a39]/40 transition-colors">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded font-mono">{doc.doc_number || "—"}</span>
                        <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded">{doc.doc_type}</span>
                        {doc.is_priority && <span className="text-xs bg-amber-50 text-amber-700 px-2 py-0.5 rounded flex items-center gap-1"><Star size={10} />Ưu tiên</span>}
                        <span className="text-xs text-gray-400">{doc.imported_from}</span>
                      </div>
                      <p className="text-sm font-medium text-gray-900 mt-1 truncate">{doc.title}</p>
                      {doc.tags && doc.tags.length > 0 && (
                        <div className="flex gap-1 flex-wrap mt-1">
                          {doc.tags.map((tag, i) => (
                            <span key={i} className="text-xs bg-green-50 text-green-700 px-1.5 py-0.5 rounded">{tag}</span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      <button onClick={() => togglePriority(doc)} title="Toggle ưu tiên" className={`p-1.5 rounded hover:bg-gray-100 ${doc.is_priority ? "text-amber-500" : "text-gray-400"}`}>
                        <Star size={14} />
                      </button>
                      <button onClick={() => aiTag(doc.id)} title="AI tự động tag" className="p-1.5 rounded hover:bg-gray-100 text-gray-400 hover:text-[#028a39]">
                        <Tag size={14} />
                      </button>
                      <button onClick={() => deletDoc(doc.id)} className="p-1.5 rounded hover:bg-red-50 text-gray-400 hover:text-red-500">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ===== TAB: UPLOAD/PASTE ===== */}
      {activeTab === "upload" && (
        <div className="max-w-2xl">
          <div className="flex gap-2 mb-6">
            {(["file", "paste"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setUploadMode(m)}
                className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${uploadMode === m ? "bg-[#028a39] text-white border-[#028a39]" : "border-gray-200 text-gray-600 hover:border-gray-300"}`}
              >
                {m === "file" ? "Upload file (PDF/DOCX/TXT)" : "Paste nội dung"}
              </button>
            ))}
          </div>

          <div className="space-y-4">
            {uploadMode === "file" ? (
              <>
                <div
                  className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center cursor-pointer hover:border-[#028a39]/50 transition-colors"
                  onClick={() => fileRef.current?.click()}
                >
                  <Upload size={32} className="mx-auto mb-3 text-gray-300" />
                  <p className="text-sm font-medium text-gray-600">{uploadFile ? uploadFile.name : "Click hoặc kéo file vào đây"}</p>
                  <p className="text-xs text-gray-400 mt-1">PDF, DOCX, TXT — tối đa 10MB</p>
                  <input ref={fileRef} type="file" accept=".pdf,.docx,.txt" className="hidden" onChange={(e) => setUploadFile(e.target.files?.[0] || null)} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-medium text-gray-500 mb-1 block">Số hiệu (tùy chọn)</label>
                    <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" placeholder="TT 80/2021/TT-BTC" value={pasteDocNumber} onChange={(e) => setPasteDocNumber(e.target.value)} />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 mb-1 block">Loại văn bản</label>
                    <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" value={pasteDocType} onChange={(e) => setPasteDocType(e.target.value)}>
                      {DOC_TYPES.map((t) => <option key={t}>{t}</option>)}
                    </select>
                  </div>
                </div>
              </>
            ) : (
              <>
                <div>
                  <label className="text-xs font-medium text-gray-500 mb-1 block">Tiêu đề *</label>
                  <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" placeholder="Thông tư 80/2021/TT-BTC..." value={pasteTitle} onChange={(e) => setPasteTitle(e.target.value)} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-medium text-gray-500 mb-1 block">Số hiệu</label>
                    <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" placeholder="80/2021/TT-BTC" value={pasteDocNumber} onChange={(e) => setPasteDocNumber(e.target.value)} />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 mb-1 block">Loại văn bản</label>
                    <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" value={pasteDocType} onChange={(e) => setPasteDocType(e.target.value)}>
                      {DOC_TYPES.map((t) => <option key={t}>{t}</option>)}
                    </select>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <input type="checkbox" id="pasteIsHtml" checked={pasteIsHtml} onChange={(e) => setPasteIsHtml(e.target.checked)} className="rounded" />
                  <label htmlFor="pasteIsHtml" className="text-sm text-gray-600">Nội dung là HTML</label>
                </div>
                <div>
                  <label className="text-xs font-medium text-gray-500 mb-1 block">Nội dung {pasteIsHtml ? "(HTML)" : "(Plain text)"}</label>
                  <textarea
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm font-mono resize-y"
                    rows={12}
                    placeholder={pasteIsHtml ? "<html>...</html>" : "Dán nội dung văn bản vào đây..."}
                    value={pasteContent}
                    onChange={(e) => setPasteContent(e.target.value)}
                  />
                </div>
              </>
            )}

            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full bg-[#028a39] text-white py-2.5 rounded-lg font-medium text-sm hover:bg-[#026d2d] disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {uploading ? <><RefreshCw size={15} className="animate-spin" /> Đang xử lý...</> : <><Plus size={15} /> Lưu văn bản</>}
            </button>
          </div>
        </div>
      )}

      {/* ===== TAB: CRAWLER ===== */}
      {activeTab === "crawler" && (
        <div className="max-w-2xl space-y-4">
          <p className="text-sm text-gray-500">Nhập URL văn bản pháp luật — hệ thống sẽ dùng CrawlKit để lấy nội dung HTML.</p>

          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">URL *</label>
            <input
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
              placeholder="https://thuvienphapluat.vn/van-ban/..."
              value={crawlUrl}
              onChange={(e) => setCrawlUrl(e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Tiêu đề (tùy chọn — nếu để trống sẽ lấy từ trang)</label>
            <input
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
              placeholder="Thông tư 80/2021/TT-BTC về..."
              value={crawlTitle}
              onChange={(e) => setCrawlTitle(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Số hiệu</label>
              <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" placeholder="80/2021/TT-BTC" value={crawlDocNumber} onChange={(e) => setCrawlDocNumber(e.target.value)} />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Loại văn bản</label>
              <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" value={crawlDocType} onChange={(e) => setCrawlDocType(e.target.value)}>
                {DOC_TYPES.map((t) => <option key={t}>{t}</option>)}
              </select>
            </div>
          </div>

          <button
            onClick={handleCrawlTab}
            disabled={crawling}
            className="w-full bg-[#028a39] text-white py-2.5 rounded-lg font-medium text-sm hover:bg-[#026d2d] disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {crawling ? <><RefreshCw size={15} className="animate-spin" /> Đang crawl...</> : <><Link2 size={15} /> Crawl & Lưu</>}
          </button>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-700">
            <strong>Lưu ý:</strong> Cần cài đặt <code>CRAWLKIT_API_KEY</code> trong Coolify. Chỉ crawl được các trang cho phép — thuvienphapluat.vn có thể yêu cầu xác thực.
          </div>
        </div>
      )}

      {/* ===== TAB: DBVNTAX ===== */}
      {activeTab === "dbvntax" && (
        <div className="space-y-4">
          {/* Search + filter bar */}
          <div className="bg-white border rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <Database className="w-4 h-4 text-[#028a39]" />
              Import từ dbvntax Database
            </h3>
            <div className="flex gap-2 mb-3 flex-wrap">
              <div className="relative flex-1 min-w-[180px]">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  className="w-full pl-9 border rounded px-3 py-2 text-sm"
                  placeholder="Tìm số hiệu, tên văn bản..."
                  value={dbSearch}
                  onChange={e => setDbSearch(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && loadDbvntaxDocs()}
                />
              </div>
              <select
                className="border rounded px-3 py-2 text-sm"
                value={dbDocType}
                onChange={e => setDbDocType(e.target.value)}
              >
                <option value="">Tất cả loại</option>
                {DBVNTAX_LOAI_OPTIONS.map(o => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
              <select
                className="border rounded px-3 py-2 text-sm"
                value={dbSacThue}
                onChange={e => setDbSacThue(e.target.value)}
              >
                {SAC_THUE_OPTIONS.map(o => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
              <button
                onClick={loadDbvntaxDocs}
                disabled={dbLoading}
                className="px-4 py-2 bg-[#028a39] text-white rounded text-sm hover:bg-[#016b2c] disabled:opacity-50 flex items-center gap-2"
              >
                {dbLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search size={14} />}
                Tìm kiếm
              </button>
            </div>

            {dbDocs.length > 0 && (
              <>
                <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
                  <span className="text-sm text-gray-600">
                    {selected.length > 0
                      ? `Đã chọn ${selected.length} văn bản`
                      : `${visibleDbDocs.length} / ${dbTotal} văn bản${hiddenImportedCount > 0 && hideImported ? ` (ẩn ${hiddenImportedCount} đã import)` : ""}`}
                  </span>
                  <div className="flex items-center gap-3 flex-wrap">
                    <label className="flex items-center gap-1 text-sm">
                      <input type="checkbox" checked={hideImported} onChange={e => setHideImported(e.target.checked)} />
                      Ẩn đã import
                    </label>
                    <label className="flex items-center gap-1 text-sm">
                      <input type="checkbox" checked={importPriority} onChange={e => setImportPriority(e.target.checked)} />
                      Đánh dấu ưu tiên
                    </label>
                    <button
                      onClick={() => handleImport()}
                      disabled={selected.length === 0 || importing}
                      className="px-4 py-2 bg-[#028a39] text-white rounded text-sm hover:bg-[#016b2c] disabled:opacity-50 flex items-center gap-2"
                    >
                      {importing ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                      Import {selected.length} văn bản đã chọn
                    </button>
                  </div>
                </div>

                <div className="overflow-x-auto rounded-lg border">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                      <tr>
                        <th className="p-2 text-left w-8">
                          <input
                            type="checkbox"
                            checked={selected.length > 0 && selected.length === visibleDbDocs.filter(d => !d.is_imported).length}
                            onChange={e => setSelected(e.target.checked ? visibleDbDocs.filter(d => !d.is_imported).map(d => d.id) : [])}
                          />
                        </th>
                        <th className="p-2 text-left">Số hiệu</th>
                        <th className="p-2 text-left">Tên văn bản</th>
                        <th className="p-2 text-left">Loại</th>
                        <th className="p-2 text-left">Sắc thuế</th>
                        <th className="p-2 text-left">Ngày BH</th>
                        <th className="p-2 text-left w-16"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {visibleDbDocs.map(doc => (
                        <tr
                          key={doc.id}
                          className={`hover:bg-gray-50 cursor-pointer ${doc.is_imported ? "bg-gray-50" : ""}`}
                          onClick={() => openPreview(doc)}
                        >
                          <td className="p-2" onClick={e => e.stopPropagation()}>
                            <input
                              type="checkbox"
                              disabled={doc.is_imported}
                              checked={selected.includes(doc.id)}
                              onChange={e =>
                                setSelected(e.target.checked
                                  ? [...selected, doc.id]
                                  : selected.filter(id => id !== doc.id))
                              }
                            />
                          </td>
                          <td className="p-2 font-mono text-xs text-gray-700 whitespace-nowrap">
                            {doc.so_hieu || "—"}
                            {doc.is_imported && (
                              <span className="ml-1.5 text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded">đã import</span>
                            )}
                          </td>
                          <td className="p-2 max-w-xs">
                            <span className={`line-clamp-2 ${doc.is_imported ? "text-gray-400" : "text-gray-900"}`}>{doc.ten}</span>
                          </td>
                          <td className="p-2">
                            <span className={`text-xs px-2 py-0.5 rounded font-medium ${LOAI_COLORS[doc.loai] || "bg-gray-100 text-gray-600"}`}>
                              {LOAI_LABELS[doc.loai] || doc.loai || "—"}
                            </span>
                          </td>
                          <td className="p-2">
                            <div className="flex gap-1 flex-wrap">
                              {(doc.sac_thue || []).map((st, i) => (
                                <span key={i} className="text-xs bg-green-50 text-green-700 px-1.5 py-0.5 rounded">{st}</span>
                              ))}
                            </div>
                          </td>
                          <td className="p-2 text-xs text-gray-500 whitespace-nowrap">
                            {doc.ngay_ban_hanh ? new Date(doc.ngay_ban_hanh).toLocaleDateString("vi-VN") : "—"}
                          </td>
                          <td className="p-2" onClick={e => e.stopPropagation()}>
                            <button
                              title="Xem nội dung"
                              onClick={() => openPreview(doc)}
                              className="p-1.5 rounded hover:bg-[#028a39]/10 text-gray-400 hover:text-[#028a39]"
                            >
                              <Eye size={14} />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}

            {dbDocs.length === 0 && !dbLoading && (
              <div className="text-center py-8 text-gray-400">
                <Database size={32} className="mx-auto mb-2 opacity-20" />
                <p className="text-sm">Không có văn bản nào phù hợp</p>
                <p className="text-xs mt-1">Thử bỏ filter hoặc thay đổi từ khóa</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ===== HTML PREVIEW MODAL ===== */}
      {previewDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={closePreview}>
          <div
            className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col"
            onClick={e => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-4 p-5 border-b">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <span className={`text-xs px-2 py-0.5 rounded font-medium ${LOAI_COLORS[previewDoc.loai] || "bg-gray-100 text-gray-600"}`}>
                    {LOAI_LABELS[previewDoc.loai] || previewDoc.loai}
                  </span>
                  {previewDoc.so_hieu && (
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded font-mono">{previewDoc.so_hieu}</span>
                  )}
                  {previewDoc.ngay_ban_hanh && (
                    <span className="text-xs text-gray-500">
                      Ngày {new Date(previewDoc.ngay_ban_hanh).toLocaleDateString("vi-VN")}
                    </span>
                  )}
                  {(previewDoc.sac_thue || []).map((st, i) => (
                    <span key={i} className="text-xs bg-green-50 text-green-700 px-1.5 py-0.5 rounded">{st}</span>
                  ))}
                </div>
                <h2 className="text-base font-semibold text-gray-900 leading-snug">{previewDoc.ten}</h2>
                {previewDoc.co_quan && (
                  <p className="text-xs text-gray-500 mt-0.5">{previewDoc.co_quan}</p>
                )}
              </div>
              <button onClick={closePreview} className="p-1.5 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600 shrink-0">
                <X size={18} />
              </button>
            </div>

            {/* Modal Body — HTML content */}
            <div className="flex-1 overflow-y-auto p-5">
              {previewLoading ? (
                <div className="flex items-center justify-center py-16 text-gray-400">
                  <Loader2 className="w-6 h-6 animate-spin mr-2" />
                  Đang tải nội dung...
                </div>
              ) : (
                <div
                  className="prose prose-sm max-w-none text-gray-800 law-content"
                  dangerouslySetInnerHTML={{ __html: previewHtml }}
                />
              )}
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-between gap-3 p-4 border-t bg-gray-50 rounded-b-xl">
              <div className="flex items-center gap-2">
                {previewDoc.link_tvpl && (
                  <a
                    href={previewDoc.link_tvpl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 text-sm text-[#028a39] hover:underline"
                  >
                    <ExternalLink size={14} />
                    Xem trên thuvienphapluat.vn
                  </a>
                )}
              </div>
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-1 text-sm text-gray-600">
                  <input
                    type="checkbox"
                    checked={importPriority}
                    onChange={e => setImportPriority(e.target.checked)}
                  />
                  Ưu tiên
                </label>
                <button
                  onClick={() => {
                    handleImport([previewDoc.id]);
                    closePreview();
                  }}
                  disabled={importingId === previewDoc.id || !!previewDoc.is_imported}
                  className="px-4 py-2 bg-[#028a39] text-white rounded-lg text-sm font-medium hover:bg-[#026d2d] disabled:opacity-50 flex items-center gap-2"
                >
                  {previewDoc.is_imported ? (
                    <><CheckCircle size={14} /> Đã import</>
                  ) : importingId === previewDoc.id ? (
                    <><Loader2 size={14} className="animate-spin" /> Đang import...</>
                  ) : (
                    <><Plus size={14} /> Import văn bản này</>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
