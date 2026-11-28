import math


def build_south_cellar_and_cookware(ctx, mats):
    # ================= 1. OPEN-FRONT 8-ESTATE WINE CELLAR (Z in [25.2..34.8]) =================
    b = ctx.mb("WineCellarFrame", mats["walnut_fluted"])
    b.add_box(-14.68, 4.40, 30.00, 0.22, 8.80, 9.60)
    b.add_box(-13.50, 0.14, 30.00, 2.40, 0.28, 9.60)
    b.add_box(-13.50, 8.58, 30.00, 2.40, 0.24, 9.60)
    for zz in (25.24, 28.42, 31.60, 34.76):
        b.add_box(-13.50, 4.40, zz, 2.38, 8.40, 0.12)
    b = ctx.mb("CellarCove", mats["warm_led"])
    b.add_box(-14.48, 4.40, 30.00, 0.04, 7.80, 9.00)
    b = ctx.mb("WineShelves", mats["rift_oak"])
    for yy in (2.25, 3.85, 5.45):
        b.add_box(-13.55, yy, 30.00, 2.00, 0.08, 9.20)

    estates = [
        ("DomPerignon", "wine_bottle", "brass", 0.145, 0.44, 0.76, 0, 0),
        ("Cristal", "champagne_liquid", "brass", 0.135, 0.48, 0.78, 1, 0),
        ("Krug", "amber_wine", "charcoal", 0.160, 0.40, 0.74, 2, 0),
        ("DRC", "burgundy_glass", "wolf_red", 0.150, 0.36, 0.72, 3, 0),
        ("Petrus", "burgundy_glass", "brass", 0.138, 0.50, 0.76, 0, 1),
        ("Lafite", "wine_bottle", "wolf_red", 0.175, 0.56, 0.88, 1, 1),
        ("OpusOne", "obsidian_bezel", "steel", 0.145, 0.48, 0.76, 2, 1),
        ("Yquem", "champagne_liquid", "brass", 0.130, 0.46, 0.74, 3, 1),
    ]
    for i, (nm, gkey, ckey, r, sh, ht, col, row) in enumerate(estates):
        z = 25.85 + i * 1.16
        u0, v0 = col * 0.25 + 0.01, row * 0.50 + 0.02
        u1, v1 = u0 + 0.23, v0 + 0.46
        for by in (2.29, 3.89):
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

    b = ctx.mb("WineCrates", mats["rift_oak"])
    for zz in (26.4, 29.2, 32.0, 33.9):
        b.add_box(-13.65, 1.35, zz, 1.2, 0.65, 1.35)
    b = ctx.mb("CrystalDecanters", mats["crystal_glass"])
    for zz in (27.4, 32.6):
        b.add_lathe(-13.10, 2.29, zz, [(0.0, 0.0), (0.28, 0.0), (0.34, 0.08),
                                       (0.16, 0.30), (0.08, 0.50), (0.07, 0.72), (0.14, 0.80), (0.0, 0.82)], segs=18)
    ctx.mb("MagnumCradle", mats["rift_oak"]).add_box(-13.45, 2.33, 25.85 + 5 * 1.16, 0.65, 0.12, 0.55)
    ctx.mb("WineCellarGlass", mats["glass"]).add_box(-12.28, 4.5, 30.0, 0.04, 7.9, 9.2)

    # ================= 2. 7-PIECE COOKWARE SUITE ON WOLF 6-BURNER RANGE =================
    b = ctx.mb("LeCreusetDutchOven", mats["le_creuset_red"])
    b.add_lathe(-13.05, 2.44, 18.85, [(0.0, 0.0), (0.42, 0.0), (0.46, 0.08), (0.46, 0.42), (0.40, 0.46), (0.0, 0.46)], segs=22)
    b.add_lathe(-13.05, 2.90, 18.85, [(0.0, 0.0), (0.42, 0.0), (0.36, 0.14), (0.14, 0.22), (0.0, 0.23)], segs=20)
    ctx.mb("LeCreusetKnob", mats["brass"]).add_sphere(-13.05, 3.16, 18.85, 0.075, 0.06, 0.075, rings=8, segs=12)

    b = ctx.mb("MauvielCopperStockpot", mats["copper_cook"])
    b.add_lathe(-14.00, 2.44, 18.95, [(0.0, 0.0), (0.40, 0.0), (0.40, 0.66), (0.37, 0.68), (0.0, 0.68)], segs=22)
    b.add_lathe(-14.00, 3.12, 18.95, [(0.0, 0.0), (0.38, 0.0), (0.32, 0.09), (0.0, 0.12)], segs=20)
    ctx.mb("MauvielBrassHandles", mats["brass"]).add_sphere(-14.00, 3.28, 18.95, 0.07, 0.06, 0.07, rings=8, segs=12)

    b = ctx.mb("CastIronGrillPan", mats["charcoal"])
    b.add_box(-13.45, 2.51, 20.50, 0.92, 0.14, 0.92)
    b.add_cylinder(-12.88, 2.54, 20.50, 0.04, 0.04, 0.56, segs=10, rot_z=-1.35)
    bs = ctx.mb("WolfRibeyes", mats["steak_marbled"])
    bs.add_rounded_box(-13.55, 2.61, 20.30, 0.34, 0.09, 0.24, bevel=0.02)
    bs.add_rounded_box(-13.35, 2.61, 20.70, 0.34, 0.09, 0.24, bevel=0.02)

    b = ctx.mb("CarbonSteelWok", mats["obsidian_bezel"])
    b.add_lathe(-13.00, 2.44, 22.05, [(0.0, 0.0), (0.16, 0.0), (0.38, 0.20), (0.48, 0.34), (0.46, 0.36), (0.0, 0.36)], segs=22)
    ctx.mb("WokHandle", mats["rift_oak"]).add_cylinder(-12.50, 2.74, 22.05, 0.045, 0.045, 0.56, segs=10, rot_z=-1.3)

    b = ctx.mb("StainlessSaucier", mats["steel"])
    b.add_lathe(-14.00, 2.44, 21.95, [(0.0, 0.0), (0.32, 0.0), (0.36, 0.12), (0.36, 0.32), (0.32, 0.34), (0.0, 0.34)], segs=20)
    b.add_cylinder(-13.56, 2.68, 21.95, 0.035, 0.035, 0.62, segs=10, rot_z=-1.3)

    # ================= 3. BRASS POT RAIL, HANGING PANS & SWING-ARM POT-FILLER =================
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

    pf = ctx.mb("WolfPotFiller", mats["brass"])
    pf.add_cylinder(-14.56, 3.65, 20.50, 0.11, 0.11, 0.12, segs=14, rot_z=math.pi / 2)
    pf.add_sphere(-14.48, 3.65, 20.50, 0.08, 0.08, 0.08, rings=8, segs=10)
    pf.add_cylinder(-14.48, 3.65, 20.50, 0.042, 0.042, 0.56, segs=10, rot_z=-math.pi / 2)
    pf.add_sphere(-13.92, 3.65, 20.50, 0.07, 0.07, 0.07, rings=8, segs=10)
    pf.add_cylinder(-13.92, 3.65, 20.50, 0.036, 0.036, 0.42, segs=10, rot_z=-math.pi / 2)
    pf.add_cylinder(-13.50, 3.35, 20.50, 0.032, 0.026, 0.32, segs=10)

    # ================= 4. HIMALAYAN PINK-SALT DRY-AGING STEAK CABINET (OPEN VITRINE) =================
    dc = ctx.mb("DryAgeSteakCabinet", mats["obsidian_bezel"])
    dc.add_box(-14.62, 4.30, 16.55, 0.14, 8.60, 1.70)
    dc.add_box(-13.50, 0.90, 16.55, 2.25, 1.80, 1.70)
    dc.add_box(-13.50, 7.60, 16.55, 2.25, 2.00, 1.70)
    for zz in (15.78, 17.32):
        dc.add_box(-13.50, 4.20, zz, 2.25, 4.80, 0.14)
    ctx.mb("DryAgeHandle", mats["steel"]).add_cylinder(-12.28, 3.10, 17.16, 0.035, 0.035, 2.40, segs=12)
    ctx.mb("DryAgeTempBadge", mats["warm_bulb"]).add_box(-12.34, 6.72, 16.55, 0.05, 0.24, 0.56)
    ctx.mb("DryAgeSaltWall", mats["himalayan_salt"]).add_box(-14.46, 4.20, 16.55, 0.12, 4.70, 1.38)
    led = ctx.mb("DryAgeLEDStrips", mats["warm_led"])
    led.add_box(-14.36, 4.20, 15.92, 0.06, 4.70, 0.06)
    led.add_box(-14.36, 4.20, 17.18, 0.06, 4.70, 0.06)
    rk = ctx.mb("DryAgeRacks", mats["steel"])
    st = ctx.mb("DryAgeSteaks", mats["steak_marbled"])
    for yy in (2.55, 3.85, 5.15):
        rk.add_box(-13.35, yy, 16.55, 1.65, 0.04, 1.24)
        for zz in (16.22, 16.88):
            st.add_rounded_box(-13.30, yy + 0.11, zz, 0.62, 0.16, 0.36, bevel=0.04)
    ctx.mb("DryAgeFrontGlass", mats["glass"]).add_box(-12.36, 4.20, 16.55, 0.04, 4.80, 1.42)

    # ================= 5. DAMASCUS KNIFE STRIP + ISLAND BERKEL SLICER & MISE-EN-PLACE =================
    ctx.mb("DamascusKnifeRack", mats["walnut_fluted"]).add_box(-14.56, 3.65, 22.72, 0.08, 0.18, 1.75)
    bl = ctx.mb("DamascusBlades", mats["steel"])
    bs = ctx.mb("DamascusBolsters", mats["walnut_fluted"])
    for i, ln in enumerate((0.46, 0.42, 0.38, 0.34, 0.30, 0.26, 0.22)):
        zz = 21.98 + i * 0.24
        bl.add_box(-14.48, 3.42 - ln * 0.4, zz, 0.02, ln, 0.075)
        bs.add_box(-14.48, 3.65 + 0.14, zz, 0.045, 0.22, 0.055)

    bk = ctx.mb("BerkelSlicer", mats["wolf_red"])
    bk.add_box(6.20, 2.46, 20.50, 0.56, 0.12, 0.68)
    bk.add_cylinder(6.20, 2.52, 20.50, 0.18, 0.14, 0.38, segs=16)
    bk.add_cylinder(6.20, 2.94, 20.88, 0.42, 0.42, 0.045, segs=24, rot_x=math.pi / 2)
    ctx.mb("BerkelBlade", mats["steel"]).add_cylinder(6.20, 2.94, 20.44, 0.38, 0.38, 0.025, segs=28, rot_x=math.pi / 2)
    ctx.mb("BerkelKnob", mats["brass"]).add_sphere(6.20, 3.28, 20.92, 0.055, 0.055, 0.055, rings=8, segs=10)
    ctx.mb("BerkelTray", mats["steel"]).add_box(5.78, 2.43, 20.50, 0.38, 0.04, 0.46)

    mm = ctx.mb("MarbleMortar", mats["travertine"])
    mm.add_lathe(5.00, 2.40, 22.10, [(0.0, 0.0), (0.16, 0.0), (0.20, 0.10), (0.22, 0.22), (0.17, 0.22), (0.0, 0.06)], segs=20)
    mm.add_cylinder(5.04, 2.52, 22.14, 0.035, 0.045, 0.24, segs=10, rot_z=-0.38)
    cr = ctx.mb("BrassCruets", mats["brass"])
    for dx in (-0.12, 0.12):
        cr.add_lathe(5.40 + dx, 2.40, 18.80, [(0.0, 0.0), (0.08, 0.0), (0.09, 0.10), (0.04, 0.28), (0.03, 0.34)], segs=12)
    cl = ctx.mb("TruffleCloche", mats["steel"])
    cl.add_lathe(4.20, 2.40, 18.90, [(0.0, 0.0), (0.24, 0.0), (0.23, 0.12), (0.16, 0.24), (0.0, 0.28)], segs=20)
    cl.add_sphere(4.20, 2.70, 18.90, 0.045, 0.045, 0.045, rings=8, segs=10)
