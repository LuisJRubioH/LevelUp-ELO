import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi, MOCK_TEACHER } from "./helpers/auth";
import type { Page } from "@playwright/test";

/**
 * Spec 007 S (FR-070, US7-AS1): the League's answers, counted per topic and per item and marked as
 * League answers, beside the practice figures — on the student's statistics, in the teacher's
 * student panel and as a sheet of the workbook. Mocked API.
 */
const LEAGUE = {
  answers: 6,
  correct: 4,
  topics: [
    { course_id: "algebra_basica", course_name: "Álgebra", topic: "Fracciones", answers: 4, correct: 2, share_correct: 0.5, source: "league" },
    { course_id: "algebra_basica", course_name: "Álgebra", topic: "Potencias", answers: 2, correct: 2, share_correct: 1, source: "league" },
  ],
  items: [
    {
      item_id: "f1",
      course_id: "algebra_basica",
      topic: "Fracciones",
      answers: 3,
      missed: 2,
      last_answered_at: "2026-10-21 10:00:00",
      source: "league",
      content: "¿Cuánto es $\\frac{1}{2}+\\frac{1}{4}$?",
      options: ["3/4", "2/6"],
      image_url: null,
    },
  ],
};

async function json(page: Page, url: string, body: unknown) {
  await page.route(url, (route) => route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) }));
}

test("la Liga aparece en mis estadísticas, aparte de la práctica (spec 007 US7-AS1)", async ({ page }) => {
  await mockStudentApi(page);
  await json(page, "**/api/student/league/stats", LEAGUE);
  await injectAuth(page);
  await page.goto("/student/stats");

  const card = page.locator(".sp-card").filter({ has: page.getByRole("heading", { name: "En la Liga" }) });
  await expect(card).toBeVisible({ timeout: 5_000 });
  await expect(card).toContainText("no cambia tu ELO");
  const topics = card.getByRole("list", { name: "En la Liga, por tema" }).getByRole("listitem");
  await expect(topics).toHaveCount(2);
  await expect(topics.first()).toContainText("Fracciones");
  await expect(topics.first()).toContainText("2 de 4");
  const missed = card.getByRole("list", { name: "Lo que más fallas en la Liga" }).getByRole("listitem");
  await expect(missed).toHaveCount(1);
  await expect(missed.first()).toContainText("falló 2 de 3");
  await expect(missed.first().locator(".katex").first()).toBeVisible(); // D5: the statement as math
  // The practice figures are still the practice ones (mock: 42 attempts).
  await expect(page.getByText(/42/)).toBeVisible();
});

test("sin respuestas en la Liga no hay tarjeta de la Liga (spec 007 FR-070)", async ({ page }) => {
  await mockStudentApi(page);
  await json(page, "**/api/student/league/stats", { answers: 0, correct: 0, topics: [], items: [] });
  await injectAuth(page);
  await page.goto("/student/stats");

  await expect(page.getByText(/42/)).toBeVisible({ timeout: 5_000 });
  await expect(page.getByRole("heading", { name: "En la Liga" })).toHaveCount(0);
});

test("el docente ve lo que el estudiante falla en la Liga (spec 007 US7-AS1)", async ({ page }) => {
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
  await json(page, "**/api/teacher/student/5/league", LEAGUE);
  await injectAuth(page, MOCK_TEACHER);
  await page.goto("/teacher");
  await page.getByTitle("Ver perfil").click();

  const section = page.locator(".sd-section").filter({ has: page.getByRole("heading", { name: "En la Liga" }) });
  await expect(section).toBeVisible();
  const topics = section.getByRole("list", { name: "En la Liga, por tema" }).getByRole("listitem");
  await expect(topics).toHaveCount(2);
  await expect(topics.first()).toContainText("2 de 4");
  const missed = section.getByRole("list", { name: "Lo que más falla en la Liga" }).getByRole("listitem");
  await expect(missed.first()).toContainText("falló 2 de 3");
  await expect(missed.first()).toContainText("f1");
});

test("el libro trae la hoja Liga (spec 007 FR-070)", async ({ page }) => {
  await page.route("**/api/teacher/**", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "[]" }),
  );
  await injectAuth(page, MOCK_TEACHER);
  await page.goto("/teacher/export");
  await page.getByRole("button", { name: /Excel/ }).click();

  await expect(page.locator(".xp-sheet")).toHaveText(["Intentos", "Matrículas", "Procedimientos", "KatIA", "Liga"]);
  await expect(page.getByText("Un archivo Excel con 5 hojas de datos.")).toBeVisible();
});
