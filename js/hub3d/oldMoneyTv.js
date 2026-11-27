import * as THREE from "three";

export const OLD_MONEY_CHANNELS = [
  {
    id: "regatta",
    code: "CH 01",
    tag: "REGATTA · 古典帆船锦标赛",
    title: "地中海古典 J-Class 单桅帆船赛实况",
    sub: "风速 14.8 KT · WSW · 215° 顺风领航",
  },
  {
    id: "auction",
    code: "CH 02",
    tag: "AUCTION · 古典大师与钟表私洽",
    title: "日内瓦与伦敦秋拍预展 · LOT 14 陀飞轮与海景油画",
    sub: "PRIVATE VIEW · ARCHIVAL HOROLOGY & MARITIME OIL",
  },
  {
    id: "equestrian",
    code: "CH 03",
    tag: "DRESSAGE · 草地盛装舞步大奖赛",
    title: "皇家草地障碍与盛装舞步 · 延长快步评分分段",
    sub: "ARENA A · 84.60% ARTISTIC IMPRESSION",
  },
  {
    id: "chamber",
    code: "CH 04",
    tag: "RECITAL · 烛光室内大提琴夜曲",
    title: "维也纳室内乐沙龙 · Op. 101 晚间现场实况",
    sub: "LIVE CHAMBER ACOUSTIC · 96kHz / 24-BIT",
  },
];

