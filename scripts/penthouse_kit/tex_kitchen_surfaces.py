import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def _lerp(c0, c1, t):
    return tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3))


def _fbm_grid(w, h, scales=(4.0, 8.0, 16.0, 32.0), weights=(0.50, 0.28, 0.14, 0.08), seed=11):
    rng = np.random.default_rng(seed)
    ys = np.linspace(0.0, 1.0, h, endpoint=False, dtype=np.float32)[:, None]
    xs = np.linspace(0.0, 1.0, w, endpoint=False, dtype=np.float32)[None, :]
    acc = np.zeros((h, w), dtype=np.float32)
    for sc, wt in zip(scales, weights):
        phx = rng.uniform(0, 6.283)
        phy = rng.uniform(0, 6.283)
        kx = 2.0 * math.pi * sc
        ky = 2.0 * math.pi * sc
        acc += wt * (
            np.sin(xs * kx + phx + np.cos(ys * ky * 0.7 + phy))
            * np.cos(ys * ky - phy + 0.5 * np.sin(xs * kx * 0.6))
        )
    return acc


def _fbm(x, y, seed=0):
    return math.sin(x * 1.1 + seed) * math.cos(y * 1.3 - seed) * 0.6


def _font(size):
    for name in ("/System/Library/Fonts/Supplemental/Georgia Bold.ttf", "DejaVuSans-Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def make_pietra_grey_marble_tex(w=1024, h=1024):
    n = _fbm_grid(w, h, scales=(3.0, 7.0, 15.0, 31.0), seed=11)
    base = np.clip(58.0 + n * 12.0, 36, 86)
    arr = np.stack([base, base + 2.5, base + 7.5], axis=-1).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    for _ in range(11):
        x0, y0 = rnd.randint(-80, w), rnd.randint(0, h)
        pts = [(x0, y0)]
        cx, cy = x0, y0
        for _ in range(44):
            cx += rnd.randint(16, 36)
            cy += rnd.randint(-20, 20)
            pts.append((cx, cy))
        d.line(pts, fill=(230, 233, 239), width=rnd.randint(1, 3))
        d.line([(p[0] + 2, p[1] + 2) for p in pts], fill=(176, 182, 192), width=1)
    return img.filter(ImageFilter.GaussianBlur(0.5))


def make_tundra_grey_floor_tex(w=1024, h=1024):
    n = _fbm_grid(w, h, scales=(5.0, 11.0, 24.0, 48.0), seed=23)
    base = np.clip(182.0 + n * 11.0, 145, 212)
    arr = np.stack([base, base - 2.0, base - 6.0], axis=-1).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    d = ImageDraw.Draw(img)
    for y in range(0, h, 256):
        d.line([(0, y), (w, y)], fill=(144, 141, 134), width=2)
    for x in range(0, w, 256):
        d.line([(x, 0), (x, h)], fill=(144, 141, 134), width=2)
    return img


def make_platinum_slate_tex(w=512, h=512):
    """Warm charcoal-dove cabinetry (#565B64, never pure jet-black)."""
    n = _fbm_grid(w, h, scales=(12.0, 24.0, 48.0, 96.0), weights=(0.35, 0.30, 0.20, 0.15), seed=31)
    base = np.clip(88.0 + n * 7.0, 72, 108)
    arr = np.stack([base, base + 5.0, base + 14.0], axis=-1).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    d = ImageDraw.Draw(img)
    for x in range(0, w, 4):
        d.line([(x, 0), (x, h)], fill=(80, 85, 94), width=1)
    d.rectangle([0, 0, w - 1, 5], fill=(64, 68, 76))
    return img


def make_alpine_granite_cliff_tex(w=1024, h=1024):
    return make_aaa_snow_granite_mountain_tex(w, h)


def make_smart_panel_tex(w=1024, h=680):
    img = Image.new("RGB", (w, h), (7, 10, 16))
    d = ImageDraw.Draw(img)
    d.rectangle([16, 16, w - 16, h - 16], outline=(214, 169, 84), width=3)
    cx, cy = w // 2, 200
    d.ellipse([cx - 122, cy - 122, cx + 122, cy + 122], outline=(214, 169, 84), width=6)
    d.ellipse([cx - 102, cy - 102, cx + 102, cy + 102], outline=(110, 88, 45), width=2)
    f_big = _font(54)
    f_md = _font(24)
    f_sm = _font(17)
    d.text((64, 42), "WHOLE-HOME INTELLIGENCE · PH-01", fill=(214, 169, 84), font=f_sm)
    d.text((cx - 86, cy - 32), "21.5 C", fill=(246, 240, 228), font=f_big)
    d.text((cx - 56, cy + 36), "CLIMATE OPTIMAL", fill=(214, 169, 84), font=f_sm)
    buttons = ["Arrival", "Chef Prep", "Piano Salon", "Poolside"]
    bw = 204
    for i, b in enumerate(buttons):
        bx = 58 + i * (bw + 24)
        fill = (32, 28, 22) if i == 1 else (16, 20, 28)
        d.rounded_rectangle([bx, 376, bx + bw, 444], radius=12, fill=fill, outline=(214, 169, 84), width=2)
        d.text((bx + 28, 396), b, fill=(248, 244, 236), font=f_md)
    labels = ["SALON COVE", "PIANO WING", "POOL & BBQ"]
    for i, lbl in enumerate(labels):
        sy = 492 + i * 52
        d.text((60, sy - 2), lbl, fill=(185, 192, 206), font=f_sm)
        d.rounded_rectangle([240, sy, w - 64, sy + 20], radius=10, fill=(22, 27, 36), outline=(72, 80, 96), width=1)
        d.rounded_rectangle([240, sy, 240 + 260 + i * 110, sy + 20], radius=10, fill=(214, 169, 84))
    return img


def make_organic_dairy_label_tex(w=512, h=256):
    img = Image.new("RGB", (w, h), (246, 242, 230))
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, w - 8, h - 8], outline=(28, 108, 68), width=4)
    d.ellipse([28, 28, 108, 108], fill=(28, 108, 68))
    d.ellipse([44, 44, 92, 92], fill=(246, 242, 230))
    f1, f2 = _font(26), _font(17)
    d.text((128, 38), "ORGANIC PASTURE", fill=(28, 108, 68), font=f1)
    d.text((128, 78), "WHOLE MILK & 0% YOGURT", fill=(48, 52, 56), font=f2)
    d.line([(128, 114), (w - 36, 114)], fill=(28, 108, 68), width=2)
    d.text((128, 134), "A2 GRASS-FED HERITAGE", fill=(58, 62, 66), font=f2)
    return img


