import type { Page, Request } from "@playwright/test";
import { test, expect } from "./fixtures";
import { injectAuth, MOCK_STUDENT } from "./helpers/auth";

/**
 * Spec 009, delivery I1 — on screen: the admin uploads the form's export, maps its columns
 * (suggested from the form's headers), chooses the batch, reads the preview with each status and
 * reason, confirms and follows the import to its result (US1-AS1, US1-AS2, US1-AS10, T020, T024);
 * a changed preview asks for a new one and changes to existing accounts need their own check box
 * (FR-003, US1-AS6, T021); the admin links and unlinks an identification from the users list
 * (US1-AS5, FR-017, T022) and creates a group for a teacher (N25); the student sees their own
 * identification and, for an imported account, a read-only name (US2-AS1, US3-AS2, T023).
 * Invented identifications only.
 */

const MOCK_ADMIN = {
  user_id: 9,
  username: "admin",
  role: "admin" as const,
  education_level: null,
  grade: null,
  email: null,
};

const HEADER = [
  "Marca temporal",
  "Número de documento",
  "Nombres",
  "Apellidos",
  "Grado que cursas en 2027",
  "Institución educativa",
  "Sede",
  "Correo electrónico de contacto",
];
const SUGGESTED = {
  identification: "Número de documento",
  name: ["Nombres", "Apellidos"],
  grade: "Grado que cursas en 2027",
  institution: "Institución educativa",
  recovery_email: "Correo electrónico de contacto",
};
const GROUPS = [
  { id: 4, name: "Semillero 9", teacher_id: 2, teacher_name: "profesor1", student_count: 0, institution: "Colegio Inventado", grade: 9 },
  { id: 5, name: "Semillero 10", teacher_id: 2, teacher_name: "profesor1", student_count: 3, institution: "Colegio Inventado", grade: 10 },
];
const ROW = {
  reasons: [],
  level: "semillero",
  grade: 9,
  group_id: 4,
  recovery_email: null,
  account_id: null,
  changes: {},
};
const PREVIEW = {
  rows: [
    { ...ROW, row: 2, status: "new", identification: "7700000001", display_name: "Ana Pérez" },
    {
      ...ROW,
      row: 3,
      status: "existing",
      identification: "7700000002",
      display_name: "Luis Gómez",
      account_id: 31,
      changes: { group_id: { from: 5, to: 4 } },
    },
    { ...ROW, row: 4, status: "duplicate", identification: "7700000001", display_name: "Ana Pérez" },
    { ...ROW, row: 5, status: "error", identification: "7700000003", display_name: null, reasons: ["name_missing"] },
  ],
  counts: { new: 1, existing: 1, duplicate: 1, error: 1 },
  pairs: [{ institution: "Colegio Inventado", grade: 9, group_id: 4, suggested_group_id: 4 }],
  digest: "digest-1",
};

const json = (page: Page, url: string, body: unknown, status = 200) =>
  page.route(url, (route) => route.fulfill({ status, json: body }));

/** A multipart field's value, as the browser sent it. */
function field(request: Request, name: string): string | null {
  const body = request.postData() ?? "";
  const match = body.match(new RegExp(`name="${name}"\\r\\n\\r\\n([^\\r]*)`));
  return match ? match[1] : null;
}

async function importPage(page: Page) {
  await json(page, "**/api/admin/groups", { groups: GROUPS });
  await json(page, "**/api/admin/imports/columns", {
    header: HEADER,
    examples: [["2026/10/18", "7700000001", "Ana", "Pérez", "Noveno", "Colegio Inventado", "Principal", ""]],
    rows: 4,
    suggested: SUGGESTED,
  });
  await injectAuth(page, MOCK_ADMIN);
  await page.goto("/admin/import");
  await page.getByLabel("Archivo del formulario").setInputFiles({
    name: "respuestas.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(HEADER.join(",") + "\n"),
  });
}

