def build_south_fridge(ctx, mats):
    G = mats['graphite_slate']
    S = mats['steel']
    W = mats['warm_grey_upper']
    B = mats['brass']
    LED = mats['warm_led']
    GL = mats['glass']
    PW = mats['porcelain_white']
    CO = mats['cobalt']
    DL = mats['dairy_label']
    RA = mats['red_apple']
    HG = mats['herb_green']
    LG = mats['lemon_gold']

    # Cabinet reveal frame
    ctx.mb('FridgeFrameTop', G).add_box(13.55, 8.02, 19.90, 2.40, 0.08, 7.80)
    ctx.mb('FridgeFrameBot', G).add_box(13.55, 0.20, 19.90, 2.40, 0.08, 7.80)
    ctx.mb('FridgeFrameL', G).add_box(12.37, 4.11, 19.90, 0.06, 7.90, 0.10)
    ctx.mb('FridgeFrameR', G).add_box(14.73, 4.11, 19.90, 0.06, 7.90, 0.10)
    ctx.mb('FridgeFrameMid', G).add_box(13.55, 4.11, 19.90, 2.40, 0.06, 0.10)

    # Upper transom fascia
    ctx.mb('FridgeTransom', W).add_box(13.55, 7.43, 19.90, 2.40, 1.26, 7.80)
    ctx.mb('FridgeLouver', S).add_box(12.42, 7.43, 19.90, 0.04, 0.90, 6.80)
    for i in range(9):
        z = 16.60 + i * 0.82
        ctx.mb('LouverSlat%d' % i, S).add_box(12.40, 7.43, z, 0.03, 0.80, 0.06)

    # Interior back glow
    ctx.mb('FridgeGlow', LED).add_box(14.35, 4.05, 19.90, 0.04, 6.40, 7.40)

    # Glass shelves
    for i, y in enumerate([2.15, 3.25, 4.35, 5.45]):
        ctx.mb('Shelf%d' % i, GL).add_box(13.55, y, 19.90, 1.70, 0.04, 7.00)

    # Doors
    for side, zc, z0, z1, hz in [('Left', 17.955, 16.05, 19.86, 19.35),
                                  ('Right', 21.845, 19.94, 23.75, 20.45)]:
        ctx.mb('FridgeDoor' + side, S).add_box(12.40, 4.05, zc, 0.10, 5.20, z1 - z0)
        ctx.mb('FridgeDoorInset' + side, G).add_box(12.34, 4.05, zc, 0.04, 4.60, (z1 - z0) - 0.30)
        ctx.mb('FridgeHandle' + side, B).add_box(12.28, 4.05, hz, 0.06, 4.20, 0.08)
        ctx.mb('FridgeHandleTop' + side, B).add_box(12.31, 6.15, hz, 0.10, 0.06, 0.08)
        ctx.mb('FridgeHandleBot' + side, B).add_box(12.31, 1.95, hz, 0.10, 0.06, 0.08)

    # Dairy carafes
    for i in range(5):
        z = 16.80 + i * 1.35
        ctx.mb('Carafe%d' % i, DL).add_cylinder(13.10, 2.19, z, 0.14, 0.12, 0.55, 16)
        ctx.mb('CarafeCap%d' % i, PW).add_cylinder(13.10, 2.74, z, 0.10, 0.10, 0.06, 16)

    # Yogurt tubs
    for i in range(8):
        z = 16.60 + (i % 4) * 1.70
        y = 3.29 if i < 4 else 4.39
        ctx.mb('Yogurt%d' % i, PW).add_cylinder(13.20, y, z, 0.16, 0.16, 0.22, 16)
        ctx.mb('YogurtCap%d' % i, CO).add_cylinder(13.20, y + 0.22, z, 0.17, 0.17, 0.04, 16)

    # Fruit bowls
    for i, (y, z, mat) in enumerate([(5.49, 17.20, RA), (5.49, 19.90, HG), (5.49, 22.60, LG)]):
        ctx.mb('Bowl%d' % i, PW).add_cylinder(13.30, y, z, 0.28, 0.32, 0.10, 16)
        for j in range(4):
            ang = j * 1.57
            ctx.mb('Fruit%d_%d' % (i, j), mat).add_sphere(
                13.30 + 0.14 * (j % 2), y + 0.16, z + 0.14 * (j // 2), 0.09, 0.09, 0.09)

    # Crisper bins
    for i, z in enumerate([17.80, 21.80]):
        ctx.mb('Crisper%d' % i, GL).add_box(13.55, 1.75, z, 1.60, 0.60, 3.40)
        ctx.mb('CrisperVeg%d' % i, HG).add_box(13.55, 1.70, z, 1.40, 0.40, 3.20)

    # BioFresh drawers
    for i, z in enumerate([17.80, 21.80]):
        ctx.mb('BioFresh%d' % i, G).add_box(13.55, 0.80, z, 1.80, 1.16, 3.60)
        ctx.mb('BioFreshFace%d' % i, S).add_box(12.42, 0.80, z, 0.06, 1.10, 3.50)
        ctx.mb('BioFreshBar%d' % i, B).add_box(12.36, 0.80, z, 0.06, 0.06, 2.80)
