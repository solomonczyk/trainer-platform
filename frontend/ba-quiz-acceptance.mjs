/**
 * BA Module Quiz Flow — Browser Acceptance Test
 *
 * Usage: TOKEN=<jwt> node ba-quiz-acceptance.mjs
 *   or:  node ba-quiz-acceptance.mjs <token-file>
 *
 * If no TOKEN env var and no argument, reads ./ba_quiz_token.txt
 */

import { chromium } from 'playwright';
import { readFileSync, existsSync } from 'fs';

const BASE = 'https://trainer.152.53.227.37.nip.io';
const TRAINER_SLUG = 'business-analyst-interview-trainer';
const SHOTS = [];

// Get token
let TOKEN = process.env.TOKEN || '';
if (!TOKEN && process.argv[2]) {
  try { TOKEN = readFileSync(process.argv[2], 'utf8').trim(); } catch {}
}
if (!TOKEN && existsSync('./ba_quiz_token.txt')) {
  try { TOKEN = readFileSync('./ba_quiz_token.txt', 'utf8').trim(); } catch {}
}
if (!TOKEN) {
  console.error('No auth token provided. Set TOKEN env var or pass path to token file.');
  process.exit(1);
}

let passed = 0;
let failed = 0;

function check(name, condition) {
  if (condition) { console.log('  [PASS] ' + name); passed++; }
  else { console.log('  [FAIL] ' + name); failed++; }
}

async function shot(page, label) {
  const path = 'screenshots/ba-accept-' + label + '.png';
  await page.screenshot({ path, fullPage: true });
  SHOTS.push(path);
  console.log('  Screenshot: ' + path);
}

