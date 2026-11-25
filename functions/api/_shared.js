// Shared helpers & Meaning-A logic for Tencent Cloud EdgeOne Pages Functions + KV

const STATE_KEY = "bruce_state_v2";

const DEFAULT_SEED_PLAYERS = [
  { nickname: "早八起不来星人", owner: "Alex", happiness: 138 },
  { nickname: "冰美式续命侠", owner: "Meya", happiness: 126 },
  { nickname: "期末周摸鱼冠军", owner: "Alex", happiness: 118 },
  { nickname: "头等舱小腊肠", owner: "Meya", happiness: 112 },
  { nickname: "游艇甲板晒太阳", owner: "Alex", happiness: 105 },
  { nickname: "周末躺平选手", owner: "Meya", happiness: 96 },
  { nickname: "低头回微信扣分王", owner: "Alex", happiness: 86 },
  { nickname: "雨天踩坑冷战中", owner: "Meya", happiness: 74 },
];

const DEFAULT_TICKER = [
  { id: "seed-1", text: "快讯：早八起不来星人 带着布鲁斯打卡宠友咖啡馆，暂居全服第 1！", ts: Date.now() - 180000 },
  { id: "seed-2", text: "吃瓜：低头回微信扣分王 连续点开 3 条消息，布鲁斯直接坐到手机屏幕上抗议。", ts: Date.now() - 90000 },
  { id: "seed-3", text: "冷战播报：雨天踩坑冷战中 正在别墅客厅掏分哄狗，祝他抽中 96% 和牛礼盒。", ts: Date.now() - 30000 },
];

export function getKv(env) {
  if (env && env.BRUCE_KV) return env.BRUCE_KV;
  if (typeof globalThis !== "undefined" && globalThis.BRUCE_KV) return globalThis.BRUCE_KV;
  return null;
}

export function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=UTF-8",
      "cache-control": "no-store",
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "GET, POST, OPTIONS",
      "access-control-allow-headers": "Content-Type",
    },
  });
}

export function validateNickname(raw) {
  const nickname = String(raw || "").trim();
  if (nickname.length < 2 || nickname.length > 12) {
    return { ok: false, error: "昵称长度需在 2 到 12 个字之间" };
  }
  if (/\s/.test(nickname)) {
    return { ok: false, error: "昵称里请不要包含空格" };
  }
  if (!/[\u4e00-\u9fff]/.test(nickname)) {
    return { ok: false, error: "昵称不能为纯数字或纯字母，必须至少包含 1 个中文字符" };
  }
  return { ok: true, nickname };
}

export function validatePin(raw) {
  const pin = String(raw || "").trim();
  if (!/^\d{4}$/.test(pin)) {
    return { ok: false, error: "请设置 4 位数字暗号（用于防同学冒用或换设备找回）" };
  }
  return { ok: true, pin };
}

export function hashPin(pin) {
  let h = 2166136261;
  const s = `bruce-salt:${pin}`;
  for (let i = 0; i < s.length; i += 1) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0).toString(16);
}

export async function loadState(kv) {
  const raw = await kv.get(STATE_KEY);
  if (raw) {
    try {
      const parsed = JSON.parse(raw);
      if (parsed && parsed.players && typeof parsed.players === "object") {
        if (!Array.isArray(parsed.ticker)) parsed.ticker = [];
        return parsed;
      }
    } catch (_) {
      // re-seed
    }
  }
  const players = {};
  const now = Date.now();
  DEFAULT_SEED_PLAYERS.forEach((p, idx) => {
    players[p.nickname] = {
      nickname: p.nickname,
      pinHash: hashPin("0000"),
      owner: p.owner,
      happiness: p.happiness,
      updatedAt: now - idx * 60000,
      isSeed: true,
    };
  });
  const initial = { players, ticker: DEFAULT_TICKER.slice() };
  await kv.put(STATE_KEY, JSON.stringify(initial));
  return initial;
}

export async function saveState(kv, state) {
  state.ticker = (state.ticker || []).slice(0, 25);
  await kv.put(STATE_KEY, JSON.stringify(state));
}

export function pushTicker(state, text) {
  if (!text) return;
  state.ticker = state.ticker || [];
  state.ticker.unshift({
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    text: String(text).slice(0, 140),
    ts: Date.now(),
  });
  state.ticker = state.ticker.slice(0, 25);
}

export function buildSortedLeaderboard(state) {
  const list = Object.values(state.players || {}).map((p) => ({
    nickname: p.nickname,
    owner: p.owner,
    happiness: Number(p.happiness) || 0,
    updatedAt: p.updatedAt || 0,
    mood: (Number(p.happiness) || 0) >= 80 ? "happy" : "sulking",
  }));
  list.sort((a, b) => {
    if (b.happiness !== a.happiness) return b.happiness - a.happiness;
    return (b.updatedAt || 0) - (a.updatedAt || 0);
  });
  return list.map((item, idx) => ({ ...item, rank: idx + 1 }));
}

export function selectMeaningATarget(state, currentNickname) {
  const current = state.players[currentNickname];
  if (!current) return null;
  const higher = Object.values(state.players)
    .filter((p) => p.nickname !== currentNickname && Number(p.happiness) > Number(current.happiness))
    .sort((a, b) => b.happiness - a.happiness);

  if (higher.length === 0) return null;

  const totalWeight = (higher.length * (higher.length + 1)) / 2;
  let roll = Math.random() * totalWeight;
  for (let i = 0; i < higher.length; i += 1) {
    const weight = i + 1;
    roll -= weight;
    if (roll <= 0) {
      return {
        target: higher[i],
        poolSize: higher.length,
        targetRankInHigherPool: i + 1,
      };
    }
  }
  return {
    target: higher[higher.length - 1],
    poolSize: higher.length,
    targetRankInHigherPool: higher.length,
  };
}
