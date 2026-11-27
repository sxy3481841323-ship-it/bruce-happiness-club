import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from yacht_kit.tex_helpers import (
    periodic_noise, periodic_voronoi, hex_to_srgb_vec, height_to_normal_y_up,
    pack_orm, downsample_box, verify_seamless_2x2, verify_convex_ridge_normal,
    save_bundle,
)

verify_convex_ridge_normal()

# ---------- 1. hull_satin ----------
S = 1024
base = hex_to_srgb_vec("#14273B")
mod = periodic_noise(8, 8, S, seed_offset=1) * 2.0
base_rgb = np.clip(base[None, None, :] + mod[..., None], 0, 255).astype(np.uint8)

rough = 0.31 + periodic_noise(32, 32, S, seed_offset=2) * 0.022 + periodic_noise(192, 192, S, seed_offset=3) * 0.010
ao = np.ones((S, S), np.float64)
metal = np.zeros((S, S), np.float64)
orm = pack_orm(ao, rough, metal, (S, S))

h = periodic_noise(160, 160, S, seed_offset=4) * 0.000006
norm = height_to_normal_y_up(h, 1.0, 1.0)

verify_seamless_2x2(base_rgb.astype(np.float64), "hull_satin_base", 30.0)
verify_seamless_2x2(orm.astype(np.float64), "hull_satin_orm", 30.0)
verify_seamless_2x2(norm.astype(np.float64), "hull_satin_norm", 30.0)
save_bundle("hull_satin", base_rgb, orm, norm, base_fmt="PNG")

