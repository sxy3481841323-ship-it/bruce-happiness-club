#!/usr/bin/env python3
"""
Parallel DeepSeek codegen dispatcher for Batch 7 (Wave 2A textures + Wave 2B 4 GLBs + Quiet-Luxury yacht copy).
Runs via scripts/ds_worker.py with deterministic local verification.
"""

from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
from ds_worker import run_parallel_codegen, save_telemetry  # noqa: E402


TEX_HELPERS_SIG = """EXACT `yacht_kit.tex_helpers` signatures (DO NOT GUESS OTHER SIGNATURES!):
- `periodic_noise(gx: int, gy: int, size_u: int, size_v: int | None = None, seed_offset: int = 0) -> np.ndarray` (returns float64 in [-1, 1])
- `periodic_voronoi(cells: int, size: int, seed_offset: int = 0) -> tuple[np.ndarray, np.ndarray]` (fast vectorized periodic jittered Voronoi returning `(f1, f2 - f1)` in cell units)
- `hex_to_srgb_vec(hex_str: str) -> np.ndarray` (returns shape (3,) float64 in [0..255])
- `height_to_normal_y_up(height_m: np.ndarray, phys_w_m: float, phys_h_m: float) -> np.ndarray` (returns uint8 (H, W, 3))
- `pack_orm(ao, rough, metal, shape: tuple[int, int]) -> np.ndarray` (returns uint8 (H, W, 3))
- `downsample_box(arr: np.ndarray, target_h: int, target_w: int) -> np.ndarray`
- `verify_seamless_2x2(arr: np.ndarray, name: str, max_jump: float = 35.0)`
- `verify_convex_ridge_normal()`
- `save_bundle(name: str, base_rgb: np.ndarray, orm_rgb: np.ndarray, norm_rgb: np.ndarray, base_fmt: str = "JPEG", quality: int = 90)`"""

