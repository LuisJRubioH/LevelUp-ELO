/* Oulad auth — shared parts: i18n, wordmark, fields, social, KatIA */
const { useState } = React;

/* ----------------------------- i18n ----------------------------- */
const T = {
  login_tab:   { es: "Iniciar sesión", en: "Log in" },
  signup_tab:  { es: "Crear cuenta",   en: "Sign up" },

  login_eyebrow:  { es: "Bienvenido de vuelta", en: "Welcome back" },
  signup_eyebrow: { es: "Únete a Oulad",        en: "Join Oulad" },
  login_title:    { es: "Continúa tu ascenso.",   en: "Continue your climb." },
  signup_title:   { es: "Crea tu cuenta.",        en: "Create your account." },
  login_title_em: { es: "ascenso",                en: "climb" },
  signup_title_em:{ es: "cuenta",                 en: "account" },
  login_sub:  { es: "Tu ELO, tus rangos y KatIA te están esperando.", en: "Your ELO, your ranks and KatIA are waiting for you." },
  signup_sub: { es: "Configura tu perfil y deja que el motor ELO encuentre tu reto perfecto.", en: "Set up your profile and let the ELO engine find your perfect challenge." },

  name:     { es: "Nombre completo", en: "Full name" },
  name_ph:  { es: "Ada Mateus",      en: "Ada Mateus" },
  email:    { es: "Correo",          en: "Email" },
  email_ph: { es: "tu@correo.com",   en: "you@email.com" },
  userOrEmail:    { es: "Usuario o correo", en: "Username or email" },
  userOrEmail_ph: { es: "ada.mateus  ·  tu@correo.com", en: "ada.mateus  ·  you@email.com" },
  password: { es: "Contraseña",      en: "Password" },
  confirm:  { es: "Confirmar contraseña", en: "Confirm password" },
  pw_ph:    { es: "••••••••",        en: "••••••••" },
  show:     { es: "ver",  en: "show" },
  hide:     { es: "ocultar", en: "hide" },

  role:        { es: "Soy…",        en: "I am a…" },
  student:     { es: "Estudiante",  en: "Student" },
  student_d:   { es: "Quiero subir de rango", en: "I want to rank up" },
  teacher:     { es: "Docente",     en: "Teacher" },
  teacher_d:   { es: "Gestiono un grupo", en: "I manage a group" },
  classcode:   { es: "Código de clase", en: "Class code" },
  optional:    { es: "opcional",    en: "optional" },
  classcode_ph:{ es: "Ej. 9A-MATE", en: "e.g. 9A-MATH" },

  level:       { es: "Nivel educativo", en: "Education level" },
  level_sec:   { es: "Secundaria",  en: "Secondary" },
  level_sec_d: { es: "Bachillerato", en: "High school" },
  level_uni:   { es: "Universidad", en: "University" },
  level_uni_d: { es: "Pregrado y más", en: "Undergrad & up" },
  level_sem:   { es: "Semillero",   en: "Semillero" },
  level_sem_d: { es: "Grupo de talento", en: "Talent track" },

  teacher_notice_t: { es: "Las cuentas docentes se verifican", en: "Teacher accounts are verified" },
  teacher_notice_b: { es: "Para proteger a los grupos, validamos a cada docente antes de dar acceso al panel. Te enviaremos un correo para confirmar tu institución (suele tardar menos de 24 h).", en: "To keep groups safe, we verify every teacher before granting dashboard access. We'll email you to confirm your institution (usually under 24 h)." },

  remember: { es: "Recordarme",    en: "Remember me" },
  forgot:   { es: "¿Olvidaste tu contraseña?", en: "Forgot password?" },
  login_btn:{ es: "Entrar a Oulad", en: "Enter Oulad" },
  signup_btn:{ es: "Crear mi cuenta", en: "Create my account" },

  or:       { es: "o continúa con", en: "or continue with" },
  google:   { es: "Google",     en: "Google" },
  microsoft:{ es: "Microsoft",  en: "Microsoft" },

  terms_pre:  { es: "Acepto los ",  en: "I agree to the " },
  terms_link: { es: "Términos",     en: "Terms" },
  terms_mid:  { es: " y la ",       en: " & " },
  privacy_link:{ es: "Privacidad",  en: "Privacy" },

  have:     { es: "¿Ya tienes cuenta?",   en: "Already have an account?" },
  no:       { es: "¿Aún no tienes cuenta?", en: "No account yet?" },

  katia_name: { es: "KatIA · tutora", en: "KatIA · tutor" },
  katia_login:  { es: "¡Hey, te extrañé! Tu racha sigue viva. ¿Seguimos donde lo dejamos?", en: "Hey, I missed you! Your streak is still alive. Pick up where we left off?" },
  katia_signup: { es: "¡Hola! Soy KatIA, tu tutora. En un minuto medimos tu ELO y empezamos.", en: "Hi! I'm KatIA, your tutor. In a minute we'll measure your ELO and begin." },
  katia_role: { es: "Tutora socrática", en: "Socratic tutor" },

  brand_h_a: { es: "Las matemáticas tienen rango.", en: "Math has a rank." },
  brand_h_b: { es: "Sube el tuyo.", en: "Climb yours." },
  quest_login:  { es: "CONTINUAR PARTIDA", en: "CONTINUE GAME" },
  quest_signup: { es: "NUEVA PARTIDA", en: "NEW GAME" },

  stat_q: { es: "preguntas", en: "questions" },
  stat_r: { es: "rangos", en: "ranks" },
};
const tr = (k, lang) => (T[k] ? T[k][lang] : k);

