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
import { useTranslation } from "react-i18next";
import { KatIAAvatar } from "../../components/KatIA/KatIAAvatar";
import { Button } from "../../components/ui/Button";
import { studentApi, type ProcedureReview } from "../../api/student";
import { apiClient } from "../../api/client";
import { useSettingsStore } from "../../stores/settingsStore";
import { ValidatedCard, PendingCard, classifyStatus } from "./Feedback";
import { PageHeader } from "../../components/ui/PageHeader";
import "./StudentContent.css";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "application/pdf"];
const MAX_SIZE_MB = 10;

type Stage = "idle" | "analyzing" | "result" | "sent";

function scoreColor(score: number): string {
  if (score < 40) return "text-rose-400";
  if (score < 70) return "text-amber-400";
  return "text-emerald-400";
}

export function ProcedureUpload() {
  const { t } = useTranslation();
  const fileRef = useRef<HTMLInputElement>(null);
  const { apiKey } = useSettingsStore();

  const katiaMessage = (score: number): string => {
    if (score >= 91) return t("procedure.katiaHigh");
    if (score >= 60) return t("procedure.katiaMid");
    return t("procedure.katiaLow");
  };

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<string>("");
  const [itemContent, setItemContent] = useState<string>("");
  const [stage, setStage] = useState<Stage>("idle");
  const [error, setError] = useState<string | null>(null);
  const [review, setReview] = useState<ProcedureReview | null>(null);
  const [usedProvider, setUsedProvider] = useState<string>("");
  const [analysisToken, setAnalysisToken] = useState("");

  const { data: courses } = useQuery({
    queryKey: ["student-courses"],
    queryFn: () => studentApi.courses(),
  });

  const { data: aiStatus } = useQuery({
    queryKey: ["ai-status"],
    queryFn: () => studentApi.aiStatus(),
    staleTime: 300_000,
  });

  const { data: myProcedures } = useQuery({
    queryKey: ["my-procedures"],
    queryFn: () => studentApi.myProcedures(),
    refetchInterval: 30_000,
  });
  const submissions = myProcedures?.submissions ?? [];

  const enrolled = (courses ?? []).filter((c) => c.enrolled);
  const canAnalyze = !!apiKey || (aiStatus?.available ?? false);

  const handleFile = (f: File) => {
    setError(null);
    setReview(null);
    setAnalysisToken("");
    if (!ALLOWED_TYPES.includes(f.type)) {
      setError(t("procedure.typeNotSupported", { type: f.type }));
      return;
    }
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(t("procedure.fileTooBig", { max: MAX_SIZE_MB }));
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
    setAnalysisToken("");
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!file || !selectedItem) return;
    setError(null);
    setStage("analyzing");
    try {
      const { review: r, provider, analysisToken: token } = await studentApi.analyzeProcedure({
        item_id: selectedItem,
        item_content: itemContent,
        api_key: apiKey || undefined,
        file,
      });
      setReview(r);
      setUsedProvider(provider);
      setAnalysisToken(token);
      setStage("result");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : t("procedure.unknownError");
      setError(t("procedure.couldNotAnalyze", { msg }));
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
      if (opts?.withAI && analysisToken) fd.append("analysis_token", analysisToken);
      await apiClient.postForm("/api/student/procedure", fd);
      setStage("sent");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : t("procedure.unknownError");
      setError(t("procedure.couldNotSend", { msg }));
    }
  };

  if (stage === "sent") {
    return (
      <div className="sp-page">
        <h2 className="sp-title">{t("procedure.sentTitle")}</h2>
        <KatIAAvatar
          state="correct"
          message={t("procedure.sentMessage")}
          size="md"
        />
        <Button variant="secondary" onClick={resetAll} className="w-full">
          {t("procedure.sendAnother")}
        </Button>
      </div>
    );
  }

  return (
    <div className="sp-page">
      <PageHeader eyebrow={t("procedure.eyebrow")} title={t("procedure.title")} />
      <div className="sp-card space-y-1">
        <p className="text-sm" style={{ color: "var(--dim)" }}>{t("procedure.intro")}</p>
        <p className="sp-mute text-xs">{t("procedure.introHint")}</p>
      </div>

      {/* Identificación del ejercicio */}
      {stage === "idle" && (
        <>
          <div className="sp-field">
            <label>
              {t("procedure.exerciseIdLabel")} <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={selectedItem}
              onChange={(e) => setSelectedItem(e.target.value)}
              placeholder={t("procedure.exerciseIdPlaceholder")}
              className="sp-input"
            />
            {enrolled.length > 0 && (
              <p className="sp-mute text-xs mt-1">
                {t("procedure.enrolledCourses", {
                  courses: enrolled.map((c) => c.name).join(", "),
                })}
              </p>
            )}
          </div>

          {canAnalyze && (
            <div className="sp-field">
              <label>
                {t("procedure.statementLabel")}
              </label>
              <textarea
                value={itemContent}
                onChange={(e) => setItemContent(e.target.value)}
                rows={3}
                placeholder={t("procedure.statementPlaceholder")}
                className="sp-input"
                style={{ resize: "none" }}
              />
            </div>
          )}

          {/* Dropzone. <label> en vez de <div onClick>: arrastrar no puede ser la
              unica via, y con `hidden` el input tampoco entraba en el orden de
              foco. El label abre el selector solo. */}
          <label
            className={`sp-dropzone${file ? " active" : ""}`}
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
                alt={t("procedure.preview")}
                className="max-h-64 mx-auto rounded-lg object-contain"
              />
            ) : (
              <div className="space-y-2">
                <div className="text-4xl">📷</div>
                <p className="sp-dim text-sm">
                  {t("procedure.dropFile")}{" "}
                  <span className="text-violet-400 underline">{t("procedure.clickToSelect")}</span>
                </p>
                <p className="sp-mute text-xs">
                  {t("procedure.fileTypes", { max: MAX_SIZE_MB })}
                </p>
              </div>
            )}
            <input
              ref={fileRef}
              type="file"
              accept={ALLOWED_TYPES.join(",")}
              className="sr-only"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleFile(f);
              }}
            />
          </label>

          {file && (
            <div className="sp-row">
              <span className="text-sm flex-1 truncate" style={{ color: "var(--dim)" }}>{file.name}</span>
              <span className="sp-mute text-xs">{(file.size / 1024).toFixed(0)} KB</span>
              <button
                onClick={() => { setFile(null); setPreview(null); }}
                className="sp-mute hover:text-red-400 text-xs"
                aria-label={t("procedure.removeFile")}
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
                {t("procedure.analyzeWithAI")}
              </Button>
              <button
                onClick={() => handleSendToTeacher()}
                disabled={!file || !selectedItem}
                className="w-full text-xs text-slate-500 hover:text-slate-300 transition-colors disabled:opacity-50"
              >
                {t("procedure.sendDirectly")}
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
                {t("procedure.sendToTeacher")}
              </Button>
              <p className="text-xs text-slate-500 text-center">{t("procedure.aiNotAvailable")}</p>
            </>
          )}
        </>
      )}

      {/* Estado: analizando */}
      {stage === "analyzing" && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="sp-card text-center space-y-4"
        >
          <KatIAAvatar state="thinking" size="lg" />
          <p className="text-sm font-medium" style={{ color: "var(--dim)" }}>{t("procedure.katiaReviewing")}</p>
          <p className="sp-mute text-xs">{t("procedure.katiaReviewingHint")}</p>
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
                alt={t("procedure.procedureAlt")}
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
                  ? t("procedure.katiaDefaultMessage")
                  : katiaMessage(review.score_procedimiento)
              }
              size="md"
            />

            {review.corresponde_a_pregunta === false && (
              <div className="rounded-xl border border-amber-600 bg-amber-900/20 p-3">
                <p className="text-sm text-amber-300">{t("procedure.notMatchingStatement")}</p>
              </div>
            )}

            <div className="sp-card space-y-4">
              <div className="flex items-baseline justify-between">
                <h3 className="text-sm font-semibold" style={{ color: "var(--text)", margin: 0 }}>
                  {usedProvider === "groq"
                    ? t("procedure.reviewRigorous")
                    : t("procedure.reviewGeneric")}
                </h3>
                {review.score_procedimiento != null && (
                  <span
                    className={`text-2xl font-bold ${scoreColor(review.score_procedimiento)}`}
                  >
                    {review.score_procedimiento}/100
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500">{t("procedure.aiScoreNote")}</p>

              {review.transcripcion && (
                <details className="group">
                  <summary className="cursor-pointer text-xs text-slate-400 hover:text-slate-200">
                    {t("procedure.transcription")}
                  </summary>
                  <p className="mt-2 text-xs text-slate-300 whitespace-pre-wrap">
                    {review.transcripcion}
                  </p>
                </details>
              )}

              {review.pasos && review.pasos.length > 0 && (
                <details>
                  <summary className="cursor-pointer text-xs text-slate-400 hover:text-slate-200">
                    {t("procedure.stepsAnalyzed", { count: review.pasos.length })}
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
                            {t("procedure.stepLabel", { n: p.numero ?? i + 1 })}
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
                    {t("procedure.errorsDetected", { count: review.errores_detectados.length })}
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
                    {t("procedure.logicalGaps", { count: review.saltos_logicos.length })}
                  </summary>
                  <ul className="mt-2 space-y-1 text-xs text-slate-300 list-disc list-inside">
                    {review.saltos_logicos.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </details>
              )}

              <div className="pt-2 border-t border-slate-800 text-xs text-slate-400">
                <strong className="text-slate-300">{t("procedure.finalResult")}</strong>{" "}
                {review.resultado_correcto ? t("procedure.correctResult") : t("procedure.incorrectResult")}
              </div>
              {review.evaluacion_global && (
                <p className="text-xs text-slate-400">
                  <strong className="text-slate-300">{t("procedure.overallEvaluation")}</strong>{" "}
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
                {t("procedure.sendForValidation")}
              </Button>
              <Button variant="secondary" onClick={resetAll} className="sm:w-auto">
                {t("procedure.uploadAnother")}
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Retroalimentación docente — mismos envíos que ve en KatIA/Feedback */}
      {submissions.length > 0 && (
        <div className="space-y-3">
          <h3 style={{ margin: 0 }}>{t("procedure.feedbackListTitle")}</h3>
          {submissions.map((row) => {
            const kind = classifyStatus(row.status);
            if (kind === "validated") return <ValidatedCard key={row.submission_id} row={row} t={t} />;
            return <PendingCard key={row.submission_id} row={row} kind={kind} t={t} />;
          })}
        </div>
      )}
    </div>
  );
}
