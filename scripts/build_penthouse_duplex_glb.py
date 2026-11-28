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
    make_verde_alpi_marble_tex,
    make_rift_oak_tex,
    make_celadon_plaster_tex,
    make_slate_linen_tex,
    make_headland_rock_tex,
    make_coastal_pine_slope_tex,
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
from penthouse_kit.tex_kitchen_surfaces import (
    make_pietra_grey_marble_tex,
    make_tundra_grey_floor_tex,
    make_platinum_slate_tex,
    make_alpine_granite_cliff_tex,
    make_smart_panel_tex,
    make_organic_dairy_label_tex,
    make_prestige_wine_labels_tex,
    make_aaa_snow_granite_mountain_tex,
    make_sheet_music_tex,
    make_glass_curtain_skyscraper_tex,
    make_himalayan_salt_tex,
)
from penthouse_kit.mod_south_kitchen import build_south_kitchen
from penthouse_kit.mod_south_terrace_mountains import build_south_terrace_and_mountains
from penthouse_kit.mod_east_piano_sport_wing import build_east_piano_sport_wing
from penthouse_kit.mod_east_river_bridge_vista import build_east_river_bridge_vista


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
    verde_alpi_img = make_verde_alpi_marble_tex(1024)
    rift_oak_img = make_rift_oak_tex(1024)
    celadon_img = make_celadon_plaster_tex(1024)
    slate_linen_img = make_slate_linen_tex(512)
    marmorino_img = make_marmorino_boiserie_tex(1024)
    headland_img = make_headland_rock_tex(512)
    coastal_pine_img = make_coastal_pine_slope_tex(1024)
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
    pietra_grey_img = make_pietra_grey_marble_tex(1024)
    tundra_grey_img = make_tundra_grey_floor_tex(1024)
    graphite_slate_img = make_platinum_slate_tex(512)
    alpine_granite_img = make_alpine_granite_cliff_tex(1024)
    smart_panel_img = make_smart_panel_tex(1024, 680)
    smart_panel_img.convert("RGB").save(
        os.path.join(REPO_ROOT, "assets", "textures", "smart_panel.jpg"),
        format="JPEG", quality=93, optimize=True,
    )
    dairy_label_img = make_organic_dairy_label_tex(512)
    prestige_wine_img = make_prestige_wine_labels_tex(1024, 512)
    aaa_mountain_img = make_aaa_snow_granite_mountain_tex(2048, 1024)
    sheet_music_img = make_sheet_music_tex(512, 384)
    city_facade_img = make_glass_curtain_skyscraper_tex(512, 512)
    himalayan_salt_img = make_himalayan_salt_tex(256, 256)

    mats = {
        "oak": ctx.tex_mat("HerringboneOak", oak_img, roughness=0.44, metalness=0.04, quality=92),
        "marble": ctx.tex_mat("CalacattaGoldMarble", marble_img, roughness=0.18, metalness=0.04, quality=92),
        "verde_alpi": ctx.tex_mat("VerdeAlpiMarble", verde_alpi_img, roughness=0.22, metalness=0.04, quality=92),
        "rift_oak": ctx.tex_mat("SmokedRiftOak", rift_oak_img, roughness=0.46, metalness=0.04, quality=90),
        "celadon_plaster": ctx.tex_mat("CeladonMineralPlaster", celadon_img, roughness=0.72, metalness=0.01, quality=90),
        "slate_linen": ctx.tex_mat("SlateMistLinen", slate_linen_img, roughness=0.88, metalness=0.0, quality=90),
        "smoked_stone": ctx.tex_mat("SmokedEmperadorStone", smoked_stone_img, roughness=0.22, metalness=0.06, quality=90),
        "table_espresso": ctx.color_mat("DarkEspressoMahogany", (0.14, 0.08, 0.05, 1.0), roughness=0.26, metalness=0.04),
        "tray_burgundy": ctx.color_mat("OxbloodTrayLeather", (0.28, 0.06, 0.09, 1.0), roughness=0.58, metalness=0.02),
        "evian_flint_glass": ctx.color_mat("EvianFlintGlass", (0.34, 0.76, 0.96, 0.74), roughness=0.06, metalness=0.14, alpha_blend=True, double_sided=True),
        "evian_cap": ctx.color_mat("EvianRoseCap", (0.94, 0.56, 0.65, 1.0), roughness=0.26, metalness=0.15),
        "water_meniscus": ctx.color_mat("AlpineWaterMeniscus", (0.58, 0.88, 1.0, 0.82), roughness=0.05, metalness=0.12, alpha_blend=True),
        "walnut_fluted": ctx.tex_mat("FlutedWalnut", walnut_fluted_img, roughness=0.46, metalness=0.05, quality=90),
        "walnut_solid": ctx.color_mat("SolidWalnut", (0.26, 0.15, 0.09, 1.0), roughness=0.38, metalness=0.05),
        "marmorino": ctx.tex_mat("MarmorinoLimestoneBoiserie", marmorino_img, roughness=0.68, metalness=0.02, quality=90),
        "plaster": ctx.color_mat("VenetianPlaster", (0.88, 0.84, 0.77, 1.0), roughness=0.76, metalness=0.01),
        "brass": ctx.color_mat("BrushedChampagneBrass", (0.82, 0.69, 0.44, 1.0), roughness=0.26, metalness=0.86),
        "bronze_dark": ctx.color_mat("StudioBronze", (0.17, 0.17, 0.15, 1.0), roughness=0.36, metalness=0.70),
        "window_frame": ctx.color_mat("ChampagneAnodizedMullion", (0.78, 0.74, 0.68, 1.0), roughness=0.34, metalness=0.58),
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
        "coastal_pine": ctx.tex_mat("MediterraneanPineSlope", coastal_pine_img, roughness=0.90, metalness=0.01, quality=88, double_sided=True),
        "far_mist_mountain": ctx.color_mat("FarMistMountain", (0.43, 0.49, 0.59, 1.0), roughness=0.96, metalness=0.0, double_sided=True),
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
        "crystal_glass": ctx.color_mat("ClearCrystalGlass", (0.56, 0.84, 0.96, 0.60), roughness=0.05, metalness=0.14, alpha_blend=True, double_sided=True),
        "orchid_white": ctx.color_mat("PhalaenopsisOrchid", (0.98, 0.97, 0.95, 1.0), roughness=0.45, metalness=0.02),
        "pietra_grey": ctx.tex_mat("PietraGreyMarble", pietra_grey_img, roughness=0.18, metalness=0.05, quality=92),
        "tundra_grey": ctx.tex_mat("TundraGreySlab", tundra_grey_img, roughness=0.28, metalness=0.04, quality=92),
        "graphite_slate": ctx.tex_mat("GraphiteSlateLacquer", graphite_slate_img, roughness=0.34, metalness=0.45, quality=90),
        "platinum": ctx.color_mat("BrushedPlatinum", (0.81, 0.83, 0.87, 1.0), roughness=0.22, metalness=0.90),
        "nordic_slate": ctx.color_mat("NordicSlateNubuck", (0.23, 0.29, 0.34, 1.0), roughness=0.78, metalness=0.02),
        "alpine_granite": ctx.tex_mat("AlpineGraniteCrag", alpine_granite_img, roughness=0.88, metalness=0.02, quality=90, double_sided=True),
        "pool_water": ctx.color_mat("InfinityPoolTurquoise", (0.07, 0.46, 0.58, 0.88), roughness=0.06, metalness=0.14, emissive=(0.02, 0.14, 0.19), alpha_blend=True),
        "terracotta": ctx.color_mat("AgedTerracottaClay", (0.68, 0.41, 0.30, 1.0), roughness=0.82, metalness=0.02),
        "smart_panel": ctx.tex_mat("SmartHomeOLED", smart_panel_img, roughness=0.16, metalness=0.06, quality=94, emissive=(0.72, 0.76, 0.82)),
        "dairy_label": ctx.tex_mat("OrganicDairyLabel", dairy_label_img, roughness=0.36, metalness=0.02, quality=92),
        "berry_blue": ctx.color_mat("OrganicBlueberry", (0.14, 0.18, 0.34, 1.0), roughness=0.42, metalness=0.02),
        "berry_red": ctx.color_mat("HeirloomBerryRed", (0.58, 0.09, 0.13, 1.0), roughness=0.38, metalness=0.02),
        "produce_green": ctx.color_mat("GardenLeafGreen", (0.22, 0.42, 0.20, 1.0), roughness=0.58, metalness=0.01),
        "citrus_yellow": ctx.color_mat("MeyerLemonCitrus", (0.90, 0.74, 0.18, 1.0), roughness=0.40, metalness=0.02),
        "steak_marbled": ctx.color_mat("DryAgedRibeyeMarbled", (0.52, 0.14, 0.15, 1.0), roughness=0.48, metalness=0.02),
        "wine_bottle": ctx.color_mat("VintageBordeauxGlass", (0.07, 0.16, 0.09, 1.0), roughness=0.14, metalness=0.12),
        "champagne_liquid": ctx.color_mat("BrutChampagneGold", (0.94, 0.84, 0.56, 0.82), roughness=0.06, metalness=0.08, alpha_blend=True),
        # Batch 14 Expansion Materials
        "obsidian_bezel": ctx.color_mat("JetObsidianBezel", (0.05, 0.06, 0.08, 1.0), roughness=0.22, metalness=0.55),
        "wolf_red": ctx.color_mat("WolfCrimsonKnob", (0.72, 0.13, 0.16, 1.0), roughness=0.24, metalness=0.18),
        "warm_grey_upper": ctx.color_mat("WarmGreyUpperFascia", (0.80, 0.78, 0.75, 1.0), roughness=0.52, metalness=0.04),
        "racing_green": ctx.color_mat("ClubRacingGreenWool", (0.10, 0.27, 0.17, 1.0), roughness=0.84, metalness=0.02),
        "ebony_piano": ctx.color_mat("ConcertEbonyLacquer", (0.04, 0.04, 0.05, 1.0), roughness=0.09, metalness=0.12),
        "copper_cook": ctx.color_mat("HammeredCopperSkillet", (0.80, 0.45, 0.26, 1.0), roughness=0.22, metalness=0.88),
        "saddle_tan": ctx.color_mat("EnglishSaddleTan", (0.58, 0.34, 0.18, 1.0), roughness=0.46, metalness=0.04),
        "steel": ctx.color_mat("BrushedStainlessSteel", (0.78, 0.80, 0.84, 1.0), roughness=0.24, metalness=0.88),
        "stainless": ctx.color_mat("HeavyApplianceSteel", (0.74, 0.77, 0.81, 1.0), roughness=0.26, metalness=0.86),
        "charcoal_steel": ctx.color_mat("CharcoalArchitecturalSteel", (0.16, 0.18, 0.20, 1.0), roughness=0.38, metalness=0.72),
        "limestone": ctx.color_mat("OutdoorSandstonePaver", (0.78, 0.75, 0.70, 1.0), roughness=0.74, metalness=0.02),
        "basalt": ctx.color_mat("BasaltInfinityWeir", (0.15, 0.16, 0.18, 1.0), roughness=0.56, metalness=0.06),
        "teak": ctx.color_mat("WeatheredPoolsideTeak", (0.46, 0.31, 0.19, 1.0), roughness=0.64, metalness=0.02),
        "offwhite_cushion": ctx.color_mat("OutdoorSunbrellaLinen", (0.93, 0.90, 0.84, 1.0), roughness=0.84, metalness=0.01),
        "conifer_dark": ctx.color_mat("AlpineEvergreenPine", (0.11, 0.22, 0.14, 1.0), roughness=0.88, metalness=0.01),
        "cobalt": ctx.color_mat("GreekDairyCobaltCap", (0.10, 0.26, 0.62, 1.0), roughness=0.32, metalness=0.06),
        "porcelain_white": ctx.color_mat("PorcelainDairyTub", (0.96, 0.96, 0.95, 1.0), roughness=0.24, metalness=0.02),
        "red_apple": ctx.color_mat("HoneycrispAppleRed", (0.72, 0.12, 0.14, 1.0), roughness=0.32, metalness=0.02),
        "herb_green": ctx.color_mat("OrchardLimeAvocado", (0.24, 0.48, 0.18, 1.0), roughness=0.52, metalness=0.02),
        "lemon_gold": ctx.color_mat("AmalfiLemonGold", (0.92, 0.78, 0.18, 1.0), roughness=0.38, metalness=0.02),
        "ivory": ctx.color_mat("PianoKeyIvory", (0.96, 0.94, 0.89, 1.0), roughness=0.22, metalness=0.04),
        "black": ctx.color_mat("MatteEbonyWood", (0.07, 0.07, 0.08, 1.0), roughness=0.38, metalness=0.08),
        "cream_wool": ctx.color_mat("SalonSilkWoolRug", (0.91, 0.87, 0.79, 1.0), roughness=0.90, metalness=0.01),
        "black_leather": ctx.color_mat("ConcertAnilineLeather", (0.09, 0.09, 0.11, 1.0), roughness=0.36, metalness=0.06),
        "velvet": ctx.color_mat("EquestrianVelvet", (0.10, 0.10, 0.13, 1.0), roughness=0.92, metalness=0.01),
        "optic_yellow": ctx.color_mat("OpticTennisBallYellow", (0.82, 0.92, 0.18, 1.0), roughness=0.78, metalness=0.01),
        "prestige_wine_labels": ctx.tex_mat("GrandCruWineLabels", prestige_wine_img, roughness=0.36, metalness=0.08, quality=92),
        "alpine_lake": ctx.color_mat("AlpineFjordWater", (0.06, 0.24, 0.34, 0.90), roughness=0.08, metalness=0.25, emissive=(0.02, 0.08, 0.13), alpha_blend=True),
        "aaa_mountain": ctx.tex_mat("AAAAlpineDolomite", aaa_mountain_img, roughness=0.84, metalness=0.02, quality=92, double_sided=True),
        # Batch 15-16 Expansion Materials
        "sheet_music": ctx.tex_mat("PianoNocturneScore", sheet_music_img, roughness=0.45, metalness=0.01, quality=92, emissive=(0.14, 0.12, 0.09)),
        "city_facade": ctx.tex_mat("GlassCurtainSkyscrapers", city_facade_img, roughness=0.14, metalness=0.72, quality=92, emissive=(0.14, 0.16, 0.22)),
        "himalayan_salt": ctx.tex_mat("HimalayanPinkSaltWall", himalayan_salt_img, roughness=0.36, metalness=0.02, quality=90, emissive=(0.56, 0.24, 0.18)),
        "bridge_steel": ctx.color_mat("SuspensionTowerSteel", (0.30, 0.15, 0.14, 1.0), roughness=0.34, metalness=0.78),
        "river_water": ctx.color_mat("EstuaryChannelWater", (0.12, 0.24, 0.34, 1.0), roughness=0.14, metalness=0.22),
        "coastal_foam": ctx.color_mat("EstuarySurfFoam", (0.86, 0.91, 0.94, 0.85), roughness=0.58, metalness=0.04, alpha_blend=True),
        "dove_boucle": ctx.color_mat("PearlDoveBoucle", (0.85, 0.86, 0.88, 1.0), roughness=0.90, metalness=0.01),
        "emerald_silk": ctx.color_mat("EmeraldBotanicalSilk", (0.11, 0.36, 0.34, 1.0), roughness=0.68, metalness=0.03),
        "le_creuset_red": ctx.color_mat("LeCreusetFlameEnamel", (0.82, 0.17, 0.10, 1.0), roughness=0.16, metalness=0.08),
        "burgundy_glass": ctx.color_mat("DarkBurgundyBottleGlass", (0.20, 0.04, 0.06, 1.0), roughness=0.14, metalness=0.12),
        "amber_wine": ctx.color_mat("SauternesAmberGlass", (0.78, 0.56, 0.16, 0.86), roughness=0.08, metalness=0.10, alpha_blend=True),
        "river_twilight": ctx.color_mat("TwilightRiverWater", (0.06, 0.09, 0.16, 0.94), roughness=0.09, metalness=0.35, emissive=(0.02, 0.03, 0.06)),
    }

    build_arch_shell(ctx, mats)
    build_salon_seating(ctx, mats)
    build_media_fireplace(ctx, mats)
    build_stair_and_balustrade(ctx, mats)
    build_loft_2f(ctx, mats)
    build_terrace_and_sky(ctx, mats)
    build_entry_and_niches(ctx, mats)
    build_south_kitchen(ctx, mats)
    build_south_terrace_and_mountains(ctx, mats)
    build_east_piano_sport_wing(ctx, mats)
    build_east_river_bridge_vista(ctx, mats)

    info = ctx.export_glb(OUT_GLB)
    for req in (
        "SkyCyclorama", "GalleryTVScreen", "ArcLampBulb", "EntryPatronCard",
        "FireplaceEmbers", "FireplaceLogs", "HiFiGlassDome",
        "ConciergePager1F", "ConciergePager2F", "EvianBottles1F",
        "TerraceSofaSeat", "OceanVistaWater", "SalonOrchidBowl",
        "GrandEntryDoors", "SmartHomePanelScreen",
        "FridgeDoorLeft", "FridgeDoorRight", "WolfRangeBody", "WolfRedKnobs",
        "LeCreusetDutchOven", "MauvielCopperStockpot", "BackSplashPotRail",
        "KitchenIslandStone", "KitchenFrenchGlass",
        "DiningTableMarble", "pool_water", "mountain_massif",
        "KitchenEspressoMachine", "DryAgeSteakCabinet", "BerkelSlicer",
        "GrandPianoCase", "GrandPianoSheetMusic", "CurvedPanoramicGlass",
        "EastRiverBridge", "PuttingGreenTurf", "TennisStrings0", "DressageSaddle",
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
