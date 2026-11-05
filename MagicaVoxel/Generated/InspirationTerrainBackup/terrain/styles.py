"""Every terrain style the images draw, measured from the art: its family, height
in levels, colours (the art's own, read from its pixels), the image's ground
tiles on top and below, and the test layout it is checked in.

A style's labels are {label: (RGB, TwoColor group, crate class)}; its files are
<Prefix>_<Name>_<Piece>[_Treatment].vox in output/<image>/. Each also records the
image it was measured in (image), its scale (ppt: the image's pixels a tile), its
vertical foreshortening (K: drawn pixels a voxel of height, over a pixel a voxel
across), the crop it was fitted against (art) and what was measured (note).
"""
import layout
from families import (CaveMouthMixin, DrainMixin, EarthBank, FacetedCliff, IslandRim, LumpyWall, MarioPlatform,
                      Masonry, NotchMixin, StonyBank, StrataCliff, StripedCliff, WaterfallMixin, ZigzagTrim,
                      with_extras)

E, G, R, W, D = "earth", "grass", "rock", "water", "dark"
STYLES = []


def L(**kw):
    return {k: tuple(v) for k, v in kw.items()}


def add(cls, source, name, levels, labels, image, ppt, K, art, note, **kw):
    """A style, checked in the standard layout (layout.standard) with its extras."""
    s = cls(source, name, levels, labels, image=image, ppt=ppt, K=K, art=art, note=note, **kw)
    s.test = layout.standard(s.extra)
    STYLES.append(s)
    return s



# ----------------------------------------------------------------------------
# mario.jpg: Paper Mario style, 3 displayed pixels an original pixel (a tile is 48),
# faces drawn at about 0.7 of their height (the tall block's face, 23 voxels drawn,
# and the low platform's, 11, then come to 2 levels and 1).
MARIO_PLATFORM = L(rim_light=((205, 255, 120), G, "grass"), fringe=((97, 201, 79), G, "grass"),
                   fringe_dark=((34, 96, 52), G, "grass"), soil_shadow=((100, 56, 41), E, "earth"),
                   soil=((206, 122, 87), E, "earth"), soil_mark=((171, 98, 67), E, "earth"),
                   soil_dark=((160, 92, 62), E, "earth"), fill=((190, 110, 78), E, "earth"))
add(MarioPlatform, "mario", "GrassPlatform_H1", 1, MARIO_PLATFORM, "mario.jpg", 48, 0.7, (380, 160, 640, 225),
    "The low raised platform in the middle of the field and the field's own front edge: a face of 11 voxels "
    "drawn (rows 180-212 at x 420-460), 1 level.",
    top="Mario_Ground_Meadow", bottom="Mario_Ground_Meadow", inset=3, tongue=4, tongue_h=3, cross=8,
    flat={E: (206, 122, 87)})
add(MarioPlatform, "mario", "GrassPlatform_H2", 2, MARIO_PLATFORM, "mario.jpg", 48, 0.7, (520, 50, 640, 150),
    "The tall block at the top right: a face of 23 voxels drawn (rows 72-139 at x 560-600), 2 levels.",
    top="Mario_Ground_Meadow", bottom="Mario_Ground_Meadow", inset=3, tongue=4, tongue_h=3, cross=8,
    flat={E: (206, 122, 87)})
add(ZigzagTrim, "mario", "TrimPlatform_H2", 2,
    L(trim_light=((243, 152, 62), "trim", "orange"), trim=((237, 122, 59), "trim", "orange"),
      trim_dark=((197, 77, 41), "trim", "red"), trim_line=((60, 14, 8), "trim", "red"),
      teal=((8, 87, 87), "teal", "rock"), teal_dark=((4, 57, 64), "teal", "rock"), fill=((8, 87, 87), "teal", "rock")),
    "mario.jpg", 48, 0.7, (600, 260, 720, 340),
    "The peach path's edge at the right: a band of orange triangles 10 voxels drawn (rows 285-314) over a dark "
    "teal wall going on below the frame, 2 levels.",
    top="Mario_Ground_PeachDirt", bottom="Mario_Ground_Meadow", inset=3, body_group="teal", trim_h=14, zig=8,
    flat={"trim": (237, 122, 59), "teal": (8, 87, 87)})

# ----------------------------------------------------------------------------
# poke_n.png: native (16 px a tile), heights at 0.46 (its buildings').
add(StripedCliff, "poke_n", "EarthCliff_H2", 2,
    L(face_light=((204, 138, 89), E, "earth"), face=((142, 94, 61), E, "earth"), face_dark=((121, 80, 51), E, "earth"),
      face_line=((82, 56, 40), E, "earth"), face_foot=((70, 46, 30), E, "earth"), fill=((110, 74, 48), E, "earth"),
      grass_edge=((137, 197, 76), G, "grass")),
    "poke_n.png", 16, 0.46, (300, 262, 430, 330),
    "The terraced earth cliffs round the village: faces 18 rows drawn from the rim to the dark foot (295-312 at "
    "x 352-362), 39 voxels, 2 levels.",
    top="PokeN_Ground_Meadow", bottom="PokeN_Ground_Meadow", flat={E: (142, 94, 61)})
add(FacetedCliff, "poke_n", "RedRockCliff_H9", 9,
    L(grass_edge=((87, 121, 53), G, "grass"), block_top=((213, 147, 97), "red", "red"),
      block_light=((181, 117, 70), "red", "red"), block=((123, 79, 52), "red", "red"),
      block_low=((104, 68, 42), "red", "red"), crease=((79, 53, 40), "red", "red"), foot=((52, 39, 30), "red", "red"),
      fill=((113, 71, 44), "red", "red")),
    "poke_n.png", 16, 0.46, (0, 515, 190, 635),
    "The tall red-brown rock at the left edge above the lake: 65 px drawn from the grass rim to the dark foot (y "
    "551-615 at x 20), 141 voxels, 9 levels, the tiers behind it shorter; broken beds of angular blocks 8-12 px "
    "drawn, each lit along its top edge (y 552, 562, 569, 579, 594 at x 20).",
    top="PokeN_Ground_Meadow", bottom="PokeN_Ground_Meadow", body_group="red",
    rows=(18, 22, 16, 20, 24, 18), blocks=((10, 6), (5, 11), (16,), (7, 9), (12, 4), (6, 10)), depth=1.8, top_h=2,
    low_h=5, flat={"red": (123, 79, 52)})

