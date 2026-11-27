import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { createLivingBruce } from "../hub3d/bruceLiving.js";
import { mountBruceChatBar } from "../hub3d/bruceChatUi.js";
import { sfx } from "../audio.js";
import { feedback } from "../juice.js";

const OVERVIEW_CAM = new THREE.Vector3(0.0, 6.2, 15.8);
const OVERVIEW_TARGET = new THREE.Vector3(0.0, 4.2, -5.5);
const FLOOR_Y = 0.0;

const BRUCE_HOME_POS = new THREE.Vector3(-0.25, FLOOR_Y, 1.8);
const BRUCE_HOME_ROT = 0.14;

const ACTIVITY_DEFS = {
  warehouse_salmon: {
    id: "warehouse_salmon",
    title: "鲜切三文鱼试吃台",
    win: 14,
    fail: -14,
    swapProb: 0.16,
    camPos: new THREE.Vector3(0.6, 5.4, -4.4),
    camTarget: new THREE.Vector3(0.0, 3.8, -10.4),
    brucePos: new THREE.Vector3(0.15, FLOOR_Y, -7.8),
    bruceRot: Math.PI,
  },
  warehouse_cart: {
    id: "warehouse_cart",
    title: "亚麻手推车备膳",
    win: 13,
    fail: -13,
    swapProb: 0.14,
    camPos: new THREE.Vector3(0.6, 4.9, 6.2),
    camTarget: new THREE.Vector3(-4.1, 2.5, 1.5),
    brucePos: new THREE.Vector3(-1.85, FLOOR_Y, 2.55),
    bruceRot: -1.18,
  },
  warehouse_freezer: {
    id: "warehouse_freezer",
    title: "和牛冷柜雾气寻宝",
    win: 12,
    fail: -13,
    swapProb: 0.12,
    camPos: new THREE.Vector3(-1.5, 5.1, -2.6),
    camTarget: new THREE.Vector3(-8.8, 4.4, -5.2),
    brucePos: new THREE.Vector3(-2.0, FLOOR_Y, -4.8),
    bruceRot: -1.46,
  },
};

const HOTSPOTS = [
  {
    id: "warehouse_salmon",
    kind: "act",
    title: "鲜切三文鱼试吃台",
    sub: "+14 分 · 16% 换分",
    pos: [0.0, 5.1, -9.2],
    icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 15h16"/><path d="M6 15a6 6 0 0 1 12 0"/><path d="M9 6c0 1.2 1 1.6 1 2.8M14 5.5c0 1.2 1 1.6 1 2.8"/></svg>`,
  },
  {
    id: "warehouse_cart",
    kind: "act",
    title: "亚麻手推车备膳",
    sub: "+13 分 · 14% 换分",
    pos: [-4.1, 4.2, 1.8],
    icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="9" cy="19" r="1.5"/><circle cx="17" cy="19" r="1.5"/><path d="M3 5h3l2.2 10h9.8l2-7H7"/></svg>`,
  },
  {
    id: "warehouse_freezer",
    kind: "act",
    title: "和牛冷柜雾气寻宝",
    sub: "+12 分 · 12% 换分",
    pos: [-7.9, 5.3, -5.2],
    icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M12 3v18"/><path d="M9 10v3M15 10v3"/></svg>`,
  },
  {
    id: "home_return",
    kind: "teleport",
    title: "返回 · 阳光客厅",
    sub: "回到主基地",
    code: "HOME·00",
    pos: [0.0, 8.0, 12.0],
    icon: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 10.5L12 3l9 7.5"/><path d="M6 9.5V20h12V9.5"/></svg>`,
  },
  {
    id: "street",
    kind: "teleport",
    title: "前往 · 海岸咖啡馆",
    sub: "吧台奶泡晒太阳",
    code: "OUT·01",
    pos: [6.0, 8.0, 12.0],
    icon: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 10h10v5a5 5 0 0 1-10 0v-5z"/><path d="M15 11h2a2.5 2.5 0 0 1 0 5h-2"/></svg>`,
  },
];

const DEFAULT_WAREHOUSE_COPY = {
  idle_happy: [
    "现煎鲜食吧台飘来野生帝王鲑与草饲黄油香，本汪的鼻尖早就先一步签到了。",
    "酒红格纹软垫铺进亚麻手推车里，挑两盒有机骨汤冻干就准备回家。",
    "左边干式熟成冷柜切着 M9 和牛，右边原木货架摆着冷压鲜食，每一样都合口味。",
  ],
  idle_sulk: [
    "幸福指数跌破 80 了，连现煎野生帝王鲑都提不起劲，快回客厅哄我。",
    "天窗外都在阴天，本汪先挨着亚麻手推车安静歇一会儿，哼。",
  ],
  click_poke: [
    "逛有机市集也要保持仪态呀，别把我的暗酒红真丝领巾戳歪啦。",
    "再轻轻戳我一下，我就跳进手推车里的格纹软垫坐好。",
  ],
  click_poke_sulk: [
    "冷战期暂不挑食盆……除非现在切一小碟微温帝王鲑过来。",
    "哼，尾巴刚才只是被暖铜吊灯晃了一下，才没有偷摇。",
  ],
  tasting_bliss: [
    "野生帝王鲑配铜灯保温微熟度刚刚好，鲜味还留在鼻尖呢。",
  ],
  cart_cruise: [
    "推着深绿铜柄手推车路过原木货架，挑几盒无谷骨汤冻干和新鲜蓝莓。",
  ],
  cold_warn: [
    "哇！干式熟成冷柜寒气太足啦，飞机耳预警！先松手缓一秒！",
  ],
  walk_call: [
    "小短腿踩在哑光水磨石廊道上哒哒走来，先去鲜食吧台还是冷柜那侧？",
    "沿着有机生鲜廊道从容小跑过来，一切都在掌握中。",
  ],
  walk_sulk: [
    "阴天出来买菜没怎么睡醒……好吧，慢慢挪过去两步。",
  ],
  roll_over: [
    "趁天窗自然光洒在水磨石上翻个身打滚，格纹领巾铺在地板上刚刚好。",
  ],
  lick_paw: [
    "细细舔净前爪沾到的野生鲑鱼油脂香，一点鲜味也不浪费。",
  ],
  play_bow: [
    "前爪压低、尾巴愉悦轻摆，推上亚麻软垫手推车逛完本周有机货架吧！",
  ],
  airplane_ears: [
    "冷链风声轻拂，本汪先折起双耳开启流线防风模式。",
  ],
};

