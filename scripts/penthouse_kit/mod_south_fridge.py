"""Monumental built-in French double-door refrigerator for the South Kitchen tall wall."""

from __future__ import annotations


def _lathe(b, cx, y0, cz, profile, segs=22):
    b.add_lathe(cx, y0, cz, profile, segs=segs)


def build_south_french_fridge(ctx, mats):
    # ------------------------------------------------------------------ shell
    b = ctx.mb("FridgeInteriorShell", mats["ceramic_white"])
    b.add_box(14.74, 3.69, 22.00, 0.06, 6.94, 5.00)          # back plate
    b.add_box(13.74, 3.69, 19.50, 2.00, 6.94, 0.06)          # north wall
    b.add_box(13.74, 3.69, 24.50, 2.00, 6.94, 0.06)          # south wall
    b.add_box(13.74, 0.22, 22.00, 2.00, 0.06, 5.00)          # floor
    b.add_box(13.74, 7.14, 22.00, 2.00, 0.06, 5.00)          # ceiling

    b = ctx.mb("FridgeFrameTrim", mats["platinum"])
    b.add_box(12.68, 7.21, 22.00, 0.10, 0.10, 5.20)          # top bezel
    b.add_box(12.68, 0.21, 22.00, 0.10, 0.10, 5.20)          # bottom bezel
    b.add_box(12.68, 3.71, 19.45, 0.10, 7.10, 0.10)          # north bezel
    b.add_box(12.68, 3.71, 24.55, 0.10, 7.10, 0.10)          # south bezel

    # ------------------------------------------------------------------- LED
    b = ctx.mb("FridgeInteriorLED", mats["warm_led"])
    b.add_box(13.25, 3.70, 19.62, 0.06, 6.40, 0.06)
    b.add_box(13.25, 3.70, 24.38, 0.06, 6.40, 0.06)
    b.add_box(13.25, 7.08, 22.00, 0.06, 0.05, 4.70)

    # --------------------------------------------------------------- shelves
    b = ctx.mb("FridgeGlassShelves", mats["crystal_glass"])
    for y in (2.45, 3.85, 5.25):
        b.add_box(13.76, y, 22.00, 1.80, 0.06, 4.84)

    b = ctx.mb("FridgeGlassShelfTrim", mats["platinum"])
    for y in (2.45, 3.85, 5.25):
        b.add_box(12.88, y, 22.00, 0.05, 0.07, 4.84)

    # ------------------------------------------------------- top shelf stock
    b = ctx.mb("FridgeMilkBottles", mats["cream_pillow"])
    milk_prof = [(0, 0), (0.13, 0), (0.145, 0.08), (0.145, 0.68),
                 (0.075, 0.88), (0.065, 1.02), (0, 1.02)]
    for z in (19.95, 20.42, 20.89, 21.36, 21.83):
        _lathe(b, 13.65, 5.28, z, milk_prof)

    b = ctx.mb("FridgeMilkLabels", mats["dairy_label"])
    for z in (19.95, 20.42, 20.89, 21.36, 21.83):
        b.add_cylinder(13.65, 5.55, z, 0.152, 0.152, 0.28, segs=18)

    b = ctx.mb("FridgeGreekYogurt", mats["ceramic_white"])
    for z in (22.35, 22.78, 23.21, 23.64, 24.07):
        b.add_cylinder(13.60, 5.28, z, 0.19, 0.19, 0.38, segs=18)
    b.add_cylinder(14.10, 5.28, 23.00, 0.19, 0.19, 0.38, segs=18)

    b = ctx.mb("FridgeGreekYogurtLid", mats["dairy_label"])
    for z in (22.35, 22.78, 23.21, 23.64, 24.07):
        b.add_cylinder(13.60, 5.66, z, 0.20, 0.20, 0.05, segs=18)
    b.add_cylinder(14.10, 5.66, 23.00, 0.20, 0.20, 0.05, segs=18)

    # -------------------------------------------------- upper-mid fruit bowls
    bowl_prof = [(0, 0), (0.26, 0), (0.44, 0.14), (0.48, 0.28), (0, 0.28)]
    b = ctx.mb("FridgeFruitBowls", mats["ceramic_white"])
    for z in (20.15, 21.45, 22.75, 23.95):
        _lathe(b, 13.68, 3.88, z, bowl_prof)

    b = ctx.mb("FridgeBerriesBlue", mats["berry_blue"])
    for i in range(9):
        b.add_sphere(13.68 + 0.10 * ((i % 3) - 1), 4.20 + 0.05 * (i // 3),
                     20.15 + 0.10 * ((i % 3) - 1), 0.085, rings=8, segs=12)

    b = ctx.mb("FridgeBerriesRed", mats["berry_red"])
    for i in range(9):
        b.add_sphere(13.68 + 0.10 * ((i % 3) - 1), 4.22 + 0.05 * (i // 3),
                     21.45 + 0.10 * ((i % 3) - 1), 0.095, rings=8, segs=12)

    b = ctx.mb("FridgeProduceGreen", mats["produce_green"])
    for i in range(7):
        b.add_sphere(13.68 + 0.12 * ((i % 3) - 1), 4.22 + 0.06 * (i // 3),
                     22.75 + 0.12 * ((i % 3) - 1), 0.14, rings=8, segs=12)

    b = ctx.mb("FridgeProduceCitrus", mats["citrus_yellow"])
    for i in range(9):
        b.add_sphere(13.68 + 0.10 * ((i % 3) - 1), 4.20 + 0.05 * (i // 3),
                     23.95 + 0.10 * ((i % 3) - 1), 0.11, rings=8, segs=12)

    # ------------------------------------------------------ lower-mid crispers
    b = ctx.mb("FridgeVeggieCrispers", mats["crystal_glass"])
    for z in (20.80, 23.20):
        b.add_rounded_box(13.72, 2.92, z, 1.55, 0.78, 2.10, bevel=0.05)

    b = ctx.mb("FridgeVeggieGreens", mats["produce_green"])
    for z in (20.80, 23.20):
        for i in range(8):
            b.add_sphere(13.72 + 0.14 * ((i % 3) - 1), 2.72 + 0.10 * (i // 3),
                         z + 0.16 * ((i % 3) - 1), 0.15, rings=8, segs=12)

    b = ctx.mb("FridgeVeggieTomatoes", mats["berry_red"])
    for z in (20.80, 23.20):
        for i in range(5):
            b.add_sphere(13.72 + 0.12 * ((i % 3) - 1), 3.10,
                         z + 0.14 * ((i % 3) - 1), 0.12, rings=8, segs=12)

    b = ctx.mb("FridgeVeggieYellow", mats["citrus_yellow"])
    for z in (20.80, 23.20):
        for i in range(4):
            b.add_sphere(13.72 + 0.12 * ((i % 2) - 0.5), 3.10,
                         z + 0.14 * ((i % 2) - 0.5), 0.12, rings=8, segs=12)

    # ------------------------------------------------------- BioFresh zone
    b = ctx.mb("FridgeBioFreshDrawer", mats["glass_smoke"])
    b.add_rounded_box(13.72, 1.78, 22.00, 1.60, 0.68, 4.70, bevel=0.05)
    b.add_rounded_box(13.72, 0.92, 22.00, 1.60, 0.68, 4.70, bevel=0.05)

    b = ctx.mb("FridgeBioFreshTrim", mats["platinum"])
    b.add_box(12.88, 1.78, 22.00, 0.06, 0.10, 4.60)
    b.add_box(12.88, 0.92, 22.00, 0.06, 0.10, 4.60)

    b = ctx.mb("FridgeBioFreshSteaks", mats["steak_marbled"])
    for i in range(4):
        b.add_box(13.72, 1.80, 20.30 + 0.55 * i, 0.90, 0.10, 0.42)

    b = ctx.mb("FridgeBioFreshJars", mats["ceramic_white"])
    for i in range(5):
        b.add_cylinder(13.72, 0.72, 20.10 + 0.55 * i, 0.16, 0.16, 0.34, segs=16)

    # ------------------------------------------------------------- left door
    b = ctx.mb("FridgeDoorLeft", mats["graphite_slate"])
    b.add_box(12.65, 3.70, 20.71, 0.14, 6.96, 2.52)
    b.add_box(12.65, 3.70, 19.47, 0.16, 6.96, 0.06)
    b.add_box(12.65, 3.70, 21.95, 0.16, 6.96, 0.06)
    b.add_box(12.65, 7.16, 20.71, 0.16, 0.06, 2.52)
    b.add_box(12.65, 0.24, 20.71, 0.16, 0.06, 2.52)

    b = ctx.mb("FridgeHandleLeft", mats["platinum"])
    b.add_cylinder(12.48, 2.10, 21.78, 0.045, 0.045, 3.40, segs=16)

    # ------------------------------------------------------------ right door
    b = ctx.mb("FridgeDoorRight", mats["graphite_slate"])
    b.add_box(12.65, 6.86, 23.29, 0.14, 0.64, 2.52)          # top rail
    b.add_box(12.65, 1.28, 23.29, 0.14, 2.14, 2.52)          # bottom apron
    b.add_box(12.65, 4.45, 22.20, 0.14, 4.20, 0.36)          # handle stile
    b.add_box(12.65, 4.45, 24.38, 0.14, 4.20, 0.36)          # hinge stile
    b.add_box(12.65, 6.55, 23.29, 0.16, 0.05, 1.82)          # window bezel top
    b.add_box(12.65, 2.35, 23.29, 0.16, 0.05, 1.82)          # window bezel bot
    b.add_box(12.65, 4.45, 22.38, 0.16, 4.20, 0.05)          # window bezel N
    b.add_box(12.65, 4.45, 24.20, 0.16, 4.20, 0.05)          # window bezel S

    b = ctx.mb("FridgeDoorRightGlass", mats["glass_smoke"])
    b.add_box(12.65, 4.45, 23.29, 0.05, 4.18, 1.80)

    b = ctx.mb("FridgeHandleRight", mats["platinum"])
    b.add_cylinder(12.48, 2.10, 22.22, 0.045, 0.045, 3.40, segs=16)
