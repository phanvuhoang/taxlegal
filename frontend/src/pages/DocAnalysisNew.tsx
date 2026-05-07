/**
 * New Document Analysis job (/doc-analysis/new)
 */
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Upload, Search, Loader2, X, Plus, Languages } from "lucide-react";
import api from "../lib/api";
import toast from "react-hot-toast";

interface LawDoc { id: number; title: string; doc_number: string | null; doc_type: string; is_priority: boolean; }
interface BotVariant { id: number; name: string; role: string; description: string; }

const ACTIONS = [
  { slug: "review", label: "Rà soát văn bản", desc: "Kiểm tra tính đầy đủ, hợp lệ, hình thức" },
  { slug: "applicable_regulations", label: "Tư vấn quy định áp dụng", desc: "Xác định các quy định pháp luật liên quan" },
  { slug: "legal_risk", label: "Tư vấn rủi ro pháp luật", desc: "Phân tích rủi ro pháp lý tiềm ẩn" },
  { slug: "tax_risk", label: "Tư vấn rủi ro thuế", desc: "Phân tích nghĩa vụ và rủi ro thuế" },
  { slug: "draft", label: "Soạn thảo/Chỉnh sửa văn bản", desc: "Đề xuất cải tiến, soạn thảo bổ sung" },
];

