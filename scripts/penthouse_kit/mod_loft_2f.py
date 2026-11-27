"""2F Loft — Old-Money collector's gallery, daybed, pet throne, hi-fi, desk."""

import math


def build_loft_2f(ctx, mats):
    y0 = 9.21
    wall_x = -14.54

    # ------------------------------------------------------------------ carpet
    b = ctx.mb("loft_rug", mats["rug_2f"])
    b.add_box(-8.2, y0 + 0.02, -4.2, 6.8, 0.04, 6.2, uv_tile=0.0)

    # ------------------------------------------------- monumental masterwork
    gz, cy = -3.4, 13.35
    y0f, y1f = cy - 1.05, cy + 1.05
    z0, z1 = gz - 2.10, gz + 2.10

    b = ctx.mb("LoftMasterworkCanvas", mats["gal_master"])
    b.add_quad((wall_x + 0.03, y0f, z1), (wall_x + 0.03, y0f, z0),
               (wall_x + 0.03, y1f, z0), (wall_x + 0.03, y1f, z1))

    # deep carved walnut shadow-box frame
    b = ctx.mb("LoftMasterworkFrame", mats["walnut_solid"])
    fd, fw = 0.18, 0.22
    b.add_box(wall_x - fd * 0.2, cy, z0 - fw * 0.5, fd, 2.10 + fw * 2, fw)
    b.add_box(wall_x - fd * 0.2, cy, z1 + fw * 0.5, fd, 2.10 + fw * 2, fw)
    b.add_box(wall_x - fd * 0.2, y1f + fw * 0.5, gz, fd, fw, 4.20)
    b.add_box(wall_x - fd * 0.2, y0f - fw * 0.5, gz, fd, fw, 4.20)

    # chamfered antique brass inner slip
    b = ctx.mb("LoftMasterworkSlip", mats["brass"])
    sd, sw = 0.05, 0.06
    b.add_box(wall_x + sd * 0.5, cy, z0 - sw * 0.5, sd, 2.10, sw)
    b.add_box(wall_x + sd * 0.5, cy, z1 + sw * 0.5, sd, 2.10, sw)
    b.add_box(wall_x + sd * 0.5, y1f + sw * 0.5, gz, sd, sw, 4.20)
    b.add_box(wall_x + sd * 0.5, y0f - sw * 0.5, gz, sd, sw, 4.20)

    # brushed-brass museum picture light + hidden warm LED bar
    b = ctx.mb("LoftMasterworkLight", mats["brass"])
    b.add_cylinder(wall_x + 0.30, 14.58, gz, 0.05, 0.05, 2.10,
                   segs=14, rot_x=1.5708)
    b.add_box(wall_x + 0.30, 14.58, gz, 0.10, 0.06, 2.10)
    b = ctx.mb("LoftMasterworkLED", mats["warm_led"])
    b.add_box(wall_x + 0.36, 14.55, gz, 0.03, 0.02, 2.00)

    # ---------------------------------------------- flanking boiserie pilasters
    for pz in (-7.0, 0.2):
        b = ctx.mb("loft_pilaster_%s" % ("a" if pz < -3 else "b"),
                   mats["marmorino"])
        b.add_box(wall_x + 0.10, cy, pz, 0.20, 3.60, 0.55)
        b = ctx.mb("loft_pilaster_walnut_%s" % ("a" if pz < -3 else "b"),
                   mats["walnut_fluted"])
        b.add_box(wall_x + 0.22, cy, pz, 0.10, 3.40, 0.42)
        b = ctx.mb("loft_pilaster_cap_%s" % ("a" if pz < -3 else "b"),
                   mats["brass"])
        b.add_box(wall_x + 0.24, cy + 1.78, pz, 0.14, 0.08, 0.50)
        b.add_box(wall_x + 0.24, cy - 1.78, pz, 0.14, 0.08, 0.50)
        # warm brass sconce
        b = ctx.mb("loft_sconce_%s" % ("a" if pz < -3 else "b"),
                   mats["brass"])
        b.add_cylinder(wall_x + 0.30, 13.90, pz, 0.06, 0.06, 0.30, segs=12)
        b = ctx.mb("loft_sconce_glow_%s" % ("a" if pz < -3 else "b"),
                   mats["warm_bulb"])
        b.add_sphere(wall_x + 0.30, 14.22, pz, 0.10, 0.12, 0.10)

    # ------------------------------------------------------------- daybed
    dx, dz = -5.8, -11.8
    b = ctx.mb("loft_daybed_base", mats["walnut_solid"])
    b.add_rounded_box(dx, y0 + 0.22, dz, 2.20, 0.44, 1.10, bevel=0.05)
    b = ctx.mb("loft_daybed_cushion", mats["boucle"])
    b.add_rounded_box(dx, y0 + 0.55, dz, 2.10, 0.22, 1.02, bevel=0.08)
    b = ctx.mb("loft_daybed_pillow", mats["cream_pillow"])
    b.add_rounded_box(dx - 0.75, y0 + 0.72, dz, 0.42, 0.20, 0.60, bevel=0.06)
    b.add_rounded_box(dx - 0.30, y0 + 0.72, dz, 0.42, 0.20, 0.60, bevel=0.06)

    # ---------------------------------------------------------- pet throne
    px, pz = -12.6, -2.2
    b = ctx.mb("loft_pet_throne_base", mats["walnut_solid"])
    b.add_rounded_box(px, y0 + 0.20, pz, 0.90, 0.40, 0.90, bevel=0.05)
    b = ctx.mb("loft_pet_throne_cushion", mats["burgundy"])
    b.add_rounded_box(px, y0 + 0.46, pz, 0.80, 0.14, 0.80, bevel=0.06)
    b = ctx.mb("loft_pet_throne_back", mats["walnut_fluted"])
    b.add_box(px, y0 + 0.75, pz - 0.42, 0.90, 0.70, 0.10)

    # ------------------------------------------------------- vinyl hi-fi
    vx, vz = -13.1, -11.4
    b = ctx.mb("loft_credenza", mats["walnut_fluted"])
    b.add_rounded_box(vx, y0 + 0.35, vz, 2.40, 0.70, 0.55, bevel=0.04)
    b = ctx.mb("loft_credenza_top", mats["marble"])
    b.add_box(vx, y0 + 0.72, vz, 2.44, 0.04, 0.58)

    b = ctx.mb("LoftTurntableVinyl", mats["vinyl_black"])
    b.add_cylinder(vx - 0.55, y0 + 0.74, vz, 0.22, 0.22, 0.03, segs=24)
    b = ctx.mb("LoftTurntableCover", mats["vinyl_cover"])
    b.add_cylinder(vx - 0.55, y0 + 0.77, vz, 0.10, 0.10, 0.01, segs=20)

    b = ctx.mb("LoftAuraSpeaker", mats["charcoal"])
    b.add_rounded_box(vx + 0.55, y0 + 0.95, vz, 0.34, 0.46, 0.34, bevel=0.04)
    b = ctx.mb("LoftAuraHalo", mats["warm_led"])
    b.add_cylinder(vx + 0.55, y0 + 1.20, vz, 0.14, 0.14, 0.02, segs=20)

    # ------------------------------------------------------- executive desk
    ex, ez = -5.8, 3.30
    b = ctx.mb("loft_desk_top", mats["walnut_solid"])
    b.add_rounded_box(ex, y0 + 0.74, ez, 2.60, 0.06, 1.10, bevel=0.03)
    b = ctx.mb("loft_desk_legs", mats["brass"])
    for lx in (-1.15, 1.15):
        for lz in (-0.45, 0.45):
            b.add_cylinder(ex + lx, y0, ez + lz, 0.04, 0.04, 0.72, segs=10)

    b = ctx.mb("EvianBottles2F", mats["glass"])
    for i, bx in enumerate((-0.55, -0.30, -0.05)):
        b.add_cylinder(ex + bx, y0 + 0.77, ez - 0.20, 0.045, 0.045, 0.26, segs=12)
    b = ctx.mb("EvianLabels2F", mats["evian_label"])
    for bx in (-0.55, -0.30, -0.05):
        b.add_box(ex + bx, y0 + 0.88, ez - 0.20, 0.09, 0.08, 0.09)

    b = ctx.mb("ConciergePager2F", mats["bronze_dark"])
    b.add_rounded_box(ex + 0.55, y0 + 0.80, ez + 0.10, 0.14, 0.05, 0.10,
                      bevel=0.02)
    b = ctx.mb("ConciergeScreen2F", mats["concierge_screen"])
    b.add_box(ex + 0.55, y0 + 0.83, ez + 0.10, 0.10, 0.01, 0.07)

    return None
