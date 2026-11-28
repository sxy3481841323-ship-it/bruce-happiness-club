#!/usr/bin/env python3
"""Parallel DeepSeek codegen batch 14: Charcoal-Oak Kitchen, Wolf Range, 8-Estate Cellar, Dining, Pool, AAA Alps, East Piano & Sports Wing."""
from ds_worker import run_parallel_codegen

COMMON_RULES = """
STRICT CODE RULES:
1. Keep total file length concise (< 225 lines).
2. Primitives from prim_lib.py ONLY:
   ctx.mb(name, mat_idx) -> b.add_box(cx,cy,cz,sx,sy,sz,uv_tile=0,rot_y=0),
   b.add_rounded_box(cx,cy,cz,sx,sy,sz,bevel=0.04,uv_tile=0,rot_y=0),
   b.add_cylinder(cx,y0,cz,r_bot,r_top,h,segs=16,rot_x=0,rot_z=0,cap_top=True,cap_bot=True),
   b.add_sphere(cx,cy,cz,rx,ry,rz,rings=10,segs=16),
   b.add_lathe(cx,y0,cz,profile_list,segs=18),
   b.add_curved_tube(spine_pts,radii,segs=10),
   b.add_quad(p0,p1,p2,p3,uv_scale=(1,1),flip=False),
   b.add_tri_raw(p0,p1,p2,uv0,uv1,uv2,n0,n1,n2).
3. Keep all identifiers and strings clean ASCII-safe or clean code without prohibited words.
4. Return ONLY valid raw Python code (< 225 lines), no markdown fences.
"""

TEX_PROMPT = """
Write scripts/penthouse_kit/tex_kitchen_surfaces.py (< 225 lines).
Include Pillow (Image, ImageDraw, ImageFilter, ImageFont) & math functions:
Keep exact signatures & quality for:
- _fbm(x, y, seed=0)
- _lerp(c0, c1, t)
- make_pietra_grey_marble_tex(w=1024, h=1024): deep charcoal-grey marble (#3A3D42) with crisp white-silver diagonal lightning veins.
- make_tundra_grey_floor_tex(w=1024, h=1024): cool light warm-grey stone slabs (#B5B2AB) with subtle mortar lines & mineral grain.
- make_organic_dairy_label_tex(w=512, h=256): clean cream/emerald organic pasture milk & Greek yogurt label graphic.
Update:
- make_platinum_slate_tex(w=512, h=512): warm charcoal-dove grey cabinetry (#565B64, RGB 86,91,100) with subtle brushed vertical grain and delicate rail shadow (NOT jet black).
- make_smart_panel_tex(w=1024, h=680): ultra-crisp deep OLED obsidian #070A10 background (zero pale haze!) with luminous brass #D6A954 circular climate ring '21.5 C', sharp white scene buttons ('Arrival', 'Chef Prep', 'Piano Salon', 'Poolside'), dimmer sliders, and crisp card outlines.
Add two NEW texture functions:
- make_prestige_wine_labels_tex(w=1024, h=512): 4 cols x 2 rows atlas of 8 distinct estate wine/champagne labels with clear titles & heraldic crests:
  Row0: ['DOM PERIGNON', 'CRISTAL', 'KRUG', 'ROMANEE-CONTI']
  Row1: ['PETRUS', 'CH. LAFITE', 'CH. MARGAUX', 'OPUS ONE']
  Vary label foil & paper backgrounds across the 8 grid cells.
- make_aaa_snow_granite_mountain_tex(w=2048, h=1024): Vertical terrain texture mapped monotonically from y=h-1 (V=0 bottom timberline) to y=0 (V=1 glacier peaks):
  * V in [0.00..0.28]: Deep emerald evergreen forest (#183124..#2E4A36) with moss & moraine stone
  * V in [0.28..0.66]: Chiseled Dolomite dark granite/limestone facets (#404550..#6E7480) with diagonal geological fissures and couloir snow ribs
  * V in [0.66..1.00]: Crisp glacial snow & ice cliffs (#D7E3F0 cool shadow to #FFF8EE sunlit crest).
"""

