#!/usr/bin/env python3
"""Local dev server mirroring EdgeOne Pages static hosting + /api/* KV endpoints."""

import argparse
import hashlib
import json
import mimetypes
import os
import random
import re
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

MIME_OVERRIDES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".glb": "model/gltf-binary",
    ".gltf": "model/gltf+json",
    ".svg": "image/svg+xml",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".mp4": "video/mp4",
}

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KV_FILE = os.path.join(ROOT_DIR, ".local_kv.json")
CONTENT_FILE = os.path.join(ROOT_DIR, "data", "content.json")
HUB_DEEPSEEK_FILE = os.path.join(ROOT_DIR, "data", "hub_deepseek.json")
LOCAL_ENV_FILE = os.path.join(ROOT_DIR, ".env")
FALLBACK_ENV_FILE = "/Users/alex/.gemini/antigravity/scratch/ai-pulse-radar/.env"
FORBIDDEN_RE = re.compile(r"杭州|西湖|钱塘江|灵隐寺|龙井|宋城|桂花|三墩|滨江|江南|石桥|拱桥|乌篷船")
VALID_AI_ACTIONS = {"roll_over", "lick_paw", "play_bow", "airplane_ears", "walk", "idle"}
LOCK = threading.Lock()


def load_deepseek_key():
    env_map = {}
    for p in (FALLBACK_ENV_FILE, LOCAL_ENV_FILE):
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        s = line.strip()
                        if s and not s.startswith("#") and "=" in s:
                            k, v = s.split("=", 1)
                            env_map[k.strip()] = v.strip().strip('"').strip("'")
            except Exception:
                pass
    return os.environ.get("DEEPSEEK_API_KEY") or env_map.get("DEEPSEEK_API_KEY", "")


def fallback_bruce_ai(body):
    mode = "suggest_names" if body.get("mode") == "suggest_names" else "chat"
    owner = "Meya" if body.get("owner") == "Meya" else "Alex"
    hub_data = {}
    try:
        if os.path.exists(HUB_DEEPSEEK_FILE):
            with open(HUB_DEEPSEEK_FILE, "r", encoding="utf-8") as f:
                hub_data = json.load(f)
    except Exception:
        pass
    if mode == "suggest_names":
        ob = hub_data.get("onboarding_pack", {})
        names = ob.get("meya_names" if owner == "Meya" else "alex_names") or ["奶油领巾侠", "太阳蛋邻居", "黑胶散步家", "早八冰美式"]
        greets = ob.get("meya_greetings" if owner == "Meya" else "alex_greetings") or ["布鲁斯正隔着门缝闻到你的味道啦，快推门进来！"]
        return {"ok": True, "mode": "suggest_names", "owner": owner, "names": names[:6], "greeting": random.choice(greets), "source": "fallback"}
    msg = str(body.get("message", "")).strip()
    sulking = bool(body.get("sulking"))
    for item in hub_data.get("offline_chat_replies", []):
        if any(k in msg for k in item.get("keywords", [])):
            return {
                "ok": True,
                "mode": "chat",
                "reply": item["reply"],
                "cue": item.get("cue", "BRUCE · 心有灵犀"),
                "action": item.get("action", "roll_over"),
                "sincerityDelta": 1 if sulking else 0,
                "source": "fallback",
            }
    return {
        "ok": True,
        "mode": "chat",
        "reply": "冷战期还没消气呢，除非你去零食柜拿一块肉干来哄我！" if sulking else "小耳朵动了一下！要不要让我给你翻个肚皮打滚呀？",
        "cue": "BRUCE · 冷战傲娇" if sulking else "BRUCE · 歪头回应",
        "action": "airplane_ears" if sulking else "roll_over",
        "sincerityDelta": 0,
        "source": "fallback",
    }


