/* Development-only real pointer, keyboard, GLB and disposal regression checks. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = process.env.CINEMATIC_URL || 'http://127.0.0.1:8778';
const out = process.env.CINEMATIC_QA_OUTPUT || path.resolve('work/cinematic-qa/interactions');
fs.mkdirSync(out, { recursive: true });
const report = { checks: [], errors: [] };
function glb() {
  const pos = new Float32Array([-2, 0, 0, 2, 0, 0, 0, 1, 0.2]);
  const json = {
    asset: { version: '2.0' },
    scene: 0,
    scenes: [{ name: 'FixtureScene', nodes: [0] }],
    nodes: [{ name: 'FixtureDog', mesh: 0, translation: [7, 15, 11] }],
    meshes: [{ primitives: [{ attributes: { POSITION: 0 }, material: 0 }] }],
    materials: [
      { pbrMetallicRoughness: { baseColorFactor: [0.8, 0.6, 0.3, 1], roughnessFactor: 0.8 } },
    ],
    buffers: [{ byteLength: pos.byteLength }],
    bufferViews: [{ buffer: 0, byteOffset: 0, byteLength: pos.byteLength }],
    accessors: [
      {
        bufferView: 0,
        componentType: 5126,
        count: 3,
        type: 'VEC3',
        min: [-2, 0, 0],
        max: [2, 1, 0.2],
      },
    ],
  };
  let text = JSON.stringify(json);
  while (text.length % 4) text += ' ';
  const j = Buffer.from(text),
    bin = Buffer.from(pos.buffer),
    b = Buffer.alloc(28 + j.length + bin.length);
  b.writeUInt32LE(0x46546c67, 0);
  b.writeUInt32LE(2, 4);
  b.writeUInt32LE(b.length, 8);
  b.writeUInt32LE(j.length, 12);
  b.writeUInt32LE(0x4e4f534a, 16);
  j.copy(b, 20);
  b.writeUInt32LE(bin.length, 20 + j.length);
  b.writeUInt32LE(0x004e4942, 24 + j.length);
  bin.copy(b, 28 + j.length);
  return b;
}
(async () => {
  const b = await chromium.launch({
    headless: true,
    ...(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}),
    args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  });
  const p = await b.newPage({ viewport: { width: 390, height: 844 } });
  p.on('pageerror', (e) => report.errors.push(e.message));
  p.on('console', (m) => {
    if (m.type() === 'error' && /THREE|shader|GL_INVALID/.test(m.text()))
      report.errors.push(m.text());
  });
  await p.goto(`${base}/cinematic-preview.html?activity=home_hide_seek&autoplay=0&quality=low`);
  await p.waitForFunction(() => window.cinematicPreview?.getSnapshot()?.phase === 'interaction', {
    timeout: 90000,
  });
  async function mount(id, extra = {}) {
    await p.evaluate(
      async ({ id, extra }) => {
        window.cinematicPreview?.destroy();
        window.qaDirector?.destroy();
        const { CinematicDirector } = await import('./js/cinematic/director.js');
        window.THREE = await import('three');
        window.qaCalls = [];
        window.qaDirector = new CinematicDirector(document.getElementById('cinematic-stage'), {
          activityId: id,
          owner: 'Meya',
          happiness: 100,
          content: await (await fetch('./data/content.json')).json(),
          quality: 'low',
          onComplete: (r) => window.qaCalls.push(r),
          ...extra,
        });
      },
      { id, extra },
    );
    await p.waitForFunction(() => window.qaDirector?.phase === 'interaction', { timeout: 90000 });
  }
  async function point(id) {
    return p.evaluate((id) => {
      const d = window.qaDirector,
        o = d.world.targets.get(id);
      d.scene.updateMatrixWorld(true);
      let v = new window.THREE.Box3().setFromObject(o).getCenter(new window.THREE.Vector3());
      if (id === 'leash') v.copy(o.position);
      v.project(d.camera);
      return { x: (v.x * 0.5 + 0.5) * innerWidth, y: (-v.y * 0.5 + 0.5) * innerHeight };
    }, id);
  }
  async function win() {
    await p.waitForFunction(() => window.qaDirector?.phase === 'result', { timeout: 90000 });
    return p.evaluate(() => window.qaCalls);
  }
  await mount('home_hide_seek');
  let q = await point('ball');
  await p.mouse.move(q.x, q.y);
  await p.mouse.down();
  await p.mouse.move(q.x - 65, q.y - 65, { steps: 6 });
  await p.mouse.up();
  assert.equal((await win())[0].outcome, 'win');
  report.checks.push('actual raycast ball drag and release completes gravity/bounce/fetch film');
  console.log('PASS', report.checks.at(-1));
  await mount('street_walk');
  q = await point('leash');
  await p.mouse.move(q.x, q.y);
  await p.mouse.down();
  await p.mouse.move(q.x - 80, q.y, { steps: 7 });
  await p.mouse.up();
  await p.waitForFunction(() => window.qaDirector?.step === 1, { timeout: 30000 });
  report.checks.push('actual copper-ring raycast drag reaches sniff step and deforms rope');
  console.log('PASS', report.checks.at(-1));
  await mount('street_cafe');
  await p.screenshot({ path: out + '/cafe-signs-390.png', animations: 'disabled' });
  q = await point('noDogs');
  assert.ok(q.x > 0 && q.x < 390 && q.y > 150 && q.y < 700);
  let w = await point('welcome');
  assert.ok(w.x > 0 && w.x < 390);
  await p.mouse.click(q.x, q.y);
  assert.equal((await win())[0].outcome, 'hazard_fail');
  report.checks.push(
    'both English storefront targets fit portrait; real NO DOGS raycast gives hazard_fail',
  );
  console.log('PASS', report.checks.at(-1));
  await mount('home_brush');
  await p.locator('#cinematic-stage canvas').focus();
  await p.keyboard.press('Space');
  await p.waitForFunction(() => window.qaDirector.warning, { timeout: 30000 });
  await p.keyboard.press('Space');
  await p.waitForFunction(() => !window.qaDirector.warning, { timeout: 15000 });
  await p.keyboard.press('Space');
  assert.equal((await win())[0].outcome, 'win');
  await p.screenshot({ path: out + '/brush-capsule-390.png', animations: 'disabled' });
  report.checks.push('manual grooming: warning, stop, rest, resume, one win');
  console.log('PASS', report.checks.at(-1));
  await p.route('**/assets/models/bruce.glb', (r) =>
    r.fulfill({ status: 200, contentType: 'model/gltf-binary', body: glb() }),
  );
  await mount('home_brush');
  await p.waitForFunction(() => window.qaDirector.bruce.mode === 'glb', { timeout: 30000 });
  const loaded = await p.evaluate(() => {
    const d = window.qaDirector,
      m = d.bruce.root.children[0].children.find((c) => c.children[0]?.name === 'FixtureScene');
    const copy = m.clone(true),
      isolated = new window.THREE.Scene();
    isolated.add(copy);
    isolated.updateMatrixWorld(true);
    const bounds = new window.THREE.Box3().setFromObject(copy),
      size = bounds.getSize(new window.THREE.Vector3()),
      center = bounds.getCenter(new window.THREE.Vector3());
    for (const mood of ['happy', 'excited', 'curious', 'warn', 'sulk', 'sleep', 'belly']) {
      d.bruce.setMood(mood);
      for (let i = 0; i < 60; i++) d.bruce.update(1 / 60, i / 60);
    }
    const gl = d.renderer.getContext();
    d.destroy();
    return {
      max: Math.max(size.x, size.y, size.z),
      minY: bounds.min.y,
      centerX: center.x,
      centerZ: center.z,
      contextLost: gl.isContextLost(),
      children: d.scene.children.length,
      listeners: d.listeners.length,
    };
  });
  assert.ok(Math.abs(loaded.max - 2.65) < 0.0001, JSON.stringify(loaded));
  assert.ok(Math.abs(loaded.minY) < 0.0001);
  assert.ok(Math.abs(loaded.centerX) < 0.0001);
  assert.ok(Math.abs(loaded.centerZ) < 0.0001);
  assert.equal(loaded.contextLost, true);
  assert.equal(loaded.children, 0);
  assert.equal(loaded.listeners, 0);
  report.checks.push(
    'valid synthetic GLB loads, recenters, normalizes to 2.65, all seven moods run; destroy releases context/tree/listeners',
  );
  console.log('PASS', report.checks.at(-1));
  await p.unroute('**/assets/models/bruce.glb');
  await p.evaluate(async () => {
    const { mountCinematicStage } = await import('./js/cinematic/index.js');
    window.qaHandle = mountCinematicStage(document.getElementById('cinematic-stage'), {
      activityId: 'home_brush',
      happiness: 100,
      content: await (await fetch('./data/content.json')).json(),
      quality: 'low',
    });
    window.qaHandle.setAutoplay(true);
  });
  assert.equal(await p.evaluate(() => window.qaHandle.getSnapshot().autoplay), true);
  await p.evaluate(() => {
    window.qaHandle.destroy();
    window.qaHandle.destroy();
  });
  assert.equal(await p.locator('#cinematic-stage canvas').count(), 0);
  assert.equal(await p.evaluate(() => document.body.style.overflow), '');
  report.checks.push('stable public handle follows restarted director; repeated destroy is safe');
  assert.deepEqual(report.errors, []);
  fs.writeFileSync(out + '/report.json', JSON.stringify(report, null, 2));
  await b.close();
  console.log('PASS advanced', report.checks.length);
})().catch((e) => {
  report.errors.push(e.stack);
  fs.writeFileSync(out + '/report.json', JSON.stringify(report, null, 2));
  console.error(e);
  process.exit(1);
});
