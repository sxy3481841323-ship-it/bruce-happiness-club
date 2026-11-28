#!/usr/bin/env python3
"""Parallel DeepSeek overnight batch 15:
1. Expanded East Piano & Sporting Wing (X=15..43.2) + Curved Glass Curtain Wall + Crisp Vitrines
2. Twilight River, Cable-Stayed Illuminated Bridge & Riverfront Skyline Vista (Photo 1)
3. Monumental Pearl-Dove U-Sectional Sofa (Photo 2) + Square Verde-Alpi Marble Table & Props (Photo 3)
4. Diverse 8-Estate Wine Cellar Silhouettes + 7-Piece Luxury Cookware Stage on Wolf Range & Island
"""
from ds_worker import run_parallel_codegen

COMMON_RULES = """
STRICT CODE RULES:
1. Keep total file length < 220 lines. Clean, readable, zero syntax or indentation glitches.
2. ONLY use prim_lib methods:
   b = ctx.mb(name, mat_idx)
   b.add_box(cx,cy,cz,sx,sy,sz,uv_tile=0.0,rot_y=0.0)
   b.add_rounded_box(cx,cy,cz,sx,sy,sz,bevel=0.04,uv_tile=0.0,rot_y=0.0)
   b.add_cylinder(cx,y0,cz,r_bot,r_top,h,segs=16,rot_x=0.0,rot_z=0.0,cap_top=True,cap_bot=True)
   b.add_sphere(cx,cy,cz,rx,ry,rz,rings=10,segs=16)
   b.add_lathe(cx,y0,cz,profile_list,segs=18)
   b.add_curved_tube(spine_pts,radii,segs=10)
   b.add_quad(p0,p1,p2,p3,uv_scale=(1.0,1.0),flip=False)
   b.add_tri_raw(p0,p1,p2,uv0=(0,0),uv1=(1,0),uv2=(1,1),n0=None,n1=None,n2=None)
   DO NOT pass rot_x or rot_z to add_box or add_rounded_box! Only add_cylinder accepts rot_x/rot_z.
3. Return ONLY valid raw Python code. No markdown fences. No prohibited Chinese city or wealth words.
"""

