import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { createLivingBruce } from "./bruceLiving.js";
import { sfx } from "../audio.js";
import { feedback } from "../juice.js";

const OVERVIEW_CAM = new THREE.Vector3(5.4, 6.2, 11.8);
const OVERVIEW_TARGET = new THREE.Vector3(0.4, 2.6, -2.8);

const ACTIVITY_DEFS = {
  home_brush: {
    id: "home_brush",
    title: "露台阳光顺毛",
    win: 11,
    fail: -13,
    swapProb: 0,
    camPos: new THREE.Vector3(2.4, 3.4, 8.2),
    camTarget: new THREE.Vector3(0.9, 2.05, 2.2),
  },
  home_rain_vinyl: {
    id: "home_rain_vinyl",
    title: "雨窗黑胶时光",
    win: 12,
    fail: -12,
    swapProb: 0,
    camPos: new THREE.Vector3(2.6, 4.4, 6.2),
    camTarget: new THREE.Vector3(-0.4, 2.6, -4.0),
  },
  home_hide_seek: {
    id: "home_hide_seek",
    title: "客厅抛球寻宝",
    win: 12,
    fail: -14,
    swapProb: 0.12,
    camPos: new THREE.Vector3(3.8, 4.8, 9.4),
    camTarget: new THREE.Vector3(0.9, 1.8, 1.0),
  },
};

const HOTSPOTS = [
  {
    id: "home_brush",
    kind: "act",
    title: "阳光顺毛",
    sub: "+11 分 · 丝毛护理",
    pos: [2.75, 2.7, 2.2],
    icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 19l11-11"/><path d="M13 5l6 6"/><path d="M11 7l5 5"/><path d="M9 9l5 5"/><path d="M18 3v2M21 6h-2"/></svg>`,
  },
  {
    id: "home_rain_vinyl",
    kind: "act",
    title: "雨窗黑胶",
    sub: "+12 分 · 33RPM",
    pos: [-3.4, 4.4, -7.8],
    icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.2"/><path d="M18 5l-3 5" stroke-linecap="round"/></svg>`,
  },
  {
    id: "home_hide_seek",
    kind: "act",
    title: "客厅抛球",
    sub: "+12 分 · 12% 换分",
    pos: [-2.2, 1.4, 2.4],
    icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/><path d="M6.5 7.5c3 3 3 6 0 9M17.5 7.5c-3 3-3 6 0 9"/></svg>`,
  },
  {
    id: "street",
    kind: "teleport",
    title: "出门 · 林荫小街",
    sub: "双幕剧场探索",
    code: "OUT·01",
    pos: [4.8, 3.8, -1.2],
    icon: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 10l2-5h12l2 5"/><path d="M5 10v9h14v-9"/><path d="M10 19v-5h4v5"/></svg>`,
  },
  {
    id: "warehouse",
    kind: "teleport",
    title: "传送 · 会员超市",
    sub: "二期冷柜试吃",
    code: "CLB·02",
    pos: [-5.6, 3.3, -2.2],
    icon: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="9" cy="19" r="1.5"/><circle cx="17" cy="19" r="1.5"/><path d="M3 5h3l2.2 10h9.8l2-7H7"/></svg>`,
  },
  {
    id: "global",
    kind: "teleport",
    title: "传送 · 环球旅行",
    sub: "北欧 / 海岸 / 游艇",
    code: "FLY·04",
    pos: [-4.2, 7.6, -6.5],
    icon: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 2l2.6 7.4L22 12l-7.4 2.6L12 22l-2.6-7.4L2 12l7.4-2.6z"/></svg>`,
  },
];

function pickRandom(arr, fallback = "") {
  if (!Array.isArray(arr) || !arr.length) return fallback;
  return arr[Math.floor(Math.random() * arr.length)];
}

const DEFAULT_HUB_COPY = {
  thought_bubbles: {
    idle_happy: [
      "地毯晒得好暖和，今天打算陪我玩哪一个？",
      "酒红丝巾刚整理好，随时准备出门巡街。",
      "听见我的小尾巴在扫地板了吗？",
    ],
    idle_sulk: [
      "哼，幸福指数跌破 80 了，我现在只认零食说话。",
      "把头扭过去十秒钟，除非拿牛肉干来哄我。",
    ],
    click_poke: [
      "干嘛戳我软乎乎的耳朵，顺毛要从头顶开始！",
      "嘿嘿，被你抓到一只刚晒暖的奶油腊肠犬。",
      "再来一下我就要原地起跳转圈圈了哦！",
    ],
    click_poke_sulk: [
      "别戳啦，冷战期的小狗很有原则的……除非加肉。",
      "尾巴才没有偷偷动一下，哼。",
    ],
    petting_bliss: [
      "就是这个力度，耳朵后面再多顺两下～",
      "呼噜呼噜，奶油长毛都要顺滑到反光啦。",
    ],
    ear_warn: [
      "哎呀太快了！飞机耳预警，快松手让我缓一秒！",
    ],
    rain_cozy: [
      "擦干小爪子裹进毛毯，听着雨声最舒服啦。",
      "黑胶唱片一转起来，整个客厅都是暖色调。",
    ],
    ball_excited: [
      "看我的短腿冲刺！这颗网球归我了！",
    ],
  },
  portal_hover: {
    street: "门外风好舒服，今天去街角巡视一圈吗？",
    warehouse: "听说大超市试吃区有三文鱼，带我坐购物车吧！",
    global: "相框里藏着好多远方，下一站想带我去哪里？",
  },
};

