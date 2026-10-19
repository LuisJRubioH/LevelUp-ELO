import { test, expect } from "./fixtures";
import type { Page, Request } from "@playwright/test";
import { injectAuth, mockStudentApi } from "./helpers/auth";

/**
 * KatIA's chat is a request like any other: when the 15-minute access token has expired, the
 * session is renewed and the question goes through (it showed «Token inválido o expirado»). On
 * the course map it uses the student's own AI key, as practice does; the server picks the provider
 * from it (spec 005 FR-011: the browser sends none).
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
    expect(body.api_key).toBe("sk-ant-student-key");
    expect(body.provider).toBeUndefined();
  });
});
