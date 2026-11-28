#!/usr/bin/env python3
"""DeepSeek Batch 16: East Estuary + Suspension Bridge + Skyscrapers, Partition Sporting Boiserie, Estate Chef Upgrade."""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from ds_worker import run_parallel_codegen

SYSTEM_MSG = (
    "You are a senior 3D computational architect for Three.js/GLB procedural scenes in Python. "
    "Output ONLY raw Python source code with zero markdown fences or prose. "
    "Keep the file STRICTLY UNDER 215 lines. Never use any tacky or forbidden words. "
    "CRITICAL MeshBuilder API rules:\n"
    "- b = ctx.mb(name, mats[mat_key])\n"
    "- b.add_box(cx, cy, cz, sx, sy, sz, rot_y=0.0, uv_tile=1.0)  # NEVER pass rot_x or rot_z!\n"
    "- b.add_rounded_box(cx, cy, cz, sx, sy, sz, bevel=0.04, rot_y=0.0, uv_tile=1.0)  # NEVER pass rot_x or rot_z!\n"
    "- b.add_cylinder(cx, y0, cz, r_bot, r_top, h, segs=16, rot_x=0.0, rot_y=0.0, rot_z=0.0, cap_top=True, cap_bot=True)  # y0 is BOTTOM!\n"
    "- b.add_sphere(cx, cy, cz, rx, ry, rz, rings=8, segs=12)\n"
    "- b.add_lathe(cx, y0, cz, [(r, y_off), ...], segs=16)  # y0 is base!\n"
    "- b.add_quad(p0, p1, p2, p3, uv_scale=(1.0, 1.0), flip=False)\n"
    "- b.add_curved_tube(pts, radii, segs=10)\n"
    "- b.add_tri_raw(p0, p1, p2, uv0, uv1, uv2, n0, n1, n2)\n"
)

def _smoke_cmd(mod_name, fn_name, required_names):
    req_repr = repr(required_names)
    code = f"""
import sys
sys.path.insert(0, 'scripts')
lines = open('scripts/penthouse_kit/{mod_name}.py').readlines()
assert len(lines) < 220, f'Too many lines: {{len(lines)}}'
from penthouse_kit.{mod_name} import {fn_name}
seen = set()
class MB:
    def add_box(self, *a, rot_y=0.0, uv_tile=1.0): assert len(a) == 6
    def add_rounded_box(self, *a, bevel=0.04, rot_y=0.0, uv_tile=1.0): assert len(a) == 6
    def add_cylinder(self, *a, segs=16, rot_x=0.0, rot_y=0.0, rot_z=0.0, cap_top=True, cap_bot=True): assert len(a) == 6
    def add_sphere(self, *a, rings=8, segs=12): assert len(a) == 6
    def add_lathe(self, *a, segs=16): assert len(a) == 4
    def add_quad(self, *a, uv_scale=(1.0, 1.0), flip=False): assert len(a) == 4
    def add_curved_tube(self, *a, segs=10): assert len(a) == 2
    def add_tri_raw(self, *a): assert len(a) == 9
class Ctx:
    def mb(self, n, m):
        seen.add(n)
        return MB()
class MD(dict):
    def __getitem__(self, k): return k
{fn_name}(Ctx(), MD())
missing = [r for r in {req_repr} if r not in seen]
assert not missing, f'Missing meshes: {{missing}}'
print('SMOKE OK', len(seen), 'lines', len(lines))
""".strip()
    return ["python3", "-c", code]

