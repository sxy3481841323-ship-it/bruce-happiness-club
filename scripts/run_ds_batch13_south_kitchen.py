#!/usr/bin/env python3
"""
Batch 13 (Full-Floor North-South Open Marble-Grey Kitchen, True 2.65x Mansion Scale,
French Triple-Bay Sliding Doors, Phase-1 Pool/BBQ Courtyard & Alpine Granite Crag Vista):
Parallel DeepSeek codegen with automated verification via ds_worker.run_parallel_codegen.
Generates:
1. scripts/penthouse_kit/tex_kitchen_surfaces.py
2. scripts/penthouse_kit/mod_south_fridge.py
3. scripts/penthouse_kit/mod_south_kitchen.py
4. scripts/penthouse_kit/mod_south_terrace_mountains.py
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
- b.add_lathe(cx, y0, cz, profile, segs=22)  # profile is list of (radius, dy) pairs!
- b.add_curved_tube(spine_pts, radii, segs=10)
Available mats keys passed in `mats`:
  oak, marmorino, marble, smoked_stone, verde_alpi, rift_oak, celadon_plaster, slate_linen,
  walnut_fluted, walnut_solid, brass, bronze_dark, window_frame, chrome,
  warm_led, warm_bulb, glass, frosted_glass, travertine,
  burgundy, cognac_suede, cream_pillow, charcoal, ceramic_white, bark,
  olive_leaf, olive_leaf_bright, headland_rock, coastal_pine, far_mist_mountain,
  crystal_glass, glass_smoke,
  pietra_grey, tundra_grey, graphite_slate, platinum, nordic_slate,
  alpine_granite, pool_water, terracotta, smart_panel, dairy_label,
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
                "You are an AD100 & Apple architectural materials synthesizer using NumPy + PIL. "
                "Create rich marble-grey architectural textures, stratified granite mountain cliffs, "
                "and an OLED smart-home interface card. Keep clean under 220 lines."
            ),
            "prompt": """Rewrite `scripts/penthouse_kit/tex_kitchen_surfaces.py` exporting 6 functions:

1. `make_pietra_grey_marble_tex(size: int = 1024) -> Image.Image`:
   - Deep architectural charcoal-dove Pietra Grey / Grigio Carnico marble (`#4C5057`..`#3A3D43`) crossed by crisp natural diagonal white calcite veins (`#EDF0F5`, `#CFD5DD`) and fine mineral fissures via vectorized NumPy FBM.
2. `make_tundra_grey_floor_tex(size: int = 1024) -> Image.Image`:
   - Serene cool-grey honed Tundra Grey large-format stone floor slab (`#8A8F96`..`#787D84`) with soft misty stone clouds and thin crisp `2px` architectural joint lines.
3. `make_platinum_slate_tex(size: int = 512) -> Image.Image`:
   - Brushed architectural Graphite-Slate metallic lacquer (`#292C32`..`#353941`) with fine brushed grain.
4. `make_alpine_granite_cliff_tex(size: int = 1024) -> Image.Image`:
   - Dramatic stratified Dolomite / Swiss granite crag rock (`#7A828C`, `#525963`, sharp `#2B3037` shadow crevices, sunlit `#D0D6DE` rock facets) blending in the lower 30% into deep emerald sub-alpine pine/fir forest (`#23372D`..`#324A3C`) so triangulated crag ridges look lifelike and monumental.
5. `make_smart_panel_tex(w: int = 1024, h: int = 704) -> Image.Image`:
   - Crisp Apple Home / Lutron obsidian dark-glass OLED wall control screen (`#0F1115`) showing a clean 3x2 grid of smoked glass status tiles (`border #3A404B`) with champagne-gold/ice-blue accent pills:
     `LIGHTS · SUNSET`, `HEARTH · 215°C`, `HARMAN · JAZZ`, `GALLERY · CH01`, `FRIDGE · 2°C`, `POOL · 27°C` plus a sleek double-diamond emblem at top-right (zero text inside the diamond).
6. `make_organic_dairy_label_tex(size: int = 512) -> Image.Image`:
   - Minimalist cream-linen dairy label card (`#FAF7F1`) with dark ink `GRASS-FED MILK` & `0% GREEK YOGURT` bands.

