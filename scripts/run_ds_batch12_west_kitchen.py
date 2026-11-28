#!/usr/bin/env python3
"""
Batch 12 (1F West Open-Plan Mountain-View Kitchen & Built-In French Double-Door Fridge):
Parallel DeepSeek codegen with automated verification via ds_worker.run_parallel_codegen.
Generates:
1. scripts/penthouse_kit/tex_kitchen_surfaces.py
2. scripts/penthouse_kit/mod_west_fridge.py
3. scripts/penthouse_kit/mod_west_kitchen.py
4. scripts/penthouse_kit/mod_west_mountain_vista.py
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
Available mats keys passed in `mats`:
  oak, marmorino, marble, smoked_stone, verde_alpi, rift_oak, celadon_plaster, slate_linen,
  walnut_fluted, walnut_solid, brass, bronze_dark, window_frame, chrome,
  warm_led, warm_bulb, glass, frosted_glass, travertine,
  burgundy, cognac_suede, cream_pillow, charcoal, ceramic_white, bark,
  olive_leaf, olive_leaf_bright, headland_rock, coastal_pine, far_mist_mountain,
  crystal_glass, glass_smoke,
  calacatta_viola, gunmetal, terracotta, dairy_label,
  berry_blue, berry_red, produce_green, citrus_yellow,
  steak_marbled, wine_bottle, champagne_liquid
STRICT BAN: NEVER include forbidden words anywhere in strings or comments.
"""


