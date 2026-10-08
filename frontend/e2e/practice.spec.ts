import { test, expect } from "@playwright/test";
import { injectAuth, mockStudentApi } from "./helpers/auth";

test.describe("Sala de Práctica", () => {
  test.beforeEach(async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page);
    await page.goto("/student/courses");
  });

  async function openPractice(page: import("@playwright/test").Page) {
    await page.getByRole("button", { name: /Practicar/ }).first().click();
    await expect(page).toHaveURL(/\/student\/course\/calculo$/);
    await page.getByRole("button", { name: /Ir a practicar/ }).click();
    await expect(page).toHaveURL("/student");
    await expect(page.getByText(/¿Cuánto es/)).toBeVisible();
  }

  test("muestra el catálogo de cursos al entrar", async ({ page }) => {
    await expect(page.getByRole("heading", { name: /Materias|Cursos/ })).toBeVisible();
    await expect(page.getByText("Cálculo Diferencial")).toBeVisible();
  });

  test("lista los cursos matriculados", async ({ page }) => {
    await expect(page.getByText("Cálculo Diferencial")).toBeVisible();
    await expect(page.getByText("Álgebra Lineal")).toBeVisible();
  });

  test("seleccionar un curso carga la primera pregunta", async ({ page }) => {
    await openPractice(page);
  });

  test("se puede seleccionar una opción y aparece botón de envío", async ({ page }) => {
    await openPractice(page);

    await page.getByRole("button", { name: "Opción B", exact: true }).click();

    await expect(page.getByRole("button", { name: "Enviar respuesta" })).toBeVisible();
  });

  test("enviar respuesta muestra el feedback de ELO", async ({ page }) => {
    await openPractice(page);

    await page.getByRole("button", { name: "Opción B", exact: true }).click();
    await page.getByRole("button", { name: "Enviar respuesta" }).click();

    // El mock devuelve is_correct=true con delta_elo=16
    await expect(page.getByText("ELO en este tema (Aritmética): 1000 → 1016 (+16.0)", { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Opción B — Correcto", exact: true })).toBeDisabled();
  });

  test("sin cursos matriculados muestra enlace al catálogo", async ({ page }) => {
    // Override: devuelve lista vacía de cursos
    await page.route("**/api/student/courses", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    });
    await page.reload();

    await page.getByRole("button", { name: "Mis matrículas" }).click();
    await expect(page.getByText("No estás matriculado en ningún curso aún.")).toBeVisible();
  });

  test("botón ← Cambiar curso vuelve al selector", async ({ page }) => {
    await openPractice(page);

    await page.getByText("← Cambiar curso").click();

    await expect(page).toHaveURL("/student/courses");
  });
});
