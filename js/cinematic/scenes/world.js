import * as THREE from 'three';
import { clamp, ellipsoid, mesh, random, roundedBox, tube } from '../math.js';
import { textTexture } from '../materials.js';
import { createLeash } from '../leash.js';

function box(parent, material, position, size, radius = 0.07) {
  return mesh(roundedBox(...size, radius), material, parent, position);
}

function label(parent, text, position, width, height, options = {}) {
  const material = new THREE.MeshBasicMaterial({
    map: textTexture(text, options),
    side: THREE.DoubleSide,
  });
  const sign = mesh(new THREE.PlaneGeometry(width, height), material, parent, position);
  sign.castShadow = false;
  return sign;
}

function plant(parent, mats, position, scale = 1, seed = 9) {
  const root = new THREE.Group();
  root.position.fromArray(position);
  root.scale.setScalar(scale);
  parent.add(root);
  mesh(new THREE.CylinderGeometry(0.22, 0.15, 0.38, 24), mats.ceramic, root, [0, 0.19, 0]);
  const rng = random(seed);
  for (let i = 0; i < 8; i++) {
    const a = i * 2.4,
      x = Math.cos(a) * (0.15 + rng() * 0.2),
      z = Math.sin(a) * 0.25,
      y = 0.7 + rng() * 0.3;
    tube(
      root,
      mats.moss,
      [
        [0, 0.3, 0],
        [x * 0.6, y * 0.7, z * 0.6],
        [x, y, z],
      ],
      0.012,
      9,
    );
    const leaf = ellipsoid(root, mats.leaf, [x, y, z], [0.1, 0.27, 0.025], 12);
    leaf.rotation.set(0.4 + rng() * 0.5, a, -0.5);
  }
  return root;
}

function tree(parent, mats, position, seed = 3, scale = 1) {
  const root = new THREE.Group();
  root.position.fromArray(position);
  root.scale.setScalar(scale);
  parent.add(root);
  const rng = random(seed);
  tube(
    root,
    mats.walnut,
    [
      [0, 0, 0],
      [0.04, 1.3, 0.06],
      [-0.08, 2.7, 0],
      [0.1, 4.2, 0.1],
    ],
    0.12,
    20,
  );
  for (let i = 0; i < 5; i++) {
    const a = i * 2.4,
      x = Math.cos(a),
      z = Math.sin(a),
      y = 2.4 + i * 0.23;
    tube(
      root,
      mats.walnut,
      [
        [0, y, 0],
        [x * 0.55, y + 0.35, z * 0.55],
        [x * 1.15, y + 0.75, z],
      ],
      0.045,
      12,
    );
  }
  const leafGeometry = new THREE.SphereGeometry(1, 6, 4),
    leaves = new THREE.InstancedMesh(leafGeometry, mats.leaf, 160),
    dummy = new THREE.Object3D();
  for (let i = 0; i < 160; i++) {
    const a = rng() * Math.PI * 2,
      r = Math.sqrt(rng()) * 1.6;
    dummy.position.set(Math.cos(a) * r, 3.5 + rng() * 1.3 - r * 0.13, Math.sin(a) * r);
    dummy.rotation.set(rng() * 0.8, rng() * 6, rng() * 2);
    dummy.scale.set(0.14 + rng() * 0.15, 0.03, 0.22 + rng() * 0.18);
    dummy.updateMatrix();
    leaves.setMatrixAt(i, dummy.matrix);
    leaves.setColorAt(
      i,
      new THREE.Color().setHSL(0.2 + rng() * 0.07, 0.23 + rng() * 0.18, 0.2 + rng() * 0.18),
    );
  }
  leaves.castShadow = true;
  leaves.receiveShadow = true;
  root.add(leaves);
  return root;
}

