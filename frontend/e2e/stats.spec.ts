import { test, expect } from "@playwright/test";
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
    await expect(page.getByText(/1[.,\s]?0[45][05]|1050/)).toBeVisible({ timeout: 5_000 });
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
