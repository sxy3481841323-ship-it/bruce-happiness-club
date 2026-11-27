import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from yacht_kit.tex_helpers import (
    periodic_noise, periodic_voronoi, hex_to_srgb_vec, height_to_normal_y_up,
    pack_orm, downsample_box, verify_seamless_2x2, verify_convex_ridge_normal,
    save_bundle,
)

S = 1024
yy, xx = np.mgrid[0:S, 0:S].astype(np.float64)
u = xx / S
v = yy / S


def _leather_base():
    f1, edge = periodic_voronoi(64, S, seed_offset=50)
    dome = np.clip(1.0 - f1 * 1.6, 0.0, 1.0)
    crease = np.clip(1.0 - edge / 0.14, 0.0, 1.0)
    pin = (periodic_noise(192, 192, S, seed_offset=51) > 0.78).astype(np.float64)
    pin = np.clip(pin * 1.0, 0.0, 1.0)
    h = 0.00006 * (dome * 0.7 - crease * 0.6) - 0.00006 * pin
    return dome, crease, pin, h


def _apply_crest(h, base_rgb):
    cx, cy = 512.0, 420.0
    dx = xx - cx
    dy = yy - cy
    # rotate 45 deg -> diamond distance
    d = (np.abs(dx + dy) + np.abs(dx - dy)) * 0.5 / np.sqrt(2.0) * np.sqrt(2.0)
    d = (np.abs(dx) + np.abs(dy)) / np.sqrt(2.0)
    outer = 160.0
    inner = 122.0
    lw = 3.0
    groove = np.zeros_like(h)
    for r in (outer, inner):
        band = np.exp(-((d - r) / lw) ** 2)
        groove = np.maximum(groove, band)
    # corner dots
    for sx in (-1, 1):
        for sy in (-1, 1):
            px = cx + sx * outer * 0.7071
            py = cy + sy * outer * 0.7071
            dd = np.sqrt((xx - px) ** 2 + (yy - py) ** 2)
            groove = np.maximum(groove, np.exp(-(dd / 4.0) ** 2))
    h = h - 0.00018 * groove
    dark = hex_to_srgb_vec("#744129")
    mix = np.clip(groove, 0, 1)[..., None]
    base_rgb = base_rgb * (1 - mix * 0.85) + dark * (mix * 0.85)
    return h, base_rgb, groove


def _save(name, base, orm, norm, fmt="JPEG", q=90, mj=35.0):
    verify_seamless_2x2(base, name + "_base", max_jump=mj)
    verify_seamless_2x2(orm, name + "_orm", max_jump=mj)
    verify_seamless_2x2(norm, name + "_norm", max_jump=mj)
    save_bundle(name, base, orm, norm, base_fmt=fmt, quality=q)


# 1. saddle_leather
dome, crease, pin, h = _leather_base()
base = hex_to_srgb_vec("#925638")[None, None, :] * np.ones((S, S, 1))
shade = (0.85 + 0.15 * dome)[..., None]
base = base * shade
base = base * (1 - 0.35 * pin[..., None])
base = np.clip(base, 0, 255)
rough = 0.53 + 0.045 * (crease - 0.5) * 2 + 0.03 * pin
rough = np.clip(rough, 0, 1)
ao = np.clip(1.0 - 0.25 * crease - 0.3 * pin, 0, 1)
orm = pack_orm(ao, rough, np.zeros_like(rough), (S, S))
norm = height_to_normal_y_up(h, 0.40, 0.40)
_save("saddle_leather", base.astype(np.uint8), orm, norm, "JPEG", 92)

# 2. saddle_leather_crest
h2, base2, groove = _apply_crest(h.copy(), base.copy())
rough2 = np.clip(rough + 0.05 * groove, 0, 1)
ao2 = np.clip(ao - 0.3 * groove, 0, 1)
orm2 = pack_orm(ao2, rough2, np.zeros_like(rough2), (S, S))
norm2 = height_to_normal_y_up(h2, 0.40, 0.40)
_save("saddle_leather_crest", np.clip(base2, 0, 255).astype(np.uint8), orm2, norm2, "PNG", 90, mj=55.0)

# 3. stitch_strip
H = 128
yy2, xx2 = np.mgrid[0:H, 0:S].astype(np.float64)
f1s, edges = periodic_voronoi(64, S, seed_offset=50)
f1s = f1s[:H]
base_s = hex_to_srgb_vec("#925638")[None, None, :] * np.ones((H, S, 1))
base_s = base_s * (0.9 + 0.1 * np.clip(1 - f1s * 1.6, 0, 1))[..., None]
h_s = 0.00006 * np.clip(1 - f1s * 1.6, 0, 1)
thread = hex_to_srgb_vec("#DDD0BC")
pitch = 16.0
phase = (xx2 % pitch)
in_band = (yy2 >= 48) & (yy2 < 80)
stitch_mask = in_band & (phase < 10.0) & (yy2 >= 60) & (yy2 < 68)
end_mask = in_band & (((phase >= 9.0) & (phase < 11.0)) | (phase < 1.0)) & (yy2 >= 58) & (yy2 < 70)
bevel = np.exp(-((yy2 - 64.0) / 3.0) ** 2)
h_s = h_s + 0.00018 * stitch_mask * bevel
base_s = np.where(stitch_mask[..., None], thread[None, None, :] * (0.9 + 0.1 * bevel[..., None]), base_s)
base_s = base_s * (1 - 0.4 * end_mask[..., None])
rough_s = np.where(stitch_mask, 0.78, 0.53)
ao_s = np.clip(1.0 - 0.4 * end_mask, 0, 1)
orm_s = pack_orm(ao_s, rough_s, np.zeros_like(rough_s), (H, S))
norm_s = height_to_normal_y_up(h_s, 0.40, 0.05)
_save("stitch_strip", np.clip(base_s, 0, 255).astype(np.uint8), orm_s, norm_s, "PNG", 90)

