import { useState, useEffect } from "react";
import { botVariantsApi, skillsApi } from "../lib/api";
import { Plus, X, Edit2, Trash2, Bot } from "lucide-react";
import toast from "react-hot-toast";

interface BotVariant {
  id: number;
  name: string;
  slug: string;
  role: string;
  description: string;
  system_prompt_base: string | null;
  skill_ids: number[];
  model_override: string | null;
  provider_override: string | null;
  is_active: boolean;
  is_builtin: boolean;
  created_at: string;
}

interface Skill {
  id: number;
  name: string;
  category: string;
  applicable_bots: string[];
  is_active: boolean;
}

const ROLES = ["Tất cả", "intake", "partner", "sa", "ja"];

const ROLE_COLORS: Record<string, string> = {
  intake: "bg-blue-100 text-blue-700",
  partner: "bg-purple-100 text-purple-700",
  sa: "bg-orange-100 text-orange-700",
  ja: "bg-green-100 text-green-700",
};

const ROLE_BG: Record<string, string> = {
  intake: "#0ea5e9",
  partner: "#8b5cf6",
  sa: "#f97316",
  ja: "#028a39",
};

const PROVIDERS = ["", "anthropic", "openai", "deepseek", "openrouter"];

function slugify(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .trim();
}

const EMPTY_FORM = {
  name: "",
  slug: "",
  role: "intake",
  description: "",
  system_prompt_base: "",
  skill_ids: [] as number[],
  model_override: "",
  provider_override: "",
  is_active: true,
};

