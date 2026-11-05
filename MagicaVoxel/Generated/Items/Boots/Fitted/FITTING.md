# Fitted equipment

These are complete equipment overlays at Character_Bigger's original T-pose coordinates (32×32×32, or 32×32×40 for tall helmets). X across, negative Y front, Z up. The original body remains at its existing coordinates. Overlay the gear on the body, letting gear colors replace exposed body voxels where they overlap; do not center or ground the gear independently. Paired boots are deliberately two components in one file.

`layouts.json` gives exact equipment bone regions, one contiguous X run per row. Put these regions BEFORE the base CHARACTER_BIGGER regions. Arm-top armor at z=19 is assigned to the upper arms, not the neck. Every gear voxel was checked against its assigned bone and every fitted file made a skinned mesh in the current VCOM rig.

Current VoxelRig centers each model on its occupied bounding box. On the combined body-and-gear model, compute `cx=(minX+maxX+1)/2`, `cy=(minY+maxY+1)/2`. Add `(16.5-cx, 0, cy-16.0)` to every original CHARACTER_BIGGER joint (Godot axes), preserving the original scale .063. The test harness uses this existing supported layout approach; no game source changes were made. Do not use the equipment-only bounds to calculate this shift. The alternative requires an explicitly supported fixed-body center in a future rig version.

Standalone counterparts are the same voxels translated into a tight grounded canvas; their `original_offset` is recorded in the master manifest. The fitted version is the geometry authority for placement, and exact translation equality was tested.

All 228 distinct wearable designs were baked in the isolated QA process with 56 animations and captured standing, running, crouching, and striking. Palette twins share geometry and bone assignments. These captures and geometric checks are not an exhaustive collision test across all character species, combined equipment, weapons or animation frames. Add an actual equipment resource, attachment/dressing logic and stats separately when integrating. The original VCOM project was not changed.
