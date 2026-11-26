import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { createLivingBruce } from "../hub3d/bruceLiving.js";

/**
 * 新 3D 传送场景标准模板（例如：海岸私家烘焙室 / ELOWEN 有机市集）
 * 协作者可复制本文件为 js/scenes3d/<scene>.js 并在 scene-preview.html?module=<scene> 中独立预览调试，
 * 无需修改 index.html、js/map.js 或 js/hub3d/*。
 */
export function mountScene(container, opts = {}) {
  let sulking = Boolean(opts.sulking);
  let destroyed = false;
  let rafId = null;

  container.innerHTML = `
    <div class="sc3d-wrap">
      <canvas class="sc3d-canvas"></canvas>
      <div class="sc3d-hud">
        <button type="button" class="sc3d-btn" id="sc3d-btn-back">返回 3D 客厅</button>
        <span class="sc3d-badge" id="sc3d-mood-tag">${sulking ? "冷战阴雨 (<80)" : "晴朗街区 · 3D 模板"}</span>
      </div>
      <div class="sc3d-footer-bar">
        <button type="button" class="sc3d-btn is-primary" id="sc3d-btn-interact">摸摸街角布鲁斯 (+14)</button>
      </div>
    </div>
  `;

  const wrap = container.querySelector(".sc3d-wrap");
  const canvas = container.querySelector(".sc3d-canvas");
  const moodTag = container.querySelector("#sc3d-mood-tag");

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.08;
  renderer.shadowMap.enabled = true;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(sulking ? 0x263547 : 0xdbe6de);

  const camera = new THREE.PerspectiveCamera(48, 16 / 10, 0.2, 120);
  camera.position.set(4.5, 4.2, 7.2);

  const controls = new OrbitControls(camera, canvas);
  controls.target.set(0, 1.4, 0);
  controls.enableDamping = true;
  controls.enablePan = false;
  controls.minDistance = 4.0;
  controls.maxDistance = 14.0;
  controls.maxPolarAngle = 1.45;
  controls.update();

  const hemi = new THREE.HemisphereLight(0xfffaf0, 0x9aa89c, 1.4);
  const sun = new THREE.DirectionalLight(0xffe7c2, 1.65);
  sun.position.set(6, 12, 5);
  sun.castShadow = true;
  scene.add(hemi, sun);

  // 街区石板广场占位（接入真实 .glb 模型后可替换此处占位地面）
  const groundGeo = new THREE.CylinderGeometry(7.5, 7.5, 0.24, 48);
  const groundMat = new THREE.MeshStandardMaterial({ color: 0xe6dfd1, roughness: 0.88, metalness: 0.04 });
  const ground = new THREE.Mesh(groundGeo, groundMat);
  ground.position.y = -0.12;
  ground.receiveShadow = true;
  scene.add(ground);

  // 如已制作轻量 .glb 场景（<= 6 MB，无 Draco/Meshopt），取消下面注释加载即可：
  let externalRoot = null;
  // const loader = new GLTFLoader();
  // loader.load("./assets/models/street.glb", (gltf) => {
  //   if (destroyed) return;
  //   externalRoot = gltf.scene;
  //   scene.add(externalRoot);
  // });
  void GLTFLoader;

  const bruce = createLivingBruce({ modelUrl: "./assets/models/bruce.glb", height: 2.3 });
  bruce.root.position.set(0, 0, 0);
  bruce.setMood(sulking ? "sulk" : "happy");
  scene.add(bruce.root);

  const onMove = (e) => {
    const r = wrap.getBoundingClientRect();
    if (!r.width || !r.height) return;
    bruce.lookAtNormalized(((e.clientX - r.left) / r.width - 0.5) * 2, ((e.clientY - r.top) / r.height - 0.5) * 2);
  };
  wrap.addEventListener("pointermove", onMove);

  container.querySelector("#sc3d-btn-back")?.addEventListener("click", () => {
    opts.onBackToHub?.();
  });

  container.querySelector("#sc3d-btn-interact")?.addEventListener("click", () => {
    if (sulking) return;
    bruce.setMood("excited");
    bruce.triggerHappyHop();
    opts.onSettle?.({
      activityId: "street_cafe",
      title: "林荫街角探店",
      outcome: "win",
      delta: 14,
      triggerSwapCandidate: false,
      summaryLine: "布鲁斯在精品街角招牌前得意地摇起尾巴。",
    });
  });

  function applyMood(nextSulk) {
    sulking = Boolean(nextSulk);
    scene.background.setHex(sulking ? 0x263547 : 0xdbe6de);
    sun.intensity = sulking ? 0.35 : 1.65;
    bruce.setMood(sulking ? "sulk" : "happy");
    if (moodTag) moodTag.textContent = sulking ? "冷战阴雨 (<80)" : "晴朗街区 · 3D 模板";
  }

  let prev = performance.now();
  const tick = (now) => {
    if (destroyed) return;
    const dt = Math.min(0.05, (now - prev) / 1000);
    prev = now;
    const w = Math.max(280, wrap.clientWidth);
    const h = Math.max(240, wrap.clientHeight);
    if (canvas.width !== Math.round(w * renderer.getPixelRatio()) || canvas.height !== Math.round(h * renderer.getPixelRatio())) {
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    controls.update();
    bruce.update(dt, now / 1000);
    renderer.render(scene, camera);
    rafId = requestAnimationFrame(tick);
  };
  rafId = requestAnimationFrame(tick);

  return {
    setSulking: applyMood,
    setContext() {},
    destroy() {
      if (destroyed) return;
      destroyed = true;
      if (rafId) cancelAnimationFrame(rafId);
      wrap.removeEventListener("pointermove", onMove);
      bruce.destroy();
      controls.dispose();
      groundGeo.dispose();
      groundMat.dispose();
      if (externalRoot) {
        externalRoot.traverse((o) => {
          o.geometry?.dispose?.();
          const ms = Array.isArray(o.material) ? o.material : [o.material];
          ms.forEach((m) => m?.dispose?.());
        });
      }
      renderer.dispose();
    },
  };
}
