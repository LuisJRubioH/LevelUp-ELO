/**
 * Renderer genérico de la arquitectura de 11 bloques.
 *
 * UNA ventana, cinco zonas por color (explorar / construir / trampa / trabajar
 * / cerrar). Todo lo específico del nodo viaja en `lesson.content`: este
 * componente no conoce ningún node_id. Cualquier nodo cuyo contenido declare
 * `kind: "eleven_block_node"` se pinta aquí sin tocar el frontend.
 *
 * Prototipo aprobado: B06 (Racionales).
 * Spec: Implementacion/specs/PREALG-N1-B06-RACIONALES-FRACCION-DIVISION.md
 */
import { useMemo, useState, type CSSProperties } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import type { LessonDetail } from "../../../../api/student";
import { MathFormula, MathText } from "../../../../components/Math/MathContent";
import { Button } from "../../../../components/ui/Button";
import { KatiaStorySlot } from "../KatiaStorySlot";
import { SetNodeScene } from "../SetNodeScene";
import {
  AbstractionQuestion,
  BridgeBlock,
  DiagnosticBlock,
  GenuineAttempt,
  LessonItemCard,
  LessonZone,
  MasteryFooter,
  MethodComparison,
  PolyaClosing,
  TrapExample,
  WorkedExample,
  useLessonItems,
  type LessonItem,
} from "./LessonBlocks";
import "./lessonBlocks.css";

type Props = {
  lesson: LessonDetail;
  courseId: string;
  onBack: () => void;
  onFinish: () => Promise<void>;
  finishing: boolean;
};

// Desvanecimiento del ejemplo resuelto según banda de presentación
// (Sweller & Cooper, 1985). La trampa NO se desvanece en ningún nivel.
type ClosingItem = {
  id: string;
  statement: string;
  prompt?: string;
  polya: { comprender: string; planear: string; ejecutar: string; comprobar: string };
  answer: string;
  hints?: { n1: string; n2: string; n3: string };
};

const FADED_STEPS: Record<string, number> = { basico: 0, intermedio: 2, avanzado: 3 };

// Marcos de los peldaños sobre la ilustración de la escalera. Solo los usa el
// nodo cuyo tema ES la escalera (B03); el resto omite el bloque.
const STAIRCASE_FRAMES = [
  { left: "18%", top: "70.8%", width: "22.8%", height: "8.4%" },
  { left: "22.2%", top: "59.5%", width: "22.4%", height: "8%" },
  { left: "26.4%", top: "48.2%", width: "22%", height: "8%" },
  { left: "30.6%", top: "36.9%", width: "21.6%", height: "8%" },
  { left: "34.8%", top: "25.6%", width: "21.2%", height: "8%" },
];

type StaircaseStep = { name: string; symbol: string; question: string; explanation: string };

/** Explorador de peldaños: la ilustración con sus zonas activas. */
function StaircaseExplorer({
  staircase,
}: {
  staircase: { image: string; aria: string; steps: StaircaseStep[]; chain?: string };
}) {
  const [active, setActive] = useState(0);
  const step = staircase.steps[active];

  return (
    <section className="staircase-layout illustrated" aria-label={staircase.aria}>
      <figure className="staircase-visual-panel">
        <img className="staircase-art" src={staircase.image} alt="" aria-hidden="true" />
        <ol className="staircase-hotspots" aria-label={staircase.aria}>
          {staircase.steps.map((item, index) => (
            <li
              key={item.name}
              style={
                {
                  "--hotspot-left": STAIRCASE_FRAMES[index]?.left,
                  "--hotspot-top": STAIRCASE_FRAMES[index]?.top,
                  "--hotspot-width": STAIRCASE_FRAMES[index]?.width,
                  "--hotspot-height": STAIRCASE_FRAMES[index]?.height,
                } as CSSProperties
              }
            >
              <motion.button
                className={active === index ? "active" : ""}
                onClick={() => setActive(index)}
                aria-pressed={active === index}
                animate={{ scale: active === index ? 1.025 : 1 }}
                transition={{ duration: 0.18, ease: "easeOut" }}
              >
                <span>0{index + 1}</span>
                <b>{item.name}</b>
                <small aria-label={item.name}>
                  <MathFormula math={item.symbol} />
                </small>
              </motion.button>
            </li>
          ))}
        </ol>
      </figure>

      <aside className="step-explanation" aria-live="polite">
        <span>La necesidad que lo creó</span>
        <h2><MathText text={step.question} /></h2>
        <p><MathText text={step.explanation} /></p>
        {staircase.chain && (
          <div className="inclusion-chain">
            <MathFormula math={staircase.chain} />
          </div>
        )}
      </aside>
    </section>
  );
}

