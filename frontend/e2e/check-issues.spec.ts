import { test, expect } from "@playwright/test";

test("Check all 5 issues on staging", async ({ page }) => {
  // Issue 1: Home hero CTA
  await page.goto("https://trainer.152.53.227.37.nip.io/");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  const heroBtn = page.locator("section:first-of-type button, section:first-of-type a:has(button)").first();
  const btnText = await heroBtn.textContent().catch(() => "NOT FOUND");
  console.log(`[1] Hero CTA text: "${btnText?.trim()}"`);
  await page.screenshot({ path: "screenshots/010b-issue1-home.png", fullPage: true });

  // Issue 3: Footer debug text
  const footerText = await page.locator("footer").textContent();
  console.log(`[3] Footer contains "ru-RU / en-US": ${footerText?.includes("ru-RU / en-US")}`);

  // Go to domains page
  await page.goto("https://trainer.152.53.227.37.nip.io/domains");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  console.log(`[2] Domains content: ${(await page.locator("body").textContent())?.substring(0, 200)}`);

  // Issue 4: QA trainer page
  await page.goto("https://trainer.152.53.227.37.nip.io/trainers/qa-engineer-interview-trainer");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  const body = await page.locator("body").textContent() || "";
  const ctaCount = (body.match(/Начать квест|Start Quest|Начать обучение/gi) || []).length;
  console.log(`[4] QA trainer CTA count: ${ctaCount}`);

  // Issue 5: Quest catalog
  await page.goto("https://trainer.152.53.227.37.nip.io/trainers/qa-engineer-interview-trainer/quests");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  const questBody = await page.locator("body").textContent() || "";
  console.log(`[5] Quest catalog preview: "${questBody.substring(0, 300)}"`);
  const hasNoQuests = questBody.includes("нет квестов") || questBody.includes("no quests");
  console.log(`[5] Empty catalog: ${hasNoQuests}`);
});
