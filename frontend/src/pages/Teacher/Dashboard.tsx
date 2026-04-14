/**
 * pages/Teacher/Dashboard.tsx
 * ============================
 * Panel principal del docente: resumen de grupos y tabla de estudiantes.
 */

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { teacherApi } from "../../api/teacher";
import type { StudentSummary } from "../../api/teacher";
import { ELOChart } from "../../components/ELO/ELOChart";
import { useSettingsStore } from "../../stores/settingsStore";

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
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="text-sm text-slate-400 mt-0.5">{label}</div>
      {sub && <div className="text-xs text-slate-600 mt-1">{sub}</div>}
    </div>
  );
}

function StudentRow({
  student,
  onSelect,
}: {
  student: StudentSummary;
  onSelect: (id: number) => void;
}) {
  return (
    <tr
      className="hover:bg-slate-700/50 cursor-pointer transition-colors"
      onClick={() => onSelect(student.user_id)}
    >
      <td className="px-4 py-3">
        <div className="font-medium text-slate-100">{student.username}</div>
      </td>
      <td className="px-4 py-3 w-40">
        <EloBar elo={student.global_elo} />
      </td>
      <td className="px-4 py-3 text-center text-slate-300 text-sm">{student.total_attempts}</td>
      <td className="px-4 py-3 text-center">
        <span
          className={`text-sm font-medium ${
            student.accuracy >= 0.7
              ? "text-green-400"
              : student.accuracy >= 0.5
                ? "text-yellow-400"
                : "text-red-400"
          }`}
        >
          {(student.accuracy * 100).toFixed(0)}%
        </span>
      </td>
      <td className="px-4 py-3 text-sm text-slate-500">
        {student.last_activity ? student.last_activity.slice(0, 10) : "—"}
      </td>
    </tr>
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
        <h4 className="font-semibold text-white">Detalle del estudiante</h4>
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

      {isLoading && <p className="text-slate-400 text-sm animate-pulse">Cargando...</p>}

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
            <span className="font-bold text-white">{Math.round((data.global_elo as number) ?? 0)}</span>
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
                    <div className="text-white text-xs font-medium">
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
                className="w-full py-2 rounded-lg bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white text-sm transition-colors"
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

export function TeacherDashboard() {
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);
  const [search, setSearch] = useState("");

  const { data, isLoading, error } = useQuery({
    queryKey: ["teacher-dashboard"],
    queryFn: teacherApi.dashboard,
    staleTime: 60_000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-400 animate-pulse">Cargando dashboard...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-2xl mx-auto py-8 px-4 text-center">
        <p className="text-red-400">Error al cargar el dashboard. Verifica tu sesión.</p>
      </div>
    );
  }

  const avgElo =
    data.students.length > 0
      ? data.students.reduce((s, u) => s + u.global_elo, 0) / data.students.length
      : 0;

  const avgAccuracy =
    data.students.length > 0
      ? data.students.reduce((s, u) => s + u.accuracy, 0) / data.students.length
      : 0;

  const filtered = data.students.filter((s) =>
    s.username.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Panel Docente</h2>
        <span className="text-xs text-slate-500">{data.students.length} estudiantes</span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard label="Grupos activos" value={data.groups.length} />
        <StatCard label="Estudiantes" value={data.students.length} />
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
              <span className="text-white font-medium">{g.name}</span>
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

      {/* Tabla de estudiantes */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
          <h3 className="text-sm font-semibold text-slate-300">Estudiantes</h3>
          <input
            type="text"
            placeholder="Buscar por nombre..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-slate-900 border border-slate-600 rounded px-3 py-1 text-sm text-slate-200 focus:outline-none focus:border-violet-500 placeholder-slate-600"
          />
        </div>

        {filtered.length === 0 ? (
          <p className="text-slate-500 text-sm text-center py-8">Sin estudiantes registrados.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-xs text-slate-500 border-b border-slate-700">
                  <th className="px-4 py-2 text-left">Estudiante</th>
                  <th className="px-4 py-2 text-left">ELO</th>
                  <th className="px-4 py-2 text-center">Intentos</th>
                  <th className="px-4 py-2 text-center">Acierto</th>
                  <th className="px-4 py-2 text-left">Última actividad</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {filtered.map((s) => (
                  <StudentRow key={s.user_id} student={s} onSelect={setSelectedStudentId} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
