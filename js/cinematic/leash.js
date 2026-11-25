import * as THREE from 'three';
import { mesh, vec } from './math.js';

/** Damped Verlet rope, fixed collar/hand endpoints and iterative length constraints. */
export function createLeash(parent, material) {
  const count = 25,
    sides = 6,
    positions = new Float32Array(count * sides * 3),
    indices = [];
  for (let i = 0; i < count - 1; i++)
    for (let j = 0; j < sides; j++) {
      const a = i * sides + j,
        b = i * sides + ((j + 1) % sides);
      indices.push(a, b, a + sides, b, b + sides, a + sides);
    }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setIndex(indices);
  const rope = mesh(geometry, material, parent);
  rope.frustumCulled = false;
  const points = Array.from({ length: count }, (_, i) => vec([i * 0.06, 0.8, i * 0.07]));
  const previous = points.map((p) => p.clone()),
    delta = new THREE.Vector3(),
    tangent = new THREE.Vector3(),
    side = new THREE.Vector3(),
    normal = new THREE.Vector3(),
    up = vec([0, 1, 0]);
  let initialized = false;
  return {
    mesh: rope,
    update(dt, start, end) {
      dt = Math.min(dt, 0.03);
      if (!initialized) {
        points.forEach((p, i) => {
          p.copy(start).lerp(end, i / (count - 1));
          previous[i].copy(p);
        });
        initialized = true;
      }
      for (let i = 1; i < count - 1; i++) {
        const p = points[i],
          oldX = p.x,
          oldY = p.y,
          oldZ = p.z;
        p.addScaledVector(delta.subVectors(p, previous[i]), 0.97);
        p.y = Math.max(0.07, p.y - 4 * dt * dt);
        previous[i].set(oldX, oldY, oldZ);
      }
      const length = Math.max(2.65, start.distanceTo(end) * 1.08) / (count - 1);
      for (let pass = 0; pass < 7; pass++) {
        points[0].copy(start);
        points[count - 1].copy(end);
        for (let i = 0; i < count - 1; i++) {
          delta.subVectors(points[i + 1], points[i]);
          const d = delta.length();
          delta.multiplyScalar((d - length) / Math.max(d, 0.0001));
          if (i > 0) points[i].addScaledVector(delta, i === count - 2 ? 1 : 0.5);
          if (i + 1 < count - 1) points[i + 1].addScaledVector(delta, i === 0 ? -1 : -0.5);
        }
      }
      points[0].copy(start);
      points[count - 1].copy(end);
      for (let i = 0; i < count; i++) {
        tangent
          .subVectors(points[Math.min(count - 1, i + 1)], points[Math.max(0, i - 1)])
          .normalize();
        side.crossVectors(tangent, Math.abs(tangent.y) > 0.95 ? vec([1, 0, 0]) : up).normalize();
        normal.crossVectors(tangent, side).normalize();
        for (let j = 0; j < sides; j++) {
          const a = (j / sides) * Math.PI * 2,
            index = (i * sides + j) * 3;
          positions[index] = points[i].x + (side.x * Math.cos(a) + normal.x * Math.sin(a)) * 0.018;
          positions[index + 1] =
            points[i].y + (side.y * Math.cos(a) + normal.y * Math.sin(a)) * 0.018;
          positions[index + 2] =
            points[i].z + (side.z * Math.cos(a) + normal.z * Math.sin(a)) * 0.018;
        }
      }
      geometry.attributes.position.needsUpdate = true;
      geometry.computeVertexNormals();
    },
  };
}
