/**
 * pages/Student/Practice.tsx
 * ===========================
 * Sala de práctica adaptativa: pregunta + opciones + feedback KatIA + timer.
 * Flujo: seleccionar opción → botón "Enviar respuesta" → feedback + KatIA.
 */

import { useEffect, useState } from "react";
import { studentApi, type Course } from "../../api/student";
import { AnswerOptions } from "../../components/Question/AnswerOptions";
import { QuestionCard } from "../../components/Question/QuestionCard";
import { KatIAAvatar } from "../../components/KatIA/KatIAAvatar";
import { SocraticChat } from "../../components/KatIA/SocraticChat";
import { RankBadge } from "../../components/ELO/RankBadge";
import { Button } from "../../components/ui/Button";
import { useStudentSession } from "../../hooks/useStudentSession";
import { useTimer } from "../../hooks/useTimer";
import { usePracticeStore } from "../../stores/practiceStore";
import { useSettingsStore } from "../../stores/settingsStore";

export function Practice() {
  const { courseId, startSession, resetSession } = usePracticeStore();
  const { currentItem, lastAnswer, phase, isLoading, sessionQuestionsCount, loadNextQuestion, submitAnswer } =
    useStudentSession();
  const { apiKey, provider } = useSettingsStore();

  const [courses, setCourses] = useState<Course[]>([]);
  // Opción seleccionada por el estudiante (antes de enviar)
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  // Si la respuesta ya fue enviada (esperando o recibida)
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [globalElo, setGlobalElo] = useState(1000);
  const [rankLabel, setRankLabel] = useState("Aspirante");
  const [deltaElo, setDeltaElo] = useState<number | undefined>(undefined);
  const [showChat, setShowChat] = useState(false);

  // Timer por pregunta — se resetea al cargar la nueva pregunta
  const timer = useTimer({ autoStart: true });

  // Cargar cursos disponibles al montar
  useEffect(() => {
    studentApi.courses().then((c) => setCourses(c.filter((x) => x.enrolled)));
    studentApi.stats().then((s) => {
      setGlobalElo(s.global_elo);
      setRankLabel(s.rank_label ?? "Aspirante");
    });
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

  // Mostrar delta ELO al recibir respuesta
  useEffect(() => {
    if (lastAnswer) {
      setDeltaElo(lastAnswer.deltaElo);
      setGlobalElo(lastAnswer.eloAfter);
      setSubmitting(false);
    }
  }, [lastAnswer]);

  // ── Sin curso seleccionado: selector de cursos ────────────────────────────
  if (!courseId) {
    return (
      <div className="max-w-xl mx-auto py-8 px-4">
        <h2 className="text-xl font-bold text-white mb-2">Sala de Práctica</h2>
        <p className="text-slate-400 text-sm mb-6">Selecciona un curso para empezar.</p>

        {courses.length === 0 ? (
          <div className="bg-slate-800 rounded-2xl p-8 text-center border border-slate-700">
            <p className="text-slate-400">No estás matriculado en ningún curso aún.</p>
            <a href="/student/courses" className="text-violet-400 text-sm mt-2 block hover:underline">
              → Ver catálogo de cursos
            </a>
          </div>
        ) : (
          <div className="grid gap-3">
            {courses.map((c) => (
              <button
                key={c.id}
                onClick={() => startSession(c.id)}
                className="w-full text-left bg-slate-800 hover:bg-slate-700 rounded-xl px-4 py-4 border border-slate-700 hover:border-violet-500 transition-all"
              >
                <div className="font-medium text-white">{c.name}</div>
                <div className="text-xs text-slate-500 mt-1">{c.block}</div>
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }

  // ── Sesión vacía ──────────────────────────────────────────────────────────
  if (phase === "empty") {
    return (
      <div className="max-w-xl mx-auto py-8 px-4 text-center">
        <KatIAAvatar state="correct" message="¡Has completado todas las preguntas disponibles hoy! Vuelve mañana 🎉" size="lg" />
        <Button className="mt-6" variant="secondary" onClick={() => resetSession()}>
          Cambiar curso
        </Button>
      </div>
    );
  }

  // ── Cargando ──────────────────────────────────────────────────────────────
  if (isLoading || !currentItem) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-slate-400">Cargando pregunta...</div>
      </div>
    );
  }

  // ── Pregunta activa ───────────────────────────────────────────────────────
  // Estado de la respuesta: null = sin respuesta, lastAnswer = recibida, submitted+!lastAnswer = enviando
  const answerReceived = submitted && !!lastAnswer;
  const answerFailed = submitted && !submitting && !lastAnswer;

  return (
    <div className="max-w-2xl mx-auto py-6 px-4 space-y-4">
      {/* Header: ELO global + rango */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => resetSession()}
          className="text-xs text-slate-500 hover:text-slate-400"
        >
          ← Cambiar curso
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
        correctOption={answerReceived ? (lastAnswer?.correctOption ?? null) : null}
        onSelect={handleSelectOption}
        disabled={submitted}
      />

      {/* Botón enviar — visible cuando hay opción seleccionada y no se ha enviado aún */}
      {selectedOption && !submitted && (
        <Button
          onClick={handleSubmit}
          size="lg"
          className="w-full"
        >
          Enviar respuesta
        </Button>
      )}

      {/* Enviando (spinner) */}
      {submitting && (
        <div className="text-center text-slate-400 text-sm animate-pulse py-2">
          Enviando respuesta...
        </div>
      )}

      {/* Error al enviar — permite continuar */}
      {answerFailed && (
        <div className="rounded-xl p-4 border border-yellow-600 bg-yellow-900/20 space-y-2">
          <p className="text-sm text-yellow-300">No se pudo registrar la respuesta (error de conexión).</p>
          <Button onClick={handleNext} size="sm" variant="secondary">
            Siguiente pregunta →
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
              {lastAnswer.isCorrect ? "✅ ¡Correcto!" : "❌ Incorrecto"}
            </p>
            <p className="text-xs text-slate-400 mt-1">
              ELO: {Math.round(lastAnswer.eloBefore)} →{" "}
              <span className={lastAnswer.deltaElo >= 0 ? "text-green-400" : "text-red-400"}>
                {Math.round(lastAnswer.eloAfter)}
              </span>{" "}
              ({lastAnswer.deltaElo >= 0 ? "+" : ""}
              {lastAnswer.deltaElo.toFixed(1)})
            </p>
          </div>

          {/* KatIA + controles */}
          <div className="flex items-start gap-3">
            <KatIAAvatar
              state={lastAnswer.isCorrect ? "correct" : "error"}
              message={
                lastAnswer.isCorrect
                  ? "¡Excelente! ¿Quieres explorar más con KatIA?"
                  : "¡No te rindas! KatIA puede ayudarte a entender este problema."
              }
              size="sm"
            />
            <div className="flex-1 flex flex-col gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setShowChat((v) => !v)}
              >
                {showChat ? "Ocultar chat KatIA" : "🐱 Preguntar a KatIA"}
              </Button>
              <Button onClick={handleNext} size="lg">
                Siguiente pregunta →
              </Button>
            </div>
          </div>

          {/* Chat socrático */}
          {showChat && (
            apiKey ? (
              <SocraticChat
                itemId={currentItem.id}
                itemContent={currentItem.content}
                courseId={courseId ?? ""}
                apiKey={apiKey}
                provider={provider}
              />
            ) : (
              <div className="bg-slate-800 rounded-2xl border border-slate-700 p-4 text-center space-y-2">
                <p className="text-violet-400 font-medium text-sm">🐱 Chat con KatIA</p>
                <p className="text-xs text-slate-400">
                  Configura una API key de IA en el panel lateral (▼ API de IA) para activar el chat socrático.
                </p>
                <p className="text-xs text-slate-500">
                  Compatible con Groq (gratis), Anthropic, OpenAI y más.
                </p>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
}
