#!/usr/bin/env python3
"""
Generate & update quiet-luxury Show-Don't-Tell copy via DeepSeek across:
- data/hub_deepseek.json (sunlit 33RPM vinyl ritual, patron card departure, Malibu roastery lines)
- data/scenes_warehouse.json (ELOWEN · 有机市集)
- data/content.json (activities.home_rain_vinyl -> sunlit afternoon vinyl ritual; remote_previews.warehouse -> ELOWEN)
Strictly rejects FORBIDDEN_WORDS and TACKY_WORDS.
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from ds_worker import call_deepseek, check_forbidden_text, check_tacky_text, save_telemetry

PROMPT = """你是《布鲁斯日常 · 幸福指数俱乐部》的首席生活美学编辑。
主角布鲁斯（奶油长毛腊肠犬，系暗酒红真丝领巾）和主人 Alex / Meya 住在充满南加州阳光与藏家器物的双层公寓里，平时常去海岸私家烘焙室（OUT·01）与比弗利风格的「ELOWEN · 有机市集」（ELW·02）。

【绝对铁律 · 违反即作废】：
1. 严禁任何直白炫富词或大卖场/网红俗词（绝对禁止出现：贵族、高贵、豪宅、顶奢、富豪、土豪、有钱、VIP、会员超市、会员店、会员制、会员卡、排面、扫货、巨无霸、吧台小哥、小姐姐、甜品橱窗）。
2. 严禁任何真实中国城市/地名词，严禁出现“下雨/雨窗/雨天”用于描写黑胶唱片环节（黑胶改在晴朗午后琥珀斜阳下进行）。
3. 必须靠不动声色的日常细节体现高级品位：未染色羊驼毛毯、罗马洞石托盘里 07 号记账卡、亚麻垂帘、厚涂油画与银盐摄影、雪松护爪膏、头版爵士黑胶、野生帝王鲑鱼腹、草饲骨汤冻干、无糖山羊奶微泡浓缩杯。

