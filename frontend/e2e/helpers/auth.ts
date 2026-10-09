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
  await page.addInitScript((authData) => {
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
    localStorage.setItem("levelup-lang", "es");
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
  await page.route("**/api/student/map/*", async (route) => {
    await route.fulfill({ json: { course_id: "calculo", course_name: "Cálculo Diferencial", diagnostic_done: true, nodes: [] } });
  });
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
        // Spec 001 API shape: screens render display_rating and rank_label as given.
        global_elo: 1050,
        display_rating: 1050,
        overall_status: "rated",
        course_ratings: [],
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
      body: JSON.stringify({ attempts: [] }),
    });
  });

  await page.route("**/api/student/activity", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ activity: {} }),
    });
  });

  await page.route("**/api/student/achievements", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ achievements: [], catalog: [] }),
    });
  });

  await page.route("**/api/student/group-ranking", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ ranking: [], my_rank: null }),
    });
  });

  await page.route("**/api/student/ai-status", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ available: false, provider: null }),
    });
  });

  await page.route("**/api/student/exam/history", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: "[]" });
  });

  await page.route("**/api/student/diagnostic/*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        completed: true,
        course_id: "calculo",
        result: {
          initial_elo: 1050,
          score_pct: 60,
          league: { name: "Aprendiz", min: 1000, color: "#6C63FF", rank: "I" },
          themes: [],
          correct_total: 3,
          answered: 5,
          completed: true,
        },
      }),
    });
  });
}

/** The public rank scale (GET /api/meta/ranks), as the API serves it (spec 001, FR-031). */
export const MOCK_RANKS = [
  { label: "Aspirante", min: 0 }, { label: "Hierro", min: 600 }, { label: "Bronce II", min: 700 },
  { label: "Bronce I", min: 800 }, { label: "Plata II", min: 900 }, { label: "Plata I", min: 1000 },
  { label: "Oro II", min: 1100 }, { label: "Oro I", min: 1200 }, { label: "Platino II", min: 1300 },
  { label: "Platino I", min: 1400 }, { label: "Diamante II", min: 1500 }, { label: "Diamante I", min: 1600 },
  { label: "Maestro", min: 1800 }, { label: "Gran Maestro", min: 2000 }, { label: "Leyenda", min: 2200 },
  { label: "Leyenda Suprema", min: 2500 },
];

/** Mock the public endpoints the landing page reads. */
export async function mockPublicApi(page: Page) {
  await page.route("**/api/meta/ranks", async (route) => {
    await route.fulfill({ json: MOCK_RANKS });
  });
}
