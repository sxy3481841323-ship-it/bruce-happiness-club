"""South terrace courtyard and alpine crag mountain range."""

import math


def _crag_range(b, x_min, x_max, z_front, z_peak, z_back, nx, peak_fn):
    """Build a faceted 3-layer triangulated mountain ridge mesh."""
    z_foothill = z_front + (z_peak - z_front) * 0.42
    z_shoulder = z_peak + (z_back - z_peak) * 0.35
    cols = []
    for i in range(nx + 1):
        t = i / float(nx)
        x = x_min + (x_max - x_min) * t
        h = peak_fn(t, x)
        ridge = h * (1.0 - 0.35 * abs(math.sin(t * 23.0 + 1.7)))
        cols.append((x, h, ridge))
    for i in range(nx):
        x0, h0, r0 = cols[i]
        x1, h1, r1 = cols[i + 1]
        # front face: z_front (Y=-9) -> z_foothill (0.42H)
        b.add_quad(
            (x0, -9.0, z_front), (x1, -9.0, z_front),
            (x1, 0.42 * h1, z_foothill), (x0, 0.42 * h0, z_foothill),
            uv_scale=(1.0, 1.0), flip=True,
        )
        # mid face: foothill -> ridge crest
        b.add_quad(
            (x0, 0.42 * h0, z_foothill), (x1, 0.42 * h1, z_foothill),
            (x1, r1, z_peak), (x0, r0, z_peak),
            uv_scale=(1.0, 1.0), flip=True,
        )
        # back face: ridge crest -> shoulder -> z_back (Y=-9)
        b.add_quad(
            (x0, r0, z_peak), (x1, r1, z_peak),
            (x1, 0.55 * h1, z_shoulder), (x0, 0.55 * h0, z_shoulder),
            uv_scale=(1.0, 1.0), flip=True,
        )
        b.add_quad(
            (x0, 0.55 * h0, z_shoulder), (x1, 0.55 * h1, z_shoulder),
            (x1, -9.0, z_back), (x0, -9.0, z_back),
            uv_scale=(1.0, 1.0), flip=True,
        )


def _peak_foothills(t, x):
    return 12.0 + 7.0 * abs(math.sin(t * 9.0 + 0.4)) + 2.5 * math.sin(t * 31.0)


def _peak_granite(t, x):
    base = 22.0 + 14.0 * abs(math.sin(t * 6.0 + 1.1))
    west = 13.0 * math.exp(-((x + 34.0) ** 2) / 320.0)
    east = 11.0 * math.exp(-((x - 42.0) ** 2) / 380.0)
    valley = -12.0 * math.exp(-((x - 1.5) ** 2) / 90.0)
    return base + west + east + valley


def _peak_distant(t, x):
    return 34.0 + 14.0 * abs(math.sin(t * 4.5 + 2.3)) + 3.0 * math.sin(t * 17.0)


