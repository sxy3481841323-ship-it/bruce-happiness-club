import { store } from "./state.js";
import { apiGetLeaderboard, apiRegister } from "./api.js";
import { renderMapView, stopMapLoop } from "./map.js";
import { renderSceneView, unmountSceneView } from "./activities.js";
import { renderShopView } from "./shop.js";
import { renderLeaderboardDrawer, renderTicker } from "./leaderboard.js";
import { sfx } from "./audio.js";

function validateNicknameClient(raw) {
  const nick = String(raw || "").trim();
  if (nick.length < 2 || nick.length > 12) {
    return { ok: false, error: "昵称长度需在 2 到 12 个字之间" };
  }
  if (/\s/.test(nick)) {
    return { ok: false, error: "昵称里请不要包含空格" };
  }
  if (!/[\u4e00-\u9fff]/.test(nick)) {
    return { ok: false, error: "昵称不能为纯数字或纯字母，必须至少包含 1 个中文字符" };
  }
  return { ok: true, nickname: nick };
}

function syncUiFromState(state) {
  const viewMap = document.getElementById("view-map");
  const viewScene = document.getElementById("view-scene");
  const viewShop = document.getElementById("view-shop");

  if (state.view !== "map") stopMapLoop();
  if (state.view !== "home" && state.view !== "street") unmountSceneView();

  viewMap.classList.toggle("hidden", state.view !== "map");
  viewScene.classList.toggle("hidden", state.view !== "home" && state.view !== "street");
  viewShop.classList.toggle("hidden", state.view !== "shop");

  if (state.view === "map") renderMapView(viewMap);
  else if (state.view === "home" || state.view === "street") renderSceneView(viewScene, state.view);
  else if (state.view === "shop") renderShopView(viewShop);
}

function setupOnboarding() {
  const modal = document.getElementById("onboarding-modal");
  const form = document.getElementById("onboarding-form");
  const errEl = document.getElementById("onboarding-error");
  const ownerOptions = document.querySelectorAll(".owner-option");

  ownerOptions.forEach((opt) => {
    opt.addEventListener("click", () => {
      ownerOptions.forEach((o) => o.classList.remove("selected"));
      opt.classList.add("selected");
      opt.querySelector("input").checked = true;
    });
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errEl.classList.add("hidden");

    const owner = document.querySelector(".owner-picker input[name='owner']:checked")?.value || "Alex";
    const nickRaw = document.getElementById("input-nickname").value;
    const pinRaw = document.getElementById("input-pin").value.trim();

    const check = validateNicknameClient(nickRaw);
    if (!check.ok) {
      errEl.textContent = check.error;
      errEl.classList.remove("hidden");
      return;
    }
    if (!/^\d{4}$/.test(pinRaw)) {
      errEl.textContent = "请输入 4 位数字暗号（如 2026）";
      errEl.classList.remove("hidden");
      return;
    }

    const submitBtn = document.getElementById("btn-enter-game");
    submitBtn.disabled = true;
    submitBtn.textContent = "正在搬进阳光小院……";

    try {
      const res = await apiRegister(owner, check.nickname, pinRaw);
      store.setPlayer({ ...res.player, pin: pinRaw });
      store.setLeaderboardAndTicker(res.leaderboard, res.ticker);
      modal.classList.add("hidden");
      sfx.playSuccess();
    } catch (err) {
      errEl.textContent = err.message || "进入失败，请重试";
      errEl.classList.remove("hidden");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "推开门 · 领布鲁斯回家";
    }
  });
}

