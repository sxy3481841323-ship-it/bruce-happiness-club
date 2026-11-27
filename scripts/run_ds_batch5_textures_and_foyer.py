#!/usr/bin/env python3
"""
Batch 5A (DeepSeek Parallel Codegen):
1. scripts/penthouse_kit/tex_luxury_props.py (Evian label, Concierge screen, Foyer bronze mirror, Foyer stone medallion, Fire embers, Charred oak bark)
2. scripts/penthouse_kit/tex_wine_and_cafe.py (Fine wine bottle labels x3, Celadon sage floor tile, RGBA fireplace flame atlas)
3. scripts/penthouse_kit/mod_entry_and_niches.py (AD100 Grand Foyer Alcove rebuild + staircase/salon sculpture niches)
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from ds_worker import run_parallel_codegen


TEX_SYS = (
    "You are a senior procedural PBR texture & UI graphics engineer writing pure Python 3 "
    "(PIL.Image, PIL.ImageDraw, PIL.ImageFilter, PIL.ImageFont, numpy, math) for Three.js glTF 2.0.\n"
    "Rules:\n"
    "- Every texture generator MUST be deterministic via `np.random.default_rng(...)`.\n"
    "- Font loading on macOS/Linux: try `/System/Library/Fonts/Helvetica.ttc`, "
    "`/System/Library/Fonts/Supplemental/Georgia.ttf`, `/System/Library/Fonts/Supplemental/Arial.ttf`, "
    "`/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`, falling back to `ImageFont.load_default()`.\n"
    "- STRICT Quiet-Luxury rule: NEVER include literal status words or geographic city names.\n"
    "- Return ONLY raw Python 3 source code with NO markdown fences."
)

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

VERIFY_PROPS = r"""
import sys, numpy as np
sys.path.insert(0, 'scripts')
from penthouse_kit.tex_luxury_props import (
    make_evian_label_tex,
    make_concierge_screen_tex,
    make_foyer_mirror_tex,
    make_foyer_medallion_tex,
    make_fire_ember_tex,
    make_charred_bark_tex,
)
checks = [
    ('evian', make_evian_label_tex(512, 256), (512, 256)),
    ('concierge', make_concierge_screen_tex(512, 320), (512, 320)),
    ('mirror', make_foyer_mirror_tex(1024), (1024, 1024)),
    ('medallion', make_foyer_medallion_tex(1024), (1024, 1024)),
    ('ember', make_fire_ember_tex(512, 256), (512, 256)),
    ('bark', make_charred_bark_tex(512, 256), (512, 256)),
]
for name, im, sz in checks:
    assert im.size == sz and im.mode == 'RGB', f'{name} bad {im.size} {im.mode}'
    arr = np.asarray(im, dtype=np.float32)
    assert np.isfinite(arr).all() and float(arr.std()) > 8.0, f'{name} low contrast std={arr.std():.2f}'
print('TEX_LUXURY_PROPS_OK')
"""

VERIFY_WINE_CAFE = r"""
import os, sys, numpy as np
sys.path.insert(0, 'scripts')
from penthouse_kit.tex_wine_and_cafe import (
    make_fine_wine_label_tex,
    make_celadon_sage_tile_tex,
    make_flame_atlas_tex,
)
os.makedirs('assets/textures', exist_ok=True)
for v in (0, 1, 2):
    w = make_fine_wine_label_tex(512, variant=v)
    assert w.size == (512, 512) and w.mode == 'RGB'
    assert np.std(np.asarray(w, dtype=np.float32)) > 15.0
tile = make_celadon_sage_tile_tex(1024)
assert tile.size == (1024, 1024) and tile.mode == 'RGB'
tarr = np.asarray(tile, dtype=np.float32)
mr, mg, mb = float(tarr[:,:,0].mean()), float(tarr[:,:,1].mean()), float(tarr[:,:,2].mean())
assert mg > mr and mg > mb, f'Sage tile should be celadon green, got ({mr:.1f},{mg:.1f},{mb:.1f})'
flame = make_flame_atlas_tex(512)
assert flame.size == (512, 512) and flame.mode == 'RGBA'
farr = np.asarray(flame)
assert farr[5, 5, 3] < 8 and farr[420, 256, 3] > 210, 'Flame alpha mask inverted or weak'
flame.save('assets/textures/fireplace_flame.png', format='PNG', optimize=True)
print(f'TEX_WINE_CAFE_OK sage=({mr:.0f},{mg:.0f},{mb:.0f}) flame_core_a={int(farr[420,256,3])}')
"""

VERIFY_FOYER = r"""
import sys
sys.path.insert(0, 'scripts')
from penthouse_kit.prim_lib import SceneContext
from penthouse_kit.mod_entry_and_niches import build_entry_and_niches