export default function AdminBotVariants() {
  const [variants, setVariants] = useState<BotVariant[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [roleFilter, setRoleFilter] = useState("Tất cả");
  const [selectedVariant, setSelectedVariant] = useState<BotVariant | null>(null);
  const [panelMode, setPanelMode] = useState<"view" | "edit">("view");
  const [editForm, setEditForm] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState<any>({ ...EMPTY_FORM });
  const [creating, setCreating] = useState(false);

  const fetchData = () => {
    setLoading(true);
    Promise.all([botVariantsApi.list(), skillsApi.list()])
      .then(([vRes, sRes]) => {
        setVariants(vRes.data);
        setSkills(sRes.data);
      })
      .catch(() => toast.error("Không tải được dữ liệu"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filtered = variants.filter(
    (v) => roleFilter === "Tất cả" || v.role === roleFilter
  );

  const openVariant = (v: BotVariant) => {
    setSelectedVariant(v);
    setEditForm({ ...v, system_prompt_base: v.system_prompt_base || "", model_override: v.model_override || "", provider_override: v.provider_override || "" });
    setPanelMode("view");
  };

  const closePanel = () => {
    setSelectedVariant(null);
    setEditForm(null);
  };

  const handleSave = async () => {
    if (!selectedVariant || !editForm) return;
    setSaving(true);
    try {
      const payload = {
        ...editForm,
        system_prompt_base: editForm.system_prompt_base || null,
        model_override: editForm.model_override || null,
        provider_override: editForm.provider_override || null,
      };
      await botVariantsApi.update(selectedVariant.id, payload);
      toast.success("Đã lưu bot variant");
      fetchData();
      closePanel();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Lưu thất bại");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (v: BotVariant) => {
    if (v.is_builtin) return;
    if (!window.confirm(`Xóa bot variant "${v.name}"?`)) return;
    try {
      await botVariantsApi.delete(v.id);
      toast.success("Đã xóa bot variant");
      if (selectedVariant?.id === v.id) closePanel();
      fetchData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Xóa thất bại");
    }
  };

  const handleCreate = async () => {
    setCreating(true);
    try {
      const payload = {
        ...createForm,
        system_prompt_base: createForm.system_prompt_base || null,
        model_override: createForm.model_override || null,
        provider_override: createForm.provider_override || null,
      };
      await botVariantsApi.create(payload);
      toast.success("Đã tạo bot variant");
      setShowCreateModal(false);
      setCreateForm({ ...EMPTY_FORM });
      fetchData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Tạo thất bại");
    } finally {
      setCreating(false);
    }
  };

  const toggleSkill = (form: any, setForm: any, skillId: number) => {
    const ids: number[] = form.skill_ids || [];
    const next = ids.includes(skillId) ? ids.filter((i) => i !== skillId) : [...ids, skillId];
    setForm({ ...form, skill_ids: next });
  };

  const SkillChecklist = ({
    form,
    setForm,
    disabled,
  }: {
    form: any;
    setForm: any;
    disabled?: boolean;
  }) => (
    <div className="space-y-1.5 max-h-48 overflow-y-auto border border-gray-100 rounded-lg p-2">
      {skills.length === 0 ? (
        <p className="text-xs text-gray-400 p-2">Không có skill nào</p>
      ) : (
        skills.map((skill) => (
          <label key={skill.id} className="flex items-start gap-2 cursor-pointer hover:bg-gray-50 rounded p-1">
            <input
              type="checkbox"
              checked={(form.skill_ids || []).includes(skill.id)}
              onChange={() => !disabled && toggleSkill(form, setForm, skill.id)}
              disabled={disabled}
              className="mt-0.5 rounded"
            />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-800">{skill.name}</p>
              <div className="flex items-center gap-1 mt-0.5 flex-wrap">
                <span className="px-1 py-0 rounded text-xs bg-gray-100 text-gray-500">
                  {skill.category}
                </span>
                {skill.applicable_bots.map((b) => (
                  <span
                    key={b}
                    className="px-1 py-0 rounded text-xs"
                    style={{ background: `${ROLE_BG[b]}20`, color: ROLE_BG[b] }}
                  >
                    {b}
                  </span>
                ))}
              </div>
            </div>
          </label>
        ))
      )}
    </div>
  );

  const EditFormBody = ({
    form,
    setForm,
    disabled,
  }: {
    form: any;
    setForm: any;
    disabled?: boolean;
  }) => (
    <div className="space-y-4">
      {disabled && (
        <div className="flex items-start gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-700">
          <span>⚠️</span>
          <span>Bot variant mặc định (built-in) — chỉ có thể xem, không thể sửa.</span>
        </div>
      )}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">Tên *</label>
          <input
            className="input-field"
            value={form.name}
            disabled={disabled}
            onChange={(e) => {
              setForm({ ...form, name: e.target.value, slug: slugify(e.target.value) });
            }}
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">Slug</label>
          <input
            className="input-field font-mono text-xs"
            value={form.slug}
            disabled={disabled}
            onChange={(e) => setForm({ ...form, slug: e.target.value })}
          />
        </div>
      </div>
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-1">Role</label>
        <select
          className="input-field"
          value={form.role}
          disabled={disabled}
          onChange={(e) => setForm({ ...form, role: e.target.value })}
        >
          <option value="intake">Intake</option>
          <option value="partner">Partner</option>
          <option value="sa">SA</option>
          <option value="ja">JA</option>
        </select>
      </div>
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-1">Mô tả</label>
        <textarea
          className="input-field"
          rows={2}
          value={form.description}
          disabled={disabled}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
      </div>
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-1">
          System Prompt Base
        </label>
        <textarea
          className="input-field font-mono text-xs"
          rows={6}
          value={form.system_prompt_base}
          disabled={disabled}
          onChange={(e) => setForm({ ...form, system_prompt_base: e.target.value })}
          placeholder="Để trống để dùng system prompt mặc định"
        />
      </div>
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-2">
          Skills ({(form.skill_ids || []).length} đã chọn)
        </label>
        <SkillChecklist form={form} setForm={setForm} disabled={disabled} />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">
            Model Override (tùy chọn)
          </label>
          <input
            className="input-field font-mono text-xs"
            value={form.model_override}
            disabled={disabled}
            onChange={(e) => setForm({ ...form, model_override: e.target.value })}
            placeholder="vd: claude-3-5-sonnet-20241022"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1">
            Provider Override (tùy chọn)
          </label>
          <select
            className="input-field"
            value={form.provider_override}
            disabled={disabled}
            onChange={(e) => setForm({ ...form, provider_override: e.target.value })}
          >
            {PROVIDERS.map((p) => (
              <option key={p} value={p}>
                {p || "— Mặc định —"}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <label className="text-xs font-semibold text-gray-600">Active</label>
        <button
          type="button"
          onClick={() => !disabled && setForm({ ...form, is_active: !form.is_active })}
          className={`relative inline-flex w-10 h-5 rounded-full transition-colors ${
            form.is_active ? "bg-green-500" : "bg-gray-300"
          } ${disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer"}`}
        >
          <span
            className={`inline-block w-4 h-4 bg-white rounded-full shadow transition-transform mt-0.5 ${
              form.is_active ? "translate-x-5" : "translate-x-0.5"
            }`}
          />
        </button>
      </div>
    </div>
  );

  return (
    <div className="flex h-full gap-0">
      {/* Main */}
      <div className="flex-1">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Bot Variants</h1>
            <p className="text-sm text-gray-500 mt-1">
              {variants.length} variants — {variants.filter((v) => v.is_active).length} đang hoạt động
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm font-medium"
            style={{ background: "#028a39" }}
          >
            <Plus className="w-4 h-4" />
            Thêm Bot Variant
          </button>
        </div>

        {/* Role tabs */}
        <div className="flex gap-1 mb-6 border-b border-gray-100">
          {ROLES.map((role) => (
            <button
              key={role}
              onClick={() => setRoleFilter(role)}
              className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
                roleFilter === role
                  ? "border-green-600 text-green-700"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {role === "Tất cả" ? "Tất cả" : role.toUpperCase()}
              <span className="ml-1.5 text-xs opacity-60">
                ({role === "Tất cả" ? variants.length : variants.filter((v) => v.role === role).length})
              </span>
            </button>
          ))}
        </div>

        {/* Cards grid */}
        {loading ? (
          <div className="flex items-center justify-center h-48">
            <div className="w-8 h-8 border-4 border-gray-200 border-t-green-600 rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <Bot className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Không có bot variant nào</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filtered.map((v) => (
              <div
                key={v.id}
                onClick={() => openVariant(v)}
                className={`bg-white rounded-xl border p-4 cursor-pointer hover:shadow-md transition-all ${
                  selectedVariant?.id === v.id
                    ? "border-green-400 shadow-md"
                    : "border-gray-100 hover:border-gray-200"
                }`}
              >
                {/* Role accent bar */}
                <div
                  className="h-1 rounded-full mb-3"
                  style={{ background: ROLE_BG[v.role] || "#6b7280" }}
                />
                {/* Name + badges */}
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <p className="font-semibold text-gray-900 text-sm">{v.name}</p>
                    <p className="text-xs text-gray-400 font-mono">{v.slug}</p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        ROLE_COLORS[v.role] || "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {v.role.toUpperCase()}
                    </span>
                    {v.is_builtin && (
                      <span className="px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-500">
                        built-in
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-xs text-gray-500 mb-3 line-clamp-2">{v.description}</p>
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>{v.skill_ids.length} skills</span>
                  {v.model_override && (
                    <span className="font-mono bg-gray-50 px-1.5 py-0.5 rounded">
                      {v.model_override.split("-").slice(0, 3).join("-")}
                    </span>
                  )}
                  <span
                    className={`w-2 h-2 rounded-full ${v.is_active ? "bg-green-400" : "bg-gray-300"}`}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Side Panel */}
      {selectedVariant && editForm && (
        <div className="fixed top-0 right-0 h-full w-[540px] bg-white border-l border-gray-200 shadow-2xl z-20 flex flex-col">
          <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div
                className="w-3 h-3 rounded-full"
                style={{ background: ROLE_BG[selectedVariant.role] || "#6b7280" }}
              />
              <div>
                <h2 className="font-bold text-gray-900">{selectedVariant.name}</h2>
                <p className="text-xs text-gray-500">{selectedVariant.slug}</p>
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
                    <p className="text-xs text-gray-400 mb-1">Role</p>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${ROLE_COLORS[selectedVariant.role]}`}
                    >
                      {selectedVariant.role.toUpperCase()}
                    </span>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-400 mb-1">Trạng thái</p>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        selectedVariant.is_active
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-600"
                      }`}
                    >
                      {selectedVariant.is_active ? "Active" : "Inactive"}
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-600 mb-1">Mô tả</p>
                  <p className="text-sm text-gray-700">{selectedVariant.description}</p>
                </div>
                {selectedVariant.system_prompt_base && (
                  <div>
                    <p className="text-xs font-semibold text-gray-600 mb-1">System Prompt Base</p>
                    <pre className="bg-gray-50 rounded-lg p-3 text-xs font-mono text-gray-700 overflow-x-auto whitespace-pre-wrap max-h-40 overflow-y-auto">
                      {selectedVariant.system_prompt_base}
                    </pre>
                  </div>
                )}
                <div>
                  <p className="text-xs font-semibold text-gray-600 mb-2">
                    Skills ({selectedVariant.skill_ids.length})
                  </p>
                  <div className="flex gap-1.5 flex-wrap">
                    {selectedVariant.skill_ids.map((sid) => {
                      const skill = skills.find((s) => s.id === sid);
                      return (
                        <span
                          key={sid}
                          className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
                        >
                          {skill ? skill.name : `#${sid}`}
                        </span>
                      );
                    })}
                    {selectedVariant.skill_ids.length === 0 && (
                      <span className="text-xs text-gray-400">Chưa gán skill nào</span>
                    )}
                  </div>
                </div>
                {(selectedVariant.model_override || selectedVariant.provider_override) && (
                  <div className="bg-gray-50 rounded-lg p-3 space-y-1">
                    {selectedVariant.model_override && (
                      <p className="text-xs text-gray-600">
                        <span className="font-semibold">Model:</span>{" "}
                        <code className="font-mono">{selectedVariant.model_override}</code>
                      </p>
                    )}
                    {selectedVariant.provider_override && (
                      <p className="text-xs text-gray-600">
                        <span className="font-semibold">Provider:</span>{" "}
                        {selectedVariant.provider_override}
                      </p>
                    )}
                  </div>
                )}
                <div className="flex gap-3 pt-2">
                  <button
                    onClick={() => setPanelMode("edit")}
                    disabled={selectedVariant.is_builtin}
                    title={selectedVariant.is_builtin ? "Bot variant mặc định không thể sửa" : ""}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium ${
                      selectedVariant.is_builtin
                        ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                        : "bg-green-50 text-green-700 hover:bg-green-100"
                    }`}
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                    Chỉnh sửa
                  </button>
                  <button
                    onClick={() => handleDelete(selectedVariant)}
                    disabled={selectedVariant.is_builtin}
                    title={selectedVariant.is_builtin ? "Bot variant mặc định không thể xóa" : ""}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium ${
                      selectedVariant.is_builtin
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
                <EditFormBody
                  form={editForm}
                  setForm={setEditForm}
                  disabled={selectedVariant.is_builtin}
                />
                {!selectedVariant.is_builtin && (
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
                )}
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
              <h2 className="font-bold text-gray-900">Thêm Bot Variant Mới</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-6">
              <EditFormBody form={createForm} setForm={setCreateForm} />
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
                  "Tạo Bot Variant"
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
