import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useNavigate, useParams } from "react-router-dom";
import {
  studentApi,
  type LessonDetail,
  type LessonEvent,
  type LessonInteractionResult,
} from "../../api/student";
import { Button } from "../../components/ui/Button";
import { MathFormula } from "../../components/Math/MathContent";
import { ElevenBlockLesson, isElevenBlock } from "./lessons/blocks/ElevenBlockLesson";
import { ClosingDiagnosticLesson } from "./lessons/ClosingDiagnosticLesson";
import { LevelTwoLesson } from "./lessons/LevelTwoLesson";
import { LevelThreeLesson } from "./lessons/LevelThreeLesson";
import { LevelFourLesson } from "./lessons/LevelFourLesson";
import { KatiaStorySlot } from "./lessons/KatiaStorySlot";
import "./Lesson.css";

const B01_ID = "PREALG-N1-B01-BIENVENIDA";
const B02_ID = "PREALG-N1-B02-PREGUNTA-DETONADORA";
const B13_ID = "PREALG-N1-B13-CIERRE-DIAGNOSTICO";
const N2_IDS = [
  "PREALG-N2-E00-CIUDAD",
  "PREALG-N2-E01-SUMA-JUNTAR",
  "PREALG-N2-E02-RESTA-QUITAR",
  "PREALG-N2-E03-MULTIPLICACION-AGRUPAR",
  "PREALG-N2-E04-DIVISION-REPARTIR",
  "PREALG-N2-E05-POTENCIACION-CRECER",
  "PREALG-N2-E06-RADICACION-RAIZ",
] as const;
const N3_IDS = [
  "PREALG-N3-M00-LABORATORIO",
  "PREALG-N3-M01-CONMUTATIVA",
  "PREALG-N3-M02-ASOCIATIVA",
  "PREALG-N3-M03-DISTRIBUTIVA",
  "PREALG-N3-M04-ELEMENTO-NEUTRO",
  "PREALG-N3-M05-INVERSOS",
] as const;
const N4_IDS = [
  "PREALG-N4-C00-PUERTO-DE-LA-POLIS",
  "PREALG-N4-C01-DIVISIBILIDAD",
  "PREALG-N4-C02-MULTIPLOS",
  "PREALG-N4-C03-PRIMOS",
  "PREALG-N4-C04-FACTORIZACION-PRIMA",
  "PREALG-N4-C05-MCD",
  "PREALG-N4-C06-MCM",
] as const;
const ALG_HUB_ID = "ALG-A00-PAPIRO-CUATRO-CASAS";