def build_south_terrace_and_mountains(ctx, mats):
    # ---- Courtyard deck ----
    b = ctx.mb("SouthCourtyardDeck", mats["tundra_grey"])
    b.add_box(0.0, -0.14, 37.0, 32.8, 0.28, 16.4, uv_tile=3.0)

    # ---- Pool coping ----
    b = ctx.mb("SouthPoolCoping", mats["pietra_grey"])
    b.add_box(5.0, 0.06, 32.85, 15.4, 0.16, 0.30, uv_tile=1.5)
    b.add_box(5.0, 0.06, 41.65, 15.4, 0.16, 0.30, uv_tile=1.5)
    b.add_box(-2.65, 0.06, 37.25, 0.30, 0.16, 8.9, uv_tile=1.5)
    b.add_box(12.65, 0.06, 37.25, 0.30, 0.16, 8.9, uv_tile=1.5)

    # ---- Pool water + cove ----
    b = ctx.mb("SouthPoolWater", mats["pool_water"])
    b.add_box(5.0, 0.05, 37.25, 14.8, 0.06, 8.3, uv_tile=2.0)
    b = ctx.mb("SouthPoolCove", mats["warm_led"])
    b.add_box(5.0, 0.02, 33.15, 14.6, 0.04, 0.10)
    b.add_box(-2.35, 0.02, 37.25, 0.10, 0.04, 8.1)

    # ---- Loungers ----
    b = ctx.mb("SouthPoolLoungers", mats["graphite_slate"])
    for (lx, lz) in ((1.5, 31.2), (5.5, 31.2)):
        b.add_rounded_box(lx, 0.22, lz, 0.9, 0.22, 2.0, bevel=0.05, uv_tile=1.0)
    b = ctx.mb("SouthPoolLoungersB", mats["nordic_slate"])
    for (lx, lz) in ((-5.6, 36.2), (-5.6, 39.2)):
        b.add_rounded_box(lx, 0.22, lz, 0.9, 0.22, 2.0, bevel=0.05, uv_tile=1.0)

    # ---- BBQ pergola ----
    b = ctx.mb("SouthBBQPergola", mats["graphite_slate"])
    for (px, pz) in ((-14.4, 32.0), (-8.8, 32.0), (-14.4, 40.4), (-8.8, 40.4)):
        b.add_box(px, 3.6, pz, 0.22, 7.2, 0.22, uv_tile=1.0)
    b.add_box(-11.6, 7.25, 36.2, 6.4, 0.18, 8.8, uv_tile=2.0)
    for k in range(9):
        b.add_box(-11.6, 7.05, 32.4 + k * 0.95, 6.2, 0.10, 0.18, uv_tile=1.0)

    # ---- BBQ counter + grill ----
    b = ctx.mb("SouthBBQCounter", mats["pietra_grey"])
    b.add_box(-13.4, 1.12, 36.2, 2.0, 2.24, 6.2, uv_tile=1.5)
    b = ctx.mb("SouthBBQGrill", mats["platinum"])
    b.add_box(-13.4, 2.38, 36.2, 1.7, 0.28, 2.4, uv_tile=1.0)
    b.add_box(-13.4, 2.55, 36.2, 1.5, 0.06, 2.2, uv_tile=1.0)

    # ---- Glass balustrade ----
    b = ctx.mb("SouthCourtyardGlass", mats["glass"])
    b.add_box(0.0, 1.1, 44.8, 32.0, 2.2, 0.06, uv_tile=2.0)
    b = ctx.mb("SouthCourtyardRail", mats["platinum"])
    b.add_box(0.0, 2.22, 44.8, 32.0, 0.06, 0.10, uv_tile=2.0)

    # ---- Layer 1: foothills ----
    b = ctx.mb("SouthForestedFoothills", mats["coastal_pine"])
    _crag_range(b, -126.0, 126.0, 50.0, 60.0, 68.0, 44, _peak_foothills)

    # ---- Layer 2: granite massifs ----
    b = ctx.mb("SouthGraniteCrags", mats["alpine_granite"])
    _crag_range(b, -126.0, 126.0, 68.0, 84.0, 96.0, 52, _peak_granite)

    # ---- Layer 3: distant sierra ----
    b = ctx.mb("SouthDistantPeaks", mats["far_mist_mountain"])
    _crag_range(b, -126.0, 126.0, 104.0, 118.0, 132.0, 48, _peak_distant)

    # ---- Courtyard cliff skirt & anchored perimeter pines (no floating cylinders!) ----
    b_skirt = ctx.mb("SouthCourtyardCliffBase", mats["headland_rock"])
    b_skirt.add_box(0.0, -4.64, 37.0, 32.8, 9.0, 16.4, uv_tile=3.0)

    b_tr = ctx.mb("SouthCourtyardFirTrunks", mats["bark"])
    b_lf = ctx.mb("SouthCourtyardFirs", mats["coastal_pine"])
    for fx, fz, sc in ((-15.2, 42.4, 1.1), (-11.8, 43.2, 0.9), (14.2, 34.5, 1.05), (14.4, 41.0, 0.95)):
        b_tr.add_cylinder(fx, -0.2, fz, 0.18 * sc, 0.11 * sc, 2.8 * sc, segs=8)
        for dy, rr in ((2.0, 1.05), (2.9, 0.82), (3.7, 0.56), (4.4, 0.34)):
            b_lf.add_sphere(fx, dy * sc, fz, rr * sc, rr * 1.15 * sc, rr * sc, rings=8, segs=12)
