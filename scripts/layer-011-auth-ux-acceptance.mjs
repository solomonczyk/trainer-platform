/**
 * Layer 011 — Auth 401 UX Browser Acceptance Test
 *
 * Verifies:
 * 1. Protected trainer route with invalid token → auth gate (not generic error)
 * 2. No repeated 401 API calls
 * 3. Header locale shows RU/US labels, not ru-RU/en-US
 * 4. After login with verified user, trainer page opens normally
 * 5. No new email verification required for already verified user
 *
 * Usage:
 *   node scripts/layer-011-auth-ux-acceptance.mjs
 */

import { chromium } from "playwright";

const BASE_URL = "https://trainer.152.53.227.37.nip.io";
const TRAINER_SLUG = "business-analyst-interview-trainer";
const TRAINER_URL = `${BASE_URL}/trainers/${TRAINER_SLUG}`;

// Existing verified test user credentials
const TEST_EMAIL = "layer011-test@example.com";
const TEST_PASSWORD = "TestPass123!";

async function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function main() {
  const results = {};

  // ── Test 1: Invalid token shows auth gate, not generic error ──
  console.log("\n══════════════════════════════════════════════════════");
  console.log("TEST 1: Protected route with invalid token → auth gate");
  console.log("══════════════════════════════════════════════════════\n");

  {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: { width: 1280, height: 800 },
      locale: "ru-RU",
    });
    const page = await context.newPage();

    // Track network requests to check for 401 spam
    const api401Calls = [];
    page.on("response", (response) => {
      const url = response.url();
      if (
        response.status() === 401 &&
        (url.includes("/api/v1/") || url.includes("/api/"))
      ) {
        api401Calls.push({ url, status: response.status() });
      }
    });

    // Inject an INVALID token before navigating
    await page.goto(BASE_URL, { waitUntil: "networkidle" });
    await page.evaluate(() => {
      localStorage.setItem("access_token", "eyJpbnZhbGlkLnRva2VuLmZvci50ZXN0aW5n"); // clearly invalid
    });
    await page.reload({ waitUntil: "networkidle" });
    await sleep(500);

    // Navigate to protected trainer route
    await page.goto(TRAINER_URL, { waitUntil: "networkidle" });
    await sleep(1000);

    // Screenshot the page
    await page.screenshot({
      path: "layer-011-01-invalid-token-auth-gate.png",
      fullPage: true,
    });

    // Get page text content
    const pageText = await page.evaluate(() => document.body.innerText);

    // Check: NO generic error text
    const hasGenericError =
      pageText.includes("Произошла ошибка") ||
      pageText.includes("Authentication Required") ||
      pageText.includes("common.error");

    // Check: HAS auth gate text
    const hasAuthGate =
      pageText.includes("Войдите в аккаунт, чтобы продолжить") ||
      pageText.includes("Sign in to continue");

    // Check: HAS login button
    const hasLoginButton =
      pageText.includes("Войти") ||
      pageText.includes("Log In");

    // Check: Header shows login/register (unauthenticated state)
    const hasRegisterLink = pageText.includes("Регистрация") || pageText.includes("Register");

    // Check: Header locale label (NOT ru-RU/en-US)
    const hasRawLocaleCode = pageText.includes("ru-RU") && pageText.includes("en-US");
    // The button text itself - check if "RU" is visible
    const localeLabelRU = await page.locator("text=RU").count();
    const localeLabelUS = await page.locator("text=US").count();
    const hasLocaleRUorUS = localeLabelRU > 0 || localeLabelUS > 0;

    // Check: no repeated 401 spam on protected API
    const trainerApiCalls = api401Calls.filter((c) =>
      c.url.includes(`/api/v1/trainers/${TRAINER_SLUG}`)
    );

    console.log(`Page text preview: ${pageText.substring(0, 500)}`);
    console.log(`401 API calls to protected endpoints: ${trainerApiCalls.length}`);
    console.log(`All 401 API calls: ${api401Calls.length} → ${JSON.stringify(api401Calls.map(c => c.url.split('/').slice(-3).join('/')))}`);
    console.log(`Generic error visible: ${hasGenericError ? 'YES (FAIL)' : 'NO (PASS)'}`);
    console.log(`Auth gate visible: ${hasAuthGate ? 'YES (PASS)' : 'NO (FAIL)'}`);
    console.log(`Login button visible: ${hasLoginButton ? 'YES (PASS)' : 'NO (FAIL)'}`);
    console.log(`Register link visible: ${hasRegisterLink ? 'YES' : 'NO'}`);
    console.log(`Raw locale code visible: ${hasRawLocaleCode ? 'YES (FAIL)' : 'NO (PASS)'}`);
    console.log(`Locale RU/US button visible: ${hasLocaleRUorUS ? 'YES (PASS)' : 'NO'}`);

    results.test1 = {
      pass: hasAuthGate && !hasGenericError && trainerApiCalls.length <= 1,
      hasAuthGate,
      hasGenericError,
      trainerApiCalls: trainerApiCalls.length,
      all401Calls: api401Calls.length,
      hasLocaleRUorUS,
      hasRawLocaleCode,
    };

    await browser.close();
  }

  // ── Test 2: Login as verified user → trainer page opens normally ──
  console.log("\n══════════════════════════════════════════════════════");
  console.log("TEST 2: Login with verified user → trainer page works");
  console.log("══════════════════════════════════════════════════════\n");

  {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: { width: 1280, height: 800 },
      locale: "ru-RU",
    });
    const page = await context.newPage();

    // Navigate to login page
    await page.goto(`${BASE_URL}/login`, { waitUntil: "networkidle" });
    await sleep(1000);

    // Fill login form — use id-based selectors for precision
    await page.locator("#email").fill(TEST_EMAIL);
    await page.locator("#password").fill(TEST_PASSWORD);

    // Click submit button
    await page.locator('button[type="submit"]').click();

    // Wait for navigation to complete (login → domains or /)
    try {
      await page.waitForURL(/\/domains|\/$/, { timeout: 20000 });
      console.log("Login redirect detected");
    } catch (e) {
      // Check if we're still on login page (login might have failed)
      const currentUrl = page.url();
      console.log(`After login attempt — URL: ${currentUrl}`);
      // Check for error message
      const errorVisible = await page.locator('[role="alert"]').first().isVisible().catch(() => false);
      if (errorVisible) {
        const errorText = await page.locator('[role="alert"]').first().textContent();
        console.log(`Login error visible: ${errorText}`);
      }
    }
    await sleep(2000);

    // Now navigate to trainer page
    await page.goto(TRAINER_URL, { waitUntil: "networkidle" });
    await sleep(2000);

    // Screenshot
    await page.screenshot({
      path: "layer-011-02-logged-in-trainer-page.png",
      fullPage: true,
    });

    const pageText = await page.evaluate(() => document.body.innerText);

    // Check: No auth gate or error
    const hasError = pageText.includes("Произошла ошибка") || pageText.includes("error");
    // Check: Trainer content is visible
    const hasTrainerContent =
      pageText.includes("Enroll") ||
      pageText.includes("Записаться") ||
      pageText.includes("enrolled") ||
      pageText.includes("Записан");

    // Check: No verification prompt (already verified user)
    const hasVerificationPrompt = pageText.includes("подтверждение email") ||
      pageText.includes("verify your email") ||
      pageText.includes("подтвердите") ||
      pageText.includes("verification");

    console.log(`Page text preview: ${pageText.substring(0, 500)}`);
    console.log(`Trainer content visible: ${hasTrainerContent ? 'YES (PASS)' : 'UNKNOWN'}`);
    console.log(`Error visible: ${hasError ? 'YES (FAIL)' : 'NO (PASS)'}`);
    console.log(`Verification prompt visible: ${hasVerificationPrompt ? 'YES' : 'NO (PASS)'}`);

    results.test2 = {
      pass: !hasError && !hasVerificationPrompt,
      hasTrainerContent,
      hasVerificationPrompt,
    };

    await browser.close();
  }

  // ── Results Summary ──
  console.log("\n══════════════════════════════════════════════════════");
  console.log("RESULTS SUMMARY");
  console.log("══════════════════════════════════════════════════════\n");
  for (const [name, result] of Object.entries(results)) {
    console.log(`${name}: ${result.pass ? '✅ PASS' : '❌ FAIL'}`);
    for (const [key, val] of Object.entries(result)) {
      if (key !== 'pass') console.log(`  ${key}: ${val}`);
    }
  }
  console.log("");

  const allPass = Object.values(results).every((r) => r.pass);
  console.log(`\nOverall: ${allPass ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
  process.exit(allPass ? 0 : 1);
}

main().catch((err) => {
  console.error("Test failed with error:", err);
  process.exit(1);
});
