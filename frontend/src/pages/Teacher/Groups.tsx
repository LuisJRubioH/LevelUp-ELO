/**
 * pages/Teacher/Groups.tsx — Grupos (rediseño)
 * ============================================
 * Portado de docs/redesign/source/teacher-groups.jsx, con datos reales:
 * teacherApi.groups() + dashboard() (roster/ELO por grupo) + allCourses()
 * + createGroup() + generateInviteCode(). Estilos en TeacherConsole.css.
 */

import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { RankPill } from "../../components/ELO/RankBadge";
import { teacherApi, type Group, type StudentSummary } from "../../api/teacher";

/* ── helpers ─────────────────────────────────────────────────────────────── */
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
const COLORS = ["#8b5cf6", "#2dd4bf", "#f59e0b", "#ec4899", "#10b981", "#f43f5e"];
const initials = (n: string) =>
  n.split(/[\s_.·]+/).filter(Boolean).slice(0, 2).map((w) => w[0] ?? "").join("").toUpperCase() ||
  n.slice(0, 2).toUpperCase();
const avaFor = (n: string) => AVAS[(n.charCodeAt(0) + n.length) % AVAS.length];
const accColor = (a: number) => (a >= 80 ? "#34d399" : a >= 65 ? "#fbbf24" : "#f87171");
const fmtMiles = (n: number) => Math.round(n).toLocaleString("es-CO");
const toPct = (a: number) => Math.round(a <= 1 ? a * 100 : a);
const GOAL = 75;

interface GroupStats {
  n: number;
  elo: number | null; // mean of rated members' display values; null if none
  acc: number;
  attn: number;
  attempts: number;
  members: StudentSummary[];
}
function statsFor(members: StudentSummary[]): GroupStats {
  const n = members.length;
  if (!n) return { n: 0, elo: null, acc: 0, attn: 0, attempts: 0, members: [] };
  return {
    n,
    elo: meanShown(members),
    acc: Math.round(members.reduce((s, x) => s + toPct(x.accuracy), 0) / n),
    attn: members.filter((x) => needsAttention(x, toPct(x.accuracy))).length,
    attempts: members.reduce((s, x) => s + x.total_attempts, 0),
    members: [...members].sort(byRatingDesc),
  };
}

