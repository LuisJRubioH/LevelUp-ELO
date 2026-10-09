/**
 * Bloques compartidos de la arquitectura de 11 bloques.
 *
 * Los 4 niveles (N1–N4) consumen ESTOS componentes: se implementan una vez, no
 * cuatro. Leen props desde `lesson.content` (dict del dominio), no claves i18n,
 * porque N2–N4 ya son data-driven (V2-R12/R13/R14).
 *
 * Contrato de claves: .claude/skills/levelup-node-author/references/implementation-mapping.md
 */
import { useState, type ReactNode } from "react";
import { useMutation } from "@tanstack/react-query";
import { studentApi } from "../../../../api/student";
import { MathFormula, MathText } from "../../../../components/Math/MathContent";
import { Button } from "../../../../components/ui/Button";
import "./lessonBlocks.css";

// ─── Zonas de color ────────────────────────────────────────────────────────
// Cinco zonas funcionales en UNA sola ventana. El riel de color es el único
// portador de zona: el cuerpo del texto no cambia de color (contraste AA igual
// en las cinco). `trap` es exclusivo — no usarlo para respuestas incorrectas.

export type Zone = "explore" | "build" | "trap" | "work" | "close";

export function LessonZone({
  zone,
  label,
  children,
  ariaLabel,
}: {
  zone: Zone;
  label: string;
  children: ReactNode;
  ariaLabel?: string;
}) {
  return (
    <section className={`lesson-zone zone-${zone}`} aria-label={ariaLabel ?? label}>
      <span className="lesson-zone-rail" aria-hidden="true" />
      <span className="lesson-zone-eyebrow">{label}</span>
      <div className="lesson-zone-body">{children}</div>
    </section>
  );
}

// ─── Motor de respuestas compartido ────────────────────────────────────────

export type ItemOption = { id: string; text?: string; latex?: string };
export type LessonItem = {
  id: string;
  kind: "numeric" | "text_exact" | "single_select" | "multi_select";
  prompt: string;
  expr?: string;
  answer?: string;
  options?: ItemOption[];
  expected?: string;
  hints?: { n1: string; n2: string; n3: string };
  tipo?: string;
  confidence?: string;
};

type Restored = Record<string, { selected_option: string; is_expected: boolean | null }>;

export function useLessonItems(courseId: string, nodeId: string, restored: Restored) {
  const [answers, setAnswers] = useState<Record<string, string>>(() =>
    Object.fromEntries(Object.entries(restored).map(([id, r]) => [id, r.selected_option])),
  );
  const [correct, setCorrect] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(
      Object.entries(restored).map(([id, r]) => [id, Boolean(r.is_expected)]),
    ),
  );
  const [feedback, setFeedback] = useState<Record<string, string>>({});
  const [attempts, setAttempts] = useState<Record<string, number>>(() =>
    Object.fromEntries(Object.entries(restored).map(([id]) => [id, 1])),
  );
  const [hintLevel, setHintLevel] = useState<Record<string, number>>({});

  const mutation = useMutation({
    mutationFn: ({ id, option }: { id: string; option: string }) =>
      studentApi.lessonInteraction(courseId, nodeId, id, option),
    onSuccess: (r) => {
      setAnswers((c) => ({ ...c, [r.interaction_id]: r.selected_option }));
      setCorrect((c) => ({ ...c, [r.interaction_id]: Boolean(r.is_expected) }));
      setFeedback((c) => ({ ...c, [r.interaction_id]: r.feedback_key }));
      setAttempts((c) => ({ ...c, [r.interaction_id]: (c[r.interaction_id] ?? 0) + 1 }));
    },
  });

  const fullId = (itemId: string) => `${nodeId}-${itemId}`;

  return {
    fullId,
    pending: mutation.isPending,
    answerOf: (itemId: string) => answers[fullId(itemId)],
    isCorrect: (itemId: string) => Boolean(correct[fullId(itemId)]),
    feedbackKey: (itemId: string) => feedback[fullId(itemId)],
    attemptsOf: (itemId: string) => attempts[fullId(itemId)] ?? 0,
    answered: (itemId: string) => Boolean(answers[fullId(itemId)]),
    hintLevelOf: (itemId: string) => hintLevel[itemId] ?? 0,
    revealHint: (itemId: string) =>
      setHintLevel((c) => ({ ...c, [itemId]: Math.min(3, (c[itemId] ?? 0) + 1) })),
    submit: (itemId: string, option: string) =>
      mutation.mutate({ id: fullId(itemId), option }),
  };
}

