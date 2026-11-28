from penthouse_kit.mod_west_fridge import build_french_fridge


def build_west_kitchen(ctx, mats):
    # ---------- 1. Mountain picture window + herb ledge ----------
    b = ctx.mb("KitchenWindowFrame", mats["window_frame"])
    for z in (-14.4, -6.6):
        b.add_box(-14.88, 3.00, z, 0.06, 3.84, 0.06)
    b.add_box(-14.88, 4.92, -10.5, 0.06, 0.06, 7.86)
    b.add_box(-14.88, 1.08, -10.5, 0.06, 0.06, 7.86)
    b.add_box(-14.88, 3.00, -10.5, 0.05, 3.84, 0.05)

    b = ctx.mb("KitchenWindowGlass", mats["glass"])
    b.add_box(-14.88, 3.00, -10.5, 0.025, 3.82, 7.76)

    b = ctx.mb("KitchenHerbCounter", mats["rift_oak"])
    b.add_box(-14.32, 0.50, -10.4, 1.05, 1.00, 8.4)
    b = ctx.mb("KitchenHerbCounterTop", mats["travertine"])
    b.add_box(-14.32, 1.04, -10.4, 1.12, 0.08, 8.48)

    b = ctx.mb("KitchenHerbSink", mats["gunmetal"])
    b.add_box(-14.30, 1.06, -10.5, 0.42, 0.04, 0.62)
    b = ctx.mb("KitchenHerbFaucet", mats["brass"])
    b.add_cylinder(-14.30, 1.08, -10.5, 0.022, 0.022, 0.34, segs=14)
    b.add_cylinder(-14.30, 1.40, -10.5, 0.020, 0.020, 0.22, segs=14, rot_x=1.5708)

    b = ctx.mb("KitchenHerbPots", mats["terracotta"])
    for z in (-13.4, -11.9, -9.1, -7.8, -6.9):
        b.add_cylinder(-14.42, 1.08, z, 0.12, 0.15, 0.15, segs=16)

    b = ctx.mb("KitchenHerbFoliage", mats["olive_leaf"])
    b_hb = ctx.mb("KitchenHerbFoliageBright", mats["olive_leaf_bright"])
    for idx, z in enumerate((-13.4, -11.9, -9.1, -7.8, -6.9)):
        for k, (dx, dy, dz, rr) in enumerate((
            (-0.04, 0.19, -0.04, 0.085), (0.05, 0.21, 0.03, 0.080),
            (-0.02, 0.25, 0.05, 0.075), (0.04, 0.18, -0.05, 0.080),
            (0.00, 0.29 + (idx % 2) * 0.05, 0.00, 0.070),
        )):
            tgt = b if (k + idx) % 2 == 0 else b_hb
            tgt.add_sphere(-14.42 + dx, 1.08 + dy, z + dz, rr, rr * 1.18, rr, rings=7, segs=10)

    # ---------- 2. Tall culinary wall ----------
    b = ctx.mb("KitchenTallUpperWall", mats["rift_oak"])
    b.add_box(-14.35, 5.84, -3.2, 1.00, 6.48, 6.0)
    b = ctx.mb("KitchenTallWallInlays", mats["brass"])
    b.add_box(-13.84, 5.80, -3.2, 0.02, 0.03, 6.0)
    for z in (-4.30, -2.10):
        b.add_box(-13.84, 4.20, z, 0.02, 3.20, 0.03)

    # North bay
    b = ctx.mb("KitchenNorthDrawers", mats["gunmetal"])
    b.add_box(-14.35, 0.575, -5.235, 0.98, 0.95, 1.83)
    b = ctx.mb("KitchenEspressoAlcove", mats["calacatta_viola"])
    b.add_box(-14.78, 1.64, -5.235, 0.04, 1.16, 1.83)
    b.add_box(-14.35, 1.64, -6.15, 0.86, 1.16, 0.04)
    b.add_box(-14.35, 1.64, -4.32, 0.86, 1.16, 0.04)
    b = ctx.mb("KitchenEspressoCove", mats["warm_led"])
    b.add_box(-14.35, 2.18, -5.235, 0.80, 0.03, 1.70)

    b = ctx.mb("KitchenEspressoShelf", mats["calacatta_viola"])
    b.add_box(-14.35, 1.06, -5.235, 0.90, 0.04, 1.80)
    b = ctx.mb("KitchenEspressoMachine", mats["gunmetal"])
    b.add_rounded_box(-14.28, 1.24, -5.20, 0.36, 0.34, 0.44, bevel=0.02)
    b = ctx.mb("KitchenEspressoChrome", mats["chrome"])
    b.add_box(-14.12, 1.28, -5.20, 0.08, 0.12, 0.36)
    b.add_cylinder(-14.28, 1.41, -5.06, 0.06, 0.09, 0.14, segs=14)
    b = ctx.mb("KitchenEspressoLevers", mats["brass"])
    b.add_cylinder(-14.08, 1.30, -5.20, 0.018, 0.018, 0.15, segs=12, rot_z=1.5708)
    b.add_cylinder(-14.10, 1.28, -5.34, 0.025, 0.025, 0.04, segs=12, rot_z=1.5708)
    b = ctx.mb("KitchenEspressoCup", mats["ceramic_white"])
    b.add_cylinder(-14.08, 1.08, -5.20, 0.045, 0.050, 0.06, segs=16)
    b.add_cylinder(-14.08, 1.06, -5.20, 0.075, 0.075, 0.02, segs=16)

    b = ctx.mb("KitchenGranolaTray", mats["walnut_solid"])
    b.add_box(-14.12, 1.08, -4.68, 0.34, 0.04, 0.52)
    b = ctx.mb("KitchenGranolaBars", mats["terracotta"])
    for z in (-4.82, -4.68, -4.54):
        b.add_box(-14.12, 1.13, z, 0.26, 0.06, 0.10)
    b = ctx.mb("KitchenGranolaNuts", mats["cognac_suede"])
    for z in (-4.82, -4.68, -4.54):
        b.add_sphere(-14.12, 1.17, z, 0.05, 0.03, 0.05, rings=6, segs=8)

    build_french_fridge(ctx, mats)

    # South bay - recessed hollow wine cellar behind smoked glass door
    b = ctx.mb("KitchenWineCellarFrame", mats["gunmetal"])
    b.add_box(-14.80, 1.35, -1.165, 0.06, 2.50, 1.83)   # back wall
    b.add_box(-14.35, 0.12, -1.165, 0.96, 0.06, 1.83)   # bottom plinth
    b.add_box(-14.35, 2.58, -1.165, 0.96, 0.06, 1.83)   # top header
    b.add_box(-14.35, 1.35, -2.06, 0.96, 2.50, 0.06)    # left side
    b.add_box(-14.35, 1.35, -0.27, 0.96, 2.50, 0.06)    # right side
    b = ctx.mb("KitchenWineCellarDoor", mats["glass_smoke"])
    b.add_box(-13.86, 1.35, -1.165, 0.03, 2.40, 1.72)
    b = ctx.mb("KitchenWineCellarLight", mats["warm_led"])
    b.add_box(-14.74, 1.35, -1.96, 0.03, 2.25, 0.04)
    b.add_box(-14.74, 1.35, -0.37, 0.03, 2.25, 0.04)
    b = ctx.mb("KitchenWineShelves", mats["burgundy"])
    for y in (0.55, 0.95, 1.35, 1.75, 2.15, 2.55):
        b.add_box(-14.30, y, -1.165, 0.80, 0.05, 1.70)
    b = ctx.mb("KitchenWineBottles", mats["wine_bottle"])
    for y in (0.62, 1.02, 1.42, 1.82, 2.22, 2.62):
        for z in (-1.55, -1.20, -0.85):
            b.add_cylinder(-14.30, y, z, 0.035, 0.035, 0.28, segs=12, rot_x=1.5708)
    b = ctx.mb("KitchenWineCaps", mats["brass"])
    for y in (0.62, 1.02, 1.42, 1.82, 2.22, 2.62):
        for z in (-1.55, -1.20, -0.85):
            b.add_cylinder(-14.30, y, z + 0.14, 0.036, 0.036, 0.03, segs=12, rot_x=1.5708)

    # ---------- 3. Waterfall island ----------
    b = ctx.mb("KitchenIslandStone", mats["calacatta_viola"])
    b.add_rounded_box(-10.4, 0.89, -9.8, 1.60, 0.06, 6.80, bevel=0.015)
    b.add_box(-10.4, 0.45, -13.13, 1.60, 0.90, 0.14)
    b.add_box(-10.4, 0.45, -6.47, 1.60, 0.90, 0.14)
    b = ctx.mb("KitchenIslandCore", mats["rift_oak"])
    b.add_box(-10.68, 0.46, -9.8, 0.96, 0.80, 6.40)
    b = ctx.mb("KitchenIslandPlinth", mats["brass"])
    b.add_box(-10.68, 0.03, -9.8, 0.92, 0.06, 6.36)

    b = ctx.mb("KitchenTeppanyaki", mats["charcoal"])
    b.add_box(-10.55, 0.929, -8.0, 0.72, 0.014, 1.15)
    b = ctx.mb("KitchenTeppanyakiBezel", mats["chrome"])
    b.add_box(-10.55, 0.926, -8.0, 0.76, 0.010, 1.19)

    b = ctx.mb("KitchenSteakBoard", mats["walnut_solid"])
    b.add_box(-10.52, 0.945, -10.3, 0.62, 0.05, 0.92)
    b = ctx.mb("KitchenRawSteaks", mats["steak_marbled"])
    for z in (-10.55, -10.30, -10.05):
        b.add_rounded_box(-10.52, 0.985, z, 0.42, 0.03, 0.18, bevel=0.012)
    b = ctx.mb("KitchenSaltBowl", mats["ceramic_white"])
    b.add_cylinder(-10.30, 0.97, -10.30, 0.05, 0.06, 0.04, segs=14)

    b = ctx.mb("KitchenPourBottle", mats["wine_bottle"])
    b.add_lathe(-10.55, 0.92, -12.10, [(0, 0), (0.045, 0), (0.045, 0.18), (0.02, 0.28), (0.016, 0.32), (0, 0.32)])
    b = ctx.mb("KitchenPourFoil", mats["brass"])
    b.add_cylinder(-10.55, 1.18, -12.10, 0.020, 0.020, 0.06, segs=12)

    b = ctx.mb("KitchenWineDecanter", mats["crystal_glass"])
    b.add_lathe(-10.22, 0.92, -12.06, [(0, 0), (0.10, 0), (0.10, 0.06), (0.05, 0.14), (0.03, 0.22), (0.03, 0.26), (0, 0.26)])
    b = ctx.mb("KitchenDecanterWine", mats["champagne_liquid"])
    b.add_cylinder(-10.22, 0.96, -12.06, 0.085, 0.085, 0.02, segs=16)
    b = ctx.mb("KitchenCoupes", mats["crystal_glass"])
    for z in (-11.74, -12.36):
        b.add_lathe(-10.14, 0.92, z, [(0, 0), (0.04, 0), (0.04, 0.01), (0.01, 0.02), (0.01, 0.10), (0.05, 0.14), (0.05, 0.16), (0, 0.16)])

    b = ctx.mb("KitchenYogurtBowl", mats["ceramic_white"])
    b.add_cylinder(-9.92, 0.92, -8.8, 0.09, 0.11, 0.07, segs=16)
    b = ctx.mb("KitchenBerriesBlue", mats["berry_blue"])
    for dz in (-0.03, 0.02):
        b.add_sphere(-9.92, 0.99, -8.8 + dz, 0.025, 0.025, 0.025, rings=6, segs=8)
    b = ctx.mb("KitchenBerriesRed", mats["berry_red"])
    b.add_sphere(-9.90, 0.99, -8.78, 0.025, 0.025, 0.025, rings=6, segs=8)

    b = ctx.mb("KitchenBruceDish", mats["brass"])
    b.add_cylinder(-9.25, 0.0, -13.25, 0.16, 0.18, 0.06, segs=18)
    b = ctx.mb("KitchenBruceDishInner", mats["travertine"])
    b.add_cylinder(-9.25, 0.04, -13.25, 0.13, 0.13, 0.02, segs=18)

    # ---------- 4. Bar stools + pendant ----------
    b = ctx.mb("KitchenBarStoolLegs", mats["walnut_solid"])
    for z in (-7.6, -9.8, -12.0):
        for dx in (-0.14, 0.14):
            for dz in (-0.14, 0.14):
                b.add_cylinder(-9.16 + dx, 0.0, z + dz, 0.018, 0.018, 0.62, segs=10)
    b = ctx.mb("KitchenBarStoolRings", mats["brass"])
    for z in (-7.6, -9.8, -12.0):
        b.add_cylinder(-9.16, 0.24, z, 0.20, 0.20, 0.02, segs=18)
    b = ctx.mb("KitchenBarStoolSeats", mats["cognac_suede"])
    for z in (-7.6, -9.8, -12.0):
        b.add_rounded_box(-9.16, 0.67, z, 0.42, 0.08, 0.42, bevel=0.03)
    b = ctx.mb("KitchenBarStoolBacks", mats["burgundy"])
    for z in (-7.6, -9.8, -12.0):
        b.add_rounded_box(-9.16, 0.80, z - 0.18, 0.40, 0.22, 0.06, bevel=0.02)

    b = ctx.mb("KitchenLinearPendant", mats["brass"])
    b.add_box(-10.4, 2.44, -9.8, 0.08, 0.06, 4.80)
    b = ctx.mb("KitchenPendantDiffuser", mats["warm_led"])
    b.add_box(-10.4, 2.40, -9.8, 0.06, 0.02, 4.70)
    b = ctx.mb("KitchenPendantRods", mats["brass"])
    for z in (-12.0, -7.6):
        b.add_cylinder(-10.4, 2.47, z, 0.012, 0.012, 6.61, segs=8)
