#!/usr/bin/env python3
"""
Batch 5B (DeepSeek Parallel Codegen):
1. scripts/penthouse_kit/mod_media_fireplace.py (Harman Kardon smoked-glass dome acoustic towers + recessed wood-burning fireplace w/ 7 charred oak logs & glowing ember bed + gallery TV + arched lamp)
2. scripts/penthouse_kit/mod_salon_seating.py (Organic Camaleonda sofa + upgraded Calacatta/travertine salon coffee & cocktail tables + chilled tray w/ 3 glass Evian bottles + concierge intercom pager)
3. scripts/penthouse_kit/mod_loft_2f.py (Upgraded 2F vinyl console + Harman Kardon Aura Studio dome speaker + Executive Collector's Study Desk w/ chair, desk lamp, 2 glass Evian bottles & 2F concierge pager)
4. scripts/gen_concierge_fireplace_copy.py (Quiet-luxury copy for concierge intercom, Harman acoustics, wood fireplace & grand foyer departure)
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from ds_worker import run_parallel_codegen


MOD_SYS = (
    "You are a senior Three.js / AD100 3D interior architectural engineer writing Python 3 modules "
    "using `SceneContext` and `MeshBuilder`.\n"
    "EXACT API (DO NOT invent other methods or keyword argument names!):\n"
    "1. `b = ctx.mb(mesh_name: str, mat_idx: int)` returns a `MeshBuilder`.\n"
    "2. Exact `MeshBuilder` methods:\n"
    "   - `b.add_tri_raw(p0, p1, p2, uv0=(0,0), uv1=(1,0), uv2=(1,1))`\n"
    "   - `b.add_quad(p0, p1, p2, p3, uv_scale=(1.0, 1.0), flip=False)`\n"
    "   - `b.add_box(cx, cy, cz, sx, sy, sz, uv_tile=0.0, rot_y=0.0)`\n"
    "   - `b.add_rounded_box(cx, cy, cz, sx, sy, sz, bevel=0.06, uv_tile=0.0, rot_y=0.0)`\n"
    "   - `b.add_cylinder(cx, y0, cz, r_bot, r_top, height, segs=18, rot_x=0.0, rot_z=0.0, cap_top=True, cap_bot=True)`\n"
    "   - `b.add_sphere(cx, cy, cz, rx, ry=None, rz=None, rings=12, segs=18)`\n"
    "   - `b.add_lathe(cx, y0, cz, profile, segs=22)`\n"
    "   - `b.add_curved_tube(spine_pts, radii, segs=10)`\n"
    "Coordinate frame: Y-up, finite floats only. Return ONLY valid Python 3 code with no markdown fences."
)


def make_verify(fn_name: str, mod_name: str, extra_checks: str) -> list[str]:
    code = f"""
import sys
sys.path.insert(0, 'scripts')
from penthouse_kit.prim_lib import SceneContext
from penthouse_kit.{mod_name} import {fn_name}

ctx = SceneContext('Test')
mats = {{k: ctx.color_mat(k, (0.85, 0.80, 0.72, 1.0)) for k in [
    'oak', 'plaster', 'marble', 'walnut_fluted', 'walnut_solid', 'brass', 'bronze_dark',
    'chrome', 'warm_led', 'warm_bulb', 'fireplace_glow', 'fire_ember', 'charred_bark',
    'glass', 'glass_smoke', 'crystal_glass', 'frosted_glass', 'sheer_linen', 'boucle',
    'travertine', 'rug', 'burgundy', 'cream_pillow', 'cognac_suede', 'charcoal',
    'vinyl_black', 'vinyl_cover', 'tv_art', 'gal_1', 'gal_2', 'gal_3', 'gal_4',
    'evian_label', 'concierge_screen', 'ceramic_white', 'orchid_white'
]}}
{fn_name}(ctx, mats)
assert len(ctx.builders) > 0
all_pts = [p for b in ctx.builders.values() for p in b.positions]
xs = [p[0] for p in all_pts]; ys = [p[1] for p in all_pts]; zs = [p[2] for p in all_pts]
names = {{b.name for b in ctx.builders.values()}}
{extra_checks}
print('MOD_V3_OK', '{mod_name}', len(all_pts), f'x=({{min(xs):.2f}},{{max(xs):.2f}}) y=({{min(ys):.2f}},{{max(ys):.2f}}) z=({{min(zs):.2f}},{{max(zs):.2f}})')
"""
    return ["python3", "-c", code]


TASKS = [
    {
        "name": "mod_media_fireplace_v3",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_media_fireplace.py",
        "check_tacky_copy": True,
        "system": MOD_SYS,
        "prompt": """Rewrite `scripts/penthouse_kit/mod_media_fireplace.py` with `build_media_fireplace(ctx, mats)`:
