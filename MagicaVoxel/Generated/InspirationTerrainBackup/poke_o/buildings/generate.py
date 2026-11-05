"""The poke_o buildings: three families, seven treatments each, 21 complete .vox
files written directly into output/poke_o/. It owns only those 21 files and this
folder's manifest; every other file in output/poke_o/ (ChatGPT's trees, palms and
plants, the vegetation, rocks, deadwood, fences, ground and props another agent
added, their records) is left alone.

    python output/poke_o/buildings/generate.py [--replace-generated]

A file already there is overwritten only if it is still exactly what this generator
wrote last time (its hash in manifest.json); anything else, a hand edit included,
stops the run unless --replace-generated is given. Every file is read back and
checked: its size, voxels and palette as intended, glass written as MagicaVoxel
Glass on its own indices, index 255 (the game's blood) never used, the recolours'
voxels exactly their Base's or Cartoon's, the crate palette byte for byte.
"""
import argparse
import hashlib
import json
from pathlib import Path

import palettes
import sculpt
from voxlib import components, read, write

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WORK = ROOT.parent.parent
STYLES = ["Base", "Cartoon", "CratePalette", "TwoColor", "Cartoon_TwoColor", "CratePalette_TwoColor",
          "Cartoon_CratePalette_TwoColor"]

# Each family, and where the art draws it (poke_o.png, x0 y0 x1 y1, right and
# bottom exclusive, in its own pixels: a tile is 16): every copy, the first the one
# modelled from.
FAMILIES = {
    "GableHouse": {"title": "Gabled house",
                   "regions": [[172, 2, 244, 80], [444, 402, 516, 480], [140, 370, 212, 448]],
                   "drawn": "Three copies of the gabled house: a pink front gable roof with its ridge front to back in "
                            "stripes under a light band, a dormer with a triangular window on its left slope, a khaki "
                            "gable with a small window over a light board, cream walls, the red door and a window, a "
                            "teal strip along the foot."},
    "SkylightHouse": {"title": "Skylight house", "regions": [[172, 196, 244, 274], [316, 276, 388, 354]],
                      "drawn": "Two copies of the skylight house: a pink split roof, flat on the right with a skylight "
                               "in it and on the left a facet in courses sloping down to its eave; a band of wall with "
                               "a small high window under its front edge, a light board, cream walls, the red door and "
                               "a window, a teal strip along the foot."},
    "WideHouse": {"title": "Wide house", "regions": [[346, 66, 452, 162]],
                  "drawn": "The wide house at the top right: the skylight house's split roof six tiles wide with two "
                           "grey rooftop units on its flat part; in front of its middle a wing under a lower split "
                           "roof, the red door in it, a mailbox and a small tree before it; two high windows over a "
                           "window on the main block's front, cream walls, a teal strip along the foot."},
}

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
palette_sha = lambda pal: hashlib.sha256(b"".join(bytes(c) for c in pal)).hexdigest()


def family_name(kind):
    return "PokeO_" + kind


def filename(kind, style):
    return "%s%s.vox" % (family_name(kind), "" if style == "Base" else "_" + style)


