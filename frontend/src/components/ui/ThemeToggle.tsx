import { useTranslation } from "react-i18next";
import { useThemeStore } from "../../stores/themeStore";

export function ThemeToggle() {
  const { theme, toggleTheme } = useThemeStore();
  const { t } = useTranslation();
  const isLight = theme === "light";

  return (
    <button
      onClick={toggleTheme}
      aria-label={isLight ? t("theme.dark") : t("theme.light")}
      title={isLight ? t("theme.dark") : t("theme.light")}
      className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors w-full text-left"
    >
      <span aria-hidden="true" className="text-sm">{isLight ? "🌙" : "☀️"}</span>
      <span>{isLight ? t("theme.dark") : t("theme.light")}</span>
    </button>
  );
}
