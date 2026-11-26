#!/usr/bin/env python3
"""
Batch 1: Dispatch 3 concurrent DeepSeek workers to build:
1. scripts/penthouse_kit/tex_sky.py (4096x2048 sunny azure blue sky + cumulus clouds & rainy sky)
2. scripts/penthouse_kit/tex_pbr.py (6 luxury 2048px/1024px seamless interior PBR textures)
3. scripts/penthouse_kit/tex_artworks.py (3 TV artworks, 4 2F travel gallery paintings, vinyl sleeve)
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from ds_worker import run_parallel_codegen


SKY_VERIFY = r"""
import os, sys, numpy as np
sys.path.insert(0, 'scripts')
from penthouse_kit.tex_sky import make_sunny_sky_panorama, make_rainy_sky_panorama
os.makedirs('assets/textures', exist_ok=True)
sun = make_sunny_sky_panorama(4096, 2048)
assert sun.size == (4096, 2048), f'bad size {sun.size}'
arr = np.asarray(sun, dtype=np.float32)
top = arr[:1024, :, :]
mr, mg, mb = float(top[:, :, 0].mean()), float(top[:, :, 1].mean()), float(top[:, :, 2].mean())
assert mb > 190 and (mb - mr) > 40, f'Sky not blue enough: mean=({mr:.1f},{mg:.1f},{mb:.1f})'
clouds = (top[:, :, 0] > 228) & (top[:, :, 1] > 232) & (top[:, :, 2] > 238)
cf = float(clouds.mean())
assert 0.08 <= cf <= 0.62, f'Cloud fraction out of range: {cf:.3f}'
sun.save('assets/textures/sky_sunny.jpg', format='JPEG', quality=88, optimize=True)
rain = make_rainy_sky_panorama(2048, 1024)
assert rain.size == (2048, 1024)
rain.save('assets/textures/sky_rainy.jpg', format='JPEG', quality=85, optimize=True)
print(f'SKY_OK sun_mean=({mr:.0f},{mg:.0f},{mb:.0f}) cloud_frac={cf:.2%}')
"""

PBR_VERIFY = r"""
import sys, numpy as np
sys.path.insert(0, 'scripts')
from penthouse_kit.tex_pbr import (
    make_herringbone_oak_tex, make_calacatta_marble_tex, make_boucle_fabric_tex,
    make_travertine_tex, make_fluted_walnut_tex, make_plush_rug_tex
)
checks = [
    ('oak', make_herringbone_oak_tex(2048), (2048, 2048), 120),
    ('marble', make_calacatta_marble_tex(2048), (2048, 2048), 195),
    ('boucle', make_boucle_fabric_tex(1024), (1024, 1024), 200),
    ('travertine', make_travertine_tex(1024), (1024, 1024), 175),
    ('walnut', make_fluted_walnut_tex(1024), (1024, 1024), 45),
    ('rug', make_plush_rug_tex(1024), (1024, 1024), 190),
]
for name, img, sz, min_luma in checks:
    assert img.size == sz and img.mode == 'RGB', f'{name}: bad {img.size} {img.mode}'
    arr = np.asarray(img, dtype=np.float32)
    assert np.isfinite(arr).all(), f'{name}: non-finite'
    luma = float(arr.mean())
    assert luma >= min_luma, f'{name}: too dark ({luma:.1f} < {min_luma})'
print('PBR_OK')
"""

ART_VERIFY = r"""
import os, sys, numpy as np
sys.path.insert(0, 'scripts')
from penthouse_kit.tex_artworks import make_tv_artworks, make_gallery_travel_artworks, make_vinyl_cover_tex
os.makedirs('assets/textures', exist_ok=True)
tvs = make_tv_artworks()
assert len(tvs) == 3
for i, im in enumerate(tvs, 1):
    assert im.size == (1024, 576) and im.mode == 'RGB', f'tv {i}: {im.size}'
    im.save(f'assets/textures/tv_art_{i}.jpg', format='JPEG', quality=90, optimize=True)
gals = make_gallery_travel_artworks()
assert len(gals) == 4
for i, im in enumerate(gals, 1):
    assert im.size == (512, 640) and im.mode == 'RGB', f'gal {i}: {im.size}'
vin = make_vinyl_cover_tex(512)
assert vin.size == (512, 512) and vin.mode == 'RGB'
print('ART_OK')
"""

TASKS = [
    {
        "name": "tex_sky_panorama",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/tex_sky.py",
        "system": (
            "You are a senior technical artist writing fast NumPy+PIL procedural sky panorama generators in Python 3. "
            "Return ONLY valid Python code (no markdown fences, no prose). Use vectorized NumPy ops so 4096x2048 runs in under 2 seconds."
        ),
        "prompt": """Write `scripts/penthouse_kit/tex_sky.py` providing two functions:
1. `make_sunny_sky_panorama(w=4096, h=2048) -> PIL.Image.Image` (RGB):
   - Renders a bright, joyful, Mediterranean sunlit azure sky cyclorama viewed from a luxury top-floor penthouse!
   - Top half `y < 0.56*h`: rich clear sky gradient from deep azure zenith `#1F6BE0` at `y=0` through vibrant cerulean `#53A5FA` to warm crisp horizon haze `#D8EEFF` / `#FFF6E8` around `y=0.56*h`, plus a soft golden morning sun halo at roughly `(0.62*w, 0.24*h)`.
   - Multi-layered fluffy white cumulus clouds across `y in [0.10*h, 0.50*h]` using vectorized 2D trigonometric / multi-octave fBm noise in NumPy (fast! avoid slow Python loops over pixels): sunlit crisp `#FFFFFF` tops (`R>235, G>238, B>242` occupying ~18-40% of the upper sky) with soft lavender-silver `#DCE8F8` cloud bellies so it looks painterly and sunlit, NEVER overcast gray!
   - Below `y > 0.56*h`: calm shimmering cerulean ocean & soft distant golden coastline / sunlit mist (`#7FB8DC` blending down to `#C9DFF0`) so downward angles from 2F look peaceful and natural.