def call_deepseek_live(body):
    key = load_deepseek_key()
    if not key:
        return fallback_bruce_ai(body)
    mode = "suggest_names" if body.get("mode") == "suggest_names" else "chat"
    owner = "Meya" if body.get("owner") == "Meya" else "Alex"
    nickname = str(body.get("nickname") or "新邻居")[:12]
    happiness = int(body.get("happiness", 100)) if str(body.get("happiness", "")).isdigit() else 100
    sulking = bool(body.get("sulking") or happiness < 80)
    scene_name = "海岸咖啡馆" if body.get("scene") == "cafe" else "顶层阳光客厅"

    if mode == "suggest_names":
        sys_p = (
            f"你是治愈 3D 小狗游戏《布鲁斯日常 · 幸福指数俱乐部》的迎宾文案师。主角是系酒红领巾的奶油长毛腊肠犬布鲁斯，当前搭档是 {owner}。"
            '严禁出现任何真实城市/景点/地域词。输出 JSON：{"names":[6个2-8字含汉字无空格昵称],"greeting":"1条16-30字隔门撒娇迎宾语"}。'
        )
        usr_p = f"请为选择了 {owner} 的新住户生成 6 个好玩可爱的中文昵称，并附一句布鲁斯的迎宾词。"
    else:
        sys_p = (
            f"你是《布鲁斯日常》里的 3D 奶油长毛腊肠犬布鲁斯（系酒红真丝领巾），正和 {owner} 的伙伴「{nickname}」待在「{scene_name}」。"
            f"当前幸福指数 {happiness}{'（<80冷战期，委屈但哄一哄也会心软）' if sulking else '（开心粘人中）'}。严禁出现任何真实城市/景点/地域词。"
            '严格输出 JSON：{"reply":"14-36字傲娇有温度的第一人称回应","cue":"BRUCE · 四字状态","action":"roll_over|lick_paw|play_bow|airplane_ears|walk|idle","sincerityDelta":-1到3整数}'
        )
        usr_p = f"玩家刚刚对布鲁斯说：「{str(body.get('message', '你好'))[:80]}」"

    try:
        req = urllib.request.Request(
            "https://api.deepseek.com/chat/completions",
            data=json.dumps({
                "model": "deepseek-chat",
                "messages": [{"role": "system", "content": sys_p}, {"role": "user", "content": usr_p}],
                "response_format": {"type": "json_object"},
                "temperature": 0.9,
            }).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=14) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
        parsed = json.loads(raw["choices"][0]["message"]["content"])
        if FORBIDDEN_RE.search(json.dumps(parsed, ensure_ascii=False)):
            return fallback_bruce_ai(body)
        if mode == "suggest_names":
            names = [re.sub(r"\s+", "", str(x)).strip() for x in (parsed.get("names") or [])]
            names = [x for x in names if 2 <= len(x) <= 10 and re.search(r"[\u4e00-\u9fff]", x)]
            if not names:
                return fallback_bruce_ai(body)
            return {
                "ok": True,
                "mode": "suggest_names",
                "owner": owner,
                "names": names[:6],
                "greeting": str(parsed.get("greeting") or "").strip() or fallback_bruce_ai(body)["greeting"],
                "source": "deepseek",
            }
        act = parsed.get("action", "roll_over")
        if act not in VALID_AI_ACTIONS:
            act = "roll_over"
        delta = max(-1, min(3, int(round(float(parsed.get("sincerityDelta", 0))))))
        reply = str(parsed.get("reply") or "").strip()
        if not reply:
            return fallback_bruce_ai(body)
        return {
            "ok": True,
            "mode": "chat",
            "reply": reply,
            "cue": str(parsed.get("cue") or "BRUCE · 灵动回应")[:24],
            "action": act,
            "sincerityDelta": delta,
            "source": "deepseek",
        }
    except Exception:
        return fallback_bruce_ai(body)

DEFAULT_SEED_PLAYERS = [
    {"nickname": "早八起不来星人", "owner": "Alex", "happiness": 138},
    {"nickname": "冰美式续命侠", "owner": "Meya", "happiness": 126},
    {"nickname": "期末周摸鱼冠军", "owner": "Alex", "happiness": 118},
    {"nickname": "头等舱小腊肠", "owner": "Meya", "happiness": 112},
    {"nickname": "游艇甲板晒太阳", "owner": "Alex", "happiness": 105},
    {"nickname": "周末躺平选手", "owner": "Meya", "happiness": 96},
    {"nickname": "低头回微信扣分王", "owner": "Alex", "happiness": 86},
    {"nickname": "雨天踩坑冷战中", "owner": "Meya", "happiness": 74},
]

DEFAULT_TICKER = [
    {"id": "seed-1", "text": "快讯：早八起不来星人 带着布鲁斯打卡宠友咖啡馆，暂居全服第 1！", "ts": int(time.time() * 1000) - 180000},
    {"id": "seed-2", "text": "吃瓜：低头回微信扣分王 连续点开 3 条消息，布鲁斯直接坐到手机屏幕上抗议。", "ts": int(time.time() * 1000) - 90000},
    {"id": "seed-3", "text": "冷战播报：雨天踩坑冷战中 正在别墅客厅掏分哄狗，祝他抽中 96% 和牛礼盒。", "ts": int(time.time() * 1000) - 30000},
]


def hash_pin(pin: str) -> str:
    return hashlib.sha256(f"bruce-salt:{pin}".encode("utf-8")).hexdigest()[:16]


