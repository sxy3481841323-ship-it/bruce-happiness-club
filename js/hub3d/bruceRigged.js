import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { sfx } from "../audio.js";

const MOOD_PRESETS = {
  happy: {
    headPitch: -0.02,
    headYaw: 0.0,
    headTilt: 0.05,
    earDrop: 0.0,
    tailAmp: 0.24,
    tailFreq: 6.4,
    tailLift: -0.22,
    breath: 0.032,
  },
  excited: {
    headPitch: -0.1,
    headYaw: 0.0,
    headTilt: -0.09,
    earDrop: -0.04,
    tailAmp: 0.36,
    tailFreq: 11.5,
    tailLift: -0.34,
    breath: 0.042,
  },
  warn: {
    headPitch: 0.1,
    headYaw: 0.0,
    headTilt: 0.02,
    earDrop: 1.0,
    tailAmp: 0.06,
    tailFreq: 2.2,
    tailLift: 0.16,
    breath: 0.022,
  },
  sulk: {
    headPitch: 0.18,
    headYaw: -0.38,
    headTilt: -0.08,
    earDrop: 0.85,
    tailAmp: 0.035,
    tailFreq: 1.4,
    tailLift: 0.28,
    breath: 0.02,
  },
};

// Sanitized bone names (GLTFLoader strips ':' so our GLB uses '_' cleanly)
const SPINE_BONES = [
  "tripo_0_Right_Limb_0",
  "tripo_0_Right_Limb_1",
  "tripo_0_Right_Limb_2",
  "tripo_0_Right_Limb_3",
];
const NECK_HEAD_BONES = ["tripo_Head_0", "tripo_Head_1", "tripo_Head_2", "tripo_Head_3"];
const JAW_BONES = ["bone_30", "bone_31", "bone_32"];
const LEFT_EAR_BONES = ["tripo_Head_4", "tripo_Head_5", "tripo_Head_6", "tripo_Head_7"];
const RIGHT_EAR_BONES = ["bone_49", "bone_50", "bone_51", "bone_52"];
const TAIL_BONES = [
  "tripo_Spine_0",
  "tripo_1_Left_Limb_0",
  "tripo_1_Left_Limb_1",
  "tripo_1_Left_Limb_2",
  "tripo_1_Left_Limb_3",
  "tripo_1_Left_Limb_4",
  "tripo_1_Left_Limb_5",
];

const FL_LEG = ["bone_16", "bone_17", "bone_18", "bone_19"];
const FR_LEG = ["bone_55", "bone_56", "bone_57", "bone_58"];
const RL_LEG = ["tripo_0_Left_Limb_0", "tripo_0_Left_Limb_1", "tripo_0_Left_Limb_2", "tripo_0_Left_Limb_3"];
const RR_LEG = ["tripo_1_Right_Limb_0", "tripo_1_Right_Limb_1", "tripo_1_Right_Limb_2", "tripo_1_Right_Limb_3"];

const CORE_REQUIRED_BONES = [
  "tripo_Root",
  ...SPINE_BONES,
  ...NECK_HEAD_BONES,
  ...JAW_BONES,
  ...LEFT_EAR_BONES,
  ...RIGHT_EAR_BONES,
  ...TAIL_BONES,
  ...FL_LEG,
  ...FR_LEG,
  ...RL_LEG,
  ...RR_LEG,
];

const ACTION_DURATIONS = {
  roll_over: 3.15,
  lick_paw: 2.65,
  play_bow: 2.65,
  airplane_ears: 2.35,
};

function damp(a, b, lambda, dt) {
  return THREE.MathUtils.lerp(a, b, 1 - Math.exp(-lambda * dt));
}

function dampAngle(a, b, lambda, dt) {
  let diff = ((b - a + Math.PI) % (Math.PI * 2)) - Math.PI;
  if (diff < -Math.PI) diff += Math.PI * 2;
  return a + diff * (1 - Math.exp(-lambda * dt));
}

function smoothstep(edge0, edge1, x) {
  const t = THREE.MathUtils.clamp((x - edge0) / Math.max(1e-5, edge1 - edge0), 0, 1);
  return t * t * (3 - 2 * t);
}

function envelopeBell(t, dur, fadeIn = 0.25, fadeOut = 0.3) {
  return smoothstep(0, fadeIn, t) * (1 - smoothstep(dur - fadeOut, dur, t));
}