EAST_WING_PROMPT = """
Rewrite scripts/penthouse_kit/mod_east_piano_sport_wing.py (< 215 lines) defining build_east_piano_sport_wing(ctx, mats).
Expand the East Piano & Sporting Salon to X in [15.0, 42.6], Z in [-15.8, +15.6], Y in [0.0, 18.6]:
1. Expanded Architectural Shell & 14-Facet Curved Panoramic Glass Curtain Wall (Photo 1 style):
   - Floor 'EastSalonFloor' (mats['oak'], 27.6 x 0.10 x 31.4 at (28.8, -0.05, -0.1)), ceiling 'EastCeiling' (mats['marmorino'], Y=18.66), warm_led perimeter cove.
   - West-to-South enclosure: South wall (mats['marmorino'], at Z=15.6, X in [15.0..41.0]) + brass chandelier at (28.5, 16.0, -1.0).
   - Curved Panoramic Floor-to-Ceiling Glass Curtain Wall bowing smoothly from (15.0, -16.0) -> (26.0, -17.8) -> (35.5, -16.2) -> (41.4, -10.2) -> (42.8, 0.0) -> (41.2, +10.2) -> (39.5, +15.4):
     Build curved mullions ('CurvedGlassMullions', mats['window_frame']) along each curve joint, curved low travertine/limestone window sill bench ('CurvedWindowSill', mats['travertine'], Y=0.0..0.85), transom rail at Y=13.6, and double-sided glass quads ('CurvedPanoramicGlass', mats['glass'], Y=0.85..18.5).
2. 9-ft Ebony Concert Grand Piano Facing the Curved Bridge Window (Photo 1, centered X=31.2, Z=-9.6):
   - Woven cream wool rug 'PianoRug' (mats['cream_wool'], 11.4 x 0.04 x 9.6 at (30.8, 0.02, -9.2)).
   - Glossy ebony curved case ('GrandPianoCase', mats['ebony_piano'], main box + cylindrical curved tail + keybed), 3 legs on brass casters, brass pedal lyre & 3 pedals, double-sided open lid ('PianoOpenLid', flip=True & flip=False quads tilted ~26 deg held by brass prop), golden harp ('GrandPianoHarp') + 14 copper strings, 52 ivory & 36 black keys.
   - Glowing Sheet Music Stand ('GrandPianoSheetMusic', mats['sheet_music']) + brass desk lamp glow ('warm_bulb') + tufted leather 'PianoBench' at (27.4, 1.24, -9.6).
   - Potted Fiddle-Leaf Fig Tree ('PianoFigTree', ceramic pot + trunk + foliage crown in olive_leaf) beside the curved window mullion at (24.4, 0.0, -14.8).
3. Expansive Tournament Golf Putting Green & Backlit 9-Club Rack (X in [21.0, 39.2], Z in [1.8, 13.4]):
   - Dark walnut trim border + emerald 'PuttingGreenTurf' (mats['racing_green'], 18.2 x 0.07 x 11.2 at (30.1, 0.06, 7.6)) + white kidney sand bunker ('PuttingBunker', mats['cream_wool'], (23.2, 0.09, 10.6), sx=3.6, sz=2.2) + 3 stainless cups + 3 tall brass pin flags + 4 golf balls + putter.
   - High-Contrast Backlit Cream Limestone Golf Club Display Board at (38.8, 3.6, 7.6) with warm_led wash + walnut rack holding 9 individually visible clubs: 3 oversized titanium drivers (bulky spheres), 5 stepped chrome irons (steel shafts + angled heads), 1 brass mallet putter, beside large stitched 'GolfTourBag' (racing_green + saddle_tan).
4. Razor-Sharp Backlit Tennis & Equestrian Vitrines (South Gallery Wall Z=14.6, facing -Z):
   - Bright backlit cream limestone alcoves ('SportVitrinePanel', mats['marmorino'] + warm_led) behind both zones so dark/tan silhouettes pop with huge contrast!
   - Tennis Showcase (X=24.2, Z=14.5): 2 crossed 3.2 WU 'TennisDisplay' rackets angled in XY plane via rot_z=+-0.55 with oval hoop rings, handle grips, AND explicit crisp white crossed string-grid thin bars ('TennisStrings', mats['porcelain_white']) + brass wire ball basket & optic-yellow tennis balls on a travertine plinth!
   - Equestrian Showcase (X=32.4, Z=14.5): Travertine plinth + white quilted cotton saddle pad + large sculpted 'DressageSaddle' (mats['saddle_tan'], X=32.4, Y=3.0, Z=14.1, pommel, cantle, dark knee rolls) + stainless stirrups ('SaddleStirrup') + mounted bridle with brass bit ring + twin tall black riding boots + black velvet helmet!
"""

RIVER_BRIDGE_PROMPT = """
Create scripts/penthouse_kit/mod_east_river_bridge_vista.py (< 165 lines) defining build_east_river_bridge_vista(ctx, mats).
Build the twilight river, illuminated suspension bridge, and city waterfront skyline outside the East curved windows (Photo 1 vista, X in [44.0, 175.0], Z in [-135.0, +48.0], Y = -10.0):
1. Twilight River Surface ('EastRiverWater', mats['alpine_lake']):
   - Wide serene river expanse below the penthouse cliff (X in [46.0, 175.0], Z in [-135.0, +48.0], Y=-10.0) plus golden/amber reflected light ribbons ('RiverLightGlints', mats['warm_bulb'] / 'warm_led') shimmering in bands across the water toward the bridge!
2. Illuminated Cable-Stayed / Suspension Bridge ('EastRiverBridge', hero landmark crossing diagonally outside the curved glass window around (56, 2) -> (120, -68)):
   - Sweeping bridge roadbed span (mats['charcoal'], rotated rot_y=-0.78) + twin bright golden highway LED edge rails ('BridgeDeckGlow', mats['warm_led']) + crimson taillight dots.
   - Two monumental sculpted illuminated H-frame Bridge Towers rising at (68, -10.0, -12) and (104, -10.0, -52) to Y=+20.0 (mats['steel'] + vertical warm_led pylon stripes).
   - 16 taut diagonal steel/warm-lit stay cables spanning from tower tops down along the bridge deck on both spans!
3. Twilight City Waterfront Skyline ('EastSkylineTowers', X in [115..168] & [-95..-45] far bank, Z in [-125..+35]):
   - 26 varied modern architectural high-rise towers textured with mats['city_facade'] (dark slate with glowing amber & warm-white window grids, heights 14..58 WU) plus luminous spire crowns ('SkylineSpires', mats['warm_bulb']) silhouettes against the dusk sky!
"""

