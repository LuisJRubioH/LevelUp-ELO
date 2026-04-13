/**
 * components/KatIA/KatIAAvatar.tsx
 * =================================
 * Avatar de KatIA con GIF condicional (correcto/error) y mensaje de texto.
 * Los assets se sirven desde /KatIA/ (carpeta en la raíz del repo).
 * En Vite, los archivos en `public/` se sirven estáticos.
 */

interface KatIAProps {
  state?: "idle" | "thinking" | "correct" | "error";
  message?: string;
  size?: "sm" | "md" | "lg";
}

const sizeClasses = {
  sm: "w-16 h-16",
  md: "w-24 h-24",
  lg: "w-32 h-32",
};

export function KatIAAvatar({ state = "idle", message, size = "md" }: KatIAProps) {
  const src =
    state === "correct"
      ? "/katia/correcto_compressed.gif"
      : state === "error"
        ? "/katia/errores_compressed.gif"
        : state === "thinking"
          ? "/katia/correcto_compressed.gif" // misma animación para "revisando"
          : "/katia/katIA.png";

  return (
    <div className="flex flex-col items-center gap-2">
      <img
        src={src}
        alt={`KatIA — ${state}`}
        className={`${sizeClasses[size]} object-contain rounded-xl`}
      />
      {message && (
        <div className="max-w-xs text-center text-sm text-slate-300 bg-slate-800 rounded-xl px-3 py-2 border border-slate-700">
          <span className="text-violet-400 font-medium">KatIA: </span>
          {message}
        </div>
      )}
    </div>
  );
}
