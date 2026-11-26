import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const MOOD_PRESETS = {
  happy: {
    pitch: -0.04,
    yaw: 0.0,
    tilt: 0.05,
    earDrop: 0.0,
    tailAmp: 0.055,
    tailFreq: 6.2,
    breath: 0.016,
  },
  excited: {
    pitch: -0.12,
    yaw: 0.0,
    tilt: -0.11,
    earDrop: -0.02,
    tailAmp: 0.095,
    tailFreq: 11.5,
    breath: 0.024,
  },
  warn: {
    pitch: 0.09,
    yaw: 0.0,
    tilt: 0.02,
    earDrop: 0.09,
    tailAmp: 0.015,
    tailFreq: 2.0,
    breath: 0.012,
  },
  sulk: {
    pitch: 0.28,
    yaw: -0.35,
    tilt: -0.08,
    earDrop: 0.07,
    tailAmp: 0.006,
    tailFreq: 1.2,
    breath: 0.011,
  },
};

function damp(a, b, lambda, dt) {
  return THREE.MathUtils.lerp(a, b, 1 - Math.exp(-lambda * dt));
}

function patchOrganicVertexShader(material, uniforms) {
  material.onBeforeCompile = (shader) => {
    shader.uniforms.uTime = uniforms.uTime;
    shader.uniforms.uHeadYaw = uniforms.uHeadYaw;
    shader.uniforms.uHeadPitch = uniforms.uHeadPitch;
    shader.uniforms.uHeadTilt = uniforms.uHeadTilt;
    shader.uniforms.uEarDrop = uniforms.uEarDrop;
    shader.uniforms.uTailAmp = uniforms.uTailAmp;
    shader.uniforms.uTailFreq = uniforms.uTailFreq;
    shader.uniforms.uBreath = uniforms.uBreath;

    shader.vertexShader =
      `
      uniform float uTime;
      uniform float uHeadYaw;
      uniform float uHeadPitch;
      uniform float uHeadTilt;
      uniform float uEarDrop;
      uniform float uTailAmp;
      uniform float uTailFreq;
      uniform float uBreath;
      ` + shader.vertexShader;

    shader.vertexShader = shader.vertexShader.replace(
      "#include <begin_vertex>",
      `
      #include <begin_vertex>

      // Normalized local coordinates: height is [0..1], paws at y=0
      float ny = transformed.y;
      float nx = transformed.x;
      float nz = transformed.z;

      // 1. Ribcage breathing (mid-torso [0.16..0.56])
      float wBreath = smoothstep(0.14, 0.32, ny) * (1.0 - smoothstep(0.42, 0.60, ny));
      float bWave = sin(uTime * 2.5) * uBreath * wBreath;
      transformed.x *= (1.0 + bWave);
      transformed.z *= (1.0 + bWave);

      // 2. Tail wagging (low rear tail region: ny < 0.28, nx < -0.08, nz < -0.06)
      float tailDist = max(0.0, (-nx - 0.08)) + max(0.0, (-nz - 0.06));
      float wTail = (1.0 - smoothstep(0.16, 0.30, ny)) * smoothstep(0.02, 0.24, tailDist);
      float wag = sin(uTime * uTailFreq - tailDist * 5.0) * uTailAmp * wTail;
      transformed.x += wag * 0.72;
      transformed.z -= wag * 0.68;

      // 3. Airplane ears droop (warn / sulk)
      float earSide = smoothstep(0.18, 0.34, length(vec2(nx - 0.14, nz - 0.18)));
      float wEar = smoothstep(0.58, 0.76, ny) * earSide;
      transformed.y -= uEarDrop * wEar;
      transformed.x += sign(nx - 0.14) * uEarDrop * 0.45 * wEar;

      // 4. Head turn, nod & cute head tilt around neck pivot
      vec3 neckPivot = vec3(0.12, 0.52, 0.16);
      float wHead = smoothstep(0.46, 0.67, ny);
      if (wHead > 0.001) {
        vec3 p = transformed - neckPivot;
        float cy = cos(uHeadYaw * wHead);
        float sy = sin(uHeadYaw * wHead);
        p = vec3(p.x * cy + p.z * sy, p.y, -p.x * sy + p.z * cy);

        float cp = cos(uHeadPitch * wHead);
        float sp = sin(uHeadPitch * wHead);
        p = vec3(p.x, p.y * cp - p.z * sp, p.y * sp + p.z * cp);

        float ct = cos(uHeadTilt * wHead);
        float st = sin(uHeadTilt * wHead);
        p = vec3(p.x * ct - p.y * st, p.x * st + p.y * ct, p.z);

        transformed = neckPivot + p;
      }
      `
    );
  };
  material.customProgramCacheKey = () => "bruce-living-v1";
  material.needsUpdate = true;
}

