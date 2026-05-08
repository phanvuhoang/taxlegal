import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Play, CheckCircle, XCircle, Clock, RefreshCw } from "lucide-react";
import { casesApi, Case, CaseEvent } from "../lib/cases";
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

function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] ?? { label: status, bg: "bg-gray-100", text: "text-gray-600" };
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${cfg.bg} ${cfg.text}`}>
      {cfg.label}
    </span>
  );
}

type Tab = "details" | "events" | "versions" | "final";

export default function CaseDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [events, setEvents] = useState<CaseEvent[]>([]);
  const [versions, setVersions] = useState<any[]>([]);
  const [finalOutput, setFinalOutput] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [approving, setApproving] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>("details");
  const [approvalNotes, setApprovalNotes] = useState("");

  const loadCase = async () => {
    if (!id) return;
    try {
      const [caseRes, eventsRes] = await Promise.all([
        casesApi.get(id),
        casesApi.getEvents(id).catch(() => ({ data: [] })),
      ]);
      setCaseData(caseRes.data);
      setEvents(eventsRes.data ?? []);
    } catch {
      toast.error("Không thể tải case");
    } finally {
      setLoading(false);
    }
  };

  const loadFinal = async () => {
    if (!id) return;
    try {
      const res = await casesApi.getFinal(id);
      setFinalOutput(res.data?.final_output ?? res.data?.content ?? null);
    } catch {
      setFinalOutput(null);
    }
  };

  const loadVersions = async () => {
    if (!id) return;
    try {
      const res = await casesApi.getVersions(id);
      setVersions(res.data ?? []);
    } catch {
      setVersions([]);
    }
  };

  useEffect(() => { loadCase(); }, [id]);
  useEffect(() => {
    if (activeTab === "final") loadFinal();
    if (activeTab === "versions") loadVersions();
  }, [activeTab]);

  const handleStart = async () => {
    if (!id) return;
    setStarting(true);
    try {
      await casesApi.start(id, { use_legacy_pipeline: true });
      toast.success("Workflow đã được khởi động!");
      loadCase();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Không thể bắt đầu workflow");
    } finally {
      setStarting(false);
    }
  };

  const handleApproval = async (decision: "approved" | "rejected") => {
    if (!id) return;
    setApproving(true);
    try {
      await casesApi.humanApproval(id, decision, approvalNotes || undefined);
      toast.success(decision === "approved" ? "Đã duyệt thành công!" : "Đã từ chối.");
      loadCase();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Lỗi khi xử lý approval");
    } finally {
      setApproving(false);
    }
  };

  const TABS: { key: Tab; label: string }[] = [
    { key: "details",  label: "Chi tiết" },
    { key: "events",   label: `Sự kiện${events.length ? ` (${events.length})` : ""}` },
    { key: "versions", label: "Phiên bản" },
    { key: "final",    label: "Kết quả" },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-7 h-7 border-2 border-gray-200 border-t-green-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-500">Không tìm thấy case</p>
        <button onClick={() => navigate("/cases")} className="mt-3 text-sm underline" style={{ color: PRIMARY }}>
          Quay lại danh sách
        </button>
      </div>
    );
  }

  const canStart = caseData.status === "draft";
  const needsApproval = caseData.status === "human_approval";

  return (
    <div className="space-y-5">
      {/* Back */}
      <button
        onClick={() => navigate("/cases")}
        className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Quay lại Cases
      </button>

      {/* Header card */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-lg font-bold text-gray-900">{caseData.title}</h1>
              <StatusBadge status={caseData.status} />
            </div>
            {caseData.current_node && (
              <p className="text-xs text-gray-400 mt-1">
                Node hiện tại: <span className="font-medium text-gray-600">{caseData.current_node}</span>
              </p>
            )}
            <p className="text-xs text-gray-400 mt-1">ID: {caseData.id}</p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={loadCase}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
              title="Tải lại"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            {canStart && (
              <button
                onClick={handleStart}
                disabled={starting}
                className="flex items-center gap-2 px-4 py-2 text-white text-sm font-medium rounded-lg disabled:opacity-60 transition-opacity"
                style={{ background: PRIMARY }}
              >
                {starting ? (
                  <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
                {starting ? "Đang khởi động..." : "Start Workflow"}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Human approval section */}
      {needsApproval && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5">
          <div className="flex items-start gap-3">
            <Clock className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
            <div className="flex-1">
              <h3 className="font-semibold text-amber-900">Cần phê duyệt thủ công</h3>
              <p className="text-sm text-amber-700 mt-1">
                Case này có điểm rủi ro cao và cần Partner/Admin phê duyệt trước khi giao.
              </p>
              <div className="mt-3">
                <textarea
                  className="w-full border border-amber-200 rounded-lg px-3 py-2 text-sm bg-white placeholder-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-400"
                  rows={2}
                  placeholder="Ghi chú (tùy chọn)..."
                  value={approvalNotes}
                  onChange={(e) => setApprovalNotes(e.target.value)}
                />
              </div>
              <div className="flex items-center gap-2 mt-3">
                <button
                  onClick={() => handleApproval("approved")}
                  disabled={approving}
                  className="flex items-center gap-2 px-4 py-2 text-white text-sm font-medium rounded-lg disabled:opacity-60"
                  style={{ background: PRIMARY }}
                >
                  <CheckCircle className="w-4 h-4" />
                  Duyệt
                </button>
                <button
                  onClick={() => handleApproval("rejected")}
                  disabled={approving}
                  className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 disabled:opacity-60"
                >
                  <XCircle className="w-4 h-4" />
                  Từ chối
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="flex border-b border-gray-100">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-5 py-3 text-sm font-medium transition-colors border-b-2 ${
                activeTab === tab.key
                  ? "border-current"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
              style={activeTab === tab.key ? { color: PRIMARY, borderColor: PRIMARY } : {}}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-5">
          {/* Details tab */}
          {activeTab === "details" && (
            <div className="space-y-4">
              <div>
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Yêu cầu khách hàng</p>
                <p className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 rounded-lg p-3">{caseData.client_request}</p>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Lĩnh vực</p>
                  <p className="text-gray-700 capitalize">{caseData.practice_area}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Ngôn ngữ</p>
                  <p className="text-gray-700 uppercase">{caseData.output_language}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Ưu tiên</p>
                  <p className="text-gray-700 capitalize">{caseData.priority}</p>
                </div>
                {caseData.quality_score !== null && (
                  <div>
                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Điểm chất lượng</p>
                    <p className="text-gray-700 font-semibold">{caseData.quality_score}/10</p>
                  </div>
                )}
                <div>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Ngày tạo</p>
                  <p className="text-gray-700">{new Date(caseData.created_at).toLocaleString("vi-VN")}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Cập nhật</p>
                  <p className="text-gray-700">{new Date(caseData.updated_at).toLocaleString("vi-VN")}</p>
                </div>
              </div>
            </div>
          )}

          {/* Events tab */}
          {activeTab === "events" && (
            <div>
              {events.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-8">Chưa có sự kiện nào</p>
              ) : (
                <ol className="relative border-l border-gray-200 ml-3 space-y-5">
                  {events.map((ev) => (
                    <li key={ev.id} className="ml-5">
                      <div className="absolute -left-1.5 mt-1 w-3 h-3 rounded-full border-2 border-white" style={{ background: PRIMARY }} />
                      <div>
                        <p className="text-xs text-gray-400">{new Date(ev.created_at).toLocaleString("vi-VN")}</p>
                        <p className="text-sm font-medium text-gray-800 mt-0.5">
                          {ev.event_type}
                          {ev.node_name && <span className="text-gray-400 font-normal"> — {ev.node_name}</span>}
                        </p>
                        {ev.actor && <p className="text-xs text-gray-500">bởi {ev.actor}</p>}
                        {Object.keys(ev.data ?? {}).length > 0 && (
                          <pre className="mt-1 text-xs bg-gray-50 rounded p-2 overflow-x-auto text-gray-600">
                            {JSON.stringify(ev.data, null, 2)}
                          </pre>
                        )}
                      </div>
                    </li>
                  ))}
                </ol>
              )}
            </div>
          )}

          {/* Versions tab */}
          {activeTab === "versions" && (
            <div>
              {versions.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-8">Chưa có phiên bản nào</p>
              ) : (
                <div className="space-y-3">
                  {versions.map((v: any) => (
                    <div key={v.id ?? v.version_number} className="border border-gray-100 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-gray-700">
                          Phiên bản {v.version_number ?? v.draft_version}
                        </span>
                        <span className="text-xs text-gray-400">
                          {v.created_at ? new Date(v.created_at).toLocaleString("vi-VN") : ""}
                        </span>
                      </div>
                      {v.content && (
                        <p className="text-sm text-gray-600 line-clamp-3 whitespace-pre-wrap">{v.content}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Final output tab */}
          {activeTab === "final" && (
            <div>
              {!finalOutput ? (
                <p className="text-sm text-gray-400 text-center py-8">
                  {caseData.status === "delivered" ? "Đang tải kết quả..." : "Case chưa hoàn thành"}
                </p>
              ) : (
                <div className="prose prose-sm max-w-none">
                  <pre className="whitespace-pre-wrap text-sm text-gray-800 bg-gray-50 rounded-lg p-4 leading-relaxed">
                    {finalOutput}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
