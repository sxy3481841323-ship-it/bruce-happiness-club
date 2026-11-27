#!/usr/bin/env python3
"""
Strict glTF 2.0 GLB structural, budget, AABB, tangent, and anchor validator
for the four bruce_day_sailer assets.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import struct
import sys
import numpy as np
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(REPO_ROOT, "assets", "models")
MAX_BYTES = 15_000_000

JOB_SPECS = {
    "berth": {
        "file": "yacht_berth.glb",
        "aabb_min": [-5.55, -0.95, -12.00],
        "aabb_max": [-2.80, 1.30, 12.00],
        "anchors": ["dock_spawn", "gangway_dock"],
        "target_mb": 7.0,
    },
    "hull_rig": {
        "file": "yacht_hull_rig.glb",
        "aabb_min": [-2.40, -1.65, -10.00],
        "aabb_max": [2.40, 18.00, 10.00],
        "anchors": ["yacht_root", "gangway_yacht", "aft_cleat", "dog_bow", "salon_mount"],
        "target_mb": 12.0,
    },
    "deck_salon": {
        "file": "yacht_deck_salon.glb",
        "aabb_min": [-1.53, 1.30, -3.20],
        "aabb_max": [1.53, 3.52, 2.20],
        "anchors": ["door_left", "door_right", "bar_top", "journal_anchor", "dog_nap"],
        "target_mb": 13.0,
    },
    "furniture_props": {
        "file": "yacht_furniture_props.glb",
        "zones": [
            ([-1.50, 1.20, -9.00], [2.20, 2.32, -3.20]),
            ([-1.42, 1.32, -2.95], [1.42, 2.80, 1.60]),
        ],
        "anchors": ["dog_mat", "prop_cleat", "prop_bar", "prop_journal"],
        "target_mb": 10.0,
    },
}


def read_accessor(gltf: dict, bin_bytes: bytes, acc_idx: int) -> np.ndarray:
    acc = gltf["accessors"][acc_idx]
    bv = gltf["bufferViews"][acc["bufferView"]]
    offset = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    comp_map = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
    type_map = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
    dtype = comp_map[acc["componentType"]]
    dims = type_map[acc["type"]]
    cnt = acc["count"]
    arr = np.frombuffer(bin_bytes, dtype=dtype, count=cnt * dims, offset=offset)
    return arr.reshape(cnt, dims) if dims > 1 else arr


def validate_single(job_id: str) -> dict:
    spec = JOB_SPECS[job_id]
    path = os.path.join(MODELS_DIR, spec["file"])
    if not os.path.exists(path):
        raise AssertionError(f"Missing GLB: {path}")
    file_bytes = os.path.getsize(path)
    if file_bytes > MAX_BYTES or file_bytes < 1024:
        raise AssertionError(f"{spec['file']} size {file_bytes} violates [1024..{MAX_BYTES}]")

    with open(path, "rb") as f:
        raw = f.read()
    magic, ver, length = struct.unpack("<III", raw[:12])
    if magic != 0x46546C67 or ver != 2 or length != len(raw):
        raise AssertionError(f"{spec['file']} invalid GLB header")

    j_len, j_type = struct.unpack("<II", raw[12:20])
    if j_type != 0x4E4F534A or j_len % 4 != 0:
        raise AssertionError(f"{spec['file']} invalid JSON chunk")
    gltf = json.loads(raw[20:20 + j_len].decode("utf-8"))
    b_off = 20 + j_len
    b_len, b_type = struct.unpack("<II", raw[b_off:b_off + 8])
    if b_type != 0x004E4942 or b_len % 4 != 0 or b_off + 8 + b_len != len(raw):
        raise AssertionError(f"{spec['file']} invalid BIN chunk")
    bin_bytes = raw[b_off + 8:b_off + 8 + b_len]

    if gltf.get("asset", {}).get("version") != "2.0":
        raise AssertionError(f"{spec['file']} glTF version != 2.0")
    for forbidden_ext in ("KHR_draco_mesh_compression", "EXT_meshopt_compression"):
        if forbidden_ext in gltf.get("extensionsUsed", []) or forbidden_ext in gltf.get("extensionsRequired", []):
            raise AssertionError(f"{spec['file']} uses forbidden compression extension {forbidden_ext}")

    # Validate images & deduplication
    img_hashes = set()
    tex_bytes = 0
    for idx, img in enumerate(gltf.get("images", [])):
        bv = gltf["bufferViews"][img["bufferView"]]
        ib = bin_bytes[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]]
        tex_bytes += len(ib)
        h = hashlib.sha256(ib).hexdigest()
        if h in img_hashes:
            raise AssertionError(f"{spec['file']} duplicate embedded image at index {idx}")
        img_hashes.add(h)
        pil = Image.open(io.BytesIO(ib))
        pil.verify()

    # Validate meshes, attributes, bounds, finite numbers
    total_tris = 0
    w_min = np.array([1e9, 1e9, 1e9], dtype=np.float64)
    w_max = np.array([-1e9, -1e9, -1e9], dtype=np.float64)
    eps = 0.005

    for mesh in gltf.get("meshes", []):
        for prim in mesh.get("primitives", []):
            attrs = prim["attributes"]
            pos = read_accessor(gltf, bin_bytes, attrs["POSITION"])
            nrm = read_accessor(gltf, bin_bytes, attrs["NORMAL"])
            uv = read_accessor(gltf, bin_bytes, attrs["TEXCOORD_0"])
            tan = read_accessor(gltf, bin_bytes, attrs["TANGENT"])
            ind = read_accessor(gltf, bin_bytes, prim["indices"])

            for name, arr in (("POSITION", pos), ("NORMAL", nrm), ("UV", uv), ("TANGENT", tan)):
                if not np.all(np.isfinite(arr)):
                    raise AssertionError(f"{spec['file']} non-finite values in {mesh['name']} {name}")

            n_len = np.linalg.norm(nrm, axis=1)
            if np.any(np.abs(n_len - 1.0) > 0.02):
                raise AssertionError(f"{spec['file']} non-unit NORMAL in {mesh['name']}")
            t_len = np.linalg.norm(tan[:, :3], axis=1)
            if np.any(np.abs(t_len - 1.0) > 0.02) or np.any(np.abs(np.abs(tan[:, 3]) - 1.0) > 0.01):
                raise AssertionError(f"{spec['file']} invalid TANGENT in {mesh['name']}")
            if ind.max() >= len(pos):
                raise AssertionError(f"{spec['file']} index out of range in {mesh['name']}")

            total_tris += len(ind) // 3
            p_min, p_max = pos.min(axis=0), pos.max(axis=0)
            w_min = np.minimum(w_min, p_min)
            w_max = np.maximum(w_max, p_max)

            if "zones" in spec:
                z0_min, z0_max = np.array(spec["zones"][0][0]) - eps, np.array(spec["zones"][0][1]) + eps
                z1_min, z1_max = np.array(spec["zones"][1][0]) - eps, np.array(spec["zones"][1][1]) + eps
                in_z0 = np.all((pos >= z0_min) & (pos <= z0_max), axis=1)
                in_z1 = np.all((pos >= z1_min) & (pos <= z1_max), axis=1)
                if not np.all(in_z0 | in_z1):
                    bad = pos[~(in_z0 | in_z1)][0]
                    raise AssertionError(f"{spec['file']} vertex {bad.tolist()} outside deck_aabb | cabin_aabb")

    if "aabb_min" in spec:
        a_min = np.array(spec["aabb_min"]) - eps
        a_max = np.array(spec["aabb_max"]) + eps
        if np.any(w_min < a_min) or np.any(w_max > a_max):
            raise AssertionError(
                f"{spec['file']} world_aabb [{w_min.round(3).tolist()}, {w_max.round(3).tolist()}] "
                f"exceeds allowed [{spec['aabb_min']}, {spec['aabb_max']}]"
            )

    nodes_by_name = {n.get("name"): n for n in gltf.get("nodes", []) if n.get("name")}
    anchors = {}
    for req_a in spec["anchors"]:
        if req_a not in nodes_by_name:
            raise AssertionError(f"{spec['file']} missing required anchor node '{req_a}'")
        tr = nodes_by_name[req_a].get("translation", [0.0, 0.0, 0.0])
        anchors[req_a] = tr

    return {
        "id": job_id,
        "file": spec["file"],
        "file_bytes": file_bytes,
        "file_mb": round(file_bytes / (1024 * 1024), 3),
        "triangles": int(total_tris),
        "texture_bytes": int(tex_bytes),
        "material_count": len(gltf.get("materials", [])),
        "world_aabb": [w_min.round(4).tolist(), w_max.round(4).tolist()],
        "anchors": anchors,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", choices=list(JOB_SPECS.keys()))
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    jobs = list(JOB_SPECS.keys()) if args.all or not args.job else [args.job]
    reports = []
    for j in jobs:
        rep = validate_single(j)
        reports.append(rep)
        print(
            f"[GLB OK] {rep['id']}: {rep['file_bytes']} bytes ({rep['file_mb']} MB), "
            f"{rep['triangles']} tris, {rep['material_count']} mats, "
            f"tex={rep['texture_bytes']}B, aabb={rep['world_aabb']}"
        )

    if len(reports) == len(JOB_SPECS):
        rep_path = os.path.join(MODELS_DIR, "yacht_build_report.json")
        with open(rep_path, "w", encoding="utf-8") as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
        print(f"Report written -> {rep_path}")


if __name__ == "__main__":
    main()
