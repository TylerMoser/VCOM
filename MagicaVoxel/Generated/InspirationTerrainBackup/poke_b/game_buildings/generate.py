"""The poke_b game-ready buildings: six families, seven treatments each, 42 complete
.vox files written directly into output/poke_b/ beside ChatGPT's poke_b buildings,
under names of their own (PokeB_Game...: the user's choice, 2026-10-28, to keep
both). It owns only those 42 files and this folder's manifest; ChatGPT's
buildings, the trees, the lantern and their records are left alone.

    python output/poke_b/game_buildings/generate.py [--replace-generated]

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

# Each family, and where the art draws it (poke_b.png, x0 y0 x1 y1, right and
# bottom exclusive).
FAMILIES = {
    "DomeLab": {"title": "Domed lab", "regions": [[222, 244, 356, 404]],
                "drawn": "The large building at the top left: two storeys under a flat red roof inside a parapet with a "
                         "raised middle, a dome with a glazed band, fluted corner pilasters, a glass door under a sign."},
    "RedClinic": {"title": "Red clinic", "regions": [[410, 288, 528, 400]],
                  "drawn": "The red-roofed building at the top middle: a white parapet, a skylight, dark corner pillars, a "
                           "red portico over the door with a roundel on it, a sign, a tank and a dark teal window."},
    "GrayEntryHouse": {"title": "Gray mansard house with a door", "regions": [[282, 464, 372, 580]],
                       "drawn": "The middle house: a grey mansard storey with two dormers and a chimney over tan boards on "
                                "a stone base; a door up a stair, a window, a shallow bay."},
    "GrayWindowHouse": {"title": "Gray mansard house with three windows", "regions": [[394, 464, 484, 566]],
                        "drawn": "The house to its right: the same mansard storey over brown boards with three windows "
                                 "and two shutters, no door on its front."},
    "CyanEntryHouse": {"title": "Cyan mansard house", "regions": [[188, 640, 276, 760]],
                       "drawn": "The house at the bottom left: the middle house again, its mansard teal, its boards "
                                "brown, its door orange."},
    "FlowerCottage": {"title": "Flower cottage", "regions": [[408, 636, 524, 742]],
                      "drawn": "The cottage at the bottom right: cream walls, a bell-cast roof with two roof lights, "
                               "flower boxes under the upper windows, a hooded door and bay, an outside stair on its "
                               "right."},
}

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
palette_sha = lambda pal: hashlib.sha256(b"".join(bytes(c) for c in pal)).hexdigest()


def family_name(kind):
    return "PokeB_Game" + kind


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
        "source_image": "poke_b.png", "source_sha256": sha(WORK / "poke_b.png"),
        "generator_sha256": sha(Path(__file__)),
        "dependencies": {f: sha(HERE / f) for f in ("sculpt.py", "palettes.py", "voxlib.py")},
        "crate_palette": "knowledge/palettes/crate-palette.json", "crate_palette_sha256": palettes.CRATE["palette_sha256"],
        "base_palette_sha256": palette_sha(palettes.BASE_PALETTE),
        "minimal_palette_sha256": {k: palette_sha(palettes.group_palette(k)) for k in FAMILIES},
        "scale": 0.0625, "front": "local -Y (Godot +Z)", "scene_translation": "0 0 floor(canvas height / 2)",
        "grid": "tile boundaries at x = 8 + 16i, y = 8 + 16j; levels z = 16k; level 0 the floor; walls two voxels "
                "thick across their boundary",
        "delivery": "Complete buildings only, one .vox per treatment; no cell files or brushes.",
        "beside": "ChatGPT's poke_b buildings (PokeB_DomeLab and the rest, output/poke_b/buildings/) are kept as they "
                  "were: these are the game-ready redo, named PokeB_Game..., the user's choice to keep both.",
        "command": "python output/poke_b/game_buildings/generate.py",
        "families": families, "models": rows,
    }
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print("Generated and checked %d files in %d families." % (len(rows), len(families)))


if __name__ == "__main__":
    main()
