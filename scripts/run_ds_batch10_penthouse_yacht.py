#!/usr/bin/env python3
"""
Batch 10 (Away-From-Keyboard Visual & Architectural Polish):
Parallel DeepSeek orchestration for:
1. Sculpted pinch-corner piped designer cushions helper (`cushion_helper.py`)
2. Salon L-sofa cushions & high-contrast smoked-stone table + Evian bottles (`mod_salon_seating.py`)
3. Ergonomic curved round single lounge chairs on Sunset Terrace (`mod_terrace_sky.py`)
4. Open 2F stair landing + true pitched dual glass/walnut handrails (`mod_stair_balustrade.py`)
5. Razor-smooth monotone-spline Corinthian hull & Burma teak rails (`job_hull_rig.py`)
6. Superyacht-club Burma teak & travertine floating pier with bronze cables (`job_berth.py`)
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from ds_worker import run_parallel_codegen


PENTHOUSE_PRIM = """
EXACT prim_lib.py SceneContext / MeshBuilder methods:
- b = ctx.mb(mesh_name: str, mat_idx: int)
- b.add_tri_raw(p0, p1, p2, uv0=(0,0), uv1=(1,0), uv2=(1,1), n0=None, n1=None, n2=None)
- b.add_quad(p0, p1, p2, p3, uv_scale=(1.0, 1.0), flip=False)
- b.add_box(cx, cy, cz, sx, sy, sz, uv_tile=0.0, rot_y=0.0)
- b.add_rounded_box(cx, cy, cz, sx, sy, sz, bevel=0.06, uv_tile=0.0, rot_y=0.0)
- b.add_cylinder(cx, y0, cz, r_bot, r_top, height, segs=18, rot_x=0.0, rot_z=0.0, cap_top=True, cap_bot=True)
- b.add_sphere(cx, cy, cz, rx, ry=None, rz=None, rings=12, segs=18)
- b.add_lathe(cx, y0, cz, profile, segs=22)
- b.add_curved_tube(spine_pts, radii, segs=10)
Available mats keys:
  oak, marmorino, marble, smoked_stone, walnut_fluted, walnut_solid, brass, bronze_dark, chrome,
  warm_led, warm_bulb, glass, frosted_glass, sheer_linen, boucle, travertine, rug, rug_2f,
  burgundy, cognac_suede, cream_pillow, charcoal, ceramic_white, bark, olive_leaf, olive_leaf_bright,
  headland_rock, horizon_ocean, sail_canvas, sky_sunny, evian_flint_glass, evian_label, evian_cap,
  water_meniscus, crystal_glass, concierge_screen
"""


YACHT_PRIM = """
EXACT yacht_kit/yacht_prim_lib.py YachtGLBBuilder / YachtMesh methods:
- gb = YachtGLBBuilder("asset_id")
- gb.add_pbr_material(name, base_bytes=..., base_mime=..., orm_bytes=..., normal_bytes=..., base_factor=(1,1,1,1), roughness=1.0, metalness=0.0, clearcoat=0.0, clearcoat_roughness=0.0, emissive=(0,0,0), double_sided=False)
- m = gb.mesh(mat_idx, "mesh_name")  # IMPORTANT: ONE mesh per material_idx in YachtGLBBuilder! Call gb.mesh once per material or reuse the returned YachtMesh.
- m.add_quad(p0, p1, p2, p3, uv0=(0,0), uv1=(1,0), uv2=(1,1), uv3=(0,1), flip=False)
- m.add_box(center, size, uv_tile=(1.0, 1.0), rot_y=0.0)
- m.add_chamfer_box(center, size, bevel=0.004, uv_tile=1.0, rot_y=0.0)
- m.add_tube(p0, p1, r0, r1=None, segs=16, cap=True, uv_scale=(1.0, 1.0))
- m.add_grid(pos_grid, uv_grid, flip=False, smooth_normals=True, seam_u=False)
- gb.add_anchor(name, (x, y, z))
"""


def main():
    tasks = [
        {
            "name": "cushion_helper",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/cushion_helper.py",
            "system": (
                "You are a luxury furniture 3D mesh sculptor. Build tactile, organic upholstered pillows "
                "with pinched corners, soft center loft, karate-chop upper dimple, and continuous perimeter welting piping. "
                "Keep clean, under 125 lines."
            ),
            "prompt": """Create `scripts/penthouse_kit/cushion_helper.py` exporting:
