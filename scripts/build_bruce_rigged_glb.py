#!/usr/bin/env python3
"""Convert Tripo FBX rigged Bruce + PBR textures into canonical glTF 2.0 GLB."""

import io
import json
import os
import struct
import zlib
import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation as R

SRC_DIR = "/Users/alex/Downloads/动态plus"
FBX_PATH = os.path.join(SRC_DIR, "tripo_convert_90200f1d-854b-417d-b495-0119d577407d.fbx")
FBM_DIR = os.path.join(SRC_DIR, "tripo_convert_90200f1d-854b-417d-b495-0119d577407d.fbm")
OUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets",
    "models",
    "bruce_rigged.glb",
)


def read_fbx_prop(buf, pos):
    t = chr(buf[pos])
    pos += 1
    if t == "Y":
        return struct.unpack_from("<h", buf, pos)[0], pos + 2
    if t == "C":
        return bool(buf[pos]), pos + 1
    if t == "I":
        return struct.unpack_from("<i", buf, pos)[0], pos + 4
    if t == "F":
        return struct.unpack_from("<f", buf, pos)[0], pos + 4
    if t == "D":
        return struct.unpack_from("<d", buf, pos)[0], pos + 8
    if t == "L":
        return struct.unpack_from("<q", buf, pos)[0], pos + 8
    if t in ("S", "R"):
        ln = struct.unpack_from("<I", buf, pos)[0]
        pos += 4
        val = buf[pos : pos + ln]
        return (val.decode("utf-8", "replace") if t == "S" else val), pos + ln
    if t in ("f", "d", "l", "i", "b"):
        arr_len, enc, comp_len = struct.unpack_from("<III", buf, pos)
        pos += 12
        raw = buf[pos : pos + comp_len]
        pos += comp_len
        if enc == 1:
            raw = zlib.decompress(raw)
        dt = {"f": "<f4", "d": "<f8", "l": "<i8", "i": "<i4", "b": "<u1"}[t]
        return np.frombuffer(raw, dtype=dt).copy(), pos
    raise ValueError(f"Unknown FBX property type {t!r} at {pos}")


def read_fbx_node(buf, pos, is64):
    if is64:
        end_off, num_props, prop_list_len, name_len = struct.unpack_from("<QQQB", buf, pos)
        pos += 25
    else:
        end_off, num_props, prop_list_len, name_len = struct.unpack_from("<IIIB", buf, pos)
        pos += 13
    if end_off == 0:
        return None, pos
    name = buf[pos : pos + name_len].decode("utf-8", "replace")
    pos += name_len
    props_end = pos + prop_list_len
    props = []
    for _ in range(num_props):
        v, pos = read_fbx_prop(buf, pos)
        props.append(v)
    pos = props_end
    children = []
    null_len = 25 if is64 else 13
    while pos + null_len <= end_off:
        child, pos = read_fbx_node(buf, pos, is64)
        if child is None:
            break
        children.append(child)
    return (name, props, children), end_off


def parse_fbx(path):
    with open(path, "rb") as f:
        data = f.read()
    if not data.startswith(b"Kaydara FBX Binary"):
        raise RuntimeError("Expected binary FBX")
    ver = struct.unpack_from("<I", data, 23)[0]
    is64 = ver >= 7500
    pos = 27
    top = {}
    while pos < len(data) - 30:
        node, pos = read_fbx_node(data, pos, is64)
        if node is None:
            break
        top[node[0]] = node
    return top


def pad4(b: bytes) -> bytes:
    rem = len(b) & 3
    return b + (b"\x00" * (4 - rem) if rem else b"")


