// API client talking to /api/* (EdgeOne Pages Functions in prod, dev_server.py locally)
// Automatically falls back to an in-browser localStorage store on static hosts (GitHub Pages / VS Code Live Server).

const STATIC_KV_KEY = "bruce_static_kv_v1";

const DEFAULT_SEEDS = [
  { nickname: "早八起不来星人", owner: "Alex", happiness: 138 },
  { nickname: "冰美式续命侠", owner: "Meya", happiness: 126 },
  { nickname: "期末周摸鱼冠军", owner: "Alex", happiness: 118 },
  { nickname: "头等舱小腊肠", owner: "Meya", happiness: 112 },
  { nickname: "游艇甲板晒太阳", owner: "Alex", happiness: 105 },
  { nickname: "周末躺平选手", owner: "Meya", happiness: 96 },
  { nickname: "低头回微信扣分王", owner: "Alex", happiness: 86 },
  { nickname: "雨天踩坑冷战中", owner: "Meya", happiness: 74 },
];

function isStaticFallbackNeeded(err) {
  const msg = String(err?.message || "");
  return (
    err?.status === 404 ||
    err?.status === 405 ||
    err?.status === 501 ||
    (Number.isFinite(err?.status) && err.status >= 500) ||
    /KV namespace|not bound|not found/i.test(msg) ||
    err?.name === "TypeError"
  );
}

async function loadStaticKv() {
  try {
    const raw = localStorage.getItem(STATIC_KV_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && parsed.players) return parsed;
    }
  } catch (_) {}

  let seeds = DEFAULT_SEEDS;
  try {
    const resp = await fetch("./data/content.json");
    if (resp.ok) {
      const data = await resp.json();
      if (Array.isArray(data?.seed_players) && data.seed_players.length) {
        seeds = data.seed_players;
      }
    }
  } catch (_) {}

  const now = Date.now();
  const players = {};
  seeds.forEach((p, idx) => {
    players[p.nickname] = {
      nickname: p.nickname,
      pin: "0000",
      owner: p.owner === "Meya" ? "Meya" : "Alex",
      happiness: Number(p.happiness) || 100,
      updatedAt: now - idx * 60000,
      isSeed: true,
    };
  });
  const state = {
    players,
    ticker: [
      { id: "seed-1", text: "快讯：早八起不来星人 带着布鲁斯打卡精品街区，暂居第 1！（纯静态离线演示模式）", ts: now - 120000 },
    ],
  };
  saveStaticKv(state);
  return state;
}

function saveStaticKv(st) {
  st.ticker = (st.ticker || []).slice(0, 25);
  try {
    localStorage.setItem(STATIC_KV_KEY, JSON.stringify(st));
  } catch (_) {}
}

function sortBoard(st) {
  return Object.values(st.players || {})
    .map((p) => ({
      nickname: p.nickname,
      owner: p.owner,
      happiness: p.happiness,
      mood: p.happiness >= 80 ? "happy" : "sulking",
      updatedAt: p.updatedAt,
    }))
    .sort((a, b) => (b.happiness - a.happiness) || (a.updatedAt - b.updatedAt))
    .map((row, i) => ({ ...row, rank: i + 1 }));
}

function pushStaticTicker(st, text) {
  if (!text) return;
  st.ticker = st.ticker || [];
  st.ticker.unshift({
    id: `${Date.now()}-${Math.floor(Math.random() * 9000 + 1000)}`,
    text: String(text).slice(0, 140),
    ts: Date.now(),
  });
  st.ticker = st.ticker.slice(0, 25);
}

async function handleStaticFallback(endpoint, payload = {}) {
  const st = await loadStaticKv();

  if (endpoint === "leaderboard") {
    return { ok: true, leaderboard: sortBoard(st), ticker: st.ticker || [] };
  }

  if (endpoint === "register") {
    const nick = String(payload.nickname || "").trim();
    const pin = String(payload.pin || "").trim();
    const owner = payload.owner === "Meya" ? "Meya" : "Alex";
    const existing = st.players[nick];
    if (existing) {
      if (existing.pin !== pin) {
        const err = new Error("该昵称已被占用（若为你本人，请输入正确的 4 位暗号恢复进度）");
        err.status = 409;
        throw err;
      }
      existing.owner = owner;
      existing.updatedAt = Date.now();
      saveStaticKv(st);
      return {
        ok: true,
        resumed: true,
        player: { nickname: existing.nickname, owner: existing.owner, happiness: existing.happiness },
        leaderboard: sortBoard(st),
        ticker: st.ticker,
      };
    }
    const created = { nickname: nick, pin, owner, happiness: 100, updatedAt: Date.now(), isSeed: false };
    st.players[nick] = created;
    pushStaticTicker(st, `新人报到：${nick} 领着布鲁斯和 ${owner} 搬进了新家，初始幸福 100 分！`);
    saveStaticKv(st);
    return {
      ok: true,
      resumed: false,
      player: { nickname: created.nickname, owner: created.owner, happiness: created.happiness },
      leaderboard: sortBoard(st),
      ticker: st.ticker,
    };
  }

  if (endpoint === "score") {
    const nick = String(payload.nickname || "").trim();
    const p = st.players[nick];
    if (!p) throw new Error("Player not found");
    p.happiness = Math.max(0, Math.min(9999, Math.round(Number(payload.happiness || 0))));
    p.updatedAt = Date.now();
    if (payload.owner === "Alex" || payload.owner === "Meya") p.owner = payload.owner;
    if (payload.tickerMessage) pushStaticTicker(st, payload.tickerMessage);
    saveStaticKv(st);
    return {
      ok: true,
      player: { nickname: p.nickname, owner: p.owner, happiness: p.happiness },
      leaderboard: sortBoard(st),
      ticker: st.ticker,
    };
  }

  if (endpoint === "swap") {
    const nick = String(payload.nickname || "").trim();
    const reason = String(payload.reason || "陪布鲁斯触发幸运时刻").trim();
    const p = st.players[nick];
    if (!p) throw new Error("Player not found");
    const higher = Object.values(st.players)
      .filter((x) => x.nickname !== nick && x.happiness > p.happiness)
      .sort((a, b) => b.happiness - a.happiness);
    if (!higher.length) {
      const oldScore = p.happiness;
      p.happiness += 6;
      p.updatedAt = Date.now();
      const msg = `榜首巡礼：${nick} 已是最高分仍触发换分奇遇，再拿 +6 分（${p.happiness} 分）！`;
      pushStaticTicker(st, msg);
      saveStaticKv(st);
      return { ok: true, topBonus: true, oldScore, newScore: p.happiness, targetNickname: null, tickerMessage: msg, leaderboard: sortBoard(st), ticker: st.ticker };
    }
    const weights = higher.map((_, i) => i + 1);
    let r = Math.random() * weights.reduce((a, b) => a + b, 0);
    let pickedIdx = 0;
    for (let i = 0; i < weights.length; i++) {
      r -= weights[i];
      if (r <= 0) {
        pickedIdx = i;
        break;
      }
    }
    const target = higher[pickedIdx];
    const oldScore = p.happiness;
    const targetOld = target.happiness;
    p.happiness = targetOld;
    target.happiness = oldScore;
    p.updatedAt = Date.now();
    target.updatedAt = Date.now();
    const msg = `吃瓜快讯：${nick} ${reason}，发动「高位交换」把「${target.nickname}」的 ${targetOld} 分收入囊中！`;
    pushStaticTicker(st, msg);
    saveStaticKv(st);
    return {
      ok: true,
      topBonus: false,
      oldScore,
      newScore: p.happiness,
      targetNickname: target.nickname,
      targetOldScore: targetOld,
      poolSize: higher.length,
      targetRankInHigherPool: pickedIdx + 1,
      tickerMessage: msg,
      leaderboard: sortBoard(st),
      ticker: st.ticker,
    };
  }
  return { ok: false };
}

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