`def add_designer_pillow(b_body, b_pipe, cx, cy, cz, w=0.52, h=0.46, thick=0.16, yaw=0.0, tilt=-0.22):`

Requirements:
- Works with ANY MeshBuilder `b_body`, `b_pipe` exposing ONLY:
  `add_tri_raw(p0, p1, p2, uv0, uv1, uv2, n0=None, n1=None, n2=None)` and `add_curved_tube(spine_pts, radii, segs=8)`.
- Construct front and back `(13 x 13)` vertex grids parameterized by `u, v in [-1, 1]`:
  - Organic square silhouette with subtle **pinched corners**:
    `rx = u * (w * 0.5) * (1.0 + 0.14 * (u*u) * (v*v))`
    `ry = v * (h * 0.5) * (1.0 + 0.14 * (u*u) * (v*v)) - 0.055 * h * math.exp(-((u*2.4)**2)) * max(0.0, v - 0.35)` (soft tailored karate-chop top dimple!)
  - Plump curved thickness profile tapering cleanly to a pinched seam along edges:
    `bulge = math.cos(u * math.pi * 0.5) ** 0.72 * math.cos(v * math.pi * 0.5) ** 0.72`
    `rz_front = +(thick * 0.5) * bulge` and `rz_back = -(thick * 0.5) * bulge` (joined seamlessly around boundary where bulge=0!).
  - Apply pitch rotation `tilt` around local X (`y' = ry*ct - rz*st, z' = ry*st + rz*ct`), then Y rotation `yaw` (`wx = cx + rx*cy_y + z'*sy_y, wz = cz - rx*sy_y + z'*cy_y, wy = cy + y'`).
  - Emit outward CCW triangles on both front (`+Z` local) and back (`-Z` local) faces using `add_tri_raw` with analytic finite-difference smooth normals!
  - If `b_pipe is not None`, trace a closed loop of ~28 perimeter points along the pillow seam (`u,v` boundary) and call `b_pipe.add_curved_tube(pts, [0.008]*len(pts), segs=6)` for tailored piping!
