import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { mattersApi } from "../lib/api";
import PipelineTracker from "../components/PipelineTracker";
import ReasonCodeBadge from "../components/ReasonCodeBadge";
import ModelPicker from "../components/ModelPicker";
import ReactMarkdown from "react-markdown";
import {
  ArrowLeft, Download, Star, RefreshCw, AlertCircle,
  CheckCircle, X, ChevronDown, ChevronUp
} from "lucide-react";
import toast from "react-hot-toast";
import { isAdmin } from "../lib/auth";

export default function MatterDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [matter, setMatter] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [approving, setApproving] = useState<number | null>(null);
  const [viewingStep, setViewingStep] = useState<any>(null);
  const [modelOverride, setModelOverride] = useState("");
  const [showFinal, setShowFinal] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const load = useCallback(async () => {
    try {
      const r = await mattersApi.get(Number(id));
      setMatter(r.data);
      // Auto-refresh if pipeline is running
      const isRunning = ["intake", "partner_p1", "sa_blueprint", "ja_research",
        "sa_review", "partner_p2", "partner_p3"].includes(r.data.status);
      setAutoRefresh(isRunning);
    } catch {
      toast.error("Không tìm thấy matter");
      navigate("/matters");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [autoRefresh, load]);

  const handleApprove = async (stepNumber: number) => {
    setApproving(stepNumber);
    try {
      await mattersApi.approveStep(Number(id), stepNumber, {
        notes: "",
        model_override: modelOverride || undefined,
      });
      toast.success(`Bước ${stepNumber} đã approve. Bước tiếp theo đang chạy...`);
      setAutoRefresh(true);
      setTimeout(load, 2000);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Lỗi approve");
    } finally {
      setApproving(null);
    }
  };

  const handleMarkSample = async () => {
    try {
      const r = await mattersApi.markSample(Number(id));
      toast.success(r.data.is_sample ? "Đã đánh dấu là bài mẫu" : "Đã bỏ đánh dấu bài mẫu");
      load();
    } catch {
      toast.error("Lỗi");
    }
  };

  const downloadFinal = () => {
    if (!matter?.final_content) return;
    const blob = new Blob([matter.final_content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${matter.title.replace(/\s+/g, "_")}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!matter) return null;

  const criticalCodes = (matter.reason_codes || []).filter((r: any) => r.severity === "CRITICAL");

  return (
    <div>
      {/* Header */}
      <div className="flex items-start gap-3 mb-6">
        <button onClick={() => navigate("/matters")} className="text-gray-400 hover:text-gray-600 mt-1">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-xl font-bold text-gray-900">{matter.title}</h1>
            {matter.is_sample && <span className="badge badge-purple">Bài Mẫu</span>}
            <span className={`badge ${matter.pipeline_mode === "auto" ? "badge-blue" : "badge-gray"}`}>
              {matter.pipeline_mode === "auto" ? "Auto" : "Manual"}
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-0.5 capitalize">{matter.practice_area} · {matter.client_request.slice(0, 80)}...</p>
        </div>
        <div className="flex items-center gap-2">
          {autoRefresh && (
            <div className="flex items-center gap-1 text-xs text-blue-500">
              <RefreshCw className="w-3 h-3 animate-spin" />
              Live
            </div>
          )}
          <button onClick={load} className="btn-secondary text-sm flex items-center gap-1">
            <RefreshCw className="w-3.5 h-3.5" /> Refresh
          </button>
          {isAdmin() && (
            <button onClick={handleMarkSample} className="btn-secondary text-sm flex items-center gap-1">
              <Star className={`w-3.5 h-3.5 ${matter.is_sample ? "text-yellow-400 fill-yellow-400" : ""}`} />
              {matter.is_sample ? "Bỏ mẫu" : "Đánh dấu mẫu"}
            </button>
          )}
          {matter.final_content && (
            <button onClick={downloadFinal} className="btn-primary text-sm flex items-center gap-1">
              <Download className="w-3.5 h-3.5" /> Tải xuống
            </button>
          )}
        </div>
      </div>

      {/* Quality & Critical issues */}
      {(matter.quality_score || criticalCodes.length > 0) && (
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          {matter.quality_score && (
            <div className="card p-4 flex items-center gap-3">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-white text-lg font-bold ${
                matter.quality_score >= 80 ? "bg-green-500" :
                matter.quality_score >= 60 ? "bg-yellow-500" : "bg-red-500"
              }`}>
                {Math.round(matter.quality_score)}
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-900">Quality Score</p>
                <p className="text-xs text-gray-500">{matter.verification_chain_status || "Pending"}</p>
              </div>
            </div>
          )}
          {criticalCodes.length > 0 && (
            <div className="card p-4">
              <p className="text-sm font-semibold text-red-700 flex items-center gap-1 mb-2">
                <AlertCircle className="w-4 h-4" /> {criticalCodes.length} Critical Issues
              </p>
              <div className="space-y-1">
                {criticalCodes.slice(0, 3).map((rc: any, i: number) => (
                  <ReasonCodeBadge key={i} code={rc.code} detail={rc.detail} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-6">
        {/* Left: Pipeline + Info */}
        <div className="md:col-span-1 space-y-4">
          {/* Pipeline tracker */}
          <div className="card">
            <h2 className="text-sm font-semibold text-gray-900 mb-3">Pipeline Progress</h2>
            {matter.pipeline_mode === "manual" && matter.status !== "completed" && (
              <div className="mb-3 p-2 bg-blue-50 rounded-lg">
                <ModelPicker
                  value={modelOverride}
                  onChange={setModelOverride}
                  label="Model cho bước tiếp theo"
                />
              </div>
            )}
            <PipelineTracker
              steps={matter.steps || []}
              currentStep={matter.current_step}
              pipelineMode={matter.pipeline_mode}
              onApprove={handleApprove}
              onViewStep={setViewingStep}
              approving={approving}
            />
          </div>

          {/* Facts summary */}
          {(matter.verified_facts?.length > 0) && (
            <div className="card">
              <h3 className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wider">
                Verified Facts ({matter.verified_facts.length})
              </h3>
              <div className="space-y-1">
                {matter.verified_facts.slice(0, 5).map((f: any, i: number) => (
                  <div key={i} className="flex items-start gap-2 text-xs">
                    <span className={`badge flex-shrink-0 mt-0.5 ${
                      f.status === "VERIFIED" ? "badge-green" :
                      f.status === "CLIENT-STATED" ? "badge-blue" :
                      f.status === "CONFLICTING" ? "badge-red" : "badge-yellow"
                    }`}>{f.status}</span>
                    <span className="text-gray-600 truncate">{f.fact}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Laws */}
          {(matter.applicable_laws?.length > 0) && (
            <div className="card">
              <h3 className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wider">
                Văn bản áp dụng ({matter.applicable_laws.length})
              </h3>
              <div className="space-y-1">
                {matter.applicable_laws.slice(0, 5).map((l: any, i: number) => (
                  <div key={i} className="flex items-start gap-2 text-xs">
                    <span className={`badge flex-shrink-0 mt-0.5 ${
                      l.status === "CURRENT" ? "badge-green" : "badge-red"
                    }`}>{l.status}</span>
                    <span className="text-gray-600 truncate">{l.law_id || l.so_hieu}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: Content */}
        <div className="md:col-span-2 space-y-4">
          {/* Final output */}
          {matter.final_content && (
            <div className="card">
              <button
                className="w-full flex items-center justify-between text-sm font-semibold text-gray-900"
                onClick={() => setShowFinal(!showFinal)}
              >
                <span className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  Văn bản Tư vấn Cuối
                </span>
                {showFinal ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              {showFinal && (
                <div className="mt-4 prose prose-sm max-w-none border-t pt-4">
                  <ReactMarkdown>{matter.final_content}</ReactMarkdown>
                </div>
              )}
            </div>
          )}

          {/* Client request */}
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-900 mb-2">Yêu cầu Khách hàng</h3>
            <pre className="text-xs text-gray-700 whitespace-pre-wrap font-sans leading-relaxed bg-gray-50 p-3 rounded-lg">
              {matter.client_request}
            </pre>
          </div>
        </div>
      </div>

      {/* Step viewer modal */}
      {viewingStep && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="font-semibold text-gray-900">
                Bước {viewingStep.step_number}: {viewingStep.step_name}
              </h3>
              <button onClick={() => setViewingStep(null)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              <div className="flex items-center gap-3 text-xs text-gray-500 mb-4 flex-wrap">
                {viewingStep.model_used && <span>Model: {viewingStep.model_used}</span>}
                {viewingStep.word_count && <span>{viewingStep.word_count.toLocaleString()} từ</span>}
                {viewingStep.duration_ms && <span>{(viewingStep.duration_ms / 1000).toFixed(1)}s</span>}
                {viewingStep.prompt_tokens > 0 && (
                  <span>{(viewingStep.prompt_tokens + viewingStep.completion_tokens).toLocaleString()} tokens</span>
                )}
              </div>
              {viewingStep.reason_codes_found?.length > 0 && (
                <div className="mb-4 space-y-1">
                  {viewingStep.reason_codes_found.map((rc: any, i: number) => (
                    <ReasonCodeBadge key={i} code={rc.code} detail={rc.detail} />
                  ))}
                </div>
              )}
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{viewingStep.output_markdown || ""}</ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
