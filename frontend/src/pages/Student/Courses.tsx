/**
 * pages/Student/Courses.tsx
 * ==========================
 * Catálogo de cursos: explorar + practicar, gestionar matrículas, acceso por código.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { studentApi, type Course } from "../../api/student";
import { Button } from "../../components/ui/Button";
import { CoursesSkeleton } from "../../components/ui/Skeleton";
import { CourseBanner } from "../../components/CourseCard/CourseBanner";
import { usePracticeStore } from "../../stores/practiceStore";

export function Courses() {
  const qc = useQueryClient();
  const navigate = useNavigate();
  const startSession = usePracticeStore((s) => s.startSession);
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

  const handlePractice = (courseId: string) => {
    startSession(courseId);
    navigate("/student");
  };

  const tabs = [
    { id: "explore" as const, label: "Explorar" },
    { id: "enrolled" as const, label: "Mis matrículas" },
    { id: "code" as const, label: "Código de acceso" },
  ];

  const enrolled = courses.filter((c) => c.enrolled);
  const displayed: Course[] = tab === "enrolled" ? enrolled : courses;

  return (
    <div className="max-w-5xl mx-auto py-6 px-4">
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
            {t.id === "enrolled" && enrolled.length > 0 && (
              <span className="ml-1.5 text-xs opacity-70">({enrolled.length})</span>
            )}
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
          {tab === "explore" && (
            <p className="text-sm text-slate-400 mb-4">
              Elige un curso para practicar. Si aún no estás matriculado, inscríbete primero.
            </p>
          )}
          {tab === "enrolled" && (
            <p className="text-sm text-slate-400 mb-4">
              Gestiona tus matrículas. Puedes darte de baja de un curso en cualquier momento.
            </p>
          )}

          {isLoading ? (
            <CoursesSkeleton />
          ) : displayed.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              {tab === "enrolled"
                ? "No estás matriculado en ningún curso aún."
                : "No hay cursos disponibles para tu nivel."}
            </div>
          ) : (
            <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
              {displayed.map((c) => (
                <article
                  key={c.id}
                  className="group flex flex-col rounded-xl border border-slate-800 bg-[#12121A] overflow-hidden transition-transform duration-200 hover:-translate-y-0.5 hover:border-slate-700"
                >
                  <CourseBanner courseName={c.name} />
                  <div className="flex flex-col gap-3 px-4 pt-3 pb-4">
                    <div>
                      <h3 className="text-[15px] font-semibold text-slate-100 leading-snug">
                        {c.name}
                      </h3>
                      <p className="text-[11px] uppercase tracking-wider text-slate-500 mt-1">
                        {c.block}
                      </p>
                    </div>

                    {tab === "explore" && (
                      <div className="flex items-center justify-between gap-2 pt-1">
                        {c.enrolled ? (
                          <Button
                            size="sm"
                            onClick={() => handlePractice(c.id)}
                            className="w-full"
                          >
                            Practicar →
                          </Button>
                        ) : (
                          <Button
                            size="sm"
                            onClick={() => enrollMutation.mutate(c.id)}
                            loading={enrollMutation.isPending}
                            className="w-full"
                          >
                            Matricularme
                          </Button>
                        )}
                      </div>
                    )}

                    {tab === "enrolled" && (
                      <div className="flex items-center justify-between gap-2 pt-1">
                        <Button
                          size="sm"
                          onClick={() => handlePractice(c.id)}
                        >
                          Practicar →
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => unenrollMutation.mutate(c.id)}
                          loading={unenrollMutation.isPending}
                        >
                          Salir
                        </Button>
                      </div>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