function rug(parent, mats, position, width = 3.8, depth = 3) {
  const r = box(parent, mats.linen, position, [width, 0.045, depth], 0.02);
  // A woven border catches light without covering Bruce's silhouette.
  for (const x of [-width / 2 + 0.12, width / 2 - 0.12])
    box(r, mats.blanket, [x, 0.025, 0], [0.022, 0.006, depth - 0.15], 0.001);
  return r;
}

function sofa(parent, mats) {
  const root = new THREE.Group();
  root.position.set(-1.1, 0, -2.4);
  parent.add(root);
  for (const x of [-1.45, 1.45])
    for (const z of [-0.36, 0.36])
      mesh(new THREE.CylinderGeometry(0.035, 0.025, 0.25, 12), mats.walnut, root, [x, 0.13, z]);
  box(root, mats.moss, [0, 0.43, 0], [3.5, 0.55, 1.2], 0.2);
  box(root, mats.moss, [0, 1.0, -0.43], [3.5, 0.85, 0.36], 0.17);
  for (const x of [-1.64, 1.64]) box(root, mats.moss, [x, 0.81, 0.05], [0.29, 0.76, 1.22], 0.12);
  for (const x of [-0.83, 0.83]) box(root, mats.linen, [x, 0.73, 0.04], [1.47, 0.18, 1], 0.08);
  const pillow = box(root, mats.blanket, [-1.1, 1.07, -0.19], [0.58, 0.55, 0.17], 0.07);
  pillow.rotation.z = -0.2;
  return root;
}

function createInterior(group, mats, config, targets, props) {
  const rain = config.rain;
  const floor = mesh(new THREE.PlaneGeometry(30, 30), mats.wood, group);
  floor.rotation.x = -Math.PI / 2;
  box(group, mats.plaster, [5.4, 2.6, -3.8], [1.2, 5.2, 0.25]);
  box(group, mats.moss, [-6.2, 2.5, -2], [0.25, 5, 9]);
  const outside = mesh(
    new THREE.PlaneGeometry(22, 12),
    new THREE.MeshBasicMaterial({ color: rain ? '#657e8a' : '#a8b6a1' }),
    group,
    [0, 4, -8],
  );
  for (let i = 0; i < 7; i++) tree(group, mats, [-8 + i * 2.5, -0.2, -6.9 - (i % 2)], i + 8, 1.3);
  for (const x of [-5.5, -2.8, -0.1, 2.6, 5.3])
    box(group, mats.walnut, [x, 2.7, -3.75], [0.06, 5.4, 0.09], 0.015);
  for (const y of [0.1, 4.9]) box(group, mats.walnut, [0, y, -3.75], [11, 0.07, 0.11], 0.015);
  const glass = mesh(new THREE.PlaneGeometry(10.8, 4.8), mats.glass, group, [0, 2.5, -3.76]);
  props.window = glass;
  props.outside = outside;
  rug(group, mats, [0, 0.025, 0.1]);
  sofa(group, mats);
  // Tall linen curtain at the left window; the cloth, rather than a UI control, moves.
  const curtainGeo = new THREE.PlaneGeometry(1.5, 4.65, 32, 2),
    cp = curtainGeo.attributes.position;
  for (let i = 0; i < cp.count; i++) cp.setZ(i, Math.sin(cp.getX(i) * 22) * 0.075);
  curtainGeo.computeVertexNormals();
  props.curtainCloth = mesh(curtainGeo, mats.linen, group, [-4.7, 2.5, -3.55]);
  plant(group, mats, [-3.7, 0, -1.8], 1.6);
  plant(group, mats, [4.5, 0, -3], 1.1, 17);
  // Floor lamp with a lit inner shade, reflected in Bruce's eyes.
  mesh(new THREE.CylinderGeometry(0.27, 0.3, 0.055, 32), mats.brass, group, [2.8, 0.035, -2.5]);
  mesh(new THREE.CylinderGeometry(0.018, 0.018, 2.7, 12), mats.brass, group, [2.8, 1.35, -2.5]);
  mesh(new THREE.ConeGeometry(0.43, 0.46, 40, 1, true), mats.linen, group, [2.8, 2.63, -2.5]);
  const lamp = new THREE.PointLight('#ffc378', rain ? 13 : 4, 8, 2);
  lamp.position.set(2.8, 2.4, -2.4);
  group.add(lamp);
  props.lamp = lamp;
  if (config.mode === 'kitchen') {
    box(group, mats.walnut, [-0.5, 0.63, -2.45], [3.8, 1.25, 1], 0.08);
    box(group, mats.stone, [-0.5, 1.3, -2.4], [4, 0.13, 1.12], 0.06);
    label(group, 'SLOW MORNINGS', [-0.5, 2.8, -3.6], 2, 0.35, {
      background: '#d8d2c1',
      color: '#474d41',
      fontSize: 55,
    });
  }
  if (config.props.includes('vinyl')) {
    const table = box(group, mats.walnut, [1.9, 0.48, -0.65], [1.1, 0.95, 0.8], 0.04);
    props.vinylTable = table;
    label(table, 'VINYL', [0, 0.17, 0.407], 0.55, 0.14, {
      background: '#4d3127',
      color: '#e5d8bc',
      fontSize: 58,
    });
  }
}

