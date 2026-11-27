# scripts/penthouse_kit/mod_terrace_sky.py
import math

def build_terrace_and_sky(ctx, mats):
    # ---------------- Terrace Deck ----------------
    b = ctx.mb("TerraceDeck", mats["travertine"])
    b.add_box(0.0, -0.10, -22.8, 32.4, 0.20, 13.6, uv_tile=2.2)
    # travertine coping edge
    b.add_box(0.0, 0.02, -29.55, 32.4, 0.10, 0.30, uv_tile=1.0)
    b.add_box(-16.05, 0.02, -22.8, 0.30, 0.10, 13.6, uv_tile=1.0)
    b.add_box(16.05, 0.02, -22.8, 0.30, 0.10, 13.6, uv_tile=1.0)

    # ---------------- Glass Balustrade ----------------
    g = ctx.mb("TerraceGlass", mats["glass"])
    g.add_box(0.0, 0.53, -29.42, 32.0, 1.06, 0.03)
    g.add_box(-16.05, 0.53, -22.8, 0.03, 1.06, 13.4)
    g.add_box(16.05, 0.53, -22.8, 0.03, 1.06, 13.4)
    # handrail
    h = ctx.mb("TerraceHandrail", mats["brass"])
    h.add_box(0.0, 1.08, -29.42, 32.2, 0.06, 0.10)
    h.add_box(-16.05, 1.08, -22.8, 0.10, 0.06, 13.6)
    h.add_box(16.05, 1.08, -22.8, 0.10, 0.06, 13.6)
    # posts
    p = ctx.mb("TerracePosts", mats["bronze_dark"])
    for x in (-16.0, -8.0, 0.0, 8.0, 16.0):
        p.add_box(x, 0.54, -29.42, 0.05, 1.08, 0.05)
    for z in (-29.4, -26.0, -22.6, -19.2, -16.2):
        p.add_box(-16.05, 0.54, z, 0.05, 1.08, 0.05)
        p.add_box(16.05, 0.54, z, 0.05, 1.08, 0.05)

    # ---------------- Outdoor Rug ----------------
    r = ctx.mb("TerraceOutdoorRug", mats["rug_2f"])
    r.add_box(1.4, 0.015, -22.6, 5.8, 0.03, 4.6, uv_tile=0.0)

    # ---------------- Plush Outdoor Sunset Bouclé Sofa (uv_tile=1.25) ----------------
    st = ctx.mb("TerraceSofaTeak", mats["walnut_solid"])
    st.add_rounded_box(1.4, 0.11, -22.4, 4.05, 0.22, 1.58, bevel=0.04, uv_tile=1.2)
    s = ctx.mb("TerraceSofaSeat", mats["boucle"])
    s.add_rounded_box(0.45, 0.38, -22.45, 1.88, 0.36, 1.38, bevel=0.14, uv_tile=1.2)
    s.add_rounded_box(2.35, 0.38, -22.45, 1.88, 0.36, 1.38, bevel=0.14, uv_tile=1.2)
    s.add_rounded_box(1.4, 0.78, -21.58, 3.82, 0.76, 0.34, bevel=0.14, uv_tile=1.2)
    s.add_rounded_box(-0.58, 0.56, -22.4, 0.32, 0.68, 1.48, bevel=0.12, uv_tile=1.2)
    s.add_rounded_box(3.38, 0.56, -22.4, 0.32, 0.68, 1.48, bevel=0.12, uv_tile=1.2)
    throw_m = ctx.mb("TerraceSofaThrow", mats["cognac_suede"])
    throw_m.add_rounded_box(2.75, 0.76, -21.62, 0.92, 0.56, 0.38, bevel=0.06, uv_tile=1.0)

    # pillows
    pl = ctx.mb("TerracePillows", mats["cognac_suede"])
    pl.add_rounded_box(0.15, 0.64, -21.80, 0.56, 0.42, 0.24, bevel=0.10, uv_tile=1.0)
    pl.add_rounded_box(2.65, 0.64, -21.80, 0.56, 0.42, 0.24, bevel=0.10, uv_tile=1.0)
    pb = ctx.mb("TerraceBolsters", mats["burgundy"])
    pb.add_cylinder(1.4, 0.58, -21.74, 0.16, 0.16, 1.2, segs=16, rot_z=math.pi / 2)

    # ---------------- Coffee Table ----------------
    t = ctx.mb("TerraceLowTable", mats["travertine"])
    t.add_rounded_box(1.4, 0.21, -24.45, 2.45, 0.42, 1.12, bevel=0.05, uv_tile=1.2)

    # ---------------- Hurricane Lanterns ----------------
    for lx in (-1.25, 4.05):
        ln = ctx.mb("TerraceLantern_%d" % int(lx*10), mats["brass"])
        ln.add_cylinder(lx, 0.0, -22.3, 0.15, 0.13, 0.56, segs=16)
        lb = ctx.mb("TerraceLanternGlow_%d" % int(lx*10), mats["warm_bulb"])
        lb.add_sphere(lx, 0.42, -22.3, 0.095, 0.12, 0.095, rings=8, segs=12)

    # ---------------- Multi-Branch Olive Trees ----------------
    for (ox, oz) in ((-12.2, -23.5), (12.4, -24.2)):
        pl2 = ctx.mb("OlivePlanter_%d" % int(ox), mats["travertine"])
        pl2.add_lathe(ox, 0.0, oz, [(0.0, 0.0), (0.46, 0.0), (0.58, 0.55), (0.62, 0.90), (0.52, 0.92)], segs=22)
        tr = ctx.mb("OliveTrunk_%d" % int(ox), mats["bark"])
        tr.add_curved_tube([(ox, 0.88, oz), (ox + 0.08, 1.65, oz + 0.05), (ox - 0.05, 2.35, oz - 0.04)], [0.13, 0.09, 0.05], segs=10)
        for bx, by, bz in ((0.75, 2.65, 0.35), (-0.70, 2.85, -0.45), (0.25, 3.15, -0.70)):
            tr.add_curved_tube([(ox, 1.85, oz), (ox + bx * 0.5, 2.35, oz + bz * 0.5), (ox + bx, by, oz + bz)], [0.06, 0.04, 0.025], segs=8)
        fl_d = ctx.mb("OliveFoliage_%d" % int(ox), mats["olive_leaf"])
        fl_b = ctx.mb("OliveFoliageBright_%d" % int(ox), mats["olive_leaf_bright"])
        for ci, (cxo, cyo, czo, cro) in enumerate((
            (0.75, 2.85, 0.35, 0.72), (-0.70, 3.05, -0.45, 0.68), (0.25, 3.35, -0.70, 0.64),
            (-0.35, 3.25, 0.55, 0.62), (0.05, 3.65, 0.0, 0.80),
        )):
            (fl_d if ci % 2 == 0 else fl_b).add_sphere(ox + cxo, cyo, oz + czo, cro, cro * 0.78, cro, rings=10, segs=14)

    # ---------------- Layer 1: Cliffside Drop-off ----------------
    c = ctx.mb("CoastalCliff", mats["headland_rock"])
    c.add_quad((-18.0, -0.5, -29.8), (18.0, -0.5, -29.8),
               (18.0, -8.8, -46.0), (-18.0, -8.8, -46.0), flip=True)
    for i, (yy, zz) in enumerate(((-2.2, -33.2), (-4.4, -37.2), (-6.6, -41.5))):
        c.add_box(0.0, yy, zz, 34.0 - i * 2.5, 0.85, 3.2, uv_tile=2.4)

    # ---------------- Layer 2: Soft Undulating Coastal Capes (NO harsh pyramid cones!) ----------------
    hd = ctx.mb("CoastalHeadlands", mats["headland_rock"])
    def add_cape(xs, hs, zh):
        for k in range(len(xs) - 1):
            x_a, x_b = xs[k], xs[k + 1]
            h_a, h_b = hs[k], hs[k + 1]
            u0, u1 = k / max(1, len(xs) - 1), (k + 1) / max(1, len(xs) - 1)
            hd.add_tri_raw((x_a, -8.5, zh), (x_b, -8.5, zh + 1.5), (x_b, h_b, zh), (u0, 0), (u1, 0), (u1, 1))
            hd.add_tri_raw((x_a, -8.5, zh), (x_b, h_b, zh), (x_a, h_a, zh), (u0, 0), (u1, 1), (u0, 1))
    add_cape([-92, -74, -56, -40, -26, -15, -7], [-8.5, 2.2, 4.4, 3.6, 1.4, -2.5, -8.5], -92.0)
    add_cape([16, 28, 44, 62, 78, 96], [-8.5, -1.8, 2.8, 5.1, 3.2, -8.5], -114.0)

    # ---------------- Layer 3: Ocean Surface (+Y upward normal) ----------------
    o = ctx.mb("OceanVistaWater", mats["horizon_ocean"])
    nx, nz = 24, 16
    x0, x1 = -180.0, 180.0
    z0, z1 = -28.0, -155.0
    y = -8.5
    for i in range(nx):
        for j in range(nz):
            xa = x0 + (x1 - x0) * i / nx
            xb = x0 + (x1 - x0) * (i + 1) / nx
            za = z0 + (z1 - z0) * j / nz
            zb = z0 + (z1 - z0) * (j + 1) / nz
            # p1-p0 = (+dx,0,0), p2-p0 = (+dx,0,-dz) => cross = (0, +1, 0) UPWARD
            o.add_quad((xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb))

    # ---------------- Horizon Sailboats ----------------
    for (bx, bz) in ((-14.0, -74.0), (22.0, -102.0)):
        hull = ctx.mb("SailboatHull_%d" % int(bx), mats["bronze_dark"])
        hull.add_box(bx, -8.35, bz, 3.6, 0.55, 1.0)
        mast = ctx.mb("SailboatMast_%d" % int(bx), mats["bronze_dark"])
        mast.add_cylinder(bx, -8.10, bz, 0.06, 0.04, 5.4, segs=8)
        sail = ctx.mb("SailboatSail_%d" % int(bx), mats["sail_canvas"])
        sail.add_tri_raw((bx, -2.7, bz), (bx, -8.0, bz), (bx + 1.85, -8.0, bz),
                         uv0=(0.0, 1.0), uv1=(0.0, 0.0), uv2=(1.0, 0.0))
        sail.add_tri_raw((bx, -2.7, bz), (bx + 1.85, -8.0, bz), (bx, -8.0, bz),
                         uv0=(0.0, 1.0), uv1=(1.0, 0.0), uv2=(0.0, 0.0))

    # ---------------- Sky Cyclorama (continuous 0..1 U across arc) ----------------
    sk = ctx.mb("SkyCyclorama", mats["sky_sunny"])
    R = 148.0
    cz = -4.0
    theta_min = -2.65
    theta_max = 2.65
    y_bot = -26.0
    y_top = 76.0
    segs = 56
    for i in range(segs):
        t0 = theta_min + (theta_max - theta_min) * i / segs
        t1 = theta_min + (theta_max - theta_min) * (i + 1) / segs
        x0s = R * math.sin(t0)
        z0s = cz - R * math.cos(t0)
        x1s = R * math.sin(t1)
        z1s = cz - R * math.cos(t1)
        u0, u1 = i / segs, (i + 1) / segs
        sk.add_tri_raw((x0s, y_bot, z0s), (x1s, y_bot, z1s), (x1s, y_top, z1s), (u0, 0.0), (u1, 0.0), (u1, 1.0))
        sk.add_tri_raw((x0s, y_bot, z0s), (x1s, y_top, z1s), (x0s, y_top, z0s), (u0, 0.0), (u1, 1.0), (u0, 1.0))
