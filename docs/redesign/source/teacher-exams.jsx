/* Oulad teacher console — Window 4: Exámenes (assessment manager) */
const { useState: useStateE, useMemo: useMemoE, useEffect: useEffectE } = React;

/* ---- exam status meta ---- */
const EX_STATUS = {
  borrador:   { lbl: "Borrador",   fg: "#9ca3af",      bg: "rgba(156,163,175,.16)", dot: "#9ca3af" },
  programado: { lbl: "Programado", fg: "#7dd3fc",      bg: "rgba(125,211,252,.16)", dot: "#7dd3fc" },
  curso:      { lbl: "En curso",   fg: "var(--gold)",  bg: "color-mix(in srgb, var(--gold) 16%, transparent)", dot: "var(--gold)" },
  finalizado: { lbl: "Finalizado", fg: "#34d399",      bg: "rgba(52,211,153,.16)",  dot: "#34d399" },
};

const QTYPE = {
  opcion:        { lbl: "Opción múltiple", ic: "◉" },
  abierta:       { lbl: "Respuesta abierta", ic: "✎" },
  procedimiento: { lbl: "Procedimiento", ic: "∑" },
};

/* result rows reference real students; grade 0-100 (KatIA + teacher) */
const R = (name, grade, time, state = "entregado") => ({ name, grade, time, state });

const EXAMS_SEED = [
  {
    id: "e1", title: "Ecuaciones lineales", topic: "algebra", group: "Álgebra · 10°B",
    status: "finalizado", date: "28 may 2026", duration: 45, assigned: 7, submitted: 7,
    questions: [
      { type: "opcion", pts: 10, q: "¿Cuál es la solución de 2x + 6 = 14?" },
      { type: "procedimiento", pts: 20, q: "Resuelve y justifica:  3(x − 2) = x + 8" },
      { type: "opcion", pts: 10, q: "Si 5x = 35, ¿cuánto vale x?" },
      { type: "procedimiento", pts: 20, q: "Despeja x:  (x/4) + 3 = 7" },
      { type: "abierta", pts: 15, q: "Explica con tus palabras qué significa 'despejar una variable'." },
      { type: "opcion", pts: 10, q: "¿Cuál ecuación tiene solución x = 0?" },
      { type: "procedimiento", pts: 15, q: "Resuelve:  2x − 7 = 3x + 1" },
    ],
    results: [
      R("Mateo Restrepo", 96, "32 min"), R("Samuel Cárdenas", 88, "38 min"),
      R("Valentina Ortiz", 84, "41 min"), R("Tomás Aguirre", 77, "44 min"),
      R("Daniel Quiroga", 68, "45 min"), R("Camila Suárez", 54, "45 min"),
      R("Joaquín Beltrán", 41, "39 min"),
    ],
  },
  {
    id: "e2", title: "Funciones trigonométricas", topic: "trigonometria", group: "Trigonometría · 11°A",
    status: "curso", date: "hoy · 10:00", duration: 60, assigned: 6, submitted: 3,
    questions: [
      { type: "opcion", pts: 10, q: "¿Cuál es el valor de sin 30°?" },
      { type: "procedimiento", pts: 25, q: "Halla todos los θ en [0°, 360°) con cos θ = ½" },
      { type: "abierta", pts: 15, q: "Describe la relación entre seno y coseno." },
      { type: "procedimiento", pts: 25, q: "Demuestra:  sin²θ + cos²θ = 1" },
      { type: "opcion", pts: 10, q: "¿En qué cuadrante el seno es negativo y el coseno positivo?" },
      { type: "opcion", pts: 15, q: "tan 45° es igual a…" },
    ],
    results: [
      R("Isabella Méndez", 91, "en curso", "curso"), R("Antonia Vega", 0, "en curso", "curso"),
      R("Mateo Restrepo", 0, "en curso", "curso"),
    ],
  },
  {
    id: "e3", title: "Áreas y perímetros", topic: "geometria", group: "Geometría · 9°C",
    status: "programado", date: "12 jun 2026 · 08:00", duration: 50, assigned: 5, submitted: 0,
    questions: [
      { type: "opcion", pts: 15, q: "Área de un cuadrado de lado 6 cm." },
      { type: "procedimiento", pts: 25, q: "Calcula el área de un triángulo de base 10 y altura 7." },
      { type: "procedimiento", pts: 25, q: "Perímetro de un rectángulo de 8 × 5 cm." },
      { type: "abierta", pts: 15, q: "¿Cuándo conviene usar la fórmula del trapecio?" },
      { type: "opcion", pts: 20, q: "Área de un círculo de radio 3 (usa π ≈ 3.14)." },
    ],
    results: [],
  },
  {
    id: "e4", title: "Operaciones con fracciones", topic: "aritmetica", group: "Aritmética · 8°A",
    status: "borrador", date: "—", duration: 40, assigned: 0, submitted: 0,
    questions: [
      { type: "opcion", pts: 10, q: "¿Cuánto es ½ + ¼?" },
      { type: "procedimiento", pts: 20, q: "Resuelve:  ⅔ × ¾" },
      { type: "procedimiento", pts: 20, q: "Simplifica:  8/12" },
    ],
    results: [],
  },
  {
    id: "e5", title: "Sistemas de ecuaciones", topic: "algebra", group: "Álgebra · 10°B",
    status: "finalizado", date: "14 may 2026", duration: 60, assigned: 7, submitted: 6,
    questions: [
      { type: "procedimiento", pts: 30, q: "Resuelve por sustitución:  x + y = 10,  x − y = 2" },
      { type: "procedimiento", pts: 30, q: "Resuelve por igualación:  2x + y = 7,  x + y = 5" },
      { type: "opcion", pts: 20, q: "¿Cuántas soluciones tiene un sistema con rectas paralelas?" },
      { type: "abierta", pts: 20, q: "Explica la diferencia entre sustitución e igualación." },
    ],
    results: [
      R("Mateo Restrepo", 92, "54 min"), R("Samuel Cárdenas", 81, "60 min"),
      R("Valentina Ortiz", 73, "58 min"), R("Daniel Quiroga", 60, "60 min"),
      R("Camila Suárez", 47, "60 min"), R("Joaquín Beltrán", 38, "51 min"),
    ],
  },
];

