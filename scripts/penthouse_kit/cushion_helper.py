import math


def add_designer_pillow(b_body, b_pipe, cx, cy, cz, w=0.52, h=0.46, thick=0.16, yaw=0.0, tilt=-0.22):
    N = 13
    ct, st = math.cos(tilt), math.sin(tilt)
    cy_y, sy_y = math.cos(yaw), math.sin(yaw)

    def surf(u, v):
        k = 1.0 + 0.14 * (u * u) * (v * v)
        rx = u * (w * 0.5) * k
        chop = 0.055 * h * math.exp(-((u * 2.4) ** 2)) * max(0.0, v - 0.35)
        ry = v * (h * 0.5) * k - chop
        bulge = (math.cos(u * math.pi * 0.5) ** 0.72) * (math.cos(v * math.pi * 0.5) ** 0.72)
        return rx, ry, bulge

    def place(u, v, sign):
        rx, ry, bulge = surf(u, v)
        rz = sign * (thick * 0.5) * bulge
        yp = ry * ct - rz * st
        zp = ry * st + rz * ct
        wx = cx + rx * cy_y + zp * sy_y
        wz = cz - rx * sy_y + zp * cy_y
        wy = cy + yp
        return (wx, wy, wz)

    def normal(u, v, sign):
        e = 1e-3
        u0, u1 = max(-1.0, u - e), min(1.0, u + e)
        v0, v1 = max(-1.0, v - e), min(1.0, v + e)
        p = place(u, v, sign)
        pu = place(u1, v, sign)
        pv = place(u, v1, sign)
        du = (pu[0] - p[0], pu[1] - p[1], pu[2] - p[2])
        dv = (pv[0] - p[0], pv[1] - p[1], pv[2] - p[2])
        nx = du[1] * dv[2] - du[2] * dv[1]
        ny = du[2] * dv[0] - du[0] * dv[2]
        nz = du[0] * dv[1] - du[1] * dv[0]
        ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
        nx, ny, nz = nx / ln, ny / ln, nz / ln
        if sign < 0:
            nx, ny, nz = -nx, -ny, -nz
        return (nx, ny, nz)

    def uv_of(i, j):
        return (-1.0 + 2.0 * i / (N - 1), -1.0 + 2.0 * j / (N - 1))

    for sign in (1, -1):
        for i in range(N - 1):
            for j in range(N - 1):
                u0, v0 = uv_of(i, j)
                u1, v1 = uv_of(i + 1, j + 1)
                p00 = place(u0, v0, sign)
                p10 = place(u1, v0, sign)
                p01 = place(u0, v1, sign)
                p11 = place(u1, v1, sign)
                n00 = normal(u0, v0, sign)
                n10 = normal(u1, v0, sign)
                n01 = normal(u0, v1, sign)
                n11 = normal(u1, v1, sign)
                if sign > 0:
                    b_body.add_tri_raw(p00, p10, p11, (u0, v0), (u1, v0), (u1, v1), n00, n10, n11)
                    b_body.add_tri_raw(p00, p11, p01, (u0, v0), (u1, v1), (u0, v1), n00, n11, n01)
                else:
                    b_body.add_tri_raw(p00, p11, p10, (u0, v0), (u1, v1), (u1, v0), n00, n11, n10)
                    b_body.add_tri_raw(p00, p01, p11, (u0, v0), (u0, v1), (u1, v1), n00, n01, n11)

    if b_pipe is not None:
        M = 28
        pts = []
        for k in range(M):
            t = 2.0 * math.pi * k / M
            c, s = math.cos(t), math.sin(t)
            m = max(abs(c), abs(s))
            u, v = c / m, s / m
            pts.append(place(u, v, 1))
        b_pipe.add_curved_tube(pts, [0.008] * len(pts), segs=6)
