import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { createLivingBruce } from "../hub3d/bruceLiving.js";
import { mountBruceChatBar } from "../hub3d/bruceChatUi.js";
import { sfx } from "../audio.js";
import { feedback } from "../juice.js";

const OVERVIEW_CAM = new THREE.Vector3(-1.5, 5.8, 20.2);
const OVERVIEW_TARGET = new THREE.Vector3(1.1, 4.5, -4.2);
const FLOOR_Y = 0.0;

const BRUCE_HOME_POS = new THREE.Vector3(-1.35, FLOOR_Y, 3.2);
const BRUCE_HOME_ROT = 0.16;

const ACTIVITY_DEFS = {
  street_cafe: {
    id: "street_cafe",
    title: "手冲吧台 · 山羊奶微泡",
    win: 13,
    fail: -14,
    swapProb: 0.15,
    camPos: new THREE.Vector3(-0.6, 5.5, 9.6),
    camTarget: new THREE.Vector3(3.8, 4.2, 2.2),
    brucePos: new THREE.Vector3(0.45, FLOOR_Y, 3.85),
    bruceRot: 1.32,
  },
  street_window: {
    id: "street_window",
    title: "烘焙台 · 海盐黑麦脆片",
    win: 12,
    fail: -13,
    swapProb: 0.12,
    camPos: new THREE.Vector3(0.4, 5.2, 7.6),
    camTarget: new THREE.Vector3(3.6, 4.6, 2.2),
    brucePos: new THREE.Vector3(0.55, FLOOR_Y, 2.65),
    bruceRot: 1.42,
  },
  street_walk: {
    id: "street_walk",
    title: "海风窗畔晒毛",
    win: 12,
    fail: -13,
    swapProb: 0.1,
    camPos: new THREE.Vector3(-1.2, 4.6, 10.6),
    camTarget: new THREE.Vector3(-6.8, 3.0, 4.4),
    brucePos: new THREE.Vector3(-3.8, FLOOR_Y, 6.8),
    bruceRot: -1.32,
  },
};

