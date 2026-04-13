/**
 * pages/Admin/Users.tsx
 * ======================
 * Panel de administración de usuarios: aprobar docentes, activar/desactivar cuentas.
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "../../api/teacher";
import type { AdminUser } from "../../api/teacher";
import { Button } from "../../components/ui/Button";

function RoleBadge({ role }: { role: string }) {
  const colors: Record<string, string> = {
    student: "bg-blue-900/50 text-blue-300",
    teacher: "bg-violet-900/50 text-violet-300",
    admin: "bg-yellow-900/50 text-yellow-300",
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${colors[role] ?? "bg-slate-700 text-slate-300"}`}>
      {role}
    </span>
  );
}

function PendingTeachersSection() {
  const qc = useQueryClient();

  const { data } = useQuery({
    queryKey: ["pending-teachers"],
    queryFn: adminApi.pendingTeachers,
    refetchInterval: 30_000,
  });

  const approveMutation = useMutation({
    mutationFn: ({ user_id, action }: { user_id: number; action: "approve" | "reject" }) =>
      adminApi.approveTeacher(user_id, action),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["pending-teachers"] });
      qc.invalidateQueries({ queryKey: ["admin-users"] });
    },
  });

  const teachers = data?.teachers ?? [];
  if (teachers.length === 0) return null;

  const getUserId = (u: AdminUser) => (u.user_id ?? u.id ?? 0) as number;

  return (
    <div className="bg-amber-900/20 border border-amber-700/40 rounded-xl p-4 space-y-3">
      <div className="flex items-center gap-2">
        <span className="text-amber-400">🔔</span>
        <h3 className="text-sm font-semibold text-amber-300">
          Docentes pendientes de aprobación ({teachers.length})
        </h3>
      </div>
      <div className="space-y-2">
        {teachers.map((t) => {
          const uid = getUserId(t);
          return (
            <div
              key={uid}
              className="flex items-center justify-between bg-slate-800 rounded-lg px-3 py-2 border border-slate-700"
            >
              <div>
                <span className="text-white font-medium text-sm">{t.username}</span>
                <span className="text-xs text-slate-500 ml-2">docente</span>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  loading={approveMutation.isPending}
                  onClick={() => approveMutation.mutate({ user_id: uid, action: "approve" })}
                >
                  ✓ Aprobar
                </Button>
                <Button
                  size="sm"
                  variant="danger"
                  loading={approveMutation.isPending}
                  onClick={() => approveMutation.mutate({ user_id: uid, action: "reject" })}
                >
                  ✕ Rechazar
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function UserRow({ user }: { user: AdminUser }) {
  const qc = useQueryClient();

  const isActive = !!user.active;
  const uid = (user.user_id ?? user.id ?? 0) as number;

  const toggleMutation = useMutation({
    mutationFn: () => (isActive ? adminApi.deactivate(uid) : adminApi.reactivate(uid)),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-users"] }),
  });

  return (
    <tr className="hover:bg-slate-700/30 transition-colors">
      <td className="px-4 py-3">
        <span className="text-slate-100 text-sm font-medium">{user.username}</span>
      </td>
      <td className="px-4 py-3">
        <RoleBadge role={user.role} />
      </td>
      <td className="px-4 py-3 text-sm text-slate-400">
        {user.education_level ?? "—"}
      </td>
      <td className="px-4 py-3 text-sm text-slate-400">
        {user.group_name ?? "—"}
      </td>
      <td className="px-4 py-3">
        <span
          className={`text-xs px-2 py-0.5 rounded-full ${
            isActive ? "bg-green-900/40 text-green-400" : "bg-red-900/40 text-red-400"
          }`}
        >
          {isActive ? "activo" : "inactivo"}
        </span>
      </td>
      <td className="px-4 py-3">
        <Button
          size="sm"
          variant={isActive ? "danger" : "secondary"}
          loading={toggleMutation.isPending}
          onClick={() => toggleMutation.mutate()}
        >
          {isActive ? "Desactivar" : "Activar"}
        </Button>
      </td>
    </tr>
  );
}

export function AdminUsers() {
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<string>("all");

  const { data, isLoading } = useQuery({
    queryKey: ["admin-users"],
    queryFn: adminApi.users,
    staleTime: 30_000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-400 animate-pulse">Cargando usuarios...</p>
      </div>
    );
  }

  const users = data?.users ?? [];
  const filtered = users.filter((u) => {
    const matchSearch = u.username.toLowerCase().includes(search.toLowerCase());
    const matchRole = roleFilter === "all" || u.role === roleFilter;
    return matchSearch && matchRole;
  });

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Gestión de Usuarios</h2>
        <span className="text-xs text-slate-500">{users.length} usuarios en total</span>
      </div>

      {/* Docentes pendientes */}
      <PendingTeachersSection />

      {/* Filtros */}
      <div className="flex gap-3 flex-wrap">
        <input
          type="text"
          placeholder="Buscar usuario..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500 placeholder-slate-600"
        />
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
        >
          <option value="all">Todos los roles</option>
          <option value="student">Estudiantes</option>
          <option value="teacher">Docentes</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      {/* Tabla */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-xs text-slate-500 border-b border-slate-700">
                <th className="px-4 py-2 text-left">Usuario</th>
                <th className="px-4 py-2 text-left">Rol</th>
                <th className="px-4 py-2 text-left">Nivel</th>
                <th className="px-4 py-2 text-left">Grupo</th>
                <th className="px-4 py-2 text-left">Estado</th>
                <th className="px-4 py-2 text-left">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center text-slate-500 text-sm py-8">
                    Sin usuarios que coincidan.
                  </td>
                </tr>
              ) : (
                filtered.map((u, idx) => <UserRow key={(u.user_id ?? u.id ?? idx) as number} user={u} />)
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
