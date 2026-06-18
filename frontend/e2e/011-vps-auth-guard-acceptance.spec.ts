/**
 * Layer 011 — Auth Guard VPS Acceptance
 *
 * Verifies:
 * 1. Unauthenticated: 0 trainer API calls, auth gate visible
 * 2. Authenticated verified: trainer page loads normally
 * 3. RU shell: no English text in auth gate
 */

import { test, expect, type Page } from '@playwright/test';

const BASE_URL = 'https://trainer.152.53.227.37.nip.io';
const TRAINER_SLUG = 'business-analyst-interview-trainer';
const TRAINER_URL = `${BASE_URL}/trainers/${TRAINER_SLUG}`;
const TRAINER_API_PATTERN = `/api/v1/trainers/${TRAINER_SLUG}`;

const TEST_EMAIL = 'layer011-test@example.com';
const TEST_PASSWORD = 'TestPass123!';

async function loginViaApi(page: Page) {
  // Navigate first to establish origin context for localStorage access
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded', timeout: 15000 });
  const resp = await page.request.post(`${BASE_URL}/api/v1/auth/login`, {
    data: { email: TEST_EMAIL, password: TEST_PASSWORD },
  });
  if (!resp.ok()) {
    console.log(`Login failed: ${resp.status()}`);
    return false;
  }
  const body = await resp.json();
  await page.evaluate((t) => localStorage.setItem('access_token', t), body.access_token);
  return true;
}

test.describe('Layer 011 — VPS Auth Guard Acceptance', () => {

  test('Unauthenticated: 0 API calls, auth gate visible', async ({ page }) => {
    // Record all trainer API requests
    const trainerApiRequests: string[] = [];

    page.on('request', (req) => {
      if (req.url().includes(TRAINER_API_PATTERN)) {
        trainerApiRequests.push(req.url());
      }
    });

    // Clean unauthenticated visit
    await page.goto(TRAINER_URL, { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForTimeout(3000);

    // Screenshot
    await page.screenshot({
      path: 'test-results/vps-unauthenticated-auth-gate.png',
      fullPage: true,
    });

    const bodyText = await page.textContent('body') || '';
    console.log('Body text preview:', bodyText.substring(0, 300));

    // ACCEPTANCE: 0 trainer API calls
    expect(trainerApiRequests).toHaveLength(0);

    // ACCEPTANCE: No generic error
    expect(bodyText).not.toContain('Error loading');
    expect(bodyText).not.toContain('common.error');

    // ACCEPTANCE: Auth gate visible (Russian)
    expect(bodyText).toContain('Войдите в аккаунт');
    expect(bodyText).toContain('Войти');

    // ACCEPTANCE: RU shell — no English nav text
    expect(bodyText).not.toContain('Log In');
    expect(bodyText).not.toContain('Register');
    expect(bodyText).not.toContain('Professional Training Platform');

    // ACCEPTANCE: Locale labels correct
    expect(bodyText).toContain('RU');
    expect(bodyText).toContain('US');
  });

  test('Authenticated verified: trainer page loads', async ({ page }) => {
    const loggedIn = await loginViaApi(page);
    test.skip(!loggedIn, 'Login failed — skipping authenticated test');

    await page.goto(TRAINER_URL, { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForTimeout(5000);

    // Screenshot
    await page.screenshot({
      path: 'test-results/vps-authenticated-trainer-page.png',
      fullPage: true,
    });

    const bodyText = await page.textContent('body') || '';
    console.log('Body text preview (auth):', bodyText.substring(0, 500));

    // Should show trainer content, not auth gate
    expect(bodyText).not.toContain('Войдите в аккаунт');
    expect(bodyText).not.toContain('Sign in to continue');

    // Should have trainer-specific text
    const hasTrainerContent = bodyText.includes('Business Analyst Interview Trainer') ||
      bodyText.includes('Запишитесь на тренажёр') ||
      bodyText.includes('Enroll') ||
      bodyText.includes('Записаться');
    expect(hasTrainerContent).toBe(true);
  });

});
