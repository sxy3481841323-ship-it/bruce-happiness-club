// API client talking to /api/* (EdgeOne Pages Functions in prod, dev_server.py locally)

async function requestJson(url, options = {}) {
  const resp = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await resp.json().catch(() => ({ ok: false, error: "服务器返回异常" }));
  if (!resp.ok || data.ok === false) {
    const err = new Error(data.error || `请求失败 (${resp.status})`);
    err.status = resp.status;
    throw err;
  }
  return data;
}

export function apiRegister(owner, nickname, pin) {
  return requestJson("/api/register", {
    method: "POST",
    body: JSON.stringify({ owner, nickname, pin }),
  });
}

export function apiUpdateScore(nickname, pin, owner, happiness, tickerMessage = "") {
  return requestJson("/api/score", {
    method: "POST",
    body: JSON.stringify({ nickname, pin, owner, happiness, tickerMessage }),
  });
}

export function apiTriggerSwap(nickname, pin, reason) {
  return requestJson("/api/swap", {
    method: "POST",
    body: JSON.stringify({ nickname, pin, reason }),
  });
}

export function apiGetLeaderboard() {
  return requestJson("/api/leaderboard", { method: "GET" });
}