# ----------------------------------------------------------------------------
# The Pixelwood images (3x for A and C, 48 px a tile; 5x for B, 80): faces measured
# against B's house, whose wall top its author put at z 34 for 30 art px drawn
# (K 0.88). B and C reuse A's meadow, as the ground collection decided.
PW = "PixelwoodA_Ground_Meadow"
PW_BANK = L(grass_edge=((48, 83, 21), G, "grass"), bank_light=((179, 101, 70), E, "earth"),
            bank=((136, 75, 44), E, "earth"), bank_dark=((108, 58, 37), E, "earth"),
            bank_foot=((97, 43, 38), E, "earth"), bank_line=((40, 12, 10), E, "earth"),
            fill=((120, 66, 40), E, "earth"))
add(EarthBank, "pixelwood_a", "EarthBank_H2", 2, PW_BANK, "pixelwood_a.jpg", 48, 0.88, (80, 70, 720, 260),
    "The raised earth banks behind the camp: faces 34 art px from the rim to the foot (y 90-192 at x 300 and 450, "
    "3x), 2 levels.",
    top=PW, bottom=PW, light_h=2, foot_teeth=4, blotch=0.14, flat={E: (136, 75, 44)})
add(StrataCliff, "pixelwood_b", "SlateLedge_H1", 1,
    L(grass_edge=((37, 86, 46), G, "grass"), band=((121, 124, 135), R, "rock"), band_alt=((113, 117, 127), R, "rock"),
      band_light=((150, 153, 164), R, "rock"), band_dark=((85, 92, 95), R, "rock"), joint=((67, 72, 78), R, "rock"),
      fill=((110, 113, 123), R, "rock")),
    "pixelwood_b.gif", 80, 0.88, (800, 430, 1210, 600),
    "The gray slate ledges between the grass terraces: two courses with lit top edges, 17 art px under a 3 px "
    "grass rim (y 475-557 at x 960 and 1040, 5x), 1 level.",
    top=PW, bottom=PW, body_group=R, bands=(7,), joint=16, rim=2, flat={R: (121, 124, 135)})
PW_FALL = dict(PW_BANK, water=((80, 143, 186), W, "water"), water_light=((129, 189, 202), W, "water"),
               foam=((174, 217, 206), W, "foam"))
add(with_extras(EarthBank, WaterfallMixin), "pixelwood_c", "EarthBank_H2", 2, PW_FALL, "pixelwood_c.jpg", 49, 0.88,
    (0, 120, 736, 330),
    "The earth banks either side of the waterfall: faces 34 art px from the rim to the foot (y 140-245 at x 560 "
    "and 640, 3x), 2 levels; the river pours over them in a sheet with a foam lip and foams at the foot.",
    top=PW, bottom=PW, light_h=2, foot_teeth=4, blotch=0.1, lip=3, extra=("Fall", "Channel"),
    plans={"Fall": "Straight", "Channel": "Fill"},
    tops={"Fall": "PixelwoodC_Ground_River", "Channel": "PixelwoodC_Ground_River"},
    bottoms={"Fall": "PixelwoodC_Ground_River"}, flat={E: (136, 75, 44)})

# ----------------------------------------------------------------------------
# poke_a.jpg: 12.25 px a tile (by the forest's period), heights at 0.46.
add(with_extras(StripedCliff, WaterfallMixin), "poke_a", "EarthCliff_H3", 3,
    L(face_light=((214, 146, 97), E, "earth"), face=((164, 104, 60), E, "earth"), face_dark=((137, 86, 47), E, "earth"),
      face_line=((112, 70, 38), E, "earth"), face_foot=((115, 85, 45), E, "earth"), fill=((150, 94, 54), E, "earth"),
      grass_edge=((141, 147, 85), G, "grass"), water=((105, 167, 215), W, "water"),
      water_light=((141, 204, 226), W, "water"), foam=((216, 232, 240), W, "foam")),
    "poke_a.jpg", 12.25, 0.46, (20, 170, 200, 270),
    "The orange ledges of the forest paths: faces 17 px drawn from the rim to the foot (y 223-239 at x 104 and "
    "110), 22 voxels at 12.25 px a tile, 3 levels at 0.46; a rounded column a tile, a crease every 12 px (x 95, "
    "107, 119, 131 at y 232). The falls (x 47-82) show light bands across the sheet.",
    top="PokeA_Ground_Meadow", bottom="PokeA_Ground_Meadow", widths=(16,), cartoon_widths=(16,), bulge=1.6,
    round_top=2, extra=("Fall", "Channel"), plans={"Fall": "Straight", "Channel": "Fill"},
    tops={"Fall": "PokeA_Ground_River", "Channel": "PokeA_Ground_River"}, bottoms={"Fall": "PokeA_Ground_River"},
    bands="across", lip=2, flat={E: (164, 104, 60)})

# ----------------------------------------------------------------------------
# poke_b.png: native, heights at 0.46.
add(LumpyWall, "poke_b", "CourseCliff_H5", 5,
    L(face_top=((209, 165, 105), E, "earth"), face_light=((148, 104, 65), E, "earth"), face=((127, 92, 59), E, "earth"),
      face_dark=((107, 80, 52), E, "earth"), crevice=((86, 70, 46), E, "earth"), course_gap=((80, 88, 70), E, "earth"),
      foot=((70, 57, 37), E, "earth"), fill=((117, 87, 56), E, "earth"), grass_edge=((78, 160, 56), G, "grass")),
    "poke_b.png", 16, 0.46, (0, 90, 140, 170),
    "The three-course cliffs round the plaza and down the west side: 40 px drawn from under the grass rim to the "
    "foot (y 116-155 at x 20 and 26), 87 voxels, 5 levels; each course 16 px, lit along its top and dark at its "
    "foot over a gray-green gap, two rounded lumps a tile in line course over course (y 132).",
    top="PokeB_Ground_Meadow", bottom="PokeB_Ground_Meadow", tiers=3, rim_kind="grass", bumps=(9, 7),
    cartoon_bumps=(16,), bulge=1.2, crevice=0.6, ledge=1, stagger=0, light=0.3, flat={E: (127, 92, 59)})

