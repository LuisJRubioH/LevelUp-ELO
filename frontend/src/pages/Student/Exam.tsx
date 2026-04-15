/**
 * pages/Student/Exam.tsx
 * =======================
 * Modo examen cronometrado: N preguntas, tiempo límite, sin KatIA.
 * El estudiante selecciona sus respuestas y al terminar (o al agotar el tiempo)
 * se envían todas de una vez y se muestra el resultado.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { InlineMath } from "react-katex";
import "katex/dist/katex.min.css";
import { apiClient } from "../../api/client";

// ── Tipos ─────────────────────────────────────────────────────────────────────

interface ExamItem {
  id: string;
  content: string;
  difficulty: number;
  topic: string;
  options: string[];
  image_url?: string;
}

interface ExamResult {
  item_id: string;
  is_correct: boolean;
  selected_option: string;
  elo_delta: number;
}

type ExamPhase = "loading" | "answering" | "submitting" | "results" | "error";

// ── Helpers ───────────────────────────────────────────────────────────────────

function renderMath(text: string) {
  const parts = text.split(/(\$[^$]+\$)/g);
  return parts.map((part, i) => {
    if (part.startsWith("$") && part.endsWith("$")) {
      const formula = part.slice(1, -1);
      return (
        <span key={i}>
          <InlineMath math={formula} />
        </span>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

// ── Componente principal ───────────────────────────────────────────────────────

export function Exam() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const courseId = searchParams.get("course") ?? "";
  const nQuestions = parseInt(searchParams.get("n") ?? "10", 10);
  const timeLimitMin = parseInt(searchParams.get("t") ?? "20", 10);

  const [phase, setPhase] = useState<ExamPhase>("loading");
  const [items, setItems] = useState<ExamItem[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({}); // item_id → selected_option
  const [timeLeft, setTimeLeft] = useState(0);
  const [results, setResults] = useState<ExamResult[]>([]);
  const [score, setScore] = useState({ correct: 0, total: 0, pct: 0, eloAfter: 0 });
  const [error, setError] = useState("");

  const itemStartTime = useRef<number>(Date.now());
  const itemTimes = useRef<Record<string, number>>({}); // item_id → segundos

  // ── Cargar examen ──────────────────────────────────────────────────────────

  useEffect(() => {
    if (!courseId) {
      setError("No se especificó un curso para el examen.");
      setPhase("error");
      return;
    }

    apiClient
      .post<{
        items: ExamItem[];
        n_questions: number;
        time_limit_seconds: number;
        course_id: string;
      }>("/student/exam/start", {
        course_id: courseId,
        n_questions: nQuestions,
        time_limit_minutes: timeLimitMin,
      })
      .then((data) => {
        setItems(data.items);
        setTimeLeft(data.time_limit_seconds);
        itemStartTime.current = Date.now();
        setPhase("answering");
      })
      .catch(() => {
        setError("No se pudo iniciar el examen. Intenta de nuevo.");
        setPhase("error");
      });
  }, [courseId, nQuestions, timeLimitMin]);

  // ── Temporizador ───────────────────────────────────────────────────────────

  useEffect(() => {
    if (phase !== "answering") return;
    const interval = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(interval);
          handleSubmit();
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [phase]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Seleccionar respuesta ──────────────────────────────────────────────────

  const selectAnswer = (itemId: string, option: string) => {
    setAnswers((prev) => ({ ...prev, [itemId]: option }));
  };

  // ── Navegar entre preguntas ────────────────────────────────────────────────

  const goToQuestion = useCallback(
    (idx: number) => {
      // Registrar tiempo en la pregunta actual
      const elapsed = (Date.now() - itemStartTime.current) / 1000;
      if (items[currentIdx]) {
        itemTimes.current[items[currentIdx].id] =
          (itemTimes.current[items[currentIdx].id] ?? 0) + elapsed;
      }
      itemStartTime.current = Date.now();
      setCurrentIdx(idx);
    },
    [currentIdx, items]
  );

  // ── Enviar examen ──────────────────────────────────────────────────────────

  const handleSubmit = useCallback(async () => {
    if (phase !== "answering") return;
    setPhase("submitting");

    // Capturar tiempo final en la pregunta actual
    const elapsed = (Date.now() - itemStartTime.current) / 1000;
    if (items[currentIdx]) {
      itemTimes.current[items[currentIdx].id] =
        (itemTimes.current[items[currentIdx].id] ?? 0) + elapsed;
    }

    const payload = {
      answers: items.map((item) => ({
        item_id: item.id,
        selected_option: answers[item.id] ?? "",
        time_taken: itemTimes.current[item.id] ?? 0,
      })),
    };

    try {
      const res = await apiClient.post<{
        results: ExamResult[];
        correct_count: number;
        total_questions: number;
        score_pct: number;
        global_elo_after: number;
      }>("/student/exam/submit", payload);

      setResults(res.results);
      setScore({
        correct: res.correct_count,
        total: res.total_questions,
        pct: res.score_pct,
        eloAfter: res.global_elo_after,
      });
      setPhase("results");
    } catch {
      setError("Error al enviar el examen. Tus respuestas se perdieron.");
      setPhase("error");
    }
  }, [phase, items, currentIdx, answers]);

  const currentItem = items[currentIdx];
  const answeredCount = Object.keys(answers).length;
  const timerColor = timeLeft < 60 ? "text-red-400" : timeLeft < 300 ? "text-amber-400" : "text-green-400";

  // ── Render: cargando ───────────────────────────────────────────────────────

  if (phase === "loading") {
    return (
      <div className="flex items-center justify-center h-full text-slate-400">
        <div className="text-center">
          <div className="text-4xl mb-3">⏳</div>
          <p>Preparando examen…</p>
        </div>
      </div>
    );
  }

  if (phase === "error") {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <div className="text-4xl mb-3">❌</div>
          <p className="text-slate-300 mb-4">{error}</p>
          <button
            onClick={() => navigate("/student")}
            className="bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg text-sm"
          >
            Volver a práctica
          </button>
        </div>
      </div>
    );
  }

  // ── Render: resultados ─────────────────────────────────────────────────────

  if (phase === "results") {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <div className="text-6xl mb-3">{score.pct >= 80 ? "🏆" : score.pct >= 60 ? "🎯" : "📚"}</div>
          <h1 className="text-2xl font-bold text-white mb-1">Examen terminado</h1>
          <p className="text-slate-400">
            {score.correct} de {score.total} correctas · {score.pct}%
          </p>
          <p className="text-sm text-violet-400 mt-1">ELO global: {score.eloAfter}</p>
        </div>

        {/* Tabla de resultados */}
        <div className="space-y-3 mb-8">
          {results.map((r, i) => {
            const item = items.find((it) => it.id === r.item_id);
            return (
              <div
                key={r.item_id}
                className={[
                  "rounded-xl border p-4",
                  r.is_correct
                    ? "border-emerald-700 bg-emerald-900/20"
                    : "border-red-700 bg-red-900/20",
                ].join(" ")}
              >
                <div className="flex items-start gap-3">
                  <span className="text-lg mt-0.5">{r.is_correct ? "✅" : "❌"}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-slate-500 mb-1">Pregunta {i + 1}</p>
                    <p className="text-sm text-slate-300 leading-snug">
                      {item ? renderMath(item.content) : r.item_id}
                    </p>
                    {r.elo_delta !== 0 && (
                      <p
                        className={[
                          "text-xs mt-1",
                          r.elo_delta > 0 ? "text-emerald-500" : "text-red-500",
                        ].join(" ")}
                      >
                        ELO {r.elo_delta > 0 ? "+" : ""}{r.elo_delta}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex gap-3 justify-center">
          <button
            onClick={() => navigate("/student")}
            className="bg-slate-700 hover:bg-slate-600 text-white px-5 py-2 rounded-lg text-sm"
          >
            Volver a práctica
          </button>
          <button
            onClick={() => navigate("/student/stats")}
            className="bg-violet-600 hover:bg-violet-700 text-white px-5 py-2 rounded-lg text-sm"
          >
            Ver mis estadísticas
          </button>
        </div>
      </div>
    );
  }

  // ── Render: examen en progreso ─────────────────────────────────────────────

  return (
    <div className="h-full flex flex-col">
      {/* Header con timer y progreso */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-slate-700 bg-slate-800">
        <div>
          <span className="text-xs text-slate-500 uppercase tracking-wide">Examen</span>
          <p className="text-sm text-slate-300 font-medium">{courseId}</p>
        </div>

        {/* Timer */}
        <div className={`text-2xl font-mono font-bold ${timerColor}`}>{formatTime(timeLeft)}</div>

        <div className="text-right">
          <p className="text-xs text-slate-500">
            {answeredCount}/{items.length} respondidas
          </p>
          <button
            onClick={handleSubmit}
            disabled={phase === "submitting"}
            className="mt-1 bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white text-xs px-3 py-1 rounded-lg"
          >
            {phase === "submitting" ? "Enviando…" : "Finalizar"}
          </button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Panel lateral: mapa de preguntas */}
        <div className="w-20 border-r border-slate-700 p-2 flex flex-col gap-1 overflow-y-auto shrink-0">
          {items.map((item, idx) => {
            const answered = item.id in answers;
            const active = idx === currentIdx;
            return (
              <button
                key={item.id}
                onClick={() => goToQuestion(idx)}
                className={[
                  "w-full h-9 rounded text-xs font-bold transition-all",
                  active
                    ? "bg-violet-600 text-white ring-2 ring-violet-400"
                    : answered
                    ? "bg-emerald-700 text-white"
                    : "bg-slate-700 text-slate-400 hover:bg-slate-600",
                ].join(" ")}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>

        {/* Pregunta actual */}
        <div className="flex-1 overflow-y-auto p-6">
          {currentItem && (
            <div className="max-w-2xl mx-auto">
              <p className="text-xs text-slate-500 mb-3 uppercase tracking-wide">
                Pregunta {currentIdx + 1} de {items.length}
              </p>

              <div className="bg-slate-800 rounded-xl p-5 mb-5 border border-slate-700">
                <p className="text-slate-200 leading-relaxed text-base">
                  {renderMath(currentItem.content)}
                </p>
                {currentItem.image_url && (
                  <img
                    src={currentItem.image_url}
                    alt="Figura"
                    className="mt-4 max-w-full rounded-lg"
                  />
                )}
              </div>

              {/* Opciones */}
              <div className="space-y-3">
                {currentItem.options.map((opt) => {
                  const selected = answers[currentItem.id] === opt;
                  return (
                    <button
                      key={opt}
                      onClick={() => selectAnswer(currentItem.id, opt)}
                      className={[
                        "w-full text-left px-4 py-3 rounded-xl border text-sm transition-all",
                        selected
                          ? "border-violet-500 bg-violet-600/20 text-violet-200 ring-1 ring-violet-500"
                          : "border-slate-600 bg-slate-800/60 text-slate-300 hover:border-slate-500 hover:bg-slate-700/60",
                      ].join(" ")}
                    >
                      {renderMath(opt)}
                    </button>
                  );
                })}
              </div>

              {/* Navegación entre preguntas */}
              <div className="flex gap-3 mt-6">
                {currentIdx > 0 && (
                  <button
                    onClick={() => goToQuestion(currentIdx - 1)}
                    className="bg-slate-700 hover:bg-slate-600 text-slate-300 px-4 py-2 rounded-lg text-sm"
                  >
                    ← Anterior
                  </button>
                )}
                {currentIdx < items.length - 1 && (
                  <button
                    onClick={() => goToQuestion(currentIdx + 1)}
                    className="ml-auto bg-slate-700 hover:bg-slate-600 text-slate-300 px-4 py-2 rounded-lg text-sm"
                  >
                    Siguiente →
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
