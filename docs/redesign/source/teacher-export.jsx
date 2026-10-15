/* Oulad teacher console — Window 5: Exportar datos (data export) */
const { useState: useStateX, useMemo: useMemoX } = React;

/* ---- format meta ---- */
const FORMATS = [
  { id: "csv",  lbl: "CSV",   ext: ".csv",  ic: "≡", note: "Texto separado por comas · universal" },
  { id: "xlsx", lbl: "Excel", ext: ".xlsx", ic: "▦", note: "Hoja de cálculo con formato" },
  { id: "pdf",  lbl: "PDF",   ext: ".pdf",  ic: "▤", note: "Reporte imprimible" },
];

/* ---- datasets: columns + row builders from live data ---- */
const DATASETS = [
  {
    id: "estudiantes", name: "Estudiantes", ic: "🎓",
    desc: "Roster completo con ELO, rango, aciertos e intentos.",
    cols: ["Nombre", "Usuario", "Curso", "ELO", "Rango", "Aciertos", "Intentos", "Última actividad"],
    rows: () => STUDENTS.map(s => [
      s.name, "@" + s.user, topicById(s.topic).name, s.elo, rankFor(s.elo).name, s.acc + "%", s.attempts, s.last,
    ]),
  },
  {
    id: "calificaciones", name: "Calificaciones de exámenes", ic: "📋",
    desc: "Resultados por estudiante de los exámenes finalizados.",
    cols: ["Estudiante", "Examen", "Curso", "Calificación", "Tiempo", "Fecha"],
    rows: () => EXAMS_SEED.filter(e => e.status === "finalizado").flatMap(e =>
      e.results.filter(r => r.state === "entregado").map(r => [
        r.name, e.title, topicById(e.topic).name, r.grade + "/100", r.time, e.date,
      ])
    ),
  },
  {
    id: "procedimientos", name: "Procedimientos", ic: "📝",
    desc: "Revisiones de procedimientos con nota de KatIA y del profesor.",
    cols: ["Estudiante", "Tema", "Problema", "Veredicto KatIA", "Confianza", "Nota", "Estado"],
    rows: () => PROCS_SEED.map(p => [
      p.name, topicById(p.topic).name, p.problem,
      AI_META[p.ai.verdict].lbl, p.ai.conf + "%",
      (p.status !== "pending" ? p.grade : p.ai.grade) + "/100",
      STATUS_META[p.status].lbl,
    ]),
  },
  {
    id: "grupos", name: "Grupos", ic: "👥",
    desc: "Resumen de cada grupo: tamaño, ELO promedio y dominio.",
    cols: ["Grupo", "Curso", "Código", "Estudiantes", "ELO promedio", "Dominio", "Objetivo"],
    rows: () => GROUPS_SEED.map(g => {
      const st = groupStats(g);
      return [g.name, topicById(g.topic).name, g.code, st.n, st.elo, st.acc + "%", g.goal + "%"];
    }),
  },
  {
    id: "actividad", name: "Actividad semanal", ic: "📈",
    desc: "Intentos registrados por día en la última semana.",
    cols: ["Día", "Intentos"],
    rows: () => ACTIVITY.map(a => [a.d, a.v]),
  },
];

/* ---- recent exports (seeded history) ---- */
const RECENTS_SEED = [
  { name: "Estudiantes", fmt: "xlsx", when: "Ayer · 16:42", size: "18 KB", scope: "Todos los cursos" },
  { name: "Calificaciones de exámenes", fmt: "csv", when: "28 may · 09:15", size: "6 KB", scope: "Álgebra · 10°B" },
  { name: "Procedimientos", fmt: "pdf", when: "25 may · 11:03", size: "112 KB", scope: "Todos los cursos" },
];

/* ---- CSV builder + real download ---- */
function toCSV(cols, rows) {
  const esc = (v) => {
    const s = String(v);
    return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  };
  return [cols.map(esc).join(","), ...rows.map(r => r.map(esc).join(","))].join("\n");
}

