import math
from penthouse_kit.cushion_helper import add_designer_pillow


def _barrel_chair(ctx, mats, name, cx, cz, face_yaw, pillow_mat):
    b = ctx.mb(name, mats["rift_oak"])
    n_seg = 36
    sweep = math.radians(240.0)
    start = face_yaw + math.pi - sweep * 0.5
    R_out, R_in = 1.62, 1.44
    y_base = 0.20

    def h(t):
        return 1.48 - 0.58 * abs(2.0 * t - 1.0) ** 1.6

    for i in range(n_seg):
        t0, t1 = i / n_seg, (i + 1) / n_seg
        a0, a1 = start + sweep * t0, start + sweep * t1
        h0, h1 = h(t0), h(t1)
        c0, s0 = math.cos(a0), math.sin(a0)
        c1, s1 = math.cos(a1), math.sin(a1)
        b.add_quad((cx + R_out * c1, y_base, cz + R_out * s1), (cx + R_out * c0, y_base, cz + R_out * s0),
                   (cx + R_out * c0, y_base + h0, cz + R_out * s0), (cx + R_out * c1, y_base + h1, cz + R_out * s1), uv_scale=(1.0, 1.0))
        b.add_quad((cx + R_in * c0, y_base, cz + R_in * s0), (cx + R_in * c1, y_base, cz + R_in * s1),
                   (cx + R_in * c1, y_base + h1, cz + R_in * s1), (cx + R_in * c0, y_base + h0, cz + R_in * s0), uv_scale=(1.0, 1.0))
        b.add_quad((cx + R_in * c0, y_base + h0, cz + R_in * s0), (cx + R_out * c0, y_base + h0, cz + R_out * s0),
                   (cx + R_out * c1, y_base + h1, cz + R_out * s1), (cx + R_in * c1, y_base + h1, cz + R_in * s1), uv_scale=(1.0, 0.25))
        b.add_quad((cx + R_out * c0, y_base, cz + R_out * s0), (cx + R_in * c0, y_base, cz + R_in * s0),
                   (cx + R_in * c1, y_base, cz + R_in * s1), (cx + R_out * c1, y_base, cz + R_out * s1), uv_scale=(1.0, 0.25))
        if i == 0:
            b.add_quad((cx + R_in * c0, y_base, cz + R_in * s0), (cx + R_out * c0, y_base, cz + R_out * s0),
                       (cx + R_out * c0, y_base + h0, cz + R_out * s0), (cx + R_in * c0, y_base + h0, cz + R_in * s0), uv_scale=(0.25, 1.0))
        if i == n_seg - 1:
            b.add_quad((cx + R_out * c1, y_base, cz + R_out * s1), (cx + R_in * c1, y_base, cz + R_in * s1),
                       (cx + R_in * c1, y_base + h1, cz + R_in * s1), (cx + R_out * c1, y_base + h1, cz + R_out * s1), uv_scale=(0.25, 1.0))

    s = ctx.mb("TerraceSofaSeat" if cx < 0 else "TerraceSofaSeat2", mats["boucle"])
    s.add_lathe(cx, 0.0, cz, [
        (0.00, 0.66), (0.45, 0.67), (0.90, 0.69),
        (1.26, 0.72), (1.40, 0.73), (1.42, 0.64), (1.40, 0.36), (0.00, 0.36),
    ], segs=36)

    bk = ctx.mb(name + "_Back", mats["boucle"])
    n_b = 28
    sweep_b = math.radians(216.0)
    start_b = face_yaw + math.pi - sweep_b * 0.5
    R_b = 1.20
    recline = math.radians(5.5)
    for i in range(n_b):
        t0, t1 = i / n_b, (i + 1) / n_b
        a0, a1 = start_b + sweep_b * t0, start_b + sweep_b * t1
        yt0 = 1.58 - 0.52 * abs(2.0 * t0 - 1.0) ** 1.5
        yt1 = 1.58 - 0.52 * abs(2.0 * t1 - 1.0) ** 1.5
        c0, s0 = math.cos(a0), math.sin(a0)
        c1, s1 = math.cos(a1), math.sin(a1)
        ri0 = R_b + math.sin(recline) * (yt0 - 0.66)
        ri1 = R_b + math.sin(recline) * (yt1 - 0.66)
        ro0, ro1 = ri0 + 0.10, ri1 + 0.10
        bk.add_quad((cx + ri0 * c0, 0.66, cz + ri0 * s0), (cx + ri1 * c1, 0.66, cz + ri1 * s1),
                    (cx + ri1 * c1, yt1, cz + ri1 * s1), (cx + ri0 * c0, yt0, cz + ri0 * s0), uv_scale=(0.5, 0.5))
        bk.add_quad((cx + ro1 * c1, 0.66, cz + ro1 * s1), (cx + ro0 * c0, 0.66, cz + ro0 * s0),
                    (cx + ro0 * c0, yt0, cz + ro0 * s0), (cx + ro1 * c1, yt1, cz + ro1 * s1), uv_scale=(0.5, 0.5))
        bk.add_quad((cx + ri0 * c0, yt0, cz + ri0 * s0), (cx + ri1 * c1, yt1, cz + ri1 * s1),
                    (cx + ro1 * c1, yt1, cz + ro1 * s1), (cx + ro0 * c0, yt0, cz + ro0 * s0), uv_scale=(0.5, 0.2))
        if i == 0:
            bk.add_quad((cx + ri0 * c0, 0.66, cz + ri0 * s0), (cx + ro0 * c0, 0.66, cz + ro0 * s0),
                        (cx + ro0 * c0, yt0, cz + ro0 * s0), (cx + ri0 * c0, yt0, cz + ri0 * s0), uv_scale=(0.2, 0.5))
        if i == n_b - 1:
            bk.add_quad((cx + ro1 * c1, 0.66, cz + ro1 * s1), (cx + ri1 * c1, 0.66, cz + ri1 * s1),
                        (cx + ri1 * c1, yt1, cz + ri1 * s1), (cx + ro1 * c1, yt1, cz + ro1 * s1), uv_scale=(0.2, 0.5))

    back_a = face_yaw + math.pi
    px = cx + 0.72 * math.cos(back_a)
    pz = cz + 0.72 * math.sin(back_a)
    add_designer_pillow(
        ctx.mb(name + "_Pillow", pillow_mat),
        ctx.mb(name + "_Pipe", mats["cream_pillow"]),
        px, 1.02, pz, w=0.86, h=0.68, thick=0.26,
        yaw=math.pi * 0.5 - face_yaw, tilt=-0.22,
    )