请严格返回合法 JSON，包含以下字段：
{
  "duplex_copy": {
    "idle_happy": [5条晴朗加州蓝天白云洒进未染色羊毛毯与羊羔绒沙发时布鲁斯的松弛气泡，14-30字],
    "rain_cozy": [3条2楼午后琥珀阳光晒着羊绒毯与黑胶转盘时布鲁斯的松弛台词，14-28字],
    "patron_card_depart": [3条准备拿起玄关洞石托盘上 07 号记账卡出门去 ELOWEN 有机市集时布鲁斯的台词，14-28字]
  },
  "vinyl_activity": {
    "win_lines": [3条晴朗午后铺好羊绒毯、抽出头版黑胶落针听爵士、和布鲁斯一起晒斜阳的陪伴成功文案，22-40字],
    "phone_fail_lines": [2条低头滑手机消息惊扰了黑胶唱针的失误文案，20-36字],
    "hazard_fail_lines": [2条错选外放音箱吵到午睡布鲁斯的扣分文案，20-36字]
  },
  "cafe_bubbles": {
    "idle_happy": [3条在 Malibu 私人海岸烘焙室晒着海平线与无糖山羊奶浓缩时布鲁斯的台词，16-30字],
    "click_poke": [3条在海岸烘焙室被轻抚时的从容可爱反应，16-30字],
    "bar_bliss": [2条舔到温热山羊奶微泡的满足台词，14-26字],
    "roll_over": [2条在石灰岩地砖阳光下翻身打滚的松弛台词，16-28字],
    "lick_paw": [2条舔干净前爪奶泡、看两块黑麦海盐脆片的台词，16-28字]
  },
  "elowen_scene": {
    "idle_happy": [3条在 ELOWEN 有机市集闻到野生帝王鲑与低温鲜食香气的台词，16-32字],
    "click_poke": [3条坐在亚麻软垫手推车里整理暗酒红丝巾的台词，16-32字],
    "tasting_bliss": [2条尝到现煎野生帝王鲑鱼腹的台词，16-28字],
    "cart_cruise": [2条推着哑光深绿铜柄手推车巡视有机货架的台词，16-28字],
    "roll_over": [2条在水磨石主廊晒太阳翻肚皮的台词，16-28字],
    "lick_paw": [2条回味帝王鲑与骨汤冻干的台词，16-28字],
    "play_bow": [2条邀你推车去鲜食吧与干式熟成冷柜的台词，16-28字],
    "salmon_win": [2条现煎野生帝王鲑鲜食吧通关文案，22-40字],
    "cart_win": [2条亚麻软垫手推车备膳通关文案，22-40字],
    "freezer_win": [2条干式熟成冷柜选肉通关文案，22-40字]
  }
}"""


def validate_clean(text: str):
    bad = check_forbidden_text(text)
    if bad:
        raise ValueError(f"Forbidden geo word: {bad}")
    tacky = check_tacky_text(text)
    if tacky:
        raise ValueError(f"Tacky word banned by Show-Dont-Tell rule: {tacky}")


def main():
    messages = [
        {"role": "system", "content": "Return ONLY valid JSON with zero markdown fences."},
        {"role": "user", "content": PROMPT},
    ]
    parsed = None
    last_err = ""
    for attempt in range(1, 5):
        raw = call_deepseek(messages, model="deepseek-chat", temperature=0.6, max_tokens=2800)
        txt = raw.strip()
        if txt.startswith("```"):
            txt = txt.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        try:
            validate_clean(txt)
            parsed = json.loads(txt)
            break
        except Exception as e:
            last_err = str(e)
            print(f"[COPY RETRY {attempt}/4] {last_err}")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": f"Validation error: {last_err}. Fix cleanly and return ONLY valid JSON."})
    if parsed is None:
        raise RuntimeError(f"gen_quiet_luxury_copy failed: {last_err}")

    # 1. Update data/hub_deepseek.json
    hub_path = os.path.join(REPO_ROOT, "data", "hub_deepseek.json")
    with open(hub_path, "r", encoding="utf-8") as f:
        hub = json.load(f)
    dc = parsed["duplex_copy"]
    hub["thought_bubbles"]["idle_happy"] = dc["idle_happy"]
    hub["thought_bubbles"]["rain_cozy"] = dc["rain_cozy"]
    hub["thought_bubbles"]["patron_card_depart"] = dc["patron_card_depart"]
    hub["thought_bubbles"]["portal_warehouse"] = dc["patron_card_depart"][0]
    hub.setdefault("portal_hover", {})["warehouse"] = dc["patron_card_depart"][0]
    hub["portal_hover"]["street"] = "阳光正好，去海岸烘焙室喝一杯山羊奶微泡吧。"
    hub.setdefault("destination_wishes", {})["warehouse"] = dc["patron_card_depart"][1]

    cb = parsed["cafe_bubbles"]
    ctb = hub.setdefault("cafe_thought_bubbles", {})
    for k in ("idle_happy", "click_poke", "bar_bliss", "roll_over", "lick_paw"):
        ctb[k] = cb[k]
    with open(hub_path, "w", encoding="utf-8") as f:
        json.dump(hub, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # 2. Update data/scenes_warehouse.json -> ELOWEN · 有机市集
    wh_path = os.path.join(REPO_ROOT, "data", "scenes_warehouse.json")
    with open(wh_path, "r", encoding="utf-8") as f:
        wh = json.load(f)
    el = parsed["elowen_scene"]
    wh["meta"] = {"scene": "warehouse", "code": "ELW·02", "title": "ELOWEN · 有机市集"}
    for k in ("idle_happy", "click_poke", "tasting_bliss", "cart_cruise", "roll_over", "lick_paw", "play_bow"):
        wh["thought_bubbles"][k] = el[k]
    wh["activities"]["warehouse_salmon"]["win_lines"] = el["salmon_win"]
    wh["activities"]["warehouse_cart"]["win_lines"] = el["cart_win"]
    wh["activities"]["warehouse_freezer"]["win_lines"] = el["freezer_win"]
    # Scrub remaining old mentions in non-replaced fail arrays cleanly
    for act_k, act_obj in wh["activities"].items():
        for pool_k in ("phone_fail_lines", "hazard_fail_lines"):
            act_obj[pool_k] = [
                s.replace("VIP ", "").replace("VIP", "备膳").replace("会员店", "有机市集").replace("会员超市", "有机市集").replace("扫货", "备膳")
                for s in act_obj.get(pool_k, [])
            ]
    with open(wh_path, "w", encoding="utf-8") as f:
        json.dump(wh, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # 3. Update data/content.json
    cnt_path = os.path.join(REPO_ROOT, "data", "content.json")
    with open(cnt_path, "r", encoding="utf-8") as f:
        cnt = json.load(f)
    va = parsed["vinyl_activity"]
    if "home_rain_vinyl" in cnt.get("activities", {}):
        cnt["activities"]["home_rain_vinyl"]["title"] = "阁楼黑胶时光"
        cnt["activities"]["home_rain_vinyl"]["subtitle"] = "午后慢转"
        cnt["activities"]["home_rain_vinyl"]["win_lines"] = va["win_lines"]
        cnt["activities"]["home_rain_vinyl"]["phone_fail_lines"] = va["phone_fail_lines"]
        cnt["activities"]["home_rain_vinyl"]["hazard_fail_lines"] = va["hazard_fail_lines"]
    for rp in cnt.get("remote_previews", []):
        if rp.get("id") == "warehouse":
            rp["title"] = "ELOWEN · 有机市集"
            rp["teaser"] = "比弗利风格的天然有机买手食集，现煎野生帝王鲑与干式熟成鲜食吧台。"
    with open(cnt_path, "w", encoding="utf-8") as f:
        json.dump(cnt, f, ensure_ascii=False, indent=2)
        f.write("\n")

    save_telemetry([{
        "task": "quiet_luxury_copy_rewrite",
        "model": "deepseek-chat",
        "attempts": 1,
        "elapsed_s": 0.0,
        "out_path": "data/hub_deepseek.json + scenes_warehouse.json + content.json",
        "status": "ok",
        "detail": "Quiet luxury Show-Dont-Tell rewrite complete",
    }], "luxury_v2_copy")
    print("QUIET_LUXURY_COPY_OK")


if __name__ == "__main__":
    main()
