import * as THREE from "three";

const AUSPICIOUS_NUMBERS = [8, 18, 28];

export function pickAuspiciousBonus() {
  const r = Math.random();
  if (r < 0.52) return 8;
  if (r < 0.85) return 18;
  return 28;
}

/**
 * Probabilistic 3D Shooting Star ("幸运时刻") for Sunset/Twilight Skies.
 */
export function createLuckyMeteorController(scene, opts = {}) {
  const meteorGroup = new THREE.Group();
  meteorGroup.visible = false;

  const headGeo = new THREE.SphereGeometry(0.42, 12, 10);
  const headMat = new THREE.MeshBasicMaterial({
    color: 0xfff4cf,
    transparent: true,
    opacity: 0,
    toneMapped: false,
  });
  const headMesh = new THREE.Mesh(headGeo, headMat);

  const tailGeo = new THREE.ConeGeometry(0.28, 16.5, 10, 1, true);
  // Orient cone along +Z then rotate toward velocity vector
  tailGeo.rotateX(Math.PI * 0.5);
  tailGeo.translate(0, 0, -8.25);
  const tailMat = new THREE.MeshBasicMaterial({
    color: 0xffd27a,
    transparent: true,
    opacity: 0,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    side: THREE.DoubleSide,
    toneMapped: false,
  });
  const tailMesh = new THREE.Mesh(tailGeo, tailMat);

  const sparkCount = 18;
  const sparkPos = new Float32Array(sparkCount * 3);
  const sparkGeo = new THREE.BufferGeometry();
  sparkGeo.setAttribute("position", new THREE.BufferAttribute(sparkPos, 3));
  const sparkMat = new THREE.PointsMaterial({
    color: 0xffe8a6,
    size: 0.72,
    transparent: true,
    opacity: 0,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    toneMapped: false,
  });
  const sparkPoints = new THREE.Points(sparkGeo, sparkMat);

  meteorGroup.add(headMesh, tailMesh, sparkPoints);
  scene.add(meteorGroup);

  let active = null;
  let lastTriggerAt = -Infinity;
  let lastRollAt = performance.now();
  let terraceEnteredAt = null;
  let seenNaturalOnce = false;
  let countTriggered = 0;

  function launchStreak(source = "natural", forcedBonus = null) {
    const startX = -38 + Math.random() * 24;
    const startY = 21 + Math.random() * 10;
    const startZ = opts.skyZ ?? -96;
    const endX = startX + 34 + Math.random() * 22;
    const endY = startY - (10 + Math.random() * 6);
    const endZ = startZ + (Math.random() - 0.5) * 14;

    const start = new THREE.Vector3(startX, startY, startZ);
    const end = new THREE.Vector3(endX, endY, endZ);
    const dir = end.clone().sub(start).normalize();

    meteorGroup.visible = true;
    headMesh.position.copy(start);
    tailMesh.position.copy(start);
    tailMesh.lookAt(start.clone().add(dir));

    for (let i = 0; i < sparkCount; i++) {
      const f = (i + 1) / sparkCount;
      const p = start.clone().lerp(end, -f * 0.08);
      sparkPos[i * 3] = p.x + (Math.random() - 0.5) * 0.5;
      sparkPos[i * 3 + 1] = p.y + (Math.random() - 0.5) * 0.5;
      sparkPos[i * 3 + 2] = p.z;
    }
    sparkGeo.attributes.position.needsUpdate = true;

    active = {
      start,
      end,
      dir,
      age: 0,
      duration: 2.05,
    };
    lastTriggerAt = performance.now();
    seenNaturalOnce = true;
    countTriggered += 1;

    const bonus = AUSPICIOUS_NUMBERS.includes(forcedBonus) ? forcedBonus : pickAuspiciousBonus();
    opts.onTrigger?.({ bonus, source, count: countTriggered });
    return { bonus, source, count: countTriggered };
  }

  return {
    triggerNow(forcedBonus = null) {
      return launchStreak("manual_or_qa", forcedBonus);
    },
    notifyZone(zoneId) {
      if (zoneId === "terrace" && terraceEnteredAt === null) {
        terraceEnteredAt = performance.now();
      } else if (zoneId !== "terrace") {
        terraceEnteredAt = null;
      }
    },
    update(dt) {
      const now = performance.now();

      if (active) {
        active.age += dt;
        const p = Math.min(1, active.age / active.duration);
        const eased = 1 - Math.pow(1 - p, 2);
        const pos = active.start.clone().lerp(active.end, eased);
        headMesh.position.copy(pos);
        tailMesh.position.copy(pos);
        tailMesh.lookAt(pos.clone().add(active.dir));

        const env = Math.sin(Math.PI * p);
        headMat.opacity = env;
        tailMat.opacity = env * 0.85;
        sparkMat.opacity = env * 0.92;
        tailMesh.scale.set(0.6 + env * 0.6, 0.6 + env * 0.6, 0.35 + env * 0.85);

        for (let i = 0; i < sparkCount; i++) {
          const back = ((i + 1) / sparkCount) * 14.5 * env;
          sparkPos[i * 3] = pos.x - active.dir.x * back + Math.sin(now * 0.01 + i) * 0.25;
          sparkPos[i * 3 + 1] = pos.y - active.dir.y * back + Math.cos(now * 0.012 + i) * 0.22;
          sparkPos[i * 3 + 2] = pos.z - active.dir.z * back;
        }
        sparkGeo.attributes.position.needsUpdate = true;

        if (p >= 1) {
          active = null;
          meteorGroup.visible = false;
        }
      }

      if (opts.isPaused?.() || active) return;

      const ctx = opts.getContext?.() || {};
      if (ctx.sulking) return;

      const cooldownOk = now - lastTriggerAt >= 70000;
      if (!cooldownOk) return;

      // Gentle balcony discovery beat (~24s on ocean sofa) if player hasn't witnessed one yet
      if (ctx.zone === "terrace" && !seenNaturalOnce && terraceEnteredAt && now - terraceEnteredAt >= 24000) {
        launchStreak("terrace_discovery");
        return;
      }

      if (now - lastRollAt >= 18000) {
        lastRollAt = now;
        let prob = 0.16;
        if (ctx.zone === "terrace") prob += 0.16;
        if (ctx.dusk) prob += 0.14;
        if (Math.random() < prob) {
          launchStreak("probabilistic");
        }
      }
    },
    getState() {
      return { active: Boolean(active), countTriggered };
    },
    dispose() {
      scene.remove(meteorGroup);
      headGeo.dispose();
      headMat.dispose();
      tailGeo.dispose();
      tailMat.dispose();
      sparkGeo.dispose();
      sparkMat.dispose();
    },
  };
}
