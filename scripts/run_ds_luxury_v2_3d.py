#!/usr/bin/env python3
"""
Batch 4 (Quiet Luxury 3D Modules):
1. scripts/penthouse_kit/mod_entry_and_niches.py (Entry travertine console, mirror, walnut suede tray, NO. 07 patron card, bronze sculpture, olive amphora, stair book niches)
2. scripts/penthouse_kit/mod_salon_seating.py (Organic Camaleonda bouclé sofa + 3 asymmetrical cognac/cashmere pebble cushions + Jeanneret chair + borderless rug)
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from ds_worker import run_parallel_codegen


COMMON_SYS = (
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


def make_verify(fn_name: str, mod_name: str, bounds_check: str, req_meshes: list[str] = None) -> list[str]:
    req = req_meshes or []
    code = f"""
import sys
sys.path.insert(0, 'scripts')
from penthouse_kit.prim_lib import SceneContext
from penthouse_kit.{mod_name} import {fn_name}

ctx = SceneContext('Test')
mats = {{k: ctx.color_mat(k, (0.85, 0.80, 0.72, 1.0)) for k in [
    'oak', 'plaster', 'marble', 'walnut_fluted', 'walnut_solid', 'brass', 'bronze_dark',
    'sheer_linen', 'warm_led', 'glass', 'frosted_glass', 'boucle', 'travertine', 'rug',
    'burgundy', 'cream_pillow', 'cognac_suede', 'patron_card', 'ceramic_white', 'soil',
    'bark', 'olive_leaf', 'olive_leaf_bright', 'charcoal'
]}}
{fn_name}(ctx, mats)
assert len(ctx.builders) > 0
all_pts = []
for b in ctx.builders.values():
    all_pts.extend(b.positions)
xs = [p[0] for p in all_pts]; ys = [p[1] for p in all_pts]; zs = [p[2] for p in all_pts]
names = {{b.name for b in ctx.builders.values()}}
for rm in {req!r}:
    assert rm in names, f'Missing mesh {{rm}}, got {{names}}'
{bounds_check}
print('MOD_V2_OK', '{mod_name}', len(all_pts), f'x=({{min(xs):.2f}},{{max(xs):.2f}}) y=({{min(ys):.2f}},{{max(ys):.2f}}) z=({{min(zs):.2f}},{{max(zs):.2f}})')
"""
    return ["python3", "-c", code]


TASKS = [
    {
        "name": "mod_entry_and_niches_3d",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_entry_and_niches.py",
        "check_tacky_copy": True,
        "system": COMMON_SYS,
        "prompt": """Write `scripts/penthouse_kit/mod_entry_and_niches.py` with `build_entry_and_niches(ctx, mats)` adding AD100 quiet-luxury entryway & collector touches (WITHOUT intruding into the 1F salon center rug `X in [-2.4, 9.8], Z in [-6.8, 6.8]`!):
Available `mats` keys: `travertine`, `walnut_solid`, `cognac_suede`, `patron_card`, `brass`, `bronze_dark`, `cream_pillow`, `ceramic_white`, `bark`, `olive_leaf`, `olive_leaf_bright`, `charcoal`, `plaster`.
Required details:
1. **Entryway Cantilevered Roman Travertine Console (`X in [-14.85, -13.35], Z in [5.0, 8.0], Y in [0.0, 1.72]`)**:
   - Two solid travertine plinth piers (`X=-14.1, Z=5.5` and `Z=7.5`, `Y=0.0..1.58`, width `1.1`) supporting a crisp cantilevered Roman travertine slab top (`X=-14.08, Y=1.65, Z=6.5, sx=1.48, sy=0.14, sz=3.05`).
   - Aged round bronze mirror mounted on Left Wall above the console (`X=-14.86, Y=4.05, Z=6.5`, thin `bronze_dark` outer ring + tinted mirror center using `add_cylinder(..., rot_z=math.pi/2)`).
2. **Walnut & Cognac-Suede Catchall Tray + 3D Patron Card `"EntryPatronCard"` (MUST use exact mesh name `"EntryPatronCard"` with `mats["patron_card"]`)**:
   - Low rounded walnut tray (`X=-13.95, Y=1.745, Z=6.42, sx=0.72, sy=0.05, sz=0.92`) with cognac suede inner bed (`Y=1.765`).
   - **`"EntryPatronCard"`**: exact upright upward-facing quad (`add_tri_raw`) resting at `Y=1.785` so a macro camera at `(-11.8, 2.55, 6.75)` looking at `(-13.92, 1.77, 6.40)` reads it right-side up & unmirrored! Use EXACT 4 corner coordinates:
     `p0 = (-13.70, 1.785, 6.62)` `uv0=(0.0, 0.0)`
     `p1 = (-13.70, 1.785, 6.20)` `uv1=(1.0, 0.0)`
     `p2 = (-14.12, 1.785, 6.20)` `uv2=(1.0, 1.0)`
     `p3 = (-14.12, 1.785, 6.62)` `uv3=(0.0, 1.0)`
     Call `card.add_tri_raw(p0, p1, p2, uv0, uv1, uv2)` and `card.add_tri_raw(p0, p2, p3, uv0, uv2, uv3)`.
   - Add a sleek small volcanic charcoal stone paperweight (`add_sphere` at `(-13.86, 1.82, 5.65)`) and slender brass letter opener (`add_cylinder` on the tray).
3. **Collector Architectural Plinth & Bronze Arp Sculpture** (`X=13.5, Z=-9.6, Y=0..3.6`):
   - Travertine monolith pedestal (`1.2x1.35x1.2` centered at `13.5, 0.675, -9.6`) topped by a fluid patinated bronze abstract loop sculpture (`add_curved_tube` + sculpted spheres in `mats["bronze_dark"]`).
