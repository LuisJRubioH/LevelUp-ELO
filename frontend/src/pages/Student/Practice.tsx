/**
 * pages/Student/Practice.tsx
 * ===========================
 * Sala de práctica adaptativa: pregunta + opciones + feedback KatIA + timer.
 * Flujo: seleccionar opción → botón "Enviar respuesta" → feedback + KatIA.
 */

import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { studentApi, type Course } from "../../api/student";
import { AnswerOptions } from "../../components/Question/AnswerOptions";
import { QuestionCard } from "../../components/Question/QuestionCard";
import { KatIAAvatar } from "../../components/KatIA/KatIAAvatar";
import { SocraticChat } from "../../components/KatIA/SocraticChat";
import { RankBadge } from "../../components/ELO/RankBadge";
import { Button } from "../../components/ui/Button";
import { StreakToast } from "../../components/ui/StreakToast";
import { useStudentSession } from "../../hooks/useStudentSession";
import { useTimer } from "../../hooks/useTimer";
import { usePracticeStore } from "../../stores/practiceStore";
import { useSettingsStore } from "../../stores/settingsStore";
import { ProcedureSection } from "../../components/Procedure/ProcedureSection";

/** Estima delta ELO antes de enviar (K=24, fórmula ELO clásica). */
function estimateEloDelta(studentElo: number, itemDifficulty: number) {
  const expected = 1 / (1 + Math.pow(10, (itemDifficulty - studentElo) / 400));
  const K = studentElo < 1400 ? 32 : 24;
  const onCorrect = +(K * (1 - expected)).toFixed(1);
  const onWrong = +(K * (0 - expected)).toFixed(1);
  return { onCorrect, onWrong };
}

const STREAK_MILESTONES = [5, 10, 20];

