import { useEffect, useState } from "react";
import { adminApi } from "../lib/api";
import { Settings, Save, AlertCircle, ChevronDown } from "lucide-react";
import toast from "react-hot-toast";

const AGENT_LABELS: Record<string, { label: string; desc: string; color: string }> = {
  intake: { label: "Intake Enhancer", desc: "Xác minh sự kiện & luật áp dụng", color: "bg-purple-100 text-purple-700" },
  partner: { label: "Partner Bot", desc: "Brief + Duyệt chiến lược + Finalize", color: "bg-blue-100 text-blue-700" },
  sa: { label: "SA Bot", desc: "Blueprint + Adversarial Review", color: "bg-orange-100 text-orange-700" },
  ja: { label: "JA Bot", desc: "Nghiên cứu sâu + Soạn thảo", color: "bg-green-100 text-green-700" },
};

export default function Admin() {
  const [stats, setStats] = useState<any>(null);
  const [settings, setSettings] = useState<any[]>([]);
  const [availableModels, setAvailableModels] = useState<any[]>([]);
  const [saving, setSaving] = useState<string | null>(null);
  const [editValues, setEditValues] = useState<Record<string, any>>({});

  useEffect(() => {
    adminApi.stats().then((r) => setStats(r.data)).catch(() => {});
    adminApi.getAgentSettings().then((r) => {
      setSettings(r.data.settings);
      setAvailableModels(r.data.available_models);
      const vals: Record<string, any> = {};
      r.data.settings.forEach((s: any) => {
        vals[s.agent_key] = {
          model_id: s.model_id,
          provider: s.provider,
          temperature: s.temperature,
          max_tokens: s.max_tokens,
          system_prompt_override: s.system_prompt_override || "",
        };
      });
      setEditValues(vals);
    }).catch(() => {});
  }, []);

  const handleSave = async (agentKey: string) => {
    setSaving(agentKey);
    try {
      const vals = editValues[agentKey];
      // Auto-detect provider from model
      const model = availableModels.find((m: any) => m.id === vals.model_id);
      const provider = model?.provider || vals.provider;
      await adminApi.updateAgentSetting(agentKey, { ...vals, provider });
      toast.success(`Đã lưu cài đặt ${AGENT_LABELS[agentKey]?.label}`);
    } catch {
      toast.error("Lưu thất bại");
    } finally {
      setSaving(null);
    }
  };

  const setVal = (agentKey: string, field: string, value: any) => {
    setEditValues((prev) => ({
      ...prev,
      [agentKey]: { ...prev[agentKey], [field]: value },
    }));
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Settings className="w-6 h-6 text-primary-500" /> Admin Dashboard
        </h1>
        <p className="text-gray-500 text-sm mt-1">Quản lý hệ thống TaxLegal AI</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[
            { label: "Users", value: stats.users },
            { label: "Matters", value: stats.matters },
            { label: "Hoàn thành", value: stats.completed },
            { label: "Điểm TB", value: stats.avg_quality_score ? `${stats.avg_quality_score}/100` : "—" },
          ].map(({ label, value }) => (
            <div key={label} className="card p-4 text-center">
              <p className="text-2xl font-bold text-gray-900">{value}</p>
              <p className="text-xs text-gray-500 mt-1">{label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Agent Settings */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Cài đặt AI Agents</h2>
        <div className="space-y-4">
          {Object.entries(AGENT_LABELS).map(([key, meta]) => {
            const vals = editValues[key] || {};
            return (
              <div key={key} className="card">
                <div className="flex items-center gap-3 mb-4">
                  <span className={`badge ${meta.color}`}>{key.toUpperCase()}</span>
                  <div>
                    <p className="text-sm font-semibold text-gray-900">{meta.label}</p>
                    <p className="text-xs text-gray-500">{meta.desc}</p>
                  </div>
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Model</label>
                    <select
                      className="input-field text-sm"
                      value={vals.model_id || ""}
                      onChange={(e) => setVal(key, "model_id", e.target.value)}
                    >
                      <option value="">-- Chọn model --</option>
                      {availableModels.map((m: any) => (
                        <option key={m.id} value={m.id}>
                          [{m.provider.toUpperCase()}] {m.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      Temperature ({vals.temperature || 0.3})
                    </label>
                    <input
                      type="range" min="0" max="1" step="0.05"
                      className="w-full accent-primary-500"
                      value={vals.temperature || 0.3}
                      onChange={(e) => setVal(key, "temperature", parseFloat(e.target.value))}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Max Tokens</label>
                    <input
                      type="number" min="1000" max="32000" step="1000"
                      className="input-field text-sm"
                      value={vals.max_tokens || 8000}
                      onChange={(e) => setVal(key, "max_tokens", parseInt(e.target.value))}
                    />
                  </div>
                </div>

                <div className="mt-3">
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    System Prompt Override (để trống = dùng mặc định)
                  </label>
                  <textarea
                    className="input-field text-xs font-mono min-h-16"
                    placeholder="Không điền sẽ sử dụng prompt mặc định của hệ thống..."
                    value={vals.system_prompt_override || ""}
                    onChange={(e) => setVal(key, "system_prompt_override", e.target.value)}
                  />
                </div>

                <div className="flex justify-end mt-3">
                  <button
                    onClick={() => handleSave(key)}
                    disabled={saving === key}
                    className="btn-primary text-sm flex items-center gap-1"
                  >
                    <Save className="w-3.5 h-3.5" />
                    {saving === key ? "Đang lưu..." : "Lưu"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Env check */}
      <div className="card">
        <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-yellow-500" /> API Keys Status
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
          {[
            { label: "Anthropic", models: availableModels.filter((m: any) => m.provider === "anthropic") },
            { label: "OpenAI", models: availableModels.filter((m: any) => m.provider === "openai") },
            { label: "DeepSeek", models: availableModels.filter((m: any) => m.provider === "deepseek") },
            { label: "OpenRouter", models: availableModels.filter((m: any) => m.provider === "openrouter") },
          ].map(({ label, models }) => (
            <div key={label} className={`p-2 rounded-lg border ${models.length > 0 ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"}`}>
              <p className={`font-semibold ${models.length > 0 ? "text-green-700" : "text-red-700"}`}>
                {models.length > 0 ? "✓" : "✗"} {label}
              </p>
              <p className={models.length > 0 ? "text-green-600" : "text-red-600"}>
                {models.length > 0 ? `${models.length} models` : "No API key"}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
