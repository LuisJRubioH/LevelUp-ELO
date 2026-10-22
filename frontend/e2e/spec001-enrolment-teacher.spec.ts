/**
 * Spec 001 delivery TCH (FR-028w; US11-AS3): no enrolment without a teacher, on the courses
 * screen. The API is mocked: these check what the screen does with `enrollable` and with a
 * refused enrolment.
 */
import type { Page } from "@playwright/test";
import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi, MOCK_STUDENT } from "./helpers/auth";

const REFUSAL = "Pide a tu docente una invitación para este curso.";

async function openCourses(page: Page, courses: object[]) {
  await mockStudentApi(page);
  await page.route("**/api/student/courses", (route) => route.fulfill({ json: courses }));
  await injectAuth(page, MOCK_STUDENT);
  await page.goto("/student/courses");
}

const card = (page: Page, name: string) => page.locator("article").filter({ hasText: name });

test.describe("Ninguna matrícula sin docente (TCH)", () => {
  test("Matricularme solo donde el docente del grupo revisa el curso; si no, la invitación (US11-AS3, FR-028w)", async ({
    page,
  }) => {
    await openCourses(page, [
      { id: "algebra_basica", name: "Álgebra Básica", block: "Colegio", enrolled: false, in_catalogue: true, enrollable: true },
      { id: "geometria_basica", name: "Geometría Básica", block: "Colegio", enrolled: false, in_catalogue: true, enrollable: false },
    ]);

    const open = card(page, "Álgebra Básica");
    await expect(open.getByRole("button", { name: "Matricularme" })).toBeVisible();
    await expect(open.getByText("Con invitación de tu docente")).toHaveCount(0);

    const closed = card(page, "Geometría Básica");
    await expect(closed.getByRole("button", { name: "Matricularme" })).toHaveCount(0);
    await expect(closed.getByText("Con invitación de tu docente")).toBeVisible();
    await closed.getByRole("button", { name: "Usar un código" }).click();
    await expect(page.getByRole("textbox", { name: "Acceder con código" })).toBeVisible();
  });

  test("Una matrícula rechazada muestra el mensaje del servidor (FR-028w)", async ({ page }) => {
    await openCourses(page, [
      { id: "algebra_basica", name: "Álgebra Básica", block: "Colegio", enrolled: false, in_catalogue: true, enrollable: true },
    ]);
    await page.route("**/api/student/enroll", (route) =>
      route.fulfill({ status: 403, json: { detail: REFUSAL } }),
    );

    await card(page, "Álgebra Básica").getByRole("button", { name: "Matricularme" }).click();

    await expect(page.getByText(REFUSAL)).toBeVisible();
  });
});
