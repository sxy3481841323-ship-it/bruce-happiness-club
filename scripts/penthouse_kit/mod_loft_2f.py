import math

def build_loft_2f(ctx, mats):
    y0 = 9.21

    # ------------------------------------------------------------------
    # LOFT RUG
    # ------------------------------------------------------------------
    b = ctx.mb("loft_rug", mats["rug"])
    b.add_box(-8.2, y0 + 0.02, -4.2, 6.4, 0.04, 5.2, uv_tile=0.0)

    # ------------------------------------------------------------------
    # SUNLIT BOUCLÉ CHAISE DAYBED  (-5.8, -11.8)
    # ------------------------------------------------------------------
    b = ctx.mb("loft_daybed_base", mats["walnut_solid"])
    b.add_rounded_box(-5.8, y0 + 0.18, -11.8, 2.4, 0.30, 1.05, bevel=0.05)
    b = ctx.mb("loft_daybed_feet", mats["brass"])
    for dx in (-1.05, 1.05):
        for dz in (-0.42, 0.42):
            b.add_cylinder(-5.8 + dx, y0, -11.8 + dz, 0.05, 0.05, 0.18, segs=12)

    b = ctx.mb("loft_daybed_cushion", mats["boucle"])
    b.add_rounded_box(-5.8, y0 + 0.42, -11.8, 2.3, 0.22, 0.98, bevel=0.08)
    b.add_rounded_box(-5.8, y0 + 0.62, -12.22, 2.2, 0.30, 0.22, bevel=0.09)
    b = ctx.mb("loft_daybed_pillows", mats["cream_pillow"])
    b.add_rounded_box(-6.55, y0 + 0.60, -12.05, 0.42, 0.30, 0.20, bevel=0.08, rot_y=0.15)
    b.add_rounded_box(-5.05, y0 + 0.60, -12.05, 0.42, 0.30, 0.20, bevel=0.08, rot_y=-0.15)

    # ------------------------------------------------------------------
    # 4 COLLECTOR GALLERY FRAMES  (wall_x = -14.80, museum scale cy=13.5)
    # ------------------------------------------------------------------
    wall_x = -14.80
    gal_keys = ["gal_1", "gal_2", "gal_3", "gal_4"]
    gal_z = [-6.8, -4.6, -2.4, -0.2]
    hw, hh, cy = 0.80, 1.00, 13.5
    for i, gz in enumerate(gal_z):
        y0f, y1f = cy - hh, cy + hh
        bfr = ctx.mb("loft_gallery_frame_%d" % i, mats["brass"])
        bfr.add_box(wall_x + 0.02, y1f + 0.04, gz, 0.06, 0.08, 1.68)
        bfr.add_box(wall_x + 0.02, y0f - 0.04, gz, 0.06, 0.08, 1.68)
        bfr.add_box(wall_x + 0.02, cy, gz - hw - 0.04, 0.06, 2.08, 0.08)
        bfr.add_box(wall_x + 0.02, cy, gz + hw + 0.04, 0.06, 2.08, 0.08)
        bp = ctx.mb("gallery_painting_%d" % i, mats[gal_keys[i]])
        bp.add_quad((wall_x, y0f, gz + hw), (wall_x, y0f, gz - hw), (wall_x, y1f, gz - hw), (wall_x, y1f, gz + hw), uv_scale=(1.0, 1.0))
        ctx.mb("loft_gallery_light_%d" % i, mats["brass"]).add_box(wall_x + 0.12, y1f + 0.18, gz, 0.10, 0.05, 1.50)
        ctx.mb("loft_gallery_led_%d" % i, mats["warm_led"]).add_box(wall_x + 0.12, y1f + 0.14, gz, 0.06, 0.02, 1.40)

    # ------------------------------------------------------------------
    # BRUCE'S VELVET PET THRONE  (-12.6, -2.2)
    # ------------------------------------------------------------------
    b = ctx.mb("loft_pet_throne_base", mats["walnut_solid"])
    b.add_rounded_box(-12.6, y0 + 0.10, -2.2, 0.85, 0.20, 0.85, bevel=0.04)
    b = ctx.mb("loft_pet_throne_velvet", mats["burgundy"])
    b.add_rounded_box(-12.6, y0 + 0.32, -2.2, 0.78, 0.24, 0.78, bevel=0.10)
    b.add_rounded_box(-12.6, y0 + 0.62, -2.55, 0.78, 0.55, 0.16, bevel=0.10)
    b = ctx.mb("loft_pet_throne_brass", mats["brass"])
    for dx in (-0.34, 0.34):
        b.add_sphere(-12.6 + dx, y0 + 0.92, -2.55, 0.05, 0.05, 0.05, rings=8, segs=10)
    b = ctx.mb("loft_pet_throne_cushion", mats["cream_pillow"])
    b.add_rounded_box(-12.6, y0 + 0.46, -2.2, 0.62, 0.10, 0.62, bevel=0.06)

    # ==================================================================
    # 1. UPGRADED VINYL HI-FI CREDENZA + AURA DOME SPEAKER (oriented along Z!)
    # ==================================================================
    cx = -13.1
    cz = -11.4
    cred_w = 1.65
    cred_len = 5.6
    tt_y = y0 + 1.80

    b = ctx.mb("LoftCredenzaPlinth", mats["bronze_dark"])
    b.add_box(cx, y0 + 0.08, cz, cred_w - 0.18, 0.16, cred_len - 0.24)
    b = ctx.mb("LoftCredenzaCoveLED", mats["warm_led"])
    b.add_box(cx + 0.06, y0 + 0.17, cz, cred_w - 0.28, 0.02, cred_len - 0.34)

    b = ctx.mb("LoftCredenzaBody", mats["walnut_fluted"])
    b.add_box(cx, y0 + 0.94, cz, cred_w, 1.50, cred_len)
    b = ctx.mb("LoftCredenzaFlutes", mats["walnut_solid"])
    n_flutes = 24
    for i in range(n_flutes):
        fz = cz - cred_len / 2 + 0.14 + i * (cred_len - 0.28) / (n_flutes - 1)
        b.add_box(cx + cred_w / 2 + 0.012, y0 + 0.94, fz, 0.025, 1.42, 0.06)

    b = ctx.mb("LoftCredenzaMarbleTop", mats["marble"])
    b.add_rounded_box(cx, tt_y - 0.05, cz, cred_w + 0.16, 0.10, cred_len + 0.16, bevel=0.03)

    tt_x = cx
    tt_z = cz + 0.65
    b = ctx.mb("LoftTurntableBase", mats["walnut_solid"])
    b.add_rounded_box(tt_x, tt_y + 0.06, tt_z, 1.15, 0.12, 1.15, bevel=0.02)
    b = ctx.mb("LoftTurntablePlatter", mats["brass"])
    b.add_cylinder(tt_x, tt_y + 0.12, tt_z, 0.44, 0.44, 0.04, segs=28)
    b = ctx.mb("LoftTurntableVinyl", mats["vinyl_black"])
    b.add_cylinder(tt_x, tt_y + 0.16, tt_z, 0.41, 0.41, 0.012, segs=32)
    b = ctx.mb("LoftTurntableArm", mats["chrome"])
    b.add_cylinder(tt_x + 0.44, tt_y + 0.12, tt_z - 0.35, 0.035, 0.035, 0.10, segs=10)
    b.add_cylinder(tt_x + 0.44, tt_y + 0.20, tt_z - 0.35, 0.015, 0.015, 0.45, segs=8, rot_x=math.radians(70))

    b = ctx.mb("LoftVinylCover", mats["vinyl_cover"])
    b.add_box(cx - 0.45, tt_y + 0.32, cz + 0.65, 0.02, 0.56, 0.56)

    # ---- Harman Kardon Aura Studio Smoked-Glass Dome Speaker ----
    aura_x = -13.0
    aura_z = -13.2
    b = ctx.mb("LoftAuraSpeaker", mats["glass_smoke"])
    b.add_cylinder(aura_x, tt_y, aura_z, 0.34, 0.34, 0.18, segs=28)
    b.add_sphere(aura_x, tt_y + 0.18, aura_z, 0.32, 0.42, 0.32, rings=14, segs=24)
    b = ctx.mb("LoftAuraTurbine", mats["chrome"])
    b.add_cylinder(aura_x, tt_y + 0.18, aura_z, 0.06, 0.18, 0.28, segs=20)
    b.add_cylinder(aura_x, tt_y + 0.46, aura_z, 0.18, 0.04, 0.06, segs=20)
    b = ctx.mb("LoftAuraHalo", mats["warm_led"])
    b.add_cylinder(aura_x, tt_y + 0.175, aura_z, 0.35, 0.35, 0.022, segs=32)

    b = ctx.mb("LoftArtBooks", mats["charcoal"])
    bx = cx + 0.05
    bz = cz + 2.15
    b.add_box(bx, tt_y + 0.04, bz, 0.46, 0.06, 0.38, rot_y=0.05)
    b.add_box(bx, tt_y + 0.10, bz, 0.42, 0.05, 0.34, rot_y=-0.08)
    b = ctx.mb("LoftArtBooksAccent", mats["burgundy"])
    b.add_box(bx, tt_y + 0.15, bz, 0.38, 0.04, 0.30, rot_y=-0.04)

    # ==================================================================
    # 2. BESPOKE 2F EXECUTIVE STUDY DESK & COLLECTOR CHAIR
    # ==================================================================
    desk_cx = -5.8
    desk_cy = 10.68
    desk_cz = 3.30

    b = ctx.mb("LoftDeskTop", mats["walnut_solid"])
    b.add_rounded_box(desk_cx, desk_cy, desk_cz, 2.95, 0.11, 1.32, bevel=0.03)
    b = ctx.mb("LoftDeskInlay", mats["marble"])
    b.add_box(desk_cx, desk_cy + 0.058, desk_cz, 2.55, 0.012, 1.05)

    for px in (-6.9, -4.7):
        tag = "L" if px < desk_cx else "R"
        b = ctx.mb("LoftDeskPedestal_%s" % tag, mats["walnut_fluted"])
        b.add_rounded_box(px, (y0 + 10.62) / 2, desk_cz, 0.42, 10.62 - y0, 0.95, bevel=0.04)
        b = ctx.mb("LoftDeskPedestalFlutes_%s" % tag, mats["walnut_solid"])
        for i in range(6):
            fz = desk_cz - 0.40 + i * 0.16
            b.add_box(px, (y0 + 10.62) / 2, fz, 0.44, 10.62 - y0 - 0.10, 0.03)
        b = ctx.mb("LoftDeskPedestalBrass_%s" % tag, mats["brass"])
        b.add_box(px, y0 + 0.03, desk_cz, 0.46, 0.06, 0.99)

    b = ctx.mb("LoftDeskBlotter", mats["cognac_suede"])
    b.add_box(-5.8, 10.745, 3.18, 1.45, 0.012, 0.72)

    # ---- Sculpted cognac-suede & curved-walnut executive swivel armchair ----
    ch_x = -5.8
    ch_z = 4.25
    b = ctx.mb("LoftChairPedestal", mats["brass"])
    b.add_cylinder(ch_x, y0, ch_z, 0.28, 0.28, 0.04, segs=24)
    b.add_cylinder(ch_x, y0 + 0.04, ch_z, 0.05, 0.05, 0.30, segs=16)
    b = ctx.mb("LoftChairSeat", mats["cognac_suede"])
    b.add_rounded_box(ch_x, y0 + 0.42, ch_z, 0.62, 0.14, 0.60, bevel=0.06)
    b.add_rounded_box(ch_x, y0 + 0.72, ch_z + 0.26, 0.62, 0.50, 0.14, bevel=0.07)
    b = ctx.mb("LoftChairArms", mats["walnut_solid"])
    for dx in (-0.32, 0.32):
        b.add_rounded_box(ch_x + dx, y0 + 0.58, ch_z + 0.02, 0.08, 0.10, 0.50, bevel=0.03)

    # ---- Brushed-Brass Atelier Desk Lamp ----
    lamp_x = -6.85
    lamp_y = 10.74
    lamp_z = 3.05
    b = ctx.mb("LoftDeskLamp", mats["brass"])
    b.add_cylinder(lamp_x, lamp_y, lamp_z, 0.09, 0.09, 0.03, segs=20)
    b.add_cylinder(lamp_x, lamp_y + 0.03, lamp_z, 0.018, 0.018, 0.42, segs=10, rot_z=0.25)
    b.add_cylinder(lamp_x + 0.10, lamp_y + 0.42, lamp_z, 0.09, 0.05, 0.10, segs=20, rot_z=0.6)
    b = ctx.mb("LoftDeskLampBulb", mats["warm_bulb"])
    b.add_sphere(lamp_x + 0.13, lamp_y + 0.40, lamp_z, 0.045, 0.045, 0.045, rings=8, segs=12)

    # ---- 2 Glass Evian Bottles + Crystal Tumbler on travertine tray ----
    tray_x = -4.82
    tray_y = 10.74
    tray_z = 3.08
    b = ctx.mb("LoftDeskTray", mats["travertine"])
    b.add_rounded_box(tray_x, tray_y + 0.015, tray_z, 0.54, 0.03, 0.34, bevel=0.01)

    b = ctx.mb("EvianBottles2F", mats["crystal_glass"])
    bcaps = ctx.mb("EvianCaps2F", mats["chrome"])
    blab = ctx.mb("EvianLabels2F", mats["evian_label"])
    for bx in (-0.12, 0.03):
        b.add_lathe(tray_x + bx, tray_y + 0.03, tray_z - 0.02, [
            (0.0, 0.0), (0.048, 0.0), (0.056, 0.05), (0.056, 0.24),
            (0.042, 0.31), (0.018, 0.35), (0.018, 0.39), (0.0, 0.39)
        ], segs=18)
        blab.add_cylinder(tray_x + bx, tray_y + 0.11, tray_z - 0.02, 0.058, 0.058, 0.15, segs=18, cap_top=False, cap_bot=False)
        bcaps.add_cylinder(tray_x + bx, tray_y + 0.42, tray_z - 0.02, 0.020, 0.019, 0.03, segs=14)
    b.add_cylinder(tray_x + 0.16, tray_y + 0.03, tray_z + 0.05, 0.038, 0.044, 0.11, segs=10)

    # ---- 2F Concierge Intercom Pager (angled toward +Z/+Y 2F camera) ----
    pager_x = -5.25
    pager_y = 10.74
    pager_z = 3.55
    b = ctx.mb("ConciergePager2F", mats["charcoal"])
    b.add_rounded_box(pager_x, pager_y + 0.05, pager_z - 0.03, 0.28, 0.10, 0.14, bevel=0.015)
    b.add_box(pager_x, pager_y + 0.02, pager_z + 0.06, 0.28, 0.04, 0.08)
    b = ctx.mb("ConciergePagerTrim2F", mats["brass"])
    b.add_box(pager_x, pager_y + 0.105, pager_z - 0.03, 0.29, 0.012, 0.15)
    for i in range(3):
        b.add_cylinder(pager_x - 0.075 + i * 0.075, pager_y + 0.042, pager_z + 0.072, 0.013, 0.013, 0.012, segs=12)

    b = ctx.mb("ConciergeScreen2F", mats["concierge_screen"])
    b.add_tri_raw((pager_x - 0.11, pager_y + 0.048, pager_z + 0.045), (pager_x + 0.11, pager_y + 0.048, pager_z + 0.045), (pager_x + 0.11, pager_y + 0.102, pager_z - 0.085), (0.0, 0.0), (1.0, 0.0), (1.0, 1.0))
    b.add_tri_raw((pager_x - 0.11, pager_y + 0.048, pager_z + 0.045), (pager_x + 0.11, pager_y + 0.102, pager_z - 0.085), (pager_x - 0.11, pager_y + 0.102, pager_z - 0.085), (0.0, 0.0), (1.0, 1.0), (0.0, 1.0))

    # linen-bound notebook & brass pen holder
    b = ctx.mb("LoftDeskNotebook", mats["cream_pillow"])
    b.add_box(-4.55, 10.745, 3.55, 0.22, 0.02, 0.16, rot_y=0.12)
    b = ctx.mb("LoftDeskPenHolder", mats["brass"])
    b.add_cylinder(-4.55, 10.745, 3.35, 0.035, 0.035, 0.09, segs=16)
    b.add_cylinder(-4.55, 10.835, 3.35, 0.006, 0.006, 0.14, segs=8, rot_z=0.15)
