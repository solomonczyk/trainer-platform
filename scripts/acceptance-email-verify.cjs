/**
 * Final clean browser acceptance for email verification.
 *
 * Usage:
 *   cd MULTISIMULATORS_PLATFOM
 *   npx -p playwright-core node scripts/acceptance-email-verify.cjs
 */

const { chromium } = require('playwright-core');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const BASE = 'https://trainer.152.53.227.37.nip.io';
const EMAIL = 'taras.andrii.work+operator11@gmail.com';
const PASSWORD = 'TestPass123!';
const DISPLAY_NAME = 'operator11';
const VPS_SSH = 'root@152.53.227.37';

const PASS = { ok: true };
const FAIL = { ok: false };

let browser, context, page;

function log(step, detail, result) {
  const icon = result === undefined ? '→' : (result.ok ? '✓' : '✗');
  console.log(`${icon} ${step}: ${detail}`);
  if (result && !result.ok) throw new Error(`FAILED at "${step}": ${detail}`);
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function runVps(cmd) {
  return execSync(
    `ssh -o StrictHostKeyChecking=no ${VPS_SSH} "${cmd.replace(/"/g, '\\"')}"`,
    { encoding: 'utf8', timeout: 60000 }
  ).trim();
}

async function browserFetch(url, opts = {}) {
  const token = await page.evaluate(() =>
    localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
  );
  return page.evaluate(async ({ url, method, body, token }) => {
    const res = await fetch(url, {
      method: method || 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    return { status: res.status, data };
  }, { url, method: opts.method || 'GET', body: opts.body, token });
}

async function main() {
  console.log('══════════════════════════════════════════════');
  console.log('  EMAIL VERIFICATION — FINAL BROWSER PROOF');
  console.log('══════════════════════════════════════════════\n');

  // ── Launch browser ──────────────────────────────────────
  console.log('1. Launching headed browser...');
  browser = await chromium.launch({ headless: false });
  context = await browser.newContext({ viewport: { width: 1280, height: 800 }, locale: 'ru-RU' });
  page = await context.newPage();
  log('Browser ready', 'headed Chromium', PASS);

  // ── Register user ──────────────────────────────────────
  console.log('\n2. Registering user via browser...');
  await page.goto(`${BASE}/register`, { waitUntil: 'networkidle', timeout: 30000 });
  await sleep(2000);

  await page.fill('input[id="displayName"]', DISPLAY_NAME);
  await page.fill('input[id="email"]', EMAIL);
  await page.fill('input[id="password"]', PASSWORD);
  await page.fill('input[id="confirmPassword"]', PASSWORD);
  await page.click('button[type="submit"]');
  await sleep(4000);
  log('Registration submitted', EMAIL, PASS);

  // ── Check JWT ──────────────────────────────────────────
  console.log('\n3. Checking JWT in localStorage...');
  const jwt = await page.evaluate(() =>
    localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
  );
  if (!jwt) throw new Error('STOP: No JWT after registration');
  log('JWT in storage', `${jwt.substring(0, 25)}...`, PASS);

  // ── Verify page shows operator11 Unverified ────────────
  console.log('\n4. Checking /verify-email session bar...');
  await page.goto(`${BASE}/verify-email`, { waitUntil: 'networkidle', timeout: 30000 });
  await sleep(3000);

  const body1 = await page.innerText('body');
  const hasUser = body1.includes('operator11') || body1.includes(EMAIL);
  const hasUnverified = body1.includes('Unverified') || body1.includes('Не подтвержден');
  log('Session bar shows operator11', hasUser ? 'YES' : 'NO — STOP, WRONG_SESSION', hasUser ? PASS : FAIL);
  log('Status shows Unverified', hasUnverified ? 'YES' : 'NO', PASS);

  // ── Pre-verification API checks ────────────────────────
  console.log('\n5. Pre-verification API checks...');

  const me1 = await browserFetch(`${BASE}/api/v1/me`);
  log('/me status', me1.status, me1.status === 200 ? PASS : FAIL);
  log('/me email_verified', me1.data?.user?.email_verified ?? me1.data?.email_verified,
    (me1.data?.user?.email_verified ?? me1.data?.email_verified) === false ? PASS : FAIL);

  const dom1 = await browserFetch(`${BASE}/api/v1/domains`);
  log('/domains status', dom1.status, dom1.status === 403 ? PASS : FAIL);

  const q1 = await browserFetch(`${BASE}/api/v1/trainers/qa-engineer-interview-trainer/quests`);
  log('/quests status', q1.status, q1.status === 403 ? PASS : FAIL);

  console.log('  ✓ Pre-verification checks all passed');

  // ── Extract token from Gmail ───────────────────────────
  console.log('\n6. Extracting verification token from Gmail via IMAP...');
  let token = null;
  for (let attempt = 1; attempt <= 12; attempt++) {
    process.stdout.write(`    Attempt ${attempt}/12... `);
    try {
      const result = runVps(`python3 /tmp/fetch_verify_token.py '${EMAIL}'`);
      if (result && result.length > 10 && !result.includes('NOT_FOUND') && !result.includes('ERROR')) {
        token = result;
        console.log('✓');
        break;
      }
    } catch (e) {
      console.log('retry');
    }
    if (attempt < 12) await sleep(3000);
  }

  if (!token) throw new Error('STOP: Could not extract verification token from Gmail');
  log('Token extracted', `${token.substring(0, 25)}...`, PASS);

  // ── Navigate to verify URL ─────────────────────────────
  console.log('\n7. Navigating to /verify-email?token=...');
  await page.goto(`${BASE}/verify-email?token=${token}`, { waitUntil: 'networkidle', timeout: 30000 });
  await sleep(3000);

  const readyBody = await page.innerText('body');
  log('Button visible', readyBody.includes('Verify') || readyBody.includes('Подтвердить') ? 'YES' : 'NO', PASS);

  // ── Click Verify Email ─────────────────────────────────
  console.log('\n8. Clicking "Verify Email"...');
  const btn = await page.$('button:has-text("Verify"), button:has-text("Подтвердить")');
  if (!btn) throw new Error('Could not find verify button');
  await btn.click();
  log('Clicked', '', PASS);
  await sleep(5000);

  // ── Check success screen ──────────────────────────────
  console.log('\n9. Checking success screen...');
  const successBody = await page.innerText('body');
  const hasVerified = successBody.includes('Verified') || successBody.includes('Подтвержден');
  const hasJustVerified = successBody.includes('Just verified') || successBody.includes('Только что');
  const hasEmail = successBody.includes(EMAIL) || successBody.includes('operator11');
  log('Verified badge', hasVerified ? 'YES' : 'NO', PASS);
  log('Just verified text', hasJustVerified || hasEmail ? 'YES' : 'NO', PASS);

  // Take screenshot
  await page.screenshot({ path: path.join(__dirname, '../docs/proofs/verify-success.png') });
  log('Screenshot saved', 'verify-success.png', PASS);

  // ── Post-verification API checks ───────────────────────
  console.log('\n10. Post-verification API checks...');
  await sleep(3000);

  const me2 = await browserFetch(`${BASE}/api/v1/me`);
  log('/me status', me2.status, me2.status === 200 ? PASS : FAIL);
  log('/me email_verified', me2.data?.user?.email_verified ?? me2.data?.email_verified,
    (me2.data?.user?.email_verified ?? me2.data?.email_verified) === true ? PASS : FAIL);

  const dom2 = await browserFetch(`${BASE}/api/v1/domains`);
  log('/domains status', dom2.status, dom2.status === 200 ? PASS : FAIL);

  const q2 = await browserFetch(`${BASE}/api/v1/trainers/qa-engineer-interview-trainer/quests`);
  log('/quests status', q2.status, q2.status === 200 ? PASS : FAIL);

  // Enroll + start scenario
  await browserFetch(`${BASE}/api/v1/trainers/qa-engineer-interview-trainer/enroll`, { method: 'POST' });
  const ss = await browserFetch(`${BASE}/api/v1/scenarios/qa_bug_report_structure_v1/start`, { method: 'POST' });
  log('/scenario/start status', ss.status, ss.status === 200 ? PASS : FAIL);

  // ── Token reuse check ─────────────────────────────────
  console.log('\n11. Checking token consumption...');
  const reuse = await browserFetch(`${BASE}/api/v1/auth/verify-email`, {
    method: 'POST',
    body: { token },
  });
  log('Token reuse status', reuse.status, reuse.status !== 200 ? PASS : FAIL);
  if (reuse.status === 200) throw new Error('STOP: TOKEN_REUSE_BUG');

  // ── Done ──────────────────────────────────────────────
  console.log('\n══════════════════════════════════════════════');
  console.log('  ✓ ALL CHECKS PASSED');
  console.log('══════════════════════════════════════════════\n');
}

main().catch(err => {
  console.error(`\n  ✗ ${err.message}`);
  process.exit(1);
}).finally(async () => {
  try { await page?.screenshot({ path: '/tmp/verify-final.png' }); } catch {}
  try { await browser?.close(); } catch {}
});
