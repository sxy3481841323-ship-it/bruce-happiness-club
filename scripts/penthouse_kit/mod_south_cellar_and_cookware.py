def build_south_cellar_and_cookware(ctx, mats):
    # ================= 1. DIVERSE 8-ESTATE WINE CELLAR (Z in [25.2..34.8]) =================
    b = ctx.mb("CellarWalnut", mats["walnut_fluted"])
    b.add_box(-14.68, 4.4, 30.0, 0.24, 8.8, 9.6)
    b = ctx.mb("CellarFrame", mats["obsidian_bezel"])
    for cz in (25.25, 28.45, 31.65, 34.75):
        b.add_box(-13.45, 4.4, cz, 2.40, 8.2, 0.12)
    b = ctx.mb("CellarOakShelves", mats["rift_oak"])
    for y in (2.2, 3.8, 5.4, 7.0):
        b.add_box(-13.60, y, 30.0, 1.90, 0.08, 9.2)
    b = ctx.mb("CellarCove", mats["warm_led"])
    b.add_box(-14.48, 4.4, 30.0, 0.04, 7.8, 9.0)

    b = ctx.mb("WineCrates", mats["rift_oak"])
    for z in (26.2, 29.0, 31.8, 33.9):
        b.add_box(-13.65, 1.35, z, 1.2, 0.65, 1.35)
    b = ctx.mb("CrystalDecanters", mats["crystal_glass"])
    for z in (27.4, 32.6):
        b.add_lathe(-13.10, 2.24, z, [(0.0, 0.0), (0.28, 0.0), (0.34, 0.08),
                                      (0.16, 0.30), (0.08, 0.50), (0.07, 0.72), (0.14, 0.80), (0.0, 0.82)], segs=18)

    # 8 genuinely distinct estate bottle shapes, glass tints, capsule colors, and UV cells
    estates = [
        ("DomPerignon", "wine_bottle", "brass", 0.145, 0.44, 0.76, 0, 0),
        ("Cristal", "champagne_liquid", "brass", 0.135, 0.48, 0.78, 1, 0),
        ("Krug", "amber_wine", "charcoal", 0.160, 0.40, 0.74, 2, 0),
        ("DRC", "burgundy_glass", "wolf_red", 0.150, 0.36, 0.72, 3, 0),
        ("Petrus", "burgundy_glass", "brass", 0.138, 0.50, 0.76, 0, 1),
        ("Lafite", "wine_bottle", "wolf_red", 0.175, 0.56, 0.88, 1, 1),  # 1.5L Magnum size
        ("OpusOne", "obsidian_bezel", "steel", 0.145, 0.48, 0.76, 2, 1),
        ("Yquem", "champagne_liquid", "brass", 0.130, 0.46, 0.74, 3, 1),
    ]
    for i, (nm, gkey, ckey, r, sh, ht, col, row) in enumerate(estates):
        z = 25.85 + i * 1.16
        u0, v0 = col * 0.25 + 0.01, row * 0.50 + 0.02
        u1, v1 = u0 + 0.23, v0 + 0.46
        for by in (2.25, 3.85):
            bx = -13.45 if by < 3.0 else -13.55
            bg = ctx.mb("Bottle_" + nm, mats[gkey])
            prof = [(0.0, 0.0), (r, 0.0), (r, ht * 0.56), (r * 0.88, sh),
                    (r * 0.42, sh + 0.09), (r * 0.38, ht), (0.0, ht)]
            bg.add_lathe(bx, by, z, prof, segs=16)
            bc = ctx.mb("Cap_" + nm, mats[ckey])
            bc.add_cylinder(bx, by + ht * 0.88, z, r * 0.40, r * 0.40, ht * 0.14, segs=12)
            bl = ctx.mb("Label_" + nm, mats["prestige_wine_labels"])
            lx = bx + r + 0.015
            p0 = (lx, by + ht * 0.14, z - r * 0.92)
            p1 = (lx, by + ht * 0.14, z + r * 0.92)
            p2 = (lx, by + ht * 0.54, z + r * 0.92)
            p3 = (lx, by + ht * 0.54, z - r * 0.92)
            bl.add_tri_raw(p0, p1, p2, (u0, v0), (u1, v0), (u1, v1), (1, 0, 0), (1, 0, 0), (1, 0, 0))
            bl.add_tri_raw(p0, p2, p3, (u0, v0), (u1, v1), (u0, v1), (1, 0, 0), (1, 0, 0), (1, 0, 0))
    ctx.mb("MagnumCradle", mats["rift_oak"]).add_box(-13.45, 2.29, 25.85 + 5 * 1.16, 0.65, 0.12, 0.55)
    ctx.mb("WineCellarGlass", mats["glass"]).add_box(-12.28, 4.5, 30.0, 0.04, 7.9, 9.2)

    # ================= 2. 7-PIECE COOKWARE SUITE ON WOLF 6-BURNER RANGE =================
    # Wolf range grates top Y = 2.44, X in [-14.4.. -12.6], Z in [18.3..22.7]
    # 1) Flame-Red Le Creuset Oval Dutch Oven (front-left burner)
    b = ctx.mb("LeCreusetDutchOven", mats["le_creuset_red"])
    b.add_lathe(-13.05, 2.44, 18.85, [(0.0, 0.0), (0.42, 0.0), (0.46, 0.08), (0.46, 0.42), (0.40, 0.46), (0.0, 0.46)], segs=22)
    b.add_lathe(-13.05, 2.90, 18.85, [(0.0, 0.0), (0.42, 0.0), (0.36, 0.14), (0.14, 0.22), (0.0, 0.23)], segs=20)
    ctx.mb("LeCreusetKnob", mats["brass"]).add_sphere(-13.05, 3.16, 18.85, 0.075, 0.06, 0.075, rings=8, segs=12)

    # 2) Hammered Mauviel Copper Stockpot (rear-left burner)
    b = ctx.mb("MauvielCopperStockpot", mats["copper_cook"])
    b.add_lathe(-14.00, 2.44, 18.95, [(0.0, 0.0), (0.40, 0.0), (0.40, 0.66), (0.37, 0.68), (0.0, 0.68)], segs=22)
    b.add_lathe(-14.00, 3.12, 18.95, [(0.0, 0.0), (0.38, 0.0), (0.32, 0.09), (0.0, 0.12)], segs=20)
    ctx.mb("MauvielBrassHandles", mats["brass"]).add_sphere(-14.00, 3.28, 18.95, 0.07, 0.06, 0.07, rings=8, segs=12)

    # 3) Matte-Black Cast-Iron Ribbed Grill Pan + 2 Ribeyes (center griddle Z=20.5)
    b = ctx.mb("CastIronGrillPan", mats["charcoal"])
    b.add_box(-13.45, 2.51, 20.50, 0.92, 0.14, 0.92)
    b.add_cylinder(-12.88, 2.54, 20.50, 0.04, 0.04, 0.56, segs=10, rot_z=-1.35)
    bs = ctx.mb("WolfRibeyes", mats["steak_marbled"])
    bs.add_rounded_box(-13.55, 2.61, 20.30, 0.34, 0.09, 0.24, bevel=0.02)
    bs.add_rounded_box(-13.35, 2.61, 20.70, 0.34, 0.09, 0.24, bevel=0.02)

    # 4) Carbon-Steel Wok with oak handle (front-right burner)
    b = ctx.mb("CarbonSteelWok", mats["obsidian_bezel"])
    b.add_lathe(-13.00, 2.44, 22.05, [(0.0, 0.0), (0.16, 0.0), (0.38, 0.20), (0.48, 0.34), (0.46, 0.36), (0.0, 0.36)], segs=22)
    ctx.mb("WokHandle", mats["rift_oak"]).add_cylinder(-12.50, 2.74, 22.05, 0.045, 0.045, 0.56, segs=10, rot_z=-1.3)

    # 5) 5-Ply Brushed Stainless Saucier (rear-right burner)
    b = ctx.mb("StainlessSaucier", mats["steel"])
    b.add_lathe(-14.00, 2.44, 21.95, [(0.0, 0.0), (0.32, 0.0), (0.36, 0.12), (0.36, 0.32), (0.32, 0.34), (0.0, 0.34)], segs=20)
    b.add_cylinder(-13.56, 2.68, 21.95, 0.035, 0.035, 0.62, segs=10, rot_z=-1.3)

    # ================= 3. BRASS BACKSPLASH POT RAIL + HANGING COPPER PANS =================
    pr = ctx.mb("BackSplashPotRail", mats["brass"])
    pr.add_cylinder(-14.48, 4.95, 17.90, 0.045, 0.045, 5.20, segs=12, rot_x=1.5708)
    for pz in (18.4, 20.5, 22.6):
        pr.add_box(-14.56, 4.95, pz, 0.18, 0.06, 0.06)
    for pz, r in ((18.8, 0.28), (20.1, 0.34), (21.5, 0.25)):
        hp = ctx.mb("HangingCopperPan", mats["copper_cook"])
        hp.add_cylinder(-14.42, 4.00, pz, r, r, 0.12, segs=18, rot_z=1.5708)
        hp.add_cylinder(-14.42, 4.35, pz, 0.025, 0.025, 0.58, segs=8)
    lt = ctx.mb("BrassUtensils", mats["brass"])
    lt.add_cylinder(-14.42, 4.18, 22.45, 0.022, 0.022, 0.72, segs=8)
    lt.add_sphere(-14.42, 4.14, 22.45, 0.05, 0.10, 0.10, rings=8, segs=10)

    # ================= 4. ISLAND INDUCTION COCOTTE & COPPER KETTLE =================
    ic = ctx.mb("IslandCocotte", mats["porcelain_white"])
    ic.add_lathe(-1.6, 2.42, 20.4, [(0.0, 0.0), (0.34, 0.0), (0.36, 0.08), (0.36, 0.36), (0.32, 0.40), (0.0, 0.40)], segs=20)
    ic.add_lathe(-1.6, 2.82, 20.4, [(0.0, 0.0), (0.32, 0.0), (0.28, 0.10), (0.0, 0.16)], segs=18)
    ctx.mb("IslandCocotteKnob", mats["brass"]).add_sphere(-1.6, 3.00, 20.4, 0.06, 0.05, 0.06, rings=8, segs=10)
    ik = ctx.mb("IslandTeaKettle", mats["copper_cook"])
    ik.add_lathe(-2.5, 2.42, 20.5, [(0.0, 0.0), (0.26, 0.0), (0.28, 0.10), (0.24, 0.28), (0.14, 0.36), (0.0, 0.38)], segs=18)
    ik.add_curved_tube([(-2.5, 2.80, 20.32), (-2.5, 3.02, 20.5), (-2.5, 2.80, 20.68)], [0.025, 0.025, 0.025], segs=8)