async function run() {
  console.log('=== BA Module Quiz Acceptance Test ===\n');

  const browser = await chromium.launch({
    headless: true,
    args: ['--ignore-certificate-errors'],
  });
  const ctx = await browser.newContext({ locale: 'ru-RU' });
  const page = await ctx.newPage();
  page.on('pageerror', () => {});

  try {
    // Set auth token in localStorage
    await page.goto(BASE + '/login', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(500);
    await page.evaluate((t) => { localStorage.setItem('access_token', t); }, TOKEN);
    console.log('Auth token set\n');

    // ================================================================
    // 1. BA TRAINER PAGE
    // ================================================================
    console.log('=== 1. BA Trainer page ===');
    await page.goto(BASE + '/trainers/' + TRAINER_SLUG, {
      waitUntil: 'networkidle', timeout: 30000,
    });
    await page.waitForTimeout(3000);
    await shot(page, '01-trainer-page');

    const pageText = await page.locator('body').innerText();
    if (pageText.includes('Authentication required') || pageText.includes('Произошла ошибка')) {
      throw new Error('Auth failed: ' + pageText.substring(0, 300));
    }
    console.log('  Trainer page loaded\n');

    // Enroll with any available button
    const enrollBtn = page.locator('button:has-text("Записаться на курс")');
    if (await enrollBtn.first().isVisible().catch(() => false)) {
      console.log('  Enrolling...');
      await enrollBtn.first().click();
      await page.waitForTimeout(2000);
      await shot(page, '02-enrolled');
      console.log('  Enrolled');
    }

    // ================================================================
    // 2. MODULE PAGE — expect START SCREEN
    // ================================================================
    console.log('=== 2. Module page — start screen ===');

    // Find module link — try expanding collapsed section
    let modLinks = page.locator('a[href*="/modules/"]');
    let modCount = await modLinks.count();
    console.log('  Module links: ' + modCount);

    if (modCount === 0) {
      // Click modules section header
      const modHeader = page.locator('button:has-text("Модули"), button:has-text("Modules")');
      if (await modHeader.isVisible().catch(() => false)) {
        await modHeader.click();
        await page.waitForTimeout(500);
      }
      // Show all modules
      const showAll = page.locator('button:has-text("Показать все"), button:has-text("Show all")');
      if (await showAll.isVisible().catch(() => false)) {
        await showAll.click();
        await page.waitForTimeout(500);
      }
      modLinks = page.locator('a[href*="/modules/"]');
      modCount = await modLinks.count();
      console.log('  After expand: ' + modCount);
    }

    if (modCount === 0) {
      // Debug — list all page links
      const allLinks = await page.locator('a').all();
      const hrefs = [];
      for (const l of allLinks) {
        const h = await l.getAttribute('href');
        if (h) hrefs.push(h);
      }
      console.log('  All page hrefs: ' + JSON.stringify(hrefs));
      await shot(page, '02b-debug');
      throw new Error('No module links');
    }

    await modLinks.first().click();
    await page.waitForTimeout(3000);
    await shot(page, '03-module-screen');
    console.log('  Module URL: ' + page.url());

    // Verify START SCREEN
    let body = await page.locator('body').innerText();
    const startBtnVisible = body.includes('Начать тестирование');
    const oldListVisible = body.includes('Junior') && body.includes('Middle');
    const bankLinkVisible = body.includes('Банк вопросов');

    check('1. Start screen: "Начать тестирование" visible', startBtnVisible);
    check('2. Old activity list NOT default', !oldListVisible);
    check('3. Question Bank link (secondary)', bankLinkVisible);

    if (!startBtnVisible) {
      await shot(page, '03b-not-start');
      console.log('  Page content: ' + body.substring(0, 500));
      throw new Error('Module page is NOT showing start screen');
    }

    // ================================================================
    // 3. START QUIZ → Q1
    // ================================================================
    console.log('\n=== 3. Quiz: Question 1 ===');
    await page.locator('button:has-text("Начать тестирование")').click();
    await page.waitForTimeout(3000);
    await shot(page, '04-q1');

    body = await page.locator('body').innerText();
    check('4. Progress "Вопрос 1 из N"', /Вопрос 1 из \d/.test(body));
    check('5. Progress bar present', body.includes('%'));

    // ================================================================
    // 4. ANSWER Q1 → FEEDBACK
    // ================================================================
    console.log('\n=== 4. Answer Q1 → feedback ===');

    // Close any open dropdown overlays first
    await page.keyboard.press('Escape');
    await page.waitForTimeout(200);

    // Select answer option — SingleChoiceActivity renders options as <button>
    // The answer buttons are inside the main content area, not the header
    const mainContent = page.locator('main');
    const allBtns = await mainContent.locator('button').all();
    let answered = false;
    for (const btn of allBtns) {
      const txt = await btn.textContent();
      // Filter: content option buttons have visible text and are not nav/action
      if (txt && txt.trim().length >= 3 && !txt.includes('Отправить') && !txt.includes('списку')) {
        await btn.click();
        console.log('  Clicked answer: ' + txt.trim().substring(0, 40));
        answered = true;
        break;
      }
    }
    if (!answered) console.log('  WARNING: Could not find answer option to click');
    await page.waitForTimeout(300);

    await page.locator('button:has-text("Отправить ответ")').first().click();
    await page.waitForTimeout(3000);
    await shot(page, '05-q1-feedback');

    body = await page.locator('body').innerText();
    check('6. Feedback text (Верно/Неверно)', /Верно!|Неверно|Частично верно/.test(body));
    check('7. Explanation section visible', /Объяснение/.test(body));

    // i18n check: no raw explanation keys in feedback
    const rawExpKeys = body.match(/ba_\w+_q\d+_explanation/g);
    check('7b. No raw *_explanation keys in feedback', !rawExpKeys || rawExpKeys.length === 0);

    // ================================================================
    // 5. NEXT → Q2 (no list return)
    // ================================================================
    console.log('\n=== 5. Next → Q2 (no list return) ===');
    const next1 = page.locator('button:has-text("Следующий вопрос")');
    if (await next1.isVisible().catch(() => false)) {
      await next1.click();
      await page.waitForTimeout(3000);
    }
    await shot(page, '06-q2');

    body = await page.locator('body').innerText();
    check('8. Q2 shown — no list return', /Вопрос 2 из \d/.test(body));
    check('9. URL stays /modules/', page.url().includes('/modules/'));

    // ================================================================
    // 6. ANSWER Q2
    // ================================================================
    console.log('\n=== 6. Answer Q2 ===');
    await page.keyboard.press('Escape');
    await page.waitForTimeout(100);
    const a2 = await page.locator('main').locator('button').all();
    for (const btn of a2) {
      const txt = await btn.textContent();
      if (txt && txt.trim().length >= 3 && !txt.includes('Отправить') && !txt.includes('списку')) {
        await btn.click(); break;
      }
    }
    await page.waitForTimeout(300);
    await page.locator('button:has-text("Отправить ответ")').first().click();
    await page.waitForTimeout(2000);
    await shot(page, '07-q2-feedback');

    // ================================================================
    // 7. NEXT → Q3
    // ================================================================
    console.log('\n=== 7. Next → Q3 ===');
    const next2 = page.locator('button:has-text("Следующий вопрос")');
    if (await next2.isVisible().catch(() => false)) {
      await next2.click();
      await page.waitForTimeout(3000);
    }
    await shot(page, '08-q3');

    body = await page.locator('body').innerText();
    check('10. Q3 — 3 sequential questions', /Вопрос 3 из \d/.test(body));

    // ================================================================
    // 8. COMPLETE ALL → RESULT
    // ================================================================
    console.log('\n=== 8. Complete all → result ===');
    for (let i = 0; i < 40; i++) {
      const txt = await page.locator('body').innerText();

      if (/Модуль пройден!/.test(txt) && /Разбор ответов/.test(txt)) {
        console.log('  Result reached at iteration ' + i);
        break;
      }

      const finBtn = page.locator('button:has-text("Завершить модуль")');
      if (await finBtn.isVisible().catch(() => false)) { await finBtn.click(); await page.waitForTimeout(2000); continue; }

      const nxBtn = page.locator('button:has-text("Следующий вопрос")');
      if (await nxBtn.isVisible().catch(() => false)) { await nxBtn.click(); await page.waitForTimeout(2000); continue; }

      await page.keyboard.press('Escape');
      await page.waitForTimeout(100);
      const rd2 = await page.locator('main').locator('button').all();
      for (const btn of rd2) {
        const txt = await btn.textContent();
        if (txt && txt.trim().length >= 3 && !txt.includes('Отправить') && !txt.includes('списку')) {
          await btn.click(); break;
        }
      }
      await page.waitForTimeout(300);
      const sbBtn = page.locator('button:has-text("Отправить ответ")');
      if (await sbBtn.isVisible().catch(() => false)) { await sbBtn.click(); await page.waitForTimeout(2000); continue; }

      console.log('  Stop at iteration ' + i);
      break;
    }

    await page.waitForTimeout(2000);
    await shot(page, '09-result-screen');

    // ================================================================
    // 9. VERIFY RESULT
    // ================================================================
    console.log('\n=== 9. Verify result page ===');
    body = await page.locator('body').innerText();

    check('11. "Модуль пройден!" title', /Модуль пройден!/.test(body));
    check('12. Score percentage', /\d+%/.test(body));
    check('13. Correct answers count', /Верных ответов/.test(body));
    check('14. Weak topics section', /Слабые темы/.test(body));
    check('15. Mistakes review heading', /Разбор ответов/.test(body));
    check('16. "Повторить модуль" button', /Повторить модуль/.test(body));
    check('17. "Банк вопросов" link', /Банк вопросов/.test(body));

    const hasRaw = /ba_trainer\./.test(body) || /modules\.\w+\.(title|description)/.test(body);
    check('18. No raw i18n keys', !hasRaw);
    // i18n check: no raw explanation keys in result review
    const rawExpKeysResult = body.match(/ba_\w+_q\d+_explanation/g);
    check('18b. No raw *_explanation keys in result', !rawExpKeysResult || rawExpKeysResult.length === 0);

    const hasEn = /\b(Start Test|Finish Module|Question \d+ of)\b/.test(body);
    if (hasEn) console.log('  (English text found — OK if en-US)');

    // ================================================================
    // 10. EXPAND REVIEW
    // ================================================================
    console.log('\n=== 10. Expand answer review ===');
    const btns = await page.locator('button').all();
    let expanded = false;
    for (const btn of btns) {
      const t = await btn.textContent();
      if (t && t.includes('%')) { await btn.click(); expanded = true; await page.waitForTimeout(500); break; }
    }
    if (!expanded) {
      const cb = await page.locator('.w-full.text-left, [class*=\"card\"] button, [class*=\"Card\"] button').all();
      if (cb.length > 1) { await cb[1].click(); expanded = true; await page.waitForTimeout(500); }
    }
    if (expanded) {
      await shot(page, '10-review-expanded');
      const ex = await page.locator('body').innerText();
      check('19. "Ваш ответ" in expanded review', /ваш ответ/i.test(ex));
      check('20. "Объяснение" in expanded review', /объяснение/i.test(ex));
    } else {
      console.log('  Note: Could not expand review');
    }

    // ================================================================
    // SUMMARY
    // ================================================================
    console.log('\n========================================');
    console.log('  PASSED: ' + passed + '  FAILED: ' + failed);
    console.log('========================================');
    for (const s of SHOTS) console.log('  ' + s);
    console.log('');
    console.log('⚠️  production_accepted=false');
    console.log('⚠️  release_allowed=false');
    console.log('⚠️  Operator visual review required');

    if (failed > 0) {
      console.log('\n❌ Some checks FAILED');
      process.exit(1);
    } else {
      console.log('\n✅ All checks PASSED');
    }

  } catch (err) {
    console.error('\n❌ ERROR: ' + err.message);
    await shot(page, 'error').catch(() => {});
    process.exit(1);
  } finally {
    await browser.close();
  }
}

run();
