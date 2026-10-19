import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import {
  studentApi,
  type LessonDetail,
  type LessonInteractionResult,
} from "../../../api/student";
import { MathFormula } from "../../../components/Math/MathContent";
import { Button } from "../../../components/ui/Button";
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

// Spec 003 N5: every destination is an eleven-block node (`ElevenBlockLesson`); this file
// renders only the hubs (`level_hub_port`, `level_hub_cards`).
export function LevelFourLesson(props: Props) {
  return <LevelFourHub {...props} />;
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
  // Los destinos se abren en orden (V2-R14) y el hub mismo los bloquea hasta
  // terminarse: «Zarpar» solo aparece donde el mapa ya deja entrar. Antes los
  // seis llevaban a «No pudimos cargar esta lección» (403).
  const { data: map } = useQuery({
    queryKey: ["course-map", courseId],
    queryFn: () => studentApi.courseMap(courseId),
  });
  const canSail = (nodeId: string) => {
    const state = map?.nodes.find((n) => n.node_id === nodeId)?.state;
    return state !== undefined && state !== "blocked";
  };

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
                  {allOpened && canSail(card.node_id) && (
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
