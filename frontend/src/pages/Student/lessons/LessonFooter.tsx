import { useTranslation } from "react-i18next";
import { Button } from "../../../components/ui/Button";

type Props = {
  label: string;
  body: string;
  finishText: string;
  completed: boolean;
  canFinish: boolean;
  finishing: boolean;
  onFinish: () => void;
  onBack: () => void;
};

/**
 * Pie compartido de las lecciones guiadas (B08–B13).
 * "Volver al mapa" SIEMPRE está habilitado (no se bloquea por resolver el
 * ejercicio) para que el estudiante nunca quede atrapado. "Finalizar" sigue
 * gateado por `canFinish` y marca el nodo como completado.
 */
export function LessonFooter({
  label,
  body,
  finishText,
  completed,
  canFinish,
  finishing,
  onFinish,
  onBack,
}: Props) {
  const { t } = useTranslation();
  return (
    <footer className="lesson-footer trigger-footer">
      <div>
        <span>{label}</span>
        <p>{body}</p>
      </div>
      <div className="lesson-footer-actions">
        {!completed && (
          <Button variant="secondary" onClick={onBack}>
            {t("prealgebra.backToMap")}
          </Button>
        )}
        <Button
          size="lg"
          disabled={!completed && !canFinish}
          loading={finishing}
          onClick={onFinish}
        >
          {completed ? t("prealgebra.backToMap") : finishText}
        </Button>
      </div>
    </footer>
  );
}
