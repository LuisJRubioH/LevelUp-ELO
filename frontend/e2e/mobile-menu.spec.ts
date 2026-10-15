import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi, MOCK_TEACHER } from "./helpers/auth";
import type { Page } from "@playwright/test";

/**
 * Below 1024px the console shell hides its sidebar. Everything that lived only there — logout,
 * the problem report, theme, language, the AI key and, for teachers, all navigation — has to stay
 * reachable: the top bar's "Menú" opens the same sidebar as a drawer.
 */
const PHONE = { width: 390, height: 844 };
const TABLET = { width: 768, height: 1024 };

const menuButton = (page: Page) => page.getByRole("button", { name: "Menú" });
const drawer = (page: Page) => page.locator("#tc-side");

test.describe("Menú móvil del panel", () => {
  test("estudiante en el móvil: el menú da cerrar sesión, exámenes, procedimiento y reportar", async ({ page }) => {
    await page.setViewportSize(PHONE);
    await mockStudentApi(page);
    await page.route("**/api/auth/logout", (route) => route.fulfill({ json: { ok: true } }));
    await page.route("**/api/student/procedures", (route) => route.fulfill({ json: { submissions: [] } }));
    await injectAuth(page);
    await page.goto("/student/stats");

    await expect(drawer(page)).toBeHidden();
    await expect(menuButton(page)).toHaveAttribute("aria-expanded", "false");
    await menuButton(page).click();

    await expect(drawer(page)).toBeVisible();
    await expect(page.getByRole("button", { name: "Cerrar menú" })).toBeFocused();
    await expect(drawer(page).getByRole("link", { name: /Exámenes/ })).toBeVisible();
    await expect(drawer(page).getByRole("link", { name: /Procedimiento/ })).toBeVisible();
    await expect(drawer(page).getByRole("button", { name: /Reportar un problema/ })).toBeVisible();

    // A link closes the drawer and navigates.
    await drawer(page).getByRole("link", { name: /Procedimiento/ }).click();
    await expect(page).toHaveURL("/student/procedure");
    await expect(drawer(page)).toBeHidden();

    // Escape closes it too.
    await menuButton(page).click();
    await expect(drawer(page)).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(drawer(page)).toBeHidden();

    await menuButton(page).click();
    await drawer(page).getByRole("button", { name: /Cerrar sesión/ }).click();
    await expect(page).toHaveURL("/login");
  });

  test("docente en una tableta: el menú da toda la navegación y cerrar sesión", async ({ page }) => {
    await page.setViewportSize(TABLET);
    await injectAuth(page, MOCK_TEACHER);
    await page.goto("/teacher/export");

    await expect(drawer(page)).toBeHidden();
    await menuButton(page).click();
    for (const name of ["Dashboard", "Grupos", "Procedimientos", "Exámenes", "Exportar datos"]) {
      await expect(drawer(page).getByRole("link", { name: new RegExp(name) })).toBeVisible();
    }
    await expect(drawer(page).getByRole("button", { name: /Cerrar sesión/ })).toBeVisible();

    // The backdrop closes it.
    await page.mouse.click(TABLET.width - 20, TABLET.height / 2);
    await expect(drawer(page)).toBeHidden();
  });

  test("en escritorio la barra lateral sigue fija y no hay botón de menú", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await mockStudentApi(page);
    await injectAuth(page);
    await page.goto("/student/stats");

    await expect(drawer(page)).toBeVisible();
    await expect(menuButton(page)).toBeHidden();
    await expect(page.getByRole("button", { name: "Cerrar menú" })).toBeHidden();
  });
});
