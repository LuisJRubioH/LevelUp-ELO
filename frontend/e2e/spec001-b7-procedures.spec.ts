import { test, expect } from "./fixtures";
import type { Page } from "@playwright/test";
import { injectAuth, mockStudentApi, MOCK_TEACHER } from "./helpers/auth";

/**
 * Spec 001, block 7 (tasks-b7.md T019–T021): a grading's rating effect is the amount applied,
 * never the computed delta (FR-024f); a copy of another student's file is graded 0 and marked
 * (FR-024i); the student's own file again is refused with its reason (FR-024j, FR-024k).
 */

const PNG = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
  "base64",
);

const graded = (overrides: Record<string, unknown>) => ({
  submission_id: 1,
  item_id: "calc_q1",
  item_content: "Deriva $x^2$",
  status: "VALIDATED_BY_TEACHER",
  ai_proposed_score: null,
  teacher_score: 30,
  final_score: 30,
  teacher_feedback: null,
  elo_delta: -10,
  computed_delta: -4,
  contribution: -4,
  is_copy: false,
  submitted_at: "2026-10-18 10:00:00",
  reviewed_at: "2026-10-18 11:00:00",
  ...overrides,
});

async function openStudent(page: Page, path: string, submissions: unknown[]) {
  await mockStudentApi(page);
  await page.route("**/api/student/procedures", (route) =>
    route.fulfill({ json: { submissions } }),
  );
  await page.route("**/api/student/ai-status", (route) =>
    route.fulfill({ json: { available: false, provider: null } }),
  );
  await injectAuth(page);
  await page.goto(path);
}

test.describe("Bloque 7 — lo que ve el estudiante", () => {
  test("la tarjeta muestra lo aplicado, no el delta calculado, y marca la copia", async ({ page }) => {
    await openStudent(page, "/student/feedback", [
      graded({}),
      graded({
        submission_id: 2,
        item_id: "calc_q2",
        teacher_score: 0,
        final_score: 0,
        elo_delta: -3,
        computed_delta: -10,
        contribution: -3,
        is_copy: true,
      }),
    ]);

    const first = page.locator("article").filter({ hasText: "calc_q1" });
    await expect(first.getByText("-10.0")).toBeVisible();
    await expect(first.getByText("-4.0")).toHaveCount(0);
    await expect(first.getByText("Copia detectada")).toHaveCount(0);

    const copy = page.locator("article").filter({ hasText: "calc_q2" });
    await expect(copy.getByText("-3.0")).toBeVisible();
    await expect(copy.getByText("Copia detectada")).toBeVisible();
  });

  async function uploadAndSend(page: Page) {
    await page.getByPlaceholder("ej: ejercicio_1, taller_3_p5, parcial_2_p3").fill("calc_q1");
    await page.locator('input[type="file"]').setInputFiles({
      name: "work.png",
      mimeType: "image/png",
      buffer: PNG,
    });
    await page.getByRole("button", { name: "📤 Enviar al docente" }).click();
  }

  test("una copia queda calificada con 0 y lo dice", async ({ page }) => {
    await openStudent(page, "/student/procedure", []);
    await page.route("**/api/student/procedure", (route) =>
      route.fulfill({
        json: {
          submission_id: 9,
          ai_score: null,
          ai_feedback: null,
          status: "graded",
          is_copy: true,
          teacher_score: 0,
          elo_delta: -10,
        },
      }),
    );

    await uploadAndSend(page);

    await expect(
      page.getByText(
        "Este archivo ya lo había entregado otro estudiante. El procedimiento quedó calificado con 0 y marcado como copia.",
      ),
    ).toBeVisible();
    await expect(page.getByText("Procedimiento enviado")).toHaveCount(0);
  });

  for (const detail of [
    "Ya subiste este archivo para este ejercicio.",
    "Este archivo pertenece a otro ejercicio.",
  ]) {
    test(`un archivo propio repetido se rechaza: «${detail}»`, async ({ page }) => {
      await openStudent(page, "/student/procedure", []);
      await page.route("**/api/student/procedure", (route) =>
        route.fulfill({ status: 409, json: { detail } }),
      );

      await uploadAndSend(page);

      await expect(page.getByText(`No se pudo enviar: ${detail}`)).toBeVisible();
    });
  }
});

const PENDING = {
  submission_id: 7,
  student_id: 11,
  student_name: "Ana Gómez",
  item_id: "calc_q1",
  item_content: "Deriva $x^2$",
  ai_score: null,
  status: "pending",
  created_at: "2026-10-18 12:00:00",
  has_image: false,
  review_round: 2,
};

