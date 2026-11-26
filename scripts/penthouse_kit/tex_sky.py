"""Procedural sky panoramas for the penthouse kit.

Two generators:
  * make_sunny_sky_panorama  - bright Mediterranean azure cyclorama
  * make_rainy_sky_panorama  - cozy slate-blue rainy sky

All noise is vectorized NumPy (multi-octave value/fBm noise via bilinear
upsampling of small random lattices) so 4096x2048 renders in well under 2s.
"""

from __future__ import annotations

import numpy as np
from PIL import Image


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _lerp(a, b, t):
    return a + (b - a) * t


def _hex(c):
    c = c.lstrip("#")
    return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _value_noise(rng, h, w, cells_y, cells_x):
    """Bilinear-upsampled value noise in [0,1] of shape (h, w)."""
    gy = cells_y + 1
    gx = cells_x + 1
    grid = rng.random((gy, gx)).astype(np.float32)
    ys = np.linspace(0.0, cells_y, h, dtype=np.float32)
    xs = np.linspace(0.0, cells_x, w, dtype=np.float32)
    y0 = np.floor(ys).astype(np.int32)
    x0 = np.floor(xs).astype(np.int32)
    fy = (ys - y0)[:, None]
    fx = (xs - x0)[None, :]
    fy = fy * fy * (3.0 - 2.0 * fy)
    fx = fx * fx * (3.0 - 2.0 * fx)
    y1 = np.minimum(y0 + 1, cells_y)
    x1 = np.minimum(x0 + 1, cells_x)
    g00 = grid[y0][:, x0]
    g01 = grid[y0][:, x1]
    g10 = grid[y1][:, x0]
    g11 = grid[y1][:, x1]
    top = g00 + (g01 - g00) * fx
    bot = g10 + (g11 - g10) * fx
    return top + (bot - top) * fy


def _fbm(rng, h, w, base_cells, octaves, persistence=0.5, lacunarity=2.0):
    """Multi-octave fBm noise normalized to ~[0,1]."""
    total = np.zeros((h, w), dtype=np.float32)
    amp = 1.0
    norm = 0.0
    cy = base_cells
    cx = max(1, int(round(base_cells * w / max(h, 1))))
    for _ in range(octaves):
        total += amp * _value_noise(rng, h, w, max(1, cy), max(1, cx))
        norm += amp
        amp *= persistence
        cy = int(round(cy * lacunarity))
        cx = int(round(cx * lacunarity))
    return total / norm


def _vertical_gradient(h, w, stops):
    """stops: list of (t, hexcolor). Returns float32 (h,w,3) in 0..255."""
    t = np.linspace(0.0, 1.0, h, dtype=np.float32)
    cols = np.zeros((h, 3), dtype=np.float32)
    ts = [s[0] for s in stops]
    cs = [_hex(s[1]) for s in stops]
    for i in range(len(stops) - 1):
        t0, t1 = ts[i], ts[i + 1]
        mask = (t >= t0) & (t <= t1)
        if not np.any(mask):
            continue
        local = (t[mask] - t0) / (t1 - t0 + 1e-9)
        local = local[:, None]
        cols[mask] = _lerp(cs[i][None, :], cs[i + 1][None, :], local)
    cols[t < ts[0]] = cs[0]
    cols[t > ts[-1]] = cs[-1]
    return np.broadcast_to(cols[:, None, :], (h, w, 3)).copy()


# ---------------------------------------------------------------------------
# sunny sky
# ---------------------------------------------------------------------------

