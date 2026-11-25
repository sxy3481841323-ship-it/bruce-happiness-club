import { store } from "./state.js";

export function renderTicker(items) {
  const track = document.getElementById("ticker-track");
  if (!track) return;
  const list = Array.isArray(items) && items.length > 0
    ? items
    : [{ text: "欢迎来到《布鲁斯》幸福指数俱乐部，陪伴不玩手机才是硬道理。" }];

  const spans = list.map((it) => `<span class="ticker-item">${it.text}</span>`).join("");
  track.innerHTML = spans + spans;
}

export function renderLeaderboardDrawer() {
  const listEl = document.getElementById("leaderboard-list");
  const noteEl = document.getElementById("swap-pool-note");
  if (!listEl) return;

  const board = store.state.leaderboard || [];
  const me = store.state.player;
  const higherCount = me
    ? board.filter((row) => row.nickname !== me.nickname && row.happiness > me.happiness).length
    : 0;

  if (noteEl && me) {
    noteEl.textContent = higherCount > 0
      ? `排在你前面有 ${higherCount} 位玩家：触发「高位交换」时，第 1 名被抽中概率最低，越靠近你的高分玩家越容易被你翻牌换分。`
      : "你目前是全服第 1 名！继续触发幸运事件可额外获 +6 分榜首巡礼。";
  }

  listEl.innerHTML = board.map((row) => {
    const isMe = me && row.nickname === me.nickname;
    const avatarSrc = row.owner === "Meya" ? "./assets/img/owner_meya.jpg" : "./assets/img/owner_alex.jpg";
    return `
      <div class="lb-row ${isMe ? "me" : ""}">
        <div class="lb-left">
          <span class="lb-rank">#${row.rank}</span>
          <img class="lb-avatar" src="${avatarSrc}" alt="${row.owner}" />
          <div>
            <div class="lb-name">${row.nickname} ${isMe ? '<span class="me-tag">你</span>' : ""}</div>
            <div class="lb-sub">${row.owner} &amp; 布鲁斯 · ${row.mood === "happy" ? "开心" : "冷战中"}</div>
          </div>
        </div>
        <div class="lb-score">${row.happiness}</div>
      </div>
    `;
  }).join("");
}

export function showSwapResultModal(swapRes) {
  const modal = document.getElementById("generic-modal");
  const card = document.getElementById("generic-modal-card");
  if (!modal || !card) return;

  if (swapRes.topBonus) {
    card.innerHTML = `
      <span class="modal-pill-tag">榜首巡礼</span>
      <h2 class="modal-title">全服第 1 · 幸运加分！</h2>
      <p class="modal-lead">你已是全服最高分，触发幸运时刻再赢 <strong>+6 分</strong>，全服吃瓜公告已发出。</p>
      <div class="score-summary-pill">
        <span>最新幸福指数</span>
        <strong style="color:var(--burgundy);">${swapRes.newScore}</strong>
      </div>
      <button class="btn-pill btn-primary btn-block" id="btn-close-swap" type="button">太棒了 · 继续</button>
    `;
  } else {
    card.innerHTML = `
      <span class="modal-pill-tag">高位幸福交换</span>
      <h2 class="modal-title">把高分换过来啦！</h2>
      <p class="modal-lead">
        布鲁斯的满格魅力在排你前面的 ${swapRes.poolSize} 位玩家里，按“越靠下越易抽中”权重，成功和 <strong>${swapRes.targetNickname}</strong> 互换了幸福指数。
      </p>
      <div class="swap-compare-box">
        <div>
          <span class="soft-hint">你的原分</span>
          <div class="swap-num">${swapRes.oldScore}</div>
        </div>
        <div class="swap-arrow">⇄</div>
        <div>
          <span class="soft-hint">换来 ${swapRes.targetNickname}</span>
          <div class="swap-num is-new">${swapRes.newScore}</div>
        </div>
      </div>
      <button class="btn-pill btn-primary btn-block" id="btn-close-swap" type="button">收下分数 · 看吃瓜</button>
    `;
  }

  modal.classList.remove("hidden");
  document.getElementById("btn-close-swap")?.addEventListener("click", () => {
    modal.classList.add("hidden");
  });
}
