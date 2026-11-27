import { test, expect } from "./fixtures";
import type { Request } from "@playwright/test";
import { injectAuth, MOCK_TEACHER } from "./helpers/auth";

/**
 * Spec 006 AB1 (FR-060): the teacher writes a template's open questions in its form — a short
 * answer with its accepted answers, a procedure with the reference solution the AI grades
 * against — and they are saved with it.
 */

const DRAFT = {
  id: 1,
  teacher_id: 1,
  course_id: "calculo",
  title: "Fase 1 · Grado 8",
  time_limit_min: 60,
  item_ids: ["a"],
  archived: false,
  created_at: "2026-11-26",
  assigned: false,
  locked: false,
  open_questions: [],
};

test.describe("Exámenes del docente — preguntas abiertas", () => {
  test("se escriben en el formulario y se guardan con la plantilla", async ({ page }) => {
    const patches: Request[] = [];
    await page.route("**/api/teacher/**", (route) => route.fulfill({ status: 200, json: [] }));
    await page.route("**/api/teacher/courses", (route) =>
      route.fulfill({
        status: 200,
        json: [{ id: "calculo", name: "Cálculo", block: "Universidad" }],
      }),
    );
    await page.route("**/api/teacher/exam-templates?*", (route) =>
      route.fulfill({ status: 200, json: [DRAFT] }),
    );
    await page.route("**/api/teacher/exam-templates/1", (route) => {
      patches.push(route.request());
      return route.fulfill({ status: 200, json: DRAFT });
    });
    await injectAuth(page, MOCK_TEACHER);
    await page.goto("/teacher/exams");

    await page
      .locator(".ex-card")
      .filter({ hasText: "Fase 1 · Grado 8" })
      .getByRole("button", { name: "Editar" })
      .click();
    await page.getByRole("button", { name: "+ Agregar pregunta abierta" }).click();
    await page.getByLabel("Enunciado de la pregunta abierta 1").fill("¿Cuánto es 10 ÷ 4?");
    await page.getByLabel(/Respuestas aceptadas 1/).fill("5/2\n2,5");
    await page.getByRole("button", { name: "+ Agregar pregunta abierta" }).click();
    await page.getByLabel("Tipo de la pregunta abierta 2").selectOption("procedure");
    await page
      .getByLabel("Enunciado de la pregunta abierta 2")
      .fill("Demuestra que la suma de dos pares es par.");
    await page.getByLabel(/Solución de referencia 2/).fill("2a + 2b = 2(a + b)");
    await page.getByRole("button", { name: "Guardar cambios" }).click();

    await expect.poll(() => patches.length).toBe(1);
    expect(patches[0].postDataJSON().open_questions).toEqual([
      {
        kind: "short",
        statement: "¿Cuánto es 10 ÷ 4?",
        accepted_answers: ["5/2", "2,5"],
        reference_solution: "",
      },
      {
        kind: "procedure",
        statement: "Demuestra que la suma de dos pares es par.",
        accepted_answers: [],
        reference_solution: "2a + 2b = 2(a + b)",
      },
    ]);
  });
});
