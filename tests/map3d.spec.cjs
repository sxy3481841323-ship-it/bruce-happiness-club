/* Run npm run test:map3d. Set CHROMIUM_PATH to use a system Chromium. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const http = require('node:http');
const fs = require('node:fs/promises');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const root = path.resolve(__dirname, '..');
const artifacts = process.env.MAP3D_ARTIFACT_DIR || path.join(root, 'test-results/map3d');
const results = [], scriptErrors = [], failedAssets = [], remoteRequests = [];
const scope = process.env.MAP3D_TEST_SCOPE || 'all';
assert(['all','module','integration'].includes(scope),'MAP3D_TEST_SCOPE must be all, module, or integration');
let base, browser;
const harness = `<!doctype html><html lang="zh-CN"><head><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><style>html,body{margin:0;width:100%;height:100%}#map{width:100%;height:100dvh}</style><script type="importmap">{"imports":{"three":"/vendor/three.module.js","three/addons/":"/vendor/addons/"}}</script></head><body><main id="map"></main><script type="module">import {mountWorldMap3D} from '/js/map3d.js';window.selections=[];window.remount=()=>window.map=mountWorldMap3D(document.querySelector('#map'),{onSelectPlayable:id=>selections.push({id,preview:false}),onSelectPreview:id=>selections.push({id,preview:true})});remount();</script></body></html>`;
const mime = { '.html':'text/html', '.js':'text/javascript', '.css':'text/css', '.json':'application/json', '.jpg':'image/jpeg', '.png':'image/png', '.svg':'image/svg+xml' };
const server = http.createServer(async (req,res) => {
  try {
    const url = new URL(req.url,'http://localhost');
    if (url.pathname === '/__map3d_test.html') { res.setHeader('Content-Type','text/html; charset=utf-8'); res.end(harness); return; }
    const filename = path.resolve(root,'.'+decodeURIComponent(url.pathname === '/' ? '/index.html' : url.pathname));
    if (!filename.startsWith(root+path.sep)) { res.writeHead(403).end(); return; }
    const data = await fs.readFile(filename);
    res.setHeader('Content-Type',mime[path.extname(filename)] || 'application/octet-stream');
    res.end(data);
  } catch { res.writeHead(404).end(); }
});
function passed(name) { results.push(name); console.log('PASS',name); }
async function observe(page) {
  page.on('pageerror',e=>scriptErrors.push(e.message));
  page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('/js/cinematic/bruceModel.js'))failedAssets.push(r.url());});
  page.on('request',r=>{if(!r.url().startsWith(base)&&!r.url().startsWith('data:'))remoteRequests.push(r.url());});
}
async function ready(page,route='/__map3d_test.html') {
  await page.goto(base+route);
  await page.waitForSelector('.wm3d[data-ready=true]',{timeout:90000});
}
async function labels(page,name) {
  await page.waitForFunction(()=>[...document.querySelectorAll('.wm3d-label:not([hidden])')].every(el=>{const r=el.getBoundingClientRect();return r.x>=-.1&&r.y>=-.1&&r.right<=innerWidth+.1&&r.bottom<=innerHeight+.1;}),null,{timeout:15000});
  const boxes = await page.locator('.wm3d-label:not([hidden])').evaluateAll(els=>els.map(e=>{const r=e.getBoundingClientRect();return {id:e.dataset.location,x:r.x,y:r.y,w:r.width,h:r.height};}));
  const size=page.viewportSize();
  assert.equal(boxes.length,8,`${name}: missing label`);
  for (const a of boxes) {
    assert(a.x>=-.1 && a.y>=-.1 && a.x+a.w<=size.width+.1 && a.y+a.h<=size.height+.1,`${name}: clipped ${a.id}`);
    assert(a.h>=43.9,`${name}: ${a.id} touch target too small (${a.h}px)`);
    for (const b of boxes) if (a.id<b.id) {
      const overlap=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)>.7 && Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y)>.7;
      assert(!overlap,`${name}: ${a.id} overlaps ${b.id}`);
    }
  }
  passed(name+' · eight readable, unclipped, nonoverlapping labels');
}
async function select(page,id,preview) {
  const count=await page.evaluate(()=>selections.length);
  await page.locator(`[data-location=${id}]`).focus();
  await page.keyboard.press('Enter');
  await page.waitForFunction(n=>selections.length===n+1,count,{timeout:30000});
  assert.deepEqual(await page.evaluate(()=>selections.at(-1)),{id,preview});
}
async function overview(page) {
  await page.locator('[data-map-reset]').click();
  await page.waitForFunction(()=>document.querySelectorAll('.wm3d-label:not([hidden])').length===8);
}
async function mainMood(page,value) { await page.evaluate(async score=>{const {store}=await import('/js/state.js');store.setHappiness(score);},value); }

(async()=>{
  await fs.mkdir(artifacts,{recursive:true});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  base=`http://127.0.0.1:${server.address().port}`;
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader']});
  if (scope !== 'integration') {
  const page=await browser.newPage({viewport:{width:1280,height:800},deviceScaleFactor:1});
  await observe(page); await ready(page);
  assert.deepEqual(await page.evaluate(()=>Object.keys(map).sort()),['destroy','setSulking']); passed('public mount, setSulking and destroy contract');
  await labels(page,'1280×800');
  const roof=await page.locator('.wm3d-leaders circle').first().evaluate(el=>({x:Number(el.getAttribute('cx')),y:Number(el.getAttribute('cy'))}));
  await page.locator('.wm3d-canvas').click({position:roof});
  await page.waitForFunction(()=>selections.length===1,{},{timeout:30000});
  assert.deepEqual(await page.evaluate(()=>selections[0]),{id:'home',preview:false});passed('canvas raycast selects the residence');
  await overview(page);
  await select(page,'home',false); passed('home fly-to completes before playable callback');
  await page.screenshot({path:path.join(artifacts,'villa-closeup.png')});
  await overview(page); await select(page,'street',false); passed('street playable callback');
  await overview(page); await select(page,'nordic',true); passed('phase-two callback preserves destination ID');
  await overview(page);
  await page.evaluate(()=>{window.originalCanvas=document.querySelector('canvas');map.setSulking(true);});
  const count=await page.evaluate(()=>selections.length);
  await page.locator('[data-location=home]').press('Enter'); await page.waitForTimeout(1600);
  assert.equal(await page.evaluate(()=>selections.length),count); assert.equal(await page.locator('.wm3d').getAttribute('data-weather'),'rain');
  assert(await page.evaluate(()=>document.querySelector('canvas')===originalCanvas)); passed('rain blocks playable entrances without replacing canvas');
  await page.evaluate(()=>map.setSulking(false)); await overview(page);
  await page.locator('[data-location=home]').press('Enter'); await page.evaluate(()=>map.setSulking(true)); await page.waitForTimeout(1600);
  assert.equal(await page.evaluate(()=>selections.length),count); passed('entering cold state cancels pending playable selection');
  await page.evaluate(()=>{map.destroy();map.destroy();}); assert.equal(await page.locator('.wm3d').count(),0); passed('idempotent destroy removes DOM');
  await page.evaluate(()=>{remount();remount();}); await page.waitForSelector('.wm3d[data-ready=true]',{timeout:90000}); assert.equal(await page.locator('canvas').count(),1); passed('repeated mounting replaces the previous instance');
  await page.close();

  const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1}); await observe(mobile); await ready(mobile);
  await labels(mobile,'390×844');
  const cdp=await mobile.context().newCDPSession(mobile);
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:150,y:590}]});
  await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:240,y:620}]});
  await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]}); await mobile.waitForTimeout(1400);
  assert.equal(await mobile.evaluate(()=>selections.length),0); passed('touch swipe changes view without accidental activation');
  await mobile.locator('[data-location=home]').tap(); await mobile.waitForFunction(()=>selections.length===1,{},{timeout:30000}); assert.equal(await mobile.evaluate(()=>selections[0].id),'home'); passed('touch tap selects home');
  await overview(mobile); await mobile.setViewportSize({width:360,height:740}); await labels(mobile,'360×740'); await mobile.close();
  }

  if (scope !== 'module') {
  const app=await browser.newPage({viewport:{width:1280,height:800},deviceScaleFactor:1}); await observe(app);
  await app.route('**/api/**',route=>{const body=route.request().postDataJSON();return route.fulfill({json:{ok:true,player:{nickname:body?.nickname||'沙盘测试',owner:body?.owner||'Alex',happiness:100},leaderboard:[],ticker:[]}});});
  await ready(app,'/');
  await app.locator('#input-nickname').fill('沙盘测试');await app.locator('#input-pin').fill('4321');await app.locator('#btn-enter-game').click();await app.locator('#onboarding-modal').waitFor({state:'hidden'});
  await labels(app,'integrated desktop');await app.screenshot({path:path.join(artifacts,'desktop.png')});
  await app.locator('[data-location=home]').press('Enter');await app.waitForSelector('#view-scene:not(.hidden)',{timeout:30000});assert.equal(await app.locator('[data-pick-act]').count(),5);assert.equal(await app.locator('.wm3d').count(),0);passed('home opens existing five activities and disposes map');
  await app.locator('#btn-scene-to-map').click();await app.waitForSelector('.wm3d[data-ready=true]',{timeout:90000});
  await app.locator('[data-location=street]').press('Enter');await app.waitForSelector('#view-scene:not(.hidden)',{timeout:30000});assert.equal(await app.locator('[data-pick-act]').count(),5);passed('street opens existing five activities');
  await app.locator('#btn-scene-to-map').click();await app.waitForSelector('.wm3d[data-ready=true]',{timeout:90000});
  await app.locator('[data-location=nordic]').press('Enter');await app.waitForSelector('#generic-modal:not(.hidden)',{timeout:30000});assert.equal(await app.locator('#map-preview-title').textContent(),'云端航线');await app.keyboard.press('Escape');passed('existing preview content uses nonregional title and keyboard close');
  await overview(app);await app.evaluate(()=>window.originalCanvas=document.querySelector('.wm3d-canvas'));await mainMood(app,79);
  assert(await app.evaluate(()=>originalCanvas===document.querySelector('.wm3d-canvas')));assert.equal(await app.locator('.wm3d').getAttribute('data-weather'),'rain');
  await mainMood(app,80);assert.equal(await app.locator('.wm3d').getAttribute('data-weather'),'sun');passed('native 79/80 score updates change weather in-place');
  await app.setViewportSize({width:390,height:844});await labels(app,'integrated phone');await app.screenshot({path:path.join(artifacts,'mobile.png')});
  await mainMood(app,79);await labels(app,'integrated rainy phone');await app.waitForTimeout(1700);await app.screenshot({path:path.join(artifacts,'mobile-rain.png')});
  await app.locator('.world-map-shop').click();await app.waitForSelector('#view-shop:not(.hidden)');assert.equal(await app.locator('.wm3d').count(),0);passed('cold-state comfort button opens existing shop'); await app.close();
  }

  const fallback=await browser.newPage({viewport:{width:390,height:844}});await observe(fallback);
  await fallback.addInitScript(()=>{const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return type.includes('webgl')?null:original.call(this,type,...args);};});
  await fallback.goto(base+'/__map3d_test.html');await fallback.waitForSelector('.wm3d[data-ready=fallback]');await fallback.locator('[data-location=park]').press('Enter');assert.deepEqual(await fallback.evaluate(()=>selections[0]),{id:'park',preview:true});passed('no-WebGL fallback retains accessible selection');await fallback.close();

  assert.deepEqual(scriptErrors,[]);assert.deepEqual(failedAssets,[]);assert.deepEqual(remoteRequests,[]);passed('no uncaught errors, missing required assets or remote/CDN requests');
  const forbidden=['data/content.json','js/state.js','js/api.js','functions','scripts/dev_server.py','js/cinematic'];
  const changes=execFileSync('git',['diff','HEAD','--',...forbidden],{cwd:root,encoding:'utf8'});assert.equal(changes,'');passed('protected backend, content, state, API and cinematic paths unchanged');
  await fs.writeFile(path.join(artifacts,`verification-${scope}.json`),JSON.stringify({scope,passed:results.length,checks:results},null,2));
  console.log(`Completed ${results.length} checks.`);
})().catch(e=>{console.error(e.stack);process.exitCode=1;}).finally(async()=>{await browser?.close();server.close();});
