import { useEffect, useState } from "react";
import { getModels } from "../lib/api";

interface Model { id: string; label: string; provider: string; }

interface Props {
  value: string;
  onChange: (v: string) => void;
  label?: string;
}

export default function ModelPicker({ value, onChange, label = "Model" }: Props) {
  const [models, setModels] = useState<Model[]>([]);

  useEffect(() => {
    getModels().then((r) => setModels(r.data.models)).catch(() => {});
  }, []);

  const providerColor: Record<string, string> = {
    anthropic: "text-orange-600",
    openai: "text-green-600",
    deepseek: "text-blue-600",
    openrouter: "text-purple-600",
  };

  return (
    <div>
      <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
      <select
        className="input-field text-sm"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">-- Default (từ Admin) --</option>
        {models.map((m) => (
          <option key={m.id} value={m.id}>
            [{m.provider.toUpperCase()}] {m.label}
          </option>
        ))}
      </select>
    </div>
  );
}
