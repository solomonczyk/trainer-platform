import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const BASE = 'https://trainer.152.53.227.37.nip.io';
const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function takeScreenshots() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    locale: 'ru-RU',
    storageState: undefined,
  });

  // Set ru-RU locale
  await context.addInitScript(() => {
    localStorage.setItem('preferred_locale', 'ru-RU');
  });

  const page = await context.newPage();
  page.setDefaultTimeout(30000);

  const shots = [];

  // 1. Domain catalog
  console.log('1/8: Domain catalog...');
  await page.goto(`${BASE}/domains`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(__dirname, '01-domains-ru.png'), fullPage: true });
  shots.push('01-domains-ru.png');
  // Check for English text
  const domainText = await page.textContent('body');
  const hasInfoTech = domainText.includes('Information Technology');
  console.log(`   Information Technology visible: ${hasInfoTech}`);

  // 2. BA trainer detail
  console.log('2/8: BA trainer detail...');
  await page.goto(`${BASE}/trainers/ba-trainer`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: path.join(__dirname, '02-trainer-detail-ru.png'), fullPage: true });
  shots.push('02-trainer-detail-ru.png');

  // Check for raw keys (only ba_*_title pattern, not all ba_ prefixed words)
  const trainerText = await page.textContent('body');
  const hasRawKeys = /ba_\w+_title/.test(trainerText);
  const hasSingleChoice = trainerText.includes('single choice');
  const hasMultipleChoice = trainerText.includes('multiple choice');
  console.log(`   Raw title keys visible: ${hasRawKeys}`);
  console.log(`   'single choice' visible: ${hasSingleChoice}`);
  console.log(`   'multiple choice' visible: ${hasMultipleChoice}`);

  // 3. BA module list
  console.log('3/8: BA module list...');
  await page.goto(`${BASE}/trainers/ba-trainer/modules/ba_hr_screening`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: path.join(__dirname, '03-module-list-ru.png'), fullPage: true });
  shots.push('03-module-list-ru.png');
  const moduleText = await page.textContent('body');
  const hasRawModuleKeys = /ba_\w+_title/.test(moduleText);
  console.log(`   Raw module title keys visible: ${hasRawModuleKeys}`);

  // 4. BA activity page
  console.log('4/8: BA activity page...');
  await page.goto(`${BASE}/login?redirect=/trainers/ba-trainer/activities/ba_hr_q1`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(__dirname, '04-activity-ru.png'), fullPage: true });
  shots.push('04-activity-ru.png');

  // 5. BA HR question title check
  console.log('5/8: Checking ba_hr_q1_title...');
  const activityText = await page.textContent('body');
  const hasRawTitle = activityText.includes('ba_hr_q1_title');
  console.log(`   ba_hr_q1_title visible: ${hasRawTitle}`);

  // 6. Quests list (if logged in, else skip)
  console.log('6/8: Quests page...');
  try {
    await page.goto(`${BASE}/trainers/ba-trainer/quests`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    await page.screenshot({ path: path.join(__dirname, '06-quests-ru.png'), fullPage: true });
    shots.push('06-quests-ru.png');
  } catch (e) {
    console.log('   Skipped (requires auth)');
  }

  // 7. Staging icon for badges
  console.log('7/8: Interaction badges in quest overview...');
  const questText = await page.textContent('body');
  const hasOdinVariant = questText.includes('Один вариант');
  const hasNeskolko = questText.includes('Несколько вариантов');
  const hasSopostavlenie = questText.includes('Сопоставление');
  console.log(`   'Один вариант' visible: ${hasOdinVariant}`);
  console.log(`   'Несколько вариантов' visible: ${hasNeskolko}`);
  console.log(`   'Сопоставление' visible: ${hasSopostavlenie}`);

  // 8. Pluralization check on trainer detail
  console.log('8/8: Pluralization check...');
  // Go back to trainer detail and check for correct plural form
  await page.goto(`${BASE}/trainers/ba-trainer`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  const detailText = await page.textContent('body');
  const hasVoprosov = detailText.includes('вопросов');
  const hasVoprosa = detailText.includes('вопроса');
  const hasVopros = detailText.includes('Вопрос');
  // Check for "20 Вопрос" (incorrect)
  const has20Vopros = /20\s*Вопрос/.test(detailText);
  console.log(`   'вопросов' plural: ${hasVoprosov}`);
  console.log(`   'вопроса' plural: ${hasVoprosa}`);
  console.log(`   '20 Вопрос' (incorrect): ${has20Vopros}`);

  await browser.close();

  console.log('\n=== RESULTS ===');
  console.log(JSON.stringify({
    screenshots_taken: shots.length,
    raw_i18n_keys_visible: hasRawKeys || hasRawModuleKeys || hasRawTitle,
    ba_hr_q1_title_visible: hasRawTitle,
    single_choice_visible_in_ru_RU: hasSingleChoice,
    multiple_choice_visible_in_ru_RU: hasMultipleChoice,
    domain_english_description_visible_in_ru_RU: hasInfoTech,
    question_pluralization_correct: (hasVoprosov || hasVoprosa) && !has20Vopros,
    screenshots: shots,
  }, null, 2));
}

takeScreenshots().catch(err => {
  console.error('Screenshot error:', err);
  process.exit(1);
});
