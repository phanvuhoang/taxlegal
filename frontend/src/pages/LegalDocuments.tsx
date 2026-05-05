import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Upload, Trash2, FileText, File, AlertCircle } from 'lucide-react';
import { legalaiApi } from '../lib/legalai';
import toast from 'react-hot-toast';

interface Document {
  id: string;
  filename: string;
  file_size?: number;
  file_type?: string;
  created_at: string;
  status?: string;
}

function formatBytes(bytes: number): string {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fileIcon(filename: string) {
  const ext = filename.split('.').pop()?.toLowerCase();
  if (ext === 'pdf') return <FileText className="w-5 h-5 text-red-500" />;
  if (ext === 'docx' || ext === 'doc') return <FileText className="w-5 h-5 text-blue-500" />;
  return <File className="w-5 h-5 text-gray-400" />;
}

function fileTypeBadge(filename: string) {
  const ext = filename.split('.').pop()?.toUpperCase() || 'FILE';
  const colors: Record<string, string> = {
    PDF: 'bg-red-100 text-red-700',
    DOCX: 'bg-blue-100 text-blue-700',
    DOC: 'bg-blue-100 text-blue-700',
    TXT: 'bg-gray-100 text-gray-600',
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded font-medium ${colors[ext] || 'bg-gray-100 text-gray-600'}`}>
      {ext}
    </span>
  );
}

export default function LegalDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const res = await legalaiApi.listDocuments();
      setDocuments(res.data.documents || []);
    } catch {
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];

    const allowed = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'application/msword'];
    if (!allowed.includes(file.type) && !file.name.match(/\.(pdf|docx?|txt)$/i)) {
      toast.error('Chỉ hỗ trợ PDF, DOCX, DOC, TXT');
      return;
    }

    setUploading(true);
    try {
      await legalaiApi.uploadDocument(file);
      toast.success(`Đã tải lên: ${file.name}`);
      await loadDocuments();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Tải lên thất bại');
    } finally {
      setUploading(false);
    }
  }, []);

  const handleDelete = async (doc: Document) => {
    if (!window.confirm(`Xóa tài liệu "${doc.filename}"?`)) return;
    setDeletingId(doc.id);
    try {
      await legalaiApi.deleteDocument(doc.id);
      toast.success('Đã xóa tài liệu');
      setDocuments(prev => prev.filter(d => d.id !== doc.id));
    } catch {
      toast.error('Không thể xóa tài liệu');
    } finally {
      setDeletingId(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleUpload(e.dataTransfer.files);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#028a39' }}>
            <FileText className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Tài liệu pháp lý</h1>
        </div>
        <p className="text-gray-500 text-sm ml-12">
          Tải lên và quản lý tài liệu pháp lý để tích hợp vào hệ thống AI
        </p>
      </div>

      {/* Upload zone */}
      <div
        onClick={() => !uploading && fileInputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        className={`border-2 border-dashed rounded-xl p-10 text-center mb-6 cursor-pointer transition-colors ${
          dragOver
            ? 'border-green-400 bg-green-50'
            : uploading
            ? 'border-gray-200 bg-gray-50 cursor-not-allowed'
            : 'border-gray-200 hover:border-green-300 hover:bg-green-50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.docx,.doc,.txt"
          onChange={e => handleUpload(e.target.files)}
          disabled={uploading}
        />
        {uploading ? (
          <>
            <div
              className="w-10 h-10 border-2 border-t-transparent rounded-full animate-spin mx-auto mb-3"
              style={{ borderColor: '#028a39', borderTopColor: 'transparent' }}
            />
            <p className="text-sm font-medium" style={{ color: '#028a39' }}>Đang tải lên...</p>
          </>
        ) : (
          <>
            <Upload
              className={`w-10 h-10 mx-auto mb-3 transition-colors ${dragOver ? 'text-green-500' : 'text-gray-300'}`}
            />
            <p className="text-sm font-medium text-gray-600 mb-1">
              Kéo & thả tài liệu vào đây hoặc <span style={{ color: '#028a39' }}>chọn file</span>
            </p>
            <p className="text-xs text-gray-400">Hỗ trợ: PDF, DOCX, DOC, TXT · Tối đa 50MB</p>
          </>
        )}
      </div>

      {/* Documents list */}
      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-700">
            Tài liệu đã tải lên
            {!loading && (
              <span className="ml-2 text-xs font-normal text-gray-400">({documents.length})</span>
            )}
          </h2>
          <button
            onClick={loadDocuments}
            className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
          >
            Làm mới
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div
              className="w-8 h-8 border-2 border-t-transparent rounded-full animate-spin"
              style={{ borderColor: '#028a39', borderTopColor: 'transparent' }}
            />
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <AlertCircle className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p className="text-sm font-medium text-gray-500">Chưa có tài liệu nào</p>
            <p className="text-xs mt-1">Tải lên PDF hoặc DOCX để bắt đầu</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {documents.map(doc => (
              <div
                key={doc.id}
                className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors"
              >
                {/* Icon */}
                <div className="shrink-0">{fileIcon(doc.filename)}</div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-sm font-medium text-gray-800 truncate">
                      {doc.filename}
                    </span>
                    {fileTypeBadge(doc.filename)}
                    {doc.status && doc.status !== 'ready' && (
                      <span className="text-xs px-2 py-0.5 rounded bg-yellow-100 text-yellow-700 font-medium">
                        {doc.status}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-400">
                    {doc.file_size !== undefined && (
                      <span>{formatBytes(doc.file_size)}</span>
                    )}
                    <span>{new Date(doc.created_at).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })}</span>
                  </div>
                </div>

                {/* Delete */}
                <button
                  onClick={() => handleDelete(doc)}
                  disabled={deletingId === doc.id}
                  className="shrink-0 p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors disabled:opacity-40"
                  title="Xóa tài liệu"
                >
                  {deletingId === doc.id ? (
                    <div className="w-4 h-4 border-2 border-red-400 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
