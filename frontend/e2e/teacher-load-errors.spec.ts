import { test, expect } from "./fixtures";
import type { Page } from "@playwright/test";
import { injectAuth, MOCK_TEACHER } from "./helpers/auth";

/**
 * A request the teacher console could not complete says so: it never shows the empty state
 * («¡Al día!», «0 grupos», «Sin datos») as if there were nothing to see.
 */

async function teacherApi(page: Page) {
  // Every teacher call answers empty unless a test overrides it (later routes win).
  await page.route("**/api/teacher/**", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "[]" }),
  );
  await page.route("**/api/teacher/dashboard", (route) =>
    route.fulfill({ status: 200, json: { students: [], groups: [] } }),
  );
  await page.route("**/api/teacher/metrics", (route) => route.fulfill({ status: 200, json: {} }));
  await page.route("**/api/student/exam/pending", (route) =>
    route.fulfill({ status: 200, json: [] }),
  );
  await injectAuth(page, MOCK_TEACHER);
}

const REFUSED = { status: 403, json: { detail: "Cuenta docente pendiente de aprobación." } };

test.describe("Consola docente — errores de carga", () => {
  test("procedimientos: un error no se muestra como «¡Al día!»", async ({ page }) => {
    await teacherApi(page);
    await page.route("**/api/teacher/procedures", (route) => route.fulfill(REFUSED));

    await page.goto("/teacher/procedures");

    await expect(page.getByText("No pudimos cargar los procedimientos")).toBeVisible();
    await expect(page.getByText("¡Al día!")).toHaveCount(0);
  });

  test("grupos: un error no se muestra como «0 grupos»", async ({ page }) => {
    await teacherApi(page);
    await page.route("**/api/teacher/groups", (route) => route.fulfill(REFUSED));

    await page.goto("/teacher/groups");

    await expect(page.getByText("No pudimos cargar tus grupos")).toBeVisible();
  });

  test("grupos: si no se puede generar el código, se dice", async ({ page }) => {
    await teacherApi(page);
    await page.route("**/api/teacher/groups", (route) =>
      route.fulfill({
        status: 200,
        json: [
          { group_id: 7, name: "10A", course_id: "algebra_basica", invite_code: null, student_count: 0 },
        ],
      }),
    );
    await page.route("**/api/teacher/groups/7/invite-code", (route) =>
      route.fulfill({ status: 500, json: { detail: "No se pudo generar el código." } }),
    );

    await page.goto("/teacher/groups");
    await page.getByTitle("Generar código de invitación").first().click();

    await expect(page.getByRole("alert")).toContainText("No se pudo generar el código.");
  });

  test("panel: si las métricas no cargan, la pestaña lo dice", async ({ page }) => {
    await teacherApi(page);
    await page.route("**/api/teacher/metrics", (route) => route.fulfill(REFUSED));

    await page.goto("/teacher");
    await page.getByRole("button", { name: /Métricas/ }).first().click();

    await expect(page.getByRole("alert")).toContainText("No pudimos cargar las métricas");
  });
});
