/**
 * pages/Student/Exam.tsx
 * =======================
 * Modo examen cronometrado: configuración → N preguntas → timer → resultados.
 * Sin KatIA ni feedback inmediato. ELO se actualiza al enviar todas las respuestas.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import katex from "katex";
import "katex/dist/katex.min.css";
import { studentApi } from "../../api/student";
import { api, resolveImageUrl } from "../../api/client";

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

// ── Persistencia de borrador (sobrevive recarga si falla el submit) ──────────

const DRAFT_KEY = "levelup-exam-draft";
const DRAFT_MAX_AGE_MS = 6 * 60 * 60 * 1000; // 6 horas

interface ExamDraft {
  courseId: string;
  courseName: string;
  nQuestions: number;
  timeLimitMin: number;
  templateId: number | null;
  items: ExamItem[];
  answers: Record<string, string>;
  itemTimes: Record<string, number>;
  startedAt: number; // ms epoch al recibir items del backend
  timeLimitSeconds: number; // tiempo total inicial
  savedAt: number;
}

function readDraft(): ExamDraft | null {
  try {
    const raw = localStorage.getItem(DRAFT_KEY);
    if (!raw) return null;
    const d = JSON.parse(raw) as ExamDraft;
    if (!d || typeof d !== "object" || !Array.isArray(d.items)) return null;
    if (Date.now() - d.savedAt > DRAFT_MAX_AGE_MS) {
      localStorage.removeItem(DRAFT_KEY);
      return null;
    }
    return d;
  } catch {
    return null;
  }
}

function writeDraft(d: ExamDraft) {
  try {
    localStorage.setItem(DRAFT_KEY, JSON.stringify({ ...d, savedAt: Date.now() }));
  } catch {
    // QuotaExceeded u otro — silencioso, el examen puede continuar igual
  }
}

function clearDraft() {
  try {
    localStorage.removeItem(DRAFT_KEY);
  } catch {
    /* noop */
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function RenderMath({ text }: { text: string }) {
  const parts = text.split(/(\$[^$]+\$)/g);
  if (parts.length === 1) return <>{text}</>;
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith("$") && part.endsWith("$")) {
          const math = part.slice(1, -1);
          try {
            const html = katex.renderToString(math, {
              displayMode: false,
              throwOnError: false,
              errorColor: "#ef4444",
            });
            return (
              <span
                key={i}
                className="inline-block align-middle"
                dangerouslySetInnerHTML={{ __html: html }}
              />
            );
          } catch {
            return <span key={i}>{part}</span>;
          }
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
}

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

// ── Pantalla de configuración ─────────────────────────────────────────────────

