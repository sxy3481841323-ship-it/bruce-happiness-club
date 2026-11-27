import * as THREE from "three";

export const YACHT_CAM_PRESETS = {
  dock_landing: {
    id: "dock_landing",
    label: "浮桥落点",
    camPos: [-4.20, 2.18, -13.10],
    lookAt: [-1.45, 1.65, -2.50],
    fov: 45,
    narrowScale: 1.12,
  },
  overview: {
    id: "overview",
    label: "右舷主总览",
    camPos: [16.8, 8.2, -23.5],
    lookAt: [-0.65, 6.35, 0.60],
    fov: 43,
    narrowScale: 1.24,
  },
  aft_door: {
    id: "aft_door",
    label: "后沙龙敞门",
    camPos: [-1.50, 2.72, -7.65],
    lookAt: [0.25, 1.94, -3.00],
    fov: 47,
    narrowScale: 1.16,
  },
  cabin_bar: {
    id: "cabin_bar",
    label: "舱内吧台",
    camPos: [0.0, 2.55, -3.60],
    lookAt: [0.0, 2.35, 1.05],
    fov: 41,
    narrowScale: 1.12,
  },
  bow_bruce: {
    id: "bow_bruce",
    label: "船首布鲁斯",
    camPos: [1.07, 2.22, 5.85],
    lookAt: [0.08, 1.98, 7.80],
    fov: 43,
    narrowScale: 1.14,
  },
};

export const YACHT_DRONE_TRACKS = {
  port: {
    id: "yacht_drone_port",
    label: "左舷俯掠",
    duration: 3.2,
    fov: 36,
    camPoints: [
      [-8.5, 11.8, -7.0],
      [-8.9, 11.2, -1.0],
      [-7.9, 10.8, 5.3],
    ],
    lookPoints: [
      [-1.8, 1.0, -5.4],
      [-2.1, 1.1, -0.6],
      [-1.4, 1.4, 4.7],
    ],
  },
  starboard: {
    id: "yacht_drone_starboard",
    label: "右舷俯推",
    duration: 3.4,
    fov: 40,
    camPoints: [
      [10.6, 13.0, -11.0],
      [8.3, 10.2, -9.8],
      [1.75, 4.15, -9.40],
    ],
    lookPoints: [
      [1.0, 1.45, -5.6],
      [0.55, 1.65, -4.3],
      [0.0, 2.36, 1.22],
    ],
  },
};

export const DOCK_SPAWN_POS = new THREE.Vector3(-4.20, 0.72, -10.60);
export const DOCK_SPAWN_YAW = 0.0; // Facing +Z along berth toward yacht gangway

export function quinticEase(t) {
  const u = Math.max(0, Math.min(1, t));
  return u * u * u * (u * (u * 6 - 15) + 10);
}

/**
 * Pulls camera backward along view ray on narrow screens (aspect < 16/9)
 * so masthead (Y=18), stern swim steps, and doorway remain legible.
 */
export function adaptPoseForAspect(camPosArr, lookAtArr, fovDeg, aspect, narrowScale = 1.18) {
  const pos = new THREE.Vector3(...camPosArr);
  const tgt = new THREE.Vector3(...lookAtArr);
  const safeAspect = Math.max(0.45, aspect || 16 / 9);
  if (safeAspect >= 1.55) {
    return { pos, target: tgt, fov: fovDeg };
  }
  const t = Math.max(0, Math.min(1, (1.55 - safeAspect) / (1.55 - 0.68)));
  const pull = 1 + t * (narrowScale - 1);
  const ray = pos.clone().sub(tgt).multiplyScalar(pull);
  return {
    pos: tgt.clone().add(ray),
    target: tgt,
    fov: fovDeg,
  };
}

/**
 * Builds an arc-length-parameterized Catmull-Rom sampler for smooth drone flyovers
 * with uniform spatial speed and level +Y horizon.
 */
export function buildArcLengthTrack(camPoints, lookPoints, durationSec, fovDeg) {
  const camVecs = camPoints.map((p) => new THREE.Vector3(...p));
  const lookVecs = lookPoints.map((p) => new THREE.Vector3(...p));
  const camCurve = new THREE.CatmullRomCurve3(camVecs, false, "centripetal", 0.5);
  const lookCurve = new THREE.CatmullRomCurve3(lookVecs, false, "centripetal", 0.5);

  // Precompute arc-length table for camCurve
  const N = 120;
  const arcLen = new Float32Array(N + 1);
  let prev = camCurve.getPoint(0);
  for (let i = 1; i <= N; i++) {
    const cur = camCurve.getPoint(i / N);
    arcLen[i] = arcLen[i - 1] + cur.distanceTo(prev);
    prev = cur;
  }
  const totalLen = Math.max(1e-5, arcLen[N]);

  function sampleU(sNorm) {
    const targetDist = Math.max(0, Math.min(1, sNorm)) * totalLen;
    let lo = 0;
    let hi = N;
    while (lo < hi - 1) {
      const mid = (lo + hi) >> 1;
      if (arcLen[mid] <= targetDist) lo = mid;
      else hi = mid;
    }
    const seg = Math.max(1e-6, arcLen[hi] - arcLen[lo]);
    const frac = (targetDist - arcLen[lo]) / seg;
    return (lo + frac) / N;
  }

  return {
    duration: durationSec,
    fov: fovDeg,
    sample(tNorm, aspect = 16 / 9) {
      const eased = quinticEase(tNorm);
      const u = sampleU(eased);
      const rawPos = camCurve.getPoint(u);
      const rawLook = lookCurve.getPoint(u);
      // Narrow portrait viewport keeps full hull/berth context by pulling slightly back along ray
      const pull = aspect < 1.35 ? 1 + (1.35 - Math.max(0.65, aspect)) * 0.28 : 1.0;
      const pos = pull > 1.001
        ? rawLook.clone().add(rawPos.clone().sub(rawLook).multiplyScalar(pull))
        : rawPos;
      return { pos, lookAt: rawLook, fov: fovDeg };
    },
  };
}

