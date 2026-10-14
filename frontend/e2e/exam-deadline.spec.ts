import { test, expect } from "./fixtures";
import type { Page } from "@playwright/test";
import { injectAuth, mockStudentApi } from "./helpers/auth";

/**
 * The exam's clock is the wall clock, not a count of timer ticks: a browser slows timers in a
 * background tab, and the server closes the session at its own deadline. A refusal from the server
 * is not retried and its reason is shown.
 */

const ITEM = {
  id: "exam-item-1",
  content: "¿Cuánto es $2+2$?",
  difficulty: 900,
  topic: "Aritmética",
  options: ["3", "4"],
  image_url: null,
  tags: [],
};

async function mockExam(page: Page, submit: { status: number; body: object }) {
  const submits: number[] = [];
  await page.route("**/api/student/exam/templates*", (route) =>
    route.fulfill({ status: 200, json: [] }),
  );
  await page.route("**/api/student/exam/start", (route) =>
    route.fulfill({
      status: 200,
      json: {
        session_id: "session-1",
        items: [ITEM],
        n_questions: 1,
        time_limit_seconds: 300,
        course_id: "calculo",
      },
    }),
  );
  await page.route("**/api/student/exam/submit", (route) => {
    submits.push(Date.now());
    return route.fulfill({ status: submit.status, json: submit.body });
  });
  return submits;
}

const RESULT = {
  results: [{ item_id: ITEM.id, is_correct: true, selected_option: "4", elo_delta: 0 }],
  correct_count: 1,
  total_questions: 1,
  score_pct: 100,
  global_elo_after: null,
};

test.describe("Examen — fin del tiempo", () => {
  test("se envía al vencer el tiempo aunque el navegador haya frenado el temporizador", async ({
    page,
  }) => {
    await page.clock.install({ time: new Date("2026-10-10T15:00:00Z") });
    await mockStudentApi(page);
    await injectAuth(page);
    const submits = await mockExam(page, { status: 200, body: RESULT });

    await page.goto("/student/exam?course=calculo&n=1&t=5");
    await expect(page.getByText("¿Cuánto es")).toBeVisible();

    // A background tab: five minutes go by and the 1 s timer barely fires.
    await page.clock.setSystemTime(new Date("2026-10-10T15:05:01Z"));
    await page.clock.runFor(1000);

    await expect.poll(() => submits.length).toBe(1);
  });

  test("un rechazo del servidor no se reintenta y muestra su motivo", async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page);
    const submits = await mockExam(page, {
      status: 409,
      body: { detail: "La sesión de examen expiró." },
    });

    await page.goto("/student/exam?course=calculo&n=1&t=5");
    await page.getByRole("button", { name: "4" }).click();
    await page.getByRole("button", { name: "Finalizar examen" }).click();
    await page.getByRole("button", { name: "Sí, finalizar" }).click();

    await expect(page.getByRole("alert")).toContainText("La sesión de examen expiró.");
    expect(submits).toHaveLength(1);
  });
});