Return ONLY valid Python code (< 125 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/cushion_helper.py', doraise=True); "
                "from scripts.penthouse_kit.prim_lib import SceneContext; "
                "from scripts.penthouse_kit.cushion_helper import add_designer_pillow; "
                "ctx=SceneContext(); b1=ctx.mb('p',0); b2=ctx.mb('w',1); "
                "add_designer_pillow(b1, b2, 0,0,0); assert len(b1.indices)>300 and len(b2.indices)>100; print('OK cushion_helper')\""
            ),
        },
        {
            "name": "mod_stair_balustrade",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_stair_balustrade.py",
            "system": (
                "You are an architectural staircase engineer for AD100 duplex interiors. Enforce clean structural continuity, "
                "OPEN landing walkthroughs (NEVER block the top landing of stairs!), dual sloped handrails, and true pitched glass panels. "
                "Keep under 220 lines."
            ),
            "prompt": f"""Rewrite `scripts/penthouse_kit/mod_stair_balustrade.py` defining `build_stair_and_balustrade(ctx, mats)`.
{PENTHOUSE_PRIM}
Exact coordinates & critical bug fixes:
1. Stair run spans `X in [-11.4, -8.2]` (`x_center = -9.8`, width `3.20`), `Z_bottom = 14.2` (`Y = 0.0`) UP to `Z_top = 6.6` (`Y = 9.20`).
   - Build 14 thick rounded oak treads (`mats["oak"]`, bevel=0.04, width=3.20, depth=0.86, thick=0.20), each with a front brushed-brass inlay (`mats["brass"]`) and under-nosing warm LED strip (`mats["warm_led"]`).
   - Build **twin TRUE pitched sloped stringer beams** (using diagonal prism quads via `add_quad` from `(Z=14.1, Y=0.05)` to `(Z=6.55, Y=9.05)` at `X = -11.25` and `-8.35`, depth `0.24`, width `0.16`, `mats["walnut_solid"]`), NOT ugly vertical boxes!
2. **DUAL-SIDE PITCHED GLASS GUARDS & CONTINUOUS SMOOTH CURVED WALNUT+BRASS HANDRAILS (`X = -11.42` AND `X = -8.18`)**:
   - On BOTH sides (`X = -11.42` and `X = -8.18`):
     - Build **TRUE sloped parallelogram glass guard panels** using `add_quad` (two faces slightly separated or double-sided glass box/strip following exact stair angle: bottom line `(Z=14.0, Y=0.35)->(Z=6.62, Y=9.25)` to top rail `(Z=14.0, Y=1.42)->(Z=6.62, Y=10.28)`), NOT stepped boxes!
     - Build 6 slim brushed-brass stanchions along each side from tread height up to top cap.
     - Build **continuous circular ergonomic walnut handrails** (`add_curved_tube`, `r = 0.036`, `mats["walnut_solid"]`) supported on brass brackets (`mats["brass"]`) along `(Z=14.35, Y=0.98) -> (Z=14.0, Y=1.42) -> (Z=6.62, Y=10.28) -> (Z=6.10, Y=10.28)`, forming a graceful horizontal entry/exit gooseneck!
3. **2F MEZZANINE BALUSTRADE — WIDE OPEN STAIR LANDING (`X in [-11.45, -8.15]`, NO BLOCKING WALL AT TOP!)**:
   - Mezzanine floor slab ends at `Z = 6.60`, `Y_base = 9.20`, and standard `1.08 m` architectural balustrade cap sits at `Y_cap = 10.28`.
   - Build East overlook balustrade along `X = -3.42, Z in [-15.8, +6.62]`.
   - Split South overlook balustrade (`Z = 6.62`) into TWO separated runs leaving the **`3.30 m` stair landing (`X in [-11.45, -8.15]`) 100% OPEN & UNOBSTRUCTED**:
     - Left wing: `X in [-14.85, -11.45], Z = 6.62`
     - Right wing: `X in [-8.15, -3.42], Z = 6.62`
   - Each run has walnut shoe base, clear tempered glass panel (`mats["glass"]`), slim brass stanchions, and continuous curved walnut/brass cap rail (`Y = 10.28`).
Return ONLY valid Python code (< 220 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_stair_balustrade.py', doraise=True); "
                "from scripts.penthouse_kit.prim_lib import SceneContext; "
                "from scripts.penthouse_kit.mod_stair_balustrade import build_stair_and_balustrade; "
                "ctx=SceneContext(); mats={k:ctx.color_mat(k,(0.5,0.5,0.5,1)) for k in ['oak','walnut_solid','brass','warm_led','glass']}; "
                "build_stair_and_balustrade(ctx, mats); assert len(ctx.builders)>=6; print('OK stair')\""
            ),
        },
        {
            "name": "mod_salon_seating",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_salon_seating.py",
            "system": (
                "You are an AD100 furniture & prop technical artist. Focus on refined tactile detail: pinched-corner piped cushions, "
                "rich dark smoked-stone tabletops with walnut edge framing so clear glass Evian bottles and tumblers stand out clearly. Keep under 190 lines."
            ),
            "prompt": f"""Rewrite `scripts/penthouse_kit/mod_salon_seating.py` defining `build_salon_seating(ctx, mats)`.
{PENTHOUSE_PRIM}
Import and use `from penthouse_kit.cushion_helper import add_designer_pillow`!

Exact layout & upgrades:
1. Keep `SalonRug` (`mats["rug"]`, centered `(0.8, 0.02, -0.3)`, size `13.8 x 0.04 x 13.6`) & `SalonRugFringe`, and `SofaPlinth`, `SofaSeat`, `SofaBack` (`-1.0, 0.42, -3.7` + chaise `-3.35, 0.42, -2.55`) & `JeanneretLoungeChair` (`-4.55, ..., -1.55`).
2. **NO ELLIPSOID/BOXY PILLOWS**: Replace `SofaPillows` & `SofaPillowsAccent` with 7 sculpted piped designer cushions via `add_designer_pillow`:
   - Place natural layered cushions along backrest `Z ~ -3.95`: alternating `cream_pillow` (`w=0.54, h=0.46, thick=0.17`), `cognac_suede` (`w=0.50, h=0.44, thick=0.16`), and `#652C39` `burgundy` (`w=0.44, h=0.38, thick=0.15`) at subtle relaxed angles (`yaw = -0.18..+0.25, tilt = -0.24..-0.32`), with `brass` / `cream_pillow` welting piping!
   - Also place one `burgundy` piped lumbar cushion against the left sofa wing (`X=-3.82, Y=0.72, Z=-2.55, yaw=1.45`) and one small tailored pillow on `JeanneretLoungeChair`.
3. **HIGH-CONTRAST SMOKED-STONE TABLE + SADDLE-LEATHER EVIAN TRAY (`Table A`)**:
   - Table A centered at `(1.15, 0.72, -2.05)`: travertine drum pedestals (`X=0.35, 1.95`) + brass collars + **solid walnut beveled outer gallery frame (`2.50 x 0.075 x 1.38`, top `Y=0.758`) cradling an inset dark Emperador `mats["smoked_stone"]` slab (`2.34 x 0.08 x 1.22`, top `Y=0.762`)** — NEVER a bright white slab!
   - Keep `Table B` at `(3.10, 0.72, -1.18)` with `ConciergePager1F` and `ConciergeScreen1F` facing forward `+Z` (`add_tri_raw` tilted OLED screen).
   - On Table A (`Y = 0.762`), place `SalonMonographs` (`X=0.35, Z=-2.15`), `SalonStonewareBowl` (`X=1.92, Z=-2.25`), and a **Saddle-Leather & Brushed-Brass Serving Tray** centered at `(1.10, 0.762, -1.92)` (`cognac_suede` tray bed `0.66 x 0.02 x 0.44` + `brass` perimeter rail frame — high contrast dark cognac against Evian glass!).
   - Inside the tray stand 3 tall sculpted `EvianBottles1F` (`mats["evian_flint_glass"]`, `bx in (0.90, 1.10, 1.30), Z=-1.94`, cylindrical body + tapered shoulder + neck `total h=0.32`, topped with `evian_cap` rose-silver cap + inner `water_meniscus` glow cylinder + crisp `EvianLabels1F`) AND 2 faceted `SalonTumblers` (`tx in (0.98, 1.22), Z=-1.78`) with aqua water fills!
Return ONLY valid Python code (< 190 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_salon_seating.py', doraise=True); "
                "import sys; sys.path.insert(0,'scripts'); "
                "from penthouse_kit.prim_lib import SceneContext; from penthouse_kit.mod_salon_seating import build_salon_seating; "
                "ctx=SceneContext(); ks=['rug','cream_pillow','walnut_solid','boucle','burgundy','cognac_suede','travertine','brass','smoked_stone','bronze_dark','walnut_fluted','sheer_linen','ceramic_white','evian_flint_glass','evian_label','evian_cap','water_meniscus','crystal_glass','charcoal','concierge_screen']; "
                "mats={k:ctx.color_mat(k,(0.5,0.5,0.5,1)) for k in ks}; build_salon_seating(ctx, mats); "
                "names=[k[0] for k in ctx.builders]; assert 'TerraceSofaSeat' not in names and 'EvianBottles1F' in names and 'ConciergePager1F' in names; print('OK salon')\""
            ),
        },
        {
            "name": "mod_terrace_sky",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_terrace_sky.py",
            "system": (
                "You are an AD100 outdoor pavilion & coastal vista architect. Build ergonomic round barrel lounge chairs "
                "with curved steam-bent teak shells, dished round bouclé seat cushions, curved channel-tufted wrap backrests, "
                "and authentic Mediterranean parallax sea vista. Keep under 235 lines."
            ),
            "prompt": f"""Rewrite `scripts/penthouse_kit/mod_terrace_sky.py` defining `build_terrace_and_sky(ctx, mats)`.
{PENTHOUSE_PRIM}
Import `from penthouse_kit.cushion_helper import add_designer_pillow`!

Exact coordinates & required upgrades:
1. Keep `TerraceDeck` (`travertine`, `0.0, -0.10, -22.8, 32.4 x 0.20 x 13.6` + coping), `TerraceGlass`, `TerraceHandrail` (`brass`), `TerracePosts` (`bronze_dark`), `TerraceOutdoorRug` (`rug_2f` at `(1.4, 0.015, -22.6), 6.2 x 0.03 x 4.8`).
2. **REPLACE RECTANGULAR TERRACE SOFA WITH TWO ERGONOMIC CURVED ROUND SINGLE LOUNGE CHAIRS**:
   - Build a helper `add_ergonomic_round_chair(cx, cz, face_yaw)` constructing:
     - Brushed bronze recessed swivel pedestal (`mats["bronze_dark"]`, `r=0.48, y=0.03..0.11`),
     - **Curved 240° steam-bent solid teak/walnut barrel shell** (`TerraceSofaTeak`, `mats["walnut_solid"]`) composed of 28 curved vertical/tapered segments sweeping `theta` around `face_yaw + math.pi` (leaving front opening toward `face_yaw` open for easy lounging!), rising smoothly in ergonomic profile from armrest `Y=0.52` at `±120°` to lumbar crown `Y=0.88` at rear `180°`! Radius `R_out=0.72, R_in=0.64`.
     - **Ergonomically dished round oatmeal bouclé seat cushion** (`TerraceSofaSeat`, `mats["boucle"]`, sculpted `add_lathe` profile centered at `(cx, 0.14, cz)` with outer rim `r=0.62, Y=0.45` gently dished toward center `Y=0.41` + piped edge) + **Curved ergonomic inner bouclé wrap-around backrest cushion** (`220°` contoured ring lining interior shell from `Y=0.42..0.83`, reclining gently `8°` backward for true human ergonomics!)!
     - One sculpted pinched-corner accent pillow via `add_designer_pillow` (`cognac_suede` on Chair 1, `burgundy` on Chair 2).
   - Place **Chair 1 (Bruce's Lounge Chair)** at `(0.38, -22.35)` facing sunset-forward (`face_yaw = math.pi * 0.92`) and **Chair 2 (Owner's Companion Chair)** at `(2.52, -22.30)` facing `(face_yaw = -math.pi * 0.88)`.
   - Place a **Central Fluted-Walnut & Roman Travertine Round Drum Side Table** between them at `(1.45, 0.0, -22.95)` (`r=0.44, top Y=0.49`) with 2 crystal sunset glasses, plus a matching **Round Travertine & Bouclé Ottoman** at `(2.38, 0.0, -23.75)`!
3. Keep `TerraceLantern_*` (`-1.45` and `4.25`), the two sculpted `OlivePlanter/Trunk/Foliage` olive trees (`(-12.2, -23.5)` & `(12.4, -24.2)`), `CoastalCliff`, `CoastalHeadlands` (smooth coastal capes without harsh pyramids), `OceanVistaWater` (`horizon_ocean`, `+Y` normal), 2 `Sailboat*` craft (`(-14, -74)` and `(22, -102)`), and `SkyCyclorama` (`mats["sky_sunny"]`, radius `148.0`, continuous U `0..1` across `theta_min=-2.65..2.65`, `y_bot=-26, y_top=76`).
Ensure required mesh names exist: `TerraceSofaSeat`, `OceanVistaWater`, `SkyCyclorama`. Return ONLY valid Python code (< 235 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_terrace_sky.py', doraise=True); "
                "import sys; sys.path.insert(0,'scripts'); "
                "from penthouse_kit.prim_lib import SceneContext; from penthouse_kit.mod_terrace_sky import build_terrace_and_sky; "
                "ctx=SceneContext(); ks=['travertine','glass','brass','bronze_dark','rug_2f','walnut_solid','walnut_fluted','boucle','cognac_suede','burgundy','cream_pillow','crystal_glass','warm_bulb','bark','olive_leaf','olive_leaf_bright','headland_rock','horizon_ocean','sail_canvas','sky_sunny']; "
                "mats={k:ctx.color_mat(k,(0.5,0.5,0.5,1)) for k in ks}; build_terrace_and_sky(ctx, mats); "
                "names=[k[0] for k in ctx.builders]; assert 'TerraceSofaSeat' in names and 'OceanVistaWater' in names and 'SkyCyclorama' in names; print('OK terrace_sky')\""
            ),
        },
        {
            "name": "job_hull_rig",
            "model": "deepseek-chat",
            "out_path": "scripts/yacht_kit/job_hull_rig.py",
            "system": (
                "You are a naval architect & marine yacht glTF engineer modeling a 20m Orient Express Corinthian inspired day-sailer. "
                "Enforce fair PCHIP monotone cubic hull lines (ZERO waviness), recessed enclosed stern steps, Burma teak toe-rails, "
                "tapered stanchions with double bronze lifelines + teak cap rail, and strict GLB AABB & anchor compliance. Keep under 235 lines."
            ),
            "prompt": f"""Rewrite `scripts/yacht_kit/job_hull_rig.py` producing `assets/models/yacht_hull_rig.glb`.
{YACHT_PRIM}
Import bundles identically: `hb = load_bundle("hull_satin")`, `tb = load_bundle("teak_deck")`, `tf = load_bundle("teak_frame")`, `pb = load_bundle("pvd_brushed")`, `sb = load_bundle("sail_coated")`.
Add material `teak_rail = gb.add_pbr_material("teak_rail", base_bytes=tf["base_bytes"], base_mime=tf["base_mime"], orm_bytes=tf["orm_bytes"], normal_bytes=tf["norm_bytes"], roughness=0.45, clearcoat=0.14)` alongside `hull_mat`, `teak`, `pvd`, `sail_mat`, `win_glass`.

CRITICAL NAVAL ARCHITECTURE & VALIDATION CONTRACTS:
1. **Fair Monotone PCHIP Half-Breadth & Sheerline (ZERO wavy humps!)**:
   - Implement a small pure-Python Fritsch-Carlson monotone cubic spline helper `pchip_eval(xs, ys, x)` over:
     - `CP = [(-10.0, 1.24), (-7.8, 1.84), (-3.0, 2.38), (2.0, 2.38), (5.5, 1.94), (8.2, 1.02), (10.0, 0.0)]` (guaranteed smooth, monotonic taper with zero overshoot > 2.39!).
     - Sheerline `SH = [(-10.0, 1.20), (-6.0, 1.24), (0.0, 1.32), (5.5, 1.44), (10.0, 1.62)]` -> smooth sweep!
   - Hull cross-section `hull_hw(z, y)` includes graceful **bow flare** (`+0.03*max(0,z-3)/7` clamped strictly `<= 2.39`) and smooth **rounded bilge curve** down to bottom keel seam (`y=-0.58`) + cutwater stem `z_stem = 9.52 + 0.46 * clamp(y/1.62, -0.35, 1.0)`.
   - Loft hull shell with high smoothness (`NZ = 84, NY = 24`, `smooth_normals=True`) + flat sealed bottom keel plate + enclosed **port & starboard transom quarter bulwarks** (`|X| in [1.06, hw(z)]` for `z in [-10.0, -8.0]`) + bulb fin keel down to `Y = -1.62` (strictly inside `Y >= -1.65`!).
2. **Main Teak Deck & Champagne Toe-Rail**:
   - Loft `deck` (`ND = 64`, `flip=True` `+Y` normal, `uv` mapped cleanly to `0.640 x 2.56m` planks) + sculpted **Burma Teak & PVD Toe-Rail / Gunwale Cap** tracing both sides along `hw(z) - 0.035`.
   - Keep `stripe` (`Y = 0.15 ± 0.021` PVD waterline stripe hugging `hull_hw(z, 0.15) + 0.004`), `windows` (`Z in [-5.8, 5.6], Y in [0.78, 0.95]`), `foredeck` plinth `(0, 1.56, 7.70)`.
3. **Enclosed Recessed Transom Swim Platform & Steps (`|X| <= 1.06`)**:
   - Solid enclosed riser steps descending smoothly from main aft deck (`z=-8.19, y=1.20`) down (`-8.45, 0.98`, `-8.71, 0.77`, `-8.97, 0.55`) to swim platform (`y=0.32, z=-9.55`), flanked by hull cheek walls & PVD stair trim!
4. **Superyacht Stanchion Rails + Lifelines + Teak Top Rail**:
   - Along both sides (leaving gangway opening `-5.75..-4.65` open on port `side=-1`): tapered PVD stanchions (`r=0.016->0.011, H=0.68`) every `~1.3m`, **2 taut thin PVD bronze lifelines (`r=0.005` at `+0.25H` & `+0.50H`)**, and a **smooth curved Burma teak top handrail (`r=0.021`, `teak_rail`)** + curved bow pulpit!
5. **Keep Mast (`(0,1.33,2.55)->(0,18.00,2.55)`), Boom, 6 SolidSail Panels (lower 3 folded 42°), & EXACT 5 Anchors**:
   - `yacht_root (0,0,0)`, `gangway_yacht (-2.26,1.29,-5.20)`, `aft_cleat (1.52,1.26,-8.55)`, `dog_bow (0,1.58,7.70)`, `salon_mount (0,1.30,0)`.
   - Export `OUT = .../assets/models/yacht_hull_rig.glb` and verify EVERY vertex is strictly inside `[-2.395, -1.645, -9.995]..[2.395, 17.995, 9.995]`!
Return ONLY valid Python code (< 235 lines).""",
            "verify_cmd": (
                "python3 scripts/yacht_kit/job_hull_rig.py && "
                "python3 scripts/yacht_kit/validate_glb.py --job hull_rig"
            ),
        },
        {
            "name": "job_berth",
            "model": "deepseek-chat",
            "out_path": "scripts/yacht_kit/job_berth.py",
            "system": (
                "You are a Monaco superyacht harbour architect. Upgrade a floating pier with honed Roman travertine coping curbs, "
                "quarter-sawn Burma teak decking, architectural bronze cable promenade railings & warm amber pier bollards—ZERO chunky "
                "chimney-pipe pilings through the deck. Must pass strict GLB validator AABB! Keep under 165 lines."
            ),
            "prompt": f"""Rewrite `scripts/yacht_kit/job_berth.py` producing `assets/models/yacht_berth.glb`.
{YACHT_PRIM}
Load bundles: `teak_b = load_bundle("teak_deck")`, `trav_b = load_bundle("filled_travertine")`, `tf_b = load_bundle("teak_frame")`, `pvd_b = load_bundle("pvd_brushed")`, `brz_b = load_bundle("bronze_brushed")`.

STRICT VALIDATOR AABB CONTRACT (EVERY vertex MUST satisfy!):
`X in [-5.54, -2.81]`, `Y in [-0.94, 1.29]`, `Z in [-11.99, +11.99]`!
Exact Anchors required: `dock_spawn (-4.20, 0.72, -10.60)` and `gangway_dock (-2.85, 0.72, -5.20)`.

Upgrades:
1. **Tailored Multi-Material Pier Deck (top `Y = 0.72`)**:
   - Central **Quarter-Sawn Burma Teak Deck** (`teak`, `X in [-5.16, -3.18], Y in [0.64, 0.72], Z in [-11.96, +11.96]`, proper plank scale `uv_tile=(0.64, 2.56)`!).
   - Outer & Inner **Honed Roman Travertine Coping Curbs** (`trav_b`, `width = 0.34`, chamfered coping slab at `X = -5.34` & `X = -3.00`, `Y in [0.64, 0.725]`) framed by **champagne-PVD edge fascia channels** (`Y in [0.58, 0.725]`).
2. **Dark Marine Pontoon Floats & Outboard Structural Pilings (BELOW DECK — zero ugly pipes blocking the walkway!)**:
   - Dark underwater floats & cross-braces (`Y in [-0.92, 0.62]`).
   - Outboard submerged pilings at `X = -5.42` (`Y in [-0.94, 0.74]`) capped neatly at deck level with slim PVD mooring caps (`Y = 0.72..0.77`, NEVER poking awkwardly to `1.26`!).
3. **Architectural Bronze & Cable Pier Promenade Railing (`X = -5.34`, `Z in [-11.6, +11.6]`, top strictly `Y = 1.28 <= 1.29`!)**:
   - 11 tapered bronze stanchions (`r=0.018->0.013`, `Y = 0.72..1.25`) at `Z = -11.4..+11.4`,
   - **3 taut champagne-PVD guard cables (`r=0.005`)** at `Y = 0.88, 1.02, 1.16`,
   - **Hand-rubbed Burma Teak top handrail (`tf_b`, bevel box/tube `0.065 x 0.036` at `Y = 1.265`)**!
4. **6 Warm `2700K` Amber Alabaster-and-Bronze Pier Light Bollards**:
   - Positioned neatly along outer curb `X = -5.34` at `Z = (-9.2, -5.4, -1.8, 1.8, 5.4, 9.2)`, `Y = 0.72..1.08`, bronze fluted shaft + warm glowing lantern cap (`emissive=(1.0, 0.78, 0.44)`).
5. **Yacht-Side Cleats & Pneumatic Fenders (`X = -2.96`)**:
   - Sleek twin-post PVD horn cleats (`Y = 0.72..0.86`) at `Z = (-9.5, -3.6, 3.2, 9.2)` + dark charcoal ribbed fenders along berth side (`X = -2.86, Y = 0.14..0.64`).
Export to `assets/models/yacht_berth.glb` and verify via `validate_glb.py`! Return ONLY valid Python code (< 165 lines).""",
            "verify_cmd": (
                "python3 scripts/yacht_kit/job_berth.py && "
                "python3 scripts/yacht_kit/validate_glb.py --job berth"
            ),
        },
    ]

    results = run_parallel_codegen(tasks, batch_name="batch10_polish", max_workers=6, max_retries=3)
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