/* ── code chip ───────────────────────────────────────────────────────────── */
function CodeChip({
  code,
  big,
  onGenerate,
  generating,
}: {
  code: string | null;
  big?: boolean;
  onGenerate: () => void;
  generating: boolean;
}) {
  const [done, setDone] = useState(false);
  if (!code) {
    return (
      <button
        className={"code-chip" + (big ? " big" : "")}
        onClick={(e) => {
          e.stopPropagation();
          onGenerate();
        }}
        disabled={generating}
        title="Generar código de invitación"
      >
        <span className="ic">🔑</span>
        <span className="cc">{generating ? "Generando…" : "Sin código"}</span>
        <span className="cp">Generar</span>
      </button>
    );
  }
  const copy = (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      navigator.clipboard.writeText(code);
    } catch {
      /* noop */
    }
    setDone(true);
    setTimeout(() => setDone(false), 1400);
  };
  return (
    <button className={"code-chip" + (big ? " big" : "")} onClick={copy} title="Copiar código de invitación">
      <span className="ic">🔑</span>
      <span className="cc">{code}</span>
      <span className="cp">{done ? "✓ Copiado" : "Copiar"}</span>
    </button>
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
          style={{ background: avaFor(s.username), zIndex: max - i }}
          title={s.username}
        >
          {initials(s.username)}
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
  members,
  onOpen,
  onGenerate,
  generating,
}: {
  g: Group;
  color: string;
  members: StudentSummary[];
  onOpen: () => void;
  onGenerate: () => void;
  generating: boolean;
}) {
  const st = statsFor(members);
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

      <CodeChip code={g.invite_code} onGenerate={onGenerate} generating={generating} />

      <div className="gc-stats">
        <div className="gcs">
          <b>{st.n}</b>
          <span>estudiantes</span>
        </div>
        <div className="gcs">
          <b>{st.elo ?? "—"}</b>
        </div>
        <div className="gcs">
          <b>{st.acc}%</b>
          <span>dominio</span>
        </div>
      </div>

      <div className="gc-mastery">
        <div className="gcm-bar">
          <i style={{ width: st.acc + "%", background: color }} />
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
  members,
  onClose,
  onGenerate,
  generating,
}: {
  g: Group;
  color: string;
  members: StudentSummary[];
  onClose: () => void;
  onGenerate: () => void;
  generating: boolean;
}) {
  const st = statsFor(members);
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
          <CodeChip code={g.invite_code} big onGenerate={onGenerate} generating={generating} />
        </div>

        <div className="gd-stats">
          <div className="gds">
            <span className="l">Estudiantes</span>
            <b>{st.n}</b>
          </div>
          <div className="gds">
            <span className="l">ELO promedio</span>
            <b>{st.elo ?? "—"}</b>
          </div>
          <div className="gds">
            <span className="l">Dominio</span>
            <b style={{ color: accColor(st.acc) }}>{st.acc}%</b>
          </div>
          <div className="gds">
            <span className="l">Intentos</span>
            <b>{fmtMiles(st.attempts)}</b>
          </div>
        </div>

        <div className="gd-section">
          <div className="gd-sechead">
            <h4>
              Roster <span>· {st.members.length}</span>
            </h4>
          </div>
          {st.members.length === 0 ? (
            <p style={{ color: "var(--mute)", fontSize: 13 }}>
              Aún no hay estudiantes. Comparte el código de invitación para que se unan.
            </p>
          ) : (
            <div className="gd-roster">
              {st.members.map((s, i) => {
                const acc = toPct(s.accuracy);
                return (
                  <div className="gdr-row" key={s.user_id}>
                    <span className="gdr-pos">{i + 1}</span>
                    <span className="av" style={{ background: avaFor(s.username) }}>
                      {initials(s.username)}
                    </span>
                    <div className="gdr-nm">
                      <b>{s.username}</b>
                      <span>@{s.username}</span>
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
              <span>Código</span>
              <b className="mono">{g.invite_code ?? "—"}</b>
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
          <button className="btn-pri" onClick={onGenerate} disabled={generating}>
            {generating ? "Generando…" : g.invite_code ? "Regenerar código" : "Generar código"}
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
        <p className="gm-sub">Genera un curso nuevo. Los estudiantes se unen con el código de invitación.</p>

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
          <span>Código de invitación</span>
          <b>se genera al crear</b>
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
  const [genId, setGenId] = useState<number | null>(null);

  const { data: groups = [], isLoading } = useQuery({
    queryKey: ["teacher-groups"],
    queryFn: () => teacherApi.groups(),
    staleTime: 30_000,
  });
  const { data: dash } = useQuery({
    queryKey: ["teacher-dashboard"],
    queryFn: () => teacherApi.dashboard(),
    staleTime: 60_000,
  });
  const { data: allCourses = [] } = useQuery({
    queryKey: ["teacher-all-courses"],
    queryFn: () => teacherApi.allCourses(),
    staleTime: 300_000,
  });

  const studentsByGroup = useMemo(() => {
    const map = new Map<number, StudentSummary[]>();
    for (const s of dash?.students ?? []) {
      if (s.group_id == null) continue;
      if (!map.has(s.group_id)) map.set(s.group_id, []);
      map.get(s.group_id)!.push(s);
    }
    return map;
  }, [dash]);

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

  const generateCode = async (group_id: number) => {
    setGenId(group_id);
    try {
      await teacherApi.generateInviteCode(group_id);
      qc.invalidateQueries({ queryKey: ["teacher-groups"] });
    } finally {
      setGenId(null);
    }
  };

  const colorFor = (i: number) => COLORS[i % COLORS.length];
  const filtered = groups.filter((g) =>
    (g.name + (g.course_id ?? "")).toLowerCase().includes(q.toLowerCase())
  );
  const totalStudents = groups.reduce((s, g) => s + g.student_count, 0);
  const totalAttn = groups.reduce(
    (s, g) => s + statsFor(studentsByGroup.get(g.group_id) ?? []).attn,
    0
  );
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

  return (
    <>
      <div className="tc-head">
        <div className="ttl">
          <h1>Grupos</h1>
          <p>
            Tus cursos activos en el motor ELO. Abre un grupo para ver su roster, código de invitación y
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
              members={studentsByGroup.get(g.group_id) ?? []}
              onOpen={() => setOpenId(g.group_id)}
              onGenerate={() => generateCode(g.group_id)}
              generating={genId === g.group_id}
            />
          );
        })}
        {q === "" && (
          <button className="grp-card add" onClick={() => setCreating(true)}>
            <span className="ag-plus">＋</span>
            <b>Crear grupo</b>
            <span>Nuevo curso con su propio código de invitación</span>
          </button>
        )}
      </div>

      {openGroup && (
        <GroupDrawer
          g={openGroup}
          color={colorFor(openIndex)}
          members={studentsByGroup.get(openGroup.group_id) ?? []}
          onClose={() => setOpenId(null)}
          onGenerate={() => generateCode(openGroup.group_id)}
          generating={genId === openGroup.group_id}
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