function createStreet(group, mats, config, props) {
  const ground = mesh(new THREE.PlaneGeometry(60, 80), mats.stone, group, [0, -0.025, -10]);
  ground.rotation.x = -Math.PI / 2;
  const path = box(group, mats.plaster, [0, -0.04, -4], [7.6, 0.1, 42], 0.03);
  path.receiveShadow = true;
  const seams = [],
    lineMat = new THREE.LineBasicMaterial({ color: '#97988b', transparent: true, opacity: 0.25 });
  for (let z = -22; z < 17; z += 1.4) seams.push(-3.7, 0.017, z, 3.7, 0.017, z);
  for (const x of [-2.2, -0.7, 0.8, 2.3]) seams.push(x, 0.017, -22, x, 0.017, 17);
  const lines = new THREE.LineSegments(
    new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(seams, 3)),
    lineMat,
  );
  group.add(lines);
  for (const side of [-1, 1])
    for (let z = -15; z <= 1; z += 5) {
      const x = side * (z >= 0 || ['cafe', 'window'].includes(config.mode) ? 6.1 : 4.5);
      tree(group, mats, [x, 0, z], Math.round(z + x * 20 + 140), 1.1);
    }
  const water = mesh(new THREE.PlaneGeometry(14, 60, 20, 40), mats.water, group, [-12, -0.14, -8]);
  water.rotation.x = -Math.PI / 2;
  props.water = water;
  box(group, mats.moss, [-4.8, -0.01, -8], [1.3, 0.13, 40], 0.03);
  const rng = random(41),
    grass = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.035, 0.26), mats.leaf, 1000),
    dummy = new THREE.Object3D();
  for (let i = 0; i < 1000; i++) {
    const side = i % 2 ? -1 : 1;
    dummy.position.set(side * (3.9 + rng() * 1.2), 0.1, -19 + rng() * 30);
    dummy.rotation.set(-0.1 + rng() * 0.2, rng() * Math.PI, 0.2 - rng() * 0.4);
    dummy.scale.setScalar(0.6 + rng() * 0.9);
    dummy.updateMatrix();
    grass.setMatrixAt(i, dummy.matrix);
  }
  group.add(grass);
  if (['cafe', 'window'].includes(config.mode)) {
    for (let i = 0; i < 2; i++) {
      const x = i === 0 ? -1.8 : 1.8;
      box(group, i ? mats.plaster : mats.moss, [x, 2.55, -3.5], [3.5, 5.1, 1.1], 0.04);
      box(group, mats.walnut, [x, 1.4, -2.89], [2.95, 2.7, 0.08], 0.03);
      box(group, mats.ceramic, [x, 1.4, -2.82], [2.73, 2.49, 0.06], 0.025);
      mesh(new THREE.PlaneGeometry(2.69, 2.45), mats.glass, group, [x, 1.4, -2.77]);
      for (const off of [-1.43, 1.43])
        box(group, mats.brass, [x + off, 1.4, -2.72], [0.035, 2.7, 0.045], 0.01);
      const awning = box(
        group,
        i ? mats.blanket : mats.moss,
        [x, 3.0, -2.15],
        [3.32, 0.1, 1.6],
        0.025,
      );
      awning.rotation.x = -0.13;
      label(group, i ? 'HOUR STUDIO' : 'OAK & OAT', [x, 3.67, -2.92], 2.8, 0.5, {
        background: i ? '#d4ccbc' : '#354b3e',
        color: i ? '#423b33' : '#f1e5c9',
      });
      plant(group, mats, [x + (i ? 1.25 : -1.25), 0, -2], 0.75, 20 + i);
      if (!i) {
        mesh(
          new THREE.CylinderGeometry(0.46, 0.46, 0.05, 40),
          mats.walnut,
          group,
          [-2.8, 0.75, -0.5],
        );
        mesh(
          new THREE.CylinderGeometry(0.035, 0.07, 0.75, 16),
          mats.brass,
          group,
          [-2.8, 0.38, -0.5],
        );
        mesh(
          new THREE.CylinderGeometry(0.09, 0.065, 0.16, 24),
          mats.ceramic,
          group,
          [-2.8, 0.86, -0.5],
        );
      }
    }
  }
  if (config.mode === 'bridge' || config.mode === 'walk') {
    for (let z = -12; z < 12; z += 2.4)
      box(group, mats.walnut, [-3.45, 0.6, z], [0.065, 1.2, 0.065], 0.02);
    for (const y of [0.39, 0.98])
      tube(
        group,
        mats.brass,
        [
          [-3.45, y, -14],
          [-3.45, y, 0],
          [-3.45, y, 14],
        ],
        0.025,
      );
    if (config.dusk)
      for (let z = -10; z < 10; z += 3) {
        ellipsoid(group, mats.glow, [-3.4, 1.14, z], [0.07, 0.11, 0.07]);
        const l = new THREE.PointLight('#ffd59b', 1.7, 3);
        l.position.set(-3.4, 1.2, z);
        group.add(l);
      }
  }
}

