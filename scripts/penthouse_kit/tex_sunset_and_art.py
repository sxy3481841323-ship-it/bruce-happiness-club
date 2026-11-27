import numpy as np
from PIL import Image, ImageFilter

def _hex(c):
    c = c.lstrip('#')
    return np.array([int(c[i:i+2], 16) for i in (0, 2, 4)], dtype=np.float32)

def _grad(stops, n):
    # stops: list of (pos, hexcolor); returns (n,3)
    pos = np.array([s[0] for s in stops], dtype=np.float32)
    cols = np.stack([_hex(s[1]) for s in stops])
    t = np.linspace(0, 1, n, dtype=np.float32)
    out = np.zeros((n, 3), dtype=np.float32)
    for k in range(3):
        out[:, k] = np.interp(t, pos, cols[:, k])
    return out

def _fbm(h, w, octaves=5, seed=0, base=4):
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), dtype=np.float32)
    amp = 1.0
    tot = 0.0
    for o in range(octaves):
        gh, gw = base * (2 ** o), base * 2 * (2 ** o)
        g = rng.random((gh, gw)).astype(np.float32)
        gi = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        acc += amp * (np.asarray(gi, dtype=np.float32) / 255.0)
        tot += amp
        amp *= 0.5
    return acc / tot

def make_sunset_sky_panorama(w=4096, h=1024):
    v = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    u = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    horizon = 0.72
    sky = _grad([(0.0, '#2B466F'), (0.24, '#4C658D'), (0.48, '#C9856C'),
                 (0.66, '#F4BE82'), (0.72, '#F7CE98')], h)
    sea = _grad([(0.72, '#2B4B6B'), (1.0, '#183049')], h)
    img = np.where(v < horizon, sky, sea)
    img = np.broadcast_to(img[:, None, :], (h, w, 3)).copy()

    # Soft radiant golden sunset halo above horizon (smooth, zero hard stripes)
    su, sv = 0.50, 0.62
    d = np.sqrt(((u - su) * 1.0) ** 2 + ((v - sv) * (h / w) * 2.4) ** 2)
    halo = np.exp(-(d / 0.14) ** 2) * 0.82 + np.exp(-(d / 0.34) ** 2) * 0.32
    orb = np.clip(1.0 - d / 0.026, 0, 1) ** 0.8
    sun_col = _hex('#FFEEC2')
    img = img + halo[..., None] * (_hex('#FFC87C') - img) * 0.82
    img = img + orb[..., None] * (sun_col - img)

    # Silky sunset clouds mid-sky (v=0.34..0.62)
    n = _fbm(h, w, octaves=5, seed=7, base=3)
    n2 = _fbm(h, w, octaves=4, seed=13, base=5)
    cloud = np.clip((n * 1.25 + n2 * 0.55 - 0.58) * 1.9, 0, 1)
    band = np.exp(-((v - 0.50) / 0.14) ** 2)
    cloud = cloud * band
    rim = np.exp(-(d / 0.38) ** 2)
    under = np.clip(1.0 - (v - 0.48) / 0.12, 0, 1)
    coral = _hex('#E59476'); cream = _hex('#FBEAD0'); gold = _hex('#FFD394')
    cloud_col = coral[None, None, :] * under[..., None] + cream[None, None, :] * (1 - under[..., None])
    cloud_col = cloud_col + rim[..., None] * (gold - cloud_col) * 0.65
    img = img * (1 - cloud[..., None] * 0.72) + cloud_col * (cloud[..., None] * 0.72)

    # Smooth sea atmospheric glow below horizon
    sea_mask = (v >= horizon).astype(np.float32)
    track = np.exp(-((u - su) / 0.10) ** 2) * sea_mask * np.clip(1 - (v - horizon) / 0.35, 0, 1)
    amber = _hex('#E8A664')
    img = img + track[..., None] * (amber - img) * 0.45

    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB')

def _sobel(a):
    a = a.astype(np.float32)
    gx = np.zeros_like(a); gy = np.zeros_like(a)
    gx[:, 1:-1] = a[:, 2:] - a[:, :-2]
    gy[1:-1, :] = a[2:, :] - a[:-2, :]
    return np.sqrt(gx * gx + gy * gy)

