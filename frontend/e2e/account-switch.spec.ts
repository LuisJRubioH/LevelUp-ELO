import type { Page } from "@playwright/test";
import { test, expect } from "./fixtures";
import { MOCK_STUDENT, mockStudentApi } from "./helpers/auth";

/**
 * A second person who signs in over an open session — a shared school computer, the login page
 * reached without logging out — must not see the first account's data, use its own AI key or
 * inherit its exam draft. Logout already cleans up; signing in as another account must too. The
 * same account coming back after its session expired keeps its draft and key, and a browser
 * without Cache Storage can still sign in.
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

type Seed = { session: typeof A | null; lastAccount: number | null };

/** Browser state left by an earlier visit: a session (or none), the last account, A's key and draft. */
async function seedBrowser(page: Page, seed: Seed) {
  await page.addInitScript((value: Seed) => {
    if (sessionStorage.getItem("seeded")) return;
    sessionStorage.setItem("seeded", "1");
    if (value.session) {
      localStorage.setItem(
        "levelup-auth",
        JSON.stringify({
          state: {
            accessToken: "token-a",
            user: value.session,
            isAuthenticated: true,
            sessionStartTime: Date.now(),
          },
          version: 0,
        }),
      );
    }
    if (value.lastAccount != null) {
      localStorage.setItem("levelup-last-account", String(value.lastAccount));
    }
    localStorage.setItem("levelup-settings", JSON.stringify({ state: { apiKey: "own-key-of-a" }, version: 0 }));
    localStorage.setItem("levelup-exam-draft", JSON.stringify({ session_id: "exam-of-a", answers: {} }));
    localStorage.setItem("levelup-lang", "es");
  }, seed);
}

async function mockLoginAs(page: Page, user: typeof A, token: string) {
  await page.route("**/api/auth/login", (route) =>
    route.fulfill({
      json: {
        access_token: token,
        token_type: "bearer",
        expires_in: 900,
        user_id: user.user_id,
        username: user.username,
        role: "student",
      },
    }),
  );
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: { ...user, approved: true } }));
}

async function signInFromLoginPage(page: Page, username: string) {
  await page.fill('input[autocomplete="username"]', username);
  await page.fill('input[autocomplete="current-password"]', "password-of-" + username);
  await page.click("button.auth-submit");
  await page.waitForURL(/\/student/);
}

const storedKey = (page: Page) =>
  page.evaluate(() => JSON.parse(localStorage.getItem("levelup-settings") ?? "{}").state?.apiKey ?? "");
const storedDraft = (page: Page) => page.evaluate(() => localStorage.getItem("levelup-exam-draft"));

test("the same account signing in again after its session expired keeps its draft and key", async ({
  page,
}) => {
  await mockStudentApi(page);
  await mockLoginAs(page, A, "token-a2");
  await seedBrowser(page, { session: null, lastAccount: A.user_id });

  await page.goto("/login");
  await signInFromLoginPage(page, A.username);

  expect(await storedKey(page)).toBe("own-key-of-a");
  expect(await storedDraft(page)).not.toBeNull();
});

test("a browser without Cache Storage still signs the new account in", async ({ page }) => {
  await mockStudentApi(page);
  await mockLoginAs(page, B, "token-b");
  await seedBrowser(page, { session: A, lastAccount: A.user_id });
  await page.addInitScript(() => {
    window.caches.keys = () => Promise.reject(new DOMException("blocked", "SecurityError"));
  });

  await page.goto("/login");
  await signInFromLoginPage(page, B.username);

  expect(await storedKey(page)).toBe("");
  expect(await storedDraft(page)).toBeNull();
});

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
  await mockLoginAs(page, B, "token-b");
  await seedBrowser(page, { session: A, lastAccount: null });

  const globalElo = page.locator(".sp-stat").filter({ hasText: "ELO global" });
  await page.goto("/student/stats");
  await expect(globalElo.getByText("987", { exact: true })).toBeVisible();

  // The login page, reached inside the same app without logging out.
  await page.evaluate(() => {
    window.history.pushState({}, "", "/login");
    window.dispatchEvent(new PopStateEvent("popstate"));
  });
  await signInFromLoginPage(page, B.username);
  await page.getByRole("link", { name: /Progreso/ }).first().click();

  await expect(globalElo.getByText("1234", { exact: true })).toBeVisible();
  await expect(globalElo.getByText("987", { exact: true })).toHaveCount(0);
  expect(await storedKey(page)).toBe("");
  expect(await storedDraft(page)).toBeNull();
});
