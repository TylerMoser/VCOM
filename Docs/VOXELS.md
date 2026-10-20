# Voxel models

Every voxel model the game draws, and how each is coloured, in full: `VoxelShape`, `VoxelModel`,
`Voxels.gdshader` and `ChunkMesher`, and the parts of `LevelRenderer`, `SceneryRenderer`,
`FigureVoxels`, `VoxelRig`, `CharacterModel`, `VoxelBody`, `VoxelTerrain`, `TerrainDestruction` and
`BloodFlow` that make or recolour one. It was written as every model came to be drawn one way
(2026-10-20); `CLAUDE.md` keeps a summary ("Every voxel model is drawn and recoloured one way").
`Docs/LEVELS.md` has the level's own side of it (its volume, its chunks, the mesher's search for
faces, the shader's growth past edges), and `Docs/BLOOD.md` what blood does with it. A section named
here that is not in this file (Gotchas, Verification, Known gaps, another subsystem's notes) is
`CLAUDE.md`'s.

## Why one way

The user asked for it (2026-10-20): "extend the new re-coloring voxels approach to any voxel mesh.
This should include characters/soldiers, props, and loose destructible terrain pieces such as the
crate boards. Anything that comes from a vox file should be re-colored using the new approach,
instead of utilizing overlays. [...] Prioritize correctness and simplification. The goal is to have
one approach for all voxel models, so ensure this approach is as straightforward and extensible as
possible."

Before, there were four. The level was drawn from a texture of its voxels' colours and blood wrote
into it (since 2026-10-19, the user's choice: texture writes rather than more textures or overlay
meshes). A crate's board and a dropped prop were meshes with vertex colours built by `VoxelMesher`,
merged by colour, rebuilt as they wore. A prop in a hand was the importer's own mesh, and a figure a
baked skinned mesh in one flat `body_material`. Blood on all three was an overlay of red squares 2 mm
proud of the faces it stained (`VoxelStains`, `FigureStains`, a skinned one for a figure), handed from
model to model face by face (`stains_of()`, `carry_stains()`, `adopt_stains()`). A block falling whole
was a vertex-coloured mesh again. All of that is gone: one shader, one mesher, one way to recolour a
voxel, and blood is a voxel's colour everywhere.

## How it works

**A model is its voxels and a palette** (`VoxelShape`): each voxel the place of its colour in the
model's palette, 0 for none, in an array padded by an empty voxel all round, with the same voxels as
rows of bits (for each y and z, the voxels along x). Its palette is 256 colours by place, and place
255 is always blood's (`VoxelShape.BLOOD`, `BLOOD_COLOR`): a model whose own colour is there has it
moved to a place none of its voxels use (`reserve_blood()`, as every reading of a `.vox` does; none in
the game has one). A shape is read once from its `.vox` with the importer's own reader and shared,
never changed: a block (`read()`, 16³ in its cell), a mesh imported straight from a `.vox`
(`read_mesh()`, which also measures `scale`, how much bigger the mesh draws a voxel than a block's: a
prop is imported at 0.063 a voxel, a block at 0.0625), or one model of a `.vox` imported as a scene
(`read_model()`, cut down to its voxels; a crate's boards). A figure's is made from its rig
(`VoxelRig.make_shape()`), and a block falling whole's from what it left in the level.

**A model is drawn by a `VoxelModel`**, a node under the `MeshInstance3D` that draws it, which goes
wherever that goes. It holds the model's voxels, its palette (its shape's, or painted one colour,
`paint()`), the texture of its voxels' places (`Texels`: a byte a voxel at
`x + (z + y * size.z) * size.x`, one layer of a `Texture2DArray`) and the material that draws it (a
`ShaderMaterial` of `Voxels.gdshader` with the texture, the palette, the box's size and its voxels a
unit). Its frame (`frame()`) is what draws it shrunk back from the mesh's space to its shape's, which
everything that walks its voxels uses: rounds tearing it (`VoxelTerrain.march()`), blood landing on
it and running over it (`BloodFlow.ModelSurface`).

