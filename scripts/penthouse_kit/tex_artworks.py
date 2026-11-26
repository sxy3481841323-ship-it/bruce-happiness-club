"""Authentic impasto / linen / silver-gelatin artwork textures for the penthouse kit."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

_SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
_SANS = "/System/Library/Fonts/Helvetica.ttc"


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        try:
            return ImageFont.truetype(_SANS, size)
        except Exception:
            return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Shared tactile studio helpers
# ---------------------------------------------------------------------------


def _linen_canvas(w: int, h: int, seed: int = 0) -> np.ndarray:
    """Fine crosshatch woven Belgian linen warp/weft bump & color texture (float RGB)."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    warp = 0.5 + 0.5 * np.sin(xx * (np.pi / 2.1) + rng.uniform(0, 6))
    weft = 0.5 + 0.5 * np.sin(yy * (np.pi / 2.1) + rng.uniform(0, 6))
    weave = (warp * weft) ** 1.4
    fiber = rng.normal(0, 1, (h, w)).astype(np.float32)
    fiber = np.array(Image.fromarray(((fiber * 0.5 + 0.5) * 255).astype(np.uint8))
                     .filter(ImageFilter.GaussianBlur(0.6)), dtype=np.float32) / 255.0
    bump = 0.55 * weave + 0.45 * fiber
    base = np.array([218, 208, 190], dtype=np.float32)
    tint = 0.86 + 0.14 * bump[..., None]
    return np.clip(base[None, None, :] * tint, 0, 255)


