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
import { useSettingsStore } from "../../stores/settingsStore";
import { resetClientAccountState } from "../../lib/accountCleanup";
import { useSideDrawer } from "../../hooks/useSideDrawer";
import { MobileBar } from "../../components/Layout/MobileBar";
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
  const { apiKey, setApiKey } = useSettingsStore();

  const [aiOpen, setAiOpen] = useState(false);
  const { open: menuOpen, setOpen: setMenuOpen, closeRef, closeOnLink } = useSideDrawer();
  const lang = i18n.language?.startsWith("en") ? "en" : "es";

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch {
      /* ignorar */
    }
    await resetClientAccountState(queryClient);
    clearAuth();
    navigate("/login");
  };

  const toggleLang = () => i18n.changeLanguage(lang === "es" ? "en" : "es");

  return (
    <div className="lue-tc">
      <MobileBar home="/teacher" open={menuOpen} onOpen={() => setMenuOpen(true)} />
      {menuOpen && <div className="tc-scrim" aria-hidden="true" onClick={() => setMenuOpen(false)} />}
      <aside id="tc-side" className={"tc-side" + (menuOpen ? " open" : "")} onClick={closeOnLink}>
        <button
          ref={closeRef}
          type="button"
          className="tc-side-close"
          aria-label="Cerrar menú"
          onClick={() => setMenuOpen(false)}
        >
          ✕
        </button>
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
            <div className="ava">{initials(user?.display_name || user?.username || "?")}</div>
            <div className="meta">
              <b>{user?.display_name || user?.username}</b>
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
          {/* Spec 004 FR-026: el propio usuario cambia su contraseña. */}
          <button className="tc-logout" onClick={() => navigate("/cambiar-contrasena")}>
            Cambiar contraseña
          </button>
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
