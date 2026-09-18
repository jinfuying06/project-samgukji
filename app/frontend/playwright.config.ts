import { defineConfig, devices } from "@playwright/test";

/**
 * Real-browser E2E + accessibility config. Only starts the frontend dev server --
 * the backend must already be running separately on :8000 with real imported data
 * (see app/backend/README.md "Running locally"), same assumption vite.config.ts's
 * `/v1` proxy already makes for `npm run dev` in normal local development.
 */
export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  fullyParallel: false,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: "http://localhost:5183",
    trace: "retain-on-failure",
  },
  webServer: {
    // A dedicated, unusual port + --strictPort (fail rather than silently pick another
    // port) + reuseExistingServer:false -- this suite must always drive its own TKAF
    // dev server, never accidentally attach to an unrelated app already running on a
    // common port like 5173 (this happened once: an unrelated project's dev server was
    // already listening there, and the suite silently tested that app instead).
    command: "npm run dev -- --port 5183 --strictPort",
    url: "http://localhost:5183",
    reuseExistingServer: false,
    timeout: 30_000,
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
