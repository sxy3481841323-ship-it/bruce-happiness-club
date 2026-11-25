import {
  buildSortedLeaderboard,
  getKv,
  hashPin,
  jsonResponse,
  loadState,
  pushTicker,
  saveState,
  selectMeaningATarget,
} from "./_shared.js";

export async function onRequest({ request, env }) {
  if (request.method === "OPTIONS") return jsonResponse({ ok: true });
  if (request.method !== "POST") return jsonResponse({ ok: false, error: "Method not allowed" }, 405);

  const kv = getKv(env);
  if (!kv) return jsonResponse({ ok: false, error: "KV namespace BRUCE_KV is not bound" }, 500);

  let body;
  try {
    body = await request.json();
  } catch (_) {
    return jsonResponse({ ok: false, error: "Invalid JSON body" }, 400);
  }

  const nickname = String(body.nickname || "").trim();
  const pin = String(body.pin || "").trim();
  const reason = String(body.reason || "陪布鲁斯触发幸运时刻").trim();
  const state = await loadState(kv);
  const player = state.players[nickname];
  if (!player) return jsonResponse({ ok: false, error: "Player not found" }, 404);
  if (player.pinHash !== hashPin(pin)) return jsonResponse({ ok: false, error: "Invalid PIN" }, 403);

  const picked = selectMeaningATarget(state, nickname);
  if (!picked) {
    // Already rank #1 (or tied at top with no higher player)
    const oldScore = player.happiness;
    player.happiness += 6;
    player.updatedAt = Date.now();
    const msg = `榜首巡礼：${nickname} 已是全服最高分仍触发换分奇遇，顺手再拿 +6 分稳居榜首（${player.happiness} 分）！`;
    pushTicker(state, msg);
    await saveState(kv, state);
    return jsonResponse({
      ok: true,
      topBonus: true,
      oldScore,
      newScore: player.happiness,
      targetNickname: null,
      tickerMessage: msg,
      leaderboard: buildSortedLeaderboard(state),
      ticker: state.ticker,
    });
  }

  const { target, poolSize, targetRankInHigherPool } = picked;
  const oldScore = player.happiness;
  const targetOldScore = target.happiness;

  // Atomic swap in state
  player.happiness = targetOldScore;
  target.happiness = oldScore;
  player.updatedAt = Date.now();
  target.updatedAt = Date.now();

  const msg = `吃瓜快讯：${nickname} ${reason}，发动「高位交换」把原高分玩家「${target.nickname}」的 ${targetOldScore} 分收入囊中（原分 ${oldScore} 分归对方）！`;
  pushTicker(state, msg);
  await saveState(kv, state);

  return jsonResponse({
    ok: true,
    topBonus: false,
    oldScore,
    newScore: player.happiness,
    targetNickname: target.nickname,
    targetOldScore,
    poolSize,
    targetRankInHigherPool,
    tickerMessage: msg,
    leaderboard: buildSortedLeaderboard(state),
    ticker: state.ticker,
  });
}
