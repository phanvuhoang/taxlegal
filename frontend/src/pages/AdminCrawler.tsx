import React, { useState, useEffect } from 'react';
import { Globe, RefreshCw, Plus, Database, Link, Layers, CheckCircle, XCircle, Clock, Play } from 'lucide-react';
import { legalaiApi } from '../lib/legalai';
import toast from 'react-hot-toast';

interface CrawlerStats {
  total_laws?: number;
  total_chunks?: number;
  chunks_with_embeddings?: number;
  domain_distribution?: Record<string, number>;
}

interface CrawlJob {
  id: string;
  url: string;
  status: string;
  created_at: string;
  completed_at?: string;
  error?: string;
  laws_found?: number;
}

interface CrawlerSource {
  url: string;
  domain?: string;
  description?: string;
  priority?: number;
}

const STATUS_CONFIG: Record<string, { label: string; cls: string; icon: React.ReactNode }> = {
  pending: { label: 'Chờ', cls: 'bg-yellow-100 text-yellow-700', icon: <Clock className="w-3 h-3" /> },
  running: { label: 'Đang chạy', cls: 'bg-blue-100 text-blue-700', icon: <RefreshCw className="w-3 h-3 animate-spin" /> },
  completed: { label: 'Xong', cls: 'bg-green-100 text-green-700', icon: <CheckCircle className="w-3 h-3" /> },
  failed: { label: 'Lỗi', cls: 'bg-red-100 text-red-700', icon: <XCircle className="w-3 h-3" /> },
};

