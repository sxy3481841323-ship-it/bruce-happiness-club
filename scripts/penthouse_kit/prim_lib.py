"""
Shared glTF 2.0 SceneContext and MeshBuilder primitives for Penthouse Duplex.
Scale: Y-up, standard uncompressed glTF 2.0 (.glb).
"""

import io
import json
import math
import os
import struct
import numpy as np
from PIL import Image


def encode_pil_image(img: Image.Image, fmt: str = "JPEG", quality: int = 88) -> tuple[bytes, str]:
    buf = io.BytesIO()
    if fmt.upper() == "PNG":
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue(), "image/png"
    img.convert("RGB").save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue(), "image/jpeg"


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
        self.positions.extend([tuple(p0), tuple(p1), tuple(p2)])
        self.normals.extend([n0 or fn, n1 or fn, n2 or fn])
        self.uvs.extend([tuple(uv0), tuple(uv1), tuple(uv2)])
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

    def add_rounded_box(self, cx, cy, cz, sx, sy, sz, bevel=0.06, uv_tile=0.0, rot_y=0.0):
        """Chamfered/beveled box with soft rounded silhouette for cushions and stone slabs."""
        b = min(bevel, sx * 0.22, sy * 0.22, sz * 0.22)
        if b <= 1e-4:
            self.add_box(cx, cy, cz, sx, sy, sz, uv_tile=uv_tile, rot_y=rot_y)
            return
        # Core cross slabs + 4 side chamfers (smooth luxury sofa & travertine edge look)
        self.add_box(cx, cy, cz, sx - 2 * b, sy, sz - 2 * b, uv_tile=uv_tile, rot_y=rot_y)
        self.add_box(cx, cy, cz, sx, sy - 2 * b, sz - 2 * b, uv_tile=uv_tile, rot_y=rot_y)
        self.add_box(cx, cy, cz, sx - 2 * b, sy - 2 * b, sz, uv_tile=uv_tile, rot_y=rot_y)

        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
        ix, iy, iz = hx - b, hy - b, hz - b
        c, s = math.cos(rot_y), math.sin(rot_y)

        def xf(lx, ly, lz):
            return (cx + lx * c + lz * s, cy + ly, cz - lx * s + lz * c)

        # Top/bottom horizontal bevel ribbons
        uv_x = max(0.25, (sx - 2 * b) / uv_tile) if uv_tile > 0 else 1.0
        uv_z = max(0.25, (sz - 2 * b) / uv_tile) if uv_tile > 0 else 1.0
        uv_y = max(0.25, (sy - 2 * b) / uv_tile) if uv_tile > 0 else 1.0
        b_uv = 0.15

        # Front/back top bevels
        self.add_quad(xf(-ix, iy, hz), xf(ix, iy, hz), xf(ix, hy, iz), xf(-ix, hy, iz), (uv_x, b_uv))
        self.add_quad(xf(ix, iy, -hz), xf(-ix, iy, -hz), xf(-ix, hy, -iz), xf(ix, hy, -iz), (uv_x, b_uv))
        # Left/right top bevels
        self.add_quad(xf(-hx, iy, -iz), xf(-hx, iy, iz), xf(-ix, hy, iz), xf(-ix, hy, -iz), (uv_z, b_uv))
        self.add_quad(xf(hx, iy, iz), xf(hx, iy, -iz), xf(ix, hy, -iz), xf(ix, hy, iz), (uv_z, b_uv))
        # Front/back bottom bevels
        self.add_quad(xf(ix, -iy, hz), xf(-ix, -iy, hz), xf(-ix, -hy, iz), xf(ix, -hy, iz), (uv_x, b_uv))
        self.add_quad(xf(-ix, -iy, -hz), xf(ix, -iy, -hz), xf(ix, -hy, -iz), xf(-ix, -hy, -iz), (uv_x, b_uv))
        # Left/right bottom bevels
        self.add_quad(xf(-hx, -iy, iz), xf(-hx, -iy, -iz), xf(-ix, -hy, -iz), xf(-ix, -hy, iz), (uv_z, b_uv))
        self.add_quad(xf(hx, -iy, -iz), xf(hx, -iy, iz), xf(ix, -hy, iz), xf(ix, -hy, -iz), (uv_z, b_uv))
        # Vertical 4 corner chamfers
        self.add_quad(xf(ix, -iy, hz), xf(hx, -iy, iz), xf(hx, iy, iz), xf(ix, iy, hz), (b_uv, uv_y))
        self.add_quad(xf(-hx, -iy, iz), xf(-ix, -iy, hz), xf(-ix, iy, hz), xf(-hx, iy, iz), (b_uv, uv_y))
        self.add_quad(xf(-ix, -iy, -hz), xf(-hx, -iy, -iz), xf(-hx, iy, -iz), xf(-ix, iy, -hz), (b_uv, uv_y))
        self.add_quad(xf(hx, -iy, -iz), xf(ix, -iy, -hz), xf(ix, iy, -hz), xf(hx, iy, -iz), (b_uv, uv_y))
        # Corner triangle caps (top + bottom)
        self.add_tri_raw(xf(ix, iy, hz), xf(hx, iy, iz), xf(ix, hy, iz))
        self.add_tri_raw(xf(-hx, iy, iz), xf(-ix, iy, hz), xf(-ix, hy, iz))
        self.add_tri_raw(xf(-ix, iy, -hz), xf(-hx, iy, -iz), xf(-ix, hy, -iz))
        self.add_tri_raw(xf(hx, iy, -iz), xf(ix, iy, -hz), xf(ix, hy, -iz))
        self.add_tri_raw(xf(hx, -iy, iz), xf(ix, -iy, hz), xf(ix, -hy, iz))
        self.add_tri_raw(xf(-ix, -iy, hz), xf(-hx, -iy, iz), xf(-ix, -hy, iz))
        self.add_tri_raw(xf(-hx, -iy, -iz), xf(-ix, -iy, -hz), xf(-ix, -hy, -iz))
        self.add_tri_raw(xf(ix, -iy, -hz), xf(hx, -iy, -iz), xf(ix, -hy, -iz))

    def add_cylinder(self, cx, y0, cz, r_bot, r_top, height, segs=18, rot_x=0.0, rot_z=0.0, cap_top=True, cap_bot=True):
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
                if r_i > 0:
                    self.add_tri_raw(p01, p00, p10, (u1, v0), (u0, v0), (u0, v1), n01, n00, n10)
                if r_i < rings - 1:
                    self.add_tri_raw(p01, p10, p11, (u1, v0), (u0, v1), (u1, v1), n01, n10, n11)

    def add_lathe(self, cx, y0, cz, profile, segs=22):
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

    def add_prism_strip(self, pts_xz, y_bot, y_top, uv_tile=4.0):
        n = len(pts_xz)
        for i in range(n - 1):
            ox0, oz0, ix0, iz0 = pts_xz[i]
            ox1, oz1, ix1, iz1 = pts_xz[i + 1]
            seg_len = math.hypot(ox1 - ox0, oz1 - oz0)
            u_s = max(0.25, seg_len / uv_tile)
            v_s = max(0.25, (y_top - y_bot) / uv_tile)
            self.add_quad((ox0, y_bot, oz0), (ox1, y_bot, oz1), (ox1, y_top, oz1), (ox0, y_top, oz0), uv_scale=(u_s, v_s))
            self.add_quad((ix1, y_bot, iz1), (ix0, y_bot, iz0), (ix0, y_top, iz0), (ix1, y_top, iz1), uv_scale=(u_s, v_s))
            self.add_quad((ox0, y_top, oz0), (ox1, y_top, oz1), (ix1, y_top, iz1), (ix0, y_top, iz0), uv_scale=(u_s, 0.5))
            self.add_quad((ix0, y_bot, iz0), (ix1, y_bot, iz1), (ox1, y_bot, oz1), (ox0, y_bot, oz0), uv_scale=(u_s, 0.5))
        ox0, oz0, ix0, iz0 = pts_xz[0]
        self.add_quad((ix0, y_bot, iz0), (ox0, y_bot, oz0), (ox0, y_top, oz0), (ix0, y_top, iz0))
        oxe, oze, ixe, ize = pts_xz[-1]
        self.add_quad((oxe, y_bot, oze), (ixe, y_bot, ize), (ixe, y_top, ize), (oxe, y_top, oze))

    def add_curved_tube(self, spine_pts, radii, segs=10):
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

        for i in range(n_pts - 1):
            r0 = rings[i]
            r1 = rings[i + 1]
            v0 = i / max(1, n_pts - 1)
            v1 = (i + 1) / max(1, n_pts - 1)
            for s_i in range(segs):
                sn = (s_i + 1) % segs
                p00, n00 = r0[s_i]
                p01, n01 = r0[sn]
                p10, n10 = r1[s_i]
                p11, n11 = r1[sn]
                u0 = s_i / segs
                u1 = (s_i + 1) / segs
                self.add_tri_raw(p00, p01, p11, (u0, v0), (u1, v0), (u1, v1), n00, n01, n11)
                self.add_tri_raw(p00, p11, p10, (u0, v0), (u1, v1), (u0, v1), n00, n11, n10)


