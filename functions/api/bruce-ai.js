// EdgeOne Pages Function: POST /api/bruce-ai
// Securely proxies DeepSeek chat/nickname requests when DEEPSEEK_API_KEY is configured in EdgeOne env,
// and degrades gracefully to rich curated local replies when running without an API key.

import { jsonResponse } from "./_shared.js";

const VALID_ACTIONS = new Set(["roll_over", "lick_paw", "play_bow", "airplane_ears", "walk", "idle"]);
const FORBIDDEN_RE = /\u676d\u5dde|\u897f\u6e56|\u94b1\u5858\u6c5f|\u7075\u9690\u5bfa|\u9f99\u4e95|\u5b8b\u57ce|\u6842\u82b1|\u4e09\u58a9|\u6ee8\u6c5f|\u6c5f\u5357|\u77f3\u6865|\u62f1\u6865|\u4e4c\u7bf7\u8239/;

const FALLBACK_NAMES = {
  Alex: ["早八冰美式", "天台晒毛怪", "奶油领巾侠", "唱片机管家", "顶层兜风王", "咖啡不加糖"],
  Meya: ["奶泡品鉴官", "太阳蛋邻居", "裙摆兜风猫", "黑胶散步家", "云朵棉花糖", "海风小财迷"],
};

const KEYWORD_FALLBACKS = [
  { keys: ["肚", "滚", "揉", "可爱", "帅", "乖", "聪明"], action: "roll_over", cue: "BRUCE · 顺毛打滚", reply: "哼，算你会说话，那就勉为其难躺倒给你揉两把奶油肚皮吧！", delta: 1 },
  { keys: ["饿", "肉", "冻干", "三文鱼", "饼干", "奶泡", "吃", "馋"], action: "lick_paw", cue: "BRUCE · 馋哭舔爪", reply: "听到好吃的我先舔干净前爪准备开饭，别光画大饼呀！", delta: 1 },
  { keys: ["玩", "球", "出门", "散步", "晒", "懒腰", "走"], action: "play_bow", cue: "BRUCE · 邀玩起势", reply: "尾巴已经摇成高速马达了，前胸贴地发车，快跟上我的短腿节奏！", delta: 1 },
  { keys: ["来", "过来", "这里", "抱", "脚边"], action: "walk", cue: "BRUCE · 哒哒跑来", reply: "听见呼唤啦，四条小短腿这就踩着地板哒哒走过来！", delta: 0 },
  { keys: ["加班", "手机", "微信", "开会", "老板", "忙", "工作", "不玩"], action: "airplane_ears", cue: "BRUCE · 委屈飞机耳", reply: "又提手机和加班……耳朵立刻折叠成飞机耳模式以示抗议！", delta: -1 },
  { keys: ["对不起", "错", "哄", "原谅", "赔罪", "求"], action: "play_bow", cue: "BRUCE · 心软破冰", reply: "看你态度这么诚恳的份上，原谅你一半……另一半拿小肉干来抵！", delta: 2 },
];

function getDeepSeekKey(env) {
  if (env && typeof env.DEEPSEEK_API_KEY === "string" && env.DEEPSEEK_API_KEY.trim()) {
    return env.DEEPSEEK_API_KEY.trim();
  }
  if (typeof globalThis !== "undefined" && typeof globalThis.DEEPSEEK_API_KEY === "string" && globalThis.DEEPSEEK_API_KEY.trim()) {
    return globalThis.DEEPSEEK_API_KEY.trim();
  }
  return "";
}

function buildFallbackResponse(body) {
  const mode = body?.mode === "suggest_names" ? "suggest_names" : "chat";
  const owner = body?.owner === "Meya" ? "Meya" : "Alex";
  if (mode === "suggest_names") {
    const names = FALLBACK_NAMES[owner];
    const greeting =
      owner === "Meya"
        ? "听见脚步声就知道是 Meya 啦，快进来摸摸我的酒红真丝领巾！"
        : "Alex 带我先占好阳台上最暖那块阳光，推门进来就能一起晒毛啦。";
    return { ok: true, mode, owner, names, greeting, source: "fallback" };
  }

  const msg = String(body?.message || "").trim();
  const sulking = Boolean(body?.sulking);
  for (const rule of KEYWORD_FALLBACKS) {
    if (rule.keys.some((k) => msg.includes(k))) {
      return {
        ok: true,
        mode: "chat",
        reply: rule.reply,
        cue: rule.cue,
        action: sulking && rule.delta <= 0 ? "airplane_ears" : rule.action,
        sincerityDelta: sulking ? Math.max(0, rule.delta) : rule.delta,
        source: "fallback",
      };
    }
  }
  return {
    ok: true,
    mode: "chat",
    reply: sulking
      ? "还在冷战期呢……除非你夸夸我的长毛或者去开零食急救柜。"
      : "耳朵动了一下表示我听见啦！要不要带我在地毯上打个滚？",
    cue: sulking ? "BRUCE · 冷战傲娇" : "BRUCE · 歪头回应",
    action: sulking ? "airplane_ears" : "roll_over",
    sincerityDelta: 0,
    source: "fallback",
  };
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "POST, OPTIONS",
      "access-control-allow-headers": "Content-Type",
    },
  });
}

