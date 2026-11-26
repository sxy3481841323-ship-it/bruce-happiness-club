#!/usr/bin/env python3
"""
Build Club Warehouse Supermarket 3D glTF 2.0 binary (assets/models/warehouse_club.glb)
for CLB·02「会员制仓储大超市」— Sam's Club / Costco boutique club aesthetic.

Coordinate system: Y-up, interior walkable terrazzo floor strictly at y = 0.0.
Scale: 4 units = 1 meter (aligned with coastal_cafe.glb).
Format: Standard uncompressed glTF 2.0 binary (.glb), <= 5.5 MB.
"""

import io
import json
import math
import os
import struct
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT_DIR, "assets", "models", "warehouse_club.glb")


# ---------------------------------------------------------------------------
# Procedural Texture Generators
# ---------------------------------------------------------------------------

def encode_pil_image(img: Image.Image, fmt="JPEG", quality=84) -> tuple[bytes, str]:
    buf = io.BytesIO()
    if fmt.upper() == "PNG":
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue(), "image/png"
    img.convert("RGB").save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue(), "image/jpeg"


def load_font(size: int):
    candidates = [
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def make_terrazzo_tex(size=1024) -> Image.Image:
    """Warm light-gray honed terrazzo floor with fine mineral speckles & expansion joints."""
    rng = np.random.default_rng(2026)
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)

    cloud = (
        np.sin(x * 0.012) * np.cos(y * 0.015) * 4.5
        + np.sin(x * 0.037 + y * 0.025) * 2.8
        + rng.normal(0, 2.0, (size, size))
    )
    r = np.clip(212 + cloud, 192, 232)
    g = np.clip(210 + cloud, 190, 230)
    b = np.clip(204 + cloud * 0.95, 184, 224)

    arr = np.stack([r, g, b], axis=-1).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    d = ImageDraw.Draw(img)

    # Mineral aggregate chips (cream, charcoal, warm taupe, subtle champagne flecks)
    chip_colors = [
        (168, 165, 158),
        (134, 132, 128),
        (235, 232, 224),
        (196, 184, 162),
        (96, 98, 102),
        (220, 206, 180),
    ]
    for _ in range(2600):
        cx = int(rng.integers(0, size))
        cy = int(rng.integers(0, size))
        rx = int(rng.integers(2, 6))
        ry = int(rng.integers(2, 5))
        col = chip_colors[int(rng.integers(0, len(chip_colors)))]
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)

    # Subtle expansion joint grid (2x2 slabs per tile)
    joint_col = (152, 150, 146)
    for pos in (0, size // 2):
        d.line([(pos, 0), (pos, size)], fill=joint_col, width=4)
        d.line([(0, pos), (size, pos)], fill=joint_col, width=4)

    return img.filter(ImageFilter.GaussianBlur(radius=0.35))


def make_stainless_tex(size=512) -> Image.Image:
    """Fine brushed stainless steel texture."""
    rng = np.random.default_rng(31)
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    streaks = rng.normal(0, 7.0, (size, 1)) + np.sin(y * 0.6) * 2.5
    fine = rng.normal(0, 2.5, (size, size))
    grad = np.sin(x * 0.012) * 8.0
    base = np.clip(204 + streaks + fine + grad, 165, 238)
    arr = np.stack([base * 0.98, base * 0.99, np.clip(base * 1.02, 0, 255)], axis=-1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def make_pallet_wood_tex(size=512) -> Image.Image:
    """Natural raw pine wood pallet slats with grain and plank seams."""
    rng = np.random.default_rng(88)
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    grain = (
        np.sin(y * 0.30 + np.sin(x * 0.04) * 2.5) * 9.0
        + np.sin(y * 0.95 + x * 0.02) * 4.0
        + rng.normal(0, 3.0, (size, size))
    )
    plank_idx = (y // 85).astype(np.int32)
    plank_shift = ((plank_idx * 17) % 19) - 9.0
    seam = (y.astype(np.int32) % 85) < 4

    r = np.clip(186 + grain + plank_shift, 130, 224)
    g = np.clip(154 + grain * 0.88 + plank_shift * 0.85, 102, 194)
    b = np.clip(112 + grain * 0.72 + plank_shift * 0.7, 74, 152)
    r[seam] *= 0.45
    g[seam] *= 0.45
    b[seam] *= 0.45
    arr = np.stack([r, g, b], axis=-1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def make_walnut_tex(size=512) -> Image.Image:
    """Rich dark walnut timber for shelving decks & tasting cutting board."""
    rng = np.random.default_rng(64)
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    grain = (
        np.sin(x * 0.22 + np.sin(y * 0.03) * 2.4) * 8.0
        + np.sin(x * 0.65 + y * 0.015) * 3.5
        + rng.normal(0, 2.2, (size, size))
    )
    r = np.clip(92 + grain, 56, 128)
    g = np.clip(64 + grain * 0.8, 38, 96)
    b = np.clip(46 + grain * 0.65, 26, 72)
    return Image.fromarray(np.stack([r, g, b], axis=-1).astype(np.uint8), "RGB")


def make_marble_tex(w=1024, h=512) -> Image.Image:
    """Calacatta white marble with warm champagne-gray veining for Tasting Bar."""
    rng = np.random.default_rng(77)
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    u = x / w
    v = y / h
    base = np.zeros((h, w, 3), dtype=np.float32)
    base[:, :, 0] = 244
    base[:, :, 1] = 242
    base[:, :, 2] = 238
    cloud = np.sin(u * 8.0 + np.cos(v * 5.5) * 1.4) * 4.0 + rng.normal(0, 1.0, (h, w))
    for c in range(3):
        base[:, :, c] += cloud
    for idx in range(7):
        phase = idx * 1.2
        freq = 3.0 + idx * 0.65
        curve = np.sin(u * freq + v * 4.8 + phase) + 0.32 * np.sin(u * 12.0 - v * 8.5 + phase * 2)
        vein = np.exp(-((curve * 10.5) ** 2))
        gold_mix = 1.0 if idx % 3 == 0 else 0.3
        base[:, :, 0] -= vein * (26 - 9 * gold_mix)
        base[:, :, 1] -= vein * (28 - 4 * gold_mix)
        base[:, :, 2] -= vein * (32 + 5 * gold_mix)
    return Image.fromarray(np.clip(base, 145, 252).astype(np.uint8), "RGB")


def make_burgundy_plaid_tex(size=512) -> Image.Image:
    """Luxury burgundy tartan plaid cushion texture echoing Bruce's silk scarf."""
    img = Image.new("RGB", (size, size), (118, 24, 38))
    d = ImageDraw.Draw(img)
    step = 64
    # Deep wine broad bands
    for p in range(0, size, step):
        d.rectangle([p, 0, p + 22, size], fill=(86, 16, 28))
        d.rectangle([0, p, size, p + 22], fill=(86, 16, 28))
    # Darker burgundy intersections
    for px in range(0, size, step):
        for py in range(0, size, step):
            d.rectangle([px, py, px + 22, py + 22], fill=(62, 10, 20))
    # Fine champagne-gold & cream pinstripes
    for p in range(0, size, step):
        d.line([(p + 38, 0), (p + 38, size)], fill=(224, 192, 126), width=3)
        d.line([(0, p + 38), (size, p + 38)], fill=(224, 192, 126), width=3)
        d.line([(p + 46, 0), (p + 46, size)], fill=(244, 232, 206), width=2)
        d.line([(0, p + 46), (size, p + 46)], fill=(244, 232, 206), width=2)
    # Soft woven fabric noise
    rng = np.random.default_rng(12)
    arr = np.array(img, dtype=np.float32) + rng.normal(0, 3.0, (size, size, 3))
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def make_cardboard_tex(size=512) -> Image.Image:
    """Kraft corrugated warehouse bulk box with clean printed club markings."""
    rng = np.random.default_rng(404)
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    fiber = np.sin(y * 1.1) * 3.0 + rng.normal(0, 3.5, (size, size))
    r = np.clip(182 + fiber, 152, 206)
    g = np.clip(144 + fiber * 0.85, 118, 168)
    b = np.clip(102 + fiber * 0.7, 78, 126)
    img = Image.fromarray(np.stack([r, g, b], axis=-1).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img)
    # Packing tape strip & clean club warehouse stencil
    d.rectangle([0, 0, size, 42], fill=(166, 130, 88))
    d.rectangle([28, 76, size - 28, size - 68], outline=(62, 46, 32), width=4)
    f_big = load_font(42)
    f_sm = load_font(22)
    d.text((54, 120), "ELOWEN PANTRY", fill=(48, 36, 26), font=f_big)
    d.text((54, 184), "ORGANIC HARVEST · LOT 02", fill=(66, 48, 34), font=f_sm)
    # Minimal barcode bars
    bx = 54
    for i in range(28):
        bw = 4 if (i % 3 == 0) else 2
        d.rectangle([bx, 310, bx + bw, 385], fill=(44, 34, 24))
        bx += bw + (4 if i % 2 == 0 else 6)
    return img


def make_product_pack_tex(size=512) -> Image.Image:
    """Premium pet freeze-dried treat & gourmet club packaging label."""
    img = Image.new("RGB", (size, size), (24, 26, 32))
    d = ImageDraw.Draw(img)
    # Gold top & bottom bands
    d.rectangle([0, 0, size, 58], fill=(214, 178, 108))
    d.rectangle([0, size - 52, size, size], fill=(214, 178, 108))
    # Burgundy accent sash
    d.rectangle([0, 170, size, 276], fill=(128, 28, 44))
    f_title = load_font(44)
    f_sub = load_font(26)
    d.text((48, 92), "BRUCE PANTRY", fill=(246, 236, 212), font=f_title)
    d.text((48, 198), "FREEZE-DRIED", fill=(255, 244, 218), font=f_title)
    d.text((48, 312), "WILD KING SALMON", fill=(224, 192, 126), font=f_sub)
    d.text((48, 360), "GRASS-FED RESERVE 1.5KG", fill=(218, 214, 206), font=f_sub)
    return img


def make_sign_board_tex(w=1024, h=256, title="ELOWEN MARKET · 02", subtitle="ORGANIC PROVISIONS · RAW TONIC GALLERY") -> Image.Image:
    """Erewhon-inspired forest-bronze & ivory signage."""
    img = Image.new("RGB", (w, h), (24, 30, 26))
    d = ImageDraw.Draw(img)
    # Fine double gold border
    d.rectangle([10, 10, w - 11, h - 11], outline=(218, 184, 114), width=4)
    d.rectangle([20, 20, w - 21, h - 21], outline=(130, 108, 66), width=2)
    f_t = load_font(50)
    f_s = load_font(26)
    d.text((48, 54), title, fill=(244, 224, 172), font=f_t)
    d.text((50, 146), subtitle, fill=(214, 208, 196), font=f_s)
    # Decorative gold pill badge on right
    d.rounded_rectangle([w - 210, 56, w - 42, 118], radius=14, fill=(42, 54, 44), outline=(224, 192, 126), width=3)
    d.text((w - 186, 72), "ORGANIC", fill=(255, 245, 222), font=load_font(26))
    return img


def make_price_tag_tex(w=512, h=256, label="DRY-AGED WAGYU M9", price="$ 68") -> Image.Image:
    """Restrained organic market placard."""
    img = Image.new("RGB", (w, h), (24, 28, 25))
    d = ImageDraw.Draw(img)
    d.rectangle([6, 6, w - 7, h - 7], outline=(212, 186, 128), width=4)
    d.rectangle([6, 6, w - 7, 74], fill=(212, 186, 128))
    d.text((26, 22), "DAILY HARVEST", fill=(24, 28, 25), font=load_font(34))
    d.text((26, 98), label, fill=(244, 238, 224), font=load_font(30))
    d.text((26, 154), price, fill=(238, 204, 128), font=load_font(56))
    return img


def make_wagyu_salmon_tex(size=512, mode="salmon") -> Image.Image:
    """Rich coral salmon stripes or M9 Wagyu marbled beef texture."""
    rng = np.random.default_rng(707 if mode == "salmon" else 808)
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    if mode == "salmon":
        # Coral orange flesh with diagonal creamy fat striations
        stripe = np.exp(-((np.sin((x * 0.08 + y * 0.04) + np.sin(y * 0.03) * 1.2)) ** 2) * 14.0)
        noise = rng.normal(0, 4.0, (size, size))
        r = np.clip(234 * (1 - stripe * 0.06) + 248 * stripe * 0.25 + noise, 180, 255)
        g = np.clip(116 * (1 - stripe * 0.35) + 232 * stripe * 0.55 + noise, 85, 246)
        b = np.clip(82 * (1 - stripe * 0.4) + 216 * stripe * 0.6 + noise, 58, 234)
    else:
        # Deep ruby Wagyu with lacy white intramuscular marbling
        web = (
            np.sin(x * 0.06 + np.cos(y * 0.05) * 2.2)
            * np.cos(y * 0.07 - np.sin(x * 0.04) * 1.8)
        )
        marble = np.clip(np.exp(-((web * 5.2) ** 2)) * 0.85, 0.0, 0.85)
        noise = rng.normal(0, 4.0, (size, size))
        r = np.clip(148 * (1 - marble) + 242 * marble + noise, 90, 250)
        g = np.clip(38 * (1 - marble) + 228 * marble + noise, 24, 240)
        b = np.clip(42 * (1 - marble) + 220 * marble + noise, 26, 232)
    return Image.fromarray(np.stack([r, g, b], axis=-1).astype(np.uint8), "RGB")


def make_concrete_wall_tex(size=512) -> Image.Image:
    """Warm architectural poured concrete wall with subtle panel seams."""
    rng = np.random.default_rng(512)
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    cloud = np.sin(x * 0.018) * np.cos(y * 0.022) * 5.0 + rng.normal(0, 3.0, (size, size))
    r = np.clip(198 + cloud, 174, 220)
    g = np.clip(196 + cloud, 172, 218)
    b = np.clip(192 + cloud, 168, 214)
    seam = ((x.astype(np.int32) % 256) < 3) | ((y.astype(np.int32) % 256) < 3)
    r[seam] -= 22
    g[seam] -= 22
    b[seam] -= 22
    return Image.fromarray(np.stack([r, g, b], axis=-1).clip(0, 255).astype(np.uint8), "RGB")


# ---------------------------------------------------------------------------
# Clean Geometry Builder (Outward CCW Normals Guaranteed)
# ---------------------------------------------------------------------------

class MeshBuilder:
    def __init__(self, name: str, material_idx: int):
        self.name = name
        self.material_idx = material_idx
        self.positions = []
        self.normals = []
        self.uvs = []
        self.indices = []

    def add_tri_raw(self, p0, p1, p2, uv0=(0, 0), uv1=(1, 0), uv2=(1, 1), n0=None, n1=None, n2=None):
        e1 = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
        e2 = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
        nx = e1[1] * e2[2] - e1[2] * e2[1]
        ny = e1[2] * e2[0] - e1[0] * e2[2]
        nz = e1[0] * e2[1] - e1[1] * e2[0]
        ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
        fn = (nx / ln, ny / ln, nz / ln)
        base = len(self.positions)
        self.positions.extend([p0, p1, p2])
        self.normals.extend([n0 or fn, n1 or fn, n2 or fn])
        self.uvs.extend([uv0, uv1, uv2])
        self.indices.extend([base, base + 1, base + 2])

    def add_quad(self, p0, p1, p2, p3, uv_scale=(1.0, 1.0), flip=False):
        su, sv = uv_scale
        u0, u1, u2, u3 = (0.0, 0.0), (su, 0.0), (su, sv), (0.0, sv)
        if flip:
            self.add_tri_raw(p0, p2, p1, u0, u2, u1)
            self.add_tri_raw(p0, p3, p2, u0, u3, u2)
        else:
            self.add_tri_raw(p0, p1, p2, u0, u1, u2)
            self.add_tri_raw(p0, p2, p3, u0, u2, u3)

    def add_box(self, cx, cy, cz, sx, sy, sz, uv_tile=0.0, rot_y=0.0):
        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
        c, s = math.cos(rot_y), math.sin(rot_y)

        def xf(lx, ly, lz):
            return (cx + lx * c + lz * s, cy + ly, cz - lx * s + lz * c)

        faces = [
            (xf(-hx, -hy, hz), xf(hx, -hy, hz), xf(hx, hy, hz), xf(-hx, hy, hz), (sx, sy)),
            (xf(hx, -hy, -hz), xf(-hx, -hy, -hz), xf(-hx, hy, -hz), xf(hx, hy, -hz), (sx, sy)),
            (xf(hx, -hy, hz), xf(hx, -hy, -hz), xf(hx, hy, -hz), xf(hx, hy, hz), (sz, sy)),
            (xf(-hx, -hy, -hz), xf(-hx, -hy, hz), xf(-hx, hy, hz), xf(-hx, hy, -hz), (sz, sy)),
            (xf(-hx, hy, hz), xf(hx, hy, hz), xf(hx, hy, -hz), xf(-hx, hy, -hz), (sx, sz)),
            (xf(-hx, -hy, -hz), xf(hx, -hy, -hz), xf(hx, -hy, hz), xf(-hx, -hy, hz), (sx, sz)),
        ]
        for p0, p1, p2, p3, (w, h) in faces:
            uvs = (w / uv_tile, h / uv_tile) if uv_tile > 0 else (1.0, 1.0)
            self.add_quad(p0, p1, p2, p3, uv_scale=uvs)

    def add_cylinder(self, cx, y0, cz, r_bot, r_top, height, segs=14, rot_x=0.0, rot_z=0.0, cap_top=True, cap_bot=True):
        y1 = y0 + height
        cx_r, sx_r = math.cos(rot_x), math.sin(rot_x)
        cz_r, sz_r = math.cos(rot_z), math.sin(rot_z)

        def xf_pt(px, py, pz):
            lx, ly, lz = px, py - y0, pz
            ly1 = ly * cx_r - lz * sx_r
            lz1 = ly * sx_r + lz * cx_r
            lx2 = lx * cz_r - ly1 * sz_r
            ly2 = lx * sz_r + ly1 * cz_r
            return (cx + lx2, y0 + ly2, cz + lz1)

        def xf_n(nx, ny, nz):
            ny1 = ny * cx_r - nz * sx_r
            nz1 = ny * sx_r + nz * cx_r
            nx2 = nx * cz_r - ny1 * sz_r
            ny2 = nx * sz_r + ny1 * cz_r
            ln = math.sqrt(nx2 * nx2 + ny2 * ny2 + nz1 * nz1) or 1.0
            return (nx2 / ln, ny2 / ln, nz1 / ln)

        slope = (r_bot - r_top) / max(1e-5, height)
        for i in range(segs):
            a0 = (i / segs) * math.tau
            a1 = ((i + 1) / segs) * math.tau
            c0, s0 = math.cos(a0), math.sin(a0)
            c1, s1 = math.cos(a1), math.sin(a1)

            b0 = xf_pt(r_bot * c0, y0, r_bot * s0)
            b1 = xf_pt(r_bot * c1, y0, r_bot * s1)
            t1 = xf_pt(r_top * c1, y1, r_top * s1)
            t0 = xf_pt(r_top * c0, y1, r_top * s0)

            n0 = xf_n(c0, slope, s0)
            n1 = xf_n(c1, slope, s1)
            self.add_tri_raw(b1, b0, t0, (1 - i / segs, 0), (1 - (i + 1) / segs, 0), (1 - (i + 1) / segs, 1), n1, n0, n0)
            self.add_tri_raw(b1, t0, t1, (1 - i / segs, 0), (1 - (i + 1) / segs, 1), (1 - i / segs, 1), n1, n0, n1)

            if cap_top and r_top > 1e-5:
                tc = xf_pt(0, y1, 0)
                nt = xf_n(0, 1, 0)
                self.add_tri_raw(tc, t1, t0, (0.5, 0.5), (0.5 + 0.5 * c1, 0.5 + 0.5 * s1), (0.5 + 0.5 * c0, 0.5 + 0.5 * s0), nt, nt, nt)
            if cap_bot and r_bot > 1e-5:
                bc = xf_pt(0, y0, 0)
                nb = xf_n(0, -1, 0)
                self.add_tri_raw(bc, b0, b1, (0.5, 0.5), (0.5 + 0.5 * c0, 0.5 + 0.5 * s0), (0.5 + 0.5 * c1, 0.5 + 0.5 * s1), nb, nb, nb)

    def add_lathe(self, cx, y0, cz, profile, segs=18):
        for j in range(len(profile) - 1):
            r0, dy0 = profile[j]
            r1, dy1 = profile[j + 1]
            dr, dy = r1 - r0, dy1 - dy0
            nl = math.sqrt(dr * dr + dy * dy) or 1.0
            nr, ny = dy / nl, -dr / nl
            for i in range(segs):
                a0 = (i / segs) * math.tau
                a1 = ((i + 1) / segs) * math.tau
                c0, s0 = math.cos(a0), math.sin(a0)
                c1, s1 = math.cos(a1), math.sin(a1)
                p00 = (cx + r0 * c0, y0 + dy0, cz + r0 * s0)
                p01 = (cx + r0 * c1, y0 + dy0, cz + r0 * s1)
                p10 = (cx + r1 * c0, y0 + dy1, cz + r1 * s0)
                p11 = (cx + r1 * c1, y0 + dy1, cz + r1 * s1)
                n0 = (nr * c0, ny, nr * s0)
                n1 = (nr * c1, ny, nr * s1)
                if r0 > 1e-5 or r1 > 1e-5:
                    if r0 <= 1e-5:
                        self.add_tri_raw(p00, p11, p10, (0.5, 0), (1, 1), (0, 1), n0, n1, n0)
                    elif r1 <= 1e-5:
                        self.add_tri_raw(p01, p00, p10, (1, 0), (0, 0), (0.5, 1), n1, n0, n0)
                    else:
                        self.add_tri_raw(p01, p00, p10, (1, 0), (0, 0), (0, 1), n1, n0, n0)
                        self.add_tri_raw(p01, p10, p11, (1, 0), (0, 1), (1, 1), n1, n0, n1)

    def add_strut(self, p0, p1, radius=0.06, segs=6):
        """Cylinder strut between two 3D points p0 and p1."""
        v = np.subtract(p1, p0)
        length = float(np.linalg.norm(v))
        if length < 1e-5:
            return
        t = v / length
        up = np.array([0.0, 0.0, 1.0]) if abs(t[1]) > 0.92 else np.array([0.0, 1.0, 0.0])
        b = np.cross(t, up)
        b /= (np.linalg.norm(b) or 1.0)
        n = np.cross(b, t)
        ring0, ring1 = [], []
        for i in range(segs):
            ang = (i / segs) * math.tau
            d = math.cos(ang) * b + math.sin(ang) * n
            ring0.append((tuple((np.array(p0) + d * radius).tolist()), tuple(d.tolist())))
            ring1.append((tuple((np.array(p1) + d * radius).tolist()), tuple(d.tolist())))
        for i in range(segs):
            nxt = (i + 1) % segs
            a0, na0 = ring0[i]
            a1, na1 = ring0[nxt]
            b0, nb0 = ring1[i]
            b1, nb1 = ring1[nxt]
            self.add_tri_raw(a0, a1, b1, (0, 0), (1, 0), (1, 1), na0, na1, nb1)
            self.add_tri_raw(a0, b1, b0, (0, 0), (1, 1), (0, 1), na0, nb1, nb0)


# ---------------------------------------------------------------------------
# Scene Assembly: CLB·02 Club Warehouse Supermarket
# ---------------------------------------------------------------------------

def build_scene():
    materials = []
    textures = []
    images_data = []

    def add_tex(pil_img, fmt="JPEG", quality=84):
        raw, mime = encode_pil_image(pil_img, fmt=fmt, quality=quality)
        img_idx = len(images_data)
        images_data.append((raw, mime))
        tex_idx = len(textures)
        textures.append({"sampler": 0, "source": img_idx})
        return tex_idx

    def add_mat(name, base_color=(1, 1, 1, 1), roughness=0.55, metalness=0.0, tex_idx=None,
                emissive=None, double_sided=False, alpha_mode=None):
        idx = len(materials)
        pbr = {
            "baseColorFactor": [float(c) for c in base_color],
            "roughnessFactor": float(roughness),
            "metallicFactor": float(metalness),
        }
        if tex_idx is not None:
            pbr["baseColorTexture"] = {"index": tex_idx}
        mat = {"name": name, "pbrMetallicRoughness": pbr}
        if emissive is not None:
            mat["emissiveFactor"] = [float(c) for c in emissive]
        if double_sided:
            mat["doubleSided"] = True
        if alpha_mode:
            mat["alphaMode"] = alpha_mode
        materials.append(mat)
        return idx

    # Procedural Textures
    t_terrazzo = add_tex(make_terrazzo_tex(1024), "JPEG", 86)
    t_stainless = add_tex(make_stainless_tex(512), "JPEG", 84)
    t_pallet = add_tex(make_pallet_wood_tex(512), "JPEG", 84)
    t_walnut = add_tex(make_walnut_tex(512), "JPEG", 84)
    t_marble = add_tex(make_marble_tex(1024, 512), "JPEG", 86)
    t_plaid = add_tex(make_burgundy_plaid_tex(512), "JPEG", 86)
    t_cardboard = add_tex(make_cardboard_tex(512), "JPEG", 82)
    t_pack = add_tex(make_product_pack_tex(512), "JPEG", 84)
    t_sign_main = add_tex(make_sign_board_tex(1024, 256, "ELOWEN MARKET · 02", "ORGANIC PROVISIONS · RAW TONIC BAR"), "JPEG", 92)
    t_sign_fresh = add_tex(make_sign_board_tex(1024, 256, "COLD ORGANIC GALLERY", "WILD SALMON · DRY-AGED WAGYU · RAW DAIRY"), "JPEG", 92)
    t_price_wagyu = add_tex(make_price_tag_tex(512, 256, "DRY-AGED WAGYU & SALMON", "$ 68"), "JPEG", 90)
    t_price_treat = add_tex(make_price_tag_tex(512, 256, "BONE BROTH TREATS", "$ 28"), "JPEG", 90)
    t_salmon = add_tex(make_wagyu_salmon_tex(512, "salmon"), "JPEG", 88)
    t_wagyu = add_tex(make_wagyu_salmon_tex(512, "wagyu"), "JPEG", 88)
    t_concrete = add_tex(make_concrete_wall_tex(512), "JPEG", 88)

    # Materials
    m_floor = add_mat("TerrazzoFloor", (1, 1, 1, 1), roughness=0.22, metalness=0.04, tex_idx=t_terrazzo)
    m_concrete = add_mat("ConcreteWall", (1, 1, 1, 1), roughness=0.78, metalness=0.0, tex_idx=t_concrete)
    m_steel_dark = add_mat("DarkTrussSteel", (0.09, 0.10, 0.12, 1.0), roughness=0.38, metalness=0.78)
    m_roof_deck = add_mat("RoofDeckDark", (0.14, 0.15, 0.18, 1.0), roughness=0.68, metalness=0.24)
    m_skylight_sky = add_mat("SkylightSky", (0.80, 0.91, 1.0, 1.0), roughness=1.0, emissive=(0.76, 0.88, 1.0), double_sided=True)
    m_led_warm = add_mat("LinearLedWarm", (1.0, 0.96, 0.86, 1.0), roughness=0.2, emissive=(1.0, 0.94, 0.80))
    m_led_ice = add_mat("FreezerLedIce", (0.86, 0.96, 1.0, 1.0), roughness=0.2, emissive=(0.72, 0.92, 1.0))
    m_stainless = add_mat("BrushedStainless", (1, 1, 1, 1), roughness=0.26, metalness=0.88, tex_idx=t_stainless)
    m_chrome = add_mat("ChromeWire", (0.88, 0.90, 0.93, 1.0), roughness=0.18, metalness=0.94)
    m_copper = add_mat("SpunCopper", (0.82, 0.45, 0.24, 1.0), roughness=0.24, metalness=0.88)
    m_brass = add_mat("BrushedBrass", (0.86, 0.72, 0.44, 1.0), roughness=0.28, metalness=0.85)
    m_rack_orange = add_mat("ElowenForestBronze", (0.18, 0.22, 0.19, 1.0), roughness=0.44, metalness=0.35)
    m_pallet = add_mat("PalletWood", (1, 1, 1, 1), roughness=0.76, metalness=0.0, tex_idx=t_pallet)
    m_walnut = add_mat("DarkWalnut", (1, 1, 1, 1), roughness=0.46, metalness=0.04, tex_idx=t_walnut)
    m_marble = add_mat("CalacattaMarble", (1, 1, 1, 1), roughness=0.16, metalness=0.04, tex_idx=t_marble)
    m_plaid = add_mat("BurgundyPlaid", (1, 1, 1, 1), roughness=0.84, metalness=0.0, tex_idx=t_plaid)
    m_cardboard = add_mat("KraftCardboard", (1, 1, 1, 1), roughness=0.86, metalness=0.0, tex_idx=t_cardboard)
    m_pack = add_mat("PetTreatPack", (1, 1, 1, 1), roughness=0.42, metalness=0.06, tex_idx=t_pack)
    m_sign_main = add_mat("SignBoardMain", (1, 1, 1, 1), roughness=0.32, metalness=0.12, tex_idx=t_sign_main, emissive=(0.16, 0.14, 0.10))
    m_sign_fresh = add_mat("SignBoardFresh", (1, 1, 1, 1), roughness=0.32, metalness=0.12, tex_idx=t_sign_fresh, emissive=(0.12, 0.15, 0.18))
    m_price_wagyu = add_mat("PriceTagWagyu", (1, 1, 1, 1), roughness=0.35, tex_idx=t_price_wagyu)
    m_price_treat = add_mat("PriceTagTreat", (1, 1, 1, 1), roughness=0.35, tex_idx=t_price_treat)
    m_salmon = add_mat("SalmonFillet", (1, 1, 1, 1), roughness=0.34, metalness=0.02, tex_idx=t_salmon)
    m_wagyu = add_mat("WagyuBeef", (1, 1, 1, 1), roughness=0.38, metalness=0.02, tex_idx=t_wagyu)
    m_freezer_glass = add_mat("FreezerGlass", (0.86, 0.95, 1.0, 0.24), roughness=0.08, metalness=0.08, double_sided=True, alpha_mode="BLEND")
    m_milk_white = add_mat("OrganicMilk", (0.96, 0.96, 0.94, 1.0), roughness=0.22, metalness=0.02)
    m_milk_cap = add_mat("MilkCapBlue", (0.14, 0.42, 0.78, 1.0), roughness=0.34)
    m_cheese = add_mat("CheeseWheel", (0.92, 0.74, 0.30, 1.0), roughness=0.56)
    m_snack_yellow = add_mat("SnackCanYellow", (0.95, 0.74, 0.16, 1.0), roughness=0.36, metalness=0.10)
    m_baguette = add_mat("BaguetteCrust", (0.80, 0.54, 0.24, 1.0), roughness=0.68)
    m_wine_bottle = add_mat("WineBottleDark", (0.10, 0.16, 0.11, 1.0), roughness=0.16, metalness=0.06)
    m_ceramic = add_mat("TastingPlateWhite", (0.96, 0.95, 0.93, 1.0), roughness=0.14, metalness=0.02)
    m_herb_green = add_mat("GarnishHerb", (0.18, 0.52, 0.22, 1.0), roughness=0.62)
    m_freezer_back = add_mat("FreezerInterior", (0.90, 0.94, 0.97, 1.0), roughness=0.32, metalness=0.12)

    builders = {}

    def mb(name, mat_idx) -> MeshBuilder:
        key = (name, mat_idx)
        if key not in builders:
            builders[key] = MeshBuilder(name, mat_idx)
        return builders[key]

    # ------------------------------------------------------------------
    # 1. Architectural Shell: Terrazzo Floor (y=0.0), Walls, Steel Trusses, Skylights
    # ------------------------------------------------------------------
    b_floor = mb("TerrazzoFloor", m_floor)
    b_floor.add_quad((-13.6, 0.0, 18.2), (13.6, 0.0, 18.2), (13.6, 0.0, -19.8), (-13.6, 0.0, -19.8),
                     uv_scale=(27.2 / 6.0, 38.0 / 6.0))

    b_wall = mb("ConcreteWalls", m_concrete)
    # Left wall (X = -13.4, facing +X)
    b_wall.add_quad((-13.4, 0.0, 18.2), (-13.4, 0.0, -19.8), (-13.4, 17.6, -19.8), (-13.4, 17.6, 18.2), uv_scale=(6.0, 3.0))
    # Right wall (X = +13.4, facing -X)
    b_wall.add_quad((13.4, 0.0, -19.8), (13.4, 0.0, 18.2), (13.4, 17.6, 18.2), (13.4, 17.6, -19.8), uv_scale=(6.0, 3.0))
    # Back wall (Z = -19.6, facing +Z)
    b_wall.add_quad((-13.4, 0.0, -19.6), (13.4, 0.0, -19.6), (13.4, 17.6, -19.6), (-13.4, 17.6, -19.6), uv_scale=(4.5, 3.0))
    # Front wall behind camera (Z = +18.2, facing -Z)
    b_wall.add_quad((13.4, 0.0, 18.2), (-13.4, 0.0, 18.2), (-13.4, 17.6, 18.2), (13.4, 17.6, 18.2), uv_scale=(4.5, 3.0))

    # Rear architectural walnut ribbed feature wall behind Tasting Bar
    b_walnut = mb("DarkWalnutMillwork", m_walnut)
    for rx in np.linspace(-6.4, 6.4, 24):
        b_walnut.add_box(float(rx), 5.6, -19.35, 0.24, 11.2, 0.28, uv_tile=4.0)

    # Rear grand illuminated club sign ("CLUB WAREHOUSE · 02")
    b_steel = mb("DarkTrussSteel", m_steel_dark)
    b_sign_main = mb("SignBoardMain", m_sign_main)
    b_steel.add_box(0.0, 12.2, -19.25, 11.4, 2.95, 0.36)
    b_sign_main.add_quad((-5.5, 10.85, -19.04), (5.5, 10.85, -19.04), (5.5, 13.55, -19.04), (-5.5, 13.55, -19.04))

    # Rear frosted-glass stockroom double doors flanking the walnut feature wall
    b_stain = mb("BrushedStainless", m_stainless)
    for dx in (-9.6, 9.6):
        b_steel.add_box(dx, 4.4, -19.35, 3.4, 8.8, 0.26)
        b_stain.add_box(dx, 4.3, -19.24, 3.0, 8.4, 0.14)
        b_steel.add_box(dx, 4.3, -19.16, 0.10, 8.4, 0.12)
        # Stainless push bars
        b_stain.add_box(dx - 0.72, 3.8, -19.04, 1.1, 0.12, 0.18)
        b_stain.add_box(dx + 0.72, 3.8, -19.04, 1.1, 0.12, 0.18)

    # Exposed Steel Columns along Left & Right walls
    for cz in (-16.0, -9.5, -3.0, 3.5, 10.0, 16.0):
        for cx in (-13.0, 13.0):
            b_steel.add_box(cx, 8.6, cz, 0.72, 17.2, 0.72)
            # Base plate bolted to floor
            b_steel.add_box(cx, 0.14, cz, 1.10, 0.28, 1.10)

    # Roof Deck with 3 High Clerestory Skylight Wells (X: -4.8 .. +4.8)
    b_roof = mb("RoofDeckDark", m_roof_deck)
    b_sky = mb("SkylightSky", m_skylight_sky)
    # Left & Right solid roof bays
    b_roof.add_box(-9.2, 17.3, -0.8, 8.8, 0.5, 38.4)
    b_roof.add_box(9.2, 17.3, -0.8, 8.8, 0.5, 38.4)
    # Solid cross bands separating the 3 skylight bays along Z
    for sz, slen in [(-17.8, 4.4), (-7.2, 2.8), (2.2, 2.8), (13.4, 9.8)]:
        b_roof.add_box(0.0, 17.3, sz, 9.8, 0.5, slen)

    # 3 Recessed Skylight Wells with sky backdrop panels above
    skylight_bays = [(-15.6, -8.6), (-5.8, 0.8), (3.6, 8.6)]
    for z0, z1 in skylight_bays:
        zc = (z0 + z1) * 0.5
        zl = z1 - z0
        # Skylight shaft framing
        b_steel.add_box(-4.8, 17.55, zc, 0.24, 1.1, zl)
        b_steel.add_box(4.8, 17.55, zc, 0.24, 1.1, zl)
        b_steel.add_box(0.0, 17.55, z0, 9.8, 1.1, 0.24)
        b_steel.add_box(0.0, 17.55, z1, 9.8, 1.1, 0.24)
        # Mullion crossbars across skylight glass
        for mx in (-1.6, 1.6):
            b_steel.add_box(mx, 17.65, zc, 0.14, 0.18, zl)
        # Bright sky plate inside skylight well (facing downward -Y)
        b_sky.add_quad((-4.8, 18.05, z0), (4.8, 18.05, z0), (4.8, 18.05, z1), (-4.8, 18.05, z1))

    # Exposed Industrial Warren Steel Roof Trusses spanning X = -13.0 .. +13.0
    for tz in (-16.0, -9.5, -3.0, 3.5, 10.0):
        # Bottom chord (y=14.6) and top chord (y=16.6)
        b_steel.add_box(0.0, 14.6, tz, 26.2, 0.28, 0.30)
        b_steel.add_box(0.0, 16.6, tz, 26.2, 0.28, 0.30)
        # Diagonal Warren web struts
        xs = np.linspace(-12.6, 12.6, 11)
        for i in range(len(xs) - 1):
            x0, x1 = float(xs[i]), float(xs[i + 1])
            xm = (x0 + x1) * 0.5
            b_steel.add_strut((x0, 14.6, tz), (xm, 16.6, tz), radius=0.085, segs=6)
            b_steel.add_strut((xm, 16.6, tz), (x1, 14.6, tz), radius=0.085, segs=6)

    # Longitudinal purlins & suspended warm-white linear pendant light arrays
    b_led_warm = mb("LinearLedWarm", m_led_warm)
    for px in (-6.2, 0.0, 6.2):
        b_steel.add_box(px, 14.35, -2.5, 0.18, 0.18, 30.0)
        for lz in (-12.5, -6.0, 0.5, 7.0):
            # Suspension rods
            b_steel.add_cylinder(px, 12.85, lz - 1.6, 0.03, 0.03, 1.55, segs=6)
            b_steel.add_cylinder(px, 12.85, lz + 1.6, 0.03, 0.03, 1.55, segs=6)
            # Matte black linear luminaire housing + warm glowing bar
            b_steel.add_box(px, 12.85, lz, 0.44, 0.22, 4.2)
            b_led_warm.add_box(px, 12.72, lz, 0.32, 0.07, 4.0)

    # ------------------------------------------------------------------
    # 2. Left Side: Full-Row Cold-Chain Fresh Freezer Gallery (X: -12.6 .. -8.2)
    # ------------------------------------------------------------------
    b_fback = mb("FreezerInterior", m_freezer_back)
    b_led_ice = mb("FreezerLedIce", m_led_ice)
    b_fglass = mb("FreezerGlass", m_freezer_glass)
    b_salmon = mb("SalmonFillets", m_salmon)
    b_wagyu = mb("WagyuBeefBoxes", m_wagyu)
    b_milk = mb("OrganicMilkBottles", m_milk_white)
    b_mcap = mb("MilkCaps", m_milk_cap)
    b_cheese = mb("CheeseWheels", m_cheese)
    b_brass = mb("BrushedBrass", m_brass)
    b_sign_fresh = mb("SignBoardFresh", m_sign_fresh)

    # Main refrigerated bank cabinet shell (Z: -15.0 .. +9.0, 6 glass-door bays of 4.0u each)
    # Base plinth (y: 0.0 .. 1.05) + top compressor fascia (y: 8.95 .. 10.6) + back/ends
    b_steel.add_box(-10.4, 0.52, -3.0, 4.2, 1.04, 24.4)
    b_stain.add_box(-8.26, 0.56, -3.0, 0.14, 0.96, 24.4)  # stainless kickplate
    b_steel.add_box(-10.4, 9.75, -3.0, 4.3, 1.65, 24.4)
    b_fback.add_box(-12.3, 5.0, -3.0, 0.35, 8.0, 24.2)
    b_steel.add_box(-10.4, 5.0, -15.1, 4.2, 8.0, 0.35)
    b_steel.add_box(-10.4, 5.0, 9.1, 4.2, 8.0, 0.35)

    # Illuminated cold-chain header fascia sign facing +X into the aisle
    b_sign_fresh.add_quad((-8.20, 9.05, 8.2), (-8.20, 9.05, -14.2), (-8.20, 10.45, -14.2), (-8.20, 10.45, 8.2))

    # 6 Refrigerated Bays (z centers: -13, -9, -5, -1, +3, +7)
    bay_zs = [-13.0, -9.0, -5.0, -1.0, 3.0, 7.0]
    for b_idx, bz in enumerate(bay_zs):
        # Vertical stainless door mullions & ice-blue interior vertical LED light strips
        b_stain.add_box(-8.32, 5.0, bz - 2.0, 0.20, 7.9, 0.22)
        b_led_ice.add_box(-8.46, 5.0, bz - 1.84, 0.08, 7.5, 0.08)
        b_led_ice.add_box(-8.46, 5.0, bz + 1.84, 0.08, 7.5, 0.08)
        # Warm top accent strip inside each chiller bay
        b_led_warm.add_box(-9.6, 8.84, bz, 0.16, 0.07, 3.6)

        # Glass door panel + brushed stainless vertical pull handle
        b_fglass.add_box(-8.34, 5.0, bz, 0.08, 7.6, 3.74)
        b_stain.add_cylinder(-8.12, 3.2, bz + 1.42, 0.055, 0.055, 3.1, segs=10)
        b_stain.add_box(-8.24, 3.35, bz + 1.42, 0.24, 0.08, 0.08)
        b_stain.add_box(-8.24, 6.15, bz + 1.42, 0.24, 0.08, 0.08)

        # 4 interior stainless display shelves per bay
        shelf_ys = [1.45, 3.35, 5.25, 7.10]
        for sy in shelf_ys:
            b_stain.add_box(-10.35, sy, bz, 3.4, 0.10, 3.80)
            b_brass.add_box(-8.64, sy, bz, 0.06, 0.14, 3.76)  # gold shelf-edge trim

        # Stock each bay with distinct gourmet cold-chain goods
        if b_idx in (1, 2):
            # M9 Wagyu Marbled Beef Gift Boxes (dark obsidian box + vibrant marbled beef cut)
            for sy in shelf_ys:
                for dz in (-1.1, 0.0, 1.1):
                    b_steel.add_box(-9.8, sy + 0.18, bz + dz, 1.45, 0.22, 0.92)
                    b_wagyu.add_box(-9.75, sy + 0.34, bz + dz, 1.24, 0.14, 0.76)
                    b_brass.add_box(-9.1, sy + 0.20, bz + dz, 0.18, 0.24, 0.94)
        elif b_idx in (3, 4):
            # Prime Atlantic Salmon Fillet Trays
            for sy in shelf_ys:
                for dz in (-1.15, 0.0, 1.15):
                    b_steel.add_box(-9.8, sy + 0.14, bz + dz, 1.55, 0.14, 0.96)
                    b_salmon.add_box(-9.75, sy + 0.29, bz + dz, 1.32, 0.18, 0.78)
        else:
            # Organic Milk Bottles (top 2 shelves) + Artisanal Cheese Wheels (bottom 2 shelves)
            for sy in shelf_ys[2:]:
                for dz in (-1.3, -0.65, 0.0, 0.65, 1.3):
                    for dx in (-9.3, -10.2):
                        b_milk.add_cylinder(dx, sy + 0.05, bz + dz, 0.21, 0.18, 0.85, segs=10)
                        b_milk.add_cylinder(dx, sy + 0.90, bz + dz, 0.18, 0.09, 0.22, segs=10)
                        b_mcap.add_cylinder(dx, sy + 1.12, bz + dz, 0.10, 0.10, 0.10, segs=10)
            for sy in shelf_ys[:2]:
                for dz in (-1.0, 0.15, 1.25):
                    b_cheese.add_cylinder(-9.7, sy + 0.06, bz + dz, 0.48, 0.48, 0.42, segs=16)
                    b_cheese.add_cylinder(-10.8, sy + 0.06, bz + dz, 0.48, 0.48, 0.42, segs=16)

    # Final right-edge mullion on freezer bank
    b_stain.add_box(-8.32, 5.0, 9.0, 0.20, 7.9, 0.22)

    # ------------------------------------------------------------------
    # 3. Right Side: Heavy-Duty American Club Warehouse Racks (X: +7.4 .. +12.6)
    # ------------------------------------------------------------------
    b_orange = mb("ClubRackOrange", m_rack_orange)
    b_pallet = mb("WoodenPallets", m_pallet)
    b_box = mb("KraftCartons", m_cardboard)
    b_pack = mb("PetTreatTubs", m_pack)
    b_yellow = mb("YellowSnackCans", m_snack_yellow)
    b_baguette = mb("BakeryBaguettes", m_baguette)
    b_wine = mb("WineBottles", m_wine_bottle)
    b_price_t = mb("PriceTagTreat", m_price_treat)
    b_price_w = mb("PriceTagWagyu", m_price_wagyu)

    rack_z_posts = [-15.2, -9.2, -3.2, 2.8, 8.8]
    # Heavy charcoal steel upright frames + diagonal side bracing
    for pz in rack_z_posts:
        b_steel.add_box(7.55, 6.4, pz, 0.28, 12.8, 0.28)
        b_steel.add_box(12.25, 6.4, pz, 0.28, 12.8, 0.28)
        for by in (1.2, 4.2, 7.2, 10.2, 12.6):
            b_steel.add_box(9.90, by, pz, 4.6, 0.18, 0.18)
        # Diagonal X-bracing between front & back posts
        for by in (1.2, 4.2, 7.2, 10.2):
            b_steel.add_strut((7.55, by, pz), (12.25, by + 3.0, pz), radius=0.055, segs=6)

    # 4 Rack Bays (each 6.0 units wide along Z)
    rack_beams_y = [0.65, 3.65, 6.65, 9.65]
    for bi in range(len(rack_z_posts) - 1):
        z0, z1 = rack_z_posts[bi], rack_z_posts[bi + 1]
        zc = (z0 + z1) * 0.5
        bw = z1 - z0
        for by in rack_beams_y:
            # Iconic safety-orange heavy load beams (front & rear)
            b_orange.add_box(7.55, by, zc, 0.22, 0.34, bw - 0.1)
            b_orange.add_box(12.25, by, zc, 0.22, 0.34, bw - 0.1)
            # Dark walnut shelving deck
            b_walnut.add_box(9.90, by + 0.18, zc, 4.45, 0.12, bw - 0.22, uv_tile=3.0)

        # Top tier (y=9.83): Slatted wooden pallets + stacked bulk kraft cartons
        for pz_off in (-1.45, 1.45):
            # Wooden pallet (top slats + 3 stringer runners)
            b_pallet.add_box(9.85, 10.02, zc + pz_off, 3.6, 0.12, 2.5, uv_tile=2.0)
            for rx in (8.3, 9.85, 11.4):
                b_pallet.add_box(rx, 9.88, zc + pz_off, 0.24, 0.20, 2.45)
            # Stacked kraft cartons
            b_box.add_box(9.85, 11.15, zc + pz_off, 3.2, 2.1, 2.2)
            if (bi % 2) == 0:
                b_box.add_box(9.85, 12.65, zc + pz_off, 2.7, 0.9, 1.9)

        # Tier 3 (y=6.83): Giant Club-Pack Pet Freeze-Dried Treat Tubs & Yellow Snack Canisters
        for dz in (-2.0, -0.7, 0.7, 2.0):
            b_pack.add_box(8.8, 7.62, zc + dz, 1.25, 1.42, 1.02)
            b_brass.add_box(8.8, 8.38, zc + dz, 1.28, 0.14, 1.05)  # champagne-gold lid
            b_yellow.add_cylinder(10.6, 6.90, zc + dz, 0.44, 0.44, 1.38, segs=12)
            b_steel.add_cylinder(10.6, 8.28, zc + dz, 0.46, 0.46, 0.10, segs=12)

        # Tier 2 (y=3.83): Mixed Oak Wine Crates + Yellow Snack Canisters + Pet Treat Tubs
        if bi in (0, 2):
            for dz in (-1.6, 0.0, 1.6):
                b_pallet.add_box(9.2, 4.55, zc + dz, 2.0, 1.25, 1.25, uv_tile=2.0)
                # Wine bottles peeking above crate
                for bx_o in (-0.45, 0.0, 0.45):
                    for bz_o in (-0.28, 0.28):
                        b_wine.add_cylinder(9.2 + bx_o, 5.15, zc + dz + bz_o, 0.14, 0.06, 0.48, segs=8)
        else:
            for dz in (-2.0, -0.7, 0.7, 2.0):
                b_yellow.add_cylinder(8.65, 3.90, zc + dz, 0.42, 0.42, 1.32, segs=12)
                b_steel.add_cylinder(8.65, 5.22, zc + dz, 0.44, 0.44, 0.10, segs=12)
                b_pack.add_box(10.5, 4.62, zc + dz, 1.3, 1.45, 1.05)

        # Tier 1 (y=0.83): Artisan Bakery Woven Baskets with Baguettes & Bulk Pet Tubs
        if bi in (1, 3):
            for dz in (-1.55, 0.0, 1.55):
                # Wooden bakery bin
                b_pallet.add_box(8.9, 1.48, zc + dz, 2.2, 1.15, 1.28, uv_tile=2.0)
                # Diagonal golden baguettes sticking out
                for k in range(5):
                    b_baguette.add_cylinder(8.35 + k * 0.24, 1.95, zc + dz + (k - 2) * 0.20, 0.13, 0.11, 1.25, segs=8, rot_z=0.35)
        else:
            for dz in (-1.6, 0.0, 1.6):
                b_pack.add_box(8.85, 1.65, zc + dz, 1.55, 1.55, 1.25)
                b_brass.add_box(8.85, 2.48, zc + dz, 1.58, 0.14, 1.28)
                b_box.add_box(10.8, 1.70, zc + dz, 1.65, 1.65, 1.35)

        # Black-Gold Membership Price Sign Boards hanging cleanly on rack front beam (facing -X)
        b_steel.add_box(7.38, 6.25, zc, 0.08, 0.84, 1.66)
        price_builder = b_price_t if (bi % 2 == 0) else b_price_w
        price_builder.add_quad((7.33, 5.86, zc - 0.78), (7.33, 5.86, zc + 0.78),
                               (7.33, 6.64, zc + 0.78), (7.33, 6.64, zc - 0.78))

    # ------------------------------------------------------------------
    # 4. Midground C-Spot Hero: Sizzling Tasting Bar Island (X=0.0, Z=-10.8)
    #    Clear of central walkway z in [-8.0, 10.0]!
    # ------------------------------------------------------------------
    b_marble = mb("TastingBarMarble", m_marble)
    b_copper = mb("CopperHeatLamps", m_copper)
    b_ceramic = mb("TastingPlates", m_ceramic)
    b_herb = mb("GarnishHerbs", m_herb_green)

    tb_x, tb_z = 0.0, -10.8
    # Recessed plinth + warm under-glow LED toe-kick
    b_steel.add_box(tb_x, 0.20, tb_z, 5.8, 0.40, 2.75)
    b_led_warm.add_box(tb_x, 0.44, tb_z + 1.40, 5.65, 0.08, 0.08)
    # Charcoal body + vertical walnut slats on front face
    b_steel.add_box(tb_x, 1.95, tb_z, 6.0, 3.10, 2.95)
    for sx in np.linspace(-2.75, 2.75, 19):
        b_walnut.add_box(float(sx), 1.95, tb_z + 1.50, 0.14, 2.95, 0.12)
    # Calacatta white marble overhanging countertop (y = 3.50 .. 3.74)
    b_marble.add_box(tb_x, 3.62, tb_z, 6.45, 0.24, 3.35, uv_tile=4.5)
    b_brass.add_box(tb_x, 3.50, tb_z + 1.68, 6.45, 0.06, 0.06)

    # Low front tempered glass sneeze-guard
    b_stain.add_cylinder(-2.85, 3.74, tb_z + 1.45, 0.05, 0.05, 1.25, segs=8)
    b_stain.add_cylinder(2.85, 3.74, tb_z + 1.45, 0.05, 0.05, 1.25, segs=8)
    b_fglass.add_box(tb_x, 4.38, tb_z + 1.45, 5.7, 1.15, 0.06)

    # 3 Suspended Spun-Copper Heat Lamp Shades over the Tasting Bar
    for lx in (-1.9, 0.0, 1.9):
        b_steel.add_cylinder(lx, 7.65, tb_z, 0.04, 0.04, 7.0, segs=8)
        b_copper.add_lathe(lx, 6.95, tb_z, [
            (0.68, 0.0), (0.64, 0.18), (0.46, 0.48), (0.20, 0.72), (0.14, 0.82), (0.0, 0.82)
        ], segs=18)
        b_led_warm.add_cylinder(lx, 6.98, tb_z, 0.22, 0.22, 0.10, segs=12)

    # Walnut Cutting Board, Searing Skillet, & 3 Ceramic Tasting Plates (Salmon & Wagyu)
    b_walnut.add_box(-1.35, 3.81, tb_z + 0.15, 1.75, 0.14, 1.15, uv_tile=2.0)
    b_salmon.add_box(-1.35, 3.97, tb_z + 0.15, 1.15, 0.18, 0.56)
    # Cast-iron induction searing pan on right
    b_steel.add_cylinder(1.55, 3.74, tb_z - 0.10, 0.78, 0.84, 0.18, segs=18)
    b_wagyu.add_box(1.55, 3.92, tb_z - 0.10, 0.82, 0.14, 0.62, rot_y=0.25)
    # 3 Ceramic tasting plates along front marble edge
    for px, is_salmon in [(-0.45, True), (0.35, False), (1.15, True)]:
        b_ceramic.add_cylinder(px, 3.74, tb_z + 0.82, 0.34, 0.38, 0.06, segs=16)
        if is_salmon:
            b_salmon.add_box(px - 0.08, 3.84, tb_z + 0.82, 0.24, 0.14, 0.20, rot_y=0.2)
            b_salmon.add_box(px + 0.10, 3.84, tb_z + 0.86, 0.20, 0.14, 0.18, rot_y=-0.3)
        else:
            b_wagyu.add_box(px, 3.84, tb_z + 0.82, 0.34, 0.14, 0.24, rot_y=0.15)
        b_herb.add_cylinder(px + 0.06, 3.91, tb_z + 0.78, 0.06, 0.02, 0.06, segs=8)

    # ------------------------------------------------------------------
    # 5. Mid-Left Hero: Bruce's Exclusive VIP Oversized Metal Shopping Cart
    #    Placed at (-4.35, 0.0, 1.6), rot_y = 0.34 -> 100% clear of x in [-2.0, 2.0]!
    # ------------------------------------------------------------------
    b_chrome = mb("VIPCartChrome", m_chrome)
    b_plaid = mb("VIPCartBurgundyCushion", m_plaid)

    cart_cx, cart_cz, cart_yaw = -4.35, 1.6, 0.34
    cc, cs = math.cos(cart_yaw), math.sin(cart_yaw)

    def cart_pt(lx, ly, lz):
        return (cart_cx + lx * cc + lz * cs, ly, cart_cz - lx * cs + lz * cc)

    def cart_box(builder, lx, ly, lz, sx, sy, sz):
        wx, wy, wz = cart_pt(lx, ly, lz)
        builder.add_box(wx, wy, wz, sx, sy, sz, rot_y=cart_yaw)

    # 4 Caster wheels resting cleanly at y = 0.0 (radius 0.22 -> center y = 0.22)
    for wx_l, wz_l in [(-0.88, -1.25), (0.88, -1.25), (-0.88, 1.25), (0.88, 1.25)]:
        px, py, pz = cart_pt(wx_l, 0.22, wz_l)
        b_steel.add_cylinder(px, 0.02, pz, 0.20, 0.20, 0.14, segs=12, rot_z=math.pi * 0.5)
        b_chrome.add_cylinder(px, 0.22, pz, 0.06, 0.06, 0.36, segs=8)

    # Tubular lower chassis & rear angled upright handle posts
    cart_box(b_chrome, -0.88, 0.56, 0.0, 0.09, 0.09, 2.65)
    cart_box(b_chrome, 0.88, 0.56, 0.0, 0.09, 0.09, 2.65)
    cart_box(b_chrome, 0.0, 0.56, -1.25, 1.84, 0.09, 0.09)
    cart_box(b_chrome, 0.0, 0.56, 1.25, 1.84, 0.09, 0.09)
    # Rear upright frame posts rising to push handle (y = 3.55)
    for sx_l in (-0.90, 0.90):
        b_chrome.add_strut(cart_pt(sx_l, 0.56, 1.25), cart_pt(sx_l, 3.55, 1.55), radius=0.055, segs=8)
        b_chrome.add_strut(cart_pt(sx_l, 0.56, -1.15), cart_pt(sx_l, 1.65, -1.25), radius=0.05, segs=8)
    # Push handle crossbar + dark leather grip + brass VIP badge
    b_chrome.add_strut(cart_pt(-0.92, 3.55, 1.55), cart_pt(0.92, 3.55, 1.55), radius=0.065, segs=8)
    cart_box(b_steel, 0.0, 3.55, 1.55, 1.56, 0.16, 0.16)
    cart_box(b_brass, 0.0, 3.22, 1.52, 0.72, 0.26, 0.06)

    # Metal Wire-Grid Basket (y = 1.65 .. 3.15, x = -0.92..+0.92, z = -1.35..+1.35)
    # Top & bottom perimeter chrome rails
    for ry in (1.65, 2.15, 2.65, 3.15):
        cart_box(b_chrome, -0.92, ry, 0.0, 0.045, 0.045, 2.74)
        cart_box(b_chrome, 0.92, ry, 0.0, 0.045, 0.045, 2.74)
        cart_box(b_chrome, 0.0, ry, -1.35, 1.88, 0.045, 0.045)
        cart_box(b_chrome, 0.0, ry, 1.35, 1.88, 0.045, 0.045)
    # Vertical wire bars around basket sides & front/back
    for lz in np.linspace(-1.25, 1.25, 10):
        cart_box(b_chrome, -0.92, 2.40, float(lz), 0.032, 1.52, 0.032)
        cart_box(b_chrome, 0.92, 2.40, float(lz), 0.032, 1.52, 0.032)
    for lx in np.linspace(-0.80, 0.80, 7):
        cart_box(b_chrome, float(lx), 2.40, -1.35, 0.032, 1.52, 0.032)
        cart_box(b_chrome, float(lx), 2.40, 1.35, 0.032, 1.52, 0.032)
        # Basket floor wire grid
        cart_box(b_chrome, float(lx), 1.65, 0.0, 0.032, 0.032, 2.70)

    # Plush Burgundy-Plaid Soft Cushion inside the VIP Cart child-seat / lounge deck!
    cart_box(b_plaid, 0.0, 2.28, 0.72, 1.68, 0.24, 1.08)
    cart_box(b_plaid, 0.0, 2.68, 1.18, 1.66, 0.62, 0.20)  # backrest bolster
    cart_box(b_plaid, -0.74, 2.52, 0.72, 0.20, 0.36, 1.02)
    cart_box(b_plaid, 0.74, 2.52, 0.72, 0.20, 0.36, 1.02)

    # Gourmet goodies already loaded in the front half of Bruce's VIP cart!
    cart_box(b_pack, -0.36, 2.26, -0.58, 0.72, 1.08, 0.72)
    cart_box(b_brass, -0.36, 2.84, -0.58, 0.74, 0.10, 0.74)
    px_y, py_y, pz_y = cart_pt(0.42, 1.72, -0.62)
    b_yellow.add_cylinder(px_y, py_y, pz_y, 0.32, 0.32, 1.05, segs=12)
    px_b, py_b, pz_b = cart_pt(0.25, 2.15, -0.15)
    b_baguette.add_cylinder(px_b, py_b, pz_b, 0.14, 0.11, 1.35, segs=8, rot_x=-0.38, rot_z=0.22)

    # ------------------------------------------------------------------
    # 6. Mid-Right Promotional Pallet Endcap (X=+4.7, Z=-3.4)
    #    Clear of central walkway x in [-2.0, 2.0]!
    # ------------------------------------------------------------------
    ep_x, ep_z = 4.7, -3.4
    b_pallet.add_box(ep_x, 0.26, ep_z, 2.4, 0.16, 2.6, uv_tile=2.0)
    for rx in (-0.9, 0.0, 0.9):
        b_pallet.add_box(ep_x + rx, 0.10, ep_z, 0.22, 0.20, 2.55)
    # Stacked gourmet pet treat tubs & yellow canisters
    for dx, dz in [(-0.52, -0.55), (0.52, -0.55), (-0.52, 0.55), (0.52, 0.55)]:
        b_pack.add_box(ep_x + dx, 1.08, ep_z + dz, 0.94, 1.44, 0.94)
        b_brass.add_box(ep_x + dx, 1.84, ep_z + dz, 0.96, 0.12, 0.96)
    b_yellow.add_cylinder(ep_x, 1.90, ep_z, 0.44, 0.44, 1.22, segs=14)
    b_steel.add_cylinder(ep_x, 3.12, ep_z, 0.46, 0.46, 0.10, segs=14)

    # Standing black-gold price pedestal beside endcap
    ped_x, ped_z = ep_x - 1.35, ep_z + 1.15
    b_steel.add_cylinder(ped_x, 0.0, ped_z, 0.34, 0.30, 0.08, segs=14)
    b_steel.add_cylinder(ped_x, 0.08, ped_z, 0.05, 0.05, 3.35, segs=8)
    b_steel.add_box(ped_x, 3.65, ped_z, 1.48, 0.86, 0.10)
    b_price_t.add_quad((ped_x - 0.70, 3.25, ped_z + 0.06), (ped_x + 0.70, 3.25, ped_z + 0.06),
                       (ped_x + 0.70, 4.05, ped_z + 0.06), (ped_x - 0.70, 4.05, ped_z + 0.06))

    # ------------------------------------------------------------------
    # Compile Binary glTF 2.0 (.glb) — Uncompressed Standard glTF 2.0
    # ------------------------------------------------------------------
    bin_chunks = bytearray()
    buffer_views = []
    accessors = []
    gltf_images = []
    meshes = []
    nodes = []

    def append_bytes(data: bytes, target=None):
        while len(bin_chunks) % 4 != 0:
            bin_chunks.append(0)
        offset = len(bin_chunks)
        bin_chunks.extend(data)
        bv = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
        if target is not None:
            bv["target"] = target
        idx = len(buffer_views)
        buffer_views.append(bv)
        return idx

    for raw, mime in images_data:
        bv_idx = append_bytes(raw)
        gltf_images.append({"bufferView": bv_idx, "mimeType": mime})

    total_tris = 0
    for (_, _), builder in builders.items():
        if not builder.indices:
            continue
        pos_arr = np.array(builder.positions, dtype=np.float32)
        nrm_arr = np.array(builder.normals, dtype=np.float32)
        uv_arr = np.array(builder.uvs, dtype=np.float32)
        uv_arr[:, 1] = 1.0 - uv_arr[:, 1]

        idx_dtype = np.uint16 if len(builder.positions) < 65535 else np.uint32
        idx_comp = 5123 if idx_dtype == np.uint16 else 5125
        idx_arr = np.array(builder.indices, dtype=idx_dtype)
        total_tris += len(idx_arr) // 3

        bv_pos = append_bytes(pos_arr.tobytes(), target=34962)
        bv_nrm = append_bytes(nrm_arr.tobytes(), target=34962)
        bv_uv = append_bytes(uv_arr.tobytes(), target=34962)
        bv_idx = append_bytes(idx_arr.tobytes(), target=34963)

        acc_pos = len(accessors)
        accessors.append({
            "bufferView": bv_pos,
            "componentType": 5126,
            "count": len(pos_arr),
            "type": "VEC3",
            "min": pos_arr.min(axis=0).tolist(),
            "max": pos_arr.max(axis=0).tolist(),
        })
        acc_nrm = len(accessors)
        accessors.append({
            "bufferView": bv_nrm,
            "componentType": 5126,
            "count": len(nrm_arr),
            "type": "VEC3",
        })
        acc_uv = len(accessors)
        accessors.append({
            "bufferView": bv_uv,
            "componentType": 5126,
            "count": len(uv_arr),
            "type": "VEC2",
        })
        acc_idx = len(accessors)
        accessors.append({
            "bufferView": bv_idx,
            "componentType": idx_comp,
            "count": len(idx_arr),
            "type": "SCALAR",
        })

        mesh_idx = len(meshes)
        meshes.append({
            "name": builder.name,
            "primitives": [{
                "attributes": {"POSITION": acc_pos, "NORMAL": acc_nrm, "TEXCOORD_0": acc_uv},
                "indices": acc_idx,
                "material": builder.material_idx,
            }],
        })
        nodes.append({"name": builder.name, "mesh": mesh_idx})

    while len(bin_chunks) % 4 != 0:
        bin_chunks.append(0)

    gltf_json = {
        "asset": {"version": "2.0", "generator": "bruce-happiness-club/build_warehouse_glb.py"},
        "scene": 0,
        "scenes": [{"name": "ClubWarehouseSupermarket", "nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": meshes,
        "materials": materials,
        "textures": textures,
        "images": gltf_images,
        "samplers": [{"magFilter": 9729, "minFilter": 9987, "wrapS": 10497, "wrapT": 10497}],
        "bufferViews": buffer_views,
        "accessors": accessors,
        "buffers": [{"byteLength": len(bin_chunks)}],
    }

    json_bytes = json.dumps(gltf_json, separators=(",", ":")).encode("utf-8")
    while len(json_bytes) % 4 != 0:
        json_bytes += b" "

    total_len = 12 + 8 + len(json_bytes) + 8 + len(bin_chunks)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total_len))
        f.write(struct.pack("<II", len(json_bytes), 0x4E4F534A))
        f.write(json_bytes)
        f.write(struct.pack("<II", len(bin_chunks), 0x004E4942))
        f.write(bin_chunks)

    size_mb = os.path.getsize(OUT_PATH) / (1024 * 1024)
    print(f"Built {OUT_PATH}: {size_mb:.2f} MB, {total_tris:,} triangles, {len(meshes)} meshes, {len(materials)} materials, {len(gltf_images)} textures")


if __name__ == "__main__":
    build_scene()
