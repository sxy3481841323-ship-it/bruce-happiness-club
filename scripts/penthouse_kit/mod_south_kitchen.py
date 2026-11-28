from penthouse_kit.mod_south_fridge import build_south_french_fridge


def build_south_kitchen(ctx, mats):
    # ---------------- Architectural shell ----------------
    b = ctx.mb("KitchenFloorGrey", mats["tundra_grey"])
    b.add_box(0.0, -0.06, 22.1, 30.4, 0.12, 13.6, uv_tile=4.0)
    b = ctx.mb("KitchenFloorInlay", mats["platinum"])
    b.add_box(0.0, 0.015, 15.55, 27.2, 0.02, 0.08)

    b = ctx.mb("KitchenCeiling", mats["tundra_grey"])
    b.add_box(0.0, 8.85, 22.1, 30.4, 0.25, 13.6, uv_tile=4.0)
    b = ctx.mb("KitchenCeilingCove", mats["warm_led"])
    for x in (-14.0, 14.0):
        b.add_box(x, 8.70, 22.0, 0.10, 0.06, 12.0)
    for z in (16.0, 28.0):
        b.add_box(0.0, 8.70, z, 28.0, 0.06, 0.10)

    b = ctx.mb("KitchenSideWalls", mats["graphite_slate"])
    b.add_box(14.9, 4.42, 22.1, 0.30, 8.85, 13.6)
    b.add_box(-14.9, 4.42, 22.1, 0.30, 8.85, 13.6)

    # ---------------- South wall + French doors ----------------
    b = ctx.mb("KitchenSouthStoneWall", mats["pietra_grey"])
    b.add_box(-12.9, 4.42, 28.6, 4.2, 8.85, 0.40)
    b.add_box(12.9, 4.42, 28.6, 4.2, 8.85, 0.40)
    b.add_box(0.0, 8.38, 28.6, 21.8, 0.96, 0.40)

    b = ctx.mb("KitchenFrenchFrames", mats["graphite_slate"])
    b.add_box(0.0, 0.10, 28.6, 21.8, 0.10, 0.30)
    b.add_box(0.0, 7.90, 28.6, 21.8, 0.10, 0.30)
    for x in (-10.8, -3.6, 3.6, 10.8):
        b.add_box(x, 4.0, 28.6, 0.14, 7.80, 0.30)
    b.add_box(0.0, 6.20, 28.6, 21.6, 0.12, 0.28)
    for x in (-8.4, -6.0, -1.2, 1.2, 6.0, 8.4):
        b.add_box(x, 4.0, 28.6, 0.09, 7.70, 0.24)
    # slid center bay panel frame
    b.add_box(2.2, 4.0, 28.38, 7.1, 0.10, 0.22)
    b.add_box(2.2, 7.85, 28.38, 7.1, 0.10, 0.22)
    b.add_box(-1.35, 4.0, 28.38, 0.10, 7.75, 0.22)
    b.add_box(5.75, 4.0, 28.38, 0.10, 7.75, 0.22)

    b = ctx.mb("KitchenFrenchTrim", mats["platinum"])
    b.add_box(0.0, 0.04, 28.6, 21.8, 0.08, 0.44)
    b.add_box(-1.35, 3.60, 28.30, 0.06, 1.20, 0.10)
    b.add_box(5.75, 3.60, 28.30, 0.06, 1.20, 0.10)

    b = ctx.mb("KitchenFrenchGlass", mats["glass"])
    b.add_box(-7.2, 4.0, 28.6, 7.1, 7.75, 0.04)
    b.add_box(2.2, 4.0, 28.38, 7.1, 7.75, 0.04)
    b.add_box(7.2, 4.0, 28.6, 7.1, 7.75, 0.04)

    # ---------------- East tall wall ----------------
    b = ctx.mb("KitchenTallUpperWall", mats["graphite_slate"])
    b.add_box(13.72, 8.03, 22.0, 2.15, 1.54, 12.6)
    b = ctx.mb("KitchenTallWallInlays", mats["platinum"])
    b.add_box(13.72, 7.26, 22.0, 2.16, 0.05, 12.6)

    # North bay: wine & champagne cellar
    b = ctx.mb("KitchenWineCellarFrame", mats["graphite_slate"])
    b.add_box(14.70, 3.69, 17.58, 0.10, 7.06, 3.47)
    b.add_box(13.72, 7.22, 17.58, 2.10, 0.10, 3.47)
    b.add_box(13.72, 0.16, 17.58, 2.10, 0.10, 3.47)
    b.add_box(13.72, 3.69, 15.85, 2.10, 7.06, 0.10)
    b.add_box(13.72, 3.69, 19.32, 2.10, 7.06, 0.10)
    b = ctx.mb("KitchenWineCellarDoor", mats["glass_smoke"])
    b.add_box(12.68, 3.69, 17.58, 0.05, 6.90, 3.30)
    b = ctx.mb("KitchenWineCellarLight", mats["warm_led"])
    for z in (16.0, 19.15):
        b.add_box(14.60, 3.69, z, 0.05, 6.80, 0.06)
    b = ctx.mb("KitchenWineShelves", mats["burgundy"])
    for y in (1.2, 2.2, 3.2, 4.2, 5.2, 6.2):
        b.add_box(13.72, y, 17.58, 1.90, 0.06, 3.30)
    b = ctx.mb("KitchenWineBottles", mats["wine_bottle"])
    for y in (1.2, 2.2, 3.2, 4.2, 5.2, 6.2):
        for i in range(4):
            z = 16.15 + i * 0.85
            b.add_cylinder(13.72, y + 0.03, z, 0.10, 0.10, 0.82, segs=12)
    b = ctx.mb("KitchenWineCaps", mats["platinum"])
    for y in (1.2, 2.2, 3.2, 4.2, 5.2, 6.2):
        for i in range(4):
            z = 16.15 + i * 0.85
            b.add_cylinder(13.72, y + 0.85, z, 0.055, 0.055, 0.06, segs=10)

    # Center bay: fridge
    build_south_french_fridge(ctx, mats)

    # South bay: espresso & granola alcove
    b = ctx.mb("KitchenSouthBase", mats["graphite_slate"])
    b.add_box(13.72, 1.15, 26.40, 2.10, 2.30, 3.50)
    b = ctx.mb("KitchenEspressoAlcove", mats["pietra_grey"])
    b.add_box(13.72, 2.32, 26.40, 2.10, 0.10, 3.50)
    b.add_box(14.70, 3.80, 26.40, 0.10, 2.90, 3.50)
    b.add_box(13.72, 3.80, 24.70, 2.10, 2.90, 0.10)
    b.add_box(13.72, 3.80, 28.10, 2.10, 2.90, 0.10)
    b = ctx.mb("KitchenEspressoCove", mats["warm_led"])
    b.add_box(13.72, 5.18, 26.40, 1.90, 0.05, 3.20)
    b = ctx.mb("KitchenEspressoMachine", mats["graphite_slate"])
    b.add_box(13.15, 2.86, 26.20, 0.96, 0.98, 1.15)
    b = ctx.mb("KitchenEspressoChrome", mats["platinum"])
    b.add_box(12.68, 2.86, 26.20, 0.06, 0.90, 1.05)
    b.add_box(13.15, 3.42, 26.20, 0.70, 0.20, 0.70)
    b = ctx.mb("KitchenEspressoLevers", mats["brass"])
    b.add_box(12.72, 3.02, 26.20, 0.14, 0.06, 0.06)
    b.add_box(12.65, 3.02, 26.20, 0.06, 0.06, 0.30)
    b = ctx.mb("KitchenEspressoCup", mats["ceramic_white"])
    b.add_cylinder(12.65, 2.34, 26.20, 0.10, 0.12, 0.16, segs=14)
    b = ctx.mb("KitchenGranolaTray", mats["walnut_solid"])
    b.add_box(13.05, 2.38, 27.35, 0.85, 0.08, 1.25)
    b = ctx.mb("KitchenGranolaBars", mats["cognac_suede"])
    for i in range(3):
        b.add_box(13.05, 2.46, 26.95 + i * 0.35, 0.70, 0.08, 0.22)

    # ---------------- West herb & prep gallery ----------------
    b = ctx.mb("KitchenHerbCounter", mats["graphite_slate"])
    b.add_box(-13.7, 1.10, 22.0, 2.0, 2.20, 9.6)
    b = ctx.mb("KitchenHerbCounterTop", mats["pietra_grey"])
    b.add_box(-13.65, 2.26, 22.0, 2.15, 0.14, 9.8)
    b = ctx.mb("KitchenHerbSink", mats["graphite_slate"])
    b.add_box(-13.6, 2.20, 22.0, 1.30, 0.14, 1.60)
    b = ctx.mb("KitchenHerbFaucet", mats["platinum"])
    b.add_cylinder(-13.6, 2.32, 22.0, 0.05, 0.05, 0.70, segs=12)
    b.add_cylinder(-13.6, 3.02, 22.0, 0.05, 0.05, 0.55, segs=12, rot_x=1.5708)
    b = ctx.mb("KitchenHerbPots", mats["terracotta"])
    for i in range(5):
        z = 18.2 + i * 1.9
        b.add_cylinder(-13.6, 2.33, z, 0.30, 0.36, 0.42, segs=16)
    b = ctx.mb("KitchenHerbFoliage", mats["olive_leaf"])
    b_hb = ctx.mb("KitchenHerbFoliageBright", mats["olive_leaf_bright"])
    for i in range(5):
        z = 18.2 + i * 1.9
        for k, (dx, dy, dz, rr) in enumerate((
            (-0.10, 0.56, -0.10, 0.22), (0.12, 0.62, 0.08, 0.20),
            (-0.04, 0.74, 0.12, 0.18), (0.10, 0.54, -0.12, 0.20),
            (0.00, 0.84 + (i % 2) * 0.10, 0.00, 0.16),
        )):
            tgt = b if (k + i) % 2 == 0 else b_hb
            tgt.add_sphere(-13.6 + dx, 2.33 + dy, z + dz, rr, rr * 1.2, rr, rings=7, segs=10)
    b = ctx.mb("KitchenWestShelf", mats["pietra_grey"])
    b.add_box(-14.1, 4.8, 22.0, 0.55, 0.10, 9.0)

    # ---------------- Waterfall island ----------------
    b = ctx.mb("KitchenIslandStone", mats["pietra_grey"])
    b.add_rounded_box(3.2, 2.24, 19.4, 10.6, 0.16, 2.80, bevel=0.04)
    b.add_box(-1.93, 1.16, 19.4, 0.34, 2.32, 2.80)
    b.add_box(8.33, 1.16, 19.4, 0.34, 2.32, 2.80)
    b = ctx.mb("KitchenIslandCore", mats["graphite_slate"])
    b.add_box(3.2, 1.08, 19.85, 9.9, 2.16, 1.85)

    # Island props
    b = ctx.mb("KitchenTeppanyaki", mats["charcoal"])
    b.add_box(5.8, 2.34, 19.6, 2.40, 0.04, 1.40)
    b = ctx.mb("KitchenTeppanyakiBezel", mats["platinum"])
    b.add_box(5.8, 2.33, 19.6, 2.48, 0.03, 1.48)
    b = ctx.mb("KitchenSteakBoard", mats["walnut_solid"])
    b.add_box(2.8, 2.38, 19.6, 1.65, 0.12, 1.25)
    b = ctx.mb("KitchenRawSteaks", mats["steak_marbled"])
    for x in (2.3, 2.8, 3.3):
        b.add_box(x, 2.48, 19.6, 0.38, 0.08, 0.55)
    b = ctx.mb("KitchenSaltBowl", mats["ceramic_white"])
    b.add_cylinder(3.85, 2.44, 19.6, 0.14, 0.16, 0.10, segs=14)

    b = ctx.mb("KitchenPourBottle", mats["wine_bottle"])
    b.add_lathe(0.10, 2.32, 19.55,
                [(0, 0), (0.12, 0), (0.12, 0.48), (0.055, 0.74), (0.045, 0.88), (0, 0.88)])
    b = ctx.mb("KitchenPourFoil", mats["platinum"])
    b.add_cylinder(0.10, 3.14, 19.55, 0.05, 0.05, 0.06, segs=10)

    b = ctx.mb("KitchenWineDecanter", mats["crystal_glass"])
    b.add_lathe(-0.75, 2.32, 19.50,
                [(0, 0), (0.22, 0), (0.24, 0.18), (0.10, 0.42), (0.06, 0.60), (0, 0.60)])
    b = ctx.mb("KitchenDecanterWine", mats["champagne_liquid"])
    b.add_lathe(-0.75, 2.42, 19.50,
                [(0, 0), (0.20, 0), (0.21, 0.14), (0.09, 0.34), (0, 0.34)])
    b = ctx.mb("KitchenCoupes", mats["crystal_glass"])
    for x in (-0.55, -1.15):
        b.add_lathe(x, 2.32, 18.85,
                    [(0, 0), (0.05, 0), (0.05, 0.10), (0.16, 0.22), (0.16, 0.26), (0, 0.26)])

    b = ctx.mb("KitchenYogurtBowl", mats["ceramic_white"])
    b.add_cylinder(1.2, 2.32, 18.55, 0.26, 0.26, 0.20, segs=16)
    b = ctx.mb("KitchenBerriesBlue", mats["berry_blue"])
    for i in range(4):
        b.add_sphere(1.12 + i * 0.05, 2.50, 18.50 + (i % 2) * 0.08, 0.05, 0.05, 0.05, rings=6, segs=8)
    b = ctx.mb("KitchenBerriesRed", mats["berry_red"])
    for i in range(3):
        b.add_sphere(1.28 + i * 0.04, 2.50, 18.60 - (i % 2) * 0.06, 0.05, 0.05, 0.05, rings=6, segs=8)

    b = ctx.mb("KitchenBruceDish", mats["platinum"])
    b.add_cylinder(-2.8, 0.02, 19.4, 0.38, 0.38, 0.16, segs=18)
    b = ctx.mb("KitchenBruceDishInlay", mats["pietra_grey"])
    b.add_cylinder(-2.8, 0.10, 19.4, 0.30, 0.30, 0.06, segs=18)

    # Stools
    for i, x in enumerate((-0.6, 1.9, 4.5, 7.0)):
        b = ctx.mb("KitchenBarStoolLegs%d" % i, mats["graphite_slate"])
        for dx, dz in ((-0.38, -0.38), (0.38, -0.38), (-0.38, 0.38), (0.38, 0.38)):
            b.add_cylinder(x + dx, 0.0, 17.35 + dz, 0.05, 0.05, 1.60, segs=10)
        b = ctx.mb("KitchenBarStoolRing%d" % i, mats["platinum"])
        b.add_cylinder(x, 0.62, 17.35, 0.44, 0.44, 0.04, segs=18)
        b = ctx.mb("KitchenBarStoolSeat%d" % i, mats["nordic_slate"])
        b.add_rounded_box(x, 1.68, 17.35, 0.95, 0.22, 0.95, bevel=0.06)
        b = ctx.mb("KitchenBarStoolBack%d" % i, mats["nordic_slate"])
        b.add_rounded_box(x, 2.08, 17.75, 0.95, 0.55, 0.16, bevel=0.05)

    # Linear pendant
    b = ctx.mb("KitchenLinearPendant", mats["platinum"])
    b.add_box(3.2, 5.85, 19.4, 8.20, 0.16, 0.26)
    b = ctx.mb("KitchenPendantDiffuser", mats["warm_led"])
    b.add_box(3.2, 5.76, 19.4, 8.00, 0.04, 0.20)
    b = ctx.mb("KitchenPendantRods", mats["platinum"])
    for x in (0.0, 6.4):
        b.add_cylinder(x, 5.93, 19.4, 0.03, 0.03, 2.92, segs=8)
