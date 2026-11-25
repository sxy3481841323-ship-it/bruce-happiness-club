import { store } from "./state.js";
import { apiTriggerSwap, apiUpdateScore } from "./api.js";
import { feedback } from "./juice.js";
import { getClipSources, THEATER_SCENES } from "./theater/clips.js";
import { mountTheater } from "./theater/stage.js";

let activeTheater = null;

function pickRandom(arr, fallback = "") {
  if (!Array.isArray(arr) || !arr.length) return fallback;
  return arr[Math.floor(Math.random() * arr.length)];
}

function formatTemplate(tpl, vars) {
  return String(tpl || "").replace(/\{(\w+)\}/g, (_, k) => (vars[k] !== undefined ? vars[k] : ""));
}

/**
 * Unmount any running fullscreen interactive theater stage cleanly.
 */
export function unmountSceneView() {
  if (activeTheater) {
    try {
      activeTheater.destroy();
    } catch (_) {}
    activeTheater = null;
  }
}

function launchSceneTheater(scene, autoplay) {
  const player = store.state.player;
  if (!player) return;

  unmountSceneView();
  activeTheater = mountTheater({
    activityId: scene.id,
    player,
    content: store.state.content || {},
    autoplay: Boolean(autoplay),
    async onSettle(result) {
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
        const swap = await apiTriggerSwap(latestPlayer.nickname, latestPlayer.pin, scene.title);
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
    },
    onExit() {
      unmountSceneView();
      if (store.isSulking()) {
        store.setView("shop");
      }
    },
  });
}

/**
 * Render the 5-scene Zone Activity Lobby ("home" -> 3 scenes, "street" -> 2 scenes).
 */
export function renderSceneView(container, sceneType) {
  if (!container) return;
  unmountSceneView();

  if (store.isSulking()) {
    store.setView("shop");
    return;
  }

  const isHome = sceneType === "home";
  const list = THEATER_SCENES.filter((s) => s.zone === (isHome ? "home" : "street"));
  const zoneTag = isHome ? "布鲁斯的小院 · 3 幕精选" : "林荫小街 · 2 幕精选";
  const zoneTitle = isHome ? "推门陪布鲁斯过一个下午" : "牵绳去林荫街区走一走";
  const zoneDesc =
    "全屏交互电影体验：自动入场运镜、关键时刻轻触介入，也可点「自动观影」沉浸观看（同样计分与触发换分）。";

  container.innerHTML = `
    <div class="lobby-shell">
      <div class="lobby-header">
        <div class="lobby-title-block">
          <span class="pill-badge">${zoneTag}</span>
          <h2>${zoneTitle}</h2>
          <p>${zoneDesc}</p>
        </div>
        <button class="btn-pill" id="btn-scene-to-map" type="button">返回大地图</button>
      </div>

      <div class="lobby-grid">
        ${list
          .map((scene, idx) => {
            const clips = getClipSources(scene);
            const swapTip = scene.swapProb > 0 ? ` · ${Math.round(scene.swapProb * 100)}% 触发换分` : "";
            return `
            <article class="lobby-card" data-act-card="${scene.id}">
              <div class="lobby-poster-wrap ${scene.tintClass}">
                <img
                  class="lobby-poster"
                  src="${clips.poster}"
                  data-fallback="${clips.posterFallback}"
                  alt="${scene.title}"
                />
              </div>
              <div class="lobby-card-top">
                <span class="lobby-index">0${idx + 1}</span>
                <span class="lobby-sub">${scene.subtitle}</span>
              </div>
              <h3>${scene.title}</h3>
              <p class="lobby-desc">${scene.desc}</p>
              <div class="lobby-chips">
                <span class="reward-chip">+${scene.win} 分${swapTip}</span>
                <span class="hazard-chip">踩雷 ${scene.fail} 分</span>
              </div>
              <div class="lobby-actions">
                <button class="btn-pill btn-primary" type="button" data-launch-act="${scene.id}" data-autoplay="false">
                  开启沉浸陪伴
                </button>
                <button class="btn-pill" type="button" data-launch-act="${scene.id}" data-autoplay="true">
                  自动观影
                </button>
              </div>
            </article>
          `;
          })
          .join("")}
      </div>
    </div>
  `;

  container.querySelectorAll(".lobby-poster").forEach((img) => {
    img.addEventListener("error", () => {
      if (!img.dataset.fallbackApplied) {
        img.dataset.fallbackApplied = "1";
        img.src = img.getAttribute("data-fallback") || "./assets/img/scene_home.jpg";
      }
    });
  });

  document.getElementById("btn-scene-to-map")?.addEventListener("click", () => {
    unmountSceneView();
    store.setView("map");
  });

  const byId = new Map(list.map((item) => [item.id, item]));
  container.querySelectorAll("[data-launch-act]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const scene = byId.get(btn.getAttribute("data-launch-act"));
      if (!scene) return;
      feedback("small", e.clientX, e.clientY);
      launchSceneTheater(scene, btn.getAttribute("data-autoplay") === "true");
    });
  });
}