class SceneContext:
    def __init__(self, scene_name: str = "PenthouseDuplex"):
        self.scene_name = scene_name
        self.images_data = []
        self.textures = []
        self.materials = []
        self.builders = {}

    def color_mat(self, name, rgba, roughness=0.5, metalness=0.0, alpha_blend=False, double_sided=False, emissive=None) -> int:
        mat = {
            "name": name,
            "pbrMetallicRoughness": {
                "baseColorFactor": [float(rgba[0]), float(rgba[1]), float(rgba[2]), float(rgba[3])],
                "roughnessFactor": float(roughness),
                "metalnessFactor": float(metalness),
            },
        }
        if alpha_blend:
            mat["alphaMode"] = "BLEND"
        if double_sided:
            mat["doubleSided"] = True
        if emissive is not None:
            mat["emissiveFactor"] = [float(emissive[0]), float(emissive[1]), float(emissive[2])]
        idx = len(self.materials)
        self.materials.append(mat)
        return idx

    def tex_mat(self, name, pil_img: Image.Image, roughness=0.5, metalness=0.0, fmt="JPEG", quality=88, emissive=None, double_sided=False) -> int:
        raw, mime = encode_pil_image(pil_img, fmt=fmt, quality=quality)
        img_idx = len(self.images_data)
        self.images_data.append((raw, mime))
        tex_idx = len(self.textures)
        self.textures.append({"sampler": 0, "source": img_idx})
        mat = {
            "name": name,
            "pbrMetallicRoughness": {
                "baseColorTexture": {"index": tex_idx},
                "roughnessFactor": float(roughness),
                "metalnessFactor": float(metalness),
            },
        }
        if double_sided:
            mat["doubleSided"] = True
        if emissive is not None:
            mat["emissiveFactor"] = [float(emissive[0]), float(emissive[1]), float(emissive[2])]
        idx = len(self.materials)
        self.materials.append(mat)
        return idx

    def mb(self, mesh_name: str, mat_idx: int) -> MeshBuilder:
        key = (mesh_name, int(mat_idx))
        if key not in self.builders:
            self.builders[key] = MeshBuilder(mesh_name, int(mat_idx))
        return self.builders[key]

    def export_glb(self, out_path: str) -> dict:
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

        for raw, mime in self.images_data:
            bv_idx = append_bytes(raw)
            gltf_images.append({"bufferView": bv_idx, "mimeType": mime})

        total_tris = 0
        g_min = [float("inf"), float("inf"), float("inf")]
        g_max = [float("-inf"), float("-inf"), float("-inf")]

        for (_, _), builder in self.builders.items():
            if not builder.indices:
                continue
            pos_arr = np.array(builder.positions, dtype=np.float32)
            nrm_arr = np.array(builder.normals, dtype=np.float32)
            uv_arr = np.array(builder.uvs, dtype=np.float32)
            if not np.isfinite(pos_arr).all() or not np.isfinite(nrm_arr).all():
                raise ValueError(f"Non-finite vertex data in mesh {builder.name}")
            # Flip V for glTF top-left origin consistency
            uv_arr[:, 1] = 1.0 - uv_arr[:, 1]

            idx_dtype = np.uint16 if len(builder.positions) < 65535 else np.uint32
            idx_comp = 5123 if idx_dtype == np.uint16 else 5125
            idx_arr = np.array(builder.indices, dtype=idx_dtype)
            total_tris += len(idx_arr) // 3

            pmin = pos_arr.min(axis=0).tolist()
            pmax = pos_arr.max(axis=0).tolist()
            for k in range(3):
                g_min[k] = min(g_min[k], pmin[k])
                g_max[k] = max(g_max[k], pmax[k])

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
                "min": pmin,
                "max": pmax,
            })
            acc_nrm = len(accessors)
            accessors.append({"bufferView": bv_nrm, "componentType": 5126, "count": len(nrm_arr), "type": "VEC3"})
            acc_uv = len(accessors)
            accessors.append({"bufferView": bv_uv, "componentType": 5126, "count": len(uv_arr), "type": "VEC2"})
            acc_idx = len(accessors)
            accessors.append({"bufferView": bv_idx, "componentType": idx_comp, "count": len(idx_arr), "type": "SCALAR"})

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
            "asset": {"version": "2.0", "generator": "bruce-happiness-club/penthouse_kit"},
            "scene": 0,
            "scenes": [{"name": self.scene_name, "nodes": list(range(len(nodes)))}],
            "nodes": nodes,
            "meshes": meshes,
            "materials": self.materials,
            "textures": self.textures,
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
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(struct.pack("<III", 0x46546C67, 2, total_len))
            f.write(struct.pack("<II", len(json_bytes), 0x4E4F534A))
            f.write(json_bytes)
            f.write(struct.pack("<II", len(bin_chunks), 0x004E4942))
            f.write(bin_chunks)

        size_mb = os.path.getsize(out_path) / (1024 * 1024)
        return {
            "out_path": out_path,
            "size_mb": round(size_mb, 3),
            "tris": total_tris,
            "meshes": len(meshes),
            "materials": len(self.materials),
            "textures": len(gltf_images),
            "bounds": {"min": g_min, "max": g_max},
            "mesh_names": [m["name"] for m in meshes],
        }
