import * as THREE from 'three';
import { Reflector } from 'three/addons/objects/Reflector.js';
import { createBruce3D } from './bruce3d.js';

/**
 * A self-contained, locally served architectural miniature.
 * No backend, globals, external assets or cinematic-file changes are required.
 * @param {HTMLElement} containerEl
 * @param {{sulking?: boolean, onSelectPlayable?: (id: string) => void,
 * onSelectPreview?: (id: string) => void}} options
 * @returns {{setSulking: (value: boolean) => void, destroy: () => void}}
 */
export function mountWorldMap3D(containerEl, options = {}) {
  if (!containerEl || containerEl.nodeType !== 1) {
    throw new TypeError('mountWorldMap3D requires a container element.');
  }
  mountedMaps.get(containerEl)?.destroy();
  const controller = createMap(containerEl, options);
  mountedMaps.set(containerEl, controller);
  return controller;
}

const mountedMaps = new WeakMap();
const LOCATIONS = [
  { id: 'home', title: '布鲁斯的小院', hint: '进去陪陪他', center: [3, 0, 5], anchor: [3, 11, 1], size: [23, 12, 16], radius: 10 },
  { id: 'street', title: '林荫小街', hint: '一起散个步', center: [-24, 0, 7], anchor: [-24, 5.6, 6], size: [15, 6, 18], radius: 6.5 },
  { id: 'park', title: '树影公园', preview: true, center: [-21, 0, -17], anchor: [-21, 6, -17], size: [17, 6, 13], radius: 7 },
  { id: 'warehouse', title: '会员仓库', preview: true, center: [9, 0, -17], anchor: [9, 6.5, -17], size: [15, 6, 12], radius: 7.5 },
  { id: 'yacht', title: '白帆码头', preview: true, center: [34, 0, -3], anchor: [36, 5.5, -3], size: [13, 5, 24], radius: 6 },
  { id: 'nordic', title: '云端航线', preview: true, center: [-27, 0, -43], anchor: [-27, 8, -43], size: [12, 9, 10], radius: 5.5 },
  { id: 'california', title: '逐光航线', preview: true, center: [0, 0, -48], anchor: [0, 6, -48], size: [12, 7, 10], radius: 5.5 },
  { id: 'nz_swiss', title: '山海航线', preview: true, center: [27, 0, -39], anchor: [27, 9, -39], size: [12, 10, 11], radius: 5.5 },
];
const clamp = THREE.MathUtils.clamp;
const lerp = THREE.MathUtils.lerp;
const Y_AXIS = new THREE.Vector3(0, 1, 0);

function random(seed = 314159) {
  return () => {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    return seed / 4294967296;
  };
}

function box(parent, material, x, y, z, w, h, d) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

function cylinder(parent, material, x, y, z, top, bottom, height, segments = 16) {
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(top, bottom, height, segments), material);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

function ellipsoid(parent, material, x, y, z, sx, sy, sz, detail = 2) {
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(1, detail ? 18 : 10, detail ? 13 : 7), material);
  mesh.position.set(x, y, z);
  mesh.scale.set(sx, sy, sz);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

function shorePlate(parent, material, y, depth, scale = 1) {
  const shape = new THREE.Shape();
  shape.moveTo(-29, -25);
  const curve = (x1, z1, x2, z2, x3, z3) => shape.bezierCurveTo(x1, -z1, x2, -z2, x3, -z3);
  curve(-34, 24, -35, 21, -35, 15);
  curve(-35, 5, -35, -15, -33, -22);
  curve(-31, -28, -24, -29, -15, -28);
  curve(-4, -27, 9, -30, 20, -27);
  curve(27, -25, 30, -21, 28, -15);
  curve(26, -10, 24, -4, 25, 2);
  curve(26, 8, 31, 15, 28, 21);
  curve(26, 26, 20, 28, 13, 27);
  curve(2, 25, -14, 28, -29, 25);
  const geometry = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: true, bevelSegments: 3, bevelSize: .12, bevelThickness: .08, curveSegments: 24 });
  geometry.rotateX(-Math.PI / 2);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.y = y;
  mesh.scale.set(scale, 1, scale);
  mesh.castShadow = mesh.receiveShadow = true;
  parent.add(mesh);
}

function roundedShape(w, d, r = 1) {
  const x = -w / 2, y = -d / 2;
  const s = new THREE.Shape();
  s.moveTo(x + r, y);
  s.lineTo(x + w - r, y);
  s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + d - r);
  s.quadraticCurveTo(x + w, y + d, x + w - r, y + d);
  s.lineTo(x + r, y + d);
  s.quadraticCurveTo(x, y + d, x, y + d - r);
  s.lineTo(x, y + r);
  s.quadraticCurveTo(x, y, x + r, y);
  return s;
}

function slab(parent, material, x, y, z, w, d, depth = .3, radius = .6) {
  const geo = new THREE.ExtrudeGeometry(roundedShape(w, d, radius), {
    depth, bevelEnabled: true, bevelSegments: 2, steps: 1,
    bevelSize: .07, bevelThickness: .06, curveSegments: 8,
  });
  geo.rotateX(-Math.PI / 2);
  const mesh = new THREE.Mesh(geo, material);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

function tube(parent, material, points, radius = .04, segments = 20) {
  const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)));
  const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, segments, radius, 6, false), material);
  mesh.castShadow = true;
  parent.add(mesh);
  return mesh;
}

// Static architectural elements are merged by material. Animated crowns and water
// stay separate; hundreds of cornices, pavers and mullions cost only a few draws.
function batchStatic(group) {
  group.updateMatrixWorld(true);
  const buckets = new Map();
  const removals = [];
  group.traverse(mesh => {
    if (!mesh.isMesh || Array.isArray(mesh.material) || mesh.material.transparent || mesh.userData.unbatched) return;
    const list = buckets.get(mesh.material) || [];
    const source = mesh.geometry.index ? mesh.geometry.toNonIndexed() : mesh.geometry.clone();
    source.applyMatrix4(mesh.matrixWorld);
    list.push(source);
    buckets.set(mesh.material, list);
    removals.push(mesh);
  });
  const oldGeometries = new Set();
  removals.forEach(mesh => { mesh.removeFromParent(); oldGeometries.add(mesh.geometry); });
  oldGeometries.forEach(geo => geo.dispose());
  for (const [material, geometries] of buckets) {
    const count = geometries.reduce((sum, g) => sum + g.attributes.position.count, 0);
    const merged = new THREE.BufferGeometry();
    for (const [name, size] of [['position', 3], ['normal', 3], ['uv', 2]]) {
      const buffer = new Float32Array(count * size);
      let offset = 0;
      for (const geo of geometries) {
        const attribute = geo.getAttribute(name);
        if (attribute) buffer.set(attribute.array, offset);
        offset += geo.attributes.position.count * size;
      }
      merged.setAttribute(name, new THREE.BufferAttribute(buffer, size));
    }
    merged.computeBoundingSphere();
    const mesh = new THREE.Mesh(merged, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    group.add(mesh);
    geometries.forEach(g => g.dispose());
  }
}

function makeTexture(kind) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 256;
  const ctx = canvas.getContext('2d');
  const rng = random(kind === 'grass' ? 13 : 71);
  ctx.fillStyle = kind === 'grass' ? '#91b778' : '#eee7d9';
  ctx.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 11000; i++) {
    const alpha = rng() * (kind === 'grass' ? .17 : .065);
    ctx.fillStyle = `rgba(${rng() > .45 ? '255,255,240' : '46,70,42'},${alpha})`;
    ctx.fillRect(rng() * 256, rng() * 256, 1, kind === 'grass' ? 2 : 1);
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(kind === 'grass' ? 10 : 4, kind === 'grass' ? 10 : 4);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function makeEnvironment(renderer) {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');
  const sky = ctx.createLinearGradient(0, 0, 0, 256);
  sky.addColorStop(0, '#c7e7f2');
  sky.addColorStop(.48, '#f4f7ef');
  sky.addColorStop(.62, '#d8e2d0');
  sky.addColorStop(1, '#9cae99');
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, 512, 256);
  const sun = ctx.createRadialGradient(148, 74, 1, 148, 74, 55);
  sun.addColorStop(0, 'rgba(255,249,220,1)');
  sun.addColorStop(.16, 'rgba(255,249,220,.85)');
  sun.addColorStop(1, 'rgba(255,249,220,0)');
  ctx.fillStyle = sun;
  ctx.fillRect(0, 0, 512, 256);
  const texture = new THREE.CanvasTexture(canvas);
  texture.mapping = THREE.EquirectangularReflectionMapping;
  texture.colorSpace = THREE.SRGBColorSpace;
  const pmrem = new THREE.PMREMGenerator(renderer);
  const target = pmrem.fromEquirectangular(texture);
  texture.dispose();
  pmrem.dispose();
  return target;
}

function waterMaterial() {
  return new THREE.ShaderMaterial({
    uniforms: THREE.UniformsUtils.merge([THREE.UniformsLib.fog, {
      time: { value: 0 }, mood: { value: 0 },
      shallow: { value: new THREE.Color('#8bc9c4') },
      deep: { value: new THREE.Color('#75b8c1') },
    }]),
    fog: true,
    vertexShader: `
      varying vec3 vWorld;
      #include <fog_pars_vertex>
      void main() {
        vec4 world = modelMatrix * vec4(position, 1.0);
        vWorld = world.xyz;
        vec4 mvPosition = viewMatrix * world;
        gl_Position = projectionMatrix * mvPosition;
        #include <fog_vertex>
      }`,
    fragmentShader: `
      uniform float time, mood;
      uniform vec3 shallow, deep;
      varying vec3 vWorld;
      #include <fog_pars_fragment>
      void main() {
        vec2 p = vWorld.xz;
        float wave = sin(p.x * .71 + p.y * .49 + time * .34)
                   + sin(p.y * 1.34 - p.x * .29 - time * .27) * .45;
        vec2 slope = vec2(cos(p.x * .71 + p.y * .49 + time * .34) * .018,
                          cos(p.y * 1.34 - p.x * .29 - time * .27) * .024);
        vec3 normal = normalize(vec3(-slope.x, 1.0, -slope.y));
        vec3 view = normalize(cameraPosition - vWorld);
        float fresnel = pow(1.0 - max(dot(normal, view), 0.0), 4.0);
        vec3 light = normalize(vec3(-.45, 1.0, .5));
        float glint = pow(max(dot(reflect(-light, normal), view), 0.0), 140.0);
        vec3 col = mix(shallow, deep, .5 + wave * .035);
        col = mix(col, vec3(.72,.86,.87), fresnel * .42);
        col += vec3(.22, .23, .19) * glint * (1.0 - mood * .8);
        col = mix(col, vec3(.27, .43, .52), mood * .72);
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
        #include <fog_fragment>
      }`,
  });
}

const POOL_SHADER = {
  uniforms: {
      color: { value: new THREE.Color('#549f9a') },
    tDiffuse: { value: null }, textureMatrix: { value: new THREE.Matrix4() },
    time: { value: 0 }, mood: { value: 0 },
  },
  vertexShader: `
    uniform mat4 textureMatrix;
    varying vec4 vUv;
    varying vec3 vWorld;
    void main() {
      vUv = textureMatrix * vec4(position, 1.0);
      vWorld = (modelMatrix * vec4(position, 1.0)).xyz;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }`,
  fragmentShader: `
    uniform vec3 color;
    uniform sampler2D tDiffuse;
    uniform float time, mood;
    varying vec4 vUv;
    varying vec3 vWorld;
    void main() {
      vec4 uv = vUv;
      uv.xy += vec2(sin(vWorld.z * 4.0 + time * .9),
                    cos(vWorld.x * 4.5 + time * .7)) * .00065 * uv.w;
      vec3 reflection = texture2DProj(tDiffuse, uv).rgb;
      float line = pow(max(0.0, sin(vWorld.z * 13.0 + vWorld.x * 3.0 + time)), 34.0);
      vec3 water = mix(color, vec3(.29, .43, .49), mood * .55);
      gl_FragColor = vec4(mix(water, reflection, .56) + line * .018, 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`,
};

