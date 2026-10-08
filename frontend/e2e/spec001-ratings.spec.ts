/**
 * Spec 001 (task T062) — frontend flows of the rating model, against a mocked API.
 * These verify what the screens render from the API; backend behaviour is proven by pytest.
 */
import { test, expect, type Page } from "@playwright/test";
import { injectAuth, mockStudentApi, MOCK_TEACHER } from "./helpers/auth";

const json = (page: Page, url: string, body: unknown) =>
  page.route(url, (route) => route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) }));

const STATS_BASE = {
  user_id: 1,
  topic_elos: [],
  total_attempts: 42,
  study_streak: 3,
};

test.describe("Spec 001 · calificaciones en pantalla", () => {
  test("Práctica muestra la previsión que envía la API (US6-AS2)", async ({ page }) => {
    await mockStudentApi(page);
    await json(page, "**/api/student/next-question", {
      item: { id: "test-item-1", content: "¿Cuánto es $2 + 2$?", difficulty: 1000, topic: "Aritmética", options: ["3", "4", "5", "6"], tags: [] },
      status: "ok",
      preview: { on_correct: 12.3, on_wrong: -7.4 },
    });
    await injectAuth(page);
    await page.goto("/student/courses");
    await page.getByRole("button", { name: /Practicar/ }).first().click();
    await page.getByRole("button", { name: /Ir a practicar/ }).click();
    await page.getByRole("button", { name: "Opción B", exact: true }).click(); // preview shows once an option is chosen

    await expect(page.getByText("+12.3", { exact: true })).toBeVisible();
    await expect(page.getByText("-7.4", { exact: true })).toBeVisible();
  });

  test("Estadísticas: diagnóstico pendiente y cursos de grados anteriores (US6-AS5/AS6)", async ({ page }) => {
    await mockStudentApi(page);
    await json(page, "**/api/student/stats", {
      ...STATS_BASE,
      global_elo: null,
      display_rating: null,
      overall_status: "pending_diagnostic",
      rank_label: null,
      course_ratings: [
        { course_id: "alg6", course_name: "Álgebra 6°", rating: 1300, display_rating: 1300, rank_label: "Platino II", current_context: false, topics: [] },
        { course_id: "alg7", course_name: "Álgebra 7°", rating: null, display_rating: null, rank_label: null, current_context: true, topics: [] },
      ],
    });
    await injectAuth(page);
    await page.goto("/student/stats");

    await expect(page.locator(".sp-stat").filter({ hasText: "ELO global" }).getByText(/Diagnóstico pendiente/)).toBeVisible();
    await expect(page.getByText("Álgebra 6°")).toBeVisible();
    await expect(page.locator(".sp-stat").filter({ hasText: "ELO global" }).getByText("1000")).toHaveCount(0);
  });

  test("Estadísticas marcan las líneas base aproximadas de la reconciliación (FR-034a)", async ({ page }) => {
    await mockStudentApi(page);
    const approx = { topic: "Fracciones", rating: 1100, rd: 200, approximate: true, origin: "legacy_topic_row" };
    const exact = { topic: "Decimales", rating: 1200, rd: 120, approximate: false, origin: "practice" };
    await json(page, "**/api/student/stats", {
      ...STATS_BASE,
      topic_elos: [approx, exact],
      global_elo: 1150,
      display_rating: 1150,
      overall_status: "rated",
      rank_label: "Oro II",
      course_ratings: [
        { course_id: "c1", course_name: "Curso reconciliado", rating: 1150, display_rating: 1150, rank_label: "Oro II", current_context: true, topics: [approx, exact] },
        { course_id: "c2", course_name: "Curso practicado", rating: 1200, display_rating: 1200, rank_label: "Oro I", current_context: true, topics: [exact] },
      ],
    });
    await injectAuth(page);
    await page.goto("/student/stats");

    await expect(page.locator(".sp-row").filter({ hasText: "Curso reconciliado" }).getByText(/aproximado/)).toBeVisible();
    await expect(page.locator(".sp-row").filter({ hasText: "Curso practicado" }).getByText(/aproximado/)).toHaveCount(0);
    await expect(page.getByTitle("Fracciones").getByText("≈")).toBeVisible();
    await expect(page.getByTitle("Decimales").getByText("≈")).toHaveCount(0);
  });

  test("Mapa y riel del curso marcan los temas con línea base aproximada (FR-034a)", async ({ page }) => {
    await mockStudentApi(page);
    await json(page, "**/api/student/map/*", {
      course_id: "calculo",
      course_name: "Cálculo Diferencial",
      diagnostic_done: true,
      nodes: [
        { topic: "Límites", label: "Límites", elo: 1100, rd: 200, approximate: true, item_count: 3, state: "available" },
        { topic: "Derivadas", label: "Derivadas", elo: 1200, rd: 120, approximate: false, item_count: 3, state: "available" },
      ],
    });
    await injectAuth(page);
    await page.goto("/student/course/calculo/map");

    const trail = page.locator(".map-nodes");
    // The trail repeats nodes to fill the path: check the first of each.
    await expect(trail.getByRole("button", { name: /^Límites/ }).first()).toContainText("≈");
    await expect(trail.getByRole("button", { name: /^Derivadas/ }).first()).toBeVisible();
    await expect(trail.getByRole("button", { name: /^Derivadas/ }).first()).not.toContainText("≈");
    await expect(page.locator(".ru-prog", { hasText: "ELO 1100" }).first()).toContainText("≈");
    await expect(page.locator(".ru-prog", { hasText: "ELO 1200" }).first()).not.toContainText("≈");
  });

  test("Número y rango salen del mismo valor: 999.6 → 1000 «Plata I» (US6-AS9)", async ({ page }) => {
    await mockStudentApi(page);
    await json(page, "**/api/student/stats", {
      ...STATS_BASE,
      global_elo: 999.6,
      display_rating: 1000,
      overall_status: "rated",
      rank_label: "Plata I",
      course_ratings: [],
    });
    await injectAuth(page);
    await page.goto("/student/stats");

    await expect(page.locator(".sp-stat").filter({ hasText: "ELO global" }).getByText("1000", { exact: true })).toBeVisible();
    await expect(page.getByText("Plata I", { exact: true }).first()).toBeVisible();
    await expect(page.getByText("ELO 1000", { exact: true }).first()).toBeVisible();
    await expect(page.getByText("Plata II", { exact: true })).toHaveCount(0);
  });

  test("La pantalla muestra display_rating tal cual, sin redondear por su cuenta (FR-028i/j)", async ({ page }) => {
    // Deliberately inconsistent mock: only a screen that renders display_rating as given — not
    // its own rounding of global_elo — shows 1201 here.
    await mockStudentApi(page);
    await json(page, "**/api/student/stats", {
      ...STATS_BASE,
      global_elo: 1180.2,
      display_rating: 1201,
      overall_status: "rated",
      rank_label: "Oro I",
      course_ratings: [],
    });
    await injectAuth(page);
    await page.goto("/student/stats");

    await expect(page.locator(".sp-stat").filter({ hasText: "ELO global" }).getByText("1201", { exact: true })).toBeVisible();
    await expect(page.getByText("ELO 1201", { exact: true }).first()).toBeVisible();
  });

  test("Ranking del grupo: base, empates con el mismo puesto, valor tal cual y pendientes al final (US6-AS7/AS8)", async ({ page }) => {
    await mockStudentApi(page);
    await json(page, "**/api/student/group-ranking", {
      basis: { kind: "course", course_id: "calculo", course_name: "Cálculo Diferencial", source: "group" },
      ranking: [
        { user_id: 4, username: "ana", rating: 1250, rank_label: "Oro I", status: "rated", rank: 1 },
        { user_id: 1, username: "estudiante1", rating: 1201, rank_label: "Oro I", status: "rated", rank: 2 },
        { user_id: 7, username: "luis", rating: 1201, rank_label: "Oro I", status: "rated", rank: 2 },
        { user_id: 9, username: "marta", rating: null, rank_label: null, status: "pending_diagnostic", rank: null },
      ],
      my_rank: 2,
    });
    await injectAuth(page);
    await page.goto("/student/stats");

    const card = page.locator(".sp-card").filter({ hasText: "Ranking" });
    await expect(card.getByText(/Cálculo Diferencial/)).toBeVisible();
    await expect(card.getByText("1201", { exact: true })).toHaveCount(2);
    await expect(card.locator(".pos").filter({ hasText: /^(#2|🥈)$/ })).toHaveCount(2);
    await expect(card.locator(".sp-row").last()).toContainText("marta");
    await expect(card.locator(".sp-row").last()).toContainText(/Diagnóstico pendiente/);
  });

  test("Panel docente usa display_rating y rank_label de la API (US6-AS3, FR-028j)", async ({ page }) => {
    await page.route("**/api/teacher/**", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "[]" }),
    );
    await json(page, "**/api/teacher/metrics", {});
    await json(page, "**/api/teacher/dashboard", {
      students: [
        { user_id: 5, username: "sofia", education_level: "colegio", group_id: 1, group_name: "10A", global_elo: 999.6, display_rating: 1000, rank_label: "Plata I", overall_status: "rated", total_attempts: 12, accuracy: 0.75, last_activity: "2026-10-07" },
      ],
      groups: [],
    });
    await injectAuth(page, MOCK_TEACHER);
    await page.goto("/teacher");

    await expect(page.getByText("Plata I", { exact: true }).first()).toBeVisible();
    await expect(page.getByText("1000", { exact: true }).first()).toBeVisible();
  });

  test("Inicio lista los rangos de /api/meta/ranks", async ({ page }) => {
    await json(page, "**/api/meta/ranks", [
      { label: "Aspirante", min: 0 }, { label: "Hierro", min: 600 }, { label: "Bronce II", min: 700 },
      { label: "Bronce I", min: 800 }, { label: "Plata II", min: 900 }, { label: "Plata I", min: 1000 },
      { label: "Oro II", min: 1100 }, { label: "Oro I", min: 1200 }, { label: "Platino II", min: 1300 },
      { label: "Platino I", min: 1400 }, { label: "Diamante II", min: 1500 }, { label: "Diamante I", min: 1600 },
      { label: "Maestro", min: 1800 }, { label: "Gran Maestro", min: 2000 }, { label: "Leyenda", min: 2200 },
      { label: "Leyenda Suprema", min: 2500 },
    ]);
    await page.addInitScript(() => localStorage.setItem("levelup-lang", "es"));
    await page.goto("/");

    await expect(page.getByText("ELO 1100+", { exact: true })).toBeVisible();
    await expect(page.getByText("ELO 1120+", { exact: true })).toHaveCount(0);
  });
});
