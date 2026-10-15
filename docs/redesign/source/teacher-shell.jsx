/* Oulad teacher console — app shell: sidebar, footer, router */
const { useState: useStateS } = React;

function Wordmark() {
  return (
    <span className="wordmark">
      <span className="mark" aria-hidden="true"></span>
      <span className="wm-text"><span className="o">O</span>ulad</span>
    </span>
  );
}

const NAV = [
  { id: "dashboard",    label: "Dashboard",     ic: "▦" },
  { id: "grupos",       label: "Grupos",        ic: "👥" },
  { id: "procedimientos", label: "Procedimientos", ic: "📝", badge: 3 },
  { id: "examenes",     label: "Exámenes",      ic: "📋" },
  { id: "exportar",     label: "Exportar datos", ic: "📤" },
];

function Sidebar({ route, setRoute, light, setLight, lang, setLang }) {
  const [aiOpen, setAiOpen] = useStateS(false);
  return (
    <aside className="tc-side">
      <div className="tc-brand">
        <Wordmark />
        <span className="tag">MOTOR ELO · CONSOLA DOCENTE</span>
      </div>

      <nav className="tc-nav">
        {NAV.map(n => (
          <button key={n.id} className={"nav-item" + (route === n.id ? " on" : "")} onClick={() => setRoute(n.id)}>
            <span className="ic">{n.ic}</span>
            {n.label}
            {n.badge ? <span className="badge">{n.badge}</span> : null}
          </button>
        ))}

        <div className={"tc-ai" + (aiOpen ? " open" : "")} style={{ marginTop: "auto" }}>
          <div className="head" onClick={() => setAiOpen(o => !o)}>
            <span className="dot"></span> API de IA · KatIA
            <span className="chev">▾</span>
          </div>
          <div className="body">
            <div className="row"><span>Estado</span><b>Conectada</b></div>
            <div className="row"><span>Modelo</span><b>katia-v2</b></div>
            <div className="row"><span>Créditos</span><b>8.420</b></div>
          </div>
        </div>
      </nav>

      <div className="tc-foot">
        <div className="tc-user">
          <div className="ava">OG</div>
          <div className="meta">
            <b>oriana_g</b>
            <span><span className="role">Docente</span> · Colegio</span>
          </div>
        </div>
        <div className="tc-banner" title="Vincular correo">
          <span className="b-ic">✉️</span>
          <span>Agrega tu correo para no perder acceso</span>
        </div>
        <div className="tc-toggles">
          <button className="tc-tog" onClick={() => setLight(v => !v)}>{light ? "🌙 Modo oscuro" : "☀️ Modo claro"}</button>
          <button className="tc-tog" onClick={() => setLang(l => l === "es" ? "en" : "es")}>🌐 {lang.toUpperCase()}</button>
        </div>
        <button className="tc-logout">Cerrar sesión →</button>
      </div>
    </aside>
  );
}

function Soon({ title, note }) {
  return (
    <div className="tc-soon"><div className="box">
      <div className="em-ic">🛠️</div>
      <h2>{title}</h2>
      <p>{note}</p>
    </div></div>
  );
}

function TeacherConsole() {
  const [route, setRoute] = useStateS("dashboard");
  const [light, setLight] = useStateS(false);
  const [lang, setLang] = useStateS("es");

  React.useEffect(() => {
    document.documentElement.classList.toggle("light", light);
  }, [light]);

  let screen;
  if (route === "dashboard") screen = <Dashboard lang={lang} />;
  else if (route === "grupos") screen = <GroupsView />;
  else if (route === "procedimientos") screen = <ProceduresView />;
  else if (route === "examenes") screen = <ExamsView />;
  else screen = <ExportView />;

  return (
    <div className="tc">
      <Sidebar route={route} setRoute={setRoute} light={light} setLight={setLight} lang={lang} setLang={setLang} />
      <main className="tc-main" data-screen-label={"Teacher · " + route}>
        <div className="tc-main-inner">{screen}</div>
      </main>
    </div>
  );
}

Object.assign(window, { Wordmark, Sidebar, Soon, TeacherConsole });
