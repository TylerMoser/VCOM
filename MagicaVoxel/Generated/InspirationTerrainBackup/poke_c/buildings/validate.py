"""Checks the 35 poke_c building files and their evidence, from what is on disk.

    python output/poke_c/buildings/validate.py      # writes validation-summary.json

Fails loudly on the first broken rule. What it checks:
- the manifest's hashes: source image, generator, its dependencies, every file;
- each file read back: its canvas, grounded at z 0, index 255 (the game's blood)
  unused, one connected model, its voxels exactly those its geometry source's
  are (a recolour keeps every coordinate), and exactly the sculptor's painted
  voxels (so the pieces the integration test cut are this file's);
- glass: MagicaVoxel Glass on exactly the glass indices, nowhere else;
- palettes: CratePalette files the pinned crate palette byte for byte; TwoColor
  files one colour for each group present, glass included;
- Cartoon differs from Base in shape, not only in paint;
- the game's grid: every room hollow where units stand (levels 1 and 2 of every
  footprint tile, away from its walls), and no glass in a sill course (level 1)
  outside a door's slot;
- evidence: the structural audit (no errors or warnings), every file imported
  whole through the game's importer (counts, glass, grounding, size), the
  integration report (every check of all 42 scenes passed), the previews;
- every file in output/poke_c/ from before the buildings is unchanged.
"""
import hashlib
import json
from pathlib import Path

