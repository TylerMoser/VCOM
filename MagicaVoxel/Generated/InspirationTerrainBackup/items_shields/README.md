# Shield collection — 2026-11-05

32 original complete models, four designs for each of the eight shield types in `VoxelXCOM/Brainstorming/Items.txt`. Delivered directly to `VoxelXCOM/MagicaVoxel/Items/Shields/`. No source image was used. The request for several variations is interpreted as distinct item designs, with four different occupied geometries per type, rather than the six named environment-art treatments.

| Type | Designs | Width × height range |
| --- | --- | --- |
| Buckler | IronBoss, BronzeSun, DuelingSpike, FlutedGuard | 7–9 × 7–9 |
| Wooden | OakPlanks, PaintedKite, ReinforcedPalisade, ForestWard | 11–13 × 13–17 |
| Hide | RawhideOval, TribalSun, BoneWard, HunterChevron | 11–13 × 13–17 |
| Steel | KnightHeater, RivetedKite, RoyalGuard, BlackenedPlate | 11–13 × 15–19 |
| Tower | LegionScutum, OakPavise, AzureBastion, IronRampart | 13–15 × 23–25 |
| Fortress | CastleGate, DwarvenBulwark, RoyalWall, SiegeMantlet | 19–21 × 27–29 |
| Round | VikingQuartered, BronzeSunburst, ForestSpiral, IronRings | 13–15 × 13–15 |
| Ballistic | Patrol, Breacher, Riot, HeavyAssault | 13–17 × 21–25 |

Names: `Shield_<Type>_<Design>.vox`. All files are complete shields, including the rear grips. They vary in outline, dimensions, raised bosses/spikes/ribs/bands, decorative motifs, panel construction and palette. Fortress is interpreted as a broad fantasy siege shield; Ballistic as modern opaque protective shields, three with small glass viewports and one solid Riot design. These are visual interpretations, without protective stats or gameplay behavior.

## Scale, axes and materials

MagicaVoxel Z up; X across the face; negative Y is the decorated front; positive Y is the rear. Body panels are two voxels thick with a stepped convex front. Total depth is 6–8 voxels including protrusions and rear grips. Grips have open hand clearance and connected mounting lugs; wide models have two grips. The exact occupied dimensions fill the canvas, listed in `manifest.json`. Ground plane z=0, horizontal scene centering, translation `0 0 floor(height/2)`, scale 0.0625.

The size reference is `MagicaVoxel/Characters/Character_Bigger.vox`, occupied z=0..27 (28 voxels tall). Bucklers are hand/forearm-sized; Tower is almost full-body; Fortress is a broad full-height barrier. These models are grounded for authoring. Equipping them requires a separate hand attachment transform and animation review; none is claimed here.

Explicit authored palettes: panel, alternate panel, rim, hardware, emblem, grip, and (where used) glass. Colors are in `generate.py`, with semantic assignments made directly by the construction rules. Slot 255 is unused. Metal is represented by opaque metal-colored diffuse voxels to remain readable in the current renderer. Viewports use actual MagicaVoxel Glass `_trans=.65`, and replace both opaque panel layers so their openings are unobstructed. No glass/liquid interface issue applies here.

## Evidence

`structural-audit.json`: workspace inspector, 32 models, no warnings/errors.
`validation.json`: saved-file dimensions, full connectivity, grip clearance, glass materials, all eight types/four unique geometries each, hashes.
`import-validation.json`: current VCOM importer, all 32 models retain exact voxel counts, dimensions and grounding; glass surfaces confirmed for all three viewports. Copied importer hashes are in `importer-provenance.json`. All front views and rear views rendered in isolated `qa/`; reviewed for silhouettes, decoration, grip attachment and viewports. This validates standalone imported meshes, not shield equipment, blocking, collision, combat or the separate VoxelModel runtime renderer. No game source or resources were changed.

[Overview](Overview.png). Each type also has `<Type>_comparison.png`, with fronts above and backs below. Panels are framed individually, not at a common world scale. Raw captures live in `previews/`.

## Reproduction and preservation

Run `generate.py` to write its 32 declared models, then `validate.py` and `tools/inspect_vox.py`. The generator refuses to replace an unknown or hand-edited file. All geometry is deterministic; there is no random seed. `setup_qa.py` refreshes the isolated importer and adapts the previous bottle import/render harness. Import the scratch project with Godot 4.7, then run `qa/probe.gd` with this folder's absolute path as the first user argument; `sheets.py` builds the contact sheets. Generators, evidence and previews stay in this workspace; only the complete models and an index are placed in the requested game authoring folder.
