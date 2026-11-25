import { store } from "./state.js";
import { apiTriggerSwap, apiUpdateScore } from "./api.js";
import { feedback } from "./juice.js";
import { sfx } from "./audio.js";
import { showSwapResultModal } from "./leaderboard.js";
import {
  drawBruce,
  drawLeash,
  drawPhoneNotificationCanvas,
  drawVillaInterior,
  fitCanvas,
} from "./renderer.js";

const HOME_ACTIVITIES = [
  {
    id: "home_hide_seek",
    title: "客厅抛球寻宝",
    desc: "在阳光客厅里拖着网球藏进角落，再呼唤布鲁斯嗅探扑找；别点弹出手机！",
    reward: "+12 分 · 12% 触发换分",
    hazard: "点手机/发呆 -14",
  },
  {
    id: "home_brush",
    title: "露台阳光顺毛",
    desc: "用木柄梳在布鲁斯背上轻轻来回滑动；看到飞机耳预警立刻停手，别开吹风机！",
    reward: "+11 分",
    hazard: "太急/吹风机 -13",
  },
  {
    id: "home_rain_vinyl",
    title: "雨窗擦爪听黑胶",
    desc: "落地窗外飘雨，先拖毛巾擦干湿爪 → 披上毛毯 → 点黑胶唱机放音乐。",
    reward: "+12 分",
    hazard: "顺序搞反 -12",
  },
  {
    id: "home_kitchen",
    title: "岛台手作鲜食",
    desc: "把安全食材拖进 BRUCE 陶瓷碗、禁忌食材拖进 TRASH 垃圾桶，顺手忍住不看手机。",
    reward: "+13 分",
    hazard: "误喂毒食/分心 -15",
  },
  {
    id: "home_nap",
    title: "庭院午睡放空",
    desc: "拉下遮阳帘、拍松软垫，再忍住 6 秒钟不点连续弹出的英文手机推送。",
    reward: "+11 分 · 12% 触发换分",
    hazard: "手痒点手机 -14",
  },
];

const STREET_ACTIVITIES = [
  {
    id: "street_cafe",
    title: "林荫街角探店",
    desc: "牵着弯弯的皮质牵引绳走过精品店门口，看清门贴 PAWS WELCOME vs NO DOGS 再进门！",
    reward: "+14 分 · 22% 触发换分",
    hazard: "硬闯禁入店 -18",
  },
  {
    id: "street_walk",
    title: "绿道晨间漫步",
    desc: "牵绳在林荫道灵活左右走位，接住落叶和小球，躲开急刹电动车与地上竹签。",
    reward: "+12 分",
    hazard: "撞车/看手机 -14",
  },
  {
    id: "street_lawn",
    title: "草坪狗友社交",
    desc: "连着 3 轮牵着布鲁斯去和摇尾巴（WAGGING）的友善狗狗贴鼻，远离炸毛恶犬。",
    reward: "+13 分 · 18% 触发换分",
    hazard: "撞上恶犬 -15",
  },
  {
    id: "street_window",
    title: "花房与烘焙橱窗",
    desc: "挑出挂着宠友试吃招牌的橱窗，拖出清水和小饼干喂布鲁斯拍下拍立得留念。",
    reward: "+11 分",
    hazard: "挤进 NO PETS 店 -15",
  },
  {
    id: "street_bridge",
    title: "暮色水岸晚风",
    desc: "在蓝调暮色水岸边点亮水面灯影，牵着布鲁斯躲开大喇叭与摩托轰鸣声浪。",
    reward: "+14 分 · 14% 触发换分",
    hazard: "噪音惊吓 -16",
  },
];

let cleanupActiveGame = null;

function pickRandom(arr, fallback = "") {
  if (!Array.isArray(arr) || arr.length === 0) return fallback;
  return arr[Math.floor(Math.random() * arr.length)];
}

function formatTemplate(tpl, vars) {
  return String(tpl || "").replace(/\{(\w+)\}/g, (_, k) => (vars[k] !== undefined ? vars[k] : ""));
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

function drawPillTag(ctx, x, y, w, h, label, bg = "rgba(255,255,255,0.92)", fg = "#1D2024", border = "rgba(29,32,36,0.16)") {
  ctx.save();
  ctx.fillStyle = bg;
  ctx.strokeStyle = border;
  ctx.lineWidth = 1.4;
  roundRect(ctx, x, y, w, h, h / 2);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = fg;
  ctx.font = "700 12px -apple-system, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(label, x + w / 2, y + h / 2 + 0.5);
  ctx.restore();
}

function getCanvasCoords(canvas, clientX, clientY) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: clientX - rect.left,
    y: clientY - rect.top,
    w: rect.width,
    h: rect.height,
  };
}

async function concludeActivity(activityId, outcome, delta, failType = "hazard", swapChance = 0, reasonLabel = "陪布鲁斯玩耍") {
  if (cleanupActiveGame) {
    cleanupActiveGame();
    cleanupActiveGame = null;
  }

  const player = store.state.player;
  const content = store.state.content;
  if (!player || !content) return;

  const actLines = content.activities?.[activityId] || {};
  let line = "";
  if (outcome === "win") {
    line = pickRandom(actLines.win_lines, "布鲁斯开心地摇着大尾巴贴了过来！");
  } else if (failType === "phone") {
    line = pickRandom(actLines.phone_fail_lines, "你低头看手机，布鲁斯默默把下巴收了回去。");
  } else {
    line = pickRandom(actLines.hazard_fail_lines, "踩到布鲁斯的雷点了，它委屈地把领巾歪到一边。");
  }

  const oldScore = player.happiness;
  let nextScore = Math.max(0, oldScore + delta);
  let tickerMsg = "";

  if (oldScore >= 80 && nextScore < 80) {
    const tpl = pickRandom(content.ticker_templates?.collapse, "{player} 踩雷跌破 80，布鲁斯宣布进入冷战！");
    tickerMsg = formatTemplate(tpl, { player: player.nickname, old_score: oldScore, new_score: nextScore });
  }

  try {
    const res = await apiUpdateScore(player.nickname, player.pin, player.owner, nextScore, tickerMsg);
    store.setHappiness(res.player.happiness);
    store.setLeaderboardAndTicker(res.leaderboard, res.ticker);
    nextScore = res.player.happiness;
  } catch (_) {
    store.setHappiness(nextScore);
  }

  const cx = window.innerWidth / 2;
  const cy = window.innerHeight * 0.36;
  feedback(outcome === "win" ? "win" : "fail", cx, cy, `${delta >= 0 ? "+" : ""}${delta}`);

  let imgFile = "bruce_happy.jpg";
  if (outcome !== "win") {
    if (failType === "phone") imgFile = "bruce_phone.jpg";
    else if (failType === "blocked") imgFile = "bruce_blocked.jpg";
    else imgFile = "bruce_sulk.jpg";
  }

  const triggeredSwap = outcome === "win" && nextScore >= 80 && Math.random() < swapChance;
  let swapData = null;
  if (triggeredSwap) {
    try {
      swapData = await apiTriggerSwap(player.nickname, player.pin, reasonLabel);
      store.setHappiness(swapData.newScore);
      store.setLeaderboardAndTicker(swapData.leaderboard, swapData.ticker);
      feedback("swap");
    } catch (_) {
      swapData = null;
    }
  }

  const modal = document.getElementById("generic-modal");
  const card = document.getElementById("generic-modal-card");
  if (!modal || !card) return;

  const fellBelow80 = nextScore < 80;
  card.innerHTML = `
    <span class="modal-pill-tag">${outcome === "win" ? "陪伴高光时刻" : "踩雷小插曲"}</span>
    <h2 class="modal-title">${outcome === "win" ? `幸福指数 ${delta >= 0 ? "+" + delta : delta}！` : `踩雷了 · 幸福指数 ${delta}`}</h2>
    <img src="./assets/img/${imgFile}" alt="布鲁斯反应" class="modal-bruce-thumb" />
    <p class="modal-lead" style="text-align:center;">${line}</p>
    <div class="score-summary-pill">
      <span>当前幸福指数</span>
      <strong style="color:${fellBelow80 ? "var(--danger)" : "var(--burgundy)"};">${store.state.player.happiness}</strong>
    </div>
    ${fellBelow80 ? `
      <p style="font-size:13px;color:var(--danger);font-weight:700;margin-bottom:10px;text-align:center;">
        已跌破 80 分！布鲁斯进入冷战状态，先去零食急救柜哄它回来吧。
      </p>
      <button class="btn-pill btn-primary btn-block" id="btn-go-shop-after" type="button">去零食急救柜哄狗</button>
    ` : `
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <button class="btn-pill" style="flex:1;" id="btn-back-hub" type="button">换个活动玩</button>
        <button class="btn-pill btn-primary" style="flex:1;" id="btn-back-map" type="button">回大地图</button>
      </div>
    `}
  `;
  modal.classList.remove("hidden");

  document.getElementById("btn-go-shop-after")?.addEventListener("click", () => {
    modal.classList.add("hidden");
    store.setView("shop");
  });
  document.getElementById("btn-back-hub")?.addEventListener("click", () => {
    modal.classList.add("hidden");
    store.setView(store.state.view, null);
  });
  document.getElementById("btn-back-map")?.addEventListener("click", () => {
    modal.classList.add("hidden");
    store.setView("map", null);
  });

  if (swapData) {
    setTimeout(() => showSwapResultModal(swapData), 420);
  }
}

