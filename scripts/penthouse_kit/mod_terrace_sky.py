import math
from penthouse_kit.cushion_helper import add_designer_pillow


def _add_round_chair(ctx, mats, cx, cz, face_yaw, pillow_mat):
    # --- swivel pedestal ---
    b = ctx.mb("TerraceSofaPedestal", mats["bronze_dark"])
    b.add_cylinder(cx, 0.03, cz, 0.92, 0.82, 0.12, segs=32)
    b.add_cylinder(cx, 0.15, cz, 0.58, 0.58, 0.05, segs=24)

    # --- airtight curved 240° steam-bent walnut barrel shell (matched to 2.55x Penthouse scale!) ---
    b = ctx.mb("TerraceSofaTeak", mats["walnut_solid"])
    n_seg = 36
    sweep = math.radians(240.0)
    start = face_yaw + math.pi - sweep * 0.5
    R_out, R_in = 1.62, 1.44
    y_base = 0.20
    def h(t):
        ang = abs(t - 0.5) * 2.0
        return 1.48 - 0.58 * (ang ** 1.6)

    for i in range(n_seg):
        t0, t1 = i / n_seg, (i + 1) / n_seg
        a0, a1 = start + sweep * t0, start + sweep * t1
        h0, h1 = h(t0), h(t1)
        c0, s0 = math.cos(a0), math.sin(a0)
        c1, s1 = math.cos(a1), math.sin(a1)
        # Outer curved wall (+N_out)
        b.add_quad(
            (cx + R_out * c1, y_base, cz + R_out * s1),
            (cx + R_out * c0, y_base, cz + R_out * s0),
            (cx + R_out * c0, y_base + h0, cz + R_out * s0),
            (cx + R_out * c1, y_base + h1, cz + R_out * s1),
            uv_scale=(1.0, 1.0),
        )
        # Inner curved wall (-N_out)
        b.add_quad(
            (cx + R_in * c0, y_base, cz + R_in * s0),
            (cx + R_in * c1, y_base, cz + R_in * s1),
            (cx + R_in * c1, y_base + h1, cz + R_in * s1),
            (cx + R_in * c0, y_base + h0, cz + R_in * s0),
            uv_scale=(1.0, 1.0),
        )
        # Top barrel rim (+Y)
        b.add_quad(
            (cx + R_in * c0, y_base + h0, cz + R_in * s0),
            (cx + R_out * c0, y_base + h0, cz + R_out * s0),
            (cx + R_out * c1, y_base + h1, cz + R_out * s1),
            (cx + R_in * c1, y_base + h1, cz + R_in * s1),
            uv_scale=(1.0, 0.25),
        )
        # Bottom barrel rim (-Y)
        b.add_quad(
            (cx + R_out * c0, y_base, cz + R_out * s0),
            (cx + R_in * c0, y_base, cz + R_in * s0),
            (cx + R_in * c1, y_base, cz + R_in * s1),
            (cx + R_out * c1, y_base, cz + R_out * s1),
            uv_scale=(1.0, 0.25),
        )
        if i == 0:
            b.add_quad(
                (cx + R_in * c0, y_base, cz + R_in * s0),
                (cx + R_out * c0, y_base, cz + R_out * s0),
                (cx + R_out * c0, y_base + h0, cz + R_out * s0),
                (cx + R_in * c0, y_base + h0, cz + R_in * s0),
                uv_scale=(0.25, 1.0),
            )
        if i == n_seg - 1:
            b.add_quad(
                (cx + R_out * c1, y_base, cz + R_out * s1),
                (cx + R_in * c1, y_base, cz + R_in * s1),
                (cx + R_in * c1, y_base + h1, cz + R_in * s1),
                (cx + R_out * c1, y_base + h1, cz + R_out * s1),
                uv_scale=(0.25, 1.0),
            )

    # --- dished round bouclé seat cushion (rim Y=0.73, center Y=0.66, strictly inside R=1.42) ---
    b = ctx.mb("TerraceSofaSeat", mats["boucle"])
    seat_profile = [
        (0.00, 0.66), (0.45, 0.67), (0.90, 0.69),
        (1.26, 0.72), (1.40, 0.73), (1.42, 0.64), (1.40, 0.36), (0.00, 0.36),
    ]
    b.add_lathe(cx, 0.0, cz, seat_profile, segs=36)

    # --- contoured inner bouclé wrap backrest (216°, strictly inside R_in=1.44: R=1.20..1.39!) ---
    b = ctx.mb("TerraceSofaBack", mats["boucle"])
    n_b = 28
    sweep_b = math.radians(216.0)
    start_b = face_yaw + math.pi - sweep_b * 0.5
    R_b = 1.20
    recline = math.radians(5.5)
    def y_top_b(t):
        ang = abs(t - 0.5) * 2.0
        return 1.58 - 0.52 * (ang ** 1.5)

    for i in range(n_b):
        t0, t1 = i / n_b, (i + 1) / n_b
        a0, a1 = start_b + sweep_b * t0, start_b + sweep_b * t1
        yt0, yt1 = y_top_b(t0), y_top_b(t1)
        c0, s0 = math.cos(a0), math.sin(a0)
        c1, s1 = math.cos(a1), math.sin(a1)
        off0 = math.sin(recline) * (yt0 - 0.66)
        off1 = math.sin(recline) * (yt1 - 0.66)
        ri0, ri1 = R_b + off0, R_b + off1
        ro0, ro1 = ri0 + 0.10, ri1 + 0.10
        # Inner curved cushion face pointing INWARD toward sitter (-N_out)
        b.add_quad((cx + ri0 * c0, 0.66, cz + ri0 * s0), (cx + ri1 * c1, 0.66, cz + ri1 * s1),
                   (cx + ri1 * c1, yt1, cz + ri1 * s1), (cx + ri0 * c0, yt0, cz + ri0 * s0), uv_scale=(0.5, 0.5))
        # Outer cushion face tucked strictly inside walnut shell (+N_out)
        b.add_quad((cx + ro1 * c1, 0.66, cz + ro1 * s1), (cx + ro0 * c0, 0.66, cz + ro0 * s0),
                   (cx + ro0 * c0, yt0, cz + ro0 * s0), (cx + ro1 * c1, yt1, cz + ro1 * s1), uv_scale=(0.5, 0.5))
        # Top rounded rim (+Y)
        b.add_quad((cx + ri0 * c0, yt0, cz + ri0 * s0), (cx + ri1 * c1, yt1, cz + ri1 * s1),
                   (cx + ro1 * c1, yt1, cz + ro1 * s1), (cx + ro0 * c0, yt0, cz + ro0 * s0), uv_scale=(0.5, 0.2))
        if i == 0:
            b.add_quad((cx + ri0 * c0, 0.66, cz + ri0 * s0), (cx + ro0 * c0, 0.66, cz + ro0 * s0),
                       (cx + ro0 * c0, yt0, cz + ro0 * s0), (cx + ri0 * c0, yt0, cz + ri0 * s0), uv_scale=(0.2, 0.5))
        if i == n_b - 1:
            b.add_quad((cx + ro1 * c1, 0.66, cz + ro1 * s1), (cx + ri1 * c1, 0.66, cz + ri1 * s1),
                       (cx + ri1 * c1, yt1, cz + ri1 * s1), (cx + ro1 * c1, yt1, cz + ro1 * s1), uv_scale=(0.2, 0.5))

    # --- sculpted pinched-corner piped accent pillow ---
    back_a = face_yaw + math.pi
    px = cx + 0.72 * math.cos(back_a)
    pz = cz + 0.72 * math.sin(back_a)
    add_designer_pillow(
        ctx.mb("TerraceSofaPillow_%d" % int(cx * 100), pillow_mat),
        ctx.mb("TerraceSofaPipe_%d" % int(cx * 100), mats["cream_pillow"]),
        px, 1.02, pz, w=0.86, h=0.68, thick=0.26,
        yaw=math.pi * 0.5 - face_yaw, tilt=-0.22,
    )


