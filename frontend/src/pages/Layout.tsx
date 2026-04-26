/**
 * pages/Layout.tsx
 * ================
 * Layout base con sidebar de navegación por rol.
 * Los hijos se renderizan en el área de contenido central.
 */

import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { PageTransition } from "../components/ui/PageTransition";
import { authApi } from "../api/auth";
import { api } from "../api/client";
import { useAuthStore } from "../stores/authStore";
import { useSettingsStore, PROVIDER_MODELS } from "../stores/settingsStore";
import { useNotifications } from "../hooks/useNotifications";
import { ReportProblemButton } from "../components/ReportProblem/ReportProblemButton";

interface NavItem {
  path: string;
  label: string;
  icon: string;
}

const studentNav: NavItem[] = [
  { path: "/student", label: "Practicar", icon: "🎯" },
  { path: "/student/stats", label: "Estadísticas", icon: "📈" },
  { path: "/student/courses", label: "Cursos", icon: "📚" },
  { path: "/student/exam", label: "Examen", icon: "📋" },
  { path: "/student/procedure", label: "Proc. abierto", icon: "✍️" },
  { path: "/student/feedback", label: "Retroalimentación", icon: "💬" },
];

const teacherNav: NavItem[] = [
  { path: "/teacher", label: "Dashboard", icon: "📊" },
  { path: "/teacher/groups", label: "Grupos", icon: "👥" },
  { path: "/teacher/procedures", label: "Procedimientos", icon: "📝" },
  { path: "/teacher/export", label: "Exportar datos", icon: "📥" },
];

const adminNav: NavItem[] = [
  { path: "/admin", label: "Usuarios", icon: "👤" },
  { path: "/admin/groups", label: "Grupos", icon: "🏫" },
  { path: "/admin/reports", label: "Reportes", icon: "🔔" },
  { path: "/admin/audit", label: "Auditoría", icon: "📜" },
];

interface LayoutProps {
  children: ReactNode;
}

