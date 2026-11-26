# DeepSeek Collaboration Playbook & Capability Ledger

## 1. Model Routing Policy
- **`deepseek-chat` (High-Throughput Parallel Worker)**:
  - 2D procedural PBR material synthesis (`PIL` + `NumPy`: herringbone parquet, Calacatta marble, travertine, fluted walnut, bouclé upholstery, wool carpets).
  - 2D vector/raster editorial artworks, TV gallery screensavers, Polaroid travel gallery illustrations (`SVG` / `PIL`).
  - 360° / Cyclorama panoramic sky + volumetric cumulus clouds synthesis (`4096×2048` sunny + `2048×1024` rainy).
  - 3D architectural & luxury furniture module codegen against `scripts/penthouse_kit/prim_lib.py` (`SceneContext` / `MeshBuilder` with strict bounding-box contracts).
  - Standalone CSS drafts, static verification tests, and localized JSON dialogue copywriting (with strict forbidden-term filtering).
- **`deepseek-reasoner` (Spatial & Mathematical Reasoning)**:
  - 3D camera Bezier/quintic transition arcs between split-level floors (`1F ⇄ 2F`) avoiding mezzanine balustrades and walls.
  - Complex GLSL shader math, procedural IK/physics constraints, and coordinate/UV orientation proofs.

## 2. Zero-Turn Auto-Repair Contract (`scripts/ds_worker.py`)
1. Antigravity defines the spatial blueprint, function signatures, coordinate envelopes, and automated validation command (`verify_cmd` or inline assertion script).
2. `run_parallel_codegen` dispatches up to `6` concurrent worker requests to `api.deepseek.com`.
3. Each output has markdown fences stripped, is saved directly to disk, and is immediately executed/checked locally.
4. If compilation, forbidden-word filtering, image checks, or 3D bounding-box assertions fail, `ds_worker.py` feeds the assistant's previous code + stderr traceback back to DeepSeek for automatic repair (up to `max_retries=3`) in the same run—consuming zero extra Antigravity turns.
5. Run telemetry is recorded to scratch and summarized below so each iteration compounds institutional knowledge.

## 3. Prompt Patterns That Work Best
- Provide exact Python/JS import signatures, exact `(X, Y, Z)` bounding boxes, and explicit face winding / UV orientation rules (`u: left->right`, `v: 0 bottom -> 1 top`, noting `prim_lib.export_glb` flips `v = 1 - v`).
- Ask for pure Python/JS source code only (no prose wrapper), paired with deterministic NumPy seeds (`np.random.default_rng(...)`) so assets remain reproducible.
- Enforce `FORBIDDEN_WORDS` checks inside every artwork/copy task.

## 4. Empirical Capability Ledger
| Date | Worker / Task | Model | Outcome & Notes |
| :--- | :--- | :--- | :--- |
| 2026-11-26 | `scripts/gen_deepseek_collab_pack.py` (onboarding & chat copy) | `deepseek-chat` | Verified: 28 nicknames, action lines, 12 offline chat replies with zero forbidden terms. |
| 2026-11-27 | Penthouse Batch 1: `tex_sky.py` (4K azure sky & white clouds + 2K rainy sky) | `deepseek-chat` | Passed via zero-turn auto-repair (3 attempts, 67.3s); refined cloud band falloff after inspecting `sky_sunny.jpg`. |
| 2026-11-27 | Penthouse Batch 1: `tex_pbr.py` (6× 2048px/1024px PBR textures) | `deepseek-chat` | Passed via zero-turn auto-repair (3 attempts, 102.3s; automatically lightened oak luminance >= 120). |
| 2026-11-27 | Penthouse Batch 1: `tex_artworks.py` (3× TV gallery arts, 4× 2F travel Polaroids, vinyl cover) | `deepseek-chat` | **Key Lesson**: Splitting complex multi-canvas painting generators into concise helper functions avoids 8K token truncation; passed in 2 attempts (23.2s). Visually swapped Art 3 to Med olive/amphora still life after visual inspection. |
| 2026-11-27 | Penthouse Batch 2: `js/hub3d/duplexCamMath.js` (`1F <-> 2F` elevator bezier/quintic arc) | `deepseek-reasoner` | First-attempt pass (9.5s), zero syntax or boundary issues, verified smooth balustrade clearance in browser QA. |
| 2026-11-27 | Penthouse Batch 2: `mod_salon_seating.py`, `mod_media_fireplace.py`, `mod_stair_balustrade.py`, `mod_loft_2f.py`, `mod_terrace_sky.py` | `deepseek-chat` | **Key Discovery**: Including exact positional signatures of `MeshBuilder` (`add_box`, `add_cylinder`, `add_rounded_box`, `add_tri_raw`) AND exact printed bounding tuples inside `verify_cmd` dropped retries from 4 -> **1 attempt (6.7s–8.7s per 3D module!)**. Visually verified `add_tri_raw` continuous `U` (`0..1`) vs `add_quad` per-segment UV tiling on curved cycloramas. |
| 2026-11-27 | `scripts/gen_duplex_copy.py` (5 duplex contextual speech banks) | `deepseek-chat` | First-attempt pass; generated 1F/2F greetings, TV artwork comments, lamp toggle & blue-sky lines with 0 forbidden terms. |