test.describe("Spec 009 · importación inicial de estudiantes", () => {
  test("subir, mapear, ver la vista previa, confirmar y ver el resultado (US1-AS1, US1-AS2, US1-AS10)", async ({
    page,
  }) => {
    const previews: Request[] = [];
    const confirms: Request[] = [];
    await page.route("**/api/admin/imports/preview", (route) => {
      previews.push(route.request());
      return route.fulfill({ json: PREVIEW });
    });
    await page.route("**/api/admin/imports", (route) => {
      confirms.push(route.request());
      return route.fulfill({ status: 202, json: { import_id: "imp-1", state: "running", retry: false } });
    });
    let polls = 0;
    await page.route("**/api/admin/imports/imp-1", (route) => {
      polls += 1;
      const counts = { created: 1, updated: 1, unchanged: 0, skipped: 0, duplicate: 1, error: 1 };
      return route.fulfill({
        json:
          polls === 1
            ? { import_id: "imp-1", state: "running", total_rows: 4, counts: { ...counts, created: 0, updated: 0 } }
            : { import_id: "imp-1", state: "finished", total_rows: 4, counts },
      });
    });
    await importPage(page);

    // T024: the form's headers suggest the mapping.
    await expect(page.getByLabel("Número de documento")).toHaveValue("Número de documento");
    await expect(page.getByLabel("Nombre visible: primera columna")).toHaveValue("Nombres");
    await expect(page.getByLabel("Nombre visible: segunda columna (opcional)")).toHaveValue("Apellidos");
    await expect(page.getByLabel("Grado (opcional)")).toHaveValue("Grado que cursas en 2027");
    await expect(page.getByLabel("Institución (opcional)")).toHaveValue("Institución educativa");
    await page.getByLabel("Último día de acceso").fill("2026-12-31");
    await page.getByRole("button", { name: "Ver vista previa" }).click();

    await expect(page.getByTestId("count-new")).toContainText("1");
    await expect(page.getByTestId("count-error")).toContainText("1");
    await expect(page.getByTestId("import-row-5")).toContainText("Falta el nombre.");
    await expect(page.getByTestId("import-row-2")).toContainText("Semillero 9 · profesor1");
    expect(JSON.parse(field(previews[0], "batch")!)).toEqual({
      level: "semillero",
      grade: null,
      access_until: "2026-12-31",
    });
    // The existing account's change is applied only with its own check box (FR-008).
    await page.getByTestId("import-row-3").getByRole("checkbox").check();
    await page.getByRole("button", { name: "Confirmar importación" }).click();

    await expect(page.getByText("Importación terminada")).toBeVisible();
    await expect(page.getByTestId("import-result")).toContainText("Creadas");
    expect(field(confirms[0], "digest")).toBe("digest-1");
    expect(JSON.parse(field(confirms[0], "confirm")!)).toEqual([{ row: 3, changes: ["group_id"] }]);
    expect(JSON.parse(field(confirms[0], "pairing")!)).toEqual([
      { institution: "Colegio Inventado", grade: 9, group_id: 4 },
    ]);
  });

  test("el admin cambia una columna sugerida (T024)", async ({ page }) => {
    const previews: Request[] = [];
    await page.route("**/api/admin/imports/preview", (route) => {
      previews.push(route.request());
      return route.fulfill({ json: PREVIEW });
    });
    await importPage(page);

    await page.getByLabel("Institución (opcional)").selectOption("Sede");
    await page.getByLabel("Correo de recuperación (opcional)").selectOption("");
    await page.getByRole("button", { name: "Ver vista previa" }).click();

    await expect(page.getByTestId("count-new")).toBeVisible();
    const mapping = JSON.parse(field(previews[0], "mapping")!);
    expect(mapping.institution).toBe("Sede");
    expect(mapping.recovery_email).toBeNull();
  });

  test("una vista previa que cambió pide generarla de nuevo, y sin marcar no se confirma ningún cambio (FR-003, US1-AS6)", async ({
    page,
  }) => {
    const confirms: Request[] = [];
    await json(page, "**/api/admin/imports/preview", PREVIEW);
    await page.route("**/api/admin/imports", (route) => {
      confirms.push(route.request());
      return route.fulfill({
        status: 409,
        json: { detail: "La vista previa cambió desde que la viste: vuelve a generarla antes de confirmar." },
      });
    });
    await importPage(page);
    await page.getByRole("button", { name: "Ver vista previa" }).click();
    await page.getByRole("button", { name: "Confirmar importación" }).click();

    await expect(page.getByRole("alert")).toContainText("vuelve a generarla");
    await expect(page.getByRole("button", { name: "Confirmar importación" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Ver vista previa" })).toBeVisible();
    expect(JSON.parse(field(confirms[0], "confirm")!)).toEqual([]);
  });

  test("vincular y quitar una identificación desde la lista de usuarios (US1-AS5, FR-017)", async ({ page }) => {
    const student = {
      id: 31,
      username: "ana.perez7",
      display_name: "Ana Pérez",
      role: "student",
      approved: true,
      active: true,
      education_level: "semillero",
      group_name: "Semillero 9",
      identification: null as string | null,
    };
    const calls: string[] = [];
    await json(page, "**/api/admin/teachers/pending", { teachers: [] });
    await json(page, "**/api/admin/groups", { groups: GROUPS });
    await page.route("**/api/admin/users", (route) => route.fulfill({ json: { users: [student] } }));
    await page.route("**/api/admin/users/31/identification", (route) => {
      const request = route.request();
      calls.push(`${request.method()} ${request.postData() ?? ""}`);
      if (request.method() === "PUT") {
        student.identification = "7700000009";
        return route.fulfill({ json: { user_id: 31, identification: "7700000009" } });
      }
      student.identification = null;
      return route.fulfill({ status: 204, body: "" });
    });
    await injectAuth(page, MOCK_ADMIN);
    await page.goto("/admin");

    await page.getByRole("button", { name: "Vincular identificación" }).click();
    await page.getByLabel("Identificación (solo dígitos)").fill("7700000009");
    await page.getByRole("button", { name: "Vincular", exact: true }).click();
    await expect(page.getByText("Identificación: 7700000009")).toBeVisible();

    page.once("dialog", (dialog) => dialog.accept());
    await page.getByRole("button", { name: "Quitar vínculo" }).click();
    await expect(page.getByRole("button", { name: "Vincular identificación" })).toBeVisible();
    expect(calls).toEqual(['PUT {"identification":"7700000009"}', "DELETE "]);
  });

  test("el admin crea un grupo para un docente con su institución y grado (N25, N26)", async ({ page }) => {
    const bodies: unknown[] = [];
    await json(page, "**/api/admin/teachers/pending", { teachers: [] });
    await json(page, "**/api/admin/groups", { groups: GROUPS });
    await json(page, "**/api/admin/users", {
      users: [
        {
          id: 2,
          username: "profesor1",
          role: "teacher",
          approved: true,
          active: true,
          education_level: null,
          group_name: null,
        },
      ],
    });
    await json(page, "**/api/admin/courses", {
      courses: [{ id: "semillero_9", name: "Semillero 9.º", block: "Semillero" }],
    });
    await page.route("**/api/admin/teachers/2/groups", (route) => {
      bodies.push(route.request().postDataJSON());
      return route.fulfill({ status: 201, json: { group_id: 7, name: "Semillero 9 B" } });
    });
    await injectAuth(page, MOCK_ADMIN);
    await page.goto("/admin");

    await page.getByRole("button", { name: "Crear grupo" }).click();
    const form = page.getByRole("form", { name: "Crear grupo" });
    await form.getByLabel("Nombre del grupo").fill("Semillero 9 B");
    await form.getByLabel("Curso").selectOption("semillero_9");
    await form.getByLabel("Institución").fill("Colegio Inventado");
    await form.getByLabel("Grado").selectOption("9");
    await form.getByRole("button", { name: "Crear", exact: true }).click();

    await expect(page.getByText("Grupo «Semillero 9 B» creado.")).toBeVisible();
    expect(bodies).toEqual([
      { name: "Semillero 9 B", course_id: "semillero_9", institution: "Colegio Inventado", grade: 9 },
    ]);
  });

  test("el estudiante importado ve su identificación y su nombre solo de lectura (US2-AS1, US3-AS2)", async ({
    page,
  }) => {
    await json(page, "**/api/auth/me", {
      ...MOCK_STUDENT,
      username: "7700000001",
      display_name: "Ana Pérez",
      identification: "7700000001",
      display_name_locked: true,
    });
    await injectAuth(page, { ...MOCK_STUDENT, username: "7700000001", display_name: "Ana Pérez" });
    await page.goto("/mi-nombre");

    await expect(page.getByTestId("own-identification")).toContainText("7700000001");
    await expect(page.getByLabel("Tu nombre")).toHaveValue("Ana Pérez");
    await expect(page.getByLabel("Tu nombre")).toHaveAttribute("readonly", "");
    await expect(page.getByText("Tu nombre lo cambia el administrador.")).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar nombre" })).toHaveCount(0);
  });
});
