"""West mountain vista: 3-layer Mediterranean-Alpine landscape west of penthouse."""

import math


def _ridge_dome(b, cx, cz, rx, rz, peak, base_y=-9.0, rings=12, segs=36, seed=0.4):
    """Smooth undulating ridge anchored at base_y, rising naturally to peak."""
    for ri in range(rings):
        t0 = ri / rings
        t1 = (ri + 1) / rings
        y0_base = base_y + (peak - base_y) * math.sin(t0 * math.pi * 0.5)
        y1_base = base_y + (peak - base_y) * math.sin(t1 * math.pi * 0.5)
        r0 = rx * math.cos(t0 * math.pi * 0.5)
        r1 = rx * math.cos(t1 * math.pi * 0.5)
        rz0 = rz * math.cos(t0 * math.pi * 0.5)
        rz1 = rz * math.cos(t1 * math.pi * 0.5)
        for si in range(segs):
            a0 = 2.0 * math.pi * si / segs
            a1 = 2.0 * math.pi * (si + 1) / segs
            mod0 = 1.0 + 0.14 * math.sin(3.0 * a0 + seed) * (1.0 - t0 * 0.5)
            mod1 = 1.0 + 0.14 * math.sin(3.0 * a1 + seed) * (1.0 - t0 * 0.5)
            y0a = base_y + (y0_base - base_y) * (0.94 + 0.06 * math.cos(2.0 * a0 + seed))
            y0b = base_y + (y0_base - base_y) * (0.94 + 0.06 * math.cos(2.0 * a1 + seed))
            y1a = base_y + (y1_base - base_y) * (0.94 + 0.06 * math.cos(2.0 * a0 + seed))
            y1b = base_y + (y1_base - base_y) * (0.94 + 0.06 * math.cos(2.0 * a1 + seed))
            p0 = (cx + r0 * mod0 * math.cos(a0), y0a, cz + rz0 * mod0 * math.sin(a0))
            p1 = (cx + r0 * mod1 * math.cos(a1), y0b, cz + rz0 * mod1 * math.sin(a1))
            p2 = (cx + r1 * mod1 * math.cos(a1), y1b, cz + rz1 * mod1 * math.sin(a1))
            p3 = (cx + r1 * mod0 * math.cos(a0), y1a, cz + rz1 * mod0 * math.sin(a0))
            b.add_quad(p0, p1, p2, p3, uv_scale=(2.0, 2.0))


def _cypress(b_trunk, b_leaf, b_leaf_b, cx, cz, h, r):
    b_trunk.add_cylinder(cx, -0.25, cz, r * 0.28, r * 0.18, h * 0.55, segs=8)
    for i in range(6):
        t = i / 5.0
        y = -0.25 + h * (0.28 + t * 0.58)
        rr = r * (0.85 - 0.52 * (t ** 1.3))
        dx = 0.06 * math.sin(i * 2.1)
        dz = 0.06 * math.cos(i * 1.7)
        target = b_leaf if i % 2 == 0 else b_leaf_b
        target.add_sphere(cx + dx, y, cz + dz, rr, rr * 1.85, rr, rings=8, segs=12)


def _umbrella_pine(b_trunk, b_leaf, b_leaf_b, cx, cz, h, r):
    b_trunk.add_cylinder(cx, -0.25, cz, r * 0.34, r * 0.22, h * 0.72, segs=8)
    for k, (dx, dy, dz, sx, sy) in enumerate((
        (0.0, h * 0.78, 0.0, r * 1.55, r * 0.48),
        (r * 0.55, h * 0.84, -r * 0.40, r * 1.05, r * 0.38),
        (-r * 0.48, h * 0.74, r * 0.45, r * 1.12, r * 0.40),
    )):
        target = b_leaf if k % 2 == 0 else b_leaf_b
        target.add_sphere(cx + dx, -0.25 + dy, cz + dz, sx, sy, sx, rings=8, segs=14)


def build_west_mountain_vista(ctx, mats):
    # ---------- Layer 1: Foreground Herbal Garden Terrace (south of ocean terrace Z=-14.0) ----------
    b = ctx.mb("WestGardenTerrace", mats["travertine"])
    b.add_box(-19.0, -0.25, -6.5, 7.4, 0.7, 15.0, uv_tile=2.0)

    b = ctx.mb("WestGardenParapet", mats["headland_rock"])
    b.add_box(-22.8, 0.35, -6.5, 0.65, 0.95, 15.4, uv_tile=1.5)

    b = ctx.mb("WestGardenBollards", mats["bronze_dark"])
    for z in (-13.0, -7.5, -1.5):
        b.add_cylinder(-21.5, 0.35, z, 0.09, 0.09, 0.85, segs=10)
    b = ctx.mb("WestGardenBollardGlow", mats["warm_bulb"])
    for z in (-13.0, -7.5, -1.5):
        b.add_sphere(-21.5, 1.28, z, 0.11, 0.11, 0.11, rings=8, segs=10)

    b_trunk = ctx.mb("WestGardenPineTrunks", mats["bark"])
    b_leaf = ctx.mb("WestGardenPines", mats["olive_leaf"])
    b_leaf_b = ctx.mb("WestGardenPinesBright", mats["olive_leaf_bright"])
    _cypress(b_trunk, b_leaf, b_leaf_b, -25.2, -18.0, 5.2, 0.55)
    _cypress(b_trunk, b_leaf, b_leaf_b, -26.4, -12.5, 4.6, 0.50)
    _cypress(b_trunk, b_leaf, b_leaf_b, -24.8, -6.0, 5.6, 0.60)
    _umbrella_pine(b_trunk, b_leaf, b_leaf_b, -26.8, 0.5, 4.8, 0.90)
    _umbrella_pine(b_trunk, b_leaf, b_leaf_b, -24.2, 3.2, 4.2, 0.80)
    _cypress(b_trunk, b_leaf, b_leaf_b, -27.0, -3.5, 5.0, 0.52)

    # ---------- Layer 2: Mid-Ground Pine Forested Slopes ----------
    b = ctx.mb("WestMidMountainSlope", mats["coastal_pine"])
    _ridge_dome(b, -44.0, -22.0, 16.0, 20.0, 8.5, rings=8, segs=22)
    _ridge_dome(b, -52.0, 4.0, 18.0, 22.0, 12.0, rings=8, segs=22)
    _ridge_dome(b, -66.0, -10.0, 20.0, 24.0, 14.8, rings=8, segs=22)

    # ---------- Layer 3: Far Alpine-Coastal Horizon Range ----------
    b = ctx.mb("WestFarMountainRange", mats["far_mist_mountain"])
    segs = 40
    z0, z1 = -98.0, 56.0
    x = -118.0
    base_y = -9.0
    for i in range(segs):
        za = z0 + (z1 - z0) * i / segs
        zb = z0 + (z1 - z0) * (i + 1) / segs
        ta = i / segs
        tb = (i + 1) / segs
        ya = base_y + (17.5 + 8.0 * (0.5 + 0.5 * math.cos(ta * math.pi * 6.0))) * (0.6 + 0.4 * math.sin(ta * math.pi * 2.0))
        yb = base_y + (17.5 + 8.0 * (0.5 + 0.5 * math.cos(tb * math.pi * 6.0))) * (0.6 + 0.4 * math.sin(tb * math.pi * 2.0))
        b.add_quad((x, base_y, za), (x, ya, za), (x, yb, zb), (x, base_y, zb), uv_scale=(1.0, 1.0))
