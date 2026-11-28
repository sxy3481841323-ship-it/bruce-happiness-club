#!/usr/bin/env python3
"""Retry just mod_south_kitchen (without dining) + mod_south_dining as twin clean <190-line modules."""
from ds_worker import run_parallel_codegen

COMMON_RULES = """
STRICT CODE RULES:
1. Keep total file length concise (< 190 lines) — NEVER repeat decimals or long loops.
2. Primitives from prim_lib.py ONLY:
   ctx.mb(name, mat_idx) -> b.add_box(cx,cy,cz,sx,sy,sz,uv_tile=0,rot_y=0),
   b.add_rounded_box(cx,cy,cz,sx,sy,sz,bevel=0.04,uv_tile=0,rot_y=0),
   b.add_cylinder(cx,y0,cz,r_bot,r_top,h,segs=16,rot_x=0,rot_z=0,cap_top=True,cap_bot=True),
   b.add_sphere(cx,cy,cz,rx,ry,rz,rings=10,segs=16),
   b.add_lathe(cx,y0,cz,profile_list,segs=18),
   b.add_curved_tube(spine_pts,radii,segs=10),
   b.add_quad(p0,p1,p2,p3,uv_scale=(1,1),flip=False).
3. NO forbidden words. Return ONLY raw Python code, no markdown fences.
"""

KITCHEN_ONLY_PROMPT = """
Write scripts/penthouse_kit/mod_south_kitchen.py (< 195 lines) defining build_south_kitchen(ctx, mats).
Import and call build_south_fridge(ctx, mats) and build_south_dining(ctx, mats) inside build_south_kitchen(ctx, mats):
  from .mod_south_fridge import build_south_fridge
  from .mod_south_dining import build_south_dining
Build Zone 4A South Culinary Hall (Z in [15.4, 36.0], X in [-15.2, +15.2], Y in [0.0, 18.6]):
1. Shell & Preserved Black French Triple-Bay Folding Glass Doors:
   - Floor 'SouthKitchenFloor' (mats['tundra_grey'], 30.4 x 0.14 x 20.6 at (0, -0.07, 25.7)).
   - Ceiling (Y=18.66, mats['marmorino'] + mats['warm_led'] perimeter cove), East & West walls (X=+-14.9, mats['marmorino']), light warm-grey upper bulkhead fascia (mats['warm_grey_upper'], Y=6.8..8.8) along East/West perimeter.
   - Black Steel French Triple-Bay Glass Doors at Z=36.0: pillars/transoms/rails in mats['charcoal'], glass panels 'KitchenFrenchGlass' in mats['glass'] spanning X in [-14.2, +14.2], Y in [0.05, 9.10] looking out onto Pool Terrace.
2. East Wall Extended Coffee & Breakfast Station (Z in [24.1, 34.8], X in [12.1, 14.75]):
   - Tall mats['graphite_slate'] (#565B64) + warm_grey_upper surround with a wide backlit walnut recessed open-shelf niche ('CoffeeNicheWalnut', mats['walnut_fluted']) + mats['pietra_grey'] counter/backsplash.
   - 'KitchenEspressoMachine' (mats['steel']) at (12.82, 2.38, 28.5), burr grinder, gooseneck kettle, porcelain espresso cups, glass granola jars ('KitchenGranolaJars').
3. West Wall 60-inch Wolf Dual-Oven Red-Knob Gas Range & Wall Hood (Z in [16.2, 24.8], X in [-14.75, -12.0]) — NO West plants:
   - Tall charcoal-grey side columns + 'WolfBacksplash' in mats['pietra_grey'] (Z in [16.2..24.8], Y in [2.25..6.35]) + clean flush hood canopy in mats['warm_grey_upper'] (Y in [6.35..8.30]) with warm_led under-strip.
   - 4.60 WU wide brushed-steel 'WolfRangeBody' at (-13.10, 1.16, 20.5) with twin steel oven doors, dark obsidian glass windows (mats['obsidian_bezel']), steel handles, 6 cast-iron grates, central griddle, and 8 crimson knobs ('WolfRedKnobs', mats['wolf_red'] at X=-11.96, Z in [18.5..22.5]).
4. West Wall 8-Estate Grand-Cru Wine Cellar (Z in [25.2, 34.8], X in [-14.75, -12.15]):
   - Bronze/glass walnut cellar ('WineCellarCase') with warm_led illumination holding 32 bottles ('PrestigeWineBottles', mats['prestige_wine_labels'] + 'wine_bottle' necks) + stemware & decanters.
5. Zone 4A Center Chef Prep Island & Suspended Stainless Chimney Hood (X in [-3.4, +7.8], Z in [18.8, 22.0]):
   - Smoked-oak base ('KitchenIslandOak', mats['rift_oak'], Y=0.05..2.22) + cascading 'KitchenIslandStone' waterfall slab (mats['pietra_grey'], 11.2 x 0.16 x 3.2 at Y=2.30 + waterfall legs).
   - 3 black-leather & brass sled-base Bar Stools ('KitchenBarStools') at Z=17.95, X=-1.2, 2.0, 5.2 (matching Photo 1!).
   - Suspended Brushed-Stainless T-Chimney Island Hood above island ('IslandRangeHood', mats['steel'], chimney shaft at (2.0, 13.4, 20.4) 2.2 x 10.2 x 1.2 + canopy at Y=7.90, 9.2 x 0.24 x 3.2 + 4 thin corner drop rods + warm_led glow strip).
   - Undermount sink & high-arc spring faucet (X=1.8, Z=20.4); maple butcher block ('KitchenSteakBoard') + forged knife + 3 steaks ('KitchenRawSteaks', mats['steak_marbled']) + pepper/salt mills; copper sauteuse skillet (mats['copper_cook']); matte-white 3-leg bowl with green limes; matte-black water pitcher; 4 crystal stems + twin Evian glass bottles + 'KitchenPourBottle'/'KitchenPourFoil'/'KitchenDecanterWine' at (0.10, 2.38, 19.55).
"""

