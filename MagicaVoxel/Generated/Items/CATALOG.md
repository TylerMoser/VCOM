# Item model catalog — 2026-11-05

Fantasy / World War I-era equipment. **3,639 new complete VOX files**, plus **87 preserved originals**: **3,726 files** in Items.

The expanded catalog contains **387 item types**, each with four geometrically distinct designs and four exact-geometry `_CratePalette` counterparts. The 57 wearable types also have fitted copies: **228 wearable designs / 456 fitted files**. Existing bottles, shields and original equipment each have a new palette counterpart.

| Category | Expanded item types | New files | Browse |
| --- | ---: | ---: | --- |
| Stims | 20 | 160 | [Catalog](Stims/Catalog.md) |
| HealingSupplies | 20 | 161 | [Catalog](HealingSupplies/Catalog.md) |
| Potions | 46 | 368 | [Catalog](Potions/Catalog.md) |
| Rounds | 41 | 328 | [Catalog](Rounds/Catalog.md) |
| GrenadesBombs | 37 | 298 | [Catalog](GrenadesBombs/Catalog.md) |
| Guns | 9 | 74 | [Catalog](Guns/Catalog.md) |
| Attachments | 6 | 48 | [Catalog](Attachments/Catalog.md) |
| Melee | 12 | 96 | [Catalog](Melee/Catalog.md) |
| Swords | 8 | 69 | [Catalog](Swords/Catalog.md) |
| Axes | 3 | 24 | [Catalog](Axes/Catalog.md) |
| Hammers | 3 | 24 | [Catalog](Hammers/Catalog.md) |
| Bows | 7 | 56 | [Catalog](Bows/Catalog.md) |
| ThrownWeapons | 2 | 16 | [Catalog](ThrownWeapons/Catalog.md) |
| WornItems | 3 | 48 | [Catalog](WornItems/Catalog.md) |
| Armor | 10 | 160 | [Catalog](Armor/Catalog.md) |
| Boots | 22 | 352 | [Catalog](Boots/Catalog.md) |
| Helmets | 22 | 352 | [Catalog](Helmets/Catalog.md) |
| MagicFocus | 24 | 192 | [Catalog](MagicFocus/Catalog.md) |
| Food | 24 | 192 | [Catalog](Food/Catalog.md) |
| MagicScrolls | 24 | 192 | [Catalog](MagicScrolls/Catalog.md) |
| MagicItems | 24 | 192 | [Catalog](MagicItems/Catalog.md) |
| Torches | 20 | 160 | [Catalog](Torches/Catalog.md) |
| Bottles | Existing collection | 45 | [Catalog](Bottles/Catalog.md) |
| Shields | Existing collection | 32 | [Catalog](Shields/Catalog.md) |

## Conventions and limitations

Scale 0.0625 for source props; Z up. Standalone files are tightly bounded and grounded. Weapons and gear retain visible functional ends; attachment transforms are a separate integration step. Fitted equipment uses the character’s authored coordinate frame rather than a tight canvas.

CratePalette uses the exact original BrightCrate1 palette, including unused entries, with material-aware nearest-color remapping. Index 255 remains reserved for blood. Glass and emission are preserved on separate material indices. The palette source is the approved pinned snapshot; no new colors are introduced into that variation.

Effects, buffs, healing, ammunition types, armor protection and magic are visual item concepts. No stats, inventory entries, combat behavior or equipment system changes are included. “Chainmail / Chain Mail” is one type and “Shortword” is interpreted as Shortsword. All named entries of Items.txt are covered; open categories are explicitly expanded in their catalogs.

The current greedy importer merges touching glass materials into one surface: translucent liquids can appear faint and lose their internal interfaces. Independent VOX glass/liquid settings are retained. The separate runtime VoxelModel checks also passed, but this is not a claim of physically correct glass/liquid refraction.

[Authoring sources, evidence and reproduction](C:/Users/tandm/Documents/Projects/VoxelRidgeInspiration/output/items_collection/README.md)