/* ---- dataset selector card ---- */
function DatasetCard({ d, rowCount, active, onClick }) {
  return (
    <button className={"ds-card" + (active ? " on" : "")} onClick={onClick}>
      <span className="ds-ic">{d.ic}</span>
      <div className="ds-body">
        <b>{d.name}</b>
        <span>{d.desc}</span>
      </div>
      <span className="ds-count">{rowCount}<i>filas</i></span>
    </button>
  );
}

/* ---- root ---- */
function ExportView() {
  const [dsId, setDsId] = useStateX("estudiantes");
  const [fmt, setFmt] = useStateX("csv");
  const [scope, setScope] = useStateX("todos");
  const [range, setRange] = useStateX("30d");
  const [hiddenCols, setHiddenCols] = useStateX({});
  const [recents, setRecents] = useStateX(RECENTS_SEED);
  const [toast, setToast] = useStateX(null);
  const [busy, setBusy] = useStateX(false);

  const ds = DATASETS.find(d => d.id === dsId);
  const allRows = useMemoX(() => ds.rows(), [dsId]);

  /* scope filter applies to datasets that have a course column */
  const courseColIdx = ds.cols.findIndex(c => c === "Curso");
  const filtered = useMemoX(() => {
    if (scope === "todos" || courseColIdx < 0) return allRows;
    const name = topicById(scope).name;
    return allRows.filter(r => r[courseColIdx] === name);
  }, [allRows, scope, courseColIdx]);

  const visIdx = ds.cols.map((_, i) => i).filter(i => !hiddenCols[ds.id + ":" + i]);
  const toggleCol = (i) => setHiddenCols(h => ({ ...h, [ds.id + ":" + i]: !h[ds.id + ":" + i] }));

  const fmtMeta = FORMATS.find(f => f.id === fmt);
  const previewRows = filtered.slice(0, 6);

  const doExport = () => {
    const cols = visIdx.map(i => ds.cols[i]);
    const rows = filtered.map(r => visIdx.map(i => r[i]));
    if (fmt === "csv") {
      const blob = new Blob([toCSV(cols, rows)], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = "oulad_" + ds.id + ".csv";
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      flash("Archivo CSV descargado", rows.length);
    } else {
      setBusy(true);
      setTimeout(() => { setBusy(false); flash("Reporte " + fmtMeta.lbl + " generado", rows.length); }, 1100);
    }
    setRecents(rs => [{
      name: ds.name, fmt, when: "Justo ahora", size: estSize(rows.length, fmt),
      scope: scope === "todos" ? "Todos los cursos" : topicById(scope).name,
    }, ...rs].slice(0, 5));
  };
  const flash = (msg, n) => { setToast({ msg, n }); setTimeout(() => setToast(null), 2600); };
  const estSize = (n, f) => {
    const base = f === "pdf" ? n * 4.2 + 40 : f === "xlsx" ? n * 1.4 + 9 : n * 0.5 + 1;
    return Math.round(base) + " KB";
  };

  return (
    <React.Fragment>
      <div className="tc-head">
        <div className="ttl">
          <h1>Exportar datos</h1>
          <p>Descarga el progreso de tus estudiantes en el formato que necesites. Elige un conjunto, ajústalo y expórtalo.</p>
        </div>
      </div>

      <div className="xp-layout">
        {/* left: dataset selector */}
        <div className="xp-datasets">
          <span className="xp-lbl">Conjunto de datos</span>
          {DATASETS.map(d => (
            <DatasetCard key={d.id} d={d} rowCount={d.rows().length} active={d.id === dsId} onClick={() => setDsId(d.id)} />
          ))}
        </div>

        {/* right: config + preview */}
        <div className="xp-config">
          <div className="xp-card">
            <span className="xp-lbl">Formato</span>
            <div className="xp-formats">
              {FORMATS.map(f => (
                <button key={f.id} className={"xp-fmt" + (fmt === f.id ? " on" : "")} onClick={() => setFmt(f.id)}>
                  <span className="xpf-ic">{f.ic}</span>
                  <b>{f.lbl}</b>
                  <span className="xpf-note">{f.note}</span>
                </button>
              ))}
            </div>

            <div className="xp-filters">
              <label className="xp-field">
                <span>Curso</span>
                <select value={scope} onChange={e => setScope(e.target.value)} disabled={courseColIdx < 0}>
                  <option value="todos">Todos los cursos</option>
                  {TOPICS.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </label>
              <div className="xp-field">
                <span>Periodo</span>
                <div className="xp-range">
                  {["7d", "30d", "todo"].map(r => (
                    <button key={r} className={range === r ? "on" : ""} onClick={() => setRange(r)}>
                      {r === "todo" ? "Todo" : r}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <span className="xp-lbl">Columnas <span className="xp-lbl-n">{visIdx.length}/{ds.cols.length}</span></span>
            <div className="xp-cols">
              {ds.cols.map((c, i) => {
                const on = !hiddenCols[ds.id + ":" + i];
                return (
                  <button key={i} className={"xp-colchip" + (on ? " on" : "")} onClick={() => toggleCol(i)}>
                    <span className="xpc-box">{on ? "✓" : ""}</span>{c}
                  </button>
                );
              })}
            </div>
          </div>

          {/* preview */}
          <div className="xp-card xp-preview">
            <div className="xp-prev-head">
              <span className="xp-lbl" style={{ margin: 0 }}>Vista previa</span>
              <span className="xp-prev-meta">{filtered.length} filas · {visIdx.length} columnas</span>
            </div>
            <div className="xp-table-wrap">
              <table className="xp-table">
                <thead>
                  <tr>{visIdx.map(i => <th key={i}>{ds.cols[i]}</th>)}</tr>
                </thead>
                <tbody>
                  {previewRows.map((r, ri) => (
                    <tr key={ri}>{visIdx.map(i => <td key={i}>{r[i]}</td>)}</tr>
                  ))}
                </tbody>
              </table>
              {filtered.length === 0 ? <div className="xp-empty">Sin filas para este filtro.</div> : null}
            </div>
            {filtered.length > previewRows.length ? (
              <div className="xp-more">+ {filtered.length - previewRows.length} filas más en el archivo</div>
            ) : null}

            <div className="xp-export-bar">
              <div className="xp-export-info">
                <b>oulad_{ds.id}{fmtMeta.ext}</b>
                <span>{fmtMeta.lbl} · ~{estSize(filtered.length, fmt)}</span>
              </div>
              <button className="btn-pri xp-export-btn" onClick={doExport} disabled={busy || filtered.length === 0}>
                {busy ? "Generando…" : "↓ Exportar " + fmtMeta.lbl}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* recent exports */}
      <div className="xp-recents">
        <span className="xp-lbl">Exportaciones recientes</span>
        <div className="xp-recent-list">
          {recents.map((r, i) => {
            const fm = FORMATS.find(f => f.id === r.fmt);
            return (
              <div className="xp-recent" key={i}>
                <span className={"xp-rfmt fmt-" + r.fmt}>{fm.lbl}</span>
                <div className="xp-rbody">
                  <b>{r.name}</b>
                  <span>{r.scope} · {r.size}</span>
                </div>
                <span className="xp-rwhen">{r.when}</span>
                <button className="xp-rdl" title="Volver a descargar">↓</button>
              </div>
            );
          })}
        </div>
      </div>

      {toast ? (
        <div className="xp-toast">
          <span className="xpt-ic">✓</span>
          <div><b>{toast.msg}</b><span>{toast.n} filas exportadas</span></div>
        </div>
      ) : null}
    </React.Fragment>
  );
}

Object.assign(window, { FORMATS, DATASETS, toCSV, DatasetCard, ExportView });
