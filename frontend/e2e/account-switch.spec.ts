import { test, expect } from "./fixtures";
import { MOCK_STUDENT, mockStudentApi } from "./helpers/auth";

/**
 * A second person who signs in over an open session — a shared school computer, the login page
 * reached without logging out — must not see the first account's data or use its own AI key.
 * Logout already cleans up; signing in must clean up the same way.
 */
const A = { ...MOCK_STUDENT, user_id: 11, username: "alumna_a" };
const B = { ...MOCK_STUDENT, user_id: 12, username: "alumno_b" };

function stats(userId: number, rating: number, attempts: number) {
  return {
    user_id: userId,
    global_elo: rating,
    display_rating: rating,
    overall_status: "rated",
    course_ratings: [],
    topic_elos: [{ topic: "Aritmética", rating, rd: 300 }],
    total_attempts: attempts,
    study_streak: 1,
    rank_label: "Aprendiz I",
  };
}

test("signing in over another account's open session shows only the new account", async ({
  page,
}) => {
  await mockStudentApi(page);
  await page.route("**/api/student/stats", (route) =>
    route.fulfill({
      json:
        route.request().headers()["authorization"] === "Bearer token-b"
          ? stats(B.user_id, 1234, 27)
          : stats(A.user_id, 987, 21),
    }),
  );
  await page.route("**/api/auth/login", (route) =>
    route.fulfill({
      json: {
        access_token: "token-b",
        token_type: "bearer",
        expires_in: 900,
        user_id: B.user_id,
        username: B.username,
        role: "student",
      },
    }),
  );
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: { ...B, approved: true } }));
  await page.addInitScript((a) => {
    if (sessionStorage.getItem("seeded")) return;
    sessionStorage.setItem("seeded", "1");
    localStorage.setItem(
      "levelup-auth",
      JSON.stringify({
        state: { accessToken: "token-a", user: a, isAuthenticated: true, sessionStartTime: Date.now() },
        version: 0,
      }),
    );
    localStorage.setItem("levelup-settings", JSON.stringify({ state: { apiKey: "own-key-of-a" }, version: 0 }));
    localStorage.setItem("levelup-lang", "es");
  }, A);

  const globalElo = page.locator(".sp-stat").filter({ hasText: "ELO global" });
  await page.goto("/student/stats");
  await expect(globalElo.getByText("987", { exact: true })).toBeVisible();

  // The login page, reached inside the same app without logging out.
  await page.evaluate(() => {
    window.history.pushState({}, "", "/login");
    window.dispatchEvent(new PopStateEvent("popstate"));
  });
  await page.fill('input[autocomplete="username"]', B.username);
  await page.fill('input[autocomplete="current-password"]', "password-of-b");
  await page.click("button.auth-submit");
  await page.waitForURL(/\/student/);
  await page.getByRole("link", { name: /Progreso/ }).first().click();

  await expect(globalElo.getByText("1234", { exact: true })).toBeVisible();
  await expect(globalElo.getByText("987", { exact: true })).toHaveCount(0);
  const apiKey = await page.evaluate(
    () => JSON.parse(localStorage.getItem("levelup-settings") ?? "{}").state?.apiKey ?? "",
  );
  expect(apiKey).toBe("");
});
