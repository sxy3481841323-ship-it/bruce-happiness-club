import sys, os, math
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from yacht_kit.yacht_prim_lib import YachtGLBBuilder
from yacht_kit.tex_helpers import load_bundle

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "models", "yacht_hull_rig.glb"))

def clamp(v, a, b): return max(a, min(b, v))

CP = [(-10,1.12),(-8,1.82),(-3,2.40),(2,2.40),(5.8,1.96),(8.5,0.98),(10,0.0)]
def hw(z):
    z = clamp(z, -10.0, 10.0)
    for i in range(len(CP)-1):
        z0,w0 = CP[i]; z1,w1 = CP[i+1]
        if z0 <= z <= z1:
            t = (z-z0)/(z1-z0)
            s = 0.5-0.5*math.cos(math.pi*t)
            return clamp(w0+(w1-w0)*s, 0.0, 2.40)
    return 0.0

def y_deck(z):
    if z <= -8.0: return 1.20
    if z <= 2.2:
        t = (z+8.0)/10.2
        s = 0.5-0.5*math.cos(math.pi*t)
        return 1.20 + 0.10*s
    t = clamp((z-2.2)/7.8, 0, 1)
    s = 0.5-0.5*math.cos(math.pi*t)
    return 1.30 + 0.32*s

def hull_hw(z, y):
    # Rake stem cleanly from (0, 1.62, 10.0) through waterline (0, 0.0, 9.50)
    z_stem = 9.50 + 0.50 * clamp(y / 1.62, -0.35, 1.0)
    if z >= z_stem:
        return 0.0
    w = hw(z)
    if z > 7.5 and w > 0.0:
        w *= clamp((z_stem - z) / max(0.05, 10.0 - z), 0.0, 1.0) ** 0.35
    if y < 0.0:
        f = clamp(1.0 + y/0.58, 0.0, 1.0)
        f = 0.28 + 0.72*math.sqrt(f)
        return w*f
    return w