Available `mats` keys: `travertine`, `walnut_fluted`, `walnut_solid`, `brass`, `bronze_dark`, `chrome`, `charcoal`, `warm_led`, `warm_bulb`, `fireplace_glow`, `fire_ember`, `charred_bark`, `glass_smoke`, `crystal_glass`, `tv_art`.
Required architectural elements along the right feature wall (`X in [10.4, 14.65]`):
1. **`MediaHearth` (`X in [12.3, 14.3], Z in [-6.8, 3.2], Y in [0.38, 1.50]`)**:
   - Floating travertine top (`bevel=0.05`), recessed walnut fluted drawer bank (`n_flutes=46`), brushed champagne-brass plinth & inlay line.
2. **Recessed Wood-Burning Firebox (`Z in [-4.1, 0.5], Y in [1.54, 2.52], X in [13.68, 14.62]`)**:
   - Build dark matte-obsidian/basalt recessed hearth cavity walls & mantle reveal in `ctx.mb("FireplaceCavity", mats["charcoal"])` plus brushed champagne-brass surround frame.
   - `"FireplaceEmbers"` (`ctx.mb("FireplaceEmbers", mats["fire_ember"])`): slightly textured glowing incandescent coal/ember bed (`X in [13.78, 14.42], Y = 1.62, Z in [-3.85, 0.25]`) with small scattered glowing ember lumps.
   - `"FireplaceLogs"` (`ctx.mb("FireplaceLogs", mats["charred_bark"])` + wrought-iron grate bars in `mats["charcoal"]`): **7 split charred-oak firewood logs** crisscrossed cleanly across `Z in [-3.55, 0.05]` at `Y in [1.72, 2.02]` using `add_cylinder` with varied `rot_x` / `rot_z` angles + glowing heartwood caps (`mats["fireplace_glow"]`) so flames in Three.js dance organically over real logs!
   - `"FireplaceGlass"` (`ctx.mb("FireplaceGlass", mats["crystal_glass"])`): subtle sleek low-iron tempered hearth wind guard ribbon across front `X = 13.66, Y in [1.58, 1.92], Z in [-4.0, 0.4]`.
3. **`GalleryTVScreen` & `GalleryTVBezel` (keep EXACT quad coordinates)**:
   - `tv = ctx.mb("GalleryTVScreen", mats["tv_art"])`, `p0=(14.10, 3.35, -5.0)`, `p1=(14.10, 3.35, 1.4)`, `p2=(14.10, 6.95, 1.4)`, `p3=(14.10, 6.95, -5.0)`.
   - Champagne brass gallery bezel at `X=14.16`.
4. **Pair of Flagship Harman Kardon Smoked-Glass Dome Acoustic Towers (`X = 13.05, Z = -7.35` and `Z = +3.75`)**:
   - Stepped forward clearly from the right wall so their silhouettes shine!
   - Each tower sits on a `HiFiPlinth` in `mats["glass_smoke"]` (`0.78 × 0.08 × 0.78`) + 4 champagne-brass isolation spikes (`mats["brass"]`).
   - `"HiFiTower"` lower sculptural tapered acoustic cabinet (`Y = 0.14..2.22`) in `mats["charcoal"]` + curved `mats["walnut_fluted"]` side ribs, housing **3 vertically stacked brushed-champagne concave driver rings & chrome phase plugs** (`Y = 0.65, 1.18, 1.72`) facing `-X`!
   - `"HiFiGlassDome"` (`ctx.mb("HiFiGlassDome", mats["glass_smoke"])`): signature **transparent smoked-borosilicate dome acoustic chamber** perched cleanly atop each tower (`Y = 2.22..3.35`, `add_lathe` dome profile `r = 0.27 -> 0.29 -> 0.24 -> 0.0`) with an internal central brushed-champagne waveguide column (`mats["chrome"]`) AND a **360° glowing `"HiFiHaloRing"`** (`ctx.mb("HiFiHaloRing", mats["warm_led"])`) inside the base of the dome (`Y = 2.34`)!
