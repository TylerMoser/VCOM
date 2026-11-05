"""Reference sheets: each image with the regions its families are read from drawn
over it, labelled (new_1: every copy of each element, the cottage, and the HUD left
out in red; new_2: every sprite box). Writes output/new_1/elements/reference/
new_1_regions.png and output/new_2/elements/reference/new_2_boxes.png.
    python output/new_images/refsheets.py [--out <folder holding new_1/ and new_2/>]"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import catalogue_new1 as C1  # noqa: E402

W = Path(r"C:/Users/tandm/Documents/Projects/VoxelRidgeInspiration")
base = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else Path(__file__).resolve().parent.parent
out1 = base / "new_1" / "elements" / "reference"
out2 = base / "new_2" / "elements" / "reference"
for o in (out1, out2):
    o.mkdir(parents=True, exist_ok=True)
font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
COLS = [(255, 220, 0), (0, 230, 255), (255, 120, 255), (120, 255, 120), (255, 160, 60), (160, 160, 255)]

# new_1: twice its size, each family's regions in one colour, numbered
im = Image.open(W / "new_1.jpg").convert("RGB")
S = 2
big = im.resize((im.width * S, im.height * S), Image.NEAREST)
d = ImageDraw.Draw(big)
entries = [(f["name"], f["regions"]) for f in C1.F] + [("Cottage", C1.COTTAGE["regions"])]
for k, (name, regions) in enumerate(entries):
    col = COLS[k % len(COLS)]
    for j, (x0, y0, x1, y1) in enumerate(regions):
        d.rectangle([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], outline=col, width=2)
        label = "%d %s" % (k + 1, name) if j == 0 else "%d" % (k + 1)
        d.text((x0 * S + 3, y0 * S + 2), label, font=font, fill=col, stroke_width=2, stroke_fill=(0, 0, 0))
for name, (x0, y0, x1, y1) in C1.HUD_LEFT_OUT.items():
    d.rectangle([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], outline=(255, 40, 40), width=3)
    d.text((x0 * S + 3, y0 * S + 2), "HUD (%s): left out" % name, font=font, fill=(255, 60, 60),
           stroke_width=2, stroke_fill=(0, 0, 0))
big.save(out1 / "new_1_regions.png")
print(out1 / "new_1_regions.png", big.size)

# new_2: three times its size, every box
B = json.loads((Path(__file__).resolve().parent / "lib" / "boxes_new2.json").read_text())
im = Image.open(W / "new_2.jpg").convert("RGB")
S = 3
big = im.resize((im.width * S, im.height * S), Image.NEAREST)
d = ImageDraw.Draw(big)
small = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
seen = set()
for k, (name, (x0, y0, x1, y1)) in enumerate(sorted(B.items())):
    if (x0, y0, x1, y1) in seen:
        continue
    seen.add((x0, y0, x1, y1))
    col = COLS[k % len(COLS)]
    d.rectangle([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], outline=col, width=2)
    d.text((x0 * S + 2, y0 * S + 1), name, font=small, fill=col, stroke_width=2, stroke_fill=(0, 0, 0))
big.save(out2 / "new_2_boxes.png")
print(out2 / "new_2_boxes.png", big.size)
