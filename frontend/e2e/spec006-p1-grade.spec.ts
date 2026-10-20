import { test, expect } from "./fixtures";
import type { Page } from "@playwright/test";
import { injectAuth, MOCK_TEACHER } from "./helpers/auth";

/**
 * Spec 006 P1 (FR-051): the grade starts empty — the AI score is shown beside it, with the AI's
 * feedback, but never pre-fills the teacher's grade — and nothing is saved until the teacher
 * picks a grade.
 */

const PROCEDURE = {
  submission_id: 7,
  student_id: 11,
  student_name: "ana_g",
  item_id: "calc_q1",
  item_content: "Calcula $\\frac{1}{2} + \\frac{1}{3}$",
  ai_score: 72,
  ai_feedback: "Falta justificar el paso 2.",
  status: "PENDING_TEACHER_VALIDATION",
  created_at: "2026-10-10 12:00:00",
  has_image: false,
  review_round: 1,
};

async function openQueue(page: Page) {
  const grades: Record<string, unknown>[] = [];
  await page.route("**/api/teacher/**", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "[]" }),
  );
  await page.route("**/api/teacher/procedures", (route) =>
    route.fulfill({ status: 200, json: [PROCEDURE] }),
  );
  await page.route("**/api/teacher/procedures/grade", (route) => {
    grades.push(route.request().postDataJSON());
    return route.fulfill({
      status: 200,
      json: {
        submission_id: 7,
        teacher_score: 80,
        elo_delta: 6,
        status: "graded",
        computed_delta: 6,
        contribution: 6,
        review_round: 1,
      },
    });
  });
  await page.route("**/api/student/exam/pending", (route) => route.fulfill({ status: 200, json: [] }));
  await injectAuth(page, MOCK_TEACHER);
  await page.goto("/teacher/procedures");
  return grades;
}

test.describe("Procedimientos — calificación con cuidado", () => {
  test("la nota empieza vacía y la de la IA se muestra al lado, con su retroalimentación (US5-AS2, FR-051)", async ({
    page,
  }) => {
    const grades = await openQueue(page);

    const verdict = page.locator(".ai-verdict");
    await expect(verdict).toContainText("72");
    await expect(verdict).toContainText("Falta justificar el paso 2.");
    await expect(page.locator(".gp-num b")).toHaveText("—");
    const save = page.getByRole("button", { name: /Guardar calificación/ });
    await expect(save).toBeDisabled();

    await page.locator(".gp-chip", { hasText: "80" }).click();
    await expect(save).toBeEnabled();
    await save.click();

    await expect.poll(() => grades.length).toBe(1);
    expect(grades[0]).toMatchObject({ submission_id: 7, teacher_score: 80, review_round: 1 });
  });
});
