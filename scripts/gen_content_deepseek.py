#!/usr/bin/env python3
"""Offline content factory using user's DeepSeek API (build-time only; never bundled to frontend)."""

import json
import os
import urllib.error
import urllib.request

ENV_PATH = "/Users/alex/.gemini/antigravity/scratch/ai-pulse-radar/.env"
OUT_PATH = "/Users/alex/.gemini/antigravity/scratch/bruce-happiness-club/data/content.json"


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


def call_deepseek(keys, system_prompt: str, user_prompt: str, temperature: float = 0.85) -> dict:
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
        except Exception as exc:
            last_err = f"key #{idx}: {type(exc).__name__}"
            if isinstance(exc, urllib.error.HTTPError):
                last_err += f" HTTP {exc.code}"
    raise RuntimeError(last_err or "DeepSeek API failed")


SYSTEM_CALL_1 = """你是《布鲁斯》养狗网页游戏的首席文案策划。
主角设定：
- 狗狗：布鲁斯（奶油长毛腊肠犬，酒红斜纹真丝领巾，傲娇又粘人）。
- 主人：20岁出头的年轻时髦情侣/搭档 Alex（男主）与 Meya（女主）。
- 居住环境：现代极简结合一点东方留白比例的独栋别墅小院（有落地玻璃窗、庭院水景与独立草坪），以及门外绿树成荫的精品街区与滨水绿道。
- 严格禁令：绝对禁止出现任何真实城市、景点或刻板地域词汇（严禁出现“杭州”“西湖”“钱塘江”“灵隐寺”“龙井”“宋城”“桂花”“三墩”“滨江”“江南”“石桥”“拱桥”“乌篷船”等字眼）！
- 语言铁律：
  - 玩家引导、内心戏、结果点评全部用轻快、年轻、有电影画面感的中文；
  - 手机推送通知（phone_notifications）必须全部用简短真实的英文（2~5个词，如 "NEW MESSAGE · 99+"、"WORK CALL"）。

必须严格输出 JSON，包含两个顶层键：
1. "activities": 对象，键名必须严格为这 10 个：
   home_hide_seek, home_brush, home_rain_vinyl, home_kitchen, home_nap,
   street_cafe, street_walk, street_lawn, street_window, street_bridge
   每个键对应一个对象，包含：
   - "win_lines": 数组，3条不重复的中文成功加分台词（20-42字，描写别墅客厅/露台/街区的具体互动细节）
   - "phone_fail_lines": 数组，2条因为低头玩手机冷落布鲁斯的中文扣分台词（20-42字）
   - "hazard_fail_lines": 数组，2条踩中该活动专属雷点（吹风机、乱按黑胶、误食洋葱葡萄巧克力、门牌禁入、恶犬、电瓶车或高分贝噪音等）的中文扣分台词（20-42字）
2. "phone_notifications": 数组，16条纯英文手机弹窗文案（格式如 {"app": "CHAT", "text": "NEW MESSAGE · 99+"}），绝不能有中文。
"""

SYSTEM_CALL_2 = """你是《布鲁斯》养狗游戏的年轻化社交文案策划。
主角：奶油长毛腊肠犬布鲁斯，20岁出头的主人 Alex / Meya，住现代独栋别墅。
严格禁令：绝对禁止出现“杭州”“西湖”“钱塘江”“灵隐寺”“龙井”“宋城”“桂花”“三墩”“滨江”“江南”等任何地域地名词汇！

必须严格输出 JSON，包含以下 4 个顶层键：
1. "ticker_templates": 对象，包含 5 个数组字段（每条用 {player}、{target}、{score}、{old_score}、{new_score} 占位符，适合顶部实时吃瓜滚动，18-38字，有年轻人网感）：
   - "swap": 6条（触发含义A互换幸福指数）
   - "collapse": 4条（踩雷跌破80进入冷战）
   - "wagyu_fail": 3条（花68分买和牛礼盒却命中4%失败被布鲁斯嫌弃）
   - "rescue_video": 3条（穷到买不起5分饼干看小视频拉回80分）
   - "streak": 4条（高分连胜或登顶风采）
2. "remote_previews": 数组，严格 6 个对象，id 必须依次为 park, warehouse, yacht, nordic, california, nz_swiss：
   每个对象包含：
   - "id": 上述 id
   - "title": 中文标题（如 "城市大公园"、"会员制仓储超市"、"私人游艇派对"、"北欧峡湾之旅"、"阳光海岸自驾"、"雪山与牧场专线"）
   - "subtitle": 英文副标题
   - "teaser": 45-70字年轻轻松的中文二期预告
   - "planned_perks": 数组，2条简短中文看点
3. "treat_monologues": 对象，包含：
   - "fail_lines": 5条买食物哄狗失败时布鲁斯的傲娇中文反应
   - "wagyu_fail_line": 1条买最贵和牛礼盒却失败的灵魂暴击台词
   - "success_lines": 4条被美食拉回 80 分以上时布鲁斯真香翻肚皮台词
4. "seed_players": 数组，8个年轻大学生/朋友群风格的中文昵称示例（至少含1个汉字，2-8字，禁止任何真实地名），每人包含：
   - "nickname": 如 "早八起不来星人"、"冰美式续命侠"、"沙发土豆本豆" 等
   - "owner": "Alex" 或 "Meya"
   - "happiness": 整数，分布在 74 到 138 之间（至少1个低于80、其余分布在86~138之间）
"""


def main():
    keys = load_keys()
    if not keys:
        raise RuntimeError("No DeepSeek API key found")

    part1 = call_deepseek(keys, SYSTEM_CALL_1, "请生成 10 个活动的年轻化独栋别墅与街区台词库及 16 条纯英文手机弹窗通知。", temperature=0.85)
    part2 = call_deepseek(keys, SYSTEM_CALL_2, "请生成全服吃瓜公告模板、6个远方场景预告、食物哄狗台词和8位年轻玩家昵称。", temperature=0.9)

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

    merged = {
        "meta": {
            "version": 2,
            "dog_name": "布鲁斯",
            "dog_breed": "奶油长毛腊肠犬",
            "happy_threshold": 80,
            "initial_happiness": 100,
            "min_treat_cost": 5,
        },
        "treats": treats,
        "activities": part1["activities"],
        "phone_notifications": part1["phone_notifications"],
        "ticker_templates": part2["ticker_templates"],
        "remote_previews": part2["remote_previews"],
        "treat_monologues": part2["treat_monologues"],
        "seed_players": part2["seed_players"],
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"Wrote fresh DeepSeek-generated content to {OUT_PATH}")


if __name__ == "__main__":
    main()
