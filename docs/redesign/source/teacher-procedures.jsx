/* Oulad teacher console — Window 3: Procedimientos (math procedure review) */
const { useState: useStateP, useMemo: useMemoP, useEffect: useEffectP } = React;

/* ---- review queue data ---- */
const PROCS_SEED = [
  {
    id: "p1", name: "Daniel Quiroga", user: "dani_q", topic: "algebra",
    problem: "Resolver para x:  2x + 7 = 3x − 5", submitted: "hace 35 min",
    reason: "Apelación del estudiante", status: "pending",
    steps: [
      { expr: "2x + 7 = 3x − 5", note: "Ecuación original" },
      { expr: "7 + 5 = 3x − 2x", note: "Pasa términos: variables a un lado, constantes al otro" },
      { expr: "12 = x" },
      { expr: "x = 12", final: true },
    ],
    correct: "x = 12",
    ai: {
      verdict: "incorrect", conf: 61, grade: 68,
      note: "Posible error de signo al mover 2x al lado derecho.",
      rubric: [
        { k: "Planteamiento", max: 30, score: 28, note: "Identifica correctamente la ecuación" },
        { k: "Procedimiento", max: 40, score: 28, note: "Pasos válidos, baja certeza en el reordenamiento" },
        { k: "Resultado", max: 30, score: 12, note: "KatIA no logró verificar el valor final" },
      ],
    },
  },
  {
    id: "p2", name: "Antonia Vega", user: "anto_v", topic: "trigonometria",
    problem: "Halla todos los valores de θ en [0°, 360°):  sin θ = ½", submitted: "hace 2 h",
    reason: "IA no segura", status: "pending",
    steps: [
      { expr: "sin θ = ½" },
      { expr: "θ = sin⁻¹(½) = 30°", note: "Solución del primer cuadrante" },
      { expr: "θ = 30°", final: true, flag: true, note: "Falta la solución del segundo cuadrante (150°)" },
    ],
    correct: "θ = 30°  y  θ = 150°",
    ai: {
      verdict: "incorrect", conf: 94, grade: 55,
      note: "Respuesta incompleta: omite θ = 150°.",
      rubric: [
        { k: "Planteamiento", max: 30, score: 28, note: "Plantea bien la ecuación trigonométrica" },
        { k: "Procedimiento", max: 40, score: 27, note: "Resuelve el primer cuadrante correctamente" },
        { k: "Resultado", max: 30, score: 0, note: "Solución incompleta: falta θ = 150°" },
      ],
    },
  },
  {
    id: "p3", name: "Camila Suárez", user: "cami_s", topic: "geometria",
    problem: "Área de un triángulo de base 12 cm y altura 5 cm", submitted: "hace 4 h",
    reason: "Error de procedimiento", status: "pending",
    steps: [
      { expr: "A = b × h", flag: true, note: "La fórmula del triángulo es (b × h) ÷ 2" },
      { expr: "A = 12 × 5 = 60" },
      { expr: "A = 60 cm²", final: true },
    ],
    correct: "A = 30 cm²",
    ai: {
      verdict: "incorrect", conf: 97, grade: 35,
      note: "Usó la fórmula del rectángulo; al triángulo le falta dividir entre 2.",
      rubric: [
        { k: "Planteamiento", max: 30, score: 8, note: "Fórmula incorrecta para el triángulo" },
        { k: "Procedimiento", max: 40, score: 17, note: "Aritmética correcta sobre fórmula errónea" },
        { k: "Resultado", max: 30, score: 10, note: "Resultado al doble del esperado" },
      ],
    },
  },
  {
    id: "p4", name: "Mateo Restrepo", user: "mateo_r", topic: "algebra",
    problem: "Resolver:  3(x − 4) = 2x + 5", submitted: "ayer",
    reason: "Revisión rutinaria", status: "approved",
    steps: [
      { expr: "3(x − 4) = 2x + 5" },
      { expr: "3x − 12 = 2x + 5", note: "Distribuye el 3" },
      { expr: "3x − 2x = 5 + 12" },
      { expr: "x = 17", final: true },
    ],
    correct: "x = 17",
    ai: {
      verdict: "correct", conf: 99, grade: 100,
      note: "Procedimiento completo y correcto.",
      rubric: [
        { k: "Planteamiento", max: 30, score: 30, note: "Distribución correcta" },
        { k: "Procedimiento", max: 40, score: 40, note: "Todos los pasos justificados" },
        { k: "Resultado", max: 30, score: 30, note: "Respuesta correcta" },
      ],
    },
    grade: 100,
  },
  {
    id: "p5", name: "Valentina Ortiz", user: "vale_o", topic: "geometria",
    problem: "Hipotenusa de un triángulo rectángulo de catetos 3 y 4", submitted: "ayer",
    reason: "Revisión rutinaria", status: "approved",
    steps: [
      { expr: "c = √(3² + 4²)", note: "Teorema de Pitágoras" },
      { expr: "c = √(9 + 16) = √25" },
      { expr: "c = 5", final: true },
    ],
    correct: "c = 5",
    ai: {
      verdict: "correct", conf: 98, grade: 98,
      note: "Aplicación correcta del teorema de Pitágoras.",
      rubric: [
        { k: "Planteamiento", max: 30, score: 30, note: "Teorema bien identificado" },
        { k: "Procedimiento", max: 40, score: 39, note: "Cálculo claro y ordenado" },
        { k: "Resultado", max: 30, score: 29, note: "Respuesta correcta" },
      ],
    },
    grade: 100,
  },
  {
    id: "p6", name: "Joaquín Beltrán", user: "joaco_b", topic: "algebra",
    problem: "Resolver:  x ÷ 3 = 6", submitted: "hace 2 d",
    reason: "Error de procedimiento", status: "rejected",
    steps: [
      { expr: "x ÷ 3 = 6" },
      { expr: "x = 6 − 3 = 3", final: true, flag: true, note: "Para despejar x debe multiplicar por 3, no restar" },
    ],
    correct: "x = 18",
    ai: {
      verdict: "incorrect", conf: 91, grade: 20,
      note: "Debe multiplicar ambos lados por 3: x = 6 × 3 = 18.",
      rubric: [
        { k: "Planteamiento", max: 30, score: 12, note: "Reconoce la ecuación pero no la operación inversa" },
        { k: "Procedimiento", max: 40, score: 5, note: "Resta en lugar de multiplicar" },
        { k: "Resultado", max: 30, score: 3, note: "Resultado incorrecto" },
      ],
    },
    grade: 25,
  },
];

