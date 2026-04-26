/**
 * pages/Admin/Audit.tsx
 * ======================
 * Log de auditoría de reasignaciones de grupo.
 */

import { useQuery } from "@tanstack/react-query";
import { adminApi } from "../../api/teacher";
import type { AuditEntry } from "../../api/teacher";

function formatTimestamp(ts: string): string {
  if (!ts) return "—";
  const d = new Date(ts.replace(" ", "T"));
  if (isNaN(d.getTime())) return ts.slice(0, 16);
  return d.toLocaleString("es-CO", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function AuditRow({ entry }: { entry: AuditEntry }) {
  const oldLabel = entry.old_group_name ?? (entry.old_group_id ? `ID ${entry.old_group_id}` : "sin grupo");
  const newLabel = entry.new_group_name ?? (entry.new_group_id ? `ID ${entry.new_group_id}` : "sin grupo");

  return (
    <tr className="hover:bg-slate-700/30 transition-colors">
      <td className="px-4 py-3 text-xs text-slate-500">#{entry.id}</td>
      <td className="px-4 py-3 text-sm text-slate-100">
        {entry.student_username ?? `ID ${entry.student_id}`}
      </td>
      <td className="px-4 py-3 text-sm text-slate-400">{oldLabel}</td>
      <td className="px-4 py-3 text-slate-500">→</td>
      <td className="px-4 py-3 text-sm text-violet-300">{newLabel}</td>
      <td className="px-4 py-3 text-sm text-amber-300">
        {entry.admin_username ?? `ID ${entry.admin_id}`}
      </td>
      <td className="px-4 py-3 text-xs text-slate-500">{formatTimestamp(entry.timestamp)}</td>
    </tr>
  );
}

export function AdminAudit() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin-audit"],
    queryFn: () => adminApi.audit(200),
    staleTime: 30_000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-400 animate-pulse">Cargando auditoría...</p>
      </div>
    );
  }

  const entries = data?.entries ?? [];

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-100">Auditoría de Grupos</h2>
        <span className="text-xs text-slate-500">
          {entries.length} reasignaci{entries.length !== 1 ? "ones" : "ón"}
        </span>
      </div>

      <p className="text-xs text-slate-500">
        Registro de cambios de grupo ejecutados por administradores. Ordenado del más reciente al
        más antiguo.
      </p>

      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-xs text-slate-500 border-b border-slate-700">
                <th className="px-4 py-2 text-left">ID</th>
                <th className="px-4 py-2 text-left">Estudiante</th>
                <th className="px-4 py-2 text-left">Grupo anterior</th>
                <th className="px-4 py-2 text-left"></th>
                <th className="px-4 py-2 text-left">Grupo nuevo</th>
                <th className="px-4 py-2 text-left">Admin</th>
                <th className="px-4 py-2 text-left">Fecha</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {entries.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center text-slate-500 text-sm py-8">
                    Sin reasignaciones registradas.
                  </td>
                </tr>
              ) : (
                entries.map((e) => <AuditRow key={e.id} entry={e} />)
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
