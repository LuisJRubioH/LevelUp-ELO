import { test, expect } from "@playwright/test";
import { injectAuth, mockStudentApi, MOCK_TEACHER } from "./helpers/auth";

test.describe("Rutas protegidas — redirección", () => {
  test("/ sin autenticación → muestra la portada pública", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveURL("/");
    await expect(page.getByRole("link", { name: /Oulad/ }).first()).toBeVisible();
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
    await injectAuth(page, MOCK_TEACHER);
    await page.goto("/student");
    await expect(page).toHaveURL("/login");
  });
});

test.describe("Página de login", () => {
  test("muestra el formulario de login", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: /Continúa tu ascenso/i })).toBeVisible();
    await expect(page.getByLabel("Usuario o correo")).toBeVisible();
    await expect(page.getByLabel("Contraseña")).toBeVisible();
    await expect(page.getByRole("button", { name: /Entrar a Oulad/ })).toBeVisible();
  });

  test("estudiante sin sesión de práctica accede al catálogo", async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page);
    await page.goto("/student");
    await expect(page).toHaveURL("/student/courses");
    await expect(page.getByText("Cálculo Diferencial")).toBeVisible();
  });
});
