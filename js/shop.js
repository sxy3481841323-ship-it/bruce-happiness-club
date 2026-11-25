import { store } from "./state.js";
import { apiUpdateScore } from "./api.js";
import { feedback } from "./juice.js";

const TREAT_ICONS = {
  biscuit: `<svg viewBox="0 0 64 64" width="48" height="48"><path d="M16 26c-4-4-2-10 4-10 3 0 5 2 6 4h12c1-2 3-4 6-4 6 0 8 6 4 10 4 4 2 10-4 10-3 0-5-2-6-4H26c-1 2-3 4-6 4-6 0-8-6-4-10z" fill="#E8C38E" stroke="#2A2421" stroke-width="2.4" transform="rotate(-14 32 32)"/><circle cx="28" cy="30" r="1.6" fill="#9B6E3C"/><circle cx="36" cy="33" r="1.6" fill="#9B6E3C"/></svg>`,
  yolk: `<svg viewBox="0 0 64 64" width="48" height="48"><rect x="16" y="16" width="32" height="32" rx="9" fill="#F9CF58" stroke="#2A2421" stroke-width="2.4"/><circle cx="32" cy="32" r="9" fill="#F3A72C" opacity="0.7"/></svg>`,
  jerky: `<svg viewBox="0 0 64 64" width="48" height="48"><path d="M14 40c4-14 20-24 36-20 4 1 5 7 1 11-10 10-20 18-32 16-4-1-6-3-5-7z" fill="#D58654" stroke="#2A2421" stroke-width="2.4"/><path d="M24 35c6-6 14-10 20-10" stroke="#A6552B" stroke-width="2" stroke-linecap="round"/></svg>`,
  pup_cup: `<svg viewBox="0 0 64 64" width="48" height="48"><path d="M18 28h28l-4 24H22l-4-24z" fill="#FFFDF8" stroke="#2A2421" stroke-width="2.4"/><path d="M16 28c0-7 6-10 10-9 2-5 10-5 12 0 4-1 10 2 10 9z" fill="#FFF7EB" stroke="#2A2421" stroke-width="2.2"/><circle cx="32" cy="18" r="3" fill="#B84B59"/></svg>`,
  salmon: `<svg viewBox="0 0 64 64" width="48" height="48"><path d="M12 36c6-14 26-20 40-10l-4 18c-12 6-26 4-36-8z" fill="#F28A72" stroke="#2A2421" stroke-width="2.4"/><path d="M22 28c4 4 4 10 2 13M34 25c4 5 4 11 2 15M44 25c3 4 3 10 1 14" stroke="#FFE5DC" stroke-width="2" stroke-linecap="round"/></svg>`,
  duck_leg: `<svg viewBox="0 0 64 64" width="48" height="48"><path d="M16 34c2-11 16-18 27-13 8 4 9 15 1 21-8 6-20 6-25 0-3-3-4-5-3-8z" fill="#C97043" stroke="#2A2421" stroke-width="2.4"/><path d="M44 39l9 8c2 2 0 6-3 5l-9-8" fill="#FAF2E4" stroke="#2A2421" stroke-width="2.2"/></svg>`,
  steak: `<svg viewBox="0 0 64 64" width="48" height="48"><path d="M13 31c0-11 13-17 26-15 11 2 14 11 11 20-3 9-17 13-28 9-7-3-9-8-9-14z" fill="#A93C46" stroke="#2A2421" stroke-width="2.4"/><path d="M22 27l18 10M24 36l14-8" stroke="#6E1E26" stroke-width="2" stroke-linecap="round"/></svg>`,
  wagyu: `<svg viewBox="0 0 64 64" width="48" height="48"><rect x="11" y="16" width="42" height="32" rx="6" fill="#2A2726" stroke="#2A2421" stroke-width="2.4"/><rect x="16" y="21" width="32" height="22" rx="4" fill="#BA4A56"/><path d="M20 26c6 2 12-2 18 3s6 9 6 9M20 35c7-2 14 2 22-3" stroke="#F8DADA" stroke-width="2.2" fill="none" stroke-linecap="round"/></svg>`,
};

function pickRandom(arr, fallback = "") {
  if (!Array.isArray(arr) || arr.length === 0) return fallback;
  return arr[Math.floor(Math.random() * arr.length)];
}

function formatTemplate(tpl, vars) {
  return String(tpl || "").replace(/\{(\w+)\}/g, (_, k) => (vars[k] !== undefined ? vars[k] : ""));
}