4. **Right-Front Unglazed Ceramic Amphora Urn + Sculptural Olive Branches** (`X=13.3, Z=8.6, Y=0..4.8`):
   - Lathe ceramic amphora vase (`mats["plaster"]`, height `1.45`) with delicate organic olive trunks & muted foliage cluster (`olive_leaf`, `olive_leaf_bright`).
5. **Staircase Wall Recessed Gallery Shelf (`X=-13.8, Z=10.6..13.8, Y=2.4..5.2`)**:
   - Two minimal dark bronze floating shelves on the left stairwell wall holding stacked flat linen-bound art monographs (`cream_pillow`, `charcoal`, `cognac_suede`) and a tiny matte stoneware vase!

Stay within `X in [-14.98, 14.75], Y in [0.0, 6.2], Z in [-11.5, 14.5]`.""",
        "verify_cmd": make_verify(
            "build_entry_and_niches",
            "mod_entry_and_niches",
            "assert -15.05 <= min(xs) and max(xs) <= 14.90 and -0.05 <= min(ys) and max(ys) <= 6.5 and -12.0 <= min(zs) and max(zs) <= 14.8, f'Bounds: x=({min(xs):.2f},{max(xs):.2f}) y=({min(ys):.2f},{max(ys):.2f}) z=({min(zs):.2f},{max(zs):.2f})'",
            req_meshes=["EntryPatronCard"],
        ),
    },
    {
        "name": "mod_salon_seating_v2",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_salon_seating.py",
        "check_tacky_copy": True,
        "system": COMMON_SYS,
        "prompt": """Rewrite `scripts/penthouse_kit/mod_salon_seating.py` with `build_salon_seating(ctx, mats)` to achieve an **AD100 Belgian / Malibu organic quiet-luxury salon** (fixing stiff boxed shapes and repetitive red square pillows!):
Required `mats` keys: `rug`, `boucle`, `walnut_solid`, `travertine`, `brass`, `bronze_dark`, `burgundy`, `cognac_suede`, `cream_pillow`.
Strict spatial envelope (`Y floor = 0.00`):
1. **Borderless Hand-Knotted Alpaca Rug (`ctx.mb("SalonRug", mats["rug"])`)**:
   - `add_rounded_box(cx=3.2, cy=0.02, cz=-0.2, sx=11.8, sy=0.04, sz=13.2, bevel=0.015, uv_tile=5.5)`.
2. **Low-Slung Organic Camaleonda / Cloud Modular Bouclé Sofa (`X in [-1.8, 5.2], Z in [-6.8, 0.6], Y in [0, 2.4]`)**:
   - Deep recessed smoked walnut plinth (`Y=0.04..0.24`).
   - Plump chamfered pillowed seat modules (`Y=0.24..1.08`, gently rounded cushions with soft segmented bolster tufts across the back + L-chaise wing at `X=-1.0`, `Z=-2.6..0.5`), sculpted rounded wraparound back (`Y=1.08..2.12`) — softer, lower, and more organic!
   - **ONLY 3 Asymmetrical Pebble & Cloud Throw Pillows** (NO 5 stiff identical red squares!):
     - 1 tilted cognac nubuck pebble bolster (`mats["cognac_suede"]`, rounded ellipsoid/capsule around `(0.2, 1.48, -5.1)`),
     - 1 soft cream/ivory linen bolster (`mats["cream_pillow"]`, around `(3.9, 1.45, -5.2)`),
     - 1 muted oxblood cashmere cushion tucked casually into the L-corner (`mats["burgundy"]`, around `(-0.3, 1.46, -1.6)`).
   - IMPORTANT: Leave `(X in [-0.5, 4.2], Z in [1.4, 5.8])` 100% open & flat on the rug so Bruce walks and rolls freely!
3. **Pierre Jeanneret-Inspired Sculpted Walnut & Bouclé Lounge Chair** (`X=7.2, Z=-6.0`, angled toward the center):
   - Angled solid walnut V-frame side legs + plump chamfered bouclé seat/back cushion (`mats["boucle"]`) + small Roman travertine drum table at `(9.1, 0.04, -5.2)`.
4. **Twin Sculptural Honed Travertine & Bronze Plinth Coffee Tables** (`X=4.2, Z=-1.6`):
   - Low oval/capsule honed travertine slab (`Y=0.04..0.88`) on two wide curved fluted travertine drums;
   - Overlapping higher dark-bronze & cream marble cocktail table (`X=5.9, Z=-2.4`, `Y=0.04..1.14`) styled subtly with two linen-bound exhibition monographs (`cream_pillow`, `cognac_suede`) and a low shallow stoneware bowl (`add_lathe`).

All geometry MUST stay inside `X in [-3.0, 10.6], Y in [0.0, 3.8], Z in [-7.6, 7.0]`.""",
        "verify_cmd": make_verify(
            "build_salon_seating",
            "mod_salon_seating",
            "assert -3.2 <= min(xs) and max(xs) <= 10.8 and -0.05 <= min(ys) and max(ys) <= 4.0 and -7.8 <= min(zs) and max(zs) <= 7.2, f'Bounds: x=({min(xs):.2f},{max(xs):.2f}) y=({min(ys):.2f},{max(ys):.2f}) z=({min(zs):.2f},{max(zs):.2f})'",
        ),
    },
]

if __name__ == "__main__":
    os.chdir(REPO_ROOT)
    run_parallel_codegen(TASKS, batch_name="luxury_v2_3d_modules", max_workers=2, max_retries=3)
