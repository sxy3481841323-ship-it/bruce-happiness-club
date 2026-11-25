import * as THREE from "three";

function createCanvas(w, h) {
  const c = document.createElement("canvas");
  c.width = w;
  c.height = h;
  return { c, ctx: c.getContext("2d") };
}

function makeFurTextures() {
  const { c, ctx } = createCanvas(256, 256);
  const { c: bumpC, ctx: bumpCtx } = createCanvas(256, 256);

  ctx.fillStyle = "#F6E9C8";
  ctx.fillRect(0, 0, 256, 256);
  bumpCtx.fillStyle = "#808080";
  bumpCtx.fillRect(0, 0, 256, 256);

  for (let i = 0; i < 1800; i += 1) {
    const x = (i * 73) % 256;
    const y = (i * 137) % 256;
    const len = 10 + (i % 14);
    const shade = i % 3 === 0 ? "#FCF5E3" : i % 3 === 1 ? "#E9D1A0" : "#DFBE82";
    ctx.strokeStyle = shade;
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.quadraticCurveTo(x + len * 0.5, y + ((i % 5) - 2), x + len, y + 1);
    ctx.stroke();

    bumpCtx.strokeStyle = i % 2 === 0 ? "#B2B2B2" : "#555555";
    bumpCtx.lineWidth = 1.2;
    bumpCtx.beginPath();
    bumpCtx.moveTo(x, y);
    bumpCtx.lineTo(x + len, y);
    bumpCtx.stroke();
  }

  const map = new THREE.CanvasTexture(c);
  map.colorSpace = THREE.SRGBColorSpace;
  map.wrapS = map.wrapT = THREE.RepeatWrapping;
  map.repeat.set(2, 2);

  const bumpMap = new THREE.CanvasTexture(bumpC);
  bumpMap.wrapS = bumpMap.wrapT = THREE.RepeatWrapping;
  bumpMap.repeat.set(2, 2);
  return { map, bumpMap };
}

function makeTwillTexture() {
  const { c, ctx } = createCanvas(128, 128);
  ctx.fillStyle = "#8C2336";
  ctx.fillRect(0, 0, 128, 128);
  ctx.strokeStyle = "#A93A4E";
  ctx.lineWidth = 3;
  for (let i = -128; i < 256; i += 8) {
    ctx.beginPath();
    ctx.moveTo(i, 0);
    ctx.lineTo(i + 128, 128);
    ctx.stroke();
  }
  const map = new THREE.CanvasTexture(c);
  map.colorSpace = THREE.SRGBColorSpace;
  map.wrapS = map.wrapT = THREE.RepeatWrapping;
  map.repeat.set(3, 3);
  return map;
}

function makeOakChevronTexture() {
  const { c, ctx } = createCanvas(512, 512);
  ctx.fillStyle = "#DFC69E";
  ctx.fillRect(0, 0, 512, 512);
  const tones = ["#E5CEAA", "#D6B78A", "#DFC295", "#CEAB7B"];
  const plankW = 64;
  const plankH = 128;
  for (let col = 0; col < 8; col += 1) {
    for (let row = 0; row < 4; row += 1) {
      const idx = (col * 3 + row * 5) % tones.length;
      ctx.fillStyle = tones[idx];
      const yOff = (col % 2) * 32;
      ctx.fillRect(col * plankW, row * plankH + yOff - 32, plankW - 2, plankH - 2);
      ctx.strokeStyle = "rgba(120, 88, 52, 0.14)";
      ctx.lineWidth = 1;
      for (let g = 8; g < plankW - 6; g += 11) {
        ctx.beginPath();
        ctx.moveTo(col * plankW + g, row * plankH + yOff - 30);
        ctx.lineTo(col * plankW + g + 2, row * plankH + yOff + plankH - 36);
        ctx.stroke();
      }
    }
  }
  const map = new THREE.CanvasTexture(c);
  map.colorSpace = THREE.SRGBColorSpace;
  map.wrapS = map.wrapT = THREE.RepeatWrapping;
  map.repeat.set(4, 4);
  return map;
}

function makeTravertineTexture() {
  const { c, ctx } = createCanvas(256, 256);
  ctx.fillStyle = "#F4EFE6";
  ctx.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 420; i += 1) {
    const x = (i * 59) % 256;
    const y = (i * 97) % 256;
    ctx.fillStyle = i % 2 === 0 ? "rgba(210, 200, 184, 0.35)" : "rgba(255, 255, 255, 0.45)";
    ctx.fillRect(x, y, 12 + (i % 18), 2);
  }
  const map = new THREE.CanvasTexture(c);
  map.colorSpace = THREE.SRGBColorSpace;
  map.wrapS = map.wrapT = THREE.RepeatWrapping;
  map.repeat.set(3, 3);
  return map;
}

function makeLawnTexture() {
  const { c, ctx } = createCanvas(256, 256);
  ctx.fillStyle = "#8EC17E";
  ctx.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 1600; i += 1) {
    const x = (i * 67) % 256;
    const y = (i * 113) % 256;
    ctx.fillStyle = i % 3 === 0 ? "#9ED08E" : i % 3 === 1 ? "#7CB06C" : "#A9D999";
    ctx.fillRect(x, y, 2, 6);
  }
  const map = new THREE.CanvasTexture(c);
  map.colorSpace = THREE.SRGBColorSpace;
  map.wrapS = map.wrapT = THREE.RepeatWrapping;
  map.repeat.set(6, 6);
  return map;
}

