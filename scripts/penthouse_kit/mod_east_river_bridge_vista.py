import math

def build_east_river_bridge_vista(ctx, mats):
    # ---------------------------------------------------------------
    # 1. Twilight River Surface (sits above -8.4 coastal cutoff on East side!)
    # ---------------------------------------------------------------
    water = ctx.mb('EastRiverWater', mats['river_twilight'])
    water.add_box(126.0, -6.2, -8.0, 164.0, 0.4, 156.0, uv_tile=6.0)

    glints = ctx.mb('RiverLightGlints', mats['warm_bulb'])
    for i in range(14):
        gx = 54.0 + (i % 7) * 14.0
        gz = 18.0 - (i // 7) * 26.0 - i * 2.5
        glints.add_box(gx, -5.92, gz, 10.0, 0.14, 1.8, uv_tile=1.0, rot_y=-0.62)

    # ---------------------------------------------------------------
    # 2. Illuminated Cable-Stayed Bridge (centered right outside East curved glass!)
    # ---------------------------------------------------------------
    rot = -0.62
    deck = ctx.mb('EastRiverBridge', mats['charcoal'])
    deck.add_box(86.0, 2.2, -10.0, 88.0, 1.5, 9.2, uv_tile=3.0, rot_y=rot)

    glow = ctx.mb('BridgeDeckGlow', mats['warm_led'])
    glow.add_box(86.0, 3.1, -6.2, 88.0, 0.42, 0.65, uv_tile=2.0, rot_y=rot)
    glow.add_box(86.0, 3.1, -13.8, 88.0, 0.42, 0.65, uv_tile=2.0, rot_y=rot)

    tail = ctx.mb('BridgeDeckGlow', mats['warm_bulb'])
    for i in range(12):
        t = i / 11.0
        tx = 50.0 + t * 72.0
        tz = 16.0 - t * 52.0
        tail.add_sphere(tx, 3.35, tz, 0.34, 0.34, 0.34, rings=6, segs=8)

    # Towers framed heroically in East curved panoramic view
    towers = ctx.mb('EastRiverBridge', mats['steel'])
    tower_defs = [(68.0, 4.0), (102.0, -22.0)]
    for tx, tz in tower_defs:
        towers.add_box(tx - 2.6, 8.0, tz, 1.8, 30.0, 1.8, uv_tile=2.0)
        towers.add_box(tx + 2.6, 8.0, tz, 1.8, 30.0, 1.8, uv_tile=2.0)
        towers.add_box(tx, 22.0, tz, 7.2, 1.9, 1.9, uv_tile=2.0)
        towers.add_box(tx, 12.0, tz, 7.2, 1.3, 1.5, uv_tile=2.0)

    pylon = ctx.mb('BridgeDeckGlow', mats['warm_led'])
    for tx, tz in tower_defs:
        pylon.add_box(tx - 2.6, 8.0, tz + 1.0, 0.38, 29.0, 0.38, uv_tile=1.0)
        pylon.add_box(tx + 2.6, 8.0, tz + 1.0, 0.38, 29.0, 0.38, uv_tile=1.0)

    # Stay cables
    cables = ctx.mb('EastRiverBridge', mats['warm_bulb'])
    for tx, tz in tower_defs:
        for k in range(8):
            frac = k / 7.0
            dx = (frac - 0.5) * 34.0
            dz = (frac - 0.5) * 24.0
            top = (tx, 22.5, tz)
            bot = (tx + dx, 3.0, tz + dz)
            mid = ((top[0] + bot[0]) * 0.5, (top[1] + bot[1]) * 0.5, (top[2] + bot[2]) * 0.5)
            cables.add_curved_tube([top, mid, bot], [0.16, 0.14, 0.12], segs=6)

    # ---------------------------------------------------------------
    # 3. Twilight City Waterfront Skyline
    # ---------------------------------------------------------------
    towers_mb = ctx.mb('EastSkylineTowers', mats['city_facade'])
    spires = ctx.mb('SkylineSpires', mats['warm_bulb'])
    import random
    rng = random.Random(7)
    for i in range(28):
        bx = 112.0 + rng.uniform(0.0, 56.0)
        bz = -76.0 + rng.uniform(0.0, 126.0)
        h = rng.uniform(18.0, 62.0)
        w = rng.uniform(5.5, 9.5)
        d = rng.uniform(5.5, 9.5)
        towers_mb.add_box(bx, h * 0.5 - 6.5, bz, w, h, d, uv_tile=2.0)
        if rng.random() > 0.30:
            spires.add_cylinder(bx, h - 6.5, bz, 0.5, 0.05, rng.uniform(3.0, 8.0), segs=8)
