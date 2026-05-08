import { Link, useLocation, useNavigate } from "react-router-dom";
import { clearAuth, getUser } from "../lib/auth";
import {
  LayoutDashboard, FileText, BookOpen, Settings,
  LogOut, Shield, FlaskConical, Scale, Search,
  MessageSquare, Globe, Target, Bot,
  ClipboardList, PenTool, BookMarked, Library,
  FileSearch, ChevronDown, ChevronRight, Gavel,
  Briefcase, GitBranch
} from "lucide-react";
import { useState } from "react";

// Module sections
const MODULE1 = [
  { href: "/cases", icon: Briefcase, label: "Cases" },
  { href: "/matters", icon: FileText, label: "Vấn đề" },
  { href: "/sample-advices", icon: BookOpen, label: "Bài tư vấn mẫu" },
];

const MODULE2 = [
  { href: "/writing", icon: PenTool, label: "Viết bài phân tích" },
  { href: "/sample-writings", icon: Library, label: "Bài viết mẫu" },
];

const MODULE3 = [
  { href: "/legal-search", icon: Search, label: "Tra cứu Luật" },
  { href: "/legal-chat", icon: MessageSquare, label: "Tư vấn AI" },
  { href: "/doc-analysis", icon: FileSearch, label: "Phân tích văn bản" },
];

const ADMIN_ITEMS = [
  { href: "/admin", icon: Settings, label: "Tổng quan" },
  { href: "/admin/users", icon: Shield, label: "Users" },
  { href: "/admin/law-documents", icon: Scale, label: "Văn bản Luật" },
  { href: "/admin/priority-docs", icon: BookMarked, label: "Priority Docs" },
  { href: "/admin/sample-writings", icon: Library, label: "Bài viết mẫu (kho)" },
  { href: "/admin/skills", icon: Target, label: "Skills" },
  { href: "/admin/bot-variants", icon: Bot, label: "Bot Variants" },
  { href: "/admin/pipeline-templates", icon: ClipboardList, label: "Pipeline Templates" },
  { href: "/admin/crawler", icon: Globe, label: "Crawler" },
  { href: "/admin/autotest", icon: FlaskConical, label: "AutoTest" },
  { href: "/admin/workflows", icon: GitBranch, label: "Workflow Editor" },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const user = getUser();
  const [settingsOpen, setSettingsOpen] = useState(
    pathname.startsWith("/admin")
  );

  const handleLogout = () => { clearAuth(); navigate("/login"); };

  const isActive = (href: string) =>
    href === "/" ? pathname === "/" : pathname === href || (href !== "/" && pathname.startsWith(href + "/"));

  const NavLink = ({ href, icon: Icon, label, indent = false }: {
    href: string; icon: any; label: string; indent?: boolean
  }) => (
    <Link
      to={href}
      className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
        indent ? "ml-2 text-xs" : ""
      } ${
        isActive(href)
          ? "text-white"
          : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
      }`}
      style={isActive(href) ? { background: "#028a39" } : {}}
    >
      <Icon className={`shrink-0 ${indent ? "w-3.5 h-3.5" : "w-4 h-4"} ${isActive(href) ? "text-white" : "text-gray-400"}`} />
      <span className="truncate">{label}</span>
    </Link>
  );

  const SectionHeader = ({ label }: { label: string }) => (
    <div className="pt-4 pb-1">
      <p className="px-3 text-[10px] font-bold text-gray-400 uppercase tracking-widest">{label}</p>
    </div>
  );

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Sidebar */}
      <aside className="w-60 bg-white border-r border-gray-100 flex flex-col shadow-sm fixed h-full z-10">
        {/* Logo */}
        <div className="px-5 py-4 border-b border-gray-100">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style={{ background: "#028a39" }}>
              <Gavel className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-gray-900 text-sm leading-tight">TaxLegal AI</h1>
              <p className="text-[10px] text-gray-400">Thuế &amp; Pháp luật Việt Nam</p>
            </div>
          </Link>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-2.5 py-3 space-y-0.5 overflow-y-auto">
          <NavLink href="/" icon={LayoutDashboard} label="Dashboard" />

          <SectionHeader label="Module 1 — Tư vấn" />
          {MODULE1.map((item) => <NavLink key={item.href} {...item} />)}

          <SectionHeader label="Module 2 — Viết bài" />
          {MODULE2.map((item) => <NavLink key={item.href} {...item} />)}

          <SectionHeader label="Module 3 — Tra cứu" />
          {MODULE3.map((item) => <NavLink key={item.href} {...item} />)}

          {user?.role === "admin" && (
            <>
              <div className="pt-4 pb-1">
                <button
                  onClick={() => setSettingsOpen(!settingsOpen)}
                  className="w-full flex items-center gap-2 px-3 py-1 text-[10px] font-bold text-gray-400 uppercase tracking-widest hover:text-gray-600"
                >
                  {settingsOpen ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                  Settings &amp; Admin
                </button>
              </div>
              {settingsOpen && ADMIN_ITEMS.map((item) => (
                <NavLink key={item.href} {...item} indent />
              ))}
            </>
          )}
        </nav>

        {/* User */}
        <div className="px-3 py-4 border-t border-gray-100">
          <div className="flex items-center gap-2.5 mb-2.5">
            <div className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0"
              style={{ background: "#028a39" }}>
              {user?.full_name?.[0] || user?.email?.[0] || "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-900 truncate">{user?.full_name || user?.email}</p>
              <p className="text-[10px] text-gray-400 capitalize">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-2.5 py-1.5 text-xs text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
            Đăng xuất
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="ml-60 flex-1 min-h-screen">
        <div className="max-w-7xl mx-auto p-6">
          {children}
        </div>
      </main>
    </div>
  );
}
