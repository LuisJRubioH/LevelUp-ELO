import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi } from "./helpers/auth";
import type { Page } from "@playwright/test";

/**
 * Eleven-block lessons (V2-R11): a multi_select practice item is graded on the whole selection
 * ("a,c"). Tapping an option used to send that one option, so an item with two or more right
 * answers could never be correct and the node could never be finished (31 of the 52 nodes).
 */
const COURSE = "algebra_basica";
const NODE = "ALG-N1-O01-SEMEJANTES";
const LESSON_URL = `**/api/student/lessons/${COURSE}/${NODE}`;

function lesson(responses: Record<string, unknown> = {}) {
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
    progress: {
      state: "current",
      objectives_viewed: false,
      math_convention_viewed: false,
      viewed_at: null,
      completed_at: null,
      responses,
    },
    content: {
      kind: "eleven_block_node",
      title: "La rampa",
      intro: "Términos semejantes.",
      katia: {
        eyebrow: "KatIA",
        title: "Antes de empezar",
        body: "Mira los bloques.",
        question: "¿Cuáles se pueden juntar?",
        attempt: {
          prompt: "Intenta antes de leer.",
          options: [{ id: "x", text: "Los de la misma letra" }],
          response: "Lo vemos enseguida.",
        },
      },
      discovery: { eyebrow: "Descubre", title: "Juntar", body: "…", cases: [], resolution: "…" },
      definition_title: "Términos semejantes",
      definition_katex: "5m + 2m = 7m",
      definition_symbols: [],
      definition: "Misma parte literal.",
      practice: [
        {
          id: "E6",
          kind: "multi_select",
          tipo: "estandar",
          prompt: "Selecciona TODOS los pares de términos que SÍ son semejantes.",
          options: [
            { id: "a", text: "5m y -2m" },
            { id: "b", text: "3k² y 7k" },
            { id: "c", text: "4ab y 9ba" },
            { id: "d", text: "6p y 6q" },
          ],
        },
      ],
      feedback: { correct: "Exacto: misma parte literal.", default: "Revisa la parte literal." },
      footer: { label: "Dominio", states: { sin_ayuda: "Sin ayuda", consolidacion: "Con ayuda", repasar: "Repasar" } },
      finish_label: "Terminar el nodo",
    },
  };
}

async function openLesson(page: Page, responses: Record<string, unknown> = {}) {
  const sent: string[] = [];
  await page.route(LESSON_URL, (route) => route.fulfill({ json: lesson(responses) }));
  await page.route(`${LESSON_URL}/events`, (route) => route.fulfill({ json: lesson(responses) }));
  await page.route(`${LESSON_URL}/interactions`, async (route) => {
    const { interaction_id, selected_option } = route.request().postDataJSON();
    sent.push(selected_option);
    const ok = selected_option === "a,c";
    await route.fulfill({
      json: {
        interaction_id,
        selected_option,
        is_expected: ok,
        misconception_tag: ok ? null : "combina_no_semejantes",
        feedback_key: ok ? "correct" : "default",
      },
    });
  });
  await mockStudentApi(page);
  await injectAuth(page);
  await page.goto(`/student/course/${COURSE}/lesson/${NODE}`);
  return sent;
}

const option = (page: Page, name: string) =>
  page.getByRole("group", { name: /Selecciona TODOS/ }).getByRole("button", { name, exact: true });

test.describe("Lección de 11 bloques — pregunta de varias respuestas", () => {
  test("marcar no envía nada; comprobar envía la selección completa y el nodo se puede terminar", async ({ page }) => {
    const sent = await openLesson(page);
    await page.getByRole("button", { name: "Los de la misma letra" }).click();
    const finish = page.getByRole("button", { name: "Terminar el nodo" });

    await option(page, "5m y -2m").click();
    await option(page, "4ab y 9ba").click();
    await expect(option(page, "5m y -2m")).toHaveAttribute("aria-pressed", "true");
    await expect(option(page, "4ab y 9ba")).toHaveAttribute("aria-pressed", "true");
    expect(sent).toEqual([]);
    await expect(finish).toBeDisabled();

    await page.getByRole("button", { name: "Comprobar" }).click();

    await expect(page.getByText("Exacto: misma parte literal.")).toBeVisible();
    expect(sent).toEqual(["a,c"]);
    await expect(option(page, "5m y -2m")).toBeDisabled();
    await expect(finish).toBeEnabled();
  });

  test("una opción se desmarca con un segundo toque y un intento fallido se puede corregir", async ({ page }) => {
    const sent = await openLesson(page);

    await option(page, "3k² y 7k").click();
    await option(page, "5m y -2m").click();
    await page.getByRole("button", { name: "Comprobar" }).click();
    await expect(page.getByText("Revisa la parte literal.")).toBeVisible();

    await option(page, "3k² y 7k").click();
    await expect(option(page, "3k² y 7k")).toHaveAttribute("aria-pressed", "false");
    await option(page, "4ab y 9ba").click();
    await page.getByRole("button", { name: "Comprobar" }).click();

    await expect(page.getByText("Exacto: misma parte literal.")).toBeVisible();
    expect(sent).toEqual(["a,b", "a,c"]);
  });

  test("una respuesta guardada vuelve marcada", async ({ page }) => {
    await openLesson(page, {
      [`${NODE}-E6`]: {
        interaction_id: `${NODE}-E6`,
        selected_option: "a,c",
        is_expected: true,
        misconception_tag: null,
      },
    });

    await expect(option(page, "5m y -2m")).toHaveAttribute("aria-pressed", "true");
    await expect(option(page, "4ab y 9ba")).toHaveAttribute("aria-pressed", "true");
    await expect(option(page, "3k² y 7k")).toHaveAttribute("aria-pressed", "false");
    await expect(option(page, "5m y -2m")).toBeDisabled();
  });
});
