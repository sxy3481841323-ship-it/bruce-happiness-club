#!/usr/bin/env python3
"""
Batch 9 ("123"):
Parallel DeepSeek orchestration for:
1. Coastal Café 360-degree Old-Money boiserie, fluted walnut library portal,
   shadow-box GeoArt framing, and two hand-knotted bordered lounge carpets.
2. Quiet-luxury Chinese monologue copy for Terrace Sunset Cuddle (+2),
   CH 01-04 TV Spatial Audio Synesthesia, and Coastal Café Boiserie.
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from ds_worker import run_parallel_codegen


def main():
    tasks = [
        {
            "name": "cafe_kit_oldmoney",
            "model": "deepseek-chat",
            "out_path": "scripts/cafe_kit_oldmoney.py",
            "system": (
                "You are a senior Three.js architectural technical artist specializing in Old-Money AD100 "
                "coastal roastery interiors. Enforce ZERO blank white walls: every wall face and column exposed "
                "during 360-degree orbit must have tactile Marmorino limestone boiserie, fluted walnut millwork, "
                "brushed brass reveals, and museum framing. Keep code clean, bug-free, and strictly under 245 lines."
            ),
            "prompt": """Create `scripts/cafe_kit_oldmoney.py` exporting:
`def build_cafe_oldmoney_millwork(mb, mats: dict):`

EXACT `mb` factory and `MeshBuilder` methods from `scripts/build_cafe_glb.py`:
- `b = mb(mesh_name: str, mat_idx: int)`
- `b.add_box(cx, cy, cz, sx, sy, sz, uv_tile=0.0, rot_y=0.0)`
- `b.add_quad(p0, p1, p2, p3, uv_scale=(1.0, 1.0), flip=False)`  # CCW from front face (+normal = cross(p1-p0, p2-p0))
- `b.add_cylinder(cx, y0, cz, r_bot, r_top, height, segs=16, rot_x=0.0, rot_z=0.0, cap_top=True, cap_bot=True)`

EXACT keys available in `mats`:
`"marmorino"`, `"walnut_fluted"`, `"walnut_dark"`, `"brass"`, `"travertine"`, `"rug_salon"`, `"rug_aubusson"`, `"warm_glow"`, `"glass_reed"`, `"ceramic"`, `"oak"`

CRITICAL COORDINATES (4 units = 1 meter, room spans X [-11.8, +11.8], Z [-22.2, +20.2], Y [0, 16.4]):
1. **Two Museum-Grade Hand-Knotted Bordered Carpets (`Y = 0.022`) + Floor Perimeter Inlay (`Y = 0.012`)**:
   - Carpet 1 (`mats["rug_salon"]`): placed cleanly under front-left window sofa & café tables at `X in [-10.9, -1.7], Z in [0.9, 9.5], Y = 0.024`. Use `b_rug1.add_quad((-10.9, 0.024, 9.5), (-1.7, 0.024, 9.5), (-1.7, 0.024, 0.9), (-10.9, 0.024, 0.9), uv_scale=(1.0, 1.0))` (so `+Y` normal & non-tiled border frames all 4 edges cleanly!), plus cream travertine/silk fringe strips (`0.14` deep) along `Z=0.83` and `Z=9.57`.
   - Carpet 2 (`mats["rug_aubusson"]`): placed under mid-back window lounge group at `X in [-10.9, -1.7], Z in [-11.4, -1.4], Y = 0.024` (note potted plant at `(-9.8, -0.9)` & side table `(-9.2, 0.55)` stay cleanly on tile aisle between rugs!). Use same `+Y` CCW quad with `uv_scale=(1.0, 1.0)` + fringe strips along `Z=-11.47` and `Z=-1.33`.
   - Perimeter floor walnut & brass inlay strips at `Y = 0.012` framing `X = -11.0/+10.9` and `Z = -21.2/+19.5` (skip only bar plinth).

2. **South / Front Entrance & Coffee-Library Wall (`Z = +20.2`, inward `-Z` facing into room)**:
   - Grand Double Walnut & Reed-Glass Entrance Portal centered at `X in [-2.15, +2.15], Y in [0.0, 10.6], Z = 19.95`: deep walnut outer frame, paired panelled walnut doors with frosted reed-glass insets (`mats["glass_reed"]`), vertical brushed-brass bar pulls, brass kickplates, and brass-mullioned transom window (`Y = 8.4..10.4`).
   - Left (`X in [-11.3, -2.25]`) & Right (`X in [+2.25, +11.3]`) Two-Tier Boiserie:
     - Walnut plinth & dado wainscoting (`Y = 0.0..3.35, Z = 20.00`), continuous brushed-brass dado rail (`Y = 3.42, Z = 19.94`), upper walnut cornice (`Y = 14.95, Z = 19.90`).
     - Fluted walnut pilasters (`Y = 0.0..14.8, Z = 19.92, sx=0.42, sz=0.26`) at `X = -10.8, -6.6, -2.35, +2.35, +6.6, +10.8` with brass plinths/capitals.
     - Proud Marmorino raised boiserie frames (`Y = 4.4..13.8, Z = 19.98`) in bays centered at `X = -8.7, -4.5, +8.7`, each topped by a delicate brass sconce + `warm_glow` bulb cap.
     - **Collector Roastery Walnut Bookcase & Coffee Canister Niche** in bay `X in [+2.65, +6.30], Y in [3.75, 11.4], Z = 19.72`: dark walnut case, warm backlit cove (`mats["warm_glow"]`), 4 horizontal shelves with brass coffee canisters, ceramic pour-over carafes, and hardbound monographs (`oak` / `ceramic` / `brass` / `walnut_fluted`).

