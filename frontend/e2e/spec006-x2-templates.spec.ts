import { test, expect } from "./fixtures";
import type { Page, Request } from "@playwright/test";
import { injectAuth, MOCK_TEACHER } from "./helpers/auth";

/**
 * Spec 006 X2 (FR-030, FR-031, FR-033): the teacher sees which exams are drafts (no assignment,
 * no student sees them), duplicates one whose items are locked, and reads the results per student
 * with the option each one chose.
 */

const BASE = { teacher_id: 1, course_id: "calculo", time_limit_min: 20, archived: false, created_at: "2026-10-19" };
const TEMPLATES = [
  { ...BASE, id: 1, title: "Borrador de límites", item_ids: ["a"], assigned: false, locked: false },
  { ...BASE, id: 2, title: "Parcial 1", item_ids: ["a", "b"], assigned: true, locked: true },
];
const RESULTS = {
  title: "Parcial 1",
  n_sessions: 1,
  n_students: 1,
  avg_score: 50,
  students: [
    {
      user_id: 9,
      name: "sofia",
      submitted_at: "2026-10-19 10:00:00",
      correct: 1,
      total: 2,
      score_pct: 50,
      answers: [
        { item_id: "a", is_correct: true, selected_option: "4" },
        { item_id: "b", is_correct: false, selected_option: "x = 3" },
      ],
    },
  ],
  questions: [
    { item_id: "a", content: "¿2+2?", topic: "Aritmética", total: 1, correct: 1, accuracy: 100, choices: {} },
    { item_id: "b", content: "Resuelve x", topic: "Álgebra", total: 1, correct: 0, accuracy: 0, choices: { "x = 3": 1 } },
  ],
  topics: [],
  best_question: null,
  worst_question: null,
  reinforce_topic: null,
};

async function mockExams(page: Page) {
  const duplicates: Request[] = [];
  await page.route("**/api/teacher/**", (route) => route.fulfill({ status: 200, json: [] }));
  await page.route("**/api/teacher/courses", (route) =>
    route.fulfill({ status: 200, json: [{ id: "calculo", name: "Cálculo", block: "Universidad" }] }),
  );
  await page.route("**/api/teacher/exam-templates?*", (route) => route.fulfill({ status: 200, json: TEMPLATES }));
  await page.route("**/api/teacher/exam-templates/2/duplicate", (route) => {
    duplicates.push(route.request());
    return route.fulfill({
      status: 201,
      json: { ...TEMPLATES[1], id: 3, title: "Parcial 1 (copia)", assigned: false, locked: false },
    });
  });
  await page.route("**/api/teacher/exam-templates/2/results", (route) => route.fulfill({ status: 200, json: RESULTS }));
  return duplicates;
}

test.describe("Exámenes del docente — borradores, bloqueo y resultados", () => {
  test("un examen sin asignar es borrador y uno ya presentado se duplica para cambiarlo", async ({ page }) => {
    const duplicates = await mockExams(page);
    await injectAuth(page, MOCK_TEACHER);
    await page.goto("/teacher/exams");

    const draft = page.locator(".ex-card").filter({ hasText: "Borrador de límites" });
    const taken = page.locator(".ex-card").filter({ hasText: "Parcial 1" });
    await expect(draft.getByText("Borrador", { exact: true })).toBeVisible();
    await expect(taken.getByText("Borrador", { exact: true })).toHaveCount(0);
    await expect(taken.getByText("Ya presentado")).toBeVisible();
    await expect(draft.getByRole("button", { name: "Duplicar" })).toHaveCount(0);

    await taken.getByRole("button", { name: "Duplicar" }).click();

    await expect.poll(() => duplicates.length).toBe(1);
    await expect(page.getByText("Parcial 1 (copia)")).toBeVisible();
  });

  test("los resultados muestran a cada estudiante con la opción que eligió", async ({ page }) => {
    await mockExams(page);
    await injectAuth(page, MOCK_TEACHER);
    await page.goto("/teacher/exams");

    await page.locator(".ex-card").filter({ hasText: "Parcial 1" }).getByRole("button", { name: "Resultados" }).click();

    const students = page.locator(".gd-section").filter({ hasText: "Por estudiante" });
    await expect(students.getByText("sofia")).toBeVisible();
    await expect(students.getByText("50%")).toBeVisible();
    await expect(students.getByText("x = 3")).toBeVisible();
  });
});
