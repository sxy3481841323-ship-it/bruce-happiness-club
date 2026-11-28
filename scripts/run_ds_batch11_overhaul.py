#!/usr/bin/env python3
"""
Batch 11 (Aesthetic, CoastalVista, Superyacht Cockpit & Shoreline Lounge Overhaul):
Parallel DeepSeek orchestration for:
1. `scripts/penthouse_kit/tex_oldmoney_surfaces.py` (Verde Alpi, Smoked Rift Oak, Celadon Limewash, Slate Linen, seamless Tibetan wool+celadon rugs, coastal pine slopes)
2. `scripts/penthouse_kit/arch_shell.py` (Remove repetitive wavy brown pilasters; add rift oak & celadon limewash bays, Verde Alpi chimney breast)
3. `scripts/penthouse_kit/mod_salon_seating.py` (Single-UV rug quad fixing grid bug, 2+1 curated pillows, slate-linen armchair, Evian pour bottle + cap + crystal bowl)
4. `scripts/penthouse_kit/mod_terrace_sky.py` (Single-UV terrace rug, rift-oak/slate round chairs, 3-layer natural Mediterranean coastline & mist mountains)
5. `scripts/yacht_kit/job_club_lounge.py` (Waterfront Travertine Promenade, Teak+Brass Bridge, Orient-Express Lounge Pavilion & Olive Hillside -> `yacht_club_lounge.glb`)
6. `scripts/yacht_kit/job_furniture_props.py` (Curved aft transom L-banquette, oval cocktail table + champagne, plush sunbeds, bespoke oval bolster dog bed)
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from ds_worker import run_parallel_codegen


PENTHOUSE_PRIM = """
EXACT scripts/penthouse_kit/prim_lib.py SceneContext / MeshBuilder methods:
- b = ctx.mb(mesh_name: str, mat_idx: int)
- b.add_tri_raw(p0, p1, p2, uv0=(0,0), uv1=(1,0), uv2=(1,1), n0=None, n1=None, n2=None)
- b.add_quad(p0, p1, p2, p3, uv_scale=(1.0, 1.0), flip=False)  # normal is (p1-p0)x(p3-p0) unless flip=True
- b.add_box(cx, cy, cz, sx, sy, sz, uv_tile=0.0, rot_y=0.0)
- b.add_rounded_box(cx, cy, cz, sx, sy, sz, bevel=0.06, uv_tile=0.0, rot_y=0.0)
- b.add_cylinder(cx, y0, cz, r_bot, r_top, height, segs=18, rot_x=0.0, rot_z=0.0, cap_top=True, cap_bot=True)
- b.add_sphere(cx, cy, cz, rx, ry=None, rz=None, rings=12, segs=18)
- b.add_lathe(cx, y0, cz, profile, segs=22)
- b.add_curved_tube(spine_pts, radii, segs=10)
Available mats keys in build_penthouse_duplex_glb.py:
  oak, marmorino, marble, smoked_stone, verde_alpi, rift_oak, celadon_plaster, slate_linen,
  walnut_fluted, walnut_solid, brass, bronze_dark, chrome,
  warm_led, warm_bulb, glass, frosted_glass, sheer_linen, boucle, travertine, rug, rug_2f,
  burgundy, cognac_suede, cream_pillow, charcoal, ceramic_white, bark, olive_leaf, olive_leaf_bright,
  headland_rock, coastal_pine, far_mist_mountain, horizon_ocean, sail_canvas, sky_sunny,
  evian_flint_glass, evian_label, evian_cap, water_meniscus, crystal_glass, concierge_screen
"""


YACHT_PRIM = """
EXACT scripts/yacht_kit/yacht_prim_lib.py & tex_helpers.py APIs:
- from yacht_kit.yacht_prim_lib import YachtGLBBuilder
- from yacht_kit.tex_helpers import load_bundle
  # Available load_bundle keys: "hull_satin", "teak_deck", "teak_frame", "marquetry",
  #   "outdoor_linen", "saddle_leather", "saddle_leather_crest", "stitch_strip",
  #   "woven_rug", "filled_travertine", "pvd_brushed", "bronze_brushed"
  # Note: load_bundle(k) returns dict with base_bytes, base_mime, orm_bytes, norm_bytes
- gb = YachtGLBBuilder("asset_id")
- i_mat = gb.add_pbr_material(name, base_bytes=..., base_mime=..., orm_bytes=..., normal_bytes=...,
    base_factor=(1,1,1,1), roughness=1.0, metalness=0.0, clearcoat=0.0, clearcoat_roughness=0.0,
    emissive=(0,0,0), transmission=0.0, ior=1.5, double_sided=False, clamp_uv=False)
