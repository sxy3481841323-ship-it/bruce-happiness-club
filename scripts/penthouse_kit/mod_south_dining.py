import math


def _chair(ctx, mats, x, z, rot_y):
    c, s = math.cos(rot_y), math.sin(rot_y)
    def rp(lx, lz):
        return (x + lx * c + lz * s, z - lx * s + lz * c)

    b = ctx.mb("DiningChair", mats["rift_oak"])
    for dx in (-0.52, 0.52):
        for dz in (-0.48, 0.48):
            wx, wz = rp(dx, dz)
            b.add_cylinder(wx, 0.0, wz, 0.06, 0.04, 1.04, segs=8)
    b.add_rounded_box(x, 1.08, z, 1.24, 0.14, 1.16, bevel=0.04, rot_y=rot_y)
    b2 = ctx.mb("DiningChairBoucle", mats["boucle"])
    b2.add_rounded_box(x, 1.22, z, 1.18, 0.18, 1.10, bevel=0.06, rot_y=rot_y)
    bx, bz = rp(0.0, -0.50)
    b2.add_rounded_box(bx, 1.72, bz, 1.18, 1.02, 0.16, bevel=0.06, rot_y=rot_y)


def _setting(ctx, mats, x, z):
    b = ctx.mb("DiningPlaceSettings", mats["ceramic_white"])
    b.add_cylinder(x, 2.13, z, 0.34, 0.34, 0.03, segs=18)
    b.add_cylinder(x, 2.16, z, 0.25, 0.25, 0.025, segs=18)
    bb = ctx.mb("DiningPlaceSettingsBrass", mats["brass"])
    bb.add_cylinder(x, 2.125, z, 0.36, 0.36, 0.015, segs=18)
    bc = ctx.mb("DiningWineStem", mats["crystal_glass"])
    bc.add_cylinder(x + 0.44, 2.13, z - 0.14, 0.022, 0.022, 0.24, segs=10)
    bc.add_sphere(x + 0.44, 2.46, z - 0.14, 0.09, 0.13, 0.09, rings=10, segs=12)


def build_south_dining(ctx, mats):
    rug = ctx.mb("DiningAreaRug", mats.get("rug_2f", mats["boucle"]))
    rug.add_box(0.0, 0.02, 31.0, 14.2, 0.04, 8.2)

    ped = ctx.mb("DiningPedestals", mats["obsidian_bezel"])
    oak = ctx.mb("DiningPedestalOak", mats["rift_oak"])
    for px in (-3.6, 3.6):
        ped.add_cylinder(px, 0.02, 31.0, 0.85, 0.72, 0.14, segs=22)
        for i in range(10):
            a = i * math.pi / 5.0
            oak.add_cylinder(px + 0.44 * math.cos(a), 0.16, 31.0 + 0.44 * math.sin(a),
                             0.075, 0.075, 1.72, segs=8)
        ped.add_cylinder(px, 1.88, 31.0, 0.70, 0.82, 0.10, segs=22)

    slab = ctx.mb("DiningTableMarble", mats["pietra_grey"])
    slab.add_rounded_box(0.0, 2.04, 31.0, 11.4, 0.16, 3.50, bevel=0.05)
    brass = ctx.mb("DiningTableBrassEdge", mats["brass"])
    brass.add_box(0.0, 2.04, 31.0, 11.44, 0.02, 3.54)

    for x in (-3.4, 0.0, 3.4):
        _chair(ctx, mats, x, 28.65, 0.0)
        _chair(ctx, mats, x, 33.35, math.pi)
    _chair(ctx, mats, -6.55, 31.0, -math.pi * 0.5)
    _chair(ctx, mats, 6.55, 31.0, math.pi * 0.5)

    for x in (-3.4, 0.0, 3.4):
        _setting(ctx, mats, x, 29.75)
        _setting(ctx, mats, x, 32.25)
    _setting(ctx, mats, -4.95, 31.0)
    _setting(ctx, mats, 4.95, 31.0)

    vase = ctx.mb("DiningCenterpiece", mats["travertine"])
    vase.add_lathe(0.0, 2.13, 31.0, [(0.0, 0.0), (0.32, 0.0), (0.38, 0.18),
                                     (0.30, 0.52), (0.20, 0.74), (0.24, 0.84)], segs=20)
    bark = ctx.mb("DiningOliveBranches", mats["bark"])
    leaf = ctx.mb("DiningOliveLeaves", mats["olive_leaf"])
    for i in range(6):
        a = i * 1.047
        bx, bz = 0.14 * math.cos(a), 31.0 + 0.14 * math.sin(a)
        bark.add_cylinder(bx, 2.95, bz, 0.02, 0.014, 0.85, segs=6)
        leaf.add_sphere(bx * 2.1, 3.72, 31.0 + (bz - 31.0) * 2.1, 0.18, 0.10, 0.18, rings=6, segs=8)

    cand = ctx.mb("DiningCandlesticks", mats["brass"])
    bulb = ctx.mb("DiningCandleFlame", mats["warm_bulb"])
    for cx in (-1.05, 1.05):
        cand.add_cylinder(cx, 2.13, 31.0, 0.08, 0.045, 0.78, segs=12)
        bulb.add_sphere(cx, 2.98, 31.0, 0.05, 0.10, 0.05, rings=8, segs=10)

    pend = ctx.mb("DiningChandeliers", mats["charcoal"])
    pbr = ctx.mb("DiningChandelierBrass", mats["brass"])
    pled = ctx.mb("DiningChandelierLED", mats["warm_led"])
    for pz in (30.4, 31.6):
        pend.add_box(0.0, 7.80, pz, 6.4, 0.14, 0.18)
        pbr.add_box(0.0, 7.72, pz, 6.4, 0.03, 0.20)
        pled.add_box(0.0, 7.68, pz, 6.1, 0.03, 0.12)
        for rx in (-2.6, 0.0, 2.6):
            pbr.add_cylinder(rx, 7.88, pz, 0.016, 0.016, 10.7, segs=6)
