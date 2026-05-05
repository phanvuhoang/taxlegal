import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { adminApi, mattersApi } from "../lib/api";
import { getUser, isAdmin } from "../lib/auth";
import {
  FileText, CheckCircle, AlertCircle, TrendingUp,
  Plus, ArrowRight, Clock
} from "lucide-react";

export default function Dashboard() {
  const user = getUser();
  const [stats, setStats] = useState<any>(null);
  const [recentMatters, setRecentMatters] = useState<any[]>([]);

  useEffect(() => {
    if (isAdmin()) {
      adminApi.stats().then((r) => setStats(r.data)).catch(() => {});
    }
    mattersApi.list({ limit: 5 }).then((r) => setRecentMatters(r.data)).catch(() => {});
  }, []);

  const statusBadge = (s: string) => {
    const map: Record<string, string> = {
      draft: "badge-gray", intake: "badge-purple",
      partner_p1: "badge-blue", sa_blueprint: "badge-yellow",
      ja_research: "badge-green", sa_review: "badge-yellow",
      partner_p2: "badge-blue", partner_p3: "badge-blue",
      completed: "badge-green", failed: "badge-red",
    };
    const labels: Record<string, string> = {
      draft: "Draft", intake: "Intake", partner_p1: "Partner P1",
      sa_blueprint: "SA Blueprint", ja_research: "JA Research",
      sa_review: "SA Review", partner_p2: "Partner P2",
      partner_p3: "Partner P3", completed: "Hoàn thành", failed: "Lỗi",
    };
    return (
      <span className={`badge ${map[s] || "badge-gray"}`}>
        {labels[s] || s}
      </span>
    );
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Xin chào, {user?.full_name || user?.email} 👋
        </h1>
        <p className="text-gray-500 mt-1">Hệ thống tư vấn Thuế & Pháp luật AI — EZLAW-AI V15.1</p>
      </div>

      {/* Stats (admin only) */}
      {isAdmin() && stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[
            { label: "Tổng Matters", value: stats.matters, icon: FileText, color: "text-blue-600 bg-blue-50" },
            { label: "Hoàn thành", value: stats.completed, icon: CheckCircle, color: "text-green-600 bg-green-50" },
            { label: "Bài mẫu", value: stats.sample_advices, icon: FileText, color: "text-purple-600 bg-purple-50" },
            { label: "Điểm TB", value: stats.avg_quality_score ? `${stats.avg_quality_score}/100` : "—", icon: TrendingUp, color: "text-orange-600 bg-orange-50" },
          ].map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="card p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-500">{label}</span>
                <span className={`w-8 h-8 rounded-lg flex items-center justify-center ${color}`}>
                  <Icon className="w-4 h-4" />
                </span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Pipeline legend */}
      <div className="card mb-6">
        <h2 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ background: "#028a39" }} />
          7-Bước Pipeline EZLAW-AI V15.1
        </h2>
        <div className="flex flex-wrap gap-2">
          {[
            { label: "1. Intake Enhancer", color: "badge-purple" },
            { label: "2. Partner P1", color: "badge-blue" },
            { label: "3. SA Blueprint", color: "badge-yellow" },
            { label: "4. JA Research", color: "badge-green" },
            { label: "5. SA Review", color: "badge-yellow" },
            { label: "6. Partner P2", color: "badge-blue" },
            { label: "7. Partner P3", color: "badge-blue" },
          ].map(({ label, color }) => (
            <span key={label} className={`badge ${color}`}>{label}</span>
          ))}
        </div>
        <p className="text-xs text-gray-400 mt-3">
          5-Tier Verification Chain • 17 Quality Mechanisms • 18 Reason Codes
        </p>
      </div>

      {/* Quick actions */}
      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <Link to="/matters/new" className="card hover:shadow-md transition-shadow group cursor-pointer">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: "#028a39" }}>
              <Plus className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="font-semibold text-gray-900">Tạo Matter mới</p>
              <p className="text-sm text-gray-500">Gửi yêu cầu tư vấn thuế/pháp luật</p>
            </div>
            <ArrowRight className="w-5 h-5 text-gray-300 group-hover:text-primary-500 ml-auto transition-colors" />
          </div>
        </Link>

        <Link to="/sample-advices" className="card hover:shadow-md transition-shadow group cursor-pointer">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center">
              <FileText className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="font-semibold text-gray-900">Bài Mẫu Tham Khảo</p>
              <p className="text-sm text-gray-500">Xem các bài tư vấn mẫu chất lượng cao</p>
            </div>
            <ArrowRight className="w-5 h-5 text-gray-300 group-hover:text-primary-500 ml-auto transition-colors" />
          </div>
        </Link>
      </div>

      {/* Recent matters */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-900">Matters gần đây</h2>
          <Link to="/matters" className="text-sm text-primary-600 hover:text-primary-700">
            Xem tất cả →
          </Link>
        </div>
        {recentMatters.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">Chưa có matter nào. Tạo matter đầu tiên!</p>
            <Link to="/matters/new" className="btn-primary text-sm mt-3 inline-block">
              + Tạo Matter
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {recentMatters.map((m) => (
              <Link
                key={m.id}
                to={`/matters/${m.id}`}
                className="flex items-center gap-3 py-3 hover:bg-gray-50 -mx-2 px-2 rounded-lg transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{m.title}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <Clock className="w-3 h-3 text-gray-300" />
                    <span className="text-xs text-gray-400">
                      {new Date(m.created_at).toLocaleDateString("vi-VN")}
                    </span>
                    <span className="text-xs text-gray-400 capitalize">{m.practice_area}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {statusBadge(m.status)}
                  {m.quality_score && (
                    <span className="text-xs font-medium text-green-600">{m.quality_score}/100</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
