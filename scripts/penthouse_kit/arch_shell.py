# scripts/penthouse_kit/arch_shell.py
from .prim_lib import SceneContext, MeshBuilder
import math


def build_arch_shell(ctx, mats):
    # ---------------- 1F FLOOR ----------------
    b = ctx.mb("FloorOak", mats["oak"])
    b.add_box(0.0, -0.06, -0.2, 30.4, 0.12, 32.0, uv_tile=6.0)

    b = ctx.mb("FloorBorderInlay", mats["rift_oak"])
    b.add_box(0.0, 0.005, -0.2, 27.2, 0.02, 28.8, uv_tile=4.0)

    b = ctx.mb("FloorBrassHairline", mats["brass"])
    for x in (-13.6, 13.6):
        b.add_box(x, 0.02, -0.2, 0.03, 0.02, 28.8)
    for z in (-14.6, 14.2):
        b.add_box(0.0, 0.02, z, 27.2, 0.02, 0.03)

    # ---------------- 1F CEILING ----------------
    b = ctx.mb("CeilingMarmorino", mats["marmorino"])
    b.add_box(0.0, 18.66, -0.2, 30.4, 0.10, 32.0, uv_tile=5.0)

    b = ctx.mb("CeilingCoveSoffit", mats["marmorino"])
    for x in (-14.6, 14.6):
        b.add_box(x, 18.30, -0.2, 0.6, 0.6, 31.6)
    for z in (-15.6, 15.2):
        b.add_box(0.0, 18.30, z, 29.6, 0.6, 0.6)

    b = ctx.mb("WarmCoveLED", mats["warm_led"])
    for x in (-14.2, 14.2):
        b.add_box(x, 18.02, -0.2, 0.10, 0.05, 31.0)
    for z in (-15.2, 14.8):
        b.add_box(0.0, 18.02, z, 29.0, 0.05, 0.10)

    # ---------------- CHANDELIER ----------------
    b = ctx.mb("ChandelierBrass", mats["brass"])
    b.add_cylinder(2.6, 16.4, -2.8, 0.05, 0.05, 2.2, segs=12)
    b.add_cylinder(2.6, 14.6, -2.8, 0.55, 0.55, 0.06, segs=24)
    for i in range(6):
        a = i * math.pi / 3.0
        b.add_cylinder(2.6 + 0.45 * math.cos(a), 14.6, -2.8 + 0.45 * math.sin(a),
                       0.02, 0.02, 0.5, segs=8)

    b = ctx.mb("ChandelierGlobes", mats["warm_bulb"])
    for i in range(6):
        a = i * math.pi / 3.0
        b.add_sphere(2.6 + 0.45 * math.cos(a), 14.35, -2.8 + 0.45 * math.sin(a),
                     0.14, 0.14, 0.14, rings=10, segs=14)

    # ---------------- MAIN WALLS (chalk limestone) ----------------
    b = ctx.mb("RightWallMarmorino", mats["marmorino"])
    b.add_box(14.9, 9.3, -0.2, 0.30, 18.6, 32.0, uv_tile=4.0)

    # Left West wall carved open for 7.8m x 3.84m Mountain-View Herb Garden Window (Z=-14.4..-6.6, Y=1.08..4.92)
    b.add_box(-14.9, 9.3, 4.6, 0.30, 18.6, 22.4, uv_tile=4.0)
    b.add_box(-14.9, 9.3, -15.3, 0.30, 18.6, 1.8, uv_tile=4.0)
    b.add_box(-14.9, 0.54, -10.5, 0.30, 1.08, 7.8, uv_tile=4.0)
    b.add_box(-14.9, 11.76, -10.5, 0.30, 13.68, 7.8, uv_tile=4.0)

    b = ctx.mb("SouthWallMarmorino", mats["marmorino"])
    b.add_box(0.0, 9.3, 15.4, 30.4, 18.6, 0.30, uv_tile=4.0)

    # ---------------- CELADON RECESSED BAYS ----------------
    b = ctx.mb("RightCeladonBays", mats["celadon_plaster"])
    for z0, z1 in ((-12.5, -10.6), (8.2, 12.2)):
        cz = 0.5 * (z0 + z1)
        sz = z1 - z0
        b.add_box(14.72, 9.3, cz, 0.06, 14.0, sz, uv_tile=3.0)

    b = ctx.mb("LeftRecesses", mats["celadon_plaster"])
    b.add_box(-14.72, 9.3, 10.5, 0.06, 14.0, 3.0, uv_tile=3.0)

    b = ctx.mb("SouthCeladonInlays", mats["celadon_plaster"])
    for i in range(6):
        x = -11.0 + i * 4.4
        if -6.8 <= x <= 0.0:
            continue
        b.add_box(x, 9.3, 15.22, 3.2, 12.0, 0.06, uv_tile=3.0)

    # ---------------- RIFT-OAK PILASTERS + BRASS FILLETS ----------------
    b = ctx.mb("RightRiftOakStiles", mats["rift_oak"])
    for z in (-13.4, -9.4, -6.2, 2.0, 6.4, 13.0):
        b.add_box(14.62, 9.3, z, 0.07, 18.0, 0.42, uv_tile=2.0)

    b = ctx.mb("LeftRiftOakStiles", mats["rift_oak"])
    for z in (-13.4, -7.0):
        b.add_box(-14.62, 13.8, z, 0.07, 9.0, 0.42, uv_tile=2.0)
    for z in (0.4, 6.2, 13.0):
        b.add_box(-14.62, 9.3, z, 0.07, 18.0, 0.42, uv_tile=2.0)

    b = ctx.mb("SouthRiftOakStiles", mats["rift_oak"])
    for x in (-13.4, -6.6, 2.2, 8.8, 13.4):
        b.add_box(x, 9.3, 15.12, 0.42, 18.0, 0.07, uv_tile=2.0)

    b = ctx.mb("BrassStileFillets", mats["brass"])
    for z in (-13.4, -9.4, -6.2, 2.0, 6.4, 13.0):
        b.add_box(14.58, 9.3, z + 0.235, 0.025, 18.0, 0.025)
    for z in (-13.4, -7.0):
        b.add_box(-14.58, 13.8, z + 0.235, 0.025, 9.0, 0.025)
    for z in (0.4, 6.2, 13.0):
        b.add_box(-14.58, 9.3, z + 0.235, 0.025, 18.0, 0.025)

    # ---------------- VERDE ALPI CHIMNEY BREAST ----------------
    b = ctx.mb("RightChimneyBreast", mats["verde_alpi"])
    b.add_box(14.75, 4.6, -1.8, 0.55, 9.2, 3.6, uv_tile=2.0)
    b.add_box(14.55, 0.9, -1.8, 0.85, 0.30, 4.0, uv_tile=1.0)
    b.add_box(14.55, 9.35, -1.8, 0.85, 0.20, 4.0, uv_tile=1.0)

    # ---------------- ENTRANCE ----------------
    b = ctx.mb("EntranceDoors", mats["rift_oak"])
    b.add_box(-14.85, 3.7, 2.2, 0.18, 7.4, 2.6, uv_tile=2.0)

    b = ctx.mb("EntranceArchitrave", mats["brass"])
    b.add_box(-14.72, 7.45, 2.2, 0.06, 0.10, 2.9)
    b.add_box(-14.72, 3.7, 0.85, 0.06, 7.4, 0.06)
    b.add_box(-14.72, 3.7, 3.55, 0.06, 7.4, 0.06)

    b = ctx.mb("EntrancePulls", mats["brass"])
    b.add_cylinder(-14.68, 3.4, 1.55, 0.03, 0.03, 0.9, segs=10)
    b.add_cylinder(-14.68, 3.4, 2.85, 0.03, 0.03, 0.9, segs=10)

    # (West Kitchen Wing at Z = -14.8..-0.2 is now completely open to the Salon)

    # ---------------- GALLERY CREDENZA ----------------
    b = ctx.mb("GalleryCredenza", mats["rift_oak"])
    b.add_box(3.4, 1.6, 15.1, 3.6, 1.4, 0.55, uv_tile=2.0)

    b = ctx.mb("GalleryCredenzaBrass", mats["brass"])
    b.add_box(3.4, 2.32, 15.1, 3.7, 0.04, 0.60)
    b.add_box(3.4, 0.88, 15.1, 3.7, 0.04, 0.60)

    b = ctx.mb("GalleryBooks", mats["slate_linen"])
    for x in (-0.9, -0.4, 0.2, 0.7, 1.2):
        b.add_box(3.4 + x, 2.55, 15.1, 0.10, 0.42, 0.32)
    b = ctx.mb("GalleryBooksBurgundy", mats["burgundy"])
    b.add_box(3.4 - 1.3, 2.55, 15.1, 0.10, 0.40, 0.32)
    b = ctx.mb("GalleryBooksCognac", mats["cognac_suede"])
    b.add_box(3.4 + 1.6, 2.55, 15.1, 0.10, 0.38, 0.32)

    # ---------------- MEZZANINE ----------------
    b = ctx.mb("MezzanineSlab", mats["oak"])
    b.add_box(-9.2, 9.14, -4.6, 11.6, 0.12, 22.4, uv_tile=4.0)

    b = ctx.mb("MezzanineLandingTrim", mats["rift_oak"])
    b.add_box(-9.8, 9.21, 6.56, 3.30, 0.03, 0.12)

    b = ctx.mb("MezzanineLandingBrass", mats["brass"])
    b.add_box(-9.8, 9.235, 6.56, 3.30, 0.02, 0.03)

    # ---------------- MASTER SUITE DOOR ----------------
    b = ctx.mb("MasterSuiteDoor", mats["rift_oak"])
    b.add_box(-14.86, 11.4, 3.6, 0.14, 4.4, 1.6, uv_tile=2.0)

    b = ctx.mb("MasterSuiteDoorBrass", mats["brass"])
    b.add_box(-14.78, 13.65, 3.6, 0.05, 0.06, 1.7)
    b.add_box(-14.78, 11.4, 2.78, 0.05, 4.4, 0.05)
    b.add_box(-14.78, 11.4, 4.42, 0.05, 4.4, 0.05)
    b.add_cylinder(-14.74, 11.2, 3.0, 0.025, 0.025, 0.4, segs=10)

    # ---------------- TERRACE CURTAIN WALL (Z = -16.0) ----------------
    b = ctx.mb("CurtainMullions", mats["window_frame"])
    for x in (-14.75, -8.4, -2.2, 4.6, 9.8, 14.75):
        b.add_box(x, 9.3, -16.0, 0.055, 18.6, 0.08)
    b.add_box(0.0, 18.55, -16.0, 30.0, 0.07, 0.08)
    b.add_box(0.0, 9.20, -16.0, 30.0, 0.06, 0.08)
    b.add_box(0.0, 0.06, -16.0, 30.0, 0.06, 0.08)

    b = ctx.mb("ClearCurtainGlass", mats["glass"])
    for x0, x1 in ((-14.75, -8.4), (-8.4, -2.2), (4.6, 9.8), (9.8, 14.75)):
        cx = 0.5 * (x0 + x1)
        sx = (x1 - x0) - 0.07
        b.add_box(cx, 9.3, -16.0, sx, 18.2, 0.025)

    b = ctx.mb("SlidingDoorFrames", mats["window_frame"])
    b.add_box(-2.2, 9.3, -16.0, 0.06, 18.2, 0.08)
    b.add_box(4.6, 9.3, -16.0, 0.06, 18.2, 0.08)
    b.add_box(1.2, 18.2, -16.0, 6.8, 0.06, 0.08)

    b = ctx.mb("TerraceThreshold", mats["marmorino"])
    b.add_box(0.0, 0.04, -15.85, 30.0, 0.08, 0.30, uv_tile=2.0)

    b = ctx.mb("SheerDrapery", mats["sheer_linen"])
    for x in (-14.35, 14.35):
        b.add_box(x, 9.3, -15.72, 0.55, 18.0, 0.04, uv_tile=3.0)