WAVE_2A_TASKS = [
    {
        "name": "tex_woods_stone",
        "out_path": "scripts/yacht_kit/tex_woods_stone.py",
        "model": "deepseek-chat",
        "verify_cmd": "python3 scripts/yacht_kit/tex_woods_stone.py",
        "verify_timeout": 180,
        "system": (
            "You are a Technical Artist writing concise, deterministic NumPy+PIL procedural PBR texture generators. "
            "Return ONLY valid Python code with no markdown explanation. Keep code under 220 lines."
        ),
        "prompt": TEX_HELPERS_SIG + "\n\n" + """Write `scripts/yacht_kit/tex_woods_stone.py` using ONLY the exact helpers above from `yacht_kit.tex_helpers` (add `scripts/` to `sys.path`).
Call `verify_convex_ridge_normal()` first. Then generate, verify `verify_seamless_2x2`, and call `save_bundle(...)` for these 5 PBR maps (baseColor sRGB + linear ORM + +Y normal):

1. `hull_satin` (1024x1024, base_fmt="PNG"):
   - Base `#14273B` modulated by `periodic_noise(8, 8, 1024, seed_offset=1) * 2.0` per channel.
   - Roughness `0.31 + periodic_noise(32, 32, 1024, seed_offset=2) * 0.022 + periodic_noise(192, 192, 1024, seed_offset=3) * 0.010`, AO=1.0, metal=0.0.
   - Orange-peel normal only: `periodic_noise(160, 160, 1024, seed_offset=4) * 0.000006` meters (`0.012 mm` peak-to-valley, ~6 px period) over physical 1.0x1.0 m.

2. `teak_deck` (2048x2048 base_fmt="JPEG" quality=90; downsample ORM & normal to 1024x1024 via `downsample_box(..., 1024, 1024)`):
   - Physical tile `0.640 m` wide (U) x `2.56 m` tall (V).
   - At 2048x2048: 8 planks across U, each 256 px wide. Center the 12 px (`3.75 mm`) `#302923` caulk seam cleanly on plank boundaries using `((x + 6) % 256) < 12` so left/right wrap edges (`x=0` and `x=2047`) are BOTH caulk (`col_diff=0`), and similarly center the staggered 12 px butt-joint caulk on `[0, 512, 1024, 1536]` via `((y + 6 - offset_v) % 2048) < 12`! Remaining 244 px (`76.25 mm`) per plank is wood.
   - Each plank gets deterministic luminance offset in `[-6, +6]` (by plank id); grain combines `periodic_noise(128, 8, 2048, seed_offset=10)` long grain + `periodic_noise(256, 32, 2048, seed_offset=11) * 0.45` fine elongated pores + wood base `#AE885F`.
   - Height: wood `0.0 m`, caulk groove recessed `-0.00035 m` (`0.35 mm`) with `2 px` beveled shoulder; ORM: plank rough `0.63 ± 0.03`, caulk rough `0.80`, AO=`0.65` in caulk else `1.0`, metal=`0.0`. Verify seamless!

3. `teak_frame` (1024x1024, base_fmt="JPEG" quality=90):
   - Clean radial-cut lighter teak `#C5A071` without dark deck caulk seams (for lounge chair wooden frames & round table), using `periodic_noise(96, 8, 1024, seed_offset=20)` grain, roughness `0.48`, subtle relief `0.00004 m`.

4. `marquetry` (2048x2048 base_fmt="JPEG" quality=90; downsample ORM & normal to 1024x1024):
   - Mirror-matched dark/medium veneer marquetry (`#6B442E` primary, `#A77448` secondary accents).
   - UV radial/wedge layout around `(0.5, 0.5)`: 8 angular wedges rotated at `[18, -18, 33, -33, 48, -48, 63, -63]` degrees; adjacent wedges alternate ±(8..14) RGB luminance & blend `#6B442E` vs `#A77448`.
   - Grain axis follows wedge angle via `periodic_noise(160, 12, 2048)` + `periodic_noise(72, 8, 2048)` sampled cleanly; wrap-safe thin 2 px dark inlay line along wedge borders; surface height variation `0.000025 m` (`0.025 mm`); roughness `0.39 ± 0.02`.

5. `filled_travertine` (2048x2048 base_fmt="JPEG" quality=90; downsample ORM & normal to 1024x1024):
   - Base `#C3B198` with `periodic_noise(5, 12, 2048, seed_offset=40)` parallel thin strata + fine filled pores (2-8 px stretched horizontally via thresholded `periodic_noise(180, 380, 2048)`), pore depth `<= 0.00012 m`, roughness `0.47 ± 0.04` (slightly matte `#AEA08A` in filled pores).

Verify every map via `verify_seamless_2x2` (for marquetry set max_jump=55 due to centered radial panel border, others max_jump=30) and print `OK tex_woods_stone` with saved file sizes at end.""",
    },
    {
        "name": "tex_fabrics_metals",
        "out_path": "scripts/yacht_kit/tex_fabrics_metals.py",
        "model": "deepseek-chat",
        "verify_cmd": "python3 scripts/yacht_kit/tex_fabrics_metals.py",
        "verify_timeout": 180,
        "system": (
            "You are a Technical Artist writing concise, deterministic NumPy+PIL procedural PBR texture generators. "
            "Return ONLY valid Python code with no markdown explanation. Keep code under 230 lines."
        ),
        "prompt": TEX_HELPERS_SIG + "\n\n" + """Write `scripts/yacht_kit/tex_fabrics_metals.py` importing ONLY the exact functions above from `yacht_kit.tex_helpers` (add `scripts/` to `sys.path`). Keep total lines < 230 and avoid huge nested loops (use pure vectorized NumPy!).
Generate, call `verify_seamless_2x2`, and `save_bundle(...)` for these 7 PBR maps (all 1024x1024 except `stitch_strip` 1024x128):

1. `saddle_leather` (1024x1024, base_fmt="JPEG" quality=92):
   - Base `#925638`. Call `f1, edge = periodic_voronoi(64, 1024, seed_offset=50)` directly (DO NOT write custom nested Voronoi loops!) -> `f1` gives organic leather pebble domes & `edge < 0.14` gives pores/creases (`0.06 mm` depth). Also add sparse `3-8 px` pinholes (`periodic_noise(192, 192, 1024) > 0.78`).
   - Roughness `0.53 ± 0.045` (creases slightly rougher), AO slightly darker in pores, metal=0.0.

2. `saddle_leather_crest` (1024x1024, base_fmt="PNG", clamp-ready book cover texture):
   - Start from `saddle_leather` base, then blind-deboss an ORIGINAL WORDLESS DOUBLE-LINE DIAMOND CREST centered at `(512, 420)` (outer & inner concentric diamond borders rotated 45 deg, radii ~160 px and ~122 px, corner dot ornaments, subtle recessed bevel & darker `#744129` debossed tone, NO LETTERS/MONOGRAMS!). Height recessed `-0.00018 m` at crest groove.

3. `stitch_strip` (1024 wide x 128 tall, base_fmt="PNG"):
   - Horizontal UV trim strip over `#925638` leather base: along center row band (y=48..80), place cream-tan (`#DDD0BC`) stitches repeating every 16 px in U (10 px thread length, 2 px height + beveled thread height `0.00018 m`, `4 mm` physical stitch pitch, dark needle-hole AO at stitch ends). Roughness: leather `0.53`, thread `0.78`.

4. `woven_rug` (1024x1024, base_fmt="JPEG" quality=90):
   - Base `#B5A692`. 64x64 cells (16 px per cell): 2/2 herringbone/twill weave with alternating pile direction per 16x16 stripe, height relief `0.00012 m` across 0.40x0.40 m physical tile, roughness `0.91`, metal `0.0`.

5. `outdoor_linen` (1024x1024, base_fmt="JPEG" quality=90):
   - Base `#D5C8AF`. 64x64 plain weave cells (16 px each), `(warp + weft) % 2` alternating over/under yarn profiles! Yarn width `0.78..0.92` cell with periodic slub variations `+0.12` width; physical pitch `1.25 mm/cell` (`0.080 m` tile), relief `0.00008 m`, roughness `0.86 ± 0.04`.

6. `sail_coated` (1024x1024, base_fmt="JPEG" quality=92):
   - Base `#ECE5D6`. 128x128 low-contrast coated rigid-sail panel weave (8 px cell), height relief `0.000008 m`, roughness `0.52 ± 0.018`, very subtle panel scrim line.

7. `pvd_brushed` (1024x1024, base_fmt="PNG") AND `bronze_brushed` (1024x1024, base_fmt="PNG"):
   - Champagne PVD `#B49A72` (`roughness=0.27`, `metalness=1.0`) and Antique Bronze `#80664A` (`roughness=0.35`, `metalness=1.0`).
   - Directional +V brushing from `periodic_noise(256, 8, 1024, seed_offset=80) + 0.5*periodic_noise(128, 16, 1024, seed_offset=81)` -> `±0.045` roughness & `±3` RGB; add deterministic `<1%` area sparse micro-scratches (`1-2 px` wide, `18-84 px` long along V), normal streak `0.000006 m`.

Verify every map via `verify_seamless_2x2` (set max_jump=55 for `saddle_leather_crest`) and print `OK tex_fabrics_metals`.""",
    },
]


