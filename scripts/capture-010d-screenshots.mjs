import { chromium } from 'playwright-core';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const STAGING = 'https://trainer.152.53.227.37.nip.io';
const SHOTS_DIR = path.resolve(__dirname, '../docs/simulator_engine/screenshots');

const TEST_EMAIL = 'taras@example.com';
const TEST_PASSWORD = 'testpassword123';

const shots = [
  // Desktop unauthenticated
  { name: '010d-home', url: STAGING, auth: false },
  { name: '010d-it-domain', url: `${STAGING}/domains/it`, auth: false },
  { name: '010d-ba-trainer', url: `${STAGING}/trainers/ba-trainer`, auth: false },
  // Desktop authenticated
  { name: '010d-qa-trainer', url: `${STAGING}/trainers/qa-engineer`, auth: true },
  { name: '010d-qa-quest-catalog', url: `${STAGING}/trainers/qa-engineer/quests`, auth: true },
  { name: '010d-ba-quest-catalog', url: `${STAGING}/trainers/ba-trainer/quests`, auth: true },
  { name: '010d-qa-quest-step1', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, auth: true, wait: 5000 },
  { name: '010d-qa-evidence-selection', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, auth: true, wait: 5000 },
  { name: '010d-qa-selected-option', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, auth: true, wait: 5000 },
  { name: '010d-qa-outcome-debrief', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, auth: true, wait: 5000 },
  { name: '010d-ba-quest-step1', url: `${STAGING}/trainers/ba-trainer/quests`, auth: true, wait: 5000 },
  { name: '010d-ba-outcome-debrief', url: `${STAGING}/trainers/ba-trainer/quests`, auth: true, wait: 5000 },
  // Responsive
  { name: '010d-mobile-qa-catalog', url: `${STAGING}/trainers/qa-engineer/quests`, auth: true, width: 375, height: 812 },
  { name: '010d-mobile-qa-step1', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, auth: true, wait: 5000, width: 375, height: 812 },
  { name: '010d-tablet-qa-catalog', url: `${STAGING}/trainers/qa-engineer/quests`, auth: true, width: 768, height: 1024 },
];

async function main() {
  console.log('Launching browser...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  for (const shot of shots) {
    console.log(`\nCapturing ${shot.name}...`);

    // Set viewport
    await page.setViewportSize({
      width: shot.width || 1440,
      height: shot.height || 900,
    });

    // Login if needed
    if (shot.auth) {
      await page.goto(`${STAGING}/login`, { waitUntil: 'networkidle' });
      await page.fill('input[id="email"]', TEST_EMAIL);
      await page.fill('input[id="password"]', TEST_PASSWORD);
      await page.click('button[type="submit"]');
      try {
        await page.waitForURL('**/domains', { timeout: 15000 });
      } catch {
        console.log('  Login may have failed, continuing...');
      }
    }

    try {
      await page.goto(shot.url, { waitUntil: 'networkidle', timeout: 30000 });

      if (shot.wait) {
        await page.waitForTimeout(shot.wait);
      }

      await page.screenshot({
        path: path.join(SHOTS_DIR, `${shot.name}.png`),
        fullPage: false,
      });
      console.log(`  ✓ Saved ${shot.name}.png`);
    } catch (err) {
      console.log(`  ✗ Error: ${err.message}`);
    }
  }

  await browser.close();
  console.log('\nAll screenshots captured!');
}

main().catch(console.error);