- m = gb.mesh(mat_idx, "mesh_name")  # IMPORTANT: ONE mesh per mat_idx! Call gb.mesh once per material or reuse returned YachtMesh.
- m.add_quad(p0, p1, p2, p3, uv0=(0,0), uv1=(1,0), uv2=(1,1), uv3=(0,1), flip=False)
- m.add_box(center, size, uv_tile=(1.0, 1.0), rot_y=0.0)
- m.add_chamfer_box(center, size, bevel=0.004, uv_tile=1.0, rot_y=0.0)
- m.add_prism(poly_xz, y0, y1, uv_tile=1.0, caps=(True, True))
- m.add_tube(p0, p1, r0, r1=None, segs=16, cap=True, uv_scale=(1.0, 1.0))
- m.add_grid(pos_grid, uv_grid, flip=False, smooth_normals=True, seam_u=False)
- gb.add_anchor(name, (x, y, z))
"""


def main():
    tasks = [
        {
            "name": "tex_oldmoney_surfaces",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/tex_oldmoney_surfaces.py",
            "system": (
                "You are an AD100 architectural materials texture synthesizer using NumPy + PIL. "
                "Create refined, calm mineral-botanical quiet-luxury textures (zero harsh checker grids, "
                "zero wavy zebra wood, soft organic stone & textile shading). Keep clean under 210 lines."
            ),
            "prompt": """Rewrite `scripts/penthouse_kit/tex_oldmoney_surfaces.py` keeping ALL existing function names PLUS adding 4 new generators so callers can import all 8 functions cleanly:

1. `make_marmorino_boiserie_tex(size: int = 1024) -> Image.Image`:
   - Warm French chalk limestone (`#EAE4D8` .. `#DDD5C7`) with soft cloud trowel movement and very delicate inset panel hairline grooves (`#C3B8A6` + subtle brass highlight `#CAB996`). Avoid loud dark borders.
2. `make_handknotted_salon_rug_tex(size: int = 2048) -> Image.Image`:
   - **NO BROWN GRID!** Designed for 1:1 non-tiled carpet mapping.
   - Cloud-washed undyed Tibetan wool & celadon-silk field: soft organic FBM + horizontal subtle silk abrash bands blending `#E7E1D6`, `#D8D1C4`, and muted sage-celadon wisps `#C6CFC6`.
   - Frame ONLY the extreme perimeter with a single refined architectural border: thin muted taupe-olive trim band `outer = int(n * 0.04)` in `#7B7D72`, delicate antique brass `2px` hairline (`#B59A6B`), and a `2px` oxblood `#652C39` inner hairline. Keep the center `91%` serene, cloud-washed, and grid-free.
3. `make_loft_aubusson_rug_tex(size: int = 1024) -> Image.Image`:
   - Harmonized warm oatmeal `#E2DDD2` & muted celadon-stone `#CFD5CB` woven boucle field with thin outer olive-slate border (`int(n * 0.038)`, `#74796F`) + brass pinhole line (`#B59A6B`). Clean non-repetitive luxury look.
4. `make_verde_alpi_marble_tex(size: int = 1024) -> Image.Image`:
   - Deep botanical forest-green Italian Alpine honed marble (`#293D34`, `#1D2C25`, `#364D43`), veined with organic domain-warped FBM diagonal alabaster-ivory rivers (`#E6E1D6`) and hairline antique-ochre mineral traces (`#9E8658`).
5. `make_rift_oak_tex(size: int = 1024) -> Image.Image`:
   - **Straight-grained Smoked Rift-Cut European Oak** (`#7C654E` .. `#66513C`): crisp FINE VERTICAL wood pores along Y (`x`-frequency cathedrals stretched `24x` vertically with near-zero lateral wave!) + tiny warm-tan medullary grain flecks — ZERO thick sinusoidal brown waves!
6. `make_celadon_plaster_tex(size: int = 1024) -> Image.Image`:
   - Serene muted botanical sage-celadon Venetian plaster (`#C7D0C4` .. `#B4BFA9`), multi-octave mineral clouding and soft plaster patina.
7. `make_slate_linen_tex(size: int = 512) -> Image.Image`:
   - Coastal Slate-Mist Belgian linen (`#5C6F7C` .. `#4B5C68`), crisp micro cross-warp/weft slub weave (`sin(x)`/`sin(y)` subtle fiber variance).
8. `make_headland_rock_tex(size: int = 512) -> Image.Image` AND `make_coastal_pine_slope_tex(size: int = 1024) -> Image.Image`:
   - `make_headland_rock_tex`: Sun-warmed pale Mediterranean limestone bluff (`#9D9283` .. `#7A7166`) with delicate organic strata and lichen moss (`#676E5F`), ZERO dark brown zebra stripes!
   - `make_coastal_pine_slope_tex`: Lush muted Mediterranean umbrella-pine & olive hillside (`#4B614E`, `#637760`, `#3A4D3E`) speckled with pale sun-dappled foliage clusters and warm limestone outcrop hints (`#998E7E`) along lower base.