# ----------------------------------------------------------------------------
# poke_c.png: native, heights at 0.46.
add(with_extras(FacetedCliff, WaterfallMixin), "poke_c", "BlockCliff_H3", 3,
    L(block_top=((200, 132, 88), E, "red"), block_light=((170, 112, 74), E, "red"), block=((148, 104, 66), E, "red"),
      block_low=((131, 85, 57), E, "red"), crease=((94, 71, 56), E, "red"), foot=((82, 60, 49), E, "red"),
      fill=((132, 92, 60), E, "red"), grass_edge=((112, 158, 106), G, "grass"),
      water=((48, 176, 240), W, "water"), water_light=((72, 200, 240), W, "water"), foam=((236, 240, 226), W, "foam")),
    "poke_c.png", 16, 0.46, (280, 150, 470, 260),
    "The red-brown block cliffs of the gorge and its terraces: each face 23 px drawn from the rim to the foot "
    "(y 166-188 and 198-220 at x 330), 50 voxels, 3 levels, a narrow grass ledge (8 px) between terraces; blocks "
    "5-10 px across in rows of 4-11, lit along the top, dark below. The cascades beside them (x 340-456) step "
    "down in white foam lines every 16 px.",
    top="PokeC_Ground_Meadow", bottom="PokeC_Ground_Meadow", rows=(14, 10, 16, 12), blocks=((10, 6), (16,), (6, 10), (9, 7)),
    top_h=2, low_h=5,
    depth=1.6, extra=("Fall", "Channel"), plans={"Fall": "Straight", "Channel": "Fill"},
    tops={"Fall": "PokeC_Ground_River", "Channel": "PokeC_Ground_River"}, bottoms={"Fall": "PokeC_Ground_River"},
    bands="across", band_every=16, foam_lines=True, lip=1, flat={E: (148, 104, 66)})

# ----------------------------------------------------------------------------
# poke_d.png: native, heights at 0.46 (no building of its own to measure; the
# Pokemon maps' K).
PD_ROCK = L(grass_edge=((164, 126, 63), "surface", "earth"), face_light=((153, 148, 134), R, "rock"),
            face=((125, 119, 106), R, "rock"), face_dark=((96, 90, 77), R, "rock"), crevice=((80, 74, 61), R, "rock"),
            foot=((60, 58, 44), R, "rock"), fill=((110, 104, 92), R, "rock"))
PD_ROCK_KW = dict(body_group=R, rim_kind="grass", bumps=(6, 5, 5), cartoon_bumps=(8, 8), bulge=1.3, crevice=0.6,
                  stagger=5, light=0.3, flat={R: (125, 119, 106)})
add(LumpyWall, "poke_d", "RockLedge_H3", 3, PD_ROCK, "poke_d.png", 16, 0.46, (440, 380, 620, 520),
    "The gray crag ledges between the ochre terraces: 21 px drawn from the ochre rim to the dark foot (y 458-478 at "
    "x 500), 46 voxels, 3 levels; small rounded chunks in three staggered rows, lit on top, dark below.",
    top="PokeD_Ground_OchreFloor", bottom="PokeD_Ground_OchreFloor", tiers=3, **PD_ROCK_KW)
add(with_extras(LumpyWall, DrainMixin), "poke_d", "RockBank_H3", 3,
    dict(PD_ROCK, arch=((170, 164, 150), R, "rock"), bars=((64, 56, 40), D, "dark"), drain_dark=((30, 28, 22), D, "dark")),
    "poke_d.png", 16, 0.46, (440, 380, 620, 520),
    "The same crag where the ochre ground meets the river: 3 levels down to the water. Its Drain is the arched, "
    "barred outfall in the east bank (x 492-516, y 488-502): a ring of pale dressed stone, dark bars.",
    top="PokeD_Ground_OchreFloor", bottom="PokeD_Ground_River", tiers=3, extra=("Drain",),
    plans={"Drain": "Straight"}, drain_w=12, drain_h=15, ring=2, drain_d=8, **PD_ROCK_KW)
add(with_extras(LumpyWall, WaterfallMixin), "poke_d", "RiverCliff_H6", 6,
    dict(PD_ROCK, water=((96, 152, 136), W, "water"), water_light=((158, 196, 174), W, "water"),
         foam=((218, 236, 209), W, "foam")),
    "poke_d.png", 16, 0.46, (150, 380, 330, 500),
    "The tall crag walls where the river falls (the islets between the falls and the banks beside them): the "
    "falls drop 47 px drawn from the foam lip to the foot (y 430-477 at x 190), 102 voxels, 6 levels; the green "
    "sheet shows light bands across it.",
    top="PokeD_Ground_OchreFloor", bottom="PokeD_Ground_River", tiers=6, extra=("Fall", "Channel"),
    plans={"Fall": "Straight", "Channel": "Fill"},
    tops={"Fall": "PokeD_Ground_River", "Channel": "PokeD_Ground_River"}, bottoms={"Fall": "PokeD_Ground_River"},
    bands="across", band_every=16, lip=2, **PD_ROCK_KW)
add(with_extras(Masonry, CaveMouthMixin), "poke_d", "RetainingWall_H5", 5,
    L(stone=((153, 148, 134), R, "rock"), stone_light=((176, 169, 152), R, "rock"), stone_alt=((153, 148, 168), R, "rock"),
      stone_tan=((166, 145, 116), R, "rock"), joint=((106, 100, 87), R, "rock"), coping=((195, 190, 176), R, "rock"),
      fill=((140, 134, 120), R, "rock"), cave_dark=((70, 74, 68), D, "dark")),
    "poke_d.png", 16, 0.46, (530, 360, 640, 470),
    "The masonry wall under the cobbled terrace east of the river: 40 px drawn from the coping to the foot (y "
    "422-461 at x 560 and 600), 87 voxels, 5 levels; a coping of big pale blocks, courses of gray stones with "
    "purple-gray and tan ones among them. Its Archway is the arched passage through it (y 440-462).",
    top="PokeD_Ground_Cobblestone", bottom="PokeD_Ground_Cobblestone", body_group=R, course=12, block=8, stagger=4,
    coping=8, lip=1, extra=("Archway",), plans={"Archway": "Straight"}, mouth_w=12, mouth_h=40, mouth_d=11,
    flat={R: (153, 148, 134)})

