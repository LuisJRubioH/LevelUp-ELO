import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { studentApi, type LessonDetail, type LessonInteractionResult } from "../../../api/student";
import { MathFormula } from "../../../components/Math/MathContent";
import { Button } from "../../../components/ui/Button";
import { KatiaStorySlot } from "./KatiaStorySlot";
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

const HUB_ID = "PREALG-N3-M00-LABORATORIO";

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

export function LevelThreeLesson({ lesson, courseId, onBack, onFinish, finishing }: Props) {
  if (lesson.content?.kind === "property_laboratory_hub") {
    return (
      <LevelThreeHub
        lesson={lesson}
        courseId={courseId}
        onBack={onBack}
        onFinish={onFinish}
        finishing={finishing}
      />
    );
  }
  return (
    <LevelThreeMachine
      lesson={lesson}
      courseId={courseId}
      onBack={onBack}
      onFinish={onFinish}
      finishing={finishing}
    />
  );
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

function LevelThreeMachine({ lesson, courseId, onBack, finishing }: Props) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const content = lesson.content;
  const groups = content?.operation_groups ?? [];
  const restored = lesson.progress.responses;
  // ponytail: un campo solo se bloquea cuando es correcto; los errados quedan editables para reintentar (can_retry)
  const initialDrafts = Object.fromEntries(
    Object.entries(restored).map(([id, response]) => [id, response.selected_option]),
  );
  const initialAnswers = Object.fromEntries(
    Object.entries(restored)
      .filter(([, response]) => response.is_expected)
      .map(([id, response]) => [id, response.selected_option]),
  );
  const initialFeedback = Object.fromEntries(
    Object.entries(restored).map(([id, response]) => [
      id,
      response.is_expected ? content?.feedback?.correct ?? "Correcto." : content?.feedback?.default ?? "Revisa el procedimiento.",
    ]),
  );
  const [drafts, setDrafts] = useState<Record<string, string>>(initialDrafts);
  const [answers, setAnswers] = useState<Record<string, string>>(initialAnswers);
  const [feedback, setFeedback] = useState<Record<string, string>>(initialFeedback);

  const operationsById = useMemo(() => {
    return Object.fromEntries(groups.flatMap((group) => group.ops.map((op) => [`${lesson.node_id}-${op.id}`, op])));
  }, [groups, lesson.node_id]);

  const mutation = useMutation({
    mutationFn: ({ id, option }: { id: string; option: string }) =>
      studentApi.lessonInteraction(courseId, lesson.node_id, id, option),
    onSuccess: (result: LessonInteractionResult) => {
      if (result.is_expected) {
        setAnswers((current) => ({ ...current, [result.interaction_id]: result.selected_option }));
        setFeedback((current) => ({ ...current, [result.interaction_id]: content?.feedback?.correct ?? "Correcto." }));
      } else {
        setFeedback((current) => ({
          ...current,
          [result.interaction_id]:
            content?.feedback?.default ?? `Resultado esperado: ${operationsById[result.interaction_id]?.answer ?? ""}`,
        }));
      }
    },
    onError: (_error, variables) => {
      setFeedback((current) => ({
        ...current,
        [variables.id]: "Revisa el formato: usa coma decimal (2,5) y, si es inverso, una fracción como 1/5.",
      }));
    },
  });

  const returnMutation = useMutation({
    mutationFn: () => studentApi.lessonEvent(courseId, lesson.node_id, "node_completed"),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["lesson", courseId, lesson.node_id] });
      await queryClient.invalidateQueries({ queryKey: ["lesson", courseId, HUB_ID] });
      await queryClient.invalidateQueries({ queryKey: ["course-map", courseId] });
      navigate(`/student/course/${courseId}/lesson/${HUB_ID}`);
    },
  });

  const allAnswered = lesson.interactions.every((interaction) => answers[interaction.interaction_id]);
  const formalization = content?.formalization;
  const formalizationItems = Array.isArray(formalization) ? formalization : [];
  const formalizationBox = formalization && !Array.isArray(formalization) ? formalization : null;
  const isUnified = content?.story_contract?.type === "unified_set_extension";

  return (
    <article className="lesson-page n3-page n3-machine" aria-labelledby="lesson-title">
      <header className="lesson-topbar">
        <button className="lesson-back" onClick={onBack}>Volver al mapa</button>
        <span className="lesson-safe">Zona segura · no afecta ELO</span>
      </header>

      <div className="lesson-shell n3-shell">
        <header className="n3-hero machine">
          <div>
            <span className="lesson-kicker">Nivel 3 · Propiedades</span>
            <h1 id="lesson-title">{content?.title}</h1>
            <p>{content?.intro}</p>
          </div>
          {!isUnified && (
            <aside className="n3-katia-card">
              <img src="/katia/katIA.png" alt="" aria-hidden="true" />
              <b>KatIA</b>
              <p>{content?.opening_hook?.katia_message}</p>
              <div className="n3-machine-demo">
                <MixedMath value={content?.opening_hook?.demo ?? ""} />
              </div>
            </aside>
          )}
        </header>

        {isUnified ? (
          <>
            {content?.katia && (
              <KatiaStorySlot
                eyebrow={content.katia.eyebrow}
                title={content.katia.title}
                body={content.katia.body}
                question={content.katia.question}
                imageSrc={content.katia.imageSrc}
              />
            )}

            <section className="set-story" aria-label="Descubrimiento y definicion">
              {content?.discovery && (
                <article>
                  <span>{content.discovery.eyebrow}</span>
                  <h2>{content.discovery.title}</h2>
                  <p>{content.discovery.body}</p>
                </article>
              )}
              <article className="set-formal">
                <span>Definicion formal</span>
                <h2>{content?.definition_title ?? "Definicion"}</h2>
                {content?.definition_katex && <MathFormula math={content.definition_katex} />}
                <p>{content?.definition}</p>
              </article>
            </section>

            <section className="set-base-examples n2-examples-2col" aria-label="Ejemplos resueltos">
              {content?.worked_examples?.filter((example) => !example.trap).map((example, index) => (
                <article key={index}>
                  <span>{example.eyebrow}</span>
                  <h3>{example.title ?? example.statement}</h3>
                  {example.image_slot && (
                    <div className="n2-image-slot" role="img" aria-label="Espacio para imagen del ejemplo">
                      {example.image ? (
                        <img src={example.image} alt="" loading="lazy" />
                      ) : (
                        <span>Imagen aqui</span>
                      )}
                    </div>
                  )}
                  <p>{example.statement}</p>
                  {example.latex && (
                    <div className="n2-example-latex"><MathFormula math={example.latex} /></div>
                  )}
                  {example.steps && (
                    <ol>{example.steps.map((step) => <li key={step}>{step}</li>)}</ol>
                  )}
                </article>
              ))}
            </section>

            {content?.worked_examples?.filter((example) => example.trap).map((example, index) => (
              <section className="set-base-examples n2-example-wide" key={index} aria-label="Trampa comun">
                <article className="n2-example-trap">
                  <span>{example.eyebrow}</span>
                  <h3>{example.title ?? example.statement}</h3>
                  <p>{example.statement}</p>
                  {example.latex && (
                    <div className="n2-example-latex"><MathFormula math={example.latex} /></div>
                  )}
                  {example.steps && (
                    <ol>{example.steps.map((step) => <li key={step}>{step}</li>)}</ol>
                  )}
                </article>
              </section>
            ))}

            {content?.closure && (
              <section className="n2-closure" aria-label={content.closure.title}>
                <div className="n2-closure-head">
                  <span>{content.closure.eyebrow ?? "Validez a lo largo de las operaciones"}</span>
                  <h2>{content.closure.title}</h2>
                  <p>{content.closure.intro}</p>
                </div>
                <ul className="n2-closure-ladder">
                  {content.closure.rows.map((row) => (
                    <li key={row.name} className={`n2-closure-row ${row.closed}`}>
                      <span className="n2-closure-set">
                        <MathFormula math={row.symbol} /> {row.name}
                      </span>
                      <span className={`n2-closure-badge ${row.closed}`}>
                        {row.closed === "yes" ? "Sí guarda" : row.closed === "no" ? "No guarda" : "Parcial"}
                      </span>
                      {row.latex && (
                        <span className="n2-closure-latex"><MathFormula math={row.latex} /></span>
                      )}
                      <span className="n2-closure-note">{row.note}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </>
        ) : (
          <section className="n3-definition">
            <div>
              <span>Descubrimiento guiado</span>
              <p>{content?.definition}</p>
              {content?.formal_expression && (
                <div className="n3-formula">
                  <MixedMath value={content.formal_expression} />
                </div>
              )}
            </div>
            <div className="n3-examples">
              {content?.worked_examples?.map((example) => (
                <article key={example.statement}>
                  <b>{example.statement}</b>
                  <MixedMath value={example.solution} />
                </article>
              ))}
            </div>
          </section>
        )}

        <section className="n3-operations" aria-label={content?.instruction}>
          <header>
            <span>Interfaz de máquina</span>
            <h2>{content?.instruction}</h2>
          </header>
          {groups.map((group) => {
            const groupAnswered = group.ops.every((op) => answers[`${lesson.node_id}-${op.id}`]);
            return (
              <article className={`n3-op-group ${groupAnswered ? "complete" : ""}`} key={group.id}>
                <div className="n3-op-grid">
                  {group.ops.map((op) => {
                    const interactionId = `${lesson.node_id}-${op.id}`;
                    const answered = Boolean(answers[interactionId]);
                    return (
                      <div className="n3-operation" key={op.id}>
                        <span>{op.id}</span>
                        <div className="n3-expression">
                          <MathFormula math={mathFromText(op.expr)} />
                        </div>
                        <div className="numeric-answer">
                          <input
                            value={drafts[interactionId] ?? ""}
                            disabled={answered}
                            inputMode={content?.property === "inverses" ? "text" : "decimal"}
                            aria-label={`Respuesta ${op.id}`}
                            onChange={(event) =>
                              setDrafts((current) => ({ ...current, [interactionId]: event.target.value }))
                            }
                          />
                          <Button
                            variant="secondary"
                            disabled={answered || !drafts[interactionId]}
                            loading={mutation.isPending}
                            onClick={() => mutation.mutate({ id: interactionId, option: drafts[interactionId] })}
                          >
                            Validar
                          </Button>
                        </div>
                        {feedback[interactionId] && (
                          <p className="trigger-feedback" role="status">{feedback[interactionId]}</p>
                        )}
                      </div>
                    );
                  })}
                </div>
                {groupAnswered && <p className="n3-katia-line">{group.katia_after}</p>}
              </article>
            );
          })}
        </section>

        <section className="n3-formalization">
          <span>Formalización</span>
          <ul>
            {formalizationBox && <li key="formalization-intro">{formalizationBox.title}: {formalizationBox.intro}</li>}
            {formalizationItems.map((item) => <li key={item}>{item}</li>)}
            {formalizationBox?.items.map((item) => (
              <li key={item.label}>
                <b>{item.label}</b> {item.rule}
                {item.latex && <MathFormula math={item.latex} />}
              </li>
            ))}
          </ul>
          <p>{content?.closing}</p>
        </section>

        <footer className="lesson-footer trigger-footer">
          <div>
            <span>Regreso al laboratorio</span>
            <p>Completa todas las operaciones para registrar esta máquina como descubierta.</p>
          </div>
          <Button
            size="lg"
            disabled={!allAnswered}
            loading={finishing || returnMutation.isPending}
            onClick={() => returnMutation.mutate()}
          >
            Volver al laboratorio
          </Button>
        </footer>
      </div>
    </article>
  );
}
