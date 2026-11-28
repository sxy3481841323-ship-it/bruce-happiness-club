/**
 * js/hub3d/bruceNavMesh.js
 *
 * 2D padded furniture obstacle boxes + visibility-graph Dijkstra path planner
 * so Bruce routes cleanly around sectional sofas, marble cocktail tables,
 * kitchen islands, dining chairs, pool basins, and room partitions with zero clipping.
 */

const OBSTACLES_1F = [
  // Monumental Pearl-Dove U-Sectional Sofa + Behind-Sofa Console (X[-7.0..4.6], Z[-7.2..3.6])
  { minX: -7.1, maxX: 5.0, minZ: -7.3, maxZ: -3.5 },   // North sofa wing
  { minX: -7.1, maxX: -2.4, minZ: -4.2, maxZ: 3.9 },   // West sofa spine + console
  { minX: -7.1, maxX: 2.3, minZ: 0.4, maxZ: 3.9 },     // South chaise wing
  // Square Verde-Alpi Cocktail Table + Concierge Accent TableB
  { minX: -1.4, maxX: 5.2, minZ: -4.2, maxZ: 1.2 },
  // Cognac Club Armchair
  { minX: 5.2, maxX: 7.8, minZ: -6.2, maxZ: -3.6 },
  // Fireplace / TV Partition Wall + Flanking Harman Towers + Back Sporting Boiserie (forces clean North/South portal detours!)
  { minX: 11.8, maxX: 17.2, minZ: -7.2, maxZ: 3.6 },
  // Relocated NW Arc Floor Lamp, West Collector Plinth, and West Amphora Urn
  { minX: -6.8, maxX: -5.4, minZ: -7.9, maxZ: -6.5 },
  { minX: -14.6, maxX: -12.9, minZ: -12.4, maxZ: -10.8 },
  { minX: -14.3, maxX: -13.0, minZ: 9.8, maxZ: 11.0 },
  // South Wall Portal Piers (Z = 15.4, keep opening X in [-12.8, +12.8] clear)
  { minX: -15.5, maxX: -12.9, minZ: 14.6, maxZ: 16.2 },
  { minX: 12.9, maxX: 15.5, minZ: 14.6, maxZ: 16.2 },
  // Kitchen Center Island + 3 Bar Stools (X[-3.4..7.8], Z[17.3..22.0])
  { minX: -4.1, maxX: 8.5, minZ: 16.9, maxZ: 22.8 },
  // Kitchen East Appliances (7.8-unit Fridge + Coffee Bar) & West Cabinets (Wolf + Wine Cellar)
  { minX: 11.6, maxX: 15.4, minZ: 15.6, maxZ: 35.4 },
  { minX: -15.4, maxX: -11.7, minZ: 15.6, maxZ: 35.4 },
  // Separate Formal Rectangular Dining Table + 8 Armchairs
  { minX: -7.4, maxX: 7.4, minZ: 27.8, maxZ: 34.2 },
  // South Courtyard Infinity Pool Basin, Loungers, and Outdoor BBQ Grill
  { minX: -11.5, maxX: 4.3, minZ: 40.9, maxZ: 53.5 },
  { minX: -14.6, maxX: -10.8, minZ: 43.2, maxZ: 49.4 },
  { minX: 4.2, maxX: 8.2, minZ: 45.4, maxZ: 51.4 },
  { minX: 7.8, maxX: 14.6, minZ: 36.8, maxZ: 42.8 },
  // East Expanded Wing: Grand Piano + Bench (Golf, Tennis & Equestrian are on partition X=[14.7..16.9])
  { minX: 26.8, maxX: 34.8, minZ: -13.4, maxZ: -6.2 },
];

const OBSTACLES_2F = [
  { minX: -10.2, maxX: -5.4, minZ: -8.6, maxZ: -5.8 }, // 2F sofa bed
];

function getObstacles(floorId) {
  return floorId === "2f" ? OBSTACLES_2F : OBSTACLES_1F;
}

function insideBox(x, z, b, eps = 0.0) {
  return x > b.minX + eps && x < b.maxX - eps && z > b.minZ + eps && z < b.maxZ - eps;
}

function segmentHitsBox(ax, az, bx, bz, box) {
  let t0 = 0;
  let t1 = 1;
  const dx = bx - ax;
  const dz = bz - az;
  const checks = [
    [-dx, ax - (box.minX + 0.02)],
    [dx, box.maxX - 0.02 - ax],
    [-dz, az - (box.minZ + 0.02)],
    [dz, box.maxZ - 0.02 - az],
  ];
  for (let i = 0; i < 4; i++) {
    const p = checks[i][0];
    const q = checks[i][1];
    if (Math.abs(p) < 1e-8) {
      if (q < 0) return false;
    } else {
      const r = q / p;
      if (p < 0) {
        if (r > t1) return false;
        if (r > t0) t0 = r;
      } else {
        if (r < t0) return false;
        if (r < t1) t1 = r;
      }
    }
  }
  return t0 <= t1;
}

