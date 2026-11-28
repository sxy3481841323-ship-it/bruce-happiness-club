"""Penthouse kit — media wall, fireplace, hi-fi towers, gallery display, arc lamp."""

import math


def build_media_fireplace(ctx, mats):
    # ------------------------------------------------------------------ #
    # 1. FIREPLACE — Calacatta chimney breast & elevated hearth (Y 0.38..1.50, firebox Y 1.54..2.52)
    # ------------------------------------------------------------------ #
    b = ctx.mb("MediaHearth", mats["travertine"])
    b.add_rounded_box(13.30, 1.44, -1.80, 2.05, 0.12, 10.00, bevel=0.05, uv_tile=1.4)
    b.add_box(13.30, 0.90, -1.80, 1.90, 0.96, 9.80, uv_tile=1.4)
    bp = ctx.mb("MediaHearthPlinth", mats["brass"])
    bp.add_box(13.30, 0.40, -1.80, 1.94, 0.04, 9.84)
    bp.add_box(13.30, 1.365, -1.80, 1.98, 0.015, 9.92)

    b = ctx.mb("FireplaceBreast", mats["verde_alpi"])
    b.add_rounded_box(14.18, 5.10, -1.80, 0.85, 7.20, 10.00, bevel=0.04, uv_tile=0.0)

    # firebox recess at Y = 1.54..2.52 (recessed cleanly behind animated flames X=13.78 so 0 Z-fighting!)
    b = ctx.mb("FireboxRecess", mats["charcoal"])
    b.add_box(14.14, 2.03, -1.80, 0.68, 0.98, 4.40)
    bf = ctx.mb("FireplaceSurround", mats["brass"])
    bf.add_box(13.70, 2.54, -1.80, 0.10, 0.06, 4.54)
    bf.add_box(13.70, 1.52, -1.80, 0.10, 0.06, 4.54)

    # embers + logs (X = 13.98, separated cleanly from animated flame ribbons X = 13.76)
    b = ctx.mb("FireplaceEmbers", mats["fire_ember"])
    b.add_box(14.00, 1.62, -1.80, 0.44, 0.05, 4.00)
    for i in range(9):
        z = -3.45 + i * 0.41
        b.add_sphere(13.98 + ((i % 2) * 0.04 - 0.02), 1.66, z, 0.14, 0.08, 0.14, rings=8, segs=12)

    b = ctx.mb("FireplaceLogs", mats["charred_bark"])
    for i in range(6):
        z = -3.35 + i * 0.62
        b.add_cylinder(13.98, 1.76, z - 0.35, 0.065, 0.058, 0.82, segs=10, rot_x=1.5708)

    # ------------------------------------------------------------------ #
    # 2. HI-FI TOWERS (Harman smoked-glass acoustic towers) at tower_x=13.05
    # ------------------------------------------------------------------ #
    for tz in (-7.35, 3.75):
        pl = ctx.mb("HiFiPlinth", mats["glass_smoke"])
        pl.add_box(13.05, 0.04, tz, 0.78, 0.08, 0.78)
        b = ctx.mb("HiFiTower", mats["charcoal"])
        b.add_cylinder(13.05, 0.14, tz, 0.34, 0.28, 2.08, segs=24)
        rb = ctx.mb("HiFiRibs", mats["rift_oak"])
        for side in (-1, 1):
            for k in range(5):
                ang = side * (0.35 + k * 0.20)
                rb.add_box(13.05 + math.cos(ang) * 0.30, 1.18, tz + math.sin(ang) * 0.30, 0.03, 1.92, 0.03)
        dm = ctx.mb("HiFiGlassDome", mats["glass_smoke"])
        dm.add_lathe(13.05, 2.22, tz, [(0.27, 0.0), (0.29, 0.30), (0.24, 0.70), (0.0, 1.13)], segs=24)
        b = ctx.mb("HiFiHaloRing", mats["warm_led"])
        b.add_cylinder(13.05, 2.34, tz, 0.26, 0.26, 0.024, segs=28, cap_top=False, cap_bot=False)

    # ------------------------------------------------------------------ #
    # 3. GALLERY DISPLAY — 16:9 screen proud in front of marble breast at X=13.66 (-X normal)
    # ------------------------------------------------------------------ #
    b = ctx.mb("GalleryTVScreen", mats["tv_art"])
    b.add_quad((13.66, 3.45, -4.90), (13.66, 3.45, 1.30),
               (13.66, 6.93, 1.30), (13.66, 6.93, -4.90),
               uv_scale=(1.0, 1.0), flip=False)

    # recessed dark bronze chassis proud of FireplaceBreast face (X=13.755)
    b = ctx.mb("GalleryTVBezel", mats["bronze_dark"])
    b.add_box(13.72, 5.19, -1.80, 0.08, 3.64, 6.36)
    # inner brass fillet
    b = ctx.mb("GalleryTVFillet", mats["brass"])
    b.add_box(13.675, 5.19, -1.80, 0.02, 3.52, 6.24)

    # sculptural oak-and-brass acoustic louver soundbar wing
    b = ctx.mb("GallerySoundbarSpine", mats["brass"])
    b.add_box(13.70, 3.10, -1.80, 0.06, 0.48, 5.60)
    b = ctx.mb("GallerySoundbarSlats", mats["walnut_solid"])
    for i in range(24):
        z = -4.60 + i * (5.60 / 23.0)
        b.add_box(13.66, 3.10, z, 0.08, 0.44, 0.055)

    # ------------------------------------------------------------------ #
    # 4. ARC FLOOR LAMP — old-money sculptural, beside right Harman tower
    # ------------------------------------------------------------------ #
    bx, bz = 12.25, 5.20

    # stepped heavy plinth
    b = ctx.mb("ArcLampBase", mats["travertine"])
    b.add_cylinder(bx, 0.00, bz, 0.34, 0.34, 0.22, segs=28)
    b = ctx.mb("ArcLampCollar", mats["bronze_dark"])
    b.add_cylinder(bx, 0.22, bz, 0.30, 0.26, 0.10, segs=28)
    b = ctx.mb("ArcLampCollarBrass", mats["brass"])
    b.add_cylinder(bx, 0.32, bz, 0.24, 0.22, 0.06, segs=28)

    # fluted walnut column with brass rings
    b = ctx.mb("ArcLampArch", mats["walnut_solid"])
    b.add_cylinder(bx, 0.38, bz, 0.055, 0.055, 3.17, segs=20)
    b = ctx.mb("ArcLampRings", mats["brass"])
    for ry in (0.55, 1.40, 2.25, 3.10):
        b.add_cylinder(bx, ry, bz, 0.075, 0.075, 0.04, segs=20)

    # machined brass cantilever arm to shade center
    b = ctx.mb("ArcLampArm", mats["brass"])
    b.add_curved_tube(
        [(bx, 3.55, bz), (12.05, 3.62, 4.95), (11.75, 3.56, 4.70)],
        [0.045, 0.040, 0.035], segs=10)
    # counterweight sphere
    b = ctx.mb("ArcLampCounterweight", mats["brass"])
    b.add_sphere(12.50, 3.90, 5.45, 0.11, 0.11, 0.11, rings=12, segs=18)

    # pleated Belgian-linen drum shade (open bottom)
    b = ctx.mb("ArcLampShade", mats["cream_pillow"])
    b.add_cylinder(11.75, 3.56, 4.70, 0.46, 0.40, 0.48, segs=32,
                   cap_top=True, cap_bot=False)
    # spun-brass trim rings
    b = ctx.mb("ArcLampShadeTrim", mats["brass"])
    b.add_cylinder(11.75, 3.56, 4.70, 0.465, 0.465, 0.025, segs=32)
    b.add_cylinder(11.75, 4.015, 4.70, 0.405, 0.405, 0.025, segs=32)

    # warm bulb nestled inside
    b = ctx.mb("ArcLampBulb", mats["warm_bulb"])
    b.add_sphere(11.75, 3.68, 4.70, 0.11, 0.11, 0.11, rings=10, segs=16)