# ----------------------------------------------------------------------------
# poke_e.png: native, heights at 0.46; its banks are poke_b's tileset's.
PE_BANK = L(face_top=((137, 97, 62), E, "earth"), face_light=((118, 88, 58), E, "earth"), face=((107, 80, 52), E, "earth"),
            face_dark=((86, 70, 46), E, "earth"), crevice=((74, 60, 39), E, "earth"), course_gap=((86, 95, 77), E, "earth"),
            foot=((60, 48, 29), E, "earth"), fill=((107, 80, 52), E, "earth"), grass_edge=((78, 160, 56), G, "grass"))
PE_KW = dict(tiers=1, rim_kind="grass", bumps=(9, 7), cartoon_bumps=(16,), bulge=1.0, crevice=0.6, stagger=0,
             light=0.3, flat={E: (107, 80, 52)})
add(LumpyWall, "poke_e", "EarthBank_H1", 1, PE_BANK, "poke_e.png", 16, 0.46, (40, 80, 200, 170),
    "The low earth banks along the forest edges: 9 px drawn from the rim to the foot (y 84-92 at x 110 and 116), "
    "20 voxels, 1 level; poke_b's course in one row.",
    top="PokeE_Ground_Meadow", bottom="PokeE_Ground_Meadow", **PE_KW)
add(LumpyWall, "poke_e", "LakeBank_H1", 1, PE_BANK, "poke_e.png", 16, 0.46, (40, 80, 200, 170),
    "The same bank where the meadow drops into the lakes, 1 level down to the water.",
    top="PokeE_Ground_Meadow", bottom="PokeE_Ground_Lake", **PE_KW)

# ----------------------------------------------------------------------------
# poke_f.png: native, heights at 0.46.
add(StonyBank, "poke_f", "StonyBank_H4", 4,
    L(stone_light=((215, 179, 135), E, "earth"), stone=((182, 141, 95), E, "earth"), seam=((153, 111, 65), E, "earth"),
      foot=((121, 71, 47), E, "earth"), fill=((160, 120, 76), E, "earth"), grass_edge=((176, 193, 99), G, "grass")),
    "poke_f.png", 16, 0.46, (0, 50, 200, 120),
    "The pale stony banks of the terraces round the town: 28 px drawn from the rim to the foot (y 83-110 at x "
    "190), 61 voxels, 4 levels; rounded tan stones in rows, the top row lit, a dark band at the foot.",
    top="PokeF_Ground_DryMeadow", bottom="PokeF_Ground_DryMeadow", foot_h=4, bulge=1.2, flat={E: (182, 141, 95)})

# ----------------------------------------------------------------------------
# poke_g.png: native, heights at 0.46.
add(LumpyWall, "poke_g", "RockLedge_H2", 2,
    L(face_top=((166, 151, 136), R, "rock"), face_light=((156, 127, 119), R, "rock"), face=((132, 114, 112), R, "rock"),
      face_dark=((106, 87, 85), R, "rock"), crevice=((80, 70, 72), R, "rock"), foot=((71, 66, 65), R, "rock"),
      fill=((120, 102, 100), R, "rock"), grass_edge=((150, 200, 128), G, "grass")),
    "poke_g.png", 16, 0.46, (300, 150, 470, 300),
    "The mauve-gray rock ledge running diagonally down the east side to the stairs: 12 px drawn from the grass rim "
    "to the dark foot where it runs straight (y 212-223 at x 340), 26 voxels, 2 levels; rounded chunks in two rows. "
    "The pond's brown rim is only 3 px (under half a level): the shore tiles of the ground collection cover it.",
    top="PokeG_Ground_Meadow", bottom="PokeG_Ground_Meadow", body_group=R, tiers=2, rim_kind="grass",
    bumps=(6, 5, 5), cartoon_bumps=(8, 8), bulge=1.3, crevice=0.6, stagger=5, light=0.3, flat={R: (132, 114, 112)})

# ----------------------------------------------------------------------------
# poke_h.png: native, heights at 0.46; poke_b's tileset again.
PH_BANK = L(face_top=((169, 137, 90), E, "earth"), face_light=((148, 104, 65), E, "earth"), face=((127, 92, 59), E, "earth"),
            face_dark=((107, 80, 52), E, "earth"), crevice=((86, 70, 46), E, "earth"), course_gap=((86, 95, 77), E, "earth"),
            foot=((60, 48, 29), E, "earth"), fill=((117, 87, 56), E, "earth"), grass_edge=((78, 160, 56), G, "grass"))
PH_KW = dict(rim_kind="grass", bumps=(9, 7), cartoon_bumps=(16,), bulge=1.0, crevice=0.6, stagger=0, light=0.3,
             flat={E: (117, 87, 56)})
add(LumpyWall, "poke_h", "FarmBank_H1", 1, PH_BANK, "poke_h.png", 16, 0.46, (100, 190, 260, 260),
    "The earth banks between the farm's terraces: 10 px drawn from the rim to the foot (y 212-221 at x 80), 22 "
    "voxels, 1 level; one course.",
    top="PokeH_Ground_Meadow", bottom="PokeH_Ground_Meadow", tiers=1, **PH_KW)
add(LumpyWall, "poke_h", "PondCliff_H3", 3, PH_BANK, "poke_h.png", 16, 0.46, (420, 320, 560, 460),
    "The cliff down to the pond in the southeast: 25 px drawn from the rim to the foot (y 342-366 at x 520 and "
    "540), 54 voxels, 3 levels; two courses, lit along their tops.",
    top="PokeH_Ground_Meadow", bottom="PokeH_Ground_Pond", tiers=2, **PH_KW)

# ----------------------------------------------------------------------------
# poke_i.jpg: 9.5 px a tile, heights at 0.46.
add(with_extras(StripedCliff, WaterfallMixin), "poke_i", "EarthCliff_H3", 3,
    L(face_light=((190, 148, 104), E, "earth"), face=((141, 89, 49), E, "earth"), face_dark=((120, 71, 42), E, "earth"),
      face_line=((100, 66, 42), E, "earth"), face_foot=((108, 76, 50), E, "earth"), fill=((128, 82, 46), E, "earth"),
      grass_edge=((130, 120, 66), G, "grass"), water=((111, 145, 151), W, "water"),
      water_light=((144, 167, 165), W, "water"), foam=((190, 208, 202), W, "foam")),
    "poke_i.jpg", 9.5, 0.46, (230, 260, 360, 340),
    "The orange ledges of the village terraces: 13 px drawn from the rim to the foot (y 288-300 at x 256), 22 "
    "voxels at 9.5 px a tile, 3 levels; a rounded column about a tile (creases at x 254, 266, 276 at y 293). Its "
    "NarrowFall is the spring falling down the ledge into the small pool above the bridge (x 278-290, 6 px wide).",
    top="PokeI_Ground_Meadow", bottom="PokeI_Ground_Meadow", widths=(16,), cartoon_widths=(16,), bulge=1.6,
    round_top=2, extra=("NarrowFall",), plans={"NarrowFall": "Straight"}, bottoms={"NarrowFall": "PokeI_Ground_Pond"},
    fall_w=6, lip=1, flat={E: (141, 89, 49)})