def validate_nickname(raw: str):
    nick = str(raw or "").strip()
    if len(nick) < 2 or len(nick) > 12:
        return False, "昵称长度需在 2 到 12 个字之间"
    if re.search(r"\s", nick):
        return False, "昵称里请不要包含空格"
    if not re.search(r"[\u4e00-\u9fff]", nick):
        return False, "昵称不能为纯数字或纯字母，必须至少包含 1 个中文字符"
    return True, nick


def validate_pin(raw: str):
    pin = str(raw or "").strip()
    if not re.fullmatch(r"\d{4}", pin):
        return False, "请设置 4 位数字暗号（用于防同学冒用或换设备找回）"
    return True, pin


def load_seed_players():
    if os.path.exists(CONTENT_FILE):
        try:
            with open(CONTENT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            seeds = data.get("seed_players")
            if isinstance(seeds, list) and len(seeds) >= 4:
                return seeds
        except Exception:
            pass
    return DEFAULT_SEED_PLAYERS


def load_kv():
    if os.path.exists(KV_FILE):
        try:
            with open(KV_FILE, "r", encoding="utf-8") as f:
                st = json.load(f)
            if isinstance(st, dict) and isinstance(st.get("players"), dict):
                st.setdefault("ticker", [])
                return st
        except Exception:
            pass
    now = int(time.time() * 1000)
    players = {}
    for idx, p in enumerate(load_seed_players()):
        nick = p["nickname"]
        players[nick] = {
            "nickname": nick,
            "pinHash": hash_pin("0000"),
            "owner": p.get("owner", "Alex"),
            "happiness": int(p.get("happiness", 100)),
            "updatedAt": now - idx * 60000,
            "isSeed": True,
        }
    st = {"players": players, "ticker": list(DEFAULT_TICKER)}
    save_kv(st)
    return st


def save_kv(st):
    st["ticker"] = st.get("ticker", [])[:25]
    with open(KV_FILE, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


def push_ticker(st, text: str):
    if not text:
        return
    st.setdefault("ticker", []).insert(0, {
        "id": f"{int(time.time()*1000)}-{random.randint(1000,9999)}",
        "text": str(text)[:140],
        "ts": int(time.time() * 1000),
    })
    st["ticker"] = st["ticker"][:25]


def sorted_leaderboard(st):
    items = []
    for p in st.get("players", {}).values():
        h = int(p.get("happiness", 0))
        items.append({
            "nickname": p["nickname"],
            "owner": p.get("owner", "Alex"),
            "happiness": h,
            "updatedAt": p.get("updatedAt", 0),
            "mood": "happy" if h >= 80 else "sulking",
        })
    items.sort(key=lambda x: (-x["happiness"], -x["updatedAt"]))
    for idx, item in enumerate(items, start=1):
        item["rank"] = idx
    return items


def select_meaning_a(st, nickname: str):
    cur = st["players"][nickname]
    higher = [
        p for p in st["players"].values()
        if p["nickname"] != nickname and int(p["happiness"]) > int(cur["happiness"])
    ]
    higher.sort(key=lambda p: -int(p["happiness"]))
    if not higher:
        return None
    weights = [i + 1 for i in range(len(higher))]
    chosen_idx = random.choices(range(len(higher)), weights=weights, k=1)[0]
    return higher[chosen_idx], len(higher), chosen_idx + 1


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send_json(self, payload, status=200):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=UTF-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/leaderboard":
            with LOCK:
                st = load_kv()
                return self._send_json({"ok": True, "leaderboard": sorted_leaderboard(st), "ticker": st.get("ticker", [])})

        rel = "index.html" if path == "/" else path.lstrip("/")
        target = os.path.normpath(os.path.join(ROOT_DIR, rel))
        if not target.startswith(ROOT_DIR) or not os.path.isfile(target):
            self.send_error(404, "Not Found")
            return
        ext = os.path.splitext(target)[1].lower()
        ctype = MIME_OVERRIDES.get(ext) or mimetypes.guess_type(target)[0]
        with open(target, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = self._read_json()
        except Exception:
            return self._send_json({"ok": False, "error": "Invalid JSON body"}, 400)

        if path == "/api/bruce-ai":
            return self._send_json(call_deepseek_live(body))

        with LOCK:
            st = load_kv()
            if path == "/api/register":
                ok, nick_or_err = validate_nickname(body.get("nickname", ""))
                if not ok:
                    return self._send_json({"ok": False, "error": nick_or_err}, 400)
                ok_pin, pin_or_err = validate_pin(body.get("pin", ""))
                if not ok_pin:
                    return self._send_json({"ok": False, "error": pin_or_err}, 400)
                owner = "Meya" if body.get("owner") == "Meya" else "Alex"
                digest = hash_pin(pin_or_err)
                existing = st["players"].get(nick_or_err)
                if existing:
                    if existing["pinHash"] != digest:
                        return self._send_json({"ok": False, "error": "该昵称已被占用（若为你本人，请输入正确的 4 位暗号恢复进度）"}, 409)
                    existing["owner"] = owner
                    existing["updatedAt"] = int(time.time() * 1000)
                    save_kv(st)
                    return self._send_json({
                        "ok": True,
                        "resumed": True,
                        "player": {"nickname": existing["nickname"], "owner": existing["owner"], "happiness": existing["happiness"]},
                        "leaderboard": sorted_leaderboard(st),
                        "ticker": st["ticker"],
                    })
                new_p = {
                    "nickname": nick_or_err,
                    "pinHash": digest,
                    "owner": owner,
                    "happiness": 100,
                    "updatedAt": int(time.time() * 1000),
                    "isSeed": False,
                }
                st["players"][nick_or_err] = new_p
                push_ticker(st, f"新人报到：{nick_or_err} 领着布鲁斯和 {owner} 搬进了新家，初始幸福 100 分！")
                save_kv(st)
                return self._send_json({
                    "ok": True,
                    "resumed": False,
                    "player": {"nickname": new_p["nickname"], "owner": new_p["owner"], "happiness": new_p["happiness"]},
                    "leaderboard": sorted_leaderboard(st),
                    "ticker": st["ticker"],
                })

            if path == "/api/score":
                nick = str(body.get("nickname", "")).strip()
                pin = str(body.get("pin", "")).strip()
                p = st["players"].get(nick)
                if not p:
                    return self._send_json({"ok": False, "error": "Player not found"}, 404)
                if p["pinHash"] != hash_pin(pin):
                    return self._send_json({"ok": False, "error": "Invalid PIN"}, 403)
                p["happiness"] = max(0, min(9999, int(round(float(body.get("happiness", 0))))))
                p["updatedAt"] = int(time.time() * 1000)
                if body.get("owner") in ("Alex", "Meya"):
                    p["owner"] = body["owner"]
                if body.get("tickerMessage"):
                    push_ticker(st, body["tickerMessage"])
                save_kv(st)
                return self._send_json({
                    "ok": True,
                    "player": {"nickname": p["nickname"], "owner": p["owner"], "happiness": p["happiness"]},
                    "leaderboard": sorted_leaderboard(st),
                    "ticker": st["ticker"],
                })

            if path == "/api/swap":
                nick = str(body.get("nickname", "")).strip()
                pin = str(body.get("pin", "")).strip()
                reason = str(body.get("reason", "陪布鲁斯触发幸运时刻")).strip()
                p = st["players"].get(nick)
                if not p:
                    return self._send_json({"ok": False, "error": "Player not found"}, 404)
                if p["pinHash"] != hash_pin(pin):
                    return self._send_json({"ok": False, "error": "Invalid PIN"}, 403)
                picked = select_meaning_a(st, nick)
                if not picked:
                    old_score = p["happiness"]
                    p["happiness"] += 6
                    p["updatedAt"] = int(time.time() * 1000)
                    msg = f"榜首巡礼：{nick} 已是全服最高分仍触发换分奇遇，顺手再拿 +6 分稳居榜首（{p['happiness']} 分）！"
                    push_ticker(st, msg)
                    save_kv(st)
                    return self._send_json({
                        "ok": True,
                        "topBonus": True,
                        "oldScore": old_score,
                        "newScore": p["happiness"],
                        "targetNickname": None,
                        "tickerMessage": msg,
                        "leaderboard": sorted_leaderboard(st),
                        "ticker": st["ticker"],
                    })
                target, pool_size, rank_in_pool = picked
                old_score = p["happiness"]
                target_old = target["happiness"]
                p["happiness"] = target_old
                target["happiness"] = old_score
                p["updatedAt"] = int(time.time() * 1000)
                target["updatedAt"] = int(time.time() * 1000)
                msg = f"吃瓜快讯：{nick} {reason}，发动「高位交换」把「{target['nickname']}」的 {target_old} 分收入囊中（原分 {old_score} 分归对方）！"
                push_ticker(st, msg)
                save_kv(st)
                return self._send_json({
                    "ok": True,
                    "topBonus": False,
                    "oldScore": old_score,
                    "newScore": p["happiness"],
                    "targetNickname": target["nickname"],
                    "targetOldScore": target_old,
                    "poolSize": pool_size,
                    "targetRankInHigherPool": rank_in_pool,
                    "tickerMessage": msg,
                    "leaderboard": sorted_leaderboard(st),
                    "ticker": st["ticker"],
                })

        return self._send_json({"ok": False, "error": "Not found"}, 404)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8781)
    parser.add_argument("--open", action="store_true", help="Open browser automatically")
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Bruce Happiness Club dev server running on {url} (also http://localhost:{args.port}/)")
    if args.open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
