/**
 * Layer 011 — REPRODUCTION: Unauthenticated Protected Trainer Route
 *
 * Required test behavior:
 * 1. Clean unauthenticated browser context (no token, no session)
 * 2. Navigate to protected trainer URL
 * 3. Assert: 0 trainer API requests, no generic error, auth gate visible
 *
 * This test is expected to FAIL BEFORE the fix is deployed.
 * It MUST PASS after the fix.
 */

import { test, expect } from "@playwright/test";

const BASE_URL =
  process.env.BASE_URL ?? "https://trainer.152.53.227.37.nip.io";

test.describe("Layer 011 — REPRO: Unauthenticated Protected Trainer Route", () => {
  test("REPRO: unauthenticated protected trainer route must not call trainer API", async ({
    page,
  }) => {
    const trainerRequests: string[] = [];

    page.on("request", (req) => {
      if (
        req.url().includes("/api/v1/trainers/business-analyst-interview-trainer")
      ) {
        trainerRequests.push(req.url());
      }
    });

    await page.goto(
      `${BASE_URL}/trainers/business-analyst-interview-trainer`,
      {
        waitUntil: "networkidle",
      }
    );

    await page.waitForTimeout(2000);

    const errorVisible = await page
      .getByText(/Error loading|Произошла ошибка/i)
      .isVisible()
      .catch(() => false);
    const authGateVisible = await page
      .getByText(/Войдите в аккаунт|Sign in to continue|Log In|Войти/i)
      .isVisible()
      .catch(() => false);

    console.log(
      JSON.stringify(
        {
          trainer_request_count: trainerRequests.length,
          trainer_requests: trainerRequests,
          error_visible: errorVisible,
          auth_gate_visible: authGateVisible,
        },
        null,
        2
      )
    );

    // Log full page text for diagnostics
    const bodyText = await page.textContent("body").catch(() => "");
    console.log("Page body text (EN):", bodyText?.substring(0, 800));

    // HARD ASSERTIONS
    expect(trainerRequests).toHaveLength(0);

    // Check body text for no generic error
    expect(bodyText).not.toContain("Error loading");
    expect(bodyText).not.toContain("Произошла ошибка");
    expect(bodyText).not.toContain("common.error");

    // Auth gate or login redirect must be visible in the DOM
    const hasAuthGate =
      bodyText.includes("Войдите в аккаунт") ||
      bodyText.includes("Sign in to continue") ||
      bodyText.includes("auth.sign_in_required");
    expect(hasAuthGate).toBe(true);
  });

  test("REPRO: RU locale shows Russian auth gate with no English text", async ({
    page,
  }) => {
    const trainerRequests: string[] = [];

    page.on("request", (req) => {
      if (
        req.url().includes("/api/v1/trainers/business-analyst-interview-trainer")
      ) {
        trainerRequests.push(req.url());
      }
    });

    // Set Russian locale via localStorage before navigation
    await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });
    await page.evaluate(() => localStorage.setItem("locale", "ru-RU"));

    await page.goto(
      `${BASE_URL}/trainers/business-analyst-interview-trainer`,
      {
        waitUntil: "networkidle",
      }
    );

    await page.waitForTimeout(2000);

    const bodyText = await page.textContent("body").catch(() => "");
    console.log("RU page text:", bodyText?.substring(0, 500));

    // 0 trainer API calls
    expect(trainerRequests).toHaveLength(0);

    // Russian auth gate must be visible
    expect(bodyText).toContain("Войдите в аккаунт");
    expect(bodyText).toContain("Войти");

    // No generic error
    expect(bodyText).not.toContain("Произошла ошибка");
    expect(bodyText).not.toContain("Error loading");

    // No English "Log In" in header (must be localized)
    expect(bodyText).not.toContain("Log In");
  });
});
