import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yacht_kit.yacht_prim_lib import YachtGLBBuilder
from yacht_kit.tex_helpers import load_bundle


def build():
    gb = YachtGLBBuilder("yacht_berth")

    teak_b = load_bundle("teak_deck")
    pvd_b = load_bundle("pvd_brushed")

    teak = gb.add_pbr_material(
        "teak",
        base_bytes=teak_b["base_bytes"], base_mime=teak_b["base_mime"],
        orm_bytes=teak_b["orm_bytes"], normal_bytes=teak_b["norm_bytes"],
        roughness=1.0, metalness=0.0, clearcoat=0.07,
    )
    pvd = gb.add_pbr_material(
        "pvd",
        base_bytes=pvd_b["base_bytes"], base_mime=pvd_b["base_mime"],
        orm_bytes=pvd_b["orm_bytes"], normal_bytes=pvd_b["norm_bytes"],
        roughness=1.0, metalness=1.0,
    )
    float_dark = gb.add_pbr_material(
        "float_dark", base_factor=(0.11, 0.14, 0.17, 1.0),
        roughness=0.72, metalness=0.1,
    )
    fender_rubber = gb.add_pbr_material(
        "fender_rubber", base_factor=(0.12, 0.14, 0.17, 1.0),
        roughness=0.58,
    )

    # --- Teak walkway deck ---
    m = gb.mesh(teak, "walkway_deck")
    m.add_box(
        center=(-4.175, 0.68, 0.0),
        size=(2.61, 0.08, 24.0),
        uv_tile=(2.61 / 0.64, 24.0 / 2.56),
    )

    # --- PVD edge fascia strips ---
    m = gb.mesh(pvd, "edge_fascia")
    m.add_box(center=(-5.49, 0.675, 0.0), size=(0.02, 0.11, 24.0), uv_tile=(1.0, 1.0))
    m.add_box(center=(-2.86, 0.675, 0.0), size=(0.02, 0.11, 24.0), uv_tile=(1.0, 1.0))

    # --- Dark pontoon hulls + cross beams ---
    m = gb.mesh(float_dark, "pontoons")
    m.add_box(center=(-4.175, -0.14, 0.0), size=(2.49, 1.56, 24.0), uv_tile=(1.0, 1.0))
    for z in [-10.0, -6.0, -2.0, 2.0, 6.0, 10.0]:
        m.add_box(center=(-4.175, 0.30, z), size=(2.49, 0.20, 0.30), uv_tile=(1.0, 1.0))

    # --- Piling posts ---
    m = gb.mesh(pvd, "pilings")
    post_z = [-11.2, -7.0, -2.2, 2.2, 7.0, 11.2]
    for x in (-5.38, -2.98):
        for z in post_z:
            m.add_tube((x, -0.95, z), (x, 1.26, z), 0.12, segs=20, cap=True)
            m.add_chamfer_box((x, 1.26, z), (0.28, 0.04, 0.28), bevel=0.008)

    # --- Twin-post mooring cleats ---
    m = gb.mesh(pvd, "cleats")
    for z in [-9.5, -3.6, 3.2, 9.2]:
        for dz in (-0.10, 0.10):
            m.add_tube((-2.98, 0.72, z + dz), (-2.98, 0.88, z + dz), 0.035, segs=12, cap=True)
        m.add_box(center=(-2.98, 0.88, z), size=(0.10, 0.04, 0.28), uv_tile=(1.0, 1.0))

    # --- Dock fenders ---
    m = gb.mesh(fender_rubber, "fenders")
    for z in [-8.4, -5.9, -3.4, 0.5, 4.4, 8.2]:
        m.add_tube((-2.92, 0.12, z), (-2.92, 0.64, z), 0.11, segs=16, cap=True)

    # --- Anchors ---
    gb.add_anchor("dock_spawn", (-4.20, 0.72, -10.60))
    gb.add_anchor("gangway_dock", (-2.85, 0.72, -5.20))

    out = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "assets", "models", "yacht_berth.glb",
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)
    rep = gb.export(out)
    print("Exported:", out)
    print("Report:", rep)


if __name__ == "__main__":
    build()
