# poke_s sky-garden ruins and temple architecture

Created 2026-11-03 from `poke_s.jpg`: **11 families, 77 complete VOX files**, Base plus the six established variations. Models live directly in [output/poke_s](../); this directory holds the reproducible generator, source crops, manifests, previews and validation evidence. No individual cell files or brush packages are generated.

[Overview](overview.png) · [All 77 files](FILES.md) · [Main temple assembly](temple_assembly.png) · [Manifest](manifest.json) · [Validation](validation-summary.json) · [Godot import evidence](godot-validation.json)

## Source interpretation

The enlarged image shows **open-topped, rounded garden terraces**, not roofed classical temples. Pale staggered masonry, white coping, vertical ivy, inset arches, garden pockets and broad central stairs establish their identity. The large northern court carries four round columns and an existing statue; smaller round terraces repeat on the west and east. The lower-left island has a two-stage stepped sanctuary. The lower-middle structure is tucked beneath a cliff. Their obstructed backs and interiors are inferred, not recovered from source pixels.

The earlier coverage audit's terms “pavilions,” “rotundas” and “ruined facades” are approximate visual labels. No invented pitched roofs, rubble heaps or broken pediments were added. `ArcadeWall` and the straight/corner retaining sections are reusable constructions derived from the source architecture, not claims that each is a separate exact sprite. Small dark arches are ambiguous: both a real underpass and recessed masonry version are provided for the repeated garden terrace.

Scale follows the existing poke_s interpretation: approximately **10 displayed JPEG pixels per original tile, 16 voxels per tile**. Source crops are context rectangles, not masks. Horizontal footprints are rounded to the tile grid; heights and hidden depth are estimates. Z is up; front is -Y (Godot +Z); one voxel is 0.0625 game units. Every model starts at z=0 and has scene translation `0 0 floor(canvas_height/2)` for grounded whole-mesh import. Refer to the manifest for occupied bounds, which can be smaller than the canvas.

## Families

| Model prefix `PokeS_Ruins…` | Canvas XYZ | Purpose |
| --- | --- | --- |
| Column | 32 × 32 × 72 | Round ivy-covered column with foot and cap rings. |
| GardenRotunda | 64 × 64 × 48 | Rounded planted terrace with a real arched underpass. |
| RecessedRotunda | 64 × 64 × 48 | Same architectural appearance with a closed, recessed masonry arch. |
| TempleWing | 96 × 112 × 64 | Raised garden flank with coping, ivy, main arch recess and small inset. Reuse on either side. |
| TempleCore | 192 × 240 × 128 | Northern raised court, four columns, broad stair and two blue-gray arched panels. |
| TerraceGateway | 96 × 32 × 64 | Broad pass-through arch below the northern court, with upper ledge. |
| SteppedSanctuary | 80 × 128 × 112 | Lower-left two-stage terrace with two stair flights and paired uprights. |
| CliffSanctuary | 64 × 64 × 80 | Lower-middle recessed doorway structure and open garden rim. Surrounding cliff is a separate terrain asset. |
| ArcadeWall | 96 × 16 × 64 | Two-bay open arched masonry wall with broad coping. |
| TerraceWall | 64 × 16 × 48 | Straight solid garden retaining wall. |
| TerraceCorner | 32 × 32 × 48 | Rounded L-shaped retaining corner, matching wall body/coping thickness at its ends. |

### Main temple assembly

The full source complex is roughly 24 tiles wide, beyond the single-model VOX axis limit of 256 voxels. Keep its whole architectural sections separate rather than shrinking it or exporting hundreds of cells:

| Section | Offset XYZ in authoring voxels, relative to the core's horizontal center and ground |
| --- | --- |
| TempleCore | `(0, 0, 0)` |
| TempleWing, left | `(-144, 0, 0)` |
| TempleWing, right | `(144, 0, 0)` |

Whole-mesh Godot offsets are `(-9,0,0)` and `(9,0,0)` for the wings. Mirror the right wing across local X (`scale.x=-1` for a MeshInstance3D) to balance its small inset; future voxel stamping must mirror voxel coordinates explicitly. Total assembled canvas footprint is **384 × 240 voxels**. These offsets put adjoining section faces together and match their terrace surfaces at z=48. Side gardens retain their low rims; they are not indoor rooms. The assembled preview shows these three sections without the already-existing statue or plant models. Placement data is also in [assembly.json](assembly.json).

