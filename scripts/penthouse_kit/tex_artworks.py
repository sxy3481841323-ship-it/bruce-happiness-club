"""Procedural artwork textures for the penthouse kit (PIL + NumPy)."""
from __future__ import annotations

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ----------------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------------
CREAM = (246, 239, 226)
TRAVERTINE = (223, 204, 176)
BURGUNDY = (110, 24, 36)
WALNUT = (74, 43, 27)
GOLD = (223, 190, 125)
CERULEAN = (18, 74, 122)
DEEP_CERULEAN = (10, 48, 88)
SAND = (232, 200, 140)
WHITE = (250, 248, 242)


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def _canvas(w: int, h: int, color) -> Image.Image:
    return Image.new("RGB", (w, h), color)


def _gradient(w: int, h: int, top, bottom) -> Image.Image:
    """Vertical linear gradient."""
    t = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    top = np.array(top, dtype=np.float32)
    bottom = np.array(bottom, dtype=np.float32)
    arr = top[None, :] * (1 - t) + bottom[None, :] * t
    arr = np.repeat(arr[:, None, :], w, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def _noise_overlay(img: Image.Image, amount: float = 6.0, seed: int = 0) -> Image.Image:
    """Add subtle grain for a painterly feel."""
    rng = np.random.default_rng(seed)
    arr = np.asarray(img, dtype=np.float32)
    noise = rng.normal(0, amount, arr.shape[:2])[..., None]
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def _soft_blur(img: Image.Image, radius: float) -> Image.Image:
    return img.filter(ImageFilter.GaussianBlur(radius))


def _mat_border(img: Image.Image, border: int = 26, color=CREAM) -> Image.Image:
    """Wrap artwork in a clean cream museum mat, preserving original size."""
    w, h = img.size
    out = _canvas(w, h, color)
    inner = img.resize((w - border * 2, h - border * 2), Image.LANCZOS)
    out.paste(inner, (border, border))
    d = ImageDraw.Draw(out)
    d.rectangle([border - 2, border - 2, w - border + 1, h - border + 1],
                outline=(210, 198, 178), width=1)
    return out


def _sunburst(draw: ImageDraw.ImageDraw, cx, cy, r, n, colors, start=0.0):
    for i in range(n):
        a0 = start + i * 2 * math.pi / n
        a1 = a0 + math.pi / n
        pts = [(cx, cy),
               (cx + r * math.cos(a0), cy + r * math.sin(a0)),
               (cx + r * math.cos(a1), cy + r * math.sin(a1))]
        draw.polygon(pts, fill=colors[i % len(colors)])


# ----------------------------------------------------------------------------
# TV artworks (1024 x 576)
# ----------------------------------------------------------------------------
def _tv_coast() -> Image.Image:
    W, H = 1024, 576
    img = _gradient(W, H, (250, 214, 150), (255, 236, 200))
    d = ImageDraw.Draw(img)
    d.ellipse([760, 60, 900, 200], fill=(255, 226, 168))
    d.ellipse([790, 90, 870, 170], fill=(255, 240, 200))
    d.rectangle([0, 300, W, H], fill=CERULEAN)
    d.rectangle([0, 300, W, 340], fill=(30, 96, 148))
    for i in range(6):
        y = 360 + i * 34
        d.line([(0, y), (W, y + 6)], fill=(40, 110, 160), width=3)
    d.polygon([(0, 300), (0, 120), (180, 180), (300, 260), (260, 320), (0, 340)],
              fill=(214, 168, 96))
    d.polygon([(0, 300), (0, 200), (120, 240), (200, 300)], fill=(232, 190, 120))
    for bx, by, s in [(560, 300, 1.0), (700, 340, 0.7)]:
        d.polygon([(bx, by), (bx, by - 120 * s), (bx + 70 * s, by)], fill=WHITE)
        d.polygon([(bx + 8 * s, by), (bx + 8 * s, by - 90 * s),
                   (bx - 50 * s, by)], fill=(240, 236, 226))
        d.line([(bx - 60 * s, by + 6), (bx + 80 * s, by + 6)], fill=WALNUT, width=4)
    return _noise_overlay(img, 4, 1)


def _tv_bauhaus() -> Image.Image:
    W, H = 1024, 576
    img = _canvas(W, H, CREAM)
    d = ImageDraw.Draw(img)
    d.pieslice([80, 120, 380, 420], 180, 360, fill=TRAVERTINE)
    d.rectangle([80, 270, 380, 420], fill=TRAVERTINE)
    d.pieslice([420, 60, 700, 340], 180, 360, fill=BURGUNDY)
    d.rectangle([420, 200, 700, 340], fill=BURGUNDY)
    d.pieslice([640, 260, 940, 560], 180, 360, fill=WALNUT)
    d.rectangle([640, 410, 940, 560], fill=WALNUT)
    d.ellipse([180, 380, 320, 520], fill=GOLD)
    d.ellipse([520, 380, 620, 480], fill=TRAVERTINE)
    d.ellipse([760, 120, 880, 240], fill=GOLD)
    d.line([(0, 300), (W, 300)], fill=WALNUT, width=2)
    d.line([(512, 0), (512, H)], fill=WALNUT, width=2)
    return _noise_overlay(img, 3, 2)


def _tv_terrace() -> Image.Image:
    W, H = 1024, 576
    img = _gradient(W, H, (246, 238, 224), (235, 222, 200))
    d = ImageDraw.Draw(img)
    # Minimalist luxury arch window overlooking azure sky + Matisse terracotta amphora & olive branch
    d.pieslice([260, 56, 764, 560], 180, 360, fill=(102, 174, 238))
    d.rectangle([260, 308, 764, 504], fill=(138, 198, 245))
    for cx, cy, rx, ry in [(390, 195, 75, 28), (455, 185, 58, 24), (630, 220, 80, 26)]:
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(252, 250, 244))
    d.rectangle([260, 390, 764, 504], fill=(48, 128, 184))
    d.rectangle([0, 496, W, H], fill=(216, 198, 168))
    # Sculptural brushed-brass pedestal + dark burgundy-terracotta amphora + olive stems
    d.polygon([(476, 512), (548, 512), (566, 392), (534, 344), (490, 344), (458, 392)], fill=BURGUNDY)
    d.ellipse([484, 336, 540, 356], fill=GOLD)
    for stem_end, side in [((420, 225), -1), ((518, 190), 1), ((590, 245), 1)]:
        d.line([(512, 344), stem_end], fill=WALNUT, width=5)
        for t in (0.35, 0.58, 0.80, 0.96):
            lx = int(512 + (stem_end[0] - 512) * t)
            ly = int(344 + (stem_end[1] - 344) * t)
            d.ellipse([lx - 22, ly - 10, lx + 22, ly + 10], fill=(92, 128, 72))
    return _noise_overlay(img, 3, 3)


