import { test, expect } from "./fixtures";
import type { Page } from "@playwright/test";
import { injectAuth, mockStudentApi } from "./helpers/auth";

/**
 * Spec 006 RS (FR-025, FR-026): starting a template already begun resumes it — the screen says so
 * and counts down from the time the server says is left; the answers this device saved for that
 * session come back. A template whose time ran out shows the server's reason, not a generic error.
 */

const ITEMS = ["uno", "dos"].map((n) => ({
  id: `rs-${n}`,
  content: `Pregunta ${n}`,
  difficulty: 900,
  topic: "Límites",
  options: ["A", "B"],
  image_url: null,
  tags: [],
}));

const TIME_OVER =
  "El tiempo de este examen terminó sin que se enviara; ya no se puede volver a presentar.";

const RESUMED = {
  session_id: "s-rs",
  items: ITEMS,
  n_questions: 2,
  time_limit_seconds: 125,
  course_id: "calculo",
  resumed: true,
};

async function mockStart(page: Page, reply: { status: number; json: unknown }) {
  await page.route("**/api/student/exam/pending", (route) =>
    route.fulfill({ status: 200, json: [] }),
  );
  await page.route("**/api/student/exam/templates*", (route) =>
    route.fulfill({ status: 200, json: [] }),
  );
  await page.route("**/api/student/exam/start", (route) => route.fulfill(reply));
}

test.describe("Examen — retomar un examen iniciado", () => {
  test("en otro dispositivo retoma con el tiempo que queda y lo dice", async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page);
    await mockStart(page, { status: 200, json: RESUMED });

    await page.goto("/student/exam?course=calculo&n=2&t=15");

    await expect(page.getByText("Pregunta uno")).toBeVisible();
    await expect(page.getByRole("status").filter({ hasText: "Retomaste este examen" })).toBeVisible();
    await expect(page.getByRole("timer")).toHaveText(/^0?2:0[0-5]$/);
    await expect(page.getByText("0/2 respondidas").first()).toBeVisible();
  });

  test("en el mismo dispositivo recupera las respuestas guardadas de esa sesión", async ({
    page,
  }) => {
    await mockStudentApi(page);
    await injectAuth(page);
    await mockStart(page, { status: 200, json: RESUMED });
    await page.addInitScript(() => {
      window.localStorage.setItem(
        "levelup-exam-draft",
        JSON.stringify({
          sessionId: "s-rs",
          courseId: "calculo",
          courseName: "Cálculo Diferencial",
          nQuestions: 2,
          timeLimitMin: 15,
          templateId: null,
          items: [
            {
              id: "rs-uno",
              content: "Pregunta uno",
              difficulty: 900,
              topic: "Límites",
              options: ["A", "B"],
              image_url: null,
              tags: [],
            },
          ],
          answers: { "rs-uno": "B" },
          itemTimes: {},
          startedAt: Date.now() - 60_000,
          timeLimitSeconds: 900,
          savedAt: Date.now(),
        }),
      );
    });

    // A draft opens the setup first; the student starts the exam from there.
    await page.goto("/student/exam");
    await page.locator("select").first().selectOption("calculo");
    await page.getByRole("button", { name: "Iniciar examen →" }).click();

    await expect(page.getByText("Pregunta uno")).toBeVisible();
    await expect(page.getByRole("status").filter({ hasText: "Retomaste este examen" })).toBeVisible();
    await expect(page.getByText("1/2 respondidas").first()).toBeVisible();
  });

  test("un examen cuyo tiempo terminó muestra el motivo del servidor", async ({ page }) => {
    await mockStudentApi(page);
    await injectAuth(page);
    await mockStart(page, { status: 409, json: { detail: TIME_OVER } });

    await page.goto("/student/exam?course=calculo&n=2&t=15");

    await expect(page.getByText(TIME_OVER)).toBeVisible();
  });
});
