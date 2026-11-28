from penthouse_kit.cushion_helper import add_designer_pillow


def build_salon_seating(ctx, mats):
    dove = mats['dove_boucle']
    oak = mats['rift_oak']
    emerald = mats['emerald_silk']
    cream = mats['cream_pillow']
    charcoal = mats['charcoal']
    walnut = mats['walnut_solid']
    saddle = mats['saddle_tan']
    verde = mats['verde_alpi']
    obsidian = mats['obsidian_bezel']
    flint = mats['evian_flint_glass']
    green = mats['herb_green']
    orchid = mats['orchid_white']
    brass = mats['brass']
    steel = mats['steel']
    porcelain = mats['porcelain_white']
    oxblood = mats['tray_burgundy']

    # 1. Expanded rug
    b = ctx.mb('SalonRugPlinth', oak)
    b.add_box(1.8, 0.012, -0.6, 18.4, 0.024, 16.0, uv_tile=2.0)
    b = ctx.mb('SalonRug', cream)
    b.add_box(1.8, 0.038, -0.6, 18.0, 0.02, 15.6, uv_tile=3.0)

    # 2. Monumental U-sectional
    b = ctx.mb('SofaPlinth', oak)
    b.add_box(-0.5, 0.16, -5.5, 10.2, 0.32, 2.6, uv_tile=1.5)
    b.add_box(-4.3, 0.16, -0.4, 2.6, 0.32, 7.6, uv_tile=1.5)
    b.add_box(-1.9, 0.16, 2.2, 7.4, 0.32, 2.5, uv_tile=1.5)
    b = ctx.mb('SofaSeat', dove)
    b.add_rounded_box(-0.5, 0.80, -5.5, 10.0, 0.72, 2.4, bevel=0.08, uv_tile=1.2)
    b.add_rounded_box(-4.3, 0.80, -0.4, 2.4, 0.72, 7.4, bevel=0.08, uv_tile=1.2)
    b.add_rounded_box(-1.9, 0.80, 2.2, 7.2, 0.72, 2.3, bevel=0.08, uv_tile=1.2)
    b = ctx.mb('SofaBack', dove)
    b.add_rounded_box(-0.5, 1.30, -6.6, 10.2, 1.10, 0.55, bevel=0.10, uv_tile=1.0)
    b.add_rounded_box(-5.4, 1.30, -0.4, 0.55, 1.10, 7.6, bevel=0.10, uv_tile=1.0)
    b.add_rounded_box(-1.9, 1.30, 3.3, 7.4, 1.10, 0.55, bevel=0.10, uv_tile=1.0)
    b = ctx.mb('SofaBolsters', dove)
    for bx, bz in [(-3.6, -5.5), (1.4, -5.5), (-4.3, -3.4), (-4.3, 1.6), (-3.4, 2.2), (0.6, 2.2)]:
        b.add_cylinder(bx, 1.16, bz, 0.22, 0.22, 1.4, segs=14, rot_z=1.5708)
    for idx, (px, py, pz, mat_p, yaw) in enumerate([
        (-2.8, 1.32, -5.9, emerald, 0.15),
        (-1.2, 1.32, -5.9, cream, -0.10),
        (-4.9, 1.32, -2.4, emerald, 1.55),
        (-4.9, 1.32, 0.6, cream, 1.55),
        (-2.4, 1.32, 2.7, emerald, -0.12),
    ]):
        add_designer_pillow(
            ctx.mb(f"SofaPillow{idx}", mat_p),
            ctx.mb(f"SofaPillowPipe{idx}", brass),
            px, py, pz, w=0.68, h=0.62, thick=0.20, yaw=yaw, tilt=-0.22,
        )

    # 3. Behind-sofa console + Taccia lamp
    b = ctx.mb('ConsoleTop', walnut)
    b.add_rounded_box(-6.55, 1.02, -1.4, 0.85, 0.10, 6.8, bevel=0.03, uv_tile=1.0)
    b = ctx.mb('ConsoleLower', charcoal)
    b.add_rounded_box(-6.55, 0.55, -1.4, 0.80, 0.06, 6.6, bevel=0.02, uv_tile=1.0)
    b = ctx.mb('ConsoleLegs', charcoal)
    for lz in [-4.6, -1.4, 1.8]:
        b.add_box(-6.55, 0.52, lz, 0.10, 1.04, 0.10, uv_tile=0.5)
    b = ctx.mb('ConsoleBooks', cream)
    b.add_box(-6.55, 1.10, -3.6, 0.55, 0.06, 0.75, uv_tile=0.5)
    b.add_box(-6.55, 1.16, -3.6, 0.50, 0.05, 0.70, uv_tile=0.5)
    b = ctx.mb('TacciaLamp', steel)
    b.add_cylinder(-6.55, 1.07, 0.6, 0.28, 0.24, 0.10, segs=20)
    b.add_cylinder(-6.55, 1.17, 0.6, 0.05, 0.05, 0.98, segs=12)
    b.add_sphere(-6.55, 2.55, 0.6, 0.42, 0.40, 0.42, rings=14, segs=20)

    # 4. Cognac saddle-leather club armchair
    b = ctx.mb('ClubChairSeat', saddle)
    b.add_rounded_box(6.4, 0.62, -5.0, 1.5, 0.55, 1.5, bevel=0.10, uv_tile=1.0, rot_y=-0.35)
    b = ctx.mb('ClubChairBack', saddle)
    b.add_rounded_box(6.4, 1.15, -5.75, 1.5, 0.95, 0.35, bevel=0.10, uv_tile=1.0, rot_y=-0.35)
    b = ctx.mb('ClubChairArms', saddle)
    b.add_rounded_box(5.55, 0.95, -5.0, 0.30, 0.55, 1.5, bevel=0.08, uv_tile=1.0, rot_y=-0.35)
    b.add_rounded_box(7.25, 0.95, -5.0, 0.30, 0.55, 1.5, bevel=0.08, uv_tile=1.0, rot_y=-0.35)
    b = ctx.mb('ClubChairLegs', walnut)
    for lx, lz in [(5.7, -5.6), (7.1, -5.6), (5.7, -4.4), (7.1, -4.4)]:
        b.add_cylinder(lx, 0.04, lz, 0.06, 0.05, 0.32, segs=10)

    # 5. Verde-Alpi cocktail table
    b = ctx.mb('TableAPedestals', obsidian)
    b.add_box(1.35, 0.42, -1.55, 3.6, 0.84, 3.4, uv_tile=1.0)
    b = ctx.mb('TableASmokedStone', verde)
    b.add_rounded_box(1.35, 0.94, -1.55, 4.60, 0.14, 4.40, bevel=0.05, uv_tile=1.5)
    b = ctx.mb('TableB', walnut)
    b.add_cylinder(4.35, 0.04, -1.55, 0.55, 0.55, 0.86, segs=20)
    b.add_rounded_box(4.35, 0.94, -1.55, 1.10, 0.10, 1.10, bevel=0.03, uv_tile=1.0)
    b = ctx.mb('ConciergePager1F', charcoal)
    b.add_rounded_box(4.20, 1.02, -1.70, 0.16, 0.06, 0.22, bevel=0.02, uv_tile=0.5)
    b = ctx.mb('ConciergeScreen1F', charcoal)
    b.add_rounded_box(4.50, 1.02, -1.40, 0.20, 0.10, 0.14, bevel=0.02, uv_tile=0.5)

    # Evian tray + pour ceremony
    b = ctx.mb('TableATrayLeather', oxblood)
    b.add_rounded_box(1.16, 1.01, -2.55, 1.30, 0.04, 0.90, bevel=0.02, uv_tile=1.0)
    b = ctx.mb('TableATrayBrass', brass)
    b.add_box(1.16, 1.035, -2.55, 1.34, 0.02, 0.94, uv_tile=0.5)
    b = ctx.mb('EvianBottles1F', flint)
    for bx in [0.85, 1.05, 1.25, 1.45]:
        b.add_cylinder(bx, 1.05, -2.75, 0.055, 0.045, 0.30, segs=12)
    b = ctx.mb('EvianCapsReserve1F', green)
    for bx in [0.85, 1.05, 1.25, 1.45]:
        b.add_cylinder(bx, 1.35, -2.75, 0.045, 0.045, 0.03, segs=10)
    b = ctx.mb('EvianLabelsReserve1F', cream)
    for bx in [0.85, 1.05, 1.25, 1.45]:
        b.add_box(bx, 1.18, -2.75, 0.09, 0.10, 0.005, uv_tile=0.5)
    b = ctx.mb('EvianPourBottle1F', flint)
    b.add_cylinder(1.15, 1.05, -2.55, 0.06, 0.05, 0.32, segs=12, rot_z=0.35)
    b = ctx.mb('EvianPourLabel1F', cream)
    b.add_box(1.15, 1.20, -2.55, 0.09, 0.10, 0.005, uv_tile=0.5)
    b = ctx.mb('EvianPourCap1F', green)
    b.add_cylinder(1.15, 1.37, -2.55, 0.05, 0.05, 0.03, segs=10)
    b = ctx.mb('CrystalWaterBowl1F', flint)
    b.add_lathe(1.44, 1.01, -2.50, [(0.0, 0.0), (0.14, 0.02), (0.18, 0.10), (0.16, 0.16)], segs=20)
    b = ctx.mb('CrystalBowlFoot1F', flint)
    b.add_cylinder(1.44, 1.01, -2.50, 0.06, 0.08, 0.03, segs=14)
    b = ctx.mb('CrystalBowlWater1F', flint)
    b.add_cylinder(1.44, 1.13, -2.50, 0.15, 0.15, 0.02, segs=18)

    # Photo 3 styling
    b = ctx.mb('SalonOrchidBowl', obsidian)
    b.add_lathe(1.45, 1.01, -1.35, [(0.0, 0.0), (0.22, 0.02), (0.26, 0.14), (0.22, 0.22)], segs=20)
    b = ctx.mb('OrchidLeaves', green)
    for i in range(6):
        b.add_sphere(1.45 + 0.18 * (i % 2), 1.28, -1.35 + 0.10 * (i % 3), 0.20, 0.03, 0.08, rings=8, segs=10)
    b = ctx.mb('OrchidStems', green)
    for sx in [-0.12, 0.0, 0.12]:
        b.add_curved_tube([(1.45 + sx, 1.22, -1.35), (1.45 + sx * 1.4, 1.55, -1.35), (1.45 + sx * 1.8, 1.80, -1.35)], [0.012, 0.010, 0.008], segs=8)
    b = ctx.mb('OrchidBlooms', orchid)
    for i in range(14):
        bx = 1.45 + (i % 5 - 2) * 0.10
        by = 1.55 + (i // 5) * 0.10
        b.add_sphere(bx, by, -1.35 + (i % 3 - 1) * 0.06, 0.055, 0.045, 0.055, rings=8, segs=10)

    b = ctx.mb('ChampagneIceBucket', steel)
    b.add_cylinder(2.55, 1.01, -0.55, 0.22, 0.26, 0.06, segs=20)
    b.add_lathe(2.55, 1.07, -0.55, [(0.0, 0.0), (0.20, 0.02), (0.24, 0.22), (0.22, 0.30)], segs=20)
    b = ctx.mb('ChampagneNapkin', cream)
    b.add_box(2.55, 1.38, -0.55, 0.30, 0.02, 0.30, uv_tile=0.5)
    b = ctx.mb('ChampagneBottle', charcoal)
    b.add_cylinder(2.55, 1.10, -0.55, 0.07, 0.06, 0.34, segs=14, rot_z=0.25)
    b = ctx.mb('ChampagneFoil', brass)
    b.add_cylinder(2.55, 1.44, -0.55, 0.06, 0.05, 0.05, segs=12)
    b = ctx.mb('ChampagneStems', flint)
    for gx in [2.30, 2.80]:
        b.add_cylinder(gx, 1.01, -0.55, 0.05, 0.05, 0.02, segs=12)
        b.add_cylinder(gx, 1.03, -0.55, 0.012, 0.012, 0.14, segs=8)
        b.add_lathe(gx, 1.17, -0.55, [(0.0, 0.0), (0.06, 0.02), (0.07, 0.10), (0.06, 0.14)], segs=14)

    b = ctx.mb('SalonFruitPlatter', porcelain)
    b.add_rounded_box(-0.15, 1.03, -0.85, 0.85, 0.04, 0.55, bevel=0.03, uv_tile=1.0)
    b = ctx.mb('FruitApples', mats['red_apple'])
    b.add_sphere(-0.30, 1.10, -0.85, 0.09, 0.09, 0.09, rings=10, segs=12)
    b = ctx.mb('FruitPears', green)
    b.add_sphere(0.05, 1.10, -0.75, 0.08, 0.10, 0.08, rings=10, segs=12)
    b.add_sphere(0.15, 1.09, -0.95, 0.07, 0.09, 0.07, rings=10, segs=12)
    b = ctx.mb('FruitGrapes', charcoal)
    for i in range(6):
        b.add_sphere(-0.05 + (i % 3) * 0.05, 1.08 + (i // 3) * 0.04, -0.95, 0.03, 0.03, 0.03, rings=6, segs=8)
    b = ctx.mb('FruitFigs', oxblood)
    b.add_sphere(-0.35, 1.09, -0.70, 0.05, 0.06, 0.05, rings=8, segs=10)

    b = ctx.mb('SanBernardoBottles', flint)
    for bx in [1.05, 1.25, 1.45, 1.65]:
        b.add_cylinder(bx, 1.01, -0.45, 0.05, 0.045, 0.28, segs=12)
    b = ctx.mb('SanBernardoCaps', green)
    for bx in [1.05, 1.25, 1.45, 1.65]:
        b.add_cylinder(bx, 1.29, -0.45, 0.045, 0.045, 0.03, segs=10)
    b = ctx.mb('WelcomeCard', cream)
    b.add_box(1.35, 1.03, -0.15, 0.20, 0.02, 0.14, uv_tile=0.5, rot_y=0.30)
    b = ctx.mb('CardFolios', charcoal)
    b.add_box(0.75, 1.03, -0.30, 0.22, 0.03, 0.16, uv_tile=0.5, rot_y=-0.20)
    b.add_box(0.75, 1.06, -0.30, 0.20, 0.02, 0.14, uv_tile=0.5, rot_y=-0.20)
    b = ctx.mb('ArtMonograph', cream)
    b.add_box(2.05, 1.03, -1.05, 0.42, 0.03, 0.30, uv_tile=0.5, rot_y=0.15)
    b = ctx.mb('NapkinPlate', porcelain)
    b.add_cylinder(0.35, 1.01, -1.35, 0.14, 0.14, 0.03, segs=18)
    b = ctx.mb('NapkinRoll', cream)
    b.add_cylinder(0.35, 1.04, -1.35, 0.05, 0.05, 0.16, segs=12, rot_z=1.5708)