function stripFlatPedestal(geometry) {
  const pos = geometry.attributes?.position;
  if (!pos) return;
  const indexAttr = geometry.index;
  if (!indexAttr) return;
  const idx = indexAttr.array;
  const kept = [];
  const a = new THREE.Vector3();
  const b = new THREE.Vector3();
  const c = new THREE.Vector3();
  const ab = new THREE.Vector3();
  const ac = new THREE.Vector3();
  const normal = new THREE.Vector3();

  for (let i = 0; i < idx.length; i += 3) {
    const i0 = idx[i];
    const i1 = idx[i + 1];
    const i2 = idx[i + 2];
    const y0 = pos.getY(i0);
    const y1 = pos.getY(i1);
    const y2 = pos.getY(i2);
    const maxY = Math.max(y0, y1, y2);
    if (maxY < 0.032) {
      continue;
    }
    if (maxY < 0.052) {
      a.fromBufferAttribute(pos, i0);
      b.fromBufferAttribute(pos, i1);
      c.fromBufferAttribute(pos, i2);
      ab.subVectors(b, a);
      ac.subVectors(c, a);
      normal.crossVectors(ab, ac).normalize();
      if (Math.abs(normal.y) > 0.62) {
        continue;
      }
    }
    kept.push(i0, i1, i2);
  }
  if (kept.length > 0 && kept.length < idx.length) {
    geometry.setIndex(kept);
  }
}

/**
 * Load Hunyuan bruce.glb, normalize to Y-up height=1.0 grounded at y=0,
 * and animate with organic GPU vertex deformation + hop/turn state.
 */
