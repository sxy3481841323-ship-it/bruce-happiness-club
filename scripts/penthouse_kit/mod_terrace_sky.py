import math

def build_terrace_and_sky(ctx, mats):
    # ---------------- Sunlit Sky Terrace Deck ----------------
    b = ctx.mb("TerraceDeck", mats["travertine"])
    # Honed travertine deck slab
    b.add_box(0.0, -0.14, -20.35, 32.4, 0.20, 8.5, uv_tile=2.0)
    # Walnut perimeter edge
    bw = ctx.mb("TerraceWalnutEdge", mats["walnut_solid"])
    bw.add_box(0.0, -0.04, -16.15, 32.4, 0.06, 0.10, uv_tile=1.0)
    bw.add_box(0.0, -0.04, -24.55, 32.4, 0.06, 0.10, uv_tile=1.0)
    bw.add_box(-16.15, -0.04, -20.35, 0.10, 0.06, 8.5, uv_tile=1.0)
    bw.add_box(16.15, -0.04, -20.35, 0.10, 0.06, 8.5, uv_tile=1.0)

    # ---------------- Glass & Brass Railing ----------------
    bg = ctx.mb("TerraceGlassRail", mats["glass"])
    bb = ctx.mb("TerraceBrassRail", mats["brass"])
    # Front rail along Z = -24.4
    bg.add_box(0.0, 1.15, -24.4, 32.0, 2.30, 0.03, uv_tile=1.0)
    bb.add_box(0.0, 2.35, -24.4, 32.0, 0.06, 0.08, uv_tile=1.0)
    bb.add_box(0.0, 0.02, -24.4, 32.0, 0.06, 0.08, uv_tile=1.0)
    # Side returns
    for sx in (-16.0, 16.0):
        bg.add_box(sx, 1.15, -20.25, 0.03, 2.30, 8.3, uv_tile=1.0)
        bb.add_box(sx, 2.35, -20.25, 0.08, 0.06, 8.3, uv_tile=1.0)
        bb.add_box(sx, 0.02, -20.25, 0.08, 0.06, 8.3, uv_tile=1.0)
    # Brass posts
    for i in range(9):
        px = -16.0 + i * 4.0
        bb.add_cylinder(px, -0.04, -24.4, 0.035, 0.035, 2.39, segs=10)
    for sx in (-16.0, 16.0):
        for i in range(3):
            pz = -24.4 + i * 4.15
            bb.add_cylinder(sx, -0.04, pz, 0.035, 0.035, 2.39, segs=10)

    # ---------------- Olive Trees in Ceramic Planters ----------------
    tree_specs = [
        (-11.2, -21.2, 1.00),
        (8.8, -22.0, 1.10),
        (12.6, -21.6, 0.95),
    ]
    for idx, (tx, tz, scale) in enumerate(tree_specs):
        # Tapered ceramic planter
        bc = ctx.mb("Planter_%d" % idx, mats["ceramic_white"])
        profile = [
            (0.00, 0.00),
            (0.42 * scale, 0.00),
            (0.46 * scale, 0.05),
            (0.52 * scale, 0.55),
            (0.56 * scale, 0.95),
            (0.58 * scale, 1.00),
            (0.54 * scale, 1.02),
            (0.50 * scale, 0.98),
        ]
        bc.add_lathe(tx, 0.0, tz, profile, segs=24)
        # Soil disc
        bs = ctx.mb("Soil_%d" % idx, mats["soil"])
        bs.add_cylinder(tx, 0.92, tz, 0.50 * scale, 0.50 * scale, 0.06, segs=20)

        # Sculpted branching trunk
        bt = ctx.mb("Trunk_%d" % idx, mats["bark"])
        base_y = 0.95
        trunk_pts = [
            (tx, base_y, tz),
            (tx + 0.05 * scale, base_y + 0.9 * scale, tz + 0.03),
            (tx - 0.08 * scale, base_y + 1.8 * scale, tz - 0.05),
            (tx + 0.04 * scale, base_y + 2.6 * scale, tz + 0.02),
        ]
        trunk_radii = [0.14 * scale, 0.11 * scale, 0.08 * scale, 0.05 * scale]
        bt.add_curved_tube(trunk_pts, trunk_radii, segs=10)

        # Branches
        branch_defs = [
            ((tx, base_y + 1.6 * scale, tz), (tx + 0.9 * scale, base_y + 2.6 * scale, tz + 0.4 * scale)),
            ((tx, base_y + 1.9 * scale, tz), (tx - 0.8 * scale, base_y + 2.9 * scale, tz - 0.5 * scale)),
            ((tx, base_y + 2.2 * scale, tz), (tx + 0.3 * scale, base_y + 3.2 * scale, tz - 0.9 * scale)),
            ((tx, base_y + 2.0 * scale, tz), (tx - 0.4 * scale, base_y + 3.0 * scale, tz + 0.8 * scale)),
        ]
        for (p0, p1) in branch_defs:
            mid = ((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5 + 0.15, (p0[2] + p1[2]) * 0.5)
            bt.add_curved_tube([p0, mid, p1], [0.06 * scale, 0.045 * scale, 0.025 * scale], segs=8)

        # Dense sunlit layered canopy
        canopy_centers = [
            (tx + 0.9 * scale, base_y + 2.9 * scale, tz + 0.4 * scale, 0.85 * scale),
            (tx - 0.8 * scale, base_y + 3.2 * scale, tz - 0.5 * scale, 0.80 * scale),
            (tx + 0.3 * scale, base_y + 3.5 * scale, tz - 0.9 * scale, 0.75 * scale),
            (tx - 0.4 * scale, base_y + 3.3 * scale, tz + 0.8 * scale, 0.78 * scale),
            (tx + 0.1 * scale, base_y + 4.0 * scale, tz + 0.1 * scale, 0.95 * scale),
            (tx + 0.6 * scale, base_y + 4.4 * scale, tz - 0.3 * scale, 0.70 * scale),
            (tx - 0.5 * scale, base_y + 4.3 * scale, tz + 0.3 * scale, 0.68 * scale),
        ]
        bl = ctx.mb("CanopyLeaf_%d" % idx, mats["olive_leaf"])
        blb = ctx.mb("CanopyLeafBright_%d" % idx, mats["olive_leaf_bright"])
        for ci, (cx, cy, cz, cr) in enumerate(canopy_centers):
            target = bl if (ci % 2 == 0) else blb
            target.add_sphere(cx, cy, cz, cr, cr * 0.85, cr, rings=10, segs=14)

    # ---------------- Sun Loungers ----------------
    lounger_specs = [(-5.6, -20.8), (-1.8, -20.8)]
    for li, (lx, lz) in enumerate(lounger_specs):
        bwf = ctx.mb("LoungerFrame_%d" % li, mats["walnut_solid"])
        bcu = ctx.mb("LoungerCushion_%d" % li, mats["boucle"])
        # Frame rails
        bwf.add_box(lx, 0.28, lz - 0.35, 0.70, 0.06, 0.06, uv_tile=1.0)
        bwf.add_box(lx, 0.28, lz + 0.35, 0.70, 0.06, 0.06, uv_tile=1.0)
        bwf.add_box(lx - 0.32, 0.28, lz, 0.06, 0.06, 0.76, uv_tile=1.0)
        bwf.add_box(lx + 0.32, 0.28, lz, 0.06, 0.06, 0.76, uv_tile=1.0)
        # Legs
        for dx in (-0.30, 0.30):
            for dz in (-0.32, 0.32):
                bwf.add_box(lx + dx, 0.14, lz + dz, 0.05, 0.28, 0.05, uv_tile=1.0)
        # Cushion
        bcu.add_rounded_box(lx, 0.36, lz, 0.62, 0.10, 0.72, bevel=0.04, uv_tile=1.0)
        # Backrest cushion (angled)
        bcu.add_rounded_box(lx, 0.52, lz - 0.42, 0.62, 0.10, 0.40, bevel=0.04, uv_tile=1.0)

    # ---------------- Travertine Pedestal Drink Table ----------------
    btbl = ctx.mb("DrinkTable", mats["travertine"])
    btbl.add_cylinder(-3.7, 0.0, -20.8, 0.22, 0.18, 0.50, segs=20)
    btbl.add_cylinder(-3.7, 0.50, -20.8, 0.30, 0.30, 0.05, segs=24)

    # ---------------- Curved Panoramic Sky Cyclorama ----------------
    sky = ctx.mb("SkyCyclorama", mats["sky_sunny"])
    R = 42.0
    cz = -4.0
    y_bot = -14.0
    y_top = 24.0
    theta_min = -2.53
    theta_max = 2.53
    segs = 48
    for i in range(segs):
        t0 = theta_min + (theta_max - theta_min) * (i / segs)
        t1 = theta_min + (theta_max - theta_min) * ((i + 1) / segs)
        x0 = R * math.sin(t0)
        z0 = cz - R * math.cos(t0)
        x1 = R * math.sin(t1)
        z1 = cz - R * math.cos(t1)
        u0 = i / segs
        u1 = (i + 1) / segs
        # Inward-facing CCW winding with continuous [0..1] horizontal U across the entire arc
        p0 = (x0, y_bot, z0)
        p1 = (x1, y_bot, z1)
        p2 = (x1, y_top, z1)
        p3 = (x0, y_top, z0)
        sky.add_tri_raw(p0, p1, p2, (u0, 0.0), (u1, 0.0), (u1, 1.0))
        sky.add_tri_raw(p0, p2, p3, (u0, 0.0), (u1, 1.0), (u0, 1.0))