# ----------------------------------------------------------------------------
# poke_j.jpg: 12.25 px a tile, heights at 0.46.
PJ_FACE = L(face_light=((204, 143, 101), E, "earth"), face=((124, 78, 48), E, "earth"), face_dark=((103, 61, 37), E, "earth"),
            face_line=((72, 51, 33), E, "earth"), face_foot=((60, 48, 22), E, "earth"), fill=((110, 70, 42), E, "earth"),
            grass_edge=((94, 110, 45), G, "grass"))
PJ_KW = dict(widths=(16,), cartoon_widths=(16,), bulge=1.6, round_top=2, flat={E: (124, 78, 48)})
add(StripedCliff, "poke_j", "EarthCliff_H3", 3, PJ_FACE, "poke_j.jpg", 12.25, 0.46, (360, 360, 560, 470),
    "The brown ledges between the village's terraces: 18 px drawn from the rim to the dark foot (y 373-390 at x "
    "470), 24 voxels at 12.25 px a tile, 3 levels; a rounded column a tile (creases every 12 px at y 420).",
    top="PokeJ_Ground_Meadow", bottom="PokeJ_Ground_Meadow", **PJ_KW)
add(StripedCliff, "poke_j", "PondBank_H3", 3, PJ_FACE, "poke_j.jpg", 12.25, 0.46, (360, 360, 560, 470),
    "The same face where it drops to the two ponds: 19 px drawn (y 409-427 at x 400, 397-415 at x 520), 3 levels.",
    top="PokeJ_Ground_Meadow", bottom="PokeJ_Ground_Pond", **PJ_KW)

# ----------------------------------------------------------------------------
# poke_k.jpg: 14.75 px a tile, heights at 0.46.
PK_FACE = L(face_light=((211, 138, 91), E, "earth"), face=((131, 82, 48), E, "earth"), face_dark=((106, 65, 41), E, "earth"),
            face_line=((78, 54, 35), E, "earth"), face_foot=((57, 37, 21), E, "earth"), fill=((116, 74, 46), E, "earth"),
            grass_edge=((80, 108, 38), G, "grass"))
PK_KW = dict(widths=(16,), cartoon_widths=(16,), bulge=1.6, round_top=2, flat={E: (131, 82, 48)})
add(StripedCliff, "poke_k", "EarthCliff_H3", 3, PK_FACE, "poke_k.jpg", 14.75, 0.46, (150, 170, 300, 230),
    "The brown ledges stepping down the forest: 23 px drawn from the rim to the dark foot (y 181-203 at x 270), "
    "25 voxels at 14.75 px a tile, 3 levels; a rounded column a tile.",
    top="PokeK_Ground_Meadow", bottom="PokeK_Ground_Meadow", **PK_KW)
add(StripedCliff, "poke_k", "LakeBank_H3", 3, PK_FACE, "poke_k.jpg", 14.75, 0.46, (150, 170, 300, 230),
    "The same face along the north and west shores of the two lakes, 3 levels down to the water.",
    top="PokeK_Ground_Meadow", bottom="PokeK_Ground_Lake", **PK_KW)

# ----------------------------------------------------------------------------
# poke_l.png (a sprite sheet): native, heights at 0.46.
add(with_extras(LumpyWall, NotchMixin), "poke_l", "TerraceBlock_H2", 2,
    L(rim_light=((222, 166, 120), E, "earth"), rim=((190, 127, 80), E, "earth"), face_light=((190, 127, 80), E, "earth"),
      face=((150, 98, 60), E, "earth"), face_dark=((118, 58, 42), E, "earth"), crevice=((93, 48, 39), E, "earth"),
      foot=((78, 41, 35), E, "earth"), fill=((150, 98, 60), E, "earth")),
    "poke_l.png", 16, 0.46, (120, 100, 200, 192),
    "The sheet's grass-topped terrace blocks: a wide band of lumpy earth round the grass on top, the face 12 px "
    "drawn from the band to the outline at the foot (y 146-157 at x 150), 26 voxels, 2 levels; big rounded lumps "
    "lit on top. The mound beside the block is this style's ridge pieces; its gully notch (x 128-160, y 160-176) "
    "is the Notch piece.",
    top="PokeL_Ground_Meadow", bottom="PokeL_Ground_Meadow", tiers=1, rim_kind="rock", rim_h=4, rim=2,
    bumps=(9, 7), cartoon_bumps=(16,), bulge=1.4, crevice=0.6, stagger=0, light=0.35, top_band=8,
    extra=("Notch",), plans={"Notch": "Straight"}, notch_w=10, notch_d=11, flat={E: (190, 127, 80)})

# ----------------------------------------------------------------------------
# poke_m.png: native, heights at 0.5 (its buildings').
PM_ROCK = L(rim_light=((173, 129, 91), E, "earth"), rim=((148, 105, 70), E, "earth"),
            face_light=((167, 125, 87), E, "earth"), face=((148, 105, 70), E, "earth"), face_dark=((125, 82, 53), E, "earth"),
            crevice=((102, 61, 36), E, "earth"), foot=((48, 34, 24), E, "earth"), fill=((140, 98, 64), E, "earth"),
            grass_edge=((99, 189, 97), G, "grass"))