export default function AdminCrawler() {
  const [stats, setStats] = useState<CrawlerStats | null>(null);
  const [sources, setSources] = useState<CrawlerSource[]>([]);
  const [jobs, setJobs] = useState<CrawlJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [customUrl, setCustomUrl] = useState('');
  const [crawlingUrl, setCrawlingUrl] = useState(false);
  const [crawlingPriority, setCrawlingPriority] = useState(false);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [statsRes, sourcesRes, jobsRes] = await Promise.allSettled([
        legalaiApi.getCrawlerStats(),
        legalaiApi.getCrawlerSources(),
        legalaiApi.listCrawlJobs(),
      ]);
      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
      if (sourcesRes.status === 'fulfilled') setSources(sourcesRes.value.data.sources || []);
      if (jobsRes.status === 'fulfilled') setJobs(jobsRes.value.data.jobs || []);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  };

  const handleCrawlUrl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customUrl.trim()) return;
    setCrawlingUrl(true);
    try {
      await legalaiApi.crawlUrl(customUrl.trim());
      toast.success('Đã gửi yêu cầu crawl URL');
      setCustomUrl('');
      setTimeout(loadAll, 1000);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Crawl thất bại');
    } finally {
      setCrawlingUrl(false);
    }
  };

  const handleCrawlPriority = async () => {
    setCrawlingPriority(true);
    try {
      await legalaiApi.crawlPriority();
      toast.success('Đã khởi động crawl tất cả nguồn ưu tiên');
      setTimeout(loadAll, 1000);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Không thể crawl');
    } finally {
      setCrawlingPriority(false);
    }
  };

  const embeddingPct = stats && stats.total_chunks
    ? ((stats.chunks_with_embeddings || 0) / stats.total_chunks * 100).toFixed(1)
    : null;

  const domainEntries = Object.entries(stats?.domain_distribution || {})
    .sort(([, a], [, b]) => b - a);
  const maxDomainCount = domainEntries.length > 0 ? domainEntries[0][1] : 1;

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6 flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#028a39' }}>
              <Globe className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Crawler Văn bản Luật</h1>
          </div>
          <p className="text-gray-500 text-sm ml-12">Quản lý thu thập và index văn bản pháp luật thuế tự động</p>
        </div>
        <button
          onClick={loadAll}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Làm mới
        </button>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          {
            label: 'Tổng Văn bản Luật',
            value: stats?.total_laws?.toLocaleString() ?? '—',
            icon: <Database className="w-5 h-5" />,
            color: '#028a39',
            bg: '#e6f4ec',
          },
          {
            label: 'Tổng Chunks',
            value: stats?.total_chunks?.toLocaleString() ?? '—',
            icon: <Layers className="w-5 h-5" />,
            color: '#2563eb',
            bg: '#eff6ff',
          },
          {
            label: 'Chunks có Embedding',
            value: stats?.chunks_with_embeddings?.toLocaleString() ?? '—',
            sub: embeddingPct ? `${embeddingPct}%` : undefined,
            icon: <CheckCircle className="w-5 h-5" />,
            color: '#7c3aed',
            bg: '#f5f3ff',
          },
        ].map(card => (
          <div
            key={card.label}
            className="bg-white border border-gray-200 rounded-xl p-4 flex items-start gap-3"
          >
            <div className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
              style={{ backgroundColor: card.bg, color: card.color }}>
              {card.icon}
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-0.5">{card.label}</p>
              <p className="text-xl font-bold text-gray-900">{loading ? '...' : card.value}</p>
              {card.sub && <p className="text-xs" style={{ color: card.color }}>{card.sub} có vector</p>}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6 mb-6">
        {/* Domain distribution */}
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Phân bổ theo Domain</h2>
          {loading ? (
            <div className="text-center py-6 text-gray-400 text-xs">Đang tải...</div>
          ) : domainEntries.length === 0 ? (
            <div className="text-center py-6 text-gray-400 text-xs">Chưa có dữ liệu</div>
          ) : (
            <div className="space-y-2">
              {domainEntries.map(([domain, count]) => (
                <div key={domain}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-gray-700 uppercase">{domain}</span>
                    <span className="text-xs text-gray-500">{count.toLocaleString()}</span>
                  </div>
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{
                        width: `${(count / maxDomainCount) * 100}%`,
                        backgroundColor: '#028a39',
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Crawl custom URL */}
        <div className="bg-white border border-gray-200 rounded-xl p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Crawl URL tùy chỉnh</h2>
          <form onSubmit={handleCrawlUrl} className="flex flex-col gap-3">
            <div className="relative">
              <Link className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="url"
                value={customUrl}
                onChange={e => setCustomUrl(e.target.value)}
                placeholder="https://thuvienphapluat.vn/..."
                className="w-full border border-gray-300 rounded-lg pl-9 pr-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:border-transparent"
                style={{ '--tw-ring-color': '#028a39' } as React.CSSProperties}
              />
            </div>
            <button
              type="submit"
              disabled={crawlingUrl || !customUrl.trim()}
              className="w-full py-2.5 text-white rounded-lg text-sm font-medium disabled:opacity-50 transition-opacity hover:opacity-90 flex items-center justify-center gap-2"
              style={{ backgroundColor: '#028a39' }}
            >
              {crawlingUrl ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Plus className="w-4 h-4" />
              )}
              {crawlingUrl ? 'Đang crawl...' : 'Crawl URL này'}
            </button>
          </form>

          <div className="mt-4 pt-4 border-t border-gray-100">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Nguồn ưu tiên
            </h3>
            <button
              onClick={handleCrawlPriority}
              disabled={crawlingPriority}
              className="w-full py-2.5 border rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              style={{ borderColor: '#028a39', color: '#028a39' }}
            >
              {crawlingPriority ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {crawlingPriority ? 'Đang chạy...' : 'Crawl tất cả nguồn ưu tiên'}
            </button>
          </div>
        </div>
      </div>

      {/* Priority sources list */}
      {sources.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden mb-6">
          <div className="px-4 py-3 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-700">Nguồn crawl ưu tiên ({sources.length})</h2>
          </div>
          <div className="divide-y divide-gray-100 max-h-64 overflow-y-auto">
            {sources.map((src, i) => (
              <div key={i} className="flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50">
                <Globe className="w-4 h-4 text-gray-400 shrink-0" />
                <div className="flex-1 min-w-0">
                  <a
                    href={src.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-medium text-blue-600 hover:underline truncate block"
                  >
                    {src.url}
                  </a>
                  {src.description && (
                    <span className="text-xs text-gray-400">{src.description}</span>
                  )}
                </div>
                {src.domain && (
                  <span
                    className="text-xs px-2 py-0.5 rounded-full font-medium shrink-0"
                    style={{ backgroundColor: '#e6f4ec', color: '#028a39' }}
                  >
                    {src.domain.toUpperCase()}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active/recent jobs */}
      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-700">Jobs gần đây</h2>
          <button
            onClick={loadAll}
            className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
          >
            Làm mới
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-10">
            <div
              className="w-6 h-6 border-2 border-t-transparent rounded-full animate-spin"
              style={{ borderColor: '#028a39', borderTopColor: 'transparent' }}
            />
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-10 text-gray-400">
            <Clock className="w-8 h-8 mx-auto mb-2 opacity-30" />
            <p className="text-sm">Chưa có jobs nào</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 bg-gray-50">
                  <th className="text-left px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">URL</th>
                  <th className="text-left px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">Trạng thái</th>
                  <th className="text-left px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">Văn bản</th>
                  <th className="text-left px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">Thời gian</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {jobs.map((job, i) => {
                  const cfg = STATUS_CONFIG[job.status] || STATUS_CONFIG['pending'];
                  return (
                    <tr key={job.id || i} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-2.5">
                        <a
                          href={job.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline text-xs truncate block max-w-xs"
                          title={job.url}
                        >
                          {job.url}
                        </a>
                        {job.error && (
                          <span className="text-xs text-red-500 block mt-0.5 truncate max-w-xs" title={job.error}>
                            {job.error}
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-2.5">
                        <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium ${cfg.cls}`}>
                          {cfg.icon}
                          {cfg.label}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-xs text-gray-600">
                        {job.laws_found !== undefined ? job.laws_found : '—'}
                      </td>
                      <td className="px-4 py-2.5 text-xs text-gray-400">
                        {new Date(job.created_at).toLocaleString('vi-VN', {
                          day: '2-digit', month: '2-digit', year: 'numeric',
                          hour: '2-digit', minute: '2-digit',
                        })}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
