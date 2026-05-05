import React, { useState, useCallback } from 'react';
import { Search, Scale, ExternalLink } from 'lucide-react';
import { legalaiApi } from '../lib/legalai';

const DOMAIN_FILTERS = [
  { label: 'Tất cả', value: '' },
  { label: 'TNDN (CIT)', value: 'cit' },
  { label: 'GTGT (VAT)', value: 'vat' },
  { label: 'TNCN (PIT)', value: 'pit' },
  { label: 'Nhà thầu', value: 'fct' },
  { label: 'TTĐB (SST)', value: 'sst' },
  { label: 'Thuế', value: 'thue' },
];

export default function LegalSearch() {
  const [query, setQuery] = useState('');
  const [domain, setDomain] = useState('');
  const [searchType, setSearchType] = useState<'chunks' | 'laws'>('chunks');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = useCallback(async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = searchType === 'chunks'
        ? await legalaiApi.searchChunks(query, domain || undefined)
        : await legalaiApi.searchLaws(query, domain || undefined);
      setResults(res.data.results || []);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [query, domain, searchType]);

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#028a39' }}>
            <Scale className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Tra cứu pháp luật thuế</h1>
        </div>
        <p className="text-gray-500 text-sm ml-12">
          Tìm kiếm văn bản pháp luật thuế Việt Nam — Luật, Nghị định, Thông tư
        </p>
      </div>

      {/* Search type toggle */}
      <div className="flex gap-2 mb-4">
        {[
          { key: 'chunks', label: 'Tra cứu điều khoản' },
          { key: 'laws', label: 'Tra cứu văn bản' },
        ].map(t => (
          <button
            key={t.key}
            onClick={() => setSearchType(t.key as 'chunks' | 'laws')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              searchType === t.key
                ? 'text-white shadow-sm'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            style={searchType === t.key ? { backgroundColor: '#028a39' } : {}}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Search form */}
      <form onSubmit={handleSearch} className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="VD: thuế GTGT hàng hóa xuất khẩu, khấu trừ thuế TNDN..."
            className="w-full border border-gray-300 rounded-lg pl-10 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:border-transparent"
            style={{ '--tw-ring-color': '#028a39' } as React.CSSProperties}
          />
        </div>
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-6 py-3 text-white rounded-lg font-medium text-sm disabled:opacity-50 transition-opacity hover:opacity-90 flex items-center gap-2"
          style={{ backgroundColor: '#028a39' }}
        >
          {loading ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Search className="w-4 h-4" />
          )}
          Tìm kiếm
        </button>
      </form>

      {/* Domain filters */}
      <div className="flex flex-wrap gap-2 mb-6">
        {DOMAIN_FILTERS.map(f => (
          <button
            key={f.value}
            onClick={() => setDomain(f.value)}
            className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
              domain === f.value
                ? 'text-white border-transparent'
                : 'bg-white text-gray-600 border-gray-200 hover:border-gray-400'
            }`}
            style={domain === f.value ? { backgroundColor: '#028a39', borderColor: '#028a39' } : {}}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <div className="text-center">
            <div className="w-10 h-10 rounded-full border-2 border-t-transparent animate-spin mx-auto mb-3"
              style={{ borderColor: '#028a39', borderTopColor: 'transparent' }} />
            <p className="text-sm text-gray-500">Đang tìm kiếm...</p>
          </div>
        </div>
      )}

      {/* No results */}
      {!loading && searched && results.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <Search className="w-12 h-12 mx-auto mb-3 opacity-40" />
          <p className="font-medium text-gray-500 mb-1">Không tìm thấy kết quả</p>
          <p className="text-sm">Thử từ khóa khác hoặc bỏ bộ lọc domain.</p>
          <p className="text-xs mt-2">Gợi ý: crawl thêm văn bản thuế trong Admin → Crawler</p>
        </div>
      )}

      {/* Results */}
      {!loading && results.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs text-gray-500 font-medium">{results.length} kết quả</p>
          {results.map((r, i) => (
            <div
              key={r.chunk_id || r.id || i}
              className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="min-w-0">
                  <span className="font-semibold text-gray-900 text-sm leading-snug">
                    {r.law_title || r.title}
                  </span>
                  {r.law_number && (
                    <span className="ml-2 text-xs text-gray-400 font-mono">{r.law_number}</span>
                  )}
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  {r.score !== undefined && (
                    <span
                      className="text-xs px-2 py-0.5 rounded-full font-semibold"
                      style={{ backgroundColor: '#e6f4ec', color: '#028a39' }}
                    >
                      {(r.score * 100).toFixed(0)}%
                    </span>
                  )}
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    (r.law_status === 'active' || r.status === 'active')
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-600'
                  }`}>
                    {(r.law_status === 'active' || r.status === 'active') ? 'Hiệu lực' : 'Hết hiệu lực'}
                  </span>
                </div>
              </div>

              {(r.article || r.clause) && (
                <p className="text-xs font-semibold mb-1.5" style={{ color: '#028a39' }}>
                  {[r.article, r.clause].filter(Boolean).join(' — ')}
                </p>
              )}

              <p className="text-sm text-gray-700 leading-relaxed line-clamp-4">
                {r.content || r.summary || 'Không có nội dung'}
              </p>

              {r.source_url && (
                <a
                  href={r.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2.5 text-xs flex items-center gap-1 hover:underline w-fit"
                  style={{ color: '#028a39' }}
                >
                  <ExternalLink className="w-3 h-3" />
                  Xem văn bản gốc
                </a>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Empty / initial state */}
      {!searched && !loading && (
        <div className="text-center py-16 text-gray-400">
          <Scale className="w-14 h-14 mx-auto mb-4 opacity-30" />
          <p className="text-sm font-medium text-gray-500 mb-1">
            Nhập từ khóa để tra cứu văn bản pháp luật thuế
          </p>
          <p className="text-xs">VD: "thuế GTGT dịch vụ kỹ thuật số", "khấu trừ thuế TNDN R&D"</p>
          <div className="mt-6 flex flex-wrap justify-center gap-2">
            {[
              'thuế GTGT hàng xuất khẩu',
              'khấu trừ chi phí TNDN',
              'thuế nhà thầu nước ngoài',
              'ưu đãi thuế đầu tư',
            ].map(q => (
              <button
                key={q}
                onClick={() => setQuery(q)}
                className="text-xs px-3 py-1.5 bg-white border border-gray-200 rounded-full hover:border-green-300 transition-colors"
                style={{ color: '#028a39' }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
