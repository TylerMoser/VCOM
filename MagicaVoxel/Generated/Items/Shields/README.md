# Shields

32 complete editable VOX models: four distinct designs for each shield type in `Brainstorming/Items.txt`.

| Type | Designs |
| --- | --- |
| Buckler | IronBoss, BronzeSun, DuelingSpike, FlutedGuard |
| Wooden | OakPlanks, PaintedKite, ReinforcedPalisade, ForestWard |
| Hide | RawhideOval, TribalSun, BoneWard, HunterChevron |
| Steel | KnightHeater, RivetedKite, RoyalGuard, BlackenedPlate |
| Tower | LegionScutum, OakPavise, AzureBastion, IronRampart |
| Fortress | CastleGate, DwarvenBulwark, RoyalWall, SiegeMantlet |
| Round | VikingQuartered, BronzeSunburst, ForestSpiral, IronRings |
| Ballistic | Patrol, Breacher, Riot, HeavyAssault |

Files use `Shield_<Type>_<Design>.vox`. All include rear grips. Z up, negative Y front, scale 0.0625, grounded scene transform. Bucklers are 7–9 voxels tall; fortress shields 27–29, relative to the 28-voxel character. Three ballistic models have Glass viewports. Palette index 255 is reserved and unused.

All 32 passed structural and current importer checks and were rendered from front and rear. Equipping, animation, collision and combat behavior are not configured.

[Previews, generators and validation](../../../../VoxelRidgeInspiration/output/items_shields/README.md) · [Overview](../../../../VoxelRidgeInspiration/output/items_shields/Overview.png)

Do not overwrite hand edits: the generator records and checks model hashes before replacing its own files.
