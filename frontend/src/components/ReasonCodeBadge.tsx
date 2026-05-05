import { AlertTriangle, AlertCircle, Info } from "lucide-react";

const REASON_CODES: Record<string, string> = {
  R01: "Missing legal basis",
  R02: "Wrong article / fabricated reference",
  R05: "Cross-chunk contradiction",
  R09: "DEEP issue missing depth markers",
  R11: "Word count below floor",
  R12: "Completeness matrix gap",
  R13: "Duplicate content",
  R14: "Wrong reading order",
  R15: "Conditional advice without decision table",
  R16: "Cited superseded / repealed law",
  R17: "Re-flagged a VERIFIED fact",
  R18: "Outdated assertion (valid law, amended provision)",
};

const CRITICAL = ["R02", "R05", "R11", "R16", "R17", "R18"];
const MODERATE = ["R01", "R09", "R12", "R13", "R14", "R15"];

interface Props {
  code: string;
  detail?: string;
}

export default function ReasonCodeBadge({ code, detail }: Props) {
  const isCritical = CRITICAL.includes(code);
  const desc = REASON_CODES[code] || "Unknown issue";

  return (
    <div className={`flex items-start gap-2 text-xs p-2 rounded-lg ${
      isCritical ? "bg-red-50 text-red-700" : "bg-yellow-50 text-yellow-700"
    }`}>
      {isCritical
        ? <AlertCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
        : <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />}
      <div>
        <span className="font-bold">{code}</span>
        <span className="mx-1 text-gray-400">—</span>
        <span>{desc}</span>
        {detail && <p className="text-gray-500 mt-0.5">{detail}</p>}
      </div>
    </div>
  );
}