# 4. woven_rug
cell = 16
cx = (xx // cell).astype(int)
cy = (yy // cell).astype(int)
stripe = (cy // 1) % 2
weave = ((cx + cy) % 4 < 2).astype(np.float64)
herring = ((cx // 4 + cy // 4) % 2)
pile = np.where(herring == 0, weave, 1 - weave)
h_r = 0.00012 * (pile - 0.5) * 2
base_r = hex_to_srgb_vec("#B5A692")[None, None, :] * np.ones((S, S, 1))
base_r = base_r * (0.88 + 0.12 * pile)[..., None]
rough_r = np.full((S, S), 0.91)
orm_r = pack_orm(np.ones((S, S)), rough_r, np.zeros((S, S)), (S, S))
norm_r = height_to_normal_y_up(h_r, 0.40, 0.40)
_save("woven_rug", np.clip(base_r, 0, 255).astype(np.uint8), orm_r, norm_r, "JPEG", 90)

# 5. outdoor_linen
cell = 16
cx = (xx // cell).astype(int)
cy = (yy // cell).astype(int)
fx = (xx % cell) / cell
fy = (yy % cell) / cell
slub = 0.12 * periodic_noise(64, 64, S, seed_offset=60)
warp_w = 0.78 + 0.14 * np.clip(0.5 + 0.5 * periodic_noise(64, 1, S, seed_offset=61), 0, 1) + slub
weft_w = 0.78 + 0.14 * np.clip(0.5 + 0.5 * periodic_noise(1, 64, S, seed_offset=62), 0, 1) + slub
warp_prof = np.clip(1 - ((fx - 0.5) / (warp_w * 0.5)) ** 2, 0, 1)
weft_prof = np.clip(1 - ((fy - 0.5) / (weft_w * 0.5)) ** 2, 0, 1)
over = ((cx + cy) % 2 == 0)
h_l = np.where(over, warp_prof, weft_prof) * 0.00008
base_l = hex_to_srgb_vec("#D5C8AF")[None, None, :] * np.ones((S, S, 1))
base_l = base_l * (0.85 + 0.15 * np.where(over, warp_prof, weft_prof))[..., None]
rough_l = np.clip(0.86 + 0.04 * (periodic_noise(128, 128, S, seed_offset=63)), 0, 1)
orm_l = pack_orm(np.ones((S, S)), rough_l, np.zeros((S, S)), (S, S))
norm_l = height_to_normal_y_up(h_l, 0.080, 0.080)
_save("outdoor_linen", np.clip(base_l, 0, 255).astype(np.uint8), orm_l, norm_l, "JPEG", 90)

# 6. sail_coated
cell = 8
cx = (xx // cell).astype(int)
cy = (yy // cell).astype(int)
over = ((cx + cy) % 2 == 0)
fx = (xx % cell) / cell
fy = (yy % cell) / cell
prof = np.where(over, np.sin(fx * np.pi), np.sin(fy * np.pi))
h_sc = 0.000008 * prof
scrim = 0.5 + 0.5 * np.sin(xx * 2 * np.pi / 256.0)
base_sc = hex_to_srgb_vec("#ECE5D6")[None, None, :] * np.ones((S, S, 1))
base_sc = base_sc * (0.97 + 0.03 * prof)[..., None] * (0.99 + 0.01 * scrim)[..., None]
rough_sc = np.clip(0.52 + 0.018 * periodic_noise(128, 128, S, seed_offset=70), 0, 1)
orm_sc = pack_orm(np.ones((S, S)), rough_sc, np.zeros((S, S)), (S, S))
norm_sc = height_to_normal_y_up(h_sc, 0.40, 0.40)
_save("sail_coated", np.clip(base_sc, 0, 255).astype(np.uint8), orm_sc, norm_sc, "JPEG", 92)


# 7. brushed metals
def _brushed(name, hexcol, rough_base):
    brush = periodic_noise(256, 8, S, seed_offset=80) + 0.5 * periodic_noise(128, 16, S, seed_offset=81)
    brush = brush / 1.5
    base_m = hex_to_srgb_vec(hexcol)[None, None, :] * np.ones((S, S, 1))
    base_m = base_m + 3.0 * brush[..., None]
    rough_m = np.clip(rough_base + 0.045 * brush, 0, 1)
    # sparse micro-scratches
    rng = np.random.default_rng(123)
    scratch = np.zeros((S, S))
    for _ in range(60):
        sx = int(rng.integers(0, S))
        sy = int(rng.integers(0, S))
        ln = int(rng.integers(18, 85))
        wd = int(rng.integers(1, 3))
        y0 = sy
        y1 = min(S, sy + ln)
        x0 = sx
        x1 = min(S, sx + wd)
        scratch[y0:y1, x0:x1] = 1.0
        if y1 == S:
            scratch[0:ln - (S - sy), x0:x1] = 1.0
    base_m = base_m * (1 - 0.15 * scratch[..., None])
    rough_m = np.clip(rough_m + 0.1 * scratch, 0, 1)
    h_m = 0.000006 * brush
    orm_m = pack_orm(np.ones((S, S)), rough_m, np.ones((S, S)), (S, S))
    norm_m = height_to_normal_y_up(h_m, 0.40, 0.40)
    _save(name, np.clip(base_m, 0, 255).astype(np.uint8), orm_m, norm_m, "PNG", 90)


_brushed("pvd_brushed", "#B49A72", 0.27)
_brushed("bronze_brushed", "#80664A", 0.35)

print("OK tex_fabrics_metals")
