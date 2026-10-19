import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi } from "./helpers/auth";
import type { Page } from "@playwright/test";

/**
 * Spec 003 L2 (FR-020; N9): the lesson content arrives without grading keys — no `expected`,
 * `answer` or per-option `correct` — and the eleven-block lesson still works end to end. The
 * abstraction question is graded by the server (`<node>-ABSTRACCION`), retried when wrong, and
 * never blocks «Terminar».
 */
const COURSE = "algebra_basica";
const NODE = "ALG-N1-O01-SEMEJANTES";
const LESSON_URL = `**/api/student/lessons/${COURSE}/${NODE}`;
const ABSTRACTION = `${NODE}-ABSTRACCION`;

function lesson(state = "current") {
  return {
    node_id: NODE,
    node_type: "concept",
    course_id: COURSE,
    i18n_prefix: "",
    next_node_id: null,
    state,
    presentation: "basico",
    explored_complex_branch: false,
    affects_elo: false,
    is_safe_zone: true,
    optional_branch: false,
    objectives: [],
    optional_objectives: [],
    unlock_after: null,
    interactions: [],
    progress: { state, objectives_viewed: false, math_convention_viewed: false, viewed_at: null, completed_at: null, responses: {} },
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
      practice: [
        {
          id: "E1",
          kind: "numeric",
          tipo: "estandar",
          prompt: "¿Cuánto es 3m + 4m? Escribe el coeficiente.",
          hints: { n1: "Suma los coeficientes.", n2: "3 + 4.", n3: "Es 7." },
        },
      ],
      abstraction_question: {
        prompt: "¿Qué tienen en común estos pares?",
        thumbnails: ["2a + 3a", "4xy - xy"],
        options: [
          { id: "a", text: "La misma parte literal" },
          { id: "b", text: "El mismo coeficiente" },
          { id: "c", text: "Se pueden sumar en uno solo" },
        ],
      },
      feedback: { correct: "Exacto.", default: "Revisa la parte literal." },
      footer: { label: "Dominio", states: { sin_ayuda: "Sin ayuda", consolidacion: "Con ayuda", repasar: "Repasar" } },
      finish_label: "Terminar el nodo",
    },
  };
}

async function openLesson(page: Page) {
  const sent: Array<{ interaction_id: string; selected_option: string }> = [];
  const events: string[] = [];
  await page.route(LESSON_URL, (route) => route.fulfill({ json: lesson() }));
  await page.route(`${LESSON_URL}/events`, async (route) => {
    const { event } = route.request().postDataJSON();
    events.push(event);
    await route.fulfill({ json: lesson(event === "node_completed" ? "completed" : "current") });
  });
  await page.route(`${LESSON_URL}/interactions`, async (route) => {
    const body = route.request().postDataJSON();
    sent.push(body);
    const ok =
      body.interaction_id === ABSTRACTION ? body.selected_option === "a,c" : body.selected_option === "7";
    await route.fulfill({
      json: { ...body, is_expected: ok, misconception_tag: null, feedback_key: ok ? "correct" : "default" },
    });
  });
  await mockStudentApi(page);
  await injectAuth(page);
  await page.goto(`/student/course/${COURSE}/lesson/${NODE}`);
  return { sent, events };
}

test.describe("Spec 003 L2 — lección sin claves de respuesta", () => {
  test("la pregunta de abstracción la califica el servidor, se reintenta y no bloquea el cierre", async ({ page }) => {
    const { sent, events } = await openLesson(page);
    await page.getByRole("button", { name: "Los de la misma letra" }).click();

    const block = page.locator(".block-abstraction");
    const group = block.getByRole("group", { name: "¿Qué tienen en común estos pares?" });
    await group.getByRole("button", { name: "El mismo coeficiente" }).click();
    await block.getByRole("button", { name: "Comprobar" }).click();
    await expect(block.getByText("Revisa la parte literal.")).toBeVisible();

    await group.getByRole("button", { name: "El mismo coeficiente" }).click();
    await group.getByRole("button", { name: "La misma parte literal" }).click();
    await group.getByRole("button", { name: "Se pueden sumar en uno solo" }).click();
    await block.getByRole("button", { name: "Comprobar" }).click();
    await expect(group.getByRole("button", { name: "La misma parte literal" })).toBeDisabled();
    expect(sent.map((s) => [s.interaction_id, s.selected_option])).toEqual([
      [ABSTRACTION, "b"],
      [ABSTRACTION, "a,c"],
    ]);

    const finish = page.getByRole("button", { name: "Terminar el nodo" });
    await expect(finish).toBeDisabled();
    await page.getByRole("textbox", { name: /3m \+ 4m/ }).fill("7");
    await page.getByRole("textbox", { name: /3m \+ 4m/ }).press("Enter");
    await expect(finish).toBeEnabled();
    await finish.click();
    await expect.poll(() => events).toContain("node_completed");
  });
});