export function mountLivingRoomHub(container, opts = {}) {
  let sulking = Boolean(opts.sulking);
  let content = opts.content || {};
  let happiness = opts.happiness ?? 100;
  let hubCopy = DEFAULT_HUB_COPY;

  document.body.classList.add("is-hub3d-view");
  document.body.classList.remove("is-hub3d-act");

  fetch("./data/hub_deepseek.json")
    .then((r) => (r.ok ? r.json() : null))
    .then((json) => {
      if (!destroyed && json?.thought_bubbles) {
        hubCopy = json;
      }
    })
    .catch(() => {});

  let destroyed = false;
  let rafId = null;
  let activeActId = null;
  let actCleanup = null;
  let camTween = null;

  const timers = new Set();
  const cleanups = [];
  const particles = [];

  const later = (fn, ms) => {
    const id = setTimeout(() => {
      timers.delete(id);
      if (!destroyed) fn();
    }, ms);
    timers.add(id);
    return id;
  };

  container.innerHTML = `
    <div class="hub3d-wrap">
      <div class="hub3d-stage">
        <canvas class="hub3d-canvas"></canvas>
        <div class="hub3d-vignette ${sulking ? "is-sulk" : ""}"></div>
        <canvas class="hub3d-fx-canvas" aria-hidden="true"></canvas>
        <div class="hub3d-viewfinder" aria-hidden="true">
          <span class="vf-corner vf-tl"></span>
          <span class="vf-corner vf-tr"></span>
          <span class="vf-corner vf-bl"></span>
          <span class="vf-corner vf-br"></span>
          <span class="vf-stamp">35MM · BRUCE LOFT · F/2.0</span>
        </div>
        <div class="hub3d-pins"></div>
        <div class="hub3d-speech" aria-live="polite"></div>
        <button type="button" class="hub3d-reset-btn">⌖ 归中视角</button>

        <div class="hub3d-act-overlay">
          <div class="hub3d-act-top">
            <button type="button" class="hub3d-glass-pill" id="hub3d-btn-back">回到客厅全景</button>
            <button type="button" class="hub3d-glass-pill" id="hub3d-btn-auto">自动演示</button>
          </div>
          <div class="hub3d-act-prompt"></div>
          <div class="hub3d-act-body"></div>
        </div>

        <div class="hub3d-swap-banner">
          <div style="font-size:12px;letter-spacing:0.1em;color:#FFE7A8;margin-bottom:4px;">高位交换 · 幸运降临</div>
          <div class="hub3d-swap-num">100</div>
          <div class="hub3d-swap-msg" style="font-size:13.5px;margin-top:4px;"></div>
        </div>

        <section class="hub3d-settle" aria-live="polite">
          <div class="hub3d-settle-head">
            <span class="hub3d-settle-title" style="font-size:12px;color:rgba(255,244,218,0.8)"></span>
            <span class="hub3d-settle-delta"></span>
          </div>
          <p class="hub3d-settle-line"></p>
          <p class="hub3d-settle-status"></p>
          <div class="hub3d-settle-actions">
            <button type="button" class="th-btn-primary" id="hub3d-btn-replay">再来一次</button>
            <button type="button" class="th-btn-ghost" id="hub3d-btn-done">回到客厅全景</button>
          </div>
        </section>

        <div class="hub3d-loading">
          <span>正在走进布鲁斯的阳光客厅……</span>
        </div>
      </div>
      <p class="hub3d-hint">拖动画面环视 3D 客厅 · 点布鲁斯互动或点传送门去街区、超市与远方</p>
    </div>
  `;

  const stageEl = container.querySelector(".hub3d-stage");
  const canvas = container.querySelector(".hub3d-canvas");
  const fxCanvas = container.querySelector(".hub3d-fx-canvas");
  const vignetteEl = container.querySelector(".hub3d-vignette");
  const pinsLayer = container.querySelector(".hub3d-pins");
  const speechEl = container.querySelector(".hub3d-speech");
  const resetBtn = container.querySelector(".hub3d-reset-btn");
  const loadingEl = container.querySelector(".hub3d-loading");
  const actOverlay = container.querySelector(".hub3d-act-overlay");
  const actPromptEl = container.querySelector(".hub3d-act-prompt");
  const actBodyEl = container.querySelector(".hub3d-act-body");
  const btnActBack = container.querySelector("#hub3d-btn-back");
  const btnActAuto = container.querySelector("#hub3d-btn-auto");
  const settleEl = container.querySelector(".hub3d-settle");
  const btnReplay = container.querySelector("#hub3d-btn-replay");
  const btnDone = container.querySelector("#hub3d-btn-done");
  const swapBanner = container.querySelector(".hub3d-swap-banner");
  const swapNumEl = container.querySelector(".hub3d-swap-num");
  const swapMsgEl = container.querySelector(".hub3d-swap-msg");

  // Create Three.js renderer + scene + camera
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.12;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(sulking ? 0x263446 : 0xeaf0f6);

  // Procedural warm sunlit interior IBL so metallic wood/chrome never renders black
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene();
  envScene.background = new THREE.Color(0xf4efe6);
  const envRoom = new THREE.Mesh(
    new THREE.BoxGeometry(24, 16, 24),
    new THREE.MeshBasicMaterial({ color: 0xf0e9dc, side: THREE.BackSide }),
  );
  const envSky = new THREE.Mesh(
    new THREE.PlaneGeometry(18, 12),
    new THREE.MeshBasicMaterial({ color: 0xdcedff }),
  );
  envSky.position.set(0, 4, -11.5);
  envScene.add(envRoom, envSky);
  const envRT = pmrem.fromScene(envScene, 0.04);
  scene.environment = envRT.texture;
  pmrem.dispose();
  envRoom.geometry.dispose();
  envRoom.material.dispose();
  envSky.geometry.dispose();
  envSky.material.dispose();

  // Exterior sky backdrop tucked right behind the window mullions (z = -19.80) and in front of backing wall (-20.11)
  const skyPlaneGeo = new THREE.PlaneGeometry(16.6, 17.0);
  const skyPlaneMat = new THREE.MeshBasicMaterial({ color: sulking ? 0x35495e : 0xe4f1fc });
  const skyPlane = new THREE.Mesh(skyPlaneGeo, skyPlaneMat);
  skyPlane.position.set(2.35, 9.75, -19.92);
  scene.add(skyPlane);

  const camera = new THREE.PerspectiveCamera(48, 16 / 10, 0.2, 160);
  camera.position.copy(OVERVIEW_CAM);

  const controls = new OrbitControls(camera, canvas);
  controls.target.copy(OVERVIEW_TARGET);
  controls.enableDamping = true;
  controls.dampingFactor = 0.07;
  controls.enablePan = false;
  controls.minDistance = 5.5;
  controls.maxDistance = 16.5;
  controls.minPolarAngle = 0.78;
  controls.maxPolarAngle = 1.48;
  controls.minAzimuthAngle = -1.05;
  controls.maxAzimuthAngle = 1.05;
  controls.update();

  // Warm sunlit interior lighting
  const hemiLight = new THREE.HemisphereLight(0xfff9f0, 0xd9d0c5, 1.45);
  scene.add(hemiLight);

  const ambientLight = new THREE.AmbientLight(0xfffaf2, 0.75);
  scene.add(ambientLight);

  const sunLight = new THREE.DirectionalLight(0xffe7bf, 1.75);
  sunLight.position.set(5, 17, -17);
  sunLight.target.position.set(0, 1, -4);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.set(1024, 1024);
  sunLight.shadow.camera.near = 2;
  sunLight.shadow.camera.far = 45;
  sunLight.shadow.camera.left = -16;
  sunLight.shadow.camera.right = 16;
  sunLight.shadow.camera.top = 16;
  sunLight.shadow.camera.bottom = -16;
  sunLight.shadow.bias = -0.0006;
  scene.add(sunLight, sunLight.target);

  const warmLampLight = new THREE.PointLight(0xffb969, 0.0, 22, 1.4);
  warmLampLight.position.set(-4.5, 4.8, -10.5);
  scene.add(warmLampLight);

  // Subtle floating sunlit dust motes
  const moteCount = 36;
  const motePos = new Float32Array(moteCount * 3);
  for (let i = 0; i < moteCount; i++) {
    motePos[i * 3] = -8 + (i * 1.73 % 18);
    motePos[i * 3 + 1] = 1.5 + (i * 2.11 % 8);
    motePos[i * 3 + 2] = -14 + (i * 1.97 % 16);
  }
  const moteGeo = new THREE.BufferGeometry();
  moteGeo.setAttribute("position", new THREE.BufferAttribute(motePos, 3));
  const moteMat = new THREE.PointsMaterial({
    color: 0xfff3cf,
    size: 0.14,
    transparent: true,
    opacity: 0.55,
    depthWrite: false,
  });
  const motePoints = new THREE.Points(moteGeo, moteMat);
  scene.add(motePoints);

  // Rain streaks near window (for sulking or rainVinyl)
  const rainCount = 80;
  const rainPos = new Float32Array(rainCount * 3);
  for (let i = 0; i < rainCount; i++) {
    rainPos[i * 3] = -10 + ((i * 2.31) % 20);
    rainPos[i * 3 + 1] = 1.5 + ((i * 3.17) % 16);
    rainPos[i * 3 + 2] = -18.5 + ((i * 0.43) % 2.2);
  }
  const rainGeo = new THREE.BufferGeometry();
  rainGeo.setAttribute("position", new THREE.BufferAttribute(rainPos, 3));
  const rainMat = new THREE.PointsMaterial({
    color: 0xbcd8f8,
    size: 0.16,
    transparent: true,
    opacity: 0.68,
    depthWrite: false,
  });
  const rainPoints = new THREE.Points(rainGeo, rainMat);
  rainPoints.visible = sulking;
  scene.add(rainPoints);

  // 3D Tennis ball for fetch activity
  const ballGeo = new THREE.SphereGeometry(0.38, 24, 18);
  const ballMat = new THREE.MeshStandardMaterial({ color: 0xd9ef42, roughness: 0.72, metalness: 0.0 });
  const tennisBall = new THREE.Mesh(ballGeo, ballMat);
  tennisBall.castShadow = true;
  tennisBall.visible = false;
  scene.add(tennisBall);

  // 3D Golden swap halo rings around Bruce
  const swapRingsGroup = new THREE.Group();
  swapRingsGroup.position.set(0.9, 1.9, 2.2);
  swapRingsGroup.visible = false;
  const swapRingGeos = [];
  const swapRingMats = [];
  for (let i = 0; i < 4; i++) {
    const rg = new THREE.TorusGeometry(1.6 + i * 0.34, 0.04, 10, 64);
    const rm = new THREE.MeshBasicMaterial({ color: 0xf7d788, transparent: true, opacity: 0.75 });
    const mesh = new THREE.Mesh(rg, rm);
    mesh.rotation.set(Math.PI * 0.42 + i * 0.3, i * 0.6, 0);
    swapRingsGroup.add(mesh);
    swapRingGeos.push(rg);
    swapRingMats.push(rm);
  }
  scene.add(swapRingsGroup);

  // Living Bruce on the clear sunlit foreground well in front of the coffee table
  const bruce = createLivingBruce({ modelUrl: "./assets/models/bruce.glb", height: 2.55 });
  bruce.root.position.set(0.9, 0.835, 2.2);
  bruce.root.rotation.y = -0.22;
  bruce.setMood(sulking ? "sulk" : "happy");
  scene.add(bruce.root);

  // Load living room GLB
  let roomRoot = null;
  const gltfLoader = new GLTFLoader();
  const roomReady = new Promise((resolve) => {
    gltfLoader.load(
      "./assets/models/living_room.glb",
      (gltf) => {
        if (destroyed) return;
        roomRoot = gltf.scene;
        roomRoot.traverse((obj) => {
          if (obj.isMesh) {
            obj.castShadow = true;
            obj.receiveShadow = true;
            const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
            mats.forEach((m) => {
              if (!m) return;
              if (m.map) m.map.colorSpace = THREE.SRGBColorSpace;
              if (m.emissiveMap) m.emissiveMap.colorSpace = THREE.SRGBColorSpace;
              // Soften mirror-metallic dark floor material into warm architectural oak/stone
              if (m.name === "material" || (!m.map && m.metalness > 0.7)) {
                m.metalness = 0.16;
                m.roughness = 0.46;
                m.color.lerp(new THREE.Color(0xbdb1a2), 0.52);
              }
              m.needsUpdate = true;
            });
          }
        });
        scene.add(roomRoot);
        resolve(true);
      },
      undefined,
      (err) => {
        console.warn("living_room.glb load error:", err);
        resolve(false);
      },
    );
  });

  Promise.all([roomReady, bruce.ready]).then(() => {
    if (!destroyed) {
      loadingEl.classList.add("is-hidden");
      later(() => {
        if (!activeActId) sayBruce(sulking ? "idle_sulk" : "idle_happy", 4400);
      }, 900);
    }
  });

  let speechTimer = null;
  let lastSpeechText = "";
  function sayBruce(categoryOrText, durationMs = 3800) {
    if (!speechEl || destroyed) return;
    const pool = hubCopy?.thought_bubbles?.[categoryOrText];
    let text = "";
    if (Array.isArray(pool) && pool.length) {
      text = pickRandom(pool, "");
      if (text === lastSpeechText && pool.length > 1) {
        const idx = pool.indexOf(text);
        text = pool[(idx + 1) % pool.length];
      }
    } else {
      text = String(categoryOrText || "");
    }
    if (!text) return;
    lastSpeechText = text;
    speechEl.textContent = text;
    speechEl.classList.toggle("is-sulk", Boolean(sulking));
    speechEl.classList.add("is-visible");
    if (speechTimer) {
      clearTimeout(speechTimer);
      timers.delete(speechTimer);
    }
    speechTimer = later(() => {
      speechEl.classList.remove("is-visible");
      speechTimer = null;
    }, durationMs);
  }

  const idleTimerId = setInterval(() => {
    if (!destroyed && !activeActId && loadingEl.classList.contains("is-hidden")) {
      sayBruce(sulking ? "idle_sulk" : "idle_happy", 5200);
    }
  }, 7000);
  cleanups.push(() => clearInterval(idleTimerId));

  // 3D hotspot artifacts (charms & boarding stubs)
  const pinItems = HOTSPOTS.map((spot) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `hub3d-pin ${spot.kind === "teleport" ? "hub3d-stub" : "hub3d-charm"}`;
    btn.setAttribute("data-spot", spot.id);
    if (spot.kind === "teleport") {
      btn.innerHTML = `
        <span class="stub-main">
          <span class="stub-icon">${spot.icon}</span>
          <span class="stub-text">
            <span class="stub-title">${spot.title}</span>
            <span class="stub-sub">${spot.sub}</span>
          </span>
        </span>
        <span class="stub-code">${spot.code}</span>
      `;
    } else {
      btn.innerHTML = `
        <span class="charm-eyelet"></span>
        <span class="charm-icon">${spot.icon}</span>
        <span class="charm-body">
          <span class="charm-title">${spot.title}</span>
          <span class="charm-sub">${spot.sub}</span>
        </span>
      `;
    }
    pinsLayer.appendChild(btn);
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      feedback("small", e.clientX, e.clientY);
      sfx.playTap();
      handleHotspotClick(spot);
    });
    if (spot.kind === "teleport") {
      btn.addEventListener("pointerenter", () => {
        const hoverLine = hubCopy?.portal_hover?.[spot.id];
        if (hoverLine && !activeActId) sayBruce(hoverLine, 3400);
      });
    }
    return { spot, btn, world: new THREE.Vector3(...spot.pos) };
  });

  function applyAtmosphere(sulkMode, rainMode = false) {
    sulking = Boolean(sulkMode);
    vignetteEl.classList.toggle("is-sulk", sulking);
    rainPoints.visible = sulking || rainMode;
    motePoints.visible = !sulking && !rainMode;

    if (sulking) {
      scene.background.setHex(0x283546);
      skyPlaneMat.color.setHex(0x35495e);
      hemiLight.color.setHex(0x9ab4d2);
      hemiLight.groundColor.setHex(0x45505e);
      hemiLight.intensity = 0.95;
      sunLight.intensity = 0.3;
      ambientLight.intensity = 0.52;
      bruce.setMood("sulk");
    } else if (rainMode) {
      scene.background.setHex(0x3a4a5e);
      skyPlaneMat.color.setHex(0x4a5e75);
      hemiLight.color.setHex(0xc4d6ea);
      hemiLight.groundColor.setHex(0x6e6258);
      hemiLight.intensity = 1.1;
      sunLight.intensity = 0.55;
      ambientLight.intensity = 0.62;
    } else {
      scene.background.setHex(0xeaf0f6);
      skyPlaneMat.color.setHex(0xe4f1fc);
      hemiLight.color.setHex(0xfff9f0);
      hemiLight.groundColor.setHex(0xd9d0c5);
      hemiLight.intensity = 1.45;
      sunLight.intensity = 1.75;
      ambientLight.intensity = 0.75;
      warmLampLight.intensity = 0.0;
      if (!activeActId) bruce.setMood("happy");
    }
    speechEl?.classList.toggle("is-sulk", sulking);

    pinItems.forEach(({ spot, btn }) => {
      if (spot.kind === "act") {
        const subEl = btn.querySelector(".charm-sub");
        if (subEl) subEl.textContent = sulking ? "先哄好布鲁斯" : spot.sub;
      }
    });
  }

  function flyCamera(toPos, toTarget, durationMs = 680, onDone = null) {
    camTween = {
      fromPos: camera.position.clone(),
      toPos: toPos.clone(),
      fromTarget: controls.target.clone(),
      toTarget: toTarget.clone(),
      start: performance.now(),
      duration: durationMs,
      onDone,
    };
  }

  resetBtn.addEventListener("click", () => {
    sfx.playTap();
    flyCamera(OVERVIEW_CAM, OVERVIEW_TARGET, 620);
  });

  function spawnFxParticles(x, y, kind = "gold", count = 10) {
    for (let i = 0; i < count; i++) {
      const a = Math.random() * Math.PI * 2;
      const spd = 40 + Math.random() * 100;
      particles.push({
        x,
        y,
        vx: Math.cos(a) * spd,
        vy: Math.sin(a) * spd - (kind === "note" ? 45 : 20),
        life: 0,
        maxLife: 0.55 + Math.random() * 0.4,
        r: kind === "warm" ? 5 + Math.random() * 5 : 2.5 + Math.random() * 3,
        kind,
      });
    }
  }

  function exitInRoomActivity() {
    actCleanup?.();
    actCleanup = null;
    activeActId = null;
    document.body.classList.remove("is-hub3d-act");
    tennisBall.visible = false;
    swapRingsGroup.visible = false;
    swapBanner.classList.remove("is-visible");
    settleEl.classList.remove("is-visible");
    vignetteEl.classList.remove("is-warn");
    actOverlay.classList.remove("is-active");
    actBodyEl.innerHTML = "";
    pinsLayer.classList.remove("is-hidden");
    resetBtn.style.display = "";
    controls.enabled = true;
    bruce.setPetting(0);
    applyAtmosphere(sulking, false);
    flyCamera(OVERVIEW_CAM, OVERVIEW_TARGET, 650);
  }

  btnActBack.addEventListener("click", () => {
    sfx.playTap();
    exitInRoomActivity();
  });

  btnDone.addEventListener("click", () => {
    sfx.playTap();
    if (sulking) {
      exitInRoomActivity();
      opts.onOpenShop?.();
    } else {
      exitInRoomActivity();
    }
  });

  let ballAnim = null;

  function startInRoomActivity(actId, autoplay = false) {
    const def = ACTIVITY_DEFS[actId];
    if (!def) return;

    actCleanup?.();
    activeActId = actId;
    document.body.classList.add("is-hub3d-act");
    if (speechTimer) {
      clearTimeout(speechTimer);
      timers.delete(speechTimer);
      speechTimer = null;
    }
    speechEl?.classList.remove("is-visible");
    controls.enabled = false;
    pinsLayer.classList.add("is-hidden");
    resetBtn.style.display = "none";
    settleEl.classList.remove("is-visible");
    swapBanner.classList.remove("is-visible");
    swapRingsGroup.visible = false;
    actBodyEl.innerHTML = "";
    btnActAuto.textContent = autoplay ? "手动玩" : "自动演示";

    applyAtmosphere(false, actId === "home_rain_vinyl");
    flyCamera(def.camPos, def.camTarget, 700, () => {
      if (!destroyed && activeActId === actId) {
        actOverlay.classList.add("is-active");
      }
    });

    let finished = false;
    const actTimers = new Set();
    const actListeners = [];

    const actLater = (fn, ms) => {
      const id = later(() => {
        actTimers.delete(id);
        if (!finished && activeActId === actId) fn();
      }, ms);
      actTimers.add(id);
      return id;
    };

    const listen = (el, ev, fn, o) => {
      el.addEventListener(ev, fn, o);
      actListeners.push(() => el.removeEventListener(ev, fn, o));
    };

    listen(btnActAuto, "click", () => {
      sfx.playTap();
      startInRoomActivity(actId, !autoplay);
    });

    // Phone temptation banner
    let phoneEl = null;
    let phoneCount = 0;
    const triggerPhone = (autoTap = false) => {
      if (finished || phoneCount >= 2 || phoneEl) return;
      phoneCount += 1;
      const note = pickRandom(content?.phone_notifications) || { app: "CHAT", text: "NEW MESSAGE · 99+" };
      const banner = document.createElement("button");
      banner.type = "button";
      banner.className = "hub3d-phone-banner";
      banner.innerHTML = `
        <span class="hub3d-phone-app"></span>
        <span class="hub3d-phone-body">
          <span class="hub3d-phone-title"></span>
          <span class="hub3d-phone-text"></span>
        </span>
      `;
      banner.querySelector(".hub3d-phone-app").textContent = String(note.app || "CHAT").slice(0, 4);
      banner.querySelector(".hub3d-phone-title").textContent = `${note.app || "CHAT"} · NOW`;
      banner.querySelector(".hub3d-phone-text").textContent = note.text || "NEW MESSAGE";
      actOverlay.appendChild(banner);
      phoneEl = banner;

      listen(banner, "click", (e) => {
        e.stopPropagation();
        sfx.playPhoneBuzz();
        conclude("phone_fail");
      });

      requestAnimationFrame(() => banner.classList.add("is-shown"));
      sfx.playPhoneBuzz();

      if (autoTap) {
        actLater(() => {
          sfx.playPhoneBuzz();
          conclude("phone_fail");
        }, 900);
        return;
      }

      actLater(() => {
        banner.classList.remove("is-shown");
        actLater(() => {
          banner.remove();
          if (phoneEl === banner) phoneEl = null;
        }, 340);
      }, 2500);
    };

    const conclude = async (outcome) => {
      if (finished) return;
      finished = true;
      actTimers.forEach((t) => clearTimeout(t));
      actTimers.clear();
      actListeners.forEach((fn) => fn());
      actListeners.length = 0;
      vignetteEl.classList.remove("is-warn");
      bruce.setPetting(0);
      if (phoneEl) {
        phoneEl.remove();
        phoneEl = null;
      }
      actBodyEl.innerHTML = "";
      actPromptEl.textContent = "";

      const isWin = outcome === "win";
      const delta = isWin ? def.win : def.fail;
      if (isWin) {
        sfx.playSuccess();
        bruce.setMood("excited");
        bruce.triggerHappyHop();
        const r = stageEl.getBoundingClientRect();
        spawnFxParticles(r.width * 0.5, r.height * 0.48, "gold", 22);
      } else {
        sfx.playFail();
        bruce.setMood("sulk");
      }

      const actCopy = content?.activities?.[actId] || {};
      const pool =
        outcome === "win"
          ? actCopy.win_lines
          : outcome === "phone_fail"
            ? actCopy.phone_fail_lines
            : actCopy.hazard_fail_lines;
      const summaryLine = pickRandom(
        pool,
        isWin ? "布鲁斯眯眼摇着尾巴，乖乖靠在你膝边。" : "布鲁斯耷拉着耳朵，默默躲回了角落。",
      );

      settleEl.querySelector(".hub3d-settle-title").textContent =
        outcome === "win" ? "陪伴成功" : outcome === "phone_fail" ? "被手机抢走了" : "踩到雷点了";
      const deltaEl = settleEl.querySelector(".hub3d-settle-delta");
      deltaEl.textContent = `${delta >= 0 ? "+" : ""}${delta}`;
      deltaEl.classList.toggle("is-neg", delta < 0);
      settleEl.querySelector(".hub3d-settle-line").textContent = summaryLine;
      const statusEl = settleEl.querySelector(".hub3d-settle-status");
      statusEl.textContent = "正在同步幸福指数……";

      const projected = Math.max(0, happiness + delta);
      btnReplay.hidden = projected < 80;
      btnDone.textContent = projected < 80 ? "去零食急救柜" : "回到客厅全景";
      settleEl.classList.add("is-visible");

      const triggerSwapCandidate = isWin && Math.random() < def.swapProb;
      try {
        const swap = await opts.onSettle?.({
          activityId: actId,
          title: def.title,
          outcome,
          delta,
          triggerSwapCandidate,
          summaryLine,
        });
        if (destroyed || activeActId !== actId) return;

        const finalScore = Number.isFinite(swap?.newScore) ? swap.newScore : opts.getHappiness?.() ?? projected;
        happiness = finalScore;
        sulking = finalScore < 80;
        btnReplay.hidden = sulking;

        if (sulking) {
          applyAtmosphere(true, false);
          statusEl.textContent = `幸福指数跌至 ${finalScore}（<80），布鲁斯进入冷战`;
          btnDone.textContent = "去零食急救柜";
        } else {
          statusEl.textContent = `当前幸福指数 · ${finalScore}`;
          btnDone.textContent = "回到客厅全景";
        }

        if (Number.isFinite(swap?.newScore)) {
          settleEl.classList.remove("is-visible");
          swapRingsGroup.visible = true;
          swapBanner.classList.add("is-visible");
          swapMsgEl.textContent = swap.topBonus
            ? "已经站在最高处，再送你 +6"
            : `这一束光来自 ${swap.targetNickname || "一位新朋友"}`;
          sfx.playSwapCelebration();

          const fromV = swap.oldScore ?? projected;
          const toV = swap.newScore;
          const t0 = performance.now();
          const rollStep = (now) => {
            if (destroyed || activeActId !== actId) return;
            const p = Math.min(1, (now - t0) / 1000);
            swapNumEl.textContent = String(Math.round(fromV + (toV - fromV) * (1 - Math.pow(1 - p, 3))));
            if (p < 1) requestAnimationFrame(rollStep);
          };
          requestAnimationFrame(rollStep);

          later(() => {
            if (destroyed || activeActId !== actId) return;
            swapBanner.classList.remove("is-visible");
            swapRingsGroup.visible = false;
            statusEl.textContent = `高位换分完成 · 当前幸福指数 ${swap.newScore}`;
            settleEl.classList.add("is-visible");
          }, 3200);
        }
      } catch (_) {
        if (!destroyed && activeActId === actId) {
          statusEl.textContent = "结算暂未同步，请稍后重试";
        }
      }
    };

    listen(btnReplay, "click", () => {
      if (sulking) return;
      sfx.playTap();
      startInRoomActivity(actId, false);
    });

    actLater(() => triggerPhone(false), 1800 + Math.random() * 1400);

    // Build specific in-room interaction
    if (actId === "home_brush") {
      actPromptEl.textContent = "在布鲁斯身上按住轻轻来回顺毛";
      actBodyEl.innerHTML = `
        <div class="hub3d-brush-zone"></div>
        <div class="hub3d-progress"><div class="hub3d-progress-fill"></div></div>
        <button type="button" class="hub3d-hazard-btn">DRYER · 吹风机</button>
      `;
      const zone = actBodyEl.querySelector(".hub3d-brush-zone");
      const fill = actBodyEl.querySelector(".hub3d-progress-fill");
      const dryer = actBodyEl.querySelector(".hub3d-hazard-btn");

      listen(dryer, "click", (e) => {
        e.stopPropagation();
        conclude("hazard_fail");
      });

      let progress = 0;
      const TARGET = 2000;
      let warning = false;
      let warnedOnce = false;
      let warnMove = 0;
      let dragging = false;
      let lastPos = null;
      let lastTapAt = 0;
      let blissStage = 0;

      const stroke = (dx, dy, cx, cy) => {
        const d = Math.hypot(dx, dy);
        if (d < 1) return;
        if (warning) {
          warnMove += d;
          if (warnMove > 65) conclude("hazard_fail");
          return;
        }
        progress = Math.min(TARGET, progress + d);
        fill.style.width = `${(progress / TARGET) * 100}%`;
        bruce.setPetting(1);
        bruce.setMood("excited");
        if (blissStage === 0 && progress >= TARGET * 0.14) {
          blissStage = 1;
          sayBruce("petting_bliss", 3000);
        } else if (blissStage === 1 && progress >= TARGET * 0.72) {
          blissStage = 2;
          sayBruce("petting_bliss", 3000);
        }
        const rect = stageEl.getBoundingClientRect();
        spawnFxParticles(cx - rect.left, cy - rect.top, "gold", 3);
        const now = performance.now();
        if (now - lastTapAt > 280) {
          lastTapAt = now;
          sfx.playTap();
        }
        if (!warnedOnce && progress >= TARGET * 0.42) {
          warnedOnce = true;
          warning = true;
          warnMove = 0;
          bruce.setMood("warn");
          sayBruce("ear_warn", 2600);
          vignetteEl.classList.add("is-warn");
          actPromptEl.textContent = "飞机耳预警！先松手等 1 秒";
          actLater(() => {
            warning = false;
            bruce.setMood("happy");
            vignetteEl.classList.remove("is-warn");
            actPromptEl.textContent = "布鲁斯放松了，继续顺毛";
          }, 1400);
        }
        if (progress >= TARGET) conclude("win");
      };

      listen(actOverlay, "pointerdown", (e) => {
        if (autoplay || e.target === dryer || e.target.closest(".hub3d-phone-banner") || e.target.closest(".hub3d-act-top")) return;
        const r = zone.getBoundingClientRect();
        if (e.clientX >= r.left - 40 && e.clientX <= r.right + 40 && e.clientY >= r.top - 40 && e.clientY <= r.bottom + 40) {
          dragging = true;
          lastPos = { x: e.clientX, y: e.clientY };
        }
      });
      listen(actOverlay, "pointermove", (e) => {
        if (autoplay || !dragging || !lastPos) return;
        stroke(e.clientX - lastPos.x, e.clientY - lastPos.y, e.clientX, e.clientY);
        lastPos = { x: e.clientX, y: e.clientY };
      });
      listen(window, "pointerup", () => {
        dragging = false;
        lastPos = null;
        bruce.setPetting(0);
      });

      if (autoplay) {
        const autoStep = () => {
          if (finished || activeActId !== actId) return;
          if (warning) {
            actLater(autoStep, 450);
            return;
          }
          const r = stageEl.getBoundingClientRect();
          stroke(440, 30, r.left + r.width * 0.5, r.top + r.height * 0.5);
          actLater(autoStep, 650);
        };
        actLater(autoStep, 750);
      }
    } else if (actId === "home_rain_vinyl") {
      actPromptEl.textContent = "按顺序安顿布鲁斯：毛巾擦爪 → 盖毛毯 → 放黑胶";
      actBodyEl.innerHTML = `
        <div class="hub3d-props-row">
          <button type="button" class="hub3d-prop-btn" data-prop="towel">TOWEL · 毛巾</button>
          <button type="button" class="hub3d-prop-btn" data-prop="blanket">BLANKET · 毛毯</button>
          <button type="button" class="hub3d-prop-btn" data-prop="vinyl">VINYL · 黑胶</button>
        </div>
      `;
      const order = ["towel", "blanket", "vinyl"];
      let step = 0;

      const handleProp = (prop, btn) => {
        if (finished || btn.classList.contains("is-done")) return;
        if (prop !== order[step]) {
          conclude("hazard_fail");
          return;
        }
        btn.classList.add("is-done");
        step += 1;
        sfx.playTap();
        warmLampLight.intensity = step * 1.4;
        bruce.triggerHappyHop();
        const r = stageEl.getBoundingClientRect();
        spawnFxParticles(r.width * 0.5, r.height * 0.52, step === 1 ? "water" : step === 2 ? "warm" : "note", 18);
        if (step <= 2) sayBruce("rain_cozy", 3000);
        if (step === 1) actPromptEl.textContent = "爪子擦干啦，披上毛毯暖一暖";
        else if (step === 2) actPromptEl.textContent = "最后点黑胶唱片放音乐";
        else actLater(() => conclude("win"), 600);
      };

      actBodyEl.querySelectorAll("[data-prop]").forEach((btn) => {
        listen(btn, "click", (e) => {
          e.stopPropagation();
          if (!autoplay) handleProp(btn.getAttribute("data-prop"), btn);
        });
      });

      if (autoplay) {
        order.forEach((p, idx) => {
          actLater(() => {
            const btn = actBodyEl.querySelector(`[data-prop="${p}"]`);
            if (btn) handleProp(p, btn);
          }, 900 + idx * 1000);
        });
      }
    } else if (actId === "home_hide_seek") {
      actPromptEl.textContent = "按住网球向上甩出！丢到客厅地板上";
      actBodyEl.innerHTML = `
        <div class="hub3d-ball-btn">BALL</div>
        <button type="button" class="hub3d-hazard-btn">SPEAKER · 低音炮</button>
      `;
      const ballBtn = actBodyEl.querySelector(".hub3d-ball-btn");
      const speakerBtn = actBodyEl.querySelector(".hub3d-hazard-btn");

      listen(speakerBtn, "click", (e) => {
        e.stopPropagation();
        conclude("hazard_fail");
      });

      let dragging = false;
      let startY = 0;
      let startT = 0;
      let thrown = false;

      const throwBall3D = () => {
        if (thrown) return;
        thrown = true;
        ballBtn.style.display = "none";
        sfx.playTap();
        tennisBall.visible = true;
        tennisBall.position.set(3.4, 2.3, 6.4);
        ballAnim = {
          vx: -1.1,
          vy: 5.0,
          vz: -2.0,
          active: true,
        };
        bruce.setMood("excited");
        bruce.triggerHappyHop();
        sayBruce("ball_excited", 3000);
        actPromptEl.textContent = "布鲁斯扑过去捡球啦…别点弹出手机";
        actLater(() => triggerPhone(false), 700);
        actLater(() => conclude("win"), 3000);
      };

      listen(ballBtn, "pointerdown", (e) => {
        if (autoplay || thrown) return;
        e.stopPropagation();
        dragging = true;
        startY = e.clientY;
        startT = performance.now();
      });
      listen(window, "pointerup", (e) => {
        if (!dragging || thrown) return;
        dragging = false;
        const dy = e.clientY - startY;
        const dt = Math.max(16, performance.now() - startT);
        if (-dy / dt > 0.5 || dy < -80) {
          throwBall3D();
        } else {
          actPromptEl.textContent = "再用力往上甩一点！";
        }
      });

      if (autoplay) {
        actLater(throwBall3D, 900);
      }
    }

    actCleanup = () => {
      finished = true;
      actTimers.forEach((t) => clearTimeout(t));
      actTimers.clear();
      actListeners.forEach((fn) => fn());
      actListeners.length = 0;
      ballAnim = null;
      tennisBall.visible = false;
    };
  }

  function handleHotspotClick(spot) {
    if (spot.kind === "act") {
      if (sulking) {
        opts.onOpenShop?.();
        return;
      }
      startInRoomActivity(spot.id, false);
      return;
    }

    if (spot.id === "street") {
      flyCamera(new THREE.Vector3(9.5, 6.2, 4.5), new THREE.Vector3(12.5, 5.5, 0.5), 520, () => {
        opts.onTeleportStreet?.();
      });
      return;
    }

    if (spot.id === "warehouse") {
      opts.onTeleportWarehouse?.();
      return;
    }

    if (spot.id === "global") {
      opts.onTeleportGlobal?.();
    }
  }

  // Pointer gaze tracking & raycast click on 3D Bruce
  const raycaster = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  let canvasDown = null;

  const onCanvasDown = (e) => {
    if (activeActId) return;
    canvasDown = { x: e.clientX, y: e.clientY };
  };
  const onCanvasClick = (e) => {
    if (activeActId) return;
    const dist = canvasDown ? Math.hypot(e.clientX - canvasDown.x, e.clientY - canvasDown.y) : 0;
    canvasDown = null;
    if (dist >= 10) return;

    const r = canvas.getBoundingClientRect();
    if (!r.width || !r.height) return;
    ndc.x = ((e.clientX - r.left) / r.width) * 2 - 1;
    ndc.y = -((e.clientY - r.top) / r.height) * 2 + 1;
    raycaster.setFromCamera(ndc, camera);
    const bruceGroup = bruce.root.children[0];
    if (!bruceGroup) return;
    bruce.root.updateMatrixWorld(true);
    const hits = raycaster.intersectObject(bruceGroup, true);
    if (hits.length > 0) {
      feedback("small", e.clientX, e.clientY);
      sfx.playTap();
      const stageRect = stageEl.getBoundingClientRect();
      spawnFxParticles(e.clientX - stageRect.left, e.clientY - stageRect.top, sulking ? "water" : "gold", 12);
      if (!sulking) bruce.triggerHappyHop();
      sayBruce(sulking ? "click_poke_sulk" : "click_poke", 4200);
    }
  };
  canvas.addEventListener("pointerdown", onCanvasDown);
  canvas.addEventListener("click", onCanvasClick);
  cleanups.push(() => {
    canvas.removeEventListener("pointerdown", onCanvasDown);
    canvas.removeEventListener("click", onCanvasClick);
  });

  const onPointerMove = (e) => {
    const r = stageEl.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const nx = ((e.clientX - r.left) / r.width - 0.5) * 2;
    const ny = ((e.clientY - r.top) / r.height - 0.5) * 2;
    bruce.lookAtNormalized(nx, ny);
  };
  stageEl.addEventListener("pointermove", onPointerMove);
  cleanups.push(() => stageEl.removeEventListener("pointermove", onPointerMove));

  // Main render loop
  let prevNow = performance.now();
  const projVec = new THREE.Vector3();
  const speechVec = new THREE.Vector3();
  const fxCtx = fxCanvas.getContext("2d");

  const tick = (now) => {
    if (destroyed) return;
    const dt = Math.min(0.05, (now - prevNow) / 1000);
    prevNow = now;
    const elapsed = now / 1000;

    // Resize renderer & fx canvas (+ adapt FOV on portrait screens so all 6 pins stay framed)
    const w = Math.max(300, stageEl.clientWidth);
    const h = Math.max(240, stageEl.clientHeight);
    const desiredFov = w < 640 ? 64 : 48;
    if (canvas.width !== Math.round(w * renderer.getPixelRatio()) || canvas.height !== Math.round(h * renderer.getPixelRatio()) || camera.fov !== desiredFov) {
      renderer.setSize(w, h, false);
      camera.fov = desiredFov;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (fxCanvas.width !== Math.round(w * dpr) || fxCanvas.height !== Math.round(h * dpr)) {
      fxCanvas.width = Math.round(w * dpr);
      fxCanvas.height = Math.round(h * dpr);
    }

    // Camera tween or clamped OrbitControls
    if (camTween) {
      const p = Math.min(1, (now - camTween.start) / camTween.duration);
      const eased = 1 - Math.pow(1 - p, 3);
      camera.position.lerpVectors(camTween.fromPos, camTween.toPos, eased);
      controls.target.lerpVectors(camTween.fromTarget, camTween.toTarget, eased);
      controls.update();
      if (p >= 1) {
        const cb = camTween.onDone;
        camTween = null;
        cb?.();
      }
    } else {
      controls.update();
      camera.position.x = THREE.MathUtils.clamp(camera.position.x, -12.5, 16.5);
      camera.position.y = THREE.MathUtils.clamp(camera.position.y, 2.6, 17.5);
      camera.position.z = THREE.MathUtils.clamp(camera.position.z, -14.5, 11.2);
    }

    // Dust motes / rain motion
    if (motePoints.visible) {
      const arr = moteGeo.attributes.position.array;
      for (let i = 0; i < moteCount; i++) {
        arr[i * 3 + 1] += dt * 0.28;
        if (arr[i * 3 + 1] > 10.5) arr[i * 3 + 1] = 1.5;
      }
      moteGeo.attributes.position.needsUpdate = true;
    }
    if (rainPoints.visible) {
      const arr = rainGeo.attributes.position.array;
      for (let i = 0; i < rainCount; i++) {
        arr[i * 3 + 1] -= dt * 11.0;
        if (arr[i * 3 + 1] < 1.2) arr[i * 3 + 1] = 17.0;
      }
      rainGeo.attributes.position.needsUpdate = true;
    }

    // 3D Tennis ball physics bounce on y=1.21
    if (ballAnim && ballAnim.active) {
      ballAnim.vy -= 14.0 * dt;
      tennisBall.position.x += ballAnim.vx * dt;
      tennisBall.position.y += ballAnim.vy * dt;
      tennisBall.position.z += ballAnim.vz * dt;
      if (tennisBall.position.y <= 1.21) {
        tennisBall.position.y = 1.21;
        ballAnim.vy = Math.abs(ballAnim.vy) * 0.56;
        ballAnim.vx *= 0.78;
        ballAnim.vz *= 0.78;
        if (ballAnim.vy < 0.35) ballAnim.active = false;
      }
    }

    if (swapRingsGroup.visible) {
      swapRingsGroup.rotation.y += dt * 1.4;
      swapRingsGroup.children.forEach((c, idx) => {
        c.rotation.z += dt * (0.6 + idx * 0.25);
      });
    }

    bruce.update(dt, elapsed);
    renderer.render(scene, camera);

    // Project Bruce speech bubble above head (clamped safely below HUD)
    const minPinTop = w < 640 ? 158 : 116;
    if (speechEl) {
      const hideForSettle = settleEl.classList.contains("is-visible") || swapBanner.classList.contains("is-visible");
      speechVec.set(bruce.root.position.x, bruce.root.position.y + 3.05, bruce.root.position.z).project(camera);
      if (hideForSettle || speechVec.z > 1 || speechVec.z < -1) {
        speechEl.style.display = "none";
      } else {
        const bx = (speechVec.x * 0.5 + 0.5) * w;
        const by = (-speechVec.y * 0.5 + 0.5) * h;
        const halfSpeechW = Math.max(96, (speechEl.offsetWidth || 220) * 0.5 + 12);
        speechEl.style.display = "";
        speechEl.style.left = `${THREE.MathUtils.clamp(bx, halfSpeechW, Math.max(halfSpeechW, w - halfSpeechW))}px`;
        speechEl.style.top = `${THREE.MathUtils.clamp(by, minPinTop + 26, h - 28)}px`;
      }
    }

    // Project 3D hotspots to 2D overlay (clamped safely away from floating HUD)
    if (!activeActId) {
      pinItems.forEach(({ world, btn }) => {
        projVec.copy(world).project(camera);
        if (projVec.z > 1 || projVec.z < -1) {
          btn.style.display = "none";
          return;
        }
        const sx = (projVec.x * 0.5 + 0.5) * w;
        const sy = (-projVec.y * 0.5 + 0.5) * h;
        if (sx < -60 || sx > w + 60 || sy < -40 || sy > h + 40) {
          btn.style.display = "none";
          return;
        }
        btn.style.display = "";
        const halfW = Math.max(52, (btn.offsetWidth || 120) * 0.5 + 12);
        btn.style.left = `${THREE.MathUtils.clamp(sx, halfW, Math.max(halfW, w - halfW))}px`;
        btn.style.top = `${THREE.MathUtils.clamp(sy, minPinTop, h - 54)}px`;
      });
    }

    // 2D particle overlay
    fxCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
    fxCtx.clearRect(0, 0, w, h);
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.life += dt;
      if (p.life >= p.maxLife) {
        particles.splice(i, 1);
        continue;
      }
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.vy += (p.kind === "water" ? 200 : p.kind === "note" ? -30 : 35) * dt;
      fxCtx.save();
      fxCtx.globalAlpha = 1 - p.life / p.maxLife;
      if (p.kind === "water") {
        fxCtx.fillStyle = "#B8E4FF";
        fxCtx.beginPath();
        fxCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        fxCtx.fill();
      } else if (p.kind === "note") {
        fxCtx.fillStyle = "#FFE5A3";
        fxCtx.font = "bold 16px sans-serif";
        fxCtx.fillText("♪", p.x, p.y);
      } else {
        fxCtx.fillStyle = "#FFE39C";
        fxCtx.beginPath();
        fxCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        fxCtx.fill();
      }
      fxCtx.restore();
    }

    rafId = requestAnimationFrame(tick);
  };

  rafId = requestAnimationFrame(tick);

  return {
    setSulking(nextSulk) {
      applyAtmosphere(nextSulk, activeActId === "home_rain_vinyl");
    },
    setContext({ happiness: nextScore, content: nextContent }) {
      if (Number.isFinite(nextScore)) happiness = nextScore;
      if (nextContent) content = nextContent;
      if (!activeActId && loadingEl.classList.contains("is-hidden")) {
        sayBruce(sulking ? "idle_sulk" : "idle_happy", 5000);
      }
    },
    destroy() {
      if (destroyed) return;
      destroyed = true;
      document.body.classList.remove("is-hub3d-view", "is-hub3d-act");
      if (rafId) cancelAnimationFrame(rafId);
      actCleanup?.();
      timers.forEach((t) => clearTimeout(t));
      timers.clear();
      cleanups.forEach((fn) => fn());
      cleanups.length = 0;
      bruce.destroy();
      controls.dispose();
      skyPlaneGeo.dispose();
      skyPlaneMat.dispose();
      envRT.dispose();
      moteGeo.dispose();
      moteMat.dispose();
      rainGeo.dispose();
      rainMat.dispose();
      ballGeo.dispose();
      ballMat.dispose();
      swapRingGeos.forEach((g) => g.dispose());
      swapRingMats.forEach((m) => m.dispose());
      if (roomRoot) {
        roomRoot.traverse((obj) => {
          if (obj.geometry) obj.geometry.dispose();
          const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
          mats.forEach((m) => {
            if (!m) return;
            m.map?.dispose?.();
            m.normalMap?.dispose?.();
            m.roughnessMap?.dispose?.();
            m.emissiveMap?.dispose?.();
            m.dispose?.();
          });
        });
      }
      renderer.dispose();
    },
  };
}
