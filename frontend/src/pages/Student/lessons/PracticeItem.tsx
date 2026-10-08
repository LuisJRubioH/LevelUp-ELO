import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { type LessonInteractionResult, type N4PracticeItem } from "../../../api/student";
import { MathFormula } from "../../../components/Math/MathContent";
import { Button } from "../../../components/ui/Button";
import "./PracticeItem.css";

export type AnswerMap = Record<string, string>;
export type FeedbackMap = Record<string, string>;

type RestoredResponse = {
  is_expected: boolean | null;
  selected_option: string;
};

export function restoredAnswers(responses: Record<string, RestoredResponse>): AnswerMap {
  return Object.fromEntries(
    Object.entries(responses)
      .filter(([, response]) => response.is_expected)
      .map(([id, response]) => [id, response.selected_option]),
  );
}

/** Item de práctica compartido por los rompe-hielo/hubs de N2/N3/N4 y la
 * práctica mixta de N4 (numeric/single_select/multi_select + historia+imagen
 * opcional). Ver .claude/skills/prealgebra-narrative-style/SKILL.md. */
export function PracticeItem({
  item,
  lessonNodeId,
  answers,
  feedback,
  mutation,
}: {
  item: N4PracticeItem;
  lessonNodeId: string;
  answers: AnswerMap;
  feedback: FeedbackMap;
  mutation: ReturnType<typeof useMutation<LessonInteractionResult, unknown, { id: string; option: string }>>;
}) {
  const interactionId = `${lessonNodeId}-${item.id}`;
  const answered = Boolean(answers[interactionId]);
  const [draft, setDraft] = useState(answers[interactionId] ?? "");
  const [selectedMulti, setSelectedMulti] = useState<Set<string>>(
    new Set((answers[interactionId] ?? "").split(",").filter(Boolean)),
  );

  const storyBlock = (item.story || item.image_slot) && (
    <div className="level-item-story">
      {item.story && <p className="level-item-story-text">{item.story}</p>}
      {item.image_slot && (
        <div className="level-item-image-slot" role="img" aria-label="Imagen de la situación">
          {item.image ? <img src={item.image} alt="" loading="lazy" /> : <span>Imagen aquí</span>}
          {item.support_objects && item.support_objects.length > 0 && (
            <ul className="level-item-support-objects">
              {item.support_objects.map((object) => (
                <li key={object}>{object}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );

  if (item.kind === "numeric") {
    return (
      <div className="level-practice-item">
        {storyBlock}
        <p>{item.prompt}</p>
        {item.expr && (
          <div className="n2-expression"><MathFormula math={item.expr} /></div>
        )}
        <div className="numeric-answer">
          <input
            value={draft}
            disabled={answered}
            inputMode="decimal"
            aria-label={`Respuesta ${item.id}`}
            onChange={(event) => setDraft(event.target.value)}
          />
          <Button
            variant="secondary"
            disabled={answered || !draft}
            loading={mutation.isPending}
            onClick={() => mutation.mutate({ id: interactionId, option: draft })}
          >
            Validar
          </Button>
        </div>
        {feedback[interactionId] && <p className="trigger-feedback" role="status">{feedback[interactionId]}</p>}
      </div>
    );
  }

  if (item.kind === "single_select") {
    const selected = answers[interactionId];
    return (
      <div className="level-practice-item">
        {storyBlock}
        <p>{item.prompt}</p>
        <div className="level-options">
          {item.options?.map((option) => (
            <button
              key={option.id}
              type="button"
              className={`level-option-btn ${selected === option.id ? "selected" : ""}`}
              disabled={answered}
              aria-pressed={selected === option.id}
              onClick={() => mutation.mutate({ id: interactionId, option: option.id })}
            >
              {option.text}
            </button>
          ))}
        </div>
        {feedback[interactionId] && <p className="trigger-feedback" role="status">{feedback[interactionId]}</p>}
      </div>
    );
  }

  const toggle = (optionId: string) => {
    setSelectedMulti((current) => {
      const next = new Set(current);
      if (next.has(optionId)) next.delete(optionId);
      else next.add(optionId);
      return next;
    });
  };

  return (
    <div className="level-practice-item">
      {storyBlock}
      <p>{item.prompt}</p>
      <div className="level-options">
        {item.valid_options?.map((optionId) => (
          <button
            key={optionId}
            type="button"
            className={`level-option-btn ${selectedMulti.has(optionId) ? "selected" : ""}`}
            disabled={answered}
            aria-pressed={selectedMulti.has(optionId)}
            onClick={() => toggle(optionId)}
          >
            {optionId}
          </button>
        ))}
      </div>
      <Button
        variant="secondary"
        disabled={answered || selectedMulti.size === 0}
        loading={mutation.isPending}
        onClick={() =>
          mutation.mutate({ id: interactionId, option: Array.from(selectedMulti).sort().join(",") })
        }
      >
        Validar selección
      </Button>
      {feedback[interactionId] && <p className="trigger-feedback" role="status">{feedback[interactionId]}</p>}
    </div>
  );
}
