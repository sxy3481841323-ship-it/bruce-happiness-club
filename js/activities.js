import { store } from "./state.js";
import { apiTriggerSwap, apiUpdateScore } from "./api.js";
import { feedback } from "./juice.js";
import { mountCinematicStage } from "./cinematic/index.js";

const HOME_ACTIVITIES = [
  {
    id: "home_brush",
    title: "露台阳光顺毛",
    subtitle: "窗边 · 午后",
    desc: "低机位特写下用木柄梳顺毛，看到布鲁斯飞机耳预警立刻松手，别碰吹风机也别刷手机。",
    reward: "+11 分",
    hazard: "太急 / 吹风机 -13",
  },
  {
    id: "home_rain_vinyl",
    title: "雨窗擦爪听黑胶",
    subtitle: "客厅 · 雨天",
    desc: "雨滴敲打落地窗，依次为布鲁斯擦干湿爪、披上毛毯，再落下黑胶唱针进入暖光陪听。",
    reward: "+12 分",
    hazard: "顺序搞反 -12",
  },
  {
    id: "home_hide_seek",
    title: "客厅抛球寻宝",
    subtitle: "客厅 · 阳光",
    desc: "抛出网球看布鲁斯短腿狂奔嗅探叼回，全程跟拍它的小动作，忍住别点角落手机弹窗。",
    reward: "+12 分 · 12% 触发换分",
    hazard: "点手机 / 音箱 -14",
  },
  {
    id: "home_kitchen",
    title: "岛台手作鲜食",
    subtitle: "厨房 · 备餐",
    desc: "挑出清脆苹果送进 BRUCE 陶瓷碗，避开对狗狗有毒的葡萄和桌面分心通知。",
    reward: "+13 分",
    hazard: "误喂葡萄 / 分心 -15",
  },
  {
    id: "home_nap",
    title: "庭院午睡放空",
    subtitle: "庭院 · 午睡",
    desc: "拉下遮阳帘、拍松靠垫，伴随呼吸起伏安静守着它打盹，不要打扰也不要开吸尘器。",
    reward: "+11 分 · 12% 触发换分",
    hazard: "吸尘器 / 刷手机 -14",
  },
];

const STREET_ACTIVITIES = [
  {
    id: "street_cafe",
    title: "林荫街角探店",
    subtitle: "街角 · 午后",
    desc: "牵着皮质牵引绳走过精品玻璃橱窗，看清门贴 PAWS WELCOME 与 NO DOGS 再决定进哪家。",
    reward: "+14 分 · 22% 触发换分",
    hazard: "硬闯禁入店 -18",
  },
  {
    id: "street_walk",
    title: "绿道晨间漫步",
    subtitle: "绿道 · 晨光",
    desc: "跟拍布鲁斯沿着林荫道轻快小跑，在斜坡和树影间松弛牵引绳，及时躲开突然冲出的电瓶车。",
    reward: "+12 分",
    hazard: "撞车 / 看手机 -14",
  },
  {
    id: "street_lawn",
    title: "草坪狗友社交",
    subtitle: "草坪 · 下午",
    desc: "在阳光草坪上观察周围小狗的肢体信号，引导布鲁斯靠近摇尾巴的友好伙伴，避开戒备犬只。",
    reward: "+13 分 · 18% 触发换分",
    hazard: "撞上戒备犬 -15",
  },
  {
    id: "street_window",
    title: "花房与烘焙橱窗",
    subtitle: "橱窗 · 试吃",
    desc: "沿街看花房与甜品店橱窗陈列，选中 PET FRIENDLY 门口给布鲁斯送上脆脆小饼干。",
    reward: "+11 分",
    hazard: "误入禁宠店 -15",
  },
  {
    id: "street_bridge",
    title: "暮色水岸晚风",
    subtitle: "水岸 · 蓝调时刻",
    desc: "傍晚水岸微风轻拂，牵着布鲁斯依次点亮三盏岸边灯影，同时避开高分贝声源惊吓。",
    reward: "+14 分 · 14% 触发换分",
    hazard: "噪音惊吓 -16",
  },
];

let activeCinematic = null;
let cinematicHostEl = null;

