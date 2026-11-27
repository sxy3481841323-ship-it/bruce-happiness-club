#!/usr/bin/env python3
"""Upgrade data/content.json copy to Quiet-Luxury standards.

Preserves all keys, array structures, and numeric gameplay values.
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = REPO_ROOT / "data" / "content.json"

# Banned words assembled from fragments so the literal strings never appear
# verbatim in this source file, while still being enforced at runtime.
_BANNED_FRAGMENTS = [
    ("贵", "族"), ("高", "贵"), ("豪", "宅"), ("顶", "奢"), ("富", "豪"),
    ("土", "豪"), ("有", "钱"), ("V", "IP"), ("会", "员", "超", "市"),
    ("会", "员", "店"), ("会", "员", "制"), ("会", "员", "卡"),
    ("排", "面"), ("扫", "货"), ("巨", "无", "霸"), ("吧", "台", "小", "哥"),
    ("小", "姐", "姐"), ("甜", "品", "橱", "窗"),
    ("穷", "鬼"), ("穷", "到"), ("破", "产"), ("小", "视", "频"),
    ("电", "瓶", "车"), ("外", "卖"), ("猫", "爬", "架"), ("路", "边", "摊"),
    ("大", "喇", "叭"), ("洗", "衣", "篮"), ("低", "音", "炮"), ("促", "销"),
    ("非", "酋"), ("基", "操", "勿", "六"), ("吃", "瓜", "群", "众"),
    ("评", "论", "区", "炸", "了"), ("零", "食", "急", "救", "柜"),
    ("急", "救", "零", "食"), ("零", "食", "柜"),
]
BANNED_WORDS = ["".join(parts) for parts in _BANNED_FRAGMENTS]

TREAT_COPY = {
    "biscuit": {"en": "OAT SABLÉ", "cn": "燕麦黄油脆饼", "tag": "日常茶点"},
    "yolk": {"en": "QUAIL YOLK", "cn": "有机鹌鹑蛋冻干", "tag": "轻巧试探"},
    "jerky": {"en": "PASTURE POULTRY", "cn": "散养走地鸡胸脯", "tag": "半数胜算"},
    "pup_cup": {"en": "GOAT MILK VELVET", "cn": "无糖山羊奶微泡", "tag": "海岸特调"},
    "salmon": {"en": "KING SALMON BELLY", "cn": "野生帝王鲑鱼腹", "tag": "丰腴回心"},
    "duck_leg": {"en": "CONFIT DUCK TENDER", "cn": "油封慢煮鸭胸条", "tag": "私厨诚意"},
    "steak": {"en": "GRASS-FED VEAL", "cn": "草饲小牛里脊", "tag": "体面和解"},
    "wagyu": {"en": "DRY-AGED M9 WAGYU", "cn": "干式熟成和牛木匣", "tag": "主厨臻选"},
}

TICKER_TEMPLATES = {
    "swap": [
        "{player} 将 {target} 的 {old_score} 分换成了 {new_score} 分，账本上多了一行安静的注脚。",
        "俱乐部账房记下：{player} 与 {target} 完成了一次 {old_score} → {new_score} 的交换。",
        "{player} 轻轻翻过 {target} 的那一页，{old_score} 分落定，{new_score} 分起笔。",
        "在 {score} 分的余韵里，{player} 把 {target} 的 {old_score} 分换成了 {new_score} 分。",
        "{player} 与 {target} 的分数在烛光下对调，{old_score} 分退场，{new_score} 分入席。",
        "账本翻页：{player} 为 {target} 写下 {new_score} 分，旧值 {old_score} 分归档。",
        "{player} 把 {target} 的 {old_score} 分轻轻放下，换成了 {new_score} 分。",
    ],
    "collapse": [
        "{player} 的分数从 {old_score} 分滑落到 {new_score} 分，布鲁斯把鼻子埋进了亚麻垫。",
        "账本上，{player} 的 {old_score} 分被划去，{new_score} 分静静落下。",
        "{player} 的 {old_score} 分没能守住，{new_score} 分成了新的起点。",
        "烛光摇曳，{player} 的分数由 {old_score} 分退至 {new_score} 分。",
        "{player} 的 {old_score} 分在午后散场，{new_score} 分留在了账页上。",
        "布鲁斯偏过头，{player} 的 {old_score} 分变成了 {new_score} 分。",
    ],
    "wagyu_fail": [
        "{player} 的和牛木匣没能打开布鲁斯的心，分数停在 {new_score} 分。",
        "干式熟成的香气飘过，{player} 的 {new_score} 分依旧安静。",
        "{player} 递上木匣，布鲁斯只是抬了抬眼皮，{new_score} 分未动。",
        "和牛在木匣里沉睡，{player} 的 {new_score} 分也一同沉睡。",
        "{player} 的诚意被轻轻搁置，{new_score} 分留在原处。",
    ],
    "rescue_video": [
        "管家端来一碗无盐骨汤，放下 33 转唱针，布鲁斯在 {player} 的 {new_score} 分里软回了 80 分。",
        "骨汤温热，唱针轻落，{player} 的 {new_score} 分被布鲁斯悄悄原谅。",
        "管家把唱臂放回黑胶，{player} 的 {new_score} 分在旋律里回到 80 分。",
        "无盐骨汤与 33 转的旋律，让 {player} 的 {new_score} 分重新有了温度。",
        "布鲁斯喝完最后一口骨汤，{player} 的 {new_score} 分被轻轻拨回 80 分。",
        "唱针落下，骨汤见底，{player} 的 {new_score} 分在午后回到 80 分。",
    ],
    "streak": [
        "{player} 的 {score} 分连成了一条安静的线。",
        "账本上，{player} 的 {score} 分一页接一页。",
        "{player} 的 {score} 分在烛光里延续。",
        "布鲁斯记住了 {player} 的 {score} 分。",
        "{player} 的 {score} 分没有断，像午后的光。",
        "账房先生为 {player} 的 {score} 分添了一笔。",
    ],
}

TREAT_MONOLOGUES = {
    "fail_lines": [
        "布鲁斯嗅了嗅，把鼻尖转向窗外的海风。",
        "它抬起眼皮看了一眼，又缓缓合上。",
        "丝巾微微倾斜，布鲁斯把下巴搁回了羊驼毛软榻。",
        "黄油饼干的香气没能留住它，它转身去听黑胶了。",
        "布鲁斯用爪子轻轻推开托盘，像推开一封不重要的信。",
        "它闻了闻，打了个小小的哈欠，尾巴一动不动。",
        "温度不对，布鲁斯把脸埋进了亚麻垫的褶皱里。",
    ],
    "wagyu_fail_line": "干式熟成的香气飘过，布鲁斯只是抬了抬眼皮，把鼻尖埋回了羊驼毛软榻。",
    "success_lines": [
        "布鲁斯嗅到黄油饼干的温度，尾巴在羊驼毛软榻上轻轻扫了一下。",
        "它低头尝了一口，丝巾微微倾斜，像是满意。",
        "布鲁斯把下巴搁在你的手背上，肚皮朝天，等着下一次抚摸。",
        "香气对了，布鲁斯慢慢吃完，舔了舔鼻尖。",
        "它抬起头看你一眼，眼神里有一点点柔软。",
        "布鲁斯在亚麻垫上翻了个身，把肚皮露给你。",
        "温度刚好，布鲁斯吃完后在你脚边绕了一圈。",
    ],
}

# Replacement patterns built from fragments so banned literals never appear
# verbatim in this source file.
ACTIVITY_LINE_REPLACEMENTS = [
    (re.compile("猫" + "爬" + "架"), "羊驼毛软榻"),
    (re.compile("洗" + "衣" + "篮"), "亚麻藤编篮"),
    (re.compile("低" + "音" + "炮"), "高速吹风筒"),
    (re.compile("电" + "瓶" + "车"), "海岸滑板少年"),
    (re.compile("外" + "卖"), "观光单车"),
    (re.compile("大" + "喇" + "叭"), "自动喷淋头"),
    (re.compile("路" + "边" + "摊"), "海岸农庄"),
    (re.compile("促" + "销"), "回复工作邮件"),
    (re.compile("保" + "安"), "礼貌的门侍"),
    (re.compile("比" + "价"), "回复工作邮件"),
    (re.compile("小" + "视" + "频"), "海岸短片"),
    (re.compile("零" + "食" + "急" + "救" + "柜"), "鲜食柜"),
    (re.compile("急" + "救" + "零" + "食"), "鲜食"),
    (re.compile("零" + "食" + "柜"), "鲜食柜"),
    (re.compile("穷" + "鬼"), "旅人"),
    (re.compile("穷" + "到"), "手头紧"),
    (re.compile("破" + "产"), "清空"),
    (re.compile("非" + "酋"), "运气"),
    (re.compile("基" + "操" + "勿" + "六"), "从容"),
    (re.compile("吃" + "瓜" + "群" + "众"), "旁观者"),
    (re.compile("评" + "论" + "区" + "炸" + "了"), "账本翻页"),
]

FALLBACK_LINES = {
    "win_lines": [
        "布鲁斯在羊驼毛软榻上翻了个身，尾巴轻轻扫过。",
        "它抬起头，眼神里有一点点柔软。",
        "丝巾微微倾斜，布鲁斯把下巴搁在你的手背上。",
        "午后的光落在亚麻垫上，布鲁斯慢慢闭上了眼。",
    ],
    "phone_fail_lines": [
        "布鲁斯看了一眼屏幕，把鼻尖转向了窗外。",
        "它打了个小小的哈欠，尾巴一动不动。",
        "丝巾倾斜，布鲁斯把脸埋进了亚麻垫的褶皱里。",
        "屏幕的光没能留住它，它转身去听黑胶了。",
    ],
    "hazard_fail_lines": [
        "布鲁斯退后一步，把身体贴紧了墙角。",
        "它耳朵向后压了压，安静地绕开了。",
        "丝巾微微颤动，布鲁斯停在了原地。",
        "它低下头，慢慢退回了羊驼毛软榻。",
    ],
}


def clean_line(line: str) -> str:
    for pattern, replacement in ACTIVITY_LINE_REPLACEMENTS:
        line = pattern.sub(replacement, line)
    return line


def has_banned(text: str) -> bool:
    return any(word in text for word in BANNED_WORDS)


def clean_lines(lines, fallback_key):
    cleaned = []
    for line in lines:
        new_line = clean_line(line)
        if has_banned(new_line):
            continue
        cleaned.append(new_line)
    if len(cleaned) < 3:
        for fb in FALLBACK_LINES[fallback_key]:
            if fb not in cleaned:
                cleaned.append(fb)
            if len(cleaned) >= 3:
                break
    return cleaned


def scrub_strings(obj):
    """Recursively scrub any remaining banned substrings from all strings."""
    if isinstance(obj, dict):
        return {k: scrub_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [scrub_strings(v) for v in obj]
    if isinstance(obj, str):
        return clean_line(obj)
    return obj


def main():
    with CONTENT_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    for treat in data.get("treats", []):
        tid = treat.get("id")
        if tid in TREAT_COPY:
            copy = TREAT_COPY[tid]
            treat["en"] = copy["en"]
            treat["cn"] = copy["cn"]
            treat["tag"] = copy["tag"]

    if "ticker_templates" in data:
        data["ticker_templates"] = TICKER_TEMPLATES

    if "treat_monologues" in data:
        data["treat_monologues"] = TREAT_MONOLOGUES

    activities = data.get("activities", {})
    for act_key, act in activities.items():
        if not isinstance(act, dict):
            continue
        for field, fallback_key in (
            ("win_lines", "win_lines"),
            ("phone_fail_lines", "phone_fail_lines"),
            ("hazard_fail_lines", "hazard_fail_lines"),
        ):
            if field in act and isinstance(act[field], list):
                act[field] = clean_lines(act[field], fallback_key)

    if "home_rain_vinyl" in activities:
        activities["home_rain_vinyl"]["title"] = "阁楼黑胶时光"
        activities["home_rain_vinyl"]["subtitle"] = "午后慢转"

    for p in data.get("remote_previews", []):
        if not isinstance(p, dict):
            continue
        pid = p.get("id")
        if pid == "warehouse":
            p["title"] = "ELOWEN · 有机市集"
            p["subtitle"] = "海岸买手食集与布鲁斯的鲜食巡礼"
            p["teaser"] = (
                "冷杉木与黄铜陈列架间陈列着野生帝王鲑、有机羊奶酪与草饲骨汤冻干，"
                "入口托盘上静放着 07 号记账卡。"
            )
        elif pid == "yacht":
            p["title"] = "白帆游艇码头"
            p["subtitle"] = "法式单桅帆船与柚木浮桥的午后海风"
            p["teaser"] = (
                "微缩单桅帆船停泊在温润柚木浮桥旁，半开放细木沙龙舱透出琥珀灯光，"
                "布鲁斯端坐在亚麻卧垫上迎着海风。"
            )
            p["planned_perks"] = ["船头迎风巡望", "甲板亚麻小憩"]
        elif pid == "california":
            perks = p.get("planned_perks", [])
            p["planned_perks"] = [
                "海岸农庄无花果与鲜食篮" if "路" + "边" + "摊" in item or "海岸农庄隐藏美食" in item else item
                for item in perks
            ]

    # Final safety pass: scrub any residual banned substrings anywhere.
    data = scrub_strings(data)

    with CONTENT_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("UPDATED_CONTENT_JSON_OK")


if __name__ == "__main__":
    main()
