from .mod_south_fridge import build_south_fridge
from .mod_south_dining import build_south_dining
from .mod_south_cellar_and_cookware import build_south_cellar_and_cookware


def _box(ctx, name, mat, cx, cy, cz, sx, sy, sz, rot=0.0):
    b = ctx.mb(name, mat)
    b.add_box(cx, cy, cz, sx, sy, sz, 0, rot)
    return b


def _cyl(ctx, name, mat, cx, y0, cz, r, h, segs=16, rx=0.0, rz=0.0):
    b = ctx.mb(name, mat)
    b.add_cylinder(cx, y0, cz, r, r, h, segs, rot_x=rx, rot_z=rz)
    return b


def build_south_kitchen(ctx, mats):
    M = mats
    # ---------- 1. Shell & Preserved Black French Triple-Bay Doors (Z=36.0) ----------
    _box(ctx, "SouthKitchenFloor", M["tundra_grey"], 0, -0.07, 25.7, 30.4, 0.14, 20.6)
    _box(ctx, "SouthKitchenCeiling", M["marmorino"], 0, 18.66, 25.7, 30.4, 0.12, 20.6)
    for sx in (-14.9, 14.9):
        _box(ctx, "SouthKitchenWall", M["marmorino"], sx, 9.3, 25.7, 0.24, 18.6, 20.6)
        _box(ctx, "SouthKitchenBulkhead", M["warm_grey_upper"], sx, 7.8, 25.7, 0.28, 2.0, 20.6)
    for cz in (15.5, 35.9):
        _box(ctx, "SouthKitchenCove", M["warm_led"], 0, 18.55, cz, 30.0, 0.06, 0.12)
    for cx in (-14.8, 14.8):
        _box(ctx, "SouthKitchenCove", M["warm_led"], cx, 18.55, 25.7, 0.12, 0.06, 20.0)

    zf = 36.0
    for px in (-14.2, -9.47, -4.73, 0.0, 4.73, 9.47, 14.2):
        _box(ctx, "KitchenFrenchPillar", M["charcoal"], px, 4.575, zf, 0.16, 9.05, 0.18)
    for py in (0.05, 3.05, 6.05, 9.10):
        _box(ctx, "KitchenFrenchRail", M["charcoal"], 0, py, zf, 28.6, 0.14, 0.18)
    for i in range(6):
        cx = -14.2 + 4.73 * (i + 0.5)
        _box(ctx, "KitchenFrenchGlass", M["glass"], cx, 4.575, zf, 4.56, 8.90, 0.04)

    # ---------- 2. East Wall Extended Coffee & Breakfast Station (Z in [24.1..34.8]) ----------
    _box(ctx, "CoffeeSurround", M["graphite_slate"], 13.55, 4.4, 29.45, 2.40, 8.8, 10.7)
    _box(ctx, "CoffeeWarmUpper", M["warm_grey_upper"], 13.55, 7.65, 29.45, 2.44, 2.3, 10.7)
    _box(ctx, "CoffeeNicheWalnut", M["walnut_fluted"], 13.10, 4.65, 29.45, 0.80, 3.2, 9.4)
    _box(ctx, "CoffeeNicheLED", M["warm_led"], 12.68, 6.20, 29.45, 0.08, 0.06, 9.2)
    _box(ctx, "CoffeeCounter", M["pietra_grey"], 13.45, 2.28, 29.45, 2.65, 0.16, 10.7)
    _box(ctx, "CoffeeBacksplash", M["pietra_grey"], 14.62, 3.15, 29.45, 0.12, 1.75, 10.7)
    _box(ctx, "KitchenEspressoMachine", M["steel"], 12.82, 2.74, 28.5, 0.92, 0.78, 0.78)
    _cyl(ctx, "CoffeeGrinder", M["steel"], 12.85, 2.36, 30.1, 0.17, 0.62)
    _cyl(ctx, "CoffeeKettle", M["charcoal"], 12.85, 2.36, 31.3, 0.15, 0.36)
    for i in range(4):
        _cyl(ctx, "CoffeeCup", M["porcelain_white"], 12.68, 2.36, 26.8 + 0.38 * i, 0.07, 0.12, 12)
    for i in range(4):
        _cyl(ctx, "KitchenGranolaJars", M["glass"], 13.0, 2.36, 32.1 + 0.52 * i, 0.16, 0.52, 14)

    # ---------- 3. West Wall 60" Wolf Dual-Oven Red-Knob Gas Range & Flush Hood ----------
    for cz in (16.4, 24.6):
        _box(ctx, "WolfSideColumn", M["graphite_slate"], -13.55, 4.4, cz, 2.40, 8.8, 1.60)
    _box(ctx, "WolfBacksplash", M["pietra_grey"], -14.66, 4.35, 20.5, 0.12, 4.2, 6.6)
    _box(ctx, "WolfHoodCanopy", M["warm_grey_upper"], -13.45, 7.40, 20.5, 2.65, 2.20, 6.8)
    _box(ctx, "WolfHoodLed", M["warm_led"], -13.45, 6.28, 20.5, 2.40, 0.05, 6.4)
    _box(ctx, "WolfRangeBody", M["steel"], -13.55, 1.18, 20.5, 2.25, 2.36, 4.80)
    for cz in (19.25, 21.75):
        _box(ctx, "WolfOvenDoor", M["obsidian_bezel"], -12.41, 1.00, cz, 0.06, 1.45, 2.15)
        _cyl(ctx, "WolfHandle", M["steel"], -12.30, 1.72, cz - 0.90, 0.04, 1.80, 10, rx=1.5708)
    for i in range(6):
        _box(ctx, "WolfGrate", M["charcoal"], -13.50, 2.40, 18.45 + 0.82 * i, 2.00, 0.07, 0.72)
    _box(ctx, "WolfGriddle", M["steel"], -13.50, 2.40, 20.50, 2.00, 0.06, 0.90)
    for i in range(8):
        _cyl(ctx, "WolfRedKnobs", M["wolf_red"], -12.36, 2.12, 18.45 + 0.58 * i, 0.10, 0.16, 14, rz=1.5708)

    # ---------- 4. West Wall 8-Estate Grand-Cru Wine Cellar & Luxury Cookware ----------
    build_south_cellar_and_cookware(ctx, mats)

    # ---------- 5. Zone 4A Center Smoked-Oak & Marble Island + Chimney Hood ----------
    _box(ctx, "KitchenIslandOak", M["rift_oak"], 2.2, 1.14, 20.4, 11.0, 2.20, 3.12)
    _box(ctx, "KitchenIslandStone", M["pietra_grey"], 2.2, 2.32, 20.4, 11.4, 0.18, 3.30)
    for cx in (-3.4, 7.8):
        _box(ctx, "KitchenIslandWaterfall", M["pietra_grey"], cx, 1.16, 20.4, 0.18, 2.34, 3.30)
    for cx in (-1.2, 2.0, 5.2):
        _box(ctx, "KitchenBarStoolsSeat", M["charcoal"], cx, 1.68, 17.85, 0.92, 0.16, 0.88)
        _box(ctx, "KitchenBarStoolsBack", M["charcoal"], cx, 2.08, 17.46, 0.92, 0.64, 0.12)
        for sx in (cx - 0.42, cx + 0.42):
            _box(ctx, "KitchenBarStools", M["brass"], sx, 0.82, 17.85, 0.05, 1.62, 0.05)
            _box(ctx, "KitchenBarStools", M["brass"], sx, 0.04, 17.85, 0.05, 0.05, 0.86)
        _box(ctx, "KitchenBarStools", M["brass"], cx, 0.04, 17.44, 0.88, 0.05, 0.05)
        _box(ctx, "KitchenBarStools", M["brass"], cx, 0.56, 17.85, 0.88, 0.04, 0.04)

    # Suspended Brushed-Stainless Chimney Island Hood (Photo 3 style)
    _box(ctx, "IslandRangeHood", M["steel"], 2.0, 13.4, 20.4, 2.4, 10.2, 1.3)
    _box(ctx, "IslandRangeHoodCanopy", M["steel"], 2.0, 7.95, 20.4, 9.4, 0.30, 3.2)
    for cx in (-2.3, 6.3):
        for cz in (19.0, 21.8):
            _cyl(ctx, "IslandHoodRod", M["steel"], cx, 8.10, cz, 0.035, 10.4, 8)
    _box(ctx, "IslandHoodLed", M["warm_led"], 2.0, 7.78, 20.4, 8.9, 0.04, 2.8)

    # Abundant Island Culinary Props & Cookware
    _box(ctx, "KitchenSink", M["steel"], 1.8, 2.38, 20.5, 1.5, 0.08, 1.1)
    ctx.mb("KitchenFaucet", M["steel"]).add_curved_tube(
        [(1.8, 2.40, 21.15), (1.8, 3.15, 21.15), (1.8, 3.48, 20.80), (1.8, 3.22, 20.48)],
        [0.045, 0.042, 0.038, 0.032], segs=10,
    )
    _box(ctx, "KitchenSteakBoard", M["rift_oak"], 2.8, 2.45, 19.6, 1.45, 0.09, 0.95)
    for i in range(3):
        _box(ctx, "KitchenRawSteaks", M["steak_marbled"], 2.35 + 0.42 * i, 2.52, 19.6, 0.34, 0.08, 0.24)
    _cyl(ctx, "KitchenPepperMill", M["walnut_solid"], 3.85, 2.42, 19.55, 0.07, 0.44, 12)
    _cyl(ctx, "KitchenSaltMill", M["porcelain_white"], 4.08, 2.42, 19.55, 0.07, 0.38, 12)
    _cyl(ctx, "KitchenCopperSkillet", M["copper_cook"], -1.6, 2.42, 20.4, 0.46, 0.20, 18)
    _cyl(ctx, "KitchenSkilletHandle", M["brass"], -1.1, 2.54, 20.4, 0.035, 0.65, 8, rz=1.42)
    _cyl(ctx, "KitchenLimeBowl", M["porcelain_white"], 4.8, 2.46, 19.6, 0.38, 0.22, 16)
    for lx, lz in ((4.68, 19.52), (4.88, 19.58), (4.78, 19.72), (4.82, 19.60)):
        ctx.mb("KitchenLimes", M["herb_green"]).add_sphere(lx, 2.66, lz, 0.085, 0.075, 0.085, rings=8, segs=10)
    _cyl(ctx, "KitchenPitcher", M["charcoal"], 6.0, 2.42, 19.8, 0.16, 0.56, 14)
    for i in range(4):
        _cyl(ctx, "KitchenCrystalStem", M["crystal_glass"], 5.2 + 0.32 * i, 2.42, 19.1, 0.07, 0.34, 12)
    _cyl(ctx, "KitchenPourBottle", M["wine_bottle"], 0.10, 2.42, 19.55, 0.095, 0.56, 14)
    _cyl(ctx, "KitchenPourFoil", M["brass"], 0.10, 2.98, 19.55, 0.055, 0.12, 12)
    _cyl(ctx, "KitchenDecanterWine", M["crystal_glass"], -0.75, 2.42, 19.50, 0.22, 0.42, 16)

    build_south_fridge(ctx, mats)
    build_south_dining(ctx, mats)
    return ctx
