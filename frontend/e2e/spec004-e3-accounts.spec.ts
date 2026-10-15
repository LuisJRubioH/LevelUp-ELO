import type { Page } from "@playwright/test";
import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi } from "./helpers/auth";

/**
 * Spec 004, delivery E3 — on screen: the admin creates a student one by one (US6, FR-040) and sets
 * a last day of access (FR-046, FR-050); an expired account is told why at sign-in and when an
 * open session ends (US7-AS1, US7-AS2, FR-048); a match closed by an expiry says so (US7-AS5).
 */

const EXPIRED =
  "El período de acceso de tu cuenta terminó. Tu progreso está guardado. Contacta al administrador si necesitas ampliar el acceso.";

const MOCK_ADMIN = {
  user_id: 9,
  username: "admin",
  role: "admin" as const,
  education_level: null,
  grade: null,
  email: null,
};

const json = (page: Page, url: string, body: unknown, status = 200) =>
  page.route(url, (route) => route.fulfill({ status, json: body }));

async function adminPage(page: Page, users: object[] = []) {
  await json(page, "**/api/admin/teachers/pending", { teachers: [] });
  await json(page, "**/api/admin/users", { users });
  await json(page, "**/api/admin/groups", {
    groups: [{ id: 4, name: "10A", teacher_id: 2, teacher_name: "profesor1", student_count: 3 }],
  });
  await injectAuth(page, MOCK_ADMIN);
  await page.goto("/admin");
  return page.getByRole("form", { name: "Crear estudiante" });
}