Return ONLY valid Python code (< 220 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/tex_oldmoney_surfaces.py', doraise=True); "
                "import sys; sys.path.insert(0,'scripts'); "
                "from penthouse_kit.tex_oldmoney_surfaces import (make_marmorino_boiserie_tex, make_handknotted_salon_rug_tex, "
                "make_loft_aubusson_rug_tex, make_verde_alpi_marble_tex, make_rift_oak_tex, make_celadon_plaster_tex, "
                "make_slate_linen_tex, make_headland_rock_tex, make_coastal_pine_slope_tex); "
                "assert make_verde_alpi_marble_tex(128).size==(128,128) and make_rift_oak_tex(128).size==(128,128) "
                "and make_celadon_plaster_tex(128).size==(128,128) and make_slate_linen_tex(128).size==(128,128) "
                "and make_coastal_pine_slope_tex(128).size==(128,128) and make_handknotted_salon_rug_tex(256).size==(256,256); "
                "print('OK tex_oldmoney_surfaces')\""
            ),
        },
        {
            "name": "arch_shell",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/arch_shell.py",
            "system": (
                "You are an AD100 & Apple architectural minimalist duplex shell architect. "
                "Eliminate monotonous wavy brown striped pilasters; compose calm wide chalk-limestone bays accented by "
                "muted celadon mineral plaster recesses, sleek smoked rift-oak stiles, brass shadow-gap hairlines, and a dramatic Verde Alpi chimney breast. "
                "Preserve ALL opening geometry (Z=-16 terrace doorway and 2F stair landing X in [-11.45, -8.15] OPEN). Keep under 215 lines."
            ),
            "prompt": f"""Rewrite `scripts/penthouse_kit/arch_shell.py` defining `build_arch_shell(ctx, mats)`.
{PENTHOUSE_PRIM}

Exact architectural requirements (preserve all coordinates from existing shell cleanly):
1. **1F Floor & Ceiling**:
   - `FloorOak` (`mats["oak"]`, `(0.0, -0.06, -0.2, 30.4, 0.12, 32.0, uv_tile=6.0)`), `FloorBorderInlay` (`mats["rift_oak"]`, `x in (-13.6,13.6)`, `z in (-14.6,14.2)`), `FloorBrassHairline` (`mats["brass"]`).
   - `CeilingMarmorino` (`Y=18.66`), `CeilingCoveSoffit`, `WarmCoveLED` (`Y=18.02`), `ChandelierBrass` & `ChandelierGlobes` centered at `(2.6, 16.4/14.6, -2.8)`.
2. **NO MORE WAVY BROWN PILASTERS (`walnut_fluted`)!**
   - Use **`mats["rift_oak"]`** (sleek architectural flat-sawn vertical panels, max `0.42` wide, shallow `0.07` projection, spaced calmly on wide architectural modules) + thin **`mats["brass"]`** vertical trim fillets (`0.025` wide).
   - **Color Variety (Mineral + Botanical Palette)**:
     - Main walls (`RightWallMarmorino`, `LeftWallMarmorino`, `SouthWallMarmorino`) in chalk limestone `mats["marmorino"]`.
     - **Architectural inset panels & recesses (`RightCeladonBays`, `LeftRecesses`, `SouthCeladonInlays`)**: use **`mats["celadon_plaster"]`** inside tall recessed shadow-gap wall frames on Right (`z in (-12.5..-10.6, 8.2..12.2)`), Left (`z=-3.8` and `z=10.5` recesses + calm upper/lower bays), and South (`x = -11.0 + i * 4.4`, avoiding `2F` painting zone `Z in [-6.8..0.0]`).
     - **`RightChimneyBreast` (`X=14.75, Y=4.6, Z=-1.8`)**: build in deep botanical **`mats["verde_alpi"]`** (honed dark Alpine green marble!) instead of grey-white marble so the fireplace wall has museum anchor weight.
3. **Portals, Mezzanine & Openings (preserve exact working doorways)**:
   - `EntranceDoors` (`mats["rift_oak"]` at `-14.85, 3.7, 2.2, 0.18, 7.4, 2.6`) + `EntranceArchitrave` + `EntrancePulls` (`brass`); keep `KitchenPortal` at `(-14.85, 3.7, -8.8)` cleanly trimmed (`mats["frosted_glass"]` + `brass`) so West wall remains sealed until Phase 2 kitchen.
   - `GalleryCredenza` (`(3.4, 1.6, 15.1)`) in `mats["rift_oak"]` + `brass` top/plinth + curated books (`slate_linen`, `burgundy`, `cognac_suede`).
   - `MezzanineSlab` (`mats["oak"]`, `(-9.2, 9.14, -4.6, 11.6, 0.12, 22.4)`) + `MezzanineLandingTrim` (`rift_oak`, `-9.8, 9.21, 6.56, 3.30, 0.03, 0.12`) + `MezzanineLandingBrass` — DO NOT place any wall across stair landing `X in [-11.45, -8.15]`!
   - `MasterSuiteDoor` (`mats["rift_oak"]`, `-14.86, 11.4, 3.6`) + `brass`.
   - Panoramic Terrace Curtain Wall (`Z = -16.0`): `CurtainMullions` (`bronze_dark`), `ClearCurtainGlass` (open center bay `X in [-2.2, 4.6]` on 1F!), `SlidingDoorFrames`, `TerraceThreshold`, `SheerDrapery`.
Return ONLY valid Python code (< 215 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/arch_shell.py', doraise=True); "
                "import sys; sys.path.insert(0,'scripts'); "
                "from penthouse_kit.prim_lib import SceneContext; from penthouse_kit.arch_shell import build_arch_shell; "
                "ctx=SceneContext(); ks=['oak','rift_oak','brass','marmorino','warm_led','warm_bulb','verde_alpi','celadon_plaster','walnut_solid','glass','frosted_glass','burgundy','cognac_suede','slate_linen','bronze_dark','sheer_linen']; "
                "mats={k:ctx.color_mat(k,(0.5,0.5,0.5,1)) for k in ks}; build_arch_shell(ctx, mats); "
                "names=[k[0] for k in ctx.builders]; assert 'MezzanineRail' not in names and 'RightChimneyBreast' in names; print('OK arch_shell')\""
            ),
        },
        {
            "name": "mod_salon_seating",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_salon_seating.py",
            "system": (
                "You are an AD100 furniture & prop sculptor. Eliminate tiled rug grids, remove cluttered excessive sofa pillows, "
                "introduce coastal Slate-Linen accent seating & Smoked Rift Oak, and provide cleanly named separable Evian bottle, cap, and crystal bowl meshes "
                "for 3D uncapping & pouring animation. Keep under 210 lines."
            ),
            "prompt": f"""Rewrite `scripts/penthouse_kit/mod_salon_seating.py` defining `build_salon_seating(ctx, mats)`.
{PENTHOUSE_PRIM}
Import `from penthouse_kit.cushion_helper import add_designer_pillow`!

Exact layout & critical visual upgrades:
1. **SERENE SINGLE-UV SALON RUG (ZERO TILED GRID!)**:
   - Dimensions: centered `(0.8, 0.02, -0.3)`, width `13.8`, depth `13.6`. X spans `[-6.1, 7.7]`, Z spans `[-7.1, 6.5]`.
   - Build thin side/edge plinth `SalonRugPlinth` (`mats["cream_pillow"]`, `(0.8, 0.018, -0.3, 13.8, 0.036, 13.6)`), and then **`SalonRug` (`mats["rug"]`) as ONE single top quad at `Y = 0.038` with `uv_scale=(1.0, 1.0)`**:
     `b.add_quad((-6.1, 0.038, 6.5), (7.7, 0.038, 6.5), (7.7, 0.038, -7.1), (-6.1, 0.038, -7.1), uv_scale=(1.0, 1.0))`
     (Verify: `(p1-p0)=(+13.8,0,0)`, `(p3-p0)=(0,0,-13.6)` -> `+X x -Z = +Y` UPWARD! This maps the borderless cloud-washed rug 1:1 with zero interior grid lines!).
2. **Sofa & Coastal Slate Accent Armchair**:
   - `SofaPlinth` in `mats["rift_oak"]` (`(-1.0, 0.20, -3.7, 4.6, 0.40, 1.30)` + chaise `(-3.35, 0.20, -2.55, 1.30, 0.40, 2.30)`).
   - `SofaSeat` & `SofaBack` in soft cream `mats["boucle"]`.
   - `JeanneretLoungeChair` frame at `(-4.55, ..., -1.55)` in `mats["rift_oak"]`, seat & back cushions (`JeanneretCushion`, `JeanneretBackCushion`) in cool **`mats["slate_linen"]`** (breaking beige monotony!), plus 1 small `cream_pillow` lumbar!
3. **CURATED `2 + 1` PILLOW STYLING (ONLY 3 PILLOWS ON MAIN SOFA — STOP OVERCROWDING!)**:
   - Group A+B tucked casually in the corner (`SofaPillowA`: `(-3.05, 0.72, -3.92)`, `cream_pillow` + `brass` pipe, `w=0.58, h=0.48, thick=0.18, yaw=-0.42, tilt=-0.28`; `SofaPillowB`: `(-2.55, 0.69, -3.75)`, `slate_linen` + `cream_pillow` pipe, `w=0.48, h=0.42, thick=0.16, yaw=0.22, tilt=-0.30`).
   - Group C single tailored burgundy lumbar on right end (`SofaPillowC`: `(0.62, 0.68, -3.92)`, `burgundy` `#652C39` + `brass` pipe, `w=0.50, h=0.35, thick=0.15, yaw=-0.16, tilt=-0.26`).
   - NO other pillows on the main sofa! (Total = 3 on sofa + 1 on armchair).
4. **SMOKED-STONE TABLE A + SEPARABLE ANIMATABLE EVIAN POUR SET + BOWL**:
   - Table A centered at `(1.15, 0.72, -2.05)`: `TableAPedestals` (`travertine`), `TableABrassCollars` (`brass`), `TableAWalnutFrame` (`rift_oak`), `TableASmokedStone` (`smoked_stone`, top `Y=0.76`).
   - `TableB` (`(3.10, 0.72, -1.18)`) + `ConciergePager1F` + `ConciergeScreen1F` (`add_tri_raw` tilted OLED screen facing `+Z`).
   - On Table A (`Y=0.762`), place `SalonMonographs` (`0.22, -2.18`), `SalonStonewareBowl` (`1.96, -2.26`), and a **Saddle-Leather & Brass Serving Tray (`TableATrayLeather`, `TableATrayBrass`)** centered at `(1.16, 0.762, -1.96)` (`0.84 x 0.02 x 0.48`, tray surface `Y=0.78`).
   - On the tray (`Y = 0.78`), place:
     a) **Reserve sealed Evian bottle (`EvianBottles1F` + `EvianCapsReserve1F` + `EvianLabelsReserve1F`)** at `(0.90, 0.78, -2.06)` (radius `0.044`, body `h=0.21`, tapered shoulder to neck `r=0.018`, total `h=0.32`).
     b) **Animatable Interactive Pour Bottle (`EvianPourBottle1F` + `EvianPourLabel1F` + `EvianPourCap1F`)** centered at `(1.15, 0.78, -1.96)`:
        - `EvianPourBottle1F` (`mats["evian_flint_glass"]`): lathe body + shoulder + open pour spout up to `Y=0.78+0.32=1.10`.
        - `EvianPourLabel1F` (`mats["evian_label"]`): thin cylinder wrap around `Y=0.84..0.95`.
        - `EvianPourCap1F` (`mats["evian_cap"]`): screw-cap seated on spout (`Y=1.095..1.125`, centered `(1.15, 1.095, -1.96)`).
     c) **Crystal Pet Tasting Bowl (`CrystalWaterBowl1F` + `CrystalBowlWater1F`)** at `(1.44, 0.78, -1.92)`:
        - `CrystalWaterBowl1F` (`mats["crystal_glass"]`): low wide chamfered/lathed crystal bowl (`r_bot=0.10, r_top=0.135, height=0.085`).
        - `CrystalBowlWater1F` (`mats["water_meniscus"]`): crisp translucent water fill disc centered `(1.44, 0.798, -1.92)`, `r=0.118, height=0.012` (so JS can raise Y cleanly during pouring!).
