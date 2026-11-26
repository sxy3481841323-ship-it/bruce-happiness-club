#!/usr/bin/env python3
"""
Batch 2: Dispatch 5 concurrent DeepSeek-chat 3D luxury furniture builders +
1 DeepSeek-reasoner 1F<->2F camera interpolation math module.
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from ds_worker import run_parallel_codegen


COMMON_SYS = (
    "You are a senior Three.js / glTF 3D architectural furniture engineer writing Python 3 modules "
    "using `SceneContext` and `MeshBuilder`.\n"
    "EXACT API (DO NOT invent other methods or keyword argument names!):\n"
    "1. `b = ctx.mb(mesh_name: str, mat_idx: int)` returns a `MeshBuilder`. NEVER call `ctx.add_box` or `ctx.add_quad` directly!\n"
    "2. Exact `MeshBuilder` signatures:\n"
    "   - `b.add_quad(p0, p1, p2, p3, uv_scale=(1.0, 1.0), flip=False)`\n"
    "   - `b.add_box(cx, cy, cz, sx, sy, sz, uv_tile=0.0, rot_y=0.0)`\n"
    "   - `b.add_rounded_box(cx, cy, cz, sx, sy, sz, bevel=0.06, uv_tile=0.0, rot_y=0.0)`\n"
    "   - `b.add_cylinder(cx, y0, cz, r_bot, r_top, height, segs=18, rot_x=0.0, rot_z=0.0, cap_top=True, cap_bot=True)`  # NOTE: positional or y0, r_bot, r_top, segs (NOT y=, radius=, segments=)\n"
    "   - `b.add_sphere(cx, cy, cz, rx, ry=None, rz=None, rings=12, segs=18)`\n"
    "   - `b.add_lathe(cx, y0, cz, profile, segs=22)`  # profile = list of (radius, y_offset)\n"
    "   - `b.add_curved_tube(spine_pts, radii, segs=10)`  # radii = list matching len(spine_pts)\n"
    "Coordinate frame: Y-up, finite floats only. Return ONLY valid Python 3 code with no markdown fences."
)


def make_mod_verify(fn_name: str, mod_name: str, bounds_check: str, required_meshes: list[str] = None) -> list[str]:
    req_meshes = required_meshes or []
    code = f"""
import sys
sys.path.insert(0, 'scripts')
from penthouse_kit.prim_lib import SceneContext
from penthouse_kit.{mod_name} import {fn_name}

ctx = SceneContext('Test')
mats = {{k: ctx.color_mat(k, (0.85, 0.80, 0.72, 1.0)) for k in [
    'oak', 'plaster', 'marble', 'walnut_fluted', 'walnut_solid', 'brass', 'warm_led',
    'glass', 'frosted_glass', 'boucle', 'travertine', 'rug', 'burgundy', 'cream_pillow',
    'tv_art', 'warm_bulb', 'fireplace_glow', 'vinyl_black', 'vinyl_cover', 'chrome',
    'ceramic_white', 'soil', 'bark', 'olive_leaf', 'olive_leaf_bright', 'sky_sunny',
    'gal_1', 'gal_2', 'gal_3', 'gal_4', 'charcoal'
]}}
{fn_name}(ctx, mats)
assert len(ctx.builders) > 0, 'No builders created'
all_pts = []
for b in ctx.builders.values():
    all_pts.extend(b.positions)