export type ItemEngine = ReturnType<typeof useLessonItems>;

// ─── Ítem genérico (usado por diagnóstico, práctica y post-diagnóstico) ─────

function NumericField({
  item,
  engine,
  disabled,
}: {
  item: LessonItem;
  engine: ItemEngine;
  disabled: boolean;
}) {
  const [value, setValue] = useState(engine.answerOf(item.id) ?? "");
  const typed = item.kind === "text_exact";
  return (
    <div className="block-numeric">
      <input
        type="text"
        inputMode={typed ? "text" : "decimal"}
        value={value}
        disabled={disabled}
        aria-label={item.prompt}
        placeholder={typed ? "Escribe la expresión (p. ej. 6r+3)" : "Tu respuesta"}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && value.trim()) engine.submit(item.id, value.trim());
        }}
      />
      <Button
        variant="secondary"
        disabled={disabled || !value.trim() || engine.pending}
        onClick={() => engine.submit(item.id, value.trim())}
      >
        Comprobar
      </Button>
    </div>
  );
}

function OptionRow({
  item,
  engine,
  disabled,
}: {
  item: LessonItem;
  engine: ItemEngine;
  disabled: boolean;
}) {
  const chosen = engine.answerOf(item.id);
  return (
    <div className="block-options" role="group" aria-label={item.prompt}>
      {(item.options ?? []).map((option) => (
        <button
          key={option.id}
          type="button"
          className={chosen === option.id ? "selected" : ""}
          disabled={disabled || engine.pending}
          aria-pressed={chosen === option.id}
          aria-label={option.text ?? option.id}
          onClick={() => engine.submit(item.id, option.id)}
        >
          <OptionLabel option={option} />
        </button>
      ))}
    </div>
  );
}

/**
 * Una opción se muestra UNA vez: si trae `latex`, se renderiza la fórmula y el
 * `text` queda solo como etiqueta accesible (lectura vocalizada). Mostrar los
 * dos duplicaba la fracción en pantalla.
 */
function OptionLabel({ option }: { option: ItemOption }) {
  if (option.latex) return <MathFormula math={option.latex} ariaLabel={option.text} />;
  return <MathText text={option.text ?? option.id} />;
}

function HintLadder({ item, engine }: { item: LessonItem; engine: ItemEngine }) {
  if (!item.hints) return null;
  const level = engine.hintLevelOf(item.id);
  const labels = ["Pregunta orientadora", "Pista conceptual", "Paso incompleto"] as const;
  const texts = [item.hints.n1, item.hints.n2, item.hints.n3];
  return (
    <div className="block-hints">
      {texts.slice(0, level).map((text, index) => (
        <p key={index}>
          <span>{labels[index]}</span>
          <MathText text={text} />
        </p>
      ))}
      {level < 3 && (
        <button type="button" className="block-hint-more" onClick={() => engine.revealHint(item.id)}>
          {level === 0 ? "Pedir una pista" : `Pista ${level + 1} de 3`}
        </button>
      )}
    </div>
  );
}

/**
 * Feedback con ACCIÓN: el botón de cierre es la acción requerida, nunca un "OK"
 * (Hattie & Timperley, 2007). Las respuestas incorrectas usan estado neutro —
 * el rojo está reservado a las trampas.
 */
