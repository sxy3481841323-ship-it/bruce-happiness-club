import math

def build_east_piano_sport_wing(ctx, mats):
    def B(n, m): return ctx.mb(n, mats[m])
    def cyl(b, cx, y0, cz, r, h, segs=16, rx=0.0, rz=0.0):
        b.add_cylinder(cx, y0, cz, r, r, h, segs=segs, rot_x=rx, rot_z=rz)

    # ---------- 1. SHELL ----------
    f = B('EastSalonFloor', 'oak')
    f.add_box(28.8, -0.05, -0.1, 27.6, 0.10, 31.4, uv_tile=2.0)
    c = B('EastCeiling', 'marmorino')
    c.add_box(28.8, 18.66, -0.1, 27.6, 0.12, 31.4)
    cove = B('EastCove', 'warm_led')
    for (x, z, sx, sz) in [(28.8, 15.4, 27.4, 0.12), (28.8, -15.6, 27.4, 0.12),
                            (15.1, -0.1, 0.12, 31.2), (42.5, -0.1, 0.12, 31.2)]:
        cove.add_box(x, 18.4, z, sx, 0.10, sz)
    sw = B('EastSouthWall', 'marmorino')
    sw.add_box(28.0, 9.3, 15.6, 26.0, 18.6, 0.30)
    ch = B('EastChandelier', 'brass')
    cyl(ch, 28.5, 15.4, -1.0, 0.06, 0.9, segs=10)
    ch.add_sphere(28.5, 16.0, -1.0, 0.55, 0.35, 0.55, rings=10, segs=16)
    for i in range(8):
        a = i * math.pi / 4.0
        ch.add_sphere(28.5 + 0.55 * math.cos(a), 15.9, -1.0 + 0.55 * math.sin(a),
                      0.07, 0.07, 0.07, rings=6, segs=8)

    # ---------- Curved panoramic glass (Photo 1 style 10-bay curved bay) ----------
    curve = [
        (15.0, -16.0), (20.8, -17.0), (26.6, -17.4), (32.0, -16.6),
        (36.8, -14.2), (40.2, -10.2), (42.2, -5.2), (42.8, 0.0),
        (42.2, +5.4), (40.8, +10.6), (39.5, +15.4),
    ]
    mull = B('CurvedGlassMullions', 'charcoal')
    sill = B('CurvedWindowSill', 'travertine')
    glass = B('CurvedPanoramicGlass', 'glass')
    trans = B('CurvedTransom', 'charcoal')
    for (vx, vz) in curve:
        mull.add_box(vx, 9.3, vz, 0.24, 18.6, 0.24)
    for i in range(len(curve) - 1):
        x0, z0 = curve[i]; x1, z1 = curve[i + 1]
        mx, mz = (x0 + x1) * 0.5, (z0 + z1) * 0.5
        dx, dz = x1 - x0, z1 - z0
        L = math.hypot(dx, dz)
        ang = math.atan2(dx, dz)
        sill.add_box(mx, 0.425, mz, 0.65, 0.85, L + 0.1, rot_y=ang)
        trans.add_box(mx, 13.6, mz, 0.16, 0.14, L + 0.1, rot_y=ang)
        p0 = (x0, 0.85, z0); p1 = (x1, 0.85, z1)
        p2 = (x1, 18.5, z1); p3 = (x0, 18.5, z0)
        glass.add_quad(p0, p1, p2, p3, uv_scale=(L * 0.3, 4.0), flip=False)
        glass.add_quad(p0, p1, p2, p3, uv_scale=(L * 0.3, 4.0), flip=True)

    # ---------- 2. 9-FT CONCERT GRAND PIANO BY CURVED WINDOW ----------
    rug = B('PianoRug', 'cream_wool')
    rug.add_box(30.8, 0.02, -9.2, 11.4, 0.04, 9.6, uv_tile=3.0)
    pc = B('GrandPianoCase', 'ebony_piano')
    pc.add_rounded_box(31.2, 2.15, -9.6, 3.8, 0.85, 3.4, bevel=0.14)
    pc.add_cylinder(31.2, 1.72, -7.8, 1.55, 1.55, 0.85, segs=26)
    pc.add_box(31.2, 1.88, -11.4, 3.8, 0.36, 1.2)
    for (lx, lz) in [(29.6, -11.2), (32.8, -11.2), (31.2, -7.2)]:
        cyl(pc, lx, 0.14, lz, 0.14, 1.58, segs=12)
        pc.add_sphere(lx, 0.10, lz, 0.14, 0.10, 0.14, rings=6, segs=10)
    lyre = B('PianoLyre', 'brass')
    cyl(lyre, 31.2, 0.14, -11.6, 0.08, 1.58, segs=10)
    lyre.add_box(31.2, 0.22, -11.6, 0.72, 0.08, 0.18)
    for px in (30.95, 31.20, 31.45):
        lyre.add_box(px, 0.14, -11.75, 0.10, 0.06, 0.26)
    lid = B('PianoOpenLid', 'ebony_piano')
    lid.add_quad((29.3, 2.60, -11.2), (33.1, 2.60, -11.2),
                 (33.1, 4.45, -7.8), (29.3, 4.45, -7.8), flip=False)
    lid.add_quad((29.3, 2.60, -11.2), (33.1, 2.60, -11.2),
                 (33.1, 4.45, -7.8), (29.3, 4.45, -7.8), flip=True)
    prop = B('PianoProp', 'brass')
    cyl(prop, 32.8, 2.55, -8.2, 0.04, 1.92, segs=8, rx=0.22)
    harp = B('GrandPianoHarp', 'brass')
    harp.add_box(31.2, 2.56, -9.4, 3.1, 0.08, 2.4)
    strings = B('PianoStrings', 'copper_cook')
    for i in range(14):
        sx = 29.8 + i * 0.21
        cyl(strings, sx, 2.62, -10.5, 0.015, 2.2, segs=6, rx=1.5708)
    keys = B('PianoKeys', 'ivory')
    for i in range(52):
        kx = 29.55 + i * 0.064
        keys.add_box(kx, 2.06, -11.82, 0.056, 0.05, 0.48)
    bk = B('PianoBlackKeys', 'ebony_piano')
    for i in range(36):
        if i % 7 in (2, 6):
            continue
        kx = 29.58 + i * 0.092
        bk.add_box(kx, 2.11, -11.74, 0.036, 0.05, 0.30)
    sm = B('GrandPianoSheetMusic', 'sheet_music')
    sm.add_box(31.2, 2.86, -11.15, 1.15, 0.72, 0.04)
    lamp = B('PianoLamp', 'warm_bulb')
    lamp.add_sphere(31.2, 3.42, -11.15, 0.16, 0.14, 0.16, rings=8, segs=12)
    bench = B('PianoBench', 'black_leather')
    bench.add_rounded_box(31.2, 1.24, -13.15, 2.45, 0.24, 1.05, bevel=0.06)
    for (bx, bz) in [(30.15, -13.55), (32.25, -13.55), (30.15, -12.75), (32.25, -12.75)]:
        cyl(bench, bx, 0.0, bz, 0.055, 1.15, segs=8)
    # Fig tree framed beside left window mullion without blocking piano camera (Photo 1)
    pot = B('PianoFigTree', 'ceramic_white')
    pot.add_lathe(21.2, 0.0, -14.8, [(0.0, 0.0), (0.55, 0.0), (0.62, 0.95), (0.52, 1.05)], segs=18)
    trunk = B('PianoFigTrunk', 'oak')
    cyl(trunk, 21.2, 1.00, -14.8, 0.09, 2.8, segs=8)
    fol = B('PianoFigFoliage', 'olive_leaf')
    for (fx, fy, fz, r) in [(21.2, 4.0, -14.8, 1.05), (20.7, 4.7, -14.4, 0.85),
                             (21.7, 4.6, -15.1, 0.85), (21.2, 5.2, -14.8, 0.75)]:
        fol.add_sphere(fx, fy, fz, r, r * 0.85, r, rings=8, segs=12)

    # ---------- 3. PUTTING GREEN ----------
    trim = B('PuttingTrim', 'walnut_solid')
    trim.add_box(30.1, 0.03, 7.6, 18.6, 0.06, 11.6)
    turf = B('PuttingGreenTurf', 'racing_green')
    turf.add_box(30.1, 0.06, 7.6, 18.2, 0.07, 11.2, uv_tile=4.0)
    bunk = B('PuttingBunker', 'cream_wool')
    bunk.add_sphere(23.2, 0.09, 10.6, 1.8, 0.10, 1.1, rings=8, segs=16)
    cups = B('PuttingCups', 'steel')
    for (cx, cz) in [(26.0, 5.0), (31.0, 9.0), (36.0, 4.5)]:
        cyl(cups, cx, 0.10, cz, 0.16, 0.03, segs=14)
    flags = B('PuttingFlags', 'brass')
    for (cx, cz) in [(26.0, 5.0), (31.0, 9.0), (36.0, 4.5)]:
        cyl(flags, cx, 0.10, cz, 0.025, 2.8, segs=8)
        flags.add_box(cx + 0.25, 2.75, cz, 0.48, 0.30, 0.03)
    balls = B('GolfBalls', 'porcelain_white')
    for (bx, bz) in [(28.0, 6.0), (29.5, 8.5), (33.0, 6.5), (34.5, 9.5)]:
        balls.add_sphere(bx, 0.16, bz, 0.08, 0.08, 0.08, rings=8, segs=10)
    putter = B('GolfPutter', 'steel')
    cyl(putter, 28.0, 0.14, 6.0, 0.02, 1.8, segs=8, rx=0.35)
    putter.add_box(28.0, 0.16, 5.95, 0.32, 0.08, 0.12)
    # High-contrast backlit golf club display board
    board = B('GolfClubBoard', 'marmorino')
    board.add_box(39.4, 3.8, 7.6, 0.24, 6.6, 7.6)
    wash = B('GolfBoardWash', 'warm_led')
    wash.add_box(39.24, 3.8, 7.6, 0.05, 6.2, 7.2)
    rack = B('GolfRack', 'walnut_solid')
    rack.add_box(39.05, 5.6, 7.6, 0.32, 0.16, 6.4)
    rack.add_box(39.05, 1.4, 7.6, 0.32, 0.16, 6.4)
    for i in range(3):
        d = B('GolfDriver%d' % i, 'platinum')
        dz = 5.0 + i * 0.85
        cyl(d, 38.85, 1.75, dz, 0.028, 3.9, segs=8)
        d.add_sphere(38.75, 1.65, dz, 0.24, 0.18, 0.22, rings=8, segs=12)
    for i in range(5):
        ir = B('GolfIron%d' % i, 'chrome')
        iz = 7.45 + i * 0.56
        cyl(ir, 38.85, 1.75, iz, 0.024, 3.5 - i * 0.12, segs=8)
        ir.add_box(38.76, 1.68, iz, 0.18, 0.11, 0.28)
    mp = B('GolfMallet', 'brass')
    cyl(mp, 38.85, 1.75, 10.35, 0.028, 3.3, segs=8)
    mp.add_box(38.75, 1.68, 10.35, 0.28, 0.12, 0.22)
    bag = B('GolfTourBag', 'racing_green')
    bag.add_cylinder(37.4, 0.0, 12.2, 0.56, 0.48, 2.55, segs=18)
    strap = B('GolfBagStrap', 'saddle_tan')
    strap.add_box(36.90, 1.25, 12.2, 0.14, 2.10, 0.48)

    # ---------- 4. CRISP BACKLIT VITRINES (facing -Z into salon at Z=15.0) ----------
    def vitrine(name, x):
        p = B(name + 'Panel', 'marmorino')
        p.add_box(x, 4.2, 15.1, 7.2, 7.6, 0.24)
        w = B(name + 'Wash', 'warm_led')
        w.add_box(x, 7.8, 14.8, 6.8, 0.10, 0.14)
        pl = B(name + 'Plinth', 'travertine')
        pl.add_box(x, 0.9, 14.3, 6.6, 1.8, 1.4)
    vitrine('TennisVitrine', 24.2)
    vitrine('EquestrianVitrine', 32.8)

    # Crossed 3.6 WU Pro Tennis Rackets with explicit white string grid
    for sgn in (-1, 1):
        rk = B('TennisDisplay%d' % (sgn + 1), 'charcoal')
        ang = sgn * 0.52
        cx, cy, cz = 24.2, 4.8, 14.4
        hx = cx + sgn * 1.15 * math.sin(ang)
        hy = cy - 1.35 * math.cos(ang)
        cyl(rk, hx, hy, cz, 0.075, 1.55, segs=10, rz=ang)
        head_x = cx - sgn * 0.38
        head_y = cy + 0.55
        for k in range(18):
            a0 = k * math.pi / 9.0
            a1 = (k + 1) * math.pi / 9.0
            x0, y0 = head_x + 0.72 * math.cos(a0), head_y + 0.92 * math.sin(a0)
            x1, y1 = head_x + 0.72 * math.cos(a1), head_y + 0.92 * math.sin(a1)
            rk.add_quad((x0, y0, cz - 0.05), (x1, y1, cz - 0.05), (x1, y1, cz + 0.05), (x0, y0, cz + 0.05), flip=False)
            rk.add_quad((x0, y0, cz - 0.05), (x1, y1, cz - 0.05), (x1, y1, cz + 0.05), (x0, y0, cz + 0.05), flip=True)
        st = B('TennisStrings%d' % (sgn + 1), 'porcelain_white')
        for k in range(7):
            off = -0.48 + k * 0.16
            st.add_box(head_x + off, head_y, cz, 0.02, 1.64, 0.02)
            st.add_box(head_x, head_y + off * 1.15, cz, 1.28, 0.02, 0.02)
    basket = B('TennisBasket', 'brass')
    basket.add_lathe(24.2, 1.80, 14.0, [(0.0, 0.0), (0.50, 0.0), (0.58, 0.58), (0.52, 0.64)], segs=16)
    tb = B('TennisBalls', 'optic_yellow')
    for (bx, by, bz) in [(23.95, 2.48, 14.0), (24.20, 2.48, 14.0), (24.45, 2.48, 14.0), (24.20, 2.66, 14.0)]:
        tb.add_sphere(bx, by, bz, 0.11, 0.11, 0.11, rings=8, segs=12)

    # Equestrian Dressage Tack (white quilted pad + cognac saddle + stirrups + bridle + boots + helmet)
    pad = B('SaddlePad', 'porcelain_white')
    pad.add_rounded_box(32.8, 1.92, 14.2, 2.6, 0.18, 1.2, bevel=0.06)
    stand = B('SaddleStand', 'walnut_solid')
    stand.add_box(32.8, 2.50, 14.2, 1.8, 1.10, 0.55)
    sad = B('DressageSaddle', 'saddle_tan')
    sad.add_rounded_box(32.8, 3.45, 14.2, 2.0, 0.56, 1.15, bevel=0.14)
    sad.add_sphere(32.0, 3.92, 14.2, 0.30, 0.24, 0.44, rings=8, segs=12)
    sad.add_sphere(33.6, 3.98, 14.2, 0.34, 0.28, 0.48, rings=8, segs=12)
    kr = B('SaddleKneeRolls', 'walnut_solid')
    kr.add_sphere(32.2, 3.25, 13.75, 0.24, 0.34, 0.18, rings=6, segs=10)
    kr.add_sphere(33.4, 3.25, 13.75, 0.24, 0.34, 0.18, rings=6, segs=10)
    stir = B('SaddleStirrup', 'steel')
    for sx in (32.0, 33.6):
        cyl(stir, sx, 2.55, 13.68, 0.035, 0.72, segs=8)
        stir.add_box(sx, 2.50, 13.68, 0.24, 0.16, 0.06)
    br = B('SaddleBridle', 'saddle_tan')
    br.add_box(32.8, 5.20, 14.6, 1.25, 0.12, 0.08)
    cyl(br, 32.35, 4.40, 14.6, 0.04, 0.85, segs=8)
    cyl(br, 33.25, 4.40, 14.6, 0.04, 0.85, segs=8)
    B('SaddleBit', 'brass').add_cylinder(32.8, 4.42, 14.56, 0.045, 0.045, 0.90, segs=8, rot_x=1.5708)
    for bx in (31.0, 34.6):
        bt = B('SaddleBoot%d' % int(bx * 10), 'ebony_piano')
        bt.add_cylinder(bx, 1.85, 14.2, 0.18, 0.16, 1.65, segs=12)
        bt.add_rounded_box(bx, 1.90, 13.95, 0.32, 0.16, 0.56, bevel=0.05)
    hel = B('SaddleHelmet', 'ebony_piano')
    hel.add_sphere(32.8, 6.20, 14.3, 0.36, 0.32, 0.38, rings=8, segs=12)
    hel.add_box(32.8, 6.00, 14.00, 0.44, 0.05, 0.18)
