import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { studentApi, type LessonDetail } from "../../../api/student";
import { LessonFooter } from "./LessonFooter";
import "./ClosingDiagnosticLesson.css";

type Props = {
  lesson: LessonDetail;
  courseId: string;
  onBack: () => void;
  onFinish: () => Promise<void>;
  finishing: boolean;
};

export function ClosingDiagnosticLesson({ lesson, courseId, onBack, onFinish, finishing }: Props) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const { data, isLoading } = useQuery({
    queryKey: ["prealgebra-summary", courseId],
    queryFn: () => studentApi.prealgebraSummary(courseId),
  });

  return (
    <article className="lesson-page closing-page" aria-labelledby="lesson-title">
      <header className="lesson-topbar">
        <button className="lesson-back" onClick={onBack}>{t("prealgebra.backToMap")}</button>
        <span className="lesson-safe">{t("prealgebra.safeZone")}</span>
      </header>

      <div className="lesson-shell closing-shell">
        <header className="closing-heading">
          <span className="lesson-kicker">{t("prealgebra.n1.b13.kicker")}</span>
          <h1 id="lesson-title">{t("prealgebra.n1.b13.title")}</h1>
        </header>

        <div className="level-presentation-media" role="img" aria-label={t("prealgebra.n1.b13.title")}>
          <img src="/leccion/01-prealg-n1-agora/b13-diagnostico-v4.png" alt="" loading="lazy" />
        </div>

        {isLoading || !data ? (
          <p className="closing-loading">{t("prealgebra.loading")}</p>
        ) : (
          <>
            <section className={`closing-result closing-${data.overall_status}`} role="status">
              <span>{t(`prealgebra.n1.b13.status.${data.overall_status}.label`)}</span>
              <p>{t(`prealgebra.n1.b13.status.${data.overall_status}.body`)}</p>
            </section>

            <section className="closing-progress" aria-label={t("prealgebra.n1.b13.progressAria")}>
              <div className="closing-metric">
                <b>{data.completed_nodes}/{data.total_nodes}</b>
                <span>{t("prealgebra.n1.b13.nodesCompleted")}</span>
              </div>
            </section>

            <section className="closing-review">
              <h2>{t("prealgebra.n1.b13.review.title")}</h2>
              {data.review.length === 0 ? (
                <p className="closing-noreview">{t("prealgebra.n1.b13.review.none")}</p>
              ) : (
                <ul className="closing-review-list">
                  {data.review.map((item) => (
                    <li key={item.node_id}>
                      <span>{t(item.label_key)}</span>
                      <button
                        className="closing-review-link"
                        onClick={() => navigate(`/student/course/${courseId}/lesson/${encodeURIComponent(item.node_id)}`)}
                      >
                        {t("prealgebra.n1.b13.review.go")}
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </>
        )}

        <LessonFooter
          label={t("prealgebra.n1.b13.footerLabel")}
          body={t("prealgebra.n1.b13.footerBody")}
          finishText={t("prealgebra.n1.b13.finish")}
          completed={lesson.state === "completed"}
          canFinish={true}
          finishing={finishing}
          onFinish={onFinish}
          onBack={onBack}
        />
      </div>
    </article>
  );
}