def main():
    top = parse_fbx(FBX_PATH)
    objs = top["Objects"][2]
    conns = top["Connections"][2]
    id_map = {c[1][0]: c for c in objs}

    # Locate geometry
    geom = [c for c in objs if c[0] == "Geometry"][0]
    raw_verts = None
    pvi = None
    uvs = None
    uv_idx = None
    uv_map_type = "ByPolygonVertex"
    uv_ref_type = "IndexToDirect"
    norms = None
    norm_idx = None
    norm_map_type = "ByPolygonVertex"
    norm_ref_type = "IndexToDirect"

    for gc in geom[2]:
        if gc[0] == "Vertices":
            raw_verts = gc[1][0].reshape(-1, 3).astype(np.float64)
        elif gc[0] == "PolygonVertexIndex":
            pvi = gc[1][0].astype(np.int64)
        elif gc[0] == "LayerElementUV":
            for s in gc[2]:
                if s[0] == "MappingInformationType":
                    uv_map_type = s[1][0]
                elif s[0] == "ReferenceInformationType":
                    uv_ref_type = s[1][0]
                elif s[0] == "UV":
                    uvs = s[1][0].reshape(-1, 2).astype(np.float64)
                elif s[0] == "UVIndex":
                    uv_idx = s[1][0].astype(np.int64)
        elif gc[0] == "LayerElementNormal":
            for s in gc[2]:
                if s[0] == "MappingInformationType":
                    norm_map_type = s[1][0]
                elif s[0] == "ReferenceInformationType":
                    norm_ref_type = s[1][0]
                elif s[0] == "Normals":
                    norms = s[1][0].reshape(-1, 3).astype(np.float64)
                elif s[0] == "NormalsIndex":
                    norm_idx = s[1][0].astype(np.int64)

    # Model hierarchy and Cluster links
    children_of = {}
    parent_of = {}
    model_names = {}
    model_types = {}
    for cid, c in id_map.items():
        if c[0] == "Model":
            model_names[cid] = c[1][1].split("\x00")[0]
            model_types[cid] = c[1][2]

    cluster_for_bone = {}
    for _, cp, _ in conns:
        cid, pid = cp[1], cp[2]
        if cid in id_map and pid in id_map:
            if id_map[cid][0] == "Model" and id_map[pid][0] == "Model":
                parent_of[cid] = pid
                children_of.setdefault(pid, []).append(cid)
            elif id_map[cid][0] == "Model" and id_map[pid][0] == "Deformer":
                dchildren = {cc[0]: cc[1][0] for cc in id_map[pid][2] if cc[1]}
                if "TransformLink" in dchildren:
                    cluster_for_bone[cid] = {
                        "indexes": dchildren.get("Indexes", np.array([], dtype=np.int32)),
                        "weights": dchildren.get("Weights", np.array([], dtype=np.float64)),
                        "transform_link": dchildren["TransformLink"].reshape(4, 4).T.astype(np.float64),
                    }

    # Topological joint traversal starting from tripo::Root
    root_bone_id = next(cid for cid, nm in model_names.items() if nm == "tripo::Root")
    joint_ids = []

    def dfs_joints(mid):
        joint_ids.append(mid)
        for ch in children_of.get(mid, []):
            if model_types.get(ch) == "LimbNode":
                dfs_joints(ch)

    dfs_joints(root_bone_id)
    assert len(joint_ids) == 86, f"Expected 86 joints, got {len(joint_ids)}"
    joint_idx_by_id = {mid: i for i, mid in enumerate(joint_ids)}
    joint_idx_by_name = {model_names[mid]: i for i, mid in enumerate(joint_ids)}

    # M_mesh transform from verified Lcl Rotation = [-90, 0, 0]: v_world = [x, z, -y]
    # Also compute via M_mesh explicitly to be exact
    mesh_id = next(cid for cid, tp in model_types.items() if tp == "Mesh")
    v_w = np.stack([raw_verts[:, 0], raw_verts[:, 2], -raw_verts[:, 1]], axis=1)
    n_w = np.stack([norms[:, 0], norms[:, 2], -norms[:, 1]], axis=1)

    def bone_world_pos(name):
        mid = joint_ids[joint_idx_by_name[name]]
        return cluster_for_bone[mid]["transform_link"][:3, 3]

    pelvis_mid = 0.5 * (bone_world_pos("tripo::0_Left_Limb_0") + bone_world_pos("tripo::1_Right_Limb_0"))
    chest_pos = bone_world_pos("tripo::0_Right_Limb_3")
    fwd_vec = chest_pos - pelvis_mid
    fwd_xz = np.array([fwd_vec[0], 0.0, fwd_vec[2]], dtype=np.float64)
    fwd_xz /= np.linalg.norm(fwd_xz)
    # u_left = [0, 1, 0] x f = [f_z, 0, -f_x] -> +X, +Y -> +Y, f -> +Z
    u_left = np.array([fwd_xz[2], 0.0, -fwd_xz[0]], dtype=np.float64)
    # R_yaw maps row/col vectors: col vectors transformed as R_yaw @ v
    # R_yaw @ u_left = [1,0,0], R_yaw @ [0,1,0] = [0,1,0], R_yaw @ fwd_xz = [0,0,1]
    R_yaw = np.stack([u_left, np.array([0.0, 1.0, 0.0]), fwd_xz], axis=0)
    assert abs(np.linalg.det(R_yaw) - 1.0) < 1e-6

    v_rot = (R_yaw @ v_w.T).T
    n_rot = (R_yaw @ n_w.T).T
    n_norms = np.linalg.norm(n_rot, axis=1, keepdims=True)
    n_rot = np.divide(n_rot, np.maximum(n_norms, 1e-8))

    bmin = v_rot.min(axis=0)
    bmax = v_rot.max(axis=0)
    scale_s = 1.0 / max(1e-6, float(bmax[1] - bmin[1]))
    center_x = 0.5 * float(bmin[0] + bmax[0])
    center_z = 0.5 * float(bmin[2] + bmax[2])
    ground_y = float(bmin[1])
    offset_rot = np.array([center_x, ground_y, center_z], dtype=np.float64)

    v_bind = (v_rot - offset_rot) * scale_s

    # Sanity check: nose faces +Z (> 0.4) and front-left shoulder (+X) > front-right shoulder (-X)
    nose_z = float(v_bind[:, 2].max())
    fl_x = float(((R_yaw @ bone_world_pos("bone_16")) - offset_rot)[0] * scale_s)
    fr_x = float(((R_yaw @ bone_world_pos("bone_55")) - offset_rot)[0] * scale_s)
    assert nose_z > 0.4, f"Expected nose_z > 0.4, got {nose_z}"
    assert fl_x > fr_x, f"Expected +X front-left ({fl_x}) > -X front-right ({fr_x})"

    # Accumulate skin weights per raw FBX vertex
    num_raw_verts = len(raw_verts)
    vert_influences = [[] for _ in range(num_raw_verts)]
    for j_idx, mid in enumerate(joint_ids):
        cl = cluster_for_bone.get(mid)
        if not cl:
            continue
        idxs = cl["indexes"]
        wts = cl["weights"]
        for vi, wt in zip(idxs, wts):
            if wt > 1e-6:
                vert_influences[int(vi)].append((j_idx, float(wt)))

    raw_joints = np.zeros((num_raw_verts, 4), dtype=np.uint8)
    raw_weights = np.zeros((num_raw_verts, 4), dtype=np.float32)
    zero_wt_verts = 0
    for vi in range(num_raw_verts):
        infs = vert_influences[vi]
        if not infs:
            zero_wt_verts += 1
            raw_joints[vi, 0] = 0
            raw_weights[vi, 0] = 1.0
            continue
        infs.sort(key=lambda x: -x[1])
        top4 = infs[:4]
        wsum = sum(w for _, w in top4)
        if wsum <= 1e-8:
            raw_joints[vi, 0] = top4[0][0]
            raw_weights[vi, 0] = 1.0
        else:
            for k, (ji, w) in enumerate(top4):
                raw_joints[vi, k] = ji
                raw_weights[vi, k] = w / wsum

    # Triangulate polygons and deduplicate corners (raw_vi, uv_i, norm_i)
    corner_map = {}
    out_pos = []
    out_norm = []
    out_uv = []
    out_joints = []
    out_weights = []
    out_indices = []

    poly_corners = []
    for c_idx, signed_vi in enumerate(pvi):
        is_end = signed_vi < 0
        vi = int(~signed_vi if is_end else signed_vi)

        if uv_map_type == "ByPolygonVertex":
            u_i = int(uv_idx[c_idx]) if uv_ref_type == "IndexToDirect" else c_idx
        else:
            u_i = vi

        if norm_map_type == "ByPolygonVertex":
            n_i = int(norm_idx[c_idx]) if norm_ref_type == "IndexToDirect" else c_idx
        else:
            n_i = vi

        key = (vi, u_i, n_i)
        out_vi = corner_map.get(key)
        if out_vi is None:
            out_vi = len(out_pos)
            corner_map[key] = out_vi
            out_pos.append(v_bind[vi])
            out_norm.append(n_rot[n_i])
            uv = uvs[u_i]
            out_uv.append((uv[0], 1.0 - uv[1]))  # Verified V-flip
            out_joints.append(raw_joints[vi])
            out_weights.append(raw_weights[vi])
        poly_corners.append(out_vi)

        if is_end:
            for k in range(1, len(poly_corners) - 1):
                out_indices.extend((poly_corners[0], poly_corners[k], poly_corners[k + 1]))
            poly_corners.clear()

    pos_arr = np.asarray(out_pos, dtype=np.float32)
    norm_arr = np.asarray(out_norm, dtype=np.float32)
    uv_arr = np.asarray(out_uv, dtype=np.float32)
    joints_arr = np.asarray(out_joints, dtype=np.uint8)
    weights_arr = np.asarray(out_weights, dtype=np.float32)
    use_u32 = len(pos_arr) > 65535
    idx_arr = np.asarray(out_indices, dtype=np.uint32 if use_u32 else np.uint16)

    # Joint transforms in canonical character space (unit scale) + inverseBindMatrices
    W_gltf = []
    R_gltf = []
    p_gltf = []
    ibm_list = []

    for j_idx, mid in enumerate(joint_ids):
        tlink = cluster_for_bone[mid]["transform_link"]
        p_j = ((R_yaw @ tlink[:3, 3]) - offset_rot) * scale_s
        rot_raw = R_yaw @ tlink[:3, :3]
        col_norms = np.linalg.norm(rot_raw, axis=0, keepdims=True)
        rot_ortho = R.from_matrix(rot_raw / np.maximum(col_norms, 1e-8)).as_matrix()

        w_mat = np.eye(4, dtype=np.float64)
        w_mat[:3, :3] = rot_ortho
        w_mat[:3, 3] = p_j
        W_gltf.append(w_mat)
        R_gltf.append(rot_ortho)
        p_gltf.append(p_j)
        ibm_list.append(np.linalg.inv(w_mat))

    # Build glTF nodes: node 0 = BruceMesh, node 1 = Armature, nodes 2..87 = joints 0..85
    nodes = [
        {"name": "BruceRiggedMesh", "mesh": 0, "skin": 0},
        {"name": "Armature", "children": [2]},
    ]
    for j_idx, mid in enumerate(joint_ids):
        node_idx = 2 + j_idx
        p_id = parent_of.get(mid)
        if j_idx == 0:
            t_loc = p_gltf[0]
            q_loc = R.from_matrix(R_gltf[0]).as_quat()
        else:
            pj = joint_idx_by_id[p_id]
            t_loc = R_gltf[pj].T @ (p_gltf[j_idx] - p_gltf[pj])
            q_loc = R.from_matrix(R_gltf[pj].T @ R_gltf[j_idx]).as_quat()

        ch_nodes = [
            2 + joint_idx_by_id[c_id]
            for c_id in children_of.get(mid, [])
            if c_id in joint_idx_by_id
        ]
        nd = {
            "name": model_names[mid],
            "translation": [float(x) for x in t_loc],
            "rotation": [float(x) for x in q_loc],
        }
        if ch_nodes:
            nd["children"] = ch_nodes
        nodes.append(nd)

    # Self-test rebuilt world matrices * IBM == I_4
    rebuilt_w = [None] * len(joint_ids)

    def eval_joint_world(j_idx):
        if rebuilt_w[j_idx] is not None:
            return rebuilt_w[j_idx]
        nd = nodes[2 + j_idx]
        loc = np.eye(4, dtype=np.float64)
        loc[:3, :3] = R.from_quat(nd["rotation"]).as_matrix()
        loc[:3, 3] = nd["translation"]
        mid = joint_ids[j_idx]
        if j_idx == 0:
            rebuilt_w[j_idx] = loc
        else:
            pj = joint_idx_by_id[parent_of[mid]]
            rebuilt_w[j_idx] = eval_joint_world(pj) @ loc
        return rebuilt_w[j_idx]

    max_err = 0.0
    for j_idx in range(len(joint_ids)):
        prod = eval_joint_world(j_idx) @ ibm_list[j_idx]
        err = float(np.max(np.abs(prod - np.eye(4))))
        if err > max_err:
            max_err = err
    assert max_err < 1e-5, f"IBM self-test failed: max_err={max_err}"

    # Serialize IBMs in column-major float32
    ibm_bytes = b"".join(m.T.astype("<f4").tobytes() for m in ibm_list)

    # Prepare PBR textures -> compacted JPEG buffers
    def encode_img_jpeg(pil_img, quality=88):
        buf = io.BytesIO()
        pil_img.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue()

    rgb_img = Image.open(os.path.join(FBM_DIR, "tripo_rgb_0721c775-ff6a-4804-aa13-cb95c864dc1f.jpg")).convert("RGB")
    rgb_img = rgb_img.resize((1024, 1024), Image.Resampling.LANCZOS)
    rgb_bytes = encode_img_jpeg(rgb_img, quality=88)

    norm_img = Image.open(os.path.join(FBM_DIR, "tripo_normal_6e415253-54ec-46c4-9caa-0ee9fbc1a1ae.jpg")).convert("RGB")
    norm_img = norm_img.resize((1024, 1024), Image.Resampling.LANCZOS)
    norm_bytes = encode_img_jpeg(norm_img, quality=86)

    rough_img = Image.open(os.path.join(FBM_DIR, "可爱狗狗3d模型_roughness.jpg")).convert("L").resize((512, 512), Image.Resampling.LANCZOS)
    metal_img = Image.open(os.path.join(FBM_DIR, "可爱狗狗3d模型_metallic.jpg")).convert("L").resize((512, 512), Image.Resampling.LANCZOS)
    r_arr = np.full((512, 512), 255, dtype=np.uint8)
    g_arr = np.asarray(rough_img, dtype=np.uint8)
    b_arr = np.asarray(metal_img, dtype=np.uint8)
    mr_img = Image.fromarray(np.stack([r_arr, g_arr, b_arr], axis=-1), mode="RGB")
    mr_bytes = encode_img_jpeg(mr_img, quality=85)

    # Assemble binary buffer and bufferViews
    chunks = []
    buffer_views = []

    def push_bv(raw_bytes, target=None, stride=None):
        offset = sum(len(c) for c in chunks)
        chunks.append(pad4(raw_bytes))
        bv = {"buffer": 0, "byteOffset": offset, "byteLength": len(raw_bytes)}
        if target is not None:
            bv["target"] = target
        if stride is not None:
            bv["byteStride"] = stride
        bv_idx = len(buffer_views)
        buffer_views.append(bv)
        return bv_idx

    bv_pos = push_bv(pos_arr.tobytes(), target=34962)
    bv_norm = push_bv(norm_arr.tobytes(), target=34962)
    bv_uv = push_bv(uv_arr.tobytes(), target=34962)
    bv_joints = push_bv(joints_arr.tobytes(), target=34962)
    bv_weights = push_bv(weights_arr.tobytes(), target=34962)
    bv_idx = push_bv(idx_arr.tobytes(), target=34963)
    bv_ibm = push_bv(ibm_bytes)
    bv_img_rgb = push_bv(rgb_bytes)
    bv_img_norm = push_bv(norm_bytes)
    bv_img_mr = push_bv(mr_bytes)

    bin_blob = b"".join(chunks)

    pos_min = [float(x) for x in pos_arr.min(axis=0)]
    pos_max = [float(x) for x in pos_arr.max(axis=0)]

    gltf = {
        "asset": {"version": "2.0", "generator": "bruce-rigged-fbx2glb/1.0"},
        "scene": 0,
        "scenes": [{"name": "Scene", "nodes": [0, 1]}],
        "nodes": nodes,
        "skins": [
            {
                "name": "BruceArmature",
                "skeleton": 2,
                "joints": list(range(2, 2 + len(joint_ids))),
                "inverseBindMatrices": 6,
            }
        ],
        "meshes": [
            {
                "name": "BruceMesh",
                "primitives": [
                    {
                        "attributes": {
                            "POSITION": 0,
                            "NORMAL": 1,
                            "TEXCOORD_0": 2,
                            "JOINTS_0": 3,
                            "WEIGHTS_0": 4,
                        },
                        "indices": 5,
                        "material": 0,
                    }
                ],
            }
        ],
        "materials": [
            {
                "name": "BruceFurPBR",
                "pbrMetallicRoughness": {
                    "baseColorTexture": {"index": 0},
                    "metallicRoughnessTexture": {"index": 2},
                    "metallicFactor": 1.0,
                    "roughnessFactor": 1.0,
                },
                "normalTexture": {"index": 1, "scale": 0.55},
            }
        ],
        "textures": [
            {"sampler": 0, "source": 0},
            {"sampler": 0, "source": 1},
            {"sampler": 0, "source": 2},
        ],
        "samplers": [
            {"magFilter": 9729, "minFilter": 9987, "wrapS": 10497, "wrapT": 10497}
        ],
        "images": [
            {"bufferView": bv_img_rgb, "mimeType": "image/jpeg", "name": "bruce_basecolor"},
            {"bufferView": bv_img_norm, "mimeType": "image/jpeg", "name": "bruce_normal"},
            {"bufferView": bv_img_mr, "mimeType": "image/jpeg", "name": "bruce_mr"},
        ],
        "accessors": [
            {
                "bufferView": bv_pos,
                "componentType": 5126,
                "count": len(pos_arr),
                "type": "VEC3",
                "min": pos_min,
                "max": pos_max,
            },
            {"bufferView": bv_norm, "componentType": 5126, "count": len(norm_arr), "type": "VEC3"},
            {"bufferView": bv_uv, "componentType": 5126, "count": len(uv_arr), "type": "VEC2"},
            {"bufferView": bv_joints, "componentType": 5121, "count": len(joints_arr), "type": "VEC4"},
            {"bufferView": bv_weights, "componentType": 5126, "count": len(weights_arr), "type": "VEC4"},
            {
                "bufferView": bv_idx,
                "componentType": 5125 if use_u32 else 5123,
                "count": len(idx_arr),
                "type": "SCALAR",
            },
            {"bufferView": bv_ibm, "componentType": 5126, "count": len(joint_ids), "type": "MAT4"},
        ],
        "bufferViews": buffer_views,
        "buffers": [{"byteLength": len(bin_blob)}],
    }

    json_bytes = json.dumps(gltf, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    rem = len(json_bytes) & 3
    if rem:
        json_bytes += b" " * (4 - rem)

    total_len = 12 + 8 + len(json_bytes) + 8 + len(bin_blob)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "wb") as out_f:
        out_f.write(struct.pack("<III", 0x46546C67, 2, total_len))
        out_f.write(struct.pack("<I4s", len(json_bytes), b"JSON"))
        out_f.write(json_bytes)
        out_f.write(struct.pack("<I4s", len(bin_blob), b"BIN\x00"))
        out_f.write(bin_blob)

    out_mb = os.path.getsize(OUT_PATH) / (1024 * 1024)
    print(f"Wrote {OUT_PATH} ({out_mb:.2f} MB)")
    print(
        f"Stats: verts={len(pos_arr)}, tris={len(idx_arr)//3}, joints={len(joint_ids)}, "
        f"zero_wt_verts={zero_wt_verts}, ibm_max_err={max_err:.2e}, "
        f"bbox_min={[round(x,4) for x in pos_min]}, bbox_max={[round(x,4) for x in pos_max]}"
    )
    assert out_mb <= 4.5, f"GLB too large: {out_mb:.2f} MB"


if __name__ == "__main__":
    main()
