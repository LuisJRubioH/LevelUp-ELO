import { useState } from "react";
import { motion } from "framer-motion";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { studentApi, type LessonDetail, type LessonInteractionResult } from "../../../api/student";
import { MathFormula } from "../../../components/Math/MathContent";
import { Button } from "../../../components/ui/Button";
import { PracticeItem, restoredAnswers, type AnswerMap, type FeedbackMap } from "./PracticeItem";
import "./LevelThreeLesson.css";
import { HubDestinationArt } from "./HubDestinationArt";
// ponytail: reutiliza las clases .set-* y .n2-closure/.n2-examples del Nivel 2 (CSS global) en vez de duplicarlas
import "./LevelTwoLesson.css";

type Props = {
  lesson: LessonDetail;
  courseId: string;
  onBack: () => void;
  onFinish: () => Promise<void>;
  finishing: boolean;
};

function mathFromText(value: string): string {
  return value
    .replaceAll("___", String.raw`\square`)
    .replaceAll("...", String.raw`\ldots`)
    .replaceAll("…", String.raw`\ldots`)
    .replaceAll("×", String.raw`\times`)
    .replaceAll("÷", String.raw`\div`)
    .replaceAll("−", "-")
    .replaceAll("⊕", String.raw`\oplus`)
    .replace(/√(\d+)/g, String.raw`\sqrt{$1}`)
    .replace(/(?<!\d)(\d+)\/(\d+)/g, String.raw`\frac{$1}{$2}`);
}

function mixedMathParts(value: string): Array<{ kind: "math" | "text"; value: string }> {
  return value
    .replace(/;\s*luego\s*/gi, "||luego||")
    .replace(/\s+y\s+/gi, "||y||")
    .replace(/\s+pero\s+/gi, "||pero||")
    .replace(/\s+entonces\s+/gi, "||entonces||")
    .replace(/;\s*/g, "||;||")
    .split("||")
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => ({
      kind: /^(luego|y|pero|entonces|;)$/i.test(part) ? "text" : "math",
      value: part === ";" ? "luego" : part,
    }));
}

function MixedMath({ value }: { value: string }) {
  return (
    <div className="n3-mixed-math">
      {mixedMathParts(value).map((part, index) =>
        part.kind === "math" ? (
          <MathFormula key={`${part.value}-${index}`} math={mathFromText(part.value)} />
        ) : (
          <span className="n3-math-connector" key={`${part.value}-${index}`}>
            {part.value}
          </span>
        ),
      )}
    </div>
  );
}

// Spec 003 N5: N3's machines are eleven-block nodes (`ElevenBlockLesson`); this file renders
// only the laboratory hub.
export function LevelThreeLesson(props: Props) {
  return <LevelThreeHub {...props} />;
}

