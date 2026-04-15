/**
 * components/Question/QuestionCard.tsx
 * =====================================
 * Tarjeta que muestra el enunciado de la pregunta con renderizado LaTeX
 * y una imagen opcional.
 */

import katex from "katex";
import "katex/dist/katex.min.css";

interface QuestionCardProps {
  content: string;
  topic: string;
  difficulty: number;
  tags?: string[];
  imageUrl?: string;
  timerFormatted: string;
  questionNumber: number;
}

/** Renderiza texto que puede contener LaTeX inline: $expr$ */
function RenderContent({ text }: { text: string }) {
  const parts = text.split(/(\$[^$]+\$)/g);
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
            return <span key={i} className="text-red-400">{part}</span>;
          }
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
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
    <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700 fade-in">
      {/* Header: tópico, dificultad y timer */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-xs font-medium text-violet-400 bg-violet-900/40 px-2 py-1 rounded-full">
            {topic}
          </span>
          <DifficultyStars difficulty={difficulty} />
        </div>
        <div className="flex items-center gap-2">
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
        <RenderContent text={content} />
      </p>

      {/* Imagen opcional */}
      {imageUrl && (
        <img
          src={imageUrl}
          alt="Figura del problema"
          className="max-w-full rounded-lg border border-slate-600 mt-2"
        />
      )}
    </div>
  );
}
