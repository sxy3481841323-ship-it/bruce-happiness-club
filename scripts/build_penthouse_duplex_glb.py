#!/usr/bin/env python3
"""
Assemble PH·01 Sunlit Two-Floor Penthouse Duplex (assets/models/penthouse_duplex.glb)
following the AD100 Quiet-Luxury standard (<= 15 MB, high-bitrate textures):
- 4K 4:1 Malibu cobalt-cerulean sky & round billowing cumulus clouds
- Studio Bronze curtain mullions & unbleached sheer Belgian linen drapery
- Borderless undyed alpaca/wool rug, organic Camaleonda sofa & cognac suede bolsters
- Roman travertine entryway console + walnut suede tray + ELOWEN HOUSE ACCOUNT NO. 07 card
- 7 AD100 collector impasto/silver-gelatin artworks
"""

import os
import sys
import numpy as np
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_GLB = os.path.join(REPO_ROOT, "assets", "models", "penthouse_duplex.glb")

sys.path.insert(0, SCRIPT_DIR)

from penthouse_kit.prim_lib import SceneContext
from penthouse_kit.tex_sunset_and_art import (
    make_sunset_sky_panorama,
    make_monumental_2f_regatta_oil_tex,
)
from penthouse_kit.tex_oldmoney_surfaces import (
    make_marmorino_boiserie_tex,
    make_handknotted_salon_rug_tex,
    make_loft_aubusson_rug_tex,
    make_headland_rock_tex,
)
from penthouse_kit.tex_pbr import (
    make_herringbone_oak_tex,
    make_calacatta_marble_tex,
    make_boucle_fabric_tex,
    make_travertine_tex,
    make_fluted_walnut_tex,
    make_sheer_linen_tex,
    make_cognac_suede_tex,
)
from penthouse_kit.tex_artworks import (
    make_tv_artworks,
    make_vinyl_cover_tex,
    make_patron_card_tex,
)
from penthouse_kit.tex_luxury_props import (
    make_evian_label_tex,
    make_concierge_screen_tex,
    make_foyer_mirror_tex,
    make_foyer_medallion_tex,
    make_fire_ember_tex,
    make_charred_bark_tex,
)
from penthouse_kit.arch_shell import build_arch_shell
from penthouse_kit.mod_salon_seating import build_salon_seating
from penthouse_kit.mod_media_fireplace import build_media_fireplace
from penthouse_kit.mod_stair_balustrade import build_stair_and_balustrade
from penthouse_kit.mod_loft_2f import build_loft_2f
from penthouse_kit.mod_terrace_sky import build_terrace_and_sky
from penthouse_kit.mod_entry_and_niches import build_entry_and_niches