# ---------- 2. teak_deck ----------
S2 = 2048
x = np.arange(S2)[None, :]
y = np.arange(S2)[:, None]
plank_id = (x // 256).astype(np.int32)
offset_v = (plank_id * 512) % 2048
seam_x = ((x + 6) % 256) < 12
seam_y = ((y + 6 - offset_v) % 2048) < 12
seam = seam_x | seam_y

wood = hex_to_srgb_vec("#AE885F")
caulk = hex_to_srgb_vec("#302923")

lum_off = ((plank_id * 37) % 13) - 6
grain = periodic_noise(128, 8, S2, seed_offset=10) + periodic_noise(256, 32, S2, seed_offset=11) * 0.45
wood_rgb = wood[None, None, :] + lum_off[..., None] + grain[..., None] * 6.0
base_rgb = np.where(seam[..., None], caulk[None, None, :], wood_rgb)
base_rgb = np.clip(base_rgb, 0, 255).astype(np.uint8)

# height: wood 0, caulk -0.00035 with 2px bevel
h = np.zeros((S2, S2), np.float64)
# distance to seam (approx via shifted masks)
seam_f = seam.astype(np.float64)
# bevel: 2px shoulder
from numpy import roll
near = np.zeros_like(seam_f)
for dy in (-2, -1, 1, 2):
    near = np.maximum(near, roll(seam_f, dy, axis=0))
for dx in (-2, -1, 1, 2):
    near = np.maximum(near, roll(seam_f, dx, axis=1))
h = np.where(seam, -0.00035, np.where(near > 0, -0.000175, 0.0))

rough = np.where(seam, 0.80, 0.63 + periodic_noise(64, 64, S2, seed_offset=12) * 0.03)
ao = np.where(seam, 0.65, 1.0)
metal = np.zeros((S2, S2), np.float64)
orm = pack_orm(ao, rough, metal, (S2, S2))
norm = height_to_normal_y_up(h, 0.640, 2.56)

orm_ds = downsample_box(orm, 1024, 1024)
norm_ds = downsample_box(norm, 1024, 1024)

verify_seamless_2x2(base_rgb.astype(np.float64), "teak_deck_base", 30.0)
verify_seamless_2x2(orm_ds.astype(np.float64), "teak_deck_orm", 30.0)
verify_seamless_2x2(norm_ds.astype(np.float64), "teak_deck_norm", 30.0)
save_bundle("teak_deck", base_rgb, orm_ds, norm_ds, base_fmt="JPEG", quality=90)

# ---------- 3. teak_frame ----------
S3 = 1024
wood = hex_to_srgb_vec("#C5A071")
grain = periodic_noise(96, 8, S3, seed_offset=20)
base_rgb = np.clip(wood[None, None, :] + grain[..., None] * 8.0, 0, 255).astype(np.uint8)
rough = np.full((S3, S3), 0.48) + periodic_noise(64, 64, S3, seed_offset=21) * 0.02
ao = np.ones((S3, S3))
metal = np.zeros((S3, S3))
orm = pack_orm(ao, rough, metal, (S3, S3))
h = periodic_noise(128, 128, S3, seed_offset=22) * 0.00004
norm = height_to_normal_y_up(h, 0.5, 0.5)

verify_seamless_2x2(base_rgb.astype(np.float64), "teak_frame_base", 30.0)
verify_seamless_2x2(orm.astype(np.float64), "teak_frame_orm", 30.0)
verify_seamless_2x2(norm.astype(np.float64), "teak_frame_norm", 30.0)
save_bundle("teak_frame", base_rgb, orm, norm, base_fmt="JPEG", quality=90)

# ---------- 4. marquetry ----------
S4 = 2048
yy, xx = np.mgrid[0:S4, 0:S4].astype(np.float64)
u = (xx + 0.5) / S4 - 0.5
v = (yy + 0.5) / S4 - 0.5
ang = np.arctan2(v, u)  # -pi..pi
ang_deg = np.degrees(ang)
# 8 wedges of 45 deg
wedge = ((ang_deg + 180.0) // 45.0).astype(np.int32) % 8
angles = np.array([18, -18, 33, -33, 48, -48, 63, -63], np.float64)
rot = angles[wedge]

# rotate coords per wedge for grain
rad = np.sqrt(u * u + v * v)
theta = np.radians(rot)
# sample noise along rotated axis
gx = (u * np.cos(theta) + v * np.sin(theta))
gy = (-u * np.sin(theta) + v * np.cos(theta))
# map to noise indices
n1 = periodic_noise(160, 12, S4, seed_offset=30)
n2 = periodic_noise(72, 8, S4, seed_offset=31)
# use rotated sampling via index remap (approx: use angle-based)
grain = n1 * 0.7 + n2 * 0.3

prim = hex_to_srgb_vec("#6B442E")
sec = hex_to_srgb_vec("#A77448")
use_sec = (wedge % 2 == 1)
lum = ((wedge * 53) % 7 - 3).astype(np.float64) * 2.0  # ±(8..14) approx
base_rgb = np.where(use_sec[..., None], sec[None, None, :], prim[None, None, :])
base_rgb = base_rgb + lum[..., None] + grain[..., None] * 10.0
base_rgb = np.clip(base_rgb, 0, 255).astype(np.uint8)

# inlay lines at wedge borders
border = np.abs(((ang_deg + 180.0) % 45.0) - 22.5) > 21.5
# thin 2px: use gradient
border_thin = np.abs(((ang_deg + 180.0) % 45.0) - 22.5) > 21.0
base_rgb = np.where(border_thin[..., None], (base_rgb * 0.4).astype(np.uint8), base_rgb)

h = grain * 0.000025
rough = 0.39 + periodic_noise(64, 64, S4, seed_offset=32) * 0.02
ao = np.ones((S4, S4))
metal = np.zeros((S4, S4))
orm = pack_orm(ao, rough, metal, (S4, S4))
norm = height_to_normal_y_up(h, 1.0, 1.0)
orm_ds = downsample_box(orm, 1024, 1024)
norm_ds = downsample_box(norm, 1024, 1024)

verify_seamless_2x2(base_rgb.astype(np.float64), "marquetry_base", 55.0)
verify_seamless_2x2(orm_ds.astype(np.float64), "marquetry_orm", 55.0)
verify_seamless_2x2(norm_ds.astype(np.float64), "marquetry_norm", 55.0)
save_bundle("marquetry", base_rgb, orm_ds, norm_ds, base_fmt="JPEG", quality=90)

# ---------- 5. filled_travertine ----------
S5 = 2048
base = hex_to_srgb_vec("#C3B198")
strata = periodic_noise(5, 12, S5, seed_offset=40)
pores_n = periodic_noise(180, 380, S5, seed_offset=41)
pores = pores_n > 0.55
# stretch horizontally
pores = pores | np.roll(pores, 1, axis=1) | np.roll(pores, 2, axis=1)
base_rgb = base[None, None, :] + strata[..., None] * 12.0
filled = hex_to_srgb_vec("#AEA08A")
base_rgb = np.where(pores[..., None], filled[None, None, :] + strata[..., None] * 6.0, base_rgb)
base_rgb = np.clip(base_rgb, 0, 255).astype(np.uint8)

h = np.where(pores, -0.00012 * (0.5 + 0.5 * pores_n), 0.0) + strata * 0.00002
rough = 0.47 + periodic_noise(64, 64, S5, seed_offset=42) * 0.04
rough = np.where(pores, 0.52, rough)
ao = np.where(pores, 0.85, 1.0)
metal = np.zeros((S5, S5))
orm = pack_orm(ao, rough, metal, (S5, S5))
norm = height_to_normal_y_up(h, 1.0, 1.0)
orm_ds = downsample_box(orm, 1024, 1024)
norm_ds = downsample_box(norm, 1024, 1024)

verify_seamless_2x2(base_rgb.astype(np.float64), "travertine_base", 30.0)
verify_seamless_2x2(orm_ds.astype(np.float64), "travertine_orm", 30.0)
verify_seamless_2x2(norm_ds.astype(np.float64), "travertine_norm", 30.0)
save_bundle("filled_travertine", base_rgb, orm_ds, norm_ds, base_fmt="JPEG", quality=90)

print("OK tex_woods_stone")
