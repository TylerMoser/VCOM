@tool
## One voxel model as the game draws and recolours it: a figure, a prop it
## carries or drops, a crate's board, a block falling whole. Each of its voxels
## holds the place of its colour in its [member palette], and it is drawn by
## the voxel shader (Voxels.gdshader), as the level is: its faces merged by
## shape alone ([ChunkMesher]), each pixel the colour of the voxel behind it,
## read from a texture of those places. So recolouring a voxel - blood - is a
## write to that texture, uploaded once at the end of the frame however many
## voxels changed: no mesh is built again, and nothing is drawn over the model.
## Every voxel model is coloured this way, the level included
## ([LevelRenderer]). A crate's boards are drawn as the importer made them only
## until they are first reached ([method VoxelTerrain.take_on_body]), and coins
## and a grenade in flight, which nothing recolours, always.
##
## Its voxels are laid out as its [VoxelShape]'s, and are the shape's own -
## shared with everything drawn whole from it, with the mesh, texture and
## material made of them once ([member VoxelShape.shared]) - until it changes.
## Recoloured, it takes its own copies of its voxels, its texture and its
## material; worn ([method remove]), its own voxels and, once drawn again
## ([method rebuild]), its own mesh. What it is cut into ([method split]) takes
## its voxels, colours and texture with it, so blood goes wherever its voxels
## go, and so do the lumps they break into ([method color_of]).
##
## It is a node under the [MeshInstance3D] that draws it, whose space is the
## model's frame grown by [member VoxelShape.scale], and goes wherever that
## goes: a prop dropped from a dying figure's hand, its mesh moved into a body
## of its own, takes its model, blood and all. A mesh made elsewhere can be
## coloured as well ([method show_on]): a figure's, baked from the same voxels
## and skinned to its skeleton, whose corners carry their voxels
## ([method ChunkMesher.arrays]) so it is coloured however it is posed.
##
## Only for show: nothing in the rules reads it.
class_name VoxelModel
extends Node

const SHADER := preload("res://Scripts/Terrain/Voxels.gdshader")
## What it is called, under what draws it.
const NAME := &"VoxelModel"
## What a palette entry says beyond its colour, in its flags, the fourth
## number of each of the shader's palette entries: the tile grid is drawn over
## it ([TileGrid]); it is wet, and glossier for it, as blood is.
const FLAG_GRID := 1
const FLAG_WET := 2
## Blood's place in every palette.
const BLOOD := VoxelShape.BLOOD

## What it is a model of: how its voxels are laid out, and its own colours.
var shape: VoxelShape
## Its voxels, laid out as [member shape]'s, each the place of its colour in
## [member palette], 0 for none; their rows; and how many there are.
var voxels: PackedByteArray
var rows: PackedInt64Array
var count := 0
## Each place's colour: its shape's, unless it is painted ([method paint]).
var palette: PackedColorArray
## The box round what is left of it, in its frame.
var bounds := AABB()
## What draws it.
var drawn: MeshInstance3D

## Whether its voxels are its own copy rather than its shape's, and whether any
## has gone, so it draws a mesh of its own.
var _owns_voxels := false
var _worn := false
## The colours it is drawn with, and the material that draws them in its
## palette; and whether that material is its own, which it alone changes.
var _texels: Texels
var _material: ShaderMaterial
var _owns_material := false


## The places of a model's voxels as the shader reads them, a byte each at
## [code]x + (z + y * size.z) * size.x[/code], and the texture holding them, a
## single layer. A shape's own are shared by everything drawn whole from it and
## never written; a model's own are shared with what it is cut into, whose
## voxels are never the same ones, so each writes only its own.
class Texels:
	var size: Vector3i
	var bytes: PackedByteArray
	var texture: Texture2DArray
	var writable := false
	var _queued := false

	func _init(dimensions: Vector3i, of_bytes: PackedByteArray, may_write: bool) -> void:
		size = dimensions
		bytes = of_bytes
		writable = may_write
		var images: Array[Image] = [_image()]
		texture = Texture2DArray.new()
		texture.create_from_images(images)

	## Sets the byte at [param at] to [param place], and uploads the texture at
	## the end of the frame, once however many are set before then.
	func write(at: int, place: int) -> void:
		bytes[at] = place
		if not _queued:
			_queued = true
			upload.call_deferred()

	func upload() -> void:
		_queued = false
		texture.update_layer(_image(), 0)

	func _image() -> Image:
		return Image.create_from_data(size.x, size.y * size.z, false, Image.FORMAT_R8, bytes)


