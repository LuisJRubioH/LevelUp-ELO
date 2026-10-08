/**
 * pages/Teacher/Dashboard.tsx — Panel Docente (rediseño)
 * ======================================================
 * Portado de docs/redesign/source/teacher-dashboard.jsx, alimentado con
 * datos REALES de teacherApi.dashboard() + teacherApi.metrics().
 * Vistas: Estudiantes (tabla) · Ranking (podio + lista) · Métricas
 * (dominio por tópico, distribución de ELO, actividad, atención).
 * Estilos en TeacherConsole.css (.lue-tc).
 *
 * Pendiente (re-integrar del dashboard previo): drawer de detalle de
 * estudiante + análisis pedagógico con IA.
 */

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { RankPill } from "../../components/ELO/RankBadge";
import { teacherApi, type StudentSummary } from "../../api/teacher";
import { useSettingsStore } from "../../stores/settingsStore";

/* ── helpers de presentación ─────────────────────────────────────────────── */
/** Spec 001: ratings and labels come from the API (display_rating, rank_label) as given. */
const fmtRating = (v: number | null | undefined) => (v == null ? "Diagnóstico pendiente" : String(v));
const byRatingDesc = (a: StudentSummary, b: StudentSummary) =>
  (b.display_rating ?? -1) - (a.display_rating ?? -1);
const needsAttention = (s: StudentSummary, acc: number) =>
  acc < 60 || (s.display_rating != null && s.display_rating < 1100);
/** A group statistic over rated students' display values; null when nobody is rated yet. */
const meanShown = (xs: StudentSummary[]) => {
  const v = xs.map((x) => x.display_rating).filter((x): x is number => x != null);
  return v.length ? Math.round(v.reduce((a, b) => a + b, 0) / v.length) : null;
};
const AVAS = [
  "linear-gradient(140deg,#8b5cf6,#6366f1)",
  "linear-gradient(140deg,#2dd4bf,#0ea5e9)",
  "linear-gradient(140deg,#f59e0b,#ef4444)",
  "linear-gradient(140deg,#ec4899,#8b5cf6)",
  "linear-gradient(140deg,#10b981,#22d3ee)",
  "linear-gradient(140deg,#f43f5e,#f59e0b)",
];
const AVAS_SOLID = ["#8b5cf6", "#2dd4bf", "#f59e0b", "#ec4899", "#10b981", "#f43f5e"];
const initials = (n: string) =>
  n.split(/[\s_.]+/).slice(0, 2).map((w) => w[0] ?? "").join("").toUpperCase() ||
  n.slice(0, 2).toUpperCase();
const avaFor = (n: string) => AVAS[(n.charCodeAt(0) + n.length) % AVAS.length];
const accColor = (a: number) => (a >= 80 ? "#34d399" : a >= 65 ? "#fbbf24" : "#f87171");
/** accuracy puede venir como fracción (0–1) o porcentaje (0–100). */
const toPct = (a: number) => Math.round(a <= 1 ? a * 100 : a);
const fmtLast = (s: string | null) => (s ? String(s).slice(0, 10) : "—");

/* ── stat card ───────────────────────────────────────────────────────────── */
function StatCard({
  ic,
  color,
  val,
  lbl,
  sub,
}: {
  ic: string;
  color: string;
  val: string | number;
  lbl: string;
  sub?: string;
}) {
  return (
    <div className="stat-card" style={{ "--c": color } as React.CSSProperties}>
      <div className="sc-top">
        <span className="sc-ic">{ic}</span>
      </div>
      <div className="sc-val">{val}</div>
      <div className="sc-lbl">{lbl}</div>
      {sub ? <div className="sc-sub">{sub}</div> : null}
    </div>
  );
}

