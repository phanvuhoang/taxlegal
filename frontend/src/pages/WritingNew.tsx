/**
 * New Writing Job page (/writing/new)
 */
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { writingApi, CONTENT_TYPES } from "../lib/writing";
import { skillsApi, botVariantsApi } from "../lib/api";
import {
  PenTool, ArrowLeft, ChevronDown, Loader2,
  Languages, Bot, Target, FileText
} from "lucide-react";
import toast from "react-hot-toast";

interface Skill { id: number; name: string; description: string; category: string; }
interface BotVariant { id: number; name: string; slug: string; role: string; description: string; }

export default function WritingNew() {
  const navigate = useNavigate();
  const [skills, setSkills] = useState<Skill[]>([]);
  const [bots, setBots] = useState<BotVariant[]>([]);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    title: "",
    content_type: "analysis",
    topic: "",
    context: "",
    output_language: "vi",
    bot_variant_id: null as number | null,
    skill_ids: [] as number[],
    word_count_target: 2000,
  });

  useEffect(() => {
    skillsApi.list().then((r) => setSkills(r.data)).catch(() => {});
    botVariantsApi.list().then((r) => setBots(r.data)).catch(() => {});
  }, []);

  const toggleSkill = (id: number) => {
    setForm((prev) => ({
      ...prev,
      skill_ids: prev.skill_ids.includes(id)
        ? prev.skill_ids.filter((s) => s !== id)
        : [...prev.skill_ids, id],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim()) { toast.error("Vui lòng nhập tiêu đề"); return; }
    if (!form.topic.trim()) { toast.error("Vui lòng nhập chủ đề"); return; }
    setLoading(true);
    try {
      const res = await writingApi.create({
        ...form,
        bot_variant_id: form.bot_variant_id || undefined,
      });
      toast.success("Đã tạo bài viết");
      navigate(`/writing/${res.data.id}`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Không thể tạo bài viết");
    } finally {
      setLoading(false);
    }
  };

  const jaRoleBots = bots.filter((b) => b.role === "ja");
  const taxSkills = skills.filter((s) => s.category === "tax");

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate("/writing")}
          className="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: "#028a39" }}>
            <PenTool className="w-4 h-4 text-white" />
          </div>
          <h1 className="text-lg font-bold text-gray-900">Bài viết mới</h1>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Title */}
        <div className="bg-white rounded-xl border border-gray-100 p-5 space-y-4">
          <h2 className="font-semibold text-gray-800 flex items-center gap-2">
            <FileText className="w-4 h-4" style={{ color: "#028a39" }} />
            Thông tin bài viết
          </h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tiêu đề bài viết <span className="text-red-500">*</span>
            </label>
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="VD: Phân tích thuế nhà thầu nước ngoài theo Thông tư 103/2014"
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2"
              style={{ "--tw-ring-color": "#028a39" } as any}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Loại bài viết</label>
              <div className="relative">
                <select
                  value={form.content_type}
                  onChange={(e) => setForm({ ...form, content_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm appearance-none focus:outline-none focus:ring-2"
                  style={{ "--tw-ring-color": "#028a39" } as any}
                >
                  {CONTENT_TYPES.map((ct) => (
                    <option key={ct.value} value={ct.value}>{ct.label}</option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-2.5 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Languages className="w-4 h-4 inline mr-1" />
                Ngôn ngữ đầu ra
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
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Chủ đề / Câu hỏi cần phân tích <span className="text-red-500">*</span>
            </label>
            <textarea
              value={form.topic}
              onChange={(e) => setForm({ ...form, topic: e.target.value })}
              rows={3}
              placeholder={
                form.output_language === "vi"
                  ? "VD: Công ty Việt Nam thuê phần mềm SaaS từ công ty Mỹ. Phân tích nghĩa vụ FCT, VAT và CIT theo Thông tư 103/2014. Có DTA Việt-Mỹ không? Cách áp dụng?"
                  : "E.g.: A Vietnamese company licenses SaaS from a US company. Analyze FCT, VAT and CIT obligations under Circular 103/2014. Does the Vietnam-US DTA apply?"
              }
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 resize-none"
              style={{ "--tw-ring-color": "#028a39" } as any}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Thông tin bổ sung / Bối cảnh
            </label>
            <textarea
              value={form.context}
              onChange={(e) => setForm({ ...form, context: e.target.value })}
              rows={2}
              placeholder="Hợp đồng, ngành nghề, quy mô, năm tài chính, các đặc điểm cụ thể..."
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 resize-none"
              style={{ "--tw-ring-color": "#028a39" } as any}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Độ dài mục tiêu (từ)
            </label>
            <div className="flex gap-2">
              {[1000, 2000, 3000, 5000].map((wc) => (
                <button
                  key={wc}
                  type="button"
                  onClick={() => setForm({ ...form, word_count_target: wc })}
                  className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
                    form.word_count_target === wc
                      ? "border-green-600 text-green-700 bg-green-50 font-medium"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {wc.toLocaleString()}
                </button>
              ))}
              <input
                type="number"
                value={form.word_count_target}
                onChange={(e) => setForm({ ...form, word_count_target: parseInt(e.target.value) || 2000 })}
                min={500}
                max={10000}
                className="w-20 px-2 py-1.5 border border-gray-200 rounded-lg text-sm text-center"
              />
            </div>
          </div>
        </div>

        {/* Bot Picker */}
        <div className="bg-white rounded-xl border border-gray-100 p-5 space-y-3">
          <h2 className="font-semibold text-gray-800 flex items-center gap-2">
            <Bot className="w-4 h-4" style={{ color: "#028a39" }} />
            Bot viết bài
            <span className="text-xs text-gray-400 font-normal ml-1">(tùy chọn)</span>
          </h2>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setForm({ ...form, bot_variant_id: null })}
              className={`p-3 rounded-lg border text-left transition-colors ${
                form.bot_variant_id === null
                  ? "border-green-600 bg-green-50"
                  : "border-gray-200 hover:bg-gray-50"
              }`}
            >
              <p className="text-sm font-medium text-gray-800">Mặc định (JA)</p>
              <p className="text-xs text-gray-400">Dùng JA model từ cài đặt</p>
            </button>
            {jaRoleBots.map((bot) => (
              <button
                key={bot.id}
                type="button"
                onClick={() => setForm({ ...form, bot_variant_id: bot.id })}
                className={`p-3 rounded-lg border text-left transition-colors ${
                  form.bot_variant_id === bot.id
                    ? "border-green-600 bg-green-50"
                    : "border-gray-200 hover:bg-gray-50"
                }`}
              >
                <p className="text-sm font-medium text-gray-800 truncate">{bot.name}</p>
                <p className="text-xs text-gray-400 truncate">{bot.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Skills Picker */}
        <div className="bg-white rounded-xl border border-gray-100 p-5 space-y-3">
          <h2 className="font-semibold text-gray-800 flex items-center gap-2">
            <Target className="w-4 h-4" style={{ color: "#028a39" }} />
            Skills kích hoạt
            <span className="text-xs text-gray-400 font-normal ml-1">(tùy chọn — inject vào system prompt)</span>
          </h2>
          {taxSkills.length === 0 ? (
            <p className="text-sm text-gray-400">Không có skills khả dụng</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {taxSkills.map((skill) => (
                <button
                  key={skill.id}
                  type="button"
                  onClick={() => toggleSkill(skill.id)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                    form.skill_ids.includes(skill.id)
                      ? "border-green-600 bg-green-50 text-green-700"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {form.skill_ids.includes(skill.id) ? "✓ " : ""}{skill.name}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Submit */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => navigate("/writing")}
            className="px-4 py-2 rounded-lg border border-gray-200 text-gray-600 text-sm hover:bg-gray-50"
          >
            Hủy
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-white text-sm font-medium disabled:opacity-60"
            style={{ background: "#028a39" }}
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <PenTool className="w-4 h-4" />}
            {loading ? "Đang tạo..." : "Tạo bài viết"}
          </button>
        </div>
      </form>
    </div>
  );
}