## The model of [param kind], its voxels [param left], laid out as the kind's
## array, each holding the place of its colour: left out, the kind whole.
## Given [param colored_as], a model whose voxels these were, it is drawn in
## its colours, from its texture. Shown once [method show_on] puts it under
## what draws it.
func _init(kind: VoxelShape, left := PackedByteArray(), colored_as: VoxelModel = null) -> void:
	name = NAME
	shape = kind
	palette = kind.colors
	if left.is_empty():
		voxels = kind.voxels
		rows = kind.rows
		count = kind.count
		_texels = _kind_texels(kind)
		_material = _kind_material(kind)
	else:
		voxels = left
		rows = kind.rows_of(left)
		count = left.size() - left.count(0)
		_owns_voxels = true
		_worn = true
		if colored_as != null:
			# Its texture too, which either writes only where its own voxels are,
			# and its material, which neither changes from now on.
			palette = colored_as.palette
			_texels = colored_as._texels
			_material = colored_as._material
		else:
			_texels = Texels.new(kind.size, _bytes_of(kind, left), true)
			_material = make_material(kind, _texels.texture, palette)
			_owns_material = true
	bounds = kind.bounds_of(rows)


## The model drawn by [param node], or null if none is.
static func of(node: Node) -> VoxelModel:
	return node.get_node_or_null(NodePath(NAME)) as VoxelModel if node != null else null


## The model drawn by [param target], a [MeshInstance3D] showing a MagicaVoxel
## model, made the first time it is asked for: its voxels read from the .vox,
## and [param target] drawn by the voxel shader from then on. Its mesh is
## either imported straight from a .vox, or a model of a .vox imported as a
## scene, [param source] being the .vox ([method VoxelShape.source_of]). Null
## if it shows no voxel model.
static func take_over(target: MeshInstance3D, source := "") -> VoxelModel:
	var model := of(target)
	if model != null or target.mesh == null:
		return model
	var kind: VoxelShape = null
	if target.has_meta(&"magica_voxel_model_id") and not source.is_empty():
		kind = VoxelShape.read_model(source, int(target.get_meta(&"magica_voxel_model_id")))
	elif target.mesh.resource_path.get_extension().to_lower() == "vox":
		kind = VoxelShape.read_mesh(target.mesh)
	if kind == null or kind.count == 0:
		return null
	model = VoxelModel.new(kind)
	model.show_on(target)
	return model


## Every voxel model under [param node], and [param node] itself if it shows
## one, each taken over ([method take_over]): what a prop is drawn with.
static func take_over_all(node: Node, source := "") -> Array[VoxelModel]:
	var found: Array[VoxelModel] = []
	var meshes: Array[Node] = node.find_children("*", "MeshInstance3D", true, false)
	if node is MeshInstance3D:
		meshes.push_front(node)
	for each in meshes:
		var model := take_over(each as MeshInstance3D, source)
		if model != null:
			found.append(model)
	return found


## Draws it on [param target], made if there is none, and goes under it: by
## its own mesh, or by the mesh [param target] has if [param keep_mesh], one
## made for it elsewhere from the same voxels ([method ChunkMesher.arrays]),
## as a figure's is baked. Returns what draws it.
func show_on(target: MeshInstance3D = null, keep_mesh := false) -> MeshInstance3D:
	if target == null:
		target = MeshInstance3D.new()
		target.name = &"Mesh"
	drawn = target
	if get_parent() != target:
		if get_parent() != null:
			get_parent().remove_child(self)
		target.add_child(self)
	if not keep_mesh:
		target.mesh = _kind_mesh(shape) if not _worn else _mesh_of(shape, rows)
	target.material_override = _material
	return target


## Where its voxels are in the world: what draws it, shrunk back from the
## mesh's space to its shape's frame.
func frame() -> Transform3D:
	return drawn.global_transform * Transform3D(Basis.from_scale(Vector3.ONE * shape.scale), Vector3.ZERO)