FRIDGE_PROMPT = """
Write scripts/penthouse_kit/mod_south_fridge.py (< 215 lines) with build_south_fridge(ctx, mats).
Build a monumental 7.80 WU wide x 7.90 WU tall built-in Double-Door Chef Refrigerator flush into East Wall of South Kitchen:
  X in [12.35, 14.75], Z in [16.00, 23.80], Y in [0.16, 8.06] (doors hinged cleanly at X=12.35 around Z=16.05 & Z=23.75).
Include:
1. Full-height cabinet reveal frame in mats['graphite_slate'] (#565B64), upper transom fascia Y in [6.80..8.06] in mats['warm_grey_upper'], stainless louver vent.
2. Articulated double doors facing -X:
   - Mesh 'FridgeDoorLeft': X=12.40, Y=4.05, spanning Z in [16.05, 19.86], Y in [1.45, 6.65] (steel frame + mats['graphite_slate'] inset + 4.2 WU brass handle at Z=19.35).
   - Mesh 'FridgeDoorRight': X=12.40, Y=4.05, spanning Z in [19.94, 23.75], Y in [1.45, 6.65] (steel frame + mats['graphite_slate'] inset + 4.2 WU brass handle at Z=20.45).
3. Illuminated interior pantry (warm_led back glow + glass shelves at Y=2.15, 3.25, 4.35, 5.45 across Z=16.4..23.4, X=12.7..14.4):
   - 5 tall organic whole-milk glass carafes & cartons (mats['dairy_label'])
   - 8 porcelain unsweetened Greek yogurt tubs (mats['porcelain_white'] + cobalt caps)
   - Fresh fruits: apples (red_apple), avocados (herb_green), lemons & oranges (lemon_gold) in bowls
   - 2 crystal veggie crisper bins filled with fresh produce + 2 bottom 0C BioFresh pull-out drawers (Y in [0.22..1.38], mats['graphite_slate'] + mats['steel'] + brass bar handles).
"""

KITCHEN_PROMPT = """
Write scripts/penthouse_kit/mod_south_kitchen.py (< 225 lines) with build_south_kitchen(ctx, mats).
Build the expanded South Culinary Hall & Separate Rectangular Dining Room spanning Z in [15.4, 36.0], X in [-15.2, +15.2], Y in [0.0, 18.6]:
1. Hall Shell & Preserved Black French Doors:
   - Floor 'SouthKitchenFloor' (mats['tundra_floor'], 30.4 x 0.14 x 20.6 at (0, -0.07, 25.7)).
   - Ceiling (Y=18.66, marmorino + warm_led cove), Side walls (X=+-14.9, marmorino), light warm-grey upper fascia (mats['warm_grey_upper'], Y=6.8..8.8) on East/West walls.
   - Black Steel-Framed French Triple-Bay Folding Glass Doors at Z=36.0 (mats['window_frame'] mullions/transoms + mats['glass'] panes, Y in [0.05..9.10]), looking straight onto Pool Courtyard!
2. East Wall Extended Coffee & Breakfast Bar (Z in [24.1, 34.8], X in [12.1, 14.75]):
   - Tall mats['graphite_slate'] & warm_grey_upper cabinetry + wide backlit recessed walnut open-shelf niche + marble_grey counter/backsplash.
   - Dual-boiler brushed-steel Espresso Machine at (12.82, 2.38, 28.5), burr grinder, kettle, cups, stacked bowls, granola jars.
3. West Wall 60-inch Wolf Dual-Oven Red-Knob Gas Range & Hood (Z in [16.2, 24.8], X in [-14.75, -12.0]) + NO West plants:
   - Charcoal-grey flanking columns + tall marble_grey veined backsplash (Z in [16.2..24.8], Y in [2.25..6.35]) + warm_grey_upper flush hood soffit (Y in [6.35..8.30]) + warm_led light.
   - 4.60 WU wide brushed-steel 'WolfRangeBody' at (-13.10, 1.16, 20.5) with twin steel oven doors, obsidian_bezel glass windows, steel handles, 6 grates, central griddle, and 8 crimson knobs ('WolfRedKnobs', mats['wolf_red'] at X=-11.96, Z in [18.5..22.5]).
4. West Wall 8-Estate Wine Cellar (Z in [25.2, 34.8], X in [-14.75, -12.15]):
   - Tall bronze/glass walnut cellar with warm_led strips, holding 32 horizontal/tilted wine bottles ('PrestigeWineBottles', mats['prestige_wine_labels']) mapping UVs across the 8 grid cells + stemware & decanters.
5. Zone 4A Center Chef Prep Island & Suspended Stainless Chimney Hood (X in [-3.4, +7.8], Z in [18.8, 22.0]):
   - Smoked-oak ('walnut') fluted base + 'marble_grey' waterfall countertop (11.2 x 3.2 x 2.36 WU).
   - 3 black-leather & brass sled-base Bar Stools along North side (Z=17.95, X=-1.2, 2.0, 5.2).
   - Suspended Brushed-Stainless T-Chimney Island Hood above island (Y=6.8..18.5, Z=20.4, X in [-2.6, +6.6], twin steel chimney stack + 4 drop rods + warm_led strip).
   - High-arc spring faucet + sink (X=1.8, Z=20.4); butcher block + forged knife + 3 steaks (mats['steak_raw']) + pepper/salt mills; copper sauteuse pan (mats['copper_cook']); matte-white 3-leg bowl with limes; matte-black pitcher; 4 crystal stems + twin water bottles.
6. Zone 4B Separate Formal Rectangular Dining Room (Z in [27.8, 34.2], X in [-6.8, +6.8]):
   - Woven rug (13.6 x 7.8 WU), 'DiningTableMarble' rectangular charcoal-grey marble slab (11.4 x 0.16 x 3.6 WU at Y=2.04, Z=30.8) on bronze pedestals, 8 cream-boucle & walnut armchairs, 8 place settings, travertine olive vase, twin black-and-brass linear pendants (Y=8.2).
"""