export function createLivingBruce({
  modelUrl = "./assets/models/bruce.glb",
  height = 3.2,
} = {}) {
  const root = new THREE.Group();
  root.name = "LivingBruce";

  const motion = new THREE.Group();
  root.add(motion);

  // Soft grounded contact shadow
  const shadowGeo = new THREE.CircleGeometry(height * 0.34, 32);
  shadowGeo.rotateX(-Math.PI / 2);
  const shadowMat = new THREE.MeshBasicMaterial({
    color: 0x1e2228,
    transparent: true,
    opacity: 0.16,
    depthWrite: false,
  });
  const contactShadow = new THREE.Mesh(shadowGeo, shadowMat);
  contactShadow.position.y = 0.02;
  root.add(contactShadow);

  const uniforms = {
    uTime: { value: 0 },
    uHeadYaw: { value: 0 },
    uHeadPitch: { value: 0 },
    uHeadTilt: { value: 0 },
    uEarDrop: { value: 0 },
    uTailAmp: { value: MOOD_PRESETS.happy.tailAmp },
    uTailFreq: { value: MOOD_PRESETS.happy.tailFreq },
    uBreath: { value: MOOD_PRESETS.happy.breath },
  };

  let mood = "happy";
  let destroyed = false;
  let gazeYaw = 0;
  let gazePitch = 0;
  let hopTimer = 0;
  let pettingBoost = 0;
  const abort = new AbortController();
  const disposables = [];

  const state = { ...MOOD_PRESETS.happy };

  const ready = (async () => {
    try {
      const resp = await fetch(modelUrl, { signal: abort.signal });
      if (!resp.ok) throw new Error(`Failed to fetch ${modelUrl}: ${resp.status}`);
      const buf = await resp.arrayBuffer();
      if (destroyed) return false;

      const loader = new GLTFLoader();
      const gltf = await loader.parseAsync(buf, new URL(".", new URL(modelUrl, window.location.href)).href);
      if (destroyed) return false;

      const scene = gltf.scene;
      scene.updateMatrixWorld(true);

      // Bake world transforms into geometry so vertex shader works in clean Y-up space
      const bounds = new THREE.Box3();
      const meshes = [];
      scene.traverse((obj) => {
        if (obj.isMesh && obj.geometry) {
          obj.geometry.applyMatrix4(obj.matrixWorld);
          bounds.expandByObject(obj);
          meshes.push(obj);
        }
      });

      const size = bounds.getSize(new THREE.Vector3());
      const center = bounds.getCenter(new THREE.Vector3());
      const normScale = 1.0 / Math.max(0.001, size.y);
      const normMat = new THREE.Matrix4()
        .makeScale(normScale, normScale, normScale)
        .multiply(new THREE.Matrix4().makeTranslation(-center.x, -bounds.min.y, -center.z));

      const holder = new THREE.Group();
      holder.scale.setScalar(height);

      meshes.forEach((m) => {
        m.geometry.applyMatrix4(normMat);
        stripFlatPedestal(m.geometry);
        m.geometry.computeBoundingBox();
        m.geometry.computeBoundingSphere();

        const newMesh = new THREE.Mesh(m.geometry, m.material);
        newMesh.castShadow = true;
        newMesh.receiveShadow = true;
        disposables.push(m.geometry);

        const mats = Array.isArray(m.material) ? m.material : [m.material];
        mats.forEach((mat) => {
          if (!mat) return;
          if (mat.map) mat.map.colorSpace = THREE.SRGBColorSpace;
          mat.roughness = Math.max(0.55, mat.roughness ?? 0.78);
          mat.metalness = 0.0;
          patchOrganicVertexShader(mat, uniforms);
          disposables.push(mat);
        });
        holder.add(newMesh);
      });

      // Invisible generous raycast hitbox so clicking anywhere on Bruce responds reliably
      const hitGeo = new THREE.CylinderGeometry(0.46, 0.52, 0.98, 12);
      hitGeo.translate(0, 0.49, 0);
      const hitMat = new THREE.MeshBasicMaterial({
        transparent: true,
        opacity: 0,
        depthWrite: false,
      });
      const hitMesh = new THREE.Mesh(hitGeo, hitMat);
      hitMesh.name = "BruceHitbox";
      hitMesh.castShadow = false;
      hitMesh.receiveShadow = false;
      holder.add(hitMesh);
      disposables.push(hitGeo, hitMat);

      motion.add(holder);
      return true;
    } catch (err) {
      if (err?.name !== "AbortError") {
        console.warn("createLivingBruce fallback:", err);
      }
      return false;
    }
  })();

  return {
    root,
    ready,
    setMood(next) {
      if (MOOD_PRESETS[next]) mood = next;
    },
    getMood() {
      return mood;
    },
    lookAtNormalized(nx = 0, ny = 0) {
      gazeYaw = THREE.MathUtils.clamp(nx * 0.42, -0.45, 0.45);
      gazePitch = THREE.MathUtils.clamp(-ny * 0.22, -0.25, 0.25);
    },
    setPetting(amount) {
      pettingBoost = THREE.MathUtils.clamp(amount, 0, 1);
    },
    triggerHappyHop() {
      hopTimer = 0.65;
    },
    update(dt, elapsed) {
      if (destroyed) return;
      const target = MOOD_PRESETS[mood] || MOOD_PRESETS.happy;

      const extraTilt = pettingBoost > 0.05 ? Math.sin(elapsed * 4.5) * 0.11 * pettingBoost : 0;
      const extraTail = pettingBoost * 0.04;

      state.yaw = damp(state.yaw, target.yaw + gazeYaw, 5, dt);
      state.pitch = damp(state.pitch, target.pitch + gazePitch, 5, dt);
      state.tilt = damp(state.tilt, target.tilt + extraTilt, 5, dt);
      state.earDrop = damp(state.earDrop, target.earDrop, 6, dt);
      state.tailAmp = damp(state.tailAmp, target.tailAmp + extraTail, 6, dt);
      state.tailFreq = damp(state.tailFreq, target.tailFreq + pettingBoost * 4, 5, dt);
      state.breath = damp(state.breath, target.breath, 4, dt);

      uniforms.uTime.value = elapsed;
      uniforms.uHeadYaw.value = state.yaw;
      uniforms.uHeadPitch.value = state.pitch;
      uniforms.uHeadTilt.value = state.tilt;
      uniforms.uEarDrop.value = state.earDrop;
      uniforms.uTailAmp.value = state.tailAmp;
      uniforms.uTailFreq.value = state.tailFreq;
      uniforms.uBreath.value = state.breath;

      if (hopTimer > 0) {
        hopTimer = Math.max(0, hopTimer - dt);
        const phase = 1 - hopTimer / 0.65;
        motion.position.y = Math.sin(phase * Math.PI) * height * 0.16;
        contactShadow.scale.setScalar(1 - Math.sin(phase * Math.PI) * 0.18);
      } else {
        motion.position.y = 0;
        contactShadow.scale.setScalar(1);
      }
    },
    destroy() {
      destroyed = true;
      abort.abort();
      shadowGeo.dispose();
      shadowMat.dispose();
      disposables.forEach((d) => {
        try {
          d.dispose?.();
        } catch (_) {}
      });
    },
  };
}
