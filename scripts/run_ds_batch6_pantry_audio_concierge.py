#!/usr/bin/env python3
"""
Parallel DeepSeek Batch 6 runner:
1. js/audioSoundscape.js (deepseek-reasoner: Web Audio procedural DSP soundscapes)
2. js/pantryIcons.js (deepseek-chat: 10 copperplate/apothecary quiet-luxury SVG icons)
3. scripts/update_quiet_luxury_content.py (deepseek-chat: quiet-luxury wash on data/content.json)
4. data/concierge_dialogue_v4.json (deepseek-chat: butler, chauffeur & Hi-Fi dialogue lines)
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ds_worker import REPO_ROOT, run_parallel_codegen  # noqa: E402


VERIFY_SOUNDSCAPE = r"""node --check js/audioSoundscape.js && node --input-type=module -e '
import fs from "fs";
import { createSoundscapeController } from "./js/audioSoundscape.js";
const src = fs.readFileSync("./js/audioSoundscape.js", "utf8");
if (src.includes("exponentialRampToValueAtTime(0,") || src.includes("exponentialRampToValueAtTime(0 ,")) {
  throw new Error("Unsafe exponentialRampToValueAtTime to 0 detected");
}
if (/https?:\/\//i.test(src)) {
  throw new Error("External URL detected in audioSoundscape.js");
}
function makeParam() {
  return {
    value: 0,
    setValueAtTime() {},
    linearRampToValueAtTime() {},
    exponentialRampToValueAtTime(v) { if (v <= 0) throw new Error("exp ramp <= 0: " + v); },
    setTargetAtTime() {},
    cancelScheduledValues() {},
  };
}
function makeNode() {
  return {
    gain: makeParam(),
    frequency: makeParam(),
    Q: makeParam(),
    detune: makeParam(),
    type: "sine",
    loop: false,
    buffer: null,
    connect() { return this; },
    disconnect() {},
    start() {},
    stop() {},
    addEventListener() {},
  };
}
const mockCtx = {
  currentTime: 1.0,
  sampleRate: 44100,
  state: "running",
  destination: {},
  createGain: makeNode,
  createBiquadFilter: makeNode,
  createOscillator: makeNode,
  createBufferSource: makeNode,
  createBuffer(ch, len) { return { getChannelData: () => new Float32Array(len) }; },
};
let muted = false;
const sc = createSoundscapeController(() => mockCtx, () => muted);
sc.setSceneAmbience("penthouse", { floor: "1f", sulking: false });
sc.setFloor("2f");
const h1 = sc.toggleHifi();
if (h1 !== true || !sc.isHifiOn()) throw new Error("toggleHifi failed");
sc.setVinylMode(true);
sc.setVinylMode(false);
sc.stokeFireplace();
sc.playConciergeBell();
sc.playGlassPour();
sc.playVinylDrop();
sc.playChauffeurReady();
sc.setSceneAmbience("cafe", { sulking: false });
sc.setSceneAmbience("warehouse", { sulking: true });
muted = true;
sc.syncMute(true);
muted = false;
sc.syncMute(false);
sc.clearSceneAmbience("cafe");
sc.clearSceneAmbience("warehouse");
sc.stopAll();
console.log("SOUNDSCAPE_VERIFY_OK");
'"""

VERIFY_PANTRY_ICONS = r"""node --check js/pantryIcons.js && node --input-type=module -e '
import fs from "fs";
import { PANTRY_ICONS } from "./js/pantryIcons.js";
const req = ["biscuit","yolk","jerky","pup_cup","salmon","duck_leg","steak","wagyu","cloche","gramophone"];
for (const k of req) {
  const s = String(PANTRY_ICONS[k] || "").trim();
  if (!s.startsWith("<svg") || !s.endsWith("</svg>")) throw new Error("Invalid SVG for " + k);
  if (!s.includes("viewBox=\"0 0 64 64\"")) throw new Error("Missing viewBox 0 0 64 64 for " + k);
  const cleaned = s.replaceAll("http://www.w3.org/2000/svg", "");
  if (/https?:\/\//i.test(cleaned)) throw new Error("External link in SVG " + k);
}
const src = fs.readFileSync("./js/pantryIcons.js", "utf8");
if (src.includes("stroke-width=\"2.4\"")) throw new Error("Old thick cartoon stroke detected");
console.log("PANTRY_ICONS_VERIFY_OK");
'"""

