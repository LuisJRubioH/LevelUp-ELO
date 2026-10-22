import { test, expect } from "./fixtures";
import type { Page, Request } from "@playwright/test";
import { injectAuth, mockStudentApi } from "./helpers/auth";

/**
 * Spec 006 X1 (FR-022, FR-024): the exam screen lists the exams assigned to the student and not
 * yet submitted; choosing one prepares it. An item removed from the bank after the start is shown
 * as not graded, not as a wrong answer.
 */

const ITEMS = ["uno", "dos"].map((n) => ({
  id: `x1-${n}`,
  content: `Pregunta ${n}`,
  difficulty: 900,
  topic: "Límites",
  options: ["A", "B"],
  image_url: null,
  tags: [],
}));

async function mockExams(page: Page) {
  const starts: Request[] = [];
  await page.route("**/api/student/exam/pending", (route) =>
    route.fulfill({
      status: 200,
      json: [
        { template_id: 7, title: "Parcial de límites", course_id: "calculo", course_name: "Cálculo Diferencial", time_limit_min: 15 },
      ],
    }),
  );
  await page.route("**/api/student/exam/templates*", (route) =>
    route.fulfill({
      status: 200,
      json: [
        { id: 7, title: "Parcial de límites", course_id: "calculo", n_questions: 2, time_limit_min: 15, created_at: "2026-10-19", window_ends_at: null },
      ],
    }),
  );
  await page.route("**/api/student/exam/start", (route) => {
    starts.push(route.request());
    return route.fulfill({
      status: 200,
      json: { session_id: "s-x1", items: ITEMS, n_questions: 2, time_limit_seconds: 900, course_id: "calculo" },
    });
  });
  await page.route("**/api/student/exam/submit", (route) =>
    route.fulfill({
      status: 200,
      json: {
        results: [
          { item_id: "x1-uno", graded: true, is_correct: true, selected_option: "A", elo_delta: 0 },
          { item_id: "x1-dos", graded: false, is_correct: false, selected_option: "B", elo_delta: 0 },
        ],
        correct_count: 1,
        total_questions: 1,
        score_pct: 100,
        global_elo_after: null,
      },
    }),
  );
  return starts;
}

test.describe("Examen — asignados y preguntas retiradas", () => {
  test("lista los exámenes asignados pendientes y prepara el elegido", async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page);
    const starts = await mockExams(page);

    await page.goto("/student/exam");
    const assigned = page.getByRole("region", { name: "Exámenes asignados" });
    await expect(assigned.getByText("Parcial de límites")).toBeVisible();
    await assigned.getByRole("button", { name: /Parcial de límites/ }).click();
    await page.getByRole("button", { name: "Iniciar examen →" }).click();

    await expect(page.getByText("Pregunta uno")).toBeVisible();
    expect(starts[0].postDataJSON()).toMatchObject({ course_id: "calculo", template_id: 7 });
  });

  test("una pregunta retirada del banco se muestra como no calificada", async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page);
    await mockExams(page);

    await page.goto("/student/exam?course=calculo&n=2&t=15");
    await expect(page.getByText("Pregunta uno")).toBeVisible();
    await page.getByRole("button", { name: "A", exact: true }).click();
    await page.getByRole("button", { name: "Siguiente →" }).click();
    await expect(page.getByText("Pregunta dos")).toBeVisible();
    await page.getByRole("button", { name: "B", exact: true }).click();
    await page.getByRole("button", { name: "Finalizar examen" }).click();
    await page.getByRole("button", { name: /Sí, finalizar/ }).click();

    await expect(page.getByText("No calificada")).toBeVisible();
  });
});
