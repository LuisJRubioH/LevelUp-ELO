import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi } from "./helpers/auth";
import type { Page } from "@playwright/test";

/**
 * Spec 005 K1 (FR-011, FR-014): the browser offers no provider or model picker — the key's
 * prefix decides on the server — and the procedure review, which runs on Groq only, says so
 * before the upload when the key in use is another provider's.
 */
async function withKey(page: Page, apiKey: string, system: { available: boolean; provider: string | null }) {
  await mockStudentApi(page);
  await page.route("**/api/student/ai-status", (route) => route.fulfill({ json: system }));
  await page.route("**/api/student/procedures", (route) => route.fulfill({ json: { submissions: [] } }));
  await page.addInitScript((key) => {
    localStorage.setItem("levelup-settings", JSON.stringify({ state: { apiKey: key }, version: 1 }));
  }, apiKey);
  await injectAuth(page);
}

test.describe("Spec 005 K1 — una key, su proveedor", () => {
  test("no hay selector de proveedor ni de modelo", async ({ page }) => {
    await withKey(page, "", { available: true, provider: "groq" });
    await page.goto("/student/procedure");
    await expect(page.getByRole("button", { name: /Analizar con IA/ })).toBeVisible();

    // The key field stays; nothing offers a provider or a model.
    await expect(page.getByPlaceholder("Tu API key (opcional)")).toHaveCount(1);
    await expect(page.locator('select[aria-label*="Proveedor"], select[aria-label*="Modelo"]')).toHaveCount(0);
    await expect(page.locator('option[value="anthropic"]')).toHaveCount(0);
  });

  test("con una key que no es de Groq, la revisión dice que usa Groq y no se ofrece", async ({ page }) => {
    await withKey(page, "sk-ant-student-key", { available: true, provider: "groq" });
    await page.goto("/student/procedure");

    await expect(page.getByText("La revisión con IA usa Groq")).toBeVisible();
    await expect(page.getByRole("button", { name: /Analizar con IA/ })).toHaveCount(0);
  });

  test("con la key del sistema de Groq, la revisión se ofrece", async ({ page }) => {
    await withKey(page, "", { available: true, provider: "groq" });
    await page.goto("/student/procedure");

    await expect(page.getByText("La revisión con IA usa Groq")).toHaveCount(0);
    await expect(page.getByRole("button", { name: /Analizar con IA/ })).toBeVisible();
  });
});
