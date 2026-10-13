import { test, expect } from "./fixtures";
import type { Page, Request } from "@playwright/test";
import { injectAuth, mockStudentApi } from "./helpers/auth";

/**
 * KatIA's chat is a request like any other: when the 15-minute access token has expired, the
 * session is renewed and the question goes through (it showed «Token inválido o expirado»). On
 * the course map it uses the student's own AI key and provider, as practice does.
 */

const SSE = [
  `data: ${JSON.stringify({ token: "¿Qué " })}`,
  `data: ${JSON.stringify({ token: "observas?" })}`,
  `data: ${JSON.stringify({ done: true, full_text: "¿Qué observas?" })}`,
  "",
].join("\n\n");

async function katia(page: Page, expiredFirst: boolean) {
  const calls: Request[] = [];
  await page.route("**/api/ai/socratic", (route) => {
    calls.push(route.request());
    if (expiredFirst && calls.length === 1) {
      return route.fulfill({ status: 401, json: { detail: "Token inválido o expirado" } });
    }
    return route.fulfill({ status: 200, contentType: "text/event-stream", body: SSE });
  });
  return calls;
}

async function ask(page: Page) {
  await page.getByPlaceholder("Escribe tu pregunta a KatIA...").fill("No sé por dónde empezar");
  await page.getByRole("button", { name: "Enviar", exact: true }).click();
}

