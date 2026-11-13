import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi } from "./helpers/auth";
import type { Page } from "@playwright/test";

/**
 * Spec 003 L6 (US8; FR-063 … FR-065, SC-005; N13): a worked example withholds its last steps in
 * the «intermedio» and «avanzado» presentations. A withheld step waits behind a control — think,
 * then reveal — with no field to fill and nothing sent to the server.
 */
const COURSE = "algebra_basica";
const NODE = "ALG-N1-O01-SEMEJANTES";
const LESSON_URL = `**/api/student/lessons/${COURSE}/${NODE}`;

const STEPS = [
  "Primero: mira la parte literal de cada término.",
  "Segundo: agrupa los que comparten la letra.",
  "Tercero: suma los coeficientes del grupo.",
  "Cuarto: escribe el coeficiente junto a la letra.",
  "Quinto: revisa que no quede nada por juntar.",
];
const EXPLAIN = "¿Por qué la letra no cambia al sumar?";
const SOLUTION = "Quedan siete trineos en la rampa.";
const NEXT = "Ver el siguiente paso";
const INVITATION = "Tu turno: piensa este paso antes de verlo.";
const REVEAL = "Comparar con el paso";
const WITHHELD = [["intermedio", 2], ["avanzado", 3]] as const;

type Presentation = "basico" | "intermedio" | "avanzado";

function lesson(presentation: Presentation, state = "current") {
  return {
    node_id: NODE,
    node_type: "concept",
    course_id: COURSE,
    i18n_prefix: "",
    next_node_id: null,
    state,
    presentation,
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
      worked_examples: [
        {
          eyebrow: "Ejemplo resuelto",
          title: "Los trineos de la rampa",
          statement: "Junta los trineos que llevan la misma carga.",
          steps: STEPS,
          solution: SOLUTION,
          self_explanation: { step_index: 3, prompt: EXPLAIN },
        },
      ],
      practice: [],
      feedback: { correct: "Exacto.", default: "Revisa la parte literal." },
      footer: { label: "Dominio", states: { sin_ayuda: "Sin ayuda", consolidacion: "Con ayuda", repasar: "Repasar" } },
      finish_label: "Terminar el nodo",
    },
  };
}

/** Opens the lesson and returns the example with the list of API requests made so far. */
async function openExample(page: Page, presentation: Presentation) {
  const requests: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (url.pathname.startsWith("/api/")) requests.push(`${request.method()} ${url.pathname}`);
  });
  await page.route(LESSON_URL, (route) => route.fulfill({ json: lesson(presentation) }));
  await page.route(`${LESSON_URL}/events`, (route) => route.fulfill({ json: lesson(presentation) }));
  await mockStudentApi(page);
  await injectAuth(page);
  await page.goto(`/student/course/${COURSE}/lesson/${NODE}`);
  const example = page.locator(".block-example");
  await expect(example.getByText(STEPS[0])).toBeVisible();
  await page.waitForLoadState("networkidle");
  return { example, requests };
}

/** Presses «Ver el siguiente paso» for as long as the example offers it; returns the presses. */
async function stepWithNextOnly(page: Page) {
  let presses = 0;
  for (let shown = 1; shown < STEPS.length; shown += 1) {
    const next = page.getByRole("button", { name: `${NEXT} (${shown} / ${STEPS.length})` });
    if ((await next.count()) === 0) break;
    await next.click();
    await expect(next).toHaveCount(0);
    presses += 1;
  }
  return presses;
}