MOUNTAIN_POOL_PROMPT = """
Write scripts/penthouse_kit/mod_south_terrace_mountains.py (< 225 lines) with build_south_terrace_and_mountains(ctx, mats).
Build 1F Walkable Outdoor Infinity Pool & BBQ Courtyard (Z in [36.0, 54.0]) + Alpine Fjord + AAA Snow-Capped Dolomite Peaks (Z in [56.0, 178.0]):
1. Pool & BBQ Courtyard (Z in [36.0, 54.0], X in [-15.2, +15.2]):
   - Travertine terrace deck surrounding sunken Infinity Pool basin (pool bounds X in [-10.8, +3.6], Z in [41.5, 52.8], floor at Y=-1.15, water 'InfinityPoolWater' at Y=-0.16 in mats['alpine_lake'], basalt infinity weir lip at Z=52.9, warm underwater LED strip).
   - Glass & charcoal-steel balustrade along edges & dry South terrace.
   - 2 teak & off-white cushioned Lounge Chairs (X=-13.0, Z=45.0 & X=6.2, Z=49.0) + umbrella + side tables.
   - Outdoor Stainless Built-In BBQ Gas Grill & Limestone Prep Bar (X in [8.2, 13.8], Z in [38.2, 43.2], hood, grates, knobs, herb planter).
2. Emerald Alpine Fjord Lake (Z in [54.0, 152.0]):
   - Wide mirror water 'AlpineLakeSurface' (mats['alpine_lake']) at Y=-8.20 spanning X in [-170, +170], Z in [54, 152], plus evergreen rocky shoreline promontories (Z in [55..72], mats['conifer_dark'] pine spires + limestone rock slabs).
3. AAA Snow-Capped Alpine Dolomite Massif (Z in [62.0, 178.0], X in [-175, +175]):
   - True 80 x 26 ridged-multifractal heightfield mesh 'AlpineMountainMassif' using mats['aaa_mountain'] via b.add_tri_raw:
     * Elevation h(x, z) features 2 majestic Dolomite peaks flanking a central glacial valley Saddle (Left peak ~ X=-42, Z=108, H=54; Right peak ~ X=+46, Z=118, H=60; foothill spurs + ridged crags from Y=-9.0 up to Y=+54.0).
     * Compute smooth analytic central-difference vertex normals (nx, ny, nz) per grid vertex so directional sunlight sculpts crisp peaks & shadow couloirs!
     * Map U = (ix / nx_seg) * 4.0 and V = max(0.02, min(0.98, (h - (-8.5)) / 58.0)).
"""

