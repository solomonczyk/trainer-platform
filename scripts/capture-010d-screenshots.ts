import { chromium, type Browser, type Page } from '@playwright/test';
import path from 'path';

const STAGING = 'https://trainer.152.53.227.37.nip.io';
const SHOTS_DIR = path.resolve(__dirname, '../docs/simulator_engine/screenshots');

interface Shot {
  name: string;
  url: string;
  width: number;
  height: number;
  wait?: number;
  auth?: boolean;
}

const desktop: Shot[] = [
  { name: '010d-home', url: STAGING, width: 1440, height: 900 },
  { name: '010d-it-domain', url: `${STAGING}/domains/it`, width: 1440, height: 900 },
  { name: '010d-qa-trainer', url: `${STAGING}/trainers/qa-engineer`, width: 1440, height: 900, auth: true },
  { name: '010d-ba-trainer', url: `${STAGING}/trainers/ba-trainer`, width: 1440, height: 900 },
  { name: '010d-qa-quest-catalog', url: `${STAGING}/trainers/qa-engineer/quests`, width: 1440, height: 900, auth: true },
  { name: '010d-ba-quest-catalog', url: `${STAGING}/trainers/ba-trainer/quests`, width: 1440, height: 900 },
  { name: '010d-qa-quest-step1', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, width: 1440, height: 900, auth: true, wait: 5000 },
  { name: '010d-qa-evidence-selection', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, width: 1440, height: 900, auth: true, wait: 5000 },
  { name: '010d-qa-selected-option', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, width: 1440, height: 900, auth: true, wait: 5000 },
  { name: '010d-qa-outcome-debrief', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, width: 1440, height: 900, auth: true, wait: 5000 },
  { name: '010d-ba-quest-step1', url: `${STAGING}/trainers/ba-trainer/quests`, width: 1440, height: 900 },
  { name: '010d-ba-outcome-debrief', url: `${STAGING}/trainers/ba-trainer/quests`, width: 1440, height: 900 },
];

const mobile: Shot[] = [
  { name: '010d-mobile-qa-catalog', url: `${STAGING}/trainers/qa-engineer/quests`, width: 375, height: 812, auth: true },
  { name: '010d-mobile-qa-step1', url: `${STAGING}/trainers/qa-engineer/quests/qa_payment_defect_release`, width: 375, height: 812, auth: true, wait: 5000 },
];

const tablet: Shot[] = [
  { name: '010d-tablet-qa-catalog', url: `${STAGING}/trainers/qa-engineer/quests`, width: 768, height: 1024, auth: true },
];

const TEST_EMAIL = 'taras@example.com';
const TEST_PASSWORD = 'testpassword123';

async function login(page: Page) {
  await page.goto(`${STAGING}/login`);
  await page.waitForLoadState('networkidle');
  await page.fill('input[id="email"]', TEST_EMAIL);
  await page.fill('input[id="password"]', TEST_PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/domains', { timeout: 15000 });
  console.log('  ✓ Logged in');
}

async function capture(browser: Browser, shots: Shot[], auth: boolean) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  let page: Page | null = null;

  for (const shot of shots) {
    console.log(`  Capturing ${shot.name}...`);

    if (shot.auth && !page) {
      page = await context.newPage();
      await login(page);
    } else if (!page) {
      page = await context.newPage();
    }

    try {
      await page.goto(shot.url, { waitUntil: 'networkidle', timeout: 30000 });
      if (shot.wait) await page.waitForTimeout(shot.wait);

      // Set viewport for responsive shots
      if (shot.width !== 1440 || shot.height !== 900) {
        await page.setViewportSize({ width: shot.width, height: shot.height });
      }

      await page.screenshot({
        path: path.join(SHOTS_DIR, `${shot.name}.png`),
        fullPage: false,
      });
      console.log(`    ✓ Saved ${shot.name}.png`);
    } catch (err) {
      console.log(`    ✗ Failed: ${err}`);
    }
  }

  await context.close();
}

async function main() {
  console.log('Starting screenshot capture...\n');

  const browser = await chromium.launch({ headless: true });

  // First login to get authenticated screens
  console.log('Desktop shots (authenticated):');
  const authDesktop = desktop.filter(s => s.auth);
  const unauthDesktop = desktop.filter(s => !s.auth);

  if (unauthDesktop.length > 0) {
    console.log('\nDesktop shots (unauthenticated):');
    await capture(browser, unauthDesktop, false);
  }

  if (authDesktop.length > 0) {
    console.log('\nDesktop shots (authenticated):');
    await capture(browser, authDesktop, true);
  }

  console.log('\nMobile/Tablet shots:');
  await capture(browser, [...mobile, ...tablet], true);

  await browser.close();
  console.log('\nDone!');
}

main().catch(console.error);