What it shares and what it owns:

- **Whole and clean, it is its shape's.** Its voxels are the shape's arrays, and its texture,
  material and mesh are made of them once and kept on the shape (`VoxelShape.shared`), for every
  model of that shape: every rifle on the map is one mesh, one texture and one material.
- **Recoloured** (`recolor(index, place)`), it takes its own copy of its voxels, of its texture's
  bytes and of its material, the first time: the shape's are never written. A recolour writes the
  byte and uploads the texture at the end of the frame, once however many changed. No mesh is built
  again, and nothing is drawn over it.
- **Worn** (`remove(index)`, by `VoxelTerrain`), it takes its own voxels, and once drawn again
  (`rebuild()`) its own mesh of what is left. The texture is left alone: a voxel taken away is no
  longer drawn, and the shader reads only the voxels of the face it draws.
- **Cut in two** (`split(indices)`), the part takes its voxels with their places, blood and all, and
  shares its source's texture and material: each writes only its own voxels, never the same ones,
  so they can share one texture for good. Neither's material is its own to change from then on; a
  change makes one.
- **Painted** (`paint(color)`), every place but blood's is that colour, on a material of its own: a
  figure in its unit's colour.

**One shader draws every voxel model** (`Scripts/Terrain/Voxels.gdshader`, moved from
`Scripts/Level/LevelVoxels.gdshader` and renamed as it came to draw more than the level). Each corner
of a face carries, in `CUSTOM0`, its place in voxels within its box and its box's texture layer
times 8 plus which way its face looks (0 +x, 1 -x, 2 +y, 3 -y, 4 +z, 5 -z), and in `CUSTOM1` the
face's extent across its two axes (`ChunkMesher.arrays()`). A pixel's voxel is half a voxel in from
the face, from those alone, kept within the face's extent, and read with `texelFetch` at
`(x, z + y * box_size.z, layer)`; its palette entry is its colour (sRGB, turned linear unless the
output is sRGB) and flags (1 the tile grid's lines, 2 wet: specular 0.35, roughness 0.55, against 0.5
and 1). Colour edges inside a merged face are blended over about a pixel (`neighbour_share()`), and
faces are drawn a fiftieth of a pixel past their edges, as `Docs/LEVELS.md` describes. Since nothing
is read from where a corner is drawn, a mesh skinned to a skeleton is coloured as one standing
still: a figure. It is lit as the importer's materials light a model (`diffuse_burley`,
`specular_schlick_ggx`, roughness 1), so a model looks as its imported mesh did.

Its uniforms: `voxels` (the texture), `palette` (256 `vec4`, passed as a `PackedVector4Array`: a
`PackedColorArray` uniform arrives converted to linear), `box_size` (the voxels along each axis of a
layer's box: 32³ for the level's chunks, 16³ for a scenery kind, a model's own size),
`voxels_per_unit` (16 for blocks, a shade fewer for props), and the growth and tile grid's. The
palette's flags come from `VoxelModel.palette_entries(colors, flags)`: the level passes its own (a
grass place has the grid), a model none, so blood's place alone is wet.

