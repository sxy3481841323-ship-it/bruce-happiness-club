import math


def _lathe_profile(r_body, r_neck, h_body, h_shoulder, h_neck):
    pts = []
    pts.append((0.0, 0.0))
    pts.append((r_body * 0.55, 0.0))
    pts.append((r_body * 0.92, h_body * 0.10))
    pts.append((r_body, h_body * 0.35))
    pts.append((r_body * 0.98, h_body * 0.62))
    pts.append((r_body * 0.80, h_body * 0.85))
    pts.append((r_body * 0.55, h_body))
    pts.append((r_neck * 1.6, h_body + h_shoulder * 0.35))
    pts.append((r_neck * 1.15, h_body + h_shoulder * 0.75))
    pts.append((r_neck, h_body + h_shoulder))
    pts.append((r_neck, h_body + h_shoulder + h_neck))
    pts.append((r_neck * 0.92, h_body + h_shoulder + h_neck))
    return pts


def _build_bottle(ctx, name, mat, cx, cy, cz, scale=1.0):
    b = ctx.mb(name, mat)
    r_body = 0.068 * scale
    r_neck = 0.022 * scale
    h_body = 0.30 * scale
    h_shoulder = 0.09 * scale
    h_neck = 0.05 * scale
    prof = _lathe_profile(r_body, r_neck, h_body, h_shoulder, h_neck)
    b.add_lathe(cx, cy, cz, prof, segs=20)
    return b, h_body, h_shoulder, h_neck, r_neck


def _build_label(ctx, name, mat, cx, cy, cz, scale=1.0):
    b = ctx.mb(name, mat)
    r = 0.070 * scale
    h = 0.18 * scale
    y0 = cy + 0.10 * scale
    b.add_cylinder(cx, y0, cz, r, r, h, segs=20, cap_top=False, cap_bot=False)
    return b


def _build_cap(ctx, name, mat, cx, cy, cz, scale=1.0):
    b = ctx.mb(name, mat)
    r = 0.024 * scale
    h = 0.035 * scale
    b.add_cylinder(cx, cy, cz, r, r * 0.95, h, segs=16)
    return b


def _build_tumbler(ctx, name, mat, cx, cy, cz, scale=1.0):
    b = ctx.mb(name, mat)
    r_bot = 0.038 * scale
    r_top = 0.048 * scale
    h = 0.11 * scale
    b.add_cylinder(cx, cy, cz, r_bot, r_top, h, segs=8, cap_top=False, cap_bot=True)
    b.add_cylinder(cx, cy + h - 0.004, cz, r_top * 0.92, r_top * 0.92, 0.004, segs=8,
                   cap_top=False, cap_bot=False)
    return b


