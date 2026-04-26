/**
 * pages/Student/Exam.tsx
 * =======================
 * Modo examen cronometrado: configuración → N preguntas → timer → resultados.
 * Sin KatIA ni feedback inmediato. ELO se actualiza al enviar todas las respuestas.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { InlineMath } from "react-katex";
import "katex/dist/katex.min.css";
import { studentApi } from "../../api/student";
import { api } from "../../api/client";

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

type ExamPhase = "setup" | "loading" | "answering" | "submitting" | "results" | "error";

// ── Helpers ───────────────────────────────────────────────────────────────────

function renderMath(text: string) {
  const parts = text.split(/(\$[^$]+\$)/g);
  return parts.map((part, i) => {
    if (part.startsWith("$") && part.endsWith("$")) {
      return (
        <span key={i}>
          <InlineMath math={part.slice(1, -1)} />
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

// ── Pantalla de configuración ─────────────────────────────────────────────────

function ExamSetup({ onStart }: { onStart: (courseId: string, courseName: string, n: number, t: number) => void }) {
  const [selectedCourse, setSelectedCourse] = useState("");
  const [nQuestions, setNQuestions] = useState(10);
  const [timeLimitMin, setTimeLimitMin] = useState(20);

  const { data: courses = [], isLoading } = useQuery({
    queryKey: ["courses"],
    queryFn: () => studentApi.courses(),
  });

  const enrolled = courses.filter((c) => c.enrolled);

  return (
    <div className="max-w-md mx-auto py-10 px-4">
      <h2 className="text-xl font-bold text-white mb-1">Modo Examen</h2>
      <p className="text-sm text-slate-400 mb-6">
        Responde N preguntas adaptativas con tiempo límite. Sin pistas ni retroalimentación
        inmediata. El ELO se actualiza al finalizar.
      </p>

      <div className="space-y-5">
        {/* Selector de curso */}
        <div>
          <label className="block text-xs text-slate-400 mb-1.5">Curso</label>
          {isLoading ? (
            <div className="h-10 bg-slate-800 rounded-lg animate-pulse" />
          ) : enrolled.length === 0 ? (
            <p className="text-sm text-slate-500 italic">
              No estás matriculado en ningún curso.{" "}
              <a href="/student/courses" className="text-violet-400 hover:underline">
                Ir a cursos →
              </a>
            </p>
          ) : (
            <select
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-slate-200 text-sm focus:outline-none focus:border-violet-500 transition-colors"
            >
              <option value="">Selecciona un curso…</option>
              {enrolled.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Número de preguntas */}
        <div>
          <label className="block text-xs text-slate-400 mb-1.5">
            Preguntas:{" "}
            <span className="text-violet-400 font-semibold">{nQuestions}</span>
          </label>
          <input
            type="range"
            min={5}
            max={30}
            step={5}
            value={nQuestions}
            onChange={(e) => setNQuestions(Number(e.target.value))}
            className="w-full accent-violet-500"
          />
          <div className="flex justify-between text-[10px] text-slate-600 mt-1">
            {[5, 10, 15, 20, 25, 30].map((v) => (
              <span key={v}>{v}</span>
            ))}
          </div>
        </div>

        {/* Tiempo límite */}
        <div>
          <label className="block text-xs text-slate-400 mb-1.5">
            Tiempo límite:{" "}
            <span className="text-violet-400 font-semibold">{timeLimitMin} min</span>
          </label>
          <input
            type="range"
            min={5}
            max={60}
            step={5}
            value={timeLimitMin}
            onChange={(e) => setTimeLimitMin(Number(e.target.value))}
            className="w-full accent-violet-500"
          />
          <div className="flex justify-between text-[10px] text-slate-600 mt-1">
            <span>5 min</span>
            <span>30 min</span>
            <span>60 min</span>
          </div>
        </div>

        {/* Resumen */}
        {selectedCourse && (
          <div className="bg-slate-800/60 border border-slate-700 rounded-xl px-4 py-3 text-xs text-slate-400 space-y-1">
            <div className="flex justify-between">
              <span>Curso</span>
              <span className="text-slate-200">
                {enrolled.find((c) => c.id === selectedCourse)?.name ?? selectedCourse}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Preguntas</span>
              <span className="text-slate-200">{nQuestions}</span>
            </div>
            <div className="flex justify-between">
              <span>Tiempo</span>
              <span className="text-slate-200">{timeLimitMin} minutos</span>
            </div>
          </div>
        )}

        <button
          onClick={() => {
            const name = enrolled.find((c) => c.id === selectedCourse)?.name ?? selectedCourse;
            onStart(selectedCourse, name, nQuestions, timeLimitMin);
          }}
          disabled={!selectedCourse}
          className="w-full bg-violet-600 hover:bg-violet-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium py-2.5 rounded-xl text-sm transition-colors"
        >
          Iniciar examen →
        </button>
      </div>
    </div>
  );
}

