import math


def build_east_piano_sport_wing(ctx, mats):
    def B(n, m):
        return ctx.mb(n, mats[m])

    def cyl(b, cx, y0, cz, r, h, segs=16, rx=0.0, rz=0.0):
        b.add_cylinder(cx, y0, cz, r, r, h, segs=segs, rot_x=rx, rot_z=rz)

    # ---------- 1. DOUBLE-HEIGHT CLUB SHELL & 10-BAY CURVED GLASS ----------
    B("EastSalonFloor", "oak").add_box(28.8, -0.05, -0.1, 27.6, 0.10, 31.4, uv_tile=2.0)
    B("EastCeiling", "marmorino").add_box(28.8, 18.66, -0.1, 27.6, 0.12, 31.4)
    cove = B("EastCove", "warm_led")
    for (x, z, sx, sz) in [(28.8, 15.4, 27.4, 0.12), (28.8, -15.6, 27.4, 0.12),
                            (15.1, -0.1, 0.12, 31.2), (42.5, -0.1, 0.12, 31.2)]:
        cove.add_box(x, 18.4, z, sx, 0.10, sz)
    B("EastSouthWall", "marmorino").add_box(28.0, 9.3, 15.6, 26.0, 18.6, 0.30)
    ch = B("EastChandelier", "brass")
    cyl(ch, 28.5, 15.4, -1.0, 0.06, 0.9, segs=10)
    ch.add_sphere(28.5, 16.0, -1.0, 0.55, 0.35, 0.55, rings=10, segs=16)
    for i in range(8):
        a = i * math.pi / 4.0
        ch.add_sphere(28.5 + 0.55 * math.cos(a), 15.9, -1.0 + 0.55 * math.sin(a), 0.07, 0.07, 0.07, rings=6, segs=8)

    curve = [
        (15.0, -16.0), (20.8, -17.0), (26.6, -17.4), (32.0, -16.6),
        (36.8, -14.2), (40.2, -10.2), (42.2, -5.2), (42.8, 0.0),
        (42.2, +5.4), (40.8, +10.6), (39.5, +15.4),
    ]
    mull = B("CurvedGlassMullions", "charcoal")
    sill = B("CurvedWindowSill", "travertine")
    glass = B("CurvedPanoramicGlass", "glass")
    trans = B("CurvedTransom", "charcoal")
    for (vx, vz) in curve:
        mull.add_box(vx, 9.3, vz, 0.24, 18.6, 0.24)
    for i in range(len(curve) - 1):
        x0, z0 = curve[i]
        x1, z1 = curve[i + 1]
        mx, mz = (x0 + x1) * 0.5, (z0 + z1) * 0.5
        dx, dz = x1 - x0, z1 - z0
        L = math.hypot(dx, dz)
        ang = math.atan2(dx, dz)
        sill.add_box(mx, 0.425, mz, 0.65, 0.85, L + 0.1, rot_y=ang)
        trans.add_box(mx, 13.6, mz, 0.16, 0.14, L + 0.1, rot_y=ang)
        p0, p1 = (x0, 0.85, z0), (x1, 0.85, z1)
        p2, p3 = (x1, 18.5, z1), (x0, 18.5, z0)
        glass.add_quad(p0, p1, p2, p3, uv_scale=(L * 0.3, 4.0), flip=False)
        glass.add_quad(p0, p1, p2, p3, uv_scale=(L * 0.3, 4.0), flip=True)

    # ---------- 2. 9-FT CONCERT GRAND PIANO BY CURVED WINDOW ----------
    B("PianoRug", "cream_wool").add_box(30.8, 0.02, -9.2, 11.4, 0.04, 9.6, uv_tile=3.0)
    pc = B("GrandPianoCase", "ebony_piano")
    pc.add_rounded_box(31.2, 2.15, -9.6, 3.8, 0.85, 3.4, bevel=0.14)
    pc.add_cylinder(31.2, 1.72, -7.8, 1.55, 1.55, 0.85, segs=26)
    pc.add_box(31.2, 1.88, -11.4, 3.8, 0.36, 1.2)
    for (lx, lz) in [(29.6, -11.2), (32.8, -11.2), (31.2, -7.2)]:
        cyl(pc, lx, 0.14, lz, 0.14, 1.58, segs=12)
        pc.add_sphere(lx, 0.10, lz, 0.14, 0.10, 0.14, rings=6, segs=10)
    lyre = B("PianoLyre", "brass")
    cyl(lyre, 31.2, 0.14, -11.6, 0.08, 1.58, segs=10)
    lyre.add_box(31.2, 0.22, -11.6, 0.72, 0.08, 0.18)
    for px in (30.95, 31.20, 31.45):
        lyre.add_box(px, 0.14, -11.75, 0.10, 0.06, 0.26)
    lid = B("PianoOpenLid", "ebony_piano")
    lid.add_quad((29.3, 2.60, -11.2), (33.1, 2.60, -11.2), (33.1, 4.45, -7.8), (29.3, 4.45, -7.8), flip=False)
    lid.add_quad((29.3, 2.60, -11.2), (33.1, 2.60, -11.2), (33.1, 4.45, -7.8), (29.3, 4.45, -7.8), flip=True)
    cyl(B("PianoProp", "brass"), 32.8, 2.55, -8.2, 0.04, 1.92, segs=8, rx=0.22)
    B("GrandPianoHarp", "brass").add_box(31.2, 2.56, -9.4, 3.1, 0.08, 2.4)
    strings = B("PianoStrings", "copper_cook")
    for i in range(14):
        cyl(strings, 29.8 + i * 0.21, 2.62, -10.5, 0.015, 2.2, segs=6, rx=1.5708)
    keys = B("PianoKeys", "ivory")
    for i in range(52):
        keys.add_box(29.55 + i * 0.064, 2.06, -11.82, 0.056, 0.05, 0.48)
    bk = B("PianoBlackKeys", "ebony_piano")
    for i in range(36):
        if i % 7 not in (2, 6):
            bk.add_box(29.58 + i * 0.092, 2.11, -11.74, 0.036, 0.05, 0.30)
    B("GrandPianoSheetMusic", "sheet_music").add_box(31.2, 2.86, -11.15, 1.15, 0.72, 0.04)
    B("PianoLamp", "warm_bulb").add_sphere(31.2, 3.42, -11.15, 0.16, 0.14, 0.16, rings=8, segs=12)
    bench = B("PianoBench", "black_leather")
    bench.add_rounded_box(31.2, 1.24, -13.15, 2.45, 0.24, 1.05, bevel=0.06)
    for (bx, bz) in [(30.15, -13.55), (32.25, -13.55), (30.15, -12.75), (32.25, -12.75)]:
        cyl(bench, bx, 0.0, bz, 0.055, 1.15, segs=8)
    B("PianoFigTree", "ceramic_white").add_lathe(21.2, 0.0, -14.8, [(0.0, 0.0), (0.55, 0.0), (0.62, 0.95), (0.52, 1.05)], segs=18)
    cyl(B("PianoFigTrunk", "oak"), 21.2, 1.00, -14.8, 0.09, 2.8, segs=8)
    fol = B("PianoFigFoliage", "olive_leaf")
    for (fx, fy, fz, r) in [(21.2, 4.0, -14.8, 1.05), (20.7, 4.7, -14.4, 0.85), (21.7, 4.6, -15.1, 0.85), (21.2, 5.2, -14.8, 0.75)]:
        fol.add_sphere(fx, fy, fz, r, r * 0.85, r, rings=8, segs=12)

    # ---------- 3. PUTTING GREEN ----------
    B("PuttingTrim", "walnut_solid").add_box(30.1, 0.03, 7.6, 18.6, 0.06, 11.6)
    B("PuttingGreenTurf", "racing_green").add_box(30.1, 0.06, 7.6, 18.2, 0.07, 11.2, uv_tile=4.0)
    B("PuttingBunker", "cream_wool").add_sphere(23.2, 0.09, 10.6, 1.8, 0.10, 1.1, rings=8, segs=16)
    cups = B("PuttingCups", "steel")
    flags = B("PuttingFlags", "brass")
    for (cx, cz) in [(26.0, 5.0), (31.0, 9.0), (36.0, 4.5)]:
        cyl(cups, cx, 0.10, cz, 0.16, 0.03, segs=14)
        cyl(flags, cx, 0.10, cz, 0.025, 2.8, segs=8)
        flags.add_box(cx + 0.25, 2.75, cz, 0.48, 0.30, 0.03)
    balls = B("GolfBalls", "porcelain_white")
    for (bx, bz) in [(28.0, 6.0), (29.5, 8.5), (33.0, 6.5), (34.5, 9.5)]:
        balls.add_sphere(bx, 0.16, bz, 0.08, 0.08, 0.08, rings=8, segs=10)
    putter = B("GolfPutter", "steel")
    cyl(putter, 28.0, 0.14, 6.0, 0.02, 1.8, segs=8, rx=0.35)
    putter.add_box(28.0, 0.16, 5.95, 0.32, 0.08, 0.12)

    # ---------- 4. 3-BAY PARTITION SPORTING WALL (X=[14.70..16.85], Z=[-6.8..+3.2], facing +X) ----------
    bo = B("SportWallBoiserie", "walnut_solid")
    bo.add_box(14.78, 4.30, -1.80, 0.16, 8.60, 10.00, uv_tile=2.0)
    for z in (-6.7, -3.45, -0.05, 3.15):
        bo.add_box(15.02, 4.30, z, 0.24, 8.60, 0.16)
    bp = B("SportBayPanels", "marmorino")
    for bz in (-5.08, -1.75, 1.55):
        bp.add_box(14.90, 4.85, bz, 0.06, 6.40, 2.85)
    B("SportCredenza", "travertine").add_box(15.65, 0.72, -1.80, 1.55, 1.44, 9.80, uv_tile=2.0)
    led = B("SportWashLED", "warm_led")
    led.add_box(15.08, 8.15, -1.80, 0.10, 0.08, 9.50)
    led.add_box(15.08, 1.50, -1.80, 0.10, 0.06, 9.50)

    for idx, sgn in enumerate((-1, 1)):
        nm_id = idx * 2
        cz = -5.10 + sgn * 0.24
        rk = B(f"TennisDisplay{nm_id}", "charcoal")
        cyl(rk, 15.16, 4.05, cz - sgn * 0.45, 0.06, 1.35, segs=8, rx=sgn * 0.45)
        hz = cz + sgn * 0.15
        for k in range(16):
            a0, a1 = k * math.pi / 8.0, (k + 1) * math.pi / 8.0
            y0, z0 = 5.45 + 0.72 * math.sin(a0), hz + 0.56 * math.cos(a0)
            y1, z1 = 5.45 + 0.72 * math.sin(a1), hz + 0.56 * math.cos(a1)
            rk.add_quad((15.12, y0, z0), (15.12, y1, z1), (15.22, y1, z1), (15.22, y0, z0), flip=False)
            rk.add_quad((15.12, y0, z0), (15.12, y1, z1), (15.22, y1, z1), (15.22, y0, z0), flip=True)
        st = B(f"TennisStrings{nm_id}", "porcelain_white")
        for off in (-0.36, -0.18, 0.0, 0.18, 0.36):
            st.add_box(15.17, 5.45, hz + off, 0.02, 1.24, 0.02)
            st.add_box(15.17, 5.45 + off * 1.25, hz, 0.02, 0.02, 0.96)
    B("TennisBasket", "brass").add_lathe(15.70, 1.44, -5.10, [(0.0, 0.0), (0.40, 0.0), (0.48, 0.50), (0.44, 0.56)], segs=16)
    tb = B("TennisBalls", "optic_yellow")
    for dz in (-0.18, 0.0, 0.18):
        tb.add_sphere(15.70, 2.04, -5.10 + dz, 0.09, 0.09, 0.09, rings=8, segs=10)

    B("SaddlePad", "porcelain_white").add_rounded_box(15.70, 1.52, -1.75, 0.95, 0.16, 1.95, bevel=0.05)
    B("SaddleStand", "walnut_solid").add_box(15.70, 2.08, -1.75, 0.50, 0.98, 1.45)
    sad = B("DressageSaddle", "saddle_tan")
    sad.add_rounded_box(15.70, 2.75, -1.75, 0.92, 0.44, 1.65, bevel=0.12)
    sad.add_sphere(15.70, 3.12, -2.35, 0.34, 0.20, 0.24, rings=8, segs=10)
    sad.add_sphere(15.70, 3.16, -1.12, 0.36, 0.22, 0.26, rings=8, segs=10)
    stir = B("SaddleStirrup", "steel")
    for side in (-0.48, 0.48):
        cyl(stir, 15.70 + side, 2.05, -1.75, 0.03, 0.65, segs=8)
        stir.add_box(15.70 + side, 2.02, -1.75, 0.06, 0.14, 0.22)
    br = B("SaddleBridle", "saddle_tan")
    br.add_box(15.08, 5.45, -1.75, 0.06, 0.12, 1.05)
    cyl(br, 15.08, 4.70, -2.10, 0.035, 0.78, segs=8)
    cyl(br, 15.08, 4.70, -1.40, 0.035, 0.78, segs=8)
    cyl(B("SaddleBit", "brass"), 15.10, 4.72, -1.75, 0.038, 0.78, segs=8, rx=1.5708)
    hel = B("SaddleHelmet", "ebony_piano")
    hel.add_sphere(15.70, 6.25, -1.75, 0.30, 0.26, 0.32, rings=8, segs=12)
    bt = B("SaddleBoot", "saddle_tan")
    for bz in (-2.55, -0.95):
        cyl(bt, 15.70, 1.44, bz, 0.15, 1.35, segs=10)

    rr = B("GolfRackRail", "walnut_solid")
    rr.add_box(15.10, 5.70, 1.55, 0.20, 0.14, 2.65)
    rr.add_box(15.10, 1.85, 1.55, 0.20, 0.14, 2.65)
    for i in range(9):
        zz = 0.45 + i * 0.27
        if i < 3:
            m, nm = "platinum", f"GolfDriver{i}"
        elif i < 8:
            m, nm = "chrome", f"GolfIron{i - 3}"
        else:
            m, nm = "brass", "GolfMallet"
        cb = B(nm, m)
        cyl(cb, 15.16, 1.95, zz, 0.022, 3.65, segs=8)
        cb.add_sphere(15.26, 1.92, zz, 0.18 if i < 3 else 0.12, 0.11, 0.14, rings=6, segs=10)
    cyl(B("GolfTourBag", "racing_green"), 16.05, 0.0, 2.45, 0.42, 2.25, segs=16)
    B("GolfBagStrap", "saddle_tan").add_box(16.44, 1.15, 2.45, 0.10, 1.80, 0.36)
