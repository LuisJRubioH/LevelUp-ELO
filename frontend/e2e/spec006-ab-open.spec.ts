import { test, expect } from "./fixtures";
import type { Page, Request } from "@playwright/test";
import { injectAuth, mockStudentApi } from "./helpers/auth";

/**
 * Spec 006 AB1 (FR-061, FR-062): a template's open questions come after its multiple choice,
 * each with a text box; what the student types travels with the submission, a blank answer too,
 * and the results say the open answers await the teachers' review.
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
  { id: 71, statement: "Demuestra que la suma de dos pares es par." },
  { id: 72, statement: "¿Cuántos divisores tiene 36?" },
];

async function mockExam(page: Page) {
  const submits: Request[] = [];
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
        open_pending: 2,
      },
    });
  });
  return submits;
}

test.describe("Examen — preguntas abiertas", () => {
  test("se escriben después de la opción múltiple y viajan con el envío", async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page);
    const submits = await mockExam(page);

    await page.goto("/student/exam?course=calculo&n=1&t=15");
    await expect(page.getByText("Pregunta uno")).toBeVisible();
    await expect(page.getByText("0/3 respondidas").first()).toBeVisible();
    await page.getByRole("button", { name: "A", exact: true }).click();
    await page.getByRole("button", { name: "Siguiente →" }).click();

    await expect(page.getByText("Pregunta abierta 1 de 2")).toBeVisible();
    await expect(page.getByText("Demuestra que la suma de dos pares es par.")).toBeVisible();
    await page.getByLabel(/Escribe tu procedimiento/).fill("2a + 2b = 2(a + b)");
    await expect(page.getByText("2/3 respondidas").first()).toBeVisible();

    await page.getByRole("button", { name: "Finalizar examen" }).click();
    await page.getByRole("button", { name: /Sí, finalizar/ }).click();

    await expect(page.getByRole("status").filter({ hasText: "quedan para revisión" })).toBeVisible();
    expect(submits[0].postDataJSON().open_answers).toEqual([
      { question_id: 71, text: "2a + 2b = 2(a + b)" },
      { question_id: 72, text: "" },
    ]);
  });
});
