#!/usr/bin/env python3
"""
Enrich data/hub_deepseek.json via DeepSeek with Two-Floor Penthouse Duplex dialogue:
- floor_1f_greet / floor_2f_greet
- tv_art_swap / lamp_toggle
- bright blue-sky idle_happy lines
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
HUB_JSON_PATH = os.path.join(REPO_ROOT, "data", "hub_deepseek.json")

sys.path.insert(0, SCRIPT_DIR)
from ds_worker import call_deepseek, check_forbidden_text, save_telemetry

PROMPT = """你是《布鲁斯日常 · 幸福指数俱乐部》的角色策划。
主角布鲁斯（奶油长毛腊肠犬，酒红色丝巾，傲娇嘴硬心软）刚刚搬进了全新升级的【PH·01 蓝天白云双层挑空阳光复式豪宅】：
- 1F 挑空阳光主客厅：全景落地窗外是蔚蓝天空、蓬松白云和橄榄树阳光露台；屋里有米白羊羔绒弧形沙发、洞石茶几、超薄画框艺术电视（点一下切换海岸帆船/包豪斯几何/地中海橄榄枝三幅画作）和香槟金弧形钓鱼落地灯（可点击开关暖光）。
- 2F 阳光私享阁楼：顺着暖光悬浮楼梯上去，玻璃护栏俯瞰一楼，有胡桃木黑胶试听台、环球旅行画廊墙和布鲁斯的酒红丝绒贵族窝。

请严格返回合法 JSON 对象，禁止使用任何真实城市或地域词，包含 5 个数组字段（每条 14-30 字中文，灵动可爱有生活气）：
{
  "floor_1f_greet": [4条布鲁斯回到1楼挑空阳光大客厅、透过落地窗晒蓝天白云太阳的台词],
  "floor_2f_greet": [4条布鲁斯登上2楼玻璃阁楼、靠着黑胶机和旅行画廊俯瞰楼下的台词],
  "tv_art_swap": [4条你点击墙上画框艺术电视切换画作时布鲁斯的点评台词],
  "lamp_toggle": [4条点击香槟金钓鱼落地灯切换光影时布鲁斯的台词],
  "idle_happy": [5条晴朗蓝天白云洒进双层大客厅时布鲁斯的悠闲气泡台词]
}"""


def main():
    with open(HUB_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw = call_deepseek(
        [
            {"role": "system", "content": "Return ONLY valid JSON with the requested arrays, no markdown fences."},
            {"role": "user", "content": PROMPT},
        ],
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=1800,
    )
    txt = raw.strip()
    if txt.startswith("```"):
        txt = txt.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    bad = check_forbidden_text(txt)
    if bad:
        raise ValueError(f"Forbidden term in DeepSeek duplex copy: {bad}")
    parsed = json.loads(txt)

    tb = data.setdefault("thought_bubbles", {})
    for key in ("floor_1f_greet", "floor_2f_greet", "tv_art_swap", "lamp_toggle"):
        lines = [str(s).strip() for s in parsed.get(key, []) if str(s).strip()]
        if not lines:
            raise ValueError(f"Missing lines for {key}")
        tb[key] = lines
    happy_new = [str(s).strip() for s in parsed.get("idle_happy", []) if str(s).strip()]
    if len(happy_new) >= 3:
        tb["idle_happy"] = happy_new

    with open(HUB_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    save_telemetry([{
        "task": "duplex_copy_enrichment",
        "model": "deepseek-chat",
        "attempts": 1,
        "elapsed_s": 0.0,
        "out_path": "data/hub_deepseek.json",
        "status": "ok",
        "detail": "Updated 5 duplex thought_bubbles keys",
    }], "penthouse_copy")
    print("DUPLEX_COPY_OK", {k: len(tb[k]) for k in ("floor_1f_greet", "floor_2f_greet", "tv_art_swap", "lamp_toggle", "idle_happy")})


if __name__ == "__main__":
    main()
