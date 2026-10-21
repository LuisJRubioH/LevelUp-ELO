import { test, expect } from "./fixtures";
import type { Page } from "@playwright/test";
import { injectAuth, MOCK_TEACHER } from "./helpers/auth";

/**
 * Spec 006 C1 (FR-041, FR-043): the teacher console renders the server's summary — ranks, mean,
 * «attention» — as given, and the 7d / 30d / Todo buttons ask the server for that window.
 * Delivery RV (FR-041c): each set shows the rating it was ranked on and names its basis.
 */

const student = (user_id: number, name: string, display_rating: number | null, accuracy: number) => ({
  user_id,
  name,
  education_level: "colegio",
  group_id: 1,
  group_name: "10A",
  display_rating, // the «Todos» rating (FR-041c)
  rank_label: display_rating == null ? null : "Oro I",
  total_attempts: 4,
  accuracy,
  last_activity: "2026-10-19",
});

const FIGURES = {
  n: 3,
  mean: 1234, // the server's figure: no arithmetic on the rows below gives it
  accuracy: 71,
  attempts: 12,
  attention: [7], // only the server decides who needs attention
  ranking: [
    { user_id: 5, rank: 1, display_rating: 1200, rank_label: "Oro I" },
    { user_id: 6, rank: 1, display_rating: 1200, rank_label: "Oro I" },
    { user_id: 7, rank: null, display_rating: null, rank_label: null },
  ],
  histogram: [{ label: "1100", count: 2 }],
  basis: { kind: "linked_courses" },
};

const DASHBOARD = {
  students: [
    student(5, "Ana", 1200, 0.9),
    student(6, "Bea", 1200, 0.2),
    student(7, "Caro", null, 0.95),
  ],
  groups: [{ group_id: 1, name: "10A", course_id: "calculo", course_name: "Cálculo", student_count: 3 }],
  summary: { ...FIGURES, groups: { "1": FIGURES } },
};

async function mockConsole(page: Page, dashboard: object = DASHBOARD) {
  const asked: string[] = [];
  await page.route("**/api/teacher/**", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: "[]" }),
  );
  await page.route("**/api/teacher/groups", (route) => route.fulfill({ json: DASHBOARD.groups }));
  await page.route("**/api/teacher/metrics*", (route) => {
    asked.push(route.request().url());
    return route.fulfill({ json: {} });
  });
  await page.route("**/api/teacher/dashboard*", (route) => {
    asked.push(route.request().url());
    return route.fulfill({ json: dashboard });
  });
  await page.route("**/api/student/exam/pending", (route) => route.fulfill({ json: [] }));
  await injectAuth(page, MOCK_TEACHER);
  return asked;
}

const windows = (asked: string[], path: string) =>
  asked.filter((u) => u.includes(path)).map((u) => new URL(u).searchParams.get("days"));

test.describe("Consola docente — cifras del servidor y ventanas", () => {
  test("el ranking, el promedio y «atención» son los del servidor (US4-AS1, FR-041)", async ({ page }) => {
    await mockConsole(page);
    await page.goto("/teacher");

    await expect(page.locator(".stat-card").filter({ hasText: "ELO promedio" })).toContainText("1234");
    // Bea has 20 % accuracy, but the server does not list her: no flag.
    await expect(page.locator(".stu-row").filter({ hasText: "Bea" }).getByText("Necesita atención")).toHaveCount(0);
    await expect(page.locator(".stu-row").filter({ hasText: "Caro" }).getByText("Necesita atención")).toBeVisible();

    await page.getByRole("button", { name: /Ranking/ }).click();
    await expect(page.locator(".pod .medal").filter({ hasText: "🥇" })).toHaveCount(2);
    await expect(page.locator(".rank-line").filter({ hasText: "Caro" }).locator(".pos")).toHaveText("—");

    await page.goto("/teacher/groups");
    await expect(page.locator(".grp-card").filter({ hasText: "10A" })).toContainText("1234");
  });

  test("7d, 30d y Todo piden esa ventana al servidor (US4-AS4, FR-043)", async ({ page }) => {
    const asked = await mockConsole(page);
    await page.goto("/teacher");
    await expect(page.getByText("Ana").first()).toBeVisible();
    await page.getByRole("button", { name: /Métricas/ }).click();
    await expect.poll(() => windows(asked, "/metrics")).toEqual(["30"]);

    await page.getByRole("button", { name: "7d", exact: true }).click();
    await expect.poll(() => windows(asked, "/dashboard").at(-1)).toBe("7");
    await expect.poll(() => windows(asked, "/metrics").at(-1)).toBe("7");

    await page.getByRole("button", { name: "Todo", exact: true }).click();
    await expect.poll(() => windows(asked, "/dashboard").at(-1)).toBe("all");
    await expect.poll(() => windows(asked, "/metrics").at(-1)).toBe("all");
    expect(windows(asked, "/dashboard")[0]).toBe("30");
  });

  test("cada grupo se ordena por su curso y «Todos» por la media de sus cursos contigo (US4-AS5, FR-041c)", async ({
    page,
  }) => {
    // Ana leads on the courses she shares with the teacher; Bea leads on the group's course.
    const place = (user_id: number, rank: number, display_rating: number, rank_label: string) => ({
      user_id,
      rank,
      display_rating,
      rank_label,
    });
    const figures = (ranking: object[], basis: object) => ({
      n: 2,
      mean: 1300,
      accuracy: 80,
      attempts: 8,
      attention: [],
      ranking,
      histogram: [],
      basis,
    });
    await mockConsole(page, {
      students: [student(5, "Ana", 1500, 0.8), student(6, "Bea", 1200, 0.8)],
      groups: DASHBOARD.groups,
      summary: {
        ...figures([place(5, 1, 1500, "Diamante II"), place(6, 2, 1200, "Oro I")], { kind: "linked_courses" }),
        groups: {
          "1": figures([place(6, 1, 1350, "Platino II"), place(5, 2, 1000, "Plata I")], {
            kind: "course",
            course_id: "calculo",
            course_name: "Cálculo",
          }),
        },
      },
    });
    await page.goto("/teacher");

    await page.getByRole("button", { name: /Ranking/ }).click();
    await expect(page.getByText("Por la media de sus cursos contigo")).toBeVisible();
    await expect(page.locator(".pod.p1")).toContainText("Ana");
    await expect(page.locator(".pod.p1")).toContainText("1500");

    await page.locator(".topic-chip").filter({ hasText: "10A" }).click();
    await expect(page.getByText("Por ELO de Cálculo")).toBeVisible();
    await expect(page.locator(".pod.p1")).toContainText("Bea");
    await expect(page.locator(".pod.p1")).toContainText("1350");
    await expect(page.locator(".pod").filter({ hasText: "Ana" })).toContainText("1000");

    await page.getByRole("button", { name: /Estudiantes/ }).click();
    await expect(page.locator(".stu-row").filter({ hasText: "Ana" })).toContainText("1000");
    await expect(page.locator(".stu-row").filter({ hasText: "Ana" })).not.toContainText("1500");
  });
});