add(with_extras(LumpyWall, WaterfallMixin), "poke_m", "GullyCliff_H3", 3,
    dict(PM_ROCK, water=((87, 160, 137), W, "water"), water_light=((118, 178, 158), W, "water"),
         foam=((243, 250, 249), W, "foam")),
    "poke_m.png", 16, 0.5, (290, 430, 450, 500),
    "The brown earth ledges of the gully and the river's steps: 26 px drawn from the grass rim to the outline at "
    "the foot (y 453-478 at x 420), 52 voxels at 0.5, 3 levels; rounded lumps lit on top. The river spills over "
    "them in three places (x 310-360 at y 432-466 the first).",
    top="PokeM_Ground_Meadow", bottom="PokeM_Ground_Meadow", tiers=2, rim_kind="grass", bumps=(9, 7),
    cartoon_bumps=(16,), bulge=1.4, crevice=0.6, stagger=4, light=0.35, extra=("Fall", "Channel"),
    plans={"Fall": "Straight", "Channel": "Fill"},
    tops={"Fall": "PokeM_Ground_ChannelWater", "Channel": "PokeM_Ground_ChannelWater"},
    bottoms={"Fall": "PokeM_Ground_ChannelWater"}, lip=2, flat={E: (148, 105, 70)})
add(LumpyWall, "poke_m", "RockMountain_H3", 3, PM_ROCK, "poke_m.png", 16, 0.5, (0, 0, 140, 110),
    "The lumpy brown rock masses in the top corners: steps of big rounded lumps, the tallest face 25 px drawn "
    "from the lit top to the outline (y 7-31 at x 40), 50 voxels at 0.5, 3 levels; their tops the rock itself, "
    "lumpy and lit.",
    top=None, bottom="PokeM_Ground_Meadow", tiers=2, rim_kind="rock", rim_h=3, rim=2, bumps=(10, 6),
    cartoon_bumps=(16,), bulge=1.8, crevice=0.8, stagger=5, light=0.35, flat={E: (148, 105, 70)})

# ----------------------------------------------------------------------------
# poke_o.png: native, heights at 0.375 (its buildings').
PO_BANK = L(face_top=((179, 149, 120), E, "earth"), face_light=((175, 112, 92), E, "earth"), face=((115, 85, 62), E, "earth"),
            face_dark=((90, 75, 62), E, "earth"), crevice=((87, 59, 56), E, "earth"), foot=((69, 62, 49), E, "earth"),
            fill=((115, 85, 62), E, "earth"), grass_edge=((111, 179, 88), G, "grass"))
PO_KW = dict(rim_kind="grass", bumps=(6, 5, 5), cartoon_bumps=(8, 8), bulge=1.1, crevice=0.6, stagger=5, light=0.3,
             flat={E: (115, 85, 62)})
add(LumpyWall, "poke_o", "EarthBank_H1", 1, PO_BANK, "poke_o.png", 16, 0.375, (0, 130, 110, 220),
    "The low mauve-brown banks of the forest terraces on the west side: 4 px drawn (y 368-371 at x 80), 11 voxels "
    "at 0.375, 1 level.",
    top="PokeO_Ground_Meadow", bottom="PokeO_Ground_Meadow", tiers=1, **PO_KW)
add(LumpyWall, "poke_o", "EarthLedge_H2", 2, PO_BANK, "poke_o.png", 16, 0.375, (0, 130, 110, 220),
    "The taller ledges of the same terraces: 15 px drawn from the lit rim to the dark foot (y 129-143 at x 40), "
    "40 voxels at 0.375, 2 levels.",
    top="PokeO_Ground_Meadow", bottom="PokeO_Ground_Meadow", tiers=2, **PO_KW)
add(FacetedCliff, "poke_o", "OrangeRock_H5", 5,
    L(block_top=((239, 189, 132), "rock", "orange"), block_light=((231, 181, 123), "rock", "orange"),
      block=((214, 165, 115), "rock", "orange"), block_low=((198, 148, 115), "rock", "orange"),
      crease=((107, 66, 57), "rock", "orange"), foot=((63, 54, 70), "rock", "orange"),
      fill=((201, 151, 114), "rock", "orange")),
    "poke_o.png", 16, 0.375, (0, 520, 120, 640),
    "The orange sandstone outcrop in the bottom-left corner: slabs lit along their tops, the top tier's face 28 px "
    "drawn (y 593-620 at x 10), 75 voxels at 0.375, 5 levels; the frame cuts off the rest. Its top is the rock "
    "itself.",
    top=None, bottom="PokeO_Ground_Meadow", body_group="rock", rows=(12, 16, 10, 14), blocks=((16,), (10, 6), (6, 10), (9, 7)),
    depth=1.4, top_h=2, low_h=4, flat={"rock": (214, 165, 115)})
add(LumpyWall, "poke_o", "PurpleRockPool_H2", 2,
    L(face_light=((145, 94, 109), "rock", "dark"), face=((131, 71, 114), "rock", "dark"),
      face_dark=((90, 65, 103), "rock", "dark"), crevice=((100, 62, 114), "rock", "dark"),
      foot=((63, 54, 70), "rock", "dark"), fill=((110, 68, 108), "rock", "dark"),
      grass_edge=((87, 59, 56), G, "grass")),
    "poke_o.png", 16, 0.375, (370, 560, 540, 640),
    "The purple rock rim of the inland pool at the bottom: 13 px drawn from the grass to the water (y 577-589 at x "
    "470), 35 voxels at 0.375, 2 levels; small rounded stones.",
    top="PokeO_Ground_Meadow", bottom="PokeO_Ground_InlandPool", body_group="rock", tiers=2, rim_kind="grass",
    bumps=(4, 4, 4, 4), cartoon_bumps=(8, 8), bulge=1.0, crevice=0.5, stagger=2, light=0.3,
    flat={"rock": (131, 71, 114)})

# ----------------------------------------------------------------------------
# poke_p.png: native, heights at 0.46.
add(with_extras(LumpyWall, CaveMouthMixin), "poke_p", "GullyWall_H2", 2,
    L(rim_light=((172, 146, 125), R, "rock"), rim=((159, 130, 108), R, "rock"), face_light=((113, 90, 78), R, "rock"),
      face=((101, 77, 63), R, "rock"), face_dark=((68, 58, 64), R, "rock"), crevice=((55, 48, 52), R, "rock"),
      foot=((60, 56, 62), R, "rock"), fill=((101, 77, 63), R, "rock"), cave_dark=((45, 34, 38), D, "dark")),
    "poke_p.png", 16, 0.46, (220, 80, 420, 220),
    "The gray-brown crag walls of the gully down from the house: 16 px drawn from the grass to the gully's gravel "
    "floor (y 95-110 at x 350), 35 voxels, 2 levels, a pale rock rim along the top, deeper parts two such walls a "
    "tile apart (y 114-127 at x 270). Its CaveMouth is the cave at the gully's head (x 287-304, y 108-118).",
    top="PokeP_Ground_Meadow", bottom="PokeP_Ground_RockyGully", body_group=R, tiers=2, rim_kind="rock", rim_h=2,
    rim=2, bumps=(6, 5, 5), cartoon_bumps=(8, 8), bulge=1.4, crevice=0.8, stagger=5, light=0.3,
    extra=("CaveMouth",), plans={"CaveMouth": "Straight"}, mouth_w=12, mouth_h=22, mouth_d=11,
    flat={R: (101, 77, 63)})

