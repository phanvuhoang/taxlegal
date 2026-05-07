/**
 * Document Analysis Detail (/doc-analysis/:id)
 */
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Play, Loader2, CheckCircle2, Copy, ChevronDown, ChevronRight } from "lucide-react";
import api from "../lib/api";
import toast from "react-hot-toast";

const ACTION_LABELS: Record<string, string> = {
  review: "Rà soát văn bản",
  applicable_regulations: "Tư vấn quy định áp dụng",
  legal_risk: "Tư vấn rủi ro pháp luật",
  tax_risk: "Tư vấn rủi ro thuế",
  draft: "Soạn thảo/Chỉnh sửa",
};

export default function DocAnalysisDetail() {
  const { id } = useParams<{id: string}>();
  const navigate = useNavigate();
  const [job, setJob] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [expandedAction, setExpandedAction] = useState<string | null>(null);
  const jobId = parseInt(id || "0");

  const loadJob = async () => {
    try {
      const res = await api.get(`/api/doc-analysis/${jobId}`);
      setJob(res.data);
      if (res.data.status === "analyzing") {
        setTimeout(loadJob, 3000); // poll
      }
    } catch { toast.error("Không tìm thấy"); navigate("/doc-analysis"); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadJob(); }, [jobId]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await api.post(`/api/doc-analysis/${jobId}/analyze`);
      setJob((prev: any) => ({ ...prev, status: "done", results: res.data.results }));
      toast.success("Phân tích hoàn thành!");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Lỗi phân tích");
    } finally { setAnalyzing(false); }
  };

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin" style={{color:"#028a39"}} /></div>;
  if (!job) return null;

  const actions = Array.isArray(job.actions) ? job.actions : (typeof job.actions === "string" ? JSON.parse(job.actions) : []);
  const results = job.results && typeof job.results === "object" ? job.results : (typeof job.results === "string" ? JSON.parse(job.results || "{}") : {});

  return (
    <div className="space-y-5">
      <div className="flex items-start gap-3">
        <button onClick={() => navigate("/doc-analysis")} className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 mt-0.5">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-xl font-bold text-gray-900">{job.title}</h1>
            <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
              job.status === "done" ? "bg-green-50 text-green-700" :
              job.status === "analyzing" ? "bg-blue-50 text-blue-700" :
              job.status === "error" ? "bg-red-50 text-red-600" : "bg-gray-100 text-gray-600"
            }`}>
              {job.status === "done" ? "✓ Hoàn thành" : job.status === "analyzing" ? "⟳ Đang phân tích..." : job.status === "error" ? "✗ Lỗi" : "◉ Chờ"}
            </span>
            <span className="px-2 py-0.5 rounded-full text-xs bg-blue-50 text-blue-700 font-bold">
              {(job.output_language || "vi").toUpperCase()}
            </span>
          </div>
          {job.uploaded_filename && <p className="text-sm text-gray-500 mt-0.5">📄 {job.uploaded_filename}</p>}
        </div>
      </div>

      {/* Analyze button */}
      {job.status !== "done" && (
        <button onClick={handleAnalyze} disabled={analyzing || job.status === "analyzing"}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-white text-sm font-medium disabled:opacity-60"
          style={{ background: "#028a39" }}>
          {analyzing || job.status === "analyzing"
            ? <><Loader2 className="w-4 h-4 animate-spin" /> Đang phân tích...</>
            : <><Play className="w-4 h-4" /> Bắt đầu phân tích</>}
        </button>
      )}

      {/* Results per action */}
      {actions.length > 0 && (
        <div className="space-y-3">
          {actions.map((action: any) => {
            const slug = action.slug;
            const label = ACTION_LABELS[slug] || action.custom_prompt || slug;
            const result = results[slug];
            const isExpanded = expandedAction === slug;
            return (
              <div key={slug} className={`bg-white rounded-xl border transition-colors ${result ? "border-green-100" : "border-gray-100"}`}>
                <button
                  onClick={() => setExpandedAction(isExpanded ? null : slug)}
                  className="w-full flex items-center justify-between p-4"
                >
                  <div className="flex items-center gap-3">
                    {result ? <CheckCircle2 className="w-5 h-5 text-green-600 shrink-0" /> :
                      <div className="w-5 h-5 rounded-full border-2 border-gray-300 shrink-0" />}
                    <div className="text-left">
                      <p className="font-semibold text-gray-800">{label}</p>
                      {action.custom_prompt && !ACTION_LABELS[slug] && (
                        <p className="text-xs text-gray-400 truncate max-w-xs">{action.custom_prompt}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {result && (
                      <button onClick={(e) => { e.stopPropagation(); navigator.clipboard.writeText(result); toast.success("Đã copy"); }}
                        className="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100">
                        <Copy className="w-3.5 h-3.5" />
                      </button>
                    )}
                    {isExpanded ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
                  </div>
                </button>
                {isExpanded && (
                  <div className="px-4 pb-4">
                    {result ? (
                      <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700 whitespace-pre-wrap leading-relaxed max-h-[500px] overflow-auto">
                        {result}
                      </div>
                    ) : (
                      <div className="text-center py-6 text-gray-400 text-sm">
                        {job.status === "analyzing" ? "Đang xử lý..." : "Chưa có kết quả — nhấn \"Bắt đầu phân tích\""}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
