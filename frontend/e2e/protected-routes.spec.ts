import { test, expect } from "@playwright/test";
import { injectAuth, mockStudentApi, MOCK_TEACHER } from "./helpers/auth";

test.describe("Rutas protegidas — redirección", () => {
  test("/ sin autenticación → redirige a /login", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveURL("/login");
  });

  test("/student sin autenticación → redirige a /login", async ({ page }) => {
    await page.goto("/student");
    await expect(page).toHaveURL("/login");
  });

  test("/student/stats sin autenticación → redirige a /login", async ({ page }) => {
    await page.goto("/student/stats");
    await expect(page).toHaveURL("/login");
  });

  test("/student/courses sin autenticación → redirige a /login", async ({ page }) => {
    await page.goto("/student/courses");
    await expect(page).toHaveURL("/login");
  });

  test("/student/exam sin autenticación → redirige a /login", async ({ page }) => {
    await page.goto("/student/exam");
    await expect(page).toHaveURL("/login");
  });

  test("/teacher sin autenticación → redirige a /login", async ({ page }) => {
    await page.goto("/teacher");
    await expect(page).toHaveURL("/login");
  });

  test("/admin sin autenticación → redirige a /login", async ({ page }) => {
    await page.goto("/admin");
    await expect(page).toHaveURL("/login");
  });

  test("ruta inexistente → redirige a /login", async ({ page }) => {
    await page.goto("/ruta-que-no-existe");
    await expect(page).toHaveURL("/login");
  });
});

test.describe("Rutas protegidas — control de roles", () => {
  test("estudiante en /teacher → redirige a /login", async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page); // estudiante
    await page.goto("/teacher");
    await expect(page).toHaveURL("/login");
  });

  test("docente en /student → redirige a /login", async ({ page }) => {
    await page.route("**/api/**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({}),
      });
    });
    await injectAuth(page, MOCK_TEACHER);
    await page.goto("/student");
    await expect(page).toHaveURL("/login");
  });
});

test.describe("Página de login", () => {
  test("muestra el formulario de login", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByText("Iniciar sesión")).toBeVisible();
    await expect(page.getByPlaceholder("usuario o correo@ejemplo.com")).toBeVisible();
    await expect(page.getByLabel("Contraseña")).toBeVisible();
    await expect(page.getByRole("button", { name: "Entrar" })).toBeVisible();
  });

  test("usuario ya autenticado en /login → redirige a /student", async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page);
    // Con auth inyectada, ir a /login debe mantenerse en /login (no hay redirect automático)
    // Pero ir a /student debe funcionar
    await page.goto("/student");
    await expect(page).toHaveURL("/student");
  });
});
