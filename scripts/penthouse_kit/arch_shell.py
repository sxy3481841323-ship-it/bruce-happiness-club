# scripts/penthouse_kit/arch_shell.py
"""Architectural shell: floors, walls, boiserie, ceiling, curtain wall."""

import math


def _boiserie(b, x, y, z, w, h, d, axis="x"):
    """Raised Marmorino boiserie frame with brass reveal."""
    if axis == "x":
        b.add_box(x, y, z, d, h, w, uv_tile=2.0)
        b.add_box(x + d * 0.5, y, z, 0.02, h * 0.92, w * 0.92, uv_tile=1.0)
    else:
        b.add_box(x, y, z, w, h, d, uv_tile=2.0)
        b.add_box(x, y, z + d * 0.5, w * 0.92, h * 0.92, 0.02, uv_tile=1.0)


def _pilaster(b, x, y, z, w, h, d, axis="x"):
    """Fluted walnut pilaster with brass cap/base."""
    if axis == "x":
        b.add_box(x, y, z, d, h, w, uv_tile=1.5)
        b.add_box(x, y + h * 0.5, z, d * 1.1, 0.06, w * 1.05, uv_tile=1.0)
        b.add_box(x, y - h * 0.5, z, d * 1.1, 0.06, w * 1.05, uv_tile=1.0)
    else:
        b.add_box(x, y, z, w, h, d, uv_tile=1.5)
        b.add_box(x, y + h * 0.5, z, w * 1.05, 0.06, d * 1.1, uv_tile=1.0)
        b.add_box(x, y - h * 0.5, z, w * 1.05, 0.06, d * 1.1, uv_tile=1.0)


def _recess(b, x, y, z, w, h, d, axis="x"):
    """Backlit walnut display recess."""
    if axis == "x":
        b.add_box(x, y, z, d, h, w, uv_tile=1.5)
        b.add_box(x - d * 0.4, y, z, 0.02, h * 0.85, w * 0.85, uv_tile=1.0)
    else:
        b.add_box(x, y, z, w, h, d, uv_tile=1.5)
        b.add_box(x, y, z - d * 0.4, w * 0.85, h * 0.85, 0.02, uv_tile=1.0)


