import { store } from "./state.js";
import { apiTriggerSwap, apiUpdateScore } from "./api.js";
import { mountLivingRoomHub } from "./hub3d/roomHub.js";
import { mountCoastalCafeHub } from "./scenes3d/cafeHub.js";

const PREVIEW_TITLES = {
  park: "树影公园",
  warehouse: "会员制大超市",
  yacht: "白帆游艇码头",
  nordic: "云端航线 · 北欧峡湾",
  california: "逐光航线 · 阳光海岸",
  nz_swiss: "山海航线 · 雪山牧场",
};

const GLOBAL_DESTINATIONS = [
  { id: "nordic", label: "北欧峡湾" },
  { id: "california", label: "阳光海岸" },
  { id: "nz_swiss", label: "雪山牧场" },
  { id: "yacht", label: "白帆游艇" },
];

let activeHub = null;
let activeContainer = null;
let activeCafe = null;
let activeCafeContainer = null;
let closeModalFn = null;
let cachedHubCopy = null;
let hubCopyPromise = null;

function loadHubDeepseek() {
  if (cachedHubCopy) return Promise.resolve(cachedHubCopy);
  if (!hubCopyPromise) {
    hubCopyPromise = fetch("./data/hub_deepseek.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((json) => {
        if (json) cachedHubCopy = json;
        return cachedHubCopy;
      })
      .catch(() => null);
  }
  return hubCopyPromise;
}

function pickRandom(arr, fallback = "") {
  if (!Array.isArray(arr) || !arr.length) return fallback;
  return arr[Math.floor(Math.random() * arr.length)];
}

function formatTemplate(tpl, vars) {
  return String(tpl || "").replace(/\{(\w+)\}/g, (_, k) => (vars[k] !== undefined ? vars[k] : ""));
}

function bindModalClose(modal, closeBtn) {
  closeModalFn?.();
  const prevFocus = document.activeElement;
  const onKey = (e) => {
    if (e.key === "Escape") {
      e.preventDefault();
      closeModalFn?.();
    }
  };
  const onBackdrop = (e) => {
    if (e.target === modal) closeModalFn?.();
  };
  closeModalFn = () => {
    modal.classList.add("hidden");
    document.removeEventListener("keydown", onKey);
    modal.removeEventListener("click", onBackdrop);
    closeModalFn = null;
    if (prevFocus?.isConnected) prevFocus.focus();
  };
  closeBtn?.addEventListener("click", () => closeModalFn?.(), { once: true });
  modal.addEventListener("click", onBackdrop);
  document.addEventListener("keydown", onKey);
  closeBtn?.focus();
}

export function openPreviewModal(previewId) {
  const content = store.state.content;
  const modal = document.getElementById("generic-modal");
  const card = document.getElementById("generic-modal-card");
  if (!modal || !card || !PREVIEW_TITLES[previewId]) return;

  const item = (content?.remote_previews || []).find((p) => p.id === previewId);
  card.innerHTML = `
    <span class="modal-pill-tag">${previewId === "warehouse" ? "传送目的地 · 会员制大超市" : "传送目的地 · 二期区域"}</span>
    <h2 class="modal-title" id="map-preview-title"></h2>
    <p class="modal-lead" id="map-preview-description"></p>
    <div class="soft-callout">
      <strong>传送解锁后可玩</strong>
      <p class="soft-hint" id="map-preview-wish" style="margin:6px 0 4px;"></p>
      <ul id="map-preview-perks"></ul>
    </div>
    <div class="modal-footer-row">
      <span class="soft-hint">${previewId === "warehouse" ? "放入超市 3D 模型后即可直接传送进入" : "放入对应 3D 场景后即可点击传送进入"}</span>
      <button class="btn-pill btn-primary" id="btn-close-preview" type="button">返回 3D 客厅</button>
    </div>
  `;
  card.querySelector("#map-preview-title").textContent = PREVIEW_TITLES[previewId];
  card.querySelector("#map-preview-description").textContent =
    item?.teaser || "这个 3D 区域正在装修中，很快就能一键传送过来陪布鲁斯玩！";
  const wishEl = card.querySelector("#map-preview-wish");
  const applyWish = (copy) => {
    const wish = copy?.destination_wishes?.[previewId];
    if (wishEl?.isConnected) {
      wishEl.textContent = wish ? `🐾 布鲁斯：${wish}` : "";
      wishEl.style.display = wish ? "" : "none";
    }
  };
  applyWish(cachedHubCopy);
  loadHubDeepseek().then(applyWish);
  const perksList = card.querySelector("#map-preview-perks");
  for (const perk of item?.planned_perks || []) {
    const li = document.createElement("li");
    li.textContent = perk;
    perksList.append(li);
  }
  modal.classList.remove("hidden");
  bindModalClose(modal, card.querySelector("#btn-close-preview"));
}