**One mesher meshes every voxel model** (`ChunkMesher`): faces open to the air found from rows of
bits and merged greedily by shape alone, since colour comes from the texture. It meshes any cube of
voxels: a level's chunk, a scenery kind's block, and a model's box set in a cube as wide as its
widest, at most 62 voxels (`VoxelModel.rectangles_of()`, which turns the model's rows along x into the
rows along z the mesher also wants). A model's mesh is built in the space its imported mesh was drawn
in (its shape's frame grown by its `scale`), so a prop scene's `Mesh` keeps the transform it was
placed with.

## Every voxel model

| Model | What draws it | Its colours | Recoloured by | Handed on |
|---|---|---|---|---|
| The level | `LevelRenderer`: sections of 2³ chunks, not `VoxelModel`s | one `Texture2DArray`, a layer a chunk; the level's palette of every kind's colours | `VoxelVolume.recolor()` | a voxel's colour goes wherever the voxel goes |
| The scenery | `SceneryRenderer`: a `MultiMesh` a kind a region | a layer a kind | nothing | - |
| A figure | its baked skinned `Body`, coloured by `FigureVoxels.body` | the rig's places; painted its unit's `tint` | blood (`FigureVoxels.bleed()`) | its lumps take each voxel's colour (`crumble()`) |
| A prop in its socket | its `Mesh`, taken over as it is made (`CharacterModel._make_prop()`) | its `.vox`'s | blood landing on it | dropped with its figure, its model goes with its mesh |
| Dropped gear | the same mesh and model, in a `RigidBody3D` of its own | its `.vox`'s, blood and all | blood, and wear once a round or blast reaches it | `VoxelBody` takes the model it finds (`VoxelModel.of()`) |
| A crate's board | the importer's mesh until it is taken on, then taken over (`VoxelTerrain.take_on_body()`) | its model of the crate's `.vox` | blood; the crate's own (`VoxelTerrain.carry_blood()`) | a part cut off keeps its voxels' colours (`split()`) |
| A block falling whole | `VoxelModel.new()` of what it left, in a `FallingBlock` | the level's palette, blood and all | - | its pieces or lumps where it lands |
| A lump of debris | `VoxelDebris`, a `MultiMesh` instance a voxel | each voxel's colour as it broke off | `VoxelDebris.stain()`, the instance's colour | - |
| A coin, a grenade in flight | the importer's meshes | their `.vox`'s | nothing | - |

Notes on each:

- **The level** is no `VoxelModel` but is drawn the same way, by the same shader, with blood at the
  same place: a model too big to draw whole, so drawn a chunk at a time from one texture array.
  `Docs/LEVELS.md` has it.
- **A figure** is a `VoxelModel` of its rig's shape (the figure as drawn, standing, every bone's
  voxels side by side: `VoxelRig.make_shape()`) shown on its `Body` with the mesh it has
  (`show_on(body, true)`), made as the figure readies (`CharacterModel._ready()`, through
  `FigureVoxels`: about 10 ms the first time, shared by every figure of the model after) and painted
  its unit's colour (`CharacterModel.tint`, set in the scene for enemies and the harness,
  `Unit._paint()` from its character for the squad). The bake (`VoxelRig.make_mesh()`) meshes each
  bone on its own in the figure's box by `ChunkMesher`, so a bent joint still shows the ends of the
  blocks it joins, every corner carrying its voxel and weighted wholly to its bone: the mesh and the
  texture are made from the same `.vox` by the same code, and must be baked again together after
  the `.vox` or the rig changes. The bake runs headless, where a texture it made has no data to be
  saved (the dummy renderer keeps none to read back), so the mesh is saved with a flat
  `StandardMaterial3D` in the model's commonest colour, which only the editor shows; in the game the
  figure's `VoxelModel` draws it (`material_override`).
- **Props** are taken over the moment a figure makes one (`VoxelModel.take_over_all(prop)`): every
  `MeshInstance3D` in the prop scene showing a mesh imported from a `.vox` is drawn by its shape's
  shared mesh and material from then on, until blood lands on it. The grenade a throw flies
  (`ThrownGrenade`) is a fresh copy of the prop scene, left as the importer draws it: nothing
  recolours it in flight.
- **A crate's board** stays the importer's mesh as it was cut until something first reaches it, as
  before: a round, a blast's crater, a drop of blood, or the crate's own blood as it breaks. Taking
  it on reads its model and draws it as one (`VoxelModel.take_over(mesh, source)`), which the eye
  cannot tell from the importer's (see "What it looks like"); most boards never are.
- **A lump of debris** is a few voxels drawn as instances of a cube, each with its own colour,
  rather than a model with a mesh: its colour is the voxel's as it broke off (its model's palette
  entry, blood's included), and blood landing on it writes the instance's colour
  (`VoxelDebris.stain()`), already a voxel's colour written in place rather than anything drawn
  over it.
