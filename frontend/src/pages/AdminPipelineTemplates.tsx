import { useState, useEffect } from "react";
import { pipelineTemplatesApi, botVariantsApi } from "../lib/api";
import { Plus, X, Edit2, Trash2, Star, LayoutTemplate } from "lucide-react";
import toast from "react-hot-toast";

interface PipelineTemplate {
  id: number;
  name: string;
  slug: string;
  description: string;
  practice_area: string;
  step_config: Record<string, { bot_variant_slug: string; label: string }>;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
}

interface BotVariant {
  id: number;
  name: string;
  slug: string;
  role: string;
  is_active: boolean;
}

const PRACTICE_AREAS = ["tax", "legal", "both", "advisory", "compliance"];

const PRACTICE_COLORS: Record<string, string> = {
  tax: "bg-blue-100 text-blue-700",
  legal: "bg-purple-100 text-purple-700",
  both: "bg-teal-100 text-teal-700",
  advisory: "bg-yellow-100 text-yellow-700",
  compliance: "bg-red-100 text-red-700",
};

const ROLE_BG: Record<string, string> = {
  intake: "#0ea5e9",
  partner: "#8b5cf6",
  sa: "#f97316",
  ja: "#028a39",
};

const DEFAULT_STEP_LABELS: Record<number, string> = {
  1: "Intake Enhancer",
  2: "Partner P1",
  3: "SA Blueprint",
  4: "JA Research",
  5: "SA Adversarial",
  6: "Partner P2",
  7: "Partner P3",
};

function slugify(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .trim();
}

const defaultStepConfig = () => {
  const config: Record<string, { bot_variant_slug: string; label: string }> = {};
  for (let i = 1; i <= 7; i++) {
    config[String(i)] = { bot_variant_slug: "", label: DEFAULT_STEP_LABELS[i] || `Step ${i}` };
  }
  return config;
};

const EMPTY_FORM = {
  name: "",
  slug: "",
  description: "",
  practice_area: "tax",
  step_config: defaultStepConfig(),
  is_active: true,
  is_default: false,
};

