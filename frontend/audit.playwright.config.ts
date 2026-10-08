import { defineConfig } from "@playwright/test";
import base from "./playwright.config";

export default defineConfig({
  ...base,
  // Functional assertions use normal browser-test budgets; this is not a latency benchmark.
  timeout: 30000,
  expect: { timeout: 5000 },
  workers: 2,
  retries: 0,
  reporter: [["json", { outputFile: "../docs/auditoria-produccion-e2e.json" }]],
  use: { ...base.use, baseURL: "http://127.0.0.1:5187" },
  webServer: {
    command: `"${process.execPath}" node_modules/vite/bin/vite.js preview --host 127.0.0.1 --port 5187 --strictPort`,
    url: "http://127.0.0.1:5187",
    reuseExistingServer: false,
    timeout: 60000,
    env: { VITE_API_URL: "" },
  },
});