- **Coins and a grenade in flight** are the importer's meshes: blood never looks for a coin (the
  user's rule), and a grenade in flight is no debris it could meet.

## What it looks like

Rendered on BoundaryMap from the same cameras on the same frame, the tree paused, each model drawn
by the voxel shader and then the old way (a figure's body in a flat `StandardMaterial3D` of its
colour, as `body_material` drew it; each prop and board by the mesh the importer made of its `.vox`):
a figure and its rifle close up differ in 0.01-0.08% of pixels, a heap of a crate's boards in 0.29%,
all of them along silhouettes and colour edges (the faces' growth past their edges, and colour edges
blended inside a face rather than by multisampling between faces). Side by side at 3x they look the
same. Blood is whole voxels everywhere, wet; a wound on a figure shows about as much red as a stain
of faces did (see `Docs/BLOOD.md`).

## Adding a voxel model

1. **Draw it in MagicaVoxel and import it** as a Mesh (one model) or a Scene (several, each its own
   `MeshInstance3D` marked with its `magica_voxel_model_id`), at a block's 0.0625 a voxel or a prop's
   0.063. At most 62 voxels along any axis.
2. **A prop an item shows** (`Item.model`, a scene placing the mesh so its grip is on the origin):
   nothing more. `CharacterModel` takes it over as it makes it.
3. **Anything else shown by a `MeshInstance3D`:** `VoxelModel.take_over(mesh_instance, source)` once
   it is made, `source` the `.vox` a scene's model came from (`VoxelShape.source_of(scene)`), or
   `VoxelModel.take_over_all(node)` for everything under a node. Then `recolor(index, place)` changes
   a voxel, `color_of(index)` reads one, `frame()` says where its voxels are in the world.
4. **A model made from voxels rather than a `.vox`:** a `VoxelShape` of its size, its `colors` its
   palette (place 255 blood's), and its voxels in an array laid out as the shape's:
   `VoxelModel.new(shape, voxels).show_on()` gives the `MeshInstance3D` that draws it, as a block
   falling whole is made.
5. **A mesh made elsewhere** (skinned, or merged with others): build it with `ChunkMesher.arrays()`
   so each corner carries its voxel in the model's box (any offset and scale for where it is drawn),
   then `VoxelModel.new(shape).show_on(mesh_instance, true)` colours it without replacing it, as a
   figure is.
6. **For blood to land on it**, `Blood`'s drops have to find it: as debris, a `RigidBody3D` on the
   debris layer taken on with `VoxelTerrain.take_on_body()` or `take_on_later()`; as a figure's gear,
   shown in a socket; anything else wants a branch in `Blood._first_met()`, splashing with
   `BloodFlow.ModelSurface.new(model)`.
7. **For it to wear away**, take it on as a loose model (`take_on_body()`), and it wears as a
   crate's boards do (`Docs/DESTRUCTION.md`, "Loose models").

## What it costs

- **Textures:** one per shape, its box's bytes (a rifle 18 x 5 x 1, 90 bytes; a crate's board at most
  100, 1 x 10 x 10; the figure 25 x 27 x 6, 4 KB), and one for each model blood has reached. A model is a
  draw call, as it was; every figure has a material of its own for its colour, and so does every
  model blood has reached.
- **A recolour** writes a byte; the upload at the end of the frame is the model's whole texture, a
  few kilobytes at most.
- **Meshing:** `ChunkMesher.arrays()` writes each corner's voxel, where it wrote the chunk's origin
  once for the whole chunk: 0.35 ms a chunk against 0.27, about 40 ms more on BoundaryMap's 520 ms
  build, and a round's bite redraws in about 2.7 ms against 2.2. A model's own mesh, built as it
  wears, is a few hundred faces at most.
- **Blood:** a hit costs 0.2 ms as before; a wound's flow on a figure (24 faces) about 1 ms, in
  blood's budget a physics step; a death with blood about 4.2 ms on its frame (3.8 before).

## Probing it

