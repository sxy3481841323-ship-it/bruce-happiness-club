import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from yacht_kit.yacht_prim_lib import YachtGLBBuilder
from yacht_kit.tex_helpers import load_bundle


def main():
    gb = YachtGLBBuilder("yacht_deck_salon")

    hull = load_bundle("hull_satin")
    marq = load_bundle("marquetry")
    leat = load_bundle("saddle_leather")
    stch = load_bundle("stitch_strip")
    rugb = load_bundle("woven_rug")
    trav = load_bundle("filled_travertine")
    pvdb = load_bundle("pvd_brushed")

    m_hull = gb.add_pbr_material("hull_dark", base_bytes=hull["base_bytes"], base_mime=hull["base_mime"],
                                 orm_bytes=hull["orm_bytes"], normal_bytes=hull["norm_bytes"], clearcoat=0.38)
    m_marq = gb.add_pbr_material("marquetry", base_bytes=marq["base_bytes"], base_mime=marq["base_mime"],
                                 orm_bytes=marq["orm_bytes"], normal_bytes=marq["norm_bytes"],
                                 clearcoat=0.36, clearcoat_roughness=0.32)
    m_leat = gb.add_pbr_material("leather", base_bytes=leat["base_bytes"], base_mime=leat["base_mime"],
                                 orm_bytes=leat["orm_bytes"], normal_bytes=leat["norm_bytes"], clearcoat=0.11)
    m_stch = gb.add_pbr_material("stitch", base_bytes=stch["base_bytes"], base_mime=stch["base_mime"],
                                 orm_bytes=stch["orm_bytes"], normal_bytes=stch["norm_bytes"], clearcoat=0.05)
    m_rug = gb.add_pbr_material("rug", base_bytes=rugb["base_bytes"], base_mime=rugb["base_mime"],
                                orm_bytes=rugb["orm_bytes"], normal_bytes=rugb["norm_bytes"], roughness=1.0)
    m_trav = gb.add_pbr_material("travertine", base_bytes=trav["base_bytes"], base_mime=trav["base_mime"],
                                 orm_bytes=trav["orm_bytes"], normal_bytes=trav["norm_bytes"], clearcoat=0.06)
    m_pvd = gb.add_pbr_material("pvd", base_bytes=pvdb["base_bytes"], base_mime=pvdb["base_mime"],
                                orm_bytes=pvdb["orm_bytes"], normal_bytes=pvdb["norm_bytes"], metalness=1.0)
    m_glass = gb.add_pbr_material("curved_glass", base_factor=(0.94, 0.97, 0.99, 1.0), roughness=0.07,
                                  metalness=0.0, transmission=0.94, ior=1.46, double_sided=True)
    m_cove = gb.add_pbr_material("warm_cove", base_factor=(1.0, 0.88, 0.72, 1.0), roughness=0.3,
                                 emissive=(1.0, 0.72, 0.38))
    m_crys = gb.add_pbr_material("sconce_crystal", base_factor=(1.0, 0.92, 0.80, 1.0), roughness=0.15,
                                 emissive=(1.0, 0.78, 0.48), transmission=0.45, ior=1.52)

    # Floor + rug
    m = gb.mesh(m_hull, "floor")
    m.add_box((0.0, 1.31, -0.50), (3.04, 0.02, 5.36))
    m = gb.mesh(m_rug, "rug")
    m.add_box((0.0, 1.324, -0.80), (1.84, 0.008, 3.30))

    # Cabin roof
    m = gb.mesh(m_hull, "roof")
    m.add_box((0.0, 3.48, -0.50), (3.06, 0.08, 5.40))
    # Lintel above doorway
    m.add_box((0.0, 3.39, -3.16), (3.06, 0.10, 0.08))
    # Cove strip + pvd thread on lintel
    m = gb.mesh(m_cove, "lintel_cove")
    m.add_box((0.0, 3.345, -3.12), (1.60, 0.008, 0.02))
    m = gb.mesh(m_pvd, "lintel_thread")
    m.add_box((0.0, 3.335, -3.11), (1.62, 0.004, 0.01))

    # Side walls (hull frame) with glass windows
    m = gb.mesh(m_hull, "side_walls")
    for sx in (-1.0, 1.0):
        # lower sill
        m.add_box((sx * 1.515, 1.55, -0.50), (0.03, 0.46, 5.36))
        # upper header
        m.add_box((sx * 1.515, 3.30, -0.50), (0.03, 0.28, 5.36))
        # vertical mullions
        for z in (-2.9, -1.4, 0.1, 1.6):
            m.add_box((sx * 1.515, 2.42, z), (0.03, 1.30, 0.05))
    m = gb.mesh(m_glass, "side_glass")
    for sx in (-1.0, 1.0):
        m.add_box((sx * 1.515, 2.42, -0.50), (0.008, 1.30, 5.30))

    # Aft curved panoramic glass (R~2.40 centered near (0,y,-0.78))
    m = gb.mesh(m_glass, "aft_glass")
    import math
    cx, cz, R = 0.0, -0.78, 2.40
    for sx in (-1.0, 1.0):
        # arc from |X|=0.80 to 1.52
        n = 14
        for i in range(n):
            a0 = math.asin(0.80 / R) if sx > 0 else math.pi - math.asin(0.80 / R)
            a1 = math.asin(1.52 / R) if sx > 0 else math.pi - math.asin(1.52 / R)
            t0 = a0 + (a1 - a0) * i / n
            t1 = a0 + (a1 - a0) * (i + 1) / n
            x0, z0 = cx + R * math.sin(t0), cz - R * math.cos(t0)
            x1, z1 = cx + R * math.sin(t1), cz - R * math.cos(t1)
            m.add_quad((x0, 1.32, z0), (x1, 1.32, z1), (x1, 3.34, z1), (x0, 3.34, z0))

    # Retracted sliding door leaves tucked behind aft glass at |X|=0.82..1.48
    m = gb.mesh(m_glass, "sliding_doors")
    for sx in (-1.0, 1.0):
        m.add_box((sx * 1.15, 2.33, -2.95), (0.66, 2.02, 0.02))

    # Forward bulkhead with 4 marquetry panels
    m = gb.mesh(m_hull, "fwd_bulkhead")
    m.add_box((0.0, 2.40, 2.15), (3.04, 2.20, 0.06))
    m = gb.mesh(m_marq, "marquetry_panels")
    for i in range(4):
        x = -0.585 + i * 0.39
        m.add_box((x, 2.475, 2.11), (0.39, 1.05, 0.02))
    m = gb.mesh(m_pvd, "panel_thread")
    for i in range(4):
        x = -0.585 + i * 0.39
        m.add_box((x, 3.005, 2.10), (0.40, 0.004, 0.01))
        m.add_box((x, 1.945, 2.10), (0.40, 0.004, 0.01))

    # Banquettes (0.43 m high seat cushion + outboard beveled backrest so Bruce curls cleanly at Y=1.75!)
    m = gb.mesh(m_leat, "banquettes")
    for sx in (-1.0, 1.0):
        # Lower seat base & cushion |X|=0.90..1.47, Y=1.32..1.75
        m.add_chamfer_box((sx * 1.185, 1.535, -0.85), (0.57, 0.43, 2.80), bevel=0.025, uv_tile=0.8)
        # Outboard backrest |X|=1.30..1.47, Y=1.75..2.22 leaving 0.40 m seat ledge!
        m.add_chamfer_box((sx * 1.385, 1.985, -0.85), (0.17, 0.47, 2.80), bevel=0.025, uv_tile=0.8)
        # Curved forward/aft armrests
        for ez in (-2.18, 0.48):
            m.add_chamfer_box((sx * 1.185, 1.84, ez), (0.55, 0.18, 0.14), bevel=0.02, uv_tile=0.6)
    m = gb.mesh(m_stch, "banquette_stitch")
    for sx in (-1.0, 1.0):
        m.add_box((sx * 0.91, 1.745, -0.85), (0.014, 0.012, 2.78))
        m.add_box((sx * 1.385, 2.22, -0.85), (0.14, 0.012, 2.78))
    m = gb.mesh(m_pvd, "banquette_piping")
    for sx in (-1.0, 1.0):
        m.add_box((sx * 1.30, 2.225, -0.85), (0.004, 0.004, 2.80))
        m.add_box((sx * 0.90, 1.34, -0.85), (0.004, 0.004, 2.80))

    # Travertine bar with 35 mm recessed marquetry cabinet doors
    m = gb.mesh(m_trav, "bar_slab")
    m.add_chamfer_box((0.0, 2.36, 1.22), (1.78, 0.04, 0.62), bevel=0.004, uv_tile=1.0)
    m = gb.mesh(m_hull, "bar_recess_core")
    m.add_box((0.0, 1.83, 1.24), (1.76, 1.01, 0.56))
    m = gb.mesh(m_marq, "bar_base")
    for sx in (-1.0, 1.0):
        # Side stiles & center divider flush at Z=0.91
        m.add_box((sx * 0.85, 1.83, 1.22), (0.08, 1.02, 0.62))
        # Cabinet door leaf recessed 35 mm inward (front at Z=0.945)
        m.add_chamfer_box((sx * 0.41, 1.83, 1.245), (0.76, 0.96, 0.56), bevel=0.003)
    m = gb.mesh(m_pvd, "bar_pulls")
    m.add_box((0.0, 2.335, 0.908), (1.78, 0.004, 0.006))
    for x in (-0.38, 0.38):
        m.add_box((x, 1.96, 0.942), (0.16, 0.014, 0.016))

    # Sconces
    m = gb.mesh(m_pvd, "sconce_backplate")
    for sx in (-1.0, 1.0):
        m.add_box((sx * 1.40, 2.83, 0.15), (0.02, 0.32, 0.11))
    m = gb.mesh(m_crys, "sconce_crystal")
    for sx in (-1.0, 1.0):
        for i in range(3):
            m.add_box((sx * 1.38, 2.83, 0.15 + (i - 1) * 0.03), (0.04, 0.32, 0.02))

    gb.add_anchor("door_left", (-0.80, 1.32, -3.12))
    gb.add_anchor("door_right", (0.80, 1.32, -3.12))
    gb.add_anchor("bar_top", (0.0, 2.38, 1.22))
    gb.add_anchor("journal_anchor", (-1.08, 1.76, -0.42))
    gb.add_anchor("dog_nap", (-1.06, 1.75, -1.18))

    out = ROOT / "assets" / "models" / "yacht_deck_salon.glb"
    out.parent.mkdir(parents=True, exist_ok=True)
    gb.export(str(out))


if __name__ == "__main__":
    main()
