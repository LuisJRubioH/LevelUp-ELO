/**
 * components/ELO/RankBadge.tsx
 * =============================
 * The student's rank and rating exactly as the API returns them (spec 001, FR-028j): the number
 * is the backend's `display_rating` and the label its `rank_label`; screens never round a rating
 * nor compute a rank. While the diagnostic is pending both are null and the badge says so.
 * Colours: rankColors.ts, the only colour map keyed by the 16 rank labels.
 */

import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { rankColor } from "./rankColors";


/** A rank pill for teacher screens: the API's label, or "pending" with no colour of a rank. */
export function RankPill({ label, style }: { label: string | null | undefined; style?: React.CSSProperties }) {
  const { t } = useTranslation();
  const color = rankColor(label);
  return (
    <span className="rank-badge" style={{ color, background: `${color}29`, ...style }}>
      {label ?? t("rating.pending")}
    </span>
  );
}

interface RankBadgeProps {
  displayRating: number | null; // the API's display_rating: rendered as given
  rankLabel: string | null;
  deltaElo?: number; // mostrar delta tras una respuesta
}

export function RankBadge({ displayRating, rankLabel, deltaElo }: RankBadgeProps) {
  const { t } = useTranslation();
  const [showDelta, setShowDelta] = useState(false);

  useEffect(() => {
    if (deltaElo !== undefined && deltaElo !== 0) {
      setShowDelta(true);
      const timer = setTimeout(() => setShowDelta(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [deltaElo]);

  return (
    <div className="flex items-center gap-2">
      <div className="text-center">
        <div className="text-sm font-bold" style={{ color: rankColor(rankLabel) }}>
          {rankLabel ?? t("rating.pending")}
        </div>
        {displayRating !== null && <div className="text-xs text-slate-500">ELO {displayRating}</div>}
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