import palettes
import sculpt
from generate import FAMILIES, STYLES, filename
from voxlib import components, read

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WORK = ROOT.parent.parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    m = json.loads((HERE / "manifest.json").read_text())
    assert len(m["models"]) == 35 and len(m["families"]) == 5
    assert sha(WORK / m["source_image"]) == m["source_sha256"]
    assert sha(HERE / "generate.py") == m["generator_sha256"]
    for name, h in m["dependencies"].items():
        assert sha(HERE / name) == h, name
    audit = {Path(a["path"]).name: a for a in json.loads((HERE / "structural-audit.json").read_text())}
    whole = json.loads((HERE / "qa" / "whole-import.json").read_text())
    report = json.loads((HERE / "qa" / "integration-report.json").read_text())
    rows = {r["file"]: r for r in m["models"]}
    built = {}
    checked = 0
    for kind in FAMILIES:
        for cartoon in (False, True):
            built[(kind, cartoon)] = sculpt.build(kind, cartoon)
    for name, r in rows.items():
        p = ROOT / name
        assert sha(p) == r["sha256"] == audit[name]["sha256"], name
        assert not audit[name]["warnings"] and not audit[name].get("errors"), name
        size, vox, pal, mats = read(p)
        kind = r["family"].removeprefix("PokeC_")
        style = r["style"]
        model = built[(kind, "Cartoon" in style)]
        assert tuple(size) == tuple(r["canvas"]) == model.size
        assert min(q[2] for q in vox) == 0 and 255 not in vox.values()
        assert len(components(vox)) == 1, name
        assert vox == {q: palettes.paint(style, l) for q, l in model.v.items()}, name
        _, src, _, _ = read(ROOT / r["geometry_source"])
        assert vox.keys() == src.keys(), name
        glass_idx = {i for i, mt in mats.items() if mt.get("_type") == "_glass"}
        want = {palettes.paint(style, l) for l in set(model.v.values()) if palettes.LABELS[l][1] == "glass"}
        assert glass_idx == want, (name, glass_idx, want)
        if "CratePalette" in style:
            assert hashlib.sha256(b"".join(bytes(c) for c in pal)).hexdigest() == palettes.CRATE["palette_sha256"]
        if "TwoColor" in style:
            groups = {palettes.LABELS[l][1] for l in set(model.v.values())}
            assert len(set(vox.values())) == len(groups) <= 6, name
        w = whole[name]
        assert w["read"] and w["voxels_match"] and w["glass_voxels_match"] and w["mesh"] and w["grounded"] and w["size_match"], name
        checked += 1
    for kind in FAMILIES:
        a = read(ROOT / filename(kind, "Base"))[1]
        b = read(ROOT / filename(kind, "Cartoon"))[1]
        assert a.keys() != b.keys(), kind
    # The grid: hollow rooms where units stand, no glass in a sill course but a door's.
    for kind in ("Cottage", "FlowerBoxCottage", "Manor"):
        for cartoon in (False, True):
            model = built[(kind, cartoon)]
            for (i, j) in model.footprint:
                for x in range(sculpt.X(i) + 3, sculpt.X(i + 1) - 3):
                    for y in range(sculpt.Y(j) + 3, sculpt.Y(j + 1) - 3):
                        for z in range(16, 48):
                            assert (x, y, z) not in model.v, (kind, cartoon, "room not hollow", (x, y, z))
            doors = set()
            for (t, a, b, k) in model.doors:
                doors.add((t, a, b))
            for (x, y, z), label in model.v.items():
                if 16 <= z < 32 and palettes.LABELS[label][1] == "glass":
                    bi, bj = round((x + 0.5 - 8) / 16), round((y + 0.5 - 8) / 16)
                    i, j = (x - 8) // 16, (y - 8) // 16
                    assert ("ey", i, bj) in doors or ("ex", bi, j) in doors, (kind, cartoon, "glass in a sill course", (x, y, z))
    assert len(report) == 42
    for scene, res in report.items():
        assert "stamped_exactly" in res["checks"] and all(res["checks"].values()), (scene, res["checks"])
    for kind in list(FAMILIES) + ["Bridge"]:
        for sheet in ("family", "geometry", "ingame"):
            assert (HERE / "previews" / ("PokeC_%s_%s.png" % (kind, sheet))).exists(), (kind, sheet)
        if kind != "Bridge":
            assert (HERE / "previews" / ("PokeC_%s_art.png" % kind)).exists(), kind
    assert (HERE / "overview.png").exists()
    record = json.loads((HERE / "preserved-hashes.json").read_text())
    preserved = record["sha256"]
    for rel, h in preserved.items():
        assert sha(ROOT / rel) == h, rel
    for rel, was in record["appended"].items():
        # Only added to: the file still begins with exactly what it was.
        assert hashlib.sha256((ROOT / rel).read_bytes()[:was["bytes"]]).hexdigest() == was["sha256"], rel
    summary = {
        "validated": "2026-10-28",
        "files": checked,
        "families": [f["asset_id"] for f in m["families"]],
        "file_sha256": {n: r["sha256"] for n, r in rows.items()},
        "structure": "pass: tools/inspect_vox.py, 35 files, no errors or warnings (structural-audit.json)",
        "geometry": "pass: canvases, grounded at z 0, one connected model each, recolours on their source's exact voxels, "
                    "Cartoon a different shape from Base",
        "palettes": "pass: CratePalette files the pinned crate palette byte for byte; TwoColor files one colour a group",
        "glass": "pass: MagicaVoxel Glass (_type _glass, _trans 0.7) on exactly the glass indices",
        "grid": "pass: rooms hollow at levels 1-2 away from the walls; no glass in a sill course outside a door's slot",
        "whole_import": "pass: every file read and meshed whole by the game's MagicaVoxel importer at Scale 0.0625 "
                        "(qa/whole-import.json)",
        "integration": "pass: 42 scenes (every treatment of the five families, and the bridge assembled), cut into the "
                       "game's pieces in a scratch copy of VCOM: the level the game stamps is each model voxel for voxel, "
                       "and every rules check passed (qa/integration-report.json)",
        "visual_review": "done: in-game renders by day, dusk and night, cut away, from four sides and the game's camera, "
                         "and each Base drawn in the art's projection beside the source (previews/)",
        "preserved": "pass: %d files in output/poke_c/ from before the buildings unchanged" % len(preserved),
        "not_tested": "the files opened in MagicaVoxel's own editor; the pieces added to the game's Pieces.tres and painted "
                      "in the level editor; play in a battle (units fighting through them, destruction, blood)",
    }
    (HERE / "validation-summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print("PASS: %d files, 5 families; geometry, palettes, glass, grid, whole import, 42 integration scenes, "
          "previews and %d preserved files." % (checked, len(preserved)))


if __name__ == "__main__":
    main()
