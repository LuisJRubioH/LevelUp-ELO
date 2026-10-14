/**
 * The admin's groups page: it reads the fields `GET /api/admin/groups` sends (teacher_name,
 * student_count), and a deletion the server refuses shows its reason instead of failing silently.
 */
import type { Page } from "@playwright/test";
import { test, expect } from "./fixtures";
import { injectAuth } from "./helpers/auth";

const MOCK_ADMIN = {
  user_id: 3,
  username: "admin",
  role: "admin" as const,
  education_level: null,
  grade: null,
  email: null,
};

const GROUP = { id: 7, name: "Grupo 10A", teacher_id: 2, teacher_name: "profesor1", student_count: 23 };

async function openGroups(page: Page) {
  await page.route("**/api/admin/groups", (route) => route.fulfill({ json: { groups: [GROUP] } }));
  await injectAuth(page, MOCK_ADMIN);
  await page.goto("/admin/groups");
}

const row = (page: Page) => page.getByRole("row").filter({ hasText: GROUP.name });

test.describe("Grupos del administrador", () => {
  test("cada grupo muestra su docente y su número de estudiantes", async ({ page }) => {
    await openGroups(page);

    await expect(row(page)).toContainText("profesor1");
    await expect(row(page).getByRole("cell").nth(2)).toHaveText("23");
    await expect(page.getByText("ID undefined")).toHaveCount(0);
  });

  test("si el servidor rechaza la eliminación, se ve el motivo", async ({ page }) => {
    await openGroups(page);
    await page.route(`**/api/admin/groups/${GROUP.id}`, (route) =>
      route.fulfill({ status: 404, json: { detail: "El grupo no existe." } }),
    );

    await row(page).getByRole("button", { name: "Eliminar" }).click();
    await row(page).getByRole("button", { name: "Sí, eliminar" }).click();

    await expect(page.getByRole("alert")).toHaveText("El grupo no existe.");
  });
});