ctx = SceneContext('TestFoyer')
mats = {k: ctx.color_mat(k, (0.85, 0.80, 0.72, 1.0)) for k in [
    'oak', 'plaster', 'marble', 'walnut_fluted', 'walnut_solid', 'brass', 'bronze_dark',
    'warm_led', 'warm_bulb', 'glass', 'frosted_glass', 'travertine', 'cognac_suede',
    'patron_card', 'foyer_mirror', 'foyer_medallion', 'ceramic_white', 'cream_pillow',
    'charcoal', 'bark', 'olive_leaf', 'olive_leaf_bright', 'orchid_white'
]}
build_entry_and_niches(ctx, mats)
all_pts = [p for b in ctx.builders.values() for p in b.positions]
xs = [p[0] for p in all_pts]; ys = [p[1] for p in all_pts]; zs = [p[2] for p in all_pts]
names = {b.name for b in ctx.builders.values()}
for req in ('EntryPatronCard', 'EntryConsoleTravertine', 'EntryMirrorBronze', 'EntryMirrorGlass', 'EntryFloorMedallion'):
    assert req in names, f'Missing mesh {req}, got {names}'
assert -15.1 <= min(xs) and max(xs) <= 14.95
assert -0.05 <= min(ys) and max(ys) <= 9.6
assert -12.0 <= min(zs) and max(zs) <= 14.8
print('MOD_FOYER_V3_OK', len(all_pts), len(names))
"""

TASKS = [
    {
        "name": "tex_luxury_props",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/tex_luxury_props.py",
        "check_tacky_copy": True,
        "system": TEX_SYS,
        "prompt": """Write `scripts/penthouse_kit/tex_luxury_props.py` implementing 6 high-craft PIL/NumPy texture generators (RGB mode):
1. `make_evian_label_tex(w=512, h=256) -> Image.Image`:
   - Crisp translucent-feeling pure glacier white band (`#F9FBFD`) framed top/bottom by cool pale-aqua tint (`#E8F1F6`).
   - Centered delicate pale-rose & alpine-blue jagged 3-peak Alps mountain silhouette line (`#D47D8A` and `#9ABCE0`) above centered serif/sans lettering `"EVIAN"` (deep glacier slate `#1F3042`) and hairline caption `"NATURAL SPRING WATER"`. Keep contrast crisp (`std > 12`).
2. `make_concierge_screen_tex(w=512, h=320) -> Image.Image`:
   - Deep brushed obsidian OLED bezel (`#101012`) with thin 2px champagne-gold inner frame (`#D6B476`).
   - Top header `"PH·01 CONCIERGE INTERCOM"` in tracked warm gold, plus 3 crisp tactile status tiles:
     - `"01  BUTLER       · STANDBY"`
     - `"02  CHAUFFEUR    · BAY B1 READY"`
     - `"03  VALET & WINE · ACTIVE"`
   - Bottom soft jade status dot + `"TAP TO SUMMON HOUSE STAFF"`.
3. `make_foyer_mirror_tex(size=1024) -> Image.Image`:
   - Smoked antique bronze beveled mirror surface: warm deep espresso-bronze base with subtle champagne diagonal sunlit reflection band, subtle vertical skylight shimmer gradient, and faint antique-mercury vignette edge.
4. `make_foyer_medallion_tex(size=1024) -> Image.Image`:
   - AD100 grand foyer inlaid stone floor medallion: pale cream honed Calacatta stone field with subtle grey-gold veins, framed by an inlaid dark Nero Marquina octagonal border, nested brushed champagne-brass double geometric hairline rings, and a delicate minimalist 8-point compass inlay in the center.
