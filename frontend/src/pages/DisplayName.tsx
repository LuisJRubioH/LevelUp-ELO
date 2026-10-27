/**
 * pages/DisplayName.tsx
 * =====================
 * Spec 004 E2 (FR-020, FR-025): the student changes the name classmates and teachers see. The
 * server applies the name filter and records the change; its refusal is shown as given.
 * Spec 009 I1: the student sees their own linked identification (FR-013), and the name of an
 * account of the initial import is shown read only — the admin changes it (FR-014).
 */

import { useId, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { authApi } from "../api/auth";
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
  const { data: profile } = useQuery({ queryKey: ["me"], queryFn: authApi.me });
  const locked = profile?.display_name_locked === true;

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
          {profile?.identification ? (
            <p className="auth-sub" data-testid="own-identification">
              Tu número de documento: <strong>{profile.identification}</strong>. Solo tú y el
              administrador lo ven.
            </p>
          ) : null}
          <div className="fields">
            <div className="field">
              <label htmlFor={inputId}>Tu nombre</label>
              <div className="input-wrap">
                <span className="lead">🪪</span>
                <input
                  id={inputId}
                  value={locked ? (profile?.display_name ?? name) : name}
                  onChange={(e) => setName(e.target.value)}
                  readOnly={locked}
                  required
                  minLength={2}
                  maxLength={80}
                  autoComplete="name"
                  placeholder={user?.username}
                />
              </div>
            </div>
          </div>
          {locked ? (
            <div className="auth-msg info" role="note">
              Tu nombre lo cambia el administrador.
            </div>
          ) : (
            <button type="submit" className="auth-submit" disabled={loading}>
              {loading ? "Guardando…" : "Guardar nombre"}
            </button>
          )}
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
