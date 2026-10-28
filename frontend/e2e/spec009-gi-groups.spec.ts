import type { Page, Request } from "@playwright/test";
import { test, expect } from "./fixtures";
import { injectAuth } from "./helpers/auth";

/**
 * Spec 009, delivery GI — on screen: the admin sees how many groups have no institution, shows only
 * those, opens one, picks a recorded institution and a grade and saves; the row shows them and the
 * count drops (US4-AS1, US4-AS5, FR-022, T013). Another group with the same institution and grade
 * is named before saving, and «Guardar de todos modos» saves (US4-AS6, FR-024, T014).
 */

const MOCK_ADMIN = {
  user_id: 3,
  username: "admin",
  role: "admin" as const,
  education_level: null,
  grade: null,
  email: null,
};

interface Group {
  id: number;
  name: string;
  teacher_id: number;
  teacher_name: string;
  student_count: number;
  institution: string | null;
  grade: number | null;
}

const INSTITUTION = "Colegio San José";

function seed(): Group[] {
  return [
    { id: 7, name: "Grupo 9A", teacher_id: 2, teacher_name: "profesor1", student_count: 23, institution: null, grade: null },
    { id: 8, name: "Grupo 10B", teacher_id: 2, teacher_name: "profesor1", student_count: 18, institution: "  ", grade: null },
    { id: 9, name: "Grupo 6A", teacher_id: 4, teacher_name: "profesor2", student_count: 30, institution: INSTITUTION, grade: 9 },
  ];
}

const blank = (g: Group) => !(g.institution ?? "").trim();

/** The server as the screen sees it: the list, its filter and count, and the recorded names. */
async function openGroups(page: Page, groups: Group[], onPut: (request: Request) => { status: number; json: unknown }) {
  await page.route(/\/api\/admin\/groups(\?.*)?$/, (route) => {
    const only = new URL(route.request().url()).searchParams.get("without_institution") === "true";
    const shown = only ? groups.filter(blank) : groups;
    return route.fulfill({
      json: { groups: shown, count: shown.length, without_institution: groups.filter(blank).length },
    });
  });
  await page.route("**/api/admin/institutions", (route) =>
    route.fulfill({ json: { institutions: [{ institution: INSTITUTION, groups: 1 }] } }),
  );
  await page.route(/\/api\/admin\/groups\/\d+\/institution$/, (route) => {
    const answer = onPut(route.request());
    return route.fulfill(answer);
  });
  await injectAuth(page, MOCK_ADMIN);
  await page.goto("/admin/groups");
}

function save(groups: Group[], request: Request) {
  const id = Number(request.url().match(/groups\/(\d+)\/institution/)![1]);
  const body = request.postDataJSON() as { institution: string; grade: number | null };
  const group = groups.find((g) => g.id === id)!;
  group.institution = body.institution.trim().split(/\s+/).join(" ");
  group.grade = body.grade;
  return {
    status: 200,
    json: {
      group_id: id,
      institution: group.institution,
      grade: group.grade,
      unchanged: false,
      students_with_other_grade: 2,
    },
  };
}

const row = (page: Page, name: string) => page.getByRole("row").filter({ hasText: name });

test.describe("Spec 009 GI · institución y grado de un grupo", () => {
  test("editar la institución y el grado de un grupo sin institución (US4-AS1, US4-AS5)", async ({
    page,
  }) => {
    const groups = seed();
    const puts: Request[] = [];
    await openGroups(page, groups, (request) => {
      puts.push(request);
      return save(groups, request);
    });

    const toggle = page.getByLabel("Solo grupos sin institución (2)");
    await expect(toggle).toBeVisible();
    await expect(row(page, "Grupo 6A")).toContainText(INSTITUTION);
    await toggle.check();
    await expect(row(page, "Grupo 6A")).toHaveCount(0);
    await expect(row(page, "Grupo 9A")).toBeVisible();
    await expect(row(page, "Grupo 10B")).toBeVisible();

    await row(page, "Grupo 9A").getByRole("button", { name: "Editar institución" }).click();
    const institution = page.getByLabel("Institución", { exact: true });
    // The recorded spelling is offered, so the admin does not type a new variant.
    await expect(page.locator(`datalist option[value="${INSTITUTION}"]`)).toHaveCount(1);
    await institution.fill(INSTITUTION);
    await page.getByLabel("Grado", { exact: true }).selectOption({ label: "9.º" });
    await page.getByRole("button", { name: "Guardar", exact: true }).click();

    // The status appears only once the PUT has been answered, so the request is recorded by then.
    await expect(page.getByRole("status")).toContainText(
      "2 estudiantes de este grupo tienen otro grado; no se cambia el suyo.",
    );
    expect(puts).toHaveLength(1);
    expect(puts[0].postDataJSON()).toEqual({ institution: INSTITUTION, grade: 9, confirm_same: false });
    // Only the group without institution is left, and the count drops by one.
    await expect(page.getByLabel("Solo grupos sin institución (1)")).toBeChecked();
    await expect(row(page, "Grupo 9A")).toHaveCount(0);
    await page.getByLabel("Solo grupos sin institución (1)").uncheck();
    await expect(row(page, "Grupo 9A")).toContainText(INSTITUTION);
    await expect(row(page, "Grupo 9A")).toContainText("9.º");
  });

  test("la misma institución y grado pide confirmación (US4-AS6)", async ({ page }) => {
    const groups = seed();
    const puts: Request[] = [];
    await openGroups(page, groups, (request) => {
      puts.push(request);
      if (!(request.postDataJSON() as { confirm_same: boolean }).confirm_same) {
        return {
          status: 409,
          json: {
            detail: {
              code: "same_institution_and_grade",
              groups: [{ id: 9, name: "Grupo 6A", teacher: "profesor2" }],
            },
          },
        };
      }
      return save(groups, request);
    });

    await row(page, "Grupo 9A").getByRole("button", { name: "Editar institución" }).click();
    await page.getByLabel("Institución", { exact: true }).fill("colegio san jose");
    await page.getByLabel("Grado", { exact: true }).selectOption({ label: "9.º" });
    await page.getByRole("button", { name: "Guardar", exact: true }).click();

    const warning = page.getByRole("alert");
    await expect(warning).toContainText("Grupo 6A");
    await expect(warning).toContainText("profesor2");
    expect(puts).toHaveLength(1);
    await expect(row(page, "Grupo 9A")).not.toContainText("colegio san jose");

    await page.getByRole("button", { name: "Guardar de todos modos" }).click();
    await expect(row(page, "Grupo 9A")).toContainText("colegio san jose");
    expect(puts).toHaveLength(2);
    expect(puts[1].postDataJSON()).toEqual({ institution: "colegio san jose", grade: 9, confirm_same: true });
  });
});
