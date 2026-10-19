"""After a full render: a contact sheet of every proposal at one view, and the costs the probe logged as
a Markdown table.

  py -3.14 finish.py sheet <MapStyles folder> <panel 0-3> <out.png> [columns] [scale]
      Every NN-*.png (00 to 89; not 90 and up, which are checks) cut to one of its four panels, scaled,
      with its number and name under it, in a grid. A style whose panels are not the standard four
      (06, 17, 21) is shown with its own panel of that place, and the label says which.

  py -3.14 finish.py costs <render log>
      The probe's lines turned into a table: the time the style took to apply as the map loads, and
      each view's GPU time and draw calls.

  py -3.14 finish.py compare <out.png> <panel 0-3> <label>=<picture>[@<panel>] [...]
      One panel of each picture, at full size, two to a row, each labelled in its top right corner:
      the same view of the map now and under some variants, as the revisited 10, 14 and 19 were
      compared. A picture followed by @ and a number gives that panel of it instead.

Needs Pillow (py -3.14 on this machine).
"""
import glob
import os
import re
import sys
from PIL import Image, ImageDraw, ImageFont

PANEL_W, PANEL_H, GAP = 1280, 720, 8
## Styles whose panels are not the standard four, and what their panels show.
SPECIAL = {
    "06": ["Realm", "Duchy tier", "the Swamp's coast, 80 mi", "the Swamp's coast, 30 mi"],
    "17": ["Travel mode, 180 mi", "Political mode, 180 mi", "Terrain mode, 180 mi", "Danger mode, 180 mi"],
    "21": ["180 mi", "180 mi, deuteranopia", "80 mi", "80 mi, deuteranopia"],
}


def panel(image, index):
    x = (index % 2) * (PANEL_W + GAP)
    y = (index // 2) * (PANEL_H + GAP)
    return image.crop((x, y, x + PANEL_W, y + PANEL_H))


def font(size):
    for name in ("segoeuisb.ttf", "segoeui.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def style_names():
    """Each style's NAME, by its number, read from the style scripts beside this folder."""
    names = {}
    styles = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "styles")
    for path in glob.glob(os.path.join(styles, "[0-9][0-9]_*.gd")):
        with open(path, encoding="utf-8") as f:
            m = re.search(r'^const NAME := "([^"]+)"', f.read(), re.M)
        if m:
            names[os.path.basename(path)[:2]] = m.group(1)
    return names


def sheet(folder, index, out, columns=5, scale=0.5):
    names = style_names()
    files = sorted(f for f in glob.glob(os.path.join(folder, "[0-9][0-9]-*.png")) if int(os.path.basename(f)[:2]) < 90)
    w, h = int(PANEL_W * scale), int(PANEL_H * scale)
    label_h = 30
    rows = (len(files) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * w + (columns + 1) * 10, rows * (h + label_h) + (rows + 1) * 10), (24, 25, 30))
    draw = ImageDraw.Draw(canvas)
    text = font(17)
    for n, path in enumerate(files):
        base = os.path.basename(path)[:-4]
        number, name = base[:2], base[3:].replace("-", " ")
        image = Image.open(path)
        which = index
        if image.size[1] < PANEL_H * 2:
            which = min(index, 1)
        thumb = panel(image, which).resize((w, h), Image.LANCZOS)
        x = 10 + (n % columns) * (w + 10)
        y = 10 + (n // columns) * (h + label_h + 10)
        canvas.paste(thumb, (x, y))
        label = "%s  %s" % (number, names.get(number, name.capitalize()))
        if number in SPECIAL:
            label += "  (%s)" % SPECIAL[number][which]
        draw.text((x + 2, y + h + 4), label, fill=(235, 235, 230), font=text)
    canvas.save(out, optimize=True)
    print("wrote", out, canvas.size, "from", len(files), "pictures")


def costs(log):
    rows = []
    current = None
    with open(log, encoding="utf-8", errors="replace") as f:
        for line in f:
            # "style 07  Forest symbols", or a variant's label: "style 14 now  The map as it is now".
            m = re.search(r"MapStyleProbe: style (.+?)  (.*)$", line)
            if m:
                current = {"id": m.group(1), "name": m.group(2).strip(), "apply": "", "ready": "", "views": {}}
                rows.append(current)
                continue
            if current is None:
                continue
            m = re.search(r"the style applied in ([\d.]+) ms", line)
            if m:
                current["apply"] = m.group(1)
            m = re.search(r"runtime part readied in ([\d.]+) ms", line)
            if m:
                current["ready"] = m.group(1)
            m = re.search(r"view (\S+)\s+zoom [\d.]+\s+cpu ([\d.]+) ms\s+gpu ([\d.]+) ms\s+draw calls (\d+)", line)
            if m:
                current["views"].setdefault(m.group(1), (m.group(3), m.group(4)))
    print("| # | Proposal | Applied at load | Runtime nodes ready | GPU A | GPU B | GPU C | GPU D | Draw calls A / B / C / D |")
    print("|---|---|---:|---:|---:|---:|---:|---:|---|")
    for r in rows:
        v = r["views"]
        keys = list(v.keys())
        gpus = [v[k][0] + " ms" for k in keys[:4]] + [""] * (4 - min(4, len(keys)))
        calls = " / ".join(v[k][1] for k in keys[:4])
        print("| %s | %s | %s | %s | %s | %s |" % (
            r["id"], r["name"], (r["apply"] + " ms") if r["apply"] else "", (r["ready"] + " ms") if r["ready"] else "—",
            " | ".join(gpus), calls))


def compare(out, index, items):
    pictures = [item.split("=", 1) for item in items]
    columns = 2 if len(pictures) > 1 else 1
    rows = (len(pictures) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * PANEL_W + (columns - 1) * GAP, rows * PANEL_H + (rows - 1) * GAP), (24, 25, 30))
    text = font(22)
    for n, (label, path) in enumerate(pictures):
        which = index
        if re.search(r"@\d$", path):
            path, which = path[:-2], int(path[-1])
        view = panel(Image.open(path).convert("RGB"), which)
        # In the top right corner: the clock is in the top left, the caption in the bottom left.
        draw = ImageDraw.Draw(view)
        width = draw.textlength(label, font=text)
        draw.rectangle([PANEL_W - width - 22, 0, PANEL_W, 36], fill=(24, 25, 30))
        draw.text((PANEL_W - width - 11, 3), label, fill=(240, 240, 235), font=text)
        canvas.paste(view, ((n % columns) * (PANEL_W + GAP), (n // columns) * (PANEL_H + GAP)))
    canvas.save(out, optimize=True)
    print("wrote", out, canvas.size)


if __name__ == "__main__":
    if sys.argv[1] == "sheet":
        sheet(sys.argv[2], int(sys.argv[3]), sys.argv[4],
              int(sys.argv[5]) if len(sys.argv) > 5 else 5, float(sys.argv[6]) if len(sys.argv) > 6 else 0.5)
    elif sys.argv[1] == "compare":
        compare(sys.argv[2], int(sys.argv[3]), sys.argv[4:])
    else:
        costs(sys.argv[2])
