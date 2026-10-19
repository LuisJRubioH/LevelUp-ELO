/**
 * pages/DisplayName.tsx
 * =====================
 * Spec 004 E2 (FR-020, FR-025): the student changes the name classmates and teachers see. The
 * server applies the name filter and records the change; its refusal is shown as given.
 */

import { useId, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { studentApi } from "../api/student";
import { useAuthStore } from "../stores/authStore";
import "./Login.css";
import "./ChangePassword.css";

export function DisplayName() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);
  const inputId = useId();

  const [name, setName] = useState(user?.display_name ?? "");
  const [error, setError] = useState("");
  const [saved, setSaved] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setSaved(null);
    setLoading(true);
    try {
      const res = await studentApi.changeDisplayName(name);
      updateUser({ display_name: res.display_name });
      setName(res.display_name);
      setSaved(res.display_name);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "No se pudo guardar el nombre.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="lue-auth pw-change">
      <motion.div
        className="pw-card"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
      >
        <form className="auth-form" onSubmit={submit} data-testid="display-name-form">
          <span className="auth-eyebrow">Tu cuenta</span>
          <h1 className="auth-title">
            Tu <span className="em">nombre</span>.
          </h1>
          <p className="auth-sub">
            Así te ven tus compañeros en el ranking y en la liga, y tu docente en su panel. Tu
            usuario para entrar no cambia.
          </p>
          <div className="fields">
            <div className="field">
              <label htmlFor={inputId}>Tu nombre</label>
              <div className="input-wrap">
                <span className="lead">🪪</span>
                <input
                  id={inputId}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  minLength={2}
                  maxLength={80}
                  autoComplete="name"
                  placeholder={user?.username}
                />
              </div>
            </div>
          </div>
          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? "Guardando…" : "Guardar nombre"}
          </button>
          {error && (
            <div className="auth-msg error" role="alert">
              {error}
            </div>
          )}
          {saved && (
            <div className="auth-msg info" role="status">
              Listo: ahora te ven como «{saved}».
            </div>
          )}
          <div className="pw-actions">
            <button type="button" onClick={() => navigate(-1)}>
              ← Volver
            </button>
            <span />
          </div>
        </form>
      </motion.div>
    </div>
  );
}
