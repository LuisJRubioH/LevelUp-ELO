/**
 * pages/Student/Feedback.tsx
 * ===========================
 * Centro de retroalimentación del estudiante: lista los procedimientos
 * enviados y, cuando el docente los valida, muestra el puntaje, comentario
 * y reacción de KatIA según el resultado.
 */

import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import type { TFunction } from "i18next";
import { studentApi } from "../../api/student";
import type { ProcedureSubmissionRow } from "../../api/student";

type StatusKind = "pending" | "ai_reviewed" | "validated" | "unknown";

function classifyStatus(s: string): StatusKind {
  const v = s.toLowerCase();
  if (v === "validated_by_teacher" || v === "graded" || v === "validated") return "validated";
  if (v === "pending_teacher_validation" || v === "ai_reviewed") return "ai_reviewed";
  if (v === "pending") return "pending";
  return "unknown";
}

const STATUS_LABEL_KEY: Record<StatusKind, string> = {
  pending: "feedback.statusPending",
  ai_reviewed: "feedback.statusAIReviewed",
  validated: "feedback.statusValidated",
  unknown: "feedback.statusUnknown",
};

const STATUS_TONE: Record<StatusKind, string> = {
  pending: "bg-slate-700/60 text-slate-300",
  ai_reviewed: "bg-amber-900/40 text-amber-300",
  validated: "bg-emerald-900/40 text-emerald-300",
  unknown: "bg-slate-700/60 text-slate-400",
};

function katiaForScore(score: number, t: TFunction): {
  gif: string;
  message: string;
  ringTone: string;
} {
  if (score >= 91) {
    return {
      gif: "/katia/correcto_compressed.gif",
      message: t("feedback.katiaHigh"),
      ringTone: "ring-emerald-500/40",
    };
  }
  if (score >= 60) {
    return {
      gif: "/katia/errores_compressed.gif",
      message: t("feedback.katiaMid"),
      ringTone: "ring-amber-500/40",
    };
  }
  return {
    gif: "/katia/errores_compressed.gif",
    message: t("feedback.katiaLow"),
    ringTone: "ring-rose-500/40",
  };
}

function ScorePill({ score }: { score: number }) {
  const tone =
    score >= 91 ? "text-emerald-300" : score >= 60 ? "text-amber-300" : "text-rose-300";
  return (
    <span className={`font-mono text-2xl font-semibold ${tone}`}>{Math.round(score)}</span>
  );
}

function ValidatedCard({ row, t }: { row: ProcedureSubmissionRow; t: TFunction }) {
  const score = row.final_score ?? row.teacher_score ?? 0;
  const katia = katiaForScore(score, t);
  const delta = row.elo_delta ?? 0;
  return (
    <article className="rounded-xl border border-slate-800 bg-[var(--surface)] overflow-hidden">
      <div className="flex flex-col sm:flex-row gap-4 p-4">
        <div
          className={`shrink-0 w-24 h-24 sm:w-28 sm:h-28 rounded-lg overflow-hidden ring-2 ${katia.ringTone}`}
        >
          <img src={katia.gif} alt="" aria-hidden="true" className="w-full h-full object-cover" />
        </div>
        <div className="flex-1 min-w-0 space-y-2">
          <header className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-[11px] uppercase tracking-wider text-slate-500">
                {t("feedback.exerciseLabel")} · {row.item_id}
              </p>
              <p className="text-sm text-slate-300 truncate">
                {row.item_content || t("feedback.handwrittenProcedure")}
              </p>
            </div>
            <ScorePill score={score} />
          </header>
          <p className="text-sm text-slate-300 leading-relaxed">{katia.message}</p>
          {row.teacher_feedback && (
            <blockquote className="text-sm text-slate-400 bg-slate-900/60 rounded-lg px-3 py-2">
              <span className="block text-[11px] uppercase tracking-wider text-slate-500 mb-0.5">
                {t("feedback.teacherComment")}
              </span>
              {row.teacher_feedback}
            </blockquote>
          )}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
            <span>
              {t("feedback.eloLabel")}:{" "}
              <span className={delta >= 0 ? "text-emerald-400" : "text-rose-400"}>
                {delta >= 0 ? "+" : ""}
                {delta.toFixed(1)}
              </span>
            </span>
            {row.reviewed_at && (
              <span>{t("feedback.gradedOn", { date: row.reviewed_at.slice(0, 10) })}</span>
            )}
          </div>
        </div>
      </div>
    </article>
  );
}

function PendingCard({
  row,
  kind,
  t,
}: {
  row: ProcedureSubmissionRow;
  kind: StatusKind;
  t: TFunction;
}) {
  return (
    <article className="rounded-xl border border-slate-800 bg-[var(--surface)] p-4 flex items-center gap-4">
      <div className="shrink-0 w-12 h-12 rounded-lg bg-slate-900 flex items-center justify-center text-slate-500 text-xl">
        ⌛
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[11px] uppercase tracking-wider text-slate-500">
          {t("feedback.exerciseLabel")} · {row.item_id}
        </p>
        <p className="text-sm text-slate-300 truncate">
          {row.item_content || t("feedback.handwrittenProcedure")}
        </p>
        <p className="text-xs text-slate-500 mt-1">
          {t("feedback.submittedOn", { date: row.submitted_at?.slice(0, 10) ?? "—" })}
          {row.ai_proposed_score != null && kind === "ai_reviewed" && (
            <>
              {" · "}
              <span className="text-amber-400/80">
                {t("feedback.aiSuggests", { score: Math.round(row.ai_proposed_score) })}
              </span>
            </>
          )}
        </p>
      </div>
      <span className={`text-[11px] px-2 py-1 rounded-full ${STATUS_TONE[kind]}`}>
        {t(STATUS_LABEL_KEY[kind])}
      </span>
    </article>
  );
}

export function Feedback() {
  const { t } = useTranslation();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["my-procedures"],
    queryFn: () => studentApi.myProcedures(),
    refetchInterval: 30_000,
  });

  const submissions = data?.submissions ?? [];

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto py-8 px-4">
        <div className="space-y-3">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="h-24 rounded-xl bg-slate-800/50 animate-pulse"
              aria-hidden="true"
            />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="max-w-3xl mx-auto py-8 px-4">
        <p className="text-sm text-rose-400">{t("feedback.loadError")}</p>
      </div>
    );
  }

  if (submissions.length === 0) {
    return (
      <div className="max-w-3xl mx-auto py-12 px-4 text-center space-y-3">
        <p className="text-slate-300 text-base">{t("feedback.emptyTitle")}</p>
        <p className="text-sm text-slate-500">
          {t("feedback.emptyHint")}{" "}
          <strong className="text-slate-300">{t("feedback.emptySection")}</strong>{" "}
          {t("feedback.emptyHintSuffix")}
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-6 px-4 space-y-4">
      <header className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-100">{t("feedback.title")}</h2>
        <p className="text-xs text-slate-500">
          {t("feedback.submissionsCount", { count: submissions.length })}
        </p>
      </header>
      <div className="space-y-3">
        {submissions.map((row) => {
          const kind = classifyStatus(row.status);
          if (kind === "validated") return <ValidatedCard key={row.submission_id} row={row} t={t} />;
          return <PendingCard key={row.submission_id} row={row} kind={kind} t={t} />;
        })}
      </div>
    </div>
  );
}