/* ----------------------------- Wordmark ----------------------------- */
function Wordmark({ size = "md" }) {
  return (
    <span className={"wordmark " + size}>
      <span className="mark" aria-hidden="true"></span>
      <span className="wm-text"><span className="o">O</span>ulad</span>
    </span>
  );
}

/* ----------------------------- Lang toggle ----------------------------- */
function LangToggle({ lang, setLang }) {
  return (
    <span className="auth-lang" role="group" aria-label="Idioma">
      <button className={lang === "es" ? "on" : ""} onClick={() => setLang("es")}>ES</button>
      <button className={lang === "en" ? "on" : ""} onClick={() => setLang("en")}>EN</button>
    </span>
  );
}

/* ----------------------------- Tabs ----------------------------- */
function Tabs({ mode, setMode, lang, full }) {
  return (
    <div className={"auth-tabs" + (full ? " full" : "")} role="tablist">
      <button className={mode === "login" ? "on" : ""} onClick={() => setMode("login")}>{tr("login_tab", lang)}</button>
      <button className={mode === "signup" ? "on" : ""} onClick={() => setMode("signup")}>{tr("signup_tab", lang)}</button>
    </div>
  );
}

/* ----------------------------- Field ----------------------------- */
function Field({ label, opt, type = "text", lead, ph, lang }) {
  const [show, setShow] = useState(false);
  const isPw = type === "password";
  return (
    <div className="field">
      <label>{label}{opt ? <span className="opt">· {opt}</span> : null}</label>
      <div className="input-wrap">
        {lead ? <span className="lead">{lead}</span> : null}
        <input type={isPw && show ? "text" : type} placeholder={ph} />
        {isPw ? (
          <button type="button" className="reveal-pw" onClick={() => setShow(s => !s)}>
            {show ? tr("hide", lang) : tr("show", lang)}
          </button>
        ) : null}
      </div>
    </div>
  );
}

/* ----------------------------- Role segmented ----------------------------- */
function RoleSeg({ role, setRole, lang }) {
  return (
    <div className="field">
      <label>{tr("role", lang)}</label>
      <div className="role-seg">
        <button type="button" className={role === "student" ? "on" : ""} onClick={() => setRole("student")}>
          <span className="ico">🎯</span>
          <span className="rl"><b>{tr("student", lang)}</b><span>{tr("student_d", lang)}</span></span>
        </button>
        <button type="button" className={role === "teacher" ? "on" : ""} onClick={() => setRole("teacher")}>
          <span className="ico">🛡️</span>
          <span className="rl"><b>{tr("teacher", lang)}</b><span>{tr("teacher_d", lang)}</span></span>
        </button>
      </div>
    </div>
  );
}

/* ----------------------------- Social ----------------------------- */
const GoogleIcon = () => (
  <svg viewBox="0 0 48 48" aria-hidden="true">
    <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.9 29.3 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.3 6.1 29.4 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.3-.4-3.5z"/>
    <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 16 19 13 24 13c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.3 6.1 29.4 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/>
    <path fill="#4CAF50" d="M24 44c5.2 0 10-2 13.6-5.2l-6.3-5.3C29.2 35 26.7 36 24 36c-5.3 0-9.7-3.1-11.3-7.5l-6.5 5C9.6 39.6 16.2 44 24 44z"/>
    <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.1-4 5.5l6.3 5.3C41.2 36.4 44 30.8 44 24c0-1.3-.1-2.3-.4-3.5z"/>
  </svg>
);
const MicrosoftIcon = () => (
  <svg viewBox="0 0 23 23" aria-hidden="true">
    <path fill="#F25022" d="M1 1h10v10H1z"/>
    <path fill="#7FBA00" d="M12 1h10v10H12z"/>
    <path fill="#00A4EF" d="M1 12h10v10H1z"/>
    <path fill="#FFB900" d="M12 12h10v10H12z"/>
  </svg>
);
function SocialRow({ lang }) {
  return (
    <React.Fragment>
      <div className="auth-or">{tr("or", lang)}</div>
      <div className="social-row">
        <button type="button" className="social-btn"><GoogleIcon />{tr("google", lang)}</button>
        <button type="button" className="social-btn"><MicrosoftIcon />{tr("microsoft", lang)}</button>
      </div>
    </React.Fragment>
  );
}

