"""
Uncompressed standard glTF 2.0 (.glb) builder for bruce_day_sailer.
Supports SHA-256 image deduplication, sRGB baseColor, linear ORM + +Y normal maps,
precomputed VEC4 vertex tangents, KHR_materials_clearcoat, KHR_materials_transmission,
KHR_materials_ior, and named anchor nodes.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import os
import struct
from typing import Sequence

import numpy as np
from PIL import Image


def encode_image(arr: np.ndarray, fmt: str = "PNG", quality: int = 90) -> bytes:
    """Encode an HxWx3 uint8 numpy array to PNG or JPEG bytes."""
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB")
    buf = io.BytesIO()
    if fmt.upper() == "JPEG":
        img.save(buf, format="JPEG", quality=quality, optimize=True)
    else:
        img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _normalize_v3(v: np.ndarray, fallback=(0.0, 1.0, 0.0)) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    ok = n[..., 0] > 1e-8
    out = np.empty_like(v, dtype=np.float32)
    out[ok] = v[ok] / n[ok]
    if not np.all(ok):
        out[~ok] = np.array(fallback, dtype=np.float32)
    return out


class YachtMesh:
    """Collects geometry for a single PBR material."""

    def __init__(self, name: str, material_idx: int):
        self.name = name
        self.material_idx = material_idx
        self.pos: list[tuple[float, float, float]] = []
        self.nrm: list[tuple[float, float, float]] = []
        self.uv: list[tuple[float, float]] = []
        self.idx: list[int] = []

    def add_tri(
        self,
        p0,
        p1,
        p2,
        uv0=(0.0, 0.0),
        uv1=(1.0, 0.0),
        uv2=(1.0, 1.0),
        n0=None,
        n1=None,
        n2=None,
    ):
        e1 = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
        e2 = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
        nx = e1[1] * e2[2] - e1[2] * e2[1]
        ny = e1[2] * e2[0] - e1[0] * e2[2]
        nz = e1[0] * e2[1] - e1[1] * e2[0]
        ln = math.sqrt(nx * nx + ny * ny + nz * nz)
        if ln < 1e-11:
            return
        fn = (nx / ln, ny / ln, nz / ln)
        base = len(self.pos)
        self.pos.extend((tuple(map(float, p0)), tuple(map(float, p1)), tuple(map(float, p2))))
        self.nrm.extend((n0 or fn, n1 or fn, n2 or fn))
        self.uv.extend(((float(uv0[0]), float(uv0[1])), (float(uv1[0]), float(uv1[1])), (float(uv2[0]), float(uv2[1]))))
        self.idx.extend((base, base + 1, base + 2))

    def add_quad(self, p0, p1, p2, p3, uv0=(0, 0), uv1=(1, 0), uv2=(1, 1), uv3=(0, 1), flip=False):
        if flip:
            self.add_tri(p0, p2, p1, uv0, uv2, uv1)
            self.add_tri(p0, p3, p2, uv0, uv3, uv2)
        else:
            self.add_tri(p0, p1, p2, uv0, uv1, uv2)
            self.add_tri(p0, p2, p3, uv0, uv2, uv3)

    def add_box(self, center, size, uv_tile=(1.0, 1.0), rot_y=0.0):
        cx, cy, cz = center
        sx, sy, sz = size
        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
        c, s = math.cos(rot_y), math.sin(rot_y)

        def xf(lx, ly, lz):
            return (cx + lx * c + lz * s, cy + ly, cz - lx * s + lz * c)

        tu, tv = (uv_tile if isinstance(uv_tile, (tuple, list)) else (uv_tile, uv_tile))
        tu = tu or 1.0
        tv = tv or 1.0
        faces = (
            (xf(-hx, -hy, hz), xf(hx, -hy, hz), xf(hx, hy, hz), xf(-hx, hy, hz), sx / tu, sy / tv),
            (xf(hx, -hy, -hz), xf(-hx, -hy, -hz), xf(-hx, hy, -hz), xf(hx, hy, -hz), sx / tu, sy / tv),
            (xf(hx, -hy, hz), xf(hx, -hy, -hz), xf(hx, hy, -hz), xf(hx, hy, hz), sz / tu, sy / tv),
            (xf(-hx, -hy, -hz), xf(-hx, -hy, hz), xf(-hx, hy, hz), xf(-hx, hy, -hz), sz / tu, sy / tv),
            (xf(-hx, hy, hz), xf(hx, hy, hz), xf(hx, hy, -hz), xf(-hx, hy, -hz), sx / tu, sz / tv),
            (xf(-hx, -hy, -hz), xf(hx, -hy, -hz), xf(hx, -hy, hz), xf(-hx, -hy, hz), sx / tu, sz / tv),
        )
        for p0, p1, p2, p3, su, sv in faces:
            self.add_quad(p0, p1, p2, p3, (0, 0), (su, 0), (su, sv), (0, sv))

    def add_chamfer_box(self, center, size, bevel=0.004, uv_tile=1.0, rot_y=0.0):
        cx, cy, cz = center
        sx, sy, sz = size
        b = min(bevel, sx * 0.24, sy * 0.24, sz * 0.24)
        if b <= 1e-5:
            self.add_box(center, size, uv_tile=uv_tile, rot_y=rot_y)
            return
        tu, tv = (uv_tile if isinstance(uv_tile, (tuple, list)) else (uv_tile, uv_tile))
        tu = tu or 1.0
        tv = tv or 1.0
        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
        ix, iy, iz = hx - b, hy - b, hz - b
        c, s = math.cos(rot_y), math.sin(rot_y)

        def xf(lx, ly, lz):
            return (cx + lx * c + lz * s, cy + ly, cz - lx * s + lz * c)

        wx, wy, wz = (sx - 2 * b) / tu, (sy - 2 * b) / tv, (sz - 2 * b) / tv
        bu = max(0.02, b / tu)
        bv = max(0.02, b / tv)
        # 6 core flat faces
        self.add_quad(xf(-ix, -iy, hz), xf(ix, -iy, hz), xf(ix, iy, hz), xf(-ix, iy, hz), (0, 0), (wx, 0), (wx, wy), (0, wy))
        self.add_quad(xf(ix, -iy, -hz), xf(-ix, -iy, -hz), xf(-ix, iy, -hz), xf(ix, iy, -hz), (0, 0), (wx, 0), (wx, wy), (0, wy))
        self.add_quad(xf(hx, -iy, iz), xf(hx, -iy, -iz), xf(hx, iy, -iz), xf(hx, iy, iz), (0, 0), (wz, 0), (wz, wy), (0, wy))
        self.add_quad(xf(-hx, -iy, -iz), xf(-hx, -iy, iz), xf(-hx, iy, iz), xf(-hx, iy, -iz), (0, 0), (wz, 0), (wz, wy), (0, wy))
        self.add_quad(xf(-ix, hy, iz), xf(ix, hy, iz), xf(ix, hy, -iz), xf(-ix, hy, -iz), (0, 0), (wx, 0), (wx, wz), (0, wz))
        self.add_quad(xf(-ix, -hy, -iz), xf(ix, -hy, -iz), xf(ix, -hy, iz), xf(-ix, -hy, iz), (0, 0), (wx, 0), (wx, wz), (0, wz))
        # 12 edge chamfers
        for q in (
            (xf(-ix, iy, hz), xf(ix, iy, hz), xf(ix, hy, iz), xf(-ix, hy, iz), wx, bv),
            (xf(ix, iy, -hz), xf(-ix, iy, -hz), xf(-ix, hy, -iz), xf(ix, hy, -iz), wx, bv),
            (xf(-hx, iy, -iz), xf(-hx, iy, iz), xf(-ix, hy, iz), xf(-ix, hy, -iz), wz, bv),
            (xf(hx, iy, iz), xf(hx, iy, -iz), xf(ix, hy, -iz), xf(ix, hy, iz), wz, bv),
            (xf(ix, -iy, hz), xf(-ix, -iy, hz), xf(-ix, -hy, iz), xf(ix, -hy, iz), wx, bv),
            (xf(-ix, -iy, -hz), xf(ix, -iy, -hz), xf(ix, -hy, -iz), xf(-ix, -hy, -iz), wx, bv),
            (xf(-hx, -iy, iz), xf(-hx, -iy, -iz), xf(-ix, -hy, -iz), xf(-ix, -hy, iz), wz, bv),
            (xf(hx, -iy, -iz), xf(hx, -iy, iz), xf(ix, -hy, iz), xf(ix, -hy, -iz), wz, bv),
            (xf(ix, -iy, hz), xf(hx, -iy, iz), xf(hx, iy, iz), xf(ix, iy, hz), bu, wy),
            (xf(-hx, -iy, iz), xf(-ix, -iy, hz), xf(-ix, iy, hz), xf(-hx, iy, iz), bu, wy),
            (xf(-ix, -iy, -hz), xf(-hx, -iy, -iz), xf(-hx, iy, -iz), xf(-ix, iy, -hz), bu, wy),
            (xf(hx, -iy, -iz), xf(ix, -iy, -hz), xf(ix, iy, -hz), xf(hx, iy, -iz), bu, wy),
        ):
            self.add_quad(q[0], q[1], q[2], q[3], (0, 0), (q[4], 0), (q[4], q[5]), (0, q[5]))
        # 8 corner triangles
        for tri in (
            (xf(ix, iy, hz), xf(hx, iy, iz), xf(ix, hy, iz)),
            (xf(-hx, iy, iz), xf(-ix, iy, hz), xf(-ix, hy, iz)),
            (xf(-ix, iy, -hz), xf(-hx, iy, -iz), xf(-ix, hy, -iz)),
            (xf(hx, iy, -iz), xf(ix, iy, -hz), xf(ix, hy, -iz)),
            (xf(hx, -iy, iz), xf(ix, -iy, hz), xf(ix, -hy, iz)),
            (xf(-ix, -iy, hz), xf(-hx, -iy, iz), xf(-ix, -hy, iz)),
            (xf(-hx, -iy, -iz), xf(-ix, -iy, -hz), xf(-ix, -hy, -iz)),
            (xf(ix, -iy, -hz), xf(hx, -iy, -iz), xf(ix, -hy, -iz)),
        ):
            self.add_tri(tri[0], tri[1], tri[2], (0, 0), (bu, 0), (0.5 * bu, bv))

    def add_tube(self, p0, p1, r0, r1=None, segs=20, cap=True, uv_scale=(1.0, 1.0)):
        r1 = r0 if r1 is None else r1
        a = np.array(p0, dtype=np.float64)
        b = np.array(p1, dtype=np.float64)
        axis = b - a
        length = np.linalg.norm(axis)
        if length < 1e-8:
            return
        w = axis / length
        ref = np.array([0.0, 0.0, 1.0]) if abs(w[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
        u_ax = np.cross(ref, w)
        u_ax /= np.linalg.norm(u_ax)
        v_ax = np.cross(w, u_ax)

        ring0, ring1 = [], []
        for i in range(segs + 1):
            ang = 2.0 * math.pi * (i / segs)
            ca, sa = math.cos(ang), math.sin(ang)
            n = u_ax * ca + v_ax * sa
            ring0.append((a + n * r0, n, i / segs))
            ring1.append((b + n * r1, n, i / segs))

        su, sv = uv_scale
        base = len(self.pos)
        for i in range(segs):
            pa, na, ua = ring0[i]
            pb, nb, ub = ring0[i + 1]
            pc, nc, uc = ring1[i + 1]
            pd, nd, ud = ring1[i]
            self.add_tri(pa, pb, pc, (ua * su, 0.0), (ub * su, 0.0), (uc * su, sv), tuple(na), tuple(nb), tuple(nc))
            self.add_tri(pa, pc, pd, (ua * su, 0.0), (uc * su, sv), (ud * su, sv), tuple(na), tuple(nc), tuple(nd))
        if cap:
            for i in range(segs):
                pa, _, ua = ring0[i]
                pb, _, ub = ring0[i + 1]
                self.add_tri(tuple(a), tuple(pb), tuple(pa), (0.5, 0.5), (ub, 0.0), (ua, 0.0), tuple(-w), tuple(-w), tuple(-w))
                pc, _, uc = ring1[i]
                pd, _, ud = ring1[i + 1]
                self.add_tri(tuple(b), tuple(pc), tuple(pd), (0.5, 0.5), (uc, 1.0), (ud, 1.0), tuple(w), tuple(w), tuple(w))
        _ = base

    def add_grid(self, pos_grid: np.ndarray, uv_grid: np.ndarray, flip=False, smooth_normals=True, seam_u=False):
        """pos_grid: (Nu, Nv, 3), uv_grid: (Nu, Nv, 2). Emits indexed triangles with optional smooth normals."""
        nu, nv, _ = pos_grid.shape
        if nu < 2 or nv < 2:
            return
        if not smooth_normals:
            for i in range(nu - 1):
                for j in range(nv - 1):
                    p00, p10, p11, p01 = pos_grid[i, j], pos_grid[i + 1, j], pos_grid[i + 1, j + 1], pos_grid[i, j + 1]
                    t00, t10, t11, t01 = uv_grid[i, j], uv_grid[i + 1, j], uv_grid[i + 1, j + 1], uv_grid[i, j + 1]
                    self.add_quad(p00, p10, p11, p01, t00, t10, t11, t01, flip=flip)
            return

        n_acc = np.zeros_like(pos_grid, dtype=np.float64)
        for i in range(nu - 1):
            for j in range(nv - 1):
                p00 = pos_grid[i, j]
                p10 = pos_grid[i + 1, j]
                p11 = pos_grid[i + 1, j + 1]
                p01 = pos_grid[i, j + 1]
                n1 = np.cross(p10 - p00, p11 - p00)
                n2 = np.cross(p11 - p00, p01 - p00)
                fn = -(n1 + n2) if flip else (n1 + n2)
                n_acc[i, j] += fn
                n_acc[i + 1, j] += fn
                n_acc[i + 1, j + 1] += fn
                n_acc[i, j + 1] += fn
        if seam_u:
            avg = n_acc[0] + n_acc[-1]
            n_acc[0] = avg
            n_acc[-1] = avg
        norms = _normalize_v3(n_acc.reshape(-1, 3)).reshape(nu, nv, 3)

        base = len(self.pos)
        flat_p = pos_grid.reshape(-1, 3)
        flat_n = norms.reshape(-1, 3)
        flat_uv = uv_grid.reshape(-1, 2)
        for k in range(len(flat_p)):
            self.pos.append((float(flat_p[k, 0]), float(flat_p[k, 1]), float(flat_p[k, 2])))
            self.nrm.append((float(flat_n[k, 0]), float(flat_n[k, 1]), float(flat_n[k, 2])))
            self.uv.append((float(flat_uv[k, 0]), float(flat_uv[k, 1])))
        for i in range(nu - 1):
            for j in range(nv - 1):
                a = base + i * nv + j
                b = base + (i + 1) * nv + j
                c = base + (i + 1) * nv + (j + 1)
                d = base + i * nv + (j + 1)
                if flip:
                    self.idx.extend((a, c, b, a, d, c))
                else:
                    self.idx.extend((a, b, c, a, c, d))

    def add_prism(self, poly_xz: Sequence[tuple[float, float]], y0: float, y1: float, uv_tile: float = 1.0, caps=(True, True)):
        """Extrude a CCW XZ polygon (or star-convex deck) from y0 to y1."""
        pts = [tuple(p) for p in poly_xz]
        n = len(pts)
        if n < 3:
            return
        # Ensure CCW winding in XZ (signed area > 0 in (x, -z) == +Y up)
        area2 = sum(pts[i][0] * (-pts[(i + 1) % n][1]) - pts[(i + 1) % n][0] * (-pts[i][1]) for i in range(n))
        if area2 < 0:
            pts.reverse()
        cx = sum(p[0] for p in pts) / n
        cz = sum(p[1] for p in pts) / n
        tu = uv_tile or 1.0
        for i in range(n):
            x0, z0 = pts[i]
            x1, z1 = pts[(i + 1) % n]
            seg_l = math.hypot(x1 - x0, z1 - z0) / tu
            h = abs(y1 - y0) / tu
            self.add_quad((x0, y0, z0), (x1, y0, z1), (x1, y1, z1), (x0, y1, z0), (0, 0), (seg_l, 0), (seg_l, h), (0, h))
            if caps[0]:
                self.add_tri(
                    (cx, y1, cz),
                    (x0, y1, z0),
                    (x1, y1, z1),
                    (cx / tu, cz / tu),
                    (x0 / tu, z0 / tu),
                    (x1 / tu, z1 / tu),
                    (0, 1, 0),
                    (0, 1, 0),
                    (0, 1, 0),
                )
            if caps[1]:
                self.add_tri(
                    (cx, y0, cz),
                    (x1, y0, z1),
                    (x0, y0, z0),
                    (cx / tu, cz / tu),
                    (x1 / tu, z1 / tu),
                    (x0 / tu, z0 / tu),
                    (0, -1, 0),
                    (0, -1, 0),
                    (0, -1, 0),
                )


def _compute_tangents(pos: np.ndarray, nrm: np.ndarray, uv: np.ndarray, idx: np.ndarray) -> np.ndarray:
    """Compute valid MikkTSpace-compatible VEC4 tangents (unit xyz, w in {-1, 1})."""
    vcount = len(pos)
    t_acc = np.zeros((vcount, 3), dtype=np.float64)
    b_acc = np.zeros((vcount, 3), dtype=np.float64)

    tris = idx.reshape(-1, 3)
    p0 = pos[tris[:, 0]].astype(np.float64)
    p1 = pos[tris[:, 1]].astype(np.float64)
    p2 = pos[tris[:, 2]].astype(np.float64)
    w0 = uv[tris[:, 0]].astype(np.float64)
    w1 = uv[tris[:, 1]].astype(np.float64)
    w2 = uv[tris[:, 2]].astype(np.float64)

    e1 = p1 - p0
    e2 = p2 - p0
    du1 = w1[:, 0] - w0[:, 0]
    dv1 = w1[:, 1] - w0[:, 1]
    du2 = w2[:, 0] - w0[:, 0]
    dv2 = w2[:, 1] - w0[:, 1]

    det = du1 * dv2 - du2 * dv1
    inv_det = np.where(np.abs(det) > 1e-10, 1.0 / np.where(np.abs(det) > 1e-10, det, 1.0), 0.0)
    t_tri = (e1 * dv2[:, None] - e2 * dv1[:, None]) * inv_det[:, None]
    b_tri = (e2 * du1[:, None] - e1 * du2[:, None]) * inv_det[:, None]

    for corner in range(3):
        np.add.at(t_acc, tris[:, corner], t_tri)
        np.add.at(b_acc, tris[:, corner], b_tri)

    n = _normalize_v3(nrm).astype(np.float64)
    t_orth = t_acc - n * np.sum(n * t_acc, axis=1, keepdims=True)
    t_len = np.linalg.norm(t_orth, axis=1)
    bad = t_len < 1e-6
    if np.any(bad):
        up = np.where(np.abs(n[bad, 1:2]) < 0.9, np.array([0.0, 1.0, 0.0]), np.array([1.0, 0.0, 0.0]))
        t_orth[bad] = np.cross(up, n[bad])
    t_unit = _normalize_v3(t_orth)
    hand = np.sum(np.cross(n, t_unit) * b_acc, axis=1)
    w = np.where(hand < 0.0, -1.0, 1.0).astype(np.float32)

    tangents = np.empty((vcount, 4), dtype=np.float32)
    tangents[:, :3] = t_unit
    tangents[:, 3] = w
    return tangents


class YachtGLBBuilder:
    """Builds one modular uncompressed glTF 2.0 GLB asset."""

    def __init__(self, asset_id: str):
        self.asset_id = asset_id
        self._images: list[dict] = []
        self._image_bytes: list[bytes] = []
        self._image_hash_to_idx: dict[str, int] = {}
        self._textures: list[dict] = []
        self._tex_key_to_idx: dict[tuple[int, int], int] = {}
        self._samplers: list[dict] = [
            {"magFilter": 9729, "minFilter": 9987, "wrapS": 10497, "wrapT": 10497},
            {"magFilter": 9729, "minFilter": 9987, "wrapS": 33071, "wrapT": 33071},
        ]
        self._materials: list[dict] = []
        self._meshes: dict[int, YachtMesh] = {}
        self._anchors: list[tuple[str, tuple[float, float, float], tuple[float, float, float, float]]] = []
        self._ext_used: set[str] = set()

    def register_image(self, raw_bytes: bytes, mime_type: str = "image/png", name: str = "") -> int:
        digest = hashlib.sha256(raw_bytes).hexdigest()
        if digest in self._image_hash_to_idx:
            return self._image_hash_to_idx[digest]
        idx = len(self._images)
        self._image_hash_to_idx[digest] = idx
        self._image_bytes.append(raw_bytes)
        entry = {"mimeType": mime_type}
        if name:
            entry["name"] = name
        self._images.append(entry)
        return idx

    def _get_texture(self, image_idx: int, clamp: bool = False) -> int:
        sampler_idx = 1 if clamp else 0
        key = (image_idx, sampler_idx)
        if key not in self._tex_key_to_idx:
            self._tex_key_to_idx[key] = len(self._textures)
            self._textures.append({"sampler": sampler_idx, "source": image_idx})
        return self._tex_key_to_idx[key]

    def add_pbr_material(
        self,
        name: str,
        base_bytes: bytes | None = None,
        base_mime: str = "image/jpeg",
        orm_bytes: bytes | None = None,
        normal_bytes: bytes | None = None,
        normal_scale: float = 1.0,
        base_factor=(1.0, 1.0, 1.0, 1.0),
        roughness: float = 1.0,
        metalness: float = 0.0,
        clearcoat: float = 0.0,
        clearcoat_roughness: float = 0.0,
        transmission: float = 0.0,
        ior: float | None = None,
        emissive=(0.0, 0.0, 0.0),
        double_sided: bool = False,
        alpha_mode: str = "OPAQUE",
        clamp_uv: bool = False,
    ) -> int:
        pbr: dict = {
            "baseColorFactor": [float(x) for x in base_factor],
            "metallicFactor": float(metalness),
            "roughnessFactor": float(roughness),
        }
        if base_bytes is not None:
            img_i = self.register_image(base_bytes, base_mime, f"{name}_base")
            pbr["baseColorTexture"] = {"index": self._get_texture(img_i, clamp=clamp_uv)}
        mat: dict = {"name": name, "pbrMetallicRoughness": pbr}
        if orm_bytes is not None:
            orm_i = self.register_image(orm_bytes, "image/png", f"{name}_orm")
            tex_i = self._get_texture(orm_i, clamp=clamp_uv)
            pbr["metallicRoughnessTexture"] = {"index": tex_i}
            mat["occlusionTexture"] = {"index": tex_i, "strength": 1.0}
        if normal_bytes is not None:
            n_i = self.register_image(normal_bytes, "image/png", f"{name}_nrm")
            mat["normalTexture"] = {"index": self._get_texture(n_i, clamp=clamp_uv), "scale": float(normal_scale)}
        if any(float(c) > 1e-4 for c in emissive):
            mat["emissiveFactor"] = [float(c) for c in emissive]
        if double_sided:
            mat["doubleSided"] = True
        if alpha_mode != "OPAQUE":
            mat["alphaMode"] = alpha_mode

        exts = {}
        if clearcoat > 1e-4:
            exts["KHR_materials_clearcoat"] = {
                "clearcoatFactor": float(clearcoat),
                "clearcoatRoughnessFactor": float(clearcoat_roughness),
            }
            self._ext_used.add("KHR_materials_clearcoat")
        if transmission > 1e-4:
            exts["KHR_materials_transmission"] = {"transmissionFactor": float(transmission)}
            self._ext_used.add("KHR_materials_transmission")
        if ior is not None:
            exts["KHR_materials_ior"] = {"ior": float(ior)}
            self._ext_used.add("KHR_materials_ior")
        if exts:
            mat["extensions"] = exts

        idx = len(self._materials)
        self._materials.append(mat)
        return idx

    def mesh(self, material_idx: int, name: str | None = None) -> YachtMesh:
        if material_idx not in self._meshes:
            m_name = name or self._materials[material_idx]["name"]
            self._meshes[material_idx] = YachtMesh(m_name, material_idx)
        return self._meshes[material_idx]

    def add_anchor(self, name: str, pos: Sequence[float], rot=(0.0, 0.0, 0.0, 1.0)):
        self._anchors.append((name, (float(pos[0]), float(pos[1]), float(pos[2])), tuple(map(float, rot))))

    def export(self, out_path: str) -> dict:
        bin_buf = bytearray()
        buffer_views = []
        accessors = []

        def push_bv(raw: bytes, target: int | None = None) -> int:
            while len(bin_buf) % 4 != 0:
                bin_buf.append(0)
            offset = len(bin_buf)
            bin_buf.extend(raw)
            bv = {"buffer": 0, "byteOffset": offset, "byteLength": len(raw)}
            if target is not None:
                bv["target"] = target
            idx = len(buffer_views)
            buffer_views.append(bv)
            return idx

        def push_acc(arr: np.ndarray, comp_type: int, acc_type: str, target: int, calc_bounds: bool = False) -> int:
            raw = np.ascontiguousarray(arr).tobytes()
            bv_idx = push_bv(raw, target=target)
            acc = {
                "bufferView": bv_idx,
                "componentType": comp_type,
                "count": int(arr.shape[0]),
                "type": acc_type,
            }
            if calc_bounds:
                acc["min"] = [float(x) for x in arr.min(axis=0)]
                acc["max"] = [float(x) for x in arr.max(axis=0)]
            idx = len(accessors)
            accessors.append(acc)
            return idx

        texture_bytes = 0
        for i, img_raw in enumerate(self._image_bytes):
            texture_bytes += len(img_raw)
            self._images[i]["bufferView"] = push_bv(img_raw, target=None)

        gltf_meshes = []
        nodes = []
        scene_children = []
        total_tris = 0
        g_min = np.array([1e9, 1e9, 1e9], dtype=np.float64)
        g_max = np.array([-1e9, -1e9, -1e9], dtype=np.float64)

        for mat_idx, ym in sorted(self._meshes.items(), key=lambda kv: kv[0]):
            if not ym.idx:
                continue
            pos_arr = np.asarray(ym.pos, dtype=np.float32)
            nrm_arr = _normalize_v3(np.asarray(ym.nrm, dtype=np.float32))
            uv_arr = np.asarray(ym.uv, dtype=np.float32)
            idx_arr = np.asarray(ym.idx, dtype=np.uint32)
            tan_arr = _compute_tangents(pos_arr, nrm_arr, uv_arr, idx_arr)

            g_min = np.minimum(g_min, pos_arr.min(axis=0))
            g_max = np.maximum(g_max, pos_arr.max(axis=0))
            total_tris += len(idx_arr) // 3

            if len(pos_arr) < 65535:
                idx_typed = idx_arr.astype(np.uint16)
                idx_comp = 5123
            else:
                idx_typed = idx_arr.astype(np.uint32)
                idx_comp = 5125

            pos_acc = push_acc(pos_arr, 5126, "VEC3", 34962, calc_bounds=True)
            nrm_acc = push_acc(nrm_arr, 5126, "VEC3", 34962)
            tan_acc = push_acc(tan_arr, 5126, "VEC4", 34962)
            uv_acc = push_acc(uv_arr, 5126, "VEC2", 34962)
            ind_acc = push_acc(idx_typed, idx_comp, "SCALAR", 34963)

            m_idx = len(gltf_meshes)
            gltf_meshes.append({
                "name": ym.name,
                "primitives": [{
                    "attributes": {"POSITION": pos_acc, "NORMAL": nrm_acc, "TANGENT": tan_acc, "TEXCOORD_0": uv_acc},
                    "indices": ind_acc,
                    "material": mat_idx,
                    "mode": 4,
                }],
            })
            n_idx = len(nodes)
            nodes.append({"name": ym.name, "mesh": m_idx})
            scene_children.append(n_idx)

        anchor_map = {}
        for aname, apos, arot in self._anchors:
            n_idx = len(nodes)
            node = {"name": aname, "translation": [round(x, 5) for x in apos]}
            if arot != (0.0, 0.0, 0.0, 1.0):
                node["rotation"] = [round(x, 6) for x in arot]
            nodes.append(node)
            scene_children.append(n_idx)
            anchor_map[aname] = [round(x, 5) for x in apos]

        while len(bin_buf) % 4 != 0:
            bin_buf.append(0)

        gltf = {
            "asset": {"version": "2.0", "generator": "BruceClub-YachtKit-v1"},
            "scene": 0,
            "scenes": [{"name": self.asset_id, "nodes": scene_children}],
            "nodes": nodes,
            "meshes": gltf_meshes,
            "materials": self._materials,
            "textures": self._textures,
            "samplers": self._samplers if self._textures else [],
            "images": self._images,
            "accessors": accessors,
            "bufferViews": buffer_views,
            "buffers": [{"byteLength": len(bin_buf)}],
        }
        if not gltf["textures"]:
            gltf.pop("textures")
            gltf.pop("samplers")
            gltf.pop("images")
        if self._ext_used:
            gltf["extensionsUsed"] = sorted(self._ext_used)

        json_bytes = json.dumps(gltf, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        while len(json_bytes) % 4 != 0:
            json_bytes += b" "

        total_len = 12 + 8 + len(json_bytes) + 8 + len(bin_buf)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(struct.pack("<III", 0x46546C67, 2, total_len))
            f.write(struct.pack("<II", len(json_bytes), 0x4E4F534A))
            f.write(json_bytes)
            f.write(struct.pack("<II", len(bin_buf), 0x004E4942))
            f.write(bin_buf)

        return {
            "id": self.asset_id,
            "path": out_path,
            "file_bytes": total_len,
            "triangles": int(total_tris),
            "texture_bytes": int(texture_bytes),
            "material_count": len(self._materials),
            "world_aabb": [
                [round(float(x), 4) for x in g_min],
                [round(float(x), 4) for x in g_max],
            ],
            "anchors": anchor_map,
        }
