import math

def build_salon_seating(ctx, mats):
    # 1. Plush Cream Wool Carpet
    rug = ctx.mb("SalonRug", mats["rug"])
    rug.add_rounded_box(cx=3.2, cy=0.02, cz=-0.2, sx=11.8, sy=0.04, sz=13.2, bevel=0.015, uv_tile=5.0)

    # 2. Curved / L-Shaped Italian Cream Boucle Modular Sofa
    # Walnut plinth base
    base = ctx.mb("SofaPlinth", mats["walnut_solid"])
    # L-shape: long section along X (back at Z=-6.8), short section along Z (back at X=-1.8)
    # Long section plinth
    base.add_rounded_box(cx=1.7, cy=0.16, cz=-6.2, sx=7.0, sy=0.24, sz=1.2, bevel=0.03, uv_tile=2.0)
    # Short section plinth (L return)
    base.add_rounded_box(cx=-1.2, cy=0.16, cz=-3.0, sx=1.2, sy=0.24, sz=5.2, bevel=0.03, uv_tile=2.0)

    # Seat cushions (plump chubby rounded boxes)
    seat = ctx.mb("SofaSeat", mats["boucle"])
    # Long section seats
    for i in range(3):
        x = -0.5 + i * 2.2
        seat.add_rounded_box(cx=x, cy=0.76, cz=-6.0, sx=2.1, sy=0.97, sz=1.5, bevel=0.18, uv_tile=1.5)
    # Short section seats
    for i in range(2):
        z = -4.2 + i * 2.2
        seat.add_rounded_box(cx=-1.2, cy=0.76, cz=z, sx=1.5, sy=0.97, sz=2.1, bevel=0.18, uv_tile=1.5)

    # Sculptural curved backrest
    back = ctx.mb("SofaBack", mats["boucle"])
    # Long back
    back.add_rounded_box(cx=1.7, cy=1.9, cz=-6.55, sx=7.0, sy=1.3, sz=0.5, bevel=0.2, uv_tile=1.5)
    # Short back
    back.add_rounded_box(cx=-1.55, cy=1.9, cz=-3.0, sx=0.5, sy=1.3, sz=5.2, bevel=0.2, uv_tile=1.5)

    # Wide rounded armrests
    arm = ctx.mb("SofaArm", mats["boucle"])
    # Right arm of long section
    arm.add_rounded_box(cx=5.0, cy=1.1, cz=-6.0, sx=0.6, sy=1.0, sz=1.6, bevel=0.2, uv_tile=1.5)
    # Front arm of short section
    arm.add_rounded_box(cx=-1.2, cy=1.1, cz=-0.4, sx=1.6, sy=1.0, sz=0.6, bevel=0.2, uv_tile=1.5)

    # Throw pillows - burgundy and cream, tilted along backrest
    pil_burg = ctx.mb("PillowBurgundy", mats["burgundy"])
    pil_cream = ctx.mb("PillowCream", mats["cream_pillow"])
    # Long back pillows
    for i in range(3):
        x = -0.3 + i * 2.2
        pil_burg.add_rounded_box(cx=x, cy=1.55, cz=-6.15, sx=0.7, sy=0.7, sz=0.25, bevel=0.1, uv_tile=1.0)
        pil_cream.add_rounded_box(cx=x + 1.0, cy=1.5, cz=-6.1, sx=0.65, sy=0.65, sz=0.22, bevel=0.1, uv_tile=1.0)
    # Short back pillows
    for i in range(2):
        z = -4.0 + i * 2.2
        pil_burg.add_rounded_box(cx=-1.35, cy=1.55, cz=z, sx=0.25, sy=0.7, sz=0.7, bevel=0.1, uv_tile=1.0)
        pil_cream.add_rounded_box(cx=-1.3, cy=1.5, cz=z + 1.0, sx=0.22, sy=0.65, sz=0.65, bevel=0.1, uv_tile=1.0)

    # 3. Boucle Swivel Lounge Chair at X=7.2, Z=-6.2
    chair_angle = math.atan2(-1.6 - (-6.2), 4.2 - 7.2)  # toward coffee table
    # Brass swivel pedestal
    ped = ctx.mb("ChairPedestal", mats["brass"])
    ped.add_cylinder(cx=7.2, y0=0.04, cz=-6.2, r_bot=0.45, r_top=0.35, height=0.35, segs=24)
    ped.add_cylinder(cx=7.2, y0=0.39, cz=-6.2, r_bot=0.12, r_top=0.12, height=0.25, segs=16)
    # Chair seat
    ch_seat = ctx.mb("ChairSeat", mats["boucle"])
    ch_seat.add_rounded_box(cx=7.2, cy=0.85, cz=-6.2, sx=1.3, sy=0.5, sz=1.3, bevel=0.18, uv_tile=1.5, rot_y=chair_angle)
    # Chair back
    ch_back = ctx.mb("ChairBack", mats["boucle"])
    bx = 7.2 + math.sin(chair_angle) * 0.55
    bz = -6.2 + math.cos(chair_angle) * 0.55
    ch_back.add_rounded_box(cx=bx, cy=1.45, cz=bz, sx=1.3, sy=0.9, sz=0.35, bevel=0.15, uv_tile=1.5, rot_y=chair_angle)
    # Chair armrests
    ch_arm = ctx.mb("ChairArm", mats["boucle"])
    for side in [-1, 1]:
        ax = 7.2 + math.cos(chair_angle) * side * 0.6
        az = -6.2 - math.sin(chair_angle) * side * 0.6
        ch_arm.add_rounded_box(cx=ax, cy=1.05, cz=az, sx=0.3, sy=0.45, sz=1.2, bevel=0.12, uv_tile=1.5, rot_y=chair_angle)

    # Travertine drum side table at X=9.2, Z=-5.4
    side = ctx.mb("SideTable", mats["travertine"])
    side.add_cylinder(cx=9.2, y0=0.04, cz=-5.4, r_bot=0.42, r_top=0.42, height=0.55, segs=28)

    # 4. Twin Overlapping Sculptural Coffee Tables
    # Low oval travertine table at X=4.2, Z=-1.6
    # Three fluted walnut legs
    legs = ctx.mb("CoffeeLegs", mats["walnut_solid"])
    for i in range(3):
        ang = i * (2 * math.pi / 3) + math.pi / 6
        lx = 4.2 + math.cos(ang) * 0.55
        lz = -1.6 + math.sin(ang) * 0.55
        legs.add_cylinder(cx=lx, y0=0.04, cz=lz, r_bot=0.09, r_top=0.09, height=0.85, segs=12)
    # Oval travertine top
    top1 = ctx.mb("CoffeeTop1", mats["travertine"])
    top1.add_rounded_box(cx=4.2, cy=0.89, cz=-1.6, sx=2.2, sy=0.12, sz=1.4, bevel=0.06, uv_tile=1.5)

    # Higher brass-ring & travertine pedestal cocktail table at X=5.8, Z=-2.4
    ped2 = ctx.mb("CocktailPedestal", mats["brass"])
    ped2.add_cylinder(cx=5.8, y0=0.04, cz=-2.4, r_bot=0.35, r_top=0.3, height=0.9, segs=24)
    # Brass ring detail
    ped2.add_cylinder(cx=5.8, y0=0.5, cz=-2.4, r_bot=0.38, r_top=0.38, height=0.06, segs=24)
    # Travertine top
    top2 = ctx.mb("CocktailTop", mats["travertine"])
    top2.add_cylinder(cx=5.8, y0=0.94, cz=-2.4, r_bot=0.75, r_top=0.75, height=0.12, segs=32)

    # Stacked art books
    books = ctx.mb("ArtBooks", mats["burgundy"])
    books.add_rounded_box(cx=5.6, cy=1.10, cz=-2.3, sx=0.55, sy=0.06, sz=0.42, bevel=0.01, uv_tile=1.0)
    books2 = ctx.mb("ArtBooks2", mats["cream_pillow"])
    books2.add_rounded_box(cx=5.65, cy=1.16, cz=-2.35, sx=0.5, sy=0.05, sz=0.38, bevel=0.01, uv_tile=1.0)

    # Sculptural ceramic vase
    vase = ctx.mb("CeramicVase", mats["cream_pillow"])
    profile = [
        (0.0, 0.0),
        (0.12, 0.0),
        (0.16, 0.05),
        (0.18, 0.15),
        (0.14, 0.28),
        (0.08, 0.38),
        (0.07, 0.45),
        (0.09, 0.48),
        (0.0, 0.48),
    ]
    vase.add_lathe(cx=6.1, y0=1.06, cz=-2.5, profile=profile, segs=24)
