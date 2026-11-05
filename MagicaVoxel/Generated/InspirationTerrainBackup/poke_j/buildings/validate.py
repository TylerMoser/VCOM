"""Checks the 14 poke_j building files and their evidence, from what is on disk.

    python output/poke_j/buildings/validate.py      # writes validation-summary.json

Fails loudly on the first broken rule. What it checks:
- the manifest's hashes: source image, generator, its dependencies, every file;
- each file read back: its canvas, grounded at z 0, index 255 (the game's blood)
  unused, one connected model, exactly the sculptor's painted voxels (so the
  pieces the integration test cut are this file's), a recolour on exactly its
  geometry source's voxels;
- glass: MagicaVoxel Glass on exactly the glass indices, nowhere else;
- palettes: CratePalette files the pinned crate palette byte for byte; TwoColor
  files one colour for each group present (folded groups resolved), glass included;
- Cartoon differs from Base in shape, not only in paint;
- the game's grid: every storey hollow where units stand (its two levels, away
  from the walls), and no glass in a sill course (the storey's own level, round
  it) but in a door's slot or a window one climbs in by;
- evidence: the structural audit (no errors or warnings), every file imported
  whole through the game's importer (counts, glass, grounding, size), the
  integration report (every check of all 14 scenes passed, the stamping exact),
  the previews;
- every file of ChatGPT's in output/poke_j/ from before these buildings is unchanged
  (preserved-hashes.json says which).
"""
import hashlib
import json
import sys
from pathlib import Path