## The box round what is left of it, in the world.
func world_box() -> AABB:
	return frame() * bounds


## Whether [param voxel], counted from its shape's voxel (0, 0, 0), is there.
func is_solid(voxel: Vector3i) -> bool:
	return shape.holds(voxel) and voxels[shape.index_of(voxel)] != 0


## The colour of the voxel at [param index] in [member voxels].
func color_of(index: int) -> Color:
	return palette[voxels[index]]


## Gives the voxel at [param index] in [member voxels] the place
## [param place] in its palette: [constant BLOOD], for blood. Drawn so from
## the end of the frame. A voxel that is not there stays not there.
func recolor(index: int, place: int) -> void:
	var held := voxels[index]
	if held == 0 or held == place:
		return
	_take_voxels()
	voxels[index] = place
	if not _texels.writable:
		_texels = Texels.new(shape.size, _texels.bytes.duplicate(), true)
		_set_texture()
	var at := shape.voxel_at(index)
	_texels.write(at.x + (at.z + at.y * shape.size.z) * shape.size.x, place)


## Paints every colour of it but blood's [param color]: a figure in its unit's
## colour.
func paint(color: Color) -> void:
	var painted := PackedColorArray()
	painted.resize(256)
	painted.fill(color)
	painted[0] = Color.TRANSPARENT
	painted[BLOOD] = shape.colors[BLOOD]
	palette = painted
	_material = make_material(shape, _texels.texture, palette)
	_owns_material = true
	if drawn != null:
		drawn.material_override = _material


## Takes the voxel at [param index] in [member voxels] away, and returns what
## it held: the place of its colour, 0 if there was none. Drawn so once
## [method rebuild] is called.
func remove(index: int) -> int:
	var held := voxels[index]
	if held != 0:
		_take_voxels()
		voxels[index] = 0
		var at := shape.voxel_at(index)
		rows[at.y + at.z * shape.size.y] &= ~(1 << at.x)
		count -= 1
		_worn = true
	return held


## Draws what is left of it.
func rebuild() -> void:
	bounds = shape.bounds_of(rows)
	if drawn != null:
		drawn.mesh = _mesh_of(shape, rows) if _worn else _kind_mesh(shape)


## Cuts the voxels at [param indices] in [member voxels] off it, as a model of
## their own, their colours and all, drawn by a mesh of its own not yet in the
## world ([member drawn]), named as its own is. Both are drawn as they are now
## once each is rebuilt ([method rebuild]); the part is already.
func split(indices: PackedInt32Array) -> VoxelModel:
	var left := PackedByteArray()
	left.resize(shape.length)
	for index in indices:
		left[index] = remove(index)
	var part := VoxelModel.new(shape, left, self)
	_owns_material = false
	var mesh := part.show_on()
	if drawn != null:
		mesh.name = drawn.name
	return part


## The arrays of the shader's palette for [param colors], each place's colour
## and, in its fourth number, its [param flags]: left out, blood's place is
## wet and no other has any. Colours go as they are stored, sRGB, as vectors:
## handed over as colours they would be turned linear first, and the shader
## turns them so itself, as the importer's material does its vertex colours.
static func palette_entries(colors: PackedColorArray, flags := PackedByteArray()) -> PackedVector4Array:
	var entries := PackedVector4Array()
	entries.resize(256)
	for place in mini(colors.size(), 256):
		var color := colors[place]
		var flag := 0
		if place < flags.size():
			flag = flags[place]
		elif place == BLOOD:
			flag = FLAG_WET
		entries[place] = Vector4(color.r, color.g, color.b, flag / 255.0)
	return entries


## A material drawing a model of [param kind], whose colours [param texture]
## holds, in [param colors].
static func make_material(kind: VoxelShape, texture: Texture2DArray, colors: PackedColorArray) -> ShaderMaterial:
	var made := ShaderMaterial.new()
	made.shader = SHADER
	made.set_shader_parameter(&"voxels", texture)
	made.set_shader_parameter(&"palette", palette_entries(colors))
	made.set_shader_parameter(&"box_size", kind.size)
	made.set_shader_parameter(&"voxels_per_unit", 1.0 / (VoxelShape.SCALE * kind.scale))
	return made


