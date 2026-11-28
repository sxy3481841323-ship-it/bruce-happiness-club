import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { createLivingBruce } from "../hub3d/bruceLiving.js";
import { mountBruceChatBar } from "../hub3d/bruceChatUi.js";
import { createLuckyMeteorController } from "../hub3d/luckyMeteor.js";
import { createHarbourWater } from "./yachtWater.js";
import {
  YACHT_CAM_PRESETS,
  YACHT_DRONE_TRACKS,
  DOCK_SPAWN_POS,
  DOCK_SPAWN_YAW,
  adaptPoseForAspect,
  buildArcLengthTrack,
  buildSafeTransitionSpline,
} from "./yachtCamMath.js";
import { sfx } from "../audio.js";
import { feedback } from "../juice.js";

const ASSET_URLS = {
  berth: "./assets/models/yacht_berth.glb",
  hull_rig: "./assets/models/yacht_hull_rig.glb",
  deck_salon: "./assets/models/yacht_deck_salon.glb",
  furniture_props: "./assets/models/yacht_furniture_props.glb",
};

const WORDLESS_CREST_SVG = `
  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
    <polygon points="12,2 21,12 12,22 3,12"/>
    <polygon points="12,5.6 17.4,12 12,18.4 6.6,12"/>
  </svg>
`;

const DEFAULT_YACHT_COPY = {
  beats: {
    yacht_shade_mat: "这儿有一小块阴凉。",
    yacht_bow_wind: "海风走在我们前面。",
    yacht_salon_nap: "我听着水声，就眯一会儿。",
  },
  idle_happy: [
    "柚木浮桥晒得刚好，左舷水线泛着香槟微光。",
    "敞门后面那张洞石吧台凉丝丝的，海风从后沙龙穿过去。",
    "帆板折起一半停在泊位上，走近些能听见水拍着桩脚。",
  ],
  idle_sulk: [
    "幸福指数低于 80 分了，先把我的心情哄顺再登船吧。",
    "海面起风了，我先蹲在浮桥边吹吹风。",
  ],
  click_poke: [
    "酒红丝巾刚系平整，海风一来尾巴就会轻轻飘。",
    "再轻轻摸一下头，我就跑去船首看海鸟。",
  ],
};

let preloadedBuffers = null;
let preloadPromise = null;

export function preloadYachtAssets({ simulateError = false } = {}) {
  if (simulateError) {
    return Promise.reject(new Error("模拟泊位预载失败：网络连接中断"));
  }
  if (preloadedBuffers) return Promise.resolve(preloadedBuffers);
  if (preloadPromise) return preloadPromise;

  preloadPromise = Promise.all(
    Object.entries(ASSET_URLS).map(async ([key, url]) => {
      const resp = await fetch(url);
      if (!resp.ok) throw new Error(`预载 ${key} 失败 (${resp.status})`);
      const buf = await resp.arrayBuffer();
      return [key, buf];
    }),
  )
    .then((entries) => {
      preloadedBuffers = Object.fromEntries(entries);
      return preloadedBuffers;
    })
    .catch((err) => {
      preloadPromise = null;
      throw err;
    });

  return preloadPromise;
}

function ensureStyles() {
  if (typeof document === "undefined") return;
  for (const href of ["./css/hub3d.css", "./css/scenes3d.css"]) {
    if (!document.querySelector(`link[href*="${href.replace("./", "")}"]`)) {
      const l = document.createElement("link");
      l.rel = "stylesheet";
      l.href = href;
      document.head.appendChild(l);
    }
  }
}

function pickRandom(arr, fallback = "") {
  if (!Array.isArray(arr) || !arr.length) return fallback;
  return arr[Math.floor(Math.random() * arr.length)];
}

