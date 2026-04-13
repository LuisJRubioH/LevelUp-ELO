/**
 * components/Question/AnswerOptions.tsx
 * ======================================
 * Botones de opciones de respuesta con feedback visual post-respuesta.
 */

interface AnswerOptionsProps {
  options: string[];
  selectedOption: string | null;
  correctOption: string | null; // null mientras no se ha respondido
  onSelect: (option: string) => void;
  disabled?: boolean;
}

function optionClass(
  option: string,
  selected: string | null,
  correct: string | null,
): string {
  const base =
    "w-full text-left px-4 py-3 rounded-xl border text-sm font-medium transition-all duration-200 cursor-pointer";

  if (correct === null) {
    // Antes de responder
    if (option === selected) {
      return `${base} border-violet-500 bg-violet-900/40 text-violet-200`;
    }
    return `${base} border-slate-600 bg-slate-800 text-slate-300 hover:border-violet-500/60 hover:bg-slate-700`;
  }

  // Post-respuesta
  if (option === correct) {
    return `${base} border-green-500 bg-green-900/40 text-green-200`;
  }
  if (option === selected && option !== correct) {
    return `${base} border-red-500 bg-red-900/40 text-red-200`;
  }
  return `${base} border-slate-700 bg-slate-800/50 text-slate-500`;
}

const LABELS = ["A", "B", "C", "D"];

export function AnswerOptions({
  options,
  selectedOption,
  correctOption,
  onSelect,
  disabled = false,
}: AnswerOptionsProps) {
  return (
    <div className="flex flex-col gap-3 mt-4">
      {options.map((option, idx) => (
        <button
          key={idx}
          className={optionClass(option, selectedOption, correctOption)}
          onClick={() => onSelect(option)}
          disabled={disabled || correctOption !== null}
        >
          <span className="inline-block w-6 h-6 rounded-full bg-slate-700 text-slate-300 text-xs font-bold text-center leading-6 mr-3">
            {LABELS[idx] ?? idx + 1}
          </span>
          {option}
          {correctOption !== null && option === correctOption && (
            <span className="ml-2 text-green-400">✓</span>
          )}
          {correctOption !== null && option === selectedOption && option !== correctOption && (
            <span className="ml-2 text-red-400">✗</span>
          )}
        </button>
      ))}
    </div>
  );
}
