"""Every model of new_1.jpg and new_2.jpg but the new_1 cottage (made by
output/new_1/buildings/generate.py): each family's seven files, written directly
into output/new_1/ and output/new_2/, and each image's manifest
(output/new_X/elements/manifest.json).

    python output/new_images/generate.py [new_1|new_2|all] [family ...] [--replace-generated] [--out <folder>]

It owns only the files its manifests name. A file already there is overwritten only
if it is still exactly what this generator wrote last time (its hash in the
manifest); anything else, a hand edit or another agent's file of the same name,
stops the run unless --replace-generated is given. --out writes a dry run's
new_1/ and new_2/ into another folder instead. Naming families after the image
limits the run to them (the manifest keeps the others).

new_2's models are sculpted from its sprites (lib/build_new2.py), new_1's from
measurements read off the image (lib/new1_*.py), its ground tiles by the ground
collection's own code (lib/new1_ground.py); the seven treatments are
lib/treatments.py's, but the ground tiles', which are the ground collection's."""
import argparse
import hashlib
import importlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))
import treatments as T  # noqa: E402
from voxlib import encode  # noqa: E402

OUTPUT = HERE.parent
sha = lambda b: hashlib.sha256(b).hexdigest()


class Guard:
    """Writes a file only where nothing is, or where this generator's last file still is."""

    def __init__(self, folder, manifest, replace):
        self.folder, self.replace = folder, replace
        old = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {"files": []}
        self.previous = {r["file"]: r["sha256"] for r in old["files"]}

    def write(self, name, data):
        dest = self.folder / name
        if dest.exists() and not self.replace:
            assert self.previous.get(name) == sha(dest.read_bytes()), \
                "%s is not what this generator wrote last: keep it, or pass --replace-generated" % dest
        dest.write_bytes(data)
        assert dest.read_bytes() == data


def new_2(out, only, replace):
    from build_new2 import build
    from catalogue_new2 import F
    folder = out / "new_2"
    mpath = folder / "elements" / "manifest.json"
    guard = Guard(folder, mpath, replace)
    records, families = [], []
    for spec in F:
        if only and spec["name"] not in only:
            continue
        t1 = time.time()
        if spec["kind"] == "copy":
            src = T.ROOT / "output" / spec["model"]
            files = T.copy_family("New2", spec["name"], [str(src) + T.suffix(t) + ".vox" for t in T.TREATMENTS],
                                  layer="Vegetation")
            info = {"copied_from": spec["model"]}
        else:
            base, cart = build(spec)
            files, info = T.family("New2", spec["name"], base, cart, layer="Vegetation")
        for name, b, rec in files:
            guard.write(name, b)
            rec.update({"kind": spec["kind"], "what": spec["what"]})
            records.append(rec)
        fam = dict(spec)
        fam.update(info)
        families.append(fam)
        print("new_2 %-24s %-8s %s %5.1fs" % (spec["name"], spec["kind"], files[0][2]["size"], time.time() - t1))
        sys.stdout.flush()
    rank = {spec["name"]: i for i, spec in enumerate(F)}
    return finish(mpath, "New2_", families, records, only, rank, "new_2.jpg")


def new_1(out, only, replace):
    from catalogue_new1 import F
    folder = out / "new_1"
    mpath = folder / "elements" / "manifest.json"
    guard = Guard(folder, mpath, replace)
    records, families = [], []
    for spec in F:
        if only and spec["name"] not in only:
            continue
        mod, fn = spec["builder"].split(".")
        builder = getattr(importlib.import_module(mod), fn)
        base, cart = builder(cartoon=False), builder(cartoon=True)
        files, info = T.family("New1", spec["name"], base, cart, layer=spec["layer"])
        for name, b, rec in files:
            guard.write(name, b)
            rec.update({"kind": spec["layer"].lower(), "what": spec["what"]})
            records.append(rec)
        fam = dict(spec)
        fam.update(info)
        families.append(fam)
        print("new_1 %-24s %-30s %s" % (spec["name"], spec["builder"], files[0][2]["size"]))
    if not only or "Ground" in only:
        import new1_ground as G
        for (r, style, v, palette, groups) in G.build_all():
            stem = r["name"] + ("" if style == "Base" else "_" + style)
            b = encode((16, 16, 16), v, [tuple(c) for c in palette], name=stem, layer="Ground")
            guard.write(stem + ".vox", b)
            records.append({"file": stem + ".vox", "family": r["name"], "treatment": style, "size": [16, 16, 16],
                            "voxels": len(v), "colours": len(set(v.values())), "groups": groups,
                            "occupied_min": [min(p[a] for p in v) for a in range(3)],
                            "occupied_max": [max(p[a] for p in v) for a in range(3)],
                            "geometry": r["name"] + ("_Cartoon" if "Cartoon" in style else "") + ".vox",
                            "kind": "ground", "what": r.get("contour", r["kind"]), "sha256": sha(b)})
        for r in G.CAT:
            families.append({"name": r["name"][len("New1_"):], "builder": "the ground collection's own code "
                             "(output/ground/generate.py, through lib/new1_ground.py)",
                             "what": "ground tile: %s" % (r.get("contour") or r["kind"]), "row": r, "layer": "Ground"})
        print("new_1 ground: %d tiles" % (len(G.CAT) * 7))
    rank = {spec["name"]: i for i, spec in enumerate(F)}
    return finish(mpath, "New1_", families, records, only, rank, "new_1.jpg")


def finish(mpath, prefix, families, records, only, rank, image):
    """Writes the manifest, keeping a partial run's other families."""
    if only and mpath.exists():
        old = json.loads(mpath.read_text(encoding="utf-8"))
        names = {f["name"] for f in families}
        families += [f for f in old["families"] if f["name"] not in names]
        records += [r for r in old["files"] if r["family"][len(prefix):] not in names]
    families.sort(key=lambda f: (rank.get(f["name"], 10000), f["name"]))
    tr = {t: i for i, t in enumerate(T.TREATMENTS)}
    records.sort(key=lambda r: (rank.get(r["family"][len(prefix):], 10000), r["family"], tr.get(r["treatment"], 9)))
    mpath.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"source_image": image, "source_sha256": sha((T.ROOT / image).read_bytes()),
                "generator": "output/new_images/generate.py", "generator_sha256": sha(Path(__file__).read_bytes()),
                "library_sha256": {p.name: sha(p.read_bytes()) for p in sorted((HERE / "lib").glob("*.py"))},
                "crate_palette_sha256": T.CRATE["palette_sha256"], "scale": 0.0625,
                "scene_translation": "0 0 floor(canvas height / 2)", "grounded": "z 0",
                "delivery": "Complete models only, one .vox per treatment; no cell files or brushes.",
                "families": families, "files": records}
    mpath.write_text(json.dumps(manifest, indent=1, default=list) + "\n", encoding="utf-8")
    print("%s: %d families, %d files -> %s" % (image, len(families), len(records), mpath))
    return len(records)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("image", nargs="?", default="all", choices=["new_1", "new_2", "all"])
    a.add_argument("families", nargs="*")
    a.add_argument("--replace-generated", action="store_true")
    a.add_argument("--out", type=Path, default=None, help="a dry run's folder (default: output/)")
    args = a.parse_args()
    out = (args.out or OUTPUT).resolve()
    only = set(args.families)
    for image in (("new_1", "new_2") if args.image == "all" else (args.image,)):
        (out / image).mkdir(parents=True, exist_ok=True)
        (new_1 if image == "new_1" else new_2)(out, only, args.replace_generated)


if __name__ == "__main__":
    main()
