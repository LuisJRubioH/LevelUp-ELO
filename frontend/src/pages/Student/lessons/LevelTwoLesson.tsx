import { useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { studentApi, type LessonDetail, type LessonInteractionResult } from "../../../api/student";
import { MathFormula } from "../../../components/Math/MathContent";
import { Button } from "../../../components/ui/Button";
import { KatiaStorySlot } from "./KatiaStorySlot";
import { PracticeItem, restoredAnswers, type AnswerMap, type FeedbackMap } from "./PracticeItem";
import "./LevelTwoLesson.css";
import { HubDestinationArt } from "./HubDestinationArt";

type Props = {
  lesson: LessonDetail;
  courseId: string;
  onBack: () => void;
  onFinish: () => Promise<void>;
  finishing: boolean;
};

function mathFromText(value: string): string {
  return value
    .replaceAll(" x ", String.raw`\times `)
    .replaceAll(" × ", String.raw`\times `)
    .replaceAll("÷", String.raw`\div`)
    .replaceAll("√20", String.raw`\sqrt{20}`)
    .replaceAll("√16", String.raw`\sqrt{16}`)
    .replaceAll("√9", String.raw`\sqrt{9}`)
    .replaceAll("∛27", String.raw`\sqrt[3]{27}`)
    .replaceAll("^", "^");
}

export function LevelTwoLesson({ lesson, courseId, onBack, onFinish, finishing }: Props) {
  if (lesson.content?.kind === "operation_city_hub") {
    return (
      <LevelTwoHub
        lesson={lesson}
        courseId={courseId}
        onBack={onBack}
        onFinish={onFinish}
        finishing={finishing}
      />
    );
  }
  return (
    <LevelTwoOperation
      lesson={lesson}
      courseId={courseId}
      onBack={onBack}
      onFinish={onFinish}
      finishing={finishing}
    />
  );
}

function LevelTwoHub({ lesson, courseId, onBack, onFinish, finishing }: Props) {
  const navigate = useNavigate();
  const content = lesson.content;
  const buildings = content?.buildings ?? [];
  const icebreakerItems = content?.icebreaker?.items ?? [];
  const restored = lesson.progress.responses;
  const [opened, setOpened] = useState<Set<string>>(
    new Set(Object.keys(restored).map((id) => id.replace(`${lesson.node_id}-CARD-`, "")).filter((id) => restored[`${lesson.node_id}-CARD-${id}`])),
  );
  const [answers, setAnswers] = useState<AnswerMap>(restoredAnswers(lesson.progress.responses));
  const [feedback, setFeedback] = useState<FeedbackMap>({});

  const mutation = useMutation({
    mutationFn: (buildingId: string) =>
      studentApi.lessonInteraction(courseId, lesson.node_id, `${lesson.node_id}-CARD-${buildingId}`, "opened"),
    onSuccess: (result: LessonInteractionResult) => {
      setOpened((current) => new Set(current).add(result.interaction_id.replace(`${lesson.node_id}-CARD-`, "")));
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

  const allOpened = opened.size >= buildings.length;

  return (
    <article className="lesson-page n2-page n2-hub" aria-labelledby="lesson-title">
      <header className="lesson-topbar">
        <button className="lesson-back" onClick={onBack}>Volver al mapa</button>
        <span className="lesson-safe">Zona segura · no afecta ELO</span>
      </header>

      <div className="lesson-shell n2-shell">
        <header className="level-presentation-header">
          <span className="lesson-kicker">{content?.level}</span>
          <h1 id="lesson-title">{content?.title}</h1>
          <p>{content?.welcome_text}</p>
        </header>

        <div className="level-presentation-media" role="img" aria-label="Imagen de KatIA aquí">
          <img src="/leccion/02-prealg-n2-mercado/e00-hub-mercado-v4.png" alt="" loading="lazy" />
        </div>

        {content?.scene_text && <p className="n2-scene-text">{content.scene_text}</p>}

        {icebreakerItems.length > 0 && (
          <section className="n2-icebreaker" aria-label={content?.icebreaker?.title}>
            <header>
              <h2 className="n2-icebreaker-title">{content?.icebreaker?.title}</h2>
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
          Abre los 6 edificios para desbloquear las operaciones · {opened.size}/{buildings.length} abiertos
        </p>

        <section className="n2-city" aria-label="Ciudad de operaciones basicas">
          {buildings.map((building, index) => {
            const isOpened = opened.has(building.id);
            return (
              <article className={`n2-building ${isOpened ? "opened" : ""}`} key={building.id}>
                <button
                  className="n2-building-tower"
                  onClick={() => {
                    if (!isOpened) mutation.mutate(building.id);
                  }}
                  aria-pressed={isOpened}
                  aria-label={`Explorar ${building.operation}`}
                  disabled={mutation.isPending}
                >
                  <HubDestinationArt id={building.id}>
                    <span>{building.symbol}</span>
                    <b>{String(index + 1).padStart(2, "0")}</b>
                  </HubDestinationArt>
                </button>
                <div className={`n2-card ${isOpened ? "revealed" : ""}`}>
                  <h2>{building.operation}</h2>
                  {isOpened ? (
                    <p>{building.card}</p>
                  ) : (
                    <p className="n2-card-closed">Haz click en el edificio para abrir su cartel.</p>
                  )}
                  {allOpened && (
                    <button
                      type="button"
                      onClick={() => navigate(`/student/course/${courseId}/lesson/${building.node_id}`)}
                    >
                      Entrar
                    </button>
                  )}
                </div>
              </article>
            );
          })}
        </section>

        {allOpened && <p className="n2-katia">{content?.advance_text}</p>}

        <footer className="lesson-footer trigger-footer">
          <div>
            <span>Gating de exploracion</span>
            <p>Abre los seis carteles para habilitar los edificios del Nivel 2.</p>
          </div>
          <Button size="lg" disabled={!allOpened} loading={finishing} onClick={onFinish}>
            Completar ciudad
          </Button>
        </footer>
      </div>
    </article>
  );
}

function LevelTwoOperation({ lesson, courseId, onBack, finishing }: Props) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const content = lesson.content;
  const situations = content?.situations ?? [];
  const restored = lesson.progress.responses;
  const initialAnswers = Object.fromEntries(
    Object.entries(restored).map(([id, response]) => [id, response.selected_option]),
  );
  const initialFeedback = Object.fromEntries(
    Object.entries(restored).map(([id, response]) => [
      id,
      response.is_expected ? content?.feedback?.correct ?? "Correcto." : content?.feedback?.default ?? "Revisa el procedimiento.",
    ]),
  );
  const [drafts, setDrafts] = useState<Record<string, string>>(initialAnswers);
  const [answers, setAnswers] = useState<Record<string, string>>(initialAnswers);
  const [feedback, setFeedback] = useState<Record<string, string>>(initialFeedback);

  const bySituationId = useMemo(
    () => Object.fromEntries(situations.map((situation) => [situation.id, situation])),
    [situations],
  );

  const mutation = useMutation({
    mutationFn: ({ id, option }: { id: string; option: string }) =>
      studentApi.lessonInteraction(courseId, lesson.node_id, id, option),
    onSuccess: (result: LessonInteractionResult) => {
      const situationKey = result.interaction_id.split("-").at(-1) ?? "";
      const situation = bySituationId[situationKey];
      setAnswers((current) => ({ ...current, [result.interaction_id]: result.selected_option }));
      setFeedback((current) => ({
        ...current,
        [result.interaction_id]: result.is_expected
          ? content?.feedback?.correct ?? "Correcto."
          : content?.feedback?.default ?? `Resultado esperado: ${situation?.answer ?? ""}`,
      }));
    },
  });

  const returnMutation = useMutation({
    mutationFn: () => studentApi.lessonEvent(courseId, lesson.node_id, "node_completed"),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["lesson", courseId, lesson.node_id] });
      await queryClient.invalidateQueries({ queryKey: ["lesson", courseId, "PREALG-N2-E00-CIUDAD"] });
      await queryClient.invalidateQueries({ queryKey: ["course-map", courseId] });
      navigate(`/student/course/${courseId}/lesson/PREALG-N2-E00-CIUDAD`);
    },
  });

  const allAnswered = lesson.interactions.every((interaction) => answers[interaction.interaction_id]);
  const formalization = content?.formalization;
  const formalizationItems = Array.isArray(formalization) ? formalization : [];
  const formalizationBox = formalization && !Array.isArray(formalization) ? formalization : null;
  const hasIntegratedStory = content?.story_contract?.type === "narrative_with_integrated_definition";
  const isUnified = content?.story_contract?.type === "unified_set_extension";

  return (
    <article className="lesson-page n2-page n2-operation" aria-labelledby="lesson-title">
      <header className="lesson-topbar">
        <button className="lesson-back" onClick={onBack}>Volver al mapa</button>
        <span className="lesson-safe">Zona segura · no afecta ELO</span>
      </header>

      <div className="lesson-shell n2-shell">
        <header className="n2-hero operation">
          <span className="lesson-kicker">Nivel 2 · Operaciones basicas</span>
          <h1 id="lesson-title">{content?.title}</h1>
          <p>{content?.intro}</p>
          <small>Contenido NEW pendiente de validacion pedagogica</small>
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
                  <span>Extension a los conjuntos numericos</span>
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
                        {row.closed === "yes" ? "Cierra" : row.closed === "no" ? "No cierra" : "Parcial"}
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
          <>
            {hasIntegratedStory && (
              <section className="n2-story-flow" aria-label="Narrativa y descubrimiento guiado">
                {content?.narrative_sections?.map((section) => (
                  <article key={section.title} className={`n2-story-card ${section.type}`}>
                    <span>{section.type === "guided_discovery" ? "Descubrimiento guiado" : "Apertura narrativa"}</span>
                    <h2>{section.title}</h2>
                    <p>{section.body}</p>
                  </article>
                ))}
              </section>
            )}

            {content?.operation === "addition" && (
              <section className="n2-basket-demo" aria-label="Canasta visual de suma">
                <div className="fruit-basket" aria-hidden="true">
                  <div className="fruit-row first">
                    {["manzana", "manzana", "manzana"].map((fruit, index) => <span key={`${fruit}-${index}`}>●</span>)}
                  </div>
                  <b>+</b>
                  <div className="fruit-row second">
                    {["manzana-verde", "manzana-verde"].map((fruit, index) => <span key={`${fruit}-${index}`}>●</span>)}
                  </div>
                  <strong>5</strong>
                </div>
                <div>
                  <span>Antes de practicar</span>
                  <h2>Las partes forman un total</h2>
                  <p>La canasta muestra la idea central: 3 frutas y 2 frutas se juntan sin que ninguna desaparezca.</p>
                </div>
              </section>
            )}

            <section className={`n2-definition ${hasIntegratedStory ? "integrated" : ""}`}>
              <div>
                <span>{hasIntegratedStory ? "Definicion integrada" : "Definicion"}</span>
                <p>{content?.definition}</p>
                {content?.definition_katex && (
                  <div className="n2-definition-formula">
                    <MathFormula math={mathFromText(content.definition_katex)} />
                  </div>
                )}
              </div>
              <div className="n2-examples">
                {content?.worked_examples?.map((example) => (
                  <article key={example.statement}>
                    <b>{example.statement}</b>
                    <MathFormula math={mathFromText(example.solution)} />
                    {example.steps && (
                      <ol>
                        {example.steps.map((step) => <li key={step}>{step}</li>)}
                      </ol>
                    )}
                  </article>
                ))}
              </div>
            </section>
          </>
        )}

        <section className="n2-situations" aria-label="Practica interactiva del edificio">
          {situations.map((situation) => {
            const interactionId = `${lesson.node_id}-${situation.id}`;
            const answered = Boolean(answers[interactionId]);
            return (
              <article className="n2-situation" key={situation.id}>
                <span>{situation.set_label ?? situation.id}</span>
                <h2>{situation.prompt}</h2>
                <div className="n2-expression">
                  <MathFormula math={isUnified ? situation.expr : mathFromText(situation.expr)} />
                </div>
                <div className="numeric-answer">
                  <input
                    value={drafts[interactionId] ?? ""}
                    disabled={answered}
                    inputMode="decimal"
                    aria-label={`Respuesta ${situation.id}`}
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
              </article>
            );
          })}
        </section>

        <section className="n2-formalization">
          <span>Formalizacion</span>
          {formalizationBox && (
            <p>{formalizationBox.title}: {formalizationBox.intro}</p>
          )}
          <ul>
            {formalizationItems.map((item) => <li key={item}>{item}</li>)}
            {formalizationBox?.items.map((item) => (
              <li key={item.label}>
                <b>{item.label}</b> {item.rule}
                {item.latex && <MathFormula math={item.latex} />}
              </li>
            ))}
          </ul>
        </section>

        <footer className="lesson-footer trigger-footer">
          <div>
            <span>{content?.character ?? "KatIA"}</span>
            <p>Completa las situaciones para volver a la ciudad con este edificio registrado.</p>
          </div>
          <Button
            size="lg"
            disabled={!allAnswered}
            loading={finishing || returnMutation.isPending}
            onClick={() => returnMutation.mutate()}
          >
            Volver a la ciudad
          </Button>
        </footer>
      </div>
    </article>
  );
}