def make_prestige_wine_labels_tex(w=1024, h=512):
    img = Image.new("RGB", (w, h), (18, 20, 22))
    d = ImageDraw.Draw(img)
    titles = [
        ["DOM PERIGNON", "CRISTAL", "KRUG", "ROMANEE-CONTI"],
        ["PETRUS", "CH. LAFITE", "CH. MARGAUX", "OPUS ONE"],
    ]
    subtitles = [
        ["VINTAGE 2013", "ROEDERER", "GRANDE CUVEE", "GRAND CRU"],
        ["POMEROL", "PAUILLAC", "PREMIER CRU", "NAPA VALLEY"],
    ]
    bg = [
        (16, 18, 20), (212, 178, 84), (242, 234, 210), (246, 240, 224),
        (238, 228, 212), (245, 240, 230), (242, 236, 222), (246, 244, 238),
    ]
    ink = [
        (228, 194, 112), (118, 24, 30), (112, 22, 34), (132, 26, 36),
        (128, 22, 30), (62, 46, 36), (34, 34, 38), (28, 42, 74),
    ]
    cw, ch = w // 4, h // 2
    f1, f2 = _font(21), _font(14)
    for r in range(2):
        for c in range(4):
            idx = r * 4 + c
            x0, y0 = c * cw, r * ch
            d.rectangle([x0 + 10, y0 + 10, x0 + cw - 10, y0 + ch - 10], fill=bg[idx], outline=ink[idx], width=3)
            d.ellipse([x0 + cw // 2 - 28, y0 + 28, x0 + cw // 2 + 28, y0 + 84], outline=ink[idx], width=3)
            d.text((x0 + 22, y0 + 116), titles[r][c], fill=ink[idx], font=f1)
            d.text((x0 + 22, y0 + 150), subtitles[r][c], fill=ink[idx], font=f2)
    return img


def make_aaa_snow_granite_mountain_tex(w=2048, h=1024):
    """V=0 (bottom) deep spruce forest -> mid Dolomite granite crags -> V=1 (top) snow glacier caps."""
    v_col = np.linspace(1.0, 0.0, h, dtype=np.float32)[:, None]
    n1 = _fbm_grid(w, h, scales=(5.0, 11.0, 23.0, 47.0), seed=41)
    n2 = _fbm_grid(w, h, scales=(14.0, 29.0, 61.0, 127.0), seed=77)
    u_col = np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]
    striation = np.sin(u_col * 36.0 * math.pi + n1 * 1.4) * 0.5 + 0.5
    v_warped = np.clip(v_col + n1 * 0.055 + (striation - 0.5) * 0.025, 0.0, 1.0)

    r = np.zeros((h, w), dtype=np.float32)
    g = np.zeros((h, w), dtype=np.float32)
    b = np.zeros((h, w), dtype=np.float32)

    # Low timberline band: dark emerald pines + alpine meadow
    m_low = v_warped < 0.24
    t_low = np.clip(v_warped / 0.24, 0.0, 1.0)
    r[m_low] = (20 + 20 * t_low + n2 * 10)[m_low]
    g[m_low] = (46 + 24 * t_low + n2 * 12)[m_low]
    b[m_low] = (32 + 16 * t_low + n2 * 8)[m_low]

    # Mid chiseled granite cliff faces + cool cleft shadows (no wormy lines)
    m_mid = (v_warped >= 0.24) & (v_warped < 0.56)
    t_mid = np.clip((v_warped - 0.24) / 0.32, 0.0, 1.0)
    cliff_shade = (striation * 0.45 + 0.55)
    r[m_mid] = ((64 + 44 * t_mid) * cliff_shade + n2 * 14)[m_mid]
    g[m_mid] = ((70 + 46 * t_mid) * cliff_shade + n2 * 14)[m_mid]
    b[m_mid] = ((82 + 48 * t_mid) * cliff_shade + n2 * 16)[m_mid]

    # Upper alpine snow & sunlit glacier crests
    m_hi = v_warped >= 0.56
    t_hi = np.clip((v_warped - 0.56) / 0.44, 0.0, 1.0)
    r[m_hi] = (176 + 78 * t_hi + n2 * 8)[m_hi]
    g[m_hi] = (196 + 56 * t_hi + n2 * 7)[m_hi]
    b[m_hi] = (218 + 30 * t_hi + n2 * 5)[m_hi]

    arr = np.clip(np.stack([r, g, b], axis=-1), 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")
