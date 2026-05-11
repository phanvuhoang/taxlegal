/**
 * Admin: Priority Docs (Anchor Documents) management (/admin/priority-docs)
 * These docs are injected first into AI writing prompts — highest priority context
 */
import { useEffect, useState } from "react";
import { priorityDocsApi, PriorityDoc, DOC_TYPES } from "../lib/writing";
import {
  FileText, Plus, Trash2, Edit2, Loader2, X,
  ChevronDown, BookMarked, Star, Database, Search
} from "lucide-react";
import toast from "react-hot-toast";

interface DocForm {
  title: string;
  doc_type: string;
  source_url: string;
  content: string;
  priority_level: number;
  is_active: boolean;
}

const DEFAULT_FORM: DocForm = {
  title: "",
  doc_type: "circular",
  source_url: "",
  content: "",
  priority_level: 1,
  is_active: true,
};

// Interface for law_documents_v2 records
interface LawDocPriority {
  id: number;
  title: string;
  doc_number: string;
  doc_type: string;
  is_priority: boolean;
}

export default function AdminPriorityDocs() {
  const [docs, setDocs] = useState<PriorityDoc[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<DocForm>(DEFAULT_FORM);
  const [saving, setSaving] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  // Main tab: "writing" | "law"
  const [mainTab, setMainTab] = useState<"writing" | "law">("writing");

  // Law docs state
  const [lawDocs, setLawDocs] = useState<LawDocPriority[]>([]);
  const [lawSearch, setLawSearch] = useState("");
  const [lawTab, setLawTab] = useState<"priority" | "all">("priority");
  const [lawLoading, setLawLoading] = useState(false);

  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}` };

  const loadDocs = async () => {
    try {
      const res = await priorityDocsApi.list();
      setDocs(res.data);
    } catch {
      toast.error("Không thể tải priority docs");
    } finally {
      setLoading(false);
    }
  };

  const loadLawDocs = async (priorityOnly = true) => {
    setLawLoading(true);
    try {
      const params = new URLSearchParams();
      if (priorityOnly) params.set("is_priority", "true");
      if (lawSearch) params.set("search", lawSearch);
      params.set("limit", "100");
      const res = await fetch(`/api/admin/law-documents?${params}`, { headers });
      if (res.ok) setLawDocs(await res.json());
    } finally {
      setLawLoading(false);
    }
  };

  useEffect(() => { loadDocs(); }, []);
  useEffect(() => { loadLawDocs(true); }, []);

  // Reload law docs when lawTab changes
  useEffect(() => {
    loadLawDocs(lawTab === "priority");
  }, [lawTab]);

  const toggleLawPriority = async (id: number, current: boolean) => {
    const res = await fetch(`/api/admin/law-documents/${id}`, {
      method: "PUT",
      headers: { ...headers, "Content-Type": "application/json" },
      body: JSON.stringify({ is_priority: !current }),
    });
    if (res.ok) {
      toast.success(!current ? "Đã đánh dấu ưu tiên" : "Đã bỏ đánh dấu");
      loadLawDocs(lawTab === "priority");
    } else {
      toast.error("Cập nhật thất bại");
    }
  };

  const openCreate = () => {
    setForm(DEFAULT_FORM);
    setEditingId(null);
    setShowModal(true);
  };

  const openEdit = (doc: PriorityDoc) => {
    setForm({
      title: doc.title,
      doc_type: doc.doc_type,
      source_url: doc.source_url || "",
      content: doc.content,
      priority_level: doc.priority_level,
      is_active: doc.is_active,
    });
    setEditingId(doc.id);
    setShowModal(true);
  };

  const handleSave = async () => {
    if (!form.title.trim()) { toast.error("Vui lòng nhập tiêu đề"); return; }
    if (!form.content.trim()) { toast.error("Vui lòng nhập nội dung"); return; }
    setSaving(true);
    try {
      if (editingId !== null) {
        await priorityDocsApi.update(editingId, {
          ...form,
          source_url: form.source_url || undefined,
        } as any);
        toast.success("Đã cập nhật");
      } else {
        await priorityDocsApi.create({
          ...form,
          source_url: form.source_url || undefined,
        });
        toast.success("Đã tạo priority doc");
      }
      setShowModal(false);
      loadDocs();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Lỗi khi lưu");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number, title: string) => {
    if (!confirm(`Xóa "${title}"?`)) return;
    try {
      await priorityDocsApi.delete(id);
      setDocs((prev) => prev.filter((d) => d.id !== id));
      toast.success("Đã xóa");
    } catch {
      toast.error("Không thể xóa");
    }
  };

  const docTypeLabel = (dt: string) => DOC_TYPES.find((d) => d.value === dt)?.label || dt;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: "#028a39" }}>
            <BookMarked className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Priority Docs (Anchor)</h1>
            <p className="text-sm text-gray-500">Tài liệu ưu tiên — inject đầu tiên vào writing prompts</p>
          </div>
        </div>
        {mainTab === "writing" && (
          <button
            onClick={openCreate}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm font-medium"
            style={{ background: "#028a39" }}
          >
            <Plus className="w-4 h-4" />
            Thêm tài liệu
          </button>
        )}
      </div>

      {/* Main Tab Switcher */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg w-fit">
        <button
          onClick={() => setMainTab("writing")}
          className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            mainTab === "writing" ? "bg-white text-[#028a39] shadow-sm" : "text-gray-600 hover:text-gray-900"
          }`}
        >
          <BookMarked className="w-4 h-4" />
          Writing Priority Docs
        </button>
        <button
          onClick={() => setMainTab("law")}
          className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            mainTab === "law" ? "bg-white text-[#028a39] shadow-sm" : "text-gray-600 hover:text-gray-900"
          }`}
        >
          <Database className="w-4 h-4" />
          Văn bản Luật ưu tiên
        </button>
      </div>

      {/* ===== TAB: WRITING PRIORITY DOCS ===== */}
      {mainTab === "writing" && (
        <>
          {/* Info box */}
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
            <strong>Cơ chế Anchor Documents:</strong> Tài liệu có priority_level thấp hơn sẽ được inject trước (level 1 = cao nhất).
            AI sẽ ưu tiên trích dẫn từ các tài liệu này trước khi tìm nguồn khác.
          </div>

          {/* List */}
          {loading ? (
            <div className="flex justify-center py-20">
              <Loader2 className="w-8 h-8 animate-spin" style={{ color: "#028a39" }} />
            </div>
          ) : docs.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-xl border border-dashed border-gray-200">
              <BookMarked className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p className="text-gray-500">Chưa có priority docs nào</p>
              <p className="text-xs text-gray-400 mt-1 mb-4">Thêm văn bản luật quan trọng làm anchor document</p>
              <button onClick={openCreate}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm"
                style={{ background: "#028a39" }}>
                <Plus className="w-4 h-4" /> Thêm tài liệu
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {docs.map((doc) => (
                <div key={doc.id}
                  className={`bg-white rounded-xl border transition-colors ${doc.is_active ? "border-gray-100" : "border-gray-200 opacity-60"}`}>
                  <div className="p-4 flex items-start gap-3">
                    {/* Priority badge */}
                    <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold"
                      style={{ background: doc.priority_level === 1 ? "#028a39" : doc.priority_level <= 3 ? "#0284c7" : "#6b7280" }}>
                      {doc.priority_level}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-gray-900 truncate">{doc.title}</p>
                        <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-600">
                          {docTypeLabel(doc.doc_type)}
                        </span>
                        {!doc.is_active && (
                          <span className="px-2 py-0.5 text-xs rounded-full bg-red-50 text-red-600">Tắt</span>
                        )}
                      </div>
                      <p className="text-xs text-gray-400 mt-0.5 flex items-center gap-2">
                        {doc.source_url && (
                          <a href={doc.source_url} target="_blank" rel="noopener noreferrer"
                            className="text-blue-500 hover:underline truncate max-w-xs">{doc.source_url}</a>
                        )}
                        <span>{doc.content.length.toLocaleString()} ký tự</span>
                      </p>
                      {/* Expandable content */}
                      <button
                        onClick={() => setExpandedId(expandedId === doc.id ? null : doc.id)}
                        className="text-xs text-gray-400 hover:text-gray-600 mt-1 flex items-center gap-1">
                        <ChevronDown className={`w-3 h-3 transition-transform ${expandedId === doc.id ? "rotate-180" : ""}`} />
                        {expandedId === doc.id ? "Ẩn nội dung" : "Xem nội dung"}
                      </button>
                      {expandedId === doc.id && (
                        <pre className="mt-2 text-xs text-gray-600 bg-gray-50 rounded-lg p-3 max-h-60 overflow-auto whitespace-pre-wrap">
                          {doc.content}
                        </pre>
                      )}
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      <button onClick={() => openEdit(doc)}
                        className="p-1.5 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50">
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button onClick={() => handleDelete(doc.id, doc.title)}
                        className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ===== TAB: VĂN BẢN LUẬT ƯU TIÊN ===== */}
      {mainTab === "law" && (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800">
            <strong>Văn bản Luật ưu tiên (law_documents_v2):</strong> Quản lý cờ <code>is_priority</code> trực tiếp trên kho văn bản luật.
            Các văn bản được đánh dấu ưu tiên sẽ được ưu tiên truy vấn trong RAG.
          </div>

          {/* Sub-tabs: Priority only / All */}
          <div className="flex gap-2 items-center">
            <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => setLawTab("priority")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  lawTab === "priority" ? "bg-white text-[#028a39] shadow-sm" : "text-gray-600 hover:text-gray-900"
                }`}
              >
                <Star className="w-3.5 h-3.5" />
                Đang ưu tiên
              </button>
              <button
                onClick={() => setLawTab("all")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  lawTab === "all" ? "bg-white text-[#028a39] shadow-sm" : "text-gray-600 hover:text-gray-900"
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                Tất cả văn bản
              </button>
            </div>

            {/* Search */}
            <div className="relative flex-1 max-w-sm ml-2">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm"
                placeholder="Tìm tiêu đề, số hiệu..."
                value={lawSearch}
                onChange={e => setLawSearch(e.target.value)}
                onKeyDown={e => e.key === "Enter" && loadLawDocs(lawTab === "priority")}
              />
            </div>
            <button
              onClick={() => loadLawDocs(lawTab === "priority")}
              disabled={lawLoading}
              className="px-3 py-2 bg-[#028a39] text-white rounded-lg text-sm hover:bg-[#016b2c] disabled:opacity-50"
            >
              {lawLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Tìm kiếm"}
            </button>
          </div>

          {/* Law docs table */}
          {lawLoading ? (
            <div className="flex justify-center py-16">
              <Loader2 className="w-8 h-8 animate-spin" style={{ color: "#028a39" }} />
            </div>
          ) : lawDocs.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border border-dashed border-gray-200">
              <Database className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p className="text-gray-500">
                {lawTab === "priority" ? "Chưa có văn bản luật nào được đánh dấu ưu tiên" : "Không tìm thấy văn bản nào"}
              </p>
              {lawTab === "priority" && (
                <p className="text-xs text-gray-400 mt-1">
                  Chuyển sang tab "Tất cả văn bản" để đánh dấu ưu tiên
                </p>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Số hiệu</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Tên văn bản</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Loại</th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wide w-32">Ưu tiên</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {lawDocs.map((doc) => (
                    <tr key={doc.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs text-gray-600 whitespace-nowrap">
                        {doc.doc_number || "—"}
                      </td>
                      <td className="px-4 py-3 text-gray-900 max-w-md">
                        <span className="truncate block" title={doc.title}>{doc.title}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs whitespace-nowrap">
                          {doc.doc_type || "—"}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <button
                          onClick={() => toggleLawPriority(doc.id, doc.is_priority)}
                          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                            doc.is_priority
                              ? "bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200"
                              : "bg-gray-100 text-gray-500 hover:bg-gray-200 border border-gray-200"
                          }`}
                        >
                          <Star className={`w-3.5 h-3.5 ${doc.is_priority ? "fill-amber-400 text-amber-400" : ""}`} />
                          {doc.is_priority ? "Bỏ ưu tiên" : "Đánh dấu"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="px-4 py-3 border-t border-gray-100 text-xs text-gray-400">
                {lawDocs.length} văn bản {lawTab === "priority" ? "đang được đánh dấu ưu tiên" : ""}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-5 border-b">
              <h2 className="font-bold text-gray-900">
                {editingId !== null ? "Chỉnh sửa" : "Thêm"} Priority Doc
              </h2>
              <button onClick={() => setShowModal(false)}
                className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-5 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tiêu đề *</label>
                <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })}
                  placeholder="VD: Thông tư 103/2014/TT-BTC về FCT"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Loại văn bản</label>
                  <div className="relative">
                    <select value={form.doc_type} onChange={(e) => setForm({ ...form, doc_type: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm appearance-none">
                      {DOC_TYPES.map((dt) => (
                        <option key={dt.value} value={dt.value}>{dt.label}</option>
                      ))}
                    </select>
                    <ChevronDown className="absolute right-2 top-2.5 w-4 h-4 text-gray-400 pointer-events-none" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    <Star className="w-3 h-3 inline mr-1" />
                    Priority Level (1=cao nhất)
                  </label>
                  <input type="number" min={1} max={10}
                    value={form.priority_level}
                    onChange={(e) => setForm({ ...form, priority_level: parseInt(e.target.value) || 1 })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
                </div>
                <div className="flex flex-col justify-end">
                  <label className="flex items-center gap-2 cursor-pointer p-2">
                    <input type="checkbox" checked={form.is_active}
                      onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                      className="rounded" />
                    <span className="text-sm text-gray-700">Kích hoạt</span>
                  </label>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">URL nguồn</label>
                <input value={form.source_url} onChange={(e) => setForm({ ...form, source_url: e.target.value })}
                  placeholder="https://thuvienphapluat.vn/..."
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nội dung văn bản *
                  <span className="text-xs text-gray-400 font-normal ml-2">(text đầy đủ để AI đọc)</span>
                </label>
                <textarea value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })}
                  rows={10} placeholder="Paste nội dung văn bản pháp lý vào đây..."
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono resize-y" />
                <p className="text-xs text-gray-400 mt-1">{form.content.length.toLocaleString()} ký tự</p>
              </div>
              <div className="flex gap-3 pt-2">
                <button onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
                  Hủy
                </button>
                <button onClick={handleSave} disabled={saving}
                  className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-white text-sm font-medium disabled:opacity-60"
                  style={{ background: "#028a39" }}>
                  {saving ? <><Loader2 className="w-4 h-4 animate-spin" /> Đang lưu...</> : "Lưu"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
