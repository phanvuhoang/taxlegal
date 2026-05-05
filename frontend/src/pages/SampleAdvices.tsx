import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { adminApi } from "../lib/api";
import { BookOpen, Plus, Trash2, Star } from "lucide-react";
import { isAdmin } from "../lib/auth";
import toast from "react-hot-toast";
import ReactMarkdown from "react-markdown";

export default function SampleAdvices() {
  const [advices, setAdvices] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ title: "", practice_area: "tax", tags: "", client_question: "", content_markdown: "" });

  const load = () => adminApi.listSampleAdvices().then((r) => setAdvices(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const handleView = async (id: number) => {
    const r = await adminApi.getSampleAdvice(id);
    setSelected(r.data);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await adminApi.createSampleAdvice({
        ...form,
        tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean),
      });
      toast.success("Đã tạo bài mẫu");
      setShowAdd(false);
      setForm({ title: "", practice_area: "tax", tags: "", client_question: "", content_markdown: "" });
      load();
    } catch { toast.error("Lỗi"); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Xoá bài mẫu này?")) return;
    try {
      await adminApi.deleteSampleAdvice(id);
      toast.success("Đã xoá");
      setSelected(null);
      load();
    } catch { toast.error("Lỗi"); }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-primary-500" /> Bài Mẫu Tham Khảo
          </h1>
          <p className="text-gray-500 text-sm mt-1">Thư viện bài tư vấn mẫu chất lượng cao</p>
        </div>
        {isAdmin() && (
          <button onClick={() => setShowAdd(!showAdd)} className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" /> Thêm Bài Mẫu
          </button>
        )}
      </div>

      {showAdd && (
        <div className="card mb-4">
          <h3 className="font-semibold text-gray-900 mb-3">Thêm bài mẫu mới</h3>
          <form onSubmit={handleCreate} className="space-y-3">
            <input className="input-field" placeholder="Tiêu đề" value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })} required />
            <div className="grid grid-cols-2 gap-3">
              <select className="input-field" value={form.practice_area}
                onChange={(e) => setForm({ ...form, practice_area: e.target.value })}>
                <option value="tax">Tax</option>
                <option value="legal">Legal</option>
                <option value="both">Cả hai</option>
              </select>
              <input className="input-field" placeholder="Tags (cách nhau bởi dấu phẩy)" value={form.tags}
                onChange={(e) => setForm({ ...form, tags: e.target.value })} />
            </div>
            <textarea className="input-field min-h-16" placeholder="Câu hỏi khách hàng (tùy chọn)" value={form.client_question}
              onChange={(e) => setForm({ ...form, client_question: e.target.value })} />
            <textarea className="input-field min-h-48 font-mono text-xs" placeholder="Nội dung bài mẫu (Markdown)..." value={form.content_markdown}
              onChange={(e) => setForm({ ...form, content_markdown: e.target.value })} required />
            <div className="flex gap-2 justify-end">
              <button type="button" onClick={() => setShowAdd(false)} className="btn-secondary">Huỷ</button>
              <button type="submit" className="btn-primary">Tạo</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-6">
        {/* List */}
        <div className="md:col-span-1">
          <div className="space-y-2">
            {advices.length === 0 ? (
              <div className="card text-center text-gray-400 text-sm py-8">Chưa có bài mẫu nào</div>
            ) : advices.map((a) => (
              <button
                key={a.id}
                onClick={() => handleView(a.id)}
                className={`w-full text-left card p-3 hover:border-primary-200 transition-colors ${
                  selected?.id === a.id ? "border-primary-300 bg-primary-50" : ""
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{a.title}</p>
                    <div className="flex items-center gap-1 mt-1 flex-wrap">
                      <span className="badge badge-blue text-xs">{a.practice_area}</span>
                      {a.tags?.slice(0, 2).map((tag: string) => (
                        <span key={tag} className="badge badge-gray text-xs">{tag}</span>
                      ))}
                    </div>
                    {a.quality_score && (
                      <p className="text-xs text-green-600 flex items-center gap-1 mt-1">
                        <Star className="w-3 h-3 fill-current" /> {a.quality_score}/100
                      </p>
                    )}
                  </div>
                  {isAdmin() && (
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDelete(a.id); }}
                      className="text-gray-300 hover:text-red-500 flex-shrink-0 ml-2"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Viewer */}
        <div className="md:col-span-2">
          {selected ? (
            <div className="card">
              <div className="mb-4 pb-4 border-b">
                <h2 className="font-semibold text-gray-900 text-lg">{selected.title}</h2>
                {selected.client_question && (
                  <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs font-semibold text-gray-500 mb-1">Câu hỏi khách hàng:</p>
                    <p className="text-sm text-gray-700">{selected.client_question}</p>
                  </div>
                )}
              </div>
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{selected.content_markdown || ""}</ReactMarkdown>
              </div>
            </div>
          ) : (
            <div className="card flex items-center justify-center py-16 text-gray-400">
              <div className="text-center">
                <BookOpen className="w-10 h-10 mx-auto mb-3 opacity-30" />
                <p>Chọn một bài mẫu để xem nội dung</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