/* ---- score distribution buckets ---- */
const scoreDist = (results) => {
  const done = results.filter(r => r.state === "entregado");
  const defs = [
    { label: "0–59", lo: 0, hi: 60, c: "#f87171" },
    { label: "60–69", lo: 60, hi: 70, c: "#fb923c" },
    { label: "70–79", lo: 70, hi: 80, c: "var(--gold)" },
    { label: "80–89", lo: 80, hi: 90, c: "#a3e635" },
    { label: "90–100", lo: 90, hi: 101, c: "#34d399" },
  ];
  return defs.map(d => ({ ...d, n: done.filter(r => r.grade >= d.lo && r.grade < d.hi).length }));
};
const examAvg = (results) => {
  const done = results.filter(r => r.state === "entregado");
  return done.length ? Math.round(done.reduce((s, r) => s + r.grade, 0) / done.length) : null;
};
const examTotalPts = (qs) => qs.reduce((s, q) => s + q.pts, 0);

/* ---- exam card ---- */
function ExamCard({ e, onOpen }) {
  const t = topicById(e.topic);
  const sm = EX_STATUS[e.status];
  const avg = examAvg(e.results);
  const pct = e.assigned ? Math.round((e.submitted / e.assigned) * 100) : 0;
  return (
    <button className="ex-card" style={{ "--c": t.color }} onClick={() => onOpen(e)}>
      <div className="ex-top">
        <span className="ex-status" style={{ color: sm.fg, background: sm.bg }}>
          <span className="ex-sdot" style={{ background: sm.dot }}></span>{sm.lbl}
        </span>
        <span className="ex-chip" style={{ color: t.color, background: "color-mix(in srgb, " + t.color + " 14%, transparent)" }}>
          <span className="gd" style={{ background: t.color }}></span>{t.name}
        </span>
      </div>
      <h3>{e.title}</h3>
      <p className="ex-grp">{e.group}</p>

      <div className="ex-meta">
        <span>{e.questions.length} preguntas</span><i></i>
        <span>{examTotalPts(e.questions)} pts</span><i></i>
        <span>{e.duration} min</span>
      </div>

      <div className="ex-foot">
        {e.status === "finalizado" ? (
          <div className="ex-result">
            <span className="ex-avg" style={{ color: gradeColor(avg) }}>{avg}<i>/100</i></span>
            <span className="ex-avg-l">promedio · {e.submitted} entregas</span>
          </div>
        ) : e.status === "curso" ? (
          <div className="ex-prog">
            <div className="ex-prog-bar"><i style={{ width: pct + "%" }}></i></div>
            <span>{e.submitted}/{e.assigned} en curso</span>
          </div>
        ) : e.status === "programado" ? (
          <div className="ex-when"><span className="ic">🗓</span>{e.date}</div>
        ) : (
          <div className="ex-when draft"><span className="ic">✎</span>Sin programar · {e.questions.length} preguntas listas</div>
        )}
        <span className="ex-open">›</span>
      </div>
    </button>
  );
}

