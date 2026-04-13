/**
 * pages/Teacher/Dashboard.tsx
 * ============================
 * Panel principal del docente: resumen de grupos y tabla de estudiantes.
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { teacherApi } from "../../api/teacher";
import type { StudentSummary } from "../../api/teacher";

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

function StudentDetailPanel({
  studentId,
  onClose,
}: {
  studentId: number;
  onClose: () => void;
}) {
  const { data, isLoading } = useQuery({
    queryKey: ["teacher-student", studentId],
    queryFn: () => teacherApi.studentReport(studentId),
  });

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="font-semibold text-white">Detalle del estudiante</h4>
        <button onClick={onClose} className="text-slate-500 hover:text-slate-300 text-sm">
          ✕ Cerrar
        </button>
      </div>

      {isLoading && <p className="text-slate-400 text-sm animate-pulse">Cargando...</p>}

      {data && (
        <div className="space-y-2 text-sm">
          <p className="text-slate-300">
            <span className="text-slate-500">ELO global:</span>{" "}
            <span className="font-medium text-white">
              {Math.round((data.global_elo as number) ?? 0)}
            </span>
          </p>

          {(() => {
            const breakdown = data.topic_breakdown as Record<string, Record<string, number>> | undefined;
            if (!breakdown || Object.keys(breakdown).length === 0) return null;
            return (
              <div>
                <p className="text-slate-500 mb-1">Tópicos:</p>
                <div className="grid grid-cols-2 gap-1">
                  {Object.entries(breakdown)
                    .slice(0, 6)
                    .map(([topic, info]) => (
                      <div key={topic} className="bg-slate-900 rounded px-2 py-1">
                        <div className="text-xs text-slate-400 truncate">{topic}</div>
                        <div className="text-white text-xs font-medium">
                          {Math.round(info.rating ?? 0)}
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            );
          })()}
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
