"""Penthouse stair + balustrade kit.

build_stair_and_balustrade(ctx, mats) -> builds:
  * 14 thick rounded oak treads w/ brass nosing + warm LED under-nosing
  * twin TRUE pitched walnut stringers (diagonal prism quads)
  * dual-side pitched glass guards + brass stanchions
  * continuous curved walnut handrails w/ gooseneck ends
  * 2F mezzanine balustrade with WIDE OPEN stair landing
"""

import math


def _lerp(a, b, t):
    return a + (b - a) * t


def _quad_prism(b, p0, p1, p2, p3, depth, axis, uv_scale=(1.0, 1.0)):
    """Extrude a quad (p0..p3) along `axis` ('x'|'y'|'z') by `depth`."""
    def off(p):
        x, y, z = p
        if axis == 'x':
            return (x + depth, y, z)
        if axis == 'y':
            return (x, y + depth, z)
        return (x, y, z + depth)

    q0, q1, q2, q3 = p0, p1, p2, p3
    r0, r1, r2, r3 = off(q0), off(q1), off(q2), off(q3)
    # front / back faces
    b.add_quad(q0, q1, q2, q3, uv_scale=uv_scale)
    b.add_quad(r3, r2, r1, r0, uv_scale=uv_scale)
    # sides
    b.add_quad(q0, r0, r1, q1, uv_scale=uv_scale)
    b.add_quad(q1, r1, r2, q2, uv_scale=uv_scale)
    b.add_quad(q2, r2, r3, q3, uv_scale=uv_scale)
    b.add_quad(q3, r3, r0, q0, uv_scale=uv_scale)


