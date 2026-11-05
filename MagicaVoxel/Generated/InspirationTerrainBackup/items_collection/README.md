# Complete item collection — 2026-11-05

[Delivered catalog](../../../VoxelXCOM/MagicaVoxel/Items/CATALOG.md) (absolute destination: `C:/Users/tandm/Documents/Projects/VoxelXCOM/MagicaVoxel/Items/`). The relative link above is supplied for a sibling-project arrangement; use the absolute catalog path if your viewer resolves it differently.

The user approved four distinct designs per type, a crate-palette counterpart for every model, preserving the existing models, both standalone and fitted wearable versions, 20–25 chosen types per open-ended category, elemental/environmental effects, and a mixed fantasy / World War I aesthetic. No image reference is involved.

## Delivered scope

- **387 explicitly cataloged new item types** × four distinct designs × two palettes = **3,096 standalone files**.
- **57 wearable types** (Armor, Boots, Helmets, WornItems) × four designs × two palettes = **456 additional fitted files**.
- **87 palette counterparts** for all existing files: 45 bottles, 32 shields, 10 original swords/rifles/grenades/medkit models.
- **3,639 new complete VOX files**, **87 preserved originals**, **3,726 total item VOX files** in 24 category folders plus the preserved legacy files at the Items root.

The 22 expanded categories are Stims 20, HealingSupplies 20, Potions 46, Rounds 41, GrenadesBombs 37, Guns 9, Attachments 6, Melee 12, Swords 8, Axes 3, Hammers 3, Bows 7, ThrownWeapons 2, WornItems 3, Armor 10, Boots 22, Helmets 22, MagicFocus 24, Food 24, MagicScrolls 24, MagicItems 24, Torches 20. Existing Bottles and Shields remain in their prior folders. Full names and category mappings are in `catalog.py`, `catalog.json`, and the delivered category catalogs.

Chainmail/Chain Mail is normalized to Chainmail; Ring Mail is a distinct RingMail. Shortword is interpreted as Shortsword. The already-modeled and implemented entries receive four new designs too (Longsword, Greatsword, Shortsword, Rifle, StickGrenade); Medkit is covered by FieldMedkit and the wider healing-supply selection, alongside a palette counterpart of the untouched original. “Rounds: all types below” is interpreted as the grenade/effect types as approved, not ammunition versions of unrelated melee weapons. “Magic Items of all kinds” is bounded to 24 chosen relic/utility types. Magic jewelry is delivered as standalone relic props; the explicit fitted set is Armor, Boots, Helmets and WornItems.

Potions cover three healing tiers, mana, the seven current UI stats and 35 named elemental/environmental/debuff effects. Rounds include standard, armor piercing, tracer, buckshot, slug and high explosive, plus those effects. Bombs include fragmentation and stick grenade plus those effects. The Fire/Incendiary, Frost/Ice and Shock/Lightning entries are intentionally separate visual concepts. These names describe art, not implemented abilities or protective performance.

## Geometry, palette and placement

One complete model per file, no cell exports. All new geometry is deterministic, with four distinct occupied-coordinate sets per item type. Authored semantic slots include steel, dark iron, wood, leather, brass, cloth, effect color, glass, emission, pale material, dark material, food, foliage, and preview-body neutral. These slots are defined in `voxlib.py`; builders choose meaningful structure and details rather than changing only colors. The default labels Field/Veteran/Officer/Arcane describe options, not previously defined Cartoon/TwoColor treatments. Some families use more specific geometry labels (e.g. RoundFlask, SquareFlask, Longneck, FacetedFlask).

Standalone models use tight canvases with ground z=0, MagicaVoxel Z up, translation `0 0 floor(height/2)`, explicit palettes and scale 0.0625. Long firearms point along +X with stock at -X; swords and polearms point up +Z; most decorated front faces look toward -Y. Crossbows run along Y. Consult the model preview before choosing an attachment transform. The maximum side is below the current 62-voxel whole-model limit; the larger items are not 16³ PieceKinds.

CratePalette uses the exact 1024 RGBA bytes of `knowledge/palettes/crate-palette.json`, SHA-256 `b1a4e811c89d143b006c0a421443dd2e1b3b9da0b6588b176c4d072b67c279c2`. This snapshot matches the current original BrightCrate1 palette checked during scope review. Nearest RGB matching selects only indices 1..254, with reservations preventing colors with different material dictionaries from collapsing onto one index. No new colors are introduced. Each output's original-to-palette mapping is recorded. All occupied coordinates and all material properties are preserved in each palette twin. Existing source scenes retain non-palette chunks and their original transforms; old MATT/IMAP metadata is replaced by explicit MATL/XYZI mapping in the new counterpart, never in the original file.

