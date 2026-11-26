#!/usr/bin/env python3
"""Offline content factory using user's DeepSeek API (build-time only; never bundled to frontend)."""

import json
import os
import re
import urllib.error
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_ENV_PATH = os.path.join(REPO_ROOT, ".env")
FALLBACK_ENV_PATH = "/Users/alex/.gemini/antigravity/scratch/ai-pulse-radar/.env"
OUT_PATH = os.path.join(REPO_ROOT, "data", "content.json")

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


def load_keys():
    env_map = {}
    for env_path in (FALLBACK_ENV_PATH, LOCAL_ENV_PATH):
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
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
                "max_tokens": 4096,
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
            with urllib.request.urlopen(req, timeout=110) as resp:
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


SHARED_RULES = """你是《布鲁斯日常 · 幸福指数俱乐部》的首席文案策划。
主角设定：
- 狗狗：布鲁斯（奶油长毛腊肠犬，脖系酒红斜纹真丝领巾，傲娇、精致又粘人）。
- 主人：20 岁出头的年轻时髦搭档 Alex（男主）与 Meya（女主）。
- 严格禁令：绝对禁止出现任何真实城市、景点或刻板地域词汇（严禁出现：杭州、西湖、钱塘江、灵隐寺、龙井、宋城、桂花、三墩、滨江、江南、石桥、拱桥、乌篷船）！
- 文风铁律：玩家引导、内心戏、结果点评全部用轻快、傲娇、有电影画面感的现代口语中文，每条不重样。
"""

SYSTEM_CALL_HOME = SHARED_RULES + """
请严格输出 JSON，包含以下 2 个顶层键：
1. "activities": 对象，键名必须严格为这 5 个室内/小院互动：
   home_hide_seek, home_brush, home_rain_vinyl, home_kitchen, home_nap
   每个键对应一个对象，包含：
   - "win_lines": 数组，严格 6 条不重复的中文成功加分台词（20-44字，描写具体互动与布鲁斯微表情动作）
   - "phone_fail_lines": 数组，严格 4 条因为低头刷手机冷落布鲁斯的中文扣分台词（20-44字）
   - "hazard_fail_lines": 数组，严格 4 条踩中专属雷点（吹风机、乱点顺序、洋葱葡萄巧克力、低音炮、打扰午睡等）的中文扣分台词（20-44字）
2. "phone_notifications": 数组，严格 24 条纯英文手机弹窗文案（格式如 {"app": "CHAT", "text": "NEW MESSAGE · 99+"}），app 2-5字母全大写，text 2-6个英文词，绝不能包含中文。
"""

SYSTEM_CALL_STREET = SHARED_RULES + """
请严格输出 JSON，只包含 1 个顶层键 "activities"：
- 键名必须严格为这 5 个街区与户外互动：
  street_cafe, street_walk, street_lawn, street_window, street_bridge
- 每个键对应一个对象，包含：
  - "win_lines": 数组，严格 6 条不重复的中文成功加分台词（20-44字，描写精品咖啡馆、林荫道、草坪、橱窗、水岸夜晚灯光互动）
  - "phone_fail_lines": 数组，严格 4 条因为低头刷手机冷落布鲁斯的中文扣分台词（20-44字）
  - "hazard_fail_lines": 数组，严格 4 条踩中专属雷点（NO DOGS 门牌、凶犬低吼、电瓶车铃、高分贝喇叭、地面积水等）的中文扣分台词（20-44字）
"""

SYSTEM_CALL_SOCIAL = SHARED_RULES + """
请严格输出 JSON，包含以下 4 个顶层键：
1. "ticker_templates": 对象，包含 5 个数组字段（每条用 {player}、{target}、{score}、{old_score}、{new_score} 占位符，适合顶部实时吃瓜滚动，18-40字，有年轻人网感）：
   - "swap": 10条（触发高位互换幸福指数）
   - "collapse": 7条（踩雷跌破80进入冷战）
   - "wagyu_fail": 5条（花68分买和牛礼盒却命中4%失败被布鲁斯嫌弃）
   - "rescue_video": 5条（穷到买不起5分饼干看小视频拉回80分）
   - "streak": 5条（高分连胜或榜首风采）
2. "remote_previews": 数组，严格 6 个对象，id 必须依次为 park, warehouse, yacht, nordic, california, nz_swiss：
   每个对象包含 "id", "title", "subtitle", "teaser" (45-70字中文), "planned_perks" (数组，2条简短中文看点)。
3. "treat_monologues": 对象，包含：
   - "fail_lines": 8条买食物哄狗失败时布鲁斯的傲娇中文反应
   - "wagyu_fail_line": 1条买最贵和牛礼盒却失败的灵魂暴击台词
   - "success_lines": 8条被美食拉回80分以上时布鲁斯真香翻肚皮台词
4. "seed_players": 数组，严格 8 个年轻大学生/朋友群风格的中文昵称示例（2-8字，至少含1个汉字，禁止任何地名），每项含 "nickname", "owner" ("Alex"或"Meya"), "happiness" (整数74~138，至少1个<80、其余在86~138)。
"""