/* ----------------------------- KatIA speech ----------------------------- */
function KatiaSpeak({ mode, lang }) {
  return (
    <div className="katia-speak">
      <div className="av"><img src="assets/katia-correcto.gif" alt="KatIA" /></div>
      <div className="bubble">
        <span className="nm">{tr("katia_name", lang)}</span>
        {tr(mode === "login" ? "katia_login" : "katia_signup", lang)}
      </div>
    </div>
  );
}

/* ----------------------------- Terms checkbox ----------------------------- */
function TermsCheck({ lang }) {
  return (
    <label className="check terms">
      <input type="checkbox" defaultChecked />
      <span className="box"></span>
      <span>{tr("terms_pre", lang)}<a href="#">{tr("terms_link", lang)}</a>{tr("terms_mid", lang)}<a href="#">{tr("privacy_link", lang)}</a></span>
    </label>
  );
}

/* ----------------------------- Education level selector ----------------------------- */
function LevelSeg({ level, setLevel, lang }) {
  const opts = [
    { id: "secundaria", ico: "📘", t: "level_sec", d: "level_sec_d" },
    { id: "universidad", ico: "🎓", t: "level_uni", d: "level_uni_d" },
    { id: "semillero", ico: "🌱", t: "level_sem", d: "level_sem_d" },
  ];
  return (
    <div className="field">
      <label>{tr("level", lang)}</label>
      <div className="level-seg">
        {opts.map(o => (
          <button key={o.id} type="button" className={level === o.id ? "on" : ""} onClick={() => setLevel(o.id)}>
            <span className="ico">{o.ico}</span>
            <b>{tr(o.t, lang)}</b>
            <span className="d">{tr(o.d, lang)}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

/* ----------------------------- Teacher verification notice ----------------------------- */
function TeacherNotice({ lang }) {
  return (
    <div className="teacher-notice" role="note">
      <span className="tn-ico">🛡️</span>
      <div className="tn-body">
        <b>{tr("teacher_notice_t", lang)}</b>
        <p>{tr("teacher_notice_b", lang)}</p>
      </div>
    </div>
  );
}

/* ----------------------------- shared form body ----------------------------- */
/* Renders the field stack + helpers for a given mode/role. */
function FormBody({ mode, lang, role, setRole }) {
  const [level, setLevel] = useState("secundaria");
  if (mode === "login") {
    return (
      <React.Fragment>
        <div className="fields">
          <Field label={tr("userOrEmail", lang)} type="text" lead="@" ph={tr("userOrEmail_ph", lang)} lang={lang} />
          <Field label={tr("password", lang)} type="password" lead="🔒" ph={tr("pw_ph", lang)} lang={lang} />
        </div>
        <div className="auth-row">
          <label className="check"><input type="checkbox" /><span className="box"></span>{tr("remember", lang)}</label>
          <span className="link-forgot">{tr("forgot", lang)}</span>
        </div>
      </React.Fragment>
    );
  }
  return (
    <React.Fragment>
      <div className="fields">
        <Field label={tr("name", lang)} lead="👤" ph={tr("name_ph", lang)} lang={lang} />
        <Field label={tr("email", lang)} type="email" lead="✉" ph={tr("email_ph", lang)} lang={lang} />
        <RoleSeg role={role} setRole={setRole} lang={lang} />
        {role === "teacher" ? <TeacherNotice lang={lang} /> : null}
        {role === "student" ? (
          <React.Fragment>
            <LevelSeg level={level} setLevel={setLevel} lang={lang} />
            <Field label={tr("classcode", lang)} opt={tr("optional", lang)} lead="#" ph={tr("classcode_ph", lang)} lang={lang} />
          </React.Fragment>
        ) : null}
        <div className="fields two">
          <Field label={tr("password", lang)} type="password" lead="🔒" ph={tr("pw_ph", lang)} lang={lang} />
          <Field label={tr("confirm", lang)} type="password" lead="🔒" ph={tr("pw_ph", lang)} lang={lang} />
        </div>
        <TermsCheck lang={lang} />
      </div>
    </React.Fragment>
  );
}

Object.assign(window, {
  T, tr, Wordmark, LangToggle, Tabs, Field, RoleSeg, LevelSeg, TeacherNotice, SocialRow,
  GoogleIcon, MicrosoftIcon, KatiaSpeak, TermsCheck, FormBody,
});
