/* Optional browser QA. Start the existing dev_server.py, then run this file.
 * Playwright is a development-only dependency; the shipped game needs no npm.
 */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const base = process.env.CINEMATIC_URL || 'http://127.0.0.1:8778';
const output = process.env.CINEMATIC_QA_OUTPUT || path.resolve('work/cinematic-qa');
const activities = {
  home_brush: 11,
  home_rain_vinyl: 12,
  home_hide_seek: 12,
  home_kitchen: 13,
  home_nap: 11,
  street_cafe: 14,
  street_walk: 12,
  street_lawn: 13,
  street_window: 11,
  street_bridge: 14,
};
const report = { checks: [], errors: [], requests: [], screenshots: [] };
fs.mkdirSync(output, { recursive: true });
let browser;

async function snapshot(page) {
  return page.evaluate(() => window.cinematicPreview?.getSnapshot());
}
async function load(page, id, extras = '') {
  await page.goto(`${base}/cinematic-preview.html?activity=${id}&quality=low${extras}`, {
    waitUntil: 'domcontentloaded',
  });
  await page.waitForFunction(() => window.cinematicPreview?.getSnapshot(), { timeout: 90000 });
  assert.equal((await snapshot(page)).error, null);
}
async function result(page) {
  await page.waitForFunction(() => window.cinematicPreview?.getSnapshot()?.phase === 'result', {
    timeout: 120000,
  });
  const state = await snapshot(page);
  assert.equal(state.error, null);
  return state;
}
async function capture(page, name) {
  const file = path.join(output, name);
  await page.screenshot({ path: file, animations: 'disabled' });
  report.screenshots.push(file);
}
async function fits(page) {
  assert.equal(
    await page.evaluate(
      () =>
        document.documentElement.scrollWidth <= innerWidth &&
        document.documentElement.scrollHeight <= innerHeight,
    ),
    true,
    'viewport must not overflow',
  );
  assert.equal(
    await page.locator('#cinematic-stage canvas').count(),
    1,
    'one fullscreen WebGL canvas',
  );
  const bounds = await page.locator('#cinematic-stage canvas').boundingBox(),
    size = page.viewportSize();
  assert.equal(bounds.width, size.width);
  assert.equal(bounds.height, size.height);
}