export function mountYachtHub(container, opts = {}) {
  ensureStyles();

  let sulking = Boolean(opts.sulking);
  let content = opts.content || {};
  let happiness = opts.happiness ?? 100;
  let yachtCopy = DEFAULT_YACHT_COPY;

  document.body.classList.add("is-hub3d-view");
  document.body.classList.remove("is-hub3d-act");

  fetch("./data/scenes_yacht.json")
    .then((r) => (r.ok ? r.json() : null))
    .then((json) => {
      if (!destroyed && json) {
        yachtCopy = {
          beats: { ...DEFAULT_YACHT_COPY.beats, ...(json.beats || {}) },
          idle_happy: json.thought_bubbles?.idle_happy || DEFAULT_YACHT_COPY.idle_happy,
          idle_sulk: json.thought_bubbles?.idle_sulk || DEFAULT_YACHT_COPY.idle_sulk,
          click_poke: json.thought_bubbles?.click_poke || DEFAULT_YACHT_COPY.click_poke,
        };
      }
    })
    .catch(() => {});

  let destroyed = false;
  let rafId = null;
  let waterPaused = false;
  let pausedWaterTime = 0;

  const timers = new Set();
  const cleanups = [];
  const disposables = [];

  const later = (fn, ms) => {
    const id = setTimeout(() => {
      timers.delete(id);
      if (!destroyed) fn();
    }, ms);
    timers.add(id);
    return id;
  };

  container.innerHTML = `
    <div class="hub3d-wrap sc3d-yacht-wrap">
      <div class="hub3d-stage">
        <canvas class="hub3d-canvas"></canvas>
        <div class="hub3d-vignette ${sulking ? "is-sulk" : ""}"></div>
        <div class="hub3d-viewfinder" aria-hidden="true">
          <span class="vf-corner vf-tl"></span>
          <span class="vf-corner vf-tr"></span>
          <span class="vf-corner vf-bl"></span>
          <span class="vf-corner vf-br"></span>
          <span class="vf-stamp">FLY·04 · MARINA BERTH · 20M</span>
        </div>

        <div class="sc3d-yacht-cam-strip" role="group" aria-label="游艇机位切换">
          <span class="sc3d-yacht-crest">${WORDLESS_CREST_SVG}</span>
          <button type="button" class="sc3d-yacht-pill is-active" data-cam="overview">主总览</button>
          <button type="button" class="sc3d-yacht-pill" data-cam="starboard_scenic">右舷观海</button>
          <button type="button" class="sc3d-yacht-pill" data-cam="aft_door">后沙龙敞门</button>
          <button type="button" class="sc3d-yacht-pill" data-cam="cabin_bar">舱内吧台</button>
          <button type="button" class="sc3d-yacht-pill" data-cam="bow_bruce">船首特写</button>
          <button type="button" class="sc3d-yacht-pill" data-cam="dock_landing">浮桥落点</button>
        </div>

        <div class="sc3d-yacht-drone-status hidden" id="yacht-drone-status" aria-live="polite">
          <span class="sc3d-yacht-crest">${WORDLESS_CREST_SVG}</span>
          <span id="yacht-drone-status-text">左舷俯掠 · 航拍中</span>
          <button type="button" class="sc3d-yacht-pill is-skip" id="btn-yacht-drone-skip">跳过航拍</button>
        </div>

        <div class="sc3d-yacht-drone-bar" role="toolbar" aria-label="双轨俯视航拍控制">
          <span class="sc3d-yacht-crest">${WORDLESS_CREST_SVG}</span>
          <button type="button" class="sc3d-yacht-pill" data-drone="port">左舷俯掠</button>
          <button type="button" class="sc3d-yacht-pill" data-drone="starboard">右舷俯推</button>
          <button type="button" class="sc3d-yacht-pill" data-drone="both">双轨连播</button>
          <button type="button" class="sc3d-yacht-pill" id="btn-yacht-speed" data-speed="1">1.0×</button>
          <button type="button" class="sc3d-yacht-pill" id="btn-yacht-water" data-action="toggle-water">定格水面</button>
          <button type="button" class="sc3d-yacht-pill" id="btn-yacht-mood" data-action="toggle-mood">🌅 晚航</button>
        </div>

        <div class="hub3d-pins"></div>

        <div class="hub3d-keyholder">
          <button type="button" class="keyholder-btn" aria-expanded="false">
            <span class="keyholder-fob">${WORDLESS_CREST_SVG}</span>
            <span>码头通行卡</span>
            <span class="keyholder-count">3</span>
          </button>
          <div class="keyholder-tray" role="menu" aria-label="前往其他场景">
            <div class="keyholder-tray-head">
              <span>PRIVATE BERTH</span>
              <span>点击返回或前往</span>
            </div>
          </div>
        </div>

        <div class="hub3d-speech" aria-live="polite">
          <span class="speech-cue"></span>
          <span class="speech-line"></span>
        </div>

        <div class="hub3d-tricks-bar" role="toolbar" aria-label="游艇互动与动作">
          <button type="button" class="trick-pill" data-beat="yacht_shade_mat">风过耳边</button>
          <button type="button" class="trick-pill" data-beat="yacht_bow_wind">船首听风</button>
          <button type="button" class="trick-pill" data-beat="yacht_salon_nap">靠窗一会儿</button>
          <button type="button" class="trick-pill" data-trick="roll_over">晒肚皮</button>
          <button type="button" class="trick-pill" data-trick="lick_paw">舔爪子</button>
          <button type="button" class="trick-pill is-ai-chat" id="hub3d-btn-chat">✦ 逗它说话</button>
        </div>
        <button type="button" class="hub3d-reset-btn">⌖ 归中视角</button>

        <div class="sc3d-yacht-fade" id="yacht-fade-veil"></div>
        <div class="hub3d-lucky-toast" id="yacht-lucky-toast" role="status" aria-live="polite">
          <span class="lucky-star-badge" aria-hidden="true">✦</span>
          <div class="lucky-toast-body">
            <div class="lucky-toast-title">幸运时刻 · 流星掠过海平线</div>
            <div class="lucky-toast-sub" id="yacht-lucky-sub">布鲁斯仰头许愿 · 幸福指数 +8</div>
          </div>
        </div>
        <div class="hub3d-loading">
          <span>正在停靠私家柚木泊位……</span>
        </div>
      </div>
      <p class="hub3d-hint">点地面或浮桥唤布鲁斯同行 · 右舷航拍可直望敞门后吧台 · 点击三大互动体验船上时光</p>
    </div>
  `;

  const wrapEl = container.querySelector(".hub3d-wrap");
  const stageEl = container.querySelector(".hub3d-stage");
  const canvas = container.querySelector(".hub3d-canvas");
  const loadingEl = container.querySelector(".hub3d-loading");
  const fadeVeil = container.querySelector("#yacht-fade-veil");
  const droneStatusEl = container.querySelector("#yacht-drone-status");
  const droneStatusTxt = container.querySelector("#yacht-drone-status-text");
  const btnDroneSkip = container.querySelector("#btn-yacht-drone-skip");
  const btnSpeed = container.querySelector("#btn-yacht-speed");
  const btnWaterToggle = container.querySelector("#btn-yacht-water");
  const speechEl = container.querySelector(".hub3d-speech");
  const speechCueEl = speechEl?.querySelector(".speech-cue");
  const speechLineEl = speechEl?.querySelector(".speech-line");
  const keyholderEl = container.querySelector(".hub3d-keyholder");
  const keyholderBtn = container.querySelector(".keyholder-btn");
  const keyholderTray = container.querySelector(".keyholder-tray");
  const pinsLayer = container.querySelector(".hub3d-pins");
  const resetBtn = container.querySelector(".hub3d-reset-btn");
  const luckyToastEl = container.querySelector("#yacht-lucky-toast");
  const luckySubEl = container.querySelector("#yacht-lucky-sub");

  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const lowTier = dpr <= 1.0 && Math.min(window.innerWidth, window.innerHeight) < 760;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(dpr);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.02;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(sulking ? 0x2c4b6e : 0x5c96cc);
  scene.fog = new THREE.FogExp2(sulking ? 0x456689 : 0x9bc4e8, 0.00072);

  // 360-degree Mediterranean Sky Dome with procedural cirrus/cumulus clouds & sun glow
  const skyUniforms = {
    uZenith: { value: new THREE.Color(sulking ? 0x163254 : 0x164a8d) },
    uMid: { value: new THREE.Color(sulking ? 0x3b638f : 0x478ad1) },
    uHorizon: { value: new THREE.Color(sulking ? 0xa5bacf : 0xf2ddc0) },
    uSunDir: { value: new THREE.Vector3(27.0, 22.8, -26.5).normalize() },
    uSunCol: { value: new THREE.Color(0xfff0cc) },
    uTime: { value: 0 },
  };
  const skyDomeMat = new THREE.ShaderMaterial({
    uniforms: skyUniforms,
    side: THREE.BackSide,
    depthWrite: false,
    vertexShader: `
      varying vec3 vDir;
      void main() {
        vDir = normalize(position);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 uZenith, uMid, uHorizon, uSunDir, uSunCol;
      uniform float uTime;
      varying vec3 vDir;
      float hash2(vec2 p) {
        return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
      }
      float vnoise(vec2 p) {
        vec2 i = floor(p), f = fract(p);
        f = f * f * (3.0 - 2.0 * f);
        return mix(
          mix(hash2(i), hash2(i + vec2(1.0, 0.0)), f.x),
          mix(hash2(i + vec2(0.0, 1.0)), hash2(i + vec2(1.0, 1.0)), f.x),
          f.y
        );
      }
      void main() {
        vec3 d = normalize(vDir);
        float h = clamp(d.y, 0.0, 1.0);
        vec3 sky = mix(uHorizon, uMid, smoothstep(0.0, 0.24, h));
        sky = mix(sky, uZenith, smoothstep(0.18, 0.78, h));
        float mu = max(dot(d, normalize(uSunDir)), 0.0);
        sky += uSunCol * (0.24 * pow(mu, 8.0) + 0.70 * pow(mu, 160.0));
        if (d.y > 0.025) {
          vec2 cuv = d.xz / (d.y + 0.16) * 1.45 + vec2(uTime * 0.0045, -uTime * 0.002);
          float cl = 0.55 * vnoise(cuv) + 0.30 * vnoise(cuv * 2.15 + 3.4) + 0.15 * vnoise(cuv * 4.5);
          float mask = smoothstep(0.56, 0.84, cl) * smoothstep(0.025, 0.19, d.y) * (1.0 - smoothstep(0.45, 0.92, d.y));
          sky = mix(sky, mix(vec3(0.98, 0.96, 0.92), uSunCol, 0.32), mask * 0.52);
        }
        gl_FragColor = vec4(sky, 1.0);
      }
    `,
  });
  const skyDome = new THREE.Mesh(new THREE.SphereGeometry(195, 40, 24), skyDomeMat);
  skyDome.name = "RivieraSkyDome";
  scene.add(skyDome);
  disposables.push(skyDome.geometry, skyDomeMat);

  // Mediterranean Riviera Coastal Vista (headlands, harbour mole + lighthouse, distant sailing sloops)
  const vistaGroup = new THREE.Group();
  vistaGroup.name = "RivieraVista";
  scene.add(vistaGroup);
  const headlandRockMat = new THREE.MeshStandardMaterial({ color: 0x8b7a67, roughness: 0.92 });
  const headlandPineMat = new THREE.MeshStandardMaterial({ color: 0x4b6346, roughness: 0.88 });
  const lighthouseStoneMat = new THREE.MeshStandardMaterial({ color: 0xdfd6c7, roughness: 0.8 });
  const distantSailMat = new THREE.MeshStandardMaterial({ color: 0xf5f0e6, roughness: 0.72, side: THREE.DoubleSide });
  const lighthouseGlowMat = new THREE.MeshBasicMaterial({ color: 0xffd27a });
  disposables.push(headlandRockMat, headlandPineMat, lighthouseStoneMat, distantSailMat, lighthouseGlowMat);

  [
    { x: -58, z: 94, rx: 32, ry: 11.5, rz: 20 },
    { x: -82, z: 62, rx: 24, ry: 8.5, rz: 18 },
    { x: 76, z: 118, rx: 38, ry: 13.5, rz: 22 },
    { x: 112, z: 54, rx: 28, ry: 9.5, rz: 20 },
  ].forEach(({ x, z, rx, ry, rz }) => {
    const rock = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), headlandRockMat);
    rock.scale.set(rx, ry, rz);
    rock.position.set(x, -1.5, z);
    const pines = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), headlandPineMat);
    pines.scale.set(rx * 0.82, ry * 0.56, rz * 0.78);
    pines.position.set(x + 1.5, ry * 0.34, z - 1.0);
    vistaGroup.add(rock, pines);
  });

  // Stone harbour mole & Mediterranean Lighthouse at (48, 0..14.5, 92)
  const mole = new THREE.Mesh(new THREE.BoxGeometry(28, 2.2, 5.4), headlandRockMat);
  mole.position.set(36, 0.1, 92);
  const lhTower = new THREE.Mesh(new THREE.CylinderGeometry(1.15, 1.85, 12.2, 16), lighthouseStoneMat);
  lhTower.position.set(48, 6.2, 92);
  const lhLantern = new THREE.Mesh(new THREE.CylinderGeometry(0.95, 0.95, 1.5, 12), lighthouseGlowMat);
  lhLantern.position.set(48, 12.9, 92);
  const lhCap = new THREE.Mesh(new THREE.ConeGeometry(1.35, 1.6, 14), headlandRockMat);
  lhCap.position.set(48, 14.35, 92);
  const lhBeacon = new THREE.PointLight(0xffcb74, 2.2, 34, 1.4);
  lhBeacon.position.set(48, 13.0, 92);
  vistaGroup.add(mole, lhTower, lhLantern, lhCap, lhBeacon);

  const distantSails = [];
  [
    { x: -24, z: 74, dir: 1, speed: 0.42, yaw: 0.25 },
    { x: 16, z: 98, dir: -1, speed: 0.34, yaw: -0.35 },
    { x: 64, z: 68, dir: 1, speed: 0.48, yaw: 0.18 },
  ].forEach((cfg) => {
    const boat = new THREE.Group();
    const hull = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.65, 5.4), headlandRockMat);
    hull.position.y = 0.22;
    const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.08, 7.6, 8), lighthouseStoneMat);
    mast.position.set(0, 4.0, 0.2);
    const sailGeo = new THREE.BufferGeometry();
    sailGeo.setAttribute(
      "position",
      new THREE.Float32BufferAttribute([0, 1.1, 0.1, 0, 7.5, 0.1, 0, 1.1, -2.5], 3),
    );
    sailGeo.computeVertexNormals();
    const mainSail = new THREE.Mesh(sailGeo, distantSailMat);
    boat.add(hull, mast, mainSail);
    boat.position.set(cfg.x, 0, cfg.z);
    boat.rotation.y = cfg.yaw;
    vistaGroup.add(boat);
    distantSails.push({ boat, originX: cfg.x, dir: cfg.dir, speed: cfg.speed });
  });

  // 7600K crisp sky PMREM environment without bloom blowout
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene();
  envScene.background = new THREE.Color(0xbcd4ec);
  const envUpper = new THREE.Mesh(
    new THREE.SphereGeometry(40, 24, 16),
    new THREE.MeshBasicMaterial({ color: 0xd3e4f6, side: THREE.BackSide }),
  );
  const envSea = new THREE.Mesh(
    new THREE.PlaneGeometry(80, 80),
    new THREE.MeshBasicMaterial({ color: 0x1e4466 }),
  );
  envSea.rotation.x = -Math.PI / 2;
  envSea.position.y = -2;
  envScene.add(envUpper, envSea);
  const envRT = pmrem.fromScene(envScene, 0.04);
  scene.environment = envRT.texture;
  scene.environmentIntensity = 0.44;
  pmrem.dispose();
  envUpper.geometry.dispose();
  envUpper.material.dispose();
  envSea.geometry.dispose();
  envSea.material.dispose();
  disposables.push(envRT);

  // 4700K afternoon sun at 31 deg elevation from (+X, +Y, -Z) illuminating hull window band & open doorway
  const sunLight = new THREE.DirectionalLight(0xffebd2, 4.45);
  sunLight.position.set(27.0, 22.8, -26.5);
  sunLight.target.position.set(0, 1.5, -1.5);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.set(2048, 2048);
  sunLight.shadow.camera.near = 2;
  sunLight.shadow.camera.far = 85;
  sunLight.shadow.camera.left = -16;
  sunLight.shadow.camera.right = 16;
  sunLight.shadow.camera.top = 18;
  sunLight.shadow.camera.bottom = -16;
  sunLight.shadow.bias = -0.00045;
  sunLight.shadow.normalBias = 0.015;
  scene.add(sunLight, sunLight.target);

  const hemiLight = new THREE.HemisphereLight(0xd9e8f8, 0x26435a, 0.56);
  scene.add(hemiLight);

  // World-space Harbour Water (identity transform, Y=0)
  const water = createHarbourWater({ lowTier });
  scene.add(water.root);

  // Independent berth root & floating yacht root
  const berthRoot = new THREE.Group();
  berthRoot.name = "BerthRoot";
  const yachtRoot = new THREE.Group();
  yachtRoot.name = "YachtRoot";
  scene.add(berthRoot, yachtRoot);

  // Interior warm lighting inside Deck Salon (2700K lintel cove + 2850K sconces)
  const lintelCoveLight = new THREE.PointLight(0xffc784, 1.05, 7.0, 1.65);
  lintelCoveLight.position.set(0.0, 3.18, -2.55);
  const sconcePortLight = new THREE.PointLight(0xffd19a, 0.85, 5.2, 1.65);
  sconcePortLight.position.set(-1.32, 2.83, 0.15);
  const sconceStbdLight = new THREE.PointLight(0xffd19a, 0.85, 5.2, 1.65);
  sconceStbdLight.position.set(1.32, 2.83, 0.15);
  const barGlowLight = new THREE.PointLight(0xffce8f, 1.0, 4.8, 1.6);
  barGlowLight.position.set(0.0, 2.76, 1.12);
  yachtRoot.add(lintelCoveLight, sconcePortLight, sconceStbdLight, barGlowLight);

  water.setLights([
    { position: new THREE.Vector3(0.0, 2.9, -2.6), color: 0xffc784, power: 14, radius: 0.45 },
    { position: new THREE.Vector3(-1.3, 2.8, 0.2), color: 0xffd19a, power: 8, radius: 0.22 },
    { position: new THREE.Vector3(1.3, 2.8, 0.2), color: 0xffd19a, power: 8, radius: 0.22 },
    { position: new THREE.Vector3(27, 22.8, -26.5), color: 0xffebd2, power: 360, radius: 1.6 },
  ]);

  // Procedural coastal seabirds circling above bow channel (for Bow Wind head tracking)
  const gullGroup = new THREE.Group();
  scene.add(gullGroup);
  const gulls = [];
  const gullMat = new THREE.MeshStandardMaterial({ color: 0xf4f0e8, roughness: 0.65 });
  disposables.push(gullMat);
  for (let i = 0; i < 3; i++) {
    const g = new THREE.Group();
    const wingGeo = new THREE.BoxGeometry(0.32, 0.015, 0.11);
    const bodyGeo = new THREE.ConeGeometry(0.04, 0.24, 6);
    bodyGeo.rotateX(Math.PI / 2);
    const lWing = new THREE.Mesh(wingGeo, gullMat);
    lWing.position.set(-0.16, 0, 0);
    const rWing = new THREE.Mesh(wingGeo, gullMat);
    rWing.position.set(0.16, 0, 0);
    const body = new THREE.Mesh(bodyGeo, gullMat);
    g.add(body, lWing, rWing);
    disposables.push(wingGeo, bodyGeo);
    gullGroup.add(g);
    gulls.push({ group: g, lWing, rWing, phase: i * 2.1, r: 4.5 + i * 1.4, baseY: 6.4 + i * 0.9, baseZ: 14.5 + i * 1.8 });
  }

  // Dynamic articulated gangway (1.00 x 0.68 m) updated each frame from gangway_dock -> gangway_yacht
  const gangwayGroup = new THREE.Group();
  const gwDeckGeo = new THREE.BoxGeometry(1.0, 0.048, 0.68);
  gwDeckGeo.translate(0.5, -0.024, 0);
  const gwDeckMat = new THREE.MeshStandardMaterial({ color: 0xae885f, roughness: 0.63, metalness: 0.0 });
  const gwRailGeo = new THREE.BoxGeometry(1.0, 0.032, 0.028);
  gwRailGeo.translate(0.5, 0.02, 0.325);
  const gwRailMat = new THREE.MeshStandardMaterial({ color: 0xb49a72, roughness: 0.27, metalness: 1.0 });
  const gwMesh = new THREE.Mesh(gwDeckGeo, gwDeckMat);
  gwMesh.castShadow = true;
  gwMesh.receiveShadow = true;
  const gwRailA = new THREE.Mesh(gwRailGeo, gwRailMat);
  const gwRailB = new THREE.Mesh(gwRailGeo, gwRailMat);
  gwRailB.position.z = -0.65;
  gangwayGroup.add(gwMesh, gwRailA, gwRailB);
  scene.add(gangwayGroup);
  disposables.push(gwDeckGeo, gwDeckMat, gwRailGeo, gwRailMat);

  // Rigged metric-scale Bruce (height 0.42 m, burgundy #652C39 silk neckerchief)
  const bruce = createLivingBruce({ modelUrl: "./assets/models/bruce_rigged.glb", height: 0.42, scarf: true });
  bruce.root.position.copy(DOCK_SPAWN_POS);
  bruce.root.rotation.y = DOCK_SPAWN_YAW;
  bruce.setMood(sulking ? "sulk" : "happy");
  bruce.setWind(0.42);
  scene.add(bruce.root);
  let bruceOnYacht = false;

  // Anchors and loaded asset groups
  const anchors = {
    dock_spawn: DOCK_SPAWN_POS.clone(),
    gangway_dock: new THREE.Vector3(-2.85, 0.72, -5.2),
    gangway_yacht: new THREE.Vector3(-2.26, 1.29, -5.2),
    dog_bow: new THREE.Vector3(0, 1.58, 7.7),
    dog_mat: new THREE.Vector3(-1.05, 1.35, -3.85),
    dog_nap: new THREE.Vector3(-1.06, 1.75, -1.18),
    stool_top: new THREE.Vector3(-0.78, 1.48, -1.18),
    bar_top: new THREE.Vector3(0, 2.38, 1.22),
  };
  const assetReports = {};
  const loadedParts = {};
  const walkMeshes = [];
  const yachtSurfaceMeshes = [];

  const camera = new THREE.PerspectiveCamera(43, 16 / 9, 0.08, 220);
  const initCam = adaptPoseForAspect(YACHT_CAM_PRESETS.overview.camPos, YACHT_CAM_PRESETS.overview.lookAt, 43, 16 / 9);
  camera.position.copy(initCam.pos);

  const controls = new OrbitControls(camera, canvas);
  controls.target.copy(initCam.target);
  controls.enableDamping = true;
  controls.dampingFactor = 0.07;
  controls.minDistance = 0.85;
  controls.maxDistance = 38.0;
  controls.minPolarAngle = 0.18;
  controls.maxPolarAngle = 1.49;
  controls.update();

  let activeCamId = "overview";
  let camTransition = null;
  let droneState = null;
  let droneSpeed = 1.0;
  let beatState = null;
  let lastSpeechAt = 0;
  let speechTimer = null;

  function sayBruce(keyOrText, durationMs = 4200, cue = "BRUCE · 泊位") {
    if (!speechEl || !speechLineEl) return;
    let line = keyOrText;
    if (yachtCopy.beats?.[keyOrText]) line = yachtCopy.beats[keyOrText];
    else if (Array.isArray(yachtCopy[keyOrText])) line = pickRandom(yachtCopy[keyOrText]);
    if (!line) return;
    if (speechCueEl) speechCueEl.textContent = cue;
    speechLineEl.textContent = line;
    speechEl.classList.add("is-visible");
    lastSpeechAt = performance.now();
    if (speechTimer) {
      clearTimeout(speechTimer);
      timers.delete(speechTimer);
    }
    speechTimer = later(() => {
      speechEl.classList.remove("is-visible");
      speechTimer = null;
    }, durationMs);
  }

  function currentAspect() {
    const w = Math.max(1, stageEl.clientWidth || canvas.clientWidth || 1280);
    const h = Math.max(1, stageEl.clientHeight || canvas.clientHeight || 800);
    return w / h;
  }

  function applyPoseImmediate(pose) {
    camera.position.copy(pose.pos);
    camera.fov = pose.fov;
    camera.updateProjectionMatrix();
    controls.target.copy(pose.target);
    camera.up.set(0, 1, 0);
    camera.lookAt(pose.target);
    controls.update();
  }

  function fadeThen(cb) {
    if (!fadeVeil) {
      cb?.();
      return;
    }
    fadeVeil.classList.add("is-active");
    later(() => {
      cb?.();
      later(() => fadeVeil.classList.remove("is-active"), 60);
    }, 220);
  }

  function switchCameraPreset(presetId, { durationSec = 2.0, onDone = null } = {}) {
    const spec = YACHT_CAM_PRESETS[presetId];
    if (!spec) return;
    activeCamId = presetId;
    container.querySelectorAll("[data-cam]").forEach((b) => {
      b.classList.toggle("is-active", b.getAttribute("data-cam") === presetId);
    });
    if (presetId === "bow_bruce" && !beatState && loadedParts.hull_rig) {
      setBruceParent(true);
      bruce.stopWalk();
      bruce.setResting(null);
      const bx = anchors.dog_bow.x;
      const bz = anchors.dog_bow.z;
      const by = sampleYachtDeckSurface(bx, bz, 1.56, 2.8);
      bruce.root.position.set(bx, by, bz);
      bruce.root.rotation.y = 0.08;
    }
    const pose = adaptPoseForAspect(spec.camPos, spec.lookAt, spec.fov, currentAspect(), spec.narrowScale);
    const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
    if (reduceMotion) {
      fadeThen(() => {
        camTransition = null;
        applyPoseImmediate(pose);
        onDone?.();
      });
      return;
    }
    const spline = buildSafeTransitionSpline(
      camera.position,
      controls.target,
      pose.pos,
      pose.target,
      camera.fov,
      pose.fov,
      durationSec,
    );
    camTransition = {
      spline,
      elapsed: 0,
      endTarget: pose.target.clone(),
      onDone,
    };
  }

  const droneSamplers = {
    port: buildArcLengthTrack(
      YACHT_DRONE_TRACKS.port.camPoints,
      YACHT_DRONE_TRACKS.port.lookPoints,
      YACHT_DRONE_TRACKS.port.duration,
      YACHT_DRONE_TRACKS.port.fov,
    ),
    starboard: buildArcLengthTrack(
      YACHT_DRONE_TRACKS.starboard.camPoints,
      YACHT_DRONE_TRACKS.starboard.lookPoints,
      YACHT_DRONE_TRACKS.starboard.duration,
      YACHT_DRONE_TRACKS.starboard.fov,
    ),
  };

  function finishDroneSequence({ fadeToDock = true, holdFinalPose = null } = {}) {
    const onComplete = droneState?.onComplete;
    droneState = null;
    wrapEl?.classList.remove("is-drone-playing");
    droneStatusEl?.classList.add("hidden");
    controls.enabled = true;
    if (holdFinalPose && !fadeToDock) {
      applyPoseImmediate({ pos: holdFinalPose.pos, target: holdFinalPose.lookAt, fov: holdFinalPose.fov });
      onComplete?.();
      return;
    }
    const land = () => {
      bruce.stopWalk();
      setBruceParent(false);
      bruce.setResting(null);
      bruce.root.position.copy(anchors.dock_spawn);
      bruce.root.rotation.y = DOCK_SPAWN_YAW;
      const landing = adaptPoseForAspect(
        YACHT_CAM_PRESETS.dock_landing.camPos,
        YACHT_CAM_PRESETS.dock_landing.lookAt,
        YACHT_CAM_PRESETS.dock_landing.fov,
        currentAspect(),
        YACHT_CAM_PRESETS.dock_landing.narrowScale,
      );
      applyPoseImmediate(landing);
      activeCamId = "dock_landing";
      container.querySelectorAll("[data-cam]").forEach((b) => {
        b.classList.toggle("is-active", b.getAttribute("data-cam") === "dock_landing");
      });
      sayBruce(sulking ? "idle_sulk" : "idle_happy", 4200);
      onComplete?.();
    };
    if (fadeToDock) fadeThen(land);
    else land();
  }

  function startDroneReel(mode = "both", { fadeOnFinish = null, onComplete = null } = {}) {
    const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
    if (reduceMotion) {
      droneState = { onComplete };
      finishDroneSequence({ fadeToDock: true });
      return;
    }
    const queue = mode === "both" ? ["port", "starboard"] : [mode];
    const shouldFade = fadeOnFinish !== null ? fadeOnFinish : mode === "both";
    camTransition = null;
    controls.enabled = false;
    wrapEl?.classList.add("is-drone-playing");
    droneStatusEl?.classList.remove("hidden");
    droneState = {
      queue,
      idx: 0,
      t: 0,
      fadeOnFinish: shouldFade,
      onComplete,
    };
    const first = YACHT_DRONE_TRACKS[queue[0]];
    if (droneStatusTxt && first) droneStatusTxt.textContent = `${first.label} · 航拍中`;
  }

  btnDroneSkip?.addEventListener("click", (e) => {
    e.stopPropagation();
    sfx.playTap();
    if (droneState) finishDroneSequence({ fadeToDock: true });
  });

  btnWaterToggle?.addEventListener("click", (e) => {
    e.stopPropagation();
    sfx.playTap();
    waterPaused = !waterPaused;
    btnWaterToggle.classList.toggle("is-active", waterPaused);
    btnWaterToggle.textContent = waterPaused ? "继续水波" : "定格水面";
  });

  btnSpeed?.addEventListener("click", (e) => {
    e.stopPropagation();
    sfx.playTap();
    const cycle = [1.0, 1.5, 0.5];
    droneSpeed = cycle[(cycle.indexOf(droneSpeed) + 1) % cycle.length];
    btnSpeed.textContent = `${droneSpeed.toFixed(1)}×`;
    btnSpeed.setAttribute("data-speed", String(droneSpeed));
  });

  container.querySelectorAll("[data-cam]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      if (droneState) return;
      sfx.playTap();
      feedback("small", e.clientX, e.clientY);
      switchCameraPreset(btn.getAttribute("data-cam"));
    });
  });

  container.querySelectorAll("[data-drone]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      sfx.playTap();
      startDroneReel(btn.getAttribute("data-drone"), { fadeOnFinish: btn.getAttribute("data-drone") === "both" });
    });
  });

  function setBruceParent(onYacht) {
    if (bruceOnYacht === onYacht) return;
    const worldPos = new THREE.Vector3();
    bruce.root.getWorldPosition(worldPos);
    bruceOnYacht = Boolean(onYacht);
    if (bruceOnYacht) {
      yachtRoot.add(bruce.root);
      yachtRoot.worldToLocal(worldPos);
      bruce.root.position.copy(worldPos);
    } else {
      scene.add(bruce.root);
      bruce.root.position.copy(worldPos);
    }
  }

  const downRay = new THREE.Raycaster();
  function sampleYachtDeckSurface(localX, localZ, fallbackY, fromY = 3.2) {
    if (!yachtSurfaceMeshes.length) return fallbackY;
    const origin = new THREE.Vector3(localX, fromY, localZ).applyMatrix4(yachtRoot.matrixWorld);
    const downDir = new THREE.Vector3(0, -1, 0).transformDirection(yachtRoot.matrixWorld);
    downRay.set(origin, downDir);
    const hits = downRay.intersectObjects(yachtSurfaceMeshes, false);
    if (hits.length > 0) {
      const localHit = yachtRoot.worldToLocal(hits[0].point.clone());
      return localHit.y;
    }
    return fallbackY;
  }

  function settleYachtBeat(beatId, title, delta = 4) {
    opts.onSettle?.({ id: beatId, title, delta, outcome: "win" });
  }

  function triggerYachtBeat(beatId) {
    if (destroyed || droneState) return;
    beatState = null;
    bruce.stopWalk();
    bruce.setResting(null);
    bruce.setWind(0.45);
    setBruceParent(true);

    if (beatId === "yacht_shade_mat") {
      // Beat 1: walk onto cushioned linen mat (-1.05, 1.31, -3.85), lie chest-down 2.6s -> single line
      const matX = anchors.dog_mat.x;
      const matZ = anchors.dog_mat.z;
      const surfaceY = sampleYachtDeckSurface(matX, matZ, 1.385, 2.2);
      const startX = matX - 0.28;
      const startZ = matZ - 0.28;
      bruce.root.position.set(startX, sampleYachtDeckSurface(startX, startZ, 1.30, 2.2), startZ);
      switchCameraPreset("aft_door", { durationSec: 1.6 });
      sayBruce("yacht_shade_mat", 4800, "BRUCE · 风过耳边");
      bruce.walkTo(matX, matZ, {
        speedScale: 1.35,
        onArrive() {
          bruce.root.position.set(matX, Math.max(1.38, surfaceY), matZ);
          bruce.root.rotation.y = Math.PI * 0.85;
          bruce.setResting("chest_down");
          bruce.setWind(0.75);
          beatState = { id: beatId, timer: 2.6 };
          settleYachtBeat(beatId, "风过耳边", 4);
        },
      });
    } else if (beatId === "yacht_bow_wind") {
      // Beat 2: foredeck (0, 1.58, 7.70), nose lift + 22° coastal gull tracking -> bow close-up 2.2s
      const bx = anchors.dog_bow.x;
      const bz = anchors.dog_bow.z;
      const surfaceY = sampleYachtDeckSurface(bx, bz, 1.56, 2.8);
      bruce.root.position.set(bx, surfaceY, bz);
      bruce.root.rotation.y = 0.08;
      bruce.setWind(1.1);
      switchCameraPreset("bow_bruce", { durationSec: 1.8 });
      sayBruce("yacht_bow_wind", 4800, "BRUCE · 船首听风");
      beatState = { id: beatId, timer: 3.4, elapsed: 0 };
      settleYachtBeat(beatId, "船首听风", 5);
    } else if (beatId === "yacht_salon_nap") {
      // Beat 3: step onto 0.16 m stool then curved saddle-leather banquette facing open doorway
      const sx = anchors.stool_top.x;
      const sz = anchors.stool_top.z;
      const nx = anchors.dog_nap.x;
      const nz = anchors.dog_nap.z;
      const floorY = sampleYachtDeckSurface(sx + 0.35, sz, 1.32, 2.4);
      const stoolY = sampleYachtDeckSurface(sx, sz, 1.48, 2.4);
      const seatY = sampleYachtDeckSurface(nx, nz, 1.75, 2.4);
      bruce.root.position.set(sx + 0.38, floorY, sz - 0.15);
      switchCameraPreset("cabin_bar", { durationSec: 1.9 });
      sayBruce("yacht_salon_nap", 4800, "BRUCE · 靠窗一会儿");
      bruce.walkTo(sx, sz, {
        speedScale: 1.0,
        onArrive() {
          bruce.root.position.set(sx, stoolY, sz);
          bruce.triggerHappyHop();
          later(() => {
            bruce.root.position.set(nx, seatY, nz);
            bruce.root.rotation.y = Math.PI * 0.92; // Nose toward aft open doorway (-Z)
            bruce.setResting("curl_nap");
            bruce.setWind(0.22);
            settleYachtBeat(beatId, "靠窗一会儿", 4);
          }, 420);
        },
      });
    }
  }

  container.querySelectorAll("[data-beat]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      sfx.playTap();
      feedback("small", e.clientX, e.clientY);
      triggerYachtBeat(btn.getAttribute("data-beat"));
    });
  });

  container.querySelectorAll("[data-trick]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      if (droneState) return;
      sfx.playTap();
      bruce.setResting(null);
      const act = btn.getAttribute("data-trick");
      bruce.playAction(act);
    });
  });

  let sunsetMode = false;
  const moodBtn = container.querySelector("#btn-yacht-mood");
  const applyAtmosphereMood = () => {
    const isSunset = sunsetMode;
    if (isSunset) {
      skyUniforms.uZenith.value.setHex(sulking ? 0x202742 : 0x223868);
      skyUniforms.uMid.value.setHex(sulking ? 0x5c5373 : 0x876285);
      skyUniforms.uHorizon.value.setHex(sulking ? 0xd99e77 : 0xf4a86e);
      skyUniforms.uSunDir.value.set(-48, 9.5, 62).normalize();
      skyUniforms.uSunCol.value.setHex(0xffbe76);
      scene.background.setHex(0x64556d);
      scene.fog.color.setHex(0xdf9f74);
      sunLight.color.setHex(0xffb46e);
      sunLight.intensity = 3.8;
      sunLight.position.set(-40.0, 9.8, 52.0);
      hemiLight.color.setHex(0xf6b98e);
      hemiLight.groundColor.setHex(0x1f283b);
      hemiLight.intensity = 0.62;
      lintelCoveLight.intensity = 1.65;
      sconcePortLight.intensity = 1.35;
      sconceStbdLight.intensity = 1.35;
      barGlowLight.intensity = 1.55;
      water.setAtmosphere({
        deepColor: 0x0d2b4e,
        shallowColor: 0x1b5c61,
        skyZenithColor: 0x223868,
        skyHorizonColor: 0xf4a86e,
        sunDir: skyUniforms.uSunDir.value,
        sunColor: 0xffc67d,
        wind: 0.45,
      });
    } else {
      skyUniforms.uZenith.value.setHex(sulking ? 0x163254 : 0x164a8d);
      skyUniforms.uMid.value.setHex(sulking ? 0x3b638f : 0x478ad1);
      skyUniforms.uHorizon.value.setHex(sulking ? 0xa5bacf : 0xf2ddc0);
      skyUniforms.uSunDir.value.set(27.0, 22.8, -26.5).normalize();
      skyUniforms.uSunCol.value.setHex(0xfff0cc);
      scene.background.setHex(sulking ? 0x2c4b6e : 0x5c96cc);
      scene.fog.color.setHex(sulking ? 0x456689 : 0x9bc4e8);
      sunLight.color.setHex(0xffebd2);
      sunLight.intensity = 4.45;
      sunLight.position.set(27.0, 22.8, -26.5);
      hemiLight.color.setHex(0xd9e8f8);
      hemiLight.groundColor.setHex(0x26435a);
      hemiLight.intensity = 0.56;
      lintelCoveLight.intensity = 1.05;
      sconcePortLight.intensity = 0.85;
      sconceStbdLight.intensity = 0.85;
      barGlowLight.intensity = 1.0;
      water.setAtmosphere({
        deepColor: 0x0a3866,
        shallowColor: 0x1b8278,
        skyZenithColor: sulking ? 0x163254 : 0x164a8d,
        skyHorizonColor: sulking ? 0xa5bacf : 0x8cc2eb,
        sunDir: skyUniforms.uSunDir.value,
        sunColor: 0xffebc2,
        wind: 0.62,
      });
    }
    if (moodBtn) {
      moodBtn.textContent = isSunset ? "☀️ 晴海" : "🌅 晚航";
      moodBtn.classList.toggle("is-active", isSunset);
    }
  };
  const toggleSunsetMood = () => {
    sunsetMode = !sunsetMode;
    applyAtmosphereMood();
    return sunsetMode;
  };
  moodBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    sfx.playTap();
    feedback("small", e.clientX, e.clientY);
    toggleSunsetMood();
  });

  resetBtn?.addEventListener("click", () => {
    if (droneState) return;
    sfx.playTap();
    switchCameraPreset(activeCamId || "overview", { durationSec: 1.8 });
  });

  // Keyholder portal menu
  const setKeyholderOpen = (open) => {
    keyholderEl?.classList.toggle("is-open", open);
    keyholderBtn?.setAttribute("aria-expanded", open ? "true" : "false");
  };
  keyholderBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    sfx.playTap();
    setKeyholderOpen(!keyholderEl?.classList.contains("is-open"));
  });
  const onDocClick = (e) => {
    if (keyholderEl && !keyholderEl.contains(e.target)) setKeyholderOpen(false);
  };
  document.addEventListener("click", onDocClick);
  cleanups.push(() => document.removeEventListener("click", onDocClick));

  const PORTALS = [
    { id: "home", title: "返回 · 阳光客厅", sub: "回到上次宅邸机位", code: "HOME·00", fn: () => opts.onBackToHub?.() },
    { id: "street", title: "前往 · 海岸烘焙室", sub: "山羊奶微泡吧台", code: "OUT·01", fn: () => opts.onTeleportStreet?.() },
    { id: "warehouse", title: "前往 · ELOWEN 市集", sub: "冷柜鲜食买手店", code: "ELW·02", fn: () => opts.onTeleportWarehouse?.() },
  ];
  PORTALS.forEach((p) => {
    if (!keyholderTray) return;
    const item = document.createElement("button");
    item.type = "button";
    item.className = "keyholder-item";
    item.setAttribute("data-spot", p.id);
    item.innerHTML = `
      <span class="stub-main">
        <span class="stub-icon">${WORDLESS_CREST_SVG}</span>
        <span class="stub-text">
          <span class="stub-title">${p.title}</span>
          <span class="stub-sub">${p.sub}</span>
        </span>
      </span>
      <span class="stub-code">${p.code}</span>
    `;
    item.addEventListener("click", (e) => {
      e.stopPropagation();
      setKeyholderOpen(false);
      sfx.playTap();
      p.fn();
    });
    keyholderTray.appendChild(item);
  });

  // Ground click raycasting to walk Bruce along berth or yacht deck
  const clickRay = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  let pointerDownXY = null;
  canvas.addEventListener("pointerdown", (e) => {
    pointerDownXY = [e.clientX, e.clientY];
  });
  canvas.addEventListener("pointerup", (e) => {
    if (!pointerDownXY || droneState) return;
    const moved = Math.hypot(e.clientX - pointerDownXY[0], e.clientY - pointerDownXY[1]);
    pointerDownXY = null;
    if (moved > 8) return;
    const rect = canvas.getBoundingClientRect();
    ndc.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    ndc.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    clickRay.setFromCamera(ndc, camera);
    const hits = clickRay.intersectObjects(walkMeshes, false);
    if (hits.length > 0) {
      const hit = hits[0];
      const onDeck = yachtSurfaceMeshes.includes(hit.object);
      bruce.setResting(null);
      setBruceParent(onDeck);
      const localPt = onDeck ? yachtRoot.worldToLocal(hit.point.clone()) : hit.point.clone();
      bruce.root.position.y = localPt.y;
      bruce.walkTo(localPt.x, localPt.z);
    }
  });

  // Floating AI chat bar
  cleanups.push(
    mountBruceChatBar({
      stageEl,
      toggleBtn: container.querySelector("#hub3d-btn-chat"),
      getContext: () => ({
        owner: opts.player?.owner || "Alex",
        nickname: opts.player?.nickname || "新邻居",
        happiness,
        sulking,
        scene: "yacht_marina",
      }),
      onAiResponse(res, showDelta) {
        if (res?.reply) sayBruce(res.reply, 4600, "BRUCE · 海风回话");
        if (res?.action) bruce.playAction(res.action);
        if (res?.sincerityDelta) {
          opts.onSincerityDelta?.(res.sincerityDelta).then?.((applied) => applied && showDelta?.(applied));
        }
      },
    }),
  );

  // Load 4 modular GLBs (from preloaded ArrayBuffers if ready, or fresh fetch)
  const loader = new GLTFLoader();
  async function loadAssetPart(key) {
    const buffers = await preloadYachtAssets();
    const buf = buffers[key];
    const baseHref = new URL(".", new URL(ASSET_URLS[key], window.location.href)).href;
    const gltf = await loader.parseAsync(buf.slice(0), baseHref);
    return { gltf, bytes: buf.byteLength };
  }

  const assetsReady = Promise.all([
    loadAssetPart("berth"),
    loadAssetPart("hull_rig"),
    loadAssetPart("deck_salon"),
    loadAssetPart("furniture_props"),
  ])
    .then(([berthRes, hullRes, salonRes, propsRes]) => {
      if (destroyed) return false;
      const parts = {
        berth: berthRes,
        hull_rig: hullRes,
        deck_salon: salonRes,
        furniture_props: propsRes,
      };
      for (const [key, res] of Object.entries(parts)) {
        const sc = res.gltf.scene;
        loadedParts[key] = sc;
        let tris = 0;
        const box = new THREE.Box3().setFromObject(sc);
        sc.traverse((obj) => {
          if (obj.isMesh) {
            const isGlass = /Glass/i.test(obj.name) || /Glass/i.test(obj.material?.name || "") || obj.material?.transmission > 0.1;
            obj.castShadow = !isGlass;
            obj.receiveShadow = !isGlass;
            const gIdx = obj.geometry?.index;
            tris += gIdx ? gIdx.count / 3 : (obj.geometry?.attributes?.position?.count || 0) / 3;
            if (key === "berth") walkMeshes.push(obj);
            else {
              yachtSurfaceMeshes.push(obj);
              walkMeshes.push(obj);
            }
          } else if (obj.name && obj.name in anchors) {
            anchors[obj.name] = obj.position.clone();
          }
        });
        assetReports[key] = {
          bytes: res.bytes,
          triangles: Math.round(tris),
          aabb: [box.min.toArray().map((n) => +n.toFixed(3)), box.max.toArray().map((n) => +n.toFixed(3))],
        };
      }

      berthRoot.add(parts.berth.gltf.scene);
      yachtRoot.add(parts.hull_rig.gltf.scene, parts.deck_salon.gltf.scene, parts.furniture_props.gltf.scene);
      yachtRoot.updateMatrixWorld(true);
      const evReport = measureGreyCardEV();
      stageEl.dataset.yachtDiag = JSON.stringify({
        assetsLoaded: Object.keys(assetReports),
        assetReports,
        ev: evReport,
        mirrorSize: water.mirrorSize,
      });
      loadingEl.classList.add("is-hidden");

      if (opts.autoStartIntro) {
        startDroneReel("both", { fadeOnFinish: true });
      } else {
        applyPoseImmediate(adaptPoseForAspect(YACHT_CAM_PRESETS.overview.camPos, YACHT_CAM_PRESETS.overview.lookAt, 43, currentAspect()));
        sayBruce(sulking ? "idle_sulk" : "idle_happy", 4200);
      }
      return true;
    })
    .catch((err) => {
      console.error("Yacht GLB load error:", err);
      loadingEl.textContent = "游艇泊位资源加载失败，请重试";
      return false;
    });

  // Diagnostic API for automated EV, piling reflection, and anchor QA
  function measureGreyCardEV() {
    const g = new THREE.PlaneGeometry(0.45, 0.45);
    const m = new THREE.MeshStandardMaterial({ color: 0x737373, roughness: 0.85, metalness: 0.0 });
    const card = new THREE.Mesh(g, m);
    scene.add(card);
    const rt = new THREE.WebGLRenderTarget(16, 16, { type: THREE.FloatType });
    const px = new Float32Array(16 * 16 * 4);
    const probeCam = new THREE.PerspectiveCamera(24, 1, 0.1, 20);
    const readCardLuma = (cardPos, camPos) => {
      card.position.copy(cardPos);
      card.lookAt(camPos);
      probeCam.position.copy(camPos);
      probeCam.lookAt(cardPos);
      const oldRT = renderer.getRenderTarget();
      renderer.setRenderTarget(rt);
      renderer.render(scene, probeCam);
      renderer.readRenderTargetPixels(rt, 0, 0, 16, 16, px);
      renderer.setRenderTarget(oldRT);
      let sum = 0;
      for (let i = 0; i < px.length; i += 4) {
        sum += 0.2126 * px[i] + 0.7152 * px[i + 1] + 0.0722 * px[i + 2];
      }
      return Math.max(1e-4, sum / (16 * 16));
    };
    const lExt = readCardLuma(new THREE.Vector3(1.1, 1.65, -5.2), new THREE.Vector3(2.2, 2.2, -6.5));
    const lInt = readCardLuma(new THREE.Vector3(0.0, 2.48, 0.55), new THREE.Vector3(0.0, 2.52, -1.15));
    scene.remove(card);
    g.dispose();
    m.dispose();
    rt.dispose();
    return { extLuma: +lExt.toFixed(4), intLuma: +lInt.toFixed(4), deltaEV: +Math.log2(lExt / lInt).toFixed(2) };
  }

  let prevNow = performance.now();
  let simClock = 0;
  const gwWorldDock = new THREE.Vector3();
  const gwWorldYacht = new THREE.Vector3();
  const tmpEuler = new THREE.Euler(0, 0, 0, "YXZ");

  const prevWaterRender = null;
  let luckyToastTimer = null;
  const meteorCtrl = createLuckyMeteorController(scene, {
    skyZ: -86,
    isPaused: () => Boolean(droneState) || !loadingEl.classList.contains("is-hidden"),
    getContext: () => ({ sulking, zone: "yacht", dusk: false }),
    async onTrigger({ bonus }) {
      sfx.playConciergeBell();
      later(() => sfx.playSuccess(), 160);
      if (!sulking) bruce.triggerHappyHop();
      sayBruce(`流星划过柚木泊位上空！布鲁斯摇着尾巴许下心愿，幸运指数 +${bonus}。`, 4600, "LUCKY · 海上流星");
      const applied = await opts.onLuckyBonus?.(bonus);
      const shownBonus = applied?.bonus ?? bonus;
      if (luckySubEl) {
        luckySubEl.textContent = applied?.newScore
          ? `布鲁斯摇尾许愿 · 幸福指数 +${shownBonus}（当前 ${applied.newScore}）`
          : `布鲁斯摇尾许愿 · 幸福指数 +${shownBonus}`;
      }
      if (luckyToastEl) {
        luckyToastEl.classList.add("is-visible");
        if (luckyToastTimer) clearTimeout(luckyToastTimer);
        luckyToastTimer = later(() => luckyToastEl.classList.remove("is-visible"), 4600);
      }
    },
  });

  function tick(nowMs) {
    if (destroyed) return;
    const dt = Math.min(0.05, Math.max(0.001, (nowMs - prevNow) / 1000));
    prevNow = nowMs;
    meteorCtrl.update(dt);

    if (!waterPaused) {
      simClock += dt;
      pausedWaterTime = simClock;
    }
    const wTime = waterPaused ? pausedWaterTime : simClock;
    water.setTime(wTime);

    // 1. Update Yacht buoyancy FIRST
    const pose = water.computeYachtBuoyancyPose(wTime);
    yachtRoot.position.y = pose.y;
    tmpEuler.set(pose.pitch, 0, pose.roll, "YXZ");
    yachtRoot.quaternion.setFromEuler(tmpEuler);
    yachtRoot.updateMatrixWorld(true);

    // 2. Update articulated gangway between fixed berth dock & floating yacht side after matrix update
    gwWorldDock.copy(anchors.gangway_dock);
    gwWorldYacht.copy(anchors.gangway_yacht).applyMatrix4(yachtRoot.matrixWorld);
    gangwayGroup.position.copy(gwWorldDock);
    const dx = gwWorldYacht.x - gwWorldDock.x;
    const dy = gwWorldYacht.y - gwWorldDock.y;
    const dz = gwWorldYacht.z - gwWorldDock.z;
    const horizLen = Math.max(0.25, Math.hypot(dx, dz));
    gangwayGroup.scale.set(horizLen, 1, 1);
    gangwayGroup.rotation.set(0, -Math.atan2(dz, dx), Math.atan2(dy, horizLen), "YXZ");

    // 3. Coastal gulls & Bruce Bow Wind tracking
    gulls.forEach((g) => {
      const a = wTime * 0.48 + g.phase;
      g.group.position.set(Math.sin(a) * g.r, g.baseY + Math.sin(a * 2.1) * 0.35, g.baseZ + Math.cos(a) * g.r * 0.65);
      g.group.rotation.y = a + Math.PI * 0.5;
      const flap = Math.sin(wTime * 6.5 + g.phase) * 0.34;
      g.lWing.rotation.z = flap;
      g.rWing.rotation.z = -flap;
    });

    skyUniforms.uTime.value = simClock;
    lhBeacon.intensity = (sunsetMode ? 3.8 : 2.0) + Math.sin(simClock * 2.2) * 0.9;
    distantSails.forEach((s, idx) => {
      const span = ((simClock * s.speed + idx * 14) % 44) - 22;
      s.boat.position.x = s.originX + span * s.dir;
      s.boat.position.y = Math.sin(simClock * 1.4 + idx) * 0.08;
      s.boat.rotation.z = Math.sin(simClock * 1.1 + idx) * 0.04;
    });

    if (beatState?.id === "yacht_bow_wind") {
      beatState.elapsed += dt;
      // Lift nose into wind, then smoothly pan head 22 deg tracking circling gull
      const u = Math.min(1, beatState.elapsed / 3.2);
      const trackYaw = Math.sin(u * Math.PI * 1.4) * (22 / 26); // lookAtNormalized maps *0.45 rad (~25.8 deg)
      bruce.lookAtNormalized(trackYaw, u < 0.35 ? -0.9 : -0.65);
      if (beatState.elapsed >= beatState.timer) {
        bruce.lookAtNormalized(0, 0);
        beatState = null;
      }
    } else if (beatState?.id === "yacht_shade_mat") {
      beatState.timer -= dt;
      if (beatState.timer <= 0) {
        beatState = null;
      }
    }

    bruce.update(dt, simClock);

    // 4. Drone reels vs playable transition vs OrbitControls
    if (droneState) {
      const trackKey = droneState.queue[droneState.idx];
      const track = YACHT_DRONE_TRACKS[trackKey];
      const sampler = droneSamplers[trackKey];
      droneState.t += dt * droneSpeed;
      const tNorm = Math.min(1, droneState.t / sampler.duration);
      const sample = sampler.sample(tNorm, currentAspect());
      camera.position.copy(sample.pos);
      camera.fov = sample.fov;
      camera.updateProjectionMatrix();
      camera.up.set(0, 1, 0);
      camera.lookAt(sample.lookAt);
      controls.target.copy(sample.lookAt);

      if (droneState.t >= sampler.duration) {
        droneState.idx += 1;
        if (droneState.idx < droneState.queue.length) {
          // Hard cut from Port to Starboard!
          droneState.t = 0;
          const nextTrack = YACHT_DRONE_TRACKS[droneState.queue[droneState.idx]];
          if (droneStatusTxt && nextTrack) droneStatusTxt.textContent = `${nextTrack.label} · 航拍中`;
        } else {
          finishDroneSequence({ fadeToDock: droneState.fadeOnFinish, holdFinalPose: sample });
        }
      }
    } else if (camTransition) {
      camTransition.elapsed += dt;
      const tNorm = Math.min(1, camTransition.elapsed / camTransition.spline.duration);
      const s = camTransition.spline.sample(tNorm);
      camera.position.copy(s.pos);
      camera.quaternion.copy(s.quat);
      camera.fov = s.fov;
      camera.updateProjectionMatrix();
      controls.target.copy(s.target);
      if (tNorm >= 1) {
        const done = camTransition.onDone;
        controls.target.copy(camTransition.endTarget);
        camTransition = null;
        controls.update();
        done?.();
      }
    } else {
      controls.update();
    }

    // Resize renderer cleanly
    const w = Math.max(1, stageEl.clientWidth);
    const h = Math.max(1, stageEl.clientHeight);
    if (canvas.width !== Math.floor(w * dpr) || canvas.height !== Math.floor(h * dpr)) {
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }

    renderer.render(scene, camera);

    if (typeof window !== "undefined") {
      window.__YACHT_DIAG__ = {
        scene: "bruce_day_sailer",
        assetsLoaded: Object.keys(assetReports),
        assetReports,
        anchors: Object.fromEntries(Object.entries(anchors).map(([k, v]) => [k, v.toArray().map((n) => +n.toFixed(3))])),
        activeCamId,
        camPos: camera.position.toArray().map((n) => +n.toFixed(3)),
        lookAt: controls.target.toArray().map((n) => +n.toFixed(3)),
        fov: +camera.fov.toFixed(2),
        dronePlaying: Boolean(droneState),
        droneTrack: droneState ? droneState.queue[droneState.idx] : null,
        waterPaused,
        sunsetMode,
        toggleSunset: () => toggleSunsetMood(),
        yachtPose: { y: +pose.y.toFixed(4), pitch: +pose.pitch.toFixed(4), roll: +pose.roll.toFixed(4) },
        bruceOnYacht,
        brucePos: bruce.root.position.toArray().map((n) => +n.toFixed(3)),
        bruceWorldPos: bruce.root.getWorldPosition(new THREE.Vector3()).toArray().map((n) => +n.toFixed(3)),
        pauseWater: (flag) => { waterPaused = Boolean(flag); },
        measureGreyCardEV,
        playDrone: (m, o) => startDroneReel(m, o),
        skipDrone: () => finishDroneSequence({ fadeToDock: true }),
        switchCam: (id) => switchCameraPreset(id),
        triggerBeat: (id) => triggerYachtBeat(id),
      };
    }

    rafId = requestAnimationFrame(tick);
  }

  sfx.setSceneAmbience("yacht", { sulking });
  rafId = requestAnimationFrame(tick);

  return {
    ready: assetsReady,
    switchCameraPreset,
    startDroneReel,
    skipDrone: () => finishDroneSequence({ fadeToDock: true }),
    setSulking(nextSulk) {
      sulking = Boolean(nextSulk);
      bruce.setMood(sulking ? "sulk" : "happy");
      applyAtmosphereMood();
      sfx.setSceneAmbience("yacht", { sulking });
    },
    setContext({ happiness: nextScore, content: nextContent }) {
      if (Number.isFinite(nextScore)) happiness = nextScore;
      if (nextContent) content = nextContent;
    },
    destroy() {
      if (destroyed) return;
      destroyed = true;
      sfx.clearSceneAmbience("yacht");
      document.body.classList.remove("is-hub3d-view", "is-hub3d-act");
      if (rafId) cancelAnimationFrame(rafId);
      timers.forEach((t) => clearTimeout(t));
      timers.clear();
      cleanups.forEach((fn) => fn());
      bruce.destroy();
      meteorCtrl.dispose();
      water.dispose();
      controls.dispose();
      disposables.forEach((d) => d?.dispose?.());
      scene.traverse((obj) => {
        if (obj.geometry) obj.geometry.dispose();
        const ms = Array.isArray(obj.material) ? obj.material : [obj.material];
        ms.forEach((m) => m?.dispose?.());
      });
      renderer.dispose();
      if (typeof window !== "undefined") delete window.__YACHT_DIAG__;
    },
  };
}

export const mountScene = mountYachtHub;
