// ============================================================
//  LevelUpElo — Prueba diagnóstica (onboarding) · DATA + ENGINE
//  Examen adaptativo de entrada que asigna el ELO inicial y, con
//  él, la unidad/nodo donde el alumno empieza en el Mapa.
//  La DIFICULTAD de cada pregunta vive aquí pero NO se muestra
//  durante el examen — solo alimenta el motor y se revela en el
//  resultado (desglose por tema).
// ============================================================

// ---- temas del diagnóstico (espejo del currículo del mapa) ----
const THEMES = {
  fundamentos:  { label: 'Fundamentos',   sub: 'Variables · constantes · expresiones', unit: 1 },
  operaciones:  { label: 'Operaciones',   sub: 'Términos semejantes · polinomios',     unit: 2 },
  notables:     { label: 'Prod. notables',sub: 'Productos y factorización',            unit: 3 },
  ecuaciones:   { label: 'Ecuaciones',    sub: 'Lineales · sistemas',                  unit: 3 },
};

// dificultad → peso ELO (oculto en el examen)
const DIFF = {
  facil:   { lbl: 'Fácil',   win: 14, loss: -20, k: 0.8 },
  media:   { lbl: 'Media',   win: 22, loss: -12, k: 1.0 },
  dificil: { lbl: 'Difícil', win: 34, loss: -6,  k: 1.3 },
};

// tipos de pregunta (hereda íconos del gestor de exámenes docente)
const QT = {
  opcion:        { lbl: 'Opción múltiple', ic: '◉' },
  numerica:      { lbl: 'Respuesta numérica', ic: '#' },
  vf:            { lbl: 'Verdadero o falso', ic: '◑' },
  procedimiento: { lbl: 'Procedimiento', ic: '∑' },
};

// ============================================================
//  BANCO DE PREGUNTAS (orden de dificultad creciente; el motor
//  real reordenaría adaptativamente, aquí va una secuencia fija
//  representativa para el diseño del flujo).
// ============================================================
const QUESTIONS = [
  {
    id: 'q1', theme: 'fundamentos', diff: 'facil', type: 'opcion',
    concept: 'Variables',
    prompt: 'En la expresión 3x + 5, ¿qué representa la letra x?',
    options: ['Un valor que puede cambiar', 'El número 3', 'Una constante fija', 'El resultado de la suma'],
    correct: 0,
  },
  {
    id: 'q2', theme: 'fundamentos', diff: 'facil', type: 'vf',
    concept: 'Constantes',
    prompt: 'En 7y − 4, el número 4 es una constante.',
    correct: true,
  },
  {
    id: 'q3', theme: 'fundamentos', diff: 'media', type: 'numerica',
    concept: 'Expresiones algebraicas',
    prompt: 'Evalúa la expresión 2x + 3 cuando x = 4.',
    answer: 11, unit: '',
  },
  {
    id: 'q4', theme: 'operaciones', diff: 'media', type: 'opcion',
    concept: 'Términos semejantes',
    prompt: '¿Cuál es el resultado de reducir 5a + 3a − 2a?',
    options: ['6a', '10a', '6a²', '0'],
    correct: 0,
  },
  {
    id: 'q5', theme: 'operaciones', diff: 'media', type: 'numerica',
    concept: 'Polinomios',
    prompt: '¿Cuál es el grado del polinomio 4x³ − 2x + 7 ?',
    answer: 3, unit: '',
  },
  {
    id: 'q6', theme: 'operaciones', diff: 'dificil', type: 'opcion',
    concept: 'Operaciones con polinomios',
    prompt: 'Multiplica: (x + 2)(x + 3).',
    options: ['x² + 5x + 6', 'x² + 6x + 5', 'x² + 6', '2x + 5'],
    correct: 0,
  },
  {
    id: 'q7', theme: 'notables', diff: 'media', type: 'opcion',
    concept: 'Productos notables',
    prompt: 'Desarrolla el binomio al cuadrado (x + 4)².',
    options: ['x² + 8x + 16', 'x² + 16', 'x² + 4x + 16', '2x + 8'],
    correct: 0,
  },
  {
    id: 'q8', theme: 'notables', diff: 'dificil', type: 'procedimiento',
    concept: 'Casos de factorización',
    prompt: 'Ordena los pasos para factorizar x² + 5x + 6.',
    steps: [
      'Buscar dos números que multiplicados den 6 y sumados den 5',
      'Esos números son 2 y 3',
      'Escribir como (x + 2)(x + 3)',
    ],
  },
  {
    id: 'q9', theme: 'ecuaciones', diff: 'media', type: 'numerica',
    concept: 'Ecuaciones',
    prompt: 'Resuelve para x:  2x + 6 = 14.',
    answer: 4, unit: '',
  },
  {
    id: 'q10', theme: 'ecuaciones', diff: 'dificil', type: 'procedimiento',
    concept: 'Sistemas de ecuaciones',
    prompt: 'Ordena los pasos para resolver  x + y = 10,  x − y = 2  por reducción.',
    steps: [
      'Sumar ambas ecuaciones: 2x = 12',
      'Despejar x = 6',
      'Sustituir en x + y = 10 → y = 4',
    ],
  },
];

