"""Views of the cottage from the files' own builds: Base and Cartoon from the front
left and from the back right. Writes previews/New1_Cottage_views.png.

    python output/new_1/buildings/previews.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for lib in (HERE.parent / "lib", HERE.parents[1] / "new_images" / "lib"):
    if (lib / "fastview.py").exists():
        sys.path.insert(0, str(lib))
        break
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import fastview  # noqa: E402
import palettes  # noqa: E402
import sculpt  # noqa: E402

font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)
rows = []
for cartoon in (False, True):
    m = sculpt.build("Cottage", cartoon)
    w = {p: palettes.LABELS[l][0] for p, l in m.v.items()}
    parts = [fastview.view3d(w, -20, 28, 4.0), fastview.view3d(w, 160, 28, 4.0)]
    row = Image.new("RGB", (sum(p.width for p in parts) + 10, max(p.height for p in parts) + 24), (236, 238, 236))
    x = 0
    for p in parts:
        row.paste(p, (x, 24))
        x += p.width + 10
    ImageDraw.Draw(row).text((4, 2), "New1_Cottage%s: front left, back right" % ("_Cartoon" if cartoon else ""),
                             font=font, fill=(0, 0, 0))
    rows.append(row)
sheet = Image.new("RGB", (max(r.width for r in rows), sum(r.height for r in rows) + 10), (250, 250, 250))
y = 0
for r in rows:
    sheet.paste(r, (0, y))
    y += r.height + 10
(HERE / "previews").mkdir(exist_ok=True)
sheet.save(HERE / "previews" / "New1_Cottage_views.png")
print("Saved previews/New1_Cottage_views.png", sheet.size)
