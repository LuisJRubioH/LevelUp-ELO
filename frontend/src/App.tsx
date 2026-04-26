/**
 * App.tsx
 * ========
 * Router principal con React Router v6.
 * Rutas protegidas por rol; redirige al login si no hay sesión.
 * Code splitting: cada página se carga bajo demanda (React.lazy).
 */

import { lazy, Suspense } from "react";
import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useAuthStore } from "./stores/authStore";
import { Layout } from "./pages/Layout";
import { Login } from "./pages/Login";
import { ErrorBoundary } from "./components/ui/ErrorBoundary";
import { PageSkeleton } from "./components/ui/PageSkeleton";
import { PWAPrompt } from "./components/ui/PWAPrompt";

// Estudiante — cargado bajo demanda
const Practice = lazy(() =>
  import("./pages/Student/Practice").then((m) => ({ default: m.Practice }))
);
const Stats = lazy(() =>
  import("./pages/Student/Stats").then((m) => ({ default: m.Stats }))
);
const Courses = lazy(() =>
  import("./pages/Student/Courses").then((m) => ({ default: m.Courses }))
);
const Exam = lazy(() =>
  import("./pages/Student/Exam").then((m) => ({ default: m.Exam }))
);
const ProcedureUpload = lazy(() =>
  import("./pages/Student/ProcedureUpload").then((m) => ({ default: m.ProcedureUpload }))
);
const Feedback = lazy(() =>
  import("./pages/Student/Feedback").then((m) => ({ default: m.Feedback }))
);

// Docente — cargado bajo demanda
const TeacherDashboard = lazy(() =>
  import("./pages/Teacher/Dashboard").then((m) => ({ default: m.TeacherDashboard }))
);
const TeacherGroups = lazy(() =>
  import("./pages/Teacher/Groups").then((m) => ({ default: m.TeacherGroups }))
);
const TeacherProcedures = lazy(() =>
  import("./pages/Teacher/Procedures").then((m) => ({ default: m.TeacherProcedures }))
);
const TeacherExport = lazy(() =>
  import("./pages/Teacher/Export").then((m) => ({ default: m.TeacherExport }))
);

// Admin — cargado bajo demanda
const AdminUsers = lazy(() =>
  import("./pages/Admin/Users").then((m) => ({ default: m.AdminUsers }))
);
const AdminGroups = lazy(() =>
  import("./pages/Admin/Groups").then((m) => ({ default: m.AdminGroups }))
);
const AdminReports = lazy(() =>
  import("./pages/Admin/Reports").then((m) => ({ default: m.AdminReports }))
);
const AdminAudit = lazy(() =>
  import("./pages/Admin/Audit").then((m) => ({ default: m.AdminAudit }))
);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
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
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <PWAPrompt />
          <Suspense fallback={<PageSkeleton />}>
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
              <Route
                path="/student/exam"
                element={<StudentRoute><Exam /></StudentRoute>}
              />
              <Route
                path="/student/procedure"
                element={<StudentRoute><ProcedureUpload /></StudentRoute>}
              />
              <Route
                path="/student/feedback"
                element={<StudentRoute><Feedback /></StudentRoute>}
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
              <Route
                path="/admin/audit"
                element={<AdminRoute><AdminAudit /></AdminRoute>}
              />

              {/* 404 */}
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </Suspense>
        </Router>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