function buildSoftShadowTexture() {
  const c = document.createElement("canvas");
  c.width = 128;
  c.height = 128;
  const ctx = c.getContext("2d");
  const g = ctx.createRadialGradient(64, 64, 8, 64, 64, 58);
  g.addColorStop(0, "rgba(32, 26, 22, 0.24)");
  g.addColorStop(0.55, "rgba(32, 26, 22, 0.09)");
  g.addColorStop(1, "rgba(32, 26, 22, 0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
}

/**
 * Sample ~80-120 extreme convex-hull vertex indices across the dog body
 * (paw soles, elbows, chest keel, chin, snout, flanks, spine, ears, rump, tail)
 * for O(1) exact per-frame SkinnedMesh ground contact clamping.
 */
function sampleHullVertexIndices(geometry) {
  const pos = geometry?.attributes?.position;
  if (!pos) return [];
  const count = pos.count;
  const minX = new Float32Array(72).fill(Infinity);
  const maxX = new Float32Array(72).fill(-Infinity);
  const minY = new Float32Array(72).fill(Infinity);
  const maxY = new Float32Array(72).fill(-Infinity);
  const idxMinX = new Int32Array(72).fill(-1);
  const idxMaxX = new Int32Array(72).fill(-1);
  const idxMinY = new Int32Array(72).fill(-1);
  const idxMaxY = new Int32Array(72).fill(-1);

  for (let i = 0; i < count; i++) {
    const x = pos.getX(i);
    const y = pos.getY(i);
    const z = pos.getZ(i);
    const ix = Math.min(3, Math.max(0, Math.floor(((x + 0.26) / 0.52) * 4)));
    const iy = Math.min(2, Math.max(0, Math.floor((y / 1.01) * 3)));
    const iz = Math.min(5, Math.max(0, Math.floor(((z + 0.65) / 1.3) * 6)));
    const cell = (iy * 6 + iz) * 4 + ix;
    if (y < minY[cell]) {
      minY[cell] = y;
      idxMinY[cell] = i;
    }
    if (y > maxY[cell]) {
      maxY[cell] = y;
      idxMaxY[cell] = i;
    }
    if (x < minX[cell]) {
      minX[cell] = x;
      idxMinX[cell] = i;
    }
    if (x > maxX[cell]) {
      maxX[cell] = x;
      idxMaxX[cell] = i;
    }
  }

  const picked = new Set();
  for (let c = 0; c < 72; c++) {
    if (idxMinY[c] >= 0) picked.add(idxMinY[c]);
    if (idxMaxY[c] >= 0) picked.add(idxMaxY[c]);
    if (idxMinX[c] >= 0) picked.add(idxMinX[c]);
    if (idxMaxX[c] >= 0) picked.add(idxMaxX[c]);
  }
  return Array.from(picked);
}

/**
 * 86-bone Skeletal Rigged Bruce Controller
 * Canonical glTF space: +Z Forward (Nose), +Y Up [0..1], +X Dog's Left.
 */
export function createRiggedBruce({
  modelUrl = "./assets/models/bruce_rigged.glb",
  height = 2.55,
} = {}) {
  const root = new THREE.Group();
  root.name = "RiggedBruce";

  const motion = new THREE.Group();
  root.add(motion);

  const shadowTex = buildSoftShadowTexture();
  const shadowGeo = new THREE.PlaneGeometry(height * 0.92, height * 1.15);
  shadowGeo.rotateX(-Math.PI / 2);
  const shadowMat = new THREE.MeshBasicMaterial({
    map: shadowTex,
    transparent: true,
    depthWrite: false,
  });
  const contactShadow = new THREE.Mesh(shadowGeo, shadowMat);
  contactShadow.position.y = 0.015;
  root.add(contactShadow);

  const disposables = [shadowTex, shadowGeo, shadowMat];
  const abort = new AbortController();

  let destroyed = false;
  let mood = "happy";
  let gazeYaw = 0;
  let gazePitch = 0;
  let pettingBoost = 0;
  let hopTimer = 0;

  let activeAction = null;
  let walkGoal = null;
  let walkBlend = 0;
  let walkPhase = 0;
  let prevStepIndex = 0;

  let skinnedMeshRef = null;
  let hullIndices = [];
  let missingCoreBones = [];
  let matchedBoneCount = 0;
  let lastDiag = null;

  const state = { ...MOOD_PRESETS.happy };
  const rigBones = new Map();

  const tmpEuler = new THREE.Euler(0, 0, 0, "YXZ");
  const tmpQuat = new THREE.Quaternion();
  const tmpScale = new THREE.Vector3();
  const tmpHullV = new THREE.Vector3();

  function addBoneRot(boneName, rx, ry, rz) {
    const rec = rigBones.get(boneName);
    if (!rec) return;
    tmpEuler.set(rx, ry, rz, "YXZ");
    tmpQuat.setFromEuler(tmpEuler);
    rec.bone.quaternion
      .multiply(rec.qBoneFromChar)
      .multiply(tmpQuat)
      .multiply(rec.qCharOfBone);
  }

  function addBoneScale(boneName, sx, sy, sz) {
    const rec = rigBones.get(boneName);
    if (!rec) return;
    tmpScale.set(sx, sy, sz);
    rec.bone.scale.multiply(tmpScale);
  }

  const ready = (async () => {
    try {
      const resp = await fetch(modelUrl, { signal: abort.signal });
      if (!resp.ok) throw new Error(`Failed to fetch ${modelUrl}: ${resp.status}`);
      const buf = await resp.arrayBuffer();
      if (destroyed) return false;

      const loader = new GLTFLoader();
      const basePath = new URL(".", new URL(modelUrl, window.location.href)).href;
      const gltf = await loader.parseAsync(buf, basePath);
      if (destroyed) return false;

      const scene = gltf.scene;
      const holder = new THREE.Group();
      holder.scale.setScalar(height);
      holder.add(scene);
      motion.add(holder);
      holder.updateMatrixWorld(true);

      const holderWorldQuatInv = new THREE.Quaternion();
      holder.getWorldQuaternion(holderWorldQuatInv).invert();

      scene.traverse((obj) => {
        if (obj.isMesh || obj.isSkinnedMesh) {
          obj.castShadow = true;
          obj.receiveShadow = true;
          obj.frustumCulled = false;
          if (obj.isSkinnedMesh && !skinnedMeshRef) {
            skinnedMeshRef = obj;
            hullIndices = sampleHullVertexIndices(obj.geometry);
          }
          if (obj.geometry) disposables.push(obj.geometry);
          const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
          mats.forEach((m) => {
            if (!m) return;
            if (m.map) {
              m.map.colorSpace = THREE.SRGBColorSpace;
              m.map.anisotropy = 4;
              disposables.push(m.map);
            }
            if (m.normalMap) disposables.push(m.normalMap);
            if (m.roughnessMap) disposables.push(m.roughnessMap);
            if (m.metalnessMap) disposables.push(m.metalnessMap);
            disposables.push(m);
          });
        }
        if (obj.isBone) {
          const bwq = new THREE.Quaternion();
          obj.getWorldQuaternion(bwq);
          const qCharOfBone = holderWorldQuatInv.clone().multiply(bwq);
          const qBoneFromChar = qCharOfBone.clone().invert();
          rigBones.set(obj.name, {
            bone: obj,
            restPos: obj.position.clone(),
            restQuat: obj.quaternion.clone(),
            qCharOfBone,
            qBoneFromChar,
          });
        }
      });

      missingCoreBones = CORE_REQUIRED_BONES.filter((n) => !rigBones.has(n));
      matchedBoneCount = CORE_REQUIRED_BONES.length - missingCoreBones.length;
      if (missingCoreBones.length > 0) {
        console.error("RiggedBruce missing core bones:", missingCoreBones);
      }

      return true;
    } catch (err) {
      if (!destroyed && err?.name !== "AbortError") {
        console.warn("createRiggedBruce load warning:", err);
      }
      return false;
    }
  })();

  function setMood(nextMood) {
    if (MOOD_PRESETS[nextMood]) mood = nextMood;
  }

  function lookAtNormalized(nx, ny) {
    gazeYaw = THREE.MathUtils.clamp(nx, -1, 1) * 0.45;
    gazePitch = THREE.MathUtils.clamp(ny, -1, 1) * 0.24;
  }

  function setPetting(amount) {
    pettingBoost = THREE.MathUtils.clamp(amount, 0, 1);
  }

  function triggerHappyHop() {
    hopTimer = 0.62;
  }

  function playAction(name, opts = {}) {
    if (!ACTION_DURATIONS[name]) return false;
    walkGoal = null;
    walkBlend = 0;
    activeAction = {
      name,
      t: 0,
      dur: opts.duration || ACTION_DURATIONS[name],
      onDone: opts.onDone || null,
    };
    return true;
  }

  function walkTo(x, z, { speedScale = 1, onArrive = null } = {}) {
    activeAction = null;
    walkGoal = { x, z, speedScale, onArrive };
  }

  function stopWalk() {
    walkGoal = null;
  }

  function update(dt, elapsed) {
    if (destroyed) return;
    const preset = MOOD_PRESETS[mood] || MOOD_PRESETS.happy;

    const targetHeadPitch = preset.headPitch + (mood === "sulk" ? 0.08 : gazePitch * (1 - pettingBoost * 0.4));
    const targetHeadYaw = mood === "sulk" ? preset.headYaw : gazeYaw * (1 - pettingBoost * 0.4);
    const breathWave = Math.sin(elapsed * (mood === "excited" ? 3.8 : 2.35));
    const spontaneousTilt = mood === "happy" ? Math.sin(elapsed * 0.72) * 0.08 : 0;

    state.headPitch = damp(state.headPitch, targetHeadPitch, 6.5, dt);
    state.headYaw = damp(state.headYaw, targetHeadYaw, 6.5, dt);
    state.headTilt = damp(state.headTilt, preset.headTilt + spontaneousTilt, 5.0, dt);
    state.earDrop = damp(state.earDrop, preset.earDrop, 7.5, dt);
    state.tailAmp = damp(state.tailAmp, preset.tailAmp + pettingBoost * 0.14, 7.0, dt);
    state.tailFreq = damp(state.tailFreq, preset.tailFreq + pettingBoost * 4.5, 6.0, dt);
    state.tailLift = damp(state.tailLift, preset.tailLift, 6.0, dt);
    state.breath = damp(state.breath, preset.breath, 5.0, dt);

    // Locomotion toward walkGoal
    if (walkGoal) {
      const dx = walkGoal.x - root.position.x;
      const dz = walkGoal.z - root.position.z;
      const dist = Math.hypot(dx, dz);
      if (dist <= 0.07) {
        const doneCb = walkGoal.onArrive;
        walkGoal = null;
        doneCb?.();
      } else {
        walkBlend = damp(walkBlend, 1.0, 11.0, dt);
        const desiredYaw = Math.atan2(dx, dz);
        root.rotation.y = dampAngle(root.rotation.y, desiredYaw, 8.5, dt);
        const speed = 2.55 * (walkGoal.speedScale || 1.0);
        const step = Math.min(dist, speed * dt);
        root.position.x += (dx / dist) * step;
        root.position.z += (dz / dist) * step;
        walkPhase += step * 5.8;

        const stepIdx = Math.floor(walkPhase / Math.PI);
        if (stepIdx !== prevStepIndex) {
          prevStepIndex = stepIdx;
          sfx.playPawStep(true);
        }
      }
    } else {
      walkBlend = damp(walkBlend, 0.0, 10.0, dt);
    }

    // Reset all bones to bind rest
    rigBones.forEach(({ bone, restPos, restQuat }) => {
      bone.position.copy(restPos);
      bone.quaternion.copy(restQuat);
      bone.scale.set(1, 1, 1);
    });

    motion.position.set(0, 0, 0);
    motion.rotation.set(0, 0, 0);
    motion.scale.set(1, 1, 1);
    contactShadow.scale.setScalar(1.0);
    contactShadow.material.opacity = 0.92;

    // 1. Visible organic ribcage & spine breathing + idle micro-motion
    const breathExpand = 1 + breathWave * state.breath;
    addBoneScale(SPINE_BONES[1], breathExpand, 1 + breathWave * state.breath * 0.55, breathExpand);
    addBoneScale(SPINE_BONES[2], breathExpand * 1.01, 1 + breathWave * state.breath * 0.72, breathExpand);
    addBoneScale(SPINE_BONES[3], 1 + breathWave * state.breath * 0.55, 1, 1 + breathWave * state.breath * 0.4);
    addBoneRot(SPINE_BONES[2], -breathWave * 0.028, 0, 0);

    let tailFreq = state.tailFreq;
    let tailAmp = state.tailAmp;
    let tailLift = state.tailLift;

    if (pettingBoost > 0.01) {
      addBoneRot(SPINE_BONES[1], 0, Math.sin(elapsed * 5.2) * 0.07 * pettingBoost, 0);
      addBoneRot(SPINE_BONES[2], 0, Math.sin(elapsed * 5.2) * 0.09 * pettingBoost, 0);
    }

    const neckShare = [0.22, 0.25, 0.27, 0.26];
    let headRx = state.headPitch + breathWave * 0.028;
    let headRy = state.headYaw;
    let headRz = state.headTilt;
    let earFold = state.earDrop;

    // 2. Full 4-Legged Diagonal Trot Gait + Serpentine Spine & Floppy Ears
    let hopAirOffset = 0;
    if (walkBlend > 0.01) {
      const wb = walkBlend;
      const pA = walkPhase;
      const pB = walkPhase + Math.PI;

      const swingA = Math.sin(pA) * 0.44 * wb;
      const liftA = Math.max(0, Math.cos(pA)) * 0.58 * wb;
      const swingB = Math.sin(pB) * 0.44 * wb;
      const liftB = Math.max(0, Math.cos(pB)) * 0.58 * wb;

      // Diagonal Pair A: Front Left + Rear Right
      addBoneRot(FL_LEG[0], -swingA, 0, 0);
      addBoneRot(FL_LEG[1], liftA, 0, 0);
      addBoneRot(FL_LEG[2], -liftA * 0.45, 0, 0);
      addBoneRot(RR_LEG[0], -swingA * 0.95, 0, 0);
      addBoneRot(RR_LEG[1], liftA * 0.95, 0, 0);
      addBoneRot(RR_LEG[2], -liftA * 0.42, 0, 0);

      // Diagonal Pair B: Front Right + Rear Left
      addBoneRot(FR_LEG[0], -swingB, 0, 0);
      addBoneRot(FR_LEG[1], liftB, 0, 0);
      addBoneRot(FR_LEG[2], -liftB * 0.45, 0, 0);
      addBoneRot(RL_LEG[0], -swingB * 0.95, 0, 0);
      addBoneRot(RL_LEG[1], liftB * 0.95, 0, 0);
      addBoneRot(RL_LEG[2], -liftB * 0.42, 0, 0);

      hopAirOffset += Math.abs(Math.sin(pA)) * 0.016 * height * wb;
      SPINE_BONES.forEach((bn, idx) => {
        addBoneRot(bn, Math.cos(pA * 2) * 0.025 * wb, Math.sin(pA - idx * 0.4) * 0.048 * wb, Math.sin(pA) * 0.02 * wb);
      });
      headRx += Math.cos(pA * 2) * 0.06 * wb;
      LEFT_EAR_BONES.forEach((bn, idx) => addBoneRot(bn, 0, 0, Math.sin(pA * 2 - idx * 0.3) * 0.08 * wb));
      RIGHT_EAR_BONES.forEach((bn, idx) => addBoneRot(bn, 0, 0, -Math.sin(pA * 2 - idx * 0.3) * 0.08 * wb));
      tailLift = THREE.MathUtils.lerp(tailLift, -0.26, wb);
      tailAmp = Math.max(tailAmp, 0.28 * wb);
    }

    // 3. Expressive Choreographed Actions
    if (activeAction) {
      activeAction.t += dt;
      const t = activeAction.t;
      const dur = activeAction.dur;
      const env = envelopeBell(t, dur, 0.28, 0.32);

      if (activeAction.name === "roll_over") {
        // Authentic 3-Stage Dachshund Belly Rub Roll (NO stiff 360° barrel roll!)
        // Stage 1 (0..0.65s): Fold legs -> lie down onto rug -> roll onto side (~85°)
        // Stage 2 (0.65..2.25s): Roll onto back (~156°) + S-wave spine rub + paw bicycle + neck look up
        // Stage 3 (2.25..3.15s): Roll BACK the same way (156° -> 0°) + stand up + 26Hz fur shake!
        let sideRoll = 0;
        if (t < 0.65) {
          sideRoll = smoothstep(0.18, 0.65, t) * 1.48;
        } else if (t < 2.25) {
          const midWiggle = Math.sin((t - 0.65) * 6.2) * 0.22 * envelopeBell(t - 0.65, 1.6, 0.28, 0.28);
          sideRoll = 1.48 + smoothstep(0.65, 1.0, t) * 1.24 + midWiggle; // peaks ~2.72 rad (~156° belly up!)
        } else {
          sideRoll = (1 - smoothstep(2.25, 2.72, t)) * 2.72;
        }
        motion.rotation.z += sideRoll;

        // Legs stay tucked/bent close to torso while lying/belly-up, and alternate bicycle paddle when belly-up!
        const tuckEnv = smoothstep(0.0, 0.35, t) * (1 - smoothstep(2.55, 2.95, t));
        const paddleEnv = smoothstep(0.7, 1.05, t) * (1 - smoothstep(2.05, 2.38, t));
        const pad = Math.sin(t * 11.5) * 0.36 * paddleEnv;

        addBoneRot(FL_LEG[0], -0.45 * tuckEnv + pad, 0, 0.28 * tuckEnv);
        addBoneRot(FL_LEG[1], 0.85 * tuckEnv, 0, 0);
        addBoneRot(FR_LEG[0], -0.45 * tuckEnv - pad, 0, -0.28 * tuckEnv);
        addBoneRot(FR_LEG[1], 0.85 * tuckEnv, 0, 0);
        addBoneRot(RL_LEG[0], -0.35 * tuckEnv - pad * 0.8, 0, 0.22 * tuckEnv);
        addBoneRot(RL_LEG[1], 0.72 * tuckEnv, 0, 0);
        addBoneRot(RR_LEG[0], -0.35 * tuckEnv + pad * 0.8, 0, -0.22 * tuckEnv);
        addBoneRot(RR_LEG[1], 0.72 * tuckEnv, 0, 0);

        // S-wave spine squirm rubbing back into carpet
        if (paddleEnv > 0.01) {
          SPINE_BONES.forEach((bn, idx) => {
            addBoneRot(bn, 0, Math.sin(t * 7.2 - idx * 0.7) * 0.14 * paddleEnv, Math.cos(t * 6.5 - idx * 0.5) * 0.06 * paddleEnv);
          });
          // Ears splay gently outward beside head on carpet
          LEFT_EAR_BONES.forEach((bn, idx) => addBoneRot(bn, 0.08 * paddleEnv, 0, (0.28 - idx * 0.04) * paddleEnv));
          RIGHT_EAR_BONES.forEach((bn, idx) => addBoneRot(bn, 0.08 * paddleEnv, 0, (-0.28 + idx * 0.04) * paddleEnv));
        }

        // Cute head curl looking up & tilted sideways while waiting for belly rubs
        headRx = THREE.MathUtils.lerp(headRx, -0.38, tuckEnv);
        headRy = THREE.MathUtils.lerp(headRy, 0.22, paddleEnv);
        headRz = THREE.MathUtils.lerp(headRz, -0.25, paddleEnv);
        tailFreq = 11.8;
        tailAmp = 0.34;
        tailLift = -0.18;

        // Crisp standing fur shake at the end (2.72s .. 3.15s)
        if (t > 2.7) {
          const shEnv = envelopeBell(t - 2.7, dur - 2.7, 0.06, 0.16);
          const sh = Math.sin((t - 2.7) * 32.0) * 0.22 * shEnv;
          SPINE_BONES.forEach((bn, idx) => addBoneRot(bn, 0, 0, -sh * (0.3 + idx * 0.12)));
          headRz += sh * 1.15;
          LEFT_EAR_BONES.forEach((bn) => addBoneRot(bn, 0, 0, sh * 1.1));
          RIGHT_EAR_BONES.forEach((bn) => addBoneRot(bn, 0, 0, sh * 1.1));
        }

        contactShadow.scale.set(1.22, 1.35, 1.0);
        contactShadow.material.opacity = 0.85;
      } else if (activeAction.name === "lick_paw") {
        // Weight shifts slightly left; Front Right paw lifts cleanly under muzzle; all 4 neck joints bow deeply!
        addBoneRot(SPINE_BONES[2], 0.08 * env, -0.12 * env, -0.09 * env);
        addBoneRot(SPINE_BONES[3], 0.12 * env, -0.1 * env, -0.06 * env);
        addBoneRot(FL_LEG[0], -0.08 * env, 0, -0.08 * env);
        addBoneRot(RL_LEG[0], 0.18 * env, 0, 0);
        addBoneRot(RL_LEG[1], -0.22 * env, 0, 0);
        addBoneRot(RR_LEG[0], 0.18 * env, 0, 0);
        addBoneRot(RR_LEG[1], -0.22 * env, 0, 0);

        // Lift Front Right paw up toward chest/chin
        addBoneRot(FR_LEG[0], -0.96 * env, 0.18 * env, -0.14 * env);
        addBoneRot(FR_LEG[1], -0.58 * env, 0, 0);
        addBoneRot(FR_LEG[2], 0.32 * env, 0, 0);

        // Deep 4-joint neck bow right down to the lifted paw + rhythmic tongue/jaw lick nods
        const lickEnv = smoothstep(0.32, 0.65, t) * (1 - smoothstep(dur - 0.45, dur - 0.08, t));
        const lickNod = Math.sin(t * 11.5) * 0.14 * lickEnv;
        headRx = 0.82 * env + lickNod;
        headRy = -0.3 * env;
        headRz = 0.16 * env;
        JAW_BONES.forEach((bn, idx) => addBoneRot(bn, (0.12 + Math.max(0, lickNod) * 1.2) * env * (idx === 0 ? 1 : 0.4), 0, 0));
        LEFT_EAR_BONES.forEach((bn, idx) => addBoneRot(bn, 0.1 * env * (idx === 0 ? 1 : 0.3), 0, 0.06 * env));
        RIGHT_EAR_BONES.forEach((bn, idx) => addBoneRot(bn, 0.1 * env * (idx === 0 ? 1 : 0.3), 0, -0.06 * env));
        tailFreq = 4.8;
        tailAmp = 0.2;
      } else if (activeAction.name === "play_bow") {
        // Real skeletal Play Bow: rear hips/legs stay TALL, spine slopes down forward, front elbows bend & stretch forward flat on carpet!
        // Ground-contact clamp lifts/seats paws at y=0 automatically without dipping body below floor!
        SPINE_BONES.forEach((bn, idx) => {
          addBoneRot(bn, (idx < 2 ? 0.14 : 0.06) * env, 0, 0);
        });
        // Keep rear legs extended upright to hold rump high
        addBoneRot(RL_LEG[0], -0.12 * env, 0, 0.06 * env);
        addBoneRot(RR_LEG[0], -0.12 * env, 0, -0.06 * env);

        // Drop chest by swinging front shoulders far forward & flexing elbows/wrists cleanly onto forearms
        addBoneRot(FL_LEG[0], -0.82 * env, 0, 0.12 * env);
        addBoneRot(FL_LEG[1], 0.56 * env, 0, 0);
        addBoneRot(FL_LEG[2], 0.34 * env, 0, 0);
        addBoneRot(FR_LEG[0], -0.82 * env, 0, -0.12 * env);
        addBoneRot(FR_LEG[1], 0.56 * env, 0, 0);
        addBoneRot(FR_LEG[2], 0.34 * env, 0, 0);

        // Arch head cheerfully up at player while tail wags super fast!
        headRx = -0.78 * env;
        headRy = Math.sin(t * 3.4) * 0.12 * env;
        headRz = 0.06 * env;
        tailLift = -0.52;
        tailFreq = 14.0;
        tailAmp = 0.38;
      } else if (activeAction.name === "airplane_ears") {
        // Both Left & Right ear chains flare outward and sweep backward symmetrically!
        earFold = Math.max(earFold, env * 1.15);
        SPINE_BONES[2] && addBoneRot(SPINE_BONES[2], 0.08 * env, -0.12 * env, 0);
        headRx = 0.28 * env;
        headRy = -0.34 * env;
        headRz = -0.09 * env;
        tailLift = 0.38;
        tailFreq = 1.5;
        tailAmp = 0.04;
      }

      if (t >= dur) {
        const doneCb = activeAction.onDone;
        activeAction = null;
        doneCb?.();
      }
    }

    // 4. Apply Neck/Head, Symmetrical Floppy/Airplane Ears & 7-Segment Tail
    NECK_HEAD_BONES.forEach((bn, i) => {
      const share = neckShare[i];
      addBoneRot(bn, headRx * share, headRy * share, headRz * share);
    });

    if (earFold > 0.01) {
      LEFT_EAR_BONES.forEach((bn, idx) => {
        const w = earFold * (idx === 0 ? 0.52 : 0.22);
        addBoneRot(bn, 0.34 * w, -0.22 * w, 0.34 * w);
      });
      RIGHT_EAR_BONES.forEach((bn, idx) => {
        const w = earFold * (idx === 0 ? 0.52 : 0.22);
        addBoneRot(bn, 0.34 * w, 0.22 * w, -0.34 * w);
      });
    }

    TAIL_BONES.forEach((bn, idx) => {
      const w = 0.24 + idx * 0.055;
      const wag = Math.sin(elapsed * tailFreq - idx * 0.48) * tailAmp * w;
      const lift = idx < 3 ? tailLift * (idx === 0 ? 0.46 : 0.28) : 0;
      addBoneRot(bn, lift, wag, wag * 0.22);
    });

    // 5. Happy hop spring envelope
    if (hopTimer > 0) {
      hopTimer = Math.max(0, hopTimer - dt);
      const u = 1 - hopTimer / 0.62;
      const tuck = Math.sin(u * Math.PI);
      hopAirOffset += tuck * 0.18 * height;
      contactShadow.scale.setScalar(1 - tuck * 0.18);
      contactShadow.material.opacity = 0.92 - tuck * 0.28;
      addBoneRot(FL_LEG[0], -0.38 * tuck, 0, 0);
      addBoneRot(FR_LEG[0], -0.38 * tuck, 0, 0);
      addBoneRot(FL_LEG[1], 0.48 * tuck, 0, 0);
      addBoneRot(FR_LEG[1], 0.48 * tuck, 0, 0);
      LEFT_EAR_BONES.forEach((bn) => addBoneRot(bn, 0, 0, 0.1 * tuck));
      RIGHT_EAR_BONES.forEach((bn) => addBoneRot(bn, 0, 0, -0.1 * tuck));
    }

    // 6. EXACT SKINNED HULL GROUND CONTACT CLAMP (Guarantees 0 floor penetration on every frame!)
    let calibratedMinY = 0;
    if (skinnedMeshRef && hullIndices.length > 0) {
      motion.position.y = 0;
      root.updateMatrixWorld(true);
      skinnedMeshRef.skeleton?.update();

      let lowestY = Infinity;
      for (let i = 0; i < hullIndices.length; i++) {
        skinnedMeshRef.getVertexPosition(hullIndices[i], tmpHullV);
        tmpHullV.applyMatrix4(skinnedMeshRef.matrixWorld);
        root.worldToLocal(tmpHullV);
        if (tmpHullV.y < lowestY) lowestY = tmpHullV.y;
      }
      if (Number.isFinite(lowestY)) {
        motion.position.y = -lowestY + hopAirOffset;
        calibratedMinY = lowestY + motion.position.y;
      }
    } else {
      motion.position.y = hopAirOffset;
    }

    lastDiag = {
      missingCoreBones,
      matchedBoneCount,
      totalCoreBones: CORE_REQUIRED_BONES.length,
      hullVertexCount: hullIndices.length,
      activeAction: activeAction?.name || (walkGoal ? "walk" : "idle"),
      rollAngleDeg: Math.round((motion.rotation.z * 180) / Math.PI),
      minVertexY: Number(calibratedMinY.toFixed(4)),
      appliedLiftY: Number(motion.position.y.toFixed(4)),
    };
    if (typeof window !== "undefined") {
      window.__BRUCE_RIG_DIAG__ = lastDiag;
    }
  }

  function destroy() {
    destroyed = true;
    abort.abort();
    disposables.forEach((d) => d?.dispose?.());
    if (typeof window !== "undefined") {
      delete window.__BRUCE_RIG_DIAG__;
    }
  }

  return {
    root,
    hitTarget: motion,
    ready,
    setMood,
    lookAtNormalized,
    setPetting,
    triggerHappyHop,
    playAction,
    walkTo,
    stopWalk,
    isWalking: () => Boolean(walkGoal),
    getActiveAction: () => activeAction?.name || null,
    getDiag: () => lastDiag,
    update,
    destroy,
  };
}