function useSessionTimer(sessionStartTime: number | null) {
  const [elapsed, setElapsed] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!sessionStartTime) return;
    const tick = () => setElapsed(Math.floor((Date.now() - sessionStartTime) / 1000));
    tick();
    intervalRef.current = setInterval(tick, 1000);
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [sessionStartTime]);

  const m = Math.floor(elapsed / 60).toString().padStart(2, "0");
  const s = (elapsed % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

export function Layout({ children }: LayoutProps) {
  const { user, sessionStartTime, clearAuth } = useAuthStore();
  const { apiKey, provider, model, setApiKey, setProvider, setModel } = useSettingsStore();
  const updateUser = useAuthStore((s) => s.updateUser);
  const availableModels = PROVIDER_MODELS[provider] ?? [];
  const location = useLocation();
  const navigate = useNavigate();
  const [showIAConfig, setShowIAConfig] = useState(false);
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [emailInput, setEmailInput] = useState("");
  const [emailError, setEmailError] = useState("");
  const [emailSaving, setEmailSaving] = useState(false);
  const sessionFormatted = useSessionTimer(sessionStartTime ?? null);

  const handleSaveEmail = async () => {
    setEmailError("");
    if (!emailInput.includes("@") || !emailInput.includes(".")) {
      setEmailError("Ingresa un correo válido.");
      return;
    }
    setEmailSaving(true);
    try {
      await api.patch("/api/student/profile", { email: emailInput });
      updateUser({ email: emailInput });
      setShowEmailForm(false);
      setEmailInput("");
    } catch (err: unknown) {
      setEmailError(err instanceof Error ? err.message : "Error al guardar.");
    } finally {
      setEmailSaving(false);
    }
  };

  const maskedEmail = user?.email
    ? user.email.replace(/^(.{2})(.*)(@.*)$/, (_, a, b, c) => a + b.replace(/./g, "*") + c)
    : null;

  // Notificaciones en tiempo real según rol
  const wsRoom = user
    ? user.role === "teacher"
      ? `teacher_${user.user_id}`
      : `student_${user.user_id}`
    : "";

  const { unreadCount, clearUnread } = useNotifications({
    room: wsRoom,
    enabled: !!user,
    onEvent: (evt) => {
      // Las notificaciones de procedimiento calificado/enviado se muestran como badge
      if (evt.type === "procedure_graded" || evt.type === "procedure_submitted") {
        // El badge se incrementa automáticamente en useNotifications
      }
    },
  });

  const navItems =
    user?.role === "admin" ? adminNav : user?.role === "teacher" ? teacherNav : studentNav;

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch {
      /* ignorar */
    }
    clearAuth();
    navigate("/login");
  };

  return (
    <div className="flex flex-col md:flex-row h-screen bg-slate-900 overflow-hidden">
      {/* Top bar móvil (solo visible en mobile) */}
      <header className="md:hidden bg-slate-800 border-b border-slate-700 px-4 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <div className="text-base font-bold text-white">
            Level<span className="text-violet-400">Up</span>
          </div>
          {user?.role === "student" && sessionStartTime && (
            <span className="ml-2 text-xs text-slate-500 font-mono bg-slate-900 rounded px-2 py-0.5">
              ⏱ {sessionFormatted}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400 truncate max-w-[80px]">{user?.username}</span>
          <button
            onClick={handleLogout}
            className="text-xs text-slate-500 hover:text-red-400 transition-colors"
            aria-label="Cerrar sesión"
          >
            Salir →
          </button>
        </div>
      </header>

      {/* Sidebar — oculta en mobile */}
      <aside className="hidden md:flex w-56 bg-slate-800 border-r border-slate-700 flex-col shrink-0">
        {/* Logo */}
        <div className="px-4 py-5 border-b border-slate-700">
          <div className="text-lg font-bold text-white">
            Level<span className="text-violet-400">Up</span>
          </div>
          <div className="text-xs text-slate-500 mt-0.5">v1.0.0 ELO</div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const active = location.pathname === item.path;
            const isProcedures = item.path.includes("procedures");
            const showBadge = isProcedures && unreadCount > 0;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => {
                  if (isProcedures) clearUnread();
                }}
                aria-current={active ? "page" : undefined}
                className={[
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all",
                  active
                    ? "bg-violet-600/30 text-violet-300 font-medium"
                    : "text-slate-400 hover:bg-slate-700 hover:text-slate-200",
                ].join(" ")}
              >
                <span aria-hidden="true">{item.icon}</span>
                <span className="flex-1">{item.label}</span>
                {showBadge && (
                  <span
                    className="ml-auto bg-red-500 text-white text-xs font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1"
                    aria-label={`${unreadCount > 99 ? "más de 99" : unreadCount} notificaciones`}
                  >
                    {unreadCount > 99 ? "99+" : unreadCount}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Config IA */}
        <div className="px-4 py-3 border-t border-slate-700">
          <button
            onClick={() => setShowIAConfig((v) => !v)}
            className="flex items-center justify-between w-full text-xs text-slate-400 hover:text-slate-200 transition-colors"
            aria-expanded={showIAConfig}
            aria-controls="ia-config-panel"
          >
            <span>🤖 API de IA</span>
            <span aria-hidden="true">{showIAConfig ? "▲" : "▼"}</span>
          </button>
          {showIAConfig && (
            <div id="ia-config-panel" className="mt-2 space-y-2">
              <div>
                <label className="block text-xs text-slate-500 mb-1">Proveedor</label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-600 rounded text-xs text-slate-300 px-2 py-1 focus:outline-none focus:border-violet-500"
                >
                  <option value="groq">Groq</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="openai">OpenAI</option>
                  <option value="google">Google Gemini</option>
                </select>
              </div>
              {availableModels.length > 0 && (
                <div>
                  <label className="block text-xs text-slate-500 mb-1">Modelo</label>
                  <select
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-600 rounded text-xs text-slate-300 px-2 py-1 focus:outline-none focus:border-violet-500"
                  >
                    <option value="">Auto (recomendado)</option>
                    {availableModels.map((m) => (
                      <option key={m.id} value={m.id}>{m.label}</option>
                    ))}
                  </select>
                </div>
              )}
              <div>
                <label className="block text-xs text-slate-500 mb-1">API Key</label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-... / gsk_..."
                  className="w-full bg-slate-900 border border-slate-600 rounded text-xs text-slate-300 px-2 py-1 focus:outline-none focus:border-violet-500 placeholder-slate-600"
                />
              </div>
              {apiKey && (
                <p className="text-xs text-green-500">✓ Clave configurada</p>
              )}
            </div>
          )}
        </div>

        {/* Usuario + timer + logout */}
        <div className="px-4 py-4 border-t border-slate-700">
          <div className="text-xs text-slate-300 font-medium truncate mb-0.5">{user?.username}</div>
          <div className="text-xs text-slate-600 mb-0.5">{user?.role}</div>
          {user?.education_level && (
            <div className="text-xs text-slate-600 mb-1">
              {user.education_level}
              {user.grade ? ` · Grado ${user.grade}` : ""}
            </div>
          )}
          {/* Email */}
          {user && !user.email && !showEmailForm && (
            <button
              onClick={() => setShowEmailForm(true)}
              className="w-full text-left text-xs bg-amber-500/10 text-amber-400 rounded px-2 py-1.5 mb-2 hover:bg-amber-500/20 transition-colors"
            >
              Agrega tu correo para no perder acceso
            </button>
          )}
          {user?.email && !showEmailForm && (
            <div className="flex items-center gap-1 mb-2">
              <span className="text-xs text-slate-600 truncate">{maskedEmail}</span>
              <button
                onClick={() => { setShowEmailForm(true); setEmailInput(""); setEmailError(""); }}
                className="text-xs text-violet-400 hover:text-violet-300 shrink-0"
              >
                Cambiar
              </button>
            </div>
          )}
          {showEmailForm && (
            <div className="mb-2 space-y-1">
              <input
                type="email"
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                placeholder="correo@ejemplo.com"
                className="w-full bg-slate-900 border border-slate-600 rounded text-xs text-slate-300 px-2 py-1 focus:outline-none focus:border-violet-500 placeholder-slate-600"
              />
              {emailError && <p className="text-xs text-red-400">{emailError}</p>}
              <div className="flex gap-1">
                <button
                  onClick={handleSaveEmail}
                  disabled={emailSaving}
                  className="flex-1 text-xs bg-violet-600 hover:bg-violet-500 text-white rounded px-2 py-1 disabled:opacity-50"
                >
                  {emailSaving ? "..." : "Guardar"}
                </button>
                <button
                  onClick={() => setShowEmailForm(false)}
                  className="text-xs text-slate-500 hover:text-slate-400 px-2 py-1"
                >
                  Cancelar
                </button>
              </div>
            </div>
          )}
          {/* Timer de sesión global */}
          {user?.role === "student" && (
            <div className="flex items-center gap-1.5 mb-3 bg-slate-900 rounded-lg px-2 py-1">
              <span className="text-slate-500 text-xs">⏱</span>
              <span className="text-slate-400 text-xs font-mono">{sessionFormatted}</span>
              <span className="text-slate-600 text-xs ml-auto">sesión</span>
            </div>
          )}
          {user?.role === "student" && (
            <div className="mb-2">
              <ReportProblemButton />
            </div>
          )}
          <button
            onClick={handleLogout}
            className="text-xs text-slate-500 hover:text-red-400 transition-colors"
          >
            Cerrar sesión →
          </button>
        </div>
      </aside>

      {/* Contenido */}
      <main className="flex-1 overflow-y-auto pb-16 md:pb-0">
        <AnimatePresence mode="wait">
          <PageTransition key={location.pathname}>{children}</PageTransition>
        </AnimatePresence>
      </main>

      {/* Bottom nav móvil */}
      <nav className="md:hidden fixed bottom-0 inset-x-0 bg-slate-800 border-t border-slate-700 flex justify-around items-stretch z-30">
        {navItems.map((item) => {
          const active = location.pathname === item.path;
          const isProcedures = item.path.includes("procedures");
          const showBadge = isProcedures && unreadCount > 0;
          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => {
                if (isProcedures) clearUnread();
              }}
              aria-current={active ? "page" : undefined}
              aria-label={showBadge ? `${item.label}, ${unreadCount > 9 ? "más de 9" : unreadCount} notificaciones` : item.label}
              className={[
                "relative flex-1 flex flex-col items-center justify-center gap-0.5 py-2 text-[10px] transition-colors",
                active ? "text-violet-300" : "text-slate-400 hover:text-slate-200",
              ].join(" ")}
            >
              <span className="text-lg leading-none" aria-hidden="true">{item.icon}</span>
              <span className="truncate max-w-full px-1" aria-hidden="true">{item.label}</span>
              {showBadge && (
                <span
                  className="absolute top-1 right-1/4 bg-red-500 text-white text-[9px] font-bold rounded-full min-w-[16px] h-[16px] flex items-center justify-center px-1"
                  aria-hidden="true"
                >
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
