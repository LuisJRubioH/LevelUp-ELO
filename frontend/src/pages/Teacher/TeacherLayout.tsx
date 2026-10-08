/**
 * pages/Teacher/TeacherLayout.tsx
 * ===============================
 * Shell de la Consola Docente (rediseño) — portado de
 * docs/redesign/source/teacher-shell.jsx + teacher.css.
 *
 * Reemplaza el Layout compartido SOLO para las rutas /teacher/*.
 * Sidebar propio (marca, navegación, widget de IA, footer con usuario,
 * tema, idioma y logout) cableado a los stores/handlers reales.
 * Estilos en TeacherConsole.css (scopeados bajo .lue-tc).
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
import { clearAccountCaches } from "../../lib/accountCleanup";
import "./TeacherConsole.css";

const NAV = [
  { path: "/teacher", label: "Dashboard", ic: "▦" },
  { path: "/teacher/groups", label: "Grupos", ic: "👥" },
  { path: "/teacher/procedures", label: "Procedimientos", ic: "📝" },
  { path: "/teacher/exams", label: "Exámenes", ic: "📋" },
  { path: "/teacher/export", label: "Exportar datos", ic: "📤" },
];

function initials(name: string): string {
  return name.slice(0, 2).toUpperCase();
}

export function TeacherLayout({ children }: { children: ReactNode }) {
  const { i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const user = useAuthStore((s) => s.user);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const queryClient = useQueryClient();
  const { theme, toggleTheme } = useThemeStore();
  const { apiKey, provider, model, setApiKey, setProvider, setModel } = useSettingsStore();
  const availableModels = PROVIDER_MODELS[provider] ?? [];

  const [aiOpen, setAiOpen] = useState(false);
  const lang = i18n.language?.startsWith("en") ? "en" : "es";

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch {
      /* ignorar */
    }
    await clearAccountCaches();
    queryClient.clear();
    setApiKey("");
    clearAuth();
    navigate("/login");
  };

  const toggleLang = () => i18n.changeLanguage(lang === "es" ? "en" : "es");

  return (
    <div className="lue-tc">
      <aside className="tc-side">
        <div className="tc-brand">
          <Link to="/teacher" aria-label="Oulad">
            <img className="brand-logo brand-logo-dark" src="/oulad-logo-dark.png" alt="Oulad" />
            <img className="brand-logo brand-logo-light" src="/oulad-logo-light.png" alt="Oulad" />
          </Link>
          <span className="tag">MOTOR ELO · CONSOLA DOCENTE</span>
        </div>

        <nav className="tc-nav">
          {NAV.map((n) => {
            const active = location.pathname === n.path;
            return (
              <Link key={n.path} to={n.path} className={"nav-item" + (active ? " on" : "")}>
                <span className="ic">{n.ic}</span>
                {n.label}
              </Link>
            );
          })}

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
              <select
                className="ai-input"
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                aria-label="Proveedor de IA"
              >
                <option value="groq">Groq</option>
                <option value="anthropic">Anthropic</option>
                <option value="openai">OpenAI</option>
                <option value="google">Google Gemini</option>
              </select>
              {availableModels.length > 0 && (
                <select
                  className="ai-input"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  aria-label="Modelo de IA"
                >
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
                <span className="role">Docente</span>
                {user?.education_level ? ` · ${user.education_level}` : ""}
              </span>
            </div>
          </div>
          <div className="tc-toggles">
            <button className="tc-tog" onClick={toggleTheme}>
              {theme === "light" ? "🌙 Modo oscuro" : "☀️ Modo claro"}
            </button>
            <button className="tc-tog" onClick={toggleLang}>
              🌐 {lang.toUpperCase()}
            </button>
          </div>
          <button className="tc-logout" onClick={handleLogout}>
            Cerrar sesión →
          </button>
        </div>
      </aside>

      <main className="tc-main">
        <div className="tc-main-inner">{children}</div>
      </main>
    </div>
  );
}
