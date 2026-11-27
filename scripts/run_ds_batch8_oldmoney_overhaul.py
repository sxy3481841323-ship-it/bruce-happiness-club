#!/usr/bin/env python3
"""
Batch 8 (Overnight Autonomous Sprint):
Parallel DeepSeek orchestration for:
1. Old-Money limewash boiserie, inlaid parquet & museum-grade bordered silk-wool rugs
2. Golden-hour sunset sky dome & monumental 2F coastal regatta oil masterwork
3. Penthouse 3D architecture cladding (zero white walls), equal-height tables,
   sculptural floor lamp, Beovision TV, single 2F masterwork, widened sunset ocean
   balcony + plush Loro-Piana style sofa + AAA 3D layered coastal headland vista.
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from ds_worker import run_parallel_codegen


PRIM_SIG = """
EXACT prim_lib.py SceneContext / MeshBuilder methods (DO NOT invent extra args!):
- b = ctx.mb(mesh_name: str, mat_idx: int)
- b.add_tri_raw(p0, p1, p2, uv0=(0,0), uv1=(1,0), uv2=(1,1), n0=None, n1=None, n2=None)
- b.add_quad(p0, p1, p2, p3, uv_scale=(1.0, 1.0), flip=False)  # p0->p1->p2->p3 CCW from front (+normal)
- b.add_box(cx, cy, cz, sx, sy, sz, uv_tile=0.0, rot_y=0.0)
- b.add_rounded_box(cx, cy, cz, sx, sy, sz, bevel=0.06, uv_tile=0.0, rot_y=0.0)
- b.add_cylinder(cx, y0, cz, r_bot, r_top, height, segs=18, rot_x=0.0, rot_z=0.0, cap_top=True, cap_bot=True)
- b.add_sphere(cx, cy, cz, rx, ry=None, rz=None, rings=12, segs=18)
- b.add_lathe(cx, y0, cz, profile, segs=22)  # profile = [(r, dy), ...]
- b.add_curved_tube(spine_pts, radii, segs=10)
Available keys in mats dict:
  oak, marmorino, travertine_wall, marble, walnut_fluted, walnut_solid, plaster,
  brass, bronze_dark, chrome, warm_led, warm_bulb, fireplace_glow, glass, frosted_glass,
  sheer_linen, boucle, travertine, rug, rug_2f, burgundy, cognac_suede, cream_pillow,
  charcoal, vinyl_black, vinyl_cover, patron_card, tv_art, ceramic_white, soil, bark,
  olive_leaf, olive_leaf_bright, sky_sunny, gal_master, evian_label, concierge_screen,
  foyer_mirror, foyer_medallion, fire_ember, charred_bark, glass_smoke, crystal_glass,
  orchid_white, headland_rock, horizon_ocean, sail_canvas
"""


def main():
    tasks = [
        {
            "name": "tex_oldmoney_surfaces",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/tex_oldmoney_surfaces.py",
            "system": (
                "You are a senior Three.js procedural material artist specializing in Old-Money AD100 interiors "
                "(Axel Vervoordt, Maxime d'Angeac, Loro Piana). Keep code under 235 lines, fast vectorized NumPy + PIL only."
            ),
            "prompt": """Create `scripts/penthouse_kit/tex_oldmoney_surfaces.py` exporting 4 functions returning RGB `PIL.Image.Image`:
1. `make_marmorino_boiserie_tex(size: int = 1024) -> Image.Image`:
   - Rich warm hand-troweled French Marmorino limewash & limestone (`#DDD2C0` to `#CBBAA2`, NEVER white `#FFFFFF`!),
   - Subtle mineral clouding + vertical trowel polish bands + recessed classical boiserie panel hairline grooves (`#B09E84` & subtle `#C7AD7B` champagne highlight) so tall walls have unmistakable bespoke depth & texture.
