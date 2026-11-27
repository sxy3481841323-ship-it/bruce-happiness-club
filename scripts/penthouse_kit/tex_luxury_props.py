"""Procedural PBR-ish textures for penthouse luxury props.

All generators are deterministic (numpy default_rng) and return RGB PIL images.
"""

from __future__ import annotations

import math
from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------

_FONT_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _hex(c: str) -> Tuple[int, int, int]:
    c = c.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))


def _tracked_text(draw: ImageDraw.ImageDraw, xy, text, font, fill, tracking=0):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        try:
            w = draw.textlength(ch, font=font)
        except Exception:
            w = font.getsize(ch)[0]
        x += w + tracking
    return x


def _tracked_width(draw, text, font, tracking=0):
    total = 0.0
    for ch in text:
        try:
            total += draw.textlength(ch, font=font)
        except Exception:
            total += font.getsize(ch)[0]
        total += tracking
    return total - tracking if text else 0


# ---------------------------------------------------------------------------
# 1. Evian-style label
# ---------------------------------------------------------------------------

def make_evian_label_tex(w: int = 512, h: int = 256) -> Image.Image:
    rng = np.random.default_rng(20240517)
    img = Image.new("RGB", (w, h), _hex("#F9FBFD"))
    draw = ImageDraw.Draw(img)

    band_h = max(6, h // 22)
    aqua = _hex("#E8F1F6")
    draw.rectangle([0, 0, w, band_h], fill=aqua)
    draw.rectangle([0, h - band_h, w, h], fill=aqua)

    # subtle paper grain
    grain = rng.normal(0, 2.2, (h, w, 1)).repeat(3, axis=2)
    arr = np.asarray(img).astype(np.float32) + grain
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(img)

    # 3-peak Alps silhouette
    cx = w // 2
    base_y = int(h * 0.42)
    peak_h = int(h * 0.16)
    span = int(w * 0.30)
    peaks = [
        (cx - span, base_y - int(peak_h * 0.55)),
        (cx - span // 2, base_y - peak_h),
        (cx, base_y - int(peak_h * 0.75)),
        (cx + span // 2, base_y - int(peak_h * 0.95)),
        (cx + span, base_y - int(peak_h * 0.5)),
    ]
    rose = _hex("#D47D8A")
    blue = _hex("#9ABCE0")
    # jagged line: alternate colors per segment
    for i in range(len(peaks) - 1):
        x0, y0 = peaks[i]
        x1, y1 = peaks[i + 1]
        col = rose if i % 2 == 0 else blue
        # jagged micro-steps
        steps = 14
        pts = []
        for s in range(steps + 1):
            t = s / steps
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t + rng.normal(0, 1.4)
            pts.append((x, y))
        draw.line(pts, fill=col, width=2)

    # EVIAN lettering
    slate = _hex("#1F3042")
    f_big = _load_font(int(h * 0.20))
    txt = "EVIAN"
    tw = _tracked_width(draw, txt, f_big, tracking=int(w * 0.012))
    _tracked_text(draw, ((w - tw) / 2, int(h * 0.52)), txt, f_big, slate,
                  tracking=int(w * 0.012))

    # hairline caption
    f_small = _load_font(max(10, int(h * 0.055)))
    cap = "NATURAL SPRING WATER"
    cw = _tracked_width(draw, cap, f_small, tracking=int(w * 0.006))
    _tracked_text(draw, ((w - cw) / 2, int(h * 0.80)), cap, f_small, slate,
                  tracking=int(w * 0.006))

    # hairline rules
    rule_y = int(h * 0.78)
    draw.line([(int(w * 0.30), rule_y), (int(w * 0.70), rule_y)],
              fill=_hex("#9ABCE0"), width=1)

    return img


# ---------------------------------------------------------------------------
# 2. Concierge screen
# ---------------------------------------------------------------------------

def make_concierge_screen_tex(w: int = 512, h: int = 320) -> Image.Image:
    rng = np.random.default_rng(777001)
    img = Image.new("RGB", (w, h), _hex("#101012"))
    draw = ImageDraw.Draw(img)

    # brushed obsidian streaks
    arr = np.asarray(img).astype(np.float32)
    streak = rng.normal(0, 3.0, (h, 1, 1)).repeat(w, axis=1).repeat(3, axis=2)
    arr = np.clip(arr + streak, 0, 255)
    img = Image.fromarray(arr.astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(img)

    gold = _hex("#D6B476")
    # inner 2px champagne frame
    draw.rectangle([6, 6, w - 7, h - 7], outline=gold, width=2)

    # header
    f_head = _load_font(max(11, int(h * 0.055)))
    header = "PH·01 CONCIERGE INTERCOM"
    hw = _tracked_width(draw, header, f_head, tracking=2)
    _tracked_text(draw, ((w - hw) / 2, int(h * 0.06)), header, f_head, gold,
                  tracking=2)

    # tiles
    tiles = [
        ("01  BUTLER       · STANDBY", _hex("#8FA9C4")),
        ("02  CHAUFFEUR    · BAY B1 READY", _hex("#D6B476")),
        ("03  VALET & WINE · ACTIVE", _hex("#7FD1A6")),
    ]
    f_tile = _load_font(max(10, int(h * 0.048)))
    tile_x0 = int(w * 0.08)
    tile_x1 = int(w * 0.92)
    tile_h = int(h * 0.14)
    gap = int(h * 0.03)
    y = int(h * 0.22)
    for label, accent in tiles:
        draw.rectangle([tile_x0, y, tile_x1, y + tile_h],
                       fill=_hex("#17171A"), outline=_hex("#2A2A2E"), width=1)
        # accent bar
        draw.rectangle([tile_x0, y, tile_x0 + 4, y + tile_h], fill=accent)
        draw.text((tile_x0 + 16, y + tile_h // 2 - f_tile.size // 2 - 2),
                  label, font=f_tile, fill=_hex("#E8E4DA"))
        y += tile_h + gap

    # bottom status
    dot_r = max(4, int(h * 0.018))
    dot_cx = int(w * 0.10)
    dot_cy = int(h * 0.90)
    jade = _hex("#5FBF8F")
    draw.ellipse([dot_cx - dot_r, dot_cy - dot_r,
                  dot_cx + dot_r, dot_cy + dot_r], fill=jade)
    # glow
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([dot_cx - dot_r * 3, dot_cy - dot_r * 3,
                dot_cx + dot_r * 3, dot_cy + dot_r * 3], fill=jade)
    glow = glow.filter(ImageFilter.GaussianBlur(dot_r * 2))
    img = Image.fromarray(
        np.clip(np.asarray(img).astype(np.int16) +
                (np.asarray(glow).astype(np.int16) // 3), 0, 255).astype(np.uint8),
        "RGB")
    draw = ImageDraw.Draw(img)

    f_bot = _load_font(max(9, int(h * 0.042)))
    bot = "TAP TO SUMMON HOUSE STAFF"
    bw = _tracked_width(draw, bot, f_bot, tracking=2)
    _tracked_text(draw, (dot_cx + dot_r * 3, dot_cy - f_bot.size // 2 - 1),
                  bot, f_bot, _hex("#C9C4B8"), tracking=2)

    return img


# ---------------------------------------------------------------------------
# 3. Foyer mirror
# ---------------------------------------------------------------------------

def make_foyer_mirror_tex(size: int = 1024) -> Image.Image:
    rng = np.random.default_rng(31415)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    nx = xx / (size - 1)
    ny = yy / (size - 1)

    # warm deep espresso-bronze base
    base = np.zeros((size, size, 3), dtype=np.float32)
    base[..., 0] = 58 + 22 * ny
    base[..., 1] = 40 + 16 * ny
    base[..., 2] = 30 + 12 * ny

    # vertical skylight shimmer
    shimmer = 0.5 + 0.5 * np.sin(nx * math.pi * 1.0)
    shimmer = shimmer ** 2
    base += shimmer[..., None] * np.array([26, 20, 14], dtype=np.float32)

    # diagonal champagne sunlit band
    diag = (nx + ny) * 0.5
    band = np.exp(-((diag - 0.42) ** 2) / (2 * 0.06 ** 2))
    base += band[..., None] * np.array([70, 58, 38], dtype=np.float32)

    # subtle noise
    base += rng.normal(0, 3.0, (size, size, 3)).astype(np.float32)

    # antique mercury vignette
    cx = nx - 0.5
    cy = ny - 0.5
    r = np.sqrt(cx * cx + cy * cy) * 1.6
    vig = np.clip(1.0 - r, 0, 1) ** 1.4
    base *= (0.55 + 0.45 * vig)[..., None]

    # beveled edge darkening
    edge = np.minimum(np.minimum(nx, 1 - nx), np.minimum(ny, 1 - ny))
    bevel = np.clip(edge / 0.06, 0, 1)
    base *= (0.6 + 0.4 * bevel)[..., None]

    # faint mercury speckle
    speck = rng.random((size, size)) > 0.9985
    base[speck] += np.array([40, 34, 24], dtype=np.float32)

    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")


# ---------------------------------------------------------------------------
# 4. Foyer medallion
# ---------------------------------------------------------------------------

def make_foyer_medallion_tex(size: int = 1024) -> Image.Image:
    rng = np.random.default_rng(90210)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    cx = cy = (size - 1) / 2.0
    dx = xx - cx
    dy = yy - cy
    r = np.sqrt(dx * dx + dy * dy)
    theta = np.arctan2(dy, dx)

    # pale cream Calacatta field
    base = np.zeros((size, size, 3), dtype=np.float32)
    base[..., 0] = 236
    base[..., 1] = 231
    base[..., 2] = 220

    # subtle grey-gold veins (procedural)
    vein = np.zeros((size, size), dtype=np.float32)
    for k in range(9):
        ang = rng.uniform(0, math.pi * 2)
        off = rng.uniform(-0.4, 0.4) * size
        freq = rng.uniform(0.004, 0.012)
        phase = rng.uniform(0, math.pi * 2)
        proj = (xx * math.cos(ang) + yy * math.sin(ang)) + off
        wob = np.sin(proj * freq + phase) * 6.0
        dist = np.abs((xx * math.sin(ang) - yy * math.cos(ang)) + wob)
        vein += np.exp(-(dist ** 2) / (2 * 2.2 ** 2)) * rng.uniform(0.3, 0.7)
    vein = np.clip(vein, 0, 1)
    base -= vein[..., None] * np.array([26, 22, 16], dtype=np.float32)

    # Nero Marquina octagonal border
    oct_r = size * 0.46
    oct_inner = size * 0.40
    # octagon distance: use max of |x|,|y| rotated
    def oct_dist(px, py, R):
        a = np.abs(px)
        b = np.abs(py)
        # regular octagon: max(|x|,|y|, (|x|+|y|)/sqrt(2))
        return np.maximum(np.maximum(a, b), (a + b) / math.sqrt(2.0)) / R

    od = oct_dist(dx, dy, oct_r)
    od_in = oct_dist(dx, dy, oct_inner)
    border_mask = (od <= 1.0) & (od_in > 1.0)
    nero = np.array([18, 16, 18], dtype=np.float32)
    base[border_mask] = nero + rng.normal(0, 4, (border_mask.sum(), 3)).astype(np.float32)

    # brass double hairline rings
    brass = np.array([196, 158, 96], dtype=np.float32)
    for rr in (size * 0.335, size * 0.315):
        ring = np.abs(r - rr) < 1.6
        base[ring] = brass

    # 8-point compass inlay
    compass_r = size * 0.20
    for k in range(8):
        ang = k * math.pi / 4.0
        length = compass_r if k % 2 == 0 else compass_r * 0.55
        ex = cx + math.cos(ang) * length
        ey = cy + math.sin(ang) * length
        # draw thin line via distance to segment
        sx, sy = cx, cy
        vx, vy = ex - sx, ey - sy
        L2 = vx * vx + vy * vy
        t = np.clip(((xx - sx) * vx + (yy - sy) * vy) / L2, 0, 1)
        px = sx + t * vx
        py = sy + t * vy
        d = np.sqrt((xx - px) ** 2 + (yy - py) ** 2)
        line = d < 1.4
        base[line] = brass

    # center dot
    dot = r < 4
    base[dot] = brass

    # honed micro-noise
    base += rng.normal(0, 2.0, (size, size, 3)).astype(np.float32)

    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")


# ---------------------------------------------------------------------------
# 5. Fire ember bed
# ---------------------------------------------------------------------------

def make_fire_ember_tex(w: int = 512, h: int = 256) -> Image.Image:
    rng = np.random.default_rng(424242)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = xx / (w - 1)
    ny = yy / (h - 1)

    # dark basalt ash base
    base = np.zeros((h, w, 3), dtype=np.float32)
    base[..., 0] = 22 + 10 * ny
    base[..., 1] = 18 + 8 * ny
    base[..., 2] = 16 + 6 * ny

    # coal chunks
    coal = np.zeros((h, w), dtype=np.float32)
    for _ in range(70):
        cx = rng.uniform(0, w)
        cy = rng.uniform(0, h)
        rad = rng.uniform(6, 22)
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        coal = np.maximum(coal, np.exp(-(d ** 2) / (2 * rad ** 2)))
    base += coal[..., None] * np.array([10, 8, 6], dtype=np.float32)

    # molten cracks
    crack = np.zeros((h, w), dtype=np.float32)
    for _ in range(26):
        x = rng.uniform(0, w)
        y = rng.uniform(0, h)
        ang = rng.uniform(0, math.pi * 2)
        length = rng.uniform(40, 160)
        steps = 40
        for s in range(steps):
            t = s / steps
            ang += rng.normal(0, 0.25)
            x += math.cos(ang) * (length / steps)
            y += math.sin(ang) * (length / steps)
            if 0 <= x < w and 0 <= y < h:
                ix, iy = int(x), int(y)
                crack[iy, ix] = max(crack[iy, ix], 1.0 - t * 0.6)
    crack = np.asarray(
        Image.fromarray((crack * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255.0

    # bokeh glow
    bokeh = np.zeros((h, w), dtype=np.float32)
    for _ in range(40):
        cx = rng.uniform(0, w)
        cy = rng.uniform(0, h)
        rad = rng.uniform(3, 12)
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        bokeh += np.exp(-(d ** 2) / (2 * rad ** 2)) * rng.uniform(0.3, 1.0)
    bokeh = np.clip(bokeh, 0, 1)

    heat = np.clip(crack * 1.2 + bokeh * 0.6, 0, 1)

    amber = np.array([255, 140, 36], dtype=np.float32)
    crimson = np.array([204, 43, 18], dtype=np.float32)
    white_hot = np.array([255, 240, 200], dtype=np.float32)

    # color ramp by heat
    t = heat[..., None]
    low = crimson * (1 - t) + amber * t
    high = amber * (1 - t) + white_hot * t
    glow_col = low * (1 - t) + high * t

    base = base + glow_col * (heat[..., None] ** 1.3) * 1.6
    base += rng.normal(0, 3.0, (h, w, 3)).astype(np.float32)

    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")


# ---------------------------------------------------------------------------
# 6. Charred bark
# ---------------------------------------------------------------------------

def make_charred_bark_tex(w: int = 512, h: int = 256) -> Image.Image:
    rng = np.random.default_rng(13579)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = xx / (w - 1)
    ny = yy / (h - 1)

    # blackened bark base
    base = np.zeros((h, w, 3), dtype=np.float32)
    base[..., 0] = 14
    base[..., 1] = 12
    base[..., 2] = 11

    # vertical striations
    stri = np.zeros((h, w), dtype=np.float32)
    for _ in range(60):
        x0 = rng.uniform(0, w)
        width = rng.uniform(1.5, 6.0)
        wob = rng.uniform(0.5, 2.0)
        phase = rng.uniform(0, math.pi * 2)
        xc = x0 + np.sin(ny * math.pi * 2 * wob + phase) * 4.0
        d = np.abs(xx - xc)
        stri += np.exp(-(d ** 2) / (2 * width ** 2)) * rng.uniform(0.3, 1.0)
    stri = np.clip(stri, 0, 1)
    base += stri[..., None] * np.array([22, 18, 15], dtype=np.float32)

    # split fissures (dark)
    fissure = np.zeros((h, w), dtype=np.float32)
    for _ in range(18):
        x = rng.uniform(0, w)
        y = rng.uniform(0, h * 0.7)
        ang = math.pi / 2 + rng.normal(0, 0.4)
        length = rng.uniform(30, 120)
        steps = 30
        for s in range(steps):
            t = s / steps
            ang += rng.normal(0, 0.15)
            x += math.cos(ang) * (length / steps)
            y += math.sin(ang) * (length / steps)
            if 0 <= x < w and 0 <= y < h:
                fissure[int(y), int(x)] = max(fissure[int(y), int(x)], 1.0 - t * 0.5)
    fissure = np.asarray(
        Image.fromarray((fissure * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(1.0))).astype(np.float32) / 255.0
    base -= fissure[..., None] * np.array([10, 8, 6], dtype=np.float32)

    # glowing ember fissures near bottom / edges
    glow_mask = np.clip((ny - 0.58) / 0.42, 0, 1)
    edge_mask = np.clip((np.abs(nx - 0.5) - 0.35) / 0.15, 0, 1)
    glow_mask = np.maximum(glow_mask, edge_mask * 0.7)

    ember = np.zeros((h, w), dtype=np.float32)
    for _ in range(30):
        x = rng.uniform(0, w)
        y = rng.uniform(h * 0.55, h)
        ang = rng.uniform(-math.pi * 0.3, math.pi * 0.3) + math.pi / 2
        length = rng.uniform(20, 90)
        steps = 24
        for s in range(steps):
            t = s / steps
            ang += rng.normal(0, 0.2)
            x += math.cos(ang) * (length / steps)
            y += math.sin(ang) * (length / steps)
            if 0 <= x < w and 0 <= y < h:
                ember[int(y), int(x)] = max(ember[int(y), int(x)], 1.0 - t * 0.4)
    ember = np.asarray(
        Image.fromarray((ember * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(1.4))).astype(np.float32) / 255.0
    ember *= glow_mask

    orange = np.array([255, 110, 30], dtype=np.float32)
    crimson = np.array([190, 40, 20], dtype=np.float32)
    t = ember[..., None]
    glow_col = crimson * (1 - t) + orange * t
    base += glow_col * (ember[..., None] ** 1.2) * 1.8

    # ambient glow bloom near bottom
    bloom = np.clip((ny - 0.6) / 0.4, 0, 1) ** 2
    base += bloom[..., None] * np.array([60, 20, 6], dtype=np.float32)

    base += rng.normal(0, 2.5, (h, w, 3)).astype(np.float32)

    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "out")
    os.makedirs(out, exist_ok=True)
    make_evian_label_tex().save(os.path.join(out, "evian_label.png"))
    make_concierge_screen_tex().save(os.path.join(out, "concierge_screen.png"))
    make_foyer_mirror_tex().save(os.path.join(out, "foyer_mirror.png"))
    make_foyer_medallion_tex().save(os.path.join(out, "foyer_medallion.png"))
    make_fire_ember_tex().save(os.path.join(out, "fire_ember.png"))
    make_charred_bark_tex().save(os.path.join(out, "charred_bark.png"))
    print("wrote textures to", out)