function buildWorld(renderer, compact, initialSulking = false) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#deedf0');
  scene.fog = new THREE.Fog('#deedf0', 110, 245);
  const environment = makeEnvironment(renderer);
  scene.environment = environment.texture;
  scene.environmentIntensity = .75;
  const staticRoot = new THREE.Group();
  const movingRoot = new THREE.Group();
  scene.add(staticRoot, movingRoot);
  const rng = random(812);
  const grassTexture = makeTexture('grass');
  const stoneTexture = makeTexture('stone');
  const standard = (color, roughness = .8, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness, ...extra });
  const m = {
    stone: standard('#efe8dc', .69, { map: stoneTexture, bumpMap: stoneTexture, bumpScale: .015 }),
    trim: standard('#fff6e5', .65),
    plaster: standard('#f3f0e6', .83),
    base: standard('#e2dfd2', .88),
    grass: standard('#9ab184', .97, { map: grassTexture }),
    lawn: standard('#8eac73', .96),
    lawnLight: standard('#9ab77e', .96),
    hedge: standard('#52754c', .95),
    foliage: standard('#426e4c', .93),
    foliageLight: standard('#70955b', .94),
    foliageDeep: standard('#365f49', .92),
    trunk: standard('#82725b', .95),
    dark: standard('#465b55', .65),
    glass: new THREE.MeshPhysicalMaterial({ color: '#688b87', metalness: .12, roughness: .08, transparent: true, opacity: .54, depthWrite: false, clearcoat: 1, envMapIntensity: 1.4, side: THREE.DoubleSide }),
    shopGlass: standard('#416e70', .12, { metalness: .34, envMapIntensity: 1.5 }),
    warm: standard('#d5b990', .8, { emissive: '#ffc578', emissiveIntensity: .12 }),
    curtain: standard('#b9ad94', .9, { emissive: '#ffc985', emissiveIntensity: .04 }),
    light: standard('#fff3d2', .35, { emissive: '#ffcd85', emissiveIntensity: .45 }),
    oak: standard('#c4a480', .8),
    teak: standard('#c8b18a', .85),
    awning: standard('#779789', .85),
    rose: standard('#dfc4ad', .9),
    roof: standard('#6f8881', .73, { metalness: .15 }),
    bronze: standard('#7c7354', .36, { metalness: .65 }),
    slate: standard('#667b7e', .48, { metalness: .28 }),
    seam: standard('#8e9d98', .5, { metalness: .25 }),
    wine: standard('#874655', .7),
    asphalt: standard('#c5ccbe', .97),
    white: standard('#fff9e9', .45),
    mountain: standard('#b6bbaa', 1),
    snow: standard('#f0f5ea', .94),
    water: waterMaterial(),
  };
  const ambient = new THREE.HemisphereLight('#deeff5', '#b4b59a', 1.6);
  const sun = new THREE.DirectionalLight('#fff1d2', 3.25);
  sun.position.set(-38, 54, 25);
  sun.castShadow = true;
  sun.shadow.mapSize.setScalar(compact ? 1024 : 2048);
  Object.assign(sun.shadow.camera, { left: -62, right: 62, top: 62, bottom: -62, near: 1, far: 160 });
  sun.shadow.normalBias = .045;
  sun.shadow.bias = -.00012;
  sun.shadow.radius = 5;
  sun.shadow.intensity = .72;
  scene.add(ambient, sun);

  // The pale cut edge makes the landscape read as a crafted architectural model.
  shorePlate(staticRoot, m.base, -2.35, 1.65, 1.004);
  shorePlate(staticRoot, m.trim, -.72, .63, 1.008);
  shorePlate(staticRoot, m.grass, -.08, .12);
  const sea = new THREE.Mesh(new THREE.PlaneGeometry(1100, 1100), m.water);
  sea.rotation.x = -Math.PI / 2;
  sea.position.y = -1.32;
  scene.add(sea);

  // Slightly inset paving and the waterside promenade.
  slab(staticRoot, m.stone, -3, .12, 23, 59, 3.7, .12, 1.4);
  for (let x = -29; x < 26; x += 2.2) box(staticRoot, m.base, x, .255, 23, .035, .012, 3.4);
  for (let i = 0; i < 3; i++) box(staticRoot, m.stone, 19.5 + i * 1.5, -.18 - i * .25, 15.5, 3.2, .2, 11.5);
  slab(staticRoot, m.stone, -23, .11, 8.5, 18, 26, .12, 1.5);
  box(staticRoot, m.water, -12.4, .13, 5, 3.6, .06, 39);
  for (const x of [-14.45, -10.35]) box(staticRoot, m.stone, x, .24, 5, .5, .32, 39.4);
  box(staticRoot, m.teak, -15.5, .3, 5, 1.5, .12, 38.9);
  for (let z=-14.2;z<24.3;z+=.46) box(staticRoot, m.base, -15.5, .367, z, 1.45, .012, .022);
  for (const z of [-7, 9]) {
    box(staticRoot, m.trim, -12.4, .5, z, 6.3, .3, 2.4);
    for (const zz of [z - 1, z + 1]) {
      box(staticRoot, m.dark, -12.4, 1.4, zz, 6.1, .045, .045);
      for (const xx of [-15.2, -13.8, -12.4, -11, -9.6]) box(staticRoot, m.dark, xx, .96, zz, .035, .85, .035);
    }
  }

  const crowns = [];
  function tree(x, z, height = 4.7, variety = 0) {
    const trunkHeight = height * .48;
    cylinder(staticRoot, m.trunk, x, trunkHeight / 2 + .2, z, .1, .18, trunkHeight, 7);
    for (let i = 0; i < 3; i++) {
      const angle = i * 2.1 + rng();
      const branch = cylinder(staticRoot, m.trunk, x + Math.cos(angle) * .25, trunkHeight * .8, z + Math.sin(angle) * .25, .035, .075, height * .34, 7);
      branch.rotation.z = Math.cos(angle) * -.48;
      branch.rotation.x = Math.sin(angle) * .48;
    }
    const crown = new THREE.Group();
    // Merge in local coordinates before positioning the wind pivot.
    ellipsoid(crown, variety ? m.foliageDeep : m.foliage, 0, height * .14, 0, height * .24, height * .23, height * .23);
    for (let i = 0; i < (compact ? 6 : 8); i++) {
      const angle = i * 2.399 + rng() * .3;
      const spread = height * (.1 + rng() * .07);
      const size = height * (.115 + rng() * .06);
      const leaf = ellipsoid(crown, i % 3 === 0 ? m.foliageLight : variety ? m.foliageDeep : m.foliage,
        Math.cos(angle) * spread, height * (.06 + rng() * .25), Math.sin(angle) * spread,
        size * (1.05 + rng() * .3), size * (1 + rng() * .25), size);
      const positions = leaf.geometry.attributes.position;
      for (let j = 0; j < positions.count; j++) {
        const px = positions.getX(j), py = positions.getY(j), pz = positions.getZ(j);
        const irregularity = 1 + Math.sin(px * 9 + py * 5) * Math.sin(pz * 7 - px * 3) * .07;
        positions.setXYZ(j, px * irregularity, py * irregularity, pz * irregularity);
      }
      leaf.geometry.computeVertexNormals();
    }
    batchStatic(crown);
    crown.position.set(x, trunkHeight - .3, z);
    movingRoot.add(crown);
    crowns.push({ object: crown, phase: rng() * Math.PI * 2, amount: .009 + rng() * .008 });
  }
  function pine(x, z, height = 4) {
    cylinder(staticRoot, m.trunk, x, height * .22, z, .08, .14, height * .44, 6);
    for (let i = 0; i < 3; i++) {
      const cone = new THREE.Mesh(new THREE.ConeGeometry(height * (.23 - i * .046), height * .49, 9), i === 1 ? m.foliage : m.foliageDeep);
      cone.position.set(x, height * (.44 + i * .19), z);
      cone.castShadow = true;
      staticRoot.add(cone);
    }
  }
  // A fog-softened, continuous shore behind the journey islands gives the model
  // a horizon instead of leaving the destinations on an empty flat backdrop.
  const coastMaterial = m.foliageDeep.clone();
  coastMaterial.transparent = true;
  coastMaterial.opacity = .32;
  coastMaterial.depthWrite = false;
  for (const [x,z,sx,sy,sz] of [[-37,-145,28,2.7,9],[-4,-151,31,3.6,11],[35,-147,30,2.4,8]]) {
    const hill = ellipsoid(staticRoot, coastMaterial, x, -.5, z, sx, sy, sz, 1);
    hill.castShadow = false;
  }
  function hedge(x, z, w, d, h = .72) {
    slab(staticRoot, m.hedge, x, .17, z, w, d, h, Math.min(.34, d * .45, w * .45));
  }
  function bench(x, z, angle = 0) {
    const group = new THREE.Group();
    group.position.set(x, .3, z);
    group.rotation.y = angle;
    staticRoot.add(group);
    for (let i = 0; i < 4; i++) box(group, m.teak, 0, .55, -.3 + i * .19, 2.1, .1, .14);
    for (const xx of [-.8, .8]) box(group, m.dark, xx, .27, 0, .065, .55, .6);
    box(group, m.teak, 0, .96, -.39, 2.1, .5, .09);
  }

  // Main residence: thin limestone piers, deep glazing, restrained cornices.
  const villa = new THREE.Group();
  villa.position.set(3, 0, 1);
  villa.scale.setScalar(1.18);
  staticRoot.add(villa);
  slab(villa, m.stone, 0, .2, .6, 18.8, 13.4, .45, .7);
  box(villa, m.stone, 0, 3.35, -3.55, 12.4, 5.5, .45);
  for (const x of [-6, 6]) box(villa, m.stone, x, 3.35, -.3, .45, 5.5, 6.5);
  for (const y of [.74, 3.48, 6.1]) box(villa, m.stone, 0, y, -.3, 12.4, .24, 7.1);
  for (const y of [6.26, 6.48]) box(villa, m.trim, 0, y, -.3, 13.1, .16, 7.75);
  box(villa, m.stone, 0, 6.7, -.3, 12.6, .33, 7.35);
  box(villa, m.roof, 0, 6.9, -.3, 11.8, .05, 6.5);
  // A shallow standing-seam hipped roof makes this read as a private residence,
  // distinct from the industrial north-light roof behind it.
  const roofVertices = [
    [-6.55,0,-4], [6.55,0,-4], [6.55,0,3.45], [-6.55,0,3.45],
    [-3.8,1.45,-.28], [3.8,1.45,-.28],
  ];
  const roofFaces = [0,5,1, 0,4,5, 2,4,3, 2,5,4, 3,4,0, 1,5,2];
  const roofGeometry = new THREE.BufferGeometry();
  roofGeometry.setAttribute('position', new THREE.Float32BufferAttribute(roofFaces.flatMap(i => roofVertices[i]), 3));
  roofGeometry.computeVertexNormals();
  const residenceRoof = new THREE.Mesh(roofGeometry, m.slate);
  residenceRoof.position.y = 6.88;
  residenceRoof.castShadow = residenceRoof.receiveShadow = true;
  villa.add(residenceRoof);
  for (let x = -5.7; x <= 5.8; x += .71) {
    const ridgeX = clamp(x, -3.8, 3.8);
    tube(villa, m.seam, [[x,6.90,3.45], [ridgeX,8.35,-.28]], .014, 3);
    tube(villa, m.seam, [[x,6.90,-4], [ridgeX,8.35,-.28]], .014, 3);
  }
  for (const x of [-3.1, 3.1]) {
    box(villa, m.stone, x, 7.95, 1.7, 1.5, 1.35, 1.2);
    box(villa, m.shopGlass, x, 7.95, 2.32, 1.07, .96, .035);
    box(villa, m.trim, x, 8.65, 1.7, 1.85, .12, 1.55);
    box(villa, m.dark, x, 7.95, 2.35, .035, 1, .045);
  }
  // Recessed warm walls and little furnishings remain visible behind the glass.
  box(villa, m.warm, 0, 2.0, -2.95, 11.6, 2.35, .08);
  box(villa, m.warm, 0, 4.7, -2.95, 11.6, 2.25, .08);
  box(villa, m.oak, -3.5, 1.15, 1.55, 3.1, .6, 1.1);
  box(villa, m.plaster, -3.5, 1.5, 1.3, 3.25, .5, .65);
  box(villa, m.oak, 2.4, 1.1, -.7, 2, .12, 1.1);
  for (const x of [-3.7, 3.6]) {
    cylinder(villa, m.dark, x, 1.65, -1.5, .025, .025, 1.8, 8);
    cylinder(villa, m.light, x, 2.6, -1.5, .37, .52, .47, 16);
  }
  for (const x of [-4.4, -1.5, 1.5, 4.4]) {
    for (const y of [2.05, 4.85]) for (const side of [-1, 1]) box(villa, m.curtain, x + side * .98, y, 2.67, .48, 2.12, .025);
    box(villa, m.glass, x, 3.4, 3.05, 2.72, 5.1, .035);
    for (const xx of [x - 1.36, x + 1.36]) box(villa, m.dark, xx, 3.4, 3.08, .045, 5.15, .055);
    box(villa, m.dark, x, 3.46, 3.09, 2.75, .045, .055);
  }
  for (const x of [-6.08, -2.93, 2.93, 6.08]) {
    box(villa, m.stone, x, 3.43, 3.55, .37, 5.32, .6);
    box(villa, m.trim, x, .94, 3.55, .55, .24, .78);
    box(villa, m.trim, x, 5.98, 3.55, .58, .23, .8);
  }
  // Recessed double doors, brass hardware, balcony and tall wall sconces.
  box(villa, m.dark, 0, 2.02, 3.12, 2.0, 2.55, .07);
  for (const x of [-.48, .48]) {
    box(villa, m.glass, x, 2.02, 3.17, .9, 2.4, .03);
    box(villa, m.bronze, x * .3, 1.98, 3.24, .025, .55, .055);
  }
  box(villa, m.trim, 0, 3.59, 3.53, 5.7, .15, .85);
  for (let i = 0; i <= 16; i++) box(villa, m.bronze, -2.7 + i * .3375, 4.05, 3.93, .019, .85, .025);
  box(villa, m.bronze, 0, 4.49, 3.93, 5.55, .04, .055);
  for (const x of [-1.35, 1.35]) {
    box(villa, m.bronze, x, 2.1, 3.22, .12, .62, .15);
    box(villa, m.light, x, 2.1, 3.31, .07, .45, .045);
  }
  // Low wings give the detached house a calm, symmetrical silhouette.
  for (const x of [-7.7, 7.7]) {
    box(villa, m.stone, x, 2.27, -.2, 3.1, 3.15, 6.5);
    box(villa, m.trim, x, 3.94, -.2, 3.55, .2, 6.95);
    box(villa, m.shopGlass, x, 2.15, 3.07, 2.25, 2.45, .05);
    box(villa, m.dark, x, 2.14, 3.12, .055, 2.5, .055);
    box(villa, m.warm, x, 1.0, 3.15, 2.2, .09, .05);
    for (const z of [-1.8, .7]) {
      box(villa, m.stone, x, 4.13, z, 2.35, .26, .65);
      for (let i = 0; i < 5; i++) ellipsoid(villa, m.hedge, x - .86 + i * .43, 4.4, z, .28, .23, .32, 1);
    }
  }
  for (let i = 0; i < 4; i++) box(villa, m.stone, 0, .58 - i * .14, 7.6 + i * .45, 5.4 + i * .35, .16, .65);
  slab(staticRoot, m.lawn, 1.6, .15, 16.2, 19.5, 12.1, .04, .7);
  for (let i = 0; i < 6; i++) box(staticRoot, m.lawnLight, -6.4 + i * 3.2, .258, 16.2, 1.58, .006, 11.6);
  hedge(-8.2, 15, .85, 16.6);
  hedge(12, 20.5, .75, 3.1);
  hedge(1.5, 22, 19.2, .8, .64);
  // A real planar reflection, with small moving distortion instead of a blue tile.
  const pool = new Reflector(new THREE.PlaneGeometry(5.1, 9.2), {
    color: '#65aaa5', clipBias: .003,
    textureWidth: compact ? 512 : 1024, textureHeight: compact ? 512 : 1024,
    multisample: 0, shader: POOL_SHADER,
  });
  pool.rotation.x = -Math.PI / 2;
  pool.position.set(8.45, .27, 15.8);
  pool.userData.unbatched = true;
  movingRoot.add(pool);
  for (const x of [5.68, 11.22]) box(staticRoot, m.trim, x, .24, 15.8, .43, .2, 9.85);
  for (const z of [10.98, 20.62]) box(staticRoot, m.trim, 8.45, .24, z, 5.9, .2, .42);
  for (let i = 0; i < 5; i++) box(staticRoot, m.stone, -3.6, .245, 10.4 + i * 2.1, 2, .1, 1.23);
  bench(-5.8, 18, Math.PI / 2);
  tree(-6.3, 11.1, 4.3);
  tree(15.4, 7.7, 5.5, 1);
  tree(16, 20, 4.6);
  tube(staticRoot, m.stone, [[14,.24,23], [18.5,.24,17], [18,.24,6], [20.5,.24,-5], [13,.24,-8]], .7, 60);
  tree(22.4, 12.6, 4.3, 1);
  tree(22, 3.4, 3.7);
  for (const [x,z] of [[20,20],[21.5,8.6],[22.4,-1],[16,-6.3]]) {
    slab(staticRoot, m.stone, x, .15, z, 3.7, 1.75, .17, .7);
    for (let i=0; i<5; i++) {
      ellipsoid(staticRoot, i%2 ? m.foliage : m.hedge, x - 1.25 + i * .6, .56 + (i%2)*.08, z, .53, .44, .6, 1);
    }
  }
  // Teak pool loungers with pale fabric; small objects provide scale.
  for (const z of [12.4, 16]) {
    box(staticRoot, m.teak, 4.2, .47, z, 1.05, .14, 2.35);
    box(staticRoot, m.plaster, 4.2, .6, z, .92, .11, 2.15);
    const back = box(staticRoot, m.plaster, 4.2, .82, z - .79, .92, .1, .71);
    back.rotation.x = -.47;
  }
  for (const x of [-4.2, 10.2]) {
    cylinder(villa, m.stone, x, 1, 6, .45, .32, .65, 16);
    ellipsoid(villa, m.hedge, x, 1.65, 6, .67, .68, .67);
  }

  function cafe(x, z, w, h, paint, mansard = false) {
    const g = new THREE.Group();
    g.position.set(x, .28, z);
    staticRoot.add(g);
    box(g, paint, 0, h / 2, 0, w, h, 5.4);
    box(g, m.trim, 0, .16, 0, w + .32, .25, 5.8);
    box(g, m.trim, 0, h, 0, w + .36, .26, 5.8);
    box(g, m.shopGlass, 0, 1.45, 2.74, w - .62, 2.35, .06);
    for (const xx of [-w / 2 + .26, 0, w / 2 - .26]) box(g, m.trim, xx, 1.5, 2.84, .1, 2.6, .18);
    box(g, m.oak, 0, .58, 2.82, w - .5, .25, .1);
    for (let i = 0; i < 6; i++) {
      const canopyShape = new THREE.Shape();
      canopyShape.moveTo(0,0);
      canopyShape.quadraticCurveTo(.72,.02,1.48,-.38);
      canopyShape.lineTo(1.48,-.46);
      canopyShape.quadraticCurveTo(.72,-.04,0,-.08);
      canopyShape.closePath();
      const canopyGeo = new THREE.ExtrudeGeometry(canopyShape, { depth:(w-.44)/6, bevelEnabled:false, curveSegments:10 });
      canopyGeo.rotateY(-Math.PI/2);
      const awning = new THREE.Mesh(canopyGeo, i%2 ? m.trim : m.awning);
      awning.position.set(-w/2+.22+(i+1)*(w-.44)/6,3.04,2.72);
      awning.castShadow = true;
      g.add(awning);
      box(g, i % 2 ? m.trim : m.awning, -w / 2 + .22 + (i + .5) * (w - .44) / 6, 2.62, 4.05, (w - .44) / 6, .24, .055);
    }
    for (const xx of [-w*.31,w*.31]) {
      cylinder(g, m.stone, xx, .45, 3.1, .32, .26, .56, 16);
      ellipsoid(g, m.foliage, xx, .94, 3.1, .45, .5, .41);
    }
    if (h > 4) {
      for (const xx of [-w * .26, w * .26]) {
        box(g, m.shopGlass, xx, 3.95, 2.75, w * .27, 1.18, .04);
        box(g, m.trim, xx, 3.3, 2.87, w * .33, .12, .3);
      }
    }
    if (mansard) {
      const roof = new THREE.Mesh(new THREE.CylinderGeometry(w * .5, w * .72, 1.1, 4, 1), m.roof);
      roof.rotation.y = Math.PI / 4;
      roof.scale.z = 5.7 / w;
      roof.position.y = h + .65;
      roof.castShadow = true;
      g.add(roof);
    } else {
      box(g, m.roof, 0, h + .2, 0, w - .2, .1, 5.1);
    }
  }
  cafe(-27, 3.8, 5.5, 5.0, m.plaster, true);
  cafe(-20.4, 3.8, 5.4, 3.35, m.rose);
  cafe(-27, -5.2, 5.5, 4.8, m.stone);
  for (const [x, z] of [[-26.6, 12.1], [-21.2, 12.6]]) {
    cylinder(staticRoot, m.dark, x, .85, z, .055, .08, 1.3);
    cylinder(staticRoot, m.teak, x, 1.52, z, .72, .72, .12, 24);
    cylinder(staticRoot, m.trim, x, 2, z, .035, .035, 3.4, 8);
    const umbrella = new THREE.Mesh(new THREE.ConeGeometry(1.8, .45, 24), m.awning);
    umbrella.position.set(x, 3.55, z);
    umbrella.castShadow = true;
    staticRoot.add(umbrella);
    for (const offset of [-1.1, 1.1]) {
      cylinder(staticRoot, m.teak, x + offset, .76, z, .34, .34, .13, 14);
      box(staticRoot, m.dark, x + offset, .45, z, .07, .6, .46);
      box(staticRoot, m.awning, x + offset, 1.04, z - .3, .65, .56, .065);
    }
  }
  for (const z of [-6.5, 1.5, 10.2, 18.2]) tree(-16.6, z, 4.1 + rng() * .8);
  tree(-30.6, 16.5, 4.8, 1);
  tree(-24.4, 20, 4.5);
  bench(-18.5, 19.5);
  bench(-5, 24, Math.PI);
  bench(12, 24, Math.PI);

  // Park: an open meadow, a loop path and a small reflective pond.
  slab(staticRoot, m.lawnLight, -22, .13, -17.7, 19, 14.4, .08, 2.5);
  tube(staticRoot, m.stone, [[-30, .26, -15], [-26, .26, -12], [-17, .26, -13], [-15, .26, -19], [-22, .26, -22.5], [-29, .26, -19], [-30, .26, -15]], .47, 70);
  const pond = new THREE.Mesh(new THREE.CircleGeometry(2.4, 48), m.water);
  pond.rotation.x = -Math.PI / 2;
  pond.scale.y = 1.45;
  pond.position.set(-23, .32, -17.5);
  movingRoot.add(pond);
  for (const [x, z, h] of [[-30,-20,5.3], [-28,-12,4.4], [-17,-22,5.1], [-16,-16,4.3], [-26,-24,4.1], [-31,-9,4.9], [-11,-21,5.3]]) tree(x, z, h, 1);
  bench(-18, -19.5, -.5);
  // A low, modern membership hall, with repeated north-light roof monitors.
  slab(staticRoot, m.stone, 8.8, .13, -17.8, 20.5, 17.3, .12, 1.3);
  box(staticRoot, m.plaster, 9, 2.4, -19.5, 15.7, 4.4, 10.1);
  box(staticRoot, m.roof, 9, 4.65, -19.5, 16.2, .18, 10.5);
  box(staticRoot, m.stone, 9, .72, -14.37, 15.8, .95, .22);
  box(staticRoot, m.shopGlass, 9, 2.45, -14.32, 13.9, 2.35, .07);
  for (let i = 0; i < 8; i++) box(staticRoot, m.trim, 2.1 + i * 1.98, 2.5, -14.2, .09, 2.7, .12);
  box(staticRoot, m.trim, 9, 3.9, -13.4, 16.7, .19, 2.3);
  for (let i = 0; i < 4; i++) {
    const skylight = box(staticRoot, m.shopGlass, 3.1 + i * 3.8, 4.97, -19.7, 2.5, .15, 7.5);
    skylight.rotation.z = -.19;
    box(staticRoot, m.trim, 1.75 + i * 3.8, 4.93, -19.7, .16, .65, 7.7);
  }
  box(staticRoot, m.asphalt, 8, .31, -10.5, 16, .04, 3.5);
  for (let i = 0; i < 6; i++) box(staticRoot, m.white, 1.1 + i * 2.8, .34, -10.4, .07, .015, 2.7);
  for (const [x, z] of [[-1, -15], [-2, -7], [21, -22], [21, -13], [20, -3]]) tree(x, z, 4.2 + rng() * .9);
  function car(x, z, paint) {
    slab(staticRoot, paint, x, .44, z, 1.35, 2.6, .55, .35);
    box(staticRoot, m.shopGlass, x, 1.15, z - .15, 1.08, .42, 1.25);
    for (const xx of [-.66, .66]) for (const zz of [-.75, .75]) {
      const wheel = cylinder(staticRoot, m.dark, x + xx, .55, z + zz, .27, .27, .12, 12);
      wheel.rotation.z = Math.PI / 2;
    }
  }
  car(4, -10.5, m.awning);
  car(12.4, -10.5, m.white);

  // Quiet marina, white hulls and real teak finger piers.
  box(staticRoot, m.trim, 31, -.1, -3, 12, .4, 2.1);
  box(staticRoot, m.teak, 36.5, -.06, -3, 1.7, .45, 26);
  for (const z of [-12, -4, 4, 9]) box(staticRoot, m.teak, 32.7, -.03, z, 8.5, .3, .85);
  for (let z = -15; z < 10; z += .43) box(staticRoot, m.base, 36.5, .18, z, 1.65, .015, .022);
  for (const z of [-14, -6, 2, 9]) cylinder(staticRoot, m.dark, 36.7, .5, z, .11, .11, 1.1, 10);
  const boats = [];
  function boat(x, z, scale = 1, sail = false) {
    const g = new THREE.Group();
    const hull = new THREE.Shape();
    hull.moveTo(0, -3.5);
    hull.bezierCurveTo(1.15, -2.5, 1.3, -.6, 1.12, 2.55);
    hull.quadraticCurveTo(0, 3.0, -1.12, 2.55);
    hull.bezierCurveTo(-1.3, -.6, -1.15, -2.5, 0, -3.5);
    const hullGeo = new THREE.ExtrudeGeometry(hull, { depth: .65, bevelEnabled: true, bevelSize: .12, bevelThickness: .14, bevelSegments: 2, curveSegments: 10 });
    hullGeo.rotateX(-Math.PI / 2);
    const hullMesh = new THREE.Mesh(hullGeo, m.white);
    hullMesh.castShadow = true;
    g.add(hullMesh);
    box(g, m.teak, 0, .72, -.1, 1.7, .08, 3.7);
    box(g, m.white, 0, 1.14, .2, 1.55, .75, 2.3);
    box(g, m.shopGlass, 0, 1.45, .05, 1.58, .38, 2.0);
    box(g, m.white, 0, 1.7, .07, 1.76, .12, 2.3);
    for (const side of [-1, 1]) tube(g, m.white, [[side * .85, .92, -2.1], [side, 1, -.5], [side, 1, 2.2]], .025, 12);
    if (sail) {
      cylinder(g, m.trim, 0, 3.3, -.3, .035, .05, 5.5, 8);
      const sailGeo = new THREE.BufferGeometry();
      sailGeo.setAttribute('position', new THREE.Float32BufferAttribute([0, 6, -.3, 0, 2.2, -.3, 0, 2.2, 2.2], 3));
      sailGeo.computeVertexNormals();
      const sailMesh = new THREE.Mesh(sailGeo, new THREE.MeshStandardMaterial({ color: '#fff9e9', side: THREE.DoubleSide, roughness: .9 }));
      g.add(sailMesh);
    }
    // Merge before translating so the animation remains in local coordinates.
    batchStatic(g);
    g.position.set(x, -.8, z);
    g.scale.setScalar(scale);
    g.rotation.y = .08;
    movingRoot.add(g);
    boats.push({ object: g, phase: rng() * 6 });
  }
  boat(32, -8, .81);
  boat(32, 1, 1.05);
  boat(40.5, -10, .78, true);
  boat(41, 1.5, .77);

  // Three unlabelled island silhouettes carry the distant journey previews.
  function island(x, z, w, d) {
    slab(staticRoot, m.mountain, x, -1.2, z, w, d, 1.1, 2.8);
    slab(staticRoot, m.lawn, x, -.2, z, w - .5, d - .5, .17, 2.6);
  }
  island(-27, -43, 12.5, 9);
  for (const [x, z, h] of [[-30,-43,4.2],[-27,-45,6.6],[-24,-42,4.4]]) {
    const peak = new THREE.Mesh(new THREE.ConeGeometry(h * .42, h, 5), m.mountain);
    peak.position.set(x, h / 2, z);
    peak.castShadow = true;
    staticRoot.add(peak);
  }
  for (const [x, z] of [[-31,-40],[-28,-40],[-24,-40],[-23,-44]]) pine(x, z, 3.2);
  island(0, -48, 12, 9.3);
  box(staticRoot, m.plaster, .5, 1.2, -48, 5.6, 2.1, 3.6);
  box(staticRoot, m.shopGlass, .5, 1.4, -46.17, 4.9, 1.5, .05);
  box(staticRoot, m.trim, .5, 2.35, -48, 6, .15, 4);
  for (const x of [-4.2, 4.5]) {
    cylinder(staticRoot, m.trunk, x, 2.0, -47, .08, .16, 4, 8);
    for (let i = 0; i < 6; i++) {
      const leaf = ellipsoid(staticRoot, m.foliageDeep, x, 4.15, -47, 1.8, .13, .28, 1);
      leaf.rotation.y = i * Math.PI / 3;
      leaf.rotation.z = .18;
    }
  }
  island(27, -39, 12.5, 10.5);
  for (const [x, z, h] of [[25,-40,6.4], [29,-41,8.2]]) {
    const peak = new THREE.Mesh(new THREE.ConeGeometry(h * .39, h, 5), m.foliageDeep);
    peak.position.set(x, h / 2, z);
    peak.castShadow = true;
    staticRoot.add(peak);
    const snow = new THREE.Mesh(new THREE.ConeGeometry(h * .14, h * .36, 5), m.snow);
    snow.position.set(x, h * .82, z);
    staticRoot.add(snow);
  }
  pine(23, -36.7, 2.9);
  pine(30.5, -36, 3.5);
  const flightPath = new THREE.CatmullRomCurve3([
    new THREE.Vector3(33, 5.5, -17), new THREE.Vector3(28, 12, -33),
    new THREE.Vector3(0, 11, -46), new THREE.Vector3(-28, 7, -40),
  ]);
  const flightGeo = new THREE.BufferGeometry().setFromPoints(flightPath.getPoints(100));
  const flightLine = new THREE.Line(flightGeo, new THREE.LineDashedMaterial({ color: '#c3ded6', dashSize: .4, gapSize: .65, transparent: true, opacity: .7 }));
  flightLine.computeLineDistances();
  movingRoot.add(flightLine);
  const airplane = new THREE.Group();
  ellipsoid(airplane, m.white, 0, 0, 0, .16, .16, .9, 1);
  box(airplane, m.white, 0, 0, .1, 1.65, .055, .24);
  box(airplane, m.white, 0, .05, .64, .65, .045, .17);
  box(airplane, m.white, 0, .2, .66, .04, .38, .25);
  movingRoot.add(airplane);
  const clouds = [];
  const cloudMat = new THREE.MeshBasicMaterial({ color: '#f8fcf8', transparent: true, opacity: .68, depthWrite: false });
  for (const [x, y, z, scale] of [[-38,7,-58,1], [13,8,-59,1.15], [38,5,-48,.85]]) {
    const cloud = new THREE.Group();
    ellipsoid(cloud, cloudMat, 0, 0, 0, 5 * scale, 1.1 * scale, 1.9 * scale);
    ellipsoid(cloud, cloudMat, -2, .7, 0, 2.7 * scale, 1.2 * scale, 1.7 * scale);
    cloud.position.set(x, y, z);
    movingRoot.add(cloud);
    clouds.push({ object: cloud, x });
  }

  // Small flowers, terrace bollards and grounded human scale, used sparingly.
  for (let i = 0; i < 16; i++) {
    const x = -6.4 + rng() * 8, z = 21.1 + rng() * .5;
    ellipsoid(staticRoot, i % 4 ? m.trim : m.rose, x, .55, z, .1, .13, .1, 0);
  }
  for (const x of [-28, -18, -5, 8, 21]) {
    cylinder(staticRoot, m.dark, x, .62, 24.1, .07, .09, .85, 8);
    cylinder(staticRoot, m.light, x, 1.02, 24.1, .1, .1, .17, 8);
  }
  batchStatic(staticRoot);

  const dog = createGardenBruce();
  dog.root.position.set(-1.8, .28, 16.2);
  movingRoot.add(dog.root);

  const rainCount = compact ? 650 : 1200;
  const rainPositions = new Float32Array(rainCount * 6);
  const rainSeeds = Array.from({ length: rainCount }, () => [rng() * 105 - 49, rng() * 48, rng() * 102 - 57, .7 + rng() * .7]);
  const rainGeo = new THREE.BufferGeometry();
  rainGeo.setAttribute('position', new THREE.BufferAttribute(rainPositions, 3).setUsage(THREE.DynamicDrawUsage));
  const rainMat = new THREE.LineBasicMaterial({ color: '#d7e5ee', transparent: true, opacity: 0, depthWrite: false });
  const rain = new THREE.LineSegments(rainGeo, rainMat);
  rain.frustumCulled = false;
  rain.visible = false;
  scene.add(rain);

  const daySky = new THREE.Color('#bce2ee'), rainSky = new THREE.Color('#a7c2d3');
  const daySun = new THREE.Color('#fff0cd'), rainSun = new THREE.Color('#d0dfe9');
  const dayAmbient = new THREE.Color('#deeff5'), rainAmbient = new THREE.Color('#b8cfe3');
  let mood = initialSulking ? 1 : 0;
  const flightTangent = new THREE.Vector3();
  function update(time, dt, sulking, reducedMotion) {
    mood = lerp(mood, sulking ? 1 : 0, 1 - Math.exp(-dt * 1.8));
    scene.background.copy(daySky).lerp(rainSky, mood);
    scene.fog.color.copy(scene.background);
    scene.environmentIntensity = lerp(.75, .45, mood);
    sun.color.copy(daySun).lerp(rainSun, mood);
    sun.intensity = lerp(3.25, 1.05, mood);
    ambient.color.copy(dayAmbient).lerp(rainAmbient, mood);
    ambient.intensity = lerp(1.6, 1.55, mood);
    m.warm.emissiveIntensity = lerp(.12, 1.4, mood);
    m.curtain.emissiveIntensity = lerp(.04, 2.3, mood);
    m.glass.emissive.set('#ffc57e');
    m.glass.emissiveIntensity = lerp(0, .28, mood);
    m.light.emissiveIntensity = lerp(.45, 1.6, mood);
    m.water.uniforms.time.value = time;
    m.water.uniforms.mood.value = mood;
    pool.material.uniforms.time.value = time;
    pool.material.uniforms.mood.value = mood;
    for (const crown of crowns) {
      crown.object.rotation.z = reducedMotion ? 0 : Math.sin(time * .7 + crown.phase) * crown.amount;
      crown.object.rotation.x = reducedMotion ? 0 : Math.cos(time * .55 + crown.phase) * crown.amount * .55;
    }
    for (const b of boats) {
      b.object.position.y = -.8 + (reducedMotion ? 0 : Math.sin(time * .65 + b.phase) * .045);
      b.object.rotation.z = reducedMotion ? 0 : Math.sin(time * .6 + b.phase) * .012;
    }
    dog.update(time, dt, reducedMotion, mood);
    const progress = reducedMotion ? .32 : (time * .014 + .24) % 1;
    airplane.position.copy(flightPath.getPointAt(progress));
    flightTangent.copy(flightPath.getTangentAt(progress));
    airplane.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, -1), flightTangent);
    clouds.forEach((c, i) => { c.object.position.x = c.x + (reducedMotion ? 0 : Math.sin(time * .035 + i) * 1.7); });
    rain.visible = mood > .01;
    rainMat.opacity = mood * .44;
    if (rain.visible) {
      for (let i = 0; i < rainCount; i++) {
        const [x, y, z, speed] = rainSeeds[i];
        const yy = ((y - time * (reducedMotion ? 1.8 : 17) * speed) % 48 + 48) % 48;
        const o = i * 6;
        rainPositions[o] = x;
        rainPositions[o + 1] = yy;
        rainPositions[o + 2] = z;
        rainPositions[o + 3] = x - .1;
        rainPositions[o + 4] = yy + .6 + speed * .2;
        rainPositions[o + 5] = z + .12;
      }
      rainGeo.attributes.position.needsUpdate = true;
    }
  }
  return { scene, update, pool, dog, environment, resources: [grassTexture, stoneTexture] };
}