2. `make_handknotted_salon_rug_tex(size: int = 2048) -> Image.Image`:
   - Museum-grade hand-knotted Tibetan wool & raw silk salon carpet (`#E4DBCA` oatmeal-ivory field with organic horizontal silk abrash striations and fine knot grain),
   - Surrounded by a tailored **double architectural woven border** spanning outer `9%` of edges: dark taupe-umber outer band (`#6A5D4D`), antique-brass inner geometric fretwork (`#B49762`), and a whisper-thin `#652C39` oxblood inner selvedge pinstripe with restrained corner medallions!
3. `make_loft_aubusson_rug_tex(size: int = 1024) -> Image.Image`:
   - Complementary 2F hand-loomed wool-and-silk carpet in warm biscuit-sand (`#DED3BE`) with muted bronze-olive (`#76725B`) & umber double frame border and subtle woven pile relief.
4. `make_headland_rock_tex(size: int = 512) -> Image.Image`:
   - Warm Mediterranean coastal limestone cliff strata in sunset amber-slate tones (`#695C52`, `#4D4540`, `#8B7562`) for parallax coastal bluffs.
Return ONLY valid Python code (target ~190-230 lines, no markdown).""",
            "verify_cmd": (
                "python3 -c \"import numpy as np; from scripts.penthouse_kit.tex_oldmoney_surfaces import "
                "make_marmorino_boiserie_tex, make_handknotted_salon_rug_tex, make_loft_aubusson_rug_tex, make_headland_rock_tex; "
                "imgs=[make_marmorino_boiserie_tex(512), make_handknotted_salon_rug_tex(512), make_loft_aubusson_rug_tex(512), make_headland_rock_tex(256)]; "
                "assert all(im.mode=='RGB' and np.std(np.asarray(im))>5.0 for im in imgs); print('OK surfaces')\""
            ),
        },
        {
            "name": "tex_sunset_and_art",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/tex_sunset_and_art.py",
            "system": (
                "You are a 2D matte-painting & oil-masterwork procedural artist for 3D coastal luxury scenes. "
                "Keep code concise (< 220 lines), vectorized NumPy + PIL."
            ),
            "prompt": """Create `scripts/penthouse_kit/tex_sunset_and_art.py` exporting 2 functions returning RGB `PIL.Image.Image`:
1. `make_sunset_sky_panorama(w: int = 4096, h: int = 1024) -> Image.Image`:
   - Panoramic 3D sky dome texture centered on horizon `v = 0.56`:
     - Sky top `v=0.0..0.38`: deep Mediterranean sapphire twilight (`#314D77`) -> warm cobalt-mauve (`#586E95`) -> rose-amber mid sky (`#CE866E`) -> glowing golden apricot horizon (`#F5BC7E`),
     - Soft radiant golden sun orb & halo around `(u=0.52, v=0.45)`,
     - Billowing golden-rimmed sunset cumulus clouds glowing coral-peach underneath and champagne-cream on sunlit crests,
     - Below horizon `v=0.56..1.0`: deep twilight-sapphire sea gradient (`#26486B` -> `#1A3552`) with a shimmering amber-gold sunset reflection track beneath `u=0.52`.
2. `make_monumental_2f_regatta_oil_tex(w: int = 2048, h: int = 1024) -> Image.Image`:
   - ONE museum-grade 19th-century oil-on-Belgian-linen panoramic coastal regatta masterwork for the 2F loft wall:
     - Warm linen canvas weave + oil impasto brushwork (using Sobel raking highlight),
     - Atmospheric Turner-inspired golden sunset & slate-indigo sky meeting Prussian-teal sea, rocky Mediterranean headland silhouette on the left, and 3 classic J-Class sloop hulls with tall ivory-cream gaff sails catching warm light,
     - Framed with an off-white linen passe-partout mat & thin antique-gold bevel (`#A68952`) around a crisp museum edge.
