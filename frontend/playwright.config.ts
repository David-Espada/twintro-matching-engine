import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e", timeout: 180000, workers: 1,
  use: { baseURL: "http://localhost:3000", trace: "retain-on-failure" },
  projects: [{ name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["iPhone 13"], defaultBrowserType: "chromium" } }],
});
