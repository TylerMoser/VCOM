"""Writes the terrain collection's documents from its manifest and evidence:
output/terrain/README.md and FILES.md, output/<image>/terrain/README.md for each
image, and knowledge/TERRAIN.md.
    python document.py [--root DIR]    # DIR a dry run's folder; default output/
The README tables are the manifest's; the words around them are below."""
import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kit  # noqa: E402
import styles as STY  # noqa: E402

IMAGE_FILE = {}
for s in STY.STYLES:
    IMAGE_FILE[s.source] = s.image
FAMILY_WORDS = {
    "StripedCliff": "the earth cliff of rounded columns most of the Pokemon maps draw: lit along the top, shaded "
                    "toward the foot, a dark crease between columns, the top's grass hanging over in a jagged edge",
    "LumpyWall": "rock or earth in rounded lumps, in one or more courses (each lit along its top, dark under it), "
                 "topped by the grass hanging over or by a rim of the rock itself",
    "StrataCliff": "horizontal beds, each top edge standing out and lit, its foot tucked in and dark, joints "
                   "staggered bed to bed",
    "FacetedCliff": "angular blocks in rows, each standing out its own amount, lit along its top and left edge, a "
                    "dark crease below and to the right",
    "EarthBank": "a near-flat earth wall, a light band under the scalloped grass rim, darker blotches, a jagged "
                 "dark foot",
    "StonyBank": "a bank faced with rounded stones of several sizes, lit along their tops, dark seams, a dark foot",
    "IslandRim": "the rim of a floating island: rows of crags hanging under the grass, each row tucked in from "
                 "the one above and tapering to points, nothing below",
    "MarioPlatform": "Paper Mario's raised ground: a flat top with a pale rim line, a fringe of grass tongues over "
                     "warm soil marked with small crosses",
    "ZigzagTrim": "Paper Mario's trimmed side: a band of orange with dark red triangles over a dark teal wall",
    "Masonry": "a built wall: staggered courses of dressed stone, a few of other stones among them, a coping",
}
EXTRA_WORDS = {
    "Fall": "the straight face with the river (its own water tile) pouring over the rim in a sheet down to the "
            "pool below (its own water tile), foam over the lip and where it lands",
    "Channel": "a raised fill tile carrying the river to a fall: the water tile on top",
    "NarrowFall": "a spring: a narrow stream rising a few voxels back from the edge and falling down the middle "
                  "of the face into its pool (off a floating rim, into the air, ending in mist)",
    "CaveMouth": "the straight face with a round-headed opening at its foot going 11 voxels back to a dark end, "
                 "the lower ground carried in as its floor",
    "Archway": "the masonry wall's straight face with a round-headed passage at its foot, as the cave mouth is",
    "Drain": "the straight face with a round-headed, barred outfall at its foot, in a ring of dressed stone",
    "Notch": "the straight face with a V-shaped gully cut down it, narrowing to nothing 11 voxels back",
}
PIECE_WORDS = {
    "Fill": "a raised tile with raised ground all round: the column, no face",
    "Straight": "a face along one side (local -y)",
    "OuterCorner": "faces on two sides meeting round a convex corner (local -y and -x)",
    "InnerCorner": "raised ground all round but one diagonal: the concave corner (the notch at local -x -y)",
    "Ridge": "a raised strip a tile wide: faces on two opposite sides (local -y and +y)",
    "RidgeEnd": "the end of such a strip: faces on three sides (local -y, +y and -x)",
    "Pillar": "a single raised tile: faces all round",
}


