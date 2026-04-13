/**
 * components/ELO/RankBadge.tsx
 * =============================
 * Badge del rango actual del estudiante (16 niveles).
 * El delta de ELO se muestra con animación +/-.
 */

import { useEffect, useState } from "react";

interface RankBadgeProps {
  elo: number;
  rankLabel: string;
  deltaElo?: number; // mostrar delta tras una respuesta
}

const rankColors: Record<string, string> = {
  "Leyenda Suprema": "text-yellow-300",
  Leyenda: "text-yellow-400",
  "Gran Maestro": "text-orange-400",
  Maestro: "text-purple-400",
  "Diamante I": "text-cyan-300",
  "Diamante II": "text-cyan-400",
  "Platino I": "text-teal-300",
  "Platino II": "text-teal-400",
  "Oro I": "text-amber-300",
  "Oro II": "text-amber-400",
  "Plata I": "text-slate-300",
  "Plata II": "text-slate-400",
  "Bronce I": "text-orange-300",
  "Bronce II": "text-orange-500",
  Hierro: "text-slate-500",
  Aspirante: "text-slate-600",
};

export function RankBadge({ elo, rankLabel, deltaElo }: RankBadgeProps) {
  const [showDelta, setShowDelta] = useState(false);

  useEffect(() => {
    if (deltaElo !== undefined && deltaElo !== 0) {
      setShowDelta(true);
      const t = setTimeout(() => setShowDelta(false), 3000);
      return () => clearTimeout(t);
    }
  }, [deltaElo]);

  const color = rankColors[rankLabel] ?? "text-slate-400";

  return (
    <div className="flex items-center gap-2">
      <div className="text-center">
        <div className={`text-sm font-bold ${color}`}>{rankLabel}</div>
        <div className="text-xs text-slate-500">ELO {Math.round(elo)}</div>
      </div>

      {showDelta && deltaElo !== undefined && (
        <span
          className={`text-sm font-bold animate-bounce ${deltaElo >= 0 ? "text-green-400" : "text-red-400"}`}
        >
          {deltaElo >= 0 ? "+" : ""}
          {deltaElo.toFixed(1)}
        </span>
      )}
    </div>
  );
}
