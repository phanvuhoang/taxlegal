/**
 * Writing Job Detail page (/writing/:id)
 * View, generate, export DOCX, create Gamma slides
 */
import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { writingApi, WritingJob, CONTENT_TYPES } from "../lib/writing";
import {
  ArrowLeft, Loader2, Play, Download, Presentation,
  CheckCircle2, AlertCircle, Clock, FileText,
  Copy, ExternalLink, RefreshCw, Languages
} from "lucide-react";
import toast from "react-hot-toast";

// Simple markdown renderer (no extra deps — just basic formatting)
function MarkdownPreview({ content }: { content: string }) {
  const lines = content.split("\n");
  return (
    <div className="prose prose-sm max-w-none">
      {lines.map((line, i) => {
        if (line.startsWith("### "))
          return <h3 key={i} className="text-base font-semibold text-gray-800 mt-4 mb-1">{line.slice(4)}</h3>;
        if (line.startsWith("## "))
          return <h2 key={i} className="text-lg font-bold mt-5 mb-2" style={{ color: "#028a39" }}>{line.slice(3)}</h2>;
        if (line.startsWith("# "))
          return <h1 key={i} className="text-xl font-bold mt-6 mb-3" style={{ color: "#028a39" }}>{line.slice(2)}</h1>;
        if (line.startsWith("- ") || line.startsWith("* "))
          return <li key={i} className="ml-4 text-sm text-gray-700">{line.slice(2)}</li>;
        if (line.match(/^\d+\. /))
          return <li key={i} className="ml-4 text-sm text-gray-700 list-decimal">{line.replace(/^\d+\. /, "")}</li>;
        if (line.startsWith("---"))
          return <hr key={i} className="my-4 border-gray-200" />;
        if (line.trim() === "")
          return <br key={i} />;
        // Inline bold
        const parts = line.split(/(\*\*[^*]+\*\*)/g);
        return (
          <p key={i} className="text-sm text-gray-700 leading-relaxed">
            {parts.map((part, j) =>
              part.startsWith("**") && part.endsWith("**")
                ? <strong key={j}>{part.slice(2, -2)}</strong>
                : part
            )}
          </p>
        );
      })}
    </div>
  );
}

