/**
 * App.tsx
 * ========
 * Router principal con React Router v6.
 * Rutas protegidas por rol; redirige al login si no hay sesión.
 */

import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useAuthStore } from "./stores/authStore";
import { Layout } from "./pages/Layout";
import { Login } from "./pages/Login";

// Estudiante
import { Practice } from "./pages/Student/Practice";
import { Stats } from "./pages/Student/Stats";
import { Courses } from "./pages/Student/Courses";

// Docente
import { TeacherDashboard } from "./pages/Teacher/Dashboard";
import { TeacherGroups } from "./pages/Teacher/Groups";
import { TeacherProcedures } from "./pages/Teacher/Procedures";
import { TeacherExport } from "./pages/Teacher/Export";

// Admin
import { AdminUsers } from "./pages/Admin/Users";
import { AdminGroups } from "./pages/Admin/Groups";
import { AdminReports } from "./pages/Admin/Reports";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000, // 30 s
    },
  },
});

function RequireAuth({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function RequireRole({
  role,
  children,
}: {
  role: string;
  children: React.ReactNode;
}) {
  const user = useAuthStore((s) => s.user);
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== role && user.role !== "admin") {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function StudentRoute({ children }: { children: React.ReactNode }) {
  return (
    <RequireRole role="student">
      <Layout>{children}</Layout>
    </RequireRole>
  );
}

function TeacherRoute({ children }: { children: React.ReactNode }) {
  return (
    <RequireRole role="teacher">
      <Layout>{children}</Layout>
    </RequireRole>
  );
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  return (
    <RequireAuth>
      <Layout>{children}</Layout>
    </RequireAuth>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* Público */}
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Navigate to="/login" replace />} />

          {/* ── Estudiante ─────────────────────────────────────────── */}
          <Route
            path="/student"
            element={<StudentRoute><Practice /></StudentRoute>}
          />
          <Route
            path="/student/stats"
            element={<StudentRoute><Stats /></StudentRoute>}
          />
          <Route
            path="/student/courses"
            element={<StudentRoute><Courses /></StudentRoute>}
          />

          {/* ── Docente ────────────────────────────────────────────── */}
          <Route
            path="/teacher"
            element={<TeacherRoute><TeacherDashboard /></TeacherRoute>}
          />
          <Route
            path="/teacher/groups"
            element={<TeacherRoute><TeacherGroups /></TeacherRoute>}
          />
          <Route
            path="/teacher/procedures"
            element={<TeacherRoute><TeacherProcedures /></TeacherRoute>}
          />
          <Route
            path="/teacher/export"
            element={<TeacherRoute><TeacherExport /></TeacherRoute>}
          />

          {/* ── Admin ──────────────────────────────────────────────── */}
          <Route
            path="/admin"
            element={<AdminRoute><AdminUsers /></AdminRoute>}
          />
          <Route
            path="/admin/groups"
            element={<AdminRoute><AdminGroups /></AdminRoute>}
          />
          <Route
            path="/admin/reports"
            element={<AdminRoute><AdminReports /></AdminRoute>}
          />

          {/* 404 */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}