function prop(parent, mats, id) {
  const group = new THREE.Group();
  group.name = id;
  parent.add(group);
  const add = (g, m, p) => mesh(g, m, group, p);
  switch (id) {
    case 'brush':
      box(group, mats.walnut, [0, 0.04, 0], [0.21, 0.09, 0.5], 0.045);
      box(group, mats.walnut, [0, 0.03, 0.39], [0.07, 0.07, 0.38], 0.03);
      for (let x = -0.065; x <= 0.08; x += 0.032)
        for (let z = -0.17; z <= 0.18; z += 0.045)
          add(new THREE.CylinderGeometry(0.004, 0.004, 0.045, 4), mats.brass, [x, 0.1, z]);
      break;
    case 'dryer':
      {
        const barrel = add(
          new THREE.CylinderGeometry(0.13, 0.11, 0.4, 24),
          mats.black,
          [0, 0.2, 0],
        );
        barrel.rotation.z = Math.PI / 2;
        box(group, mats.black, [0.1, 0.1, 0], [0.1, 0.27, 0.13], 0.04);
        const nose = add(new THREE.TorusGeometry(0.086, 0.015, 8, 24), mats.brass, [-0.21, 0.2, 0]);
        nose.rotation.y = Math.PI / 2;
      }
      break;
    case 'towel':
      box(group, mats.linen, [0, 0.06, 0], [0.66, 0.12, 0.38], 0.05);
      label(group, 'TOWEL', [0, 0.1, 0.195], 0.49, 0.09, {
        background: '#cfc4a2',
        color: '#66523d',
        fontSize: 58,
      });
      break;
    case 'blanket':
      box(group, mats.blanket, [0, 0.07, 0], [0.7, 0.14, 0.52], 0.06);
      label(group, 'BLANKET', [0, 0.1, 0.267], 0.56, 0.1, { background: '#98604f', fontSize: 54 });
      break;
    case 'vinyl':
      box(group, mats.walnut, [0, 0.06, 0], [0.94, 0.13, 0.68], 0.04);
      add(new THREE.CylinderGeometry(0.29, 0.29, 0.019, 64), mats.black, [0, 0.142, 0]);
      for (let r = 0.08; r < 0.28; r += 0.012) {
        const ring = add(new THREE.TorusGeometry(r, 0.0015, 3, 64), mats.brass, [0, 0.153, 0]);
        ring.rotation.x = Math.PI / 2;
      }
      add(new THREE.CylinderGeometry(0.065, 0.065, 0.021, 28), mats.blanket, [0, 0.15, 0]);
      tube(
        group,
        mats.brass,
        [
          [0.38, 0.19, -0.21],
          [0.33, 0.21, 0.04],
          [0.21, 0.2, 0.13],
        ],
        0.012,
      );
      break;
    case 'ball':
      ellipsoid(group, mats.green, [0, 0.15, 0], [0.15, 0.15, 0.15]);
      {
        const ring = add(new THREE.TorusGeometry(0.147, 0.006, 5, 40), mats.white, [0, 0.15, 0]);
        ring.rotation.z = 0.7;
      }
      break;
    case 'speaker':
      box(group, mats.walnut, [0, 0.29, 0], [0.4, 0.58, 0.27], 0.03);
      for (const y of [0.17, 0.42]) {
        const cone = add(new THREE.CylinderGeometry(0.105, 0.105, 0.02, 28), mats.black, [
          0,
          y,
          0.145,
        ]);
        cone.rotation.x = Math.PI / 2;
      }
      break;
    case 'apple':
      ellipsoid(group, mats.red, [0, 0.17, 0], [0.2, 0.17, 0.18]);
      tube(
        group,
        mats.walnut,
        [
          [0, 0.28, 0],
          [0.02, 0.37, 0],
        ],
        0.013,
        6,
      );
      ellipsoid(group, mats.leaf, [0.08, 0.34, 0], [0.1, 0.022, 0.043]);
      break;
    case 'grapes':
      for (let i = 0; i < 11; i++)
        ellipsoid(
          group,
          mats.moss,
          [Math.sin(i * 3) * 0.12, 0.09 + Math.floor(i / 4) * 0.1, Math.cos(i * 3) * 0.11],
          [0.066, 0.075, 0.066],
          16,
        );
      label(group, 'GRAPES', [0, 0.37, 0.12], 0.53, 0.12, { background: '#34483a', fontSize: 58 });
      break;
    case 'bowl':
      {
        const b = add(
          new THREE.CylinderGeometry(0.3, 0.23, 0.2, 40, 1, true),
          mats.ceramic,
          [0, 0.1, 0],
        );
        b.material.side = THREE.DoubleSide;
        add(new THREE.CylinderGeometry(0.235, 0.235, 0.018, 36), mats.water, [0, 0.046, 0]);
        label(group, 'BRUCE', [0, 0.1, 0.28], 0.33, 0.095, {
          background: '#e5ddc9',
          color: '#40382b',
          fontSize: 58,
        });
      }
      break;
    case 'cushion':
      box(group, mats.blanket, [0, 0.13, 0], [1, 0.25, 0.75], 0.11);
      break;
    case 'curtain':
      add(new THREE.TorusGeometry(0.13, 0.023, 8, 32), mats.brass, [0, 0.2, 0]);
      tube(
        group,
        mats.linen,
        [
          [0, 0.33, 0],
          [0, 1.7, 0],
        ],
        0.012,
      );
      break;
    case 'vacuum':
      ellipsoid(group, mats.black, [0, 0.22, 0], [0.32, 0.22, 0.38]);
      tube(
        group,
        mats.black,
        [
          [0, 0.28, 0.22],
          [0.1, 0.65, 0.6],
          [0.25, 0.2, 0.9],
        ],
        0.045,
      );
      break;
    case 'welcome':
    case 'noDogs':
      label(group, id === 'welcome' ? 'PAWS WELCOME' : 'NO DOGS', [0, 0, 0], 2.05, 0.48, {
        background: id === 'welcome' ? '#2c5945' : '#734337',
        fontSize: id === 'welcome' ? 68 : 90,
      });
      label(
        group,
        id === 'welcome' ? 'WATER & BISCUITS INSIDE' : 'THANK YOU FOR UNDERSTANDING',
        [0, -0.34, 0],
        2.05,
        0.18,
        { background: '#ddd9c9', color: '#47483c', fontSize: 42 },
      );
      break;
    case 'leash':
      add(new THREE.TorusGeometry(0.135, 0.024, 10, 36), mats.brass, [0, 0, 0]);
      add(
        new THREE.SphereGeometry(0.21, 12, 8),
        new THREE.MeshBasicMaterial({
          transparent: true,
          opacity: 0,
          depthWrite: false,
          colorWrite: false,
        }),
        [0, 0, 0],
      );
      break;
    case 'shrub':
      for (let i = 0; i < 7; i++) {
        const leaf = ellipsoid(
          group,
          mats.leaf,
          [Math.sin(i * 2) * 0.29, 0.19 + Math.cos(i) * 0.1, Math.cos(i * 2) * 0.2],
          [0.22, 0.26, 0.16],
          16,
        );
        leaf.rotation.z = i;
      }
      break;
    case 'scooter':
      box(group, mats.moss, [0, 0.18, 0], [0.28, 0.13, 0.95], 0.06);
      for (const z of [-0.37, 0.37]) {
        const wheel = add(new THREE.TorusGeometry(0.16, 0.037, 10, 24), mats.black, [0, 0.16, z]);
        wheel.rotation.y = Math.PI / 2;
      }
      tube(
        group,
        mats.brass,
        [
          [0, 0.18, 0.3],
          [0, 0.9, 0.2],
          [0, 1.1, 0.18],
        ],
        0.025,
      );
      tube(
        group,
        mats.black,
        [
          [-0.25, 1.1, 0.18],
          [0.25, 1.1, 0.18],
        ],
        0.035,
      );
      break;
    case 'friend':
    case 'angry':
      ellipsoid(
        group,
        id === 'friend' ? mats.paleFur : mats.earFur,
        [0, 0.36, 0],
        [0.25, 0.29, 0.48],
      );
      ellipsoid(group, mats.fur, [0, 0.67, 0.34], [0.22, 0.22, 0.2]);
      ellipsoid(group, mats.nose, [0, 0.66, 0.53], [0.05, 0.04, 0.04]);
      for (const side of [-1, 1]) {
        ellipsoid(group, mats.eye, [side * 0.09, 0.73, 0.49], [0.026, 0.03, 0.018]);
        ellipsoid(group, mats.earFur, [side * 0.18, 0.83, 0.3], [0.07, 0.16, 0.08]);
      }
      tube(
        group,
        mats.fur,
        [
          [0, 0.45, -0.42],
          [0.1, 0.63, -0.58],
          [0.12, 0.72, -0.54],
        ],
        0.045,
      );
      label(
        group,
        id === 'friend' ? 'WAGGING' : 'GIVE ME SPACE',
        [0, 1.15, 0.15],
        id === 'friend' ? 1 : 1.55,
        0.23,
        { background: id === 'friend' ? '#355c42' : '#734337', fontSize: 54 },
      );
      break;
    case 'biscuit':
      ellipsoid(group, mats.earFur, [0, 0.07, 0], [0.19, 0.055, 0.12]);
      for (const x of [-0.15, 0.15])
        for (const z of [-0.08, 0.08])
          ellipsoid(group, mats.earFur, [x, 0.07, z], [0.09, 0.055, 0.08], 16);
      break;
    default:
      if (id.startsWith('lantern')) {
        add(new THREE.CylinderGeometry(0.16, 0.2, 0.27, 24), mats.brass, [0, 0.16, 0]);
        ellipsoid(group, mats.glow, [0, 0.36, 0], [0.12, 0.18, 0.12]);
      }
  }
  return group;
}