export function openGlobalTeleportModal() {
  const content = store.state.content;
  const modal = document.getElementById("generic-modal");
  const card = document.getElementById("generic-modal-card");
  if (!modal || !card) return;

  let activeId = GLOBAL_DESTINATIONS[0].id;
  card.innerHTML = `
    <span class="modal-pill-tag">✈️ 环球旅行相框墙 · 点击传送</span>
    <h2 class="modal-title">选择远方旅行目的地</h2>
    <div class="tp-tabs">
      ${GLOBAL_DESTINATIONS.map(
        (d, idx) => `<button type="button" class="tp-tab ${idx === 0 ? "is-active" : ""}" data-dest="${d.id}">${d.label}</button>`,
      ).join("")}
    </div>
    <p class="modal-lead" id="tp-dest-teaser"></p>
    <div class="soft-callout">
      <strong id="tp-dest-title"></strong>
      <p class="soft-hint" id="tp-dest-wish" style="margin:6px 0 4px;"></p>
      <ul id="tp-dest-perks"></ul>
    </div>
    <div class="modal-footer-row">
      <span class="soft-hint">二期接入对应 3D 景区模型后即可直接传送出发</span>
      <button class="btn-pill btn-primary" id="btn-close-preview" type="button">返回 3D 客厅</button>
    </div>
  `;

  const renderDest = (destId) => {
    activeId = destId;
    const item = (content?.remote_previews || []).find((p) => p.id === destId);
    card.querySelectorAll(".tp-tab").forEach((t) => {
      t.classList.toggle("is-active", t.getAttribute("data-dest") === activeId);
    });
    card.querySelector("#tp-dest-title").textContent = PREVIEW_TITLES[destId] || destId;
    card.querySelector("#tp-dest-teaser").textContent = item?.teaser || "";
    const wishEl = card.querySelector("#tp-dest-wish");
    const wish = cachedHubCopy?.destination_wishes?.[destId];
    if (wishEl) {
      wishEl.textContent = wish ? `🐾 布鲁斯：${wish}` : "";
      wishEl.style.display = wish ? "" : "none";
    }
    const ul = card.querySelector("#tp-dest-perks");
    ul.innerHTML = "";
    for (const perk of item?.planned_perks || []) {
      const li = document.createElement("li");
      li.textContent = perk;
      ul.append(li);
    }
  };

  card.querySelectorAll(".tp-tab").forEach((t) => {
    t.addEventListener("click", () => renderDest(t.getAttribute("data-dest")));
  });
  renderDest(activeId);
  loadHubDeepseek().then(() => {
    if (card.isConnected) renderDest(activeId);
  });

  modal.classList.remove("hidden");
  bindModalClose(modal, card.querySelector("#btn-close-preview"));
}

export function stopMapLoop() {
  closeModalFn?.();
  if (activeHub) {
    activeHub.destroy();
    activeHub = null;
  }
  activeContainer = null;
}

export function stopCafeLoop() {
  closeModalFn?.();
  if (activeCafe) {
    activeCafe.destroy();
    activeCafe = null;
  }
  activeCafeContainer = null;
}

async function settleScoreAndSwap(result, fallbackReason) {
  const latestPlayer = store.state.player;
  if (!latestPlayer) return null;

  const prevScore = latestPlayer.happiness;
  const delta = Number.isFinite(result?.delta) ? result.delta : 0;
  const nextScore = Math.max(0, Math.min(9999, Math.round(prevScore + delta)));

  let tickerMsg = "";
  if (prevScore >= 80 && nextScore < 80) {
    const templates = store.state.content?.ticker_templates?.collapse || [];
    tickerMsg = formatTemplate(pickRandom(templates), {
      player: latestPlayer.nickname,
      old_score: prevScore,
      new_score: nextScore,
    });
  }

  const res = await apiUpdateScore(
    latestPlayer.nickname,
    latestPlayer.pin,
    latestPlayer.owner,
    nextScore,
    tickerMsg,
  );
  store.setPlayer({ ...res.player, pin: latestPlayer.pin });
  store.setLeaderboardAndTicker(res.leaderboard, res.ticker);

  if (result?.outcome === "win" && result?.triggerSwapCandidate) {
    const swap = await apiTriggerSwap(latestPlayer.nickname, latestPlayer.pin, result.title || fallbackReason);
    if (Number.isFinite(swap?.newScore)) {
      store.setHappiness(swap.newScore);
    }
    if (swap?.leaderboard || swap?.ticker) {
      store.setLeaderboardAndTicker(swap.leaderboard, swap.ticker);
    }
    return {
      oldScore: swap.oldScore,
      newScore: swap.newScore,
      targetNickname: swap.targetNickname,
      topBonus: Boolean(swap.topBonus),
    };
  }
  return null;
}

export function renderMapView(container) {
  if (!container) return;
  const sulking = store.isSulking();
  const player = store.state.player;

  if (activeHub && activeContainer === container && container.querySelector(".hub3d-stage")) {
    activeHub.setContext({ happiness: player?.happiness ?? 100, content: store.state.content });
    activeHub.setSulking(sulking);
    return;
  }

  stopMapLoop();
  activeContainer = container;

  activeHub = mountLivingRoomHub(container, {
    sulking,
    happiness: player?.happiness ?? 100,
    content: store.state.content || {},
    getHappiness: () => store.state.player?.happiness ?? 100,
    onSettle: (result) => settleScoreAndSwap(result, "客厅陪玩"),
    onOpenShop: () => store.setView("shop"),
    onTeleportStreet: () => store.setView("street"),
    onTeleportWarehouse: () => openPreviewModal("warehouse"),
    onTeleportGlobal: () => openGlobalTeleportModal(),
  });
}

export function renderCafeView(container) {
  if (!container) return;
  const sulking = store.isSulking();
  const player = store.state.player;

  if (activeCafe && activeCafeContainer === container && container.querySelector(".hub3d-stage")) {
    activeCafe.setContext({ happiness: player?.happiness ?? 100, content: store.state.content });
    activeCafe.setSulking(sulking);
    return;
  }

  stopCafeLoop();
  activeCafeContainer = container;

  activeCafe = mountCoastalCafeHub(container, {
    sulking,
    happiness: player?.happiness ?? 100,
    content: store.state.content || {},
    getHappiness: () => store.state.player?.happiness ?? 100,
    onSettle: (result) => settleScoreAndSwap(result, "海岸咖啡馆探店"),
    onOpenShop: () => store.setView("shop"),
    onBackToHub: () => store.setView("map"),
    onTeleportWarehouse: () => openPreviewModal("warehouse"),
  });
}
