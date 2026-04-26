/**
 * pages/Admin/Groups.tsx
 * =======================
 * Vista de administrador: todos los grupos del sistema con opción de eliminar.
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "../../api/teacher";
import type { AdminGroup } from "../../api/teacher";
import { Button } from "../../components/ui/Button";

function GroupRow({
  group,
  onDelete,
  deleting,
}: {
  group: AdminGroup;
  onDelete: (id: number) => void;
  deleting: boolean;
}) {
  const [confirm, setConfirm] = useState(false);

  return (
    <tr className="hover:bg-slate-700/30 transition-colors">
      <td className="px-4 py-3 text-slate-100 text-sm font-medium">{group.name}</td>
      <td className="px-4 py-3 text-slate-400 text-sm">{group.teacher_username ?? `ID ${group.teacher_id}`}</td>
      <td className="px-4 py-3 text-center text-slate-300 text-sm">{group.student_count ?? "—"}</td>
      <td className="px-4 py-3">
        {confirm ? (
          <div className="flex items-center gap-2">
            <span className="text-xs text-red-400">¿Confirmar?</span>
            <Button
              size="sm"
              variant="danger"
              loading={deleting}
              onClick={() => onDelete(group.id)}
            >
              Sí, eliminar
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setConfirm(false)}>
              Cancelar
            </Button>
          </div>
        ) : (
          <Button size="sm" variant="danger" onClick={() => setConfirm(true)}>
            Eliminar
          </Button>
        )}
      </td>
    </tr>
  );
}

export function AdminGroups() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["admin-groups"],
    queryFn: adminApi.allGroups,
    staleTime: 30_000,
  });

  const deleteMutation = useMutation({
    mutationFn: (group_id: number) => adminApi.deleteGroup(group_id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-groups"] });
      setDeletingId(null);
    },
    onError: () => setDeletingId(null),
  });

  const handleDelete = (group_id: number) => {
    setDeletingId(group_id);
    deleteMutation.mutate(group_id);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-400 animate-pulse">Cargando grupos...</p>
      </div>
    );
  }

  const groups = data?.groups ?? [];
  const filtered = groups.filter((g) =>
    g.name.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="max-w-4xl mx-auto py-6 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-100">Grupos del Sistema</h2>
        <span className="text-xs text-slate-500">{groups.length} grupos</span>
      </div>

      <div className="bg-amber-900/20 border border-amber-700/30 rounded-lg px-4 py-2 text-xs text-amber-300">
        ⚠ Eliminar un grupo desvincula a sus estudiantes. Esta acción queda registrada en la auditoría.
      </div>

      <input
        type="text"
        placeholder="Buscar grupo..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500 placeholder-slate-600"
      />

      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-xs text-slate-500 border-b border-slate-700">
                <th className="px-4 py-2 text-left">Nombre del grupo</th>
                <th className="px-4 py-2 text-left">Docente</th>
                <th className="px-4 py-2 text-center">Estudiantes</th>
                <th className="px-4 py-2 text-left">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={4} className="text-center text-slate-500 text-sm py-8">
                    Sin grupos registrados.
                  </td>
                </tr>
              ) : (
                filtered.map((g) => (
                  <GroupRow
                    key={g.id}
                    group={g}
                    onDelete={handleDelete}
                    deleting={deletingId === g.id && deleteMutation.isPending}
                  />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