def build():
    gb = YachtGLBBuilder("yacht_hull_rig")
    hb = load_bundle("hull_satin")
    tb = load_bundle("teak_deck")
    pb = load_bundle("pvd_brushed")
    sb = load_bundle("sail_coated")

    hull_mat = gb.add_pbr_material("hull_mat", base_bytes=hb["base_bytes"], base_mime=hb["base_mime"],
        orm_bytes=hb["orm_bytes"], normal_bytes=hb["norm_bytes"], clearcoat=0.38, clearcoat_roughness=0.27)
    teak = gb.add_pbr_material("teak", base_bytes=tb["base_bytes"], base_mime=tb["base_mime"],
        orm_bytes=tb["orm_bytes"], normal_bytes=tb["norm_bytes"], clearcoat=0.07)
    pvd = gb.add_pbr_material("pvd", base_bytes=pb["base_bytes"], base_mime=pb["base_mime"],
        orm_bytes=pb["orm_bytes"], normal_bytes=pb["norm_bytes"], metalness=1.0, roughness=1.0)
    sail_mat = gb.add_pbr_material("sail_mat", base_bytes=sb["base_bytes"], base_mime=sb["base_mime"],
        orm_bytes=sb["orm_bytes"], normal_bytes=sb["norm_bytes"], clearcoat=0.10, double_sided=True)
    win_glass = gb.add_pbr_material("win_glass", base_factor=(0.04,0.06,0.09,1.0),
        roughness=0.08, metalness=0.15, clearcoat=0.65)

    # ---- Hull shell loft + closed bottom + stern transom + underwater keel down to -1.65 ----
    mh = gb.mesh(hull_mat, "hull")
    NZ = 48; NY = 16
    zs = [-10.0 + 20.0*i/(NZ-1) for i in range(NZ)]
    for side in (1, -1):
        pos = np.zeros((NZ, NY, 3), dtype=np.float64)
        uvg = np.zeros((NZ, NY, 2), dtype=np.float64)
        for i, z in enumerate(zs):
            y_top = y_deck(z)
            ys = [-0.58 + (y_top + 0.58)*j/(NY-1) for j in range(NY)]
            for j, y in enumerate(ys):
                w = hull_hw(z, y)
                pos[i, j] = (side*w, y, z)
                uvg[i, j] = (z / 4.0, j / (NY - 1))
        mh.add_grid(pos, uvg, flip=(side > 0))
    # Close hull bottom & stern transom bulkhead (-10.0) & fin keel down to Y=-1.65
    for i in range(NZ - 1):
        z0, z1 = zs[i], zs[i + 1]
        b0, b1 = hull_hw(z0, -0.58), hull_hw(z1, -0.58)
        mh.add_quad((-b0, -0.58, z0), (b0, -0.58, z0), (b1, -0.58, z1), (-b1, -0.58, z1), (0, 0), (1, 0), (1, 1), (0, 1))
    tw_top = hw(-10.0)
    tw_bot = hull_hw(-10.0, -0.58)
    mh.add_quad((-tw_bot, -0.58, -10.0), (-tw_top, 1.20, -10.0), (tw_top, 1.20, -10.0), (tw_bot, -0.58, -10.0))
    mh.add_chamfer_box((0.0, -1.10, -0.4), (0.14, 1.10, 2.2), bevel=0.03)
    mh.add_chamfer_box((0.0, -1.56, -0.4), (0.28, 0.18, 2.5), bevel=0.04)

    # ---- Main teak deck (+Y upward normals, solid thickness, physical 0.640x2.56m plank UV) ----
    md = gb.mesh(teak, "deck")
    ND = 48
    for i in range(ND - 1):
        z0 = -10.0 + 20.0 * i / (ND - 1); z1 = -10.0 + 20.0 * (i + 1) / (ND - 1)
        w0 = hw(z0); w1 = hw(z1)
        y0 = y_deck(z0); y1 = y_deck(z1)
        # Top teak planks (flip=True gives +Y upward normal!)
        md.add_quad(
            (-w0, y0, z0), (w0, y0, z0), (w1, y1, z1), (-w1, y1, z1),
            uv0=(-w0 / 0.64, z0 / 2.56), uv1=(w0 / 0.64, z0 / 2.56),
            uv2=(w1 / 0.64, z1 / 2.56), uv3=(-w1 / 0.64, z1 / 2.56),
            flip=True,
        )
        # Dark hull deckhead backing 4cm below so there is never a see-through gap
        mh.add_quad((-w0, y0 - 0.04, z0), (w0, y0 - 0.04, z0), (w1, y1 - 0.04, z1), (-w1, y1 - 0.04, z1))

    # ---- Waterline PVD stripe ----
    mp = gb.mesh(pvd, "stripe")
    NS = 60
    for side in (1,-1):
        for i in range(NS-1):
            z0 = -9.7 + (9.52+9.7)*i/(NS-1); z1 = -9.7 + (9.52+9.7)*(i+1)/(NS-1)
            w0 = hull_hw(z0, 0.15)+0.003; w1 = hull_hw(z1, 0.15)+0.003
            y0a=0.15-0.021; y0b=0.15+0.021
            mp.add_quad((side*w0,y0a,z0),(side*w0,y0b,z0),(side*w1,y0b,z1),(side*w1,y0a,z1), flip=(side<0))

    # ---- Window band ----
    mw = gb.mesh(win_glass, "windows")
    NW = 40
    for side in (1,-1):
        for i in range(NW-1):
            z0 = -5.80 + (5.60+5.80)*i/(NW-1); z1 = -5.80 + (5.60+5.80)*(i+1)/(NW-1)
            w0 = hull_hw(z0, 0.86)+0.004; w1 = hull_hw(z1, 0.86)+0.004
            mw.add_quad((side*w0,0.78,z0),(side*w0,0.95,z0),(side*w1,0.95,z1),(side*w1,0.78,z1), flip=(side<0))

    # ---- Swim platform ----
    mt = gb.mesh(teak, "platform")
    mt.add_box((0,0.32,-9.55),(2.12,0.04,0.90), uv_tile=(2.0,1.0))
    mp2 = gb.mesh(pvd, "platform_edge")
    mp2.add_box((0,0.32,-9.10),(2.12,0.05,0.03))
    for yy,zz in [(0.55,-8.97),(0.77,-8.71),(0.98,-8.45),(1.20,-8.19)]:
        mt.add_box((0,yy-0.02,zz),(2.12,0.04,0.26), uv_tile=(2.0,0.3))

    # ---- Foredeck plinth ----
    mt.add_chamfer_box((0,1.56,7.70),(1.6,0.06,1.4), bevel=0.02, uv_tile=1.0)

    # ---- Stanchion rails ----
    mr = gb.mesh(pvd, "rails")
    H = 0.68
    def rail_seg(z0, z1, side):
        n = max(2, int(abs(z1-z0)/0.6))
        for i in range(n):
            za = z0+(z1-z0)*i/n; zb = z0+(z1-z0)*(i+1)/n
            wa = hw(za)-0.06; wb = hw(zb)-0.06
            ya = y_deck(za); yb = y_deck(zb)
            mr.add_tube((side*wa,ya,za),(side*wa,ya+H,za),0.018,segs=8)
            mr.add_tube((side*wa,ya+H,za),(side*wb,yb+H,zb),0.018,segs=8)
    for side in (1,-1):
        rail_seg(-9.8, -5.75, side)
        rail_seg(-4.65, 9.5, side)
    for i in range(8):
        za = 8.5 + (9.5-8.5)*i/8; zb = 8.5 + (9.5-8.5)*(i+1)/8
        wa = hw(za)-0.06; wb = hw(zb)-0.06
        mr.add_tube((-wa,y_deck(za)+H,za),(wb,y_deck(zb)+H,zb),0.018,segs=8)

    # ---- Mast & boom ----
    mm = gb.mesh(pvd, "mast")
    mm.add_tube((0,1.33,2.55),(0,18.00,2.55),0.14,0.05,segs=16)
    mm.add_tube((0,4.55,2.55),(0,4.55,-3.15),0.09,0.06,segs=12)

    # ---- Six sail panels (8 mm chamfer, folded lower 3) ----
    ms = gb.mesh(sail_mat, "sails")
    mhng = gb.mesh(pvd, "hinges")
    y_bot = 4.75; y_top = 17.65
    n_pan = 6
    gap = 0.012
    total_h = y_top - y_bot
    ph = (total_h - gap*(n_pan-1))/n_pan
    for k in range(n_pan):
        y0 = y_bot + k*(ph+gap)
        y1 = y0 + ph
        tc = (k + 0.5)/n_pan
        c0 = 4.20 + (0.65-4.20)*tc
        th0 = 0.12*(1-0.5*tc)
        if k < 3:
            inner_c0 = c0*0.55
            outer_c0 = c0*0.45
            ms.add_chamfer_box((0,(y0+y1)/2, 2.55-inner_c0/2),(th0,ph,inner_c0), bevel=0.008, uv_tile=1.0)
            ang = math.radians(42)
            ox = -math.sin(ang)*outer_c0/2
            oz = 2.55-inner_c0 - math.cos(ang)*outer_c0/2
            ms.add_chamfer_box((ox,(y0+y1)/2,oz),(th0,ph,outer_c0), bevel=0.008, uv_tile=1.0, rot_y=ang)
            mhng.add_tube((0,y0,2.55-inner_c0),(0,y1,2.55-inner_c0),0.03,segs=8)
        else:
            ms.add_chamfer_box((0,(y0+y1)/2, 2.55-c0/2),(th0,ph,c0), bevel=0.008, uv_tile=1.0)

    # ---- Anchors ----
    gb.add_anchor("yacht_root", (0,0,0))
    gb.add_anchor("gangway_yacht", (-2.26,1.29,-5.20))
    gb.add_anchor("aft_cleat", (1.52,1.26,-8.55))
    gb.add_anchor("dog_bow", (0,1.58,7.70))
    gb.add_anchor("salon_mount", (0,1.30,0))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    return gb.export(OUT)

if __name__ == "__main__":
    build()