const DEFAULT_ACTIVITY_LINES = {
  warehouse_salmon: {
    win_lines: ["布鲁斯在铜灯暖光下先闻香验货，吹凉后一口叼住现煎野生帝王鲑，舔爪舔得十分满足。"],
    phone_fail_lines: ["低头滑手机两秒钟，试吃碟里刚煎好的帝王鲑凉掉了，布鲁斯安静坐着望向你。"],
    hazard_fail_lines: ["哎呀！误碰了旁边的青芥末小碟，布鲁斯打了个轻响的小喷嚏，耳朵贴成飞机耳。"],
  },
  warehouse_cart: {
    win_lines: ["酒红格纹软垫铺得松软贴身，布鲁斯稳稳挑齐了草饲骨汤冻干与有机鲜果，惬意收工。"],
    phone_fail_lines: ["刚看中上层原木架的冻干罐，你却点开了手机通知，推车半途停在过道上。"],
    hazard_fail_lines: ["拐弯太快轻轻晃了一下，果酱罐碰得叮当响，布鲁斯乖乖缩进软垫抱紧靠背。"],
  },
  warehouse_freezer: {
    win_lines: ["隔着擦净的冷柜玻璃一眼相中纹理最漂亮的 M9 雪花和牛，布鲁斯开心得当场翻肚皮打滚！"],
    phone_fail_lines: ["雾气刚擦开一半你就低头看手机，玻璃又重新起霜，M9 和牛礼盒被挡得严严实实。"],
    hazard_fail_lines: ["冷柜直吹寒风扑面而来，把布鲁斯的奶油长毛和耳朵吹得冰凉，立刻进入飞机耳抗议模式！"],
  },
};

function ensureHubStyles() {
  if (typeof document === "undefined") return;
  if (!document.querySelector('link[href*="hub3d.css"]')) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "./css/hub3d.css";
    document.head.appendChild(link);
  }
  if (!document.querySelector('link[href*="scenes3d.css"]')) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "./css/scenes3d.css";
    document.head.appendChild(link);
  }
}

function pickRandom(arr, fallback = "") {
  if (!Array.isArray(arr) || !arr.length) return fallback;
  return arr[Math.floor(Math.random() * arr.length)];
}

