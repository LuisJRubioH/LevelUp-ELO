import { test, expect } from "./fixtures";
import { injectAuth, MOCK_TEACHER } from "./helpers/auth";
import type { Page } from "@playwright/test";

/**
 * Spec 005 K3 (FR-033): the teacher's student panel shows where the student got with KatIA — one
 * row per closed conversation of the selected course with its outcome, turns and kind of
 * difficulty. No message text exists to show.
 */
async function json(page: Page, url: string, body: unknown) {
  await page.route(url, (route) => route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) }));
}

test("el panel del estudiante muestra las conversaciones con KatIA del curso, sin texto", async ({ page }) => {
  await page.route("**/api/teacher/**", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "[]" }),
  );
  await json(page, "**/api/teacher/metrics*", {});
  await json(page, "**/api/teacher/dashboard*", {
    students: [
      { user_id: 5, name: "sofia", education_level: "colegio", group_id: 1, group_name: "10A", global_elo: 1000, display_rating: 1000, rank_label: "Plata I", overall_status: "rated", total_attempts: 3, accuracy: 0.5, last_activity: "2026-10-19" },
    ],
    groups: [{ group_id: 1, name: "10A", course_id: "algebra_basica", student_count: 1 }],
  });
  await page.route("**/api/teacher/student/5/path/**", (route) => route.fulfill({ status: 404, json: { detail: "x" } }));
  const summary = { course_name: "Álgebra", misconception_tag: null, opened_at: "2026-10-19 03:00:00", closed_at: "2026-10-19 03:05:00" };
  await json(page, "**/api/teacher/student/5/katia-history", {
    conversations: [
      { id: 3, course_id: "algebra_basica", topic: "Fracciones", item_id: "i3", turns: 4, outcome: "superado", difficulty: "procedimiento", ...summary },
      { id: 2, course_id: "algebra_basica", topic: "Potencias", item_id: "i2", turns: 1, outcome: "abandonado", difficulty: "sin_clasificar", ...summary },
      { id: 1, course_id: "calculo", topic: "Límites", item_id: "i1", turns: 2, outcome: "no_superado", difficulty: "calculo", ...summary },
    ],
  });
  await injectAuth(page, MOCK_TEACHER);
  await page.goto("/teacher");
  await page.getByTitle("Ver perfil").click();

  const section = page.locator(".sd-section").filter({ hasText: "Conversaciones con KatIA" });
  const rows = section.locator("tbody tr");
  await expect(rows).toHaveCount(2); // only the selected course
  await expect(rows.nth(0)).toContainText("Fracciones");
  await expect(rows.nth(0)).toContainText("Superado");
  await expect(rows.nth(0)).toContainText("Procedimiento");
  await expect(rows.nth(1)).toContainText("Abandonado");
  await expect(rows.nth(1)).toContainText("Sin clasificar");
  await expect(section.getByText("Límites")).toHaveCount(0);
});
