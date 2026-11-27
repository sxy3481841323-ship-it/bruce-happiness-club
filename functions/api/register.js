import {
  buildSortedLeaderboard,
  getKv,
  hashPin,
  jsonResponse,
  loadState,
  pushTicker,
  saveState,
  validateNickname,
  validatePin,
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

  const nickCheck = validateNickname(body.nickname);
  if (!nickCheck.ok) return jsonResponse({ ok: false, error: nickCheck.error }, 400);

  const pinCheck = validatePin(body.pin);
  if (!pinCheck.ok) return jsonResponse({ ok: false, error: pinCheck.error }, 400);

  const owner = body.owner === "Meya" ? "Meya" : "Alex";
  const state = await loadState(kv);
  const existing = state.players[nickCheck.nickname];
  const pinDigest = hashPin(pinCheck.pin);

  if (existing) {
    if (existing.pinHash !== pinDigest) {
      return jsonResponse({ ok: false, error: "该昵称已被占用（若为你本人，请输入正确的 4 位暗号恢复进度）" }, 409);
    }
    existing.owner = owner;
    existing.updatedAt = Date.now();
    await saveState(kv, state);
    return jsonResponse({
      ok: true,
      resumed: true,
      player: { nickname: existing.nickname, owner: existing.owner, happiness: existing.happiness },
      leaderboard: buildSortedLeaderboard(state),
      ticker: state.ticker,
    });
  }

  const newPlayer = {
    nickname: nickCheck.nickname,
    pinHash: pinDigest,
    owner,
    happiness: 100,
    updatedAt: Date.now(),
    isSeed: false,
  };
  state.players[nickCheck.nickname] = newPlayer;
  pushTicker(state, `新住户入驻：${nickCheck.nickname} 领着布鲁斯和 ${owner} 推开了阳光顶层公寓大门，初始幸福 100 分。`);
  await saveState(kv, state);

  return jsonResponse({
    ok: true,
    resumed: false,
    player: { nickname: newPlayer.nickname, owner: newPlayer.owner, happiness: newPlayer.happiness },
    leaderboard: buildSortedLeaderboard(state),
    ticker: state.ticker,
  });
}
