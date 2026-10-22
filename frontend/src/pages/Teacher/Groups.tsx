/**
 * pages/Teacher/Groups.tsx — Grupos (rediseño)
 * ============================================
 * Portado de docs/redesign/source/teacher-groups.jsx, con datos reales:
 * teacherApi.groups() + dashboard() (roster/ELO por grupo) + allCourses()
 * + createGroup() + the group's single-use invitations (spec 001, delivery INV:
 * invitations() / createInvitations() / revokeInvitation()). Estilos en TeacherConsole.css.
 */

import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { Link } from "react-router-dom";
import { RankPill } from "../../components/ELO/RankBadge";
import {
  teacherApi,
  type ConsoleFigures,
  type Group,
  type Invitation,
  type StudentSummary,
} from "../../api/teacher";

/* ── helpers ─────────────────────────────────────────────────────────────── */
/** Spec 001: ratings and labels come from the API (display_rating, rank_label) as given. */
const fmtRating = (v: number | null | undefined) => (v == null ? "Diagnóstico pendiente" : String(v));
const AVAS = [
  "linear-gradient(140deg,#8b5cf6,#6366f1)",
  "linear-gradient(140deg,#2dd4bf,#0ea5e9)",
  "linear-gradient(140deg,#f59e0b,#ef4444)",
  "linear-gradient(140deg,#ec4899,#8b5cf6)",
  "linear-gradient(140deg,#10b981,#22d3ee)",
  "linear-gradient(140deg,#f43f5e,#f59e0b)",
];
const COLORS = ["#8b5cf6", "#2dd4bf", "#f59e0b", "#ec4899", "#10b981", "#f43f5e"];
const initials = (n: string) =>
  n.split(/[\s_.·]+/).filter(Boolean).slice(0, 2).map((w) => w[0] ?? "").join("").toUpperCase() ||
  n.slice(0, 2).toUpperCase();
const avaFor = (n: string) => AVAS[(n.charCodeAt(0) + n.length) % AVAS.length];
const accColor = (a: number) => (a >= 80 ? "#34d399" : a >= 65 ? "#fbbf24" : "#f87171");
const fmtMiles = (n: number) => Math.round(n).toLocaleString("es-CO");
const toPct = (a: number) => Math.round(a <= 1 ? a * 100 : a);
const fmtPct = (a: number | null) => (a == null ? "—" : a + "%");
const GOAL = 75;

interface GroupStats {
  n: number;
  elo: number | null; // the server's mean of rated members' display values; null if none
  acc: number | null; // percent over members with attempts; null if none
  attn: number;
  attempts: number;
  members: (StudentSummary & { rank: number | null })[]; // the server's ranking, in its order
  basis: ConsoleFigures["basis"]; // what the group is ranked on (FR-041a)
}
const NO_FIGURES: ConsoleFigures = {
  n: 0,
  mean: null,
  accuracy: null,
  attempts: 0,
  attention: [],
  ranking: [],
  histogram: [],
  basis: { kind: "linked_courses" },
};
/** Spec 006 FR-041c: the screen names what the group's ratings are. */
const basisShort = (b: ConsoleFigures["basis"]) =>
  b.kind === "course" ? `ELO · ${b.course_name}` : "ELO · sus cursos contigo";
/** Spec 006 FR-041: the group's figures as the server computed them; nothing worked out here. */
function statsFor(figures: ConsoleFigures, students: Map<number, StudentSummary>): GroupStats {
  return {
    n: figures.n,
    elo: figures.mean,
    acc: figures.accuracy,
    attn: figures.attention.length,
    attempts: figures.attempts,
    // FR-041c: each member with the rating the group was ranked on.
    members: figures.ranking.flatMap((r) => {
      const s = students.get(r.user_id);
      return s
        ? [{ ...s, rank: r.rank, display_rating: r.display_rating, rank_label: r.rank_label }]
        : [];
    }),
    basis: figures.basis,
  };
}

/* ── invitations (spec 001, delivery INV) ────────────────────────────────── */
const MAX_INVITATIONS = 50;
/** "YYYY-MM-DD HH:MM:SS" → "dd/mm/aaaa", read from the text (no time-zone shift). */
const fmtDay = (stamp: string) => {
  const [y, m, d] = stamp.slice(0, 10).split("-");
  return `${d}/${m}/${y}`;
};
/** FR-028t: what each state says; a used one names the student by their public name. */
const invitationState = (i: Invitation) =>
  i.status === "unused"
    ? `Sin usar · vence ${fmtDay(i.expires_at)}`
    : i.status === "used"
      ? `Usada por ${i.used_by_name ?? "un estudiante"}`
      : i.status === "expired"
        ? "Vencida"
        : "Anulada";