SALON_SEATING_PROMPT = """
Rewrite scripts/penthouse_kit/mod_salon_seating.py (< 215 lines) defining build_salon_seating(ctx, mats).
Preserve import: from penthouse_kit.cushion_helper import add_designer_pillow
Build the Monumental Central Salon (Photos 2 & 3 style, preserving exact interactive mesh names for Evian & Concierge):
1. Expanded Rug: 'SalonRugPlinth' & 'SalonRug' spanning 18.4 x 16.0 WU around (1.8, 0.038, -0.6).
2. Monumental Pearl-Dove Modular U-Sectional Sofa ('SofaPlinth' in rift_oak, 'SofaSeat'/'SofaBack' in mats['dove_boucle']):
   - Large three-wing U-wrap framing the central table while staying open on the +X side toward Fireplace/TV:
     * North wing: cx=-0.5, cz=-5.5, sx=10.2, sz=2.6 (backrest at cz=-6.6)
     * West wing: cx=-4.3, cz=-0.4, sx=2.6, sz=7.6 (backrest at cx=-5.4)
     * South chaise wing: cx=-1.9, cz=+2.2, sx=7.4, sz=2.5 (backrest at cz=+3.3)
   - Deep cushioned seats (Y=0.44..1.16) + tailored bolsters + 5 emerald-jade botanical Jacquard throw pillows ('SofaPillowA..E', mats['emerald_silk'] / mats['cream_pillow']).
3. Behind-Sofa Console & Taccia Lamp (Photo 2, X=-6.55, Z in [-4.8..+2.0], mats['charcoal'] + 'walnut_solid'):
   - Sleek 2-tier long console table behind West wing + chrome pedestal & angled glowing glass dome Taccia lamp ('TacciaLamp', Y=2.15..2.95) + art books!
4. Cognac Saddle-Leather Club Armchair (Photo 2, centered at (6.4, 0.04, -5.0), angled slightly toward table) in mats['saddle_tan'].
5. Square Verde-Alpi Green Marble Low Cocktail Table ('TableASmokedStone', mats['verde_alpi'], centered at (1.35, 0.94, -1.55), 4.60 x 0.14 x 4.40 WU, beveled on recessed 'TableAPedestals' obsidian plinth):
   - Compact oak/travertine 'TableB' accent side table at (4.35, 0.94, -1.55) holding 'ConciergePager1F' & 'ConciergeScreen1F'.
   - Preserved Interactive Evian Oxblood Leather Tray & Pour Ceremony meshes at tray center (1.16, 1.01, -2.55):
     'TableATrayLeather', 'TableATrayBrass', 'EvianBottles1F', 'EvianCapsReserve1F', 'EvianLabelsReserve1F',
     'EvianPourBottle1F' (at (1.15, 1.01, -2.55)), 'EvianPourLabel1F', 'EvianPourCap1F',
     'CrystalWaterBowl1F' (at (1.44, 1.01, -2.50)), 'CrystalBowlFoot1F', 'CrystalBowlWater1F'!
   - Rich Photo 3 Coffee Table Styling on the Verde-Alpi surface (Y=1.01):
     * 'SalonOrchidBowl' (obsidian stoneware pot + cascading green leaves + arched stems + 14 white/blush 'orchid_white' blooms at (1.45, 1.01, -1.35))
     * 'ChampagneIceBucket' (brushed steel pail on silver round tray + folded white napkin + dark tilted champagne bottle with gold foil + 2 crystal wine stems at (2.55, 1.01, -0.55))
     * 'SalonFruitPlatter' (oval porcelain platter + red apple + pears/grapes + figs at (-0.15, 1.01, -0.85))
     * 4 Green-Cap Clear Water Bottles ('SanBernardoBottles', mats['evian_flint_glass'] + mats['herb_green'] caps at (1.35, 1.01, -0.45)) + tilted welcome card + twin cardfolios + open luxury art monograph + rolled porcelain napkin plate!
"""

