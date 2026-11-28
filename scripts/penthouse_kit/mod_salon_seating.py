from penthouse_kit.cushion_helper import add_designer_pillow


def build_salon_seating(ctx, mats):
    # ---------------- RUG (single UV, no grid) ----------------
    b = ctx.mb("SalonRugPlinth", mats["cream_pillow"])
    b.add_box(0.8, 0.018, -0.3, 13.8, 0.036, 13.6)

    b = ctx.mb("SalonRug", mats["rug"])
    b.add_quad((-6.1, 0.038, 6.5), (7.7, 0.038, 6.5),
               (7.7, 0.038, -7.1), (-6.1, 0.038, -7.1),
               uv_scale=(1.0, 1.0))

    # ---------------- SOFA ----------------
    b = ctx.mb("SofaPlinth", mats["rift_oak"])
    b.add_rounded_box(-1.0, 0.20, -3.7, 4.6, 0.40, 1.30, bevel=0.05)
    b.add_rounded_box(-3.35, 0.20, -2.55, 1.30, 0.40, 2.30, bevel=0.05)

    b = ctx.mb("SofaSeat", mats["boucle"])
    b.add_rounded_box(-1.0, 0.52, -3.7, 4.5, 0.24, 1.20, bevel=0.08)
    b.add_rounded_box(-3.35, 0.52, -2.55, 1.20, 0.24, 2.20, bevel=0.08)

    b = ctx.mb("SofaBack", mats["boucle"])
    b.add_rounded_box(-1.0, 0.86, -4.28, 4.5, 0.62, 0.22, bevel=0.08)
    b.add_rounded_box(-3.95, 0.86, -2.55, 0.22, 0.62, 2.20, bevel=0.08)

    # ---------------- JEANNERET LOUNGE CHAIR ----------------
    b = ctx.mb("JeanneretLoungeChair", mats["rift_oak"])
    cx, cz = -4.55, -1.55
    b.add_box(cx, 0.30, cz, 0.62, 0.06, 0.62)
    b.add_box(cx - 0.28, 0.55, cz, 0.06, 0.55, 0.62)
    b.add_box(cx + 0.28, 0.55, cz, 0.06, 0.55, 0.62)
    b.add_box(cx, 0.55, cz - 0.28, 0.62, 0.55, 0.06)
    b.add_box(cx, 0.55, cz + 0.28, 0.62, 0.55, 0.06)
    b.add_box(cx, 0.86, cz - 0.28, 0.62, 0.62, 0.06)

    b = ctx.mb("JeanneretCushion", mats["slate_linen"])
    b.add_rounded_box(cx, 0.36, cz, 0.56, 0.10, 0.56, bevel=0.04)

    b = ctx.mb("JeanneretBackCushion", mats["slate_linen"])
    b.add_rounded_box(cx, 0.62, cz - 0.24, 0.56, 0.42, 0.10, bevel=0.04)

    # ---------------- PILLOWS (2+1 on sofa, 1 on chair) ----------------
    def _pillow(name, pos, fab, pipe, w=0.52, h=0.44, thick=0.16, yaw=0.0, tilt=-0.26):
        add_designer_pillow(
            ctx.mb(name, mats[fab]),
            ctx.mb(name + "Pipe", mats[pipe]),
            pos[0], pos[1], pos[2],
            w=w, h=h, thick=thick, yaw=yaw, tilt=tilt,
        )

    _pillow("SofaPillowA", (-3.05, 0.72, -3.92), "cream_pillow", "brass", w=0.58, h=0.48, thick=0.18, yaw=-0.42, tilt=-0.28)
    _pillow("SofaPillowB", (-2.55, 0.69, -3.75), "slate_linen", "cream_pillow", w=0.48, h=0.42, thick=0.16, yaw=0.22, tilt=-0.30)
    _pillow("SofaPillowC", (0.62, 0.68, -3.92), "burgundy", "brass", w=0.50, h=0.35, thick=0.15, yaw=-0.16, tilt=-0.26)
    _pillow("JeanneretLumbar", (cx, 0.50, cz + 0.10), "cream_pillow", "brass", w=0.40, h=0.26, thick=0.12, yaw=0.0, tilt=-0.15)

    # ---------------- TABLE A ----------------
    b = ctx.mb("TableAPedestals", mats["travertine"])
    b.add_cylinder(0.75, 0.0, -2.05, 0.10, 0.10, 0.72, segs=16)
    b.add_cylinder(1.55, 0.0, -2.05, 0.10, 0.10, 0.72, segs=16)

    b = ctx.mb("TableABrassCollars", mats["brass"])
    b.add_cylinder(0.75, 0.70, -2.05, 0.12, 0.12, 0.04, segs=16)
    b.add_cylinder(1.55, 0.70, -2.05, 0.12, 0.12, 0.04, segs=16)

    b = ctx.mb("TableAWalnutFrame", mats["rift_oak"])
    b.add_box(1.15, 0.73, -2.05, 1.30, 0.06, 0.80)

    b = ctx.mb("TableASmokedStone", mats["smoked_stone"])
    b.add_rounded_box(1.15, 0.76, -2.05, 1.34, 0.04, 0.84, bevel=0.02)

    # ---------------- TABLE B + CONCIERGE ----------------
    b = ctx.mb("TableB", mats["rift_oak"])
    b.add_rounded_box(3.10, 0.72, -1.18, 0.70, 0.04, 0.50, bevel=0.02)
    b.add_cylinder(3.10, 0.0, -1.18, 0.06, 0.06, 0.72, segs=14)

    b = ctx.mb("ConciergePager1F", mats["bronze_dark"])
    b.add_rounded_box(3.10, 0.755, -1.18, 0.16, 0.03, 0.10, bevel=0.01)

    b = ctx.mb("ConciergeScreen1F", mats["concierge_screen"])
    p0 = (3.02, 0.77, -1.13)
    p1 = (3.18, 0.77, -1.13)
    p2 = (3.18, 0.85, -1.13)
    p3 = (3.02, 0.85, -1.13)
    b.add_tri_raw(p0, p1, p2, uv0=(0, 0), uv1=(1, 0), uv2=(1, 1))
    b.add_tri_raw(p0, p2, p3, uv0=(0, 0), uv1=(1, 1), uv2=(0, 1))

    # ---------------- TABLE A OBJECTS ----------------
    b = ctx.mb("SalonMonographs", mats["burgundy"])
    b.add_box(0.22, 0.79, -2.18, 0.22, 0.05, 0.16)

    b = ctx.mb("SalonStonewareBowl", mats["ceramic_white"])
    b.add_lathe(1.96, 0.762, -2.26,
                [(0.0, 0.0), (0.09, 0.0), (0.11, 0.05), (0.10, 0.09), (0.0, 0.09)])

    # ---------------- SERVING TRAY ----------------
    b = ctx.mb("TableATrayLeather", mats["cognac_suede"])
    b.add_box(1.16, 0.772, -1.96, 0.84, 0.02, 0.48)

    b = ctx.mb("TableATrayBrass", mats["brass"])
    b.add_box(1.16, 0.782, -1.96, 0.86, 0.006, 0.50)

    # ---------------- EVIAN RESERVE (sealed) ----------------
    b = ctx.mb("EvianBottles1F", mats["evian_flint_glass"])
    b.add_lathe(0.90, 0.78, -2.06, [
        (0.0, 0.0), (0.044, 0.0), (0.044, 0.21),
        (0.030, 0.26), (0.018, 0.30), (0.018, 0.32), (0.0, 0.32)])

    b = ctx.mb("EvianCapsReserve1F", mats["evian_cap"])
    b.add_cylinder(0.90, 1.10, -2.06, 0.020, 0.020, 0.025, segs=14)

    b = ctx.mb("EvianLabelsReserve1F", mats["evian_label"])
    b.add_cylinder(0.90, 0.86, -2.06, 0.0455, 0.0455, 0.09, segs=18,
                   cap_top=False, cap_bot=False)

    # ---------------- EVIAN POUR (animatable) ----------------
    b = ctx.mb("EvianPourBottle1F", mats["evian_flint_glass"])
    b.add_lathe(1.15, 0.78, -1.96, [
        (0.0, 0.0), (0.044, 0.0), (0.044, 0.21),
        (0.030, 0.26), (0.018, 0.30), (0.018, 0.32), (0.0, 0.32)])

    b = ctx.mb("EvianPourLabel1F", mats["evian_label"])
    b.add_cylinder(1.15, 0.84, -1.96, 0.0455, 0.0455, 0.11, segs=18,
                   cap_top=False, cap_bot=False)

    b = ctx.mb("EvianPourCap1F", mats["evian_cap"])
    b.add_cylinder(1.15, 1.095, -1.96, 0.020, 0.020, 0.030, segs=14)

    # ---------------- CRYSTAL BOWL ----------------
    b = ctx.mb("CrystalWaterBowl1F", mats["crystal_glass"])
    b.add_lathe(1.44, 0.78, -1.92, [
        (0.0, 0.0), (0.10, 0.0), (0.135, 0.085), (0.0, 0.085)])

    b = ctx.mb("CrystalBowlWater1F", mats["water_meniscus"])
    b.add_cylinder(1.44, 0.798, -1.92, 0.118, 0.118, 0.012, segs=20)