function LevelThreeHub({ lesson, courseId, onBack, onFinish, finishing }: Props) {
  const navigate = useNavigate();
  const content = lesson.content;
  const machines = content?.machines ?? [];
  const icebreakerItems = content?.icebreaker?.items ?? [];
  const restored = lesson.progress.responses;
  const [introduced, setIntroduced] = useState<Set<string>>(
    new Set(Object.keys(restored).map((id) => id.replace(`${lesson.node_id}-MACHINE-`, "")).filter((id) => restored[`${lesson.node_id}-MACHINE-${id}`])),
  );
  const [answers, setAnswers] = useState<AnswerMap>(restoredAnswers(lesson.progress.responses));
  const [feedback, setFeedback] = useState<FeedbackMap>({});

  const mutation = useMutation({
    mutationFn: (machineId: string) =>
      studentApi.lessonInteraction(
        courseId,
        lesson.node_id,
        `${lesson.node_id}-MACHINE-${machineId}`,
        "introduced",
      ),
    onSuccess: (result: LessonInteractionResult) => {
      setIntroduced((current) =>
        new Set(current).add(result.interaction_id.replace(`${lesson.node_id}-MACHINE-`, "")),
      );
    },
  });

  const answerMutation = useMutation({
    mutationFn: ({ id, option }: { id: string; option: string }) =>
      studentApi.lessonInteraction(courseId, lesson.node_id, id, option),
    onSuccess: (result: LessonInteractionResult) => {
      if (result.is_expected) {
        setAnswers((current) => ({ ...current, [result.interaction_id]: result.selected_option }));
      }
      setFeedback((current) => ({
        ...current,
        [result.interaction_id]:
          content?.feedback?.[result.feedback_key] ?? (result.is_expected ? "Correcto." : "Revisa tu respuesta."),
      }));
    },
  });

  const allIntroduced = introduced.size >= machines.length;

  return (
    <article className="lesson-page n3-page n3-hub" aria-labelledby="lesson-title">
      <header className="lesson-topbar">
        <button className="lesson-back" onClick={onBack}>Volver al mapa</button>
        <span className="lesson-safe">Zona segura · no afecta ELO</span>
      </header>

      <div className="lesson-shell n3-shell">
        <header className="level-presentation-header">
          <span className="lesson-kicker">{content?.level}</span>
          <h1 id="lesson-title">{content?.title}</h1>
          <p>{content?.welcome_text}</p>
        </header>

        <div className="level-presentation-media">
          <img src="/leccion/03-prealg-n3-fabrica/m00-hub-fabrica-v5.png" alt="" aria-hidden="true" loading="lazy" />
        </div>

        {content?.scene_text && <p className="n3-scene-text">{content.scene_text}</p>}

        {icebreakerItems.length > 0 && (
          <section className="n3-icebreaker" aria-label={content?.icebreaker?.title}>
            <header>
              <h2 className="n3-icebreaker-title">{content?.icebreaker?.title}</h2>
              <p>{content?.icebreaker?.intro}</p>
            </header>
            {icebreakerItems.map((item) => (
              <PracticeItem
                key={item.id}
                item={item}
                lessonNodeId={lesson.node_id}
                answers={answers}
                feedback={feedback}
                mutation={answerMutation}
              />
            ))}
          </section>
        )}

        <p className="level-gating-hint">
          Calibra las 5 máquinas para desbloquear las propiedades · {introduced.size}/{machines.length} calibradas
        </p>

        <section className="n3-lab" aria-label="Laboratorio de propiedades misteriosas">
          {machines.map((machine, index) => {
            const isIntroduced = introduced.has(machine.id);
            const canEnter = allIntroduced && machine.state !== "blocked";
            return (
              <motion.article
                className={`n3-machine-card ${isIntroduced ? "introduced" : ""} ${machine.state ?? ""}`}
                key={machine.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.04, duration: 0.18 }}
              >
                <button
                  type="button"
                  className="n3-machine-face"
                  disabled={mutation.isPending}
                  aria-pressed={isIntroduced}
                  aria-label={`Explorar ${machine.station ?? machine.property}`}
                  onClick={() => {
                    if (!isIntroduced) mutation.mutate(machine.id);
                  }}
                >
                  <HubDestinationArt id={machine.id}>
                    <span>{machine.symbol}</span>
                    <b>{machine.id}</b>
                  </HubDestinationArt>
                </button>
                <div className="n3-machine-copy">
                  <span>{machine.station ?? machine.property}</span>
                  <div className="n3-machine-demo">
                    <MixedMath value={machine.demo} />
                  </div>
                  <p>{isIntroduced ? machine.katia_message : content?.drag_rule}</p>
                  {allIntroduced && (
                    <button
                      type="button"
                      disabled={!canEnter}
                      onClick={() => navigate(`/student/course/${courseId}/lesson/${machine.node_id}`)}
                    >
                      {machine.state === "completed" ? "Revisar" : machine.state === "blocked" ? "Bloqueada" : "Entrar"}
                    </button>
                  )}
                </div>
              </motion.article>
            );
          })}
        </section>

        {allIntroduced && <p className="n3-katia-final">{content?.advance_text}</p>}

        <footer className="lesson-footer trigger-footer">
          <div>
            <span>Activación del laboratorio</span>
            <p>Calibra las cinco máquinas para desbloquear la ruta de propiedades.</p>
          </div>
          <Button size="lg" disabled={!allIntroduced} loading={finishing} onClick={onFinish}>
            Activar laboratorio
          </Button>
        </footer>
      </div>
    </article>
  );
}
