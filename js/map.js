import { store } from "./state.js";
import { feedback } from "./juice.js";
import { mountWorldMap3D } from "./map3d.js";

let activeMap = null;
let activeContainer = null;
let mapStage = null;
let hudObserver = null;
let closePreview = null;

// Keep destination IDs stable without putting regional names on the map or its
// preview dialogs. Content remains read-only and supplies the existing teasers.
const PREVIEW_TITLES = {
  park: "树影公园",
  warehouse: "会员仓库",
  yacht: "白帆码头",
  nordic: "云端航线",
  california: "逐光航线",
  nz_swiss: "山海航线",
};

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
  card.querySelector("#map-preview-description").textContent = item?.teaser || "这段风景还在准备。下一次散步，和布鲁斯一起去。";
  for (const perk of item?.planned_perks || []) {
    const li = document.createElement("li");
    li.textContent = perk;
    card.querySelector("#map-preview-perks").append(li);
  }
  modal.setAttribute("role", "dialog");
  modal.setAttribute("aria-modal", "true");
  modal.setAttribute("aria-labelledby", "map-preview-title");
  modal.setAttribute("aria-describedby", "map-preview-description");
  modal.classList.remove("hidden");
  const closeButton = card.querySelector("#btn-close-preview");
  const onKey = event => {
    if (event.key === "Escape") { event.preventDefault(); closePreview?.(); }
    if (event.key === "Tab") { event.preventDefault(); closeButton.focus(); }
  };
  closePreview = () => {
    modal.classList.add("hidden");
    document.removeEventListener("keydown", onKey);
    for (const name of ["role", "aria-modal", "aria-labelledby", "aria-describedby"]) modal.removeAttribute(name);
    closePreview = null;
    if (previousFocus?.isConnected) previousFocus.focus();
  };
  closeButton.addEventListener("click", () => closePreview?.(), { once: true });
  document.addEventListener("keydown", onKey);
  closeButton.focus();
}

export function stopMapLoop() {
  closePreview?.();
  hudObserver?.disconnect();
  hudObserver = null;
  activeMap?.destroy();
  activeMap = null;
  activeContainer = null;
  mapStage = null;
  document.body.classList.remove("world-map-open");
}

export function renderMapView(container) {
  if (!container) return;
  const sulking = store.isSulking();
  if (activeMap && activeContainer === container && mapStage?.isConnected) {
    activeMap.setSulking(sulking);
    updateMapNote(sulking);
    return;
  }
  stopMapLoop();
  document.body.classList.add("world-map-open");
  container.innerHTML = `<div class="world-stage world-stage-3d">
    <aside class="world-map-note" data-world-map-obstacle>
      <strong>布鲁斯的小小世界</strong>
      <p class="world-map-caption"></p>
      <button class="btn-pill world-map-shop hidden" type="button">去哄哄他</button>
    </aside>
  </div>`;
  activeContainer = container;
  mapStage = container.querySelector(".world-stage-3d");
  activeMap = mountWorldMap3D(mapStage, {
    sulking,
    onSelectPlayable(id) {
      if (store.isSulking()) { activeMap?.setSulking(true); return; }
      feedback("small", innerWidth / 2, innerHeight / 2);
      store.setView(id);
    },
    onSelectPreview: openPreviewModal,
  });
  mapStage.querySelector(".world-map-shop").addEventListener("click", () => store.setView("shop"));
  updateMapNote(sulking);
  const reserveHud = () => {
    if (!mapStage) return;
    const hud = document.querySelector(".hud-bar");
    const hudBottom = hud ? hud.getBoundingClientRect().bottom + 14 : 24;
    mapStage.style.setProperty("--world-map-safe-top", `${Math.ceil(hudBottom)}px`);
    const note = mapStage.querySelector(".world-map-note");
    mapStage.style.setProperty("--world-map-safe-bottom", `${Math.ceil(note.getBoundingClientRect().height + 44)}px`);
  };
  reserveHud();
  if (typeof ResizeObserver !== "undefined") {
    hudObserver = new ResizeObserver(reserveHud);
    const hud = document.querySelector(".hud-bar");
    if (hud) hudObserver.observe(hud);
    hudObserver.observe(mapStage.querySelector(".world-map-note"));
  }
}

function updateMapNote(sulking) {
  if (!mapStage) return;
  mapStage.querySelector(".world-map-caption").textContent = sulking
    ? "细雨来了。先哄好布鲁斯，再一起出门。"
    : "点一处建筑，陪他去走走。";
  mapStage.querySelector(".world-map-shop").classList.toggle("hidden", !sulking);
}