function ExamSetup({
  onStart,
  onResume,
}: {
  onStart: (
    courseId: string,
    courseName: string,
    n: number,
    t: number,
    templateId?: number,
  ) => void;
  onResume: (draft: ExamDraft) => void;
}) {
  const [selectedCourse, setSelectedCourse] = useState("");
  const [nQuestions, setNQuestions] = useState(10);
  const [timeLimitMin, setTimeLimitMin] = useState(20);
  const [mode, setMode] = useState<"standard" | "template">("standard");
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);
  const [pendingDraft, setPendingDraft] = useState<ExamDraft | null>(() => readDraft());

  const { data: courses = [], isLoading } = useQuery({
    queryKey: ["courses"],
    queryFn: () => studentApi.courses(),
  });

  const { data: templates = [], isLoading: loadingTemplates } = useQuery({
    queryKey: ["exam-templates", selectedCourse],
    queryFn: () => studentApi.examTemplates(selectedCourse),
    enabled: !!selectedCourse,
  });

  const enrolled = courses.filter((c) => c.enrolled);
  const activeTemplate = templates.find((t) => t.id === selectedTemplate) ?? null;

  return (
    <div className="max-w-md mx-auto py-10 px-4">
      <h2 className="text-xl font-bold text-slate-100 mb-1">Modo Examen</h2>
      <p className="text-sm text-slate-400 mb-6">
        Responde N preguntas con tiempo límite y curva de dificultad estándar
        (fácil → difícil). Sin pistas ni retroalimentación inmediata.{" "}
        <span className="text-amber-400">El examen no afecta tu ELO</span> — es una
        evaluación. El ELO se ajusta solo en la sala de práctica.
      </p>

      {pendingDraft && (
        <div
          role="alert"
          className="mb-6 border border-amber-500/40 bg-amber-500/10 rounded-xl p-4"
        >
          <p className="text-sm font-medium text-amber-200">
            Tienes un examen pendiente
          </p>
          <p className="text-xs text-amber-300/80 mt-1 mb-3">
            {pendingDraft.courseName} ·{" "}
            {Object.keys(pendingDraft.answers).length}/{pendingDraft.items.length} respondidas
            · guardado{" "}
            {(() => {
              const mins = Math.max(
                0,
                Math.round((Date.now() - pendingDraft.savedAt) / 60000),
              );
              return mins === 0 ? "ahora" : `hace ${mins} min`;
            })()}
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => onResume(pendingDraft)}
              className="flex-1 bg-amber-500 hover:bg-amber-400 text-slate-900 font-medium text-xs py-2 rounded-lg transition-colors"
            >
              Continuar examen
            </button>
            <button
              type="button"
              onClick={() => {
                clearDraft();
                setPendingDraft(null);
              }}
              className="px-3 text-xs text-amber-300/70 hover:text-amber-200 transition-colors"
            >
              Descartar
            </button>
          </div>
        </div>
      )}

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

        {/* Selector de tipo de examen — visible solo si hay curso elegido */}
        {selectedCourse && (
          <div>
            <label className="block text-xs text-slate-400 mb-1.5">Tipo de examen</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => { setMode("standard"); setSelectedTemplate(null); }}
                className={[
                  "text-xs px-3 py-2 rounded-lg border transition-colors",
                  mode === "standard"
                    ? "bg-violet-600 border-violet-500 text-white font-medium"
                    : "bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700",
                ].join(" ")}
              >
                Estándar (auto)
              </button>
              <button
                type="button"
                onClick={() => setMode("template")}
                disabled={!loadingTemplates && templates.length === 0}
                className={[
                  "text-xs px-3 py-2 rounded-lg border transition-colors",
                  mode === "template"
                    ? "bg-violet-600 border-violet-500 text-white font-medium"
                    : "bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700",
                  "disabled:opacity-40 disabled:cursor-not-allowed",
                ].join(" ")}
                title={templates.length === 0 ? "El docente no ha creado exámenes para este curso" : ""}
              >
                Del docente
                {!loadingTemplates && (
                  <span className="text-[10px] ml-1 opacity-80">
                    ({templates.length})
                  </span>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Dropdown de plantillas (solo modo template) */}
        {selectedCourse && mode === "template" && (
          <div>
            <label className="block text-xs text-slate-400 mb-1.5">Examen del docente</label>
            {loadingTemplates ? (
              <div className="h-10 bg-slate-800 rounded-lg animate-pulse" />
            ) : templates.length === 0 ? (
              <p className="text-xs text-slate-500 italic">
                El docente aún no ha publicado exámenes para este curso.
              </p>
            ) : (
              <select
                value={selectedTemplate ?? ""}
                onChange={(e) => setSelectedTemplate(e.target.value ? Number(e.target.value) : null)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2.5 text-slate-200 text-sm focus:outline-none focus:border-violet-500 transition-colors"
              >
                <option value="">Selecciona un examen…</option>
                {templates.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.title} · {t.n_questions} preg · {t.time_limit_min} min
                  </option>
                ))}
              </select>
            )}
          </div>
        )}

        {/* Sliders solo en modo estándar */}
        {mode === "standard" && (
          <>
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
          </>
        )}

        {/* Resumen */}
        {selectedCourse && (
          <div className="bg-slate-800/60 border border-slate-700 rounded-xl px-4 py-3 text-xs text-slate-400 space-y-1">
            <div className="flex justify-between">
              <span>Curso</span>
              <span className="text-slate-200">
                {enrolled.find((c) => c.id === selectedCourse)?.name ?? selectedCourse}
              </span>
            </div>
            {mode === "template" && activeTemplate ? (
              <>
                <div className="flex justify-between">
                  <span>Examen del docente</span>
                  <span className="text-slate-200">{activeTemplate.title}</span>
                </div>
                <div className="flex justify-between">
                  <span>Preguntas</span>
                  <span className="text-slate-200">{activeTemplate.n_questions}</span>
                </div>
                <div className="flex justify-between">
                  <span>Tiempo</span>
                  <span className="text-slate-200">{activeTemplate.time_limit_min} minutos</span>
                </div>
              </>
            ) : (
              <>
                <div className="flex justify-between">
                  <span>Modo</span>
                  <span className="text-slate-200">Estándar (curva 30/40/30)</span>
                </div>
                <div className="flex justify-between">
                  <span>Preguntas</span>
                  <span className="text-slate-200">{nQuestions}</span>
                </div>
                <div className="flex justify-between">
                  <span>Tiempo</span>
                  <span className="text-slate-200">{timeLimitMin} minutos</span>
                </div>
              </>
            )}
          </div>
        )}

        <button
          onClick={() => {
            const name = enrolled.find((c) => c.id === selectedCourse)?.name ?? selectedCourse;
            if (mode === "template" && activeTemplate) {
              onStart(
                selectedCourse,
                name,
                activeTemplate.n_questions,
                activeTemplate.time_limit_min,
                activeTemplate.id,
              );
            } else {
              onStart(selectedCourse, name, nQuestions, timeLimitMin);
            }
          }}
          disabled={
            !selectedCourse ||
            (mode === "template" && !activeTemplate)
          }
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

  // Si hay un borrador pendiente, siempre arrancar en setup para que el
  // estudiante decida si continuar o descartar — los params de URL pueden
  // llevarlo a un examen nuevo y perder lo que tenía guardado.
  const [phase, setPhase] = useState<ExamPhase>(() =>
    readDraft() ? "setup" : courseIdParam ? "loading" : "setup",
  );
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
  const [showConfirm, setShowConfirm] = useState(false);
  const [templateId, setTemplateId] = useState<number | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitAttempt, setSubmitAttempt] = useState(0);

  const itemStartTime = useRef<number>(Date.now());
  const itemTimes = useRef<Record<string, number>>({});
  const submitRef = useRef<(() => void) | null>(null);
  const startedAtRef = useRef<number>(Date.now());
  const timeLimitSecondsRef = useRef<number>(0);

  const handleStart = useCallback(
    (cId: string, cName: string, n: number, t: number, tplId?: number) => {
      setCourseId(cId);
      setCourseName(cName);
      setNQuestions(n);
      setTimeLimitMin(t);
      setTemplateId(tplId ?? null);
      setItems([]);
      setCurrentIdx(0);
      setAnswers({});
      itemTimes.current = {};
      setSubmitError(null);
      setSubmitAttempt(0);
      setPhase("loading");
    },
    [],
  );

  const handleResume = useCallback((draft: ExamDraft) => {
    setCourseId(draft.courseId);
    setCourseName(draft.courseName);
    setNQuestions(draft.nQuestions);
    setTimeLimitMin(draft.timeLimitMin);
    setTemplateId(draft.templateId);
    setItems(draft.items);
    setAnswers(draft.answers);
    itemTimes.current = { ...draft.itemTimes };
    startedAtRef.current = draft.startedAt;
    timeLimitSecondsRef.current = draft.timeLimitSeconds;
    const elapsedSeconds = (Date.now() - draft.startedAt) / 1000;
    setTimeLeft(Math.max(0, Math.floor(draft.timeLimitSeconds - elapsedSeconds)));
    setCurrentIdx(0);
    itemStartTime.current = Date.now();
    setSubmitError(null);
    setSubmitAttempt(0);
    setPhase("answering");
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
        template_id: templateId ?? undefined,
      })
      .then((data) => {
        setItems(data.items);
        setTimeLeft(data.time_limit_seconds);
        itemStartTime.current = Date.now();
        startedAtRef.current = Date.now();
        timeLimitSecondsRef.current = data.time_limit_seconds;
        setPhase("answering");
      })
      .catch(() => {
        setError("No se pudo iniciar el examen. Intenta de nuevo.");
        setPhase("error");
      });
  }, [phase, courseId, nQuestions, timeLimitMin, templateId]);

  // ── Auto-guardar borrador para resistir caídas de red al enviar ──────────
  useEffect(() => {
    if (phase !== "answering" || items.length === 0) return;
    writeDraft({
      courseId,
      courseName,
      nQuestions,
      timeLimitMin,
      templateId,
      items,
      answers,
      itemTimes: itemTimes.current,
      startedAt: startedAtRef.current,
      timeLimitSeconds: timeLimitSecondsRef.current,
      savedAt: Date.now(),
    });
  }, [phase, items, answers, currentIdx, courseId, courseName, nQuestions, timeLimitMin, templateId]);

  // ── Enviar examen ──────────────────────────────────────────────────────────

  const handleSubmit = useCallback(async () => {
    setPhase("submitting");
    setSubmitError(null);

    const elapsed = (Date.now() - itemStartTime.current) / 1000;
    if (items[currentIdx]) {
      itemTimes.current[items[currentIdx].id] =
        (itemTimes.current[items[currentIdx].id] ?? 0) + elapsed;
    }
    // Reset para que reintentos posteriores no doble-cuenten el tiempo en pantalla
    itemStartTime.current = Date.now();

    const payload = {
      course_id: courseId,
      course_name: courseName,
      answers: items.map((item) => ({
        item_id: item.id,
        selected_option: answers[item.id] ?? "",
        time_taken: itemTimes.current[item.id] ?? 0,
      })),
    };

    // Reintentos con backoff: 0s, 3s, 8s. Cada api.post ya añade su propio retry
    // de cold start, así que en el peor caso son 3 × (1 + 1 cold) = 6 intentos.
    const backoffs = [0, 3000, 8000];
    let lastError: unknown = null;

    for (let attempt = 0; attempt < backoffs.length; attempt++) {
      if (backoffs[attempt] > 0) {
        await new Promise((r) => setTimeout(r, backoffs[attempt]));
      }
      setSubmitAttempt(attempt + 1);
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
        clearDraft();
        setSubmitAttempt(0);
        setPhase("results");
        return;
      } catch (err) {
        lastError = err;
      }
    }

    // Los 3 intentos fallaron — mantener al estudiante en "answering" con
    // el banner de error visible. El borrador sigue en localStorage, así
    // que aunque recargue la página puede reintentar.
    void lastError;
    setSubmitError(
      "No pudimos enviar tu examen tras varios intentos. Tus respuestas siguen guardadas — puedes reintentar.",
    );
    setSubmitAttempt(0);
    setPhase("answering");
  }, [items, currentIdx, answers, courseId, courseName]);

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

  if (phase === "setup") return <ExamSetup onStart={handleStart} onResume={handleResume} />;

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
            onClick={() => { setPhase("setup"); setAnswers({}); setItems([]); setCurrentIdx(0); }}
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
          <h1 className="text-2xl font-bold text-slate-100 mb-4">{label}</h1>
          <div className="flex items-center justify-center gap-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-slate-100 tabular-nums">{score.pct}%</p>
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
          <p className="text-xs text-slate-500 mt-4">
            Calificado automáticamente · las respuestas correctas provienen del banco de preguntas.
          </p>
          <p className="text-xs text-amber-400 mt-1">
            Este examen no modificó tu ELO. Para subir tu rating, practica en la sala adaptativa.
          </p>
        </div>

        {/* Mini-mapa de resultados */}
        <div className="flex flex-wrap gap-1.5 justify-center mb-6 max-w-md mx-auto" role="group" aria-label="Resumen de respuestas">
          {results.map((r, i) => (
            <span
              key={r.item_id}
              title={`Pregunta ${i + 1}: ${r.is_correct ? "correcta" : "incorrecta"}`}
              className={[
                "w-8 h-8 rounded text-xs font-bold flex items-center justify-center border",
                r.is_correct
                  ? "bg-emerald-600 text-white border-emerald-400"
                  : "bg-red-600 text-white border-red-400",
              ].join(" ")}
            >
              {i + 1}
            </span>
          ))}
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
                    {item ? <RenderMath text={item.content} /> : r.item_id}
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
            onClick={() => { setPhase("setup"); setAnswers({}); setItems([]); setCurrentIdx(0); }}
            className="bg-slate-700 hover:bg-slate-600 text-slate-100 px-5 py-2 rounded-xl text-sm transition-colors"
          >
            Nuevo examen
          </button>
          <button
            onClick={() => navigate("/student")}
            className="bg-slate-700 hover:bg-slate-600 text-slate-100 px-5 py-2 rounded-xl text-sm transition-colors"
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
      {/* Banner de error de envío — visible si fallaron los reintentos */}
      {submitError && (
        <div
          role="alert"
          className="px-4 md:px-6 py-3 border-b border-red-700/50 bg-red-900/30 flex items-center justify-between gap-3 shrink-0"
        >
          <div className="min-w-0">
            <p className="text-sm font-medium text-red-200">
              No se pudo enviar el examen
            </p>
            <p className="text-xs text-red-300/80 mt-0.5 truncate">
              {submitError}
            </p>
          </div>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={phase === "submitting"}
            className="shrink-0 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white text-xs font-medium px-4 py-2 rounded-lg transition-colors"
          >
            Reintentar enviar
          </button>
        </div>
      )}

      {/* Banner de progreso de reintentos */}
      {phase === "submitting" && submitAttempt > 1 && (
        <div
          role="status"
          aria-live="polite"
          className="px-4 md:px-6 py-2 border-b border-amber-700/50 bg-amber-900/30 text-xs text-amber-200 shrink-0"
        >
          Reintentando envío (intento {submitAttempt} de 3)…
        </div>
      )}

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
          <p className="text-[10px] text-slate-500">
            {answeredCount}/{items.length} respondidas
          </p>
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
                  "w-full h-8 rounded text-xs font-bold transition-all border",
                  active
                    ? "bg-violet-600 text-white border-violet-400 ring-2 ring-violet-400"
                    : answered
                    ? "bg-amber-500 text-slate-900 border-amber-400 hover:bg-amber-400"
                    : "bg-slate-700 text-slate-300 border-slate-600 hover:bg-slate-600",
                ].join(" ")}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>

        {/* Modal de confirmación */}
        {showConfirm && (
          <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
            <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 max-w-sm w-full mx-4 shadow-2xl">
              <h3 className="text-lg font-bold text-slate-100 mb-2">¿Finalizar examen?</h3>
              <div className="text-sm text-slate-400 space-y-1 mb-5">
                <p>Respondidas: <span className="text-emerald-400 font-semibold">{answeredCount}</span> de {items.length}</p>
                {answeredCount < items.length && (
                  <p className="text-amber-400">⚠️ {items.length - answeredCount} pregunta{items.length - answeredCount !== 1 ? "s" : ""} sin responder</p>
                )}
                <p className="text-slate-500 text-xs mt-2">Las respuestas en blanco cuentan como incorrectas.</p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowConfirm(false)}
                  className="flex-1 bg-slate-700 hover:bg-slate-600 text-slate-200 py-2.5 rounded-xl text-sm transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={() => { setShowConfirm(false); handleSubmit(); }}
                  className="flex-1 bg-violet-600 hover:bg-violet-700 text-white py-2.5 rounded-xl text-sm font-medium transition-colors"
                >
                  Sí, finalizar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Pregunta actual */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6">
          {currentItem && (
            <div className="max-w-2xl mx-auto">
              <p className="text-[10px] text-slate-500 mb-3 uppercase tracking-wide">
                Pregunta {currentIdx + 1} de {items.length}
              </p>

              <div className="bg-slate-800 rounded-xl p-5 mb-5 border border-slate-700">
                <p className="text-slate-200 leading-relaxed text-[15px]">
                  <RenderMath text={currentItem.content} />
                </p>
                {resolveImageUrl(currentItem.image_url) && (
                  <img
                    src={resolveImageUrl(currentItem.image_url)}
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
                      <RenderMath text={opt} />
                    </button>
                  );
                })}
              </div>

              {/* Navegación + finalizar */}
              <div className="mt-6 space-y-3">
                <div className="flex gap-3">
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

                <div className="flex items-center justify-between pt-3 border-t border-slate-700">
                  <span className="text-xs text-slate-500">
                    {answeredCount}/{items.length} respondidas
                  </span>
                  <button
                    onClick={() => setShowConfirm(true)}
                    disabled={phase === "submitting"}
                    className="bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white text-sm px-5 py-2 rounded-xl transition-colors font-medium"
                  >
                    {phase === "submitting" ? "Enviando…" : "Finalizar examen"}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
