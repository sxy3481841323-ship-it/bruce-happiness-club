#!/usr/bin/env python3
"""
Batch 3 (15 MB Quiet Luxury Standard): Dispatch 4 concurrent DeepSeek visual/texture generators:
1. scripts/penthouse_kit/tex_sky.py (4096x1024 true 4:1 Malibu cobalt-cerulean sky + round cluster cumulus clouds)
2. scripts/penthouse_kit/tex_artworks.py (7 collector impasto/silver-gelatin paintings + NO. 07 patron card + jazz vinyl sleeve)
3. scripts/penthouse_kit/tex_pbr.py (borderless hand-knotted wool/alpaca rug + sheer linen + cognac suede + existing textures)
4. scripts/penthouse_kit/tex_cafe_coastal.py (4096x2048 razor-sharp Malibu coast + silver-gelatin wave print)
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from ds_worker import run_parallel_codegen


SKY_V2_VERIFY = r"""
import os, sys, numpy as np
sys.path.insert(0, 'scripts')
from penthouse_kit.tex_sky import make_sunny_sky_panorama, make_rainy_sky_panorama
os.makedirs('assets/textures', exist_ok=True)
sun = make_sunny_sky_panorama(4096, 1024)
assert sun.size == (4096, 1024) and sun.mode == 'RGB', f'bad sky size {sun.size}'
arr = np.asarray(sun, dtype=np.float32)
zenith = arr[:int(1024*0.20), :, :]
zr, zg, zb = float(zenith[:,:,0].mean()), float(zenith[:,:,1].mean()), float(zenith[:,:,2].mean())
assert zb > 130 and (zb - zr) > 85, f'Zenith not rich cobalt blue: ({zr:.1f},{zg:.1f},{zb:.1f})'
upper = arr[:int(1024*0.56), :, :]
clouds = (upper[:,:,0] > 218) & (upper[:,:,1] > 218) & (upper[:,:,2] > 220)
cf = float(clouds.mean())
assert 0.08 <= cf <= 0.36, f'Cloud fraction must be puffy & open sky (8-36%), got {cf:.3f}'
sun.save('assets/textures/sky_sunny.jpg', format='JPEG', quality=95, optimize=True)
rain = make_rainy_sky_panorama(2048, 512)
assert rain.size == (2048, 512)
rain.save('assets/textures/sky_rainy.jpg', format='JPEG', quality=92, optimize=True)
print(f'SKY_V2_OK zenith=({zr:.0f},{zg:.0f},{zb:.0f}) cloud_frac={cf:.2%}')
"""

ART_V2_VERIFY = r"""
import os, sys, numpy as np
sys.path.insert(0, 'scripts')
from penthouse_kit.tex_artworks import (
    make_tv_artworks, make_gallery_travel_artworks, make_vinyl_cover_tex, make_patron_card_tex
)
os.makedirs('assets/textures', exist_ok=True)
tvs = make_tv_artworks()
assert len(tvs) == 3
for i, im in enumerate(tvs, 1):
    assert im.size == (1600, 900) and im.mode == 'RGB', f'tv {i}: {im.size}'
    arr = np.asarray(im, dtype=np.float32)
    assert np.std(arr) > 4.0, f'tv {i} looks blank'
    im.save(f'assets/textures/tv_art_{i}.jpg', format='JPEG', quality=95, optimize=True)
gals = make_gallery_travel_artworks()
assert len(gals) == 4
for i, im in enumerate(gals, 1):
    assert im.size == (800, 1000) and im.mode == 'RGB', f'gal {i}: {im.size}'
    assert np.std(np.asarray(im, dtype=np.float32)) > 4.0, f'gal {i} looks blank'
vin = make_vinyl_cover_tex(1024)
assert vin.size == (1024, 1024) and vin.mode == 'RGB'
card = make_patron_card_tex(1024, 640)
assert card.size == (1024, 640) and card.mode == 'RGB'
card.save('assets/textures/patron_card.jpg', format='JPEG', quality=95, optimize=True)
print('ART_V2_OK')
"""

PBR_V2_VERIFY = r"""
import sys, numpy as np
sys.path.insert(0, 'scripts')
from penthouse_kit.tex_pbr import (
    make_herringbone_oak_tex, make_calacatta_marble_tex, make_boucle_fabric_tex,
    make_travertine_tex, make_fluted_walnut_tex, make_plush_rug_tex,
    make_sheer_linen_tex, make_cognac_suede_tex
)
checks = [
    ('oak', make_herringbone_oak_tex(2048), (2048, 2048), 125),
    ('marble', make_calacatta_marble_tex(2048), (2048, 2048), 195),
    ('boucle', make_boucle_fabric_tex(1024), (1024, 1024), 195),
    ('travertine', make_travertine_tex(1024), (1024, 1024), 175),
    ('walnut', make_fluted_walnut_tex(1024), (1024, 1024), 45),
    ('rug', make_plush_rug_tex(2048), (2048, 2048), 185),
    ('sheer_linen', make_sheer_linen_tex(1024), (1024, 1024), 195),
    ('cognac_suede', make_cognac_suede_tex(1024), (1024, 1024), 60),
]
for name, img, sz, min_luma in checks:
    assert img.size == sz and img.mode == 'RGB', f'{name}: bad {img.size}'
    arr = np.asarray(img, dtype=np.float32)
    assert np.isfinite(arr).all() and float(arr.mean()) >= min_luma, f'{name} failed check'
