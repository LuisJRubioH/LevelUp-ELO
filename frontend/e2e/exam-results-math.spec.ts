import { test, expect } from "./fixtures";
import type { Page } from "@playwright/test";
import { injectAuth, MOCK_TEACHER } from "./helpers/auth";

/**
 * QA round 2, Q14 (AGENTS D5): in the teacher's exam results every statement and every chosen
 * option goes through MathText, so a formula renders as KaTeX instead of showing `\frac{x}{3}`
 * or `$x = 4$` as plain text. Mirrors what the flow sweep saw on `alb1` and `alb10`.
 */

const BASE = { teacher_id: 1, course_id: "algebra", time_limit_min: 20, archived: false, created_at: "2026-11-14" };
const TEMPLATES = [{ ...BASE, id: 2, title: "Parcial con fórmulas", item_ids: ["a", "b"], assigned: true, locked: true }];
const STATEMENT_A = "Resuelve $\\frac{x}{3} = 6$";
const STATEMENT_B = "Si \\(x + 2 = 20\\), ¿cuánto vale $x$?";
const QUESTION_A = { item_id: "a", content: STATEMENT_A, topic: "Ecuaciones", total: 1, correct: 1, accuracy: 100, choices: {} };
const QUESTION_B = { item_id: "b", content: STATEMENT_B, topic: "Ecuaciones", total: 1, correct: 0, accuracy: 0, choices: {} };
const RESULTS = {
  title: "Parcial con fórmulas",
  n_sessions: 1,
  n_students: 1,
  avg_score: 50,
  students: [
    {
      user_id: 9,
      name: "sofia",
      submitted_at: "2026-11-14 10:00:00",
      correct: 1,
      total: 2,
      score_pct: 50,
      answers: [
        { item_id: "a", is_correct: true, selected_option: "$x = 18$" },
        { item_id: "b", is_correct: false, selected_option: "$x = 4$" },
      ],
    },
  ],
  questions: [QUESTION_A, QUESTION_B],
  topics: [{ topic: "Ecuaciones", total: 2, correct: 1, accuracy: 50 }],
  best_question: QUESTION_A,
  worst_question: QUESTION_B,
  reinforce_topic: { topic: "Ecuaciones", total: 2, correct: 1, accuracy: 50 },
};

async function openResults(page: Page) {
  await page.route("**/api/teacher/**", (route) => route.fulfill({ status: 200, json: [] }));
  await page.route("**/api/teacher/courses", (route) =>
    route.fulfill({ status: 200, json: [{ id: "algebra", name: "Álgebra", block: "Colegio" }] }),
  );
  await page.route("**/api/teacher/exam-templates?*", (route) => route.fulfill({ status: 200, json: TEMPLATES }));
  await page.route("**/api/teacher/exam-templates/2/results", (route) => route.fulfill({ status: 200, json: RESULTS }));
  await injectAuth(page, MOCK_TEACHER);
  await page.goto("/teacher/exams");
  await page.locator(".ex-card").filter({ hasText: "Parcial con fórmulas" }).getByRole("button", { name: "Resultados" }).click();
  await expect(page.getByRole("dialog", { name: "Resultados del examen" })).toBeVisible();
}

test.describe("Resultados de un examen — las fórmulas se renderizan (Q14, AGENTS D5)", () => {
  test("el enunciado y la respuesta elegida pasan por KaTeX, no se imprimen como texto", async ({ page }) => {
    await openResults(page);
    const drawer = page.getByRole("dialog", { name: "Resultados del examen" });

    // Resumen (más acertada / más fallada), «Por pregunta» y «Por estudiante»: una fórmula
    // renderizada por cada sitio donde se imprime un enunciado o una opción.
    await expect(drawer.locator(".ex-hl .hl-s .katex")).toHaveCount(3); // 1 fórmula en la más acertada, 2 en la más fallada
    await expect(drawer.locator(".ex-qstat .q-txt .katex")).toHaveCount(3);
    await expect(drawer.locator(".ex-stu .s-answers .o .katex")).toHaveCount(2);

    // Ni delimitadores ni comandos LaTeX a la vista como texto.
    const text = (await drawer.innerText()) ?? "";
    const visible = await drawer.evaluate((el) => {
      const clone = el.cloneNode(true) as HTMLElement;
      clone.querySelectorAll(".katex-mathml, .katex-html").forEach((n) => n.remove());
      return clone.textContent ?? "";
    });
    expect(visible, text).not.toMatch(/\\frac|\\\(|\$/);
  });
});
