import { Link } from "react-router-dom";

/** Barra superior del shell `.lue-tc` bajo 1024px: marca + botón que abre el cajón. */
export function MobileBar({ home, open, onOpen }: { home: string; open: boolean; onOpen: () => void }) {
  return (
    <header className="tc-mobbar">
      <Link to={home} aria-label="Oulad">
        <img className="brand-logo brand-logo-dark" src="/oulad-logo-dark.png" alt="Oulad" />
        <img className="brand-logo brand-logo-light" src="/oulad-logo-light.png" alt="Oulad" />
      </Link>
      <button
        type="button"
        className="tc-mobbar-menu"
        aria-expanded={open}
        aria-controls="tc-side"
        onClick={onOpen}
      >
        <span className="ic" aria-hidden="true">☰</span>
        Menú
      </button>
    </header>
  );
}
