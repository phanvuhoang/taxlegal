/**
 * Document Analysis — list page (/doc-analysis)
 * Module 3: Phân tích văn bản
 */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FileSearch, Plus, Loader2, Clock, Trash2 } from "lucide-react";
import api from "../lib/api";
import toast from "react-hot-toast";

interface AnalysisJob {
  id: number;
  title: string;
  uploaded_filename: string | null;
  output_language: string;
  actions: any[];
  status: string;
  created_at: string | null;
}

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  pending: { label: "Chờ phân tích", color: "bg-gray-100 text-gray-600" },
  analyzing: { label: "Đang phân tích...", color: "bg-blue-50 text-blue-700" },
  done: { label: "Hoàn thành", color: "bg-green-50 text-green-700" },
  error: { label: "Lỗi", color: "bg-red-50 text-red-600" },
};

export default function DocAnalysis() {
  const [jobs, setJobs] = useState<AnalysisJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/api/doc-analysis")
      .then((r) => setJobs(r.data))
      .catch(() => toast.error("Không thể tải danh sách"))
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm("Xóa job này?")) return;
    await api.delete(`/api/doc-analysis/${id}`);
    setJobs((prev) => prev.filter((j) => j.id !== id));
    toast.success("Đã xóa");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: "#028a39" }}>
            <FileSearch className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Phân tích văn bản</h1>
            <p className="text-sm text-gray-500">Upload văn bản và phân tích với AI theo từng action</p>
          </div>
        </div>
        <Link to="/doc-analysis/new"
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm font-medium"
          style={{ background: "#028a39" }}>
          <Plus className="w-4 h-4" /> Phân tích mới
        </Link>
      </div>

      {loading ? (
        <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin" style={{ color: "#028a39" }} /></div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-dashed border-gray-200">
          <FileSearch className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="text-gray-500 font-medium">Chưa có phân tích nào</p>
          <p className="text-sm text-gray-400 mt-1 mb-4">Upload hợp đồng, văn bản để AI phân tích</p>
          <Link to="/doc-analysis/new"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm" style={{ background: "#028a39" }}>
            <Plus className="w-4 h-4" /> Phân tích mới
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => {
            const sc = STATUS_CONFIG[job.status] || STATUS_CONFIG.pending;
            const actionCount = Array.isArray(job.actions) ? job.actions.length : 0;
            return (
              <div key={job.id} className="bg-white rounded-xl border border-gray-100 p-4 hover:border-green-200 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Link to={`/doc-analysis/${job.id}`} className="font-semibold text-gray-900 hover:underline">
                        {job.title}
                      </Link>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${sc.color}`}>{sc.label}</span>
                      <span className="px-2 py-0.5 rounded-full text-xs bg-blue-50 text-blue-700 font-semibold">
                        {job.output_language.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 mt-1.5 text-xs text-gray-400">
                      {job.uploaded_filename && <span>📄 {job.uploaded_filename}</span>}
                      <span>{actionCount} actions</span>
                      {job.created_at && <span><Clock className="w-3 h-3 inline mr-0.5" />{new Date(job.created_at).toLocaleDateString("vi-VN")}</span>}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Link to={`/doc-analysis/${job.id}`}
                      className="px-3 py-1.5 rounded-lg text-xs border border-gray-200 text-gray-600 hover:bg-gray-50">Xem</Link>
                    <button onClick={() => handleDelete(job.id)}
                      className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50">
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