test.describe("Spec 003 L6 — pasos retenidos de un ejemplo resuelto", () => {
  test("básico no retiene ningún paso", async ({ page }) => {
    const { example } = await openExample(page, "basico");
    expect(await stepWithNextOnly(page)).toBe(4);
    for (const step of STEPS) await expect(example.getByText(step)).toBeVisible();
    await expect(example.getByLabel(EXPLAIN)).toBeVisible();
    await expect(example.getByText(SOLUTION)).toBeVisible();
  });

  test("intermedio retiene los dos últimos pasos y avanzado los tres últimos", async ({ page }) => {
    for (const [presentation, withheld] of [["intermedio", 2], ["avanzado", 3]] as const) {
      const { example } = await openExample(page, presentation);
      await stepWithNextOnly(page);
      const plain = STEPS.length - withheld;
      for (const step of STEPS.slice(0, plain)) await expect(example.getByText(step)).toBeVisible();
      for (const step of STEPS.slice(plain)) await expect(example.getByText(step)).toHaveCount(0);
    }
  });

  test("mostrar un paso no envía nada al servidor", async ({ page }) => {
    const { example, requests } = await openExample(page, "basico");
    const before = [...requests];
    expect(await stepWithNextOnly(page)).toBe(4);
    await expect(example.getByText(STEPS[4])).toBeVisible();
    await page.waitForLoadState("networkidle");
    expect(requests).toEqual(before);
  });

  test("un paso retenido invita a pensarlo y se revela con su control", async ({ page }) => {
    for (const [presentation, withheld] of WITHHELD) {
      const { example, requests } = await openExample(page, presentation);
      const plain = STEPS.length - withheld;
      expect(await stepWithNextOnly(page)).toBe(plain - 1);
      const before = [...requests];
      const reveal = example.getByRole("button", { name: REVEAL, exact: true });

      for (let index = plain; index < STEPS.length; index += 1) {
        await expect(example.getByText(INVITATION)).toBeVisible();
        await expect(example.getByRole("button", { name: new RegExp(NEXT) })).toHaveCount(0);
        await expect(example.getByText(STEPS[index])).toHaveCount(0);
        await reveal.click();
        await expect(example.getByText(STEPS[index])).toBeVisible();
      }

      // Every step is on screen, in full: nothing is left to ask for, and nothing to fill in.
      for (const step of STEPS) await expect(example.getByText(step)).toBeVisible();
      await expect(example.getByText(INVITATION)).toHaveCount(0);
      await expect(reveal).toHaveCount(0);
      await expect(example.getByText("Complétalo tú")).toHaveCount(0);
      await page.waitForLoadState("networkidle");
      expect(requests).toEqual(before);
    }
  });

  test("la autoexplicación aparece con su paso, no antes", async ({ page }) => {
    for (const [presentation, withheld] of WITHHELD) {
      const { example } = await openExample(page, presentation);
      await stepWithNextOnly(page);
      const reveal = example.getByRole("button", { name: REVEAL, exact: true });
      // The prompt hangs from the fourth step: every withheld step before it comes first.
      for (let index = STEPS.length - withheld; index < 3; index += 1) {
        await expect(example.getByLabel(EXPLAIN)).toHaveCount(0);
        await reveal.click();
        await expect(example.getByText(STEPS[index])).toBeVisible();
      }
      await expect(example.getByText(STEPS[3])).toHaveCount(0);
      await expect(example.getByLabel(EXPLAIN)).toHaveCount(0);
      await reveal.click();
      await expect(example.getByText(STEPS[3])).toBeVisible();
      await expect(example.getByLabel(EXPLAIN)).toBeVisible();
    }
  });

  test("la solución espera a que todos los pasos estén a la vista", async ({ page }) => {
    for (const [presentation, withheld] of WITHHELD) {
      const { example } = await openExample(page, presentation);
      await stepWithNextOnly(page);
      const reveal = example.getByRole("button", { name: REVEAL, exact: true });
      for (let index = STEPS.length - withheld; index < STEPS.length; index += 1) {
        await expect(example.getByText(SOLUTION)).toHaveCount(0);
        await reveal.click();
        await expect(example.getByText(STEPS[index])).toBeVisible();
      }
      await expect(example.getByText(SOLUTION)).toBeVisible();
    }
  });
});
