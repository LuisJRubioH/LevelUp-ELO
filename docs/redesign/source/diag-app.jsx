// ============================================================
//  LevelUpElo — Prueba diagnóstica · APP
//  Máquina de estados: welcome → question(i) → result.
//  Lleva las respuestas (correct/wrong/dontknow/skip), calcula el
//  ELO al final (oculto durante el examen) y ofrece 2 variaciones
//  de la pantalla de pregunta vía Tweaks (calmado / arena).
// ============================================================

const { useState, useMemo, useRef, useEffect, useCallback } = React;
const {
  TweaksPanel, TweakSection, TweakRadio, TweakToggle, TweakColor, TweakButton, useTweaks,
} = window;

const DX_DEFAULTS = /*EDITMODE-BEGIN*/{
  "layout": "calmado",
  "accent": "#8b5cf6",
  "ok": "#2dd4bf",
  "pixel": true,
  "theme": "dark",
  "allowSkip": true,
  "outcome": "mixto"
}/*EDITMODE-END*/;

// para la demo: cómo se "responde" automáticamente al avanzar, de
// modo que el resultado tenga un perfil realista de fortalezas/vacíos.
function judge(q, answer, forced) {
  if (forced) return forced;            // 'dontknow' | 'skip'
  if (answer == null) return 'skip';
  if (q.type === 'opcion') return answer === q.correct ? 'correct' : 'wrong';
  if (q.type === 'vf') return answer === q.correct ? 'correct' : 'wrong';
  if (q.type === 'numerica') return Number(answer) === q.answer ? 'correct' : 'wrong';
  if (q.type === 'procedimiento') {
    const ok = Array.isArray(answer) && answer.length === q.steps.length && answer.every((v, i) => v === i);
    return ok ? 'correct' : 'wrong';
  }
  return 'skip';
}