VERIFY_CONTENT_SCRIPT = r"""python3 scripts/update_quiet_luxury_content.py && python3 -c '
import json, re
from pathlib import Path
import sys
sys.path.insert(0, "scripts")
from ds_worker import FORBIDDEN_WORDS, TACKY_WORDS

text = Path("data/content.json").read_text(encoding="utf-8")
d = json.loads(text)
expected = [
    ("biscuit", 5, 0.22, 80),
    ("yolk", 10, 0.36, 81),
    ("jerky", 16, 0.5, 82),
    ("pup_cup", 23, 0.64, 84),
    ("salmon", 32, 0.76, 86),
    ("duck_leg", 42, 0.85, 88),
    ("steak", 54, 0.92, 91),
    ("wagyu", 68, 0.96, 94),
]
got = [(t["id"], t["cost"], t["prob"], t["target"]) for t in d["treats"]]
assert got == expected, f"Treats math altered: {got}"
for w in FORBIDDEN_WORDS + TACKY_WORDS:
    assert w not in text, f"Forbidden word remains: {w}"
legacy_re = re.compile(r"穷鬼|穷到|破产|小视频|电瓶车|外卖|猫爬架|路边摊|大喇叭|洗衣篮|低音炮|促销|非酋|基操勿六|吃瓜群众|评论区炸了|零食急救柜|急救零食|零食柜")
m = legacy_re.search(text)
assert not m, f"Legacy tacky phrase remains: {m.group(0)}"
for act_name, bank in d["activities"].items():
    for k in ("win_lines", "phone_fail_lines", "hazard_fail_lines"):
        assert len(bank.get(k, [])) >= 2, f"Empty lines in {act_name}.{k}"
assert "{player}" in d["ticker_templates"]["rescue_video"][0], "Missing {player} placeholder in rescue_video"
assert len(d["seed_players"]) == 8
assert len(d["phone_notifications"]) == 24
print("CONTENT_JSON_WASH_OK")
'"""

VERIFY_CONCIERGE_JSON = r"""python3 -c '
import json, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from ds_worker import FORBIDDEN_WORDS, TACKY_WORDS
raw = Path("data/concierge_dialogue_v4.json").read_text(encoding="utf-8")
d = json.loads(raw)
req = {
    "butler_water_lines": 4,
    "butler_pantry_lines": 3,
    "chauffeur_cafe_lines": 3,
    "chauffeur_market_lines": 3,
    "chauffeur_marina_lines": 3,
    "hifi_on_lines": 3,
    "hifi_off_lines": 2,
}
for k, min_n in req.items():
    arr = d.get(k)
    assert isinstance(arr, list) and len(arr) >= min_n, f"Bad key {k}"
    for s in arr:
        assert isinstance(s, str) and 8 <= len(s) <= 44, f"Bad line length in {k}: {s!r}"
for w in FORBIDDEN_WORDS + TACKY_WORDS:
    assert w not in raw, f"Forbidden word in concierge json: {w}"
print("CONCIERGE_DIALOGUE_V4_OK")
'"""