def build_terrace_and_sky(ctx, mats):
    d = ctx.mb("TerraceDeck", mats["travertine"])
    d.add_box(0.0, -0.10, -22.0, 34.0, 0.20, 16.0, uv_tile=2.0)

    g = ctx.mb("TerraceGlass", mats["glass"])
    g.add_box(0.0, 0.75, -29.42, 32.0, 1.50, 0.04)
    g.add_box(-16.05, 0.75, -22.0, 0.04, 1.50, 15.0)
    g.add_box(16.05, 0.75, -22.0, 0.04, 1.50, 15.0)

    hr = ctx.mb("TerraceHandrail", mats["brass"])
    hr.add_box(0.0, 1.55, -29.42, 32.2, 0.06, 0.10)
    hr.add_box(-16.05, 1.55, -22.0, 0.10, 0.06, 15.2)
    hr.add_box(16.05, 1.55, -22.0, 0.10, 0.06, 15.2)

    p = ctx.mb("TerracePosts", mats["bronze_dark"])
    for x in (-16.0, -8.0, 0.0, 8.0, 16.0):
        p.add_cylinder(x, 0.0, -29.42, 0.05, 0.05, 1.55, segs=10)
    for z in (-29.0, -22.0, -15.0):
        p.add_cylinder(-16.05, 0.0, z, 0.05, 0.05, 1.55, segs=10)
        p.add_cylinder(16.05, 0.0, z, 0.05, 0.05, 1.55, segs=10)

    r = ctx.mb("TerraceOutdoorRug", mats["rug_2f"])
    r.add_box(1.10, 0.015, -22.90, 11.6, 0.03, 7.6)
    r.add_quad((-4.7, 0.032, -19.1), (6.9, 0.032, -19.1),
               (6.9, 0.032, -26.7), (-4.7, 0.032, -26.7),
               uv_scale=(1.0, 1.0))

    _barrel_chair(ctx, mats, "TerraceSofaSeatChair1",
                  -1.35, -22.60, -math.pi * 0.5 + 0.18, mats["slate_linen"])
    _barrel_chair(ctx, mats, "TerraceSofaSeatChair2",
                  3.55, -22.60, -math.pi * 0.5 - 0.22, mats["burgundy"])

    dt = ctx.mb("TerraceDrumTable", mats["rift_oak"])
    dt.add_cylinder(1.10, 0.0, -23.20, 0.55, 0.55, 0.70, segs=24)
    tt = ctx.mb("TerraceDrumTop", mats["travertine"])
    tt.add_cylinder(1.10, 0.70, -23.20, 0.58, 0.58, 0.04, segs=24)

    gl = ctx.mb("TerraceGlasses", mats["crystal_glass"])
    for gx, gz in ((0.90, -23.08), (1.30, -23.32)):
        gl.add_cylinder(gx, 0.74, gz, 0.045, 0.05, 0.14, segs=12)

    ot = ctx.mb("TerraceOttoman", mats["cognac_suede"])
    ot.add_rounded_box(-1.10, 0.22, -25.15, 1.10, 0.44, 0.90, bevel=0.08)

    ln = ctx.mb("TerraceLanterns", mats["bronze_dark"])
    for lx in (-5.10, 7.30):
        ln.add_cylinder(lx, 0.0, -24.40, 0.16, 0.16, 0.55, segs=12)
        ln.add_sphere(lx, 0.62, -24.40, 0.14, 0.18, 0.14, rings=8, segs=12)
    lb = ctx.mb("TerraceLanternGlow", mats["warm_bulb"])
    for lx in (-5.10, 7.30):
        lb.add_sphere(lx, 0.55, -24.40, 0.10, 0.12, 0.10, rings=6, segs=10)

    for tx, tz in ((-12.2, -23.5), (12.4, -24.2)):
        tr = ctx.mb("TerraceOliveTrunk_%d" % int(tx), mats["bark"])
        tr.add_cylinder(tx, 0.0, tz, 0.14, 0.10, 1.30, segs=10)
        fo = ctx.mb("TerraceOliveFoliage_%d" % int(tx), mats["olive_leaf"])
        fo.add_sphere(tx, 1.65, tz, 0.85, 0.70, 0.85, rings=10, segs=14)
        fo.add_sphere(tx + 0.35, 1.95, tz - 0.20, 0.55, 0.50, 0.55, rings=8, segs=12)
        fo.add_sphere(tx - 0.30, 1.90, tz + 0.25, 0.50, 0.45, 0.50, rings=8, segs=12)

    cf = ctx.mb("CoastalCliff", mats["headland_rock"])
    cf.add_quad((-16.0, -0.5, -29.8), (16.0, -0.5, -29.8),
                (16.0, -8.8, -46.0), (-16.0, -8.8, -46.0))

    ow = ctx.mb("OceanVistaWater", mats["horizon_ocean"])
    nx, nz = 24, 16
    x0, x1, z0, z1 = -210.0, 210.0, -28.0, -165.0
    for i in range(nx):
        for j in range(nz):
            xa = x0 + (x1 - x0) * i / nx
            xb = x0 + (x1 - x0) * (i + 1) / nx
            za = z0 + (z1 - z0) * j / nz
            zb = z0 + (z1 - z0) * (j + 1) / nz
            ow.add_quad((xa, -8.5, za), (xb, -8.5, za),
                        (xb, -8.5, zb), (xa, -8.5, zb))

    # Grounded 3-layer Mediterranean coastline & mountains (anchored cleanly into Y=-9.0 seabed so zero floating gap!)
    hk = ctx.mb("CoastalHeadlandsRock", mats["headland_rock"])
    for cx_h, cz_h, rx_h, ry_h, rz_h in (
        (-48.0, -68.0, 26.0, 4.6, 13.0),
        (-28.0, -64.0, 18.0, 3.4, 10.5),
        (54.0, -78.0, 22.0, 3.8, 12.0),
    ):
        rings_h, segs_h = 8, 22
        for ri in range(rings_h):
            v0, v1 = (ri / rings_h) * (math.pi * 0.5), ((ri + 1) / rings_h) * (math.pi * 0.5)
            for si in range(segs_h):
                u0, u1 = (si / segs_h) * 2.0 * math.pi, ((si + 1) / segs_h) * 2.0 * math.pi
                def pt(v, u):
                    c_v, s_v = math.cos(v), math.sin(v)
                    return (cx_h + rx_h * c_v * math.cos(u), -9.0 + ry_h * s_v, cz_h + rz_h * c_v * math.sin(u))
                hk.add_quad(pt(v0, u0), pt(v1, u0), pt(v1, u1), pt(v0, u1), uv_scale=(1.0, 0.5))

    sf = ctx.mb("CoastalSurfFoam", mats["cream_pillow"])
    for sx, sz, sr in ((-48.0, -68.0, 27.2), (-28.0, -64.0, 19.0), (54.0, -78.0, 23.0)):
        sf.add_cylinder(sx, -8.49, sz, sr, sr * 0.96, 0.06, segs=28)

    pl = ctx.mb("CoastalPineHeadlands", mats["coastal_pine"])
    for cx_h, cz_h, rx_h, ry_h, rz_h in (
        (-74.0, -102.0, 44.0, 11.2, 22.0),
        (-36.0, -96.0, 28.0, 7.6, 16.0),
        (64.0, -112.0, 42.0, 11.8, 20.0),
        (28.0, -104.0, 26.0, 6.8, 15.0),
    ):
        rings_h, segs_h = 9, 24
        for ri in range(rings_h):
            v0, v1 = (ri / rings_h) * (math.pi * 0.5), ((ri + 1) / rings_h) * (math.pi * 0.5)
            for si in range(segs_h):
                u0, u1 = (si / segs_h) * 2.0 * math.pi, ((si + 1) / segs_h) * 2.0 * math.pi
                def pt_p(v, u):
                    c_v, s_v = math.cos(v), math.sin(v)
                    return (cx_h + rx_h * c_v * math.cos(u), -9.0 + ry_h * s_v, cz_h + rz_h * c_v * math.sin(u))
                pl.add_quad(pt_p(v0, u0), pt_p(v1, u0), pt_p(v1, u1), pt_p(v0, u1), uv_scale=(1.0, 0.5))

    fm = ctx.mb("FarMistMountains", mats["far_mist_mountain"])
    K = 48
    for i in range(K):
        t0, t1 = i / K, (i + 1) / K
        xa = -165.0 + 330.0 * t0
        xb = -165.0 + 330.0 * t1
        ya = -9.0 + 18.2 * (0.5 + 0.5 * math.cos(math.pi * (2 * t0 - 1) + 0.7)) * (0.6 + 0.4 * math.sin(3 * math.pi * t0))
        yb = -9.0 + 18.2 * (0.5 + 0.5 * math.cos(math.pi * (2 * t1 - 1) + 0.7)) * (0.6 + 0.4 * math.sin(3 * math.pi * t1))
        fm.add_quad((xa, -9.0, -142.0), (xb, -9.0, -142.0),
                    (xb, yb, -142.0), (xa, ya, -142.0))

    sb = ctx.mb("CoastalSailboats", mats["sail_canvas"])
    for bx, bz in ((-14.0, -74.0), (22.0, -102.0)):
        sb.add_quad((bx - 0.6, -8.4, bz), (bx + 0.6, -8.4, bz),
                    (bx + 0.6, -8.4, bz + 0.3), (bx - 0.6, -8.4, bz + 0.3))
        sb.add_quad((bx, -8.4, bz + 0.15), (bx, -6.4, bz + 0.15),
                    (bx + 0.5, -8.4, bz + 0.15), (bx, -8.4, bz + 0.15))

    sk = ctx.mb("SkyCyclorama", mats["sky_sunny"])
    sk.add_lathe(0.0, -32.0, 0.0,
                 [(245.0, 0.0), (245.0, 148.0), (0.0, 148.0)], segs=36)
