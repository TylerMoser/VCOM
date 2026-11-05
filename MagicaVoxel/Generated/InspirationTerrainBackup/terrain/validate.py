"""Checks the terrain collection on disk against its manifest and its rules.

    python validate.py [--root DIR]    # DIR: a dry run's folder; default output/
                                       # writes terrain/validation-summary.json there

Fails loudly, listing what broke. What it checks:
- every file of the manifest there, with the hash the manifest recorded;
- each file read back: its canvas the manifest's, whole tiles across (16, or the
  island's tiles) and whole levels tall, its voxels the manifest's count, inside
  the canvas, grounded at z 0, index 255 (the game's blood) unused, every voxel's
  index a colour of the palette, no glass material, one six-connected model;
- geometry: every treatment the exact occupancy of its Base (or Cartoon) file, and
  Cartoon a different shape from Base on every piece with a face;
- palettes: CratePalette files the pinned crate palette byte for byte; TwoColor
  files one colour for each material group (the manifest's groups, all ones);
- the ground: a piece's lowest level holds its style's lower ground tile intact
  in the same treatment (anything more only above that tile's surface: a cliff's
  foot on water, a fall's foam), a Fill's top three layers exactly its upper
  tile's;
- the evidence files named on the command line or found (structural audit, whole
  import, in-game report) when there, every row passing;
- every file older than these, ChatGPT's of before 2026-10-28 that
  preserved-hashes.json lists, unchanged.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kit  # noqa: E402
import styles as STY  # noqa: E402
from voxlib import components, read  # noqa: E402


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--root", type=Path, default=kit.ROOT / "output")
    args = a.parse_args()
    root = args.root.resolve()
    manifest = json.loads((root / "terrain" / "manifest.json").read_text(encoding="utf-8"))
    rows = manifest["files"]
    by_file = {r["file"]: r for r in rows}
    styles = {(s.source, s.name): s for s in STY.STYLES}
    crate = [tuple(c) for c in kit.CRATE_RGBA]
    problems = []

    def fail(f, why):
        problems.append("%s: %s" % (f, why))

    occupancy = {}
    for r in rows:
        f = r["file"]
        p = root / f
        if not p.exists():
            fail(f, "missing")
            continue
        if sha(p) != r["sha256"]:
            fail(f, "hash differs from the manifest")
        size, vox, pal, mats = read(p)
        if list(size) != r["size"]:
            fail(f, "canvas %s, manifest %s" % (size, r["size"]))
        if any(d % 16 for d in size):
            fail(f, "canvas %s not whole tiles and levels" % (size,))
        if len(vox) != r["voxels"]:
            fail(f, "%d voxels, manifest %d" % (len(vox), r["voxels"]))
        if any(not (0 <= x < size[0] and 0 <= y < size[1] and 0 <= z < size[2]) for x, y, z in vox):
            fail(f, "a voxel outside the canvas")
        if min(z for x, y, z in vox) != 0:
            fail(f, "not grounded at z 0")
        if 255 in set(vox.values()):
            fail(f, "index 255 used")
        if any(m.get("_type") == "_glass" for m in mats.values()):
            fail(f, "a glass material")
        parts = components(vox)
        if len(parts) != 1:
            fail(f, "%d separate parts %s" % (len(parts), parts[:5]))
        t = r["treatment"]
        if "CratePalette" in t and [tuple(c) for c in pal] != crate:
            fail(f, "not the pinned crate palette")
        if "TwoColor" in t and any(n != 1 for n in r["groups"].values()):
            fail(f, "TwoColor groups %s" % r["groups"])
        occupancy[f] = frozenset(vox)
        st = styles[(r["source"], r["style"])] if r["kind"] == "piece" else None
        if st is not None and st.bottom:
            # The lower tile intact in the piece's lowest level: every voxel of it,
            # in its own colour; anything else there only above the tile's surface
            # (a cliff's foot or a fall's foam standing on water).
            g = kit.ground(st.bottom_for(r["part"]), t)
            got = {(x, y, z): tuple(pal[i - 1][:3]) for (x, y, z), i in vox.items() if z < 16}
            surface = {}
            for (x, y, z) in g:
                surface[(x, y)] = max(surface.get((x, y), -1), z)
            if any(got.get(q) != rgb for q, (i, rgb, grp) in g.items()):
                fail(f, "its lowest level does not hold its lower ground tile intact")
            elif any(q not in g and q[2] <= surface.get(q[:2], 15) for q in got):
                fail(f, "a voxel inside its lower ground tile's space that the tile does not have")
        if st is not None and st.top and r["part"] == "Fill":
            g = kit.ground(st.top, t)
            zt = 16 * (st.levels + 1) - 3
            cells = {(x, y, z - zt + 13): tuple(pal[i - 1][:3]) for (x, y, z), i in vox.items() if z >= zt}
            want = {q: rgb for q, (i, rgb, grp) in g.items() if q[2] >= 13}
            if cells != want:
                fail(f, "top is not its upper ground tile")
    for r in rows:
        f = r["file"]
        if f in occupancy and r["geometry"] in occupancy and occupancy[f] != occupancy[r["geometry"]]:
            fail(f, "occupancy differs from %s" % r["geometry"])
        if r["treatment"] == "Cartoon" and r["part"] not in ("Fill", "Channel"):
            base = r["geometry"].replace("_Cartoon.vox", ".vox")
            if base in occupancy and occupancy[base] == occupancy.get(f):
                fail(f, "Cartoon has Base's shape")
    evidence = {}
    for name in ("structural-audit.json", "whole-import.json", "integration-report.json"):
        p = root / "terrain" / "qa" / name
        if p.exists():
            evidence[name] = sha(p)
    audit = root / "terrain" / "qa" / "structural-audit.json"
    if audit.exists():
        d = json.loads(audit.read_text(encoding="utf-8"))
        files = d if isinstance(d, list) else d.get("files", [])
        bad = [x for x in files if x.get("error") or x.get("errors") or x.get("warnings")]
        if bad:
            fail("structural-audit.json", "%d files with errors or warnings" % len(bad))
    whole = root / "terrain" / "qa" / "whole-import.json"
    if whole.exists():
        d = json.loads(whole.read_text(encoding="utf-8"))
        for f, res in d.items():
            if not all(res.get(k) for k in ("read", "voxels_match", "mesh", "grounded", "size_match")):
                fail(f, "whole import %s" % res)
        missing = [r["file"] for r in rows if Path(r["file"]).name not in d and r["file"] not in d]
        if missing:
            fail("whole-import.json", "%d files not imported, %s" % (len(missing), missing[:3]))
    integ = root / "terrain" / "qa" / "integration-report.json"
    if integ.exists():
        d = json.loads(integ.read_text(encoding="utf-8"))
        for scene, res in d.items():
            for c, ok in res["checks"].items():
                if not ok:
                    fail(scene, "in-game check %s failed" % c)
    preserved = root / "terrain" / "preserved-hashes.json"
    kept = 0
    if preserved.exists():
        d = json.loads(preserved.read_text(encoding="utf-8"))
        for rel, h in d["chatgpt"].items():
            p = kit.ROOT / rel
            if not p.exists() or sha(p) != h:
                fail(rel, "ChatGPT's file changed or gone")
            kept += 1
        for rel, rec in d.get("appended", {}).items():
            p = kit.ROOT / rel
            b = p.read_bytes()
            if hashlib.sha256(b[:rec["bytes"]]).hexdigest() != rec["sha256"]:
                fail(rel, "shared file changed before the appended section")
    summary = {"files": len(rows), "problems": problems, "evidence": evidence, "preserved_checked": kept,
               "pieces": sum(1 for r in rows if r["kind"] == "piece"),
               "islands": sum(1 for r in rows if r["kind"] == "island")}
    (root / "terrain" / "validation-summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print("files:", len(rows), "problems:", len(problems), "preserved checked:", kept)
    for x in problems[:40]:
        print("  ", x)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