def build_arch_shell(ctx, mats: dict):
    # ---------- 1F FLOOR ----------
    b = ctx.mb("FloorOak", mats["oak"])
    b.add_box(0.0, -0.06, -0.2, 30.4, 0.12, 32.0, uv_tile=6.0)

    b = ctx.mb("FloorBorderInlay", mats["walnut_solid"])
    for x in (-13.6, 13.6):
        b.add_box(x, 0.004, -0.2, 0.28, 0.008, 28.8, uv_tile=2.0)
    for z in (-14.6, 14.2):
        b.add_box(0.0, 0.004, z, 27.2, 0.008, 0.28, uv_tile=2.0)

    b = ctx.mb("FloorBrassHairline", mats["brass"])
    for x in (-13.6, 13.6):
        b.add_box(x, 0.009, -0.2, 0.03, 0.004, 28.8, uv_tile=1.0)
    for z in (-14.6, 14.2):
        b.add_box(0.0, 0.009, z, 27.2, 0.004, 0.03, uv_tile=1.0)

    # ---------- CEILING ----------
    b = ctx.mb("CeilingMarmorino", mats["marmorino"])
    b.add_box(0.0, 18.66, -0.2, 30.4, 0.12, 32.0, uv_tile=4.5)

    b = ctx.mb("CeilingCoveSoffit", mats["marmorino"])
    for x in (-14.6, 14.6):
        b.add_box(x, 18.30, -0.2, 0.8, 0.6, 31.6, uv_tile=3.0)
    for z in (-15.6, 15.2):
        b.add_box(0.0, 18.30, z, 29.2, 0.6, 0.8, uv_tile=3.0)

    b = ctx.mb("WarmCoveLED", mats["warm_led"])
    for x in (-14.2, 14.2):
        b.add_box(x, 18.02, -0.2, 0.06, 0.04, 31.2, uv_tile=1.0)
    for z in (-15.2, 14.8):
        b.add_box(0.0, 18.02, z, 28.4, 0.04, 0.06, uv_tile=1.0)

    # ---------- ATRIUM CHANDELIER ----------
    b = ctx.mb("ChandelierBrass", mats["brass"])
    b.add_cylinder(2.6, 17.9, -2.8, 0.04, 0.04, 0.7, segs=12)
    b.add_cylinder(2.6, 16.4, -2.8, 1.55, 1.55, 0.06, segs=32)
    b.add_cylinder(2.6, 14.6, -2.8, 1.05, 1.05, 0.06, segs=32)
    for i in range(12):
        import math
        a = i * math.pi / 6.0
        b.add_cylinder(2.6 + 1.55 * math.cos(a), 16.4, -2.8 + 1.55 * math.sin(a),
                       0.02, 0.02, 0.5, segs=6)
    b = ctx.mb("ChandelierGlobes", mats["warm_bulb"])
    for i in range(12):
        import math
        a = i * math.pi / 6.0
        b.add_sphere(2.6 + 1.55 * math.cos(a), 16.15, -2.8 + 1.55 * math.sin(a),
                     0.11, 0.11, 0.11, rings=8, segs=12)
    for i in range(8):
        import math
        a = i * math.pi / 4.0
        b.add_sphere(2.6 + 1.05 * math.cos(a), 14.35, -2.8 + 1.05 * math.sin(a),
                     0.09, 0.09, 0.09, rings=8, segs=12)

    # ---------- RIGHT WALL (X=+15.0) ----------
    b = ctx.mb("RightWallMarmorino", mats["marmorino"])
    b.add_box(15.0, 9.3, -0.2, 0.3, 18.6, 32.0, uv_tile=4.5)

    b = ctx.mb("RightChimneyBreast", mats["marble"])
    b.add_box(14.75, 4.6, -1.8, 0.5, 9.2, 10.0, uv_tile=3.0)
    b.add_box(14.55, 0.9, -1.8, 0.15, 1.8, 3.2, uv_tile=2.0)

    b = ctx.mb("RightFlutedWalnut", mats["walnut_fluted"])
    for z in (-9.5, -7.0, 3.5, 6.0):
        b.add_box(14.85, 4.6, z, 0.25, 9.2, 0.9, uv_tile=1.5)
    for z in (-9.5, -7.0, 3.5, 6.0):
        b.add_box(14.7, 4.6, z, 0.05, 9.0, 0.06, uv_tile=1.0)

    b = ctx.mb("RightBoiserie", mats["marmorino"])
    for z in (-12.5, -10.8, 8.0, 10.0, 12.0):
        _boiserie(b, 14.82, 4.6, z, 1.4, 7.5, 0.12, axis="x")

    # ---------- LEFT WALL (X=-15.0) ----------
    b = ctx.mb("LeftWallMarmorino", mats["marmorino"])
    b.add_box(-15.0, 9.3, -0.2, 0.3, 18.6, 32.0, uv_tile=4.5)

    # Entrance doors
    b = ctx.mb("EntranceDoors", mats["walnut_solid"])
    b.add_box(-14.85, 3.7, 2.2, 0.18, 7.4, 2.6, uv_tile=2.0)
    b.add_box(-14.85, 3.7, 2.2, 0.20, 7.4, 0.04, uv_tile=1.0)
    b = ctx.mb("EntranceArchitrave", mats["brass"])
    b.add_box(-14.78, 3.7, 2.2, 0.06, 7.6, 2.9, uv_tile=1.0)
    b.add_box(-14.72, 3.7, 2.2, 0.04, 7.4, 0.05, uv_tile=1.0)
    b.add_box(-14.72, 3.7, 2.2, 0.04, 0.05, 2.6, uv_tile=1.0)
    b = ctx.mb("EntrancePulls", mats["brass"])
    b.add_cylinder(-14.68, 3.0, 1.6, 0.03, 0.03, 1.4, segs=10)
    b.add_cylinder(-14.68, 3.0, 2.8, 0.03, 0.03, 1.4, segs=10)

    # Kitchen glass portal
    b = ctx.mb("KitchenPortal", mats["glass"])
    b.add_box(-14.85, 3.7, -8.8, 0.06, 7.4, 2.4, uv_tile=1.0)
    b = ctx.mb("KitchenPortalFrame", mats["brass"])
    b.add_box(-14.78, 3.7, -8.8, 0.06, 7.6, 2.6, uv_tile=1.0)

    # Left wall boiserie + pilasters + recesses (keep 2F Z=[-6.8..0.0] clear for monumental regatta masterwork)
    b = ctx.mb("LeftBoiserie", mats["marmorino"])
    for z in (-13.2, -11.8, -5.5, -3.0, -1.2, 6.0, 8.0, 11.5, 13.5):
        _boiserie(b, -14.82, 4.6, z, 1.4, 7.5, 0.12, axis="x")
    for z in (-13.2, -11.8, 6.0, 8.0, 11.5, 13.5):
        _boiserie(b, -14.82, 13.8, z, 1.4, 7.5, 0.12, axis="x")

    b = ctx.mb("LeftPilasters", mats["walnut_fluted"])
    for z in (-14.2, -10.5, -6.5, -0.5, 4.8, 9.5, 14.5):
        _pilaster(b, -14.85, 4.6, z, 0.7, 9.2, 0.22, axis="x")
    for z in (-14.2, -10.5, -7.8, 1.0, 5.2, 9.5, 14.5):
        _pilaster(b, -14.85, 13.8, z, 0.7, 8.8, 0.22, axis="x")

    b = ctx.mb("LeftBrassRails", mats["brass"])
    for y in (1.35, 8.9):
        b.add_box(-14.78, y, -0.2, 0.05, 0.06, 31.6, uv_tile=1.0)

    b = ctx.mb("LeftRecesses", mats["walnut_solid"])
    _recess(b, -14.75, 4.6, -3.8, 1.6, 6.0, 0.35, axis="x")
    _recess(b, -14.75, 4.6, 10.5, 1.6, 6.0, 0.35, axis="x")
    b = ctx.mb("LeftRecessLED", mats["warm_led"])
    b.add_box(-14.55, 7.4, -3.8, 0.04, 0.04, 1.4, uv_tile=1.0)
    b.add_box(-14.55, 7.4, 10.5, 0.04, 0.04, 1.4, uv_tile=1.0)

    # ---------- SOUTH / BACK WALL (Z=+15.8) ----------
    b = ctx.mb("SouthWallMarmorino", mats["marmorino"])
    b.add_box(0.0, 9.3, 15.8, 30.4, 18.6, 0.3, uv_tile=4.5)

    b = ctx.mb("SouthBoiserieBays", mats["marmorino"])
    for i in range(6):
        x = -11.0 + i * 4.4
        _boiserie(b, x, 4.6, 15.62, 3.6, 7.5, 0.14, axis="z")
        _boiserie(b, x, 13.8, 15.62, 3.6, 7.5, 0.14, axis="z")

    b = ctx.mb("SouthPilasters", mats["walnut_fluted"])
    for i in range(5):
        x = -13.0 + i * 5.2
        _pilaster(b, x, 4.6, 15.65, 0.8, 9.2, 0.24, axis="z")
        _pilaster(b, x, 13.8, 15.65, 0.8, 8.8, 0.24, axis="z")

    b = ctx.mb("SouthBrassRails", mats["brass"])
    for y in (1.35, 8.9):
        b.add_box(0.0, y, 15.58, 27.2, 0.06, 0.05, uv_tile=1.0)

    # Gallery bookcase credenza
    b = ctx.mb("GalleryCredenza", mats["walnut_solid"])
    b.add_box(3.4, 1.6, 15.1, 6.8, 3.2, 0.7, uv_tile=2.0)
    b = ctx.mb("GalleryCredenzaBrass", mats["brass"])
    b.add_box(3.4, 3.25, 15.1, 6.9, 0.06, 0.75, uv_tile=1.0)
    b.add_box(3.4, 0.05, 15.1, 6.9, 0.06, 0.75, uv_tile=1.0)
    b = ctx.mb("GalleryBooks", mats["burgundy"])
    for i in range(14):
        x = 0.4 + i * 0.46
        b.add_box(x, 2.4, 15.05, 0.32, 1.4, 0.5, uv_tile=1.0)
    b = ctx.mb("GalleryBooks2", mats["cognac_suede"])
    for i in range(10):
        x = 0.8 + i * 0.6
        b.add_box(x, 1.0, 15.05, 0.4, 1.0, 0.5, uv_tile=1.0)

    # ---------- 2F MEZZANINE ----------
    b = ctx.mb("MezzanineSlab", mats["oak"])
    b.add_box(-9.2, 9.14, -4.6, 11.6, 0.12, 22.4, uv_tile=4.0)
    b = ctx.mb("MezzanineRail", mats["brass"])
    b.add_box(-3.4, 9.9, -4.6, 0.06, 1.4, 22.4, uv_tile=1.0)
    b.add_box(-9.2, 9.9, 6.6, 11.6, 1.4, 0.06, uv_tile=1.0)

    b = ctx.mb("MasterSuiteDoor", mats["walnut_solid"])
    b.add_box(-14.86, 11.4, 3.6, 0.16, 4.4, 1.6, uv_tile=2.0)
    b = ctx.mb("MasterSuiteDoorBrass", mats["brass"])
    b.add_box(-14.78, 11.4, 3.6, 0.05, 4.6, 1.8, uv_tile=1.0)

    # ---------- PANORAMIC CURTAIN WALL (Z=-16.0) ----------
    b = ctx.mb("CurtainMullions", mats["bronze_dark"])
    for x in (-14.82, -9.6, -3.5, 4.4, 9.4, 14.82):
        b.add_box(x, 9.3, -16.0, 0.14, 18.6, 0.14, uv_tile=1.0)
    b.add_box(0.0, 9.18, -16.0, 29.8, 0.14, 0.14, uv_tile=1.0)
    b.add_box(0.0, 0.02, -16.0, 29.8, 0.06, 0.14, uv_tile=1.0)

    b = ctx.mb("ClearCurtainGlass", mats["glass"])
    b.add_box(-8.1, 4.6, -16.0, 13.4, 9.16, 0.04, uv_tile=1.0)
    b.add_box(9.5, 4.6, -16.0, 10.6, 9.16, 0.04, uv_tile=1.0)
    b.add_box(0.0, 12.95, -16.0, 29.6, 10.5, 0.04, uv_tile=1.0)

    b = ctx.mb("SlidingDoorFrames", mats["bronze_dark"])
    b.add_box(-2.2, 3.8, -15.85, 0.08, 7.6, 0.08, uv_tile=1.0)
    b.add_box(4.6, 3.8, -15.85, 0.08, 7.6, 0.08, uv_tile=1.0)

    b = ctx.mb("TerraceThreshold", mats["brass"])
    b.add_box(1.4, 0.015, -15.9, 5.6, 0.03, 0.2, uv_tile=1.0)

    b = ctx.mb("SheerDrapery", mats["sheer_linen"])
    for x in (-14.1, -3.85, 14.05):
        b.add_box(x, 4.6, -15.7, 0.6, 9.16, 0.12, uv_tile=2.0)
        b.add_box(x, 13.0, -15.7, 0.6, 10.4, 0.12, uv_tile=2.0)
