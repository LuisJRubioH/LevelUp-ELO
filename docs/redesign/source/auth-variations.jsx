/* Oulad auth — Option A (split-screen), single full-page deliverable */
const { useState: useStateV } = React;

function AuthTitle({ mode, lang }) {
  const key = mode === "login" ? "login_title" : "signup_title";
  const emKey = mode === "login" ? "login_title_em" : "signup_title_em";
  const full = tr(key, lang);
  const em = tr(emKey, lang);
  const idx = full.indexOf(em);
  if (idx === -1) return <h1 className="auth-title">{full}</h1>;
  return (
    <h1 className="auth-title">
      {full.slice(0, idx)}<span className="em">{em}</span>{full.slice(idx + em.length)}
    </h1>
  );
}

function Submit({ mode, lang }) {
  return (
    <button type="submit" className="auth-submit">
      {tr(mode === "login" ? "login_btn" : "signup_btn", lang)}
      <span className="arr">→</span>
    </button>
  );
}

function Switch({ mode, setMode, lang }) {
  return (
    <div className="auth-switch">
      {tr(mode === "login" ? "no" : "have", lang)}
      <button type="button" onClick={() => setMode(mode === "login" ? "signup" : "login")}>
        {tr(mode === "login" ? "signup_tab" : "login_tab", lang)}
      </button>
    </div>
  );
}

const stop = (e) => e.preventDefault();

/* ============================================================ OPTION A — SPLIT */
function OuladAuth() {
  const [lang, setLang] = useStateV("es");
  const [mode, setMode] = useStateV("login");
  const [role, setRole] = useStateV("student");
  return (
    <div className="auth-screen var-split" lang={lang} data-screen-label="Oulad Auth">
      <div className="auth-bg"><div className="grid"></div></div>
      <div className="split">
        <aside className="brand-panel">
          <div className="pbg"><span style={{ position: "absolute", width: 360, height: 360, borderRadius: "50%", filter: "blur(90px)", background: "var(--glow-a)", top: -120, left: -90 }}></span></div>
          <Wordmark size="md" />
          <h2 className="brand-h">{tr("brand_h_a", lang)} <span className="em">{tr("brand_h_b", lang)}</span></h2>
          <div className="brand-katia">
            <div className="katia-card" style={{ marginBottom: 20 }}>
              <div className="hud">
                <span className="fdot" style={{ background: "#ff5f57" }}></span>
                <span className="fdot" style={{ background: "#febc2e" }}></span>
                <span className="fdot" style={{ background: "#28c840" }}></span>
                <span className="lbl">KATIA.EXE</span>
              </div>
              <img src="assets/katia-correcto.gif" alt="KatIA, tutora socrática pixel-art" />
              <div className="scan"></div>
              <div className="nameplate">
                <div className="who">KatIA<small>{tr("katia_role", lang)}</small></div>
                <div className="hpbar"><div className="t">XP 72%</div><div className="bar"><i style={{ width: "72%" }}></i></div></div>
              </div>
            </div>
            <div className="brand-stats">
              <div><div className="n"><span className="a">+1.900</span></div><div className="l">{tr("stat_q", lang)}</div></div>
              <div><div className="n">16</div><div className="l">{tr("stat_r", lang)}</div></div>
              <div><div className="n">10+</div><div className="l">materias</div></div>
            </div>
          </div>
        </aside>

        <main className="form-panel">
          <div className="form-scroll">
            <div className="form-topbar">
              <Tabs mode={mode} setMode={setMode} lang={lang} />
              <LangToggle lang={lang} setLang={setLang} />
            </div>
            <form className="auth-form" onSubmit={stop}>
              <span className="auth-eyebrow">{tr(mode === "login" ? "login_eyebrow" : "signup_eyebrow", lang)}</span>
              <AuthTitle mode={mode} lang={lang} />
              <p className="auth-sub">{tr(mode === "login" ? "login_sub" : "signup_sub", lang)}</p>
              <FormBody mode={mode} lang={lang} role={role} setRole={setRole} />
              <Submit mode={mode} lang={lang} />
              <SocialRow lang={lang} />
              <Switch mode={mode} setMode={setMode} lang={lang} />
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<OuladAuth />);
