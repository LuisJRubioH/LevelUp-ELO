import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi } from "./helpers/auth";

/**
 * Q13 (AGENTS D5): el mensaje de un hueco del puente («Tu turno») pasa por MathText; una fórmula
 * del mensaje se dibuja, no se imprime con sus signos de dólar.
 */
const COURSE = "algebra_basica";
const NODE = "ALG-N1-O01-SEMEJANTES";
const LESSON_URL = `**/api/student/lessons/${COURSE}/${NODE}`;
const BLANK = "B1";
const BLANK_LABEL = "Parte imaginaria";

function lesson() {
  return {
    node_id: NODE,
    node_type: "concept",
    course_id: COURSE,
    i18n_prefix: "",
    next_node_id: null,
    state: "current",
    presentation: "basico",
    explored_complex_branch: false,
    affects_elo: false,
    is_safe_zone: true,
    optional_branch: false,
    objectives: [],
    optional_objectives: [],
    unlock_after: null,
    interactions: [],
    progress: { state: "current", objectives_viewed: false, math_convention_viewed: false, viewed_at: null, completed_at: null, responses: {} },
    content: {
      kind: "eleven_block_node",
      title: "La rampa",
      intro: "Términos semejantes.",
      katia: {
        eyebrow: "KatIA",
        title: "Antes de empezar",
        body: "Mira los bloques.",
        question: "¿Cuáles se pueden juntar?",
        attempt: { prompt: "Intenta antes de leer.", options: [{ id: "x", text: "Los de la misma letra" }], response: "Lo vemos enseguida." },
      },
      discovery: { eyebrow: "Descubre", title: "Juntar", body: "…", cases: [], resolution: "…" },
      definition_title: "Términos semejantes",
      definition_katex: "5m + 2m = 7m",
      definition_symbols: [],
      definition: "Misma parte literal.",
      bridge: {
        intro: "Completa el procedimiento.",
        items: [
          {
            id: "P1",
            statement: "Separa la parte imaginaria de 3 + 4i.",
            given_steps: ["z = 3 + 4i"],
            blanks: [{ id: BLANK, label: BLANK_LABEL }],
          },
        ],
      },
      practice: [
        {
          id: "E1",
          kind: "numeric",
          tipo: "estandar",
          prompt: "¿Cuánto es 3m + 4m? Escribe el coeficiente.",
          hints: { n1: "Suma los coeficientes.", n2: "3 + 4.", n3: "Es 7." },
        },
      ],
      feedback: {
        correct: "Correcto.",
        default: "Separa las dos partes: la imaginaria es el número que acompaña a $i$. Recuerda que $i^2=-1$.",
      },
      footer: { label: "Dominio", states: { sin_ayuda: "Sin ayuda", consolidacion: "Con ayuda", repasar: "Repasar" } },
      finish_label: "Terminar el nodo",
    },
  };
}

test.describe("Q13 — mensaje de un hueco del puente", () => {
  test("el mensaje de un hueco del puente muestra sus fórmulas, no los signos de dólar", async ({ page }) => {
    await page.route(LESSON_URL, (route) => route.fulfill({ json: lesson() }));
    await page.route(`${LESSON_URL}/events`, (route) => route.fulfill({ json: lesson() }));
    await page.route(`${LESSON_URL}/interactions`, async (route) => {
      const body = route.request().postDataJSON();
      await route.fulfill({
        json: { ...body, is_expected: false, misconception_tag: null, feedback_key: "default" },
      });
    });
    await mockStudentApi(page);
    await injectAuth(page);
    await page.goto(`/student/course/${COURSE}/lesson/${NODE}`);
    await page.getByRole("button", { name: "Los de la misma letra" }).click();

    const blank = page.locator(".block-bridge-blank");
    await blank.getByRole("textbox", { name: BLANK_LABEL }).fill("5");
    await blank.getByRole("textbox", { name: BLANK_LABEL }).press("Enter");

    const mark = blank.locator(".block-bridge-mark");
    await expect(mark).toBeVisible();
    await expect(mark.locator(".katex").first()).toBeVisible();
    await expect(mark).not.toContainText("$");
  });
});
