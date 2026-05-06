import { useState, useEffect } from "react";
import { skillsApi } from "../lib/api";
import { Plus, X, Eye, Edit2, Trash2, Tag, Bot } from "lucide-react";
import toast from "react-hot-toast";

interface Skill {
  id: number;
  name: string;
  version: string;
  description: string;
  category: string;
  tags: string[];
  applicable_bots: string[];
  content_markdown: string;
  is_active: boolean;
  is_builtin: boolean;
  created_at: string;
  updated_at: string;
}

const CATEGORIES = ["Tất cả", "tax", "legal", "advisory", "compliance"];
const BOT_FILTERS = ["Tất cả", "partner", "ja", "sa", "intake"];

const CATEGORY_COLORS: Record<string, string> = {
  tax: "bg-blue-100 text-blue-700",
  legal: "bg-purple-100 text-purple-700",
  advisory: "bg-yellow-100 text-yellow-700",
  compliance: "bg-red-100 text-red-700",
};

const BOT_COLORS: Record<string, string> = {
  partner: "bg-purple-100 text-purple-700",
  ja: "bg-green-100 text-green-700",
  sa: "bg-orange-100 text-orange-700",
  intake: "bg-blue-100 text-blue-700",
};

function simpleMarkdown(md: string): string {
  if (!md) return "";
  let html = md
    // Headings
    .replace(/^### (.+)$/gm, "<h3 class=\"text-base font-bold mt-4 mb-1\">$1</h3>")
    .replace(/^## (.+)$/gm, "<h2 class=\"text-lg font-bold mt-5 mb-2\">$1</h2>")
    .replace(/^# (.+)$/gm, "<h1 class=\"text-xl font-bold mt-6 mb-2\">$1</h1>")
    // Bold
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    // Italic
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    // Code block
    .replace(/```[\s\S]*?```/g, (m) => `<pre class="bg-gray-100 rounded p-2 text-xs font-mono my-2 overflow-x-auto">${m.replace(/```\w*\n?/g, "").replace(/```/g, "")}</pre>`)
    // Inline code
    .replace(/`(.+?)`/g, "<code class=\"bg-gray-100 rounded px-1 text-xs font-mono\">$1</code>")
    // Horizontal rule
    .replace(/^---$/gm, "<hr class=\"my-4 border-gray-200\" />")
    // Bullet points
    .replace(/^- (.+)$/gm, "<li class=\"ml-4 list-disc\">$1</li>")
    .replace(/(<li[\s\S]*?<\/li>)+/g, (m) => `<ul class="my-2 space-y-1">${m}</ul>`)
    // Double newline = paragraph
    .replace(/\n\n/g, "</p><p class=\"mb-2\">");
  return `<p class="mb-2">${html}</p>`;
}

const EMPTY_SKILL: Omit<Skill, "id" | "created_at" | "updated_at"> = {
  name: "",
  version: "1.0",
  description: "",
  category: "tax",
  tags: [],
  applicable_bots: [],
  content_markdown: "",
  is_active: true,
  is_builtin: false,
};

export default function AdminSkills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState("Tất cả");
  const [botFilter, setBotFilter] = useState("Tất cả");
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);
  const [panelTab, setPanelTab] = useState<"view" | "edit" | "preview">("view");
  const [editForm, setEditForm] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState<any>({ ...EMPTY_SKILL });
  const [creating, setCreating] = useState(false);

  const fetchSkills = () => {
    setLoading(true);
    skillsApi
      .list()
      .then((r) => setSkills(r.data))
      .catch(() => toast.error("Không tải được danh sách skills"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchSkills();
  }, []);

  const filtered = skills.filter((s) => {
    const catOk = categoryFilter === "Tất cả" || s.category === categoryFilter;
    const botOk = botFilter === "Tất cả" || s.applicable_bots.includes(botFilter);
    return catOk && botOk;
  });

  const openSkill = (skill: Skill) => {
    setSelectedSkill(skill);
    setEditForm({
      ...skill,
      tags: skill.tags.join(", "),
    });
    setPanelTab("view");
  };

  const closePanel = () => {
    setSelectedSkill(null);
    setEditForm(null);
  };

  const handleSave = async () => {
    if (!selectedSkill || !editForm) return;
    setSaving(true);
    try {
      const payload = {
        ...editForm,
        tags: editForm.tags
          ? editForm.tags.split(",").map((t: string) => t.trim()).filter(Boolean)
          : [],
      };
      await skillsApi.update(selectedSkill.id, payload);
      toast.success("Đã lưu skill");
      fetchSkills();
      closePanel();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Lưu thất bại");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (skill: Skill) => {
    if (skill.is_builtin) return;
    if (!window.confirm(`Xóa skill "${skill.name}"?`)) return;
    try {
      await skillsApi.delete(skill.id);
      toast.success("Đã xóa skill");
      if (selectedSkill?.id === skill.id) closePanel();
      fetchSkills();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Xóa thất bại");
    }
  };

  const handleCreate = async () => {
    setCreating(true);
    try {
      const payload = {
        ...createForm,
        tags: createForm.tags
          ? createForm.tags.split(",").map((t: string) => t.trim()).filter(Boolean)
          : [],
      };
      await skillsApi.create(payload);
      toast.success("Đã tạo skill");
      setShowCreateModal(false);
      setCreateForm({ ...EMPTY_SKILL });
      fetchSkills();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Tạo thất bại");
    } finally {
      setCreating(false);
    }
  };

  const toggleBot = (form: any, setForm: any, bot: string) => {
    const bots: string[] = form.applicable_bots || [];
    const next = bots.includes(bot) ? bots.filter((b) => b !== bot) : [...bots, bot];
    setForm({ ...form, applicable_bots: next });
  };

  return (
    <div className="flex h-full gap-0">
      {/* Main panel */}
      <div className={`flex-1 transition-all ${selectedSkill ? "mr-0" : ""}`}>
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Quản lý Skills</h1>
            <p className="text-sm text-gray-500 mt-1">
              {skills.length} skills — {skills.filter((s) => s.is_active).length} đang hoạt động
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-white text-sm font-medium"
            style={{ background: "#028a39" }}
          >
            <Plus className="w-4 h-4" />
            Thêm Skill
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-4 mb-4 flex-wrap">
          <div className="flex gap-1 flex-wrap">
            <span className="text-xs font-medium text-gray-500 self-center mr-1">Danh mục:</span>
            {CATEGORIES.map((c) => (
              <button
                key={c}
                onClick={() => setCategoryFilter(c)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  categoryFilter === c
                    ? "text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
                style={categoryFilter === c ? { background: "#028a39" } : {}}
              >
                {c}
              </button>
            ))}
          </div>
          <div className="flex gap-1 flex-wrap">
            <span className="text-xs font-medium text-gray-500 self-center mr-1">Bot:</span>
            {BOT_FILTERS.map((b) => (
              <button
                key={b}
                onClick={() => setBotFilter(b)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  botFilter === b
                    ? "text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
                style={botFilter === b ? { background: "#028a39" } : {}}
              >
                {b}
              </button>
            ))}
          </div>
        </div>

        {/* Skills grid */}
        {loading ? (
          <div className="flex items-center justify-center h-48">
            <div className="w-8 h-8 border-4 border-gray-200 border-t-green-600 rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <Tag className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Không có skill nào phù hợp</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filtered.map((skill) => (
              <div
                key={skill.id}
                onClick={() => openSkill(skill)}
                className={`bg-white rounded-xl border p-4 cursor-pointer hover:shadow-md transition-all ${
                  selectedSkill?.id === skill.id
                    ? "border-green-400 shadow-md"
                    : "border-gray-100 hover:border-gray-200"
                }`}
              >
                {/* Top row */}
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <span className="font-semibold text-gray-900 text-sm truncate">
                        {skill.name}
                      </span>
                      <span className="px-1.5 py-0.5 rounded text-xs bg-gray-100 text-gray-500 font-mono">
                        v{skill.version}
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          CATEGORY_COLORS[skill.category] || "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {skill.category}
                      </span>
                      {skill.is_builtin && (
                        <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500">
                          built-in
                        </span>
                      )}
                      {!skill.is_active && (
                        <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-red-50 text-red-500">
                          inactive
                        </span>
                      )}
                    </div>
                  </div>
                  <div
                    className={`w-2.5 h-2.5 rounded-full mt-1 flex-shrink-0 ${
                      skill.is_active ? "bg-green-400" : "bg-gray-300"
                    }`}
                  />
                </div>

                {/* Description */}
                <p className="text-xs text-gray-500 mb-3 line-clamp-2">{skill.description}</p>

                {/* Applicable bots */}
                {skill.applicable_bots.length > 0 && (
                  <div className="flex gap-1 flex-wrap">
                    {skill.applicable_bots.map((bot) => (
                      <span
                        key={bot}
                        className={`px-1.5 py-0.5 rounded text-xs font-medium ${
                          BOT_COLORS[bot] || "bg-gray-100 text-gray-500"
                        }`}
                      >
                        {bot}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Side panel */}
      {selectedSkill && editForm && (
        <div className="fixed top-0 right-0 h-full w-[520px] bg-white border-l border-gray-200 shadow-2xl z-20 flex flex-col">
          {/* Panel header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
            <div>
              <h2 className="font-bold text-gray-900">{selectedSkill.name}</h2>
              <p className="text-xs text-gray-500">v{selectedSkill.version}</p>
            </div>
            <button onClick={closePanel} className="text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-gray-100 px-5">
            {(["view", "edit", "preview"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setPanelTab(tab)}
                className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
                  panelTab === tab
                    ? "border-green-600 text-green-700"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                {tab === "view" ? "Chi tiết" : tab === "edit" ? "Chỉnh sửa" : "Preview MD"}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto p-5">
            {panelTab === "view" && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-400 mb-1">Danh mục</p>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        CATEGORY_COLORS[selectedSkill.category] || "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {selectedSkill.category}
                    </span>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-400 mb-1">Trạng thái</p>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        selectedSkill.is_active
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-600"
                      }`}
                    >
                      {selectedSkill.is_active ? "Active" : "Inactive"}
                    </span>
                  </div>
                </div>

                <div>
                  <p className="text-xs font-semibold text-gray-600 mb-1">Mô tả</p>
                  <p className="text-sm text-gray-700">{selectedSkill.description}</p>
                </div>

                {selectedSkill.tags.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-gray-600 mb-1">Tags</p>
                    <div className="flex gap-1 flex-wrap">
                      {selectedSkill.tags.map((t) => (
                        <span key={t} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {selectedSkill.applicable_bots.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-gray-600 mb-1">Applicable Bots</p>
                    <div className="flex gap-1 flex-wrap">
                      {selectedSkill.applicable_bots.map((b) => (
                        <span
                          key={b}
                          className={`px-2 py-0.5 rounded text-xs font-medium ${BOT_COLORS[b] || "bg-gray-100 text-gray-600"}`}
                        >
                          {b}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <p className="text-xs font-semibold text-gray-600 mb-2">Nội dung Markdown</p>
                  <pre className="bg-gray-50 rounded-lg p-3 text-xs font-mono text-gray-700 overflow-x-auto whitespace-pre-wrap max-h-64 overflow-y-auto">
                    {selectedSkill.content_markdown || "(Chưa có nội dung)"}
                  </pre>
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    onClick={() => setPanelTab("edit")}
                    disabled={selectedSkill.is_builtin}
                    title={selectedSkill.is_builtin ? "Skill mặc định không thể sửa" : ""}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      selectedSkill.is_builtin
                        ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                        : "bg-green-50 text-green-700 hover:bg-green-100"
                    }`}
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                    Chỉnh sửa
                  </button>
                  <button
                    onClick={() => handleDelete(selectedSkill)}
                    disabled={selectedSkill.is_builtin}
                    title={selectedSkill.is_builtin ? "Skill mặc định không thể xóa" : ""}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      selectedSkill.is_builtin
                        ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                        : "bg-red-50 text-red-600 hover:bg-red-100"
                    }`}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    Xóa
                  </button>
                </div>
              </div>
            )}

            {panelTab === "edit" && (
              <div className="space-y-4">
                {selectedSkill.is_builtin && (
                  <div className="flex items-start gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-700">
                    <span>⚠️</span>
                    <span>Skill mặc định (built-in) — chỉ có thể xem, không thể sửa.</span>
                  </div>
                )}
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1">Tên Skill</label>
                  <input
                    className="input-field"
                    value={editForm.name}
                    onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                    disabled={selectedSkill.is_builtin}
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-gray-600 mb-1">Version</label>
                    <input
                      className="input-field"
                      value={editForm.version}
                      onChange={(e) => setEditForm({ ...editForm, version: e.target.value })}
                      disabled={selectedSkill.is_builtin}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-600 mb-1">Danh mục</label>
                    <select
                      className="input-field"
                      value={editForm.category}
                      onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                      disabled={selectedSkill.is_builtin}
                    >
                      <option value="tax">Tax</option>
                      <option value="legal">Legal</option>
                      <option value="advisory">Advisory</option>
                      <option value="compliance">Compliance</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1">Mô tả</label>
                  <textarea
                    className="input-field"
                    rows={2}
                    value={editForm.description}
                    onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                    disabled={selectedSkill.is_builtin}
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1">Tags (phẩy phân cách)</label>
                  <input
                    className="input-field"
                    value={editForm.tags}
                    placeholder="vd: vat, tax-treaty, withholding"
                    onChange={(e) => setEditForm({ ...editForm, tags: e.target.value })}
                    disabled={selectedSkill.is_builtin}
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-2">Applicable Bots</label>
                  <div className="flex gap-3 flex-wrap">
                    {["partner", "ja", "sa", "intake"].map((bot) => (
                      <label key={bot} className="flex items-center gap-1.5 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={(editForm.applicable_bots || []).includes(bot)}
                          onChange={() => toggleBot(editForm, setEditForm, bot)}
                          disabled={selectedSkill.is_builtin}
                          className="rounded"
                        />
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-medium ${BOT_COLORS[bot]}`}
                        >
                          {bot}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-xs font-semibold text-gray-600">Nội dung Markdown</label>
                    <button
                      type="button"
                      onClick={() => setPanelTab("preview")}
                      className="flex items-center gap-1 text-xs text-green-700 hover:underline"
                    >
                      <Eye className="w-3 h-3" />
                      Preview
                    </button>
                  </div>
                  <textarea
                    className="input-field font-mono text-xs"
                    style={{ minHeight: 400 }}
                    value={editForm.content_markdown}
                    onChange={(e) => setEditForm({ ...editForm, content_markdown: e.target.value })}
                    disabled={selectedSkill.is_builtin}
                    placeholder="# Skill Title&#10;&#10;## Overview&#10;..."
                  />
                </div>
                <div className="flex items-center gap-3">
                  <label className="text-xs font-semibold text-gray-600">Active</label>
                  <button
                    type="button"
                    onClick={() =>
                      !selectedSkill.is_builtin &&
                      setEditForm({ ...editForm, is_active: !editForm.is_active })
                    }
                    className={`relative inline-flex w-10 h-5 rounded-full transition-colors ${
                      editForm.is_active ? "bg-green-500" : "bg-gray-300"
                    } ${selectedSkill.is_builtin ? "cursor-not-allowed opacity-60" : "cursor-pointer"}`}
                  >
                    <span
                      className={`inline-block w-4 h-4 bg-white rounded-full shadow transition-transform mt-0.5 ${
                        editForm.is_active ? "translate-x-5" : "translate-x-0.5"
                      }`}
                    />
                  </button>
                </div>

                {!selectedSkill.is_builtin && (
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

            {panelTab === "preview" && (
              <div>
                <div
                  className="prose prose-sm max-w-none text-gray-800"
                  dangerouslySetInnerHTML={{
                    __html: simpleMarkdown(editForm.content_markdown || selectedSkill.content_markdown),
                  }}
                />
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
              <h2 className="font-bold text-gray-900">Thêm Skill Mới</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1">Tên Skill *</label>
                  <input
                    className="input-field"
                    value={createForm.name}
                    onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1">Version</label>
                  <input
                    className="input-field"
                    value={createForm.version}
                    onChange={(e) => setCreateForm({ ...createForm, version: e.target.value })}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1">Danh mục</label>
                  <select
                    className="input-field"
                    value={createForm.category}
                    onChange={(e) => setCreateForm({ ...createForm, category: e.target.value })}
                  >
                    <option value="tax">Tax</option>
                    <option value="legal">Legal</option>
                    <option value="advisory">Advisory</option>
                    <option value="compliance">Compliance</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1">Tags</label>
                  <input
                    className="input-field"
                    value={createForm.tags}
                    placeholder="tag1, tag2, ..."
                    onChange={(e) => setCreateForm({ ...createForm, tags: e.target.value })}
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Mô tả</label>
                <textarea
                  className="input-field"
                  rows={2}
                  value={createForm.description}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-2">Applicable Bots</label>
                <div className="flex gap-3 flex-wrap">
                  {["partner", "ja", "sa", "intake"].map((bot) => (
                    <label key={bot} className="flex items-center gap-1.5 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={(createForm.applicable_bots || []).includes(bot)}
                        onChange={() => toggleBot(createForm, setCreateForm, bot)}
                        className="rounded"
                      />
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${BOT_COLORS[bot]}`}>
                        {bot}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Nội dung Markdown</label>
                <textarea
                  className="input-field font-mono text-xs"
                  style={{ minHeight: 300 }}
                  value={createForm.content_markdown}
                  onChange={(e) => setCreateForm({ ...createForm, content_markdown: e.target.value })}
                  placeholder="# Skill Title&#10;&#10;## Overview&#10;..."
                />
              </div>
              <div className="flex items-center gap-3">
                <label className="text-xs font-semibold text-gray-600">Active</label>
                <button
                  type="button"
                  onClick={() => setCreateForm({ ...createForm, is_active: !createForm.is_active })}
                  className={`relative inline-flex w-10 h-5 rounded-full transition-colors cursor-pointer ${
                    createForm.is_active ? "bg-green-500" : "bg-gray-300"
                  }`}
                >
                  <span
                    className={`inline-block w-4 h-4 bg-white rounded-full shadow transition-transform mt-0.5 ${
                      createForm.is_active ? "translate-x-5" : "translate-x-0.5"
                    }`}
                  />
                </button>
              </div>
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
                  "Tạo Skill"
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
