"""Built-in French double-door refrigerator for the penthouse kitchen."""

from __future__ import annotations


def _box(b, cx, cy, cz, sx, sy, sz, tile=0.0):
    b.add_box(cx, cy, cz, sx, sy, sz, uv_tile=tile)


def _cyl(b, cx, y0, cz, r, h, segs=16):
    b.add_cylinder(cx, y0, cz, r, r, h, segs=segs)


def _sphere(b, cx, cy, cz, r, segs=12):
    b.add_sphere(cx, cy, cz, r, r, r, rings=8, segs=segs)


def build_french_fridge(ctx, mats):
    # ---------------- Cabinet shell ----------------
    b = ctx.mb("FridgeInteriorShell", mats["ceramic_white"])
    _box(b, -14.78, 1.32, -3.20, 0.04, 2.36, 2.12)          # back
    _box(b, -14.46, 1.32, -4.26, 0.64, 2.36, 0.04)          # left wall
    _box(b, -14.46, 1.32, -2.14, 0.64, 2.36, 0.04)          # right wall
    _box(b, -14.46, 0.14, -3.20, 0.64, 0.04, 2.12)          # floor
    _box(b, -14.46, 2.50, -3.20, 0.64, 0.04, 2.12)          # top

    b = ctx.mb("FridgeFrameTrim", mats["gunmetal"])
    _box(b, -13.88, 0.10, -3.20, 0.04, 0.04, 2.20)          # bottom bezel
    _box(b, -13.88, 2.58, -3.20, 0.04, 0.04, 2.20)          # top bezel
    _box(b, -13.88, 1.34, -4.30, 0.04, 2.48, 0.04)          # left bezel
    _box(b, -13.88, 1.34, -2.10, 0.04, 2.48, 0.04)          # right bezel

    b = ctx.mb("FridgeInteriorLED", mats["warm_led"])
    _box(b, -14.08, 1.375, -4.22, 0.03, 2.05, 0.03)         # left strip
    _box(b, -14.08, 1.375, -2.18, 0.03, 2.05, 0.03)         # right strip
    _box(b, -14.08, 2.47, -3.20, 0.03, 0.03, 2.00)          # top cornice

    # ---------------- Glass shelves ----------------
    b = ctx.mb("FridgeGlassShelves", mats["crystal_glass"])
    for y in (1.00, 1.42, 1.84):
        _box(b, -14.34, y, -3.20, 0.78, 0.02, 2.04)
    b = ctx.mb("FridgeGlassShelves", mats["chrome"])
    for y in (1.00, 1.42, 1.84):
        _box(b, -13.96, y, -3.20, 0.03, 0.03, 2.04)

    # ---------------- Top shelf: milk + yogurt ----------------
    b = ctx.mb("FridgeMilkBottles", mats["cream_pillow"])
    for z in (-4.02, -3.84, -3.66, -3.48):
        b.add_lathe(-14.32, 1.86, z,
                    [(0.0, 0.0), (0.048, 0.0), (0.054, 0.03), (0.054, 0.25),
                     (0.028, 0.31), (0.024, 0.36), (0.0, 0.36)], segs=14)
    b = ctx.mb("FridgeMilkLabels", mats["dairy_label"])
    for z in (-4.02, -3.84, -3.66, -3.48):
        _cyl(b, -14.32, 1.94, z, 0.057, 0.10, segs=14)

    b = ctx.mb("FridgeGreekYogurt", mats["ceramic_white"])
    for z in (-3.12, -2.94, -2.76, -2.58, -2.42):
        _cyl(b, -14.28, 1.86, z, 0.075, 0.14, segs=16)
    b = ctx.mb("FridgeGreekYogurtLid", mats["dairy_label"])
    for z in (-3.12, -2.94, -2.76, -2.58, -2.42):
        _cyl(b, -14.28, 2.00, z, 0.078, 0.02, segs=16)

    # ---------------- Upper-mid: fruit bowls ----------------
    b = ctx.mb("FridgeFruitBowls", mats["ceramic_white"])
    for z in (-3.92, -3.20, -2.50):
        b.add_lathe(-14.32, 1.44, z,
                    [(0.0, 0.0), (0.10, 0.0), (0.16, 0.04), (0.18, 0.10),
                     (0.0, 0.10)], segs=18)

    b = ctx.mb("FridgeBerriesBlue", mats["berry_blue"])
    for dz in (-0.06, 0.0, 0.06):
        for dx in (-0.04, 0.04):
            _sphere(b, -14.32 + dx, 1.56, -3.92 + dz, 0.028)

    b = ctx.mb("FridgeBerriesRed", mats["berry_red"])
    for dz in (-0.06, 0.0, 0.06):
        for dx in (-0.04, 0.04):
            _sphere(b, -14.32 + dx, 1.56, -3.20 + dz, 0.030)

    b = ctx.mb("FridgeProduceGreen", mats["produce_green"])
    for dz in (-0.05, 0.05):
        _sphere(b, -14.32, 1.56, -2.50 + dz, 0.055)
    b = ctx.mb("FridgeProduceCitrus", mats["citrus_yellow"])
    for dz in (-0.06, 0.0, 0.06):
        _sphere(b, -14.28, 1.56, -2.50 + dz, 0.038)

    # ---------------- Lower-mid: crispers ----------------
    b = ctx.mb("FridgeVeggieCrispers", mats["crystal_glass"])
    for z in (-3.68, -2.72):
        _box(b, -14.34, 1.18, z, 0.60, 0.30, 0.80)
    b = ctx.mb("FridgeVeggieGreens", mats["produce_green"])
    for z in (-3.68, -2.72):
        for dz in (-0.20, -0.05, 0.10, 0.25):
            _sphere(b, -14.34, 1.20, z + dz, 0.055)
    b = ctx.mb("FridgeVeggieTomatoes", mats["berry_red"])
    for z in (-3.68, -2.72):
        for dz in (-0.15, 0.05, 0.20):
            _sphere(b, -14.30, 1.22, z + dz, 0.045)
    b = ctx.mb("FridgeVeggieYellow", mats["citrus_yellow"])
    for z in (-3.68, -2.72):
        _sphere(b, -14.36, 1.22, z, 0.050)

    # ---------------- Bottom BioFresh ----------------
    b = ctx.mb("FridgeBioFreshDrawer", mats["glass_smoke"])
    _box(b, -14.34, 0.72, -3.20, 0.60, 0.22, 2.00)
    _box(b, -14.34, 0.38, -3.20, 0.60, 0.22, 2.00)
    b = ctx.mb("FridgeBioFreshTrim", mats["chrome"])
    for y in (0.72, 0.38):
        _box(b, -14.02, y, -3.20, 0.03, 0.03, 1.60)
    b = ctx.mb("FridgeBioFreshSteaks", mats["steak_marbled"])
    for z in (-3.90, -3.60, -3.30):
        _box(b, -14.34, 0.72, z, 0.40, 0.06, 0.22)
    b = ctx.mb("FridgeBioFreshJars", mats["ceramic_white"])
    for z in (-2.90, -2.60, -2.30):
        _cyl(b, -14.34, 0.38, z, 0.06, 0.16, segs=14)

    # ---------------- Left door ----------------
    b = ctx.mb("FridgeDoorLeft", mats["rift_oak"])
    _box(b, -13.86, 1.34, -3.745, 0.055, 2.44, 1.06)
    b = ctx.mb("FridgeDoorLeft", mats["gunmetal"])
    _box(b, -13.83, 1.34, -4.26, 0.02, 2.44, 0.03)
    _box(b, -13.83, 1.34, -3.23, 0.02, 2.44, 0.03)

    b = ctx.mb("FridgeHandleLeft", mats["brass"])
    _cyl(b, -13.79, 0.88, -3.30, 0.016, 1.08, segs=14)

    # ---------------- Right door (windowed) ----------------
    b = ctx.mb("FridgeDoorRight", mats["rift_oak"])
    _box(b, -13.86, 2.45, -2.655, 0.055, 0.22, 1.06)        # top rail
    _box(b, -13.86, 0.55, -2.655, 0.055, 0.86, 1.06)        # bottom apron
    _box(b, -13.86, 1.66, -3.155, 0.055, 1.36, 0.07)        # hinge stile
    _box(b, -13.86, 1.66, -2.155, 0.055, 1.36, 0.07)        # handle stile
    b = ctx.mb("FridgeDoorRight", mats["gunmetal"])
    _box(b, -13.83, 2.34, -2.655, 0.02, 0.02, 0.73)
    _box(b, -13.83, 0.98, -2.655, 0.02, 0.02, 0.73)
    _box(b, -13.83, 1.66, -3.02, 0.02, 1.36, 0.02)
    _box(b, -13.83, 1.66, -2.29, 0.02, 1.36, 0.02)

    b = ctx.mb("FridgeDoorRightGlass", mats["glass_smoke"])
    _box(b, -13.86, 1.66, -2.655, 0.02, 1.36, 0.73)

    b = ctx.mb("FridgeHandleRight", mats["brass"])
    _cyl(b, -13.79, 0.88, -3.10, 0.016, 1.08, segs=14)
