/**
 * components/Procedure/ProcedureSection.tsx
 * ==========================================
 * Sección colapsable de subida de procedimiento manuscrito.
 * Se integra en Practice.tsx vinculada al ítem activo (como V1).
 * Máquina de estados: idle → analyzing → result → sent.
 */

import { useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import { KatIAAvatar } from "../KatIA/KatIAAvatar";
import { Button } from "../ui/Button";
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

interface ProcedureSectionProps {
  itemId: string;
  itemContent: string;
}

export function ProcedureSection({ itemId, itemContent }: ProcedureSectionProps) {
  const { t } = useTranslation();
  const fileRef = useRef<HTMLInputElement>(null);
  const { apiKey } = useSettingsStore();

  const katiaMessage = (score: number): string => {
    if (score >= 91) return t("procedureSection.katiaHigh");
    if (score >= 60) return t("procedureSection.katiaMid");
    return t("procedureSection.katiaLow");
  };

  const [expanded, setExpanded] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [stage, setStage] = useState<Stage>("idle");
  const [error, setError] = useState<string | null>(null);
  const [review, setReview] = useState<ProcedureReview | null>(null);
  const [usedProvider, setUsedProvider] = useState<string>("");

  const { data: aiStatus } = useQuery({
    queryKey: ["ai-status"],
    queryFn: () => studentApi.aiStatus(),
    staleTime: 300_000,
  });

  const canAnalyze = !!apiKey || (aiStatus?.available ?? false);

  const handleFile = (f: File) => {
    setError(null);
    setReview(null);
    if (!ALLOWED_TYPES.includes(f.type)) {
      setError(t("procedureSection.typeNotSupported", { type: f.type }));
      return;
    }
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(t("procedureSection.fileTooBig", { max: MAX_SIZE_MB }));
      return;
    }
    setFile(f);
    if (f.type.startsWith("image/")) setPreview(URL.createObjectURL(f));
    else setPreview(null);
  };

  const resetAll = () => {
    setFile(null);
    setPreview(null);
    setStage("idle");
    setReview(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setError(null);
    setStage("analyzing");
    try {
      const { review: r, provider } = await studentApi.analyzeProcedure({
        item_id: itemId,
        item_content: itemContent,
        api_key: apiKey || undefined,
        file,
      });
      setReview(r);
      setUsedProvider(provider);
      setStage("result");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : t("procedureSection.unknownError");
      setError(t("procedureSection.couldNotAnalyze", { msg }));
      setStage("idle");
    }
  };

  const handleSendToTeacher = async (opts?: { withAI?: boolean }) => {
    if (!file) return;
    setError(null);
    try {
      const fd = new FormData();
      fd.append("item_id", itemId);
      fd.append("item_content", itemContent);
      fd.append("file", file);
      if (opts?.withAI && review?.score_procedimiento !== undefined) {
        fd.append("ai_proposed_score", String(review.score_procedimiento));
        fd.append("ai_feedback", review.evaluacion_global ?? "");
      }
      await apiClient.postForm("/api/student/procedure", fd);
      setStage("sent");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : t("procedureSection.unknownError");
      setError(t("procedureSection.couldNotSend", { msg }));
    }
  };

  // Sent state
  if (stage === "sent") {
    return (
      <div className="rounded-2xl border border-emerald-700/40 bg-emerald-900/10 p-5 space-y-3">
        <KatIAAvatar
          state="correct"
          message={t("procedureSection.sentMessage")}
          size="sm"
        />
        <Button variant="secondary" size="sm" onClick={resetAll} className="w-full">
          {t("procedureSection.uploadAnother")}
        </Button>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-slate-700/60 bg-[var(--surface)] overflow-hidden">
      {/* Toggle header */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-800/40 transition-colors text-left"
      >
        <span className="text-lg">📸</span>
        <div className="flex-1">
          <span className="text-sm font-medium text-slate-200">
            {t("procedureSection.toggleTitle")}
          </span>
          <span className="block text-[11px] text-slate-500">
            {t("procedureSection.toggleHint")}
          </span>
        </div>
        <span
          className={`text-slate-500 text-xs transition-transform ${expanded ? "rotate-180" : ""}`}
        >
          ▼
        </span>
      </button>

      {/* Expandable content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-3 border-t border-slate-800">
              {/* Item indicator */}
              <p className="text-xs text-emerald-400 pt-3">
                {t("procedureSection.boundToCurrent", { itemId })}
              </p>

              {/* Stage: idle — file upload */}
              {stage === "idle" && (
                <>
                  {/* Dropzone */}
                  <div
                    className={[
                      "border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-all",
                      file
                        ? "border-violet-500/60 bg-violet-900/10"
                        : "border-slate-600/60 hover:border-slate-500 bg-slate-800/30",
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
                        alt={t("procedureSection.preview")}
                        className="max-h-48 mx-auto rounded-lg object-contain"
                      />
                    ) : (
                      <div className="space-y-1">
                        <p className="text-slate-400 text-sm">
                          {t("procedureSection.dropFile")}{" "}
                          <span className="text-violet-400 underline">{t("procedureSection.selectFile")}</span>
                        </p>
                        <p className="text-[11px] text-slate-600">
                          {t("procedureSection.fileTypes", { max: MAX_SIZE_MB })}
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
                    <div className="flex items-center gap-2 bg-slate-800/50 rounded-lg px-3 py-1.5 border border-slate-700/50">
                      <span className="text-slate-300 text-xs flex-1 truncate">{file.name}</span>
                      <span className="text-[10px] text-slate-500">
                        {(file.size / 1024).toFixed(0)} KB
                      </span>
                      <button
                        onClick={() => {
                          setFile(null);
                          setPreview(null);
                        }}
                        className="text-slate-500 hover:text-red-400 text-xs"
                        aria-label={t("procedureSection.removeFile")}
                      >
                        ✕
                      </button>
                    </div>
                  )}

                  {error && (
                    <p className="text-xs text-red-400">{error}</p>
                  )}

                  {file && (
                    <div className="flex flex-col gap-1.5">
                      {canAnalyze ? (
                        <>
                          <Button onClick={handleAnalyze} size="sm" className="w-full">
                            {t("procedureSection.analyzeWithAI")}
                          </Button>
                          <button
                            onClick={() => handleSendToTeacher()}
                            className="text-[11px] text-slate-500 hover:text-slate-300 transition-colors"
                          >
                            {t("procedureSection.sendDirectly")}
                          </button>
                        </>
                      ) : (
                        <Button
                          onClick={() => handleSendToTeacher()}
                          size="sm"
                          className="w-full"
                        >
                          {t("procedureSection.sendToTeacher")}
                        </Button>
                      )}
                    </div>
                  )}
                </>
              )}

              {/* Stage: analyzing */}
              {stage === "analyzing" && (
                <div className="py-4 text-center space-y-3">
                  <KatIAAvatar state="thinking" size="md" />
                  <p className="text-xs text-slate-400">{t("procedureSection.katiaReviewingShort")}</p>
                  <div className="flex justify-center">
                    <div className="w-5 h-5 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
                  </div>
                </div>
              )}

              {/* Stage: result */}
              {stage === "result" && review && (
                <div className="space-y-3">
                  {preview && (
                    <img
                      src={preview}
                      alt={t("procedureSection.procedureAlt")}
                      className="max-h-40 mx-auto rounded-lg object-contain border border-slate-700/50"
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
                        ? t("procedureSection.katiaDefaultShort")
                        : katiaMessage(review.score_procedimiento)
                    }
                    size="sm"
                  />

                  {review.corresponde_a_pregunta === false && (
                    <p className="text-xs text-amber-300 bg-amber-900/20 rounded-lg px-3 py-2 border border-amber-700/40">
                      {t("procedureSection.notMatchingShort")}
                    </p>
                  )}

                  <div className="rounded-xl border border-slate-700/50 bg-slate-800/30 p-3 space-y-2">
                    <div className="flex items-baseline justify-between">
                      <span className="text-xs font-semibold text-slate-300">
                        {usedProvider === "groq"
                          ? t("procedureSection.reviewRigorousShort")
                          : t("procedureSection.reviewGenericShort")}
                      </span>
                      {review.score_procedimiento != null && (
                        <span
                          className={`text-lg font-bold ${scoreColor(review.score_procedimiento)}`}
                        >
                          {review.score_procedimiento}/100
                        </span>
                      )}
                    </div>

                    <p className="text-[10px] text-slate-500">{t("procedureSection.aiScoreNote")}</p>

                    {review.transcripcion && (
                      <details className="group">
                        <summary className="cursor-pointer text-[11px] text-slate-400 hover:text-slate-200">
                          {t("procedureSection.transcriptionShort")}
                        </summary>
                        <p className="mt-1 text-[11px] text-slate-300 whitespace-pre-wrap">
                          {review.transcripcion}
                        </p>
                      </details>
                    )}

                    {review.pasos && review.pasos.length > 0 && (
                      <details>
                        <summary className="cursor-pointer text-[11px] text-slate-400 hover:text-slate-200">
                          {t("procedureSection.stepsShort", { count: review.pasos.length })}
                        </summary>
                        <ul className="mt-1 space-y-1">
                          {review.pasos.map((p, i) => {
                            const ev = (p.evaluacion ?? "").toLowerCase();
                            const color = ev === "valido"
                              ? "text-emerald-400"
                              : ev.includes("incorrecto")
                                ? "text-rose-400"
                                : "text-amber-400";
                            return (
                              <li
                                key={i}
                                className="text-[11px] text-slate-300 border-l-2 border-slate-700 pl-2 py-0.5"
                              >
                                <span className="font-medium text-slate-200">
                                  {t("procedureSection.stepShort", { n: p.numero ?? i + 1 })}
                                </span>{" "}
                                {p.contenido && (
                                  <span className="text-slate-400">{p.contenido} </span>
                                )}
                                <span className={color}>({p.evaluacion})</span>
                                {p.comentario && (
                                  <span className="text-slate-500 italic block">
                                    {p.comentario}
                                  </span>
                                )}
                              </li>
                            );
                          })}
                        </ul>
                      </details>
                    )}

                    {review.errores_detectados && review.errores_detectados.length > 0 && (
                      <details>
                        <summary className="cursor-pointer text-[11px] text-rose-400 hover:text-rose-300">
                          {t("procedureSection.errorsShort", { count: review.errores_detectados.length })}
                        </summary>
                        <ul className="mt-1 space-y-0.5 text-[11px] text-slate-300 list-disc list-inside">
                          {review.errores_detectados.map((err, i) => (
                            <li key={i}>{err}</li>
                          ))}
                        </ul>
                      </details>
                    )}

                    {review.saltos_logicos && review.saltos_logicos.length > 0 && (
                      <details>
                        <summary className="cursor-pointer text-[11px] text-amber-400 hover:text-amber-300">
                          {t("procedureSection.logicalGapsShort", { count: review.saltos_logicos.length })}
                        </summary>
                        <ul className="mt-1 space-y-0.5 text-[11px] text-slate-300 list-disc list-inside">
                          {review.saltos_logicos.map((s, i) => (
                            <li key={i}>{s}</li>
                          ))}
                        </ul>
                      </details>
                    )}

                    <div className="pt-1 border-t border-slate-700/50 text-[11px] text-slate-400">
                      <strong className="text-slate-300">{t("procedureSection.resultShort")}</strong>{" "}
                      {review.resultado_correcto
                        ? t("procedureSection.correctResult")
                        : t("procedureSection.incorrectResult")}
                    </div>
                    {review.evaluacion_global && (
                      <p className="text-[11px] text-slate-400">{review.evaluacion_global}</p>
                    )}
                  </div>

                  {error && <p className="text-xs text-red-400">{error}</p>}

                  <div className="flex gap-2">
                    <Button
                      onClick={() => handleSendToTeacher({ withAI: true })}
                      size="sm"
                      className="flex-1"
                    >
                      {t("procedureSection.sendToTeacher")}
                    </Button>
                    <Button variant="secondary" size="sm" onClick={resetAll}>
                      {t("procedureSection.other")}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