// ── Componente principal ───────────────────────────────────────────────────────

export function Exam() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const courseIdParam = searchParams.get("course") ?? "";
  const nParam = parseInt(searchParams.get("n") ?? "10", 10);
  const tParam = parseInt(searchParams.get("t") ?? "20", 10);

  const [phase, setPhase] = useState<ExamPhase>(courseIdParam ? "loading" : "setup");
  const [courseId, setCourseId] = useState(courseIdParam);
  const [courseName, setCourseName] = useState(courseIdParam);
  const [nQuestions, setNQuestions] = useState(nParam);
  const [timeLimitMin, setTimeLimitMin] = useState(tParam);

  const [items, setItems] = useState<ExamItem[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [results, setResults] = useState<ExamResult[]>([]);
  const [score, setScore] = useState({ correct: 0, total: 0, pct: 0, eloAfter: 0 });
  const [error, setError] = useState("");

  const itemStartTime = useRef<number>(Date.now());
  const itemTimes = useRef<Record<string, number>>({});
  const submitRef = useRef<(() => void) | null>(null);

  const handleStart = useCallback((cId: string, cName: string, n: number, t: number) => {
    setCourseId(cId);
    setCourseName(cName);
    setNQuestions(n);
    setTimeLimitMin(t);
    setItems([]);
    setCurrentIdx(0);
    setAnswers({});
    itemTimes.current = {};
    setPhase("loading");
  }, []);

  // ── Cargar examen ──────────────────────────────────────────────────────────

  useEffect(() => {
    if (phase !== "loading" || !courseId) return;

    api
      .post<{
        items: ExamItem[];
        n_questions: number;
        time_limit_seconds: number;
        course_id: string;
      }>("/api/student/exam/start", {
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
  }, [phase, courseId, nQuestions, timeLimitMin]);

  // ── Enviar examen ──────────────────────────────────────────────────────────

  const handleSubmit = useCallback(async () => {
    setPhase("submitting");

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
      const res = await api.post<{
        results: ExamResult[];
        correct_count: number;
        total_questions: number;
        score_pct: number;
        global_elo_after: number;
      }>("/api/student/exam/submit", payload);

      setResults(res.results);
      setScore({
        correct: res.correct_count,
        total: res.total_questions,
        pct: res.score_pct,
        eloAfter: res.global_elo_after,
      });
      setPhase("results");
    } catch {
      setError("Error al enviar el examen. Intenta recargar.");
      setPhase("error");
    }
  }, [items, currentIdx, answers]);

  // Mantener ref estable para el timer
  useEffect(() => {
    submitRef.current = handleSubmit;
  }, [handleSubmit]);

  // ── Temporizador ───────────────────────────────────────────────────────────

  useEffect(() => {
    if (phase !== "answering") return;
    const interval = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(interval);
          submitRef.current?.();
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [phase]);

  // ── Navegación entre preguntas ─────────────────────────────────────────────

  const goToQuestion = useCallback(
    (idx: number) => {
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

  const selectAnswer = (itemId: string, option: string) => {
    setAnswers((prev) => ({ ...prev, [itemId]: option }));
  };

  // ── Derivados ──────────────────────────────────────────────────────────────

  const currentItem = items[currentIdx];
  const answeredCount = Object.keys(answers).length;
  const timerColor =
    timeLeft < 60
      ? "text-red-400"
      : timeLeft < 300
      ? "text-amber-400"
      : "text-emerald-400";

  // ── Render: setup ──────────────────────────────────────────────────────────

  if (phase === "setup") return <ExamSetup onStart={handleStart} />;

  // ── Render: cargando ───────────────────────────────────────────────────────

  if (phase === "loading") {
    return (
      <div className="flex items-center justify-center h-full text-slate-400">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-2 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm">Preparando examen…</p>
        </div>
      </div>
    );
  }

  // ── Render: error ──────────────────────────────────────────────────────────

  if (phase === "error") {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-sm px-4">
          <div className="text-4xl mb-3">⚠️</div>
          <p className="text-slate-300 mb-4 text-sm">{error}</p>
          <button
            onClick={() => setPhase("setup")}
            className="bg-violet-600 hover:bg-violet-700 text-white px-5 py-2 rounded-xl text-sm transition-colors"
          >
            Volver a configuración
          </button>
        </div>
      </div>
    );
  }

  // ── Render: resultados ─────────────────────────────────────────────────────

  if (phase === "results") {
    const emoji = score.pct >= 80 ? "🏆" : score.pct >= 60 ? "🎯" : "📚";
    const label =
      score.pct >= 80 ? "¡Excelente trabajo!" : score.pct >= 60 ? "¡Buen resultado!" : "Sigue practicando";

    return (
      <div className="max-w-2xl mx-auto p-6">
        {/* Encabezado de resultados */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">{emoji}</div>
          <h1 className="text-2xl font-bold text-white mb-4">{label}</h1>
          <div className="flex items-center justify-center gap-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-white tabular-nums">{score.pct}%</p>
              <p className="text-xs text-slate-500 mt-0.5">puntuación</p>
            </div>
            <div className="w-px h-10 bg-slate-700" />
            <div className="text-center">
              <p className="text-3xl font-bold text-emerald-400 tabular-nums">{score.correct}</p>
              <p className="text-xs text-slate-500 mt-0.5">correctas</p>
            </div>
            <div className="w-px h-10 bg-slate-700" />
            <div className="text-center">
              <p className="text-3xl font-bold text-red-400 tabular-nums">
                {score.total - score.correct}
              </p>
              <p className="text-xs text-slate-500 mt-0.5">incorrectas</p>
            </div>
          </div>
          <p className="text-sm text-violet-400 mt-4">
            ELO global actualizado: <span className="font-semibold">{score.eloAfter}</span>
          </p>
        </div>

        {/* Detalle por pregunta */}
        <div className="space-y-2 mb-8">
          {results.map((r, i) => {
            const item = items.find((it) => it.id === r.item_id);
            return (
              <div
                key={r.item_id}
                className={[
                  "rounded-xl border p-3.5 flex items-start gap-3",
                  r.is_correct
                    ? "border-emerald-700/40 bg-emerald-900/10"
                    : "border-red-700/40 bg-red-900/10",
                ].join(" ")}
              >
                <span className="text-base shrink-0 mt-0.5">{r.is_correct ? "✅" : "❌"}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-[10px] text-slate-500 mb-0.5 uppercase tracking-wide">
                    Pregunta {i + 1}
                  </p>
                  <p className="text-sm text-slate-300 leading-snug line-clamp-2">
                    {item ? renderMath(item.content) : r.item_id}
                  </p>
                </div>
                {r.elo_delta !== 0 && (
                  <span
                    className={[
                      "text-xs font-mono shrink-0 mt-0.5",
                      r.elo_delta > 0 ? "text-emerald-500" : "text-red-500",
                    ].join(" ")}
                  >
                    {r.elo_delta > 0 ? "+" : ""}
                    {r.elo_delta}
                  </span>
                )}
              </div>
            );
          })}
        </div>

        <div className="flex flex-wrap gap-3 justify-center">
          <button
            onClick={() => setPhase("setup")}
            className="bg-slate-700 hover:bg-slate-600 text-white px-5 py-2 rounded-xl text-sm transition-colors"
          >
            Nuevo examen
          </button>
          <button
            onClick={() => navigate("/student")}
            className="bg-slate-700 hover:bg-slate-600 text-white px-5 py-2 rounded-xl text-sm transition-colors"
          >
            Practicar
          </button>
          <button
            onClick={() => navigate("/student/stats")}
            className="bg-violet-600 hover:bg-violet-700 text-white px-5 py-2 rounded-xl text-sm transition-colors"
          >
            Ver estadísticas →
          </button>
        </div>
      </div>
    );
  }

  // ── Render: examen en progreso (answering / submitting) ───────────────────

  return (
    <div className="h-full flex flex-col">
      {/* Header con timer */}
      <div className="flex items-center justify-between px-4 md:px-6 py-3 border-b border-slate-700 bg-slate-800/80 backdrop-blur-sm shrink-0">
        <div className="min-w-0">
          <span className="text-[10px] text-slate-500 uppercase tracking-wide">Examen</span>
          <p className="text-sm text-slate-300 font-medium truncate max-w-[120px] md:max-w-none">
            {courseName}
          </p>
        </div>

        {/* Timer */}
        <div
          className={`text-xl md:text-2xl font-mono font-bold tabular-nums ${timerColor}`}
          aria-live={timeLeft < 60 ? "assertive" : "off"}
          aria-label={`Tiempo restante: ${formatTime(timeLeft)}`}
          role="timer"
        >
          {formatTime(timeLeft)}
        </div>

        <div className="text-right">
          <p className="text-[10px] text-slate-500 mb-1">
            {answeredCount}/{items.length} respondidas
          </p>
          <button
            onClick={handleSubmit}
            disabled={phase === "submitting"}
            className="bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white text-xs px-3 py-1 rounded-lg transition-colors"
          >
            {phase === "submitting" ? "Enviando…" : "Finalizar"}
          </button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Mapa de preguntas */}
        <div className="w-14 md:w-20 border-r border-slate-700 py-3 px-1.5 flex flex-col gap-1 overflow-y-auto shrink-0">
          {items.map((item, idx) => {
            const answered = item.id in answers;
            const active = idx === currentIdx;
            return (
              <button
                key={item.id}
                onClick={() => goToQuestion(idx)}
                aria-label={`Pregunta ${idx + 1}${answered ? " (respondida)" : ""}${active ? ", actual" : ""}`}
                aria-current={active ? "true" : undefined}
                className={[
                  "w-full h-8 rounded text-xs font-bold transition-all",
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
        <div className="flex-1 overflow-y-auto p-4 md:p-6">
          {currentItem && (
            <div className="max-w-2xl mx-auto">
              <p className="text-[10px] text-slate-500 mb-3 uppercase tracking-wide">
                Pregunta {currentIdx + 1} de {items.length}
              </p>

              <div className="bg-slate-800 rounded-xl p-5 mb-5 border border-slate-700">
                <p className="text-slate-200 leading-relaxed text-[15px]">
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

              {/* Navegación prev / next */}
              <div className="flex gap-3 mt-6">
                {currentIdx > 0 && (
                  <button
                    onClick={() => goToQuestion(currentIdx - 1)}
                    className="bg-slate-700 hover:bg-slate-600 text-slate-300 px-4 py-2 rounded-lg text-sm transition-colors"
                  >
                    ← Anterior
                  </button>
                )}
                {currentIdx < items.length - 1 && (
                  <button
                    onClick={() => goToQuestion(currentIdx + 1)}
                    className="ml-auto bg-slate-700 hover:bg-slate-600 text-slate-300 px-4 py-2 rounded-lg text-sm transition-colors"
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
