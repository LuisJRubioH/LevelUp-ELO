import type { Page } from "@playwright/test";
import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi, MOCK_STUDENT } from "./helpers/auth";

/**
 * Spec 004, delivery E2 — passwords and sessions on screen (FR-026, FR-029 … FR-031): a temporary
 * password is changed before anything else, the user can change theirs, and the admin resets
 * access and creates teachers, seeing the temporary password once.
 */

const FORCED = "Debes cambiar tu contraseña temporal antes de continuar.";

const MOCK_ADMIN = {
  user_id: 9,
  username: "admin",
  role: "admin" as const,
  education_level: null,
  grade: null,
  email: null,
};

async function mockPasswordChange(page: Page, bodies: unknown[], status = 200) {
  await page.route("**/api/auth/password", async (route) => {
    bodies.push(route.request().postDataJSON());
    if (status !== 200) {
      await route.fulfill({ status, json: { detail: "La contraseña actual no es correcta." } });
      return;
    }
    await route.fulfill({
      status: 200,
      json: {
        access_token: "new-token",
        token_type: "bearer",
        expires_in: 900,
        user_id: MOCK_STUDENT.user_id,
        username: MOCK_STUDENT.username,
        role: "student",
        must_change_password: false,
      },
    });
  });
}

test.describe("Spec 004 · contraseñas y sesiones", () => {
  test("una contraseña temporal se cambia antes de seguir (spec 004 US5-AS1, FR-030)", async ({
    page,
  }) => {
    await mockStudentApi(page);
    await page.route("**/api/auth/login", (route) =>
      route.fulfill({
        status: 200,
        json: {
          access_token: "temp-token",
          token_type: "bearer",
          expires_in: 900,
          user_id: MOCK_STUDENT.user_id,
          username: MOCK_STUDENT.username,
          role: "student",
          must_change_password: true,
        },
      }),
    );
    await page.route("**/api/auth/me", (route) =>
      route.fulfill({
        status: 200,
        json: { ...MOCK_STUDENT, approved: true, must_change_password: true },
      }),
    );
    const bodies: unknown[] = [];
    await mockPasswordChange(page, bodies);

    await page.goto("/login");
    await page.getByLabel("Usuario o correo").fill(MOCK_STUDENT.username);
    await page.getByLabel("Contraseña").fill("Temporal1234");
    await page.getByRole("button", { name: /Entrar a Oulad/ }).click();

    await expect(page).toHaveURL("/cambiar-contrasena");
    await expect(page.getByText("Entraste con una contraseña temporal.", { exact: false })).toBeVisible();
    await page.goto("/student/courses");
    await expect(page).toHaveURL("/cambiar-contrasena");

    await page.getByLabel("Contraseña temporal").fill("Temporal1234");
    await page.getByLabel("Nueva contraseña", { exact: true }).fill("propia-123");
    await page.getByLabel("Repite la nueva contraseña").fill("propia-123");
    await page.getByRole("button", { name: "Guardar contraseña" }).click();

    await expect(page).toHaveURL(/\/student/);
    expect(bodies).toEqual([{ current_password: "Temporal1234", new_password: "propia-123" }]);
  });

  test("si la API exige el cambio, la app lleva a la pantalla de cambio (spec 004 FR-030)", async ({
    page,
  }) => {
    await injectAuth(page);
    await mockStudentApi(page);
    await page.route("**/api/student/**", (route) =>
      route.fulfill({ status: 403, json: { detail: FORCED } }),
    );

    await page.goto("/student/courses");

    await expect(page).toHaveURL("/cambiar-contrasena");
  });

  test("el estudiante cambia su contraseña desde el menú (spec 004 US4-AS3, FR-026)", async ({
    page,
  }) => {
    await injectAuth(page);
    await mockStudentApi(page);
    const bodies: unknown[] = [];
    await mockPasswordChange(page, bodies, 400);

    await page.goto("/student/courses");
    await page.getByRole("button", { name: "Cambiar contraseña" }).first().click();
    await expect(page).toHaveURL("/cambiar-contrasena");
    await expect(page.getByRole("button", { name: /Volver/ })).toBeVisible();

    await page.getByLabel("Nueva contraseña", { exact: true }).fill("corta");
    await page.getByLabel("Contraseña actual").fill("demo1234");
    await page.getByLabel("Repite la nueva contraseña").fill("corta");
    await page.getByRole("button", { name: "Guardar contraseña" }).click();
    await expect(page.getByRole("alert")).toContainText("al menos 6");
    expect(bodies).toEqual([]);

    await page.getByLabel("Contraseña actual").fill("equivocada");
    await page.getByLabel("Nueva contraseña", { exact: true }).fill("valida-123");
    await page.getByLabel("Repite la nueva contraseña").fill("valida-123");
    await page.getByRole("button", { name: "Guardar contraseña" }).click();
    await expect(page.getByRole("alert")).toContainText("La contraseña actual no es correcta.");
    await expect(page).toHaveURL("/cambiar-contrasena");
  });

  test("el admin restablece el acceso y crea un docente; ve la contraseña temporal una vez (spec 004 US5-AS1, US5-AS2)", async ({
    page,
  }) => {
    await injectAuth(page, MOCK_ADMIN);
    // The student creation form (E3) lists the groups.
    await page.route("**/api/admin/groups", (route) => route.fulfill({ json: { groups: [] } }));
    await page.route("**/api/admin/teachers/pending", (route) =>
      route.fulfill({ status: 200, json: { teachers: [] } }),
    );
    await page.route("**/api/admin/users", (route) =>
      route.fulfill({
        status: 200,
        json: {
          users: [
            {
              id: 5,
              username: "estudiante5",
              role: "student",
              approved: true,
              active: true,
              education_level: "colegio",
              group_name: "10A",
              must_change_password: false,
            },
          ],
        },
      }),
    );
    const resets: string[] = [];
    await page.route("**/api/admin/users/5/reset-password", (route) => {
      resets.push(route.request().method());
      return route.fulfill({ status: 200, json: { user_id: 5, temporary_password: "Kq7hTz3mWp2x" } });
    });
    const created: unknown[] = [];
    await page.route("**/api/admin/teachers", (route) => {
      created.push(route.request().postDataJSON());
      return route.fulfill({
        status: 201,
        json: { user_id: 12, username: "docente.nueva", temporary_password: "Rb4nVc8sYe6d" },
      });
    });
    page.on("dialog", (dialog) => dialog.accept());

    await page.goto("/admin");
    await page.getByRole("button", { name: "Restablecer contraseña" }).click();

    const notice = page.getByTestId("temporary-password");
    await expect(notice).toContainText("estudiante5");
    await expect(notice).toContainText("Kq7hTz3mWp2x");
    expect(resets).toEqual(["POST"]);

    await page.getByLabel("Usuario", { exact: true }).fill("docente.nueva");
    await page.getByRole("button", { name: "Crear docente" }).click();
    await expect(notice).toContainText("docente.nueva");
    await expect(notice).toContainText("Rb4nVc8sYe6d");
    expect(created).toEqual([{ username: "docente.nueva" }]);

    await notice.getByRole("button", { name: "Cerrar" }).click();
    await expect(page.getByTestId("temporary-password")).toHaveCount(0);
  });
});