test.describe("KatIA", () => {
  test("con el token caducado, renueva la sesión y responde", async ({ page }) => {
    await mockStudentApi(page);
    const calls = await katia(page, true);
    let refreshed = 0;
    await page.route("**/api/auth/refresh", (route) => {
      refreshed += 1;
      return route.fulfill({ status: 200, json: { access_token: "renewed-token" } });
    });
    await injectAuth(page);
    await page.goto("/student/courses");
    await page.getByRole("button", { name: /Practicar/ }).first().click();
    await page.getByRole("button", { name: /Ir a practicar/ }).click();
    await page.getByRole("button", { name: /Pregúntale a KatIA/ }).click();

    await ask(page);

    await expect(page.getByText("¿Qué observas?")).toBeVisible();
    expect(refreshed).toBe(1);
    expect(calls.map((c) => c.headers()["authorization"])).toEqual([
      "Bearer fake-test-token",
      "Bearer renewed-token",
    ]);
  });

  test("la petición lleva el ejercicio, el mensaje y el idioma; nunca el enunciado", async ({ page }) => {
    // Spec 005 FR-018: the server reads the exercise from the store; without a key of the
    // student's own the browser names no provider either (FR-027).
    await mockStudentApi(page);
    const calls = await katia(page, false);
    await injectAuth(page);
    await page.goto("/student/courses");
    await page.getByRole("button", { name: /Practicar/ }).first().click();
    await page.getByRole("button", { name: /Ir a practicar/ }).click();
    await page.getByRole("button", { name: /Pregúntale a KatIA/ }).click();

    await ask(page);

    await expect(page.getByText("¿Qué observas?")).toBeVisible();
    const body = calls[0].postDataJSON();
    expect(Object.keys(body).sort()).toEqual(["item_id", "lang", "student_message"]);
    expect(body).toEqual({ item_id: "test-item-1", student_message: "No sé por dónde empezar", lang: "es" });
  });

  const refusals = [
    { status: 403, code: "exam_active", es: "Durante un examen no puedo ayudarte" },
    { status: 409, code: "not_served", es: "solo puedo ayudarte con la pregunta que estás practicando" },
    { status: 403, code: "not_enrolled", es: "un curso en el que no estás inscrito" },
    { status: 422, code: "message_too_long", es: "Escribe tu pregunta en menos palabras" },
    { status: 429, code: null, es: "Hiciste muchas preguntas seguidas" },
  ];
  for (const r of refusals) {
    test(`un rechazo se explica en el chat: ${r.code ?? "429"}`, async ({ page }) => {
      // Spec 005 FR-036: a translated message, never the raw status or the server's detail.
      await mockStudentApi(page);
      await page.route("**/api/ai/socratic", (route) =>
        route.fulfill({
          status: r.status,
          json: r.code
            ? { detail: { code: r.code, message: "texto del servidor" } }
            : { error: "Rate limit exceeded: 10 per 1 minute" },
        }),
      );
      await injectAuth(page);
      await page.goto("/student/courses");
      await page.getByRole("button", { name: /Practicar/ }).first().click();
      await page.getByRole("button", { name: /Ir a practicar/ }).click();
      await page.getByRole("button", { name: /Pregúntale a KatIA/ }).click();

      await ask(page);

      await expect(page.getByText(r.es)).toBeVisible();
      await expect(page.getByText(/texto del servidor|Rate limit|Error 4\d\d/)).toHaveCount(0);
    });
  }

  test("en inglés, el rechazo del examen se explica en inglés", async ({ page }) => {
    await mockStudentApi(page);
    await page.route("**/api/ai/socratic", (route) =>
      route.fulfill({ status: 403, json: { detail: { code: "exam_active", message: "texto" } } }),
    );
    await injectAuth(page);
    await page.addInitScript(() => localStorage.setItem("levelup-lang", "en"));
    await page.goto("/student/courses");
    await page.getByRole("button", { name: /Practi/ }).first().click();
    await page.getByRole("button", { name: /Ir a practicar/ }).click(); // not translated yet
    await page.getByRole("button", { name: /Ask KatIA/ }).click();
    await page.getByPlaceholder("Type your question to KatIA...").fill("Where do I start?");
    await page.getByRole("button", { name: "Send", exact: true }).click();

    await expect(page.getByText("During an exam I can't help you")).toBeVisible();
  });

  test("el examen no ofrece KatIA", async ({ page }) => {
    // Spec 005 FR-026 (pin): the exam screen has no KatIA; the server refuses exam items too.
    await mockStudentApi(page);
    await page.route("**/api/student/exam/start", (route) =>
      route.fulfill({
        status: 200,
        json: {
          session_id: "exam-1",
          course_id: "calculo",
          n_questions: 2,
          time_limit_seconds: 600,
          items: [
            { id: "e1", content: "¿Cuánto es $3 + 4$?", difficulty: 900, topic: "Aritmética", options: ["6", "7", "8"], tags: [] },
            { id: "e2", content: "¿Cuánto es $2 \\cdot 5$?", difficulty: 950, topic: "Aritmética", options: ["10", "7", "25"], tags: [] },
          ],
        },
      }),
    );
    await injectAuth(page);
    await page.goto("/student/exam?course=calculo&n=2&t=10");

    await expect(page.getByText("¿Cuánto es")).toBeVisible();
    // The sidebar's link to the feedback page is named KatIA too; the chat is what must be absent.
    const main = page.locator("main");
    await expect(main.getByRole("button", { name: /KatIA/ })).toHaveCount(0);
    await expect(page.getByPlaceholder("Escribe tu pregunta a KatIA...")).toHaveCount(0);
    await expect(page.locator(".rail-katia")).toHaveCount(0);
  });

  test("en el mapa usa la key y el proveedor del estudiante", async ({ page }) => {
    await mockStudentApi(page);
    await page.route("**/api/student/map/*", (route) =>
      route.fulfill({
        status: 200,
        json: {
          course_id: "calculo",
          course_name: "Cálculo Diferencial",
          diagnostic_done: true,
          nodes: [{ topic: "Límites", label: "Límites", elo: 1100, rd: 200, item_count: 3, state: "available" }],
        },
      }),
    );
    const calls = await katia(page, false);
    await page.addInitScript(() =>
      localStorage.setItem(
        "levelup-settings",
        JSON.stringify({ state: { apiKey: "sk-ant-student-key", provider: "anthropic", model: "" }, version: 0 }),
      ),
    );
    await injectAuth(page);
    await page.goto("/student/course/calculo/map");
    await page.locator(".cd-handle").focus(); // the drawer opens on focus, as on hover
    await page.locator(".rail-katia").click();

    await ask(page);

    await expect(page.getByText("¿Qué observas?")).toBeVisible();
    const body = calls[0].postDataJSON();
    expect([body.api_key, body.provider]).toEqual(["sk-ant-student-key", "anthropic"]);
  });
});
