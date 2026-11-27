"""Old-money AD100 surface textures: marmorino boiserie, salon rug, aubusson, headland rock."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def _fbm(size, octaves=5, seed=0, persistence=0.55):
    rng = np.random.default_rng(seed)
    out = np.zeros((size, size), np.float32)
    amp = 1.0; tot = 0.0
    for o in range(octaves):
        g = max(2, size >> (octaves - o - 1))
        base = rng.random((g, g)).astype(np.float32)
        img = Image.fromarray((base * 255).astype(np.uint8)).resize((size, size), Image.BICUBIC)
        out += amp * (np.asarray(img, np.float32) / 255.0)
        tot += amp; amp *= persistence
    return out / tot

def _lerp(c0, c1, t):
    c0 = np.array(c0, np.float32); c1 = np.array(c1, np.float32)
    return c0 + (c1 - c0) * t[..., None]

def _to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

def make_marmorino_boiserie_tex(size: int = 1024) -> Image.Image:
    n = size
    cloud = _fbm(n, 6, 11, 0.6)
    cloud2 = _fbm(n, 4, 23, 0.5)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n
    # vertical trowel polish bands
    band = 0.5 + 0.5 * np.sin(xx * np.pi * 9 + cloud2 * 3.0)
    band = band ** 2
    t = np.clip(0.35 * cloud + 0.25 * cloud2 + 0.25 * band + 0.15 * yy, 0, 1)
    base = _lerp((0xDD, 0xD2, 0xC0), (0xCB, 0xBA, 0xA2), t)
    # mineral speckle
    rng = np.random.default_rng(7)
    speck = rng.random((n, n)).astype(np.float32)
    speck = np.asarray(Image.fromarray((speck * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255.0
    base *= (0.94 + 0.12 * speck[..., None])
    img = _to_img(base)
    d = ImageDraw.Draw(img)
    groove = (0xB0, 0x9E, 0x84); champ = (0xC7, 0xAD, 0x7B)
    # classical boiserie panel: outer frame + inner recessed panel
    def panel(x0, y0, x1, y1, w):
        d.rectangle([x0, y0, x1, y1], outline=groove, width=w)
        d.rectangle([x0 + w, y0 + w, x1 - w, y1 - w], outline=champ, width=1)
        d.rectangle([x0 + w + 2, y0 + w + 2, x1 - w - 2, y1 - w - 2], outline=groove, width=1)
    m = int(n * 0.06)
    panel(m, m, n - m, n - m, 3)
    im = int(n * 0.16)
    panel(im, im, n - im, n - im, 2)
    # vertical stile grooves
    for fx in (0.5,):
        x = int(n * fx)
        d.line([(x, m), (x, n - m)], fill=groove, width=2)
        d.line([(x + 2, m), (x + 2, n - m)], fill=champ, width=1)
    return img.filter(ImageFilter.GaussianBlur(0.4))

def make_handknotted_salon_rug_tex(size: int = 2048) -> Image.Image:
    n = size
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n
    abrash = _fbm(n, 5, 41, 0.55)
    # horizontal silk abrash striations
    stri = 0.5 + 0.5 * np.sin(yy * np.pi * 60 + abrash * 6.0)
    stri = stri ** 3
    knot = _fbm(n, 3, 91, 0.5)
    t = np.clip(0.45 * abrash + 0.35 * stri + 0.2 * knot, 0, 1)
    field = _lerp((0xE4, 0xDB, 0xCA), (0xD8, 0xCC, 0xB6), t)
    # fine knot grain
    rng = np.random.default_rng(3)
    grain = rng.random((n, n)).astype(np.float32)
    grain = np.asarray(Image.fromarray((grain * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5)), np.float32) / 255.0
    field *= (0.95 + 0.1 * grain[..., None])
    img = _to_img(field)
    d = ImageDraw.Draw(img)
    outer = int(n * 0.09)
    taupe = (0x6A, 0x5D, 0x4D); brass = (0xB4, 0x97, 0x62); oxblood = (0x65, 0x2C, 0x39)
    # outer taupe band
    d.rectangle([0, 0, n - 1, n - 1], outline=taupe, width=outer)
    # brass fretwork inner band
    bw = max(4, int(n * 0.012))
    d.rectangle([outer, outer, n - outer, n - outer], outline=brass, width=bw)
    # geometric fretwork ticks
    step = max(8, n // 64)
    for i in range(outer, n - outer, step):
        d.line([(i, outer), (i, outer + bw)], fill=brass, width=1)
        d.line([(i, n - outer - bw), (i, n - outer)], fill=brass, width=1)
        d.line([(outer, i), (outer + bw, i)], fill=brass, width=1)
        d.line([(n - outer - bw, i), (n - outer, i)], fill=brass, width=1)
    # oxblood pinstripe
    pin = outer + bw + 2
    d.rectangle([pin, pin, n - pin, n - pin], outline=oxblood, width=2)
    # corner medallions
    cm = int(n * 0.055)
    for cx, cy in [(outer + cm, outer + cm), (n - outer - cm, outer + cm),
                   (outer + cm, n - outer - cm), (n - outer - cm, n - outer - cm)]:
        d.ellipse([cx - cm // 2, cy - cm // 2, cx + cm // 2, cy + cm // 2], outline=brass, width=2)
        d.ellipse([cx - cm // 4, cy - cm // 4, cx + cm // 4, cy + cm // 4], outline=oxblood, width=1)
    return img.filter(ImageFilter.GaussianBlur(0.3))

def make_loft_aubusson_rug_tex(size: int = 1024) -> Image.Image:
    n = size
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n
    weave = _fbm(n, 5, 61, 0.55)
    pile = 0.5 + 0.5 * np.sin(xx * np.pi * 80 + weave * 4) * np.sin(yy * np.pi * 80 + weave * 4)
    t = np.clip(0.6 * weave + 0.4 * pile, 0, 1)
    field = _lerp((0xDE, 0xD3, 0xBE), (0xCF, 0xC2, 0xA8), t)
    img = _to_img(field)
    d = ImageDraw.Draw(img)
    olive = (0x76, 0x72, 0x5B); umber = (0x5A, 0x4A, 0x3A)
    b1 = int(n * 0.05); b2 = int(n * 0.085)
    d.rectangle([0, 0, n - 1, n - 1], outline=umber, width=b1)
    d.rectangle([b1, b1, n - b1, n - b1], outline=olive, width=max(3, b1 // 2))
    d.rectangle([b2, b2, n - b2, n - b2], outline=umber, width=2)
    # subtle woven relief dots
    step = max(6, n // 96)
    for y in range(b2 + 4, n - b2 - 4, step):
        for x in range(b2 + 4, n - b2 - 4, step):
            if ((x // step) + (y // step)) % 2 == 0:
                d.point((x, y), fill=(0xC8, 0xBC, 0xA2))
    return img.filter(ImageFilter.GaussianBlur(0.5))

def make_headland_rock_tex(size: int = 512) -> Image.Image:
    n = size
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / n
    strata = _fbm(n, 6, 13, 0.6)
    # horizontal strata bands
    band = 0.5 + 0.5 * np.sin(yy * np.pi * 14 + strata * 5.0)
    band = band ** 2
    detail = _fbm(n, 4, 77, 0.5)
    t = np.clip(0.5 * band + 0.3 * strata + 0.2 * detail, 0, 1)
    c0 = np.array((0x69, 0x5C, 0x52), np.float32)
    c1 = np.array((0x4D, 0x45, 0x40), np.float32)
    c2 = np.array((0x8B, 0x75, 0x62), np.float32)
    mix1 = _lerp(c0, c1, np.clip(t * 1.4, 0, 1))
    mix2 = _lerp(mix1, c2, np.clip((band - 0.5) * 1.6, 0, 1))
    # cracks
    rng = np.random.default_rng(5)
    crack = rng.random((n, n)).astype(np.float32)
    crack = np.asarray(Image.fromarray((crack * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255.0
    crack = np.clip((crack - 0.55) * 3.0, 0, 1)
    mix2 *= (1.0 - 0.35 * crack[..., None])
    return _to_img(mix2)
