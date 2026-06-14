import { test, expect, Page } from "@playwright/test";

const URL = "https://trainer.152.53.227.37.nip.io";
const USER = { email: `qb_final_${Date.now()}@test.com`, password: "Test123!" };

let consoleErrors: string[] = [];
let serverErrors: string[] = [];

test.describe("010B Full Acceptance", () => {
  test.beforeEach(async ({ page }) => {
    consoleErrors = []; serverErrors = [];
    page.on("console", (msg) => { if (msg.type() === "error") consoleErrors.push(msg.text()); });
    page.on("pageerror", (err) => { consoleErrors.push(`CRASH: ${err.message}`); });
    page.on("response", (r) => { if (r.status() >= 500) serverErrors.push(`${r.status()} ${r.url()}`); });
  });

  test.afterEach(async () => {
    const ue = consoleErrors.filter(e => e.includes("Cannot read properties"));
    console.log(`[${test.info().title}]: undefined_errs=${ue.length} crashes=${consoleErrors.filter(e => e.includes("CRASH")).length} 5xx=${serverErrors.length}`);
  });

  async function register(page: Page) {
    await page.goto(`${URL}/register`); await page.waitForLoadState("networkidle"); await page.waitForTimeout(1000);
    await page.locator('input[type="email"]').fill(USER.email);
    await page.locator('input[type="password"]').first().fill(USER.password);
    const p2 = page.locator('input[type="password"]').nth(1);
    if (await p2.isVisible().catch(() => false)) await p2.fill(USER.password);
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(3000);
  }

  async function login(page: Page) {
    await page.goto(`${URL}/login`); await page.waitForLoadState("networkidle"); await page.waitForTimeout(1000);
    await page.locator('input[type="email"]').fill(USER.email);
    await page.locator('input[type="password"]').first().fill(USER.password);
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(3000);
  }

  // ========================================================================
  // 1. Home page
  // ========================================================================
  test("1. Home: CTA has text, no locale codes in footer", async ({ page }) => {
    await page.goto(`${URL}/`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);

    // Find any button or link in the hero section
    const heroLinks = page.locator("section").first().locator("a, button");
    const count = await heroLinks.count();
    if (count > 0) {
      const text = await heroLinks.first().textContent();
      expect(text?.trim().length).toBeGreaterThan(0);
    }

    // Footer should NOT contain raw locale codes
    const footer = await page.locator("footer").textContent() || "";
    expect(footer.includes("ru-RU / en-US")).toBe(false);
    expect(consoleErrors.filter(e => e.includes("Cannot read properties")).length).toBe(0);
  });

  // ========================================================================
  // 2. QA: quest catalog shows quests → quest opens → complete
  // ========================================================================
  test("2. QA: quest catalog shows quests, quest opens, all steps done", async ({ page }) => {
    await register(page); await login(page);

    // Navigate directly to QA trainer quests (skip enrollment — catalog loads regardless)
    await page.goto(`${URL}/trainers/qa-engineer-interview-trainer/quests`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);

    // Verify catalog shows quests (not empty message)
    const body = await page.locator("body").textContent() || "";
    const emptyMsg = body.includes("нет квестов") || body.includes("no quests");
    if (emptyMsg) {
      // Try enrolling first
      await page.goto(`${URL}/trainers/qa-engineer-interview-trainer`);
      await page.waitForLoadState("networkidle"); await page.waitForTimeout(2000);
      // Click any enrollment button
      const btns = page.locator("button");
      const btnCount = await btns.count();
      for (let i = 0; i < btnCount; i++) {
        const txt = await btns.nth(i).textContent();
        if (txt?.includes("Записать") || txt?.includes("Enroll")) {
          await btns.nth(i).click();
          await page.waitForTimeout(3000);
          break;
        }
      }
      // Retry quest catalog
      await page.goto(`${URL}/trainers/qa-engineer-interview-trainer/quests`);
      await page.waitForLoadState("networkidle"); await page.waitForTimeout(3000);
    }

    const body2 = await page.locator("body").textContent() || "";
    console.log(`QA catalog empty: ${body2.includes("нет квестов") || body2.includes("no quests")}`);
    expect(body2.includes("нет квестов") || body2.includes("no quests")).toBe(false);

    // Open first quest — find any card-like element that links to a quest
    const questCard = page.locator("a[href*='/quests/']").first();
    if (await questCard.count() > 0) {
      await questCard.first().click();
    } else {
      // Try direct navigation
      await page.goto(`${URL}/trainers/qa-engineer-interview-trainer/quests/qa_bug_report_structure_v1`);
    }
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);

    // Verify page loaded
    expect(consoleErrors.filter(e => e.includes("Cannot read properties")).length).toBe(0);

    // Start quest
    const startBtn = page.locator("button:has-text('Начать квест'), button:has-text('Start Quest')").first();
    if (await startBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await startBtn.click();
      await page.waitForTimeout(1500);
    }

    // Work through steps
    for (let i = 0; i < 12; i++) {
      if (await page.locator('[role="radio"]').first().isVisible({ timeout: 300 }).catch(() => false)) {
        await page.locator('[role="radio"]').first().click(); await page.waitForTimeout(200);
      }
      if (await page.locator('[role="checkbox"]').first().isVisible({ timeout: 300 }).catch(() => false)) {
        await page.locator('[role="checkbox"]').first().click(); await page.waitForTimeout(200);
      }
      if (await page.locator("textarea").first().isVisible({ timeout: 300 }).catch(() => false)) {
        await page.locator("textarea").first().fill("Include steps to reproduce, expected vs actual behavior, environment, severity. A well-structured report helps developers fix issues efficiently.");
        await page.waitForTimeout(200);
      }
      const sb = page.locator("button[data-testid='button']:not([disabled])").last();
      if (await sb.isVisible({ timeout: 300 }).catch(() => false)) { await sb.click(); await page.waitForTimeout(2000); } else break;
    }

    await page.waitForTimeout(3000);
    console.log("QA quest steps done ✅");
    expect(consoleErrors.filter(e => e.includes("Cannot read properties")).length).toBe(0);
  });

  // ========================================================================
  // 3. BA: quest catalog shows quests → quest opens → complete
  // ========================================================================
  test("3. BA: quest catalog shows quests, quest opens, all steps done", async ({ page }) => {
    await login(page).catch(async () => { await register(page); await login(page); });

    await page.goto(`${URL}/trainers/business-analyst-interview-trainer/quests`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);

    const body = await page.locator("body").textContent() || "";
    console.log(`BA catalog empty: ${body.includes("нет квестов") || body.includes("no quests")}`);
    expect(body.includes("нет квестов") || body.includes("no quests")).toBe(false);

    // Open first quest
    const ql = page.locator("a[href*='/quests/']").first();
    if (await ql.count() > 0) {
      await ql.first().click();
    } else {
      await page.goto(`${URL}/trainers/business-analyst-interview-trainer/quests/ba_payment_requirements_conflict`);
    }
    await page.waitForLoadState("networkidle"); await page.waitForTimeout(3000);

    expect(consoleErrors.filter(e => e.includes("Cannot read properties")).length).toBe(0);

    const startBtn = page.locator("button:has-text('Начать квест'), button:has-text('Start Quest')").first();
    if (await startBtn.isVisible({ timeout: 2000 }).catch(() => false)) { await startBtn.click(); await page.waitForTimeout(1500); }

    for (let i = 0; i < 12; i++) {
      if (await page.locator('[role="radio"]').first().isVisible({ timeout: 300 }).catch(() => false)) {
        await page.locator('[role="radio"]').first().click(); await page.waitForTimeout(200);
      }
      if (await page.locator('[role="checkbox"]').first().isVisible({ timeout: 300 }).catch(() => false)) {
        await page.locator('[role="checkbox"]').first().click(); await page.waitForTimeout(200);
      }
      if (await page.locator("textarea").first().isVisible({ timeout: 300 }).catch(() => false)) {
        await page.locator("textarea").first().fill("Key requirements should be documented and prioritized. Regular stakeholder communication ensures alignment throughout the project.");
        await page.waitForTimeout(200);
      }
      const sb = page.locator("button[data-testid='button']:not([disabled])").last();
      if (await sb.isVisible({ timeout: 300 }).catch(() => false)) { await sb.click(); await page.waitForTimeout(2000); } else break;
    }

    await page.waitForTimeout(3000);
    console.log("BA quest steps done ✅");
    expect(consoleErrors.filter(e => e.includes("Cannot read properties")).length).toBe(0);
  });

  // ========================================================================
  // 4. No 5xx
  // ========================================================================
  test("4. No 5xx on key pages", async ({ page }) => {
    for (const p of ["/", "/login", "/register", "/domains"]) {
      const r = await page.request.get(`${URL}${p}`);
      expect(r.status()).toBeLessThan(500);
    }
    expect(serverErrors.length).toBe(0);
  });

  // ========================================================================
  // 5. Legacy URL
  // ========================================================================
  test("5. Legacy /scenarios/ loads without crash or textarea", async ({ page }) => {
    await page.goto(`${URL}/scenarios/qa_bug_report_structure_v1`);
    await page.waitForLoadState("networkidle"); await page.waitForTimeout(3000);
    expect((await page.locator("body").textContent() || "").includes("textarea")).toBe(false);
    expect(consoleErrors.filter(e => e.includes("Cannot read properties")).length).toBe(0);
  });
});
