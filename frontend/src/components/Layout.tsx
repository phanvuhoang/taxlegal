import { Link, useLocation, useNavigate } from "react-router-dom";
import { clearAuth, getUser } from "../lib/auth";
import {
  LayoutDashboard, FileText, BookOpen, Settings,
  LogOut, Shield, FlaskConical, Scale, Search,
  MessageSquare, FolderOpen, Globe
} from "lucide-react";

const navItems = [
  { href: "/", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/matters", icon: FileText, label: "Matters" },
  { href: "/sample-advices", icon: BookOpen, label: "Bài Mẫu" },
  { href: "/laws", icon: Scale, label: "Văn Bản Luật" },
];

const legalAgentItems = [
  { href: "/legal-search", icon: Search, label: "Tra cứu Luật" },
  { href: "/legal-chat", icon: MessageSquare, label: "Tư vấn AI" },
  { href: "/legal-documents", icon: FolderOpen, label: "Tài liệu" },
];

const adminItems = [
  { href: "/admin", icon: Settings, label: "Admin" },
  { href: "/admin/users", icon: Shield, label: "Users" },
  { href: "/admin/autotest", icon: FlaskConical, label: "AutoTest" },
  { href: "/admin/crawler", icon: Globe, label: "Crawler Văn bản" },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const user = getUser();

  const handleLogout = () => {
    clearAuth();
    navigate("/login");
  };

  const isActive = (href: string) =>
    href === "/" ? pathname === "/" : pathname.startsWith(href);

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-100 flex flex-col shadow-sm fixed h-full z-10">
        {/* Logo */}
        <div className="px-6 py-5 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "#028a39" }}>
              <Scale className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-gray-900 text-sm leading-tight">TaxLegal AI</h1>
              <p className="text-xs text-gray-400">Tư vấn Thuế & Pháp luật</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map(({ href, icon: Icon, label }) => (
            <Link
              key={href}
              to={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive(href)
                  ? "bg-primary-50 text-primary-600"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive(href) ? "text-primary-500" : "text-gray-400"}`} />
              {label}
            </Link>
          ))}

          {/* Legal Agent section */}
          <div className="pt-3 pb-1">
            <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">Legal AI</p>
          </div>
          {legalAgentItems.map(({ href, icon: Icon, label }) => (
            <Link
              key={href}
              to={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive(href)
                  ? "bg-primary-50 text-primary-600"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive(href) ? "text-primary-500" : "text-gray-400"}`} />
              {label}
            </Link>
          ))}

          {user?.role === "admin" && (
            <>
              <div className="pt-3 pb-1">
                <p className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">Admin</p>
              </div>
              {adminItems.map(({ href, icon: Icon, label }) => (
                <Link
                  key={href}
                  to={href}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive(href)
                      ? "bg-primary-50 text-primary-600"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive(href) ? "text-primary-500" : "text-gray-400"}`} />
                  {label}
                </Link>
              ))}
            </>
          )}
        </nav>

        {/* User info */}
        <div className="px-4 py-4 border-t border-gray-100">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold"
              style={{ background: "#028a39" }}>
              {user?.full_name?.[0] || user?.email?.[0] || "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{user?.full_name || user?.email}</p>
              <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Đăng xuất
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="ml-64 flex-1 min-h-screen">
        <div className="max-w-7xl mx-auto p-6">
          {children}
        </div>
      </main>
    </div>
  );
}
