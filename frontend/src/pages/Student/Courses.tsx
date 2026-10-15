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
import { PageHeader } from "../../components/ui/PageHeader";
import { useAuthStore } from "../../stores/authStore";
import "./StudentContent.css";

export function Courses() {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const navigate = useNavigate();
  const [tab, setTab] = useState<"explore" | "enrolled" | "code">("explore");
  const [inviteCode, setInviteCode] = useState("");
  const [codeMsg, setCodeMsg] = useState("");
  // Spec 001 FR-028o: a semillero student without a grade has no catalogue. No grade is ever
  // assigned here; their enrolments stay listed.
  const user = useAuthStore((s) => s.user);
  const needsGrade = user?.education_level === "semillero" && !user?.grade;

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
    // Entrar a la materia: gating de diagnóstico → bifurcación Practicar/Mapa.
    navigate(`/student/course/${courseId}`);
  };

  const tabs = [
    { id: "explore" as const, label: t("courses.tabExplore") },
    { id: "enrolled" as const, label: t("courses.tabEnrolled") },
    { id: "code" as const, label: t("courses.tabCode") },
  ];

  const enrolled = courses.filter((c) => c.enrolled);
  // Explorar offers the catalogue only; an invited course lives under Mis matrículas (FR-028l).
  const catalogue = courses.filter((c) => c.in_catalogue !== false);
  const displayed: Course[] = tab === "enrolled" ? enrolled : catalogue;

  return (
    <div className="sp-page-wide">
      <PageHeader eyebrow={t("courses.eyebrow")} title={t("courses.title")} subtitle={t("courses.intro")} />

      {/* Tabs */}
      <div className="view-tabs">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => { setTab(t.id); setCodeMsg(""); }}
            className={tab === t.id ? "on" : ""}
          >
            {t.label}
            {t.id === "enrolled" && enrolled.length > 0 && (
              <span className="ml-1.5 text-xs opacity-70">({enrolled.length})</span>
            )}
          </button>
        ))}
      </div>

      {needsGrade && (
        <p
          role="status"
          className="sp-card text-sm mb-4"
          style={{ borderLeft: "3px solid var(--color-partial)", color: "var(--text)" }}
        >
          {t("courses.gradeRequired")}
        </p>
      )}

      {/* Código de acceso */}
      {tab === "code" && (
        <div className="sp-card space-y-4">
          <p className="sp-dim text-sm">{t("courses.codeIntro")}</p>
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
            <p className="sp-dim text-sm mb-4">{t("courses.exploreIntro")}</p>
          )}
          {tab === "enrolled" && (
            <p className="sp-dim text-sm mb-4">{t("courses.enrolledIntro")}</p>
          )}

          {isLoading ? (
            <CoursesSkeleton />
          ) : displayed.length === 0 ? (
            needsGrade && tab === "explore" ? null : (
              <div className="sp-card sp-empty-text text-center py-12">
                {tab === "enrolled" ? t("courses.noEnrolled") : t("courses.noAvailable")}
              </div>
            )
          ) : (
            <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
              {displayed.map((c) => (
                <article
                  key={c.id}
                  className="sp-card group flex flex-col overflow-hidden transition-transform duration-200 hover:-translate-y-0.5"
                  style={{ padding: 0 }}
                >
                  <CourseBanner courseName={c.name} />
                  <div className="flex flex-col gap-3 px-4 pt-3 pb-4">
                    <div>
                      <h3
                        className="leading-snug"
                        style={{ color: "var(--text)", margin: 0, fontSize: 15, fontWeight: 600 }}
                      >
                        {c.name}
                      </h3>
                      <p className="sp-mute text-[11px] uppercase tracking-wider mt-1">
                        {c.block}
                      </p>
                      {c.in_catalogue === false && (
                        <p className="text-[11px] mt-1" style={{ color: "var(--color-partial)" }}>
                          {t("courses.byInvitation")}
                        </p>
                      )}
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
                        <div className="flex items-center gap-2">
                          <Button size="sm" onClick={() => handlePractice(c.id)}>
                            {t("courses.practice")}
                          </Button>
                          {c.diagnostic_done && c.block !== "Concursos" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => navigate(`/student/course/${c.id}/map`)}
                            >
                              🗺️ Mapa
                            </Button>
                          )}
                        </div>
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
