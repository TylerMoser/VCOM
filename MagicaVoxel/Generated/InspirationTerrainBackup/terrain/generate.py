"""Writes the terrain kits' complete models: every piece of every style (styles.py),
in Base and the six treatments, into output/<image>/, the whole small islands
(islands.py) beside them, and the collection's manifest, output/terrain/manifest.json.

    python generate.py              # writes them
    python generate.py --dry DIR    # writes them under DIR instead (DIR/<image>/...)
    python generate.py --check      # builds every file in memory, compares with disk

A file is <Prefix>_<Style>_<Piece>[_<Treatment>].vox (an island's
<Prefix>_<Island>[_<Treatment>].vox), Base without a suffix. Every file is built
and every target checked before anything is written: a file already on disk is
left alone if it is the same, replaced only if it holds what this generator's last
manifest recorded for it, and otherwise the run stops, writing nothing. So it
never overwrites another author's file, nor one changed by hand since.
"""
import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import islands as ISL
import kit
import styles as STY
from voxlib import encode

HERE = Path(__file__).resolve().parent
OUTPUT = kit.ROOT / "output"
MANIFEST = OUTPUT / "terrain" / "manifest.json"


def suffix(treatment):
    return "" if treatment == "Base" else "_" + treatment


def sha(b):
    return hashlib.sha256(b).hexdigest()


def occupied(v):
    xs, ys, zs = zip(*v)
    return [min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]


def record(file, kind, style, part, treatment, size, v, groups, b, geometry):
    lo, hi = occupied(v)
    return {"file": file, "kind": kind, "source": style.source, "style": style.name, "family": style.family,
            "part": part, "treatment": treatment, "size": list(size), "voxels": len(v),
            "colours": len(set(v.values())), "groups": {g: len(ix) for g, ix in sorted(groups.items())},
            "occupied_min": lo, "occupied_max": hi, "geometry": geometry, "sha256": sha(b)}


def build_all():
    """(file relative to output/, bytes, record) for every file, in order."""
    out = []
    for st in STY.STYLES:
        pre = STY.prefix(st.source)
        size = (16, 16, 16 * (st.levels + 1))
        for piece in st.pieces:
            raws = {False: kit.build(st, piece, False), True: kit.build(st, piece, True)}
            for t in kit.TREATMENTS:
                cartoon = "Cartoon" in t
                v, pal, groups = kit.paint(st, raws[cartoon], t)
                stem = "%s_%s_%s%s" % (pre, st.name, piece, suffix(t))
                file = "%s/%s.vox" % (st.source, stem)
                b = encode(size, v, pal, name=stem, layer="Terrain")
                geometry = "%s/%s_%s_%s%s.vox" % (st.source, pre, st.name, piece, "_Cartoon" if cartoon else "")
                out.append((file, b, record(file, "piece", st, piece, t, size, v, groups, b, geometry)))
    for src, items in ISL.ISLANDS.items():
        rim = [s for s in STY.STYLES if s.source == src and s.family == "IslandRim"][0]
        pre = STY.prefix(src)
        for iname, rows, depth in items:
            raws = {c: ISL.raw(rim, rows, depth, c) for c in (False, True)}
            for t in kit.TREATMENTS:
                cartoon = "Cartoon" in t
                raw, size = raws[cartoon]
                v, pal, groups = kit.paint(rim, raw, t)
                stem = "%s_%s%s" % (pre, iname, suffix(t))
                file = "%s/%s.vox" % (src, stem)
                b = encode(size, v, pal, name=stem, layer="Terrain")
                geometry = "%s/%s_%s%s.vox" % (src, pre, iname, "_Cartoon" if cartoon else "")
                rec = record(file, "island", rim, iname, t, size, v, groups, b, geometry)
                rec["rows"], rec["underside_levels"] = rows, depth
                out.append((file, b, rec))
    return out


def style_record(st):
    return {"source": st.source, "name": st.name, "family": st.family, "levels": st.levels, "image": st.image,
            "px_per_tile": st.ppt, "K": st.K, "art_crop": list(st.art), "top": st.top, "bottom": st.bottom,
            "tops": st.tops, "bottoms": st.bottoms, "pieces": list(st.pieces), "body_group": st.body_group,
            "labels": {k: {"rgb": list(v[0]), "group": v[1], "crate_class": v[2]} for k, v in st.labels.items()},
            "flat": {k: list(v) for k, v in st.flat.items()}, "params": {k: v for k, v in st.params.items()
                                                                           if k not in ("image", "ppt", "K", "art",
                                                                                        "note")},
            "test_layout": st.test, "note": st.note}


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--dry", type=Path, default=None)
    a.add_argument("--check", action="store_true")
    args = a.parse_args()
    files = build_all()
    names = [f for f, b, r in files]
    assert len(names) == len(set(names)), "two files with one name"
    root = args.dry.resolve() if args.dry else OUTPUT
    if args.check:
        bad = [f for f, b, r in files if not (root / f).exists() or sha((root / f).read_bytes()) != r["sha256"]]
        print("checked", len(files), "files;", len(bad), "differ or are missing")
        for f in bad[:20]:
            print("  ", f)
        return 1 if bad else 0
    previous = {}
    if not args.dry and MANIFEST.exists():
        previous = {r["file"]: r["sha256"] for r in json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]}
    refused, todo = [], []
    for f, b, r in files:
        p = root / f
        if p.exists():
            h = sha(p.read_bytes())
            if h == r["sha256"]:
                continue
            if previous.get(f) != h:
                refused.append(f)
                continue
        todo.append((p, b))
    if refused:
        print("REFUSED: %d files are already there and are not this generator's:" % len(refused))
        for f in refused[:30]:
            print("  ", f)
        return 1
    for p, b in todo:
        assert p.parent.exists() or args.dry, p.parent
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b)
    manifest = {"date": date.today().isoformat(), "generator": "output/terrain/generate.py",
                "treatments": list(kit.TREATMENTS), "styles": [style_record(s) for s in STY.STYLES],
                "islands": {src: [{"name": n, "rows": r, "underside_levels": d} for n, r, d in items]
                            for src, items in ISL.ISLANDS.items()},
                "files": [r for f, b, r in files]}
    mpath = (root / "terrain" / "manifest.json") if args.dry else MANIFEST
    mpath.parent.mkdir(parents=True, exist_ok=True)
    mpath.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print("files:", len(files), "written:", len(todo), "unchanged:", len(files) - len(todo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
