"""Refined mineral-botanical quiet-luxury surface textures (NumPy + PIL)."""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter

# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def _fbm(n: int, octaves: int = 5, seed: int = 0, base: int = 4) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = np.zeros((n, n), dtype=np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        res = max(2, base * (2 ** o))
        g = rng.random((res, res)).astype(np.float32)
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
        out += amp * (np.asarray(img, dtype=np.float32) / 255.0)
        tot += amp
        amp *= 0.5
    return out / tot


def _warp(field: np.ndarray, dx: np.ndarray, dy: np.ndarray, amount: float) -> np.ndarray:
    n = field.shape[0]
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    sx = np.clip(xx + dx * amount, 0, n - 1).astype(np.int32)
    sy = np.clip(yy + dy * amount, 0, n - 1).astype(np.int32)
    return field[sy, sx]


def _mix(c0, c1, t):
    c0 = np.array(c0, dtype=np.float32)
    c1 = np.array(c1, dtype=np.float32)
    return c0 + (c1 - c0) * t[..., None]


def _to_img(rgb: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")


def _hex(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ----------------------------------------------------------------------------
# 1. marmorino boiserie
# ----------------------------------------------------------------------------

def make_marmorino_boiserie_tex(size: int = 1024) -> Image.Image:
    n = size
    cloud = _fbm(n, 5, seed=11, base=3)
    trowel = _fbm(n, 4, seed=12, base=6)
    t = np.clip(0.55 * cloud + 0.45 * trowel, 0, 1)
    rgb = _mix(_hex("#DDD5C7"), _hex("#EAE4D8"), t)
    # delicate inset panel grooves
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    m = int(n * 0.12)
    groove = np.zeros((n, n), dtype=np.float32)
    for edge in (m, n - m):
        groove += np.exp(-((xx - edge) ** 2) / 2.0)
        groove += np.exp(-((yy - edge) ** 2) / 2.0)
    groove = np.clip(groove, 0, 1)
    rgb = rgb * (1 - 0.35 * groove[..., None]) + np.array(_hex("#C3B8A6")) * (0.35 * groove[..., None])
    brass = np.clip(groove - 0.55, 0, 1) * 0.4
    rgb = rgb * (1 - brass[..., None]) + np.array(_hex("#CAB996")) * brass[..., None]
    return _to_img(rgb)


# ----------------------------------------------------------------------------
# 2. handknotted salon rug
# ----------------------------------------------------------------------------

def make_handknotted_salon_rug_tex(size: int = 2048) -> Image.Image:
    n = size
    f = _fbm(n, 6, seed=21, base=3)
    warp = _fbm(n, 4, seed=22, base=5) - 0.5
    f = _warp(f, warp, warp * 0.6, 40)
    yy = np.linspace(0, 1, n, dtype=np.float32)[:, None]
    abrash = 0.5 + 0.5 * np.sin(yy * 9.0 + f * 2.0)
    base = _mix(_hex("#E7E1D6"), _hex("#D8D1C4"), np.clip(0.5 * f + 0.5 * abrash, 0, 1))
    sage = _fbm(n, 5, seed=23, base=4)
    sage_mask = np.clip((sage - 0.55) * 2.2, 0, 1) * 0.35
    rgb = base * (1 - sage_mask[..., None]) + np.array(_hex("#C6CFC6")) * sage_mask[..., None]
    # perimeter border
    outer = int(n * 0.04)
    yy2, xx2 = np.mgrid[0:n, 0:n]
    edge = np.minimum(np.minimum(xx2, yy2), np.minimum(n - 1 - xx2, n - 1 - yy2))
    band = (edge < outer)
    rgb[band] = np.array(_hex("#7B7D72"), dtype=np.float32)
    brass = (edge >= outer - 2) & (edge < outer)
    rgb[brass] = np.array(_hex("#B59A6B"), dtype=np.float32)
    ox = (edge >= outer - 4) & (edge < outer - 2)
    rgb[ox] = np.array(_hex("#652C39"), dtype=np.float32)
    return _to_img(rgb)


# ----------------------------------------------------------------------------
# 3. loft aubusson rug
# ----------------------------------------------------------------------------

def make_loft_aubusson_rug_tex(size: int = 1024) -> Image.Image:
    n = size
    f = _fbm(n, 5, seed=31, base=4)
    cel = _fbm(n, 4, seed=32, base=6)
    t = np.clip(0.6 * f + 0.4 * cel, 0, 1)
    rgb = _mix(_hex("#E2DDD2"), _hex("#CFD5CB"), t)
    outer = int(n * 0.038)
    yy, xx = np.mgrid[0:n, 0:n]
    edge = np.minimum(np.minimum(xx, yy), np.minimum(n - 1 - xx, n - 1 - yy))
    rgb[edge < outer] = np.array(_hex("#74796F"), dtype=np.float32)
    rgb[(edge >= outer - 2) & (edge < outer)] = np.array(_hex("#B59A6B"), dtype=np.float32)
    return _to_img(rgb)


# ----------------------------------------------------------------------------
# 4. verde alpi marble
# ----------------------------------------------------------------------------

def make_verde_alpi_marble_tex(size: int = 1024) -> Image.Image:
    n = size
    base = _fbm(n, 6, seed=41, base=3)
    warp1 = _fbm(n, 5, seed=42, base=3) - 0.5
    warp2 = _fbm(n, 4, seed=44, base=5) - 0.5
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    diag = (xx * 0.72 + yy * 0.45) / n
    # Thin organic mineral quartz fractures instead of thick bright stripes
    f1 = np.abs(np.sin((diag + warp1 * 0.85) * 6.8))
    f2 = np.abs(np.sin(((xx * -0.45 + yy * 0.82) / n + warp2 * 0.75) * 9.5 + 1.1))
    veins = np.clip((1.0 - f1) ** 16 * 0.52 + (1.0 - f2) ** 20 * 0.34, 0, 0.58)
    rgb = _mix(_hex("#192821"), _hex("#2E463B"), base)
    rgb = rgb * (1 - veins[..., None]) + np.array(_hex("#D5D0C4")) * veins[..., None]
    hair = np.clip((1.0 - np.abs(np.sin((diag + warp2 * 0.9) * 13.0))) ** 22, 0, 1) * 0.28
    rgb = rgb * (1 - hair[..., None]) + np.array(_hex("#9B8459")) * hair[..., None]
    return _to_img(rgb)


# ----------------------------------------------------------------------------
# 5. rift oak
# ----------------------------------------------------------------------------

def make_rift_oak_tex(size: int = 1024) -> Image.Image:
    n = size
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    # stretched vertical grain: high x-frequency, near-zero lateral wave
    grain = np.sin(xx * 0.9 + np.sin(yy * 0.004) * 0.6)
    grain = 0.5 + 0.5 * grain
    fine = _fbm(n, 5, seed=51, base=8)
    t = np.clip(0.55 * grain + 0.45 * fine, 0, 1)
    rgb = _mix(_hex("#66513C"), _hex("#7C654E"), t)
    fleck = _fbm(n, 6, seed=52, base=16)
    fleck = np.clip((fleck - 0.78) * 5.0, 0, 1) * 0.35
    rgb = rgb * (1 - fleck[..., None]) + np.array(_hex("#8A7256")) * fleck[..., None]
    return _to_img(rgb)


# ----------------------------------------------------------------------------
# 6. celadon plaster
# ----------------------------------------------------------------------------

def make_celadon_plaster_tex(size: int = 1024) -> Image.Image:
    n = size
    f = _fbm(n, 6, seed=61, base=3)
    patina = _fbm(n, 4, seed=62, base=5)
    t = np.clip(0.6 * f + 0.4 * patina, 0, 1)
    rgb = _mix(_hex("#B4BFA9"), _hex("#C7D0C4"), t)
    return _to_img(rgb)


# ----------------------------------------------------------------------------
# 7. slate linen
# ----------------------------------------------------------------------------

def make_slate_linen_tex(size: int = 512) -> Image.Image:
    n = size
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    warp = 0.5 + 0.5 * np.sin(xx * 1.4)
    weft = 0.5 + 0.5 * np.sin(yy * 1.4)
    slub = _fbm(n, 4, seed=71, base=8)
    t = np.clip(0.35 * warp + 0.35 * weft + 0.3 * slub, 0, 1)
    rgb = _mix(_hex("#4B5C68"), _hex("#5C6F7C"), t)
    return _to_img(rgb)


# ----------------------------------------------------------------------------
# 8a. headland rock
# ----------------------------------------------------------------------------

def make_headland_rock_tex(size: int = 512) -> Image.Image:
    n = size
    f = _fbm(n, 6, seed=81, base=3)
    strata = _fbm(n, 4, seed=82, base=6)
    yy = np.linspace(0, 1, n, dtype=np.float32)[:, None]
    band = 0.5 + 0.5 * np.sin(yy * 14.0 + strata * 3.0)
    t = np.clip(0.55 * f + 0.45 * band, 0, 1)
    rgb = _mix(_hex("#7A7166"), _hex("#9D9283"), t)
    lichen = _fbm(n, 5, seed=83, base=8)
    lm = np.clip((lichen - 0.62) * 3.0, 0, 1) * 0.4
    rgb = rgb * (1 - lm[..., None]) + np.array(_hex("#676E5F")) * lm[..., None]
    return _to_img(rgb)


# ----------------------------------------------------------------------------
# 8b. coastal pine slope
# ----------------------------------------------------------------------------

def make_coastal_pine_slope_tex(size: int = 1024) -> Image.Image:
    n = size
    f = _fbm(n, 6, seed=91, base=3)
    clus = _fbm(n, 5, seed=92, base=10)
    t = np.clip(0.6 * f + 0.4 * clus, 0, 1)
    rgb = _mix(_hex("#3A4D3E"), _hex("#637760"), t)
    dapple = np.clip((clus - 0.68) * 4.0, 0, 1) * 0.35
    rgb = rgb * (1 - dapple[..., None]) + np.array(_hex("#8FA07E")) * dapple[..., None]
    yy = np.linspace(0, 1, n, dtype=np.float32)[:, None]
    base_mask = np.clip((yy - 0.82) * 6.0, 0, 1) * np.clip((f - 0.4) * 2.0, 0, 1)
    rgb = rgb * (1 - base_mask[..., None] * 0.7) + np.array(_hex("#998E7E")) * (base_mask[..., None] * 0.7)
    return _to_img(rgb)
