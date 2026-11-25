import * as THREE from 'three';

export const clamp = THREE.MathUtils.clamp;
export const lerp = THREE.MathUtils.lerp;
export const smooth = (t) => {
  t = clamp(t, 0, 1);
  return t * t * (3 - 2 * t);
};
export const ease = (t) => {
  t = clamp(t, 0, 1);
  return t < 0.5 ? 4 * t ** 3 : 1 - (-2 * t + 2) ** 3 / 2;
};
export const damp = (a, b, speed, dt) => lerp(a, b, 1 - Math.exp(-speed * dt));
export const vec = (a) => new THREE.Vector3(...a);
export function random(seed = 37) {
  return () => {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let n = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    n ^= n + Math.imul(n ^ (n >>> 7), 61 | n);
    return ((n ^ (n >>> 14)) >>> 0) / 4294967296;
  };
}

/** One disposal pass per mount, including shared resources and ImageBitmaps. */
export function disposeTree(root) {
  const geometries = new Set(),
    materials = new Set(),
    textures = new Set(),
    skeletons = new Set();
  root.traverse((object) => {
    if (object.geometry) geometries.add(object.geometry);
    if (object.material)
      (Array.isArray(object.material) ? object.material : [object.material]).forEach((m) =>
        materials.add(m),
      );
    if (object.skeleton) skeletons.add(object.skeleton);
    // r187 Object3D/InstancedMesh disposal also frees instance attributes.
    object.dispose?.();
  });
  for (const material of materials) {
    for (const value of Object.values(material)) if (value?.isTexture) textures.add(value);
    for (const uniform of Object.values(material.uniforms || {}))
      if (uniform.value?.isTexture) textures.add(uniform.value);
    material.dispose();
  }
  for (const geometry of geometries) geometry.dispose();
  for (const skeleton of skeletons) skeleton.dispose();
  for (const texture of textures) {
    texture.source?.data?.close?.();
    texture.dispose();
  }
  root.clear();
}

export function mesh(geometry, material, parent, position = [0, 0, 0]) {
  const object = new THREE.Mesh(geometry, material);
  object.position.fromArray(position);
  object.castShadow = object.receiveShadow = true;
  parent?.add(object);
  return object;
}

export function ellipsoid(parent, material, position, scale, segments = 28) {
  const object = mesh(new THREE.SphereGeometry(1, segments, 20), material, parent, position);
  object.scale.fromArray(scale);
  return object;
}

/** Rounded furniture edges, made without an additional loader or CDN. */
export function roundedBox(width, height, depth, radius = 0.1) {
  radius = Math.min(radius, width / 2 - 0.001, height / 2 - 0.001, depth / 2 - 0.001);
  const s = new THREE.Shape(),
    x = -width / 2,
    y = -height / 2,
    r = radius;
  s.moveTo(x + r, y);
  s.lineTo(x + width - r, y);
  s.quadraticCurveTo(x + width, y, x + width, y + r);
  s.lineTo(x + width, y + height - r);
  s.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
  s.lineTo(x + r, y + height);
  s.quadraticCurveTo(x, y + height, x, y + height - r);
  s.lineTo(x, y + r);
  s.quadraticCurveTo(x, y, x + r, y);
  const g = new THREE.ExtrudeGeometry(s, {
    depth: depth - 2 * r,
    bevelEnabled: true,
    bevelSegments: 3,
    steps: 1,
    bevelSize: r,
    bevelThickness: r,
    curveSegments: 5,
  });
  g.translate(0, 0, -depth / 2 + r);
  g.computeVertexNormals();
  return g;
}

export function tube(parent, material, points, radius = 0.025, segments = 30) {
  return mesh(
    new THREE.TubeGeometry(
      new THREE.CatmullRomCurve3(points.map((p) => (Array.isArray(p) ? vec(p) : p))),
      segments,
      radius,
      7,
      false,
    ),
    material,
    parent,
  );
}
