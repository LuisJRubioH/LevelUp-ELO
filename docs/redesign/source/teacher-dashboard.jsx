/* Oulad teacher console — Window 1: Panel Docente (Dashboard) */
const { useState: useStateD, useMemo } = React;

/* ---- stat cards ---- */
function StatCard({ ic, color, val, sub, lbl, trend, trendDir }) {
  return (
    <div className="stat-card" style={{ "--c": color }}>
      <div className="sc-top">
        <span className="sc-ic">{ic}</span>
        {trend ? <span className={"sc-trend " + trendDir}>{trendDir === "up" ? "▲" : trendDir === "down" ? "▼" : "•"} {trend}</span> : null}
      </div>
      <div className="sc-val">{val}</div>
      <div className="sc-lbl">{lbl}</div>
      {sub ? <div className="sc-sub">{sub}</div> : null}
    </div>
  );
}

/* ---- Estudiantes tab ---- */
function StudentsView({ students }) {
  const [q, setQ] = useStateD("");
  const [sort, setSort] = useStateD("elo");
  const rows = useMemo(() => {
    let r = students.filter(s => (s.name + s.user).toLowerCase().includes(q.toLowerCase()));
    r = [...r].sort((a, b) => sort === "elo" ? b.elo - a.elo : sort === "acc" ? b.acc - a.acc : a.name.localeCompare(b.name));
    return r;
  }, [students, q, sort]);

  return (
    <div className="panel">
      <div className="panel-head">
        <h3>Estudiantes <span style={{ color: "var(--mute)", fontWeight: 500, fontSize: 13 }}>· {rows.length}</span></h3>
        <div className="ph-side">
          <select className="sort-sel" value={sort} onChange={e => setSort(e.target.value)}>
            <option value="elo">Ordenar: ELO</option>
            <option value="acc">Ordenar: Acierto</option>
            <option value="name">Ordenar: Nombre</option>
          </select>
          <div className="search">
            <span className="ic">🔍</span>
            <input placeholder="Buscar estudiante…" value={q} onChange={e => setQ(e.target.value)} />
          </div>
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="empty"><div className="em-ic">🗒️</div><p>Sin estudiantes para los filtros aplicados.</p></div>
      ) : (
        <div className="stu-table">
          <div className="stu-row head">
            <div>Estudiante</div><div>Grupo</div><div>ELO · Rango</div><div>Acierto</div><div>Actividad</div><div></div>
          </div>
          {rows.map(s => {
            const t = topicById(s.topic); const rk = rankFor(s.elo);
            return (
              <div className="stu-row" key={s.user}>
                <div className="stu-id">
                  <div className="av" style={{ background: avaFor(s.name) }}>{initials(s.name)}</div>
                  <div className="nm"><b>{s.name}</b><span>@{s.user}</span></div>
                </div>
                <div className="stu-group"><span className="gd" style={{ background: t.color }}></span>{t.name}</div>
                <div className="stu-elo">
                  <span className="e">{fmtMiles(s.elo)}</span>
                  <span className="rank-badge" style={{ color: rk.fg, background: rk.bg }}>{rk.name}</span>
                </div>
                <div className="acc-cell">
                  <div className="av"><span style={{ color: "var(--mute)" }}>{s.attempts} int.</span><b>{s.acc}%</b></div>
                  <div className="bar"><i style={{ width: s.acc + "%", background: accColor(s.acc) }}></i></div>
                </div>
                <div className="stu-last">
                  {s.last}
                  {s.attn ? <span className="flag">⚠ Necesita atención</span> : null}
                </div>
                <button className="stu-go" title="Ver perfil">›</button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ---- Ranking tab ---- */
function RankingView({ students }) {
  const sorted = [...students].sort((a, b) => b.elo - a.elo);
  const top3 = sorted.slice(0, 3);
  const order = [top3[1], top3[0], top3[2]]; // silver, gold, bronze
  const medals = { 0: "🥇", 1: "🥈", 2: "🥉" };
  const goldIdx = 0;
  return (
    <div className="panel">
      <div className="panel-head"><h3>Ranking global</h3><span style={{ fontSize: 12, color: "var(--mute)" }}>Actualizado hace 10 min</span></div>
      <div className="podium">
        {order.map((s, i) => {
          const realPos = sorted.indexOf(s);
          return (
            <div className={"pod " + (realPos === 0 ? "p1" : "")} key={s.user}>
              <div className="medal">{medals[realPos]}</div>
              <div className="av" style={{ width: 44, height: 44, borderRadius: 12, margin: "10px auto 0", display: "grid", placeItems: "center", color: "#fff", fontFamily: "var(--font-display)", fontWeight: 700, background: avaFor(s.name) }}>{initials(s.name)}</div>
              <div className="pname">{s.name}</div>
              <div className="pelo">{fmtMiles(s.elo)}</div>
              <span className="rank-badge" style={{ color: rankFor(s.elo).fg, background: rankFor(s.elo).bg }}>{rankFor(s.elo).name}</span>
            </div>
          );
        })}
      </div>
      <div className="rank-list">
        {sorted.slice(3).map((s, i) => (
          <div className="rank-line" key={s.user}>
            <div className="pos">{i + 4}</div>
            <div className="who">
              <div className="av" style={{ background: avaFor(s.name) }}>{initials(s.name)}</div>
              <div><b>{s.name}</b> <span style={{ color: "var(--mute)", fontSize: 12 }}>· {topicById(s.topic).name}</span></div>
            </div>
            <div className={"delta " + (s.dElo > 0 ? "up" : s.dElo < 0 ? "down" : "flat")}>{s.dElo > 0 ? "▲" : s.dElo < 0 ? "▼" : "•"} {Math.abs(s.dElo)}</div>
            <div className="rl-elo">{fmtMiles(s.elo)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---- Métricas tab ---- */
function MetricsView({ students }) {
  const buckets = eloBuckets(students);
  const maxN = Math.max(...buckets.map(b => b.n), 1);
  const mastery = topicCounts(students);
  const attn = students.filter(s => s.attn);
  const maxAct = Math.max(...ACTIVITY.map(a => a.v));
  // sparkline points
  const w = 320, h = 110, pad = 6;
  const pts = ACTIVITY.map((a, i) => [pad + i * (w - 2 * pad) / (ACTIVITY.length - 1), h - pad - (a.v / maxAct) * (h - 2 * pad)]);
  const line = pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ");
  const area = line + ` L${w - pad} ${h - pad} L${pad} ${h - pad} Z`;

  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <h4>Dominio por tópico</h4>
        <div className="mc-sub">Acierto promedio de los estudiantes en cada curso</div>
        {mastery.map(t => (
          <div className="mastery-row" key={t.id}>
            <div className="ml"><span className="gd" style={{ background: t.color }}></span>{t.name}</div>
            <div className="mbar"><i style={{ width: t.mastery + "%", background: t.color }}></i></div>
            <div className="mv">{t.mastery}%</div>
          </div>
        ))}
      </div>

      <div className="metric-card">
        <h4>Distribución de ELO</h4>
        <div className="mc-sub">Cuántos estudiantes hay en cada rango</div>
        <div className="histo">
          {buckets.map(b => (
            <div className="col" key={b.label}>
              <div className="cn">{b.n}</div>
              <div className="bar" style={{ height: `${(b.n / maxN) * 100}%` }}></div>
              <div className="cl">{b.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="metric-card">
        <h4>Actividad de la semana</h4>
        <div className="mc-sub">Intentos de práctica por día · {ACTIVITY.reduce((s,a)=>s+a.v,0)} en total</div>
        <svg className="spark" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
          <defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="var(--accent)" stopOpacity="0.4" /><stop offset="100%" stopColor="var(--accent)" stopOpacity="0" /></linearGradient></defs>
          <path d={area} fill="url(#sg)" />
          <path d={line} fill="none" stroke="var(--accent)" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />
          {pts.map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r="3" fill="var(--accent-2)" />)}
        </svg>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
          {ACTIVITY.map(a => <span key={a.d} style={{ fontSize: 11, color: "var(--mute)" }}>{a.d}</span>)}
        </div>
      </div>

      <div className="metric-card">
        <h4>Necesitan atención <span style={{ color: "var(--gold)" }}>· {attn.length}</span></h4>
        <div className="mc-sub">Caída de ELO o baja actividad reciente</div>
        {attn.length === 0 ? <p style={{ color: "var(--mute)", fontSize: 13 }}>Ningún estudiante en riesgo. 🎉</p> :
          attn.map(s => (
            <div className="attn-row" key={s.user}>
              <div className="av" style={{ background: avaFor(s.name) }}>{initials(s.name)}</div>
              <div className="ab"><b>{s.name}</b><span>{s.dElo < 0 ? `${s.dElo} ELO esta semana` : "Inactivo " + s.last} · {s.acc}% acierto</span></div>
              <div className="ax">{s.acc}%</div>
            </div>
          ))}
      </div>
    </div>
  );
}

/* ---- Dashboard root ---- */
function Dashboard() {
  const [topic, setTopic] = useStateD("all");
  const [tab, setTab] = useStateD("estudiantes");
  const [range, setRange] = useStateD("30d");

  const filtered = useMemo(() => topic === "all" ? STUDENTS : STUDENTS.filter(s => s.topic === topic), [topic]);
  const stats = computeStats(STUDENTS);
  const counts = topicCounts(STUDENTS);

  return (
    <React.Fragment>
      <div className="tc-head">
        <div className="ttl">
          <h1>Panel Docente</h1>
          <p>Tu vista general de grupos, progreso y dominio. Datos en tiempo real del motor ELO.</p>
        </div>
        <div className="head-side">
          <div className="tc-range">
            {["7d","30d","Todo"].map(r => <button key={r} className={range === r ? "on" : ""} onClick={() => setRange(r)}>{r === "Todo" ? "Todo" : r}</button>)}
          </div>
        </div>
      </div>

      <div className="stat-grid">
        <StatCard ic="👥" color="#8b5cf6" val={stats.groups} lbl="Grupos activos" sub="4 cursos en curso" trend="estable" trendDir="flat" />
        <StatCard ic="🎓" color="#2dd4bf" val={stats.students} lbl="Estudiantes" sub="10 activos esta semana" trend="2 nuevos" trendDir="up" />
        <StatCard ic="♛" color="#ffd700" val={fmtMiles(stats.elo)} lbl="ELO promedio" sub="vs. 1.498 hace 30 d" trend="+24" trendDir="up" />
        <StatCard ic="🎯" color="#34d399" val={stats.acc + "%"} lbl="Acierto promedio" sub="objetivo del grupo: 75%" trend="+3 pts" trendDir="up" />
      </div>

      <div className="topic-row">
        <button className={"topic-chip all" + (topic === "all" ? " on" : "")} onClick={() => setTopic("all")}>
          <span className="dot" style={{ background: "linear-gradient(140deg,#8b5cf6,#2dd4bf)" }}></span><b>Todos</b><span>· {STUDENTS.length}</span>
        </button>
        {counts.map(t => (
          <button key={t.id} className={"topic-chip" + (topic === t.id ? " on" : "")} style={{ "--c": t.color }} onClick={() => setTopic(t.id)}>
            <span className="dot"></span><b>{t.name}</b><span>· {t.count} est.</span>
          </button>
        ))}
      </div>

      <div className="view-tabs">
        <button className={tab === "estudiantes" ? "on" : ""} onClick={() => setTab("estudiantes")}>👥 Estudiantes</button>
        <button className={tab === "ranking" ? "on" : ""} onClick={() => setTab("ranking")}>🏆 Ranking</button>
        <button className={tab === "metricas" ? "on" : ""} onClick={() => setTab("metricas")}>📊 Métricas</button>
      </div>

      {tab === "estudiantes" ? <StudentsView students={filtered} /> :
       tab === "ranking" ? <RankingView students={filtered} /> :
       <MetricsView students={filtered} />}
    </React.Fragment>
  );
}

Object.assign(window, { StatCard, StudentsView, RankingView, MetricsView, Dashboard });
