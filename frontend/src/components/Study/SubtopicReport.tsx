import { useTranslation } from "react-i18next";
import "./SubtopicReport.css";
import type { SubtopicResult } from "../../api/student";

/**
 * Spec 008 FR-042: a student's results per subtopic, across courses, weakest first — for study,
 * never a rating. The bar's length is the share correct; its colour says how far from solid.
 */
export function SubtopicReport({ rows, limit = 8 }: { rows: SubtopicResult[]; limit?: number }) {
  const { t } = useTranslation();
  if (rows.length === 0) return <p className="sr-empty">{t("subtopics.empty")}</p>;
  return (
    <ul className="sr-list" aria-label={t("subtopics.title")}>
      {rows.slice(0, limit).map((r) => {
        const pct = Math.round(r.share_correct * 100);
        const tone = pct < 50 ? "var(--color-wrong)" : pct < 75 ? "var(--color-warn)" : "var(--color-correct)";
        return (
          <li key={`${r.course_id}|${r.topic}|${r.subtopic}`} className="sr-row">
            <div className="sr-head">
              <span className="sr-name">{r.subtopic}</span>
              <span className="sr-count">
                {t("subtopics.correctOf", { correct: r.correct, attempts: r.attempts })}
              </span>
            </div>
            <div className="sr-meta">
              {r.topic} · {r.course_name}
            </div>
            <div className="sr-bar" role="presentation">
              <span style={{ width: `${pct}%`, background: tone }} />
            </div>
          </li>
        );
      })}
    </ul>
  );
}
