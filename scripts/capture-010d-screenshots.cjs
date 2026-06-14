const { chromium } = require('playwright-core');
const path = require('path');

const STAGING = 'https://trainer.152.53.227.37.nip.io';
const SHOTS_DIR = path.resolve(__dirname, '../docs/simulator_engine/screenshots');

const TEST_EMAIL = 'shot_capture_010d_v2@example.com';
const TEST_PASSWORD = 'ShotPass123!';

const shots = [
  { name: '010d-home', url: STAGING },
  { name: '010d-it-domain', url: `${STAGING}/domains/it` },
  { name: '010d-ba-trainer', url: `${STAGING}/trainers/ba-trainer` },
  { name: '010d-qa-trainer', url: `${STAGING}/trainers/qa-engineer` },
  { name: '010d-qa-quest-catalog', url: `${STAGING}/trainers/qa-engineer/quests` },
  { name: '010d-ba-quest-catalog', url: `${STAGING}/trainers/ba-trainer/quests` },
  { name: '010d-qa-quest-step1', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, wait: 10000, desc: 'quest-intro' },
  { name: '010d-qa-evidence-selection', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, wait: 10000, desc: 'quest-step' },
  { name: '010d-qa-selected-option', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, wait: 10000, desc: 'quest-option-selected' },
  { name: '010d-qa-outcome-debrief', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, wait: 10000, desc: 'quest-outcome' },
  { name: '010d-ba-quest-step1', url: `${STAGING}/trainers/ba-trainer/quests`, wait: 5000 },
  { name: '010d-ba-outcome-debrief', url: `${STAGING}/trainers/ba-trainer/quests`, wait: 5000 },
  { name: '010d-mobile-qa-catalog', url: `${STAGING}/trainers/qa-engineer/quests`, width: 375, height: 812 },
  { name: '010d-mobile-qa-step1', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, wait: 10000, width: 375, height: 812 },
  { name: '010d-tablet-qa-catalog', url: `${STAGING}/trainers/qa-engineer/quests`, width: 768, height: 1024 },
];

async function waitForContent(page) {
  try {
    await page.waitForFunction(() => {
      const text = document.body?.innerText || '';
      return text.length > 100 && !text.includes('Loading...');
    }, { timeout: 20000 });
  } catch { /* ok */ }
}

async function ensureLoggedIn(page) {
  // Try registering (if new user)
  await page.goto(`${STAGING}/register`, { waitUntil: 'networkidle', timeout: 20000 });
  await page.waitForTimeout(2000);

  try {
    await page.waitForSelector('input[id="email"]', { timeout: 8000 });
    await page.fill('input[id="displayName"]', 'Screenshot Tester');
    await page.fill('input[id="email"]', TEST_EMAIL);
    await page.fill('input[id="password"]', TEST_PASSWORD);
    await page.fill('input[id="confirmPassword"]', TEST_PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(3000);
  } catch { /* user may already exist */ }

  // If we're still on register page, try login
  if (page.url().includes('register') || page.url().includes('login')) {
    console.log('  Already registered, logging in...');
    await page.goto(`${STAGING}/login`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    try {
      await page.waitForSelector('input[id="email"]', { timeout: 8000 });
      await page.fill('input[id="email"]', TEST_EMAIL);
      await page.fill('input[id="password"]', TEST_PASSWORD);
      await page.click('button[type="submit"]');
      await page.waitForTimeout(3000);
    } catch (e) {
      console.log('  Login failed:', e.message);
    }
  }

  // Ensure we're on domains page
  await page.goto(`${STAGING}/domains`, { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(2000);
  await waitForContent(page);

  // Enroll in QA trainer
  console.log('  Checking enrollment...');
  await page.goto(`${STAGING}/trainers/qa-engineer`, { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(3000);
  await waitForContent(page);

  const qaText = await page.innerText('body');
  if (qaText.includes('Записаться') || qaText.includes('Enroll')) {
    try {
      const enrollBtn = await page.$('button:has-text("Записаться"), button:has-text("Enroll")');
      if (enrollBtn) {
        await enrollBtn.click();
        await page.waitForTimeout(3000);
        console.log('  Enrolled in QA trainer!');
      }
    } catch (e) {
      console.log('  Enroll click failed');
    }
  } else {
    console.log('  Already enrolled in QA trainer');
  }
}

async function captureShots(browser, allShots) {
  // Create a single authenticated session
  console.log('=== Setting up authenticated session ===');
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  await ensureLoggedIn(page);

  // Group shots by viewport and capture
  const viewportGroups = [
    { label: 'Desktop (1440×900)', width: 1440, height: 900, shots: allShots.filter(s => !s.width) },
    { label: 'Mobile (375×812)', width: 375, height: 812, shots: allShots.filter(s => s.width === 375) },
    { label: 'Tablet (768×1024)', width: 768, height: 1024, shots: allShots.filter(s => s.width === 768) },
  ];

  for (const group of viewportGroups) {
    console.log(`\n=== ${group.label} ===`);
    await page.setViewportSize({ width: group.width, height: group.height });

    for (const shot of group.shots) {
      console.log(`  ${shot.name}...`);

      try {
        await page.goto(shot.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      } catch { /* ok */ }

      await waitForContent(page);

      if (shot.wait) {
        await page.waitForTimeout(shot.wait);
      } else {
        await page.waitForTimeout(3000);
      }

      await page.screenshot({
        path: path.join(SHOTS_DIR, `${shot.name}.png`),
        fullPage: false,
      });
      console.log(`    ✓`);
    }
  }

  await ctx.close();
}

async function main() {
  console.log('Launching browser...');
  const browser = await chromium.launch({ headless: true });

  await captureShots(browser, shots);

  await browser.close();
  console.log('\n=== All screenshots captured! ===');
}

main().catch((err) => { console.error(err); process.exit(1); });
