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

    # Hearth wall with real recessed 4.50m x 1.16m open firebox (Z = -4.05..0.45, Y = 1.50..2.66)
    b = ctx.mb("FireplaceBreast", mats["verde_alpi"])
    b.add_rounded_box(14.18, 5.68, -1.80, 0.85, 6.04, 10.00, bevel=0.04, uv_tile=0.0)
    b.add_rounded_box(14.18, 2.08, -5.425, 0.85, 1.16, 2.75, bevel=0.03, uv_tile=0.0)
    b.add_rounded_box(14.18, 2.08, 1.825, 0.85, 1.16, 2.75, bevel=0.03, uv_tile=0.0)

    # Recessed 5-wall dark firebrick firebox behind the opening (X = 13.76..14.50)
    b = ctx.mb("FireboxRecess", mats["charcoal"])
    b.add_box(14.48, 2.08, -1.80, 0.08, 1.24, 4.60)
    b.add_box(14.13, 2.68, -1.80, 0.74, 0.06, 4.60)
    b.add_box(14.13, 1.49, -1.80, 0.74, 0.06, 4.60)
    b.add_box(14.13, 2.08, -4.08, 0.74, 1.20, 0.06)
    b.add_box(14.13, 2.08, 0.48, 0.74, 1.20, 0.06)

    bm = ctx.mb("FireplaceMantel", mats["travertine"])
    bm.add_box(13.72, 2.72, -1.80, 0.14, 0.14, 4.90)
    bm.add_box(13.72, 1.45, -1.80, 0.14, 0.12, 4.90)
    bm.add_box(13.72, 2.08, -4.14, 0.14, 1.18, 0.18)
    bm.add_box(13.72, 2.08, 0.54, 0.14, 1.18, 0.18)

    bf = ctx.mb("FireplaceSurround", mats["brass"])
    bf.add_box(13.75, 2.66, -1.80, 0.05, 0.035, 4.56)
    bf.add_box(13.75, 1.50, -1.80, 0.05, 0.035, 4.56)
    bf.add_box(13.75, 2.08, -4.06, 0.05, 1.16, 0.035)
    bf.add_box(13.75, 2.08, 0.46, 0.05, 1.16, 0.035)

    # embers + logs recessed inside open firebox chamber (X = 14.02..14.05, flames at X = 13.92)
    b = ctx.mb("FireplaceEmbers", mats["fire_ember"])
    b.add_box(14.05, 1.56, -1.80, 0.46, 0.06, 4.05)
    for i in range(9):
        z = -3.45 + i * 0.41
        b.add_sphere(14.03 + ((i % 2) * 0.04 - 0.02), 1.61, z, 0.14, 0.08, 0.14, rings=8, segs=12)

    b = ctx.mb("FireplaceLogs", mats["charred_bark"])
    for i in range(6):
        z = -3.35 + i * 0.62
        b.add_cylinder(14.02, 1.71, z - 0.35, 0.065, 0.058, 0.82, segs=10, rot_x=1.5708)

    # ------------------------------------------------------------------ #
    # 2. HI-FI TOWERS (Harman smoked-glass acoustic towers) on MediaHearth ends (Y=1.50, clear of portals!)
    # ------------------------------------------------------------------ #
    hy = 1.50
    for tz in (-6.05, 2.45):
        pl = ctx.mb("HiFiPlinth", mats["glass_smoke"])
        pl.add_box(13.28, hy + 0.04, tz, 0.78, 0.08, 0.78)
        b = ctx.mb("HiFiTower", mats["charcoal"])
        b.add_cylinder(13.28, hy + 0.14, tz, 0.34, 0.28, 2.08, segs=24)
        rb = ctx.mb("HiFiRibs", mats["rift_oak"])
        for side in (-1, 1):
            for k in range(5):
                ang = side * (0.35 + k * 0.20)
                rb.add_box(13.28 + math.cos(ang) * 0.30, hy + 1.18, tz + math.sin(ang) * 0.30, 0.03, 1.92, 0.03)
        dm = ctx.mb("HiFiGlassDome", mats["glass_smoke"])
        dm.add_lathe(13.28, hy + 2.22, tz, [(0.27, 0.0), (0.29, 0.30), (0.24, 0.70), (0.0, 1.13)], segs=24)
        b = ctx.mb("HiFiHaloRing", mats["warm_led"])
        b.add_cylinder(13.28, hy + 2.34, tz, 0.26, 0.26, 0.024, segs=28, cap_top=False, cap_bot=False)

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
    # 4. ARC FLOOR LAMP — old-money sculptural, beside U-sofa NW reading corner
    # ------------------------------------------------------------------ #
    bx, bz = -6.10, -7.20

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
        [(bx, 3.55, bz), (-5.45, 3.64, -6.55), (-4.85, 3.56, -5.95)],
        [0.045, 0.040, 0.035], segs=10)
    # counterweight sphere
    b = ctx.mb("ArcLampCounterweight", mats["brass"])
    b.add_sphere(-6.35, 3.90, -7.45, 0.11, 0.11, 0.11, rings=12, segs=18)

    # pleated Belgian-linen drum shade (open bottom)
    b = ctx.mb("ArcLampShade", mats["cream_pillow"])
    b.add_cylinder(-4.85, 3.56, -5.95, 0.46, 0.40, 0.48, segs=32,
                   cap_top=True, cap_bot=False)
    # spun-brass trim rings
    b = ctx.mb("ArcLampShadeTrim", mats["brass"])
    b.add_cylinder(-4.85, 3.56, -5.95, 0.465, 0.465, 0.025, segs=32)
    b.add_cylinder(-4.85, 4.015, -5.95, 0.405, 0.405, 0.025, segs=32)

    # warm bulb nestled inside
    b = ctx.mb("ArcLampBulb", mats["warm_bulb"])
    b.add_sphere(-4.85, 3.68, -5.95, 0.11, 0.11, 0.11, rings=10, segs=16)
