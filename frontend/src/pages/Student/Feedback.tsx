/**
 * pages/Student/Feedback.tsx
 * ===========================
 * Centro de retroalimentación del estudiante: lista los procedimientos
 * enviados y, cuando el docente los valida, muestra el puntaje, comentario
 * y reacción de KatIA según el resultado.
 */

import { useQuery } from "@tanstack/react-query";
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

const STATUS_LABEL: Record<StatusKind, string> = {
  pending: "En cola",
  ai_reviewed: "Revisado por IA",
  validated: "Calificado",
  unknown: "—",
};

const STATUS_TONE: Record<StatusKind, string> = {
  pending: "bg-slate-700/60 text-slate-300",
  ai_reviewed: "bg-amber-900/40 text-amber-300",
  validated: "bg-emerald-900/40 text-emerald-300",
  unknown: "bg-slate-700/60 text-slate-400",
};

function katiaForScore(score: number): {
  gif: string;
  message: string;
  ringTone: string;
} {
  if (score >= 91) {
    return {
      gif: "/katia/correcto_compressed.gif",
      message: "¡Excelente trabajo! Tu procedimiento está muy bien resuelto. Sigue así.",
      ringTone: "ring-emerald-500/40",
    };
  }
  if (score >= 60) {
    return {
      gif: "/katia/errores_compressed.gif",
      message:
        "Vas bien, pero hay detalles que pulir. Revisa los pasos donde te marcaron y vuelve a intentarlo.",
      ringTone: "ring-amber-500/40",
    };
  }
  return {
    gif: "/katia/errores_compressed.gif",
    message:
      "Necesitamos repasar este tema juntas. Vuelve a la teoría y prueba un ejercicio más sencillo antes de reintentar.",
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

function ValidatedCard({ row }: { row: ProcedureSubmissionRow }) {
  const score = row.final_score ?? row.teacher_score ?? 0;
  const katia = katiaForScore(score);
  const delta = row.elo_delta ?? 0;
  return (
    <article className="rounded-xl border border-slate-800 bg-[#12121A] overflow-hidden">
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
                Ejercicio · {row.item_id}
              </p>
              <p className="text-sm text-slate-300 truncate">
                {row.item_content || "Procedimiento manuscrito"}
              </p>
            </div>
            <ScorePill score={score} />
          </header>
          <p className="text-sm text-slate-300 leading-relaxed">{katia.message}</p>
          {row.teacher_feedback && (
            <blockquote className="text-sm text-slate-400 bg-slate-900/60 rounded-lg px-3 py-2">
              <span className="block text-[11px] uppercase tracking-wider text-slate-500 mb-0.5">
                Comentario del docente
              </span>
              {row.teacher_feedback}
            </blockquote>
          )}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
            <span>
              ELO:{" "}
              <span className={delta >= 0 ? "text-emerald-400" : "text-rose-400"}>
                {delta >= 0 ? "+" : ""}
                {delta.toFixed(1)}
              </span>
            </span>
            {row.reviewed_at && <span>Calificado el {row.reviewed_at.slice(0, 10)}</span>}
          </div>
        </div>
      </div>
    </article>
  );
}

function PendingCard({ row, kind }: { row: ProcedureSubmissionRow; kind: StatusKind }) {
  return (
    <article className="rounded-xl border border-slate-800 bg-[#12121A] p-4 flex items-center gap-4">
      <div className="shrink-0 w-12 h-12 rounded-lg bg-slate-900 flex items-center justify-center text-slate-500 text-xl">
        ⌛
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[11px] uppercase tracking-wider text-slate-500">
          Ejercicio · {row.item_id}
        </p>
        <p className="text-sm text-slate-300 truncate">
          {row.item_content || "Procedimiento manuscrito"}
        </p>
        <p className="text-xs text-slate-500 mt-1">
          Enviado el {row.submitted_at?.slice(0, 10) ?? "—"}
          {row.ai_proposed_score != null && kind === "ai_reviewed" && (
            <>
              {" · "}
              <span className="text-amber-400/80">
                IA sugiere {Math.round(row.ai_proposed_score)}
              </span>
            </>
          )}
        </p>
      </div>
      <span className={`text-[11px] px-2 py-1 rounded-full ${STATUS_TONE[kind]}`}>
        {STATUS_LABEL[kind]}
      </span>
    </article>
  );
}

export function Feedback() {
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
        <p className="text-sm text-rose-400">No pude cargar tus procedimientos. Reintenta.</p>
      </div>
    );
  }

  if (submissions.length === 0) {
    return (
      <div className="max-w-3xl mx-auto py-12 px-4 text-center space-y-3">
        <p className="text-slate-300 text-base">Aún no enviaste ningún procedimiento.</p>
        <p className="text-sm text-slate-500">
          Sube una foto desde la sección <strong className="text-slate-300">Procedimientos</strong>{" "}
          y aquí verás la retroalimentación de tu docente.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-6 px-4 space-y-4">
      <header className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-100">Retroalimentación</h2>
        <p className="text-xs text-slate-500">{submissions.length} envío(s)</p>
      </header>
      <div className="space-y-3">
        {submissions.map((row) => {
          const kind = classifyStatus(row.status);
          if (kind === "validated") return <ValidatedCard key={row.submission_id} row={row} />;
          return <PendingCard key={row.submission_id} row={row} kind={kind} />;
        })}
      </div>
    </div>
  );
}