2. `make_rainy_sky_panorama(w=2048, h=1024) -> PIL.Image.Image` (RGB):
   - Cozy rainy slate-blue sky (`#2F4257` .. `#5E748C`) with soft rainclouds for cold-war/rain-vinyl mood.

Verify deterministic seeds (`np.random.default_rng`), fast vectorized NumPy, return `Image.fromarray(..., 'RGB')`. Return ONLY Python code.""",
        "verify_cmd": ["python3", "-c", SKY_VERIFY],
        "verify_timeout": 90,
    },
    {
        "name": "tex_pbr_materials",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/tex_pbr.py",
        "system": (
            "You are a senior architectural visualization material artist writing fast vectorized NumPy+PIL procedural PBR texture generators. "
            "Return ONLY valid Python code with zero markdown explanation."
        ),
        "prompt": """Write `scripts/penthouse_kit/tex_pbr.py` implementing 6 bright, ultra-refined luxury interior architectural textures (NO dark muddy or dirty textures!):
1. `make_herringbone_oak_tex(size=2048) -> PIL.Image.Image`:
   - Warm pale-honey French oak herringbone parquet (`#DFC7A4` to `#C7A67E` planks) with crisp herringbone diagonal joints (`45°` chevron/herringbone look, tileable), fine delicate wood grain, subtle plank-to-plank warm variance.
2. `make_calacatta_marble_tex(size=2048) -> PIL.Image.Image`:
   - Creamy white Italian Calacatta Gold slab (`#F8F5EE` ivory-white stone) with organic diagonal flowing dove-gray veins (`#B6B0A8`) delicately kissed with warm champagne-gold veins (`#C9A663`).
3. `make_boucle_fabric_tex(size=1024) -> PIL.Image.Image`:
   - Tactile creamy white/oatmeal Italian bouclé upholstery (`#F6F0E4`) with fine multi-scale woven pebble loops.
4. `make_travertine_tex(size=1024) -> PIL.Image.Image`:
   - Honed Roman beige travertine (`#E9DEC9`) with subtle horizontal sedimentary bedding bands and tiny mineral pores.
5. `make_fluted_walnut_tex(size=1024) -> PIL.Image.Image`:
   - Luxury architectural vertical fluted American walnut slats (24 flutes across X with semicircular lighting roll-off: warm walnut crests `#684028` and crisp dark walnut shadow grooves `#26140A` + fine vertical grain).
6. `make_plush_rug_tex(size=1024) -> PIL.Image.Image`:
   - Soft cream-ivory wool rug (`#F2ECE2`) with ultra-fine fibrous tuft texture and an understated woven oatmeal-gold border frame.

Use vectorized NumPy ops (`size=2048` must finish in <1.5s each), fixed seeds, return `Image.fromarray(..., 'RGB')`. Return ONLY Python code.""",
        "verify_cmd": ["python3", "-c", PBR_VERIFY],
        "verify_timeout": 90,
    },
    {
        "name": "tex_artworks_curator",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/tex_artworks.py",
        "system": (
            "You are an editorial art director writing high-resolution PIL+ImageDraw+NumPy illustration generators. "
            "Strictly avoid any Chinese city names or specific landmarks. Return ONLY valid Python code."
        ),
        "prompt": """Write a concise, clean `scripts/penthouse_kit/tex_artworks.py` (keep total length ~180-260 lines by sharing small helper functions so code is never truncated!) using PIL (`Image`, `ImageDraw`, `ImageFilter`) + `numpy`:
1. `make_tv_artworks() -> list[PIL.Image.Image]` returning 3 `1024x576` RGB paintings for the Living Room Gallery Art TV:
   - Art 1: Abstract Sunlit Coast & White Sailboats — deep cerulean ocean, golden cliffside, two crisp geometric white sailboat sails, warm sun orb.
   - Art 2: Quiet Luxury Bauhaus Composition — creamy linen background `#F6EFE2` with intersecting arches & spheres in Roman travertine `#DFCCB0`, burgundy `#6E1824`, walnut `#4A2B1B`, and champagne gold `#DFBE7D`.
   - Art 3: Golden-Hour Coastal Terrace — minimalist warm painterly portrait of a cream long-haired dachshund silhouette looking out an arched sunlit balcony at clouds & lemon leaves.
2. `make_gallery_travel_artworks() -> list[PIL.Image.Image]` returning 4 `512x640` RGB Polaroid/gallery paintings for the 2F `FLY·04` travel wall:
   - Card 1: Nordic Aurora Cabin under emerald aurora & pines;
   - Card 2: Turquoise Bay Promenade with striped parasol & golden beach;
   - Card 3: Luxury Wooden Yacht Deck gliding on deep sapphire sea under puffy white clouds;
   - Card 4: Alpine Golden Meadow at sunrise with distant snow-capped peaks.
   (Wrap each with a clean cream museum mat border helper!)
3. `make_vinyl_cover_tex(size=512) -> PIL.Image.Image`:
   - Mid-century modern jazz vinyl album cover (`SUNLIT PENTHOUSE · 33RPM` sunburst in burgundy, champagne gold, and cream).

Make sure exact exported names exist: `make_tv_artworks`, `make_gallery_travel_artworks`, `make_vinyl_cover_tex`. Return ONLY complete, concise Python code.""",
        "verify_cmd": ["python3", "-c", ART_VERIFY],
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
    run_parallel_codegen(selected, batch_name="penthouse_batch1_2d_art", max_workers=3, max_retries=3)
