"""Procedural PBR textures for the AD100 penthouse kit.

All generators are seamless (tileable) and use fast vectorised NumPy + PIL.
Each function returns an RGB ``PIL.Image`` of the requested square size.
"""

from __future__ import annotations

import numpy as np
from PIL import Image

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _fbm(size: int, octaves: int, base: float, seed: int,
         persistence: float = 0.5) -> np.ndarray:
    """Seamless fractal value-noise in [0,1] built from tiled random grids."""
    rng = _rng(seed)
    out = np.zeros((size, size), dtype=np.float32)
    amp = 1.0
    total = 0.0
    for o in range(octaves):
        cells = max(2, int(round(base * (2 ** o))))
        grid = rng.random((cells, cells)).astype(np.float32)
        # tile to size+1 then bilinear sample -> seamless
        ys = np.linspace(0, cells, size, endpoint=False, dtype=np.float32)
        xs = np.linspace(0, cells, size, endpoint=False, dtype=np.float32)
        y0 = np.floor(ys).astype(np.int32)
        x0 = np.floor(xs).astype(np.int32)
        fy = (ys - y0)[:, None]
        fx = (xs - x0)[None, :]
        # smoothstep
        fy = fy * fy * (3 - 2 * fy)
        fx = fx * fx * (3 - 2 * fx)
        y1 = (y0 + 1) % cells
        x1 = (x0 + 1) % cells
        g00 = grid[np.ix_(y0, x0)]
        g01 = grid[np.ix_(y0, x1)]
        g10 = grid[np.ix_(y1, x0)]
        g11 = grid[np.ix_(y1, x1)]
        top = g00 * (1 - fx) + g01 * fx
        bot = g10 * (1 - fx) + g11 * fx
        out += amp * (top * (1 - fy) + bot * fy)
        total += amp
        amp *= persistence
    out /= total
    return out


