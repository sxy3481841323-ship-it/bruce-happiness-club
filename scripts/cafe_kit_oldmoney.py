def build_cafe_oldmoney_millwork(mb, mats):
    M = mats
    def box(name, mat, cx, cy, cz, sx, sy, sz, tile=0.0, ry=0.0):
        b = mb(name, M[mat]); b.add_box(cx, cy, cz, sx, sy, sz, tile, ry); return b
    def quad(name, mat, p0, p1, p2, p3, uv=(1.0, 1.0)):
        b = mb(name, M[mat]); b.add_quad(p0, p1, p2, p3, uv); return b
    def cyl(name, mat, cx, y0, cz, rb, rt, h, segs=16):
        b = mb(name, M[mat]); b.add_cylinder(cx, y0, cz, rb, rt, h, segs); return b

    # ---------- 1. RUGS + FLOOR INLAY ----------
    quad("rug_salon", "rug_salon", (-10.9, 0.024, 9.5), (-1.7, 0.024, 9.5),
         (-1.7, 0.024, 0.9), (-10.9, 0.024, 0.9))
    quad("rug_aubusson", "rug_aubusson", (-10.9, 0.024, -1.4), (-1.7, 0.024, -1.4),
         (-1.7, 0.024, -11.4), (-10.9, 0.024, -11.4))
    for z in (0.83, 9.57):
        box("fringe1", "travertine", -6.3, 0.020, z, 9.2, 0.008, 0.14)
    for z in (-11.47, -1.33):
        box("fringe2", "travertine", -6.3, 0.020, z, 9.2, 0.008, 0.14)
    for x in (-11.0, 10.9):
        box("inlay_x", "walnut_dark", x, 0.012, -0.85, 0.10, 0.006, 40.7)
        box("inlay_xb", "brass", x, 0.014, -0.85, 0.04, 0.004, 40.7)
    for z in (-21.2, 19.5):
        box("inlay_z", "walnut_dark", -0.05, 0.012, z, 21.9, 0.006, 0.10)
        box("inlay_zb", "brass", -0.05, 0.014, z, 21.9, 0.004, 0.04)

    # ---------- 2. SOUTH ENTRANCE WALL (Z=+20.2) ----------
    box("ent_frame", "walnut_dark", 0.0, 5.3, 19.95, 4.5, 10.6, 0.30)
    box("ent_recess", "walnut_fluted", 0.0, 5.3, 19.80, 3.9, 10.2, 0.10)
    for sx in (-1.0, 1.0):
        box("door", "walnut_fluted", sx*0.95, 4.0, 19.72, 1.75, 7.6, 0.12)
        box("door_glass", "glass_reed", sx*0.95, 5.6, 19.66, 1.35, 3.6, 0.04)
        box("door_pull", "brass", sx*0.18, 4.0, 19.60, 0.10, 2.4, 0.10)
        box("kick", "brass", sx*0.95, 0.25, 19.66, 1.75, 0.45, 0.04)
    box("transom", "glass_reed", 0.0, 9.4, 19.72, 3.9, 2.0, 0.06)
    for i in range(5):
        box("mull", "brass", -1.95 + i*0.975, 9.4, 19.66, 0.06, 2.0, 0.06)
    box("transom_rail", "brass", 0.0, 8.4, 19.66, 3.9, 0.10, 0.08)

    for side in (-1, 1):
        x0 = side * 2.25
        xc = side * 6.775
        box("dado", "walnut_fluted", xc, 1.675, 20.00, 9.05, 3.35, 0.20)
        box("dado_rail", "brass", xc, 3.42, 19.94, 9.05, 0.14, 0.10)
        box("cornice", "walnut_dark", xc, 14.95, 19.90, 9.05, 0.55, 0.30)
        for px in (-10.8, -6.6, -2.35, 2.35, 6.6, 10.8):
            if side * px > 0:
                box("pil", "walnut_fluted", px, 7.4, 19.92, 0.42, 14.8, 0.26)
                box("pil_base", "brass", px, 0.20, 19.86, 0.52, 0.40, 0.30)
                box("pil_cap", "brass", px, 14.55, 19.86, 0.52, 0.30, 0.30)
        for bx in (-8.7, -4.5, 8.7):
            if side * bx > 0:
                # Raised Marmorino boiserie centre panel surrounded by hollow 4-bar walnut & brass mouldings
                box("frame", "marmorino", bx, 9.1, 20.00, 3.4, 9.4, 0.08, tile=4.2)
                for dy in (-4.45, 4.45):
                    box("frame_h", "walnut_dark", bx, 9.1 + dy, 19.91, 3.05, 0.18, 0.08)
                    box("frame_hb", "brass", bx, 9.1 + dy * 0.94, 19.90, 2.75, 0.05, 0.06)
                for dx in (-1.45, 1.45):
                    box("frame_v", "walnut_dark", bx + dx, 9.1, 19.91, 0.18, 9.05, 0.08)
                    box("frame_vb", "brass", bx + dx * 0.94, 9.1, 19.90, 0.05, 8.40, 0.06)
                box("sconce", "brass", bx, 13.9, 19.80, 0.30, 0.30, 0.20)
                box("sconce_glow", "warm_glow", bx, 14.15, 19.80, 0.22, 0.22, 0.14)

    # Bookcase niche (protrudes cleanly in front of South wall at -Z)
    box("bc_case", "walnut_dark", 4.475, 7.575, 19.72, 3.65, 7.65, 0.36)
    box("bc_back", "warm_glow", 4.475, 7.575, 19.53, 3.35, 7.30, 0.03)
    for i in range(4):
        y = 4.6 + i * 1.7
        box("bc_shelf", "walnut_fluted", 4.475, y, 19.50, 3.42, 0.11, 0.42)
        for j in range(4):
            x = 3.2 + j * 0.85
            if (i + j) % 2 == 0:
                cyl("canister", "brass", x, y + 0.055, 19.44, 0.13, 0.13, 0.52, segs=12)
            elif (i + j) % 3 == 0:
                cyl("carafe", "ceramic", x, y + 0.055, 19.44, 0.15, 0.09, 0.46, segs=12)
            else:
                box("book", "oak", x, y + 0.27, 19.44, 0.20, 0.42, 0.30)

    # ---------- 3. RIGHT WALL (X=+11.5) ----------
    for z0, z1 in ((-22.0, -7.5), (11.6, 20.0)):
        zc = (z0 + z1) / 2; ln = z1 - z0
        box("rdado", "walnut_fluted", 11.36, 1.675, zc, 0.20, 3.35, ln)
        box("rrail", "brass", 11.30, 3.42, zc, 0.10, 0.14, ln)
    for pz in (-21.2, -16.8, -8.0, 12.0, 19.4):
        box("rpil", "walnut_fluted", 11.30, 7.4, pz, 0.26, 14.8, 0.42)
        box("rpil_b", "brass", 11.24, 0.20, pz, 0.30, 0.40, 0.52)
        box("rpil_c", "brass", 11.24, 14.55, pz, 0.30, 0.30, 0.52)
    for pz in (-19.0, 15.7):
        box("rframe", "marmorino", 11.40, 9.0, pz, 0.08, 9.2, 3.4, tile=4.2)
        for dy in (-4.35, 4.35):
            box("rf_h", "walnut_dark", 11.32, 9.0 + dy, pz, 0.08, 0.18, 3.05)
            box("rf_hb", "brass", 11.31, 9.0 + dy * 0.94, pz, 0.06, 0.05, 2.75)
        for dz in (-1.45, 1.45):
            box("rf_v", "walnut_dark", 11.32, 9.0, pz + dz, 0.08, 8.85, 0.18)
            box("rf_vb", "brass", 11.31, 9.0, pz + dz * 0.94, 0.06, 8.20, 0.05)

    # Museum shadow-box around GeoArt
    for y in (10.85, 5.95):
        box("sb_h", "walnut_dark", 11.40, y, -12.6, 0.24, 0.30, 4.10)
        box("sb_hi", "brass", 11.28, y, -12.6, 0.06, 0.14, 3.90)
    for z in (-14.65, -10.55):
        box("sb_v", "walnut_dark", 11.40, 8.4, z, 0.24, 4.90, 0.30)
        box("sb_vi", "brass", 11.28, 8.4, z, 0.06, 4.70, 0.14)
    box("plight", "brass", 10.95, 11.25, -12.6, 0.20, 0.14, 3.6)
    box("plight_g", "warm_glow", 10.95, 11.14, -12.6, 0.14, 0.06, 3.4)

    # ---------- 4. LEFT COLUMNS + BACK PILLAR ----------
    for cz in (11.8, 2.0, -9.8, -21.8):
        box("col_flute", "walnut_fluted", -11.4, 7.4, cz, 1.10, 14.8, 1.10)
        for y in (0.35, 3.42, 13.8):
            box("col_collar", "brass", -11.4, y, cz, 1.22, 0.22, 1.22)
    box("pillar", "walnut_fluted", 1.3, 7.4, -21.8, 1.10, 14.8, 1.10)
    for y in (0.35, 3.42, 13.8):
        box("pil_collar", "brass", 1.3, y, -21.8, 1.22, 0.22, 1.22)
    # Center portal crown & left/back header beam walnut-brass fascia trims
    box("frieze_center", "walnut_dark", 0.0, 14.95, 19.90, 4.6, 0.55, 0.30)
    box("frieze_center_b", "brass", 0.0, 14.65, 19.86, 4.6, 0.08, 0.32)
    box("frieze_left", "walnut_dark", -10.82, 14.25, -1.0, 0.16, 0.45, 42.0)
    box("frieze_left_b", "brass", -10.78, 14.00, -1.0, 0.08, 0.08, 42.0)
    box("frieze_back", "walnut_dark", -5.0, 14.25, -21.22, 13.0, 0.45, 0.16)
    box("frieze_back_b", "brass", -5.0, 14.00, -21.18, 13.0, 0.08, 0.08)
