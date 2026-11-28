"""Procedural kitchen surface textures (NumPy + PIL)."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def _fbm(size: int, octaves: int, seed: int, persistence: float = 0.5) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = np.zeros((size, size), dtype=np.float64)
    amp = 1.0
    total = 0.0
    for o in range(octaves):
        res = max(2, size >> (octaves - o))
        grid = rng.random((res + 1, res + 1))
        img = Image.fromarray((grid * 255).astype(np.uint8)).resize(
            (size, size), Image.BICUBIC
        )
        out += amp * (np.asarray(img, dtype=np.float64) / 255.0)
        total += amp
        amp *= persistence
    return out / total


def _smoothstep(e0: float, e1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def make_calacatta_viola_tex(size: int = 1024) -> Image.Image:
    base = _fbm(size, 5, 11, 0.55)
    warp = _fbm(size, 4, 23, 0.5)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float64) / size
    field = base + 0.35 * np.sin((xx * 3.0 + yy * 1.4 + warp * 2.2) * np.pi)
    field = (field - field.min()) / (field.max() - field.min())

    ivory = np.array([0xF2, 0xED, 0xE5], dtype=np.float64)
    ivory2 = np.array([0xE7, 0xDF, 0xD3], dtype=np.float64)
    taupe = np.array([0x9C, 0x8F, 0x87], dtype=np.float64)
    cab = np.array([0x65, 0x2C, 0x39], dtype=np.float64)
    cab2 = np.array([0x4A, 0x1E, 0x28], dtype=np.float64)

    img = ivory[None, None, :] * (1 - base[..., None]) + ivory2[None, None, :] * base[..., None]

    vein_taupe = _smoothstep(0.62, 0.70, field) * (1 - _smoothstep(0.74, 0.82, field))
    img = img * (1 - vein_taupe[..., None] * 0.55) + taupe[None, None, :] * (vein_taupe[..., None] * 0.55)

    vein_cab = _smoothstep(0.80, 0.86, field)
    vein_cab2 = _smoothstep(0.88, 0.94, field)
    img = img * (1 - vein_cab[..., None] * 0.75) + cab[None, None, :] * (vein_cab[..., None] * 0.75)
    img = img * (1 - vein_cab2[..., None] * 0.85) + cab2[None, None, :] * (vein_cab2[..., None] * 0.85)

    grain = _fbm(size, 3, 77, 0.5) - 0.5
    img = np.clip(img + grain[..., None] * 6.0, 0, 255)
    return Image.fromarray(img.astype(np.uint8), "RGB")


def make_gunmetal_brushed_tex(size: int = 512) -> Image.Image:
    rng = np.random.default_rng(5)
    dark = np.array([0x2B, 0x2D, 0x32], dtype=np.float64)
    light = np.array([0x3A, 0x3D, 0x43], dtype=np.float64)

    rows = rng.random((size, 1))
    rows = np.repeat(rows, size, axis=1)
    fine = rng.random((size, size))
    fine = (fine + np.roll(fine, 1, axis=1) + np.roll(fine, 2, axis=1)) / 3.0
    streak = 0.6 * rows + 0.4 * fine
    streak = (streak - streak.min()) / (streak.max() - streak.min())

    img = dark[None, None, :] * (1 - streak[..., None]) + light[None, None, :] * streak[..., None]
    micro = (rng.random((size, size)) - 0.5) * 4.0
    img = np.clip(img + micro[..., None], 0, 255)
    return Image.fromarray(img.astype(np.uint8), "RGB")


def make_terracotta_pot_tex(size: int = 512) -> Image.Image:
    base = _fbm(size, 5, 31, 0.55)
    fine = _fbm(size, 3, 47, 0.5)
    c1 = np.array([0xB5, 0x6B, 0x4E], dtype=np.float64)
    c2 = np.array([0x9E, 0x58, 0x3E], dtype=np.float64)

    t = np.clip(0.55 * base + 0.45 * fine, 0, 1)
    img = c1[None, None, :] * (1 - t[..., None]) + c2[None, None, :] * t[..., None]

    efflor = _smoothstep(0.72, 0.86, _fbm(size, 4, 91, 0.5))
    img = img * (1 - efflor[..., None] * 0.35) + 235.0 * (efflor[..., None] * 0.35)

    speck = (np.random.default_rng(13).random((size, size)) > 0.995).astype(np.float64)
    img = np.clip(img - speck[..., None] * 25.0, 0, 255)
    return Image.fromarray(img.astype(np.uint8), "RGB")


def make_organic_dairy_label_tex(size: int = 512) -> Image.Image:
    cream = (0xFA, 0xF7, 0xF1)
    gold = (0xB8, 0xA0, 0x7A)
    ink = (0x2A, 0x26, 0x22)

    img = Image.new("RGB", (size, size), cream)
    d = ImageDraw.Draw(img)

    m = int(size * 0.06)
    d.rectangle([m, m, size - m, size - m], outline=gold, width=max(1, size // 256))

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    def centered(text: str, cy: int) -> None:
        if font is None:
            return
        try:
            bbox = d.textbbox((0, 0), text, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
        except Exception:
            w, h = len(text) * 6, 10
        d.text(((size - w) // 2, cy - h // 2), text, fill=ink, font=font)

    centered("GRASS-FED MILK", int(size * 0.30))
    centered("0% GREEK YOGURT", int(size * 0.70))

    cx, cy = size // 2, size // 2
    r = max(4, size // 40)
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], outline=gold)
    r2 = max(2, r // 2)
    d.polygon([(cx, cy - r2), (cx + r2, cy), (cx, cy + r2), (cx - r2, cy)], outline=gold)

    return img
