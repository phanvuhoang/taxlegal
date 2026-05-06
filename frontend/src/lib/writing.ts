/**
 * Writing module API client — uses same axios instance as api.ts
 */
import api from "./api";

export interface WritingJob {
  id: number;
  title: string;
  content_type: string;
  topic: string;
  context: string | null;
  output_language: string;
  bot_variant_id: number | null;
  skill_ids: number[];
  status: string; // draft | generating | done | error
  word_count_target: number;
  final_content: string | null;
  docx_path: string | null;
  gamma_url: string | null;
  created_at: string | null;
}

export interface PriorityDoc {
  id: number;
  title: string;
  doc_type: string;
  source_url: string | null;
  content: string;
  priority_level: number;
  is_active: boolean;
  created_at: string | null;
}

export interface SampleWriting {
  id: number;
  title: string;
  content_type: string;
  language: string;
  content: string;
  tags: string[];
  is_active: boolean;
  created_at: string | null;
}

// Writing Jobs
export const writingApi = {
  list: () => api.get("/api/writing"),
  get: (id: number) => api.get(`/api/writing/${id}`),
  create: (data: {
    title: string;
    content_type: string;
    topic: string;
    context?: string;
    output_language: string;
    bot_variant_id?: number | null;
    skill_ids?: number[];
    word_count_target?: number;
  }) => api.post("/api/writing", data),
  generate: (id: number) => api.post(`/api/writing/${id}/generate`),
  createSlides: (id: number) => api.post(`/api/writing/${id}/create-slides`),
  delete: (id: number) => api.delete(`/api/writing/${id}`),

  exportDocx: async (id: number, title: string) => {
    const token = localStorage.getItem("token");
    const res = await fetch(`/api/writing/${id}/export-docx`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token || ""}` },
    });
    if (!res.ok) throw new Error("Export DOCX failed");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title.substring(0, 60)}.docx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },
};

// Priority Docs (admin)
export const priorityDocsApi = {
  list: () => api.get("/api/admin/priority-docs"),
  create: (data: {
    title: string;
    doc_type: string;
    source_url?: string;
    content: string;
    priority_level: number;
    is_active: boolean;
  }) => api.post("/api/admin/priority-docs", data),
  update: (id: number, data: Partial<PriorityDoc>) =>
    api.put(`/api/admin/priority-docs/${id}`, data),
  delete: (id: number) => api.delete(`/api/admin/priority-docs/${id}`),
};

// Sample Writings (admin)
export const sampleWritingsApi = {
  list: () => api.get("/api/admin/sample-writings"),
  create: (data: {
    title: string;
    content_type: string;
    language: string;
    content: string;
    tags?: string[];
    is_active: boolean;
  }) => api.post("/api/admin/sample-writings", data),
  delete: (id: number) => api.delete(`/api/admin/sample-writings/${id}`),
};

export const CONTENT_TYPES = [
  { value: "analysis", label: "Phân tích thuế" },
  { value: "advisory", label: "Tư vấn thuế" },
  { value: "press", label: "Bài báo / Thông cáo" },
  { value: "scenario", label: "Phân tích tình huống" },
];

export const DOC_TYPES = [
  { value: "law", label: "Luật" },
  { value: "decree", label: "Nghị định" },
  { value: "circular", label: "Thông tư" },
  { value: "official_letter", label: "Công văn" },
  { value: "treaty", label: "Hiệp định (DTA)" },
  { value: "other", label: "Khác" },
];
