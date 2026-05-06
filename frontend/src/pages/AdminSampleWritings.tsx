/**
 * Admin: Sample Writings vault (/admin/sample-writings)
 * Reference writings for AI to use as style/format examples
 */
import { useEffect, useState } from "react";
import { sampleWritingsApi, SampleWriting, CONTENT_TYPES } from "../lib/writing";
import {
  Library, Plus, Trash2, Loader2, X, ChevronDown, Eye, EyeOff
} from "lucide-react";
import toast from "react-hot-toast";

interface SWForm {
  title: string;
  content_type: string;
  language: string;
  content: string;
  tags: string;
  is_active: boolean;
}

const DEFAULT_FORM: SWForm = {
  title: "",
  content_type: "analysis",
  language: "vi",
  content: "",
  tags: "",
  is_active: true,
};

export default function AdminSampleWritings() {
  const [items, setItems] = useState<SampleWriting[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<SWForm>(DEFAULT_FORM);
  const [saving, setSaving] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [filterLang, setFilterLang] = useState<string>("all");

  const loadItems = async () => {
    try {
      const res = await sampleWritingsApi.list();
      setItems(res.data);
    } catch {
      toast.error("Không thể tải sample writings");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadItems(); }, []);

  const handleSave = async () => {
    if (!form.title.trim()) { toast.error("Vui lòng nhập tiêu đề"); return; }
    if (!form.content.trim()) { toast.error("Vui lòng nhập nội dung"); return; }
    setSaving(true);
    try {
      await sampleWritingsApi.create({
        ...form,
        tags: form.tags ? form.tags.split(",").map((t) => t.trim()).filter(Boolean) : [],
      });
      toast.success("Đã thêm sample writing");
      setShowModal(false);
      setForm(DEFAULT_FORM);
      loadItems();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Lỗi khi lưu");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number, title: string) => {
    if (!confirm(`Xóa "${title}"?`)) return;
    try {
      await sampleWritingsApi.delete(id);
      setItems((prev) => prev.filter((i) => i.id !== id));
      toast.success("Đã xóa");
    } catch {
      toast.error("Không thể xóa");
    }
  };

  const ctLabel = (ct: string) => CONTENT_TYPES.find((c) => c.value === ct)?.label || ct;

  const filtered = filterLang === "all" ? items : items.filter((i) => i.language === filterLang);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: "#028a39" }}>
            <Library className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Sample Writing Vault</h1>
            <p className="text-sm text-gray-500">Bài viết mẫu tham khảo — style & format reference cho AI</p>
          </div>
        </div>
        <button
          onClick={() => { setForm(DEFAULT_FORM); setShowModal(true); }}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm font-medium"
          style={{ background: "#028a39" }}
        >
          <Plus className="w-4 h-4" />
          Thêm bài mẫu
        </button>
      </div>

      {/* Filter */}
      <div className="flex gap-2">
        {[
          { value: "all", label: "Tất cả" },
          { value: "vi", label: "🇻🇳 Tiếng Việt" },
          { value: "en", label: "🇺🇸 English" },
        ].map((f) => (
          <button
            key={f.value}
            onClick={() => setFilterLang(f.value)}
            className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
              filterLang === f.value
                ? "border-green-600 bg-green-50 text-green-700 font-medium"
                : "border-gray-200 text-gray-600 hover:bg-gray-50"
            }`}
          >
            {f.label} {f.value !== "all" && `(${items.filter((i) => i.language === f.value).length})`}
          </button>
        ))}
        <span className="ml-auto text-sm text-gray-400 self-center">{filtered.length} bài</span>
      </div>

      {/* List */}
      {loading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin" style={{ color: "#028a39" }} />
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-dashed border-gray-200">
          <Library className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="text-gray-500">Chưa có bài mẫu nào</p>
          <p className="text-xs text-gray-400 mt-1 mb-4">Thêm bài viết mẫu để AI học phong cách viết</p>
          <button onClick={() => { setForm(DEFAULT_FORM); setShowModal(true); }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm"
            style={{ background: "#028a39" }}>
            <Plus className="w-4 h-4" /> Thêm bài mẫu
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((item) => (
            <div key={item.id}
              className={`bg-white rounded-xl border transition-colors ${item.is_active ? "border-gray-100" : "border-gray-200 opacity-60"}`}>
              <div className="p-4">
                <div className="flex items-start gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className="font-semibold text-gray-900">{item.title}</p>
                      <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-600">
                        {ctLabel(item.content_type)}
                      </span>
                      <span className={`px-2 py-0.5 text-xs rounded-full font-semibold ${
                        item.language === "vi" ? "bg-red-50 text-red-700" : "bg-blue-50 text-blue-700"
                      }`}>
                        {item.language.toUpperCase()}
                      </span>
                      {!item.is_active && (
                        <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-500">
                          <EyeOff className="w-3 h-3 inline" /> Ẩn
                        </span>
                      )}
                    </div>
                    {item.tags && item.tags.length > 0 && (
                      <div className="flex gap-1 mt-1 flex-wrap">
                        {item.tags.map((tag) => (
                          <span key={tag} className="px-1.5 py-0.5 text-xs bg-green-50 text-green-700 rounded">
                            #{tag}
                          </span>
                        ))}
                      </div>
                    )}
                    <p className="text-xs text-gray-400 mt-1">
                      {item.content.length.toLocaleString()} ký tự ·{" "}
                      {item.created_at ? new Date(item.created_at).toLocaleDateString("vi-VN") : "—"}
                    </p>
                    <button
                      onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}
                      className="text-xs text-gray-400 hover:text-gray-600 mt-1 flex items-center gap-1"
                    >
                      <ChevronDown className={`w-3 h-3 transition-transform ${expandedId === item.id ? "rotate-180" : ""}`} />
                      {expandedId === item.id ? "Ẩn" : "Xem nội dung"}
                    </button>
                    {expandedId === item.id && (
                      <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                        <pre className="text-xs text-gray-700 whitespace-pre-wrap font-sans max-h-80 overflow-auto leading-relaxed">
                          {item.content}
                        </pre>
                      </div>
                    )}
                  </div>
                  <button onClick={() => handleDelete(item.id, item.title)}
                    className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 shrink-0">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-5 border-b">
              <h2 className="font-bold text-gray-900">Thêm bài viết mẫu</h2>
              <button onClick={() => setShowModal(false)}
                className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-5 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tiêu đề *</label>
                <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })}
                  placeholder="VD: Phân tích FCT cho dịch vụ tư vấn nước ngoài"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Loại bài</label>
                  <div className="relative">
                    <select value={form.content_type}
                      onChange={(e) => setForm({ ...form, content_type: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm appearance-none">
                      {CONTENT_TYPES.map((ct) => (
                        <option key={ct.value} value={ct.value}>{ct.label}</option>
                      ))}
                    </select>
                    <ChevronDown className="absolute right-2 top-2.5 w-4 h-4 text-gray-400 pointer-events-none" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ngôn ngữ</label>
                  <div className="flex gap-2">
                    {["vi", "en"].map((lang) => (
                      <button key={lang} type="button"
                        onClick={() => setForm({ ...form, language: lang })}
                        className={`flex-1 py-2 rounded-lg text-sm border transition-colors ${
                          form.language === lang
                            ? "border-green-600 bg-green-50 text-green-700"
                            : "border-gray-200 text-gray-600"
                        }`}>
                        {lang.toUpperCase()}
                      </button>
                    ))}
                  </div>
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
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags <span className="text-xs text-gray-400">(phân cách bằng dấu phẩy)</span>
                </label>
                <input value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })}
                  placeholder="fct, circular-103, foreign-contractor"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nội dung bài viết mẫu *
                </label>
                <textarea value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })}
                  rows={12} placeholder="Paste bài viết mẫu vào đây (markdown hoặc plain text)..."
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
                  {saving ? <><Loader2 className="w-4 h-4 animate-spin" /> Đang lưu...</> : "Lưu bài mẫu"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
