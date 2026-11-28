import math


def build_east_river_bridge_vista(ctx, mats):
    b = ctx.mb("WestBluffTerrain", mats["headland_rock"])
    b.add_box(45.0, -7.35, 24.0, 18.0, 4.3, 96.0, uv_tile=6.0)
    b.add_box(48.0, -6.2, 24.0, 12.0, 2.0, 96.0, uv_tile=5.0)
    b.add_box(51.0, -5.6, 24.0, 6.0, 1.2, 96.0, uv_tile=4.0)
    for i in range(9):
        z = -22.0 + i * 11.0
        b.add_box(44.0 + (i % 2) * 2.0, -8.6, z, 6.0, 1.6, 5.0, uv_tile=2.0)

    b = ctx.mb("WestSeawall", mats["travertine"])
    b.add_box(53.5, -4.9, 23.0, 1.2, 0.6, 90.0, uv_tile=3.0)
    b.add_box(53.5, -4.55, 23.0, 1.4, 0.12, 90.0, uv_tile=3.0)
    for i in range(23):
        z = -22.0 + i * 4.0
        b.add_cylinder(53.5, -4.55, z, 0.09, 0.09, 0.55, segs=8)

    b = ctx.mb("WestBollards", mats["warm_led"])
    for i in range(23):
        z = -22.0 + i * 4.0
        b.add_sphere(53.5, -3.95, z, 0.11, 0.11, 0.11, rings=6, segs=8)

    b = ctx.mb("WestRiparianBanks", mats["coastal_pine"])
    for i in range(7):
        z = -24.0 + i * 2.4
        b.add_box(50.0, -7.2 + i * 0.35, z, 5.0, 0.5, 2.2, uv_tile=2.0)
    for i in range(11):
        z = -23.0 + i * 1.6
        b.add_cylinder(48.5 + (i % 3) * 0.9, -7.0, z, 0.18, 0.05, 1.4, segs=6)

    b = ctx.mb("EastRiverChannel", mats["river_water"])
    nx, nz = 14, 18
    x0, x1 = 52.0, 96.0
    z0, z1 = -24.0, 88.0
    for i in range(nx):
        for j in range(nz):
            xa = x0 + (x1 - x0) * i / nx
            xb = x0 + (x1 - x0) * (i + 1) / nx
            za = z0 + (z1 - z0) * j / nz
            zb = z0 + (z1 - z0) * (j + 1) / nz
            b.add_quad((xa, -8.50, za), (xb, -8.50, za),
                       (xb, -8.50, zb), (xa, -8.50, zb),
                       uv_scale=(1.0, 1.0))

    b = ctx.mb("EastEstuaryMouth", mats["coastal_foam"])
    for cx, cz in ((57.0, -22.5), (90.5, -25.5)):
        b.add_cylinder(cx, -8.18, cz, 3.1, 3.0, 0.08, segs=18)
    b = ctx.mb("EstuarySandbars", mats["headland_rock"])
    b.add_cylinder(57.0, -9.20, -22.5, 4.4, 2.7, 1.35, segs=18)
    b.add_cylinder(90.5, -9.20, -25.5, 4.8, 3.0, 1.35, segs=18)

    b = ctx.mb("EstuaryJetties", mats["headland_rock"])
    for i in range(6):
        b.add_box(56.0 + i * 0.9, -8.4, -22.0 - i * 0.6, 1.2, 0.9, 1.2, uv_tile=1.5)
        b.add_box(92.0 - i * 0.9, -8.4, -26.0 - i * 0.6, 1.2, 0.9, 1.2, uv_tile=1.5)

    b = ctx.mb("LighthouseBeacon", mats["warm_led"])
    b.add_cylinder(56.0, -8.0, -24.5, 0.35, 0.28, 3.2, segs=10)
    b.add_sphere(56.0, -4.6, -24.5, 0.32, 0.32, 0.32, rings=8, segs=10)
    b.add_cylinder(92.0, -8.0, -28.5, 0.35, 0.28, 3.2, segs=10)
    b.add_sphere(92.0, -4.6, -28.5, 0.32, 0.32, 0.32, rings=8, segs=10)

    b = ctx.mb("EastPeninsulaTerrain", mats["headland_rock"])
    b.add_box(141.5, -7.0, 33.5, 107.0, 5.0, 123.0, uv_tile=8.0)
    b.add_box(141.5, -5.2, 33.5, 103.0, 1.6, 119.0, uv_tile=7.0)

    b = ctx.mb("EastEmbankment", mats["travertine"])
    b.add_box(90.5, -4.35, 33.5, 3.0, 0.5, 123.0, uv_tile=4.0)
    b.add_box(90.5, -4.05, 33.5, 3.4, 0.12, 123.0, uv_tile=4.0)
    for i in range(31):
        z = -28.0 + i * 4.0
        b.add_cylinder(90.5, -4.05, z, 0.08, 0.08, 0.5, segs=8)

    b = ctx.mb("EastParkway", mats["coastal_pine"])
    for i in range(14):
        z = -26.0 + i * 8.5
        b.add_box(96.0, -4.15, z, 6.0, 0.35, 3.0, uv_tile=2.0)
        b.add_cylinder(96.0, -4.0, z, 0.22, 0.06, 1.8, segs=6)

    ax, ay, az = 50.0, -4.5, -8.0
    bx, by, bz = 94.0, -4.5, -18.0
    dx, dz = bx - ax, bz - az
    L = math.hypot(dx, dz)
    rot = math.atan2(dx, dz)
    mx, mz = (ax + bx) * 0.5, (az + bz) * 0.5
    ux, uz = dx / L, dz / L
    px, pz = -uz, ux

    b = ctx.mb("EastBridgeTowers", mats["bridge_steel"])
    tower_ts = [0.24, 0.76]
    for t in tower_ts:
        cx = ax + dx * t
        cz = az + dz * t
        for s in (-1, 1):
            ox, oz = px * 2.4 * s, pz * 2.4 * s
            b.add_cylinder(cx + ox, -4.0, cz + oz, 0.42, 0.24, 18.5, segs=12)
        for h in (2.5, 8.0, 13.5):
            b.add_box(cx, -4.0 + h, cz, 0.35, 0.35, 5.2, rot_y=rot, uv_tile=1.0)
        b.add_sphere(cx, 14.7, cz, 0.28, 0.28, 0.28, rings=6, segs=8)

    b = ctx.mb("EastBridgeCaissons", mats["travertine"])
    for t in tower_ts:
        cx = ax + dx * t
        cz = az + dz * t
        b.add_cylinder(cx, -10.5, cz, 2.2, 1.8, 6.7, segs=14)

    b = ctx.mb("EastRiverBridge", mats["obsidian_bezel"])
    b.add_box(mx, -4.35, mz, 4.4, 0.35, L, rot_y=rot, uv_tile=2.0)
    b.add_box(mx, -4.15, mz, 0.5, 0.08, L, rot_y=rot, uv_tile=2.0)

    b = ctx.mb("EastBridgeEdgeStrips", mats["warm_led"])
    for s in (-1, 1):
        ox, oz = px * 2.1 * s, pz * 2.1 * s
        b.add_box(mx + ox, -4.12, mz + oz, 0.12, 0.06, L, rot_y=rot, uv_tile=2.0)

    b = ctx.mb("EastBridgeCables", mats["steel"])
    cable_pts = []
    n = 15
    for i in range(n):
        t = i / (n - 1)
        cx = ax + dx * t
        cz = az + dz * t
        if t < 0.24:
            u = t / 0.24
            y = -4.2 + (14.2 + 4.2) * (u * u)
        elif t < 0.76:
            u = (t - 0.24) / 0.52
            y = 14.2 - (14.2 + 0.8) * (4.0 * u * (1.0 - u))
        else:
            u = (t - 0.76) / 0.24
            y = 14.2 - (14.2 + 4.2) * (u * u)
        cable_pts.append((cx, y, cz))
    for s in (-1, 1):
        ox, oz = px * 2.4 * s, pz * 2.4 * s
        pts = [(p[0] + ox, p[1], p[2] + oz) for p in cable_pts]
        b.add_curved_tube(pts, [0.065] * n, segs=8)

    b = ctx.mb("EastBridgeSuspenders", mats["steel"])
    for i in range(1, 23):
        t = i / 23.0
        cx = ax + dx * t
        cz = az + dz * t
        if t < 0.24:
            u = t / 0.24
            y = -4.2 + (14.2 + 4.2) * (u * u)
        elif t < 0.76:
            u = (t - 0.24) / 0.52
            y = 14.2 - (14.2 + 0.8) * (4.0 * u * (1.0 - u))
        else:
            u = (t - 0.76) / 0.24
            y = 14.2 - (14.2 + 4.2) * (u * u)
        for s in (-1, 1):
            ox, oz = px * 2.4 * s, pz * 2.4 * s
            b.add_cylinder(cx + ox, -4.2, cz + oz, 0.016, 0.016, y + 4.2, segs=6)

    towers = [
        (104, -14, 22, 8, 8), (118, 4, 30, 9, 9), (132, -8, 26, 8, 8),
        (146, 18, 34, 10, 10), (160, -2, 28, 9, 9), (174, 26, 38, 11, 11),
        (110, 34, 24, 8, 8), (124, 48, 32, 9, 9), (138, 62, 28, 8, 8),
        (152, 44, 36, 10, 10), (166, 58, 30, 9, 9), (180, 72, 42, 11, 11),
        (100, 62, 20, 7, 7), (114, 76, 26, 8, 8), (128, 84, 22, 7, 7),
        (142, 78, 30, 9, 9),
    ]
    b = ctx.mb("EastCitySkyscrapers", mats["city_facade"])
    for (cx, cz, h, sx, sz) in towers:
        b.add_box(cx, -4.5 + h * 0.5, cz, sx, h, sz, uv_tile=1.0)
    b = ctx.mb("EastCityPodiums", mats["travertine"])
    for (cx, cz, h, sx, sz) in towers:
        b.add_box(cx, -4.0, cz, sx + 1.5, 1.0, sz + 1.5, uv_tile=2.0)
    b = ctx.mb("EastCityFins", mats["obsidian_bezel"])
    for (cx, cz, h, sx, sz) in towers:
        b.add_box(cx, -4.5 + h + 1.35, cz, sx * 0.72, 2.7, sz * 0.72, uv_tile=1.5)
        b.add_box(cx - sx * 0.48, -4.5 + h * 0.5, cz, 0.28, h, 0.35, uv_tile=1.0)
        b.add_box(cx + sx * 0.48, -4.5 + h * 0.5, cz, 0.28, h, 0.35, uv_tile=1.0)
    b = ctx.mb("EastCitySpires", mats["steel"])
    for (cx, cz, h, sx, sz) in towers:
        b.add_cylinder(cx, -4.5 + h, cz, 0.35, 0.05, 3.5, segs=8)
    b = ctx.mb("EastCityHalos", mats["warm_led"])
    for (cx, cz, h, sx, sz) in towers:
        b.add_sphere(cx, -4.5 + h + 3.6, cz, 0.22, 0.22, 0.22, rings=6, segs=8)

    yachts = [(66.0, -24.0), (75.0, -42.0), (62.0, 18.0)]
    b = ctx.mb("RiverYachts", mats["sail_canvas"])
    for (cx, cz) in yachts:
        b.add_box(cx, -8.18, cz, 2.2, 0.5, 6.0, uv_tile=1.5)
        b.add_box(cx, -7.92, cz + 1.5, 1.6, 0.4, 2.4, uv_tile=1.5)
    b = ctx.mb("YachtCabins", mats["obsidian_bezel"])
    for (cx, cz) in yachts:
        b.add_box(cx, -7.57, cz + 0.8, 1.4, 0.5, 2.0, uv_tile=1.0)
        b.add_cylinder(cx, -7.32, cz - 1.5, 0.05, 0.05, 2.2, segs=6)
