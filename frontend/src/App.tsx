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
        <Route path="/admin" element={<RequireAdmin><Admin /></RequireAdmin>} />
        <Route path="/admin/users" element={<RequireAdmin><AdminUsers /></RequireAdmin>} />
        <Route path="/admin/autotest" element={<RequireAdmin><AdminAutotest /></RequireAdmin>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