Glass and emission use separate material indices. The first two potion shapes have semi-transparent liquid, the other two opaque liquid; all have glass bodies. Previously delivered bottles retain their complete seven-color/transparency matrix. Emission `_flux=0` gives a luminous surface without promising registered environmental light. Current imported meshes merge glass materials and suppress touching glass interfaces, so glass liquids are faint in that preview path. Saved VOX settings remain separate. Runtime tests verify data and meshing, not physically correct refraction or actual liquid simulation.

## Wearable fitting

Fitted files contain **equipment only**, at Character_Bigger's original coordinates, in a 32×32×32/40 canvas. Standalone counterparts are exact translations of those gear voxels into tight grounded canvases. Paired boots intentionally have two components; every other newly authored item is face-connected. Some wearable voxels replace exposed body colors; composing them over the unchanged body preserves every original occupied body position.

Every fitted file has an exact bone-region record in `layouts.json`, also supplied per category in `Items/<category>/Fitted/layouts.json`, and integration notes in the adjacent `FITTING.md`. Shoulder additions at z=19 belong to upper-arm bones rather than the neck. The current rig's centering is handled by shifting its original joints according to the *combined body-and-gear* bounds, not by modifying VoxelRig or recentering the gear. This was tested with the existing rig API. These are placement and rigging deliverables, not registered inventory/equipment resources.

## Validation evidence

- `preserved-originals.json`: all 87 pre-existing model hashes, verified unchanged.
- `structural-audit.json`: standard workspace inspector across all 3,726 item files, zero errors/warnings.
- `validation.json`: all 3,639 generated files checked from disk for structure, counts, dimensions, material-aware palette geometry equality, face connectivity, exact standalone/fitted translation, exact gear-to-bone coverage and four distinct geometries per item type.
- `import-validation.json`: all 3,639 final hashes read/meshed/rendered through the copied current importer, with count/bounds/transparency checks.
- `runtime-validation.json`: all 3,639 final hashes read with current VoxelShape and meshed through current VoxelModel, retaining counts and glass classification.
- `rig-validation.json`: all 456 fitted models, with gear over the actual body, produce skinned meshes with exact gear-bone assignments. All **228 Base wearable designs** generate the current **56-animation library** and are captured standing, running, crouching and striking with a sword. Palette twins are rig-checked and share exact geometry.
- `final-verification.json`: final evidence/file hash agreement and current-source provenance.

Every generated model is rendered; every new Base design also has a rear view. `sheets/` holds 387 item comparison sheets plus category overviews and fitted-on-body contact sheets. `pose_sheets/` holds 57 four-design/four-pose sheets. Representative sheets were visually reviewed for silhouette, palette fidelity, grips, wearable placement and animation behavior; automated coverage is exhaustive, manual review is representative. No exhaustive cross-equipment collision test, all-species fit test or combat simulation is claimed. Only the scratch copy of VCOM was run; game source and existing hand-authored models were preserved. The runtime logged a harmless existing GL Compatibility warning that 2D MSAA is unsupported; no script/runtime errors were present.

## Reproduction

Python 3 and Pillow; Godot executable used: `C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe`.

1. `python output/items_collection/preflight.py`
2. `python output/items_collection/build.py` (refuses unowned or modified output files; verifies preserved originals)
3. `python output/items_collection/validate.py`
4. `python tools/inspect_vox.py ../VoxelXCOM/MagicaVoxel/Items --output output/items_collection/structural-audit.json`
5. `python output/items_collection/setup_qa.py`; import the isolated `qa/` project, then run its `probe.gd` with this support directory's absolute path as the first user argument. The probe skips only hash-and-script-matching finished captures.
6. `python output/items_collection/setup_runtime.py`; import the isolated `qa_runtime/` project, then run its `items_probe.gd` with `--rendering-method gl_compatibility` and the same support directory argument. This validates the current runtime and rig; do not run it in the real game project.
7. `python output/items_collection/sheets.py` and `python output/items_collection/document.py`.
8. `python output/items_collection/finalize.py` checks all final evidence before reporting completion.

Sources: `catalog.py`, `voxlib.py`, `weapons.py`, `objects.py`, `wearables.py`, `build.py`. No random seed or generated bitmap source is used. Category docs and preview copies are generated; preserve any manually edited exports separately. Regenerating with changed source originals requires deliberate manifest review rather than silently adopting different references.
