import { test, expect } from "@playwright/test";

test("dashboard, comparison, ranking and profile browsing", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await expect(page.locator(".status-value")).toContainText("Connected", { timeout: 30000 });
  await expect(page.getByRole("heading", {name: "Great work starts with the right people."})).toBeVisible();
  await page.screenshot({path: `test-results/dashboard-${test.info().project.name}.png`, fullPage: true});
  await page.getByRole("link", {name: "Create a match", exact: true}).click();
  await expect(page.getByRole("button", {name: "Analyze Match"})).toBeEnabled();
  await page.getByRole("button", {name: "Analyze Match"}).click();
  await expect(page.getByRole("heading", {name: "Match analysis", exact: true})).toBeVisible({timeout: 150000});
  await expect(page.getByText("Evidence-based explanation", {exact: true})).toBeVisible();
  await expect(page.getByRole("region", {name: "Professional Affinity", exact: true})).toContainText("Weak Match");
  await expect(page.getByRole("region", {name: "Collaboration Potential", exact: true})).toContainText("Exceptional Complementarity");
  await expect(page.getByRole("region", {name: "Professional Connection Insight", exact: true})).toContainText("cross-functional collaboration");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({path: `test-results/comparison-${test.info().project.name}.png`, fullPage: true});
  await page.getByRole("link", {name: "1-to-N Ranking", exact: true}).click();
  await page.getByRole("button", {name: "Find Best Matches"}).click();
  await expect(page.locator(".ranking-card")).toHaveCount(20, {timeout: 150000});
  const scores = await page.locator(".rank-score strong").allTextContents();
  const values = scores.map(parseFloat);
  expect(values).toEqual([...values].sort((a, b) => b - a));
  await page.locator(".ranking-row").first().click();
  await expect(page.getByRole("heading", {name: "Match analysis", exact: true})).toBeVisible();
  await page.getByRole("link", {name: "Professional Profiles", exact: true}).click();
  await page.getByRole("textbox", {name: "Search professionals"}).fill("TensorFlow");
  await expect(page.locator(".directory-card").first()).toBeVisible();
  await page.getByRole("link", {name: "Engine Explanation", exact: true}).click();
  await expect(page.getByRole("heading", {name: "No black box. Just better connections."})).toBeVisible();
  await expect(page.getByText("The AI language model does not calculate the score.", {exact: true})).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  expect(errors).toEqual([]);
});

test("manual profiles and missing evidence", async ({ page }) => {
  await page.goto("/match");
  await expect(page.getByRole("button", {name: "Enter manually"}).first()).toBeVisible();
  await page.getByRole("button", {name: "Enter manually"}).first().click();
  await page.getByRole("textbox", {name: "Name", exact: true}).fill("Manual professional");
  await page.getByRole("textbox", {name: "Professional role"}).fill("");
  await page.getByRole("textbox", {name: "Industry", exact: true}).fill("");
  await page.getByRole("spinbutton", {name: "Experience (years)"}).fill("");
  await page.getByRole("textbox", {name: "Skills (comma separated)"}).fill("");
  await page.getByRole("textbox", {name: "Interests (comma separated)"}).fill("");
  await page.getByRole("button", {name: "Analyze Match"}).click();
  await expect(page.getByText("Insufficient evidence", {exact: true})).toBeVisible({timeout: 150000});
  await expect(page.getByText("0% confidence", {exact: true})).toBeVisible();
  await expect(page.getByText("Complementarity unavailable", {exact: true})).toBeVisible();
});

