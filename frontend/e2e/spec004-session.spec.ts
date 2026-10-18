import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi } from "./helpers/auth";

/**
 * Spec 004, delivery E5 — session renewal on screen (US9): an expired access token renews by
 * itself through the page's own origin, a reload keeps the session, logout ends it, and a refused
 * renewal sends the user to sign in. Chromium here; Safari on real devices is the owner's check
 * (US9-AS5).
 */

test.describe("Spec 004 · renovación de sesión", () => {
  test("un access token vencido se renueva solo, por el mismo origen (spec 004 US9-AS1)", async ({
    page,
    baseURL,
  }) => {
    await injectAuth(page);
    await mockStudentApi(page);
    const refreshUrls: string[] = [];
    await page.route("**/api/auth/refresh", (route) => {
      refreshUrls.push(route.request().url());
      return route.fulfill({
        status: 200,
        json: {
          access_token: "renewed-token",
          token_type: "bearer",
          expires_in: 900,
          user_id: 1,
          username: "estudiante1",
          role: "student",
        },
      });
    });
    const seen: string[] = [];
    await page.route("**/api/student/courses", (route) => {
      const auth = route.request().headers()["authorization"] ?? "";
      seen.push(auth);
      if (auth === "Bearer fake-test-token") {
        return route.fulfill({ status: 401, json: { detail: "Token inválido o expirado." } });
      }
      return route.fallback();
    });

    await page.goto("/student/courses");

    await expect(page.getByText("Cálculo Diferencial").first()).toBeVisible();
    expect(seen).toContain("Bearer fake-test-token");
    expect(seen).toContain("Bearer renewed-token");
    expect(refreshUrls.length).toBeGreaterThan(0);
    for (const url of refreshUrls) expect(new URL(url).origin).toBe(new URL(baseURL!).origin);
  });

  test("recargar la página conserva la sesión (spec 004 US9-AS2)", async ({ page }) => {
    await injectAuth(page);
    await mockStudentApi(page);

    await page.goto("/student/courses");
    await expect(page.getByText("Cálculo Diferencial").first()).toBeVisible();
    await page.reload();

    await expect(page).toHaveURL("/student/courses");
    await expect(page.getByText("Cálculo Diferencial").first()).toBeVisible();
  });

  test("cerrar sesión la termina y pide entrar de nuevo (spec 004 US9-AS3)", async ({ page }) => {
    await injectAuth(page);
    await mockStudentApi(page);
    let loggedOut = 0;
    await page.route("**/api/auth/logout", (route) => {
      loggedOut += 1;
      return route.fulfill({ status: 204 });
    });

    await page.goto("/student/courses");
    await page.getByRole("button", { name: /Cerrar sesión/ }).first().click();

    await expect(page).toHaveURL("/login");
    expect(loggedOut).toBe(1);
    // injectAuth re-seeds storage on every navigation, so read what logout left instead.
    const stored = await page.evaluate(() => JSON.parse(localStorage.getItem("levelup-auth") ?? "{}"));
    expect(stored.state?.accessToken ?? null).toBeNull();
    expect(stored.state?.isAuthenticated ?? false).toBe(false);
  });

  test("si la renovación se rechaza, la app pide entrar de nuevo (spec 004 US9-AS4, FR-084)", async ({
    page,
  }) => {
    await injectAuth(page);
    await mockStudentApi(page);
    await page.route("**/api/student/**", (route) =>
      route.fulfill({ status: 401, json: { detail: "Tu sesión terminó porque la contraseña cambió." } }),
    );
    await page.route("**/api/auth/refresh", (route) =>
      route.fulfill({ status: 401, json: { detail: "Tu sesión terminó porque la contraseña cambió." } }),
    );

    await page.goto("/student/courses");

    await expect(page).toHaveURL("/login");
  });
});
