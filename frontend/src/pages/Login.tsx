/**
 * pages/Login.tsx
 * ================
 * Pantalla de acceso (rediseño) — variante split-screen portada de
 * docs/redesign/source/Oulad Auth.html (auth-parts.jsx + auth-variations.jsx).
 *
 * - Estilos en Login.css, scopeados bajo .lue-auth (tokens propios del
 *   rediseño; tema claro vía html.light). Marca real LevelUp (logo).
 * - Cableado al backend real: authApi.login / register / me + authStore.
 * - i18n local ES/EN sincronizada con la clave "levelup-lang".
 *
 * Notas: el login social (Google/Microsoft) y "¿olvidaste tu contraseña?"
 * no tienen backend todavía — se muestran (fidelidad al diseño) pero
 * deshabilitados/no operativos para no prometer lo que no existe.
 */

import { useId, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../api/auth";
import { studentApi } from "../api/student";
import { useAuthStore } from "../stores/authStore";
import type { AuthUser } from "../stores/authStore";
import "./Login.css";

const KATIA_GIF = "/katia/correcto_compressed.gif";
const LS_LANG = "levelup-lang";

type Lang = "es" | "en";
type Mode = "login" | "signup";
type Role = "student" | "teacher";
/** Nivel del diseño → education_level del backend (secundaria = colegio). */
type DesignLevel = "secundaria" | "universidad" | "semillero" | "concursos";
type Bi = { es: string; en: string };

const LEVEL_MAP: Record<DesignLevel, "colegio" | "universidad" | "semillero" | "concursos"> = {
  secundaria: "colegio",
  universidad: "universidad",
  semillero: "semillero",
  concursos: "concursos",
};

function GoogleIcon() {
  return (
    <svg viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.9 29.3 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.3 6.1 29.4 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.3-.4-3.5z" />
      <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 16 19 13 24 13c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.3 6.1 29.4 4 24 4 16.3 4 9.7 8.3 6.3 14.7z" />
      <path fill="#4CAF50" d="M24 44c5.2 0 10-2 13.6-5.2l-6.3-5.3C29.2 35 26.7 36 24 36c-5.3 0-9.7-3.1-11.3-7.5l-6.5 5C9.6 39.6 16.2 44 24 44z" />
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.1-4 5.5l6.3 5.3C41.2 36.4 44 30.8 44 24c0-1.3-.1-2.3-.4-3.5z" />
    </svg>
  );
}
function MicrosoftIcon() {
  return (
    <svg viewBox="0 0 23 23" aria-hidden="true">
      <path fill="#F25022" d="M1 1h10v10H1z" />
      <path fill="#7FBA00" d="M12 1h10v10H12z" />
      <path fill="#00A4EF" d="M1 12h10v10H1z" />
      <path fill="#FFB900" d="M12 12h10v10H12z" />
    </svg>
  );
}

interface FieldProps {
  label: string;
  lead?: string;
  type?: string;
  placeholder?: string;
  value: string;
  onChange: (v: string) => void;
  optional?: string;
  required?: boolean;
  autoComplete?: string;
  minLength?: number;
  showLabel: Bi;
  hideLabel: Bi;
  lang: Lang;
}

function Field({
  label,
  lead,
  type = "text",
  placeholder,
  value,
  onChange,
  optional,
  required,
  autoComplete,
  minLength,
  showLabel,
  hideLabel,
  lang,
}: FieldProps) {
  const inputId = useId();
  const [show, setShow] = useState(false);
  const isPw = type === "password";
  return (
    <div className="field">
      <label htmlFor={inputId}>
        {label}
        {optional ? <span className="opt">· {optional}</span> : null}
      </label>
      <div className="input-wrap">
        {lead ? <span className="lead">{lead}</span> : null}
        <input
          id={inputId}
          type={isPw && show ? "text" : type}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required={required}
          autoComplete={autoComplete}
          minLength={minLength}
        />
        {isPw ? (
          <button type="button" className="reveal-pw" onClick={() => setShow((s) => !s)}>
            {show ? (lang === "es" ? hideLabel.es : hideLabel.en) : lang === "es" ? showLabel.es : showLabel.en}
          </button>
        ) : null}
      </div>
    </div>
  );
}

export function Login() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const [lang, setLang] = useState<Lang>(() => ((localStorage.getItem(LS_LANG) as Lang) || "es"));
  const t = (b: Bi) => (lang === "es" ? b.es : b.en);
  const switchLang = (l: Lang) => {
    setLang(l);
    localStorage.setItem(LS_LANG, l);
    document.documentElement.lang = l;
  };

  const [mode, setMode] = useState<Mode>("login");
  const [role, setRole] = useState<Role>("student");
  const [level, setLevel] = useState<DesignLevel>("secundaria");
  const [grade, setGrade] = useState("9");

  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);

  // login
  const [loginUser, setLoginUser] = useState("");
  const [loginPw, setLoginPw] = useState("");

  // signup
  const [suName, setSuName] = useState("");
  const [suEmail, setSuEmail] = useState("");
  const [suPw, setSuPw] = useState("");
  const [suPw2, setSuPw2] = useState("");
  const [suCode, setSuCode] = useState("");
  const [terms, setTerms] = useState(true);

  const resetMsgs = () => {
    setError("");
    setInfo("");
  };
  const changeMode = (m: Mode) => {
    setMode(m);
    resetMsgs();
  };

  const finishLogin = async (username: string, password: string) => {
    const res = await authApi.login({ username, password });
    setAuth(res.access_token, {
      user_id: res.user_id,
      username: res.username,
      role: res.role as AuthUser["role"],
      education_level: null,
      grade: null,
      email: null,
    });
    const profile = await authApi.me();
    setAuth(res.access_token, profile as AuthUser);
    return res;
  };

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    resetMsgs();
    setLoading(true);
    try {
      const res = await finishLogin(loginUser, loginPw);
      navigate(res.role === "teacher" ? "/teacher" : res.role === "admin" ? "/admin" : "/student");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : t({ es: "Credenciales inválidas.", en: "Invalid credentials." }));
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e: FormEvent) => {
    e.preventDefault();
    resetMsgs();
    if (suPw !== suPw2) {
      setError(t({ es: "Las contraseñas no coinciden.", en: "Passwords don't match." }));
      return;
    }
    if (!terms) {
      setError(t({ es: "Debes aceptar los términos.", en: "You must accept the terms." }));
      return;
    }
    setLoading(true);
    try {
      const eduLevel = LEVEL_MAP[level];
      await authApi.register({
        username: suName,
        password: suPw,
        email: suEmail || undefined,
        role,
        education_level: role === "student" ? eduLevel : undefined,
        grade: role === "student" && eduLevel === "semillero" ? grade : undefined,
      });
      if (role === "teacher") {
        changeMode("login");
        setInfo(
          t({
            es: "Registro exitoso. Tu cuenta de docente está pendiente de aprobación.",
            en: "Registration successful. Your teacher account is pending approval.",
          })
        );
        return;
      }
      // estudiante: login + (best-effort) inscripción por código de clase
      await finishLogin(suName, suPw);
      if (suCode.trim()) {
        try {
          await studentApi.enrollByCode(suCode.trim());
        } catch {
          /* código inválido: no bloquea el registro, el alumno puede usarlo luego */
        }
      }
      navigate("/student");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : t({ es: "Error al registrarse.", en: "Sign up failed." }));
    } finally {
      setLoading(false);
    }
  };

  const showPw: Bi = { es: "ver", en: "show" };
  const hidePw: Bi = { es: "ocultar", en: "hide" };

  return (
    <div className="lue-auth" lang={lang}>
      <div className="auth-bg">
        <div className="grid" />
      </div>
      <div className="split">
        {/* ── PANEL MARCA ─────────────────────────────────────────── */}
        <aside className="brand-panel">
          <div className="pbg">
            <span
              style={{
                position: "absolute",
                width: 360,
                height: 360,
                borderRadius: "50%",
                filter: "blur(90px)",
                background: "var(--glow-a)",
                top: -120,
                left: -90,
              }}
            />
          </div>
          <a href="/" aria-label="Oulad">
            <img className="auth-logo auth-logo-dark" src="/oulad-logo-dark.png" alt="Oulad" />
            <img className="auth-logo auth-logo-light" src="/oulad-logo-light.png" alt="Oulad" />
          </a>
          <h2 className="brand-h">
            {t({ es: "Las matemáticas tienen rango.", en: "Math has a rank." })}{" "}
            <span className="em">{t({ es: "Sube el tuyo.", en: "Climb yours." })}</span>
          </h2>
          <div className="brand-katia">
            <div className="katia-card" style={{ marginBottom: 20 }}>
              <div className="hud">
                <span className="fdot" style={{ background: "#ff5f57" }} />
                <span className="fdot" style={{ background: "#febc2e" }} />
                <span className="fdot" style={{ background: "#28c840" }} />
                <span className="lbl">KATIA.EXE</span>
              </div>
              <img src={KATIA_GIF} alt="KatIA, tutora socrática pixel-art" />
              <div className="scan" />
              <div className="nameplate">
                <div className="who">
                  KatIA<small>{t({ es: "Tutora socrática", en: "Socratic tutor" })}</small>
                </div>
                <div className="hpbar">
                  <div className="t">XP 72%</div>
                  <div className="bar">
                    <i style={{ width: "72%" }} />
                  </div>
                </div>
              </div>
            </div>
            <div className="brand-stats">
              <div>
                <div className="n">
                  <span className="a">+1.900</span>
                </div>
                <div className="l">{t({ es: "preguntas", en: "questions" })}</div>
              </div>
              <div>
                <div className="n">16</div>
                <div className="l">{t({ es: "rangos", en: "ranks" })}</div>
              </div>
              <div>
                <div className="n">10+</div>
                <div className="l">{t({ es: "materias", en: "subjects" })}</div>
              </div>
            </div>
          </div>
        </aside>

        {/* ── PANEL FORMULARIO ────────────────────────────────────── */}
        <main className="form-panel">
          <div className="form-scroll">
            <div className="form-topbar">
              <div className="auth-tabs" role="tablist">
                <button className={mode === "login" ? "on" : ""} onClick={() => changeMode("login")}>
                  {t({ es: "Iniciar sesión", en: "Log in" })}
                </button>
                <button className={mode === "signup" ? "on" : ""} onClick={() => changeMode("signup")}>
                  {t({ es: "Crear cuenta", en: "Sign up" })}
                </button>
              </div>
              <span className="auth-lang" role="group" aria-label="Idioma">
                <button className={lang === "es" ? "on" : ""} onClick={() => switchLang("es")}>
                  ES
                </button>
                <button className={lang === "en" ? "on" : ""} onClick={() => switchLang("en")}>
                  EN
                </button>
              </span>
            </div>

            <form className="auth-form" onSubmit={mode === "login" ? handleLogin : handleSignup}>
              <span className="auth-eyebrow">
                {t(
                  mode === "login"
                    ? { es: "Bienvenido de vuelta", en: "Welcome back" }
                    : { es: "Únete a Oulad", en: "Join Oulad" }
                )}
              </span>
              <h1 className="auth-title">
                {mode === "login" ? (
                  <>
                    {t({ es: "Continúa tu ", en: "Continue your " })}
                    <span className="em">{t({ es: "ascenso", en: "climb" })}</span>.
                  </>
                ) : (
                  <>
                    {t({ es: "Crea tu ", en: "Create your " })}
                    <span className="em">{t({ es: "cuenta", en: "account" })}</span>.
                  </>
                )}
              </h1>
              <p className="auth-sub">
                {t(
                  mode === "login"
                    ? {
                        es: "Tu ELO, tus rangos y KatIA te están esperando.",
                        en: "Your ELO, your ranks and KatIA are waiting for you.",
                      }
                    : {
                        es: "Configura tu perfil y deja que el motor ELO encuentre tu reto perfecto.",
                        en: "Set up your profile and let the ELO engine find your perfect challenge.",
                      }
                )}
              </p>

              {mode === "login" ? (
                <>
                  <div className="fields">
                    <Field
                      label={t({ es: "Usuario o correo", en: "Username or email" })}
                      lead="@"
                      placeholder={t({ es: "ada.mateus  ·  tu@correo.com", en: "ada.mateus  ·  you@email.com" })}
                      value={loginUser}
                      onChange={setLoginUser}
                      required
                      autoComplete="username"
                      showLabel={showPw}
                      hideLabel={hidePw}
                      lang={lang}
                    />
                    <Field
                      label={t({ es: "Contraseña", en: "Password" })}
                      lead="🔒"
                      type="password"
                      placeholder="••••••••"
                      value={loginPw}
                      onChange={setLoginPw}
                      required
                      autoComplete="current-password"
                      showLabel={showPw}
                      hideLabel={hidePw}
                      lang={lang}
                    />
                  </div>
                  <div className="auth-row">
                    <label className="check">
                      <input type="checkbox" />
                      <span className="box" />
                      {t({ es: "Recordarme", en: "Remember me" })}
                    </label>
                    <button
                      type="button"
                      className="link-forgot"
                      title={t({ es: "Próximamente", en: "Coming soon" })}
                      onClick={() =>
                        setInfo(
                          t({
                            es: "Recuperación de contraseña: próximamente. Contacta a tu docente o admin.",
                            en: "Password recovery: coming soon. Contact your teacher or admin.",
                          })
                        )
                      }
                    >
                      {t({ es: "¿Olvidaste tu contraseña?", en: "Forgot password?" })}
                    </button>
                  </div>
                </>
              ) : (
                <div className="fields">
                  <Field
                    label={t({ es: "Nombre de usuario", en: "Username" })}
                    lead="👤"
                    placeholder="ada.mateus"
                    value={suName}
                    onChange={setSuName}
                    required
                    minLength={3}
                    autoComplete="username"
                    showLabel={showPw}
                    hideLabel={hidePw}
                    lang={lang}
                  />
                  <Field
                    label={t({ es: "Correo", en: "Email" })}
                    lead="✉"
                    type="email"
                    optional={t({ es: "opcional", en: "optional" })}
                    placeholder={t({ es: "tu@correo.com", en: "you@email.com" })}
                    value={suEmail}
                    onChange={setSuEmail}
                    autoComplete="email"
                    showLabel={showPw}
                    hideLabel={hidePw}
                    lang={lang}
                  />

                  <div className="field">
                    <label>{t({ es: "Soy…", en: "I am a…" })}</label>
                    <div className="role-seg">
                      <button type="button" className={role === "student" ? "on" : ""} onClick={() => setRole("student")}>
                        <span className="ico">🎯</span>
                        <span className="rl">
                          <b>{t({ es: "Estudiante", en: "Student" })}</b>
                          <span>{t({ es: "Quiero subir de rango", en: "I want to rank up" })}</span>
                        </span>
                      </button>
                      <button type="button" className={role === "teacher" ? "on" : ""} onClick={() => setRole("teacher")}>
                        <span className="ico">🛡️</span>
                        <span className="rl">
                          <b>{t({ es: "Docente", en: "Teacher" })}</b>
                          <span>{t({ es: "Gestiono un grupo", en: "I manage a group" })}</span>
                        </span>
                      </button>
                    </div>
                  </div>

                  {role === "teacher" && (
                    <div className="teacher-notice" role="note">
                      <span className="tn-ico">🛡️</span>
                      <div className="tn-body">
                        <b>{t({ es: "Las cuentas docentes se verifican", en: "Teacher accounts are verified" })}</b>
                        <p>
                          {t({
                            es: "Para proteger a los grupos, validamos a cada docente antes de dar acceso al panel. Un administrador aprobará tu cuenta.",
                            en: "To keep groups safe, we verify every teacher before granting dashboard access. An admin will approve your account.",
                          })}
                        </p>
                      </div>
                    </div>
                  )}

                  {role === "student" && (
                    <>
                      <div className="field">
                        <label>{t({ es: "Nivel educativo", en: "Education level" })}</label>
                        <div className="level-seg">
                          <button type="button" className={level === "secundaria" ? "on" : ""} onClick={() => setLevel("secundaria")}>
                            <span className="ico">📘</span>
                            <b>{t({ es: "Secundaria", en: "Secondary" })}</b>
                            <span className="d">{t({ es: "Bachillerato", en: "High school" })}</span>
                          </button>
                          <button type="button" className={level === "universidad" ? "on" : ""} onClick={() => setLevel("universidad")}>
                            <span className="ico">🎓</span>
                            <b>{t({ es: "Universidad", en: "University" })}</b>
                            <span className="d">{t({ es: "Pregrado y más", en: "Undergrad & up" })}</span>
                          </button>
                          <button type="button" className={level === "semillero" ? "on" : ""} onClick={() => setLevel("semillero")}>
                            <span className="ico">🌱</span>
                            <b>{t({ es: "Semillero", en: "Semillero" })}</b>
                            <span className="d">{t({ es: "Grupo de talento", en: "Talent track" })}</span>
                          </button>
                          <button type="button" className={level === "concursos" ? "on" : ""} onClick={() => setLevel("concursos")}>
                            <span className="ico">🏆</span>
                            <b>{t({ es: "Concursos", en: "Contests" })}</b>
                            <span className="d">{t({ es: "DIAN, SENA y más", en: "DIAN, SENA & more" })}</span>
                          </button>
                        </div>
                      </div>

                      {level === "semillero" && (
                        <div className="field">
                          <label>{t({ es: "Grado", en: "Grade" })}</label>
                          <select value={grade} onChange={(e) => setGrade(e.target.value)}>
                            {["6", "7", "8", "9", "10", "11"].map((g) => (
                              <option key={g} value={g}>
                                {t({ es: "Grado", en: "Grade" })} {g}°
                              </option>
                            ))}
                          </select>
                        </div>
                      )}

                      <Field
                        label={t({ es: "Código de clase", en: "Class code" })}
                        lead="#"
                        optional={t({ es: "opcional", en: "optional" })}
                        placeholder={t({ es: "Ej. 9A-MATE", en: "e.g. 9A-MATH" })}
                        value={suCode}
                        onChange={setSuCode}
                        showLabel={showPw}
                        hideLabel={hidePw}
                        lang={lang}
                      />
                    </>
                  )}

                  <div className="fields two">
                    <Field
                      label={t({ es: "Contraseña", en: "Password" })}
                      lead="🔒"
                      type="password"
                      placeholder="••••••••"
                      value={suPw}
                      onChange={setSuPw}
                      required
                      minLength={6}
                      autoComplete="new-password"
                      showLabel={showPw}
                      hideLabel={hidePw}
                      lang={lang}
                    />
                    <Field
                      label={t({ es: "Confirmar contraseña", en: "Confirm password" })}
                      lead="🔒"
                      type="password"
                      placeholder="••••••••"
                      value={suPw2}
                      onChange={setSuPw2}
                      required
                      minLength={6}
                      autoComplete="new-password"
                      showLabel={showPw}
                      hideLabel={hidePw}
                      lang={lang}
                    />
                  </div>

                  <label className="check terms">
                    <input type="checkbox" checked={terms} onChange={(e) => setTerms(e.target.checked)} />
                    <span className="box" />
                    <span>
                      {t({ es: "Acepto los ", en: "I agree to the " })}
                      <a href="#" onClick={(e) => e.preventDefault()}>
                        {t({ es: "Términos", en: "Terms" })}
                      </a>
                      {t({ es: " y la ", en: " & " })}
                      <a href="#" onClick={(e) => e.preventDefault()}>
                        {t({ es: "Privacidad", en: "Privacy" })}
                      </a>
                    </span>
                  </label>
                </div>
              )}

              {error && <div className="auth-msg error">{error}</div>}
              {info && <div className="auth-msg info">{info}</div>}

              <button type="submit" className="auth-submit" disabled={loading}>
                {loading
                  ? t({ es: "Un momento…", en: "One moment…" })
                  : t(
                      mode === "login"
                        ? { es: "Entrar a Oulad", en: "Enter Oulad" }
                        : { es: "Crear mi cuenta", en: "Create my account" }
                    )}
                <span className="arr">→</span>
              </button>

              <div className="auth-or">{t({ es: "o continúa con", en: "or continue with" })}</div>
              <div className="social-row">
                <button type="button" className="social-btn" disabled title={t({ es: "Próximamente", en: "Coming soon" })}>
                  <GoogleIcon />
                  Google
                </button>
                <button type="button" className="social-btn" disabled title={t({ es: "Próximamente", en: "Coming soon" })}>
                  <MicrosoftIcon />
                  Microsoft
                </button>
              </div>

              <div className="auth-switch">
                {t(mode === "login" ? { es: "¿Aún no tienes cuenta?", en: "No account yet?" } : { es: "¿Ya tienes cuenta?", en: "Already have an account?" })}
                <button type="button" onClick={() => changeMode(mode === "login" ? "signup" : "login")}>
                  {t(mode === "login" ? { es: "Crear cuenta", en: "Sign up" } : { es: "Iniciar sesión", en: "Log in" })}
                </button>
              </div>
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}
