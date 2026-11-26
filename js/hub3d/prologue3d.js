import * as THREE from "three";

function makeWalnutTexture() {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 512;
  const ctx = c.getContext("2d");
  const grad = ctx.createLinearGradient(0, 0, 512, 0);
  grad.addColorStop(0, "#382016");
  grad.addColorStop(0.5, "#46281B");
  grad.addColorStop(1, "#321C12");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 512, 512);

  for (let i = 0; i < 190; i++) {
    const x = (i * 2.71) % 512;
    const w = 1 + (i % 4);
    ctx.strokeStyle = i % 3 === 0 ? "rgba(22, 11, 6, 0.28)" : "rgba(104, 62, 38, 0.14)";
    ctx.lineWidth = w;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    for (let y = 32; y <= 512; y += 32) {
      const wave = Math.sin(y * 0.025 + i * 0.4) * 5;
      ctx.lineTo(x + wave, y);
    }
    ctx.stroke();
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  return tex;
}

function makeBronzeTexture() {
  const c = document.createElement("canvas");
  c.width = 256;
  c.height = 256;
  const ctx = c.getContext("2d");
  const g = ctx.createLinearGradient(0, 0, 256, 256);
  g.addColorStop(0, "#2A2422");
  g.addColorStop(0.5, "#1E1918");
  g.addColorStop(1, "#2E2724");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 220; i++) {
    ctx.fillStyle = i % 2 === 0 ? "rgba(255, 224, 178, 0.035)" : "rgba(0, 0, 0, 0.08)";
    ctx.fillRect((i * 1.17) % 256, 0, 1, 256);
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  return tex;
}