def _raking_light(height_map: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """Sobel/gradient raking light from top-left (-0.7,-0.7,1.0) -> relief shading multiplier."""
    hm = height_map.astype(np.float32)
    if hm.ndim == 3:
        hm = hm.mean(axis=2)
    hm = hm / (hm.max() + 1e-6)
    gy, gx = np.gradient(hm)
    lx, ly, lz = -0.7, -0.7, 1.0
    n = np.sqrt(gx * gx + gy * gy + 1.0)
    nx, ny, nz = -gx / n, -gy / n, 1.0 / n
    lam = np.clip(nx * lx + ny * ly + nz * lz, 0.0, None)
    shade = 0.55 + 0.45 * lam
    return np.clip(1.0 + (shade - 1.0) * strength, 0.35, 1.6)


def _museum_mat(inner: Image.Image, out_w: int, out_h: int,
                mat_color=(244, 240, 232)) -> Image.Image:
    """Crisp wide passe-partout mat with thin #322B24 shadow bevel."""
    canvas = Image.new("RGB", (out_w, out_h), mat_color)
    d = ImageDraw.Draw(canvas)
    iw, ih = inner.size
    scale = min((out_w * 0.78) / iw, (out_h * 0.78) / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    art = inner.resize((nw, nh), Image.LANCZOS)
    x, y = (out_w - nw) // 2, (out_h - nh) // 2
    d.rectangle([x - 3, y - 3, x + nw + 2, y + nh + 2], fill=(50, 43, 36))
    canvas.paste(art, (x, y))
    return canvas


def _to_img(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def _feather_bands(w: int, h: int, bands, seed: int) -> np.ndarray:
    """Stacked luminous color-field bands with feathered edges + dry-brush bristles."""
    rng = np.random.default_rng(seed)
    img = np.zeros((h, w, 3), dtype=np.float32)
    edges = np.linspace(0, h, len(bands) + 1)
    yy = np.mgrid[0:h, 0:w][0].astype(np.float32)
    for i, col in enumerate(bands):
        top, bot = edges[i], edges[i + 1]
        mask = np.clip((yy - top) / 6.0, 0, 1) * np.clip((bot - yy) / 6.0, 0, 1)
        mask = np.array(Image.fromarray((mask * 255).astype(np.uint8))
                        .filter(ImageFilter.GaussianBlur(9)), dtype=np.float32) / 255.0
        img += mask[..., None] * np.array(col, dtype=np.float32)
    bristle = rng.normal(0, 1, (h, w)).astype(np.float32)
    bristle = np.array(Image.fromarray(((bristle * 0.5 + 0.5) * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(0.4)), dtype=np.float32) / 255.0
    streak = np.sin(np.mgrid[0:h, 0:w][1] * 0.9 + rng.uniform(0, 6)) * 0.5 + 0.5
    img *= (0.94 + 0.06 * bristle)[..., None]
    img *= (0.97 + 0.03 * streak)[..., None]
    return img


# ---------------------------------------------------------------------------
# 1600x900 horizontal works
# ---------------------------------------------------------------------------


def _art_color_field(w=1600, h=900) -> Image.Image:
    bands = [(221, 208, 188), (174, 118, 70), (43, 37, 33)]
    img = _feather_bands(w, h, bands, seed=11)
    linen = _linen_canvas(w, h, seed=3)
    img = img * 0.82 + linen * 0.18
    relief = _raking_light(img, strength=1.1)
    return _to_img(img * relief[..., None])


def _art_chalk_relief(w=1600, h=900) -> Image.Image:
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = xx / w
    v = yy / h
    # Sculptural radial plaster combs & diagonal palette-knife impasto ridges
    height = (
        0.55 * np.sin(np.hypot((u - 0.34) * 1.6, v - 0.72) * 34.0) * np.exp(-(((u - 0.34) ** 2 + (v - 0.72) ** 2) / 0.18))
        + 0.45 * np.sin((u * 0.8 + v * 0.55) * 42.0) * np.exp(-(((u - 0.68) ** 2 + (v - 0.38) ** 2) / 0.16))
        + 0.25 * np.cos(u * 90.0 + np.sin(v * 14.0) * 2.0) * 0.25
    )
    height = (height - height.min()) / (height.max() - height.min() + 1e-6)
    linen = _linen_canvas(w, h, seed=17)
    base = np.array([239, 233, 222], dtype=np.float32) * 0.88 + linen * 0.12
    relief = _raking_light(height * 4.5, strength=2.6)
    img = base * relief[..., None]
    return _museum_mat(_to_img(img), w, h, mat_color=(244, 240, 232))


def _art_silver_gelatin(w=1600, h=900) -> Image.Image:
    rng = np.random.default_rng(21)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    horizon = h * 0.58
    sky = np.clip(1.0 - yy / horizon, 0, 1)
    sea = np.clip((yy - horizon) / (h - horizon), 0, 1)
    gray = np.where(yy < horizon, 200 - 60 * sky, 120 - 40 * sea)
    mist = np.exp(-((yy - horizon) ** 2) / (2 * 90.0 ** 2)) * 40
    gray = gray + mist
    grain = rng.normal(0, 9, (h, w)).astype(np.float32)
    gray = np.clip(gray + grain, 0, 255)
    img = np.stack([gray] * 3, axis=-1)
    # two sloop sails
    d = ImageDraw.Draw(_to_img(img))
    for sx, sh in ((w * 0.42, 260), (w * 0.60, 200)):
        d.polygon([(sx, horizon - sh), (sx + 90, horizon - 20), (sx, horizon - 20)],
                  fill=(238, 238, 238))
        d.line([(sx, horizon - sh), (sx, horizon + 30)], fill=(30, 30, 30), width=3)
    img = np.array(d._image if hasattr(d, "_image") else d, dtype=np.float32) if False else \
        np.array(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)), dtype=np.float32)
    return _to_img(img)


def make_tv_artworks() -> list[Image.Image]:
    return [
        _art_color_field(),
        _art_chalk_relief(),
        _museum_mat(_art_silver_gelatin(), 1600, 900),
    ]


# ---------------------------------------------------------------------------
# 800x1000 vertical works
# ---------------------------------------------------------------------------


def _work_strata(w=800, h=1000) -> Image.Image:
    rng = np.random.default_rng(31)
    cols = [(196, 168, 130), (222, 210, 190), (176, 108, 74), (150, 130, 108)]
    img = _feather_bands(w, h, [cols[i % len(cols)] for i in range(7)], seed=5)
    scraper = rng.normal(0, 1, (h, w)).astype(np.float32)
    scraper = np.array(Image.fromarray(((scraper * 0.5 + 0.5) * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(1.2)), dtype=np.float32) / 255.0
    img *= (0.9 + 0.1 * scraper)[..., None]
    relief = _raking_light(img, strength=1.0)
    return _to_img(img * relief[..., None])


def _work_horizon(w=800, h=1000) -> Image.Image:
    yy = np.mgrid[0:h, 0:w][0].astype(np.float32)
    horizon = h * 0.52
    sky = np.clip(1.0 - yy / horizon, 0, 1)
    sea = np.clip((yy - horizon) / (h - horizon), 0, 1)
    top = np.array([120, 140, 160], dtype=np.float32)
    bot = np.array([18, 26, 48], dtype=np.float32)
    img = np.where((yy < horizon)[..., None], top * (0.7 + 0.3 * sky[..., None]),
                   bot * (0.6 + 0.4 * sea[..., None]))
    d = ImageDraw.Draw(_to_img(img))
    gx = int(w * 0.62)
    d.line([(gx, int(horizon) - 2), (gx + 60, int(horizon) + 2)], fill=(220, 224, 230), width=2)
    return _to_img(np.array(d._image if hasattr(d, "_image") else d, dtype=np.float32)) \
        if False else _to_img(np.array(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))))


def _work_linen_gesture(w=800, h=1000) -> Image.Image:
    linen = _linen_canvas(w, h, seed=9)
    img = Image.fromarray(linen.astype(np.uint8))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(4)
    for _ in range(6):
        pts = [(rng.uniform(0, w), rng.uniform(0, h)) for _ in range(4)]
        d.line(pts, fill=(60, 55, 50), width=rng.integers(2, 5), joint="curve")
    for _ in range(4):
        pts = [(rng.uniform(0, w), rng.uniform(0, h)) for _ in range(3)]
        d.line(pts, fill=(235, 230, 220), width=rng.integers(3, 6), joint="curve")
    arr = np.array(img, dtype=np.float32)
    relief = _raking_light(arr, strength=0.8)
    return _to_img(arr * relief[..., None])


def _work_amber(w=800, h=1000) -> Image.Image:
    rng = np.random.default_rng(17)
    palette = [(150, 90, 50), (180, 130, 60), (110, 80, 55), (235, 220, 195)]
    img = np.zeros((h, w, 3), dtype=np.float32)
    step = 26
    for y in range(0, h, step):
        for x in range(0, w, step):
            col = palette[rng.integers(0, len(palette))]
            img[y:y + step, x:x + step] = col
    img = np.array(Image.fromarray(img.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.4)),
                   dtype=np.float32)
    relief = _raking_light(img, strength=1.2)
    return _museum_mat(_to_img(img * relief[..., None]), w, h)


