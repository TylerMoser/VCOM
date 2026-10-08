"""Makes the sheets again from proposals already drawn.

Usage: sheets.py <the pack's folder> <folder holding the kinds' folders> [kind ...]
"""
import os
import sys
from PIL import Image
import kit
import build
import settlements
import markers

kit.PACK, out = sys.argv[1:3]
what = dict(settlements.WHAT)
what.update(markers.WHAT)
for kind in sys.argv[3:] or list(what):
    folder = os.path.join(out, kind)
    names = sorted(n for n in os.listdir(folder) if n.startswith(kind + " ") and n.endswith(".png"))
    icons = [Image.open(os.path.join(folder, n)).convert("RGBA") for n in names]
    maker = markers.sheet_of if kind in markers.SETS else build.sheet_of
    sheet = maker(kind, icons, what[kind])
    sheet.save(os.path.join(folder, "_%s proposals.png" % kind))
    print("%s: %d proposals, sheet %d x %d" % (kind, len(icons), sheet.width, sheet.height))
