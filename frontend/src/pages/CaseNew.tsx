import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Send } from "lucide-react";
import { casesApi, workflowsApi, WorkflowDefinition } from "../lib/cases";
import toast from "react-hot-toast";

const PRIMARY = "#028a39";

export default function CaseNew() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [workflows, setWorkflows] = useState<WorkflowDefinition[]>([]);

  const [form, setForm] = useState({
    title: "",
    client_request: "",
    practice_area: "tax",
    output_language: "vi",
    priority: "normal",
    workflow_definition_id: "",
    use_legacy_pipeline: true,
  });

  useEffect(() => {
    workflowsApi.list()
      .then((res) => {
        const data = res.data;
        setWorkflows(Array.isArray(data) ? data : (data.items ?? []));
      })
      .catch(() => {});
  }, []);

  const set = (field: string, value: string | boolean) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim()) { toast.error("Vui lòng nhập tiêu đề"); return; }
    if (!form.client_request.trim()) { toast.error("Vui lòng nhập nội dung yêu cầu"); return; }

    setSubmitting(true);
    try {
      const payload: Record<string, unknown> = {
        title: form.title.trim(),
        client_request: form.client_request.trim(),
        practice_area: form.practice_area,
        output_language: form.output_language,
        priority: form.priority,
        use_legacy_pipeline: form.use_legacy_pipeline,
      };
      if (form.workflow_definition_id) {
        payload.workflow_definition_id = form.workflow_definition_id;
      }

      const res = await casesApi.create(payload as any);
      toast.success("Case đã được tạo!");
      navigate(`/cases/${res.data.id}`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Không thể tạo case");
    } finally {
      setSubmitting(false);
    }
  };

  const inputCls =
    "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:border-transparent bg-white";
  const focusStyle = { "--tw-ring-color": PRIMARY } as React.CSSProperties;

  return (
    <div className="max-w-2xl space-y-5">
      {/* Back */}
      <button
        onClick={() => navigate("/cases")}
        className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Quay lại Cases
      </button>

      <div>
        <h1 className="text-xl font-bold text-gray-900">Tạo Case Mới</h1>
        <p className="text-sm text-gray-500 mt-0.5">Điền thông tin để bắt đầu quy trình tư vấn</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-5">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Tiêu đề <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            className={inputCls}
            style={focusStyle}
            placeholder="VD: Tư vấn thuế TNDN năm 2024 cho Công ty ABC"
            value={form.title}
            onChange={(e) => set("title", e.target.value)}
            required
          />
        </div>

        {/* Client request */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Nội dung yêu cầu <span className="text-red-500">*</span>
          </label>
          <textarea
            className={`${inputCls} resize-none`}
            style={focusStyle}
            rows={5}
            placeholder="Mô tả chi tiết vấn đề pháp lý / thuế cần tư vấn..."
            value={form.client_request}
            onChange={(e) => set("client_request", e.target.value)}
            required
          />
        </div>

        {/* Row: practice_area + output_language */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Lĩnh vực</label>
            <select
              className={inputCls}
              value={form.practice_area}
              onChange={(e) => set("practice_area", e.target.value)}
            >
              <option value="tax">Thuế</option>
              <option value="legal">Pháp lý</option>
              <option value="both">Thuế &amp; Pháp lý</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Ngôn ngữ đầu ra</label>
            <select
              className={inputCls}
              value={form.output_language}
              onChange={(e) => set("output_language", e.target.value)}
            >
              <option value="vi">Tiếng Việt (VI)</option>
              <option value="en">English (EN)</option>
            </select>
          </div>
        </div>

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Độ ưu tiên</label>
          <select
            className={inputCls}
            value={form.priority}
            onChange={(e) => set("priority", e.target.value)}
          >
            <option value="low">Thấp</option>
            <option value="normal">Bình thường</option>
            <option value="high">Cao</option>
            <option value="urgent">Khẩn cấp</option>
          </select>
        </div>

        {/* Workflow selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Workflow (tùy chọn)
          </label>
          <select
            className={inputCls}
            value={form.workflow_definition_id}
            onChange={(e) => set("workflow_definition_id", e.target.value)}
          >
            <option value="">— Sử dụng mặc định —</option>
            {workflows.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name} {w.is_default ? "(mặc định)" : ""}
              </option>
            ))}
          </select>
        </div>

        {/* Legacy pipeline toggle */}
        <div className="flex items-center justify-between py-2 border-t border-gray-100">
          <div>
            <p className="text-sm font-medium text-gray-700">Dùng pipeline cũ</p>
            <p className="text-xs text-gray-400 mt-0.5">Bật để chạy quy trình LangGraph truyền thống</p>
          </div>
          <button
            type="button"
            onClick={() => set("use_legacy_pipeline", !form.use_legacy_pipeline)}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none ${
              form.use_legacy_pipeline ? "" : "bg-gray-200"
            }`}
            style={form.use_legacy_pipeline ? { background: PRIMARY } : {}}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
                form.use_legacy_pipeline ? "translate-x-4" : "translate-x-0.5"
              }`}
            />
          </button>
        </div>

        {/* Submit */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={() => navigate("/cases")}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Hủy
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="flex items-center gap-2 px-5 py-2 text-white text-sm font-medium rounded-lg transition-opacity disabled:opacity-60"
            style={{ background: PRIMARY }}
          >
            {submitting ? (
              <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            {submitting ? "Đang tạo..." : "Tạo Case"}
          </button>
        </div>
      </form>
    </div>
  );
}
