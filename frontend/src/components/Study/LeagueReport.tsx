import { useTranslation } from "react-i18next";
import "./LeagueReport.css";
import type { LeagueStats } from "../../api/student";
import { MathText } from "../Math/MathContent";
import { QuestionImage } from "../Question/QuestionImage";

/**
 * Spec 007 FR-070: the League's answers, for study — per topic, weakest first, and the items
 * missed most with their statement (D5: through MathText). Marked by the League's gold, beside
 * the practice report, never inside it. The same component on the student's statistics and in the
 * teacher's student panel; `audience` only changes who the copy talks to.
 */
export function LeagueReport({
  stats,
  audience,
  limit = 8,
}: {
  stats: LeagueStats;
  audience: "student" | "teacher";
  limit?: number;
}) {
  const { t } = useTranslation();
  const missedTitle = audience === "student" ? t("league.stats.missedTitle") : t("league.stats.missedTitleTeacher");
  return (
    <div className="lr">
      <ul className="lr-list" aria-label={t("league.stats.topicsLabel")}>
        {stats.topics.slice(0, limit).map((r) => {
          const pct = Math.round(r.share_correct * 100);
          const tone = pct < 50 ? "var(--color-wrong)" : pct < 75 ? "var(--color-partial)" : "var(--color-correct)";
          return (
            <li key={`${r.course_id}|${r.topic}`} className="lr-row">
              <div className="lr-head">
                <span className="lr-name">{r.topic}</span>
                <span className="lr-count">{t("league.stats.correctOf", { correct: r.correct, answers: r.answers })}</span>
              </div>
              <div className="lr-meta">{r.course_name}</div>
              <div className="lr-bar" role="presentation">
                <span style={{ width: `${pct}%`, background: tone }} />
              </div>
            </li>
          );
        })}
      </ul>
      {stats.items.length > 0 && (
        <>
          <h4 className="lr-sub">{missedTitle}</h4>
          <ul className="lr-items" aria-label={missedTitle}>
            {stats.items.map((i) => (
              <li key={i.item_id} className="lr-item">
                <div className="lr-stmt">
                  <MathText text={i.content} />
                </div>
                <QuestionImage imageUrl={i.image_url} className="lr-img" />
                <div className="lr-foot">
                  <span className="lr-meta">
                    {audience === "teacher" && <code>{i.item_id}</code>} {i.topic}
                  </span>
                  <span className="lr-miss">{t("league.stats.missedOf", { missed: i.missed, answers: i.answers })}</span>
                </div>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
