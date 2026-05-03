import type { Page } from "@playwright/test";

export const MOCK_STUDENT = {
  user_id: 1,
  username: "estudiante1",
  role: "student" as const,
  education_level: "colegio",
  grade: "10",
  email: null,
};

export const MOCK_TEACHER = {
  user_id: 2,
  username: "profesor1",
  role: "teacher" as const,
  education_level: null,
  grade: null,
  email: null,
};

/** Inject Zustand auth state directly into localStorage to skip the login UI. */
export async function injectAuth(page: Page, user = MOCK_STUDENT) {
  await page.goto("/");
  await page.evaluate((authData) => {
    localStorage.setItem(
      "levelup-auth",
      JSON.stringify({
        state: {
          accessToken: "fake-test-token",
          user: authData,
          isAuthenticated: true,
          sessionStartTime: Date.now(),
        },
        version: 0,
      })
    );
  }, user);
}

/** Mock login endpoint so the login form works without a real backend. */
export async function mockLoginEndpoint(page: Page, user = MOCK_STUDENT) {
  await page.route("**/api/auth/login", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: "fake-test-token",
        token_type: "bearer",
        expires_in: 900,
        user_id: user.user_id,
        username: user.username,
        role: user.role,
      }),
    });
  });

  await page.route("**/api/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        ...user,
        approved: true,
      }),
    });
  });
}

/** Mock the common student endpoints used in most tests. */
export async function mockStudentApi(page: Page) {
  await page.route("**/api/student/courses", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        { id: "calculo", name: "Cálculo Diferencial", block: "Universidad", enrolled: true },
        { id: "algebra", name: "Álgebra Lineal", block: "Universidad", enrolled: true },
      ]),
    });
  });

  await page.route("**/api/student/next-question", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        item: {
          id: "test-item-1",
          content: "¿Cuánto es $2 + 2$?",
          difficulty: 1000,
          topic: "Aritmética",
          options: ["3", "4", "5", "6"],
          tags: ["operaciones"],
        },
        status: "ok",
      }),
    });
  });

  await page.route("**/api/student/answer", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        is_correct: true,
        elo_before: 1000,
        elo_after: 1016,
        rd_after: 335,
        delta_elo: 16,
        cog_data: {},
      }),
    });
  });

  await page.route("**/api/student/stats", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        user_id: 1,
        global_elo: 1050,
        topic_elos: [
          { topic: "Aritmética", rating: 1050, rd: 335 },
          { topic: "Álgebra", rating: 980, rd: 340 },
        ],
        total_attempts: 42,
        study_streak: 3,
        rank_label: "Aprendiz I",
      }),
    });
  });

  await page.route("**/api/student/history", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([]),
    });
  });

  await page.route("**/api/student/activity", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([]),
    });
  });

  await page.route("**/api/student/achievements", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([]),
    });
  });

  await page.route("**/api/student/group-ranking", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([]),
    });
  });

  await page.route("**/api/student/ai-status", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ available: false, provider: null }),
    });
  });
}
