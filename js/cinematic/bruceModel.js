import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { clamp, damp, disposeTree, ellipsoid, mesh, random, tube } from './math.js';

const MOODS = {
  happy: {
    head: -0.04,
    tilt: 0.02,
    ears: 0.1,
    tail: 5.1,
    tailHeight: -0.22,
    low: 0,
    roll: 0,
    turn: 0,
    eye: 1,
  },
  excited: {
    head: -0.16,
    tilt: -0.09,
    ears: 0.2,
    tail: 11,
    tailHeight: -0.48,
    low: -0.02,
    roll: 0,
    turn: 0,
    eye: 1,
  },
  curious: {
    head: -0.08,
    tilt: -0.23,
    ears: 0.08,
    tail: 3.1,
    tailHeight: -0.1,
    low: 0,
    roll: 0,
    turn: 0,
    eye: 1,
  },
  warn: {
    head: 0.12,
    tilt: 0.04,
    ears: 1.02,
    tail: 1.4,
    tailHeight: 0.15,
    low: -0.04,
    roll: 0,
    turn: 0,
    eye: 0.85,
  },
  sulk: {
    head: 0.4,
    tilt: -0.12,
    ears: 0.72,
    tail: 0.45,
    tailHeight: 0.52,
    low: -0.15,
    roll: 0,
    turn: Math.PI,
    eye: 0.55,
  },
  sleep: {
    head: 0.19,
    tilt: 0.08,
    ears: 0.06,
    tail: 0.75,
    tailHeight: 0.4,
    low: -0.24,
    roll: -0.16,
    turn: 0,
    eye: 0.04,
  },
  belly: {
    head: -0.16,
    tilt: 0.1,
    ears: 0.36,
    tail: 7.5,
    tailHeight: 0,
    low: 0.05,
    roll: Math.PI * 0.78,
    turn: -0.3,
    eye: 0.84,
  },
};

