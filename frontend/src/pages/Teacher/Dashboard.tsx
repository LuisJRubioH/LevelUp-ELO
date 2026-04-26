/**
 * pages/Teacher/Dashboard.tsx
 * ============================
 * Panel principal del docente: resumen de grupos y tabla de estudiantes.
 */

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { teacherApi } from "../../api/teacher";
import { ELOChart } from "../../components/ELO/ELOChart";
import { useSettingsStore } from "../../stores/settingsStore";
import { DashboardSkeleton, Skeleton } from "../../components/ui/Skeleton";

function EloBar({ elo }: { elo: number }) {
  const pct = Math.min(100, Math.round((elo / 2500) * 100));
  const color =
    elo >= 1800 ? "bg-yellow-400" : elo >= 1400 ? "bg-violet-500" : elo >= 1000 ? "bg-blue-500" : "bg-slate-500";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-slate-700 rounded-full h-1.5">
        <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-slate-300 w-12 text-right">{Math.round(elo)}</span>
    </div>
  );
}

function StatCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
      <div className="text-2xl font-bold text-slate-100">{value}</div>
      <div className="text-sm text-slate-400 mt-0.5">{label}</div>
      {sub && <div className="text-xs text-slate-600 mt-1">{sub}</div>}
    </div>
  );
}


type DetailTab = "elo" | "topics" | "katia" | "ai";

