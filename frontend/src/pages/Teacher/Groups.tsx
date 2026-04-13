/**
 * pages/Teacher/Groups.tsx
 * ========================
 * Gestión de grupos del docente: crear grupos y generar códigos de invitación.
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { teacherApi } from "../../api/teacher";
import { studentApi } from "../../api/student";
import { Button } from "../../components/ui/Button";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="text-xs bg-slate-700 hover:bg-slate-600 text-slate-300 px-2 py-1 rounded transition-colors"
    >
      {copied ? "✓ Copiado" : "Copiar"}
    </button>
  );
}

function GroupCard({
  group,
  onGenerateCode,
  loadingCode,
}: {
  group: { group_id: number; name: string; course_id: string | null; invite_code: string | null; student_count: number };
  onGenerateCode: (id: number) => void;
  loadingCode: boolean;
}) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div>
          <h4 className="font-semibold text-white">{group.name}</h4>
          {group.course_id && (
            <p className="text-xs text-slate-500 mt-0.5">{group.course_id}</p>
          )}
        </div>
        <span className="text-sm text-slate-400 bg-slate-700 px-2 py-0.5 rounded-full">
          {group.student_count} estudiantes
        </span>
      </div>

      {/* Código de invitación */}
      <div className="border-t border-slate-700 pt-3">
        <p className="text-xs text-slate-500 mb-2">Código de acceso inter-nivel</p>
        {group.invite_code ? (
          <div className="flex items-center gap-2">
            <code className="flex-1 bg-slate-900 border border-slate-600 rounded px-3 py-1.5 text-sm text-violet-300 font-mono tracking-wider">
              {group.invite_code}
            </code>
            <CopyButton text={group.invite_code} />
          </div>
        ) : (
          <p className="text-xs text-slate-600 italic mb-2">Sin código generado</p>
        )}
        <Button
          variant="ghost"
          size="sm"
          className="mt-2 text-xs"
          loading={loadingCode}
          onClick={() => onGenerateCode(group.group_id)}
        >
          {group.invite_code ? "🔄 Regenerar código" : "✨ Generar código"}
        </Button>
      </div>
    </div>
  );
}

export function TeacherGroups() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ course_id: "", group_name: "" });
  const [generatingId, setGeneratingId] = useState<number | null>(null);
  const [formError, setFormError] = useState("");

  const { data: groups = [], isLoading } = useQuery({
    queryKey: ["teacher-groups"],
    queryFn: teacherApi.groups,
    staleTime: 30_000,
  });

  // Lista de cursos para el selector al crear grupo
  const { data: allCourses = [] } = useQuery({
    queryKey: ["all-courses"],
    queryFn: () => studentApi.courses(),
    staleTime: 300_000,
  });

  const createMutation = useMutation({
    mutationFn: () => teacherApi.createGroup(formData.course_id, formData.group_name),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teacher-groups"] });
      qc.invalidateQueries({ queryKey: ["teacher-dashboard"] });
      setShowForm(false);
      setFormData({ course_id: "", group_name: "" });
      setFormError("");
    },
    onError: (err: Error) => setFormError(err.message),
  });

  const handleGenerateCode = async (group_id: number) => {
    setGeneratingId(group_id);
    try {
      await teacherApi.generateInviteCode(group_id);
      qc.invalidateQueries({ queryKey: ["teacher-groups"] });
    } finally {
      setGeneratingId(null);
    }
  };

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.course_id || !formData.group_name.trim()) {
      setFormError("Selecciona un curso y escribe un nombre de grupo.");
      return;
    }
    createMutation.mutate();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-400 animate-pulse">Cargando grupos...</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-6 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Mis Grupos</h2>
        <Button size="sm" onClick={() => { setShowForm(true); setFormError(""); }}>
          + Nuevo grupo
        </Button>
      </div>

      {/* Formulario de creación */}
      {showForm && (
        <div className="bg-slate-800 border border-violet-600/40 rounded-xl p-4 space-y-4">
          <h3 className="text-sm font-semibold text-violet-300">Crear grupo nuevo</h3>
          <form onSubmit={handleCreateSubmit} className="space-y-3">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Nombre del grupo</label>
              <input
                type="text"
                value={formData.group_name}
                onChange={(e) => setFormData((d) => ({ ...d, group_name: e.target.value }))}
                placeholder="Ej: Cálculo 2025-A"
                maxLength={80}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-violet-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Curso</label>
              <select
                value={formData.course_id}
                onChange={(e) => setFormData((d) => ({ ...d, course_id: e.target.value }))}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-100 text-sm focus:outline-none focus:border-violet-500"
                required
              >
                <option value="">— Seleccionar curso —</option>
                {allCourses.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.block})
                  </option>
                ))}
              </select>
            </div>
            {formError && <p className="text-red-400 text-xs">{formError}</p>}
            <div className="flex gap-2">
              <Button type="submit" size="sm" loading={createMutation.isPending}>
                Crear
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => { setShowForm(false); setFormError(""); }}
              >
                Cancelar
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Lista de grupos */}
      {groups.length === 0 ? (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 text-center">
          <p className="text-slate-400 mb-2">No tienes grupos creados.</p>
          <p className="text-slate-600 text-sm">Crea un grupo para empezar a gestionar estudiantes.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {groups.map((g) => (
            <GroupCard
              key={g.group_id}
              group={g}
              onGenerateCode={handleGenerateCode}
              loadingCode={generatingId === g.group_id}
            />
          ))}
        </div>
      )}
    </div>
  );
}
