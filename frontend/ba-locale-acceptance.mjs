/**
 * Locale Switch Reactivity — Browser Acceptance Test
 *
 * Verifies that switching language updates visible text immediately
 * without manual page refresh.
 *
 * Usage: node ba-locale-acceptance.mjs
 */

import { chromium } from 'playwright';
import { readFileSync, existsSync } from 'fs';

const BASE = 'https://trainer.152.53.227.37.nip.io';
const TRAINER_SLUG = 'business-analyst-interview-trainer';

let TOKEN = process.env.TOKEN || '';
if (!TOKEN && existsSync('./ba_quiz_token.txt')) {
  TOKEN = readFileSync('./ba_quiz_token.txt', 'utf8').trim();
}
if (!TOKEN) {
  console.error('No token. Run setup first.');
  process.exit(1);
}

const SHOTS = [];
let passed = 0;
let failed = 0;

function check(name, condition) {
  if (condition) { console.log('  [PASS] ' + name); passed++; }
  else { console.log('  [FAIL] ' + name); failed++; }
}

async function shot(page, label) {
  const path = 'screenshots/ba-locale-' + label + '.png';
  await page.screenshot({ path, fullPage: true });
  SHOTS.push(path);
  console.log('  Screenshot: ' + path);
}

async function run() {
  console.log('=== Locale Switch Reactivity Test ===\n');

  const browser = await chromium.launch({
    headless: true,
    args: ['--ignore-certificate-errors'],
  });
  const ctx = await browser.newPage();
  const page = ctx;

  page.on('pageerror', () => {});

  try {
    // Setup auth
    await page.goto(BASE + '/login', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(500);
    await page.evaluate((t) => { localStorage.setItem('access_token', t); }, TOKEN);
    console.log('Auth token set\n');

    // ================================================================
    // 1. Open BA trainer page in ru-RU
    // ================================================================
    console.log('=== 1. Page in ru-RU ===');
    await page.goto(BASE + '/trainers/' + TRAINER_SLUG, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);
    await shot(page, '01-ru-initial');

    let body = await page.locator('body').innerText();
    const hasRussian = body.includes('Модули') || body.includes('Записаться') || body.includes('Тренажёр');
    check('1. ru-RU text visible initially', hasRussian);

    // ================================================================
    // 2. Switch to English via "English" button
    // ================================================================
    console.log('\n=== 2. Switch to English ===');
    // Click the English button in the locale switcher (footer or header)
    const enBtn = page.locator('button:has-text("English")');
    if (await enBtn.isVisible().catch(() => false)) {
      await enBtn.click();
      await page.waitForTimeout(1500); // Wait for React re-render
      await shot(page, '02-en-after-switch');

      body = await page.locator('body').innerText();
      const hasEnglish = body.includes('Modules') || body.includes('Domains') || body.includes('Business Analyst');
      check('2. English text visible after switch (no refresh)', hasEnglish);

      // Check no mixed Russian text in key labels
      const hasMixedRussian = body.includes('Модули') && body.includes('Modules');
      check('3. No mixed language in nav labels', !hasMixedRussian);
    } else {
      console.log('  English button not found');
      check('2. English button clickable', false);
    }

    // ================================================================
    // 3. Switch back to Russian
    // ================================================================
    console.log('\n=== 3. Switch back to Russian ===');
    const ruBtn = page.locator('button:has-text("Русский")');
    if (await ruBtn.isVisible().catch(() => false)) {
      await ruBtn.click();
      await page.waitForTimeout(1500);
      await shot(page, '03-ru-after-switch-back');

      body = await page.locator('body').innerText();
      const ruBack = body.includes('Модули') || body.includes('Записаться') || body.includes('Тренажёр');
      check('4. Russian text after switch back', ruBack);

      const hasEnglishAfter = body.includes('Modules') && body.includes('Business Analyst Interview Trainer');
      check('5. No English text in key labels after switch back', !hasEnglishAfter);
    } else {
      console.log('  Russian button not found');
      check('4. Russian button clickable', false);
    }

    // ================================================================
    // 4. Locale persists after reload
    // ================================================================
    console.log('\n=== 4. Reload — locale persists ===');
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    await shot(page, '04-after-reload');

    body = await page.locator('body').innerText();
    const persists = body.includes('Модули') || body.includes('Записаться') || body.includes('Тренажёр');
    check('6. Locale persists after reload (still Russian)', persists);

    // ================================================================
    // 5. Locale switch on module page
    // ================================================================
    console.log('\n=== 5. Locale switch on module page ===');

    // Enroll first if needed
    const enrollBtn = page.locator('button:has-text("Записаться на курс")');
    if (await enrollBtn.isVisible().catch(() => false)) {
      await enrollBtn.first().click();
      await page.waitForTimeout(2000);
    }

    // Navigate to a module
    const modLinks = page.locator('a[href*="/modules/"]');
    if (await modLinks.first().isVisible().catch(() => false)) {
      await modLinks.first().click();
      await page.waitForTimeout(2000);
    } else {
      // Expand module section
      const modSection = page.locator('button:has-text("Модули")');
      if (await modSection.isVisible().catch(() => false)) await modSection.click();
      await page.waitForTimeout(500);
      const showAll = page.locator('button:has-text("Показать все")');
      if (await showAll.isVisible().catch(() => false)) await showAll.click();
      await page.waitForTimeout(500);
      const ml2 = page.locator('a[href*="/modules/"]');
      if (await ml2.first().isVisible().catch(() => false)) {
        await ml2.first().click();
        await page.waitForTimeout(2000);
      }
    }

    await shot(page, '05-module-ru');
    body = await page.locator('body').innerText();
    const modInRu = body.includes('Начать тестирование');
    check('7. Module page in Russian', modInRu);

    // Switch to English on module page
    const enBtn2 = page.locator('button:has-text("English")');
    if (await enBtn2.isVisible().catch(() => false)) {
      await enBtn2.click();
      await page.waitForTimeout(1500);
      await shot(page, '06-module-en');

      body = await page.locator('body').innerText();
      const modInEn = body.includes('Start Test') || body.includes('Question Bank');
      check('8. Module page switches to English without refresh', modInEn);
    }

    // ================================================================
    // 6. No raw i18n keys after switch
    // ================================================================
    const rawKeys = body.match(/ba_trainer\.|modules\.\w+\.(title|description)|ba_\w+_q\d+_explanation/g);
    check('9. No raw i18n keys after locale switch', !rawKeys || rawKeys.length === 0);

    // ================================================================
    // SUMMARY
    // ================================================================
    console.log('\n========================================');
    console.log('  PASSED: ' + passed + '  FAILED: ' + failed);
    console.log('========================================');
    for (const s of SHOTS) console.log('  ' + s);
    console.log('\nproduction_accepted=false');
    console.log('release_allowed=false');

    if (failed > 0) {
      console.log('\n❌ Some checks FAILED');
      process.exit(1);
    } else {
      console.log('\n✅ All checks PASSED');
    }

  } catch (err) {
    console.error('\nERROR: ' + err.message);
    await shot(page, 'error').catch(() => {});
    process.exit(1);
  } finally {
    await browser.close();
  }
}

run();
