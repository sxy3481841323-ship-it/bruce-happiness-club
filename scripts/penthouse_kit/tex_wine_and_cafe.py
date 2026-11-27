import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def _load_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _tracked_text(draw, xy, text, font, fill, tracking=0, anchor_center=True):
    widths = []
    for ch in text:
        try:
            bbox = draw.textbbox((0, 0), ch, font=font)
            widths.append(bbox[2] - bbox[0])
        except Exception:
            widths.append(font.getsize(ch)[0])
    total = sum(widths) + tracking * max(0, len(text) - 1)
    x, y = xy
    if anchor_center:
        x -= total / 2.0
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking
    return total


def make_fine_wine_label_tex(size=512, variant=0):
    rng = np.random.default_rng(1000 + variant)
    W = H = size
    img = Image.new("RGB", (W, H), (18, 40, 30))
    px = np.array(img).astype(np.float32)

    yy = np.linspace(0, 1, H)[:, None]
    xx = np.linspace(0, 1, W)[None, :]

    base_r = 22 + 10 * yy
    base_g = 46 + 14 * yy
    base_b = 34 + 8 * yy
    px[..., 0] = base_r
    px[..., 1] = base_g
    px[..., 2] = base_b

    streak = (np.sin(xx * 40 + rng.uniform(0, 6)) * 0.5 + 0.5) * 6
    px[..., 1] += streak
    px[..., 2] += streak * 0.6

    neck_mask = np.clip(1.0 - yy / 0.18, 0, 1)
    capsule = neck_mask * (0.55 + 0.45 * np.cos((xx - 0.5) * math.pi * 1.4))
    capsule = np.clip(capsule, 0, 1)
    px[..., 0] += capsule * 150
    px[..., 1] += capsule * 110
    px[..., 2] += capsule * 40

    bottom = np.clip((yy - 0.85) / 0.15, 0, 1)
    px *= (1.0 - bottom * 0.35)[..., None]

    img = Image.fromarray(np.clip(px, 0, 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(img)

    lx0, ly0, lx1, ly1 = 64, 145, 448, 365
    draw.rectangle([lx0, ly0, lx1, ly1], fill=(238, 228, 202))

    grain = rng.normal(0, 3.0, (ly1 - ly0, lx1 - lx0, 3))
    lab = np.array(img.crop((lx0, ly0, lx1, ly1))).astype(np.float32)
    lab = np.clip(lab + grain, 0, 255)
    img.paste(Image.fromarray(lab.astype(np.uint8), "RGB"), (lx0, ly0))
    draw = ImageDraw.Draw(img)

    draw.rectangle([lx0 + 6, ly0 + 6, lx1 - 6, ly1 - 6], outline=(140, 26, 34), width=2)
    draw.rectangle([lx0 + 12, ly0 + 12, lx1 - 12, ly1 - 12], outline=(176, 138, 62), width=1)

    cx, cy = (lx0 + lx1) // 2, ly0 + 62
    d = 22
    draw.polygon([(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)],
                 outline=(140, 26, 34))
    d2 = 14
    draw.polygon([(cx, cy - d2), (cx + d2, cy), (cx, cy + d2), (cx - d2, cy)],
                 outline=(176, 138, 62))
    draw.line([(cx, cy - 8), (cx, cy + 8)], fill=(140, 26, 34), width=1)
    draw.line([(cx - 8, cy), (cx + 8, cy)], fill=(140, 26, 34), width=1)

    if variant == 0:
        title = "CHATEAU MALIBU"
        sub = "GRAND VIN"
    elif variant == 1:
        title = "COTE DE BEAUNE"
        sub = "GRAND VIN"
    else:
        title = "BAROLO RISERVA"
        sub = "GRAND VIN \u00b7 2018"

    f_title = _load_font(26)
    f_sub = _load_font(15)
    _tracked_text(draw, (cx, ly0 + 108), title, f_title, (60, 20, 24), tracking=3)
    _tracked_text(draw, (cx, ly0 + 150), sub, f_sub, (110, 80, 40), tracking=4)

    draw.line([(cx - 90, ly0 + 178), (cx + 90, ly0 + 178)], fill=(176, 138, 62), width=1)

    f_foot = _load_font(11)
    _tracked_text(draw, (cx, ly0 + 190), "MISE EN BOUTEILLE", f_foot, (110, 80, 40), tracking=2)

    return img


def make_celadon_sage_tile_tex(size=1024):
    rng = np.random.default_rng(2024)
    W = H = size
    base = np.array([182, 206, 174], dtype=np.float32)

    def octave(scale, amp):
        small = rng.normal(0, 1, (scale, scale)).astype(np.float32)
        lo = float(small.min())
        hi = float(small.max())
        rng_span = max(hi - lo, 1e-6)
        norm = ((small - lo) / rng_span * 255.0).astype(np.uint8)
        im = Image.fromarray(norm, "L")
        im = im.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(max(1.0, scale * 0.4)))
        return (np.array(im).astype(np.float32) / 255.0 - 0.5) * amp

    field = octave(8, 14) + octave(24, 8) + octave(64, 4) + octave(160, 2)

    px = np.zeros((H, W, 3), dtype=np.float32)
    px[..., 0] = base[0] + field * 0.9
    px[..., 1] = base[1] + field * 1.0
    px[..., 2] = base[2] + field * 0.85

    speck = rng.normal(0, 2.2, (H, W, 1))
    px += speck

    img = Image.fromarray(np.clip(px, 0, 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(img)

    grout = (128, 148, 122)
    half = W // 2
    for gx in (0, half, W - 5):
        draw.rectangle([gx, 0, gx + 4, H], fill=grout)
    for gy in (0, half, H - 5):
        draw.rectangle([0, gy, W, gy + 4], fill=grout)

    arr = np.array(img).astype(np.float32)
    yy = np.linspace(0, 1, H)[:, None, None]
    sheen = 1.0 + 0.03 * np.sin(yy * math.pi)
    arr = np.clip(arr * sheen, 0, 255)
    img = Image.fromarray(arr.astype(np.uint8), "RGB")

    return img


def make_flame_atlas_tex(size=512):
    W = H = size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = xx / (W - 1)
    ny = yy / (H - 1)

    base_y = 0.88
    tip_y = 0.08
    t = np.clip((base_y - ny) / (base_y - tip_y), 0, 1)

    center = 0.5 + 0.035 * np.sin(t * math.pi * 3.1 + 0.7) * t \
        + 0.02 * np.sin(t * math.pi * 6.3 + 1.9) * t \
        + 0.012 * np.sin(t * math.pi * 11.0 + 0.3) * t

    width = 0.30 * (1.0 - t) ** 0.85 + 0.02
    width *= 1.0 + 0.10 * np.sin(t * math.pi * 4.0 + 0.5)

    dx = (nx - center) / np.maximum(width, 1e-4)
    radial = np.exp(-dx * dx * 1.6)

    vert = np.clip((base_y - ny) / (base_y - tip_y), 0, 1)
    vert = np.power(vert, 0.55)
    vert *= np.clip((ny - tip_y) / 0.05, 0, 1)

    flick = 0.85 + 0.15 * np.sin(ny * 40 + nx * 12 + 1.3) * np.sin(ny * 17 + 0.4)
    intensity = radial * vert * flick
    intensity = np.clip(intensity, 0, 1)

    core_dx = (nx - 0.5) / 0.10
    core_dy = (ny - 0.82) / 0.10
    core = np.exp(-(core_dx * core_dx + core_dy * core_dy) * 1.2)
    intensity = np.clip(intensity + core * 0.9, 0, 1)

    c_outer = np.array([238, 72, 18], dtype=np.float32)
    c_mid = np.array([255, 165, 48], dtype=np.float32)
    c_core = np.array([255, 244, 196], dtype=np.float32)

    heat = np.clip(intensity, 0, 1)
    h1 = np.clip(heat / 0.55, 0, 1)
    h2 = np.clip((heat - 0.55) / 0.45, 0, 1)

    col = c_outer[None, None, :] * (1 - h1[..., None]) + c_mid[None, None, :] * h1[..., None]
    col = col * (1 - h2[..., None]) + c_core[None, None, :] * h2[..., None]

    alpha = np.clip(intensity * 1.15, 0, 1)
    alpha = np.power(alpha, 0.85)

    border = 6
    alpha[:border, :] = 0
    alpha[-border:, :] = 0
    alpha[:, :border] = 0
    alpha[:, -border:] = 0

    cy_i, cx_i = 420, 256
    if 0 <= cy_i < H and 0 <= cx_i < W:
        alpha[cy_i, cx_i] = max(alpha[cy_i, cx_i], 0.92)
        col[cy_i, cx_i] = c_core

    alpha_u8 = np.clip(alpha * 255, 0, 255).astype(np.uint8)
    rgb_u8 = np.clip(col, 0, 255).astype(np.uint8)

    out = np.dstack([rgb_u8, alpha_u8])
    img = Image.fromarray(out, "RGBA")

    img = img.filter(ImageFilter.GaussianBlur(1.2))
    arr = np.array(img)
    arr[:border, :, 3] = 0
    arr[-border:, :, 3] = 0
    arr[:, :border, 3] = 0
    arr[:, -border:, 3] = 0
    arr[cy_i, cx_i, 3] = max(arr[cy_i, cx_i, 3], 225)
    img = Image.fromarray(arr, "RGBA")

    return img
