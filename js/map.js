import { store } from "./state.js";
import { feedback } from "./juice.js";
import { drawWorldAtlas, fitCanvas, WORLD_HOTSPOTS } from "./renderer.js";

let mapRafId = null;

export function openPreviewModal(previewId) {
  const content = store.state.content;
  const modal = document.getElementById("generic-modal");
  const card = document.getElementById("generic-modal-card");
  if (!content || !modal || !card) return;

  const list = content.remote_previews || [];
  const item = list.find((p) => p.id === previewId) || list[0];
  if (!item) return;

  const perksHtml = (item.planned_perks || [])
    .map((perk) => `<li>${perk}</li>`)
    .join("");

  card.innerHTML = `
    <span class="modal-pill-tag">${item.subtitle || "二期航线预告"}</span>
    <h2 class="modal-title">${item.title}</h2>
    <p class="modal-lead">${item.teaser}</p>
    <div class="soft-callout">
      <strong>二期将解锁的玩法亮点</strong>
      <ul>${perksHtml}</ul>
    </div>
    <div class="modal-footer-row">
      <span class="soft-hint">一期先在独栋小院与街区冲榜，远方航线随后开放</span>
      <button class="btn-pill btn-primary" id="btn-close-preview" type="button">返回大地图</button>
    </div>
  `;
  modal.classList.remove("hidden");
  document.getElementById("btn-close-preview")?.addEventListener("click", () => {
    modal.classList.add("hidden");
  });
}

export function stopMapLoop() {
  if (mapRafId) {
    cancelAnimationFrame(mapRafId);
    mapRafId = null;
  }
}

export function renderMapView(container) {
  stopMapLoop();
  if (!container) return;
  const sulking = store.isSulking();

  const pinsHtml = WORLD_HOTSPOTS.map((pin) => `
    <button
      type="button"
      class="world-pin ${pin.playable ? "is-playable" : "is-preview"}"
      style="left:${pin.x * 100}%;top:${pin.y * 100}%;"
      data-spot="${pin.id}"
    >
      <span class="pin-pulse"></span>
      <span class="pin-full">${pin.label}${pin.playable ? (sulking ? " · 冷战中" : " · 去陪玩") : ""}</span>
      <span class="pin-short">${pin.shortLabel}</span>
    </button>
  `).join("");

  container.innerHTML = `
    <div class="world-stage">
      <canvas id="world-atlas-canvas" class="world-canvas" aria-label="手绘世界互动地图"></canvas>
      <div class="world-pins-layer">${pinsHtml}</div>
      <div class="world-floating-dock">
        <button type="button" class="dock-pill dock-primary" data-spot="home">
          <span class="dock-dot"></span>
          <span>进入独栋小院（5 个互动）</span>
        </button>
        <button type="button" class="dock-pill dock-primary" data-spot="street">
          <span class="dock-dot"></span>
          <span>牵绳逛街区（5 个互动）</span>
        </button>
        <button type="button" class="dock-pill" data-spot="yacht">
          <span>游艇派对 · 二期预告</span>
        </button>
        <button type="button" class="dock-pill" data-spot="nordic">
          <span>全球 4 地航线 · 预告</span>
        </button>
      </div>
    </div>
  `;

  const canvas = document.getElementById("world-atlas-canvas");
  const startMs = performance.now();

  const frame = (now) => {
    if (!document.body.contains(canvas)) {
      mapRafId = null;
      return;
    }
    const t = (now - startMs) / 1000;
    const { w, h, ctx } = fitCanvas(canvas);
    drawWorldAtlas(ctx, w, h, t, store.isSulking());
    mapRafId = requestAnimationFrame(frame);
  };
  mapRafId = requestAnimationFrame(frame);

  container.querySelectorAll("[data-spot]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const spot = btn.getAttribute("data-spot");
      feedback("small", e.clientX || window.innerWidth / 2, e.clientY || 260);
      if (spot === "home" || spot === "street") {
        stopMapLoop();
        if (store.isSulking()) {
          store.setView("shop");
          return;
        }
        store.setView(spot);
      } else {
        openPreviewModal(spot);
      }
    });
  });
}
