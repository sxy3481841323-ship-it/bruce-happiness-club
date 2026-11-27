/**
 * js/hub3d/duplexCamMath.js
 *
 * Pure, dependency-free camera math for the double-height penthouse duplex.
 * Handles floor presets (1F Salon <-> 2F Sunlit Mezzanine Loft) and smooth
 * quintic-eased "elevator" transitions with a parabolic atrium clearance arc
 * that keeps the camera clear of the 2F glass balustrade edge.
 *
 * No imports. ES module only.
 */

/* ------------------------------------------------------------------ *
 * Constants
 * ------------------------------------------------------------------ */

/** Vertical gap (world units) above which a transition is a floor change. */
const FLOOR_CROSS_THRESHOLD = 4.0;

/** Lateral push toward the open double-height atrium (X > 0). */
const ATRIUM_PUSH_X = 1.6;

/** Gentle vertical lift that clears the mezzanine slab / glass edge. */
const ATRIUM_LIFT_Y = 0.85;

/* ------------------------------------------------------------------ *
 * Floor presets
 * ------------------------------------------------------------------ */

/**
 * @typedef {Object} FloorPreset
 * @property {'1f'|'2f'} id
 * @property {string} label
 * @property {[number, number, number]} camPos
 * @property {[number, number, number]} target
 * @property {number} floorY
 * @property {[number, number, number]} brucePos
 * @property {number} bruceRot
 * @property {{ minX: number, maxX: number, minZ: number, maxZ: number }} walkBounds
 * @property {Array<[number, number]>} walkSpots
 */

/**
 * @type {{ '1f': FloorPreset, '2f': FloorPreset }}
 */
export const FLOOR_PRESETS = {
  '1f': {
    id: '1f',
    label: '1F · 挑空客厅',
    camPos: [-3.2, 5.4, 14.2],
    target: [3.4, 3.0, -2.6],
    floorY: 0.04,
    brucePos: [1.2, 0.04, 2.6],
    bruceRot: -0.24,
    walkBounds: { minX: -2.2, maxX: 6.2, minZ: 1.4, maxZ: 6.4 },
    walkSpots: [
      [1.2, 2.6],
      [3.4, 4.0],
      [-0.8, 3.2],
      [4.8, 2.2]
    ]
  },
  '2f': {
    id: '2f',
    label: '2F · 阳光阁楼',
    camPos: [-0.2, 13.0, 6.8],
    target: [-8.6, 10.8, -3.6],
    floorY: 9.24,
    brucePos: [-8.0, 9.24, -4.2],
    bruceRot: 0.82,
    walkBounds: { minX: -10.8, maxX: -5.0, minZ: -8.5, maxZ: 1.1 },
    walkSpots: [
      [-8.0, -4.2],
      [-9.4, -7.2],
      [-6.2, -1.8],
      [-9.8, 0.2]
    ]
  }
};

/* ------------------------------------------------------------------ *
 * Internal helpers
 * ------------------------------------------------------------------ */

/**
 * Clamp a value into [min, max]; non-finite values fall back to `fallback`.
 * @param {number} value
 * @param {number} min
 * @param {number} max
 * @param {number} fallback
 * @returns {number}
 */
function clampSafe(value, min, max, fallback) {
  const v = typeof value === 'number' && Number.isFinite(value) ? value : fallback;
  return v < min ? min : v > max ? max : v;
}

/**
 * Read a component defensively (missing vector / NaN -> 0).
 * @param {{x:number,y:number,z:number}|null|undefined} v
 * @param {'x'|'y'|'z'} axis
 * @returns {number}
 */
function comp(v, axis) {
  if (!v) return 0;
  const n = v[axis];
  return typeof n === 'number' && Number.isFinite(n) ? n : 0;
}

/**
 * Quintic (smoother-step) easing: zero 1st and 2nd derivatives at both ends.
 * s(t) = t^3 * (t * (t * 6 - 15) + 10)
 * @param {number} t clamped progress in [0, 1]
 * @returns {number} eased progress in [0, 1]
 */
function quinticEase(t) {
  return t * t * t * (t * (t * 6 - 15) + 10);
}

/**
 * @param {number} a
 * @param {number} b
 * @param {number} k
 * @returns {number}
 */
function lerp(a, b, k) {
  return a + (b - a) * k;
}

/* ------------------------------------------------------------------ *
 * Transition solver
 * ------------------------------------------------------------------ */

/**
 * Compute an eased, atrium-clearing camera pose for a duplex floor transition.
 *
 * @param {{x:number,y:number,z:number}} fromPos    camera position at t = 0
 * @param {{x:number,y:number,z:number}} toPos      camera position at t = 1
 * @param {{x:number,y:number,z:number}} fromTarget look target at t = 0
 * @param {{x:number,y:number,z:number}} toTarget   look target at t = 1
 * @param {number} rawProgress                      raw 0..1 progress (clamped)
 * @returns {{
 *   pos: {x:number,y:number,z:number},
 *   target: {x:number,y:number,z:number},
 *   eased: number
 * }}
 */
export function computeDuplexCameraPose(
  fromPos,
  toPos,
  fromTarget,
  toTarget,
  rawProgress
) {
  /* --- clamp progress ------------------------------------------------ */
  const t = clampSafe(rawProgress, 0, 1, 0);

  const fx = comp(fromPos, 'x');
  const fy = comp(fromPos, 'y');
  const fz = comp(fromPos, 'z');

  const tx = comp(toPos, 'x');
  const ty = comp(toPos, 'y');
  const tz = comp(toPos, 'z');

  const ftX = comp(fromTarget, 'x');
  const ftY = comp(fromTarget, 'y');
  const ftZ = comp(fromTarget, 'z');

  const ttX = comp(toTarget, 'x');
  const ttY = comp(toTarget, 'y');
  const ttZ = comp(toTarget, 'z');

  /* --- exact endpoint guarantees ------------------------------------- */
  if (t === 0) {
    return {
      pos: { x: fx, y: fy, z: fz },
      target: { x: ftX, y: ftY, z: ftZ },
      eased: 0
    };
  }
  if (t === 1) {
    return {
      pos: { x: tx, y: ty, z: tz },
      target: { x: ttX, y: ttY, z: ttZ },
      eased: 1
    };
  }

  /* --- quintic easing ------------------------------------------------ */
  const s = quinticEase(t);

  /* --- base interpolation -------------------------------------------- */
  let px = lerp(fx, tx, s);
  let py = lerp(fy, ty, s);
  let pz = lerp(fz, tz, s);

  const gx = lerp(ftX, ttX, s);
  const gy = lerp(ftY, ttY, s);
  const gz = lerp(ftZ, ttZ, s);

  /* --- atrium clearance arc (only across floors) --------------------- */
  if (Math.abs(ty - fy) > FLOOR_CROSS_THRESHOLD) {
    // Bell-shaped: 0 at both ends, 1 at mid-transition.
    const arc = Math.sin(Math.PI * s);
    // Slide out over the open double-height atrium (X > 0) and lift slightly
    // so the camera sweeps around the 2F glass balustrade edge
    // (X = -3.42, Z = 6.62) instead of clipping through the mezzanine slab.
    px += ATRIUM_PUSH_X * arc;
    py += ATRIUM_LIFT_Y * arc;
  }

  return {
    pos: { x: px, y: py, z: pz },
    target: { x: gx, y: gy, z: gz },
    eased: s
  };
}