5. `make_fire_ember_tex(w=512, h=256) -> Image.Image`:
   - Glowing hearth bed of dark basalt ash & charred coal chunks crossed with incandescent molten-amber (`#FF8C24`), cherry-crimson (`#CC2B12`), and white-hot yellow ember veins (`rng` deterministic cracks + bokeh glow).
6. `make_charred_bark_tex(w=512, h=256) -> Image.Image`:
   - Deep blackened split-oak bark striations on the upper portion blending into glowing orange-crimson burning ember fissures near the bottom/edge (`v > 0.58`) so split logs look actively aflame underneath.""",
        "verify_cmd": ["python3", "-c", VERIFY_PROPS],
    },
    {
        "name": "tex_wine_and_cafe",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/tex_wine_and_cafe.py",
        "check_tacky_copy": True,
        "system": TEX_SYS,
        "prompt": """Write `scripts/penthouse_kit/tex_wine_and_cafe.py` implementing 3 PIL/NumPy generators:
1. `make_fine_wine_label_tex(size=512, variant=0) -> Image.Image` (RGB):
   - Cylindrical wine bottle wrap texture for Sketchfab-matched Grand Cru bottles: dark emerald-burgundy glass above & below, wine/gold neck capsule highlight, and a crisp cream-ivory French paper label wrapped across `x in [64, 448], y in [145, 365]` with a double crimson/gold hairline border, minimalist vineyard crest diamond, and tracked lettering (`variant==0` -> `"CHATEAU MALIBU"`, `variant==1` -> `"COTE DE BEAUNE"`, `variant==2` -> `"BAROLO RISERVA"` + `"GRAND VIN · 2018"`).
2. `make_celadon_sage_tile_tex(size=1024) -> Image.Image` (RGB):
   - Matte honed pale celadon-pistachio sage ceramic floor tile matching the Sketchfab reference cafe floor (`2x2` grid per repeat): soft sage-celadon stone base around RGB `(182, 206, 174)` with subtle cloudy mineral variance and crisp `5px` muted sage grout lines at tile seams (`mean G > mean R` and `mean G > mean B`).
3. `make_flame_atlas_tex(size=512) -> Image.Image` (RGBA!):
   - Glowing upward-flickering wood-fire flame tongue texture on pure transparent background (`alpha=0` along all 4 borders!):
   - Built mathematically in NumPy with multi-harmonic organic flame curves (`x` centered at `0.5`, base near `y=0.88`, tapering upward to `y=0.08`): bright warm-white core near bottom-center (`(255, 244, 196)`), rich golden-amber mid (`(255, 165, 48)`), warm orange-red outer tips (`(238, 72, 18)`), smooth Gaussian falloff to `alpha = 0` at borders and `alpha > 220` at core `(y=420, x=256)`.""",
        "verify_cmd": ["python3", "-c", VERIFY_WINE_CAFE],
    },
    {
        "name": "mod_entry_and_niches_v3",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_entry_and_niches.py",
        "check_tacky_copy": True,
        "system": MOD_SYS,
        "prompt": """Rewrite `scripts/penthouse_kit/mod_entry_and_niches.py` with `build_entry_and_niches(ctx, mats)` to DEMOLISH the plain old entry table and build an **AD100 Grand Foyer Alcove** (plus keep the salon niches intact), staying strictly outside the center salon rug (`X in [-2.4, 9.8], Z in [-6.8, 6.8]`):