/* ---- grade helpers ---- */
function gradeColor(g) {
  if (g >= 80) return "#34d399";
  if (g >= 60) return "var(--gold)";
  if (g >= 40) return "#fb923c";
  return "#f87171";
}
function gradeLabel(g) {
  if (g >= 90) return "Sobresaliente";
  if (g >= 80) return "Notable";
  if (g >= 60) return "Aprobado";
  if (g >= 40) return "Insuficiente";
  return "Deficiente";
}

const AI_META = {
  correct:   { lbl: "Correcto",   fg: "#34d399", icon: "✓" },
  incorrect: { lbl: "Incorrecto", fg: "#f87171", icon: "✕" },
  unsure:    { lbl: "Sin certeza", fg: "var(--gold)", icon: "?" },
};
const STATUS_META = {
  pending:  { lbl: "Pendiente", fg: "var(--gold)", bg: "color-mix(in srgb, var(--gold) 14%, transparent)" },
  approved: { lbl: "Aprobado",  fg: "#34d399", bg: "color-mix(in srgb, #34d399 14%, transparent)" },
  rejected: { lbl: "Corregido", fg: "#f87171", bg: "color-mix(in srgb, #f87171 14%, transparent)" },
};

/* ---- queue item ---- */
function QueueItem({ p, active, onClick }) {
  const t = topicById(p.topic);
  const sm = STATUS_META[p.status];
  const shown = p.status !== "pending" ? p.grade : p.ai.grade;
  return (
    <button className={"pq-card" + (active ? " on" : "")} style={{ "--c": t.color }} onClick={onClick}>
      <div className="pq-top">
        <span className="av" style={{ background: avaFor(p.name) }}>{initials(p.name)}</span>
        <div className="pq-id">
          <b>{p.name}</b>
          <span><span className="gd" style={{ background: t.color }}></span>{t.name} · {p.submitted}</span>
        </div>
        <span className="pq-grade" style={{ color: gradeColor(shown), borderColor: "color-mix(in srgb, " + gradeColor(shown) + " 45%, transparent)" }} title={p.status !== "pending" ? "Calificación final" : "Sugerencia de KatIA"}>{shown}</span>
      </div>
      <div className="pq-problem">{p.problem}</div>
      <div className="pq-foot-row">
        <span className="pq-status" style={{ color: sm.fg, background: sm.bg }}>{sm.lbl}</span>
        <span className="pq-reason">{p.status === "pending" ? "⚑ " + p.reason : "✦ " + p.reason}</span>
      </div>
    </button>
  );
}