# Verify borderless alpaca rug (no dark hotel rectangle frame near borders)
rug_arr = np.asarray(make_plush_rug_tex(1024), dtype=np.float32)
assert abs(float(rug_arr[:40].mean()) - float(rug_arr[400:600].mean())) < 18, 'Rug still has a stark border frame!'
print('PBR_V2_OK')
"""

CAFE_V2_VERIFY = r"""
import sys, numpy as np
sys.path.insert(0, 'scripts')
from penthouse_kit.tex_cafe_coastal import make_malibu_coastal_panorama, make_coastal_wave_photo_tex
coast = make_malibu_coastal_panorama(4096, 2048)
assert coast.size == (4096, 2048) and coast.mode == 'RGB'
arr = np.asarray(coast, dtype=np.float32)
# Check crispness (high-frequency detail, no GaussianBlur mush)
grad = np.abs(np.diff(arr[1100:1600, :, :], axis=1)).mean()
assert grad > 2.2, f'Coast image too blurry (mean diff={grad:.2f})'
wave = make_coastal_wave_photo_tex(1024)
assert wave.size == (1024, 1024) and wave.mode == 'RGB'
print(f'CAFE_COAST_OK sharpness_grad={grad:.2f}')
"""

TASKS = [
    {
        "name": "tex_sky_v2_cumulus",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/tex_sky.py",
        "check_tacky_copy": True,
        "system": (
            "You are a senior graphics programmer specializing in atmospheric scattering & volumetric cumulus clouds in Python NumPy+PIL. "
            "Return ONLY valid Python 3 code with no markdown fences."
        ),
        "prompt": """Rewrite `scripts/penthouse_kit/tex_sky.py` so exterior penthouse clouds are TRUE ROUND BILLOWING CUMULUS CLOUDS (NEVER horizontal line streaks!) and the sky is a rich California coastal cobalt-cerulean blue:
CRITICAL GEOMETRY FACT: The 3D sky cyclorama is `~180` units wide by `42` units tall (~4.2:1 aspect ratio). Therefore `make_sunny_sky_panorama` MUST use default size **`(w=4096, h=1024)`** (`4:1` aspect ratio so every world pixel is square, 1:1)!
1. `make_sunny_sky_panorama(w=4096, h=1024) -> PIL.Image.Image`:
   - Sky vertical stops (`y/h` from `0.0` top to `1.0` bottom):
     - Zenith `0.00 -> 0.58`: deep pure cobalt `#154690` -> crisp Malibu cerulean `#2C6DB8` -> sunlit horizon blue `#5A9CE0` -> warm alabaster horizon haze `#EBF2F7` right at `0.58`. Avoid chalky pale-cyan washout (`B - R` at top 20% must be `> 90`).
     - Ocean `0.58 -> 1.00`: crisp deep Pacific sapphire `#245A88` at horizon line blending softly down to `#4478A2`.
   - Warm subtle sun glow centered near `(0.58*w, 0.24*h)`.
   - **CUMULUS CLOUD CLUSTERS (DO NOT use horizontal grid noise!)**:
     - Generate `24` independent fluffy cumulus cloud formations placed organically across `u in [0.06, 0.94]`, `v in [0.16, 0.48]` (use deterministic `rng = np.random.default_rng(77)`).
     - Each cloud formation consists of `10..16` overlapping **isotropic circular puff blobs in PIXEL coordinates** (radius `rx = ry * 1.15` in pixels, e.g., `ry ~ 26..68px`, `rx ~ 30..82px` — because the image is `4096x1024` mapped onto `4.2:1` world space, near-circular puffs in pixel space look naturally billowing round in 3D instead of stretched lines!).
     - Perturb the puff distance field smoothly with isotropic high-frequency detail (`dx/r, dy/r`) using vectorized bounding-box slice updates (fast! finishes `< 2s`).
     - Flatten cloud bottoms very gently while keeping domed cauliflower tops crisp `#FFFCF7`, and shade lower undersides soft cool silver-blue `#C8D9EC` based on vertical offset within the cluster!
     - Leave generous (~70-82%) clean cobalt sky visible around distinct sculptural cloud banks (cloud coverage ~14-28% of upper sky).
