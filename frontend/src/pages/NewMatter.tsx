import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { mattersApi, pipelineTemplatesApi } from "../lib/api";
import ModelPicker from "../components/ModelPicker";
import { ArrowLeft, Zap, Languages } from "lucide-react";
import toast from "react-hot-toast";

interface PipelineTemplate {
  id: number;
  name: string;
  slug: string;
  description: string;
  practice_area: string;
  is_active: boolean;
  is_default: boolean;
}

export default function NewMatter() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<PipelineTemplate[]>([]);
  const [form, setForm] = useState({
    title: "",
    client_request: "",
    practice_area: "tax",
    pipeline_mode: "manual",
    output_language: "vi",
    model_override: "",
    pipeline_template_id: null as number | null,
  });

  useEffect(() => {
    pipelineTemplatesApi
      .listPublic()
      .then((r) => {
        const active: PipelineTemplate[] = (r.data || []).filter((t: PipelineTemplate) => t.is_active);
        setTemplates(active);
        const defaultTemplate = active.find((t) => t.is_default);
        if (defaultTemplate) {
          setForm((prev) => ({ ...prev, pipeline_template_id: defaultTemplate.id }));
        }
      })
      .catch(() => {
        // Templates are optional — fail silently
      });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim() || !form.client_request.trim()) {
      toast.error("Vui lòng điền đầy đủ tiêu đề và yêu cầu");
      return;
    }
    setLoading(true);
    try {
      const payload: Record<string, any> = {
        title: form.title,
        client_request: form.client_request,
        practice_area: form.practice_area,
        pipeline_mode: form.pipeline_mode,
      };
      payload.output_language = form.output_language;
      if (form.model_override) payload.model_override = form.model_override;
      if (form.pipeline_template_id) payload.pipeline_template_id = form.pipeline_template_id;

      const res = await mattersApi.create(payload);
      toast.success("Matter đã tạo! Intake Enhancer đang phân tích...");
      navigate(`/matters/${res.data.id}`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Tạo matter thất bại");
      setLoading(false);
    }
  };

  const EXAMPLE = `Tôi là công ty Việt Nam, hàng tháng trả chi phí subscription cho Claude Code ($200/tháng) cho Anthropic là công ty cung cấp dịch vụ AI qua nền tảng số ở nước ngoài và khoảng $1000 để sử dụng API của Anthropic.

Câu hỏi:
1. Khoản chi này chịu thuế như thế nào ở Việt Nam (thuế TNDN, thuế GTGT và các thuế khác)?
2. Công ty tôi có cần khai báo thuế gì không?
3. Chi phí này có được trừ cho mục đích thuế TNDN không, cần những chứng từ gì?`;

  const selectedTemplate = templates.find((t) => t.id === form.pipeline_template_id);

  return (
    <div className="max-w-3xl">
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={() => navigate(-1)}
          className="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Tạo Matter Mới</h1>
          <p className="text-sm text-gray-500">Gửi yêu cầu tư vấn để AI pipeline xử lý</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Title */}
        <div className="card">
          <label className="block text-sm font-semibold text-gray-900 mb-2">
            Tiêu đề Matter <span className="text-red-500">*</span>
          </label>
          <input
            className="input-field"
            placeholder="VD: Thuế nhà thầu — Anthropic Claude API"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            required
          />
        </div>

        {/* Client request */}
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-semibold text-gray-900">
              Yêu cầu của Khách hàng <span className="text-red-500">*</span>
            </label>
            <button
              type="button"
              onClick={() => setForm({ ...form, client_request: EXAMPLE, title: form.title || "Thuế nhà thầu — Dịch vụ AI nước ngoài" })}
              className="text-xs text-primary-600 hover:text-primary-700 font-medium"
            >
              Dùng ví dụ mẫu
            </button>
          </div>
          <textarea
            className="input-field min-h-48 font-mono text-sm"
            placeholder="Mô tả chi tiết yêu cầu tư vấn, bao gồm:
• Thông tin cụ thể về tình huống
• Các câu hỏi cụ thể cần được tư vấn
• Thông tin về công ty, ngành nghề..."
            value={form.client_request}
            onChange={(e) => setForm({ ...form, client_request: e.target.value })}
            required
          />
          <p className="text-xs text-gray-400 mt-1">
            {form.client_request.length} ký tự
          </p>
        </div>

        {/* Settings */}
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Cấu hình Pipeline</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Lĩnh vực</label>
              <select
                className="input-field"
                value={form.practice_area}
                onChange={(e) => setForm({ ...form, practice_area: e.target.value })}
              >
                <option value="tax">Thuế (Tax)</option>
                <option value="legal">Pháp luật (Legal)</option>
                <option value="both">Thuế & Pháp luật</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Chế độ Pipeline</label>
              <select
                className="input-field"
                value={form.pipeline_mode}
                onChange={(e) => setForm({ ...form, pipeline_mode: e.target.value })}
              >
                <option value="manual">Manual — Duyệt từng bước</option>
                <option value="auto">Auto — Chạy tự động</option>
              </select>
            </div>
          </div>

          {/* Pipeline Template selector */}
          {templates.length > 0 && (
            <div className="mt-4">
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Pipeline Template
              </label>
              <select
                className="input-field"
                value={form.pipeline_template_id ?? ""}
                onChange={(e) =>
                  setForm({
                    ...form,
                    pipeline_template_id: e.target.value ? Number(e.target.value) : null,
                  })
                }
              >
                <option value="">— Không dùng template —</option>
                {templates.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}{t.is_default ? " ★" : ""} [{t.practice_area}]
                  </option>
                ))}
              </select>
              {selectedTemplate && (
                <p className="text-xs text-gray-500 mt-1 ml-1">
                  {selectedTemplate.description}
                </p>
              )}
            </div>
          )}

          <div className="mt-4 p-3 rounded-lg bg-gray-50 border border-gray-100">
            {form.pipeline_mode === "manual" ? (
              <p className="text-xs text-gray-600">
                <strong>Manual Mode:</strong> Sau mỗi bước, bạn sẽ xem kết quả và nhấn "Tiếp tục" để chạy bước tiếp theo. Kiểm soát hoàn toàn.
              </p>
            ) : (
              <p className="text-xs text-gray-600">
                <Zap className="w-3 h-3 inline mr-1 text-yellow-500" />
                <strong>Auto Mode:</strong> Pipeline chạy tự động qua tất cả 7 bước. Nhanh hơn nhưng ít kiểm soát hơn.
              </p>
            )}
          </div>

          {/* Output language toggle */}
          <div className="mt-4">
            <label className="block text-xs font-medium text-gray-600 mb-2">
              <Languages className="w-3 h-3 inline mr-1" />
              Ngôn ngữ kết quả tư vấn
            </label>
            <div className="flex gap-2">
              {[
                { value: "vi", label: "🇻🇳 Tiếng Việt" },
                { value: "en", label: "🇺🇸 English" },
              ].map((lang) => (
                <button
                  key={lang.value}
                  type="button"
                  onClick={() => setForm({ ...form, output_language: lang.value })}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium border transition-colors ${
                    form.output_language === lang.value
                      ? "border-green-600 text-green-700 bg-green-50"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {lang.label}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-4">
            <ModelPicker
              value={form.model_override}
              onChange={(v) => setForm({ ...form, model_override: v })}
              label="Model override (tùy chọn — mặc định theo Admin settings)"
            />
          </div>
        </div>

        {/* Pipeline overview */}
        <div className="card bg-primary-50 border-primary-100">
          <p className="text-xs font-semibold text-primary-700 mb-2">Pipeline sẽ chạy qua 7 bước:</p>
          <div className="grid grid-cols-1 gap-1">
            {[
              "1. Intake Enhancer — Xác minh sự kiện & luật áp dụng",
              "2. Partner P1 — Lập brief & phân công",
              "3. SA Blueprint — Thiết kế cấu trúc tài liệu",
              "4. JA Research — Nghiên cứu sâu, soạn thảo từng phần",
              "5. SA Adversarial Review — Kiểm tra đối kháng",
              "6. Partner P2 — Duyệt chiến lược & chain audit",
              "7. Partner P3 — Hoàn thiện văn bản cuối",
            ].map((s) => (
              <p key={s} className="text-xs text-primary-700">{s}</p>
            ))}
          </div>
        </div>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="btn-secondary flex-1"
          >
            Huỷ
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex-2 flex items-center justify-center gap-2 flex-1"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Đang tạo...
              </>
            ) : (
              "Tạo Matter & Bắt đầu Pipeline →"
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
