import { test as base, expect } from "@playwright/test";

/**
 * Every spec imports `test` from here. The e2e suite mocks the API: these tests verify frontend
 * flows, not backend integration. A request to `/api/*` that no test mocked never reaches the
 * network — it gets a fixed 503 — so a run cannot depend on whether a backend happens to be
 * listening on the dev proxy's port — and the test fails, naming the call, so every request a test
 * makes is answered by its own fixtures. Mocks registered later in a test take precedence
 * (Playwright runs matching routes in reverse registration order).
 */
export const test = base.extend<{ unmockedApi: string[] }>({
  unmockedApi: [
    async ({ page }, use) => {
      const unmocked: string[] = [];
      await page.route(
        (url) => url.pathname.startsWith("/api/"),
        async (route) => {
          const url = new URL(route.request().url());
          unmocked.push(`${route.request().method()} ${url.pathname}`);
          await route.fulfill({ status: 503, json: { detail: "not mocked in e2e" } });
        },
      );
      await page.routeWebSocket(
        (url) => url.pathname.startsWith("/api/"),
        (ws) => ws.close({ code: 1011, reason: "not mocked in e2e" }),
      );
      await use(unmocked);
      // Unload the app while the routes above are still installed: at teardown Playwright
      // removes routes before closing the page, and a request fired in between would reach the
      // dev proxy.
      await page.goto("about:blank").catch(() => {});
      expect([...new Set(unmocked)], "API calls this test did not mock").toEqual([]);
    },
    { auto: true },
  ],
});

export { expect };
