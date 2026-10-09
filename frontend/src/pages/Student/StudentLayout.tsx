/**
 * pages/Student/StudentLayout.tsx
 * ===============================
 * Shell del panel estudiante (rediseño) — unificado con la Consola Docente:
 * reusa el shell `.lue-tc` (TeacherConsole.css). Sidebar (escritorio) + nav
 * inferior (móvil, mobile-first). El item "Mapa" aparece al entrar a una
 * materia (cuando hay sesión de práctica activa = post-diagnóstico).
 */

import type { ReactNode } from "react";
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useQueryClient } from "@tanstack/react-query";
import { authApi } from "../../api/auth";
import { useAuthStore } from "../../stores/authStore";
import { useThemeStore } from "../../stores/themeStore";
import { useSettingsStore, PROVIDER_MODELS } from "../../stores/settingsStore";
import { usePracticeStore } from "../../stores/practiceStore";
import { ReportProblemButton } from "../../components/ReportProblem/ReportProblemButton";
import { CourseRail } from "../../components/Course/CourseRail";
import { clearAccountCaches } from "../../lib/accountCleanup";
import "../Teacher/TeacherConsole.css";

const NAV = [
  { path: "/student", label: "Practicar", ic: "🎯" },
  { path: "/student/courses", label: "Materias", ic: "📚" },
  { path: "/student/stats", label: "Progreso", ic: "📈" },
  { path: "/student/league", label: "Liga", ic: "⚔️" },
  { path: "/student/exam", label: "Exámenes", ic: "📋" },
  { path: "/student/procedure", label: "Procedimiento", ic: "✍️" },
  { path: "/student/feedback", label: "KatIA", ic: "💬" },
];
const MOB = [NAV[0], NAV[1], NAV[2], NAV[3], NAV[6]];

function initials(n: string) {
  return n.slice(0, 2).toUpperCase();
}

export function StudentLayout({ children }: { children: ReactNode }) {
  const { i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const user = useAuthStore((s) => s.user);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const queryClient = useQueryClient();
  const { theme, toggleTheme } = useThemeStore();
  const { apiKey, provider, model, setApiKey, setProvider, setModel } = useSettingsStore();
  const courseId = usePracticeStore((s) => s.courseId);
  const availableModels = PROVIDER_MODELS[provider] ?? [];
  const [aiOpen, setAiOpen] = useState(false);

  const lang = i18n.language?.startsWith("en") ? "en" : "es";
  const onMap = location.pathname.includes("/course/");
  const fullBleed = location.pathname.endsWith("/map");

  // Cajón derecho del curso: se muestra en el mapa Y dentro de las lecciones.
  // courseId/nodeId salen de la URL (no del store) para cubrir ambas rutas.
  const courseMatch = location.pathname.match(/\/course\/([^/]+)(?:\/lesson\/([^/]+))?/);
  const railCourseId = courseMatch ? decodeURIComponent(courseMatch[1]) : null;
  const railNodeId = courseMatch?.[2] ? decodeURIComponent(courseMatch[2]) : undefined;

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch {
      /* ignorar */
    }
    await clearAccountCaches();
    queryClient.clear();
    setApiKey("");
    usePracticeStore.getState().resetSession();
    clearAuth();
    navigate("/login");
  };

  return (
    <div className="lue-tc">
      <aside className="tc-side">
        <div className="tc-brand">
          <Link to="/student" aria-label="Oulad">
            <img className="brand-logo brand-logo-dark" src="/oulad-logo-dark.png" alt="Oulad" />
            <img className="brand-logo brand-logo-light" src="/oulad-logo-light.png" alt="Oulad" />
          </Link>
          <span className="tag">MOTOR ELO · ESTUDIANTE</span>
        </div>

        <nav className="tc-nav">
          {NAV.map((n) => (
            <Link key={n.path} to={n.path} className={"nav-item" + (location.pathname === n.path ? " on" : "")}>
              <span className="ic">{n.ic}</span>
              {n.label}
            </Link>
          ))}
          {courseId && (
            <Link
              to={`/student/course/${courseId}/map`}
              className={"nav-item" + (onMap ? " on" : "")}
            >
              <span className="ic">🗺️</span>
              Mapa
            </Link>
          )}

          <div className={"tc-ai" + (aiOpen ? " open" : "")} style={{ marginTop: "auto" }}>
            <button className="head" onClick={() => setAiOpen((o) => !o)} aria-expanded={aiOpen}>
              <span className={"dot " + (apiKey ? "ok" : "off")} />
              API de IA · KatIA
              <span className="chev">▾</span>
            </button>
            <div className="body">
              <div className="row">
                <span>Key</span>
                <b>{apiKey ? "Tuya" : "Del sistema"}</b>
              </div>
              <select className="ai-input" value={provider} onChange={(e) => setProvider(e.target.value)} aria-label="Proveedor">
                <option value="groq">Groq</option>
                <option value="anthropic">Anthropic</option>
                <option value="openai">OpenAI</option>
                <option value="google">Google Gemini</option>
              </select>
              {availableModels.length > 0 && (
                <select className="ai-input" value={model} onChange={(e) => setModel(e.target.value)} aria-label="Modelo">
                  <option value="">Modelo automático</option>
                  {availableModels.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.label}
                    </option>
                  ))}
                </select>
              )}
              <input
                className="ai-input"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Tu API key (opcional)"
              />
            </div>
          </div>
        </nav>

        <div className="tc-foot">
          <div className="tc-user">
            <div className="ava">{initials(user?.username ?? "?")}</div>
            <div className="meta">
              <b>{user?.username}</b>
              <span>
                <span className="role">Estudiante</span>
                {user?.education_level ? ` · ${user.education_level}` : ""}
              </span>
            </div>
          </div>
          <div style={{ display: "flex" }}>
            <ReportProblemButton />
          </div>
          <div className="tc-toggles">
            <button className="tc-tog" onClick={toggleTheme}>
              {theme === "light" ? "🌙 Modo oscuro" : "☀️ Modo claro"}
            </button>
            <button className="tc-tog" onClick={() => i18n.changeLanguage(lang === "es" ? "en" : "es")}>
              🌐 {lang.toUpperCase()}
            </button>
          </div>
          <button className="tc-logout" onClick={handleLogout}>
            Cerrar sesión →
          </button>
        </div>
      </aside>

      <main className="tc-main">
        <div className={"tc-main-inner" + (fullBleed ? " full" : "")}>{children}</div>
      </main>

      {railCourseId && <CourseRail courseId={railCourseId} currentNodeId={railNodeId} />}

      {/* nav inferior (móvil) */}
      <nav className="tc-mobnav">
        {MOB.map((n) => (
          <Link key={n.path} to={n.path} className={location.pathname === n.path ? "on" : ""}>
            <span className="ic" aria-hidden="true">
              {n.ic}
            </span>
            <span>{n.label}</span>
          </Link>
        ))}
      </nav>
    </div>
  );
}