function segmentClear(ax, az, bx, bz, obstacles) {
  for (let i = 0; i < obstacles.length; i++) {
    if (segmentHitsBox(ax, az, bx, bz, obstacles[i])) return false;
  }
  return true;
}

export function projectToWalkable(rawX, rawZ, floorId = "1f", bounds = null) {
  let x = bounds ? Math.max(bounds.minX, Math.min(bounds.maxX, rawX)) : rawX;
  let z = bounds ? Math.max(bounds.minZ, Math.min(bounds.maxZ, rawZ)) : rawZ;
  const obstacles = getObstacles(floorId);
  for (let pass = 0; pass < 3; pass++) {
    for (let i = 0; i < obstacles.length; i++) {
      const b = obstacles[i];
      if (!insideBox(x, z, b, -0.02)) continue;
      const dLeft = Math.abs(x - b.minX);
      const dRight = Math.abs(b.maxX - x);
      const dTop = Math.abs(z - b.minZ);
      const dBot = Math.abs(b.maxZ - z);
      const m = Math.min(dLeft, dRight, dTop, dBot);
      if (m === dLeft) x = b.minX - 0.08;
      else if (m === dRight) x = b.maxX + 0.08;
      else if (m === dTop) z = b.minZ - 0.08;
      else z = b.maxZ + 0.08;
    }
  }
  if (bounds) {
    x = Math.max(bounds.minX, Math.min(bounds.maxX, x));
    z = Math.max(bounds.minZ, Math.min(bounds.maxZ, z));
  }
  return [x, z];
}

export function clampOutOfObstacles(pos, floorId = "1f", bounds = null) {
  const [px, pz] = projectToWalkable(pos.x, pos.z, floorId, bounds);
  pos.x = px;
  pos.z = pz;
}

export function planSafeWalkPath(x0, z0, rawX1, rawZ1, floorId = "1f", bounds = null) {
  const obstacles = getObstacles(floorId);
  const [sx, sz] = projectToWalkable(x0, z0, floorId, bounds);
  const [tx, tz] = projectToWalkable(rawX1, rawZ1, floorId, bounds);
  if (segmentClear(sx, sz, tx, tz, obstacles)) return [[tx, tz]];

  const nodes = [[sx, sz], [tx, tz]];
  const cornerOff = 0.14;
  for (let i = 0; i < obstacles.length; i++) {
    const b = obstacles[i];
    const cs = [
      [b.minX - cornerOff, b.minZ - cornerOff],
      [b.maxX + cornerOff, b.minZ - cornerOff],
      [b.minX - cornerOff, b.maxZ + cornerOff],
      [b.maxX + cornerOff, b.maxZ + cornerOff],
    ];
    for (const [cx, cz] of cs) {
      if (bounds && (cx < bounds.minX || cx > bounds.maxX || cz < bounds.minZ || cz > bounds.maxZ)) continue;
      let blocked = false;
      for (let j = 0; j < obstacles.length; j++) {
        if (insideBox(cx, cz, obstacles[j], 0.01)) { blocked = true; break; }
      }
      if (!blocked) nodes.push([cx, cz]);
    }
  }

  const n = nodes.length;
  const dist = new Float64Array(n).fill(Infinity);
  const prev = new Int32Array(n).fill(-1);
  const vis = new Uint8Array(n);
  dist[0] = 0;

  for (let step = 0; step < n; step++) {
    let u = -1;
    let best = Infinity;
    for (let i = 0; i < n; i++) {
      if (!vis[i] && dist[i] < best) { best = dist[i]; u = i; }
    }
    if (u === -1 || u === 1) break;
    vis[u] = 1;
    const [ux, uz] = nodes[u];
    for (let v = 0; v < n; v++) {
      if (vis[v]) continue;
      const [vx, vz] = nodes[v];
      const w = Math.hypot(vx - ux, vz - uz);
      if (dist[u] + w < dist[v] && segmentClear(ux, uz, vx, vz, obstacles)) {
        dist[v] = dist[u] + w;
        prev[v] = u;
      }
    }
  }

  if (prev[1] === -1) return [[tx, tz]];
  const out = [];
  for (let cur = 1; cur !== 0 && cur !== -1; cur = prev[cur]) {
    out.push(nodes[cur]);
  }
  out.reverse();
  return out;
}