export default function AdminPipelineTemplates() {
  const [templates, setTemplates] = useState<PipelineTemplate[]>([]);
  const [variants, setVariants] = useState<BotVariant[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTemplate, setSelectedTemplate] = useState<PipelineTemplate | null>(null);
  const [panelMode, setPanelMode] = useState<"view" | "edit">("view");
  const [editForm, setEditForm] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState<any>({ ...EMPTY_FORM, step_config: defaultStepConfig() });
  const [creating, setCreating] = useState(false);

  const fetchData = () => {
    setLoading(true);
    Promise.all([pipelineTemplatesApi.list(), botVariantsApi.list()])
      .then(([tRes, vRes]) => {
        setTemplates(tRes.data);
        setVariants(vRes.data.filter((v: BotVariant) => v.is_active));
      })
      .catch(() => toast.error("Không tải được dữ liệu"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchData();
  }, []);

  const openTemplate = (t: PipelineTemplate) => {
    // Ensure step_config has all 7 steps
    const config = { ...defaultStepConfig() };
    Object.keys(t.step_config || {}).forEach((k) => {
      config[k] = t.step_config[k];
    });
    setSelectedTemplate(t);
    setEditForm({ ...t, step_config: config });
    setPanelMode("view");
  };

  const closePanel = () => {
    setSelectedTemplate(null);
    setEditForm(null);
  };

  const handleSave = async () => {
    if (!selectedTemplate || !editForm) return;
    setSaving(true);
    try {
      await pipelineTemplatesApi.update(selectedTemplate.id, editForm);
      toast.success("Đã lưu pipeline template");
      fetchData();
      closePanel();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Lưu thất bại");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (t: PipelineTemplate) => {
    if (t.is_default) return;
    if (!window.confirm(`Xóa template "${t.name}"?`)) return;
    try {
      await pipelineTemplatesApi.delete(t.id);
      toast.success("Đã xóa template");
      if (selectedTemplate?.id === t.id) closePanel();
      fetchData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Xóa thất bại");
    }
  };

  const handleCreate = async () => {
    setCreating(true);
    try {
      await pipelineTemplatesApi.create(createForm);
      toast.success("Đã tạo pipeline template");
      setShowCreateModal(false);
      setCreateForm({ ...EMPTY_FORM, step_config: defaultStepConfig() });
      fetchData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Tạo thất bại");
    } finally {
      setCreating(false);
    }
  };

  const getRoleForSlug = (slug: string) => {
    const v = variants.find((v) => v.slug === slug);
    return v?.role || "";
  };

  const MiniPipeline = ({ stepConfig }: { stepConfig: Record<string, { bot_variant_slug: string; label: string }> }) => (
    <div className="flex gap-1 mt-3 overflow-x-auto pb-1">
      {[1, 2, 3, 4, 5, 6, 7].map((step) => {
        const s = stepConfig?.[String(step)];
        const role = s ? getRoleForSlug(s.bot_variant_slug) : "";
        const bg = role ? ROLE_BG[role] : "#d1d5db";
        return (
          <div
            key={step}
            className="flex-shrink-0 flex flex-col items-center"
            style={{ width: 52 }}
          >
            <div
              className="w-full rounded py-1 px-1 text-center text-white"
              style={{ background: bg, fontSize: 9 }}
            >
              <div className="font-bold opacity-60 text-xs">{step}</div>
              <div className="leading-tight mt-0.5 line-clamp-2" style={{ fontSize: 8 }}>
                {s?.label || `Step ${step}`}
              </div>
            </div>
            {step < 7 && (
              <div className="text-gray-300 mt-0.5" style={{ fontSize: 8 }}>→</div>
            )}
          </div>
        );
      })}
    </div>
  );

  const StepConfigEditor = ({
    form,
    setForm,
  }: {
    form: any;
    setForm: any;
  }) => (
    <div className="space-y-2">
      {[1, 2, 3, 4, 5, 6, 7].map((step) => {
        const key = String(step);
        const s = form.step_config?.[key] || { bot_variant_slug: "", label: DEFAULT_STEP_LABELS[step] };
        return (
          <div key={step} className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
            <div
              className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
              style={{
                background: getRoleForSlug(s.bot_variant_slug)
                  ? ROLE_BG[getRoleForSlug(s.bot_variant_slug)]
                  : "#9ca3af",
              }}
            >
              {step}
            </div>
            <div className="flex-1 min-w-0">
              <input
                className="input-field text-xs py-1 mb-1"
                value={s.label}
                onChange={(e) =>
                  setForm({
                    ...form,
                    step_config: {
                      ...form.step_config,
                      [key]: { ...s, label: e.target.value },
                    },
                  })
                }
                placeholder={`Nhãn bước ${step}`}
              />
              <select
                className="input-field text-xs py-1"
                value={s.bot_variant_slug}
                onChange={(e) =>
                  setForm({
                    ...form,
                    step_config: {
                      ...form.step_config,
                      [key]: { ...s, bot_variant_slug: e.target.value },
                    },
                  })
                }
              >
                <option value="">— Chọn Bot Variant —</option>
                {variants.map((v) => (
                  <option key={v.id} value={v.slug}>
                    [{v.role.toUpperCase()}] {v.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        );
      })}
    </div>
  );

  const TemplateFormBody = ({ form, setForm }: { form: any; setForm: any }) => (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">Tên Template *</label>
          <input
            className="input-field"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value, slug: slugify(e.target.value) })}
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">Slug</label>
          <input
            className="input-field font-mono text-xs"
            value={form.slug}
            onChange={(e) => setForm({ ...form, slug: e.target.value })}
          />
        </div>
      </div>
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-1">Mô tả</label>
        <textarea
          className="input-field"
          rows={2}
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
      </div>
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-1">Lĩnh vực</label>
        <select
          className="input-field"
          value={form.practice_area}
          onChange={(e) => setForm({ ...form, practice_area: e.target.value })}
        >
          {PRACTICE_AREAS.map((a) => (
            <option key={a} value={a}>{a}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-2">Cấu hình 7 bước</label>
        <StepConfigEditor form={form} setForm={setForm} />
      </div>
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-2">Preview Pipeline</label>
        <MiniPipeline stepConfig={form.step_config} />
      </div>
      <div className="flex gap-6">
        <div className="flex items-center gap-2">
          <label className="text-xs font-semibold text-gray-600">Active</label>
          <button
            type="button"
            onClick={() => setForm({ ...form, is_active: !form.is_active })}
            className={`relative inline-flex w-10 h-5 rounded-full transition-colors cursor-pointer ${
              form.is_active ? "bg-green-500" : "bg-gray-300"
            }`}
          >
            <span
              className={`inline-block w-4 h-4 bg-white rounded-full shadow transition-transform mt-0.5 ${
                form.is_active ? "translate-x-5" : "translate-x-0.5"
              }`}
            />
          </button>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs font-semibold text-gray-600">Mặc định</label>
          <button
            type="button"
            onClick={() => setForm({ ...form, is_default: !form.is_default })}
            className={`relative inline-flex w-10 h-5 rounded-full transition-colors cursor-pointer ${
              form.is_default ? "bg-yellow-400" : "bg-gray-300"
            }`}
          >
            <span
              className={`inline-block w-4 h-4 bg-white rounded-full shadow transition-transform mt-0.5 ${
                form.is_default ? "translate-x-5" : "translate-x-0.5"
              }`}
            />
          </button>
          {form.is_default && (
            <span className="text-xs text-yellow-600">⚠️ Chỉ một template có thể là mặc định</span>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex h-full gap-0">
      <div className="flex-1">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Pipeline Templates</h1>
            <p className="text-sm text-gray-500 mt-1">
              {templates.length} templates — {templates.filter((t) => t.is_active).length} đang hoạt động
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm font-medium"
            style={{ background: "#028a39" }}
          >
            <Plus className="w-4 h-4" />
            Thêm Template
          </button>
        </div>

        {/* Cards */}
        {loading ? (
          <div className="flex items-center justify-center h-48">
            <div className="w-8 h-8 border-4 border-gray-200 border-t-green-600 rounded-full animate-spin" />
          </div>
        ) : templates.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <LayoutTemplate className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Không có pipeline template nào</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {templates.map((t) => (
              <div
                key={t.id}
                onClick={() => openTemplate(t)}
                className={`bg-white rounded-xl border p-4 cursor-pointer hover:shadow-md transition-all ${
                  selectedTemplate?.id === t.id
                    ? "border-green-400 shadow-md"
                    : "border-gray-100 hover:border-gray-200"
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="font-semibold text-gray-900 text-sm">{t.name}</p>
                    {t.is_default && (
                      <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-yellow-100 text-yellow-700 font-medium">
                        <Star className="w-3 h-3" />
                        Mặc định
                      </span>
                    )}
                    {!t.is_active && (
                      <span className="px-2 py-0.5 rounded-full text-xs bg-red-50 text-red-500">
                        inactive
                      </span>
                    )}
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium flex-shrink-0 ${
                      PRACTICE_COLORS[t.practice_area] || "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {t.practice_area}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mb-1">{t.description}</p>
                <MiniPipeline stepConfig={t.step_config} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Side Panel */}
      {selectedTemplate && editForm && (
        <div className="fixed top-0 right-0 h-full w-[560px] bg-white border-l border-gray-200 shadow-2xl z-20 flex flex-col">
          <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
            <div className="flex items-center gap-2">
              {selectedTemplate.is_default && (
                <Star className="w-4 h-4 text-yellow-500" />
              )}
              <div>
                <h2 className="font-bold text-gray-900">{selectedTemplate.name}</h2>
                <p className="text-xs text-gray-500">{selectedTemplate.slug}</p>
              </div>
            </div>
            <button onClick={closePanel} className="text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="flex border-b border-gray-100 px-5">
            {(["view", "edit"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setPanelMode(tab)}
                className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
                  panelMode === tab
                    ? "border-green-600 text-green-700"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                {tab === "view" ? "Chi tiết" : "Chỉnh sửa"}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto p-5">
            {panelMode === "view" ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-400 mb-1">Lĩnh vực</p>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        PRACTICE_COLORS[selectedTemplate.practice_area] || "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {selectedTemplate.practice_area}
                    </span>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-400 mb-1">Trạng thái</p>
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          selectedTemplate.is_active
                            ? "bg-green-100 text-green-700"
                            : "bg-red-100 text-red-600"
                        }`}
                      >
                        {selectedTemplate.is_active ? "Active" : "Inactive"}
                      </span>
                      {selectedTemplate.is_default && (
                        <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-yellow-100 text-yellow-700">
                          <Star className="w-3 h-3" />
                          Mặc định
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-600 mb-1">Mô tả</p>
                  <p className="text-sm text-gray-700">{selectedTemplate.description}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-600 mb-2">Cấu hình bước</p>
                  <div className="space-y-2">
                    {[1, 2, 3, 4, 5, 6, 7].map((step) => {
                      const s = selectedTemplate.step_config?.[String(step)];
                      const role = s ? getRoleForSlug(s.bot_variant_slug) : "";
                      return (
                        <div key={step} className="flex items-center gap-2">
                          <div
                            className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                            style={{ background: role ? ROLE_BG[role] : "#9ca3af" }}
                          >
                            {step}
                          </div>
                          <div className="flex-1">
                            <p className="text-xs font-medium text-gray-800">{s?.label || `Step ${step}`}</p>
                            <p className="text-xs text-gray-400 font-mono">{s?.bot_variant_slug || "—"}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-600 mb-2">Preview</p>
                  <MiniPipeline stepConfig={selectedTemplate.step_config} />
                </div>
                <div className="flex gap-3 pt-2">
                  <button
                    onClick={() => setPanelMode("edit")}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium bg-green-50 text-green-700 hover:bg-green-100"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                    Chỉnh sửa
                  </button>
                  <button
                    onClick={() => handleDelete(selectedTemplate)}
                    disabled={selectedTemplate.is_default}
                    title={selectedTemplate.is_default ? "Template mặc định không thể xóa" : ""}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium ${
                      selectedTemplate.is_default
                        ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                        : "bg-red-50 text-red-600 hover:bg-red-100"
                    }`}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    Xóa
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <TemplateFormBody form={editForm} setForm={setEditForm} />
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="w-full flex items-center justify-center gap-2 py-2 rounded-lg text-white text-sm font-medium"
                  style={{ background: "#028a39" }}
                >
                  {saving ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Đang lưu...
                    </>
                  ) : (
                    "Lưu thay đổi"
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/40 z-30 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h2 className="font-bold text-gray-900">Thêm Pipeline Template Mới</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-6">
              <TemplateFormBody form={createForm} setForm={setCreateForm} />
            </div>
            <div className="px-6 py-4 border-t border-gray-100 flex gap-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 py-2 rounded-lg border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50"
              >
                Huỷ
              </button>
              <button
                onClick={handleCreate}
                disabled={creating || !createForm.name.trim()}
                className="flex-1 py-2 rounded-lg text-white text-sm font-medium flex items-center justify-center gap-2"
                style={{ background: "#028a39" }}
              >
                {creating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Đang tạo...
                  </>
                ) : (
                  "Tạo Template"
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
