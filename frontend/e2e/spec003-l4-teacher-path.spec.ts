import { test, expect } from "./fixtures";
import { injectAuth, MOCK_TEACHER } from "./helpers/auth";
import type { Page } from "@playwright/test";

/**
 * Spec 003 L4 (FR-042; N11): the teacher's student panel shows the learning path — one row per
 * node with activity, the answer history in order on demand (right or wrong, the tag) and the
 * post-diagnostic outcome. No chosen value reaches the screen.
 */
async function json(page: Page, url: string, body: unknown) {
  await page.route(url, (route) => route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) }));
}

test("el panel del estudiante muestra la ruta: historial en orden y resultado del post-diagnóstico", async ({ page }) => {
  await page.route("**/api/teacher/**", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "[]" }),
  );
  await json(page, "**/api/teacher/metrics", {});
  await json(page, "**/api/teacher/dashboard", {
    students: [
      { user_id: 5, name: "sofia", education_level: "colegio", group_id: 1, group_name: "10A", global_elo: 1000, display_rating: 1000, rank_label: "Plata I", overall_status: "rated", total_attempts: 3, accuracy: 0.5, last_activity: "2026-10-19" },
    ],
    groups: [{ group_id: 1, name: "10A", course_id: "algebra_basica", student_count: 1 }],
  });
  await json(page, "**/api/teacher/student/5/path/algebra_basica", {
    student_id: 5,
    course_id: "algebra_basica",
    nodes: [
      { node_id: "B01", title: "Bienvenida", state: "completed", answers: [], outcome: null },
      {
        node_id: "B03",
        title: "La escalera",
        state: "current",
        answers: [
          { label: "Práctica 1", is_expected: false, misconception_tag: "error_escalera", answered_at: "2026-10-19 03:10:00" },
          { label: "Práctica 1", is_expected: true, misconception_tag: null, answered_at: "2026-10-19 03:11:00" },
        ],
        outcome: { diagnostic_correct: 1, post_correct: 3, items: 3, outcome: "gain" },
      },
      { node_id: "B04", title: "Naturales", state: null, answers: [], outcome: null },
    ],
  });
  await injectAuth(page, MOCK_TEACHER);
  await page.goto("/teacher");
  await page.getByTitle("Ver perfil").click();

  const section = page.locator(".sd-section").filter({ hasText: "Ruta de aprendizaje" });
  await expect(section.getByText("Bienvenida")).toBeVisible();
  await expect(section.getByText("Naturales")).toHaveCount(0); // no activity: not listed
  await expect(section.getByText("Avance · 1→3/3")).toBeVisible();

  await section.getByRole("button", { name: /La escalera/ }).click();
  const answers = section.locator(".sd-path-answers li");
  await expect(answers).toHaveCount(2);
  await expect(answers.nth(0)).toContainText("Incorrecta");
  await expect(answers.nth(0)).toContainText("error_escalera");
  await expect(answers.nth(1)).toContainText("Correcta");
});
