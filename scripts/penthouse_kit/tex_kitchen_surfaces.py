"""Penthouse kitchen surface textures — NumPy + PIL, deterministic, vectorized."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def _fbm(size, octaves=5, seed=0, persistence=0.5):
    rng = np.random.default_rng(seed)
    out = np.zeros((size, size), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        g = max(2, size >> (octaves - o))
        base = rng.random((g, g)).astype(np.float32)
        img = Image.fromarray((base * 255).astype(np.uint8)).resize((size, size), Image.BICUBIC)
        out += amp * (np.asarray(img, np.float32) / 255.0)
        tot += amp
        amp *= persistence
    return out / tot

def _lerp(c0, c1, t):
    c0 = np.array(c0, np.float32); c1 = np.array(c1, np.float32)
    return (c0 + (c1 - c0) * t[..., None]).clip(0, 255).astype(np.uint8)

def make_pietra_grey_marble_tex(size: int = 1024) -> Image.Image:
    y, x = np.mgrid[0:size, 0:size].astype(np.float32) / size
    cloud = _fbm(size, 4, 11, persistence=0.45)
    warp = _fbm(size, 3, 23, persistence=0.45) * 0.28 + _fbm(size, 2, 37, persistence=0.4) * 0.14
    diag = (x * 0.82 + y * 0.58 + warp) % 1.0
    vein = np.exp(-((diag - 0.42) ** 2) / 0.00014) * 0.78
    vein2 = np.exp(-(((diag * 2.1 + 0.18) % 1.0 - 0.55) ** 2) / 0.000045) * 0.45
    vein3 = np.exp(-(((x * 0.45 - y * 0.90 + warp * 0.7) % 1.0 - 0.62) ** 2) / 0.00003) * 0.30
    base = _lerp((54, 57, 63), (74, 78, 86), cloud)
    v = np.clip(vein + vein2 + vein3, 0, 0.85)[..., None]
    vc = np.array([232, 236, 242], np.float32)
    img = base.astype(np.float32) * (1 - v) + vc * v
    return Image.fromarray(img.clip(0, 255).astype(np.uint8))

def make_tundra_grey_floor_tex(size: int = 1024) -> Image.Image:
    n = _fbm(size, 5, 7)
    cloud = _fbm(size, 3, 19)
    t = np.clip(n * 0.6 + cloud * 0.4, 0, 1)
    img = _lerp((120, 125, 132), (138, 143, 150), t).astype(np.float32)
    joint = np.zeros((size, size), np.float32)
    step = size // 2
    for k in range(1, 2):
        joint[k * step - 1:k * step + 1, :] = 1
        joint[:, k * step - 1:k * step + 1] = 1
    img = img * (1 - joint[..., None] * 0.55) + np.array([90, 94, 100]) * joint[..., None] * 0.55
    return Image.fromarray(img.clip(0, 255).astype(np.uint8))

def make_platinum_slate_tex(size: int = 512) -> Image.Image:
    rng = np.random.default_rng(3)
    grain = rng.random((size, size)).astype(np.float32)
    grain = np.asarray(Image.fromarray((grain * 255).astype(np.uint8)).resize((size, size), Image.BILINEAR), np.float32) / 255
    streak = np.tile(np.linspace(0, 1, size, dtype=np.float32), (size, 1))
    t = np.clip(grain * 0.5 + streak * 0.5, 0, 1)
    return Image.fromarray(_lerp((41, 44, 50), (53, 57, 65), t))

def make_alpine_granite_cliff_tex(size: int = 1024) -> Image.Image:
    y, x = np.mgrid[0:size, 0:size].astype(np.float32) / size
    strata = _fbm(size, 6, 31)
    ridge = np.abs(np.sin((y * 9 + strata * 2.5) * np.pi)) ** 0.6
    facet = _fbm(size, 4, 41)
    t = np.clip(ridge * 0.7 + facet * 0.3, 0, 1)
    rock = _lerp((82, 90, 100), (208, 214, 222), t).astype(np.float32)
    crev = np.exp(-((np.abs(np.sin(y * 22 + strata * 3)) - 0.05) ** 2) / 0.002)
    rock = rock * (1 - crev[..., None] * 0.7) + np.array([43, 48, 55]) * crev[..., None] * 0.7
    forest_mask = np.clip((y - 0.70) / 0.30, 0, 1)
    fn = _fbm(size, 4, 53)
    forest = _lerp((35, 55, 45), (50, 74, 60), fn).astype(np.float32)
    out = rock * (1 - forest_mask[..., None]) + forest * forest_mask[..., None]
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))

def make_smart_panel_tex(w: int = 1024, h: int = 704) -> Image.Image:
    img = Image.new("RGB", (w, h), (15, 17, 21))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 22)
        small = ImageFont.truetype("DejaVuSans.ttf", 16)
    except Exception:
        font = ImageFont.load_default(); small = font
    tiles = [("LIGHTS", "SUNSET", (200, 170, 110)), ("HEARTH", "215°C", (200, 170, 110)),
             ("HARMAN", "JAZZ", (140, 190, 220)), ("GALLERY", "CH01", (140, 190, 220)),
             ("FRIDGE", "2°C", (140, 190, 220)), ("POOL", "27°C", (140, 190, 220))]
    pad, gap = 40, 24
    tw = (w - pad * 2 - gap * 2) // 3
    th = (h - pad * 2 - gap) // 2
    for i, (a, b, acc) in enumerate(tiles):
        cx = pad + (i % 3) * (tw + gap)
        cy = pad + (i // 3) * (th + gap)
        d.rounded_rectangle([cx, cy, cx + tw, cy + th], radius=18, fill=(24, 27, 33), outline=(58, 64, 75), width=2)
        d.text((cx + 24, cy + 24), a, fill=(220, 224, 230), font=font)
        d.rounded_rectangle([cx + 24, cy + th - 60, cx + 24 + 130, cy + th - 24], radius=18, fill=acc)
        d.text((cx + 40, cy + th - 54), b, fill=(15, 17, 21), font=small)
    ex, ey = w - 90, 60
    d.polygon([(ex, ey - 22), (ex + 22, ey), (ex, ey + 22), (ex - 22, ey)], outline=(200, 170, 110), width=2)
    d.polygon([(ex, ey - 12), (ex + 12, ey), (ex, ey + 12), (ex - 12, ey)], outline=(140, 190, 220), width=2)
    return img

def make_organic_dairy_label_tex(size: int = 512) -> Image.Image:
    img = Image.new("RGB", (size, size), (250, 247, 241))
    d = ImageDraw.Draw(img)
    try:
        big = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
        med = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
    except Exception:
        big = med = ImageFont.load_default()
    d.rectangle([40, 150, size - 40, 250], fill=(30, 32, 36))
    d.text((60, 175), "GRASS-FED MILK", fill=(250, 247, 241), font=big)
    d.rectangle([40, 280, size - 40, 370], fill=(30, 32, 36))
    d.text((60, 300), "0% GREEK YOGURT", fill=(250, 247, 241), font=med)
    return img
