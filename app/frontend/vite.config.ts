import { defineConfig } from "vite";
import { configDefaults } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/v1": "http://localhost:8000",
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup/vitest.setup.ts"],
    css: true,
    // tests/e2e/* are real-browser Playwright specs (`npm run test:e2e`), not
    // jsdom unit tests -- vitest's default glob would otherwise also pick them
    // up and fail on @playwright/test's incompatible test.describe API.
    exclude: [...configDefaults.exclude, "tests/e2e/**"],
  },
});
