// ============================================================
//  LevelUpElo — Mapa de contenido · DATA + GEOMETRY LAYER
//  Layer 2 of 3: anchor points (coords as % of canvas width +
//  absolute y in px) live here, decoupled from both the
//  background illustration (Layer 1) and the interactive nodes
//  (Layer 3). Adding a future unit = append rows here; nodes
//  inherit lane/zigzag, states and styles automatically.
// ============================================================

// fixed inner width of the app canvas (matches the device screen)
const MAP_W = 402;

// horizontal lanes as % of canvas width
const LANES = { C: 50, R: 71, L: 29 };
// zigzag descending: centro → derecha → centro → izquierda → (repite)
const LANE_SEQ = ['C', 'R', 'C', 'L'];
const laneFor = (gi) => LANE_SEQ[(gi - 1) % LANE_SEQ.length];

// vertical rhythm (px)
const GEO = {
  top: 54,        // first banner offset
  bannerToNode: 80,   // gap from a unit banner to its first node
  nodeGap: 90,    // node-center to node-center
  unitGap: 26,    // extra breathing room before the next banner
  bottom: 120,    // tail space below last node (KatIA / nav clearance)
};

// ---- unit definitions (banners / separators) -------------------
const UNITS = [
  { id: 1, label: 'Unidad 1', name: 'Básico',     tier: 'success' },
  { id: 2, label: 'Unidad 2', name: 'Intermedio', tier: 'primary' },
  { id: 3, label: 'Unidad 3', name: 'Avanzado',   tier: 'gold'    },
  { id: 4, label: 'Unidad 4', name: 'Extensión',  tier: 'mute', reserved: true },
];

// ---- the ordered curriculum (each node = one concept) ----------
const CURRICULUM = [
  { unit: 1, name: 'Variables' },
  { unit: 1, name: 'Constantes' },
  { unit: 1, name: 'Expresiones algebraicas' },
  { unit: 1, name: 'Términos semejantes' },
  { unit: 1, name: 'Reto de Unidad 1', type: 'challenge' },

  { unit: 2, name: 'Polinomios' },
  { unit: 2, name: 'Operaciones con polinomios' },
  { unit: 2, name: 'Productos notables' },
  { unit: 2, name: 'Reto de Unidad 2', type: 'challenge' },

  { unit: 3, name: 'Ecuaciones' },
  { unit: 3, name: 'Sistemas de ecuaciones' },
  { unit: 3, name: 'Casos de factorización' },
  { unit: 3, name: 'Reto de Unidad 3', type: 'challenge' },
];

// Unidad 4 — reserva de estructura (aún sin contenido)
const RESERVED = [
  { unit: 4, name: 'Matrices' },
  { unit: 4, name: 'Métodos matriciales' },
];

const SHORT = {
  'Expresiones algebraicas': 'Expresiones',
  'Operaciones con polinomios': 'Operaciones',
  'Casos de factorización': 'Factorización',
  'Sistemas de ecuaciones': 'Sistemas',
  'Métodos matriciales': 'Métodos',
};

// ============================================================
//  Build the laid-out map: walk units top→bottom, place a
//  banner then its nodes, accumulating y. Returns nodes (with
//  anchor coords), banners, and total scroll height.
// ============================================================
function buildLayout() {
  const nodes = [];
  const banners = [];
  let y = GEO.top;
  let gi = 0; // global node index (drives the zigzag + numbering)

  const placeUnit = (unitDef, rows, reserved) => {
    banners.push({ ...unitDef, y });
    y += GEO.bannerToNode;
    rows.forEach((row) => {
      gi += 1;
      const lane = laneFor(gi);
      nodes.push({
        id: gi,
        index: gi,
        name: row.name,
        short: SHORT[row.name] || row.name,
        unit: row.unit,
        type: row.type || (reserved ? 'reserved' : 'lesson'),
        reserved: !!reserved,
        lane,
        // anchor point — kept as % (x) so the layer is resolution-independent
        xPct: LANES[lane],
        x: (LANES[lane] / 100) * MAP_W,
        y,
      });
      y += GEO.nodeGap;
    });
    y += GEO.unitGap;
  };

  UNITS.filter((u) => !u.reserved).forEach((u) => {
    placeUnit(u, CURRICULUM.filter((r) => r.unit === u.id), false);
  });
  // reserved extension unit
  const u4 = UNITS.find((u) => u.reserved);
  placeUnit(u4, RESERVED, true);

  const height = y + GEO.bottom;
  return { nodes, banners, height };
}

// ============================================================
//  PATH SEGMENTS (Layer 1 geometry) — one reusable cubic per
//  consecutive node pair. The S-curve handles point vertically
//  so lanes connect with a smooth winding "stone path".
//  Segments are independent → chain more to extend the map.
// ============================================================
function buildSegments(nodes) {
  const segs = [];
  for (let i = 0; i < nodes.length - 1; i++) {
    const a = nodes[i];
    const b = nodes[i + 1];
    const dy = b.y - a.y;
    const c1y = a.y + dy * 0.5;
    const c2y = b.y - dy * 0.5;
    const d = `M ${a.x} ${a.y} C ${a.x} ${c1y}, ${b.x} ${c2y}, ${b.x} ${b.y}`;
    segs.push({ d, from: a.index, to: b.index });
  }
  return segs;
}

// derive a node's state purely from the current progress pointer.
// Art (Layer 1) never changes; only this logic flips states.
function deriveState(node, currentIndex) {
  if (node.reserved) return 'reserved';
  if (node.index < currentIndex) return 'completed';
  if (node.index === currentIndex) return 'current';
  return 'locked';
}

// decorative pixel-flora anchored to the sides of the trail —
// derived from node positions so they never sit on a node.
function buildPlants(nodes) {
  const kinds = ['sprout', 'crystal', 'shroom', 'sprout', 'crystal'];
  const plants = [];
  nodes.forEach((n, i) => {
    if (i % 2 !== 0) return;            // every other node
    if (n.reserved) return;
    const onLeft = n.lane === 'R' || (n.lane === 'C' && i % 4 === 0);
    plants.push({
      kind: kinds[i % kinds.length],
      x: onLeft ? n.xPct - 26 : n.xPct + 26,
      y: n.y + 30,
      flip: !onLeft,
      key: 'p' + i,
    });
  });
  return plants;
}

Object.assign(window, {
  MAP_W, LANES, UNITS, CURRICULUM, RESERVED,
  buildLayout, buildSegments, deriveState, buildPlants,
});
