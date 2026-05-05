import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../lib/api";
import { setAuth } from "../lib/auth";
import { Scale } from "lucide-react";
import toast from "react-hot-toast";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await authApi.login(email, password);
      setAuth(res.data.access_token, res.data.user);
      navigate("/");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Đăng nhập thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-green-100">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4" style={{ background: "#028a39" }}>
            <Scale className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">TaxLegal AI</h1>
          <p className="text-gray-500 mt-1 text-sm">Hệ thống tư vấn Thuế & Pháp luật AI</p>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                className="input-field"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mật khẩu</label>
              <input
                type="password"
                className="input-field"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-2.5"
            >
              {loading ? "Đang đăng nhập..." : "Đăng nhập"}
            </button>
          </form>
        </div>

        <p className="text-center text-xs text-gray-400 mt-6">
          TaxLegal AI v1.0 — Powered by EZLAW-AI V15.1 Architecture
        </p>
      </div>
    </div>
  );
}