test("ranking filters and expansions use existing backend results", async ({ page }) => {
  const matchRequests: string[] = [];
  page.on("request", request => { if (request.method() === "POST" && request.url().includes("/match/")) matchRequests.push(request.url()); });
  await page.goto("/ranking");
  await expect(page.getByRole("button", {name: "Find Best Matches"})).toBeEnabled();
  await page.getByLabel("Results to show", {exact: true}).selectOption("100");
  await page.getByLabel("Candidate pool", {exact: true}).selectOption("demo");
  await page.getByRole("button", {name: "Find Best Matches"}).click();
  await expect(page.locator(".ranking-card")).toHaveCount(99, {timeout: 150000});
  await page.locator(".ranking-row").nth(6).click();
  await expect(page.getByText("Deterministic insight", {exact: true})).toBeVisible();
  await page.locator(".ranking-row").nth(6).click();
  await page.getByLabel("Minimum complementarity (%)", {exact: true}).fill("80");
  await page.getByLabel("Role family", {exact: true}).selectOption("product");
  await page.getByLabel("Industry", {exact: true}).selectOption("technology");
  await expect(page.locator(".ranking-card").first()).toBeVisible();
  const complements = await page.locator(".rank-complement strong").allTextContents();
  expect(complements.every(value => parseFloat(value) >= 80)).toBe(true);
  const tagCounts = await page.locator(".rank-tags .tags").evaluateAll(nodes => nodes.map(n => n.children.length));
  expect(tagCounts.every(count => count <= 3)).toBe(true);
  await page.getByLabel("Minimum affinity (%)", {exact: true}).fill("100");
  await expect(page.getByRole("heading", {name: "No returned matches meet these filters"})).toBeVisible();
  await page.getByRole("button", {name: "Clear filters"}).click();
  await expect(page.locator(".ranking-card")).toHaveCount(99);
  expect(matchRequests).toHaveLength(1);
  expect(matchRequests[0]).toContain("/match/1-to-n");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({path: `test-results/ranking-${test.info().project.name}.png`, fullPage: false});
});

test("demo indicator matches selector recommendations", async ({ page }) => {
  await page.goto("/match");
  await expect(page.getByLabel("Professional A", {exact: true})).toBeVisible();
  const enabled = await page.getByText("Hackathon Demo", {exact: true}).isVisible();
  const group = page.getByLabel("Professional A", {exact: true}).locator('optgroup[label="Recommended demo profiles"]');
  await expect(group).toHaveCount(enabled ? 1 : 0);
  if (enabled) {
    expect(await group.locator("option").count()).toBe(14);
    await expect(group.locator("option").first()).toHaveAttribute("value", "usr_00004");
  }
});

test("backend connection failure is understandable", async ({ page }) => {
  await page.route("**/api/v1/profiles/demo", route => route.abort("connectionrefused"));
  await page.goto("/match");
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Cannot reach the matching engine");
});

for (const message of ["Database unavailable. Start PostgreSQL and initialize the schema.", "Local embedding model unavailable. Check the model files."]) {
  test(`matching service error: ${message.split(".")[0]}`, async ({ page }) => {
    await page.route("**/api/v1/match/1-to-1", route => route.fulfill({status: 503, contentType: "application/json", body: JSON.stringify({detail: message})}));
    await page.goto("/match");
    await page.getByRole("button", {name: "Analyze Match"}).click();
    await expect(page.getByRole("main").getByRole("alert")).toHaveText(message);
    await expect(page.getByRole("button", {name: "Analyze Match"})).toBeEnabled();
  });
}

test("stored hybrid ranking exposes measured engine metrics", async ({ page }) => {
  await page.goto("/ranking");
  await expect(page.getByRole("button", {name: "Find Best Matches"})).toBeEnabled();
  await page.getByLabel("Candidate pool", {exact: true}).selectOption("stored");
  const responsePromise = page.waitForResponse(response => response.url().includes("/match/1-to-n") && response.request().method() === "POST");
  await page.getByRole("button", {name: "Find Best Matches"}).click();
  const response = await responsePromise;
  expect(response.ok()).toBe(true);
  const { metadata } = await response.json();
  await expect(page.locator(".ranking-card").first()).toBeVisible();
  const metrics = page.locator(".engine-metrics");
  await expect(metrics).not.toHaveAttribute("open", "");
  await page.getByText("Engine metrics", {exact: true}).click();
  await expect(metrics).toContainText(metadata.total_network_size.toLocaleString());
  await expect(metrics).toContainText(metadata.profiles_fully_scored.toLocaleString());
  expect(metadata.profiles_fully_scored).toBe(metadata.candidate_pool_size);
  if (metadata.retrieval_mode === "hybrid") {
    expect(metadata.retrieval_backend).toBe("pgvector");
    expect(metadata.semantic_candidates).toBe(200);
    expect(metadata.complementarity_candidates).toBe(100);
    expect(metadata.candidate_pool_size).toBeLessThanOrEqual(300);
    await expect(metrics).toContainText("Hybrid pgvector + complementarity");
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({path: `test-results/engine-metrics-${test.info().project.name}.png`, fullPage: true});
});
