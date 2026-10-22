// ============================================================
//  LevelUpElo — Mapa de contenido · COMPONENTS
//  Icons (simple geometric SVG, brand-consistent) + the three
//  rendering layers and chrome. Art (trail/plants) and logic
//  (node states) are deliberately separate components.
// ============================================================

/* ---------------- icon set ---------------- */
const IcChevron = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" width="20" height="20"><path d="M15 5l-7 7 7 7"/></svg>
);
const IcFlame = () => (
  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M13 2c.5 3-1.5 4.5-2.8 6C8.6 10 8 11.4 8 13a4 4 0 0 0 1.4 3c-.2-.8-.1-1.7.6-2.5.8-1 .9-1.9.9-1.9.9.8 1.6 1.8 1.6 3.2 0 .6-.2 1.1-.5 1.6 1.7-.6 3-2.3 3-4.6 0-2.4-1.3-3.8-2.4-5.2C11.8 5.5 11.4 4 13 2z"/></svg>
);
const IcGem = () => (
  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 3h12l3 5-9 13L3 8l3-5zm.6 2L5 7.7h4L10 5H6.6zm7.4 0H10l-1 2.7h6L14 5zm3.4 0H14l1 2.7h4L17.4 5zM5.5 9.7l4.7 6.8-2-6.8h-2.7zM12 17.8l3.6-8.1H8.4L12 17.8zm2.8-2 4.7-6.8h-2.7l-2 6.8z"/></svg>
);
const IcCheck = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12.5l4.5 4.5L19 7"/></svg>
);
const IcLock = () => (
  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a5 5 0 0 0-5 5v3H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2h-1V7a5 5 0 0 0-5-5zm0 2a3 3 0 0 1 3 3v3H9V7a3 3 0 0 1 3-3zm0 10a1.8 1.8 0 0 1 1 3.3V19a1 1 0 0 1-2 0v-1.7A1.8 1.8 0 0 1 12 14z"/></svg>
);
const IcStar = () => (
  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.5l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5L12 17.8 6.2 20.9l1.1-6.5L2.6 9.3l6.5-.9L12 2.5z"/></svg>
);
const IcBook = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 5a2 2 0 0 1 2-2h6v16H6a2 2 0 0 0-2 2V5z"/><path d="M20 5a2 2 0 0 0-2-2h-6v16h6a2 2 0 0 1 2 2V5z"/></svg>
);
const IcMap = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 4 4 6v14l5-2 6 2 5-2V4l-5 2-6-2z"/><path d="M9 4v14M15 6v14"/></svg>
);
const IcTrophy = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M7 4h10v4a5 5 0 0 1-10 0V4z"/><path d="M7 5H4v2a3 3 0 0 0 3 3M17 5h3v2a3 3 0 0 1-3 3M9 15h6M10 19h4M12 13v2"/></svg>
);
const IcUser = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="8" r="3.6"/><path d="M5 20a7 7 0 0 1 14 0"/></svg>
);
const IcArrow = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" width="18" height="18"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
);
const IcInfo = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>
);

/* ---------------- decorative pixel flora ---------------- */
function Plant({ kind }) {
  if (kind === 'crystal') {
    return (
      <svg width="22" height="30" viewBox="0 0 22 30">
        <rect className="stem" x="10" y="20" width="2" height="9"/>
        <path className="gem" d="M11 4l5 7-5 9-5-9z"/>
        <path className="gem" d="M4 14l3 4-3 4-2-4z" opacity="0.7"/>
      </svg>
    );
  }
  if (kind === 'shroom') {
    return (
      <svg width="24" height="28" viewBox="0 0 24 28">
        <rect className="stem" x="9" y="14" width="6" height="12" rx="2"/>
        <path className="cap" d="M2 13a10 7 0 0 1 20 0z"/>
        <circle cx="8" cy="9" r="1.6" fill="rgba(255,255,255,.55)"/>
        <circle cx="15" cy="10.5" r="1.2" fill="rgba(255,255,255,.45)"/>
      </svg>
    );
  }
  // sprout (default)
  return (
    <svg width="24" height="30" viewBox="0 0 24 30">
      <rect className="stem" x="11" y="12" width="2" height="17"/>
      <path className="leaf" d="M12 18C6 18 3 14 2 9c6-1 9 3 10 9z"/>
      <path className="leaf-2" d="M12 14c6 0 9-4 10-9-6-1-9 3-10 9z"/>
    </svg>
  );
}

