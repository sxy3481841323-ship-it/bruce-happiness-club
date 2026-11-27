import math


def build_salon_seating(ctx, mats):
    # ---------- Museum bordered rug ----------
    b = ctx.mb("SalonRug", mats["rug"])
    b.add_box(0.8, 0.02, -0.3, 13.8, 0.04, 13.6, uv_tile=0.0)
    b = ctx.mb("SalonRugFringe", mats["cream_pillow"])
    b.add_box(0.8, 0.02, -7.12, 13.8, 0.02, 0.10, uv_tile=0.0)
    b.add_box(0.8, 0.02, 6.52, 13.8, 0.02, 0.10, uv_tile=0.0)

    # ---------- Main sofa (boucle uv_tile=1.4 for lush woven texture) ----------
    b = ctx.mb("SofaPlinth", mats["walnut_solid"])
    b.add_box(-1.0, 0.10, -3.7, 5.4, 0.20, 1.55, uv_tile=1.4)
    b.add_box(-3.35, 0.10, -2.55, 1.6, 0.20, 1.55, uv_tile=1.4)
    b = ctx.mb("SofaSeat", mats["boucle"])
    b.add_rounded_box(-1.0, 0.42, -3.7, 5.2, 0.36, 1.45, bevel=0.10, uv_tile=1.3)
    b.add_rounded_box(-3.35, 0.42, -2.55, 1.55, 0.36, 1.45, bevel=0.10, uv_tile=1.3)
    b = ctx.mb("SofaBack", mats["boucle"])
    b.add_rounded_box(-1.0, 0.78, -4.30, 5.2, 0.64, 0.34, bevel=0.12, uv_tile=1.3)
    b.add_rounded_box(-4.05, 0.78, -2.55, 0.34, 0.64, 1.45, bevel=0.12, uv_tile=1.3)
    b = ctx.mb("SofaPillows", mats["cream_pillow"])
    for px in (-3.0, -1.6, -0.2, 1.2):
        b.add_rounded_box(px, 0.72, -4.05, 0.55, 0.42, 0.18, bevel=0.05, uv_tile=0.0)
    b = ctx.mb("SofaPillowsAccent", mats["burgundy"])
    b.add_rounded_box(-2.3, 0.72, -4.02, 0.50, 0.40, 0.16, bevel=0.05, uv_tile=0.0)
    b.add_rounded_box(0.5, 0.72, -4.02, 0.50, 0.40, 0.16, bevel=0.05, uv_tile=0.0)

    # ---------- Jeanneret lounge chair ----------
    b = ctx.mb("JeanneretLoungeChair", mats["walnut_solid"])
    b.add_box(-4.55, 0.22, -1.55, 0.70, 0.44, 0.70, uv_tile=0.0)
    b.add_box(-4.55, 0.62, -1.90, 0.70, 0.80, 0.10, uv_tile=0.0)
    b = ctx.mb("JeanneretLoungeChairSeat", mats["cognac_suede"])
    b.add_rounded_box(-4.55, 0.50, -1.55, 0.62, 0.12, 0.62, bevel=0.04, uv_tile=0.0)
    b.add_rounded_box(-4.55, 0.72, -1.88, 0.60, 0.55, 0.10, bevel=0.04, uv_tile=0.0)

    # ---------- Table A: travertine + marble ----------
    b = ctx.mb("SalonDrumTable", mats["travertine"])
    for px in (0.35, 1.95):
        b.add_cylinder(px, 0.04, -2.05, 0.34, 0.34, 0.64, segs=24)
    b = ctx.mb("SalonDrumTableBrass", mats["brass"])
    for px in (0.35, 1.95):
        b.add_cylinder(px, 0.66, -2.05, 0.36, 0.36, 0.04, segs=24)
    b = ctx.mb("SalonTableMarbleTop", mats["marble"])
    b.add_rounded_box(1.15, 0.72, -2.05, 2.45, 0.08, 1.32, bevel=0.05, uv_tile=0.0)

    # ---------- Table B: staggered companion ----------
    b = ctx.mb("SalonCocktailPedestal", mats["bronze_dark"])
    b.add_cylinder(3.10, 0.04, -1.18, 0.30, 0.30, 0.64, segs=24)
    b = ctx.mb("SalonCocktailPedestalBrass", mats["brass"])
    b.add_cylinder(3.10, 0.66, -1.18, 0.32, 0.32, 0.04, segs=24)
    b = ctx.mb("SalonCocktailTop", mats["walnut_fluted"])
    b.add_rounded_box(3.10, 0.72, -1.18, 1.36, 0.08, 1.36, bevel=0.05, uv_tile=0.0, rot_y=0.14)

    # ---------- Props on Table A ----------
    b = ctx.mb("SalonMonographs", mats["sheer_linen"])
    b.add_box(0.35, 0.775, -2.15, 0.42, 0.03, 0.30, uv_tile=0.0)
    b.add_box(0.35, 0.805, -2.15, 0.40, 0.03, 0.28, uv_tile=0.0)
    b = ctx.mb("SalonStonewareBowl", mats["ceramic_white"])
    b.add_lathe(1.92, 0.76, -2.25, [(0.02, 0.0), (0.16, 0.02), (0.20, 0.10), (0.18, 0.14)], segs=24)

    # Chilled tray + Evian bottles + tumblers
    b = ctx.mb("SalonChilledTray", mats["chrome"])
    b.add_rounded_box(1.10, 0.775, -1.92, 0.62, 0.03, 0.42, bevel=0.02, uv_tile=0.0)
    b = ctx.mb("EvianBottles1F", mats["glass"])
    for i, bx in enumerate((0.92, 1.10, 1.28)):
        b.add_cylinder(bx, 0.79, -1.92, 0.045, 0.045, 0.24, segs=16)
        b.add_cylinder(bx, 1.03, -1.92, 0.045, 0.020, 0.06, segs=16)
    b = ctx.mb("EvianLabels1F", mats["evian_label"])
    for bx in (0.92, 1.10, 1.28):
        b.add_cylinder(bx, 0.86, -1.92, 0.047, 0.047, 0.10, segs=16, cap_top=False, cap_bot=False)
    b = ctx.mb("SalonTumblers", mats["crystal_glass"])
    for tx in (0.98, 1.22):
        b.add_cylinder(tx, 0.79, -1.78, 0.035, 0.040, 0.10, segs=16)

    # ---------- Props on Table B: concierge pager + screen ----------
    px, py, pz = 3.10, 0.76, -1.18
    b = ctx.mb("ConciergePager1F", mats["charcoal"])
    b.add_rounded_box(px, py + 0.04, pz - 0.03, 0.30, 0.08, 0.16, bevel=0.015, uv_tile=0.0)
    b.add_box(px, py + 0.018, pz + 0.06, 0.30, 0.036, 0.08, uv_tile=0.0)
    b = ctx.mb("ConciergePager1F", mats["brass"])
    b.add_box(px, py + 0.084, pz - 0.03, 0.31, 0.01, 0.17, uv_tile=0.0)
    b = ctx.mb("ConciergeScreen1F", mats["concierge_screen"])
    # tilted upward (+Y) and forward (+Z) facing salon camera
    b.add_tri_raw((px - 0.12, py + 0.045, pz + 0.055), (px + 0.12, py + 0.045, pz + 0.055), (px + 0.12, py + 0.105, pz - 0.085), (0.0, 0.0), (1.0, 0.0), (1.0, 1.0))
    b.add_tri_raw((px - 0.12, py + 0.045, pz + 0.055), (px + 0.12, py + 0.105, pz - 0.085), (px - 0.12, py + 0.105, pz - 0.085), (0.0, 0.0), (1.0, 1.0), (0.0, 1.0))
