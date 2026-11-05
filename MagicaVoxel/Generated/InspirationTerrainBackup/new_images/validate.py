"""Checks the new_1 and new_2 files and their records, from what is on disk, and
that nothing that was in output/new_1/ and output/new_2/ before them, nor the shared
files they were added to, has changed (preserved-hashes.json).
    python output/new_images/validate.py [--files <folder holding new_1/ and new_2/>]
writes output/new_images/validation-summary.json (a dry run's: --out <json>)

Per file: it reads; its voxels inside its canvas; grounded (lowest voxel z 0);
palette index 255 (the game's blood) never used; a CratePalette file's palette the
pinned crate palette byte for byte, index 253 (the crate's glass) only on glass; a
TwoColor file one colour a material. Per family: its seven files; every recolour's
voxels exactly its Base's or Cartoon's; Cartoon's shape not Base's (but where the
conventions keep it: ground tiles, copies of an earlier image's model); the
Cartoon's symmetry, found and checked against what its builder makes; its parts
(six-connected), one but for the families drawn as a scatter or a patch of
separate plants."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from voxlib import read  # noqa: E402

HERE = Path(__file__).resolve().parent
_args = sys.argv[1:]
ROOT = Path(_args[_args.index("--files") + 1]) if "--files" in _args else HERE.parent
OUT = Path(_args[_args.index("--out") + 1]) if "--out" in _args else HERE / "validation-summary.json"
W = Path(r"C:/Users/tandm/Documents/Projects/VoxelRidgeInspiration")
CRATE = json.loads((W / "knowledge" / "palettes" / "crate-palette.json").read_text())
TREATMENTS = ["Base", "Cartoon", "CratePalette", "TwoColor", "Cartoon_TwoColor", "CratePalette_TwoColor",
              "Cartoon_CratePalette_TwoColor"]
M1 = json.loads((ROOT / "new_1" / "elements" / "manifest.json").read_text(encoding="utf-8"))
M2 = json.loads((ROOT / "new_2" / "elements" / "manifest.json").read_text(encoding="utf-8"))
MC = json.loads((ROOT / "new_1" / "buildings" / "manifest.json").read_text(encoding="utf-8"))

# Builders whose Cartoon is exactly quarter-turn symmetric; mirrored ones; none required.
C4 = {"tree", "palm", "clumps", "fern", "cactus", "stump", "lobes_c4"}
SCATTER = {"New2_FloatingLilyPads", "New2_LilyPadTrio", "New2_LotusLilyPads", "New2_GrassTuft_A",
           "New2_GrassTuft_B", "New2_GrassTuft_A2", "New2_FloweringTuft", "New2_WindBlownBlades",
           "New2_SpikyGrassClump", "New2_TallGrassClump", "New2_WaterReeds_A", "New2_WaterReeds_B",
           "New1_TallGrass"}
SAME_SHAPE_OK = {"ground", "copy"}

sha = lambda b: hashlib.sha256(b).hexdigest()


def suffix(t):
    return "" if t == "Base" else "_" + t


def parts(vox):
    left = set(vox)
    out = []
    while left:
        s = left.pop()
        todo, n = [s], 1
        while todo:
            x, y, z = todo.pop()
            for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if q in left:
                    left.discard(q)
                    todo.append(q)
                    n += 1
        out.append(n)
    return sorted(out, reverse=True)


def symmetry(size, vox):
    W_, D, _ = size
    found = []
    if W_ == D and {(W_ - 1 - y, x, z): c for (x, y, z), c in vox.items()} == vox:
        found.append("quarter-turn")
    if {(W_ - 1 - x, y, z): c for (x, y, z), c in vox.items()} == vox:
        found.append("mirror-x")
    if {(x, D - 1 - y, z): c for (x, y, z), c in vox.items()} == vox:
        found.append("mirror-y")
    return found or ["none"]


def families():
    """(image folder, family stem, builder kind, materials per file record) of every family."""
    out = []
    for f in M2["families"]:
        k = f["kind"]
        if k == "hedge" and f["name"] == "Hedge_Pillar":
            k = "hedge_pillar"
        out.append(("new_2", "New2_" + f["name"], k))
    for f in M1["families"]:
        if f.get("layer") == "Ground":
            out.append(("new_1", f["row"]["name"], "ground"))
        else:
            mod = f["builder"].split(".")[1]
            kind = {"cone_tree": "tree", "rosette": "lobes_c4", "planter_plant": "lobes_c4"}.get(mod, mod)
            out.append(("new_1", "New1_" + f["name"], kind))
    for f in MC["families"]:
        out.append(("new_1", f["asset_id"], "building"))
    return out


records = {}
for r in M1["files"] + M2["files"]:
    records[r["file"]] = r
for r in MC["models"]:
    records[r["file"]] = r

report = {"files": {}, "families": {}, "problems": []}
for folder, stem, kind in families():
    vox_of = {}
    for t in TREATMENTS:
        name = stem + suffix(t) + ".vox"
        path = ROOT / folder / name
        problems = []
        if not path.exists():
            report["problems"].append((name, "missing"))
            continue
        data = path.read_bytes()
        size, vox, pal, mats = read(path)
        vox_of[t] = (size, vox)
        used = set(vox.values())
        if 255 in used:
            problems.append("index 255 used")
        if any(not (0 <= p[a] < size[a]) for p in vox for a in range(3)):
            problems.append("voxel outside its canvas")
        if min(p[2] for p in vox) != 0:
            problems.append("not grounded")
        glass_idx = {i for i, m in mats.items() if m.get("_type") == "_glass"}
        if "CratePalette" in t:
            if hashlib.sha256(b"".join(bytes(c) for c in pal)).hexdigest() != CRATE["palette_sha256"]:
                problems.append("crate palette not byte for byte")
            if 253 in used and 253 not in glass_idx:
                problems.append("253 on an opaque voxel")
        rec = records.get(name, {})
        if "TwoColor" in t and kind not in ("ground", "building", "copy", "recolour"):
            ngroups = len(rec.get("groups", {}))
            if ngroups and len(used) != ngroups:
                problems.append("TwoColor: %d colours for %d materials" % (len(used), ngroups))
        report["files"][folder + "/" + name] = {"sha256": sha(data), "size": list(size), "voxels": len(vox),
                                                 "colours": len(used), "glass_voxels": sum(1 for v in vox.values()
                                                                                          if v in glass_idx),
                                                 "problems": problems}
        for p in problems:
            report["problems"].append((name, p))
    if len(vox_of) != 7:
        continue
    base_set, cart_set = set(vox_of["Base"][1]), set(vox_of["Cartoon"][1])
    for t in TREATMENTS:
        want = cart_set if "Cartoon" in t else base_set
        if set(vox_of[t][1]) != want:
            report["problems"].append((stem + suffix(t), "voxels differ from its geometry source"))
    if base_set == cart_set and kind not in SAME_SHAPE_OK:
        report["problems"].append((stem, "Cartoon has Base's shape"))
    sym = symmetry(*vox_of["Cartoon"])
    if kind in C4 and "quarter-turn" not in sym:
        report["problems"].append((stem, "Cartoon not quarter-turn symmetric: %s" % sym))
    np_base, np_cart = parts(vox_of["Base"][1]), parts(vox_of["Cartoon"][1])
    if (len(np_base) > 1 or len(np_cart) > 1) and stem not in SCATTER and kind not in ("ground",):
        report["problems"].append((stem, "parts apart: Base %s, Cartoon %s" % (np_base[:6], np_cart[:6])))
    report["families"][stem] = {"folder": folder, "builder": kind, "cartoon_symmetry": sym,
                                "parts_base": len(np_base), "parts_cartoon": len(np_cart),
                                "canvas": list(vox_of["Base"][0])}
# every file recorded before these were added: unchanged (the shared files appended
# to: their old bytes still the start of them)
pres = HERE / "preserved-hashes.json"
if pres.exists() and ROOT.resolve() == HERE.parent.resolve():
    rec = json.loads(pres.read_text(encoding="utf-8"))
    changed = []
    for rel, h in rec["files"].items():
        p = W / rel
        if not p.exists() or sha(p.read_bytes()) != h:
            changed.append(rel)
    for rel, a in rec.get("appended", {}).items():
        b = (W / rel).read_bytes()
        if len(b) < a["bytes"] or sha(b[:a["bytes"]]) != a["sha256"]:
            changed.append(rel + " (its start)")
    for rel in changed:
        report["problems"].append((rel, "a file there before these was changed"))
    report["preserved"] = {"files": len(rec["files"]), "appended_to": sorted(rec.get("appended", {})),
                           "changed": changed}
report["summary"] = {"families": len(report["families"]), "files": len(report["files"]),
                     "problems": len(report["problems"])}
OUT.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
print(report["summary"])
for p in report["problems"][:40]:
    print("  ", p)
