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
  ctx.fillStyle = "#DECDB4";
  ctx.fillRect(0, 0, 512, 512);

  // Subtle tile grid, Emperador bronze border inlay & warm travertine veining
  ctx.strokeStyle = "rgba(118, 92, 58, 0.28)";
  ctx.lineWidth = 3;
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
  for (let v = 0; v < 36; v++) {
    ctx.strokeStyle = v % 3 === 0 ? "rgba(148, 114, 72, 0.22)" : "rgba(255, 248, 234, 0.34)";
    ctx.lineWidth = 1.4 + (v % 3) * 0.6;
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
  c.width = 512;
  c.height = 512;
  const ctx = c.getContext("2d");
  const g = ctx.createLinearGradient(0, 0, 512, 512);
  g.addColorStop(0, "#CEBEAA");
  g.addColorStop(0.5, "#C1AE96");
  g.addColorStop(1, "#D4C4AE");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 512, 512);

  // Warm Venetian Marmorino mineral plaster trowel clouds (no stark white!)
  for (let i = 0; i < 1400; i++) {
    const shade = 178 + (i % 28);
    ctx.fillStyle = `rgba(${shade}, ${shade - 12}, ${shade - 26}, 0.22)`;
    ctx.fillRect((i * 37) % 512, (i * 59) % 512, 14 + (i % 9), 7 + (i % 5));
  }
  // Architectural limestone ashlar joint lines & subtle antique-brass hairline reveals
  ctx.strokeStyle = "rgba(110, 88, 64, 0.28)";
  ctx.lineWidth = 2;
  for (let y = 0; y <= 512; y += 128) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(512, y);
    ctx.stroke();
  }
  for (let x = 0; x <= 512; x += 256) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, 512);
    ctx.stroke();
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(2, 2);
  return tex;
}