BUILDER_API_SIG = """EXACT `scripts/yacht_kit` API (DO NOT GUESS OTHER SIGNATURES!):
- `from yacht_kit.yacht_prim_lib import YachtGLBBuilder`
- `from yacht_kit.tex_helpers import load_bundle`
- `b = load_bundle(name)` returns dict with `b["base_bytes"]`, `b["base_mime"]`, `b["orm_bytes"]`, `b["norm_bytes"]`.
  Valid bundle names: `hull_satin`, `teak_deck`, `teak_frame`, `marquetry`, `filled_travertine`, `saddle_leather`, `saddle_leather_crest`, `stitch_strip`, `woven_rug`, `outdoor_linen`, `sail_coated`, `pvd_brushed`, `bronze_brushed`.
- `gb = YachtGLBBuilder(asset_id: str)`
- `mat = gb.add_pbr_material(name, base_bytes=None, base_mime="image/jpeg", orm_bytes=None, normal_bytes=None, normal_scale=1.0, base_factor=(1,1,1,1), roughness=1.0, metalness=0.0, clearcoat=0.0, clearcoat_roughness=0.0, transmission=0.0, ior=None, emissive=(0,0,0), double_sided=False, alpha_mode="OPAQUE", clamp_uv=False) -> int`
- `m = gb.mesh(mat_idx: int, name: str | None = None)` returns `YachtMesh` with:
  - `m.add_tri(p0, p1, p2, uv0=(0,0), uv1=(1,0), uv2=(1,1), n0=None, n1=None, n2=None)`
  - `m.add_quad(p0, p1, p2, p3, uv0=(0,0), uv1=(1,0), uv2=(1,1), uv3=(0,1), flip=False)`
  - `m.add_box(center, size, uv_tile=(1.0, 1.0), rot_y=0.0)`
  - `m.add_chamfer_box(center, size, bevel=0.004, uv_tile=1.0, rot_y=0.0)`
  - `m.add_tube(p0, p1, r0, r1=None, segs=20, cap=True, uv_scale=(1.0, 1.0))`
  - `m.add_grid(pos_grid, uv_grid, flip=False, smooth_normals=True, seam_u=False)` (pos_grid shape (Nu, Nv, 3), uv_grid shape (Nu, Nv, 2))
  - `m.add_prism(poly_xz, y0, y1, uv_tile=1.0, caps=(True, True))`
- `gb.add_anchor(name: str, pos: tuple[float, float, float], rot=(0,0,0,1))`
- `rep = gb.export(out_path: str)`
Keep total code concise (~160-260 lines), return ONLY valid Python code with no markdown explanation! Always add `scripts/` to `sys.path` cleanly."""

