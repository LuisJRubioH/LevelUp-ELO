import { useEffect, useRef, useState, type MouseEvent } from "react";

/**
 * Bajo 1024px la barra lateral del shell `.lue-tc` se oculta; este estado la
 * abre como cajón (TeacherConsole.css: `.tc-side.open`). Se cierra al tocar un
 * enlace del cajón, con Escape o con su botón ✕, que recibe el foco al abrir.
 */
export function useSideDrawer() {
  const [open, setOpen] = useState(false);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const closeOnLink = (e: MouseEvent<HTMLElement>) => {
    if ((e.target as HTMLElement).closest("a")) setOpen(false);
  };

  return { open, setOpen, closeRef, closeOnLink };
}
