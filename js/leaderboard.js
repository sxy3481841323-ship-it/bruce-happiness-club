import { store } from "./state.js";

function escapeHtml(raw) {
  return String(raw ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export function renderTicker(items) {
  const track = document.getElementById("ticker-track");
  if (!track) return;
  const list = Array.isArray(items) && items.length > 0
    ? items
    : [{ text: "欢迎来到《布鲁斯》幸福指数俱乐部，陪伴不玩手机才是硬道理。" }];

  const spans = list.map((it) => `<span class="ticker-item">${escapeHtml(it.text)}</span>`).join("");
  track.innerHTML = spans + spans;
}

export function renderLeaderboardDrawer() {
  const listEl = document.getElementById("leaderboard-list");
  const noteEl = document.getElementById("swap-pool-note");
  if (!listEl) return;

  const board = store.state.leaderboard || [];
  const me = store.state.player;

  // Match backend Meaning-A weight pool (functions/api/_shared.js -> selectMeaningATarget)
  const higherPool = me
    ? board.filter((row) => row.nickname !== me.nickname && Number(row.happiness) > Number(me.happiness))
    : [];
  const higherCount = higherPool.length;
  const totalWeight = (higherCount * (higherCount + 1)) / 2;
  const preyPctMap = new Map();
  if (totalWeight > 0) {
    higherPool.forEach((row, idx) => {
      const weight = idx + 1;
      const pct = Math.max(1, Math.round((weight / totalWeight) * 100));
      preyPctMap.set(row.nickname, pct);
    });
  }

  if (noteEl && me) {
    noteEl.textContent = higherCount > 0
      ? `你的上方有 ${higherCount} 块荣誉铭牌：金标 ⌖ 为触发「高位交换」时的猎物权重占比，第 1 名最稳，越接近你的高分住户越容易被翻牌互换。`
      : "你的铭牌已高悬俱乐部榜首第 1 位！继续触发幸运事件可再获 +6 分榜首巡礼。";
  }

  if (board.length === 0) {
    listEl.innerHTML = `<div class="lb-empty">暂无住户荣誉铭牌，快成为第 1 位推开客厅大门的主人吧。</div>`;
    return;
  }

  listEl.innerHTML = board.map((row) => {
    const isMe = Boolean(me && row.nickname === me.nickname);
    const rankNum = Number(row.rank) || 0;
    const scoreNum = Number(row.happiness) || 0;
    const safeNick = escapeHtml(row.nickname || "神秘住户");
    const safeOwner = row.owner === "Meya" ? "Meya" : "Alex";
    const avatarSrc = safeOwner === "Meya" ? "./assets/img/owner_meya.jpg" : "./assets/img/owner_alex.jpg";
    const isHappy = row.mood === "happy" || scoreNum >= 80;
    const preyPct = preyPctMap.get(row.nickname);

    const tierClass = rankNum === 1
      ? "is-rank-1"
      : rankNum === 2
        ? "is-rank-2"
        : rankNum === 3
          ? "is-rank-3"
          : "is-rank-other";

    const rankBadge = rankNum === 1 ? "NO.01" : `#${rankNum}`;
    const rivetsHtml = rankNum === 1
      ? `<span class="plaque-rivet r-tl"></span><span class="plaque-rivet r-tr"></span><span class="plaque-rivet r-bl"></span><span class="plaque-rivet r-br"></span>`
      : "";

    const preyHtml = preyPct !== undefined
      ? `<span class="lb-prey-badge" title="触发高位交换时抽中该住户的概率">⌖ 换分猎物 · 约 ${preyPct}%</span>`
      : "";

    const moodHtml = isHappy
      ? `<span class="lb-mood-tag is-happy">☀ 活力陪玩</span>`
      : `<span class="lb-mood-tag is-sulk">🌧️ 冷战哄狗中</span>`;

    return `
      <article class="lb-plaque ${tierClass} ${isMe ? "is-me" : ""} ${preyPct !== undefined ? "is-prey" : ""}">
        ${rivetsHtml}
        ${rankNum === 1 ? '<div class="lb-sovereign-banner">👑 俱乐部首席荣誉铭牌 · 稳坐云端客厅</div>' : ""}
        <div class="lb-plaque-body">
          <div class="lb-left">
            <span class="lb-rank">${rankBadge}</span>
            <img class="lb-avatar" src="${avatarSrc}" alt="${safeOwner}" />
            <div class="lb-info">
              <div class="lb-name">
                <span class="lb-name-text" title="${safeNick}">${safeNick}</span>
                ${isMe ? '<span class="me-tag">你</span>' : ""}
              </div>
              <div class="lb-meta-row">
                <span class="lb-sub">${safeOwner} &amp; 布鲁斯</span>
                ${moodHtml}
                ${preyHtml}
              </div>
            </div>
          </div>
          <div class="lb-score-col">
            <span class="lb-score">${scoreNum}</span>
            <span class="lb-score-unit">PTS</span>
          </div>
        </div>
      </article>
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
        <strong style="color:var(--burgundy);">${Number(swapRes.newScore) || 0}</strong>
      </div>
      <button class="btn-pill btn-primary btn-block" id="btn-close-swap" type="button">太棒了 · 继续</button>
    `;
  } else {
    const safeTarget = escapeHtml(swapRes.targetNickname || "神秘住户");
    card.innerHTML = `
      <span class="modal-pill-tag">高位幸福交换</span>
      <h2 class="modal-title">把高分换过来啦！</h2>
      <p class="modal-lead">
        布鲁斯的满格魅力在排你前面的 ${Number(swapRes.poolSize) || 1} 位玩家里，按“越靠下越易抽中”权重，成功和 <strong>${safeTarget}</strong> 互换了幸福指数。
      </p>
      <div class="swap-compare-box">
        <div>
          <span class="soft-hint">你的原分</span>
          <div class="swap-num">${Number(swapRes.oldScore) || 0}</div>
        </div>
        <div class="swap-arrow">⇄</div>
        <div>
          <span class="soft-hint">换来 ${safeTarget}</span>
          <div class="swap-num is-new">${Number(swapRes.newScore) || 0}</div>
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
