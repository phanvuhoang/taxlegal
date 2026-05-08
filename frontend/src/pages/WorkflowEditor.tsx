import { useEffect, useState } from "react";
import {
  Plus, CheckCircle, AlertCircle, XCircle, ChevronDown, ChevronRight,
  GitBranch, Trash2, Save, RefreshCw,
} from "lucide-react";
import { workflowsApi, WorkflowDefinition } from "../lib/cases";
import toast from "react-hot-toast";

const PRIMARY = "#028a39";

interface ValidationResult {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
}

interface NodeForm { node_name: string; node_type: string; description: string; [key: string]: unknown; }
interface EdgeForm { from_node: string; to_node: string; condition: string; [key: string]: unknown; }

export default function WorkflowEditor() {
  const [workflows, setWorkflows] = useState<WorkflowDefinition[]>([]);
  const [selected, setSelected] = useState<WorkflowDefinition | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);

  // JSON editor state
  const [jsonText, setJsonText] = useState("");
  const [jsonError, setJsonError] = useState<string | null>(null);

  // Create new workflow form
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newWf, setNewWf] = useState({ name: "", slug: "", practice_area: "tax", description: "" });
  const [creating, setCreating] = useState(false);

  // Node form
  const [showNodeForm, setShowNodeForm] = useState(false);
  const [nodeForm, setNodeForm] = useState<NodeForm>({ node_name: "", node_type: "llm", description: "" });

  // Edge form
  const [showEdgeForm, setShowEdgeForm] = useState(false);
  const [edgeForm, setEdgeForm] = useState<EdgeForm>({ from_node: "", to_node: "", condition: "" });

  const loadWorkflows = async () => {
    setLoading(true);
    try {
      const res = await workflowsApi.list();
      const data = res.data;
      setWorkflows(Array.isArray(data) ? data : (data.items ?? []));
    } catch {
      toast.error("Không thể tải workflows");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadWorkflows(); }, []);

  const selectWorkflow = (wf: WorkflowDefinition) => {
    setSelected(wf);
    setValidationResult(null);
    try {
      setJsonText(JSON.stringify(wf.graph_definition ?? {}, null, 2));
      setJsonError(null);
    } catch {
      setJsonText("{}");
    }
  };

  const handleJsonChange = (val: string) => {
    setJsonText(val);
    try {
      JSON.parse(val);
      setJsonError(null);
    } catch (e: any) {
      setJsonError(e.message);
    }
  };

  const handleSaveGraph = async () => {
    if (!selected) return;
    if (jsonError) { toast.error("JSON không hợp lệ"); return; }
    setSaving(true);
    try {
      const parsed = JSON.parse(jsonText);
      await workflowsApi.update(selected.id, { graph_definition: parsed });
      toast.success("Đã lưu graph definition!");
      loadWorkflows();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Lỗi khi lưu");
    } finally {
      setSaving(false);
    }
  };

  const handleValidate = async () => {
    if (!selected) return;
    setValidating(true);
    setValidationResult(null);
    try {
      const res = await workflowsApi.validate(selected.id);
      setValidationResult(res.data);
    } catch (err: any) {
      toast.error("Lỗi khi validate");
    } finally {
      setValidating(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWf.name.trim() || !newWf.slug.trim()) { toast.error("Vui lòng nhập tên và slug"); return; }
    setCreating(true);
    try {
      await workflowsApi.create({ ...newWf, graph_definition: {} });
      toast.success("Workflow đã được tạo!");
      setShowCreateForm(false);
      setNewWf({ name: "", slug: "", practice_area: "tax", description: "" });
      loadWorkflows();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Lỗi khi tạo workflow");
    } finally {
      setCreating(false);
    }
  };

  const handleAddNode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selected || !nodeForm.node_name.trim()) { toast.error("Vui lòng nhập tên node"); return; }
    try {
      await workflowsApi.addNode(selected.id, nodeForm);
      toast.success("Node đã được thêm!");
      setShowNodeForm(false);
      setNodeForm({ node_name: "", node_type: "llm", description: "" });
      const res = await workflowsApi.get(selected.id);
      selectWorkflow(res.data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Lỗi khi thêm node");
    }
  };

  const handleAddEdge = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selected || !edgeForm.from_node.trim() || !edgeForm.to_node.trim()) {
      toast.error("Vui lòng nhập from_node và to_node");
      return;
    }
    try {
      await workflowsApi.addEdge(selected.id, edgeForm);
      toast.success("Edge đã được thêm!");
      setShowEdgeForm(false);
      setEdgeForm({ from_node: "", to_node: "", condition: "" });
      const res = await workflowsApi.get(selected.id);
      selectWorkflow(res.data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Lỗi khi thêm edge");
    }
  };

  const graphDef = (() => {
    try { return JSON.parse(jsonText); } catch { return selected?.graph_definition ?? {}; }
  })();
  const nodes: any[] = graphDef.nodes ?? [];
  const edges: any[] = graphDef.edges ?? [];

  const inputCls = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 bg-white";

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Workflow Editor</h1>
          <p className="text-sm text-gray-500 mt-0.5">Quản lý định nghĩa quy trình tư vấn</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={loadWorkflows} className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors">
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="flex items-center gap-2 px-4 py-2 text-white text-sm font-medium rounded-lg"
            style={{ background: PRIMARY }}
          >
            <Plus className="w-4 h-4" />
            New Workflow
          </button>
        </div>
      </div>

      {/* Create form */}
      {showCreateForm && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
          <h3 className="font-semibold text-gray-800 mb-4">Tạo Workflow Mới</h3>
          <form onSubmit={handleCreate} className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Tên *</label>
              <input className={inputCls} placeholder="VD: Tax Advisory v2" value={newWf.name} onChange={e => setNewWf(p => ({ ...p, name: e.target.value }))} required />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Slug *</label>
              <input className={inputCls} placeholder="tax-advisory-v2" value={newWf.slug} onChange={e => setNewWf(p => ({ ...p, slug: e.target.value }))} required />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Lĩnh vực</label>
              <select className={inputCls} value={newWf.practice_area} onChange={e => setNewWf(p => ({ ...p, practice_area: e.target.value }))}>
                <option value="tax">Thuế</option>
                <option value="legal">Pháp lý</option>
                <option value="both">Cả hai</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Mô tả</label>
              <input className={inputCls} placeholder="Mô tả ngắn..." value={newWf.description} onChange={e => setNewWf(p => ({ ...p, description: e.target.value }))} />
            </div>
            <div className="col-span-2 flex items-center gap-2 justify-end">
              <button type="button" onClick={() => setShowCreateForm(false)} className="px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50">Hủy</button>
              <button type="submit" disabled={creating} className="px-4 py-2 text-sm text-white font-medium rounded-lg disabled:opacity-60" style={{ background: PRIMARY }}>
                {creating ? "Đang tạo..." : "Tạo"}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-3 gap-5">
        {/* Workflow list */}
        <div className="col-span-1 space-y-2">
          <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider px-1">
            Workflows ({workflows.length})
          </h3>
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="w-5 h-5 border-2 border-gray-200 border-t-green-600 rounded-full animate-spin" />
            </div>
          ) : workflows.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-8">Chưa có workflow nào</p>
          ) : (
            workflows.map((wf) => (
              <div
                key={wf.id}
                onClick={() => selectWorkflow(wf)}
                className={`cursor-pointer rounded-lg border p-3 transition-colors ${
                  selected?.id === wf.id ? "border-transparent text-white" : "border-gray-100 bg-white hover:border-gray-200"
                }`}
                style={selected?.id === wf.id ? { background: PRIMARY } : {}}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className={`text-sm font-semibold truncate ${selected?.id === wf.id ? "text-white" : "text-gray-800"}`}>
                      {wf.name}
                    </p>
                    <p className={`text-xs mt-0.5 ${selected?.id === wf.id ? "text-green-100" : "text-gray-400"}`}>
                      v{wf.version} · {wf.practice_area}
                    </p>
                  </div>
                  <div className="flex items-center gap-1 shrink-0">
                    {wf.is_default && (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                        selected?.id === wf.id ? "bg-green-700 text-green-100" : "bg-green-50 text-green-700"
                      }`}>
                        Default
                      </span>
                    )}
                    {!wf.is_active && (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                        selected?.id === wf.id ? "bg-red-800 text-red-100" : "bg-red-50 text-red-600"
                      }`}>
                        Off
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Editor panel */}
        <div className="col-span-2 space-y-4">
          {!selected ? (
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm flex items-center justify-center h-64">
              <div className="text-center text-gray-400">
                <GitBranch className="w-8 h-8 mx-auto mb-2 opacity-40" />
                <p className="text-sm">Chọn một workflow để chỉnh sửa</p>
              </div>
            </div>
          ) : (
            <>
              {/* Toolbar */}
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-bold text-gray-800">{selected.name}</h2>
                  <p className="text-xs text-gray-400">{selected.slug} · {selected.entry_node ? `Entry: ${selected.entry_node}` : "No entry node"}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleValidate}
                    disabled={validating}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-60"
                  >
                    {validating ? <span className="w-3.5 h-3.5 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin" /> : <CheckCircle className="w-3.5 h-3.5" />}
                    Validate
                  </button>
                  <button
                    onClick={handleSaveGraph}
                    disabled={saving || !!jsonError}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-white rounded-lg disabled:opacity-60"
                    style={{ background: PRIMARY }}
                  >
                    {saving ? <span className="w-3.5 h-3.5 border-2 border-white/40 border-t-white rounded-full animate-spin" /> : <Save className="w-3.5 h-3.5" />}
                    Lưu
                  </button>
                </div>
              </div>

              {/* Validation result */}
              {validationResult && (
                <div className={`rounded-lg border p-4 ${validationResult.is_valid ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"}`}>
                  <div className="flex items-center gap-2 mb-2">
                    {validationResult.is_valid
                      ? <CheckCircle className="w-4 h-4 text-green-600" />
                      : <XCircle className="w-4 h-4 text-red-600" />
                    }
                    <span className={`text-sm font-semibold ${validationResult.is_valid ? "text-green-800" : "text-red-800"}`}>
                      {validationResult.is_valid ? "Workflow hợp lệ" : "Workflow không hợp lệ"}
                    </span>
                  </div>
                  {validationResult.errors.length > 0 && (
                    <ul className="text-xs text-red-700 space-y-1 ml-6 list-disc">
                      {validationResult.errors.map((e, i) => <li key={i}>{e}</li>)}
                    </ul>
                  )}
                  {validationResult.warnings.length > 0 && (
                    <ul className="text-xs text-amber-700 space-y-1 ml-6 list-disc mt-2">
                      {validationResult.warnings.map((w, i) => (
                        <li key={i} className="flex items-start gap-1">
                          <AlertCircle className="w-3 h-3 mt-0.5 shrink-0" />
                          {w}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              {/* Nodes */}
              <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
                  <h3 className="text-sm font-semibold text-gray-700">
                    Nodes <span className="text-gray-400 font-normal">({nodes.length})</span>
                  </h3>
                  <button
                    onClick={() => setShowNodeForm(!showNodeForm)}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white rounded-lg"
                    style={{ background: PRIMARY }}
                  >
                    <Plus className="w-3 h-3" />
                    Thêm Node
                  </button>
                </div>

                {showNodeForm && (
                  <form onSubmit={handleAddNode} className="px-4 py-3 bg-gray-50 border-b border-gray-100">
                    <div className="grid grid-cols-3 gap-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Tên node *</label>
                        <input className={inputCls} placeholder="intake" value={nodeForm.node_name} onChange={e => setNodeForm(p => ({ ...p, node_name: e.target.value }))} required />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Loại</label>
                        <select className={inputCls} value={nodeForm.node_type} onChange={e => setNodeForm(p => ({ ...p, node_type: e.target.value }))}>
                          <option value="llm">LLM</option>
                          <option value="retrieval">Retrieval</option>
                          <option value="human">Human</option>
                          <option value="router">Router</option>
                          <option value="tool">Tool</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Mô tả</label>
                        <input className={inputCls} placeholder="..." value={nodeForm.description} onChange={e => setNodeForm(p => ({ ...p, description: e.target.value }))} />
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mt-3 justify-end">
                      <button type="button" onClick={() => setShowNodeForm(false)} className="px-3 py-1.5 text-xs text-gray-600 border border-gray-200 rounded-lg hover:bg-white">Hủy</button>
                      <button type="submit" className="px-3 py-1.5 text-xs text-white rounded-lg" style={{ background: PRIMARY }}>Thêm</button>
                    </div>
                  </form>
                )}

                {nodes.length === 0 ? (
                  <p className="text-xs text-gray-400 text-center py-6">Chưa có node nào</p>
                ) : (
                  <div className="p-3 grid grid-cols-2 gap-2">
                    {nodes.map((n: any, i: number) => (
                      <div key={n.node_name ?? i} className="flex items-center gap-2 p-2.5 border border-gray-100 rounded-lg">
                        <div className="w-2 h-2 rounded-full shrink-0" style={{ background: PRIMARY }} />
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-gray-800 truncate">{n.node_name}</p>
                          {n.node_type && <p className="text-xs text-gray-400">{n.node_type}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Edges */}
              <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
                  <h3 className="text-sm font-semibold text-gray-700">
                    Edges <span className="text-gray-400 font-normal">({edges.length})</span>
                  </h3>
                  <button
                    onClick={() => setShowEdgeForm(!showEdgeForm)}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white rounded-lg"
                    style={{ background: PRIMARY }}
                  >
                    <Plus className="w-3 h-3" />
                    Thêm Edge
                  </button>
                </div>

                {showEdgeForm && (
                  <form onSubmit={handleAddEdge} className="px-4 py-3 bg-gray-50 border-b border-gray-100">
                    <div className="grid grid-cols-3 gap-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">From node *</label>
                        <input className={inputCls} placeholder="intake" value={edgeForm.from_node} onChange={e => setEdgeForm(p => ({ ...p, from_node: e.target.value }))} required />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">To node *</label>
                        <input className={inputCls} placeholder="research" value={edgeForm.to_node} onChange={e => setEdgeForm(p => ({ ...p, to_node: e.target.value }))} required />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Điều kiện</label>
                        <input className={inputCls} placeholder="default" value={edgeForm.condition} onChange={e => setEdgeForm(p => ({ ...p, condition: e.target.value }))} />
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mt-3 justify-end">
                      <button type="button" onClick={() => setShowEdgeForm(false)} className="px-3 py-1.5 text-xs text-gray-600 border border-gray-200 rounded-lg hover:bg-white">Hủy</button>
                      <button type="submit" className="px-3 py-1.5 text-xs text-white rounded-lg" style={{ background: PRIMARY }}>Thêm</button>
                    </div>
                  </form>
                )}

                {edges.length === 0 ? (
                  <p className="text-xs text-gray-400 text-center py-6">Chưa có edge nào</p>
                ) : (
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="bg-gray-50 border-b border-gray-100">
                        <th className="text-left px-4 py-2 font-semibold text-gray-500">From</th>
                        <th className="text-left px-4 py-2 font-semibold text-gray-500">To</th>
                        <th className="text-left px-4 py-2 font-semibold text-gray-500">Condition</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {edges.map((e: any, i: number) => (
                        <tr key={i} className="hover:bg-gray-50">
                          <td className="px-4 py-2 font-mono text-gray-700">{e.from_node}</td>
                          <td className="px-4 py-2 font-mono text-gray-700">{e.to_node}</td>
                          <td className="px-4 py-2 text-gray-400">{e.condition ?? "—"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>

              {/* JSON editor */}
              <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
                  <h3 className="text-sm font-semibold text-gray-700">Graph Definition (JSON)</h3>
                  {jsonError && (
                    <span className="text-xs text-red-600 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" />
                      {jsonError}
                    </span>
                  )}
                </div>
                <div className="p-4">
                  <textarea
                    className={`${inputCls} font-mono text-xs resize-none ${jsonError ? "border-red-300 focus:ring-red-300" : "focus:ring-green-300"}`}
                    rows={14}
                    value={jsonText}
                    onChange={(e) => handleJsonChange(e.target.value)}
                    spellCheck={false}
                  />
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
