import { useEffect, useState } from "react";
import { adminApi } from "../lib/api";
import { FlaskConical, Plus, Play, CheckCircle, XCircle } from "lucide-react";
import toast from "react-hot-toast";

export default function AdminAutotest() {
  const [cases, setCases] = useState<any[]>([]);
  const [runs, setRuns] = useState<any[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [running, setRunning] = useState<number | null>(null);
  const [form, setForm] = useState({
    name: "",
    description: "",
    client_request: "",
    practice_area: "tax",
    complexity: "standard",
    expected_topics: "",
  });

  const load = () => {
    adminApi.listTestCases().then((r) => setCases(r.data)).catch(() => {});
    adminApi.listTestRuns().then((r) => setRuns(r.data)).catch(() => {});
  };
  useEffect(() => { load(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await adminApi.createTestCase({
        ...form,
        expected_topics: form.expected_topics.split("\n").filter(Boolean),
        scoring_criteria: { structure: 20, legal_accuracy: 30, practicality: 25, completeness: 25 },
      });
      toast.success("Đã tạo test case");
      setShowAdd(false);
      load();
    } catch { toast.error("Lỗi"); }
  };

  const handleRun = async (id: number) => {
    setRunning(id);
    try {
      const r = await adminApi.runAutotest(id);
      toast.success(r.data.message);
      load();
    } catch { toast.error("Lỗi"); }
    finally { setRunning(null); }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <FlaskConical className="w-6 h-6 text-primary-500" /> AutoTest
          </h1>
          <p className="text-gray-500 text-sm mt-1">Tự động kiểm tra và cải tiến chất lượng pipeline</p>
        </div>
        <button onClick={() => setShowAdd(!showAdd)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Thêm Test Case
        </button>
      </div>

      {/* AutoTest principle */}
      <div className="card bg-blue-50 border-blue-100 mb-6">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">Nguyên lý AutoTest (EZLAW-AI)</h3>
        <div className="grid md:grid-cols-3 gap-3 text-xs text-blue-800">
          <div><strong>1. Define "tốt"</strong><br />Tiêu chí chấm điểm: cấu trúc, độ chính xác, thực tiễn, đầy đủ</div>
          <div><strong>2. Baseline Lock</strong><br />Điểm gốc bị khoá cứng. Chỉ giữ thay đổi nếu điểm tăng ≥0.01</div>
          <div><strong>3. Anti-inflation</strong><br />Không cho điểm cao hơn chỉ vì "trông hay" — phải chứng minh output tốt hơn thực sự</div>
        </div>
      </div>

      {showAdd && (
        <div className="card mb-4">
          <h3 className="font-semibold text-gray-900 mb-3">Thêm Test Case mới</h3>
          <form onSubmit={handleCreate} className="space-y-3">
            <input className="input-field" placeholder="Tên test case" value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            <input className="input-field" placeholder="Mô tả (tùy chọn)" value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })} />
            <textarea className="input-field min-h-24" placeholder="Yêu cầu khách hàng mô phỏng..." value={form.client_request}
              onChange={(e) => setForm({ ...form, client_request: e.target.value })} required />
            <div className="grid grid-cols-2 gap-3">
              <select className="input-field" value={form.practice_area}
                onChange={(e) => setForm({ ...form, practice_area: e.target.value })}>
                <option value="tax">Tax</option>
                <option value="legal">Legal</option>
              </select>
              <select className="input-field" value={form.complexity}
                onChange={(e) => setForm({ ...form, complexity: e.target.value })}>
                <option value="simple">Simple</option>
                <option value="standard">Standard</option>
                <option value="complex">Complex</option>
              </select>
            </div>
            <textarea className="input-field min-h-16" placeholder="Expected topics (mỗi dòng một topic)..."
              value={form.expected_topics} onChange={(e) => setForm({ ...form, expected_topics: e.target.value })} />
            <div className="flex gap-2 justify-end">
              <button type="button" onClick={() => setShowAdd(false)} className="btn-secondary">Huỷ</button>
              <button type="submit" className="btn-primary">Tạo</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        {/* Test Cases */}
        <div>
          <h2 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Test Cases</h2>
          <div className="space-y-3">
            {cases.length === 0 ? (
              <div className="card text-center text-gray-400 text-sm py-8">Chưa có test case nào</div>
            ) : cases.map((tc) => (
              <div key={tc.id} className="card">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-semibold text-gray-900">{tc.name}</p>
                    {tc.description && <p className="text-xs text-gray-500 mt-0.5">{tc.description}</p>}
                    <div className="flex items-center gap-2 mt-1">
                      <span className="badge badge-blue">{tc.practice_area}</span>
                      <span className="badge badge-gray">{tc.complexity}</span>
                      {tc.baseline_score && (
                        <span className="text-xs text-green-600 font-medium">Baseline: {tc.baseline_score}/100</span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => handleRun(tc.id)}
                    disabled={running === tc.id}
                    className="btn-primary text-xs flex items-center gap-1"
                  >
                    <Play className="w-3 h-3" />
                    {running === tc.id ? "Running..." : "Run"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Runs */}
        <div>
          <h2 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Runs gần đây</h2>
          <div className="space-y-2">
            {runs.length === 0 ? (
              <div className="card text-center text-gray-400 text-sm py-8">Chưa có run nào</div>
            ) : runs.map((r) => (
              <div key={r.id} className="card p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      {r.passed
                        ? <CheckCircle className="w-4 h-4 text-green-500" />
                        : <XCircle className="w-4 h-4 text-red-500" />}
                      <span className="text-sm font-medium text-gray-900">
                        Case #{r.test_case_id}
                      </span>
                      {r.score_total && (
                        <span className="text-xs text-gray-500">{r.score_total}/100</span>
                      )}
                    </div>
                    {r.delta_from_baseline !== null && r.delta_from_baseline !== undefined && (
                      <p className={`text-xs mt-0.5 ${r.delta_from_baseline >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {r.delta_from_baseline >= 0 ? "+" : ""}{r.delta_from_baseline?.toFixed(2)} vs baseline
                      </p>
                    )}
                    {r.reason_codes_triggered?.length > 0 && (
                      <p className="text-xs text-red-500 mt-0.5">
                        Codes: {r.reason_codes_triggered.join(", ")}
                      </p>
                    )}
                  </div>
                  <p className="text-xs text-gray-400">{new Date(r.created_at).toLocaleDateString("vi-VN")}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