def _smoothstep(e0: float, e1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _hex(c: str) -> np.ndarray:
    c = c.lstrip("#")
    return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def _mix(a: np.ndarray, b: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Blend two RGB colours (arrays of shape (3,)) by scalar field t (H,W)."""
    t = t[..., None]
    return a * (1 - t) + b * t


def _to_img(rgb: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")


def _coords(size: int):
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    return y, x


# ---------------------------------------------------------------------------
# 1. herringbone oak parquet
# ---------------------------------------------------------------------------


def make_herringbone_oak_tex(size: int = 2048) -> Image.Image:
    y, x = _coords(size)
    # plank geometry: herringbone with plank length L, width W
    L = size / 8.0
    W = L / 3.0
    # rotate into herringbone lattice
    u = (x + y) / np.sqrt(2.0)
    v = (x - y) / np.sqrt(2.0)
    # two interleaved plank orientations
    pu = np.mod(u, L)
    pv = np.mod(v, W)
    # which diagonal band
    band = np.floor(u / L) + np.floor(v / W)
    alt = np.mod(band, 2.0)

    # plank id for per-plank colour variation
    pid_u = np.floor(u / L)
    pid_v = np.floor(v / W)
    plank_id = (pid_u * 7.0 + pid_v * 13.0 + alt * 3.0)
    rng = _rng(11)
    plank_tone = rng.random((64, 64)).astype(np.float32)
    pi = np.mod(plank_id.astype(np.int32), 64)
    pj = np.mod((pid_u.astype(np.int32) * 3 + pid_v.astype(np.int32) * 5), 64)
    tone = plank_tone[pi, pj]

    # wood grain along plank direction
    grain = _fbm(size, 5, 4.0, 21, 0.55)
    # stretch grain along u
    grain2 = _fbm(size, 4, 2.0, 22, 0.5)
    grain = 0.6 * grain + 0.4 * grain2

    # bevel: distance to plank edge
    du = np.minimum(pu, L - pu)
    dv = np.minimum(pv, W - pv)
    edge = np.minimum(du, dv)
    bevel = _smoothstep(0.0, W * 0.06, edge)

    base_light = _hex("#DEC8A8")
    base_dark = _hex("#C9A984")

    t = 0.35 * tone + 0.45 * grain + 0.2 * (1.0 - bevel)
    t = np.clip(t, 0.0, 1.0)
    rgb = _mix(base_light, base_dark, t)

    # subtle sheen highlight on bevel
    sheen = (1.0 - bevel) * 0.15
    rgb = rgb + sheen[..., None] * 20.0
    return _to_img(rgb)


# ---------------------------------------------------------------------------
# 2. calacatta marble
# ---------------------------------------------------------------------------


def make_calacatta_marble_tex(size: int = 2048) -> Image.Image:
    y, x = _coords(size)
    base = _hex("#F8F5EE")
    gray = _hex("#B9B4AC")
    gold = _hex("#C9A96A")

    # domain-warped fbm for organic veins
    warp = _fbm(size, 4, 3.0, 31, 0.55)
    warp2 = _fbm(size, 4, 3.0, 32, 0.55)
    nx = x / size + 0.35 * (warp - 0.5)
    ny = y / size + 0.35 * (warp2 - 0.5)

    # primary veins: sin of warped coordinate
    v1 = np.abs(np.sin((nx * 6.0 + ny * 2.0) * np.pi))
    v2 = np.abs(np.sin((nx * 3.0 - ny * 5.0) * np.pi + 1.3))
    vein = np.minimum(v1, v2)
    vein = 1.0 - _smoothstep(0.0, 0.06, vein)  # thin bright lines

    # secondary fine veins
    v3 = np.abs(np.sin((nx * 14.0 + ny * 9.0) * np.pi))
    fine = 1.0 - _smoothstep(0.0, 0.03, v3)

    # gold accent veins (sparse)
    gv = np.abs(np.sin((nx * 4.0 + ny * 7.0) * np.pi + 2.1))
    gold_mask = (1.0 - _smoothstep(0.0, 0.02, gv)) * _smoothstep(0.55, 0.75, warp)

    # cloudy base variation
    cloud = _fbm(size, 5, 2.0, 33, 0.5)

    rgb = base[None, None, :] * np.ones((size, size, 1), dtype=np.float32)
    rgb = rgb * (0.97 + 0.06 * cloud[..., None])

    vein_strength = np.clip(vein * 0.85 + fine * 0.35, 0.0, 1.0)
    rgb = rgb * (1 - vein_strength[..., None]) + gray[None, None, :] * vein_strength[..., None]
    rgb = rgb * (1 - gold_mask[..., None] * 0.7) + gold[None, None, :] * (gold_mask[..., None] * 0.7)
    return _to_img(rgb)


# ---------------------------------------------------------------------------
# 3. boucle fabric
# ---------------------------------------------------------------------------


def make_boucle_fabric_tex(size: int = 1024) -> Image.Image:
    y, x = _coords(size)
    base = _hex("#F4EFE5")
    shadow = _hex("#D9D0C0")

    # nubby loops: many small blobs via high-freq noise thresholded
    n1 = _fbm(size, 6, 8.0, 41, 0.6)
    n2 = _fbm(size, 6, 12.0, 42, 0.6)
    nub = np.clip((n1 * 0.6 + n2 * 0.4 - 0.35) * 3.0, 0.0, 1.0)

    # loop shading: use gradient of nub for pseudo-3d
    gy, gx = np.gradient(nub)
    shade = np.clip(0.5 + (gx + gy) * 4.0, 0.0, 1.0)

    # fine fiber grain
    fiber = _fbm(size, 5, 24.0, 43, 0.55)

    t = np.clip(0.55 * nub + 0.25 * shade + 0.2 * fiber, 0.0, 1.0)
    rgb = _mix(base, shadow, t * 0.55)
    # brighten loop tops
    rgb = rgb + (nub ** 2)[..., None] * 12.0
    return _to_img(rgb)


# ---------------------------------------------------------------------------
# 4. travertine
# ---------------------------------------------------------------------------


def make_travertine_tex(size: int = 1024) -> Image.Image:
    y, x = _coords(size)
    base = _hex("#E7DBC8")
    dark = _hex("#C9B79A")

    # horizontal strata
    strata = _fbm(size, 5, 3.0, 51, 0.55)
    # stretch horizontally: sample noise with y compressed
    yy = (y / size * 6.0)
    band = 0.5 + 0.5 * np.sin(yy * np.pi * 2.0 + strata * 6.0)
    band = _smoothstep(0.3, 0.9, band)

    # porous pits: small dark specks
    pits = _fbm(size, 6, 20.0, 52, 0.6)
    pit_mask = _smoothstep(0.62, 0.78, pits)

    # fine grain
    grain = _fbm(size, 5, 40.0, 53, 0.5)

    t = np.clip(0.35 * band + 0.35 * pit_mask + 0.3 * grain, 0.0, 1.0)
    rgb = _mix(base, dark, t * 0.6)
    return _to_img(rgb)


# ---------------------------------------------------------------------------
# 5. fluted walnut
# ---------------------------------------------------------------------------


def make_fluted_walnut_tex(size: int = 1024) -> Image.Image:
    y, x = _coords(size)
    light = _hex("#643E26")
    dark = _hex("#241309")

    # vertical flutes: sinusoidal profile across x
    n_flutes = 10
    phase = (x / size) * n_flutes * 2.0 * np.pi
    flute = 0.5 + 0.5 * np.cos(phase)  # 1 at crest, 0 at valley
    # sharpen
    flute = flute ** 1.6

    # wood grain along y
    grain = _fbm(size, 5, 4.0, 61, 0.55)
    grain2 = _fbm(size, 4, 16.0, 62, 0.5)
    grain = 0.6 * grain + 0.4 * grain2

    # per-flute tone
    fid = np.floor(x / size * n_flutes).astype(np.int32) % n_flutes
    rng = _rng(63)
    tones = rng.random(n_flutes).astype(np.float32)
    tone = tones[fid]

    t = np.clip(0.55 * (1.0 - flute) + 0.3 * grain + 0.15 * tone, 0.0, 1.0)
    rgb = _mix(light, dark, t)
    # crest highlight
    rgb = rgb + (flute ** 3)[..., None] * 18.0
    return _to_img(rgb)


# ---------------------------------------------------------------------------
# 6. plush rug (borderless raw alpaca/wool)
# ---------------------------------------------------------------------------


def make_plush_rug_tex(size: int = 2048) -> Image.Image:
    y, x = _coords(size)
    light = _hex("#EFE9DE")
    dark = _hex("#E3DACB")

    # gentle horizontal abrash (hand-loomed colour drift)
    abrash = _fbm(size, 4, 2.0, 71, 0.55)
    # stretch horizontally: use y-weighted noise
    abrash2 = _fbm(size, 3, 1.0, 72, 0.5)
    abrash = 0.6 * abrash + 0.4 * abrash2
    # horizontal banding
    band = 0.5 + 0.5 * np.sin((y / size) * np.pi * 2.0 * 3.0 + abrash * 4.0)
    band = _smoothstep(0.2, 0.8, band)

    # micro tuft fiber grain
    tuft = _fbm(size, 6, 32.0, 73, 0.6)
    tuft2 = _fbm(size, 6, 64.0, 74, 0.55)
    fiber = 0.5 * tuft + 0.5 * tuft2

    # subtle pile height variation
    pile = _fbm(size, 5, 8.0, 75, 0.55)

    t = np.clip(0.3 * band + 0.4 * fiber + 0.3 * pile, 0.0, 1.0)
    rgb = _mix(light, dark, t * 0.7)
    # soft highlight on pile tops
    rgb = rgb + (pile ** 2)[..., None] * 8.0
    return _to_img(rgb)


# ---------------------------------------------------------------------------
# 7. sheer linen
# ---------------------------------------------------------------------------


def make_sheer_linen_tex(size: int = 1024) -> Image.Image:
    y, x = _coords(size)
    base = _hex("#F5EFE4")
    shadow = _hex("#E2D8C6")

    # irregular flax slub fibers: vertical + horizontal
    vfib = _fbm(size, 5, 3.0, 81, 0.55)
    hfib = _fbm(size, 5, 3.0, 82, 0.55)
    # stretch: vertical fibers vary mostly in x
    vfib2 = _fbm(size, 4, 40.0, 83, 0.5)
    hfib2 = _fbm(size, 4, 40.0, 84, 0.5)

    # weave: alternating vertical/horizontal threads
    weave_v = 0.5 + 0.5 * np.sin((x / size) * np.pi * 2.0 * 90.0)
    weave_h = 0.5 + 0.5 * np.sin((y / size) * np.pi * 2.0 * 90.0)
    weave = 0.5 * weave_v + 0.5 * weave_h

    slub = np.clip(0.4 * vfib + 0.4 * hfib + 0.2 * (vfib2 + hfib2) * 0.5, 0.0, 1.0)
    slub = _smoothstep(0.35, 0.75, slub)

    t = np.clip(0.35 * slub + 0.35 * weave + 0.3 * (vfib2 * 0.5 + hfib2 * 0.5), 0.0, 1.0)
    rgb = _mix(base, shadow, t * 0.55)
    # translucent brightening
    rgb = rgb + (1.0 - t)[..., None] * 6.0
    return _to_img(rgb)


# ---------------------------------------------------------------------------
# 8. cognac suede / nubuck
# ---------------------------------------------------------------------------


def make_cognac_suede_tex(size: int = 1024) -> Image.Image:
    y, x = _coords(size)
    base = _hex("#9C5C34")
    dark = _hex("#6E3D20")
    light = _hex("#B87A4E")

    # velvety micro-nap: fine directional noise
    nap = _fbm(size, 6, 16.0, 91, 0.6)
    nap2 = _fbm(size, 6, 48.0, 92, 0.55)
    nap = 0.55 * nap + 0.45 * nap2

    # broad tonal variation (dye unevenness)
    broad = _fbm(size, 4, 2.0, 93, 0.55)

    # subtle directional nap streaks
    streak = _fbm(size, 4, 6.0, 94, 0.5)
    streak = 0.5 + 0.5 * np.sin((x / size) * np.pi * 2.0 * 8.0 + streak * 5.0)

    t = np.clip(0.4 * nap + 0.35 * broad + 0.25 * streak, 0.0, 1.0)

    rgb = _mix(base, dark, t * 0.6)
    # highlight nap tips
    hi = np.clip((nap - 0.55) * 2.0, 0.0, 1.0)
    rgb = rgb * (1 - hi[..., None] * 0.4) + light[None, None, :] * (hi[..., None] * 0.4)
    return _to_img(rgb)


__all__ = [
    "make_herringbone_oak_tex",
    "make_calacatta_marble_tex",
    "make_boucle_fabric_tex",
    "make_travertine_tex",
    "make_fluted_walnut_tex",
    "make_plush_rug_tex",
    "make_sheer_linen_tex",
    "make_cognac_suede_tex",
]
