import math

def build_entry_and_niches(ctx, mats):
    # ------------------------------------------------------------------
    # 1. GRAND FOYER ARCHITECTURAL FRAMING
    # ------------------------------------------------------------------
    # Floor inlay medallion
    b = ctx.mb("EntryFloorMedallion", mats["foyer_medallion"])
    b.add_box(-13.25, 0.015, 6.65, 2.6, 0.02, 4.4)

    # Full-height bookmatched marble focal wall
    b = ctx.mb("EntryFocalWall", mats["marble"])
    b.add_box(-14.86, 4.55, 6.65, 0.14, 8.9, 4.5)

    # Rift oak wing panels flanking focal wall
    b = ctx.mb("EntryWingPanels", mats["rift_oak"])
    b.add_box(-14.80, 4.55, 4.20, 0.22, 8.9, 0.30)
    b.add_box(-14.80, 4.55, 9.10, 0.22, 8.9, 0.30)

    # Brushed champagne brass pilasters
    b = ctx.mb("EntryBrassPilasters", mats["brass"])
    b.add_box(-14.72, 4.55, 4.42, 0.10, 8.9, 0.14)
    b.add_box(-14.72, 4.55, 8.88, 0.10, 8.9, 0.14)

    # Top warm LED cove beam
    b = ctx.mb("EntryCoveBeam", mats["warm_led"])
    b.add_box(-14.55, 8.92, 6.65, 0.55, 0.10, 4.5)

    # ------------------------------------------------------------------
    # Sculptural Travertine & Smoked Rift-Oak Console
    # ------------------------------------------------------------------
    # Two tapered rift-oak plinth piers with brass bands
    b = ctx.mb("EntryConsolePiers", mats["rift_oak"])
    for z in (5.30, 8.00):
        b.add_cylinder(-14.02, 0.0, z, 0.22, 0.16, 1.58, segs=20)
    b = ctx.mb("EntryConsolePierBands", mats["brass"])
    for z in (5.30, 8.00):
        b.add_cylinder(-14.02, 0.02, z, 0.235, 0.235, 0.05, segs=20)
        b.add_cylinder(-14.02, 1.52, z, 0.175, 0.175, 0.05, segs=20)

    # Lower travertine gallery shelf
    b = ctx.mb("EntryConsoleShelf", mats["travertine"])
    b.add_box(-14.02, 0.45, 6.65, 1.30, 0.08, 3.4)

    # Linen art books on shelf
    b = ctx.mb("EntryConsoleBooks", mats["cream_pillow"])
    b.add_box(-14.02, 0.55, 5.85, 0.85, 0.10, 0.55)
    b.add_box(-14.02, 0.66, 5.85, 0.80, 0.08, 0.50)
    b = ctx.mb("EntryConsoleBooksDark", mats["charcoal"])
    b.add_box(-14.02, 0.55, 7.45, 0.85, 0.10, 0.55)
    b.add_box(-14.02, 0.66, 7.45, 0.80, 0.08, 0.50)

    # Thick rounded Roman travertine top slab
    b = ctx.mb("EntryConsoleTravertine", mats["travertine"])
    b.add_rounded_box(-14.02, 1.68, 6.65, 1.56, 0.16, 3.8, bevel=0.05)

    # ------------------------------------------------------------------
    # Beveled Arched Smoked-Bronze Mirror
    # ------------------------------------------------------------------
    b = ctx.mb("EntryMirrorBronze", mats["bronze_dark"])
    b.add_cylinder(-14.74, 4.35, 6.65, 0.95, 0.95, 0.06, segs=32,
                   rot_z=math.pi / 2, cap_top=True, cap_bot=True)
    b = ctx.mb("EntryMirrorGlass", mats["foyer_mirror"])
    b.add_cylinder(-14.72, 4.35, 6.65, 0.86, 0.86, 0.02, segs=32,
                   rot_z=math.pi / 2, cap_top=True, cap_bot=True)
    # Sleek vertical mirror arch trim in brass
    b = ctx.mb("EntryMirrorArchTrim", mats["brass"])
    b.add_box(-14.70, 5.42, 6.65, 0.06, 0.10, 1.30)
    b.add_box(-14.70, 3.28, 6.65, 0.06, 0.10, 1.30)

    # ------------------------------------------------------------------
    # Pair of Alabaster & Brass Wall Sconces
    # ------------------------------------------------------------------
    b = ctx.mb("EntrySconceBackplates", mats["brass"])
    for z in (5.10, 8.20):
        b.add_box(-14.72, 4.35, z, 0.06, 0.55, 0.14)
    b = ctx.mb("EntrySconceAlabaster", mats["warm_bulb"])
    for z in (5.10, 8.20):
        b.add_cylinder(-14.62, 4.10, z, 0.09, 0.09, 0.50, segs=18)
        b.add_sphere(-14.62, 4.62, z, 0.09, 0.09, 0.09, rings=10, segs=16)

    # ------------------------------------------------------------------
    # 2. FOYER CONSOLE STYLING + TILTED PATRON CARD
    # ------------------------------------------------------------------
    # Cognac leather & brass valet tray (brass rim framing exposed cognac suede interior!)
    b = ctx.mb("EntryValetTrayBrass", mats["brass"])
    b.add_box(-13.86, 1.77, 6.44, 0.80, 0.02, 1.06)
    b.add_box(-13.86, 1.815, 5.93, 0.80, 0.07, 0.035)
    b.add_box(-13.86, 1.815, 6.95, 0.80, 0.07, 0.035)
    b.add_box(-13.46, 1.815, 6.44, 0.035, 0.07, 1.06)
    b.add_box(-14.26, 1.815, 6.44, 0.035, 0.07, 1.06)
    b = ctx.mb("EntryValetTrayLeather", mats["cognac_suede"])
    b.add_box(-13.86, 1.792, 6.44, 0.74, 0.032, 0.99)

    # Brass card easel stand (cradling card from behind without clipping through)
    b = ctx.mb("EntryCardEasel", mats["brass"])
    b.add_box(-14.04, 1.86, 6.46, 0.03, 0.16, 0.04)
    b.add_box(-13.73, 1.795, 6.46, 0.025, 0.022, 0.34)

    # Sculpted brass car key fob inside tray
    b = ctx.mb("EntryKeyFob", mats["brass"])
    b.add_rounded_box(-13.70, 1.84, 6.20, 0.14, 0.03, 0.06, bevel=0.01)
    b.add_cylinder(-13.62, 1.84, 6.20, 0.015, 0.015, 0.10, segs=10,
                   rot_z=math.pi / 2)

    # Tilted 3D Patron Card
    card = ctx.mb("EntryPatronCard", mats["patron_card"])
    p0 = (-13.74, 1.80, 6.68)
    p1 = (-13.74, 1.80, 6.24)
    p2 = (-14.00, 1.92, 6.24)
    p3 = (-14.00, 1.92, 6.68)
    uv0 = (0.0, 0.0)
    uv1 = (1.0, 0.0)
    uv2 = (1.0, 1.0)
    uv3 = (0.0, 1.0)
    card.add_tri_raw(p0, p1, p2, uv0, uv1, uv2)
    card.add_tri_raw(p0, p2, p3, uv0, uv2, uv3)

    # Left side: fluted ceramic vessel with orchid
    b = ctx.mb("EntryOrchidVessel", mats["ceramic_white"])
    b.add_lathe(-14.02, 1.76, 7.85, [
        (0.00, 0.00), (0.10, 0.00), (0.12, 0.05),
        (0.13, 0.15), (0.11, 0.25), (0.09, 0.30),
        (0.10, 0.32), (0.00, 0.32)
    ], segs=24)
    b = ctx.mb("EntryOrchidStems", mats["bark"])
    for i, (dx, dz) in enumerate([(-0.02, 0.02), (0.03, -0.02), (0.0, 0.04)]):
        b.add_cylinder(-14.02 + dx, 2.05, 7.85 + dz, 0.008, 0.006, 0.55, segs=8)
    b = ctx.mb("EntryOrchidBlossoms", mats["orchid_white"])
    for (bx, by, bz) in [(-14.04, 2.55, 7.87), (-13.99, 2.62, 7.83),
                          (-14.02, 2.48, 7.89), (-14.05, 2.68, 7.84),
                          (-13.98, 2.50, 7.86)]:
        b.add_sphere(bx, by, bz, 0.045, 0.025, 0.045, rings=8, segs=12)

    # Right side: reed diffuser + travertine sphere
    b = ctx.mb("EntryDiffuserBottle", mats["charcoal"])
    b.add_cylinder(-14.02, 1.76, 5.25, 0.09, 0.07, 0.22, segs=18)
    b = ctx.mb("EntryDiffuserReeds", mats["brass"])
    for i in range(5):
        ang = i * (2 * math.pi / 5)
        rx = -14.02 + 0.03 * math.cos(ang)
        rz = 5.25 + 0.03 * math.sin(ang)
        b.add_cylinder(rx, 1.98, rz, 0.004, 0.004, 0.35, segs=6,
                       rot_x=0.08 * math.sin(ang), rot_z=0.08 * math.cos(ang))
    b = ctx.mb("EntryTravertineSphere", mats["travertine"])
    b.add_sphere(-14.02, 1.86, 5.65, 0.09, 0.09, 0.09, rings=12, segs=16)

    # ------------------------------------------------------------------
    # 3. PRESERVE 1F COLLECTORS' NICHE 1 — Bronze Arp Sculpture
    # ------------------------------------------------------------------
    b = ctx.mb("CollectorPlinth", mats["travertine"])
    b.add_box(13.5, 0.675, -9.6, 1.15, 1.35, 1.15)

    b = ctx.mb("CollectorArpSculpture", mats["bronze_dark"])
    b.add_curved_tube(
        [(13.5, 1.55, -9.6), (13.42, 1.95, -9.55), (13.30, 2.35, -9.62),
         (13.28, 2.75, -9.72), (13.40, 3.05, -9.68), (13.58, 3.18, -9.55),
         (13.72, 3.05, -9.45), (13.74, 2.70, -9.42), (13.62, 2.35, -9.48),
         (13.52, 2.05, -9.55), (13.50, 1.80, -9.60)],
        [0.075, 0.070, 0.065, 0.060, 0.058, 0.055, 0.058, 0.062, 0.068, 0.072, 0.075], segs=10
    )
    b.add_sphere(13.5, 1.55, -9.6, 0.11, 0.11, 0.11, rings=10, segs=14)
    b.add_sphere(13.50, 1.80, -9.60, 0.09, 0.09, 0.09, rings=10, segs=14)
    b.add_sphere(13.72, 3.05, -9.45, 0.08, 0.08, 0.08, rings=10, segs=14)

    # ------------------------------------------------------------------
    # 3. PRESERVE 1F COLLECTORS' NICHE 2 — Amphora Urn & Olive Branches
    # ------------------------------------------------------------------
    b = ctx.mb("AmphoraUrn", mats["ceramic_white"])
    b.add_lathe(13.3, 0.0, 8.6, [
        (0.00, 0.00), (0.22, 0.00), (0.28, 0.10),
        (0.32, 0.40), (0.30, 0.80), (0.22, 1.20),
        (0.14, 1.55), (0.16, 1.75), (0.20, 1.90),
        (0.18, 2.00), (0.00, 2.00)
    ], segs=28)

    b = ctx.mb("AmphoraOliveBranches", mats["bark"])
    for (dx, dz, tilt) in [(0.05, 0.02, 0.15), (-0.04, 0.05, -0.12),
                            (0.02, -0.05, 0.08)]:
        b.add_cylinder(13.3 + dx, 2.00, 8.6 + dz, 0.015, 0.010, 0.85, segs=8,
                       rot_x=tilt, rot_z=tilt * 0.7)

    b = ctx.mb("AmphoraOliveLeaves", mats["olive_leaf"])
    for (lx, ly, lz) in [(13.35, 2.55, 8.62), (13.28, 2.70, 8.58),
                          (13.32, 2.85, 8.65), (13.25, 2.62, 8.55)]:
        b.add_sphere(lx, ly, lz, 0.06, 0.02, 0.03, rings=6, segs=10)
    b = ctx.mb("AmphoraOliveLeavesBright", mats["olive_leaf_bright"])
    for (lx, ly, lz) in [(13.38, 2.78, 8.60), (13.30, 2.92, 8.63)]:
        b.add_sphere(lx, ly, lz, 0.05, 0.02, 0.03, rings=6, segs=10)

    # ------------------------------------------------------------------
    # 3. PRESERVE STAIRCASE FLOATING GALLERY SHELVES
    # ------------------------------------------------------------------
    b = ctx.mb("GalleryShelves", mats["walnut_solid"])
    for y in (2.40, 3.10, 3.80):
        b.add_box(-13.8, y, 12.2, 0.90, 0.06, 0.55)

    b = ctx.mb("GalleryMonographs", mats["charcoal"])
    b.add_box(-13.8, 2.48, 12.2, 0.55, 0.10, 0.40)
    b.add_box(-13.8, 2.60, 12.2, 0.50, 0.08, 0.36)
    b = ctx.mb("GalleryMonographsLight", mats["cream_pillow"])
    b.add_box(-13.8, 3.18, 12.2, 0.50, 0.10, 0.38)
    b.add_box(-13.8, 3.30, 12.2, 0.45, 0.08, 0.34)

    b = ctx.mb("GalleryStonewareVase", mats["ceramic_white"])
    b.add_lathe(-13.8, 3.83, 12.2, [
        (0.00, 0.00), (0.10, 0.00), (0.13, 0.06),
        (0.14, 0.16), (0.10, 0.26), (0.07, 0.32),
        (0.08, 0.36), (0.00, 0.36)
    ], segs=20)

    # ------------------------------------------------------------------
    # 4. PALATIAL WEST GRAND DOUBLE ENTRANCE DOORS (6.40 WU wide x 8.40 WU tall)
    # ------------------------------------------------------------------
    # Stepped Silver-Travertine & Obsidian Cast-Bronze Architrave (X=-14.78, Z in [-6.8, -0.4])
    b = ctx.mb("GrandEntryPortalStone", mats["travertine"])
    b.add_box(-14.74, 4.25, -7.12, 0.44, 8.50, 0.64)
    b.add_box(-14.74, 4.25, -0.08, 0.44, 8.50, 0.64)
    b.add_box(-14.74, 8.20, -3.60, 0.48, 0.72, 7.68)

    b = ctx.mb("GrandEntryPortalBronze", mats["bronze_dark"])
    b.add_box(-14.66, 4.00, -6.82, 0.26, 8.00, 0.14)
    b.add_box(-14.66, 4.00, -0.38, 0.26, 8.00, 0.14)
    b.add_box(-14.66, 7.72, -3.60, 0.28, 0.18, 6.58)
    b.add_box(-14.66, 0.04, -3.60, 0.32, 0.08, 6.58)

    # Twin Mansion Cast-Bronze & Grey-Marble Double Door Leaves (Z in [-6.72, -3.62] and [-3.58, -0.48])
    b = ctx.mb("GrandEntryDoors", mats["bronze_dark"])
    b.add_box(-14.74, 3.82, -5.17, 0.18, 7.56, 3.06)
    b.add_box(-14.74, 3.82, -2.03, 0.18, 7.56, 3.06)

    b = ctx.mb("GrandEntryDoorStoneInlay", mats["pietra_grey"])
    for dz in (-5.17, -2.03):
        b.add_box(-14.63, 5.20, dz, 0.04, 2.95, 2.24)
        b.add_box(-14.63, 1.95, dz, 0.04, 2.65, 2.24)

    # Brushed Champagne-Gold Coffer Mouldings, Overhead Crest Transom & Twin Vertical Bar Pulls
    b = ctx.mb("GrandEntryDoorBrassTrim", mats["brass"])
    for dz in (-5.17, -2.03):
        b.add_box(-14.60, 5.20, dz - 1.15, 0.05, 3.02, 0.06)
        b.add_box(-14.60, 5.20, dz + 1.15, 0.05, 3.02, 0.06)
        b.add_box(-14.60, 1.95, dz - 1.15, 0.05, 2.72, 0.06)
        b.add_box(-14.60, 1.95, dz + 1.15, 0.05, 2.72, 0.06)
    # Center astragal bead + tall architectural pulls
    b.add_box(-14.62, 3.82, -3.60, 0.08, 7.56, 0.06)
    b.add_box(-14.60, 7.64, -3.60, 0.10, 0.08, 6.32)
    b = ctx.mb("GrandEntryPulls", mats["brass"])
    for pz in (-3.92, -3.28):
        b.add_cylinder(-14.48, 2.05, pz, 0.048, 0.048, 3.40, segs=16)
        b.add_cylinder(-14.56, 2.40, pz, 0.030, 0.030, 0.18, segs=10, rot_z=1.5708)
        b.add_cylinder(-14.56, 5.10, pz, 0.030, 0.030, 0.18, segs=10, rot_z=1.5708)

    # Tall Fluted Alabaster Sconces Flanking the Grand Double Doors
    b = ctx.mb("GrandEntrySconces", mats["warm_bulb"])
    for sz in (-7.65, 0.45):
        b.add_cylinder(-14.52, 3.30, sz, 0.12, 0.12, 1.65, segs=18)
    b = ctx.mb("GrandEntrySconceCaps", mats["brass"])
    for sz in (-7.65, 0.45):
        b.add_box(-14.56, 3.24, sz, 0.22, 0.10, 0.30)
        b.add_box(-14.56, 4.98, sz, 0.22, 0.10, 0.30)

    # ------------------------------------------------------------------
    # 5. WHOLE-HOME SMART CONTROL WALL PANEL (Right next to Grand Entrance at Z=+2.10)
    # ------------------------------------------------------------------
    b = ctx.mb("SmartHomePanelFrame", mats["platinum"])
    b.add_rounded_box(-14.70, 3.65, 2.10, 0.09, 1.24, 1.78, bevel=0.025)
    b = ctx.mb("SmartHomePanelCove", mats["warm_led"])
    b.add_box(-14.73, 3.65, 2.10, 0.02, 1.30, 1.84)
    b = ctx.mb("SmartHomePanelScreen", mats["smart_panel"])
    b.add_quad((-14.64, 3.12, 2.91), (-14.64, 3.12, 1.29),
               (-14.64, 4.18, 1.29), (-14.64, 4.18, 2.91), uv_scale=(1.0, 1.0))
