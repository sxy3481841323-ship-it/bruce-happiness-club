import { store } from "./state.js";
import { feedback } from "./juice.js";

const MAP_SPOTS = [
  { id: "home", title: "布鲁斯的小院", sub: "进去陪陪他", x: 54, y: 79, playable: true },
  { id: "street", title: "林荫小街", sub: "一起散个步", x: 35, y: 69, playable: true },
  { id: "park", title: "树影公园", sub: "二期预告", x: 22, y: 50, playable: false },
  { id: "warehouse", title: "会员仓库", sub: "二期预告", x: 74, y: 46, playable: false },
  { id: "yacht", title: "白帆码头", sub: "二期预告", x: 82, y: 80, playable: false },
  { id: "nordic", title: "云端航线", sub: "二期预告", x: 18, y: 20, playable: false },
  { id: "california", title: "逐光航线", sub: "二期预告", x: 43, y: 17, playable: false },
  { id: "nz_swiss", title: "山海航线", sub: "二期预告", x: 76, y: 20, playable: false },
];

const PREVIEW_TITLES = {
  park: "树影公园",
  warehouse: "会员仓库",
  yacht: "白帆码头",
  nordic: "云端航线",
  california: "逐光航线",
  nz_swiss: "山海航线",
};

const WATER_ZONES = [
  { x0: 0.10, x1: 0.36, y0: 0.52, y1: 0.74 },
  { x0: 0.68, x1: 1.00, y0: 0.58, y1: 0.97 },
];

let rafId = null;
let closePreview = null;
let activeCleanup = null;
let activeStageEl = null;
let activeContainerEl = null;
let isSulkingState = false;

export function openPreviewModal(previewId) {
  const content = store.state.content;
  const modal = document.getElementById("generic-modal");
  const card = document.getElementById("generic-modal-card");
  if (!modal || !card || !PREVIEW_TITLES[previewId]) return;

  const item = (content?.remote_previews || []).find((p) => p.id === previewId);
  closePreview?.();
  const previousFocus = document.activeElement;

  card.innerHTML = `
    <span class="modal-pill-tag">二期 · 慢慢相见</span>
    <h2 class="modal-title" id="map-preview-title"></h2>
    <p class="modal-lead" id="map-preview-description"></p>
    <div class="soft-callout">
      <strong>二期将解锁的玩法亮点</strong>
      <ul id="map-preview-perks"></ul>
    </div>
    <div class="modal-footer-row">
      <span class="soft-hint">先在小院与街区走走，远方的风景慢慢相见</span>
      <button class="btn-pill btn-primary" id="btn-close-preview" type="button">返回大地图</button>
    </div>
  `;

  card.querySelector("#map-preview-title").textContent = PREVIEW_TITLES[previewId];
  card.querySelector("#map-preview-description").textContent =
    item?.teaser || "这段风景还在准备。下一次散步，和布鲁斯一起去。";

  const perksList = card.querySelector("#map-preview-perks");
  for (const perk of item?.planned_perks || []) {
    const li = document.createElement("li");
    li.textContent = perk;
    perksList.append(li);
  }

  modal.setAttribute("role", "dialog");
  modal.setAttribute("aria-modal", "true");
  modal.setAttribute("aria-labelledby", "map-preview-title");
  modal.setAttribute("aria-describedby", "map-preview-description");
  modal.classList.remove("hidden");

  const closeButton = card.querySelector("#btn-close-preview");
  const onKey = (event) => {
    if (event.key === "Escape") {
      event.preventDefault();
      closePreview?.();
    }
    if (event.key === "Tab") {
      event.preventDefault();
      closeButton?.focus();
    }
  };
  const onBackdrop = (event) => {
    if (event.target === modal) closePreview?.();
  };

  closePreview = () => {
    modal.classList.add("hidden");
    document.removeEventListener("keydown", onKey);
    modal.removeEventListener("click", onBackdrop);
    for (const name of ["role", "aria-modal", "aria-labelledby", "aria-describedby"]) {
      modal.removeAttribute(name);
    }
    closePreview = null;
    if (previousFocus?.isConnected) previousFocus.focus();
  };

  closeButton?.addEventListener("click", () => closePreview?.(), { once: true });
  modal.addEventListener("click", onBackdrop);
  document.addEventListener("keydown", onKey);
  closeButton?.focus();
}

