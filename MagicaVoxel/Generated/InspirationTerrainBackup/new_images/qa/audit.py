"""The workspace's read-only structural audit (tools/inspect_vox.py) over exactly the
new images' files, the ones their manifests name (output/new_1/ and output/new_2/
hold another agent's files too, which this leaves alone). Writes
output/new_images/structural-audit.json in the tool's own form.

    python output/new_images/qa/audit.py [--files <folder holding new_1/ and new_2/>] [--out <json>]"""
import argparse
import importlib.util
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = Path(r"C:/Users/tandm/Documents/Projects/VoxelRidgeInspiration")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", type=Path, default=HERE.parents[1])
    ap.add_argument("--out", type=Path, default=HERE.parent / "structural-audit.json")
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location("inspect_vox", W / "tools" / "inspect_vox.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    root = args.files.resolve()
    names = []
    for rel in ("new_1/elements/manifest.json", "new_2/elements/manifest.json"):
        names += [rel.split("/")[0] + "/" + r["file"] for r in json.loads((root / rel).read_text(encoding="utf-8"))["files"]]
    names += ["new_1/" + r["file"] for r in
              json.loads((root / "new_1" / "buildings" / "manifest.json").read_text(encoding="utf-8"))["models"]]
    results = []
    for rel in sorted(names):
        path = root / rel
        try:
            results.append(tool.inspect(path))
        except (ValueError, struct.error, IndexError) as error:
            results.append(dict(path=str(path.resolve()), error=str(error)))
    args.out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    errors = sum(1 for r in results if "error" in r) + sum(len(r.get("errors", [])) for r in results)
    warnings = sum(len(r.get("warnings", [])) for r in results)
    print("Audited %d files; %d errors; %d warnings -> %s" % (len(results), errors, warnings, args.out))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