/* ---------------- Layer 1: trail ---------------- */
function TrailLayer({ segments, currentIndex, height }) {
  return (
    <svg className="map-illustration" width="402" height={height} viewBox={`0 0 402 ${height}`} preserveAspectRatio="xMidYMin meet" aria-hidden="true">
      {/* faint connecting ribbon under the stones */}
      {segments.map((s) => <path key={'r' + s.from} className="trail-ribbon" d={s.d} />)}
      {/* stepping stones, colored by progress */}
      {segments.map((s) => (
        <path key={'s' + s.from} d={s.d}
          className={'trail-stones ' + (s.to <= currentIndex ? 'traveled' : 'upcoming')} />
      ))}
    </svg>
  );
}

/* ---------------- App sidebar (desktop nav) ---------------- */
const NAVITEMS = [
  { id: 'mapa', label: 'Mapa', icon: <IcMap /> },
  { id: 'ligas', label: 'Ligas', icon: <IcTrophy /> },
  { id: 'perfil', label: 'Perfil', icon: <IcUser /> },
];
function Sidebar({ active, onNav, streak, gems, theme, onTheme }) {
  return (
    <aside className="lu-side">
      <div className="lu-brand">
        <img src="assets/logo.png" alt="LevelUp ELO" />
        <span className="lu-tag">Estudiante · Álgebra</span>
      </div>
      <nav className="lu-nav" aria-label="Navegación principal">
        <span className="lu-navsec">Aprender</span>
        {NAVITEMS.map((it) => (
          <button key={it.id} className={'lu-navitem' + (active === it.id ? ' on' : '')}
            aria-current={active === it.id ? 'page' : undefined} onClick={() => onNav(it.id)}>
            <span className="ic">{it.icon}</span>{it.label}
          </button>
        ))}
      </nav>
      <div className="lu-foot">
        <div className="lu-streakbar">
          <span className="lsb-item" aria-label={`Racha ${streak} días`}>
            <span className="i flame"><IcFlame /></span><b>{streak}</b><span className="k">Racha</span>
          </span>
          <span className="lsb-item" aria-label={`${gems} gemas`}>
            <span className="i gem"><IcGem /></span><b>{gems}</b><span className="k">Gemas</span>
          </span>
        </div>
        <div className="lu-user">
          <div className="ava">SR</div>
          <div className="meta"><b>santi_r</b><span><span className="role">Estudiante</span> · 2.º medio</span></div>
        </div>
        <div className="lu-toggles">
          <button className="lu-tog" onClick={onTheme}>{theme === 'light' ? '🌙 Oscuro' : '☀️ Claro'}</button>
          <button className="lu-tog">🌐 ES</button>
        </div>
      </div>
    </aside>
  );
}

/* ---------------- Course top bar (sticky) ---------------- */
function MapBar({ onBack, done, total }) {
  const pct = Math.round((done / total) * 100);
  return (
    <div className="lu-mapbar">
      <button className="icon-btn" onClick={onBack} aria-label="Volver a cursos"><IcChevron /></button>
      <div className="mb-title">
        <span className="mb-kicker">Mapa de contenido</span>
        <span className="mb-h">Álgebra</span>
      </div>
      <div className="mb-prog">
        <div className="mb-prog-top"><span>{done} de {total} nodos</span><b>{pct}%</b></div>
        <div className="mb-bar"><i style={{ width: pct + '%' }}></i></div>
      </div>
    </div>
  );
}