export function createOldMoneyTv() {
  const w = 768;
  const h = 432;
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  // GLB Geometry uses top-left image origin (prim_lib flips V via 1 - v),
  // so flipY = false aligns canvas (0,0) top-left cleanly with Screen top-left.
  texture.flipY = false;

  let chIdx = 0;
  let lastDrawTime = -1;

  function drawOsdChrome(ch, elapsed) {
    // Subtle Apple-minimal cinema top bar & corner live dot
    const gradTop = ctx.createLinearGradient(0, 0, 0, 74);
    gradTop.addColorStop(0, "rgba(12, 11, 10, 0.72)");
    gradTop.addColorStop(1, "rgba(12, 11, 10, 0.0)");
    ctx.fillStyle = gradTop;
    ctx.fillRect(0, 0, w, 74);

    const gradBot = ctx.createLinearGradient(0, h - 84, 0, h);
    gradBot.addColorStop(0, "rgba(12, 11, 10, 0.0)");
    gradBot.addColorStop(1, "rgba(12, 11, 10, 0.80)");
    ctx.fillStyle = gradBot;
    ctx.fillRect(0, h - 84, w, 84);

    // Corner serif wordmark / channel code
    ctx.fillStyle = "rgba(232, 206, 152, 0.92)";
    ctx.font = "600 15px -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif";
    ctx.textAlign = "left";
    ctx.fillText(`${ch.code}  ·  ${ch.tag}`, 28, 34);

    const pulse = 0.55 + 0.45 * Math.sin(elapsed * 3.2);
    ctx.fillStyle = `rgba(220, 178, 106, ${pulse.toFixed(2)})`;
    ctx.beginPath();
    ctx.arc(w - 92, 30, 4.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "rgba(245, 239, 226, 0.82)";
    ctx.font = "600 13px -apple-system, BlinkMacSystemFont, sans-serif";
    ctx.textAlign = "right";
    ctx.fillText("ARCHIVE LIVE", w - 28, 34);

    // Lower chyron
    ctx.textAlign = "left";
    ctx.fillStyle = "#F5EFE2";
    ctx.font = "600 20px Georgia, 'Noto Serif SC', serif";
    ctx.fillText(ch.title, 28, h - 42);
    ctx.fillStyle = "rgba(224, 198, 142, 0.84)";
    ctx.font = "500 13px -apple-system, BlinkMacSystemFont, sans-serif";
    ctx.fillText(ch.sub, 28, h - 20);

    // Subtle hairline museum frame inside bezel
    ctx.strokeStyle = "rgba(218, 190, 132, 0.25)";
    ctx.lineWidth = 1.5;
    ctx.strokeRect(10, 10, w - 20, h - 20);
  }

  function drawRegatta(t) {
    const sky = ctx.createLinearGradient(0, 0, 0, h * 0.62);
    sky.addColorStop(0, "#1D3554");
    sky.addColorStop(0.58, "#6A829D");
    sky.addColorStop(1, "#E8BA84");
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, w, h * 0.62);

    // Warm horizon sun glow
    const sunX = w * 0.72;
    const sunY = h * 0.52;
    const sg = ctx.createRadialGradient(sunX, sunY, 8, sunX, sunY, 170);
    sg.addColorStop(0, "rgba(255, 238, 196, 0.92)");
    sg.addColorStop(0.35, "rgba(240, 178, 108, 0.42)");
    sg.addColorStop(1, "rgba(240, 178, 108, 0)");
    ctx.fillStyle = sg;
    ctx.fillRect(0, 0, w, h * 0.65);

    // Deep sapphire ocean & shimmering wave highlights
    const sea = ctx.createLinearGradient(0, h * 0.60, 0, h);
    sea.addColorStop(0, "#1D466E");
    sea.addColorStop(1, "#0E253D");
    ctx.fillStyle = sea;
    ctx.fillRect(0, h * 0.60, w, h * 0.40);

    for (let i = 0; i < 28; i++) {
      const yy = h * 0.62 + i * 5.8;
      const shift = Math.sin(t * 1.6 + i * 0.7) * 18;
      ctx.strokeStyle = i % 3 === 0 ? "rgba(255, 224, 168, 0.34)" : "rgba(182, 214, 240, 0.16)";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(w * 0.1 + shift, yy);
      ctx.lineTo(w * 0.9 + shift * 0.6, yy);
      ctx.stroke();
    }

    // 3 classic J-Class yachts racing left-to-right
    const yachts = [
      { bx: ((t * 18) % (w + 260)) - 130, by: h * 0.66, scale: 1.05, heel: 0.08 },
      { bx: ((t * 14 + 260) % (w + 260)) - 130, by: h * 0.63, scale: 0.76, heel: 0.06 },
      { bx: ((t * 11 + 510) % (w + 260)) - 130, by: h * 0.61, scale: 0.56, heel: 0.05 },
    ];
    yachts.forEach((y, idx) => {
      const bob = Math.sin(t * 2.2 + idx * 1.4) * 3.5;
      ctx.save();
      ctx.translate(y.bx, y.by + bob);
      ctx.scale(y.scale, y.scale);
      ctx.rotate(y.heel + Math.sin(t * 1.7 + idx) * 0.02);

      // Wake line
      ctx.strokeStyle = "rgba(244, 238, 226, 0.45)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(-95, 10);
      ctx.lineTo(-22, 6);
      ctx.stroke();

      // Dark navy hull
      ctx.fillStyle = "#122136";
      ctx.beginPath();
      ctx.moveTo(-48, 0);
      ctx.lineTo(52, -2);
      ctx.lineTo(38, 11);
      ctx.lineTo(-42, 11);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = "#DFBE7D";
      ctx.lineWidth = 1.4;
      ctx.stroke();

      // Ivory gaff mainsail + jib
      ctx.fillStyle = "#F3EBDC";
      ctx.beginPath();
      ctx.moveTo(0, -118);
      ctx.lineTo(-34, -8);
      ctx.lineTo(2, -8);
      ctx.closePath();
      ctx.fill();

      ctx.fillStyle = "#E6DAC5";
      ctx.beginPath();
      ctx.moveTo(4, -104);
      ctx.lineTo(44, -8);
      ctx.lineTo(6, -8);
      ctx.closePath();
      ctx.fill();

      ctx.restore();
    });
  }

  function drawAuction(t) {
    ctx.fillStyle = "#181412";
    ctx.fillRect(0, 0, w, h);

    // Left frame: Chiaroscuro Turner seascape preview with slow Ken Burns pan
    const fx = 52;
    const fy = 66;
    const fw = 360;
    const fh = 264;
    ctx.fillStyle = "#2E2318";
    ctx.fillRect(fx - 10, fy - 10, fw + 20, fh + 20);
    ctx.strokeStyle = "#C4A362";
    ctx.lineWidth = 2;
    ctx.strokeRect(fx - 6, fy - 6, fw + 12, fh + 12);

    ctx.save();
    ctx.beginPath();
    ctx.rect(fx, fy, fw, fh);
    ctx.clip();
    const pan = Math.sin(t * 0.45) * 14;
    const artGrad = ctx.createLinearGradient(fx, fy, fx, fy + fh);
    artGrad.addColorStop(0, "#243140");
    artGrad.addColorStop(0.52, "#9F6E4A");
    artGrad.addColorStop(0.65, "#E0B474");
    artGrad.addColorStop(1, "#1C2B33");
    ctx.fillStyle = artGrad;
    ctx.fillRect(fx, fy, fw, fh);
    ctx.fillStyle = "rgba(255, 232, 184, 0.25)";
    ctx.beginPath();
    ctx.arc(fx + 220 + pan, fy + 124, 52, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#1A1918";
    ctx.beginPath();
    ctx.moveTo(fx + 100 + pan, fy + 195);
    ctx.lineTo(fx + 172 + pan, fy + 195);
    ctx.lineTo(fx + 158 + pan, fy + 210);
    ctx.lineTo(fx + 112 + pan, fy + 210);
    ctx.closePath();
    ctx.fill();
    ctx.restore();

    // Right panel: Rotating golden mechanical tourbillon caliber study
    const cx = 580;
    const cy = 198;
    ctx.strokeStyle = "rgba(218, 190, 132, 0.35)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, 112, 0, Math.PI * 2);
    ctx.stroke();
    ctx.fillStyle = "#221D1A";
    ctx.beginPath();
    ctx.arc(cx, cy, 102, 0, Math.PI * 2);
    ctx.fill();

    // Ticking skeleton balance gear + escapement
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(t * 0.85);
    ctx.strokeStyle = "#DFBE7D";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(0, 0, 68, 0, Math.PI * 2);
    ctx.stroke();
    for (let s = 0; s < 6; s++) {
      const a = (s * Math.PI) / 3;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(Math.cos(a) * 68, Math.sin(a) * 68);
      ctx.stroke();
    }
    ctx.restore();

    // Second sweep hand
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(t * 1.4);
    ctx.strokeStyle = "#E8D5B0";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 16);
    ctx.lineTo(0, -86);
    ctx.stroke();
    ctx.fillStyle = "#8C3344";
    ctx.beginPath();
    ctx.arc(0, 0, 7, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  function drawEquestrian(t) {
    const sky = ctx.createLinearGradient(0, 0, 0, h * 0.56);
    sky.addColorStop(0, "#4B6882");
    sky.addColorStop(1, "#DFCEB4");
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, w, h * 0.56);

    // Distant hedged manor trees
    ctx.fillStyle = "#2B4031";
    ctx.fillRect(0, h * 0.46, w, h * 0.11);

    // Emerald turf arena
    const turf = ctx.createLinearGradient(0, h * 0.56, 0, h);
    turf.addColorStop(0, "#375639");
    turf.addColorStop(1, "#243D26");
    ctx.fillStyle = turf;
    ctx.fillRect(0, h * 0.56, w, h * 0.44);

    // Classic white arena dressage rails
    ctx.strokeStyle = "#EFE9DC";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(30, h * 0.64);
    ctx.lineTo(w - 30, h * 0.64);
    ctx.stroke();
    for (let x = 60; x <= w - 60; x += 92) {
      ctx.fillStyle = "#EFE9DC";
      ctx.fillRect(x - 4, h * 0.61, 8, 28);
    }

    // Animated warm bay dressage horse & rider in extended trot
    const hx = ((t * 58) % (w + 180)) - 90;
    const hy = h * 0.68 + Math.abs(Math.sin(t * 4.5)) * -6;
    ctx.save();
    ctx.translate(hx, hy);
    // Horse silhouette in rich chestnut bay
    ctx.fillStyle = "#5C311B";
    ctx.beginPath();
    ctx.ellipse(0, 0, 38, 16, 0, 0, Math.PI * 2);
    ctx.fill();
    // Neck & head
    ctx.beginPath();
    ctx.moveTo(22, -6);
    ctx.lineTo(44, -38);
    ctx.lineTo(58, -32);
    ctx.lineTo(54, -22);
    ctx.lineTo(36, 4);
    ctx.closePath();
    ctx.fill();
    // Animated striding legs
    const stride = Math.sin(t * 4.5) * 14;
    ctx.strokeStyle = "#482412";
    ctx.lineWidth = 5.5;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(-22, 10);
    ctx.lineTo(-26 - stride, 42);
    ctx.moveTo(-14, 10);
    ctx.lineTo(-10 + stride, 42);
    ctx.moveTo(20, 10);
    ctx.lineTo(28 + stride * 1.15, 38);
    ctx.moveTo(14, 10);
    ctx.lineTo(10 - stride * 0.9, 42);
    ctx.stroke();

    // Navy tailcoat rider & top hat
    ctx.fillStyle = "#192234";
    ctx.fillRect(-10, -44, 16, 32);
    ctx.fillStyle = "#EFE9DC";
    ctx.fillRect(-6, -18, 12, 18);
    ctx.fillStyle = "#141416";
    ctx.fillRect(-9, -56, 14, 12);
    ctx.restore();
  }

  function drawChamber(t) {
    const bg = ctx.createRadialGradient(w * 0.5, h * 0.45, 30, w * 0.5, h * 0.5, w * 0.62);
    bg.addColorStop(0, "#462A1B");
    bg.addColorStop(0.55, "#231712");
    bg.addColorStop(1, "#0F0C0B");
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, w, h);

    // Warm candle bokeh circles
    for (let i = 0; i < 16; i++) {
      const bx = 70 + ((i * 97) % (w - 140));
      const by = 80 + ((i * 61) % 210) + Math.sin(t * 1.8 + i) * 4;
      const rad = 14 + (i % 4) * 7;
      const g = ctx.createRadialGradient(bx, by, 1, bx, by, rad);
      g.addColorStop(0, "rgba(255, 224, 148, 0.55)");
      g.addColorStop(1, "rgba(255, 190, 96, 0)");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(bx, by, rad, 0, Math.PI * 2);
      ctx.fill();
    }

    // Cello silhouette + moving bow
    const cx = w * 0.5;
    const cy = h * 0.54;
    ctx.fillStyle = "#8C4C28";
    ctx.beginPath();
    ctx.ellipse(cx, cy + 28, 34, 42, 0, 0, Math.PI * 2);
    ctx.ellipse(cx, cy - 22, 24, 28, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillRect(cx - 5, cy - 102, 10, 62);
    const bowX = Math.sin(t * 2.1) * 38;
    ctx.strokeStyle = "#E8CE96";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(cx - 58 + bowX, cy - 14);
    ctx.lineTo(cx + 58 + bowX, cy - 4);
    ctx.stroke();

    // Subtle champagne-gold harmonic bars
    for (let b = 0; b < 28; b++) {
      const amp = 10 + Math.abs(Math.sin(t * 3.1 + b * 0.45)) * 42;
      ctx.fillStyle = "rgba(223, 190, 125, 0.42)";
      ctx.fillRect(140 + b * 17.5, h - 104 - amp, 6, amp);
    }
  }

  function renderFrame(elapsed) {
    const ch = OLD_MONEY_CHANNELS[chIdx];
    if (ch.id === "regatta") drawRegatta(elapsed);
    else if (ch.id === "auction") drawAuction(elapsed);
    else if (ch.id === "equestrian") drawEquestrian(elapsed);
    else drawChamber(elapsed);
    drawOsdChrome(ch, elapsed);
    texture.needsUpdate = true;
  }

  renderFrame(0);

  return {
    texture,
    getChannel: () => ({ index: chIdx, ...OLD_MONEY_CHANNELS[chIdx] }),
    setChannel(idx, elapsed = 0) {
      chIdx = ((idx % OLD_MONEY_CHANNELS.length) + OLD_MONEY_CHANNELS.length) % OLD_MONEY_CHANNELS.length;
      renderFrame(elapsed);
      lastDrawTime = elapsed;
      return this.getChannel();
    },
    nextChannel(elapsed = 0) {
      return this.setChannel(chIdx + 1, elapsed);
    },
    update(elapsed) {
      if (lastDrawTime < 0 || elapsed - lastDrawTime >= 1 / 24) {
        lastDrawTime = elapsed;
        renderFrame(elapsed);
      }
    },
    dispose() {
      texture.dispose();
    },
  };
}
