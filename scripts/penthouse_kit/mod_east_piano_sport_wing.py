import math


def build_east_piano_sport_wing(ctx, mats):
    oak = mats["oak"]
    brass = mats["brass"]
    ebony = mats["ebony_piano"]
    copper = mats["copper_cook"]
    green = mats["racing_green"]
    tan = mats["saddle_tan"]
    steel = mats["steel"]
    ivory = mats.get("ivory", brass)
    black = mats.get("black", ebony)
    glass = mats.get("glass", brass)
    wf = mats.get("window_frame", brass)
    lime = mats.get("limestone", oak)
    wal = mats.get("walnut_fluted", oak)
    led = mats.get("warm_led", brass)
    marm = mats.get("marmorino", oak)
    cream = mats.get("cream_wool", ivory)
    leather = mats.get("black_leather", black)
    trav = mats.get("travertine", lime)
    velvet = mats.get("velvet", black)
    optic = mats.get("optic_yellow", brass)

    # 1. East Wing Shell (X in [15.0, 29.6], Z in [-15.8, +14.8], Y in [0, 18.6])
    ctx.mb("EastSalonFloor", oak).add_box(22.3, -0.05, -0.5, 14.6, 0.10, 30.6, uv_tile=5.0)
    ctx.mb("FloorInlay", brass).add_box(22.3, 0.01, -0.5, 14.2, 0.02, 0.06)
    ctx.mb("FloorInlay2", brass).add_box(22.3, 0.01, -0.5, 0.06, 0.02, 30.2)
    ctx.mb("EastWall", marm).add_box(29.65, 9.3, -0.5, 0.24, 18.6, 30.6, uv_tile=4.0)
    ctx.mb("EastSouthWall", marm).add_box(22.3, 9.3, 14.95, 14.6, 18.6, 0.24, uv_tile=4.0)
    ctx.mb("EastNorthGlass", glass).add_box(22.3, 9.3, -16.02, 14.6, 18.4, 0.05)
    for px in (15.5, 19.2, 22.8, 26.4, 29.5):
        ctx.mb("EastWinFrame", wf).add_box(px, 9.3, -16.0, 0.08, 18.6, 0.12)
    ctx.mb("EastWinFrameTop", wf).add_box(22.3, 18.52, -16.0, 14.6, 0.10, 0.12)
    ctx.mb("EastCeiling", marm).add_box(22.3, 18.66, -0.5, 14.6, 0.10, 30.6, uv_tile=4.0)

    for i in range(4):
        z = -10.5 + i * 6.5
        ctx.mb("EastWallNiche", wal).add_box(29.46, 6.2, z, 0.16, 7.6, 2.5, uv_tile=2.0)
        ctx.mb("EastWallNicheLED", led).add_box(29.36, 10.05, z, 0.04, 0.08, 2.3)

    ctx.mb("EastChandStem", brass).add_cylinder(22.4, 15.2, 1.0, 0.04, 0.04, 3.4)
    for i in range(6):
        ang = i * math.pi / 3.0
        ctx.mb("EastChandGlobe", mats["warm_bulb"]).add_sphere(
            22.4 + 0.9 * math.cos(ang), 14.9, 1.0 + 0.9 * math.sin(ang), 0.24, 0.24, 0.24,
        )

    # 2. 9-ft Ebony Concert Grand Piano (Penthouse 2.65x scale, focused at X=22.4, Z=-6.8)
    ctx.mb("PianoRug", cream).add_box(22.2, 0.02, -6.8, 9.6, 0.04, 8.2)
    ctx.mb("GrandPianoCase", ebony).add_rounded_box(22.4, 2.15, -6.8, 4.4, 0.90, 3.8, bevel=0.18)
    ctx.mb("GrandPianoCaseTail", ebony).add_cylinder(24.1, 1.70, -7.2, 1.35, 1.35, 0.90, segs=24)
    ctx.mb("GrandPianoKeybed", ebony).add_box(19.9, 1.88, -6.8, 1.3, 0.36, 3.6)
    for lx, lz in ((20.1, -8.3), (20.1, -5.3), (24.4, -7.3)):
        ctx.mb("PianoLeg", ebony).add_cylinder(lx, 0.16, lz, 0.16, 0.10, 1.56, segs=12)
        ctx.mb("PianoCaster", brass).add_sphere(lx, 0.12, lz, 0.12, 0.12, 0.12)
    ctx.mb("PedalLyre", brass).add_box(20.2, 0.92, -6.8, 0.12, 1.65, 0.56)
    for pz in (-7.0, -6.8, -6.6):
        ctx.mb("Pedal", brass).add_box(20.1, 0.14, pz, 0.22, 0.06, 0.12)
    # Double-faced glossy black concert lid held open at ~26 deg facing salon
    b_lid = ctx.mb("PianoOpenLid", ebony)
    b_lid.add_quad((20.4, 2.64, -8.6), (24.6, 2.64, -8.6), (24.6, 4.42, -4.9), (20.4, 4.42, -4.9), flip=True)
    b_lid.add_quad((20.4, 2.64, -8.6), (24.6, 2.64, -8.6), (24.6, 4.42, -4.9), (20.4, 4.42, -4.9), flip=False)
    ctx.mb("PianoLidProp", brass).add_cylinder(22.5, 2.55, -5.05, 0.038, 0.038, 1.88, segs=10)
    ctx.mb("GrandPianoHarp", brass).add_box(22.5, 2.58, -6.8, 3.8, 0.08, 3.1)
    for i in range(14):
        ctx.mb("PianoStrings", copper).add_cylinder(20.8 + i * 0.26, 2.64, -8.1, 0.014, 0.014, 2.6, rot_x=1.5708)
    for i in range(52):
        ctx.mb("GrandPianoKeys", ivory).add_box(19.65, 2.08, -8.45 + i * 0.064, 0.64, 0.06, 0.054)
    for i in range(36):
        if i % 7 in (2, 6):
            continue
        ctx.mb("GrandPianoBlackKeys", black).add_box(19.78, 2.13, -8.42 + i * 0.092, 0.38, 0.06, 0.036)
    ctx.mb("PianoBench", leather).add_rounded_box(18.0, 1.24, -6.8, 1.15, 0.24, 2.45, bevel=0.06)
    for bx, bz in ((17.55, -7.85), (17.55, -5.75), (18.45, -7.85), (18.45, -5.75)):
        ctx.mb("PianoBenchLeg", ebony).add_cylinder(bx, 0.0, bz, 0.06, 0.045, 1.14, segs=10)

    # 3. Indoor Golf Putting Green & Leather Tour Bag (X in [18.4, 28.4], Z in [6.4, 13.8])
    ctx.mb("PuttingGreenBorder", wal).add_rounded_box(23.4, 0.04, 10.2, 10.2, 0.08, 7.2, bevel=0.25)
    ctx.mb("PuttingGreenTurf", green).add_rounded_box(23.4, 0.08, 10.2, 9.6, 0.06, 6.6, bevel=0.35)
    for cx, cz in ((20.6, 8.8), (26.0, 11.4)):
        ctx.mb("PuttingCup", steel).add_cylinder(cx, 0.08, cz, 0.22, 0.22, 0.06)
        ctx.mb("PuttingPin", brass).add_cylinder(cx, 0.12, cz, 0.03, 0.03, 2.8)
        ctx.mb("PuttingFlag", optic).add_box(cx + 0.26, 2.65, cz, 0.52, 0.34, 0.03)
    for bx, bz in ((21.4, 8.4), (24.0, 11.8), (25.6, 9.6)):
        ctx.mb("GolfBall", ivory).add_sphere(bx, 0.18, bz, 0.08, 0.08, 0.08)
    ctx.mb("GolfPutter", steel).add_cylinder(22.2, 0.12, 12.6, 0.025, 0.025, 2.1, rot_z=0.26)
    ctx.mb("GolfTourBag", green).add_cylinder(27.8, 0.0, 12.6, 0.52, 0.44, 2.35, segs=18)
    ctx.mb("GolfBagTrim", tan).add_box(27.32, 1.18, 12.6, 0.12, 1.9, 0.44)
    for i in range(6):
        ctx.mb("GolfIrons", steel).add_cylinder(27.55 + i * 0.10, 2.25, 12.5, 0.026, 0.026, 1.1, rot_z=0.14)

    # 4. Tennis & Equestrian Tack Wall Gallery (Mounted cleanly in front of plaster wall pier)
    ctx.mb("SportGalleryConsole", trav).add_box(28.3, 1.12, 1.4, 1.4, 2.24, 5.6, uv_tile=2.0)
    for ang in (0.58, -0.58):
        ctx.mb("TennisDisplay", black).add_cylinder(29.18, 3.8, 3.8, 0.055, 0.055, 2.2, segs=10, rot_x=ang)
        ctx.mb("TennisHead", brass).add_sphere(29.18, 5.2, 3.8 + (0.65 if ang > 0 else -0.65), 0.09, 0.54, 0.42)
    ctx.mb("TennisBasket", brass).add_cylinder(28.1, 2.24, 3.5, 0.36, 0.42, 0.48, segs=16)
    for bx, bz in ((28.0, 3.4), (28.2, 3.6), (28.05, 3.65)):
        ctx.mb("TennisBall", optic).add_sphere(bx, 2.74, bz, 0.11, 0.11, 0.11)
    ctx.mb("EquestrianTack", wal).add_box(28.1, 1.15, -1.2, 1.1, 2.30, 0.7)
    ctx.mb("DressageSaddle", tan).add_rounded_box(28.1, 2.48, -1.2, 1.35, 0.56, 0.98, bevel=0.16)
    ctx.mb("DressagePommel", tan).add_rounded_box(27.6, 2.82, -1.2, 0.35, 0.30, 0.88, bevel=0.10)
    for sz in (-1.75, -0.65):
        ctx.mb("SaddleStirrup", steel).add_box(28.2, 1.85, sz, 0.10, 0.56, 0.10)
    for bz in (-2.05, -1.65):
        ctx.mb("RidingBoot", black).add_cylinder(28.1, 0.0, bz, 0.16, 0.14, 1.15, segs=12)
    ctx.mb("RidingHelmet", velvet).add_sphere(28.2, 2.65, 0.4, 0.34, 0.28, 0.38)
    return ctx