Return ONLY valid Python code (< 220 lines).""",
            "verify_cmd": (
                "python3 -c \"import numpy as np; from scripts.penthouse_kit.tex_sunset_and_art import "
                "make_sunset_sky_panorama, make_monumental_2f_regatta_oil_tex; "
                "s=make_sunset_sky_panorama(1024,256); a=make_monumental_2f_regatta_oil_tex(1024,512); "
                "assert s.size==(1024,256) and a.size==(1024,512) and np.std(np.asarray(s))>12 and np.std(np.asarray(a))>12; print('OK sunset+art')\""
            ),
        },
        {
            "name": "arch_shell",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/arch_shell.py",
            "system": (
                "You are a Classical Interior Architect & Three.js Technical Artist. Enforce ZERO blank white walls: "
                "every visible wall surface must have textured limestone/Marmorino boiserie mouldings, fluted walnut pilasters, "
                "warm brass shadow-gap inlays, and curated backlit shelving so 360-degree camera orbit looks rich from every angle. "
                "Stay strictly under 240 lines."
            ),
            "prompt": f"""Rewrite `scripts/penthouse_kit/arch_shell.py` defining `build_arch_shell(ctx, mats: dict)`.
{PRIM_SIG}
Exact architectural & coordinate requirements:
1. **1F Main Floor Slab + Inlaid Walnut Border**:
   - `FloorOak` (`mats["oak"]`) spanning `X in [-15.2, 15.2], Z in [-16.2, 15.8], top Y = 0.00`.
   - `FloorBorderInlay` (`mats["walnut_solid"]` + `mats["brass"]` hairline) framing the perimeter at `X = ±13.6` and `Z = -14.6, +14.2` at `Y = 0.004`.
2. **Ceiling & Atrium Chandelier (`mats["marmorino"]`)**:
   - Double-height ceiling `Y = 18.60`, perimeter cove soffit + `WarmCoveLED`, and keep the iconic two-ring Brass & Opal-Globe Atrium Chandelier at `(2.6, 18.1..13.65, -2.8)`.
3. **ALL 4 WALLS CLAD IN OLD-MONEY BOISERIE (ZERO PLAIN WHITE WALLS!)**:
   - Base walls use `mats["marmorino"]` (`uv_tile=4.5`) instead of plain `plaster`!
   - **Right Wall (`X = +15.0`)**: central Calacatta marble chimney breast (`Z in [-6.8, +3.2]`), flanked by fluted walnut panels + brass reveal trims + recessed limestone boiserie moulding panels.
   - **Left Entrance Wall (`X = -15.0`)**:
     - Keep `PH·01` double walnut entrance doors at `Z = +2.2` (`Y = 0..7.4`, `brass` architrave + twin bar pulls) and Kitchen glass portal at `Z = -8.8`.
     - Cover ALL remaining left-wall expanses (`Z in [-15.5..-11.0]`, `Z in [-6.5..-0.5]`, `Z in [+4.8..+15.4]`, and **2F upper left wall `Y in [9.4..18.2]`**) with **raised Marmorino boiserie frames (`b_boiserie`), fluted walnut pilasters (`b_walnut`), brass picture-rail/dado strips, and backlit walnut library/display recesses (`Z = -3.8`, `Z = +10.5`)** so BOTH sides of the entrance door look unmistakably architectural & warm!
   - **South / Back Wall (`Z = +15.8`, seen prominently during 360° orbit!)**:
     - Full sculptural 1F+2F wall composition (`marmorino` wall + 6 tall framed limestone boiserie bays across `X = -13..+13`, 5 fluted walnut pilasters between bays, dado rail at `Y = 1.35`, brass frieze strip at `Y = 8.9`, and centered illuminated walnut gallery bookcase credenza at `X = 0..6.8, Z = 15.1` with brass trim and hardcover art monographs!).
   - Keep **2F Mezzanine Slab (`X in [-15.0, -3.4], Z in [-15.8, +6.6], top Y = 9.20`)** and **2F Master Suite Door (`X = -14.86, Z = +3.6`)**.
4. **Panoramic Curtain Wall (`Z = -16.0`) WITH OPEN WALKABLE TERRACE PORTAL**:
   - Slim Studio Bronze mullions at `X = (-14.82, -9.6, -3.5, +4.4, +9.4, +14.82)` and horizon transom `Y = 9.18`.
   - **Leave `X in [-1.4, +4.2], Y in [0.02, 7.6]` COMPLETELY OPEN (no glass slab across this opening!)** by placing `ClearCurtainGlass` panes on the left (`X in [-14.8, -1.4]`), right (`X in [+4.2, +14.8]`), and 2F upper (`Y in [7.7, 18.2]`) plus parked stacked open sliding door frames at `X = -2.2` and `X = +4.6`! Floor brass threshold flush at `Y = 0.015`.
   - Keep sheer Belgian linen drapery panels gathered cleanly at `X = -14.1, -3.85, +14.05`.
