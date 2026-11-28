import * as THREE from "three";
import { Reflector } from "three/addons/objects/Reflector.js";

/**
 * 3D Harbour Water module adapted for bruce_day_sailer (1:1 meters):
 * - Depth-aware oblique planar reflection (768x432 hi / 512x288 lo) reconstructing world hit via inverseVP
 * - Shared CPU+GPU 3-wave harbour swell: wavelengths 3.8 / 1.7 / 0.73 m, amplitudes 0.012 / 0.007 / 0.003 m,
 *   directions 18 deg / 71 deg / 137 deg
 * - Shallow (#287D73) to deep (#184771) colour blend + Fresnel F0=0.020 + 4-point yacht buoyancy solver
 */

const SPEC_WAVES = [
  { lambda: 3.8, amp: 0.012, deg: 18 },
  { lambda: 1.7, amp: 0.007, deg: 71 },
  { lambda: 0.73, amp: 0.003, deg: 137 },
];

const WAVES = SPEC_WAVES.map(({ lambda, amp, deg }, i) => {
  const kMag = (Math.PI * 2) / lambda;
  const rad = (deg * Math.PI) / 180;
  const kx = kMag * Math.cos(rad);
  const kz = kMag * Math.sin(rad);
  // Deep-water dispersion omega = sqrt(g * k)
  const omega = Math.sqrt(9.81 * kMag) * (i % 2 === 1 ? -1 : 1) * 0.42;
  return [kx, kz, omega, amp];
});

const WAVE_TERMS_GLSL = WAVES.map(
  ([kx, kz, omega, amp]) =>
    `wave(h, vec3(p, uTime), vec3(${kx.toFixed(4)}, ${kz.toFixed(4)}, ${omega.toFixed(4)}), ${amp.toFixed(4)});`,
).join("\n");

const SWELL_GLSL = `
  void wave(inout vec3 h, vec3 p, vec3 k, float a) {
    float phase = dot(k, p);
    h += a * vec3(sin(phase), k.xy * cos(phase));
  }
  vec3 swell(vec2 p) {
    vec3 h = vec3(0.0);
    ${WAVE_TERMS_GLSL}
    return (.58 + .42 * wind) * h;
  }
`;

const VERTEX_SHADER = `
  uniform mat4 textureMatrix;
  uniform float uTime, wind;
  varying vec3 world;
  varying vec4 mirrorUV;
  ${SWELL_GLSL}
  void main() {
    mirrorUV = textureMatrix * vec4(position, 1.0);
    world = (modelMatrix * vec4(position, 1.0)).xyz;
    world.y += swell(world.xz).x;
    gl_Position = projectionMatrix * viewMatrix * vec4(world, 1.0);
  }
`;

const HISTORY_SIZE = 28;
const MAX_LIGHTS = 8;

