import { test, expect } from "@playwright/test";
import { injectAuth, mockStudentApi } from "./helpers/auth";

test.describe("Sala de Práctica", () => {
  test.beforeEach(async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page);
    await page.goto("/student");
  });

  test("muestra el selector de cursos al entrar", async ({ page }) => {
    await expect(page.getByText("Sala de Práctica")).toBeVisible();
    await expect(page.getByText("Selecciona un curso para empezar")).toBeVisible();
  });

  test("lista los cursos matriculados", async ({ page }) => {
    await expect(page.getByText("Cálculo Diferencial")).toBeVisible();
    await expect(page.getByText("Álgebra Lineal")).toBeVisible();
  });

  test("seleccionar un curso carga la primera pregunta", async ({ page }) => {
    await page.getByText("Cálculo Diferencial").click();

    // Esperar a que desaparezca el estado de carga y aparezca la pregunta
    await expect(page.getByText("Cargando pregunta...")).not.toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("¿Cuánto es")).toBeVisible();
  });

  test("se puede seleccionar una opción y aparece botón de envío", async ({ page }) => {
    await page.getByText("Cálculo Diferencial").click();
    await expect(page.getByText("¿Cuánto es")).toBeVisible({ timeout: 5_000 });

    await page.getByText("4").click();

    await expect(page.getByRole("button", { name: "Enviar respuesta" })).toBeVisible();
  });

  test("enviar respuesta muestra el feedback de ELO", async ({ page }) => {
    await page.getByText("Cálculo Diferencial").click();
    await expect(page.getByText("¿Cuánto es")).toBeVisible({ timeout: 5_000 });

    await page.getByText("4").click();
    await page.getByRole("button", { name: "Enviar respuesta" }).click();

    // El mock devuelve is_correct=true con delta_elo=16
    await expect(page.getByText(/\+16|ELO|\+[0-9]/i)).toBeVisible({ timeout: 5_000 });
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

    await expect(page.getByText(/[Nn]o estás matriculado/)).toBeVisible();
    await expect(page.getByText(/catálogo de cursos/)).toBeVisible();
  });

  test("botón ← Cambiar curso vuelve al selector", async ({ page }) => {
    await page.getByText("Cálculo Diferencial").click();
    await expect(page.getByText("¿Cuánto es")).toBeVisible({ timeout: 5_000 });

    await page.getByText("← Cambiar curso").click();

    await expect(page.getByText("Selecciona un curso para empezar")).toBeVisible();
  });
});