def build_salon_seating(ctx, mats):
    # ------------------------------------------------------------------
    # 1F Salon Sofa: Low-Slung Organic Camaleonda Cloud Bouclé Sofa
    # ------------------------------------------------------------------
    plinth = ctx.mb("SofaPlinth", mats["walnut_solid"])
    plinth.add_rounded_box(1.7, 0.14, -3.1, 6.6, 0.20, 6.6, bevel=0.03, uv_tile=2.0)
    plinth.add_rounded_box(-1.0, 0.14, -1.05, 1.6, 0.20, 3.1, bevel=0.03, uv_tile=2.0)

    seat = ctx.mb("SofaSeat", mats["boucle"])
    seat_xs = [-0.6, 0.9, 2.4, 3.9]
    for sx in seat_xs:
        seat.add_rounded_box(sx, 0.66, -5.4, 1.45, 0.84, 1.55, bevel=0.16, uv_tile=1.2)
    for sx in seat_xs:
        seat.add_rounded_box(sx, 0.66, -3.7, 1.45, 0.84, 1.55, bevel=0.16, uv_tile=1.2)
    seat.add_rounded_box(-1.0, 0.66, -1.9, 1.45, 0.84, 1.55, bevel=0.16, uv_tile=1.2)
    seat.add_rounded_box(-1.0, 0.66, -0.3, 1.45, 0.84, 1.55, bevel=0.16, uv_tile=1.2)

    back = ctx.mb("SofaBack", mats["boucle"])
    for sx in seat_xs:
        back.add_rounded_box(sx, 1.60, -6.15, 1.45, 1.02, 0.55, bevel=0.22, uv_tile=1.2)
    back.add_rounded_box(-1.75, 1.60, -3.7, 0.55, 1.02, 1.55, bevel=0.22, uv_tile=1.2)
    back.add_rounded_box(-1.75, 1.60, -1.9, 0.55, 1.02, 1.55, bevel=0.22, uv_tile=1.2)
    back.add_rounded_box(-1.75, 1.60, -0.3, 0.55, 1.02, 1.55, bevel=0.22, uv_tile=1.2)
    back.add_rounded_box(5.05, 1.60, -3.7, 0.55, 1.02, 1.55, bevel=0.22, uv_tile=1.2)
    back.add_rounded_box(5.05, 1.60, -5.4, 0.55, 1.02, 1.55, bevel=0.22, uv_tile=1.2)
    for sx in seat_xs:
        back.add_cylinder(sx, 1.05, -5.85, 0.28, 0.28, 1.35, segs=16, rot_z=math.pi / 2.0)
    back.add_cylinder(-1.55, 1.05, -1.1, 0.28, 0.28, 2.6, segs=16, rot_x=math.pi / 2.0)

    # ------------------------------------------------------------------
    # Borderless Alpaca Rug
    # ------------------------------------------------------------------
    br = ctx.mb("SalonRug", mats["rug"])
    br.add_rounded_box(3.2, 0.02, -0.2, 11.8, 0.04, 13.2, bevel=0.015, uv_tile=5.5)

    # ------------------------------------------------------------------
    # 3 asymmetrical cognac suede / cream silk / oxblood pebble cushions
    # ------------------------------------------------------------------
    ctx.mb("SofaPillows", mats["cognac_suede"]).add_sphere(0.2, 1.48, -5.1, 0.62, 0.34, 0.42, rings=14, segs=20)
    ctx.mb("SofaPillowsCream", mats["cream_pillow"]).add_sphere(3.9, 1.45, -5.2, 0.58, 0.32, 0.40, rings=14, segs=20)
    ctx.mb("SofaPillowsBurgundy", mats["burgundy"]).add_sphere(-0.3, 1.46, -1.6, 0.55, 0.30, 0.38, rings=14, segs=20)

    # ------------------------------------------------------------------
    # Jeanneret lounge chair (7.2, -6.0)
    # ------------------------------------------------------------------
    jx, jz = 7.2, -6.0
    bj = ctx.mb("JeanneretLoungeChair", mats["walnut_solid"])
    bj.add_box(jx, 0.42, jz, 0.62, 0.06, 0.58, uv_tile=1.0)
    bj.add_box(jx, 0.78, jz - 0.26, 0.62, 0.62, 0.05, uv_tile=1.0)
    bj.add_box(jx - 0.31, 0.42, jz, 0.05, 0.06, 0.58, uv_tile=1.0)
    bj.add_box(jx + 0.31, 0.42, jz, 0.05, 0.06, 0.58, uv_tile=1.0)
    for lx in (jx - 0.28, jx + 0.28):
        for lz in (jz - 0.24, jz + 0.24):
            bj.add_cylinder(lx, 0.0, lz, 0.028, 0.024, 0.40, segs=10)
    bjc = ctx.mb("JeanneretCushion", mats["cognac_suede"])
    bjc.add_rounded_box(jx, 0.48, jz + 0.02, 0.54, 0.08, 0.50, bevel=0.03, uv_tile=1.0)

    # ------------------------------------------------------------------
    # Drum table (9.1, -5.2)
    # ------------------------------------------------------------------
    dx, dz = 9.1, -5.2
    bd = ctx.mb("SalonDrumTable", mats["travertine"])
    bd.add_cylinder(dx, 0.0, dz, 0.34, 0.34, 0.52, segs=24)
    bd.add_cylinder(dx, 0.52, dz, 0.36, 0.36, 0.04, segs=24)
    bdb = ctx.mb("SalonDrumTableBrass", mats["brass"])
    bdb.add_cylinder(dx, 0.0, dz, 0.345, 0.345, 0.02, segs=24)
    bdb.add_cylinder(dx, 0.50, dz, 0.345, 0.345, 0.02, segs=24)

    # ==================================================================
    # UPGRADED LAYERED 1F SALON TABLE ENSEMBLE
    # ==================================================================
    tx, tz = 4.25, -1.70

    # --- Fluted travertine twin curved pedestals ---
    bp = ctx.mb("SalonTablePedestals", mats["travertine"])
    for px in (3.35, 5.15):
        n_flutes = 14
        for i in range(n_flutes):
            ang = (i / n_flutes) * math.tau
            fx = px + math.cos(ang) * 0.20
            fz = tz + math.sin(ang) * 0.20
            bp.add_cylinder(fx, 0.0, fz, 0.045, 0.045, 0.78, segs=8)
        bp.add_cylinder(px, 0.0, tz, 0.16, 0.16, 0.78, segs=20)
        bp.add_cylinder(px, 0.0, tz, 0.26, 0.22, 0.06, segs=20)

    # --- Brass plinth rings ---
    bpr = ctx.mb("SalonTableBrassRings", mats["brass"])
    for px in (3.35, 5.15):
        bpr.add_cylinder(px, 0.78, tz, 0.24, 0.24, 0.03, segs=24)
        bpr.add_cylinder(px, 0.02, tz, 0.27, 0.27, 0.02, segs=24)

    # --- Bookmatched Calacatta Marble slab top ---
    bm = ctx.mb("SalonTableMarbleTop", mats["marble"])
    bm.add_box(tx, 0.86, tz, 3.05, 0.10, 1.62, uv_tile=1.0)
    bm.add_box(tx, 0.805, tz, 3.07, 0.012, 1.64, uv_tile=1.0)

    # --- Overlapping higher Smoked-Bronze & Marble Cocktail Tier ---
    cx2, cz2 = 5.85, -2.35
    bcb = ctx.mb("SalonCocktailPlinth", mats["bronze_dark"])
    n_flutes = 16
    for i in range(n_flutes):
        ang = (i / n_flutes) * math.tau
        fx = cx2 + math.cos(ang) * 0.22
        fz = cz2 + math.sin(ang) * 0.22
        bcb.add_cylinder(fx, 0.0, fz, 0.05, 0.05, 1.02, segs=8)
    bcb.add_cylinder(cx2, 0.0, cz2, 0.18, 0.18, 1.02, segs=20)
    bcb.add_cylinder(cx2, 0.0, cz2, 0.30, 0.26, 0.06, segs=20)

    bgc = ctx.mb("SalonCocktailCollar", mats["brass"])
    bgc.add_cylinder(cx2, 1.02, cz2, 0.26, 0.26, 0.03, segs=24)

    bct = ctx.mb("SalonCocktailTop", mats["marble"])
    bct.add_box(cx2, 1.08, cz2, 1.45, 0.08, 1.45, uv_tile=1.0)
    bct.add_box(cx2, 1.035, cz2, 1.47, 0.012, 1.47, uv_tile=1.0)

    # --- Stacked silk-linen exhibition monographs + carved stoneware bowl ---
    bmono = ctx.mb("SalonMonographs", mats["cream_pillow"])
    bmono.add_box(3.55, 0.945, -1.30, 0.42, 0.05, 0.32, uv_tile=1.0)
    bmono.add_box(3.57, 0.995, -1.32, 0.40, 0.05, 0.30, uv_tile=1.0)
    bmono.add_box(3.54, 1.045, -1.28, 0.38, 0.05, 0.28, uv_tile=1.0)

    bbowl = ctx.mb("SalonStonewareBowl", mats["travertine"])
    bbowl.add_lathe(4.95, 0.91, -1.30, [
        (0.0, 0.0),
        (0.10, 0.0),
        (0.14, 0.04),
        (0.16, 0.10),
        (0.15, 0.14),
        (0.13, 0.15),
    ], segs=20)

    # ==================================================================
    # CHILLED BRUSHED-SILVER TRAY WITH 3 EVIAN BOTTLES + 2 TUMBLERS
    # ==================================================================
    tray_x, tray_y, tray_z = 3.95, 0.925, -1.58
    bt = ctx.mb("SalonChilledTray", mats["chrome"])
    bt.add_box(tray_x, tray_y, tray_z, 0.62, 0.03, 0.42, uv_tile=1.0)
    bt.add_box(tray_x, tray_y + 0.02, tray_z - 0.20, 0.62, 0.04, 0.02, uv_tile=1.0)
    bt.add_box(tray_x, tray_y + 0.02, tray_z + 0.20, 0.62, 0.04, 0.02, uv_tile=1.0)
    bt.add_box(tray_x - 0.30, tray_y + 0.02, tray_z, 0.02, 0.04, 0.42, uv_tile=1.0)
    bt.add_box(tray_x + 0.30, tray_y + 0.02, tray_z, 0.02, 0.04, 0.42, uv_tile=1.0)

    bottle_positions = [
        (tray_x - 0.18, tray_y + 0.015, tray_z - 0.06),
        (tray_x + 0.02, tray_y + 0.015, tray_z + 0.08),
        (tray_x + 0.20, tray_y + 0.015, tray_z - 0.04),
    ]
    for i, (bx, by, bz) in enumerate(bottle_positions):
        _, h_body, h_shoulder, h_neck, r_neck = _build_bottle(
            ctx, "EvianBottles1F", mats["crystal_glass"], bx, by, bz, scale=1.18)
        _build_label(ctx, "EvianLabels1F", mats["evian_label"], bx, by, bz, scale=1.18)
        cap_y = by + h_body + h_shoulder + h_neck
        _build_cap(ctx, "EvianBottles1F", mats["chrome"], bx, cap_y, bz, scale=1.18)

    _build_tumbler(ctx, "SalonTumblers", mats["crystal_glass"],
                   tray_x - 0.22, tray_y + 0.015, tray_z + 0.13, scale=1.12)
    _build_tumbler(ctx, "SalonTumblers", mats["crystal_glass"],
                   tray_x + 0.24, tray_y + 0.015, tray_z + 0.13, scale=1.12)

    # ==================================================================
    # 1F HOUSE CONCIERGE INTERCOM PAGER (angled cleanly toward +Z/+Y viewer)
    # ==================================================================
    px, py, pz = 5.82, 1.13, -2.22

    bpag = ctx.mb("ConciergePager1F", mats["charcoal"])
    bpag.add_box(px, py + 0.04, pz - 0.04, 0.32, 0.09, 0.16, uv_tile=1.0)
    bpag.add_box(px, py + 0.018, pz + 0.07, 0.32, 0.042, 0.08, uv_tile=1.0)

    btrim = ctx.mb("ConciergePager1F", mats["brass"])
    btrim.add_box(px, py + 0.088, pz - 0.04, 0.33, 0.012, 0.17, uv_tile=1.0)

    # Tilted touchscreen facing toward +Z (front camera) and +Y (upward)
    bs = ctx.mb("ConciergeScreen1F", mats["concierge_screen"])
    bs.add_tri_raw((px - 0.13, py + 0.048, pz + 0.055), (px + 0.13, py + 0.048, pz + 0.055), (px + 0.13, py + 0.098, pz - 0.085), (0.0, 0.0), (1.0, 0.0), (1.0, 1.0))
    bs.add_tri_raw((px - 0.13, py + 0.048, pz + 0.055), (px + 0.13, py + 0.098, pz - 0.085), (px - 0.13, py + 0.098, pz - 0.085), (0.0, 0.0), (1.0, 1.0), (0.0, 1.0))

    bbtn = ctx.mb("ConciergePager1F", mats["brass"])
    for bx in (px - 0.085, px, px + 0.085):
        bbtn.add_cylinder(bx, py + 0.040, pz + 0.082, 0.014, 0.014, 0.012, segs=12)

    bhs = ctx.mb("ConciergePager1F", mats["chrome"])
    bhs.add_box(px, py + 0.102, pz - 0.10, 0.24, 0.018, 0.026, uv_tile=1.0)
