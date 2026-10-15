// ============================================================
//  LevelUpElo — Mapa de contenido · APP (escritorio)
//  Shell hermano de la consola docente: sidebar + mapa central
//  scrollable + rail derecho. El progreso es lo único que cambia
//  el estado de los nodos; la ilustración (trail + plantas) nunca
//  se redibuja.
// ============================================================

const { useState, useMemo, useRef, useEffect, useCallback } = React;
const {
  TweaksPanel, TweakSection, TweakSlider, TweakToggle, TweakRadio, TweakColor, useTweaks,
} = window;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "primary": "#8b5cf6",
  "success": "#2dd4bf",
  "pathStyle": "stones",
  "plants": true,
  "katia": true,
  "pixel": true,
  "theme": "dark",
  "progress": 3
}/*EDITMODE-END*/;

function MapApp() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);

  const { nodes, banners, height } = useMemo(() => buildLayout(), []);
  const segments = useMemo(() => buildSegments(nodes), [nodes]);
  const plants = useMemo(() => buildPlants(nodes), [nodes]);

  const currentIndex = Math.round(t.progress);
  const [nav, setNav] = useState('mapa');
  const [sheet, setSheet] = useState(null);
  const [toast, setToast] = useState('');
  const [shakeId, setShakeId] = useState(null);
  const scrollRef = useRef(null);
  const toastTimer = useRef(null);
  const rootRef = useRef(null);

  // ---- apply tweakable tokens onto the inherited brand vars ----
  useEffect(() => {
    const el = rootRef.current;
    if (!el) return;
    el.style.setProperty('--accent', t.primary);
    el.style.setProperty('--m-primary', t.primary);
    el.style.setProperty('--accent-soft', `color-mix(in srgb, ${t.primary} 62%, white)`);
    el.style.setProperty('--glow-a', `color-mix(in srgb, ${t.primary} 42%, transparent)`);
    el.style.setProperty('--accent-2', t.success);
    el.style.setProperty('--m-success', t.success);
    el.style.setProperty('--accent-2-soft', `color-mix(in srgb, ${t.success} 58%, white)`);
  }, [t.primary, t.success]);

  useEffect(() => {
    document.documentElement.classList.toggle('light', t.theme === 'light');
    document.body.dataset.pixel = t.pixel ? 'on' : 'off';
  }, [t.theme, t.pixel]);

  // ---- keep the current node in view inside the map column ----
  useEffect(() => {
    const sc = scrollRef.current;
    if (!sc) return;
    const cn = nodes.find((n) => n.index === currentIndex);
    if (!cn) return;
    const target = cn.y - sc.clientHeight * 0.4;
    sc.scrollTo({ top: Math.max(0, target), behavior: 'smooth' });
  }, [currentIndex, nodes]);

  const flashToast = useCallback((msg) => {
    setToast(msg);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(''), 2200);
  }, []);

  const activate = useCallback((node, state) => {
    if (state === 'locked' || state === 'reserved') {
      setShakeId(node.id);
      setTimeout(() => setShakeId(null), 420);
      flashToast(state === 'reserved'
        ? 'Disponible en una próxima actualización'
        : 'Completa el nodo anterior para desbloquear');
      return;
    }
    setSheet({ ...node, state, idx: 'Nodo ' + String(node.index).padStart(2, '0') });
  }, [flashToast]);

  const sheetAction = useCallback((n) => {
    const verb = n.type === 'challenge' ? 'Iniciando examen'
      : n.state === 'completed' ? 'Repasando' : 'Abriendo lección';
    flashToast(`${verb}: ${n.name}`);
    setSheet(null);
  }, [flashToast]);

  const onNav = useCallback((id) => {
    setNav(id);
    if (id !== 'mapa') flashToast(`${id === 'ligas' ? 'Ligas' : 'Perfil'} — demo`);
  }, [flashToast]);

  // unit progress strings for banners + rail
  const unitProgress = useMemo(() => {
    const map = {};
    UNITS.forEach((u) => {
      const inUnit = nodes.filter((n) => n.unit === u.id);
      const done = inUnit.filter((n) => n.index < currentIndex).length;
      map[u.id] = `${done}/${inUnit.length}`;
    });
    return map;
  }, [nodes, currentIndex]);

  const lessonNodes = nodes.filter((n) => !n.reserved);
  const doneCount = lessonNodes.filter((n) => n.index < currentIndex).length;
  const currentNode = nodes.find((n) => n.index === currentIndex) || lessonNodes[lessonNodes.length - 1];

  // nodes left to reach this unit's Reto
  const unitReto = nodes.find((n) => n.unit === currentNode.unit && n.type === 'challenge');
  const retoLeft = unitReto ? Math.max(0, unitReto.index - currentIndex) : 0;

  // KatIA companion position beside the current node
  let katiaX = 201, katiaY = 0;
  if (currentNode) {
    katiaX = currentNode.lane === 'R' ? currentNode.x - 104 : currentNode.x + 104;
    katiaX = Math.max(82, Math.min(MAP_W - 70, katiaX));
    katiaY = currentNode.y + 30;
  }

  const onContinue = () => activate(currentNode, deriveState(currentNode, currentIndex));

  return (
    <div className="lu" ref={rootRef} data-path={t.pathStyle}>
      <Sidebar active={nav} onNav={onNav} streak={5} gems={120}
        theme={t.theme} onTheme={() => setTweak('theme', t.theme === 'light' ? 'dark' : 'light')} />

      <main className="lu-map" ref={scrollRef} data-screen-label="Mapa · Álgebra">
        <MapBar onBack={() => flashToast('Volver a mis cursos')} done={doneCount} total={lessonNodes.length} />

        <div className="map-stage">
          <div className="map-canvas" style={{ height }}>
            {/* Layer 1 — illustration: trail + plants (recolorable) */}
            <TrailLayer segments={segments} currentIndex={currentIndex} height={height} />
            {t.plants && plants.map((p) => (
              <div key={p.key} className={'plant' + (p.flip ? ' flip' : '')}
                style={{ left: (p.x / 100 * MAP_W), top: p.y }} aria-hidden="true">
                <Plant kind={p.kind} />
              </div>
            ))}

            {/* unit banners (separators) */}
            {banners.map((u) => (
              <UnitBanner key={u.id} unit={u} progress={unitProgress[u.id]} />
            ))}

            {/* Layer 3 — interactive nodes */}
            <div className="map-nodes">
              {nodes.map((n) => (
                <NodeView key={n.id} node={n}
                  state={deriveState(n, currentIndex)}
                  shaking={shakeId === n.id}
                  onActivate={activate} />
              ))}
            </div>

            {/* KatIA companion beside the current node */}
            {t.katia && currentNode && (
              <KatiaCompanion x={katiaX} y={katiaY} currentName={currentNode.short} />
            )}
          </div>
        </div>
      </main>

      <RightRail currentNode={currentNode} onContinue={onContinue}
        units={UNITS} unitProgress={unitProgress} retoLeft={retoLeft} />

      <NodeSheet data={sheet} onClose={() => setSheet(null)} onAction={sheetAction} />
      <MapToast msg={toast} />

      <TweaksPanel>
        <TweakSection label="Progreso" />
        <TweakSlider label="Nodo actual" value={t.progress} min={1} max={13} step={1}
          onChange={(v) => setTweak('progress', v)} />
        <TweakSection label="Sendero" />
        <TweakRadio label="Estilo del camino" value={t.pathStyle}
          options={['stones', 'solid', 'dashed']}
          onChange={(v) => setTweak('pathStyle', v)} />
        <TweakToggle label="Plantas decorativas" value={t.plants}
          onChange={(v) => setTweak('plants', v)} />
        <TweakToggle label="Mascota KatIA" value={t.katia}
          onChange={(v) => setTweak('katia', v)} />
        <TweakToggle label="Detalle pixel-art" value={t.pixel}
          onChange={(v) => setTweak('pixel', v)} />
        <TweakSection label="Color" />
        <TweakColor label="Primario (actual)" value={t.primary}
          options={['#8b5cf6', '#6366f1', '#3b82f6', '#d946ef']}
          onChange={(v) => setTweak('primary', v)} />
        <TweakColor label="Éxito (completado)" value={t.success}
          options={['#2dd4bf', '#22c55e', '#06b6d4', '#84cc16']}
          onChange={(v) => setTweak('success', v)} />
        <TweakRadio label="Tema" value={t.theme} options={['dark', 'light']}
          onChange={(v) => setTweak('theme', v)} />
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<MapApp />);
