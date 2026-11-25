import * as THREE from "three";

/**
 * Sculpted Articulated 3D Bruce (Candidate 01: Cream Long-haired Dachshund w/ Burgundy Twill Neckerchief)
 * Named hierarchy: root -> bodyPivot -> { torso, headPivot (eyeL, eyeR, earL, earR, tongue), legFL/FR/BL/BR, tailPivot, scarfPivot, blanket, wetDrops }
 */
export function createBruce3D(mats) {
  const root = new THREE.Group();
  const bodyPivot = new THREE.Group();
  root.add(bodyPivot);

  // 1. Sculpted Dachshund Torso via smooth LatheGeometry profile rotated along Z
  const torsoPts = [
    new THREE.Vector2(0.01, -0.78),
    new THREE.Vector2(0.21, -0.70),
    new THREE.Vector2(0.30, -0.45),
    new THREE.Vector2(0.28, -0.05),
    new THREE.Vector2(0.32, 0.34), // deep chest
    new THREE.Vector2(0.27, 0.62),
    new THREE.Vector2(0.14, 0.76),
    new THREE.Vector2(0.01, 0.80),
  ];
  const torsoGeo = new THREE.LatheGeometry(torsoPts, 24);
  torsoGeo.rotateX(Math.PI / 2);
  torsoGeo.scale(0.88, 0.96, 1.0);
  const torso = new THREE.Mesh(torsoGeo, mats.furCream);
  torso.position.y = 0.50;
  torso.castShadow = true;
  torso.receiveShadow = true;
  bodyPivot.add(torso);

  // Feathered chest ruff
  const ruffGeo = new THREE.SphereGeometry(0.24, 18, 14);
  ruffGeo.scale(0.85, 1.05, 0.75);
  const ruff = new THREE.Mesh(ruffGeo, mats.furCream);
  ruff.position.set(0, 0.45, 0.56);
  ruff.castShadow = true;
  bodyPivot.add(ruff);

  // 2. Signature Burgundy Twill Silk Neckerchief
  const scarfPivot = new THREE.Group();
  scarfPivot.position.set(0, 0.62, 0.50);
  bodyPivot.add(scarfPivot);

  const collarMesh = new THREE.Mesh(new THREE.TorusGeometry(0.23, 0.045, 12, 24), mats.scarfSilk);
  collarMesh.rotation.x = Math.PI * 0.38;
  collarMesh.castShadow = true;
  scarfPivot.add(collarMesh);

  const bibGeo = new THREE.ConeGeometry(0.16, 0.28, 4);
  bibGeo.rotateX(Math.PI);
  bibGeo.scale(1.1, 1.0, 0.35);
  const bibMesh = new THREE.Mesh(bibGeo, mats.scarfSilk);
  bibMesh.position.set(0, -0.14, 0.21);
  bibMesh.rotation.x = -0.22;
  bibMesh.castShadow = true;
  scarfPivot.add(bibMesh);

  const knotMesh = new THREE.Mesh(new THREE.SphereGeometry(0.052, 12, 10), mats.scarfSilk);
  knotMesh.position.set(0, -0.02, 0.23);
  scarfPivot.add(knotMesh);

  // Brass tag on collar
  const tagMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.036, 0.036, 0.014, 16), mats.brass);
  tagMesh.rotation.x = Math.PI / 2;
  tagMesh.position.set(0.06, -0.10, 0.24);
  scarfPivot.add(tagMesh);

  // 3. Neck & Sculpted Dachshund Head Group
  const headPivot = new THREE.Group();
  headPivot.position.set(0, 0.72, 0.64);
  bodyPivot.add(headPivot);

  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.22, 0.26, 16), mats.furCream);
  neck.position.set(0, -0.08, -0.05);
  neck.rotation.x = 0.28;
  neck.castShadow = true;
  headPivot.add(neck);

  // Cranium
  const skullGeo = new THREE.SphereGeometry(0.23, 22, 18);
  skullGeo.scale(0.92, 0.94, 1.05);
  const skull = new THREE.Mesh(skullGeo, mats.furCream);
  skull.position.set(0, 0.12, 0.04);
  skull.castShadow = true;
  headPivot.add(skull);

  // Sleek tapered dachshund snout
  const snoutPts = [
    new THREE.Vector2(0.01, 0),
    new THREE.Vector2(0.08, 0.04),
    new THREE.Vector2(0.115, 0.16),
    new THREE.Vector2(0.155, 0.32),
  ];
  const snoutGeo = new THREE.LatheGeometry(snoutPts, 18);
  snoutGeo.rotateX(-Math.PI / 2);
  snoutGeo.scale(0.95, 0.78, 1.0);
  const snout = new THREE.Mesh(snoutGeo, mats.furCream);
  snout.position.set(0, 0.06, 0.39);
  snout.castShadow = true;
  headPivot.add(snout);

  // Wet glossy black nose
  const noseGeo = new THREE.SphereGeometry(0.052, 16, 12);
  noseGeo.scale(1.15, 0.85, 0.9);
  const nose = new THREE.Mesh(noseGeo, mats.noseWet);
  nose.position.set(0, 0.085, 0.39);
  headPivot.add(nose);

  // Cute pink tongue (shown when excited)
  const tongueGeo = new THREE.SphereGeometry(0.042, 12, 10);
  tongueGeo.scale(0.8, 0.3, 1.5);
  const tongue = new THREE.Mesh(tongueGeo, mats.tonguePink);
  tongue.position.set(0, -0.01, 0.31);
  tongue.rotation.x = 0.35;
  tongue.visible = false;
  headPivot.add(tongue);

  // Expressive 3D eyes with catchlights
  const makeEye = (side) => {
    const eyePivot = new THREE.Group();
    eyePivot.position.set(side * 0.105, 0.14, 0.21);
    const orb = new THREE.Mesh(new THREE.SphereGeometry(0.042, 16, 14), mats.eyeGloss);
    const glint = new THREE.Mesh(new THREE.SphereGeometry(0.013, 8, 8), mats.eyeWhite);
    glint.position.set(side * 0.012, 0.015, 0.036);
    eyePivot.add(orb, glint);
    headPivot.add(eyePivot);
    return eyePivot;
  };
  const eyeL = makeEye(-1);
  const eyeR = makeEye(1);

  // Feathered long dachshund ears (hinged cleanly on upper sides of cranium)
  const makeEar = (side) => {
    const earPivot = new THREE.Group();
    earPivot.position.set(side * 0.18, 0.18, -0.02);
    const earGeo = new THREE.SphereGeometry(0.14, 16, 14);
    earGeo.scale(0.32, 1.55, 0.82);
    const earMesh = new THREE.Mesh(earGeo, mats.furEar);
    earMesh.position.set(side * 0.03, -0.18, 0.02);
    earMesh.rotation.z = side * -0.14;
    earMesh.castShadow = true;
    earPivot.add(earMesh);
    headPivot.add(earPivot);
    return earPivot;
  };
  const earL = makeEar(-1);
  const earR = makeEar(1);

  // 4. Four Short Articulated Legs
  const makeLeg = (x, z) => {
    const legPivot = new THREE.Group();
    legPivot.position.set(x, 0.34, z);
    const shaft = new THREE.Mesh(new THREE.CapsuleGeometry(0.068, 0.20, 8, 12), mats.furCream);
    shaft.position.y = -0.14;
    shaft.castShadow = true;
    const paw = new THREE.Mesh(new THREE.SphereGeometry(0.078, 12, 10), mats.furCream);
    paw.scale.set(0.95, 0.58, 1.32);
    paw.position.set(0, -0.29, 0.035);
    paw.castShadow = true;
    legPivot.add(shaft, paw);
    bodyPivot.add(legPivot);
    return legPivot;
  };
  const legFL = makeLeg(-0.15, 0.44);
  const legFR = makeLeg(0.15, 0.44);
  const legBL = makeLeg(-0.15, -0.44);
  const legBR = makeLeg(0.15, -0.44);

  // 5. Silky Plumed Tail
  const tailPivot = new THREE.Group();
  tailPivot.position.set(0, 0.54, -0.74);
  bodyPivot.add(tailPivot);

  const tailCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0, 0.14, -0.18),
    new THREE.Vector3(0, 0.30, -0.34),
    new THREE.Vector3(0, 0.36, -0.48),
  ]);
  const tailMesh = new THREE.Mesh(new THREE.TubeGeometry(tailCurve, 14, 0.048, 10, false), mats.furEar);
  tailMesh.castShadow = true;
  tailPivot.add(tailMesh);

  // 6. Optional Props: Cozy Blanket & Wet Paw Droplets
  const blanket = new THREE.Mesh(
    new THREE.CylinderGeometry(0.32, 0.33, 0.68, 18, 1, false, -Math.PI * 0.48, Math.PI * 0.96),
    mats.blanketRose
  );
  blanket.rotation.x = Math.PI / 2;
  blanket.rotation.z = Math.PI / 2;
  blanket.position.set(0, 0.51, -0.08);
  blanket.visible = false;
  blanket.castShadow = true;
  bodyPivot.add(blanket);

  const wetDrops = new THREE.Group();
  const dropMat = new THREE.MeshPhysicalMaterial({ color: 0x70b8e8, roughness: 0.08, clearcoat: 1 });
  [[-0.18, 0.06, 0.48], [0.18, 0.06, 0.48], [-0.18, 0.06, -0.42], [0.18, 0.06, -0.42]].forEach(([dx, dy, dz]) => {
    const d = new THREE.Mesh(new THREE.SphereGeometry(0.032, 10, 8), dropMat);
    d.position.set(dx, dy, dz);
    wetDrops.add(d);
  });
  wetDrops.visible = false;
  bodyPivot.add(wetDrops);

  let currentMood = "happy";
  let blinkTimer = 0;

  return {
    root,
    joints: { bodyPivot, headPivot, earL, earR, eyeL, eyeR, legFL, legFR, legBL, legBR, tailPivot, scarfPivot, tongue, blanket, wetDrops },
    setMood(m) { currentMood = m; },
    update(dt, t, opts = {}) {
      const mood = opts.mood || currentMood;
      const walkSpeed = opts.walkSpeed || 0;
      const lookTarget = opts.lookTarget || null;
      blanket.visible = Boolean(opts.blanketOn);
      wetDrops.visible = Boolean(opts.wetPaws);
      tongue.visible = mood === "excited";

      // Reset base transforms smoothly
      let bodyY = 0;
      let bodyRoll = 0;
      let bodyPitch = 0;
      let scarfTwist = 0;
      let earBack = 0;
      let tailWagSpeed = 6.5;
      let tailWagAmp = 0.35;
      let tailPitch = 0;

      if (mood === "excited") {
        bodyY = Math.abs(Math.sin(t * 9)) * 0.05;
        tailWagSpeed = 14;
        tailWagAmp = 0.55;
        earBack = -0.16;
      } else if (mood === "warn") {
        bodyY = -0.05;
        earBack = 0.62;
        tailWagSpeed = 1.4;
        tailWagAmp = 0.08;
        tailPitch = -0.45;
      } else if (mood === "sulk") {
        bodyY = -0.10;
        scarfTwist = 0.40;
        earBack = 0.25;
        tailWagSpeed = 0.8;
        tailWagAmp = 0.04;
        tailPitch = -0.65;
      } else if (mood === "sleep") {
        bodyY = -0.22;
        bodyRoll = 0.25;
        tailWagSpeed = 0.5;
        tailWagAmp = 0.02;
        tailPitch = -0.7;
      } else if (mood === "belly") {
        bodyY = 0.16;
        bodyRoll = Math.PI;
        tailWagSpeed = 10;
        tailWagAmp = 0.45;
      }

      bodyPivot.position.y += (bodyY - bodyPivot.position.y) * Math.min(1, dt * 8);
      bodyPivot.rotation.z += (bodyRoll - bodyPivot.rotation.z) * Math.min(1, dt * 8);
      bodyPivot.rotation.x += (bodyPitch - bodyPivot.rotation.x) * Math.min(1, dt * 8);

      // Breathing
      const breath = 1 + Math.sin(t * (mood === "excited" ? 5 : 2.4)) * 0.018;
      torso.scale.set(0.88 * breath, 0.96 * breath, 1.0);

      // Scarf crookedness
      scarfPivot.rotation.z += (scarfTwist - scarfPivot.rotation.z) * Math.min(1, dt * 6);

      // Tail wag
      tailPivot.rotation.y = Math.sin(t * tailWagSpeed) * tailWagAmp;
      tailPivot.rotation.x += (tailPitch - tailPivot.rotation.x) * Math.min(1, dt * 6);

      // Ears
      const earBounce = walkSpeed > 0.1 ? Math.sin(t * 14) * 0.08 : Math.sin(t * 2.5) * 0.02;
      earL.rotation.x += (earBack + earBounce - earL.rotation.x) * Math.min(1, dt * 10);
      earR.rotation.x += (earBack - earBounce - earR.rotation.x) * Math.min(1, dt * 10);

      // Trotting gait
      if (walkSpeed > 0.05) {
        const s = Math.sin(t * 13) * Math.min(1, walkSpeed) * 0.55;
        legFL.rotation.x = s;
        legBR.rotation.x = s;
        legFR.rotation.x = -s;
        legBL.rotation.x = -s;
      } else if (mood === "belly") {
        const w = Math.sin(t * 8) * 0.25;
        legFL.rotation.x = 0.6 + w;
        legFR.rotation.x = 0.6 - w;
        legBL.rotation.x = 0.5 - w;
        legBR.rotation.x = 0.5 + w;
      } else {
        legFL.rotation.x *= 0.85;
        legFR.rotation.x *= 0.85;
        legBL.rotation.x *= 0.85;
        legBR.rotation.x *= 0.85;
      }

      // Head tracking lookTarget (in world space)
      let targetYaw = 0;
      let targetPitch = mood === "sulk" ? 0.24 : mood === "phone" ? -0.06 : 0;
      if (lookTarget) {
        const localTarget = root.worldToLocal(lookTarget.clone());
        targetYaw = Math.max(-0.55, Math.min(0.55, Math.atan2(localTarget.x, Math.max(0.4, localTarget.z - 0.3))));
        targetPitch = Math.max(-0.35, Math.min(0.35, -(localTarget.y - 0.8) * 0.35));
      }
      headPivot.rotation.y += (targetYaw - headPivot.rotation.y) * Math.min(1, dt * 7);
      headPivot.rotation.x += (targetPitch - headPivot.rotation.x) * Math.min(1, dt * 7);

      // Natural blinking
      blinkTimer = (blinkTimer + dt) % 4.2;
      const eyeScaleY = blinkTimer > 4.06 ? 0.12 : 1.0;
      eyeL.scale.y = eyeScaleY;
      eyeR.scale.y = eyeScaleY;
    },
  };
}

/**
 * Dynamic 3D Catenary Woven Leather Leash connecting owner hand anchor to Bruce's collar
 */
export function createLeash3D(mats) {
  const mat = new THREE.MeshStandardMaterial({ color: 0x7b2131, roughness: 0.45 });
  const curve = new THREE.QuadraticBezierCurve3(
    new THREE.Vector3(0, 1.3, 2.6),
    new THREE.Vector3(0, 0.5, 1.5),
    new THREE.Vector3(0, 0.65, 0.55)
  );
  const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, 18, 0.022, 8, false), mat);
  mesh.castShadow = true;

  return {
    mesh,
    update(pStart, pEnd) {
      const dist = pStart.distanceTo(pEnd);
      const sag = Math.max(0.15, Math.min(0.75, 0.85 - dist * 0.14));
      curve.v0.copy(pStart);
      curve.v2.copy(pEnd);
      curve.v1.lerpVectors(pStart, pEnd, 0.5);
      curve.v1.y = Math.min(pStart.y, pEnd.y) - sag * 0.5;
      mesh.geometry.dispose();
      mesh.geometry = new THREE.TubeGeometry(curve, 18, 0.022, 8, false);
    },
  };
}