Reuse `PokeS_CourtyardStatue` on the court (place its bottom at z=48), and the existing poke_s trees, shrubs, lamps, fountain and balustrade where desired. Do not generate duplicates of those collections. `TerraceGateway` is a separate southern architectural feature, not automatically placed over the core's stair. The cliff sanctuary's rock overhang, floating islands, waterfalls and free river bridges remain outside this architecture batch.

## Seven treatments

Names follow the shared canonical suffixes: no suffix for Base, then `_Cartoon`, `_CratePalette`, `_TwoColor`, `_Cartoon_TwoColor`, `_CratePalette_TwoColor`, `_Cartoon_CratePalette_TwoColor`.

- **Base:** source-inspired warm limestone, recessed mortar, green ivy and blue-gray inset stone. RGB choices are manually interpreted from the compressed reference, not a claim of exact original sprite colors. All materials are opaque diffuse; the blue insets are stone panels, not invented glass or lights.
- **Cartoon:** broader rounded corners, wider column shafts, chunkier coping on wall sections, larger regular masonry/paving courses and simpler ivy paint. It preserves the directional stair, arch and garden design. Corner sections keep their L shape; the wing keeps its small off-center inset. Repetition is regularized; exact quarter-turn symmetry is not asserted for directional architecture.
- **CratePalette:** exact Base occupancy, the pinned crate RGBA palette copied byte-for-byte. Limestone maps within indices 193–196, ivy 241–246, blue inset 249–254, by nearest RGB. The manifest records the mapping and palette hash.
- **TwoColor:** follows the user's amended minimal-color rule. All stone/mortar/coping/paving merge into one flat stone color, all ivy/grass into one flat green; the temple's blue inset panels retain their third material color. No painted shading remains inside a group.
- **Mixtures:** use the exact Base or Cartoon occupancy as specified, and the same semantic flat-color representatives. No color-only variant changes geometry. Index 255 is unused.

## Validation and limitations

`generate.py` writes one rooted, one-model VOX per treatment; reads each back; checks its palette and occupied voxels; checks connectedness; and preserves prior files. A rerun refuses to overwrite an existing model whose hash no longer matches its previous manifest entry.

`validate.py` independently reads the saved files, checks structure, unique coordinates, dimensions, grounding transforms, connected Base/Cartoon geometry, distinct Cartoon geometry, exact recolor occupancy, flat semantic groups and the pinned palette. It also checks the hashes of **336 pre-existing poke_s VOX files**.

`qa/probe.gd` uses a copied snapshot of the **current VCOM MagicaVoxel importer** at scale 0.0625. It checks flattened voxel count and mesh bounds/grounding and renders every style, plus four cardinal views of Base and Cartoon. `qa/source-provenance.json` pins the copied importer. Previews use the imported Mesh, not the game's combat-level voxel shader. The main assembly has a separate preview. Geometry sheets include a source crop for comparison; all-style sheets are independently framed for each family.

These are complete authoring models, **not registered combat pieces**. Many exceed the runtime whole-prop width limit of 62 voxels, and none should simply be assigned to one 16³ PieceKind. Future combat integration must handle their multi-tile geometry and rules separately. No game project files were changed, and navigation, cover, cutaway, destruction or battle behavior is not claimed tested. The rotunda's small arch is scenery-scale and does not guarantee soldier clearance. Stairs encode geometry only.

## Reproduce

From the workspace root, with Python and Pillow:

```powershell
python output/poke_s/ruins/generate.py
python output/poke_s/ruins/validate.py
python output/poke_s/ruins/setup_qa.py
```

Run Godot 4.7 with `--path output/poke_s/ruins/qa/game --script <absolute-path-to-qa/probe.gd> -- <absolute-workspace-path>` to refresh render evidence, then run `python output/poke_s/ruins/sheets.py`. `setup_qa.py` refreshes the isolated importer copy and its provenance; it never edits VoxelXCOM. Final render hashes must match the manifest before considering a regenerated batch reviewed.
