/**
 * components/Question/QuestionImage.tsx
 * ======================================
 * Imagen opcional adjunta al enunciado. Si la URL es nula/vacía, no renderiza.
 * Si la imagen falla a cargar (404, red caída, cold start del backend), muestra
 * un mensaje claro con botón de reintentar — antes solo se veía el `alt` ("Figura")
 * lo que confundía al estudiante.
 */

import { useState, useCallback } from "react";
import { resolveImageUrl } from "../../api/client";

interface QuestionImageProps {
  imageUrl?: string | null;
  alt?: string;
  className?: string;
}

export function QuestionImage({
  imageUrl,
  alt = "Diagrama del problema",
  className,
}: QuestionImageProps) {
  const resolved = resolveImageUrl(imageUrl ?? undefined);
  const [failed, setFailed] = useState(false);
  const [retryKey, setRetryKey] = useState(0);

  const onRetry = useCallback(() => {
    setFailed(false);
    setRetryKey((k) => k + 1);
  }, []);

  if (!resolved) return null;

  if (failed) {
    return (
      <div
        role="status"
        className={[
          "mt-4 px-4 py-3 rounded-lg border border-amber-700/40 bg-amber-900/20 text-sm text-amber-200 flex items-center gap-3 justify-between",
          className ?? "",
        ].join(" ")}
      >
        <span>No se pudo cargar la imagen del problema.</span>
        <button
          type="button"
          onClick={onRetry}
          className="shrink-0 text-xs bg-amber-500 hover:bg-amber-400 text-slate-900 font-medium px-3 py-1 rounded-md transition-colors"
        >
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <img
      key={retryKey}
      src={resolved}
      alt={alt}
      onError={() => setFailed(true)}
      className={className ?? "mt-4 max-w-full rounded-lg"}
    />
  );
}