/** Un nodo se pinta aquí si su contenido lo declara. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function isElevenBlock(content: any): boolean {
  return content?.kind === "eleven_block_node";
}

export function ElevenBlockLesson({ lesson, courseId, onBack, onFinish, finishing }: Props) {
  const { t } = useTranslation();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const content = lesson.content as any;
  const engine = useLessonItems(courseId, lesson.node_id, lesson.progress.responses);
  const [attempted, setAttempted] = useState(false);

  const feedbackText = useMemo(
    () => (key: string) => content?.feedback?.[key] ?? content?.feedback?.default ?? "",
    [content],
  );

  // El nodo no puede renderizarse con el contenido viejo: si el backend todavía
  // sirve el molde anterior, no inventamos una pantalla a medias.
  if (!isElevenBlock(content)) {
    return (
      <article className="lesson-page eleven-block-page">
        <header className="lesson-topbar">
          <button className="lesson-back" onClick={onBack}>{t("prealgebra.backToMap")}</button>
        </header>
        <div className="lesson-shell">
          <p>Este nodo se está reconstruyendo. Reinicia el backend para cargar el contenido nuevo.</p>
        </div>
      </article>
    );
  }

  const practice: LessonItem[] = content.practice ?? [];
  const [exampleA, exampleB, trap] = content.worked_examples ?? [];
  const faded = FADED_STEPS[lesson.presentation] ?? 0;
  // No es un LessonItem: el cierre de Polya trae `statement` y los cuatro
  // pasos, y no trae `kind` — el motor lo resuelve siempre por respuesta escrita.
  const closingItem: ClosingItem | undefined = content.closing_item;

  const practiceDone = practice.filter((item) => engine.isCorrect(item.id)).length;
  const closingDone = !closingItem || engine.isCorrect(closingItem.id);
  const allResolved = practiceDone === practice.length && closingDone;

  // "Correcto con ayuda" no es dominio (VanLehn, 2011).
  const usedHints = practice.some((item) => engine.hintLevelOf(item.id) > 0);
  const masteryState = !allResolved ? "repasar" : usedHints ? "consolidacion" : "sin_ayuda";

  // Post-diagnóstico: solo "avance" / "sin evidencia de avance". Nunca "empeoró".
  const diagnosticItems: LessonItem[] = content.diagnostic?.items ?? [];
  const diagnosticScore = diagnosticItems.filter((i) => engine.isCorrect(i.id)).length;
  const postItems: LessonItem[] = content.post_diagnostic?.items ?? [];
  const postAnswered = postItems.length > 0 && postItems.every((i) => engine.answered(i.id));
  const postScore = postItems.filter((i) => engine.isCorrect(i.id)).length;
  const postOutcome = !postAnswered
    ? null
    : postScore > diagnosticScore
      ? (content.post_diagnostic.outcome_gain ?? "Avance: hoy resolviste más que al entrar.")
      : (content.post_diagnostic.outcome_flat ??
        "Sin evidencia de avance todavía. KatIA va a retomar contigo lo que quedó suelto.");

  return (
    <article className="lesson-page eleven-block-page" aria-labelledby="lesson-title">
      <header className="lesson-topbar">
        <button className="lesson-back" onClick={onBack}>{t("prealgebra.backToMap")}</button>
        <span className="lesson-safe">{t("prealgebra.safeZone")}</span>
      </header>

      <div className="lesson-shell eleven-block-shell">
        {/* ── Zona 1 · EXPLORAR — bloques 1, 2, 3 ─────────────────────── */}
        <LessonZone zone="explore" label="Explorar">
          <header className="blk-heading">
            {content.kicker && <span className="lesson-kicker">{content.kicker}</span>}
            <h1 id="lesson-title"><MathText text={content.title} /></h1>
            <p><MathText text={content.intro} /></p>
          </header>

          {content.scene && (
            <SetNodeScene
              imageSrc={content.scene.image}
              activeStep={content.scene.step}
              ariaLabel={content.scene.aria}
            />
          )}

          {content.staircase && <StaircaseExplorer staircase={content.staircase} />}

          {content.diagnostic && (
            <DiagnosticBlock
              intro={content.diagnostic.intro}
              items={diagnosticItems}
              engine={engine}
              feedbackText={feedbackText}
            />
          )}

          {content.katia && (
            <KatiaStorySlot
              eyebrow={content.katia.eyebrow}
              title={content.katia.title}
              body={content.katia.body}
              question={content.katia.question}
              imageSrc={content.katia.image}
            />
          )}

          {content.katia?.attempt && (
            <GenuineAttempt attempt={content.katia.attempt} onAttempted={() => setAttempted(true)} />
          )}
        </LessonZone>

        {/* ── Zona 2 · CONSTRUIR — bloques 4, 5a, 5b ──────────────────── */}
        <LessonZone zone="build" label="Construir">
          <section className="set-story">
            <article>
              <span>{content.discovery.eyebrow}</span>
              <h2><MathText text={content.discovery.title} /></h2>
              <p><MathText text={content.discovery.body} /></p>
              <div className="blk-cases">
                {content.discovery.cases.map((c: Record<string, string>) => (
                  <div key={c.label}>
                    <span>{c.label}</span>
                    <p><MathText text={c.context} /></p>
                    {c.fraction && <MathFormula math={c.fraction} display />}
                    {c.division && <MathFormula math={c.division} />}
                    <small><MathText text={c.note} /></small>
                  </div>
                ))}
              </div>
              <p className="blk-resolution"><MathText text={content.discovery.resolution} /></p>
            </article>

            <article className="set-formal">
              <span>Definición formal</span>
              <h2><MathText text={content.definition_title} /></h2>
              <MathFormula math={content.definition_katex} display />
              <dl className="blk-symbols">
                {(content.definition_symbols ?? []).map((s: Record<string, string>) => (
                  <div key={s.symbol}>
                    <dt>
                      <MathFormula math={s.symbol} ariaLabel={s.reads} />
                    </dt>
                    <dd>
                      <b>{s.reads}</b> — <MathText text={s.means} />
                    </dd>
                  </div>
                ))}
              </dl>
              <p><MathText text={content.definition} /></p>
            </article>
          </section>

          {exampleA && <WorkedExample example={exampleA} faded={faded} />}
          {exampleB && <WorkedExample example={exampleB} faded={faded} />}
        </LessonZone>

        {/* ── Zona 3 · TRAMPA — bloque 5c. Color e icono reservados ───── */}
        {trap && (
          <LessonZone zone="trap" label="⚠ Error" ariaLabel="Trampa común">
            <TrapExample example={trap} />
          </LessonZone>
        )}

        {/* ── Zona 4 · TU TURNO — bloques 6, 7, 8 ─────────────────────── */}
        <LessonZone zone="work" label="Tu turno">
          {content.bridge && (
            <BridgeBlock
              bridge={content.bridge}
              engine={engine}
              feedbackText={feedbackText}
              presentation={lesson.presentation}
            />
          )}

          {content.method_comparison && <MethodComparison comparison={content.method_comparison} />}

          <div className="blk-practice">
            <h2>Práctica</h2>
            {practice.map((item, index) => (
              <LessonItemCard
                key={item.id}
                item={item}
                index={index + 1}
                engine={engine}
                feedbackText={feedbackText}
              />
            ))}
          </div>
        </LessonZone>

        {/* ── Zona 5 · CERRAR — bloques 9, 10, 11 ─────────────────────── */}
        <LessonZone zone="close" label="Cerrar">
          {content.closure && (
            <section className="blk-closure">
              <span>{content.closure.eyebrow}</span>
              <h2><MathText text={content.closure.title} /></h2>
              <p><MathText text={content.closure.intro} /></p>
              <table>
                <tbody>
                  {content.closure.rows.map((row: Record<string, string>) => (
                    <tr key={row.name} className={`is-${row.closed}`}>
                      <th scope="row">
                        <MathFormula math={row.symbol} ariaLabel={row.name} />
                        <small>{row.name}</small>
                      </th>
                      {/* "partial": cierra salvo en un caso concreto, y ese caso
                          es contenido (p. ej. la potencia con exponente 1/2).
                          El símbolo va aparte de la palabra: verde/ámbar/rojo no
                          distingue nada para quien no ve el color. */}
                      <td>
                        <span aria-hidden="true">
                          {{ yes: "✓", partial: "~" }[row.closed] ?? "✗"}
                        </span>
                        <span className="sr-only">
                          {{ yes: "sí", partial: "solo en parte", no: "no" }[row.closed] ?? "no"}
                        </span>
                      </td>
                      <td>{row.latex && <MathFormula math={row.latex} />}</td>
                      <td><MathText text={row.note} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="blk-resolution"><MathText text={content.closure.outro} /></p>
            </section>
          )}

          {content.abstraction_question && (
            <AbstractionQuestion question={content.abstraction_question} />
          )}

          {closingItem && (
            <PolyaClosing item={closingItem} engine={engine} feedbackText={feedbackText} />
          )}

          {content.post_diagnostic && (
            <DiagnosticBlock
              intro={content.post_diagnostic.intro}
              items={postItems}
              engine={engine}
              feedbackText={feedbackText}
              outcome={postOutcome}
            />
          )}

          {content.closing && (
            <p className="blk-resolution">
              <MathText text={content.closing} />
            </p>
          )}
        </LessonZone>

        <MasteryFooter footer={content.footer} state={masteryState}>
          <Button
            size="lg"
            disabled={!allResolved || !attempted}
            loading={finishing}
            onClick={onFinish}
          >
            {lesson.state === "completed"
              ? t("prealgebra.backToMap")
              : (content.finish_label ?? "Terminar el nodo")}
          </Button>
        </MasteryFooter>
      </div>
    </article>
  );
}
