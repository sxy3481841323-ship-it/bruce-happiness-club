import math

def build_entry_and_niches(ctx, mats):
    # ---------------------------------------------------------------
    # 1. Entryway Cantilevered Roman Travertine Console
    # ---------------------------------------------------------------
    trav = ctx.mb("EntryConsoleTravertine", mats["travertine"])
    # Two solid plinth piers
    trav.add_box(-14.1, 0.79, 5.5, 1.1, 1.58, 1.1, uv_tile=1.0)
    trav.add_box(-14.1, 0.79, 7.5, 1.1, 1.58, 1.1, uv_tile=1.0)
    # Cantilevered slab top
    trav.add_box(-14.08, 1.65, 6.5, 1.48, 0.14, 3.05, uv_tile=1.0)

    # Aged round bronze mirror on left wall
    bronze = ctx.mb("EntryMirrorBronze", mats["bronze_dark"])
    # Outer ring (thin cylinder rotated to face +X)
    bronze.add_cylinder(-14.86, 4.05, 6.5, 0.62, 0.62, 0.06, segs=32,
                        rot_z=math.pi / 2, cap_top=True, cap_bot=True)
    # Inner recessed ring
    bronze.add_cylinder(-14.83, 4.05, 6.5, 0.54, 0.54, 0.04, segs=32,
                        rot_z=math.pi / 2, cap_top=True, cap_bot=True)
    # Tinted mirror center
    mirror = ctx.mb("EntryMirrorGlass", mats["charcoal"])
    mirror.add_cylinder(-14.80, 4.05, 6.5, 0.50, 0.50, 0.02, segs=32,
                        rot_z=math.pi / 2, cap_top=True, cap_bot=True)

    # ---------------------------------------------------------------
    # 2. Walnut & Cognac-Suede Catchall Tray + Patron Card
    # ---------------------------------------------------------------
    walnut = ctx.mb("EntryTrayWalnut", mats["walnut_solid"])
    walnut.add_rounded_box(-13.95, 1.745, 6.42, 0.72, 0.05, 0.92,
                           bevel=0.02, uv_tile=1.0)
    # Cognac suede inner bed
    suede = ctx.mb("EntryTraySuede", mats["cognac_suede"])
    suede.add_box(-13.95, 1.765, 6.42, 0.62, 0.012, 0.82, uv_tile=1.0)

    # Patron card (exact mesh name)
    card = ctx.mb("EntryPatronCard", mats["patron_card"])
    p0 = (-13.70, 1.785, 6.62)
    p1 = (-13.70, 1.785, 6.20)
    p2 = (-14.12, 1.785, 6.20)
    p3 = (-14.12, 1.785, 6.62)
    uv0 = (0.0, 0.0)
    uv1 = (1.0, 0.0)
    uv2 = (1.0, 1.0)
    uv3 = (0.0, 1.0)
    card.add_tri_raw(p0, p1, p2, uv0, uv1, uv2)
    card.add_tri_raw(p0, p2, p3, uv0, uv2, uv3)

    # Volcanic charcoal stone paperweight
    stone = ctx.mb("EntryPaperweight", mats["charcoal"])
    stone.add_sphere(-13.86, 1.82, 5.65, 0.075, 0.055, 0.065, rings=10, segs=14)

    # Slender brass letter opener
    brass = ctx.mb("EntryLetterOpener", mats["brass"])
    brass.add_cylinder(-13.98, 1.79, 6.05, 0.012, 0.008, 0.42, segs=10,
                       rot_x=math.pi / 2, cap_top=True, cap_bot=True)
    brass.add_sphere(-13.98, 1.79, 6.27, 0.022, 0.022, 0.022, rings=8, segs=12)

    # ---------------------------------------------------------------
    # 3. Collector Architectural Plinth & Bronze Arp Sculpture
    # ---------------------------------------------------------------
    ped = ctx.mb("CollectorPlinth", mats["travertine"])
    ped.add_box(13.5, 0.675, -9.6, 1.2, 1.35, 1.2, uv_tile=1.0)

    sculpt = ctx.mb("CollectorArpSculpture", mats["bronze_dark"])
    # Fluid abstract loop spine
    spine = [
        (13.5, 1.55, -9.6),
        (13.42, 1.95, -9.55),
        (13.30, 2.35, -9.62),
        (13.28, 2.75, -9.72),
        (13.40, 3.05, -9.68),
        (13.58, 3.18, -9.55),
        (13.72, 3.05, -9.45),
        (13.74, 2.70, -9.42),
        (13.62, 2.35, -9.48),
        (13.52, 2.05, -9.55),
        (13.50, 1.80, -9.60),
    ]
    radii = [0.075, 0.070, 0.065, 0.060, 0.058, 0.055, 0.058, 0.062, 0.068, 0.072, 0.075]
    sculpt.add_curved_tube(spine, radii, segs=10)
    # Sculpted spheres at loop ends
    sculpt.add_sphere(13.5, 1.55, -9.6, 0.11, 0.11, 0.11, rings=12, segs=16)
    sculpt.add_sphere(13.50, 1.80, -9.60, 0.09, 0.09, 0.09, rings=12, segs=16)
    sculpt.add_sphere(13.72, 3.05, -9.45, 0.08, 0.08, 0.08, rings=12, segs=16)

    # ---------------------------------------------------------------
    # 4. Right-Front Unglazed Ceramic Amphora Urn + Olive Branches
    # ---------------------------------------------------------------
    amph = ctx.mb("AmphoraUrn", mats["plaster"])
    profile = [
        (0.00, 0.00),
        (0.28, 0.00),
        (0.34, 0.08),
        (0.40, 0.30),
        (0.42, 0.55),
        (0.36, 0.85),
        (0.26, 1.10),
        (0.20, 1.28),
        (0.22, 1.38),
        (0.24, 1.45),
        (0.20, 1.45),
    ]
    amph.add_lathe(13.3, 0.0, 8.6, profile, segs=28)

    # Olive trunks
    trunk = ctx.mb("OliveTrunks", mats["bark"])
    trunk.add_curved_tube(
        [(13.3, 1.42, 8.6), (13.28, 1.85, 8.58), (13.24, 2.25, 8.62),
         (13.20, 2.65, 8.58), (13.18, 3.00, 8.62)],
        [0.045, 0.040, 0.034, 0.028, 0.022], segs=8)
    trunk.add_curved_tube(
        [(13.3, 1.42, 8.6), (13.36, 1.80, 8.66), (13.42, 2.15, 8.70),
         (13.46, 2.50, 8.68), (13.48, 2.80, 8.72)],
        [0.040, 0.035, 0.030, 0.024, 0.018], segs=8)
    trunk.add_curved_tube(
        [(13.3, 1.42, 8.6), (13.32, 1.75, 8.52), (13.30, 2.05, 8.46),
         (13.26, 2.35, 8.44)],
        [0.038, 0.032, 0.026, 0.020], segs=8)

    # Olive foliage clusters
    leaf = ctx.mb("OliveFoliage", mats["olive_leaf"])
    leaf_b = ctx.mb("OliveFoliageBright", mats["olive_leaf_bright"])
    clusters = [
        (13.18, 3.05, 8.62, 0.22, 0.16, 0.20),
        (13.48, 2.85, 8.72, 0.20, 0.15, 0.18),
        (13.26, 2.40, 8.44, 0.18, 0.13, 0.16),
        (13.22, 2.70, 8.58, 0.16, 0.12, 0.15),
        (13.44, 2.55, 8.68, 0.15, 0.11, 0.14),
    ]
    for i, (cx, cy, cz, rx, ry, rz) in enumerate(clusters):
        target = leaf if i % 2 == 0 else leaf_b
        target.add_sphere(cx, cy, cz, rx, ry, rz, rings=10, segs=14)

    # ---------------------------------------------------------------
    # 5. Staircase Wall Recessed Gallery Shelf
    # ---------------------------------------------------------------
    shelf = ctx.mb("GalleryShelves", mats["bronze_dark"])
    shelf.add_box(-13.8, 2.4, 12.2, 0.55, 0.05, 3.2, uv_tile=1.0)
    shelf.add_box(-13.8, 3.9, 12.2, 0.55, 0.05, 3.2, uv_tile=1.0)

    # Stacked monographs on lower shelf
    books_cream = ctx.mb("GalleryBooksCream", mats["cream_pillow"])
    books_char = ctx.mb("GalleryBooksCharcoal", mats["charcoal"])
    books_cog = ctx.mb("GalleryBooksCognac", mats["cognac_suede"])

    # Lower shelf stack
    books_cream.add_box(-13.8, 2.46, 11.2, 0.42, 0.06, 0.62, uv_tile=1.0)
    books_char.add_box(-13.8, 2.53, 11.2, 0.40, 0.05, 0.58, uv_tile=1.0)
    books_cog.add_box(-13.8, 2.59, 11.2, 0.38, 0.05, 0.55, uv_tile=1.0)
    books_cream.add_box(-13.8, 2.65, 11.2, 0.36, 0.05, 0.52, uv_tile=1.0)

    # Lower shelf second stack
    books_char.add_box(-13.8, 2.46, 12.4, 0.40, 0.06, 0.58, uv_tile=1.0)
    books_cog.add_box(-13.8, 2.53, 12.4, 0.38, 0.05, 0.54, uv_tile=1.0)
    books_cream.add_box(-13.8, 2.59, 12.4, 0.36, 0.05, 0.50, uv_tile=1.0)

    # Upper shelf stack
    books_cog.add_box(-13.8, 3.96, 11.4, 0.40, 0.06, 0.60, uv_tile=1.0)
    books_cream.add_box(-13.8, 4.03, 11.4, 0.38, 0.05, 0.56, uv_tile=1.0)
    books_char.add_box(-13.8, 4.09, 11.4, 0.36, 0.05, 0.52, uv_tile=1.0)

    # Tiny matte stoneware vase on upper shelf
    vase = ctx.mb("GalleryStonewareVase", mats["ceramic_white"])
    vase_profile = [
        (0.00, 0.00),
        (0.06, 0.00),
        (0.09, 0.04),
        (0.10, 0.12),
        (0.08, 0.20),
        (0.05, 0.26),
        (0.055, 0.30),
        (0.045, 0.30),
    ]
    vase.add_lathe(-13.8, 3.925, 12.9, vase_profile, segs=18)
