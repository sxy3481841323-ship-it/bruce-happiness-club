#!/usr/bin/env python3
"""
Build 1:1 Coastal Café 3D glTF 2.0 binary (assets/models/coastal_cafe.glb)
matching the 'Stylish and Open Café' interior architecture, materials,
furniture, lighting fixtures, and coastal boardwalk exterior.

Scale: 4 units = 1 meter (Y-up, standard uncompressed glTF 2.0).
"""

import io
import json
import math
import os
import struct
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT_DIR, "assets", "models", "coastal_cafe.glb")

import sys
if os.path.join(ROOT_DIR, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
from penthouse_kit.tex_cafe_coastal import make_malibu_coastal_panorama, make_coastal_wave_photo_tex
from penthouse_kit.tex_wine_and_cafe import make_fine_wine_label_tex, make_celadon_sage_tile_tex
from penthouse_kit.tex_oldmoney_surfaces import (
    make_marmorino_boiserie_tex,
    make_handknotted_salon_rug_tex,
    make_loft_aubusson_rug_tex,
)
from penthouse_kit.tex_pbr import make_fluted_walnut_tex, make_travertine_tex
from cafe_kit_oldmoney import build_cafe_oldmoney_millwork


# ---------------------------------------------------------------------------
# Procedural Texture Generators (embedded cleanly into GLB)
# ---------------------------------------------------------------------------

def encode_pil_image(img: Image.Image, fmt="JPEG", quality=86) -> tuple[bytes, str]:
    buf = io.BytesIO()
    if fmt.upper() == "PNG":
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue(), "image/png"
    img.convert("RGB").save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue(), "image/jpeg"


def make_sage_tile_tex(size=1024) -> Image.Image:
    """Pale sage-mint honed stone floor tiles (2x2 tiles per UV repeat) with crisp grout."""
    rng = np.random.default_rng(42)
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    # Soft multi-frequency mineral variation
    cloud = (
        np.sin(x * 0.014) * np.cos(y * 0.017) * 5.0
        + np.sin(x * 0.041 + y * 0.029) * 3.2
        + rng.normal(0, 1.8, (size, size))
    )
    # Per-tile slight tonal shift (2x2 tiles in one texture repeat)
    tx = (x >= size // 2).astype(np.float32)
    ty = (y >= size // 2).astype(np.float32)
    tile_shift = (tx * 2.4 - ty * 1.8 + tx * ty * 1.5)

    r = np.clip(212 + cloud + tile_shift, 192, 232)
    g = np.clip(208 + cloud + tile_shift, 188, 228)
    b = np.clip(198 + cloud * 0.9 + tile_shift, 178, 218)

    # Crisp grout seams at 0 and size/2
    grout_w = 5
    grout_mask = (
        (x < grout_w) | (x >= size - grout_w)
        | (np.abs(x - size / 2) < grout_w)
        | (y < grout_w) | (y >= size - grout_w)
        | (np.abs(y - size / 2) < grout_w)
    )
    r[grout_mask] = 132
    g[grout_mask] = 144
    b[grout_mask] = 128

    # Subtle edge bevel near grout
    near = (
        (x < grout_w + 5) | (x >= size - grout_w - 5)
        | (np.abs(x - size / 2) < grout_w + 5)
        | (y < grout_w + 5) | (y >= size - grout_w - 5)
        | (np.abs(y - size / 2) < grout_w + 5)
    ) & (~grout_mask)
    r[near] -= 6
    g[near] -= 6
    b[near] -= 6

    arr = np.stack([r, g, b], axis=-1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def make_white_brick_tex(size=1024) -> Image.Image:
    """Running-bond whitewashed exposed brick wall texture matching right bar wall."""
    rng = np.random.default_rng(108)
    arr = np.zeros((size, size, 3), dtype=np.float32)
    # Mortar base
    arr[:, :, 0] = 166
    arr[:, :, 1] = 162
    arr[:, :, 2] = 156

    rows = 16
    cols = 8
    row_h = size / rows
    col_w = size / cols
    mortar = 5

    noise = rng.normal(0, 6.0, (size, size))

    for row in range(rows):
        y0 = int(row * row_h + mortar * 0.5)
        y1 = int((row + 1) * row_h - mortar * 0.5)
        offset = (col_w * 0.5) if (row % 2 == 1) else 0.0
        for col in range(-1, cols + 1):
            x0 = int(col * col_w + offset + mortar * 0.5)
            x1 = int((col + 1) * col_w + offset - mortar * 0.5)
            cx0, cx1 = max(0, x0), min(size, x1)
            if cx1 <= cx0 or y1 <= y0:
                continue
            tone = rng.uniform(-16, 14)
            warm = rng.uniform(-3, 5)
            base_r = 216 + tone + warm
            base_g = 212 + tone + warm * 0.6
            base_b = 205 + tone
            arr[y0:y1, cx0:cx1, 0] = base_r + noise[y0:y1, cx0:cx1]
            arr[y0:y1, cx0:cx1, 1] = base_g + noise[y0:y1, cx0:cx1]
            arr[y0:y1, cx0:cx1, 2] = base_b + noise[y0:y1, cx0:cx1]

            # Subtle limewash highlight on top edge of each brick
            if y0 + 4 < y1:
                arr[y0:y0 + 3, cx0:cx1, :] += 8
                arr[y1 - 3:y1, cx0:cx1, :] -= 10

    arr = np.clip(arr, 110, 245).astype(np.uint8)
    return Image.fromarray(arr, "RGB").filter(ImageFilter.GaussianBlur(radius=0.45))


def make_marble_tex(w=1024, h=512) -> Image.Image:
    """Calacatta white marble with soft gray-gold veining for the curved bar top."""
    rng = np.random.default_rng(77)
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    u = x / w
    v = y / h

    base = np.zeros((h, w, 3), dtype=np.float32)
    base[:, :, 0] = 245
    base[:, :, 1] = 243
    base[:, :, 2] = 238

    # Soft marble clouding
    cloud = np.sin(u * 9.0 + np.cos(v * 6.0) * 1.4) * 4.5 + rng.normal(0, 1.0, (h, w))
    for c in range(3):
        base[:, :, c] += cloud

    # Diagonal organic veins
    for idx in range(7):
        phase = idx * 1.15
        freq = 3.2 + idx * 0.7
        curve = np.sin(u * freq + v * 5.0 + phase) + 0.35 * np.sin(u * 13.0 - v * 9.0 + phase * 2)
        vein = np.exp(-((curve * 11.0) ** 2))
        gold_mix = 1.0 if idx % 3 == 0 else 0.35
        base[:, :, 0] -= vein * (28 - 8 * gold_mix)
        base[:, :, 1] -= vein * (30 - 3 * gold_mix)
        base[:, :, 2] -= vein * (34 + 6 * gold_mix)

    return Image.fromarray(np.clip(base, 140, 252).astype(np.uint8), "RGB")


def make_oak_tex(size=512) -> Image.Image:
    """Pale warm rift-oak wood grain for ceiling panel & café round tables."""
    rng = np.random.default_rng(19)
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    grain = (
        np.sin(x * 0.24 + np.sin(y * 0.03) * 2.2) * 7.0
        + np.sin(x * 0.75 + y * 0.01) * 3.5
        + rng.normal(0, 2.2, (size, size))
    )
    # Subtle plank seams every 64px
    plank_seam = ((x.astype(np.int32) % 64) < 2)
    r = np.clip(192 + grain, 145, 224)
    g = np.clip(175 + grain * 0.92, 130, 208)
    b = np.clip(148 + grain * 0.80, 108, 182)
    r[plank_seam] -= 18
    g[plank_seam] -= 16
    b[plank_seam] -= 14
    return Image.fromarray(np.stack([r, g, b], axis=-1).clip(0, 255).astype(np.uint8), "RGB")


def make_oatmeal_fabric_tex(size=512) -> Image.Image:
    """Tailored oatmeal woven bouclé upholstery texture."""
    rng = np.random.default_rng(55)
    y, x = np.mgrid[0:size, 0:size]
    weave = ((x % 4 == 0).astype(np.float32) - (y % 4 == 0).astype(np.float32)) * 4.0
    noise = rng.normal(0, 3.2, (size, size))
    r = np.clip(198 + weave + noise, 164, 224)
    g = np.clip(170 + weave + noise, 138, 198)
    b = np.clip(138 + weave + noise, 108, 168)
    return Image.fromarray(np.stack([r, g, b], axis=-1).astype(np.uint8), "RGB")


def make_geo_art_tex(size=512) -> Image.Image:
    """Modern geometric abstract wall art matching right back wall painting."""
    img = Image.new("RGB", (size, size), (242, 241, 244))
    d = ImageDraw.Draw(img)
    # Angular modernist triangles (cobalt, lavender, pale blue, charcoal)
    d.polygon([(0, 0), (size * 0.56, 0), (size * 0.28, size * 0.62)], fill=(182, 198, 232))
    d.polygon([(size * 0.56, 0), (size, 0), (size, size * 0.48), (size * 0.48, size * 0.38)], fill=(142, 146, 208))
    d.polygon([(size * 0.24, size * 0.45), (size * 0.72, size * 0.28), (size * 0.54, size * 0.88)], fill=(64, 82, 168))
    d.polygon([(0, size * 0.45), (size * 0.36, size * 0.56), (size * 0.16, size)], fill=(28, 30, 38))
    d.polygon([(size * 0.52, size * 0.64), (size, size * 0.52), (size, size), (size * 0.44, size)], fill=(198, 210, 236))
    d.polygon([(size * 0.66, size * 0.68), (size * 0.94, size * 0.74), (size * 0.78, size)], fill=(38, 42, 54))
    # Crisp geometric frame border inside
    d.rectangle([0, 0, size - 1, size - 1], outline=(24, 24, 28), width=18)
    return img


def make_coastal_backdrop_tex(w=2048, h=1024) -> Image.Image:
    """Sunlit sky with cumulus clouds, cerulean sea, surf line, and pale beach."""
    rng = np.random.default_rng(303)
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    v = y / h  # 0 top -> 1 bottom
    u = x / w

    img = np.zeros((h, w, 3), dtype=np.float32)
    horizon_v = 0.58
    shore_v = 0.76

    # Sky region (0 .. horizon_v): vivid azure-to-sky gradient
    sky_t = np.clip(v / horizon_v, 0.0, 1.0)
    sky_r = 46 + sky_t * 114
    sky_g = 128 + sky_t * 82
    sky_b = 228 + sky_t * 22

    # Fluffy bright white cumulus clouds across upper-mid sky
    cloud_wave = (
        np.sin(u * 14.0 + np.cos(v * 18.0) * 1.6) * 0.5
        + np.sin(u * 31.0 - v * 22.0) * 0.32
        + np.cos(u * 53.0 + v * 12.0) * 0.18
    )
    cloud_band = np.exp(-(((sky_t - 0.52) / 0.30) ** 2))
    cloud_alpha = np.clip((cloud_wave + 0.32) * 1.25 * cloud_band, 0.0, 0.90)
    sky_r = sky_r * (1 - cloud_alpha) + 250 * cloud_alpha
    sky_g = sky_g * (1 - cloud_alpha) + 252 * cloud_alpha
    sky_b = sky_b * (1 - cloud_alpha) + 255 * cloud_alpha

    img[:, :, 0] = sky_r
    img[:, :, 1] = sky_g
    img[:, :, 2] = sky_b

    # Ocean region (horizon_v .. shore_v): rich cerulean-turquoise sea
    sea_mask = (v >= horizon_v) & (v < shore_v)
    sea_t = np.clip((v - horizon_v) / (shore_v - horizon_v), 0.0, 1.0)
    ripple = np.sin(u * 160.0 + v * 80.0) * 5.0
    img[sea_mask, 0] = 32 + sea_t[sea_mask] * 58 + ripple[sea_mask]
    img[sea_mask, 1] = 136 + sea_t[sea_mask] * 48 + ripple[sea_mask]
    img[sea_mask, 2] = 188 + sea_t[sea_mask] * 18 + ripple[sea_mask]

    # White surf foam line right at shore_v
    surf_mask = np.abs(v - shore_v) < (0.012 + 0.004 * np.sin(u * 40.0))
    img[surf_mask, 0] = 240
    img[surf_mask, 1] = 245
    img[surf_mask, 2] = 246

    # Pale warm beach sand below shore_v
    sand_mask = v >= shore_v + 0.01
    sand_noise = rng.normal(0, 3.0, (h, w))
    img[sand_mask, 0] = 218 + sand_noise[sand_mask]
    img[sand_mask, 1] = 205 + sand_noise[sand_mask]
    img[sand_mask, 2] = 186 + sand_noise[sand_mask]

    pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")
    return pil.filter(ImageFilter.GaussianBlur(radius=0.8))


def make_latte_art_tex(size=256) -> Image.Image:
    """Warm espresso crema + white microfoam rosetta top."""
    img = Image.new("RGB", (size, size), (146, 94, 52))
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    d.ellipse([18, 18, size - 18, size - 18], fill=(162, 106, 60))
    d.ellipse([48, 56, size - 48, size - 56], fill=(242, 235, 222))
    d.ellipse([66, 76, size - 66, size - 76], fill=(168, 112, 64))
    d.ellipse([86, 94, size - 86, size - 94], fill=(246, 241, 232))
    return img.filter(ImageFilter.GaussianBlur(radius=1.2))


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
        """Quad p0->p1->p2->p3 in CCW order from front face."""
        su, sv = uv_scale
        u0, u1, u2, u3 = (0.0, 0.0), (su, 0.0), (su, sv), (0.0, sv)
        if flip:
            self.add_tri_raw(p0, p2, p1, u0, u2, u1)
            self.add_tri_raw(p0, p3, p2, u0, u3, u2)
        else:
            self.add_tri_raw(p0, p1, p2, u0, u1, u2)
            self.add_tri_raw(p0, p2, p3, u0, u2, u3)

    def add_box(self, cx, cy, cz, sx, sy, sz, uv_tile=0.0, rot_y=0.0):
        """Axis-aligned or Y-rotated solid box centered at (cx, cy, cz)."""
        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
        c, s = math.cos(rot_y), math.sin(rot_y)

        def xf(lx, ly, lz):
            return (cx + lx * c + lz * s, cy + ly, cz - lx * s + lz * c)

        # 6 faces (CCW viewed from outside)
        faces = [
            # +Z front
            (xf(-hx, -hy, hz), xf(hx, -hy, hz), xf(hx, hy, hz), xf(-hx, hy, hz), (sx, sy)),
            # -Z back
            (xf(hx, -hy, -hz), xf(-hx, -hy, -hz), xf(-hx, hy, -hz), xf(hx, hy, -hz), (sx, sy)),
            # +X right
            (xf(hx, -hy, hz), xf(hx, -hy, -hz), xf(hx, hy, -hz), xf(hx, hy, hz), (sz, sy)),
            # -X left
            (xf(-hx, -hy, -hz), xf(-hx, -hy, hz), xf(-hx, hy, hz), xf(-hx, hy, -hz), (sz, sy)),
            # +Y top
            (xf(-hx, hy, hz), xf(hx, hy, hz), xf(hx, hy, -hz), xf(-hx, hy, -hz), (sx, sz)),
            # -Y bottom
            (xf(-hx, -hy, -hz), xf(hx, -hy, -hz), xf(hx, -hy, hz), xf(-hx, -hy, hz), (sx, sz)),
        ]
        for p0, p1, p2, p3, (w, h) in faces:
            uvs = (w / uv_tile, h / uv_tile) if uv_tile > 0 else (1.0, 1.0)
            self.add_quad(p0, p1, p2, p3, uv_scale=uvs)

    def add_cylinder(self, cx, y0, cz, r_bot, r_top, height, segs=16, rot_x=0.0, rot_z=0.0, cap_top=True, cap_bot=True):
        """Tapered cylinder with smooth side normals and optional end caps."""
        y1 = y0 + height
        cx_r, sx_r = math.cos(rot_x), math.sin(rot_x)
        cz_r, sz_r = math.cos(rot_z), math.sin(rot_z)

        def xf_pt(px, py, pz):
            # rotate around (cx, y0, cz)
            lx, ly, lz = px, py - y0, pz
            # X rot
            ly1 = ly * cx_r - lz * sx_r
            lz1 = ly * sx_r + lz * cx_r
            # Z rot
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
            # Note: in XZ with x=r*cos(a), z=r*sin(a), increasing 'a' goes from +X toward +Z (CW from +Y),
            # so outward CCW quad is b1 -> b0 -> t0 -> t1.
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

    def add_sphere(self, cx, cy, cz, rx, ry=None, rz=None, rings=12, segs=18):
        ry = rx if ry is None else ry
        rz = rx if rz is None else rz
        for r_i in range(rings):
            v0 = r_i / rings
            v1 = (r_i + 1) / rings
            phi0 = v0 * math.pi
            phi1 = v1 * math.pi
            for s_i in range(segs):
                u0 = s_i / segs
                u1 = (s_i + 1) / segs
                th0 = u0 * math.tau
                th1 = u1 * math.tau

                def sp(phi, th):
                    nx = math.sin(phi) * math.cos(th)
                    ny = math.cos(phi)
                    nz = math.sin(phi) * math.sin(th)
                    p = (cx + rx * nx, cy + ry * ny, cz + rz * nz)
                    ln = math.sqrt((nx / rx) ** 2 + (ny / ry) ** 2 + (nz / rz) ** 2) or 1.0
                    n = ((nx / rx) / ln, (ny / ry) / ln, (nz / rz) / ln)
                    return p, n

                p00, n00 = sp(phi0, th0)
                p01, n01 = sp(phi0, th1)
                p10, n10 = sp(phi1, th0)
                p11, n11 = sp(phi1, th1)
                # CCW outward: p01 -> p00 -> p10 -> p11
                if r_i > 0:
                    self.add_tri_raw(p01, p00, p10, (u1, v0), (u0, v0), (u0, v1), n01, n00, n10)
                if r_i < rings - 1:
                    self.add_tri_raw(p01, p10, p11, (u1, v0), (u0, v1), (u1, v1), n01, n10, n11)

    def add_lathe(self, cx, y0, cz, profile, segs=22):
        """profile = list of (radius, y_offset) from bottom to top."""
        for j in range(len(profile) - 1):
            r0, dy0 = profile[j]
            r1, dy1 = profile[j + 1]
            # Segment tangent to compute outward normal
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

    def add_prism_strip(self, pts_xz, y_bot, y_top, uv_tile=4.0):
        """
        Extrude a thick closed ribbon / wall from ordered 2D points (x, z)
        Wait: uses a polyline of outer/inner points [(ox, oz, ix, iz), ...].
        """
        n = len(pts_xz)
        # Side faces + top + bottom
        for i in range(n - 1):
            ox0, oz0, ix0, iz0 = pts_xz[i]
            ox1, oz1, ix1, iz1 = pts_xz[i + 1]
            seg_len = math.hypot(ox1 - ox0, oz1 - oz0)
            u_s = max(0.25, seg_len / uv_tile)
            v_s = max(0.25, (y_top - y_bot) / uv_tile)
            # Outer wall (facing outward, assuming pts go left->right along outer normal)
            self.add_quad(
                (ox0, y_bot, oz0), (ox1, y_bot, oz1), (ox1, y_top, oz1), (ox0, y_top, oz0),
                uv_scale=(u_s, v_s),
            )
            # Inner wall
            self.add_quad(
                (ix1, y_bot, iz1), (ix0, y_bot, iz0), (ix0, y_top, iz0), (ix1, y_top, iz1),
                uv_scale=(u_s, v_s),
            )
            # Top cap
            self.add_quad(
                (ox0, y_top, oz0), (ox1, y_top, oz1), (ix1, y_top, iz1), (ix0, y_top, iz0),
                uv_scale=(u_s, 0.5),
            )
            # Bottom cap
            self.add_quad(
                (ix0, y_bot, iz0), (ix1, y_bot, iz1), (ox1, y_bot, oz1), (ox0, y_bot, oz0),
                uv_scale=(u_s, 0.5),
            )
        # End caps
        ox0, oz0, ix0, iz0 = pts_xz[0]
        self.add_quad((ix0, y_bot, iz0), (ox0, y_bot, oz0), (ox0, y_top, oz0), (ix0, y_top, iz0))
        oxe, oze, ixe, ize = pts_xz[-1]
        self.add_quad((oxe, y_bot, oze), (ixe, y_bot, ize), (ixe, y_top, ize), (oxe, y_top, oze))

    def add_curved_tube(self, spine_pts, radii, segs=8):
        """Sweep circular cross-section along 3D spine points."""
        n_pts = len(spine_pts)
        rings = []
        for idx, p in enumerate(spine_pts):
            if idx == 0:
                t = np.subtract(spine_pts[1], spine_pts[0])
            elif idx == n_pts - 1:
                t = np.subtract(spine_pts[-1], spine_pts[-2])
            else:
                t = np.subtract(spine_pts[idx + 1], spine_pts[idx - 1])
            tl = np.linalg.norm(t) or 1.0
            t = t / tl
            up = np.array([0.0, 0.0, 1.0]) if abs(t[1]) > 0.92 else np.array([0.0, 1.0, 0.0])
            b = np.cross(t, up)
            b /= (np.linalg.norm(b) or 1.0)
            n = np.cross(b, t)
            r = radii[idx]
            ring = []
            for s_i in range(segs):
                ang = (s_i / segs) * math.tau
                dir_v = math.cos(ang) * b + math.sin(ang) * n
                pt = tuple((np.array(p) + dir_v * r).tolist())
                nrm = tuple(dir_v.tolist())
                ring.append((pt, nrm))
            rings.append(ring)

        for idx in range(n_pts - 1):
            r0 = rings[idx]
            r1 = rings[idx + 1]
            v0 = idx / max(1, n_pts - 1)
            v1 = (idx + 1) / max(1, n_pts - 1)
            for s_i in range(segs):
                s_next = (s_i + 1) % segs
                p00, n00 = r0[s_i]
                p01, n01 = r0[s_next]
                p10, n10 = r1[s_i]
                p11, n11 = r1[s_next]
                u0, u1 = s_i / segs, (s_i + 1) / segs
                self.add_tri_raw(p00, p01, p11, (u0, v0), (u1, v0), (u1, v1), n00, n01, n11)
                self.add_tri_raw(p00, p11, p10, (u0, v0), (u1, v1), (u0, v1), n00, n11, n10)


# ---------------------------------------------------------------------------
# Scene Assembly (Matches ref_cafe.jpg 1:1)
# ---------------------------------------------------------------------------

def build_scene():
    materials = []
    textures = []
    images_data = []  # list of (bytes, mime)

    def add_tex(pil_img, fmt="JPEG", quality=86):
        raw, mime = encode_pil_image(pil_img, fmt=fmt, quality=quality)
        img_idx = len(images_data)
        images_data.append((raw, mime))
        tex_idx = len(textures)
        textures.append({"sampler": 0, "source": img_idx})
        return tex_idx

    def add_mat(name, base_color=(1, 1, 1, 1), roughness=0.6, metalness=0.0, tex_idx=None,
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

    # Textures (High-Res 15 MB Quiet Luxury + 1:1 Sketchfab Reference)
    t_tile = add_tex(make_celadon_sage_tile_tex(1024), "JPEG", 92)
    t_brick = add_tex(make_white_brick_tex(1024), "JPEG", 90)
    t_marble = add_tex(make_marble_tex(1024, 512), "JPEG", 90)
    t_oak = add_tex(make_oak_tex(512), "JPEG", 88)
    t_fabric = add_tex(make_oatmeal_fabric_tex(512), "JPEG", 88)
    t_art = add_tex(make_coastal_wave_photo_tex(1024), "JPEG", 94)
    t_coast = add_tex(make_malibu_coastal_panorama(4096, 2048), "JPEG", 95)
    t_latte = add_tex(make_latte_art_tex(256), "JPEG", 88)
    t_wine_0 = add_tex(make_fine_wine_label_tex(512, variant=0), "JPEG", 92)
    t_wine_1 = add_tex(make_fine_wine_label_tex(512, variant=1), "JPEG", 92)
    t_wine_2 = add_tex(make_fine_wine_label_tex(512, variant=2), "JPEG", 92)
    t_marmorino = add_tex(make_marmorino_boiserie_tex(768), "JPEG", 88)
    t_walnut_fluted = add_tex(make_fluted_walnut_tex(512), "JPEG", 88)
    t_travertine = add_tex(make_travertine_tex(512), "JPEG", 88)
    t_rug_salon = add_tex(make_handknotted_salon_rug_tex(1024), "JPEG", 90)
    t_rug_aubusson = add_tex(make_loft_aubusson_rug_tex(1024), "JPEG", 90)

    # Materials
    m_floor = add_mat("SageTileFloor", (1, 1, 1, 1), roughness=0.25, metalness=0.04, tex_idx=t_tile)
    m_brick = add_mat("WhiteBrickWall", (1, 1, 1, 1), roughness=0.86, metalness=0.0, tex_idx=t_brick)
    m_wall_white = add_mat("MarmorinoLimestone", (1, 1, 1, 1), roughness=0.68, metalness=0.0, tex_idx=t_marmorino)
    m_walnut_fluted = add_mat("WalnutFluted", (1, 1, 1, 1), roughness=0.44, metalness=0.04, tex_idx=t_walnut_fluted)
    m_walnut_dark = add_mat("WalnutDarkSolid", (0.22, 0.14, 0.09, 1.0), roughness=0.42, metalness=0.04)
    m_travertine = add_mat("RomanTravertine", (1, 1, 1, 1), roughness=0.58, metalness=0.02, tex_idx=t_travertine)
    m_rug_salon = add_mat("SalonSilkWoolCarpet", (1, 1, 1, 1), roughness=0.86, metalness=0.0, tex_idx=t_rug_salon)
    m_rug_aubusson = add_mat("AubussonBorderCarpet", (1, 1, 1, 1), roughness=0.86, metalness=0.0, tex_idx=t_rug_aubusson)
    m_glass_reed = add_mat("ReedTransomGlass", (0.94, 0.90, 0.80, 0.72), roughness=0.22, metalness=0.05, double_sided=True, alpha_mode="BLEND")
    m_soffit_dark = add_mat("DarkCharcoalWood", (0.07, 0.07, 0.08, 1.0), roughness=0.52, metalness=0.08)
    m_black_metal = add_mat("MatteBlackMetal", (0.06, 0.065, 0.075, 1.0), roughness=0.34, metalness=0.76)
    m_chrome = add_mat("BrushedChrome", (0.82, 0.84, 0.87, 1.0), roughness=0.22, metalness=0.92)
    m_oak = add_mat("WarmOak", (1, 1, 1, 1), roughness=0.50, metalness=0.02, tex_idx=t_oak)
    m_marble = add_mat("CalacattaMarble", (1, 1, 1, 1), roughness=0.16, metalness=0.03, tex_idx=t_marble)
    m_bar_flute = add_mat("BarFlutes", (0.065, 0.068, 0.075, 1.0), roughness=0.46, metalness=0.14)
    m_leather = add_mat("CaramelLeather", (0.68, 0.37, 0.16, 1.0), roughness=0.42, metalness=0.03)
    m_fabric = add_mat("OatmealFabric", (1, 1, 1, 1), roughness=0.88, metalness=0.0, tex_idx=t_fabric)
    m_teal = add_mat("TealPillow", (0.05, 0.50, 0.54, 1.0), roughness=0.82)
    m_espresso_pillow = add_mat("EspressoPillow", (0.28, 0.17, 0.11, 1.0), roughness=0.84)
    m_curtain = add_mat("SheerCurtain", (0.94, 0.91, 0.82, 0.84), roughness=0.85, double_sided=True, alpha_mode="BLEND")
    m_pot_white = add_mat("CeramicWhite", (0.95, 0.95, 0.95, 1.0), roughness=0.14, metalness=0.02)
    m_soil = add_mat("PlanterSoil", (0.18, 0.14, 0.11, 1.0), roughness=0.95)
    m_wood_branch = add_mat("BranchWood", (0.34, 0.24, 0.16, 1.0), roughness=0.88)
    m_leaf = add_mat("FoliageGreen", (0.17, 0.43, 0.17, 1.0), roughness=0.56, double_sided=True)
    m_leaf_bright = add_mat("FoliageBright", (0.25, 0.54, 0.21, 1.0), roughness=0.52, double_sided=True)
    m_palm_trunk = add_mat("PalmTrunk", (0.38, 0.31, 0.24, 1.0), roughness=0.86)
    m_palm_frond = add_mat("PalmFronds", (0.20, 0.46, 0.18, 1.0), roughness=0.60, double_sided=True)
    m_flower_pink = add_mat("FlowerPink", (0.88, 0.34, 0.72, 1.0), roughness=0.68)
    m_flower_coral = add_mat("FlowerCoral", (0.94, 0.45, 0.48, 1.0), roughness=0.68)
    m_boardwalk = add_mat("BoardwalkTimber", (0.56, 0.48, 0.40, 1.0), roughness=0.84)
    m_coast_bg = add_mat("CoastalBackdrop", (1, 1, 1, 1), roughness=1.0, emissive=None, tex_idx=t_coast, double_sided=True)
    m_art = add_mat("GeoPainting", (1, 1, 1, 1), roughness=0.45, tex_idx=t_art)
    m_globe_glow = add_mat("PendantGlobe", (1.0, 0.98, 0.94, 1.0), roughness=0.2, emissive=(1.0, 0.97, 0.90))
    m_led_warm = add_mat("UnderBarLed", (1.0, 0.93, 0.78, 1.0), roughness=0.3, emissive=(1.0, 0.89, 0.65))
    m_led_cool = add_mat("LinearLed", (1.0, 0.99, 0.96, 1.0), roughness=0.2, emissive=(1.0, 0.98, 0.92))
    m_pastry_glass = add_mat("PastryGlass", (0.88, 0.95, 0.98, 0.22), roughness=0.08, metalness=0.05, double_sided=True, alpha_mode="BLEND")
    m_pastry_gold = add_mat("PastryGold", (0.84, 0.58, 0.28, 1.0), roughness=0.58)
    m_pastry_cream = add_mat("PastryCream", (0.94, 0.89, 0.78, 1.0), roughness=0.48)
    m_bottle_dark = add_mat("WineBottle", (0.09, 0.14, 0.09, 1.0), roughness=0.14, metalness=0.06)
    m_label_red = add_mat("BottleLabel", (0.76, 0.18, 0.16, 1.0), roughness=0.55)
    m_wine_wrap_0 = add_mat("WineWrapChateau", (1, 1, 1, 1), roughness=0.38, metalness=0.02, tex_idx=t_wine_0)
    m_wine_wrap_1 = add_mat("WineWrapBeaune", (1, 1, 1, 1), roughness=0.38, metalness=0.02, tex_idx=t_wine_1)
    m_wine_wrap_2 = add_mat("WineWrapBarolo", (1, 1, 1, 1), roughness=0.38, metalness=0.02, tex_idx=t_wine_2)
    m_ruby_wine = add_mat("RubyWineLiquid", (0.24, 0.02, 0.04, 0.90), roughness=0.08, metalness=0.04, alpha_mode="BLEND")
    m_foil_cap = add_mat("BottleCapsule", (0.64, 0.12, 0.14, 1.0), roughness=0.32, metalness=0.55)
    m_latte_top = add_mat("LatteFoam", (1, 1, 1, 1), roughness=0.42, tex_idx=t_latte)
    m_brass = add_mat("BrassSign", (0.86, 0.71, 0.42, 1.0), roughness=0.26, metalness=0.88)

    builders = {}

    def mb(name, mat_idx) -> MeshBuilder:
        key = (name, mat_idx)
        if key not in builders:
            builders[key] = MeshBuilder(name, mat_idx)
        return builders[key]

    # ------------------------------------------------------------------
    # 1. Room Shell: Sage Tile Floor, Walls, Ceiling & Lighting Channels
    # ------------------------------------------------------------------
    # Floor: X [-11.8, +11.8] (23.6), Z [-22.2, +20.2] (42.4); UV tiled at 7.2 units (2x2 tiles = 3.6 per tile)
    b_floor = mb("Floor", m_floor)
    b_floor.add_quad((-11.8, 0.0, 20.2), (11.8, 0.0, 20.2), (11.8, 0.0, -22.2), (-11.8, 0.0, -22.2),
                     uv_scale=(23.6 / 7.2, 42.4 / 7.2))

    # Right Wall (facing -X into the room):
    # - Brick zone: Z [-7.4, +11.5]
    b_brick = mb("RightBrickWall", m_brick)
    b_brick.add_quad((11.5, 0.0, -7.4), (11.5, 0.0, 11.5), (11.5, 15.6, 11.5), (11.5, 15.6, -7.4),
                     uv_scale=(18.9 / 5.4, 15.6 / 5.4))
    # - Textured warm French Marmorino limestone right wall zones: back Z [-22.2, -7.4] and front Z [11.5, 20.2]
    b_wall = mb("WallsAndColumns", m_wall_white)
    b_wall.add_quad((11.5, 0.0, -22.2), (11.5, 0.0, -7.4), (11.5, 15.6, -7.4), (11.5, 15.6, -22.2), uv_scale=(3.0, 2.5))
    b_wall.add_quad((11.5, 0.0, 11.5), (11.5, 0.0, 20.2), (11.5, 15.6, 20.2), (11.5, 15.6, 11.5), uv_scale=(2.0, 2.5))
    # Rear enclosure behind curtain X [+1.2, +11.5], Z=-22.2
    b_wall.add_quad((1.2, 0.0, -22.2), (11.5, 0.0, -22.2), (11.5, 15.6, -22.2), (1.2, 15.6, -22.2), uv_scale=(2.2, 2.5))
    # Front wall behind camera Z=+20.2 (boiserie & roastery bookcase portal added below!)
    b_wall.add_quad((11.5, 0.0, 20.2), (-11.5, 0.0, 20.2), (-11.5, 16.4, 20.2), (11.5, 16.4, 20.2), uv_scale=(4.6, 2.8))

    # Left structural limestone pilasters & header beams along X=-11.4
    for pz in (11.8, 2.0, -9.8, -21.8):
        b_wall.add_box(-11.4, 7.6, pz, 1.15, 15.2, 1.15, uv_tile=5.0)
    # Back-center pillar separating glass wall and sheer curtain
    b_wall.add_box(1.3, 7.6, -21.8, 1.0, 15.2, 1.0, uv_tile=5.0)
    # Left & back header beams
    b_wall.add_box(-11.4, 15.1, -1.0, 1.15, 2.2, 42.4, uv_tile=5.0)
    b_wall.add_box(-5.0, 15.1, -21.8, 13.0, 2.2, 1.05, uv_tile=5.0)

    # Geometric abstract painting on smooth right wall (z = -12.6, y = 8.4)
    b_art = mb("GeoArt", m_art)
    b_art.add_box(11.40, 8.4, -12.6, 0.16, 4.6, 3.8)

    # Ceiling system (Y = 15.6 .. 16.4)
    b_soffit = mb("DarkSoffit", m_soffit_dark)
    b_oak_ceil = mb("OakCeiling", m_oak)
    b_led_cool = mb("CeilingLinearLED", m_led_cool)
    b_led_warm = mb("UnderBarLED", m_led_warm)

    # Left dark band (X: -11.6..-8.2)
    b_soffit.add_box(-9.9, 16.05, -1.0, 3.4, 0.7, 42.4)
    # White stepped soffit (X: -8.2..-5.2)
    b_wall.add_box(-6.7, 16.10, -1.0, 3.0, 0.6, 42.4)
    # Black recessed spotlight slot (X: -5.2..-3.8)
    b_soffit.add_box(-4.5, 16.25, -1.0, 1.4, 0.4, 42.4)
    # Paired glowing spotlight pucks inside the black slot
    for sz in range(-18, 18, 6):
        b_led_cool.add_cylinder(-4.72, 16.02, sz - 0.35, 0.14, 0.14, 0.05, segs=12)
        b_led_cool.add_cylinder(-4.26, 16.02, sz + 0.35, 0.14, 0.14, 0.05, segs=12)

    # Wide warm oak ceiling panel (X: -3.8..+9.2, Y: 15.95)
    b_oak_ceil.add_quad((-3.8, 15.95, -22.2), (9.2, 15.95, -22.2), (9.2, 15.95, 20.2), (-3.8, 15.95, 20.2),
                       uv_scale=(2.6, 8.0))
    # Continuous glowing linear LED bar inlaid in oak ceiling (X = +4.4)
    b_led_cool.add_box(4.4, 15.91, -1.0, 0.22, 0.06, 41.0)
    # Right dark wood soffit fascia above brick wall (X: +9.2..+11.5)
    b_soffit.add_box(10.35, 16.0, -1.0, 2.3, 0.8, 42.4)
    b_soffit.add_box(11.25, 14.3, -1.0, 0.55, 2.4, 42.4)
    # Cove light strip under right fascia
    b_led_cool.add_box(11.0, 14.9, -1.0, 0.12, 0.14, 40.0)

    # ------------------------------------------------------------------
    # 2. Curtain Wall Black Mullions & Back-Right Cream Sheer Curtain
    # ------------------------------------------------------------------
    b_black = mb("BlackMetal", m_black_metal)

    # Left glass bay mullions (X = -11.4, between pilasters)
    for (z0, z1) in [(2.6, 11.2), (-9.2, 1.4), (-21.2, -10.4)]:
        bay_w = z1 - z0
        zc = (z0 + z1) * 0.5
        # Horizontal transoms (bottom, y=4.6, y=9.4, top y=14.0)
        for ty in (0.14, 4.6, 9.4, 14.0):
            b_black.add_box(-11.4, ty, zc, 0.34, 0.24, bay_w)
        # Vertical mullions dividing bay into 2 panes
        for tz in (z0 + 0.12, zc, z1 - 0.12):
            b_black.add_box(-11.4, 7.05, tz, 0.34, 14.0, 0.24)

    # Back glass curtain wall mullions (Z = -21.8, X: -10.8..+0.8)
    for ty in (0.14, 4.6, 9.4, 14.0):
        b_black.add_box(-5.0, ty, -21.8, 11.7, 0.24, 0.34)
    for tx in (-10.8, -7.9, -5.0, -2.1, 0.8):
        b_black.add_box(tx, 7.05, -21.8, 0.24, 14.0, 0.34)

    # Cream pleated sheer curtain on back-right (X: +1.5..+11.2, Z = -21.4)
    b_curtain = mb("SheerCurtain", m_curtain)
    pleats = 42
    x_start, x_end = 1.5, 11.2
    for i in range(pleats):
        px0 = x_start + (i / pleats) * (x_end - x_start)
        px1 = x_start + ((i + 1) / pleats) * (x_end - x_start)
        pz0 = -21.35 + math.sin(i * 1.1) * 0.22
        pz1 = -21.35 + math.sin((i + 1) * 1.1) * 0.22
        b_curtain.add_quad((px0, 0.0, pz0), (px1, 0.0, pz1), (px1, 14.8, pz1), (px0, 14.8, pz0),
                           uv_scale=(0.25, 2.0))

    # ------------------------------------------------------------------
    # 3. White Globe Pendant Lamps (Left Window Row + Right Bar Row)
    # ------------------------------------------------------------------
    b_globe = mb("PendantGlobes", m_globe_glow)
    # Left window row (5 pendants)
    for idx, pz in enumerate([8.2, 3.0, -2.2, -7.4, -12.8]):
        gy = 10.6 + (idx % 2) * 0.18
        rod_h = 15.9 - gy
        b_black.add_cylinder(-7.5, 15.82, pz, 0.22, 0.22, 0.12, segs=12)
        b_black.add_cylinder(-7.5, gy + 0.35, pz, 0.045, 0.045, rod_h - 0.35, segs=8)
        b_globe.add_sphere(-7.5, gy, pz, 0.44, rings=10, segs=16)

    # Right bar & back row (6 pendants)
    for (px, pz, gy) in [
        (4.1, 6.2, 10.3),
        (4.1, -0.4, 10.4),
        (4.1, -6.8, 10.4),
        (4.1, -13.0, 10.4),
        (9.3, 6.4, 10.4),
        (9.3, -10.8, 10.5),
    ]:
        rod_h = 15.9 - gy
        b_black.add_cylinder(px, 15.82, pz, 0.20, 0.20, 0.12, segs=12)
        b_black.add_cylinder(px, gy + 0.30, pz, 0.04, 0.04, rod_h - 0.30, segs=8)
        b_globe.add_sphere(px, gy, pz, 0.37, rings=10, segs=16)

    # ------------------------------------------------------------------
    # 4. Curved Dark Charcoal Fluted Bar Counter + Marble Top + Appliances
    # ------------------------------------------------------------------
    # Bar footprint: straight along X=+3.35 from Z=-17.2 to Z=+5.6,
    # then quarter-circle arc around (cx=6.55, cz=5.6) R=3.2 to (6.55, 8.8),
    # then straight across to (11.4, 8.8).
    bar_spine = []
    for z in np.linspace(-17.2, 5.6, 18):
        bar_spine.append((3.35, float(z), 4.05, float(z)))
    arc_cx, arc_cz, arc_r = 6.55, 5.6, 3.2
    for step in range(1, 15):
        ang = math.pi - (step / 14.0) * (math.pi * 0.5)  # pi (-X) -> pi/2 (+Z)
        ox = arc_cx + arc_r * math.cos(ang)
        oz = arc_cz + arc_r * math.sin(ang)
        ix = arc_cx + (arc_r - 0.70) * math.cos(ang)
        iz = arc_cz + (arc_r - 0.70) * math.sin(ang)
        bar_spine.append((ox, oz, ix, iz))
    bar_spine.append((11.4, 8.8, 11.4, 8.1))

    # Recessed dark base plinth
    b_soffit.add_prism_strip([(ox + 0.14 if ox < 6 else ox, oz - 0.10 if oz > 7 else oz, ix, iz)
                              for ox, oz, ix, iz in bar_spine], 0.0, 0.28)
    # Main bar body
    b_flute = mb("BarCounterBody", m_bar_flute)
    b_flute.add_prism_strip(bar_spine, 0.28, 4.18, uv_tile=4.0)

    # 3D vertical charcoal fluted slats along outer face (key visual signature!)
    slat_pts = []
    for z in np.linspace(-17.0, 5.5, 48):
        slat_pts.append((3.32, float(z), 0.0))
    for step in range(1, 14):
        ang = math.pi - (step / 13.0) * (math.pi * 0.5)
        slat_pts.append((arc_cx + (arc_r + 0.03) * math.cos(ang), arc_cz + (arc_r + 0.03) * math.sin(ang), ang - math.pi))
    for x in np.linspace(6.8, 11.2, 10):
        slat_pts.append((float(x), 8.83, -math.pi * 0.5))
    for sx, sz, ry in slat_pts:
        b_flute.add_box(sx, 2.22, sz, 0.11, 3.84, 0.12, rot_y=ry)

    # Warm LED cove strip right beneath the marble overhang
    led_spine = [(ox - 0.04 if ox < 6 else ox, oz + 0.04 if oz > 7 else oz, ix, iz) for ox, oz, ix, iz in bar_spine]
    b_led_warm.add_prism_strip(led_spine, 4.12, 4.18)

    # Overhanging Calacatta marble countertop (wider 2.35u depth covering bar top cleanly)
    marble_spine = []
    for z in np.linspace(-17.2, 5.6, 18):
        marble_spine.append((3.10, float(z), 5.45, float(z)))
    for step in range(1, 15):
        ang = math.pi - (step / 14.0) * (math.pi * 0.5)
        ox = arc_cx + (arc_r + 0.26) * math.cos(ang)
        oz = arc_cz + (arc_r + 0.26) * math.sin(ang)
        ix = arc_cx + (arc_r - 2.35) * math.cos(ang)
        iz = arc_cz + (arc_r - 2.35) * math.sin(ang)
        marble_spine.append((ox, oz, ix, iz))
    marble_spine.append((11.4, 9.06, 11.4, 6.70))
    b_marble = mb("MarbleCounter", m_marble)
    b_marble.add_prism_strip(marble_spine, 4.18, 4.42, uv_tile=5.5)

    # Recessed dark-oak & stainless barista worktop filling interior counter bay (Y = 3.85)
    b_oak_work = mb("WarmOakBaristaWorktop", m_oak)
    b_oak_work.add_box(7.15, 3.78, -1.6, 3.6, 0.18, 17.6, uv_tile=3.0)
    b_flute.add_box(7.15, 1.85, -1.6, 3.5, 3.7, 17.4)

    # Back prep counter along right wall (X: +8.8..+11.4, Z: -10.0..+6.8)
    b_flute.add_box(10.1, 2.05, -1.6, 2.5, 4.1, 16.8)
    b_marble.add_box(10.05, 4.22, -1.6, 2.65, 0.24, 17.0, uv_tile=5.5)

    # Sleek Curved/Sloped-Front Glass Patisserie Showcase on front marble bar (X=+4.25, Y=4.42, Z=+2.8)
    b_chrome = mb("ChromeAccents", m_chrome)
    b_glass = mb("PastryCaseGlass", m_pastry_glass)
    b_pastry_g = mb("PastriesGold", m_pastry_gold)
    b_pastry_c = mb("PastriesCream", m_pastry_cream)
    b_pink = mb("FlowersPink", m_flower_pink)
    b_stem = mb("FlowerStems", m_leaf)
    b_walnut = mb("BaristaWalnut", m_espresso_pillow)

    # Display plinth & rear frame
    b_black.add_box(4.25, 4.58, 2.8, 1.48, 0.32, 3.08)
    # Sloped/curved front ribs & top frame
    for dz in (-1.50, 1.50):
        b_black.add_box(4.94, 5.38, 2.8 + dz, 0.08, 1.32, 0.08)
        b_black.add_box(3.56, 5.10, 2.8 + dz, 0.07, 0.72, 0.07)
        b_black.add_curved_tube([
            (3.56, 5.42, 2.8 + dz),
            (3.68, 5.82, 2.8 + dz),
            (3.98, 6.02, 2.8 + dz),
            (4.94, 6.04, 2.8 + dz),
        ], [0.04, 0.04, 0.04, 0.04], segs=6)
    b_black.add_box(4.46, 6.04, 2.8, 1.00, 0.07, 3.08)
    # Warm interior showcase LED strip under top frame
    b_led_warm.add_box(4.32, 5.96, 2.8, 0.14, 0.05, 2.86)
    # Sloped front & side glass panels
    b_glass.add_quad((3.54, 4.74, 1.30), (3.54, 4.74, 4.30), (3.62, 5.56, 4.30), (3.62, 5.56, 1.30))
    b_glass.add_quad((3.62, 5.56, 1.30), (3.62, 5.56, 4.30), (4.00, 6.01, 4.30), (4.00, 6.01, 1.30))
    b_glass.add_quad((4.00, 6.01, 1.30), (4.00, 6.01, 4.30), (4.92, 6.01, 4.30), (4.92, 6.01, 1.30))
    b_glass.add_box(4.25, 5.38, 4.28, 1.32, 1.24, 0.04)
    b_glass.add_box(4.25, 5.38, 1.32, 1.32, 1.24, 0.04)
    # Two glass tiers stocked with golden crescent croissants, berry tarts, & cream cakes
    for sy in (4.94, 5.46):
        b_glass.add_box(4.28, sy, 2.8, 1.12, 0.04, 2.80)
        for pz in (1.85, 2.45, 3.05, 3.65):
            # Crescent croissant
            b_pastry_g.add_curved_tube([
                (3.96, sy + 0.09, pz - 0.14),
                (4.05, sy + 0.13, pz),
                (3.96, sy + 0.09, pz + 0.14),
            ], [0.05, 0.09, 0.05], segs=8)
            # Berry/cream tart
            b_pastry_c.add_cylinder(4.46, sy + 0.02, pz, 0.16, 0.17, 0.16, segs=12)
            b_pink.add_sphere(4.46, sy + 0.19, pz, 0.06, 0.05, 0.06, rings=4, segs=6)

    # Petite clear glass bud vase with slender stems & delicate pink blossoms atop showcase
    b_pot = mb("CeramicWhite", m_pot_white)
    b_glass.add_cylinder(4.45, 6.08, 2.8, 0.09, 0.07, 0.28, segs=12)
    b_stem.add_cylinder(4.45, 6.26, 2.8, 0.015, 0.015, 0.34, segs=6)
    b_stem.add_cylinder(4.42, 6.28, 2.83, 0.014, 0.014, 0.30, segs=6, rot_z=0.18)
    b_stem.add_cylinder(4.48, 6.28, 2.77, 0.014, 0.014, 0.28, segs=6, rot_z=-0.20)
    for (fx, fy, fz, fr) in [(4.45, 6.62, 2.80, 0.09), (4.37, 6.57, 2.84, 0.075), (4.53, 6.54, 2.76, 0.08)]:
        b_pink.add_sphere(fx, fy, fz, fr, fr * 0.85, fr, rings=5, segs=8)

    # Bordeaux wine bottle builder helper (dark glass + fine vintage wrap label + foil capsule)
    b_bottle = mb("WineBottles", m_bottle_dark)
    b_cap = mb("WineBottleCapsules", m_foil_cap)
    b_wine_wraps = [
        mb("WineLabelChateau", m_wine_wrap_0),
        mb("WineLabelBeaune", m_wine_wrap_1),
        mb("WineLabelBarolo", m_wine_wrap_2),
    ]
    b_ruby = mb("RubyWineLiquid", m_ruby_wine)

    def add_wine_bottle(bx, by, bz, scale=1.0, variant=0):
        b_bottle.add_lathe(bx, by, bz, [
            (0.0, 0.0), (0.145 * scale, 0.0), (0.150 * scale, 0.56 * scale),
            (0.115 * scale, 0.68 * scale), (0.052 * scale, 0.78 * scale),
            (0.048 * scale, 0.96 * scale), (0.055 * scale, 0.99 * scale), (0.0, 0.99 * scale)
        ], segs=14)
        b_wine_wraps[variant % 3].add_cylinder(
            bx, by + 0.14 * scale, bz, 0.154 * scale, 0.154 * scale, 0.34 * scale,
            segs=14, cap_top=False, cap_bot=False
        )
        b_cap.add_cylinder(bx, by + 0.80 * scale, bz, 0.052 * scale, 0.054 * scale, 0.195 * scale, segs=12)

    def add_wine_glass(gx, gy, gz, poured=False, scale=1.0):
        b_glass.add_cylinder(gx, gy, gz, 0.11 * scale, 0.11 * scale, 0.025 * scale, segs=12)
        b_glass.add_cylinder(gx, gy + 0.025 * scale, gz, 0.018 * scale, 0.016 * scale, 0.22 * scale, segs=8)
        b_glass.add_lathe(gx, gy + 0.24 * scale, gz, [
            (0.0, 0.0), (0.06 * scale, 0.02 * scale), (0.135 * scale, 0.12 * scale),
            (0.125 * scale, 0.25 * scale), (0.105 * scale, 0.32 * scale)
        ], segs=12)
        if poured:
            b_ruby.add_cylinder(gx, gy + 0.27 * scale, gz, 0.07 * scale, 0.12 * scale, 0.10 * scale, segs=12)

    # Prominent front-bar red-wine bottle & tasting glass between showcase and POS register (X=4.18, Z=0.65)
    add_wine_bottle(4.18, 4.42, 0.65, scale=1.05, variant=0)
    add_wine_glass(4.02, 4.42, 0.12, poured=True, scale=0.95)

    # POS Register on front bar (Z = -6.8)
    b_black.add_box(4.15, 4.55, -6.8, 0.85, 0.26, 0.95)
    b_black.add_box(4.15, 5.02, -6.8, 0.18, 0.72, 0.18)
    b_black.add_box(4.02, 5.45, -6.8, 0.10, 0.75, 1.05, rot_y=0.15)

    # Detailed Commercial Espresso Machine & Grinder on back counter (X = 9.65, Z = 1.6)
    b_walnut.add_box(9.85, 4.90, 1.6, 1.18, 1.10, 2.25)
    b_chrome.add_box(9.72, 5.02, 1.6, 1.05, 0.92, 2.08)
    b_chrome.add_box(9.28, 4.48, 1.6, 0.42, 0.14, 2.05)  # drip tray
    b_black.add_box(9.20, 5.16, 1.6, 0.24, 0.28, 1.92)  # front fascia
    # 2 chrome groupheads + black angled portafilters + steam wand
    for gz in (1.12, 2.08):
        b_chrome.add_cylinder(9.05, 4.92, gz, 0.13, 0.13, 0.20, segs=12)
        b_black.add_box(8.80, 4.94, gz, 0.42, 0.06, 0.06, rot_y=0.18)
    b_chrome.add_curved_tube([(9.12, 5.04, 2.48), (8.92, 4.86, 2.54), (8.88, 4.64, 2.56)], [0.025, 0.02, 0.02], segs=6)
    # Stacked white ceramic espresso cups on cup warmer top
    for (cz, cy) in [(1.10, 5.48), (1.42, 5.48), (1.26, 5.72), (1.98, 5.48)]:
        b_pot.add_cylinder(9.75, cy, cz, 0.10, 0.13, 0.22, segs=10)
    # Conical burr grinder with roasted coffee beans inside clear hopper
    b_black.add_cylinder(9.65, 4.35, -0.45, 0.25, 0.22, 0.72, segs=12)
    b_glass.add_cylinder(9.65, 5.08, -0.45, 0.16, 0.29, 0.48, segs=12)
    b_walnut.add_cylinder(9.65, 5.10, -0.45, 0.15, 0.22, 0.26, segs=12)  # coffee beans inside hopper

    # ------------------------------------------------------------------
    # 5. Right Brick Wall Open Hollow Square-Tube Iron Shelf + Bottles/Glassware
    # ------------------------------------------------------------------
    # Staggered asymmetric 4-bay matte-black square-tube iron shelving (no solid side slabs!)
    bays = [
        # (z0, z1, y_levels)
        (-2.2, -0.1, [6.2, 7.9, 9.6, 11.2]),
        (-0.1, 2.1, [6.2, 7.6, 9.7, 11.8]),
        (2.1, 4.5, [6.2, 8.2, 10.1, 11.4]),
        (4.5, 7.2, [6.2, 7.9, 9.6, 11.9]),
    ]
    # Vertical hollow square-tube posts (front x=10.48, back wall x=11.38)
    post_z_list = [(-2.2, 11.2), (-0.1, 11.8), (2.1, 11.8), (4.5, 11.9), (7.2, 11.9)]
    for pz, y_top in post_z_list:
        h_post = y_top - 6.2
        yc = 6.2 + h_post * 0.5
        b_black.add_box(10.48, yc, pz, 0.075, h_post, 0.075)
        b_black.add_box(11.38, yc, pz, 0.075, h_post, 0.075)
        # Top & bottom cross-ties per post
        b_black.add_box(10.93, 6.2, pz, 0.96, 0.075, 0.075)
        b_black.add_box(10.93, y_top, pz, 0.96, 0.075, 0.075)

    for z0, z1, y_levels in bays:
        zc = (z0 + z1) * 0.5
        bw = (z1 - z0) + 0.06
        for sy in y_levels:
            b_black.add_box(10.48, sy, zc, 0.075, 0.075, bw)
            b_black.add_box(11.38, sy, zc, 0.075, 0.075, bw)
            if sy < y_levels[-1]:
                b_black.add_box(10.93, sy + 0.01, zc, 0.86, 0.055, bw - 0.10)

    # Stocked wine bottles (Bordeaux/Pinot Noir with fine textured cream/gold labels) & crystal stemware
    rack_bottles = [
        (-1.45, 6.24, 0), (-0.92, 6.24, 1), (-0.42, 6.24, 2),
        (0.55, 9.74, 0), (1.05, 9.74, 1),
        (2.65, 8.24, 2), (3.15, 8.24, 0), (3.65, 8.24, 1),
        (5.05, 7.94, 0), (5.55, 7.94, 2), (6.05, 7.94, 1),
        (4.95, 9.64, 1), (5.45, 9.64, 0),
    ]
    for (bz, by, var) in rack_bottles:
        add_wine_bottle(10.88, by, bz, scale=1.02, variant=var)

    for (gz, gy) in [(0.35, 6.24), (0.85, 6.24), (1.35, 6.24), (2.75, 6.24), (3.35, 6.24), (3.95, 6.24), (6.45, 7.94), (6.85, 7.94)]:
        add_wine_glass(10.86, gy, gz, poured=False, scale=0.88)

    for (kz, ky) in [(3.0, 10.14), (5.8, 6.24), (0.9, 7.64)]:
        b_pot.add_cylinder(10.92, ky, kz, 0.21, 0.14, 0.46, segs=14)

    # Right Marble Countertop Sommelier Red-Wine Tasting Station + Coffee Bean Dispenser & Kettle
    # Front-right marble curve return (X=7.2..9.6, Z=6.8..8.3, Y=4.42)
    for (bx, bz, var) in [(7.65, 7.85, 0), (8.25, 7.95, 1), (8.82, 7.72, 2), (9.85, 4.35, 0)]:
        add_wine_bottle(bx, 4.42 if bx < 9.2 else 4.34, bz, scale=1.08, variant=var)
    # Crystal Wine Decanter filled with deep ruby wine on right front counter (X=7.65, Y=4.42, Z=6.85)
    b_glass.add_lathe(7.65, 4.42, 6.85, [
        (0.0, 0.0), (0.24, 0.0), (0.30, 0.14), (0.24, 0.30), (0.10, 0.44), (0.08, 0.68), (0.11, 0.74)
    ], segs=18)
    b_ruby.add_lathe(7.65, 4.43, 6.85, [
        (0.0, 0.0), (0.21, 0.0), (0.26, 0.12), (0.21, 0.24), (0.0, 0.24)
    ], segs=16)
    add_wine_glass(6.95, 4.42, 7.15, poured=True, scale=1.0)
    add_wine_glass(7.25, 4.42, 6.65, poured=True, scale=1.0)
    add_wine_glass(7.95, 4.42, 6.45, poured=False, scale=1.0)
    # Back-right Sommelier reserve bottles near brick counter (X=9.85, Z=-2.8..-1.8)
    add_wine_bottle(9.85, 4.34, -2.75, scale=1.06, variant=1)
    add_wine_bottle(9.85, 4.34, -2.25, scale=1.06, variant=2)
    # Glass coffee-bean dispenser & matte-black pour-over kettle on right counter
    b_oak_work.add_cylinder(9.75, 4.34, 3.85, 0.34, 0.34, 0.14, segs=16)
    b_glass.add_cylinder(9.75, 4.48, 3.85, 0.28, 0.28, 0.72, segs=16)
    b_walnut.add_cylinder(9.75, 4.49, 3.85, 0.25, 0.25, 0.46, segs=16)
    b_black.add_cylinder(9.75, 5.20, 3.85, 0.30, 0.30, 0.08, segs=16)
    b_black.add_lathe(6.25, 4.42, 5.55, [
        (0.0, 0.0), (0.22, 0.0), (0.20, 0.16), (0.14, 0.38), (0.16, 0.42), (0.0, 0.42)
    ], segs=14)
    b_black.add_curved_tube([(6.05, 4.52, 5.55), (5.82, 4.72, 5.55), (5.75, 4.86, 5.55)], [0.025, 0.020, 0.016], segs=6)

    # ------------------------------------------------------------------
    # 6. 7 Caramel-Tan Round Barstools along the Curved Bar
    # ------------------------------------------------------------------
    b_leather = mb("BarstoolLeather", m_leather)
    stool_positions = [
        (2.05, 5.1),
        (2.05, 2.6),
        (2.05, 0.1),
        (2.05, -2.4),
        (2.05, -4.9),
        (2.05, -7.4),
        (2.05, -9.9),
    ]
    for sx, sz in stool_positions:
        # Plush caramel leather cushion (lathed beveled disc at Y = 2.86)
        b_leather.add_lathe(sx, 2.74, sz, [
            (0.0, 0.0), (0.62, 0.0), (0.68, 0.08), (0.68, 0.20), (0.60, 0.26), (0.0, 0.26)
        ], segs=18)
        # 4 slim splayed black legs + ring footrest
        for lx, lz in [(-0.44, -0.44), (0.44, -0.44), (0.44, 0.44), (-0.44, 0.44)]:
            b_black.add_box(sx + lx, 1.37, sz + lz, 0.08, 2.74, 0.08)
        for fy in (0.92, 2.64):
            b_black.add_box(sx, fy, sz + 0.44, 0.92, 0.07, 0.07)
            b_black.add_box(sx, fy, sz - 0.44, 0.92, 0.07, 0.07)
            b_black.add_box(sx + 0.44, fy, sz, 0.07, 0.07, 0.92)
            b_black.add_box(sx - 0.44, fy, sz, 0.07, 0.07, 0.92)

    # ------------------------------------------------------------------
    # 7. Left Window Sofas, Side Table, Round Oak Tables & Tub Chairs
    # ------------------------------------------------------------------
    b_fabric = mb("OatmealUpholstery", m_fabric)
    b_teal = mb("TealPillows", m_teal)
    b_esp = mb("EspressoPillows", m_espresso_pillow)
    b_oak = mb("WarmOakFurniture", m_oak)

    def add_sofa(sx, sz):
        # Black steel legs
        for lx in (-1.2, 1.2):
            for lz in (-2.2, 2.2):
                b_black.add_box(sx + lx, 0.35, sz + lz, 0.12, 0.70, 0.12)
        # Seat cushion & base frame + rounded front edge bolster
        b_fabric.add_box(sx, 1.08, sz, 2.68, 0.80, 5.04, uv_tile=3.0)
        b_fabric.add_cylinder(sx + 1.32, 1.24, sz - 2.48, 0.24, 0.24, 4.96, segs=10, rot_x=math.pi * 0.5)
        # Backrest against window (-X)
        b_fabric.add_box(sx - 1.10, 2.15, sz, 0.65, 1.75, 5.08, uv_tile=3.0)
        # Sculpted armrests
        b_fabric.add_box(sx, 1.85, sz + 2.30, 2.72, 1.15, 0.50, uv_tile=3.0)
        b_fabric.add_box(sx, 1.85, sz - 2.30, 2.72, 1.15, 0.50, uv_tile=3.0)
        # Plump rounded teal & espresso throw cushions
        b_teal.add_sphere(sx - 0.54, 1.92, sz - 1.35, 0.25, 0.50, 0.52, rings=8, segs=12)
        b_esp.add_sphere(sx - 0.54, 1.88, sz + 1.35, 0.24, 0.48, 0.48, rings=8, segs=12)

    add_sofa(-9.0, 5.5)
    add_sofa(-9.0, -4.4)

    # Oak side table between the two sofas (X=-9.2, Z=+0.55)
    b_oak.add_box(-9.2, 1.48, 0.55, 1.35, 0.16, 1.35, uv_tile=2.0)
    b_oak.add_box(-9.75, 0.74, 0.0, 0.14, 1.48, 0.14)
    b_oak.add_box(-8.65, 0.74, 0.0, 0.14, 1.48, 0.14)
    b_oak.add_box(-9.75, 0.74, 1.1, 0.14, 1.48, 0.14)
    b_oak.add_box(-8.65, 0.74, 1.1, 0.14, 1.48, 0.14)
    b_pot.add_cylinder(-9.2, 1.56, 0.55, 0.18, 0.22, 0.34, segs=12)
    b_pink.add_sphere(-9.2, 2.02, 0.55, 0.34, 0.24, 0.34, rings=6, segs=10)

    def add_round_table(tx, tz, r=1.55):
        # Black circular floor base + central column + beveled oak top (Y = 2.75)
        b_black.add_cylinder(tx, 0.0, tz, r * 0.52, r * 0.48, 0.10, segs=20)
        b_black.add_cylinder(tx, 0.10, tz, 0.15, 0.15, 2.55, segs=14)
        b_oak.add_cylinder(tx, 2.65, tz, r, r, 0.14, segs=24)

    def add_tub_chair(cx, cz, yaw):
        c, s = math.cos(yaw), math.sin(yaw)

        def rot_p(lx, lz):
            return (cx + lx * c + lz * s, cz - lx * s + lz * c)

        # 4 splayed black tapered legs
        for lx, lz in [(-0.62, -0.60), (0.62, -0.60), (0.58, 0.58), (-0.58, 0.58)]:
            px, pz = rot_p(lx, lz)
            b_black.add_cylinder(px, 0.0, pz, 0.05, 0.075, 1.38, segs=8)
        # Round seat cushion
        b_fabric.add_lathe(cx, 1.32, cz, [
            (0.0, 0.0), (0.82, 0.0), (0.94, 0.10), (0.94, 0.30), (0.84, 0.38), (0.0, 0.38)
        ], segs=18)
        # Curved wrap-around horseshoe backrest (sweeping 220 deg around local -Z back)
        segs_back = 14
        r_out, r_in = 0.98, 0.74
        for i in range(segs_back):
            t0 = i / segs_back
            t1 = (i + 1) / segs_back
            # Angle centered around local -Z (ang = -pi/2) spanning -1.18*pi..+0.18*pi
            a0 = -math.pi * 1.12 + t0 * (math.pi * 1.24)
            a1 = -math.pi * 1.12 + t1 * (math.pi * 1.24)
            # Taper armrest height down at ends
            h0 = 1.48 + 1.15 * math.sin(t0 * math.pi) ** 0.65
            h1 = 1.48 + 1.15 * math.sin(t1 * math.pi) ** 0.65
            ox0, oz0 = rot_p(r_out * math.cos(a0), r_out * math.sin(a0))
            ox1, oz1 = rot_p(r_out * math.cos(a1), r_out * math.sin(a1))
            ix0, iz0 = rot_p(r_in * math.cos(a0), r_in * math.sin(a0))
            ix1, iz1 = rot_p(r_in * math.cos(a1), r_in * math.sin(a1))
            # Outer face
            b_fabric.add_quad((ox1, 1.38, oz1), (ox0, 1.38, oz0), (ox0, h0, oz0), (ox1, h1, oz1), uv_scale=(0.4, 0.8))
            # Inner face
            b_fabric.add_quad((ix0, 1.38, iz0), (ix1, 1.38, iz1), (ix1, h1, iz1), (ix0, h0, iz0), uv_scale=(0.4, 0.8))
            # Top rim
            b_fabric.add_quad((ox0, h0, oz0), (ix0, h0, iz0), (ix1, h1, iz1), (ox1, h1, oz1), uv_scale=(0.4, 0.2))

    # Arrange 4 round oak tables + tub chairs down left side exactly like ref_cafe.jpg
    add_round_table(-5.4, 5.4, r=1.55)
    add_tub_chair(-6.5, 3.0, yaw=0.25)
    add_tub_chair(-3.2, 5.5, yaw=-1.45)

    add_round_table(-5.4, -1.6, r=1.50)
    add_tub_chair(-6.5, -3.9, yaw=0.35)
    add_tub_chair(-3.2, -1.5, yaw=-1.55)

    add_round_table(-5.2, -8.8, r=1.45)
    add_tub_chair(-3.4, -8.5, yaw=-1.35)
    add_tub_chair(-6.6, -10.8, yaw=0.45)

    add_round_table(-4.8, -15.6, r=1.40)
    add_tub_chair(-2.6, -15.4, yaw=-1.40)
    add_tub_chair(0.2, -16.8, yaw=-0.85)

    # Latte cup + Brass "PAWS WELCOME" tent on front café table (-5.4, 2.79, 5.4)
    b_pot.add_cylinder(-5.2, 2.79, 5.5, 0.34, 0.34, 0.04, segs=14)
    b_pot.add_cylinder(-5.2, 2.83, 5.5, 0.16, 0.22, 0.26, segs=14)
    b_latte = mb("LatteFoam", m_latte_top)
    b_latte.add_cylinder(-5.2, 3.06, 5.5, 0.20, 0.20, 0.02, segs=14)
    b_brass = mb("BrassTableTent", m_brass)
    b_brass.add_box(-5.7, 2.95, 5.2, 0.36, 0.32, 0.14, rot_y=0.4)

    # ------------------------------------------------------------------
    # 8. Glossy White Planters with Layered Green Broadleaf Ficus Plants
    # ------------------------------------------------------------------
    b_soil = mb("PlanterSoil", m_soil)
    b_branch = mb("BranchWood", m_wood_branch)
    b_leaf1 = mb("FoliageDark", m_leaf)
    b_leaf2 = mb("FoliageBright", m_leaf_bright)

    def add_potted_plant(px, pz, scale=1.0, seed=1):
        rng = np.random.default_rng(seed)
        # Tapered white ceramic planter
        b_pot.add_lathe(px, 0.0, pz, [
            (0.0, 0.0), (0.64 * scale, 0.0), (0.94 * scale, 1.55 * scale),
            (0.96 * scale, 1.68 * scale), (0.84 * scale, 1.68 * scale), (0.80 * scale, 1.48 * scale), (0.0, 1.48 * scale)
        ], segs=18)
        b_soil.add_cylinder(px, 1.44 * scale, pz, 0.78 * scale, 0.78 * scale, 0.05, segs=14)
        # Main trunk + 5 radiating branches + dense angled broad leaves
        b_branch.add_cylinder(px, 1.45 * scale, pz, 0.09 * scale, 0.05 * scale, 1.85 * scale, segs=8)
        for bi in range(6):
            ang = bi * (math.tau / 6.0) + rng.uniform(-0.2, 0.2)
            tilt = rng.uniform(0.32, 0.65)
            bx = px + math.cos(ang) * 0.75 * scale
            bz = pz + math.sin(ang) * 0.75 * scale
            by = (2.15 + (bi % 3) * 0.45) * scale
            b_branch.add_curved_tube([
                (px, (1.8 + (bi % 2) * 0.3) * scale, pz),
                ((px + bx) * 0.5, by - 0.15 * scale, (pz + bz) * 0.5),
                (bx, by + 0.35 * scale, bz),
            ], [0.05 * scale, 0.035 * scale, 0.02 * scale], segs=6)
            for li in range(5):
                la = ang + (li - 2) * 0.48
                lx = bx + math.cos(la) * 0.42 * scale
                lz = bz + math.sin(la) * 0.42 * scale
                ly = by + 0.25 * scale + rng.uniform(-0.22, 0.38) * scale
                target = b_leaf1 if (li + bi) % 2 == 0 else b_leaf2
                target.add_sphere(lx, ly, lz, 0.38 * scale, 0.07 * scale, 0.24 * scale, rings=4, segs=8)

    add_potted_plant(-8.7, 11.4, scale=1.22, seed=11)
    add_potted_plant(-9.8, -0.9, scale=0.92, seed=22)
    add_potted_plant(-9.6, -10.5, scale=1.08, seed=33)
    add_potted_plant(-0.8, -19.6, scale=0.88, seed=44)
    add_potted_plant(10.2, 11.2, scale=1.05, seed=55)

    # ------------------------------------------------------------------
    # 9. Exterior Coastal Boardwalk, Wildflowers, Palms & Sky/Ocean Wrap
    # ------------------------------------------------------------------
    b_coast = mb("CoastalBackdrop", m_coast_bg)
    # Curved wrap-around coastal sky & sea cyclorama outside left (-X) and back (-Z) windows
    cy_pts = []
    # Span from front-left (-32, +24) -> back-left (-36, -38) -> back-right (+18, -38)
    arc_bg = [
        (-28.0, 22.0), (-32.0, 8.0), (-34.0, -8.0), (-35.0, -24.0),
        (-26.0, -35.0), (-12.0, -37.0), (4.0, -37.0), (18.0, -34.0),
    ]
    n_bg = len(arc_bg)
    for i in range(n_bg - 1):
        x0, z0 = arc_bg[i]
        x1, z1 = arc_bg[i + 1]
        u0, u1 = i / (n_bg - 1), (i + 1) / (n_bg - 1)
        # Note glTF exporter flips uv_y = 1.0 - uv_y: so (u, 0.0) at y_bot=-4.0 -> v_gltf=1.0 (sand bottom),
        # and (u, 1.0) at y_top=22.0 -> v_gltf=0.0 (sky zenith top). Ocean horizon v=0.58 sits at y=4.6!
        b_coast.add_tri_raw((x0, -4.0, z0), (x1, -4.0, z1), (x1, 22.0, z1), (u0, 0.0), (u1, 0.0), (u1, 1.0))
        b_coast.add_tri_raw((x0, -4.0, z0), (x1, 22.0, z1), (x0, 22.0, z0), (u0, 0.0), (u1, 1.0), (u0, 1.0))

    # Exterior low planter bed + boardwalk deck + wooden seaside fence
    b_board = mb("BoardwalkTimber", m_boardwalk)
    b_coral = mb("FlowersCoral", m_flower_coral)
    # Exterior ground & timber boardwalk outside left & back glass
    b_board.add_quad((-22.0, 0.0, 18.0), (-11.9, 0.0, 18.0), (-11.9, 0.0, -26.0), (-22.0, 0.0, -26.0), uv_scale=(3, 12))
    b_board.add_quad((-22.0, 0.0, -22.2), (6.0, 0.0, -22.2), (6.0, 0.0, -28.0), (-22.0, 0.0, -28.0), uv_scale=(8, 2))
    # Wooden seaside railing posts & rails at X = -18.5 & Z = -26.2
    b_board.add_box(-18.5, 2.8, -4.0, 0.25, 0.25, 36.0)
    b_board.add_box(-18.5, 1.5, -4.0, 0.22, 0.22, 36.0)
    for fz in range(-22, 16, 4):
        b_board.add_box(-18.5, 1.6, fz, 0.35, 3.2, 0.35)
    b_board.add_box(-6.0, 2.8, -26.2, 24.0, 0.25, 0.25)
    for fx in range(-18, 6, 4):
        b_board.add_box(fx, 1.6, -26.2, 0.35, 3.2, 0.35)

    # Low green shrubs & coral-pink flower clusters right outside glass (X=-13.8 & Z=-23.5)
    rng_fl = np.random.default_rng(91)
    for fz in np.linspace(-21.0, 11.0, 22):
        b_leaf1.add_sphere(-13.6 + rng_fl.uniform(-0.4, 0.4), 1.3, float(fz), 1.1, 0.9, 1.1, rings=5, segs=8)
        for _ in range(3):
            b_coral.add_sphere(-13.2 + rng_fl.uniform(-0.7, 0.4), rng_fl.uniform(1.5, 2.6), float(fz) + rng_fl.uniform(-0.5, 0.5),
                               0.22, 0.22, 0.22, rings=4, segs=6)
    for fx in np.linspace(-12.5, 0.5, 10):
        b_leaf2.add_sphere(float(fx), 1.2, -23.6, 1.1, 0.85, 1.0, rings=5, segs=8)
        b_pink.add_sphere(float(fx) + 0.2, 2.1, -23.4, 0.24, 0.24, 0.24, rings=4, segs=6)

    # 6 Curved Coconut Palm Trees outside the curtain wall
    b_ptrunk = mb("PalmTrunks", m_palm_trunk)
    b_pfrond = mb("PalmFronds", m_palm_frond)

    def add_palm_tree(px, pz, height=15.0, lean_x=2.2, lean_z=1.0):
        spine = []
        radii = []
        steps = 8
        for s_i in range(steps):
            t = s_i / (steps - 1)
            cx_s = px + lean_x * (t ** 1.6)
            cy_s = t * height
            cz_s = pz + lean_z * (t ** 1.6)
            spine.append((cx_s, cy_s, cz_s))
            radii.append(0.42 * (1.0 - 0.52 * t))
        b_ptrunk.add_curved_tube(spine, radii, segs=8)
        # Subtle bark rings along coconut trunk
        for rk in range(1, 9):
            rt = rk / 9.0
            rx_s = px + lean_x * (rt ** 1.6)
            ry_s = rt * height
            rz_s = pz + lean_z * (rt ** 1.6)
            rr = 0.44 * (1.0 - 0.50 * rt)
            b_branch.add_cylinder(rx_s, ry_s, rz_s, rr, rr * 0.94, 0.14, segs=8)
        top_x, top_y, top_z = spine[-1]
        # 12 arched drooping feathered palm fronds
        for fi in range(12):
            ang = (fi / 12.0) * math.tau + 0.15
            ca, sa = math.cos(ang), math.sin(ang)
            f_len = 5.8
            for seg in range(5):
                t0 = seg / 5.0
                t1 = (seg + 1) / 5.0
                r0 = t0 * f_len
                r1 = t1 * f_len
                y0 = top_y + math.sin(t0 * math.pi * 0.78) * 1.45 - (t0 ** 2) * 2.35
                y1 = top_y + math.sin(t1 * math.pi * 0.78) * 1.45 - (t1 ** 2) * 2.35
                w0 = 0.50 * math.sin(max(0.15, t0) * math.pi)
                w1 = 0.50 * math.sin(max(0.15, t1) * math.pi)
                # Frond ribbon perpendicular to direction
                px0, pz0 = -sa * w0, ca * w0
                px1, pz1 = -sa * w1, ca * w1
                a0 = (top_x + ca * r0 - px0, y0, top_z + sa * r0 - pz0)
                b0 = (top_x + ca * r0 + px0, y0, top_z + sa * r0 + pz0)
                b1 = (top_x + ca * r1 + px1, y1, top_z + sa * r1 + pz1)
                a1 = (top_x + ca * r1 - px1, y1, top_z + sa * r1 - pz1)
                b_pfrond.add_quad(a0, b0, b1, a1, uv_scale=(1, 1))

    add_palm_tree(-20.0, 5.5, height=16.5, lean_x=2.4, lean_z=-1.2)
    add_palm_tree(-21.5, -5.0, height=15.0, lean_x=2.0, lean_z=1.5)
    add_palm_tree(-20.5, -16.5, height=16.0, lean_x=2.2, lean_z=0.8)
    add_palm_tree(-14.0, -28.0, height=15.2, lean_x=1.6, lean_z=1.8)
    add_palm_tree(-5.2, -29.0, height=14.6, lean_x=-1.4, lean_z=1.5)
    add_palm_tree(1.8, -28.5, height=15.5, lean_x=-1.8, lean_z=1.2)

    # Old-Money Boiserie, Coffee Library South Portal, Shadow-Box GeoArt Frame & Hand-Knotted Carpets
    om_mats = {
        "marmorino": m_wall_white,
        "walnut_fluted": m_walnut_fluted,
        "walnut_dark": m_walnut_dark,
        "brass": m_brass,
        "travertine": m_travertine,
        "rug_salon": m_rug_salon,
        "rug_aubusson": m_rug_aubusson,
        "warm_glow": m_led_warm,
        "glass_reed": m_glass_reed,
        "ceramic": m_pot_white,
        "oak": m_oak,
    }
    build_cafe_oldmoney_millwork(mb, om_mats)

    # ------------------------------------------------------------------
    # Compile Binary glTF 2.0 (.glb)
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

    # Embed textures
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
        # Flip V for glTF top-left origin consistency
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
        "asset": {"version": "2.0", "generator": "bruce-happiness-club/build_cafe_glb.py"},
        "scene": 0,
        "scenes": [{"name": "CoastalCafe", "nodes": list(range(len(nodes)))}],
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
