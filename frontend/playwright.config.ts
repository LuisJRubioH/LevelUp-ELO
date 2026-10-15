import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  // No retries: a test that only passes on a second try is a failure, not a pass.
  retries: 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? [["github"], ["list"], ["html", { open: "never" }]] : "html",
  use: {
    channel: process.env.PLAYWRIGHT_CHANNEL || undefined,
    locale: "es-CO",
    // Dates render the same on every machine (CI runs in UTC).
    timezoneId: "America/Bogota",
    baseURL: "http://localhost:5173",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "pnpm run dev",
    url: "http://localhost:5173",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
