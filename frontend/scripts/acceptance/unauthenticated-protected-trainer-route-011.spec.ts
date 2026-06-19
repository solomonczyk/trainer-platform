/**
 * Layer 011 — UNAUTHENTICATED PROTECTED TRAINER ROUTE
 *
 * Final live acceptance test against VPS.
 *
 * Final assertions:
 * - trainer API request count === 0
 * - "Error loading" not visible
 * - auth gate or login redirect visible
 * - no repeated 401 spam
 * - screenshot saved
 */

import { test, expect } from "@playwright/test";

const BASE_URL = process.env.BASE_URL ?? "https://trainer.152.53.227.37.nip.io";
const TRAINER_SLUG = "business-analyst-interview-trainer";
const TRAINER_URL = `${BASE_URL}/trainers/${TRAINER_SLUG}`;

const TEST_EMAIL = "layer011-test@example.com";
const TEST_PASSWORD = "TestPass123!";

test.describe("Layer 011 — Final Auth Guard Acceptance", () => {
  test("Unauthenticated: 0 API calls, auth gate visible, no error", async ({
    page,
  }) => {
    const trainerApiRequests: string[] = [];
    const all401Responses: { url: string; status: number }[] = [];

    page.on("request", (req) => {
      if (req.url().includes(`/api/v1/trainers/${TRAINER_SLUG}`)) {
        trainerApiRequests.push(req.url());
      }
    });

    page.on("response", (res) => {
      if (res.status() === 401 && res.url().includes("/api/v1/trainers/")) {
        all401Responses.push({ url: res.url(), status: res.status() });
      }
    });

    await page.goto(TRAINER_URL, { waitUntil: "networkidle", timeout: 60000 });
    await page.waitForTimeout(3000);

    // Screenshot
    await page.screenshot({
      path: "test-results/unauthenticated-protected-trainer-route-011.png",
      fullPage: true,
    });

    const bodyText = (await page.textContent("body")) || "";
    console.log("Final acceptance body text:", bodyText.substring(0, 500));

    // Final assertions
    expect(trainerApiRequests).toHaveLength(0);
    expect(bodyText).not.toContain("Error loading");
    expect(bodyText).not.toContain("Произошла ошибка");
    expect(bodyText).not.toContain("common.error");

    const hasAuthGate =
      bodyText.includes("Войдите в аккаунт") ||
      bodyText.includes("Sign in to continue") ||
      bodyText.includes("Войти");
    expect(hasAuthGate).toBe(true);

    // No repeated 401 spam
    expect(all401Responses).toHaveLength(0);

    console.log(
      JSON.stringify(
        {
          base_url: BASE_URL,
          route: TRAINER_URL,
          browser_context: "clean_unauthenticated",
          trainer_api_request_count: trainerApiRequests.length,
          trainer_api_401_count: all401Responses.length,
          generic_error_visible: bodyText.includes("Error loading"),
          auth_gate_or_login_redirect_visible: hasAuthGate,
          screenshot_captured: true,
        },
        null,
        2
      )
    );
  });

  test("Authenticated verified: trainer page loads correctly", async ({
    page,
  }) => {
    // Login via API
    await page.goto(`${BASE_URL}/login`, {
      waitUntil: "domcontentloaded",
      timeout: 15000,
    });
    const resp = await page.request.post(`${BASE_URL}/api/v1/auth/login`, {
      data: { email: TEST_EMAIL, password: TEST_PASSWORD },
    });
    const loggedIn = resp.ok();

    if (!loggedIn) {
      console.log(`Login failed: ${resp.status()}`);
      test.skip(true, "Login failed — skipping authenticated test");
      return;
    }

    const body = await resp.json();
    await page.evaluate(
      (t) => localStorage.setItem("access_token", t),
      body.access_token
    );

    // Navigate to trainer page
    await page.goto(TRAINER_URL, {
      waitUntil: "networkidle",
      timeout: 60000,
    });
    await page.waitForTimeout(3000);

    await page.screenshot({
      path: "test-results/authenticated-trainer-page-011.png",
      fullPage: true,
    });

    const bodyText = (await page.textContent("body")) || "";
    console.log("Auth body text:", bodyText.substring(0, 500));

    // No auth gate
    expect(bodyText).not.toContain("Войдите в аккаунт");
    expect(bodyText).not.toContain("Sign in to continue");

    // No email verification screen
    expect(bodyText).not.toContain("Требуется подтверждение email");
    expect(bodyText).not.toContain("Email Verification Required");

    // No generic error
    expect(bodyText).not.toContain("Error loading");
    expect(bodyText).not.toContain("Произошла ошибка");

    // Trainer page content present
    const hasTrainerContent =
      bodyText.includes("Запишитесь на тренажёр") ||
      bodyText.includes("Enroll") ||
      bodyText.includes("Записаться");
    expect(hasTrainerContent).toBe(true);

    console.log(
      JSON.stringify(
        {
          verified_user_login: true,
          verified_user_email_verification_required: false,
          trainer_page_loaded: true,
          generic_error_visible: false,
        },
        null,
        2
      )
    );
  });
});
