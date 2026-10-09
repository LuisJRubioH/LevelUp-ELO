/* Oulad teacher console — sample data + helpers (realistic populated state) */

/* Topic / course palette (matches dashboard chips) */
const TOPICS = [
  { id: "algebra",  name: "Álgebra",      slug: "algebra_basica",    color: "#8b5cf6" },
  { id: "aritmetica", name: "Aritmética", slug: "aritmetica_basica",  color: "#2dd4bf" },
  { id: "geometria", name: "Geometría",   slug: "geometria",          color: "#f59e0b" },
  { id: "trigonometria", name: "Trigonometría", slug: "trigonometria", color: "#ec4899" },
];
const topicById = (id) => TOPICS.find(t => t.id === id) || TOPICS[0];

/* ELO → rank tiers (16-rank ladder, condensed to named tiers) */
const RANKS = [
  { min: 0,    name: "HIERRO",   fg: "#9ca3af", bg: "rgba(156,163,175,.16)" },
  { min: 950,  name: "BRONCE",   fg: "#c2814e", bg: "rgba(194,129,78,.18)" },
  { min: 1150, name: "PLATA",    fg: "#cbd5e1", bg: "rgba(203,213,225,.16)" },
  { min: 1350, name: "ORO",      fg: "#fbbf24", bg: "rgba(251,191,36,.16)" },
  { min: 1550, name: "PLATINO",  fg: "#5eead4", bg: "rgba(94,234,212,.16)" },
  { min: 1750, name: "DIAMANTE", fg: "#7dd3fc", bg: "rgba(125,211,252,.16)" },
  { min: 1950, name: "MAESTRO",  fg: "#c4b5fd", bg: "rgba(196,181,253,.18)" },
];
const rankFor = (elo) => { let r = RANKS[0]; for (const x of RANKS) if (elo >= x.min) r = x; return r; };

/* avatar gradient by name */
const AVAS = [
  "linear-gradient(140deg,#8b5cf6,#6366f1)", "linear-gradient(140deg,#2dd4bf,#0ea5e9)",
  "linear-gradient(140deg,#f59e0b,#ef4444)", "linear-gradient(140deg,#ec4899,#8b5cf6)",
  "linear-gradient(140deg,#10b981,#22d3ee)", "linear-gradient(140deg,#f43f5e,#f59e0b)",
];
const initials = (n) => n.split(" ").slice(0,2).map(w => w[0]).join("").toUpperCase();
const avaFor = (n) => AVAS[(n.charCodeAt(0) + n.length) % AVAS.length];
const accColor = (a) => a >= 80 ? "#34d399" : a >= 65 ? "#fbbf24" : "#f87171";

/* students */
const STUDENTS = [
  { name: "Mateo Restrepo",   user: "mateo_r",   topic: "algebra",       elo: 1986, acc: 91, last: "hace 2 h",  dElo: +34, attempts: 312, attn: false },
  { name: "Valentina Ortiz",  user: "vale_o",    topic: "geometria",     elo: 1842, acc: 88, last: "hace 5 h",  dElo: +21, attempts: 268, attn: false },
  { name: "Samuel Cárdenas",  user: "samu_c",    topic: "algebra",       elo: 1788, acc: 84, last: "ayer",      dElo: +12, attempts: 240, attn: false },
  { name: "Isabella Méndez",  user: "isa_m",     topic: "trigonometria", elo: 1701, acc: 79, last: "hace 3 h",  dElo: +27, attempts: 198, attn: false },
  { name: "Tomás Aguirre",    user: "tomas_a",   topic: "aritmetica",    elo: 1654, acc: 82, last: "hace 1 d",  dElo: +8,  attempts: 221, attn: false },
  { name: "Luciana Páez",     user: "luci_p",    topic: "geometria",     elo: 1588, acc: 74, last: "hace 6 h",  dElo: +15, attempts: 176, attn: false },
  { name: "Daniel Quiroga",   user: "dani_q",    topic: "algebra",       elo: 1432, acc: 68, last: "hace 2 d",  dElo: -6,  attempts: 154, attn: false },
  { name: "Antonia Vega",     user: "anto_v",    topic: "trigonometria", elo: 1377, acc: 61, last: "hace 4 d",  dElo: -18, attempts: 132, attn: true  },
  { name: "Emiliano Ríos",    user: "emi_r",     topic: "aritmetica",    elo: 1298, acc: 66, last: "hace 1 d",  dElo: +4,  attempts: 119, attn: false },
  { name: "Camila Suárez",    user: "cami_s",    topic: "geometria",     elo: 1184, acc: 54, last: "hace 5 d",  dElo: -22, attempts: 98,  attn: true  },
  { name: "Joaquín Beltrán",  user: "joaco_b",   topic: "algebra",       elo: 1096, acc: 49, last: "hace 8 d",  dElo: -31, attempts: 74,  attn: true  },
  { name: "Renata Lozano",    user: "rena_l",    topic: "aritmetica",    elo: 1027, acc: 58, last: "hace 3 h",  dElo: +19, attempts: 61,  attn: false },
];

/* aggregate stats */
const fmtMiles = (n) => n.toLocaleString("es-CO");
const computeStats = (students) => {
  const n = students.length;
  const elo = Math.round(students.reduce((s, x) => s + x.elo, 0) / n);
  const acc = Math.round(students.reduce((s, x) => s + x.acc, 0) / n);
  return { groups: TOPICS.length, students: n, elo, acc };
};

/* per-topic counts + mastery (avg accuracy) */
const topicCounts = (students) => TOPICS.map(t => {
  const list = students.filter(s => s.topic === t.id);
  const mastery = list.length ? Math.round(list.reduce((s,x)=>s+x.acc,0)/list.length) : 0;
  return { ...t, count: list.length, mastery };
});

/* ELO distribution buckets for histogram */
const eloBuckets = (students) => {
  const defs = [["<1100","#",0,1100],["1100–1300",0,1100,1300],["1300–1500",0,1300,1500],["1500–1700",0,1500,1700],["1700–1900",0,1700,1900],["1900+",0,1900,9999]];
  const buckets = [
    { label: "<1100", lo: 0, hi: 1100 },
    { label: "1100", lo: 1100, hi: 1300 },
    { label: "1300", lo: 1300, hi: 1500 },
    { label: "1500", lo: 1500, hi: 1700 },
    { label: "1700", lo: 1700, hi: 1900 },
    { label: "1900+", lo: 1900, hi: 9999 },
  ];
  return buckets.map(b => ({ ...b, n: students.filter(s => s.elo >= b.lo && s.elo < b.hi).length }));
};

/* weekly activity series (attempts per day) */
const ACTIVITY = [
  { d: "Lun", v: 142 }, { d: "Mar", v: 168 }, { d: "Mié", v: 131 },
  { d: "Jue", v: 196 }, { d: "Vie", v: 213 }, { d: "Sáb", v: 88 }, { d: "Dom", v: 64 },
];

Object.assign(window, {
  TOPICS, topicById, RANKS, rankFor, AVAS, initials, avaFor, accColor,
  STUDENTS, fmtMiles, computeStats, topicCounts, eloBuckets, ACTIVITY,
});
