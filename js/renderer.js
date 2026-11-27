// High-DPI Living Canvas Renderer for Bruce Happiness Club
// Fresh sunlit contemporary gallery palette · Modern standalone villa + lush avenue · Zero place-name text

export function fitCanvas(canvas) {
  const rect = canvas.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const w = Math.max(300, Math.round(rect.width));
  const h = Math.max(240, Math.round(rect.height));
  if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
  }
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { w, h, ctx };
}

function roundRect(ctx, x, y, w, h, r) {
  const rr = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + rr, y);
  ctx.arcTo(x + w, y, x + w, y + h, rr);
  ctx.arcTo(x + w, y + h, x, y + h, rr);
  ctx.arcTo(x, y + h, x, y, rr);
  ctx.arcTo(x, y, x + w, y, rr);
  ctx.closePath();
}

/**
 * Draw articulated Candidate-01 Cream Long-haired Dachshund ("Bruce")
 */
export function drawBruce(ctx, opts = {}) {
  const {
    x = 200,
    y = 200,
    scale = 1,
    facing = 1, // 1 right, -1 left
    mood = "happy", // happy | excited | warn | sulk | phone | sleep | belly
    t = 0,
    walkSpeed = 0,
    lookTarget = null,
    wetPaws = false,
    blanketOn = false,
    brushGlow = 0,
  } = opts;

  ctx.save();
  ctx.translate(x, y);
  ctx.scale(facing * scale, scale);

  const breath = Math.sin(t * (mood === "excited" ? 5 : 2.6)) * 1.4;
  const stride = walkSpeed > 0.05 ? Math.sin(t * 14) * Math.min(1, walkSpeed) : 0;
  const tailSpeed = mood === "sulk" || mood === "warn" ? 1.2 : mood === "excited" ? 13 : 6.8;
  const tailSwing = (mood === "sulk" ? 0.08 : 0.34) * Math.sin(t * tailSpeed);

  // Soft ambient ground shadow
  ctx.fillStyle = "rgba(35, 38, 44, 0.14)";
  ctx.beginPath();
  ctx.ellipse(0, 34, 48, 11, 0, 0, Math.PI * 2);
  ctx.fill();

  if (brushGlow > 0) {
    const grad = ctx.createRadialGradient(0, -4, 10, 0, -4, 68);
    grad.addColorStop(0, `rgba(246, 200, 110, ${0.35 * brushGlow})`);
    grad.addColorStop(1, "rgba(246, 200, 110, 0)");
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(0, -4, 68, 0, Math.PI * 2);
    ctx.fill();
  }

  // Curled croissant sleep pose
  if (mood === "sleep") {
    ctx.fillStyle = "#F7E9C8";
    ctx.strokeStyle = "#2A2421";
    ctx.lineWidth = 2.2;
    ctx.beginPath();
    ctx.ellipse(0, 14 + breath * 0.5, 42, 24, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Feathered tail curled around
    ctx.fillStyle = "#EED5A4";
    ctx.beginPath();
    ctx.ellipse(-28, 18, 18, 10, -0.35, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Head resting on paws
    ctx.fillStyle = "#FAF0D6";
    ctx.beginPath();
    ctx.ellipse(24, 8 + breath * 0.4, 21, 16, 0.12, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Burgundy scarf peeking
    ctx.fillStyle = "#8C2638";
    ctx.beginPath();
    ctx.ellipse(12, 16, 10, 5, 0.5, 0, Math.PI * 2);
    ctx.fill();

    // Floppy cream ear
    ctx.fillStyle = "#E4C185";
    ctx.beginPath();
    ctx.ellipse(18, 12, 10, 14, 0.25, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Closed peaceful eye + nose
    ctx.beginPath();
    ctx.arc(31, 6, 4.5, 0.15, Math.PI - 0.15);
    ctx.stroke();
    ctx.fillStyle = "#231E1C";
    ctx.beginPath();
    ctx.ellipse(44, 10, 4.2, 3.2, 0, 0, Math.PI * 2);
    ctx.fill();

    // Floating Zzz
    ctx.fillStyle = "rgba(42, 36, 33, 0.55)";
    ctx.font = "600 13px -apple-system, sans-serif";
    const zy = -14 - ((t * 14) % 18);
    ctx.fillText("z", 34, zy);
    ctx.font = "600 16px -apple-system, sans-serif";
    ctx.fillText("Z", 44, zy - 9);
    ctx.restore();
    return;
  }

  // Belly-up happy pose
  if (mood === "belly") {
    ctx.fillStyle = "#FAF0D6";
    ctx.strokeStyle = "#2A2421";
    ctx.lineWidth = 2.2;
    ctx.beginPath();
    ctx.ellipse(0, 12 + breath * 0.4, 46, 21, -0.05, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Pink soft belly patch
    ctx.fillStyle = "#F7D9CD";
    ctx.beginPath();
    ctx.ellipse(-4, 9, 26, 11, 0, 0, Math.PI * 2);
    ctx.fill();

    // Four tucked paws waving gently
    const pawWave = Math.sin(t * 7) * 3;
    [[-22, -6 + pawWave], [-8, -8 - pawWave], [16, -7 + pawWave], [26, -5 - pawWave]].forEach(([px, py]) => {
      ctx.fillStyle = "#F5E4BE";
      ctx.beginPath();
      ctx.ellipse(px, py, 6, 9, 0.2, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    });

    // Happy head tilted back
    ctx.fillStyle = "#FAF0D6";
    ctx.beginPath();
    ctx.ellipse(35, 4, 18, 16, -0.25, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Scarf
    ctx.fillStyle = "#8C2638";
    ctx.beginPath();
    ctx.ellipse(23, 12, 8, 12, 0.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Happy curved eyes
    ctx.beginPath();
    ctx.arc(36, 1, 3.6, Math.PI + 0.2, -0.2);
    ctx.stroke();
    ctx.fillStyle = "#231E1C";
    ctx.beginPath();
    ctx.ellipse(48, -2, 4, 3, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    return;
  }

  // Standard standing / sitting / trotting / sulking body
  const crouch = mood === "sulk" ? 7 : mood === "warn" ? 3 : 0;

  // Feathered long cream tail
  ctx.save();
  ctx.translate(-37, 4 + crouch + breath * 0.4);
  ctx.rotate((mood === "sulk" ? 0.55 : -0.42) + tailSwing);
  ctx.fillStyle = "#F3DFB4";
  ctx.strokeStyle = "#2A2421";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.quadraticCurveTo(-24, -18, -32, -8);
  ctx.quadraticCurveTo(-22, 6, 0, 5);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  ctx.restore();

  // Back legs
  const legSwing1 = stride * 7;
  const legSwing2 = -stride * 7;
  const drawLeg = (lx, ly, swing, dark = false) => {
    ctx.save();
    ctx.translate(lx + swing, ly);
    ctx.fillStyle = dark ? "#E6CCA0" : "#F8E9C6";
    ctx.strokeStyle = "#2A2421";
    ctx.lineWidth = 2;
    roundRect(ctx, -6, 0, 12, 22 - crouch * 0.5, 6);
    ctx.fill();
    ctx.stroke();
    ctx.beginPath();
    ctx.ellipse(2, 21 - crouch * 0.5, 7, 4, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  };

  drawLeg(-22, 13 + crouch, legSwing2, true);
  drawLeg(18, 13 + crouch, legSwing1, true);

  // Elongated dachshund torso (cream long-haired coat)
  const bodyGrad = ctx.createLinearGradient(-40, -14, 30, 22);
  bodyGrad.addColorStop(0, "#FBF2DB");
  bodyGrad.addColorStop(0.65, "#F5E2B8");
  bodyGrad.addColorStop(1, "#E7C992");

  ctx.fillStyle = bodyGrad;
  ctx.strokeStyle = "#2A2421";
  ctx.lineWidth = 2.2;
  ctx.beginPath();
  ctx.ellipse(-4, 5 + crouch + breath * 0.5, 39, 18, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();

  // Feathery chest & belly fur tuft
  ctx.strokeStyle = "rgba(42, 36, 33, 0.35)";
  ctx.lineWidth = 1.4;
  for (let i = -24; i <= 18; i += 10) {
    ctx.beginPath();
    ctx.moveTo(i, 19 + crouch);
    ctx.quadraticCurveTo(i - 3, 25 + crouch, i - 6, 22 + crouch);
    ctx.stroke();
  }

  // Optional cozy knit blanket draped over torso
  if (blanketOn) {
    ctx.fillStyle = "#D98074";
    ctx.strokeStyle = "#2A2421";
    ctx.lineWidth = 1.8;
    roundRect(ctx, -33, -12 + crouch + breath * 0.4, 48, 25, 10);
    ctx.fill();
    ctx.stroke();
    ctx.strokeStyle = "rgba(255,255,255,0.45)";
    ctx.beginPath();
    ctx.moveTo(-27, -2 + crouch);
    ctx.lineTo(9, -2 + crouch);
    ctx.stroke();
  }

  // Front legs
  drawLeg(-28, 14 + crouch, legSwing1, false);
  drawLeg(12, 14 + crouch, legSwing2, false);

  // Wet paw droplets if wetPaws
  if (wetPaws) {
    ctx.fillStyle = "#5B9BD5";
    [[-26, 35], [-16, 36], [14, 35], [24, 36]].forEach(([dx, dy]) => {
      ctx.beginPath();
      ctx.arc(dx, dy, 2.8, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  // Signature Burgundy Twill Silk Neckerchief (crooked when sulking!)
  ctx.save();
  ctx.translate(23, 2 + crouch + breath * 0.4);
  ctx.rotate(mood === "sulk" ? 0.38 : 0.08);
  ctx.fillStyle = "#8B2436";
  ctx.strokeStyle = "#2A2421";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(-11, -11);
  ctx.quadraticCurveTo(6, -12, 14, -4);
  ctx.lineTo(18, 10);
  ctx.lineTo(2, 14);
  ctx.lineTo(-10, 4);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  // Scarf knot & tail
  ctx.fillStyle = "#A8354A";
  ctx.beginPath();
  ctx.ellipse(12, 4, 5, 4, 0.3, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.restore();

  // Head + Muzzle
  ctx.save();
  const headTilt = mood === "sulk" ? 0.16 : mood === "excited" ? -0.1 : mood === "warn" ? -0.06 : 0;
  ctx.translate(31, -14 + crouch * 1.1 + breath * 0.5);
  ctx.rotate(headTilt);

  ctx.fillStyle = "#FBF1D9";
  ctx.strokeStyle = "#2A2421";
  ctx.lineWidth = 2.2;

  // Cranium + long sleek dachshund snout
  ctx.beginPath();
  ctx.moveTo(-16, -6);
  ctx.quadraticCurveTo(-14, -23, 6, -21);
  ctx.quadraticCurveTo(18, -19, 22, -7);
  ctx.quadraticCurveTo(38, -5, 38, 4);
  ctx.quadraticCurveTo(37, 13, 18, 13);
  ctx.quadraticCurveTo(2, 16, -12, 9);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  // Glossy black nose
  ctx.fillStyle = "#1E1B1A";
  ctx.beginPath();
  ctx.ellipse(36, 1, 5.2, 3.8, -0.1, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "rgba(255,255,255,0.65)";
  ctx.beginPath();
  ctx.arc(35, -0.4, 1.3, 0, Math.PI * 2);
  ctx.fill();

  // Mouth / tongue
  ctx.strokeStyle = "#2A2421";
  ctx.lineWidth = 1.7;
  ctx.beginPath();
  if (mood === "sulk" || mood === "warn") {
    ctx.moveTo(22, 8);
    ctx.quadraticCurveTo(27, 6, 32, 9);
  } else {
    ctx.moveTo(20, 6);
    ctx.quadraticCurveTo(26, 11, 32, 7);
  }
  ctx.stroke();
  if (mood === "excited") {
    ctx.fillStyle = "#EC7B85";
    ctx.beginPath();
    ctx.ellipse(27, 11, 3.5, 5, 0.2, 0, Math.PI * 2);
    ctx.fill();
  }

  // Eye tracking lookTarget
  let eyeDx = 0;
  let eyeDy = 0;
  if (lookTarget) {
    const dx = (lookTarget.x - x) * facing;
    const dy = lookTarget.y - y;
    const mag = Math.hypot(dx, dy) || 1;
    eyeDx = Math.max(-1.8, Math.min(1.8, (dx / mag) * 1.8));
    eyeDy = Math.max(-1.5, Math.min(1.5, (dy / mag) * 1.5));
  }
  const blink = (t * 0.9) % 4.3 > 4.18;
  ctx.fillStyle = "#1E1A18";
  if (blink) {
    ctx.beginPath();
    ctx.moveTo(9, -6);
    ctx.lineTo(16, -6);
    ctx.stroke();
  } else if (mood === "sulk") {
    ctx.beginPath();
    ctx.arc(12.5, -5, 4.2, 0, Math.PI);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(7, -8);
    ctx.lineTo(18, -5);
    ctx.stroke();
  } else {
    ctx.beginPath();
    ctx.ellipse(12.5 + eyeDx * 0.4, -6 + eyeDy * 0.4, 4.4, 4.8, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#FFFFFF";
    ctx.beginPath();
    ctx.arc(13.8 + eyeDx * 0.6, -7.6 + eyeDy * 0.6, 1.5, 0, Math.PI * 2);
    ctx.fill();
  }

  // Expressive brow for phone glare or warning
  if (mood === "phone" || mood === "warn") {
    ctx.strokeStyle = "#2A2421";
    ctx.lineWidth = 2.2;
    ctx.beginPath();
    ctx.moveTo(6, -13);
    ctx.lineTo(17, -10);
    ctx.stroke();
  }

  // Silky feathered long dachshund ear (flattens back on warn/sulk!)
  ctx.save();
  ctx.translate(-5, -12);
  ctx.rotate(mood === "warn" ? 0.58 : mood === "sulk" ? 0.18 : mood === "excited" ? -0.18 : 0);
  const earGrad = ctx.createLinearGradient(-8, 0, 8, 32);
  earGrad.addColorStop(0, "#EBD09B");
  earGrad.addColorStop(1, "#D5AC6B");
  ctx.fillStyle = earGrad;
  ctx.strokeStyle = "#2A2421";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(-4, -2);
  ctx.bezierCurveTo(-17, 6, -18, 28, -6, 31);
  ctx.bezierCurveTo(6, 32, 9, 14, 4, -1);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();
  ctx.restore();

  ctx.restore();
  ctx.restore();
}

/**
 * Natural catenary woven leather leash between owner's hand and Bruce's collar
 */
export function drawLeash(ctx, x1, y1, x2, y2) {
  ctx.save();
  const midX = (x1 + x2) / 2;
  const dist = Math.hypot(x2 - x1, y2 - y1);
  const sag = Math.max(12, Math.min(48, 56 - dist * 0.18));
  const midY = Math.max(y1, y2) + sag;

  ctx.strokeStyle = "#6E1C2B";
  ctx.lineWidth = 4;
  ctx.lineCap = "round";
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.quadraticCurveTo(midX, midY, x2, y2);
  ctx.stroke();

  ctx.strokeStyle = "#B34658";
  ctx.lineWidth = 1.4;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.quadraticCurveTo(midX, midY, x2, y2);
  ctx.stroke();

  // Brass clip at collar
  ctx.setLineDash([]);
  ctx.fillStyle = "#D4A44C";
  ctx.beginPath();
  ctx.arc(x2, y2, 3.6, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

/**
 * Full-bleed Living Illustrated World Canvas (ZERO place-name text anywhere)
 */
export const WORLD_HOTSPOTS = [
  { id: "home", label: "阳光顶层公寓", shortLabel: "公寓", x: 0.53, y: 0.68, playable: true },
  { id: "street", label: "海岸烘焙室", shortLabel: "烘焙", x: 0.34, y: 0.64, playable: true },
  { id: "park", label: "树影公园", shortLabel: "公园", x: 0.19, y: 0.48, playable: false },
  { id: "warehouse", label: "ELOWEN 市集", shortLabel: "市集", x: 0.76, y: 0.48, playable: true },
  { id: "yacht", label: "白帆游艇码头", shortLabel: "游艇", x: 0.80, y: 0.77, playable: false },
  { id: "nordic", label: "远方航线 · 北", shortLabel: "航线1", x: 0.17, y: 0.19, playable: false },
  { id: "california", label: "远方航线 · 西", shortLabel: "航线2", x: 0.46, y: 0.16, playable: false },
  { id: "nz_swiss", label: "远方航线 · 南/峰", shortLabel: "航线3", x: 0.79, y: 0.19, playable: false },
];

export function drawWorldAtlas(ctx, w, h, t, sulking = false) {
  // Fresh daylight gallery sky & ground gradient
  const skyGrad = ctx.createLinearGradient(0, 0, 0, h);
  if (sulking) {
    skyGrad.addColorStop(0, "#DDE6EE");
    skyGrad.addColorStop(0.38, "#EAEFF4");
    skyGrad.addColorStop(1, "#EEF2F0");
  } else {
    skyGrad.addColorStop(0, "#EBF4F8");
    skyGrad.addColorStop(0.32, "#F9F7F0");
    skyGrad.addColorStop(1, "#F3F0E6");
  }
  ctx.fillStyle = skyGrad;
  ctx.fillRect(0, 0, w, h);

  // Soft sunlit hills / watercolor washes
  ctx.fillStyle = sulking ? "rgba(182, 204, 214, 0.35)" : "rgba(196, 224, 206, 0.36)";
  ctx.beginPath();
  ctx.ellipse(w * 0.2, h * 0.52, w * 0.26, h * 0.2, -0.1, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = sulking ? "rgba(195, 205, 214, 0.32)" : "rgba(244, 232, 205, 0.45)";
  ctx.beginPath();
  ctx.ellipse(w * 0.54, h * 0.69, w * 0.34, h * 0.22, 0.05, 0, Math.PI * 2);
  ctx.fill();

  // Gentle clouds drifting
  const drawCloud = (cx, cy, cw) => {
    const shift = ((t * 7) % (w + 180)) - 90;
    const xPos = (cx + shift * 0.35) % (w + 120) - 60;
    ctx.fillStyle = "rgba(255, 255, 255, 0.72)";
    ctx.beginPath();
    ctx.ellipse(xPos, cy, cw, cw * 0.42, 0, 0, Math.PI * 2);
    ctx.ellipse(xPos - cw * 0.45, cy + 4, cw * 0.55, cw * 0.32, 0, 0, Math.PI * 2);
    ctx.ellipse(xPos + cw * 0.45, cy + 4, cw * 0.55, cw * 0.32, 0, 0, Math.PI * 2);
    ctx.fill();
  };
  drawCloud(w * 0.15, h * 0.1, 38);
  drawCloud(w * 0.62, h * 0.08, 46);

  // Upper dashed flight arcs & tiny moving plane
  ctx.save();
  ctx.strokeStyle = "rgba(42, 48, 54, 0.28)";
  ctx.lineWidth = 1.6;
  ctx.setLineDash([5, 6]);
  ctx.beginPath();
  ctx.moveTo(w * 0.17, h * 0.22);
  ctx.quadraticCurveTo(w * 0.32, h * 0.06, w * 0.46, h * 0.19);
  ctx.quadraticCurveTo(w * 0.63, h * 0.05, w * 0.80, h * 0.21);
  ctx.stroke();
  ctx.restore();

  // Tiny animated airplane along upper arc
  const pFrac = (t * 0.045) % 1;
  const px = w * (0.17 + 0.63 * pFrac);
  const py = h * (0.18 - Math.sin(pFrac * Math.PI) * 0.09);
  ctx.save();
  ctx.translate(px, py);
  ctx.fillStyle = "#2E343B";
  ctx.beginPath();
  ctx.moveTo(8, 0);
  ctx.lineTo(-6, -4);
  ctx.lineTo(-3, 0);
  ctx.lineTo(-6, 4);
  ctx.closePath();
  ctx.fill();
  ctx.restore();

  // ---- 4 Distant Travel Vignettes (ZERO text) ----
  // 1. Nordic fjord cottages (top-left)
  ctx.save();
  ctx.translate(w * 0.17, h * 0.22);
  ctx.fillStyle = "#BBD8E6";
  ctx.beginPath();
  ctx.ellipse(0, 12, w * 0.075, 18, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#7D9AA6";
  ctx.beginPath();
  ctx.moveTo(-48, 4); ctx.lineTo(-22, -26); ctx.lineTo(8, 4); ctx.closePath(); ctx.fill();
  ctx.fillStyle = "#C95248";
  roundRect(ctx, -18, -8, 22, 18, 2); ctx.fill();
  ctx.fillStyle = "#E5AE4E";
  roundRect(ctx, 8, -4, 18, 14, 2); ctx.fill();
  ctx.restore();

  // 2. California sunset palm coast + red suspension bridge (top-mid)
  ctx.save();
  ctx.translate(w * 0.46, h * 0.2);
  const sunG = ctx.createRadialGradient(0, -4, 4, 0, -4, 46);
  sunG.addColorStop(0, "#FFE0B2");
  sunG.addColorStop(1, "rgba(255, 224, 178, 0)");
  ctx.fillStyle = sunG;
  ctx.beginPath(); ctx.arc(0, -4, 46, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = "#C84B31"; ctx.lineWidth = 2.4;
  ctx.beginPath();
  ctx.moveTo(-38, 12); ctx.lineTo(38, 12);
  ctx.moveTo(-18, 12); ctx.lineTo(-18, -14);
  ctx.moveTo(18, 12); ctx.lineTo(18, -14);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-38, 12); ctx.quadraticCurveTo(-18, -14, 0, 8); ctx.quadraticCurveTo(18, -14, 38, 12);
  ctx.stroke();
  // Palm tree
  ctx.strokeStyle = "#5D4B3B"; ctx.lineWidth = 2.5;
  ctx.beginPath(); ctx.moveTo(-44, 16); ctx.quadraticCurveTo(-48, -2, -40, -18); ctx.stroke();
  ctx.strokeStyle = "#4A7C59"; ctx.lineWidth = 2;
  [[-12, -4], [12, -2], [-8, -12], [10, -10]].forEach(([dx, dy]) => {
    ctx.beginPath(); ctx.moveTo(-40, -18); ctx.quadraticCurveTo(-40 + dx * 0.6, -24, -40 + dx, -18 + dy); ctx.stroke();
  });
  ctx.restore();

  // 3. NZ emerald hills + Swiss snow-capped peak + red alpine train (top-right)
  ctx.save();
  ctx.translate(w * 0.79, h * 0.22);
  ctx.fillStyle = "#9CCB8B";
  ctx.beginPath(); ctx.ellipse(-28, 12, 34, 15, 0, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = "#FFFFFF";
  [[-36, 9], [-24, 12], [-18, 7]].forEach(([sx, sy]) => {
    ctx.beginPath(); ctx.arc(sx, sy, 3.2, 0, Math.PI * 2); ctx.fill();
  });
  // Swiss peak
  ctx.fillStyle = "#CFDCE4";
  ctx.beginPath(); ctx.moveTo(0, 16); ctx.lineTo(28, -28); ctx.lineTo(54, 16); ctx.closePath(); ctx.fill();
  ctx.fillStyle = "#FFFFFF";
  ctx.beginPath(); ctx.moveTo(28, -28); ctx.lineTo(18, -12); ctx.lineTo(26, -9); ctx.lineTo(36, -13); ctx.closePath(); ctx.fill();
  // Tiny red train
  const tx = 6 + ((t * 10) % 34);
  ctx.fillStyle = "#C93B3B";
  roundRect(ctx, tx, 10, 14, 6, 2); ctx.fill();
  ctx.restore();

  // ---- Mid-Left: Lush Metropolitan Park (bow bridge + pond + meadow) ----
  ctx.save();
  ctx.translate(w * 0.19, h * 0.51);
  ctx.fillStyle = "#A9D39E";
  ctx.beginPath(); ctx.ellipse(0, 0, w * 0.125, h * 0.13, -0.08, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = "#9ED0E0";
  ctx.beginPath(); ctx.ellipse(-4, 14, w * 0.068, h * 0.055, 0.1, 0, Math.PI * 2); ctx.fill();
  // Subtle bow bridge
  ctx.strokeStyle = "#4A4540"; ctx.lineWidth = 2.4;
  ctx.beginPath(); ctx.moveTo(-28, 16); ctx.quadraticCurveTo(0, 1, 28, 16); ctx.stroke();
  // Tree crowns
  ctx.fillStyle = "#5F9666";
  [[-42, -26], [-18, -38], [26, -30], [44, -8], [-38, 28]].forEach(([tx, ty]) => {
    ctx.beginPath(); ctx.arc(tx, ty, 13, 0, Math.PI * 2); ctx.fill();
  });
  ctx.restore();

  // ---- Mid-Right: Sleek Warehouse Superstore ----
  ctx.save();
  ctx.translate(w * 0.76, h * 0.51);
  ctx.fillStyle = "#E8EAEB";
  ctx.strokeStyle = "#2C3034"; ctx.lineWidth = 1.8;
  roundRect(ctx, -56, -24, 112, 46, 6); ctx.fill(); ctx.stroke();
  ctx.fillStyle = "#C93F3B";
  roundRect(ctx, -56, -24, 112, 12, 4); ctx.fill();
  ctx.fillStyle = "#93B7D0";
  roundRect(ctx, -22, -4, 44, 24, 3); ctx.fill();
  // Flatbed carts
  ctx.strokeStyle = "#495057"; ctx.lineWidth = 1.5;
  [36, 46].forEach((cx) => {
    ctx.strokeRect(cx, 12, 14, 8);
  });
  ctx.restore();

  // ---- Bottom-Right: Sunlit Yacht Marina ----
  ctx.save();
  ctx.translate(w * 0.80, h * 0.80);
  const seaG = ctx.createLinearGradient(-80, -30, 80, 60);
  seaG.addColorStop(0, "#A9D9E8");
  seaG.addColorStop(1, "#7FBBD2");
  ctx.fillStyle = seaG;
  ctx.beginPath(); ctx.ellipse(0, 0, w * 0.14, h * 0.13, -0.2, 0, Math.PI * 2); ctx.fill();
  // Wooden pier
  ctx.fillStyle = "#B98B5D";
  roundRect(ctx, -46, -12, 66, 9, 2); ctx.fill();
  // Bobbing white luxury yacht
  const bob = Math.sin(t * 2.2) * 2.5;
  ctx.save();
  ctx.translate(4, 8 + bob);
  ctx.fillStyle = "#FFFFFF";
  ctx.strokeStyle = "#24303C"; ctx.lineWidth = 1.8;
  ctx.beginPath();
  ctx.moveTo(-26, 0); ctx.lineTo(24, 0); ctx.lineTo(34, -8); ctx.lineTo(-20, -8); ctx.closePath();
  ctx.fill(); ctx.stroke();
  ctx.fillStyle = "#3E627A";
  roundRect(ctx, -10, -14, 24, 6, 2); ctx.fill();
  ctx.restore();
  ctx.restore();

  // ---- Center-Left: Upscale Tree-Lined Boutique Avenue (Playable Phase 1) ----
  ctx.save();
  ctx.translate(w * 0.34, h * 0.69);
  ctx.fillStyle = "#E4DFD4";
  ctx.beginPath();
  ctx.moveTo(-78, 18); ctx.lineTo(76, 8); ctx.lineTo(84, 34); ctx.lineTo(-74, 42); ctx.closePath();
  ctx.fill();
  // 3 sleek contemporary glass-and-brick boutiques
  [
    { x: -58, w: 38, h: 36, roof: "#2F353B", wall: "#FAF5EC", awning: "#7F2334" },
    { x: -16, w: 38, h: 40, roof: "#4B5D52", wall: "#F3EFE6", awning: "#3A5A46" },
    { x: 26, w: 38, h: 34, roof: "#2F353B", wall: "#FBF8F2", awning: "#C88D3B" },
  ].forEach((b) => {
    ctx.fillStyle = b.wall;
    ctx.strokeStyle = "#2A2B2E"; ctx.lineWidth = 1.6;
    roundRect(ctx, b.x, -b.h + 14, b.w, b.h, 4); ctx.fill(); ctx.stroke();
    ctx.fillStyle = b.roof;
    roundRect(ctx, b.x - 2, -b.h + 12, b.w + 4, 7, 2); ctx.fill();
    ctx.fillStyle = "#D6EAF2";
    roundRect(ctx, b.x + 6, -b.h + 26, b.w - 12, b.h - 18, 2); ctx.fill();
    ctx.fillStyle = b.awning;
    roundRect(ctx, b.x + 2, -b.h + 22, b.w - 4, 6, 2); ctx.fill();
  });
  ctx.restore();

  // ---- Centerpiece: Standalone Modern Villa House with Classical Courtyard Proportion (Playable Phase 1) ----
  ctx.save();
  ctx.translate(w * 0.55, h * 0.73);
  // Private sunlit green lawn
  ctx.fillStyle = sulking ? "#8CA89A" : "#97C98D";
  ctx.beginPath(); ctx.ellipse(0, 14, w * 0.145, h * 0.11, 0, 0, Math.PI * 2); ctx.fill();

  // Minimalist courtyard reflecting pool
  ctx.fillStyle = "#A9D5E0";
  roundRect(ctx, -64, 16, 46, 18, 6); ctx.fill();

  // Standalone 2-story modern architectural villa (cantilevered dark-timber eaves + white limestone + soaring glass)
  ctx.fillStyle = "#FAF8F2";
  ctx.strokeStyle = "#232528"; ctx.lineWidth = 1.8;
  // Main lower pavilion
  roundRect(ctx, -46, -24, 96, 38, 4); ctx.fill(); ctx.stroke();
  // Second-floor cantilevered suite
  roundRect(ctx, -28, -50, 66, 28, 4); ctx.fill(); ctx.stroke();
  // Warm glowing floor-to-ceiling glass walls
  const glassG = ctx.createLinearGradient(-34, -18, 36, 10);
  glassG.addColorStop(0, "#FFEAC2");
  glassG.addColorStop(1, "#D6E8EE");
  ctx.fillStyle = glassG;
  roundRect(ctx, -38, -16, 44, 26, 2); ctx.fill(); ctx.stroke();
  roundRect(ctx, 14, -16, 28, 26, 2); ctx.fill(); ctx.stroke();
  roundRect(ctx, -20, -42, 48, 16, 2); ctx.fill(); ctx.stroke();

  // Signature contemporary-classical flat cantilevered dark timber eaves
  ctx.fillStyle = "#2C3035";
  roundRect(ctx, -34, -55, 78, 8, 2); ctx.fill();
  roundRect(ctx, -52, -28, 108, 7, 2); ctx.fill();

  // Sculptural courtyard pine
  ctx.strokeStyle = "#4A3F38"; ctx.lineWidth = 2.6;
  ctx.beginPath(); ctx.moveTo(-66, 18); ctx.quadraticCurveTo(-72, -4, -62, -16); ctx.stroke();
  ctx.fillStyle = "#4A7856";
  ctx.beginPath(); ctx.ellipse(-60, -18, 15, 7, -0.2, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.ellipse(-72, -8, 11, 5, 0.15, 0, Math.PI * 2); ctx.fill();

  // Animated tiny Bruce trotting happily on the villa lawn!
  const bruceX = 24 + Math.sin(t * 1.4) * 14;
  drawBruce(ctx, {
    x: bruceX,
    y: 26,
    scale: 0.36,
    facing: Math.cos(t * 1.4) >= 0 ? 1 : -1,
    mood: sulking ? "sulk" : "happy",
    t,
    walkSpeed: sulking ? 0 : 0.7,
  });

  ctx.restore();
}

/**
 * Shared Villa Living Room interior (sunlit oak chevron floor, floor-to-ceiling courtyard glass, sofa, vinyl)
 */
export function drawVillaInterior(ctx, w, h, t, opts = {}) {
  const { rain = false, shadeDrop = 0, spinVinyl = false } = opts;
  // Warm off-white gallery wall
  ctx.fillStyle = rain ? "#E7ECEF" : "#F8F5EE";
  ctx.fillRect(0, 0, w, h * 0.62);

  // Floor-to-ceiling modern glass wall looking out to private villa courtyard & sculptural pine
  const gx = w * 0.36;
  const gy = h * 0.08;
  const gw = w * 0.56;
  const gh = h * 0.54;
  const outGrad = ctx.createLinearGradient(gx, gy, gx, gy + gh);
  outGrad.addColorStop(0, rain ? "#CBD8E2" : "#DDF0F6");
  outGrad.addColorStop(1, rain ? "#BDCAC9" : "#DCEBD4");
  ctx.fillStyle = outGrad;
  ctx.fillRect(gx, gy, gw, gh);

  // Courtyard cedar eave & pine outside glass
  ctx.fillStyle = "#2E3338";
  ctx.fillRect(gx, gy, gw, 16);
  ctx.fillStyle = rain ? "#6A8479" : "#679B6E";
  ctx.beginPath();
  ctx.ellipse(gx + gw * 0.72, gy + gh * 0.56, 56, 26, -0.1, 0, Math.PI * 2);
  ctx.ellipse(gx + gw * 0.58, gy + gh * 0.68, 42, 18, 0.1, 0, Math.PI * 2);
  ctx.fill();

  // Animated raindrops on glass if rain
  if (rain) {
    ctx.strokeStyle = "rgba(86, 124, 156, 0.5)";
    ctx.lineWidth = 1.6;
    for (let i = 0; i < 24; i += 1) {
      const rx = gx + ((i * 37) % gw);
      const ry = gy + (((i * 53) + t * 180) % gh);
      ctx.beginPath();
      ctx.moveTo(rx, ry);
      ctx.lineTo(rx - 4, ry + 14);
      ctx.stroke();
    }
  }

  // Retractable linen terrace shade if shadeDrop > 0
  if (shadeDrop > 0) {
    ctx.fillStyle = "rgba(244, 236, 220, 0.9)";
    ctx.fillRect(gx, gy, gw, gh * Math.min(1, shadeDrop));
    ctx.strokeStyle = "#8C7B65";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(gx, gy + gh * Math.min(1, shadeDrop));
    ctx.lineTo(gx + gw, gy + gh * Math.min(1, shadeDrop));
    ctx.stroke();
  }

  // Minimalist black window mullions
  ctx.strokeStyle = "#2A2D31";
  ctx.lineWidth = 3;
  ctx.strokeRect(gx, gy, gw, gh);
  ctx.beginPath();
  ctx.moveTo(gx + gw * 0.5, gy);
  ctx.lineTo(gx + gw * 0.5, gy + gh);
  ctx.stroke();

  // Sunlit oak floor
  const floorGrad = ctx.createLinearGradient(0, h * 0.62, 0, h);
  floorGrad.addColorStop(0, rain ? "#CFC5B4" : "#E5D0AE");
  floorGrad.addColorStop(1, rain ? "#BFB3A0" : "#D6BA90");
  ctx.fillStyle = floorGrad;
  ctx.fillRect(0, h * 0.62, w, h * 0.38);
  ctx.strokeStyle = "rgba(115, 86, 52, 0.16)";
  ctx.lineWidth = 1.2;
  for (let i = 0; i < 9; i += 1) {
    const px = (w / 8) * i;
    ctx.beginPath();
    ctx.moveTo(px, h * 0.62);
    ctx.lineTo(px - 60, h);
    ctx.stroke();
  }

  // Sunbeam diagonal wash on sunny days
  if (!rain && shadeDrop < 0.6) {
    ctx.fillStyle = `rgba(255, 246, 214, ${0.26 * (1 - shadeDrop)})`;
    ctx.beginPath();
    ctx.moveTo(gx + 20, gy + gh);
    ctx.lineTo(gx + gw - 20, gy + gh);
    ctx.lineTo(w * 0.68, h);
    ctx.lineTo(w * 0.15, h);
    ctx.closePath();
    ctx.fill();
  }

  // Woven neutral wool rug
  ctx.fillStyle = "#EFE6D6";
  ctx.strokeStyle = "rgba(42, 36, 33, 0.25)";
  ctx.lineWidth = 1.5;
  roundRect(ctx, w * 0.18, h * 0.67, w * 0.64, h * 0.24, 18);
  ctx.fill();
  ctx.stroke();

  // Cream bouclé lounge sofa on left
  ctx.fillStyle = "#F7F3EA";
  ctx.strokeStyle = "#2A2421";
  ctx.lineWidth = 1.8;
  roundRect(ctx, w * 0.04, h * 0.43, w * 0.28, h * 0.23, 14);
  ctx.fill();
  ctx.stroke();

  // Walnut vinyl player stand on far left/side
  ctx.fillStyle = "#8C623D";
  roundRect(ctx, w * 0.05, h * 0.66, 78, 52, 8);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#232528";
  ctx.beginPath();
  ctx.ellipse(w * 0.05 + 39, h * 0.66 + 10, 22, 8, 0, 0, Math.PI * 2);
  ctx.fill();
  if (spinVinyl) {
    ctx.strokeStyle = "#D4A44C";
    ctx.beginPath();
    ctx.arc(w * 0.05 + 39, h * 0.66 + 10, 5, t * 5, t * 5 + Math.PI);
    ctx.stroke();
  }
}

export function drawPhoneNotificationCanvas(ctx, x, y, app, text, t) {
  ctx.save();
  const wobble = Math.sin(t * 14) * 1.8;
  ctx.translate(x + wobble, y);
  ctx.fillStyle = "rgba(24, 24, 28, 0.94)";
  roundRect(ctx, 0, 0, 196, 54, 16);
  ctx.fill();
  ctx.strokeStyle = "rgba(255,255,255,0.16)";
  ctx.lineWidth = 1;
  ctx.stroke();

  // Red notification dot
  ctx.fillStyle = "#EF4444";
  ctx.beginPath();
  ctx.arc(18, 17, 4.5, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#A1A1AA";
  ctx.font = "700 10px -apple-system, sans-serif";
  ctx.fillText(app, 28, 20);

  ctx.fillStyle = "#FFFFFF";
  ctx.font = "700 12px -apple-system, sans-serif";
  ctx.fillText(text, 16, 40);
  ctx.restore();
}