Available `mats` keys: `marble`, `walnut_fluted`, `walnut_solid`, `travertine`, `brass`, `bronze_dark`, `warm_led`, `warm_bulb`, `cognac_suede`, `patron_card`, `foyer_mirror`, `foyer_medallion`, `ceramic_white`, `cream_pillow`, `charcoal`, `bark`, `olive_leaf`, `olive_leaf_bright`, `orchid_white`.
Required Foyer & Niche geometry:
1. **Grand Foyer Architectural Framing (`X in [-14.95, -12.0], Z in [4.3, 9.2], Y in [0.0, 9.1]`)**:
   - Floor inlay `"EntryFloorMedallion"` (`mats["foyer_medallion"]`) at `(-13.25, 0.015, 6.65)` with size `(2.6, 0.02, 4.4)`.
   - Full-height Bookmatched Calacatta Marble focal wall panel (`X=-14.86, Y=4.55, Z=6.65, sx=0.14, sy=8.9, sz=4.5`) flanked by vertical `walnut_fluted` wing panels (`Z=4.2` and `Z=9.1`), brushed champagne `brass` pilasters (`Z=4.42` and `Z=8.88`), and top `warm_led` cove beam (`Y=8.92`).
   - Sculptural overhanging Travertine & Fluted-Walnut Console (`"EntryConsoleTravertine"`): two tapered fluted walnut & brass-banded plinth piers at `Z=5.3` & `Z=8.0` (`Y=0..1.58`), lower travertine gallery shelf (`Y=0.45`) with linen coffee-table art books (`cream_pillow`, `charcoal`), and a thick rounded Roman travertine top slab (`X=-14.02, Y=1.68, Z=6.65, sx=1.56, sy=0.16, sz=3.8`).
   - Beveled Arched/Circular Smoked-Bronze Mirror (`"EntryMirrorBronze"` ring + `"EntryMirrorGlass"` in `mats["foyer_mirror"]` cylinder `r=0.95`, facing `+X` via `rot_z=math.pi/2`) at `(-14.74, 4.35, 6.65)`, topped with a sleek vertical mirror arch trim in brass.
   - **Pair of Alabaster & Brass Wall Sconces** flanking the mirror at `X=-14.72, Y=4.35, Z=5.10` and `Z=8.20`: brass backplate + cylindrical warm-glowing alabaster diffusers (`mats["warm_bulb"]`).
2. **Rich Foyer Console Styling + Tilted 3D `"EntryPatronCard"` (MUST use exact mesh name `"EntryPatronCard"` with `mats["patron_card"]`)**:
   - Cognac leather & brushed-brass framed valet tray (`X=-13.86, Y=1.78, Z=6.44, sx=0.76, sy=0.05, sz=1.02`) + brushed-brass card easel stand + sculpted brass car key fob resting inside tray.
   - **`"EntryPatronCard"` tilted `22°` up toward `+X` facing the camera at `(-12.55, 2.36, 6.66)`** so it reads large, bright, crisp, and upright/unmirrored! Use EXACT 4 corners:
     `p0 = (-13.74, 1.80, 6.68)` `uv0=(0.0, 0.0)`
     `p1 = (-13.74, 1.80, 6.24)` `uv1=(1.0, 0.0)`
     `p2 = (-14.00, 1.92, 6.24)` `uv2=(1.0, 1.0)`
     `p3 = (-14.00, 1.92, 6.68)` `uv3=(0.0, 1.0)`
     Call `card.add_tri_raw(p0, p1, p2, uv0, uv1, uv2)` and `card.add_tri_raw(p0, p2, p3, uv0, uv2, uv3)`.
   - Left side of console (`Z=7.85`): fluted ceramic vessel (`ceramic_white`) holding dark slender orchid stems (`bark`) and delicate white Phalaenopsis orchid blossoms (`orchid_white`).
   - Right side of console (`Z=5.25`): smoked charcoal & brass reed diffuser bottle (`charcoal` + thin vertical `brass` reeds) + sculpted travertine tray sphere.
3. **Preserve 1F Collectors' Niches**:
   - `CollectorPlinth` & fluid bronze `CollectorArpSculpture` at `(13.5, 0..3.4, -9.6)`.
   - `AmphoraUrn` & sculpted olive branches at `(13.3, 0..3.2, 8.6)`.
   - Staircase floating `GalleryShelves`, stacked monographs & stoneware vase at `(-13.8, 2.4..4.2, 12.2)`.""",
        "verify_cmd": ["python3", "-c", VERIFY_FOYER],
    },
]

if __name__ == "__main__":
    print("=== Running DeepSeek Batch 5A (Textures & Grand Foyer) ===")
    res = run_parallel_codegen(TASKS, batch_name="luxury_v3_tex_foyer", max_workers=3, max_retries=3)
    for r in res:
        print(r)
