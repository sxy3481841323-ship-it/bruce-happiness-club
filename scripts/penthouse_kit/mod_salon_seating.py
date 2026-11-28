from penthouse_kit.cushion_helper import add_designer_pillow


def build_salon_seating(ctx, mats):
    # ---------- Rug ----------
    b = ctx.mb("SalonRug", mats["rug"])
    b.add_box(0.8, 0.02, -0.3, 13.8, 0.04, 13.6, uv_tile=2.0)
    b = ctx.mb("SalonRugFringe", mats["rug"])
    for sx in (-1, 1):
        b.add_box(0.8 + sx * 6.95, 0.02, -0.3, 0.10, 0.03, 13.6, uv_tile=1.0)
    for sz in (-1, 1):
        b.add_box(0.8, 0.02, -0.3 + sz * 6.85, 13.8, 0.03, 0.10, uv_tile=1.0)

    # ---------- Sofa ----------
    b = ctx.mb("SofaPlinth", mats["walnut_solid"])
    b.add_rounded_box(-1.0, 0.20, -3.7, 4.6, 0.40, 1.30, bevel=0.05)
    b.add_rounded_box(-3.35, 0.20, -2.55, 1.30, 0.40, 2.30, bevel=0.05)

    b = ctx.mb("SofaSeat", mats["boucle"])
    b.add_rounded_box(-1.0, 0.46, -3.7, 4.55, 0.20, 1.25, bevel=0.07)
    b.add_rounded_box(-3.35, 0.46, -2.55, 1.25, 0.20, 2.25, bevel=0.07)

    b = ctx.mb("SofaBack", mats["boucle"])
    b.add_rounded_box(-1.0, 0.86, -4.28, 4.55, 0.72, 0.22, bevel=0.08)
    b.add_rounded_box(-3.82, 0.86, -2.55, 0.22, 0.72, 2.25, bevel=0.08)

    # ---------- Jeanneret lounge chair ----------
    b = ctx.mb("JeanneretLoungeChair", mats["walnut_fluted"])
    b.add_rounded_box(-4.55, 0.30, -1.55, 0.72, 0.10, 0.72, bevel=0.04)
    b.add_rounded_box(-4.55, 0.62, -1.90, 0.72, 0.62, 0.10, bevel=0.04)
    for sx in (-1, 1):
        for sz in (-1, 1):
            b.add_box(-4.55 + sx * 0.30, 0.15, -1.55 + sz * 0.30, 0.06, 0.30, 0.06)
    b = ctx.mb("JeanneretCushion", mats["cognac_suede"])
    b.add_rounded_box(-4.55, 0.40, -1.55, 0.62, 0.10, 0.62, bevel=0.05)

    # ---------- Designer piped cushions ----------
    def _pillow(name, pos, fab, pipe, w=0.52, h=0.46, thick=0.16, yaw=0.0, tilt=-0.26):
        add_designer_pillow(
            ctx.mb(name, mats[fab]),
            ctx.mb(name + "Pipe", mats[pipe]),
            pos[0], pos[1], pos[2],
            w=w, h=h, thick=thick, yaw=yaw, tilt=tilt,
        )

    _pillow("SofaPillowA", (-2.55, 0.72, -3.95), "cream_pillow", "brass", w=0.54, h=0.46, thick=0.17, yaw=-0.18, tilt=-0.26)
    _pillow("SofaPillowB", (-1.95, 0.72, -3.95), "cognac_suede", "cream_pillow", w=0.50, h=0.44, thick=0.16, yaw=0.12, tilt=-0.30)
    _pillow("SofaPillowC", (-1.35, 0.72, -3.95), "burgundy", "brass", w=0.44, h=0.38, thick=0.15, yaw=-0.10, tilt=-0.24)
    _pillow("SofaPillowD", (-0.75, 0.72, -3.95), "cream_pillow", "brass", w=0.54, h=0.46, thick=0.17, yaw=0.20, tilt=-0.28)
    _pillow("SofaPillowE", (-0.15, 0.72, -3.95), "cognac_suede", "cream_pillow", w=0.50, h=0.44, thick=0.16, yaw=-0.14, tilt=-0.32)
    _pillow("SofaPillowF", (0.45, 0.72, -3.95), "burgundy", "brass", w=0.44, h=0.38, thick=0.15, yaw=0.25, tilt=-0.26)
    _pillow("SofaPillowG", (1.05, 0.72, -3.95), "cream_pillow", "brass", w=0.54, h=0.46, thick=0.17, yaw=-0.08, tilt=-0.30)
    _pillow("SofaLumbar", (-3.55, 0.70, -2.55), "burgundy", "brass", w=0.44, h=0.30, thick=0.15, yaw=1.45, tilt=-0.14)
    _pillow("JeanneretPillow", (-4.55, 0.58, -1.66), "cream_pillow", "brass", w=0.42, h=0.34, thick=0.13, yaw=0.0, tilt=-0.18)

    # ---------- Table A: smoked stone + walnut gallery ----------
    b = ctx.mb("TableAPedestals", mats["travertine"])
    for px in (0.35, 1.95):
        b.add_cylinder(px, 0.0, -2.05, 0.30, 0.26, 0.66, segs=24)
    b = ctx.mb("TableABrassCollars", mats["brass"])
    for px in (0.35, 1.95):
        b.add_cylinder(px, 0.66, -2.05, 0.28, 0.28, 0.04, segs=24)
    b = ctx.mb("TableAWalnutFrame", mats["walnut_solid"])
    b.add_box(1.15, 0.720, -2.05, 2.50, 0.075, 1.38, uv_tile=1.0)
    b = ctx.mb("TableASmokedStone", mats["smoked_stone"])
    b.add_box(1.15, 0.722, -2.05, 2.34, 0.080, 1.22, uv_tile=1.0)

    # ---------- Table B ----------
    b = ctx.mb("TableBPedestal", mats["travertine"])
    b.add_cylinder(3.10, 0.0, -1.18, 0.26, 0.24, 0.66, segs=24)
    b = ctx.mb("TableBTop", mats["smoked_stone"])
    b.add_box(3.10, 0.72, -1.18, 0.90, 0.06, 0.70, uv_tile=1.0)
    b = ctx.mb("ConciergePager1F", mats["charcoal"])
    b.add_rounded_box(2.95, 0.78, -1.18, 0.16, 0.05, 0.22, bevel=0.02)
    b = ctx.mb("ConciergeScreen1F", mats["concierge_screen"])
    p0 = (2.88, 0.805, -1.07)
    p1 = (3.02, 0.805, -1.07)
    p2 = (3.02, 0.805, -1.29)
    p3 = (2.88, 0.805, -1.29)
    b.add_tri_raw(p0, p1, p2, uv0=(0, 0), uv1=(1, 0), uv2=(1, 1))
    b.add_tri_raw(p0, p2, p3, uv0=(0, 0), uv1=(1, 1), uv2=(0, 1))

    # ---------- Table A objects ----------
    b = ctx.mb("SalonMonographs", mats["walnut_solid"])
    b.add_box(0.35, 0.79, -2.15, 0.34, 0.06, 0.26, uv_tile=1.0)
    b = ctx.mb("SalonStonewareBowl", mats["ceramic_white"])
    b.add_lathe(1.92, 0.762, -2.25, [(0.0, 0.0), (0.10, 0.0), (0.14, 0.06), (0.12, 0.10)], segs=24)

    # ---------- Saddle-leather tray ----------
    b = ctx.mb("SalonTrayBed", mats["cognac_suede"])
    b.add_box(1.10, 0.772, -1.92, 0.66, 0.02, 0.44, uv_tile=1.0)
    b = ctx.mb("SalonTrayRail", mats["brass"])
    b.add_box(1.10, 0.792, -1.70, 0.66, 0.04, 0.02)
    b.add_box(1.10, 0.792, -2.14, 0.66, 0.04, 0.02)
    b.add_box(0.77, 0.792, -1.92, 0.02, 0.04, 0.44)
    b.add_box(1.43, 0.792, -1.92, 0.02, 0.04, 0.44)

    # ---------- Evian bottles ----------
    b = ctx.mb("EvianBottles1F", mats["evian_flint_glass"])
    for bx in (0.90, 1.10, 1.30):
        b.add_cylinder(bx, 0.782, -1.94, 0.045, 0.045, 0.22, segs=20)
        b.add_cylinder(bx, 1.002, -1.94, 0.045, 0.022, 0.06, segs=20)
        b.add_cylinder(bx, 1.062, -1.94, 0.022, 0.020, 0.04, segs=16)
    b = ctx.mb("EvianCaps1F", mats["evian_cap"])
    for bx in (0.90, 1.10, 1.30):
        b.add_cylinder(bx, 1.102, -1.94, 0.022, 0.022, 0.018, segs=16)
    b = ctx.mb("EvianWater1F", mats["water_meniscus"])
    for bx in (0.90, 1.10, 1.30):
        b.add_cylinder(bx, 0.79, -1.94, 0.038, 0.038, 0.20, segs=16)
    b = ctx.mb("EvianLabels1F", mats["evian_label"])
    for bx in (0.90, 1.10, 1.30):
        b.add_cylinder(bx, 0.86, -1.94, 0.046, 0.046, 0.10, segs=20, cap_top=False, cap_bot=False)

    # ---------- Tumblers ----------
    b = ctx.mb("SalonTumblers", mats["crystal_glass"])
    for tx in (0.98, 1.22):
        b.add_cylinder(tx, 0.782, -1.78, 0.038, 0.042, 0.10, segs=8)
    b = ctx.mb("SalonTumblerWater", mats["water_meniscus"])
    for tx in (0.98, 1.22):
        b.add_cylinder(tx, 0.79, -1.78, 0.032, 0.032, 0.06, segs=8)