function furFringe(parent, material, center, radii, count, seed) {
  const rng = random(seed),
    rings = 6,
    sides = 4,
    strands = [];
  const positions = new Float32Array(count * rings * sides * 3),
    normals = new Float32Array(positions.length),
    uvs = new Float32Array(count * rings * sides * 2),
    indices = [],
    components = ['x', 'y', 'z'];
  for (let i = 0; i < count; i++) {
    const theta = rng() * Math.PI * 2,
      h = rng() * 2 - 1,
      w = Math.sqrt(1 - h * h);
    const n = new THREE.Vector3(Math.cos(theta) * w, h, Math.sin(theta) * w);
    const base = new THREE.Vector3(
      center[0] + n.x * radii[0],
      center[1] + n.y * radii[1],
      center[2] + n.z * radii[2],
    );
    strands.push({ base, n, length: 0.65 + rng() * 0.65, width: 0.0014 + rng() * 0.0014 });
    for (let ring = 0; ring < rings - 1; ring++)
      for (let side = 0; side < sides; side++) {
        const a = (i * rings + ring) * sides + side,
          b = (i * rings + ring) * sides + ((side + 1) % sides);
        indices.push(a, b, a + sides, b, b + sides, a + sides);
      }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
  geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
  geometry.setIndex(indices);
  geometry.attributes.position.setUsage(THREE.DynamicDrawUsage);
  geometry.attributes.normal.setUsage(THREE.DynamicDrawUsage);
  const coat = material.clone();
  coat.sheen = 0.3;
  coat.roughness = 0.94;
  const fringe = mesh(geometry, coat, parent);
  fringe.frustumCulled = false;
  const gravity = new THREE.Vector3(),
    tangent = new THREE.Vector3(),
    end = new THREE.Vector3(),
    p = new THREE.Vector3(),
    direction = new THREE.Vector3(),
    side = new THREE.Vector3(),
    normal = new THREE.Vector3(),
    axis = new THREE.Vector3();
  // Curved, gravity-draped fibres, rather than straight spikes along the normal.
  function update(roll) {
    gravity.set(-Math.sin(roll), -Math.cos(roll), 0);
    strands.forEach((strand, i) => {
      const { base, n, length, width } = strand,
        top = Math.max(0, n.y);
      tangent.copy(gravity).addScaledVector(n, -gravity.dot(n));
      if (tangent.lengthSq() < 0.05) tangent.set(0, 0, -1);
      tangent.normalize();
      end
        .copy(base)
        .addScaledVector(n, 0.018 + top * 0.045)
        .addScaledVector(gravity, 0.09 * length * (1 - top * 0.75))
        .addScaledVector(tangent, 0.045 * length);
      for (let ring = 0; ring < rings; ring++) {
        const t = ring / (rings - 1),
          arc = Math.sin(t * Math.PI),
          radius = width * Math.pow(1 - t, 0.7) + 0.0001;
        p.copy(base)
          .lerp(end, t)
          .addScaledVector(n, arc * 0.021)
          .addScaledVector(tangent, arc * 0.012);
        direction
          .subVectors(end, base)
          .addScaledVector(n, Math.cos(t * Math.PI) * Math.PI * 0.021)
          .addScaledVector(tangent, Math.cos(t * Math.PI) * Math.PI * 0.012)
          .normalize();
        axis.set(Math.abs(direction.z) > 0.9 ? 1 : 0, 0, Math.abs(direction.z) > 0.9 ? 0 : 1);
        side.crossVectors(direction, axis).normalize();
        normal.crossVectors(direction, side).normalize();
        for (let s = 0; s < sides; s++) {
          const a = (s / sides) * Math.PI * 2,
            vertex = (i * rings + ring) * sides + s,
            c = Math.cos(a),
            sn = Math.sin(a);
          for (let k = 0; k < 3; k++) {
            const key = components[k],
              nn = side[key] * c + normal[key] * sn;
            positions[vertex * 3 + k] = p[key] + nn * radius;
            normals[vertex * 3 + k] = nn;
          }
          uvs[vertex * 2] = s / sides;
          uvs[vertex * 2 + 1] = t;
        }
      }
    });
    geometry.attributes.position.needsUpdate = true;
    geometry.attributes.normal.needsUpdate = true;
  }
  update(0);
  fringe.userData.groom = { update };
  return fringe;
}

function createScarf(parent, mats) {
  const root = new THREE.Group();
  root.position.set(0, 0.73, 0.78);
  parent.add(root);
  const collar = mesh(new THREE.TorusGeometry(0.235, 0.047, 10, 40), mats.scarf, root);
  collar.rotation.x = Math.PI / 2;
  collar.scale.z = 0.65;
  const geo = new THREE.PlaneGeometry(0.4, 0.4, 12, 14),
    pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const y = pos.getY(i),
      v = (0.2 - y) / 0.4;
    pos.setXYZ(
      i,
      pos.getX(i) * (1 - v * 0.91),
      y - 0.14,
      0.29 + 0.055 * Math.sin(v * 3.1) + 0.018 * Math.cos(pos.getX(i) * 40),
    );
  }
  geo.computeVertexNormals();
  const bib = mesh(geo, mats.scarf, root);
  ellipsoid(root, mats.scarf, [0.19, 0.01, 0.12], [0.07, 0.055, 0.075]);
  const end = ellipsoid(root, mats.scarf, [0.29, -0.08, 0.12], [0.14, 0.035, 0.065]);
  end.rotation.z = -0.45;
  const tag = mesh(
    new THREE.CylinderGeometry(0.036, 0.036, 0.012, 24),
    mats.brass,
    root,
    [0.055, -0.12, 0.24],
  );
  tag.rotation.x = Math.PI / 2;
  return { root, bib, end };
}

