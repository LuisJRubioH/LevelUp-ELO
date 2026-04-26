/**
 * ReportProblemButton — botón discreto que abre un modal para que el
 * estudiante envíe un reporte técnico (descripción ≥10 caracteres).
 */

import { useEffect, useRef, useState } from "react";
import { studentApi } from "../../api/student";

const MIN_LENGTH = 10;
const MAX_LENGTH = 2000;

const DIALOG_TITLE_ID = "report-dialog-title";

export function ReportProblemButton() {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 3000);
    return () => clearTimeout(t);
  }, [toast]);

  function closeModal() {
    setOpen(false);
    triggerRef.current?.focus();
  }

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeModal();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]); // eslint-disable-line react-hooks/exhaustive-deps

  const trimmed = text.trim();
  const valid = trimmed.length >= MIN_LENGTH && trimmed.length <= MAX_LENGTH;

  async function handleSubmit() {
    if (!valid || submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      const r = await studentApi.reportProblem(trimmed);
      setOpen(false);
      setText("");
      setToast(r.message ?? "Reporte enviado. Gracias.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo enviar el reporte.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <button
        ref={triggerRef}
        onClick={() => setOpen(true)}
        className="w-full text-left text-xs text-slate-500 hover:text-slate-200 transition-colors"
        aria-haspopup="dialog"
        aria-expanded={open}
      >
        Reportar un problema
      </button>

      {toast && (
        <div
          role="status"
          aria-live="polite"
          className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-emerald-600 text-white text-sm px-4 py-2 rounded-lg shadow-lg"
        >
          {toast}
        </div>
      )}

      {open && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby={DIALOG_TITLE_ID}
          className="fixed inset-0 z-40 flex items-center justify-center bg-black/60 px-4"
          onClick={closeModal}
        >
          <div
            className="w-full max-w-md rounded-xl border border-slate-700 bg-[#12121A] p-5 space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <header className="flex items-start justify-between gap-2">
              <div>
                <h3 id={DIALOG_TITLE_ID} className="text-base font-semibold text-slate-100">
                  Reportar un problema
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Cuéntanos qué pasó. Nuestro equipo lo revisará lo antes posible.
                </p>
              </div>
              <button
                onClick={closeModal}
                aria-label="Cerrar modal"
                className="shrink-0 text-slate-500 hover:text-slate-300 transition-colors mt-0.5"
              >
                ✕
              </button>
            </header>

            <textarea
              value={text}
              onChange={(e) => {
                setText(e.target.value);
                if (error) setError(null);
              }}
              rows={5}
              maxLength={MAX_LENGTH}
              placeholder="Describe el problema con tantos detalles como puedas (mínimo 10 caracteres)…"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-violet-500 resize-none"
              aria-label="Descripción del problema"
              aria-required="true"
              aria-invalid={trimmed.length > 0 && trimmed.length < MIN_LENGTH}
              autoFocus
            />

            <div className="flex items-center justify-between text-xs" aria-live="polite">
              <span
                className={
                  trimmed.length === 0
                    ? "text-slate-600"
                    : trimmed.length < MIN_LENGTH
                      ? "text-rose-400"
                      : "text-slate-500"
                }
              >
                {trimmed.length}/{MAX_LENGTH} {trimmed.length < MIN_LENGTH && "(mín. 10)"}
              </span>
              {error && <span role="alert" className="text-rose-400">{error}</span>}
            </div>

            <div className="flex justify-end gap-2 pt-1">
              <button
                onClick={closeModal}
                disabled={submitting}
                className="px-3 py-1.5 text-sm text-slate-400 hover:text-slate-200 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleSubmit}
                disabled={!valid || submitting}
                aria-disabled={!valid || submitting}
                className="px-4 py-1.5 text-sm font-medium rounded-lg bg-violet-600 text-white hover:bg-violet-500 transition-colors disabled:bg-slate-700 disabled:text-slate-500"
              >
                {submitting ? "Enviando…" : "Enviar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
