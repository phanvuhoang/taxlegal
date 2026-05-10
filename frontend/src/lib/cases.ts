import api from "./api";

export interface Case {
  id: string;
  title: string;
  client_request: string;
  practice_area: string;
  status: string;
  current_node: string | null;
  output_language: string;
  priority: string;
  workflow_definition_id: string | null;
  final_output: string | null;
  quality_score: number | null;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface CaseEvent {
  id: string;
  event_type: string;
  node_name: string | null;
  actor: string | null;
  data: Record<string, unknown>;
  created_at: string;
}

export const casesApi = {
  list: (params?: { status?: string; skip?: number; limit?: number }) =>
    api.get("/api/cases", { params }),
  get: (id: string) => api.get(`/api/cases/${id}`),
  create: (data: Partial<Case> & { client_request: string; title: string }) =>
    api.post("/api/cases", data),
  start: (id: string, opts?: { model_override?: string; use_legacy_pipeline?: boolean }) =>
    api.post(`/api/cases/${id}/start`, opts || {}),
  getState: (id: string) => api.get(`/api/cases/${id}/state`),
  getEvents: (id: string) => api.get(`/api/cases/${id}/events`),
  getVersions: (id: string) => api.get(`/api/cases/${id}/versions`),
  humanApproval: (id: string, decision: string, notes?: string) =>
    api.post(`/api/cases/${id}/human-approval`, { decision, notes }),
  getFinal: (id: string) => api.get(`/api/cases/${id}/final`),
};

export interface WorkflowNode {
  id: string;
  workflow_id: string;
  node_id: string;
  node_type: string;
  label: string;
  bot_definition_id: number | null;
  skill_ids: number[];
  config: Record<string, unknown>;
  position_x: number | null;
  position_y: number | null;
  created_at: string;
}

export interface WorkflowEdge {
  id: string;
  workflow_id: string;
  from_node: string;
  to_node: string;
  condition: string | null;
  label: string | null;
  created_at: string;
}

export interface WorkflowDefinition {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  version: number;
  is_active: boolean;
  is_default: boolean;
  practice_area: string;
  entry_node: string | null;
  graph_definition: Record<string, unknown>;
  created_at: string;
  // returned by GET /api/workflows/{id}
  nodes?: WorkflowNode[];
  edges?: WorkflowEdge[];
}

export const workflowsApi = {
  list: () => api.get("/api/workflows"),
  get: (id: string) => api.get(`/api/workflows/${id}`),
  create: (data: Partial<WorkflowDefinition>) => api.post("/api/workflows", data),
  update: (id: string, data: Partial<WorkflowDefinition>) => api.patch(`/api/workflows/${id}`, data),
  validate: (id: string) => api.post(`/api/workflows/${id}/validate`),
  addNode: (id: string, node: Record<string, unknown>) => api.post(`/api/workflows/${id}/nodes`, node),
  addEdge: (id: string, edge: Record<string, unknown>) => api.post(`/api/workflows/${id}/edges`, edge),
};