Return ONLY valid Python code (< 210 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_salon_seating.py', doraise=True); "
                "import sys; sys.path.insert(0,'scripts'); "
                "from penthouse_kit.prim_lib import SceneContext; from penthouse_kit.mod_salon_seating import build_salon_seating; "
                "ctx=SceneContext(); ks=['rug','cream_pillow','rift_oak','walnut_solid','boucle','burgundy','cognac_suede','slate_linen','travertine','brass','smoked_stone','bronze_dark','walnut_fluted','sheer_linen','ceramic_white','evian_flint_glass','evian_label','evian_cap','water_meniscus','crystal_glass','charcoal','concierge_screen']; "
                "mats={k:ctx.color_mat(k,(0.5,0.5,0.5,1)) for k in ks}; build_salon_seating(ctx, mats); "
                "names=[k[0] for k in ctx.builders]; "
                "for req in ['SalonRug','EvianBottles1F','EvianPourBottle1F','EvianPourCap1F','CrystalWaterBowl1F','CrystalBowlWater1F','ConciergePager1F']: assert req in names, req; "
                "rug_b=dict((k[0],v) for k,v in ctx.builders.items())['SalonRug']; assert rug_b.normals[0][1] > 0.9, rug_b.normals[0]; "
                "print('OK mod_salon_seating')\""
            ),
        },
        {
            "name": "mod_terrace_sky",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_terrace_sky.py",
            "system": (
                "You are an AD100 outdoor pavilion & coastal landscape 3D artist. Build solid outward-normal ergonomic curved barrel chairs, "
                "non-tiled cloud-washed outdoor rug, and organic 3-layer atmospheric coastal mountains with surf-kissed rocky shoreline, pine ridges, and misty far peaks. Keep under 240 lines."
            ),
            "prompt": f"""Rewrite `scripts/penthouse_kit/mod_terrace_sky.py` defining `build_terrace_and_sky(ctx, mats)`.
{PENTHOUSE_PRIM}
Import `from penthouse_kit.cushion_helper import add_designer_pillow`!

Exact coordinates & required upgrades:
1. Keep `TerraceDeck`, `TerraceGlass` (`Z=-29.42` & `X=+-16.05`), `TerraceHandrail`, `TerracePosts`.
2. **NO MORE TILED GRID ON TERRACE RUG**:
   - Build `TerraceOutdoorRug` (`mats["rug_2f"]`) centered `(1.10, 0.015, -22.90)`, width `11.6`, depth `7.6` (`X in [-4.7, 6.9]`, `Z in [-26.7, -19.1]`) as a single thin plinth + ONE `+Y` top quad with `uv_scale=(1.0, 1.0)`:
     `b.add_quad((-4.7, 0.032, -19.1), (6.9, 0.032, -19.1), (6.9, 0.032, -26.7), (-4.7, 0.032, -26.7), uv_scale=(1.0, 1.0))`!
3. **TWO ERGONOMIC ROUND BARREL LOUNGE CHAIRS** (keep exact verified `2.55x` scale & outward winding!):
   - `Chair 1`: `(-1.35, -22.60)` yaw `-math.pi * 0.5 + 0.18` (`slate_linen` pillow); `Chair 2`: `(3.55, -22.60)` yaw `-math.pi * 0.5 - 0.22` (`burgundy` pillow).
   - Outer shell `TerraceSofaTeak` in `mats["rift_oak"]` (`R_out=1.62, R_in=1.44, y_base=0.20, h(t)=1.48 - 0.58 * abs(2t-1)^1.6`, WITH outward outer-wall normals `(c1->c0)`, inward inner-wall normals `(c0->c1)`, upward top rim, downward bottom rim, closed start/end caps!).
   - Inner `TerraceSofaSeat` (`mats["boucle"]`, lathe rim `Y=0.73, r=1.40, center Y=0.66`) + `TerraceSofaBack` (`R=1.20..1.39` strictly inside `R_in=1.44`, correct inward/outward/top winding!).
   - Side Drum Table `(1.10, -23.20)` in `rift_oak` + `travertine` top (`Y=0.72`) + `TerraceGlasses` (`(0.90, -23.08)` & `(1.30, -23.32)`); Ottoman `(-1.10, -25.15)`; Lanterns `(-5.10, -24.40)` & `(7.30, -24.40)`; Olive Trees `(-12.2, -23.5)` & `(12.4, -24.2)`.
4. **3-LAYER NATURAL ATMOSPHERIC COASTAL MOUNTAINS (`Y=-8.5` sea plane — REPLACE THE UGLY 6-VERTEX CARDBOARD TRAPEZOID!)**:
   - Keep `CoastalCliff` bluff slope under terrace (`Z=-29.8..-46.0`, `Y=-0.5..-8.8`) and `OceanVistaWater` (`Y=-8.5`, `X=-210..210`, `Z=-28..-165`, `24x16` grid).
   - Build **Layer 1 (`CoastalHeadlandsRock`, `mats["headland_rock"]`) & Surf Foam (`CoastalSurfFoam`, `mats["cream_pillow"]`)**:
     - Left sculpted 3D peninsula cove (`Z ~ -64..-78, X in [-82, -12]`): 30 radial/ridge segments tapering softly into `-8.5` water (`Y = -8.5` shoreline -> `+0.8 .. +3.2` rounded limestone spine, depth from `Z=-62` back to `Z=-78` so it reads as solid 3D rock, NOT a flat cardboard wall!) + thin glowing shoreline surf apron (`Y = -8.42`) curving along its water edge.
   - Build **Layer 2 (`CoastalPineHeadlands`, `mats["coastal_pine"]`)**:
     - Rich rolling Mediterranean pine & cypress ridges left (`X in [-125, -18], Z ~ -94..-112`, peak `Y = +5.6` with smooth harmonic cosine hills `32` segments + back slope!) and right (`X in [+18, +125], Z ~ -106..-124`, peak `Y = +6.4` with soft valley saddle!).
   - Build **Layer 3 (`FarMistMountains`, `mats["far_mist_mountain"]`)**:
     - Sweeping distant mountain range (`X in [-165, +165], Z = -142`, `48` segments) softly undulated between `Y = -8.5` and `Y = +10.2` via smooth cosine harmonics for serene aerial depth!
   - Keep 2 distant sailboats (`(-14.0, -74.0)` & `(22.0, -102.0)`) + `SkyCyclorama` (`radius=148, y=-26..76`).
Return ONLY valid Python code (< 240 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_terrace_sky.py', doraise=True); "
                "import sys; sys.path.insert(0,'scripts'); "
                "from penthouse_kit.prim_lib import SceneContext; from penthouse_kit.mod_terrace_sky import build_terrace_and_sky; "
                "ctx=SceneContext(); ks=['travertine','glass','brass','bronze_dark','rug_2f','rift_oak','boucle','slate_linen','burgundy','cream_pillow','walnut_fluted','crystal_glass','warm_bulb','bark','olive_leaf','olive_leaf_bright','headland_rock','coastal_pine','far_mist_mountain','horizon_ocean','sail_canvas','sky_sunny']; "
                "mats={k:ctx.color_mat(k,(0.5,0.5,0.5,1)) for k in ks}; build_terrace_and_sky(ctx, mats); "
                "names=[k[0] for k in ctx.builders]; "
                "for req in ['TerraceSofaSeat','TerraceSofaTeak','CoastalPineHeadlands','FarMistMountains','OceanVistaWater','SkyCyclorama','TerraceOutdoorRug']: assert req in names, req; "
                "rug=dict((k[0],v) for k,v in ctx.builders.items())['TerraceOutdoorRug']; assert rug.normals[-1][1] > 0.9, rug.normals[-1]; "
                "print('OK mod_terrace_sky')\""
            ),
        },
        {
            "name": "job_club_lounge",
            "model": "deepseek-chat",
            "out_path": "scripts/yacht_kit/job_club_lounge.py",
            "system": (
                "You are a Monaco/Portofino waterfront yacht-club architect. Build an anchored Roman travertine seawall promenade, "
                "teak & brass shore gangway bridge connecting to the floating pier (X=-5.50, Y=0.72), an open-air Orient-Express Marina Lounge Pavilion "
                "with aperitivo bar, linen lounge suites, olive planters, and coastal terraced backdrop. Keep under 215 lines."
            ),
            "prompt": f"""Create `scripts/yacht_kit/job_club_lounge.py` building and exporting `assets/models/yacht_club_lounge.glb`.
{YACHT_PRIM}

CRITICAL Seam & Coordinate Contract (`yacht_berth.glb` occupies `X in [-5.55, -2.80], Z in [-12, 12], Y_top = 0.72`):
1. **Teak & Brass Connecting Bridge (`X = -9.15 .. -5.45, Z in [-11.3, -7.9]`)**:
   - Arched Burma teak walkway (`i_teak`) ramping gently from shore promenade `(-9.15, Y=1.12)` to floating pier `(-5.45, Y=0.72)`, width `3.2m` along Z (`Z=-9.6`), supported by sleek bronze under-beams (`i_brz`), flanked at `Z=-11.2` and `Z=-8.0` by frameless clear glass guard panels (`m_glass`) capped with Burma teak & PVD rails (`i_tf`, `i_pvd`).
2. **Roman Travertine Seawall & Waterfront Promenade (`X = -24.5 .. -9.05, Z in [-16.0, 14.0]`)**:
   - Solid seawall plinth (`i_trav`) extending down to underwater `-1.25` up to crisp bullnose deck `Y = 1.12` (`X = -9.2` seawall edge).
   - Warm underwater cove LED strip along `X = -9.06, Y = 0.15` (`i_amber` emissive) & carved sea steps descending into the harbour at `Z = +5.0..+8.5`.
   - Along the waterfront promenade edge (`X = -9.20`), install frameless clear tempered glass panels & Burma-teak/champagne-PVD handrails (`Y = 1.12..2.02`), leaving `Z in [-11.4, -7.8]` **OPEN** onto the connecting bridge!
3. **Orient-Express Marina Lounge Pavilion (`X = -21.5 .. -10.8, Z in [-12.0, +6.0]`)**:
   - Raised Burma teak & woven rug terrace plinth (`Y = 1.12..1.18`), architectural fluted-limestone/travertine colonnade pillars rising from `Y=1.18` to cantilevered cantilevered navy (`i_hull`) + slatted teak (`i_tf`) roof (`Y = 4.40..4.68`) with recessed warm 2700K emissive ceiling coves (`i_amber`).
   - **Marina Aperitivo Bar (`X = -18.8, Z = -2.0`)**: Travertine waterfall counter (`Y=1.18..2.22`), marquetry walnut (`i_marq`) front, 4 brushed bronze & cognac saddle-leather barstools (`X=-17.3, Z in [-3.4..+0.4]`), backlit bar bottle display (`i_glass` + `i_amber`).
   - **Two Waterfront Lounge Sofa Suites (`X = -13.6, Z = -5.2` and `Z = +1.8`)** facing `+X` toward the moored 20m yacht: woven rug bases (`i_rug`), low teak plinths, deep cream outdoor-linen sofas (`i_linen`) with cognac leather bolsters (`i_leather`), travertine drum coffee tables + crystal tumblers, and sculpted travertine planters with green olive spheres (`base_factor=(0.30, 0.39, 0.28, 1.0)` & `bark`) at promenade corners!
4. **Terraced Limestone & Mediterranean Pine Coastal Backdrop (`X = -42.0 .. -23.5, Z in [-22, 20]`)**:
   - Multi-stepped limestone retaining walls (`i_trav`, rising `Y = 1.1 .. 4.2`) + soft rolling coastal hills & lush green Mediterranean pine canopies rising to `Y = +9.5` so views looking West (`-X`) sit naturally in a Portofino/Monaco hillside amphitheatre.
5. Export directly to `OUT = Path(__file__).resolve().parents[2] / "assets" / "models" / "yacht_club_lounge.glb"`.
   Keep file size compact (< 6,000,000 bytes) using `load_bundle(...)` shared material builders cleanly (remember `gb.mesh(mat_idx, name)` ONCE per material!).
Return ONLY valid Python code (< 220 lines).""",
            "verify_cmd": (
                "python3 scripts/yacht_kit/job_club_lounge.py && "
                "python3 -c \"import os, struct, json; p='assets/models/yacht_club_lounge.glb'; "
                "sz=os.path.getsize(p); assert 50000 < sz < 7500000, sz; "
                "raw=open(p,'rb').read(); jl=struct.unpack('<I',raw[12:16])[0]; g=json.loads(raw[20:20+jl]); "
                "assert len(g['meshes'])>=6; print('OK club_lounge', sz)\""
            ),
        },
        {
            "name": "job_furniture_props",
            "model": "deepseek-chat",
            "out_path": "scripts/yacht_kit/job_furniture_props.py",
            "system": (
                "You are a superyacht exterior & cabin bespoke furniture artist. Strictly stay within both validate_glb.py bounding zones "
                "and create all 4 required anchors (`dog_mat`, `prop_cleat`, `prop_bar`, `prop_journal`). Make the aft cockpit genuinely plush and rich. Keep under 240 lines."
            ),
            "prompt": f"""Rewrite `scripts/yacht_kit/job_furniture_props.py` defining `build()` outputting `assets/models/yacht_furniture_props.glb`.
{YACHT_PRIM}

STRICT VALIDATOR ZONES & ANCHORS (`scripts/yacht_kit/validate_glb.py` WILL REJECT ANY VERTEX EVEN 5mm OUTSIDE!):
- Zone 0 (Aft exterior cockpit): `[-1.50, 1.20, -9.00]` .. `[+2.20, 2.32, -3.20]`
- Zone 1 (Cabin interior): `[-1.42, 1.32, -2.95]` .. `[+1.42, 2.80, +1.60]`
- Required anchors:
  `gb.add_anchor("dog_mat", (-1.02, 1.41, -3.88))`
  `gb.add_anchor("prop_cleat", (1.52, 1.26, -8.55))`
  `gb.add_anchor("prop_bar", (0.0, 2.38, 1.22))`
  `gb.add_anchor("prop_journal", (-1.08, 1.76, -0.42))`

Upgrade the exterior yacht deck furniture inside Zone 0 (`X in [-1.48..2.18], Y in [1.22..2.30], Z in [-8.95..-3.25]`):
1. **Aft Transom Curved L-Lounge Banquette (`X in [-0.45..1.98], Z in [-8.35..-6.05]`)**:
   - Sculpted Burma teak base (`m_teak`, `Y=1.26..1.44`) wrapping both aft (`Z=-8.10`, length `2.30`) and starboard arm (`X=1.78`, `Z in [-8.10..-6.10]`).
   - Deep plush cream `m_linen` seat cushions (`Y=1.44..1.72`, `bevel=0.03`) + **contrast saddle-leather piping strips** (`m_leather` / `m_piping`) + sculpted reclined cushioned backrests (`Y=1.72..2.14` well below `2.32`!) + **4 thick tailored scatter pillows** along the banquette!
2. **Inlaid Teak & PVD-Brass Yacht Cocktail Table (`(0.55, 1.30, -6.95)`, top `Y=1.88`)**:
   - Twin brushed-PVD tapered pedestals (`m_pvd`), elliptical/chamfered Burma teak top (`0.96 x 0.04 x 0.68`) with inset PVD brass trim ring, styled with crystal champagne ice bucket + bottle + two champagne flutes (`m_glass`) + stitched leather serving tray (`m_leather`)!
3. **Two Plush Resort Sunbeds (`Z in [-5.45..-3.45]`, centered at `X=0.45` and `X=1.45`) + Low Side Table `(0.95, 1.30, -4.45)`**:
   - Sculpted Burma teak sunbed platforms (`Y=1.28..1.46`) topped with thick `12cm` padded cream `m_linen` tufted mattresses (`Y=1.46..1.58`, gracefully curved reclined backrest rising to `Y=2.14`) and cylindrical cognac saddle-leather headrest bolsters (`m_leather` at `Z=-3.75`)!
4. **Bruce's Bespoke Raised Oval Yacht Daybed (`dog_mat` around `(-1.02, 1.32, -3.88)`)**:
   - Sculpted Burma-teak oval cradle rim (`0.90 x 0.14 x 0.56`), plush cognac `m_leather` wrap-around bolster wall (`Y=1.34..1.50`), thick soft cream `m_linen` interior pillow mattress (`Y=1.34..1.42`, centered `dog_mat` anchor `(-1.02, 1.41, -3.88)`), and a miniature PVD brass nameplate on front! No flat scrap mat!
5. **Preserve Deck Cleat + Coiled Mooring Rope** (`(1.52, 1.26, -8.55)`), **Salon Barware** (`(0.0, 2.38, 1.22)`), **Stitched Leather Logbook** (`(-1.08, 1.76, -0.42)`), and **Step Stool** (`(-0.78, 1.32, -1.18)`), ALL strictly inside Zone 0 or Zone 1!
Return ONLY valid Python code (< 240 lines).""",
            "verify_cmd": "python3 scripts/yacht_kit/job_furniture_props.py && python3 scripts/yacht_kit/validate_glb.py --job furniture_props",
        },
    ]

    summary = run_parallel_codegen(tasks, max_workers=6, max_retries=3)
    failed = [r for r in summary["results"] if not r["ok"]]
    if failed:
        for r in failed:
            print(f"[FAILED] {r['name']}: {r.get('verify_msg', '')[:600]}")
        sys.exit(1)
    print(f"ALL {len(tasks)} BATCH 11 TASKS PASSED IN {summary['wall_sec']}s!")


if __name__ == "__main__":
    main()
