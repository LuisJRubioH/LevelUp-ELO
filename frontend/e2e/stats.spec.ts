import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi } from "./helpers/auth";

test.describe("Estadísticas del estudiante", () => {
  test.beforeEach(async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page);
    await page.goto("/student/stats");
  });

  test("página de estadísticas carga sin errores", async ({ page }) => {
    // No debe mostrar error boundary ni página en blanco
    await expect(page.getByText(/[Ee]rror|[Ss]omething went wrong/i)).not.toBeVisible();
  });

  test("muestra el ELO global del estudiante", async ({ page }) => {
    // El mock devuelve global_elo: 1050
    await expect(page.locator(".sp-stat").filter({ hasText: "ELO global" }).getByText("1050", { exact: true })).toBeVisible({ timeout: 5_000 });
  });

  test("muestra el rango del estudiante", async ({ page }) => {
    // El mock devuelve rank_label: "Aprendiz I"
    await expect(page.getByText(/Aprendiz/i)).toBeVisible({ timeout: 5_000 });
  });

  test("muestra los intentos totales", async ({ page }) => {
    // El mock devuelve total_attempts: 42
    await expect(page.getByText(/42/)).toBeVisible({ timeout: 5_000 });
  });
});

test("muestra el reporte por subtema, del más débil al más firme (spec 008 US5-AS3)", async ({ page }) => {
  await mockStudentApi(page);
  await page.route("**/api/student/stats", (route) =>
    route.fulfill({
      status: 200,
      json: {
        user_id: 1,
        global_elo: 1050,
        display_rating: 1050,
        overall_status: "rated",
        course_ratings: [],
        topic_elos: [],
        total_attempts: 4,
        study_streak: 1,
        rank_label: "Aprendiz I",
        subtopics: [
          {
            course_id: "evaluar_para_avanzar_8",
            course_name: "Evaluar para Avanzar 8",
            topic: "Pensamiento variacional",
            subtopic: "proporcionalidad entre variables",
            attempts: 1,
            correct: 0,
            share_correct: 0,
          },
          {
            course_id: "evaluar_para_avanzar_8",
            course_name: "Evaluar para Avanzar 8",
            topic: "Pensamiento aleatorio",
            subtopic: "porcentaje sobre un total",
            attempts: 3,
            correct: 2,
            share_correct: 2 / 3,
          },
        ],
      },
    }),
  );
  await injectAuth(page);
  await page.goto("/student/stats");

  const rows = page.getByRole("list", { name: "Por subtema" }).getByRole("listitem");
  await expect(rows).toHaveCount(2);
  await expect(rows.first()).toContainText("proporcionalidad entre variables");
  await expect(rows.first()).toContainText("0 de 1");
  await expect(rows.nth(1)).toContainText("porcentaje sobre un total");
  await expect(rows.nth(1)).toContainText("2 de 3");
});