TASKS = [
    {
        "name": "mod_east_river_bridge_vista",
        "out_path": "scripts/penthouse_kit/mod_east_river_bridge_vista.py",
        "system": SYSTEM_MSG,
        "verify_cmd": _smoke_cmd(
            "mod_east_river_bridge_vista",
            "build_east_river_bridge_vista",
            ["EastRiverChannel", "EastEstuaryMouth", "WestBluffTerrain", "EastPeninsulaTerrain",
             "EastRiverBridge", "EastBridgeTowers", "EastBridgeCables", "EastCitySkyscrapers", "RiverYachts"],
        ),
        "prompt": """Rewrite `scripts/penthouse_kit/mod_east_river_bridge_vista.py` defining ONLY `build_east_river_bridge_vista(ctx, mats)` (<210 lines).
Goal: Replace all floating river strips and cartoonish blocks with a physically grounded, breathtaking architectural Estuary-to-Ocean Marina, Suspension Bridge, and Dark-Glass Financial Skyline seen through the East curved glass (facing +X and North-East out from X=42.8).
Exact Materials available: `river_water`, `coastal_foam`, `headland_rock`, `travertine`, `coastal_pine`, `sail_canvas`, `obsidian_bezel`, `bridge_steel`, `steel`, `warm_led`, `city_facade`, `brass`.

MUST follow exact shared vertical datum (Open ocean & estuary sit at `Y = -8.50` in `mod_terrace_sky.py`):
1. West Bluff & Coastal Seawall (`X in [36.0, 54.0], Z in [-24.0, +72.0]`):
   - `WestBluffTerrain` (`headland_rock`): rocky terraced cliff rising from seabed `Y=-9.5` up to promenade top `Y=-5.2`, plus granite parapet seawall (`travertine`) along `X=53.5` from `Z=-22` to `+68` with warm bollard `warm_led` lights.
   - Sloped riparian pine & reed banks (`coastal_pine`) stepping down smoothly to the waterline at `Z in [-24, -8]`.
2. River Channel + Hyperbolic Estuary Transition (`Y = -8.48` river upstream fading cleanly into `Y = -8.50` ocean at `Z < -18`):
   - `EastRiverChannel` (`river_water`): 14x18 subdivided water grid spanning `X in [52.0, 96.0], Z in [-18.0, +88.0]` at exact `Y = -8.48`, flaring outward toward `Z = -18`.
   - `EastEstuaryMouth` (`coastal_foam` & `headland_rock`): shallow estuary sandbars (`Y = -8.62 .. -8.35`) + crescent breakwater jetties at `(56, -22)` & `(92, -26)` with lighthouse beacon (`warm_led`) + coastal foam ripples blending the turquoise river mouth into open ocean at `Z = -18 .. -48`.
3. East Stepped Peninsula Podium (`X in [88.0, 195.0], Z in [-28.0, +95.0]`):
   - `EastPeninsulaTerrain` (`headland_rock` + `travertine`): grounded layered bedrock from `Y=-9.5` up to `-4.2`, topped with a grand granite waterfront embankment promenade along `X=90.5`, green parkway plinths (`coastal_pine`), and wide podium plazas so ZERO skyscrapers sit in water!
4. Authentic Architectural Suspension Bridge (`EastRiverBridge`, `EastBridgeTowers`, `EastBridgeCables`):
   - Spans West abutment `(50.0, -4.5, -8.0)` cleanly to East abutment `(94.0, -4.5, -18.0)` across the estuary mouth! Calculate exact midpoint, length `L ≈ 45.12`, and `rot_y = math.atan2(dx, dz)`.
   - Twin submerged stone caisson piers (`travertine`) anchored deep into seabed `Y = -10.5` up to `-3.8` at `t=0.24` and `t=0.76` along the span.
   - Twin Art-Deco tapered H-frame suspension towers (`bridge_steel`, rising from `Y=-4.0` up to `Y=+14.5`) with TWO slender shafts (`r=0.42 -> 0.24`) straddling the deck (`±2.4m` perpendicular offset) joined by 3 horizontal steel cross-braces + finial beacons (`warm_led`).
   - Slender box-girder road deck (`obsidian_bezel`, width `4.4m`) + crisp double warm deck edge strips (`warm_led`) + center median (`steel`).
   - Two TRUE parabolic catenary main cables (`EastBridgeCables`, `steel`, using `add_curved_tube` with 15 control points from abutment anchor `Y=-4.2` over tower saddle `Y=+14.2`, dipping smoothly to `Y=-0.8` at midspan, then over 2nd tower `Y=+14.2` to East anchor `Y=-4.2`, slender radius `0.065`)!
   - 22 slender vertical suspender cables (`r=0.016`, `steel`) connecting the exact parabolic cable points straight down to the road deck!
5. Modern Dark-Glass Financial Skyline (`EastCitySkyscrapers`, 16 tiered curtain-wall towers grounded on `EastPeninsulaTerrain` at `X in [98..182], Z in [-22..+84]`):
   - Use `city_facade` for tall glass shafts (`Y=-4.5` base up to heights `Y=+16 .. +42`) + `travertine` podium bases + `obsidian_bezel` setbacks/fins + subtle `steel` crown spires + tiny `warm_led` aviation/crown halos (NO bright orange block cubes!).
6. Marina Vessels (`RiverYachts`):
   - 3 sleek motor yachts (`sail_canvas` hull + `obsidian_bezel` cabins) cruising north out of the estuary mouth at `(66, -8.46, -24)`, `(75, -8.46, -42)`, `(62, -8.46, +18)`.""",
    },
    {
        "name": "mod_east_piano_sport_wing",
        "out_path": "scripts/penthouse_kit/mod_east_piano_sport_wing.py",
        "system": SYSTEM_MSG,
        "verify_cmd": _smoke_cmd(
            "mod_east_piano_sport_wing",
            "build_east_piano_sport_wing",
            ["EastSalonFloor", "CurvedPanoramicGlass", "GrandPianoCase", "PuttingGreenTurf",
             "SportWallBoiserie", "SportCredenza", "TennisDisplay0", "TennisStrings0",
             "DressageSaddle", "SaddleBridle", "GolfDriver0", "GolfTourBag"],
        ),
        "prompt": """Update `scripts/penthouse_kit/mod_east_piano_sport_wing.py` defining ONLY `build_east_piano_sport_wing(ctx, mats)` (<215 lines).
Exact Materials: `oak`, `marmorino`, `warm_led`, `brass`, `charcoal`, `travertine`, `glass`, `cream_wool`, `ebony_piano`, `copper_cook`, `ivory`, `sheet_music`, `warm_bulb`, `black_leather`, `ceramic_white`, `olive_leaf`, `walnut_solid`, `racing_green`, `steel`, `platinum`, `chrome`, `saddle_tan`, `porcelain_white`, `optic_yellow`.

Preserve items 1, 2, 3 intact:
1. Shell (`EastSalonFloor`, `EastCeiling`, `EastCove`, `EastSouthWall` at `Z=15.6`, `EastChandelier`) + 10-bay Curved Glass (`curve = [(15.0,-16.0),(20.8,-17.0),(26.6,-17.4),(32.0,-16.6),(36.8,-14.2),(40.2,-10.2),(42.2,-5.2),(42.8,0.0),(42.2,5.4),(40.8,10.6),(39.5,15.4)]`, `CurvedGlassMullions`, `CurvedWindowSill`, `CurvedPanoramicGlass`, `CurvedTransom`).
2. 9-ft Concert Grand Piano by curved window (`PianoRug`, `GrandPianoCase`, `PianoLyre`, `PianoOpenLid`, `PianoProp`, `GrandPianoHarp`, `PianoStrings`, `PianoKeys`, `PianoBlackKeys`, `GrandPianoSheetMusic`, `PianoLamp`, `PianoBench`, `PianoFigTree`, `PianoFigTrunk`, `PianoFigFoliage`).
3. Putting Green (`PuttingTrim`, `PuttingGreenTurf`, `PuttingBunker`, `PuttingCups`, `PuttingFlags`, `GolfBalls`, `GolfPutter`) at `X=30.1, Z=7.6` (`18.2x11.2`). REMOVE old `GolfClubBoard`, `GolfBoardWash`, `GolfRack`, `TennisVitrine*`, `EquestrianVitrine*` completely!

NEW Item 4 — Unified 3-Bay Partition-Backed Sporting Collector Wall (strictly along the EAST back of the TV/Fireplace partition wall, `X in [14.70, 16.95], Z in [-6.80, +3.20], Y in [0.0, 8.60]`, facing `+X` into the Piano & Putting wing! Leave `Z < -7.0` and `Z > +3.4` 100% open for the twin portals!):
- `SportWallBoiserie` (`walnut_solid` & `marmorino` framing): recessed architectural paneling against `X=14.75` (`Z in [-6.8, +3.2], Y=0..8.6`), divided by vertical fluted walnut pilasters (`X=15.02`) at `Z in (-6.7, -3.45, -0.05, +3.15)` into 3 gallery bays (`2.8m` wide each), plus a long Travertine plinth/credenza (`SportCredenza` at `X=15.65, Y=0.72, Z=-1.80, sx=1.55, sy=1.44, sz=9.80` with walnut drawer fronts + `warm_led` cove strip at `Y=8.25` & `1.50`!).
- **Bay 1 (`Z in [-6.55, -3.65]`, Pro Tennis)**:
  * Backlit Marmorino panel (`X=14.90`), crossed twin Pro Rackets mounted cleanly facing `+X` (`TennisDisplay0` & `TennisDisplay2` at `X=15.18, Y=4.85, Z=-5.10`, tilted ±0.48 rad in YZ plane using `rot_x=sgn*0.48` on cylinder shafts and elliptical frame quads in `YZ` at `X=15.18`, plus crisp white `TennisStrings0`/`TennisStrings2` mesh grids in `YZ`!).
  * `TennisBasket` (`brass`) + 5 `TennisBalls` (`optic_yellow`) perched on credenza top `Y=1.46` at `Z=-5.10, X=15.70`.
- **Bay 2 (`Z in [-3.30, -0.20]`, Equestrian Dressage Tack)**:
  * Backlit Marmorino panel (`X=14.90`).
  * Mounted walnut saddle horse on credenza top (`X=15.70, Y=1.45, Z=-1.75`): crisp white quilted `SaddlePad`, sculpted Cognac leather `DressageSaddle` (`saddle_tan`, cantle/pommel spheres, knee rolls, long vertical flaps), dangling `SaddleStirrup` leathers & steel irons (`steel`), mounted `SaddleBridle` + brass `SaddleBit` (`X=15.12, Y=5.35, Z=-1.75`), riding `SaddleHelmet` on upper shelf, and tall `SaddleBoot` pair at `Z=-2.65` & `-0.85`.
- **Bay 3 (`Z in [+0.05, +3.05]`, Custom Forged Golf Bag & Club Rack)**:
  * Backlit Marmorino panel (`X=14.90`) + horizontal walnut rail at `Y=5.70` & `Y=1.80` (`X=15.12`) holding 9 forged clubs spaced along `Z in [+0.45..+2.75]` (`GolfDriver0..2` in `platinum`, `GolfIron0..4` in `chrome`, `GolfMallet` putter in `brass`) with distinct clubheads resting cleanly at `Y=1.95`!
  * `GolfTourBag` (`racing_green` leather cylinder + `saddle_tan` `GolfBagStrap` + extra club heads peeking out) standing neatly beside Bay 3 at `(16.15, 0.0, 2.55)` inside the credenza bay envelope (never protruding into `Z > 3.25` portal!).""",
    },
    {
        "name": "mod_south_cellar_and_cookware",
        "out_path": "scripts/penthouse_kit/mod_south_cellar_and_cookware.py",
        "system": SYSTEM_MSG,
        "verify_cmd": _smoke_cmd(
            "mod_south_cellar_and_cookware",
            "build_south_cellar_and_cookware",
            ["Bottle_DomPerignon", "Bottle_Lafite", "LeCreusetDutchOven", "MauvielCopperStockpot",
             "CastIronGrillPan", "DryAgeSteakCabinet", "DryAgeSaltWall", "WolfPotFiller",
             "DamascusKnifeRack", "BerkelSlicer", "MarbleMortar"],
        ),
        "prompt": """Upgrade `scripts/penthouse_kit/mod_south_cellar_and_cookware.py` defining ONLY `build_south_cellar_and_cookware(ctx, mats)` (<215 lines).
Exact Materials: `walnut_fluted`, `obsidian_bezel`, `rift_oak`, `warm_led`, `crystal_glass`, `wine_bottle`, `brass`, `champagne_liquid`, `amber_wine`, `wolf_red`, `burgundy_glass`, `steel`, `prestige_wine_labels`, `glass`, `le_creuset_red`, `copper_cook`, `charcoal`, `steak_marbled`, `himalayan_salt`, `warm_bulb`, `porcelain_white`, `travertine`, `gold_brass`.

Must keep existing Items 1-3 AND add Items 4-5 ultra-luxury culinary hardware:
1. Diverse 8-Estate Wine Cellar (`Z in [25.2..34.8]`, `X in [-14.7..-12.3]`):
   Keep all 8 distinct estate bottles (`DomPerignon`, `Cristal`, `Krug`, `DRC`, `Petrus`, `Lafite`, `OpusOne`, `Yquem`) on lower & upper shelves (`Y=2.25, 3.85`) with unique bottle lathe profiles, distinct capsule colors, UV-mapped `prestige_wine_labels` quads, `WineCrates`, `CrystalDecanters`, `MagnumCradle`, `WineCellarGlass`.
2. 7-Piece Cookware Suite on Wolf 60" Dual-Oven Range (`Y=2.44` grates, `X in [-14.4..-12.6]`, `Z in [18.3..22.7]`):
   Keep `LeCreusetDutchOven` + lid + brass knob (`-13.05, 18.85`), `MauvielCopperStockpot` (`-14.00, 18.95`), `CastIronGrillPan` + `WolfRibeyes` (`-13.45, 20.50`), `CarbonSteelWok` (`-13.00, 22.05`), `StainlessSaucier` (`-14.00, 21.95`), plus `BackSplashPotRail`, `HangingCopperPan`, `BrassUtensils`!
3. NEW: **Articulated Brass Wall Pot-Filler (`WolfPotFiller`)** mounted over the Wolf burners at `(-14.55, 3.65, 20.50)`:
   Swivel brass wall escutcheon + articulated twin swing arms (`brass` cylinders & elbow spheres) extending toward `(-13.75, 3.65, 20.50)` with turncock spout!
4. NEW: **Backlit Himalayan Pink-Salt Dry-Aging Steak Cabinet (`DryAgeSteakCabinet`)** replacing the plain left Wolf column at `Z in [15.70, 17.40], X in [-14.65, -12.35], Y in [0.0, 8.6]`:
   - `obsidian_bezel` outer cabinet frame (`-13.50, 4.30, 16.55`) with brushed `steel` vertical door handle (`X=-12.30`) and temperature digital glow badge (`warm_bulb` at `-12.32, 6.4, 16.55`).
   - Recessed backlit Himalayan Salt Block Wall (`DryAgeSaltWall`, `himalayan_salt`, `-14.48, 4.30, 16.55, 0.14, 5.2, 1.35`) framed by `warm_led` vertical side strips!
   - 3 stainless wire racks (`Y=2.6, 3.9, 5.2`, `steel`) holding 6 thick marbled prime tomahawk/ribeye cuts (`steak_marbled`) aging inside, behind crystal-clear front glass (`glass` at `X=-12.36`).
5. NEW: **West & Island Private-Chef Hardware** (avoid obstructing island prep zone `X in [-4..+3]` & Wolf center `Z=20.5`):
   - **Damascus Chef Knife Magnetic Strip (`DamascusKnifeRack`)** mounted neatly on backsplash at `(-14.56, 3.18, 22.8..24.4)`: `walnut_fluted` bar (`sz=1.6`) + 7 distinct Damascus steel blades (`steel`, lengths `0.42..0.20`, curved tips) hanging from vertical walnut bolsters!
   - **Bespoke Crimson Flywheel Prosciutto Slicer (`BerkelSlicer`)** on the East end of the Pietra Grey Island (`Y=2.40` countertop top, `X=6.20, Z=20.50`): `wolf_red` cast-iron pedestal + angled cradle, gleaming `steel` rotary blade disk (`r=0.38`), and signature outer red spoke flywheel (`r=0.42` with `gold_brass` knob) + receiving tray!
   - **Island Culinary Mise-en-Place (`MarbleMortar`)**: carved `travertine` mortar & pestle at `(5.0, 2.40, 22.1)`, twin brass olive oil cruets (`brass` at `(5.4, 2.40, 18.8)`), and hammered `steel` truffle/caviar cloche (`(4.2, 2.40, 18.9)`).""",
    },
]

if __name__ == "__main__":
    print("[Batch 16] Running parallel DeepSeek codegen...")
    res = run_parallel_codegen(TASKS, batch_name="batch16_estuary_chef", max_workers=3, max_retries=3)
    print(f"[Batch 16] Finished {len(res)} modules cleanly.")
