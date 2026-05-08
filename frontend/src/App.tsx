import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Matters from "./pages/Matters";
import NewMatter from "./pages/NewMatter";
import MatterDetail from "./pages/MatterDetail";
import Admin from "./pages/Admin";
import AdminUsers from "./pages/AdminUsers";
import AdminAutotest from "./pages/AdminAutotest";
import SampleAdvices from "./pages/SampleAdvices";
import Laws from "./pages/Laws";
import LegalSearch from "./pages/LegalSearch";
import LegalChat from "./pages/LegalChat";
import LegalDocuments from "./pages/LegalDocuments";
import AdminCrawler from "./pages/AdminCrawler";
import AdminSkills from "./pages/AdminSkills";
import AdminBotVariants from "./pages/AdminBotVariants";
import AdminPipelineTemplates from "./pages/AdminPipelineTemplates";
// Module 2 — Writing
import Writing from "./pages/Writing";
import WritingNew from "./pages/WritingNew";
import WritingDetail from "./pages/WritingDetail";
import AdminPriorityDocs from "./pages/AdminPriorityDocs";
import AdminSampleWritings from "./pages/AdminSampleWritings";
import DocAnalysis from "./pages/DocAnalysis";
import DocAnalysisNew from "./pages/DocAnalysisNew";
import DocAnalysisDetail from "./pages/DocAnalysisDetail";
import AdminLawDocuments from "./pages/AdminLawDocuments";
import SampleWritingsPublic from "./pages/SampleWritingsPublic";
import Cases from "./pages/Cases";
import CaseNew from "./pages/CaseNew";
import CaseDetail from "./pages/CaseDetail";
import WorkflowEditor from "./pages/WorkflowEditor";
import { getUser } from "./lib/auth";

function RequireAuth({ children }: { children: React.ReactNode }) {
  const user = getUser();
  if (!user) return <Navigate to="/login" replace />;
  return <Layout>{children}</Layout>;
}

function RequireAdmin({ children }: { children: React.ReactNode }) {
  const user = getUser();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== "admin") return <Navigate to="/" replace />;
  return <Layout>{children}</Layout>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: { fontSize: "14px" },
          success: { iconTheme: { primary: "#028a39", secondary: "white" } },
        }}
      />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<RequireAuth><Dashboard /></RequireAuth>} />
        <Route path="/matters" element={<RequireAuth><Matters /></RequireAuth>} />
        <Route path="/matters/new" element={<RequireAuth><NewMatter /></RequireAuth>} />
        <Route path="/matters/:id" element={<RequireAuth><MatterDetail /></RequireAuth>} />
        <Route path="/sample-advices" element={<RequireAuth><SampleAdvices /></RequireAuth>} />
        <Route path="/laws" element={<RequireAuth><Laws /></RequireAuth>} />
        <Route path="/legal-search" element={<RequireAuth><LegalSearch /></RequireAuth>} />
        <Route path="/legal-chat" element={<RequireAuth><LegalChat /></RequireAuth>} />
        <Route path="/legal-documents" element={<RequireAuth><LegalDocuments /></RequireAuth>} />
        {/* Module 2 — Writing */}
        <Route path="/writing" element={<RequireAuth><Writing /></RequireAuth>} />
        <Route path="/writing/new" element={<RequireAuth><WritingNew /></RequireAuth>} />
        <Route path="/writing/:id" element={<RequireAuth><WritingDetail /></RequireAuth>} />
        <Route path="/sample-writings" element={<RequireAuth><SampleWritingsPublic /></RequireAuth>} />
        {/* Module 3 — Tra cứu & Phân tích */}
        <Route path="/doc-analysis" element={<RequireAuth><DocAnalysis /></RequireAuth>} />
        <Route path="/doc-analysis/new" element={<RequireAuth><DocAnalysisNew /></RequireAuth>} />
        <Route path="/doc-analysis/:id" element={<RequireAuth><DocAnalysisDetail /></RequireAuth>} />
        {/* Admin */}
        <Route path="/admin" element={<RequireAdmin><Admin /></RequireAdmin>} />
        <Route path="/admin/users" element={<RequireAdmin><AdminUsers /></RequireAdmin>} />
        <Route path="/admin/autotest" element={<RequireAdmin><AdminAutotest /></RequireAdmin>} />
        <Route path="/admin/crawler" element={<RequireAdmin><AdminCrawler /></RequireAdmin>} />
        <Route path="/admin/skills" element={<RequireAdmin><AdminSkills /></RequireAdmin>} />
        <Route path="/admin/bot-variants" element={<RequireAdmin><AdminBotVariants /></RequireAdmin>} />
        <Route path="/admin/pipeline-templates" element={<RequireAdmin><AdminPipelineTemplates /></RequireAdmin>} />
        <Route path="/admin/priority-docs" element={<RequireAdmin><AdminPriorityDocs /></RequireAdmin>} />
        <Route path="/admin/sample-writings" element={<RequireAdmin><AdminSampleWritings /></RequireAdmin>} />
        <Route path="/admin/law-documents" element={<RequireAdmin><AdminLawDocuments /></RequireAdmin>} />
        <Route path="/admin/workflows" element={<RequireAdmin><WorkflowEditor /></RequireAdmin>} />
        {/* Module 0 — Cases */}
        <Route path="/cases" element={<RequireAuth><Cases /></RequireAuth>} />
        <Route path="/cases/new" element={<RequireAuth><CaseNew /></RequireAuth>} />
        <Route path="/cases/:id" element={<RequireAuth><CaseDetail /></RequireAuth>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