export default function WritingDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [job, setJob] = useState<WritingJob | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [creatingSlides, setCreatingSlides] = useState(false);
  const [streamContent, setStreamContent] = useState("");
  const [activeTab, setActiveTab] = useState<"preview" | "raw" | "review">("preview");
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const jobId = parseInt(id || "0");

  const loadJob = async () => {
    try {
      const res = await writingApi.get(jobId);
      setJob(res.data);
      if (res.data.status === "generating") {
        startPolling();
      }
    } catch {
      toast.error("Không tìm thấy bài viết");
      navigate("/writing");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJob();
    return () => { if (pollingRef.current) clearInterval(pollingRef.current); };
  }, [jobId]);

  const startPolling = () => {
    if (pollingRef.current) clearInterval(pollingRef.current);
    pollingRef.current = setInterval(async () => {
      try {
        const res = await writingApi.get(jobId);
        setJob(res.data);
        if (res.data.status !== "generating") {
          clearInterval(pollingRef.current!);
          pollingRef.current = null;
          setGenerating(false);
          if (res.data.status === "done") toast.success("Tạo bài viết thành công!");
          else toast.error("Lỗi khi tạo bài viết");
        }
      } catch {
        clearInterval(pollingRef.current!);
        pollingRef.current = null;
        setGenerating(false);
      }
    }, 3000);
  };

  const handleGenerate = async () => {
    if (!job) return;
    setGenerating(true);
    setStreamContent("");
    try {
      // Start SSE stream for live preview
      const token = localStorage.getItem("token");
      const evtSrc = new EventSource(`/api/writing/${jobId}/stream?token=${token}`);
      let collected = "";

      evtSrc.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.chunk) {
            collected += data.chunk;
            setStreamContent(collected);
          }
          if (data.done) {
            evtSrc.close();
            loadJob();
            setGenerating(false);
          }
        } catch { /* ignore parse errors */ }
      };

      evtSrc.onerror = () => {
        evtSrc.close();
        // Fallback: use non-streaming generate
        writingApi.generate(jobId)
          .then(() => { loadJob(); setGenerating(false); })
          .catch(() => { toast.error("Lỗi khi tạo bài viết"); setGenerating(false); });
      };

      // Update local status
      setJob((prev) => prev ? { ...prev, status: "generating" } : prev);
      startPolling();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Lỗi khi tạo bài viết");
      setGenerating(false);
    }
  };

  const handleExportDocx = async () => {
    if (!job) return;
    setExporting(true);
    try {
      await writingApi.exportDocx(jobId, job.title);
      toast.success("Đã tải DOCX");
    } catch {
      toast.error("Lỗi khi xuất DOCX");
    } finally {
      setExporting(false);
    }
  };

  const handleCreateSlides = async () => {
    if (!job) return;
    setCreatingSlides(true);
    try {
      const res = await writingApi.createSlides(jobId);
      setJob((prev) => prev ? { ...prev, gamma_url: res.data.gamma_url } : prev);
      toast.success("Đã tạo Gamma Slides!");
      window.open(res.data.gamma_url, "_blank");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Gamma API chưa khả dụng (cần GAMMA_API_KEY)");
    } finally {
      setCreatingSlides(false);
    }
  };

  const handleCopyContent = () => {
    if (job?.final_content) {
      navigator.clipboard.writeText(job.final_content);
      toast.success("Đã copy nội dung");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin" style={{ color: "#028a39" }} />
      </div>
    );
  }

  if (!job) return null;

  const contentTypeLabel = CONTENT_TYPES.find((c) => c.value === job.content_type)?.label || job.content_type;
  const displayContent = generating && streamContent ? streamContent : job.final_content || "";
  const isDone = job.status === "done";
  const isGenerating = job.status === "generating" || generating;

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-start gap-3">
        <button onClick={() => navigate("/writing")}
          className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 mt-0.5">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-xl font-bold text-gray-900 truncate">{job.title}</h1>
            <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
              isDone ? "bg-green-50 text-green-700" :
              isGenerating ? "bg-blue-50 text-blue-700" :
              job.status === "error" ? "bg-red-50 text-red-600" :
              "bg-gray-100 text-gray-600"
            }`}>
              {isDone ? "✓ Hoàn thành" :
               isGenerating ? "⟳ Đang tạo..." :
               job.status === "error" ? "✗ Lỗi" : "◉ Bản nháp"}
            </span>
            <span className="px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">{contentTypeLabel}</span>
            <span className="px-2 py-0.5 rounded-full text-xs bg-blue-50 text-blue-700 font-bold">
              {job.output_language.toUpperCase()}
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-0.5 line-clamp-2">{job.topic}</p>
        </div>
      </div>

      {/* Action Toolbar */}
      <div className="flex items-center gap-2 flex-wrap">
        {/* Generate button */}
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm font-medium disabled:opacity-60"
          style={{ background: "#028a39" }}
        >
          {isGenerating
            ? <><Loader2 className="w-4 h-4 animate-spin" /> Đang tạo...</>
            : isDone
            ? <><RefreshCw className="w-4 h-4" /> Tạo lại</>
            : <><Play className="w-4 h-4" /> Tạo bài viết</>
          }
        </button>

        {isDone && (
          <>
            <button
              onClick={handleExportDocx}
              disabled={exporting}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-200 text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-60"
            >
              {exporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              Xuất DOCX
            </button>

            <button
              onClick={handleCreateSlides}
              disabled={creatingSlides}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-purple-200 text-sm text-purple-700 bg-purple-50 hover:bg-purple-100 disabled:opacity-60"
            >
              {creatingSlides ? <Loader2 className="w-4 h-4 animate-spin" /> : <Presentation className="w-4 h-4" />}
              Tạo Gamma Slides
            </button>

            <button
              onClick={handleCopyContent}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-200 text-sm text-gray-700 hover:bg-gray-50"
            >
              <Copy className="w-4 h-4" />
              Copy
            </button>
          </>
        )}

        {job.gamma_url && (
          <a
            href={job.gamma_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-purple-200 text-sm text-purple-700 hover:bg-purple-50"
          >
            <ExternalLink className="w-4 h-4" />
            Xem Slides
          </a>
        )}
      </div>

      {/* Content Area */}
      {(displayContent || isGenerating) ? (
        <div className="bg-white rounded-xl border border-gray-100">
          {/* Tab bar */}
          <div className="flex items-center border-b border-gray-100 px-4">
            {["preview", "raw", "review"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab
                    ? tab === "review"
                      ? (job?.review_content ? "border-purple-600 text-purple-700" : "border-gray-400 text-gray-500")
                      : "border-green-600 text-green-700"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                {tab === "preview" ? "Preview" : tab === "raw" ? "Markdown" : (
                  <span className="flex items-center gap-1">
                    Review
                    {job?.review_content && (
                      <span className="w-1.5 h-1.5 rounded-full bg-purple-500 inline-block" />
                    )}
                  </span>
                )}
              </button>
            ))}
            {displayContent && (
              <span className="ml-auto text-xs text-gray-400 pr-2">
                ~{Math.round(displayContent.split(/\s+/).length).toLocaleString()} từ
              </span>
            )}
          </div>
          <div className="p-6">
            {isGenerating && !displayContent ? (
              <div className="flex items-center gap-3 text-gray-500">
                <Loader2 className="w-5 h-5 animate-spin" style={{ color: "#028a39" }} />
                <span>Đang tạo nội dung... (max 16,000 tokens)</span>
              </div>
            ) : activeTab === "preview" ? (
              <MarkdownPreview content={displayContent} />
            ) : activeTab === "raw" ? (
              <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono overflow-auto max-h-[600px]">
                {displayContent}
              </pre>
            ) : activeTab === "review" ? (
              job?.review_content ? (
                <div className="space-y-2">
                  <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                    job.review_status === "done" ? "bg-green-50 text-green-700" :
                    job.review_status === "reviewing" ? "bg-blue-50 text-blue-700" :
                    "bg-gray-100 text-gray-600"
                  }`}>
                    {job.review_status === "done" ? "✓ Review hoàn thành" :
                     job.review_status === "reviewing" ? "⟳ Đang review..." : "◎ " + (job.review_status || "none")}
                  </div>
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                    {job.review_content}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <p className="font-medium">Chưa có review</p>
                  <p className="text-sm mt-1">Chọn Bot review khi tạo bài hoặc tạo bài mới với bot review</p>
                </div>
              )
            ) : null}
          </div>
        </div>
      ) : (
        /* Empty state */
        <div className="bg-white rounded-xl border border-dashed border-gray-200 p-12 text-center">
          <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="text-gray-500 font-medium">Chưa có nội dung</p>
          <p className="text-sm text-gray-400 mt-1 mb-4">
            Nhấn "Tạo bài viết" để AI tạo nội dung dựa trên chủ đề của bạn
          </p>
          <button
            onClick={handleGenerate}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm font-medium"
            style={{ background: "#028a39" }}
          >
            <Play className="w-4 h-4" />
            Tạo bài viết
          </button>
        </div>
      )}

      {/* Meta info */}
      <div className="bg-gray-50 rounded-xl p-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wide">Độ dài mục tiêu</p>
          <p className="font-medium text-gray-700">{job.word_count_target.toLocaleString()} từ</p>
        </div>
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wide">Ngôn ngữ</p>
          <p className="font-medium text-gray-700 flex items-center gap-1">
            <Languages className="w-3 h-3" />
            {job.output_language === "vi" ? "Tiếng Việt" : "English"}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wide">Loại</p>
          <p className="font-medium text-gray-700">{contentTypeLabel}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wide">Tạo lúc</p>
          <p className="font-medium text-gray-700">
            {job.created_at ? new Date(job.created_at).toLocaleString("vi-VN") : "—"}
          </p>
        </div>
      </div>
    </div>
  );
}