2. `make_rainy_sky_panorama(w=2048, h=512) -> PIL.Image.Image`:
   - Calm cool slate twilight overcast (`#2B3B4D`..`#556B82`), used ONLY when mood score `< 80`.

Return ONLY complete Python 3 code.""",
        "verify_cmd": ["python3", "-c", SKY_V2_VERIFY],
        "verify_timeout": 90,
    },
    {
        "name": "tex_artworks_v2_collector",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/tex_artworks.py",
        "check_tacky_copy": True,
        "system": (
            "You are a museum conservator & computational fine artist generating high-resolution oil impasto, raw linen, "
            "and archival silver-gelatin textures via NumPy heightfields, Sobel raking light normals, and PIL. "
            "Strictly avoid any literal status words or Chinese city words. Keep code clean, modular and under 280 lines. Return ONLY valid Python 3 code."
        ),
        "prompt": """Rewrite `scripts/penthouse_kit/tex_artworks.py` replacing ALL flat cartoon shapes with authentic **AD100 collector impasto oil paintings, raw Belgian linen gestures, and silver-gelatin photography** (concise helper functions so code never exceeds ~260 lines):
1. Shared tactile studio helpers:
   - `_linen_canvas(w, h, seed)`: fine crosshatch woven Belgian linen warp/weft bump & color texture;
   - `_raking_light(height_map, strength=1.0)`: computes `dx, dy` slopes (Sobel/gradient from top-left `(-0.7, -0.7, 1.0)`) to cast authentic 2-3mm palette-knife relief highlights & micro-shadows onto oil paintings;
   - `_museum_mat(inner_img, out_w, out_h, mat_color=(244,240,232))`: crisp wide museum passe-partout mat with thin `#322B24` shadow bevel.
2. `make_tv_artworks() -> list[PIL.Image.Image]` returning 3 `1600x900` horizontal works:
   - Art 1 (**Afternoon Wall · Color-Field Oil**): Rothko / Vervoordt stacked luminous bands of warm limestone `#DDD0BC`, burnt ochre `#AE7646`, and deep umber-charcoal `#2B2521` with soft feathered edges, vertical dry-brush bristles & raking relief light.
   - Art 2 (**Salt Mist · Chalk Plaster Relief**): Minimalist sculptural monochrome cream-ivory `#F0EADF` impasto sweeping knife arcs lit obliquely via `_raking_light` so shadows reveal sculptural ridges.
   - Art 3 (**Regatta Silver Gelatin**): Museum-matted archival monochrome silver-gelatin sea horizon photograph with fine film grain, distant morning mist, and two crisp slanting classic sloop sails catching sunlight.
3. `make_gallery_travel_artworks() -> list[PIL.Image.Image]` returning 4 `800x1000` vertical works for 2F:
   - Work 1 (**Strata**): Mineral sand, limewash & terracotta horizontal sedimentary scraper textures;
   - Work 2 (**Horizon Study**): Misty slate-blue sky above deep indigo sea with a single delicate silver reflection glint;
   - Work 3 (**Linen Gesture**): Unbleached warm Belgian linen `#DAD0BE` with loose architectural charcoal & chalk sweeping loops;
   - Work 4 (**Amber Hour**): Rich dense short impasto brush dabs in warm sienna, ochre, umber, and cream framed in museum mat.
4. `make_patron_card_tex(w=1024, h=640) -> PIL.Image.Image`:
   - Minimalist cotton-stock account card in matte Studio Green / dark slate (`#1D231F`), fine hairline muted gold rule inset 32px, centered crisp serif/sans tracking:
     - Small tracked header: `BEVERLY HILLS · ORGANIC PROVISIONS`
     - Main wordmark (clean crisp vector strokes or large font): `ELOWEN`
     - Bottom line: `HOUSE ACCOUNT · NO. 07` (NO "VIP", NO "MEMBER").
5. `make_vinyl_cover_tex(size=1024) -> PIL.Image.Image`:
   - Archival ECM/Blue-Note minimalist jazz LP sleeve (`COOL AFTERNOON · 33 RPM` offset typographic block & slate-amber tonal study).