assert len(all_pts) > 20, 'Too few vertices'
xs = [p[0] for p in all_pts]; ys = [p[1] for p in all_pts]; zs = [p[2] for p in all_pts]
names = {{b.name for b in ctx.builders.values()}}
for rm in {req_meshes!r}:
    assert rm in names, f'Missing required mesh {{rm}}, got {{names}}'
{bounds_check}
print('MOD_OK', '{mod_name}', len(all_pts), (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
"""
    return ["python3", "-c", code]


CAM_VERIFY = """
node -e "
import('./js/hub3d/duplexCamMath.js').then(m => {
  if (typeof m.computeDuplexCameraPose !== 'function') throw new Error('missing computeDuplexCameraPose');
  if (!m.FLOOR_PRESETS || !m.FLOOR_PRESETS['1f'] || !m.FLOOR_PRESETS['2f']) throw new Error('missing FLOOR_PRESETS');
  const p0 = { x: 3.4, y: 5.4, z: 12.6 };
  const p1 = { x: -0.4, y: 12.8, z: 5.2 };
  const t0 = { x: -0.4, y: 4.0, z: -4.2 };
  const t1 = { x: -9.4, y: 11.0, z: -6.2 };
  const mid = m.computeDuplexCameraPose(p0, p1, t0, t1, 0.5);
  if (!mid || !mid.pos || !mid.target || !Number.isFinite(mid.pos.y)) throw new Error('invalid mid pose');
  if (mid.pos.y < Math.min(p0.y, p1.y)) throw new Error('unexpected dip during ascent');
  const start = m.computeDuplexCameraPose(p0, p1, t0, t1, 0.0);
  const end = m.computeDuplexCameraPose(p0, p1, t0, t1, 1.0);
  if (Math.abs(start.pos.y - p0.y) > 1e-4 || Math.abs(end.pos.y - p1.y) > 1e-4) throw new Error('endpoint mismatch');
  console.log('CAM_MATH_OK');
}).catch(e => { console.error(e); process.exit(1); });
"
"""


TASKS = [
    {
        "name": "mod_salon_seating_3d",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_salon_seating.py",
        "system": COMMON_SYS,
        "prompt": """Write `scripts/penthouse_kit/mod_salon_seating.py` with `build_salon_seating(ctx, mats)` creating 1F luxury living room salon seating:
Required material keys used from `mats`: `rug`, `boucle`, `walnut_solid`, `travertine`, `brass`, `burgundy`, `cream_pillow`.
Strict spatial envelope (`Y floor = 0.00`):
1. Plush Cream Wool Carpet (`ctx.mb("SalonRug", mats["rug"])`): `add_rounded_box(cx=3.2, cy=0.02, cz=-0.2, sx=11.8, sy=0.04, sz=13.2, bevel=0.015, uv_tile=5.0)`.
2. Curved / L-Shaped Italian Cream Boucle Modular Sofa (`X in [-1.8, 5.2], Z in [-6.8, 0.6], Y in [0, 3.0]`):
   - Walnut plinth base (`Y=0.04..0.28`), plump chubby `add_rounded_box` seat cushions (`Y=0.28..1.25`), sculptural curved backrest (`Y=1.25..2.55`), wide rounded armrests, plus burgundy-silk (`mats["burgundy"]`) & cream accent throw pillows tilted gently along the backrest.
   - IMPORTANT: Leave `(X in [-0.5, 4.2], Z in [1.4, 5.8])` completely open & flat on the rug so Bruce stands and runs freely there!
3. Boucle Swivel Lounge Chair (`X=7.2, Z=-6.2`, angled toward the center coffee table) with circular brushed-brass swivel pedestal (`mats["brass"]`) + small travertine drum side table next to it (`X=9.2, Z=-5.4`).
4. Twin Overlapping Sculptural Coffee Tables (`X=4.2, Z=-1.6`):
   - Low oval/rounded Roman travertine table (`mats["travertine"]`, `Y=0.04..0.95`) on three cylindrical fluted walnut legs;
   - Overlapping higher brass-ring & travertine pedestal cocktail table (`X=5.8, Z=-2.4`, `Y=0.04..1.20`) topped with 2 stacked coffee-table art books (`mats["burgundy"]`, `mats["cream_pillow"]`) and a sculptural ceramic vase (`add_lathe` with `mats["cream_pillow"]`).

All geometry MUST stay inside `X in [-3.0, 10.6], Y in [0.0, 3.8], Z in [-7.6, 7.0]`.""",
        "verify_cmd": make_mod_verify(
            "build_salon_seating",
            "mod_salon_seating",
            "assert -3.2 <= min(xs) and max(xs) <= 10.8 and -0.05 <= min(ys) and max(ys) <= 4.0 and -7.8 <= min(zs) and max(zs) <= 7.2, f'Bounds exceeded: {(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs))}'",
        ),
    },
    {
        "name": "mod_media_fireplace_3d",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_media_fireplace.py",
        "system": COMMON_SYS,
        "prompt": """Write `scripts/penthouse_kit/mod_media_fireplace.py` with `build_media_fireplace(ctx, mats)` adorning the 1F Right Marble & Walnut Feature Wall (`X = +14.6`):
Required EXACT mesh names & material keys:
1. `"MediaHearth"` (`mats["travertine"]` + `mats["walnut_fluted"]` + `mats["brass"]`):
   - Sleek floating hearth console spanning `X in [12.3, 14.3], Z in [-6.8, 3.2], Y in [0.38, 1.50]` (champagne-brass recessed plinth + fluted walnut drawer fronts + thick beveled Roman travertine slab top).
   - Glowing linear architectural fireplace firebox (`ctx.mb("FireplaceGlow", mats["fireplace_glow"])`): recessed amber-flame strip at `X=14.18, Y=1.95, Z=-1.8, size=(0.18, 0.36, 4.6)` framed in brushed brass (`mats["brass"]`).
2. **`"GalleryTVScreen"` (`mats["tv_art"]`)** — MUST have exact mesh name `"GalleryTVScreen"`:
   - Positioned in front of the Calacatta marble chimney breast at `X = 14.12`, centered at `Y = 5.15, Z = -1.8`, width `6.4` (along Z: `-5.0 .. +1.4`), height `3.6` (`Y = 3.35 .. 6.95`), framed by an ultra-thin champagne-brass Gallery Picture Frame (`ctx.mb("GalleryTVBezel", mats["brass"])`) at `X = 14.16`.
   - CRITICAL UV + WINDING RULE for `"GalleryTVScreen"`: use `add_quad(p0, p1, p2, p3, uv_scale=(1.0, 1.0))` with EXACT vertices:
     `p0 = (14.10, 3.35, -5.0)`, `p1 = (14.10, 3.35, 1.4)`, `p2 = (14.10, 6.95, 1.4)`, `p3 = (14.10, 6.95, -5.0)`
     (this guarantees normal strictly faces `-X` into the room, `u` runs left-to-right, and `v=0` at bottom -> `v=1` at top so the painting renders right-side up!).
3. Pair of Sculptural Walnut & Brass Hi-Fi Acoustic Towers (`Z = -6.0` and `Z = +2.4`, `X = 13.4, Y = 0.0 .. 3.45`, warm walnut cabinet + brass tweeter ring).
4. **Champagne-Gold Arched Floor Lamp** near the front-right corner (`base at X = 12.6, Z = 4.6, Y = 0.0`):
   - Heavy Roman travertine cylindrical base (`mats["travertine"]`), sweeping brass arch tube via `add_curved_tube` (`mats["brass"]`) arching up to `Y = 6.2` and inward to `(X = 10.6, Y = 5.3, Z = 2.8)`, hanging a warm-brass dome shade (`add_lathe`) and glowing opal bulb **`ctx.mb("ArcLampBulb", mats["warm_bulb"])`** at `(10.6, 4.95, 2.8)`.

Keep all geometry inside `X in [9.5, 14.8], Y in [0.0, 7.6], Z in [-7.2, 5.6]`.""",
        "verify_cmd": make_mod_verify(
            "build_media_fireplace",
            "mod_media_fireplace",
            "assert 9.2 <= min(xs) and max(xs) <= 14.95 and -0.05 <= min(ys) and max(ys) <= 7.8 and -7.4 <= min(zs) and max(zs) <= 5.8",
            required_meshes=["GalleryTVScreen", "ArcLampBulb"],
        ),
    },
    {
        "name": "mod_stair_balustrade_3d",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_stair_balustrade.py",
        "system": COMMON_SYS,
        "prompt": """Write `scripts/penthouse_kit/mod_stair_balustrade.py` with `build_stair_and_balustrade(ctx, mats)` creating:
Required material keys: `oak`, `brass`, `warm_led`, `glass`.
1. **Floating Cantilevered French-Oak & Warm-LED Architectural Staircase**:
   - Rises cleanly from 1F (`Z = 14.2, Y = 0.0`) up toward the 2F Mezzanine landing (`Z = 6.6, Y = 9.20`), centered horizontally along `X = -9.8` (treads spanning `X = -11.4 .. -8.2`, width `3.2`).
   - 14 floating thick chamfered oak treads (`add_rounded_box`, width `3.2`, thickness `0.24`, depth `0.85`, step rise `9.20 / 14`) supported by two recessed dark-brass diagonal stringer beams underneath (`mats["brass"]`), plus a warm LED light strip (`mats["warm_led"]`) tucked beneath the front lip of every tread!
   - Sleek tempered glass side guard panel + angled champagne-brass handrail along `X = -8.15` connecting `Z=14.0, Y=2.4` smoothly up to `Z=6.6, Y=11.45`.
2. **2F Mezzanine Overlook Tempered-Glass & Champagne-Brass Balustrade**:
   - Protects the open mezzanine edge at `Y = 9.20` along:
     - East overlook edge: `X = -3.42, Z in [-15.8, +6.6], Y in [9.20, 11.45]` (thin champagne-brass base shoe + glass panels + continuous brushed-brass top cap rail + minimalist brass slim stanchions every ~3.2 units);
     - South overlook edge (stopping cleanly at the stair arrival): `Z = 6.62, X in [-8.2, -3.42], Y in [9.20, 11.45]`.

Keep all geometry inside `X in [-12.0, -3.1], Y in [0.0, 12.0], Z in [-16.0, 14.8]`.""",
        "verify_cmd": make_mod_verify(
            "build_stair_and_balustrade",
            "mod_stair_balustrade",
            "assert -12.6 <= min(xs) and max(xs) <= -3.0 and -0.05 <= min(ys) and max(ys) <= 12.6 and -16.2 <= min(zs) and max(zs) <= 15.2, f'Bounds: x=({min(xs):.2f},{max(xs):.2f}) y=({min(ys):.2f},{max(ys):.2f}) z=({min(zs):.2f},{max(zs):.2f})'",
        ),
    },
    {
        "name": "mod_loft_2f_3d",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_loft_2f.py",
        "system": COMMON_SYS,
        "prompt": """Write `scripts/penthouse_kit/mod_loft_2f.py` with `build_loft_2f(ctx, mats)` furnishing the 2F Mezzanine Loft (`Y floor top = 9.21`, walkable zone `X in [-14.7, -3.7], Z in [-15.4, 6.0]`):
Required material keys: `rug`, `walnut_solid`, `walnut_fluted`, `brass`, `chrome`, `vinyl_black`, `vinyl_cover`, `boucle`, `travertine`, `burgundy`, `cream_pillow`, `warm_led`, `gal_1`, `gal_2`, `gal_3`, `gal_4`.
1. **2F Plush Loft Rug** (`X=-8.2, Y=9.23, Z=-4.2, sx=6.8, sz=9.4`) — leave `X in [-10.8, -5.0], Z in [-8.5, +1.5]` unobstructed above rug so Bruce walks/rolls cleanly on 2F!
2. **2F Walnut & Brass Hi-Fi Vinyl Credenza + Precision Turntable** (`X = -13.2, Z = -11.4, Y = 9.21`):
   - Low architectural walnut & fluted credenza (`sx=2.2, sy=1.75, sz=5.4`) on slim brass legs;
   - Precision brushed-brass & chrome turntable (`platter`, tonearm, spinning black vinyl LP `mats["vinyl_black"]`), upright showcased vinyl sleeve (`mats["vinyl_cover"]`), and pair of sleek bookshelf monitor speakers flanking it!
3. **Sunlit Boucle Chaise Lounge Daybed + Travertine Drink Pedestal** (`X = -5.8, Z = -11.8, Y = 9.21`, facing the panoramic north curtain window):
   - Rounded bouclé chaise cushion + curved bolster + burgundy silk throw pillow + travertine round drink pedestal at `(-4.4, 9.21, -10.8)`.
4. **`FLY·04` Illuminated Travel Gallery Wall** along the Left 2F Wall (`X = -14.84`, facing `+X` into the loft):
   - 4 large vertical champagne-brass picture frames centered at `Z = -6.8, -4.6, -2.4, -0.2`, `Y = 13.5`, each `1.6` wide (`Z`) by `2.0` tall (`Y`), displaying `gal_1`, `gal_2`, `gal_3`, `gal_4` respectively!
   - IMPORTANT UV + WINDING RULE for `+X`-facing frames on `X = -14.80`: use `add_quad(( -14.80, y0, z+hw ), ( -14.80, y0, z-hw ), ( -14.80, y1, z-hw ), ( -14.80, y1, z+hw ), uv_scale=(1.0, 1.0))` so each painting faces `+X` upright and unmirrored, plus a delicate brass gallery picture bar light above each frame (`mats["brass"]` + `mats["warm_led"]`)!
5. **Bruce's Royal Burgundy-Velvet & Brass Pet Throne** (`X = -12.6, Z = -2.2, Y = 9.21`):
   - Oval/U-shaped burgundy velvet bolster bed (`mats["burgundy"]`), plump ivory center cushion (`mats["cream_pillow"]`), brushed-brass trim ring (`mats["brass"]`).

Keep all geometry inside `X in [-14.95, -3.7], Y in [9.15, 16.4], Z in [-15.4, 5.8]`.""",
        "verify_cmd": make_mod_verify(
            "build_loft_2f",
            "mod_loft_2f",
            "assert -15.05 <= min(xs) and max(xs) <= -3.45 and 9.10 <= min(ys) and max(ys) <= 16.8 and -15.6 <= min(zs) and max(zs) <= 6.2, f'Bounds: x=({min(xs):.2f},{max(xs):.2f}) y=({min(ys):.2f},{max(ys):.2f}) z=({min(zs):.2f},{max(zs):.2f})'",
        ),
    },
    {
        "name": "mod_terrace_sky_3d",
        "model": "deepseek-chat",
        "out_path": "scripts/penthouse_kit/mod_terrace_sky.py",
        "system": COMMON_SYS,
        "prompt": """Write `scripts/penthouse_kit/mod_terrace_sky.py` with `build_terrace_and_sky(ctx, mats)` creating the sunlit sky terrace outside `Z = -16.1` and the curved panoramic sky cyclorama:
Required EXACT mesh name `"SkyCyclorama"` (`mats["sky_sunny"]`, with `mats["sky_sunny"]` created double-sided so inward faces always render).
Material keys: `travertine`, `glass`, `brass`, `ceramic_white`, `soil`, `bark`, `olive_leaf`, `olive_leaf_bright`, `boucle`, `walnut_solid`, `sky_sunny`.
1. **Sunlit Sky Terrace Deck** (`Z in [-24.6, -16.1], X in [-16.2, 16.2], Y top = -0.04`):
   - Honed travertine deck slab (`mats["travertine"]`) + warm walnut deck perimeter edge (`mats["walnut_solid"]`).
   - Low glass & champagne-brass penthouse railing along `Z = -24.4, X in [-16.0, 16.0], Y in [-0.04, 2.35]` + side return rails at `X = -16.0` and `X = +16.0`.
2. **3 Mediterranean Olive / Sculpted Potted Trees in Tapered White Ceramic Planters** (`X = -11.2, +8.8, +12.6`, `Z = -21.2 .. -22.4`, `Y = 0.0`):
   - Tapered ceramic planter (`add_lathe`), dark soil disc, sculpted branching trunk (`add_curved_tube`), dense sunlit layered canopy spheres (`olive_leaf` + `olive_leaf_bright`, heights reaching `Y ~ 5.5 .. 6.8` so 2F & 1F both see sunlit Mediterranean greenery outside the curtain wall!).
3. **2 Resort Sun Loungers & Travertine Pedestal Drink Table** (`X = -5.6` and `-1.8`, `Z = -20.8`, `Y = 0.0`) with sleek walnut frames and cream bouclé cushions.
4. **Curved Panoramic Sky Cyclorama (`ctx.mb("SkyCyclorama", mats["sky_sunny"])`)** — MUST have exact mesh name `"SkyCyclorama"`:
   - Smooth wide cylindrical arc screen wrapping around `-Z` centered at `(0.0, 0.0, -4.0)` with radius `R = 42.0`, height `Y from -10.0 to +34.0`, angle spanning `-145 deg` to `+145 deg` around `-Z` (`x = R * sin(theta), z = -4.0 - R * cos(theta)` for `theta in [-2.53, +2.53]`, subdivided cleanly in 48 azimuth segments).
   - Map UVs cleanly `(u in [0, 1] left-to-right across the arc, v=0 at bottom Y=-10 -> v=1 at top Y=+34)` so the zenith of `sky_sunny.jpg` sits at the top and clouds fill the middle! Wrap winding so inward faces (`-Z -> +Z`) are front-facing CCW!

Keep terrace geometry outside `Z <= -16.0` and cyclorama radius >= 38.""",
        "verify_cmd": make_mod_verify(
            "build_terrace_and_sky",
            "mod_terrace_sky",
            "assert min(zs) <= -30.0 and max(ys) >= 24.0",
            required_meshes=["SkyCyclorama"],
        ),
    },
    {
        "name": "duplex_cam_math_reasoner",
        "model": "deepseek-reasoner",
        "out_path": "js/hub3d/duplexCamMath.js",
        "system": (
            "You are a 3D graphics & camera math specialist. Return ONLY valid ES Module JavaScript code "
            "(no markdown fences, no commentary). Avoid ALL external imports."
        ),
        "prompt": """Write `js/hub3d/duplexCamMath.js`, a pure dependency-free ES module controlling camera presets and smooth vertical elevator camera transitions between 1F (Salon) and 2F (Sunlit Mezzanine Loft) of a double-height penthouse duplex:
Space facts:
- 1F floor height Y = 0.04; 2F mezzanine floor height Y = 9.24 (mezzanine spans X in [-15, -3.4], Z in [-15.8, 6.6], edge glass balustrade at X = -3.42, Z = 6.62).
- Export `FLOOR_PRESETS` object with exact keys `'1f'` and `'2f'`:
  - `'1f'`: `{ id: '1f', label: '1F · 挑空客厅', camPos: [3.4, 5.4, 12.6], target: [-0.4, 4.0, -4.2], floorY: 0.04, brucePos: [1.4, 0.04, 3.8], bruceRot: 0.28, walkBounds: { minX: -1.8, maxX: 6.2, minZ: 1.4, maxZ: 6.2 }, walkSpots: [[1.4, 3.8], [3.6, 4.6], [-0.4, 3.2], [5.0, 2.2]] }`
  - `'2f'`: `{ id: '2f', label: '2F · 阳光阁楼', camPos: [-0.4, 12.8, 5.2], target: [-9.4, 11.0, -6.2], floorY: 9.24, brucePos: [-8.0, 9.24, -4.2], bruceRot: 0.82, walkBounds: { minX: -10.8, maxX: -5.0, minZ: -8.5, maxZ: 1.5 }, walkSpots: [[-8.0, -4.2], [-9.4, -7.2], [-6.2, -1.8], [-9.8, 0.4]] }`
- Export `computeDuplexCameraPose(fromPos, toPos, fromTarget, toTarget, rawProgress)`:
  - Inputs have `{ x, y, z }`. Clamp `t = Math.max(0, Math.min(1, rawProgress))`.
  - Use smooth quintic easing `s = t * t * t * (t * (t * 6 - 15) + 10)`.
  - Compute base lerped `pos` and `target`.
  - When crossing floors (`Math.abs(toPos.y - fromPos.y) > 4.0`), add a smooth parabolic/bell-shaped atrium clearance arc `Math.sin(Math.PI * s)`:
    - slightly boost `pos.x` positively (+1.6 * arc) toward the open double-height atrium (`X > 0`) and gently lift `pos.y` (+0.85 * arc) so the camera glides cleanly around the 2F glass mezzanine edge without clipping!
  - Guarantee at `t === 0` returns exact `(fromPos, fromTarget)` and at `t === 1` returns exact `(toPos, toTarget)`.
  - Return `{ pos: { x, y, z }, target: { x, y, z }, eased: s }`.""",
        "verify_cmd": CAM_VERIFY.strip(),
        "verify_timeout": 45,
    },
]

if __name__ == "__main__":
    os.chdir(REPO_ROOT)
    selected = TASKS
    if "--only" in sys.argv:
        idx = sys.argv.index("--only")
        want = set(sys.argv[idx + 1 :])
        selected = [t for t in TASKS if t["name"] in want]
    run_parallel_codegen(selected, batch_name="penthouse_batch2_3d_modules", max_workers=6, max_retries=3)
