import { test, expect, Page } from '@playwright/test';

const BASE = 'https://trainer.152.53.227.37.nip.io';
const EMAIL = 'test@test.com';
const PASSWORD = 'testtest';

async function loginViaApi(page: Page) {
  await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded', timeout: 15000 });
  const resp = await page.request.post(`${BASE}/api/v1/auth/login`, {
    data: { email: EMAIL, password: PASSWORD },
  });
  if (resp.ok()) {
    const body = await resp.json();
    await page.evaluate((t) => localStorage.setItem('access_token', t), body.access_token);
    return true;
  }
  return false;
}

async function go(page: Page, path: string) {
  await loginViaApi(page);
  await page.goto(`${BASE}${path}`, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(3000);
}

async function ensureEnrolled(page: Page, path: string) {
  await go(page, path);
  for (const text of ['Enroll', 'Записаться', 'enroll']) {
    const btn = page.locator(`button:has-text("${text}")`);
    if (await btn.isVisible({ timeout: 1000 }).catch(() => false)) {
      await btn.click();
      await page.waitForTimeout(3000);
      await page.goto(`${BASE}${path}`, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
      await page.waitForTimeout(3000);
      break;
    }
  }
}

test.describe('Layer 011 Fix Verification', () => {

  test('FIX-1: No duplicate CTA — only one startQuest header button, recommended CTA shows', async ({ page }) => {
    await ensureEnrolled(page, '/trainers/qa-engineer-interview-trainer');
    await page.screenshot({ path: 'test-results/011-fix-1-no-dup-cta.png', fullPage: true });

    const buttons = await page.locator('button').allTextContents();

    // HEADER: there must be exactly ONE "Start Quest" / "Начать квест" in the header area.
    // This is the legitimate enrolled-user CTA to the quest catalog.
    const headerStartQuest = buttons.filter(t =>
      /^Start Quest$|^Начать квест$/i.test(t.trim())
    );
    expect(headerStartQuest.length).toBe(1);

    // RECOMMENDED QUEST CARD: the primary CTA inside the recommended-quest card
    // must be "Start Recommended Quest" / "Начать рекомендуемый квест" — NOT a second
    // "Start Quest" button. The fix removed the duplicate below the card.
    const primaryRecommended = buttons.filter(t =>
      /Start Recommended Quest|Начать рекомендуемый квест/i.test(t.trim())
    );
    expect(primaryRecommended.length).toBeGreaterThanOrEqual(1);
  });

  test('FIX-2: No raw i18n keys visible in ru-RU trainer page', async ({ page }) => {
    // Set locale to ru-RU
    await ensureEnrolled(page, '/trainers/qa-engineer-interview-trainer');
    await page.evaluate(() => localStorage.setItem('locale', 'ru-RU'));
    await page.goto(`${BASE}/trainers/qa-engineer-interview-trainer`, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(3000);

    const body = await page.textContent('body') || '';
    // Check for raw i18n keys from Layer 011 namespaces
    const rawKeys = (body.match(/([a-z_]+\.[a-z_]+\.[a-z_]+)/gi) || [])
      .filter(k => /^recommended_quest\./.test(k) || /^quest\./.test(k) || /^mission_intro\./.test(k));
    expect(rawKeys).toEqual([]);

    // Check no English description text (the old hardcoded strings)
    const hasEnglishDesc = /This quest covers the fundamentals|This quest introduces core BA skills/i.test(body);
    expect(hasEnglishDesc).toBeFalsy();
  });

  test('FIX-3: No "Session not found" on quest page with stale localStorage', async ({ page }) => {
    const pageErrors: string[] = [];
    page.on('pageerror', e => pageErrors.push(e.message));

    // Clear localStorage to simulate fresh start
    await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => localStorage.clear());
    await loginViaApi(page);

    // Set a stale session in localStorage (simulates old/expired session)
    await page.evaluate(() => localStorage.setItem('quest_session_qa_bug_report_structure_v1', 'stale-invalid-session-123'));

    // Navigate to quest — should not crash with "Session not found"
    await page.goto(`${BASE}/trainers/qa-engineer-interview-trainer/quests/qa_bug_report_structure_v1`,
      { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(4000);
    await page.screenshot({ path: 'test-results/011-fix-3-stale-session.png', fullPage: true });

    const body = await page.textContent('body') || '';
    // No "Session not found" text
    expect(body).not.toContain('Session not found');
    expect(body).not.toContain('Сессия не найдена');

    // No React errors
    expect(pageErrors.length).toBe(0);

    // Page should have meaningful content (either intro or ready state)
    expect(body.length).toBeGreaterThan(100);
  });

  test('FIX-4: ru-RU recommended quest description is Russian, not English', async ({ page }) => {
    // Set ru-RU locale
    await ensureEnrolled(page, '/trainers/qa-engineer-interview-trainer');
    await page.evaluate(() => localStorage.setItem('locale', 'ru-RU'));
    await page.goto(`${BASE}/trainers/qa-engineer-interview-trainer`, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(3000);

    await page.screenshot({ path: 'test-results/011-fix-4-ru-text.png', fullPage: true });

    const body = await page.textContent('body') || '';

    // Russian description text must be present (the fix added ru-RU localization for for_qa_why)
    const hasRussianText = /Этот квест охватывает/i.test(body);
    expect(hasRussianText).toBeTruthy();

    // English description text must NOT be present (the fix replaced hardcoded English with t())
    const hasEnglishText = /This quest covers the fundamentals/i.test(body);
    expect(hasEnglishText).toBeFalsy();
  });

  test('FIX-5: BA page ru-RU uses Russian text', async ({ page }) => {
    await ensureEnrolled(page, '/trainers/business-analyst-interview-trainer');
    await page.evaluate(() => localStorage.setItem('locale', 'ru-RU'));
    await page.goto(`${BASE}/trainers/business-analyst-interview-trainer`, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(3000);

    await page.screenshot({ path: 'test-results/011-fix-5-ba-ru.png', fullPage: true });

    const body = await page.textContent('body') || '';

    // BA recommended quest description should be Russian
    const hasBaRussian = /стейкхолдер|критери|Этот квест знакомит/i.test(body);
    expect(hasBaRussian).toBeTruthy();

    // No English BA description
    const hasEnglishBaDesc = /This quest introduces core BA skills/i.test(body);
    expect(hasEnglishBaDesc).toBeFalsy();
  });

});