Headless, as everything else (`CLAUDE.md`'s Verification). On a map, a unit's figure is
`unit.model.voxels()`, its body's model `.body` (`body.voxels.count(VoxelModel.BLOOD)` is how many of
its voxels are red; `body._texels.writable` whether its texture is its own;
`VoxelModel._kind_texels(figure.rig.shape)` the shared one, which should never hold blood); its
props' models `unit.model.gear()`; the model under any mesh `VoxelModel.of(mesh_instance)`; a loose
model's `voxels._loose[body].model`. Check what draws a model with `drawn.material_override` (the
shader is `VoxelModel.SHADER`) and `drawn.mesh` (a taken-over prop's is no `.vox` resource). The
probe made for this step checked 72 things on BoundaryMap: every figure and prop drawn by the
shader and painted its colour, a hit recolouring only its figure's own texture, the lumps carrying
the same red voxels, blood on a rifle in hand leaving every other rifle on the shared material, a
death dropping the rifle with its blood, taken on as the same model, a crate's blood carried to its
boards, a board torn and drawn from a mesh of its own, and a bloodied crate falling whole as a
voxel model and handing its blood to its boards where it landed.

To compare a model's look with the old way, render it twice on one paused frame: as it is, and with
its `material_override` set to a flat `StandardMaterial3D` (a figure) or its `mesh` set back to its
`.vox` and `material_override` to null (a prop or board), and diff the two.

## Known gaps

- Coins and a grenade in flight are drawn by the importer, not taken over: blood never reaches them,
  so nothing needed it. Taking one over is one call (`take_over_all()`).
- Every model blood reaches has a texture and material of its own, a draw call each, as before: fine
  for the dozens a battle makes. Hundreds would want one atlas of every model's colours, with each
  model's place in it as an instance uniform (the textures themselves cannot be).
- A model is at most 62 voxels along any axis (the mesher's rows are 64-bit, as `VoxelShape.WIDEST`
  already held a model's x to).
- On a figure the faces grow past their edges along their axes as they rest, so on a turned bone
  part of that is out of the face's plane: a fiftieth of a pixel either way.
- The figure's baked mesh shows a flat material of its model's commonest colour in the editor, not
  its colours, since the bake runs headless; the base figure is one grey, so it shows as it is.
- A figure is painted all one colour, its unit's: a model drawn in colours of its own with only some
  of them its unit's (a uniform's trim) would want a palette with some places painted and some not.
- A lump keeps the colour its voxel had as it broke off, and is no `VoxelModel`: a voxel recoloured
  after it broke off is coloured on its own instance only.
- The baked figure's texture places and its mesh must come from the same bake of the same `.vox`; a
  `.vox` edited and not baked again draws its colours in the wrong voxels.

## Decided without asking

- One texture for each model blood reaches, copied from its shape's on the first stain, rather than
  an atlas shared by every model: the user wanted texture writes rather than overlays or more
  textures, and each model has one texture only, the one it is drawn from, with no blood layer over
  it; the shared textures keep it to the shapes and the models actually bloodied.
- A part cut from a model shares its source's texture for good, each writing only its own voxels.
- Props taken over as a figure makes them, so every prop in play looks one way; a crate's boards only
  as they are taken on, as before, since most never are and they look the same either way.
- A figure painted through its palette (every place its unit's colour), so its texture stays the
  `.vox`'s places and a model drawn in its own colours needs no change; `CharacterModel.body_material`
  became `tint`, a colour, and the scenes' materials for it went.
- The bake's saved material flat, in the model's commonest colour, as the editor's view only.
- Lumps left as `MultiMesh` instances coloured each on its own: already a voxel's colour written in
  place, and a model with a mesh a lump would cost far more.
- Coins and a grenade in flight left to the importer.
- The shader moved to `Scripts/Terrain/` and renamed `Voxels.gdshader`, beside `VoxelShape` and
  `VoxelModel`, as it draws every voxel model; its `chunk_size` uniform became `box_size`, three
  numbers, since a model's box is no cube.
- Blood spends one unit for each face it turns red, so a wound shows as much red as it did when blood
  stained faces (`Docs/BLOOD.md`).