export function stopMapLoop() {
  closePreview?.();
  if (rafId) {
    cancelAnimationFrame(rafId);
    rafId = null;
  }
  activeCleanup?.();
  activeCleanup = null;
  activeStageEl = null;
  activeContainerEl = null;
}

function updateSulkingPins(stageEl, sulking) {
  isSulkingState = sulking;
  stageEl.classList.toggle("is-sulk", sulking);
  stageEl.querySelectorAll(".wm-pin.is-playable .wm-pin-sub").forEach((el) => {
    const orig = el.getAttribute("data-orig-sub") || "";
    el.textContent = sulking ? "先哄好布鲁斯" : orig;
  });
}

export function renderMapView(container) {
  if (!container) return;
  const sulking = store.isSulking();

  if (activeContainerEl === container && activeStageEl?.isConnected) {
    updateSulkingPins(activeStageEl, sulking);
    return;
  }

  stopMapLoop();
  activeContainerEl = container;

  const pinsHtml = MAP_SPOTS.map((spot) => `
    <button
      type="button"
      class="wm-pin ${spot.playable ? "is-playable" : "is-preview"}"
      style="left:${spot.x}%;top:${spot.y}%;"
      data-spot="${spot.id}"
      data-playable="${spot.playable ? "1" : "0"}"
      data-x="${spot.x}"
      data-y="${spot.y}"
    >
      <span class="wm-pin-dot"></span>
      <span class="wm-pin-text">
        <span class="wm-pin-title">${spot.title}</span>
        <span class="wm-pin-sub" data-orig-sub="${spot.sub}">${
          spot.playable && sulking ? "先哄好布鲁斯" : spot.sub
        }</span>
      </span>
    </button>
  `).join("");

  container.innerHTML = `
    <div class="wm-wrap">
      <div class="wm-stage ${sulking ? "is-sulk" : ""}">
        <div class="wm-scroller">
          <div class="wm-camera">
            <img class="wm-base" src="./assets/img/world_map_v2.jpg" alt="布鲁斯的世界地图" />
            <canvas class="wm-fx" aria-hidden="true"></canvas>
            <div class="wm-pins">${pinsHtml}</div>
          </div>
        </div>
      </div>
      <p class="wm-hint">点地标进入<span class="wm-mobile-only"> · 手指可左右拖动地图</span></p>
    </div>
  `;

  const stageEl = container.querySelector(".wm-stage");
  const scrollerEl = container.querySelector(".wm-scroller");
  const cameraEl = container.querySelector(".wm-camera");
  const imgEl = container.querySelector(".wm-base");
  const canvas = container.querySelector(".wm-fx");
  activeStageEl = stageEl;
  isSulkingState = sulking;

  imgEl.addEventListener("error", () => {
    if (!imgEl.dataset.fallbackApplied) {
      imgEl.dataset.fallbackApplied = "1";
      imgEl.src = "./assets/img/world_map.jpg";
    }
  });

  // 手机竖屏初始定位到布鲁斯的小院 (54%) 居中
  requestAnimationFrame(() => {
    if (scrollerEl && scrollerEl.scrollWidth > scrollerEl.clientWidth) {
      scrollerEl.scrollLeft = Math.max(
        0,
        scrollerEl.scrollWidth * 0.54 - scrollerEl.clientWidth * 0.5,
      );
    }
  });

  const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
  let targetPx = 0;
  let targetPy = 0;
  let curPx = 0;
  let curPy = 0;
  let zooming = false;
  let zoomTimer = null;

  const onPointerMove = (e) => {
    if (reducedMotion || zooming || e.pointerType === "touch") return;
    const rect = stageEl.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const nx = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
    const ny = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
    targetPx = -nx * 10;
    targetPy = -ny * 8;
    cameraEl.classList.add("is-live-parallax");
  };

  const onPointerLeave = () => {
    targetPx = 0;
    targetPy = 0;
  };

  stageEl.addEventListener("pointermove", onPointerMove);
  stageEl.addEventListener("pointerleave", onPointerLeave);

  stageEl.querySelectorAll(".wm-pin").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      if (zooming) return;
      const id = btn.getAttribute("data-spot");
      const playable = btn.getAttribute("data-playable") === "1";
      feedback("small", e.clientX, e.clientY);

      if (!playable) {
        openPreviewModal(id);
        return;
      }
      if (store.isSulking()) {
        store.setView("shop");
        return;
      }

      if (reducedMotion) {
        store.setView(id);
        return;
      }

      zooming = true;
      const sx = btn.getAttribute("data-x") || "50";
      const sy = btn.getAttribute("data-y") || "50";
      cameraEl.classList.remove("is-live-parallax");
      cameraEl.classList.add("is-zooming");
      cameraEl.style.transformOrigin = `${sx}% ${sy}%`;
      cameraEl.style.transform = "scale(1.9)";
      zoomTimer = setTimeout(() => {
        zooming = false;
        store.setView(id);
      }, 600);
    });
  });

  // 2.5D 动态环境粒子状态
  const motes = Array.from({ length: 20 }, (_, i) => ({
    x: (i * 0.173) % 1,
    y: (i * 0.291) % 1,
    vy: 0.008 + (i % 5) * 0.003,
    r: 1.4 + (i % 3) * 0.8,
    phase: i * 0.9,
  }));

  const clouds = [
    { x: 0.15, y: 0.26, rx: 0.22, ry: 0.11, speed: 0.008 },
    { x: 0.55, y: 0.44, rx: 0.26, ry: 0.13, speed: 0.006 },
    { x: 0.82, y: 0.28, rx: 0.20, ry: 0.10, speed: 0.009 },
  ];

  const shimmers = Array.from({ length: 28 }, (_, i) => {
    const zone = WATER_ZONES[i % 2];
    return {
      zone,
      nx: zone.x0 + ((i * 0.37) % 1) * (zone.x1 - zone.x0),
      ny: zone.y0 + ((i * 0.61) % 1) * (zone.y1 - zone.y0),
      len: 10 + (i % 4) * 6,
      speed: 0.012 + (i % 3) * 0.004,
      phase: i * 1.1,
    };
  });

  const rainDrops = Array.from({ length: 75 }, (_, i) => ({
    x: (i * 0.137) % 1,
    y: (i * 0.241) % 1,
    len: 12 + (i % 4) * 5,
    speed: 0.55 + (i % 5) * 0.12,
  }));

  const ripples = Array.from({ length: 8 }, (_, i) => {
    const zone = WATER_ZONES[i % 2];
    return {
      x: zone.x0 + ((i * 0.41 + 0.1) % 0.85) * (zone.x1 - zone.x0),
      y: zone.y0 + ((i * 0.53 + 0.1) % 0.85) * (zone.y1 - zone.y0),
      t: i / 8,
    };
  });

  let prevTime = performance.now();
  const ctx = canvas.getContext("2d");

  const tick = (now) => {
    if (!stageEl.isConnected) return;
    const dt = Math.min(0.05, (now - prevTime) / 1000);
    prevTime = now;
    const t = now / 1000;

    if (!reducedMotion && !zooming) {
      curPx += (targetPx - curPx) * Math.min(1, dt * 7);
      curPy += (targetPy - curPy) * Math.min(1, dt * 7);
      const isActive = Math.abs(curPx) > 0.05 || Math.abs(curPy) > 0.05 || Math.abs(targetPx) > 0.05;
      cameraEl.style.transform = isActive
        ? `translate3d(${curPx.toFixed(2)}px, ${curPy.toFixed(2)}px, 0) scale(1.04)`
        : "scale(1.02)";
    }

    const rect = cameraEl.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(300, Math.round(rect.width));
    const h = Math.max(200, Math.round(rect.height));
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
    }

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);

    if (!reducedMotion) {
      // 1. 漂浮云影 (multiply)
      ctx.save();
      ctx.globalCompositeOperation = "multiply";
      for (const c of clouds) {
        c.x = (c.x + c.speed * dt) % 1.3;
        const cx = (c.x - 0.15) * w;
        const cy = c.y * h;
        const r = c.rx * w;
        const grad = ctx.createRadialGradient(cx, cy, r * 0.1, cx, cy, r);
        grad.addColorStop(0, "rgba(70, 88, 108, 0.08)");
        grad.addColorStop(1, "rgba(70, 88, 108, 0)");
        ctx.fillStyle = grad;
        ctx.save();
        ctx.translate(cx, cy);
        ctx.scale(1, c.ry / c.rx);
        ctx.beginPath();
        ctx.arc(0, 0, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
      ctx.restore();

      // 2. 水面波光 (screen)
      ctx.save();
      ctx.globalCompositeOperation = "screen";
      ctx.lineCap = "round";
      for (const s of shimmers) {
        s.nx += s.speed * dt;
        if (s.nx > s.zone.x1) s.nx = s.zone.x0;
        const sx = s.nx * w;
        const sy = s.ny * h + Math.sin(t * 1.8 + s.phase) * 1.5;
        const alpha = (isSulkingState ? 0.16 : 0.34) * (0.5 + 0.5 * Math.sin(t * 2.4 + s.phase));
        ctx.strokeStyle = `rgba(255, 252, 238, ${alpha.toFixed(3)})`;
        ctx.lineWidth = 1.4;
        ctx.beginPath();
        ctx.moveTo(sx, sy);
        ctx.lineTo(sx + s.len, sy);
        ctx.stroke();
      }

      if (!isSulkingState) {
        // 3. 阳光微尘
        for (const m of motes) {
          m.y -= m.vy * dt;
          if (m.y < 0) m.y = 1;
          const mx = (m.x + Math.sin(t * 0.9 + m.phase) * 0.01) * w;
          const my = m.y * h;
          const a = 0.22 + 0.22 * Math.sin(t * 2.1 + m.phase);
          ctx.fillStyle = `rgba(255, 246, 206, ${a.toFixed(3)})`;
          ctx.beginPath();
          ctx.arc(mx, my, m.r, 0, Math.PI * 2);
          ctx.fill();
        }
      }
      ctx.restore();

      // 4. 冷战雨丝与水域涟漪
      if (isSulkingState) {
        ctx.save();
        ctx.strokeStyle = "rgba(205, 224, 245, 0.36)";
        ctx.lineWidth = 1.1;
        for (const d of rainDrops) {
          d.y += d.speed * dt;
          d.x -= d.speed * 0.18 * dt;
          if (d.y > 1) {
            d.y = 0;
            d.x = (d.x + 0.37) % 1;
          }
          if (d.x < 0) d.x += 1;
          const rx = d.x * w;
          const ry = d.y * h;
          ctx.beginPath();
          ctx.moveTo(rx, ry);
          ctx.lineTo(rx - 3.5, ry + d.len);
          ctx.stroke();
        }
        for (const rp of ripples) {
          rp.t = (rp.t + dt * 0.65) % 1;
          const rad = 2 + rp.t * 14;
          const ra = (1 - rp.t) * 0.32;
          ctx.strokeStyle = `rgba(220, 236, 252, ${ra.toFixed(3)})`;
          ctx.beginPath();
          ctx.ellipse(rp.x * w, rp.y * h, rad, rad * 0.45, 0, 0, Math.PI * 2);
          ctx.stroke();
        }
        ctx.restore();
      }
    }

    rafId = requestAnimationFrame(tick);
  };

  rafId = requestAnimationFrame(tick);

  activeCleanup = () => {
    if (zoomTimer) clearTimeout(zoomTimer);
    stageEl.removeEventListener("pointermove", onPointerMove);
    stageEl.removeEventListener("pointerleave", onPointerLeave);
  };
}