const POSITIONS = {
  brush: [-1.15, 0.09, 1.25],
  dryer: [1.45, 0.06, -0.05],
  towel: [-1.1, 0.08, 1.2],
  blanket: [0.88, 0.08, 1.48],
  vinyl: [1.9, 0.98, -0.65],
  ball: [0.85, 0.06, 1.36],
  speaker: [-1.9, 0.04, -0.35],
  apple: [-0.65, 0.15, 1.3],
  grapes: [1.35, 0.1, -0.5],
  bowl: [0.9, 0.04, 1.35],
  curtain: [-1.1, 0.16, -0.65],
  cushion: [0.9, 0.06, 1.3],
  vacuum: [1.85, 0.04, -0.65],
  welcome: [-1.8, 1.67, -2.65],
  noDogs: [1.8, 1.67, -2.65],
  leash: [1.55, 1, 1.65],
  shrub: [-1.4, 0.02, 1],
  scooter: [2.7, 0.02, -0.8],
  friend: [-1.4, 0, -0.15],
  angry: [1.6, 0, -0.5],
  biscuit: [-1, 0.08, 1.4],
  lantern0: [-1.5, 0.03, 1.15],
  lantern1: [1, 0.03, 0.8],
  lantern2: [-1.3, 0.03, -1.6],
};