Return ONLY valid Python code (target ~200-235 lines).""",
            "verify_cmd": (
                "python3 -c \"import ast; ast.parse(open('scripts/penthouse_kit/arch_shell.py').read()); print('OK arch_shell AST')\""
            ),
        },
        {
            "name": "mod_salon_seating",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_salon_seating.py",
            "system": (
                "You are an expert Three.js bespoke furniture modeler. Keep code clean (< 235 lines), "
                "all +Y top faces upward, exact equal height Y=0.760 on both staggered salon coffee tables, "
                "and preserve every required mesh name cleanly."
            ),
            "prompt": f"""Rewrite `scripts/penthouse_kit/mod_salon_seating.py` defining `build_salon_seating(ctx, mats)`.
{PRIM_SIG}
Keep & refine all existing geometry & mesh names (`SofaPlinth`, `SofaSeat`, `SofaBack`, `SalonRug`, `SofaPillows`, `JeanneretLoungeChair`, `SalonDrumTable`, `SalonTableMarbleTop`, `SalonCocktailTop`, `EvianBottles1F`, `ConciergePager1F`, `ConciergeScreen1F`), fixing TWO crucial spatial flaws:
1. **Museum Bordered Rug (`SalonRug`)**:
   - Single sculpted carpet slab `X = 2.6, Z = -0.3`, size `12.6 × 13.6 m`, `top Y = 0.04` (`mats["rug"]` with **`uv_tile=0.0`** so its double architectural woven border frames the entire seating group cleanly without tiling!). Add subtle silk fringe strips (`mats["cream_pillow"]`) at `Z = -7.12` and `Z = +6.52`.
2. **Staggered / Non-Aligned Twin Coffee Tables — CLOSER TO LEFT SOFA & EXACT EQUAL HEIGHT (`top Y = 0.760 m`)**:
   - Notice the sofa chaise on the left sits at `X = -1.0` (`inner edge X = -0.27`), and main sofa seats sit at `Z = -3.7` (`front edge Z = -2.92`).
   - **Table A (`SalonTableMarbleTop`, organic rounded Travertine & Calacatta oval/rectangle slab `2.45 × 1.32 m`)**:
     - Centered at **`tx = 1.15, tz = -2.05`** (only ~0.35 m reach from the left chaise AND ~0.20 m from the main sofa!).
     - Fluted Roman travertine twin drum pedestals (`px = 0.35, 1.95`, `Y = 0.04..0.68`) + brass collars + marble top centered at `Y = 0.72` with height `0.08` -> **exact top surface `Y = 0.760`**!
   - **Table B (`SalonCocktailTop`, staggered non-aligned smoked-walnut & marble companion table `1.36 × 1.36 m`, `rot_y = 0.14`)**:
     - Centered at **`cx2 = 3.10, cz2 = -1.18`** (staggered diagonally, preserving the cool non-aligned two-table rhythm!).
     - Fluted `bronze_dark` & brass pedestal (`Y = 0.04..0.68`) + marble top centered at `Y = 0.72` with height `0.08` -> **EXACT SAME top surface `Y = 0.760`**!
3. **Props Seated Flush on `Y = 0.760` Tabletops**:
   - On Table A (`Y = 0.760`): silk-linen monographs at `(0.35, 0.76, -2.15)`, carved stoneware bowl at `(1.92, 0.76, -2.25)`, and brushed-chrome chilled tray `SalonChilledTray` at `(1.10, 0.775, -1.92)` holding **3 glass Evian bottles (`EvianBottles1F` + `EvianLabels1F`) + 2 crystal tumblers**.
   - On Table B (`Y = 0.760`): **`ConciergePager1F` + `ConciergeScreen1F`** centered at `(3.10, 0.76, -1.18)` tilted cleanly toward `+Z/+Y` (ensure `add_tri_raw` face normal points `+Y/+Z` toward camera!).