def suffix(t):
    return "" if t == "Base" else "_" + t


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--root", type=Path, default=kit.ROOT / "output")
    args = a.parse_args()
    root = args.root.resolve()
    m = json.loads((root / "terrain" / "manifest.json").read_text(encoding="utf-8"))
    files = m["files"]
    val = json.loads((root / "terrain" / "validation-summary.json").read_text(encoding="utf-8"))
    qa = root / "terrain" / "qa"
    integ = json.loads((qa / "integration-report.json").read_text(encoding="utf-8")) if (
        qa / "integration-report.json").exists() else {}
    whole = json.loads((qa / "whole-import.json").read_text(encoding="utf-8")) if (
        qa / "whole-import.json").exists() else {}
    by_source = collections.defaultdict(list)
    for s in m["styles"]:
        by_source[s["source"]].append(s)
    n_pieces = sum(1 for r in files if r["kind"] == "piece")
    n_islands = sum(1 for r in files if r["kind"] == "island")
    n_styles = len(m["styles"])
    n_scenes = len(integ)
    passed = sum(1 for r in integ.values() if all(r["checks"].values()))
    whole_ok = sum(1 for r in whole.values() if all(r.get(k) for k in ("read", "voxels_match", "mesh", "grounded",
                                                                         "size_match")))
    sources = sorted(by_source)

    # ------------------------------------------------------------------ README
    rows = []
    for src in sources:
        for s in by_source[src]:
            extra = [p for p in s["pieces"] if p not in kit.PIECES]
            rows.append("| [%s](../%s/terrain/README.md) | %s | %s | %d | %g | %g | %s | %s |" % (
                src, src, s["name"], s["family"], s["levels"], s["px_per_tile"], s["K"],
                s["bottom"].split("_Ground_")[-1] if s["bottom"] else "none (floating)",
                ", ".join(extra) or "-"))
    readme = """# Terrain kits

2026-11-03/04: **the ground shapes of all 25 inspiration images as modular voxel kits: %d styles, %d pieces, \
%s complete VOX files** (%s of the kits' pieces, %d of %d whole small floating islands), each in Base and the six \
established variations. Every ridge, cliff, raised terrace, bank, ledge, gully wall, cave wall, island rim, platform and \
retaining wall the images draw is a style here, with its cave mouths, waterfalls, drains and notches as extra \
pieces of it. The files sit beside each image's other models in `output/<image>/`; this folder holds the code, \
the checks and the evidence, and `output/<image>/terrain/` each image's notes and previews.

[All files](FILES.md) | [Overview](overview.png) | [Manifest](manifest.json) | \
[Validation](validation-summary.json) | [In-game report](qa/integration-report.json) | \
[Whole import](qa/whole-import.json) | [Structural audit](qa/structural-audit.json) | \
[Authoring notes](../../knowledge/TERRAIN.md)

## The user's decisions (2026-11-03)

- **Modular kits.** For each distinct style an image draws: complete pieces on the game's grid, one tile wide \
at the height drawn (the straight face, outer and inner corners, and the ends, falls, mouths and gullies drawn), \
turned and placed side by side; each image its own files in its own colours, with previews of the pieces put \
together as the image draws them.
- **Heights as drawn, in whole levels.** An image with tall and short cliffs gets several styles.
- **Also cave mouths, waterfalls and retaining walls** (not Mario's backdrop hills).
- **Floating islands both ways**: rim pieces hanging down, and a few whole small islands.

## A piece

A piece is one tile, 16 x 16 voxels, and a whole column: `16 x 16 x 16(H+1)` for a style `H` levels high. Its \
lowest level (z 0-15) is the image's lower ground tile, the ground collection's file copied voxel for voxel in the \
same treatment, so a piece stands among the plain ground tiles without a seam; over a water tile, whose surface \
is two voxels down, the cliff's foot stands on the water. Its face is set back four voxels from the tile's edge \
and stands out of that line by the style's relief (columns, lumps, beds, blocks, crags), its top the upper ground \
tile's top three layers, the grass hanging over the face. A floating rim has no lower ground: its rock hangs to \
z 0. Every pattern repeats every 16 voxels along a face and is measured round the corners the same way, so the \
pieces join along a run and round corners.

The pieces, drawn facing local -y (MagicaVoxel's front) and turned in quarter turns about z to fit:

%s

and the extras a style has:

%s

**Placing them** is the autotiling every 2D map uses: for each raised tile, the lower of its four neighbours \
pick the piece and its turn (none lower: Fill, or InnerCorner if a diagonal is; one: Straight; two at a corner: \
OuterCorner; two opposite: Ridge; three: RidgeEnd; four: Pillar). `layout.py` does it (`piece_for`, `place`), and \
the previews and the in-game test put every style together that way. A turn `q` takes (x, y) to (15-y, x) q \
times, VCOM's own turn. For VCOM a piece's column is cut into its `H+1` 16-cubed cells, one a level, as the \
level editor places a cell's middle piece: the test does exactly that.

**Whole islands** are the rim style's pieces laid out as an island, with the rock hanging below in a mass that \
tapers to a point: two for poke_s, two for poke_u, as the images' small islands are, each one model on the \
grid (its underside two whole levels deep).

## The styles

Heights were measured on each image's own faces: the face's drawn height in the image's pixels, from under the \
rim to the foot, times 16 over the image's pixels a tile is a height in voxels as drawn, divided by the image's \
vertical foreshortening K (drawn pixels a voxel of height, over a pixel a voxel across) to a true height, and \
rounded to whole levels. K is the one each image's buildings were made with (0.46 for the Pokemon maps that \
have none of their own; poke_m 0.5; poke_o and poke_r 0.375; poke_u 0.4375); Pixelwood's, 0.88, is its house's \
(its author put the wall top at z 34 for 30 art pixels drawn), Mario's, 0.7, its blocks'. Every style's colours \
are its art's own, read off its pixels; its measurements, crop and the reasons are in its image's notes.

| Image | Style | Family | Levels | Px a tile | K | Lower ground | Extra pieces |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
%s

The families (`families.py`):

%s

## The seven treatments

- **Base**: the art's colours.
- **Cartoon**: simpler, bolder shapes: wider columns and lumps, an even rim a voxel further out, larger \
blocks and courses, and fewer shades. Every piece with a face differs from Base in shape.
- **CratePalette**: Base's geometry exactly, the pinned crate palette byte for byte, each colour on the \
nearest entry of its material's range; the copied ground keeps its tile's own crate entries.
- **TwoColor**: Base's geometry, one flat colour for each material, per the rule: *"Don't require exactly 2 \
colors. Make exceptions for glass and lights. Also allow more than 2 colors, but minimizing the number of colors \
and combining all similar colors into large chunks of single-color voxels."* A face's shades, lines and lit \
edges are its material's one colour; the grass hanging over a face is its top tile's grass; a fall's water and \
foam its river's water; the copied ground tiles are the ground collection's own TwoColor tiles, each of their \
groups one colour. There is no glass and no light in terrain.
- **Cartoon_TwoColor**, **CratePalette_TwoColor**, **Cartoon_CratePalette_TwoColor**: the combinations, each \
on its geometry's exact occupancy.

Palette index 255 (the game's blood) is never used; every material is diffuse.

## Checks

- [validate.py](validate.py) reads every file back (%d files, %d problems): its canvas whole tiles and levels, \
its voxels the manifest's, grounded, one connected model, index 255 unused, no glass; each treatment on its \
geometry's exact occupancy and Cartoon a different shape; the crate palette byte for byte; one colour a \
material in TwoColor; a piece's lowest level holding its lower ground tile intact, a Fill's top its upper \
tile's; and the %d files of ChatGPT's of before 2026-10-28 in the image folders unchanged \
([preserved-hashes.json](preserved-hashes.json)).
- [qa/structural-audit.json](qa/structural-audit.json): the workspace's own `tools/inspect_vox.py` over every file.
- [qa/whole-import.json](qa/whole-import.json): every file read and meshed whole by the game's own MagicaVoxel \
importer at Scale 0.0625 in a scratch copy of VCOM (%d of %d: counts, grounded, size).
- [qa/integration-report.json](qa/integration-report.json): **in the game** (a scratch copy of VCOM checked \
identical to the real one first), every style in every treatment and every island: the delivered files cut into \
the game's cells and laid out (the standard layout: straight runs, outer and inner corners, a ridge with both \
ends, a pillar, the fill and the style's extras, on a field of its ground), the rules asked: every tile a floor \
at its level and nothing stood on inside a cliff, a one-level face climbed and a taller one not, the plateau \
reached from below only over a one-level face (a floating one from its own top), and the level stamped voxel for \
voxel as the files are (%d scenes, %d passing every check). [qa/renders/](qa/renders/) has a few by day, dusk \
and night in the game's renderer.

## What to know when using them

- **Kit pieces join at one height and one style.** A raised area of one style is all its pieces; a step from one \
height to another, or one style to another, is two raised areas meeting, not a transition piece. A diagonal \
ledge (poke_g's) is laid out stepped, as tiles are.
- **The heights are as drawn**, so the tallest are tall: poke_n's red rock 9 levels, poke_d's river cliffs 6, \
poke_b's three-course cliffs and poke_d's retaining wall 5. They are measured with each image's K, which the \
buildings were made with; the [stairs collection](../stairs/README.md) measured its rises differently (poke_b's \
and poke_k's stairs rise 32 voxels, 2 levels), so its stairs are lower than these cliffs: a stair climbs \
part of a face, or the stair's rise wants revising.
- **Water is static, opaque voxel art**, as the ground collection's: the rules see a fall's or a pool's cell as \
solid ground, nothing in VCOM swims or flows.
- **A cave mouth, an archway and a drain are recesses in one tile** (11 voxels deep at most, a dark end), not \
passages: to the rules the cell is solid. The [Codex waterfalls and caves](../codex_waterfalls_caves/README.md) \
are whole models of the falls' curtains and of cave entrances with real passages, meant to be placed beside \
cliffs; these kits are those cliffs, with a fall or a mouth of their own as a piece.
- Approximations: the faces' depths, hidden sides and the islands' undersides are inferred from 2D art; poke_o's \
orange outcrop is cut off by the frame (its top tier measured); poke_u's narrow fall is clipped in the art and \
reconstructed; poke_s is a blurred JPEG.

## Reproduction

```
python output/terrain/generate.py           # writes the files and manifest.json (refuses others' files)
python output/terrain/validate.py           # validation-summary.json
python output/terrain/compose_previews.py   # previews and overview.png
python output/terrain/document.py           # these documents
python output/terrain/qa/terrain_test.py --game <scratch copy of VoxelXCOM/vcom> --files output [--render]
```

`styles.py` holds every style (its family, levels, colours, ground tiles, measurements and notes), \
`families.py` the families, `kit.py` the pieces and painting, `layout.py` the autotiling, `islands.py` the \
whole islands. The generator writes only the files its manifest lists, and refuses any file already there that \
it did not write.
""" % (n_styles, n_pieces // 7, format(len(files), ","), format(n_pieces, ","), n_islands,
       sum(len(v) for v in m["islands"].values()),
       "\n".join("- **%s**: %s." % (p, PIECE_WORDS[p]) for p in kit.PIECES),
       "\n".join("- **%s**: %s." % (p, w) for p, w in EXTRA_WORDS.items()),
       "\n".join(rows),
       "\n".join("- **%s**: %s." % (f, w) for f, w in FAMILY_WORDS.items()),
       len(files), len(val["problems"]), val.get("preserved_checked", 0), whole_ok, len(whole), n_scenes, passed)
    write(root / "terrain" / "README.md", readme)

    # ------------------------------------------------------------------ FILES
    lines = ["# Terrain kit files", "",
             "Every file of the [terrain kits](README.md), %d in all: a row a piece (or island), its seven "
             "treatments across. Files are in `output/<image>/`." % len(files), ""]
    for src in sources:
        lines += ["## %s" % src, ""]
        for s in by_source[src]:
            lines += ["### %s (%s, %d level%s)" % (s["name"], s["family"], s["levels"], "" if s["levels"] == 1 else "s"),
                      "", "| Piece | " + " | ".join(m["treatments"]) + " |",
                      "| --- |" + " --- |" * len(m["treatments"])]
            pre = STY.prefix(src)
            for p in s["pieces"]:
                cells = ["[vox](../%s/%s_%s_%s%s.vox)" % (src, pre, s["name"], p, suffix(t)) for t in m["treatments"]]
                lines.append("| %s | %s |" % (p, " | ".join(cells)))
            lines.append("")
        for isl in m["islands"].get(src, []):
            pre = STY.prefix(src)
            lines += ["### %s (whole island)" % isl["name"], "", "| " + " | ".join(m["treatments"]) + " |",
                      "|" + " --- |" * len(m["treatments"]),
                      "| " + " | ".join("[vox](../%s/%s_%s%s.vox)" % (src, pre, isl["name"], suffix(t))
                                        for t in m["treatments"]) + " |", ""]
    write(root / "terrain" / "FILES.md", "\n".join(lines))

    # ------------------------------------------------------------------ per image
    for src in sources:
        pre = STY.prefix(src)
        img = IMAGE_FILE[src]
        ss = by_source[src]
        count = sum(1 for r in files if r["source"] == src)
        parts = ["# %s terrain" % src, "",
                 "2026-11-03/04: **%d style%s, %d complete VOX files**, the ground shapes of [%s](../../../%s), "
                 "kit pieces on VCOM's grid in Base and the six variations. The files are in this image's folder, "
                 "`%s_<Style>_<Piece>[_<Treatment>].vox`. How a piece is made, placed, painted and checked: the "
                 "[collection's README](../../terrain/README.md); every file: [FILES.md](../../terrain/FILES.md)."
                 % (len(ss), "" if len(ss) == 1 else "s", count, img, img, pre), ""]
        for s in ss:
            extra = [p for p in s["pieces"] if p not in kit.PIECES]
            parts += ["## %s" % s["name"], "",
                      "![%s](previews/%s_layout.png)" % (s["name"], s["name"]), "",
                      "**%s**, %d level%s (%d voxels from its lower ground's top to its own): %s." % (
                          s["family"], s["levels"], "" if s["levels"] == 1 else "s", 16 * s["levels"],
                          FAMILY_WORDS[s["family"]]), "",
                      "- **As drawn:** %s" % s["note"],
                      "- **Scale:** %g of the image's pixels a tile, K %g; measured in the crop x %d-%d, y %d-%d "
                      "(beside the voxels above, at one scale)." % (s["px_per_tile"], s["K"], s["art_crop"][0],
                                                                   s["art_crop"][2], s["art_crop"][1],
                                                                   s["art_crop"][3]),
                      "- **Ground:** on top `%s`, below `%s`%s." % (
                          s["top"] or "its own rock", s["bottom"] or "nothing (it floats)",
                          "".join("; the %s's top `%s`" % (p, f) for p, f in s["tops"].items()) +
                          "".join("; the %s's pool `%s`" % (p, f) for p, f in s["bottoms"].items())),
                      "- **Colours:** " + ", ".join("%s #%02x%02x%02x" % (k, *v["rgb"]) for k, v in
                                                     s["labels"].items()) + ".",
                      "- **Pieces:** %s%s, each in seven treatments: [every piece](previews/%s_pieces.png), "
                      "[the seven treatments](previews/%s_treatments.png)." % (
                          ", ".join(kit.PIECES), (" and " + ", ".join(extra)) if extra else "", s["name"], s["name"]),
                      ""]
        for isl in m["islands"].get(src, []):
            parts += ["## %s (a whole island)" % isl["name"], "",
                      "![%s](previews/%s.png)" % (isl["name"], isl["name"]), "",
                      "The island rim's pieces laid out as `%s` (rows from the back), its rock hanging %d levels "
                      "below them and tapering to a point: `%s_%s[_<Treatment>].vox`, one model on the grid." % (
                          " / ".join(isl["rows"]), isl["underside_levels"], pre, isl["name"]), ""]
        write(root / src / "terrain" / "README.md", "\n".join(parts))

    # ------------------------------------------------------------------ knowledge
    notes = """# Terrain kits: authoring notes

Completed 2026-11-04: [%d styles, %d files](../output/terrain/README.md) covering the ground shapes of all 25 \
images (the backlog's item 5 with the cave mouths, waterfalls and retaining walls of items 6-8 as pieces of them). \
Read the collection README and `output/terrain/styles.py` before adding to it.

- **The user's calls (2026-11-03):** modular kits a style an image; heights as drawn, whole levels; cave mouths, \
waterfalls, retaining walls included (not Mario's backdrop hills); islands as rim pieces and a few whole islands.
- **Measuring a height:** profile a column of the face (`vprofile` of the face's colours, rim to foot), drawn \
pixels times 16 over the pixels a tile, over K, over 16, rounded. K is the image's buildings' (0.46 default; poke_m \
0.5; poke_o, poke_r 0.375; poke_u 0.4375; Pixelwood 0.88, Mario 0.7). Check each profile against a crop with the \
column marked: profiles that cross a tree or a roof read nonsense.
- **Scales:** native maps 16 px a tile; poke_a 12.25 and poke_j 12.25, poke_i 9.5, poke_k 14.75 (the stairs used \
14.72), poke_s about 10; Pixelwood A and C 48 (3x), B 80 (5x); Mario 48.
- **Adding a style:** a family (or a new `Style` subclass in `families.py`), colours as `label: (RGB, group, crate \
class)` from the art, the image's ground tiles from output/ground's manifest, `add()` in `styles.py`; then \
`preview.py <image>` beside the art, `generate.py`, `validate.py`, the in-game test.
- **Rules learnt the hard way:** every face pattern must repeat every 16 voxels (Cartoon ones too, so doubled \
widths must still divide 16); a water tile's surface is z 13, two below the grass, so the body stands from just \
above the lower tile's surface; a fall's foam lies on the pool, never inside its tile; copied ground keeps its own \
tile's colours in every treatment (merging a tile's substrate into the body in TwoColor put a seam beside the plain \
tiles); a TwoColor flat colour must be cached (asked once a voxel); rounding at corners can cut off crumbs of a few \
voxels (dropped); a floating rim's tucked rows must not vanish down a ridge's middle; Cartoon must differ in shape \
on every faced piece (its rim a voxel further out does it).
- **Stairs:** the stairs collection's rises are lower than these heights (see the README); reconcile one with the \
other before building a map from both.
- **Neighbours:** output/ground (the tiles reused), output/stairs, output/bridges, \
output/codex_waterfalls_caves (whole falls and cave entrances to stand beside these cliffs).
""" % (n_styles, len(files))
    target = kit.ROOT / "knowledge" / "TERRAIN.md" if root == (kit.ROOT / "output") else root / "knowledge_TERRAIN.md"
    if target.exists():
        assert target.read_text(encoding="utf-8").startswith("# Terrain kits: authoring notes"),             "%s is someone else's: not overwritten" % target
    write(target, notes)
    print("documents written")


if __name__ == "__main__":
    main()