export function makeSignTexture(text, bg = "#FFFFFF", fg = "#1D2024", accent = "") {
  const { c, ctx } = createCanvas(512, 160);
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, 512, 160);
  if (accent) {
    ctx.strokeStyle = accent;
    ctx.lineWidth = 10;
    ctx.strokeRect(8, 8, 496, 144);
  }
  ctx.fillStyle = fg;
  ctx.font = "800 54px -apple-system, BlinkMacSystemFont, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(text, 256, 84);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

export function createMaterialLibrary(renderer) {
  // Bake procedural PMREM sunlit studio environment map
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envScene = new THREE.Scene();
  const skyGeo = new THREE.SphereGeometry(20, 24, 16);
  const { c: skyC, ctx: skyCtx } = createCanvas(256, 128);
  const g = skyCtx.createLinearGradient(0, 0, 0, 128);
  g.addColorStop(0, "#CFE7F5");
  g.addColorStop(0.45, "#FFFDF7");
  g.addColorStop(0.65, "#F2E9D8");
  g.addColorStop(1, "#B8C7B4");
  skyCtx.fillStyle = g;
  skyCtx.fillRect(0, 0, 256, 128);
  // Warm studio sun highlight
  skyCtx.fillStyle = "#FFF5DB";
  skyCtx.beginPath();
  skyCtx.arc(190, 36, 22, 0, Math.PI * 2);
  skyCtx.fill();
  const skyTex = new THREE.CanvasTexture(skyC);
  skyTex.colorSpace = THREE.SRGBColorSpace;
  envScene.add(new THREE.Mesh(skyGeo, new THREE.MeshBasicMaterial({ map: skyTex, side: THREE.BackSide })));
  const envRT = pmrem.fromScene(envScene, 0.04);
  pmrem.dispose();

  const fur = makeFurTextures();
  const twill = makeTwillTexture();
  const oak = makeOakChevronTexture();
  const stone = makeTravertineTexture();
  const lawn = makeLawnTexture();

  return {
    envMap: envRT.texture,
    disposeEnv: () => envRT.dispose(),

    furCream: new THREE.MeshStandardMaterial({
      map: fur.map,
      bumpMap: fur.bumpMap,
      bumpScale: 0.015,
      roughness: 0.78,
      metalness: 0.02,
    }),
    furEar: new THREE.MeshStandardMaterial({
      map: fur.map,
      bumpMap: fur.bumpMap,
      bumpScale: 0.02,
      color: new THREE.Color("#E8C88E"),
      roughness: 0.72,
      metalness: 0.02,
    }),
    scarfSilk: new THREE.MeshPhysicalMaterial({
      map: twill,
      roughness: 0.42,
      metalness: 0.05,
      sheen: 0.65,
      sheenRoughness: 0.4,
      sheenColor: new THREE.Color("#D46A7D"),
    }),
    noseWet: new THREE.MeshPhysicalMaterial({
      color: 0x181515,
      roughness: 0.16,
      clearcoat: 1.0,
      clearcoatRoughness: 0.08,
    }),
    eyeGloss: new THREE.MeshPhysicalMaterial({
      color: 0x151110,
      roughness: 0.08,
      clearcoat: 1.0,
      clearcoatRoughness: 0.04,
      envMapIntensity: 1.5,
    }),
    eyeWhite: new THREE.MeshBasicMaterial({ color: 0xffffff }),
    tonguePink: new THREE.MeshStandardMaterial({ color: 0xe67c87, roughness: 0.45 }),
    brass: new THREE.MeshStandardMaterial({ color: 0xd9a84e, roughness: 0.28, metalness: 0.85 }),
    oakFloor: new THREE.MeshStandardMaterial({ map: oak, roughness: 0.62, metalness: 0.04 }),
    travertine: new THREE.MeshStandardMaterial({ map: stone, roughness: 0.76, metalness: 0.02 }),
    cedarDark: new THREE.MeshStandardMaterial({ color: 0x2f3338, roughness: 0.68, metalness: 0.08 }),
    glassClear: new THREE.MeshPhysicalMaterial({
      color: 0xdff2f8,
      transparent: true,
      opacity: 0.34,
      roughness: 0.06,
      metalness: 0.05,
      transmission: 0.55,
      ior: 1.48,
      envMapIntensity: 1.4,
    }),
    waterSurface: new THREE.MeshPhysicalMaterial({
      color: 0x84c7d9,
      roughness: 0.08,
      metalness: 0.05,
      transparent: true,
      opacity: 0.86,
      clearcoat: 0.9,
      envMapIntensity: 1.4,
    }),
    lawnMat: new THREE.MeshStandardMaterial({ map: lawn, roughness: 0.92, metalness: 0 }),
    boucleCream: new THREE.MeshStandardMaterial({ color: 0xf6f1e7, roughness: 0.92, metalness: 0 }),
    blanketRose: new THREE.MeshStandardMaterial({ color: 0xd67c72, roughness: 0.88, metalness: 0 }),
    walnut: new THREE.MeshStandardMaterial({ color: 0x7b5233, roughness: 0.52, metalness: 0.05 }),
    ceramicWhite: new THREE.MeshPhysicalMaterial({ color: 0xfaf8f3, roughness: 0.2, clearcoat: 0.6 }),
  };
}
