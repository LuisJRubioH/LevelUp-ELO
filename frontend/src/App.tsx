/**
 * App.tsx
 * ========
 * Router principal con React Router v6.
 * Rutas protegidas por rol; redirige al login si no hay sesión.
 * Code splitting: cada página se carga bajo demanda (React.lazy).
 */

import { lazy, Suspense, useEffect } from "react";
import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useAuthStore } from "./stores/authStore";
import { Layout } from "./pages/Layout";
import { Login } from "./pages/Login";
import { ErrorBoundary } from "./components/ui/ErrorBoundary";
import { PageSkeleton } from "./components/ui/PageSkeleton";

// Landing pública — cargada bajo demanda
const Home = lazy(() => import("./pages/Home").then((m) => ({ default: m.Home })));
const ChangePassword = lazy(() =>
  import("./pages/ChangePassword").then((m) => ({ default: m.ChangePassword }))
);
const DisplayName = lazy(() =>
  import("./pages/DisplayName").then((m) => ({ default: m.DisplayName }))
);

// Shell de la Consola Docente (rediseño) — reemplaza el Layout para /teacher/*
const TeacherLayout = lazy(() =>
  import("./pages/Teacher/TeacherLayout").then((m) => ({ default: m.TeacherLayout }))
);

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
const CourseEntry = lazy(() =>
  import("./pages/Student/CourseEntry").then((m) => ({ default: m.CourseEntry }))
);
const CourseMap = lazy(() =>
  import("./pages/Student/CourseMap").then((m) => ({ default: m.CourseMap }))
);
const Lesson = lazy(() =>
  import("./pages/Student/Lesson").then((m) => ({ default: m.Lesson }))
);
const StudentLayout = lazy(() =>
  import("./pages/Student/StudentLayout").then((m) => ({ default: m.StudentLayout }))
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
const League = lazy(() =>
  import("./pages/Student/League").then((m) => ({ default: m.League }))
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
const TeacherExams = lazy(() =>
  import("./pages/Teacher/Exams").then((m) => ({ default: m.TeacherExams }))
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
      // 3 reintentos con backoff exponencial (≈ 2s, 4s, 8s) — el cold start
      // de Render free tier puede tardar hasta 30s. No reintentes errores
      // 4xx (auth/validación): no van a desaparecer con un reintento.
      retry: (failureCount, error) => {
        const status = (error as { status?: number } | null)?.status ?? 0;
        if (status >= 400 && status < 500) return false;
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) =>
        Math.min(2000 * 2 ** attemptIndex, 15_000),
      staleTime: 30_000,
    },
  },
});

function RequireRole({
  role,
  also = [],
  children,
}: {
  role: string;
  also?: string[];
  children: React.ReactNode;
}) {
  const user = useAuthStore((s) => s.user);
  const mustChangePassword = useAuthStore((s) => s.mustChangePassword);
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== role && !also.includes(user.role) && user.role !== "admin") {
    return <Navigate to="/login" replace />;
  }
  // Spec 004 FR-030: a temporary password is changed before anything else.
  if (mustChangePassword) return <Navigate to="/cambiar-contrasena" replace />;
  return <>{children}</>;
}

function RequireSignedIn({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user);
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function StudentRoute({ children }: { children: React.ReactNode }) {
  return (
    <RequireRole role="student">
      <StudentLayout>{children}</StudentLayout>
    </RequireRole>
  );
}

/**
 * The course map and its lessons (spec 003 L1). A student walks them; a teacher of a group in the
 * course, or an admin, previews them read only — the API refuses whatever they send, and the
 * banner says so before they try.
 */
function PathRoute({ children }: { children: React.ReactNode }) {
  const role = useAuthStore((s) => s.user?.role);
  const Shell = role === "teacher" ? TeacherLayout : StudentLayout;
  return (
    <RequireRole role="student" also={["teacher"]}>
      <Shell>
        {role !== "student" && (
          <p className="path-preview-banner" role="status">
            Vista previa: puedes recorrer todos los nodos, pero nada de lo que respondas se guarda.
          </p>
        )}
        {children}
      </Shell>
    </RequireRole>
  );
}

function TeacherRoute({ children }: { children: React.ReactNode }) {
  return (
    <RequireRole role="teacher">
      <TeacherLayout>{children}</TeacherLayout>
    </RequireRole>
  );
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  return (
    <RequireRole role="admin">
      <Layout>{children}</Layout>
    </RequireRole>
  );
}

export default function App() {
  // Guard global: cancela cualquier intento del navegador de mostrar
  // el banner "Instalar app". Combinado con manifest display:"browser"
  // y la ausencia del componente PWAPrompt, evita que aparezca por
  // cualquier camino — los usuarios solo deben usar la plataforma desde
  // el navegador (estudiantes y docentes se confundían con la instalación).
  useEffect(() => {
    const blockInstall = (e: Event) => {
      e.preventDefault();
      return false;
    };
    window.addEventListener("beforeinstallprompt", blockInstall);
    return () => window.removeEventListener("beforeinstallprompt", blockInstall);
  }, []);

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Suspense fallback={<PageSkeleton />}>
            <Routes>
              {/* Público */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route
                path="/cambiar-contrasena"
                element={<RequireSignedIn><ChangePassword /></RequireSignedIn>}
              />
              {/* Spec 004 FR-025: the student's own display name. */}
              <Route
                path="/mi-nombre"
                element={<RequireRole role="student"><DisplayName /></RequireRole>}
              />

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
                path="/student/course/:courseId"
                element={<StudentRoute><CourseEntry /></StudentRoute>}
              />
              <Route
                path="/student/course/:courseId/map"
                element={<PathRoute><CourseMap /></PathRoute>}
              />
              <Route
                path="/student/course/:courseId/lesson/:nodeId"
                element={<PathRoute><Lesson /></PathRoute>}
              />
              <Route
                path="/student/league"
                element={<StudentRoute><League /></StudentRoute>}
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
              <Route
                path="/teacher/exams"
                element={<TeacherRoute><TeacherExams /></TeacherRoute>}
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