TASKS = [
    {
        "name": "batch6_audio_soundscape",
        "model": "deepseek-chat",
        "out_path": "js/audioSoundscape.js",
        "max_tokens": 8192,
        "system": (
            "You are a senior Web Audio API DSP engineer writing clean, zero-dependency vanilla ES module JavaScript "
            "for a quiet-luxury 3D web game. Output ONLY valid ES module code with no markdown fences."
        ),
        "prompt": r"""Write `js/audioSoundscape.js` implementing zero-dependency procedural Web Audio soundscapes and subtle luxury tactile cues.

Required export:
```js
export function createSoundscapeController(ensureCtxFn, isMutedFn)
```
where `ensureCtxFn()` returns a `AudioContext` (or `null` when muted/unavailable before user gesture) and `isMutedFn()` returns a boolean.

Implement a clean, resilient soundscape engine inside `createSoundscapeController` returning an object with ALL of these exact methods:
1. `setSceneAmbience(sceneId, opts = {})`
   - `sceneId` is one of `"penthouse"`, `"cafe"`, `"warehouse"`, or `"none"`.
   - Store `desiredScene = sceneId` and `desiredOpts = { floor: opts.floor || "1f", sulking: Boolean(opts.sulking) }` even if `ensureCtxFn()` currently returns `null` or `ctx.state === "suspended"`, so calling `unlock()` / `syncMute(false)` later automatically brings up the ambience!
   - When `"penthouse"`:
     * Create/maintain a warm wood-burning fireplace ambience bed: pink/brown filtered noise through a lowpass filter (~115 Hz warmth floor rumble) + subtle highpass/bandpass ember crackle pops (`1300–3200 Hz`, micro bursts `10–26 ms` triggered via `setTimeout` jittered `220–920 ms`).
     * Attenuate hearth gain gently on `"2f"` (`~0.35` multiplier) vs `"1f"` (`1.0` multiplier), and slightly cooler (`0.6` multiplier) when `sulking` is true.
     * Preserve `hifiOn` state across floor changes/re-applications inside `"penthouse"`. If leaving `"penthouse"` to `"cafe"`/`"warehouse"`/`"none"`, pause the lounge jazz loop cleanly.
   - When `"cafe"`:
     * Gentle Malibu coastal surf & sea breeze: filtered pink noise swept slowly up and down via `setInterval` or scheduled `setTargetAtTime` (`180 Hz` <-> `740 Hz` every ~4.2s) creating calm breaking-wave swells + subtle warm coastal air shimmer.
   - When `"warehouse"`:
     * Subtle sunlit `ELOWEN` glass-atrium room tone: ultra-soft filtered airy noise + occasional gentle warm porcelain/glass harmonic overtone (`~660Hz` / `990Hz`, gain `0.008`, `1.4s` decay) every `4–7s`.
   - When `"none"` (or falsy): smoothly ramp ambient gain down to `0.0001` over ~`0.22s`, stop scene timers, and clean up scene bed.
2. `clearSceneAmbience(expectedSceneId)`:
   - Only fades out / stops if `desiredScene === expectedSceneId` (prevents an outgoing scene's `destroy()` from muting a newly mounted scene).
3. `setFloor(floorId)`:
   - Updates `desiredOpts.floor` (`"1f"` or `"2f"`) and smoothly scales hearth/Hi-Fi gains via `setTargetAtTime`.
4. `toggleHifi(forceBool)`:
   - Toggles (or sets if `typeof forceBool === "boolean"`) `hifiOn` and returns the new `boolean` state.
   - When `hifiOn` is `true` and `desiredScene === "penthouse"` and `!isMutedFn()`, starts a soft, unhurried Rhodes + upright-bass 4-chord ambient jazz loop (`Fmaj9 -> Em7 -> Dm9 -> Cmaj9` ~`64 BPM`, using soft sine + lowpass-filtered triangle voices at very gentle gain `<= 0.045`, scheduled every ~`3.75s` via `setTimeout`, fading smoothly out when turned off).
5. `isHifiOn()`: returns boolean `hifiOn`.
6. `setVinylMode(active)`: sets `vinylMode = Boolean(active)`; if `active` becomes `true`, ensures `hifiOn = true` with warm 33RPM vinyl surface crackle pulses added softly; when `active` becomes `false`, turns off extra stylus hiss while leaving `hifiOn` smoothly active if requested or untouched.
7. `stokeFireplace()`: immediately plays 3 staggered warm charred-oak crackle & gentle ember-whoosh micro-bursts.
8. `playConciergeBell()`: brushed-brass two-tone residence intercom chime (`880 Hz` -> `1318.5 Hz`, warm sine + soft overtone, ~`0.55s` decay, gain `<= 0.06`).
9. `playGlassPour()`: flint-glass crystal clink (`2349 Hz` + `2793 Hz` short sine chime) + `0.62s` sparkling mineral-water effervescent bandpass-noise pour.
10. `playVinylDrop()`: soft cushioned tonearm drop (`112 Hz -> 62 Hz` short sine thump) + brief groove warmth burst.
11. `playChauffeurReady()`: understated twin-note luxury sedan dispatch confirmation (`329.63 Hz` -> `440 Hz` triangle through 900 Hz lowpass).
12. `syncMute(muted)`: smoothly ramps master ambience gain to `0.0001` when `muted` is true, or restores active scene & hifi gains when `false`.
13. `unlock()`: attempts to ensure/resume AudioContext and start any pending `desiredScene` / `hifiOn` playback if not yet active.
14. `stopAll()`: stops all intervals/timeouts, ramps down and disconnects nodes cleanly.

CRITICAL SAFETY RULES:
- NEVER call `exponentialRampToValueAtTime(0, ...)` anywhere — always use `0.0001` or larger!
- Pre-allocate 2-second reusable `white`, `pink`, and `brown` noise `AudioBuffer`s once per `AudioContext` (in a helper `_ensureNoiseBuffers(ctx)`), never per trigger.
- Keep master ambience gain modest (`<= 0.16`) so background soundscape is soothing, refined, and never clips.
- Check `ctx` safely everywhere (never throw if `ensureCtxFn()` returns `null`, or if a mock `AudioContext` has minimal node methods).
- Zero external URLs, zero external imports.
- STRICT CODE LENGTH CAP: Keep the entire file concise, DRY, and well-factored in **180–260 lines max** (no JSDoc comments or repetitive node setup; use 2 small helpers `playNoiseBurst(...)` and `playTone(...)`). Any output over 300 lines risks truncation!
""",
        "verify_cmd": VERIFY_SOUNDSCAPE,
    },
    {
        "name": "batch6_pantry_icons",
        "model": "deepseek-chat",
        "out_path": "js/pantryIcons.js",
        "max_tokens": 8192,
        "system": (
            "You are a luxury editorial botanical/culinary illustrator creating fine-line SVG apothecary and "
            "copperplate illustrations for a quiet-luxury residence app. Output ONLY valid ES module JavaScript."
        ),
        "prompt": r"""Create `js/pantryIcons.js` exporting:
```js
export const PANTRY_ICONS = {
  biscuit: `<svg ...>...</svg>`,
  yolk: `<svg ...>...</svg>`,
  jerky: `<svg ...>...</svg>`,
  pup_cup: `<svg ...>...</svg>`,
  salmon: `<svg ...>...</svg>`,
  duck_leg: `<svg ...>...</svg>`,
  steak: `<svg ...>...</svg>`,
  wagyu: `<svg ...>...</svg>`,
  cloche: `<svg ...>...</svg>`,
  gramophone: `<svg ...>...</svg>`,
};
```

Design direction (AD100 / Quiet Luxury / Fine Apothecary Copperplate Engraving):
- Every SVG MUST start with `<svg viewBox="0 0 64 64" width="48" height="48" xmlns="http://www.w3.org/2000/svg">` and end with `</svg>`.
- Aesthetic: delicate espresso-ink linework (`stroke="#231D18"`, `stroke-width="1.35"` primary contours, `"0.85"` inner hatching/texture details, `stroke-linecap="round"`, `stroke-linejoin="round"`), antique brushed-brass details (`#C59B57` / `#A77D3C`), muted burgundy ribbon/wax accents (`#7D1E2E`), and soft mineral parchment washes (`#FAF5EB`, `#EFE6D5`, `#E8C9B5`, `#D89A82`, `#C78B62`, `#D6DFD8`).
- NO thick `2.4px` cartoon outlines, NO neon colors, NO external `<image>` or URLs!
- Subjects for the 10 keys:
  1. `biscuit`: Fluted oval artisan oat sablé biscuit resting on a porcelain saucer with delicate scoring lines.
  2. `yolk`: Apothecary clear glass jar with brass screw lid holding golden quail-yolk medallions and ribbon tag.
  3. `jerky`: Hand-sliced pasture poultry tender strips wrapped cleanly on folded parchment paper tied with burgundy twine.
  4. `pup_cup`: Fluted porcelain demitasse cup on saucer topped with velvety goat-milk microfoam & delicate cinnamon dash.
  5. `salmon`: Thick wild King Salmon belly fillet cut with crisp diagonal marbling lines on a dark slate tasting plate (`#2B3033` plate + coral-salmon `#E38E72` cut).
  6. `duck_leg`: Slow-cooked confit duck medallion with a delicate rosemary sprig on a brass-rimmed ivory plate.
  7. `steak`: Grass-fed veal tournedos tied neatly with butcher twine + herb sprig on warm travertine dish.
  8. `wagyu`: Hinged dark walnut presentation box with brass clasp (`NO.09` / subtle seal) revealing richly marbled M9 cut inside.
  9. `cloche`: Domed brushed-silver & brass hotel steward cloche resting on a scalloped tray.
  10. `gramophone`: Brushed-brass turntable tonearm beside a steaming porcelain bone-broth bowl for the afternoon steward comforting ritual.
""",
        "verify_cmd": VERIFY_PANTRY_ICONS,
    },
    {
        "name": "batch6_update_content_script",
        "model": "deepseek-chat",
        "check_tacky_copy": True,
        "out_path": "scripts/update_quiet_luxury_content.py",
        "max_tokens": 8192,
        "system": (
            "You are a senior localization editor and Python automation engineer. Write a self-contained Python 3 "
            "script `scripts/update_quiet_luxury_content.py` that transforms `data/content.json` into pure Quiet-Luxury "
            "(Show, Don't Tell) Chinese copy WITHOUT changing any JSON structure, key names, or numeric gameplay values. "
            "Output ONLY valid Python source code."
        ),
        "prompt": r"""Write `scripts/update_quiet_luxury_content.py` which loads `data/content.json`, upgrades its copy to quiet-luxury standards (keeping every key, array structure, and numeric value intact), writes `data/content.json` back cleanly with `indent=2, ensure_ascii=False`, and exits cleanly.

READ THESE STRICT REQUIREMENTS CAREFULLY:

1. **CRITICAL GAMEPLAY INVARIANTS (NEVER MODIFY THESE)**:
   - Keep `meta` (`happy_threshold: 80`, `initial_happiness: 100`, etc.) UNCHANGED.
   - Keep `phone_notifications` (all 24 entries) UNCHANGED.
   - Keep `seed_players` (all 8 entries) UNCHANGED.
   - Keep `treats` length = 8, and NEVER alter any treat's `id`, `cost`, `prob`, or `target`!
   - Update ONLY each treat's `en`, `cn`, and `tag` strings according to this exact table:
     * `biscuit`: `en="OAT SABLÉ"`, `cn="燕麦黄油脆饼"`, `tag="日常茶点"`
     * `yolk`: `en="QUAIL YOLK"`, `cn="有机鹌鹑蛋冻干"`, `tag="轻巧试探"`
     * `jerky`: `en="PASTURE POULTRY"`, `cn="散养走地鸡胸脯"`, `tag="半数胜算"`
     * `pup_cup`: `en="GOAT MILK VELVET"`, `cn="无糖山羊奶微泡"`, `tag="海岸特调"`
     * `salmon`: `en="KING SALMON BELLY"`, `cn="野生帝王鲑鱼腹"`, `tag="丰腴回心"`
     * `duck_leg`: `en="CONFIT DUCK TENDER"`, `cn="油封慢煮鸭胸条"`, `tag="私厨诚意"`
     * `steak`: `en="GRASS-FED VEAL"`, `cn="草饲小牛里脊"`, `tag="体面和解"`
     * `wagyu`: `en="DRY-AGED M9 WAGYU"`, `cn="干式熟成和牛木匣"`, `tag="主厨臻选"`

2. **BANNED WORDS & LEGACY PATTERNS (MUST NOT APPEAR ANYWHERE IN THE SCRIPT OR GENERATED `data/content.json`)**:
   - NEVER use: `贵族`, `高贵`, `豪宅`, `顶奢`, `富豪`, `土豪`, `有钱`, `VIP`, `会员超市`, `会员店`, `会员制`, `会员卡`, `排面`, `扫货`, `巨无霸`, `吧台小哥`, `小姐姐`, `甜品橱窗`.
   - NEVER use Chinese city/region names like 杭州/西湖/江南 etc.
   - NEVER include these outdated slang/tacky words anywhere in `data/content.json`: `穷鬼`, `穷到`, `破产`, `小视频`, `电瓶车`, `外卖`, `猫爬架`, `路边摊`, `大喇叭`, `洗衣篮`, `低音炮`, `促销`, `非酋`, `基操勿六`, `吃瓜群众`, `评论区炸了`, `零食急救柜`, `急救零食`, `零食柜`.

3. **Rewrites required in `ticker_templates`**:
   - Keep exact keys: `swap`, `collapse`, `wagyu_fail`, `rescue_video`, `streak` (5~10 varied Chinese club ledger lines each).
   - Keep exact placeholders used in each list:
     * `swap`: `{player}`, `{target}`, `{old_score}`, `{new_score}`, `{score}`
     * `collapse`: `{player}`, `{old_score}`, `{new_score}`
     * `wagyu_fail`: `{player}`, `{new_score}` (optional)
     * `rescue_video`: `{player}`, `{new_score}` (narrative: steward brings a warm bowl of unsalted bone broth & lowers the 33RPM vinyl tonearm so Bruce softens back to `80` points!)
     * `streak`: `{player}`, `{score}`

4. **Rewrites required in `treat_monologues`**:
   - Keep `fail_lines` (6~8 lines), `wagyu_fail_line` (single string), `success_lines` (6~8 lines).
   - Express Bruce's picky, aristocratic little-dachshund poise through sensory tastes (scent, temperature, butter biscuit texture, silk scarf tilt, belly rub on alpaca rug) rather than crass talk about money/price.

5. **Clean targeted activities & previews cleanly**:
   - Do NOT erase unaffected good lines in `activities`! Read `data/content.json`, and for EVERY activity under `activities` (`home_hide_seek`, `home_brush`, `home_rain_vinyl`, `home_kitchen`, `home_nap`, `street_cafe`, `street_walk`, `street_lawn`, `street_window`, `street_bridge`), inspect each line in `win_lines`, `phone_fail_lines`, `hazard_fail_lines`:
     * Cleanly rewrite any line containing legacy terms (replacing e.g. cat tree -> `羊驼毛软榻`, laundry basket -> `亚麻藤编篮`, subwoofer -> `高速吹风筒`, delivery scooter -> `海岸滑板少年` or `观光单车`, loudspeaker -> `自动喷淋头`, price-comparison -> `回复工作邮件`, security guard -> `礼貌的门侍`), OR supply crisp curated replacements keyed cleanly by string match / regex normalization so zero legacy words remain while preserving `>= 3` rich varied lines per array!
   - Keep `activities["home_rain_vinyl"]["title"] = "阁楼黑胶时光"` and `"subtitle"] = "午后慢转"`.
   - In `remote_previews`:
     * Update `warehouse`: `title="ELOWEN · 有机市集"`, `subtitle="海岸买手食集与布鲁斯的鲜食巡礼"`, `teaser="冷杉木与黄铜陈列架间陈列着野生帝王鲑、有机羊奶酪与草饲骨汤冻干，入口托盘上静放着 07 号记账卡。"`
     * Update `yacht`: `title="白帆游艇码头"`, `subtitle="法式单桅帆船与柚木浮桥的午后海风"`, `teaser="微缩单桅帆船停泊在温润柚木浮桥旁，半开放细木沙龙舱透出琥珀灯光，布鲁斯端坐在亚麻卧垫上迎着海风。"`, `planned_perks=["船头迎风巡望", "甲板亚麻小憩"]`
     * Update `california`: replace `"路边摊隐藏美食"` in `planned_perks` with `"海岸农庄无花果与鲜食篮"`.

Note: Inside Python, represent `REPO_ROOT = Path(__file__).resolve().parents[1]` and read/write `REPO_ROOT / "data" / "content.json"`. Print `UPDATED_CONTENT_JSON_OK` on completion.
""",
        "verify_cmd": VERIFY_CONTENT_SCRIPT,
    },
    {
        "name": "batch6_concierge_dialogue",
        "model": "deepseek-chat",
        "check_tacky_copy": True,
        "out_path": "data/concierge_dialogue_v4.json",
        "max_tokens": 4096,
        "system": (
            "You write ultra-refined, warm Chinese in-world microcopy for Bruce (a cream long-haired dachshund "
            "in a quiet-luxury coastal penthouse). Follow Show, Don't Tell strictly. Output ONLY valid JSON."
        ),
        "prompt": r"""Output valid JSON for `data/concierge_dialogue_v4.json` with these exact 7 keys:
1. `"butler_water_lines"`: array of 4 Chinese lines (12~32 chars each). Describe the butler uncapping chilled flint-glass Evian mineral water onto the travertine/walnut table, condensation on crystal glass, and 布鲁斯 trotting over to inspect with his burgundy scarf.
2. `"butler_pantry_lines"`: array of 3 Chinese lines (12~32 chars each) when checking the House Pantry chilled cuts for 布鲁斯.
3. `"chauffeur_cafe_lines"`: array of 3 Chinese lines (12~32 chars each) when the B1 chauffeur signals the car is poised downstairs for the Coastal Roastery (`海岸烘焙室`).
4. `"chauffeur_market_lines"`: array of 3 Chinese lines (12~32 chars each) when the B1 chauffeur awaits in the subterranean porte-cochère while picking up the `07` house card for `ELOWEN` organic market.
5. `"chauffeur_marina_lines"`: array of 3 Chinese lines (12~32 chars each) when contacting the private marina berth master about sea breeze and teak pier readiness (`白帆游艇码头`).
6. `"hifi_on_lines"`: array of 3 Chinese lines (12~32 chars each) when the Harman smoked-glass dome warms up with unhurried electric-piano jazz.
7. `"hifi_off_lines"`: array of 2 Chinese lines (12~32 chars each) when the acoustic system fades back into peaceful afternoon stillness.

STRICT RULES:
- Address the dog as `布鲁斯` (never English `Bruce`).
- Strictly forbid: 贵族/高贵/豪宅/顶奢/富豪/土豪/有钱/VIP/会员/排面/扫货/巨无霸/吧台小哥/小姐姐/甜品橱窗/穷鬼/低音炮/小视频, and never mention Chinese city names.
- Let status shine quietly through textures (flint glass, travertine, walnut, brass bell, B1 porte-cochère, cellar-chilled water, smoked glass).
""",
        "verify_cmd": VERIFY_CONCIERGE_JSON,
    },
]

if __name__ == "__main__":
    results = run_parallel_codegen(TASKS, batch_name="batch6_pantry_audio_concierge", max_workers=4, max_retries=3)
    print(json.dumps(results, ensure_ascii=False, indent=2))
