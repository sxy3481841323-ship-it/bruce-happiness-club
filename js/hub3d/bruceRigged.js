import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { sfx } from "../audio.js";

const MOOD_PRESETS = {
  happy: {
    headPitch: -0.02,
    headYaw: 0.0,
    headTilt: 0.04,
    earDrop: 0.0,
    tailAmp: 0.22,
    tailFreq: 6.2,
    tailLift: -0.18,
    breath: 0.018,
  },
  excited: {
    headPitch: -0.08,
    headYaw: 0.0,
    headTilt: -0.08,
    earDrop: -0.04,
    tailAmp: 0.34,
    tailFreq: 11.2,
    tailLift: -0.28,
    breath: 0.025,
  },
  warn: {
    headPitch: 0.08,
    headYaw: 0.0,
    headTilt: 0.02,
    earDrop: 0.95,
    tailAmp: 0.06,
    tailFreq: 2.2,
    tailLift: 0.14,
    breath: 0.014,
  },
  sulk: {
    headPitch: 0.14,
    headYaw: -0.34,
    headTilt: -0.07,
    earDrop: 0.72,
    tailAmp: 0.035,
    tailFreq: 1.4,
    tailLift: 0.24,
    breath: 0.012,
  },
};

const SPINE_BONES = [
  "tripo::0_Right_Limb_0",
  "tripo::0_Right_Limb_1",
  "tripo::0_Right_Limb_2",
  "tripo::0_Right_Limb_3",
];
const NECK_HEAD_BONES = ["tripo::Head_0", "tripo::Head_1", "tripo::Head_2", "tripo::Head_3"];
const JAW_BONES = ["bone_30", "bone_31", "bone_32"];
const LEFT_EAR_BONES = ["tripo::Head_4", "tripo::Head_5", "tripo::Head_6", "tripo::Head_7"];
const RIGHT_EAR_BONES = ["bone_49", "bone_50", "bone_51", "bone_52"];
const TAIL_BONES = [
  "tripo::Spine_0",
  "tripo::1_Left_Limb_0",
  "tripo::1_Left_Limb_1",
  "tripo::1_Left_Limb_2",
  "tripo::1_Left_Limb_3",
  "tripo::1_Left_Limb_4",
  "tripo::1_Left_Limb_5",
];

const FL_LEG = ["bone_16", "bone_17", "bone_18", "bone_19"];
const FR_LEG = ["bone_55", "bone_56", "bone_57", "bone_58"];
const RL_LEG = ["tripo::0_Left_Limb_0", "tripo::0_Left_Limb_1", "tripo::0_Left_Limb_2", "tripo::0_Left_Limb_3"];
const RR_LEG = ["tripo::1_Right_Limb_0", "tripo::1_Right_Limb_1", "tripo::1_Right_Limb_2", "tripo::1_Right_Limb_3"];

