import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from yacht_kit.yacht_prim_lib import YachtGLBBuilder
from yacht_kit.tex_helpers import load_bundle
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                   "assets", "models", "yacht_hull_rig.glb")

def clamp(v, a, b): return a if v < a else (b if v > b else v)

def pchip_eval(xs, ys, x):
    n = len(xs)
    if x <= xs[0]: return ys[0]
    if x >= xs[-1]: return ys[-1]
    h = [xs[i+1]-xs[i] for i in range(n-1)]
    d = [(ys[i+1]-ys[i])/h[i] for i in range(n-1)]
    m = [0.0]*n
    m[0] = d[0]; m[-1] = d[-1]
    for i in range(1, n-1):
        if d[i-1]*d[i] <= 0: m[i] = 0.0
        else:
            w1 = 2*h[i]+h[i-1]; w2 = h[i]+2*h[i-1]
            m[i] = (w1+w2)/(w1/d[i-1]+w2/d[i])
    for i in range(n-1):
        if d[i] == 0: m[i] = m[i+1] = 0.0
        else:
            a = m[i]/d[i]; b = m[i+1]/d[i]
            s = a*a+b*b
            if s > 9:
                t = 3.0/math.sqrt(s); m[i] = t*a*d[i]; m[i+1] = t*b*d[i]
    i = 0
    while i < n-2 and x > xs[i+1]: i += 1
    t = (x-xs[i])/h[i]
    h00 = 2*t**3-3*t**2+1; h10 = t**3-2*t**2+t
    h01 = -2*t**3+3*t**2; h11 = t**3-t**2
    return h00*ys[i]+h10*h[i]*m[i]+h01*ys[i+1]+h11*h[i]*m[i+1]

CP = [(-10.0,1.24),(-7.8,1.84),(-3.0,2.38),(2.0,2.38),(5.5,1.94),(8.2,1.02),(10.0,0.0)]
SH = [(-10.0,1.20),(-6.0,1.24),(0.0,1.32),(5.5,1.44),(10.0,1.62)]
CPX = [p[0] for p in CP]; CPY = [p[1] for p in CP]
SHX = [p[0] for p in SH]; SHY = [p[1] for p in SH]

def hw(z): return min(2.39, max(0.0, pchip_eval(CPX, CPY, z)))
def sheer(z): return pchip_eval(SHX, SHY, z)
def hull_hw(z, y):
    base = hw(z)
    flare = 0.03*max(0.0, z-3.0)/7.0
    if y < 0.15:
        t = clamp((0.15-y)/0.73, 0.0, 1.0)
        base *= (1.0 - 0.55*t*t)
    return min(2.39, base+flare)
def z_stem(y): return 9.52 + 0.46*clamp(y/1.62, -0.35, 1.0)

def to_grid(rows):
    if np is not None:
        return np.array(rows, dtype=float)
    return rows

gb = YachtGLBBuilder("yacht_hull_rig")
hb = load_bundle("hull_satin"); tb = load_bundle("teak_deck")
tf = load_bundle("teak_frame"); pb = load_bundle("pvd_brushed")
sb = load_bundle("sail_coated")

hull_mat = gb.add_pbr_material("hull_satin", base_bytes=hb["base_bytes"], base_mime=hb["base_mime"],
    orm_bytes=hb["orm_bytes"], normal_bytes=hb["norm_bytes"], roughness=0.28, clearcoat=0.6, clearcoat_roughness=0.08)
teak = gb.add_pbr_material("teak_deck", base_bytes=tb["base_bytes"], base_mime=tb["base_mime"],
    orm_bytes=tb["orm_bytes"], normal_bytes=tb["norm_bytes"], roughness=0.55)
teak_rail = gb.add_pbr_material("teak_rail", base_bytes=tf["base_bytes"], base_mime=tf["base_mime"],
    orm_bytes=tf["orm_bytes"], normal_bytes=tf["norm_bytes"], roughness=0.45, clearcoat=0.14)