test.describe("Spec 004 · estudiantes creados uno a uno y último día de acceso", () => {
  test("el admin crea un estudiante y ve su contraseña temporal una vez (spec 004 US6-AS1, FR-040)", async ({
    page,
  }) => {
    const bodies: unknown[] = [];
    await page.route("**/api/admin/students", (route) => {
      bodies.push(route.request().postDataJSON());
      return route.fulfill({
        status: 201,
        json: { user_id: 31, username: "ana.perez7", temporary_password: "k7Qm-2xRt-9pLw" },
      });
    });
    const form = await adminPage(page);

    await form.getByLabel("Usuario del estudiante").fill("ana.perez7");
    await form.getByLabel("Nombre visible").fill("Ana Pérez");
    await form.getByLabel("Grupo").selectOption("4");
    await form.getByLabel("Nivel").selectOption("colegio");
    await expect(form.getByText("No aplica")).toBeVisible();
    await form.getByLabel("Nivel").selectOption("semillero");
    await form.getByLabel("Grado").selectOption("9");
    await form.getByLabel("Último día de acceso (opcional)").fill("2026-12-31");
    await form.getByRole("button", { name: "Crear estudiante" }).click();

    await expect(page.getByTestId("temporary-password")).toContainText("k7Qm-2xRt-9pLw");
    await expect(page.getByTestId("temporary-password")).toContainText("ana.perez7");
    expect(bodies).toEqual([
      {
        username: "ana.perez7",
        display_name: "Ana Pérez",
        group_id: 4,
        education_level: "semillero",
        grade: "9",
        access_until: "2026-12-31",
      },
    ]);
    await expect(form.getByLabel("Usuario del estudiante")).toHaveValue("");
  });

  test("una creación rechazada muestra el motivo y no da contraseña (spec 004 US6-AS2 … AS4)", async ({
    page,
  }) => {
    await page.route("**/api/admin/students", (route) =>
      route.fulfill({ status: 400, json: { detail: "El nombre de usuario ya existe." } }),
    );
    const form = await adminPage(page);

    await form.getByLabel("Usuario del estudiante").fill("estudiante1");
    await form.getByLabel("Nombre visible").fill("Ana Pérez");
    await form.getByLabel("Grupo").selectOption("4");
    await form.getByLabel("Nivel").selectOption("colegio");
    await form.getByRole("button", { name: "Crear estudiante" }).click();

    await expect(form.getByRole("alert")).toContainText("El nombre de usuario ya existe.");
    await expect(page.getByTestId("temporary-password")).toHaveCount(0);
  });

  test("el admin ve, amplía y quita el último día de acceso (spec 004 US7-AS4, FR-046, FR-050)", async ({
    page,
  }) => {
    const bodies: unknown[] = [];
    await page.route("**/api/admin/users/5/access-until", (route) => {
      bodies.push({ method: route.request().method(), body: route.request().postDataJSON() });
      return route.fulfill({ status: 200, json: { user_id: 5, access_until: null, access_expired: false } });
    });
    await adminPage(page, [
      {
        id: 5, username: "estudiante5", display_name: "Sofía Vélez", role: "student",
        approved: true, active: true, education_level: "colegio", group_name: "10A",
        must_change_password: false, access_until: "2026-10-14", access_expired: true,
      },
      {
        id: 6, username: "estudiante6", display_name: "Tomás Ruiz", role: "student",
        approved: true, active: true, education_level: "colegio", group_name: "10A",
        must_change_password: false, access_until: null, access_expired: false,
      },
    ]);

    const row = page.getByRole("row").filter({ hasText: "estudiante5" });
    await expect(row).toContainText("14/10/2026");
    await expect(row).toContainText("vencida");
    await expect(page.getByRole("row").filter({ hasText: "estudiante6" })).toContainText("sin límite");

    await row.getByRole("button", { name: "Último día" }).click();
    await row.getByLabel("Último día de acceso").fill("2027-01-31");
    await row.getByRole("button", { name: "Guardar" }).click();
    await expect.poll(() => bodies.length).toBe(1);

    await row.getByRole("button", { name: "Último día" }).click();
    await row.getByRole("button", { name: "Quitar límite" }).click();
    await expect.poll(() => bodies.length).toBe(2);
    expect(bodies).toEqual([
      { method: "PUT", body: { access_until: "2027-01-31" } },
      { method: "PUT", body: { access_until: null } },
    ]);
  });

  test("una cuenta vencida ve el mensaje al iniciar sesión (spec 004 US7-AS1, FR-048)", async ({ page }) => {
    await json(page, "**/api/auth/login", { detail: EXPIRED }, 403);
    await page.goto("/login");
    await page.getByLabel("Usuario o correo").fill("estudiante1");
    await page.getByLabel("Contraseña").fill("demo1234");
    await page.getByRole("button", { name: /Entrar a Oulad/ }).click();

    await expect(page.getByRole("alert")).toHaveText(EXPIRED);
    await expect(page).toHaveURL("/login");
  });

  test("una sesión abierta termina al vencer y el inicio de sesión dice por qué (spec 004 US7-AS2, FR-047)", async ({
    page,
  }) => {
    await mockStudentApi(page);
    await json(page, "**/api/student/courses", { detail: EXPIRED }, 401);
    let renewals = 0;
    await page.route("**/api/auth/refresh", (route) => {
      renewals += 1;
      return route.fulfill({ status: 401, json: { detail: EXPIRED } });
    });
    await injectAuth(page);
    await page.goto("/student/courses");

    await expect(page).toHaveURL("/login");
    await expect(page.getByRole("alert")).toHaveText(EXPIRED);
    expect(renewals).toBeGreaterThanOrEqual(1);
  });

  test("una partida cerrada por un vencimiento lo explica y no mueve el ELO (spec 004 US7-AS5, FR-051)", async ({
    page,
  }) => {
    await mockStudentApi(page);
    await json(page, "**/api/student/pvp/history", []);
    await page.routeWebSocket("**/api/ws/pvp/**", (ws) => {
      ws.onMessage((raw) => {
        if (!("token" in JSON.parse(String(raw)))) return;
        ws.send(
          JSON.stringify({
            type: "game_start",
            match_id: 3,
            items: [{ id: "i1", content: "¿$1+1$?", options: ["2", "3"], topic: "Suma", difficulty: 900 }],
            opponent: { name: "Laura Gómez", elo: 1010 },
            duration_seconds: 180,
          }),
        );
        ws.send(
          JSON.stringify({
            type: "game_end", your_score: 0, opp_score: 0, won: false, draw: false,
            abandoned: true, reason: "account_expired", elo_delta: 0, elo_reason: "account_expired",
          }),
        );
      });
    });
    await injectAuth(page);
    await page.goto("/student/league");
    await page.locator("select.pv-select").selectOption("calculo");
    await page.getByRole("button", { name: "Buscar rival →" }).click();

    await expect(page.getByRole("heading", { name: "Partida cancelada" })).toBeVisible();
    await expect(page.getByRole("status").filter({ hasText: "período de acceso" })).toContainText(
      "Ningún ELO cambió",
    );
    await expect(page.locator(".pv-elo-delta")).toContainText("+0");
  });
});