// ============================================================
//  MOTOR ELO (oculto durante el examen)
//  Arranca en una base neutra y se mueve según acierto/dificultad.
//  "No lo sé" y "Saltar" no penalizan el ELO pero marcan vacío en
//  el tema (señal honesta, sin adivinar).
// ============================================================
const ELO_BASE = 1000;

// answer record: { qid, outcome: 'correct'|'wrong'|'dontknow'|'skip' }
function scoreDiagnostic(records) {
  let elo = ELO_BASE;
  const byTheme = {};
  Object.keys(THEMES).forEach((t) => { byTheme[t] = { correct: 0, total: 0, attempted: 0 }; });

  records.forEach((r) => {
    const q = QUESTIONS.find((x) => x.id === r.qid);
    if (!q) return;
    const d = DIFF[q.diff];
    const th = byTheme[q.theme];
    th.total += 1;
    if (r.outcome === 'correct') { elo += d.win; th.correct += 1; th.attempted += 1; }
    else if (r.outcome === 'wrong') { elo += d.loss; th.attempted += 1; }
    // dontknow / skip: sin cambio de ELO, cuenta como vacío del tema
  });

  elo = Math.max(760, Math.round(elo));

  const league = LEAGUES.find((l) => elo >= l.min) || LEAGUES[LEAGUES.length - 1];

  // desglose por tema
  const themes = Object.keys(THEMES).map((key) => {
    const t = byTheme[key];
    const ratio = t.total ? t.correct / t.total : 0;
    let status = 'gap';
    if (ratio >= 0.67) status = 'strong';
    else if (ratio >= 0.34) status = 'mid';
    return { key, ...THEMES[key], ...t, ratio, status };
  });

  // ubicación en el mapa: primer tema con vacío marca dónde empezar.
  // si domina todo → empieza más adelante.
  const strongCount = themes.filter((t) => t.status === 'strong').length;
  let startUnit = 1, startNode = 1, startName = 'Variables';
  if (strongCount >= 4) { startUnit = 3; startNode = 10; startName = 'Ecuaciones'; }
  else if (strongCount === 3) { startUnit = 2; startNode = 6; startName = 'Polinomios'; }
  else if (strongCount === 2) { startUnit = 1; startNode = 4; startName = 'Términos semejantes'; }
  else if (strongCount === 1) { startUnit = 1; startNode = 3; startName = 'Expresiones algebraicas'; }
  else { startUnit = 1; startNode = 1; startName = 'Variables'; }

  const correctTotal = records.filter((r) => r.outcome === 'correct').length;

  return { elo, league, themes, startUnit, startNode, startName, correctTotal, answered: records.length };
}

const LEAGUES = [
  { id: 'diamante', name: 'Diamante', min: 1320, color: '#7dd3fc', rank: 'Avanzado' },
  { id: 'oro',      name: 'Oro',      min: 1180, color: '#ffd700', rank: 'Intermedio-alto' },
  { id: 'plata',    name: 'Plata',    min: 1040, color: '#cbd5e1', rank: 'Intermedio' },
  { id: 'bronce',   name: 'Bronce',   min: 0,    color: '#d8975a', rank: 'Inicial' },
];

Object.assign(window, {
  THEMES, DIFF, QT, QUESTIONS, ELO_BASE, LEAGUES, scoreDiagnostic,
});