function ItemFeedback({
  item,
  engine,
  feedbackText,
  showConfidenceBadge,
  acknowledgeOnly = false,
}: {
  item: LessonItem;
  engine: ItemEngine;
  feedbackText: (key: string) => string;
  showConfidenceBadge?: boolean;
  /** Diagnóstico: se acusa recibo, no se corrige ni se muestra nota. */
  acknowledgeOnly?: boolean;
}) {
  const key = engine.feedbackKey(item.id);
  if (!key) return null;
  const ok = engine.isCorrect(item.id);
  const usedHints = engine.hintLevelOf(item.id);

  if (acknowledgeOnly) {
    return (
      <div className="block-feedback is-noted" role="status">
        Anotado. Seguimos.
      </div>
    );
  }

  return (
    <div className={`block-feedback ${ok ? "is-ok" : "is-retry"}`} role="status">
      {/* El borde verde o gris es el único signo visual del resultado; el
          símbolo lo dice sin depender del color. */}
      <span className="block-feedback-mark" aria-hidden="true">{ok ? "✓" : "↻"}</span>
      <span className="sr-only">{ok ? "Correcto. " : "Todavía no. "}</span>
      <MathText text={feedbackText(key)} />
      {ok && usedHints > 0 && <small>Resuelto con pista {usedHints}</small>}
      {!ok && showConfidenceBadge && <small>Marcado como trampa: vuelve a leer el enunciado.</small>}
    </div>
  );
}

export function LessonItemCard({
  item,
  index,
  engine,
  feedbackText,
  lockWhenCorrect = true,
  showHints = true,
  acknowledgeOnly = false,
}: {
  item: LessonItem;
  index?: number;
  engine: ItemEngine;
  feedbackText: (key: string) => string;
  lockWhenCorrect?: boolean;
  showHints?: boolean;
  acknowledgeOnly?: boolean;
}) {
  const done = lockWhenCorrect ? engine.isCorrect(item.id) : engine.answered(item.id);
  const isTrap = item.tipo === "trampa";
  return (
    <article className={`block-item ${isTrap ? "block-item-trap" : ""}`}>
      {index !== undefined && <span className="block-item-number">{String(index).padStart(2, "0")}</span>}
      <div>
        {item.tipo && item.tipo !== "estandar" && item.tipo !== "diagnostico" && (
          <span className="block-item-tag">{item.tipo}</span>
        )}
        <h3>
          <MathText text={item.prompt} />
        </h3>
        {item.expr && <MathFormula math={item.expr} display />}
        {isTrap && item.confidence === "fija" && <ConfidenceSlider itemId={item.id} />}
        {item.kind === "numeric" || item.kind === "text_exact" ? (
          <NumericField item={item} engine={engine} disabled={done} />
        ) : (
          <OptionRow item={item} engine={engine} disabled={done} />
        )}
        {showHints && !done && <HintLadder item={item} engine={engine} />}
        <ItemFeedback
          item={item}
          engine={engine}
          feedbackText={feedbackText}
          showConfidenceBadge={isTrap}
          acknowledgeOnly={acknowledgeOnly}
        />
      </div>
    </article>
  );
}

// ─── Bloque 2/10 · Mini-diagnóstico y post-diagnóstico ─────────────────────
// Sin cronómetro, sin nota al terminar, sin la palabra examen. El resultado
// solo distingue "avance" / "sin evidencia de avance": "empeoró" no existe.

export function DiagnosticBlock({
  intro,
  items,
  engine,
  feedbackText,
  outcome,
}: {
  intro: string;
  items: LessonItem[];
  engine: ItemEngine;
  feedbackText: (key: string) => string;
  outcome?: string | null;
}) {
  return (
    <div className="block-diagnostic">
      <p className="block-lead"><MathText text={intro} /></p>
      {items.map((item) => (
        <LessonItemCard
          key={item.id}
          item={item}
          engine={engine}
          feedbackText={feedbackText}
          // Línea base: se responde una vez y no se corrige. Reintentar la
          // contaminaría, y corregir aquí convertiría el bloque en examen.
          lockWhenCorrect={false}
          showHints={false}
          acknowledgeOnly
        />
      ))}
      {outcome && <p className="block-outcome"><MathText text={outcome} /></p>}
    </div>
  );
}

// ─── Bloque 3 · Intento genuino ────────────────────────────────────────────
// Obligatorio pero NUNCA calificado, y no viaja al backend: cualquier intento
// vale y el sistema responde "veámoslo" (Sinha & Kapur, 2021).