pvd = gb.add_pbr_material("pvd_brushed", base_bytes=pb["base_bytes"], base_mime=pb["base_mime"],
    orm_bytes=pb["orm_bytes"], normal_bytes=pb["norm_bytes"], roughness=0.22, metalness=1.0)
sail_mat = gb.add_pbr_material("sail_coated", base_bytes=sb["base_bytes"], base_mime=sb["base_mime"],
    orm_bytes=sb["orm_bytes"], normal_bytes=sb["norm_bytes"], roughness=0.7, double_sided=True)
win_glass = gb.add_pbr_material("win_glass", base_factor=(0.05,0.08,0.10,1.0), roughness=0.05, metalness=0.0)

# ---- Hull shell (z clamped to [-9.98, 9.98]) ----
NZ, NY = 84, 24
ZMIN, ZMAX = -9.98, 9.98
mh = gb.mesh(hull_mat, "hull_shell")
for side in (-1, 1):
    grid = []; uvg = []
    for i in range(NZ+1):
        z = ZMIN + (ZMAX-ZMIN)*i/NZ
        row = []; uvr = []
        for j in range(NY+1):
            t = j/NY
            y = sheer(z) - t*(sheer(z)+0.58)
            x = side*hull_hw(z, y)
            if z > 9.0: x = side*max(0.0, hull_hw(z,y)*(1.0-(z-9.0)/1.0))
            row.append((x, y, z)); uvr.append((i/NZ*4.0, t*2.0))
        grid.append(row); uvg.append(uvr)
    mh.add_grid(to_grid(grid), to_grid(uvg), flip=(side<0), smooth_normals=True, seam_u=False)

# keel plate
mk = gb.mesh(hull_mat, "keel_plate")
mk.add_quad((-0.9,-0.58,-9.0),(0.9,-0.58,-9.0),(0.9,-0.58,9.0),(-0.9,-0.58,9.0),flip=True)
mk.add_tube((0,-0.58,1.2),(0,-1.55,1.2),0.10,0.06,segs=12)
mk.add_tube((0,-1.55,1.2),(0,-1.62,1.2),0.06,0.02,segs=12)

# transom quarter bulwarks
mb = gb.mesh(hull_mat, "bulwark")
for side in (-1,1):
    for i in range(8):
        za = -9.98+1.98*i/8; zb = -9.98+1.98*(i+1)/8
        xa = side*clamp(hull_hw(za,1.0),1.06,2.39)
        xb = side*clamp(hull_hw(zb,1.0),1.06,2.39)
        ya = sheer(za); yb = sheer(zb)
        mb.add_quad((side*1.06,ya,za),(xa,ya,za),(xb,yb,zb),(side*1.06,yb,zb),flip=(side<0))

# ---- Deck (true 0.64m x 2.56m quarter-sawn Burma teak plank scaling!) ----
ND = 64
md = gb.mesh(teak, "deck")
grid = []; uvg = []
for i in range(ND+1):
    z = ZMIN + (ZMAX-ZMIN)*i/ND
    w = hw(z)
    row = [(-w, sheer(z), z), (w, sheer(z), z)]
    uvr = [(-w / 0.64, z / 2.56), (w / 0.64, z / 2.56)]
    grid.append(row); uvg.append(uvr)
md.add_grid(to_grid(grid), to_grid(uvg), flip=True, smooth_normals=True)

# ---- Deckhead dark backing 4cm below teak ----
mh_back = gb.mesh(hull_mat, "deckhead_backing")
for i in range(ND):
    z0 = ZMIN + (ZMAX-ZMIN)*i/ND; z1 = ZMIN + (ZMAX-ZMIN)*(i+1)/ND
    w0, w1 = hw(z0), hw(z1)
    y0, y1 = sheer(z0) - 0.04, sheer(z1) - 0.04
    mh_back.add_quad((-w0, y0, z0), (w0, y0, z0), (w1, y1, z1), (-w1, y1, z1))