/* ---- detail drawer ---- */
function ExamDrawer({ e, onClose }) {
  const [closing, setClosing] = useStateE(false);
  const [tab, setTab] = useStateE("preguntas");
  const close = () => { setClosing(true); setTimeout(onClose, 240); };
  useEffectE(() => {
    setTab(e && e.status === "finalizado" ? "resultados" : "preguntas");
    const k = (ev) => ev.key === "Escape" && close();
    window.addEventListener("keydown", k);
    return () => window.removeEventListener("keydown", k);
  }, [e && e.id]);
  if (!e) return null;
  const t = topicById(e.topic);
  const sm = EX_STATUS[e.status];
  const avg = examAvg(e.results);
  const dist = scoreDist(e.results);
  const maxN = Math.max(1, ...dist.map(d => d.n));
  const hasResults = e.status === "finalizado" || e.status === "curso";
  const sorted = [...e.results].sort((a, b) => b.grade - a.grade);

  return (
    <div className={"grp-backdrop" + (closing ? " out" : "")} onClick={close}>
      <aside className={"grp-drawer ex-drawer" + (closing ? " out" : "")} style={{ "--c": t.color }} onClick={ev => ev.stopPropagation()}>
        <div className="gd-head">
          <div className="gd-htop">
            <span className="ex-status" style={{ color: sm.fg, background: sm.bg }}>
              <span className="ex-sdot" style={{ background: sm.dot }}></span>{sm.lbl}
            </span>
            <button className="gd-x" onClick={close}>✕</button>
          </div>
          <h2>{e.title}</h2>
          <p className="gd-sub">
            <span className="ex-dot" style={{ background: t.color }}></span>{t.name} · {e.group} · {e.date}
          </p>
        </div>

        <div className="gd-stats">
          <div className="gds"><span className="l">Preguntas</span><b>{e.questions.length}</b></div>
          <div className="gds"><span className="l">Puntos</span><b>{examTotalPts(e.questions)}</b></div>
          <div className="gds"><span className="l">Duración</span><b>{e.duration}<i style={{fontSize:"11px",fontWeight:500,color:"var(--mute)"}}> min</i></b></div>
          <div className="gds"><span className="l">{e.status === "finalizado" ? "Promedio" : "Asignados"}</span>
            <b style={e.status === "finalizado" ? { color: gradeColor(avg) } : null}>{e.status === "finalizado" ? avg : e.assigned}</b>
          </div>
        </div>

        {hasResults ? (
          <div className="ex-tabs">
            <button className={tab === "resultados" ? "on" : ""} onClick={() => setTab("resultados")}>Resultados</button>
            <button className={tab === "preguntas" ? "on" : ""} onClick={() => setTab("preguntas")}>Preguntas</button>
          </div>
        ) : null}

        {tab === "resultados" && hasResults ? (
          <React.Fragment>
            {e.status === "finalizado" ? (
              <div className="gd-section">
                <span className="pd-lbl">Distribución de calificaciones</span>
                <div className="ex-dist">
                  {dist.map((d, i) => (
                    <div className="exd-col" key={i}>
                      <span className="exd-n">{d.n || ""}</span>
                      <div className="exd-track"><i style={{ height: (d.n / maxN * 100) + "%", background: d.c }}></i></div>
                      <span className="exd-lbl">{d.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}

            <div className="gd-section">
              <div className="gd-sechead">
                <h4>{e.status === "curso" ? "Progreso" : "Entregas"} <span>· {e.results.length}</span></h4>
              </div>
              <div className="ex-roster">
                {sorted.map((r, i) => (
                  <div className="exr-row" key={r.name}>
                    <span className="exr-pos">{r.state === "curso" ? "•" : i + 1}</span>
                    <span className="av" style={{ background: avaFor(r.name) }}>{initials(r.name)}</span>
                    <div className="exr-nm"><b>{r.name}</b><span>{r.time}</span></div>
                    {r.state === "curso"
                      ? <span className="exr-live">En curso</span>
                      : <span className="exr-grade" style={{ color: gradeColor(r.grade) }}>{r.grade}<i>/100</i></span>}
                  </div>
                ))}
              </div>
            </div>
          </React.Fragment>
        ) : (
          <div className="gd-section">
            <div className="gd-sechead"><h4>Preguntas <span>· {e.questions.length}</span></h4><button className="gd-mini">＋ Añadir</button></div>
            <div className="ex-qlist">
              {e.questions.map((q, i) => (
                <div className="exq-row" key={i}>
                  <span className="exq-num">{i + 1}</span>
                  <div className="exq-main">
                    <p>{q.q}</p>
                    <span className="exq-type"><span className="exq-tic">{QTYPE[q.type].ic}</span>{QTYPE[q.type].lbl}</span>
                  </div>
                  <span className="exq-pts">{q.pts} pts</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="gd-footer">
          {e.status === "borrador" ? (
            <React.Fragment>
              <button className="btn-soft">Editar</button>
              <button className="btn-pri">Programar examen →</button>
            </React.Fragment>
          ) : e.status === "finalizado" ? (
            <React.Fragment>
              <button className="btn-soft">Duplicar</button>
              <button className="btn-pri">Exportar resultados →</button>
            </React.Fragment>
          ) : (
            <React.Fragment>
              <button className="btn-soft">Editar</button>
              <button className="btn-pri">{e.status === "curso" ? "Ver en vivo →" : "Vista previa →"}</button>
            </React.Fragment>
          )}
        </div>
      </aside>
    </div>
  );
}

/* ---- root ---- */
function ExamsView() {
  const [exams] = useStateE(EXAMS_SEED);
  const [tab, setTab] = useStateE("todos");
  const [open, setOpen] = useStateE(null);

  const counts = useMemoE(() => ({
    todos: exams.length,
    curso: exams.filter(e => e.status === "curso").length,
    programado: exams.filter(e => e.status === "programado").length,
    finalizado: exams.filter(e => e.status === "finalizado").length,
    borrador: exams.filter(e => e.status === "borrador").length,
  }), [exams]);

  const list = useMemoE(() => tab === "todos" ? exams : exams.filter(e => e.status === tab), [exams, tab]);

  const TABS = [
    { id: "todos", lbl: "Todos", n: counts.todos },
    { id: "curso", lbl: "En curso", n: counts.curso },
    { id: "programado", lbl: "Programados", n: counts.programado },
    { id: "finalizado", lbl: "Finalizados", n: counts.finalizado },
    { id: "borrador", lbl: "Borradores", n: counts.borrador },
  ];

  return (
    <React.Fragment>
      <div className="tc-head">
        <div className="ttl">
          <h1>Exámenes</h1>
          <p>Crea evaluaciones formales y revisa los resultados. Las calificaciones combinan la lectura de KatIA con tu ajuste.</p>
        </div>
        <div className="head-side">
          <button className="btn-pri">＋ Crear examen</button>
        </div>
      </div>

      <div className="ex-filterbar">
        {TABS.map(tb => (
          <button key={tb.id} className={"ex-filter" + (tab === tb.id ? " on" : "")} onClick={() => setTab(tb.id)}>
            {tb.lbl} <span className="n">{tb.n}</span>
          </button>
        ))}
      </div>

      <div className="ex-grid">
        {list.map(e => <ExamCard key={e.id} e={e} onOpen={setOpen} />)}
      </div>

      {open ? <ExamDrawer e={open} onClose={() => setOpen(null)} /> : null}
    </React.Fragment>
  );
}

Object.assign(window, { EXAMS_SEED, EX_STATUS, scoreDist, examAvg, examTotalPts, ExamCard, ExamDrawer, ExamsView });
