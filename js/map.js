import { store } from "./state.js";
import { apiTriggerSwap, apiUpdateScore } from "./api.js";
import { mountLivingRoomHub } from "./hub3d/roomHub.js";
import { mountCoastalCafeHub } from "./scenes3d/cafeHub.js";
import { mountWarehouseHub } from "./scenes3d/warehouseHub.js";
import { mountYachtHub, preloadYachtAssets } from "./scenes3d/yachtHub.js";

const PREVIEW_TITLES = {
  park: "树影公园",
  warehouse: "ELOWEN · 有机市集",
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
let activeWarehouse = null;
let activeWarehouseContainer = null;
let activeYacht = null;
let activeYachtContainer = null;
let savedPenthouseAnchor = null;
let yachtAutoIntroPending = true;
let closeModalFn = null;
let cachedHubCopy = null;
let hubCopyPromise = null;
let lastSincerityAt = 0;
let lastLuckyAt = 0;

async function applyLuckyBonus(rawBonus) {
  const bonus = [8, 18, 28].includes(Number(rawBonus)) ? Number(rawBonus) : 8;
  const now = Date.now();
  if (now - lastLuckyAt < 12000) return null;
  const player = store.state.player;
  if (!player) return null;
  lastLuckyAt = now;
  const nextScore = Math.max(0, Math.min(9999, Math.round(player.happiness + bonus)));
  const tickerMsg = `${player.nickname} 与布鲁斯在夕照海平线捕捉到划落流星 · 幸运时刻 +${bonus}`;
  try {
    const res = await apiUpdateScore(player.nickname, player.pin, player.owner, nextScore, tickerMsg);
    store.setPlayer({ ...res.player, pin: player.pin });
    store.setLeaderboardAndTicker(res.leaderboard, res.ticker);
    return { bonus, newScore: res.player.happiness };
  } catch (_) {
    return null;
  }
}

async function applyAiSincerityDelta(rawDelta) {
  const delta = Math.max(-1, Math.min(3, Math.round(Number(rawDelta) || 0)));
  if (!delta) return 0;
  const now = Date.now();
  if (delta > 0 && now - lastSincerityAt < 20000) return 0;
  const player = store.state.player;
  if (!player) return 0;
  if (delta > 0) lastSincerityAt = now;
  const nextScore = Math.max(0, Math.min(9999, Math.round(player.happiness + delta)));
  try {
    const res = await apiUpdateScore(player.nickname, player.pin, player.owner, nextScore, "");
    store.setPlayer({ ...res.player, pin: player.pin });
    store.setLeaderboardAndTicker(res.leaderboard, res.ticker);
    return delta;
  } catch (_) {
    return 0;
  }
}

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
    <span class="modal-pill-tag">${previewId === "warehouse" ? "传送目的地 · ELOWEN 有机市集" : "传送目的地 · 二期区域"}</span>
    <h2 class="modal-title" id="map-preview-title"></h2>
    <p class="modal-lead" id="map-preview-description"></p>
    <div class="soft-callout">
      <strong>传送解锁后可玩</strong>
      <p class="soft-hint" id="map-preview-wish" style="margin:6px 0 4px;"></p>
      <ul id="map-preview-perks"></ul>
    </div>
    <div class="modal-footer-row">
      <span class="soft-hint">${previewId === "warehouse" ? "点击卡片特写即可直接传送进入" : "放入对应 3D 场景后即可点击传送进入"}</span>
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
      <span class="soft-hint">可从二楼相框查看远途航线，或直达私人柚木泊位</span>
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <button class="btn-pill hidden" id="btn-launch-yacht-modal" type="button">启程前往白帆泊位 →</button>
        <button class="btn-pill btn-primary" id="btn-close-preview" type="button">返回 3D 客厅</button>
      </div>
    </div>
  `;

  const launchYachtBtn = card.querySelector("#btn-launch-yacht-modal");
  const renderDest = (destId) => {
    activeId = destId;
    const item = (content?.remote_previews || []).find((p) => p.id === destId);
    card.querySelectorAll(".tp-tab").forEach((t) => {
      t.classList.toggle("is-active", t.getAttribute("data-dest") === activeId);
    });
    launchYachtBtn?.classList.toggle("hidden", destId !== "yacht");
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

  launchYachtBtn?.addEventListener("click", () => {
    closeModalFn?.();
    if (activeHub?.departToYacht) {
      activeHub.departToYacht();
    } else {
      yachtAutoIntroPending = true;
      preloadYachtAssets().then(() => store.setView("yacht")).catch(() => {});
    }
  });

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

export function stopWarehouseLoop() {
  closeModalFn?.();
  if (activeWarehouse) {
    activeWarehouse.destroy();
    activeWarehouse = null;
  }
  activeWarehouseContainer = null;
}

export function stopYachtLoop() {
  closeModalFn?.();
  if (activeYacht) {
    activeYacht.destroy();
    activeYacht = null;
  }
  activeYachtContainer = null;
}

async function settleScoreAndSwap(result, fallbackReason) {
  const latestPlayer = store.state.player;
  if (!latestPlayer) return null;

  const prevScore = latestPlayer.happiness;
  const delta = Number.isFinite(result?.delta) ? result.delta : 0;
  const nextScore = Math.max(0, Math.min(9999, Math.round(prevScore + delta)));

  let tickerMsg = typeof result?.tickerMsg === "string" ? result.tickerMsg : "";
  if (!tickerMsg && prevScore >= 80 && nextScore < 80) {
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

  const restoreAnchor = savedPenthouseAnchor;
  savedPenthouseAnchor = null;

  activeHub = mountLivingRoomHub(container, {
    sulking,
    happiness: player?.happiness ?? 100,
    player,
    content: store.state.content || {},
    restoreAnchor,
    getHappiness: () => store.state.player?.happiness ?? 100,
    onSettle: (result) => settleScoreAndSwap(result, "客厅陪玩"),
    onSincerityDelta: (delta) => applyAiSincerityDelta(delta),
    onLuckyBonus: (bonus) => applyLuckyBonus(bonus),
    onOpenShop: () => store.setView("shop"),
    onTeleportStreet: () => store.setView("street"),
    onTeleportWarehouse: () => store.setView("warehouse"),
    onSavePenthouseAnchor: (anchor) => {
      savedPenthouseAnchor = anchor;
    },
    onPreloadYacht: (o) => preloadYachtAssets(o),
    onTeleportYacht: () => {
      yachtAutoIntroPending = true;
      store.setView("yacht");
    },
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
    player,
    content: store.state.content || {},
    getHappiness: () => store.state.player?.happiness ?? 100,
    onSettle: (result) => settleScoreAndSwap(result, "海岸咖啡馆探店"),
    onSincerityDelta: (delta) => applyAiSincerityDelta(delta),
    onOpenShop: () => store.setView("shop"),
    onBackToHub: () => store.setView("map"),
    onTeleportWarehouse: () => store.setView("warehouse"),
  });
}

export function renderWarehouseView(container) {
  if (!container) return;
  const sulking = store.isSulking();
  const player = store.state.player;

  if (activeWarehouse && activeWarehouseContainer === container && container.querySelector(".hub3d-stage")) {
    activeWarehouse.setContext({ happiness: player?.happiness ?? 100, content: store.state.content });
    activeWarehouse.setSulking(sulking);
    return;
  }

  stopWarehouseLoop();
  activeWarehouseContainer = container;

  activeWarehouse = mountWarehouseHub(container, {
    sulking,
    happiness: player?.happiness ?? 100,
    player,
    content: store.state.content || {},
    getHappiness: () => store.state.player?.happiness ?? 100,
    onSettle: (result) => settleScoreAndSwap(result, "ELOWEN 有机市集备膳"),
    onSincerityDelta: (delta) => applyAiSincerityDelta(delta),
    onOpenShop: () => store.setView("shop"),
    onBackToHub: () => store.setView("map"),
    onTeleportStreet: () => store.setView("street"),
  });
}

export function renderYachtView(container) {
  if (!container) return;
  const sulking = store.isSulking();
  const player = store.state.player;

  if (activeYacht && activeYachtContainer === container && container.querySelector(".hub3d-stage")) {
    activeYacht.setContext({ happiness: player?.happiness ?? 100, content: store.state.content });
    activeYacht.setSulking(sulking);
    return;
  }

  stopYachtLoop();
  activeYachtContainer = container;
  const autoStartIntro = yachtAutoIntroPending;
  yachtAutoIntroPending = false;

  activeYacht = mountYachtHub(container, {
    sulking,
    happiness: player?.happiness ?? 100,
    player,
    content: store.state.content || {},
    autoStartIntro,
    getHappiness: () => store.state.player?.happiness ?? 100,
    onSettle: (result) => settleScoreAndSwap(result, "白帆游艇泊位时光"),
    onSincerityDelta: (delta) => applyAiSincerityDelta(delta),
    onLuckyBonus: (bonus) => applyLuckyBonus(bonus),
    onOpenShop: () => store.setView("shop"),
    onBackToHub: () => store.setView("map"),
    onTeleportStreet: () => store.setView("street"),
    onTeleportWarehouse: () => store.setView("warehouse"),
  });
}
