import math


def _fluted_panel(b, cx, cy, cz, sx, sy, sz, n_flutes, axis="z"):
    """Add a fluted panel: a base box plus n_flutes thin vertical ribs."""
    b.add_box(cx, cy, cz, sx, sy, sz)
    if axis == "z":
        span = sx
        for i in range(n_flutes):
            t = (i + 0.5) / n_flutes
            x = cx - span * 0.5 + span * t
            b.add_box(x, cy, cz + sz * 0.5 + 0.006, span / n_flutes * 0.55, sy * 0.94, 0.012)
    else:
        span = sz
        for i in range(n_flutes):
            t = (i + 0.5) / n_flutes
            z = cz - span * 0.5 + span * t
            b.add_box(cx + sx * 0.5 + 0.006, cy, z, 0.012, sy * 0.94, span / n_flutes * 0.55)


def build_media_fireplace(ctx, mats):
    # ------------------------------------------------------------------
    # 1. MediaHearth  (X 12.3..14.3, Z -6.8..3.2, Y 0.38..1.50)
    # ------------------------------------------------------------------
    hearth = ctx.mb("MediaHearth", mats["travertine"])
    hx0, hx1 = 12.3, 14.3
    hz0, hz1 = -6.8, 3.2
    hy0, hy1 = 0.38, 1.50
    hcx = (hx0 + hx1) * 0.5
    hcz = (hz0 + hz1) * 0.5
    hsx = hx1 - hx0
    hsz = hz1 - hz0
    hsy = hy1 - hy0
    hcy = (hy0 + hy1) * 0.5

    # Floating travertine top slab
    hearth.add_rounded_box(hcx, hy1 - 0.06, hcz, hsx, 0.12, hsz, bevel=0.05)
    # Travertine body (recessed slightly so top overhangs)
    hearth.add_box(hcx, hcy - 0.02, hcz, hsx - 0.10, hsy - 0.14, hsz - 0.10)

    # Brushed champagne-brass plinth
    plinth = ctx.mb("MediaHearthPlinth", mats["brass"])
    plinth.add_box(hcx, hy0 + 0.02, hcz, hsx - 0.06, 0.04, hsz - 0.06)
    # Brass inlay line just under the top slab
    plinth.add_box(hcx, hy1 - 0.135, hcz, hsx - 0.02, 0.012, hsz - 0.02)

    # Recessed walnut fluted drawer bank (front face toward -X)
    drawer = ctx.mb("MediaHearthDrawers", mats["walnut_fluted"])
    d_x = hx0 + 0.03
    d_cy = hcy - 0.02
    d_sy = hsy - 0.22
    d_sz = hsz - 0.30
    # base recessed panel
    drawer.add_box(d_x + 0.02, d_cy, hcz, 0.06, d_sy, d_sz)
    # 46 vertical flutes across Z
    n_flutes = 46
    for i in range(n_flutes):
        t = (i + 0.5) / n_flutes
        z = hcz - d_sz * 0.5 + d_sz * t
        drawer.add_box(d_x - 0.006, d_cy, z, 0.014, d_sy * 0.96, d_sz / n_flutes * 0.55)

    # ------------------------------------------------------------------
    # 2. Recessed Wood-Burning Firebox
    #    Z -4.1..0.5, Y 1.54..2.52, X 13.68..14.62
    # ------------------------------------------------------------------
    fx0, fx1 = 13.68, 14.62
    fz0, fz1 = -4.1, 0.5
    fy0, fy1 = 1.54, 2.52
    fcx = (fx0 + fx1) * 0.5
    fcz = (fz0 + fz1) * 0.5
    fsx = fx1 - fx0
    fsz = fz1 - fz0
    fsy = fy1 - fy0
    fcy = (fy0 + fy1) * 0.5

    cav = ctx.mb("FireplaceCavity", mats["charcoal"])
    # back wall of cavity
    cav.add_box(fx1 - 0.03, fcy, fcz, 0.06, fsy, fsz)
    # top reveal
    cav.add_box(fcx, fy1 - 0.03, fcz, fsx, 0.06, fsz)
    # bottom hearth floor
    cav.add_box(fcx, fy0 + 0.02, fcz, fsx, 0.04, fsz)
    # side walls
    cav.add_box(fcx, fcy, fz0 + 0.03, fsx, fsy, 0.06)
    cav.add_box(fcx, fcy, fz1 - 0.03, fsx, fsy, 0.06)

    # Brushed champagne-brass surround frame
    frame = ctx.mb("FireplaceSurround", mats["brass"])
    fr = 0.05
    # top bar
    frame.add_box(fcx, fy1 + fr * 0.5, fcz, fsx + 0.10, fr, fsz + 0.10)
    # bottom bar
    frame.add_box(fcx, fy0 - fr * 0.5, fcz, fsx + 0.10, fr, fsz + 0.10)
    # side bars
    frame.add_box(fcx, fcy, fz0 - fr * 0.5, fsx + 0.10, fsy + fr * 2.0, fr)
    frame.add_box(fcx, fcy, fz1 + fr * 0.5, fsx + 0.10, fsy + fr * 2.0, fr)

    # ---- Ember bed ----
    emb = ctx.mb("FireplaceEmbers", mats["fire_ember"])
    ex0, ex1 = 13.78, 14.42
    ez0, ez1 = -3.85, 0.25
    ecx = (ex0 + ex1) * 0.5
    ecz = (ez0 + ez1) * 0.5
    esx = ex1 - ex0
    esz = ez1 - ez0
    emb.add_box(ecx, 1.62, ecz, esx, 0.05, esz)
    # scattered glowing ember lumps
    ember_spots = [
        (-3.6, 0.10), (-3.2, -0.05), (-2.7, 0.08), (-2.2, -0.10),
        (-1.6, 0.06), (-1.0, -0.08), (-0.4, 0.10), (0.1, -0.05),
        (-3.4, 0.12), (-2.0, 0.14), (-0.8, 0.12), (0.15, 0.10),
    ]
    for i, (z, off) in enumerate(ember_spots):
        r = 0.035 + 0.02 * ((i * 7) % 5) / 5.0
        emb.add_sphere(ecx + off, 1.645 + r * 0.4, z, r, r * 0.7, r, rings=8, segs=10)

    # ---- Logs + grate ----
    logs = ctx.mb("FireplaceLogs", mats["charred_bark"])
    grate = ctx.mb("FireplaceGrate", mats["charcoal"])
    # wrought-iron grate bars
    for i in range(5):
        gz = -3.45 + i * 0.85
        grate.add_cylinder(ecx, 1.66, gz, 0.012, 0.012, 0.10, segs=8)
    grate.add_box(ecx, 1.70, ecz, esx * 0.9, 0.02, 0.02)
    grate.add_box(ecx, 1.70, ecz, 0.02, 0.02, esz * 0.9)

    # 7 split charred-oak logs laid horizontally across the ember grate along Z
    log_specs = [
        # (x_off, y_center, z_center, length, rx, rz)
        (-0.08, 1.76, -3.55, 0.96, math.pi * 0.5 + 0.06, 0.14),
        (0.06,  1.77, -2.65, 1.02, math.pi * 0.5 - 0.05, -0.18),
        (-0.05, 1.78, -1.75, 1.04, math.pi * 0.5 + 0.04, 0.10),
        (0.08,  1.77, -0.85, 0.98, math.pi * 0.5 - 0.06, -0.15),
        (-0.04, 1.76,  0.02, 0.92, math.pi * 0.5 + 0.05, 0.12),
        (0.02,  1.90, -2.95, 0.88, math.pi * 0.5 - 0.12, 0.42),
        (-0.02, 1.91, -1.25, 0.90, math.pi * 0.5 + 0.10, -0.38),
    ]
    glow_ends = ctx.mb("FireplaceLogEnds", mats["fireplace_glow"])
    for (xoff, ly, lz, ll, rx, rz) in log_specs:
        lx = ecx + xoff
        logs.add_cylinder(lx, ly, lz - ll * 0.45, 0.062, 0.052, ll, segs=10,
                          rot_x=rx, rot_z=rz)
        # glowing heartwood ember ends
        glow_ends.add_sphere(lx, ly + 0.01, lz - ll * 0.42, 0.044, 0.040, 0.044, rings=6, segs=8)
        glow_ends.add_sphere(lx, ly + 0.02, lz + ll * 0.42, 0.038, 0.036, 0.038, rings=6, segs=8)

    # ---- Glass wind guard ----
    glass = ctx.mb("FireplaceGlass", mats["crystal_glass"])
    glass.add_box(13.66, 1.75, -1.8, 0.012, 0.34, 4.4)

    # ------------------------------------------------------------------
    # 3. GalleryTVScreen & GalleryTVBezel
    # ------------------------------------------------------------------
    tv = ctx.mb("GalleryTVScreen", mats["tv_art"])
    p0 = (14.10, 3.35, -5.0)
    p1 = (14.10, 3.35, 1.4)
    p2 = (14.10, 6.95, 1.4)
    p3 = (14.10, 6.95, -5.0)
    tv.add_quad(p0, p1, p2, p3)

    bezel = ctx.mb("GalleryTVBezel", mats["brass"])
    bx = 14.16
    bz0, bz1 = -5.0, 1.4
    by0, by1 = 3.35, 6.95
    bw = 0.06
    bcz = (bz0 + bz1) * 0.5
    bcy = (by0 + by1) * 0.5
    bsz = bz1 - bz0
    bsy = by1 - by0
    bezel.add_box(bx, by1 + bw * 0.5, bcz, 0.04, bw, bsz + bw * 2)
    bezel.add_box(bx, by0 - bw * 0.5, bcz, 0.04, bw, bsz + bw * 2)
    bezel.add_box(bx, bcy, bz0 - bw * 0.5, 0.04, bsy, bw)
    bezel.add_box(bx, bcy, bz1 + bw * 0.5, 0.04, bsy, bw)

    # ------------------------------------------------------------------
    # 4. Pair of Harman Kardon smoked-glass dome acoustic towers
    # ------------------------------------------------------------------
    tower_z = [-7.35, 3.75]
    tower_x = 13.05

    for tz in tower_z:
        # HiFiPlinth
        plinth_mb = ctx.mb("HiFiPlinth", mats["glass_smoke"])
        plinth_mb.add_box(tower_x, 0.04, tz, 0.78, 0.08, 0.78)
        # 4 brass isolation spikes
        spike = ctx.mb("HiFiSpikes", mats["brass"])
        for sx in (-0.30, 0.30):
            for sz in (-0.30, 0.30):
                spike.add_cylinder(tower_x + sx, 0.0, tz + sz, 0.018, 0.008, 0.04, segs=8)

        # HiFiTower cabinet
        tower = ctx.mb("HiFiTower", mats["charcoal"])
        t_y0, t_y1 = 0.14, 2.22
        t_cy = (t_y0 + t_y1) * 0.5
        t_h = t_y1 - t_y0
        # tapered cabinet: bottom wider, top narrower
        tower.add_cylinder(tower_x, t_y0, tz, 0.34, 0.28, t_h, segs=24)

        # curved walnut fluted side ribs
        ribs = ctx.mb("HiFiRibs", mats["walnut_fluted"])
        for side in (-1, 1):
            for k in range(6):
                ang = side * (0.35 + k * 0.18)
                rx = tower_x + math.cos(ang) * 0.30
                rz = tz + math.sin(ang) * 0.30
                ribs.add_box(rx, t_cy, rz, 0.03, t_h * 0.92, 0.03)

        # 3 driver rings + chrome phase plugs facing -X
        drivers = ctx.mb("HiFiDrivers", mats["brass"])
        plugs = ctx.mb("HiFiPlugs", mats["chrome"])
        for dy in (0.65, 1.18, 1.72):
            # concave ring (approximated with cylinder)
            drivers.add_cylinder(tower_x - 0.30, dy - 0.10, tz, 0.14, 0.14, 0.06,
                                 segs=20, rot_z=math.pi * 0.5)
            # chrome phase plug
            plugs.add_sphere(tower_x - 0.34, dy, tz, 0.05, 0.05, 0.05,
                             rings=8, segs=12)

        # HiFiGlassDome
        dome = ctx.mb("HiFiGlassDome", mats["glass_smoke"])
        dome_profile = [
            (0.27, 0.0),
            (0.29, 0.30),
            (0.24, 0.70),
            (0.0, 1.13),
        ]
        dome.add_lathe(tower_x, 2.22, tz, dome_profile, segs=24)

        # internal central waveguide column
        wg = ctx.mb("HiFiWaveguide", mats["chrome"])
        wg.add_cylinder(tower_x, 2.22, tz, 0.04, 0.03, 0.95, segs=12)

        # 360 glowing halo ring inside base of dome
        halo = ctx.mb("HiFiHaloRing", mats["warm_led"])
        halo.add_cylinder(tower_x, 2.34, tz, 0.26, 0.26, 0.02, segs=28,
                          cap_top=False, cap_bot=False)

    # ------------------------------------------------------------------
    # 5. Arc lamp
    # ------------------------------------------------------------------
    base_x, base_z = 12.6, 4.8
    lamp_base = ctx.mb("ArcLampBase", mats["bronze_dark"])
    lamp_base.add_cylinder(base_x, 0.0, base_z, 0.22, 0.18, 0.06, segs=20)
    lamp_base.add_cylinder(base_x, 0.06, base_z, 0.05, 0.04, 0.10, segs=12)

    # Arch spine from base up and over to shade
    arch = ctx.mb("ArcLampArch", mats["chrome"])
    spine = []
    n_pts = 14
    for i in range(n_pts + 1):
        t = i / n_pts
        # quadratic-ish arc from (base_x, 0.16, base_z) to (10.6, 4.95, 2.8)
        x = base_x + (10.6 - base_x) * t
        z = base_z + (2.8 - base_z) * t
        y = 0.16 + (4.95 - 0.16) * math.sin(t * math.pi * 0.5) ** 0.85
        spine.append((x, y, z))
    radii = [0.022] * (n_pts + 1)
    arch.add_curved_tube(spine, radii, segs=8)

    # Hanging dome shade
    shade = ctx.mb("ArcLampShade", mats["brass"])
    shade_profile = [
        (0.0, 0.0),
        (0.10, 0.02),
        (0.18, 0.10),
        (0.20, 0.20),
        (0.16, 0.28),
        (0.0, 0.30),
    ]
    shade.add_lathe(10.6, 4.65, 2.8, shade_profile, segs=20)

    # Bulb
    bulb = ctx.mb("ArcLampBulb", mats["warm_bulb"])
    bulb.add_sphere(10.6, 4.95, 2.8, 0.06, 0.06, 0.06, rings=10, segs=14)
