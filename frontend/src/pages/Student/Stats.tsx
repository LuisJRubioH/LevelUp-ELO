/**
 * pages/Student/Stats.tsx
 * ========================
 * Estadísticas del estudiante: ELO global, por tópico, racha, historial y logros.
 */

import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import { studentApi } from "../../api/student";
import type { ExamSession, GroupRanking } from "../../api/student";
import { ELOChart } from "../../components/ELO/ELOChart";
import { StatsSkeleton } from "../../components/ui/Skeleton";
import { RankBadge } from "../../components/ELO/RankBadge";
import { TopicRadarChart } from "../../components/ELO/TopicRadarChart";
import { ActivityHeatmap } from "../../components/ui/ActivityHeatmap";
import { PageHeader } from "../../components/ui/PageHeader";
import { apiClient } from "../../api/client";
import "./StudentContent.css";

interface Achievement {
  badge_id: string;
  label: string;
  icon: string;
  desc: string;
  earned_at: string;
}


export function Stats() {
  const { t, i18n } = useTranslation();
  const { data: stats, isLoading, isError, failureCount } = useQuery({
    queryKey: ["student-stats"],
    queryFn: () => studentApi.stats(),
  });

  const { data: history } = useQuery({
    queryKey: ["student-history"],
    queryFn: () => studentApi.history(),
  });

  const { data: achievementsData } = useQuery({
    queryKey: ["student-achievements"],
    queryFn: () =>
      apiClient.get<{ achievements: Achievement[]; catalog: Achievement[] }>("/api/student/achievements"),
  });

  const { data: activityData } = useQuery({
    queryKey: ["student-activity"],
    queryFn: () => apiClient.get<{ activity: Record<string, number> }>("/api/student/activity"),
  });

  const { data: rankingData } = useQuery({
    queryKey: ["student-group-ranking"],
    queryFn: () =>
      apiClient.get<GroupRanking>("/api/student/group-ranking"),
    retry: 1,
  });

  const { data: examHistory = [] } = useQuery<ExamSession[]>({
    queryKey: ["examHistory"],
    queryFn: () => studentApi.examHistory(),
  });

  if (isLoading) {
    return (
      <div>
        {failureCount > 0 && (
          <div
            role="status"
            aria-live="polite"
            className="max-w-3xl mx-auto mt-4 mb-2 px-4"
          >
            <div className="text-xs text-amber-400/90 bg-amber-500/10 border border-amber-500/30 rounded-lg px-3 py-2">
              <span className="inline-block w-2 h-2 mr-2 bg-amber-400 rounded-full animate-pulse align-middle" />
              {t("stats.serverWaking", { current: failureCount + 1 })}
            </div>
          </div>
        )}
        <StatsSkeleton />
      </div>
    );
  }

  if (isError || !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center max-w-sm">
          <p className="sp-dim mb-2">{t("stats.error")}</p>
          <p className="sp-mute text-sm mb-4">{t("stats.errorHint")}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-violet-600 hover:bg-violet-500 text-white text-sm px-4 py-2 rounded-lg transition-colors"
          >
            {t("stats.reload")}
          </button>
        </div>
      </div>
    );
  }

  // Preparar datos del gráfico ELO (los más recientes al final — API retorna DESC)
  const chartData = ((history?.attempts ?? []) as Record<string, unknown>[])
    .slice(0, 20)
    .reverse()
    .map((a, i) => {
      const ts = typeof a["timestamp"] === "string" ? a["timestamp"] : null;
      const label = ts
        ? `${ts.slice(8, 10)}/${ts.slice(5, 7)}`
        : `#${i + 1}`;
      return {
        label,
        elo: typeof a["elo_after"] === "number" ? a["elo_after"] : 1000,
      };
    });

  const topicElos = Array.isArray(stats.topic_elos) ? stats.topic_elos : [];
  const ranking = Array.isArray(rankingData?.ranking) ? rankingData.ranking : [];
  const earnedAchievements = Array.isArray(achievementsData?.achievements)
    ? achievementsData.achievements
    : [];
  const achievementCatalog = Array.isArray(achievementsData?.catalog)
    ? achievementsData.catalog
    : [];
  const safeExamHistory = Array.isArray(examHistory) ? examHistory : [];
  const earnedIds = new Set(earnedAchievements.map((a) => a.badge_id));

  return (
    <div className="sp-page">
      <PageHeader eyebrow={t("stats.eyebrow")} title={t("stats.title")} subtitle={t("stats.intro")} />

      {/* Resumen top */}
      <div className="sp-stat-grid">
        <div className="sp-card sp-stat">
          <div className="v">{stats.display_rating ?? t("rating.pending")}</div>
          <div className="l">{t("stats.globalElo")}</div>
        </div>
        <div className="sp-card sp-stat">
          <div className="v gold">{stats.study_streak}</div>
          <div className="l">{t("stats.streakFire")}</div>
        </div>
        <div className="sp-card sp-stat">
          <div className="v accent">{stats.total_attempts}</div>
          <div className="l">{t("stats.attempts")}</div>
        </div>
      </div>

      {/* Rango */}
      <div className="sp-card">
        <p className="sp-mute text-xs mb-2">{t("stats.currentRank")}</p>
        <RankBadge displayRating={stats.display_rating ?? null} rankLabel={stats.rank_label} />
      </div>

      {/* Por curso: el valor y el rango que da la API; grados anteriores como historial */}
      {(stats.course_ratings ?? []).length > 0 && (
        <div className="sp-card">
          <h3>{t("rating.byCourse")}</h3>
          <div className="space-y-1.5">
            {(stats.course_ratings ?? []).map((c) => (
              <div key={c.course_id} className="sp-row">
                <span className="nm">
                  {c.course_name}
                  {!c.current_context && <span className="sp-mute text-xs"> · {t("rating.history")}</span>}
                </span>
                <span className="val">
                  {c.display_rating ?? t("rating.pending")}
                  {c.rank_label && <span className="sp-mute text-xs"> · {c.rank_label}</span>}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Gráfico de evolución ELO */}
      <div className="sp-card">
        <ELOChart data={chartData} title={t("stats.eloEvolution")} />
      </div>

      {/* Heatmap de actividad */}
      {activityData && (
        <div className="sp-card">
          <h3>{t("stats.weeklyActivity")}</h3>
          <ActivityHeatmap data={activityData.activity ?? {}} />
        </div>
      )}

      {/* Radar chart de tópicos */}
      {topicElos.length >= 3 && (
        <div className="sp-card">
          <h3>{t("stats.topicPerformance")}</h3>
          <p className="sp-card-hint">{t("stats.topicPerformanceHint")}</p>
          <TopicRadarChart topics={topicElos} />
        </div>
      )}

      {/* ELO por tópico (barras) */}
      <div className="sp-card">
        <h3>{t("stats.topicElo")}</h3>
        {topicElos.length === 0 ? (
          <p className="sp-empty-text">{t("stats.topicEloEmpty")}</p>
        ) : (
          <div className="space-y-2">
            {topicElos.map((t) => (
              <div key={t.topic} className="flex items-center gap-3">
                <span className="sp-dim text-xs w-40 truncate" title={t.topic}>
                  {t.topic}
                </span>
                <div className="sp-bar">
                  <i style={{ width: `${Math.min(100, ((t.rating - 400) / 2600) * 100)}%` }} />
                </div>
                <span className="sp-dim text-xs w-12 text-right">
                  {Math.round(t.rating)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Ranking del grupo */}
      {rankingData && ranking.length > 0 && (
        <div className="sp-card">
          <div className="flex items-center justify-between mb-3">
            <h3 style={{ margin: 0 }}>
              {t("stats.groupRanking")}
              {rankingData.basis && (
                <span className="sp-mute text-xs">
                  {" · "}
                  {rankingData.basis.course_name ?? t("rating.basisOverall")}
                </span>
              )}
            </h3>
            {rankingData.my_rank && (
              <span className="text-xs font-medium" style={{ color: "var(--accent)" }}>
                {t("stats.yourPosition")}: #{rankingData.my_rank}
              </span>
            )}
          </div>
          <div className="space-y-1.5">
            {ranking.slice(0, 10).map((r) => {
              const isMe = r.user_id === stats.user_id;
              // Competition rank from the API: ties share it; pending rows have none.
              const medal =
                r.rank === 1 ? "🥇" : r.rank === 2 ? "🥈" : r.rank === 3 ? "🥉" : null;
              return (
                <div key={r.user_id} className={`sp-row${isMe ? " me" : ""}`}>
                  <span className="pos">{medal ?? (r.rank === null ? "—" : `#${r.rank}`)}</span>
                  <span className={`nm${isMe ? " me" : ""}`}>
                    {r.username} {isMe && t("stats.you")}
                  </span>
                  <span className="val">{r.rating ?? t("rating.pending")}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Logros / Badges — animados con Framer Motion */}
      <div className="sp-card">
        <h3>
          {t("stats.achievements")}{" "}
          {achievementsData && `(${earnedAchievements.length}/${achievementCatalog.length})`}
        </h3>
        {achievementsData ? (
          <div className="grid grid-cols-2 gap-2">
            <AnimatePresence>
              {achievementCatalog.map((badge, i) => {
                const earned = earnedIds.has(badge.badge_id);
                const earnedAt = earnedAchievements.find(
                  (a) => a.badge_id === badge.badge_id,
                )?.earned_at;
                return (
                  <motion.div
                    key={badge.badge_id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: earned ? 1 : 0.4, scale: 1 }}
                    transition={{ delay: i * 0.04, duration: 0.3 }}
                    className={`sp-badge${earned ? " earned" : ""}`}
                    title={badge.desc}
                  >
                    <span className="ic">{badge.icon}</span>
                    <div>
                      <p className="lbl">{badge.label}</p>
                      {earned && earnedAt && (
                        <p className="sub">
                          {new Date(earnedAt).toLocaleDateString(
                            i18n.language === "en" ? "en-US" : "es-CO",
                          )}
                        </p>
                      )}
                      {!earned && <p className="sub">{badge.desc}</p>}
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        ) : (
          <p className="sp-empty-text">{t("stats.achievementsLoading")}</p>
        )}
      </div>

      {/* Historial de exámenes */}
      <div className="sp-card">
        <div className="flex items-baseline justify-between mb-3">
          <h3 style={{ margin: 0 }}>{t("stats.examHistory")}</h3>
          <p className="sp-mute text-[10px] italic">{t("stats.examNoElo")}</p>
        </div>
        {safeExamHistory.length === 0 ? (
          <p className="sp-empty-text">{t("stats.noExams")}</p>
        ) : (
          <div className="space-y-2">
            {safeExamHistory.map((session) => {
              const scoreColor =
                session.score_pct >= 70
                  ? "text-emerald-400"
                  : session.score_pct >= 50
                  ? "text-amber-400"
                  : "text-red-400";
              return (
                <div key={session.id} className="sp-row">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium truncate" style={{ color: "var(--text)" }}>
                      {session.course_name || session.course_id}
                    </p>
                    <p className="sp-mute text-[10px]">{session.created_at}</p>
                  </div>
                  <span className={`text-sm font-semibold ${scoreColor} tabular-nums`}>
                    {session.correct_count}/{session.n_questions}
                    <span className="text-xs font-normal ml-1">({session.score_pct}%)</span>
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