export async function apiRegister(owner, nickname, pin) {
  try {
    return await requestJson("./api/register", {
      method: "POST",
      body: JSON.stringify({ owner, nickname, pin }),
    });
  } catch (err) {
    if (isStaticFallbackNeeded(err)) {
      return handleStaticFallback("register", { owner, nickname, pin });
    }
    throw err;
  }
}

export async function apiUpdateScore(nickname, pin, owner, happiness, tickerMessage = "") {
  try {
    return await requestJson("./api/score", {
      method: "POST",
      body: JSON.stringify({ nickname, pin, owner, happiness, tickerMessage }),
    });
  } catch (err) {
    if (isStaticFallbackNeeded(err)) {
      return handleStaticFallback("score", { nickname, pin, owner, happiness, tickerMessage });
    }
    throw err;
  }
}

export async function apiTriggerSwap(nickname, pin, reason) {
  try {
    return await requestJson("./api/swap", {
      method: "POST",
      body: JSON.stringify({ nickname, pin, reason }),
    });
  } catch (err) {
    if (isStaticFallbackNeeded(err)) {
      return handleStaticFallback("swap", { nickname, pin, reason });
    }
    throw err;
  }
}

export async function apiGetLeaderboard() {
  try {
    return await requestJson("./api/leaderboard", { method: "GET" });
  } catch (err) {
    if (isStaticFallbackNeeded(err)) {
      return handleStaticFallback("leaderboard");
    }
    throw err;
  }
}

export async function apiAskBruce(payload = {}) {
  try {
    return await requestJson("./api/bruce-ai", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  } catch (_) {
    let hubData = null;
    try {
      const resp = await fetch("./data/hub_deepseek.json");
      if (resp.ok) hubData = await resp.json();
    } catch (__) {}

    const owner = payload.owner === "Meya" ? "Meya" : "Alex";
    if (payload.mode === "suggest_names") {
      const ob = hubData?.onboarding_pack || {};
      const names = (owner === "Meya" ? ob.meya_names : ob.alex_names) || ["奶油领巾侠", "太阳蛋邻居", "黑胶散步家", "早八冰美式"];
      const greets = (owner === "Meya" ? ob.meya_greetings : ob.alex_greetings) || ["布鲁斯正贴在门缝边闻你的味道呢，快推门进来！"];
      return {
        ok: true,
        mode: "suggest_names",
        owner,
        names,
        greeting: greets[Math.floor(Math.random() * greets.length)],
        source: "static",
      };
    }

    const msg = String(payload.message || "").trim();
    const sulking = Boolean(payload.sulking);
    const rules = hubData?.offline_chat_replies || [];
    for (const rule of rules) {
      if (Array.isArray(rule.keywords) && rule.keywords.some((k) => msg.includes(k))) {
        return {
          ok: true,
          mode: "chat",
          reply: rule.reply,
          cue: rule.cue || "BRUCE · 心有灵犀",
          action: rule.action || "roll_over",
          sincerityDelta: sulking ? 1 : 0,
          source: "static",
        };
      }
    }
    return {
      ok: true,
      mode: "chat",
      reply: sulking
        ? "还在冷战期呢，除非你去零食柜挑一块牛肉干，或者再好好哄哄我！"
        : "耳朵听见啦！要不要趁着阳光好，点一下让我翻肚皮给你摸？",
      cue: sulking ? "BRUCE · 冷战傲娇" : "BRUCE · 歪头回应",
      action: sulking ? "airplane_ears" : "roll_over",
      sincerityDelta: 0,
      source: "static",
    };
  }
}