function setupGlobalNav() {
  document.getElementById("btn-nav-map")?.addEventListener("click", () => store.setView("map"));
  document.getElementById("btn-nav-shop")?.addEventListener("click", () => store.setView("shop"));
  document.getElementById("btn-open-shop-banner")?.addEventListener("click", () => store.setView("shop"));

  const drawer = document.getElementById("leaderboard-drawer");
  document.getElementById("btn-nav-board")?.addEventListener("click", async () => {
    drawer.classList.remove("hidden");
    drawer.setAttribute("aria-hidden", "false");
    try {
      const res = await apiGetLeaderboard();
      store.setLeaderboardAndTicker(res.leaderboard, res.ticker);
    } catch (_) {}
  });

  document.getElementById("btn-close-board")?.addEventListener("click", () => {
    drawer.classList.add("hidden");
    drawer.setAttribute("aria-hidden", "true");
  });
  drawer?.addEventListener("click", (e) => {
    if (e.target === drawer) {
      drawer.classList.add("hidden");
      drawer.setAttribute("aria-hidden", "true");
    }
  });

  document.getElementById("btn-sound-toggle")?.addEventListener("click", (e) => {
    const muted = sfx.toggleMute();
    e.currentTarget.textContent = muted ? "静音" : "音效";
  });

  document.getElementById("btn-switch-player")?.addEventListener("click", () => {
    localStorage.removeItem("bruce_club_session_v1");
    drawer?.classList.add("hidden");
    drawer?.setAttribute("aria-hidden", "true");
    document.getElementById("input-nickname").value = "";
    document.getElementById("input-pin").value = "";
    document.getElementById("onboarding-error").classList.add("hidden");
    document.getElementById("onboarding-modal")?.classList.remove("hidden");
  });
}

async function boot() {
  setupOnboarding();
  setupGlobalNav();

  let lastView = "";
  let lastAct = "";
  let lastNick = "";
  let lastScore = null;

  store.subscribe((state) => {
    const viewChanged = state.view !== lastView || state.activeActivityId !== lastAct;
    const playerChanged = (state.player?.nickname || "") !== lastNick;
    const scoreChanged = (state.player?.happiness ?? null) !== lastScore;

    const player = state.player;
    const sulking = (player?.happiness ?? 100) < 80;
    document.body.classList.toggle("mood-sulk", sulking);
    document.body.classList.toggle("mood-happy", !sulking);

    if (player) {
      document.getElementById("hud-nickname").textContent = player.nickname;
      document.getElementById("hud-owner-tag").textContent = `${player.owner} & 布鲁斯`;
      document.getElementById("hud-owner-img").src = player.owner === "Meya"
        ? "./assets/img/owner_meya.jpg"
        : "./assets/img/owner_alex.jpg";
      document.getElementById("hud-bruce-img").src = sulking
        ? "./assets/img/bruce_sulk.jpg"
        : "./assets/img/bruce_happy.jpg";
      document.getElementById("hud-score").textContent = String(player.happiness);
      const moodEl = document.getElementById("hud-mood-pill");
      moodEl.className = `mood-pill ${sulking ? "mood-pill-sulk" : "mood-pill-happy"}`;
      moodEl.textContent = sulking ? "冷战锁定 (<80)" : "活力陪玩中";
      const myRow = (state.leaderboard || []).find((r) => r.nickname === player.nickname);
      document.getElementById("hud-rank").textContent = myRow ? `#${myRow.rank}` : "#--";
    }

    document.getElementById("anhedonia-banner").classList.toggle("hidden", !sulking);
    document.getElementById("btn-nav-shop").classList.toggle("hidden", !sulking);
    renderTicker(state.ticker);
    renderLeaderboardDrawer();

    if (viewChanged || playerChanged || (scoreChanged && (state.view === "shop" || state.view === "map"))) {
      lastView = state.view;
      lastAct = state.activeActivityId;
      lastNick = state.player?.nickname || "";
      lastScore = state.player?.happiness ?? null;
      syncUiFromState(state);
    }
  });

  try {
    const contentResp = await fetch("./data/content.json");
    const content = await contentResp.json();
    store.setContent(content);
  } catch (_) {}

  try {
    const lb = await apiGetLeaderboard();
    store.setLeaderboardAndTicker(lb.leaderboard, lb.ticker);
  } catch (_) {}

  const saved = store.loadSavedSession();
  if (saved && saved.nickname && saved.pin) {
    try {
      const res = await apiRegister(saved.owner || "Alex", saved.nickname, saved.pin);
      store.setPlayer({ ...res.player, pin: saved.pin });
      store.setLeaderboardAndTicker(res.leaderboard, res.ticker);
      document.getElementById("onboarding-modal").classList.add("hidden");
    } catch (_) {}
  }

  setInterval(async () => {
    try {
      const res = await apiGetLeaderboard();
      store.setLeaderboardAndTicker(res.leaderboard, res.ticker);
    } catch (_) {}
  }, 15000);
}

boot();
