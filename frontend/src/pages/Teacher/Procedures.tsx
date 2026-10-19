/**
 * pages/Teacher/Procedures.tsx — Procedimientos (rediseño)
 * ========================================================
 * Portado de docs/redesign/source/teacher-procedures.jsx, adaptado a la data
 * real: cola de envíos pendientes (teacherApi.procedures) + detalle con la
 * imagen manuscrita (procedureImage), veredicto de IA (ai_score, no afecta
 * ELO) y panel de calificación (slider + presets + feedback → gradeProcedure).
 * Los "pasos/rúbrica" del diseño eran mock y no existen en la data real.
 */

import { useEffect, useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { teacherApi, type GradeResult, type PendingProcedure } from "../../api/teacher";
import { ApiError } from "../../api/client";
import { MathText } from "../../components/Math/MathContent";

const AVAS = [
  "linear-gradient(140deg,#8b5cf6,#6366f1)",
  "linear-gradient(140deg,#2dd4bf,#0ea5e9)",
  "linear-gradient(140deg,#f59e0b,#ef4444)",
  "linear-gradient(140deg,#ec4899,#8b5cf6)",
  "linear-gradient(140deg,#10b981,#22d3ee)",
  "linear-gradient(140deg,#f43f5e,#f59e0b)",
];
const initials = (n: string) =>
  n.split(/[\s_.]+/).filter(Boolean).slice(0, 2).map((w) => w[0] ?? "").join("").toUpperCase() ||
  n.slice(0, 2).toUpperCase();
const avaFor = (n: string) => AVAS[(n.charCodeAt(0) + n.length) % AVAS.length];
const gradeColor = (v: number) => (v >= 91 ? "#34d399" : v >= 60 ? "#fbbf24" : "#f87171");
const judgeLabel = (v: number) => (v >= 91 ? "Excelente" : v >= 60 ? "Aceptable" : "Necesita refuerzo");

/* ── visor del envío: foto o PDF, tal como lo subió el estudiante ─────────── */
function ProcedureImage({ submissionId, reviewRound }: { submissionId: number; reviewRound?: number }) {
  // Spec 001 FR-024l: a resubmission is a new file under the same id — cached per review round.
  const { data: file, isLoading, isError } = useQuery({
    queryKey: ["procedure-image", submissionId, reviewRound ?? 1],
    queryFn: () => teacherApi.procedureImage(submissionId),
    staleTime: Infinity,
  });
  if (isLoading) return <div className="pd-image-box">Cargando imagen…</div>;
  if (isError || !file) return <div className="pd-image-box">Imagen no disponible</div>;
  if (file.type === "application/pdf") {
    // Un PDF en <img> se ve roto: va en el visor de documentos del navegador.
    return (
      <div className="pd-pdf">
        <object data={file.url} type="application/pdf" aria-label="Procedimiento del estudiante (PDF)">
          <p className="pd-image-box">Este navegador no muestra el PDF aquí.</p>
        </object>
        <a href={file.url} target="_blank" rel="noopener noreferrer">Abrir el PDF</a>
      </div>
    );
  }
  return <img className="pd-image" src={file.url} alt="Procedimiento manuscrito del estudiante" />;
}

/* ── copias detectadas (spec 001 FR-024i) ─────────────────────────────────── */
// Calificadas con 0 por el sistema: nunca se nombra a quien subió el archivo primero, que
// puede ser de otro grupo.
function CopiesPanel() {
  const { data: copies = [] } = useQuery({
    queryKey: ["teacher-procedure-copies"],
    queryFn: () => teacherApi.procedureCopies(),
    refetchInterval: 60_000,
  });
  if (copies.length === 0) return null;
  return (
    <section className="panel" aria-labelledby="proc-copies-title" style={{ marginTop: 16 }}>
      <h2 id="proc-copies-title" style={{ fontSize: 15, marginBottom: 8 }}>
        Copias detectadas
      </h2>
      <p style={{ fontSize: 13, opacity: 0.75, marginBottom: 10 }}>
        Archivos que otro estudiante ya había entregado. Últimos 30 días.
      </p>
      <ul style={{ display: "grid", gap: 8 }}>
        {copies.map((c) => (
          <li key={c.submission_id} className="pq-card" style={{ cursor: "default" }}>
            <div className="pq-top">
              <span className="av" style={{ background: avaFor(c.student_name) }}>
                {initials(c.student_name)}
              </span>
              <div className="pq-id">
                <b>{c.student_name}</b>
                <span>{c.item_id}</span>
              </div>
            </div>
            <div className="pq-foot-row">
              <span className="pq-status">Calificado 0 automáticamente</span>
              <span className="pq-when">{c.reviewed_at?.slice(0, 10) ?? ""}</span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

const signed = (v: number) => (v > 0 ? `+${v}` : v < 0 ? `−${Math.abs(v)}` : "0");

/* ── detalle ─────────────────────────────────────────────────────────────── */
function ProcedureDetail({
  proc,
  onGraded,
}: {
  proc: PendingProcedure;
  onGraded: (result: GradeResult, studentName: string) => void;
}) {
  const qc = useQueryClient();
  // Spec 006 FR-051: the grade starts empty; the AI score is shown beside it, never pre-filled.
  const [score, setScore] = useState<number | null>(null);
  const [feedback, setFeedback] = useState("");

  // resetear al cambiar de envío (o de ronda de revisión)
  useEffect(() => {
    setScore(null);
    setFeedback("");
  }, [proc.submission_id, proc.review_round]);

  const gradeMutation = useMutation({
    // Spec 001 FR-024g: the review round travels with the grade, so a retry cannot grade twice.
    mutationFn: () =>
      teacherApi.gradeProcedure(proc.submission_id, score ?? 0, feedback || undefined, proc.review_round),
    onSuccess: (result) => {
      onGraded(result, proc.student_name);
      qc.invalidateQueries({ queryKey: ["teacher-procedures"] });
    },
    // Spec 001 FR-024l: the student resubmitted while this review was open — the queue reloads
    // with the new submission and the server's message stays on screen.
    onError: (error) => {
      if (error instanceof ApiError && error.status === 409) {
        qc.invalidateQueries({ queryKey: ["teacher-procedures"] });
      }
    },
  });

  const gc = score == null ? "var(--mute)" : gradeColor(score);
  const nudge = (step: number) => setScore((s) => Math.min(100, Math.max(0, (s ?? 50) + step)));
  const presets = [0, 60, 80, 100];

  return (
    <div className="proc-detail">
      <div className="pd-head">
        <div className="pd-htop">
          <span className="pd-chip">📝 {proc.item_id}</span>
          <span className="pd-when">{proc.created_at.slice(0, 10)}</span>
        </div>
        <div className="pd-who">
          <span className="av" style={{ background: avaFor(proc.student_name) }}>
            {initials(proc.student_name)}
          </span>
          <div>
            <b>{proc.student_name}</b>
            <span>Envío #{proc.submission_id}</span>
          </div>
        </div>
      </div>

      <div className="pd-body">
        {proc.item_content && (
          <>
            <span className="pd-lbl">Ejercicio</span>
            <div className="pd-problem">
              <p><MathText text={proc.item_content} /></p>
            </div>
          </>
        )}

        <span className="pd-lbl">Procedimiento del estudiante</span>
        {proc.has_image ? (
          <ProcedureImage submissionId={proc.submission_id} reviewRound={proc.review_round} />
        ) : (
          <div className="pd-image-box">El estudiante no adjuntó imagen.</div>
        )}

        {proc.ai_score != null && (
          <div className="ai-verdict">
            <div className="av-head">
              <span className="av-dot" />
              <b>Revisión de KatIA</b>
              <span className="av-score">{Math.round(proc.ai_score)}</span>
            </div>
            {proc.ai_feedback && <p className="av-feedback">{proc.ai_feedback}</p>}
            <p>
              Puntaje sugerido por la IA. Es solo orientativo —{" "}
              <strong>no afecta el ELO</strong>; la nota oficial es la que tú asignes.
            </p>
          </div>
        )}

        <div
          className="grade-panel"
          style={{ ["--gc"]: gc, ["--pct"]: score ?? 0 } as React.CSSProperties}
        >
          <div className="gp-head">
            <h4>Calificación</h4>
          </div>
          <div className="gp-main">
            <div className="gp-dial">
              <div className="gp-num">
                <b>{score ?? "—"}</b>
                <span>/ 100</span>
              </div>
            </div>
            <div className="gp-ctrl">
              <div className="gp-judge" style={{ color: gc }}>
                {score == null ? "Elige una calificación" : judgeLabel(score)}
              </div>
              <div className="gp-slider-row">
                <button
                  className="gp-step"
                  onClick={() => nudge(-1)}
                  disabled={score === 0}
                  aria-label="Bajar"
                >
                  −
                </button>
                <input
                  type="range"
                  min={0}
                  max={100}
                  step={1}
                  value={score ?? 50}
                  className={score == null ? "unset" : undefined}
                  onChange={(e) => setScore(Number(e.target.value))}
                  aria-label="Calificación"
                />
                <button
                  className="gp-step"
                  onClick={() => nudge(1)}
                  disabled={score === 100}
                  aria-label="Subir"
                >
                  ＋
                </button>
              </div>
              <div className="gp-presets">
                {presets.map((p) => (
                  <button key={p} className={"gp-chip" + (score === p ? " on" : "")} onClick={() => setScore(p)}>
                    {p}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="pd-actions">
        <textarea
          className="pd-note"
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="Retroalimentación para el estudiante (opcional)…"
        />
        {gradeMutation.isError && (
          <p style={{ color: "#f87171", fontSize: 13, marginBottom: 10 }}>
            {(gradeMutation.error as Error).message}
          </p>
        )}
        <div className="pd-btns">
          <button
            className="btn-approve"
            onClick={() => gradeMutation.mutate()}
            disabled={score == null || gradeMutation.isPending}
          >
            {gradeMutation.isPending
              ? "Guardando…"
              : score == null
                ? "Guardar calificación"
                : `Guardar calificación · ${score}`}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── root ────────────────────────────────────────────────────────────────── */
export function TeacherProcedures() {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  // Spec 001 FR-024f: what the last grading applied to the rating — never the computed delta.
  const [lastGraded, setLastGraded] = useState<string | null>(null);
  const onGraded = (result: GradeResult, studentName: string) =>
    setLastGraded(
      `Calificación guardada · ${studentName}: efecto en la nota ${signed(result.elo_delta)}`,
    );

  const { data: procedures = [], isLoading, isError, refetch } = useQuery({
    queryKey: ["teacher-procedures"],
    queryFn: () => teacherApi.procedures(),
    refetchInterval: 30_000,
  });

  // auto-seleccionar el primero / mantener selección válida
  useEffect(() => {
    if (procedures.length === 0) {
      setSelectedId(null);
    } else if (selectedId == null || !procedures.some((p) => p.submission_id === selectedId)) {
      setSelectedId(procedures[0].submission_id);
    }
  }, [procedures, selectedId]);

  const selected = useMemo(
    () => procedures.find((p) => p.submission_id === selectedId) ?? null,
    [procedures, selectedId]
  );

  if (isLoading) {
    return (
      <div className="tc-soon">
        <div className="box">
          <div className="em-ic">⏳</div>
          <h2>Cargando procedimientos…</h2>
        </div>
      </div>
    );
  }
  // A failed load is not an empty queue: «¡Al día!» would hide submissions waiting for a grade.
  if (isError && procedures.length === 0) {
    return (
      <div className="tc-soon">
        <div className="box" role="alert">
          <div className="em-ic">⚠️</div>
          <h2>No pudimos cargar los procedimientos</h2>
          <p>Revisa tu conexión e inténtalo de nuevo.</p>
          <button type="button" className="btn-pri" onClick={() => refetch()}>
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="tc-head">
        <div className="ttl">
          <h1>Procedimientos</h1>
          <p>Revisa los desarrollos a mano de tus estudiantes y asigna la calificación oficial.</p>
        </div>
      </div>

      {lastGraded && (
        <p role="status" className="proc-graded-note" style={{ margin: "0 0 12px", fontSize: 14 }}>
          {lastGraded}
        </p>
      )}

      {procedures.length === 0 ? (
        <div className="panel">
          <div className="empty">
            <div className="em-ic">✅</div>
            <p>No hay procedimientos pendientes de revisión. ¡Al día!</p>
          </div>
        </div>
      ) : (
        <div className="proc-layout">
          <div className="proc-queue">
            {procedures.map((p) => (
              <button
                key={p.submission_id}
                className={"pq-card" + (p.submission_id === selectedId ? " on" : "")}
                onClick={() => setSelectedId(p.submission_id)}
              >
                <div className="pq-top">
                  <span className="av" style={{ background: avaFor(p.student_name) }}>
                    {initials(p.student_name)}
                  </span>
                  <div className="pq-id">
                    <b>{p.student_name}</b>
                    <span>{p.item_id}</span>
                  </div>
                  {p.ai_score != null && <span className="pq-ai">{Math.round(p.ai_score)}</span>}
                </div>
                <div className="pq-foot-row">
                  <span className="pq-status">Pendiente</span>
                  <span className="pq-when">{p.created_at.slice(0, 10)}</span>
                </div>
              </button>
            ))}
          </div>

          {selected ? (
            <ProcedureDetail key={selected.submission_id} proc={selected} onGraded={onGraded} />
          ) : (
            <div className="proc-detail empty">
              <div>
                <div className="em-ic">📝</div>
                <p>Selecciona un envío de la cola para revisarlo.</p>
              </div>
            </div>
          )}
        </div>
      )}

      <CopiesPanel />
    </>
  );
}