CELLAR_COOKWARE_PROMPT = """
Create scripts/penthouse_kit/mod_south_cellar_and_cookware.py (< 215 lines) defining build_south_cellar_and_cookware(ctx, mats).
Build two standout realistic features for the West Kitchen Wall & Island:
1. Genuinely Diverse 8-Estate Grand-Cru Wine Cellar (X in [-14.75, -12.15], Z in [25.2, 34.8]):
   - Fluted walnut recessed cellar alcoves, oak horizontal display shelves, warm_led cove lighting, lower wooden OWC wine crates ('WineCrates', mats['rift_oak']), crystal decanters.
   - 8 DISTINCT estate bays (different bottle shapes via varied lathe radii/shoulder heights, distinct glass tints: emerald wine_bottle / ruby burgundy_glass / clear champagne_liquid / golden amber_wine, distinct capsule colors: gold brass / crimson wolf_red / matte charcoal, AND sliced UVs from mats['prestige_wine_labels'] across all 8 cells!):
     Dom Perignon, Cristal, Krug, DRC Romanee-Conti, Chateau Petrus, Chateau Lafite (plus 1.5L Magnum cradle!), Opus One, Chateau d'Yquem!
2. Abundant Multi-Pot Luxury Cooking Stage on 60" Wolf Range (X=-13.45, Z=20.5, Y=2.44) + Brass Wall Rail + Island:
   - On Wolf 6-Burner Grates & Griddle:
     * Burner 1 (front-left): Flame-Red 'LeCreusetDutchOven' (mats['le_creuset_red'], oval enameled pot + domed lid + brass knob + loop handles)
     * Burner 2 (rear-left): Hammered 'MauvielCopperStockpot' (mats['copper_cook'], tall cylindrical pot + brass handles + fitted copper lid)
     * Burner 3 (front-right): Brushed Stainless 5-Ply 'StainlessSaucier' (mats['steel'] pan + long steel riveted handle)
     * Burner 4 (rear-right): Seasoned Matte-Black 'CastIronGrillPan' (mats['charcoal'] square grill pan + 2 sizzling ribeyes mats['steak_marbled'])
     * Burner 5 (center): Hand-Hammered 'CarbonSteelWok' (mats['obsidian_bezel'] flared lathe wok + wooden handle mats['rift_oak'])
   - Brass Wall Hanging Pot Rail on the Wolf Backsplash ('BackSplashPotRail', mats['brass'] horizontal rod at (-14.48, 4.75, 20.5) spanning 5.2 WU) holding:
     * 2 hanging graduated hammered copper saucepans + skillets + brass ladle & slotted turner!
   - On Center Prep Island (X=-1.6, Y=2.42, Z=20.4):
     * White Enameled Cast-Iron Cocotte ('IslandCocotte', mats['porcelain_white'] + brass knob) + Hammered Copper Tea Kettle ('IslandTeaKettle', mats['copper_cook'] + arched brass handle)!
"""

JOBS = [
    {
        "name": "mod_east_piano_sport_wing",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_east_piano_sport_wing.py",
        "system": "You are a senior architectural 3D salon & sporting gallery modeler for Three.js GLTF pipelines. Produce crisp high-contrast geometry.",
        "prompt": EAST_WING_PROMPT + COMMON_RULES,
        "verify_cmd": "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_east_piano_sport_wing.py', doraise=True); print('OK east_wing')\"",
    },
    {
        "name": "mod_east_river_bridge_vista",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_east_river_bridge_vista.py",
        "system": "You are an architectural 3D city waterfront vista artist creating a twilight river, illuminated suspension bridge, and city skyline.",
        "prompt": RIVER_BRIDGE_PROMPT + COMMON_RULES,
        "verify_cmd": "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_east_river_bridge_vista.py', doraise=True); print('OK river_bridge')\"",
    },
    {
        "name": "mod_salon_seating",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_salon_seating.py",
        "system": "You are a residential luxury interior modeler creating an oversized pearl-dove U-sectional, Verde Alpi marble table, and botanical tablescape.",
        "prompt": SALON_SEATING_PROMPT + COMMON_RULES,
        "verify_cmd": "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_salon_seating.py', doraise=True); print('OK salon_seating')\"",
    },
    {
        "name": "mod_south_cellar_and_cookware",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_south_cellar_and_cookware.py",
        "system": "You are a specialized 3D prop artist crafting diverse Grand-Cru wine bottles and multi-pot enameled/copper cookware.",
        "prompt": CELLAR_COOKWARE_PROMPT + COMMON_RULES,
        "verify_cmd": "python3 -c \"import py_compile; py_compile.compile('scripts/penthouse_kit/mod_south_cellar_and_cookware.py', doraise=True); print('OK cellar_cookware')\"",
    },
]

if __name__ == "__main__":
    run_parallel_codegen(JOBS, batch_name="batch15_overnight", max_workers=4)