const HOTSPOTS = [
  {
    id: "street_cafe",
    kind: "act",
    title: "吧台羊奶微泡",
    sub: "+13 分 · 15% 换分",
    pos: [4.2, 3.2, 5.4],
    icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 10h10v5a5 5 0 0 1-10 0v-5z"/><path d="M15 11h2a2.5 2.5 0 0 1 0 5h-2"/><path d="M8 5c0 1.2 1 1.5 1 2.6M12 4.5c0 1.2 1 1.5 1 2.6"/></svg>`,
  },
  {
    id: "street_window",
    kind: "act",
    title: "烘焙海盐脆片",
    sub: "+12 分 · 12% 换分",
    pos: [3.8, 5.6, 0.2],
    icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 14h16v5H4z"/><path d="M6 14a6 6 0 0 1 12 0"/><path d="M9 11h6"/></svg>`,
  },
  {
    id: "street_walk",
    kind: "act",
    title: "海风窗畔晒毛",
    sub: "+12 分 · 10% 换分",
    pos: [-5.5, 4.7, 0.8],
    icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M2 12h3M19 12h3"/></svg>`,
  },
  {
    id: "home_return",
    kind: "teleport",
    title: "返回 · 阳光客厅",
    sub: "回到双层复式家",
    code: "HOME·00",
    pos: [-5.4, 8.0, -9.0],
    icon: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 10.5L12 3l9 7.5"/><path d="M6 9.5V20h12V9.5"/></svg>`,
  },
  {
    id: "warehouse",
    kind: "teleport",
    title: "下一站 · ELOWEN 有机市集",
    sub: "野生帝王鲑与冷柜鲜食",
    code: "ELW·02",
    pos: [4.2, 9.0, -10.5],
    icon: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="9" cy="19" r="1.5"/><circle cx="17" cy="19" r="1.5"/><path d="M3 5h3l2.2 10h9.8l2-7H7"/></svg>`,
  },
];

const DEFAULT_CAFE_COPY = {
  idle_happy: [
    "海平线刚好压在橡木长台这一线，今天这杯无糖山羊奶微泡水温刚刚好。",
    "坐在靠海石灰岩地面这一排，海风把奶油长毛的尾尖吹得蓬蓬的。",
    "听见铜壳小批烘豆机低低沙沙响着，午后一小时就这样慢下来了。",
  ],
  idle_sulk: [
    "幸福指数低于 80 了，我现在连海平线都不想看，快带我回家哄一哄。",
    "外面飘起海雾小雨，本汪的山羊奶微泡也没心情喝了，哼。",
  ],
  click_poke: [
    "在烘焙室也要保持从容仪态，别把暗酒红真丝领巾戳歪啦。",
    "嘿嘿，听到分享壶倒咖啡的微响，尾巴已经轻轻摇起来了。",
    "光斑正斜斜落在白瓷杯和海景银盐照上，帮我拍一张胶片吧。",
  ],
  click_poke_sulk: [
    "冷战期的小狗在这里也很克制……除非端来两块黑麦海盐脆片。",
    "别戳了，等幸福指数回到 80 再陪你吹海风。",
  ],
  bar_bliss: [
    "绵密的无糖山羊奶微泡，鼻尖沾了一圈白绒绒也太舒服啦。",
    "陶瓷滤杯手冲旁搭一小碟温热奶泡，完美。",
  ],
  ear_warn: [
    "哇！手写单牌靠太近了，飞机耳预警，先停一秒缓一缓！",
  ],
  walk_call: [
    "小爪子踩着哑光石灰岩地砖哒哒过来，帮我留好窗边那张矮凳。",
    "绕过白橡木长台慢慢晃过来，顺路闻闻烘豆的坚果焦香。",
  ],
  walk_sulk: [
    "起雾的海边有点懒懒的……好吧，我挪过去一点点。",
  ],
  roll_over: [
    "趁太阳正斜照在石灰岩砖面上翻个滚，整间烘焙室只有海浪声。",
    "肚皮翻出来晒一晒海风微光，一天里最松弛的二十分钟。",
  ],
  lick_paw: [
    "细细舔干净前爪沾到的山羊奶泡，接着把小碟里的两块黑麦脆片推过来吧。",
    "舔两口右前爪，鼻尖还留着一点浅焙豆和海盐黄油香。",
  ],
  play_bow: [
    "对着落地无框玻璃海景伸个大懒腰，尾巴摇成温柔节拍器。",
    "前爪压低对你发出邀请信号，去窗边看远方那艘白帆船吗？",
  ],
  airplane_ears: [
    "海风声拍打落地玻璃，本汪先折个标准飞机耳听会儿涛声。",
  ],
};

function pickRandom(arr, fallback = "") {
  if (!Array.isArray(arr) || !arr.length) return fallback;
  return arr[Math.floor(Math.random() * arr.length)];
}

export function mountCoastalCafeHub(container, opts = {}) {
  let sulking = Boolean(opts.sulking);
  let content = opts.content || {};
  let happiness = opts.happiness ?? 100;
  let cafeCopy = DEFAULT_CAFE_COPY;
  let hubCopy = null;

  document.body.classList.add("is-hub3d-view");
  document.body.classList.remove("is-hub3d-act");

  fetch("./data/hub_deepseek.json")
    .then((r) => (r.ok ? r.json() : null))
    .then((json) => {
      if (!destroyed && json) {
        hubCopy = json;
        if (json.cafe_thought_bubbles) {
          cafeCopy = { ...DEFAULT_CAFE_COPY, ...json.cafe_thought_bubbles };
        }
        if (Array.isArray(json.cafe_boiserie_lines) && json.cafe_boiserie_lines.length) {
          cafeCopy = {
            ...cafeCopy,
            idle_happy: [...(cafeCopy.idle_happy || []), ...json.cafe_boiserie_lines],
          };
        }
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
          <span class="vf-stamp">35MM · MALIBU ROASTERY · F/1.8</span>
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
              <span>CAFÉ PASS HOLDER</span>
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
            <button type="button" class="hub3d-glass-pill" id="hub3d-btn-back">回到咖啡馆全景</button>
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
            <button type="button" class="th-btn-ghost" id="hub3d-btn-done">回到咖啡馆全景</button>
          </div>
        </section>

        <div class="hub3d-loading">
          <span>正在推开海岸咖啡馆玻璃门……</span>
        </div>
      </div>
      <p class="hub3d-hint">拖动环视海岸咖啡馆 · 点黄铜光点体验吧台，左下「通行钥匙夹」可返回客厅</p>
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
  renderer.toneMappingExposure = 0.94;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(sulking ? 0x3b4d63 : 0x7cb8e8);

  // Coastal PMREM Environment Map so marble, glass, ceramic planters, and black steel read crisply
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene();
  envScene.background = new THREE.Color(0xe6dfd4);
  const envBox = new THREE.Mesh(
    new THREE.BoxGeometry(26, 18, 26),
    new THREE.MeshBasicMaterial({ color: 0xe3dcd0, side: THREE.BackSide }),
  );
  const envSkyLeft = new THREE.Mesh(
    new THREE.PlaneGeometry(24, 15),
    new THREE.MeshBasicMaterial({ color: 0xaed7ff }),
  );
  envSkyLeft.position.set(-12.5, 4, 0);
  envSkyLeft.rotation.y = Math.PI * 0.5;
  const envSkyBack = new THREE.Mesh(
    new THREE.PlaneGeometry(24, 15),
    new THREE.MeshBasicMaterial({ color: 0xc2e2ff }),
  );
  envSkyBack.position.set(0, 4, -12.5);
  const envOakCeil = new THREE.Mesh(
    new THREE.PlaneGeometry(24, 24),
    new THREE.MeshBasicMaterial({ color: 0xebd8b8 }),
  );
  envOakCeil.position.set(0, 8.8, 0);
  envOakCeil.rotation.x = Math.PI * 0.5;
  envScene.add(envBox, envSkyLeft, envSkyBack, envOakCeil);
  const envRT = pmrem.fromScene(envScene, 0.04);
  scene.environment = envRT.texture;
  scene.environmentIntensity = 0.56;
  pmrem.dispose();
  [envBox, envSkyLeft, envSkyBack, envOakCeil].forEach((m) => {
    m.geometry.dispose();
    m.material.dispose();
  });

  const camera = new THREE.PerspectiveCamera(50, 16 / 10, 0.25, 180);
  camera.position.copy(OVERVIEW_CAM);

  const controls = new OrbitControls(camera, canvas);
  controls.target.copy(OVERVIEW_TARGET);
  controls.enableDamping = true;
  controls.dampingFactor = 0.07;
  controls.enablePan = false;
  controls.minDistance = 6.0;
  controls.maxDistance = 26.5;
  controls.minPolarAngle = 0.55;
  controls.maxPolarAngle = 1.54;
  controls.minAzimuthAngle = -Infinity;
  controls.maxAzimuthAngle = Infinity;
  controls.update();

  // Coastal Daylight + Warm Bar/Pendant Lighting Rig
  const hemiLight = new THREE.HemisphereLight(0xfffaf2, 0xa8b6a2, 0.85);
  scene.add(hemiLight);

  const ambientLight = new THREE.AmbientLight(0xfffaf2, 0.26);
  scene.add(ambientLight);

  const sunLight = new THREE.DirectionalLight(0xfff1d6, 1.55);
  sunLight.position.set(-22, 16, -6);
  sunLight.target.position.set(2, 1.5, -2);
  sunLight.castShadow = true;
  sunLight.shadow.mapSize.set(1024, 1024);
  sunLight.shadow.camera.near = 4;
  sunLight.shadow.camera.far = 52;
  sunLight.shadow.camera.left = -22;
  sunLight.shadow.camera.right = 22;
  sunLight.shadow.camera.top = 18;
  sunLight.shadow.camera.bottom = -18;
  sunLight.shadow.bias = -0.0005;
  scene.add(sunLight, sunLight.target);

  const barGlowLight = new THREE.PointLight(0xffd79e, 1.35, 22, 1.3);
  barGlowLight.position.set(4.5, 8.8, 2.5);
  scene.add(barGlowLight);

  const loungeFillLight = new THREE.PointLight(0xfff3de, 0.72, 22, 1.4);
  loungeFillLight.position.set(-5.0, 9.5, -2.0);
  scene.add(loungeFillLight);

  // Warm wash illuminating the South Roastery Boiserie & Walnut Bookcase Wall (Z=+20.2) for 360° orbit
  const southBoiserieLight = new THREE.PointLight(0xffe1b5, 1.05, 24, 1.35);
  southBoiserieLight.position.set(1.2, 8.8, 13.8);
  scene.add(southBoiserieLight);

  // Subtle architectural glass panes fitted into left & back curtain wall openings
  const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0xd9f0ff,
    metalness: 0.0,
    roughness: 0.08,
    transparent: true,
    opacity: 0.11,
    clearcoat: 1.0,
    envMapIntensity: 1.4,
    depthWrite: false,
  });
  const leftGlassGeo = new THREE.PlaneGeometry(31.6, 13.8);
  const leftGlass = new THREE.Mesh(leftGlassGeo, glassMat);
  leftGlass.position.set(-11.4, 7.05, -4.8);
  leftGlass.rotation.y = Math.PI * 0.5;
  const backGlassGeo = new THREE.PlaneGeometry(11.6, 13.8);
  const backGlass = new THREE.Mesh(backGlassGeo, glassMat);
  backGlass.position.set(-5.0, 7.05, -21.8);
  scene.add(leftGlass, backGlass);

  // Sunlit motes & exterior coastal rain (for sulk mode)
  const moteCount = 34;
  const motePos = new Float32Array(moteCount * 3);
  for (let i = 0; i < moteCount; i++) {
    motePos[i * 3] = -9 + ((i * 2.13) % 16);
    motePos[i * 3 + 1] = 1.6 + ((i * 1.91) % 9);
    motePos[i * 3 + 2] = -14 + ((i * 2.47) % 22);
  }
  const moteGeo = new THREE.BufferGeometry();
  moteGeo.setAttribute("position", new THREE.BufferAttribute(motePos, 3));
  const moteMat = new THREE.PointsMaterial({
    color: 0xfff5d8,
    size: 0.14,
    transparent: true,
    opacity: 0.52,
    depthWrite: false,
  });
  const motePoints = new THREE.Points(moteGeo, moteMat);
  scene.add(motePoints);

  const rainCount = 110;
  const rainPos = new Float32Array(rainCount * 3);
  for (let i = 0; i < rainCount; i++) {
    const onLeft = i % 2 === 0;
    rainPos[i * 3] = onLeft ? -13.2 - ((i * 0.71) % 4.0) : -12.0 + ((i * 1.37) % 14.0);
    rainPos[i * 3 + 1] = 1.0 + ((i * 2.77) % 15.0);
    rainPos[i * 3 + 2] = onLeft ? -20.0 + ((i * 1.83) % 32.0) : -23.0 - ((i * 0.63) % 4.0);
  }
  const rainGeo = new THREE.BufferGeometry();
  rainGeo.setAttribute("position", new THREE.BufferAttribute(rainPos, 3));
  const rainMat = new THREE.PointsMaterial({
    color: 0xc2defa,
    size: 0.18,
    transparent: true,
    opacity: 0.72,
    depthWrite: false,
  });
  const rainPoints = new THREE.Points(rainGeo, rainMat);
  rainPoints.visible = sulking;
  scene.add(rainPoints);

  // 3D Pup Cup prop on marble bar counter (animated during street_cafe)
  const pupCupGroup = new THREE.Group();
  pupCupGroup.position.set(3.85, 4.44, 5.85);
  pupCupGroup.visible = false;
  const cupGeo = new THREE.CylinderGeometry(0.24, 0.18, 0.34, 16);
  const cupMat = new THREE.MeshStandardMaterial({ color: 0xfbf8f2, roughness: 0.28 });
  const cupMesh = new THREE.Mesh(cupGeo, cupMat);
  cupMesh.position.y = 0.17;
  cupMesh.castShadow = true;
  const foamGeo = new THREE.SphereGeometry(0.22, 14, 10);
  const foamMat = new THREE.MeshStandardMaterial({ color: 0xfffdf8, roughness: 0.65 });
  const foamMesh = new THREE.Mesh(foamGeo, foamMat);
  foamMesh.position.y = 0.35;
  foamMesh.scale.set(1, 0.65, 1);
  const swirlGeo = new THREE.ConeGeometry(0.11, 0.18, 12);
  const swirlMesh = new THREE.Mesh(swirlGeo, foamMat);
  swirlMesh.position.y = 0.51;
  pupCupGroup.add(cupMesh, foamMesh, swirlMesh);
  scene.add(pupCupGroup);

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

  // Living Bruce on the sunlit sage tile floor beside the front café table
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

  // Tracked shader materials from GLB
  let palmShaderMat = null;
  let coastMatRef = null;
  let globeMatRef = null;
  let underBarMatRef = null;
  let cafeRoot = null;

  const gltfLoader = new GLTFLoader();
  const cafeReady = new Promise((resolve) => {
    gltfLoader.load(
      "./assets/models/coastal_cafe.glb",
      (gltf) => {
        if (destroyed) return;
        cafeRoot = gltf.scene;
        cafeRoot.traverse((obj) => {
          if (!obj.isMesh) return;
          const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
          const matName = mats[0]?.name || obj.name || "";

          // Backdrop & translucent curtains shouldn't cast opaque shadows
          if (matName === "CoastalBackdrop" || matName === "SheerCurtain" || matName === "PastryGlass") {
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

            if (m.name === "CoastalBackdrop") {
              const basicCoast = new THREE.MeshBasicMaterial({
                map: m.map,
                side: THREE.DoubleSide,
                color: sulking ? 0x6e85a0 : 0xffffff,
                toneMapped: false,
              });
              obj.material = basicCoast;
              coastMatRef = basicCoast;
              m.dispose();
            } else if (m.name === "PendantGlobe") {
              globeMatRef = m;
              m.emissiveIntensity = sulking ? 1.8 : 1.35;
            } else if (m.name === "UnderBarLed") {
              underBarMatRef = m;
              m.emissiveIntensity = sulking ? 1.9 : 1.2;
            } else if (m.name === "LinearLed") {
              m.emissiveIntensity = 1.4;
            } else if (m.name === "PalmFronds") {
              palmShaderMat = m;
              m.onBeforeCompile = (shader) => {
                shader.uniforms.uTime = { value: 0 };
                m.userData.shader = shader;
                shader.vertexShader =
                  "uniform float uTime;\n" +
                  shader.vertexShader.replace(
                    "#include <begin_vertex>",
                    `#include <begin_vertex>
                     float sway = sin(uTime * 1.4 + position.x * 0.35 + position.z * 0.25) * 0.14;
                     transformed.x += sway;
                     transformed.y += cos(uTime * 1.1 + position.z * 0.4) * 0.06;`,
                  );
              };
              m.customProgramCacheKey = () => "cafe-palm-sway-v1";
            }
            m.needsUpdate = true;
          });
        });
        scene.add(cafeRoot);
        resolve(true);
      },
      undefined,
      (err) => {
        console.warn("coastal_cafe.glb load error:", err);
        resolve(false);
      },
    );
  });

  Promise.all([cafeReady, bruce.ready]).then(() => {
    if (!destroyed) {
      loadingEl.classList.add("is-hidden");
      later(() => {
        if (!activeActId) sayBruce(sulking ? "idle_sulk" : "idle_happy", 4400);
      }, 900);
    }
  });

  const CAFE_SPEECH_CUES = {
    idle_happy: "BRUCE · 海风絮语",
    idle_sulk: "BRUCE · 雨窗冷战中",
    click_poke: "BRUCE · 丝巾晃动",
    click_poke_sulk: "BRUCE · 别扭哼声",
    bar_bliss: "BRUCE · 舔奶泡中",
    ear_warn: "BRUCE · 飞机耳预警",
    walk_call: "BRUCE · 小短腿巡店",
    walk_sulk: "BRUCE · 缓慢挪步",
    roll_over: "BRUCE · 晒日打滚",
    lick_paw: "BRUCE · 舔干净奶泡",
    play_bow: "BRUCE · 窗边伸懒腰",
    airplane_ears: "BRUCE · 海风飞机耳",
  };

  let speechTimer = null;
  let lastSpeechText = "";
  let lastSpeechAt = 0;
  function sayBruce(categoryOrText, durationMs = 3800, customCue = "") {
    if (!speechEl || !speechLineEl || destroyed) return;
    const pool = cafeCopy?.[categoryOrText];
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
      speechCueEl.textContent = customCue || CAFE_SPEECH_CUES[categoryOrText] || (sulking ? "BRUCE · 雨窗冷战中" : "BRUCE · 吧台轻哼");
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

  // Build breathing brass dots (in-scene activities) & keyholder passes (teleports)
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
        sayBruce("玩够了就点这里回阳光客厅的毛毯上打盹吧！", 3200, "BRUCE · 门边张望");
      } else {
        const line = hubCopy?.portal_hover?.[spot.id];
        if (line) sayBruce(line, 3400, "BRUCE · 门边张望");
      }
    });
  });

  function applyAtmosphere(sulkMode) {
    sulking = Boolean(sulkMode);
    vignetteEl.classList.toggle("is-sulk", sulking);
    rainPoints.visible = sulking;
    motePoints.visible = !sulking;

    if (sulking) {
      scene.background.setHex(0x304258);
      hemiLight.color.setHex(0x9ab4d2);
      hemiLight.groundColor.setHex(0x525c62);
      hemiLight.intensity = 0.65;
      sunLight.intensity = 0.38;
      ambientLight.intensity = 0.25;
      barGlowLight.intensity = 1.9;
      loungeFillLight.intensity = 0.95;
      if (coastMatRef) {
        coastMatRef.color.setHex(0x6e85a0);
      }
      if (globeMatRef) globeMatRef.emissiveIntensity = 1.85;
      if (underBarMatRef) underBarMatRef.emissiveIntensity = 1.9;
      bruce.setMood("sulk");
    } else {
      scene.background.setHex(0x7cb8e8);
      hemiLight.color.setHex(0xfffaf2);
      hemiLight.groundColor.setHex(0xa8b6a2);
      hemiLight.intensity = 0.85;
      sunLight.intensity = 1.55;
      ambientLight.intensity = 0.26;
      barGlowLight.intensity = 1.35;
      loungeFillLight.intensity = 0.72;
      if (coastMatRef) {
        coastMatRef.color.setHex(0xffffff);
      }
      if (globeMatRef) globeMatRef.emissiveIntensity = 1.35;
      if (underBarMatRef) underBarMatRef.emissiveIntensity = 1.2;
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
    pupCupGroup.visible = false;
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
    sfx.setSceneAmbience("cafe", { sulking });
    stageEl.dataset.soundscapeDiag = JSON.stringify({ scene: "cafe", sulking, muted: sfx.muted });
    flyCamera(OVERVIEW_CAM, OVERVIEW_TARGET, 650);
  }

  btnActBack.addEventListener("click", () => {
    sfx.playTap();
    exitActivity();
  });

  btnReplay.addEventListener("click", () => {
    if (sulking || !activeActId) return;
    sfx.playTap();
    startCafeActivity(activeActId, false);
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

  function startCafeActivity(actId, autoplay = false) {
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
    pupCupGroup.visible = actId === "street_cafe";
    pupCupGroup.position.set(3.85, 4.44, 5.85);

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
      startCafeActivity(actId, !autoplay);
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
        if (actId === "street_cafe") {
          bruce.playAction("lick_paw");
        } else if (actId === "street_walk") {
          bruce.playAction("play_bow");
        } else if (Math.random() < 0.6) {
          bruce.playAction("roll_over");
        } else {
          bruce.triggerHappyHop();
        }
        const r = stageEl.getBoundingClientRect();
        spawnFxParticles(r.width * 0.5, r.height * 0.48, "gold", 22);
      } else {
        sfx.playFail();
        bruce.setMood("sulk");
        bruce.playAction("airplane_ears");
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
        isWin ? "布鲁斯坐在阳光吧台前舔完最后一口奶泡，满意地晃着尾巴。" : "布鲁斯被突发状况吓了一跳，默默把领巾蹭歪了。",
      );

      settleEl.querySelector(".hub3d-settle-title").textContent =
        outcome === "win" ? "探店成功" : outcome === "phone_fail" ? "被手机抢走了" : "踩到雷点了";
      const deltaEl = settleEl.querySelector(".hub3d-settle-delta");
      deltaEl.textContent = `${delta >= 0 ? "+" : ""}${delta}`;
      deltaEl.classList.toggle("is-neg", delta < 0);
      settleEl.querySelector(".hub3d-settle-line").textContent = summaryLine;
      const statusEl = settleEl.querySelector(".hub3d-settle-status");
      statusEl.textContent = "正在同步幸福指数……";

      const projected = Math.max(0, happiness + delta);
      btnReplay.hidden = projected < 80;
      btnDone.textContent = projected < 80 ? "去私厨鲜食柜" : "回到咖啡馆全景";
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
          btnDone.textContent = "回到咖啡馆全景";
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

    actLater(() => triggerPhone(false), 1800 + Math.random() * 1400);

    // 3 Café-specific 3D interactions
    if (actId === "street_cafe") {
      actPromptEl.textContent = "按顺序为布鲁斯特调：现磨香气 → 鲜打奶泡 → 端上吧台";
      actBodyEl.innerHTML = `
        <div class="hub3d-props-row">
          <button type="button" class="hub3d-prop-btn" data-prop="grind">GRIND · 现磨香气</button>
          <button type="button" class="hub3d-prop-btn" data-prop="whip">WHIP · 鲜打奶泡</button>
          <button type="button" class="hub3d-prop-btn" data-prop="serve">SERVE · 端给布鲁斯</button>
        </div>
        <button type="button" class="hub3d-hazard-btn">ESPRESSO · 浓咖误喂</button>
      `;
      const order = ["grind", "whip", "serve"];
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
        spawnFxParticles(r.width * 0.56, r.height * 0.5, step === 3 ? "gold" : "warm", 18);
        if (step === 1) {
          actPromptEl.textContent = "咖啡豆磨好啦，接着打出绵密宠物奶泡";
        } else if (step === 2) {
          pupCupGroup.position.set(3.55, 4.44, 4.85);
          sayBruce("bar_bliss", 3000);
          actPromptEl.textContent = "奶泡打好啦！端到布鲁斯面前的吧台边缘";
        } else {
          pupCupGroup.position.set(3.25, 4.44, 3.85);
          bruce.playAction("lick_paw");
          sayBruce("bar_bliss", 3000);
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
    } else if (actId === "street_window") {
      actPromptEl.textContent = "轻拭白橡木烘焙台面，替布鲁斯挑两块黑麦海盐脆片";
      actBodyEl.innerHTML = `
        <div class="hub3d-brush-zone"></div>
        <div class="hub3d-progress"><div class="hub3d-progress-fill"></div></div>
        <button type="button" class="hub3d-hazard-btn">NO DOGS · 禁入贴</button>
      `;
      const zone = actBodyEl.querySelector(".hub3d-brush-zone");
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
        fill.style.width = `${(progress / TARGET) * 100}%`;
        bruce.setPetting(0.9);
        bruce.setMood("excited");
        const rect = stageEl.getBoundingClientRect();
        spawnFxParticles(cx - rect.left, cy - rect.top, "gold", 3);
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
          sayBruce("ear_warn", 2600);
          vignetteEl.classList.add("is-warn");
          actPromptEl.textContent = "玻璃反光惊到耳朵啦！先停手等 1 秒";
          actLater(() => {
            warning = false;
            bruce.setMood("happy");
            vignetteEl.classList.remove("is-warn");
            actPromptEl.textContent = "布鲁斯继续贴窗挑选，轻划完成";
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
          stroke(420, 28, r.left + r.width * 0.52, r.top + r.height * 0.5);
          actLater(autoStep, 650);
        };
        actLater(autoStep, 750);
      }
    } else if (actId === "street_walk") {
      actPromptEl.textContent = "带布鲁斯去海景落地窗晒太阳：吹海风 → 侧颜定格 → 赏小饼干";
      actBodyEl.innerHTML = `
        <div class="hub3d-props-row">
          <button type="button" class="hub3d-prop-btn" data-prop="breeze">BREEZE · 迎海风</button>
          <button type="button" class="hub3d-prop-btn" data-prop="pose">POSE · 侧颜45°</button>
          <button type="button" class="hub3d-prop-btn" data-prop="treat">TREAT · 赏小饼干</button>
        </div>
        <button type="button" class="hub3d-hazard-btn">SCOOTER · 露台电铃</button>
      `;
      const order = ["breeze", "pose", "treat"];
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
        spawnFxParticles(r.width * 0.45, r.height * 0.54, step === 1 ? "warm" : "gold", 18);
        if (step === 1) {
          actPromptEl.textContent = "海风吹起酒红丝巾啦，快给它抓拍侧颜 45°";
        } else if (step === 2) {
          sayBruce("click_poke", 3000);
          actPromptEl.textContent = "大片定格成功！掰一块无糖小饼干奖励";
        } else {
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
    }

    actCleanup = () => {
      finished = true;
      actTimers.forEach((t) => clearTimeout(t));
      actTimers.clear();
      actListeners.forEach((fn) => fn());
      actListeners.length = 0;
      pupCupGroup.visible = false;
    };
  }

  function handleHotspotClick(spot) {
    if (spot.kind === "act") {
      if (sulking) {
        opts.onOpenShop?.();
        return;
      }
      startCafeActivity(spot.id, false);
      return;
    }

    if (spot.id === "home_return") {
      flyCamera(new THREE.Vector3(-0.4, 5.8, 17.5), new THREE.Vector3(-0.2, 4.6, 4.0), 480, () => {
        opts.onBackToHub?.();
      });
      return;
    }

    if (spot.id === "warehouse") {
      opts.onTeleportWarehouse?.();
    }
  }

  // Pointer gaze tracking, raycast click on 3D Bruce, Click-to-Walk floor & Trick Bar
  const raycaster = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  const floorPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -FLOOR_Y);
  const floorHit = new THREE.Vector3();
  const CAFE_WALK_SPOTS = [
    [-1.35, 3.2],
    [-0.4, 7.6],
    [0.2, 0.6],
    [-2.4, 8.8],
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
    const tz = THREE.MathUtils.clamp(rawZ, -5.2, 11.0);
    const tx = tz >= 7.2
      ? THREE.MathUtils.clamp(rawX, -3.8, 2.1)
      : THREE.MathUtils.clamp(rawX, -1.6, 0.55);
    triggerFloorRipple(tx, tz);
    bruce.walkTo(tx, tz, { speedScale: sulking ? 0.65 : 1.0 });
    sayBruce(sulking ? "walk_sulk" : "walk_call", 3400);
  }

  function runTrick(trickId) {
    if (destroyed || activeActId) return;
    highlightTrickBtn(trickId);
    if (trickId === "walk") {
      walkSpotCursor = (walkSpotCursor + 1) % CAFE_WALK_SPOTS.length;
      const [wx, wz] = CAFE_WALK_SPOTS[walkSpotCursor];
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
      scene: "cafe",
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

    // Walkable sage tile corridor raycast -> Click-to-Walk
    if (raycaster.ray.direction.y < -0.04 && raycaster.ray.intersectPlane(floorPlane, floorHit)) {
      if (floorHit.x >= -5.4 && floorHit.x <= 3.0 && floorHit.z >= -6.0 && floorHit.z <= 12.0) {
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
    const desiredFov = w / h < 0.95 ? 62 : w < 920 ? 56 : 50;
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
      camera.position.x = THREE.MathUtils.clamp(camera.position.x, -9.8, 9.8);
      camera.position.y = THREE.MathUtils.clamp(camera.position.y, 2.2, 13.8);
      camera.position.z = THREE.MathUtils.clamp(camera.position.z, -16.5, 18.2);
    }

    if (palmShaderMat?.userData?.shader) {
      palmShaderMat.userData.shader.uniforms.uTime.value = elapsed;
    }

    if (motePoints.visible) {
      const arr = moteGeo.attributes.position.array;
      for (let i = 0; i < moteCount; i++) {
        arr[i * 3 + 1] += dt * 0.25;
        if (arr[i * 3 + 1] > 11.5) arr[i * 3 + 1] = 1.6;
      }
      moteGeo.attributes.position.needsUpdate = true;
    }
    if (rainPoints.visible) {
      const arr = rainGeo.attributes.position.array;
      for (let i = 0; i < rainCount; i++) {
        arr[i * 3 + 1] -= dt * 11.5;
        if (arr[i * 3 + 1] < 0.8) arr[i * 3 + 1] = 16.0;
      }
      rainGeo.attributes.position.needsUpdate = true;
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

    // Expose live renderer diagnostics for QA budget checks
    const diagObj = {
      calls: renderer.info.render.calls,
      triangles: renderer.info.render.triangles,
      geometries: renderer.info.memory.geometries,
      textures: renderer.info.memory.textures,
      dpr: renderer.getPixelRatio(),
      loaded: loadingEl.classList.contains("is-hidden"),
      setOrbitPose: (pos, target) => {
        camTween = null;
        camera.position.fromArray(pos);
        controls.target.fromArray(target);
        controls.update();
      },
    };
    window.__BRUCE_CAFE_DIAG__ = diagObj;
    if (Math.floor(elapsed * 2) !== Math.floor((elapsed - dt) * 2)) {
      stageEl.dataset.diag = JSON.stringify(diagObj);
    }

    // Hide cinema subtitle when settle modal or swap celebration banner is shown
    const minPinTop = w < 640 ? 158 : 116;
    if (speechEl) {
      const hideForSettle = settleEl.classList.contains("is-visible") || swapBanner.classList.contains("is-visible");
      speechEl.style.display = hideForSettle ? "none" : "";
    }

    // Project 3D hotspots to 2D overlay
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
      sfx.setSceneAmbience("cafe", { sulking: nextSulk });
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
      sfx.clearSceneAmbience("cafe");
      delete window.__BRUCE_CAFE_DIAG__;
      document.body.classList.remove("is-hub3d-view", "is-hub3d-act");
      if (rafId) cancelAnimationFrame(rafId);
      actCleanup?.();
      timers.forEach((t) => clearTimeout(t));
      timers.clear();
      cleanups.forEach((fn) => fn());
      cleanups.length = 0;
      bruce.destroy();
      controls.dispose();
      leftGlassGeo.dispose();
      backGlassGeo.dispose();
      glassMat.dispose();
      envRT.dispose();
      moteGeo.dispose();
      moteMat.dispose();
      rainGeo.dispose();
      rainMat.dispose();
      cupGeo.dispose();
      cupMat.dispose();
      foamGeo.dispose();
      foamMat.dispose();
      swirlGeo.dispose();
      rippleGeo.dispose();
      rippleMat.dispose();
      swapRingGeos.forEach((g) => g.dispose());
      swapRingMats.forEach((m) => m.dispose());
      if (cafeRoot) {
        cafeRoot.traverse((obj) => {
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