def build_duplex():
    ctx = SceneContext("PenthouseDuplex")

    oak_img = make_herringbone_oak_tex(2048)
    marble_img = make_calacatta_marble_tex(2048)
    smoked_stone_img = Image.fromarray(
        np.clip(np.asarray(marble_img, dtype=np.float32) * np.array([0.27, 0.21, 0.17]), 14, 155).astype(np.uint8),
        "RGB",
    )
    boucle_img = make_boucle_fabric_tex(1024)
    travertine_img = make_travertine_tex(1024)
    walnut_fluted_img = make_fluted_walnut_tex(1024)
    rug_img = make_handknotted_salon_rug_tex(2048)
    rug_2f_img = make_loft_aubusson_rug_tex(1024)
    marmorino_img = make_marmorino_boiserie_tex(1024)
    headland_img = make_headland_rock_tex(512)
    sheer_linen_img = make_sheer_linen_tex(1024)
    cognac_suede_img = make_cognac_suede_tex(1024)
    sky_sunny_img = make_sunset_sky_panorama(4096, 1024)
    sky_sunny_img.convert("RGB").save(
        os.path.join(REPO_ROOT, "assets", "textures", "sky_sunset.jpg"),
        format="JPEG", quality=92, optimize=True,
    )
    tv_arts = make_tv_artworks()
    gal_master_img = make_monumental_2f_regatta_oil_tex(2048, 1024)
    vinyl_cover_img = make_vinyl_cover_tex(1024)
    patron_card_img = make_patron_card_tex(1024, 640)
    evian_label_img = make_evian_label_tex(512, 256)
    concierge_screen_img = make_concierge_screen_tex(512, 320)
    foyer_mirror_img = make_foyer_mirror_tex(1024)
    foyer_medallion_img = make_foyer_medallion_tex(1024)
    fire_ember_img = make_fire_ember_tex(512, 256)
    charred_bark_img = make_charred_bark_tex(512, 256)

    mats = {
        "oak": ctx.tex_mat("HerringboneOak", oak_img, roughness=0.44, metalness=0.04, quality=92),
        "marble": ctx.tex_mat("CalacattaGoldMarble", marble_img, roughness=0.18, metalness=0.04, quality=92),
        "smoked_stone": ctx.tex_mat("SmokedEmperadorStone", smoked_stone_img, roughness=0.22, metalness=0.06, quality=90),
        "evian_flint_glass": ctx.color_mat("EvianFlintGlass", (0.70, 0.90, 0.96, 0.62), roughness=0.05, metalness=0.12, alpha_blend=True, double_sided=True),
        "evian_cap": ctx.color_mat("EvianRoseCap", (0.92, 0.72, 0.76, 1.0), roughness=0.28, metalness=0.15),
        "water_meniscus": ctx.color_mat("AlpineWaterMeniscus", (0.82, 0.95, 1.0, 0.72), roughness=0.06, metalness=0.10, alpha_blend=True),
        "walnut_fluted": ctx.tex_mat("FlutedWalnut", walnut_fluted_img, roughness=0.46, metalness=0.05, quality=90),
        "walnut_solid": ctx.color_mat("SolidWalnut", (0.26, 0.15, 0.09, 1.0), roughness=0.38, metalness=0.05),
        "marmorino": ctx.tex_mat("MarmorinoLimestoneBoiserie", marmorino_img, roughness=0.68, metalness=0.02, quality=90),
        "plaster": ctx.color_mat("VenetianPlaster", (0.88, 0.84, 0.77, 1.0), roughness=0.76, metalness=0.01),
        "brass": ctx.color_mat("BrushedChampagneBrass", (0.82, 0.69, 0.44, 1.0), roughness=0.26, metalness=0.86),
        "bronze_dark": ctx.color_mat("StudioBronze", (0.17, 0.17, 0.15, 1.0), roughness=0.36, metalness=0.70),
        "chrome": ctx.color_mat("BrushedChrome", (0.86, 0.88, 0.91, 1.0), roughness=0.18, metalness=0.92),
        "warm_led": ctx.color_mat("WarmCoveLED", (1.0, 0.91, 0.74, 1.0), roughness=0.2, emissive=(0.95, 0.76, 0.46)),
        "warm_bulb": ctx.color_mat("ArcLampBulbMat", (1.0, 0.93, 0.78, 1.0), roughness=0.22, emissive=(0.82, 0.64, 0.36)),
        "fireplace_glow": ctx.color_mat("FireplaceFlame", (1.0, 0.64, 0.25, 1.0), roughness=0.35, emissive=(0.96, 0.48, 0.14)),
        "glass": ctx.color_mat("ClearTemperedGlass", (0.86, 0.94, 1.0, 0.07), roughness=0.06, metalness=0.10, alpha_blend=True, double_sided=True),
        "frosted_glass": ctx.color_mat("ReededFrostedGlass", (0.92, 0.94, 0.95, 0.42), roughness=0.38, metalness=0.05, alpha_blend=True, double_sided=True),
        "sheer_linen": ctx.tex_mat("SheerBelgianLinen", sheer_linen_img, roughness=0.92, metalness=0.0, quality=88, double_sided=True),
        "boucle": ctx.tex_mat("ItalianBoucle", boucle_img, roughness=0.90, metalness=0.0, quality=88),
        "travertine": ctx.tex_mat("RomanTravertine", travertine_img, roughness=0.38, metalness=0.02, quality=90),
        "rug": ctx.tex_mat("HandKnottedSalonRug", rug_img, roughness=0.90, metalness=0.0, quality=92),
        "rug_2f": ctx.tex_mat("AubussonLoftRug", rug_2f_img, roughness=0.90, metalness=0.0, quality=90),
        "headland_rock": ctx.tex_mat("MediterraneanHeadlandRock", headland_img, roughness=0.88, metalness=0.02, quality=88, double_sided=True),
        "horizon_ocean": ctx.color_mat("SunsetHorizonSea", (0.14, 0.25, 0.36, 1.0), roughness=0.14, metalness=0.22),
        "sail_canvas": ctx.color_mat("ClassicRegattaSail", (0.95, 0.91, 0.84, 1.0), roughness=0.72, metalness=0.02, double_sided=True),
        "burgundy": ctx.color_mat("OxbloodCashmere", (0.36, 0.09, 0.13, 1.0), roughness=0.82, metalness=0.01),
        "cognac_suede": ctx.tex_mat("CognacNubuckSuede", cognac_suede_img, roughness=0.86, metalness=0.0, quality=88),
        "cream_pillow": ctx.color_mat("CreamSilkLinen", (0.94, 0.90, 0.83, 1.0), roughness=0.78, metalness=0.02),
        "charcoal": ctx.color_mat("MatteCharcoal", (0.14, 0.14, 0.16, 1.0), roughness=0.45, metalness=0.20),
        "vinyl_black": ctx.color_mat("VinylRecord", (0.06, 0.06, 0.07, 1.0), roughness=0.16, metalness=0.25),
        "vinyl_cover": ctx.tex_mat("VinylCoverArt", vinyl_cover_img, roughness=0.42, metalness=0.02, quality=90),
        "patron_card": ctx.tex_mat("PatronAccountCard", patron_card_img, roughness=0.55, metalness=0.02, quality=95, double_sided=True),
        "tv_art": ctx.tex_mat("GalleryTVArtMat", tv_arts[0], roughness=0.32, metalness=0.01, quality=95, emissive=(0.10, 0.10, 0.10)),
        "ceramic_white": ctx.color_mat("GlossCeramicWhite", (0.96, 0.94, 0.90, 1.0), roughness=0.24, metalness=0.03),
        "soil": ctx.color_mat("PottingSoil", (0.24, 0.18, 0.14, 1.0), roughness=0.95),
        "bark": ctx.color_mat("OliveBark", (0.42, 0.34, 0.27, 1.0), roughness=0.86),
        "olive_leaf": ctx.color_mat("OliveLeafDeep", (0.26, 0.38, 0.25, 1.0), roughness=0.76),
        "olive_leaf_bright": ctx.color_mat("OliveLeafSunlit", (0.39, 0.50, 0.35, 1.0), roughness=0.72),
        "sky_sunny": ctx.tex_mat("SkyCycloramaSunny", sky_sunny_img, roughness=1.0, metalness=0.0, quality=92, double_sided=True),
        "gal_master": ctx.tex_mat("LoftMonumentalRegatta", gal_master_img, roughness=0.34, quality=92, emissive=(0.08, 0.08, 0.08)),
        "evian_label": ctx.tex_mat("EvianAlpineLabel", evian_label_img, roughness=0.32, metalness=0.02, quality=94),
        "concierge_screen": ctx.tex_mat("ConciergeOLED", concierge_screen_img, roughness=0.22, metalness=0.05, quality=94, emissive=(0.75, 0.72, 0.65)),
        "foyer_mirror": ctx.tex_mat("FoyerSmokedMirror", foyer_mirror_img, roughness=0.06, metalness=0.88, quality=94, emissive=(0.12, 0.11, 0.09)),
        "foyer_medallion": ctx.tex_mat("FoyerStoneMedallion", foyer_medallion_img, roughness=0.18, metalness=0.06, quality=92),
        "fire_ember": ctx.tex_mat("FireEmberBed", fire_ember_img, roughness=0.45, metalness=0.0, quality=92, emissive=(0.95, 0.42, 0.10)),
        "charred_bark": ctx.tex_mat("CharredOakBark", charred_bark_img, roughness=0.82, metalness=0.0, quality=90, emissive=(0.24, 0.06, 0.01)),
        "glass_smoke": ctx.color_mat("SmokedBorosilicateGlass", (0.14, 0.15, 0.17, 0.34), roughness=0.06, metalness=0.15, alpha_blend=True, double_sided=True),
        "crystal_glass": ctx.color_mat("ClearCrystalGlass", (0.74, 0.89, 0.96, 0.44), roughness=0.05, metalness=0.12, alpha_blend=True, double_sided=True),
        "orchid_white": ctx.color_mat("PhalaenopsisOrchid", (0.98, 0.97, 0.95, 1.0), roughness=0.45, metalness=0.02),
    }

    build_arch_shell(ctx, mats)
    build_salon_seating(ctx, mats)
    build_media_fireplace(ctx, mats)
    build_stair_and_balustrade(ctx, mats)
    build_loft_2f(ctx, mats)
    build_terrace_and_sky(ctx, mats)
    build_entry_and_niches(ctx, mats)

    info = ctx.export_glb(OUT_GLB)
    for req in (
        "SkyCyclorama", "GalleryTVScreen", "ArcLampBulb", "EntryPatronCard",
        "FireplaceEmbers", "FireplaceLogs", "HiFiGlassDome",
        "ConciergePager1F", "ConciergePager2F", "EvianBottles1F",
        "TerraceSofaSeat", "OceanVistaWater",
    ):
        assert req in info["mesh_names"], f"Missing required mesh {req}"
    assert info["size_mb"] <= 15.0, f"GLB exceeds 15 MB cap: {info['size_mb']} MB"
    print(
        f"Built penthouse_duplex.glb: {info['size_mb']:.2f} MB, "
        f"{info['tris']:,} tris, {info['meshes']} meshes, "
        f"{info['materials']} mats, {info['textures']} texs"
    )
    return info


if __name__ == "__main__":
    build_duplex()
