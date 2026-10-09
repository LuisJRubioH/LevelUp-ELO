/**
 * Spec 001, follow-up F-1 (FR-028l, FR-028o; US7-AS5, US7-AS6; task T099): the courses screen
 * for a semillero student without a grade, and courses reached by invitation. The API is mocked:
 * these check what the screen does with `in_catalogue` and the student's grade.
 */
import { test, expect, type Page } from "@playwright/test";
import { injectAuth, mockStudentApi, MOCK_STUDENT } from "./helpers/auth";

const NOTICE =
  "Necesitamos registrar tu grado para mostrar tus cursos. Contacta a tu docente o al administrador.";

async function openCourses(page: Page, user: typeof MOCK_STUDENT, courses: object[]) {
  await mockStudentApi(page);
  await page.route("**/api/student/courses", (route) => route.fulfill({ json: courses }));
  await injectAuth(page, user);
  await page.goto("/student/courses");
}

const card = (page: Page, name: string) => page.locator("article").filter({ hasText: name });

test.describe("Catálogo por nivel y grado (F-1)", () => {
  test("Semillero sin grado: aviso, sin catálogo y con sus matrículas abiertas (FR-028o)", async ({
    page,
  }) => {
    await openCourses(page, { ...MOCK_STUDENT, education_level: "semillero", grade: null }, [
      {
        id: "algebra_semillero_6",
        name: "Álgebra 6°",
        block: "Semillero",
        enrolled: true,
        in_catalogue: false,
      },
    ]);

    await expect(page.getByText(NOTICE)).toBeVisible();
    await expect(page.locator("article")).toHaveCount(0);

    await page.getByRole("button", { name: /Mis matrículas/ }).click();
    await expect(page.getByText(NOTICE)).toBeVisible();
    await expect(card(page, "Álgebra 6°").getByRole("button", { name: /Practicar/ })).toBeVisible();
  });

  test("Semillero con grado: sin aviso (FR-028o)", async ({ page }) => {
    await openCourses(page, { ...MOCK_STUDENT, education_level: "semillero", grade: "6" }, [
      {
        id: "algebra_semillero_6",
        name: "Álgebra 6°",
        block: "Semillero",
        enrolled: false,
        in_catalogue: true,
      },
    ]);

    await expect(card(page, "Álgebra 6°")).toBeVisible();
    await expect(page.getByText(NOTICE)).toHaveCount(0);
  });

  test("Un curso por invitación solo aparece en Mis matrículas (FR-028l)", async ({ page }) => {
    await openCourses(page, MOCK_STUDENT, [
      { id: "algebra_basica", name: "Álgebra Básica", block: "Colegio", enrolled: false, in_catalogue: true },
      {
        id: "calculo_diferencial",
        name: "Cálculo Diferencial",
        block: "Universidad",
        enrolled: true,
        in_catalogue: false,
        group_id: 7,
      },
    ]);

    await expect(card(page, "Álgebra Básica")).toBeVisible();
    await expect(card(page, "Cálculo Diferencial")).toHaveCount(0);

    await page.getByRole("button", { name: /Mis matrículas/ }).click();
    const invited = card(page, "Cálculo Diferencial");
    await expect(invited).toBeVisible();
    await expect(invited.getByText("Acceso por invitación")).toBeVisible();
    await expect(invited.getByRole("button", { name: /Practicar/ })).toBeVisible();
    await expect(card(page, "Álgebra Básica")).toHaveCount(0);
  });
});