Return ONLY valid Python code (< 235 lines).""",
            "verify_cmd": (
                "python3 -c \"import ast; ast.parse(open('scripts/penthouse_kit/mod_salon_seating.py').read()); print('OK mod_salon_seating AST')\""
            ),
        },
        {
            "name": "mod_media_fireplace",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_media_fireplace.py",
            "system": (
                "You are a luxury furniture & consumer industrial designer channeling Bang & Olufsen and Maxime d'Angeac. "
                "Replace flimsy wireframe furniture with grounded sculptural mass. Keep code < 235 lines."
            ),
            "prompt": f"""Rewrite `scripts/penthouse_kit/mod_media_fireplace.py` defining `build_media_fireplace(ctx, mats)`.
{PRIM_SIG}
Keep exact existing fireplace (`X=12.3..14.3, Z=-6.8..3.2`) + `FireplaceEmbers` + `FireplaceLogs` + `HiFiTower`/`HiFiGlassDome`/`HiFiHaloRing` (`tower_x=13.05, tower_z=[-7.35, 3.75]`), AND make TWO decisive visual upgrades:
1. **Architectural Beovision-Inspired Display (`GalleryTVScreen` & Surround)**:
   - On the Calacatta marble chimney breast at `X = 14.08`, build a crisp 16:9 screen quad `GalleryTVScreen` (`Y = 3.45..6.93, Z = -4.90..1.30`, facing `-X` with `(0,0)->(1,1)` UVs: `p0=(14.08,3.45,-4.90), p1=(14.08,3.45,1.30), p2=(14.08,6.93,1.30), p3=(14.08,6.93,-4.90)`).
   - Frame `GalleryTVBezel` with a recessed dark anodized bronze outer chassis (`mats["bronze_dark"]`) + delicate brushed champagne-brass inner fillet (`mats["brass"]`), AND add a **sculptural Beovision oak-and-brass acoustic louver soundbar wing** (`24` fine vertical oak/walnut slats `mats["walnut_solid"]` + brass spine) directly below the screen at `Y = 2.86..3.34, Z = -4.60..1.00`!
2. **Substantial Old-Money Sculptural Floor Lamp Beside the Right Harman Speaker**:
   - Place the lamp firmly at `(bx=12.25, bz=5.20)` beside the `(13.05, 3.75)` Harman speaker tower:
     - **Stepped Heavy Plinth (`ArcLampBase`)**: wide solid Roman travertine cylinder/block (`r=0.34, h=0.22`) topped with a chamfered `bronze_dark` & `brass` stepped collar (`Y = 0.0..0.38`) — visually rock-solid!
     - **Fluted Walnut & Aged-Brass Column (`ArcLampArch`)**: substantial solid upright shaft (`r = 0.055`, walnut sleeve + brass rings) rising straight from `Y = 0.38` to `Y = 3.55`, then a crisp machined brass cantilever arm extending forward to `(11.75, 4.05, 4.70)` with a counterweight brass sphere at `(12.50, 3.90, 5.45)`!
     - **Pleated Belgian-Linen / Alabaster Drum Shade (`ArcLampShade`)**: generous tailored linen drum (`mats["cream_pillow"]`, `r_bot=0.46, r_top=0.40, h=0.48`, open bottom so light spills down) centered at `(11.75, 3.56, 4.70)` with spun-brass top/bottom trim rings!
     - **`ArcLampBulb`** (`mats["warm_bulb"]`) nestled inside shade at `(11.75, 3.68, 4.70)` (`radius=0.11`).