def storeys_record(m):
    return [{"stand_level": s["stand"], "tiles": sorted([list(t) for t in s["tiles"]]),
             "entered_by": s["entry"] or "closed off (no way up drawn)", "cut_away_from": s["cut"]}
            for s in m.storeys]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replace-generated", action="store_true")
    args = parser.parse_args()
    old = json.loads((HERE / "manifest.json").read_text()) if (HERE / "manifest.json").exists() else {"models": []}
    previous = {r["file"]: r["sha256"] for r in old["models"]}
    rows, families = [], []
    for kind, info in FAMILIES.items():
        models = {False: sculpt.build(kind, False), True: sculpt.build(kind, True)}
        for cartoon, m in models.items():
            sizes = components(m.v)
            assert len(sizes) == 1, (kind, cartoon, "is not one connected model", sizes[:5])
            assert min(z for (_, _, z) in m.v) == 0
        for style in STYLES:
            m = models["Cartoon" in style]
            voxels = {p: palettes.paint(style, label, kind) for p, label in m.v.items()}
            pal, glass = palettes.palette_of(style, kind)
            glass = {i: t for i, t in glass.items() if i in set(voxels.values())}
            name = filename(kind, style)
            dest = ROOT / name
            if dest.exists() and not args.replace_generated:
                assert previous.get(name) == sha(dest), "%s is not what this generator wrote last: keep it, or pass --replace-generated" % name
            write(dest, m.size, voxels, pal, glass)
            size, saved, saved_pal, mats = read(dest)
            assert tuple(size) == m.size and saved == voxels and saved_pal == list(pal), name
            assert 255 not in saved.values()
            used = sorted(set(saved.values()))
            glass_used = sorted(i for i in used if mats.get(i, {}).get("_type") == "_glass")
            labels_glass = {palettes.paint(style, l, kind) for l in set(m.v.values()) if palettes.LABELS[l][1] == "glass"}
            assert set(glass_used) == labels_glass, (name, glass_used, labels_glass)
            if "CratePalette" in style:
                assert palette_sha(saved_pal) == palettes.CRATE["palette_sha256"], name
            if "TwoColor" in style:
                groups = palettes.groups_used(set(m.v.values()), kind)
                assert len(used) == len(groups), (name, used, groups)
            rows.append({
                "file": name, "family": family_name(kind), "style": style, "canvas": list(m.size),
                "occupied_min": [min(q[a] for q in saved) for a in range(3)],
                "occupied_max": [max(q[a] for q in saved) for a in range(3)],
                "voxels": len(saved), "sha256": sha(dest), "palette_sha256": palette_sha(saved_pal),
                "used_indices": used, "used_rgba": [list(saved_pal[c - 1]) for c in used],
                "glass_indices": {str(i): float(mats[i]["_trans"]) for i in glass_used},
                "glass_voxels": sum(1 for c in saved.values() if c in glass_used),
                "geometry_source": filename(kind, "Cartoon" if "Cartoon" in style else "Base"),
            })
        base, cart = models[False], models[True]
        groups = {}
        for l in sorted(set(base.v.values()) | set(cart.v.values())):
            groups.setdefault(palettes.resolve_group(kind, palettes.LABELS[l][1]), []).append(l)
        families.append({
            "asset_id": family_name(kind), "kind": kind, "title": info["title"], "drawn": info["drawn"],
            "source_regions_xyxy_exclusive": info["regions"], "canvas_xyz": list(base.size),
            "footprint_tiles": sorted([list(t) for t in base.footprint]),
            "doors": [list(d) for d in base.doors],
            "storeys": storeys_record(base),
            "stair_tiles": {"%d,%d" % t: lv for t, lv in sorted(base.stairs.items())},
            "labels_by_group": groups,
            "minimal_colours": {g: list(palettes.GROUPS[kind][g]) for g in groups},
            "folded_groups": {g: c[1:] for g, c in palettes.GROUPS[kind].items() if isinstance(c, str)},
            "crate_group_indices": {g: palettes.crate_group_index(kind, g) for g in groups},
            "crate_label_indices": {l: palettes.CRATE_INDEX[l] for gl in groups.values() for l in gl},
        })
    by_name = {r["file"]: r for r in rows}
    for r in rows:
        src = by_name[r["geometry_source"]]
        r["geometry_source_sha256"] = src["sha256"]
        _, a, _, _ = read(ROOT / r["file"])
        _, b, _, _ = read(ROOT / r["geometry_source"])
        assert a.keys() == b.keys(), r["file"]
    for kind in FAMILIES:
        _, a, _, _ = read(ROOT / filename(kind, "Base"))
        _, b, _, _ = read(ROOT / filename(kind, "Cartoon"))
        assert a.keys() != b.keys(), kind + ": Cartoon must change the shape, not only the paint"
    manifest = {
        "source_image": "poke_o.png", "source_sha256": sha(WORK / "poke_o.png"),
        "generator_sha256": sha(Path(__file__)),
        "dependencies": {f: sha(HERE / f) for f in ("sculpt.py", "palettes.py", "voxlib.py")},
        "crate_palette": "knowledge/palettes/crate-palette.json", "crate_palette_sha256": palettes.CRATE["palette_sha256"],
        "base_palette_sha256": palette_sha(palettes.BASE_PALETTE),
        "minimal_palette_sha256": {k: palette_sha(palettes.group_palette(k)) for k in FAMILIES},
        "scale": 0.0625, "front": "local -Y (Godot +Z)", "scene_translation": "0 0 floor(canvas height / 2)",
        "grid": "tile boundaries at x = 8 + 16i, y = 8 + 16j; levels z = 16k; level 0 the floor; walls two voxels "
                "thick across their boundary",
        "delivery": "Complete buildings only, one .vox per treatment; no cell files or brushes.",
        "command": "python output/poke_o/buildings/generate.py",
        "families": families, "models": rows,
    }
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print("Generated and checked %d files in %d families." % (len(rows), len(families)))


if __name__ == "__main__":
    main()