function sculptBruce(mats) {
  const sculpt = new THREE.Group(),
    body = new THREE.Group();
  sculpt.add(body);
  // Continuous pear-shaped torso: a low, elongated rib cage, not a chain of blocks.
  const profile = [
    [0, -1.08],
    [0.18, -0.99],
    [0.29, -0.8],
    [0.32, -0.49],
    [0.305, -0.05],
    [0.33, 0.43],
    [0.29, 0.72],
    [0.17, 0.88],
    [0, 0.93],
  ];
  const torsoGeo = new THREE.LatheGeometry(
    profile.map((p) => new THREE.Vector2(...p)),
    40,
  );
  torsoGeo.rotateX(Math.PI / 2);
  torsoGeo.scale(1, 0.94, 1);
  mesh(torsoGeo, mats.fur, body, [0, 0.53, -0.12]);
  ellipsoid(body, mats.paleFur, [0, 0.48, 0.61], [0.285, 0.37, 0.38]);
  furFringe(body, mats.paleFur, [0, 0.48, 0.64], [0.26, 0.3, 0.28], 240, 39);
  furFringe(body, mats.fur, [0, 0.48, -0.2], [0.3, 0.25, 0.86], 720, 17);
  const legs = [];
  for (const z of [0.61, -0.79])
    for (const side of [-1, 1]) {
      const leg = new THREE.Group();
      leg.position.set(side * 0.235, 0.41, z);
      body.add(leg);
      legs.push(leg);
      ellipsoid(leg, mats.fur, [0, -0.13, 0], [0.105, 0.23, 0.12]);
      ellipsoid(leg, mats.paleFur, [0, -0.32, 0.065], [0.132, 0.085, 0.18]);
      for (let toe = -1; toe <= 1; toe++) {
        ellipsoid(leg, mats.paleFur, [toe * 0.054, -0.337, 0.18], [0.045, 0.049, 0.061], 16);
        ellipsoid(leg, mats.nose, [toe * 0.054, -0.334, 0.226], [0.013, 0.012, 0.019], 12);
      }
    }
  const head = new THREE.Group();
  head.position.set(0, 0.88, 0.72);
  body.add(head);
  ellipsoid(head, mats.fur, [0, 0.08, 0.03], [0.247, 0.24, 0.27]);
  const muzzleCurve = new THREE.CatmullRomCurve3(
    [
      [0.16, 0, 0],
      [0.155, 0.08, 0],
      [0.13, 0.22, 0],
      [0.095, 0.39, 0],
      [0.075, 0.45, 0],
      [0, 0.47, 0],
    ].map((p) => new THREE.Vector3(...p)),
  );
  const muzzleGeo = new THREE.LatheGeometry(
    muzzleCurve.getPoints(24).map((p) => new THREE.Vector2(p.x, p.y)),
    32,
  );
  muzzleGeo.rotateX(Math.PI / 2);
  muzzleGeo.scale(1, 0.69, 1);
  mesh(muzzleGeo, mats.fur, head, [0, -0.065, 0.15]);
  ellipsoid(head, mats.paleFur, [0, -0.135, 0.34], [0.116, 0.062, 0.245]);
  ellipsoid(head, mats.nose, [0, -0.045, 0.62], [0.102, 0.067, 0.053]);
  for (const side of [-1, 1]) {
    ellipsoid(head, mats.black, [side * 0.051, -0.052, 0.666], [0.024, 0.015, 0.007], 14);
    ellipsoid(head, mats.glint, [side * 0.027, -0.013, 0.669], [0.01, 0.004, 0.003], 12);
    // A restrained lower lip and whisker follicles preserve the long dachshund muzzle.
    tube(
      head,
      mats.nose,
      [
        [0, -0.115, 0.633],
        [side * 0.06, -0.145, 0.53],
        [side * 0.119, -0.14, 0.37],
      ],
      0.006,
      12,
    );
    for (let i = 0; i < 4; i++)
      ellipsoid(
        head,
        mats.earFur,
        [side * (0.11 + i * 0.005), -0.055 - (i % 2) * 0.03, 0.43 - Math.floor(i / 2) * 0.05],
        [0.004, 0.004, 0.004],
        8,
      );
  }
  const eyes = [];
  for (const side of [-1, 1]) {
    const eye = new THREE.Group();
    eye.position.set(side * 0.164, 0.125, 0.224);
    eye.rotation.y = side * 0.18;
    head.add(eye);
    eyes.push(eye);
    ellipsoid(eye, mats.earFur, [0, -0.002, -0.012], [0.068, 0.063, 0.033]);
    ellipsoid(eye, mats.eye, [0, 0, 0.009], [0.052, 0.052, 0.027]);
    ellipsoid(eye, mats.iris, [side * -0.005, -0.003, 0.034], [0.034, 0.039, 0.007]);
    ellipsoid(eye, mats.eye, [side * -0.005, -0.002, 0.041], [0.023, 0.031, 0.005]);
    ellipsoid(eye, mats.glint, [-0.014, 0.019, 0.044], [0.01, 0.012, 0.004], 16);
    ellipsoid(eye, mats.glint, [0.014, -0.011, 0.044], [0.004, 0.005, 0.002], 12);
    ellipsoid(head, mats.paleFur, [side * 0.164, 0.195, 0.19], [0.045, 0.018, 0.03]);
  }
  const ears = [];
  for (const side of [-1, 1]) {
    const ear = new THREE.Group();
    ear.position.set(side * 0.22, 0.19, -0.015);
    head.add(ear);
    ears.push(ear);
    const shape = new THREE.SphereGeometry(1, 28, 28),
      p = shape.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const y = p.getY(i),
        x = p.getX(i),
        z = p.getZ(i);
      p.setXYZ(
        i,
        x * (0.16 + 0.045 * (1 - y)),
        (y - 1) * 0.3,
        z * 0.105 + 0.045 * Math.sin(y * 2.3),
      );
    }
    shape.computeVertexNormals();
    mesh(shape, mats.earFur, ear);
    furFringe(ear, mats.fur, [0, -0.34, 0.015], [0.173, 0.265, 0.105], 300, side === 1 ? 23 : 19);
  }
  const tail = new THREE.Group();
  tail.position.set(0, 0.61, -1.12);
  body.add(tail);
  tube(
    tail,
    mats.fur,
    [
      [0, 0, 0],
      [0, 0.03, -0.23],
      [0.01, 0.23, -0.45],
      [0.02, 0.32, -0.64],
    ],
    0.065,
  );
  furFringe(tail, mats.paleFur, [0, 0.1, -0.35], [0.065, 0.14, 0.25], 65, 45);
  const scarf = createScarf(body, mats);
  sculpt.traverse((o) => {
    if (o.isMesh) {
      o.castShadow = true;
      o.receiveShadow = true;
    }
  });
  return { sculpt, body, head, ears, eyes, legs, tail, scarf };
}

