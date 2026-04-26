/**
 * pages/Student/ProcedureUpload.tsx
 * ===================================
 * Subida de procedimiento para preguntas abiertas / ejercicios externos.
 * Para procedimientos vinculados a preguntas de selección múltiple,
 * el estudiante usa la sección integrada en Practice.tsx.
 */

import { useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { KatIAAvatar } from "../../components/KatIA/KatIAAvatar";
import { Button } from "../../components/ui/Button";
import { studentApi, type ProcedureReview } from "../../api/student";
import { apiClient } from "../../api/client";
import { useSettingsStore } from "../../stores/settingsStore";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "application/pdf"];
const MAX_SIZE_MB = 10;

type Stage = "idle" | "analyzing" | "result" | "sent";

function scoreColor(score: number): string {
  if (score < 40) return "text-rose-400";
  if (score < 70) return "text-amber-400";
  return "text-emerald-400";
}

function katiaMessage(score: number): string {
  if (score >= 91)
    return "Miau-ravilloso! Tu procedimiento es una obra de arte. Mis procesadores ronronean de alegría.";
  if (score >= 60)
    return "Casi purrr-fecto! Solo nos faltó afinar un detallito. Revisa los comentarios abajo.";
  return "Detecto un pequeño enredo en los cables de este procedimiento. Revisa los pasos marcados y vuelve a intentarlo.";
}