function DiagApp() {
  const [t, setTweak] = useTweaks(DX_DEFAULTS);
  const rootRef = useRef(null);
  const total = QUESTIONS.length;

  const [phase, setPhase] = useState('welcome');  // welcome | quiz | result
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState({});     // qid -> value
  const [records, setRecords] = useState([]);     // [{qid, outcome}]
  const [toast, setToast] = useState('');
  const toastTimer = useRef(null);

  // ---- apply tweakable tokens ----
  useEffect(() => {
    const el = rootRef.current;
    if (!el) return;
    el.style.setProperty('--accent', t.accent);
    el.style.setProperty('--dx-accent', t.accent);
    el.style.setProperty('--accent-soft', `color-mix(in srgb, ${t.accent} 62%, white)`);
    el.style.setProperty('--glow-a', `color-mix(in srgb, ${t.accent} 42%, transparent)`);
    el.style.setProperty('--accent-2', t.ok);
    el.style.setProperty('--dx-ok', t.ok);
    el.style.setProperty('--accent-2-soft', `color-mix(in srgb, ${t.ok} 58%, white)`);
  }, [t.accent, t.ok]);

  useEffect(() => {
    document.documentElement.classList.toggle('light', t.theme === 'light');
    document.body.dataset.pixel = t.pixel ? 'on' : 'off';
  }, [t.theme, t.pixel]);

  const flashToast = useCallback((msg) => {
    setToast(msg);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(''), 2000);
  }, []);

  const q = QUESTIONS[index];
  const curVal = q ? answers[q.id] : undefined;
  const hasAnswer = curVal !== undefined && curVal !== null &&
    !(Array.isArray(curVal) && curVal.length === 0);

  const pick = (val) => setAnswers((a) => ({ ...a, [q.id]: val }));

  const recordAndAdvance = (outcome) => {
    const rec = { qid: q.id, outcome };
    const nextRecords = [...records.filter((r) => r.qid !== q.id), rec];
    setRecords(nextRecords);
    if (index + 1 >= total) {
      setPhase('result');
    } else {
      setIndex((i) => i + 1);
    }
  };

  const onNext = () => recordAndAdvance(judge(q, curVal));
  const onDontKnow = () => { flashToast('Marcado como "No lo sé" — sin penalización'); recordAndAdvance('dontknow'); };
  const onSkip = () => { flashToast('Pregunta saltada'); recordAndAdvance('skip'); };

  const restart = () => { setPhase('welcome'); setIndex(0); setAnswers({}); setRecords([]); };

  const result = useMemo(() => phase === 'result' ? scoreDiagnostic(records) : null, [phase, records]);

  const progressPct = phase === 'result' ? 100 : Math.round((index / total) * 100);

  return (
    <div className="dx" ref={rootRef} data-layout={t.layout}>
      {/* top progress bar (calmado layout) */}
      {phase !== 'welcome' && (
        <div className="dx-top">
          <button className="dx-close" onClick={restart} aria-label="Salir del diagnóstico"><DxClose /></button>
          <div className="dx-progress" role="progressbar" aria-valuenow={progressPct} aria-valuemin={0} aria-valuemax={100}>
            <i style={{ width: progressPct + '%' }}></i>
          </div>
          <span className="dx-count"><b>{phase === 'result' ? total : index + 1}</b> / {total}</span>
        </div>
      )}

      <div className="dx-body">
        {phase === 'quiz' && t.layout === 'arena' && (
          <ArenaRail index={index} total={total} answeredCount={records.length} />
        )}

        <div className="dx-center" data-screen-label={phase === 'welcome' ? 'Diagnóstico · Bienvenida' : phase === 'result' ? 'Diagnóstico · Resultado' : `Diagnóstico · Pregunta ${index + 1}`}>
          {phase === 'welcome' && <Welcome total={total} onStart={() => { setPhase('quiz'); setIndex(0); }} />}

          {phase === 'quiz' && (
            <div className="qwrap-outer" style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 26, maxWidth: t.layout === 'arena' ? 620 : 600, margin: '0 auto' }}>
              <QuestionCard q={q} index={index} value={curVal} onPick={pick} />
              <div className="q-foot">
                {t.allowSkip && <button className="dx-link" onClick={onSkip}><DxSkip /> Saltar</button>}
                <button className="dx-link" onClick={onDontKnow}><DxHelp /> No lo sé</button>
                <span className="grow"></span>
                <button className="dx-btn" onClick={onNext} disabled={!hasAnswer}>
                  {index + 1 >= total ? 'Ver resultado' : 'Siguiente'} <DxArrow />
                </button>
              </div>
            </div>
          )}

          {phase === 'result' && result && (
            <Result data={result}
              onGoMap={() => flashToast('Abriendo tu mapa de Álgebra…')}
              onRetry={restart} />
          )}
        </div>
      </div>

      <div className={'dx-toast' + (toast ? ' show' : '')} role="status">
        <DxBolt /><span>{toast}</span>
      </div>

      <TweaksPanel>
        <TweakSection label="Pantalla de pregunta" />
        <TweakRadio label="Variación de layout" value={t.layout}
          options={['calmado', 'arena']}
          onChange={(v) => setTweak('layout', v)} />
        <TweakToggle label='Permitir "Saltar"' value={t.allowSkip}
          onChange={(v) => setTweak('allowSkip', v)} />
        <TweakSection label="Flujo (demo)" />
        <TweakButton label="Reiniciar diagnóstico" onClick={restart} />
        <TweakSection label="Estilo" />
        <TweakToggle label="Detalle pixel-art" value={t.pixel}
          onChange={(v) => setTweak('pixel', v)} />
        <TweakColor label="Primario" value={t.accent}
          options={['#8b5cf6', '#6366f1', '#3b82f6', '#d946ef']}
          onChange={(v) => setTweak('accent', v)} />
        <TweakColor label="Acierto / acento" value={t.ok}
          options={['#2dd4bf', '#22c55e', '#06b6d4', '#84cc16']}
          onChange={(v) => setTweak('ok', v)} />
        <TweakRadio label="Tema" value={t.theme} options={['dark', 'light']}
          onChange={(v) => setTweak('theme', v)} />
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<DiagApp />);