Keep ALL functions deterministic, vectorized, zero syntax errors, < 220 lines.""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/tex_kitchen_surfaces.py', doraise=True); "
                "import sys; sys.path.insert(0,'scripts'); "
                "from penthouse_kit.tex_kitchen_surfaces import ("
                "make_pietra_grey_marble_tex, make_tundra_grey_floor_tex, make_platinum_slate_tex, "
                "make_alpine_granite_cliff_tex, make_smart_panel_tex, make_organic_dairy_label_tex); "
                "assert make_pietra_grey_marble_tex(256).size==(256,256); "
                "assert make_tundra_grey_floor_tex(256).size==(256,256); "
                "assert make_platinum_slate_tex(128).size==(128,128); "
                "assert make_alpine_granite_cliff_tex(256).size==(256,256); "
                "assert make_smart_panel_tex(256,176).size==(256,176); "
                "assert make_organic_dairy_label_tex(256).size==(256,256); "
                "print('OK tex_kitchen_surfaces')\""
            ),
        },
        {
            "name": "mod_south_fridge",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_south_fridge.py",
            "system": (
                "You are a Gaggenau / Sub-Zero luxury appliance 3D modeler working at TRUE 2.65x Penthouse scale "
                "(2.65 WU = 1 real meter). Build a monumental 5.20 WU wide x 7.10 WU tall Built-In French Double-Door "
                "Refrigerator in the East Culinary Tall Wall facing -X. Keep under 210 lines."
            ),
            "prompt": f"""Create `scripts/penthouse_kit/mod_south_fridge.py` exporting `build_south_french_fridge(ctx, mats)`.
{PENTHOUSE_PRIM}

CRITICAL SCALE: In Penthouse, `1 real meter = 2.65 WU`! This fridge is **7.10 WU tall x 5.20 WU wide** (`Z in [19.40, 24.60]`, `Y in [0.16, 7.26]`), recessed along `X in [12.65, 14.78]` facing **`-X`** into the South Kitchen!

Build these EXACT mesh names so JS can pivot both doors cleanly:
1. **Monumental Cabinet Shell & LED Interior (`X = 12.75..14.74, Z = 19.50..24.50, Y = 0.22..7.16`)**:
   - `FridgeInteriorShell` (`mats["ceramic_white"]`): back plate (`X=14.74`), North/South walls (`Z=19.50`, `Z=24.50`), floor (`Y=0.22`), ceiling (`Y=7.14`).
   - `FridgeFrameTrim` (`mats["platinum"]`): flush outer perimeter bezel around `Z=19.40..24.60, Y=0.16..7.26, X=12.68`.
   - `FridgeInteriorLED` (`mats["warm_led"]`): bright full-height vertical diffuser columns (`X=13.25, Z=19.62` & `Z=24.38, Y=0.50..6.90`) + top strip (`Y=7.08`).
   - `FridgeGlassShelves` (`mats["crystal_glass"]`): 3 thick glass shelves (`X=13.76, sx=1.80, sy=0.06, sz=4.84` at `Y=2.45, 3.85, 5.25`) + `FridgeGlassShelfTrim` (`mats["platinum"]` front edge at `X=12.88`).
2. **True-Scale Stocked Western Healthy Groceries (spaced cleanly along `Z in [19.85, 24.15]`, `X in [13.25, 14.25]`)**:
   - **Top shelf (`Y = 5.28..6.70`)**:
     - `FridgeMilkBottles` (`mats["cream_pillow"]`): 5 large tall milk & oat-milk glass carafes at `Z in (19.95, 20.42, 20.89, 21.36, 21.83)`, `X=13.65`, `add_lathe(..., [(0,0),(0.13,0),(0.145,0.08),(0.145,0.68),(0.075,0.88),(0.065,1.02),(0,1.02)])`.
     - `FridgeMilkLabels` (`mats["dairy_label"]`): collar bands `y0=5.55, r=0.152, h=0.28` on those 5 carafes.
     - `FridgeGreekYogurt` (`mats["ceramic_white"]`): 6 wide 0% Unsweetened Greek Yogurt tubs at `Z in (22.35, 22.78, 23.21, 23.64, 24.07, 23.00)`, `X=13.60` (and `14.10` for 6th), `y0=5.28, r=0.19, h=0.38`.
     - `FridgeGreekYogurtLid` (`mats["dairy_label"]`): matching lids `y0=5.66, r=0.20, h=0.05`.
   - **Upper-mid shelf (`Y = 3.88..4.95`)**:
     - `FridgeFruitBowls` (`mats["ceramic_white"]`): 4 large shallow ceramic fruit bowls at `Z in (20.15, 21.45, 22.75, 23.95)`, `X=13.68, y0=3.88`, `lathe` profile `[(0,0),(0.26,0),(0.44,0.14),(0.48,0.28),(0,0.28)]`.
     - `FridgeBerriesBlue` (`mats["berry_blue"]`): abundant blueberry mound spheres (`r=0.085`) inside `Z=20.15` bowl (`Y=4.20`).
     - `FridgeBerriesRed` (`mats["berry_red"]`): strawberry/raspberry mound spheres (`r=0.095`) inside `Z=21.45` bowl (`Y=4.22`).
     - `FridgeProduceGreen` (`mats["produce_green"]`): avocados & crisp green apples (`r=0.14`) inside `Z=22.75` bowl (`Y=4.22`).
     - `FridgeProduceCitrus` (`mats["citrus_yellow"]`): Meyer lemons (`r=0.11`) inside `Z=23.95` bowl (`Y=4.20`).
   - **Lower-mid shelf (`Y = 2.48..3.55`)**:
     - `FridgeVeggieCrispers` (`mats["crystal_glass"]`): 2 wide clear crisper drawers (`X=13.72, cy=2.92, Z=20.80 & 23.20, sx=1.55, sy=0.78, sz=2.10`).
     - `FridgeVeggieGreens` (`mats["produce_green"]`): lush leafy spinach/kale/asparagus clusters (`r=0.15`) packed inside both crispers.
     - `FridgeVeggieTomatoes` (`mats["berry_red"]`): vine heirloom tomatoes & red bell peppers (`r=0.12`).
     - `FridgeVeggieYellow` (`mats["citrus_yellow"]`): yellow sweet peppers (`r=0.12`).
   - **Bottom `0°C` BioFresh Zone (`Y = 0.35..2.32`)**:
     - `FridgeBioFreshDrawer` (`mats["glass_smoke"]`): twin large smoked drawers (`X=13.72, Z=22.00, Y=1.78` and `0.92`, `sx=1.60, sy=0.68, sz=4.70`), `FridgeBioFreshTrim` (`mats["platinum"]` wide pulls at `X=12.88`), `FridgeBioFreshSteaks` (`mats["steak_marbled"]` marbled dry-aged steaks in upper drawer `Y=1.80`), `FridgeBioFreshJars` (`mats["ceramic_white"]` Bruce fresh-food glass jars in lower drawer `Y=0.72`).
3. **Monumental Outward-Hinged Double Doors (front face at `X = 12.65`, swinging toward `-X`!)**:
   - **Left Door (`Z in [19.44, 21.98]`, center `Z = 20.71`, hinged along `Z=19.45`)**:
     - `FridgeDoorLeft` (`mats["graphite_slate"]`): main slab `(12.65, 3.70, 20.71, 0.14, 6.96, 2.52)` + brushed platinum edge frame (`mats["platinum"]`).
     - `FridgeHandleLeft` (`mats["platinum"]`): tall sculptural cylindrical pull at `cx=12.48, y0=2.10, cz=21.78, r=0.045, h=3.40`.
   - **Right Door (`Z in [22.02, 24.56]`, center `Z = 23.29`, hinged along `Z=24.55`) — Smart-View Glass Door**:
     - `FridgeDoorRight` (`mats["graphite_slate"]`): 4-piece door perimeter framing an open viewing window `Z in [22.38, 24.20], Y in [2.35, 6.55]`:
       - top rail `(12.65, 6.86, 23.29, 0.14, 0.64, 2.52)`, bottom apron `(12.65, 1.28, 23.29, 0.14, 2.14, 2.52)`, North/handle stile `(12.65, 4.45, 22.20, 0.14, 4.20, 0.36)`, South/hinge stile `(12.65, 4.45, 24.38, 0.14, 4.20, 0.36)`, plus thin `mats["platinum"]` inner window bezel.
     - `FridgeDoorRightGlass` (`mats["glass_smoke"]`): smoked glass pane `(12.65, 4.45, 23.29, 0.05, 4.18, 1.80)`.
     - `FridgeHandleRight` (`mats["platinum"]`): tall sculptural cylindrical pull at `cx=12.48, y0=2.10, cz=22.22, r=0.045, h=3.40`.

Return ONLY valid Python code (< 210 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_south_fridge.py', doraise=True); "
                "print('OK mod_south_fridge syntax')\""
            ),
        },
        {
            "name": "mod_south_kitchen",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_south_kitchen.py",
            "system": (
                "You are an AD100 & Boffi South Culinary Wing architect building at TRUE 2.65x Penthouse scale. "
                "Zero warm brown wood or white walls — pure Marble-Grey (Tundra Grey floor, Pietra Grey waterfall island & splashbacks, "
                "Graphite Slate tall cabinetry, Platinum hardware, Nordic Slate stools) with French Slim-Frame Triple-Bay Sliding Doors "
                "looking out to the Pool/BBQ Courtyard and Mountains. Keep under 230 lines."
            ),
            "prompt": f"""Create `scripts/penthouse_kit/mod_south_kitchen.py` exporting `build_south_kitchen(ctx, mats)`.
First import `from penthouse_kit.mod_south_fridge import build_south_french_fridge` and call `build_south_french_fridge(ctx, mats)` inside `build_south_kitchen(ctx, mats)`.
{PENTHOUSE_PRIM}

Build the South Open Culinary Wing (`X in [-15.0, +15.0]`, `Z in [15.4, 28.8]`, `Y in [0, 8.85]`):
1. **Marble-Grey Architectural Shell (zero white walls!)**:
   - `KitchenFloorGrey` (`mats["tundra_grey"]`): `(0.0, -0.06, 22.1, 30.4, 0.12, 13.6, uv_tile=4.0)` + `KitchenFloorInlay` (`mats["platinum"]`, `(0.0, 0.015, 15.55, 27.2, 0.02, 0.08)`).
   - `KitchenCeiling` (`mats["tundra_grey"]`): `(0.0, 8.85, 22.1, 30.4, 0.25, 13.6, uv_tile=4.0)` + `KitchenCeilingCove` (`mats["warm_led"]` perimeter recessed LED lines along `X=±14.0`, `Z=16.0` & `Z=28.0` at `Y=8.70`).
   - `KitchenSideWalls` (`mats["graphite_slate"]`): East wall backing `(14.9, 4.42, 22.1, 0.30, 8.85, 13.6)` & West wall `(-14.9, 4.42, 22.1, 0.30, 8.85, 13.6)`.
2. **South Wall: `21.6 WU` Wide x `7.80 WU` Tall French Slim-Frame Triple-Bay Sliding Glass Doors (`Z = 28.6, X in [-10.8, +10.8], Y in [0.10, 7.90]`)**:
   - `KitchenSouthStoneWall` (`mats["pietra_grey"]`): left pier `(-12.9, 4.42, 28.6, 4.2, 8.85, 0.40)`, right pier `(12.9, 4.42, 28.6, 4.2, 8.85, 0.40)`, header beam `(0.0, 8.38, 28.6, 21.8, 0.96, 0.40)`.
   - `KitchenFrenchFrames` (`mats["graphite_slate"]`): outer perimeter + 4 main bay mullions (`X in (-10.8, -3.6, 3.6, 10.8)`) + horizontal architectural transom bar across all 3 bays at `Y=6.20` + slender French interior sub-bars (`0.09` thick) dividing each 7.2 WU bay cleanly into 3 vertical panes (`X = -8.4, -6.0, -1.2, +1.2, +6.0, +8.4`, note shift center bay sliding panel at `Z=28.38` open by `+2.4 WU` to invite outdoor breeze!).
   - `KitchenFrenchTrim` (`mats["platinum"]`): sleek bottom threshold `(0.0, 0.04, 28.6, 21.8, 0.08, 0.44)` and sliding handle bars.
   - `KitchenFrenchGlass` (`mats["glass"]`): 3 clear glass panels covering Left bay `(-7.2, 4.0, 28.6, 7.1, 7.75, 0.04)`, slid Center bay `(2.2, 4.0, 28.38, 7.1, 7.75, 0.04)`, and Right bay `(7.2, 4.0, 28.6, 7.1, 7.75, 0.04)`.
3. **East Culinary Tall Wall (`X in [12.65, 14.80], Z in [15.8, 28.2], Y in [0, 8.80]`)**:
   - `KitchenTallUpperWall` (`mats["graphite_slate"]`): continuous upper fascia `(13.72, 8.03, 22.0, 2.15, 1.54, 12.6)` + `KitchenTallWallInlays` (`mats["platinum"]` horizontal reveal at `Y=7.26`).
   - **North Bay (`Z in [15.8, 19.35]`) — Dual-Zone Wine & Champagne Cellar**:
     - Hollow cavity frame (`mats["graphite_slate"]`: back `X=14.70`, top `Y=7.22`, bottom `Y=0.16`, sides `Z=15.85` & `19.32`), `KitchenWineCellarDoor` (`mats["glass_smoke"]` at `X=12.68`), `KitchenWineCellarLight` (`mats["warm_led"]` vertical strips at `X=14.60`), 6 `KitchenWineShelves` (`mats["burgundy"]` at `Y=1.2, 2.2, 3.2, 4.2, 5.2, 6.2`), 24 horizontal `KitchenWineBottles` (`mats["wine_bottle"]` `r=0.10, h=0.82`) + `KitchenWineCaps` (`mats["platinum"]`).
   - **Center Bay (`Z in [19.40, 24.60]`)**: Call `build_south_french_fridge(ctx, mats)`.
   - **South Bay (`Z in [24.65, 28.15]`) — Pietra Grey Espresso & Granola Alcove**:
     - `KitchenSouthBase` (`mats["graphite_slate"]`, `(13.72, 1.15, 26.40, 2.10, 2.30, 3.50)`), `KitchenEspressoAlcove` (`mats["pietra_grey"]` counter slab at `Y=2.32`, back & side panels `Y=2.34..5.25`), `KitchenEspressoCove` (`mats["warm_led"]` at `Y=5.18`).
     - `KitchenEspressoMachine` (`mats["graphite_slate"]`, `(13.15, 2.86, 26.20, 0.96, 0.98, 1.15)`), `KitchenEspressoChrome` (`mats["platinum"]` front panel & hopper), `KitchenEspressoLevers` (`mats["brass"]` group handle extending to `X=12.65, Y=3.02`), `KitchenEspressoCup` (`mats["ceramic_white"]` scaled cup at `(12.65, 2.34, 26.20)`), `KitchenGranolaTray` (`mats["walnut_solid"]` `(13.05, 2.38, 27.35, 0.85, 0.08, 1.25)`) + golden `KitchenGranolaBars`.
4. **West Pietra-Grey Herb & Prep Gallery (`X in [-14.8, -12.6], Z in [17.2, 26.8], Y = 0..2.30`)**:
   - `KitchenHerbCounter` (`mats["graphite_slate"]`, `(-13.7, 1.10, 22.0, 2.0, 2.20, 9.6)`), `KitchenHerbCounterTop` (`mats["pietra_grey"]`, `(-13.65, 2.26, 22.0, 2.15, 0.14, 9.8)`), `KitchenHerbSink` (`mats["graphite_slate"]` basin) + `KitchenHerbFaucet` (`mats["platinum"]` high gooseneck at `X=-13.6, Y=2.32, Z=22.0`), 5 `KitchenHerbPots` (`mats["terracotta"]`, `r=0.34, h=0.40` along `Z=18.2..25.8`) + multi-cluster `KitchenHerbFoliage` (`mats["olive_leaf"]` & `olive_leaf_bright`), plus backlit `KitchenWestShelf` (`mats["pietra_grey"]` at `X=-14.1, Y=4.8, Z=22.0`).
5. **Monumental `10.6 x 2.80 x 2.32 WU` Pietra-Grey Waterfall Island (`center X = 3.2, Z = 19.4, top Y = 2.32`)**:
   - `KitchenIslandStone` (`mats["pietra_grey"]`): top slab `add_rounded_box(3.2, 2.24, 19.4, 10.6, 0.16, 2.80, bevel=0.04)` + West/East waterfall legs `(-1.93, 1.16, 19.4, 0.34, 2.32, 2.80)` & `(8.33, 1.16, 19.4, 0.34, 2.32, 2.80)` + `KitchenIslandCore` (`mats["graphite_slate"]`, `(3.2, 1.08, 19.85, 9.9, 2.16, 1.85)` leaving a North-facing cantilevered knee overhang!).
   - **Scaled Props on Island (`Y = 2.32`)**:
     - `KitchenTeppanyaki` (`mats["charcoal"]` `(5.8, 2.34, 19.6, 2.40, 0.04, 1.40)`) + `KitchenTeppanyakiBezel` (`mats["platinum"]`);
     - `KitchenSteakBoard` (`mats["walnut_solid"]` `(2.8, 2.38, 19.6, 1.65, 0.12, 1.25)`) + 3 marbled `KitchenRawSteaks` (`X in (2.3, 2.8, 3.3), Y=2.48`) + `KitchenSaltBowl` (`(3.85, 2.44, 19.6)`);
     - `KitchenPourBottle` (`mats["wine_bottle"]` at `(0.10, 2.32, 19.55)`, `add_lathe(..., [(0,0),(0.12,0),(0.12,0.48),(0.055,0.74),(0.045,0.88),(0,0.88)])`) + `KitchenPourFoil` (`mats["platinum"]`);
     - `KitchenWineDecanter` (`mats["crystal_glass"]` at `(-0.75, 2.32, 19.50)`) + `KitchenDecanterWine` (`mats["champagne_liquid"]` at `Y=2.42`) + `KitchenCoupes` at `(-0.55, 2.32, 18.85)` & `(-1.15, 2.32, 18.85)`;
     - `KitchenYogurtBowl` (`mats["ceramic_white"]` at `(1.2, 2.32, 18.55)`, `r=0.26, h=0.20`) + `KitchenBerriesBlue`/`Red`;
     - `KitchenBruceDish` (`mats["platinum"]` & `mats["pietra_grey"]` at `(-2.8, 0.02, 19.4)`, `r=0.38, h=0.16`).
   - **4 Nordic Storm-Slate Counter Stools (`KitchenBarStool*`)** along North side (`Z = 17.35, X in (-0.6, 1.9, 4.5, 7.0)`): `mats["graphite_slate"]` legs, `mats["platinum"]` footrest ring (`Y=0.62`), `mats["nordic_slate"]` padded seats (`Y=1.68`, `0.95 x 0.22 x 0.95`) & curved backrests (`Y=2.08`).
   - **Monumental `8.2 WU` Brushed-Platinum Linear Pendant (`KitchenLinearPendant`)**: `(3.2, 5.85, 19.4, 8.20, 0.16, 0.26)` + `KitchenPendantDiffuser` (`mats["warm_led"]` at `Y=5.76`) + twin suspension rods up to `Y=8.85`.

Return ONLY valid Python code (< 230 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_south_kitchen.py', doraise=True); "
                "print('OK mod_south_kitchen syntax')\""
            ),
        },
        {
            "name": "mod_south_terrace_mountains",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_south_terrace_mountains.py",
            "system": (
                "You are an AAA landscape & architectural courtyard artist. Build the South Phase-1 Pool & BBQ Courtyard "
                "AND a breathtaking 3-layer triangulated Alpine-Granite Crag Mountain Range (ZERO sphere/dome hills!) "
                "purely using crisp ridged-heightfield grids anchored to Y=-9.0. Keep under 190 lines."
            ),
            "prompt": f"""Create `scripts/penthouse_kit/mod_south_terrace_mountains.py` exporting `build_south_terrace_and_mountains(ctx, mats)`.
{PENTHOUSE_PRIM}

Everything sits SOUTH of `Z = 28.8` (`X in [-125, +125], Z in [28.8, 134.0]`, all well inside `SkyCyclorama` radius 148):
1. **Phase-1 Pool & BBQ Mountain Estate Courtyard (`Z in [28.8, 45.2], X in [-16.0, +16.0]`)**:
   - `SouthCourtyardDeck` (`mats["tundra_grey"]`): main stone terrace `(0.0, -0.14, 37.0, 32.8, 0.28, 16.4, uv_tile=3.0)`.
   - **Infinity-Edge Lap Pool (`X in [-2.5, +12.5], Z in [33.0, 41.5]`)**:
     - `SouthPoolCoping` (`mats["pietra_grey"]`): raised stone rim walls (`Y = -0.02..0.14`) framing the water basin (`X=5.0, Z=37.25, w=15.4, l=8.9`).
     - `SouthPoolWater` (`mats["pool_water"]`): shimmering crystalline turquoise surface `(5.0, 0.05, 37.25, 14.8, 0.06, 8.3)` + glowing underwater `SouthPoolCove` (`mats["warm_led"]` strip along inner North & West edges).
     - `SouthPoolLoungers` (`mats["graphite_slate"]` & `mats["nordic_slate"]`): 2 architectural sun loungers at `(1.5, 0.22, 31.2)` & `(5.5, 0.22, 31.2)` and 2 poolside lounges at `(-5.6, 0.22, 36.2)` & `(-5.6, 0.22, 39.2)`.
   - **Covered BBQ & Al-Fresco Dining Pavilion (`X in [-14.8, -8.4], Z in [31.5, 40.8]`)**:
     - `SouthBBQPergola` (`mats["graphite_slate"]`): 4 slim architectural columns (`Y=0..7.2`) at corners `(-14.4, 32.0), (-8.8, 32.0), (-14.4, 40.4), (-8.8, 40.4)` + louvered slatted roof canopy at `Y=7.2`.
     - `SouthBBQCounter` (`mats["pietra_grey"]`): outdoor grill island `(-13.4, 1.12, 36.2, 2.0, 2.24, 6.2)` + brushed stainless `SouthBBQGrill` (`mats["platinum"]` grill hood & grates at `(-13.4, 2.38, 36.2)`).
   - `SouthCourtyardGlass` (`mats["glass"]` + `mats["platinum"]` rail): infinity safety glass balustrade along `Z=44.8, X in [-16.0, +16.0], Y=0..2.2`.
2. **AAA 3-Layer Triangulated Craggy Alpine Granite Mountain Range (`Z in [50, 132], X in [-126, +126]`) — ZERO SPHERES!**:
   Write a clean helper `_crag_range(b, x_min, x_max, z_front, z_peak, z_back, nx, peak_fn)` that builds a 3D faceted mountain ridge mesh (`nx` columns x 4 Z profiles: `z_front` at `Y=-9.0` -> `z_foothill` at `0.42*H` -> `z_peak` crisp ridged crest `H` with `0.35*abs(sin(...))` sharp arête peaks & valley saddles -> `z_back` at `Y=-9.0`, triangulated seamlessly with `b.add_quad` / `b.add_tri_raw` facing `-Z` toward the kitchen window!):
   - **Layer 1 (`Z = 50..68`, `H = 12..19`) — Sub-Alpine Pine Foothills**: `SouthForestedFoothills` (`mats["coastal_pine"]`, `nx=44`) + 14 slender tapered cypress/fir silhouettes (`SouthCourtyardFirs` `mats["olive_leaf"]`) along the valley terrace edge (`Z = 47..53`).
   - **Layer 2 (`Z = 68..96`, `H = 22..36`) — Twin Dramatic Stratified Granite Massifs**: `SouthGraniteCrags` (`mats["alpine_granite"]`, `nx=52`), dipping into a scenic central glacial valley pass near `X = +1.5` (`H ~ 15`) and rising sharply to monumental craggy peaks on West (`X ~ -34`, `H ~ 35`) and East (`X ~ +42`, `H ~ 33`)!
   - **Layer 3 (`Z = 104..132`, `H = 34..48`) — High Atmospheric Distant Sierra**: `SouthDistantPeaks` (`mats["far_mist_mountain"]`, `nx=48`) framing the golden horizon sky behind the valley pass.

Return ONLY valid Python code (< 190 lines).""",
            "verify_cmd": (
                "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_south_terrace_mountains.py', doraise=True); "
                "print('OK mod_south_terrace_mountains syntax')\""
            ),
        },
    ]

    results = run_parallel_codegen(tasks, max_workers=4)
    print(f"Batch 13 finished: {len(results)} modules generated cleanly.")


if __name__ == "__main__":
    main()
