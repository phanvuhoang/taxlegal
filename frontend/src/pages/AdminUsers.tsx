import { useEffect, useState } from "react";
import { adminApi } from "../lib/api";
import { Plus, Trash2, Shield, User } from "lucide-react";
import toast from "react-hot-toast";

export default function AdminUsers() {
  const [users, setUsers] = useState<any[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ email: "", password: "", full_name: "", role: "user" });
  const [saving, setSaving] = useState(false);

  const load = () => adminApi.listUsers().then((r) => setUsers(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await adminApi.createUser(form);
      toast.success("Đã tạo user");
      setShowAdd(false);
      setForm({ email: "", password: "", full_name: "", role: "user" });
      load();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Lỗi");
    } finally {
      setSaving(false);
    }
  };

  const handleToggleActive = async (user: any) => {
    try {
      await adminApi.updateUser(user.id, { is_active: !user.is_active });
      toast.success("Đã cập nhật");
      load();
    } catch { toast.error("Lỗi"); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Xoá user này?")) return;
    try {
      await adminApi.deleteUser(id);
      toast.success("Đã xoá");
      load();
    } catch (err: any) { toast.error(err.response?.data?.detail || "Lỗi"); }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Shield className="w-6 h-6 text-primary-500" /> Quản lý Users
          </h1>
        </div>
        <button onClick={() => setShowAdd(!showAdd)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Thêm User
        </button>
      </div>

      {showAdd && (
        <div className="card mb-4">
          <h3 className="font-semibold text-gray-900 mb-3">Thêm User mới</h3>
          <form onSubmit={handleCreate} className="grid md:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Email</label>
              <input type="email" className="input-field" value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Mật khẩu</label>
              <input type="password" className="input-field" value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={8} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Tên</label>
              <input type="text" className="input-field" value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Vai trò</label>
              <select className="input-field" value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}>
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <div className="md:col-span-2 flex gap-2 justify-end">
              <button type="button" onClick={() => setShowAdd(false)} className="btn-secondary">Huỷ</button>
              <button type="submit" disabled={saving} className="btn-primary">{saving ? "Đang tạo..." : "Tạo"}</button>
            </div>
          </form>
        </div>
      )}

      <div className="card p-0 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50">
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">User</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Vai trò</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Trạng thái</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Ngày tạo</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {users.map((u) => (
              <tr key={u.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold"
                      style={{ background: "#028a39" }}>
                      {u.full_name?.[0] || u.email[0]}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{u.full_name || "—"}</p>
                      <p className="text-xs text-gray-400">{u.email}</p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`badge ${u.role === "admin" ? "badge-purple" : "badge-gray"}`}>
                    {u.role}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleToggleActive(u)}
                    className={`badge ${u.is_active ? "badge-green" : "badge-red"} cursor-pointer`}
                  >
                    {u.is_active ? "Hoạt động" : "Vô hiệu"}
                  </button>
                </td>
                <td className="px-4 py-3 text-xs text-gray-400">
                  {new Date(u.created_at).toLocaleDateString("vi-VN")}
                </td>
                <td className="px-4 py-3">
                  <button onClick={() => handleDelete(u.id)}
                    className="text-gray-300 hover:text-red-500 transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