/* ---- grade panel (KatIA suggests, teacher adjusts) ---- */
function GradePanel({ p, grade, setGrade, locked }) {
  const col = gradeColor(grade);
  const suggested = p.ai.grade;
  const adjusted = grade !== suggested;
  const r = 30, circ = 2 * Math.PI * r, dash = (grade / 100) * circ;
  const step = (d) => setGrade(Math.max(0, Math.min(100, grade + d)));
  return (
    <div className="grade-panel" style={{ "--gc": col }}>
      <div className="gp-head">
        <span className="pd-lbl" style={{ margin: 0 }}>Calificación</span>
        {adjusted
          ? <span className="gp-src adj">Ajustada por el profesor</span>
          : <span className="gp-src">Sugerida por KatIA</span>}
      </div>

      <div className="gp-main">
        <div className="gp-dial">
          <svg viewBox="0 0 72 72" width="72" height="72">
            <circle cx="36" cy="36" r={r} fill="none" stroke="var(--surface-3)" strokeWidth="7" />
            <circle cx="36" cy="36" r={r} fill="none" stroke={col} strokeWidth="7" strokeLinecap="round"
              strokeDasharray={circ} strokeDashoffset={circ - dash} transform="rotate(-90 36 36)" style={{ transition: "stroke-dashoffset .3s, stroke .3s" }} />
          </svg>
          <div className="gp-num"><b>{grade}</b><span>/100</span></div>
        </div>

        <div className="gp-ctrl">
          <div className="gp-toprow">
            <span className="gp-judge" style={{ color: col }}>{gradeLabel(grade)}</span>
            {adjusted && !locked ? <button className="gp-reset" onClick={() => setGrade(suggested)}>↺ KatIA: {suggested}</button> : null}
          </div>
          <div className="gp-slider-row">
            <button className="gp-step" onClick={() => step(-1)} disabled={locked}>−</button>
            <input type="range" min="0" max="100" value={grade} disabled={locked}
              onChange={e => setGrade(+e.target.value)}
              style={{ "--pct": grade + "%" }} />
            <button className="gp-step" onClick={() => step(1)} disabled={locked}>+</button>
          </div>
          {!locked ? (
            <div className="gp-presets">
              {[0, 60, 80, 100].map(v => (
                <button key={v} className={"gp-chip" + (grade === v ? " on" : "")} onClick={() => setGrade(v)}>{v}</button>
              ))}
            </div>
          ) : null}
        </div>
      </div>

      <div className="gp-rubric">
        <span className="pd-lbl">Desglose de KatIA</span>
        {p.ai.rubric.map((cr, i) => {
          const pct = Math.round((cr.score / cr.max) * 100);
          return (
            <div className="rub-row" key={i}>
              <div className="rub-top">
                <b>{cr.k}</b>
                <span className="rub-pts">{cr.score}<i>/{cr.max}</i></span>
              </div>
              <div className="rub-bar"><i style={{ width: pct + "%", background: gradeColor(pct) }}></i></div>
              <span className="rub-note">{cr.note}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ---- procedure detail ---- */
function ProcedureDetail({ p, onResolve }) {
  const [note, setNote] = useStateP("");
  const [grade, setGrade] = useStateP(0);
  useEffectP(() => {
    setNote("");
    if (p) setGrade(p.status !== "pending" ? p.grade : p.ai.grade);
  }, [p && p.id]);
  if (!p) return (
    <div className="proc-detail empty"><div className="em-ic">🧮</div><p>Selecciona un procedimiento de la cola para revisarlo.</p></div>
  );
  const t = topicById(p.topic);
  const ai = AI_META[p.ai.verdict];
  const resolved = p.status !== "pending";

  return (
    <div className="proc-detail">
      <div className="pd-head" style={{ "--c": t.color }}>
        <div className="pd-htop">
          <span className="pd-chip" style={{ color: t.color, background: "color-mix(in srgb, " + t.color + " 14%, transparent)" }}>
            <span className="gd" style={{ background: t.color }}></span>{t.name}
          </span>
          <span className="pd-when">Enviado {p.submitted}</span>
        </div>
        <div className="pd-who">
          <span className="av" style={{ background: avaFor(p.name) }}>{initials(p.name)}</span>
          <div><b>{p.name}</b><span>@{p.user}</span></div>
        </div>
      </div>

      <div className="pd-body">
        <div className="pd-problem">
          <span className="pd-lbl">Enunciado</span>
          <p className="math">{p.problem}</p>
        </div>

        <span className="pd-lbl">Procedimiento del estudiante</span>
        <div className="proc-steps">
          {p.steps.map((s, i) => (
            <div className={"ps-row" + (s.flag ? " flag" : "") + (s.final ? " final" : "")} key={i}>
              <span className="ps-dot">{s.flag ? "!" : i + 1}</span>
              <div className="ps-main">
                <div className="ps-expr math">{s.expr}</div>
                {s.note ? <div className={"ps-note" + (s.flag ? " flag" : "")}>{s.note}</div> : null}
              </div>
            </div>
          ))}
        </div>

        <div className="pd-answers">
          <div className="pd-ans">
            <span className="pd-lbl">Respuesta del estudiante</span>
            <p className="math">{p.steps.find(s => s.final)?.expr || "—"}</p>
          </div>
          <div className="pd-ans correct">
            <span className="pd-lbl">Respuesta esperada</span>
            <p className="math">{p.correct}</p>
          </div>
        </div>

        <div className="ai-verdict" style={{ "--av": ai.fg }}>
          <div className="av-head">
            <span className="av-dot"></span>
            <b>Lectura de KatIA</b>
            <span className="av-tag" style={{ color: ai.fg }}><span className="av-ic">{ai.icon}</span>{ai.lbl}</span>
            <span className="av-conf">{p.ai.conf}% confianza</span>
          </div>
          <p>{p.ai.note}</p>
        </div>

        <GradePanel p={p} grade={grade} setGrade={setGrade} locked={resolved} />
      </div>

      <div className="pd-actions">
        {resolved ? (
          <div className="pd-resolved" style={{ color: STATUS_META[p.status].fg }}>
            <span className="pd-res-grade" style={{ color: gradeColor(p.grade) }}>{p.grade}<i>/100</i></span>
            <span>{p.status === "approved" ? "Procedimiento aprobado" : "Marcado como incorrecto — comentario enviado"}</span>
            <button className="pd-reopen" onClick={() => onResolve(p.id, "pending", grade)}>Reabrir</button>
          </div>
        ) : (
          <React.Fragment>
            <textarea className="pd-note" placeholder="Comentario para el estudiante (opcional)…" value={note} onChange={e => setNote(e.target.value)} />
            <div className="pd-btns">
              <button className="btn-reject" onClick={() => onResolve(p.id, "rejected", grade)}>✕ Marcar incorrecto</button>
              <button className="btn-approve" onClick={() => onResolve(p.id, "approved", grade)}>✓ Aprobar con {grade}</button>
            </div>
          </React.Fragment>
        )}
      </div>
    </div>
  );
}

/* ---- root ---- */
function ProceduresView() {
  const [procs, setProcs] = useStateP(PROCS_SEED);
  const [tab, setTab] = useStateP("pending");
  const [sel, setSel] = useStateP("p1");

  const counts = useMemoP(() => ({
    pending: procs.filter(p => p.status === "pending").length,
    reviewed: procs.filter(p => p.status !== "pending").length,
    all: procs.length,
  }), [procs]);

  const list = useMemoP(() => procs.filter(p =>
    tab === "all" ? true : tab === "pending" ? p.status === "pending" : p.status !== "pending"
  ), [procs, tab]);

  useEffectP(() => {
    if (!list.find(p => p.id === sel)) setSel(list[0]?.id || null);
  }, [list]);

  const selected = procs.find(p => p.id === sel) || null;
  const resolve = (id, status, grade) => setProcs(ps => ps.map(p => p.id === id ? { ...p, status, grade: status === "pending" ? p.grade : grade } : p));

  const TABS = [
    { id: "pending", lbl: "Pendientes", n: counts.pending },
    { id: "reviewed", lbl: "Revisados", n: counts.reviewed },
    { id: "all", lbl: "Todos", n: counts.all },
  ];

  return (
    <React.Fragment>
      <div className="tc-head">
        <div className="ttl">
          <h1>Procedimientos</h1>
          <p>Revisa los procedimientos matemáticos paso a paso. KatIA marca los dudosos; tú tienes la última palabra.</p>
        </div>
        <div className="head-side">
          <div className="tc-range proc-tabs">
            {TABS.map(tb => (
              <button key={tb.id} className={tab === tb.id ? "on" : ""} onClick={() => setTab(tb.id)}>
                {tb.lbl} <span className="n">{tb.n}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="proc-layout">
        <div className="proc-queue">
          {list.length === 0 ? (
            <div className="proc-q-empty"><div className="em-ic">🎉</div><p>Nada por aquí. La cola está limpia.</p></div>
          ) : list.map(p => (
            <QueueItem key={p.id} p={p} active={p.id === sel} onClick={() => setSel(p.id)} />
          ))}
        </div>
        <ProcedureDetail p={selected} onResolve={resolve} />
      </div>
    </React.Fragment>
  );
}

Object.assign(window, { PROCS_SEED, gradeColor, gradeLabel, QueueItem, GradePanel, ProcedureDetail, ProceduresView });