function makeMarbleFloorTexture() {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 512;
  const ctx = c.getContext("2d");
  ctx.fillStyle = "#EAE0D0";
  ctx.fillRect(0, 0, 512, 512);

  // Subtle tile grid & warm cream travertine veining
  ctx.strokeStyle = "rgba(156, 128, 88, 0.2)";
  ctx.lineWidth = 2;
  for (let i = 0; i <= 512; i += 128) {
    ctx.beginPath();
    ctx.moveTo(i, 0);
    ctx.lineTo(i, 512);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, i);
    ctx.lineTo(512, i);
    ctx.stroke();
  }
  for (let v = 0; v < 24; v++) {
    ctx.strokeStyle = v % 3 === 0 ? "rgba(182, 148, 102, 0.16)" : "rgba(255, 250, 240, 0.35)";
    ctx.lineWidth = 1.2 + (v % 2);
    ctx.beginPath();
    let x = (v * 37) % 512;
    let y = (v * 53) % 512;
    ctx.moveTo(x, y);
    for (let s = 0; s < 6; s++) {
      x += 34 + Math.sin(v + s) * 18;
      y += 28 + Math.cos(v * 2 + s) * 14;
      ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(3, 4);
  return tex;
}

function makeStoneWallTexture() {
  const c = document.createElement("canvas");
  c.width = 256;
  c.height = 256;
  const ctx = c.getContext("2d");
  ctx.fillStyle = "#E2D7C5";
  ctx.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 650; i++) {
    const shade = 205 + (i % 24);
    ctx.fillStyle = `rgba(${shade}, ${shade - 8}, ${shade - 20}, 0.25)`;
    ctx.fillRect((i * 29) % 256, (i * 47) % 256, 6, 4);
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(2, 2);
  return tex;
}

function makeDialCanvas() {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 144;
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const draw = (floorStr, subStr, isPH = false) => {
    const ctx = c.getContext("2d");
    ctx.fillStyle = "#120F0E";
    ctx.fillRect(0, 0, 512, 144);
    ctx.strokeStyle = "#DFBE7D";
    ctx.lineWidth = 4;
    ctx.strokeRect(8, 8, 496, 128);

    ctx.fillStyle = isPH ? "#FFE7A3" : "#DFBE7D";
    ctx.font = "900 54px -apple-system, BlinkMacSystemFont, sans-serif";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText(floorStr, 36, 72);

    ctx.fillStyle = isPH ? "#FFFFFF" : "rgba(246, 238, 222, 0.72)";
    ctx.font = "700 22px -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif";
    ctx.textAlign = "right";
    ctx.fillText(subStr, 474, 72);
    tex.needsUpdate = true;
  };
  draw("16 ▲", "PRIVATE PENTHOUSE LIFT");
  return { tex, draw };
}

function makeNameplateTexture() {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 128;
  const ctx = c.getContext("2d");
  const g = ctx.createLinearGradient(0, 0, 512, 128);
  g.addColorStop(0, "#FCECB6");
  g.addColorStop(0.5, "#DFBE7D");
  g.addColorStop(1, "#B38637");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 512, 128);
  ctx.strokeStyle = "#4A310D";
  ctx.lineWidth = 6;
  ctx.strokeRect(10, 10, 492, 108);
  ctx.fillStyle = "#221409";
  ctx.font = "900 28px -apple-system, BlinkMacSystemFont, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("PH · 01   SUNLIT LOFT", 256, 65);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function mountPrologue3D(canvasEl, opts = {}) {
  let destroyed = false;
  let rafId = null;

  const disposables = [];
  const trackGeo = (g) => { disposables.push(g); return g; };
  const trackMat = (m) => { disposables.push(m); return m; };
  const trackTex = (t) => { disposables.push(t); return t; };

  const renderer = new THREE.WebGLRenderer({
    canvas: canvasEl,
    antialias: true,
    powerPreference: "high-performance",
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.18;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xdad0c0);
  scene.fog = new THREE.FogExp2(0xdad0c0, 0.022);

  // Interior PMREM bronze/warm-stone environment so brass hardware & walnut have real reflections
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene();
  envScene.background = new THREE.Color(0x282422);
  const envBox = new THREE.Mesh(
    new THREE.BoxGeometry(16, 12, 16),
    new THREE.MeshBasicMaterial({ color: 0x38302b, side: THREE.BackSide }),
  );
  const envGlowStrip = new THREE.Mesh(
    new THREE.PlaneGeometry(8, 2.5),
    new THREE.MeshBasicMaterial({ color: 0xffe4aa }),
  );
  envGlowStrip.position.set(0, 5.2, -3);
  envGlowStrip.rotation.x = Math.PI * 0.5;
  envScene.add(envBox, envGlowStrip);
  const envRT = pmrem.fromScene(envScene, 0.04);
  scene.environment = envRT.texture;
  scene.environmentIntensity = 0.85;
  pmrem.dispose();
  envBox.geometry.dispose();
  envBox.material.dispose();
  envGlowStrip.geometry.dispose();
  envGlowStrip.material.dispose();
  disposables.push(envRT);

  const camera = new THREE.PerspectiveCamera(50, 16 / 9, 0.1, 60);
  const baseCamPos = new THREE.Vector3(0, 1.54, 5.95);
  const baseLookAt = new THREE.Vector3(0, 1.62, 0.0);
  camera.position.copy(baseCamPos);
  camera.lookAt(baseLookAt);

  // Materials
  const walnutTex = trackTex(makeWalnutTexture());
  const bronzeTex = trackTex(makeBronzeTexture());
  const marbleTex = trackTex(makeMarbleFloorTexture());
  const stoneTex = trackTex(makeStoneWallTexture());
  const plateTex = trackTex(makeNameplateTexture());
  const dial = makeDialCanvas();
  trackTex(dial.tex);

  const matWalnut = trackMat(new THREE.MeshStandardMaterial({
    map: walnutTex,
    roughness: 0.42,
    metalness: 0.08,
  }));
  const matWalnutPanel = trackMat(new THREE.MeshStandardMaterial({
    map: walnutTex,
    color: 0xd8c3b4,
    roughness: 0.36,
    metalness: 0.1,
  }));
  const matBronze = trackMat(new THREE.MeshStandardMaterial({
    map: bronzeTex,
    roughness: 0.32,
    metalness: 0.82,
  }));
  const matBrass = trackMat(new THREE.MeshStandardMaterial({
    color: 0xe6c37a,
    roughness: 0.24,
    metalness: 0.92,
  }));
  const matMarble = trackMat(new THREE.MeshStandardMaterial({
    map: marbleTex,
    roughness: 0.22,
    metalness: 0.1,
  }));
  const matStoneWall = trackMat(new THREE.MeshStandardMaterial({
    map: stoneTex,
    roughness: 0.68,
    metalness: 0.06,
  }));
  const matCeiling = trackMat(new THREE.MeshStandardMaterial({
    color: 0xe6dccb,
    roughness: 0.72,
    metalness: 0.04,
  }));
  const matRug = trackMat(new THREE.MeshStandardMaterial({
    color: 0x541825,
    roughness: 0.92,
    metalness: 0.0,
  }));
  const matCoveGlow = trackMat(new THREE.MeshBasicMaterial({ color: 0xffe0a1 }));

  // =========================================================================
  // ARCHITECTURAL SHELL: PENTHOUSE ELEVATOR CAB (z = 2.85 .. 6.8)
  // =========================================================================
  const floorMesh = new THREE.Mesh(trackGeo(new THREE.PlaneGeometry(7.2, 9.6)), matMarble);
  floorMesh.rotation.x = -Math.PI / 2;
  floorMesh.position.set(0, 0, 3.0);
  floorMesh.receiveShadow = true;
  scene.add(floorMesh);

  const ceilingMesh = new THREE.Mesh(trackGeo(new THREE.PlaneGeometry(7.2, 9.6)), matCeiling);
  ceilingMesh.rotation.x = Math.PI / 2;
  ceilingMesh.position.set(0, 3.32, 3.0);
  scene.add(ceilingMesh);

  // Elevator cab side walls (x = +/- 1.82)
  [-1, 1].forEach((side) => {
    const x = side * 1.82;
    const cabWall = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.14, 3.35, 4.1)), matBronze);
    cabWall.position.set(x, 1.67, 4.9);
    scene.add(cabWall);

    // Fluted walnut inset slats inside elevator cab
    for (let s = 0; s < 9; s++) {
      const slat = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.05, 2.55, 0.16)), matWalnut);
      slat.position.set(x - side * 0.07, 1.45, 3.25 + s * 0.36);
      scene.add(slat);
    }

    // Horizontal brushed-brass handrail
    const rail = new THREE.Mesh(trackGeo(new THREE.CylinderGeometry(0.025, 0.025, 3.3, 12)), matBrass);
    rail.rotation.x = Math.PI / 2;
    rail.position.set(x - side * 0.16, 1.05, 4.75);
    scene.add(rail);

    // Vertical warm LED cove light strip
    const cove = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.025, 2.9, 0.04)), matCoveGlow);
    cove.position.set(x - side * 0.09, 1.6, 3.02);
    scene.add(cove);
  });

  // Recessed elevator ceiling coffer + warm overhead downlight
  const cabCoffer = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(2.4, 0.06, 2.6)), matBronze);
  cabCoffer.position.set(0, 3.26, 4.75);
  scene.add(cabCoffer);
  const cabCeilingGlow = new THREE.Mesh(trackGeo(new THREE.PlaneGeometry(1.9, 2.1)), matCoveGlow);
  cabCeilingGlow.rotation.x = Math.PI / 2;
  cabCeilingGlow.position.set(0, 3.22, 4.75);
  scene.add(cabCeilingGlow);

  // Elevator front portal wall at z = 2.86 (leaves 2.04m x 2.62m center opening)
  const portalLeft = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(2.6, 3.36, 0.24)), matStoneWall);
  portalLeft.position.set(-2.32, 1.68, 2.86);
  const portalRight = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(2.6, 3.36, 0.24)), matStoneWall);
  portalRight.position.set(2.32, 1.68, 2.86);
  const portalTop = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(2.2, 0.74, 0.24)), matStoneWall);
  portalTop.position.set(0, 2.98, 2.86);
  scene.add(portalLeft, portalRight, portalTop);

  // Brushed-brass elevator portal frame + overhead floor indicator
  const portalJambL = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.08, 2.64, 0.28)), matBrass);
  portalJambL.position.set(-1.04, 1.32, 2.86);
  const portalJambR = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.08, 2.64, 0.28)), matBrass);
  portalJambR.position.set(1.04, 1.32, 2.86);
  const portalLintel = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(2.16, 0.1, 0.28)), matBrass);
  portalLintel.position.set(0, 2.64, 2.86);
  scene.add(portalJambL, portalJambR, portalLintel);

  const dialPlate = new THREE.Mesh(
    trackGeo(new THREE.PlaneGeometry(0.96, 0.25)),
    trackMat(new THREE.MeshBasicMaterial({ map: dial.tex })),
  );
  dialPlate.position.set(0, 2.52, 3.02);
  scene.add(dialPlate);

  // Sliding 3D Double Bronze Elevator Doors
  const elevDoorGeo = trackGeo(new THREE.BoxGeometry(1.03, 2.62, 0.08));
  const elevTrimGeo = trackGeo(new THREE.BoxGeometry(0.76, 2.15, 0.03));
  const elevDoorL = new THREE.Group();
  elevDoorL.position.set(-0.515, 1.31, 2.86);
  const elevLeafL = new THREE.Mesh(elevDoorGeo, matBronze);
  const elevInsetL = new THREE.Mesh(elevTrimGeo, matWalnut);
  elevInsetL.position.z = 0.04;
  const elevSeamL = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.02, 2.62, 0.095)), matBrass);
  elevSeamL.position.x = 0.505;
  elevDoorL.add(elevLeafL, elevInsetL, elevSeamL);

  const elevDoorR = new THREE.Group();
  elevDoorR.position.set(0.515, 1.31, 2.86);
  const elevLeafR = new THREE.Mesh(elevDoorGeo, matBronze);
  const elevInsetR = new THREE.Mesh(elevTrimGeo, matWalnut);
  elevInsetR.position.z = 0.04;
  const elevSeamR = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.02, 2.62, 0.095)), matBrass);
  elevSeamR.position.x = -0.505;
  elevDoorR.add(elevLeafR, elevInsetR, elevSeamR);
  scene.add(elevDoorL, elevDoorR);

  // =========================================================================
  // ARCHITECTURAL SHELL: PENTHOUSE PRIVATE FOYER (z = 0 .. 2.75)
  // =========================================================================
  // Left & Right Stone/Walnut Foyer Walls
  [-1, 1].forEach((side) => {
    const wx = side * 2.75;
    const upperWall = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.18, 3.36, 3.0)), matStoneWall);
    upperWall.position.set(wx, 1.68, 1.38);
    upperWall.receiveShadow = true;
    scene.add(upperWall);

    // Lower walnut architectural wainscoting
    const wainscot = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.06, 1.15, 2.8)), matWalnut);
    wainscot.position.set(wx - side * 0.1, 0.58, 1.38);
    const chairRail = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.08, 0.05, 2.82)), matBrass);
    chairRail.position.set(wx - side * 0.1, 1.16, 1.38);
    scene.add(wainscot, chairRail);
  });

  // Back wall around the 3D entrance doorway (z = 0.0)
  const backWallL = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(2.1, 3.36, 0.28)), matStoneWall);
  backWallL.position.set(-1.82, 1.68, 0.0);
  backWallL.receiveShadow = true;
  const backWallR = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(2.1, 3.36, 0.28)), matStoneWall);
  backWallR.position.set(1.82, 1.68, 0.0);
  backWallR.receiveShadow = true;
  const backWallTop = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(1.7, 0.78, 0.28)), matStoneWall);
  backWallTop.position.set(0, 2.97, 0.0);
  scene.add(backWallL, backWallR, backWallTop);

  // Two 3D Brass & Frosted Glass Wall Sconces flanking the doorway
  const sconceGlassMat = trackMat(new THREE.MeshBasicMaterial({ color: 0xffefc9 }));
  [-1, 1].forEach((side) => {
    const sx = side * 1.24;
    const backplate = new THREE.Mesh(trackGeo(new THREE.CylinderGeometry(0.08, 0.08, 0.03, 18)), matBrass);
    backplate.rotation.x = Math.PI / 2;
    backplate.position.set(sx, 1.92, 0.16);
    const shade = new THREE.Mesh(trackGeo(new THREE.CylinderGeometry(0.055, 0.042, 0.28, 16)), sconceGlassMat);
    shade.position.set(sx, 2.02, 0.23);
    const ring = new THREE.Mesh(trackGeo(new THREE.TorusGeometry(0.056, 0.008, 8, 24)), matBrass);
    ring.rotation.x = Math.PI / 2;
    ring.position.set(sx, 1.89, 0.23);
    scene.add(backplate, shade, ring);
  });

  // Left Marble & Brass Entry Console Table + Decorative Vase (frames doorway nicely)
  const consoleGroup = new THREE.Group();
  consoleGroup.position.set(-1.62, 0, 1.05);
  const consoleTop = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.55, 0.05, 1.15)), matMarble);
  consoleTop.position.y = 0.84;
  consoleTop.castShadow = true;
  consoleGroup.add(consoleTop);
  [[-0.22, -0.5], [0.22, -0.5], [-0.22, 0.5], [0.22, 0.5]].forEach(([lx, lz]) => {
    const leg = new THREE.Mesh(trackGeo(new THREE.CylinderGeometry(0.018, 0.018, 0.84, 10)), matBrass);
    leg.position.set(lx, 0.42, lz);
    consoleGroup.add(leg);
  });
  const vase = new THREE.Mesh(
    trackGeo(new THREE.CylinderGeometry(0.08, 0.11, 0.34, 18)),
    trackMat(new THREE.MeshStandardMaterial({ color: 0xece3d5, roughness: 0.35 })),
  );
  vase.position.set(0, 1.03, -0.22);
  const brassTray = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.24, 0.02, 0.18)), matBrass);
  brassTray.position.set(0.04, 0.875, 0.22);
  consoleGroup.add(vase, brassTray);
  scene.add(consoleGroup);

  // Right Architectural Brass Planter Stand + Greenery (balances right side of Foyer)
  const planterGroup = new THREE.Group();
  planterGroup.position.set(1.62, 0, 1.02);
  const potMesh = new THREE.Mesh(
    trackGeo(new THREE.CylinderGeometry(0.22, 0.17, 0.48, 20)),
    trackMat(new THREE.MeshStandardMaterial({ color: 0x262425, roughness: 0.5 })),
  );
  potMesh.position.y = 0.38;
  const potStand = new THREE.Mesh(trackGeo(new THREE.CylinderGeometry(0.23, 0.23, 0.04, 20)), matBrass);
  potStand.position.y = 0.14;
  const leafMat = trackMat(new THREE.MeshStandardMaterial({ color: 0x2a523c, roughness: 0.72 }));
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2;
    const leaf = new THREE.Mesh(trackGeo(new THREE.SphereGeometry(0.14, 10, 8)), leafMat);
    leaf.scale.set(1.2, 0.45, 0.7);
    leaf.position.set(Math.cos(a) * 0.15, 0.74 + (i % 2) * 0.08, Math.sin(a) * 0.15);
    leaf.rotation.set(0.3, a, 0.35);
    planterGroup.add(leaf);
  }
  planterGroup.add(potMesh, potStand);
  scene.add(planterGroup);

  // Woven Burgundy Runner Carpet leading up to the door threshold
  const runnerMesh = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(1.42, 0.014, 2.3)), matRug);
  runnerMesh.position.set(0, 0.008, 1.38);
  runnerMesh.receiveShadow = true;
  const runnerBorder = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(1.48, 0.01, 2.36)), matBrass);
  runnerBorder.position.set(0, 0.005, 1.38);
  scene.add(runnerBorder, runnerMesh);

  // =========================================================================
  // SCULPTED 3D AMERICAN WALNUT ENTRANCE DOOR + BRASS ARCHITRAVE + HINGE PIVOT
  // =========================================================================
  // Deep stepped 3D walnut & brass architrave frame
  const jambL = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.14, 2.66, 0.34)), matWalnut);
  jambL.position.set(-0.81, 1.33, 0.04);
  const jambR = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.14, 2.66, 0.34)), matWalnut);
  jambR.position.set(0.81, 1.33, 0.04);
  const jambTop = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(1.82, 0.16, 0.36)), matWalnut);
  jambTop.position.set(0, 2.64, 0.04);
  const jambBrassTrim = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(1.56, 2.6, 0.3)), matBrass);
  jambBrassTrim.position.set(0, 1.3, 0.02);
  // Hollow out center visually by keeping trim only as thin border strips:
  jambBrassTrim.visible = false;
  const brassBorderL = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.025, 2.62, 0.35)), matBrass);
  brassBorderL.position.set(-0.745, 1.31, 0.04);
  const brassBorderR = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.025, 2.62, 0.35)), matBrass);
  brassBorderR.position.set(0.745, 1.31, 0.04);
  const brassBorderTop = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(1.52, 0.025, 0.35)), matBrass);
  brassBorderTop.position.set(0, 2.57, 0.04);
  const threshold = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(1.56, 0.024, 0.32)), matBrass);
  threshold.position.set(0, 0.012, 0.04);
  scene.add(jambL, jambR, jambTop, brassBorderL, brassBorderR, brassBorderTop, threshold);

  // Hinge group pivoted cleanly on the inside left jamb (-0.73, 0, 0.02) for inward swing
  const doorHingeGroup = new THREE.Group();
  doorHingeGroup.position.set(-0.73, 0, 0.02);
  scene.add(doorHingeGroup);

  const doorBodyGroup = new THREE.Group();
  doorBodyGroup.position.set(0.73, 0, 0);
  doorHingeGroup.add(doorBodyGroup);

  // Main thick walnut slab (1.46w x 2.53h x 0.11d, leaving 2.8cm warm light gap at floor)
  const doorSlab = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(1.46, 2.53, 0.11)), matWalnut);
  doorSlab.position.set(0, 1.292, 0);
  doorSlab.castShadow = true;
  doorSlab.receiveShadow = true;
  doorBodyGroup.add(doorSlab);

  // 4 Sculpted Raised 3D Coffer Panels + Beveled Trim
  const cofferDefs = [
    { x: -0.31, y: 1.78, w: 0.46, h: 0.72 },
    { x: 0.31, y: 1.78, w: 0.46, h: 0.72 },
    { x: -0.31, y: 0.78, w: 0.46, h: 0.86 },
    { x: 0.31, y: 0.78, w: 0.46, h: 0.86 },
  ];
  cofferDefs.forEach((p) => {
    const outer = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(p.w, p.h, 0.032)), matBrass);
    outer.position.set(p.x, p.y, 0.056);
    const inner = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(p.w - 0.05, p.h - 0.05, 0.045)), matWalnutPanel);
    inner.position.set(p.x, p.y, 0.062);
    inner.castShadow = true;
    doorBodyGroup.add(outer, inner);
  });

  // 3D Brushed-Brass Residential Crest Plate mounted upper-center
  const nameplateMesh = new THREE.Mesh(
    trackGeo(new THREE.BoxGeometry(0.68, 0.17, 0.025)),
    [
      matBrass, matBrass, matBrass, matBrass,
      trackMat(new THREE.MeshStandardMaterial({ map: plateTex, roughness: 0.25, metalness: 0.85 })),
      matBrass,
    ],
  );
  nameplateMesh.position.set(0, 2.28, 0.068);
  doorBodyGroup.add(nameplateMesh);

  // 3 Left Barrel Hinges in 3D brass
  [0.42, 1.32, 2.22].forEach((hy) => {
    const hinge = new THREE.Mesh(trackGeo(new THREE.CylinderGeometry(0.02, 0.02, 0.12, 12)), matBrass);
    hinge.position.set(-0.725, hy, 0.052);
    doorBodyGroup.add(hinge);
  });

  // Machined 3D Brass Escutcheon & Rotating Lever Handle (right edge)
  const escutcheon = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.07, 0.28, 0.024)), matBrass);
  escutcheon.position.set(0.61, 1.12, 0.064);
  doorBodyGroup.add(escutcheon);

  const handlePivot = new THREE.Group();
  handlePivot.position.set(0.61, 1.18, 0.088);
  const handleStem = new THREE.Mesh(trackGeo(new THREE.CylinderGeometry(0.018, 0.018, 0.055, 14)), matBrass);
  handleStem.rotation.x = Math.PI / 2;
  const handleLever = new THREE.Mesh(trackGeo(new THREE.CylinderGeometry(0.016, 0.015, 0.19, 14)), matBrass);
  handleLever.rotation.z = Math.PI / 2;
  handleLever.position.set(-0.085, 0, 0.026);
  const handleTip = new THREE.Mesh(trackGeo(new THREE.SphereGeometry(0.017, 12, 10)), matBrass);
  handleTip.position.set(-0.18, 0, 0.026);
  handlePivot.add(handleStem, handleLever, handleTip);
  doorBodyGroup.add(handlePivot);

  // Warm sunlight portal chamber BEHIND the door (revealed smoothly as the door swings inward)
  const portalBackMat = trackMat(new THREE.MeshBasicMaterial({ color: 0xfff3d4 }));
  const portalChamber = new THREE.Mesh(trackGeo(new THREE.PlaneGeometry(4.2, 4.0)), portalBackMat);
  portalChamber.position.set(0, 1.65, -1.35);
  scene.add(portalChamber);

  // Glowing golden under-door sunlight seam strip on threshold floor
  const seamMat = trackMat(new THREE.MeshBasicMaterial({
    color: 0xffdf94,
    transparent: true,
    opacity: 0.92,
  }));
  const underDoorGlow = new THREE.Mesh(trackGeo(new THREE.PlaneGeometry(1.42, 0.16)), seamMat);
  underDoorGlow.rotation.x = -Math.PI / 2;
  underDoorGlow.position.set(0, 0.026, 0.12);
  scene.add(underDoorGlow);

  // =========================================================================
  // LIGHTING RIG
  // =========================================================================
  scene.add(new THREE.AmbientLight(0xfff7ea, 0.78));
  scene.add(new THREE.HemisphereLight(0xfffaf0, 0xd4c3ae, 0.65));
  const cabLight = new THREE.PointLight(0xffe1ad, 7.5, 9, 1.6);
  cabLight.position.set(0, 2.95, 4.65);
  scene.add(cabLight);

  const foyerSconceL = new THREE.PointLight(0xffcb82, 5.4, 7, 1.6);
  foyerSconceL.position.set(-1.18, 2.02, 0.45);
  const foyerSconceR = new THREE.PointLight(0xffcb82, 5.4, 7, 1.6);
  foyerSconceR.position.set(1.18, 2.02, 0.45);
  scene.add(foyerSconceL, foyerSconceR);

  const foyerOverhead = new THREE.SpotLight(0xfff1d6, 9.0, 9, Math.PI * 0.34, 0.55, 1.5);
  foyerOverhead.position.set(0, 3.1, 1.9);
  foyerOverhead.target.position.set(0, 1.15, 0.05);
  foyerOverhead.castShadow = true;
  foyerOverhead.shadow.mapSize.set(1024, 1024);
  foyerOverhead.shadow.bias = -0.0005;
  scene.add(foyerOverhead, foyerOverhead.target);

  const sunBehindDoor = new THREE.PointLight(0xffe5a3, 4.0, 10, 1.2);
  sunBehindDoor.position.set(0, 1.5, -0.55);
  scene.add(sunBehindDoor);

  // =========================================================================
  // ANIMATION & INTERACTION STATE MACHINE
  // =========================================================================
  // Phase: "ascending" -> "opening_lift" -> "foyer" -> "unlocking"
  let phase = "ascending";
  let phaseStart = null;
  let lastDialStage = -1;
  let fovW = 0;
  let pointerNX = 0;
  let pointerNY = 0;
  let foyerNotified = false;
  let unlockDoneCb = null;

  const raycaster = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  const doorHitTargets = [doorSlab, handlePivot];

  const onPointerMove = (e) => {
    const w = window.innerWidth || 1;
    const h = window.innerHeight || 1;
    pointerNX = (e.clientX / w - 0.5) * 2;
    pointerNY = (e.clientY / h - 0.5) * 2;
  };
  window.addEventListener("pointermove", onPointerMove, { passive: true });

  const onCanvasClick = (e) => {
    if (destroyed) return;
    if (phase === "ascending") {
      phase = "opening_lift";
      phaseStart = performance.now();
      dial.draw("PH · ▲", "PENTHOUSE ARRIVED", true);
      opts.onArrivedTop?.();
      return;
    }
    if (phase === "foyer") {
      const r = canvasEl.getBoundingClientRect();
      ndc.x = ((e.clientX - r.left) / r.width) * 2 - 1;
      ndc.y = -((e.clientY - r.top) / r.height) * 2 + 1;
      raycaster.setFromCamera(ndc, camera);
      if (raycaster.intersectObjects(doorHitTargets, true).length > 0) {
        opts.onDoorClicked?.();
      }
    }
  };
  canvasEl.addEventListener("click", onCanvasClick);

  const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);
  const easeInOutQuart = (t) => (t < 0.5 ? 8 * t * t * t * t : 1 - Math.pow(-2 * t + 2, 4) / 2);

  const tick = (now) => {
    if (destroyed) return;
    if (phaseStart === null) phaseStart = now;

    // Resize responsive renderer & FOV
    const w = Math.max(300, canvasEl.clientWidth || window.innerWidth);
    const h = Math.max(240, canvasEl.clientHeight || window.innerHeight);
    const desiredFov = w < 640 ? 64 : w < 900 ? 56 : 50;
    if (canvasEl.width !== Math.round(w * renderer.getPixelRatio()) || canvasEl.height !== Math.round(h * renderer.getPixelRatio()) || fovW !== desiredFov) {
      fovW = desiredFov;
      renderer.setSize(w, h, false);
      camera.fov = desiredFov;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }

    const dtPhase = (now - phaseStart) / 1000;

    if (phase === "ascending") {
      const steps = [
        [0.0, "16 ▲", "PRIVATE PENTHOUSE LIFT", false],
        [0.42, "22 ▲", "PRIVATE PENTHOUSE LIFT", false],
        [0.86, "28 ▲", "ALMOST THERE...", false],
        [1.28, "PH · ▲", "PENTHOUSE ARRIVED", true],
      ];
      let stIdx = 0;
      for (let i = 0; i < steps.length; i++) {
        if (dtPhase >= steps[i][0]) stIdx = i;
      }
      if (stIdx !== lastDialStage) {
        lastDialStage = stIdx;
        dial.draw(steps[stIdx][1], steps[stIdx][2], steps[stIdx][3]);
        if (stIdx === 3) opts.onArrivedTop?.();
      }
      // Subtle lift vibration while ascending
      const vib = dtPhase < 1.3 ? Math.sin(dtPhase * 34) * 0.004 : 0;
      baseCamPos.set(0, 1.54 + vib, 5.95);
      baseLookAt.set(0, 1.62, 0.0);
      if (dtPhase >= 1.65) {
        phase = "opening_lift";
        phaseStart = now;
      }
    } else if (phase === "opening_lift") {
      const pDoor = Math.min(1, dtPhase / 0.85);
      const eDoor = easeInOutQuart(pDoor);
      elevDoorL.position.x = THREE.MathUtils.lerp(-0.515, -1.62, eDoor);
      elevDoorR.position.x = THREE.MathUtils.lerp(0.515, 1.62, eDoor);

      const pCam = Math.min(1, Math.max(0, (dtPhase - 0.16) / 1.05));
      const eCam = easeOutCubic(pCam);
      baseCamPos.set(0, THREE.MathUtils.lerp(1.54, 1.48, eCam), THREE.MathUtils.lerp(5.95, 3.45, eCam));
      baseLookAt.set(0, THREE.MathUtils.lerp(1.62, 1.34, eCam), 0.0);

      if (pCam >= 0.45 && !foyerNotified) {
        foyerNotified = true;
        opts.onArrivedFoyer?.();
      }
      if (pCam >= 1 && pDoor >= 1) {
        phase = "foyer";
        phaseStart = now;
      }
    } else if (phase === "foyer") {
      elevDoorL.position.x = -1.62;
      elevDoorR.position.x = 1.62;
      baseCamPos.set(0, 1.48, 3.45);
      baseLookAt.set(0, 1.34, 0.0);
      seamMat.opacity = 0.78 + Math.sin(now * 0.0032) * 0.16;
    } else if (phase === "unlocking") {
      const pHandle = Math.min(1, dtPhase / 0.18);
      handlePivot.rotation.z = THREE.MathUtils.lerp(0, -0.48, easeOutCubic(pHandle));

      const pSwing = Math.min(1, Math.max(0, (dtPhase - 0.08) / 0.76));
      const eSwing = easeInOutQuart(pSwing);
      doorHingeGroup.rotation.y = THREE.MathUtils.lerp(0, -1.22, eSwing);
      baseCamPos.set(0, 1.48, THREE.MathUtils.lerp(3.45, 0.95, eSwing));
      baseLookAt.set(0, 1.44, -1.2);
      sunBehindDoor.intensity = THREE.MathUtils.lerp(4.0, 26.0, eSwing);
      renderer.toneMappingExposure = THREE.MathUtils.lerp(1.08, 1.85, eSwing);

      if (dtPhase >= 0.92) {
        const cb = unlockDoneCb;
        unlockDoneCb = null;
        cb?.();
        return;
      }
    }

    // Subtle pointer parallax in cab / foyer
    const parAmp = phase === "unlocking" ? 0.02 : 0.11;
    camera.position.set(
      baseCamPos.x + pointerNX * parAmp,
      baseCamPos.y - pointerNY * parAmp * 0.45,
      baseCamPos.z,
    );
    camera.lookAt(baseLookAt);
    renderer.render(scene, camera);
    rafId = requestAnimationFrame(tick);
  };

  rafId = requestAnimationFrame(tick);

  return {
    skipToFoyer() {
      if (destroyed) return;
      elevDoorL.position.x = -1.62;
      elevDoorR.position.x = 1.62;
      dial.draw("PH · ▲", "PENTHOUSE ARRIVED", true);
      phase = "foyer";
      phaseStart = performance.now();
      if (!foyerNotified) {
        foyerNotified = true;
        opts.onArrivedFoyer?.();
      }
    },
    playUnlockAndSwing(onDone) {
      if (destroyed) {
        onDone?.();
        return;
      }
      elevDoorL.position.x = -1.62;
      elevDoorR.position.x = 1.62;
      phase = "unlocking";
      phaseStart = performance.now();
      unlockDoneCb = onDone;
    },
    destroy() {
      if (destroyed) return;
      destroyed = true;
      if (rafId) cancelAnimationFrame(rafId);
      window.removeEventListener("pointermove", onPointerMove);
      canvasEl.removeEventListener("click", onCanvasClick);
      disposables.forEach((d) => {
        try {
          d.dispose?.();
        } catch (_) {}
      });
      renderer.dispose();
    },
  };
}