function openRescueVideoModal() {
  const modal = document.getElementById("generic-modal");
  const card = document.getElementById("generic-modal-card");
  if (!modal || !card) return;

  let timer = null;
  let completed = false;

  const finishVideo = async () => {
    if (completed) return;
    completed = true;
    if (timer) clearInterval(timer);

    const player = store.state.player;
    if (!player) return;

    const tpl = pickRandom(
      store.state.content?.ticker_templates?.rescue_video,
      "回血现场：{player} 破产看小视频成功把布鲁斯哄回 80 分！"
    );
    const tickerMsg = formatTemplate(tpl, {
      player: player.nickname,
      old_score: player.happiness,
      new_score: 80,
    });

    try {
      const res = await apiUpdateScore(player.nickname, player.pin, player.owner, 80, tickerMsg);
      store.setHappiness(res.player.happiness);
      store.setLeaderboardAndTicker(res.leaderboard, res.ticker);
    } catch (_) {
      store.setHappiness(80);
    }

    feedback("win", window.innerWidth / 2, window.innerHeight * 0.4, "回血至 80!");
    card.innerHTML = `
      <span class="modal-pill-tag">元气恢复完成</span>
      <h2 class="modal-title">布鲁斯被哄好啦！</h2>
      <img src="./assets/img/bruce_happy.jpg" alt="布鲁斯开心" class="modal-bruce-thumb" />
      <p class="modal-lead" style="text-align:center;">
        幸福指数已精准恢复至 <strong>80 分</strong>，冷战解除，现在可以去小院或街区继续冲榜了。
      </p>
      <button class="btn-pill btn-primary btn-block" id="btn-video-done" type="button">回到大地图继续玩</button>
    `;
    document.getElementById("btn-video-done")?.addEventListener("click", () => {
      modal.classList.add("hidden");
      store.setView("map");
    });
  };

  card.innerHTML = `
    <span class="modal-pill-tag">最后救急通道</span>
    <h2 class="modal-title">小视频急救放映室</h2>
    <p class="modal-lead">完整看完这段小视频，即可把布鲁斯的幸福指数精准拉回 <strong>80 分</strong>。</p>
    <div id="video-slot-wrap"></div>
    <div class="modal-footer-row">
      <span id="video-countdown-label" class="soft-hint">准备播放中……</span>
      <button class="btn-pill" id="btn-cancel-video" type="button">暂不观看</button>
    </div>
  `;
  modal.classList.remove("hidden");

  const slot = document.getElementById("video-slot-wrap");
  const label = document.getElementById("video-countdown-label");

  document.getElementById("btn-cancel-video")?.addEventListener("click", () => {
    if (timer) clearInterval(timer);
    modal.classList.add("hidden");
  });

  const video = document.createElement("video");
  video.src = "./assets/video/rescue.mp4";
  video.controls = true;
  video.playsInline = true;
  video.autoplay = true;
  video.style.width = "100%";
  video.style.maxHeight = "260px";
  video.style.borderRadius = "18px";
  video.style.margin = "12px 0";

  let fallbackStarted = false;
  const startPlaceholder = () => {
    if (fallbackStarted) return;
    fallbackStarted = true;
    slot.innerHTML = `
      <div class="video-placeholder-frame">
        <div style="font-size:12px;opacity:0.75;">复活小视频预留位</div>
        <div style="font-size:19px;font-weight:700;margin:8px 0;">待放入 <code>assets/video/rescue.mp4</code></div>
        <p style="font-size:12px;opacity:0.72;">当前为演示倒计时，放入真视频后将自动真片播放。</p>
        <div id="reel-sec" style="font-size:34px;font-weight:800;margin-top:10px;color:#FCD34D;">5s</div>
      </div>
    `;
    let left = 5;
    label.textContent = `倒计时 ${left} 秒后恢复至 80 分`;
    timer = setInterval(() => {
      left -= 1;
      const secEl = document.getElementById("reel-sec");
      if (secEl) secEl.textContent = `${Math.max(0, left)}s`;
      if (left <= 0) {
        clearInterval(timer);
        finishVideo();
      } else {
        label.textContent = `倒计时 ${left} 秒后恢复至 80 分`;
      }
    }, 1000);
  };

  video.addEventListener("error", startPlaceholder, { once: true });
  video.addEventListener("canplay", () => {
    label.textContent = "请完整看完视频即可恢复至 80 分";
  }, { once: true });
  video.addEventListener("ended", finishVideo, { once: true });
  slot.appendChild(video);

  setTimeout(() => {
    if (!fallbackStarted && video.readyState === 0) {
      startPlaceholder();
    }
  }, 1500);
}