/* ---------------- Right rail (continue + path) ---------------- */
function RightRail({ currentNode, onContinue, units, unitProgress, retoLeft }) {
  return (
    <aside className="lu-rail" aria-label="Resumen del curso">
      <div className="rail-cont">
        <span className="rc-kicker">Continuar</span>
        <div className="rc-card">
          <div className="rc-ic"><IcBook /></div>
          <div className="rc-meta">
            <span className="rc-st">En curso · Unidad {currentNode.unit}</span>
            <span className="rc-name">{currentNode.name}</span>
          </div>
        </div>
        <button className="rail-btn" onClick={onContinue}>Empezar lección <IcArrow /></button>
      </div>

      <div className="rail-katia">
        <div className="katia-av small"><img src="assets/katia-correcto.gif" alt="KatIA" /><span className="scan"></span></div>
        <div className="rk-bubble">
          <span className="nm">KatIA</span>
          ¡Vas muy bien! Te {retoLeft === 1 ? 'queda' : 'quedan'} <b>{retoLeft} {retoLeft === 1 ? 'nodo' : 'nodos'}</b> para el Reto de Unidad.
        </div>
      </div>

      <div className="rail-units">
        <span className="ru-title">Tu camino</span>
        {units.map((u) => {
          const [done, tot] = unitProgress[u.id].split('/').map(Number);
          const pct = u.reserved ? 0 : Math.round((done / tot) * 100);
          return (
            <div key={u.id} className={'ru-item' + (u.reserved ? ' soon' : '')}>
              <span className={'ru-badge ' + u.tier}>{u.reserved ? '∞' : u.id}</span>
              <div className="ru-body">
                <span className="ru-name">{u.label} · {u.reserved ? 'Extensión' : u.name}</span>
                <div className="ru-bar"><i style={{ width: pct + '%' }}></i></div>
              </div>
              <span className="ru-prog">{u.reserved ? '—' : unitProgress[u.id]}</span>
            </div>
          );
        })}
      </div>
    </aside>
  );
}

/* ---------------- Unit banner ---------------- */
function UnitBanner({ unit, progress }) {
  const tier = unit.tier;
  const badge = unit.reserved ? '∞' : unit.id;
  return (
    <div className={'unit-banner ' + tier} style={{ top: unit.y }}>
      <div className="ub-badge">{badge}</div>
      <div className="ub-text">
        <span className="ub-kicker">{unit.label} · {unit.reserved ? 'Próximamente' : unit.name}</span>
        <span className="ub-name">{unit.reserved ? 'Extensión' : unit.name}</span>
      </div>
      <span className="ub-prog">{unit.reserved ? 'En camino' : progress}</span>
    </div>
  );
}

/* ---------------- Layer 3: a single node ---------------- */
const STATE_LABEL = { completed: 'completado', current: 'nivel actual', locked: 'bloqueado', reserved: 'próximamente' };

function NodeView({ node, state, onActivate, shaking }) {
  const isReto = node.type === 'challenge';
  const cls = ['node', state, isReto ? 'reto' : ''].join(' ').trim() + (shaking ? ' shake' : '');
  // label side: keep text off the trail
  const side = node.lane === 'R' ? 'lbl-left' : 'lbl-right';
  const anchorCls = ['node-anchor', side,
    state === 'current' ? 'is-current' : '', node.reserved ? 'is-reserved' : ''].join(' ').trim();

  let glyph = null;
  if (isReto) glyph = <span className="glyph"><IcStar /></span>;
  else if (state === 'completed') glyph = <span className="glyph"><IcCheck /></span>;
  else if (state === 'current') glyph = <span className="glyph"><IcBook /></span>;
  else if (state === 'reserved') glyph = <span className="glyph"><IcLock /></span>;
  else glyph = <span className="glyph"><IcLock /></span>;

  const retoLocked = isReto && (state === 'locked' || state === 'reserved');
  const aria = `${node.name}, ${isReto ? 'reto de unidad, ' : ''}${STATE_LABEL[state]}`;

  return (
    <div className={anchorCls} style={{ left: node.x, top: node.y }}>
      {state === 'current' && <span className="here-flag">¡Aquí!</span>}
      <button className={cls} aria-label={aria}
        onClick={() => onActivate(node, state)}>
        <span className="disc">{glyph}</span>
        {retoLocked && <span className="lock-badge"><IcLock /></span>}
      </button>
      {state !== 'current' && (
        <span className="node-label">
          <span className="nl-idx">{node.reserved ? 'EXT' : String(node.index).padStart(2, '0')}</span>
          {node.short}
        </span>
      )}
    </div>
  );
}

