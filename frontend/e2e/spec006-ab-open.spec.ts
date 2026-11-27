import { test, expect } from "./fixtures";
import type { Page, Request } from "@playwright/test";
import { injectAuth, mockStudentApi } from "./helpers/auth";

/**
 * Spec 006 AB1 (FR-061 … FR-063): a template's open questions come after its multiple choice — a
 * short answer typed in a field, a procedure sent as a photo while the exam is open; only the short
 * answers travel with the submission, and the results say how many were right and that the
 * procedures await the teachers' review.
 */

const ITEMS = [
  {
    id: "ab-uno",
    content: "Pregunta uno",
    difficulty: 900,
    topic: "Límites",
    options: ["A", "B"],
    image_url: null,
    tags: [],
  },
];
const OPEN = [
  { id: 71, statement: "¿Cuánto es 10 ÷ 4?", kind: "short", has_photo: false },
  { id: 72, statement: "Demuestra que la suma de dos pares es par.", kind: "procedure", has_photo: false },
];
// A 1×1 PNG.
const PNG = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
  "base64",
);

async function mockExam(page: Page) {
  const submits: Request[] = [];
  const photos: Request[] = [];
  await page.route("**/api/student/exam/open-photo", (route) => {
    photos.push(route.request());
    return route.fulfill({ status: 200, json: { question_id: 72, has_photo: true } });
  });
  await page.route("**/api/student/exam/pending", (route) =>
    route.fulfill({ status: 200, json: [] }),
  );
  await page.route("**/api/student/exam/templates*", (route) =>
    route.fulfill({ status: 200, json: [] }),
  );
  await page.route("**/api/student/exam/start", (route) =>
    route.fulfill({
      status: 200,
      json: {
        session_id: "s-ab",
        items: ITEMS,
        n_questions: 1,
        time_limit_seconds: 900,
        course_id: "calculo",
        resumed: false,
        open_questions: OPEN,
      },
    }),
  );
  await page.route("**/api/student/exam/submit", (route) => {
    submits.push(route.request());
    return route.fulfill({
      status: 200,
      json: {
        results: [
          { item_id: "ab-uno", graded: true, is_correct: true, selected_option: "A", elo_delta: 0 },
        ],
        correct_count: 1,
        total_questions: 1,
        score_pct: 100,
        global_elo_after: null,
        open_results: [{ question_id: 71, correct: true }],
        open_pending: 1,
      },
    });
  });
  return { submits, photos };
}

test.describe("Examen — preguntas abiertas", () => {
  test("la respuesta corta se escribe y el procedimiento se sube como foto", async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page);
    const { submits, photos } = await mockExam(page);

    await page.goto("/student/exam?course=calculo&n=1&t=15");
    await expect(page.getByText("Pregunta uno")).toBeVisible();
    await expect(page.getByText("0/3 respondidas").first()).toBeVisible();
    await page.getByRole("button", { name: "A", exact: true }).click();
    await page.getByRole("button", { name: "Siguiente →" }).click();

    await expect(page.getByText("Pregunta abierta 1 de 2")).toBeVisible();
    await page.getByLabel(/Escribe solo tu respuesta/).fill("2,5");
    await page.getByRole("button", { name: "Siguiente →" }).click();

    await expect(page.getByText("Demuestra que la suma de dos pares es par.")).toBeVisible();
    await page.locator("#photo-72").setInputFiles({ name: "hoja.png", mimeType: "image/png", buffer: PNG });
    await expect(page.getByRole("status").filter({ hasText: "Foto recibida." })).toBeVisible();
    await expect(page.getByText("3/3 respondidas").first()).toBeVisible();
    expect(photos).toHaveLength(1);

    await page.getByRole("button", { name: "Finalizar examen" }).click();
    await page.getByRole("button", { name: /Sí, finalizar/ }).click();

    await expect(page.getByText("Respuestas cortas: 1 de 1 correctas.")).toBeVisible();
    await expect(page.getByRole("status").filter({ hasText: "quedan para revisión" })).toBeVisible();
    expect(submits[0].postDataJSON().open_answers).toEqual([{ question_id: 71, text: "2,5" }]);
  });
});
