import { defineConfig, devices } from "@playwright/test";
import { tmpdir } from "node:os";
import { join } from "node:path";

/**
 * Spec 004 E5, US9-AS5 (automated): session renewal against the real API, on the page's own
 * origin and with the cookie as after the switch (`AUTH_COOKIE_SAMESITE=lax`, docs/transfer.md
 * § 3.3), in WebKit — Safari's engine — as desktop, iPhone and iPad, and in Chromium.
 * Not a real device: WebKit on Linux does not apply Safari's tracking prevention, so the
 * owner's check on real devices stays the reference.
 */
const DB = join(tmpdir(), "oulad-session.db");
const BASE_URL = "https://localhost:5174";

export default defineConfig({
  testDir: "./e2e-session",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  // One API and one database: the tests run one after another.
  workers: 1,
  reporter: process.env.CI ? [["github"], ["list"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: BASE_URL,
    ignoreHTTPSErrors: true,
    locale: "es-CO",
    timezoneId: "America/Bogota",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "safari-desktop", use: { ...devices["Desktop Safari"] } },
    { name: "safari-iphone", use: { ...devices["iPhone 15"] } },
    { name: "safari-ipad", use: { ...devices["iPad Pro 11"] } },
    { name: "chrome-desktop", use: { ...devices["Desktop Chrome"] } },
  ],
  webServer: [
    {
      // A fresh SQLite database for every run; seeded with the demo and test users.
      command: `rm -f "${DB}" && python -m uvicorn api.main:app --port 8000`,
      cwd: "..",
      url: "http://localhost:8000/api/health",
      reuseExistingServer: false,
      timeout: 180_000,
      env: {
        DATABASE_URL: "",
        DB_PATH: DB,
        ADMIN_PASSWORD: "testadmin123",
        AUTH_COOKIE_SAMESITE: "lax",
        CORS_ORIGINS: JSON.stringify([BASE_URL]),
        RATE_LIMIT_LOGIN_ACCOUNT: "1000/minute",
      },
    },
    {
      command: "pnpm exec vite --config vite.session.config.ts",
      url: BASE_URL,
      ignoreHTTPSErrors: true,
      reuseExistingServer: false,
      timeout: 120_000,
      env: { VITE_API_URL: "", VITE_WS_URL: "ws://localhost:8000" },
    },
  ],
});