export async function onRequestPost(context) {
  let body = {};
  try {
    body = await context.request.json();
  } catch (_) {
    return jsonResponse({ ok: false, error: "请求格式不正确" }, 400);
  }

  const apiKey = getDeepSeekKey(context.env);
  if (!apiKey) {
    return jsonResponse(buildFallbackResponse(body));
  }

  const mode = body?.mode === "suggest_names" ? "suggest_names" : "chat";
  const owner = body?.owner === "Meya" ? "Meya" : "Alex";
  const nickname = String(body?.nickname || "新邻居").slice(0, 12);
  const happiness = Number.isFinite(body?.happiness) ? Number(body.happiness) : 100;
  const sulking = Boolean(body?.sulking || happiness < 80);
  const sceneName = body?.scene === "cafe" ? "海岸烘焙室" : body?.scene === "warehouse" ? "ELOWEN 有机市集" : "双层阳光客厅";

  const systemPrompt =
    mode === "suggest_names"
      ? `你是治愈 3D 小狗游戏《布鲁斯日常 · 幸福指数俱乐部》的迎宾文案师。主角是系酒红领巾的奶油长毛腊肠犬布鲁斯，当前搭档是 ${owner}。严禁出现任何真实城市/景点/地域词。输出 JSON：{"names": [6个2-8字、至少含1个汉字且无空格的俏皮中文昵称], "greeting": "1条16-30字布鲁斯隔门撒娇迎宾语"}。`
      : `你是《布鲁斯日常》里的 3D 奶油长毛腊肠犬布鲁斯（系酒红真丝领巾），正和 ${owner} 的伙伴「${nickname}」待在「${sceneName}」。当前幸福指数 ${happiness}${sulking ? "（<80冷战期，委屈但哄一哄也会心软）" : "（开心粘人中）"}。严禁出现任何真实城市/景点/地域词。
严格输出 JSON：
{
  "reply": "布鲁斯第一人称口语回应（14-36字，有画面感与傲娇温度，不堆表情）",
  "cue": "BRUCE · 四字状态标签",
  "action": "必须从 roll_over(翻肚皮撒娇) / lick_paw(舔爪馋嘴) / play_bow(撅屁股邀玩) / airplane_ears(委屈抗议) / walk(走过去凑近) / idle 中选最贴合这句回复的一个",
  "sincerityDelta": -1到3之间的整数（冷战期真诚道歉/肉干诚意哄狗给+1~+3，逗开心给+1，敷衍提加班/手机给-1，普通闲聊0）
}`;

  const userPrompt =
    mode === "suggest_names"
      ? `请为选择了 ${owner} 的新住户生成 6 个不撞款的可爱中文昵称灵感，并附一句布鲁斯的迎宾台词。`
      : `玩家刚刚对布鲁斯说：「${String(body?.message || "你好").slice(0, 80)}」`;

  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    const resp = await fetch("https://api.deepseek.com/chat/completions", {
      method: "POST",
      signal: controller.signal,
      headers: {
        "content-type": "application/json",
        authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: "deepseek-chat",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt },
        ],
        response_format: { type: "json_object" },
        temperature: 0.9,
      }),
    });
    clearTimeout(timer);

    if (!resp.ok) {
      return jsonResponse(buildFallbackResponse(body));
    }
    const payload = await resp.json();
    const parsed = JSON.parse(payload?.choices?.[0]?.message?.content || "{}");
    const rawStr = JSON.stringify(parsed);
    if (FORBIDDEN_RE.test(rawStr)) {
      return jsonResponse(buildFallbackResponse(body));
    }

    if (mode === "suggest_names") {
      const names = (Array.isArray(parsed.names) ? parsed.names : [])
        .map((s) => String(s || "").replace(/\s+/g, "").trim())
        .filter((s) => s.length >= 2 && s.length <= 10 && /[\u4e00-\u9fff]/.test(s));
      if (!names.length) return jsonResponse(buildFallbackResponse(body));
      return jsonResponse({
        ok: true,
        mode,
        owner,
        names: names.slice(0, 6),
        greeting: String(parsed.greeting || "").trim() || buildFallbackResponse(body).greeting,
        source: "deepseek",
      });
    }

    const action = VALID_ACTIONS.has(parsed.action) ? parsed.action : "roll_over";
    const delta = Math.max(-1, Math.min(3, Math.round(Number(parsed.sincerityDelta) || 0)));
    const reply = String(parsed.reply || "").trim();
    if (!reply) return jsonResponse(buildFallbackResponse(body));

    return jsonResponse({
      ok: true,
      mode: "chat",
      reply,
      cue: String(parsed.cue || "BRUCE · 灵动回应").slice(0, 24),
      action,
      sincerityDelta: delta,
      source: "deepseek",
    });
  } catch (_) {
    return jsonResponse(buildFallbackResponse(body));
  }
}