export function GenuineAttempt({
  attempt,
  onAttempted,
}: {
  attempt: {
    prompt: string;
    options: ItemOption[];
    response: string;
  };
  onAttempted: () => void;
}) {
  const [chosen, setChosen] = useState<string | null>(null);
  return (
    <div className="block-attempt">
      <p className="block-lead"><MathText text={attempt.prompt} /></p>
      <div className="block-options" role="group" aria-label={attempt.prompt}>
        {attempt.options.map((option) => (
          <button
            key={option.id}
            type="button"
            className={chosen === option.id ? "selected" : ""}
            aria-pressed={chosen === option.id}
            aria-label={option.text ?? option.latex}
            onClick={() => {
              setChosen(option.id);
              onAttempted();
            }}
          >
            <OptionLabel option={option} />
          </button>
        ))}
      </div>
      {chosen && (
        <p className="block-attempt-response" role="status" aria-live="polite">
          <MathText text={attempt.response} />
        </p>
      )}
    </div>
  );
}

// ─── Bloque 5 · Ejemplos resueltos, autoexplicación y trampa ────────────────

/** Pasos revelados al tocar (segmentación; obligatorio en móvil). */
export function WorkedExample({
  example,
  faded = 0,
}: {
  example: {
    eyebrow?: string;
    title?: string;
    statement?: string;
    latex?: string;
    steps?: string[];
    solution?: string;
    self_explanation?: { step_index: number; prompt: string };
  };
  faded?: number;
}) {
  const total = example.steps?.length ?? 0;
  const [shown, setShown] = useState(1);
  const [explanation, setExplanation] = useState("");
  return (
    <article className="block-example">
      {example.eyebrow && <span>{example.eyebrow}</span>}
      {example.title && <h3><MathText text={example.title} /></h3>}
      {example.statement && <p><MathText text={example.statement} /></p>}
      {example.latex && <MathFormula math={example.latex} display />}
      <ol className="block-example-steps">
        {(example.steps ?? []).slice(0, shown).map((step, index) => {
          const hidden = index >= total - faded;
          return (
            <li key={index}>
              {hidden ? <em className="block-step-faded">Complétalo tú</em> : <MathText text={step} />}
              {example.self_explanation?.step_index === index && (
                <div className="block-self-explanation">
                  <label htmlFor={`se-${example.title ?? index}`}>
                    <MathText text={example.self_explanation.prompt} />
                  </label>
                  {/* Local: no se persiste texto libre del estudiante. */}
                  <textarea
                    id={`se-${example.title ?? index}`}
                    rows={2}
                    value={explanation}
                    onChange={(e) => setExplanation(e.target.value)}
                    placeholder="En una frase"
                  />
                </div>
              )}
            </li>
          );
        })}
      </ol>
      {shown < total && (
        <button type="button" className="block-step-more" onClick={() => setShown((s) => s + 1)}>
          Ver el siguiente paso ({shown} / {total})
        </button>
      )}
      {shown >= total && example.solution && (
        <p className="block-example-solution">
          <MathText text={example.solution} />
        </p>
      )}
    </article>
  );
}

function ConfidenceSlider({ itemId }: { itemId: string }) {
  const [value, setValue] = useState(50);
  const [locked, setLocked] = useState(false);
  return (
    <div className="block-confidence">
      <label htmlFor={`conf-${itemId}`}>¿Qué tan seguro estás de dónde falla?</label>
      <input
        id={`conf-${itemId}`}
        type="range"
        min={0}
        max={100}
        step={5}
        value={value}
        disabled={locked}
        onChange={(e) => setValue(Number(e.target.value))}
      />
      <output aria-live="polite">{value}%</output>
      {!locked && (
        <Button variant="secondary" onClick={() => setLocked(true)}>
          Fijar y continuar
        </Button>
      )}
    </div>
  );
}

/**
 * Tarjeta de trampa: calibración de confianza ANTES de revelar (hipercorrección,
 * Metcalfe 2017) → error señalizado → contraste con la versión correcta a un
 * toque (Durkin & Rittle-Johnson, 2012) → explica-y-corrige.
 */