export function createWorld(scene, mats, config) {
  const group = new THREE.Group();
  scene.add(group);
  const props = {},
    targets = new Map();
  if (config.environment === 'home') createInterior(group, mats, config, targets, props);
  else createStreet(group, mats, config, props);
  for (const id of config.props) {
    const object = prop(group, mats, id);
    object.position.fromArray(POSITIONS[id] || [0, 0, 0]);
    object.userData.action = id;
    object.userData.base = object.position.clone();
    targets.set(id, object);
    props[id] = object;
    if (config.mode === 'cafe' && ['bowl', 'biscuit'].includes(id)) {
      object.visible = false;
      object.position.set(-1.2 + (id === 'bowl' ? 0.3 : -0.2), 0.05, -0.2);
    }
  }
  if (props.vinyl && props.vinylTable) {
    group.updateMatrixWorld(true);
    props.vinyl.attach(props.vinylTable);
  }
  if (props.blanket) {
    const drape = new THREE.Group();
    group.add(drape);
    drape.visible = false;
    const cloth = new THREE.PlaneGeometry(1.04, 1.25, 24, 30);
    cloth.rotateX(-Math.PI / 2);
    const vertices = cloth.attributes.position;
    for (let i = 0; i < vertices.count; i++) {
      const x = vertices.getX(i),
        z = vertices.getZ(i) - 0.16;
      vertices.setXYZ(
        i,
        x,
        0.62 - 0.3 * Math.pow(Math.abs(x) / 0.52, 1.7) + Math.sin(z * 22 + x * 7) * 0.009,
        z,
      );
    }
    cloth.computeVertexNormals();
    const fabric = mats.blanket.clone();
    fabric.side = THREE.DoubleSide;
    fabric.transparent = true;
    fabric.opacity = 0;
    mesh(cloth, fabric, drape);
    const stitching = mats.linen.clone();
    stitching.transparent = true;
    stitching.opacity = 0;
    for (const z of [-0.76, 0.44]) {
      const points = Array.from({ length: 15 }, (_, i) => {
        const x = -0.5 + i / 14;
        return [x, 0.63 - 0.3 * Math.pow(Math.abs(x) / 0.52, 1.7), z];
      });
      tube(drape, stitching, points, 0.004, 28);
    }
    props.drapedBlanket = drape;
  }
  const ringMat = new THREE.MeshBasicMaterial({
    color: '#ffe5ac',
    transparent: true,
    opacity: 0.65,
    depthWrite: false,
    side: THREE.DoubleSide,
  });
  const indicator = mesh(new THREE.RingGeometry(0.22, 0.245, 60), ringMat, group, [0, 0.065, 0]);
  indicator.rotation.x = -Math.PI / 2;
  indicator.visible = false;
  let leash;
  if (config.environment === 'street') {
    const leather = new THREE.MeshStandardMaterial({ color: '#703e34', roughness: 0.65 });
    leash = createLeash(group, leather);
    if (!props.leash) {
      props.leash = prop(group, mats, 'leash');
      props.leash.position.fromArray(POSITIONS.leash);
      props.leash.visible = !['cafe', 'window'].includes(config.mode);
    }
  }
  return {
    group,
    props,
    targets,
    indicator,
    leash,
    highlight(id) {
      const target = targets.get(id);
      indicator.visible = !!target;
      if (target) {
        indicator.position.set(target.position.x, 0.075, target.position.z);
        indicator.rotation.x = -Math.PI / 2;
        if (['welcome', 'noDogs'].includes(id)) {
          indicator.position.copy(target.position);
          indicator.position.z += 0.02;
          indicator.rotation.x = 0;
          indicator.scale.set(3.9, 1.1, 1);
        } else indicator.scale.setScalar(1);
      }
    },
    update(
      time,
      dt,
      bruce,
      { record = 0, blanket = 0, curtain = 0, cold = 0, leashOffset = 0 } = {},
    ) {
      indicator.material.opacity = 0.4 + Math.sin(time * 3.2) * 0.16;
      if (props.vinyl) props.vinyl.children[1].rotation.y += dt * record * 2.5;
      if (props.blanket && blanket > 0) {
        const t = clamp(blanket, 0, 1);
        props.blanket.position
          .copy(props.blanket.userData.base)
          .lerp(new THREE.Vector3(0.06, 0.7, -0.14), t);
        props.blanket.rotation.z = -Math.sin(t * Math.PI) * 0.2;
        props.blanket.visible = t < 0.85;
        props.drapedBlanket.visible = t > 0.65;
        props.drapedBlanket.position.copy(bruce.root.position);
        props.drapedBlanket.position.y -= cold * 0.22;
        props.drapedBlanket.scale.z = 0.65 + t * 0.35;
        props.drapedBlanket.traverse((o) => {
          if (o.material) o.material.opacity = clamp((t - 0.65) / 0.25, 0, 1);
        });
      }
      if (props.curtainCloth) props.curtainCloth.scale.x = 1 + curtain * 4;
      if (props.lamp) props.lamp.intensity = (config.rain ? 13 : 4) + record * 6;
      if (props.friend) props.friend.rotation.y = 0.2 + Math.sin(time * 2.6) * 0.12;
      if (props.leash && leash) {
        props.leash.position.x = 1.55 + clamp(leashOffset, -1.4, 0.8);
        const start = bruce.getCollarPosition();
        leash.update(dt, start, props.leash.position);
      }
      if (props.water) {
        const p = props.water.geometry.attributes.position;
        for (let i = 0; i < p.count; i++)
          p.setZ(
            i,
            Math.sin(p.getX(i) * 3 + time) * 0.024 + Math.sin(p.getY(i) * 2.4 + time * 0.8) * 0.018,
          );
        p.needsUpdate = true;
        props.water.geometry.computeVertexNormals();
      }
    },
  };
}
