# Lights

Glowing voxels, lamps and the time of day in full: how a battle's time of day is picked and what dusk
and night look like, how a voxel glows, how to make a lamp in MagicaVoxel and what each of its numbers
does, how to override them in Godot, the street lamp, the two ways lamps light a battle (omni lights
casting hard shadows, the default, and area lights casting soft ones), how a lamp's own frame is kept
out of its shadow, how area lights are kept from leaking through walls, how broken lamps go dark, what
it all costs, how to probe it, its gaps and what was decided without asking. It was written as lights
came in (2026-10-27); `CLAUDE.md` keeps a summary ("Lamps light battles at dusk and at night...") and
the rules that must not drift. `Docs/VOXELS.md` has the rest of how every voxel model is drawn,
`Docs/LEVELS.md` the rest of a level, `Docs/GLASS.md` the glass a lantern is glazed with, and
`Docs/DESTRUCTION.md` the rest of breaking and wear. A section named here that is not in this file
(Gotchas, Verification, Known gaps, another subsystem's notes) is `CLAUDE.md`'s.

## What the user decided

The user asked (2026-10-27) to "start exploring glowing voxels, such as street lights, lamps, etc.",
with an analysis like the one done for glass: MagicaVoxel's options and Godot's. The research
(MagicaVoxel's Emit material read as a glow, nine ways of lighting the voxels round a lamp prototyped
on TestMap and BoundaryMap and timed on the Vega 8 that stands in for the Steam Deck) left the user
torn between an omni light casting hard shadows and an area light; a comparison of the two showed the
omni's "hard shadows that don't seem to come from anywhere" to be the lantern's own four corner
posts, one voxel thick and right beside the bulb. The user then decided, in their words:

- "Implement 2 different lighting options. 1. Omni hard shadows, as in your original proposal, but
  with the 4 corner posts of the light fixture not casting shadows. However, leave all other shadows,
  including the one from the large post that holds up the light. 2. Area light."
- "Make omni hard shadows the default, and make this setting togglable from the pause menu just like
  blood. Also like blood, only allow changing this setting from the world map. Once in battle, this
  setting should be disabled."
- "Give every battle a 50% chance of happening during the day, a 25% chance of happening at dusk,
  and a 25% chance of happening at night. We will eventually be expanding-on this, but for now this
  should be randomly picked at the start of any combat."
- "Yes, lights are only for show."
- "Broken lamps should go dark."
- "Set each lamp's brightness and reach in MagicaVoxel, but allow overrides in Godot. Be sure to
  fully document this."
- "Include night and dusk environments in the game now, just like the ones you created in your
  example images."
- "Persist the lamp voxel model from your examples in the repo, for future modification."
- "Leave 2 lamps next to the house in the test scene, but not on top of any crates."

XCOM 2 gave the shape of the time of day: its lighting is cosmetic, picked per mission from the
battle's local time (`XComEnvLightingManager`), and Teardown that of a broken lamp: a light belongs
to the shape that glows and goes out when the shape breaks.

## The time of day

**Every combat map has a `TimeOfDay` node** (`Scripts/Combat/TimeOfDay.gd`), which as the map loads
picks the battle's time of day, `TimeOfDay.Period`: `DAY` half the time, `DUSK` a quarter and `NIGHT`
a quarter (`TimeOfDay.ODDS`, in `pick(roll)`). It rolls on a `RandomNumberGenerator` of its own,
seeded at random, never the global generator, so a seeded fight replays the same whatever the time
of day. `TimeOfDay.forced` (static, -1) makes every battle one time of day, for probes and
harnesses; nothing in play sets it. Nothing else decides it yet: the campaign's clock
(`MapClock`) does not lead to it, and nothing on the world map says what time a battle will be.

By day the map is exactly as it was made: its `WorldEnvironment`, sky and sun (style 05, Colour
Bounce, `Styles/`). At dusk and at night `apply()` lights it otherwise, on copies of its environment
and sky (`duplicate(true)`), since the map's own resources are shared by every battle fought on it:
the next battle on the same map by day finds them untouched. The looks are the research's example
images':

| | Dusk | Night |
|---|---|---|
| Sky top / horizon | (0.16, 0.2, 0.38) / (0.85, 0.52, 0.34) | (0.012, 0.018, 0.045) / (0.045, 0.06, 0.1) |
| Ground bottom / horizon | (0.1, 0.1, 0.16) / (0.55, 0.38, 0.3) | (0.01, 0.012, 0.02) / (0.035, 0.045, 0.07) |
| Sun | orange (1.0, 0.62, 0.38), energy 0.55, 14 degrees up (`DUSK_ELEVATION`) on the map's own heading | the moon: blue (0.55, 0.66, 1.0), energy 0.22, where the sun was |
| Ambient light | the sky's, energy 0.55 | a colour, (0.11, 0.13, 0.2), energy 1.0: enough to fight by |
| Glow | on | on |

The glow is the environment's bloom: intensity 0.8, strength 1, bloom 0, soft light, from an HDR
threshold of 1, so only what shines brighter than white blooms: glowing voxels, and little else.
SSAO and SSIL stay as the map has them. Then `apply()` turns glowing voxels on: the global shader
uniform `voxel_glow` (`TimeOfDay.GLOBAL`, `project.godot`'s `[shader_globals]`, 0 there) is 1 at dusk
and at night and 0 by day. The battle's `Lamps` reads `TimeOfDay.lamps_lit()` (dusk or night) as it
loads, after it.

## A voxel that glows

**A colour glows if MagicaVoxel draws it with the Emit material.** `VoxelShape._paint()` reads each
palette entry's material from the importer's reader, as it does glass (`Docs/GLASS.md`), and gives an
Emit colour its glow in the top five bits of its flags byte: the Emission, 0 to 100%, in 31 steps
(`VoxelShape.glow_flags()`, `glow_of()`, `glows()`; an Emission above 0 never rounds down to none).
Those bits are a glass colour's clarity; a colour has one material in MagicaVoxel, so it is glass or
glowing, never both, and `glow_of()` reads 0 for glass. Beside the flags, `VoxelShape.powers` keeps
each glowing colour's Power (`_flux`), which is the light it casts (below); its `_ldr` and the rest
are not read. Blood's place never glows (`reserve_blood()` moves any Power off it).

The voxel shader (`Voxels.gdshader`) draws a glowing colour's own light:
`EMISSION = albedo * glow * glow_most * voxel_glow`, the colour itself (linear) times its glow, times
`glow_most` (8: an Emission of 100% shines eight times its own colour, well past the glow's threshold),
times the global `voxel_glow`, so by day nothing glows. That is the voxel itself shining; the light
it throws on everything round it is a lamp's (below), and only a level's pieces have lamps.

Every voxel model reads it the same way: a level's pieces, a prop, a crate's boards and, through
`VoxelRig.load_vox()`, a figure. A figure's tint (`VoxelModel.paint()`) never paints over a glowing
colour, as it never paints over glass, so a unit's lamp or visor keeps its glow.

## Making a lamp in MagicaVoxel

A lamp is a model with voxels that glow, and the light it casts is set in MagicaVoxel, on those
voxels' colour:

1. **Paint the bulb with a colour of its own**, and give that colour the **Emit** material (the
   material panel, top right, with the colour selected in the palette).
2. **Emission** is how brightly the voxels glow at dusk and at night: 75% (the street lamp's) shines
   about six times its colour; 100% eight times. 0 does not glow at all.
3. **Power** is the light the voxels cast round them, as bright and as far as this table has it:

   | Power | Brightness (light energy) | Reach (cells) |
   |---|---|---|
   | 0 | no light: the voxels only glow | - |
   | 1 | 2 | 3.5 |
   | 2 | 4 (the street lamp's) | 7 |
   | 3 | 8 | 14 |
   | 4 | 16 | 28 |

   Brightness is 2 to the Power and reach 3.5 cells times 2 to one less than the Power
   (`Lamps.REACH_AT_ONE`); a Power between steps lands between them. MagicaVoxel lights its own
   renders by Emission times 10 to the Power, far too steep for a game, so its own renders are no
   guide to how bright a lamp is in battle.
4. **The light's colour is the bulb's colour**, its RGB, not anything the material says; with
   several glowing colours, their average, weighted by how many voxels each has. Paint the bulb the
   colour the light should be.
5. **Each piece gets one light**, standing at the middle of its glowing voxels (an area light: just
   under them, below), as bright and far as the highest Power among its glowing colours. A glowing
   piece with every Power at 0 only glows. A lamp drawn as several pieces (a tall one, stacked) puts
   its glowing voxels in one piece of them.
6. **Keep anything opaque out from right beside the bulb**, or give it a colour of its own and list
   that colour in the kind's `shadowless_colors` (below): a post one voxel thick a few voxels from a
   point of light throws a hard wedge of shadow across half the map. That is why the street lamp's
   corner posts are colour 186, the same iron as colour 185, but a colour apart.
7. **A piece is 16 voxels a side.** A lamp taller than a cell is drawn whole and cut into 16-voxel
   slices, stacked as a brush (the street lamp is; its script does the cutting).
8. **Bring it into the game** as any block (`Docs/LEVEL_EDITOR.md`, "Adding kinds and brushes"): the
   `.vox` in `vcom/Blocks/` with an `.import` at Scale 0.0625, a kind in `Blocks/Pieces.tres` (a post
   is a corner piece, `corner_piece`), its destruction (a `VoxelDestruction` in
   `Resources/Destruction/`, as the fence's), and a brush for a stack.

## Overriding it in Godot

Two settings on a kind of piece (`PieceKind`, in `Blocks/Pieces.tres`, the inspector or by text)
change what MagicaVoxel says without touching the `.vox`. Like every kind's setting they are shared
by every piece of the kind, and nothing in play changes them.

**`PieceKind.lamp`**, a `LampLight` resource (`Scripts/Level/LampLight.gd`). Each of its settings
left as it is takes MagicaVoxel's; a kind with none is lit exactly as its `.vox` says:

| Setting | Default | What it does |
|---|---|---|
| `glow` | -1 (the Emission) | how brightly the voxels glow, 0 to 1, in place of every glowing colour's Emission. 0 puts the lamp out altogether: nothing of it glows, it casts no light and its bulb casts shadows as any voxel |
| `energy` | -1 (the Power's) | the light's brightness, in place of 2 to the Power. 0 casts no light; the voxels still glow |
| `reach` | -1 (the Power's) | how far the light reaches, in cells, in place of the Power's; with `energy` set on a colour whose Power is 0, 7 |
| `color` | clear (the voxels') | the light's colour, in place of the glowing colours' average; its alpha only says it is set |
| `offset` | (0, 0, 0) | where the light stands from the middle of the glowing voxels, in cells, as the model lies before the piece is turned: it turns with the piece |
| `area_size` | (0.3, 0.3) | the rectangle an area light shines from, in cells (below); its soft shadows are as soft as its larger side |

For example, a kind whose bulb should glow at half its Emission and throw a cold light ten cells,
written into `Pieces.tres` (with the script's `ext_resource` added, as the kinds' own):

```
[sub_resource type="Resource" id="Resource_coldlamp"]
script = ExtResource("<LampLight.gd's id>")
glow = 0.5
reach = 10.0
color = Color(0.7, 0.85, 1, 1)
```

and `lamp = SubResource("Resource_coldlamp")` on the kind.

**`PieceKind.shadowless_colors`**, the palette places (1 to 255, as MagicaVoxel numbers them) of the
kind's colours whose voxels cast no shadow from any lamp's light (below). The street lamp's top piece
lists 186, its lantern's corner posts. A glowing colour never casts a lamp's shadow, listed or not. A
colour listed casts its shadow from the sun and the moon as ever.

## The street lamp

The lamp from the research, kept for later work: `MagicaVoxel/Lamps/StreetLamp1.vox`, one model 16 x
16 x 48 voxels, and `make_street_lamp.py`, which drew it and cuts it into the game's three pieces
(`--split` only cuts it, after a hand edit: `MagicaVoxel/Lamps/README.md`). An iron post on a plinth
under a brass finial, an arm reaching out to a lantern: four iron corner posts, glass sides and a
glass bottom under an iron cap, a bulb inside. Its colours sit in palette places 185 to 189, above the
Apollo palette every piece takes from `MagicaVoxel/Plants/LeafCluster1.vox`:

| Place | Colour | Material | Where |
|---|---|---|---|
| 185 | iron (46, 48, 54) | diffuse | post, plinth, arm, hook, cap |
| 186 | the same iron | diffuse; the top piece's `shadowless_colors` | the lantern's corner posts |
| 187 | brass (122, 98, 60) | diffuse | the finial |
| 188 | pale glass (236, 240, 232) | Glass, Transparency 0.85 | the lantern's sides and bottom |
| 189 | warm white (255, 210, 140) | Emit, Emission 0.75, Power 2 | the bulb, 2 x 4 x 2 voxels |

So its bulb glows about six times its colour (an Emission of 75% is 23 steps of 31), and its light is
an omni light of brightness 4 reaching 7 cells, 2.25 cells over the lamp's foot and 5 voxels out
along its arm, in the bulb's warm white. In the game it is three corner pieces, `StreetLamp1Bottom`,
`StreetLamp1Middle` and `StreetLamp1Top` (`vcom/Blocks/StreetLamp1*.vox`, kinds in `Pieces.tres`),
stacked by the brush `StreetLamp1`, whose destruction is `Resources/Destruction/StreetLamp1.tres` (a
`VoxelDestruction` like the fence's: 8 voxels a damage, debris 600 kg/m3 in lumps of 2, 40 kg whole).
Being on corners, it is decoration to the fight (`CLAUDE.md`'s rules): no sight line, step, cover,
throw or round meets it.

TestMap has two, in front of its house, one off each front corner a cell out from the front wall
(corner slots (45, 2, -37), turned 0, and (53, 2, -37), turned 2), their lanterns reaching in toward
each other, on the grass of the house's plot and on no crate.

## Lamps: two ways to light a battle

**Every combat map has a `Lamps` node** (`Scripts/Combat/Lamps.gd`), after `TimeOfDay`. At dusk and
at night, as the map loads, it gives every piece of the level whose glowing voxels cast light
(`spec_of()`: MagicaVoxel's numbers and the kind's `LampLight`) one light, a child of its own named
`Lamp<piece>`, standing where those voxels are; by day it makes none and does nothing. A light is one
of two kinds, as `Lamps.area_lights` says:

- **Omni lights, casting hard shadows: the default.** An `OmniLight3D` at the middle of the glowing
  voxels, its range the reach, its attenuation 1, its shadows Godot's cube map. Shadows are sharp,
  and every opaque voxel near the bulb throws one: hence the lamp's own frame is kept out (below).
- **Area lights, casting soft shadows.** An `AreaLight3D`, a rectangle `area_size` across (0.3 x
  0.3), half a voxel under the lowest glowing voxel (`Lamps.AREA_BELOW`), facing down, its range the
  reach and its soft shadows (`light_size`) as wide as its larger side. Facing down, it sends more
  light right under the lamp and none above itself, so it is made 1.23 times as bright as the omni
  light would be (`Lamps.AREA_ENERGY`), which lights the ground about the same two metres out
  (measured on a flat floor under the street lamp: 1.13 times the omni's half a metre out, 0.97 at
  two, 0.68 at four). A wall above a lamp stays dark in its light, as the research showed. It costs
  far more (below), and its shadows are drawn from fine copies of the level (below).

**The pause menu's System tab switches between them**: **Lamp Lights: Omni** / **Area**
(`SystemTab`), beside **Blood**, and like it only between battles: greyed out while
`Campaign.in_mission`, the note under them saying "Blood and lamp lights can only be changed on the
world map". `Lamps.area_lights` is static, as `Blood.enabled` is; each map's `Lamps` reads it once,
as it loads, so a battle keeps what it began with, and nothing saves it: every launch starts with
omni lights. `Lamps` must not name `Campaign` (no probe could name it); the lock is the menu's.

## Shadows from a lamp's own frame

A lamp's light stands among its own voxels, and from there everything opaque near it throws a hard
shadow: the street lamp's four corner posts, one voxel thick and 22 cm from the bulb, each threw a
wedge some 23 degrees wide from 1.8 m out to the light's reach, the "shadows from nowhere" of the
comparison. The user had them gone and every other shadow kept, the post's among them.

**Voxels that cast no lamp's shadow are meshed apart.** As the level stamps a piece
(`VoxelVolume._stamp()`), every voxel of a glowing colour, and every voxel of a colour in its kind's
`shadowless_colors`, is marked in the chunk's `shadowless_x` / `shadowless_z` rows (laid out as the
glass rows are, and never glass), a voxel at a time, since two of a kind's colours can be the same
RGB and so the same place in the level's palette (the street lamp's 185 and 186 are). `ChunkMesher.faces()`
gives their faces as a third set, after the rest and the glass, hiding and showing faces as any
voxel that is not glass does, and `LevelRenderer` draws them as a third surface of each section's
mesh, `"shadowless"`, by `shadowless_material`: the voxel shader with `lamp_shadows` off. They
collide, take blood, wear and break as the rest do. A cut (`Docs/CUTAWAY.md`) cuts them as it cuts
the rest.

**The shader leaves them out of a lamp's shadow map only.** In a shadow pass of a lamp's light,
`Voxels.gdshaderinc` moves every corner of such a face to one point, so nothing of it is drawn into
the map; `is_lamp_pass(PROJECTION_MATRIX)` says which passes are a lamp's. An omni light's cube faces
are drawn in perspective (the projection's `[3][3]` is 0). An area light's map is a single paraboloid
Godot warps the corners into itself, in the vertex shader after the material's own code, its
projection left the depth correction alone: 1 across x, a half along z, reversed (`[0][0]` 1,
`[2][2]` -0.5); Godot 4.7's `renderer_scene_cull.cpp` and `render_forward_clustered.cpp` show it. The
sun's and the moon's maps are orthographic, never either (`[0][0]` 2 over a cascade many metres wide,
`[2][2]` 1 over its depth, positive), so the corner posts keep their shadows from the sun and moon:
by day, the frames with `lamp_shadows` on and off are the same to the pixel. The bulb casts no lamp's
shadow either; its light stands inside it. The post, arm, hook and cap cast theirs.

## Area lights' shadows from fine copies

**An area light's shadow map is a paraboloid, and the level's faces are big.** Godot 4.7 draws an
`AreaLight3D`'s shadow map in one paraboloid (dual-paraboloid's front half), warping each corner of a
face into it; the face between is drawn straight, so a face near the light, long across what the
light sees, lands in the wrong place in the map, and so does its depth. Godot's own documentation of
`AreaLight3D` warns of it. The level's faces are merged as large as their shape allows, up to a chunk
(2 cells) long, so area lights leaked through walls: a lamp shut in a house with its windows walled
up lit two crescents of ground outside it, and a lamp outside lit the inside of the walls. Nothing
of Godot's lets an area light use a cube map instead.

**So area lights take their shadows from copies of the level cut fine round them.** Once its area
lights are made, `Lamps` calls `LevelRenderer.use_fine_shadows(area lights, [the sun])`. Every
section within reach of one gets a `FineShadow` mesh of its own: its faces as they are whole (a cut
changes no shadow), cut into pieces no longer than `LevelRenderer.FINE_STEPS` allows by how far the
face is from the nearest such light (2 voxels within 1 cell, 4 within 2, 8 within 4.5, 16 beyond),
so that no corner is more than a centimetre or so from where the paraboloid should put it. Only
faces a light reaches, faces turned toward it and faces not wholly behind it are cut (a shadow map
is drawn with back faces culled, as the section is, and a paraboloid sees only what is in front);
never glass, which casts no shadow, nor the voxels casting no lamp's shadow. The copies are drawn only
into shadow maps (`SHADOWS_ONLY`), on visual layer 20 (`FINE_LAYER`); while they exist the sections,
and the whole meshes a cut keeps casting shadows, are on layer 19 (`SECTION_LAYER`) instead of layer
1. Each area light's `shadow_caster_mask` leaves layer 19 out, and the sun's leaves layer 20 out, so
the sun's and the moon's shadows are the sections' as ever. A section whose chunks are meshed again,
worn or broken, is cut again (`_fine_stale`); a light put out keeps its copies, which nothing else
sees. With omni lights there are no copies and nothing changes layer.

Everything else still casts into an area light's map as it is: units' figures, crates' boards,
debris, shards and a block falling whole, whose faces are small and whose errors are too.

**Its soft shadows are as soft as it is big.** PCSS (Godot's soft shadows) blurs a shadow by
`light_size`, 0.5 for an area light unless set, wider than the street lamp's 0.3 m lantern, and a
blur that wide reaches round a thin wall edge-on to the light: measured with a lamp standing on the
line of the house's west wall, the windows walled up, 21% of the floor inside was lit at 0.5, 10% at
0.3, 1.4% at 0.15 and none at 0, and with TestMap's own lamps 1.3% at 0.5 and none at 0.3. So
`light_size` is the light's larger side.

What is left: a lamp standing in line with a thin wall still lets some soft light round its edge, and
a faint speckle of light (a few dozen pixels at most 5% bright) can show at the outside foot of a
wall near a lamp shut inside; the omni light has neither.

## Broken lamps go dark

**A lamp's light follows its glowing voxels.** `VoxelVolume.glow_whole` and `glow_counts` keep, for
every piece, how many glowing voxels it had as stamped and has now: a voxel taken away (`remove()`,
`remove_many()`), stained with blood (`recolor()`), or laid bare as earth (`lay_bare()`) takes one
off, by its colour's place (`_count_recolor()`), and restamping counts afresh. Every frame `Lamps`
dims each light to its brightness times the share left (`_dim()`), and puts it out with the last
(`_put_out()`, which frees it). A lamp also goes out the moment its piece leaves the rules
(`LevelRules.removed`): broken, blasted, or falling whole, so a lamp coming down is dark all the way
down. A piece falling whole (`TerrainDestruction._drop_whole()`) is drawn with no colour glowing,
and lumps of debris never glow. Nothing relights.

In play: a round passes through a corner piece, so no shot ever hits a lamp (`CLAUDE.md`'s rules);
blood can stain its bulb, dimming it a sixteenth a voxel; a grenade breaks it, every piece of it in
the blast's cells, and what stood over them falls. The street lamp has fewer voxels than
`VoxelTerrain.HOLD_SEARCH` (1,024), so as its foot breaks, what is left of its post and frame is cut
loose and drops in lumps, and its glass, never searched for being loose, falls whole as a block and
shatters where it lands (`Docs/DESTRUCTION.md`); the lamp is dark from the first frame.

## Only for show

Nothing in the rules reads a light, the time of day, a glow or which voxels cast a lamp's shadow:
sight, cover, paths, rolls and throws are the same at night as by day, lit or dark, and the lamps
themselves, on corners, are decoration to the fight (TestMap's rules, every cell and edge, are the
same with its lamps as without them). The time of day draws on its own generator. A light, its
dimming and its fine copies change nothing a seeded fight replays.

A lamp in a part of the level cut away from the view (`Docs/CUTAWAY.md`) still lights, and its
shadows fall as before: only the view is cut.

## What it costs

Measured on TestMap from the game's camera at 1280 x 800, its two lamps lit, GPU time a frame:

| | RTX 3060 (D3D12) | Vega 8 (Vulkan, the Deck's stand-in) |
|---|---|---|
| Day | 3.0 ms | 18.1 ms |
| Dusk or night, omni lights | 3.6 ms (+0.6) | 20.7 to 20.9 ms (+2.7) |
| Dusk or night, area lights | 4.1 to 4.2 ms (+1.2) | 28.1 to 28.5 ms (+10.2) |

A box turning by each lamp, its shadow maps drawn again every frame, measured the same. The research
measured more lamps on BoundaryMap with prototype lights (Vega 8, things moving near them): hard omni
lights cost 1.0, 3.0 and 6.3 ms for 1, 4 and 12 lamps, area lights 6.4, 11.5 and 23.4 ms, an area
light costing about 6 ms once any is in view, before its shadows. The glow, on at dusk and at night,
is about half a millisecond there.

The fine copies, area lights only: TestMap's two lamps cut 21,906 triangles (the level is 268,788)
in 49 ms as the map loads, and a blast beside them takes 24 ms to draw again instead of 18. The
shadowless voxels are a third surface only in the sections that have any.

## Its scripts

- `Scripts/Combat/TimeOfDay.gd`: picks the time of day, lights the map for it, sets `voxel_glow`.
- `Scripts/Combat/Lamps.gd`: the lamps' lights, omni or area; `spec_of()` (Emission, Power and the
  kind's `LampLight`); dimming and putting out; `area_lights`.
- `Scripts/Level/LampLight.gd`: a kind's overrides.
- `Scripts/Level/PieceKind.gd`: `lamp`, `shadowless_colors`.
- `Scripts/Terrain/VoxelShape.gd`: the Emit material read into the flags (`glow_flags()`,
  `glow_of()`, `glows()`, `has_glow()`, `set_glow()`) and `powers`.
- `Scripts/Level/VoxelVolume.gd`: `glow_whole`, `glow_counts`, `glowing_of()`, `glows()`; the
  shadowless rows (`Chunk.shadowless_x` / `_z`, `is_shadowless()`), stamped in `_stamp()`.
- `Scripts/Level/ChunkMesher.gd`: `faces()` gives the third set.
- `Scripts/Level/LevelRenderer.gd`: the `"shadowless"` surface and `shadowless_material`;
  `use_fine_shadows()`, `_build_fine()`, `_fine_pieces()`, `SECTION_LAYER`, `FINE_LAYER`.
- `Scripts/Terrain/Voxels.gdshader` / `.gdshaderinc`: `EMISSION`, `voxel_glow`, `glow_most`,
  `lamp_shadows`, `is_lamp_pass()`.
- `Scripts/Terrain/VoxelModel.gd` (`paint()` leaves glowing colours), `Scripts/Characters/VoxelRig.gd`
  (`load_vox()` reads Emit), `Scripts/Terrain/TerrainDestruction.gd` (`_drop_whole()` falls dark).
- `Scripts/UI/SystemTab.gd`: Lamp Lights; `addons/level_editor/LevelEditorDock.gd`: the palette
  notes a lamp ("corner, lamp").
- `project.godot`: the `voxel_glow` global; the four maps: their `TimeOfDay` and `Lamps` nodes.
- `MagicaVoxel/Lamps/`: the street lamp and its script.

## Probing it

Set `TimeOfDay.forced` (a `TimeOfDay.Period`) and `Lamps.area_lights` before instantiating a map;
both are static and keep their value for the rest of the run. Then, headless:

- `map.get_node("Lamps")`: `count()`, `light_of(piece)` (the light, or null), `spec_of(kind)`.
- `level.volume.glow_counts[piece]` / `glow_whole[piece]`, `glowing_of(piece)`, `is_shadowless(voxel)`.
- `level.renderer.fine_count()`, `fine_triangles`, and `use_fine_shadows()` returns its time.
- Bleed a bulb with `volume.recolor(voxel, VoxelVolume.BLOOD)`, take its voxels with
  `volume.remove()`, break a lamp with `terrain.break_piece()` or `grid.blast()`; then await two
  frames, since `process_frame` is emitted before the frame's `_process` and `Lamps` follows the
  counts there.
- `RenderingServer.global_shader_parameter_get()` reads null outside the editor (Godot refuses it at
  run time), so `voxel_glow` is checked by its frames, in a window (`--write-movie` or
  `get_image()`): a bulb shines at dusk and at night, and shows only its colour by day. So is
  anything else about how a light looks.

The corner posts' shadows, shown and hidden: in a window, at night, frame the lamp, then set
`level.renderer.shadowless_material.set_shader_parameter(&"lamp_shadows", true)` and frame it again:
the difference is the wedges they would throw. Light leaking through walls: replace TestMap's windows
with walls (a `LevelData` made from its pieces), put a lamp inside the house, turn the environment's
SSIL, SSAO and glow off, and compare frames with and without the lamp; nothing outside should
differ (with the house cut away, `cut_away(5)`, the same for a lamp outside). GPU time:
`RenderingServer.viewport_set_measure_render_time()` and `viewport_get_measured_render_time_gpu()`,
`--disable-vsync`; the Vega 8 is `--rendering-driver vulkan --gpu-index 1`.

## Known gaps

- One light a piece, at the middle of its glowing voxels however many colours or clumps they make,
  and it stays where it began: a bulb worn lopsided keeps its light's place, only its brightness
  follows.
- Only a level's pieces cast light: a glowing figure, prop or crate board only glows.
- A lamp put out never relights, and nothing turns lamps on or off in a battle.
- Godot's positional shadow atlas holds 88 shadows by default and Forward+ clusters 512 lights: with
  many lamps in view, the smallest on screen lose their shadows first, and past that lights drop out.
- Area lights cost about ten milliseconds more than omni lights on the Deck's stand-in for TestMap's
  two lamps, and their fine copies cost load time and drawing time near them that grows with the
  lamps.
- An area light lights nothing above its own plane: a wall above a lamp is dark in its light.
- An area light lets some soft light round a thin wall it stands in line with, and can leave a faint
  speckle at the foot of a wall near it (PCSS); the omni light does neither.
- The time of day is not the campaign's: it is rolled afresh for every battle, the world map never
  says it, and nothing saves it.
- Dusk's sun is always 14 degrees up on the map's heading, and night's moon is where the sun was; a
  map has no dusk or night of its own, nor weather.
- Glow blooms whatever shines past white at dusk and at night; nothing else in a map does now, but a
  white wall a lamp lights very close could.
- Lamps neither glow nor light in the level editor: `voxel_glow` is 0 there.
- The street lamp crumbles as its foot breaks rather than toppling whole (fewer voxels than
  `VoxelTerrain.HOLD_SEARCH`).

## Decided without asking

- **Lamps glow and light only at dusk and at night**; by day they are dark.
- **The corner posts keep their shadows from the sun and the moon**: only lamps' lights leave them
  out.
- **Area lights leave the corner posts out too**: what casts no lamp's shadow is a matter of the lamp,
  not of the kind of light.
- **The street lamp is three corner pieces and a brush**, so it is decoration to the fight: rounds
  pass through it and blasts break it.
- **Emission and Power mean**: an Emission of 100% shines eight times the colour; Power p gives a
  light of brightness 2 to the p reaching 3.5 times 2 to the p - 1 cells, and Power 0 none.
- **The light is the voxels' colour**, averaged by voxel, and stands at their middle.
- **`LampLight.glow` 0 puts a lamp out altogether**; `energy` 0 leaves it glowing.
- **The time of day rolls on its own generator**, with `TimeOfDay.forced` for probes.
- **Area lights**: 0.3 x 0.3, half a voxel under the bulb, facing down, 1.23 times as bright as the
  omni light, soft as they are big, and shadowed from fine copies of the level (layers 19 and 20).
- **Dusk's sun stands 14 degrees up on the map's own heading; night's moon is where the sun was.**
- **The glow is on only at dusk and at night.**
- **The street lamp's palette places (185 to 189), its materials and destruction** (as the fence's,
  40 kg).
- **TestMap's lamps stand off the house's front corners**, a cell out from the front wall.
- **The `Styles/` harness renders by day** (`TimeOfDay.forced`), as every style is a day look.
- **The level editor's palette notes a lamp** ("corner, lamp"), as it notes a window.
