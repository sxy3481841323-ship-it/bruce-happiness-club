from pathlib import Path
import math
import sys

_here = Path(__file__).resolve()
for _p in (_here.parent, _here.parent.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from yacht_kit.yacht_prim_lib import YachtGLBBuilder
from yacht_kit.tex_helpers import load_bundle

OUT = Path(__file__).resolve().parents[2] / "assets" / "models" / "yacht_club_lounge.glb"

gb = YachtGLBBuilder("yacht_club_lounge")

def mat(name, key, rough=0.85, metal=0.0, factor=(1,1,1,1), emis=(0,0,0), cc=0.0, ccr=0.0, ior=1.5, ds=False):
    b = load_bundle(key)
    return gb.add_pbr_material(name, base_bytes=b["base_bytes"], base_mime=b["base_mime"],
        orm_bytes=b["orm_bytes"], normal_bytes=b["norm_bytes"], base_factor=factor,
        roughness=rough, metalness=metal, emissive=emis, clearcoat=cc, clearcoat_roughness=ccr,
        ior=ior, double_sided=ds)

i_trav = mat("travertine", "filled_travertine", rough=0.75)
i_teak = mat("teak", "teak_deck", rough=0.55, cc=0.3, ccr=0.4)
i_tf   = mat("teak_frame", "teak_frame", rough=0.5, cc=0.3, ccr=0.4)
i_brz  = mat("bronze", "bronze_brushed", rough=0.35, metal=1.0)
i_pvd  = mat("pvd", "pvd_brushed", rough=0.25, metal=1.0)
i_marq = mat("marquetry", "marquetry", rough=0.4, cc=0.4, ccr=0.3)
i_linen= mat("linen", "outdoor_linen", rough=0.95)
i_leather = mat("leather", "saddle_leather", rough=0.6)
i_rug  = mat("rug", "woven_rug", rough=1.0)
i_hull = mat("hull", "hull_satin", rough=0.3, cc=0.6, ccr=0.2)
i_glass= mat("glass", "hull_satin", rough=0.05, metal=0.0, factor=(0.85,0.92,0.95,0.35), ds=True)
i_amber= mat("amber", "pvd_brushed", rough=0.4, metal=0.0, factor=(1.0,0.72,0.35,1.0), emis=(1.0,0.55,0.2))
i_olive= mat("olive", "outdoor_linen", rough=0.9, factor=(0.30,0.39,0.28,1.0))
i_bark = mat("bark", "saddle_leather", rough=0.9, factor=(0.35,0.25,0.18,1.0))

m_trav = gb.mesh(i_trav, "travertine")
m_teak = gb.mesh(i_teak, "teak")
m_tf   = gb.mesh(i_tf, "teak_frame")
m_brz  = gb.mesh(i_brz, "bronze")
m_pvd  = gb.mesh(i_pvd, "pvd")
m_marq = gb.mesh(i_marq, "marquetry")
m_linen= gb.mesh(i_linen, "linen")
m_leather = gb.mesh(i_leather, "leather")
m_rug  = gb.mesh(i_rug, "rug")
m_hull = gb.mesh(i_hull, "hull")
m_glass= gb.mesh(i_glass, "glass")
m_amber= gb.mesh(i_amber, "amber")
m_olive= gb.mesh(i_olive, "olive")
m_bark = gb.mesh(i_bark, "bark")

# --- Seawall & promenade ---
m_trav.add_box((-16.85, -0.065, -1.0), (15.3, 2.37, 30.0), uv_tile=(4,8))
m_trav.add_box((-9.2, 1.06, -1.0), (0.3, 0.12, 30.0), uv_tile=(1,8))
for i in range(4):
    m_trav.add_box((-9.6 - i*0.35, 0.9 - i*0.28, 6.75), (0.35, 0.28, 3.5), uv_tile=(1,2))
m_amber.add_box((-9.06, 0.15, -1.0), (0.04, 0.05, 28.0), uv_tile=(1,20))

# --- Promenade glass railing (skip bridge gap) ---
for z0, z1 in [(-16.0, -11.4), (-7.8, 14.0)]:
    zc = (z0+z1)/2; zl = z1-z0
    m_glass.add_box((-9.2, 1.57, zc), (0.03, 0.9, zl), uv_tile=(1, zl/2))
    m_tf.add_box((-9.2, 2.02, zc), (0.08, 0.06, zl), uv_tile=(1, zl/2))
    m_pvd.add_box((-9.2, 2.08, zc), (0.05, 0.04, zl), uv_tile=(1, zl/2))

# --- Bridge ---
bx0, bx1 = -9.15, -5.45
bz0, bz1 = -11.3, -7.9
zc = (bz0+bz1)/2
N = 8
for i in range(N):
    t0 = i/N; t1 = (i+1)/N
    x0 = bx0 + (bx1-bx0)*t0; x1 = bx0 + (bx1-bx0)*t1
    y0 = 1.12 + (0.72-1.12)*t0 + 0.06*math.sin(math.pi*t0)
    y1 = 1.12 + (0.72-1.12)*t1 + 0.06*math.sin(math.pi*t1)
    m_teak.add_quad((x0, y0, bz0), (x1, y1, bz0), (x1, y1, bz1), (x0, y0, bz1))
    m_brz.add_box(((x0+x1)/2, (y0+y1)/2 - 0.08, zc), (abs(x1-x0)+0.02, 0.12, 3.0))
for zr in (bz0+0.1, bz1-0.1):
    for i in range(N):
        t0 = i/N; t1 = (i+1)/N
        x0 = bx0 + (bx1-bx0)*t0; x1 = bx0 + (bx1-bx0)*t1
        y0 = 1.12 + (0.72-1.12)*t0 + 0.06*math.sin(math.pi*t0)
        y1 = 1.12 + (0.72-1.12)*t1 + 0.06*math.sin(math.pi*t1)
        m_glass.add_quad((x0, y0+0.05, zr), (x1, y1+0.05, zr), (x1, y1+0.95, zr), (x0, y0+0.95, zr))
        m_tf.add_box(((x0+x1)/2, (y0+y1)/2+0.98, zr), (abs(x1-x0)+0.02, 0.06, 0.08))
        m_pvd.add_box(((x0+x1)/2, (y0+y1)/2+1.04, zr), (abs(x1-x0)+0.02, 0.04, 0.05))

# --- Pavilion terrace plinth ---
m_teak.add_box((-16.15, 1.15, -3.0), (10.7, 0.06, 18.0), uv_tile=(6,10))
m_rug.add_box((-13.6, 1.19, -5.2), (3.2, 0.02, 3.2), uv_tile=(2,2))
m_rug.add_box((-13.6, 1.19, 1.8), (3.2, 0.02, 3.2), uv_tile=(2,2))

# --- Colonnade pillars ---
for px in (-21.0, -10.8):
    for pz in (-11.5, -6.0, -0.5, 5.5):
        m_trav.add_box((px, 2.79, pz), (0.35, 3.22, 0.35), uv_tile=(1,4))

# --- Roof ---
m_hull.add_box((-16.15, 4.54, -3.0), (11.2, 0.28, 18.6), uv_tile=(6,10))
for i in range(14):
    z = -11.8 + i*1.35
    m_tf.add_box((-16.15, 4.72, z), (11.0, 0.06, 0.35), uv_tile=(6,1))
for pz in (-9.0, -3.0, 3.0):
    m_amber.add_box((-16.15, 4.38, pz), (10.0, 0.04, 0.15), uv_tile=(8,1))

# --- Aperitivo bar ---
m_trav.add_box((-18.8, 1.70, -2.0), (1.0, 1.04, 4.0), uv_tile=(2,3))
m_marq.add_box((-18.8, 1.70, -2.0), (1.02, 0.9, 4.02), uv_tile=(2,3))
m_trav.add_box((-18.8, 2.24, -2.0), (1.15, 0.06, 4.15), uv_tile=(2,3))
m_glass.add_box((-19.4, 2.9, -2.0), (0.05, 1.2, 3.6), uv_tile=(1,3))
m_amber.add_box((-19.42, 2.9, -2.0), (0.02, 1.1, 3.4), uv_tile=(1,3))
for z in (-3.4, -2.3, -1.2, -0.1):
    m_brz.add_tube((-17.3, 1.18, z), (-17.3, 1.85, z), 0.04, 0.04, segs=10)
    m_leather.add_box((-17.3, 1.92, z), (0.42, 0.14, 0.42), uv_tile=(1,1))

# --- Lounge suites ---
def suite(zc):
    m_teak.add_box((-13.6, 1.22, zc), (2.6, 0.08, 2.6), uv_tile=(2,2))
    m_linen.add_box((-13.6, 1.55, zc), (2.4, 0.55, 2.4), uv_tile=(2,2))
    m_linen.add_box((-14.6, 1.95, zc), (0.4, 0.55, 2.4), uv_tile=(1,2))
    m_leather.add_box((-13.4, 1.85, zc-1.0), (0.5, 0.25, 0.5), uv_tile=(1,1))
    m_leather.add_box((-13.4, 1.85, zc+1.0), (0.5, 0.25, 0.5), uv_tile=(1,1))
    m_trav.add_tube((-12.2, 1.18, zc), (-12.2, 1.55, zc), 0.35, 0.35, segs=16)
    m_glass.add_tube((-12.2, 1.58, zc-0.15), (-12.2, 1.72, zc-0.15), 0.05, 0.05, segs=8)
    m_glass.add_tube((-12.2, 1.58, zc+0.15), (-12.2, 1.72, zc+0.15), 0.05, 0.05, segs=8)

suite(-5.2)
suite(1.8)

def _add_ellipsoid(mesh, cx, cy, cz, rx, ry, rz, rings=10, segs=16):
    import numpy as np
    pos = np.zeros((rings + 1, segs + 1, 3), dtype=np.float32)
    uv = np.zeros((rings + 1, segs + 1, 2), dtype=np.float32)
    for i in range(rings + 1):
        v = i / rings
        phi = (v - 0.5) * math.pi
        cp, sp = math.cos(phi), math.sin(phi)
        for j in range(segs + 1):
            u = j / segs
            th = u * 2.0 * math.pi
            pos[i, j] = (cx + rx * cp * math.cos(th), cy + ry * sp, cz + rz * cp * math.sin(th))
            uv[i, j] = (u, v)
    mesh.add_grid(pos, uv, flip=True, smooth_normals=True, seam_u=False)


# --- Olive planters (sculpted rounded organic Mediterranean olive foliage, never cones!) ---
for px, pz in ((-10.9, -11.5), (-10.9, 5.5), (-21.0, -11.5), (-21.0, 5.5)):
    m_trav.add_tube((px, 1.18, pz), (px, 1.72, pz), 0.42, 0.36, segs=16)
    m_bark.add_tube((px, 1.70, pz), (px, 2.25, pz), 0.055, 0.04, segs=10)
    _add_ellipsoid(m_olive, px, 2.55, pz, 0.56, 0.42, 0.56, rings=10, segs=16)
    _add_ellipsoid(m_olive, px + 0.18, 2.75, pz - 0.12, 0.38, 0.30, 0.38, rings=8, segs=12)

# --- Terraced coastal hillside & rounded evergreen pine dunes behind club (zero flat cones!) ---
for i in range(5):
    x = -24.5 - i * 3.5
    y_top = 1.1 + i * 0.65
    m_trav.add_box((x, y_top / 2, -1.0), (3.5, y_top, 42.0), uv_tile=(2, 10))
for cx_h, cz_h, rx_h, ry_h, rz_h in (
    (-30.0, -14.0, 7.5, 4.2, 9.0),
    (-32.5, -2.0, 8.2, 4.8, 10.5),
    (-31.0, 10.5, 7.2, 4.0, 8.5),
    (-38.0, 4.0, 9.0, 5.2, 11.0),
):
    _add_ellipsoid(m_olive, cx_h, 2.8, cz_h, rx_h, ry_h, rz_h, rings=10, segs=18)

gb.add_anchor("bridge_pier", (-5.45, 0.72, -9.6))
gb.add_anchor("promenade", (-9.2, 1.12, 0.0))
gb.add_anchor("bar", (-18.8, 1.18, -2.0))
gb.add_anchor("lounge_a", (-13.6, 1.18, -5.2))
gb.add_anchor("lounge_b", (-13.6, 1.18, 1.8))

OUT.parent.mkdir(parents=True, exist_ok=True)
gb.export(str(OUT))
print(f"Exported {OUT}")
