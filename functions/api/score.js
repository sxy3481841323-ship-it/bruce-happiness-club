import {
  buildSortedLeaderboard,
  getKv,
  hashPin,
  jsonResponse,
  loadState,
  pushTicker,
  saveState,
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
  const state = await loadState(kv);
  const player = state.players[nickname];
  if (!player) return jsonResponse({ ok: false, error: "Player not found" }, 404);
  if (player.pinHash !== hashPin(pin)) return jsonResponse({ ok: false, error: "Invalid PIN" }, 403);

  const nextScore = Math.max(0, Math.min(9999, Math.round(Number(body.happiness) || 0)));
  player.happiness = nextScore;
  player.updatedAt = Date.now();
  if (body.owner === "Alex" || body.owner === "Meya") {
    player.owner = body.owner;
  }

  if (body.tickerMessage) {
    pushTicker(state, body.tickerMessage);
  }

  await saveState(kv, state);

  return jsonResponse({
    ok: true,
    player: { nickname: player.nickname, owner: player.owner, happiness: player.happiness },
    leaderboard: buildSortedLeaderboard(state),
    ticker: state.ticker,
  });
}
