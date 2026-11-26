import math

def build_loft_2f(ctx, mats):
    # ------------------------------------------------------------------
    # 1. 2F Plush Loft Rug
    # ------------------------------------------------------------------
    b = ctx.mb("loft_rug", mats["rug"])
    b.add_box(-8.2, 9.23, -4.2, 6.8, 0.04, 9.4, uv_tile=1.0)

    # ------------------------------------------------------------------
    # 2. Walnut & Brass Hi-Fi Vinyl Credenza + Turntable
    # ------------------------------------------------------------------
    cx, cz = -13.2, -11.4
    y0 = 9.21
    # Credenza body
    b = ctx.mb("credenza_body", mats["walnut_solid"])
    b.add_rounded_box(cx, y0 + 0.55 + 0.875, cz, 2.2, 1.75, 5.4, bevel=0.05, uv_tile=1.0)
    # Fluted front panel (facing +X)
    bf = ctx.mb("credenza_fluted", mats["walnut_fluted"])
    for i in range(18):
        zz = cz - 2.55 + i * (5.1 / 17.0)
        bf.add_cylinder(cx + 1.11, y0 + 0.62, zz, 0.055, 0.055, 1.6, segs=10)
    # Slim brass legs
    bl = ctx.mb("credenza_legs", mats["brass"])
    for dx in (-0.9, 0.9):
        for dz in (-2.4, 2.4):
            bl.add_cylinder(cx + dx, y0, cz + dz, 0.035, 0.035, 0.55, segs=10)
    # Top surface
    bt = ctx.mb("credenza_top", mats["walnut_solid"])
    bt.add_box(cx, y0 + 1.75 + 0.55 + 0.02, cz, 2.25, 0.04, 5.45, uv_tile=1.0)

    # Turntable plinth
    tt_y = y0 + 1.75 + 0.55 + 0.04
    bp = ctx.mb("tt_plinth", mats["walnut_solid"])
    bp.add_rounded_box(cx, tt_y + 0.06, cz + 0.6, 1.4, 0.12, 1.4, bevel=0.02, uv_tile=1.0)
    # Brushed brass platter
    bpl = ctx.mb("tt_platter", mats["brass"])
    bpl.add_cylinder(cx, tt_y + 0.12, cz + 0.6, 0.55, 0.55, 0.04, segs=32)
    # Chrome spindle
    bsp = ctx.mb("tt_spindle", mats["chrome"])
    bsp.add_cylinder(cx, tt_y + 0.16, cz + 0.6, 0.012, 0.012, 0.06, segs=10)
    # Black vinyl LP
    blp = ctx.mb("tt_lp", mats["vinyl_black"])
    blp.add_cylinder(cx, tt_y + 0.165, cz + 0.6, 0.5, 0.5, 0.008, segs=40)
    # Label
    blb = ctx.mb("tt_label", mats["burgundy"])
    blb.add_cylinder(cx, tt_y + 0.174, cz + 0.6, 0.14, 0.14, 0.004, segs=24)
    # Tonearm base + arm
    bta = ctx.mb("tt_tonearm", mats["chrome"])
    bta.add_cylinder(cx + 0.55, tt_y + 0.12, cz + 1.15, 0.05, 0.05, 0.08, segs=14)
    bta.add_cylinder(cx + 0.55, tt_y + 0.20, cz + 1.15, 0.018, 0.018, 0.55, segs=10, rot_x=math.radians(70))
    # Upright showcased vinyl sleeve
    bs = ctx.mb("tt_sleeve", mats["vinyl_cover"])
    bs.add_box(cx - 0.55, tt_y + 0.35, cz + 0.6, 0.02, 0.62, 0.62, uv_tile=1.0)
    # Bookshelf monitor speakers
    bspk = ctx.mb("tt_speakers", mats["walnut_solid"])
    for dz in (-1.6, 1.6):
        bspk.add_rounded_box(cx, tt_y + 0.28, cz + dz, 0.55, 0.55, 0.42, bevel=0.03, uv_tile=1.0)
    bspk2 = ctx.mb("tt_speaker_cones", mats["chrome"])
    for dz in (-1.6, 1.6):
        bspk2.add_cylinder(cx + 0.28, tt_y + 0.28, cz + dz, 0.14, 0.14, 0.02, segs=20, rot_z=math.radians(90))

    # ------------------------------------------------------------------
    # 3. Sunlit Boucle Chaise Lounge Daybed + Travertine Pedestal
    # ------------------------------------------------------------------
    chx, chz = -5.8, -11.8
    # Base frame
    bch = ctx.mb("chaise_base", mats["walnut_solid"])
    bch.add_rounded_box(chx, y0 + 0.18, chz, 2.4, 0.36, 1.1, bevel=0.05, uv_tile=1.0)
    # Boucle cushion
    bcu = ctx.mb("chaise_cushion", mats["boucle"])
    bcu.add_rounded_box(chx, y0 + 0.55, chz, 2.35, 0.32, 1.05, bevel=0.12, uv_tile=1.0)
    # Curved bolster (backrest)
    bbo = ctx.mb("chaise_bolster", mats["boucle"])
    bbo.add_cylinder(chx - 0.9, y0 + 0.55, chz, 0.22, 0.22, 1.0, segs=20, rot_x=math.radians(90))
    # Burgundy silk throw pillow
    bpi = ctx.mb("chaise_pillow", mats["burgundy"])
    bpi.add_rounded_box(chx + 0.6, y0 + 0.78, chz - 0.2, 0.45, 0.35, 0.45, bevel=0.08, uv_tile=1.0)
    # Travertine drink pedestal
    btp = ctx.mb("travertine_pedestal", mats["travertine"])
    btp.add_cylinder(-4.4, y0, -10.8, 0.28, 0.32, 0.55, segs=24)
    btp.add_cylinder(-4.4, y0 + 0.55, -10.8, 0.34, 0.34, 0.04, segs=24)

    # ------------------------------------------------------------------
    # 4. FLY·04 Illuminated Travel Gallery Wall
    # ------------------------------------------------------------------
    wall_x = -14.80
    frame_z = [-6.8, -4.6, -2.4, -0.2]
    gal_mats = [mats["gal_1"], mats["gal_2"], mats["gal_3"], mats["gal_4"]]
    hw = 0.8
    hh = 1.0
    cy = 13.5
    for i, z in enumerate(frame_z):
        y0f = cy - hh
        y1f = cy + hh
        # Frame border (brass)
        bfr = ctx.mb("gallery_frame_%d" % i, mats["brass"])
        # top
        bfr.add_box(wall_x + 0.02, y1f + 0.04, z, 0.06, 0.08, 1.68, uv_tile=1.0)
        # bottom
        bfr.add_box(wall_x + 0.02, y0f - 0.04, z, 0.06, 0.08, 1.68, uv_tile=1.0)
        # left
        bfr.add_box(wall_x + 0.02, cy, z - hw - 0.04, 0.06, 2.08, 0.08, uv_tile=1.0)
        # right
        bfr.add_box(wall_x + 0.02, cy, z + hw + 0.04, 0.06, 2.08, 0.08, uv_tile=1.0)
        # Painting quad facing +X
        bp = ctx.mb("gallery_painting_%d" % i, gal_mats[i])
        bp.add_quad(
            (wall_x, y0f, z + hw),
            (wall_x, y0f, z - hw),
            (wall_x, y1f, z - hw),
            (wall_x, y1f, z + hw),
            uv_scale=(1.0, 1.0)
        )
        # Picture bar light
        blt = ctx.mb("gallery_light_%d" % i, mats["brass"])
        blt.add_box(wall_x + 0.12, y1f + 0.18, z, 0.10, 0.05, 1.5, uv_tile=1.0)
        bled = ctx.mb("gallery_led_%d" % i, mats["warm_led"])
        bled.add_box(wall_x + 0.12, y1f + 0.14, z, 0.06, 0.02, 1.4, uv_tile=1.0)

    # ------------------------------------------------------------------
    # 5. Bruce's Royal Burgundy-Velvet & Brass Pet Throne
    # ------------------------------------------------------------------
    px, pz = -12.6, -2.2
    # Oval base
    bpb = ctx.mb("pet_base", mats["burgundy"])
    bpb.add_cylinder(px, y0, pz, 0.75, 0.75, 0.18, segs=28)
    # Bolster ring (U-shape approximated with torus-like segments)
    bbr = ctx.mb("pet_bolster", mats["burgundy"])
    for i in range(20):
        ang = math.radians(200 + i * (140.0 / 19.0))
        bx = px + 0.62 * math.cos(ang)
        bz = pz + 0.62 * math.sin(ang)
        bbr.add_sphere(bx, y0 + 0.32, bz, 0.16, 0.14, 0.16, rings=8, segs=12)
    # Ivory center cushion
    bcc = ctx.mb("pet_cushion", mats["cream_pillow"])
    bcc.add_cylinder(px, y0 + 0.18, pz, 0.55, 0.55, 0.12, segs=24)
    # Brass trim ring
    btr = ctx.mb("pet_trim", mats["brass"])
    btr.add_cylinder(px, y0 + 0.18, pz, 0.76, 0.76, 0.03, segs=28)
