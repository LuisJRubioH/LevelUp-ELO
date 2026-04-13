/**
 * pages/Login.tsx
 * ================
 * Página de login con wizard de registro en dos pasos.
 * Paso 1: selección de rol (Estudiante / Docente)
 * Paso 2: datos de cuenta
 */

import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../api/auth";
import { Button } from "../components/ui/Button";
import { useAuthStore } from "../stores/authStore";
import type { AuthUser } from "../stores/authStore";

type View = "login" | "register-role" | "register-form";

export function Login() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const [view, setView] = useState<View>("login");
  const [selectedRole, setSelectedRole] = useState<"student" | "teacher">("student");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Login form
  const [loginData, setLoginData] = useState({ username: "", password: "" });

  // Register form
  const [regData, setRegData] = useState({
    username: "",
    password: "",
    education_level: "colegio" as "universidad" | "colegio" | "semillero",
    grade: "9",
  });

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await authApi.login(loginData);
      const profile = await authApi.me();
      setAuth(res.access_token, profile as AuthUser);
      navigate(res.role === "teacher" ? "/teacher" : res.role === "admin" ? "/admin" : "/student");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Credenciales inválidas.");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await authApi.register({
        ...regData,
        role: selectedRole,
        grade: regData.education_level === "semillero" ? regData.grade : undefined,
      });
      // Auto-login tras registro
      const res = await authApi.login({
        username: regData.username,
        password: regData.password,
      });
      const profile = await authApi.me();
      setAuth(res.access_token, profile as AuthUser);
      if (selectedRole === "teacher") {
        // Docente pendiente de aprobación
        setView("login");
        setError("Registro exitoso. Tu cuenta de docente está pendiente de aprobación.");
      } else {
        navigate("/student");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error al registrarse.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white">
            Level<span className="text-violet-400">Up</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">Plataforma educativa adaptativa con ELO</p>
        </div>

        <div className="bg-slate-800 rounded-2xl p-8 border border-slate-700 shadow-2xl">
          {/* ── LOGIN ─────────────────────────────────────────────── */}
          {view === "login" && (
            <form onSubmit={handleLogin} className="space-y-4">
              <h2 className="text-xl font-semibold text-white mb-6">Iniciar sesión</h2>

              <div>
                <label className="block text-sm text-slate-400 mb-1">Usuario</label>
                <input
                  type="text"
                  value={loginData.username}
                  onChange={(e) => setLoginData((d) => ({ ...d, username: e.target.value }))}
                  className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-violet-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Contraseña</label>
                <input
                  type="password"
                  value={loginData.password}
                  onChange={(e) => setLoginData((d) => ({ ...d, password: e.target.value }))}
                  className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-violet-500"
                  required
                />
              </div>

              {error && <p className="text-red-400 text-sm">{error}</p>}

              <Button type="submit" className="w-full" loading={loading} size="lg">
                Entrar
              </Button>

              <p className="text-center text-sm text-slate-500">
                ¿Sin cuenta?{" "}
                <button
                  type="button"
                  onClick={() => { setView("register-role"); setError(""); }}
                  className="text-violet-400 hover:text-violet-300"
                >
                  Registrarse
                </button>
              </p>
            </form>
          )}

          {/* ── REGISTRO PASO 1: ROL ──────────────────────────────── */}
          {view === "register-role" && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-white mb-2">¿Quién eres?</h2>
              <p className="text-slate-400 text-sm mb-6">Selecciona tu rol en la plataforma.</p>

              <div className="grid grid-cols-2 gap-4">
                {(["student", "teacher"] as const).map((role) => (
                  <button
                    key={role}
                    type="button"
                    onClick={() => setSelectedRole(role)}
                    className={[
                      "p-6 rounded-xl border-2 transition-all",
                      selectedRole === role
                        ? "border-violet-500 bg-violet-900/30"
                        : "border-slate-600 bg-slate-800 hover:border-slate-500",
                    ].join(" ")}
                  >
                    <div className="text-2xl mb-2">{role === "student" ? "🎓" : "👨‍🏫"}</div>
                    <div className="text-sm font-medium text-white">
                      {role === "student" ? "Estudiante" : "Docente"}
                    </div>
                  </button>
                ))}
              </div>

              <Button
                className="w-full"
                size="lg"
                onClick={() => setView("register-form")}
              >
                Continuar →
              </Button>

              <button
                type="button"
                onClick={() => setView("login")}
                className="w-full text-center text-sm text-slate-500 hover:text-slate-400"
              >
                ← Volver al login
              </button>
            </div>
          )}

          {/* ── REGISTRO PASO 2: DATOS ────────────────────────────── */}
          {view === "register-form" && (
            <form onSubmit={handleRegister} className="space-y-4">
              <h2 className="text-xl font-semibold text-white mb-2">
                Crear cuenta de {selectedRole === "student" ? "estudiante" : "docente"}
              </h2>

              <div>
                <label className="block text-sm text-slate-400 mb-1">Nombre de usuario</label>
                <input
                  type="text"
                  value={regData.username}
                  onChange={(e) => setRegData((d) => ({ ...d, username: e.target.value }))}
                  minLength={3}
                  className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-violet-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Contraseña</label>
                <input
                  type="password"
                  value={regData.password}
                  onChange={(e) => setRegData((d) => ({ ...d, password: e.target.value }))}
                  minLength={6}
                  className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-violet-500"
                  required
                />
              </div>

              {selectedRole === "student" && (
                <div>
                  <label className="block text-sm text-slate-400 mb-1">Nivel educativo</label>
                  <select
                    value={regData.education_level}
                    onChange={(e) =>
                      setRegData((d) => ({
                        ...d,
                        education_level: e.target.value as typeof regData.education_level,
                      }))
                    }
                    className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-violet-500"
                  >
                    <option value="colegio">Colegio</option>
                    <option value="universidad">Universidad</option>
                    <option value="semillero">Semillero</option>
                  </select>
                </div>
              )}

              {selectedRole === "student" && regData.education_level === "semillero" && (
                <div>
                  <label className="block text-sm text-slate-400 mb-1">Grado</label>
                  <select
                    value={regData.grade}
                    onChange={(e) => setRegData((d) => ({ ...d, grade: e.target.value }))}
                    className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-violet-500"
                  >
                    {["6", "7", "8", "9", "10", "11"].map((g) => (
                      <option key={g} value={g}>
                        Grado {g}°
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {error && <p className="text-red-400 text-sm">{error}</p>}

              <Button type="submit" className="w-full" size="lg" loading={loading}>
                Registrarse
              </Button>

              <button
                type="button"
                onClick={() => setView("register-role")}
                className="w-full text-center text-sm text-slate-500 hover:text-slate-400"
              >
                ← Volver
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