/**
 * +Z is Bruce's nose; ground is Y=0. Root positioning belongs to the director.
 * The same emotional pose drives the sculpt and any named GLB bones.
 */
export function createBruceModel(
  materials,
  { modelUrl = new URL('../../assets/models/bruce.glb', import.meta.url), onModeChange } = {},
) {
  const root = new THREE.Group();
  root.name = 'Bruce';
  const motion = new THREE.Group();
  root.add(motion);
  const rig = sculptBruce(materials);
  motion.add(rig.sculpt);
  const halo = mesh(
    new THREE.TorusGeometry(0.51, 0.014, 8, 60),
    new THREE.MeshBasicMaterial({
      color: '#f9db9a',
      transparent: true,
      opacity: 0,
      depthWrite: false,
    }),
    root,
    [0, 0.05, 0.1],
  );
  halo.rotation.x = Math.PI / 2;
  halo.scale.y = 1.65;
  const abort = new AbortController();
  let destroyed = false,
    mode = 'procedural',
    mood = 'happy',
    mixer,
    loaded,
    bones = [];
  let pose = { ...MOODS.happy },
    gazeX = 0,
    gazeY = 0,
    phase = 0,
    restPose = 0,
    loadedScarf,
    gazeTarget = null;
  const fringes = [];
  rig.sculpt.traverse((o) => {
    if (o.userData.groom) fringes.push(o);
  });
  let lastGroomRoll = 0;
  let lastMood = '',
    animationActions = [];
  const ready = (async () => {
    try {
      const response = await fetch(modelUrl, { signal: abort.signal });
      if (!response.ok) return mode;
      const buffer = await response.arrayBuffer();
      if (destroyed) return mode;
      const gltf = await new GLTFLoader().parseAsync(buffer, new URL('.', modelUrl).href);
      if (destroyed) {
        disposeTree(gltf.scene);
        return mode;
      }
      loaded = gltf.scene;
      const bounds = new THREE.Box3().setFromObject(loaded),
        size = bounds.getSize(new THREE.Vector3());
      if (!Number.isFinite(size.length()) || size.length() < 0.0001) {
        disposeTree(loaded);
        loaded = null;
        return mode;
      }
      const scale = 2.65 / Math.max(size.x, size.y, size.z),
        center = bounds.getCenter(new THREE.Vector3());
      const normalized = new THREE.Group();
      normalized.scale.setScalar(scale);
      normalized.add(loaded);
      loaded.position.sub(new THREE.Vector3(center.x, bounds.min.y, center.z));
      loaded.traverse((o) => {
        if (o.isMesh) {
          o.castShadow = o.receiveShadow = true;
        }
        if (o.isBone)
          bones.push({
            bone: o,
            rest: o.rotation.clone(),
            kind: /head|neck/i.test(o.name)
              ? 'head'
              : /tail/i.test(o.name)
                ? 'tail'
                : /ear/i.test(o.name)
                  ? 'ear'
                  : '',
          });
      });
      let hasScarf = false;
      loaded.traverse((o) => {
        if (/scarf|bandana|neckerchief/i.test(o.name)) hasScarf = true;
      });
      if (!hasScarf) loadedScarf = createScarf(motion, materials);
      motion.add(normalized);
      rig.sculpt.visible = false;
      if (gltf.animations.length) {
        mixer = new THREE.AnimationMixer(loaded);
        animationActions = gltf.animations.map((clip) => ({
          name: clip.name,
          action: mixer.clipAction(clip),
        }));
      }
      mode = 'glb';
      onModeChange?.(mode);
      return mode;
    } catch (error) {
      if (error.name !== 'AbortError') onModeChange?.('procedural', error);
      return mode;
    }
  })();

  return {
    root,
    ready,
    get mode() {
      return mode;
    },
    get mood() {
      return mood;
    },
    setMood(next) {
      if (!Object.hasOwn(MOODS, next)) throw new RangeError(`Unknown Bruce mood: ${next}`);
      mood = next;
    },
    lookAt(point) {
      gazeTarget = point?.isVector3 ? point.clone() : null;
    },
    getCollarPosition(target = new THREE.Vector3()) {
      return (loadedScarf?.root || rig.scarf.root).getWorldPosition(target);
    },
    update(
      dt,
      time,
      {
        gaze = [0, 0],
        walking = 0,
        petting = 0,
        shake = 0,
        resting = 0,
        jump = 0,
        halo: haloAmount = 0,
      } = {},
    ) {
      if (destroyed) return;
      if (gazeTarget) {
        const p = root.worldToLocal(gazeTarget.clone());
        gaze = [
          Math.atan2(p.x, p.z - 0.72),
          -Math.atan2(p.y - 0.95, Math.max(0.1, Math.abs(p.z - 0.72))),
        ];
      }
      for (const key of Object.keys(pose))
        pose[key] = damp(pose[key], MOODS[mood][key], key === 'turn' ? 2.2 : 5, dt);
      gazeX = damp(gazeX, clamp(gaze[0], -1, 1), 4, dt);
      gazeY = damp(gazeY, clamp(gaze[1], -1, 1), 4, dt);
      phase += dt * pose.tail;
      const breath = Math.sin(time * (mood === 'sleep' ? 1.7 : 2.3));
      const bounce = Math.abs(Math.sin(time * 12)) * 0.055 * walking;
      restPose = damp(restPose, Math.max(resting, mood === 'sleep' ? 1 : 0), 3, dt);
      motion.position.x = Math.sin(pose.roll) * 0.48;
      motion.position.y =
        pose.low -
        restPose * (mood === 'sleep' ? 0 : 0.2) +
        0.48 * (1 - Math.cos(pose.roll)) +
        bounce +
        Math.max(0, Math.sin(jump * Math.PI)) * 0.34;
      motion.rotation.set(
        0,
        pose.turn,
        pose.roll +
          Math.sin(time * 30) * shake * 0.09 +
          (mood === 'warn' ? Math.sin(time * 32) * 0.006 : 0),
      );
      if (Math.abs(pose.roll - lastGroomRoll) > 0.015) {
        lastGroomRoll = pose.roll;
        for (const fringe of fringes) fringe.userData.groom.update(pose.roll);
      }
      motion.scale.set(1 + breath * 0.005, 1 + breath * 0.012, 1 + breath * 0.007);
      rig.head.rotation.set(
        pose.head + gazeY * 0.1 + Math.sin(time * 2) * petting * 0.05,
        gazeX * 0.2,
        pose.tilt + Math.sin(time * 29) * shake * 0.18,
      );
      rig.ears.forEach((ear, i) => {
        const side = i === 0 ? -1 : 1;
        ear.rotation.set(
          -pose.ears * 0.15,
          side * pose.ears * 0.52,
          side *
            (pose.ears +
              Math.sin(time * 11 + i) * 0.06 * walking +
              Math.sin(time * 25) * shake * 0.38),
        );
      });
      rig.tail.rotation.y = Math.sin(phase) * (mood === 'sulk' ? 0.04 : 0.48);
      rig.tail.rotation.x = pose.tailHeight;
      rig.legs.forEach((leg, i) => {
        leg.rotation.x =
          Math.sin(time * 13 + (i === 0 || i === 3 ? 0 : Math.PI)) * 0.67 * walking +
          restPose * (i < 2 ? -0.85 : 0.85);
      });
      const blink = Math.sin(time * 0.83) > 0.998 ? 0.12 : 1;
      rig.eyes.forEach((eye) => {
        eye.scale.y = Math.max(0.035, pose.eye * blink);
      });
      rig.scarf.root.rotation.z =
        Math.sin(time * 2.1) * 0.027 + Math.sin(time * 11) * walking * 0.04;
      rig.scarf.end.rotation.x = Math.sin(time * 5) * 0.15 * (walking + 0.2);
      if (loadedScarf) {
        loadedScarf.root.rotation.z = rig.scarf.root.rotation.z;
        loadedScarf.end.rotation.x = rig.scarf.end.rotation.x;
      }
      halo.material.opacity = damp(
        halo.material.opacity,
        haloAmount * 0.32 + petting * 0.17,
        4,
        dt,
      );
      halo.scale.set(1 + Math.sin(time * 2) * 0.04, 1.65 + Math.sin(time * 2) * 0.05, 1);
      if (mixer) {
        if (lastMood !== mood) {
          const wanted =
            animationActions.find((a) =>
              (walking ? /run|walk/i : mood === 'sleep' ? /sleep|rest/i : /idle|breath/i).test(
                a.name,
              ),
            ) || animationActions[0];
          animationActions.forEach((a) =>
            a === wanted ? a.action.reset().fadeIn(0.4).play() : a.action.fadeOut(0.4),
          );
          lastMood = mood;
        }
        mixer.update(dt);
      }
      for (const b of bones) {
        if (b.kind === 'head') {
          b.bone.rotation.x = b.rest.x + pose.head;
          b.bone.rotation.z = b.rest.z + pose.tilt;
          b.bone.rotation.y = b.rest.y + gazeX * 0.12;
        }
        if (b.kind === 'tail') b.bone.rotation.y = b.rest.y + Math.sin(phase) * 0.22;
        if (b.kind === 'ear')
          b.bone.rotation.z = b.rest.z + pose.ears * (/left|\.l|_l/i.test(b.bone.name) ? -1 : 1);
      }
      if (loaded && !bones.some((b) => b.kind === 'head')) motion.rotation.x = pose.head * 0.15;
    },
    destroy() {
      destroyed = true;
      abort.abort();
      mixer?.stopAllAction();
      if (loaded) mixer?.uncacheRoot(loaded);
      bones = [];
      animationActions = [];
    },
  };
}
