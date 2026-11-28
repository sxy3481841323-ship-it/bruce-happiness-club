"""Bespoke yacht furniture & props: aft cockpit lounge, sunbeds, daybed, barware, journal."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yacht_kit.yacht_prim_lib import YachtGLBBuilder
from yacht_kit.tex_helpers import load_bundle


def build():
    gb = YachtGLBBuilder("yacht_furniture_props")

    def mat(name, key, rough=0.6, metal=0.0, cc=0.0, ccr=0.0, tint=(1, 1, 1, 1)):
        b = load_bundle(key)
        return gb.add_pbr_material(
            name, base_bytes=b["base_bytes"], base_mime=b["base_mime"],
            orm_bytes=b["orm_bytes"], normal_bytes=b["norm_bytes"],
            base_factor=tint, roughness=rough, metalness=metal,
            clearcoat=cc, clearcoat_roughness=ccr)

    m_teak = mat("teak", "teak_frame", rough=0.45, cc=0.4, ccr=0.25)
    m_linen = mat("linen", "outdoor_linen", rough=0.85)
    m_leather = mat("leather", "saddle_leather", rough=0.5, cc=0.3, ccr=0.4)
    m_piping = mat("piping", "saddle_leather_crest", rough=0.5, cc=0.3, ccr=0.4)
    m_pvd = mat("pvd", "pvd_brushed", rough=0.28, metal=1.0)
    m_bronze = mat("bronze", "bronze_brushed", rough=0.35, metal=1.0)
    m_glass = mat("glass", "pvd_brushed", rough=0.05, metal=0.0, cc=1.0, ccr=0.05,
                  tint=(0.85, 0.92, 0.95, 0.55))
    m_rug = mat("rug", "woven_rug", rough=0.95)
    m_marq = mat("marq", "marquetry", rough=0.4, cc=0.5, ccr=0.2)
    m_stitch = mat("stitch", "stitch_strip", rough=0.7)
    m_trav = mat("trav", "filled_travertine", rough=0.55)

    teak = gb.mesh(m_teak, "teak_parts")
    linen = gb.mesh(m_linen, "linen_parts")
    leather = gb.mesh(m_leather, "leather_parts")
    piping = gb.mesh(m_piping, "piping_parts")
    pvd = gb.mesh(m_pvd, "pvd_parts")
    bronze = gb.mesh(m_bronze, "bronze_parts")
    glass = gb.mesh(m_glass, "glass_parts")
    rug = gb.mesh(m_rug, "rug_parts")
    marq = gb.mesh(m_marq, "marq_parts")
    stitch = gb.mesh(m_stitch, "stitch_parts")
    trav = gb.mesh(m_trav, "trav_parts")

    # 1. L-lounge banquette: teak base (aft + starboard arm)
    teak.add_chamfer_box((0.765, 1.35, -8.10), (2.30, 0.18, 0.50), bevel=0.02)
    teak.add_chamfer_box((1.78, 1.35, -7.10), (0.40, 0.18, 2.00), bevel=0.02)
    linen.add_chamfer_box((0.765, 1.58, -8.10), (2.24, 0.28, 0.46), bevel=0.03)
    linen.add_chamfer_box((1.78, 1.58, -7.10), (0.36, 0.28, 1.96), bevel=0.03)
    piping.add_box((0.765, 1.72, -7.88), (2.24, 0.02, 0.02))
    piping.add_box((1.78, 1.72, -6.14), (0.36, 0.02, 0.02))
    linen.add_chamfer_box((0.765, 1.94, -8.32), (2.24, 0.42, 0.14), bevel=0.03)
    linen.add_chamfer_box((1.96, 1.94, -7.10), (0.14, 0.42, 1.96), bevel=0.03)
    for px, pz in [(0.05, -8.05), (0.75, -8.05), (1.45, -8.05), (1.78, -6.55)]:
        linen.add_chamfer_box((px, 1.86, pz), (0.34, 0.30, 0.12), bevel=0.04, rot_y=0.15)
        piping.add_box((px, 1.86, pz + 0.07), (0.30, 0.02, 0.02))

    # 2. Cocktail table
    pvd.add_tube((0.55, 1.30, -6.95), (0.55, 1.86, -6.95), 0.05, 0.03, segs=16)
    teak.add_chamfer_box((0.55, 1.88, -6.95), (0.96, 0.04, 0.68), bevel=0.02)
    pvd.add_box((0.55, 1.905, -6.95), (0.90, 0.005, 0.62))
    marq.add_box((0.55, 1.908, -6.95), (0.86, 0.004, 0.58))
    pvd.add_tube((0.35, 1.90, -6.95), (0.35, 2.10, -6.95), 0.09, 0.10, segs=20)
    glass.add_tube((0.55, 1.90, -6.95), (0.55, 2.16, -6.95), 0.035, 0.02, segs=12)
    for fx in (0.72, 0.80):
        glass.add_tube((fx, 1.90, -6.95), (fx, 2.02, -6.95), 0.018, 0.028, segs=10)
    leather.add_chamfer_box((0.55, 1.905, -6.55), (0.40, 0.02, 0.20), bevel=0.01)
    stitch.add_box((0.55, 1.917, -6.55), (0.36, 0.002, 0.16))

    # 3. Sunbeds
    for cx in (0.45, 1.45):
        teak.add_chamfer_box((cx, 1.37, -4.45), (0.80, 0.18, 1.90), bevel=0.02)
        linen.add_chamfer_box((cx, 1.52, -4.45), (0.76, 0.12, 1.86), bevel=0.03)
        linen.add_chamfer_box((cx, 1.90, -5.30), (0.76, 0.60, 0.14), bevel=0.03)
        leather.add_tube((cx - 0.36, 1.60, -3.75), (cx + 0.36, 1.60, -3.75),
                         0.06, 0.06, segs=14)
    pvd.add_tube((0.95, 1.30, -4.45), (0.95, 1.60, -4.45), 0.03, 0.03, segs=12)
    teak.add_chamfer_box((0.95, 1.62, -4.45), (0.34, 0.04, 0.34), bevel=0.015)

    # 4. Bruce's oval daybed (strictly within X >= -1.49 inside deck_aabb!)
    teak.add_prism([(-1.45, -4.16), (-0.59, -4.16), (-0.59, -3.60), (-1.45, -3.60)],
                   1.32, 1.46, uv_tile=1.0)
    leather.add_prism([(-1.42, -4.13), (-0.62, -4.13), (-0.62, -3.63), (-1.42, -3.63)],
                      1.34, 1.50, uv_tile=1.0)
    linen.add_chamfer_box((-1.02, 1.38, -3.88), (0.76, 0.08, 0.44), bevel=0.03)
    pvd.add_box((-1.02, 1.47, -3.62), (0.14, 0.02, 0.01))
    rug.add_box((-1.00, 1.325, -3.88), (0.94, 0.005, 0.70))

    # 5. Deck cleat + coiled rope
    bronze.add_box((1.52, 1.30, -8.55), (0.22, 0.06, 0.06))
    bronze.add_tube((1.44, 1.30, -8.55), (1.44, 1.36, -8.55), 0.03, 0.03, segs=10)
    bronze.add_tube((1.60, 1.30, -8.55), (1.60, 1.36, -8.55), 0.03, 0.03, segs=10)
    for i in range(3):
        r = 0.10 - i * 0.025
        bronze.add_tube((1.52 - r, 1.28 + i * 0.02, -8.55),
                        (1.52 + r, 1.28 + i * 0.02, -8.55), 0.012, 0.012, segs=8)

    # Step stool (bottom >= 1.325 strictly inside cabin_aabb Y >= 1.32)
    teak.add_chamfer_box((-0.78, 1.40, -1.18), (0.40, 0.08, 0.30), bevel=0.015)
    teak.add_chamfer_box((-0.78, 1.348, -1.18), (0.36, 0.04, 0.26), bevel=0.01)

    # Salon barware
    pvd.add_tube((0.0, 2.38, 1.22), (0.0, 2.52, 1.22), 0.05, 0.06, segs=16)
    glass.add_tube((-0.10, 2.38, 1.22), (-0.10, 2.50, 1.22), 0.025, 0.03, segs=10)
    glass.add_tube((0.10, 2.38, 1.22), (0.10, 2.50, 1.22), 0.025, 0.03, segs=10)
    trav.add_box((0.0, 2.385, 1.22), (0.30, 0.01, 0.20))

    # Stitched leather logbook
    leather.add_chamfer_box((-1.08, 1.76, -0.42), (0.24, 0.04, 0.32), bevel=0.008)
    stitch.add_box((-1.08, 1.782, -0.42), (0.20, 0.002, 0.28))
    marq.add_box((-1.08, 1.784, -0.42), (0.16, 0.002, 0.24))

    gb.add_anchor("dog_mat", (-1.02, 1.41, -3.88))
    gb.add_anchor("prop_cleat", (1.52, 1.26, -8.55))
    gb.add_anchor("prop_bar", (0.0, 2.38, 1.22))
    gb.add_anchor("prop_journal", (-1.08, 1.76, -0.42))

    gb.export("assets/models/yacht_furniture_props.glb")


if __name__ == "__main__":
    build()