const ACTION_DURATIONS = {
  roll_over: 2.85,
  lick_paw: 2.55,
  play_bow: 2.55,
  airplane_ears: 2.25,
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
 * 86-bone Skeletal Rigged Bruce Controller
 * Canonical glTF space: +Z Forward (Nose), +Y Up [0..1], +X Dog's Left.
 * Supports: walkTo, breathing, tail wag, head gaze, roll_over, lick_paw, play_bow, airplane_ears, happyHop.
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

  let activeAction = null; // { name, t, dur, onDone }
  let walkGoal = null; // { x, z, speedScale, onArrive }
  let walkBlend = 0;
  let walkPhase = 0;
  let prevStepIndex = 0;

  const state = { ...MOOD_PRESETS.happy };
  const rigBones = new Map(); // name -> { bone, restPos, restQuat, qCharOfBone, qBoneFromChar }

  // Reusable math scratch objects (zero per-frame allocations)
  const tmpEuler = new THREE.Euler(0, 0, 0, "YXZ");
  const tmpQuat = new THREE.Quaternion();
  const tmpScale = new THREE.Vector3();

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
    gazeYaw = THREE.MathUtils.clamp(nx, -1, 1) * 0.42;
    gazePitch = THREE.MathUtils.clamp(ny, -1, 1) * 0.22;
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

    // 1. Damp mood targets
    const targetHeadPitch = preset.headPitch + (mood === "sulk" ? 0.08 : gazePitch * (1 - pettingBoost * 0.4));
    const targetHeadYaw = mood === "sulk" ? preset.headYaw : gazeYaw * (1 - pettingBoost * 0.4);
    const breathWave = Math.sin(elapsed * (mood === "excited" ? 3.8 : 2.35));
    const spontaneousTilt = mood === "happy" ? Math.sin(elapsed * 0.7) * 0.07 : 0;

    state.headPitch = damp(state.headPitch, targetHeadPitch, 6.5, dt);
    state.headYaw = damp(state.headYaw, targetHeadYaw, 6.5, dt);
    state.headTilt = damp(state.headTilt, preset.headTilt + spontaneousTilt, 5.0, dt);
    state.earDrop = damp(state.earDrop, preset.earDrop, 7.5, dt);
    state.tailAmp = damp(state.tailAmp, preset.tailAmp + pettingBoost * 0.14, 7.0, dt);
    state.tailFreq = damp(state.tailFreq, preset.tailFreq + pettingBoost * 4.5, 6.0, dt);
    state.tailLift = damp(state.tailLift, preset.tailLift, 6.0, dt);
    state.breath = damp(state.breath, preset.breath, 5.0, dt);

    // 2. Locomotion steering toward walkGoal
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
        const nx = dx / dist;
        const nz = dz / dist;
        root.position.x += nx * step;
        root.position.z += nz * step;
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

    // 3. Reset all bones cleanly before compositing character-space poses
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

    // 4. Base organic life: chest breathing, tail wag, head gaze, mood airplane ears
    const breathScale = 1 + breathWave * state.breath;
    addBoneScale("tripo::0_Right_Limb_1", breathScale, 1 + breathWave * state.breath * 0.45, breathScale);
    addBoneScale("tripo::0_Right_Limb_2", breathScale, 1 + breathWave * state.breath * 0.65, breathScale);
    addBoneScale("tripo::0_Right_Limb_3", 1 + breathWave * state.breath * 0.55, 1, 1 + breathWave * state.breath * 0.35);
    motion.position.y += (breathWave * 0.5 + 0.5) * 0.008 * height;

    // 7-segment tail wag with wave lag
    let tailFreq = state.tailFreq;
    let tailAmp = state.tailAmp;
    let tailLift = state.tailLift;

    // Petting purr body sway
    if (pettingBoost > 0.01) {
      motion.rotation.z += Math.sin(elapsed * 12) * 0.03 * pettingBoost;
      motion.rotation.y += Math.sin(elapsed * 5.2) * 0.055 * pettingBoost;
    }

    // Head/neck gaze
    const neckShare = [0.2, 0.25, 0.28, 0.27];
    let headRx = state.headPitch;
    let headRy = state.headYaw;
    let headRz = state.headTilt;

    // Mood ear fold baseline
    let earFold = state.earDrop;

    // 5. Walk gait layered on limbs + spine + ears
    if (walkBlend > 0.01) {
      const wb = walkBlend;
      const pA = walkPhase;
      const pB = walkPhase + Math.PI;

      const swingA = Math.sin(pA) * 0.42 * wb;
      const liftA = Math.max(0, Math.cos(pA)) * 0.56 * wb;
      const swingB = Math.sin(pB) * 0.42 * wb;
      const liftB = Math.max(0, Math.cos(pB)) * 0.56 * wb;

      // Diagonal Pair A: Front Left + Rear Right
      addBoneRot(FL_LEG[0], -swingA, 0, 0);
      addBoneRot(FL_LEG[1], liftA, 0, 0);
      addBoneRot(FL_LEG[2], -liftA * 0.45, 0, 0);
      addBoneRot(RR_LEG[0], -swingA * 0.9, 0, 0);
      addBoneRot(RR_LEG[1], liftA * 0.9, 0, 0);
      addBoneRot(RR_LEG[2], -liftA * 0.4, 0, 0);

      // Diagonal Pair B: Front Right + Rear Left
      addBoneRot(FR_LEG[0], -swingB, 0, 0);
      addBoneRot(FR_LEG[1], liftB, 0, 0);
      addBoneRot(FR_LEG[2], -liftB * 0.45, 0, 0);
      addBoneRot(RL_LEG[0], -swingB * 0.9, 0, 0);
      addBoneRot(RL_LEG[1], liftB * 0.9, 0, 0);
      addBoneRot(RL_LEG[2], -liftB * 0.4, 0, 0);

      // Trotting torso bounce & lateral waggle
      const strideBob = Math.abs(Math.sin(pA)) * 0.028 * height * wb;
      motion.position.y += strideBob;
      motion.rotation.z += Math.sin(pA) * 0.032 * wb;
      SPINE_BONES.forEach((bn, idx) => {
        addBoneRot(bn, 0, Math.sin(pA - idx * 0.35) * 0.04 * wb, 0);
      });
      LEFT_EAR_BONES.forEach((bn, idx) => addBoneRot(bn, 0, 0, Math.sin(pA * 2 - idx * 0.3) * 0.045 * wb));
      RIGHT_EAR_BONES.forEach((bn, idx) => addBoneRot(bn, 0, 0, -Math.sin(pA * 2 - idx * 0.3) * 0.045 * wb));
      tailLift = THREE.MathUtils.lerp(tailLift, -0.22, wb);
      tailAmp = Math.max(tailAmp, 0.24 * wb);
    }

    // 6. Active showcased trick choreography (overrides/layers cleanly onto skeleton)
    if (activeAction) {
      activeAction.t += dt;
      const t = activeAction.t;
      const dur = activeAction.dur;
      const env = envelopeBell(t, dur, 0.24, 0.28);

      if (activeAction.name === "roll_over") {
        // 0..0.38 crouch -> 0.38..2.28 smooth 360 roll with belly-up paw paddle -> 2.28..2.85 shake
        const crouchEnv = t < 0.55 ? envelopeBell(t, 0.55, 0.16, 0.22) : 0;
        motion.position.y -= crouchEnv * 0.05 * height;
        if (crouchEnv > 0.01) {
          [FL_LEG, FR_LEG, RL_LEG, RR_LEG].forEach((leg) => {
            addBoneRot(leg[0], -0.28 * crouchEnv, 0, 0);
            addBoneRot(leg[1], 0.55 * crouchEnv, 0, 0);
          });
        }

        const rollU = THREE.MathUtils.clamp((t - 0.32) / 1.98, 0, 1);
        // Warp rollU so belly-up region around 0.5 has a playful wiggle dwell
        let rollAngle = 0;
        if (rollU > 0 && rollU < 1) {
          const base = rollU < 0.5
            ? 0.5 * Math.pow(rollU * 2, 0.78)
            : 1 - 0.5 * Math.pow((1 - rollU) * 2, 0.78);
          const dwell = Math.sin(rollU * Math.PI);
          rollAngle = base * Math.PI * 2 + Math.sin(t * 10.5) * 0.22 * dwell;
        }
        motion.rotation.z += rollAngle;
        // Exact geometric floor-clearance curve across 0..2π roll:
        // 0 at upright, ~0.28*H on sides (π/2, 3π/2), ~0.52*H belly-up (π) so back touches y=0 without clipping!
        const bellyFactor = Math.sin(rollAngle * 0.5) ** 2;
        const sideFactor = Math.abs(Math.sin(rollAngle));
        motion.position.y += (0.52 * bellyFactor + 0.04 * sideFactor) * height;
        contactShadow.scale.setScalar(1 + bellyFactor * 0.28);
        contactShadow.material.opacity = 0.92 - bellyFactor * 0.22;

        // Tuck & paddle all 4 paws in the air while rolling
        const airEnv = Math.sin(rollU * Math.PI);
        if (airEnv > 0.01) {
          const pad = Math.sin(t * 14.0) * 0.32 * airEnv;
          addBoneRot(FL_LEG[0], -0.45 * airEnv + pad, 0, 0.16 * airEnv);
          addBoneRot(FL_LEG[1], 0.72 * airEnv, 0, 0);
          addBoneRot(FR_LEG[0], -0.45 * airEnv - pad, 0, -0.16 * airEnv);
          addBoneRot(FR_LEG[1], 0.72 * airEnv, 0, 0);
          addBoneRot(RL_LEG[0], -0.35 * airEnv - pad * 0.7, 0, 0.12 * airEnv);
          addBoneRot(RL_LEG[1], 0.55 * airEnv, 0, 0);
          addBoneRot(RR_LEG[0], -0.35 * airEnv + pad * 0.7, 0, -0.12 * airEnv);
          addBoneRot(RR_LEG[1], 0.55 * airEnv, 0, 0);
          headRx -= 0.18 * airEnv;
          tailFreq = 12.5;
          tailAmp = 0.32;
        }

        // Cute finishing shake right after standing back up
        if (t > 2.25) {
          const shEnv = envelopeBell(t - 2.25, dur - 2.25, 0.08, 0.22);
          const sh = Math.sin((t - 2.25) * 28.0) * 0.18 * shEnv;
          headRz += sh;
          LEFT_EAR_BONES.forEach((bn) => addBoneRot(bn, 0, 0, sh * 0.85));
          RIGHT_EAR_BONES.forEach((bn) => addBoneRot(bn, 0, 0, sh * 0.85));
        }
      } else if (activeAction.name === "lick_paw") {
        // Weight shift to Left (+X), lift Front Right paw toward muzzle, bow head & lick
        motion.position.x += 0.028 * height * env;
        motion.rotation.z -= 0.065 * env;
        motion.rotation.x -= 0.04 * env;

        // Brace supporting Front Left & Rear legs slightly
        addBoneRot(FL_LEG[0], -0.08 * env, 0, -0.08 * env);
        addBoneRot(RL_LEG[0], 0.12 * env, 0, 0);
        addBoneRot(RR_LEG[0], 0.12 * env, 0, 0);

        // Lift Front Right paw up & slightly inward toward nose
        addBoneRot(FR_LEG[0], -0.82 * env, 0.14 * env, -0.12 * env);
        addBoneRot(FR_LEG[1], -0.52 * env, 0, 0);
        addBoneRot(FR_LEG[2], 0.34 * env, 0, 0);

        // Bow head down & right toward lifted paw + gentle licking nods
        const lickNod = Math.sin(t * 11.5) * 0.11 * smoothstep(0.35, 0.7, t) * (1 - smoothstep(dur - 0.5, dur - 0.1, t));
        headRx = 0.44 * env + lickNod;
        headRy = -0.24 * env;
        headRz = 0.12 * env;
        JAW_BONES.forEach((bn, idx) => addBoneRot(bn, (0.08 + Math.max(0, lickNod) * 1.1) * env * (idx === 0 ? 1 : 0.35), 0, 0));
        tailFreq = 4.6;
        tailAmp = 0.18;
      } else if (activeAction.name === "play_bow") {
        // Classic dog play bow: chest low near carpet, rump high, tail wagging rapidly
        motion.rotation.x += 0.25 * env;
        motion.position.y -= 0.08 * height * env;
        motion.position.z += 0.04 * height * env;

        // Counter-rotate rear legs so back paws stay planted while rump stays elevated
        addBoneRot(RL_LEG[0], -0.24 * env, 0, 0);
        addBoneRot(RL_LEG[1], 0.18 * env, 0, 0);
        addBoneRot(RR_LEG[0], -0.24 * env, 0, 0);
        addBoneRot(RR_LEG[1], 0.18 * env, 0, 0);

        // Stretch front legs forward along floor
        addBoneRot(FL_LEG[0], -0.56 * env, 0, 0.08 * env);
        addBoneRot(FL_LEG[1], -0.14 * env, 0, 0);
        addBoneRot(FL_LEG[2], 0.46 * env, 0, 0);
        addBoneRot(FR_LEG[0], -0.56 * env, 0, -0.08 * env);
        addBoneRot(FR_LEG[1], -0.14 * env, 0, 0);
        addBoneRot(FR_LEG[2], 0.46 * env, 0, 0);

        // Arch spine concave slightly & raise head cheerfully
        addBoneRot(SPINE_BONES[1], -0.06 * env, 0, 0);
        addBoneRot(SPINE_BONES[2], -0.08 * env, 0, 0);
        headRx = -0.46 * env;
        headRy = Math.sin(t * 3.2) * 0.1 * env;
        tailLift = -0.32;
        tailFreq = 13.5;
        tailAmp = 0.34;
      } else if (activeAction.name === "airplane_ears") {
        earFold = Math.max(earFold, env);
        headRx = 0.22 * env;
        headRy = -0.26 * env;
        headRz = -0.08 * env;
        motion.position.y -= 0.025 * height * env;
        tailLift = 0.28;
        tailFreq = 1.6;
        tailAmp = 0.04;
      }

      if (t >= dur) {
        const doneCb = activeAction.onDone;
        activeAction = null;
        doneCb?.();
      }
    }

    // 7. Apply Head/Neck, Tail, and Airplane Ear chains
    NECK_HEAD_BONES.forEach((bn, i) => {
      const share = neckShare[i];
      addBoneRot(bn, headRx * share, headRy * share, headRz * share);
    });

    if (earFold > 0.01) {
      LEFT_EAR_BONES.forEach((bn, idx) => {
        const w = earFold * (idx === 0 ? 0.46 : 0.2);
        addBoneRot(bn, 0.26 * w, -0.18 * w, 0.28 * w);
      });
      RIGHT_EAR_BONES.forEach((bn, idx) => {
        const w = earFold * (idx === 0 ? 0.46 : 0.2);
        addBoneRot(bn, 0.26 * w, 0.18 * w, -0.28 * w);
      });
    }

    TAIL_BONES.forEach((bn, idx) => {
      const w = 0.22 + idx * 0.05;
      const wag = Math.sin(elapsed * tailFreq - idx * 0.48) * tailAmp * w;
      const lift = (idx < 3 ? tailLift * (idx === 0 ? 0.45 : 0.28) : 0);
      addBoneRot(bn, lift, wag, wag * 0.25);
    });

    // 8. Happy hop vertical spring + paw tuck
    if (hopTimer > 0) {
      hopTimer = Math.max(0, hopTimer - dt);
      const u = 1 - hopTimer / 0.62;
      const hopHeight = Math.sin(u * Math.PI) * 0.2 * height;
      motion.position.y += hopHeight;
      const tuck = Math.sin(u * Math.PI);
      motion.rotation.x -= tuck * 0.08;
      contactShadow.scale.setScalar(1 - tuck * 0.18);
      contactShadow.material.opacity = 0.92 - tuck * 0.26;
      addBoneRot(FL_LEG[0], -0.35 * tuck, 0, 0);
      addBoneRot(FR_LEG[0], -0.35 * tuck, 0, 0);
      addBoneRot(FL_LEG[1], 0.45 * tuck, 0, 0);
      addBoneRot(FR_LEG[1], 0.45 * tuck, 0, 0);
      LEFT_EAR_BONES.forEach((bn) => addBoneRot(bn, 0, 0, 0.08 * tuck));
      RIGHT_EAR_BONES.forEach((bn) => addBoneRot(bn, 0, 0, -0.08 * tuck));
    }
  }

  function destroy() {
    destroyed = true;
    abort.abort();
    disposables.forEach((d) => d?.dispose?.());
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
    update,
    destroy,
  };
}
