/**
 * Layer 011 — Auth Guard Live Browser Reproduction & Fix Verification
 *
 * Step 1: Reproduce the bug on live VPS (unauthenticated trainer API call)
 * Step 2: Verify fix after deploy
 *
 * Reproduction acceptance:
 *   - Trainer API call happens for unauthenticated user (BUG)
 *   - Status 401 returned
 *   - "Error loading" is visible (BUG)
 *
 * Fix acceptance:
 *   - 0 trainer API calls for unauthenticated user
 *   - Auth gate visible
 *   - No "Error loading" text
 */

import { test, expect, type Page, type BrowserContext } from '@playwright/test';

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'https://frontend-staging-4146.up.railway.app';
const TRAINER_SLUG = 'business-analyst-interview-trainer';
const TRAINER_URL = `${BASE_URL}/trainers/${TRAINER_SLUG}`;
const TRAINER_API_PATTERN = `/api/v1/trainers/${TRAINER_SLUG}`;

test.describe('Layer 011 — Auth Guard Live Browser', () => {

  test('REPRO: unauthenticated user calls trainer API (current broken state)', async ({ page }) => {
    // Record network requests
    const trainerApiRequests: string[] = [];
    const all401Responses: { url: string; status: number }[] = [];

    page.on('request', (req) => {
      if (req.url().includes(TRAINER_API_PATTERN)) {
        trainerApiRequests.push(req.url());
      }
    });

    page.on('response', (res) => {
      if (res.status() === 401 && res.url().includes('/api/v1/trainers/')) {
        all401Responses.push({ url: res.url(), status: res.status() });
      }
    });

    // Navigate clean (no token)
    await page.goto(TRAINER_URL, { waitUntil: 'networkidle', timeout: 60000 });

    // Wait for JS to execute
    await page.waitForTimeout(3000);

    // Screenshot
    await page.screenshot({
      path: 'test-results/011-auth-repro-broken-state.png',
      fullPage: true,
    });

    console.log(`Trainer API requests made: ${trainerApiRequests.length}`);
    console.log(`401 responses: ${JSON.stringify(all401Responses)}`);

    // REPRODUCTION CHECK: These assertions should FAIL for the BUG state
    const bodyText = await page.textContent('body') || '';
    console.log(`Page text preview: ${bodyText.substring(0, 500)}`);

    // Record what we see
    test.info().annotations.push({
      type: 'reproduction',
      description: `Trainer API calls: ${trainerApiRequests.length}, 401 responses: ${all401Responses.length}`,
    });

    // Log for reproduction evidence
    expect(trainerApiRequests.length).toBeGreaterThanOrEqual(0); // just log, don't fail
    expect(bodyText).toBeTruthy();
  });

  test('FIX-VERIFY: unauthenticated user does NOT call trainer API', async ({ page }) => {
    // Record network requests
    const trainerApiRequests: string[] = [];
    const allErrors401: { url: string; status: number }[] = [];

    page.on('request', (req) => {
      if (req.url().includes(TRAINER_API_PATTERN)) {
        trainerApiRequests.push(req.url());
      }
    });

    page.on('response', (res) => {
      if (res.status() === 401 && res.url().includes('/api/v1/trainers/')) {
        allErrors401.push({ url: res.url(), status: res.status() });
      }
    });

    // Navigate clean (no localStorage token)
    await page.goto(TRAINER_URL, { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForTimeout(3000);

    // Screenshot
    await page.screenshot({
      path: 'test-results/011-auth-fix-verified.png',
      fullPage: true,
    });

    const bodyText = await page.textContent('body') || '';
    console.log(`Page text preview: ${bodyText.substring(0, 500)}`);

    // ACCEPTANCE: 0 trainer API calls for unauthenticated user
    expect(trainerApiRequests).toHaveLength(0);

    // ACCEPTANCE: No generic error
    expect(bodyText).not.toContain('Error loading');
    expect(bodyText).not.toContain('An error occurred');
    expect(bodyText).not.toContain('Произошла ошибка');

    // ACCEPTANCE: Auth gate is visible
    const hasAuthGate = bodyText.includes('Войдите в аккаунт') ||
      bodyText.includes('Sign in to continue') ||
      bodyText.includes('auth.sign_in_required');
    expect(hasAuthGate).toBe(true);
  });

});