export function Lesson() {
  const { courseId = "", nodeId = "" } = useParams();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const viewedRef = useRef(false);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["lesson", courseId, nodeId],
    queryFn: () => studentApi.lesson(courseId, nodeId),
    enabled: Boolean(courseId && nodeId),
  });

  const [objectivesOpen, setObjectivesOpen] = useState(false);
  const [conventionOpen, setConventionOpen] = useState(false);

  const eventMutation = useMutation({
    mutationFn: (event: LessonEvent) => studentApi.lessonEvent(courseId, nodeId, event),
    onSuccess: (lesson) => {
      queryClient.setQueryData(["lesson", courseId, nodeId], lesson);
    },
  });

  useEffect(() => {
    if (!data || viewedRef.current) return;
    viewedRef.current = true;
    const expanded = data.presentation === "basico";
    setObjectivesOpen(expanded || data.progress.objectives_viewed);
    setConventionOpen(expanded || data.progress.math_convention_viewed);
    eventMutation.mutate("node_viewed");
    if (nodeId === B01_ID) {
      if (expanded && !data.progress.objectives_viewed) {
        eventMutation.mutate("objectives_viewed");
      }
      if (expanded && !data.progress.math_convention_viewed) {
        eventMutation.mutate("math_convention_viewed");
      }
    }
    // El primer payload fija el estado inicial; no debe repetirse en cada refetch.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data?.node_id]);

  const toggleObjectives = () => {
    const next = !objectivesOpen;
    setObjectivesOpen(next);
    if (next && !data?.progress.objectives_viewed) eventMutation.mutate("objectives_viewed");
  };

  const toggleConvention = () => {
    const next = !conventionOpen;
    setConventionOpen(next);
    if (next && !data?.progress.math_convention_viewed) {
      eventMutation.mutate("math_convention_viewed");
    }
  };

  const finish = async () => {
    if (data?.state !== "completed") await eventMutation.mutateAsync("node_completed");
    await queryClient.invalidateQueries({ queryKey: ["course-map", courseId] });
    navigate(`/student/course/${courseId}/map`);
  };

  if (isLoading) {
    return <div className="lesson-state">{t("prealgebra.loading")}</div>;
  }
  // Aquí había una lista blanca con los 50 node_id. Era redundante y había que
  // tocarla con cada nodo nuevo: el backend ya devuelve 404 para un nodo que no
  // existe, y eso llega como `isError`. Las listas N2/N3/N4 siguen abajo porque
  // eligen renderer, que es otra cosa.
  if (isError || !data) {
    return <div className="lesson-state error">{t("prealgebra.error")}</div>;
  }

  // Un nodo reconstruido a 11 bloques se declara en su propio contenido y se
  // pinta con el renderer genérico: migrar un nodo no toca este archivo.
  if (isElevenBlock(data.content)) {
    return (
      <ElevenBlockLesson
        lesson={data}
        courseId={courseId}
        onBack={() => navigate(`/student/course/${courseId}/map`)}
        onFinish={finish}
        finishing={eventMutation.isPending}
      />
    );
  }

  // Los hubs se eligen por tipo, no por id: el backend ya declara
  // `level_hub_cards`, asi que un hub nuevo no toca este archivo.
  if (
    data.node_type === "level_hub_cards" ||
    nodeId === ALG_HUB_ID ||
    (N4_IDS as readonly string[]).includes(nodeId)
  ) {
    return (
      <LevelFourLesson
        lesson={data}
        courseId={courseId}
        onBack={() => navigate(`/student/course/${courseId}/map`)}
        onFinish={finish}
        finishing={eventMutation.isPending}
      />
    );
  }

  if ((N3_IDS as readonly string[]).includes(nodeId)) {
    return (
      <LevelThreeLesson
        lesson={data}
        courseId={courseId}
        onBack={() => navigate(`/student/course/${courseId}/map`)}
        onFinish={finish}
        finishing={eventMutation.isPending}
      />
    );
  }

  if ((N2_IDS as readonly string[]).includes(nodeId)) {
    return (
      <LevelTwoLesson
        lesson={data}
        courseId={courseId}
        onBack={() => navigate(`/student/course/${courseId}/map`)}
        onFinish={finish}
        finishing={eventMutation.isPending}
      />
    );
  }

  if (nodeId === B02_ID) {
    return (
      <TriggerQuestionLesson
        lesson={data}
        courseId={courseId}
        onBack={() => navigate(`/student/course/${courseId}/map`)}
        onFinish={finish}
        finishing={eventMutation.isPending}
      />
    );
  }

  if (nodeId === B13_ID) {
    return (
      <ClosingDiagnosticLesson
        lesson={data}
        courseId={courseId}
        onBack={() => navigate(`/student/course/${courseId}/map`)}
        onFinish={finish}
        finishing={eventMutation.isPending}
      />
    );
  }

  const isAdvanced = data.presentation === "avanzado";

  return (
    <article className="lesson-page" aria-labelledby="lesson-title">
      <header className="lesson-topbar">
        <button
          className="lesson-back"
          onClick={() => navigate(`/student/course/${courseId}/map`)}
        >
          {t("prealgebra.backToMap")}
        </button>
        <span className="lesson-safe">{t("prealgebra.safeZone")}</span>
      </header>

      <div className="lesson-shell">
        <section className="lesson-hero">
          <div className="lesson-copy">
            <span className="lesson-kicker">{t("prealgebra.n1.b01.kicker")}</span>
            <h1 id="lesson-title">{t("prealgebra.n1.b01.title")}</h1>
            <p className="lesson-lead">
              {t(
                isAdvanced
                  ? "prealgebra.n1.b01.leadAdvanced"
                  : "prealgebra.n1.b01.lead",
              )}
            </p>
            {!isAdvanced && <p className="lesson-body">{t("prealgebra.n1.b01.body")}</p>}
          </div>
        </section>

        <KatiaStorySlot
          eyebrow="KatIA"
          body={t("prealgebra.n1.b01.katiaMessage")}
          imageSrc="/leccion/01-prealg-n1-agora/b01-bienvenida-v4.png"
          imageAlt={t("prealgebra.n1.b01.katiaAlt")}
        />

        <div className="lesson-disclosures">
          <section className={`lesson-panel ${objectivesOpen ? "open" : ""}`}>
            <button
              className="lesson-panel-trigger"
              onClick={toggleObjectives}
              aria-expanded={objectivesOpen}
            >
              <span>
                <small>{t("prealgebra.n1.b01.objectivesLabel")}</small>
                {t("prealgebra.n1.b01.objectivesTitle")}
              </span>
              <span aria-hidden="true">{objectivesOpen ? "−" : "+"}</span>
            </button>
            {objectivesOpen && (
              <ul className="lesson-objectives">
                <li>{t("prealgebra.n1.b01.objectives.recognize")}</li>
                <li>{t("prealgebra.n1.b01.objectives.explain")}</li>
                <li>{t("prealgebra.n1.b01.objectives.classify")}</li>
                <li>{t("prealgebra.n1.b01.objectives.membership")}</li>
                <li className="optional">{t("prealgebra.n1.b01.objectives.optional")}</li>
              </ul>
            )}
          </section>

          <section className={`lesson-panel convention ${conventionOpen ? "open" : ""}`}>
            <button
              className="lesson-panel-trigger"
              onClick={toggleConvention}
              aria-expanded={conventionOpen}
            >
              <span>
                <small>{t("prealgebra.n1.b01.conventionLabel")}</small>
                {t("prealgebra.n1.b01.conventionTitle")}
              </span>
              <span aria-hidden="true">{conventionOpen ? "−" : "+"}</span>
            </button>
            {conventionOpen && (
              <div className="lesson-convention-body">
                <div
                  className="lesson-formula"
                  aria-label={t("prealgebra.n1.b01.conventionAria")}
                >
                  <MathFormula math={String.raw`\mathbb{N}=\{0,1,2,3,\ldots\}`} />
                </div>
                <p>{t("prealgebra.n1.b01.conventionBody")}</p>
              </div>
            )}
          </section>
        </div>

        <footer className="lesson-footer">
          <div>
            <span>{t("prealgebra.n1.b01.footerLabel")}</span>
            <p>{t("prealgebra.n1.b01.footerBody")}</p>
          </div>
          <Button size="lg" onClick={finish} loading={eventMutation.isPending}>
            {data.state === "completed"
              ? t("prealgebra.backToMap")
              : t("prealgebra.n1.b01.start")}
          </Button>
        </footer>
      </div>
    </article>
  );
}

type TriggerProps = {
  lesson: LessonDetail;
  courseId: string;
  onBack: () => void;
  onFinish: () => Promise<void>;
  finishing: boolean;
};

const Q01 = "PREALG-N1-B02-Q01";
const Q02 = "PREALG-N1-B02-Q02";

function TriggerQuestionLesson({ lesson, courseId, onBack, onFinish, finishing }: TriggerProps) {
  const { t } = useTranslation();
  const storedQ1 = lesson.progress.responses[Q01];
  const storedQ2 = lesson.progress.responses[Q02];
  const [q1, setQ1] = useState(storedQ1?.selected_option ?? "");
  const [q2, setQ2] = useState(storedQ2?.selected_option ?? "");
  const [feedback, setFeedback] = useState<Record<string, string>>({
    ...(storedQ1 ? { [Q01]: storedQ1.selected_option === "yes" ? "counting_is_not_enough" : "need_new_numbers" } : {}),
    ...(storedQ2 ? {
      [Q02]: storedQ2.selected_option === "bread"
        ? "sharing_needs_fractions"
        : `${storedQ2.selected_option}_needs_integers`,
    } : {}),
  });
  const [challenge, setChallenge] = useState<Record<string, string>>({});
  const [challengeChecked, setChallengeChecked] = useState(false);

  const interactionMutation = useMutation({
    mutationFn: ({ interactionId, option }: { interactionId: string; option: string }) =>
      studentApi.lessonInteraction(courseId, lesson.node_id, interactionId, option),
    onSuccess: (result: LessonInteractionResult) => {
      if (result.interaction_id === Q01) setQ1(result.selected_option);
      if (result.interaction_id === Q02) setQ2(result.selected_option);
      setFeedback((current) => ({
        ...current,
        [result.interaction_id]: result.feedback_key,
      }));
    },
  });

  const situations = ["advance", "bread", "debt"] as const;
  const challengeCorrect =
    challenge.advance === "integers" &&
    challenge.bread === "rationals" &&
    challenge.debt === "integers";

  return (
    <article className="lesson-page trigger-page" aria-labelledby="lesson-title">
      <header className="lesson-topbar">
        <button className="lesson-back" onClick={onBack}>{t("prealgebra.backToMap")}</button>
        <span className="lesson-safe">{t("prealgebra.safeZone")}</span>
      </header>

      <div className="lesson-shell trigger-shell">
        <header className="trigger-heading">
          <span className="lesson-kicker">{t("prealgebra.n1.b02.kicker")}</span>
          <h1 id="lesson-title">{t("prealgebra.n1.b02.title")}</h1>
          <p>{t(`prealgebra.n1.b02.intro.${lesson.presentation}`)}</p>
        </header>

        <KatiaStorySlot
          eyebrow={t("prealgebra.n1.b02.story.katiaEyebrow")}
          title={t("prealgebra.n1.b02.story.katiaTitle")}
          body={t("prealgebra.n1.b02.story.katiaBody")}
          question={t("prealgebra.n1.b02.story.katiaQuestion")}
          imageSrc="/leccion/01-prealg-n1-agora/b02-pregunta-detonadora-v4.png"
          imageAlt={t("prealgebra.n1.b02.story.katiaImageAlt")}
        />

        <section className="situation-grid" aria-label={t("prealgebra.n1.b02.situationsLabel")}>
          {situations.map((key) => (
            <article className={`situation-card situation-${key}`} key={key}>
              <span>{t(`prealgebra.n1.b02.situations.${key}.eyebrow`)}</span>
              <h2>{t(`prealgebra.n1.b02.situations.${key}.title`)}</h2>
              <div className="situation-math" aria-label={t(`prealgebra.n1.b02.situations.${key}.aria`)}>
                <MathFormula math={
                  key === "advance"
                    ? String.raw`0-3=?`
                    : key === "bread"
                      ? String.raw`1\div4=?`
                      : String.raw`5-2=?`
                } />
              </div>
              <p>{t(`prealgebra.n1.b02.situations.${key}.body`)}</p>
            </article>
          ))}
        </section>

        <section className="trigger-question" aria-labelledby="q01-title">
          <span className="question-number">01</span>
          <div>
            <h2 id="q01-title">{t("prealgebra.n1.b02.q01.prompt")}</h2>
            <div className="choice-row">
              {(["yes", "no"] as const).map((option) => (
                <button
                  key={option}
                  className={q1 === option ? "selected" : ""}
                  disabled={Boolean(q1) || interactionMutation.isPending}
                  onClick={() => interactionMutation.mutate({ interactionId: Q01, option })}
                  aria-pressed={q1 === option}
                >
                  {t(`prealgebra.n1.b02.q01.options.${option}`)}
                </button>
              ))}
            </div>
            {feedback[Q01] && (
              <p className="trigger-feedback" role="status">
                {t(`prealgebra.n1.b02.feedback.${feedback[Q01]}`)}
              </p>
            )}
          </div>
        </section>

        {q1 && (
          <section className="trigger-question" aria-labelledby="q02-title">
            <span className="question-number">02</span>
            <div>
              <h2 id="q02-title">{t("prealgebra.n1.b02.q02.prompt")}</h2>
              <div className="choice-stack">
                {situations.map((option) => (
                  <button
                    key={option}
                    className={q2 === option ? "selected" : ""}
                    disabled={Boolean(q2) || interactionMutation.isPending}
                    onClick={() => interactionMutation.mutate({ interactionId: Q02, option })}
                    aria-pressed={q2 === option}
                  >
                    {t(`prealgebra.n1.b02.q02.options.${option}`)}
                  </button>
                ))}
              </div>
              {feedback[Q02] && (
                <p className="trigger-feedback teal" role="status">
                  {t(`prealgebra.n1.b02.feedback.${feedback[Q02]}`)}
                </p>
              )}
            </div>
          </section>
        )}

        {q2 && lesson.presentation === "avanzado" && (
          <section className="trigger-challenge">
            <span>{t("prealgebra.n1.b02.challenge.eyebrow")}</span>
            <h2>{t("prealgebra.n1.b02.challenge.title")}</h2>
            <div className="challenge-grid">
              {situations.map((key) => (
                <label key={key}>
                  {t(`prealgebra.n1.b02.q02.options.${key}`)}
                  <select
                    value={challenge[key] ?? ""}
                    disabled={challengeChecked}
                    onChange={(event) => setChallenge((current) => ({ ...current, [key]: event.target.value }))}
                  >
                    <option value="">{t("prealgebra.n1.b02.challenge.choose")}</option>
                    <option value="integers">{t("prealgebra.n1.b02.challenge.integers")}</option>
                    <option value="rationals">{t("prealgebra.n1.b02.challenge.rationals")}</option>
                  </select>
                </label>
              ))}
            </div>
            {!challengeChecked ? (
              <Button
                variant="secondary"
                disabled={Object.keys(challenge).length < 3}
                onClick={() => setChallengeChecked(true)}
              >
                {t("prealgebra.n1.b02.challenge.check")}
              </Button>
            ) : (
              <p className="trigger-feedback" role="status">
                {t(`prealgebra.n1.b02.challenge.${challengeCorrect ? "correct" : "review"}`)}
              </p>
            )}
          </section>
        )}

        <footer className="lesson-footer trigger-footer">
          <div>
            <span>{t("prealgebra.n1.b02.footerLabel")}</span>
            <p>{t("prealgebra.n1.b02.footerBody")}</p>
          </div>
          <Button
            size="lg"
            disabled={!q1 || !q2}
            loading={finishing}
            onClick={onFinish}
          >
            {lesson.state === "completed"
              ? t("prealgebra.backToMap")
              : t("prealgebra.n1.b02.finish")}
          </Button>
        </footer>
      </div>
    </article>
  );
}
