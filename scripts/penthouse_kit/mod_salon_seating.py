import math


def build_salon_seating(ctx, mats):
    # ------------------------------------------------------------------
    # 1. Borderless Hand-Knotted Alpaca Rug
    # ------------------------------------------------------------------
    rug = ctx.mb("SalonRug", mats["rug"])
    rug.add_rounded_box(3.2, 0.02, -0.2, 11.8, 0.04, 13.2, bevel=0.015, uv_tile=5.5)

    # ------------------------------------------------------------------
    # 2. Low-Slung Organic Cloud Modular Bouclé Sofa
    #    X in [-1.8, 5.2], Z in [-6.8, 0.6], Y in [0, 2.4]
    # ------------------------------------------------------------------
    # --- Recessed smoked walnut plinth (Y 0.04..0.24) ---
    plinth = ctx.mb("SofaPlinth", mats["walnut_solid"])
    # main body plinth
    plinth.add_rounded_box(1.7, 0.14, -3.1, 6.6, 0.20, 6.6, bevel=0.03, uv_tile=2.0)
    # L-chaise wing plinth (X=-1.0, Z=-2.6..0.5)
    plinth.add_rounded_box(-1.0, 0.14, -1.05, 1.6, 0.20, 3.1, bevel=0.03, uv_tile=2.0)

    # --- Plump chamfered pillowed seat modules (Y 0.24..1.08) ---
    seat = ctx.mb("SofaSeat", mats["boucle"])
    # main run of seat cushions (segmented, plump)
    seat_xs = [-0.6, 0.9, 2.4, 3.9]
    for sx in seat_xs:
        seat.add_rounded_box(sx, 0.66, -5.4, 1.45, 0.84, 1.55, bevel=0.16, uv_tile=1.2)
    # front row of seat cushions (deeper)
    for sx in seat_xs:
        seat.add_rounded_box(sx, 0.66, -3.7, 1.45, 0.84, 1.55, bevel=0.16, uv_tile=1.2)
    # L-chaise wing seat cushions
    seat.add_rounded_box(-1.0, 0.66, -1.9, 1.45, 0.84, 1.55, bevel=0.16, uv_tile=1.2)
    seat.add_rounded_box(-1.0, 0.66, -0.3, 1.45, 0.84, 1.55, bevel=0.16, uv_tile=1.2)

    # --- Sculpted rounded wraparound back (Y 1.08..2.12) ---
    back = ctx.mb("SofaBack", mats["boucle"])
    # rear back cushions (soft segmented bolster tufts)
    for sx in seat_xs:
        back.add_rounded_box(sx, 1.60, -6.15, 1.45, 1.02, 0.55, bevel=0.22, uv_tile=1.2)
    # side back cushions (left wing)
    back.add_rounded_box(-1.75, 1.60, -3.7, 0.55, 1.02, 1.55, bevel=0.22, uv_tile=1.2)
    back.add_rounded_box(-1.75, 1.60, -1.9, 0.55, 1.02, 1.55, bevel=0.22, uv_tile=1.2)
    back.add_rounded_box(-1.75, 1.60, -0.3, 0.55, 1.02, 1.55, bevel=0.22, uv_tile=1.2)
    # right side back cushion
    back.add_rounded_box(5.05, 1.60, -3.7, 0.55, 1.02, 1.55, bevel=0.22, uv_tile=1.2)
    back.add_rounded_box(5.05, 1.60, -5.4, 0.55, 1.02, 1.55, bevel=0.22, uv_tile=1.2)
    # soft bolster tufts across the back (rounded cylinders)
    for sx in seat_xs:
        back.add_cylinder(sx, 1.05, -5.85, 0.28, 0.28, 1.35, segs=16, rot_z=math.pi / 2.0)
    # L-corner back bolster
    back.add_cylinder(-1.55, 1.05, -1.1, 0.28, 0.28, 2.6, segs=16, rot_x=math.pi / 2.0)

    # --- ONLY 3 Asymmetrical Pebble & Cloud Throw Pillows ---
    pillows = ctx.mb("SofaPillows", mats["cognac_suede"])
    # 1. tilted cognac nubuck pebble bolster around (0.2, 1.48, -5.1)
    pillows.add_sphere(0.2, 1.48, -5.1, 0.62, 0.34, 0.42, rings=14, segs=20)
    # 2. soft cream/ivory linen bolster around (3.9, 1.45, -5.2)
    pillows_cream = ctx.mb("SofaPillowsCream", mats["cream_pillow"])
    pillows_cream.add_sphere(3.9, 1.45, -5.2, 0.58, 0.32, 0.40, rings=14, segs=20)
    # 3. muted oxblood cashmere cushion tucked into L-corner around (-0.3, 1.46, -1.6)
    pillows_burg = ctx.mb("SofaPillowsBurgundy", mats["burgundy"])
    pillows_burg.add_sphere(-0.3, 1.46, -1.6, 0.55, 0.30, 0.38, rings=14, segs=20)

    # ------------------------------------------------------------------
    # 3. Pierre Jeanneret-Inspired Sculpted Walnut & Bouclé Lounge Chair
    #    X=7.2, Z=-6.0, angled toward center
    # ------------------------------------------------------------------
    chair_angle = math.radians(-35.0)
    ca = math.cos(chair_angle)
    sa = math.sin(chair_angle)
    cx0, cz0 = 7.2, -6.0

    def rot(px, pz):
        return (cx0 + px * ca - pz * sa, cz0 + px * sa + pz * ca)

    # --- Angled solid walnut V-frame side legs ---
    legs = ctx.mb("LoungeChairLegs", mats["walnut_solid"])
    for side in (-1.0, 1.0):
        # V-frame: two angled struts meeting at bottom
        lx = side * 0.62
        # front strut
        p0 = rot(lx, 0.55)
        p1 = rot(lx * 0.55, -0.55)
        legs.add_cylinder(p0[0], 0.0, p0[1], 0.055, 0.055, 0.95, segs=10,
                          rot_x=math.radians(18.0 * side), rot_z=math.radians(10.0))
        # rear strut
        p2 = rot(lx, -0.55)
        legs.add_cylinder(p2[0], 0.0, p2[1], 0.055, 0.055, 0.95, segs=10,
                          rot_x=math.radians(-18.0 * side), rot_z=math.radians(-10.0))
        # cross rail
        legs.add_cylinder(p1[0], 0.42, p1[1], 0.045, 0.045, 0.9, segs=8,
                          rot_z=math.pi / 2.0)

    # --- Plump chamfered bouclé seat/back cushion ---
    chair_cush = ctx.mb("LoungeChairCushion", mats["boucle"])
    seat_c = rot(0.0, 0.0)
    chair_cush.add_rounded_box(seat_c[0], 0.62, seat_c[1], 1.15, 0.42, 1.15,
                               bevel=0.14, uv_tile=1.0, rot_y=chair_angle)
    back_c = rot(0.0, -0.52)
    chair_cush.add_rounded_box(back_c[0], 1.18, back_c[1], 1.15, 0.72, 0.32,
                               bevel=0.14, uv_tile=1.0, rot_y=chair_angle)

    # --- Small Roman travertine drum table at (9.1, 0.04, -5.2) ---
    drum = ctx.mb("TravertineDrumTable", mats["travertine"])
    drum.add_cylinder(9.1, 0.04, -5.2, 0.42, 0.40, 0.52, segs=24)
    drum.add_cylinder(9.1, 0.56, -5.2, 0.44, 0.44, 0.05, segs=24)

    # ------------------------------------------------------------------
    # 4. Twin Sculptural Honed Travertine & Bronze Plinth Coffee Tables
    #    X=4.2, Z=-1.6
    # ------------------------------------------------------------------
    # --- Low oval/capsule honed travertine slab (Y 0.04..0.88) ---
    trav = ctx.mb("TravertineCoffeeTable", mats["travertine"])
    # two wide curved fluted travertine drums
    trav.add_cylinder(3.4, 0.04, -1.6, 0.55, 0.52, 0.72, segs=28)
    trav.add_cylinder(5.0, 0.04, -1.6, 0.55, 0.52, 0.72, segs=28)
    # fluting detail (thin vertical ridges)
    for i in range(12):
        ang = (i / 12.0) * math.pi * 2.0
        fx = 3.4 + math.cos(ang) * 0.54
        fz = -1.6 + math.sin(ang) * 0.54
        trav.add_cylinder(fx, 0.06, fz, 0.025, 0.025, 0.68, segs=6)
        fx2 = 5.0 + math.cos(ang) * 0.54
        fz2 = -1.6 + math.sin(ang) * 0.54
        trav.add_cylinder(fx2, 0.06, fz2, 0.025, 0.025, 0.68, segs=6)
    # oval capsule slab top
    trav.add_rounded_box(4.2, 0.84, -1.6, 2.6, 0.08, 1.35, bevel=0.04, uv_tile=1.5)

    # --- Overlapping higher dark-bronze & cream marble cocktail table ---
    bronze = ctx.mb("BronzeCocktailTable", mats["bronze_dark"])
    # bronze plinth base
    bronze.add_rounded_box(5.9, 0.30, -2.4, 1.15, 0.52, 1.15, bevel=0.05, uv_tile=1.0)
    # cream marble top (use travertine as cream marble proxy)
    bronze_top = ctx.mb("BronzeCocktailTop", mats["travertine"])
    bronze_top.add_rounded_box(5.9, 1.10, -2.4, 1.35, 0.08, 1.35, bevel=0.04, uv_tile=1.2)

    # --- Styling: two linen-bound exhibition monographs + stoneware bowl ---
    books = ctx.mb("CoffeeTableBooks", mats["cream_pillow"])
    books.add_rounded_box(5.55, 1.17, -2.55, 0.42, 0.06, 0.32, bevel=0.01, uv_tile=0.5)
    books2 = ctx.mb("CoffeeTableBooks2", mats["cognac_suede"])
    books2.add_rounded_box(5.62, 1.24, -2.50, 0.40, 0.06, 0.30, bevel=0.01, uv_tile=0.5)

    # low shallow stoneware bowl (add_lathe)
    bowl = ctx.mb("StonewareBowl", mats["travertine"])
    bowl_profile = [
        (0.00, 0.00),
        (0.18, 0.00),
        (0.22, 0.04),
        (0.24, 0.10),
        (0.22, 0.14),
        (0.18, 0.15),
        (0.16, 0.13),
        (0.15, 0.08),
        (0.14, 0.04),
        (0.00, 0.03),
    ]
    bowl.add_lathe(6.25, 1.14, -2.25, bowl_profile, segs=24)
