import { useTranslation } from "react-i18next";

export function LanguageToggle() {
  const { i18n, t } = useTranslation();
  const isEs = i18n.language?.startsWith("es");

  const toggle = () => {
    i18n.changeLanguage(isEs ? "en" : "es");
  };

  return (
    <button
      onClick={toggle}
      aria-label={isEs ? "Switch to English" : "Cambiar a Español"}
      title={isEs ? "Switch to English" : "Cambiar a Español"}
      className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors w-full text-left"
    >
      <span aria-hidden="true" className="text-sm">🌐</span>
      <span>{t("lang.toggle")}</span>
    </button>
  );
}