const FRAGMENT_SHADER = `
  uniform float uTime, wind;
  uniform sampler2D tDiffuse, depths, spectrum;
  uniform mat4 reflectedVP, inverseVP;
  uniform int lampCount, wakeCount;
  uniform vec4 lamps[${MAX_LIGHTS}], trail[${HISTORY_SIZE}], wakeBounds;
  uniform vec3 lampPower[${MAX_LIGHTS}], deepColor, shallowColor, skyColor, skyZenithColor, skyHorizonColor, sunDir, sunColor;
  varying vec3 world;
  varying vec4 mirrorUV;
  ${SWELL_GLSL}

  vec3 wakeShape(vec2 p) {
    if (wakeCount < 2 || any(lessThan(p, wakeBounds.xy)) || any(greaterThan(p, wakeBounds.zw))) return vec3(0.0);
    float nearest = 1e5, age = 0.0, speed = 0.0;
    vec2 side = vec2(0.0);
    for (int i = 1; i < ${HISTORY_SIZE}; i++) {
      if (i >= wakeCount) break;
      vec4 a = trail[i - 1], b = trail[i];
      vec2 ab = b.xy - a.xy;
      float h = clamp(dot(p - a.xy, ab) / max(dot(ab, ab), 0.000001), 0.0, 1.0);
      vec2 delta = p - (a.xy + ab * h);
      float d2 = dot(delta, delta);
      if (d2 < nearest) {
        nearest = d2; side = delta; age = uTime - mix(a.z, b.z, h); speed = mix(a.w, b.w, h);
      }
    }
    float d = sqrt(nearest), offset = d - (0.16 + age * 0.47);
    float energy = smoothstep(0.0, 0.22, age) * (1.0 - smoothstep(1.1, 6.0, age)) * smoothstep(0.08, 1.2, speed);
    float crest = exp(-abs(offset) * 4.4) * energy;
    return vec3(side / max(d, 0.001) * crest * cos(offset * 13.0) * 0.17, crest * exp(-abs(offset) * 5.0));
  }

  void main() {
    vec2 p = world.xz;
    float fp = max(length(dFdx(p)), length(dFdy(p)));
    mat2 turn = mat2(0.80, 0.60, -0.60, 0.80);
    vec3 a = texture2D(spectrum, p / 10.4 + uTime * vec2(-0.025, -0.039)).rgb - 0.5;
    vec3 b = texture2D(spectrum, turn * p / 4.7 + uTime * vec2(0.038, 0.017) + 0.39).rgb - 0.5;
    vec3 c = texture2D(spectrum, p / 1.75 + uTime * vec2(-0.037, 0.068) + 0.12).rgb - 0.5;
    vec2 fine = texture2D(spectrum, turn * p / vec2(0.87, 2.4) - uTime * vec2(0.073, 0.011)).rg - 0.5;
    float nearWeight = 1.0 - smoothstep(0.035, 0.19, fp);

    vec2 slope = swell(p).yz + (0.24 + 0.26 * wind) * (
      a.xy * 0.45 + transpose(turn) * b.xy * 0.30 + c.xy * 0.22 +
      transpose(turn) * fine * 0.14 * nearWeight
    );
    vec3 wake = wakeShape(p);
    slope += wake.xy;

    vec3 N = normalize(vec3(-slope.x, 1.0, -slope.y));
    vec3 V = normalize(cameraPosition - world);
    float facing = clamp(dot(N, V), 0.01, 1.0);
    float fresnel = 0.020 + 0.980 * pow(1.0 - facing, 5.0);

    vec3 ray = reflect(-V, N);
    vec3 ideal = reflect(-V, vec3(0.0, 1.0, 0.0));
    vec2 uv = mirrorUV.xy / mirrorUV.w;
    float z = texture2D(depths, clamp(uv, vec2(0.001), vec2(0.999))).r;
    vec4 hit = inverseVP * vec4(uv * 2.0 - 1.0, z * 2.0 - 1.0, 1.0);
    float path = (z > 0.9999 || abs(hit.w) < 0.00001) ? 55.0 : clamp(distance(hit.xyz / hit.w, world), 0.02, 75.0);
    vec4 proj = reflectedVP * vec4(world + path * normalize(mix(ideal, ray, 0.52)), 1.0);
    vec2 shift = proj.xy / max(0.02, proj.w) * 0.5 + 0.5 - uv;
    vec2 coord = uv + shift / (1.0 + 13.0 * length(shift));
    vec2 edge = min(coord, 1.0 - coord);
    float valid = smoothstep(0.0, 0.024, min(edge.x, edge.y)) * step(0.001, proj.w);

    vec2 texel = 0.65 / vec2(textureSize(tDiffuse, 0));
    vec3 reflection = texture2D(tDiffuse, coord).rgb * 0.56 +
      0.22 * (texture2D(tDiffuse, coord + texel).rgb + texture2D(tDiffuse, coord - texel).rgb);

    // Shallow water tint along teak berth (X < -2.6, |Z| < 13) blending into deep sapphire harbour channel
    float berthDist = max(max(world.x - (-2.85), -5.60 - world.x), abs(world.z) - 12.2);
    float shallowFactor = 1.0 - smoothstep(-0.6, 8.5, berthDist);
    vec3 body = mix(deepColor, shallowColor, clamp(shallowFactor * 0.72, 0.0, 0.78));

    vec2 along = normalize(V.xz + vec2(0.00001));
    vec2 across = vec2(-along.y, along.x);
    float rolled = dot(slope, along);
    float broken = smoothstep(-0.16, 0.18, b.z * 0.79 + c.z * 0.49);
    float silver = smoothstep(0.024, 0.21, rolled + 0.20 * c.z) * (0.15 + 0.85 * broken);

    vec3 reflSky = mix(skyHorizonColor, skyZenithColor, clamp(pow(max(ray.y, 0.0), 0.72), 0.0, 1.0));
    float specSun = pow(max(dot(ray, normalize(sunDir)), 0.0), 96.0);
    vec3 result = mix(body * (0.94 + 0.22 * a.z), mix(reflSky, reflection, valid), 0.08 + 0.56 * fresnel);
    result += sunColor * specSun * (0.35 + 0.65 * broken);
    result += skyHorizonColor * silver * (0.09 + 0.26 * nearWeight) * exp(-abs(ray.y - 0.22) * 3.6);

    vec2 width = vec2(0.022, 0.145 + 0.048 * wind);
    vec2 filterWidth = min(0.038 * fwidth(slope) * 8.0, vec2(0.032));
    for (int i = 0; i < ${MAX_LIGHTS}; i++) {
      if (i >= lampCount) break;
      vec3 L = lamps[i].xyz - world;
      float d2 = max(dot(L, L), 0.02);
      L *= inversesqrt(d2);
      vec3 H = normalize(V + L);
      vec2 error = H.xz / max(H.y, 0.08) + slope;
      float angular = clamp(lamps[i].w * inversesqrt(d2), 0.001, 0.07);
      vec2 spread = sqrt(width * width + filterWidth * filterWidth + angular * angular * vec2(1.0, 0.4));
      vec2 k = vec2(dot(error, across), dot(error, along)) / spread;
      float lobe = exp(-dot(k, k)) / (3.14159 * spread.x * spread.y);
      float nl = max(dot(N, L), 0.0);
      float fl = 0.035 + 0.91 * pow(1.0 - max(dot(L, H), 0.0), 5.0);
      result += lampPower[i] * lobe * fl * nl * (0.32 + 1.12 * broken) / ((3.0 + d2) * (0.08 + facing * nl));
    }
    result += vec3(0.26, 0.38, 0.41) * wake.z * (0.22 + 0.78 * broken);
    gl_FragColor = vec4(result, 1.0);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
  }
`;