def build_terrace_and_sky(ctx, mats):
    # ================= TERRACE DECK =================
    b = ctx.mb("TerraceDeck", mats["travertine"])
    b.add_box(0.0, -0.10, -22.8, 32.4, 0.20, 13.6, uv_tile=2.2)
    b.add_box(0.0, 0.02, -29.55, 32.4, 0.10, 0.30, uv_tile=1.0)
    b.add_box(-16.05, 0.02, -22.8, 0.30, 0.10, 13.6, uv_tile=1.0)
    b.add_box(16.05, 0.02, -22.8, 0.30, 0.10, 13.6, uv_tile=1.0)

    # ================= OCEAN CLIFF GLASS BALUSTRADE (Z=-29.42 & X=±16.05, OPEN DOORWAY AT Z=-16!) =================
    b = ctx.mb("TerraceGlass", mats["glass"])
    b.add_box(0.0, 0.53, -29.42, 32.0, 1.06, 0.03)
    b.add_box(-16.05, 0.53, -22.8, 0.03, 1.06, 13.4)
    b.add_box(16.05, 0.53, -22.8, 0.03, 1.06, 13.4)
    b = ctx.mb("TerraceHandrail", mats["brass"])
    b.add_box(0.0, 1.08, -29.42, 32.2, 0.06, 0.10)
    b.add_box(-16.05, 1.08, -22.8, 0.10, 0.06, 13.6)
    b.add_box(16.05, 1.08, -22.8, 0.10, 0.06, 13.6)
    b = ctx.mb("TerracePosts", mats["bronze_dark"])
    for x in (-16.0, -8.0, 0.0, 8.0, 16.0):
        b.add_box(x, 0.54, -29.42, 0.05, 1.08, 0.05)
    for z in (-29.4, -26.0, -22.6, -19.2, -16.2):
        b.add_box(-16.05, 0.54, z, 0.05, 1.08, 0.05)
        b.add_box(16.05, 0.54, z, 0.05, 1.08, 0.05)

    # ================= OUTDOOR RUG =================
    b = ctx.mb("TerraceOutdoorRug", mats["rug_2f"])
    b.add_box(1.10, 0.015, -22.90, 11.6, 0.03, 7.6, uv_tile=1.4)

    # ================= TWO ERGONOMIC ROUND LOUNGE CHAIRS (opening cleanly toward -Z ocean horizon) =================
    _add_round_chair(ctx, mats, -1.35, -22.60, -math.pi * 0.5 + 0.18, mats["cognac_suede"])
    _add_round_chair(ctx, mats, 3.55, -22.60, -math.pi * 0.5 - 0.22, mats["burgundy"])

    # ================= CENTRAL DRUM SIDE TABLE =================
    b = ctx.mb("TerraceSideTable", mats["walnut_fluted"])
    b.add_cylinder(1.10, 0.0, -23.20, 0.72, 0.72, 0.66, segs=32)
    b = ctx.mb("TerraceSideTableTop", mats["travertine"])
    b.add_cylinder(1.10, 0.66, -23.20, 0.76, 0.76, 0.06, segs=32)
    b = ctx.mb("TerraceGlasses", mats["crystal_glass"])
    for gx, gz in [(0.90, -23.08), (1.30, -23.32)]:
        b.add_cylinder(gx, 0.72, gz, 0.075, 0.09, 0.22, segs=14)

    # ================= ROUND OTTOMAN =================
    b = ctx.mb("TerraceOttoman", mats["travertine"])
    b.add_cylinder(-1.10, 0.0, -25.15, 0.68, 0.68, 0.46, segs=28)
    b = ctx.mb("TerraceOttomanCushion", mats["boucle"])
    b.add_cylinder(-1.10, 0.46, -25.15, 0.70, 0.68, 0.14, segs=28)

    # ================= LANTERNS =================
    for lx in (-5.10, 7.30):
        tag = "L" if lx < 0 else "R"
        b = ctx.mb("TerraceLantern_%s" % tag, mats["bronze_dark"])
        b.add_cylinder(lx, 0.0, -24.40, 0.16, 0.16, 0.82, segs=14)
        b = ctx.mb("TerraceLanternGlow_%s" % tag, mats["warm_bulb"])
        b.add_sphere(lx, 0.92, -24.40, 0.14, 0.17, 0.14, rings=10, segs=14)

    # ================= OLIVE TREES (placed symmetrically at X=-12.2 / +12.4) =================
    for ox, oz in [(-12.2, -23.5), (12.4, -24.2)]:
        tag = int(ox)
        b = ctx.mb("OlivePlanter_%d" % tag, mats["travertine"])
        b.add_cylinder(ox, 0.0, oz, 0.55, 0.50, 0.55, segs=20)
        b = ctx.mb("OliveTrunk_%d" % tag, mats["bark"])
        b.add_cylinder(ox, 0.55, oz, 0.10, 0.08, 1.30, segs=12)
        b = ctx.mb("OliveFoliage_%d" % tag, mats["olive_leaf"])
        b.add_sphere(ox, 2.10, oz, 0.85, 0.70, 0.85, rings=12, segs=16)
        b = ctx.mb("OliveFoliageBright_%d" % tag, mats["olive_leaf_bright"])
        b.add_sphere(ox + 0.25, 2.35, oz + 0.15, 0.55, 0.45, 0.55, rings=10, segs=14)

    # ================= CLIFF, HEADLANDS, OCEAN & SAILBOATS (Y=-8.5 horizon vista!) =================
    c = ctx.mb("CoastalCliff", mats["headland_rock"])
    c.add_quad((-18.0, -0.5, -29.8), (18.0, -0.5, -29.8), (18.0, -8.8, -46.0), (-18.0, -8.8, -46.0), flip=True)
    hd = ctx.mb("CoastalHeadlands", mats["headland_rock"])
    for xs, hs, zh in (
        ([-92, -74, -56, -40, -26, -15, -7], [-8.5, 2.2, 4.4, 3.6, 1.4, -2.5, -8.5], -92.0),
        ([16, 28, 44, 62, 78, 96], [-8.5, -1.8, 2.8, 5.1, 3.2, -8.5], -114.0),
    ):
        for k in range(len(xs) - 1):
            u0, u1 = k / max(1, len(xs) - 1), (k + 1) / max(1, len(xs) - 1)
            hd.add_tri_raw((xs[k], -8.5, zh), (xs[k + 1], -8.5, zh + 1.5), (xs[k + 1], hs[k + 1], zh), (u0, 0), (u1, 0), (u1, 1))
            hd.add_tri_raw((xs[k], -8.5, zh), (xs[k + 1], hs[k + 1], zh), (xs[k], hs[k], zh), (u0, 0), (u1, 1), (u0, 1))

    o = ctx.mb("OceanVistaWater", mats["horizon_ocean"])
    nx, nz = 24, 16
    for i in range(nx):
        for j in range(nz):
            xa, xb = -180.0 + 360.0 * i / nx, -180.0 + 360.0 * (i + 1) / nx
            za, zb = -28.0 - 127.0 * j / nz, -28.0 - 127.0 * (j + 1) / nz
            o.add_quad((xa, -8.5, za), (xb, -8.5, za), (xb, -8.5, zb), (xa, -8.5, zb))

    for (bx, bz) in ((-14.0, -74.0), (22.0, -102.0)):
        ctx.mb("SailboatHull_%d" % int(bx), mats["bronze_dark"]).add_box(bx, -8.35, bz, 3.6, 0.55, 1.0)
        ctx.mb("SailboatMast_%d" % int(bx), mats["bronze_dark"]).add_cylinder(bx, -8.10, bz, 0.06, 0.04, 5.4, segs=8)
        sail = ctx.mb("SailboatSail_%d" % int(bx), mats["sail_canvas"])
        sail.add_tri_raw((bx, -2.7, bz), (bx, -8.0, bz), (bx + 1.85, -8.0, bz), (0, 1), (0, 0), (1, 0))
        sail.add_tri_raw((bx, -2.7, bz), (bx + 1.85, -8.0, bz), (bx, -8.0, bz), (0, 1), (1, 0), (0, 0))

    # ================= SKY CYCLORAMA =================
    b = ctx.mb("SkyCyclorama", mats["sky_sunny"])
    radius = 148.0
    y_bot, y_top = -26.0, 76.0
    theta_min, theta_max = -2.65, 2.65
    n_sky = 40
    for i in range(n_sky):
        t0 = i / n_sky
        t1 = (i + 1) / n_sky
        a0 = theta_min + (theta_max - theta_min) * t0
        a1 = theta_min + (theta_max - theta_min) * t1
        c0, s0 = math.cos(a0), math.sin(a0)
        c1, s1 = math.cos(a1), math.sin(a1)
        b.add_quad(
            (radius * c0, y_bot, radius * s0),
            (radius * c1, y_bot, radius * s1),
            (radius * c1, y_top, radius * s1),
            (radius * c0, y_top, radius * s0),
            uv_scale=(1.0 / n_sky, 1.0),
        )
