#!/usr/bin/env python3
"""Enrich data/hub_deepseek.json with DeepSeek onboarding pack, offline chat replies, and action dialogue."""

import json
import os
import re
import urllib.error
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_ENV_PATH = os.path.join(REPO_ROOT, ".env")
FALLBACK_ENV_PATH = "/Users/alex/.gemini/antigravity/scratch/ai-pulse-radar/.env"
HUB_JSON_PATH = os.path.join(REPO_ROOT, "data", "hub_deepseek.json")

FORBIDDEN_WORDS = (
    "杭州", "西湖", "钱塘江", "灵隐寺", "龙井", "宋城", "桂花",
    "三墩", "滨江", "江南", "石桥", "拱桥", "乌篷船",
)

SYSTEM_PROMPT = """你是《布鲁斯日常 · 幸福指数俱乐部》的首席角色与文案策划。
主角布鲁斯（Bruce）：奶油长毛腊肠犬，系酒红色斜纹真丝领巾，性格傲娇、细腻又嘴硬心软。
搭档主人：Alex（男主人）与 Meya（女主人），住在充满阳光与黑胶音乐的顶层公寓。
硬红线：绝对禁止出现任何真实城市名或地域词（尤其严禁：杭州、西湖、钱塘江、灵隐寺、龙井、宋城、桂花、三墩、滨江、江南、石桥、拱桥、乌篷船）。

请严格返回合法 JSON，包含以下顶层字段：
1. "onboarding_pack": {
     "alex_greetings": [6条布鲁斯隔着门缝对选Alex的新玩家撒娇/欢迎台词，每条16-30字],
     "meya_greetings": [6条布鲁斯隔着门缝对选Meya的新玩家撒娇/欢迎台词，每条16-30字],
     "alex_names": [14个俏皮时髦且至少含1个汉字的中文昵称，2-8字，无空格],
     "meya_names": [14个俏皮时髦且至少含1个汉字的中文昵称，2-8字，无空格],
     "welcome_back": [4条欢迎老邻居回家的温暖打趣短句，16-28字]
   }
2. "action_dialogues": {
     "walk_call": [5条唤狗小短腿走过来的台词，14-26字],
     "walk_sulk": [3条冷战期慢吞吞挪步的别扭台词，14-26字],
     "roll_over": [5条侧躺翻肚皮扭腰蹭地毯求摸肚子的台词，14-28字],
     "lick_paw": [5条低头认真舔右前爪的臭美台词，14-28字],
     "play_bow": [5条前胸贴地撅屁股伸懒腰邀玩的台词，14-28字],
     "airplane_ears": [4条双耳后压委屈飞机耳的台词，14-26字]
   }
3. "offline_chat_replies": [
     12条预设对话触发器，格式为 {"keywords": ["关键词1","关键词2"], "reply": "布鲁斯第一人称回应(14-34字)", "cue": "BRUCE · 状态标签", "action": "roll_over|lick_paw|play_bow|airplane_ears|walk|idle"}
     覆盖夸奖(帅/可爱/乖)、肚皮/摸摸、吃饭/肉干/冻干/三文鱼、出去玩/散步、加班/手机/微信、生气/道歉哄狗等场景。
   ]
"""


def load_key():
    env_map = {}
    for p in (FALLBACK_ENV_PATH, LOCAL_ENV_PATH):
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if s and not s.startswith("#") and "=" in s:
                        k, v = s.split("=", 1)
                        env_map[k.strip()] = v.strip().strip('"').strip("'")
    return os.environ.get("DEEPSEEK_API_KEY") or env_map.get("DEEPSEEK_API_KEY", "")


def check_forbidden(obj):
    raw = json.dumps(obj, ensure_ascii=False)
    for w in FORBIDDEN_WORDS:
        if w in raw:
            raise ValueError(f"Forbidden word found in DeepSeek output: {w}")


def clean_names(arr):
    out = []
    for s in arr or []:
        t = re.sub(r"\s+", "", str(s or "").strip())
        if 2 <= len(t) <= 10 and re.search(r"[\u4e00-\u9fff]", t) and t not in out:
            out.append(t)
    return out


def main():
    with open(HUB_JSON_PATH, "r", encoding="utf-8") as f:
        hub_data = json.load(f)

    key = load_key()
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY missing")

    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps({
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "请立刻生成这套新鲜、时髦、绝对不老套的入场迎宾与互动词库 JSON。"},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.92,
        }).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    gen = json.loads(body["choices"][0]["message"]["content"])
    check_forbidden(gen)

    ob = gen.get("onboarding_pack", {})
    ob["alex_names"] = clean_names(ob.get("alex_names"))
    ob["meya_names"] = clean_names(ob.get("meya_names"))
    assert len(ob.get("alex_names", [])) >= 8 and len(ob.get("meya_names", [])) >= 8

    hub_data["onboarding_pack"] = ob

    ad = gen.get("action_dialogues", {})
    tb = hub_data.setdefault("thought_bubbles", {})
    for k in ("walk_call", "walk_sulk", "roll_over", "lick_paw", "play_bow", "airplane_ears"):
        if isinstance(ad.get(k), list) and ad[k]:
            tb[k] = ad[k]

    replies = gen.get("offline_chat_replies", [])
    valid_actions = {"roll_over", "lick_paw", "play_bow", "airplane_ears", "walk", "idle"}
    cleaned_replies = []
    for item in replies:
        if isinstance(item, dict) and item.get("reply") and item.get("keywords"):
            act = item.get("action", "idle")
            if act not in valid_actions:
                act = "idle"
            cleaned_replies.append({
                "keywords": [str(k) for k in item["keywords"] if str(k).strip()],
                "reply": str(item["reply"]).strip(),
                "cue": str(item.get("cue") or "BRUCE · 心有灵犀").strip(),
                "action": act,
            })
    hub_data["offline_chat_replies"] = cleaned_replies

    with open(HUB_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(hub_data, f, ensure_ascii=False, indent=2)
    print(
        f"Updated {HUB_JSON_PATH}: alex_names={len(ob['alex_names'])}, "
        f"meya_names={len(ob['meya_names'])}, offline_chat_replies={len(cleaned_replies)}"
    )


if __name__ == "__main__":
    main()