export function renderShopView(container) {
  if (!container) return;
  const player = store.state.player;
  const content = store.state.content;
  if (!player || !content) return;

  const treats = content.treats || [];
  const sulking = store.isSulking();
  const canBuyAny = store.canAffordCheapestTreat();

  const cardsHtml = treats.map((t) => {
    const affordable = player.happiness >= t.cost;
    const pct = Math.round(t.prob * 100);
    return `
      <div class="treat-pill-card ${affordable && sulking ? "" : "is-dim"}">
        <div class="treat-top-row">
          <div class="treat-art">${TREAT_ICONS[t.id] || TREAT_ICONS.biscuit}</div>
          <div class="treat-name-col">
            <div class="treat-en">${t.en}</div>
            <div class="treat-cn">${t.cn} · <span class="treat-tag">${t.tag}</span></div>
          </div>
        </div>
        <div class="treat-stats">
          <span>花 <strong>${t.cost}</strong> 分</span>
          <span>概率 <strong>${pct}%</strong></span>
          <span>拉回 <strong>${t.target}</strong></span>
        </div>
        <button
          type="button"
          class="btn-pill ${affordable && sulking ? "btn-primary" : ""}"
          data-treat="${t.id}"
          ${affordable && sulking ? "" : "disabled"}
        >
          ${!sulking ? "当前状态正常 (≥80)" : (affordable ? `花 ${t.cost} 分哄布鲁斯` : "幸福指数不够")}
        </button>
      </div>
    `;
  }).join("");

  container.innerHTML = `
    <div class="pantry-shell">
      <div class="pantry-hero">
        <img src="./assets/img/${sulking ? "bruce_sulk.jpg" : "bruce_happy.jpg"}" alt="布鲁斯状态" class="pantry-bruce-img" />
        <div class="pantry-hero-text">
          <span class="modal-pill-tag">${sulking ? "低于 80 · 冷战中" : "已恢复快乐"}</span>
          <h2>${sulking ? `布鲁斯拒绝陪玩（当前 ${player.happiness} 分）` : `布鲁斯已经原谅你了（${player.happiness} 分）`}</h2>
          <p id="shop-monologue">
            ${sulking ? "它现在感受不到陪玩的快乐，只能花幸福指数买零食来赌一把它的回心转意。" : "快回大地图或独栋小院继续陪布鲁斯吧！"}
          </p>
        </div>
        <button class="btn-pill" id="btn-shop-back" type="button">返回大地图</button>
      </div>

      <div class="treat-shelf">${cardsHtml}</div>

      ${sulking && !canBuyAny ? `
        <div class="video-rescue-banner">
          <div>
            <strong>兜里连 5 分的磨牙饼干都买不起了</strong>
            <p>触发保底复活：看完一段小视频，布鲁斯心软原谅你，幸福指数回到刚好 80 分。</p>
          </div>
          <button class="btn-pill btn-primary" id="btn-watch-rescue-video" type="button">看小视频拉回 80 分</button>
        </div>
      ` : ""}
    </div>
  `;

  document.getElementById("btn-shop-back")?.addEventListener("click", () => store.setView("map"));
  document.getElementById("btn-watch-rescue-video")?.addEventListener("click", openRescueVideoModal);

  container.querySelectorAll("[data-treat]").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      const treatId = btn.getAttribute("data-treat");
      const treat = treats.find((t) => t.id === treatId);
      if (!treat || !store.isSulking() || player.happiness < treat.cost) return;

      btn.disabled = true;
      const afterSpend = player.happiness - treat.cost;
      const success = Math.random() < treat.prob;
      let nextScore = success ? treat.target : afterSpend;
      let tickerMsg = "";
      let monologue = "";

      if (success) {
        monologue = pickRandom(content.treat_monologues?.success_lines, "布鲁斯吃得尾巴摇成螺旋桨，瞬间原谅你了！");
        tickerMsg = `投喂成功：${player.nickname} 用 ${treat.cn}（${Math.round(treat.prob * 100)}%）把布鲁斯哄回 ${nextScore} 分！`;
      } else if (treat.id === "wagyu") {
        monologue = content.treat_monologues?.wagyu_fail_line || "68分和牛礼盒也救不了的傲娇！布鲁斯闻了一下扭头就走。";
        tickerMsg = formatTemplate(
          pickRandom(content.ticker_templates?.wagyu_fail, "{player} 花68分买和牛礼盒竟然撞中4%失败，实惨！"),
          { player: player.nickname, new_score: nextScore }
        );
      } else {
        monologue = pickRandom(content.treat_monologues?.fail_lines, "布鲁斯扭过头去：这点小零食打发不了我。");
      }

      try {
        const res = await apiUpdateScore(player.nickname, player.pin, player.owner, nextScore, tickerMsg);
        store.setHappiness(res.player.happiness);
        store.setLeaderboardAndTicker(res.leaderboard, res.ticker);
      } catch (_) {
        store.setHappiness(nextScore);
      }

      const cx = e.clientX || window.innerWidth / 2;
      const cy = e.clientY || window.innerHeight * 0.4;
      feedback(success ? "win" : "fail", cx, cy, success ? `拉回 ${nextScore}!` : `-${treat.cost}`);

      const monoEl = document.getElementById("shop-monologue");
      if (monoEl) {
        monoEl.innerHTML = `<strong style="color:${success ? "var(--cypress)" : "var(--danger)"}">${success ? "哄狗成功！" : "投喂失败！"}</strong> ${monologue}`;
      }
    });
  });
}
