"""
Master Architectural Shell for PH·01 Sunlit Two-Floor Penthouse Duplex.
Locks all 4 enclosed walls, double-height ceiling + atrium chandelier,
2F mezzanine slab, panoramic curtain window wall, PH·01 entrance doors,
and 3 modular future expansion portals.
"""

import math


def build_arch_shell(ctx, mats: dict):
    b_floor = ctx.mb("FloorOak", mats["oak"])
    b_wall = ctx.mb("PlasterWalls", mats["plaster"])
    b_marble = ctx.mb("MarbleArchitecture", mats["marble"])
    b_walnut = ctx.mb("WalnutFlutedPanels", mats["walnut_fluted"])
    b_walnut_solid = ctx.mb("WalnutSolidTrim", mats["walnut_solid"])
    b_brass = ctx.mb("BrassArchitecture", mats["brass"])
    b_bronze = ctx.mb("StudioBronzeMullions", mats["bronze_dark"])
    b_linen = ctx.mb("SheerLinenDrapery", mats["sheer_linen"])
    b_led = ctx.mb("WarmCoveLED", mats["warm_led"])
    b_glass = ctx.mb("ClearCurtainGlass", mats["glass"])
    b_frosted = ctx.mb("FrostedPortalGlass", mats["frosted_glass"])

    # 1. 1F Main Floor Slab (Y top = 0.00, X in [-15.2, 15.2], Z in [-16.2, 15.8])
    b_floor.add_box(0.0, -0.25, -0.2, 30.4, 0.50, 32.0, uv_tile=5.2)

    # 2. Double-Height Ceiling (Y bottom = 18.60) + Recessed Cove Ceiling Coffer
    b_wall.add_box(0.0, 18.90, -0.2, 30.4, 0.60, 32.0, uv_tile=8.0)
    # Dropped perimeter soffit ring for hidden warm LED cove lighting
    b_wall.add_box(0.0, 18.42, 13.8, 30.0, 0.36, 3.6, uv_tile=6.0)
    b_wall.add_box(13.6, 18.42, -0.2, 2.8, 0.36, 31.6, uv_tile=6.0)
    b_wall.add_box(-13.6, 18.42, -0.2, 2.8, 0.36, 31.6, uv_tile=6.0)
    b_wall.add_box(0.0, 18.42, -14.4, 30.0, 0.36, 3.2, uv_tile=6.0)
    # Warm LED cove ribbons
    b_led.add_box(0.0, 18.54, -12.82, 24.4, 0.10, 0.14)
    b_led.add_box(12.22, 18.54, -0.2, 0.14, 0.10, 25.4)
    b_led.add_box(-12.22, 18.54, -0.2, 0.14, 0.10, 25.4)

    # Sculptural Atrium Brass & Opal-Globe Chandelier at (2.6, 18.6 -> 13.4, -2.8)
    cx, cz = 2.6, -2.8
    b_brass.add_cylinder(cx, 18.10, cz, 0.65, 0.65, 0.12, segs=24)
    for rx, rz in [(-0.22, -0.15), (0.22, 0.15)]:
        b_brass.add_cylinder(cx + rx, 14.35, cz + rz, 0.025, 0.025, 3.80, segs=8)
    # Two sweeping brass rings
    for r_ring, y_ring, n_globes in [(2.15, 14.45, 8), (1.35, 13.65, 6)]:
        pts = []
        segs = 28
        for i in range(segs + 1):
            a = (i / segs) * math.tau
            pts.append((cx + math.cos(a) * r_ring, y_ring, cz + math.sin(a) * r_ring))
        b_brass.add_curved_tube(pts, [0.055] * len(pts), segs=8)
        for gi in range(n_globes):
            ga = (gi / n_globes) * math.tau + (0.25 if n_globes == 6 else 0.0)
            gx = cx + math.cos(ga) * r_ring
            gz = cz + math.sin(ga) * r_ring
            b_brass.add_cylinder(gx, y_ring + 0.03, gz, 0.04, 0.04, 0.14, segs=10)
            b_led.add_sphere(gx, y_ring + 0.24, gz, 0.17, 0.16, 0.17, rings=8, segs=12)

    # 3. COMPLETE RIGHT FEATURE WALL (X = +15.0) — Fixes old missing right wall!
    b_wall.add_box(15.25, 9.30, -0.2, 0.50, 18.60, 32.0, uv_tile=6.0)
    # Fluted walnut full-height wings flanking central marble chimney breast
    b_walnut.add_box(14.86, 9.30, -11.4, 0.22, 18.60, 9.2, uv_tile=3.6)
    b_walnut.add_box(14.86, 9.30, 9.4, 0.22, 18.60, 12.2, uv_tile=3.6)
    # Brushed brass vertical inlay reveal trims + hidden warm LED slot
    for zr in (-6.82, 3.22):
        b_brass.add_box(14.82, 9.30, zr, 0.14, 18.50, 0.10)
        b_led.add_box(14.78, 9.30, zr + (0.08 if zr < 0 else -0.08), 0.06, 18.20, 0.06)
    # Central full-height Calacatta Gold marble feature chimney breast (Z in [-6.8, +3.2])
    b_marble.add_box(14.62, 9.30, -1.8, 0.72, 18.60, 10.0, uv_tile=5.5)
    b_brass.add_box(14.60, 0.10, -0.2, 0.78, 0.20, 31.6)

    # 4. COMPLETE LEFT WALL (X = -15.0) + Twin Walnut Entrance Doors + Expansion Portals
    b_wall.add_box(-15.25, 9.30, -0.2, 0.50, 18.60, 32.0, uv_tile=6.0)
    b_walnut.add_box(-14.90, 9.30, -11.8, 0.18, 18.60, 8.2, uv_tile=3.6)

    # Left-wing 1F Grand Sculpted Entrance Double Doors (PH·01, centered at Z=+2.2) — matches prologue3d.js
    b_brass.add_box(-14.86, 3.80, 2.2, 0.34, 7.60, 4.90)
    b_walnut_solid.add_box(-14.82, 3.70, 2.2, 0.30, 7.40, 4.50, uv_tile=2.4)
    b_walnut.add_box(-14.69, 3.70, 1.15, 0.10, 6.85, 2.05, uv_tile=2.2)
    b_walnut.add_box(-14.69, 3.70, 3.25, 0.10, 6.85, 2.05, uv_tile=2.2)
    b_brass.add_box(-14.64, 3.70, 2.2, 0.12, 7.10, 0.06)
    # Dual brass bar pulls
    b_brass.add_cylinder(-14.56, 2.65, 1.92, 0.045, 0.045, 1.55, segs=12)
    b_brass.add_cylinder(-14.56, 2.65, 2.48, 0.045, 0.045, 1.55, segs=12)
    b_led.add_box(-14.88, 7.68, 2.2, 0.18, 0.08, 4.92)

    # Future Expansion Portal #2: 1F Chef's Kitchen Reeded-Walnut & Brass Glass Portal (centered at Z=-8.8)
    b_brass.add_box(-14.86, 3.75, -8.8, 0.34, 7.50, 3.90)
    b_walnut_solid.add_box(-14.82, 3.70, -8.8, 0.24, 7.25, 3.54, uv_tile=2.2)
    b_frosted.add_box(-14.66, 3.70, -8.8, 0.08, 6.80, 3.16)
    for m_off in (-0.82, 0.0, 0.82):
        b_brass.add_box(-14.60, 3.70, -8.8 + m_off, 0.08, 6.90, 0.06)
    b_brass.add_cylinder(-14.54, 2.80, -8.56, 0.035, 0.035, 1.15, segs=10)

    # 5. 2F MEZZANINE FLOOR SLAB (X in [-15.0, -3.4], Z in [-15.8, +6.6], top Y = 9.20)
    b_wall.add_box(-9.20, 8.95, -4.60, 11.60, 0.42, 22.40, uv_tile=6.0)
    b_floor.add_box(-9.20, 9.18, -4.60, 11.60, 0.06, 22.40, uv_tile=4.8)
    # Mezzanine edge fascia: Calacatta marble band + champagne brass nose + under-slab warm LED glow
    b_marble.add_box(-3.36, 8.97, -4.60, 0.18, 0.46, 22.50, uv_tile=3.0)
    b_marble.add_box(-9.20, 8.97, 6.64, 11.76, 0.46, 0.18, uv_tile=3.0)
    b_brass.add_box(-3.26, 9.18, -4.60, 0.12, 0.10, 22.58)
    b_brass.add_box(-9.20, 9.18, 6.72, 11.82, 0.10, 0.12)
    b_led.add_box(-3.46, 8.70, -4.60, 0.10, 0.08, 22.20)
    b_led.add_box(-9.20, 8.70, 6.50, 11.40, 0.08, 0.10)

    # Future Expansion Portal #3: 2F Master Suite & Dressing Room Door (X=-14.86, Z=+3.6, Y=9.20..15.8)
    b_brass.add_box(-14.86, 12.50, 3.6, 0.30, 6.60, 3.40)
    b_walnut_solid.add_box(-14.80, 12.45, 3.6, 0.22, 6.42, 3.12, uv_tile=2.2)
    b_walnut.add_box(-14.68, 12.45, 3.6, 0.08, 6.10, 2.86, uv_tile=2.0)
    b_brass.add_cylinder(-14.60, 11.75, 2.48, 0.035, 0.035, 1.05, segs=10)

    # 6. DOUBLE-HEIGHT PANORAMIC CURTAIN WINDOW WALL (Z = -16.0) + Future Terrace Door Portal #1
    # Matte Studio Bronze structural mullions & framing (AD100 architectural bronze contrast)
    b_bronze.add_box(0.0, 18.25, -16.0, 30.2, 0.70, 0.48)
    b_bronze.add_box(0.0, 0.12, -16.0, 30.2, 0.24, 0.48)
    b_bronze.add_box(0.0, 9.18, -16.0, 30.2, 0.28, 0.40)  # slim mezzanine horizon transom
    for mx in (-14.82, -9.6, -3.5, 3.6, 9.4, 14.82):
        b_bronze.add_box(mx, 9.25, -16.0, 0.20, 18.50, 0.38)

    # Future Expansion Portal #1: Center-Right Sliding Glass Terrace Door (X in [-1.2, 3.6], Y in [0, 7.6])
    b_bronze.add_box(-1.2, 3.85, -15.88, 0.14, 7.70, 0.24)
    b_bronze.add_box(1.2, 7.70, -15.88, 4.96, 0.16, 0.24)
    b_bronze.add_box(1.2, 3.85, -15.84, 0.10, 7.60, 0.18)
    b_brass.add_cylinder(0.85, 3.05, -15.70, 0.035, 0.035, 1.35, segs=10)
    b_brass.add_cylinder(1.55, 3.05, -15.70, 0.035, 0.035, 1.35, segs=10)

    # Softly gathered floor-to-ceiling sheer Belgian linen drapery panels framing the windows
    for dx_center in (-14.1, -3.85, 14.05):
        for p_idx in range(6):
            px = dx_center + (p_idx - 2.5) * 0.21
            pz = -15.56 + (0.09 if p_idx % 2 == 0 else -0.05)
            b_linen.add_cylinder(px, 0.06, pz, 0.125, 0.115, 18.10, segs=10)

    # Subtle clear low-iron curtain glass panes (alpha ~ 0.07 so blue sky stays crystal bright)
    b_glass.add_box(0.0, 9.25, -16.02, 29.4, 17.80, 0.04)

    # 7. FRONT BACK-OF-CAMERA ENCLOSURE WALL (Z = +15.6) so orbiting never hits void
    b_wall.add_box(0.0, 9.30, 15.80, 30.4, 18.60, 0.50, uv_tile=6.0)
    b_walnut.add_box(-6.8, 9.30, 15.50, 11.2, 18.40, 0.14, uv_tile=3.6)
    b_brass.add_box(0.0, 0.10, 15.48, 29.6, 0.20, 0.12)