EAST_WING_PROMPT = """
Write scripts/penthouse_kit/mod_east_piano_sport_wing.py (< 225 lines) with build_east_piano_sport_wing(ctx, mats).
Build the East Piano & Sporting Salon (X in [15.0, 29.6], Z in [-15.8, +14.8], Y in [0.0, 18.6]), directly connected to Living Room via North (Z in [-14.6,-7.0]) and South (Z in [3.4,13.8]) portals:
1. Salon Shell:
   - Herringbone oak floor 'EastSalonFloor' (mats['oak']), brass floor inlay, limestone walls on East (X=29.6), South (Z=14.9), North glass curtain extension (Z=-16.0, window_frame + glass looking out at sea), fluted walnut architectural niches with warm_led accents on East wall, marmorino ceiling (Y=18.66) + brass globe chandelier (X=22.4, Z=1.0).
2. 9-ft Ebony Concert Grand Piano (X=22.2, Z=-6.8):
   - Woven cream wool rug (9.2 x 7.8 WU).
   - Glossy 'GrandPianoCase' (mats['ebony_piano']) contoured body + cheekblocks + 3 tapered legs on brass casters + brass pedal lyre & 3 pedals; open angled lid held by thin brass prop rod; golden cast harp & strings 'GrandPianoHarp' (mats['brass'] + mats['copper_cook']); 'GrandPianoKeys' (52 white ivory + 36 ebony sharps at Y=2.04, X=19.8); tufted black-leather bench ('PianoBench') at X=18.3, Z=-6.8.
3. Indoor Golf Putting Green & Leather Tour Golf Bag (South-East bay, X in [18.4, 28.4], Z in [6.8, 13.8]):
   - Dark walnut fringe border + sculpted kidney-shaped tournament turf ('PuttingGreenTurf', mats['racing_green'], Y=0.05) with 2 stainless cups, brass pin flags, 3 white golf balls + brass putter.
   - Stitched 'GolfTourBag' (mats['racing_green'] + 'saddle_tan' straps + 'steel' irons/drivers) standing at (27.6, 0.0, 12.6).
4. Crossed Pro Tennis Rackets & Equestrian Saddle Display (East Gallery Wall, X in [27.4, 29.3], Z in [-2.5, +5.5]):
   - Travertine gallery console + Wall-mounted Crossed Tennis Rackets ('TennisDisplay', matte frames + strung heads + optic-yellow tennis balls in brass basket at (28.3, 2.35, 3.8)).
   - Walnut & Brass Equestrian Saddle Stand ('EquestrianTack', X=28.1, Z=-1.4): cognac leather dressage saddle (mats['saddle_tan']) + steel stirrups + tall riding boots + black velvet helmet.
"""

JOBS = [
    {
        "name": "tex_kitchen_surfaces",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/tex_kitchen_surfaces.py",
        "system": "You are a senior graphics/PIL procedural PBR texture engineer. Write clean fast pure-Python Pillow textures.",
        "prompt": TEX_PROMPT + COMMON_RULES,
        "verify_cmd": (
            "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/tex_kitchen_surfaces.py', doraise=True); "
            "import sys; sys.path.insert(0,'scripts'); "
            "from penthouse_kit.tex_kitchen_surfaces import make_platinum_slate_tex, make_smart_panel_tex, make_prestige_wine_labels_tex, make_aaa_snow_granite_mountain_tex; "
            "assert make_platinum_slate_tex(64,64).size==(64,64) and make_smart_panel_tex(128,85).size==(128,85) and make_prestige_wine_labels_tex(128,64).size==(128,64) and make_aaa_snow_granite_mountain_tex(128,64).size==(128,64); "
            "print('OK tex_kitchen_surfaces')\""
        ),
    },
    {
        "name": "mod_south_fridge",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_south_fridge.py",
        "system": "You are an architectural 3D appliance builder for Three.js GLTF pipelines. Produce clean, well-proportioned procedural geometry.",
        "prompt": FRIDGE_PROMPT + COMMON_RULES,
        "verify_cmd": "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_south_fridge.py', doraise=True); print('OK mod_south_fridge')\"",
    },
    {
        "name": "mod_south_kitchen",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_south_kitchen.py",
        "system": "You are an architectural 3D interior designer building a charcoal-oak chef kitchen & separate rectangular dining hall in Three.js.",
        "prompt": KITCHEN_PROMPT + COMMON_RULES,
        "verify_cmd": "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_south_kitchen.py', doraise=True); print('OK mod_south_kitchen')\"",
    },
    {
        "name": "mod_south_terrace_mountains",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_south_terrace_mountains.py",
        "system": "You are a 3D environment technical artist creating a walkable pool courtyard, glacial lake, and ridged-multifractal Dolomite alpine peaks.",
        "prompt": MOUNTAIN_POOL_PROMPT + COMMON_RULES,
        "verify_cmd": "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_south_terrace_mountains.py', doraise=True); print('OK mod_south_terrace_mountains')\"",
    },
    {
        "name": "mod_east_piano_sport_wing",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_east_piano_sport_wing.py",
        "system": "You are a 3D architectural salon & acoustic instrument modeler creating an East piano, putting green, tennis, and equestrian lounge.",
        "prompt": EAST_WING_PROMPT + COMMON_RULES,
        "verify_cmd": "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_east_piano_sport_wing.py', doraise=True); print('OK mod_east_piano_sport_wing')\"",
    },
]

if __name__ == "__main__":
    res = run_parallel_codegen(JOBS, batch_name="batch14_grand_expansion", max_workers=5)
    for k, v in res.items():
        print(f"=== {k}: ok={v.get('ok')} ({v.get('lines', '?')} lines) ===")
