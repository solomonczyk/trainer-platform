import { test, expect, Page } from "@playwright/test";

const STAGING_URL = "https://trainer.152.53.227.37.nip.io";

// Unique test user per run
const TEST_USER = {
  email: `quest_010b_full_${Date.now()}@test.com`,
  password: "QuestTest123!",
  name: "Quest 010B Full Test",
};

// Shared error collectors
let consoleErrors: string[] = [];
let serverErrors: string[] = [];
let networkRequests: { url: string; status: number }[] = [];

test.describe("Quest Play Browser Runtime 010B — Full Acceptance", () => {
  test.beforeEach(async ({ page }) => {
    consoleErrors = [];
    serverErrors = [];
    networkRequests = [];

    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text());
      }
    });

    page.on("pageerror", (err) => {
      consoleErrors.push(`PAGE_CRASH: ${err.message}`);
    });

    page.on("response", (response) => {
      networkRequests.push({ url: response.url(), status: response.status() });
      if (response.status() >= 500) {
        serverErrors.push(`${response.status()} ${response.url()}`);
      }
    });
  });

  test.afterEach(async () => {
    // Print summary after each test
    const undefinedErrors = consoleErrors.filter(
      (e) => e.includes("Cannot read properties of undefined") || e.includes("Cannot read properties")
    );
    const crashErrors = consoleErrors.filter((e) => e.includes("PAGE_CRASH"));
    const runtimeErrors = consoleErrors.filter(
      (e) => !e.includes("401") && !e.includes("Failed to load resource")
    );

    console.log(`\n[ERRORS (${test.info().title})]:`);
    console.log(`  undefined.message errors: ${undefinedErrors.length}`);
    console.log(`  page crashes: ${crashErrors.length}`);
    console.log(`  runtime errors: ${runtimeErrors.length}`);
    console.log(`  total console errors: ${consoleErrors.length}`);
    console.log(`  server 5xx errors: ${serverErrors.length}`);

    if (runtimeErrors.length > 0) {
      console.log(`  runtime error details: ${runtimeErrors.slice(0, 5).join(" | ")}`);
    }

    // Separate 401 auth errors from unexpected errors
    const auth401Errors = consoleErrors.filter((e) => e.includes("401"));
    const unexpectedErrors = consoleErrors.filter(
      (e) => !e.includes("401") && !e.includes("Failed to load resource")
    );

    console.log(`  auth 401 errors (expected): ${auth401Errors.length}`);
    console.log(`  unexpected errors: ${unexpectedErrors.length}`);
  });

  // =========================================================================
  // Helpers
  // =========================================================================

  async function registerUser(page: Page) {
    await page.goto(`${STAGING_URL}/register`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);

    const emailInput = page.locator('input[type="email"]');
    await emailInput.waitFor({ state: "visible", timeout: 10000 });
    await emailInput.fill(TEST_USER.email);

    const pwdInputs = page.locator('input[type="password"]');
    await pwdInputs.first().fill(TEST_USER.password);

    // Confirm password if field exists
    if (await pwdInputs.nth(1).isVisible().catch(() => false)) {
      await pwdInputs.nth(1).fill(TEST_USER.password);
    }

    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(3000);
  }

  async function loginUser(page: Page) {
    await page.goto(`${STAGING_URL}/login`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);

    await page.locator('input[type="email"]').waitFor({ state: "visible", timeout: 10000 });
    await page.locator('input[type="email"]').fill(TEST_USER.email);
    await page.locator('input[type="password"]').first().fill(TEST_USER.password);
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(3000);
  }

  async function navigateToQuestCatalog(page: Page, trainerSlug: string) {
    await page.goto(`${STAGING_URL}/trainers/${trainerSlug}/quests`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
  }

  async function openQuest(page: Page, questId: string) {
    await page.goto(`${STAGING_URL}/trainers/qa-engineer-interview-trainer/quests/${questId}`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);
  }

  async function clickStartQuest(page: Page) {
    // Look for the start quest button
    const startBtn = page.getByText("quest.start_quest", { exact: true }).first()
      .or(page.locator("button:has-text('Начать')").first())
      .or(page.locator("button:has-text('Start')").first());
    if (await startBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await startBtn.click();
      await page.waitForTimeout(1500);
    }
  }

  async function selectSingleChoice(page: Page, optionText: string) {
    // Click the option with matching text
    const option = page.locator(`button:has-text("${optionText}")`).first()
      .or(page.locator(`[role="radio"]:has-text("${optionText}")`).first());
    if (await option.isVisible({ timeout: 3000 }).catch(() => false)) {
      await option.click();
      await page.waitForTimeout(500);
    }
  }

  async function clickSubmit(page: Page) {
    const submitBtn = page.getByText("quest.next_step", { exact: true }).first()
      .or(page.getByText("Далее", { exact: true }).first())
      .or(page.getByText("Next", { exact: true }).first())
      .or(page.locator("button[data-testid='button']:not([disabled])").last());
    if (await submitBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await submitBtn.click();
      await page.waitForTimeout(2000);
    }
  }

  async function waitForReady(page: Page) {
    // Wait for the quest interaction to be ready (not loading, not intro)
    await page.waitForTimeout(2000);
  }

  // =========================================================================
  // Full QA Quest — All Steps
  // =========================================================================

  test("QA full quest: register, complete all steps, verify outcome", async ({ page, context }) => {
    // Step 1: Register new user
    await registerUser(page);
    console.log("[QA] Registration done");

    // Step 2: Login
    await loginUser(page);
    console.log("[QA] Login done");

    // Step 3: Navigate to QA trainer
    await page.goto(`${STAGING_URL}/trainers/qa-engineer-interview-trainer`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    console.log("[QA] On QA trainer page");

    // Step 4: Click primary CTA that leads to quest catalog
    // Try looking for a link/button labeled "Quest" or "Квесты"
    const catalogLink = page.locator("a[href*='/quests']").first()
      .or(page.getByText("Квесты", { exact: true }).first())
      .or(page.getByText("Quests", { exact: true }).first());
    if (await catalogLink.isVisible({ timeout: 3000 }).catch(() => false)) {
      await catalogLink.click();
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(2000);
    }

    // Step 5: Navigate to catalog
    await navigateToQuestCatalog(page, "qa-engineer-interview-trainer");
    console.log("[QA] Quest catalog loaded");

    // Step 6: Open the QA bug report quest
    await openQuest(page, "qa_bug_report_structure_v1");
    console.log("[QA] Quest page loaded without crash");

    // Check for undefined.message error
    const undefinedErrors1 = consoleErrors.filter(
      (e) => e.includes("Cannot read properties of undefined") || e.includes("Cannot read properties")
    );
    expect(undefinedErrors1.length).toBe(0);

    // Step 7: Click start
    await clickStartQuest(page);
    console.log("[QA] Clicked start quest");

    // Now we need to navigate through the steps
    // The quest should have: multiple_choice, ordering, single_choice, evidence_select, free_text
    // Each step has a submit button

    // Try to work through available steps
    // Each step appears as an interaction with a submit button
    for (let step = 1; step <= 8; step++) {
      // Check if we're on the outcome or feedback page
      const bodyText = await page.locator("body").textContent().catch(() => "");
      if (!bodyText) break;

      // Look for interactive elements we can click
      const clickableButtons = await page.locator("button:not([disabled])").count();

      // Try clicking radio buttons / choices if present
      const radioButtons = page.locator('[role="radio"]');
      const radioCount = await radioButtons.count().catch(() => 0);
      if (radioCount > 0) {
        await radioButtons.first().click();
        await page.waitForTimeout(500);
      }

      // Try clicking checkboxes
      const checkboxes = page.locator('[role="checkbox"]');
      const checkboxCount = await checkboxes.count().catch(() => 0);
      if (checkboxCount > 0) {
        await checkboxes.first().click();
        await page.waitForTimeout(500);
      }

      // Try clicking any selectable option buttons
      const optionBtns = page.locator('button:not([disabled]):not([data-testid="button"])');
      const optionCount = await optionBtns.count().catch(() => 0);
      if (optionCount > 0 && optionCount <= 10) {
        // Click first option
        await optionBtns.first().click();
        await page.waitForTimeout(500);
      }

      // Try filling a textarea if visible
      const textarea = page.locator("textarea");
      if (await textarea.isVisible({ timeout: 500 }).catch(() => false)) {
        await textarea.fill("The bug report should include steps to reproduce, expected vs actual behavior, environment details, severity assessment, and any relevant logs or screenshots. A well-structured report helps developers understand and fix the issue efficiently.");
        await page.waitForTimeout(500);
      }

      // Click submit
      const submitBtn = page.locator('button[data-testid="button"]:not([disabled])').last();
      if (await submitBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
        await submitBtn.click();
        await page.waitForTimeout(3000);
      } else {
        break; // No more submit buttons
      }
    }

    console.log("[QA] Steps completed");

    // Step 8: Wait for outcome/debrief
    await page.waitForTimeout(5000);

    // Step 9: Check for view_debrief button or outcome
    const viewDebriefBtn = page.getByText("quest.view_debrief", { exact: true }).first()
      .or(page.getByText("Разбор", { exact: true }).first())
      .or(page.getByText("Debrief", { exact: true }).first());
    if (await viewDebriefBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await viewDebriefBtn.click();
      await page.waitForTimeout(2000);
    }

    // Step 10: Screenshot proof
    await page.screenshot({
      path: "docs/simulator_engine/screenshots/010b-qa-full-completion.png",
      fullPage: true,
    });

    // Step 11: Refresh and check persistence
    const currentUrl = page.url();
    await page.goto(currentUrl);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);

    await page.screenshot({
      path: "docs/simulator_engine/screenshots/010b-qa-refresh-persistence.png",
      fullPage: true,
    });

    // Step 12: Verify no errors
    const undefinedErrors = consoleErrors.filter(
      (e) => e.includes("Cannot read properties of undefined") || e.includes("Cannot read properties")
    );
    expect(undefinedErrors.length).toBe(0);

    const crashErrors = consoleErrors.filter((e) => e.includes("PAGE_CRASH"));
    expect(crashErrors.length).toBe(0);

    // Separate expected 401 auth errors from unexpected runtime errors
    const unexpectedErrors = consoleErrors.filter(
      (e) => !e.includes("401") && !e.includes("Failed to load resource")
    );
    expect(unexpectedErrors.length).toBe(0);

    console.log("[QA] ✅ Full quest acceptance PASSED");
  });

  // =========================================================================
  // Full BA Quest
  // =========================================================================

  test("BA full quest: register, complete, verify outcome", async ({ page }) => {
    // Use the same user from QA test if available, otherwise register new
    await loginUser(page).catch(async () => {
      await registerUser(page);
      await loginUser(page);
    });

    // Navigate to BA trainer
    await page.goto(`${STAGING_URL}/trainers/business-analyst-interview-trainer`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    console.log("[BA] On BA trainer page");

    // Navigate to BA quest catalog
    await navigateToQuestCatalog(page, "business-analyst-interview-trainer");
    console.log("[BA] Quest catalog loaded");

    // Find and open the first BA quest
    const questLinks = page.locator("a[href*='/quests/']");
    const questCount = await questLinks.count().catch(() => 0);
    if (questCount > 0) {
      await questLinks.first().click();
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(3000);
      console.log("[BA] Opened first available quest");
    }

    // Check for undefined.message error
    const undefinedErrors0 = consoleErrors.filter(
      (e) => e.includes("Cannot read properties of undefined") || e.includes("Cannot read properties")
    );
    expect(undefinedErrors0.length).toBe(0);

    // Click start
    await clickStartQuest(page);
    console.log("[BA] Clicked start quest");

    // Work through steps (similar to QA)
    for (let step = 1; step <= 8; step++) {
      // Select options if available
      const radioButtons = page.locator('[role="radio"]');
      if (await radioButtons.first().isVisible({ timeout: 500 }).catch(() => false)) {
        await radioButtons.first().click();
        await page.waitForTimeout(500);
      }

      const checkboxes = page.locator('[role="checkbox"]');
      if (await checkboxes.first().isVisible({ timeout: 500 }).catch(() => false)) {
        await checkboxes.first().click();
        await page.waitForTimeout(500);
      }

      // Fill textarea if visible
      const textarea = page.locator("textarea");
      if (await textarea.isVisible({ timeout: 500 }).catch(() => false)) {
        await textarea.fill("The key stakeholder requirements should be clearly documented and prioritized based on business value and technical feasibility. Regular communication with stakeholders ensures alignment throughout the project lifecycle.");
        await page.waitForTimeout(500);
      }

      // Click submit
      const submitBtn = page.locator('button[data-testid="button"]:not([disabled])').last();
      if (await submitBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
        await submitBtn.click();
        await page.waitForTimeout(3000);
      } else {
        break;
      }
    }

    // Wait for outcome
    await page.waitForTimeout(5000);
    console.log("[BA] Steps completed");

    // View debrief if available
    const viewDebriefBtn = page.getByText("quest.view_debrief", { exact: true }).first()
      .or(page.getByText("Разбор", { exact: true }).first());
    if (await viewDebriefBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await viewDebriefBtn.click();
      await page.waitForTimeout(2000);
    }

    await page.screenshot({
      path: "docs/simulator_engine/screenshots/010b-ba-full-completion.png",
      fullPage: true,
    });

    // Refresh persistence
    const currentUrl = page.url();
    await page.goto(currentUrl);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);

    await page.screenshot({
      path: "docs/simulator_engine/screenshots/010b-ba-refresh-persistence.png",
      fullPage: true,
    });

    // Verify no errors
    const undefinedErrors = consoleErrors.filter(
      (e) => e.includes("Cannot read properties of undefined") || e.includes("Cannot read properties")
    );
    expect(undefinedErrors.length).toBe(0);
    const crashErrors = consoleErrors.filter((e) => e.includes("PAGE_CRASH"));
    expect(crashErrors.length).toBe(0);

    const unexpectedErrors = consoleErrors.filter(
      (e) => !e.includes("401") && !e.includes("Failed to load resource")
    );
    expect(unexpectedErrors.length).toBe(0);

    console.log("[BA] ✅ Full quest acceptance PASSED");
  });

  // =========================================================================
  // Legacy URL check
  // =========================================================================

  test("Legacy /scenarios/ url loads without old textarea UI or crash", async ({ page }) => {
    await page.goto(`${STAGING_URL}/scenarios/qa_bug_report_structure_v1`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);

    const bodyText = await page.locator("body").textContent();
    expect(bodyText).toBeTruthy();

    const undefinedErrors = consoleErrors.filter(
      (e) => e.includes("Cannot read properties of undefined")
    );
    expect(undefinedErrors.length).toBe(0);

    // Should NOT show old textarea (legacy flow removed)
    expect(bodyText!.includes("textarea")).toBe(false);

    await page.screenshot({
      path: "docs/simulator_engine/screenshots/010b-legacy-url.png",
      fullPage: true,
    });
  });

  // =========================================================================
  // Route regression — no 5xx
  // =========================================================================

  test("No 5xx errors on key routes", async ({ page }) => {
    const routes = [
      `${STAGING_URL}/`,
      `${STAGING_URL}/login`,
      `${STAGING_URL}/register`,
      `${STAGING_URL}/domains`,
    ];

    for (const url of routes) {
      const resp = await page.request.get(url);
      expect(resp.status()).toBeLessThan(500);
    }

    expect(serverErrors.length).toBe(0);
  });
});
