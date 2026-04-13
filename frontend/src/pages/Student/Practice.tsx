/**
 * pages/Student/Practice.tsx
 * ===========================
 * Sala de práctica adaptativa: pregunta + opciones + feedback KatIA + timer.
 * Cuando el estudiante elige un curso → empieza la sesión adaptativa.
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
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
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

  // Resetear timer y selected option al cargar nueva pregunta
  useEffect(() => {
    if (phase === "question") {
      timer.reset();
      timer.start();
      setSelectedOption(null);
    }
  }, [currentItem?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSelectOption = (option: string) => {
    if (selectedOption || lastAnswer) return;
    setSelectedOption(option);
    timer.stop();
    submitAnswer(option);
  };

  const handleNext = () => {
    setSelectedOption(null);
    setDeltaElo(undefined);
    setShowChat(false);
    loadNextQuestion();
  };

  // Mostrar delta ELO al recibir respuesta
  useEffect(() => {
    if (lastAnswer) {
      setDeltaElo(lastAnswer.deltaElo);
      setGlobalElo(lastAnswer.eloAfter);
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
        imageUrl={currentItem.image_url}
        timerFormatted={timer.formatted}
        questionNumber={sessionQuestionsCount + 1}
      />

      {/* Opciones */}
      <AnswerOptions
        options={currentItem.options}
        selectedOption={selectedOption}
        correctOption={lastAnswer?.correctOption ?? null}
        onSelect={handleSelectOption}
      />

      {/* Feedback post-respuesta */}
      {lastAnswer && (
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
              <span
                className={lastAnswer.deltaElo >= 0 ? "text-green-400" : "text-red-400"}
              >
                {Math.round(lastAnswer.eloAfter)}
              </span>{" "}
              ({lastAnswer.deltaElo >= 0 ? "+" : ""}
              {lastAnswer.deltaElo.toFixed(1)})
            </p>
          </div>

          <div className="flex items-center gap-3">
            <KatIAAvatar
              state={lastAnswer.isCorrect ? "correct" : "error"}
              message={
                lastAnswer.isCorrect
                  ? "¡Excelente razonamiento!"
                  : "Analiza bien cada opción. ¿Quieres ayuda del chat socrático?"
              }
              size="sm"
            />
            <div className="flex-1 flex flex-col gap-2">
              {!lastAnswer.isCorrect && apiKey && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setShowChat((v) => !v)}
                >
                  {showChat ? "Ocultar chat KatIA" : "🐱 Preguntar a KatIA"}
                </Button>
              )}
              <Button onClick={handleNext} size="lg">
                Siguiente pregunta →
              </Button>
            </div>
          </div>

          {/* Chat socrático — visible solo si el estudiante lo abre y tiene API key */}
          {showChat && currentItem && apiKey && (
            <SocraticChat
              itemId={currentItem.id}
              itemContent={currentItem.content}
              courseId={courseId ?? ""}
              apiKey={apiKey}
              provider={provider}
            />
          )}

          {/* Aviso si no hay API key configurada */}
          {!lastAnswer.isCorrect && !apiKey && (
            <p className="text-xs text-slate-500 text-center">
              Configura una API key de IA en el sidebar para usar el chat socrático de KatIA.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
