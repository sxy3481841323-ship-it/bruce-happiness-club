"""Floating cantilevered oak staircase + mezzanine glass/brass balustrade."""

import math


def _lerp(a, b, t):
    return a + (b - a) * t


def build_stair_and_balustrade(ctx, mats):
    oak = mats["oak"]
    brass = mats["brass"]
    led = mats["warm_led"]
    glass = mats["glass"]

    # ------------------------------------------------------------------
    # Stair geometry parameters
    # ------------------------------------------------------------------
    x_center = -9.8
    x_min = -11.4
    x_max = -8.2
    width = 3.2

    z_bottom = 14.2
    z_top = 6.6
    y_bottom = 0.0
    y_top = 9.20

    n_steps = 14
    rise = (y_top - y_bottom) / n_steps          # 0.6571
    run = (z_bottom - z_top) / n_steps           # 0.5428
    tread_thick = 0.24
    tread_depth = 0.85

    # ------------------------------------------------------------------
    # 1. Floating oak treads + LED strips + brass stringers
    # ------------------------------------------------------------------
    b_tread = ctx.mb("stair_treads", oak)
    b_led = ctx.mb("stair_led", led)
    b_stringer = ctx.mb("stair_stringers", brass)

    for i in range(n_steps):
        # top surface of tread i
        y_top_i = y_bottom + rise * (i + 1)
        z_front_i = z_bottom - run * i          # front (lower) edge
        z_center_i = z_front_i - tread_depth * 0.5
        y_center_i = y_top_i - tread_thick * 0.5

        b_tread.add_rounded_box(
            x_center, y_center_i, z_center_i,
            width, tread_thick, tread_depth,
            bevel=0.05, uv_tile=0.0,
        )

        # warm LED strip tucked under front lip
        b_led.add_box(
            x_center, y_top_i - tread_thick - 0.02, z_front_i - 0.06,
            width - 0.30, 0.03, 0.05,
            uv_tile=0.0,
        )

    # Two recessed dark-brass diagonal stringer beams underneath
    # Spine from bottom to top, offset in X to sit under tread edges.
    y0 = y_bottom + rise * 0.5
    z0 = z_bottom - run * 0.5
    y1 = y_top - rise * 0.5
    z1 = z_top + run * 0.5

    dy = y1 - y0
    dz = z1 - z0
    length = math.sqrt(dy * dy + dz * dz)
    angle = math.atan2(dy, -dz)  # rotation about X so beam follows slope

    for sx in (x_min + 0.35, x_max - 0.35):
        # Build a thin beam as a rotated box via add_box with rot_y=0
        # (we approximate slope with a stack of small segments for accuracy)
        segs = 10
        for s in range(segs):
            t0 = s / segs
            t1 = (s + 1) / segs
            ya = _lerp(y0, y1, t0)
            yb = _lerp(y0, y1, t1)
            za = _lerp(z0, z1, t0)
            zb = _lerp(z0, z1, t1)
            cy = (ya + yb) * 0.5 - 0.30
            cz = (za + zb) * 0.5
            seg_len = math.sqrt((yb - ya) ** 2 + (zb - za) ** 2) + 0.02
            # approximate with axis-aligned thin box; slight overlap hides seams
            b_stringer.add_box(
                sx, cy, cz,
                0.14, 0.22, seg_len,
                uv_tile=0.0,
            )

    # ------------------------------------------------------------------
    # 2. Stair side glass guard + angled brass handrail at X = -8.15
    # ------------------------------------------------------------------
    b_glass = ctx.mb("stair_glass", glass)
    b_rail = ctx.mb("stair_handrail", brass)

    x_guard = -8.15
    # glass panel follows slope from (Z=14.0, Y=2.4) to (Z=6.6, Y=11.45)
    gz0, gy0 = 14.0, 2.4
    gz1, gy1 = 6.6, 11.45
    g_segs = 12
    for s in range(g_segs):
        t0 = s / g_segs
        t1 = (s + 1) / g_segs
        za = _lerp(gz0, gz1, t0)
        zb = _lerp(gz0, gz1, t1)
        ya = _lerp(gy0, gy1, t0)
        yb = _lerp(gy0, gy1, t1)
        cy = (ya + yb) * 0.5
        cz = (za + zb) * 0.5
        seg_len = math.sqrt((yb - ya) ** 2 + (zb - za) ** 2) + 0.02
        b_glass.add_box(
            x_guard, cy, cz,
            0.03, 0.90, seg_len,
            uv_tile=0.0,
        )

    # Angled brass handrail (continuous tube approximated by segments)
    r_segs = 16
    for s in range(r_segs):
        t0 = s / r_segs
        t1 = (s + 1) / r_segs
        za = _lerp(gz0, gz1, t0)
        zb = _lerp(gz0, gz1, t1)
        ya = _lerp(gy0, gy1, t0) + 0.95
        yb = _lerp(gy0, gy1, t1) + 0.95
        cy = (ya + yb) * 0.5
        cz = (za + zb) * 0.5
        seg_len = math.sqrt((yb - ya) ** 2 + (zb - za) ** 2) + 0.03
        b_rail.add_box(
            x_guard, cy, cz,
            0.07, 0.07, seg_len,
            uv_tile=0.0,
        )

    # ------------------------------------------------------------------
    # 3. Mezzanine overlook balustrade
    # ------------------------------------------------------------------
    b_mglass = ctx.mb("mezz_glass", glass)
    b_mshoe = ctx.mb("mezz_shoe", brass)
    b_mcap = ctx.mb("mezz_cap", brass)
    b_mstan = ctx.mb("mezz_stanchions", brass)

    y_base = 9.20
    y_cap = 11.45
    glass_h = y_cap - y_base - 0.10

    def _build_run(x0, z0, x1, z1):
        """Build a straight balustrade run from (x0,z0) to (x1,z1)."""
        dx = x1 - x0
        dz = z1 - z0
        length = math.sqrt(dx * dx + dz * dz)
        if length < 1e-4:
            return
        ux = dx / length
        uz = dz / length
        cx = (x0 + x1) * 0.5
        cz = (z0 + z1) * 0.5
        rot_y = math.atan2(dx, dz)

        # base shoe
        b_mshoe.add_box(
            cx, y_base + 0.05, cz,
            0.10, 0.10, length,
            uv_tile=0.0, rot_y=rot_y,
        )
        # glass panel
        b_mglass.add_box(
            cx, y_base + 0.10 + glass_h * 0.5, cz,
            0.03, glass_h, length - 0.06,
            uv_tile=0.0, rot_y=rot_y,
        )
        # top cap rail
        b_mcap.add_box(
            cx, y_cap - 0.04, cz,
            0.12, 0.08, length,
            uv_tile=0.0, rot_y=rot_y,
        )
        # stanchions every ~3.2 units
        n_stan = max(2, int(round(length / 3.2)) + 1)
        for k in range(n_stan):
            t = k / (n_stan - 1)
            sx = _lerp(x0, x1, t)
            sz = _lerp(z0, z1, t)
            b_mstan.add_box(
                sx, y_base + 0.10 + glass_h * 0.5, sz,
                0.06, glass_h, 0.06,
                uv_tile=0.0,
            )

    # East overlook edge: X = -3.42, Z in [-15.8, +6.6]
    _build_run(-3.42, -15.8, -3.42, 6.6)

    # South overlook edge: Z = 6.62, X in [-8.2, -3.42]
    _build_run(-8.2, 6.62, -3.42, 6.62)
