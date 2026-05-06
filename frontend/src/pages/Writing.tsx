/**
 * Writing Module — Main list page (/writing)
 * Module 3: Viết bài phân tích thuế
 */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { writingApi, WritingJob, CONTENT_TYPES } from "../lib/writing";
import {
  PenTool, Plus, FileText, Clock, CheckCircle2,
  AlertCircle, Loader2, Trash2, ExternalLink
} from "lucide-react";
import toast from "react-hot-toast";

const STATUS_CONFIG: Record<string, { label: string; icon: any; color: string }> = {
  draft: { label: "Bản nháp", icon: FileText, color: "text-gray-500 bg-gray-50" },
  generating: { label: "Đang tạo...", icon: Loader2, color: "text-blue-600 bg-blue-50" },
  done: { label: "Hoàn thành", icon: CheckCircle2, color: "text-green-700 bg-green-50" },
  error: { label: "Lỗi", icon: AlertCircle, color: "text-red-600 bg-red-50" },
};

export default function Writing() {
  const [jobs, setJobs] = useState<WritingJob[]>([]);
  const [loading, setLoading] = useState(true);

  const loadJobs = async () => {
    try {
      const res = await writingApi.list();
      setJobs(res.data);
    } catch {
      toast.error("Không thể tải danh sách bài viết");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadJobs(); }, []);

  const handleDelete = async (id: number, title: string) => {
    if (!confirm(`Xóa bài viết "${title}"?`)) return;
    try {
      await writingApi.delete(id);
      setJobs((prev) => prev.filter((j) => j.id !== id));
      toast.success("Đã xóa");
    } catch {
      toast.error("Không thể xóa");
    }
  };

  const contentTypeLabel = (ct: string) =>
    CONTENT_TYPES.find((c) => c.value === ct)?.label || ct;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: "#028a39" }}>
            <PenTool className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Viết bài phân tích</h1>
            <p className="text-sm text-gray-500">Tạo bài phân tích thuế chuyên sâu với AI</p>
          </div>
        </div>
        <Link
          to="/writing/new"
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm font-medium"
          style={{ background: "#028a39" }}
        >
          <Plus className="w-4 h-4" />
          Bài viết mới
        </Link>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Tổng bài", value: jobs.length, color: "text-gray-900" },
          { label: "Hoàn thành", value: jobs.filter((j) => j.status === "done").length, color: "text-green-700" },
          { label: "Đang tạo", value: jobs.filter((j) => j.status === "generating").length, color: "text-blue-600" },
          { label: "Lỗi", value: jobs.filter((j) => j.status === "error").length, color: "text-red-600" },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl border border-gray-100 p-4">
            <p className="text-xs text-gray-500">{stat.label}</p>
            <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      {/* List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin" style={{ color: "#028a39" }} />
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-dashed border-gray-200">
          <PenTool className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="text-gray-500 font-medium">Chưa có bài viết nào</p>
          <p className="text-sm text-gray-400 mt-1 mb-4">Tạo bài phân tích thuế đầu tiên của bạn</p>
          <Link
            to="/writing/new"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm font-medium"
            style={{ background: "#028a39" }}
          >
            <Plus className="w-4 h-4" />
            Tạo bài viết
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => {
            const sc = STATUS_CONFIG[job.status] || STATUS_CONFIG.draft;
            const StatusIcon = sc.icon;
            return (
              <div key={job.id}
                className="bg-white rounded-xl border border-gray-100 p-4 hover:border-green-200 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Link
                        to={`/writing/${job.id}`}
                        className="font-semibold text-gray-900 hover:underline truncate"
                      >
                        {job.title}
                      </Link>
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${sc.color}`}>
                        <StatusIcon className={`w-3 h-3 ${job.status === "generating" ? "animate-spin" : ""}`} />
                        {sc.label}
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">
                        {contentTypeLabel(job.content_type)}
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-xs bg-blue-50 text-blue-700 font-semibold">
                        {job.output_language.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">{job.topic}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {job.created_at ? new Date(job.created_at).toLocaleDateString("vi-VN") : "—"}
                      </span>
                      <span>{job.word_count_target.toLocaleString()} từ mục tiêu</span>
                      {job.gamma_url && (
                        <a href={job.gamma_url} target="_blank" rel="noopener noreferrer"
                          className="flex items-center gap-1 text-purple-600 hover:underline">
                          <ExternalLink className="w-3 h-3" />
                          Gamma Slides
                        </a>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Link
                      to={`/writing/${job.id}`}
                      className="px-3 py-1.5 rounded-lg text-xs font-medium border border-gray-200 text-gray-600 hover:bg-gray-50"
                    >
                      Xem
                    </Link>
                    <button
                      onClick={() => handleDelete(job.id, job.title)}
                      className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
