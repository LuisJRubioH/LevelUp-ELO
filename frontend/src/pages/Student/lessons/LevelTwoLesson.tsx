import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { studentApi, type LessonDetail, type LessonInteractionResult } from "../../../api/student";
import { Button } from "../../../components/ui/Button";
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

// Spec 003 N5: N2's operation nodes are eleven-block nodes (`ElevenBlockLesson`); this file
// renders only the city hub.
export function LevelTwoLesson(props: Props) {
  return <LevelTwoHub {...props} />;
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