function makeSpectrum() {
  const size = 128;
  const data = new Uint8Array(size * size * 4);
  const modes = [
    [1, 2, 0.83], [2, -1, 0.71], [3, 2, 0.44], [2, 5, 0.39], [-4, 3, 0.33],
    [5, 7, 0.22], [8, 3, 0.23], [-6, 7, 0.19], [11, -3, 0.16], [-5, 12, 0.12],
    [10, 9, 0.12], [17, 5, 0.08], [19, -7, 0.06],
  ];
  for (let j = 0; j < size; j++) {
    for (let i = 0; i < size; i++) {
      let sx = 0, sz = 0, height = 0;
      for (let n = 0; n < modes.length; n++) {
        const [x, z, weight] = modes[n];
        const phase = (2 * Math.PI * (x * i + z * j)) / size + n * n * 1.735;
        const slope = (weight * Math.cos(phase)) / Math.hypot(x, z);
        sx += slope * x;
        sz += slope * z;
        height += weight * Math.sin(phase);
      }
      const off = (j * size + i) * 4;
      data[off] = Math.round(127.5 + 124 * Math.tanh(sx * 0.82));
      data[off + 1] = Math.round(127.5 + 124 * Math.tanh(sz * 0.82));
      data[off + 2] = Math.round(127.5 + 124 * Math.tanh(height * 0.82));
      data[off + 3] = 255;
    }
  }
  const map = new THREE.DataTexture(data, size, size);
  map.wrapS = map.wrapT = THREE.RepeatWrapping;
  map.minFilter = THREE.LinearMipmapLinearFilter;
  map.magFilter = THREE.LinearFilter;
  map.generateMipmaps = true;
  map.needsUpdate = true;
  return map;
}