def make_monumental_2f_regatta_oil_tex(w=2048, h=1024):
    # Canvas weave
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    weave = (np.sin(xx * 1.7) * np.sin(yy * 1.7) * 0.5 + 0.5) * 0.06 + 0.94
    linen = _hex('#E8DCC0')

    # Sky gradient
    v = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    u = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    horizon = 0.62
    sky = _grad([(0.0, '#3A4A6B'), (0.25, '#7A6E7E'), (0.45, '#C98A6A'),
                 (0.60, '#F0C48A'), (0.62, '#F0C48A')], h)
    sea = _grad([(0.62, '#2E6B6E'), (1.0, '#1B3F4A')], h)
    img = np.where(v < horizon, sky, sea)
    img = np.broadcast_to(img[:, None, :], (h, w, 3)).copy()

    # Sun glow
    su, sv = 0.62, 0.50
    d = np.sqrt((u - su) ** 2 + ((v - sv) * 2.0) ** 2)
    glow = np.exp(-(d / 0.18) ** 2)
    img = img + glow[..., None] * (_hex('#FFD9A0') - img) * 0.7

    # Clouds
    n = _fbm(h, w, octaves=5, seed=3, base=4)
    cloud = np.clip((n - 0.5) * 2.5, 0, 1) * np.exp(-((v - 0.42) / 0.18) ** 2)
    img = img * (1 - cloud[..., None] * 0.6) + _hex('#E8C9A8') * (cloud[..., None] * 0.6)

    # Headland silhouette left
    head_x = np.clip((0.28 - u) / 0.28, 0, 1)
    head_top = horizon - 0.10 - 0.06 * np.sin(u * 40) * head_x
    head = ((v > head_top) & (v < horizon) & (u < 0.28)).astype(np.float32)
    head = np.asarray(Image.fromarray((head * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)), dtype=np.float32) / 255
    img = img * (1 - head[..., None]) + _hex('#2A2E3A') * head[..., None]

    # Sloops (3 hulls with sails)
    def sloop(cx, cy, s, tilt=0.0):
        m = np.zeros((h, w), dtype=np.float32)
        # hull
        hw = 0.05 * s; hh = 0.012 * s
        hull = ((np.abs(u - cx) < hw) & (np.abs(v - cy) < hh)).astype(np.float32)
        # sail (triangle)
        sail_h = 0.14 * s; sail_w = 0.06 * s
        sx = (u - cx) / sail_w
        sy = (cy - v) / sail_h
        sail = ((sx > -0.2) & (sx < 1.0) & (sy > 0) & (sy < 1) & (sx < 1 - sy * 0.6)).astype(np.float32)
        return hull, sail

    for (cx, cy, s) in [(0.42, 0.66, 1.0), (0.58, 0.68, 0.85), (0.74, 0.67, 0.9)]:
        hull, sail = sloop(cx, cy, s)
        img = img * (1 - hull[..., None] * 0.9) + _hex('#3A2A22') * (hull[..., None] * 0.9)
        img = img * (1 - sail[..., None] * 0.92) + _hex('#F2E8D0') * (sail[..., None] * 0.92)

    # Impasto via Sobel raking highlight
    lum = img.mean(axis=2)
    sob = _sobel(lum)
    sob = sob / (sob.max() + 1e-6)
    img = img + sob[..., None] * 22.0

    # Canvas weave multiply
    img = img * weave[..., None] + linen * (1 - weave[..., None]) * 0.15

    # Frame: passe-partout + gold bevel
    border = int(min(w, h) * 0.045)
    gold = _hex('#A68952')
    mat = _hex('#F4EFE4')
    img[:border, :] = mat; img[-border:, :] = mat
    img[:, :border] = mat; img[:, -border:] = mat
    b2 = max(2, border // 6)
    for sl in [slice(border, border + b2), slice(-border - b2, -border)]:
        img[sl, :] = gold
        img[:, sl] = gold

    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB')
