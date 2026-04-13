/**
 * pages/Student/Stats.tsx
 * ========================
 * Estadísticas del estudiante: ELO global, por tópico, racha, historial y logros.
 */

import { useQuery } from "@tanstack/react-query";
import { studentApi } from "../../api/student";
import { ELOChart } from "../../components/ELO/ELOChart";
import { RankBadge } from "../../components/ELO/RankBadge";
import { apiClient } from "../../api/client";

interface Achievement {
  badge_id: string;
  label: string;
  icon: string;
  desc: string;
  earned_at: string;
}

export function Stats() {
  const { data: stats, isLoading } = useQuery({
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
      apiClient.get<{ achievements: Achievement[]; catalog: Achievement[] }>("/student/achievements"),
  });

  if (isLoading || !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-slate-400">Cargando estadísticas...</div>
      </div>
    );
  }

  // Preparar datos del gráfico ELO desde historial de intentos
  const chartData = ((history?.attempts ?? []) as Record<string, unknown>[])
    .slice(-20)
    .map((a, i) => ({
      label: `#${i + 1}`,
      elo: typeof a["elo_after"] === "number" ? a["elo_after"] : 1000,
    }));

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

      {/* ELO por tópico */}
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

      {/* Logros / Badges */}
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-400 mb-3">
          Logros {achievementsData && `(${achievementsData.achievements.length}/${achievementsData.catalog.length})`}
        </h3>
        {achievementsData ? (
          <div className="grid grid-cols-2 gap-2">
            {achievementsData.catalog.map((badge) => {
              const earned = achievementsData.achievements.find(
                (a) => a.badge_id === badge.badge_id
              );
              return (
                <div
                  key={badge.badge_id}
                  className={[
                    "flex items-center gap-3 rounded-lg px-3 py-2 border transition-all",
                    earned
                      ? "border-violet-600 bg-violet-900/30"
                      : "border-slate-700 bg-slate-900/30 opacity-40",
                  ].join(" ")}
                  title={badge.desc}
                >
                  <span className="text-xl">{badge.icon}</span>
                  <div>
                    <p className="text-xs font-medium text-slate-200">{badge.label}</p>
                    {earned && (
                      <p className="text-xs text-slate-500">
                        {new Date(earned.earned_at).toLocaleDateString("es-CO")}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-slate-500 text-sm">Cargando logros…</p>
        )}
      </div>
    </div>
  );
}
