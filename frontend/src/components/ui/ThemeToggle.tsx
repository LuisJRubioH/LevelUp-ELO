import { useThemeStore } from "../../stores/themeStore";

export function ThemeToggle() {
  const { theme, toggleTheme } = useThemeStore();
  const isLight = theme === "light";

  return (
    <button
      onClick={toggleTheme}
      aria-label={isLight ? "Cambiar a modo oscuro" : "Cambiar a modo claro"}
      title={isLight ? "Modo oscuro" : "Modo claro"}
      className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors w-full text-left"
    >
      <span aria-hidden="true" className="text-sm">{isLight ? "🌙" : "☀️"}</span>
      <span>{isLight ? "Modo oscuro" : "Modo claro"}</span>
    </button>
  );
}
