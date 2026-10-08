/**
 * pages/Student/CourseEntry.tsx — Inicio de materia (P2)
 * =====================================================
 * Al entrar a una materia: si no hay diagnóstico → examen diagnóstico
 * (bienvenida → preguntas → resultado). Si ya está hecho → bifurcación
 * Practicar / Mapa de contenido. El diagnóstico fija el ELO inicial por
 * tópico (backend). Estilos en CourseEntry.css (.lue-dx).
 */

import { useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  studentApi,
  type DiagnosticQuestion,
  type DiagnosticResult,
} from "../../api/student";
import { usePracticeStore } from "../../stores/practiceStore";
import { ConcoursEntry } from "./ConcoursEntry";
import { MathText } from "../../components/Math/MathContent";
import "./CourseEntry.css";

const KEYS = ["A", "B", "C", "D", "E", "F"];

/* ── flujo del diagnóstico ───────────────────────────────────────────────── */
function Diagnostic({
  courseId,
  courseName,
  questions,
  onDone,
  onExit,
}: {
  courseId: string;
  courseName: string;
  questions: DiagnosticQuestion[];
  onDone: () => void;
  onExit: () => void;
}) {
  const [phase, setPhase] = useState<"welcome" | "quiz">("welcome");
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const total = questions.length;
  const q = questions[index];
  const selected = q ? answers[q.id] : undefined;
  const progress = Math.round((index / Math.max(1, total)) * 100);

  const advance = async () => {
    if (index + 1 >= total) {
      setSubmitting(true);
      setError("");
      try {
        const payload = questions.map((qq) => ({
          item_id: qq.id,
          selected_option: answers[qq.id] ?? "",
        }));
        await studentApi.submitDiagnostic(courseId, payload, courseName);
        onDone();
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "No se pudo enviar el diagnóstico.");
        setSubmitting(false);
      }
    } else {
      setIndex((i) => i + 1);
    }
  };

  const pick = (opt: string) => setAnswers((a) => ({ ...a, [q.id]: opt }));
  const skip = (val: string) => {
    setAnswers((a) => ({ ...a, [q.id]: val }));
    advance();
  };

  if (phase === "welcome") {
    return (
      <div className="lue-dx">
        <div className="dx-top">
          <button className="dx-close" onClick={onExit} aria-label="Salir">
            ✕
          </button>
          <div className="dx-progress">
            <i style={{ width: "0%" }} />
          </div>
          <span className="dx-count">
            <b>0</b> / {total}
          </span>
        </div>
        <div className="dx-body">
          <div className="dx-center dx-welcome">
            <span className="dx-eyebrow">Examen diagnóstico</span>
            <h1>
              Antes de empezar, <span className="em">midamos tu nivel.</span>
            </h1>
            <p>
              Son {total} preguntas de <b>{courseName}</b>. No afecta tu ELO de práctica: solo nos sirve para ubicarte
              en el punto justo del mapa y de la práctica adaptativa.
            </p>
            <div className="dx-points">
              <div className="dx-point">
                <span className="pi">🎯</span>
                <span>
                  Responde con calma. Si no sabes una, usa <b>"No lo sé"</b> — es honesto y no penaliza.
                </span>
              </div>
              <div className="dx-point">
                <span className="pi">♟</span>
                <span>
                  Con tus respuestas fijamos tu <b>ELO inicial por tema</b>.
                </span>
              </div>
            </div>
            {error && <p style={{ color: "#f87171" }}>{error}</p>}
            <button className="dx-btn" style={{ margin: "0 auto" }} onClick={() => setPhase("quiz")}>
              Comenzar →
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="lue-dx">
      <div className="dx-top">
        <button className="dx-close" onClick={onExit} aria-label="Salir">
          ✕
        </button>
        <div className="dx-progress" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
          <i style={{ width: progress + "%" }} />
        </div>
        <span className="dx-count">
          <b>{index + 1}</b> / {total}
        </span>
      </div>
      <div className="dx-body">
        <div className="dx-center">
          <div className="dx-qmeta">
            {q.topic && <span className="dx-qtopic">{q.topic}</span>}
          </div>
          <div className="dx-qcard">
            <p className="dx-prompt">
              <MathText text={q.content} />
            </p>
            <div className="dx-options">
              {q.options.map((opt, i) => (
                <button
                  key={i}
                  className={"dx-opt" + (selected === opt ? " on" : "")}
                  onClick={() => pick(opt)}
                >
                  <span className="dx-key">{KEYS[i] ?? i + 1}</span>
                  <span>
                    <MathText text={opt} />
                  </span>
                </button>
              ))}
            </div>
          </div>
          {error && <p style={{ color: "#f87171", marginTop: 12 }}>{error}</p>}
          <div className="dx-foot">
            <button className="dx-link" onClick={() => skip("")}>
              ⏭ Saltar
            </button>
            <button className="dx-link" onClick={() => skip("")}>
              🤔 No lo sé
            </button>
            <span className="dx-grow" />
            <button className="dx-btn" onClick={advance} disabled={!selected || submitting}>
              {submitting ? "Enviando…" : index + 1 >= total ? "Ver resultado" : "Siguiente"} →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── bifurcación / resultado ─────────────────────────────────────────────── */
const STATUS_LABEL: Record<string, string> = { strong: "Fuerte", mid: "Medio", gap: "Vacío" };

function CourseHub({
  courseId,
  courseName,
  result,
  onRedo,
}: {
  courseId: string;
  courseName: string;
  result: DiagnosticResult;
  onRedo: () => void;
}) {
  const navigate = useNavigate();
  const startSession = usePracticeStore((s) => s.startSession);
  const league = result.league;

  const practice = () => {
    startSession(courseId);
    navigate("/student");
  };

  return (
    <div className="lue-dx">
      <div className="dx-body" style={{ alignItems: "flex-start", paddingTop: 36 }}>
        <div className="dx-hub">
          <span className="dx-eyebrow">Diagnóstico completado · {courseName}</span>
          <div className="dx-result-head" style={{ marginTop: 12 }}>
            <div className="dx-elo">
              <div className="ev">{Math.round(result.initial_elo).toLocaleString("es-CO")}</div>
              <div className="el">ELO INICIAL</div>
            </div>
            <div className="dx-result-meta">
              <span className="dx-league">
                <span className="ld" style={{ background: league?.color ?? "var(--accent)" }} />
                {league?.name ?? "—"}
                <span style={{ color: "var(--mute)", fontWeight: 500, fontSize: 13 }}>· {league?.rank ?? ""}</span>
              </span>
              <p>
                Acertaste {result.correct_total} de {result.answered} respondidas ({result.score_pct}%). Ya fijamos tu
                punto de partida por tema.
              </p>
            </div>
          </div>

          <div className="dx-themes">
            <h3>Tu mapa de fortalezas</h3>
            {result.themes.map((t) => (
              <div className="dx-theme" key={t.topic}>
                <div className="tl">
                  {t.topic}
                  <span>
                    {t.correct}/{t.total} correctas
                  </span>
                </div>
                <span className={"dx-tag " + t.status}>{STATUS_LABEL[t.status] ?? t.status}</span>
                <span className="te">{Math.round(t.elo)}</span>
              </div>
            ))}
          </div>

          <div className="dx-choices">
            <button className="dx-choice" onClick={practice}>
              <span className="ci">🎯</span>
              <h4>Practicar</h4>
              <p>Sala de práctica adaptativa: el motor ELO te sirve el reto perfecto, una jugada a la vez.</p>
              <span className="cgo">Ir a practicar →</span>
            </button>
            <button className="dx-choice alt" onClick={() => navigate(`/student/course/${courseId}/map`)}>
              <span className="ci">🗺️</span>
              <h4>Mapa de contenido</h4>
              <p>Refuerza conceptos y habilidades nodo a nodo antes de poner en movimiento tu ELO.</p>
              <span className="cgo">Ir al mapa →</span>
            </button>
          </div>

          <button className="dx-redo" onClick={onRedo}>
            ↻ Rehacer diagnóstico
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── root (gating) ───────────────────────────────────────────────────────── */
export function CourseEntry() {
  const { courseId = "" } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [redo, setRedo] = useState(false);

  const { data: courses } = useQuery({ queryKey: ["courses"], queryFn: () => studentApi.courses() });
  const course = useMemo(() => courses?.find((c) => c.id === courseId), [courses, courseId]);
  const courseName = course?.name ?? courseId;
  const isConcours = course?.block === "Concursos";

  const { data, isLoading, isError } = useQuery({
    queryKey: ["diagnostic", courseId, redo],
    queryFn: () => studentApi.diagnostic(courseId, redo),
    enabled: !!courseId && !isConcours,
    // El set de preguntas se genera aleatoriamente en el backend: hay que
    // cargarlo UNA vez y no re-fetchear (si no, cambian las preguntas a media
    // prueba y se reinicia el flujo).
    staleTime: Infinity,
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  });

  const reload = () => {
    setRedo(false);
    qc.invalidateQueries({ queryKey: ["diagnostic", courseId] });
  };

  // Cursos de concursos (DIAN/SENA): sin diagnóstico, navegación por bloques
  if (isConcours) {
    return <ConcoursEntry courseId={courseId} courseName={courseName} />;
  }

  if (isLoading) {
    return (
      <div className="lue-dx">
        <div className="dx-body">
          <div className="dx-center" style={{ textAlign: "center", color: "var(--mute)" }}>
            Cargando materia…
          </div>
        </div>
      </div>
    );
  }
  if (isError || !data) {
    return (
      <div className="lue-dx">
        <div className="dx-body">
          <div className="dx-center" style={{ textAlign: "center", color: "#f87171" }}>
            No se pudo cargar la materia.
          </div>
        </div>
      </div>
    );
  }

  if (data.completed && data.result && !redo) {
    return (
      <CourseHub
        courseId={courseId}
        courseName={courseName}
        result={data.result}
        onRedo={() => {
          setRedo(true);
          qc.invalidateQueries({ queryKey: ["diagnostic", courseId, true] });
        }}
      />
    );
  }

  return (
    <Diagnostic
      courseId={courseId}
      courseName={courseName}
      questions={data.questions ?? []}
      onDone={reload}
      onExit={() => navigate("/student/courses")}
    />
  );
}
