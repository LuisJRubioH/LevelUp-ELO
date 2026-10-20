import { request as apiRequest, test, expect, type Page } from "@playwright/test";

/**
 * Spec 004 E5, US9-AS5 — US9-AS1 … AS4 against the real API, in each browser of
 * playwright.session.config.ts (WebKit as Safari desktop, iPhone and iPad; Chromium). The page
 * and the API share one origin and the renewal cookie is `SameSite=Lax`, as after the switch
 * (docs/transfer.md § 3.3). Labelled *automated*; real devices are the owner's check.
 */

const STORE = "levelup-auth";

async function signIn(page: Page, username: string, password: string) {
  await page.goto("/login");
  await page.getByLabel("Usuario o correo").fill(username);
  await page.getByLabel("Contraseña").fill(password);
  await page.getByRole("button", { name: /Entrar a Oulad/ }).click();
  await expect(page).toHaveURL(/\/student\/courses$/);
}

/** Replaces the stored access token, as one that expired after its 15 minutes would be. */
async function expireAccessToken(page: Page) {
  await page.evaluate((key) => {
    const stored = JSON.parse(localStorage.getItem(key) ?? "{}");
    stored.state.accessToken = "expired-access-token";
    localStorage.setItem(key, JSON.stringify(stored));
  }, STORE);
}

/** Below 1024 px logout lives in the top bar's "Menú" drawer (iPhone, iPad); above, in the sidebar. */
async function signOut(page: Page) {
  const menu = page.getByRole("button", { name: "Menú" });
  const logout = page.getByRole("button", { name: /Cerrar sesión/ }).first();
  await expect(menu.or(logout).first()).toBeVisible();
  if (await menu.isVisible()) {
    await menu.click();
    await page.locator("#tc-side").getByRole("button", { name: /Cerrar sesión/ }).click();
  } else {
    await logout.click();
  }
}

async function storedAccessToken(page: Page): Promise<string | null> {
  return page.evaluate(
    (key) => JSON.parse(localStorage.getItem(key) ?? "{}").state?.accessToken ?? null,
    STORE,
  );
}

test.describe("Spec 004 E5 · sesión en el navegador real", () => {
  test("un access token vencido se renueva con la cookie del mismo origen (spec 004 US9-AS1)", async ({
    page,
    baseURL,
  }) => {
    await signIn(page, "estudiante1", "demo1234");
    await expireAccessToken(page);

    const renewal = page.waitForResponse((r) => r.url().endsWith("/api/auth/refresh"));
    await page.reload();

    const response = await renewal;
    expect(new URL(response.url()).origin).toBe(new URL(baseURL!).origin);
    expect(response.status()).toBe(200);
    await expect(page).toHaveURL(/\/student\/courses$/);
    await expect.poll(() => storedAccessToken(page)).not.toBe("expired-access-token");
    expect(await storedAccessToken(page)).not.toBeNull();
  });

  test("recargar la página conserva la sesión (spec 004 US9-AS2)", async ({ page }) => {
    await signIn(page, "estudiante1", "demo1234");

    await page.reload();

    await expect(page).toHaveURL(/\/student\/courses$/);
    await page.goto("/student/courses");
    await expect(page).toHaveURL(/\/student\/courses$/);
  });

  test("cerrar sesión borra la cookie y una recarga pide entrar (spec 004 US9-AS3)", async ({
    page,
  }) => {
    await signIn(page, "estudiante1", "demo1234");

    await signOut(page);
    await expect(page).toHaveURL(/\/login$/);
    await page.reload();
    await expect(page).toHaveURL(/\/login$/);
    await page.goto("/student/courses");
    await expect(page).toHaveURL(/\/login$/);

    // The browser no longer holds a renewal cookie: renewing from this context is refused.
    const renew = await page.request.post("/api/auth/refresh");
    expect(renew.status()).toBe(401);
  });

  test("cambiar la contraseña en otro navegador cierra esta sesión (spec 004 US9-AS4, FR-084)", async ({
    page,
    baseURL,
  }, testInfo) => {
    // One seeded account per browser: the password changes for good in this run's database.
    const accounts: Record<string, string> = {
      "safari-desktop": "estudiante_colegio_1",
      "safari-iphone": "estudiante_colegio_2",
      "safari-ipad": "estudiante_colegio_3",
      "chrome-desktop": "estudiante_universidad_1",
    };
    const username = accounts[testInfo.project.name];
    expect(username, `sin cuenta para ${testInfo.project.name}`).toBeTruthy();
    await signIn(page, username, "test1234");

    const other = await apiRequest.newContext({ baseURL, ignoreHTTPSErrors: true });
    const login = await other.post("/api/auth/login", {
      data: { username, password: "test1234" },
    });
    expect(login.status()).toBe(200);
    const { access_token } = await login.json();
    const changed = await other.post("/api/auth/password", {
      headers: { Authorization: `Bearer ${access_token}` },
      data: { current_password: "test1234", new_password: "otra-clave-segura-2026" },
    });
    expect(changed.status()).toBe(200);
    await other.dispose();

    await page.reload();

    await expect(page).toHaveURL(/\/login$/);
  });
});
