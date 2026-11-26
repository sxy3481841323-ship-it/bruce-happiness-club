# scripts/penthouse_kit/tex_cafe_coastal.py
"""
Malibu Private Coastal Roastery (OUT·01) — coastal backdrop textures.

Two generators:
  * make_malibu_coastal_panorama  — razor-sharp 4K coastal panorama (no blur on final)
  * make_coastal_wave_photo_tex   — framed silver-gelatin wave photograph

Pure NumPy + PIL. No GaussianBlur on the final panorama.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

# ----------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------

def _hex(c: str) -> np.ndarray:
    c = c.lstrip("#")
    return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def _lerp(a, b, t):
    return a + (b - a) * t


def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-12), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _value_noise(h: int, w: int, cells: int, seed: int) -> np.ndarray:
    """Bilinear value noise in [0,1], shape (h,w)."""
    rng = np.random.default_rng(seed)
    gh, gw = cells + 2, cells + 2
    grid = rng.random((gh, gw))
    ys = np.linspace(0, cells, h, endpoint=False)
    xs = np.linspace(0, cells, w, endpoint=False)
    y0 = np.floor(ys).astype(np.int64)
    x0 = np.floor(xs).astype(np.int64)
    fy = (ys - y0)[:, None]
    fx = (xs - x0)[None, :]
    fy = fy * fy * (3 - 2 * fy)
    fx = fx * fx * (3 - 2 * fx)
    g00 = grid[y0][:, x0]
    g10 = grid[y0 + 1][:, x0]
    g01 = grid[y0][:, x0 + 1]
    g11 = grid[y0 + 1][:, x0 + 1]
    top = g00 + (g01 - g00) * fx
    bot = g10 + (g11 - g10) * fx
    return top + (bot - top) * fy


def _fbm(h: int, w: int, base_cells: int, octaves: int, seed: int) -> np.ndarray:
    out = np.zeros((h, w), dtype=np.float64)
    amp = 1.0
    tot = 0.0
    cells = base_cells
    for o in range(octaves):
        out += amp * _value_noise(h, w, cells, seed + o * 977)
        tot += amp
        amp *= 0.5
        cells = max(2, cells * 2)
    return out / tot


def _add_detail(img: np.ndarray, amount: float, seed: int) -> None:
    """Add crisp high-frequency detail so the image is never flat/blurry."""
    h, w = img.shape[:2]
    # fine per-pixel grain
    rng = np.random.default_rng(seed)
    grain = (rng.random((h, w, 1)) - 0.5) * amount
    img += grain
    # crisp high-frequency noise (per-pixel checker-ish) for edge energy
    hf = _value_noise(h, w, max(64, w // 4), seed + 1) - 0.5
    img += hf[..., None] * (amount * 1.5)


# ----------------------------------------------------------------------------
# 1) MALIBU COASTAL PANORAMA
# ----------------------------------------------------------------------------

def _paint_sky(img: np.ndarray, w: int, h: int, horizon_v: float) -> None:
    """Cobalt -> cerulean -> warm horizon gradient, plus crisp cumulus."""
    top = _hex("#1A519A")
    mid = _hex("#5998DC")
    warm = _hex("#EEF3F7")

    v = np.linspace(0.0, 1.0, h)[:, None]
    vv = np.repeat(v, w, axis=1)
    t = np.clip(vv / horizon_v, 0.0, 1.0)

    t1 = np.clip(t / 0.55, 0.0, 1.0)
    t2 = np.clip((t - 0.55) / 0.45, 0.0, 1.0)
    col = np.empty((h, w, 3), dtype=np.float64)
    for c in range(3):
        col[..., c] = _lerp(_lerp(top[c], mid[c], t1), warm[c], t2)

    img[:] = col

    # ---- crisp cumulus clouds -------------------------------------------
    cloud_mask = np.zeros((h, w), dtype=np.float64)
    cloud_shade = np.zeros((h, w), dtype=np.float64)

    rng = np.random.default_rng(2024)
    n_clusters = 26
    for _ in range(n_clusters):
        cu = rng.uniform(0.02, 0.98)
        cv = rng.uniform(0.06, horizon_v * 0.92)
        scale = rng.uniform(0.035, 0.11)
        n_puffs = rng.integers(6, 14)
        for _p in range(n_puffs):
            pu = cu + rng.normal(0, scale * 0.9)
            pv = cv + rng.normal(0, scale * 0.45)
            pr = scale * rng.uniform(0.35, 0.85)
            cx = pu * w
            cy = pv * h
            rx = pr * w
            ry = pr * w
            x0 = int(max(0, cx - rx - 2))
            x1 = int(min(w, cx + rx + 3))
            y0 = int(max(0, cy - ry - 2))
            y1 = int(min(h, cy + ry + 3))
            if x1 <= x0 or y1 <= y0:
                continue
            yy, xx = np.mgrid[y0:y1, x0:x1]
            d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
            puff = np.clip(1.0 - d, 0.0, 1.0)
            puff = puff ** 0.55
            belly = np.clip((yy - (cy - ry * 0.15)) / (ry * 1.15), 0.0, 1.0)
            region = cloud_mask[y0:y1, x0:x1]
            cloud_mask[y0:y1, x0:x1] = np.maximum(region, puff)
            sh = cloud_shade[y0:y1, x0:x1]
            cloud_shade[y0:y1, x0:x1] = np.maximum(sh, puff * belly)

    m = _smoothstep(0.28, 0.62, cloud_mask)
    m = m * _smoothstep(0.30, 0.55, cloud_mask)

    sunny = _hex("#FFFFFF")
    belly_col = _hex("#B9C6D6")
    shade = np.clip(cloud_shade * 1.15, 0.0, 1.0)

    for c in range(3):
        cloud_col = _lerp(sunny[c], belly_col[c], shade)
        img[..., c] = _lerp(img[..., c], cloud_col, m)

    rim = _smoothstep(0.55, 0.75, cloud_mask) * (1.0 - _smoothstep(0.75, 0.95, cloud_mask))
    img += rim[..., None] * 6.0


def _paint_sea(img: np.ndarray, w: int, h: int, horizon_v: float, beach_v: float) -> None:
    """Multi-band crystal Pacific sea with crisp wavelets and foam lines."""
    y0 = int(horizon_v * h)
    y1 = int(beach_v * h)
    if y1 <= y0:
        return

    deep = _hex("#0E3A6B")
    sapphire = _hex("#1C5C97")
    turq = _hex("#3FB6C4")
    shallow = _hex("#8FE0D8")

    band = img[y0:y1]
    bh = band.shape[0]
    v = np.linspace(0.0, 1.0, bh)[:, None]
    vv = np.repeat(v, w, axis=1)

    t = vv
    t1 = np.clip(t / 0.45, 0.0, 1.0)
    t2 = np.clip((t - 0.45) / 0.35, 0.0, 1.0)
    t3 = np.clip((t - 0.80) / 0.20, 0.0, 1.0)
    col = np.empty((bh, w, 3), dtype=np.float64)
    for c in range(3):
        a = _lerp(deep[c], sapphire[c], t1)
        b = _lerp(a, turq[c], t2)
        col[..., c] = _lerp(b, shallow[c], t3)

    # crisp specular wavelets
    wav = _fbm(bh, w, 48, 4, 71)
    wav2 = _fbm(bh, w, 160, 3, 133)
    spec = _smoothstep(0.62, 0.78, wav * 0.6 + wav2 * 0.4)
    spec *= _smoothstep(0.02, 0.25, vv)
    col += spec[..., None] * np.array([70.0, 80.0, 85.0])

    trough = _smoothstep(0.30, 0.18, wav2)
    col -= trough[..., None] * np.array([10.0, 14.0, 16.0])

    img[y0:y1] = np.clip(col, 0, 255)

    # ---- two crisp lacy surf foam lines near beach_v --------------------
    foam = _hex("#F4FAFF")
    for k, off in enumerate((0.012, 0.028)):
        fy = int((beach_v - off) * h)
        if fy <= y0 or fy >= y1:
            continue
        thick = max(3, int(h * 0.004))
        yy = np.arange(fy - thick, fy + thick + 1)
        yy = yy[(yy >= y0) & (yy < y1)]
        if yy.size == 0:
            continue
        lace = _value_noise(1, w, 220, 900 + k)
        lace = _smoothstep(0.35, 0.75, lace[0])
        for y in yy:
            dist = abs(y - fy) / (thick + 1e-6)
            a = np.clip(1.0 - dist, 0.0, 1.0) ** 1.4
            a = a * lace
            row = img[y]
            for c in range(3):
                row[:, c] = _lerp(row[:, c], foam[c], a * 0.92)
            img[y] = row


def _paint_beach(img: np.ndarray, w: int, h: int, beach_v: float) -> None:
    y0 = int(beach_v * h)
    if y0 >= h:
        return
    sand = _hex("#E8DCC0")
    sand_dk = _hex("#C9B896")
    wet = _hex("#B9A98A")

    band = img[y0:]
    bh = band.shape[0]
    v = np.linspace(0.0, 1.0, bh)[:, None]
    vv = np.repeat(v, w, axis=1)

    wet_t = _smoothstep(0.0, 0.10, vv)
    col = np.empty((bh, w, 3), dtype=np.float64)
    for c in range(3):
        col[..., c] = _lerp(wet[c], sand[c], wet_t)

    tex = _fbm(bh, w, 90, 3, 555)
    col -= (tex[..., None] - 0.5) * 14.0
    patch = _smoothstep(0.55, 0.75, _fbm(bh, w, 24, 3, 808))
    for c in range(3):
        col[..., c] = _lerp(col[..., c], sand_dk[c], patch * 0.35)

    img[y0:] = np.clip(col, 0, 255)


def _paint_coastline(img: np.ndarray, w: int, h: int) -> None:
    """Sunlit sandstone bluff + cypress/palm silhouettes, u in [0,0.28]."""
    u0, u1 = 0.0, 0.28
    v0, v1 = 0.46, 0.72
    x0, x1 = int(u0 * w), int(u1 * w)
    y0, y1 = int(v0 * h), int(v1 * h)
    if x1 <= x0 or y1 <= y0:
        return

    bw, bh = x1 - x0, y1 - y0
    yy, xx = np.mgrid[0:bh, 0:bw]
    u = xx / max(1, bw - 1)
    v = yy / max(1, bh - 1)

    ridge = 0.18 + 0.55 * (1.0 - u) ** 1.3
    ridge += 0.06 * np.sin(u * 9.0) + 0.03 * np.sin(u * 23.0 + 1.3)
    inside = v > ridge

    facet = _fbm(bh, bw, 18, 4, 4242)
    facet2 = _fbm(bh, bw, 60, 3, 9191)
    lit = _smoothstep(0.35, 0.75, facet * 0.7 + facet2 * 0.3)

    rock_hi = _hex("#E4C79A")
    rock_mid = _hex("#C79A6B")
    rock_dk = _hex("#8A6440")
    col = np.empty((bh, bw, 3), dtype=np.float64)
    for c in range(3):
        a = _lerp(rock_dk[c], rock_mid[c], lit)
        col[..., c] = _lerp(a, rock_hi[c], _smoothstep(0.55, 0.9, lit))

    gx = np.abs(np.gradient(facet, axis=1))
    gy = np.abs(np.gradient(facet, axis=0))
    edge = _smoothstep(0.02, 0.06, gx + gy)
    col -= edge[..., None] * 22.0

    region = img[y0:y1, x0:x1]
    m = inside.astype(np.float64)
    for c in range(3):
        region[..., c] = _lerp(region[..., c], col[..., c], m)

    rng = np.random.default_rng(31337)
    olive = _hex("#2E3A22")
    olive_hi = _hex("#4A5A32")

    n_cyp = 9
    for i in range(n_cyp):
        cu = rng.uniform(0.05, 0.85)
        base_v = 0.18 + 0.55 * (1.0 - cu) ** 1.3
        cx = cu * bw
        cy = base_v * bh
        cw = rng.uniform(0.012, 0.028) * bw
        ch = rng.uniform(0.10, 0.22) * bh
        for _p in range(10):
            px = cx + rng.normal(0, cw * 0.5)
            py = cy - rng.uniform(0.0, ch)
            pr = cw * rng.uniform(0.35, 0.75)
            xa = int(max(0, px - pr - 1)); xb = int(min(bw, px + pr + 2))
            ya = int(max(0, py - pr - 1)); yb = int(min(bh, py + pr + 2))
            if xb <= xa or yb <= ya:
                continue
            syy, sxx = np.mgrid[ya:yb, xa:xb]
            d = np.sqrt((sxx - px) ** 2 + (syy - py) ** 2) / (pr + 1e-6)
            a = np.clip(1.0 - d, 0.0, 1.0) ** 0.5
            a = _smoothstep(0.15, 0.55, a)
            sub = region[ya:yb, xa:xb]
            for c in range(3):
                sub[..., c] = _lerp(sub[..., c], olive[c], a * 0.95)
            hi = a * _smoothstep(0.0, 0.4, (px - sxx) / (pr + 1e-6))
            for c in range(3):
                sub[..., c] = _lerp(sub[..., c], olive_hi[c], hi * 0.35)

    n_palm = 4
    for i in range(n_palm):
        pu = rng.uniform(0.10, 0.80)
        base_v = 0.18 + 0.55 * (1.0 - pu) ** 1.3
        px = pu * bw
        py = base_v * bh
        th = rng.uniform(0.10, 0.18) * bh
        tw = max(1, int(bw * 0.004))
        xa = int(max(0, px - tw)); xb = int(min(bw, px + tw + 1))
        ya = int(max(0, py - th)); yb = int(min(bh, py + 1))
        if xb > xa and yb > ya:
            region[ya:yb, xa:xb] = _lerp(region[ya:yb, xa:xb], olive, 0.9)
        top_y = py - th
        for f in range(9):
            ang = np.pi * (0.15 + 0.7 * f / 8.0) + rng.normal(0, 0.05)
            flen = rng.uniform(0.05, 0.10) * bh
            steps = int(flen)
            for s in range(steps):
                fx = px + np.cos(ang) * s * 1.4
                fy = top_y - np.sin(ang) * s * 0.6 + s * 0.25
                ix = int(fx); iy = int(fy)
                if 0 <= ix < bw and 0 <= iy < bh:
                    region[iy, ix] = _lerp(region[iy, ix], olive, 0.85)

    img[y0:y1, x0:x1] = region


def _draw_sloop(img: np.ndarray, w: int, h: int, cu: float, cv: float, scale: float) -> None:
    """Delicate sharp-edged wooden sloop with tall white sails + reflection."""
    cx = cu * w
    cy = cv * h
    s = scale * h

    hull_len = s * 0.55
    hull_h = s * 0.06
    mast_h = s * 1.05

    y0 = int(cy - s * 0.1)
    y1 = int(cy + s * 0.9)
    x0 = int(cx - hull_len)
    x1 = int(cx + hull_len)
    y0c = max(0, y0); y1c = min(h, y1)
    x0c = max(0, x0); x1c = min(w, x1)
    if y1c > y0c and x1c > x0c:
        src = img[y0c:y1c, x0c:x1c].copy()
        flipped = src[::-1]
        for r in range(flipped.shape[0]):
            shift = int(3 * np.sin(r * 0.35))
            flipped[r] = np.roll(flipped[r], shift, axis=0)
        dst = img[y0c:y1c, x0c:x1c]
        a = 0.28 * np.linspace(1.0, 0.0, flipped.shape[0])[:, None, None]
        img[y0c:y1c, x0c:x1c] = dst * (1 - a) + flipped * a

    hull_col = _hex("#5A3A22")
    hull_hi = _hex("#8A5A34")
    hy = cy
    hx0 = cx - hull_len * 0.5
    hx1 = cx + hull_len * 0.5
    for i in range(int(hull_h) + 1):
        yy = int(hy + i)
        if yy < 0 or yy >= h:
            continue
        frac = i / max(1.0, hull_h)
        xa = int(hx0 + frac * hull_len * 0.12)
        xb = int(hx1 - frac * hull_len * 0.12)
        xa = max(0, xa); xb = min(w, xb)
        if xb <= xa:
            continue
        img[yy, xa:xb] = _lerp(hull_col, hull_hi, 1.0 - frac)

    mast_x = int(cx)
    mast_top = int(cy - mast_h)
    mast_bot = int(cy)
    if 0 <= mast_x < w:
        ya = max(0, mast_top); yb = min(h, mast_bot)
        img[ya:yb, mast_x] = _hex("#3A2A1A")

    sail = _hex("#F7F5EF")
    sail_shade = _hex("#D8D4C8")

    boom_x = int(cx + hull_len * 0.42)
    boom_y = int(cy - hull_h * 0.4)
    tri = [(mast_x, mast_top), (boom_x, boom_y), (mast_x, mast_bot)]
    _fill_triangle(img, tri, sail, sail_shade, w, h)

    bow_x = int(cx - hull_len * 0.48)
    bow_y = int(cy - hull_h * 0.2)
    tri2 = [(mast_x, mast_top), (bow_x, bow_y), (mast_x, int(cy - mast_h * 0.15))]
    _fill_triangle(img, tri2, sail, sail_shade, w, h)


def _fill_triangle(img, pts, col_a, col_b, w, h):
    (x0, y0), (x1, y1), (x2, y2) = pts
    minx = max(0, min(x0, x1, x2)); maxx = min(w - 1, max(x0, x1, x2))
    miny = max(0, min(y0, y1, y2)); maxy = min(h - 1, max(y0, y1, y2))
    if maxx <= minx or maxy <= miny:
        return
    yy, xx = np.mgrid[miny:maxy + 1, minx:maxx + 1]

    def sign(ax, ay, bx, by, px, py):
        return (px - bx) * (ay - by) - (ax - bx) * (py - by)

    d1 = sign(x0, y0, x1, y1, xx, yy)
    d2 = sign(x1, y1, x2, y2, xx, yy)
    d3 = sign(x2, y2, x0, y0, xx, yy)
    has_neg = (d1 < 0) | (d2 < 0) | (d3 < 0)
    has_pos = (d1 > 0) | (d2 > 0) | (d3 > 0)
    inside = ~(has_neg & has_pos)

    t = np.clip((xx - minx) / max(1, (maxx - minx)), 0.0, 1.0)
    sub = img[miny:maxy + 1, minx:maxx + 1]
    for c in range(3):
        shade = _lerp(col_a[c], col_b[c], t)
        sub[..., c] = np.where(inside, shade, sub[..., c])
    img[miny:maxy + 1, minx:maxx + 1] = sub


def make_malibu_coastal_panorama(w: int = 4096, h: int = 2048) -> Image.Image:
    """Razor-sharp 4K Malibu coastal panorama. No GaussianBlur on final."""
    horizon_v = 0.56
    beach_v = 0.78

    img = np.zeros((h, w, 3), dtype=np.float64)

    _paint_sky(img, w, h, horizon_v)
    _paint_sea(img, w, h, horizon_v, beach_v)
    _paint_beach(img, w, h, beach_v)
    _paint_coastline(img, w, h)

    _draw_sloop(img, w, h, cu=0.42, cv=0.575, scale=0.055)
    _draw_sloop(img, w, h, cu=0.62, cv=0.578, scale=0.048)

    # crisp high-frequency detail pass (no blur) — ensures sharpness
    _add_detail(img, amount=6.0, seed=424242)

    out = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(out, mode="RGB")


# ----------------------------------------------------------------------------
# 2) FRAMED SILVER-GELATIN WAVE PHOTOGRAPH
# ----------------------------------------------------------------------------

def make_coastal_wave_photo_tex(size: int = 1024) -> Image.Image:
    """Museum-matted silver-gelatin archival wave photograph."""
    S = size
    canvas = Image.new("RGB", (S, S), (244, 240, 232))
    draw = ImageDraw.Draw(canvas)

    inner = int(S * 0.20)

    border_col = (58, 46, 38)
    draw.rectangle(
        [inner - 3, inner - 3, S - inner + 2, S - inner + 2],
        outline=border_col, width=max(2, S // 340),
    )

    pw = S - 2 * inner
    ph = S - 2 * inner
    if pw <= 4 or ph <= 4:
        return canvas

    yy, xx = np.mgrid[0:ph, 0:pw].astype(np.float64)
    u = xx / max(1, pw - 1)
    v = yy / max(1, ph - 1)

    dark = _hex("#1E2124")
    mid = _hex("#6E7378")
    light = _hex("#F2EFE9")

    cx, cy = 0.30, 1.05
    r = 0.95
    d = np.sqrt((u - cx) ** 2 + (v - cy) ** 2)
    arc = np.exp(-((d - r) ** 2) / (2 * 0.045 ** 2))

    body = _smoothstep(0.0, 0.9, v)
    tone = np.empty((ph, pw, 3), dtype=np.float64)
    for c in range(3):
        tone[..., c] = _lerp(dark[c], mid[c], body)

    lace = _fbm(ph, pw, 40, 4, 1234)
    lace2 = _fbm(ph, pw, 140, 3, 5678)
    foam = arc * _smoothstep(0.35, 0.75, lace * 0.6 + lace2 * 0.4)
    foam = np.clip(foam * 1.6, 0.0, 1.0)

    rng = np.random.default_rng(99)
    flecks = (rng.random((ph, pw)) > 0.9965).astype(np.float64)
    flecks = np.clip(flecks + foam * 0.4, 0.0, 1.0)

    for c in range(3):
        tone[..., c] = _lerp(tone[..., c], light[c], foam)
        tone[..., c] = _lerp(tone[..., c], light[c], flecks * 0.9)

    wash = _smoothstep(0.72, 1.0, v) * _smoothstep(0.3, 0.7, lace2)
    for c in range(3):
        tone[..., c] = _lerp(tone[..., c], light[c], wash * 0.85)

    tone = np.clip(tone, 0, 255)
    tone = 255.0 * _smoothstep(0.0, 1.0, tone / 255.0) * 0.5 + tone * 0.5

    grain = rng.normal(0.0, 7.0, (ph, pw, 1))
    tone = np.clip(tone + grain, 0, 255)

    vx = (u - 0.5) * 2.0
    vy = (v - 0.5) * 2.0
    vig = 1.0 - 0.18 * np.clip(vx ** 2 + vy ** 2, 0.0, 1.0)
    tone *= vig[..., None]

    plate = Image.fromarray(tone.astype(np.uint8), mode="RGB")
    canvas.paste(plate, (inner, inner))

    draw.rectangle(
        [inner - 1, inner - 1, S - inner, S - inner],
        outline=(30, 33, 36), width=1,
    )

    return canvas


if __name__ == "__main__":
    pano = make_malibu_coastal_panorama(2048, 1024)
    pano.save("/tmp/malibu_coastal_panorama.png")
    photo = make_coastal_wave_photo_tex(1024)
    photo.save("/tmp/coastal_wave_photo.png")
    print("wrote /tmp/malibu_coastal_panorama.png and /tmp/coastal_wave_photo.png")
