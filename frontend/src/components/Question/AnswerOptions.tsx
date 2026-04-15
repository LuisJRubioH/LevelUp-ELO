/**
 * components/Question/AnswerOptions.tsx
 * ======================================
 * Botones de opciones de respuesta con feedback visual post-respuesta.
 *
 * IMPORTANTE: nunca se revela cuál era la opción correcta. Tras responder
 * solo se colorea la opción elegida (verde si acertó, rojo si falló) —
 * las demás quedan neutras para que el estudiante no memorice la respuesta
 * si la pregunta vuelve a aparecer.
 */

import katex from "katex";
import "katex/dist/katex.min.css";

/** Renderiza texto con LaTeX inline: $expr$ */
function RenderOption({ text }: { text: string }) {
  const parts = text.split(/(\$[^$]+\$)/g);
  if (parts.length === 1) return <>{text}</>;
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

interface AnswerOptionsProps {
  options: string[];
  selectedOption: string | null;
  /** null = pre-respuesta; true/false = feedback de la opción elegida */
  isCorrect: boolean | null;
  onSelect: (option: string) => void;
  disabled?: boolean;
}

function optionClass(
  option: string,
  selected: string | null,
  isCorrect: boolean | null,
): string {
  const base =
    "w-full text-left px-4 py-3 rounded-xl border text-sm font-medium transition-all duration-200 cursor-pointer";

  if (isCorrect === null) {
    // Antes de responder
    if (option === selected) {
      return `${base} border-violet-500 bg-violet-900/40 text-violet-200`;
    }
    return `${base} border-slate-600 bg-slate-800 text-slate-300 hover:border-violet-500/60 hover:bg-slate-700`;
  }

  // Post-respuesta: solo se colorea la opción seleccionada.
  if (option === selected) {
    return isCorrect
      ? `${base} border-green-500 bg-green-900/40 text-green-200`
      : `${base} border-red-500 bg-red-900/40 text-red-200`;
  }
  return `${base} border-slate-700 bg-slate-800/50 text-slate-500`;
}

const LABELS = ["A", "B", "C", "D"];

export function AnswerOptions({
  options,
  selectedOption,
  isCorrect,
  onSelect,
  disabled = false,
}: AnswerOptionsProps) {
  const answered = isCorrect !== null;
  return (
    <div className="flex flex-col gap-3 mt-4">
      {options.map((option, idx) => (
        <button
          key={idx}
          className={optionClass(option, selectedOption, isCorrect)}
          onClick={() => onSelect(option)}
          disabled={disabled || answered}
        >
          <span className="inline-block w-6 h-6 rounded-full bg-slate-700 text-slate-300 text-xs font-bold text-center leading-6 mr-3">
            {LABELS[idx] ?? idx + 1}
          </span>
          <RenderOption text={option} />
          {answered && option === selectedOption && (
            <span className={`ml-2 ${isCorrect ? "text-green-400" : "text-red-400"}`}>
              {isCorrect ? "✓" : "✗"}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}
