"""Every element of new_1.jpg, a scene of pixel art enlarged 4.6 times (a tile 16
of its art pixels, 73.6 of the image's): what it is, where the image draws it (each
copy, in the image's own pixels, x0 y0 x1 y1, right and bottom exclusive), and
the builder that makes it. The cottage is made by cottage/generate.py, the ground
tiles by new1_ground.py (the ground collection's own code); everything else here.

Left out, by the user's call (2026-11-04): the HUD over the scene (the three hearts,
the d-pad and arrow icons, the item bubble with its small table and Y button, the
corner logo). The fairy's sparkles are an effect, and the shadows under things are
the light's: neither is modelled. The scene's elements (the user's call: every one,
the four figures included, as static figures):"""

F = []


def fam(name, builder, what, regions, layer):
    F.append(dict(name=name, builder=builder, what=what, regions=regions, layer=layer))


fam("OliveConeTree", "new1_sculpt.cone_tree",
    "the olive cone tree: a straight cone, lit on its left, dark leaf-marks on it and a pale cap at its tip, over a "
    "skirt of two tiers of round scalloped leaves, a short red-brown trunk and spreading roots (drawn eight times, "
    "every one cut off by the image's edge or overlapped by a neighbour or the HUD; the second from the left at the "
    "top the clearest)",
    [[69, 23, 183, 197], [0, 0, 115, 150], [495, 0, 620, 86], [575, 0, 700, 161], [0, 541, 58, 736],
     [23, 610, 150, 736], [586, 644, 690, 736], [667, 587, 736, 736]], "Vegetation")
fam("TallGrass", "new1_plants.tall_grass",
    "a tile of the tall leafy grass (the strip at the top, the patch at the left: one tile of it, repeated)",
    [[0, 160, 78, 295], [260, 15, 470, 95]], "Vegetation")
fam("SmallYellowFlower", "new1_plants.small_flower",
    "the small yellow flower in front of the tall grass: five petals round a cream heart",
    [[38, 265, 64, 294]], "Vegetation")
fam("TinySprout", "new1_sculpt.sprout",
    "the tiny two-leaved sprout (drawn three times: in the grass, and twice in the moss on the roof, which the "
    "cottage holds)", [[24, 428, 62, 454], [185, 118, 220, 138], [170, 195, 205, 212]], "Vegetation")
fam("BroadLeafPlant", "new1_sculpt.rosette",
    "the broad-leaved plant: five broad oval leaves round a dark heart (drawn three times, beside the house)",
    [[70, 295, 182, 378], [540, 230, 645, 305], [540, 300, 645, 375]], "Vegetation")
fam("PlanterPlant", "new1_sculpt.planter_plant",
    "the small jagged-leaved plant in the house's flower box (drawn twice; the cottage holds both)",
    [[222, 345, 262, 395], [265, 345, 305, 395]], "Vegetation")
fam("RoofFlowerPlant", "new1_plants.roof_plant",
    "the low flowering plant on the roof: round leaves and three yellow star flowers (the cottage holds it too)",
    [[190, 212, 295, 280]], "Vegetation")
fam("CoralFlower", "new1_plants.flower6",
    "the six-petalled coral-red flower (drawn twice in the grass)", [[450, 455, 515, 505], [497, 685, 592, 736]],
    "Vegetation")
fam("BlueFlower", "new1_plants.flower6_blue",
    "the six-petalled blue flower: the coral flower's shape in blue (drawn three times in the grass)",
    [[665, 440, 720, 495], [685, 495, 736, 550], [420, 645, 480, 702]], "Vegetation")
fam("Woodpile", "new1_props.woodpile",
    "the woodpile beside the house: three stripped logs side by side, ringed ends, two boards across them",
    [[80, 170, 182, 300]], "Props")
fam("ChoppingStump", "new1_props.stump_axe",
    "the chopping stump with an axe stuck in its top", [[40, 372, 182, 492]], "Props")
fam("Hero", "new1_figures.hero",
    "the hooded hero on the path, a golden staff in his hand (a static figure)", [[325, 520, 405, 615]], "Figures")
fam("Fairy", "new1_figures.fairy",
    "the yellow fairy floating beside the hero (a static figure; it floats about 6 voxels up, lift it when placing "
    "it)", [[410, 535, 475, 595]], "Figures")
fam("CrestedCreature", "new1_figures.creature",
    "the green crested creature by the flowers: an orange crest, yellow and blue feathers, a cape and scarf (a "
    "static figure)", [[538, 405, 648, 548]], "Figures")
fam("Crow", "new1_figures.crow", "the crow perched on the roof, facing right (a static figure)",
    [[450, 162, 528, 236]], "Figures")

# Made elsewhere, listed for the record.
COTTAGE = dict(name="Cottage", regions=[[175, 100, 550, 475]],
               what="the cottage: blue-grey stone walls and corner pillars, a flat roof of tan stone with a parapet, "
                    "moss, a flowering plant and a chimney, the arched door with a doorstep, two dark windows over "
                    "flower boxes")
GROUND = ["Meadow", "LightMeadow", "SandPath", "PathEdge", "PathOuterCorner", "PathInnerCorner",
          "LightPatchEdge", "LightPatchOuterCorner", "LightPatchInnerCorner"]
HUD_LEFT_OUT = dict(hearts=[0, 0, 75, 25], dpad=[0, 50, 115, 105], bubble=[585, 15, 685, 105],
                    logo=[690, 715, 736, 736])
