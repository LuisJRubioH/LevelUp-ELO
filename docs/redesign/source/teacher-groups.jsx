/* Oulad teacher console — Window 2: Grupos (group management) */
const { useState: useStateG, useMemo: useMemoG, useEffect: useEffectG } = React;

/* ---- group metadata (each maps to a topic/course) ---- */
const GROUPS_SEED = [
  { id: "g-alg", topic: "algebra",       name: "Álgebra · 10°B",       code: "OUL-ALG-7X2", grade: "Grado 10", schedule: "Lun · Mié · Vie", created: "12 feb 2026", goal: 75 },
  { id: "g-geo", topic: "geometria",     name: "Geometría · 9°C",      code: "OUL-GEO-4K9", grade: "Grado 9",  schedule: "Mar · Jue",       created: "12 feb 2026", goal: 72 },
  { id: "g-ari", topic: "aritmetica",    name: "Aritmética · 8°A",     code: "OUL-ARI-2M5", grade: "Grado 8",  schedule: "Lun · Mié",       created: "03 mar 2026", goal: 70 },
  { id: "g-tri", topic: "trigonometria", name: "Trigonometría · 11°A", code: "OUL-TRI-9P3", grade: "Grado 11", schedule: "Mié · Vie",       created: "03 mar 2026", goal: 78 },
];

const groupMembers = (g) => STUDENTS.filter(s => s.topic === g.topic);
const groupStats = (g) => {
  const m = groupMembers(g);
  const n = m.length;
  if (!n) return { n: 0, elo: 0, acc: 0, attn: 0, attempts: 0, top: null };
  return {
    n,
    elo: Math.round(m.reduce((s, x) => s + x.elo, 0) / n),
    acc: Math.round(m.reduce((s, x) => s + x.acc, 0) / n),
    attn: m.filter(x => x.attn).length,
    attempts: m.reduce((s, x) => s + x.attempts, 0),
    top: [...m].sort((a, b) => b.elo - a.elo)[0],
  };
};

/* ---- invite code chip with copy ---- */
function CodeChip({ code, big }) {
  const [done, setDone] = useStateG(false);
  const copy = (e) => {
    e.stopPropagation();
    try { navigator.clipboard.writeText(code); } catch (_) {}
    setDone(true); setTimeout(() => setDone(false), 1400);
  };
  return (
    <button className={"code-chip" + (big ? " big" : "")} onClick={copy} title="Copiar código de invitación">
      <span className="ic">🔑</span>
      <span className="cc">{code}</span>
      <span className="cp">{done ? "✓ Copiado" : "Copiar"}</span>
    </button>
  );
}

/* ---- avatar stack ---- */
function AvaStack({ members, max = 5 }) {
  const shown = members.slice(0, max);
  const rest = members.length - shown.length;
  return (
    <div className="ava-stack">
      {shown.map((s, i) => (
        <span key={s.user} className="as-ava" style={{ background: avaFor(s.name), zIndex: max - i }} title={s.name}>{initials(s.name)}</span>
      ))}
      {rest > 0 ? <span className="as-more">+{rest}</span> : null}
    </div>
  );
}

/* ---- group card ---- */
function GroupCard({ g, onOpen }) {
  const t = topicById(g.topic);
  const st = groupStats(g);
  const rk = rankFor(st.elo);
  const members = groupMembers(g);
  return (
    <div className="grp-card" style={{ "--c": t.color }} onClick={() => onOpen(g)}>
      <div className="gc-top">
        <span className="gc-ic" style={{ background: t.color }}>{g.name.split(" ").slice(-1)[0]}</span>
        <div className="gc-id">
          <h3>{g.name}</h3>
          <span className="gc-meta">{g.grade} · {g.schedule}</span>
        </div>
        {st.attn > 0 ? <span className="gc-attn" title={st.attn + " necesitan atención"}>⚠ {st.attn}</span> : null}
      </div>

      <CodeChip code={g.code} />

      <div className="gc-stats">
        <div className="gcs"><b>{st.n}</b><span>estudiantes</span></div>
        <div className="gcs">
          <b>{fmtMiles(st.elo)}</b>
          <span className="rank-badge" style={{ color: rk.fg, background: rk.bg }}>{rk.name}</span>
        </div>
        <div className="gcs"><b>{st.acc}%</b><span>dominio</span></div>
      </div>

      <div className="gc-mastery">
        <div className="gcm-bar">
          <i style={{ width: st.acc + "%", background: t.color }}></i>
          <span className="goal" style={{ left: g.goal + "%" }} title={"Objetivo " + g.goal + "%"}></span>
        </div>
        <div className="gcm-lbl"><span>Dominio del grupo</span><span>objetivo {g.goal}%</span></div>
      </div>

      <div className="gc-foot">
        <AvaStack members={members} />
        <span className="gc-open">Abrir grupo <span className="ar">›</span></span>
      </div>
    </div>
  );
}

