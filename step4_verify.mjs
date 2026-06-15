import { chromium } from "playwright";
import fs from "fs";

async function screenshot(page, name) {
  const path = `C:\Users\taras\Desktop\010d-${name}.png`;
  await page.screenshot({ path, fullPage: true });
  console.log(`  OK ${name}`);
}

async function run() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, locale: "ru-RU" });

  const BASE = "https://trainer.152.53.227.37.nip.io";

  // Login
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  await page.waitForTimeout(2000);
  await page.locator('input[type="email"]').fill("test-010d@example.com");
  await page.locator('input[type="password"]').fill("Test123!");
  await page.locator('button[type="submit"]').last().click();
  await page.waitForTimeout(3000);

  // Start the quest and submit steps 1-3 via API
  let sid = null;
  const token = await page.evaluate(() => localStorage.getItem("access_token"));

  // Enroll
  await page.evaluate(async (t) => {
    await fetch("https://trainer.152.53.227.37.nip.io/api/v1/trainers/qa-engineer-interview-trainer/enroll", {
      method: "POST", headers: { Authorization: `Bearer ${t}`, "Content-Type": "application/json" },
    });
  }, token);

  // Start quest
  const startR = await page.evaluate(async (t) => {
    const r = await fetch("https://trainer.152.53.227.37.nip.io/api/v1/quests/qa_bug_report_structure_v1/start", {
      method: "POST", headers: { Authorization: `Bearer ${t}`, "Content-Type": "application/json" },
      body: JSON.stringify({ locale: "ru-RU" }),
    });
    return r.json();
  }, token);
  sid = startR.session_id;
  let step = startR.current_step;
  console.log(`  Started quest. Step 1: ${step.step_id} (${step.step_type})`);

  // Submit steps 1-3
  const answers = [
    { sid: "br_step_01_required_fields", ans: ["title", "description", "environment", "steps_to_reproduce", "actual_result", "expected_result", "severity", "priority"] },
    { sid: "br_step_02_ordering", ans: ["summary_title", "environment_info", "preconditions", "steps_to_repro", "actual_result_reported", "expected_result_reported", "attachments"] },
    { sid: "br_step_03_severity_priority", ans: { value: "severity_is_impact" } },
  ];

  for (const a of answers) {
    const r = await page.evaluate(async (args) => {
      const res = await fetch(`https://trainer.152.53.227.37.nip.io/api/v1/quests/sessions/${args.sid}/answer`, {
        method: "POST", headers: { Authorization: `Bearer ${args.t}`, "Content-Type": "application/json" },
        body: JSON.stringify({ step_id: args.step, answer: args.ans, locale: "ru-RU" }),
      });
      return res.json();
    }, { t: token, sid, step: a.sid, ans: a.ans });
    console.log(`  Step ${a.sid}: ${r.status} score=${r.score}`);
  }

  // Navigate to quest page - should show step 4
  await page.goto(`${BASE}/trainers/qa-engineer-interview-trainer/quests/qa_bug_report_structure_v1`, { waitUntil: "networkidle" });
  await page.waitForTimeout(5000);

  // Check for the evidence panel
  const panelVisible = await page.evaluate(() => {
    const panels = document.querySelectorAll('.font-mono');
    return panels.length > 0;
  });
  console.log(`  Evidence panel visible: ${panelVisible}`);

  // Check for raw keys
  const rawKeys = await page.evaluate(() => {
    const body = document.body.innerText;
    return body.includes("quest.qa.bug_report");
  });
  console.log(`  Raw i18n keys in page: ${rawKeys ? "YES (BUG)" : "NO (FIXED)"}`);

  // Check the panel contains the bad report text
  const hasReport = await page.evaluate(() => {
    const body = document.body.innerText;
    return body.includes("Кнопка «Оформить заказ»") || body.includes("Place Order button");
  });
  console.log(`  Bad report text visible: ${hasReport}`);

  // Check panel comes before answer options
  const panelBeforeOptions = await page.evaluate(() => {
    const mono = document.querySelector('.font-mono');
    const grid = document.querySelector('.grid');
    if (!mono || !grid) return false;
    return mono.compareDocumentPosition(grid) & Node.DOCUMENT_POSITION_FOLLOWING;
  });
  console.log(`  Panel before options: ${panelBeforeOptions}`);

  await screenshot(page, "qa-bugreport-step4-panel");

  await browser.close();
  console.log("\nDone");
}

run().catch(e => { console.error(e.message); process.exit(1); });
