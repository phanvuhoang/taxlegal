import { useState } from "react";
import { lawsApi } from "../lib/api";
import { Search, Scale, ExternalLink, Plus } from "lucide-react";
import { isAdmin } from "../lib/auth";
import toast from "react-hot-toast";

export default function Laws() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchType, setSearchType] = useState<"local" | "dbvntax">("local");
  const [selected, setSelected] = useState<any>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      if (searchType === "dbvntax") {
        const r = await lawsApi.searchDbvntax(query);
        setResults(r.data);
      } else {
        const r = await lawsApi.search(query);
        setResults(r.data);
      }
    } catch { toast.error("Lỗi tìm kiếm"); }
    finally { setLoading(false); }
  };

  const handleView = async (id: number) => {
    try {
      const r = await lawsApi.get(id);
      setSelected(r.data);
    } catch { toast.error("Lỗi"); }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Scale className="w-6 h-6 text-primary-500" /> Văn Bản Pháp Luật
        </h1>
        <p className="text-gray-500 text-sm mt-1">Tra cứu văn bản pháp lý từ database</p>
      </div>

      {/* Search */}
      <div className="card mb-4">
        <div className="flex items-center gap-3">
          <div className="flex rounded-lg border border-gray-200 overflow-hidden text-sm">
            {[
              { key: "local", label: "Taxlegal DB" },
              { key: "dbvntax", label: "DBvntax (Tax)" },
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setSearchType(key as any)}
                className={`px-3 py-2 text-xs font-medium transition-colors ${
                  searchType === key ? "bg-primary-500 text-white" : "text-gray-600 hover:bg-gray-50"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              className="input-field pl-9"
              placeholder="Nhập số hiệu hoặc tên văn bản..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
          </div>
          <button onClick={handleSearch} disabled={loading} className="btn-primary">
            {loading ? "Đang tìm..." : "Tìm kiếm"}
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-5 gap-6">
        {/* Results */}
        <div className="md:col-span-2">
          <div className="space-y-2">
            {results.length === 0 ? (
              <div className="card text-center text-gray-400 text-sm py-8">
                <Scale className="w-8 h-8 mx-auto mb-2 opacity-30" />
                <p>Nhập từ khoá và tìm kiếm</p>
              </div>
            ) : results.map((law) => (
              <button
                key={law.id}
                onClick={() => law.id ? handleView(law.id) : setSelected(law)}
                className={`w-full text-left card p-3 hover:border-primary-200 transition-colors ${
                  selected?.id === law.id ? "border-primary-300 bg-primary-50" : ""
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-primary-600">{law.so_hieu}</p>
                    <p className="text-sm text-gray-800 mt-0.5 leading-snug">{law.ten}</p>
                    <div className="flex items-center gap-2 mt-1">
                      {law.loai && <span className="badge badge-blue text-xs">{law.loai}</span>}
                      <span className={`badge text-xs ${
                        law.tinh_trang === "con_hieu_luc" || !law.het_hieu_luc_tu
                          ? "badge-green" : "badge-red"
                      }`}>
                        {law.het_hieu_luc_tu ? "Hết hiệu lực" : "Còn hiệu lực"}
                      </span>
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Detail */}
        <div className="md:col-span-3">
          {selected ? (
            <div className="card">
              <div className="mb-4">
                <p className="text-xs font-bold text-primary-600 uppercase">{selected.so_hieu}</p>
                <h2 className="font-semibold text-gray-900 text-base mt-1">{selected.ten}</h2>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selected.loai && <span className="badge badge-blue">{selected.loai}</span>}
                  {selected.co_quan && <span className="badge badge-gray">{selected.co_quan}</span>}
                  <span className={`badge ${
                    selected.tinh_trang === "con_hieu_luc" ? "badge-green" : "badge-red"
                  }`}>
                    {selected.tinh_trang === "con_hieu_luc" ? "✓ Còn hiệu lực" : "✗ Hết hiệu lực"}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs mb-4">
                {selected.ngay_ban_hanh && (
                  <div><span className="text-gray-400">Ban hành:</span> <span className="text-gray-700">{selected.ngay_ban_hanh}</span></div>
                )}
                {selected.hieu_luc_tu && (
                  <div><span className="text-gray-400">Hiệu lực từ:</span> <span className="text-gray-700">{selected.hieu_luc_tu}</span></div>
                )}
                {selected.het_hieu_luc_tu && (
                  <div><span className="text-red-400">Hết hiệu lực:</span> <span className="text-red-600">{selected.het_hieu_luc_tu}</span></div>
                )}
                {selected.replaced_by && (
                  <div><span className="text-gray-400">Thay thế bởi:</span> <span className="text-orange-600">{selected.replaced_by}</span></div>
                )}
              </div>

              {selected.link_tvpl && (
                <a
                  href={selected.link_tvpl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-primary-600 hover:underline mb-4"
                >
                  <ExternalLink className="w-3 h-3" /> Xem trên TVPL
                </a>
              )}

              {selected.content_text && (
                <div className="mt-4 border-t pt-4">
                  <p className="text-xs font-semibold text-gray-500 mb-2">Nội dung:</p>
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap font-sans leading-relaxed max-h-64 overflow-y-auto">
                    {selected.content_text.slice(0, 3000)}
                    {selected.content_text.length > 3000 ? "\n...[cắt bớt]" : ""}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="card flex items-center justify-center py-16 text-gray-400">
              <div className="text-center">
                <Scale className="w-10 h-10 mx-auto mb-3 opacity-30" />
                <p>Chọn văn bản để xem chi tiết</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
