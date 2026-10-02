import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import {
  studentApi,
  type LessonDetail,
  type LessonInteractionResult,
} from "../../../api/student";
import { MathFormula } from "../../../components/Math/MathContent";
import { Button } from "../../../components/ui/Button";
import { KatiaStorySlot } from "./KatiaStorySlot";
import { PracticeItem, restoredAnswers, type AnswerMap, type FeedbackMap } from "./PracticeItem";
import "./LevelFourLesson.css";
import { HubDestinationArt } from "./HubDestinationArt";
// ponytail: reutiliza .set-*/.n2-*/.trigger-feedback del Nivel 2 (CSS global) en vez de duplicarlas
import "./LevelTwoLesson.css";

type Props = {
  lesson: LessonDetail;
  courseId: string;
  onBack: () => void;
  onFinish: () => Promise<void>;
  finishing: boolean;
};

const HUB_ID = "PREALG-N4-C00-PUERTO-DE-LA-POLIS";

export function LevelFourLesson({ lesson, courseId, onBack, onFinish, finishing }: Props) {
  if (lesson.content?.kind === "level_hub_port" || lesson.content?.kind === "level_hub_cards") {
    return (
      <LevelFourHub lesson={lesson} courseId={courseId} onBack={onBack} onFinish={onFinish} finishing={finishing} />
    );
  }
  return <LevelFourConcept lesson={lesson} courseId={courseId} onBack={onBack} finishing={finishing} />;
}

