import { CheckCircle, Circle, Clock, AlertCircle, PlayCircle, XCircle } from "lucide-react";

const STEPS = [
  { number: 1, name: "Intake Enhancer", agent: "INTAKE", desc: "Xác minh sự kiện & luật áp dụng" },
  { number: 2, name: "Partner P1", agent: "PARTNER", desc: "Lập brief & phân công" },
  { number: 3, name: "SA Blueprint", agent: "SA", desc: "Thiết kế cấu trúc tài liệu" },
  { number: 4, name: "JA Research", agent: "JA", desc: "Nghiên cứu sâu từng chunk" },
  { number: 5, name: "SA Review", agent: "SA", desc: "Adversarial review & spot-check" },
  { number: 6, name: "Partner P2", agent: "PARTNER", desc: "Duyệt chiến lược & chain audit" },
  { number: 7, name: "Partner P3", agent: "PARTNER", desc: "Hoàn thiện văn bản cuối" },
];

const agentColors: Record<string, string> = {
  INTAKE: "bg-purple-100 text-purple-700",
  PARTNER: "bg-blue-100 text-blue-700",
  SA: "bg-orange-100 text-orange-700",
  JA: "bg-green-100 text-green-700",
};

const statusIcon = (status: string) => {
  switch (status) {
    case "completed":
    case "approved":
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    case "running":
      return <PlayCircle className="w-5 h-5 text-blue-500 animate-pulse" />;
    case "waiting":
      return <Clock className="w-5 h-5 text-yellow-500" />;
    case "failed":
      return <XCircle className="w-5 h-5 text-red-500" />;
    default:
      return <Circle className="w-5 h-5 text-gray-300" />;
  }
};

interface StepData {
  step_number: number;
  status: string;
  model_used?: string;
  word_count?: number;
  duration_ms?: number;
  reason_codes_found?: Array<{ code: string; severity: string }>;
  output_markdown?: string;
  error_message?: string;
}

interface Props {
  steps: StepData[];
  currentStep: number;
  pipelineMode: string;
  onApprove?: (step: number) => void;
  onViewStep?: (step: StepData) => void;
  approving?: number | null;
}

export default function PipelineTracker({
  steps, currentStep, pipelineMode, onApprove, onViewStep, approving
}: Props) {
  const getStep = (n: number) => steps.find((s) => s.step_number === n);

  return (
    <div className="space-y-2">
      {STEPS.map((def, idx) => {
        const step = getStep(def.number);
        const status = step?.status || "pending";
        const isCurrent = def.number === currentStep;
        const criticals = step?.reason_codes_found?.filter((r) => r.severity === "CRITICAL") || [];

        return (
          <div key={def.number} className="relative">
            {/* Connector */}
            {idx > 0 && (
              <div className="absolute left-5 -top-2 h-2 w-0.5 bg-gray-200" />
            )}

            <div className={`flex items-start gap-3 p-3 rounded-lg border transition-colors ${
              isCurrent ? "border-primary-200 bg-primary-50" : "border-gray-100 bg-white hover:border-gray-200"
            }`}>
              {/* Status icon */}
              <div className="flex-shrink-0 mt-0.5">
                {statusIcon(status)}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-medium text-gray-900">{def.name}</span>
                  <span className={`badge text-xs px-1.5 py-0 ${agentColors[def.agent]}`}>{def.agent}</span>
                  {criticals.length > 0 && (
                    <span className="badge badge-red gap-1">
                      <AlertCircle className="w-3 h-3" />
                      {criticals.length} CRITICAL
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{def.desc}</p>
                {step && (
                  <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                    {step.model_used && <span>{step.model_used}</span>}
                    {step.word_count && <span>{step.word_count.toLocaleString()} từ</span>}
                    {step.duration_ms && <span>{(step.duration_ms / 1000).toFixed(1)}s</span>}
                  </div>
                )}
                {step?.error_message && (
                  <p className="text-xs text-red-600 mt-1 truncate">{step.error_message}</p>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 flex-shrink-0">
                {step?.output_markdown && (
                  <button
                    onClick={() => onViewStep?.(step)}
                    className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                  >
                    Xem
                  </button>
                )}
                {status === "waiting" && pipelineMode === "manual" && onApprove && (
                  <button
                    onClick={() => onApprove(def.number)}
                    disabled={approving === def.number}
                    className="btn-primary text-xs px-3 py-1"
                  >
                    {approving === def.number ? "Đang xử lý..." : "Tiếp tục →"}
                  </button>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