/* ---------------- KatIA companion ---------------- */
function KatiaCompanion({ x, y, currentName }) {
  return (
    <div className="katia-companion" style={{ left: x, top: y }}>
      <div className="kbubble">¡Tú puedes! <b>{currentName}</b> te espera.</div>
      <div className="katia-av">
        <img src="assets/katia-correcto.gif" alt="KatIA, tu mentora" />
        <span className="scan"></span>
      </div>
    </div>
  );
}

/* ---------------- Node detail bottom sheet ---------------- */
function NodeSheet({ data, onClose, onAction }) {
  const open = !!data;
  const n = data || {};
  const state = n.state || 'locked';
  const isReto = n.type === 'challenge';
  const iconCls = isReto ? 'reto' : state;
  let glyph;
  if (isReto) glyph = <IcStar />;
  else if (state === 'completed') glyph = <IcCheck />;
  else if (state === 'current') glyph = <IcBook />;
  else glyph = <IcLock />;

  const copy = {
    completed: { k: 'Completado', d: 'Ya dominaste este concepto. Repásalo cuando quieras para mantener tu racha.', btn: 'Repasar lección', cls: 'ghost' },
    current: { k: 'En curso', d: 'Tu próximo paso. Termina la lección para desbloquear el siguiente nodo del sendero.', btn: 'Empezar lección', cls: '' },
    locked: { k: 'Bloqueado', d: 'Completa el nodo anterior del camino para desbloquear este concepto.', btn: 'Bloqueado', cls: '', disabled: true },
    reserved: { k: 'Próximamente', d: 'Este contenido llegará en una próxima actualización del curso.', btn: 'Próximamente', cls: 'ghost', disabled: true },
  }[state];

  const retoCopy = isReto ? {
    k: 'Reto de Unidad', d: state === 'locked'
      ? 'Completa todos los nodos de la unidad para desbloquear el examen de cierre.'
      : 'Examen de cierre de la unidad. Apruébalo para desbloquear la siguiente unidad.',
    btn: state === 'locked' ? 'Bloqueado' : 'Empezar examen',
    cls: state === 'locked' ? '' : 'gold', disabled: state === 'locked',
  } : null;

  const c = retoCopy || copy;

  return (
    <React.Fragment>
      <div className={'node-modal-scrim' + (open ? ' open' : '')} onClick={onClose}></div>
      <div className={'node-modal' + (open ? ' open' : '')} role="dialog" aria-modal="true" aria-hidden={!open}>
        <button className="nm-close" onClick={onClose} aria-label="Cerrar">×</button>
        <div className="sheet-head">
          <div className={'sheet-icon ' + iconCls}>{glyph}</div>
          <div className="sheet-meta">
            <div className={'sheet-kicker ' + (isReto ? 'reto' : state)}>
              {isReto ? `${c.k} · U${n.unit}` : `${n.idx || ''} · ${c.k}`}
            </div>
            <div className="sheet-title">{n.name}</div>
          </div>
        </div>
        <p className="sheet-desc">{c.d}</p>
        <div className="sheet-stats">
          <div className="sheet-stat"><div className="ss-k">XP</div><div className="ss-v teal">+{isReto ? 120 : 40}</div></div>
          <div className="sheet-stat"><div className="ss-k">GEMAS</div><div className="ss-v gold">+{isReto ? 30 : 10}</div></div>
          <div className="sheet-stat"><div className="ss-k">LECCIONES</div><div className="ss-v">{isReto ? 1 : 3}</div></div>
        </div>
        <button className={'sheet-btn ' + (c.cls || '')} disabled={c.disabled} onClick={() => onAction(n)}>
          {c.btn}{!c.disabled && <IcArrow />}
        </button>
      </div>
    </React.Fragment>
  );
}

/* ---------------- toast ---------------- */
function MapToast({ msg }) {
  return (
    <div className={'map-toast' + (msg ? ' show' : '')} role="status">
      <span style={{ color: 'var(--accent-2)', width: 16, height: 16, display: 'block', flex: 'none' }}><IcInfo /></span>
      <span>{msg}</span>
    </div>
  );
}

Object.assign(window, {
  IcChevron, IcFlame, IcGem, IcCheck, IcLock, IcStar, IcBook, IcMap, IcTrophy, IcUser, IcArrow, IcInfo,
  Plant, TrailLayer, Sidebar, MapBar, RightRail, UnitBanner, NodeView, KatiaCompanion, NodeSheet, MapToast,
});