/* ---- create-group card (add new) ---- */
function AddGroupCard({ onClick }) {
  return (
    <button className="grp-card add" onClick={onClick}>
      <span className="ag-plus">＋</span>
      <b>Crear grupo</b>
      <span>Nuevo curso con su propio código de invitación</span>
    </button>
  );
}

/* ---- detail drawer ---- */
function GroupDrawer({ g, onClose }) {
  const [closing, setClosing] = useStateG(false);
  const close = () => { setClosing(true); setTimeout(onClose, 240); };
  useEffectG(() => {
    const k = (e) => e.key === "Escape" && close();
    window.addEventListener("keydown", k);
    return () => window.removeEventListener("keydown", k);
  }, []);
  if (!g) return null;
  const t = topicById(g.topic);
  const st = groupStats(g);
  const members = [...groupMembers(g)].sort((a, b) => b.elo - a.elo);

  return (
    <div className={"grp-backdrop" + (closing ? " out" : "")} onClick={close}>
      <aside className={"grp-drawer" + (closing ? " out" : "")} style={{ "--c": t.color }} onClick={e => e.stopPropagation()}>
        <div className="gd-head">
          <div className="gd-htop">
            <span className="gd-ic" style={{ background: t.color }}>{g.name.split(" ").slice(-1)[0]}</span>
            <button className="gd-x" onClick={close}>✕</button>
          </div>
          <h2>{g.name}</h2>
          <p className="gd-sub">{t.name} · {g.grade} · creado el {g.created}</p>
          <CodeChip code={g.code} big />
        </div>

        <div className="gd-stats">
          <div className="gds"><span className="l">Estudiantes</span><b>{st.n}</b></div>
          <div className="gds"><span className="l">ELO promedio</span><b>{fmtMiles(st.elo)}</b></div>
          <div className="gds"><span className="l">Dominio</span><b style={{ color: accColor(st.acc) }}>{st.acc}%</b></div>
          <div className="gds"><span className="l">Intentos</span><b>{fmtMiles(st.attempts)}</b></div>
        </div>

        <div className="gd-section">
          <div className="gd-sechead"><h4>Roster <span>· {members.length}</span></h4><button className="gd-mini">＋ Invitar</button></div>
          <div className="gd-roster">
            {members.map((s, i) => {
              const rk = rankFor(s.elo);
              return (
                <div className="gdr-row" key={s.user}>
                  <span className="gdr-pos">{i + 1}</span>
                  <span className="av" style={{ background: avaFor(s.name) }}>{initials(s.name)}</span>
                  <div className="gdr-nm">
                    <b>{s.name}</b>
                    <span>@{s.user}{s.attn ? <span className="gdr-flag"> · ⚠ atención</span> : null}</span>
                  </div>
                  <span className="rank-badge" style={{ color: rk.fg, background: rk.bg }}>{rk.name}</span>
                  <span className="gdr-acc" style={{ color: accColor(s.acc) }}>{s.acc}%</span>
                  <span className="gdr-elo">{fmtMiles(s.elo)}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="gd-section">
          <h4>Configuración</h4>
          <div className="gd-config">
            <div className="gcf"><span>Curso</span><b><span className="gd-dot" style={{ background: t.color }}></span>{t.name}</b></div>
            <div className="gcf"><span>Horario</span><b>{g.schedule}</b></div>
            <div className="gcf"><span>Objetivo de dominio</span><b>{g.goal}%</b></div>
            <div className="gcf"><span>Slug del curso</span><b className="mono">{t.slug}</b></div>
          </div>
        </div>

        <div className="gd-footer">
          <button className="btn-soft">Editar grupo</button>
          <button className="btn-pri">Asignar práctica →</button>
        </div>
      </aside>
    </div>
  );
}

/* ---- create-group modal ---- */
function CreateGroupModal({ onClose, onCreate }) {
  const [name, setName] = useStateG("");
  const [topic, setTopic] = useStateG(TOPICS[0].id);
  const [grade, setGrade] = useStateG("");
  const t = topicById(topic);
  const code = "OUL-" + (t.name.slice(0, 3).toUpperCase()) + "-" + Math.random().toString(36).slice(2, 5).toUpperCase();
  const submit = () => {
    onCreate({
      id: "g-" + Date.now(), topic, code,
      name: name.trim() || (t.name + (grade ? " · " + grade : "")),
      grade: grade.trim() || "—", schedule: "Por definir", created: "hoy", goal: 75,
    });
    onClose();
  };
  return (
    <div className="grp-backdrop center" onClick={onClose}>
      <div className="grp-modal" onClick={e => e.stopPropagation()}>
        <div className="gm-head"><h3>Crear grupo</h3><button className="gd-x" onClick={onClose}>✕</button></div>
        <p className="gm-sub">Genera un curso nuevo. Los estudiantes se unen con el código de invitación.</p>

        <label className="gm-field">
          <span>Nombre del grupo</span>
          <input value={name} onChange={e => setName(e.target.value)} placeholder="Ej. Álgebra · 10°B" />
        </label>

        <label className="gm-field">
          <span>Curso</span>
          <div className="gm-topics">
            {TOPICS.map(tp => (
              <button key={tp.id} type="button" className={"gm-topic" + (topic === tp.id ? " on" : "")} style={{ "--c": tp.color }} onClick={() => setTopic(tp.id)}>
                <span className="d" style={{ background: tp.color }}></span>{tp.name}
              </button>
            ))}
          </div>
        </label>

        <label className="gm-field">
          <span>Grado / sección</span>
          <input value={grade} onChange={e => setGrade(e.target.value)} placeholder="Ej. Grado 10" />
        </label>

        <div className="gm-codebox">
          <span>Código de invitación</span>
          <b className="mono">{code}</b>
        </div>

        <div className="gm-foot">
          <button className="btn-soft" onClick={onClose}>Cancelar</button>
          <button className="btn-pri" onClick={submit}>Crear grupo</button>
        </div>
      </div>
    </div>
  );
}

/* ---- root ---- */
function GroupsView() {
  const [groups, setGroups] = useStateG(GROUPS_SEED);
  const [open, setOpen] = useStateG(null);
  const [creating, setCreating] = useStateG(false);
  const [q, setQ] = useStateG("");

  const filtered = useMemoG(
    () => groups.filter(g => (g.name + topicById(g.topic).name).toLowerCase().includes(q.toLowerCase())),
    [groups, q]
  );
  const totalStudents = useMemoG(() => groups.reduce((s, g) => s + groupMembers(g).length, 0), [groups]);
  const totalAttn = useMemoG(() => groups.reduce((s, g) => s + groupStats(g).attn, 0), [groups]);

  return (
    <React.Fragment>
      <div className="tc-head">
        <div className="ttl">
          <h1>Grupos</h1>
          <p>Tus cursos activos en el motor ELO. Abre un grupo para ver su roster, código de invitación y configuración.</p>
        </div>
        <div className="head-side">
          <div className="search">
            <span className="ic">🔍</span>
            <input placeholder="Buscar grupo…" value={q} onChange={e => setQ(e.target.value)} />
          </div>
          <button className="btn-pri" onClick={() => setCreating(true)}>＋ Crear grupo</button>
        </div>
      </div>

      <div className="grp-summary">
        <span><b>{groups.length}</b> grupos</span>
        <span className="sep"></span>
        <span><b>{totalStudents}</b> estudiantes en total</span>
        <span className="sep"></span>
        <span className={totalAttn ? "warn" : ""}><b>{totalAttn}</b> necesitan atención</span>
      </div>

      <div className="grp-grid">
        {filtered.map(g => <GroupCard key={g.id} g={g} onOpen={setOpen} />)}
        {q === "" ? <AddGroupCard onClick={() => setCreating(true)} /> : null}
      </div>

      {open ? <GroupDrawer g={open} onClose={() => setOpen(null)} /> : null}
      {creating ? <CreateGroupModal onClose={() => setCreating(false)} onCreate={(g) => setGroups(gs => [...gs, g])} /> : null}
    </React.Fragment>
  );
}

Object.assign(window, { GROUPS_SEED, groupMembers, groupStats, CodeChip, AvaStack, GroupCard, AddGroupCard, GroupDrawer, CreateGroupModal, GroupsView });