def assert_clean_and_valid(merged: dict):
    acts = merged["activities"]
    expected_acts = (
        "home_hide_seek", "home_brush", "home_rain_vinyl", "home_kitchen", "home_nap",
        "street_cafe", "street_walk", "street_lawn", "street_window", "street_bridge",
    )
    for k in expected_acts:
        item = acts.get(k) or {}
        if len(item.get("win_lines", [])) < 6 or len(item.get("phone_fail_lines", [])) < 4 or len(item.get("hazard_fail_lines", [])) < 4:
            raise ValueError(f"Insufficient lines for activity {k}")
    if len(merged.get("phone_notifications", [])) < 24:
        raise ValueError("Need >= 24 phone_notifications")
    for note in merged["phone_notifications"]:
        if re.search(r"[\u4e00-\u9fff]", json.dumps(note, ensure_ascii=False)):
            raise ValueError(f"Chinese char in phone_notification: {note}")
    tt = merged.get("ticker_templates", {})
    for k, min_n in (("swap", 10), ("collapse", 7), ("wagyu_fail", 5), ("rescue_video", 5), ("streak", 5)):
        if len(tt.get(k, [])) < min_n:
            raise ValueError(f"Insufficient ticker_templates.{k}")
    tm = merged.get("treat_monologues", {})
    if len(tm.get("fail_lines", [])) < 8 or len(tm.get("success_lines", [])) < 8 or not tm.get("wagyu_fail_line"):
        raise ValueError("Insufficient treat_monologues")

    serialized = json.dumps(merged, ensure_ascii=False)
    hits = [w for w in FORBIDDEN_WORDS if re.search(re.escape(w), serialized)]
    if hits:
        raise ValueError(f"Forbidden regional terms found: {hits}")


def main():
    keys = load_keys()
    if not keys:
        raise RuntimeError("No DeepSeek API key found")

    part_home = call_deepseek(keys, SYSTEM_CALL_HOME, "请为 5 个室内/客厅活动分别生成 6+4+4 条台词，以及 24 条纯英文手机弹窗通知。", temperature=0.88)
    part_street = call_deepseek(keys, SYSTEM_CALL_STREET, "请为 5 个林荫街区活动分别生成 6+4+4 条台词。", temperature=0.88)
    part_social = call_deepseek(keys, SYSTEM_CALL_SOCIAL, "请生成 32 条全服吃瓜模板、6 个远方场景预告、17 条食物哄狗台词和 8 位年轻玩家昵称。", temperature=0.9)

    treats = [
        {"id": "biscuit", "en": "BISCUIT", "cn": "磨牙饼干", "cost": 5, "prob": 0.22, "target": 80, "tag": "底线救命"},
        {"id": "yolk", "en": "YOLK", "cn": "蛋黄冻干", "cost": 10, "prob": 0.36, "target": 81, "tag": "轻量试水"},
        {"id": "jerky", "en": "JERKY", "cn": "鸡肉干", "cost": 16, "prob": 0.50, "target": 82, "tag": "五五博弈"},
        {"id": "pup_cup", "en": "PUP CUP", "cn": "爪爪奶泡", "cost": 23, "prob": 0.64, "target": 84, "tag": "咖啡馆特调"},
        {"id": "salmon", "en": "SALMON", "cn": "三文鱼块", "cost": 32, "prob": 0.76, "target": 86, "tag": "留足安全垫"},
        {"id": "duck_leg", "en": "DUCK LEG", "cn": "烤鸭腿", "cost": 42, "prob": 0.85, "target": 88, "tag": "肉食大招"},
        {"id": "steak", "en": "STEAK", "cn": "小牛排", "cost": 54, "prob": 0.92, "target": 91, "tag": "体面回血"},
        {"id": "wagyu", "en": "WAGYU", "cn": "和牛礼盒", "cost": 68, "prob": 0.96, "target": 94, "tag": "顶配豪赌"},
    ]

    activities = {}
    activities.update(part_home["activities"])
    activities.update(part_street["activities"])

    merged = {
        "meta": {
            "version": 3,
            "dog_name": "布鲁斯",
            "dog_breed": "奶油长毛腊肠犬",
            "happy_threshold": 80,
            "initial_happiness": 100,
            "min_treat_cost": 5,
        },
        "treats": treats,
        "activities": activities,
        "phone_notifications": part_home["phone_notifications"],
        "ticker_templates": part_social["ticker_templates"],
        "remote_previews": part_social["remote_previews"],
        "treat_monologues": part_social["treat_monologues"],
        "seed_players": part_social["seed_players"],
    }

    assert_clean_and_valid(merged)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"Wrote expanded DeepSeek-generated content to {OUT_PATH}")


if __name__ == "__main__":
    main()
