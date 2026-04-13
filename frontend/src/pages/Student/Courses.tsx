/**
 * pages/Student/Courses.tsx
 * ==========================
 * Catálogo de cursos: explorar, matricularse, acceso por código.
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { studentApi, type Course } from "../../api/student";
import { Button } from "../../components/ui/Button";

export function Courses() {
  const qc = useQueryClient();
  const [tab, setTab] = useState<"explore" | "enrolled" | "code">("explore");
  const [inviteCode, setInviteCode] = useState("");
  const [codeMsg, setCodeMsg] = useState("");

  const { data: courses = [], isLoading } = useQuery({
    queryKey: ["courses"],
    queryFn: () => studentApi.courses(),
  });

  const enrollMutation = useMutation({
    mutationFn: (courseId: string) => studentApi.enroll(courseId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["courses"] }),
  });

  const unenrollMutation = useMutation({
    mutationFn: (courseId: string) => studentApi.unenroll(courseId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["courses"] }),
  });

  const codeMutation = useMutation({
    mutationFn: (code: string) => studentApi.enrollByCode(code),
    onSuccess: (data) => {
      setCodeMsg(`✅ Acceso especial activado para ${data.course_id}`);
      qc.invalidateQueries({ queryKey: ["courses"] });
      setInviteCode("");
    },
    onError: (err: Error) => setCodeMsg(`❌ ${err.message}`),
  });

  const tabs = [
    { id: "explore" as const, label: "Explorar" },
    { id: "enrolled" as const, label: "Mis matrículas" },
    { id: "code" as const, label: "Código de acceso" },
  ];

  const displayed: Course[] =
    tab === "enrolled" ? courses.filter((c) => c.enrolled) : courses;

  return (
    <div className="max-w-2xl mx-auto py-6 px-4">
      <h2 className="text-xl font-bold text-white mb-6">Cursos</h2>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-slate-700 pb-2">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => { setTab(t.id); setCodeMsg(""); }}
            className={[
              "px-3 py-1.5 rounded-lg text-sm font-medium transition-all",
              tab === t.id
                ? "bg-violet-600 text-white"
                : "text-slate-400 hover:text-white",
            ].join(" ")}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Código de acceso */}
      {tab === "code" && (
        <div className="space-y-4">
          <p className="text-sm text-slate-400">
            Usa el código de invitación que te compartió tu docente para acceder a
            un curso de otro nivel educativo.
          </p>
          <div className="flex gap-3">
            <input
              type="text"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value.trim().toUpperCase())}
              placeholder="Ej: ABC123"
              className="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-violet-500"
            />
            <Button
              onClick={() => codeMutation.mutate(inviteCode)}
              loading={codeMutation.isPending}
              disabled={!inviteCode}
            >
              Acceder
            </Button>
          </div>
          {codeMsg && (
            <p className={`text-sm ${codeMsg.startsWith("✅") ? "text-green-400" : "text-red-400"}`}>
              {codeMsg}
            </p>
          )}
        </div>
      )}

      {/* Lista de cursos */}
      {tab !== "code" && (
        <>
          {isLoading ? (
            <div className="animate-pulse text-slate-400 text-sm">Cargando cursos...</div>
          ) : displayed.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              {tab === "enrolled"
                ? "No estás matriculado en ningún curso aún."
                : "No hay cursos disponibles para tu nivel."}
            </div>
          ) : (
            <div className="space-y-3">
              {displayed.map((c) => (
                <div
                  key={c.id}
                  className="bg-slate-800 rounded-xl px-4 py-4 border border-slate-700 flex items-center justify-between"
                >
                  <div>
                    <div className="font-medium text-white text-sm">{c.name}</div>
                    <div className="text-xs text-slate-500 mt-0.5">{c.block}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    {c.enrolled ? (
                      <>
                        <span className="text-xs text-green-400 bg-green-900/30 px-2 py-0.5 rounded-full">
                          Matriculado
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => unenrollMutation.mutate(c.id)}
                          loading={unenrollMutation.isPending}
                        >
                          Salir
                        </Button>
                      </>
                    ) : (
                      <Button
                        size="sm"
                        onClick={() => enrollMutation.mutate(c.id)}
                        loading={enrollMutation.isPending}
                      >
                        Matricularme
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