## The rectangles of every face of a model of [param kind] whose rows are
## [param of_rows], in [param kind]'s voxels, packed as [ChunkMesher] packs
## them, for each set of rows the mesher wants: the model's box stands for a
## cube as wide as its widest.
static func rectangles_of(kind: VoxelShape, of_rows: PackedInt64Array) -> PackedInt32Array:
	var size := kind.size
	var n := maxi(size.x, maxi(size.y, size.z))
	if n > VoxelShape.WIDEST:
		push_error("VoxelModel: a model %s voxels across is more than the %d a side one can be." % [size, VoxelShape.WIDEST])
		return PackedInt32Array()
	# Along x for each z and y, as the model's own rows are; along z for each x
	# and y, turned from them.
	var rows_x := PackedInt64Array()
	var rows_z := PackedInt64Array()
	rows_x.resize(n * n)
	rows_z.resize(n * n)
	for z in size.z:
		for y in size.y:
			var row := of_rows[y + z * size.y]
			if row == 0:
				continue
			rows_x[z + y * n] = row
			while row != 0:
				var low := row & -row
				row ^= low
				rows_z[ChunkMesher.BIT[low % 67] + y * n] |= 1 << z
	return ChunkMesher.rectangles(n, rows_x, rows_z, ChunkMesher.Near.new())


## A mesh of every face of a model of [param kind] whose rows are
## [param of_rows], in the space its imported mesh was drawn in: the shape's
## frame grown by its [member VoxelShape.scale]. Null if no face shows.
static func _mesh_of(kind: VoxelShape, of_rows: PackedInt64Array) -> ArrayMesh:
	var quads := rectangles_of(kind, of_rows)
	if quads.is_empty():
		return null
	var arrays := ChunkMesher.arrays(quads, Vector3i.ZERO, 0, VoxelShape.SCALE * kind.scale, kind.corner * kind.scale)
	@warning_ignore("integer_division")
	arrays[Mesh.ARRAY_INDEX] = ChunkMesher.index_array(quads.size() / ChunkMesher.FIELDS)
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays, [], {}, ChunkMesher.format())
	return mesh


## The places of [param of_voxels], laid out as [param kind]'s array, as the
## shader reads them ([Texels]).
static func _bytes_of(kind: VoxelShape, of_voxels: PackedByteArray) -> PackedByteArray:
	var bytes := PackedByteArray()
	for y in kind.size.y:
		for z in kind.size.z:
			var from := kind.origin + y * kind.stride_y + z * kind.stride_z
			bytes.append_array(of_voxels.slice(from, from + kind.size.x))
	return bytes


## What everything drawn whole from [param kind] shares, made the first time
## it is asked for: its colours, its material in its own palette, its mesh.
static func _kind_texels(kind: VoxelShape) -> Texels:
	if not kind.shared.has(&"texels"):
		kind.shared[&"texels"] = Texels.new(kind.size, _bytes_of(kind, kind.voxels), false)
	return kind.shared[&"texels"]


static func _kind_material(kind: VoxelShape) -> ShaderMaterial:
	if not kind.shared.has(&"material"):
		kind.shared[&"material"] = make_material(kind, _kind_texels(kind).texture, kind.colors)
	return kind.shared[&"material"]


static func _kind_mesh(kind: VoxelShape) -> ArrayMesh:
	if not kind.shared.has(&"mesh"):
		kind.shared[&"mesh"] = _mesh_of(kind, kind.rows)
	return kind.shared[&"mesh"]


## Makes its voxels its own, the first time it changes them: its shape's are
## everything's drawn from it.
func _take_voxels() -> void:
	if _owns_voxels:
		return
	voxels = voxels.duplicate()
	rows = rows.duplicate()
	_owns_voxels = true


## Draws it from the texture it has now, on a material of its own.
func _set_texture() -> void:
	if _owns_material:
		_material.set_shader_parameter(&"voxels", _texels.texture)
	else:
		_material = make_material(shape, _texels.texture, palette)
		_owns_material = true
	if drawn != null:
		drawn.material_override = _material
