"""The poke_c buildings: five families, seven treatments each, 35 complete .vox files
written directly into output/poke_c/. It owns only those 35 files and this folder's
manifest; the poke_c trees and their generator are left alone.

    python output/poke_c/buildings/generate.py [--replace-generated]

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

# Each family, and where the art draws it (poke_c.png, x0 y0 x1 y1, right and
# bottom exclusive): every copy, the first the one modelled from.
FAMILIES = {
    "Cottage": {"title": "Cottage", "regions": [[146, 138, 216, 226], [162, 266, 232, 354], [578, 378, 648, 466],
                                                [34, 298, 104, 386], [162, 378, 232, 466]],
                "drawn": "Five copies: the small slate-roofed house without flower boxes (two partly hidden by a lamp and a bush)."},
    "FlowerBoxCottage": {"title": "Flower-box cottage", "regions": [[50, 154, 120, 242], [546, 250, 616, 338],
                                                                    [690, 250, 760, 338]],
                         "drawn": "Three copies: the same house with flower boxes under its front windows."},
    "Manor": {"title": "Manor", "regions": [[578, 68, 730, 186]],
              "drawn": "The large house at the top right: scalloped slate roof, barrel dormer, double door under a hood, "
                       "a half-timbered wing on the left, a bay on the right."},
    "BridgePavilion": {"title": "Bridge pavilion", "regions": [[284, 318, 372, 450], [412, 318, 500, 450]],
                       "drawn": "Two identical pavilions eight tiles apart on the covered bridge over the river."},
    "BridgeSpan": {"title": "Bridge span", "regions": [[362, 364, 422, 446]],
                   "drawn": "The arched stone span between the two pavilions, its railed walkway."},
}

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
palette_sha = lambda pal: hashlib.sha256(b"".join(bytes(c) for c in pal)).hexdigest()


def filename(kind, style):
    return "PokeC_%s%s.vox" % (kind, "" if style == "Base" else "_" + style)


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
            voxels = {p: palettes.paint(style, label) for p, label in m.v.items()}
            pal, glass = palettes.palette_of(style)
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
            labels_glass = {palettes.paint(style, l) for l in set(m.v.values()) if palettes.LABELS[l][1] == "glass"}
            assert set(glass_used) == labels_glass, (name, glass_used, labels_glass)
            if "CratePalette" in style:
                assert palette_sha(saved_pal) == palettes.CRATE["palette_sha256"], name
            if "TwoColor" in style:
                groups = {palettes.LABELS[l][1] for l in set(m.v.values())}
                assert len(used) == len(groups), (name, used, groups)
            rows.append({
                "file": name, "family": "PokeC_" + kind, "style": style, "canvas": list(m.size),
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
            groups.setdefault(palettes.LABELS[l][1], []).append(l)
        families.append({
            "asset_id": "PokeC_" + kind, "kind": kind, "title": info["title"], "drawn": info["drawn"],
            "source_regions_xyxy_exclusive": info["regions"], "canvas_xyz": list(base.size),
            "footprint_tiles": sorted([list(t) for t in base.footprint]),
            "doors": [list(d) for d in base.doors],
            "labels_by_group": groups,
            "minimal_colours": {g: list(palettes.GROUPS[g]) for g in groups},
            "crate_group_indices": {g: palettes.CRATE_GROUP_INDEX[g] for g in groups},
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
        "source_image": "poke_c.png", "source_sha256": sha(WORK / "poke_c.png"),
        "generator_sha256": sha(Path(__file__)),
        "dependencies": {f: sha(HERE / f) for f in ("sculpt.py", "palettes.py", "voxlib.py")},
        "crate_palette": "knowledge/palettes/crate-palette.json", "crate_palette_sha256": palettes.CRATE["palette_sha256"],
        "base_palette_sha256": palette_sha(palettes.BASE_PALETTE),
        "minimal_palette_sha256": palette_sha(palettes.GROUP_PALETTE),
        "scale": 0.0625, "front": "local -Y (Godot +Z)", "scene_translation": "0 0 floor(canvas height / 2)",
        "grid": "tile boundaries at x = 8 + 16i, y = 8 + 16j; levels z = 16k; level 0 the floor; walls two voxels "
                "thick across their boundary",
        "delivery": "Complete buildings only, one .vox per treatment; no cell files or brushes.",
        "command": "python output/poke_c/buildings/generate.py",
        "families": families, "models": rows,
    }
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print("Generated and checked %d files in %d families." % (len(rows), len(families)))


if __name__ == "__main__":
    main()
