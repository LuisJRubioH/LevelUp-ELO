/**
 * pages/Layout.tsx
 * ================
 * Layout base con sidebar de navegación por rol.
 * Los hijos se renderizan en el área de contenido central.
 */

import { useState } from "react";
import type { ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { authApi } from "../api/auth";
import { useAuthStore } from "../stores/authStore";
import { useSettingsStore } from "../stores/settingsStore";

interface NavItem {
  path: string;
  label: string;
  icon: string;
}

const studentNav: NavItem[] = [
  { path: "/student", label: "Practicar", icon: "🎯" },
  { path: "/student/stats", label: "Estadísticas", icon: "📈" },
  { path: "/student/courses", label: "Cursos", icon: "📚" },
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
];

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { user, clearAuth } = useAuthStore();
  const { apiKey, provider, setApiKey, setProvider } = useSettingsStore();
  const location = useLocation();
  const navigate = useNavigate();
  const [showIAConfig, setShowIAConfig] = useState(false);

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
    <div className="flex h-screen bg-slate-900 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-56 bg-slate-800 border-r border-slate-700 flex flex-col shrink-0">
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
            return (
              <Link
                key={item.path}
                to={item.path}
                className={[
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all",
                  active
                    ? "bg-violet-600/30 text-violet-300 font-medium"
                    : "text-slate-400 hover:bg-slate-700 hover:text-slate-200",
                ].join(" ")}
              >
                <span>{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Config IA */}
        <div className="px-4 py-3 border-t border-slate-700">
          <button
            onClick={() => setShowIAConfig((v) => !v)}
            className="flex items-center justify-between w-full text-xs text-slate-400 hover:text-slate-200 transition-colors"
          >
            <span>🤖 API de IA</span>
            <span>{showIAConfig ? "▲" : "▼"}</span>
          </button>
          {showIAConfig && (
            <div className="mt-2 space-y-2">
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

        {/* Usuario + logout */}
        <div className="px-4 py-4 border-t border-slate-700">
          <div className="text-xs text-slate-400 truncate mb-2">{user?.username}</div>
          <div className="text-xs text-slate-600 mb-3">{user?.role}</div>
          <button
            onClick={handleLogout}
            className="text-xs text-slate-500 hover:text-red-400 transition-colors"
          >
            Cerrar sesión →
          </button>
        </div>
      </aside>

      {/* Contenido */}
      <main className="flex-1 overflow-y-auto">{children}</main>
    </div>
  );
}
