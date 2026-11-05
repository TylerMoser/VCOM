# Potion bottles

45 complete editable models: Small (3×3×5), Medium (5×5×7), Large (7×7×10). Medium is sized relative to FragGrenade and StickGrenade.

Each size has an Empty bottle and Red, Blue, Pink, Cyan, Purple, Green, Yellow liquid in Translucent and Opaque variants. All bottle bodies are hollow glass, with cork stoppers. Translucent liquid has its own 50% transparency Glass material; opaque liquid is Diffuse. Bottle glass is 85% transparent. Use scale 0.0625, Z up; grounded scene transforms are included.

Authoring sources, previews, full notes and verification: `../../../../VoxelRidgeInspiration/output/items_bottles/` relative to this folder's project sibling arrangement; absolute path `C:/Users/tandm/Documents/Projects/VoxelRidgeInspiration/output/items_bottles/`.

All 45 passed structural and current VCOM importer checks. Current greedy importer merges glass materials and hides glass-to-glass interfaces, making translucent fills appear faint and mainly visible from above. The VOX files retain separate shell and liquid material settings. Gameplay/inventory integration has not been performed.

Names: `PotionBottle_<Size>_Empty.vox`, `PotionBottle_<Size>_<Color>_Translucent.vox`, `PotionBottle_<Size>_<Color>_Opaque.vox`. Preserve hand edits; the generator checks file hashes before overwriting.