5. **`ArcLampBase`, `ArcLampArch`, `ArcLampShade`, `ArcLampBulb`**:
   - Keep lamp base at `(12.6, 0.0, 4.8)` arching smoothly to hanging dome + `ArcLampBulb` at `(10.6, 4.95, 2.8)`.""",
        "verify_cmd": make_verify(
            "build_media_fireplace",
            "mod_media_fireplace",
            "for rm in ('GalleryTVScreen', 'ArcLampBulb', 'FireplaceEmbers', 'FireplaceLogs', 'HiFiTower', 'HiFiGlassDome', 'HiFiHaloRing'): assert rm in names, f'Missing {rm}'",
        ),
    },
    {
        "name": "mod_salon_seating_v3",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_salon_seating.py",
        "check_tacky_copy": True,
        "system": MOD_SYS,
        "prompt": """Rewrite `scripts/penthouse_kit/mod_salon_seating.py` with `build_salon_seating(ctx, mats)`:
Available `mats` keys: `rug`, `boucle`, `walnut_solid`, `walnut_fluted`, `marble`, `travertine`, `brass`, `bronze_dark`, `chrome`, `burgundy`, `cognac_suede`, `cream_pillow`, `charcoal`, `crystal_glass`, `evian_label`, `concierge_screen`.
Keep 1F Salon sofa (`X in [-1.8, 5.2], Z in [-6.8, 0.6]`), `SalonRug`, 3 asymmetrical pebble cushions, and Jeanneret lounge chair (`7.2, -6.0`) + drum table (`9.1, -5.2`), AND upgrade the 1F Salon Coffee/Cocktail Table ensemble (`X = 4.25, Z = -1.70`, staying strictly `Z <= 0.9` so Bruce's `walkBounds Z >= 1.4` stays 100% unobstructed!):
1. **Upgraded Layered 1F Salon Table Ensemble (`X = 4.25, Z = -1.70`)**:
   - Fluted travertine twin curved pedestals (`X=3.35` & `5.15, Z=-1.70`) + brass plinth rings supporting a thick beveled **Bookmatched Calacatta Marble slab top** (`X=4.25, Y=0.86, Z=-1.70, sx=3.05, sy=0.10, sz=1.62`, top surface `Y=0.91`).
   - Overlapping higher **Smoked-Bronze & Marble Cocktail Tier** (`X=5.85, Z=-2.35, top Y=1.12`): fluted bronze cylindrical plinth + brass gallery collar + honed travertine/marble beveled top (`1.45 × 0.08 × 1.45`).
   - Stacked silk-linen exhibition monographs + carved stoneware bowl on one corner.
2. **Chilled Brushed-Silver Tray with 3 Glass Evian-Standard Mineral Water Bottles (`EvianBottles1F`, `EvianLabels1F`)**:
   - Brushed-chrome chilled service tray (`X=3.95, Y=0.925, Z=-1.58`, `0.62 × 0.03 × 0.42`) in `mats["chrome"]`.
   - **3 Sleek Clear Flint-Glass Evian Bottles** in `ctx.mb("EvianBottles1F", mats["crystal_glass"])` arranged naturally on the tray (lathed slender tear-drop silhouette: `r=0.068` body, graceful shoulder taper to `r=0.022`, total height `0.44`), each wrapped mid-body with an `add_cylinder` label band in `ctx.mb("EvianLabels1F", mats["evian_label"])` (`h=0.18`) and topped with a white/silver cap (`mats["chrome"]` / `mats["cream_pillow"]`), PLUS **2 faceted clear crystal water tumblers** beside them!
3. **1F House Concierge Intercom Pager (`ConciergePager1F`, `ConciergeScreen1F`) at `(5.82, 1.13, -2.22)`**:
   - Sleek angled brushed-brass & matte obsidian architectural desk pager housing (`ctx.mb("ConciergePager1F", mats["charcoal"])` + brass trim frame `mats["brass"]`), featuring an angled front touchscreen quad (`ctx.mb("ConciergeScreen1F", mats["concierge_screen"])` facing camera `-Z/+Z` cleanly — orient screen slightly angled toward viewer `(0, 0, +1)` / `-X`!), 3 tiny tactile brass call buttons for Butler / Chauffeur / Valet, and a slim docked metallic handset bar!""",
        "verify_cmd": make_verify(
            "build_salon_seating",
            "mod_salon_seating",
            "for rm in ('SalonRug', 'SofaSeat', 'EvianBottles1F', 'EvianLabels1F', 'ConciergePager1F', 'ConciergeScreen1F'): assert rm in names, f'Missing {rm}'",
        ),
    },
    {
        "name": "mod_loft_2f_v3",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_loft_2f.py",
        "check_tacky_copy": True,
        "system": MOD_SYS,
        "prompt": """Rewrite `scripts/penthouse_kit/mod_loft_2f.py` with `build_loft_2f(ctx, mats)` for the 2F Mezzanine Loft (`y0 = 9.21`, X in `[-14.9, -3.6]`, Z in `[-15.5, 6.2]`):
Available `mats` keys: `rug`, `walnut_solid`, `walnut_fluted`, `marble`, `travertine`, `brass`, `bronze_dark`, `chrome`, `warm_led`, `warm_bulb`, `glass_smoke`, `crystal_glass`, `vinyl_black`, `vinyl_cover`, `boucle`, `burgundy`, `cognac_suede`, `cream_pillow`, `charcoal`, `gal_1`, `gal_2`, `gal_3`, `gal_4`, `evian_label`, `concierge_screen`.
Keep `loft_rug` (`-8.2, 9.23, -4.2`), sunlit bouclé chaise daybed (`-5.8, -11.8`), 4 collector gallery frames (`wall_x=-14.80`), and Bruce's velvet pet throne (`-12.6, -2.2`), AND build these major upgrades:
1. **Upgraded Architectural Vinyl Hi-Fi Credenza + Harman Kardon Aura Dome Speaker (`X = -13.1, Z = -11.4, y0 = 9.21`)**:
   - Recessed smoked-bronze plinth + warm cove LED glow beneath (`y0 + 0.08`), fluted walnut body (`5.8` long), overhanging beveled **Calacatta Marble top slab** (`tt_y = 9.21 + 1.80 = 11.01`).
   - Brass-platter turntable (`cz + 0.6`), upright `vinyl_cover`, plus an iconic **Harman Kardon Aura Studio Smoked-Glass Dome Tabletop Speaker (`"LoftAuraSpeaker"`, `mats["glass_smoke"]`)** at `(-13.0, tt_y, -13.3)` with dark acoustic base, internal central chrome turbine cone, and glowing 360° warm LED halo ring (`mats["warm_led"]`), mirrored on the other end by stacked audiophile art books.
2. **Bespoke 2F Executive Study Desk & Collector Chair (`X in [-7.3, -4.3], Z in [2.1, 4.5], y0 = 9.21`, clear of Bruce `walkBounds Z <= 1.1`!)**:
   - Positioned along the sunlit mezzanine overlook facing `-Z`:
   - Curved cantilevered solid-walnut & Calacatta-inlaid executive desktop (`center=(-5.8, 10.68, 3.30), sx=2.95, sy=0.11, sz=1.32`) resting on twin sculpted fluted-walnut & brushed-brass architectural pedestals (`X=-6.9` and `X=-4.7`, `Y=9.21..10.62`) + cognac saddle-leather desktop blotter pad (`-5.8, 10.745, 3.18, sx=1.45, sz=0.72`).
   - Sculpted cognac-suede & curved-walnut executive swivel armchair at `(-5.8, y0, 4.25)` facing `-Z` (brass pedestal base + rounded seat + curved bolster back).
   - **Brushed-Brass Atelier Desk Lamp (`"LoftDeskLamp"`)** at `(-6.85, 10.74, 3.05)` with sleek angled arm, brass hood, and warm glowing `warm_bulb` diffuser.
   - **2 Glass Evian Bottles + Crystal Tumbler (`"EvianBottles2F"`, `"EvianLabels2F"`)** on a brushed-travertine coaster tray at `(-4.82, 10.74, 3.08)` (`mats["crystal_glass"]`, `mats["evian_label"]`, `mats["chrome"]`).
   - **2F Concierge Intercom Pager (`"ConciergePager2F"`, `"ConciergeScreen2F"`)** at `(-5.25, 10.74, 3.60)` facing `-Z` (obsidian housing, brass trim, angled `concierge_screen` quad, brass speed-dial keys) + linen-bound notebook & brass pen holder.""",
        "verify_cmd": make_verify(
            "build_loft_2f",
            "mod_loft_2f",
            "for rm in ('LoftAuraSpeaker', 'LoftDeskLamp', 'EvianBottles2F', 'ConciergePager2F', 'ConciergeScreen2F', 'gallery_painting_0'): assert rm in names, f'Missing {rm}'",
        ),
    },
    {
        "name": "gen_concierge_copy_v3",
        "model": "deepseek-chat",
        "out_path": "/Users/alex/.gemini/antigravity/brain/14d1e65e-43fb-418c-90dc-a038fd5ae47a/scratch/concierge_copy_v3.json",
        "check_tacky_copy": True,
        "system": "You are the Quiet Luxury editorial writer for Bruce Happiness Club. Return ONLY valid JSON with zero markdown fences, zero banned city names, and zero literal wealth/influencer clichés.",
        "prompt": """Generate fresh Chinese dialogue lines (strictly Show, Don't Tell via everyday understated objects) for `data/hub_deepseek.json`:
Forbidden words (never use): 贵族、高贵、豪宅、顶奢、富豪、土豪、有钱、VIP、会员、排面、扫货、巨无霸、吧台小哥、小姐姐、甜品橱窗.
Return ONLY valid JSON:
{
  "concierge_call": [
    "3 concise warm lines (16-28 Chinese chars each) when tapping the brass concierge intercom pager on the marble table or 2F desk — mentioning B1 chauffeur standby, evening pantry prep, or Bruce sniffing the glass alpine water bottle."
  ],
  "hifi_toggle": [
    "3 concise warm lines (16-28 Chinese chars each) when tapping the smoked-glass dome Harman acoustic towers — mentioning warm 360-degree halo glow, translucent crystal sound chamber, and subtle bass warmth across the oak floor."
  ],
  "fireplace_warm": [
    "3 concise warm lines (16-28 Chinese chars each) when tapping the crackling wood-burning hearth — mentioning split oak logs, dancing orange embers, and Bruce curling up by the travertine hearth."
  ],
  "patron_card_depart": [
    "3 concise warm lines (18-30 Chinese chars each) during the 4-second Grand Foyer reveal before going to ELOWEN — mentioning the bookmatched marble foyer sconces, white orchid petals, cognac leather tray, and NO. 07 house card."
  ]
}""",
        "verify_cmd": [
            "python3",
            "-c",
            "import json; d=json.load(open('/Users/alex/.gemini/antigravity/brain/14d1e65e-43fb-418c-90dc-a038fd5ae47a/scratch/concierge_copy_v3.json')); assert all(k in d and len(d[k])>=3 for k in ('concierge_call','hifi_toggle','fireplace_warm','patron_card_depart')); print('COPY_V3_OK')",
        ],
    },
]

if __name__ == "__main__":
    print("=== Running DeepSeek Batch 5B (Harman Speakers, Firebox, Salon & 2F Desk + Copy) ===")
    res = run_parallel_codegen(TASKS, batch_name="luxury_v3_3d_copy", max_workers=4, max_retries=3)
    for r in res:
        print(r)
