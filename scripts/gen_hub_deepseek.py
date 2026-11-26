#!/usr/bin/env python3
"""Generate 3D Living Room Hub inner monologues and portal wishes via DeepSeek API."""

import json
import os
import re
import urllib.error
import urllib.request

ENV_PATH = "/Users/alex/.gemini/antigravity/scratch/ai-pulse-radar/.env"
OUT_PATH = "/Users/alex/.gemini/antigravity/scratch/bruce-happiness-club/data/hub_deepseek.json"

FORBIDDEN_WORDS = (
    "杭州",
    "西湖",
    "钱塘江",
    "灵隐寺",
    "龙井",
    "宋城",
    "桂花",
    "三墩",
    "滨江",
    "江南",
    "石桥",
    "拱桥",
    "乌篷船",
)

SYSTEM_PROMPT = """你是《布鲁斯日常 · 幸福指数俱乐部》3D 客厅主基地的首席角色台词策划。
主角设定：
- 布鲁斯（Bruce）：一只奶油长毛腊肠犬，脖子上系着酒红色斜纹真丝领巾，性格傲娇、精致又粘人。
- 主人：20 岁出头、时髦松弛的年轻情侣/搭档 Alex 与 Meya，住在阳光通透的现代极简客厅里。
- 严格禁令：绝对禁止出现任何真实中国或国际具体城市名/景点或地域刻板词，尤其严禁出现：杭州、西湖、钱塘江、灵隐寺、龙井、宋城、桂花、三墩、滨江、江南、石桥、拱桥、乌篷船！
- 文风要求：全部用轻快、傲娇、可爱、有画面感的现代口语中文，不要说教，不要表情符号堆砌。

请严格输出 JSON，不要包含 Markdown 代码块之外的多余文字，顶层必须严格包含以下 3 个键：
1. "thought_bubbles": 对象，包含以下 8 个字符串数组字段，每条控制在 12~26 个汉字以内：
   - "idle_happy": 6条（布鲁斯趴在客厅地毯晒太阳发呆、等主人摸摸的内心戏）
   - "idle_sulk": 6条（幸福指数低于80进入冷战期，布鲁斯背对主人小声哼唧讨零食的内心戏）
   - "click_poke": 6条（玩家在 3D 客厅直接点击/戳一戳布鲁斯时，布鲁斯的傲娇或撒娇反应）
   - "click_poke_sulk": 4条（冷战期被玩家戳一戳时，布鲁斯不情愿但又忍不住摇一下尾巴的反差反应）
   - "petting_bliss": 5条（正在顺毛享受时的舒服低哼或小骄傲）
   - "ear_warn": 4条（顺毛太快触发“飞机耳预警”时的小警告）
   - "rain_cozy": 4条（下雨天擦爪、盖毛毯、听黑胶唱片时的惬意念叨）
   - "ball_excited": 4条（客厅追网球时的兴奋冲刺台词）
2. "portal_hover": 对象，当玩家鼠标悬停或靠近 3D 客厅的三个传送点时，布鲁斯头顶浮现的简短好奇台词（每条 14~26 个汉字）：
   - "street": 门口出门去林荫小街探店/遛弯的好奇心
   - "warehouse": 幻想坐进会员制大超市超大购物车的好奇心
   - "global": 盯着墙上旅行相框墙幻想远方假期的好奇心
3. "destination_wishes": 对象，布鲁斯第一人称的旅行心愿单（每条 30~50 个汉字）：
   - "warehouse": 坐进巨大购物车逛肉类冷柜与试吃三文鱼的心愿
   - "nordic": 北欧峡湾木屋壁炉边盖毛毯听海风的心愿
   - "california": 坐敞篷车沿阳光海岸吹风戴墨镜的心愿
   - "nz_swiss": 在雪山下的绿色牧场草坡打滚奔跑的心愿
   - "yacht": 在白色帆船游艇甲板上吹海风晒太阳的心愿
"""

USER_PROMPT = "请为 3D 阳光客厅里的奶油长毛腊肠犬布鲁斯，生成一套鲜活、不重复、符合傲娇精致小狗人设的 JSON 台词包。"


def load_keys():
    env_map = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env_map[k.strip()] = v.strip().strip('"').strip("'")
    keys = []
    for name in ("DEEPSEEK_API_KEY", "DEEPSEEK_API_KEY_FALLBACK"):
        val = os.environ.get(name) or env_map.get(name, "")
        if val and val not in keys:
            keys.append(val)
    return keys


def call_deepseek(keys, system_prompt: str, user_prompt: str, temperature: float = 0.88) -> dict:
    last_err = None
    for idx, key in enumerate(keys, start=1):
        try:
            payload = json.dumps({
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": temperature,
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.deepseek.com/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            return json.loads(body["choices"][0]["message"]["content"])
        except urllib.error.HTTPError as exc:
            err_body = ""
            try:
                err_body = exc.read().decode("utf-8", errors="replace")[:200]
            except Exception:
                pass
            last_err = f"key #{idx}: HTTP {exc.code} {err_body}".strip()
        except Exception as exc:
            last_err = f"key #{idx}: {type(exc).__name__}: {exc}"
    raise RuntimeError(last_err or "DeepSeek API failed")


def validate_payload(data: dict):
    required_bubbles = {
        "idle_happy": 6,
        "idle_sulk": 6,
        "click_poke": 6,
        "click_poke_sulk": 4,
        "petting_bliss": 5,
        "ear_warn": 4,
        "rain_cozy": 4,
        "ball_excited": 4,
    }
    bubbles = data.get("thought_bubbles")
    if not isinstance(bubbles, dict):
        raise ValueError("Missing thought_bubbles object")
    for k, min_len in required_bubbles.items():
        arr = bubbles.get(k)
        if not isinstance(arr, list) or len(arr) < min_len or not all(isinstance(s, str) and s.strip() for s in arr):
            raise ValueError(f"Invalid thought_bubbles.{k}")

    portal = data.get("portal_hover")
    if not isinstance(portal, dict):
        raise ValueError("Missing portal_hover object")
    for k in ("street", "warehouse", "global"):
        if not isinstance(portal.get(k), str) or not portal[k].strip():
            raise ValueError(f"Invalid portal_hover.{k}")

    wishes = data.get("destination_wishes")
    if not isinstance(wishes, dict):
        raise ValueError("Missing destination_wishes object")
    for k in ("warehouse", "nordic", "california", "nz_swiss", "yacht"):
        if not isinstance(wishes.get(k), str) or not wishes[k].strip():
            raise ValueError(f"Invalid destination_wishes.{k}")

    serialized = json.dumps(data, ensure_ascii=False)
    hits = [w for w in FORBIDDEN_WORDS if re.search(re.escape(w), serialized)]
    if hits:
        raise ValueError(f"Forbidden regional terms found: {hits}")


def main():
    keys = load_keys()
    if not keys:
        raise RuntimeError("No DeepSeek API key found")

    raw = call_deepseek(keys, SYSTEM_PROMPT, USER_PROMPT, temperature=0.88)
    validate_payload(raw)

    out = {
        "meta": {
            "generator": "deepseek-chat",
            "purpose": "3D Living Room Hub dynamic inner monologues & portal wishes",
        },
        "thought_bubbles": raw["thought_bubbles"],
        "portal_hover": raw["portal_hover"],
        "destination_wishes": raw["destination_wishes"],
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Wrote DeepSeek 3D hub copy to {OUT_PATH}")


if __name__ == "__main__":
    main()
