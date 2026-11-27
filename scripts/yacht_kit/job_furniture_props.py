import os
import sys
import math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from yacht_kit.yacht_prim_lib import YachtGLBBuilder
from yacht_kit.tex_helpers import load_bundle


def build():
    gb = YachtGLBBuilder("yacht_furniture_props")

    b_teak = load_bundle("teak_frame")
    b_linen = load_bundle("outdoor_linen")
    b_leather = load_bundle("saddle_leather")
    b_crest = load_bundle("saddle_leather_crest")
    b_stitch = load_bundle("stitch_strip")
    b_pvd = load_bundle("pvd_brushed")

    m_teak = gb.add_pbr_material("teak_frame", base_bytes=b_teak["base_bytes"], base_mime=b_teak["base_mime"],
                                 orm_bytes=b_teak["orm_bytes"], normal_bytes=b_teak["norm_bytes"],
                                 roughness=0.55, metalness=0.0)
    m_linen = gb.add_pbr_material("linen", base_bytes=b_linen["base_bytes"], base_mime=b_linen["base_mime"],
                                  orm_bytes=b_linen["orm_bytes"], normal_bytes=b_linen["norm_bytes"],
                                  roughness=0.85, metalness=0.0, double_sided=True)
    m_leather = gb.add_pbr_material("leather", base_bytes=b_leather["base_bytes"], base_mime=b_leather["base_mime"],
                                    orm_bytes=b_leather["orm_bytes"], normal_bytes=b_leather["norm_bytes"],
                                    roughness=0.62, metalness=0.0)
    m_crest = gb.add_pbr_material("crest_leather", base_bytes=b_crest["base_bytes"], base_mime=b_crest["base_mime"],
                                  orm_bytes=b_crest["orm_bytes"], normal_bytes=b_crest["norm_bytes"],
                                  roughness=0.62, metalness=0.0, clamp_uv=True)
    m_stitch = gb.add_pbr_material("stitch", base_bytes=b_stitch["base_bytes"], base_mime=b_stitch["base_mime"],
                                   orm_bytes=b_stitch["orm_bytes"], normal_bytes=b_stitch["norm_bytes"],
                                   roughness=0.75, metalness=0.0)
    m_pvd = gb.add_pbr_material("pvd", base_bytes=b_pvd["base_bytes"], base_mime=b_pvd["base_mime"],
                                orm_bytes=b_pvd["orm_bytes"], normal_bytes=b_pvd["norm_bytes"],
                                roughness=0.28, metalness=1.0)
    m_rope = gb.add_pbr_material("rope", base_factor=(0.80, 0.74, 0.62, 1.0), roughness=0.88, metalness=0.0)
    m_glass = gb.add_pbr_material("crystal_glass", base_factor=(0.94, 0.98, 1.0, 1.0),
                                  roughness=0.06, metalness=0.0, transmission=0.92, ior=1.50)
    m_piping = gb.add_pbr_material("piping_trim", base_factor=(0.28, 0.22, 0.19, 1.0),
                                   roughness=0.72, metalness=0.0)

    # ---------------- Loungers ----------------
    def lounger(cx, cy, cz):
        m = gb.mesh(m_teak, "lounger_frame")
        for sx in (-0.26, 0.26):
            m.add_chamfer_box((cx + sx, cy + 0.19, cz), (0.028, 0.038, 1.63), bevel=0.004, uv_tile=1.0)
        for zz in (-0.78, 0.78):
            m.add_chamfer_box((cx, cy + 0.19, cz + zz), (0.55, 0.038, 0.028), bevel=0.004, uv_tile=1.0)
        for sx in (-0.24, 0.24):
            for zz in (-0.72, 0.72):
                m.add_chamfer_box((cx + sx, cy + 0.09, cz + zz), (0.028, 0.18, 0.028), bevel=0.003, uv_tile=1.0)
        mp = gb.mesh(m_pvd, "lounger_pins")
        for sx in (-0.26, 0.26):
            mp.add_tube((cx + sx - 0.02, cy + 0.21, cz - 0.30), (cx + sx + 0.02, cy + 0.21, cz - 0.30),
                        0.008, segs=12, cap=True)
        ms = gb.mesh(m_linen, "lounger_sling")
        nu, nv = 6, 16
        pos = np.zeros((nu, nv, 3), dtype=np.float32)
        uv = np.zeros((nu, nv, 2), dtype=np.float32)
        for i in range(nu):
            u = i / (nu - 1)
            arc = 0.0
            prev_pt = None
            for j in range(nv):
                v = j / (nv - 1)
                z = -0.78 + v * 1.56
                if z <= 0.10:
                    y = cy + 0.212 + math.sin(u * math.pi) * 0.012
                else:
                    t = (z - 0.10) / 0.68
                    y = cy + 0.212 + t * 0.54
                x = cx - 0.24 + u * 0.48
                pt = (x, y, cz + z)
                if prev_pt is not None:
                    arc += math.hypot(pt[1] - prev_pt[1], pt[2] - prev_pt[2])
                prev_pt = pt
                pos[i, j] = pt
                uv[i, j] = ((u * 0.48) / 0.16, arc / 0.16)
        ms.add_grid(pos, uv, flip=True, smooth_normals=True)

    lounger(0.62, 1.28, -4.45)
    lounger(1.44, 1.28, -4.45)

    # ---------------- Round teak table ----------------
    mt = gb.mesh(m_teak, "table")
    tx, ty, tz = 1.22, 1.30, -6.55
    top_y = 2.03
    segs = 32
    r = 0.39
    poly = [(tx + r * math.cos(2 * math.pi * i / segs), tz + r * math.sin(2 * math.pi * i / segs)) for i in range(segs)]
    mt.add_prism(poly, top_y - 0.028, top_y, uv_tile=1.0, caps=(True, True))
    for i in range(3):
        a = 2 * math.pi * i / 3 + math.pi / 6
        lx = tx + 0.30 * math.cos(a)
        lz = tz + 0.30 * math.sin(a)
        mt.add_tube((lx, ty, lz), (tx + 0.10 * math.cos(a), top_y - 0.028, tz + 0.10 * math.sin(a)),
                    0.022, 0.016, segs=10, cap=True)
    mn = gb.mesh(m_linen, "napkin")
    mn.add_chamfer_box((tx + 0.05, top_y + 0.008, tz - 0.05), (0.14, 0.016, 0.14), bevel=0.003, uv_tile=1.0)

    # ---------------- Mooring cleat + rope ----------------
    mc = gb.mesh(m_pvd, "cleat")
    cx, cy, cz = 1.52, 1.26, -8.55
    mc.add_chamfer_box((cx, cy + 0.01, cz), (0.46, 0.02, 0.10), bevel=0.004, uv_tile=1.0)
    for sx in (-0.14, 0.14):
        mc.add_tube((cx + sx, cy + 0.02, cz), (cx + sx, cy + 0.15, cz), 0.019, segs=16, cap=True)
    mc.add_tube((cx - 0.14, cy + 0.15, cz), (cx + 0.14, cy + 0.15, cz), 0.019, segs=16, cap=True)

    mr = gb.mesh(m_rope, "rope_coil")
    turns = 5
    nu, nv = 8, 60
    pos = np.zeros((nu, nv, 3), dtype=np.float32)
    uv = np.zeros((nu, nv, 2), dtype=np.float32)
    for i in range(nu):
        u = i / (nu - 1)
        for j in range(nv):
            v = j / (nv - 1)
            ang = v * 2 * math.pi * turns
            rx = 0.20 + 0.03 * math.cos(ang * 0.5)
            rz = 0.13 + 0.03 * math.sin(ang * 0.5)
            px = cx + rx * math.cos(ang)
            pz = cz + rz * math.sin(ang)
            py = cy + 0.03 + v * 0.10
            nx = math.cos(ang)
            nz = math.sin(ang)
            rr = 0.013
            ox = rr * math.cos(u * 2 * math.pi)
            oy = rr * math.sin(u * 2 * math.pi)
            pos[i, j] = (px + nx * ox, py + oy, pz + nz * ox)
            uv[i, j] = (u, v * turns)
    mr.add_grid(pos, uv, smooth_normals=True, seam_u=True)

    # ---------------- Dog cushion ----------------
    md = gb.mesh(m_linen, "dog_cushion")
    dx, dy, dz = -1.05, 1.328, -3.85
    md.add_chamfer_box((dx, dy + 0.0275, dz), (0.78, 0.055, 0.43), bevel=0.015, uv_tile=1.0)
    mp = gb.mesh(m_piping, "dog_piping")
    hw, hd = 0.39, 0.215
    corners = [(dx - hw, dz - hd), (dx + hw, dz - hd), (dx + hw, dz + hd), (dx - hw, dz + hd)]
    for i in range(4):
        p0 = corners[i]
        p1 = corners[(i + 1) % 4]
        mp.add_tube((p0[0], dy + 0.0275, p0[1]), (p1[0], dy + 0.0275, p1[1]), 0.003, segs=8, cap=True)

    # ---------------- Barware ----------------
    bx, by, bz = 0.0, 2.38, 1.22
    mg = gb.mesh(m_glass, "glasses")
    for gx in (-0.10, 0.10):
        poly = []
        for i in range(4):
            a = 2 * math.pi * i / 4 + math.pi / 4
            poly.append((bx + gx + 0.036 * math.cos(a), bz + 0.036 * math.sin(a)))
        mg.add_prism(poly, by, by + 0.098, uv_tile=1.0, caps=(True, True))

    mb = gb.mesh(m_pvd, "ice_bucket")
    poly_b = []
    for i in range(20):
        a = 2 * math.pi * i / 20
        poly_b.append((bx + 0.09 * math.cos(a), bz + 0.09 * math.sin(a)))
    mb.add_prism(poly_b, by, by + 0.185, uv_tile=1.0, caps=(True, True))

    mi = gb.mesh(m_glass, "ice_cubes")
    for ix, iz in [(-0.03, -0.02), (0.03, 0.02), (0.0, 0.04), (-0.02, 0.03)]:
        mi.add_box((bx + ix, by + 0.16, bz + iz), (0.025, 0.025, 0.025), uv_tile=1.0)

    mbt = gb.mesh(m_glass, "bottle")
    poly_bt = []
    for i in range(16):
        a = 2 * math.pi * i / 16
        poly_bt.append((bx + 0.037 * math.cos(a), bz + 0.037 * math.sin(a)))
    mbt.add_prism(poly_bt, by, by + 0.20, uv_tile=1.0, caps=(True, True))
    mbt.add_tube((bx, by + 0.20, bz), (bx, by + 0.25, bz), 0.037, 0.018, segs=16, cap=True)

    # ---------------- Logbook ----------------
    jx, jy, jz = -1.08, 1.76, -0.42
    mj = gb.mesh(m_crest, "logbook")
    mj.add_chamfer_box((jx, jy + 0.009, jz), (0.18, 0.018, 0.125), bevel=0.003, uv_tile=1.0)
    ms = gb.mesh(m_stitch, "logbook_stitch")
    hw, hd = 0.09, 0.0625
    corners = [(jx - hw, jz - hd), (jx + hw, jz - hd), (jx + hw, jz + hd), (jx - hw, jz + hd)]
    for i in range(4):
        p0 = corners[i]
        p1 = corners[(i + 1) % 4]
        ms.add_tube((p0[0], jy + 0.018, p0[1]), (p1[0], jy + 0.018, p1[1]), 0.002, segs=6, cap=True)

    # ---------------- Step stool ----------------
    sx, sy, sz = -0.78, 1.32, -1.18
    mst = gb.mesh(m_teak, "stool_frame")
    for lx in (-0.17, 0.17):
        for lz in (-0.12, 0.12):
            mst.add_chamfer_box((sx + lx, sy + 0.06, sz + lz), (0.03, 0.12, 0.03), bevel=0.003, uv_tile=1.0)
    mst.add_chamfer_box((sx, sy + 0.13, sz), (0.38, 0.02, 0.28), bevel=0.003, uv_tile=1.0)
    msp = gb.mesh(m_leather, "stool_pad")
    msp.add_chamfer_box((sx, sy + 0.15, sz), (0.36, 0.02, 0.26), bevel=0.005, uv_tile=1.0)

    # ---------------- Anchors ----------------
    gb.add_anchor("dog_mat", (-1.05, 1.355, -3.85))
    gb.add_anchor("prop_cleat", (1.52, 1.26, -8.55))
    gb.add_anchor("prop_bar", (0.0, 2.38, 1.22))
    gb.add_anchor("prop_journal", (-1.08, 1.76, -0.42))

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                       "assets", "models", "yacht_furniture_props.glb")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    gb.export(out)
    return out


if __name__ == "__main__":
    build()