export function ProcedureUpload() {
  const fileRef = useRef<HTMLInputElement>(null);
  const { apiKey } = useSettingsStore();

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<string>("");
  const [itemContent, setItemContent] = useState<string>("");
  const [stage, setStage] = useState<Stage>("idle");
  const [error, setError] = useState<string | null>(null);
  const [review, setReview] = useState<ProcedureReview | null>(null);
  const [usedProvider, setUsedProvider] = useState<string>("");

  const { data: courses } = useQuery({
    queryKey: ["student-courses"],
    queryFn: () => studentApi.courses(),
  });

  const { data: aiStatus } = useQuery({
    queryKey: ["ai-status"],
    queryFn: () => studentApi.aiStatus(),
    staleTime: 300_000,
  });

  const enrolled = (courses ?? []).filter((c) => c.enrolled);
  const canAnalyze = !!apiKey || (aiStatus?.available ?? false);

  const handleFile = (f: File) => {
    setError(null);
    setReview(null);
    if (!ALLOWED_TYPES.includes(f.type)) {
      setError(`Tipo no soportado: ${f.type}. Usa JPEG, PNG, WebP o PDF.`);
      return;
    }
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`El archivo supera el límite de ${MAX_SIZE_MB} MB.`);
      return;
    }
    setFile(f);
    if (f.type.startsWith("image/")) setPreview(URL.createObjectURL(f));
    else setPreview(null);
  };

  const resetAll = () => {
    setFile(null);
    setPreview(null);
    setSelectedItem("");
    setItemContent("");
    setStage("idle");
    setReview(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!file || !selectedItem) return;
    setError(null);
    setStage("analyzing");
    try {
      const { review: r, provider } = await studentApi.analyzeProcedure({
        item_id: selectedItem,
        item_content: itemContent,
        api_key: apiKey || undefined,
        file,
      });
      setReview(r);
      setUsedProvider(provider);
      setStage("result");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Error desconocido";
      setError(`No se pudo analizar: ${msg}`);
      setStage("idle");
    }
  };

  const handleSendToTeacher = async (opts?: { withAI?: boolean }) => {
    if (!file || !selectedItem) return;
    setError(null);
    try {
      const fd = new FormData();
      fd.append("item_id", selectedItem);
      fd.append("item_content", itemContent);
      fd.append("file", file);
      if (opts?.withAI && review?.score_procedimiento !== undefined) {
        fd.append("ai_proposed_score", String(review.score_procedimiento));
        fd.append("ai_feedback", review.evaluacion_global ?? "");
      }
      await apiClient.postForm("/api/student/procedure", fd);
      setStage("sent");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Error desconocido";
      setError(`No se pudo enviar: ${msg}`);
    }
  };

  if (stage === "sent") {
    return (
      <div className="max-w-xl mx-auto py-8 px-4 space-y-6">
        <h2 className="text-xl font-bold text-slate-100">Procedimiento enviado</h2>
        <KatIAAvatar
          state="correct"
          message="Recibido! Tu docente revisará tu procedimiento pronto. Sigue practicando."
          size="md"
        />
        <Button variant="secondary" onClick={resetAll} className="w-full">
          Enviar otro
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto py-8 px-4 space-y-6">
      <h2 className="text-xl font-bold text-slate-100">Procedimiento abierto</h2>
      <div className="rounded-xl border border-slate-700/50 bg-[var(--surface)] p-4 space-y-1">
        <p className="text-sm text-slate-300">
          Sube el procedimiento de un ejercicio de desarrollo o pregunta abierta.
        </p>
        <p className="text-xs text-slate-500">
          Si estás respondiendo una pregunta de selección múltiple, usa el botón
          "Subir procedimiento manuscrito" que aparece debajo de la pregunta en la sala de práctica.
        </p>
      </div>

      {/* Identificación del ejercicio */}
      {stage === "idle" && (
        <>
          <div>
            <label className="block text-xs text-slate-400 mb-1.5">
              Identificador del ejercicio <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={selectedItem}
              onChange={(e) => setSelectedItem(e.target.value)}
              placeholder="ej: ejercicio_1, taller_3_p5, parcial_2_p3"
              className="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500"
            />
            {enrolled.length > 0 && (
              <p className="text-xs text-slate-600 mt-1">
                Cursos matriculados: {enrolled.map((c) => c.name).join(", ")}
              </p>
            )}
          </div>

          {canAnalyze && (
            <div>
              <label className="block text-xs text-slate-400 mb-1.5">
                Enunciado del ejercicio (mejora el análisis de la IA)
              </label>
              <textarea
                value={itemContent}
                onChange={(e) => setItemContent(e.target.value)}
                rows={3}
                placeholder="Pega el enunciado del ejercicio para que la IA verifique que tu procedimiento corresponde..."
                className="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-violet-500 resize-none"
              />
            </div>
          )}

          {/* Dropzone */}
          <div
            className={[
              "border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all",
              file
                ? "border-violet-500 bg-violet-900/10"
                : "border-slate-600 hover:border-slate-500 bg-slate-800/50",
            ].join(" ")}
            onClick={() => fileRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              const f = e.dataTransfer.files[0];
              if (f) handleFile(f);
            }}
          >
            {preview ? (
              <img
                src={preview}
                alt="Previsualización"
                className="max-h-64 mx-auto rounded-lg object-contain"
              />
            ) : (
              <div className="space-y-2">
                <div className="text-4xl">📷</div>
                <p className="text-slate-400 text-sm">
                  Arrastra tu imagen aquí o{" "}
                  <span className="text-violet-400 underline">haz clic para seleccionar</span>
                </p>
                <p className="text-xs text-slate-600">
                  JPEG, PNG, WebP o PDF · Máx. {MAX_SIZE_MB} MB
                </p>
              </div>
            )}
            <input
              ref={fileRef}
              type="file"
              accept={ALLOWED_TYPES.join(",")}
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleFile(f);
              }}
            />
          </div>

          {file && (
            <div className="flex items-center gap-3 bg-slate-800 rounded-xl px-4 py-2 border border-slate-700">
              <span className="text-slate-300 text-sm flex-1 truncate">{file.name}</span>
              <span className="text-xs text-slate-500">{(file.size / 1024).toFixed(0)} KB</span>
              <button
                onClick={() => { setFile(null); setPreview(null); }}
                className="text-slate-500 hover:text-red-400 text-xs"
                aria-label="Quitar archivo"
              >
                ✕
              </button>
            </div>
          )}

          {error && (
            <div className="rounded-xl p-3 border border-red-600 bg-red-900/20">
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          {canAnalyze ? (
            <div className="flex flex-col gap-2">
              <Button
                onClick={handleAnalyze}
                disabled={!file || !selectedItem}
                size="lg"
                className="w-full"
              >
                🔬 Analizar con IA
              </Button>
              <button
                onClick={() => handleSendToTeacher()}
                disabled={!file || !selectedItem}
                className="w-full text-xs text-slate-500 hover:text-slate-300 transition-colors disabled:opacity-50"
              >
                O enviar directo al docente sin análisis →
              </button>
            </div>
          ) : (
            <>
              <Button
                onClick={() => handleSendToTeacher()}
                disabled={!file || !selectedItem}
                size="lg"
                className="w-full"
              >
                📤 Enviar al docente
              </Button>
              <p className="text-xs text-slate-500 text-center">
                La revisión automática con IA no está disponible en este momento.
              </p>
            </>
          )}
        </>
      )}

      {/* Estado: analizando */}
      {stage === "analyzing" && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl border border-slate-700 bg-[var(--surface)] p-8 text-center space-y-4"
        >
          <KatIAAvatar state="thinking" size="lg" />
          <p className="text-sm text-slate-300 font-medium">
            KatIA está revisando tu procedimiento…
          </p>
          <p className="text-xs text-slate-500">
            Analizando con rigor matemático. Suele tardar 10–30 s.
          </p>
          <div className="flex justify-center">
            <div className="w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
          </div>
        </motion.div>
      )}

      {/* Estado: resultado */}
      <AnimatePresence>
        {stage === "result" && review && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            className="space-y-4"
          >
            {preview && (
              <img
                src={preview}
                alt="Procedimiento"
                className="max-h-56 mx-auto rounded-lg object-contain border border-slate-700"
              />
            )}

            <KatIAAvatar
              state={
                review.score_procedimiento == null
                  ? "idle"
                  : review.score_procedimiento >= 91
                    ? "correct"
                    : "error"
              }
              message={
                review.score_procedimiento == null
                  ? "La IA revisó tu procedimiento. Revisa los comentarios abajo."
                  : katiaMessage(review.score_procedimiento)
              }
              size="md"
            />

            {review.corresponde_a_pregunta === false && (
              <div className="rounded-xl border border-amber-600 bg-amber-900/20 p-3">
                <p className="text-sm text-amber-300">
                  ⚠️ El procedimiento no corresponde al enunciado proporcionado.
                </p>
              </div>
            )}

            <div className="rounded-2xl border border-slate-700 bg-[var(--surface)] p-5 space-y-4">
              <div className="flex items-baseline justify-between">
                <h3 className="text-sm font-semibold text-slate-200">
                  {usedProvider === "groq"
                    ? "🔬 Revisión Matemática Rigurosa"
                    : "🔍 Retroalimentación de la IA"}
                </h3>
                {review.score_procedimiento != null && (
                  <span
                    className={`text-2xl font-bold ${scoreColor(review.score_procedimiento)}`}
                  >
                    {review.score_procedimiento}/100
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500">
                Nota propuesta por IA — el ELO solo se ajusta con la calificación del profesor.
              </p>

              {review.transcripcion && (
                <details className="group">
                  <summary className="cursor-pointer text-xs text-slate-400 hover:text-slate-200">
                    📝 Transcripción del procedimiento
                  </summary>
                  <p className="mt-2 text-xs text-slate-300 whitespace-pre-wrap">
                    {review.transcripcion}
                  </p>
                </details>
              )}

              {review.pasos && review.pasos.length > 0 && (
                <details>
                  <summary className="cursor-pointer text-xs text-slate-400 hover:text-slate-200">
                    🔢 Pasos analizados ({review.pasos.length})
                  </summary>
                  <ul className="mt-2 space-y-2">
                    {review.pasos.map((p, i) => {
                      const ev = (p.evaluacion ?? "").toLowerCase();
                      const color =
                        ev === "valido"
                          ? "text-emerald-400"
                          : ev.includes("incorrecto")
                            ? "text-rose-400"
                            : "text-amber-400";
                      return (
                        <li
                          key={i}
                          className="text-xs text-slate-300 border-l-2 border-slate-700 pl-3 py-1"
                        >
                          <div className="font-medium text-slate-200">
                            Paso {p.numero ?? i + 1}
                          </div>
                          {p.contenido && (
                            <div className="text-slate-400">{p.contenido}</div>
                          )}
                          <div className={color}>▶ {p.evaluacion}</div>
                          {p.comentario && (
                            <div className="text-slate-500 italic">{p.comentario}</div>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                </details>
              )}

              {review.errores_detectados && review.errores_detectados.length > 0 && (
                <details>
                  <summary className="cursor-pointer text-xs text-rose-400 hover:text-rose-300">
                    ⚠️ Errores detectados ({review.errores_detectados.length})
                  </summary>
                  <ul className="mt-2 space-y-1 text-xs text-slate-300 list-disc list-inside">
                    {review.errores_detectados.map((err, i) => (
                      <li key={i}>{err}</li>
                    ))}
                  </ul>
                </details>
              )}

              {review.saltos_logicos && review.saltos_logicos.length > 0 && (
                <details>
                  <summary className="cursor-pointer text-xs text-amber-400 hover:text-amber-300">
                    🔗 Saltos lógicos ({review.saltos_logicos.length})
                  </summary>
                  <ul className="mt-2 space-y-1 text-xs text-slate-300 list-disc list-inside">
                    {review.saltos_logicos.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </details>
              )}

              <div className="pt-2 border-t border-slate-800 text-xs text-slate-400">
                <strong className="text-slate-300">Resultado final:</strong>{" "}
                {review.resultado_correcto ? "✅ Correcto" : "❌ Incorrecto"}
              </div>
              {review.evaluacion_global && (
                <p className="text-xs text-slate-400">
                  <strong className="text-slate-300">Evaluación global:</strong>{" "}
                  {review.evaluacion_global}
                </p>
              )}
            </div>

            {error && (
              <div className="rounded-xl p-3 border border-red-600 bg-red-900/20">
                <p className="text-sm text-red-300">{error}</p>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-2">
              <Button
                onClick={() => handleSendToTeacher({ withAI: true })}
                size="lg"
                className="flex-1"
              >
                📤 Enviar al docente para validar
              </Button>
              <Button variant="secondary" onClick={resetAll} className="sm:w-auto">
                Subir otro
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
