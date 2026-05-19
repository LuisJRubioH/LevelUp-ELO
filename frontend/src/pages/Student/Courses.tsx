/**
 * pages/Student/Courses.tsx
 * ==========================
 * Catálogo de cursos: explorar + practicar, gestionar matrículas, acceso por código.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { studentApi, type Course } from "../../api/student";
import { Button } from "../../components/ui/Button";
import { CoursesSkeleton } from "../../components/ui/Skeleton";
import { CourseBanner } from "../../components/CourseCard/CourseBanner";
import { usePracticeStore } from "../../stores/practiceStore";

export function Courses() {
  const { t } = useTranslation();
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
      setCodeMsg(`✅ ${t("courses.codeActivated", { course: data.course_id })}`);
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
    { id: "explore" as const, label: t("courses.tabExplore") },
    { id: "enrolled" as const, label: t("courses.tabEnrolled") },
    { id: "code" as const, label: t("courses.tabCode") },
  ];

  const enrolled = courses.filter((c) => c.enrolled);
  const displayed: Course[] = tab === "enrolled" ? enrolled : courses;

  return (
    <div className="max-w-5xl mx-auto py-6 px-4">
      <h2 className="text-xl font-bold text-slate-100 mb-6">{t("courses.title")}</h2>

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
                : "text-slate-400 hover:text-slate-100",
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
          <p className="text-sm text-slate-400">{t("courses.codeIntro")}</p>
          <div className="flex gap-3">
            <input
              type="text"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value.trim().toUpperCase())}
              placeholder={t("courses.codePlaceholder")}
              className="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-100 focus:outline-none focus:border-violet-500"
            />
            <Button
              onClick={() => codeMutation.mutate(inviteCode)}
              loading={codeMutation.isPending}
              disabled={!inviteCode}
            >
              {t("courses.accessButton")}
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
            <p className="text-sm text-slate-400 mb-4">{t("courses.exploreIntro")}</p>
          )}
          {tab === "enrolled" && (
            <p className="text-sm text-slate-400 mb-4">{t("courses.enrolledIntro")}</p>
          )}

          {isLoading ? (
            <CoursesSkeleton />
          ) : displayed.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              {tab === "enrolled" ? t("courses.noEnrolled") : t("courses.noAvailable")}
            </div>
          ) : (
            <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
              {displayed.map((c) => (
                <article
                  key={c.id}
                  className="group flex flex-col rounded-xl border border-slate-800 bg-[var(--surface)] overflow-hidden transition-transform duration-200 hover:-translate-y-0.5 hover:border-slate-700"
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
                            {t("courses.practice")}
                          </Button>
                        ) : (
                          <Button
                            size="sm"
                            onClick={() => enrollMutation.mutate(c.id)}
                            loading={enrollMutation.isPending}
                            className="w-full"
                          >
                            {t("courses.enroll")}
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
                          {t("courses.practice")}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => unenrollMutation.mutate(c.id)}
                          loading={unenrollMutation.isPending}
                        >
                          {t("courses.unenroll")}
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