# ---- Toe-rail / gunwale cap ----
mr = gb.mesh(teak_rail, "toe_rail")
for side in (-1,1):
    for i in range(ND):
        z0 = ZMIN+(ZMAX-ZMIN)*i/ND; z1 = ZMIN+(ZMAX-ZMIN)*(i+1)/ND
        w0 = hw(z0)-0.035; w1 = hw(z1)-0.035
        y0 = sheer(z0); y1 = sheer(z1)
        mr.add_tube((side*w0,y0+0.02,z0),(side*w1,y1+0.02,z1),0.028,0.028,segs=8,cap=False)

# ---- Waterline stripe ----
ms = gb.mesh(pvd, "stripe")
for side in (-1,1):
    for i in range(ND):
        z0 = ZMIN+(ZMAX-ZMIN)*i/ND; z1 = ZMIN+(ZMAX-ZMIN)*(i+1)/ND
        x0 = side*(hull_hw(z0,0.15)+0.004); x1 = side*(hull_hw(z1,0.15)+0.004)
        ms.add_quad((x0,0.129,z0),(x0,0.171,z0),(x1,0.171,z1),(x1,0.129,z1),flip=(side<0))

# ---- Windows ----
mw = gb.mesh(win_glass, "windows")
for side in (-1,1):
    for i in range(12):
        z0 = -5.8+11.4*i/12; z1 = -5.8+11.4*(i+1)/12
        x0 = side*(hull_hw(z0,0.86)+0.006); x1 = side*(hull_hw(z1,0.86)+0.006)
        mw.add_quad((x0,0.78,z0),(x0,0.95,z0),(x1,0.95,z1),(x1,0.78,z1),flip=(side<0))

# ---- Foredeck plinth ----
mf = gb.mesh(teak, "foredeck")
mf.add_box((0,1.56,7.70),(1.4,0.06,1.2),uv_tile=(2.0,2.0))

# ---- Recessed transom steps ----
mst = gb.mesh(teak, "transom_steps")
steps = [(-8.19,1.20),(-8.45,0.98),(-8.71,0.77),(-8.97,0.55)]
for i in range(len(steps)-1):
    z0,y0 = steps[i]; z1,y1 = steps[i+1]
    mst.add_box((0,(y0+y1)/2-0.02,(z0+z1)/2),(2.12,0.04,abs(z1-z0)+0.02),uv_tile=(3.0,1.0))
mst.add_box((0,0.30,-9.46),(2.12,0.04,1.00),uv_tile=(3.0,2.0))
mt = gb.mesh(pvd, "stair_trim")
for side in (-1,1):
    for i in range(len(steps)-1):
        z0,y0 = steps[i]; z1,y1 = steps[i+1]
        mt.add_tube((side*1.06,y0,z0),(side*1.06,y1,z1),0.012,0.012,segs=6)