function LevelFourHub({ lesson, courseId, onBack, onFinish, finishing }: Props) {
  const navigate = useNavigate();
  const content = lesson.content;
  const cards = content?.cards ?? [];
  const icebreakerItems = content?.icebreaker?.items ?? [];
  const restored = lesson.progress.responses;
  const [opened, setOpened] = useState<Set<string>>(
    new Set(Object.keys(restored).map((id) => id.replace(`${lesson.node_id}-CARD-`, "")).filter((id) => restored[`${lesson.node_id}-CARD-${id}`])),
  );
  const [answers, setAnswers] = useState<AnswerMap>(restoredAnswers(lesson.progress.responses));
  const [feedback, setFeedback] = useState<FeedbackMap>({});

  const cardMutation = useMutation({
    mutationFn: (cardId: string) =>
      studentApi.lessonInteraction(courseId, lesson.node_id, `${lesson.node_id}-CARD-${cardId}`, "opened"),
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

  const allOpened = opened.size >= cards.length;

  return (
    <article className="lesson-page n4-page n4-hub" aria-labelledby="lesson-title">
      <header className="lesson-topbar">
        <button className="lesson-back" onClick={onBack}>Volver al mapa</button>
        <span className="lesson-safe">Zona segura · no afecta ELO</span>
      </header>

      <div className="lesson-shell n4-shell">
        <header className="level-presentation-header">
          <span className="lesson-kicker">{content?.level ?? "Nivel 4"}</span>
          <h1>{content?.title ?? "El Puerto de la Polis"}</h1>
          <p>{content?.welcome_text ?? ""}</p>
        </header>

        <div className="level-presentation-media" role="img" aria-label="Imagen de KatIA aquí">
          <img
            src={content?.image ?? "/leccion/04-prealg-n4-puerto/c00-hub-puerto-v4.png"}
            alt=""
            loading="lazy"
          />
        </div>

        {content?.scene_text && <p className="n4-scene-text">{content.scene_text}</p>}

        {icebreakerItems.length > 0 && (
          <section className="n4-icebreaker" aria-label={content?.icebreaker?.title}>
            <header>
              <h2 className="n4-icebreaker-title">{content?.icebreaker?.title}</h2>
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
          {content?.cards_hint ?? `Abre los ${cards.length} muelles para habilitar la ruta de divisibilidad`} · {opened.size}/{cards.length} abiertos
        </p>

        <section className="n4-port" aria-label={content?.cards_aria ?? "Muelles del puerto"}>
          {cards.map((card, index) => {
            const isOpened = opened.has(card.id);
            return (
              <article className={`n4-card ${isOpened ? "opened" : ""}`} key={card.id}>
                <button
                  className="n4-card-face"
                  onClick={() => {
                    if (!isOpened) cardMutation.mutate(card.id);
                  }}
                  aria-pressed={isOpened}
                  aria-label={`Explorar ${card.destination}`}
                  disabled={cardMutation.isPending}
                >
                  <HubDestinationArt id={card.id}>
                    <MathFormula math={card.symbol} />
                    <b>{String(index + 1).padStart(2, "0")}</b>
                  </HubDestinationArt>
                </button>
                <div className={`n4-card-copy ${isOpened ? "revealed" : ""}`}>
                  <span>{card.destination}</span>
                  {isOpened ? <p>{card.teaser}</p> : <p className="n4-card-closed">{content?.card_closed_hint ?? "Haz click en el muelle para ver su ruta."}</p>}
                  {allOpened && (
                    <button
                      type="button"
                      onClick={() => navigate(`/student/course/${courseId}/lesson/${card.node_id}`)}
                    >
                      {content?.card_cta ?? "Zarpar"}
                    </button>
                  )}
                </div>
              </article>
            );
          })}
        </section>

        {allOpened && <p className="n4-katia-final">{content?.advance_text}</p>}

        <footer className="lesson-footer trigger-footer">
          <div>
            <span>{content?.gating_label ?? "Gating del puerto"}</span>
            <p>{content?.cards_hint ?? "Abre los seis muelles para habilitar la ruta de divisibilidad."}</p>
          </div>
          <Button size="lg" disabled={!allOpened} loading={finishing} onClick={onFinish}>
            {content?.finish_label ?? "Entrar al puerto"}
          </Button>
        </footer>
      </div>
    </article>
  );
}

function LevelFourConcept({ lesson, courseId, onBack, finishing }: Omit<Props, "onFinish">) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const content = lesson.content;
  const practiceItems = content?.practice ?? [];
  const [answers, setAnswers] = useState<AnswerMap>(restoredAnswers(lesson.progress.responses));
  const [feedback, setFeedback] = useState<FeedbackMap>({});

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
  const isFormalizationBox = formalization && !Array.isArray(formalization);

  return (
    <article className="lesson-page n4-page n4-concept" aria-labelledby="lesson-title">
      <header className="lesson-topbar">
        <button className="lesson-back" onClick={onBack}>Volver al mapa</button>
        <span className="lesson-safe">Zona segura · no afecta ELO</span>
      </header>

      <div className="lesson-shell n4-shell">
        <header className="n4-hero">
          <span className="lesson-kicker">Nivel 4 · Divisibilidad</span>
          <h1 id="lesson-title">{content?.title}</h1>
        </header>

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
            <span>Definición formal</span>
            <h2>{content?.definition_title ?? "Definición"}</h2>
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
                    <span>Imagen aquí</span>
                  )}
                </div>
              )}
              <p>{example.statement}</p>
              {example.latex && (
                <div className="n2-example-latex"><MathFormula math={example.latex} /></div>
              )}
              {example.steps && <ol>{example.steps.map((step) => <li key={step}>{step}</li>)}</ol>}
            </article>
          ))}
        </section>

        {content?.worked_examples?.filter((example) => example.trap).map((example, index) => (
          <section className="set-base-examples n2-example-wide" key={index} aria-label="Trampa común">
            <article className="n2-example-trap">
              <span>{example.eyebrow}</span>
              <h3>{example.title ?? example.statement}</h3>
              <p>{example.statement}</p>
              {example.latex && (
                <div className="n2-example-latex"><MathFormula math={example.latex} /></div>
              )}
              {example.steps && <ol>{example.steps.map((step) => <li key={step}>{step}</li>)}</ol>}
            </article>
          </section>
        ))}

        {isFormalizationBox && !Array.isArray(formalization) && (
          <section className="n4-formalization" aria-label={formalization.title}>
            <header>
              <span>Formalización</span>
              <h2>{formalization.title}</h2>
              <p>{formalization.intro}</p>
            </header>
            <ul>
              {formalization.items.map((item) => (
                <li key={item.label}>
                  <b>{item.label}</b>
                  <span>{item.rule}</span>
                  {item.latex && <MathFormula math={item.latex} />}
                </li>
              ))}
            </ul>
          </section>
        )}

        <section className="n4-practice" aria-label="Práctica">
          <header>
            <span>Práctica</span>
            <h2>Pon a prueba lo que descubriste</h2>
          </header>
          {practiceItems.map((item) => (
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

        {content?.closing && (
          <section className="n4-closing">
            <p>{content.closing}</p>
          </section>
        )}

        <footer className="lesson-footer trigger-footer">
          <div>
            <span>Regreso al puerto</span>
            <p>Completa toda la práctica para registrar este muelle como visitado.</p>
          </div>
          <Button
            size="lg"
            disabled={!allAnswered}
            loading={finishing || returnMutation.isPending}
            onClick={() => returnMutation.mutate()}
          >
            Volver al puerto
          </Button>
        </footer>
      </div>
    </article>
  );
}