/* ==================== 10 RICH CANVAS COMPANIONSHIP GAMES ==================== */

function mountHomeHideSeek(stage) {
  stage.innerHTML = `
    <div class="canvas-hud-overlay">
      <span class="hud-chip" id="hs-round">第 1 / 3 轮 · 拖网球藏进角落</span>
      <button class="btn-pill btn-cypress hidden" id="btn-call-bruce" type="button">呼唤布鲁斯来找球</button>
    </div>
    <canvas class="scene-canvas" id="game-canvas"></canvas>
  `;
  const canvas = document.getElementById("game-canvas");
  const roundEl = document.getElementById("hs-round");
  const callBtn = document.getElementById("btn-call-bruce");

  let round = 1;
  let ball = { x: 0, y: 0, dragging: false, hiddenZone: null, init: false };
  let bruce = { x: 140, y: 245, targetX: 140, targetY: 245, chasing: false };
  let phone = null;
  let idleSec = 0;
  let finished = false;
  let rafId = null;

  const phonePool = store.state.content?.phone_notifications || [{ app: "CHAT", text: "NEW MESSAGE · 99+" }];
  const zones = [
    { id: "SOFA", label: "SOFA", rx: 0.18, ry: 0.56 },
    { id: "RUG", label: "RUG", rx: 0.52, ry: 0.78 },
    { id: "PLANT", label: "COURTYARD", rx: 0.80, ry: 0.58 },
  ];

  const onDown = (e) => {
    if (finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    idleSec = 0;
    if (phone && p.x >= phone.x && p.x <= phone.x + 196 && p.y >= phone.y && p.y <= phone.y + 54) {
      finished = true;
      concludeActivity("home_hide_seek", "fail", -14, "phone");
      return;
    }
    if (!ball.hiddenZone && !bruce.chasing && Math.hypot(p.x - ball.x, p.y - ball.y) < 34) {
      ball.dragging = true;
      canvas.setPointerCapture(e.pointerId);
    }
  };
  const onMove = (e) => {
    if (!ball.dragging || finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    ball.x = p.x;
    ball.y = p.y;
  };
  const onUp = (e) => {
    if (!ball.dragging || finished) return;
    ball.dragging = false;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    const hit = zones.find((z) => Math.hypot(p.x - p.w * z.rx, p.y - p.h * z.ry) < 58);
    if (hit) {
      ball.hiddenZone = hit;
      ball.x = p.w * hit.rx;
      ball.y = p.h * hit.ry;
      callBtn.classList.remove("hidden");
      roundEl.textContent = `第 ${round} / 3 轮 · 已藏在 ${hit.label}，点按钮喊它！`;
      feedback("small", e.clientX, e.clientY);
    } else {
      ball.x = p.w * 0.5;
      ball.y = p.h * 0.88;
    }
  };

  canvas.addEventListener("pointerdown", onDown);
  canvas.addEventListener("pointermove", onMove);
  canvas.addEventListener("pointerup", onUp);

  callBtn.addEventListener("click", (e) => {
    if (finished || !ball.hiddenZone || bruce.chasing) return;
    callBtn.classList.add("hidden");
    bruce.chasing = true;
    bruce.targetX = ball.x - 24;
    bruce.targetY = ball.y;
    feedback("small", e.clientX, e.clientY);
  });

  const tPhone = setTimeout(() => {
    if (!finished) {
      const pick = pickRandom(phonePool, { app: "CHAT", text: "NEW MESSAGE · 99+" });
      phone = { ...pick, x: 16, y: 58 };
      sfx.playPhoneBuzz();
    }
  }, 2000);

  let lastTs = performance.now();
  const loop = (now) => {
    if (finished || !document.body.contains(canvas)) return;
    const dt = Math.min(0.05, (now - lastTs) / 1000);
    lastTs = now;
    idleSec += dt;
    if (idleSec > 8.5) {
      finished = true;
      concludeActivity("home_hide_seek", "fail", -14, "phone");
      return;
    }

    const { w, h, ctx } = fitCanvas(canvas);
    if (!ball.init) {
      ball.init = true;
      ball.x = w * 0.5;
      ball.y = h * 0.87;
      bruce.x = w * 0.25;
      bruce.y = h * 0.72;
    }

    const t = now / 1000;
    drawVillaInterior(ctx, w, h, t);

    // Draw hiding spot targets softly
    zones.forEach((z) => {
      const zx = w * z.rx;
      const zy = h * z.ry;
      const active = ball.hiddenZone?.id === z.id;
      drawPillTag(ctx, zx - 46, zy - 15, 92, 30, z.label, active ? "#3A5A46" : "rgba(255,255,255,0.86)", active ? "#FFF" : "#1D2024");
    });

    // Bruce chasing animation
    let walkSpd = 0;
    if (bruce.chasing) {
      const dx = bruce.targetX - bruce.x;
      const dy = bruce.targetY - bruce.y;
      const d = Math.hypot(dx, dy);
      if (d > 6) {
        bruce.x += (dx / d) * 240 * dt;
        bruce.y += (dy / d) * 240 * dt;
        walkSpd = 1;
      } else {
        bruce.chasing = false;
        if (round >= 3) {
          finished = true;
          concludeActivity("home_hide_seek", "win", 12, "hazard", 0.12, "客厅藏球寻宝大获全胜");
          return;
        }
        round += 1;
        ball.hiddenZone = null;
        ball.x = w * 0.5;
        ball.y = h * 0.87;
        roundEl.textContent = `第 ${round} / 3 轮 · 拖网球藏进角落`;
      }
    }

    drawBruce(ctx, {
      x: bruce.x,
      y: bruce.y,
      scale: 0.95,
      facing: bruce.chasing && bruce.targetX < bruce.x ? -1 : 1,
      mood: bruce.chasing ? "excited" : "happy",
      t,
      walkSpeed: walkSpd,
      lookTarget: ball,
    });

    // Tennis ball with ground shadow
    if (!ball.hiddenZone || ball.dragging) {
      ctx.fillStyle = "rgba(0,0,0,0.16)";
      ctx.beginPath();
      ctx.ellipse(ball.x, ball.y + 15, 13, 5, 0, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = "#CBE857";
      ctx.strokeStyle = "#2A2421";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(ball.x, ball.y, 15, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.strokeStyle = "#FFFDF8";
      ctx.lineWidth = 1.8;
      ctx.beginPath();
      ctx.arc(ball.x - 5, ball.y, 10, -0.8, 0.8);
      ctx.stroke();
    }

    if (phone) {
      phone.x = Math.max(12, w - 210);
      drawPhoneNotificationCanvas(ctx, phone.x, 58, phone.app, phone.text, t);
    }
    rafId = requestAnimationFrame(loop);
  };
  rafId = requestAnimationFrame(loop);

  return () => {
    finished = true;
    clearTimeout(tPhone);
    cancelAnimationFrame(rafId);
  };
}

function mountHomeBrush(stage) {
  stage.innerHTML = `
    <div class="canvas-hud-overlay">
      <span class="hud-chip" id="brush-hud">舒缓顺毛 0% · CHILL</span>
      <button class="btn-pill" id="btn-dryer-trap" type="button">HAIR DRYER（吹风机）</button>
    </div>
    <canvas class="scene-canvas" id="game-canvas"></canvas>
  `;
  const canvas = document.getElementById("game-canvas");
  const hudEl = document.getElementById("brush-hud");

  let progress = 0;
  let warning = false;
  let finished = false;
  let brush = { x: 180, y: 120, active: false, lastX: null, lastT: 0 };
  let sparkles = [];
  let rafId = null;

  const warnTimer = setInterval(() => {
    if (finished) return;
    warning = !warning;
    hudEl.textContent = warning
      ? `舒缓顺毛 ${Math.round(progress)}% · EARS FLAT 快停手！`
      : `舒缓顺毛 ${Math.round(progress)}% · CHILL 轻轻梳`;
    hudEl.style.color = warning ? "var(--danger)" : "var(--ink)";
  }, 2400);

  document.getElementById("btn-dryer-trap")?.addEventListener("click", () => {
    if (finished) return;
    finished = true;
    concludeActivity("home_brush", "fail", -13, "hazard");
  });

  canvas.addEventListener("pointerdown", (e) => {
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    brush.active = true;
    brush.x = p.x;
    brush.y = p.y;
    brush.lastX = p.x;
    brush.lastT = performance.now();
    canvas.setPointerCapture(e.pointerId);
  });

  canvas.addEventListener("pointermove", (e) => {
    if (finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    brush.x = p.x;
    brush.y = p.y;
    if (!brush.active && e.pointerType === "mouse" && e.buttons === 0) return;

    const now = performance.now();
    if (brush.lastX !== null) {
      const dist = Math.abs(p.x - brush.lastX);
      const speed = (dist / Math.max(16, now - brush.lastT)) * 1000;
      const nearDog = Math.abs(p.x - p.w * 0.5) < 110 && Math.abs(p.y - p.h * 0.62) < 95;
      if (nearDog && dist > 5) {
        if (warning || speed > 1450) {
          finished = true;
          concludeActivity("home_brush", "fail", -13, "hazard");
          return;
        }
        progress = Math.min(100, progress + Math.min(3.4, dist * 0.14));
        hudEl.textContent = `舒缓顺毛 ${Math.round(progress)}% · CHILL 轻轻梳`;
        sparkles.push({ x: p.x, y: p.y, life: 1 });
        if (progress >= 100) {
          finished = true;
          concludeActivity("home_brush", "win", 11, "hazard", 0);
          return;
        }
      }
    }
    brush.lastX = p.x;
    brush.lastT = now;
  });

  canvas.addEventListener("pointerup", () => { brush.active = false; });

  const loop = (now) => {
    if (finished || !document.body.contains(canvas)) return;
    const t = now / 1000;
    const { w, h, ctx } = fitCanvas(canvas);
    drawVillaInterior(ctx, w, h, t);

    // Smooth calm progress ring behind Bruce
    const cx = w * 0.5;
    const cy = h * 0.64;
    ctx.strokeStyle = "rgba(58,90,70,0.16)";
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.arc(cx, cy, 88, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = warning ? "#B4382A" : "#3A5A46";
    ctx.beginPath();
    ctx.arc(cx, cy, 88, -Math.PI / 2, -Math.PI / 2 + (Math.PI * 2 * progress) / 100);
    ctx.stroke();

    drawBruce(ctx, {
      x: cx,
      y: cy,
      scale: 1.32,
      mood: warning ? "warn" : progress > 72 ? "belly" : "happy",
      t,
      lookTarget: brush,
      brushGlow: brush.active && !warning ? 1 : 0,
    });

    // Golden sparkle fur particles
    for (let i = sparkles.length - 1; i >= 0; i -= 1) {
      const s = sparkles[i];
      s.y -= 0.9;
      s.life -= 0.035;
      if (s.life <= 0) { sparkles.splice(i, 1); continue; }
      ctx.fillStyle = `rgba(218, 165, 65, ${s.life})`;
      ctx.beginPath();
      ctx.arc(s.x, s.y, 4 * s.life, 0, Math.PI * 2);
      ctx.fill();
    }

    // Beechwood paddle brush following pointer
    ctx.save();
    ctx.translate(brush.x, brush.y);
    ctx.rotate(-0.35);
    ctx.fillStyle = "#C9986B";
    ctx.strokeStyle = "#2A2421";
    ctx.lineWidth = 2;
    roundRect(ctx, -18, -12, 36, 22, 10);
    ctx.fill();
    ctx.stroke();
    roundRect(ctx, 16, -4, 18, 8, 4);
    ctx.fill();
    ctx.stroke();
    ctx.restore();

    rafId = requestAnimationFrame(loop);
  };
  rafId = requestAnimationFrame(loop);

  return () => {
    finished = true;
    clearInterval(warnTimer);
    cancelAnimationFrame(rafId);
  };
}

function mountHomeRainVinyl(stage) {
  stage.innerHTML = `
    <div class="canvas-hud-overlay">
      <span class="hud-chip" id="rv-step">第 1 步：把毛巾 TOWEL 拖到布鲁斯身上擦爪</span>
    </div>
    <canvas class="scene-canvas" id="game-canvas"></canvas>
  `;
  const canvas = document.getElementById("game-canvas");
  const stepEl = document.getElementById("rv-step");

  let stageStep = 0; // 0: need towel, 1: need blanket, 2: tap vinyl
  let finished = false;
  let dragging = null;
  let towel = { x: 0, y: 0, homeX: 0.42, homeY: 0.87, used: false };
  let blanket = { x: 0, y: 0, homeX: 0.66, homeY: 0.87, used: false };
  let init = false;
  let rafId = null;

  canvas.addEventListener("pointerdown", (e) => {
    if (finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    // Check vinyl turntable area on left
    if (p.x >= p.w * 0.04 && p.x <= p.w * 0.04 + 92 && p.y >= p.h * 0.60 && p.y <= p.h * 0.60 + 82) {
      if (stageStep !== 2) {
        finished = true;
        concludeActivity("home_rain_vinyl", "fail", -12, "hazard");
        return;
      }
      finished = true;
      concludeActivity("home_rain_vinyl", "win", 12, "hazard", 0);
      return;
    }
    if (!towel.used && Math.hypot(p.x - towel.x, p.y - towel.y) < 38) {
      dragging = "towel";
      canvas.setPointerCapture(e.pointerId);
    } else if (!blanket.used && Math.hypot(p.x - blanket.x, p.y - blanket.y) < 38) {
      dragging = "blanket";
      canvas.setPointerCapture(e.pointerId);
    }
  });

  canvas.addEventListener("pointermove", (e) => {
    if (!dragging || finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    if (dragging === "towel") { towel.x = p.x; towel.y = p.y; }
    else { blanket.x = p.x; blanket.y = p.y; }
  });

  canvas.addEventListener("pointerup", (e) => {
    if (!dragging || finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    const overBruce = Math.hypot(p.x - p.w * 0.54, p.y - p.h * 0.64) < 95;
    if (overBruce) {
      if (dragging === "towel" && stageStep === 0) {
        towel.used = true;
        stageStep = 1;
        stepEl.textContent = "第 2 步：把小毛毯 BLANKET 拖给布鲁斯盖好";
        feedback("small", e.clientX, e.clientY);
      } else if (dragging === "blanket" && stageStep === 1) {
        blanket.used = true;
        stageStep = 2;
        stepEl.textContent = "第 3 步：点击左侧 VINYL 黑胶唱机放音乐！";
        feedback("small", e.clientX, e.clientY);
      } else {
        finished = true;
        concludeActivity("home_rain_vinyl", "fail", -12, "hazard");
        return;
      }
    }
    towel.x = p.w * towel.homeX; towel.y = p.h * towel.homeY;
    blanket.x = p.w * blanket.homeX; blanket.y = p.h * blanket.homeY;
    dragging = null;
  });

  const loop = (now) => {
    if (finished || !document.body.contains(canvas)) return;
    const t = now / 1000;
    const { w, h, ctx } = fitCanvas(canvas);
    if (!init) {
      init = true;
      towel.x = w * towel.homeX; towel.y = h * towel.homeY;
      blanket.x = w * blanket.homeX; blanket.y = h * blanket.homeY;
    }
    drawVillaInterior(ctx, w, h, t, { rain: true, spinVinyl: stageStep === 2 });
    drawPillTag(ctx, w * 0.05, h * 0.57, 78, 26, "VINYL", stageStep === 2 ? "#7F2334" : "#FFF", stageStep === 2 ? "#FFF" : "#1D2024");

    drawBruce(ctx, {
      x: w * 0.54,
      y: h * 0.64,
      scale: 1.25,
      mood: stageStep >= 2 ? "excited" : "happy",
      t,
      wetPaws: stageStep === 0,
      blanketOn: stageStep >= 2,
    });

    if (!towel.used) {
      ctx.save();
      ctx.translate(towel.x, towel.y);
      ctx.fillStyle = "#FFFDF8";
      ctx.strokeStyle = "#2A2421";
      ctx.lineWidth = 2;
      roundRect(ctx, -34, -18, 68, 36, 10);
      ctx.fill();
      ctx.stroke();
      drawPillTag(ctx, -28, -11, 56, 22, "TOWEL", "#EEF4EE");
      ctx.restore();
    }
    if (!blanket.used) {
      ctx.save();
      ctx.translate(blanket.x, blanket.y);
      ctx.fillStyle = "#D98074";
      ctx.strokeStyle = "#2A2421";
      ctx.lineWidth = 2;
      roundRect(ctx, -38, -18, 76, 36, 10);
      ctx.fill();
      ctx.stroke();
      drawPillTag(ctx, -33, -11, 66, 22, "BLANKET", "#FFF5F3");
      ctx.restore();
    }
    rafId = requestAnimationFrame(loop);
  };
  rafId = requestAnimationFrame(loop);

  return () => {
    finished = true;
    cancelAnimationFrame(rafId);
  };
}

function mountHomeKitchen(stage) {
  stage.innerHTML = `
    <div class="canvas-hud-overlay">
      <span class="hud-chip" id="kit-hud">备餐分拣 0 / 6 · 安全食材进碗</span>
    </div>
    <canvas class="scene-canvas" id="game-canvas"></canvas>
  `;
  const canvas = document.getElementById("game-canvas");
  const hudEl = document.getElementById("kit-hud");

  const foods = [
    { id: "CHICKEN", safe: true, color: "#E8AE72", rx: 0.16, ry: 0.84, used: false },
    { id: "ONION", safe: false, color: "#C683A8", rx: 0.30, ry: 0.84, used: false },
    { id: "PUMPKIN", safe: true, color: "#EC9342", rx: 0.44, ry: 0.84, used: false },
    { id: "GRAPE", safe: false, color: "#795695", rx: 0.58, ry: 0.84, used: false },
    { id: "EGG", safe: true, color: "#F7D060", rx: 0.72, ry: 0.84, used: false },
    { id: "CHOCO", safe: false, color: "#684434", rx: 0.86, ry: 0.84, used: false },
  ];
  foods.forEach((f) => { f.x = 0; f.y = 0; f.init = false; });

  let dragItem = null;
  let sorted = 0;
  let phone = null;
  let finished = false;
  let rafId = null;
  const phonePool = store.state.content?.phone_notifications || [{ app: "CHAT", text: "NEW MESSAGE · 99+" }];

  const tPhone = setTimeout(() => {
    if (!finished) {
      phone = { ...pickRandom(phonePool, { app: "CHAT", text: "NEW MESSAGE · 99+" }), x: 16, y: 58 };
      sfx.playPhoneBuzz();
    }
  }, 2200);

  canvas.addEventListener("pointerdown", (e) => {
    if (finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    if (phone && p.x >= phone.x && p.x <= phone.x + 196 && p.y >= phone.y && p.y <= phone.y + 54) {
      finished = true;
      concludeActivity("home_kitchen", "fail", -15, "phone");
      return;
    }
    const hit = foods.find((f) => !f.used && Math.hypot(p.x - f.x, p.y - f.y) < 34);
    if (hit) {
      dragItem = hit;
      canvas.setPointerCapture(e.pointerId);
    }
  });

  canvas.addEventListener("pointermove", (e) => {
    if (!dragItem || finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    dragItem.x = p.x;
    dragItem.y = p.y;
  });

  canvas.addEventListener("pointerup", (e) => {
    if (!dragItem || finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    const inBowl = Math.hypot(p.x - p.w * 0.30, p.y - p.h * 0.56) < 70;
    const inTrash = Math.hypot(p.x - p.w * 0.72, p.y - p.h * 0.56) < 70;

    if (inBowl || inTrash) {
      if ((dragItem.safe && inBowl) || (!dragItem.safe && inTrash)) {
        dragItem.used = true;
        sorted += 1;
        hudEl.textContent = `备餐分拣 ${sorted} / 6`;
        feedback("small", e.clientX, e.clientY);
        if (sorted >= 6) {
          finished = true;
          concludeActivity("home_kitchen", "win", 13, "hazard", 0);
          return;
        }
      } else {
        finished = true;
        concludeActivity("home_kitchen", "fail", -15, "hazard");
        return;
      }
    }
    dragItem.x = p.w * dragItem.rx;
    dragItem.y = p.h * dragItem.ry;
    dragItem = null;
  });

  const loop = (now) => {
    if (finished || !document.body.contains(canvas)) return;
    const t = now / 1000;
    const { w, h, ctx } = fitCanvas(canvas);
    drawVillaInterior(ctx, w, h, t);

    // Sleek travertine kitchen counter in foreground
    ctx.fillStyle = "#EFECE4";
    ctx.strokeStyle = "#2A2421";
    ctx.lineWidth = 2;
    roundRect(ctx, w * 0.06, h * 0.48, w * 0.88, h * 0.48, 22);
    ctx.fill();
    ctx.stroke();

    // Bruce peeking over counter watching ingredients!
    drawBruce(ctx, {
      x: w * 0.51,
      y: h * 0.42,
      scale: 0.92,
      mood: dragItem ? "excited" : "happy",
      t,
      lookTarget: dragItem || { x: w * 0.5, y: h * 0.75 },
    });

    // Glazed ceramic BRUCE bowl & brass TRASH bin
    ctx.fillStyle = "#FAF8F2";
    ctx.beginPath(); ctx.ellipse(w * 0.30, h * 0.57, 48, 18, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    drawPillTag(ctx, w * 0.30 - 48, h * 0.57 + 22, 96, 26, "BRUCE BOWL", "#EEF4EE");

    ctx.fillStyle = "#C5A86E";
    roundRect(ctx, w * 0.72 - 30, h * 0.57 - 18, 60, 36, 8); ctx.fill(); ctx.stroke();
    drawPillTag(ctx, w * 0.72 - 44, h * 0.57 + 22, 88, 26, "TRASH BIN", "#F8ECEA");

    foods.forEach((f) => {
      if (!f.init) {
        f.init = true;
        f.x = w * f.rx;
        f.y = h * f.ry;
      }
      if (f.used) return;
      ctx.save();
      ctx.fillStyle = f.color;
      ctx.strokeStyle = "#2A2421";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(f.x, f.y, 17, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      drawPillTag(ctx, f.x - 36, f.y + 18, 72, 22, f.id, "#FFFDF9");
      ctx.restore();
    });

    if (phone) {
      phone.x = Math.max(12, w - 210);
      drawPhoneNotificationCanvas(ctx, phone.x, 58, phone.app, phone.text, t);
    }
    rafId = requestAnimationFrame(loop);
  };
  rafId = requestAnimationFrame(loop);

  return () => {
    finished = true;
    clearTimeout(tPhone);
    cancelAnimationFrame(rafId);
  };
}

function mountHomeNap(stage) {
  stage.innerHTML = `
    <div class="canvas-hud-overlay">
      <span class="hud-chip" id="nap-hud">点窗帘拉下遮光，再点软垫拍松</span>
      <span class="hud-chip hidden" id="nap-timer">6s</span>
    </div>
    <canvas class="scene-canvas" id="game-canvas"></canvas>
  `;
  const canvas = document.getElementById("game-canvas");
  const hudEl = document.getElementById("nap-hud");
  const timerEl = document.getElementById("nap-timer");

  let shaded = false;
  let fluffed = false;
  let waitLeft = 6;
  let countdown = null;
  let activePhones = [];
  let finished = false;
  let rafId = null;
  const phonePool = store.state.content?.phone_notifications || [{ app: "WORK", text: "WORK CALL · NOW" }];

  const tryStartNap = () => {
    if (!shaded || !fluffed || countdown) return;
    hudEl.textContent = "午睡开始 · 忍住 6 秒钟不要点任何手机弹窗！";
    timerEl.classList.remove("hidden");
    timerEl.textContent = `${waitLeft}s`;

    [600, 2100, 3800].forEach((ms, idx) => {
      setTimeout(() => {
        if (finished) return;
        const pick = pickRandom(phonePool, { app: "WORK", text: "WORK CALL · NOW" });
        activePhones.push({ ...pick, y: 58 + idx * 62 });
        sfx.playPhoneBuzz();
      }, ms);
    });

    countdown = setInterval(() => {
      if (finished) return;
      waitLeft -= 1;
      timerEl.textContent = `${Math.max(0, waitLeft)}s`;
      if (waitLeft <= 0) {
        finished = true;
        clearInterval(countdown);
        concludeActivity("home_nap", "win", 11, "hazard", 0.12, "忍住没刷手机陪布鲁斯午睡");
      }
    }, 1000);
  };

  canvas.addEventListener("pointerdown", (e) => {
    if (finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    for (const ph of activePhones) {
      const px = Math.max(12, p.w - 210);
      if (p.x >= px && p.x <= px + 196 && p.y >= ph.y && p.y <= ph.y + 54) {
        finished = true;
        concludeActivity("home_nap", "fail", -14, "phone");
        return;
      }
    }
    if (!shaded && p.x >= p.w * 0.36 && p.y <= p.h * 0.56) {
      shaded = true;
      feedback("small", e.clientX, e.clientY);
      tryStartNap();
    } else if (!fluffed && Math.hypot(p.x - p.w * 0.52, p.y - p.h * 0.72) < 95) {
      fluffed = true;
      feedback("small", e.clientX, e.clientY);
      tryStartNap();
    }
  });

  const loop = (now) => {
    if (finished || !document.body.contains(canvas)) return;
    const t = now / 1000;
    const { w, h, ctx } = fitCanvas(canvas);
    drawVillaInterior(ctx, w, h, t, { shadeDrop: shaded ? 0.78 : 0.1 });

    if (!shaded) drawPillTag(ctx, w * 0.64 - 55, h * 0.24, 110, 30, "PULL SHADE", "#FFF");

    // Cozy linen floor cushion
    ctx.fillStyle = fluffed ? "#F5E4D3" : "#E5D8C8";
    ctx.strokeStyle = "#2A2421";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.ellipse(w * 0.52, h * 0.74, fluffed ? 72 : 62, 26, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    if (!fluffed) drawPillTag(ctx, w * 0.52 - 58, h * 0.80, 116, 26, "FLUFF CUSHION", "#FFF");

    drawBruce(ctx, {
      x: w * 0.50,
      y: h * 0.68,
      scale: 1.15,
      mood: shaded && fluffed ? "sleep" : "happy",
      t,
    });

    activePhones.forEach((ph) => {
      drawPhoneNotificationCanvas(ctx, Math.max(12, w - 210), ph.y, ph.app, ph.text, t);
    });
    rafId = requestAnimationFrame(loop);
  };
  rafId = requestAnimationFrame(loop);

  return () => {
    finished = true;
    clearInterval(countdown);
    cancelAnimationFrame(rafId);
  };
}

function mountStreetCafe(stage) {
  stage.innerHTML = `
    <div class="canvas-hud-overlay">
      <span class="hud-chip">拖动牵引绳带布鲁斯走进贴着 PAWS WELCOME 的店门！</span>
    </div>
    <canvas class="scene-canvas" id="game-canvas"></canvas>
  `;
  const canvas = document.getElementById("game-canvas");

  const flags = [true, true, false, false].sort(() => Math.random() - 0.5);
  const shops = [
    { name: "ROASTERY", ok: flags[0], roof: "#7F2334" },
    { name: "BAKERY", ok: flags[1], roof: "#3A5A46" },
    { name: "NOODLE BAR", ok: flags[2], roof: "#C88D3B" },
    { name: "BISTRO", ok: flags[3], roof: "#3B4A5A" },
  ];

  let bruce = { x: 0, y: 0, dragging: false, init: false };
  let finished = false;
  let rafId = null;

  canvas.addEventListener("pointerdown", (e) => {
    if (finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    if (Math.hypot(p.x - bruce.x, p.y - bruce.y) < 75) {
      bruce.dragging = true;
      canvas.setPointerCapture(e.pointerId);
    }
  });

  canvas.addEventListener("pointermove", (e) => {
    if (!bruce.dragging || finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    bruce.x = Math.max(40, Math.min(p.w - 40, p.x));
    bruce.y = Math.max(p.h * 0.42, Math.min(p.h * 0.88, p.y));
  });

  canvas.addEventListener("pointerup", (e) => {
    if (!bruce.dragging || finished) return;
    bruce.dragging = false;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    // Check if dropped at one of the 4 storefronts
    if (bruce.y <= p.h * 0.62) {
      const idx = Math.min(3, Math.max(0, Math.floor((bruce.x / p.w) * 4)));
      const shop = shops[idx];
      finished = true;
      if (shop.ok) {
        concludeActivity("street_cafe", "win", 14, "hazard", 0.22, "林荫宠友店大受夸赞");
      } else {
        concludeActivity("street_cafe", "fail", -18, "blocked");
      }
    }
  });

  const loop = (now) => {
    if (finished || !document.body.contains(canvas)) return;
    const t = now / 1000;
    const { w, h, ctx } = fitCanvas(canvas);
    if (!bruce.init) {
      bruce.init = true;
      bruce.x = w * 0.5;
      bruce.y = h * 0.80;
    }

    // Airy sunlit boulevard sky + stone sidewalk
    ctx.fillStyle = "#EFF5F6";
    ctx.fillRect(0, 0, w, h * 0.64);
    ctx.fillStyle = "#EAE4D7";
    ctx.fillRect(0, h * 0.64, w, h * 0.36);

    const slotW = w / 4;
    shops.forEach((s, i) => {
      const sx = i * slotW + 8;
      const sw = slotW - 16;
      const sy = h * 0.14;
      const sh = h * 0.50;

      // Boutique facade
      ctx.fillStyle = "#FAF7F0";
      ctx.strokeStyle = "#2A2421";
      ctx.lineWidth = 1.8;
      roundRect(ctx, sx, sy, sw, sh, 10);
      ctx.fill();
      ctx.stroke();

      // Awning
      ctx.fillStyle = s.roof;
      roundRect(ctx, sx - 2, sy, sw + 4, 34, 8);
      ctx.fill();
      ctx.fillStyle = "#FFFDF8";
      ctx.font = "700 11px -apple-system, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(s.name, sx + sw / 2, sy + 21);

      // Glass door
      ctx.fillStyle = "#DCECF2";
      roundRect(ctx, sx + sw * 0.2, sy + 46, sw * 0.6, sh - 52, 4);
      ctx.fill();
      ctx.stroke();

      // Door sticker: PAWS WELCOME vs NO DOGS
      drawPillTag(
        ctx,
        sx + sw / 2 - 44,
        sy + sh - 46,
        88,
        24,
        s.ok ? "PAWS WELCOME" : "NO DOGS",
        s.ok ? "#E4F1E8" : "#FBEAEA",
        s.ok ? "#2F573E" : "#B4382A",
        s.ok ? "#3A5A46" : "#B4382A"
      );

      // Stainless water bowl outside pet-friendly shops
      if (s.ok) {
        ctx.fillStyle = "#CBD5E1";
        ctx.beginPath();
        ctx.ellipse(sx + sw * 0.5, sy + sh + 8, 12, 5, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
      }
    });

    // Owner hand anchor + catenary leash to Bruce
    const handX = w * 0.5;
    const handY = h * 0.94;
    drawLeash(ctx, handX, handY, bruce.x + 24, bruce.y - 8);
    drawBruce(ctx, {
      x: bruce.x,
      y: bruce.y,
      scale: 0.96,
      mood: bruce.dragging ? "excited" : "happy",
      t,
      walkSpeed: bruce.dragging ? 1 : 0,
    });
    rafId = requestAnimationFrame(loop);
  };
  rafId = requestAnimationFrame(loop);

  return () => {
    finished = true;
    cancelAnimationFrame(rafId);
  };
}

function mountStreetWalk(stage) {
  stage.innerHTML = `
    <div class="canvas-hud-overlay">
      <span class="hud-chip" id="walk-hud">接花瓣 0 · 剩余 10s · 拖牵引绳左右避险</span>
    </div>
    <canvas class="scene-canvas" id="game-canvas"></canvas>
  `;
  const canvas = document.getElementById("game-canvas");
  const hudEl = document.getElementById("walk-hud");

  let bruceX = 0.5;
  let petals = 0;
  let leftSec = 10;
  let items = [];
  let phone = null;
  let finished = false;
  let rafId = null;
  const phonePool = store.state.content?.phone_notifications || [{ app: "CHAT", text: "NEW MESSAGE · 99+" }];

  const move = (e) => {
    if (finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    bruceX = Math.max(0.1, Math.min(0.9, p.x / p.w));
  };

  canvas.addEventListener("pointerdown", (e) => {
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    if (phone && p.x >= phone.x && p.x <= phone.x + 196 && p.y >= phone.y && p.y <= phone.y + 54) {
      finished = true;
      concludeActivity("street_walk", "fail", -14, "phone");
      return;
    }
    canvas.setPointerCapture(e.pointerId);
    move(e);
  });
  canvas.addEventListener("pointermove", (e) => {
    if (e.pointerType === "mouse" && e.buttons === 0) return;
    move(e);
  });

  const spawner = setInterval(() => {
    if (finished) return;
    const good = Math.random() < 0.56;
    items.push({
      rx: 0.1 + Math.random() * 0.8,
      ry: -0.05,
      good,
      label: good ? "LEAF" : pickRandom(["BEEP!", "SKEWER"]),
      speed: good ? 0.34 : 0.42,
    });
  }, 680);

  const secTimer = setInterval(() => {
    if (finished) return;
    leftSec -= 1;
    hudEl.textContent = `接落叶 ${petals} · 剩余 ${Math.max(0, leftSec)}s`;
    if (leftSec <= 0) {
      finished = true;
      concludeActivity("street_walk", "win", 12, "hazard", 0);
    }
  }, 1000);

  const tPhone = setTimeout(() => {
    if (!finished) {
      phone = { ...pickRandom(phonePool, { app: "CHAT", text: "NEW MESSAGE · 99+" }), x: 16, y: 58 };
      sfx.playPhoneBuzz();
    }
  }, 3000);

  let lastTs = performance.now();
  const loop = (now) => {
    if (finished || !document.body.contains(canvas)) return;
    const dt = Math.min(0.05, (now - lastTs) / 1000);
    lastTs = now;
    const t = now / 1000;
    const { w, h, ctx } = fitCanvas(canvas);

    // Lush sunlit avenue walkway
    ctx.fillStyle = "#DCEAD9";
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = "#F0EADE";
    ctx.fillRect(w * 0.08, 0, w * 0.84, h);

    // Moving path flagstones
    ctx.strokeStyle = "rgba(60, 56, 50, 0.12)";
    ctx.lineWidth = 1.5;
    for (let i = 0; i < 6; i += 1) {
      const ly = ((i * 75 + t * 130) % (h + 60)) - 30;
      ctx.beginPath();
      ctx.moveTo(w * 0.08, ly);
      ctx.lineTo(w * 0.92, ly);
      ctx.stroke();
    }

    const bx = w * bruceX;
    const by = h * 0.78;
    drawLeash(ctx, w * 0.5, h * 0.96, bx + 20, by - 6);
    drawBruce(ctx, { x: bx, y: by, scale: 0.9, mood: "excited", t, walkSpeed: 1 });

    for (let i = items.length - 1; i >= 0; i -= 1) {
      const it = items[i];
      it.ry += it.speed * dt;
      const ix = w * it.rx;
      const iy = h * it.ry;
      drawPillTag(
        ctx,
        ix - 34,
        iy - 14,
        68,
        28,
        it.label,
        it.good ? "#E7F4E8" : "#FBEAE8",
        it.good ? "#2F573E" : "#B4382A",
        it.good ? "#3A5A46" : "#B4382A"
      );

      if (Math.abs(iy - by) < 34 && Math.abs(ix - bx) < 48) {
        items.splice(i, 1);
        if (it.good) {
          petals += 1;
          hudEl.textContent = `接落叶 ${petals} · 剩余 ${Math.max(0, leftSec)}s`;
          feedback("small", ix, iy);
        } else {
          finished = true;
          concludeActivity("street_walk", "fail", -14, "hazard");
          return;
        }
      } else if (it.ry > 1.08) {
        items.splice(i, 1);
      }
    }

    if (phone) {
      phone.x = Math.max(12, w - 210);
      drawPhoneNotificationCanvas(ctx, phone.x, 58, phone.app, phone.text, t);
    }
    rafId = requestAnimationFrame(loop);
  };
  rafId = requestAnimationFrame(loop);

  return () => {
    finished = true;
    clearInterval(spawner);
    clearInterval(secTimer);
    clearTimeout(tPhone);
    cancelAnimationFrame(rafId);
  };
}

function mountStreetLawn(stage) {
  stage.innerHTML = `
    <div class="canvas-hud-overlay">
      <span class="hud-chip" id="lawn-hud">第 1 / 3 轮 · 拖布鲁斯找 WAGGING 友善狗友贴鼻</span>
    </div>
    <canvas class="scene-canvas" id="game-canvas"></canvas>
  `;
  const canvas = document.getElementById("game-canvas");
  const hudEl = document.getElementById("lawn-hud");

  let wave = 1;
  let dogs = [];
  let bruce = { x: 0, y: 0, dragging: false, init: false };
  let finished = false;
  let rafId = null;

  const setupWave = () => {
    dogs = [
      { label: "WAGGING", ok: true, color: "#E8A96B" },
      { label: "GROWLING", ok: false, color: "#7B8591" },
      { label: "GUARDING", ok: false, color: "#ECEAE4" },
    ].sort(() => Math.random() - 0.5).map((d, idx) => ({
      ...d,
      rx: 0.22 + idx * 0.28,
      ry: 0.36,
    }));
    hudEl.textContent = `第 ${wave} / 3 轮 · 拖布鲁斯找 WAGGING 友善狗友贴鼻`;
  };
  setupWave();

  canvas.addEventListener("pointerdown", (e) => {
    if (finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    if (Math.hypot(p.x - bruce.x, p.y - bruce.y) < 75) {
      bruce.dragging = true;
      canvas.setPointerCapture(e.pointerId);
    }
  });
  canvas.addEventListener("pointermove", (e) => {
    if (!bruce.dragging || finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    bruce.x = p.x;
    bruce.y = p.y;
  });
  canvas.addEventListener("pointerup", (e) => {
    if (!bruce.dragging || finished) return;
    bruce.dragging = false;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    const hit = dogs.find((d) => Math.hypot(p.x - p.w * d.rx, p.y - p.h * d.ry) < 62);
    if (hit) {
      if (!hit.ok) {
        finished = true;
        concludeActivity("street_lawn", "fail", -15, "hazard");
        return;
      }
      feedback("small", e.clientX, e.clientY);
      if (wave >= 3) {
        finished = true;
        concludeActivity("street_lawn", "win", 13, "hazard", 0.18, "在草坪交到贴鼻好朋友");
        return;
      }
      wave += 1;
      setupWave();
    }
    bruce.x = p.w * 0.5;
    bruce.y = p.h * 0.80;
  });

  const loop = (now) => {
    if (finished || !document.body.contains(canvas)) return;
    const t = now / 1000;
    const { w, h, ctx } = fitCanvas(canvas);
    if (!bruce.init) {
      bruce.init = true;
      bruce.x = w * 0.5;
      bruce.y = h * 0.80;
    }

    // Sunlit green private villa lawn
    const g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, "#CEE7BA");
    g.addColorStop(1, "#A8D492");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, w, h);

    dogs.forEach((d) => {
      const dx = w * d.rx;
      const dy = h * d.ry;
      ctx.save();
      ctx.translate(dx, dy);
      ctx.fillStyle = "rgba(0,0,0,0.12)";
      ctx.beginPath(); ctx.ellipse(0, 26, 26, 7, 0, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = d.color;
      ctx.strokeStyle = "#2A2421";
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(0, 0, 22, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      // Ears
      ctx.beginPath(); ctx.ellipse(-16, -12, 6, 12, -0.3, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      ctx.beginPath(); ctx.ellipse(16, -12, 6, 12, 0.3, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      ctx.restore();

      drawPillTag(
        ctx,
        dx - 44,
        dy + 30,
        88,
        24,
        d.label,
        d.ok ? "#E4F1E8" : "#FBEAEA",
        d.ok ? "#2F573E" : "#B4382A",
        d.ok ? "#3A5A46" : "#B4382A"
      );
    });

    drawLeash(ctx, w * 0.5, h * 0.96, bruce.x + 20, bruce.y - 8);
    drawBruce(ctx, { x: bruce.x, y: bruce.y, scale: 0.94, mood: "happy", t, walkSpeed: bruce.dragging ? 1 : 0 });
    rafId = requestAnimationFrame(loop);
  };
  rafId = requestAnimationFrame(loop);

  return () => {
    finished = true;
    cancelAnimationFrame(rafId);
  };
}

function mountStreetWindow(stage) {
  stage.innerHTML = `
    <div class="canvas-hud-overlay">
      <span class="hud-chip" id="win-hud">第 1 步：点选欢迎狗狗的橱窗，再拖清水饼干喂布鲁斯</span>
    </div>
    <canvas class="scene-canvas" id="game-canvas"></canvas>
  `;
  const canvas = document.getElementById("game-canvas");
  const hudEl = document.getElementById("win-hud");

  const windows = [
    { name: "FLOWER SHOP", tag: "DOG TREATS", ok: true },
    { name: "DESSERT BAR", tag: "NO PETS", ok: false },
    { name: "BAKERY", tag: "WATER BOWL", ok: true },
  ].sort(() => Math.random() - 0.5);

  let picked = false;
  let treat = { x: 0, y: 0, dragging: false, init: false };
  let finished = false;
  let rafId = null;

  canvas.addEventListener("pointerdown", (e) => {
    if (finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    if (!picked) {
      if (p.y >= p.h * 0.16 && p.y <= p.h * 0.62) {
        const idx = Math.min(2, Math.max(0, Math.floor((p.x / p.w) * 3)));
        const win = windows[idx];
        if (!win.ok) {
          finished = true;
          concludeActivity("street_window", "fail", -15, "blocked");
          return;
        }
        picked = true;
        hudEl.textContent = "第 2 步：把试吃点心拖给布鲁斯留影！";
        feedback("small", e.clientX, e.clientY);
      }
    } else if (Math.hypot(p.x - treat.x, p.y - treat.y) < 42) {
      treat.dragging = true;
      canvas.setPointerCapture(e.pointerId);
    }
  });

  canvas.addEventListener("pointermove", (e) => {
    if (!treat.dragging || finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    treat.x = p.x;
    treat.y = p.y;
  });

  canvas.addEventListener("pointerup", (e) => {
    if (!treat.dragging || finished) return;
    treat.dragging = false;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    if (Math.hypot(p.x - p.w * 0.5, p.y - p.h * 0.72) < 85) {
      finished = true;
      concludeActivity("street_window", "win", 11, "hazard", 0);
    } else {
      treat.x = p.w * 0.78;
      treat.y = p.h * 0.84;
    }
  });

  const loop = (now) => {
    if (finished || !document.body.contains(canvas)) return;
    const t = now / 1000;
    const { w, h, ctx } = fitCanvas(canvas);
    if (!treat.init) {
      treat.init = true;
      treat.x = w * 0.78;
      treat.y = h * 0.84;
    }

    ctx.fillStyle = "#F5F2EA";
    ctx.fillRect(0, 0, w, h);
    const slotW = w / 3;
    windows.forEach((win, i) => {
      const wx = i * slotW + 12;
      const ww = slotW - 24;
      ctx.fillStyle = "#DCEEF4";
      ctx.strokeStyle = "#2A2421";
      ctx.lineWidth = 1.8;
      roundRect(ctx, wx, h * 0.16, ww, h * 0.44, 14);
      ctx.fill();
      ctx.stroke();
      drawPillTag(ctx, wx + ww / 2 - 48, h * 0.22, 96, 24, win.name, "#232528", "#FFF");
      drawPillTag(
        ctx,
        wx + ww / 2 - 44,
        h * 0.48,
        88,
        24,
        win.tag,
        win.ok ? "#E4F1E8" : "#FBEAEA",
        win.ok ? "#2F573E" : "#B4382A",
        win.ok ? "#3A5A46" : "#B4382A"
      );
    });

    drawBruce(ctx, { x: w * 0.46, y: h * 0.74, scale: 1.05, mood: picked ? "excited" : "happy", t });

    if (picked) {
      ctx.fillStyle = "#E8C38E";
      ctx.strokeStyle = "#2A2421";
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(treat.x, treat.y, 18, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      drawPillTag(ctx, treat.x - 42, treat.y + 22, 84, 22, "DOG TREAT", "#FFF");
    }
    rafId = requestAnimationFrame(loop);
  };
  rafId = requestAnimationFrame(loop);

  return () => {
    finished = true;
    cancelAnimationFrame(rafId);
  };
}

function mountStreetBridge(stage) {
  stage.innerHTML = `
    <div class="canvas-hud-overlay">
      <span class="hud-chip" id="br-hud">水岸晚风 · 剩余 9s · 拖动布鲁斯躲避红圈噪音</span>
    </div>
    <canvas class="scene-canvas" id="game-canvas"></canvas>
  `;
  const canvas = document.getElementById("game-canvas");
  const hudEl = document.getElementById("br-hud");

  let bruce = { x: 0, y: 0, init: false };
  let leftSec = 9;
  let noiseZone = null; // { rx, label, timer }
  let lanterns = [0.22, 0.48, 0.76].map((rx) => ({ rx, lit: false }));
  let finished = false;
  let rafId = null;

  const move = (e) => {
    if (finished) return;
    const p = getCanvasCoords(canvas, e.clientX, e.clientY);
    bruce.x = Math.max(40, Math.min(p.w - 40, p.x));
    lanterns.forEach((l) => {
      if (!l.lit && Math.hypot(p.x - p.w * l.rx, p.y - p.h * 0.34) < 42) {
        l.lit = true;
        feedback("small", e.clientX, e.clientY);
      }
    });
  };
  canvas.addEventListener("pointerdown", (e) => { canvas.setPointerCapture(e.pointerId); move(e); });
  canvas.addEventListener("pointermove", (e) => { if (e.pointerType === "mouse" && e.buttons === 0) return; move(e); });

  const noiseLoop = setInterval(() => {
    if (finished) return;
    const rx = Math.random() < 0.5 ? 0.28 : 0.72;
    noiseZone = { rx, label: rx < 0.5 ? "LOUD SPEAKER" : "MOTORBIKE" };
    setTimeout(() => {
      if (finished) return;
      const w = canvas.getBoundingClientRect().width || 600;
      if (Math.abs(bruce.x - w * noiseZone.rx) < w * 0.20) {
        finished = true;
        concludeActivity("street_bridge", "fail", -16, "hazard");
        return;
      }
      noiseZone = null;
    }, 1500);
  }, 2900);

  const secTimer = setInterval(() => {
    if (finished) return;
    leftSec -= 1;
    hudEl.textContent = `水岸晚风 · 剩余 ${Math.max(0, leftSec)}s · 拖动布鲁斯躲避红圈噪音`;
    if (leftSec <= 0) {
      finished = true;
      concludeActivity("street_bridge", "win", 14, "hazard", 0.14, "夜幕水岸静享晚风");
    }
  }, 1000);

  const loop = (now) => {
    if (finished || !document.body.contains(canvas)) return;
    const t = now / 1000;
    const { w, h, ctx } = fitCanvas(canvas);
    if (!bruce.init) {
      bruce.init = true;
      bruce.x = w * 0.5;
      bruce.y = h * 0.74;
    }

    // Blue-rose twilight waterfront gradient
    const sky = ctx.createLinearGradient(0, 0, 0, h * 0.56);
    sky.addColorStop(0, "#314259");
    sky.addColorStop(1, "#70859E");
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, w, h * 0.56);

    // Rippling water + promenade
    ctx.fillStyle = "#3E546E";
    ctx.fillRect(0, h * 0.34, w, h * 0.24);
    ctx.fillStyle = "#E6E0D3";
    ctx.fillRect(0, h * 0.58, w, h * 0.42);

    // Glowing lanterns
    lanterns.forEach((l) => {
      const lx = w * l.rx;
      const ly = h * 0.34;
      ctx.fillStyle = l.lit ? "#FCD34D" : "rgba(255, 224, 150, 0.45)";
      ctx.beginPath(); ctx.arc(lx, ly, l.lit ? 16 : 11, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "rgba(252, 211, 77, 0.25)";
      ctx.beginPath(); ctx.ellipse(lx, ly + 42, 18, 6, 0, 0, Math.PI * 2); ctx.fill();
    });

    if (noiseZone) {
      const nx = w * noiseZone.rx;
      const pulse = 58 + Math.sin(t * 14) * 10;
      ctx.fillStyle = "rgba(180, 56, 42, 0.22)";
      ctx.strokeStyle = "#EF4444";
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(nx, h * 0.74, pulse, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      drawPillTag(ctx, nx - 52, h * 0.52, 104, 24, noiseZone.label, "#B4382A", "#FFF");
    }

    drawLeash(ctx, w * 0.5, h * 0.96, bruce.x + 18, bruce.y - 6);
    drawBruce(ctx, { x: bruce.x, y: bruce.y, scale: 0.96, mood: "happy", t });
    rafId = requestAnimationFrame(loop);
  };
  rafId = requestAnimationFrame(loop);

  return () => {
    finished = true;
    clearInterval(noiseLoop);
    clearInterval(secTimer);
    cancelAnimationFrame(rafId);
  };
}

const MOUNT_MAP = {
  home_hide_seek: mountHomeHideSeek,
  home_brush: mountHomeBrush,
  home_rain_vinyl: mountHomeRainVinyl,
  home_kitchen: mountHomeKitchen,
  home_nap: mountHomeNap,
  street_cafe: mountStreetCafe,
  street_walk: mountStreetWalk,
  street_lawn: mountStreetLawn,
  street_window: mountStreetWindow,
  street_bridge: mountStreetBridge,
};

export function renderSceneView(container, sceneType) {
  if (!container) return;
  if (cleanupActiveGame) {
    cleanupActiveGame();
    cleanupActiveGame = null;
  }

  if (store.isSulking()) {
    store.setView("shop");
    return;
  }

  const isHome = sceneType === "home";
  const list = isHome ? HOME_ACTIVITIES : STREET_ACTIVITIES;
  const activeId = store.state.activeActivityId || list[0].id;
  const currentAct = list.find((a) => a.id === activeId) || list[0];

  container.innerHTML = `
    <div class="scene-stage-shell">
      <div class="scene-top-strip">
        <div class="scene-title-block">
          <span class="pill-badge">${isHome ? "独栋小院" : "精品街区"}</span>
          <h2>${currentAct.title}</h2>
          <p>${currentAct.desc}</p>
        </div>
        <div class="scene-rewards-block">
          <span class="reward-chip">${currentAct.reward}</span>
          <span class="hazard-chip">${currentAct.hazard}</span>
          <button class="btn-pill" id="btn-scene-to-map" type="button">返回大地图</button>
        </div>
      </div>

      <div class="canvas-stage-box" id="canvas-stage-box"></div>

      <div class="scene-filmstrip" aria-label="切换陪伴活动">
        ${list.map((act) => `
          <button
            type="button"
            class="filmstrip-pill ${act.id === currentAct.id ? "is-active" : ""}"
            data-pick-act="${act.id}"
          >
            <strong>${act.title}</strong>
            <span>${act.reward}</span>
          </button>
        `).join("")}
      </div>
    </div>
  `;

  document.getElementById("btn-scene-to-map")?.addEventListener("click", () => {
    if (cleanupActiveGame) {
      cleanupActiveGame();
      cleanupActiveGame = null;
    }
    store.setView("map");
  });

  container.querySelectorAll("[data-pick-act]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      feedback("small", e.clientX, e.clientY);
      store.setView(sceneType, btn.getAttribute("data-pick-act"));
    });
  });

  const stageBox = document.getElementById("canvas-stage-box");
  if (stageBox && MOUNT_MAP[currentAct.id]) {
    cleanupActiveGame = MOUNT_MAP[currentAct.id](stageBox);
  }
}