export function Practice() {
  const { t } = useTranslation();
  const { courseId, startSession, resetSession, setPhase } = usePracticeStore();
  const { currentItem, lastAnswer, phase, isLoading, sessionQuestionsCount, loadNextQuestion, submitAnswer } =
    useStudentSession();
  const { apiKey, provider } = useSettingsStore();

  // Cursos matriculados (enrolled=true) y disponibles (enrolled=false).
  // Mostramos AMBOS en la pantalla inicial: matriculados primero (entrada
  // directa a sesión) y disponibles abajo (matrícula + entrada en un click).
  const [enrolledCourses, setEnrolledCourses] = useState<Course[]>([]);
  const [availableCourses, setAvailableCourses] = useState<Course[]>([]);
  const [coursesLoading, setCoursesLoading] = useState(true);
  const [enrollingCourseId, setEnrollingCourseId] = useState<string | null>(null);
  // Opción seleccionada por el estudiante (antes de enviar)
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  // Si la respuesta ya fue enviada (esperando o recibida)
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [globalElo, setGlobalElo] = useState(1000);
  const [rankLabel, setRankLabel] = useState("Aspirante");
  const [deltaElo, setDeltaElo] = useState<number | undefined>(undefined);
  const [showChat, setShowChat] = useState(false);
  // Racha de respuestas correctas consecutivas
  const [_consecutiveCorrect, setConsecutiveCorrect] = useState(0);
  const [streakToast, setStreakToast] = useState<number | null>(null);

  // Timer por pregunta — se resetea al cargar la nueva pregunta
  const timer = useTimer({ autoStart: true });

  // Cargar cursos disponibles al montar
  useEffect(() => {
    studentApi.courses()
      .then((c) => {
        setEnrolledCourses(c.filter((x) => x.enrolled));
        setAvailableCourses(c.filter((x) => !x.enrolled));
      })
      .catch(() => {/* silencioso — el backend puede estar durmiendo */})
      .finally(() => setCoursesLoading(false));
    studentApi.stats()
      .then((s) => {
        setGlobalElo(s.global_elo);
        setRankLabel(s.rank_label ?? "Aspirante");
      })
      .catch(() => {/* silencioso */});
  }, []);

  // Cargar primera pregunta cuando el curso está seleccionado
  useEffect(() => {
    if (courseId && phase === "loading") {
      loadNextQuestion();
    }
  }, [courseId, phase, loadNextQuestion]);

  // Resetear estado local al cargar nueva pregunta
  useEffect(() => {
    if (phase === "question") {
      timer.reset();
      timer.start();
      setSelectedOption(null);
      setSubmitted(false);
      setSubmitting(false);
      setShowChat(false);
    }
  }, [currentItem?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSelectOption = (option: string) => {
    // Solo permite cambiar opción si no se ha enviado aún
    if (submitted) return;
    setSelectedOption(option);
  };

  const handleSubmit = async () => {
    if (!selectedOption || submitted) return;
    timer.stop();
    setSubmitted(true);
    setSubmitting(true);
    await submitAnswer(selectedOption);
    setSubmitting(false);
  };

  const handleNext = () => {
    setSelectedOption(null);
    setSubmitted(false);
    setSubmitting(false);
    setDeltaElo(undefined);
    setShowChat(false);
    loadNextQuestion();
  };

  // Mostrar delta ELO al recibir respuesta + actualizar racha
  // OJO: lastAnswer.eloAfter es el ELO del TÓPICO, no el ELO GLOBAL.
  // El header (RankBadge) muestra ELO global, así que lo refrescamos desde
  // /stats en lugar de pisarlo con el del tópico (causaba la inconsistencia
  // entre sidebar 1022 vs feedback 1009).
  useEffect(() => {
    if (lastAnswer) {
      setDeltaElo(lastAnswer.deltaElo);
      setSubmitting(false);

      studentApi.stats()
        .then((s) => {
          setGlobalElo(s.global_elo);
          setRankLabel(s.rank_label ?? rankLabel);
        })
        .catch(() => {/* silencioso — siguiente respuesta volverá a intentar */});

      setConsecutiveCorrect((prev) => {
        const next = lastAnswer.isCorrect ? prev + 1 : 0;
        if (lastAnswer.isCorrect && STREAK_MILESTONES.includes(next)) {
          setStreakToast(next);
        }
        return next;
      });
    }
  }, [lastAnswer]); // eslint-disable-line react-hooks/exhaustive-deps

  const dismissStreakToast = useCallback(() => setStreakToast(null), []);

  // Click en curso disponible: matricula + arranca sesión en un solo paso.
  const enrollAndStart = async (cid: string) => {
    setEnrollingCourseId(cid);
    try {
      await studentApi.enroll(cid);
      startSession(cid);
    } catch (e) {
      console.error("Error matriculando en curso", e);
      setEnrollingCourseId(null);
    }
  };

  // ── Sin curso seleccionado: selector de cursos ────────────────────────────
  if (!courseId) {
    const hasEnrolled = enrolledCourses.length > 0;
    const hasAvailable = availableCourses.length > 0;
    return (
      <div className="max-w-xl mx-auto py-8 px-4">
        <h2 className="text-xl font-bold text-slate-100 mb-2">{t("practice.title")}</h2>
        <p className="text-slate-400 text-sm mb-6">
          {hasEnrolled ? t("practice.subtitle") : t("practice.subtitleAvailable")}
        </p>

        {coursesLoading ? (
          <div className="text-center text-slate-500 animate-pulse py-8">{t("practice.loadingCourses")}</div>
        ) : !hasEnrolled && !hasAvailable ? (
          <div className="bg-slate-800 rounded-2xl p-8 text-center border border-slate-700">
            <p className="text-slate-400">{t("practice.noCourses")}</p>
            <a href="/student/courses" className="text-violet-400 text-sm mt-2 block hover:underline">
              {t("practice.browseCourses")}
            </a>
          </div>
        ) : (
          <div className="space-y-6">
            {hasEnrolled && (
              <div className="grid gap-3">
                {enrolledCourses.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => startSession(c.id)}
                    className="w-full text-left bg-slate-800 hover:bg-slate-700 rounded-xl px-4 py-4 border border-slate-700 hover:border-violet-500 transition-all"
                  >
                    <div className="font-medium text-slate-100">{c.name}</div>
                    <div className="text-xs text-slate-500 mt-1">{c.block}</div>
                  </button>
                ))}
              </div>
            )}
            {hasAvailable && (
              <div>
                <p className="text-xs uppercase tracking-wider text-slate-500 mb-2">
                  {hasEnrolled
                    ? t("practice.availableMore")
                    : t("practice.availableEnroll")}
                </p>
                <div className="grid gap-3">
                  {availableCourses.map((c) => {
                    const loading = enrollingCourseId === c.id;
                    return (
                      <button
                        key={c.id}
                        disabled={loading}
                        onClick={() => enrollAndStart(c.id)}
                        className="w-full text-left bg-slate-900/60 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-wait rounded-xl px-4 py-4 border border-violet-700/40 hover:border-violet-500 transition-all"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div>
                            <div className="font-medium text-slate-100">{c.name}</div>
                            <div className="text-xs text-slate-500 mt-1">{c.block}</div>
                          </div>
                          <span className="text-xs text-violet-300 font-medium whitespace-nowrap">
                            {loading ? t("practice.enrolling") : t("practice.enrollAndStart")}
                          </span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // ── Sesión vacía ──────────────────────────────────────────────────────────
  if (phase === "empty") {
    return (
      <div className="max-w-xl mx-auto py-8 px-4 text-center">
        <KatIAAvatar state="correct" message={t("practice.noMoreQuestions")} size="lg" />
        <Button className="mt-6" variant="secondary" onClick={() => resetSession()}>
          Cambiar curso
        </Button>
      </div>
    );
  }

  // ── Error de red / servidor ───────────────────────────────────────────────
  if (phase === "error") {
    return (
      <div className="max-w-xl mx-auto py-8 px-4 text-center space-y-4">
        <KatIAAvatar state="error" message={t("practice.errorLoading")} size="lg" />
        <Button onClick={() => setPhase("loading")} variant="secondary">
          {t("practice.retry")}
        </Button>
        <button
          onClick={() => resetSession()}
          className="block mx-auto text-xs text-slate-500 hover:text-slate-400"
        >
          {t("practice.changeCourse")}
        </button>
      </div>
    );
  }

  // ── Cargando ──────────────────────────────────────────────────────────────
  if (isLoading || !currentItem) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-slate-400">{t("practice.loadingQuestion")}</div>
      </div>
    );
  }

  // ── Pregunta activa ───────────────────────────────────────────────────────
  // Estado de la respuesta: null = sin respuesta, lastAnswer = recibida, submitted+!lastAnswer = enviando
  const answerReceived = submitted && !!lastAnswer;
  const answerFailed = submitted && !submitting && !lastAnswer;

  // Cálculo ELO preview (estimado, antes de enviar)
  const eloPreview = currentItem && selectedOption && !submitted
    ? estimateEloDelta(globalElo, currentItem.difficulty)
    : null;

  return (
    <div className="max-w-2xl mx-auto py-6 px-4 space-y-4">
      {/* Toast de racha */}
      {streakToast && (
        <StreakToast streak={streakToast} onDismiss={dismissStreakToast} />
      )}

      {/* Header: ELO global + rango */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => resetSession()}
          className="text-xs text-slate-500 hover:text-slate-400"
        >
          {t("practice.changeCourse")}
        </button>
        <RankBadge elo={globalElo} rankLabel={rankLabel} deltaElo={deltaElo} />
      </div>

      {/* Tarjeta de pregunta */}
      <QuestionCard
        content={currentItem.content}
        topic={currentItem.topic}
        difficulty={currentItem.difficulty}
        tags={currentItem.tags}
        imageUrl={currentItem.image_url}
        timerFormatted={timer.formatted}
        questionNumber={sessionQuestionsCount + 1}
      />

      {/* Opciones */}
      <AnswerOptions
        options={currentItem.options}
        selectedOption={selectedOption}
        isCorrect={answerReceived ? (lastAnswer?.isCorrect ?? null) : null}
        onSelect={handleSelectOption}
        disabled={submitted}
      />

      {/* KatIA pre-answer: pedir ayuda antes de responder */}
      {!submitted && (
        <div className="flex justify-end">
          <button
            onClick={() => setShowChat((v) => !v)}
            className="text-xs text-violet-400 hover:text-violet-300 transition-colors"
          >
            {showChat ? t("practice.hideChat") : t("practice.katiaHelp")}
          </button>
        </div>
      )}

      {!submitted && showChat && (
        <SocraticChat
          itemId={currentItem.id}
          itemContent={currentItem.content}
          courseId={courseId ?? ""}
          apiKey={apiKey}
          provider={provider}
        />
      )}

      {/* Preview ELO + botón enviar */}
      {selectedOption && !submitted && (
        <div className="space-y-2">
          {eloPreview && (
            <div className="flex justify-center gap-4 text-xs">
              <span className="text-green-400">
                {t("practice.ifCorrect")} <strong>+{eloPreview.onCorrect}</strong>
              </span>
              <span className="text-slate-500">|</span>
              <span className="text-red-400">
                {t("practice.ifWrong")} <strong>{eloPreview.onWrong}</strong>
              </span>
            </div>
          )}
          <Button onClick={handleSubmit} size="lg" className="w-full">
            {t("practice.sendAnswer")}
          </Button>
        </div>
      )}

      {/* Enviando (spinner) */}
      {submitting && (
        <div className="text-center text-slate-400 text-sm animate-pulse py-2">
          {t("practice.sending")}
        </div>
      )}

      {/* Error al enviar — permite continuar */}
      {answerFailed && (
        <div className="rounded-xl p-4 border border-yellow-600 bg-yellow-900/20 space-y-2">
          <p className="text-sm text-yellow-300">{t("practice.connectionError")}</p>
          <Button onClick={handleNext} size="sm" variant="secondary">
            {t("practice.nextQuestion")}
          </Button>
        </div>
      )}

      {/* Feedback post-respuesta */}
      {answerReceived && lastAnswer && (
        <div className="fade-in space-y-3">
          <div
            className={`rounded-xl p-4 border ${
              lastAnswer.isCorrect
                ? "border-green-600 bg-green-900/30"
                : "border-red-600 bg-red-900/30"
            }`}
          >
            <p className="text-sm font-medium">
              {lastAnswer.isCorrect ? t("practice.feedbackCorrect") : t("practice.feedbackWrong")}
            </p>
            <p className="text-xs text-slate-400 mt-1">
              {t("practice.topicEloLabel")} ({currentItem.topic}):{" "}
              {Math.round(lastAnswer.eloBefore)} →{" "}
              <span className={lastAnswer.deltaElo >= 0 ? "text-green-400" : "text-red-400"}>
                {Math.round(lastAnswer.eloAfter)}
              </span>{" "}
              ({lastAnswer.deltaElo >= 0 ? "+" : ""}
              {lastAnswer.deltaElo.toFixed(1)})
            </p>
            <p className="text-[10px] text-slate-500 mt-1 italic">
              {t("practice.topicEloNote")}
            </p>
          </div>

          {/* KatIA + controles */}
          <div className="flex items-start gap-3">
            <KatIAAvatar
              state={lastAnswer.isCorrect ? "correct" : "error"}
              message={
                lastAnswer.isCorrect
                  ? t("practice.katiaCorrect")
                  : t("practice.katiaWrong")
              }
              size="sm"
            />
            <div className="flex-1 flex flex-col gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setShowChat((v) => !v)}
              >
                {showChat ? t("practice.hideChat") : t("practice.katiaHelp")}
              </Button>
              <Button onClick={handleNext} size="lg">
                {t("practice.nextQuestion")}
              </Button>
            </div>
          </div>

          {/* Chat socrático */}
          {showChat && (
            <SocraticChat
              itemId={currentItem.id}
              itemContent={currentItem.content}
              courseId={courseId ?? ""}
              apiKey={apiKey}
              provider={provider}
            />
          )}
        </div>
      )}

      {/* Procedimiento manuscrito — vinculado a la pregunta actual (como V1) */}
      <ProcedureSection
        itemId={currentItem.id}
        itemContent={currentItem.content}
      />
    </div>
  );
}