export function TrapExample({
  example,
}: {
  example: {
    eyebrow?: string;
    title?: string;
    statement?: string;
    latex?: string;
    confidence_prompt?: string;
    error_latex?: string;
    error_note?: string;
    correct_version?: {
      wrong_latex: string;
      right_latex: string;
      rows: Array<{ wrong: string; right: string }>;
    };
    explain_prompt?: string;
    steps?: string[];
    solution?: string;
  };
}) {
  const [confidence, setConfidence] = useState(50);
  const [calibrated, setCalibrated] = useState(false);
  const [showContrast, setShowContrast] = useState(false);
  const [explanation, setExplanation] = useState("");
  const [explained, setExplained] = useState(false);

  // La trampa es una secuencia de 3 pasos, no un bloque que se abre solo: se
  // numeran para que se vea qué falta hacer y qué desbloquea cada paso.
  const stepClass = (done: boolean, active: boolean) =>
    `block-trap-step ${done ? "is-done" : ""} ${active ? "is-active" : ""}`.trim();

  return (
    <article className="block-trap">
      <header>
        <span aria-hidden="true">⚠</span>
        <div>
          <span>{example.eyebrow ?? "Trampa común"}</span>
          {example.title && <h3><MathText text={example.title} /></h3>}
        </div>
      </header>
      {example.statement && <p><MathText text={example.statement} /></p>}
      {example.latex && <MathFormula math={example.latex} display />}

      {/* Paso 1 · calibración de confianza, obligatoria antes de revelar */}
      <section className={stepClass(calibrated, !calibrated)}>
        <h4>
          <span aria-hidden="true">1</span> Antes de mirar: ¿cuánto crees saber dónde falla?
        </h4>
        <div className="block-confidence">
          <label htmlFor="trap-confidence">
            <MathText text={example.confidence_prompt ?? "¿Qué tan seguro estás de dónde falla?"} />
          </label>
          <input
            id="trap-confidence"
            type="range"
            min={0}
            max={100}
            step={5}
            value={confidence}
            disabled={calibrated}
            onChange={(e) => setConfidence(Number(e.target.value))}
          />
          <output aria-live="polite">{confidence}%</output>
          {!calibrated && (
            <Button variant="secondary" onClick={() => setCalibrated(true)}>
              Fijar y ver dónde falla
            </Button>
          )}
        </div>
      </section>

      {/* Paso 2 · el error señalizado + contraste con la versión correcta */}
      {calibrated && (
        <section className={stepClass(showContrast, !showContrast)}>
          <h4>
            <span aria-hidden="true">2</span> Aquí falla
          </h4>
          {example.error_latex && (
            <div className="block-trap-signal">
              <MathFormula math={example.error_latex} display />
              {example.error_note && <p><MathText text={example.error_note} /></p>}
            </div>
          )}
          <button
            type="button"
            className="block-trap-toggle"
            aria-expanded={showContrast}
            onClick={() => setShowContrast((s) => !s)}
          >
            {showContrast ? "Ocultar la versión correcta" : "Comparar con la versión correcta"}
          </button>
          {showContrast && example.correct_version && (
            <div className="block-trap-contrast">
              <div className="wrong">
                <span>❌ Lo que escribió</span>
                <MathFormula math={example.correct_version.wrong_latex} display />
              </div>
              <div className="right">
                <span>✅ Lo correcto</span>
                <MathFormula math={example.correct_version.right_latex} display />
              </div>
              <ul>
                {example.correct_version.rows.map((row, index) => (
                  <li key={index}>
                    <span><MathText text={row.wrong} /></span>
                    <span><MathText text={row.right} /></span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {/* Paso 3 · explica-y-corrige. Se guarda en el navegador, no se envía:
          el nodo no persiste texto libre del estudiante. */}
      {showContrast && example.explain_prompt && (
        <section className={stepClass(explained, !explained)}>
          <h4>
            <span aria-hidden="true">3</span> Ahora explícalo tú
          </h4>
          <div className="block-self-explanation">
            <label htmlFor="trap-explain"><MathText text={example.explain_prompt} /></label>
            <textarea
              id="trap-explain"
              rows={2}
              value={explanation}
              disabled={explained}
              onChange={(e) => setExplanation(e.target.value)}
              placeholder="Por qué falla + la igualdad corregida"
            />
            {!explained && (
              <Button
                variant="secondary"
                disabled={explanation.trim().length < 10}
                onClick={() => setExplained(true)}
              >
                Enviar mi explicación
              </Button>
            )}
            {!explained && explanation.trim().length < 10 && (
              <small className="block-trap-hint">
                Escribe al menos una frase para poder comparar con la de KatIA.
              </small>
            )}
          </div>
          {explained && example.solution && (
            <div className="block-trap-resolution">
              <span>Lo que dice KatIA</span>
              <p><MathText text={example.solution} /></p>
            </div>
          )}
        </section>
      )}
    </article>
  );
}

// ─── Bloque 6 · Puente (parcialmente resueltos) ────────────────────────────
// Huecos editables dentro del procedimiento. El andamiaje sube o baja en
// silencio: no se anuncia ningún cambio de nivel.

export function BridgeBlock({
  bridge,
  engine,
  feedbackText,
  presentation,
}: {
  bridge: {
    intro: string;
    items: Array<{
      id: string;
      statement: string;
      given_steps: string[];
      presentation?: string;
      blanks: Array<{ id: string; label: string; answer: string }>;
    }>;
  };
  engine: ItemEngine;
  feedbackText: (key: string) => string;
  presentation: string;
}) {
  const visible = bridge.items.filter(
    (item) => !item.presentation || item.presentation === presentation,
  );
  return (
    <div className="block-bridge">
      <p className="block-lead"><MathText text={bridge.intro} /></p>
      {visible.map((item) => (
        <article key={item.id} className="block-bridge-item">
          <p><MathText text={item.statement} /></p>
          <ol>
            {item.given_steps.map((step, index) => (
              <li key={index}>
                <MathFormula math={step} />
              </li>
            ))}
            {item.blanks.map((blank) => (
              <li key={blank.id} className="block-bridge-blank">
                <MathFormula math={blank.label} />
                <NumericField
                  item={{ id: blank.id, kind: "numeric", prompt: blank.label }}
                  engine={engine}
                  disabled={engine.isCorrect(blank.id)}
                />
                {engine.feedbackKey(blank.id) && (
                  <span
                    className={`block-bridge-mark ${engine.isCorrect(blank.id) ? "is-ok" : "is-retry"}`}
                    role="status"
                  >
                    {engine.isCorrect(blank.id) ? (
                      <>
                        <span aria-hidden="true">✓</span>
                        <span className="sr-only">correcto</span>
                      </>
                    ) : (
                      feedbackText(engine.feedbackKey(blank.id))
                    )}
                  </span>
                )}
              </li>
            ))}
          </ol>
        </article>
      ))}
    </div>
  );
}

// ─── Bloque 7 · Comparación de métodos ─────────────────────────────────────
// Solo si el tema admite dos métodos válidos, y SIEMPRE después del puente
// (Rittle-Johnson, Star & Durkin, 2009).

export function MethodComparison({
  comparison,
}: {
  comparison: {
    title: string;
    intro: string;
    methods: Array<{ label: string; steps: string[]; note?: string }>;
    question: string;
    insight?: string;
  };
}) {
  const [revealed, setRevealed] = useState(false);
  return (
    <div className="block-methods">
      <h3><MathText text={comparison.title} /></h3>
      <p className="block-lead">
        <MathText text={comparison.intro} />
      </p>
      <div className="block-methods-grid">
        {comparison.methods.map((method) => (
          <article key={method.label}>
            <span>
              <MathText text={method.label} />
            </span>
            <ol>
              {method.steps.map((step, index) => (
                <li key={index}>
                  <MathFormula math={step} />
                </li>
              ))}
            </ol>
            {method.note && <p><MathText text={method.note} /></p>}
          </article>
        ))}
      </div>
      <blockquote><MathText text={comparison.question} /></blockquote>
      {comparison.insight &&
        (revealed ? (
          <p className="block-methods-insight"><MathText text={comparison.insight} /></p>
        ) : (
          <button type="button" className="block-step-more" onClick={() => setRevealed(true)}>
            Ver la respuesta
          </button>
        ))}
    </div>
  );
}

// ─── Bloque 9 · Abstracción + cierre con Pólya ─────────────────────────────

export function AbstractionQuestion({
  question,
}: {
  question: {
    prompt: string;
    thumbnails: string[];
    options: Array<{ id: string; text: string; correct: boolean }>;
  };
}) {
  const [picked, setPicked] = useState<Set<string>>(new Set());
  const [checked, setChecked] = useState(false);
  const toggle = (id: string) =>
    setPicked((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  return (
    <div className="block-abstraction">
      <h3><MathText text={question.prompt} /></h3>
      <div className="block-thumbnails" aria-hidden="true">
        {question.thumbnails.map((math) => (
          <MathFormula key={math} math={math} display />
        ))}
      </div>
      <div className="block-options block-options-column" role="group" aria-label={question.prompt}>
        {question.options.map((option) => (
          <button
            key={option.id}
            type="button"
            className={[
              picked.has(option.id) ? "selected" : "",
              checked ? (option.correct ? "is-ok" : "is-off") : "",
            ]
              .filter(Boolean)
              .join(" ")}
            aria-pressed={picked.has(option.id)}
            disabled={checked}
            onClick={() => toggle(option.id)}
          >
            <MathText text={option.text} />
          </button>
        ))}
      </div>
      {!checked && (
        <Button variant="secondary" disabled={picked.size === 0} onClick={() => setChecked(true)}>
          Comprobar
        </Button>
      )}
    </div>
  );
}

export function PolyaClosing({
  item,
  engine,
  feedbackText,
}: {
  item: {
    id: string;
    statement: string;
    prompt?: string;
    polya: { comprender: string; planear: string; ejecutar: string; comprobar: string };
    answer: string;
    hints?: { n1: string; n2: string; n3: string };
  };
  engine: ItemEngine;
  feedbackText: (key: string) => string;
}) {
  const [step, setStep] = useState(0);
  const micro = [
    ["Comprender", item.polya.comprender],
    ["Planear", item.polya.planear],
    ["Ejecutar", item.polya.ejecutar],
    ["Comprobar", item.polya.comprobar],
  ] as const;
  return (
    <div className="block-polya">
      <p className="block-lead"><MathText text={item.statement} /></p>
      <ol className="block-polya-steps">
        {micro.slice(0, step).map(([label, text]) => (
          <li key={label}>
            <span>{label}</span>
            <MathText text={text} />
          </li>
        ))}
      </ol>
      {step < micro.length ? (
        <button type="button" className="block-step-more" onClick={() => setStep((s) => s + 1)}>
          {step === 0 ? "Empezar por comprender" : `Siguiente: ${micro[step][0]}`}
        </button>
      ) : (
        <LessonItemCard
          item={{
            id: item.id,
            kind: "numeric",
            prompt: item.prompt ?? "¿Cuál es el resultado?",
            hints: item.hints,
          }}
          engine={engine}
          feedbackText={feedbackText}
        />
      )}
    </div>
  );
}

// ─── Bloque 11 · Footer con estado de dominio ──────────────────────────────
// Nunca porcentaje de lectura ni check de completado. "Correcto con ayuda" no
// es dominio (VanLehn, 2011).

export function MasteryFooter({
  footer,
  state,
  children,
}: {
  footer: { label: string; states: Record<string, string>; note?: string };
  state: "sin_ayuda" | "consolidacion" | "repasar";
  children: ReactNode;
}) {
  return (
    <footer className="block-footer">
      <div>
        <span>{footer.label}</span>
        <p className={`block-mastery is-${state}`}>{footer.states[state]}</p>
        {footer.note && <small><MathText text={footer.note} /></small>}
      </div>
      {children}
    </footer>
  );
}