def make_sunny_sky_panorama(w: int = 4096, h: int = 2048) -> Image.Image:
    rng = np.random.default_rng(20240517)

    horizon = 0.56
    y = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]  # (h,1)
    x = np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]  # (1,w)

    # ---- base sky gradient (upper) -------------------------------------
    sky_stops = [
        (0.00, "#1F6BE0"),
        (0.18, "#2E7DEA"),
        (0.34, "#53A5FA"),
        (0.46, "#8FC4FB"),
        (0.52, "#C4E2FF"),
        (0.56, "#D8EEFF"),
        (0.60, "#FFF6E8"),
    ]
    sky = _vertical_gradient(h, w, sky_stops)

    # ---- ocean / mist (lower) ------------------------------------------
    ocean_stops = [
        (0.56, "#FFF6E8"),
        (0.60, "#C9DFF0"),
        (0.68, "#9FCBE6"),
        (0.78, "#7FB8DC"),
        (0.90, "#6FA9CF"),
        (1.00, "#5E97BE"),
    ]
    ocean = _vertical_gradient(h, w, ocean_stops)

    # blend upper/lower around horizon -> broadcast (h,1) to (h,w,1)
    blend = _smoothstep(0.545, 0.585, y)[..., None]
    img = sky * (1.0 - blend) + ocean * blend

    # ---- sun halo -------------------------------------------------------
    sun_x, sun_y = 0.62, 0.24
    dx = (x - sun_x) * (w / h)
    dy = (y - sun_y)
    dist = np.sqrt(dx * dx + dy * dy)  # (h,w)
    halo = np.exp(-(dist / 0.16) ** 2).astype(np.float32)
    halo_core = np.exp(-(dist / 0.045) ** 2).astype(np.float32)
    sun_col = _hex("#FFF4D2")
    core_col = _hex("#FFFFFF")
    img += halo[..., None] * (sun_col - img) * 0.55
    img += halo_core[..., None] * (core_col - img) * 0.85

    # ---- clouds ---------------------------------------------------------
    band = _smoothstep(0.02, 0.24, y) * (1.0 - _smoothstep(0.36, 0.54, y))

    n1 = _fbm(rng, h, w, base_cells=6, octaves=5, persistence=0.55)
    n2 = _fbm(rng, h, w, base_cells=14, octaves=4, persistence=0.5)
    n3 = _fbm(rng, h, w, base_cells=30, octaves=3, persistence=0.5)

    cloud_field = 0.55 * n1 + 0.30 * n2 + 0.15 * n3
    cloud_field = cloud_field * (0.45 + 0.65 * band) - (1.0 - band) * 0.18

    thr = 0.52
    density = _smoothstep(thr - 0.08, thr + 0.11, cloud_field) * band

    shift = max(1, h // 200)
    below = np.roll(density, shift, axis=0)
    topness = np.clip(density - below + 0.5, 0.0, 1.0)

    sun_side = np.exp(-(((x - sun_x) * 1.6) ** 2 + ((y - sun_y) * 1.2) ** 2))
    topness = np.clip(topness + 0.35 * sun_side, 0.0, 1.0)

    white = _hex("#FFFFFF")
    belly = _hex("#DCE8F8")
    cloud_col = _lerp(belly[None, None, :], white[None, None, :], topness[..., None])

    above = (y < horizon).astype(np.float32)
    a = (density * above)[..., None]
    img = img * (1.0 - a) + cloud_col * a

    # ---- ocean shimmer --------------------------------------------------
    lower_mask = _smoothstep(0.58, 0.62, y)
    shimmer = _fbm(rng, h, w, base_cells=40, octaves=3, persistence=0.5)
    streak = 0.5 + 0.5 * np.sin((y * 220.0) + shimmer * 6.0)
    streak = streak.astype(np.float32)
    glint = (streak * lower_mask * 0.10)[..., None]
    img = img + glint * (np.array([255, 250, 235], dtype=np.float32) - img)

    # distant golden coastline hint near horizon
    coast = np.exp(-((y - 0.585) / 0.012) ** 2).astype(np.float32)  # (h,1)
    coast = coast * (0.35 + 0.65 * _fbm(rng, h, w, base_cells=8, octaves=3))
    coast_col = _hex("#F3D9A8")
    img = img + (coast[..., None] * 0.35) * (coast_col - img)

    # ---- final tone / clamp --------------------------------------------
    img = np.clip(img, 0.0, 255.0)
    img = np.clip(img * 1.02, 0.0, 255.0)

    return Image.fromarray(img.astype(np.uint8), "RGB")


# ---------------------------------------------------------------------------
# rainy sky
# ---------------------------------------------------------------------------

def make_rainy_sky_panorama(w: int = 2048, h: int = 1024) -> Image.Image:
    rng = np.random.default_rng(19870214)

    y = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    x = np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]

    stops = [
        (0.00, "#2F4257"),
        (0.30, "#3C5168"),
        (0.55, "#4C6379"),
        (0.78, "#5E748C"),
        (1.00, "#6E849A"),
    ]
    img = _vertical_gradient(h, w, stops)

    n1 = _fbm(rng, h, w, base_cells=5, octaves=5, persistence=0.55)
    n2 = _fbm(rng, h, w, base_cells=12, octaves=4, persistence=0.5)
    n3 = _fbm(rng, h, w, base_cells=28, octaves=3, persistence=0.5)
    field = 0.5 * n1 + 0.32 * n2 + 0.18 * n3

    band = _smoothstep(0.02, 0.12, y) * (1.0 - _smoothstep(0.72, 0.95, y))
    field = field * band

    density = _smoothstep(0.42, 0.72, field)

    dark = _hex("#26374A")
    light = _hex("#7C90A6")
    shift = max(1, h // 160)
    below = np.roll(density, shift, axis=0)
    topness = np.clip(density - below + 0.5, 0.0, 1.0)
    cloud_col = _lerp(dark[None, None, :], light[None, None, :], topness[..., None])

    a = (density * 0.85)[..., None]
    img = img * (1.0 - a) + cloud_col * a

    mist = _smoothstep(0.75, 1.0, y) * 0.25
    mist_col = _hex("#8FA3B8")
    img = img * (1.0 - mist[..., None]) + mist_col * mist[..., None]

    streak = 0.5 + 0.5 * np.sin((x * 900.0) + (y * 40.0) + n3 * 8.0)
    streak = (streak ** 6).astype(np.float32)
    rain = streak * 0.06
    img = img + rain[..., None] * (np.array([200, 215, 230], dtype=np.float32) - img)

    img = np.clip(img, 0.0, 255.0)
    return Image.fromarray(img.astype(np.uint8), "RGB")


if __name__ == "__main__":
    import time

    t0 = time.time()
    a = make_sunny_sky_panorama()
    t1 = time.time()
    b = make_rainy_sky_panorama()
    t2 = time.time()
    print(f"sunny {a.size} in {t1 - t0:.2f}s")
    print(f"rainy {b.size} in {t2 - t1:.2f}s")