function createGardenBruce() {
  const root = new THREE.Group();
  const bodyRoot = new THREE.Group();
  root.add(bodyRoot);
  const fur = new THREE.MeshStandardMaterial({ color: '#c99c63', roughness: .96 });
  const light = new THREE.MeshStandardMaterial({ color: '#eed6a7', roughness: .95 });
  const dark = new THREE.MeshStandardMaterial({ color: '#403f36', roughness: .65 });
  const collar = new THREE.MeshStandardMaterial({ color: '#728f82', roughness: .85 });
  ellipsoid(bodyRoot, fur, 0, .65, 0, .39, .42, .72);
  ellipsoid(bodyRoot, light, 0, .65, -.5, .33, .43, .22);
  const head = new THREE.Group();
  head.position.set(0, 1.09, -.64);
  bodyRoot.add(head);
  ellipsoid(head, fur, 0, 0, 0, .37, .36, .34);
  ellipsoid(head, light, 0, -.12, -.3, .24, .17, .24);
  ellipsoid(head, dark, 0, -.065, -.5, .105, .075, .06, 1);
  for (const side of [-1, 1]) {
    const ear = ellipsoid(head, fur, side * .32, -.1, .02, .13, .33, .21);
    ear.rotation.z = side * .16;
    ellipsoid(head, dark, side * .17, .05, -.29, .031, .041, .03, 1);
  }
  const legs = [];
  for (const x of [-.24, .24]) for (const z of [-.43, .43]) {
    const leg = new THREE.Group();
    leg.position.set(x, .55, z);
    cylinder(leg, fur, 0, -.2, 0, .1, .075, .48, 8);
    ellipsoid(leg, light, 0, -.44, -.03, .12, .085, .18, 1);
    bodyRoot.add(leg);
    legs.push(leg);
  }
  const tail = new THREE.Group();
  tail.position.set(0, .85, .61);
  bodyRoot.add(tail);
  tube(tail, fur, [[0,0,0], [0,.17,.22], [0,.5,.42], [0,.69,.31]], .09, 12);
  cylinder(bodyRoot, collar, 0, .94, -.51, .29, .29, .11, 14).rotation.x = .3;
  // Reuse this project's articulated cream dachshund, including its scarf and
  // expressive joints. Keep the lightweight sculpt as an emergency fallback.
  try {
    const materials = {
      furCream: new THREE.MeshStandardMaterial({ color: '#f3e3c1', roughness: .9 }),
      furEar: new THREE.MeshStandardMaterial({ color: '#e2c393', roughness: .88 }),
      scarfSilk: new THREE.MeshPhysicalMaterial({ color: '#8c2336', roughness: .55, sheen: .55, sheenColor: '#b94a61' }),
      brass: new THREE.MeshStandardMaterial({ color: '#c7a363', metalness: .75, roughness: .35 }),
      noseWet: new THREE.MeshPhysicalMaterial({ color: '#241d1b', roughness: .13, clearcoat: 1 }),
      tonguePink: new THREE.MeshStandardMaterial({ color: '#e18f93', roughness: .8 }),
      eyeGloss: new THREE.MeshPhysicalMaterial({ color: '#201b18', roughness: .12, clearcoat: 1 }),
      eyeWhite: new THREE.MeshBasicMaterial({ color: '#fffdf0' }),
      blanketRose: new THREE.MeshStandardMaterial({ color: '#ce8b7e', roughness: .95 }),
    };
    const projectBruce = createBruce3D(materials);
    projectBruce.root.name = 'GardenBruce';
    projectBruce.root.scale.setScalar(1.35);
    root.add(projectBruce.root);
    bodyRoot.visible = false;
    root.userData.projectBruce = projectBruce;
  } catch {
    // A future incompatible model must not prevent the map from mounting.
  }
  let adopted = null, adoptedTail = null, adoptedTailRest = 0;
  return {
    root,
    adopt(object) {
      adopted = object;
      object.traverse(part => { if (!adoptedTail && /tail|尾/.test(part.name.toLowerCase())) adoptedTail = part; });
      adoptedTailRest = adoptedTail?.rotation.z || 0;
      bodyRoot.visible = false;
      if (root.userData.projectBruce) root.userData.projectBruce.root.visible = false;
      root.add(object);
    },
    update(time, dt, reducedMotion, mood) {
      const t = reducedMotion ? 0 : time * .32;
      root.position.set(-1.8 + Math.sin(t) * 1.9, .28, 16.2 + Math.cos(t) * 1.25);
      const projectBruce = root.userData.projectBruce;
      root.rotation.y = Math.atan2(Math.cos(t) * 1.9, -Math.sin(t) * 1.25) + (projectBruce && !adopted ? 0 : Math.PI);
      if (projectBruce && !adopted) {
        projectBruce.update(dt, reducedMotion ? 0 : time, { mood: mood > .5 ? 'sulk' : 'happy', walkSpeed: reducedMotion ? 0 : .18 });
      }
      bodyRoot.position.y = reducedMotion ? 0 : Math.sin(time * 4.7) * .025;
      head.rotation.z = reducedMotion ? 0 : Math.sin(time * .9) * .055;
      tail.rotation.z = reducedMotion ? 0 : Math.sin(time * (mood > .5 ? 2.5 : 7)) * .5;
      legs.forEach((leg, i) => { leg.rotation.x = reducedMotion ? 0 : Math.sin(time * 4.7 + (i === 0 || i === 3 ? 0 : Math.PI)) * .24; });
      if (adopted) adopted.position.y = reducedMotion ? 0 : Math.sin(time * 4.7) * .025;
      if (adoptedTail) adoptedTail.rotation.z = adoptedTailRest + (reducedMotion ? 0 : Math.sin(time * (mood > .5 ? 2.5 : 7)) * .35);
    },
  };
}

