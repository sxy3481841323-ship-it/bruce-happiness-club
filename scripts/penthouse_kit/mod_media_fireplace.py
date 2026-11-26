# scripts/penthouse_kit/mod_media_fireplace.py
"""1F Right Marble & Walnut Feature Wall media / fireplace module.

Adds a floating travertine + fluted-walnut hearth console with a linear
fireplace, a gallery-framed TV screen, a pair of walnut/brass hi-fi towers,
and a champagne-gold arched floor lamp.
"""

import math


def build_media_fireplace(ctx, mats):
    # ------------------------------------------------------------------
    # 1. MediaHearth  -- floating console
    # ------------------------------------------------------------------
    b = ctx.mb("MediaHearth", mats["travertine"])

    # Console body extents
    x0, x1 = 12.3, 14.3
    z0, z1 = -6.8, 3.2
    y0, y1 = 0.38, 1.50
    cx = (x0 + x1) * 0.5
    cz = (z0 + z1) * 0.5
    sx = x1 - x0
    sz = z1 - z0

    # Thick beveled Roman travertine slab top
    top_h = 0.14
    b.add_rounded_box(cx, y1 - top_h * 0.5, cz,
                      sx + 0.06, top_h, sz + 0.06,
                      bevel=0.05, uv_tile=0.0)

    # Travertine carcass (recessed 0.06 behind the fluted walnut drawer fronts to eliminate z-fighting)
    body_h = (y1 - top_h) - (y0 + 0.10)
    body_cy = (y0 + 0.10) + body_h * 0.5
    b.add_box(cx + 0.04, body_cy, cz, sx - 0.12, body_h, sz - 0.04, uv_tile=0.0)

    # Champagne-brass recessed plinth
    bb = ctx.mb("MediaHearth", mats["brass"])
    plinth_h = 0.10
    bb.add_box(cx, y0 + plinth_h * 0.5, cz,
               sx - 0.30, plinth_h, sz - 0.30, uv_tile=0.0)

    # Fluted walnut drawer fronts (a row of vertical flutes on the -X face)
    bw = ctx.mb("MediaHearth", mats["walnut_fluted"])
    face_x = x0 + 0.02
    flute_depth = 0.05
    flute_h = body_h - 0.06
    flute_cy = body_cy
    n_flutes = 46
    flute_w = (sz - 0.20) / n_flutes
    for i in range(n_flutes):
        fz = z0 + 0.10 + flute_w * (i + 0.5)
        bw.add_box(face_x + flute_depth * 0.5, flute_cy, fz,
                   flute_depth, flute_h, flute_w * 0.72, uv_tile=0.0)

    # Thin brass reveal line between drawer banks
    bb.add_box(face_x + flute_depth * 0.5, flute_cy, cz,
               flute_depth + 0.01, 0.012, sz - 0.20, uv_tile=0.0)

    # ------------------------------------------------------------------
    # 1b. FireplaceGlow -- recessed linear firebox
    # ------------------------------------------------------------------
    fg = ctx.mb("FireplaceGlow", mats["fireplace_glow"])
    fx, fy, fz = 14.18, 1.95, -1.8
    fsx, fsy, fsz = 0.18, 0.36, 4.6
    fg.add_box(fx, fy, fz, fsx, fsy, fsz, uv_tile=0.0)

    # Brushed brass frame around the firebox
    bf = ctx.mb("FireplaceGlow", mats["brass"])
    frame_t = 0.06
    frame_d = 0.10
    # top & bottom rails
    bf.add_box(fx, fy + fsy * 0.5 + frame_t * 0.5, fz,
               frame_d, frame_t, fsz + frame_t * 2.0, uv_tile=0.0)
    bf.add_box(fx, fy - fsy * 0.5 - frame_t * 0.5, fz,
               frame_d, frame_t, fsz + frame_t * 2.0, uv_tile=0.0)
    # left & right stiles
    bf.add_box(fx, fy, fz - fsz * 0.5 - frame_t * 0.5,
               frame_d, fsy, frame_t, uv_tile=0.0)
    bf.add_box(fx, fy, fz + fsz * 0.5 + frame_t * 0.5,
               frame_d, fsy, frame_t, uv_tile=0.0)

    # ------------------------------------------------------------------
    # 2. GalleryTVScreen -- painting quad facing -X
    # ------------------------------------------------------------------
    tv = ctx.mb("GalleryTVScreen", mats["tv_art"])
    p0 = (14.10, 3.35, -5.0)
    p1 = (14.10, 3.35, 1.4)
    p2 = (14.10, 6.95, 1.4)
    p3 = (14.10, 6.95, -5.0)
    tv.add_quad(p0, p1, p2, p3, uv_scale=(1.0, 1.0))

    # Ultra-thin champagne-brass gallery picture frame at X = 14.16
    gb = ctx.mb("GalleryTVBezel", mats["brass"])
    bx = 14.16
    bz0, bz1 = -5.0, 1.4
    by0, by1 = 3.35, 6.95
    bcz = (bz0 + bz1) * 0.5
    bcy = (by0 + by1) * 0.5
    bsz = bz1 - bz0
    bsy = by1 - by0
    rail = 0.07
    depth = 0.05
    # top / bottom
    gb.add_box(bx, by1 + rail * 0.5, bcz, depth, rail, bsz + rail * 2.0, uv_tile=0.0)
    gb.add_box(bx, by0 - rail * 0.5, bcz, depth, rail, bsz + rail * 2.0, uv_tile=0.0)
    # left / right
    gb.add_box(bx, bcy, bz0 - rail * 0.5, depth, bsy, rail, uv_tile=0.0)
    gb.add_box(bx, bcy, bz1 + rail * 0.5, depth, bsy, rail, uv_tile=0.0)

    # ------------------------------------------------------------------
    # 3. Pair of walnut & brass hi-fi acoustic towers
    # ------------------------------------------------------------------
    for tz in (-6.0, 2.4):
        tx = 13.4
        tw = 0.42          # width along X
        td = 0.42          # depth along Z
        th = 3.45          # height
        # Walnut cabinet
        tw_b = ctx.mb("HiFiTower", mats["walnut_fluted"])
        tw_b.add_rounded_box(tx, th * 0.5, tz, tw, th, td,
                             bevel=0.03, uv_tile=0.0)
        # Brass tweeter ring (front face toward -X)
        tb = ctx.mb("HiFiTower", mats["brass"])
        ring_x = tx - tw * 0.5 - 0.01
        tb.add_cylinder(ring_x, 2.55, tz, 0.11, 0.11, 0.03,
                        segs=20, rot_z=math.pi * 0.5,
                        cap_top=True, cap_bot=True)
        # Brass mid-woofer ring
        tb.add_cylinder(ring_x, 1.55, tz, 0.15, 0.15, 0.03,
                        segs=22, rot_z=math.pi * 0.5,
                        cap_top=True, cap_bot=True)
        # Brass base plinth
        tb.add_box(tx, 0.04, tz, tw + 0.04, 0.08, td + 0.04, uv_tile=0.0)

    # ------------------------------------------------------------------
    # 4. Champagne-gold arched floor lamp
    # ------------------------------------------------------------------
    base_x, base_z = 12.6, 4.6
    # Heavy Roman travertine cylindrical base
    lb = ctx.mb("ArcLampBase", mats["travertine"])
    lb.add_cylinder(base_x, 0.0, base_z, 0.30, 0.26, 0.22,
                    segs=24, cap_top=True, cap_bot=True)

    # Sweeping brass arch tube
    la = ctx.mb("ArcLampArch", mats["brass"])
    spine = [
        (base_x, 0.22, base_z),
        (base_x, 1.60, base_z),
        (base_x - 0.10, 3.20, base_z - 0.10),
        (base_x - 0.55, 4.60, base_z - 0.55),
        (base_x - 1.20, 5.70, base_z - 1.10),
        (base_x - 1.75, 6.15, base_z - 1.55),
        (base_x - 2.00, 6.20, base_z - 1.80),
        (10.6, 5.90, 2.8),
        (10.6, 5.55, 2.8),
    ]
    radii = [0.045, 0.042, 0.040, 0.038, 0.036, 0.034, 0.032, 0.030, 0.028]
    la.add_curved_tube(spine, radii, segs=10)

    # Hanging warm-brass dome shade
    ls = ctx.mb("ArcLampShade", mats["brass"])
    dome_profile = [
        (0.02, 0.00),
        (0.10, -0.02),
        (0.18, -0.06),
        (0.24, -0.14),
        (0.27, -0.24),
        (0.28, -0.34),
        (0.26, -0.42),
    ]
    ls.add_lathe(10.6, 5.30, 2.8, dome_profile, segs=24)

    # Glowing opal bulb
    bulb = ctx.mb("ArcLampBulb", mats["warm_bulb"])
    bulb.add_sphere(10.6, 4.95, 2.8, 0.11, 0.13, 0.11, rings=12, segs=18)