WAVE_2B_TASKS = [
    {
        "name": "job_berth",
        "out_path": "scripts/yacht_kit/job_berth.py",
        "model": "deepseek-chat",
        "verify_cmd": "python3 scripts/yacht_kit/job_berth.py && python3 scripts/yacht_kit/validate_glb.py --job berth",
        "verify_timeout": 120,
        "system": "You are a Marine 3D Technical Artist. Return ONLY concise, clean Python code (<220 lines) that builds assets/models/yacht_berth.glb.",
        "prompt": BUILDER_API_SIG + """

Write `scripts/yacht_kit/job_berth.py` to build `assets/models/yacht_berth.glb` (strict AABB `[-5.55, -0.95, -12.00] .. [-2.80, 1.30, 12.00]`, meters, +Y up).
Build:
1. Materials:
   - `teak`: `load_bundle("teak_deck")`, `roughness=1.0, metalness=0.0, clearcoat=0.07` (`teak_deck` physical tile is `0.640 m` x `2.56 m`, so pass `uv_tile=(0.64, 2.56)` when mapping planks along Z!).
   - `pvd`: `load_bundle("pvd_brushed")`, `roughness=1.0, metalness=1.0`.
   - `float_dark`: `base_factor=(0.11, 0.14, 0.17, 1.0), roughness=0.72, metalness=0.1`.
   - `fender_rubber`: `base_factor=(0.12, 0.14, 0.17, 1.0), roughness=0.58`.
2. Geometry (STRICTLY keep all vertices inside `X=[-5.55..-2.80], Y=[-0.95..1.30], Z=[-12.00..12.00]`):
   - Teak walkway deck `X=-5.48..-2.87` (`width=2.61`, `Z=-12.00..12.00`, `Y=0.64..0.72` so top is exactly `Y=0.72`), plus brushed PVD edge fascia strips at `X=-5.50..-5.48` and `-2.87..-2.85` (`Y=0.62..0.73`).
   - Dark underwater pontoon hulls under walkway (`Y=-0.92..0.64`, `X=-5.42..-2.93`) with cross beams.
   - Cylindrical piling posts (`Ø0.24 m`, `r=0.12`) spanning `Y=-0.95..1.26` along `X=-5.38` and `X=-2.98` at `Z = [-11.2, -7.0, -2.2, 2.2, 7.0, 11.2]` (avoiding gangway slot at `Z=-5.20`) with chamfered PVD caps.
   - Four twin-post PVD mooring cleats along inner dock edge (`X=-2.98, Y=0.72..0.88`, `Z=-9.5, -3.6, 3.2, 9.2`).
   - Six dark dock fenders (`r=0.11, height=0.52`) hanging along `X=-2.92` protruding no further than `X=-2.805` (`Y=0.12..0.64`) at `Z=[-8.4, -5.9, -3.4, 0.5, 4.4, 8.2]`.
3. Anchors:
   - `dock_spawn`: `(-4.20, 0.72, -10.60)`
   - `gangway_dock`: `(-2.85, 0.72, -5.20)`
4. Export to `assets/models/yacht_berth.glb` and print summary.""",
    },
    {
        "name": "job_hull_rig",
        "out_path": "scripts/yacht_kit/job_hull_rig.py",
        "model": "deepseek-chat",
        "verify_cmd": "python3 scripts/yacht_kit/job_hull_rig.py && python3 scripts/yacht_kit/validate_glb.py --job hull_rig",
        "verify_timeout": 150,
        "system": "You are a Marine 3D Technical Artist. Return ONLY concise, clean Python code (<270 lines) that builds assets/models/yacht_hull_rig.glb.",
        "prompt": BUILDER_API_SIG + """

Write `scripts/yacht_kit/job_hull_rig.py` to build `assets/models/yacht_hull_rig.glb` (strict AABB `[-2.40, -1.65, -10.00] .. [2.40, 18.00, 10.00]`, meters).
Build:
1. Materials:
   - `hull_mat`: `load_bundle("hull_satin")`, `clearcoat=0.38, clearcoat_roughness=0.27`.
   - `teak`: `load_bundle("teak_deck")`, `clearcoat=0.07`.
   - `pvd`: `load_bundle("pvd_brushed")`, `metalness=1.0, roughness=1.0`.
   - `sail_mat`: `load_bundle("sail_coated")`, `clearcoat=0.10, double_sided=True`.
   - `win_glass`: `base_factor=(0.04, 0.06, 0.09, 1.0), roughness=0.08, metalness=0.15, clearcoat=0.65`.
2. Hull & Deck Loft (`Z = -10.00 .. 10.00`):
   - Interpolate deck half-width `hw(z)` smoothly via piecewise Hermite/cosine spline through exact control points: `[(-10,1.12), (-8,1.82), (-3,2.40), (2,2.40), (5.8,1.96), (8.5,0.98), (10,0.03)]`, strictly clamped to `[0.02, 2.40]`.
   - Deck sheer `y_deck(z)`: `1.20` on stern `[-10,-8]`, smooth `1.30` through `[-8, 2.2]`, rising cleanly from `1.30` at `Z=2.2` to `1.62` at `Z=10.0` (so at `Z=7.70`, `y_deck ≈ 1.56`).
   - Waterline bow crossing: at `Y=0`, bow stem is `Z=9.50` -> outer shell cross-section narrows below waterline to `Y=-0.55` (and slim fin keel/rudder drops from `-0.55` to `-1.62` around `Z=-2.5..2.0` & `-8.5`). Build continuous lofted port & starboard hull shell grids (`hull_mat`), keeping `|X| <= 2.40`, `Z in [-10..10]`, `Y >= -1.65`.
   - Champagne PVD waterline stripe (`pvd`): thin ribbon hugging hull contour at `Y = 0.15 ± 0.021` (`height=0.042 m`, `Z=-9.7..9.52`) sticking cleanly 3 mm proud of hull.
   - Elongated window band (`win_glass` + `pvd` trim): along both flanks `Z = -5.80 .. 5.60`, `Y = 0.78 .. 0.95` (`height=0.17 m`), conforming closely to hull breadth.
   - Stern swim platform (`teak` + `pvd` edge): `X = -1.06..1.06` (`width=2.12`), `Z = -10.00..-9.10` (`depth=0.90`), top `Y=0.34`, plus 4 ascending teak steps from `Z=-9.10` forward with `0.26 m` treads at `Y = 0.55, 0.77, 0.98, 1.20`.
   - Teak main deck (`teak`, `uv_tile=(0.64, 2.56)`), raised foredeck plinth around `(0, 1.56, 7.70)`, chamfered PVD stanchion rails (`H=0.68 m`) along perimeter EXCEPT open port boarding gate at `Z = -5.75 .. -4.65` (`Y=1.29` gangway landing!).
3. Mast & Six Folded SolidSail Panels:
   - Single tapered mast (`pvd`/`hull_mat`) at `X=0, Z=2.55` from `Y=1.33` to `Y=18.00` (check <= `18.00`!), boom extending aft (`Y=4.55`, `Z=2.55..-3.15`).
   - Six rigid SolidSail wing-sail panels (`sail_mat`, chamfered thickness ~0.12 m tapering aft, `12 mm` vertical gap between panels) from `Y=4.75` to `Y=17.65`. Unfolded chord tapers linearly `4.20 m` (bottom) -> `0.65 m` (top). Lower 3 panels split cleanly at `Z ≈ -0.6` and have outer segments folded `42 deg` to port/stbd so max visible chord `<= 2.85 m` and `|X| <= 2.35`! Add PVD hinge knuckles between panel segments.
4. Anchors: `yacht_root=(0,0,0)`, `gangway_yacht=(-2.26, 1.29, -5.20)`, `aft_cleat=(1.52, 1.26, -8.55)`, `dog_bow=(0, 1.58, 7.70)`, `salon_mount=(0, 1.30, 0)`. Export to `assets/models/yacht_hull_rig.glb`.""",
    },
    {
        "name": "job_deck_salon",
        "out_path": "scripts/yacht_kit/job_deck_salon.py",
        "model": "deepseek-chat",
        "verify_cmd": "python3 scripts/yacht_kit/job_deck_salon.py && python3 scripts/yacht_kit/validate_glb.py --job deck_salon",
        "verify_timeout": 120,
        "system": "You are a Marine 3D Technical Artist. Return ONLY concise, clean Python code (<270 lines) that builds assets/models/yacht_deck_salon.glb.",
        "prompt": BUILDER_API_SIG + """

Write `scripts/yacht_kit/job_deck_salon.py` to build `assets/models/yacht_deck_salon.glb` (strict AABB `[-1.53, 1.30, -3.20] .. [1.53, 3.52, 2.20]`, meters).
CRITICAL SIGHTLINE RULE: Twin aft sliding glass doors MUST be retracted outward behind fixed port/starboard curved glass so the entire central doorway `X in [-0.80, 0.80], Y in [1.32, 3.34]` at `Z = -3.20..-2.6` is 100% OPEN with NO glass or mullion blocking the bar!
Build:
1. Materials:
   - `hull_dark`: `load_bundle("hull_satin")`, `clearcoat=0.38`.
   - `marquetry`: `load_bundle("marquetry")`, `clearcoat=0.36, clearcoat_roughness=0.32`.
   - `leather`: `load_bundle("saddle_leather")`, `clearcoat=0.11`.
   - `stitch`: `load_bundle("stitch_strip")`, `clearcoat=0.05`.
   - `rug`: `load_bundle("woven_rug")`, `roughness=1.0`.
   - `travertine`: `load_bundle("filled_travertine")`, `clearcoat=0.06`.
   - `pvd`: `load_bundle("pvd_brushed")`, `metalness=1.0`.
   - `curved_glass`: `base_factor=(0.94, 0.97, 0.99, 1.0), roughness=0.07, metalness=0.0, transmission=0.94, ior=1.46, double_sided=True`.
   - `warm_cove`: `base_factor=(1.0, 0.88, 0.72, 1.0), roughness=0.3, emissive=(1.0, 0.72, 0.38)`.
   - `sconce_crystal`: `base_factor=(1.0, 0.92, 0.80, 1.0), roughness=0.15, emissive=(1.0, 0.78, 0.48), transmission=0.45, ior=1.52`.
2. Salon Envelope & Aft Curved Glass:
   - Floor `Y=1.30..1.32` (`X=-1.52..1.52, Z=-3.18..2.18`), woven rug `Y=1.32..1.328` (`X=-0.92..0.92, Z=-2.45..0.85`).
   - Cabin roof `Y=3.44..3.52` (`X=-1.53..1.53, Z=-3.20..2.20`, curved aft overhang matching `R≈2.40 m` plan arc), lintel above doorway `Y=3.34..3.44` with recessed `8 mm` `warm_cove` strip + continuous `4 mm` `pvd` golden thread!
   - Port & starboard salon side walls (`hull_dark` frame + large side `curved_glass` windows), plus curved panoramic aft glass (`R≈2.40 m` centered near `(0, y, -0.78)` spanning `|X|=0.80..1.52`, `8 mm` thick `curved_glass`) AND retracted sliding door leaves tucked behind them at `|X|=0.82..1.48`. Central `1.60 x 2.02 m` opening stays wide open!
3. Art Deco Interior:
   - Forward bulkhead (`Z=2.12..2.18`): 4 mirrored bookmatched `marquetry` panels (`0.39 x 1.05 m` each, centered across `X`, `Y=1.95..3.00`) framed by continuous `4 mm` `pvd` golden thread trim!
   - Mirrored port & starboard curved `leather` banquettes (`X=-1.45..-0.92` and `0.92..1.45`, `Z=-2.25..0.55`, seat top `Y=1.75` = `0.43 m` above floor, curved backrest `Y=1.75..2.28`, `stitch` edge seams & golden thread piping).
   - Filled travertine cold-drink bar: slab centered `(0, 2.36, 1.22)`, `1.78 x 0.62 m` (`bevel=0.004`, top `Y=2.38`), marquetry cabinet base (`Y=1.32..2.34`) with doors recessed `35 mm` & PVD pulls.
   - Left & right Art Deco twin-flute faceted crystal sconces (`0.11 x 0.075 x 0.32 m`) mounted at `(±1.40, 2.83, 0.15)` with `pvd` backplate.
4. Anchors: `door_left=(-0.80, 1.32, -3.12)`, `door_right=(0.80, 1.32, -3.12)`, `bar_top=(0, 2.38, 1.22)`, `journal_anchor=(-1.08, 1.76, -0.42)`, `dog_nap=(-1.06, 1.75, -1.18)`. Export to `assets/models/yacht_deck_salon.glb`.""",
    },
    {
        "name": "job_furniture_props",
        "out_path": "scripts/yacht_kit/job_furniture_props.py",
        "model": "deepseek-chat",
        "verify_cmd": "python3 scripts/yacht_kit/job_furniture_props.py && python3 scripts/yacht_kit/validate_glb.py --job furniture_props",
        "verify_timeout": 120,
        "system": "You are a Marine 3D Technical Artist. Return ONLY concise, clean Python code (<270 lines) that builds assets/models/yacht_furniture_props.glb.",
        "prompt": BUILDER_API_SIG + """

Write `scripts/yacht_kit/job_furniture_props.py` to build `assets/models/yacht_furniture_props.glb`.
STRICT ZONE RULE: Every single vertex MUST fall inside EITHER `deck_aabb: [[-1.50, 1.20, -9.00], [2.20, 2.32, -3.20]]` OR `cabin_aabb: [[-1.42, 1.32, -2.95], [1.42, 2.80, 1.60]]`! Check every coordinate carefully!
Build:
1. Materials: `teak_frame` (`load_bundle("teak_frame")`), `linen` (`load_bundle("outdoor_linen")`), `leather` (`load_bundle("saddle_leather")`), `crest_leather` (`load_bundle("saddle_leather_crest")`, `clamp_uv=True`), `stitch` (`load_bundle("stitch_strip")`), `pvd` (`load_bundle("pvd_brushed")`, `metalness=1.0`), `rope` (`base_factor=(0.80, 0.74, 0.62, 1.0), roughness=0.88`), `crystal_glass` (`base_factor=(0.94, 0.98, 1.0, 1.0), roughness=0.06, transmission=0.92, ior=1.50`), `piping_trim` (`base_factor=(0.28, 0.22, 0.19, 1.0), roughness=0.72`).
2. Four Exterior Deck Props (strictly inside `deck_aabb`):
   - **Two wood-frame marine-linen folding loungers** (`0.58 x 1.63 x 0.82 m` each) on starboard aft salon centered around `(0.62, 1.28, -4.45)` and `(1.44, 1.28, -4.45)`: `28x38 mm` teak_frame side rails, `Ø16 mm` PVD pivot pins, curved sling seat + backrest built via `add_grid` with arc-length cloth UVs! Keep Y <= 2.25!
   - **Round teak dining table** (`Ø0.78 x 0.73 m`, `28 mm` beveled top, 3 inward-tapered teak legs) at `(1.22, 1.30, -6.55)` (`top Y=2.03`) with folded square marine-linen napkin on top.
   - **Twin-post PVD mooring cleat** (`H=0.15 m`, `Ø38 mm` chamfered posts) + **5-turn coiled Ø26 mm rope** (`0.46 x 0.30 m` oval base built cleanly via swept tube grid) centered at `(1.52, 1.26, -8.55)`.
   - **Piped marine-linen dog cushion** (`0.78 x 0.43 x 0.055 m`, bevel `0.015`, `Ø6 mm` dark piping ring around perimeter) centered at `(-1.05, 1.328, -3.85)` (check X in `[-1.44..-0.66]`, strictly inside `[-1.50..2.20]`!).
3. Three Interior Cabin Props (strictly inside `cabin_aabb`):
   - **Barware on bar_top `(0, 2.38, 1.22)`**: Two 4-facet crystal water glasses (`H=0.098 m`, `Ø0.072 m`), brushed PVD ice bucket (`Ø0.180 x 0.185 m`) with faceted clear ice cubes, and an unlabeled flint-glass citrus sparkling water bottle (`H=0.25 m`, `Ø0.074 m`). (ALL unlabeled — NO logos!)
   - **Saddle-leather navigation logbook** (`0.18 x 0.018 x 0.125 m`, top cover mapped `(0,0)..(1,1)` to `crest_leather` showing the wordless double-line diamond crest!) resting on port banquette armrest at `(-1.08, 1.76, -0.42)` with `stitch` border strip.
   - **Banquette step-stool** (`0.38 x 0.16 x 0.28 m`, teak frame + saddle_leather padded top, `Y=1.32..1.48`) at `(-0.78, 1.32, -1.18)`.
4. Anchors: `dog_mat=(-1.05, 1.355, -3.85)`, `prop_cleat=(1.52, 1.26, -8.55)`, `prop_bar=(0, 2.38, 1.22)`, `prop_journal=(-1.08, 1.76, -0.42)`. Export to `assets/models/yacht_furniture_props.glb`.""",
    },
    {
        "name": "scenes_yacht_json",
        "out_path": "data/scenes_yacht.json",
        "model": "deepseek-chat",
        "check_tacky_copy": True,
        "verify_cmd": "python3 -c 'import json; d=json.load(open(\"data/scenes_yacht.json\")); assert all(k in d.get(\"beats\",{}) for k in (\"yacht_shade_mat\",\"yacht_bow_wind\",\"yacht_salon_nap\")); print(\"OK scenes_yacht.json\")'",
        "system": (
            "You write ultra-restrained Quiet Luxury literary Chinese copy for Bruce Happiness Club. "
            "Return ONLY valid UTF-8 JSON with no markdown. Never use banned status words or real luxury brand names."
        ),
        "prompt": """Write `data/scenes_yacht.json` as valid JSON containing:
{
  "meta": { "scene": "yacht", "code": "FLY·04", "title": "白帆游艇码头" },
  "beats": {
    "yacht_shade_mat": "这儿有一小块阴凉。",
    "yacht_bow_wind": "海风走在我们前面。",
    "yacht_salon_nap": "我听着水声，就眯一会儿。"
  },
  "thought_bubbles": {
    "idle_happy": [3 poetic sensory observations about the 20m deep-blue hull, champagne waterline, teak walkway, or travertine bar seen past open curved glass],
    "idle_sulk": [2 restrained lines when happiness < 80],
    "click_poke": [2 restrained lines mentioning Bruce's dark-burgundy silk scarf #652C39 in coastal breeze]
  }
}
Keep the exact 3 beat strings verbatim!""",
    },
]


def main():
    wave = sys.argv[1] if len(sys.argv) > 1 else "2a"
    if wave == "2a":
        res = run_parallel_codegen(WAVE_2A_TASKS, batch_name="batch7_wave2a_pbr_tex", max_workers=2, max_retries=3)
        save_telemetry(res, "batch7_wave2a_pbr_tex")
        print("Wave 2A complete:", res)
    elif wave == "2b":
        res = run_parallel_codegen(WAVE_2B_TASKS, batch_name="batch7_wave2b_glbs", max_workers=5, max_retries=3)
        save_telemetry(res, "batch7_wave2b_glbs")
        print("Wave 2B complete:", res)
    elif wave == "all":
        for w in ("2a", "2b"):
            sys.argv = [sys.argv[0], w]
            main()


if __name__ == "__main__":
    main()