// A restrained photographic depth of field: the residence stays sharp while
// the distant shore and the nearest water soften slightly. DOM callouts remain
// crisp. This pass uses the same local renderer and requires no new assets.
function createArchitecturalLens(renderer) {
  const depth = new THREE.DepthTexture(1, 1, THREE.UnsignedIntType);
  const target = new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType, depthTexture: depth });
  target.samples = Math.min(2, renderer.capabilities.maxSamples);
  const uniforms = {
    image: { value: target.texture }, depth: { value: depth }, pixel: { value: new THREE.Vector2(1,1) },
    cameraNear: { value: .3 }, cameraFar: { value: 1100 }, focus: { value: 130 }, strength: { value: 2.8 },
    inverseProjection: { value: new THREE.Matrix4() }, height: { value: 800 }, projectionScale: { value: 3 },
  };
  const material = new THREE.ShaderMaterial({
    uniforms, depthTest: false, depthWrite: false,
    vertexShader: 'varying vec2 vUv; void main(){vUv=uv;gl_Position=vec4(position.xy,0.0,1.0);}',
    fragmentShader: `
      uniform sampler2D image, depth;
      uniform vec2 pixel;
      uniform float cameraNear, cameraFar, focus, strength;
      uniform float height, projectionScale;
      uniform mat4 inverseProjection;
      varying vec2 vUv;
      #include <packing>
      vec3 positionAt(vec2 uv,float d){
        vec4 p=inverseProjection*vec4(uv*2.0-1.0,d*2.0-1.0,1.0);
        return p.xyz/p.w;
      }
      void main(){
        float d=texture2D(depth,vUv).r;
        float distance=-perspectiveDepthToViewZ(d,cameraNear,cameraFar);
        float blur=clamp((abs(distance-focus)/max(focus,1.0)-.07)*strength,0.0,2.7);
        vec3 color=texture2D(image,vUv).rgb*.28;
        vec3 center=positionAt(vUv,d);
        vec3 normal=normalize(cross(dFdx(center),dFdy(center)));
        float occlusion=0.0;
        float radius=clamp(1.5*projectionScale*height/(2.0*max(distance,1.0)),2.0,28.0);
        for(int i=0;i<8;i++){
          float a=float(i)*.785398163;
          vec2 direction=vec2(cos(a),sin(a));
          color+=texture2D(image,vUv+direction*pixel*blur).rgb*.09;
          vec2 nearby=vUv+direction*pixel*radius*(i%2==0 ? .46 : 1.0);
          vec3 delta=positionAt(nearby,texture2D(depth,nearby).r)-center;
          float len=length(delta);
          occlusion+=max(dot(normal,delta/max(len,.001))-.15,0.0)*(1.0-smoothstep(.15,2.2,len));
        }
        color*=1.0-clamp(occlusion*.105,0.0,.32);
        gl_FragColor=vec4(color,1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
  const scene = new THREE.Scene();
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2,2), material);
  quad.frustumCulled = false;
  scene.add(quad);
  const camera = new THREE.OrthographicCamera(-1,1,1,-1,0,1);
  const size = new THREE.Vector2(), direction = new THREE.Vector3(), offset = new THREE.Vector3();
  return {
    resize(compact) {
      renderer.getDrawingBufferSize(size);
      target.setSize(size.x,size.y);
      uniforms.pixel.value.set(1/size.x,1/size.y);
      uniforms.height.value=size.y;
      uniforms.strength.value=compact ? 1.7 : 2.8;
    },
    render(world, viewCamera, focusPoint) {
      viewCamera.getWorldDirection(direction);
      offset.copy(focusPoint).sub(viewCamera.position);
      uniforms.focus.value=Math.max(3,offset.dot(direction));
      uniforms.cameraNear.value=viewCamera.near;
      uniforms.cameraFar.value=viewCamera.far;
      uniforms.inverseProjection.value.copy(viewCamera.projectionMatrixInverse);
      uniforms.projectionScale.value=viewCamera.projectionMatrix.elements[5];
      const previous=renderer.getRenderTarget();
      renderer.setRenderTarget(target);
      renderer.render(world,viewCamera);
      renderer.setRenderTarget(previous);
      renderer.render(scene,camera);
    },
    dispose() { quad.geometry.dispose(); material.dispose(); target.dispose(); depth.dispose(); },
  };
}

const MAP_CSS = `
.wm3d{position:absolute;inset:0;overflow:hidden;isolation:isolate;color:#304d45;font-family:Inter,"PingFang SC","Microsoft YaHei",sans-serif;background:#deedf0;touch-action:pan-y}
.wm3d *{box-sizing:border-box}
.wm3d-canvas{position:absolute;inset:0;width:100%;height:100%;display:block;touch-action:none;outline:none}
.wm3d-labels,.wm3d-leaders{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
.wm3d-leaders{z-index:1;overflow:hidden}
.wm3d-leaders line{stroke:#5b7d71;stroke-width:1;opacity:.35}
.wm3d-leaders circle{fill:#f8fcf3;stroke:#668579;stroke-width:1;opacity:.8}
.wm3d-labels{z-index:2}
.wm3d-label{position:absolute;left:0;top:0;display:flex;align-items:center;gap:9px;min-height:44px;padding:9px 14px 9px 12px;white-space:nowrap;border:1px solid rgba(255,255,255,.87);border-radius:30px;background:rgba(251,253,246,.82);box-shadow:0 4px 15px #314a3c0d,0 1px 2px #314a3c0a;backdrop-filter:blur(16px) saturate(1.15);-webkit-backdrop-filter:blur(16px) saturate(1.15);color:#3f5b50;cursor:pointer;pointer-events:auto;font:inherit;text-align:left;transition:background .25s,box-shadow .25s,border-color .25s,opacity .25s;will-change:transform}
.wm3d-label[data-kind=playable]{padding-right:16px;background:rgba(255,255,248,.91)}
.wm3d-label[hidden]{display:none}
.wm3d-label:hover,.wm3d-label.is-active{background:rgba(255,255,248,.97);border-color:#9cba9a;box-shadow:0 5px 20px #36513f20}
.wm3d-label:focus-visible,.wm3d-reset:focus-visible{outline:3px solid #547e69;outline-offset:4px}
.wm3d-pin{width:7px;height:7px;flex:0 0 7px;border-radius:50%;background:#93ab9a;box-shadow:0 0 0 4px #91aa9810}
.wm3d-label[data-kind=playable] .wm3d-pin{background:#5b8662;box-shadow:0 0 0 4px #6f9d7319}
.wm3d-name{font-size:12px;letter-spacing:.035em;font-weight:600;line-height:1.35}
.wm3d-copy{display:flex;flex-direction:column;gap:1px}
.wm3d-hint{font-size:10px;color:#6f8377;line-height:1.45;letter-spacing:.02em}
.wm3d-label[data-kind=preview] .wm3d-copy{display:flex;flex-direction:row;align-items:center;gap:9px}
.wm3d-label[data-kind=preview] .wm3d-hint{font-size:9px;border-left:1px solid #83968636;padding-left:8px}
.wm3d[data-weather=rain] .wm3d-label{background:rgba(242,248,250,.87);color:#3e5967;border-color:#ffffffc9}
.wm3d[data-weather=rain] .wm3d-label[data-kind=playable] .wm3d-pin{background:#a2aeb6}
.wm3d[data-weather=rain] .wm3d-hint{color:#617c8d}
.wm3d-reset{position:absolute;z-index:3;right:24px;bottom:var(--world-map-control-bottom,24px);height:44px;display:flex;align-items:center;gap:8px;padding:0 15px;border:1px solid #ffffffc9;border-radius:24px;background:#fbfff4c9;backdrop-filter:blur(16px);color:#486254;cursor:pointer;font:inherit;font-size:11px;font-weight:500;letter-spacing:.1em;box-shadow:0 3px 16px #344b3b09}
.wm3d-reset svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:1.25}
.wm3d-toast{position:absolute;z-index:5;left:50%;bottom:calc(var(--world-map-safe-bottom,24px) + 6px);max-width:calc(100% - 32px);padding:13px 20px;border-radius:18px;transform:translate(-50%,12px);opacity:0;pointer-events:none;background:#f7fcf4ed;border:1px solid #fff;color:#41604f;box-shadow:0 6px 28px #284c4014;font-size:12px;line-height:1.6;text-align:center;transition:opacity .25s,transform .25s;backdrop-filter:blur(16px)}
.wm3d-toast.is-visible{opacity:1;transform:translate(-50%,0)}
.wm3d-sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.wm3d-fallback{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:28px;color:#49614e;background:#e1ece0}
.wm3d-fallback p{font-size:13px;line-height:1.9;max-width:340px;text-align:center}
.wm3d.is-fallback .wm3d-labels{inset:50% 18px auto;width:auto;height:auto;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;max-width:450px;margin:20px auto 0}
.wm3d.is-fallback .wm3d-label{position:relative;transform:none!important;justify-content:center;min-width:0;padding:10px;white-space:normal}
.wm3d.is-fallback .wm3d-leaders,.wm3d.is-fallback .wm3d-reset{display:none}
@media(max-width:520px){.wm3d-label{gap:7px;padding:9px 10px;min-height:44px}.wm3d-name{font-size:11px}.wm3d-hint{font-size:9px}.wm3d-label[data-kind=preview] .wm3d-copy{gap:6px}.wm3d-label[data-kind=preview] .wm3d-hint{padding-left:6px;font-size:8px}.wm3d-label[data-kind=playable]{padding-right:12px}.wm3d-reset{right:18px;padding:0 13px}}
@media(prefers-reduced-motion:reduce){.wm3d-label,.wm3d-toast{transition:none}}
`;

function createMap(container, options) {
  const root = document.createElement('div');
  root.className = 'wm3d';
  root.setAttribute('role', 'region');
  root.setAttribute('aria-label', '布鲁斯的立体世界地图');
  root.innerHTML = `<style>${MAP_CSS}</style>
    <svg class="wm3d-leaders" aria-hidden="true"></svg>
    <div class="wm3d-labels" role="group" aria-label="散步地点"></div>
    <button class="wm3d-reset" type="button" aria-label="回到全景" title="回到全景（Esc）" data-map-reset>
      <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M7 3H3v4m10-4h4v4M3 13v4h4m6 0h4v-4M7 10h6m-3-3v6"/></svg>全景
    </button>
    <div class="wm3d-toast" role="status" aria-live="polite"></div>
    <span class="wm3d-sr" aria-live="polite"></span>`;
  const oldPosition = container.style.position;
  const changedPosition = getComputedStyle(container).position === 'static';
  if (changedPosition) container.style.position = 'relative';
  container.append(root);
  const listeners = [];
  function listen(target, name, handler, config) {
    target.addEventListener(name, handler, config);
    listeners.push(() => target.removeEventListener(name, handler, config));
  }
  const svg = root.querySelector('.wm3d-leaders');
  const labelsEl = root.querySelector('.wm3d-labels');
  const toast = root.querySelector('.wm3d-toast');
  const live = root.querySelector('.wm3d-sr');
  const abort = new AbortController();
  const motionPreference = matchMedia('(prefers-reduced-motion: reduce)');
  let reducedMotion = motionPreference.matches;
  let sulking = Boolean(options.sulking);
  let destroyed = false, frameId = 0, lastFrame = 0, elapsed = 0;
  let hoverTimer = 0, resetTimer = 0, toastTimer = 0;
  let focusId = null, focusKind = 'overview', pendingSelection = null;
  let width = 1, height = 1, compact = false, overviewDistance = 140;
  let inView = true, contextLost = false;
  let renderer, world, camera, lens, resizeObserver, intersectionObserver;
  let labelMeasuresDirty = true;
  const pointer = new THREE.Vector2();
  const cameraDirection = new THREE.Vector3(.60, .66, .98).normalize();
  const overviewTarget = new THREE.Vector3(-.5, 0, -9.5);
  const residenceFocus = new THREE.Vector3(3, 2, 4);
  const desiredTarget = overviewTarget.clone();
  const currentTarget = overviewTarget.clone();
  const desiredCamera = new THREE.Vector3();
  const projection = new THREE.Vector3();
  const cameraRight = new THREE.Vector3();
  const raycaster = new THREE.Raycaster();
  const pointerNdc = new THREE.Vector2();
  const hitObjects = [];
  const markers = [];
  const locationById = new Map(LOCATIONS.map(l => [l.id, l]));

  function notify(message) {
    toast.textContent = message;
    toast.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('is-visible'), 3600);
  }
  function setFocus(id, kind) {
    if (destroyed) return;
    clearTimeout(resetTimer);
    clearTimeout(hoverTimer);
    focusId = id;
    focusKind = id ? kind : 'overview';
    root.dataset.focus = id || 'overview';
    markers.forEach(m => {
      m.button.classList.toggle('is-active', m.place.id === id);
      m.button.setAttribute('aria-pressed', String(m.place.id === id));
    });
  }
  function resetFocus() {
    pendingSelection = null;
    pointer.set(0, 0);
    setFocus(null, 'overview');
  }
  function select(id) {
    if (destroyed) return;
    const place = locationById.get(id);
    if (!place) return;
    setFocus(id, 'selected');
    pendingSelection = null;
    if (sulking && !place.preview) {
      notify('布鲁斯还在闹小情绪。先哄好他，再一起出门吧。');
      return;
    }
    if (!world) { dispatchSelection(place); return; }
    pendingSelection = { place, at: performance.now(), duration: reducedMotion ? 260 : 1250 };
  }
  function dispatchSelection(place) {
    if (destroyed || (sulking && !place.preview)) return;
    const callback = place.preview ? options.onSelectPreview : options.onSelectPlayable;
    if (typeof callback === 'function') {
      // Host callbacks cannot interrupt the renderer's animation loop.
      queueMicrotask(() => { if (!destroyed && !(sulking && !place.preview)) callback(place.id); });
    } else {
      notify(place.preview ? '这片风景将在二期开放。到时候，和布鲁斯一起去。' : `已选中${place.title}。`);
    }
  }
  function requestHover(id) {
    clearTimeout(resetTimer);
    clearTimeout(hoverTimer);
    if (focusKind === 'selected' || reducedMotion || focusId === id) return;
    hoverTimer = setTimeout(() => setFocus(id, 'hover'), 240);
  }
  function leaveHover() {
    clearTimeout(hoverTimer);
    if (focusKind !== 'selected') resetTimer = setTimeout(resetFocus, 1000);
  }
  for (const place of LOCATIONS) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'wm3d-label';
    button.dataset.location = place.id;
    button.dataset.kind = place.preview ? 'preview' : 'playable';
    button.setAttribute('aria-pressed', 'false');
    button.innerHTML = `<span class="wm3d-pin" aria-hidden="true"></span><span class="wm3d-copy"><span class="wm3d-name">${place.title}</span><span class="wm3d-hint">${place.preview ? '二期' : place.hint}</span></span>`;
    labelsEl.append(button);
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    dot.setAttribute('r', '2');
    svg.append(line, dot);
    const marker = { place, button, line, dot, anchor: new THREE.Vector3(...place.anchor), w: 0, h: 0, last: null, halo: null };
    markers.push(marker);
    listen(button, 'click', () => select(place.id));
    listen(button, 'pointerenter', e => { if (e.pointerType === 'mouse') requestHover(place.id); });
    listen(button, 'pointerleave', leaveHover);
    listen(button, 'focus', () => { if (button.matches(':focus-visible')) requestHover(place.id); });
    listen(button, 'blur', leaveHover);
  }
  listen(root.querySelector('.wm3d-reset'), 'click', resetFocus);
  listen(root, 'keydown', e => { if (e.key === 'Escape') resetFocus(); });
  listen(motionPreference, 'change', e => { reducedMotion = e.matches; pointer.set(0, 0); });

  function setSulking(value) {
    if (destroyed) return;
    sulking = Boolean(value);
    root.dataset.weather = sulking ? 'rain' : 'sun';
    live.textContent = sulking ? '细雨来了。布鲁斯需要你哄一哄。' : '晴天回来了，可以和布鲁斯一起散步。';
    for (const marker of markers) {
      const { place, button } = marker;
      button.querySelector('.wm3d-hint').textContent = place.preview ? '二期' : sulking ? '先哄好布鲁斯' : place.hint;
      button.setAttribute('aria-label', `${place.title}，${place.preview ? '二期预告' : sulking ? '先哄好布鲁斯再出门' : place.hint}`);
      if (!place.preview) button.setAttribute('aria-disabled', String(sulking));
    }
    labelMeasuresDirty = true;
    if (sulking && pendingSelection && !pendingSelection.place.preview) {
      pendingSelection = null;
      notify('先哄好布鲁斯，再一起出门吧。');
    }
  }

  // Solve labels in screen space. Place the playable entrances first, then find
  // collision-free candidates around each projected roof anchor. Previous positions
  // only break ties; label rectangles are never interpolated through one another.
  function layoutLabels() {
    const style = getComputedStyle(root);
    const inset = (name, fallback) => {
      const value = parseFloat(style.getPropertyValue(name));
      return Number.isFinite(value) ? value : fallback;
    };
    let top = inset('--world-map-safe-top', 20);
    let bottom = height - inset('--world-map-safe-bottom', 78);
    const left = inset('--world-map-safe-left', compact ? 12 : 22);
    const right = width - inset('--world-map-safe-right', compact ? 12 : 22);
    if (bottom - top < 220) { top = 12; bottom = height - 58; }
    if (labelMeasuresDirty) {
      markers.forEach(m => { m.button.hidden = false; });
      markers.forEach(m => { m.w = m.button.offsetWidth; m.h = m.button.offsetHeight; });
      labelMeasuresDirty = false;
    }
    const rootRect = root.getBoundingClientRect();
    const placed = [...container.querySelectorAll('[data-world-map-obstacle]')].map(el => {
      const r = el.getBoundingClientRect();
      return { x: r.left - rootRect.left + r.width / 2, y: r.top - rootRect.top + r.height / 2, w: r.width + 12, h: r.height + 12 };
    });
    // On a portrait screen, reserve the middle of the miniature for the buildings.
    // Callouts sit around it, still connected to their actual projected anchors.
    let modelTop = 0, modelBottom = 0;
    if (compact && focusKind !== 'selected') {
      projection.set(-2, 1, 3).project(camera);
      const cy = (1 - projection.y) * height / 2;
      const reservedHeight = Math.min(height * .215, 192);
      modelTop = cy - reservedHeight / 2;
      modelBottom = cy + reservedHeight / 2;
      placed.push({ x: width / 2, y: cy, w: width - 16, h: reservedHeight });
    }
    const gap = compact ? 7 : 9;
    const overlaps = (a, b) => Math.abs(a.x - b.x) < (a.w + b.w) / 2 + gap && Math.abs(a.y - b.y) < (a.h + b.h) / 2 + gap;
    for (const m of markers) {
      projection.copy(m.anchor).project(camera);
      const anchorX = (projection.x + 1) * width / 2;
      const anchorY = (1 - projection.y) * height / 2;
      const offscreen = focusKind === 'selected' && m.place.id !== focusId && (anchorX < left || anchorX > right || anchorY < top || anchorY > bottom || projection.z > 1);
      m.button.hidden = offscreen;
      if (offscreen) { m.line.style.display = m.dot.style.display = 'none'; continue; }
      const minX = left + m.w / 2, maxX = Math.max(minX, right - m.w / 2);
      const minY = top + m.h / 2, maxY = Math.max(minY, bottom - m.h / 2);
      const x = clamp(anchorX, minX, maxX);
      const preferredY = modelBottom ? (m.place.preview ? Math.min(anchorY - m.h / 2 - 12, modelTop - m.h / 2 - 12) : modelBottom + m.h / 2 + 16) : anchorY - m.h / 2 - 12;
      const y = clamp(preferredY, minY, maxY);
      const xs = [x, clamp(x - m.w - gap, minX, maxX), clamp(x + m.w + gap, minX, maxX), minX, maxX, (minX + maxX) / 2];
      const ys = [y];
      if (m.last) { xs.push(clamp(m.last.x, minX, maxX)); ys.push(clamp(m.last.y, minY, maxY)); }
      for (let i = 1; i <= 12; i++) ys.push(clamp(y - i * (m.h + gap), minY, maxY), clamp(y + i * (m.h + gap), minY, maxY));
      let best = null, bestScore = Infinity;
      for (const xx of xs) for (const yy of ys) {
        const candidate = { x: xx, y: yy, w: m.w, h: m.h };
        let score = (xx - x) ** 2 + (yy - y) ** 2;
        if (m.last) score += ((xx - m.last.x) ** 2 + (yy - m.last.y) ** 2) * .1;
        for (const other of placed) if (overlaps(candidate, other)) score += 1e8;
        if (score < bestScore) { bestScore = score; best = candidate; }
      }
      placed.push(best);
      m.last = best;
      m.button.style.transform = `translate3d(${(best.x - m.w / 2).toFixed(2)}px,${(best.y - m.h / 2).toFixed(2)}px,0)`;
      const ax = clamp(anchorX, 3, width - 3), ay = clamp(anchorY, 3, height - 3);
      const endX = clamp(ax, best.x - m.w / 2 + 8, best.x + m.w / 2 - 8);
      const endY = clamp(ay, best.y - m.h / 2 + 5, best.y + m.h / 2 - 5);
      m.line.setAttribute('x1', ax.toFixed(1)); m.line.setAttribute('y1', ay.toFixed(1));
      m.line.setAttribute('x2', endX.toFixed(1)); m.line.setAttribute('y2', endY.toFixed(1));
      m.dot.setAttribute('cx', ax.toFixed(1)); m.dot.setAttribute('cy', ay.toFixed(1));
      const showLeader = Math.hypot(ax - endX, ay - endY) > 18 && projection.z < 1;
      m.line.style.display = m.dot.style.display = showLeader ? '' : 'none';
    }
  }

  function fitOverview() {
    const right = new THREE.Vector3().crossVectors(Y_AXIS, cameraDirection).normalize();
    const up = new THREE.Vector3().crossVectors(cameraDirection, right).normalize();
    const tan = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
    let distance = 10;
    const regions = [
      [-36, 30, -30, 29, 8], [25, 44, -16, 13, 8],
      [-34, -20, -49, -37, 9], [-6, 6, -53, -43, 6], [21, 34, -45, -32, 11],
    ];
    for (const [minX, maxX, minZ, maxZ, maxY] of regions) {
      for (const x of [minX, maxX]) for (const y of [-2, maxY]) for (const z of [minZ, maxZ]) {
        const p = new THREE.Vector3(x, y, z).sub(overviewTarget);
        const forward = p.dot(cameraDirection);
        distance = Math.max(distance, forward + Math.abs(p.dot(right)) / (tan * camera.aspect * .96), forward + Math.abs(p.dot(up)) / (tan * .92));
      }
    }
    return distance * 1.03 * (compact ? .84 : 1);
  }
  function resize() {
    if (destroyed) return;
    width = Math.max(1, root.clientWidth);
    height = Math.max(1, root.clientHeight);
    compact = width < 640;
    labelMeasuresDirty = true;
    markers.forEach(m => { m.last = null; });
    if (!renderer) return;
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, compact ? 1.6 : 1.8));
    renderer.setSize(width, height, false);
    lens?.resize(compact);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    overviewDistance = fitOverview();
    if (!lastFrame) {
      currentTarget.copy(overviewTarget);
      camera.position.copy(cameraDirection).multiplyScalar(overviewDistance).add(currentTarget);
      camera.lookAt(currentTarget);
    }
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    // Re-clamp callouts in the resize observer itself, before the next painted
    // frame, so rotating a phone cannot leave the previous viewport's positions.
    if (world && width > 1 && height > 1) {
      camera.updateMatrixWorld();
      layoutLabels();
    }
  }

  function updateCamera(dt) {
    desiredTarget.copy(overviewTarget);
    let distance = overviewDistance;
    if (focusId) {
      const place = locationById.get(focusId);
      const target = new THREE.Vector3(...place.center);
      target.y = 1.4;
      if (focusKind === 'hover') {
        desiredTarget.lerp(target, .45);
        distance *= .84;
      } else {
        desiredTarget.copy(target);
        const tan = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
        distance = Math.max(place.radius * 3.8, place.radius / (tan * camera.aspect) * 1.1);
      }
    }
    desiredCamera.copy(cameraDirection).multiplyScalar(distance).add(desiredTarget);
    if (!reducedMotion) {
      cameraRight.crossVectors(Y_AXIS, cameraDirection).normalize();
      desiredCamera.addScaledVector(cameraRight, pointer.x * (focusKind === 'selected' ? .55 : 1.8));
      desiredCamera.y -= pointer.y * 1.1;
    }
    const smoothing = 1 - Math.exp(-dt * (reducedMotion ? 24 : 4.4));
    camera.position.lerp(desiredCamera, smoothing);
    currentTarget.lerp(desiredTarget, smoothing);
    camera.lookAt(currentTarget);
    camera.updateMatrixWorld();
    world.scene.fog.near = camera.position.distanceTo(currentTarget) * .94;
    world.scene.fog.far = world.scene.fog.near + 145;
  }
  function schedule() {
    if (!destroyed && world && !frameId && inView && !document.hidden && !contextLost) frameId = requestAnimationFrame(frame);
  }
  function frame(now) {
    frameId = 0;
    if (destroyed || !world || !inView || document.hidden || contextLost) return;
    const dt = lastFrame ? clamp((now - lastFrame) / 1000, .001, .2) : 1 / 60;
    lastFrame = now;
    elapsed += dt;
    updateCamera(dt);
    world.update(elapsed, dt, sulking, reducedMotion);
    for (const marker of markers) {
      const target = marker.place.id === focusId ? .5 : 0;
      marker.halo.material.opacity = lerp(marker.halo.material.opacity, target, 1 - Math.exp(-dt * 5));
      const pulse = reducedMotion ? 1 : 1 + Math.sin(elapsed * 1.7) * .025;
      marker.halo.scale.setScalar(pulse);
      marker.halo.material.color.set(sulking ? '#bfd7e4' : '#fff5bf');
    }
    lens.render(world.scene, camera, focusKind === 'selected' ? currentTarget : residenceFocus);
    layoutLabels();
    root.dataset.ready = 'true';
    if (pendingSelection && now - pendingSelection.at >= pendingSelection.duration && camera.position.distanceTo(desiredCamera) < .65 && currentTarget.distanceTo(desiredTarget) < .3) {
      const selection = pendingSelection;
      pendingSelection = null;
      dispatchSelection(selection.place);
    }
    schedule();
  }

  try {
    compact = root.clientWidth < 640;
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
    renderer.domElement.className = 'wm3d-canvas';
    renderer.domElement.setAttribute('aria-hidden', 'true');
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.04;
    renderer.shadowMap.enabled = true;
    // r187 removed PCFSoftShadowMap; use its supported PCF replacement with
    // shadow radius for the same soft architectural-shadow intent.
    renderer.shadowMap.type = THREE.PCFShadowMap;
    root.prepend(renderer.domElement);
    camera = new THREE.PerspectiveCamera(36, 1, .3, 1100);
    world = buildWorld(renderer, compact, sulking);
    lens = createArchitecturalLens(renderer);
    const hitMaterial = new THREE.MeshBasicMaterial({ visible: false });
    for (const marker of markers) {
      const { place } = marker;
      const hit = new THREE.Mesh(new THREE.BoxGeometry(...place.size), hitMaterial);
      hit.position.set(place.center[0], place.size[1] / 2, place.center[2]);
      hit.userData.location = place.id;
      world.scene.add(hit);
      hitObjects.push(hit);
      const halo = new THREE.Mesh(new THREE.RingGeometry(place.radius, place.radius + .13, 72), new THREE.MeshBasicMaterial({ color: '#fff5bf', opacity: 0, transparent: true, depthWrite: false, side: THREE.DoubleSide }));
      halo.rotation.x = -Math.PI / 2;
      halo.position.set(place.center[0], .36, place.center[2]);
      world.scene.add(halo);
      marker.halo = halo;
    }
    resize();
    const canvas = renderer.domElement;
    let gesture = null, rayHover = null;
    function rayLocation(e) {
      const rect = root.getBoundingClientRect();
      pointerNdc.set((e.clientX - rect.left) / width * 2 - 1, -(e.clientY - rect.top) / height * 2 + 1);
      raycaster.setFromCamera(pointerNdc, camera);
      return raycaster.intersectObjects(hitObjects, false)[0]?.object.userData.location || null;
    }
    listen(canvas, 'pointerdown', e => {
      if (e.button !== 0) return;
      gesture = { id: e.pointerId, x: e.clientX, y: e.clientY, moved: false };
      canvas.setPointerCapture(e.pointerId);
    });
    listen(canvas, 'pointermove', e => {
      const rect = root.getBoundingClientRect();
      if (gesture && gesture.id === e.pointerId) {
        const dx = e.clientX - gesture.x, dy = e.clientY - gesture.y;
        gesture.moved ||= Math.hypot(dx, dy) > 7;
        if (gesture.moved) pointer.set(clamp(dx / 85, -1, 1), clamp(dy / 110, -1, 1));
      } else if (e.pointerType === 'mouse') {
        pointer.set(clamp((e.clientX - rect.left) / width * 2 - 1, -1, 1), clamp((e.clientY - rect.top) / height * 2 - 1, -1, 1));
        const id = rayLocation(e);
        if (id !== rayHover) {
          rayHover = id;
          canvas.style.cursor = id ? 'pointer' : 'default';
          if (id) requestHover(id); else leaveHover();
        }
      }
    });
    listen(canvas, 'pointerup', e => {
      if (!gesture || gesture.id !== e.pointerId) return;
      const shouldSelect = !gesture.moved;
      gesture = null;
      if (canvas.hasPointerCapture(e.pointerId)) canvas.releasePointerCapture(e.pointerId);
      if (shouldSelect) { const id = rayLocation(e); if (id) select(id); }
      if (e.pointerType !== 'mouse') pointer.set(0, 0);
    });
    listen(canvas, 'pointercancel', () => { gesture = null; pointer.set(0, 0); });
    listen(canvas, 'lostpointercapture', () => { gesture = null; });
    listen(canvas, 'pointerleave', () => { if (!gesture) pointer.set(0, 0); rayHover = null; leaveHover(); });
    listen(canvas, 'webglcontextlost', e => {
      e.preventDefault();
      contextLost = true;
      pendingSelection = null;
      notify('画面暂时休息一下，正在等待恢复。');
    });
    listen(canvas, 'webglcontextrestored', () => { contextLost = false; lastFrame = 0; schedule(); });
    listen(document, 'visibilitychange', () => { lastFrame = 0; schedule(); });
    if (typeof IntersectionObserver !== 'undefined') {
      intersectionObserver = new IntersectionObserver(entries => {
        inView = entries[0].isIntersecting;
        if (inView) { lastFrame = 0; schedule(); }
      });
      intersectionObserver.observe(root);
    }
    // Existing model factories are optional; a missing model never blocks mounting.
    reuseCinematicBruce(abort.signal, () => destroyed, model => {
      if (!destroyed) world.dog.adopt(model);
    });
  } catch (error) {
    lens?.dispose();
    if (world) disposeWorld(world);
    renderer?.dispose();
    renderer?.domElement.remove();
    world = null;
    root.classList.add('is-fallback');
    root.dataset.ready = 'fallback';
    const fallback = document.createElement('div');
    fallback.className = 'wm3d-fallback';
    fallback.innerHTML = '<p style="margin-top:-270px">立体画面暂时未能打开。<br>你仍然可以选择地点，陪布鲁斯走走。</p>';
    root.prepend(fallback);
    root.dispatchEvent(new CustomEvent('worldmap3d:error', { bubbles: true, detail: { message: error.message } }));
  }
  if (typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(root);
    markers.forEach(m => resizeObserver.observe(m.button));
  } else listen(window, 'resize', resize);
  setSulking(sulking);
  resize();
  schedule();
  document.fonts?.ready.then(() => { if (!destroyed) labelMeasuresDirty = true; });

  const api = { setSulking, destroy };
  function destroy() {
    if (destroyed) return;
    destroyed = true;
    pendingSelection = null;
    abort.abort();
    cancelAnimationFrame(frameId);
    clearTimeout(hoverTimer); clearTimeout(resetTimer); clearTimeout(toastTimer);
    resizeObserver?.disconnect();
    intersectionObserver?.disconnect();
    listeners.forEach(remove => remove());
    if (world) disposeWorld(world);
    lens?.dispose();
    renderer?.renderLists.dispose();
    renderer?.dispose();
    renderer?.forceContextLoss();
    world = null;
    renderer = null;
    camera = null;
    lens = null;
    markers.length = 0;
    hitObjects.length = 0;
    listeners.length = 0;
    root.remove();
    if (changedPosition && container.style.position === 'relative') container.style.position = oldPosition;
    if (mountedMaps.get(container) === api) mountedMaps.delete(container);
  }
  return api;
}

function disposeObject(root, extraTextures = []) {
  const geometries = new Set(), materials = new Set(), textures = new Set(extraTextures);
  root.traverse(object => {
    if (object.geometry) geometries.add(object.geometry);
    const list = object.material ? (Array.isArray(object.material) ? object.material : [object.material]) : [];
    for (const material of list) {
      materials.add(material);
      for (const value of Object.values(material)) if (value?.isTexture) textures.add(value);
    }
    if (object.isLight) object.shadow?.dispose();
  });
  geometries.forEach(g => g.dispose());
  materials.forEach(m => m.dispose());
  textures.forEach(t => t.dispose());
}

function disposeWorld(world) {
  world.pool.getRenderTarget().dispose();
  world.environment.dispose();
  disposeObject(world.scene, world.resources);
}

async function reuseCinematicBruce(signal, isDestroyed, adopt) {
  const url = new URL('./cinematic/bruceModel.js', import.meta.url);
  try {
    const response = await fetch(url, { signal });
    if (!response.ok) return;
    const source = await response.text();
    // SPA fallback HTML and models that directly import a CDN are not executable
    // local model modules. The lightweight garden dog stays in place in that case.
    if (/^\s*</.test(source) || /(?:from\s*|import\s*\(?\s*)['"](?:https?:|\/\/)/.test(source) || isDestroyed()) return;
    const imported = await import(/* @vite-ignore */ url.href);
    if (isDestroyed()) return;
    const factories = [imported.createBruceModel, imported.createBruce, imported.buildBruceModel, imported.default].filter(f => typeof f === 'function');
    for (const factory of factories) {
      let result;
      try { result = await factory(THREE); } catch { continue; }
      const model = [result, result?.group, result?.root, result?.model, result?.mesh, result?.scene].find(o => o?.isObject3D);
      if (!model) continue;
      if (isDestroyed()) { disposeObject(model); return; }
      // Own cloned resources so destroy() never disposes a cinematic module's
      // shared geometry, material, or texture caches.
      const clone = model.clone(true);
      clone.traverse(o => {
        if (o.geometry) o.geometry = o.geometry.clone();
        if (o.material) {
          const cloneMaterial = material => {
            const owned = material.clone();
            for (const [key, value] of Object.entries(owned)) if (value?.isTexture) owned[key] = value.clone();
            return owned;
          };
          o.material = Array.isArray(o.material) ? o.material.map(cloneMaterial) : cloneMaterial(o.material);
        }
        o.castShadow = true;
      });
      clone.updateMatrixWorld(true);
      const bounds = new THREE.Box3().setFromObject(clone);
      const size = bounds.getSize(new THREE.Vector3());
      if (!Number.isFinite(size.y) || size.y < .0001) { disposeObject(clone); continue; }
      const normalized = new THREE.Group();
      const scaled = new THREE.Group();
      scaled.add(clone);
      normalized.add(scaled);
      const scale = 1.6 / size.y;
      scaled.scale.setScalar(scale);
      const center = bounds.getCenter(new THREE.Vector3());
      scaled.position.set(-center.x * scale, -bounds.min.y * scale, -center.z * scale);
      if (isDestroyed()) { disposeObject(normalized); return; }
      adopt(normalized);
      return;
    }
  } catch (error) {
    // Abort, absent files, and incompatible legacy modules all keep the fallback.
    if (error.name !== 'AbortError') return;
  }
}