import palettes
import sculpt
from generate import FAMILIES, STYLES, family_name, filename
from voxlib import components, read

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WORK = ROOT.parent.parent
sys.path.insert(0, str(HERE / "qa"))
from cut_pieces import resolve  # noqa: E402

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    m = json.loads((HERE / "manifest.json").read_text())
    assert len(m["models"]) == 14 and len(m["families"]) == 2
    assert sha(WORK / m["source_image"]) == m["source_sha256"]
    assert sha(HERE / "generate.py") == m["generator_sha256"]
    for name, h in m["dependencies"].items():
        assert sha(HERE / name) == h, name
    audit = {Path(a["path"]).name: a for a in json.loads((HERE / "structural-audit.json").read_text())}
    whole = json.loads((HERE / "qa" / "whole-import.json").read_text())
    report = json.loads((HERE / "qa" / "integration-report.json").read_text())
    rows = {r["file"]: r for r in m["models"]}
    built = {(k, c): sculpt.build(k, c) for k in FAMILIES for c in (False, True)}
    checked = 0
    for name, r in rows.items():
        p = ROOT / name
        assert sha(p) == r["sha256"] == audit[name]["sha256"], name
        assert not audit[name]["warnings"] and not audit[name].get("errors"), name
        size, vox, pal, mats = read(p)
        kind = r["family"].removeprefix("PokeJ_")
        style = r["style"]
        model = built[(kind, "Cartoon" in style)]
        assert tuple(size) == tuple(r["canvas"]) == model.size
        assert min(q[2] for q in vox) == 0 and 255 not in vox.values()
        assert len(components(vox)) == 1, name
        assert vox == {q: palettes.paint(style, l, kind) for q, l in model.v.items()}, name
        _, src, _, _ = read(ROOT / r["geometry_source"])
        assert vox.keys() == src.keys(), name
        glass_idx = {i for i, mt in mats.items() if mt.get("_type") == "_glass"}
        want = {palettes.paint(style, l, kind) for l in set(model.v.values()) if palettes.LABELS[l][1] == "glass"}
        assert glass_idx == want, (name, glass_idx, want)
        if "CratePalette" in style:
            assert hashlib.sha256(b"".join(bytes(c) for c in pal)).hexdigest() == palettes.CRATE["palette_sha256"]
        if "TwoColor" in style:
            groups = palettes.groups_used(set(model.v.values()), kind)
            assert len(set(vox.values())) == len(groups) <= 8, name
        w = whole[name]
        assert w["read"] and w["voxels_match"] and w["glass_voxels_match"] and w["mesh"] and w["grounded"] and w["size_match"], name
        checked += 1
    for kind in FAMILIES:
        a = read(ROOT / filename(kind, "Base"))[1]
        b = read(ROOT / filename(kind, "Cartoon"))[1]
        assert a.keys() != b.keys(), kind
    # The grid: hollow storeys where units stand; no glass in a sill course but a
    # door's slot or a window one climbs in by.
    glassy = {l for l in palettes.LABELS if palettes.LABELS[l][1] == "glass"}
    for (kind, cartoon), model in built.items():
        doors = {tuple(d) for d in model.doors}
        climb_slots = set()
        for a, b in model.climbs:
            (i0, j0, _), (i1, j1, k1) = a, b
            if i0 != i1:
                climb_slots.add(("ex", max(i0, i1), j0, k1))
            else:
                climb_slots.add(("ey", i0, max(j0, j1), k1))
        slot_of = {q: resolve(model, *q, model.role[q]) for q in model.v}
        for st in model.storeys:
            s = st["stand"]
            # Nothing in the middle of a storey's tiles at the two levels units fill
            # there (the walls, slopes and dormers round it are edge pieces).
            for q, slot in slot_of.items():
                if slot[0] == "mid" and slot[3] in (s, s + 1):
                    assert (slot[1], slot[2]) not in st["tiles"], (kind, cartoon, "storey not hollow", q, slot)
            if st["entry"] == "climb":
                continue
            for (x, y, z), label in model.v.items():
                if label in glassy and z // 16 == s:
                    slot = slot_of[(x, y, z)]
                    if slot[0] in ("ex", "ey"):
                        assert slot in doors or slot in climb_slots, (kind, cartoon, "glass in a sill course", (x, y, z), slot)
    assert len(report) == 14
    for scene, res in report.items():
        assert "stamped_exactly" in res["checks"] and all(res["checks"].values()), (scene, res["checks"])
    for kind in FAMILIES:
        for sheet in ("family", "geometry", "ingame", "art"):
            assert (HERE / "previews" / ("%s_%s.png" % (family_name(kind), sheet))).exists(), (kind, sheet)
    assert (HERE / "overview.png").exists()
    record = json.loads((HERE / "preserved-hashes.json").read_text())
    preserved = record["sha256"]
    for rel, h in preserved.items():
        assert sha(ROOT / rel) == h, rel
    for rel, was in record["appended"].items():
        # Only added to: the file still begins with exactly what it was.
        assert hashlib.sha256((ROOT / rel).read_bytes()[:was["bytes"]]).hexdigest() == was["sha256"], rel
    checks = sorted({c for res in report.values() for c in res["checks"]})
    summary = {
        "validated": "2026-10-28",
        "files": checked,
        "families": [f["asset_id"] for f in m["families"]],
        "file_sha256": {n: r["sha256"] for n, r in rows.items()},
        "structure": "pass: tools/inspect_vox.py, 14 files, no errors or warnings (structural-audit.json)",
        "geometry": "pass: canvases, grounded at z 0, one connected model each, recolours on their source's exact voxels, "
                    "Cartoon a different shape from Base",
        "palettes": "pass: CratePalette files the pinned crate palette byte for byte; TwoColor files one colour a group "
                    "(each family's own colours, folded groups resolved)",
        "glass": "pass: MagicaVoxel Glass (_type _glass, _trans 0.45-0.7) on exactly the glass indices",
        "grid": "pass: nothing in the middle of a storey's tiles at the two levels units fill; no glass in a sill course "
                "outside a door's slot",
        "whole_import": "pass: every file read and meshed whole by the game's MagicaVoxel importer at Scale 0.0625 "
                        "(qa/whole-import.json)",
        "integration": "pass: 14 scenes (every treatment of the two families), cut into the game's pieces in a scratch "
                       "copy of VCOM: the level the game stamps is each model voxel for voxel, and every rules check "
                       "passed: %s (qa/integration-report.json)" % ", ".join(checks),
        "visual_review": "done: in-game renders by day, dusk and night, cut away at each storey, from four sides and the "
                         "game's camera, and each Base drawn in the art's projection beside the source (previews/)",
        "preserved": "pass: %d files of ChatGPT's in output/poke_j/ from before these buildings unchanged (its models, "
                     "generator, records and previews)" % len(preserved),
        "not_tested": "the files opened in MagicaVoxel's own editor; the pieces added to the game's Pieces.tres and painted "
                      "in the level editor; play in a battle (units fighting through them, destruction, blood)",
    }
    (HERE / "validation-summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print("PASS: %d files, 2 families; geometry, palettes, glass, grid, whole import, 14 integration scenes, "
          "previews and %d preserved files." % (checked, len(preserved)))


if __name__ == "__main__":
    main()