(async () => {
  browser = await chromium.launch({
    headless: true,
    ...(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}),
    args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  });
  const page = await browser.newPage({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 1,
  });
  await page.addInitScript(() => {
    window.qaResults = [];
    Object.defineProperty(window, 'lastCinematicResult', {
      configurable: true,
      get() {
        return window.qaResults.at(-1);
      },
      set(value) {
        window.qaResults.push(value);
      },
    });
  });
  page.on('pageerror', (error) => report.errors.push(error.stack));
  page.on('console', (message) => {
    if (message.type() === 'error' && /THREE|shader|WebGL|GL_INVALID/i.test(message.text()))
      report.errors.push(message.text());
  });
  page.on('request', (request) => {
    if (/^https?:/.test(request.url()) && new URL(request.url()).origin !== new URL(base).origin)
      report.requests.push(request.url());
  });
  const content = await (await page.request.get(`${base}/data/content.json`)).json();
  for (const [id, delta] of Object.entries(activities)) {
    await load(page, id);
    await fits(page);
    const state = await result(page);
    assert.equal(
      state.result.outcome,
      'win',
      `${id} autoplay should complete the same interactions as the player`,
    );
    assert.equal(state.result.delta, delta);
    assert.ok(content.activities[id].win_lines.includes(state.result.summaryLine));
    assert.equal(
      await page.evaluate(() => window.qaResults.length),
      1,
      'callback fires exactly once',
    );
    assert.equal(await page.getByText('陪伴高光时刻', { exact: true }).isVisible(), true);
    if (['home_brush', 'home_rain_vinyl', 'street_cafe', 'street_walk'].includes(id))
      await capture(page, `${id}-390.png`);
    report.checks.push(
      `${id}: 390×844 autoplay win +${delta}, one callback, original content, no overflow`,
    );
    console.log('PASS', report.checks.at(-1));
  }
  await page.setViewportSize({ width: 1280, height: 800 });
  await load(page, 'home_rain_vinyl', '&autoplay=0');
  await fits(page);
  await page.waitForFunction(
    () => window.cinematicPreview?.getSnapshot()?.phase === 'interaction',
    { timeout: 60000 },
  );
  await capture(page, 'rain-desktop-1280.png');
  // A real DOM notification click, followed by the cold 3.5-second outro.
  await page.locator('.phone.visible').waitFor({ state: 'visible', timeout: 60000 });
  await page.locator('.phone.visible').click();
  let state = await result(page);
  assert.equal(state.result.outcome, 'phone_fail');
  assert.equal(state.result.delta, -12);
  assert.ok(content.activities.home_rain_vinyl.phone_fail_lines.includes(state.result.summaryLine));
  assert.equal(await page.evaluate(() => window.qaResults.length), 1);
  report.checks.push(
    '1280×800 real notification click: phone_fail, one callback, original failure line',
  );
  await load(page, 'home_brush', '&autoplay=0&happiness=85');
  await page.waitForFunction(
    () => window.cinematicPreview?.getSnapshot()?.phase === 'interaction',
    { timeout: 60000 },
  );
  const dryer = page.getByRole('button', { name: '吹风机', exact: true });
  await dryer.focus();
  await dryer.press('Enter');
  state = await result(page);
  assert.equal(state.result.outcome, 'hazard_fail');
  assert.equal(state.result.delta, -13);
  assert.equal(await page.getByText('幸福跌破 80 · 冷战中', { exact: true }).isVisible(), true);
  await capture(page, 'cold-outro-1280.png');
  report.checks.push('keyboard 3D-prop action: hazard_fail, 85→72 cold-war ending');
  await load(page, 'home_nap', '&happiness=70');
  await page.waitForFunction(
    () => window.cinematicPreview?.getSnapshot()?.phase === 'locked_result',
    { timeout: 60000 },
  );
  assert.equal(await page.evaluate(() => window.qaResults.length), 0);
  assert.equal((await snapshot(page)).result, null);
  report.checks.push('entry below 80 is locked; no score, win or completion callback');
  await load(page, 'street_cafe');
  await page.getByText('放映目录', { exact: true }).click();
  await page.getByRole('button', { name: '换分试映', exact: true }).click();
  await page.waitForFunction(() => window.cinematicPreview?.getSnapshot()?.phase === 'swap', {
    timeout: 120000,
  });
  await capture(page, 'swap-reveal-1280.png');
  await page.waitForFunction(() => window.cinematicPreview?.getSnapshot()?.phase === 'result', {
    timeout: 60000,
  });
  assert.equal(await page.locator('.score strong').textContent(), '168');
  assert.equal(await page.evaluate(() => window.qaResults.length), 1);
  report.checks.push('confirmed swap payload drives reveal, score 168, completion still once');
  // Same-page switching exercises destroy(), rather than relying on page unload.
  for (let i = 0; i < 8; i++) {
    await page.getByRole('button', { name: '下一幕', exact: true }).click();
    assert.equal(await page.locator('#cinematic-stage canvas').count(), 1);
  }
  await page.evaluate(() => window.cinematicPreview.destroy());
  assert.equal(await page.locator('#cinematic-stage canvas').count(), 0);
  assert.equal(await page.evaluate(() => document.body.style.overflow), '');
  report.checks.push(
    '8 same-page switches and final destroy: one live canvas, then none, scroll lock restored',
  );
  assert.deepEqual(report.errors, [], 'no uncaught errors or shader errors');
  assert.deepEqual(report.requests, [], 'all runtime requests stay local');
  fs.writeFileSync(path.join(output, 'report.json'), JSON.stringify(report, null, 2));
  console.log(
    `PASS ${report.checks.length} checks; no page/shader errors; no external runtime requests`,
  );
})()
  .catch((error) => {
    report.errors.push(error.stack);
    fs.writeFileSync(path.join(output, 'report.json'), JSON.stringify(report, null, 2));
    console.error(error);
    process.exitCode = 1;
  })
  .finally(async () => {
    await browser?.close();
  });