# ---- Stanchions + lifelines + top rail ----
mstan = gb.mesh(pvd, "stanchions")
mline = gb.mesh(pvd, "lifelines")
mrail = gb.mesh(teak_rail, "top_rail")
H = 0.68
for side in (-1,1):
    zs = []
    z = -9.5
    while z < 9.0:
        if not (side==-1 and -5.75 < z < -4.65):
            zs.append(z)
        z += 1.3
    pts = []
    for z in zs:
        w = hw(z)-0.035
        y = sheer(z)
        mstan.add_tube((side*w,y,z),(side*w,y+H,z),0.016,0.011,segs=8)
        pts.append((side*w,y,z))
    for i in range(len(pts)-1):
        p0 = pts[i]; p1 = pts[i+1]
        for frac in (0.25,0.50):
            mline.add_tube((p0[0],p0[1]+H*frac,p0[2]),(p1[0],p1[1]+H*frac,p1[2]),0.005,0.005,segs=6,cap=False)
        mrail.add_tube((p0[0],p0[1]+H,p0[2]),(p1[0],p1[1]+H,p1[2]),0.021,0.021,segs=8,cap=False)
    p_end = pts[-1]
    p_bow_knuckle = (side*(hw(9.0)-0.035), sheer(9.0), 9.0)
    p_bow_tip = (0.0, sheer(9.5)+0.05, 9.5)
    mstan.add_tube(p_bow_knuckle, (p_bow_knuckle[0], p_bow_knuckle[1]+H, p_bow_knuckle[2]), 0.016, 0.012, segs=8)
    for frac in (0.25, 0.50):
        mline.add_tube((p_end[0], p_end[1]+H*frac, p_end[2]), (p_bow_knuckle[0], p_bow_knuckle[1]+H*frac, p_bow_knuckle[2]), 0.005, 0.005, segs=6, cap=False)
        mline.add_tube((p_bow_knuckle[0], p_bow_knuckle[1]+H*frac, p_bow_knuckle[2]), (p_bow_tip[0], p_bow_tip[1]+H*frac, p_bow_tip[2]), 0.005, 0.005, segs=6, cap=False)
    mrail.add_tube((p_end[0], p_end[1]+H, p_end[2]), (p_bow_knuckle[0], p_bow_knuckle[1]+H, p_bow_knuckle[2]), 0.021, 0.021, segs=8, cap=False)
    mrail.add_tube((p_bow_knuckle[0], p_bow_knuckle[1]+H, p_bow_knuckle[2]), (p_bow_tip[0], p_bow_tip[1]+H, p_bow_tip[2]), 0.021, 0.021, segs=8)
mstan.add_tube((0.0, sheer(9.45), 9.45), (0.0, sheer(9.5)+H+0.05, 9.5), 0.016, 0.012, segs=8)

# ---- Mast, boom, sails (Corinthian 6-panel SolidSail with lower 3 folded 42 deg!) ----
mm = gb.mesh(pvd, "mast")
mm.add_tube((0, 1.33, 2.55), (0, 17.95, 2.55), 0.14, 0.05, segs=16)
mm.add_tube((0, 4.55, 2.55), (0, 4.55, -3.15), 0.09, 0.06, segs=12)
msail = gb.mesh(sail_mat, "sails")
mhng = gb.mesh(pvd, "hinges")
y_bot, y_top, n_pan, gap = 4.75, 17.65, 6, 0.012
ph = (y_top - y_bot - gap * (n_pan - 1)) / n_pan
for k in range(n_pan):
    y0s = y_bot + k * (ph + gap)
    y1s = y0s + ph
    tc = (k + 0.5) / n_pan
    c0 = 4.20 + (0.65 - 4.20) * tc
    th0 = 0.12 * (1.0 - 0.5 * tc)
    if k < 3:
        in_c, out_c = c0 * 0.55, c0 * 0.45
        msail.add_chamfer_box((0, (y0s + y1s) / 2, 2.55 - in_c / 2), (th0, ph, in_c), bevel=0.008, uv_tile=1.0)
        ang = math.radians(42)
        ox = -math.sin(ang) * out_c / 2
        oz = 2.55 - in_c - math.cos(ang) * out_c / 2
        msail.add_chamfer_box((ox, (y0s + y1s) / 2, oz), (th0, ph, out_c), bevel=0.008, uv_tile=1.0, rot_y=ang)
        mhng.add_tube((0, y0s, 2.55 - in_c), (0, y1s, 2.55 - in_c), 0.03, segs=8)
    else:
        msail.add_chamfer_box((0, (y0s + y1s) / 2, 2.55 - c0 / 2), (th0, ph, c0), bevel=0.008, uv_tile=1.0)

# ---- Anchors ----
gb.add_anchor("yacht_root",(0,0,0))
gb.add_anchor("gangway_yacht",(-2.26,1.29,-5.20))
gb.add_anchor("aft_cleat",(1.52,1.26,-8.55))
gb.add_anchor("dog_bow",(0,1.58,7.70))
gb.add_anchor("salon_mount",(0,1.30,0))

gb.export(OUT)
print("wrote", OUT)