Return ONLY valid Python code (< 235 lines).""",
            "verify_cmd": (
                "python3 -c \"import ast; ast.parse(open('scripts/penthouse_kit/mod_media_fireplace.py').read()); print('OK mod_media AST')\""
            ),
        },
        {
            "name": "mod_loft_2f",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_loft_2f.py",
            "system": (
                "You are a museum-grade Old-Money residential architect. Keep code < 235 lines, preserve all 2F interactive meshes "
                "(`LoftTurntableVinyl`, `LoftAuraSpeaker`, `LoftAuraHalo`, `ConciergePager2F`, `ConciergeScreen2F`, `EvianBottles2F`), "
                "and replace cluttered 4-frame grids with ONE serene monumental collector oil painting."
            ),
            "prompt": f"""Rewrite `scripts/penthouse_kit/mod_loft_2f.py` defining `build_loft_2f(ctx, mats)`.
{PRIM_SIG}
Exact requirements (`y0 = 9.21`):
1. **Bordered 2F Aubusson-Inspired Carpet (`loft_rug`)**:
   - `mats["rug_2f"]` centered at `(-8.2, y0 + 0.02, -4.2)`, size `6.8 × 6.2 m`, **`uv_tile=0.0`** so its woven double border shows cleanly!
2. **REPLACE the 4 cluttered frames (`gal_1..4`) with ONE MONUMENTAL MUSEUM MASTERWORK**:
   - Centered on the 2F left feature wall at `wall_x = -14.76, cy = 13.35, gz = -3.4`:
   - Dimensions: width `4.20 m` (`gz - 2.10` to `gz + 2.10`), height `2.10 m` (`cy - 1.05` to `cy + 1.05`).
   - Quad `LoftMasterworkCanvas` using `mats["gal_master"]` facing `+X` into the loft (`p0=(wall_x, y0f, gz+2.10), p1=(wall_x, y0f, gz-2.10), p2=(wall_x, y1f, gz-2.10), p3=(wall_x, y1f, gz+2.10)`).
   - Deep carved solid walnut outer shadow-box frame (`mats["walnut_solid"]`) + chamfered antique brass inner slip (`mats["brass"]`) + a sleek `2.1 m` brushed-brass museum picture light (`y = 14.58`) with hidden warm LED bar!
   - Flank the masterwork on `Z = -7.0` and `Z = +0.2` with matching tall walnut-and-Marmorino boiserie pilasters + warm brass sconces so the 2F wall looks calm, curated, and unmistakably Old Money!
3. Keep all 2F loft furniture & interactive props intact (`loft_daybed_*` at `(-5.8,-11.8)`, `loft_pet_throne_*` at `(-12.6,-2.2)`, Vinyl Hi-Fi Credenza + `LoftTurntableVinyl` + `LoftAuraSpeaker` + `LoftAuraHalo` at `(-13.1,-11.4)`, Executive Desk + `EvianBottles2F` + `ConciergePager2F` + `ConciergeScreen2F` at `(-5.8, 3.30)`).
Return ONLY valid Python code (< 235 lines).""",
            "verify_cmd": (
                "python3 -c \"import ast; ast.parse(open('scripts/penthouse_kit/mod_loft_2f.py').read()); print('OK mod_loft AST')\""
            ),
        },
        {
            "name": "mod_terrace_sky",
            "model": "deepseek-chat",
            "out_path": "scripts/penthouse_kit/mod_terrace_sky.py",
            "system": (
                "You are a Principal Environment Artist at Naughty Dog / Rockstar solving interior-to-exterior vistas in 3D games. "
                "Build a wide cliffside sunset balcony with plush bouclé lounge seating, 3D layered coastal headlands for real parallax, "
                "classic horizon sailboats, ocean surface (`OceanVistaWater`), and wide panoramic `SkyCyclorama`. Keep < 235 lines."
            ),
            "prompt": f"""Rewrite `scripts/penthouse_kit/mod_terrace_sky.py` defining `build_terrace_and_sky(ctx, mats)`.
{PRIM_SIG}
Exact spatial requirements:
1. **Widened Cliffside Sunset Balcony (`TerraceDeck`)**:
   - Teak-and-travertine deck spanning `X in [-16.2, 16.2], Z in [-29.6, -16.0], top Y = 0.00` (`depth 13.6 m`, `width 32.4 m`, `uv_tile=2.2`) + travertine coping edge around outer perimeter!
   - Ultra-clear frameless glass balustrade (`Z = -29.42`, height `1.06 m` so ocean horizon is totally unobstructed when Bruce sits on the sofa!) with slim `bronze_dark` & `brass` top handrail (`Y = 1.08`) and slim posts along `Z = -29.42` and side edges `X = ±16.05`.
