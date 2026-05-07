/**
 * Sample Writings — public browsable page (Module 2)
 * Filter by category, language, content type, search
 */
import { useEffect, useState } from "react";
import { Library, Search, Filter } from "lucide-react";
import api from "../lib/api";
import toast from "react-hot-toast";
import { CONTENT_TYPES } from "../lib/writing";

interface SampleWriting {
  id: number;
  title: string;
  content_type: string;
  language: string;
  content: string;
  tags: string[];
  category: string | null;
  topic: string | null;
  is_active: boolean;
  created_at: string | null;
}

export default function SampleWritingsPublic() {
  const [items, setItems] = useState<SampleWriting[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterLang, setFilterLang] = useState("all");
  const [filterType, setFilterType] = useState("all");
  const [filterCategory, setFilterCategory] = useState("all");
  const [expandedId, setExpandedId] = useState<number | null>(null);

  useEffect(() => {
    api.get("/api/sample-writings")
      .then((r) => setItems(r.data.filter((i: SampleWriting) => i.is_active)))
      .catch(() => toast.error("Không thể tải bài viết mẫu"))
      .finally(() => setLoading(false));
  }, []);

  const categories = ["all", ...Array.from(new Set(items.map((i) => i.category).filter(Boolean))) as string[]];
  const ctLabel = (ct: string) => CONTENT_TYPES.find((c) => c.value === ct)?.label || ct;

  const filtered = items.filter((item) => {
    if (filterLang !== "all" && item.language !== filterLang) return false;
    if (filterType !== "all" && item.content_type !== filterType) return false;
    if (filterCategory !== "all" && item.category !== filterCategory) return false;
    if (search && !item.title.toLowerCase().includes(search.toLowerCase()) &&
        !item.content.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: "#028a39" }}>
          <Library className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Bài viết mẫu</h1>
          <p className="text-sm text-gray-500">Thư viện bài phân tích thuế tham khảo</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-100 p-4 space-y-3">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Tìm kiếm theo tiêu đề, nội dung..."
              className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2"
              style={{ "--tw-ring-color": "#028a39" } as any}
            />
          </div>
          <Filter className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-400">{filtered.length} bài</span>
        </div>
        <div className="flex gap-2 flex-wrap">
          {/* Language filter */}
          {["all", "vi", "en"].map((lang) => (
            <button key={lang} onClick={() => setFilterLang(lang)}
              className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                filterLang === lang ? "bg-green-50 border-green-600 text-green-700 font-medium" : "border-gray-200 text-gray-600 hover:bg-gray-50"
              }`}>
              {lang === "all" ? "Tất cả ngôn ngữ" : lang === "vi" ? "🇻🇳 VI" : "🇺🇸 EN"}
            </button>
          ))}
          <div className="w-px bg-gray-200 self-stretch" />
          {/* Content type filter */}
          {["all", ...CONTENT_TYPES.map((c) => c.value)].map((ct) => (
            <button key={ct} onClick={() => setFilterType(ct)}
              className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                filterType === ct ? "bg-green-50 border-green-600 text-green-700 font-medium" : "border-gray-200 text-gray-600 hover:bg-gray-50"
              }`}>
              {ct === "all" ? "Tất cả loại" : ctLabel(ct)}
            </button>
          ))}
          {categories.length > 1 && (
            <>
              <div className="w-px bg-gray-200 self-stretch" />
              {categories.map((cat) => (
                <button key={cat} onClick={() => setFilterCategory(cat)}
                  className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                    filterCategory === cat ? "bg-blue-50 border-blue-500 text-blue-700 font-medium" : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}>
                  {cat === "all" ? "Tất cả chủ đề" : cat}
                </button>
              ))}
            </>
          )}
        </div>
      </div>

      {/* List */}
      {loading ? (
        <div className="text-center py-10 text-gray-400">Đang tải...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-dashed border-gray-200">
          <Library className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="text-gray-500">Không tìm thấy bài viết phù hợp</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((item) => (
            <div key={item.id} className="bg-white rounded-xl border border-gray-100 p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-semibold text-gray-900">{item.title}</h3>
                    <span className={`px-2 py-0.5 text-xs rounded-full font-medium ${
                      item.language === "vi" ? "bg-red-50 text-red-700" : "bg-blue-50 text-blue-700"
                    }`}>{item.language.toUpperCase()}</span>
                    <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-600">{ctLabel(item.content_type)}</span>
                    {item.category && <span className="px-2 py-0.5 text-xs rounded-full bg-amber-50 text-amber-700">{item.category}</span>}
                  </div>
                  {item.topic && <p className="text-xs text-gray-500 mt-0.5">{item.topic}</p>}
                  {item.tags?.length > 0 && (
                    <div className="flex gap-1 mt-1 flex-wrap">
                      {item.tags.map((tag) => (
                        <span key={tag} className="px-1.5 py-0.5 text-xs bg-green-50 text-green-700 rounded">#{tag}</span>
                      ))}
                    </div>
                  )}
                </div>
                <button
                  onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}
                  className="px-3 py-1.5 rounded-lg border border-gray-200 text-xs text-gray-600 hover:bg-gray-50 shrink-0"
                >
                  {expandedId === item.id ? "Đóng" : "Xem"}
                </button>
              </div>
              {expandedId === item.id && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans leading-relaxed max-h-[500px] overflow-auto">
                    {item.content}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