Use `ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia.ttf', ...)` / `Helvetica.ttc` with clean fallback to `load_default()`. Return ONLY Python code.""",
        "verify_cmd": ["python3", "-c", ART_V2_VERIFY],
        "verify_timeout": 90,
    },
    {
        "name": "tex_pbr_v2_quiet_luxury",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/tex_pbr.py",
        "check_tacky_copy": True,
        "system": "You are a senior PBR material artist writing fast vectorized NumPy+PIL texture generators. Return ONLY Python 3 code.",
        "prompt": """Rewrite `scripts/penthouse_kit/tex_pbr.py` implementing all 8 seamless AD100 interior textures (fast vectorized NumPy, finishes in `<1.5s` each):
Keep existing signatures:
1. `make_herringbone_oak_tex(size=2048)` (warm honey-oak parquet `#DEC8A8`..`#C9A984`, refined bevels)
2. `make_calacatta_marble_tex(size=2048)` (creamy white `#F8F5EE` with organic dove-gray & delicate warm gold veins)
3. `make_boucle_fabric_tex(size=1024)` (warm oatmeal-ivory `#F4EFE5` nubby Belgian bouclé)
4. `make_travertine_tex(size=1024)` (honed Roman beige `#E7DBC8` with delicate linear porous strata)
5. `make_fluted_walnut_tex(size=1024)` (architectural vertical walnut flutes `#643E26`..`#241309`)
6. `make_plush_rug_tex(size=2048)`: **IMPORTANT CHANGE**: Borderless undyed raw alpaca & wool hand-knotted carpet (`#EFE9DE` .. `#E3DACB`) with gentle horizontal hand-loomed abrash & micro tuft fiber grain — **COMPLETELY REMOVE any dark hotel-lobby concentric rectangle border!**
7. `make_sheer_linen_tex(size=1024)`: Translucent-toned unbleached Belgian slub linen drapery texture (`#F5EFE4` with fine vertical & horizontal irregular flax slub fibers).
8. `make_cognac_suede_tex(size=1024)`: Rich warm cognac/saddle nubuck calfskin suede (`#9C5C34` with velvety micro-nap variation).

Return ONLY complete Python 3 code.""",
        "verify_cmd": ["python3", "-c", PBR_V2_VERIFY],
        "verify_timeout": 90,
    },
    {
        "name": "tex_cafe_coastal_4k",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/tex_cafe_coastal.py",
        "check_tacky_copy": True,
        "system": "You are a senior architectural visualizer creating crisp 4K coastal backdrops & archival film photography in NumPy+PIL. Return ONLY Python 3 code.",
        "prompt": """Write `scripts/penthouse_kit/tex_cafe_coastal.py` for our Malibu Private Coastal Roastery (`OUT·01`):
1. `make_malibu_coastal_panorama(w=4096, h=2048) -> PIL.Image.Image`:
   - **CRITICAL**: ZERO `GaussianBlur` on the final image! Everything viewed outside the roastery floor-to-ceiling windows must look razor-sharp in 4K:
   - Rich cobalt-cerulean sky (`#1A519A` -> `#5998DC` -> warm horizon `#EEF3F7` at `v=0.56`) with sculptural crisp-edged puffy cumulus clouds (round isotropic puff clusters, sunny tops, shaded bellies, plenty of blue sky).
   - Multi-band crystal Pacific sea (`v = 0.56 .. 0.78`): deep sapphire horizon -> translucent turquoise shallows -> crisp specular wavelets -> 2 crisp lacy white surf foam lines near `v=0.77` -> warm pale limestone sand beach below `v=0.78`.
   - Left coastline silhouette (`u in [0.0, 0.28], v in [0.46, 0.72]`): sunlit sandstone Malibu bluff with textured dark olive cypress & palm silhouettes and crisp coastal cliff facets.
   - Offshore (`u ~ 0.42` and `u ~ 0.62`, just above `v=0.58` horizon): two delicate sharp-edged wooden sloop sailboats with tall white sails and fine reflections on water!
2. `make_coastal_wave_photo_tex(size=1024) -> PIL.Image.Image`:
   - Framed museum-matted silver-gelatin archival photograph of a sunlit curling Pacific wave & foam curl (high-contrast monochrome `#1E2124`..`#F2EFE9`, authentic film grain, wide cream matte `#F4F0E8` with slender walnut-charcoal inner border) — replaces the old generic triangle wall art!

Return ONLY complete Python 3 code.""",
        "verify_cmd": ["python3", "-c", CAFE_V2_VERIFY],
        "verify_timeout": 90,
    },
]

if __name__ == "__main__":
    os.chdir(REPO_ROOT)
    selected = TASKS
    if "--only" in sys.argv:
        idx = sys.argv.index("--only")
        want = set(sys.argv[idx + 1 :])
        selected = [t for t in TASKS if t["name"] in want]
    run_parallel_codegen(selected, batch_name="luxury_v2_art_batch", max_workers=4, max_retries=3)
