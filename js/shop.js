import { store } from "./state.js";
import { apiUpdateScore } from "./api.js";
import { feedback } from "./juice.js";
import { PANTRY_ICONS } from "./pantryIcons.js";
import { sfx } from "./audio.js";

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

  sfx.playConciergeBell?.();
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
      "管家端来一碗无盐骨汤，放下 33 转唱针，布鲁斯在 {player} 的温柔陪伴里软回了 80 分。"
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

    sfx.playSuccess();
    feedback("win", window.innerWidth / 2, window.innerHeight * 0.4, "回暖至 80!");
    card.innerHTML = `
      <span class="modal-pill-tag">STEWARD CARE · 安抚完成</span>
      <h2 class="modal-title">布鲁斯软下耳朵啦</h2>
      <img src="./assets/img/bruce_happy.jpg" alt="布鲁斯开心" class="modal-bruce-thumb" />
      <p class="modal-lead" style="text-align:center;">
        温热骨汤见底，唱针刚好走到尾声。幸福指数已温和恢复至 <strong>80 分</strong>，可以回客厅或出海走走了。
      </p>
      <button class="btn-pill btn-primary btn-block" id="btn-video-done" type="button">返回顶层客厅</button>
    `;
    document.getElementById("btn-video-done")?.addEventListener("click", () => {
      sfx.playTap();
      modal.classList.add("hidden");
      store.setView("map");
    });
  };

  card.innerHTML = `
    <span class="modal-pill-tag">STEWARD SERVICE · 管家私厨</span>
    <h2 class="modal-title">管家私厨温汤 · 午后留声时刻</h2>
    <p class="modal-lead">侍应生正在温一盅无盐慢熬骨汤并轻落黑胶唱针，稍候片刻即可将幸福指数温和抚平至 <strong>80 分</strong>。</p>
    <div id="video-slot-wrap"></div>
    <div class="modal-footer-row">
      <span id="video-countdown-label" class="soft-hint">备餐准备中……</span>
      <button class="btn-pill" id="btn-cancel-video" type="button">暂不呈上</button>
    </div>
  `;
  modal.classList.remove("hidden");

  const slot = document.getElementById("video-slot-wrap");
  const label = document.getElementById("video-countdown-label");

  document.getElementById("btn-cancel-video")?.addEventListener("click", () => {
    sfx.playTap();
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
  video.style.borderRadius = "14px";
  video.style.margin = "12px 0";

  let fallbackStarted = false;
  const startPlaceholder = () => {
    if (fallbackStarted) return;
    fallbackStarted = true;
    sfx.playVinylDrop?.();
    slot.innerHTML = `
      <div class="video-placeholder-frame pantry-steward-frame">
        <div class="pantry-steward-icon">${PANTRY_ICONS.gramophone || PANTRY_ICONS.cloche}</div>
        <div class="pantry-steward-kicker">UNSALTED BONE BROTH · 33 RPM LOUNGE</div>
        <div class="pantry-steward-title">瓷盅慢熬骨汤温热中 · 唱针轻落午后爵士</div>
        <p class="pantry-steward-sub">侍应静候布鲁斯放松耳朵（支持放入 <code>assets/video/rescue.mp4</code> 自定义映像）</p>
        <div id="reel-sec" class="pantry-steward-timer">5s</div>
      </div>
    `;
    let left = 5;
    label.textContent = `侍应备餐中 · ${left} 秒后恢复至 80 分`;
    timer = setInterval(() => {
      left -= 1;
      const secEl = document.getElementById("reel-sec");
      if (secEl) secEl.textContent = `${Math.max(0, left)}s`;
      if (left <= 0) {
        clearInterval(timer);
        finishVideo();
      } else {
        label.textContent = `侍应备餐中 · ${left} 秒后恢复至 80 分`;
      }
    }, 1000);
  };

  video.addEventListener("error", startPlaceholder, { once: true });
  video.addEventListener("canplay", () => {
    label.textContent = "静候片段播毕即可温和恢复至 80 分";
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

  const cardsHtml = treats.map((t, idx) => {
    const affordable = player.happiness >= t.cost;
    const pct = Math.round(t.prob * 100);
    const isReserve = idx >= 6;
    return `
      <div class="treat-pill-card ${affordable && sulking ? "" : "is-dim"} ${isReserve ? "is-reserve" : ""}">
        <div class="treat-top-row">
          <div class="treat-art">${PANTRY_ICONS[t.id] || PANTRY_ICONS.biscuit}</div>
          <div class="treat-name-col">
            <div class="treat-en">${t.en}</div>
            <div class="treat-cn">${t.cn} · <span class="treat-tag">${t.tag}</span></div>
          </div>
        </div>
        <div class="treat-stats">
          <span>账目记 <strong>${t.cost}</strong> 分</span>
          <span>合意率 <strong>${pct}%</strong></span>
          <span>恢复至 <strong>${t.target}</strong></span>
        </div>
        <button
          type="button"
          class="btn-pill ${affordable && sulking ? "btn-primary" : ""}"
          data-treat="${t.id}"
          ${affordable && sulking ? "" : "disabled"}
        >
          ${!sulking ? "当前状态舒展 (≥80)" : (affordable ? `呈上这份鲜食 (${t.cost} 分)` : "当前分数不足")}
        </button>
      </div>
    `;
  }).join("");

  container.innerHTML = `
    <div class="pantry-shell">
      <div class="pantry-hero">
        <img src="./assets/img/${sulking ? "bruce_sulk.jpg" : "bruce_happy.jpg"}" alt="布鲁斯状态" class="pantry-bruce-img" />
        <div class="pantry-hero-text">
          <span class="modal-pill-tag">${sulking ? "HOUSE PANTRY · 低于 80 · 待安抚" : "HOUSE PANTRY · 私厨鲜食冷柜"}</span>
          <h2>${sulking ? `布鲁斯正趴在壁炉边生闷气（当前 ${player.happiness} 分）` : `布鲁斯已经舒展耳朵了（${player.happiness} 分）`}</h2>
          <p id="shop-monologue">
            ${sulking ? "从 ELOWEN 与私厨备餐抽屉里挑一份合心意的风干冷切或温热奶泡，用诚意融化他的小脾气。" : "丝巾与情绪都已妥帖，回阳光客厅继续陪布鲁斯吧。"}
          </p>
        </div>
        <button class="btn-pill" id="btn-shop-back" type="button">返回顶层客厅</button>
      </div>

      <div class="treat-shelf">${cardsHtml}</div>

      ${sulking && !canBuyAny ? `
        <div class="video-rescue-banner">
          <div class="rescue-banner-lead">
            <div class="rescue-banner-icon">${PANTRY_ICONS.cloche || ""}</div>
            <div>
              <strong>管家应急温汤 · 留声机午后安抚</strong>
              <p>当前幸福指数不足 5 分。请管家端上一盅无盐慢熬骨汤、轻轻落下一曲 33 转黑胶，布鲁斯便会软下耳朵回到 80 分。</p>
            </div>
          </div>
          <button class="btn-pill btn-primary" id="btn-watch-rescue-video" type="button">请管家备温汤 · 恢复至 80 分</button>
        </div>
      ` : ""}
    </div>
  `;

  document.getElementById("btn-shop-back")?.addEventListener("click", () => {
    sfx.playTap();
    store.setView("map");
  });
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
        sfx.playSuccess();
        monologue = pickRandom(content.treat_monologues?.success_lines, "布鲁斯嗅了嗅温度正好的瓷碟，尾巴在羊驼毛地毯上轻轻扫了两下。");
        tickerMsg = `私厨呈餐：${player.nickname} 挑出「${treat.cn}」（${Math.round(treat.prob * 100)}%），布鲁斯柔和地回到 ${nextScore} 分。`;
      } else if (treat.id === "wagyu") {
        sfx.playFail();
        monologue = content.treat_monologues?.wagyu_fail_line || "干式熟成的香气飘过，布鲁斯只是抬了抬眼皮，把鼻尖埋回了羊驼毛软榻。";
        tickerMsg = formatTemplate(
          pickRandom(content.ticker_templates?.wagyu_fail, "{player} 的和牛木匣没能打开布鲁斯的心，分数停在 {new_score} 分。"),
          { player: player.nickname, new_score: nextScore }
        );
      } else {
        sfx.playFail();
        monologue = pickRandom(content.treat_monologues?.fail_lines, "布鲁斯闻了闻瓷碟，礼貌地把下巴枕回了亚麻软垫。");
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
      feedback(success ? "win" : "fail", cx, cy, success ? `回暖 ${nextScore}!` : `-${treat.cost}`);

      const monoEl = document.getElementById("shop-monologue");
      if (monoEl) {
        monoEl.innerHTML = `<strong style="color:${success ? "var(--cypress)" : "var(--danger)"}">${success ? "合意 · 情绪舒展" : "暂未合意"}</strong> ${monologue}`;
      }
    });
  });
}