# ----------------------------------------------------------------------------
# poke_q.png: native, heights at 0.46.
PQ_ROCK = dict(block_top=((206, 151, 102), R, "orange"), block_light=((173, 127, 67), R, "orange"),
               block=((156, 99, 66), R, "orange"), block_low=((123, 74, 57), R, "orange"),
               crease=((107, 66, 57), R, "orange"), foot=((82, 49, 41), R, "orange"), fill=((148, 90, 66), R, "orange"))
PQ_KW = dict(body_group=R, rows=(10, 8, 12, 9), blocks=((10, 6), (6, 5, 5), (16,), (7, 9)), depth=1.6, top_h=2,
             low_h=3, flat={R: (156, 99, 66)})
add(FacetedCliff, "poke_q", "ClayTerrace_H3", 3, L(grass_edge=((206, 151, 102), "surface", "orange"), **PQ_ROCK),
    "poke_q.png", 16, 0.46, (110, 120, 260, 240),
    "The chunky orange rock between the summit's clay terraces: 24 px drawn from the clay's lit rim to the dark "
    "foot (y 180-206 at x 130), 52 voxels, 3 levels; clay above and below.",
    top="PokeQ_Ground_TerraceClay", bottom="PokeQ_Ground_TerraceClay", **PQ_KW)
add(FacetedCliff, "poke_q", "RockTerrace_H3", 3, L(grass_edge=((86, 138, 77), G, "grass"), **PQ_ROCK),
    "poke_q.png", 16, 0.46, (400, 440, 560, 560),
    "The same rock under the jungle's grass terraces and beside the stairs, 3 levels.",
    top="PokeQ_Ground_Meadow", bottom="PokeQ_Ground_Meadow", **PQ_KW)
add(FacetedCliff, "poke_q", "CoastalCliff_H5", 5, L(grass_edge=((86, 138, 77), G, "grass"), **PQ_ROCK),
    "poke_q.png", 16, 0.46, (60, 600, 240, 720),
    "The coastal cliffs down to the beach: tiers of 34-36 px drawn from the grass rim to the dark foot (y 632-667 "
    "and 668-701 at x 120; 660-712 at x 180), about 75 voxels, 5 levels; sand at the foot.",
    top="PokeQ_Ground_Meadow", bottom="PokeQ_Ground_BeachSand", **PQ_KW)

# ----------------------------------------------------------------------------
# poke_r.png: native, heights at 0.375 (its buildings').
add(StripedCliff, "poke_r", "EarthCliff_H3", 3,
    L(face_light=((177, 119, 79), E, "earth"), face=((148, 99, 65), E, "earth"), face_dark=((107, 74, 57), E, "earth"),
      face_line=((90, 66, 50), E, "earth"), face_foot=((111, 120, 130), R, "rock"), fill=((140, 90, 57), E, "earth"),
      grass_edge=((84, 175, 100), G, "grass")),
    "poke_r.png", 16, 0.375, (160, 30, 440, 110),
    "The terraced ledges north of the village: 16 px of brown face over a 3 px gray stone foot (y 88-106 at x "
    "400), 51 voxels at 0.375, 3 levels; a rounded column a tile (creases every 16 px at y 96).",
    top="PokeR_Ground_Meadow", bottom="PokeR_Ground_Meadow", widths=(16,), cartoon_widths=(16,), bulge=1.4,
    round_top=2, foot_h=8, flat={E: (148, 99, 65), R: (111, 120, 130)})
add(LumpyWall, "poke_r", "RaisedBed_H1", 1,
    L(rim_light=((170, 145, 120), E, "earth"), rim=((163, 138, 114), E, "earth"), face_light=((163, 138, 114), E, "earth"),
      face=((150, 123, 97), E, "earth"), face_dark=((135, 110, 88), E, "earth"), crevice=((120, 99, 84), E, "earth"),
      foot=((100, 82, 70), E, "earth"), fill=((150, 123, 97), E, "earth")),
    "poke_r.png", 16, 0.375, (235, 240, 340, 330),
    "The two raised garden beds in the village: a border of light soil about 5 px wide round the crops, its front "
    "about 4 px drawn, 1 level; the bed's top is the garden soil.",
    top="PokeR_Ground_GardenSoil", bottom="PokeR_Ground_Meadow", tiers=1, rim_kind="rock", rim_h=2, rim=1,
    bumps=(16,), cartoon_bumps=(16,), bulge=0.3, crevice=0.1, stagger=0, light=0.3, top_band=5,
    flat={E: (150, 123, 97)})

# ----------------------------------------------------------------------------
# poke_s.jpg: about 10 px a tile, heights at 0.46.
PS_WATER = dict(water=((64, 163, 200), W, "water"), water_light=((110, 190, 220), W, "water"),
                foam=((215, 235, 240), W, "foam"))
add(with_extras(IslandRim, WaterfallMixin), "poke_s", "IslandRim_H3", 3,
    dict(L(rock_light=((149, 145, 142), R, "rock"), rock=((115, 106, 97), R, "rock"), rock_dark=((99, 91, 88), R, "rock"),
           rock_line=((86, 77, 70), R, "rock"), fill=((105, 100, 92), R, "rock"),
           grass_edge=((91, 161, 72), G, "grass")), **PS_WATER),
    "poke_s.jpg", 10, 0.46, (290, 600, 440, 720),
    "The rim of the floating island: dark gray-brown crags hanging under the grass's edge, 13 px drawn (y 690-702 "
    "at x 360), 21 voxels at 10 px a tile, 3 levels, over the island's gray underside; no ground below. The "
    "rivers pour off it into the clouds (x 108-140 at y 700-740).",
    top="PokeS_Ground_Meadow", bottom=None, body_group=R, row_h=16, crags=(6, 5, 5), cartoon_crags=(8, 8), tuck=2.0,
    point=6, extra=("Fall", "Channel"), plans={"Fall": "Straight", "Channel": "Fill"},
    tops={"Fall": "PokeS_Ground_River", "Channel": "PokeS_Ground_River"}, lip=1, flat={R: (115, 106, 97)})
