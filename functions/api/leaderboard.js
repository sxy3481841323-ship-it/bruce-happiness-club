import { buildSortedLeaderboard, getKv, jsonResponse, loadState } from "./_shared.js";

export async function onRequest({ request, env }) {
  if (request.method === "OPTIONS") return jsonResponse({ ok: true });
  if (request.method !== "GET") return jsonResponse({ ok: false, error: "Method not allowed" }, 405);

  const kv = getKv(env);
  if (!kv) return jsonResponse({ ok: false, error: "KV namespace BRUCE_KV is not bound" }, 500);

  const state = await loadState(kv);
  return jsonResponse({
    ok: true,
    leaderboard: buildSortedLeaderboard(state),
    ticker: state.ticker || [],
  });
}