export default function DocAnalysisNew() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Step 1: Document
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [pastedText, setPastedText] = useState("");
  const [useFile, setUseFile] = useState(true);

  // Step 2: Regulations
  const [regSearch, setRegSearch] = useState("");
  const [regResults, setRegResults] = useState<LawDoc[]>([]);
  const [selectedRegs, setSelectedRegs] = useState<LawDoc[]>([]);
  const [regSearching, setRegSearching] = useState(false);

  // Step 3: Actions
  const [selectedActions, setSelectedActions] = useState<{slug: string; custom_prompt: string}[]>([]);
  const [customAction, setCustomAction] = useState("");

  // Step 4: Options
  const [outputLang, setOutputLang] = useState("vi");
  const [bots, setBots] = useState<BotVariant[]>([]);
  const [selectedBot, setSelectedBot] = useState<number | null>(null);

  useEffect(() => {
    api.get("/api/bot-variants").then((r) => setBots(r.data)).catch(() => {});
  }, []);

  const searchRegs = async () => {
    if (!regSearch.trim()) return;
    setRegSearching(true);
    try {
      const res = await api.get(`/api/law-documents/search?q=${encodeURIComponent(regSearch)}&limit=10`);
      setRegResults(res.data);
    } catch { toast.error("Lỗi tìm kiếm"); }
    finally { setRegSearching(false); }
  };

  const toggleAction = (slug: string) => {
    setSelectedActions((prev) =>
      prev.find((a) => a.slug === slug)
        ? prev.filter((a) => a.slug !== slug)
        : [...prev, { slug, custom_prompt: "" }]
    );
  };

  const updateCustomPrompt = (slug: string, prompt: string) => {
    setSelectedActions((prev) =>
      prev.map((a) => a.slug === slug ? { ...a, custom_prompt: prompt } : a)
    );
  };

  const handleSubmit = async () => {
    if (!title.trim()) { toast.error("Nhập tiêu đề"); return; }
    if (!file && !pastedText.trim()) { toast.error("Upload hoặc paste văn bản"); return; }
    if (selectedActions.length === 0) { toast.error("Chọn ít nhất 1 action"); return; }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("title", title);
      formData.append("output_language", outputLang);
      formData.append("actions", JSON.stringify(selectedActions));
      formData.append("regulation_ids", JSON.stringify(selectedRegs.map((r) => r.id)));
      if (selectedBot) formData.append("bot_variant_id", String(selectedBot));
      if (useFile && file) {
        formData.append("file", file);
      } else {
        // Create text file from pasted content
        const blob = new Blob([pastedText], { type: "text/plain" });
        formData.append("file", blob, "pasted-document.txt");
      }

      const res = await api.post("/api/doc-analysis", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      toast.success("Đã tạo job phân tích");
      navigate(`/doc-analysis/${res.data.id}`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Lỗi khi tạo");
    } finally { setLoading(false); }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-5">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate("/doc-analysis")} className="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <h1 className="text-lg font-bold text-gray-900">Phân tích văn bản mới</h1>
      </div>

      {/* Step indicators */}
      <div className="flex items-center gap-2">
        {[1,2,3,4].map((s) => (
          <div key={s} className={`flex items-center gap-2 ${s < 4 ? "flex-1" : ""}`}>
            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
              step >= s ? "text-white" : "bg-gray-200 text-gray-500"
            }`} style={step >= s ? { background: "#028a39" } : {}}>
              {s}
            </div>
            <span className={`text-xs ${step === s ? "font-medium text-gray-800" : "text-gray-400"} hidden sm:inline`}>
              {["Văn bản", "Quy định", "Actions", "Tùy chọn"][s-1]}
            </span>
            {s < 4 && <div className={`flex-1 h-0.5 ${step > s ? "" : "bg-gray-200"}`} style={step > s ? { background: "#028a39" } : {}} />}
          </div>
        ))}
      </div>

      {/* Step 1: Document */}
      {step === 1 && (
        <div className="bg-white rounded-xl border border-gray-100 p-5 space-y-4">
          <h2 className="font-semibold text-gray-800">Bước 1: Tiêu đề &amp; Văn bản</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tiêu đề *</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)}
              placeholder="VD: Phân tích hợp đồng dịch vụ phần mềm với công ty nước ngoài"
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          </div>
          <div className="flex gap-2">
            {[true, false].map((isFile) => (
              <button key={String(isFile)} type="button" onClick={() => setUseFile(isFile)}
                className={`flex-1 py-2 rounded-lg text-sm border ${useFile === isFile ? "border-green-600 bg-green-50 text-green-700" : "border-gray-200 text-gray-600"}`}>
                {isFile ? "Upload file" : "Paste text"}
              </button>
            ))}
          </div>
          {useFile ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Upload file (PDF, DOCX, TXT)</label>
              <label className={`flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-colors ${file ? "border-green-400 bg-green-50" : "border-gray-300 hover:border-green-400"}`}>
                <Upload className={`w-8 h-8 mb-2 ${file ? "text-green-600" : "text-gray-400"}`} />
                <span className="text-sm text-gray-500">{file ? file.name : "Kéo thả hoặc click để chọn file"}</span>
                <input type="file" className="hidden" accept=".pdf,.docx,.doc,.txt"
                  onChange={(e) => setFile(e.target.files?.[0] || null)} />
              </label>
            </div>
          ) : (
            <textarea value={pastedText} onChange={(e) => setPastedText(e.target.value)}
              rows={10} placeholder="Paste nội dung văn bản vào đây..."
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono resize-y" />
          )}
          <button onClick={() => setStep(2)} disabled={!title.trim() || (useFile ? !file : !pastedText.trim())}
            className="w-full py-2 rounded-lg text-white text-sm font-medium disabled:opacity-50"
            style={{ background: "#028a39" }}>Tiếp theo →</button>
        </div>
      )}

      {/* Step 2: Regulations */}
      {step === 2 && (
        <div className="bg-white rounded-xl border border-gray-100 p-5 space-y-4">
          <h2 className="font-semibold text-gray-800">Bước 2: Chọn quy định áp dụng</h2>
          <p className="text-xs text-gray-400">Chọn văn bản luật để AI ưu tiên trong phân tích. Nếu không chọn, AI sẽ tự tìm kiếm trong anchor docs và internet.</p>
          <div className="flex gap-2">
            <input value={regSearch} onChange={(e) => setRegSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && searchRegs()}
              placeholder="Tìm quy định (VD: Thông tư 103, FCT, chuyển giá...)"
              className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
            <button onClick={searchRegs} disabled={regSearching}
              className="px-3 py-2 rounded-lg text-white text-sm" style={{ background: "#028a39" }}>
              {regSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            </button>
          </div>
          {regResults.length > 0 && (
            <div className="border border-gray-200 rounded-lg divide-y max-h-48 overflow-y-auto">
              {regResults.map((doc) => (
                <button key={doc.id} onClick={() => {
                  if (!selectedRegs.find((r) => r.id === doc.id)) setSelectedRegs((prev) => [...prev, doc]);
                }} className="w-full text-left px-3 py-2 hover:bg-green-50 text-sm flex items-center justify-between">
                  <span className="truncate">{doc.title} <span className="text-gray-400 text-xs ml-1">({doc.doc_number})</span></span>
                  {doc.is_priority && <span className="text-xs text-amber-600 ml-2 shrink-0">⭐</span>}
                </button>
              ))}
            </div>
          )}
          {selectedRegs.length > 0 && (
            <div className="space-y-1">
              <p className="text-xs font-medium text-gray-600">Đã chọn ({selectedRegs.length}):</p>
              {selectedRegs.map((reg) => (
                <div key={reg.id} className="flex items-center justify-between bg-green-50 rounded-lg px-3 py-1.5 text-sm">
                  <span className="truncate text-green-800">{reg.title}</span>
                  <button onClick={() => setSelectedRegs((prev) => prev.filter((r) => r.id !== reg.id))}>
                    <X className="w-3.5 h-3.5 text-green-600 hover:text-red-500" />
                  </button>
                </div>
              ))}
            </div>
          )}
          <div className="flex gap-2">
            <button onClick={() => setStep(1)} className="px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-600">← Quay lại</button>
            <button onClick={() => setStep(3)} className="flex-1 py-2 rounded-lg text-white text-sm font-medium" style={{ background: "#028a39" }}>
              {selectedRegs.length === 0 ? "Bỏ qua →" : `Tiếp theo (${selectedRegs.length} quy định) →`}
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Actions */}
      {step === 3 && (
        <div className="bg-white rounded-xl border border-gray-100 p-5 space-y-4">
          <h2 className="font-semibold text-gray-800">Bước 3: Chọn actions phân tích</h2>
          <div className="space-y-2">
            {ACTIONS.map((action) => {
              const isSelected = !!selectedActions.find((a) => a.slug === action.slug);
              return (
                <div key={action.slug} className={`border rounded-xl p-3 transition-colors ${isSelected ? "border-green-500 bg-green-50" : "border-gray-200 hover:border-gray-300"}`}>
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input type="checkbox" checked={isSelected} onChange={() => toggleAction(action.slug)}
                      className="mt-0.5 rounded" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-800">{action.label}</p>
                      <p className="text-xs text-gray-400">{action.desc}</p>
                    </div>
                  </label>
                  {isSelected && (
                    <div className="mt-2 ml-6">
                      <input
                        value={selectedActions.find((a) => a.slug === action.slug)?.custom_prompt || ""}
                        onChange={(e) => updateCustomPrompt(action.slug, e.target.value)}
                        placeholder="Prompt bổ sung (tùy chọn)..."
                        className="w-full px-2 py-1.5 border border-green-300 rounded-lg text-xs bg-white" />
                    </div>
                  )}
                </div>
              );
            })}
            <div className="border border-dashed border-gray-300 rounded-xl p-3">
              <div className="flex gap-2">
                <input value={customAction} onChange={(e) => setCustomAction(e.target.value)}
                  placeholder="Thêm action tùy chỉnh..."
                  className="flex-1 px-2 py-1.5 border border-gray-200 rounded-lg text-sm" />
                <button onClick={() => {
                  if (customAction.trim()) {
                    setSelectedActions((prev) => [...prev, { slug: `custom_${Date.now()}`, custom_prompt: customAction }]);
                    setCustomAction("");
                  }
                }} className="px-3 py-1.5 rounded-lg text-white text-xs" style={{ background: "#028a39" }}>
                  <Plus className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setStep(2)} className="px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-600">← Quay lại</button>
            <button onClick={() => setStep(4)} disabled={selectedActions.length === 0}
              className="flex-1 py-2 rounded-lg text-white text-sm font-medium disabled:opacity-50" style={{ background: "#028a39" }}>
              Tiếp theo ({selectedActions.length} actions) →
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Options + Submit */}
      {step === 4 && (
        <div className="bg-white rounded-xl border border-gray-100 p-5 space-y-4">
          <h2 className="font-semibold text-gray-800">Bước 4: Tùy chọn &amp; Xác nhận</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Languages className="w-3.5 h-3.5 inline mr-1" /> Ngôn ngữ đầu ra
            </label>
            <div className="flex gap-2">
              {[{v:"vi",l:"🇻🇳 Tiếng Việt"},{v:"en",l:"🇺🇸 English"}].map(({v,l}) => (
                <button key={v} type="button" onClick={() => setOutputLang(v)}
                  className={`flex-1 py-2 rounded-lg text-sm border ${outputLang === v ? "border-green-600 bg-green-50 text-green-700 font-medium" : "border-gray-200 text-gray-600"}`}>{l}</button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Bot phân tích (tùy chọn)</label>
            <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
              <button type="button" onClick={() => setSelectedBot(null)}
                className={`p-2 rounded-lg border text-left text-xs ${!selectedBot ? "border-green-600 bg-green-50" : "border-gray-200 hover:bg-gray-50"}`}>
                <p className="font-medium">Mặc định</p><p className="text-gray-400">AI model chuẩn</p>
              </button>
              {bots.map((bot) => (
                <button key={bot.id} type="button" onClick={() => setSelectedBot(bot.id)}
                  className={`p-2 rounded-lg border text-left text-xs ${selectedBot === bot.id ? "border-green-600 bg-green-50" : "border-gray-200 hover:bg-gray-50"}`}>
                  <p className="font-medium truncate">{bot.name}</p>
                  <p className="text-gray-400 truncate">{bot.role}</p>
                </button>
              ))}
            </div>
          </div>
          {/* Summary */}
          <div className="bg-gray-50 rounded-lg p-3 text-xs text-gray-600 space-y-1">
            <p><strong>Văn bản:</strong> {useFile ? file?.name : "Văn bản paste"} </p>
            <p><strong>Quy định:</strong> {selectedRegs.length > 0 ? selectedRegs.map(r=>r.title).join(", ") : "Tự động tìm kiếm"}</p>
            <p><strong>Actions:</strong> {selectedActions.length} actions</p>
            <p><strong>Ngôn ngữ:</strong> {outputLang === "vi" ? "Tiếng Việt" : "English"}</p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setStep(3)} className="px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-600">← Quay lại</button>
            <button onClick={handleSubmit} disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-white text-sm font-medium disabled:opacity-60"
              style={{ background: "#028a39" }}>
              {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Đang tạo...</> : "Tạo & Phân tích"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
