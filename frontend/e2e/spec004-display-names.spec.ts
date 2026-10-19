import type { Page } from "@playwright/test";
import { test, expect } from "./fixtures";
import { injectAuth, mockStudentApi, MOCK_STUDENT, MOCK_TEACHER } from "./helpers/auth";

/**
 * Spec 004, delivery E2 — display names on screen (US3, FR-020 … FR-025). Classmates and teachers
 * see a student by `name` (the display name, or the username of an account without one); the
 * registration asks students for a name; a student changes their own; the admin sees username and
 * name and corrects a name.
 */

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

test.describe("Spec 004 · nombres visibles", () => {
  test("el ranking muestra a cada compañero por su nombre (spec 004 US3-AS1, FR-021)", async ({ page }) => {
    await mockStudentApi(page);
    await json(page, "**/api/student/group-ranking", {
      basis: { kind: "overall", course_id: null, course_name: null, source: "overall" },
      ranking: [
        { user_id: 4, name: "Ana María Pérez", rating: 1250, rank_label: "Oro I", status: "rated", rank: 1 },
        { user_id: 1, name: "estudiante1", rating: 1201, rank_label: "Oro I", status: "rated", rank: 2 },
      ],
      my_rank: 2,
    });
    await injectAuth(page);
    await page.goto("/student/stats");

    const card = page.locator(".sp-card").filter({ hasText: "Ranking" });
    await expect(card.locator(".sp-row").first()).toContainText("Ana María Pérez");
    await expect(card.locator(".sp-row").nth(1)).toContainText("estudiante1");
  });

  test("en la liga, el rival aparece por su nombre (spec 004 US3-AS2, FR-021)", async ({ page }) => {
    await mockStudentApi(page);
    await json(page, "**/api/student/pvp/history", []);
    await page.routeWebSocket("**/api/ws/pvp/**", (ws) => {
      ws.onMessage((raw) => {
        if ("token" in JSON.parse(String(raw))) {
          ws.send(
            JSON.stringify({
              type: "game_start",
              match_id: 3,
              items: [{ id: "i1", content: "¿$1+1$?", options: ["2", "3"], topic: "Suma", difficulty: 900 }],
              opponent: { name: "Laura Gómez", elo: 1010 },
              duration_seconds: 180,
            }),
          );
        }
      });
    });
    await injectAuth(page);
    await page.goto("/student/league");
    await page.locator("select.pv-select").selectOption("calculo");
    await page.getByRole("button", { name: "Buscar rival →" }).click();

    await expect(page.getByText("Laura Gómez").first()).toBeVisible();
  });

  test("el panel docente muestra nombre y grupo, sin el usuario (spec 004 US3-AS4, FR-023)", async ({ page }) => {
    await page.route("**/api/teacher/**", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "[]" }),
    );
    await json(page, "**/api/teacher/metrics*", {});
    await json(page, "**/api/teacher/dashboard*", {
      students: [
        {
          user_id: 5, name: "Sofía Vélez", education_level: "colegio", group_id: 1, group_name: "10A",
          global_elo: 1000, display_rating: 1000, rank_label: "Plata I", overall_status: "rated",
          total_attempts: 12, accuracy: 0.75, last_activity: "2026-10-07",
        },
      ],
      groups: [{ id: 1, name: "10A", course_id: null, invite_code: null, student_count: 1 }],
    });
    await injectAuth(page, MOCK_TEACHER);
    await page.goto("/teacher");

    await expect(page.getByText("Sofía Vélez").first()).toBeVisible();
    await expect(page.getByText(/^@/)).toHaveCount(0);
  });

  test("los procedimientos pendientes muestran el nombre del estudiante (spec 004 US3-AS4)", async ({ page }) => {
    await page.route("**/api/teacher/**", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "[]" }),
    );
    await json(page, "**/api/teacher/procedures", [
      {
        submission_id: 8, student_id: 5, student_name: "Sofía Vélez", item_id: "it-1",
        item_content: "Deriva $x^2$", ai_score: null, status: "pending",
        created_at: "2026-10-14 10:00", has_image: false,
      },
    ]);
    await injectAuth(page, MOCK_TEACHER);
    await page.goto("/teacher/procedures");

    await expect(page.getByText("Sofía Vélez").first()).toBeVisible();
  });

  test("el registro pide el nombre al estudiante (spec 004 US3-AS8, FR-020)", async ({ page }) => {
    await json(page, "**/api/auth/registration", { enabled: true });
    const bodies: Record<string, unknown>[] = [];
    await page.route("**/api/auth/register", (route) => {
      bodies.push(route.request().postDataJSON());
      return route.fulfill({ status: 400, json: { detail: "Ese nombre no está permitido." } });
    });
    await page.goto("/login");
    await page.getByRole("button", { name: "Crear cuenta", exact: true }).first().click();

    const name = page.getByLabel("Tu nombre");
    await expect(name).toBeVisible();
    await expect(name).toHaveAttribute("required", "");
    await name.fill("Tomás Ruiz");
    await page.getByLabel("Nombre de usuario").fill("tomas.r");
    await page.getByLabel("Contraseña", { exact: true }).fill("password123");
    await page.getByLabel("Confirmar contraseña").fill("password123");
    await page.locator("label.check.terms").click();
    await page.getByRole("button", { name: /Crear mi cuenta/ }).click();

    await expect.poll(() => bodies.length).toBe(1);
    expect(bodies[0]).toMatchObject({ username: "tomas.r", display_name: "Tomás Ruiz", role: "student" });
    await expect(page.getByRole("alert")).toContainText("Ese nombre no está permitido.");
  });

  test("el estudiante cambia su propio nombre (spec 004 US3-AS7, FR-025)", async ({ page }) => {
    await mockStudentApi(page);
    const bodies: unknown[] = [];
    let refuse = true;
    await page.route("**/api/student/display-name", (route) => {
      bodies.push(route.request().postDataJSON());
      if (refuse) {
        refuse = false;
        return route.fulfill({ status: 400, json: { detail: "Ese nombre no está permitido." } });
      }
      return route.fulfill({ status: 200, json: { display_name: "Sofía Vélez" } });
    });
    await injectAuth(page, { ...MOCK_STUDENT });
    await page.goto("/student");
    await page.getByRole("button", { name: "Mi nombre" }).click();
    await expect(page).toHaveURL("/mi-nombre");

    const field = page.getByLabel("Tu nombre");
    await field.fill("Elver Galarga");
    await page.getByRole("button", { name: "Guardar nombre" }).click();
    await expect(page.getByRole("alert")).toContainText("Ese nombre no está permitido.");

    await field.fill("Sofía Vélez");
    await page.getByRole("button", { name: "Guardar nombre" }).click();
    await expect(page.getByRole("status")).toContainText("Sofía Vélez");
    expect(bodies).toEqual([{ display_name: "Elver Galarga" }, { display_name: "Sofía Vélez" }]);

    // Back in the app (no reload: the test's stored session would come back), the menu shows it.
    await page.getByRole("button", { name: "← Volver" }).click();
    await expect(page.locator(".tc-user")).toContainText("Sofía Vélez");
  });

  test("el admin ve usuario y nombre, y corrige un nombre (spec 004 US3-AS5, US3-AS6)", async ({ page }) => {
    await json(page, "**/api/admin/teachers/pending", { teachers: [] });
    await json(page, "**/api/admin/groups", { groups: [] }); // the student creation form (E3)
    await json(page, "**/api/admin/users", {
      users: [
        {
          id: 5, username: "estudiante5", display_name: "Sofía Vélez", role: "student",
          approved: true, active: true, education_level: "colegio", group_name: "10A",
          must_change_password: false,
        },
      ],
    });
    const bodies: unknown[] = [];
    await page.route("**/api/admin/users/5/display-name", (route) => {
      bodies.push({ method: route.request().method(), body: route.request().postDataJSON() });
      return route.fulfill({ status: 200, json: { user_id: 5, display_name: "Sofía Vélez Ríos" } });
    });
    await injectAuth(page, MOCK_ADMIN);
    await page.goto("/admin");

    const row = page.getByRole("row").filter({ hasText: "estudiante5" });
    await expect(row).toContainText("Sofía Vélez");
    await row.getByRole("button", { name: "Cambiar nombre" }).click();
    await row.getByLabel("Nombre visible").fill("Sofía Vélez Ríos");
    await row.getByRole("button", { name: "Guardar" }).click();

    await expect.poll(() => bodies.length).toBe(1);
    expect(bodies[0]).toEqual({ method: "PUT", body: { display_name: "Sofía Vélez Ríos" } });
  });
});
