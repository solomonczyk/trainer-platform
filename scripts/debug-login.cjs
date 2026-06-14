const { chromium } = require('playwright-core');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  // Check login page
  console.log('=== LOGIN PAGE ===');
  await page.goto('https://trainer.152.53.227.37.nip.io/login', { waitUntil: 'networkidle' });
  await page.waitForTimeout(5000);

  const text = await page.innerText('body');
  const url = page.url();
  console.log('URL:', url);
  console.log('Body text (first 500):', text.substring(0, 500));

  const inputs = await page.evaluate(() =>
    Array.from(document.querySelectorAll('input')).map(e => ({ id: e.id, type: e.type, name: e.name, placeholder: e.placeholder }))
  );
  console.log('Inputs:', JSON.stringify(inputs, null, 2));

  // Try to submit login
  if (inputs.length > 0) {
    const emailInput = await page.$('input[type="email"], input[id="email"]');
    if (emailInput) await emailInput.fill('taras@example.com');
    const pwInput = await page.$('input[type="password"], input[id="password"]');
    if (pwInput) await pwInput.fill('testpassword123');
    const sb = await page.$('button[type="submit"]');
    if (sb) {
      await sb.click();
      await page.waitForTimeout(5000);
      console.log('\nAfter login URL:', page.url());
      console.log('After login text:', (await page.innerText('body')).substring(0, 300));
    }
  }

  // Check a quest page
  console.log('\n=== QUEST CATALOG ===');
  await page.goto('https://trainer.152.53.227.37.nip.io/trainers/qa-engineer/quests', { waitUntil: 'networkidle' });
  await page.waitForTimeout(8000);
  console.log('Quest URL:', page.url());
  console.log('Quest text:', (await page.innerText('body')).substring(0, 500));

  await browser.close();
})();
