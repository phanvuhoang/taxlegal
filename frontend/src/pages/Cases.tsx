import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Eye, Play, RefreshCw } from "lucide-react";
import { casesApi, Case } from "../lib/cases";
import toast from "react-hot-toast";

const PRIMARY = "#028a39";

const STATUS_CONFIG: Record<string, { label: string; bg: string; text: string }> = {
  draft:          { label: "Nháp",          bg: "bg-gray-100",   text: "text-gray-600" },
  intake:         { label: "Tiếp nhận",     bg: "bg-blue-100",   text: "text-blue-700" },
  researching:    { label: "Nghiên cứu",    bg: "bg-yellow-100", text: "text-yellow-700" },
  drafting:       { label: "Soạn thảo",     bg: "bg-yellow-100", text: "text-yellow-700" },
  sa_review:      { label: "SA Review",     bg: "bg-orange-100", text: "text-orange-700" },
  partner_review: { label: "Partner Review",bg: "bg-purple-100", text: "text-purple-700" },
  human_approval: { label: "Chờ duyệt",     bg: "bg-pink-100",   text: "text-pink-700"  },
  delivered:      { label: "Hoàn thành",    bg: "bg-green-100",  text: "text-green-700" },
  failed:         { label: "Lỗi",           bg: "bg-red-100",    text: "text-red-700"   },
};

const PRACTICE_LABELS: Record<string, string> = {
  tax:   "Thuế",
  legal: "Pháp lý",
  both:  "Thuế & Pháp lý",
};

const PRIORITY_CONFIG: Record<string, { label: string; color: string }> = {
  low:    { label: "Thấp",   color: "text-gray-500" },
  normal: { label: "Bình thường", color: "text-blue-600" },
  high:   { label: "Cao",    color: "text-orange-600" },
  urgent: { label: "Khẩn",   color: "text-red-600" },
};

function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] ?? { label: status, bg: "bg-gray-100", text: "text-gray-600" };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${cfg.bg} ${cfg.text}`}>
      {cfg.label}
    </span>
  );
}

export default function Cases() {
  const navigate = useNavigate();
  const [cases, setCases] = useState<Case[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>("");

  const loadCases = async () => {
    setLoading(true);
    try {
      const res = await casesApi.list({ status: filterStatus || undefined, limit: 50 });
      const data = res.data;
      if (Array.isArray(data)) {
        setCases(data);
        setTotal(data.length);
      } else {
        setCases(data.items ?? []);
        setTotal(data.total ?? 0);
      }
    } catch (err: any) {
      toast.error("Không thể tải danh sách cases");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadCases(); }, [filterStatus]);

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Cases</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {total} vấn đề tư vấn{filterStatus ? ` — lọc: ${STATUS_CONFIG[filterStatus]?.label ?? filterStatus}` : ""}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadCases}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            title="Tải lại"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => navigate("/cases/new")}
            className="flex items-center gap-2 px-4 py-2 text-white text-sm font-medium rounded-lg transition-colors"
            style={{ background: PRIMARY }}
          >
            <Plus className="w-4 h-4" />
            New Case
          </button>
        </div>
      </div>

      {/* Filter bar */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs text-gray-500 font-medium">Lọc:</span>
        {["", ...Object.keys(STATUS_CONFIG)].map((s) => (
          <button
            key={s || "all"}
            onClick={() => setFilterStatus(s)}
            className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
              filterStatus === s
                ? "border-transparent text-white"
                : "border-gray-200 text-gray-600 hover:border-gray-300 bg-white"
            }`}
            style={filterStatus === s ? { background: PRIMARY } : {}}
          >
            {s ? (STATUS_CONFIG[s]?.label ?? s) : "Tất cả"}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-48">
            <div className="w-6 h-6 border-2 border-gray-200 border-t-green-600 rounded-full animate-spin" />
          </div>
        ) : cases.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-gray-400">
            <p className="text-sm">Chưa có case nào</p>
            <button
              onClick={() => navigate("/cases/new")}
              className="mt-3 text-sm font-medium underline"
              style={{ color: PRIMARY }}
            >
              Tạo case đầu tiên
            </button>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Tiêu đề</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Trạng thái</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Lĩnh vực</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Ưu tiên</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Ngày tạo</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {cases.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900 truncate max-w-xs">{c.title}</div>
                    {c.current_node && (
                      <div className="text-xs text-gray-400 mt-0.5">Node: {c.current_node}</div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={c.status} />
                  </td>
                  <td className="px-4 py-3 text-gray-600">
                    {PRACTICE_LABELS[c.practice_area] ?? c.practice_area}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-medium ${PRIORITY_CONFIG[c.priority]?.color ?? "text-gray-500"}`}>
                      {PRIORITY_CONFIG[c.priority]?.label ?? c.priority}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">
                    {new Date(c.created_at).toLocaleDateString("vi-VN")}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1 justify-end">
                      <button
                        onClick={() => navigate(`/cases/${c.id}`)}
                        className="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                        title="Xem chi tiết"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      {c.status === "draft" && (
                        <button
                          onClick={() => navigate(`/cases/${c.id}`)}
                          className="p-1.5 rounded-lg transition-colors text-white"
                          style={{ background: PRIMARY }}
                          title="Bắt đầu"
                        >
                          <Play className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
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