def make_tv_artworks() -> list[Image.Image]:
    return [_tv_coast(), _tv_bauhaus(), _tv_terrace()]


# ----------------------------------------------------------------------------
# Gallery travel cards (512 x 640)
# ----------------------------------------------------------------------------
def _card_aurora() -> Image.Image:
    W, H = 512, 640
    img = _gradient(W, H, (10, 24, 40), (30, 60, 70))
    d = ImageDraw.Draw(img)
    for y, c in [(120, (40, 200, 140)), (170, (60, 220, 160)),
                 (220, (30, 180, 130))]:
        d.arc([-100, y, W + 100, y + 200], 200, 340, fill=c, width=18)
    for px in range(40, W, 70):
        d.polygon([(px, 520), (px + 30, 400), (px + 60, 520)], fill=(15, 40, 30))
    d.rectangle([200, 480, 320, 560], fill=(60, 40, 30))
    d.polygon([(190, 480), (260, 430), (330, 480)], fill=(90, 60, 40))
    d.rectangle([240, 510, 270, 540], fill=(255, 210, 120))
    return _noise_overlay(img, 5, 4)


def _card_bay() -> Image.Image:
    W, H = 512, 640
    img = _gradient(W, H, (200, 240, 250), (120, 210, 220))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 380, W, H], fill=(60, 190, 200))
    d.rectangle([0, 500, W, H], fill=(240, 210, 140))
    d.pieslice([180, 260, 340, 420], 180, 360, fill=(230, 90, 80))
    for i in range(6):
        a = math.pi + i * math.pi / 6
        d.line([(260, 340), (260 + 80 * math.cos(a), 340 + 80 * math.sin(a))],
               fill=WHITE, width=3)
    d.line([(260, 340), (260, 500)], fill=WALNUT, width=5)
    return _noise_overlay(img, 4, 5)


def _card_yacht() -> Image.Image:
    W, H = 512, 640
    img = _gradient(W, H, (140, 200, 240), (200, 230, 250))
    d = ImageDraw.Draw(img)
    for cx, cy, r in [(120, 120, 50), (300, 90, 60), (420, 140, 45)]:
        d.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], fill=WHITE)
    d.rectangle([0, 400, W, H], fill=(20, 50, 110))
    d.polygon([(60, 460), (450, 460), (420, 520), (90, 520)], fill=(180, 130, 80))
    d.rectangle([140, 380, 380, 460], fill=(230, 220, 200))
    d.rectangle([160, 400, 360, 440], fill=(120, 180, 210))
    return _noise_overlay(img, 4, 6)


def _card_alpine() -> Image.Image:
    W, H = 512, 640
    img = _gradient(W, H, (255, 220, 170), (255, 240, 210))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 380), (140, 180), (280, 380)], fill=(120, 130, 150))
    d.polygon([(200, 380), (360, 150), (512, 380)], fill=(100, 110, 130))
    d.polygon([(100, 240), (140, 180), (180, 240)], fill=WHITE)
    d.polygon([(320, 220), (360, 150), (400, 220)], fill=WHITE)
    d.rectangle([0, 380, W, H], fill=(200, 170, 80))
    for i in range(40):
        x = (i * 37) % W
        y = 400 + (i * 53) % 220
        d.ellipse([x, y, x + 6, y + 6], fill=(230, 200, 100))
    return _noise_overlay(img, 5, 7)


def make_gallery_travel_artworks() -> list[Image.Image]:
    cards = [_card_aurora(), _card_bay(), _card_yacht(), _card_alpine()]
    return [_mat_border(c, border=28) for c in cards]


# ----------------------------------------------------------------------------
# Vinyl cover
# ----------------------------------------------------------------------------
def make_vinyl_cover_tex(size: int = 512) -> Image.Image:
    img = _canvas(size, size, CREAM)
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    _sunburst(d, cx, cy, size * 0.46, 24, [BURGUNDY, GOLD, CREAM], start=-math.pi / 2)
    d.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], fill=CREAM)
    d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=BURGUNDY)
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=CREAM)
    try:
        from PIL import ImageFont
        font = ImageFont.load_default()
    except Exception:
        font = None
    d.text((cx, size - 60), "SUNLIT PENTHOUSE", fill=WALNUT, anchor="mm", font=font)
    d.text((cx, size - 36), "· 33RPM ·", fill=BURGUNDY, anchor="mm", font=font)
    return _noise_overlay(img, 3, 8)


__all__ = ["make_tv_artworks", "make_gallery_travel_artworks", "make_vinyl_cover_tex"]
