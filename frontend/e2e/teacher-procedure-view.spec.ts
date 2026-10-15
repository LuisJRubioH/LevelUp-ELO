import { test, expect } from "./fixtures";
import type { Page } from "@playwright/test";
import { injectAuth, MOCK_TEACHER } from "./helpers/auth";

/**
 * The teacher sees the submission as the student sent it: a PDF in a document viewer (an <img>
 * showed it broken), a photo as an image; and the exercise with its formulas rendered (D5).
 */

// The smallest PDF a viewer accepts: one empty page.
const PDF = Buffer.from(
  "%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n" +
    "3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n",
);
// A 1×1 PNG.
const PNG = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
  "base64",
);

const PROCEDURE = {
  submission_id: 7,
  student_id: 11,
  student_name: "ana_g",
  item_id: "calc_q1",
  item_content: "Calcula $\\frac{1}{2} + \\frac{1}{3}$",
  ai_score: null,
  status: "PENDING_TEACHER_VALIDATION",
  created_at: "2026-10-10 12:00:00",
  has_image: true,
};

async function openQueue(page: Page, file: { body: Buffer; contentType: string }) {
  await page.route("**/api/teacher/**", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "[]" }),
  );
  await page.route("**/api/teacher/procedures", (route) =>
    route.fulfill({ status: 200, json: [PROCEDURE] }),
  );
  await page.route("**/api/teacher/procedures/7/image", (route) =>
    route.fulfill({ status: 200, contentType: file.contentType, body: file.body }),
  );
  await page.route("**/api/student/exam/pending", (route) => route.fulfill({ status: 200, json: [] }));
  await injectAuth(page, MOCK_TEACHER);
  await page.goto("/teacher/procedures");
}

test.describe("Procedimientos — lo que envió el estudiante", () => {
  test("un PDF se muestra como documento, no como imagen rota", async ({ page }) => {
    await openQueue(page, { body: PDF, contentType: "application/pdf" });

    await expect(page.locator(".pd-pdf")).toBeVisible();
    await expect(page.getByRole("link", { name: "Abrir el PDF" })).toBeVisible();
    await expect(page.locator("img.pd-image")).toHaveCount(0);
  });

  test("una foto se sigue mostrando como imagen", async ({ page }) => {
    await openQueue(page, { body: PNG, contentType: "image/png" });

    await expect(page.locator("img.pd-image")).toBeVisible();
    await expect(page.locator(".pd-pdf")).toHaveCount(0);
  });

  test("el ejercicio muestra sus fórmulas", async ({ page }) => {
    await openQueue(page, { body: PNG, contentType: "image/png" });

    await expect(page.locator(".pd-problem .katex")).toHaveCount(1);
    await expect(page.locator(".pd-problem .katex .mfrac")).toHaveCount(2);
    await expect(page.locator(".pd-problem .katex-error")).toHaveCount(0);
  });
});