add(with_extras(LumpyWall, CaveMouthMixin, WaterfallMixin), "poke_s", "Terrace_H2", 2,
    dict(L(face_light=((155, 154, 134), R, "rock"), face=((128, 132, 107), R, "rock"), face_dark=((116, 125, 98), R, "rock"),
           crevice=((100, 101, 80), R, "rock"), foot=((86, 77, 70), R, "rock"), fill=((122, 124, 104), R, "rock"),
           grass_edge=((91, 161, 72), G, "grass"), cave_dark=((40, 36, 30), D, "dark")), **PS_WATER),
    "poke_s.jpg", 10, 0.46, (200, 140, 300, 210),
    "The terraces inside the island: a greenish-gray stone face 7 px drawn under the grass (y 173-179 at x 250), "
    "11 voxels at 10 px a tile, 2 levels. Its CaveMouth is one of the small dark alcoves in these faces (x "
    "220-235, y 165-178); its Fall the rivers stepping down the terraces (x 108-140, y 600-640).",
    top="PokeS_Ground_Meadow", bottom="PokeS_Ground_Meadow", body_group=R, tiers=1, rim_kind="grass",
    bumps=(6, 5, 5), cartoon_bumps=(8, 8), bulge=1.2, crevice=0.6, stagger=5, light=0.3,
    extra=("CaveMouth", "Fall", "Channel"), plans={"CaveMouth": "Straight", "Fall": "Straight", "Channel": "Fill"},
    tops={"Fall": "PokeS_Ground_River", "Channel": "PokeS_Ground_River"}, bottoms={"Fall": "PokeS_Ground_River"},
    mouth_w=12, mouth_h=20, mouth_d=11, lip=1, flat={R: (128, 132, 107)})

# ----------------------------------------------------------------------------
# poke_t.png: native, heights at 0.46.
PT_ROCK = L(rim_light=((173, 129, 91), R, "warm_rock"), rim=((148, 105, 70), R, "warm_rock"),
            face_light=((148, 105, 70), R, "warm_rock"), face=((125, 82, 53), R, "warm_rock"),
            face_dark=((102, 61, 36), R, "warm_rock"), crevice=((80, 52, 32), R, "warm_rock"),
            foot=((42, 32, 24), R, "warm_rock"), fill=((125, 82, 53), R, "warm_rock"))
PT_KW = dict(body_group=R, tiers=2, rim_kind="rock", rim_h=3, rim=2, bumps=(10, 6), cartoon_bumps=(16,), bulge=1.8,
             crevice=0.8, stagger=5, light=0.35, flat={R: (125, 82, 53)})
add(with_extras(LumpyWall, CaveMouthMixin), "poke_t", "CaveWall_H4", 4,
    dict(PT_ROCK, cave_dark=((40, 30, 24), D, "dark")), "poke_t.png", 16, 0.46, (860, 400, 980, 480),
    "The cave's warm brown rock walls, stepping round the chamber: 27 px drawn from the rim to the dark outline (y "
    "384-410 at x 60), 59 voxels, 4 levels; big rounded lumps, the cave's rock on top, its sand below. Its "
    "CaveMouth is the opening in the east wall (x 928-948, y 430-448).",
    top="PokeT_Ground_CaveRock", bottom="PokeT_Ground_CaveSand", extra=("CaveMouth",),
    plans={"CaveMouth": "Straight"}, mouth_w=12, mouth_h=36, mouth_d=11, **PT_KW)
add(LumpyWall, "poke_t", "RockPlatform_H4", 4, PT_ROCK, "poke_t.png", 16, 0.46, (140, 420, 260, 530),
    "The raised rock platforms inside the cave, topped with the damp dark floor and climbed by stairs: about 28 px "
    "drawn (the stairs' rise, y 498-525 at x 190), 61 voxels, 4 levels.",
    top="PokeT_Ground_DampCaveFloor", bottom="PokeT_Ground_CaveSand", **PT_KW)

# ----------------------------------------------------------------------------
# poke_u.jpg: native, heights at 0.4375 (its buildings').
add(with_extras(IslandRim, WaterfallMixin), "poke_u", "IslandRim_H5", 5,
    L(rock_light=((188, 180, 169), R, "rock"), rock=((130, 126, 117), R, "rock"), rock_dark=((96, 92, 83), R, "rock"),
      rock_line=((66, 62, 58), R, "rock"), fill=((117, 114, 105), R, "rock"), grass_edge=((128, 138, 103), G, "grass"),
      water=((62, 160, 199), W, "water"), water_light=((104, 185, 216), W, "water"), foam=((220, 236, 242), W, "foam")),
    "poke_u.jpg", 16, 0.4375, (0, 230, 130, 384),
    "The rims of the floating islands: two rows of pointed gray crags hanging under the grass, 34 px drawn (y "
    "279-312 at x 100), 78 voxels at 0.4375, 5 levels; no ground below. Its NarrowFall is the narrow ribbon of "
    "water off an island's edge, clipped by the frame in the art, so reconstructed.",
    top="PokeU_Ground_Meadow", bottom=None, body_group=R, row_h=38, crags=(8, 8), cartoon_crags=(16,), tuck=2.5,
    point=20, crag_bulge=2.6, lit=12, extra=("NarrowFall",), plans={"NarrowFall": "Straight"}, fall_w=5, lip=1,
    flat={R: (130, 126, 117)})


def prefix(source):
    """The file prefix of an image: poke_n -> PokeN, pixelwood_a -> PixelwoodA, mario -> Mario."""
    head, _, tail = source.partition("_")
    return head.capitalize() + tail.upper()


def by_name(spec):
    """Styles named "<source>:<name>" (or all of a source's, "<source>")."""
    return [s for s in STYLES if spec in (s.source, "%s:%s" % (s.source, s.name))]