const CABIN_CHECK_MIN_Z = -3.18;
const CABIN_CHECK_MAX_Z = 2.18;

/**
 * Generates collision-free C2 camera path with r=0.12 m clearance sphere.
 * Exterior <-> Cabin transitions route cleanly through the aft deck & 1.60 m open doorway centerline.
 */
export function buildSafeTransitionSpline(fromPos, fromTarget, toPos, toTarget, fromFov, toFov, durationSec = 2.0) {
  const isCabin = (p) => p.z > CABIN_CHECK_MIN_Z && p.z < CABIN_CHECK_MAX_Z && Math.abs(p.x) < 1.52;
  const fromInCabin = isCabin(fromPos);
  const toInCabin = isCabin(toPos);

  const camPts = [fromPos.clone()];
  const tgtPts = [fromTarget.clone()];

  if (fromInCabin !== toInCabin) {
    // Route safely via aft centerline -> doorway centerline (X=0, Y=2.46, Z=-3.15) with 0.12 m wall clearance
    const exterior = fromInCabin ? toPos : fromPos;
    const preDeck = new THREE.Vector3(
      THREE.MathUtils.clamp(exterior.x * 0.18, -0.58, 0.58),
      2.52,
      -5.95,
    );
    const doorMid = new THREE.Vector3(0.0, 2.48, -3.15);
    const insideMid = new THREE.Vector3(0.0, 2.50, -2.55);

    if (fromInCabin) {
      camPts.push(insideMid, doorMid, preDeck);
      tgtPts.push(
        new THREE.Vector3(0.0, 2.15, -3.5),
        new THREE.Vector3(0.1, 1.95, -5.2),
        toTarget.clone().lerp(fromTarget, 0.35),
      );
      if (toPos.z > CABIN_CHECK_MAX_Z) {
        camPts.push(new THREE.Vector3(3.15, 2.75, -0.2));
        tgtPts.push(new THREE.Vector3(0.1, 2.1, 3.8));
      }
    } else {
      if (fromPos.z > CABIN_CHECK_MAX_Z) {
        camPts.push(new THREE.Vector3(3.15, 2.75, -0.2));
        tgtPts.push(new THREE.Vector3(0.1, 2.1, -1.8));
      }
      camPts.push(preDeck, doorMid, insideMid);
      tgtPts.push(
        new THREE.Vector3(0.0, 2.10, -2.8),
        new THREE.Vector3(0.0, 2.30, 0.2),
        toTarget.clone(),
      );
    }
  } else if (!fromInCabin && !toInCabin && ((fromPos.z < -2.5 && toPos.z > 2.5) || (fromPos.z > 2.5 && toPos.z < -2.5) || fromPos.distanceTo(toPos) > 10.0)) {
    // Exterior aft <-> bow orbit stays safely outside starboard cabin glass, boom, and folded SolidSail
    const midSide = (fromPos.x < -1.0 && toPos.x < -1.0) ? -3.4 : 3.2;
    camPts.push(new THREE.Vector3(midSide, Math.max(2.9, (fromPos.y + toPos.y) * 0.55), -0.4));
    tgtPts.push(fromTarget.clone().lerp(toTarget, 0.5));
  }

  camPts.push(toPos.clone());
  tgtPts.push(toTarget.clone());

  const posCurve = new THREE.CatmullRomCurve3(camPts, false, "centripetal", 0.5);
  const tgtCurve = new THREE.CatmullRomCurve3(tgtPts, false, "centripetal", 0.5);

  const qStart = new THREE.Quaternion().setFromRotationMatrix(
    new THREE.Matrix4().lookAt(fromPos, fromTarget, new THREE.Vector3(0, 1, 0)),
  );
  const qEnd = new THREE.Quaternion().setFromRotationMatrix(
    new THREE.Matrix4().lookAt(toPos, toTarget, new THREE.Vector3(0, 1, 0)),
  );

  return {
    duration: Math.max(1.8, Math.min(2.4, durationSec)),
    sample(tRaw) {
      const s = quinticEase(tRaw);
      const pos = posCurve.getPoint(s);
      // Only enforce cabin doorway/wall clearance when point actually lies inside cabin Z band!
      if (pos.z > CABIN_CHECK_MIN_Z - 0.15 && pos.z < CABIN_CHECK_MAX_Z + 0.15 && Math.abs(pos.x) < 1.55) {
        pos.x = THREE.MathUtils.clamp(pos.x, -0.68, 0.68);
        pos.y = THREE.MathUtils.clamp(pos.y, 1.52, 3.16);
      }
      const target = tgtCurve.getPoint(s);
      const quat = qStart.clone().slerp(qEnd, s);
      const fov = THREE.MathUtils.lerp(fromFov, toFov, s);
      return { pos, target, quat, fov };
    },
  };
}
