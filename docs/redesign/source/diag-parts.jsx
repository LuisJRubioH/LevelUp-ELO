// ============================================================
//  LevelUpElo — Prueba diagnóstica · COMPONENTS
//  Iconos + pantallas (bienvenida, renderers de pregunta por
//  tipo, resultado). KatIA solo aparece en bienvenida y resultado
//  (ausente durante las preguntas, sin pistas de presión).
// ============================================================

/* ---------------- icons ---------------- */
const DxClose = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>);
const DxArrow = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>);
const DxSkip = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 5l7 7-7 7M13 5l7 7-7 7"/></svg>);
const DxHelp = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9.2 9a2.8 2.8 0 1 1 3.8 2.6c-.8.4-1 .9-1 1.7M12 17h.01"/><circle cx="12" cy="12" r="9.5"/></svg>);
const DxCheck = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12.5l4.5 4.5L19 7"/></svg>);
const DxX = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round"><path d="M7 7l10 10M17 7L7 17"/></svg>);
const DxLock = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9.5"/><path d="M12 8v4l3 2"/></svg>);
const DxBolt = () => (<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13 2 4 14h6l-1 8 9-12h-6l1-8z"/></svg>);
const DxGrip = () => (<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="9" cy="6" r="1.5"/><circle cx="15" cy="6" r="1.5"/><circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/><circle cx="9" cy="18" r="1.5"/><circle cx="15" cy="18" r="1.5"/></svg>);
const DxBook = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 5a2 2 0 0 1 2-2h6v16H6a2 2 0 0 0-2 2V5z"/><path d="M20 5a2 2 0 0 0-2-2h-6v16h6a2 2 0 0 1 2 2V5z"/></svg>);
const DxFlag = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 21V4M5 4h11l-2 4 2 4H5"/></svg>);
const DxBrain = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-1 5 3 3 0 0 0 2 4 3 3 0 0 0 5 1V4.5A2.5 2.5 0 0 0 9 4zM15 4a3 3 0 0 1 3 3 3 3 0 0 1 1 5 3 3 0 0 1-2 4 3 3 0 0 1-5 1"/></svg>);
const DxTrophy = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M7 4h10v4a5 5 0 0 1-10 0V4z"/><path d="M7 5H4v2a3 3 0 0 0 3 3M17 5h3v2a3 3 0 0 1-3 3M9 15h6M10 19h4M12 13v2"/></svg>);
const DxTarget = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.4" fill="currentColor"/></svg>);
const DxClock = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>);
const DxLayers = () => (<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3 3 8l9 5 9-5-9-5zM3 13l9 5 9-5M3 8v0"/></svg>);

/* ---------------- WELCOME ---------------- */
function Welcome({ total, onStart }) {
  return (
    <div className="wel">
      <div className="wel-kat">
        <img src="assets/katia-correcto.gif" alt="KatIA, tu mentora" />
        <span className="scan pix"></span>
      </div>
      <span className="wel-eyebrow">Prueba diagnóstica · Álgebra</span>
      <h1>Veamos <em>dónde empezar</em></h1>
      <p>Soy KatIA. Te haré unas preguntas para encontrar tu punto de partida en el mapa. No es un examen con nota: responde con calma y sin adivinar.</p>
      <div className="wel-points">
        <div className="wp">
          <span className="wp-ic"><DxClock /></span>
          <b>Sin tiempo</b><span>Tómate lo que necesites</span>
        </div>
        <div className="wp">
          <span className="wp-ic"><DxBrain /></span>
          <b>Se adapta a ti</b><span>{total} preguntas que ajustan su dificultad</span>
        </div>
        <div className="wp">
          <span className="wp-ic"><DxTarget /></span>
          <b>Tu punto de inicio</b><span>Define tu nivel en el mapa</span>
        </div>
      </div>
      <button className="dx-btn" onClick={onStart}>Comenzar <DxArrow /></button>
      <span className="wel-note">Si no sabes una respuesta, usa "No lo sé". Es mejor que adivinar.</span>
    </div>
  );
}

/* ---------------- QUESTION renderers by type ---------------- */
function OptionList({ q, value, onPick }) {
  const keys = ['A', 'B', 'C', 'D', 'E'];
  return (
    <div className="q-options" role="radiogroup">
      {q.options.map((opt, i) => (
        <button key={i} className={'opt' + (value === i ? ' sel' : '')} role="radio"
          aria-checked={value === i} onClick={() => onPick(i)}>
          <span className="opt-key">{keys[i]}</span>
          <span>{opt}</span>
        </button>
      ))}
    </div>
  );
}

function TrueFalse({ value, onPick }) {
  return (
    <div className="q-vf">
      <button className={'vf-btn t' + (value === true ? ' sel' : '')} onClick={() => onPick(true)}>
        <span className="vf-ic"><DxCheck /></span>Verdadero
      </button>
      <button className={'vf-btn' + (value === false ? ' sel' : '')} onClick={() => onPick(false)}>
        <span className="vf-ic"><DxX /></span>Falso
      </button>
    </div>
  );
}

function Numeric({ q, value, onPick }) {
  return (
    <div>
      <div className="q-num">
        <span className="num-eq">=</span>
        <input type="number" inputMode="decimal" placeholder="?" value={value ?? ''}
          onChange={(e) => onPick(e.target.value === '' ? null : Number(e.target.value))}
          aria-label="Tu respuesta numérica" />
      </div>
      <div className="q-num-hint">Escribe solo el número.</div>
    </div>
  );
}

function Procedure({ q, value, onPick }) {
  // value = array of step indices in chosen order
  const order = value || [];
  const inPool = q.steps.map((_, i) => i).filter((i) => !order.includes(i));
  const add = (i) => onPick([...order, i]);
  const removeFrom = (pos) => onPick(order.filter((_, p) => p !== pos));
  return (
    <div className="q-proc">
      <div className="proc-col">
        <span className="proc-label">Tu orden — toca para quitar</span>
        <div className="proc-pool">
          {order.length === 0 && <div className="proc-empty">Toca los pasos abajo en el orden correcto.</div>}
          {order.map((stepIdx, pos) => (
            <button key={stepIdx} className="proc-step" onClick={() => removeFrom(pos)}>
              <span className="ps-num">{pos + 1}</span>
              <span>{q.steps[stepIdx]}</span>
              <span className="ps-grip"><DxGrip /></span>
            </button>
          ))}
        </div>
      </div>
      {inPool.length > 0 && (
        <div className="proc-col">
          <span className="proc-label">Pasos disponibles</span>
          <div className="proc-pool">
            {inPool.map((i) => (
              <button key={i} className="proc-step pool" onClick={() => add(i)}>
                <span className="ps-num">+</span>
                <span>{q.steps[i]}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function QuestionCard({ q, index, value, onPick }) {
  const t = QT[q.type];
  return (
    <div className="qwrap q-anim" key={q.id}>
      <div className="q-meta">
        <span className="q-type-chip"><span className="ic">{t.ic}</span>{t.lbl}</span>
        <span className="q-concept">{q.concept}</span>
      </div>
      <h2 className="q-prompt">{q.prompt}</h2>
      {q.type === 'opcion' && <OptionList q={q} value={value} onPick={onPick} />}
      {q.type === 'vf' && <TrueFalse value={value} onPick={onPick} />}
      {q.type === 'numerica' && <Numeric q={q} value={value} onPick={onPick} />}
      {q.type === 'procedimiento' && <Procedure q={q} value={value} onPick={onPick} />}
    </div>
  );
}

/* ---------------- ARENA rail (variación B) ---------------- */
function ArenaRail({ index, total, answeredCount }) {
  return (
    <aside className="arena-rail">
      <div className="ar-brand"><img src="assets/logo.png" alt="LevelUp ELO" /></div>
      <div>
        <div className="ar-head" style={{ marginBottom: 12 }}>Diagnóstico</div>
        <div className="ar-pixbar">
          {Array.from({ length: total }).map((_, i) => (
            <span key={i} className={'ar-pix' + (i < index ? ' done' : i === index ? ' now' : '')}>
              {i < index ? '✓' : i + 1}
            </span>
          ))}
        </div>
      </div>
      <div className="ar-stat">
        <span className="k">Pregunta</span>
        <span className="v">{String(index + 1).padStart(2, '0')}<span style={{ color: 'var(--mute)', fontSize: 18 }}> / {total}</span></span>
        <span className="hidden-elo"><DxLock /> ELO oculto hasta el final</span>
      </div>
    </aside>
  );
}

/* ---------------- RESULT ---------------- */
function ThemeRow({ th }) {
  const tag = { strong: 'Fortaleza', mid: 'En progreso', gap: 'A reforzar' }[th.status];
  return (
    <div className="th-row">
      <span className={'th-ic ' + th.status}>{th.status === 'strong' ? <DxCheck /> : th.status === 'mid' ? <DxBolt /> : <DxTarget />}</span>
      <div className="th-body">
        <div className="th-top">
          <span className="th-name">{th.label}</span>
          <span className={'th-tag ' + th.status}>{tag}</span>
        </div>
        <div className="th-bar"><i className={th.status} style={{ width: Math.round(th.ratio * 100) + '%' }}></i></div>
      </div>
    </div>
  );
}

function Result({ data, onGoMap, onRetry }) {
  const { elo, league, themes, startName, startUnit, startNode } = data;
  // ELO scale pin position (760–1500 range mapped)
  const pinPct = Math.max(2, Math.min(98, ((elo - 760) / (1500 - 760)) * 100));
  const strengths = themes.filter((t) => t.status === 'strong').map((t) => t.label);
  const gaps = themes.filter((t) => t.status === 'gap').map((t) => t.label);

  let summary;
  if (strengths.length && gaps.length) summary = `Dominas ${strengths.join(' y ')}. Empezaremos reforzando ${gaps.join(' y ')} para que avances con base sólida.`;
  else if (strengths.length) summary = `¡Gran base! Te ubicamos más adelante en el mapa para que no repitas lo que ya sabes.`;
  else summary = `Construiremos desde los fundamentos. Cada nodo que completes sube tu ELO y abre el siguiente.`;

  return (
    <div className="res">
      <div className="res-hero res-reveal d1">
        <div className="res-kat"><img src="assets/katia-correcto.gif" alt="KatIA" /><span className="scan pix"></span></div>
        <div className="res-hero-txt">
          <div className="res-eyebrow">Diagnóstico completo</div>
          <h1>Tu punto de partida está listo</h1>
          <p>{summary}</p>
        </div>
      </div>

      <div className="res-grid">
        <div className="res-card res-reveal d2">
          <div className="rc-h">Tu ELO inicial</div>
          <div className="elo-row">
            <div className="elo-badge" style={{ color: league.color }}>
              <span className="eb-ring"></span>
              <span style={{ color: league.color }}><DxTrophy /></span>
            </div>
            <div className="elo-meta">
              <div className="em-elo">{elo}<span> ELO</span></div>
              <div className="em-league"><span className="dot" style={{ background: league.color }}></span>Liga {league.name} · {league.rank}</div>
            </div>
          </div>
          <div className="elo-scale">
            <i></i>
            <span className="pin" style={{ left: pinPct + '%' }}></span>
          </div>
          <div className="elo-scale-labels"><span>BRONCE</span><span>PLATA</span><span>ORO</span><span>DIAMANTE</span></div>
        </div>

        <div className="res-card res-reveal d2">
          <div className="rc-h">Empiezas en el mapa</div>
          <div className="start-row">
            <div className="start-node"><DxBook /></div>
            <div className="start-txt">
              <div className="st-k">Nodo {String(startNode).padStart(2, '0')} · Unidad {startUnit}</div>
              <div className="st-name">{startName}</div>
              <div className="st-unit">Desbloqueado según tu diagnóstico</div>
            </div>
          </div>
          <div style={{ height: 1, background: 'var(--border)', margin: '18px 0' }}></div>
          <div className="start-txt" style={{ display: 'flex', gap: 18 }}>
            <div><div className="st-k">Aciertos</div><div className="st-name" style={{ fontSize: 18, color: 'var(--accent-2)' }}>{data.correctTotal}/{data.answered}</div></div>
            <div><div className="st-k">Nivel sugerido</div><div className="st-name" style={{ fontSize: 18 }}>{THEMES[themes.find(t=>t.status!=='strong')?.key || 'ecuaciones'].label}</div></div>
          </div>
        </div>
      </div>

      <div className="res-card res-reveal d3">
        <div className="rc-h">Desglose por tema — fortalezas y vacíos</div>
        <div className="themes">
          {themes.map((th) => <ThemeRow key={th.key} th={th} />)}
        </div>
      </div>

      <div className="res-cta res-reveal d4">
        <button className="dx-btn ghost" onClick={onRetry}>Repetir diagnóstico</button>
        <button className="dx-btn" onClick={onGoMap}>Ir a mi mapa <DxArrow /></button>
      </div>
    </div>
  );
}

Object.assign(window, {
  DxClose, DxArrow, DxSkip, DxHelp, DxCheck, DxX, DxLock, DxBolt, DxBook, DxFlag,
  DxBrain, DxTrophy, DxTarget, DxClock, DxLayers, DxGrip,
  Welcome, QuestionCard, ArenaRail, Result,
});