2. **Plush Old-Money Sunset Sofa (`TerraceSofaSeat`) Facing Out Toward the Sunset Sea (`-Z`)**:
   - Outdoor woven rug (`TerraceOutdoorRug`, `mats["rug_2f"]`, `uv_tile=0.0`) at `(1.4, 0.015, -22.6)`, `5.8 × 4.6 m`.
   - Deep teak plinth (`mats["walnut_solid"]`) + **luxurious plush Loro-Piana oatmeal bouclé sofa (`TerraceSofaSeat`, `mats["boucle"]`)** at `X = 1.4, Z = -22.4` (`width 4.0 m, depth 1.55 m`):
     - Plump bevelled seat cushions centered at `Z = -22.45, Y = 0.36, height = 0.36` -> **cushion top `Y = 0.54`**!
     - Backrest cushion on the **`+Z` side (`Z = -21.58`, height `0.78`)** and curved wing armrests at `X = -0.58` and `X = +3.38`, so the open front faces **`-Z` straight toward the sunset ocean & horizon**!
     - Scatter cognac suede & burgundy piped bolster pillows (`mats["cognac_suede"]`, `mats["burgundy"]`) cleanly against the `+Z` backrest.
   - Low travertine sunset coffee table (`TerraceLowTable`) in front of sofa at `(1.4, 0.0, -24.35)` (`top Y = 0.42`), plus 2 warm brass hurricane lanterns (`mats["brass"]` + glowing `mats["warm_bulb"]`) at `(-1.25, -22.3)` and `(4.05, -22.3)`.
   - Sculpted olive trees in travertine/ceramic planters tucked at outer wings `(-12.2, -23.5)` and `(+12.4, -24.2)` so the central `-Z` ocean vista stays sweeping and clear!
3. **AAA 3-Layer 3D Exterior Vista**:
   - **Layer 1 — Cliffside Drop-off & Olive Terraces (`CoastalCliff`, `mats["headland_rock"]`)**: rugged faceted rocky cliff edge directly below the balcony (`Z in [-46, -29.8], Y in [-8.8, -0.5]`).
   - **Layer 2 — Mid-ground Layered 3D Coastal Headlands (`CoastalHeadlands`, `mats["headland_rock"]`)**: stepped 3D peninsula ridge silhouettes on left (`X=-75..-18, Z=-88, top Y=16`) and far right (`X=+24..+92, Z=-116, top Y=19`) creating real parallax during 360° orbit!
   - **Layer 3 — Expansive 3D Ocean Surface (`OceanVistaWater`, `mats["horizon_ocean"]`)**: single large flat subdivided quad grid (`X in [-180, 180], Z in [-28, -155], Y = -8.5`, upward `+Y` normal!) + **2 Distant Classic White-Sailed Yachts (`HorizonSailboats`, `mats["sail_canvas"]` & `mats["bronze_dark"]`)** at `(-14, -8.4, -74)` and `(22, -8.4, -102)`.
   - **4K Sunset `SkyCyclorama`** (`mats["sky_sunny"]`): curved cylinder wrap `R = 148.0, cz = -4.0, theta_min = -2.65, theta_max = 2.65, y_bot = -26.0, y_top = 76.0, segs = 56` (inward CCW normals facing center).
Return ONLY valid Python code (< 235 lines).""",
            "verify_cmd": (
                "python3 -c \"import ast; ast.parse(open('scripts/penthouse_kit/mod_terrace_sky.py').read()); print('OK mod_terrace AST')\""
            ),
        },
    ]
    results = run_parallel_codegen(tasks, batch_name="batch8_oldmoney_overhaul", max_workers=6, max_retries=3)
    print(f"Batch 8 complete: {len(results)} modules verified.")


if __name__ == "__main__":
    main()