export function mountWarehouseHub(container, opts = {}) {
  ensureHubStyles();

  let sulking = Boolean(opts.sulking);
  let content = opts.content || {};
  let happiness = opts.happiness ?? 100;
  let whCopy = { ...DEFAULT_WAREHOUSE_COPY };
  let whActivities = { ...DEFAULT_ACTIVITY_LINES };

  document.body.classList.add("is-hub3d-view");
  document.body.classList.remove("is-hub3d-act");

  let destroyed = false;
  let rafId = null;
  let activeActId = null;
  let actCleanup = null;
  let camTween = null;

  fetch("./data/scenes_warehouse.json")
    .then((r) => (r.ok ? r.json() : null))
    .then((json) => {
      if (!destroyed && json) {
        if (json.thought_bubbles) {
          whCopy = { ...DEFAULT_WAREHOUSE_COPY, ...json.thought_bubbles };
        }
        if (json.activities) {
          whActivities = { ...DEFAULT_ACTIVITY_LINES, ...json.activities };
        }
      }
    })
    .catch(() => {});

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
    <div class="hub3d-wrap sc3d-wh-wrap">
      <div class="hub3d-stage">
        <canvas class="hub3d-canvas"></canvas>
        <div class="hub3d-vignette ${sulking ? "is-sulk" : ""}"></div>
        <canvas class="hub3d-fx-canvas" aria-hidden="true"></canvas>
        <div class="hub3d-viewfinder" aria-hidden="true">
          <span class="vf-corner vf-tl"></span>
          <span class="vf-corner vf-tr"></span>
          <span class="vf-corner vf-bl"></span>
          <span class="vf-corner vf-br"></span>
          <span class="vf-stamp">35MM · ELOWEN MARKET · F/2.0</span>
        </div>
        <div class="hub3d-pins"></div>
        <div class="hub3d-keyholder">
          <button type="button" class="keyholder-btn" aria-expanded="false">
            <span class="keyholder-fob" aria-hidden="true">🔑</span>
            <span>通行钥匙夹</span>
            <span class="keyholder-count">2</span>
          </button>
          <div class="keyholder-tray" role="menu" aria-label="前往其他场景">
            <div class="keyholder-tray-head">
              <span>CLUB PASS HOLDER</span>
              <span>点击传送</span>
            </div>
          </div>
        </div>
        <div class="hub3d-speech" aria-live="polite">
          <span class="speech-cue"></span>
          <span class="speech-line"></span>
        </div>
        <div class="hub3d-tricks-bar" role="toolbar" aria-label="与布鲁斯互动动作">
          <button type="button" class="trick-pill" data-trick="walk">
            <svg class="trick-ico" viewBox="0 0 24 24" width="13" height="13" fill="currentColor" aria-hidden="true"><circle cx="7" cy="8.5" r="1.8"/><circle cx="12" cy="6.5" r="1.8"/><circle cx="17" cy="8.5" r="1.8"/><path d="M12 11.2c-3 0-5.2 2.4-5.2 4.7 0 1.4 1 2.4 2.4 2.4.9 0 1.8-.35 2.8-.35s1.9.35 2.8.35c1.4 0 2.4-1 2.4-2.4 0-2.3-2.2-4.7-5.2-4.7z"/></svg>
            <span>唤过来</span>
          </button>
          <button type="button" class="trick-pill" data-trick="roll_over">肚皮打滚</button>
          <button type="button" class="trick-pill" data-trick="lick_paw">舔小爪子</button>
          <button type="button" class="trick-pill" data-trick="play_bow">伸个懒腰</button>
          <button type="button" class="trick-pill" data-trick="airplane_ears">委屈飞机耳</button>
          <button type="button" class="trick-pill is-ai-chat" id="hub3d-btn-chat">✦ 逗它说话</button>
        </div>
        <button type="button" class="hub3d-reset-btn">⌖ 归中视角</button>

        <div class="hub3d-act-overlay">
          <div class="hub3d-act-top">
            <button type="button" class="hub3d-glass-pill" id="hub3d-btn-back">回到有机市集全景</button>
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
            <button type="button" class="th-btn-ghost" id="hub3d-btn-done">回到有机市集全景</button>
          </div>
        </section>

        <div class="hub3d-loading">
          <span>正在推开 ELOWEN 有机市集木框玻璃门……</span>
        </div>
      </div>
      <p class="hub3d-hint">拖动环视 ELOWEN 有机市集 · 点击水磨石廊道唤狗，点黄铜光点体验鲜食吧/冷柜/备膳车</p>
    </div>
  `;

  const stageEl = container.querySelector(".hub3d-stage");
  const canvas = container.querySelector(".hub3d-canvas");
  const fxCanvas = container.querySelector(".hub3d-fx-canvas");
  const vignetteEl = container.querySelector(".hub3d-vignette");
  const pinsLayer = container.querySelector(".hub3d-pins");
  const keyholderEl = container.querySelector(".hub3d-keyholder");
  const keyholderBtn = container.querySelector(".keyholder-btn");
  const keyholderTray = container.querySelector(".keyholder-tray");
  const speechEl = container.querySelector(".hub3d-speech");
  const speechCueEl = speechEl?.querySelector(".speech-cue");
  const speechLineEl = speechEl?.querySelector(".speech-line");
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

  // Renderer
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.96;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(sulking ? 0x1c2633 : 0x252830);

  // Studio Club Warehouse PMREM Environment Map (crisp reflections on terrazzo, stainless, copper, marble)
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene();
  envScene.background = new THREE.Color(0xd8d5ce);
  const envBox = new THREE.Mesh(
    new THREE.BoxGeometry(28, 20, 28),
    new THREE.MeshBasicMaterial({ color: 0xd0ccc4, side: THREE.BackSide }),
  );
  const envSkylight = new THREE.Mesh(
    new THREE.PlaneGeometry(14, 24),
    new THREE.MeshBasicMaterial({ color: 0xf4f8ff }),
  );
  envSkylight.position.set(0, 9.6, 0);
  envSkylight.rotation.x = Math.PI * 0.5;
  const envIceLeft = new THREE.Mesh(
    new THREE.PlaneGeometry(24, 12),
    new THREE.MeshBasicMaterial({ color: 0xbce2ff }),
  );
  envIceLeft.position.set(-13.2, 2.0, 0);
  envIceLeft.rotation.y = Math.PI * 0.5;
  const envWarmRight = new THREE.Mesh(
    new THREE.PlaneGeometry(24, 12),
    new THREE.MeshBasicMaterial({ color: 0xffdfad }),
  );
  envWarmRight.position.set(13.2, 2.0, 0);
  envWarmRight.rotation.y = -Math.PI * 0.5;
  envScene.add(envBox, envSkylight, envIceLeft, envWarmRight);
  const envRT = pmrem.fromScene(envScene, 0.04);
  scene.environment = envRT.texture;
  scene.environmentIntensity = 0.62;
  pmrem.dispose();
  [envBox, envSkylight, envIceLeft, envWarmRight].forEach((m) => {
    m.geometry.dispose();
    m.material.dispose();
  });

  const camera = new THREE.PerspectiveCamera(50, 16 / 10, 0.25, 160);
  camera.position.copy(OVERVIEW_CAM);

  const controls = new OrbitControls(camera, canvas);
  controls.target.copy(OVERVIEW_TARGET);
  controls.enableDamping = true;
  controls.dampingFactor = 0.07;
  controls.enablePan = false;
  controls.minDistance = 5.5;
  controls.maxDistance = 23.0;
  controls.minPolarAngle = 0.72;
  controls.maxPolarAngle = 1.46;
  controls.minAzimuthAngle = -0.92;
  controls.maxAzimuthAngle = 0.92;
  controls.update();

  // Lighting Rig: Clerestory Skylight Daylight + Copper Tasting Bar Warm Glow + Freezer Ice-Blue Glow
  const hemiLight = new THREE.HemisphereLight(0xf6f9ff, 0x9b968d, 0.84);
  scene.add(hemiLight);

  const ambientLight = new THREE.AmbientLight(0xfffaf2, 0.28);
  scene.add(ambientLight);

  const skylightSun = new THREE.DirectionalLight(0xfff5e4, 1.48);
  skylightSun.position.set(4, 22, 6);
  skylightSun.target.position.set(0, 0, -4);
  skylightSun.castShadow = true;
  skylightSun.shadow.mapSize.set(1024, 1024);
  skylightSun.shadow.camera.near = 4;
  skylightSun.shadow.camera.far = 48;
  skylightSun.shadow.camera.left = -18;
  skylightSun.shadow.camera.right = 18;
  skylightSun.shadow.camera.top = 18;
  skylightSun.shadow.camera.bottom = -18;
  skylightSun.shadow.bias = -0.0005;
  scene.add(skylightSun, skylightSun.target);

  const tastingHeatLight = new THREE.PointLight(0xffb86c, 1.85, 22, 1.35);
  tastingHeatLight.position.set(0.0, 6.4, -10.5);
  scene.add(tastingHeatLight);

  const freezerGlowLight = new THREE.PointLight(0x9bd6ff, 1.25, 20, 1.35);
  freezerGlowLight.position.set(-6.4, 5.2, -3.5);
  scene.add(freezerGlowLight);

  const rackWarmLight = new THREE.PointLight(0xffe4b8, 1.05, 24, 1.4);
  rackWarmLight.position.set(5.6, 8.8, -1.5);
  scene.add(rackWarmLight);

  // Sunlit warehouse motes (happy mode) & Rain streaks outside high skylight wells (sulk mode)
  const moteCount = 36;
  const motePos = new Float32Array(moteCount * 3);
  for (let i = 0; i < moteCount; i++) {
    motePos[i * 3] = -6.5 + ((i * 1.93) % 13.0);
    motePos[i * 3 + 1] = 2.0 + ((i * 2.11) % 12.0);
    motePos[i * 3 + 2] = -14.0 + ((i * 2.37) % 24.0);
  }
  const moteGeo = new THREE.BufferGeometry();
  moteGeo.setAttribute("position", new THREE.BufferAttribute(motePos, 3));
  const moteMat = new THREE.PointsMaterial({
    color: 0xfff4d4,
    size: 0.14,
    transparent: true,
    opacity: 0.48,
    depthWrite: false,
  });
  const motePoints = new THREE.Points(moteGeo, moteMat);
  scene.add(motePoints);

  const rainCount = 120;
  const rainPos = new Float32Array(rainCount * 3);
  for (let i = 0; i < rainCount; i++) {
    rainPos[i * 3] = -4.4 + ((i * 0.77) % 8.8);
    rainPos[i * 3 + 1] = 11.5 + ((i * 1.41) % 6.4);
    rainPos[i * 3 + 2] = -15.0 + ((i * 1.97) % 23.0);
  }
  const rainGeo = new THREE.BufferGeometry();
  rainGeo.setAttribute("position", new THREE.BufferAttribute(rainPos, 3));
  const rainMat = new THREE.PointsMaterial({
    color: 0xb8d8ff,
    size: 0.18,
    transparent: true,
    opacity: 0.78,
    depthWrite: false,
  });
  const rainPoints = new THREE.Points(rainGeo, rainMat);
  rainPoints.visible = sulking;
  scene.add(rainPoints);

  // Animated 3D Tasting Salmon Plate Prop (slides toward Bruce during warehouse_salmon)
  const salmonPlateGroup = new THREE.Group();
  salmonPlateGroup.position.set(0.0, 3.76, -10.35);
  salmonPlateGroup.visible = false;
  const plateGeo = new THREE.CylinderGeometry(0.42, 0.36, 0.06, 20);
  const plateMat = new THREE.MeshStandardMaterial({ color: 0xf8f6f2, roughness: 0.16, metalness: 0.05 });
  const plateMesh = new THREE.Mesh(plateGeo, plateMat);
  plateMesh.castShadow = true;
  const salmonCubeGeo = new THREE.BoxGeometry(0.26, 0.15, 0.22);
  const salmonCubeMat = new THREE.MeshStandardMaterial({ color: 0xeb7852, roughness: 0.34 });
  const s1 = new THREE.Mesh(salmonCubeGeo, salmonCubeMat);
  s1.position.set(-0.11, 0.11, 0.02);
  s1.rotation.y = 0.22;
  const s2 = new THREE.Mesh(salmonCubeGeo, salmonCubeMat);
  s2.position.set(0.12, 0.11, -0.04);
  s2.rotation.y = -0.34;
  salmonPlateGroup.add(plateMesh, s1, s2);
  scene.add(salmonPlateGroup);

  // Animated 3D Elowen Cart Treat Loot Prop (pops into Bruce's cart during warehouse_cart)
  const cartLootGroup = new THREE.Group();
  cartLootGroup.position.set(-4.35, 3.25, 1.35);
  cartLootGroup.visible = false;
  const lootBoxGeo = new THREE.BoxGeometry(0.76, 0.92, 0.62);
  const lootBoxMat = new THREE.MeshStandardMaterial({ color: 0x20222a, roughness: 0.38, metalness: 0.15 });
  const lootBox = new THREE.Mesh(lootBoxGeo, lootBoxMat);
  const lootLidGeo = new THREE.BoxGeometry(0.80, 0.12, 0.66);
  const lootLidMat = new THREE.MeshStandardMaterial({ color: 0xdfbe7d, roughness: 0.28, metalness: 0.78 });
  const lootLid = new THREE.Mesh(lootLidGeo, lootLidMat);
  lootLid.position.y = 0.50;
  cartLootGroup.add(lootBox, lootLid);
  scene.add(cartLootGroup);

  // 3D Golden swap halo rings around Bruce
  const swapRingsGroup = new THREE.Group();
  swapRingsGroup.position.copy(BRUCE_HOME_POS).add(new THREE.Vector3(0, 1.35, 0));
  swapRingsGroup.visible = false;
  const swapRingGeos = [];
  const swapRingMats = [];
  for (let i = 0; i < 4; i++) {
    const rg = new THREE.TorusGeometry(1.45 + i * 0.30, 0.04, 10, 64);
    const rm = new THREE.MeshBasicMaterial({ color: 0xf7d788, transparent: true, opacity: 0.78 });
    const mesh = new THREE.Mesh(rg, rm);
    mesh.rotation.set(Math.PI * 0.42 + i * 0.3, i * 0.6, 0);
    swapRingsGroup.add(mesh);
    swapRingGeos.push(rg);
    swapRingMats.push(rm);
  }
  scene.add(swapRingsGroup);

  // Living Bruce on polished terrazzo floor (FLOOR_Y = 0.0)
  const bruce = createLivingBruce({ modelUrl: "./assets/models/bruce_rigged.glb", height: 2.38 });
  bruce.root.position.copy(BRUCE_HOME_POS);
  bruce.root.rotation.y = BRUCE_HOME_ROT;
  bruce.setMood(sulking ? "sulk" : "happy");
  scene.add(bruce.root);

  // Champagne-gold floor click ripple indicator for Walk-to navigation
  const rippleGeo = new THREE.RingGeometry(0.16, 0.24, 32);
  rippleGeo.rotateX(-Math.PI / 2);
  const rippleMat = new THREE.MeshBasicMaterial({
    color: 0xf4d48c,
    transparent: true,
    opacity: 0,
    depthWrite: false,
    side: THREE.DoubleSide,
  });
  const rippleMesh = new THREE.Mesh(rippleGeo, rippleMat);
  rippleMesh.position.set(BRUCE_HOME_POS.x, FLOOR_Y + 0.025, BRUCE_HOME_POS.z);
  rippleMesh.visible = false;
  scene.add(rippleMesh);
  let rippleAge = -1;

  function triggerFloorRipple(x, z) {
    rippleMesh.position.set(x, FLOOR_Y + 0.025, z);
    rippleMesh.scale.setScalar(0.6);
    rippleMesh.visible = true;
    rippleAge = 0;
  }

  // Tracked GLB materials for atmosphere switching
  let skylightMatRef = null;
  let warmLedMatRef = null;
  let iceLedMatRef = null;
  let warehouseRoot = null;

  const gltfLoader = new GLTFLoader();
  const warehouseReady = new Promise((resolve) => {
    gltfLoader.load(
      "./assets/models/warehouse_club.glb",
      (gltf) => {
        if (destroyed) return;
        warehouseRoot = gltf.scene;
        warehouseRoot.traverse((obj) => {
          if (!obj.isMesh) return;
          const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
          const matName = mats[0]?.name || obj.name || "";

          if (matName === "FreezerGlass" || matName === "SkylightSky") {
            obj.castShadow = false;
            obj.receiveShadow = false;
          } else {
            obj.castShadow = true;
            obj.receiveShadow = true;
          }

          mats.forEach((m) => {
            if (!m) return;
            if (m.map) {
              m.map.colorSpace = THREE.SRGBColorSpace;
              m.map.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
            }
            if (m.emissiveMap) m.emissiveMap.colorSpace = THREE.SRGBColorSpace;

            if (m.name === "SkylightSky") {
              skylightMatRef = m;
              m.color.setHex(sulking ? 0x455a75 : 0xd6ebff);
              m.emissive.setHex(sulking ? 0x2f435c : 0xcce4ff);
              m.emissiveIntensity = sulking ? 0.65 : 1.35;
            } else if (m.name === "LinearLedWarm") {
              warmLedMatRef = m;
              m.emissiveIntensity = sulking ? 1.95 : 1.35;
            } else if (m.name === "FreezerLedIce") {
              iceLedMatRef = m;
              m.emissiveIntensity = sulking ? 2.1 : 1.45;
            }
            m.needsUpdate = true;
          });
        });
        scene.add(warehouseRoot);
        resolve(true);
      },
      undefined,
      (err) => {
        console.warn("warehouse_club.glb load error:", err);
        resolve(false);
      },
    );
  });

  Promise.all([warehouseReady, bruce.ready]).then(() => {
    if (!destroyed) {
      loadingEl.classList.add("is-hidden");
      later(() => {
        if (!activeActId) sayBruce(sulking ? "idle_sulk" : "idle_happy", 4400);
      }, 900);
    }
  });

  const WH_SPEECH_CUES = {
    idle_happy: "BRUCE · 市集晨巡",
    idle_sulk: "BRUCE · 阴天冷战中",
    click_poke: "BRUCE · 领巾晃动",
    click_poke_sulk: "BRUCE · 别扭哼声",
    tasting_bliss: "BRUCE · 帝王鲑微熟",
    cart_cruise: "BRUCE · 有机备膳中",
    cold_warn: "BRUCE · 冷气飞机耳预警",
    walk_call: "BRUCE · 通道巡视",
    walk_sulk: "BRUCE · 缓慢挪步",
    roll_over: "BRUCE · 水磨石打滚",
    lick_paw: "BRUCE · 舔干净鱼油香",
    play_bow: "BRUCE · 货架前伸懒腰",
    airplane_ears: "BRUCE · 冷风飞机耳",
  };

  let speechTimer = null;
  let lastSpeechText = "";
  let lastSpeechAt = 0;
  function sayBruce(categoryOrText, durationMs = 3800, customCue = "") {
    if (!speechEl || !speechLineEl || destroyed) return;
    const pool = whCopy?.[categoryOrText];
    let text = "";
    if (Array.isArray(pool) && pool.length) {
      text = pickRandom(pool, "");
      if (text === lastSpeechText && pool.length > 1) {
        text = pool[(pool.indexOf(text) + 1) % pool.length];
      }
    } else {
      text = String(categoryOrText || "");
    }
    if (!text) return;
    lastSpeechText = text;
    lastSpeechAt = performance.now();
    if (speechCueEl) {
      speechCueEl.textContent = customCue || WH_SPEECH_CUES[categoryOrText] || (sulking ? "BRUCE · 阴天冷战中" : "BRUCE · 鲜食吧轻哼");
    }
    speechLineEl.textContent = text;
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
    if (
      !destroyed &&
      !activeActId &&
      loadingEl.classList.contains("is-hidden") &&
      performance.now() - lastSpeechAt >= 6800 &&
      !bruce.isWalking?.() &&
      !bruce.getActiveAction?.()
    ) {
      sayBruce(sulking ? "idle_sulk" : "idle_happy", 5200);
    }
  }, 7500);
  cleanups.push(() => clearInterval(idleTimerId));

  // Folding keyholder toggle
  const setKeyholderOpen = (open) => {
    keyholderEl?.classList.toggle("is-open", open);
    keyholderBtn?.setAttribute("aria-expanded", open ? "true" : "false");
  };
  keyholderBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    sfx.playTap();
    setKeyholderOpen(!keyholderEl?.classList.contains("is-open"));
  });
  const onDocClickCloseKey = (e) => {
    if (keyholderEl && !keyholderEl.contains(e.target)) {
      setKeyholderOpen(false);
    }
  };
  document.addEventListener("click", onDocClickCloseKey);
  cleanups.push(() => document.removeEventListener("click", onDocClickCloseKey));

  // Build breathing brass dots (3 warehouse activities) & keyholder passes (teleports)
  const pinItems = HOTSPOTS.filter((s) => s.kind === "act").map((spot) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "hub3d-pin hub3d-dot";
    btn.setAttribute("data-spot", spot.id);
    btn.setAttribute("aria-label", `${spot.title}（${spot.sub}）`);
    btn.innerHTML = `
      <span class="dot-core">${spot.icon}</span>
      <span class="dot-popover">
        <span class="dot-title">${spot.title}</span>
        <span class="dot-sub">${spot.sub}</span>
      </span>
    `;
    pinsLayer.appendChild(btn);
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      setKeyholderOpen(false);
      feedback("small", e.clientX, e.clientY);
      sfx.playTap();
      handleHotspotClick(spot);
    });
    return { spot, btn, world: new THREE.Vector3(...spot.pos) };
  });

  HOTSPOTS.filter((s) => s.kind === "teleport").forEach((spot) => {
    if (!keyholderTray) return;
    const item = document.createElement("button");
    item.type = "button";
    item.className = "keyholder-item";
    item.setAttribute("data-spot", spot.id);
    item.innerHTML = `
      <span class="stub-main">
        <span class="stub-icon">${spot.icon}</span>
        <span class="stub-text">
          <span class="stub-title">${spot.title}</span>
          <span class="stub-sub">${spot.sub}</span>
        </span>
      </span>
      <span class="stub-code">${spot.code}</span>
    `;
    keyholderTray.appendChild(item);
    item.addEventListener("click", (e) => {
      e.stopPropagation();
      setKeyholderOpen(false);
      feedback("small", e.clientX, e.clientY);
      sfx.playTap();
      handleHotspotClick(spot);
    });
    item.addEventListener("pointerenter", () => {
      if (activeActId) return;
      if (spot.id === "home_return") {
        sayBruce("备膳挑好啦，携 07 号记账卡回阳光客厅吧。", 3200, "BRUCE · 出口张望");
      } else if (spot.id === "street") {
        sayBruce("有机食材齐了，顺路去海岸烘焙室喝一杯山羊奶微泡吧。", 3200, "BRUCE · 出口张望");
      }
    });
  });

  function applyAtmosphere(sulkMode) {
    sulking = Boolean(sulkMode);
    vignetteEl.classList.toggle("is-sulk", sulking);
    rainPoints.visible = sulking;
    motePoints.visible = !sulking;

    if (sulking) {
      scene.background.setHex(0x182230);
      hemiLight.color.setHex(0x88a4c6);
      hemiLight.groundColor.setHex(0x414852);
      hemiLight.intensity = 0.56;
      skylightSun.color.setHex(0x9ab8dc);
      skylightSun.intensity = 0.42;
      ambientLight.intensity = 0.22;
      tastingHeatLight.intensity = 2.55;
      freezerGlowLight.intensity = 1.85;
      rackWarmLight.intensity = 1.25;
      if (skylightMatRef) {
        skylightMatRef.color.setHex(0x455a75);
        skylightMatRef.emissive.setHex(0x2f435c);
        skylightMatRef.emissiveIntensity = 0.65;
      }
      if (warmLedMatRef) warmLedMatRef.emissiveIntensity = 1.95;
      if (iceLedMatRef) iceLedMatRef.emissiveIntensity = 2.1;
      bruce.setMood("sulk");
    } else {
      scene.background.setHex(0x252830);
      hemiLight.color.setHex(0xf6f9ff);
      hemiLight.groundColor.setHex(0x9b968d);
      hemiLight.intensity = 0.84;
      skylightSun.color.setHex(0xfff5e4);
      skylightSun.intensity = 1.48;
      ambientLight.intensity = 0.28;
      tastingHeatLight.intensity = 1.85;
      freezerGlowLight.intensity = 1.25;
      rackWarmLight.intensity = 1.05;
      if (skylightMatRef) {
        skylightMatRef.color.setHex(0xd6ebff);
        skylightMatRef.emissive.setHex(0xcce4ff);
        skylightMatRef.emissiveIntensity = 1.35;
      }
      if (warmLedMatRef) warmLedMatRef.emissiveIntensity = 1.35;
      if (iceLedMatRef) iceLedMatRef.emissiveIntensity = 1.45;
      if (!activeActId) bruce.setMood("happy");
    }

    speechEl?.classList.toggle("is-sulk", sulking);
    pinItems.forEach(({ spot, btn }) => {
      const subEl = btn.querySelector(".dot-sub");
      if (subEl) subEl.textContent = sulking ? "先哄好布鲁斯" : spot.sub;
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

  function exitActivity() {
    actCleanup?.();
    actCleanup = null;
    activeActId = null;
    document.body.classList.remove("is-hub3d-act");
    salmonPlateGroup.visible = false;
    cartLootGroup.visible = false;
    swapRingsGroup.visible = false;
    swapBanner.classList.remove("is-visible");
    settleEl.classList.remove("is-visible");
    vignetteEl.classList.remove("is-warn");
    actOverlay.classList.remove("is-active");
    actBodyEl.innerHTML = "";
    pinsLayer.classList.remove("is-hidden");
    resetBtn.style.display = "";
    controls.enabled = true;
    bruce.stopWalk();
    bruce.setPetting(0);
    bruce.root.position.copy(BRUCE_HOME_POS);
    bruce.root.rotation.y = BRUCE_HOME_ROT;
    swapRingsGroup.position.copy(BRUCE_HOME_POS).add(new THREE.Vector3(0, 1.35, 0));
    applyAtmosphere(sulking);
    sfx.setSceneAmbience("warehouse", { sulking });
    stageEl.dataset.soundscapeDiag = JSON.stringify({ scene: "warehouse", sulking, muted: sfx.muted });
    flyCamera(OVERVIEW_CAM, OVERVIEW_TARGET, 650);
  }

  btnActBack.addEventListener("click", () => {
    sfx.playTap();
    exitActivity();
  });

  btnReplay.addEventListener("click", () => {
    if (sulking || !activeActId) return;
    sfx.playTap();
    startWarehouseActivity(activeActId, false);
  });

  btnDone.addEventListener("click", () => {
    sfx.playTap();
    if (sulking) {
      exitActivity();
      opts.onOpenShop?.();
    } else {
      exitActivity();
    }
  });

  function startWarehouseActivity(actId, autoplay = false) {
    const def = ACTIVITY_DEFS[actId];
    if (!def) return;

    actCleanup?.();
    activeActId = actId;
    bruce.stopWalk();
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

    bruce.root.position.copy(def.brucePos);
    bruce.root.rotation.y = def.bruceRot;
    swapRingsGroup.position.copy(def.brucePos).add(new THREE.Vector3(0, 1.35, 0));
    bruce.setMood("happy");

    salmonPlateGroup.visible = actId === "warehouse_salmon";
    salmonPlateGroup.position.set(0.0, 3.76, -10.35);
    cartLootGroup.visible = false;
    cartLootGroup.position.set(-4.35, 3.25, 1.35);

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
      startWarehouseActivity(actId, !autoplay);
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
        if (actId === "warehouse_salmon") {
          bruce.playAction("lick_paw");
        } else if (actId === "warehouse_cart") {
          bruce.playAction("play_bow");
        } else {
          bruce.playAction("roll_over");
        }
        const r = stageEl.getBoundingClientRect();
        spawnFxParticles(r.width * 0.5, r.height * 0.48, "gold", 22);
      } else {
        sfx.playFail();
        bruce.setMood("sulk");
        bruce.playAction("airplane_ears");
      }

      const actCopy = content?.activities?.[actId] || whActivities?.[actId] || DEFAULT_ACTIVITY_LINES[actId] || {};
      const pool =
        outcome === "win"
          ? actCopy.win_lines
          : outcome === "phone_fail"
            ? actCopy.phone_fail_lines
            : actCopy.hazard_fail_lines;
      const summaryLine = pickRandom(
        pool,
        isWin ? "布鲁斯在 ELOWEN 有机市集备好本周鲜食，满意地晃起大尾巴。" : "布鲁斯被突发声响惊了一下，默默折平飞机耳。",
      );

      settleEl.querySelector(".hub3d-settle-title").textContent =
        outcome === "win" ? "备膳完成" : outcome === "phone_fail" ? "被手机抢走了" : "踩到雷点了";
      const deltaEl = settleEl.querySelector(".hub3d-settle-delta");
      deltaEl.textContent = `${delta >= 0 ? "+" : ""}${delta}`;
      deltaEl.classList.toggle("is-neg", delta < 0);
      settleEl.querySelector(".hub3d-settle-line").textContent = summaryLine;
      const statusEl = settleEl.querySelector(".hub3d-settle-status");
      statusEl.textContent = "正在同步幸福指数……";

      const projected = Math.max(0, happiness + delta);
      btnReplay.hidden = projected < 80;
      btnDone.textContent = projected < 80 ? "去私厨鲜食柜" : "回到有机市集全景";
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
          applyAtmosphere(true);
          statusEl.textContent = `幸福指数跌至 ${finalScore}（<80），布鲁斯进入冷战`;
          btnDone.textContent = "去私厨鲜食柜";
        } else {
          statusEl.textContent = `当前幸福指数 · ${finalScore}`;
          btnDone.textContent = "回到有机市集全景";
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

    actLater(() => triggerPhone(false), 1900 + Math.random() * 1400);

    // 3 Warehouse-specific 3D interactions
    if (actId === "warehouse_salmon") {
      actPromptEl.textContent = "按顺序侍奉试吃台：闻香验货 → 吹凉切块 → 端上试吃碟";
      actBodyEl.innerHTML = `
        <div class="hub3d-props-row">
          <button type="button" class="hub3d-prop-btn" data-prop="sniff">SNIFF · 闻香验货</button>
          <button type="button" class="hub3d-prop-btn" data-prop="cool">COOL · 吹凉切块</button>
          <button type="button" class="hub3d-prop-btn" data-prop="serve">SERVE · 端上试吃碟</button>
        </div>
        <button type="button" class="hub3d-hazard-btn">WASABI · 误碰青芥末</button>
      `;
      const order = ["sniff", "cool", "serve"];
      let step = 0;
      const hazardBtn = actBodyEl.querySelector(".hub3d-hazard-btn");
      listen(hazardBtn, "click", (e) => {
        e.stopPropagation();
        conclude("hazard_fail");
      });

      const handleProp = (prop, btn) => {
        if (finished || btn.classList.contains("is-done")) return;
        if (prop !== order[step]) {
          conclude("hazard_fail");
          return;
        }
        btn.classList.add("is-done");
        step += 1;
        sfx.playTap();
        bruce.setMood("excited");
        bruce.triggerHappyHop();
        const r = stageEl.getBoundingClientRect();
        spawnFxParticles(r.width * 0.52, r.height * 0.5, step === 3 ? "gold" : "warm", 18);
        if (step === 1) {
          salmonPlateGroup.position.set(0.0, 3.76, -9.95);
          actPromptEl.textContent = "鲜度验收通过！赶紧吹凉切块准备装碟";
        } else if (step === 2) {
          salmonPlateGroup.position.set(0.0, 3.76, -9.55);
          sayBruce("tasting_bliss", 3000);
          actPromptEl.textContent = "温度刚刚好！端到布鲁斯面前的试吃碟";
        } else {
          salmonPlateGroup.position.set(0.10, 3.76, -9.15);
          bruce.playAction("lick_paw");
          sayBruce("tasting_bliss", 3000);
          actLater(() => conclude("win"), 600);
        }
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
    } else if (actId === "warehouse_cart") {
      actPromptEl.textContent = "亚麻手推车备膳：铺好格纹软垫 → 巡视原木货架 → 装入冻干食材";
      actBodyEl.innerHTML = `
        <div class="hub3d-props-row">
          <button type="button" class="hub3d-prop-btn" data-prop="cushion">CUSHION · 铺好格纹软垫</button>
          <button type="button" class="hub3d-prop-btn" data-prop="patrol">PATROL · 巡视有机货架</button>
          <button type="button" class="hub3d-prop-btn" data-prop="load">LOAD · 选入冻干食材</button>
        </div>
        <button type="button" class="hub3d-hazard-btn">BUMP · 急转弯颠簸</button>
      `;
      const order = ["cushion", "patrol", "load"];
      let step = 0;
      const hazardBtn = actBodyEl.querySelector(".hub3d-hazard-btn");
      listen(hazardBtn, "click", (e) => {
        e.stopPropagation();
        conclude("hazard_fail");
      });

      const handleProp = (prop, btn) => {
        if (finished || btn.classList.contains("is-done")) return;
        if (prop !== order[step]) {
          conclude("hazard_fail");
          return;
        }
        btn.classList.add("is-done");
        step += 1;
        sfx.playTap();
        bruce.setMood("excited");
        bruce.triggerHappyHop();
        const r = stageEl.getBoundingClientRect();
        spawnFxParticles(r.width * 0.45, r.height * 0.52, step === 3 ? "gold" : "warm", 18);
        if (step === 1) {
          actPromptEl.textContent = "酒红格纹软垫铺平啦！稳步推去冻干货架巡视";
        } else if (step === 2) {
          cartLootGroup.visible = true;
          cartLootGroup.position.set(-4.35, 3.45, 1.35);
          sayBruce("cart_cruise", 3000);
          actPromptEl.textContent = "选中有机草饲冻干！放入亚麻手推车里";
        } else {
          cartLootGroup.visible = true;
          cartLootGroup.position.set(-4.35, 2.75, 1.35);
          bruce.playAction("play_bow");
          sayBruce("cart_cruise", 3000);
          actLater(() => conclude("win"), 600);
        }
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
    } else if (actId === "warehouse_freezer") {
      actPromptEl.textContent = "在起雾的冷柜玻璃上来回擦拭，替布鲁斯挑出 M9 雪花和牛";
      actBodyEl.innerHTML = `
        <div class="hub3d-brush-zone sc3d-wh-frost-zone">
          <span class="sc3d-wh-frost-label">按住来回擦拭冷柜雾气</span>
        </div>
        <div class="hub3d-progress"><div class="hub3d-progress-fill"></div></div>
        <button type="button" class="hub3d-hazard-btn">COLD BLAST · 冷风直吹</button>
      `;
      const zone = actBodyEl.querySelector(".hub3d-brush-zone");
      const frostLabel = actBodyEl.querySelector(".sc3d-wh-frost-label");
      const fill = actBodyEl.querySelector(".hub3d-progress-fill");
      const hazardBtn = actBodyEl.querySelector(".hub3d-hazard-btn");

      listen(hazardBtn, "click", (e) => {
        e.stopPropagation();
        conclude("hazard_fail");
      });

      let progress = 0;
      const TARGET = 1800;
      let warning = false;
      let warnedOnce = false;
      let warnMove = 0;
      let dragging = false;
      let lastPos = null;
      let lastTapAt = 0;

      const stroke = (dx, dy, cx, cy) => {
        const d = Math.hypot(dx, dy);
        if (d < 1) return;
        if (warning) {
          warnMove += d;
          if (warnMove > 65) conclude("hazard_fail");
          return;
        }
        progress = Math.min(TARGET, progress + d);
        const pct = progress / TARGET;
        fill.style.width = `${pct * 100}%`;
        zone.style.opacity = String(Math.max(0.18, 1 - pct * 0.78));
        if (frostLabel && pct > 0.25) {
          frostLabel.textContent = pct > 0.72 ? "M9 雪花和牛已现身，继续擦净！" : "雾气散开中……";
        }
        bruce.setPetting(0.9);
        bruce.setMood("excited");
        const rect = stageEl.getBoundingClientRect();
        spawnFxParticles(cx - rect.left, cy - rect.top, "water", 3);
        const now = performance.now();
        if (now - lastTapAt > 280) {
          lastTapAt = now;
          sfx.playTap();
        }
        if (!warnedOnce && progress >= TARGET * 0.44) {
          warnedOnce = true;
          warning = true;
          warnMove = 0;
          bruce.setMood("warn");
          bruce.playAction("airplane_ears");
          sayBruce("cold_warn", 2600);
          vignetteEl.classList.add("is-warn");
          actPromptEl.textContent = "冷气冰耳朵 · 飞机耳预警！快松手停顿 1.4 秒";
          actLater(() => {
            warning = false;
            bruce.setMood("happy");
            vignetteEl.classList.remove("is-warn");
            actPromptEl.textContent = "冷气散去啦，继续擦拭找出金标 M9 和牛";
          }, 1400);
        }
        if (progress >= TARGET) conclude("win");
      };

      listen(actOverlay, "pointerdown", (e) => {
        if (autoplay || e.target === hazardBtn || e.target.closest(".hub3d-phone-banner") || e.target.closest(".hub3d-act-top")) return;
        const r = zone.getBoundingClientRect();
        if (e.clientX >= r.left - 45 && e.clientX <= r.right + 45 && e.clientY >= r.top - 45 && e.clientY <= r.bottom + 45) {
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
          stroke(420, 28, r.left + r.width * 0.5, r.top + r.height * 0.5);
          actLater(autoStep, 650);
        };
        actLater(autoStep, 750);
      }
    }

    actCleanup = () => {
      finished = true;
      actTimers.forEach((t) => clearTimeout(t));
      actTimers.clear();
      actListeners.forEach((fn) => fn());
      actListeners.length = 0;
      salmonPlateGroup.visible = false;
      cartLootGroup.visible = false;
    };
  }

  function handleHotspotClick(spot) {
    if (spot.kind === "act") {
      if (sulking) {
        sayBruce("idle_sulk", 3600);
        opts.onOpenShop?.();
        return;
      }
      startWarehouseActivity(spot.id, false);
      return;
    }

    if (spot.id === "home_return") {
      flyCamera(new THREE.Vector3(0.0, 5.8, 16.0), new THREE.Vector3(0.0, 4.4, 2.0), 480, () => {
        opts.onBackToHub?.();
      });
      return;
    }

    if (spot.id === "street") {
      opts.onTeleportStreet?.();
    }
  }

  // Pointer gaze tracking, raycast click on 3D Bruce, Click-to-Walk central corridor & Trick Bar
  const raycaster = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  const floorPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -FLOOR_Y);
  const floorHit = new THREE.Vector3();
  const WAREHOUSE_WALK_SPOTS = [
    [-0.35, 4.2],
    [1.1, 0.4],
    [-1.2, -4.6],
    [0.8, 7.6],
  ];
  let walkSpotCursor = 0;
  let pokeCount = 0;
  let canvasDown = null;

  const trickButtons = Array.from(container.querySelectorAll(".trick-pill[data-trick]"));
  function highlightTrickBtn(trickId) {
    trickButtons.forEach((b) => b.classList.toggle("is-playing", b.getAttribute("data-trick") === trickId));
    later(() => {
      trickButtons.forEach((b) => {
        if (b.getAttribute("data-trick") === trickId) b.classList.remove("is-playing");
      });
    }, 2400);
  }

  function walkBruceTo(rawX, rawZ) {
    const tx = THREE.MathUtils.clamp(rawX, -2.0, 2.0);
    const tz = THREE.MathUtils.clamp(rawZ, -8.0, 10.0);
    triggerFloorRipple(tx, tz);
    bruce.walkTo(tx, tz, { speedScale: sulking ? 0.65 : 1.0 });
    sayBruce(sulking ? "walk_sulk" : "walk_call", 3400);
  }

  function runTrick(trickId) {
    if (destroyed || activeActId) return;
    highlightTrickBtn(trickId);
    if (trickId === "walk") {
      walkSpotCursor = (walkSpotCursor + 1) % WAREHOUSE_WALK_SPOTS.length;
      const [wx, wz] = WAREHOUSE_WALK_SPOTS[walkSpotCursor];
      sfx.playTap();
      walkBruceTo(wx, wz);
      return;
    }
    if (trickId === "roll_over") sfx.playRollJoy();
    else if (trickId === "play_bow") sfx.playStretchSigh();
    else sfx.playTap();
    bruce.playAction(trickId);
    const rect = stageEl.getBoundingClientRect();
    spawnFxParticles(rect.width * 0.52, rect.height * 0.56, trickId === "airplane_ears" ? "water" : "gold", 14);
    sayBruce(trickId, 3800);
  }

  trickButtons.forEach((btn) => {
    const onTrickClick = (e) => {
      e.stopPropagation();
      setKeyholderOpen(false);
      feedback("small", e.clientX, e.clientY);
      runTrick(btn.getAttribute("data-trick"));
    };
    btn.addEventListener("click", onTrickClick);
    cleanups.push(() => btn.removeEventListener("click", onTrickClick));
  });

  const chatCleanup = mountBruceChatBar({
    stageEl,
    toggleBtn: container.querySelector("#hub3d-btn-chat"),
    getContext: () => ({
      scene: "warehouse",
      sulking,
      happiness,
      owner: opts.player?.owner,
      nickname: opts.player?.nickname,
    }),
    onAiResponse(res, showDelta) {
      if (destroyed) return;
      sayBruce(res.reply, 5400, res.cue || "BRUCE · 灵动回应");
      const act = res.action;
      if (act === "walk") {
        runTrick("walk");
      } else if (act && act !== "idle") {
        bruce.playAction(act);
        highlightTrickBtn(act);
        if (act === "roll_over") sfx.playRollJoy();
        else if (act === "play_bow") sfx.playStretchSigh();
      }
      if (res.sincerityDelta) {
        opts.onSincerityDelta?.(res.sincerityDelta)?.then((applied) => {
          if (applied) showDelta?.(applied);
        });
      }
    },
  });
  cleanups.push(chatCleanup);

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
    const bruceGroup = bruce.hitTarget || bruce.root.children[0];
    if (bruceGroup) {
      bruce.root.updateMatrixWorld(true);
      const hits = raycaster.intersectObject(bruceGroup, true);
      if (hits.length > 0) {
        feedback("small", e.clientX, e.clientY);
        const stageRect = stageEl.getBoundingClientRect();
        spawnFxParticles(e.clientX - stageRect.left, e.clientY - stageRect.top, sulking ? "water" : "gold", 14);
        if (sulking) {
          sfx.playTap();
          bruce.playAction("airplane_ears");
          highlightTrickBtn("airplane_ears");
          sayBruce("click_poke_sulk", 4200);
        } else {
          const cycle = ["roll_over", "play_bow", "lick_paw"];
          const chosen = cycle[pokeCount % cycle.length];
          pokeCount += 1;
          if (chosen === "roll_over") sfx.playRollJoy();
          else if (chosen === "play_bow") sfx.playStretchSigh();
          else sfx.playTap();
          bruce.playAction(chosen);
          highlightTrickBtn(chosen);
          sayBruce(chosen, 4000);
        }
        return;
      }
    }

    // Walkable terrazzo central aisle raycast -> Click-to-Walk (x in [-2.0, 2.0], z in [-8.0, 10.0])
    if (raycaster.ray.direction.y < -0.04 && raycaster.ray.intersectPlane(floorPlane, floorHit)) {
      if (floorHit.x >= -2.4 && floorHit.x <= 2.4 && floorHit.z >= -8.4 && floorHit.z <= 10.4) {
        sfx.playTap();
        walkBruceTo(floorHit.x, floorHit.z);
        highlightTrickBtn("walk");
      }
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
  const fxCtx = fxCanvas.getContext("2d");

  const tick = (now) => {
    if (destroyed) return;
    const dt = Math.min(0.05, (now - prevNow) / 1000);
    prevNow = now;
    const elapsed = now / 1000;

    const w = Math.max(300, stageEl.clientWidth);
    const h = Math.max(240, stageEl.clientHeight);
    const desiredFov = w / h < 0.95 ? 60 : w < 920 ? 55 : 50;
    if (
      canvas.width !== Math.round(w * renderer.getPixelRatio()) ||
      canvas.height !== Math.round(h * renderer.getPixelRatio()) ||
      camera.fov !== desiredFov
    ) {
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
      camera.position.x = THREE.MathUtils.clamp(camera.position.x, -7.2, 7.2);
      camera.position.y = THREE.MathUtils.clamp(camera.position.y, 2.2, 13.4);
      camera.position.z = THREE.MathUtils.clamp(camera.position.z, -14.0, 16.8);
    }

    if (motePoints.visible) {
      const arr = moteGeo.attributes.position.array;
      for (let i = 0; i < moteCount; i++) {
        arr[i * 3 + 1] += dt * 0.22;
        if (arr[i * 3 + 1] > 14.2) arr[i * 3 + 1] = 2.0;
      }
      moteGeo.attributes.position.needsUpdate = true;
    }
    if (rainPoints.visible) {
      const arr = rainGeo.attributes.position.array;
      for (let i = 0; i < rainCount; i++) {
        arr[i * 3 + 1] -= dt * 11.5;
        if (arr[i * 3 + 1] < 10.5) arr[i * 3 + 1] = 17.8;
      }
      rainGeo.attributes.position.needsUpdate = true;
    }

    if (cartLootGroup.visible) {
      cartLootGroup.rotation.y += dt * 0.9;
    }

    if (swapRingsGroup.visible) {
      swapRingsGroup.position.set(bruce.root.position.x, bruce.root.position.y + 1.1, bruce.root.position.z);
      swapRingsGroup.rotation.y += dt * 1.4;
      swapRingsGroup.children.forEach((c, idx) => {
        c.rotation.z += dt * (0.6 + idx * 0.25);
      });
    }

    if (rippleAge >= 0) {
      rippleAge += dt;
      const p = rippleAge / 0.85;
      if (p >= 1) {
        rippleAge = -1;
        rippleMesh.visible = false;
      } else {
        rippleMesh.scale.setScalar(0.6 + p * 2.2);
        rippleMat.opacity = (1 - p) * 0.82;
      }
    }

    bruce.update(dt, elapsed);
    const rigDiag = bruce.getDiag?.();
    if (rigDiag) stageEl.dataset.rigDiag = JSON.stringify(rigDiag);
    renderer.render(scene, camera);

    const diagObj = {
      calls: renderer.info.render.calls,
      triangles: renderer.info.render.triangles,
      geometries: renderer.info.memory.geometries,
      textures: renderer.info.memory.textures,
      dpr: renderer.getPixelRatio(),
      loaded: loadingEl.classList.contains("is-hidden"),
    };
    window.__BRUCE_WAREHOUSE_DIAG__ = diagObj;
    if (Math.floor(elapsed * 2) !== Math.floor((elapsed - dt) * 2)) {
      stageEl.dataset.diag = JSON.stringify(diagObj);
    }

    const minPinTop = w < 640 ? 136 : 96;
    if (speechEl) {
      const hideForSettle = settleEl.classList.contains("is-visible") || swapBanner.classList.contains("is-visible");
      speechEl.style.display = hideForSettle ? "none" : "";
    }

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
      applyAtmosphere(nextSulk);
      sfx.setSceneAmbience("warehouse", { sulking: nextSulk });
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
      sfx.clearSceneAmbience("warehouse");
      delete window.__BRUCE_WAREHOUSE_DIAG__;
      document.body.classList.remove("is-hub3d-view", "is-hub3d-act");
      if (rafId) cancelAnimationFrame(rafId);
      actCleanup?.();
      timers.forEach((t) => clearTimeout(t));
      timers.clear();
      cleanups.forEach((fn) => fn());
      cleanups.length = 0;
      bruce.destroy();
      controls.dispose();
      envRT.dispose();
      moteGeo.dispose();
      moteMat.dispose();
      rainGeo.dispose();
      rainMat.dispose();
      plateGeo.dispose();
      plateMat.dispose();
      salmonCubeGeo.dispose();
      salmonCubeMat.dispose();
      lootBoxGeo.dispose();
      lootBoxMat.dispose();
      lootLidGeo.dispose();
      lootLidMat.dispose();
      rippleGeo.dispose();
      rippleMat.dispose();
      swapRingGeos.forEach((g) => g.dispose());
      swapRingMats.forEach((m) => m.dispose());
      if (warehouseRoot) {
        warehouseRoot.traverse((obj) => {
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

export const mountScene = mountWarehouseHub;