function StudentDetailPanel({
  studentId,
  onClose,
}: {
  studentId: number;
  onClose: () => void;
}) {
  const [tab, setTab] = useState<DetailTab>("elo");
  const [aiResult, setAiResult] = useState<string | null>(null);
  const { apiKey, provider } = useSettingsStore();

  const { data, isLoading } = useQuery({
    queryKey: ["teacher-student", studentId],
    queryFn: () => teacherApi.studentReport(studentId),
  });

  const { data: eloHistory } = useQuery({
    queryKey: ["teacher-student-elo", studentId],
    queryFn: () => teacherApi.studentEloHistory(studentId),
    enabled: tab === "elo",
  });

  const { data: katiaHistory } = useQuery({
    queryKey: ["teacher-student-katia", studentId],
    queryFn: () => teacherApi.studentKatiaHistory(studentId),
    enabled: tab === "katia",
  });

  const aiMutation = useMutation({
    mutationFn: () => teacherApi.studentAiAnalysis(studentId, apiKey || undefined, provider),
    onSuccess: (res) => setAiResult(res.analysis),
  });

  // Preparar datos ELO chart
  const chartData = (eloHistory?.attempts ?? []).map((a, i) => {
    const ts = typeof a["timestamp"] === "string" ? a["timestamp"] : null;
    return {
      label: ts ? `${ts.slice(8, 10)}/${ts.slice(5, 7)}` : `#${i + 1}`,
      elo: typeof a["elo_after"] === "number" ? a["elo_after"] : 1000,
    };
  });

  const tabs: { id: DetailTab; label: string }[] = [
    { id: "elo", label: "📈 ELO" },
    { id: "topics", label: "📚 Tópicos" },
    { id: "katia", label: "🐱 KatIA" },
    { id: "ai", label: "🤖 Análisis IA" },
  ];

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="font-semibold text-slate-100">Detalle del estudiante</h4>
        <button onClick={onClose} className="text-slate-500 hover:text-slate-300 text-sm">
          ✕ Cerrar
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-700 pb-2">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={[
              "text-xs px-2.5 py-1 rounded-lg transition-colors",
              tab === t.id
                ? "bg-violet-600/30 text-violet-300"
                : "text-slate-500 hover:text-slate-300",
            ].join(" ")}
          >
            {t.label}
          </button>
        ))}
      </div>

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-4 w-full" />
          ))}
        </div>
      )}

      {/* Tab: ELO temporal */}
      {tab === "elo" && (
        <ELOChart
          data={chartData}
          title={`Evolución ELO (últimos ${chartData.length} intentos)`}
        />
      )}

      {/* Tab: Tópicos */}
      {tab === "topics" && data && (
        <div className="space-y-2 text-sm">
          <p className="text-slate-300 text-xs">
            ELO global:{" "}
            <span className="font-bold text-slate-100">{Math.round((data.global_elo as number) ?? 0)}</span>
          </p>
          {(() => {
            const breakdown = data.topic_breakdown as Record<string, Record<string, number>> | undefined;
            if (!breakdown || Object.keys(breakdown).length === 0)
              return <p className="text-slate-500 text-xs">Sin datos de tópicos.</p>;
            return (
              <div className="grid grid-cols-2 gap-1 max-h-48 overflow-y-auto">
                {Object.entries(breakdown).map(([topic, info]) => (
                  <div key={topic} className="bg-slate-900 rounded px-2 py-1">
                    <div className="text-xs text-slate-400 truncate" title={topic}>{topic}</div>
                    <div className="text-slate-100 text-xs font-medium">
                      {Math.round(info.rating ?? 0)}
                    </div>
                  </div>
                ))}
              </div>
            );
          })()}
        </div>
      )}

      {/* Tab: KatIA */}
      {tab === "katia" && (
        <div className="max-h-64 overflow-y-auto space-y-2">
          {!katiaHistory || katiaHistory.interactions.length === 0 ? (
            <p className="text-slate-500 text-sm">Sin interacciones con KatIA registradas.</p>
          ) : (
            katiaHistory.interactions.slice(0, 20).map((k, i) => (
              <div key={i} className="bg-slate-900 rounded-lg p-2 space-y-0.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-violet-400">{String(k["item_topic"] ?? "—")}</span>
                  <span className="text-xs text-slate-600">
                    {typeof k["created_at"] === "string" ? k["created_at"].slice(0, 10) : ""}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  👤 {String(k["student_message"] ?? "").slice(0, 80)}
                </p>
                <p className="text-xs text-slate-500">
                  🐱 {String(k["katia_response"] ?? "").slice(0, 80)}
                </p>
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab: Análisis IA */}
      {tab === "ai" && (
        <div className="space-y-3">
          {!aiResult && (
            <>
              {!apiKey && (
                <p className="text-xs text-slate-500">
                  Configura una API key en el panel lateral para usar el análisis IA.
                </p>
              )}
              <button
                onClick={() => aiMutation.mutate()}
                disabled={aiMutation.isPending || !apiKey}
                className="w-full py-2 rounded-lg bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-slate-100 text-sm transition-colors"
              >
                {aiMutation.isPending ? "Generando análisis…" : "🤖 Generar análisis pedagógico"}
              </button>
            </>
          )}
          {aiMutation.isError && (
            <p className="text-xs text-red-400">Error al generar el análisis.</p>
          )}
          {aiResult && (
            <div className="bg-slate-900 rounded-xl p-3 text-xs text-slate-300 whitespace-pre-wrap leading-relaxed max-h-64 overflow-y-auto">
              {aiResult}
            </div>
          )}
          {aiResult && (
            <button
              onClick={() => { setAiResult(null); aiMutation.reset(); }}
              className="text-xs text-slate-500 hover:text-slate-400"
            >
              Regenerar análisis
            </button>
          )}
        </div>
      )}
    </div>
  );
}

// ── Tab de métricas de uso ─────────────────────────────────────────────────

function MetricsView() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["teacher-metrics"],
    queryFn: teacherApi.metrics,
    staleTime: 120_000,
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-20 w-full rounded-xl" />
        ))}
      </div>
    );
  }

  if (error || !data) {
    return <p className="text-slate-500 text-sm py-4">No se pudieron cargar las métricas.</p>;
  }

  const peakHour = data.hourly_distribution.reduce(
    (max, h) => (h.count > max.count ? h : max),
    { hour: 0, count: 0 },
  );

  return (
    <div className="space-y-6">
      {/* KPIs principales */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard
          label="Total intentos"
          value={data.total_attempts.toLocaleString()}
        />
        <StatCard
          label="Tiempo promedio"
          value={`${data.avg_time_seconds}s`}
          sub="por pregunta (válidos)"
        />
        <StatCard
          label="Tasa de abandono"
          value={`${(data.abandonment_rate * 100).toFixed(1)}%`}
          sub="fuera de 3–600s"
        />
        <StatCard
          label="Hora pico"
          value={`${peakHour.hour}:00`}
          sub={`${peakHour.count} intentos`}
        />
      </div>

      {/* Actividad diaria (últimos 30 días) */}
      {data.daily_attempts.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
          <h4 className="text-sm font-semibold text-slate-300 mb-3">
            Actividad diaria — últimos 30 días
          </h4>
          <ResponsiveContainer width="100%" height={120}>
            <BarChart data={data.daily_attempts} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
              <XAxis
                dataKey="date"
                tick={{ fontSize: 9, fill: "#64748b" }}
                tickFormatter={(v: string) => v.slice(5)}
                interval="preserveStartEnd"
              />
              <YAxis tick={{ fontSize: 9, fill: "#64748b" }} allowDecimals={false} />
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#94a3b8" }}
                itemStyle={{ color: "#a78bfa" }}
              />
              <Bar dataKey="count" name="Intentos" fill="#6c63ff" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Top temas */}
      {data.topic_stats.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-700">
            <h4 className="text-sm font-semibold text-slate-300">Temas más practicados</h4>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-xs text-slate-500 border-b border-slate-700">
                  <th className="px-4 py-2 text-left">Tema</th>
                  <th className="px-4 py-2 text-right">Intentos</th>
                  <th className="px-4 py-2 text-right">Acierto</th>
                  <th className="px-4 py-2 text-right hidden sm:table-cell">Tiempo prom.</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {data.topic_stats.map((t) => (
                  <tr key={t.topic} className="hover:bg-slate-700/30 transition-colors">
                    <td className="px-4 py-2.5 text-sm text-slate-300 max-w-[160px] truncate">
                      {t.topic}
                    </td>
                    <td className="px-4 py-2.5 text-sm text-slate-300 text-right tabular-nums">
                      {t.attempts}
                    </td>
                    <td className="px-4 py-2.5 text-right">
                      <span
                        className={`text-sm font-medium ${
                          t.accuracy >= 0.7
                            ? "text-emerald-400"
                            : t.accuracy >= 0.5
                            ? "text-amber-400"
                            : "text-red-400"
                        }`}
                      >
                        {(t.accuracy * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-sm text-slate-500 text-right tabular-nums hidden sm:table-cell">
                      {t.avg_time > 0 ? `${t.avg_time.toFixed(0)}s` : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Distribución horaria */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
        <h4 className="text-sm font-semibold text-slate-300 mb-3">
          Distribución horaria de actividad
        </h4>
        <ResponsiveContainer width="100%" height={100}>
          <BarChart data={data.hourly_distribution} margin={{ top: 0, right: 0, bottom: 0, left: -30 }}>
            <XAxis
              dataKey="hour"
              tick={{ fontSize: 9, fill: "#64748b" }}
              tickFormatter={(v: number) => `${v}h`}
              interval={3}
            />
            <YAxis tick={{ fontSize: 9, fill: "#64748b" }} allowDecimals={false} />
            <Tooltip
              contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: "#94a3b8" }}
              itemStyle={{ color: "#a78bfa" }}
              labelFormatter={(v) => `${v}:00 h`}
            />
            <Bar dataKey="count" name="Intentos" radius={[2, 2, 0, 0]}>
              {data.hourly_distribution.map((h) => (
                <Cell
                  key={h.hour}
                  fill={h.hour === peakHour.hour ? "#a78bfa" : "#6c63ff"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ── Tab de ranking del grupo ────────────────────────────────────────────────

function GroupRankingSection({ students }: { students: import("../../api/teacher").StudentSummary[] }) {
  // Deduplica por user_id y ordena por ELO DESC
  const uniqueById = new Map<number, import("../../api/teacher").StudentSummary>();
  for (const s of students) {
    const existing = uniqueById.get(s.user_id);
    if (!existing || s.global_elo > existing.global_elo) uniqueById.set(s.user_id, s);
  }
  const ranked = [...uniqueById.values()].sort((a, b) => b.global_elo - a.global_elo);

  if (ranked.length === 0) {
    return <p className="text-slate-500 text-sm py-4">Sin datos de ranking.</p>;
  }

  const medal = (pos: number) => pos === 1 ? "🥇" : pos === 2 ? "🥈" : pos === 3 ? "🥉" : null;

  return (
    <div className="space-y-1.5">
      {ranked.map((s, i) => {
        const pos = i + 1;
        const m = medal(pos);
        return (
          <div
            key={s.user_id}
            className="flex items-center gap-3 rounded-lg px-3 py-2 bg-slate-900/60 border border-slate-700/50"
          >
            <span className="text-xs text-slate-500 w-7 text-center font-mono">
              {m ?? `#${pos}`}
            </span>
            <span className="text-xs text-slate-300 flex-1 truncate">{s.username}</span>
            {s.group_name && (
              <span className="text-xs text-slate-600 hidden sm:block">{s.group_name}</span>
            )}
            <span className="text-xs font-mono text-slate-300 w-14 text-right">
              {Math.round(s.global_elo)}
            </span>
            <span className={`text-xs w-12 text-right ${s.accuracy >= 0.7 ? "text-green-400" : s.accuracy >= 0.5 ? "text-yellow-400" : "text-red-400"}`}>
              {(s.accuracy * 100).toFixed(0)}%
            </span>
          </div>
        );
      })}
    </div>
  );
}

// ── Dashboard principal ─────────────────────────────────────────────────────

type DashboardView = "students" | "ranking" | "metrics";

export function TeacherDashboard() {
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);
  const [search, setSearch] = useState("");
  const [filterGroup, setFilterGroup] = useState<string>("all");
  const [filterLevel, setFilterLevel] = useState<string>("all");
  const [view, setView] = useState<DashboardView>("students");

  const { data, isLoading, error } = useQuery({
    queryKey: ["teacher-dashboard"],
    queryFn: teacherApi.dashboard,
    staleTime: 60_000,
  });

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (error || !data) {
    return (
      <div className="max-w-2xl mx-auto py-8 px-4 text-center">
        <p className="text-red-400">Error al cargar el dashboard. Verifica tu sesión.</p>
      </div>
    );
  }

  // Filtros disponibles derivados de los datos
  const groupOptions = Array.from(
    new Map(data.students.filter((s) => s.group_id).map((s) => [s.group_id, s.group_name])).entries()
  );
  const levelOptions = Array.from(
    new Set(data.students.map((s) => s.education_level).filter(Boolean)) as Set<string>
  );

  // Aplicar filtros en cascada
  const afterGroupFilter =
    filterGroup === "all"
      ? data.students
      : data.students.filter((s) => String(s.group_id) === filterGroup);

  const afterLevelFilter =
    filterLevel === "all"
      ? afterGroupFilter
      : afterGroupFilter.filter((s) => s.education_level === filterLevel);

  const filtered = afterLevelFilter.filter((s) =>
    s.username.toLowerCase().includes(search.toLowerCase()),
  );

  // Stats sobre los estudiantes visibles (deduplicados por user_id para los promedios)
  const uniqueStudents = Array.from(new Map(data.students.map((s) => [s.user_id, s])).values());
  const avgElo = uniqueStudents.length > 0
    ? uniqueStudents.reduce((s, u) => s + u.global_elo, 0) / uniqueStudents.length
    : 0;
  const avgAccuracy = uniqueStudents.length > 0
    ? uniqueStudents.reduce((s, u) => s + u.accuracy, 0) / uniqueStudents.length
    : 0;

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-100">Panel Docente</h2>
        <span className="text-xs text-slate-500">{uniqueStudents.length} estudiantes</span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard label="Grupos activos" value={data.groups.length} />
        <StatCard label="Estudiantes" value={uniqueStudents.length} />
        <StatCard label="ELO promedio" value={Math.round(avgElo)} />
        <StatCard label="Acierto promedio" value={`${(avgAccuracy * 100).toFixed(0)}%`} />
      </div>

      {/* Grupos resumen */}
      {data.groups.length > 0 && (
        <div className="flex flex-wrap gap-3">
          {data.groups.map((g) => (
            <div
              key={g.group_id}
              className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm"
            >
              <span className="text-slate-100 font-medium">{g.name}</span>
              <span className="text-slate-500 ml-2">· {g.student_count} estudiantes</span>
            </div>
          ))}
        </div>
      )}

      {/* Detalle de estudiante seleccionado */}
      {selectedStudentId !== null && (
        <StudentDetailPanel
          studentId={selectedStudentId}
          onClose={() => setSelectedStudentId(null)}
        />
      )}

      {/* Tabs: Estudiantes | Ranking | Métricas */}
      <div className="flex gap-1 border-b border-slate-700 pb-2">
        {([
          { id: "students", label: "👥 Estudiantes" },
          { id: "ranking", label: "🏆 Ranking" },
          { id: "metrics", label: "📊 Métricas" },
        ] as { id: DashboardView; label: string }[]).map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setView(id)}
            aria-current={view === id ? "true" : undefined}
            className={[
              "text-sm px-3 py-1.5 rounded-lg transition-colors",
              view === id ? "bg-violet-600/30 text-violet-300" : "text-slate-500 hover:text-slate-300",
            ].join(" ")}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Vista: Tabla de estudiantes */}
      {view === "students" && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
          {/* Filtros */}
          <div className="flex flex-wrap items-center gap-3 px-4 py-3 border-b border-slate-700">
            <h3 className="text-sm font-semibold text-slate-300 mr-auto">Estudiantes</h3>

            {/* Filtro Grupo */}
            {groupOptions.length > 1 && (
              <select
                value={filterGroup}
                onChange={(e) => { setFilterGroup(e.target.value); setFilterLevel("all"); }}
                className="bg-slate-900 border border-slate-600 rounded px-2 py-1 text-xs text-slate-300 focus:outline-none focus:border-violet-500"
              >
                <option value="all">Todos los grupos</option>
                {groupOptions.map(([id, name]) => (
                  <option key={id} value={String(id)}>{name}</option>
                ))}
              </select>
            )}

            {/* Filtro Nivel (solo si hay más de uno disponible en el grupo seleccionado) */}
            {levelOptions.length > 1 && (
              <select
                value={filterLevel}
                onChange={(e) => setFilterLevel(e.target.value)}
                className="bg-slate-900 border border-slate-600 rounded px-2 py-1 text-xs text-slate-300 focus:outline-none focus:border-violet-500"
              >
                <option value="all">Todos los niveles</option>
                {levelOptions.map((l) => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
            )}

            {/* Búsqueda por nombre */}
            <input
              type="text"
              placeholder="Buscar..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-slate-900 border border-slate-600 rounded px-3 py-1 text-sm text-slate-200 focus:outline-none focus:border-violet-500 placeholder-slate-600 w-36"
            />
          </div>

          {filtered.length === 0 ? (
            <p className="text-slate-500 text-sm text-center py-8">Sin estudiantes para los filtros aplicados.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-xs text-slate-500 border-b border-slate-700">
                    <th className="px-4 py-2 text-left">Estudiante</th>
                    <th className="px-4 py-2 text-left hidden sm:table-cell">Grupo</th>
                    <th className="px-4 py-2 text-left">ELO</th>
                    <th className="px-4 py-2 text-center">Intentos</th>
                    <th className="px-4 py-2 text-center">Acierto</th>
                    <th className="px-4 py-2 text-left">Última actividad</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50">
                  {filtered.map((s) => (
                    <tr
                      key={`${s.user_id}-${s.group_id}`}
                      className="hover:bg-slate-700/50 cursor-pointer transition-colors"
                      onClick={() => setSelectedStudentId(s.user_id)}
                    >
                      <td className="px-4 py-3">
                        <div className="font-medium text-slate-100">{s.username}</div>
                        {s.education_level && (
                          <div className="text-xs text-slate-600">{s.education_level}</div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-500 hidden sm:table-cell">
                        {s.group_name ?? "—"}
                      </td>
                      <td className="px-4 py-3 w-40">
                        <EloBar elo={s.global_elo} />
                      </td>
                      <td className="px-4 py-3 text-center text-slate-300 text-sm">{s.total_attempts}</td>
                      <td className="px-4 py-3 text-center">
                        <span className={`text-sm font-medium ${s.accuracy >= 0.7 ? "text-green-400" : s.accuracy >= 0.5 ? "text-yellow-400" : "text-red-400"}`}>
                          {(s.accuracy * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-500">
                        {s.last_activity ?? "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Vista: Ranking */}
      {view === "ranking" && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-300">Ranking de estudiantes</h3>
            {groupOptions.length > 1 && (
              <select
                value={filterGroup}
                onChange={(e) => setFilterGroup(e.target.value)}
                className="bg-slate-900 border border-slate-600 rounded px-2 py-1 text-xs text-slate-300 focus:outline-none focus:border-violet-500"
              >
                <option value="all">Todos los grupos</option>
                {groupOptions.map(([id, name]) => (
                  <option key={id} value={String(id)}>{name}</option>
                ))}
              </select>
            )}
          </div>
          <GroupRankingSection students={afterGroupFilter} />
        </div>
      )}

      {/* Vista: Métricas */}
      {view === "metrics" && <MetricsView />}
    </div>
  );
}