function makeFoyerRunnerTexture() {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 1024;
  const ctx = c.getContext("2d");
  // Midnight Slate & Champagne-Gold woven runner (distinct palette for Exterior Foyer!)
  ctx.fillStyle = "#242B35";
  ctx.fillRect(0, 0, 512, 1024);
  for (let y = 0; y < 1024; y += 4) {
    const tone = 38 + Math.round(Math.sin(y * 0.045) * 4 + ((y * 7) % 4));
    ctx.fillStyle = `rgba(${tone}, ${tone + 6}, ${tone + 15}, 0.45)`;
    ctx.fillRect(0, y, 512, 2);
  }
  ctx.strokeStyle = "#171A20";
  ctx.lineWidth = 28;
  ctx.strokeRect(18, 18, 476, 988);
  ctx.strokeStyle = "#DFBE7D";
  ctx.lineWidth = 8;
  ctx.strokeRect(42, 42, 428, 940);
  ctx.strokeStyle = "#652C39";
  ctx.lineWidth = 4;
  ctx.strokeRect(56, 56, 400, 912);
  [300, 724].forEach((cy) => {
    ctx.save();
    ctx.translate(256, cy);
    ctx.strokeStyle = "rgba(223, 190, 125, 0.65)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, -110);
    ctx.lineTo(96, 0);
    ctx.lineTo(0, 110);
    ctx.lineTo(-96, 0);
    ctx.closePath();
    ctx.fillStyle = "rgba(223, 190, 125, 0.14)";
    ctx.fill();
    ctx.stroke();
    ctx.strokeStyle = "#DFBE7D";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, -68);
    ctx.lineTo(58, 0);
    ctx.lineTo(0, 68);
    ctx.lineTo(-58, 0);
    ctx.closePath();
    ctx.stroke();
    ctx.restore();
  });
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function makeEtchingArtTexture(seed = 1) {
  const c = document.createElement("canvas");
  c.width = 256;
  c.height = 340;
  const ctx = c.getContext("2d");
  ctx.fillStyle = "#EAE0CE";
  ctx.fillRect(0, 0, 256, 340);
  ctx.strokeStyle = "#3E3228";
  ctx.lineWidth = 3;
  ctx.strokeRect(24, 24, 208, 292);
  ctx.fillStyle = "#D4C4AA";
  ctx.fillRect(34, 34, 188, 272);
  ctx.strokeStyle = "#4A3C31";
  ctx.lineWidth = 2.2;
  ctx.beginPath();
  if (seed === 1) {
    ctx.moveTo(46, 232);
    ctx.lineTo(210, 232);
    ctx.moveTo(124, 92);
    ctx.lineTo(124, 232);
    ctx.lineTo(182, 210);
    ctx.closePath();
  } else {
    ctx.arc(128, 165, 62, 0, Math.PI * 2);
    ctx.moveTo(64, 245);
    ctx.quadraticCurveTo(128, 195, 192, 245);
  }
  ctx.stroke();
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
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
  const runnerTex = trackTex(makeFoyerRunnerTexture());
  const artTex1 = trackTex(makeEtchingArtTexture(1));
  const artTex2 = trackTex(makeEtchingArtTexture(2));
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
    color: 0xd7cbb8,
    roughness: 0.72,
    metalness: 0.04,
  }));
  const matRug = trackMat(new THREE.MeshStandardMaterial({
    map: runnerTex,
    roughness: 0.90,
    metalness: 0.02,
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

  // Fluted walnut architectural wing panels & brass reveals flanking the lift doors (eliminates plain stone)
  [-1, 1].forEach((side) => {
    const px = side * 1.46;
    const wingWalnut = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.62, 2.88, 0.06)), matWalnut);
    wingWalnut.position.set(px, 1.44, 2.74);
    const wingBrass = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.68, 2.94, 0.03)), matBrass);
    wingBrass.position.set(px, 1.44, 2.725);
    const frontWingWalnut = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.62, 2.88, 0.06)), matWalnut);
    frontWingWalnut.position.set(px, 1.44, 2.98);
    scene.add(wingWalnut, wingBrass, frontWingWalnut);
  });

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
  // ARCHITECTURAL SHELL: PALATIAL PENTHOUSE FOYER (z = 0 .. 2.80, x = +-3.45, h = 4.10)
  // =========================================================================
  const matPietra = trackMat(new THREE.MeshStandardMaterial({
    color: 0x454950,
    roughness: 0.20,
    metalness: 0.12,
  }));
  const matTravertine = trackMat(new THREE.MeshStandardMaterial({
    color: 0xd5d2ca,
    roughness: 0.42,
    metalness: 0.04,
  }));
  const matObsidian = trackMat(new THREE.MeshStandardMaterial({
    color: 0x13161b,
    roughness: 0.16,
    metalness: 0.65,
  }));
  const sconceGlassMat = trackMat(new THREE.MeshBasicMaterial({ color: 0xffefc9 }));

  [-1, 1].forEach((side) => {
    const wx = side * 3.45;
    const upperWall = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.18, 4.10, 3.1)), matStoneWall);
    upperWall.position.set(wx, 2.05, 1.38);
    upperWall.receiveShadow = true;
    scene.add(upperWall);

    const wainscot = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.08, 1.30, 2.9)), matPietra);
    wainscot.position.set(wx - side * 0.10, 0.65, 1.38);
    const chairRail = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.10, 0.05, 2.92)), matBrass);
    chairRail.position.set(wx - side * 0.10, 1.32, 1.38);
    const baseSkirt = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.10, 0.14, 2.92)), matBronze);
    baseSkirt.position.set(wx - side * 0.10, 0.07, 1.38);

    [0.42, 2.34].forEach((pz) => {
      const pilaster = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.10, 4.00, 0.30)), matTravertine);
      pilaster.position.set(wx - side * 0.10, 2.00, pz);
      const brassBead = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.11, 4.00, 0.03)), matBrass);
      brassBead.position.set(wx - side * 0.10, 2.00, pz);
      scene.add(pilaster, brassBead);
    });
    const boiserieFrame = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.05, 1.90, 1.44)), matBronze);
    boiserieFrame.position.set(wx - side * 0.10, 2.40, 1.38);
    const artPlate = new THREE.Mesh(
      trackGeo(new THREE.BoxGeometry(0.06, 1.54, 1.12)),
      trackMat(new THREE.MeshStandardMaterial({ map: side < 0 ? artTex1 : artTex2, roughness: 0.42 })),
    );
    artPlate.position.set(wx - side * 0.11, 2.40, 1.38);
    scene.add(wainscot, chairRail, baseSkirt, boiserieFrame, artPlate);
  });

  // Back portal wall framing monumental 2.96m x 3.45m mansion double doorway
  const backWallL = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(2.1, 4.10, 0.30)), matStoneWall);
  backWallL.position.set(-2.55, 2.05, 0.0);
  backWallL.receiveShadow = true;
  const backWallR = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(2.1, 4.10, 0.30)), matStoneWall);
  backWallR.position.set(2.55, 2.05, 0.0);
  backWallR.receiveShadow = true;
  const backWallTop = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(3.2, 0.65, 0.30)), matStoneWall);
  backWallTop.position.set(0, 3.78, 0.0);
  scene.add(backWallL, backWallR, backWallTop);

  [-1, 1].forEach((side) => {
    const panelX = side * 2.45;
    const travPanel = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(1.56, 3.92, 0.08)), matTravertine);
    travPanel.position.set(panelX, 1.96, 0.15);
    const innerPietra = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(1.18, 3.30, 0.06)), matPietra);
    innerPietra.position.set(panelX, 1.92, 0.17);
    const brassTrim = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(1.24, 3.36, 0.04)), matBrass);
    brassTrim.position.set(panelX, 1.92, 0.165);
    scene.add(travPanel, innerPietra, brassTrim);

    // Sculpted bronze/alabaster wall sconce columns flanking double doors
    const sx = side * 1.76;
    const backplate = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.14, 0.92, 0.04)), matBrass);
    backplate.position.set(sx, 2.18, 0.18);
    const shade = new THREE.Mesh(trackGeo(new THREE.CylinderGeometry(0.065, 0.055, 0.72, 18)), sconceGlassMat);
    shade.position.set(sx, 2.18, 0.24);
    scene.add(backplate, shade);
  });

  // Obsidian Entry Smart Terminal beside right door jamb (echoes interior Smart Home Panel!)
  const extSmartFrame = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.36, 0.48, 0.04)), matBrass);
  extSmartFrame.position.set(1.76, 1.38, 0.19);
  const extSmartGlass = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.32, 0.44, 0.045)), matObsidian);
  extSmartGlass.position.set(1.76, 1.38, 0.20);
  const extSmartGlow = new THREE.Mesh(
    trackGeo(new THREE.PlaneGeometry(0.24, 0.12)),
    trackMat(new THREE.MeshBasicMaterial({ color: 0x7fd8ff })),
  );
  extSmartGlow.position.set(1.76, 1.44, 0.226);
  scene.add(extSmartFrame, extSmartGlass, extSmartGlow);

  // Symmetrical Sculpted Silver-Travertine & Pietra-Grey Consoles (left & right foyer!)
  [-1, 1].forEach((side) => {
    const cg = new THREE.Group();
    cg.position.set(side * 2.48, 0, 1.05);
    const plinthL = new THREE.Mesh(trackGeo(new THREE.CylinderGeometry(0.14, 0.18, 0.86, 20)), matTravertine);
    plinthL.position.set(0, 0.43, -0.36);
    const plinthR = new THREE.Mesh(trackGeo(new THREE.CylinderGeometry(0.14, 0.18, 0.86, 20)), matTravertine);
    plinthR.position.set(0, 0.43, 0.36);
    const topSlab = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.62, 0.09, 1.38)), matPietra);
    topSlab.position.set(0, 0.90, 0);
    topSlab.castShadow = true;
    const brassBand = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.64, 0.025, 1.40)), matBrass);
    brassBand.position.set(0, 0.855, 0);
    // Warm alabaster console lamp on rear end
    const lampBase = new THREE.Mesh(trackGeo(new THREE.CylinderGeometry(0.09, 0.12, 0.28, 18)), matBrass);
    lampBase.position.set(0, 1.08, -0.44);
    const lampShade = new THREE.Mesh(trackGeo(new THREE.CylinderGeometry(0.14, 0.16, 0.24, 20)), sconceGlassMat);
    lampShade.position.set(0, 1.32, -0.44);
    cg.add(plinthL, plinthR, topSlab, brassBand, lampBase, lampShade);

    if (side < 0) {
      // Left console: sculptural porcelain vessel + blooming orchid sprays + bronze valet dish
      const vase = new THREE.Mesh(
        trackGeo(new THREE.CylinderGeometry(0.11, 0.15, 0.36, 20)),
        trackMat(new THREE.MeshStandardMaterial({ color: 0xf4efe6, roughness: 0.28 })),
      );
      vase.position.set(0, 1.12, 0.16);
      const orchidMat = trackMat(new THREE.MeshStandardMaterial({ color: 0xfbf9f4, roughness: 0.4 }));
      for (let k = 0; k < 5; k++) {
        const bl = new THREE.Mesh(trackGeo(new THREE.SphereGeometry(0.055, 10, 8)), orchidMat);
        bl.scale.set(1.0, 0.55, 1.0);
        bl.position.set((k % 2 ? 0.04 : -0.04), 1.42 + k * 0.05, 0.16 + (k - 2) * 0.04);
        cg.add(bl);
      }
      cg.add(vase);
    } else {
      // Right console: champagne-gold sculptural torus centerpiece + travertine art block
      const sculp = new THREE.Mesh(trackGeo(new THREE.TorusGeometry(0.16, 0.038, 14, 32)), matBrass);
      sculp.position.set(0, 1.16, 0.14);
      sculp.rotation.y = Math.PI * 0.35;
      const artPed = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.22, 0.07, 0.22)), matTravertine);
      artPed.position.set(0, 0.98, 0.14);
      cg.add(sculp, artPed);
    }
    scene.add(cg);
  });

  // Woven Midnight-Slate Runner Carpet leading up to the double door threshold
  const runnerMesh = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(2.16, 0.016, 2.35)), matRug);
  runnerMesh.position.set(0, 0.008, 1.40);
  runnerMesh.receiveShadow = true;
  const runnerBorder = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(2.24, 0.01, 2.42)), matBrass);
  runnerBorder.position.set(0, 0.005, 1.40);
  scene.add(runnerBorder, runnerMesh);

  // =========================================================================
  // PALATIAL 2.88m x 3.45m CAST-BRONZE & PIETRA-GREY DOUBLE ENTRANCE DOORS
  // =========================================================================
  const jambL = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.22, 3.48, 0.38)), matBronze);
  jambL.position.set(-1.55, 1.74, 0.04);
  const jambR = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(0.22, 3.48, 0.38)), matBronze);
  jambR.position.set(1.55, 1.74, 0.04);
  const jambTop = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(3.34, 0.24, 0.42)), matBronze);
  jambTop.position.set(0, 3.52, 0.04);
  const threshold = new THREE.Mesh(trackGeo(new THREE.BoxGeometry(3.04, 0.028, 0.36)), matBrass);
  threshold.position.set(0, 0.014, 0.04);
  scene.add(jambL, jambR, jambTop, threshold);

  // Overhead Illuminated Champagne-Gold Crest Transom
  const nameplateMesh = new THREE.Mesh(
    trackGeo(new THREE.BoxGeometry(1.36, 0.30, 0.04)),
    [
      matBrass, matBrass, matBrass, matBrass,
      trackMat(new THREE.MeshStandardMaterial({ map: plateTex, roughness: 0.25, metalness: 0.85 })),
      matBrass,
    ],
  );
  nameplateMesh.position.set(0, 3.22, 0.20);
  scene.add(nameplateMesh);

  // Twin Hinged Leaves pivoting outward/inward smoothly (-1.44 & +1.44)
  const doorHingeGroup = new THREE.Group();
  doorHingeGroup.position.set(-1.44, 0, 0.02);
  scene.add(doorHingeGroup);

  const doorHingeGroupR = new THREE.Group();
  doorHingeGroupR.position.set(1.44, 0, 0.02);
  scene.add(doorHingeGroupR);

  const doorBodyL = new THREE.Group();
  doorBodyL.position.set(0.72, 0, 0);
  doorHingeGroup.add(doorBodyL);

  const doorBodyR = new THREE.Group();
  doorBodyR.position.set(-0.72, 0, 0);
  doorHingeGroupR.add(doorBodyR);

  const leafGeo = trackGeo(new THREE.BoxGeometry(1.42, 3.04, 0.12));
  const cofferOuterGeo = trackGeo(new THREE.BoxGeometry(0.96, 1.24, 0.032));
  const cofferInnerGeo = trackGeo(new THREE.BoxGeometry(0.88, 1.16, 0.045));
  const barPullGeo = trackGeo(new THREE.CylinderGeometry(0.024, 0.024, 1.38, 14));

  const doorSlab = new THREE.Mesh(leafGeo, matBronze);
  doorSlab.position.set(0, 1.54, 0);
  doorSlab.castShadow = true;
  doorBodyL.add(doorSlab);

  const doorSlabR = new THREE.Mesh(leafGeo, matBronze);
  doorSlabR.position.set(0, 1.54, 0);
  doorSlabR.castShadow = true;
  doorBodyR.add(doorSlabR);

  [doorBodyL, doorBodyR].forEach((body, idx) => {
    [2.28, 0.88].forEach((cy) => {
      const outer = new THREE.Mesh(cofferOuterGeo, matBrass);
      outer.position.set(0, cy, 0.06);
      const inner = new THREE.Mesh(cofferInnerGeo, matPietra);
      inner.position.set(0, cy, 0.068);
      body.add(outer, inner);
    });
    const pullX = idx === 0 ? 0.56 : -0.56;
    const pull = new THREE.Mesh(barPullGeo, matBrass);
    pull.position.set(pullX, 1.42, 0.12);
    body.add(pull);
  });

  const handlePivot = new THREE.Group();
  handlePivot.position.set(0.56, 1.42, 0.12);
  doorBodyL.add(handlePivot);

  // Warm sunlight portal chamber BEHIND the double doors
  const portalBackMat = trackMat(new THREE.MeshBasicMaterial({ color: 0xfff3d4 }));
  const portalChamber = new THREE.Mesh(trackGeo(new THREE.PlaneGeometry(5.8, 4.6)), portalBackMat);
  portalChamber.position.set(0, 1.9, -1.35);
  scene.add(portalChamber);

  const seamMat = trackMat(new THREE.MeshBasicMaterial({
    color: 0xffdf94,
    transparent: true,
    opacity: 0.92,
  }));
  const underDoorGlow = new THREE.Mesh(trackGeo(new THREE.PlaneGeometry(2.86, 0.18)), seamMat);
  underDoorGlow.rotation.x = -Math.PI / 2;
  underDoorGlow.position.set(0, 0.026, 0.14);
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
  const doorHitTargets = [doorSlab, doorSlabR, handlePivot];

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
      baseCamPos.set(0, 1.62, 3.85);
      baseLookAt.set(0, 1.56, 0.0);
      seamMat.opacity = 0.78 + Math.sin(now * 0.0032) * 0.16;
    } else if (phase === "unlocking") {
      const pHandle = Math.min(1, dtPhase / 0.18);
      handlePivot.rotation.z = THREE.MathUtils.lerp(0, -0.48, easeOutCubic(pHandle));

      const pSwing = Math.min(1, Math.max(0, (dtPhase - 0.08) / 0.76));
      const eSwing = easeInOutQuart(pSwing);
      doorHingeGroup.rotation.y = THREE.MathUtils.lerp(0, -1.16, eSwing);
      doorHingeGroupR.rotation.y = THREE.MathUtils.lerp(0, 1.16, eSwing);
      baseCamPos.set(0, 1.62, THREE.MathUtils.lerp(3.85, 0.95, eSwing));
      baseLookAt.set(0, 1.56, -1.2);
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
