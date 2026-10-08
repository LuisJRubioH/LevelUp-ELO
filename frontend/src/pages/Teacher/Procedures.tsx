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
import { teacherApi, type PendingProcedure } from "../../api/teacher";

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

/* ── visor de imagen ─────────────────────────────────────────────────────── */
function ProcedureImage({ submissionId }: { submissionId: number }) {
  const { data: url, isLoading, isError } = useQuery({
    queryKey: ["procedure-image", submissionId],
    queryFn: () => teacherApi.procedureImage(submissionId),
    staleTime: Infinity,
  });
  if (isLoading) return <div className="pd-image-box">Cargando imagen…</div>;
  if (isError || !url) return <div className="pd-image-box">Imagen no disponible</div>;
  return <img className="pd-image" src={url} alt="Procedimiento manuscrito del estudiante" />;
}

/* ── detalle ─────────────────────────────────────────────────────────────── */
function ProcedureDetail({ proc }: { proc: PendingProcedure }) {
  const qc = useQueryClient();
  const [score, setScore] = useState(proc.ai_score != null ? Math.round(proc.ai_score) : 70);
  const [feedback, setFeedback] = useState("");

  // resetear al cambiar de envío
  useEffect(() => {
    setScore(proc.ai_score != null ? Math.round(proc.ai_score) : 70);
    setFeedback("");
  }, [proc.submission_id, proc.ai_score]);

  const gradeMutation = useMutation({
    mutationFn: () => teacherApi.gradeProcedure(proc.submission_id, score, feedback || undefined),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["teacher-procedures"] }),
  });

  const gc = gradeColor(score);
  const presets = [0, 60, 80, 100];

  return (
    <div className="proc-detail">
      <div className="pd-head">
        <div className="pd-htop">
          <span className="pd-chip">📝 {proc.item_id}</span>
          <span className="pd-when">{proc.created_at.slice(0, 10)}</span>
        </div>
        <div className="pd-who">
          <span className="av" style={{ background: avaFor(proc.student_username) }}>
            {initials(proc.student_username)}
          </span>
          <div>
            <b>{proc.student_username}</b>
            <span>Envío #{proc.submission_id}</span>
          </div>
        </div>
      </div>

      <div className="pd-body">
        {proc.item_content && (
          <>
            <span className="pd-lbl">Ejercicio</span>
            <div className="pd-problem">
              <p>{proc.item_content}</p>
            </div>
          </>
        )}

        <span className="pd-lbl">Procedimiento del estudiante</span>
        {proc.has_image ? (
          <ProcedureImage submissionId={proc.submission_id} />
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
            <p>
              Puntaje sugerido por la IA. Es solo orientativo —{" "}
              <strong>no afecta el ELO</strong>; la nota oficial es la que tú asignes.
            </p>
          </div>
        )}

        <div
          className="grade-panel"
          style={{ ["--gc"]: gc, ["--pct"]: score } as React.CSSProperties}
        >
          <div className="gp-head">
            <h4>Calificación</h4>
          </div>
          <div className="gp-main">
            <div className="gp-dial">
              <div className="gp-num">
                <b>{score}</b>
                <span>/ 100</span>
              </div>
            </div>
            <div className="gp-ctrl">
              <div className="gp-judge" style={{ color: gc }}>
                {judgeLabel(score)}
              </div>
              <div className="gp-slider-row">
                <button
                  className="gp-step"
                  onClick={() => setScore((s) => Math.max(0, s - 1))}
                  disabled={score <= 0}
                  aria-label="Bajar"
                >
                  −
                </button>
                <input
                  type="range"
                  min={0}
                  max={100}
                  step={1}
                  value={score}
                  onChange={(e) => setScore(Number(e.target.value))}
                  aria-label="Calificación"
                />
                <button
                  className="gp-step"
                  onClick={() => setScore((s) => Math.min(100, s + 1))}
                  disabled={score >= 100}
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
          <button className="btn-approve" onClick={() => gradeMutation.mutate()} disabled={gradeMutation.isPending}>
            {gradeMutation.isPending ? "Guardando…" : `Guardar calificación · ${score}`}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── root ────────────────────────────────────────────────────────────────── */
export function TeacherProcedures() {
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const { data: procedures = [], isLoading } = useQuery({
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

  return (
    <>
      <div className="tc-head">
        <div className="ttl">
          <h1>Procedimientos</h1>
          <p>Revisa los desarrollos a mano de tus estudiantes y asigna la calificación oficial.</p>
        </div>
      </div>

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
                  <span className="av" style={{ background: avaFor(p.student_username) }}>
                    {initials(p.student_username)}
                  </span>
                  <div className="pq-id">
                    <b>{p.student_username}</b>
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
            <ProcedureDetail key={selected.submission_id} proc={selected} />
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
    </>
  );
}