export function createHarbourWater({ lowTier = false, size = 240, segments = 128 } = {}) {
  const mirrorWidth = lowTier ? 512 : 768;
  const mirrorHeight = lowTier ? 288 : 432;

  const uniforms = {
    color: { value: null },
    tDiffuse: { value: null },
    textureMatrix: { value: null },
    spectrum: { value: makeSpectrum() },
    depths: { value: null },
    uTime: { value: 0 },
    wind: { value: 0.62 },
    lampCount: { value: 0 },
    wakeCount: { value: 0 },
    reflectedVP: { value: new THREE.Matrix4() },
    inverseVP: { value: new THREE.Matrix4() },
    deepColor: { value: new THREE.Color(0x0a3866) },
    shallowColor: { value: new THREE.Color(0x1b8278) },
    skyColor: { value: new THREE.Color(0x3b7ec2) },
    skyZenithColor: { value: new THREE.Color(0x164a8d) },
    skyHorizonColor: { value: new THREE.Color(0x8cc2eb) },
    sunDir: { value: new THREE.Vector3(27.0, 22.8, -26.5).normalize() },
    sunColor: { value: new THREE.Color(0xffebc2) },
    lamps: { value: Array.from({ length: MAX_LIGHTS }, () => new THREE.Vector4()) },
    lampPower: { value: Array.from({ length: MAX_LIGHTS }, () => new THREE.Vector3()) },
    trail: { value: Array.from({ length: HISTORY_SIZE }, () => new THREE.Vector4()) },
    wakeBounds: { value: new THREE.Vector4() },
  };

  const geometry = new THREE.PlaneGeometry(size, size, segments, segments);
  const mesh = new Reflector(geometry, {
    textureWidth: mirrorWidth,
    textureHeight: mirrorHeight,
    multisample: 0,
    clipBias: 0.001,
    shader: {
      name: "HarbourWater",
      uniforms,
      vertexShader: VERTEX_SHADER,
      fragmentShader: FRAGMENT_SHADER,
    },
  });
  // Identity-transform root group; rotate water plane cleanly into XZ plane at Y = 0
  const root = new THREE.Group();
  root.name = "HarbourWaterRoot";
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.set(0, 0, 0);
  root.add(mesh);

  const u = mesh.material.uniforms;
  const target = mesh.getRenderTarget();
  target.depthTexture = new THREE.DepthTexture(mirrorWidth, mirrorHeight);
  target.depthTexture.format = THREE.DepthFormat;
  target.depthTexture.type = THREE.UnsignedIntType;
  u.depths.value = target.depthTexture;

  const origReflect = mesh.onBeforeRender;
  mesh.onBeforeRender = function (renderer, scene, camera) {
    origReflect.call(mesh, renderer, scene, camera);
    const reflCam = mesh.getReflectionCamera(camera);
    if (reflCam) {
      u.reflectedVP.value.multiplyMatrices(reflCam.projectionMatrix, reflCam.matrixWorldInverse);
      u.inverseVP.value.copy(u.reflectedVP.value).invert();
    }
  };

  function heightAt(x, z, timeSec = u.uTime.value) {
    let h = 0;
    for (let i = 0; i < WAVES.length; i++) {
      const [kx, kz, omega, amp] = WAVES[i];
      h += amp * Math.sin(kx * x + kz * z + omega * timeSec);
    }
    return h * (0.58 + 0.42 * u.wind.value);
  }

  function computeYachtBuoyancyPose(timeSec = u.uTime.value) {
    const hBow = heightAt(0.0, 7.6, timeSec);
    const hStern = heightAt(0.0, -7.6, timeSec);
    const hPort = heightAt(-2.0, -0.5, timeSec);
    const hStbd = heightAt(2.0, -0.5, timeSec);
    const heave = (hBow + hStern + hPort + hStbd) * 0.25;
    const pitch = Math.atan2(hStern - hBow, 15.2) * 0.9;
    const roll = Math.atan2(hStbd - hPort, 4.0) * 0.9;
    return { y: heave, pitch, roll };
  }

  function setLights(list) {
    const count = Math.min(MAX_LIGHTS, list.length);
    for (let i = 0; i < count; i++) {
      const { position, color, power, radius = 0.2 } = list[i];
      u.lamps.value[i].set(position.x, position.y, position.z, radius);
      const c = new THREE.Color(color);
      u.lampPower.value[i].set(c.r, c.g, c.b).multiplyScalar(power);
    }
    u.lampCount.value = count;
  }

  function clearWake() {
    u.wakeCount.value = 0;
  }

  function setTime(t) {
    if (t < u.uTime.value) clearWake();
    u.uTime.value = t;
  }

  function setWeather(wind) {
    u.wind.value = Math.max(0, Math.min(1.5, wind));
  }

  function setAtmosphere({ deepColor, shallowColor, skyZenithColor, skyHorizonColor, sunDir, sunColor, wind } = {}) {
    if (deepColor !== undefined) u.deepColor.value.set(deepColor);
    if (shallowColor !== undefined) u.shallowColor.value.set(shallowColor);
    if (skyZenithColor !== undefined) u.skyZenithColor.value.set(skyZenithColor);
    if (skyHorizonColor !== undefined) {
      u.skyHorizonColor.value.set(skyHorizonColor);
      u.skyColor.value.set(skyHorizonColor);
    }
    if (sunDir) u.sunDir.value.copy(sunDir).normalize();
    if (sunColor !== undefined) u.sunColor.value.set(sunColor);
    if (typeof wind === "number") setWeather(wind);
  }

  function dispose() {
    clearWake();
    root.removeFromParent();
    geometry.dispose();
    u.spectrum.value?.dispose?.();
    target.depthTexture?.dispose?.();
    mesh.dispose();
  }

  return {
    root,
    mesh,
    mirrorSize: [mirrorWidth, mirrorHeight],
    heightAt,
    computeYachtBuoyancyPose,
    setLights,
    setWeather,
    setAtmosphere,
    setTime,
    clearWake,
    dispose,
  };
}
