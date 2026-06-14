const { chromium } = require('playwright-core');

const STAGING = 'https://trainer.152.53.227.37.nip.io';

async function checkPage(page, url, label) {
  console.log(`\n--- ${label} ---`);
  console.log(`URL: ${url}`);

  try {
    const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    const status = response ? response.status() : 'no response';
    console.log(`HTTP status: ${status}`);

    await page.waitForTimeout(5000);

    // Check for console errors
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });

    const text = await page.innerText('body');
    const hasErrors = text.includes('Error') || text.includes('error') || text.includes('ошибк');
    const hasLoading = text.includes('Loading...');

    console.log(`Console errors captured: ${errors.length}`);
    if (hasErrors) console.log('  WARNING: Page shows error text');
    if (hasLoading) console.log('  NOTE: Page still shows loading');
    console.log(`Page title: ${await page.title()}`);

    return { status, errors: errors.length, hasErrors, url };
  } catch (err) {
    console.log(`FAILED: ${err.message}`);
    return { status: 'failed', errors: 1, hasErrors: true, url };
  }
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();

  // Login
  console.log('=== Logging in ===');
  await page.goto(`${STAGING}/register`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  const testEmail = 'runtime_check_test@example.com';
  const testPassword = 'CheckPass123!';

  try {
    await page.waitForSelector('input[id="email"]', { timeout: 8000 });
    await page.fill('input[id="displayName"]', 'Runtime Check');
    await page.fill('input[id="email"]', testEmail);
    await page.fill('input[id="password"]', testPassword);
    await page.fill('input[id="confirmPassword"]', testPassword);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(3000);
  } catch {
    // Already registered, login
    await page.goto(`${STAGING}/login`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    try {
      await page.waitForSelector('input[id="email"]', { timeout: 8000 });
      await page.fill('input[id="email"]', testEmail);
      await page.fill('input[id="password"]', testPassword);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(3000);
    } catch (e) {
      console.log('Login failed:', e.message);
    }
  }

  // Enroll in QA trainer
  await page.goto(`${STAGING}/trainers/qa-engineer`, { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(3000);

  const qaText = await page.innerText('body');
  if (qaText.includes('Записаться') || qaText.includes('Enroll')) {
    const enrollBtn = await page.$('button:has-text("Записаться"), button:has-text("Enroll")');
    if (enrollBtn) { await enrollBtn.click(); await page.waitForTimeout(3000); }
  }

  // QA flow checks
  console.log('\n=== QA FLOW ===');
  await checkPage(page, `${STAGING}/`, 'Home');
  await checkPage(page, `${STAGING}/domains/it`, 'IT Domain');
  await checkPage(page, `${STAGING}/trainers/qa-engineer`, 'QA Trainer');
  await checkPage(page, `${STAGING}/trainers/qa-engineer/quests`, 'QA Quest Catalog');
  await checkPage(page, `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, 'QA Quest Play');

  // BA flow checks
  console.log('\n=== BA FLOW ===');
  await checkPage(page, `${STAGING}/trainers/ba-trainer`, 'BA Trainer');
  await checkPage(page, `${STAGING}/trainers/ba-trainer/quests`, 'BA Quest Catalog');

  await ctx.close();
  await browser.close();
  console.log('\n=== Runtime checks complete ===');
}

main().catch(console.error);
