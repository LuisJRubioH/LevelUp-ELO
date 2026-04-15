/**
 * pages/Teacher/Procedures.tsx
 * =============================
 * Cola de procedimientos matemáticos pendientes de revisión y calificación.
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { teacherApi } from "../../api/teacher";
import type { PendingProcedure, GradeResult } from "../../api/teacher";
import { Button } from "../../components/ui/Button";

function ProcedureImageViewer({ submissionId }: { submissionId: number }) {
  const { data: imageUrl, isLoading, isError } = useQuery({
    queryKey: ["procedure-image", submissionId],
    queryFn: () => teacherApi.procedureImage(submissionId),
    staleTime: Infinity, // imagen no cambia
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-40 bg-slate-900 rounded-lg border border-slate-700">
        <span className="text-slate-400 text-sm animate-pulse">Cargando imagen...</span>
      </div>
    );
  }

  if (isError || !imageUrl) {
    return (
      <div className="flex items-center justify-center h-24 bg-slate-900 rounded-lg border border-slate-700">
        <span className="text-slate-500 text-xs">Imagen no disponible</span>
      </div>
    );
  }

  return (
    <img
      src={imageUrl}
      alt="Procedimiento del estudiante"
      className="w-full rounded-lg border border-slate-600 object-contain max-h-96"
    />
  );
}

function ScoreSlider({
  value,
  onChange,
}: {
  value: number;
  onChange: (v: number) => void;
}) {
  const color =
    value >= 91 ? "text-green-400" : value >= 60 ? "text-yellow-400" : "text-red-400";
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <label className="text-xs text-slate-400">Puntaje (0–100)</label>
        <span className={`text-lg font-bold ${color}`}>{value}</span>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        step={1}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-violet-500"
      />
      <div className="flex justify-between text-xs text-slate-600">
        <span>0 — Incompleto</span>
        <span>50 — Básico</span>
        <span>100 — Perfecto</span>
      </div>
    </div>
  );
}

function ProcedureCard({ proc }: { proc: PendingProcedure }) {
  const qc = useQueryClient();
  const [score, setScore] = useState(proc.ai_score ? Math.round(proc.ai_score) : 70);
  const [feedback, setFeedback] = useState("");
  const [result, setResult] = useState<GradeResult | null>(null);
  const [showImage, setShowImage] = useState(false);

  const gradeMutation = useMutation({
    mutationFn: () => teacherApi.gradeProcedure(proc.submission_id, score, feedback || undefined),
    onSuccess: (res) => {
      setResult(res);
      qc.invalidateQueries({ queryKey: ["teacher-procedures"] });
    },
  });

  if (result) {
    const delta = result.elo_delta;
    return (
      <div className="bg-slate-800 border border-green-700/50 rounded-xl p-4 space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-green-400">✓</span>
          <span className="text-sm text-slate-300 font-medium">
            Procedimiento de <strong className="text-white">{proc.student_username}</strong> calificado
          </span>
        </div>
        <div className="text-sm text-slate-400">
          Puntaje: <strong className="text-white">{result.teacher_score}</strong>
          {" · "}
          Delta ELO:{" "}
          <span className={delta >= 0 ? "text-green-400" : "text-red-400"}>
            {delta >= 0 ? "+" : ""}
            {delta.toFixed(1)}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <span className="text-sm font-semibold text-white">{proc.student_username}</span>
          <span className="text-xs text-slate-500 ml-2">#{proc.submission_id}</span>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-500">Subido</div>
          <div className="text-xs text-slate-400">{proc.created_at.slice(0, 10)}</div>
        </div>
      </div>

      {/* Ítem */}
      {proc.item_content && (
        <div className="bg-slate-900 rounded-lg px-3 py-2 text-xs text-slate-400 border border-slate-700 line-clamp-2">
          <span className="text-slate-500 mr-1">Ejercicio:</span>
          {proc.item_content}
        </div>
      )}

      {/* Visor de imagen */}
      {proc.has_image && (
        <div>
          <button
            onClick={() => setShowImage((v) => !v)}
            className="text-xs text-violet-400 hover:text-violet-300 transition-colors"
          >
            {showImage ? "▲ Ocultar imagen" : "🖼️ Ver imagen del procedimiento"}
          </button>
          {showImage && <div className="mt-2"><ProcedureImageViewer submissionId={proc.submission_id} /></div>}
        </div>
      )}

      {/* Score propuesto por IA */}
      {proc.ai_score !== null && (
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-500">Score propuesto por IA:</span>
          <span className="text-violet-300 font-semibold">{proc.ai_score.toFixed(0)}</span>
          <span className="text-slate-600 italic">(solo referencia — no afecta ELO)</span>
        </div>
      )}

      {/* Formulario de calificación */}
      <div className="border-t border-slate-700 pt-3 space-y-3">
        <ScoreSlider value={score} onChange={setScore} />
        <div>
          <label className="block text-xs text-slate-400 mb-1">
            Comentario para el estudiante (opcional)
          </label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            rows={2}
            placeholder="Escribe un comentario de retroalimentación..."
            className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-violet-500 resize-none"
          />
        </div>

        {gradeMutation.isError && (
          <p className="text-red-400 text-xs">{(gradeMutation.error as Error).message}</p>
        )}

        <Button
          onClick={() => gradeMutation.mutate()}
          loading={gradeMutation.isPending}
          className="w-full"
        >
          Calificar procedimiento
        </Button>
      </div>
    </div>
  );
}

export function TeacherProcedures() {
  const { data: procedures = [], isLoading } = useQuery({
    queryKey: ["teacher-procedures"],
    queryFn: teacherApi.procedures,
    refetchInterval: 30_000, // refrescar cada 30 s
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-400 animate-pulse">Cargando procedimientos...</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-6 px-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Revisión de Procedimientos</h2>
        {procedures.length > 0 && (
          <span className="text-xs bg-violet-700 text-white px-2.5 py-1 rounded-full font-medium">
            {procedures.length} pendiente{procedures.length !== 1 ? "s" : ""}
          </span>
        )}
      </div>

      {procedures.length === 0 ? (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-12 text-center">
          <div className="text-3xl mb-3">✅</div>
          <p className="text-slate-300 font-medium">Sin procedimientos pendientes</p>
          <p className="text-slate-600 text-sm mt-1">Los nuevos envíos de estudiantes aparecerán aquí.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {procedures.map((p) => (
            <ProcedureCard key={p.submission_id} proc={p} />
          ))}
        </div>
      )}
    </div>
  );
}
