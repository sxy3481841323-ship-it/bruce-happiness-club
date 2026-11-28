import math

def build_south_terrace_and_mountains(ctx, mats):
    mb = ctx.mb
    M = mats
    travertine = M.get('travertine', M.get('limestone', 0))
    basalt = M.get('basalt', 0)
    steel = M.get('charcoal_steel', 0)
    glass = M.get('glass', 0)
    teak = M.get('teak', 0)
    cushion = M.get('offwhite_cushion', 0)
    water = M.get('alpine_lake', 0)
    conifer = M.get('conifer_dark', 0)
    rock = M.get('limestone', 0)
    mtn = M.get('aaa_mountain', 0)
    led = M.get('warm_led', 0)
    stain = M.get('stainless', 0)

    # ---- Terrace deck (travertine) ----
    b = mb('terrace_deck', travertine)
    b.add_box(0.0, -0.30, 45.0, 30.4, 0.60, 18.0, uv_tile=6)
    # pool cutout rim coping
    b.add_box(-3.6, -0.02, 41.4, 14.6, 0.10, 0.5, uv_tile=3)
    b.add_box(-3.6, -0.02, 52.9, 14.6, 0.10, 0.5, uv_tile=3)
    b.add_box(-10.9, -0.02, 47.15, 0.5, 0.10, 11.5, uv_tile=3)
    b.add_box(3.7, -0.02, 47.15, 0.5, 0.10, 11.5, uv_tile=3)

    # ---- Sunken infinity pool basin ----
    b = mb('pool_basin', basalt)
    b.add_box(-3.6, -1.30, 47.15, 14.4, 0.30, 11.3, uv_tile=4)
    b.add_box(-10.8, -0.65, 47.15, 0.3, 1.3, 11.3, uv_tile=3)
    b.add_box(3.6, -0.65, 47.15, 0.3, 1.3, 11.3, uv_tile=3)
    b.add_box(-3.6, -0.65, 41.5, 14.4, 1.3, 0.3, uv_tile=3)
    # infinity weir lip
    b.add_box(-3.6, -0.10, 52.9, 14.6, 0.22, 0.35, uv_tile=3)
    # underwater LED strip
    b = mb('pool_led', led)
    b.add_box(-3.6, -1.05, 41.7, 14.0, 0.06, 0.10)
    b.add_box(-10.6, -1.05, 47.15, 0.10, 0.06, 11.0)
    b.add_box(3.4, -1.05, 47.15, 0.10, 0.06, 11.0)

    # ---- Pool water surface ----
    b = mb('pool_water', water)
    b.add_box(-3.6, -0.16, 47.15, 14.2, 0.04, 11.1, uv_tile=2)

    # ---- Balustrade (Frameless Infinity Glass + Steel Posts; Z=36 door threshold stays wide open!) ----
    b = mb('balustrade_steel', steel)
    posts = []
    for x in (-15.0, -10.8, 3.8, 9.4, 15.0):
        posts.append((x, 53.8))
    for z in (37.0, 42.5, 48.0, 53.8):
        posts.append((-15.0, z))
        posts.append((15.0, z))
    for (px, pz) in posts:
        b.add_box(px, 1.12, pz, 0.12, 2.24, 0.12)
    b = mb('balustrade_glass', glass)
    b.add_box(9.3, 1.12, 53.8, 11.2, 2.10, 0.05)
    b.add_box(-12.9, 1.12, 53.8, 4.2, 2.10, 0.05)
    b.add_box(-15.0, 1.12, 45.0, 0.05, 2.10, 17.6)
    b.add_box(15.0, 1.12, 45.0, 0.05, 2.10, 17.6)

    # ---- Scaled Poolside Loungers (2.6 x 5.2 WU at Penthouse scale) ----
    def lounge(cx, cz, rot):
        bb = mb('lounge_teak', teak)
        bb.add_box(cx, 0.62, cz, 2.05, 0.16, 5.10, rot_y=rot)
        bb.add_box(cx, 1.25, cz - 2.10, 2.05, 1.15, 0.16, rot_y=rot)
        bc = mb('lounge_cushion', cushion)
        bc.add_rounded_box(cx, 0.82, cz + 0.15, 1.88, 0.24, 4.70, bevel=0.06, rot_y=rot)
        bc.add_rounded_box(cx, 1.42, cz - 1.98, 1.88, 0.96, 0.22, bevel=0.06, rot_y=rot)
    lounge(-13.0, 46.2, 0.0)
    lounge(6.6, 48.4, 0.0)

    # side tables
    b = mb('side_table', teak)
    b.add_cylinder(-11.4, 0.0, 46.2, 0.45, 0.45, 0.92, segs=16)
    b.add_cylinder(4.9, 0.0, 48.4, 0.45, 0.45, 0.92, segs=16)

    # umbrella
    b = mb('umbrella_pole', steel)
    b.add_cylinder(-13.8, 0.0, 42.6, 0.07, 0.07, 5.6, segs=10)
    b = mb('umbrella_canopy', cushion)
    b.add_lathe(-13.8, 5.4, 42.6, [(0.0, 0.0), (3.4, 0.0), (3.1, 0.55), (0.0, 0.85)], segs=18)

    # ---- Outdoor Stainless Built-In Gas BBQ Grill + Limestone Prep Bar ----
    b = mb('bbq_body', stain)
    b.add_box(11.4, 1.12, 41.2, 4.8, 2.24, 2.1, uv_tile=2)
    b.add_box(11.4, 2.48, 41.2, 4.6, 0.72, 1.9, uv_tile=2)
    b = mb('bbq_grates', steel)
    for i in range(8):
        b.add_box(9.4 + i * 0.54, 2.28, 41.2, 0.08, 0.06, 1.7)
    b = mb('bbq_knobs', steel)
    for i in range(5):
        b.add_cylinder(9.6 + i * 0.88, 1.85, 40.10, 0.11, 0.11, 0.14, segs=12, rot_x=math.pi / 2)
    b = mb('prep_bar', rock)
    b.add_box(11.4, 1.12, 38.4, 5.6, 2.24, 2.1, uv_tile=2)
    b.add_box(11.4, 2.28, 38.4, 5.8, 0.14, 2.3, uv_tile=2)
    b = mb('herb_planter', conifer)
    b.add_box(13.5, 2.52, 38.4, 1.1, 0.45, 0.9)
    for i in range(5):
        b.add_sphere(13.15 + i * 0.18, 2.92, 38.4, 0.16, 0.22, 0.16, rings=6, segs=8)

    # ---- Alpine fjord lake surface (open mirror lake Z in [54..152]) ----
    b = mb('lake_surface', water)
    b.add_box(0.0, -4.40, 108.0, 420.0, 0.08, 108.0, uv_tile=10)

    # ---- Shoreline promontories ----
    b = mb('shore_rock', rock)
    for (sx, sz, sw, sd) in [(-125, 76, 48, 16), (-68, 72, 34, 12), (74, 74, 38, 14), (132, 78, 48, 16)]:
        b.add_box(sx, -3.5, sz, sw, 2.8, sd, uv_tile=4)
    b = mb('shore_pines', conifer)
    for i in range(28):
        px = -155 + i * 11.5
        if -44 < px < 44:
            continue
        pz = 70.0 + (i % 4) * 3.5
        h = 3.2 + (i % 5) * 0.9
        b.add_cylinder(px, -3.2, pz, 0.25, 0.05, h, segs=8)
        b.add_sphere(px, -3.2 + h, pz, 1.2, 1.8, 1.2, rings=8, segs=10)

    # ---- Distant Sculpted Multi-Peak Dolomite Alps (Z in [108, 212]) ----
    NX, NZ = 84, 28
    X0, X1 = -205.0, 205.0
    Z0, Z1 = 108.0, 212.0
    Y_BASE = -5.0

    def ridged(x, z):
        # Twin towering Dolomite spires framing a wide golden glacial valley saddle
        dl = math.hypot(x + 56.0, z - 156.0)
        dr = math.hypot(x - 58.0, z - 162.0)
        dc = math.hypot(x - 4.0, z - 184.0)
        df = math.hypot(x + 118.0, z - 168.0)
        dg = math.hypot(x - 122.0, z - 170.0)
        pl = 58.0 * math.exp(-(dl * dl) / (2.0 * 30.0 * 30.0))
        pr = 64.0 * math.exp(-(dr * dr) / (2.0 * 32.0 * 32.0))
        pc = 42.0 * math.exp(-(dc * dc) / (2.0 * 24.0 * 24.0))
        pf = 48.0 * math.exp(-(df * df) / (2.0 * 34.0 * 34.0))
        pg = 50.0 * math.exp(-(dg * dg) / (2.0 * 34.0 * 34.0))
        base = max(pl, pr, pc, pf, pg)
        amp = 1.0
        freq = 0.042
        ridge = 0.0
        for o in range(5):
            n = math.sin(x * freq + o * 1.7) * math.cos(z * freq * 1.15 + o * 2.3)
            n += 0.5 * math.sin(x * freq * 2.1 - z * freq * 0.7 + o)
            r = 1.0 - abs(n * 0.55)
            ridge += r * r * amp
            amp *= 0.52
            freq *= 2.02
        h = base + ridge * 5.2 * min(1.0, base / 18.0 + 0.25)
        ex = min(1.0, (x - X0) / 30.0, (X1 - x) / 30.0)
        ez = min(1.0, (z - Z0) / 22.0, (Z1 - z) / 22.0)
        h *= max(0.0, ex) * max(0.0, ez)
        return Y_BASE + max(0.0, h)

    verts = [[0.0] * 3 for _ in range((NX + 1) * (NZ + 1))]
    for iz in range(NZ + 1):
        z = Z0 + (Z1 - Z0) * iz / NZ
        for ix in range(NX + 1):
            x = X0 + (X1 - X0) * ix / NX
            h = ridged(x, z)
            verts[iz * (NX + 1) + ix] = [x, h, z]

    def vget(ix, iz):
        ix = max(0, min(NX, ix))
        iz = max(0, min(NZ, iz))
        return verts[iz * (NX + 1) + ix]

    def normal_at(ix, iz):
        dx = 2.0 * (X1 - X0) / NX
        dz = 2.0 * (Z1 - Z0) / NZ
        hl = vget(ix - 1, iz)[1]
        hr = vget(ix + 1, iz)[1]
        hd = vget(ix, iz - 1)[1]
        hu = vget(ix, iz + 1)[1]
        nx = (hl - hr) / dx
        nz = (hd - hu) / dz
        ny = 1.0
        ln = math.sqrt(nx * nx + ny * ny + nz * nz)
        return (nx / ln, ny / ln, nz / ln)

    b = mb('mountain_massif', mtn)
    for iz in range(NZ):
        for ix in range(NX):
            p00 = vget(ix, iz)
            p10 = vget(ix + 1, iz)
            p01 = vget(ix, iz + 1)
            p11 = vget(ix + 1, iz + 1)
            n00 = normal_at(ix, iz)
            n10 = normal_at(ix + 1, iz)
            n01 = normal_at(ix, iz + 1)
            n11 = normal_at(ix + 1, iz + 1)
            u0 = (ix / NX) * 4.0
            u1 = ((ix + 1) / NX) * 4.0
            v00 = max(0.02, min(0.98, (p00[1] - (-4.8)) / 62.0))
            v10 = max(0.02, min(0.98, (p10[1] - (-4.8)) / 62.0))
            v01 = max(0.02, min(0.98, (p01[1] - (-4.8)) / 62.0))
            v11 = max(0.02, min(0.98, (p11[1] - (-4.8)) / 62.0))
            b.add_tri_raw(p00, p10, p11, (u0, v00), (u1, v10), (u1, v11), n00, n10, n11)
            b.add_tri_raw(p00, p11, p01, (u0, v00), (u1, v11), (u0, v01), n00, n11, n01)
