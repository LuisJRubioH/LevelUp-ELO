/**
 * components/ELO/rankColors.ts
 * ============================
 * The only colour map keyed by the 16 rank labels (spec 001). Presentation only: the labels and
 * their thresholds come from the API (rank_label, GET /api/meta/ranks).
 */

/** Presentation only: one colour per label of the single 16-level scale (GET /api/meta/ranks). */
export const RANK_COLORS: Record<string, string> = {
  "Leyenda Suprema": "#fde047",
  Leyenda: "#facc15",
  "Gran Maestro": "#fb923c",
  Maestro: "#c084fc",
  "Diamante I": "#67e8f9",
  "Diamante II": "#22d3ee",
  "Platino I": "#5eead4",
  "Platino II": "#2dd4bf",
  "Oro I": "#fcd34d",
  "Oro II": "#fbbf24",
  "Plata I": "#cbd5e1",
  "Plata II": "#94a3b8",
  "Bronce I": "#fdba74",
  "Bronce II": "#f97316",
  Hierro: "#64748b",
  Aspirante: "#475569",
};

export const rankColor = (label: string | null | undefined) =>
  (label && RANK_COLORS[label]) || "#94a3b8";
