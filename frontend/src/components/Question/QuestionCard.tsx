/**
 * components/Question/QuestionCard.tsx
 * =====================================
 * Tarjeta que muestra el enunciado de la pregunta con renderizado LaTeX
 * y una imagen opcional.
 */

import { QuestionImage } from "./QuestionImage";
import { MathText } from "../Math/MathContent";
import "../../pages/Student/StudentContent.css";

interface QuestionCardProps {
  content: string;
  topic: string;
  difficulty: number;
  tags?: string[];
  imageUrl?: string;
  timerFormatted: string;
  questionNumber: number;
}

function DifficultyStars({ difficulty }: { difficulty: number }) {
  const filled =
    difficulty < 750 ? 1 : difficulty < 950 ? 2 : difficulty < 1150 ? 3 : difficulty < 1400 ? 4 : 5;
  return (
    <span className="text-sm" aria-label={`Dificultad ${filled} de 5`}>
      {Array.from({ length: 5 }).map((_, i) => (
        <span key={i} style={{ color: i < filled ? "#ffd700" : "#334155" }}>
          ★
        </span>
      ))}
    </span>
  );
}

export function QuestionCard({
  content,
  topic,
  difficulty,
  tags,
  imageUrl,
  timerFormatted,
  questionNumber,
}: QuestionCardProps) {
  return (
    <div className="sp-card fade-in">
      {/* Header: tópico, dificultad y timer.
          flex-wrap permite que el grupo de tópico+estrellas y el grupo de
          número+timer se apilen en mobile (375px) en lugar de solaparse. */}
      <div className="flex flex-wrap items-center justify-between gap-y-2 gap-x-3 mb-4">
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <span
            className="text-xs font-medium text-violet-400 bg-violet-900/40 px-2 py-1 rounded-full truncate max-w-[160px] shrink"
            title={topic}
          >
            {topic}
          </span>
          <DifficultyStars difficulty={difficulty} />
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-xs text-slate-500">#{questionNumber}</span>
          <span
            className="text-lg font-bold text-amber-400"
            style={{ fontVariantNumeric: "tabular-nums" }}
          >
            {timerFormatted}
          </span>
        </div>
      </div>

      {/* Tags de habilidades / taxonomía */}
      {tags && tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {tags.map((tag) => (
            <span
              key={tag}
              className="text-xs text-slate-400 bg-slate-700/60 border border-slate-600 px-2 py-0.5 rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Enunciado */}
      <p className="text-base leading-relaxed text-slate-100 mb-4">
        <MathText text={content} />
      </p>

      {/* Imagen opcional */}
      <QuestionImage
        imageUrl={imageUrl}
        alt="Figura del problema"
        className="max-w-full rounded-lg border border-slate-600 mt-2"
      />

    </div>
  );
}