/** The card's hint: invitations live in the group's drawer. */
function InvitationsChip() {
  return (
    <span className="code-chip" title="Invitaciones de un solo uso">
      <span className="ic">🔑</span>
      <span className="cl">Invitaciones de un solo uso</span>
      <span className="cp">Gestionar</span>
    </span>
  );
}

function InvitationsPanel({ groupId }: { groupId: number }) {
  const qc = useQueryClient();
  const queryKey = ["teacher-invitations", groupId];
  const { data, isLoading, isError } = useQuery({
    queryKey,
    queryFn: () => teacherApi.invitations(groupId),
  });
  const [count, setCount] = useState(1);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState<number | null>(null);

  const refresh = () => qc.invalidateQueries({ queryKey });
  const create = useMutation({
    mutationFn: (n: number) => teacherApi.createInvitations(groupId, n),
    onSuccess: () => {
      setError("");
      refresh();
    },
    onError: (err: Error) => setError(err.message || "No se pudieron generar las invitaciones."),
  });
  const revoke = useMutation({
    mutationFn: (id: number) => teacherApi.revokeInvitation(id),
    onSuccess: () => {
      setError("");
      refresh();
    },
    onError: (err: Error) => {
      setError(err.message || "No se pudo anular la invitación.");
      refresh();
    },
  });

  const copy = async (i: Invitation) => {
    try {
      await navigator.clipboard.writeText(i.token);
      setCopied(i.id);
      setTimeout(() => setCopied((c) => (c === i.id ? null : c)), 1400);
    } catch {
      setError("No se pudo copiar. Selecciona el código y cópialo a mano.");
    }
  };

  const invitations = data?.invitations ?? [];
  const unused = invitations.filter((i) => i.status === "unused").length;
  const countOk = Number.isInteger(count) && count >= 1 && count <= MAX_INVITATIONS;

  return (
    <section className="gd-section gd-inv" aria-label="Invitaciones">
      <div className="gd-sechead">
        <h4>
          Invitaciones <span>· {unused} sin usar</span>
        </h4>
      </div>
      {data && (
        <p className="inv-hint">
          Cada código sirve para un solo estudiante y vence a los {data.ttl_days} días si nadie lo
          usa.
        </p>
      )}
      <div className="inv-make">
        <input
          type="number"
          min={1}
          max={MAX_INVITATIONS}
          value={Number.isNaN(count) ? "" : count}
          onChange={(e) => setCount(e.target.valueAsNumber)}
          aria-label="Cantidad de invitaciones"
        />
        <span className="inv-unit">{count === 1 ? "código" : "códigos"}</span>
        <button
          className="btn-pri"
          onClick={() => create.mutate(count)}
          disabled={!countOk || create.isPending}
        >
          {create.isPending ? "Generando…" : "Generar invitaciones"}
        </button>
      </div>
      {error && (
        <p className="inv-err" role="alert">
          {error}
        </p>
      )}
      {isLoading ? (
        <p className="inv-empty">Cargando invitaciones…</p>
      ) : isError ? (
        <p className="inv-err" role="alert">
          No pudimos cargar las invitaciones. Cierra el grupo y vuelve a abrirlo.
        </p>
      ) : invitations.length === 0 ? (
        <p className="inv-empty">Aún no hay invitaciones para este grupo.</p>
      ) : (
        <ul className="inv-list">
          <AnimatePresence initial={false}>
            {invitations.map((i) => (
              <motion.li
                key={i.id}
                layout
                className={"inv-row s-" + i.status}
                initial={{ opacity: 0, y: -10, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ type: "spring", stiffness: 420, damping: 32 }}
              >
                <b className="inv-token">{i.token}</b>
                <span className="inv-state">{invitationState(i)}</span>
                {i.status === "unused" && (
                  <span className="inv-actions">
                    <button className="inv-btn" onClick={() => copy(i)}>
                      {copied === i.id ? "✓ Copiado" : "Copiar"}
                    </button>
                    <button
                      className="inv-btn danger"
                      onClick={() => revoke.mutate(i.id)}
                      disabled={revoke.isPending}
                    >
                      Anular
                    </button>
                  </span>
                )}
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
      )}
    </section>
  );
}

function AvaStack({ members, max = 5 }: { members: StudentSummary[]; max?: number }) {
  const shown = members.slice(0, max);
  const rest = members.length - shown.length;
  return (
    <div className="ava-stack">
      {shown.map((s, i) => (
        <span
          key={s.user_id}
          className="as-ava"
          style={{ background: avaFor(s.name), zIndex: max - i }}
          title={s.name}
        >
          {initials(s.name)}
        </span>
      ))}
      {rest > 0 ? <span className="as-more">+{rest}</span> : null}
    </div>
  );
}

/* ── group card ──────────────────────────────────────────────────────────── */
function GroupCard({
  g,
  color,
  st,
  onOpen,
}: {
  g: Group;
  color: string;
  st: GroupStats;
  onOpen: () => void;
}) {
  return (
    <div className="grp-card" style={{ "--c": color } as React.CSSProperties} onClick={onOpen}>
      <div className="gc-top">
        <span className="gc-ic" style={{ background: color }}>
          {initials(g.name)}
        </span>
        <div className="gc-id">
          <h3>{g.name}</h3>
          <span className="gc-meta">{g.course_id ?? "Sin curso"}</span>
        </div>
        {st.attn > 0 ? (
          <span className="gc-attn" title={st.attn + " necesitan atención"}>
            ⚠ {st.attn}
          </span>
        ) : null}
      </div>

      <InvitationsChip />

      <div className="gc-stats">
        <div className="gcs">
          <b>{st.n}</b>
          <span>estudiantes</span>
        </div>
        <div className="gcs">
          <b>{st.elo ?? "—"}</b>
          <span>{basisShort(st.basis)}</span>
        </div>
        <div className="gcs">
          <b>{fmtPct(st.acc)}</b>
          <span>dominio</span>
        </div>
      </div>

      <div className="gc-mastery">
        <div className="gcm-bar">
          <i style={{ width: (st.acc ?? 0) + "%", background: color }} />
          <span className="goal" style={{ left: GOAL + "%" }} title={"Objetivo " + GOAL + "%"} />
        </div>
        <div className="gcm-lbl">
          <span>Dominio del grupo</span>
          <span>objetivo {GOAL}%</span>
        </div>
      </div>

      <div className="gc-foot">
        <AvaStack members={st.members} />
        <span className="gc-open">
          Abrir grupo <span className="ar">›</span>
        </span>
      </div>
    </div>
  );
}

/* ── detail drawer ───────────────────────────────────────────────────────── */
function GroupDrawer({
  g,
  color,
  st,
  onClose,
}: {
  g: Group;
  color: string;
  st: GroupStats;
  onClose: () => void;
}) {
  return (
    <div className="grp-backdrop" onClick={onClose}>
      <aside
        className="grp-drawer"
        style={{ "--c": color } as React.CSSProperties}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-label={`Grupo ${g.name}`}
      >
        <div className="gd-head">
          <div className="gd-htop">
            <span className="gd-ic" style={{ background: color }}>
              {initials(g.name)}
            </span>
            <button className="gd-x" onClick={onClose} aria-label="Cerrar">
              ✕
            </button>
          </div>
          <h2>{g.name}</h2>
          <p className="gd-sub">{g.course_id ?? "Sin curso"}</p>
          {g.course_id && (
            // Spec 003 L1: the path the group's students walk, read only.
            <Link className="gd-path-link" to={`/student/course/${encodeURIComponent(g.course_id)}/map`}>
              Ver ruta de aprendizaje
            </Link>
          )}
        </div>

        <div className="gd-stats">
          <div className="gds">
            <span className="l">Estudiantes</span>
            <b>{st.n}</b>
          </div>
          <div className="gds">
            <span className="l">{basisShort(st.basis)} · promedio</span>
            <b>{st.elo ?? "—"}</b>
          </div>
          <div className="gds">
            <span className="l">Dominio</span>
            <b style={{ color: st.acc == null ? undefined : accColor(st.acc) }}>{fmtPct(st.acc)}</b>
          </div>
          <div className="gds">
            <span className="l">Intentos</span>
            <b>{fmtMiles(st.attempts)}</b>
          </div>
        </div>

        <InvitationsPanel groupId={g.group_id} />

        <div className="gd-section">
          <div className="gd-sechead">
            <h4>
              Roster <span>· {st.members.length}</span>
            </h4>
          </div>
          {st.members.length === 0 ? (
            <p style={{ color: "var(--mute)", fontSize: 13 }}>
              Aún no hay estudiantes. Genera invitaciones y comparte una con cada estudiante.
            </p>
          ) : (
            <div className="gd-roster">
              {st.members.map((s) => {
                const acc = toPct(s.accuracy);
                return (
                  <div className="gdr-row" key={s.user_id}>
                    <span className="gdr-pos">{s.rank ?? "—"}</span>
                    <span className="av" style={{ background: avaFor(s.name) }}>
                      {initials(s.name)}
                    </span>
                    <div className="gdr-nm">
                      <b>{s.name}</b>
                      <span>{s.total_attempts} intentos</span>
                    </div>
                    <RankPill label={s.rank_label} />
                    <span className="gdr-acc" style={{ color: accColor(acc) }}>
                      {acc}%
                    </span>
                    <span className="gdr-elo">{fmtRating(s.display_rating)}</span>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="gd-section">
          <h4>Configuración</h4>
          <div className="gd-config">
            <div className="gcf">
              <span>Curso</span>
              <b>
                <span className="gd-dot" style={{ background: color }} />
                {g.course_id ?? "—"}
              </b>
            </div>
            <div className="gcf">
              <span>Objetivo de dominio</span>
              <b>{GOAL}%</b>
            </div>
            <div className="gcf">
              <span>ID del grupo</span>
              <b className="mono">#{g.group_id}</b>
            </div>
          </div>
        </div>

        <div className="gd-footer">
          <button className="btn-soft" onClick={onClose}>
            Cerrar
          </button>
        </div>
      </aside>
    </div>
  );
}

/* ── create modal ────────────────────────────────────────────────────────── */
function CreateGroupModal({
  courses,
  onClose,
  onCreate,
  creating,
  error,
}: {
  courses: { id: string; name: string; block: string }[];
  onClose: () => void;
  onCreate: (course_id: string, name: string) => void;
  creating: boolean;
  error: string;
}) {
  const [name, setName] = useState("");
  const [courseId, setCourseId] = useState("");

  const grouped = useMemo(() => {
    const blockRank = (block: string): number => {
      const base: Record<string, number> = { Colegio: 0, Universidad: 1, Concursos: 2, Semillero: 3 };
      if (block in base) return base[block];
      const m = block.match(/Semillero\s*(\d+)/);
      if (m) return 100 + parseInt(m[1], 10);
      return 999;
    };
    const byBlock = new Map<string, typeof courses>();
    for (const c of courses) {
      const k = c.block || "Otros";
      if (!byBlock.has(k)) byBlock.set(k, []);
      byBlock.get(k)!.push(c);
    }
    return [...byBlock.keys()]
      .sort((a, b) => blockRank(a) - blockRank(b) || a.localeCompare(b))
      .map((block) => ({
        block,
        items: byBlock.get(block)!.slice().sort((a, b) => a.name.localeCompare(b.name)),
      }));
  }, [courses]);

  return (
    <div className="grp-backdrop center" onClick={onClose}>
      <div className="grp-modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="Crear grupo">
        <div className="gm-head">
          <h3>Crear grupo</h3>
          <button className="gd-x" onClick={onClose} aria-label="Cerrar">
            ✕
          </button>
        </div>
        <p className="gm-sub">Genera un curso nuevo. Los estudiantes se unen con invitaciones de un solo uso.</p>

        <label className="gm-field">
          <span>Nombre del grupo</span>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Ej. Álgebra · 10°B" maxLength={80} />
        </label>

        <label className="gm-field">
          <span>Curso</span>
          <select value={courseId} onChange={(e) => setCourseId(e.target.value)}>
            <option value="">Selecciona un curso…</option>
            {grouped.map((grp) => (
              <optgroup key={grp.block} label={grp.block}>
                {grp.items.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </label>

        <div className="gm-codebox">
          <span>Invitaciones</span>
          <b>las generas al abrir el grupo</b>
        </div>

        {error && <p className="gm-err">{error}</p>}

        <div className="gm-foot">
          <button className="btn-soft" onClick={onClose}>
            Cancelar
          </button>
          <button
            className="btn-pri"
            onClick={() => onCreate(courseId, name.trim())}
            disabled={creating || !courseId || !name.trim()}
          >
            {creating ? "Creando…" : "Crear grupo"}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── root ────────────────────────────────────────────────────────────────── */
export function TeacherGroups() {
  const qc = useQueryClient();
  const [openId, setOpenId] = useState<number | null>(null);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState("");
  const [q, setQ] = useState("");

  const { data: groups = [], isLoading, isError } = useQuery({
    queryKey: ["teacher-groups"],
    queryFn: () => teacherApi.groups(),
    staleTime: 30_000,
  });
  const { data: dash } = useQuery({
    queryKey: ["teacher-dashboard", "30"],
    queryFn: () => teacherApi.dashboard("30"),
    staleTime: 60_000,
  });
  const { data: allCourses = [] } = useQuery({
    queryKey: ["teacher-all-courses"],
    queryFn: () => teacherApi.allCourses(),
    staleTime: 300_000,
  });

  const byId = useMemo(
    () => new Map((dash?.students ?? []).map((s) => [s.user_id, s] as const)),
    [dash]
  );
  const statsOf = (g: Group) => statsFor(dash?.summary?.groups?.[String(g.group_id)] ?? NO_FIGURES, byId);

  const createMutation = useMutation({
    mutationFn: ({ course_id, name }: { course_id: string; name: string }) =>
      teacherApi.createGroup(course_id, name),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teacher-groups"] });
      qc.invalidateQueries({ queryKey: ["teacher-dashboard"] });
      setCreating(false);
      setCreateError("");
    },
    onError: (err: Error) => setCreateError(err.message),
  });

  const colorFor = (i: number) => COLORS[i % COLORS.length];
  const filtered = groups.filter((g) =>
    (g.name + (g.course_id ?? "")).toLowerCase().includes(q.toLowerCase())
  );
  const totalStudents = groups.reduce((s, g) => s + g.student_count, 0);
  const totalAttn = dash?.summary?.attention.length ?? 0; // a student in two groups counts once
  const openGroup = groups.find((g) => g.group_id === openId) ?? null;
  const openIndex = groups.findIndex((g) => g.group_id === openId);

  if (isLoading) {
    return (
      <div className="tc-soon">
        <div className="box">
          <div className="em-ic">⏳</div>
          <h2>Cargando grupos…</h2>
        </div>
      </div>
    );
  }
  // A failed load is not «0 grupos».
  if (isError) {
    return (
      <div className="tc-soon">
        <div className="box" role="alert">
          <div className="em-ic">⚠️</div>
          <h2>No pudimos cargar tus grupos</h2>
          <p>Revisa tu conexión e inténtalo de nuevo.</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="tc-head">
        <div className="ttl">
          <h1>Grupos</h1>
          <p>
            Tus cursos activos en el motor ELO. Abre un grupo para ver su roster, sus invitaciones y su
            configuración.
          </p>
        </div>
        <div className="head-side">
          <div className="search">
            <span className="ic">🔍</span>
            <input placeholder="Buscar grupo…" value={q} onChange={(e) => setQ(e.target.value)} />
          </div>
          <button
            className="btn-pri"
            onClick={() => {
              setCreating(true);
              setCreateError("");
            }}
          >
            ＋ Crear grupo
          </button>
        </div>
      </div>

      <div className="grp-summary">
        <span>
          <b>{groups.length}</b> grupos
        </span>
        <span className="sep" />
        <span>
          <b>{totalStudents}</b> estudiantes en total
        </span>
        <span className="sep" />
        <span className={totalAttn ? "warn" : ""}>
          <b>{totalAttn}</b> necesitan atención
        </span>
      </div>

      <div className="grp-grid">
        {filtered.map((g) => {
          const idx = groups.findIndex((x) => x.group_id === g.group_id);
          return (
            <GroupCard
              key={g.group_id}
              g={g}
              color={colorFor(idx)}
              st={statsOf(g)}
              onOpen={() => setOpenId(g.group_id)}
            />
          );
        })}
        {q === "" && (
          <button className="grp-card add" onClick={() => setCreating(true)}>
            <span className="ag-plus">＋</span>
            <b>Crear grupo</b>
            <span>Nuevo curso; cada estudiante entra con su propia invitación</span>
          </button>
        )}
      </div>

      {openGroup && (
        <GroupDrawer
          g={openGroup}
          color={colorFor(openIndex)}
          st={statsOf(openGroup)}
          onClose={() => setOpenId(null)}
        />
      )}

      {creating && (
        <CreateGroupModal
          courses={allCourses}
          onClose={() => setCreating(false)}
          onCreate={(course_id, name) => createMutation.mutate({ course_id, name })}
          creating={createMutation.isPending}
          error={createError}
        />
      )}
    </>
  );
}
