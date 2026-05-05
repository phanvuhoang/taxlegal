import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { mattersApi } from "../lib/api";
import { Plus, Search, FileText, AlertCircle, Clock, Trash2 } from "lucide-react";
import toast from "react-hot-toast";
import { isAdmin } from "../lib/auth";

const STATUS_LABELS: Record<string, string> = {
  draft: "Draft", intake: "Intake", partner_p1: "Partner P1",
  sa_blueprint: "SA Blueprint", ja_research: "JA Research",
  sa_review: "SA Review", partner_p2: "Partner P2",
  partner_p3: "Partner P3", completed: "Hoàn thành", failed: "Lỗi",
};
const STATUS_COLORS: Record<string, string> = {
  draft: "badge-gray", intake: "badge-purple", partner_p1: "badge-blue",
  sa_blueprint: "badge-yellow", ja_research: "badge-green", sa_review: "badge-yellow",
  partner_p2: "badge-blue", partner_p3: "badge-blue",
  completed: "badge-green", failed: "badge-red",
};

export default function Matters() {
  const [matters, setMatters] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("");

  const load = () => {
    setLoading(true);
    mattersApi.list({ limit: 50, status: filterStatus || undefined })
      .then((r) => setMatters(r.data))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [filterStatus]);

  const filtered = matters.filter((m) =>
    m.title.toLowerCase().includes(search.toLowerCase())
  );

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.preventDefault();
    if (!confirm("Xoá matter này?")) return;
    try {
      await mattersApi.delete(id);
      toast.success("Đã xoá");
      load();
    } catch {
      toast.error("Không thể xoá");
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Matters</h1>
          <p className="text-gray-500 text-sm mt-1">Quản lý các yêu cầu tư vấn</p>
        </div>
        <Link to="/matters/new" className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Tạo Matter
        </Link>
      </div>

      {/* Filters */}
      <div className="card mb-4 p-4 flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            className="input-field pl-9"
            placeholder="Tìm theo tiêu đề..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          className="input-field w-40"
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
        >
          <option value="">Tất cả trạng thái</option>
          {Object.entries(STATUS_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        {loading ? (
          <div className="py-12 text-center text-gray-400">
            <div className="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Đang tải...
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-12 text-center text-gray-400">
            <FileText className="w-8 h-8 mx-auto mb-2 opacity-40" />
            <p>Không có matter nào</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Matter</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Lĩnh vực</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Trạng thái</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Bước</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Điểm</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Ngày</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filtered.map((m) => (
                <tr key={m.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <Link to={`/matters/${m.id}`} className="group">
                      <p className="text-sm font-medium text-gray-900 group-hover:text-primary-600 transition-colors truncate max-w-xs">
                        {m.title}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        {m.is_sample && <span className="badge badge-purple text-xs">Mẫu</span>}
                        {m.reason_codes?.length > 0 && (
                          <span className="flex items-center gap-1 text-xs text-red-500">
                            <AlertCircle className="w-3 h-3" />
                            {m.reason_codes.filter((r: any) => r.severity === "CRITICAL").length} Critical
                          </span>
                        )}
                      </div>
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs text-gray-600 capitalize">{m.practice_area}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`badge ${STATUS_COLORS[m.status] || "badge-gray"}`}>
                      {STATUS_LABELS[m.status] || m.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-500">{m.current_step}/7</td>
                  <td className="px-4 py-3 text-xs font-medium text-green-600">
                    {m.quality_score ? `${m.quality_score}/100` : "—"}
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-400">
                    <Clock className="w-3 h-3 inline mr-1" />
                    {new Date(m.created_at).toLocaleDateString("vi-VN")}
                  </td>
                  <td className="px-4 py-3">
                    {(isAdmin() || true) && (
                      <button
                        onClick={(e) => handleDelete(m.id, e)}
                        className="text-gray-300 hover:text-red-500 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