3. **Right Smooth Wall Bays (`X = +11.5`, inward `-X` — do NOT overlap brick wall `Z in [-7.4, +11.5]`)**:
   - In zones `Z in [-22.0, -7.5]` and `Z in [+11.6, +20.0]`: walnut lower dado (`Y = 0..3.35, X = 11.36`), brass dado rail (`Y = 3.42, X = 11.30`), fluted walnut pilasters (`X = 11.30, Y = 0..14.8`) at `Z = -21.2, -16.8, -8.0, +12.0, +19.4`.
   - Raised Marmorino boiserie panel moulding frames at `Z = -19.0` and `Z = +15.7` (`Y = 4.4..13.6, X = 11.38`).
   - **Museum Shadow-Box Frame & Brass Picture Light around `GeoArt` (`X=11.40, Y=8.4, Z=-12.6, height=4.6, width=3.8`)**: 4 hollow perimeter frame bars (`walnut_dark` outer + `brass` inner liner at `Y=10.85/5.95` and `Z=-14.65/-10.55`, center kept open so artwork shines cleanly!), plus overhead horizontal brass picture light (`X = 10.95, Y = 11.25, Z = -12.6`) with `warm_glow` strip.

4. **Left Column Walnut/Brass Accents (`X = -11.4, Z in (11.8, 2.0, -9.8, -21.8)`) + Back Pillar (`(1.3, -21.8)`)**:
   - Vertical fluted walnut face strips & brushed-brass collar bands at `Y = 0.35, 3.42, 13.8` (`sx=1.22, sz=1.22` collars) + walnut/brass ceiling frieze trim along `Y = 14.3` header beams.

Make sure there are NO unused variables, clean helper functions, and all coordinates stay clear of existing sofas/tables/bar. Return ONLY valid Python code (< 245 lines, no markdown fences).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/cafe_kit_oldmoney.py', doraise=True); "
                "import sys; sys.path.insert(0,'scripts'); "
                "from build_cafe_glb import MeshBuilder; import cafe_kit_oldmoney as m; "
                "bmap={}; mb=lambda n,mi: bmap.setdefault((n,mi), MeshBuilder(n,mi)); "
                "mats={k:i for i,k in enumerate(['marmorino','walnut_fluted','walnut_dark','brass','travertine','rug_salon','rug_aubusson','warm_glow','glass_reed','ceramic','oak'])}; "
                "m.build_cafe_oldmoney_millwork(mb, mats); "
                "tot=sum(len(b.indices)//3 for b in bmap.values()); assert tot>200, tot; print('OK cafe_kit_oldmoney:', tot, 'tris')\""
            ),
        },
        {
            "name": "sunset_and_cafe_v9_copy",
            "model": "deepseek-chat",
            "out_path": "data/sunset_and_cafe_v9.json",
            "check_tacky_copy": True,
            "system": (
                "You are a quiet-luxury Chinese narrative copywriter for '《布鲁斯日常 · 幸福指数俱乐部》' "
                "(owner Alex/Meya, cream long-haired dachshund Bruce wearing a #652C39 burgundy silk scarf). "
                "Tone: tactile, serene Old-Money & Apple minimalism. Never mention any real city names or tacky words "
                "(贵族/高贵/豪宅/顶奢/富豪/土豪/VIP/会员/排面). Show status only through wool-silk weave, brass click, "
                "limestone grain, sea breeze, and warm dog companionship. Output valid JSON only."
            ),
            "prompt": """Generate `data/sunset_and_cafe_v9.json` with exact top-level keys:
1. `sunset_cuddle_lines`: array of 8 evocative Chinese lines (18-36 chars each) for sitting beside Bruce on the widened terrace oatmeal bouclé sofa watching golden ocean ripples, seagulls, and distant sails (zero penalty slow moment).
2. `tv_audio_lines`: object with 4 keys (`"regatta"`, `"auction"`, `"equestrian"`, `"chamber"`), each a concise atmospheric Chinese caption (16-30 chars) describing both the visual broadcast and its subtle ambient sound in the salon:
   - `regatta`: gentle sea swell, sail luff & rigging chime
   - `auction`: refined Geneva tourbillon tick & velvet preview salon
   - `equestrian`: manicured turf hoof cadence & coastal meadow air
   - `chamber`: warm bowed cello night recital harmonizing through linen grilles
3. `cafe_boiserie_lines`: array of 5 evocative Chinese lines (18-34 chars each) appreciating the Coastal Roastery's Marmorino limestone boiserie walls, walnut coffee-library portal, and hand-knotted bordered silk-wool lounge carpets.
Return ONLY valid JSON.""",
            "verify_cmd": (
                "python3 -c \"import json; d=json.load(open('data/sunset_and_cafe_v9.json')); "
                "assert len(d['sunset_cuddle_lines'])>=8; "
                "assert set(d['tv_audio_lines'].keys())=={'regatta','auction','equestrian','chamber'}; "
                "assert len(d['cafe_boiserie_lines'])>=5; print('OK v9 JSON')\""
            ),
        },
    ]

    results = run_parallel_codegen(tasks, batch_name="batch9_123", max_workers=2, max_retries=3)
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