def build_stair_and_balustrade(ctx, mats):
    oak = mats["oak"]
    brass = mats["brass"]
    led = mats["warm_led"]
    walnut = mats["walnut_solid"]
    glass = mats["glass"]

    # ---------------------------------------------------------------- geometry
    x_center = -9.8
    width = 3.20
    x_left = x_center - width * 0.5      # -11.40
    x_right = x_center + width * 0.5     # -8.20

    z_bot, y_bot = 14.2, 0.0
    z_top, y_top = 6.6, 9.20
    n_steps = 14
    rise = (y_top - y_bot) / n_steps     # 0.6571
    run = (z_bot - z_top) / n_steps      # 0.5429

    tread_depth = 0.86
    tread_thick = 0.20

    # ---------------------------------------------------------------- treads
    b_tread = ctx.mb("stair_treads", oak)
    b_brass = ctx.mb("stair_brass", brass)
    b_led = ctx.mb("stair_led", led)

    for i in range(n_steps):
        y = y_bot + rise * (i + 1)
        z = z_bot - run * (i + 1) + tread_depth * 0.5
        b_tread.add_rounded_box(
            x_center, y - tread_thick * 0.5, z,
            width, tread_thick, tread_depth,
            bevel=0.04, uv_tile=0.0,
        )
        # brass front inlay
        b_brass.add_box(
            x_center, y - tread_thick * 0.5, z - tread_depth * 0.5 + 0.02,
            width - 0.10, 0.02, 0.03, uv_tile=0.0,
        )
        # warm LED under-nosing
        b_led.add_box(
            x_center, y - tread_thick - 0.01, z - tread_depth * 0.5 + 0.05,
            width - 0.20, 0.015, 0.02, uv_tile=0.0,
        )

    # ---------------------------------------------------------------- stringers
    b_str = ctx.mb("stair_stringers", walnut)
    # diagonal prism: bottom edge (z=14.1,y=0.05) -> top (z=6.55,y=9.05)
    for sx in (-11.25, -8.35):
        x0 = sx - 0.08
        x1 = sx + 0.08
        zb, yb = 14.1, 0.05
        zt, yt = 6.55, 9.05
        # outer face quad (in Y-Z plane at x0), extruded along X by 0.16
        p0 = (x0, yb, zb)
        p1 = (x0, yt, zt)
        p2 = (x0, yt + 0.24, zt)
        p3 = (x0, yb + 0.24, zb)
        _quad_prism(b_str, p0, p1, p2, p3, 0.16, 'x')

    # ---------------------------------------------------------------- glass guards
    b_glass = ctx.mb("stair_glass", glass)
    b_stanch = ctx.mb("stair_stanchions", brass)

    for gx in (-11.42, -8.18):
        # sloped parallelogram glass panel (double-sided thin prism)
        gb_z, gb_y = 14.0, 0.35
        gt_z, gt_y = 6.62, 9.25
        tb_z, tb_y = 14.0, 1.42
        tt_z, tt_y = 6.62, 10.28
        p0 = (gx, gb_y, gb_z)
        p1 = (gx, gt_y, gt_z)
        p2 = (gx, tt_y, tt_z)
        p3 = (gx, tb_y, tb_z)
        _quad_prism(b_glass, p0, p1, p2, p3, 0.012, 'x')

        # 6 brass stanchions along the slope
        for k in range(6):
            t = k / 5.0
            z = _lerp(gb_z, gt_z, t)
            y0 = _lerp(gb_y, gt_y, t)
            y1 = _lerp(tb_y, tt_y, t)
            h = y1 - y0
            b_stanch.add_cylinder(gx, y0, z, 0.018, 0.018, h, segs=12)

    # ---------------------------------------------------------------- handrails
    b_rail = ctx.mb("stair_handrail", walnut)
    b_brack = ctx.mb("stair_brackets", brass)

    for hx in (-11.42, -8.18):
        spine = [
            (hx, 0.98, 14.35),
            (hx, 1.42, 14.00),
            (hx, 10.28, 6.62),
            (hx, 10.28, 6.10),
        ]
        radii = [0.036] * len(spine)
        b_rail.add_curved_tube(spine, radii, segs=10)

        # brass brackets under rail
        for k in range(6):
            t = k / 5.0
            z = _lerp(14.0, 6.62, t)
            y = _lerp(1.42, 10.28, t)
            b_brack.add_box(hx, y - 0.06, z, 0.05, 0.10, 0.05, uv_tile=0.0)

    # ---------------------------------------------------------------- 2F balustrade
    y_base = 9.20
    y_cap = 10.28
    cap_h = y_cap - y_base

    b_shoe = ctx.mb("bal_shoe", walnut)
    b_bglass = ctx.mb("bal_glass", glass)
    b_bstanch = ctx.mb("bal_stanchions", brass)
    b_bcap = ctx.mb("bal_cap", walnut)

    def _run(x0, x1, z):
        length = x1 - x0
        if length <= 0.01:
            return
        cx = (x0 + x1) * 0.5
        # walnut shoe base
        b_shoe.add_box(cx, y_base + 0.05, z, length, 0.10, 0.10, uv_tile=0.0)
        # glass panel
        b_bglass.add_box(cx, y_base + cap_h * 0.5, z, length - 0.10, cap_h - 0.20, 0.012, uv_tile=0.0)
        # stanchions
        n = max(2, int(length / 1.2) + 1)
        for k in range(n):
            t = k / (n - 1)
            sx = _lerp(x0 + 0.10, x1 - 0.10, t)
            b_bstanch.add_cylinder(sx, y_base + 0.10, z, 0.016, 0.016, cap_h - 0.20, segs=10)
        # continuous cap rail
        b_bcap.add_box(cx, y_cap - 0.03, z, length, 0.06, 0.10, uv_tile=0.0)

    # East overlook
    _run(-3.42, -3.42, -15.8)  # placeholder no-op guard
    # East overlook runs along X = -3.42, Z in [-15.8, 6.62]
    # build as Z-oriented run
    z0, z1 = -15.8, 6.62
    length = z1 - z0
    cz = (z0 + z1) * 0.5
    b_shoe.add_box(-3.42, y_base + 0.05, cz, 0.10, 0.10, length, uv_tile=0.0)
    b_bglass.add_box(-3.42, y_base + cap_h * 0.5, cz, 0.012, cap_h - 0.20, length - 0.10, uv_tile=0.0)
    n = max(2, int(length / 1.2) + 1)
    for k in range(n):
        t = k / (n - 1)
        sz = _lerp(z0 + 0.10, z1 - 0.10, t)
        b_bstanch.add_cylinder(-3.42, y_base + 0.10, sz, 0.016, 0.016, cap_h - 0.20, segs=10)
    b_bcap.add_box(-3.42, y_cap - 0.03, cz, 0.10, 0.06, length, uv_tile=0.0)

    # South overlook — split into two wings leaving stair landing OPEN
    _run(-14.85, -11.45, 6.62)   # left wing
    _run(-8.15, -3.42, 6.62)     # right wing
