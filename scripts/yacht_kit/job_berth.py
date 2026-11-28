import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from yacht_kit.yacht_prim_lib import YachtGLBBuilder
from yacht_kit.tex_helpers import load_bundle

OUT = Path(__file__).resolve().parents[2] / "assets" / "models" / "yacht_berth.glb"
gb = YachtGLBBuilder("yacht_berth")

teak_b = load_bundle("teak_deck")
trav_b = load_bundle("filled_travertine")
tf_b = load_bundle("teak_frame")
pvd_b = load_bundle("pvd_brushed")
brz_b = load_bundle("bronze_brushed")

i_teak = gb.add_pbr_material("teak", base_bytes=teak_b["base_bytes"], base_mime=teak_b["base_mime"],
                             orm_bytes=teak_b["orm_bytes"], normal_bytes=teak_b["norm_bytes"],
                             roughness=1.0, metalness=0.0, clearcoat=0.07)
i_trav = gb.add_pbr_material("travertine", base_bytes=trav_b["base_bytes"], base_mime=trav_b["base_mime"],
                             orm_bytes=trav_b["orm_bytes"], normal_bytes=trav_b["norm_bytes"],
                             roughness=1.0, metalness=0.0, clearcoat=0.05)
i_tf = gb.add_pbr_material("teak_frame", base_bytes=tf_b["base_bytes"], base_mime=tf_b["base_mime"],
                           orm_bytes=tf_b["orm_bytes"], normal_bytes=tf_b["norm_bytes"],
                           roughness=1.0, metalness=0.0, clearcoat=0.14)
i_pvd = gb.add_pbr_material("pvd", base_bytes=pvd_b["base_bytes"], base_mime=pvd_b["base_mime"],
                            orm_bytes=pvd_b["orm_bytes"], normal_bytes=pvd_b["norm_bytes"],
                            roughness=1.0, metalness=1.0)
i_brz = gb.add_pbr_material("bronze", base_bytes=brz_b["base_bytes"], base_mime=brz_b["base_mime"],
                            orm_bytes=brz_b["orm_bytes"], normal_bytes=brz_b["norm_bytes"],
                            roughness=1.0, metalness=1.0)
i_float = gb.add_pbr_material("float", base_factor=(0.09, 0.10, 0.11, 1.0),
                              roughness=0.85, metalness=0.0)
i_amber = gb.add_pbr_material("amber", base_factor=(1.0, 0.78, 0.44, 1.0),
                              roughness=0.35, metalness=0.0,
                              emissive=(1.0, 0.78, 0.44))
i_fender = gb.add_pbr_material("fender", base_factor=(0.13, 0.13, 0.14, 1.0),
                               roughness=0.9, metalness=0.0)

m_teak = gb.mesh(i_teak, "teak_deck")
m_trav = gb.mesh(i_trav, "travertine")
m_tf = gb.mesh(i_tf, "teak_frame")
m_pvd = gb.mesh(i_pvd, "pvd")
m_brz = gb.mesh(i_brz, "bronze")
m_float = gb.mesh(i_float, "floats")
m_amber = gb.mesh(i_amber, "amber")
m_fender = gb.mesh(i_fender, "fenders")

# 1. Teak deck
m_teak.add_box((-4.17, 0.68, 0.0), (1.98, 0.08, 23.92), uv_tile=(0.64, 2.56))

# 2. Travertine coping curbs + PVD fascia
for x in (-5.34, -3.00):
    m_trav.add_chamfer_box((x, 0.6825, 0.0), (0.34, 0.085, 23.92), bevel=0.006, uv_tile=1.0)
    m_pvd.add_box((x, 0.6525, 0.0), (0.36, 0.145, 23.92))

# 3. Floats & outboard pilings
m_float.add_box((-4.17, -0.15, 0.0), (2.30, 1.54, 23.60))
for z in (-11.0, -5.5, 0.0, 5.5, 11.0):
    m_float.add_box((-4.17, -0.15, z), (2.34, 1.50, 0.30))
for z in (-11.4, -5.7, 0.0, 5.7, 11.4):
    m_float.add_tube((-5.42, -0.94, z), (-5.42, 0.72, z), 0.075, segs=12)
    m_pvd.add_tube((-5.42, 0.72, z), (-5.42, 0.77, z), 0.085, segs=12)

# 4. Railing: stanchions, cables, handrail
zs = [-11.4 + i * 2.28 for i in range(11)]
for z in zs:
    m_brz.add_tube((-5.34, 0.72, z), (-5.34, 1.25, z), 0.018, 0.013, segs=10)
for y in (0.88, 1.02, 1.16):
    m_pvd.add_tube((-5.34, y, -11.6), (-5.34, y, 11.6), 0.005, segs=8)
m_tf.add_chamfer_box((-5.34, 1.265, 0.0), (0.065, 0.036, 23.2), bevel=0.004, uv_tile=1.0)

# 5. Amber bollards
for z in (-9.2, -5.4, -1.8, 1.8, 5.4, 9.2):
    m_brz.add_tube((-5.34, 0.72, z), (-5.34, 1.00, z), 0.055, 0.045, segs=12)
    m_amber.add_tube((-5.34, 1.00, z), (-5.34, 1.08, z), 0.048, 0.040, segs=12)

# 6. Cleats & fenders
for z in (-9.5, -3.6, 3.2, 9.2):
    for dz in (-0.09, 0.09):
        m_pvd.add_tube((-2.96, 0.72, z + dz), (-2.96, 0.86, z + dz), 0.014, segs=8)
    m_pvd.add_tube((-2.96, 0.86, z - 0.09), (-2.96, 0.86, z + 0.09), 0.014, segs=8)
for z in (-10.5, -7.0, -3.5, 0.0, 3.5, 7.0, 10.5):
    m_fender.add_tube((-2.90, 0.14, z), (-2.90, 0.64, z), 0.075, segs=12)

gb.add_anchor("dock_spawn", (-4.20, 0.72, -10.60))
gb.add_anchor("gangway_dock", (-2.85, 0.72, -5.20))
gb.export(str(OUT))
print("wrote", OUT)