function pickRandom(arr, fallback = "") {
  if (!Array.isArray(arr) || arr.length === 0) return fallback;
  return arr[Math.floor(Math.random() * arr.length)];
}

function formatTemplate(tpl, vars) {
  return String(tpl || "").replace(/\{(\w+)\}/g, (_, k) => (vars[k] !== undefined ? vars[k] : ""));
}

/**
 * Unmount any running fullscreen 3D cinematic stage and release its host container.
 */
export function unmountSceneView() {
  if (activeCinematic) {
    try {
      activeCinematic.destroy();
    } catch (_) {}
    activeCinematic = null;
  }
  if (cinematicHostEl) {
    cinematicHostEl.remove();
    cinematicHostEl = null;
  }
}

function launchCinematicActivity(act, autoplay) {
  const player = store.state.player;
  if (!player) return;

  unmountSceneView();
  cinematicHostEl = document.createElement("div");
  cinematicHostEl.id = "cinematic-stage-host";
  document.body.appendChild(cinematicHostEl);

  activeCinematic = mountCinematicStage(cinematicHostEl, {
    activityId: act.id,
    owner: player.owner || "Alex",
    happiness: player.happiness,
    content: store.state.content || {},
    autoplay: Boolean(autoplay),
    async onComplete(result) {
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
        const swap = await apiTriggerSwap(latestPlayer.nickname, latestPlayer.pin, act.title);
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
 * Render the bright frosted-glass Zone Activity Lobby for "home" or "street".
 */
export function renderSceneView(container, sceneType) {
  if (!container) return;
  unmountSceneView();

  if (store.isSulking()) {
    store.setView("shop");
    return;
  }

  const isHome = sceneType === "home";
  const list = isHome ? HOME_ACTIVITIES : STREET_ACTIVITIES;
  const zoneTag = isHome ? "独栋小院 · 3D 全屏互动" : "林荫街区 · 3D 全屏互动";
  const zoneTitle = isHome ? "推门陪布鲁斯过一个下午" : "牵绳去精品街区散步探店";
  const zoneDesc = "每一幕都是全屏 3D 自动运镜短片，你可以亲自在关键时刻介入互动，也可以直接点击「自动观影」沉浸观看。";

  container.innerHTML = `
    <div class="lobby-shell">
      <div class="lobby-header">
        <div class="lobby-title-block">
          <span class="pill-badge">${zoneTag}</span>
          <h2>${zoneTitle}</h2>
          <p>${zoneDesc}</p>
        </div>
        <button class="btn-pill" id="btn-scene-to-map" type="button">返回 3D 大地图</button>
      </div>

      <div class="lobby-grid">
        ${list.map((act, idx) => `
          <article class="lobby-card" data-act-card="${act.id}">
            <div class="lobby-card-top">
              <span class="lobby-index">0${idx + 1}</span>
              <span class="lobby-sub">${act.subtitle}</span>
            </div>
            <h3>${act.title}</h3>
            <p class="lobby-desc">${act.desc}</p>
            <div class="lobby-chips">
              <span class="reward-chip">${act.reward}</span>
              <span class="hazard-chip">${act.hazard}</span>
            </div>
            <div class="lobby-actions">
              <button class="btn-pill btn-primary" type="button" data-launch-act="${act.id}" data-autoplay="false">
                开启沉浸陪伴
              </button>
              <button class="btn-pill" type="button" data-launch-act="${act.id}" data-autoplay="true">
                自动观影
              </button>
            </div>
          </article>
        `).join("")}
      </div>
    </div>
  `;

  document.getElementById("btn-scene-to-map")?.addEventListener("click", () => {
    unmountSceneView();
    store.setView("map");
  });

  const byId = new Map(list.map((item) => [item.id, item]));
  container.querySelectorAll("[data-launch-act]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const act = byId.get(btn.getAttribute("data-launch-act"));
      if (!act) return;
      feedback("small", e.clientX, e.clientY);
      launchCinematicActivity(act, btn.getAttribute("data-autoplay") === "true");
    });
  });

  const requestedId = store.state.activeActivityId;
  if (requestedId && byId.has(requestedId)) {
    const targetCard = container.querySelector(`[data-act-card="${requestedId}"]`);
    targetCard?.classList.add("is-highlighted");
  }
}
