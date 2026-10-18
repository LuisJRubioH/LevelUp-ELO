/**
 * pages/ChangePassword.tsx
 * ========================
 * Spec 004 E2 (FR-026, FR-028, FR-030): the signed-in user changes their password. Forced when
 * the account entered with a temporary password; voluntary otherwise. The API ends every other
 * session and returns new credentials for this one.
 */

import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { authApi } from "../api/auth";
import { useAuthStore } from "../stores/authStore";
import { resetClientAccountState } from "../lib/accountCleanup";
import { useQueryClient } from "@tanstack/react-query";
import "./Login.css";
import "./ChangePassword.css";

const MIN_LENGTH = 6;

function homeFor(role: string | undefined): string {
  return role === "teacher" ? "/teacher" : role === "admin" ? "/admin" : "/student";
}

export function ChangePassword() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const forced = useAuthStore((s) => s.mustChangePassword);
  const updateAccessToken = useAuthStore((s) => s.updateAccessToken);
  const setMustChangePassword = useAuthStore((s) => s.setMustChangePassword);
  const clearAuth = useAuthStore((s) => s.clearAuth);

  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [repeat, setRepeat] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    if (next.trim().length < MIN_LENGTH) {
      setError(`La nueva contraseña debe tener al menos ${MIN_LENGTH} caracteres.`);
      return;
    }
    if (next !== repeat) {
      setError("Las contraseñas nuevas no coinciden.");
      return;
    }
    setLoading(true);
    try {
      const res = await authApi.changePassword({ current_password: current, new_password: next });
      updateAccessToken(res.access_token);
      setMustChangePassword(false);
      navigate(homeFor(user?.role), { replace: true });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "No se pudo cambiar la contraseña.");
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch {
      /* ignorar */
    }
    await resetClientAccountState(queryClient);
    clearAuth();
    navigate("/login", { replace: true });
  };

  return (
    <div className="lue-auth pw-change">
      <motion.div
        className={`pw-card${forced ? " forced" : ""}`}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
      >
        <form className="auth-form" onSubmit={submit} data-testid="change-password-form">
          <span className="auth-eyebrow">{forced ? "Contraseña temporal" : "Tu cuenta"}</span>
          <h1 className="auth-title">
            Cambia tu <span className="em">contraseña</span>.
          </h1>
          <p className="auth-sub">
            {forced
              ? "Entraste con una contraseña temporal. Elige una propia para continuar."
              : "Al cambiarla se cierran tus otras sesiones abiertas."}
          </p>
          <div className="fields">
            <PasswordField
              label={forced ? "Contraseña temporal" : "Contraseña actual"}
              value={current}
              onChange={setCurrent}
              autoComplete="current-password"
            />
            <PasswordField
              label="Nueva contraseña"
              value={next}
              onChange={setNext}
              autoComplete="new-password"
            />
            <PasswordField
              label="Repite la nueva contraseña"
              value={repeat}
              onChange={setRepeat}
              autoComplete="new-password"
            />
          </div>
          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? "Guardando…" : "Guardar contraseña"}
          </button>
          {error && (
            <div className="auth-msg error" role="alert">
              {error}
            </div>
          )}
          <div className="pw-actions">
            {forced ? (
              <span />
            ) : (
              <button type="button" onClick={() => navigate(-1)}>
                ← Volver
              </button>
            )}
            <button type="button" onClick={logout}>
              Cerrar sesión
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}

function PasswordField({
  label,
  value,
  onChange,
  autoComplete,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  autoComplete: string;
}) {
  const id = `pw-${label.replace(/\s+/g, "-").toLowerCase()}`;
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <div className="input-wrap">
        <span className="lead">🔒</span>
        <input
          id={id}
          type="password"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required
          autoComplete={autoComplete}
        />
      </div>
    </div>
  );
}