def make_gallery_travel_artworks() -> list[Image.Image]:
    return [_work_strata(), _work_horizon(), _work_linen_gesture(), _work_amber()]


# ---------------------------------------------------------------------------
# Patron card
# ---------------------------------------------------------------------------


def make_patron_card_tex(w=1024, h=640) -> Image.Image:
    img = Image.new("RGB", (w, h), (29, 35, 31))
    d = ImageDraw.Draw(img)
    gold = (176, 148, 96)
    d.rectangle([32, 32, w - 32, h - 32], outline=gold, width=1)
    header = _font(_SANS, 20)
    word = _font(_SERIF, 120)
    foot = _font(_SANS, 22)
    d.text((w // 2, 120), "B E V E R L Y   H I L L S   ·   O R G A N I C   P R O V I S I O N S",
           font=header, fill=gold, anchor="mm")
    d.text((w // 2, h // 2), "ELOWEN", font=word, fill=(238, 232, 220), anchor="mm")
    d.text((w // 2, h - 120), "H O U S E   A C C O U N T   ·   N O .   0 7",
           font=foot, fill=gold, anchor="mm")
    return img


# ---------------------------------------------------------------------------
# Vinyl cover
# ---------------------------------------------------------------------------


def make_vinyl_cover_tex(size=1024) -> Image.Image:
    img = Image.new("RGB", (size, size), (34, 40, 44))
    d = ImageDraw.Draw(img)
    amber = (196, 150, 84)
    slate = (58, 68, 74)
    d.rectangle([0, int(size * 0.62), size, size], fill=slate)
    d.rectangle([int(size * 0.08), int(size * 0.08), int(size * 0.92), int(size * 0.92)],
                outline=amber, width=2)
    title = _font(_SERIF, 64)
    sub = _font(_SANS, 22)
    d.text((int(size * 0.12), int(size * 0.18)), "COOL", font=title, fill=(238, 232, 220))
    d.text((int(size * 0.12), int(size * 0.30)), "AFTERNOON", font=title, fill=(238, 232, 220))
    d.text((int(size * 0.12), int(size * 0.46)), "· 33 RPM ·", font=sub, fill=amber)
    return img
