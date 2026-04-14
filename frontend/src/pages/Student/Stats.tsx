/**
 * pages/Student/Stats.tsx
 * ========================
 * Estadísticas del estudiante: ELO global, por tópico, racha, historial y logros.
 */

import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { studentApi } from "../../api/student";
import { ELOChart } from "../../components/ELO/ELOChart";
import { RankBadge } from "../../components/ELO/RankBadge";
import { TopicRadarChart } from "../../components/ELO/TopicRadarChart";
import { ActivityHeatmap } from "../../components/ui/ActivityHeatmap";
import { apiClient } from "../../api/client";

interface Achievement {
  badge_id: string;
  label: string;
  icon: string;
  desc: string;
  earned_at: string;
}

interface RankEntry {
  user_id: number;
  username: string;
  global_elo: number;
  total_attempts: number;
  rank_pos: number;
}

export function Stats() {
  const { data: stats, isLoading, isError } = useQuery({
    queryKey: ["student-stats"],
    queryFn: () => studentApi.stats(),
    retry: 2,
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
      apiClient.get<{ ranking: RankEntry[]; my_rank: number | null }>("/api/student/group-ranking"),
    retry: 1,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-slate-400">Cargando estadísticas...</div>
      </div>
    );
  }

  if (isError || !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-slate-400 mb-2">No se pudieron cargar las estadísticas.</p>
          <p className="text-slate-500 text-sm">El servidor puede estar iniciando. Intenta recargar la página.</p>
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

  const earnedIds = new Set((achievementsData?.achievements ?? []).map((a) => a.badge_id));

  return (
    <div className="max-w-2xl mx-auto py-6 px-4 space-y-6">
      <h2 className="text-xl font-bold text-white">Mis Estadísticas</h2>

      {/* Resumen top */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700 text-center">
          <div className="text-2xl font-bold text-white">{Math.round(stats.global_elo)}</div>
          <div className="text-xs text-slate-400 mt-1">ELO Global</div>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700 text-center">
          <div className="text-2xl font-bold text-amber-400">{stats.study_streak}</div>
          <div className="text-xs text-slate-400 mt-1">🔥 Racha</div>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700 text-center">
          <div className="text-2xl font-bold text-violet-400">{stats.total_attempts}</div>
          <div className="text-xs text-slate-400 mt-1">Intentos</div>
        </div>
      </div>

      {/* Rango */}
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <p className="text-xs text-slate-400 mb-2">Rango actual</p>
        <RankBadge elo={stats.global_elo} rankLabel={stats.rank_label ?? "Aspirante"} />
      </div>

      {/* Gráfico de evolución ELO */}
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <ELOChart data={chartData} title="Evolución ELO (últimos 20 intentos)" />
      </div>

      {/* Heatmap de actividad */}
      {activityData && (
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <h3 className="text-sm font-medium text-slate-400 mb-3">Actividad semanal</h3>
          <ActivityHeatmap data={activityData.activity} />
        </div>
      )}

      {/* Radar chart de tópicos */}
      {stats.topic_elos.length >= 3 && (
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <h3 className="text-sm font-medium text-slate-400 mb-1">Rendimiento por tópico</h3>
          <p className="text-xs text-slate-600 mb-2">Top 8 tópicos más practicados</p>
          <TopicRadarChart topics={stats.topic_elos} />
        </div>
      )}

      {/* ELO por tópico (barras) */}
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-400 mb-3">ELO por tópico</h3>
        {stats.topic_elos.length === 0 ? (
          <p className="text-slate-500 text-sm">Sin datos de tópicos aún.</p>
        ) : (
          <div className="space-y-2">
            {stats.topic_elos.map((t) => (
              <div key={t.topic} className="flex items-center gap-3">
                <span className="text-xs text-slate-400 w-40 truncate" title={t.topic}>
                  {t.topic}
                </span>
                <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-violet-500 rounded-full"
                    style={{ width: `${Math.min(100, ((t.rating - 400) / 2600) * 100)}%` }}
                  />
                </div>
                <span className="text-xs text-slate-300 w-12 text-right">
                  {Math.round(t.rating)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Ranking del grupo */}
      {rankingData && rankingData.ranking.length > 0 && (
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-slate-400">Ranking del grupo</h3>
            {rankingData.my_rank && (
              <span className="text-xs text-violet-400 font-medium">
                Tu posición: #{rankingData.my_rank}
              </span>
            )}
          </div>
          <div className="space-y-1.5">
            {rankingData.ranking.slice(0, 10).map((r) => {
              const isMe = r.user_id === stats.user_id;
              const medal =
                r.rank_pos === 1 ? "🥇" : r.rank_pos === 2 ? "🥈" : r.rank_pos === 3 ? "🥉" : null;
              return (
                <div
                  key={r.user_id}
                  className={[
                    "flex items-center gap-3 rounded-lg px-3 py-2",
                    isMe
                      ? "bg-violet-900/40 border border-violet-700"
                      : "bg-slate-900/40 border border-slate-700/50",
                  ].join(" ")}
                >
                  <span className="text-xs text-slate-500 w-5 text-center">
                    {medal ?? `#${r.rank_pos}`}
                  </span>
                  <span className={`text-xs flex-1 ${isMe ? "text-violet-300 font-medium" : "text-slate-300"}`}>
                    {r.username} {isMe && "(tú)"}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">
                    {Math.round(r.global_elo)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Logros / Badges — animados con Framer Motion */}
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-400 mb-3">
          Logros{" "}
          {achievementsData &&
            `(${achievementsData.achievements.length}/${achievementsData.catalog.length})`}
        </h3>
        {achievementsData ? (
          <div className="grid grid-cols-2 gap-2">
            <AnimatePresence>
              {achievementsData.catalog.map((badge, i) => {
                const earned = earnedIds.has(badge.badge_id);
                const earnedAt = achievementsData.achievements.find(
                  (a) => a.badge_id === badge.badge_id,
                )?.earned_at;
                return (
                  <motion.div
                    key={badge.badge_id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: earned ? 1 : 0.4, scale: 1 }}
                    transition={{ delay: i * 0.04, duration: 0.3 }}
                    className={[
                      "flex items-center gap-3 rounded-lg px-3 py-2 border transition-colors",
                      earned
                        ? "border-violet-600 bg-violet-900/30"
                        : "border-slate-700 bg-slate-900/30",
                    ].join(" ")}
                    title={badge.desc}
                  >
                    <span className="text-xl">{badge.icon}</span>
                    <div>
                      <p className="text-xs font-medium text-slate-200">{badge.label}</p>
                      {earned && earnedAt && (
                        <p className="text-xs text-slate-500">
                          {new Date(earnedAt).toLocaleDateString("es-CO")}
                        </p>
                      )}
                      {!earned && (
                        <p className="text-xs text-slate-600">{badge.desc}</p>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        ) : (
          <p className="text-slate-500 text-sm">Cargando logros…</p>
        )}
      </div>
    </div>
  );
}