def main():
    tasks = [
        {
            "name": "tex_kitchen_surfaces",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/tex_kitchen_surfaces.py",
            "system": (
                "You are an AD100 architectural materials synthesizer using NumPy + PIL. "
                "Write clean, vectorized, deterministic texture generators under 200 lines."
            ),
            "prompt": """Create `scripts/penthouse_kit/tex_kitchen_surfaces.py` exporting 4 functions:

1. `make_calacatta_viola_tex(size: int = 1024) -> Image.Image`:
   - Warm alabaster/ivory marble (`#F2EDE5`, `#E7DFD3`) veined with organic multi-octave FBM breccia ribbons in deep cabernet-burgundy (`#652C39`, `#4A1E28`) and soft warm taupe-grey (`#9C8F87`).
2. `make_gunmetal_brushed_tex(size: int = 512) -> Image.Image`:
   - Architectural brushed PVD dark gunmetal (`#2B2D32` .. `#3A3D43`) with subtle fine horizontal brushed streaks.
3. `make_terracotta_pot_tex(size: int = 512) -> Image.Image`:
   - Aged Tuscan hand-thrown terracotta clay (`#B56B4E` .. `#9E583E`) with subtle mineral efflorescence.
4. `make_organic_dairy_label_tex(size: int = 512) -> Image.Image`:
   - Clean Apple-minimalist dairy/yogurt label sheet on cream-linen card (`#FAF7F1`): thin gold-taupe border, dark ink serif/sans band reading `GRASS-FED MILK` on upper band and `0% GREEK YOGURT` on lower band, plus a tiny double-diamond emblem drawn cleanly with `ImageDraw` (no text inside the diamond). Use PIL `ImageDraw.Draw` with `ImageFont.load_default()` safely.

Return ONLY valid Python code (< 200 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/tex_kitchen_surfaces.py', doraise=True); "
                "import sys; sys.path.insert(0,'scripts'); "
                "from penthouse_kit.tex_kitchen_surfaces import ("
                "make_calacatta_viola_tex, make_gunmetal_brushed_tex, make_terracotta_pot_tex, make_organic_dairy_label_tex); "
                "assert make_calacatta_viola_tex(256).size==(256,256); "
                "assert make_gunmetal_brushed_tex(128).size==(128,128); "
                "assert make_terracotta_pot_tex(128).size==(128,128); "
                "assert make_organic_dairy_label_tex(256).size==(256,256); "
                "print('OK tex_kitchen_surfaces')\""
            ),
        },
        {
            "name": "mod_west_fridge",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_west_fridge.py",
            "system": (
                "You are a luxury Gaggenau / Sub-Zero built-in appliance 3D modeler. "
                "Build a richly stocked built-in French double-door refrigerator with EXACT required mesh names "
                "and flush coordinates. Keep code under 210 lines."
            ),
            "prompt": f"""Create `scripts/penthouse_kit/mod_west_fridge.py` exporting `build_french_fridge(ctx, mats)`.
{PENTHOUSE_PRIM}

EXACT spatial bay (facing +X into the kitchen at X = -13.86):
- Width along Z: `Z in [-4.30, -2.10]` (center Z = -3.20, bay width = 2.20m).
- Height along Y: `Y in [0.10, 2.58]` (flush plinth Y=0..0.10, interior floor Y=0.14, ceiling Y=2.52).
- Depth along X: back wall `X = -14.80`, door front face at `X = -13.86` (depth ~0.94m).

Build these EXACT named meshes cleanly (must be distinct names so JS can pivot doors!):
1. **Cabinet Shell & Lighting**:
   - `FridgeInteriorShell` (`mats["ceramic_white"]`): back plate (`X=-14.78`), left/right walls (`Z=-4.26`, `Z=-2.14`), floor (`Y=0.14`), top (`Y=2.50`), so interior looks bright & clean when opened.
   - `FridgeFrameTrim` (`mats["gunmetal"]`): recessed outer perimeter bezel flush around `Z=-4.30..-2.10, Y=0.10..2.58, X=-13.88`.
   - `FridgeInteriorLED` (`mats["warm_led"]`): left & right vertical side diffuser strips (`X=-14.08, Z=-4.22` and `Z=-2.18, Y=0.35..2.40`) + top cornice light (`Y=2.47`).
   - `FridgeGlassShelves` (`mats["crystal_glass"]`): 3 glass shelves spanning `X=-14.34, sx=0.78, sz=2.04` at `Y = 1.00, 1.42, 1.84` + stainless front trim lips (`mats["chrome"]`).
2. **Stocked Western Luxury Healthy Produce (clean silhouettes, well spaced inside `X in [-14.66, -14.02]`, `Z in [-4.12, -2.28]`)**:
   - **Top shelf (`Y = 1.85..2.38`)**:
     - `FridgeMilkBottles`: 4 tall tapered glass milk & oat-milk carafes (`mats["cream_pillow"]` & `mats["evian_flint_glass"]` or `mats["crystal_glass"]`, `Z = -4.02, -3.84, -3.66, -3.48`, `X = -14.32, Y = 1.86..2.22`) + `FridgeMilkLabels` (`mats["dairy_label"]` collar cylinders around them).
     - `FridgeGreekYogurt`: 5 squat cylindrical 0% Unsweetened Greek Yogurt tubs (`mats["ceramic_white"]` body `r=0.075, h=0.14` at `Y=1.86` and `Z = -3.12..-2.42`, `X = -14.28`, topped with `mats["dairy_label"]` / `mats["slate_linen"]` lids).
   - **Upper-mid shelf (`Y = 1.43..1.78`)**:
     - `FridgeFruitBowls`: 3 ceramic shallow bowls (`mats["ceramic_white"]` wide cones/lathes at `Z = -3.92, -3.20, -2.50`, `X = -14.32, Y = 1.44`) filled generously with:
       - Cluster of blueberries (`mats["berry_blue"]` small spheres at `Z=-3.92`),
       - Cluster of strawberries/raspberries (`mats["berry_red"]` small spheres at `Z=-3.20`),
       - Green avocados & crisp apples (`mats["produce_green"]`) + Meyer lemons (`mats["citrus_yellow"]`) at `Z=-2.50`.
   - **Lower-mid shelf (`Y = 1.01..1.36`)**:
     - `FridgeVeggieCrispers`: 2 clear acrylic crisper trays (`mats["crystal_glass"]` boxes `X=-14.34, Z=-3.68` and `Z=-2.72`) filled with crisp leafy greens/spinach puffs & asparagus stalks (`mats["produce_green"]`), red heirloom tomatoes & bell peppers (`mats["berry_red"]`), and yellow squash (`mats["citrus_yellow"]`).
   - **Bottom 0°C BioFresh Zone (`Y = 0.22..0.94`)**:
     - `FridgeBioFreshDrawer`: twin wide drawers (`mats["glass_smoke"]` fronts + `mats["chrome"]` pulls at `Y = 0.72` and `0.38`) holding `mats["steak_marbled"]` marbled ribeyes & Bruce's glass meal jars (`mats["ceramic_white"]`/`mats["dairy_label"]`).
3. **Double Doors & Handles (EXACT names, flush at `X = -13.86`, thickness `0.06m`)**:
   - **Left Door (`Z in [-4.28, -3.21]`, center `Z = -3.745`, width `1.07`, `Y = 0.12..2.56`)**:
     - `FridgeDoorLeft`: `mats["rift_oak"]` flush panel (`cx=-13.86, cy=1.34, cz=-3.745, sx=0.055, sy=2.44, sz=1.06`) with slim `mats["gunmetal"]` side stile accent.
     - `FridgeHandleLeft`: `mats["brass"]` vertical bar cylinder at `cx=-13.79, y0=0.88, cz=-3.30, r=0.016, h=1.08`.
   - **Right Door (`Z in [-3.19, -2.12]`, center `Z = -2.655`, width `1.07`, `Y = 0.12..2.56`) — Windowed Beverage/Produce Showcase Door**:
     - `FridgeDoorRight`: 4-piece `mats["rift_oak"]` frame leaving a sleek rectangular glass window open at `Z in [-3.02, -2.29], Y in [0.98, 2.34]` (top rail, bottom apron, hinge stile, handle stile) + slim `mats["gunmetal"]` bezel.
     - `FridgeDoorRightGlass`: `mats["glass_smoke"]` box inside that opening (`cx=-13.86, cy=1.66, cz=-2.655, sx=0.02, sy=1.36, sz=0.73`).
     - `FridgeHandleRight`: `mats["brass"]` vertical bar cylinder at `cx=-13.79, y0=0.88, cz=-3.10, r=0.016, h=1.08`.

Return ONLY valid Python code (< 210 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_west_fridge.py', doraise=True); "
                "print('OK mod_west_fridge syntax')\""
            ),
        },
        {
            "name": "mod_west_kitchen",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_west_kitchen.py",
            "system": (
                "You are an AD100 & Boffi architectural kitchen architect. "
                "Build the West Mountain-View Open Kitchen (`X in [-14.85, -8.5]`, `Z in [-15.2, -0.2]`, `Y in [0, 9.08]`) "
                "featuring zero blank white walls, exact floor/counter datums, outward normals, and < 220 lines."
            ),
            "prompt": f"""Create `scripts/penthouse_kit/mod_west_kitchen.py` exporting `build_west_kitchen(ctx, mats)`.
First import `from penthouse_kit.mod_west_fridge import build_french_fridge` and call `build_french_fridge(ctx, mats)` inside `build_west_kitchen(ctx, mats)`.
{PENTHOUSE_PRIM}

EXACT Coordinates & Zones:
1. **7.8m Frameless Mountain Picture Window & Herb Garden Ledge (`X = -14.9..-13.9, Z in [-14.6, -6.2]`)**:
   - `KitchenWindowFrame` (`mats["window_frame"]`): slim architectural perimeter boxes (`0.06` thick) framing `Z in [-14.4, -6.6], Y in [1.08, 4.92]` at `X=-14.88` (left/right jambs, head beam, sill rail; ONLY 1 slender center mullion at `Z=-10.5` or none for max panorama).
   - `KitchenWindowGlass` (`mats["glass"]`): clear pane across opening `(-14.88, 3.00, -10.5, 0.025, 3.82, 7.76)`.
   - `KitchenHerbCounter` (`mats["rift_oak"]` lower cabinets at `(-14.32, 0.50, -10.4, 1.05, 1.00, 8.4)` + `mats["travertine"]` waterproof counter slab top at `Y = 1.04` (`(-14.32, 1.04, -10.4, 1.12, 0.08, 8.48)`) + brass undermount sink recess (`mats["gunmetal"]` + `mats["brass"]` arched gooseneck faucet at `(-14.30, 1.08, -10.5)`).
   - `KitchenHerbPots` (`mats["terracotta"]` 5 low wide pots at `X=-14.42, Y=1.08, Z in (-13.4, -11.9, -9.1, -7.8, -6.9)`) + `KitchenHerbFoliage` (`mats["olive_leaf"]` & `mats["olive_leaf_bright"]` lush layered herb foliage domes/clusters rising to `Y=1.22..1.44`).
2. **Floor-to-Mezzanine Architectural Culinary Tall Wall (`X = -14.85..-13.85, Z in [-6.2, -0.2], Y = 0..9.08`)**:
   - `KitchenTallUpperWall`: Fill `Y = 2.60..9.08` seamlessly up to mezzanine floor `Y=9.14` across `Z in [-6.2, -0.2]` using `mats["rift_oak"]` vertical architectural cabinetry + `mats["brass"]` shadow-gap inlays at `Y=5.80`, `Z=-4.30`, `Z=-2.10` (ZERO blank white wall!).
   - **North Bay (`Z in [-6.15, -4.32]`)**:
     - Flush `mats["gunmetal"]` lower drawers & under-counter oven (`Y=0.10..1.05`).
     - Backlit `mats["calacatta_viola"]` espresso alcove (`Y=1.06..2.22`, back `X=-14.78`, side cheeks, `mats["warm_led"]` top cove strip at `Y=2.18`).
     - `KitchenEspressoMachine` (`mats["chrome"]` + `mats["brass"]` levers at `(-14.26, 1.06, -5.20)` so portafilter spout sits near `(-14.08, 1.32, -5.20)`), `KitchenEspressoCup` (`mats["ceramic_white"]` cup & saucer at `(-14.08, 1.06, -5.20)`), `KitchenGranolaTray` (`mats["walnut_solid"]` board + golden `mats["terracotta"]`/`mats["cognac_suede"]` oat-nut Granola bars at `(-14.12, 1.06, -4.68)`).
   - **Center Bay (`Z in [-4.30, -2.10]`)**: Handled by `build_french_fridge(ctx, mats)`.
   - **South Bay (`Z in [-2.08, -0.25]`)**:
     - `KitchenWineCellar`: Dual-zone glass cellar (`mats["gunmetal"]` frame, `mats["glass_smoke"]` front door at `X=-13.86`, `mats["warm_led"]` interior backlight, 6 `mats["burgundy"]` suede cradle shelves holding horizontal `mats["wine_bottle"]` champagne & Bordeaux bottles + `mats["brass"]` cap highlights).
3. **Calacatta Viola Monolithic Waterfall Island (`X = -10.4, Z in [-13.2, -6.4], top Y = 0.92 m`)**:
   - `KitchenIslandStone` (`mats["calacatta_viola"]`): `60mm` top slab `add_rounded_box(-10.4, 0.89, -9.8, 1.60, 0.06, 6.80, bevel=0.015)` + North & South `0.14m` thick waterfall legs at `Z=-13.13` & `Z=-6.47` (`cy=0.45, sy=0.90`).
   - `KitchenIslandCore` (`mats["rift_oak"]` + `mats["brass"]` plinth kick): centered at `X=-10.68, sx=0.96, Y=0.06..0.86` leaving a generous cantilevered East bar knee overhang (`X=-10.20..-9.60`).
   - **Island Props (sitting cleanly at `Y = 0.92`)**:
     - `KitchenTeppanyaki`: flush `mats["charcoal"]` + `mats["chrome"]` bezel grill plate at `(-10.55, 0.926, -8.0, 0.72, 0.016, 1.15)`.
     - `KitchenSteakBoard`: `mats["walnut_solid"]` thick cutting block at `(-10.52, 0.945, -10.3, 0.62, 0.05, 0.92)` topped by 3 neatly aligned `KitchenRawSteaks` (`mats["steak_marbled"]` rounded slabs at `Z=-10.55, -10.30, -10.05`, `Y=0.985`) + small `mats["ceramic_white"]` sea-salt pinch bowl.
     - `KitchenPourBottle` (`mats["wine_bottle"]` champagne bottle `add_lathe(-10.55, 0.92, -12.10, [(0,0),(0.045,0),(0.045,0.18),(0.02,0.28),(0.016,0.32),(0,0.32)])`) + `KitchenPourFoil` (`mats["brass"]` capsule cylinder at `y0=1.18, h=0.06`).
     - `KitchenWineDecanter` (`mats["crystal_glass"]` wide-base decanter lathe at `(-10.22, 0.92, -12.06)` + 2 champagne coupes at `(-10.14, 0.92, -11.74)` & `(-10.14, 0.92, -12.36)`) + `KitchenDecanterWine` (`mats["champagne_liquid"]` disc inside decanter at `Y=0.96`).
     - `KitchenYogurtBowl` (`mats["ceramic_white"]` breakfast bowl with `mats["berry_blue"]` / `mats["berry_red"]` berries on East bar at `(-9.92, 0.92, -8.8)`).
     - `KitchenBruceDish` (`mats["brass"]` & `mats["travertine"]` dog tasting bowl resting cleanly on floor near island North corner `(-9.25, 0.0, -13.25)`).
4. **3 Counter Bar Stools & Overhead Brass Linear Pendant**:
   - `KitchenBarStools`: at `X = -9.16, Z in (-7.6, -9.8, -12.0)`: walnut legs + brass footrest ring (`Y=0.24`), `mats["cognac_suede"]` contoured saddle seat (`Y=0.67`), `mats["burgundy"]` backrest & piping cushion (`Y=0.80`).
   - `KitchenLinearPendant`: `4.8m` slim `mats["brass"]` housing (`(-10.4, 2.44, -9.8, 0.08, 0.06, 4.80)`) + `mats["warm_led"]` diffuser strip + twin brass suspension rods up to `Y=9.08`.

Return ONLY valid Python code (< 220 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_west_kitchen.py', doraise=True); "
                "print('OK mod_west_kitchen syntax')\""
            ),
        },
        {
            "name": "mod_west_mountain_vista",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_west_mountain_vista.py",
            "system": (
                "You are an AAA environment artist building a 3-layer Mediterranean-Alpine mountain vista in Three.js. "
                "All geometry stays west of X=-15.2 and inside R=145m SkyCyclorama, anchored cleanly into Y=-9.0 seabed so zero floating edges. Keep under 155 lines."
            ),
            "prompt": f"""Create `scripts/penthouse_kit/mod_west_mountain_vista.py` exporting `build_west_mountain_vista(ctx, mats)`.
{PENTHOUSE_PRIM}

Place grounded 3-layer 3D mountain landscape strictly west of the penthouse (`X < -15.3`, `X > -136`, `Z in [-105, 55]`):
1. **Foreground Herbal Garden Terrace (`X in [-30, -15.3]`, `Z in [-32, 12]`)**:
   - `WestGardenTerrace`: `mats["travertine"]` stone garden terrace apron outside window (`X=-19.0, Y=-0.25, Z=-10.5, sx=7.4, sy=0.7, sz=22.0`) + low dry-stone retaining parapet (`mats["headland_rock"]` along `X=-22.8, Y=0.35, Z=-10.5, sx=0.65, sy=0.95, sz=22.4`) + warm garden bollards (`mats["bronze_dark"]` & `mats["warm_bulb"]`).
   - `WestGardenPines`: 6 sculpted Mediterranean cypress & umbrella pine trees outside the stone parapet (`X in [-27.5, -23.6], Z in [-20, 4]`): slender trunks (`mats["bark"]`) + layered organic foliage clusters (`mats["olive_leaf"]` & `mats["olive_leaf_bright"]`) visible right outside the `Y=1.08..4.92` window!
2. **Mid-Ground Pine Forested Slopes & Morning Mist (`X in [-78, -32]`, `Z in [-72, 42]`)**:
   - `WestMidMountainSlope` (`mats["coastal_pine"]`): 3 overlapping sculpted ridge domes using smooth `(ri, si)` spherical/ridge grids anchored from `Y = -9.0` rising cleanly to peaks `Y = 8.5 .. 14.8` around `(-44, -22)`, `(-52, 4)`, `(-66, -10)`.
   - `WestValleyMist`: subtle translucent morning-mist ribbon (`mats["frosted_glass"]` or `mats["glass"]`) hovering calmly in the saddle between foreground & mid-ridge (`X=-36, Y=1.8, Z=-12, sx=3.5, sy=1.1, sz=68`).
3. **Far Alpine-Coastal Horizon Range (`X in [-128, -88]`, `Z in [-98, 56]`)**:
   - `WestFarMountainRange` (`mats["far_mist_mountain"]`): smooth multi-peak silhouette curtain grid (`40` segments along `Z in [-98, 56]`) anchored at base `X=-118, Y=-9.0` and rising in natural cosine ridge peaks to `Y = 17.5 .. 25.5`, facing `+X` toward the kitchen window (`add_quad((x, -9.0, za), (x, -9.0, zb), (x, yb, zb), (x, ya, za))` -> outward normal points `+X`!).

Return ONLY valid Python code (< 155 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_west_mountain_vista.py', doraise=True); "
                "print('OK mod_west_mountain_vista syntax')\""
            ),
        },
    ]

    results = run_parallel_codegen(tasks, max_workers=4)
    print(f"Batch 12 finished: {len(results)} modules generated cleanly.")


if __name__ == "__main__":
    main()
