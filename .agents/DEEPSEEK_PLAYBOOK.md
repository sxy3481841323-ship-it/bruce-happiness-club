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
| 2026-11-27 | Quiet-Luxury Batch 3: `tex_sky.py` (v2 cumulus clusters `4096×1024`), `tex_artworks.py` (collector set + `ELOWEN NO.07`), `tex_pbr.py` (linen/suede/borderless rug), `tex_cafe_coastal.py` (`4096×2048` zero-blur coastline) | `deepseek-chat` | 4-way parallel codegen + `ds_worker.py` `check_tacky_copy` enforcement; verified true volumetric puffy clouds (zero horizontal bands) & crisp coastal shoreline. |
| 2026-11-27 | Quiet-Luxury Batch 4: `mod_entry_and_niches.py`, `mod_salon_seating.py` v2, `gen_quiet_luxury_copy.py` | `deepseek-chat` | Both 3D modules passed in **1 attempt** (9.2s & 11.7s); quiet-luxury copywriter rewrote roastery, `ELOWEN · 有机市集`, and sunlit `阁楼黑胶时光` lines with zero forbidden/tacky terms. |
| 2026-11-27 | Quiet-Luxury Batch 5A/5B: `tex_luxury_props.py`, `tex_wine_and_cafe.py`, `mod_entry_and_niches.py` v3, `mod_media_fireplace.py`, `mod_salon_seating.py`, `mod_loft_2f.py`, `concierge_copy_v3.json` | `deepseek-chat` | 7/7 parallel codegen tasks passed in **1–2 attempts** (`3.45s–33.35s`); Antigravity code-reviewed coordinates/orientation (`mod_loft_2f` credenza Z-alignment, horizontal split-oak hearth logs, `+Z` screen tilt) prior to GLB export. |
| 2026-11-28 | Quiet-Luxury Batch 6: `js/audioSoundscape.js`, `js/pantryIcons.js`, `scripts/update_quiet_luxury_content.py`, `data/concierge_dialogue_v4.json` | `deepseek-chat` | **Key Lessons**: (1) SVG external-link checks must whitelist standard `xmlns="http://www.w3.org/2000/svg"`; (2) Give Web Audio DSP codegen an explicit `180–260 line` concise budget so `deepseek-chat` completes cleanly in **1 attempt (22.47s)** without 8K output truncation (Antigravity fixed closure capture in `_stopScene`/`_stopHifi` & initial `master.gain` ramp); (3) Schema-locked Python JSON transformer (`update_quiet_luxury_content.py`) safely sanitized 570-line `content.json` with 100% numeric treat math preserved. |
| 2026-11-28 | Marine Architecture Batch 7A/7B: `tex_woods_stone.py`, `tex_fabrics_metals.py`, `job_berth.py`, `job_hull_rig.py`, `job_deck_salon.py`, `job_furniture_props.py`, `data/scenes_yacht.json` | `deepseek-chat` | **Key Lessons**: (1) Always pass exact Python helper signatures (`tex_helpers.py`, `YachtGLBBuilder`, `YachtMesh`) in the prompt -> dropped Wave 2A/2B to **1–2 attempts (`3.1s–42.4s`)**; (2) Provide a fast vectorized `periodic_voronoi(cells, size)` helper for leather/pebble distance fields and center deck caulk grooves on wrap boundaries so `verify_seamless_2x2` passes cleanly; (3) Visual Chromium screenshot inspection immediately caught `-Y` deck quad winding, missing `flip=True` on lounger slings, missing `z < maxZ` cabin bounds check, and banquette backrest depth—all fixed via targeted geometry & camera verification. |
