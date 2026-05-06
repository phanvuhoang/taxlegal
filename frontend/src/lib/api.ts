import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "";

const api = axios.create({
  baseURL: BASE,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    return api.post("/api/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
  me: () => api.get("/api/auth/me"),
  changePassword: (old_password: string, new_password: string) =>
    api.post("/api/auth/change-password", { old_password, new_password }),
};

// ── Matters ───────────────────────────────────────────────────────────────────
export const mattersApi = {
  list: (params?: Record<string, any>) => api.get("/api/matters/", { params }),
  get: (id: number) => api.get(`/api/matters/${id}`),
  create: (data: any) => api.post("/api/matters/", data),
  approveStep: (id: number, step: number, body: any) =>
    api.post(`/api/matters/${id}/approve-step/${step}`, body),
  runStep: (id: number, step: number, body: any) =>
    api.post(`/api/matters/${id}/run-step/${step}`, body),
  getChunks: (id: number) => api.get(`/api/matters/${id}/chunks`),
  markSample: (id: number) => api.patch(`/api/matters/${id}/mark-sample`),
  delete: (id: number) => api.delete(`/api/matters/${id}`),
};

// ── Admin ─────────────────────────────────────────────────────────────────────
export const adminApi = {
  stats: () => api.get("/api/admin/stats"),
  listUsers: () => api.get("/api/admin/users"),
  createUser: (data: any) => api.post("/api/admin/users", data),
  updateUser: (id: number, data: any) => api.patch(`/api/admin/users/${id}`, data),
  deleteUser: (id: number) => api.delete(`/api/admin/users/${id}`),
  getAgentSettings: () => api.get("/api/admin/agent-settings"),
  updateAgentSetting: (key: string, data: any) =>
    api.put(`/api/admin/agent-settings/${key}`, data),
  listSampleAdvices: () => api.get("/api/admin/sample-advices"),
  getSampleAdvice: (id: number) => api.get(`/api/admin/sample-advices/${id}`),
  createSampleAdvice: (data: any) => api.post("/api/admin/sample-advices", data),
  deleteSampleAdvice: (id: number) => api.delete(`/api/admin/sample-advices/${id}`),
  listTestCases: () => api.get("/api/admin/autotest/cases"),
  createTestCase: (data: any) => api.post("/api/admin/autotest/cases", data),
  runAutotest: (id: number) => api.post(`/api/admin/autotest/run/${id}`),
  listTestRuns: () => api.get("/api/admin/autotest/runs"),
};

// ── Laws ──────────────────────────────────────────────────────────────────────
export const lawsApi = {
  search: (q: string, params?: Record<string, any>) =>
    api.get("/api/laws/", { params: { q, ...params } }),
  get: (id: number) => api.get(`/api/laws/${id}`),
  add: (data: any) => api.post("/api/laws/", data),
  searchDbvntax: (q: string) => api.get("/api/laws/dbvntax/search", { params: { q } }),
};

// ── Models ────────────────────────────────────────────────────────────────────
export const getModels = () => api.get("/api/models");

// ── Skills ────────────────────────────────────────────────────────────────────
export const skillsApi = {
  list: () => api.get('/api/admin/skills'),
  get: (id: number) => api.get(`/api/admin/skills/${id}`),
  create: (data: any) => api.post('/api/admin/skills', data),
  update: (id: number, data: any) => api.put(`/api/admin/skills/${id}`, data),
  delete: (id: number) => api.delete(`/api/admin/skills/${id}`),
};

// ── Bot Variants ──────────────────────────────────────────────────────────────
export const botVariantsApi = {
  list: () => api.get('/api/admin/bot-variants'),
  get: (id: number) => api.get(`/api/admin/bot-variants/${id}`),
  create: (data: any) => api.post('/api/admin/bot-variants', data),
  update: (id: number, data: any) => api.put(`/api/admin/bot-variants/${id}`, data),
  delete: (id: number) => api.delete(`/api/admin/bot-variants/${id}`),
};

// ── Pipeline Templates ────────────────────────────────────────────────────────
export const pipelineTemplatesApi = {
  list: () => api.get('/api/admin/pipeline-templates'),
  listPublic: () => api.get('/api/pipeline-templates'),
  get: (id: number) => api.get(`/api/admin/pipeline-templates/${id}`),
  create: (data: any) => api.post('/api/admin/pipeline-templates', data),
  update: (id: number, data: any) => api.put(`/api/admin/pipeline-templates/${id}`, data),
  delete: (id: number) => api.delete(`/api/admin/pipeline-templates/${id}`),
};