test.describe("Bloque 7 — lo que ve el docente", () => {
  test("al calificar ve lo aplicado y envía la ronda de revisión; las copias aparecen marcadas", async ({
    page,
  }) => {
    let graded = false;
    let body: Record<string, unknown> = {};
    await page.route("**/api/teacher/**", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "[]" }),
    );
    await page.route("**/api/teacher/procedures", (route) =>
      route.fulfill({ json: graded ? [] : [PENDING] }),
    );
    await page.route("**/api/teacher/procedures/copies", (route) =>
      route.fulfill({
        json: [
          {
            submission_id: 12,
            student_id: 13,
            student_name: "Bruno Díaz",
            item_id: "calc_q3",
            item_content: null,
            reviewed_at: "2026-10-18 09:00:00",
          },
        ],
      }),
    );
    await page.route("**/api/teacher/procedures/grade", async (route) => {
      body = route.request().postDataJSON();
      graded = true;
      await route.fulfill({
        json: {
          submission_id: 7,
          teacher_score: 30,
          elo_delta: -10,
          computed_delta: -4,
          contribution: -4,
          review_round: 2,
          status: "graded",
        },
      });
    });
    await page.route("**/api/student/exam/pending", (route) => route.fulfill({ json: [] }));
    await injectAuth(page, MOCK_TEACHER);
    await page.goto("/teacher/procedures");

    const copies = page.getByRole("region", { name: "Copias detectadas" });
    await expect(copies.getByText("Bruno Díaz")).toBeVisible();
    await expect(copies.getByText("Calificado 0 automáticamente")).toBeVisible();

    await page.getByRole("button", { name: "0", exact: true }).click();
    await page.getByRole("button", { name: /Guardar calificación/ }).click();

    await expect(page.getByRole("status")).toHaveText(
      "Calificación guardada · Ana Gómez: efecto en la nota −10",
    );
    expect(body.review_round).toBe(2);
  });

  test("si el estudiante reenvió, el docente lo ve y la cola se recarga con el envío nuevo", async ({
    page,
  }) => {
    // Spec 001 FR-024l (US9-AS14): the round on screen was replaced by a resubmission.
    let round = 1;
    const gradeBodies: Record<string, unknown>[] = [];
    const imageRequests: string[] = [];
    await page.route("**/api/teacher/**", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "[]" }),
    );
    await page.route("**/api/teacher/procedures", (route) =>
      route.fulfill({ json: [{ ...PENDING, has_image: true, review_round: round }] }),
    );
    await page.route("**/api/teacher/procedures/7/image", (route) => {
      imageRequests.push(`round ${round}`);
      return route.fulfill({ status: 200, contentType: "image/png", body: PNG });
    });
    await page.route("**/api/teacher/procedures/grade", async (route) => {
      const body = route.request().postDataJSON();
      gradeBodies.push(body);
      if (body.review_round === 1) {
        round = 2; // the student resubmitted while the teacher had round 1 open
        return route.fulfill({
          status: 409,
          json: {
            detail:
              "El estudiante reenvió este procedimiento; revisa el envío nuevo antes de calificar.",
          },
        });
      }
      return route.fulfill({
        json: {
          submission_id: 7,
          teacher_score: 80,
          elo_delta: 6,
          computed_delta: 6,
          contribution: 6,
          review_round: 2,
          status: "graded",
        },
      });
    });
    await page.route("**/api/student/exam/pending", (route) => route.fulfill({ json: [] }));
    await injectAuth(page, MOCK_TEACHER);
    await page.goto("/teacher/procedures");

    await expect(page.getByAltText("Procedimiento manuscrito del estudiante")).toBeVisible();
    await page.getByRole("button", { name: "80", exact: true }).click();
    await page.getByRole("button", { name: /Guardar calificación/ }).click();

    await expect(
      page.getByText(
        "El estudiante reenvió este procedimiento; revisa el envío nuevo antes de calificar.",
      ),
    ).toBeVisible();
    // The queue reloads and the new submission's file is fetched, not the cached one.
    await expect.poll(() => imageRequests).toEqual(["round 1", "round 2"]);

    await page.getByRole("button", { name: /Guardar calificación/ }).click();
    await expect(page.getByRole("status")).toHaveText(
      "Calificación guardada · Ana Gómez: efecto en la nota +6",
    );
    expect(gradeBodies.map((b) => b.review_round)).toEqual([1, 2]);
  });
});
