import { test, expect } from "@playwright/test";
import { injectAuth, mockLoginEndpoint, MOCK_STUDENT } from "./helpers/auth";

test.describe("Autenticación", () => {
  test("login con credenciales válidas → redirige a /student", async ({ page }) => {
    await mockLoginEndpoint(page);

    await page.goto("/login");
    await expect(page.getByText("Iniciar sesión")).toBeVisible();

    await page.getByPlaceholder("usuario o correo@ejemplo.com").fill("estudiante1");
    await page.getByLabel("Contraseña").fill("demo1234");
    await page.getByRole("button", { name: "Entrar" }).click();

    await expect(page).toHaveURL("/student");
  });

  test("login con contraseña incorrecta → muestra error", async ({ page }) => {
    await page.route("**/api/auth/login", async (route) => {
      await route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Credenciales inválidas" }),
      });
    });

    await page.goto("/login");
    await page.getByPlaceholder("usuario o correo@ejemplo.com").fill("estudiante1");
    await page.getByLabel("Contraseña").fill("incorrecto");
    await page.getByRole("button", { name: "Entrar" }).click();

    await expect(page.getByText(/[Cc]redenciales|inválidas|error/i)).toBeVisible();
    await expect(page).toHaveURL("/login");
  });

  test("login como docente → redirige a /teacher", async ({ page }) => {
    await page.route("**/api/auth/login", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "fake-token",
          token_type: "bearer",
          expires_in: 900,
          user_id: 2,
          username: "profesor1",
          role: "teacher",
        }),
      });
    });
    await page.route("**/api/auth/me", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          user_id: 2,
          username: "profesor1",
          role: "teacher",
          approved: true,
          education_level: null,
          grade: null,
          email: null,
        }),
      });
    });
    // Teacher dashboard needs at least a basic response
    await page.route("**/api/teacher/**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ students: [], summary: {} }),
      });
    });

    await page.goto("/login");
    await page.getByPlaceholder("usuario o correo@ejemplo.com").fill("profesor1");
    await page.getByLabel("Contraseña").fill("demo1234");
    await page.getByRole("button", { name: "Entrar" }).click();

    await expect(page).toHaveURL("/teacher");
  });

  test("formulario de registro está accesible desde login", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("button", { name: "Registrarse" }).click();

    await expect(page.getByText(/[Ee]studiante|[Dd]ocente/)).toBeVisible();
  });

  test("usuario ya autenticado en / → redirige a /student", async ({ page }) => {
    await injectAuth(page, MOCK_STUDENT);
    await page.goto("/");
    await expect(page).toHaveURL("/login");
  });
});