/* ── vista estudiantes ───────────────────────────────────────────────────── */
function StudentsView({
  students,
  onSelect,
}: {
  students: StudentSummary[];
  onSelect: (s: StudentSummary) => void;
}) {
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<"elo" | "acc" | "name">("elo");
  const rows = useMemo(() => {
    let r = students.filter((s) => s.username.toLowerCase().includes(q.toLowerCase()));
    r = [...r].sort((a, b) =>
      sort === "elo"
        ? byRatingDesc(a, b)
        : sort === "acc"
        ? toPct(b.accuracy) - toPct(a.accuracy)
        : a.username.localeCompare(b.username)
    );
    return r;
  }, [students, q, sort]);

  return (
    <div className="panel">
      <div className="panel-head">
        <h3>
          Estudiantes{" "}
          <span style={{ color: "var(--mute)", fontWeight: 500, fontSize: 13 }}>· {rows.length}</span>
        </h3>
        <div className="ph-side">
          <select className="sort-sel" value={sort} onChange={(e) => setSort(e.target.value as typeof sort)}>
            <option value="elo">Ordenar: ELO</option>
            <option value="acc">Ordenar: Acierto</option>
            <option value="name">Ordenar: Nombre</option>
          </select>
          <div className="search">
            <span className="ic">🔍</span>
            <input placeholder="Buscar estudiante…" value={q} onChange={(e) => setQ(e.target.value)} />
          </div>
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="empty">
          <div className="em-ic">🗒️</div>
          <p>Sin estudiantes para los filtros aplicados.</p>
        </div>
      ) : (
        <div className="stu-table">
          <div className="stu-row head">
            <div>Estudiante</div>
            <div>Grupo</div>
            <div>ELO · Rango</div>
            <div>Acierto</div>
            <div>Actividad</div>
            <div></div>
          </div>
          {rows.map((s) => {
            const rk = s.rank_label;
            const acc = toPct(s.accuracy);
            const attn = needsAttention(s, acc);
            return (
              <div className="stu-row" key={s.user_id}>
                <div className="stu-id">
                  <div className="av" style={{ background: avaFor(s.username) }}>{initials(s.username)}</div>
                  <div className="nm">
                    <b>{s.username}</b>
                    <span>@{s.username}</span>
                  </div>
                </div>
                <div className="stu-group">
                  <span className="gd" style={{ background: "var(--accent)" }} />
                  {s.group_name ?? "Sin grupo"}
                </div>
                <div className="stu-elo">
                  <span className="e">{fmtRating(s.display_rating)}</span>
                  <RankPill label={rk} />
                </div>
                <div className="acc-cell">
                  <div className="av">
                    <span style={{ color: "var(--mute)" }}>{s.total_attempts} int.</span>
                    <b>{acc}%</b>
                  </div>
                  <div className="bar">
                    <i style={{ width: acc + "%", background: accColor(acc) }} />
                  </div>
                </div>
                <div className="stu-last">
                  {fmtLast(s.last_activity)}
                  {attn ? <span className="flag">⚠ Necesita atención</span> : null}
                </div>
                <button className="stu-go" title="Ver perfil" onClick={() => onSelect(s)}>
                  ›
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ── vista ranking ───────────────────────────────────────────────────────── */
function RankingView({ students }: { students: StudentSummary[] }) {
  const sorted = [...students].sort((a, b) => byRatingDesc(a, b));
  const top3 = sorted.slice(0, 3);
  const order = [top3[1], top3[0], top3[2]].filter(Boolean) as StudentSummary[];
  const medals = ["🥇", "🥈", "🥉"];

  return (
    <div className="panel">
      <div className="panel-head">
        <h3>Ranking global</h3>
        <span style={{ fontSize: 12, color: "var(--mute)" }}>Por ELO global</span>
      </div>
      {sorted.length === 0 ? (
        <div className="empty">
          <div className="em-ic">🏆</div>
          <p>Aún no hay estudiantes con actividad.</p>
        </div>
      ) : (
        <>
          <div className="podium">
            {order.map((s) => {
              const realPos = sorted.indexOf(s);
              const rk = s.rank_label;
              return (
                <div className={"pod " + (realPos === 0 ? "p1" : "")} key={s.user_id}>
                  <div className="medal">{medals[realPos]}</div>
                  <div
                    className="av"
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: 12,
                      margin: "10px auto 0",
                      display: "grid",
                      placeItems: "center",
                      color: "#fff",
                      fontFamily: "var(--font-display)",
                      fontWeight: 700,
                      background: avaFor(s.username),
                    }}
                  >
                    {initials(s.username)}
                  </div>
                  <div className="pname">{s.username}</div>
                  <div className="pelo">{fmtRating(s.display_rating)}</div>
                  <RankPill label={rk} />
                </div>
              );
            })}
          </div>
          <div className="rank-list">
            {sorted.slice(3).map((s, i) => (
              <div className="rank-line" key={s.user_id}>
                <div className="pos">{i + 4}</div>
                <div className="who">
                  <div className="av" style={{ background: avaFor(s.username) }}>{initials(s.username)}</div>
                  <div>
                    <b>{s.username}</b>{" "}
                    <span style={{ color: "var(--mute)", fontSize: 12 }}>· {s.group_name ?? "Sin grupo"}</span>
                  </div>
                </div>
                <div className="rl-elo">{fmtRating(s.display_rating)}</div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

/* ── vista métricas ──────────────────────────────────────────────────────── */
const BUCKETS = [
  { label: "<1100", lo: 0, hi: 1100 },
  { label: "1100", lo: 1100, hi: 1300 },
  { label: "1300", lo: 1300, hi: 1500 },
  { label: "1500", lo: 1500, hi: 1700 },
  { label: "1700", lo: 1700, hi: 1900 },
  { label: "1900+", lo: 1900, hi: 99999 },
];

function MetricsView({ students }: { students: StudentSummary[] }) {
  const metricsQ = useQuery({ queryKey: ["teacher-metrics"], queryFn: () => teacherApi.metrics() });
  const m = metricsQ.data;

  const buckets = BUCKETS.map((b) => ({
    ...b,
    n: students.filter(
      (s) => s.display_rating != null && s.display_rating >= b.lo && s.display_rating < b.hi
    ).length,
  }));
  const maxN = Math.max(...buckets.map((b) => b.n), 1);

  const topics = (m?.topic_stats ?? [])
    .slice()
    .sort((a, b) => toPct(b.accuracy) - toPct(a.accuracy))
    .slice(0, 8);

  const attn = students.filter((s) => needsAttention(s, toPct(s.accuracy)));

  // sparkline actividad diaria
  const daily = m?.daily_attempts ?? [];
  const maxAct = Math.max(...daily.map((d) => d.count), 1);
  const w = 320;
  const h = 110;
  const pad = 6;
  const pts = daily.map((d, i) => [
    pad + (daily.length > 1 ? (i * (w - 2 * pad)) / (daily.length - 1) : 0),
    h - pad - (d.count / maxAct) * (h - 2 * pad),
  ]);
  const line = pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ");
  const area = pts.length ? line + ` L${w - pad} ${h - pad} L${pad} ${h - pad} Z` : "";
  const totalAct = daily.reduce((s, d) => s + d.count, 0);

  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <h4>Dominio por tópico</h4>
        <div className="mc-sub">Acierto promedio de los estudiantes en cada curso</div>
        {topics.length === 0 ? (
          <p style={{ color: "var(--mute)", fontSize: 13 }}>Sin datos de tópicos todavía.</p>
        ) : (
          topics.map((t) => {
            const v = toPct(t.accuracy);
            return (
              <div className="mastery-row" key={t.topic}>
                <div className="ml">
                  <span className="gd" style={{ background: "var(--accent-2)" }} />
                  {t.topic}
                </div>
                <div className="mbar">
                  <i style={{ width: v + "%", background: "var(--accent-2)" }} />
                </div>
                <div className="mv">{v}%</div>
              </div>
            );
          })
        )}
      </div>

      <div className="metric-card">
        <h4>Distribución de ELO</h4>
        <div className="mc-sub">Cuántos estudiantes hay en cada rango</div>
        <div className="histo">
          {buckets.map((b) => (
            <div className="col" key={b.label}>
              <div className="cn">{b.n}</div>
              <div className="bar" style={{ height: `${(b.n / maxN) * 100}%` }} />
              <div className="cl">{b.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="metric-card">
        <h4>Actividad reciente</h4>
        <div className="mc-sub">Intentos de práctica por día · {totalAct} en total</div>
        {pts.length === 0 ? (
          <p style={{ color: "var(--mute)", fontSize: 13 }}>Sin actividad registrada.</p>
        ) : (
          <svg className="spark" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
            <defs>
              <linearGradient id="tc-sg" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.4" />
                <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
              </linearGradient>
            </defs>
            <path d={area} fill="url(#tc-sg)" />
            <path
              d={line}
              fill="none"
              stroke="var(--accent)"
              strokeWidth="2.5"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
            {pts.map((p, i) => (
              <circle key={i} cx={p[0]} cy={p[1]} r="3" fill="var(--accent-2)" />
            ))}
          </svg>
        )}
      </div>

      <div className="metric-card">
        <h4>
          Necesitan atención <span style={{ color: "var(--gold)" }}>· {attn.length}</span>
        </h4>
        <div className="mc-sub">Bajo acierto o ELO bajo</div>
        {attn.length === 0 ? (
          <p style={{ color: "var(--mute)", fontSize: 13 }}>Ningún estudiante en riesgo. 🎉</p>
        ) : (
          attn.map((s) => (
            <div className="attn-row" key={s.user_id}>
              <div className="av" style={{ background: avaFor(s.username) }}>{initials(s.username)}</div>
              <div className="ab">
                <b>{s.username}</b>
                <span>
                  ELO {fmtRating(s.display_rating)} · {toPct(s.accuracy)}% acierto
                </span>
              </div>
              <div className="ax">{toPct(s.accuracy)}%</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

/* ── drawer de perfil de estudiante ──────────────────────────────────────── */
function StudentDrawer({ student, onClose }: { student: StudentSummary; onClose: () => void }) {
  const { apiKey, provider } = useSettingsStore();
  const [analysis, setAnalysis] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const rk = student.rank_label;
  const acc = toPct(student.accuracy);

  const runAnalysis = async () => {
    setErr("");
    setLoading(true);
    try {
      const res = await teacherApi.studentAiAnalysis(student.user_id, apiKey || undefined, provider);
      setAnalysis(res.analysis);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "No se pudo generar el análisis.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="stu-backdrop" onClick={onClose} />
      <aside className="stu-drawer" role="dialog" aria-label={`Perfil de ${student.username}`}>
        <div className="sd-head">
          <div className="sd-htop">
            <div className="sd-who">
              <div className="av" style={{ background: avaFor(student.username) }}>{initials(student.username)}</div>
              <div className="nm">
                <b>{student.username}</b>
                <span>{student.group_name ?? "Sin grupo"}</span>
              </div>
            </div>
            <button className="sd-x" onClick={onClose} aria-label="Cerrar">
              ✕
            </button>
          </div>
        </div>

        <div className="sd-stats">
          <div className="sds">
            <span className="l">ELO global</span>
            <b>{fmtRating(student.display_rating)}</b>
            <RankPill label={rk} style={{ alignSelf: "flex-start" }} />
          </div>
          <div className="sds">
            <span className="l">Acierto</span>
            <b style={{ color: accColor(acc) }}>{acc}%</b>
          </div>
          <div className="sds">
            <span className="l">Intentos</span>
            <b>{student.total_attempts}</b>
          </div>
        </div>

        <div className="sd-section">
          <h4>
            Análisis pedagógico con IA
            <button className="sd-ai-btn" onClick={runAnalysis} disabled={loading}>
              {loading ? "Analizando…" : analysis ? "Regenerar" : "Generar"}
            </button>
          </h4>
          {err && <p style={{ color: "#f87171", fontSize: 13, marginBottom: 10 }}>{err}</p>}
          {analysis ? (
            <div className="sd-ai-out">{analysis}</div>
          ) : (
            <p className="sd-ai-hint">
              Genera un resumen del desempeño de {student.username} y recomendaciones pedagógicas a partir de su
              actividad reciente. Usa la API de IA configurada en la barra lateral.
            </p>
          )}
        </div>

        <div className="sd-section">
          <h4>Actividad</h4>
          <p className="sd-ai-hint">
            Última actividad: {fmtLast(student.last_activity)}.{" "}
            {needsAttention(student, acc)
              ? "⚠ Este estudiante puede necesitar atención."
              : "Progreso dentro de lo esperado."}
          </p>
        </div>
      </aside>
    </>
  );
}

/* ── root ────────────────────────────────────────────────────────────────── */
export function TeacherDashboard() {
  const [groupId, setGroupId] = useState<number | "all">("all");
  const [tab, setTab] = useState<"estudiantes" | "ranking" | "metricas">("estudiantes");
  const [range, setRange] = useState("30d");
  const [selected, setSelected] = useState<StudentSummary | null>(null);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["teacher-dashboard"],
    queryFn: () => teacherApi.dashboard(),
    staleTime: 60_000,
  });

  const students = data?.students ?? [];
  const groups = data?.groups ?? [];

  const filtered = useMemo(
    () => (groupId === "all" ? students : students.filter((s) => s.group_id === groupId)),
    [students, groupId]
  );

  const stats = useMemo(() => {
    const n = students.length || 1;
    return {
      groups: groups.length,
      students: students.length,
      elo: meanShown(students),
      acc: Math.round(students.reduce((s, x) => s + toPct(x.accuracy), 0) / n),
    };
  }, [students, groups]);

  if (isLoading) {
    return (
      <div className="tc-soon">
        <div className="box">
          <div className="em-ic">⏳</div>
          <h2>Cargando panel…</h2>
          <p>Trayendo datos del motor ELO.</p>
        </div>
      </div>
    );
  }
  if (isError) {
    return (
      <div className="tc-soon">
        <div className="box">
          <div className="em-ic">⚠️</div>
          <h2>No pudimos cargar el panel</h2>
          <p>Revisa tu conexión e inténtalo de nuevo.</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="tc-head">
        <div className="ttl">
          <h1>Panel Docente</h1>
          <p>Tu vista general de grupos, progreso y dominio. Datos en tiempo real del motor ELO.</p>
        </div>
        <div className="head-side">
          <div className="tc-range">
            {["7d", "30d", "Todo"].map((r) => (
              <button key={r} className={range === r ? "on" : ""} onClick={() => setRange(r)}>
                {r}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="stat-grid">
        <StatCard ic="👥" color="#8b5cf6" val={stats.groups} lbl="Grupos activos" />
        <StatCard ic="🎓" color="#2dd4bf" val={stats.students} lbl="Estudiantes" />
        <StatCard ic="♛" color="#ffd700" val={stats.elo ?? "—"} lbl="ELO promedio" />
        <StatCard ic="🎯" color="#34d399" val={stats.acc + "%"} lbl="Acierto promedio" />
      </div>

      <div className="topic-row">
        <button
          className={"topic-chip" + (groupId === "all" ? " on" : "")}
          style={{ "--c": "#8b5cf6" } as React.CSSProperties}
          onClick={() => setGroupId("all")}
        >
          <span className="dot" style={{ background: "linear-gradient(140deg,#8b5cf6,#2dd4bf)" }} />
          <b>Todos</b>
          <span>· {students.length}</span>
        </button>
        {groups.map((g, i) => (
          <button
            key={g.group_id}
            className={"topic-chip" + (groupId === g.group_id ? " on" : "")}
            style={{ "--c": AVAS_SOLID[i % AVAS_SOLID.length] } as React.CSSProperties}
            onClick={() => setGroupId(g.group_id)}
          >
            <span className="dot" />
            <b>{g.name}</b>
            <span>· {g.student_count} est.</span>
          </button>
        ))}
      </div>

      <div className="view-tabs">
        <button className={tab === "estudiantes" ? "on" : ""} onClick={() => setTab("estudiantes")}>
          👥 Estudiantes
        </button>
        <button className={tab === "ranking" ? "on" : ""} onClick={() => setTab("ranking")}>
          🏆 Ranking
        </button>
        <button className={tab === "metricas" ? "on" : ""} onClick={() => setTab("metricas")}>
          📊 Métricas
        </button>
      </div>

      {tab === "estudiantes" ? (
        <StudentsView students={filtered} onSelect={setSelected} />
      ) : tab === "ranking" ? (
        <RankingView students={filtered} />
      ) : (
        <MetricsView students={filtered} />
      )}

      {selected && <StudentDrawer student={selected} onClose={() => setSelected(null)} />}
    </>
  );
}
