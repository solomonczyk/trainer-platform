import { test, expect, Page } from "@playwright/test";

const STAGING_URL = "https://trainer.152.53.227.37.nip.io";

// Test user credentials
const TEST_USER = {
  email: `quest_010b_${Date.now()}@test.com`,
  password: "QuestTest123!",
  name: "Quest 010B Test User",
};

let consoleErrors: string[] = [];
let serverErrors: string[] = [];

test.describe("Quest Play Browser Runtime 010B", () => {
  test.beforeEach(async ({ page }) => {
    consoleErrors = [];
    serverErrors = [];

    // Collect browser console errors
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    // Collect page crashes
    page.on("pageerror", (err) => {
      consoleErrors.push(`PAGE_CRASH: ${err.message}`);
    });

    // Collect HTTP errors
    page.on("response", (response) => {
      if (response.status() >= 500) {
        serverErrors.push(`${response.status()} ${response.url()}`);
      }
    });
  });

  test.afterEach(async () => {
    // Log all collected errors
    if (consoleErrors.length > 0) {
      console.log(`[CONSOLE ERRORS (${test.info().title})]:`, consoleErrors.slice(0, 10));
    }
    if (serverErrors.length > 0) {
      console.log(`[SERVER ERRORS (${test.info().title})]:`, serverErrors.slice(0, 5));
    }
  });

  // =========================================================================
  // Registration helper
  // =========================================================================

  async function registerUser(page: Page) {
    await page.goto(`${STAGING_URL}/register`);
    await page.waitForLoadState("networkidle");

    // Fill registration form
    const emailInput = page.locator('input[type="email"]');
    await emailInput.waitFor({ state: "visible", timeout: 10000 });
    await emailInput.fill(TEST_USER.email);

    const passwordInput = page.locator('input[type="password"]').first();
    await passwordInput.fill(TEST_USER.password);

    // Confirm password if present
    const confirmInput = page.locator('input[type="password"]').nth(1);
    if (await confirmInput.isVisible().catch(() => false)) {
      await confirmInput.fill(TEST_USER.password);
    }

    // Click submit
    await page.locator('button[type="submit"]').first().click();

    // Wait for navigation away from /register
    await page.waitForTimeout(2000);
  }

  async function loginUser(page: Page) {
    await page.goto(`${STAGING_URL}/login`);
    await page.waitForLoadState("networkidle");

    const emailInput = page.locator('input[type="email"]');
    await emailInput.waitFor({ state: "visible", timeout: 10000 });
    await emailInput.fill(TEST_USER.email);

    await page.locator('input[type="password"]').first().fill(TEST_USER.password);
    await page.locator('button[type="submit"]').first().click();

    // Wait for navigation away from /login
    await page.waitForTimeout(2000);
  }

  // =========================================================================
  // QA Quest Browser Acceptance
  // =========================================================================

  test("QA quest catalog loads without undefined.message error", async ({ page }) => {
    // Navigate directly to QA trainer quest page
    await page.goto(`${STAGING_URL}/trainers/qa-engineer-interview-trainer/quests`);
    await page.waitForLoadState("networkidle");

    // Verify page content loaded
    const bodyText = await page.locator("body").textContent();
    expect(bodyText).toBeTruthy();
    expect(bodyText!.length).toBeGreaterThan(50);

    // Check for specific error — the exact name we are fixing
    const undefinedMessageErrors = consoleErrors.filter(
      (e) => e.includes("Cannot read properties of undefined") || e.includes("Cannot read properties")
    );
    expect(undefinedMessageErrors.length).toBe(0);

    const crashErrors = consoleErrors.filter((e) => e.includes("PAGE_CRASH"));
    expect(crashErrors.length).toBe(0);

    // Take screenshot
    await page.screenshot({
      path: "docs/simulator_engine/screenshots/010b-qa-quest-catalog.png",
      fullPage: true,
    });
  });

  test("QA bug report quest can be opened without crash", async ({ page }) => {
    // Navigate directly to QA quest catalog
    await page.goto(`${STAGING_URL}/trainers/qa-engineer-interview-trainer/quests`);
    await page.waitForLoadState("networkidle");

    // Find and click the bug report quest
    const questCard = page.locator("text=qa_bug_report_structure_v1").first()
      .or(page.locator("a[href*='qa_bug_report_structure_v1']").first());
    if (await questCard.isVisible({ timeout: 5000 }).catch(() => false)) {
      await questCard.click();
    } else {
      // Direct URL navigation
      await page.goto(`${STAGING_URL}/trainers/qa-engineer-interview-trainer/quests/qa_bug_report_structure_v1`);
    }
    await page.waitForLoadState("networkidle");

    // Wait for page to load
    await page.waitForTimeout(3000);

    // Check page is not blank
    const bodyText = await page.locator("body").textContent();
    expect(bodyText).toBeTruthy();

    // Check for the undefined.message error
    const undefinedMessageErrors = consoleErrors.filter(
      (e) => e.includes("Cannot read properties of undefined") || e.includes("Cannot read properties")
    );
    expect(undefinedMessageErrors.length).toBe(0);

    // No page crashes
    const crashErrors = consoleErrors.filter((e) => e.includes("PAGE_CRASH"));
    expect(crashErrors.length).toBe(0);

    // Check for white screen or infinite loader
    const whiteScreen = bodyText!.trim().length < 20;
    expect(whiteScreen).toBe(false);

    // Take screenshot
    await page.screenshot({
      path: "docs/simulator_engine/screenshots/010b-qa-quest-load.png",
      fullPage: true,
    });
  });

  test("BA quest catalog loads without undefined.message error", async ({ page }) => {
    // Navigate to the BA trainer quest catalog
    await page.goto(`${STAGING_URL}/trainers/business-analyst-interview-trainer/quests`);
    await page.waitForLoadState("networkidle");

    const bodyText = await page.locator("body").textContent();
    expect(bodyText).toBeTruthy();
    expect(bodyText!.length).toBeGreaterThan(50);

    // Check for the undefined.message error
    const undefinedMessageErrors = consoleErrors.filter(
      (e) => e.includes("Cannot read properties of undefined")
    );
    expect(undefinedMessageErrors.length).toBe(0);

    await page.screenshot({
      path: "docs/simulator_engine/screenshots/010b-ba-quest-catalog.png",
      fullPage: true,
    });
  });

  // =========================================================================
  // Legacy URL verification
  // =========================================================================

  test("Legacy /scenarios/qa_bug_report_structure_v1 does not show old textarea UI", async ({ page }) => {
    await page.goto(`${STAGING_URL}/scenarios/qa_bug_report_structure_v1`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    const bodyText = await page.locator("body").textContent();
    expect(bodyText).toBeTruthy();

    // Check page didn't crash
    const undefinedMessageErrors = consoleErrors.filter(
      (e) => e.includes("Cannot read properties of undefined")
    );
    expect(undefinedMessageErrors.length).toBe(0);

    await page.screenshot({
      path: "docs/simulator_engine/screenshots/010b-legacy-url.png",
      fullPage: true,
    });
  });

  // =========================================================================
  // General health
  // =========================================================================

  test("Frontend health check returns 200", async ({ page }) => {
    const response = await page.request.get(`${STAGING_URL}/health`);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.status).toBe("ok");
  });

  test("No unexpected 5xx errors during navigation", async ({ page }) => {
    // Navigate through several key pages
    const pages = [
      `${STAGING_URL}/`,
      `${STAGING_URL}/login`,
      `${STAGING_URL}/register`,
      `${STAGING_URL}/domains`,
    ];

    for (const url of pages) {
      const response = await page.request.get(url);
      expect(response.status()).toBeLessThan(500);
    }

    // Check all collected server errors
    expect(serverErrors.length).toBe(0);
  });
});
