"""
Shared deterministic periodic PBR noise, +Y tangent normal map, ORM packing,
2x2 seam verification, and .tex_cache serialization helpers (seed 404).
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import numpy as np
from PIL import Image

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tex_cache")


def periodic_noise(gx: int, gy: int, size_u: int, size_v: int | None = None, seed_offset: int = 0) -> np.ndarray:
    """
    2D periodic quintic value noise P(gx, gy) in [-1, 1] using modulo lattice lookup
    and pixel-center sampling (i + 0.5) / N with deterministic seed 404.
    """
    size_v = size_u if size_v is None else size_v
    rng = np.random.default_rng(404 + seed_offset + gx * 97 + gy * 389)
    grid = rng.uniform(-1.0, 1.0, size=(gy, gx))

    xs = ((np.arange(size_u, dtype=np.float64) + 0.5) / size_u) * gx
    ys = ((np.arange(size_v, dtype=np.float64) + 0.5) / size_v) * gy

    ix = np.floor(xs).astype(np.int64) % gx
    iy = np.floor(ys).astype(np.int64) % gy
    ix1 = (ix + 1) % gx
    iy1 = (iy + 1) % gy

    fx = xs - np.floor(xs)
    fy = ys - np.floor(ys)
    tx = fx * fx * fx * (fx * (fx * 6.0 - 15.0) + 10.0)
    ty = fy * fy * fy * (fy * (fy * 6.0 - 15.0) + 10.0)

    v00 = grid[np.ix_(iy, ix)]
    v10 = grid[np.ix_(iy, ix1)]
    v01 = grid[np.ix_(iy1, ix)]
    v11 = grid[np.ix_(iy1, ix1)]

    vx0 = v00 + (v10 - v00) * tx[None, :]
    vx1 = v01 + (v11 - v01) * tx[None, :]
    return vx0 + (vx1 - vx0) * ty[:, None]


def periodic_voronoi(cells: int, size: int, seed_offset: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """
    Fast vectorized periodic jittered Voronoi distance field on [0, size)^2.
    Returns (f1, f2 - f1) normalized in cell units (~[0..1]).
    """
    rng = np.random.default_rng(404 + seed_offset + cells * 31)
    jx = rng.uniform(0.15, 0.85, size=(cells, cells))
    jy = rng.uniform(0.15, 0.85, size=(cells, cells))
    px = ((np.arange(size, dtype=np.float64) + 0.5) / size) * cells
    py = ((np.arange(size, dtype=np.float64) + 0.5) / size) * cells
    gx = np.floor(px).astype(np.int64) % cells
    gy = np.floor(py).astype(np.int64) % cells
    ix, iy = np.meshgrid(gx, gy)
    fx, fy = np.meshgrid(px, py)
    d1 = np.full((size, size), 1e9, dtype=np.float64)
    d2 = np.full((size, size), 1e9, dtype=np.float64)
    for dy in (-1, 0, 1):
        ny = (iy + dy) % cells
        wy = (iy + dy) + jy[ny, 0]  # placeholder overwritten below
        for dx in (-1, 0, 1):
            nx = (ix + dx) % cells
            cx = (ix + dx) + jx[ny, nx]
            cy = (iy + dy) + jy[ny, nx]
            dist = np.hypot(fx - cx, fy - cy)
            mask1 = dist < d1
            d2 = np.where(mask1, d1, np.minimum(d2, dist))
            d1 = np.where(mask1, dist, d1)
    return d1, (d2 - d1)


def hex_to_srgb_vec(hex_str: str) -> np.ndarray:
    s = hex_str.lstrip("#")
    return np.array([int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)], dtype=np.float64)


def height_to_normal_y_up(height_m: np.ndarray, phys_w_m: float, phys_h_m: float) -> np.ndarray:
    """
    Convert periodic physical heightfield (meters) into +Y tangent normal map uint8 [H, W, 3].
    Wrap-around central differences: convex ridge has +X slope on left (-X side -> R>128)
    and +Y slope above (-Y in UV/row -> G>128).
    """
    ny_px, nx_px = height_m.shape
    dx_m = phys_w_m / max(1, nx_px)
    dy_m = phys_h_m / max(1, ny_px)
    dh_dx = (np.roll(height_m, -1, axis=1) - np.roll(height_m, 1, axis=1)) / (2.0 * dx_m)
    dh_dy = (np.roll(height_m, -1, axis=0) - np.roll(height_m, 1, axis=0)) / (2.0 * dy_m)
    # Tangent +U -> +X image right, Tangent +V -> -Y image row (V goes down row index -> +Y tangent is -dh/drow)
    nx = -dh_dx
    ny = dh_dy
    nz = np.ones_like(nx)
    inv = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz)
    rgb = np.stack(((nx * inv * 0.5 + 0.5), (ny * inv * 0.5 + 0.5), (nz * inv * 0.5 + 0.5)), axis=-1)
    return np.clip(np.round(rgb * 255.0), 0, 255).astype(np.uint8)


def pack_orm(ao: np.ndarray | float, rough: np.ndarray | float, metal: np.ndarray | float, shape: tuple[int, int]) -> np.ndarray:
    """Pack linear ORM uint8 texture: R=AO, G=roughness, B=metalness."""
    def _to_arr(v):
        if np.ndim(v) == 0:
            return np.full(shape, float(v), dtype=np.float64)
        return np.asarray(v, dtype=np.float64)

    a = np.clip(np.round(_to_arr(ao) * 255.0), 0, 255).astype(np.uint8)
    r = np.clip(np.round(_to_arr(rough) * 255.0), 0, 255).astype(np.uint8)
    m = np.clip(np.round(_to_arr(metal) * 255.0), 0, 255).astype(np.uint8)
    return np.stack((a, r, m), axis=-1)


def downsample_box(arr: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
    pil = Image.fromarray(arr.astype(np.uint8), mode="RGB")
    if pil.size == (target_w, target_h):
        return arr.astype(np.uint8)
    return np.asarray(pil.resize((target_w, target_h), Image.Resampling.LANCZOS), dtype=np.uint8)


def verify_seamless_2x2(arr: np.ndarray, name: str, max_jump: float = 35.0):
    """Verify horizontal and vertical wrap seams have no harsh tiling artifacts."""
    a = arr.astype(np.float64)
    row_diff = np.mean(np.abs(a[0] - a[-1]))
    col_diff = np.mean(np.abs(a[:, 0] - a[:, -1]))
    if row_diff > max_jump or col_diff > max_jump:
        raise AssertionError(f"{name} seam continuity jump too high: row={row_diff:.2f}, col={col_diff:.2f}")


def verify_convex_ridge_normal():
    """Sanity check that a positive bump produces +Y tangent normal convention."""
    xs = np.linspace(-1, 1, 32, endpoint=False)
    ys = np.linspace(-1, 1, 32, endpoint=False)
    xv, yv = np.meshgrid(xs, ys)
    dome = 0.001 * np.exp(-(xv * xv + yv * yv) * 6.0)
    nrm = height_to_normal_y_up(dome, 0.1, 0.1)
    # Left slope tilts toward -X (R < 128), top slope (row 10, uv V small) tilts toward +Y (G > 128)
    assert nrm[16, 12, 0] < 128 and nrm[12, 16, 1] > 128, f"Convex ridge check failed: {nrm[16,12]} {nrm[12,16]}"


def save_bundle(
    name: str,
    base_rgb: np.ndarray,
    orm_rgb: np.ndarray,
    norm_rgb: np.ndarray,
    base_fmt: str = "JPEG",
    quality: int = 90,
):
    os.makedirs(CACHE_DIR, exist_ok=True)
    b_buf = io.BytesIO()
    if base_fmt.upper() == "PNG":
        Image.fromarray(base_rgb, "RGB").save(b_buf, format="PNG", optimize=True)
        b_ext, b_mime = "png", "image/png"
    else:
        Image.fromarray(base_rgb, "RGB").save(b_buf, format="JPEG", quality=quality, optimize=True)
        b_ext, b_mime = "jpg", "image/jpeg"
    o_buf = io.BytesIO()
    Image.fromarray(orm_rgb, "RGB").save(o_buf, format="PNG", optimize=True)
    n_buf = io.BytesIO()
    Image.fromarray(norm_rgb, "RGB").save(n_buf, format="PNG", optimize=True)

    b_path = os.path.join(CACHE_DIR, f"{name}_base.{b_ext}")
    o_path = os.path.join(CACHE_DIR, f"{name}_orm.png")
    n_path = os.path.join(CACHE_DIR, f"{name}_nrm.png")
    with open(b_path, "wb") as f:
        f.write(b_buf.getvalue())
    with open(o_path, "wb") as f:
        f.write(o_buf.getvalue())
    with open(n_path, "wb") as f:
        f.write(n_buf.getvalue())

    meta = {
        "name": name,
        "base_file": os.path.basename(b_path),
        "base_mime": b_mime,
        "base_shape": list(base_rgb.shape[:2]),
        "orm_file": os.path.basename(o_path),
        "orm_shape": list(orm_rgb.shape[:2]),
        "norm_file": os.path.basename(n_path),
        "norm_shape": list(norm_rgb.shape[:2]),
    }
    with open(os.path.join(CACHE_DIR, f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def load_bundle(name: str) -> dict:
    meta_path = os.path.join(CACHE_DIR, f"{name}.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    with open(os.path.join(CACHE_DIR, meta["base_file"]), "rb") as f:
        base_bytes = f.read()
    with open(os.path.join(CACHE_DIR, meta["orm_file"]), "rb") as f:
        orm_bytes = f.read()
    with open(os.path.join(CACHE_DIR, meta["norm_file"]), "rb") as f:
        norm_bytes = f.read()
    return {
        "base_bytes": base_bytes,
        "base_mime": meta["base_mime"],
        "orm_bytes": orm_bytes,
        "norm_bytes": norm_bytes,
        "meta": meta,
    }