DINING_PROMPT = """
Write scripts/penthouse_kit/mod_south_dining.py (< 165 lines) defining build_south_dining(ctx, mats).
Build Zone 4B Formal Separate Rectangular Dining Room in the South Wing (Z in [27.4, 34.6], X in [-7.2, +7.2], facing the Z=36.0 French triple-bay terrace glass doors & Alpine peaks):
1. Area Rug:
   - Woven architectural wool area rug 'DiningAreaRug' (mats['rug_2f'] or mats['boucle'], 13.6 x 0.03 x 7.6 at (0.0, 0.02, 31.0)).
2. Formal Rectangular Charcoal-Grey Marble Dining Table:
   - Twin fluted bronze-and-oak pedestals at (X=+-3.6, Y=1.02, Z=31.0) in mats['obsidian_bezel'] / mats['rift_oak'].
   - Monumental rectangular chamfered dining slab 'DiningTableMarble' (mats['pietra_grey'], 11.4 x 0.14 x 3.50 at (0.0, 2.04, 31.0)) with thin brass edge bevel inlay.
3. 8 Tailored Boucle & Walnut Dining Armchairs:
   - 3 chairs along North long side (Z=28.8, X=-3.4, 0.0, +3.4 facing +Z),
   - 3 chairs along South long side (Z=33.2, X=-3.4, 0.0, +3.4 facing -Z),
   - 2 Host/Hostess armchairs at West & East ends (X=-6.2 & +6.2, Z=31.0).
   - Each chair built cleanly with tapered walnut legs (mats['rift_oak']), brass sabots, curved cream boucle seat cushion & wrap-around backrest (mats['boucle']).
4. Formal Table Settings & Centerpiece:
   - 8 stoneware dinner plates + charger rims + linen napkins ('DiningPlaceSettings', mats['ceramic_white'] & mats['brass']) + 8 tall crystal wine stems (mats['crystal_glass']).
   - Central sculptural Roman travertine vase ('DiningCenterpiece', mats['travertine']) + lush olive branches (mats['bark'] & mats['olive_leaf']) + pair of slim brass candlesticks (mats['brass'] & mats['warm_bulb']).
5. Twin Black-and-Brass Architectural Linear Dining Pendants:
   - Two sleek suspended matte-charcoal & brass linear pendants ('DiningChandeliers', mats['charcoal'], mats['brass'], mats['warm_led']) spanning X=-2.8..+2.8 at Z=31.0, Y=7.80 with slender ceiling suspension rods up to Y=18.6.
"""

JOBS = [
    {
        "name": "mod_south_kitchen",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_south_kitchen.py",
        "system": "You are an architectural 3D interior designer writing clean compact Python GLTF geometry.",
        "prompt": KITCHEN_ONLY_PROMPT + COMMON_RULES,
        "verify_cmd": "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_south_kitchen.py', doraise=True); print('OK mod_south_kitchen')\"",
    },
    {
        "name": "mod_south_dining",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_south_dining.py",
        "system": "You are an architectural 3D dining salon furniture modeler writing clean compact Python GLTF geometry.",
        "prompt": DINING_PROMPT + COMMON_RULES,
        "verify_cmd": "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_south_dining.py', doraise=True); print('OK mod_south_dining')\"",
    },
]

if __name__ == "__main__":
    run_parallel_codegen(JOBS, batch_name="batch14b_kitchen_dining", max_workers=2)
