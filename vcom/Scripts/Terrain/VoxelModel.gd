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
## Its glass voxels, if it has any ([member glass_rows]), are meshed as a
## second surface of its mesh, named [constant GLASS_SURFACE], and drawn by the
## glass shaders ([constant GLASS_SHADER], [constant SHINE_SHADER]) from the same
## texture and palette: what it draws is then given a material for each
## surface, where a model with no glass is drawn by [member
## MeshInstance3D.material_override] as it always was.
##
## Only for show: nothing in the rules reads it.
class_name VoxelModel
extends Node

const SHADER := preload("res://Scripts/Terrain/Voxels.gdshader")
## Glass, in two passes: the tint over what shows through it, then its shine
## and whatever of its own colour it does not let through, added on top. The
## second pass draws after every first pass ([constant SHINE_PRIORITY]).
const GLASS_SHADER := preload("res://Scripts/Terrain/VoxelGlass.gdshader")
const SHINE_SHADER := preload("res://Scripts/Terrain/VoxelGlassShine.gdshader")
const SHINE_PRIORITY := 1
## The name of a mesh's glass surface: every mesh of glass voxels has it last.
const GLASS_SURFACE := "glass"
## What it is called, under what draws it.
const NAME := &"VoxelModel"
## What a palette entry says beyond its colour, in its flags, the fourth
## number of each of the shader's palette entries ([constant
## VoxelShape.FLAG_GRID]): the tile grid is drawn over it ([TileGrid]); it is
## wet, and glossier for it, as blood is; it is glass.
const FLAG_GRID := VoxelShape.FLAG_GRID
const FLAG_WET := VoxelShape.FLAG_WET
const FLAG_GLASS := VoxelShape.FLAG_GLASS
## Blood's place in every palette.
const BLOOD := VoxelShape.BLOOD

## What it is a model of: how its voxels are laid out, and its own colours.
var shape: VoxelShape
## Its voxels, laid out as [member shape]'s, each the place of its colour in
## [member palette], 0 for none; their rows; and how many there are.
var voxels: PackedByteArray
var rows: PackedInt64Array
var count := 0
## Which of its voxels are glass, as rows laid out as [member rows] are, and
## how many: empty, and 0, for a model with none. A voxel stays glass whatever
## it is recoloured.
var glass_rows := PackedInt64Array()
var glass_count := 0
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
## The material its glass is drawn with, as [member _material] its other
## voxels, the shine its next pass; null for a model with no glass.
var _glass_material: ShaderMaterial


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
## its colours, from its texture. Which of [param left] are glass is
## [param left_glass], rows laid out as [member rows]: left out, those holding
## a glass colour of the kind's ([member VoxelShape.flags]). Shown once
## [method show_on] puts it under what draws it.
func _init(kind: VoxelShape, left := PackedByteArray(), colored_as: VoxelModel = null, left_glass := PackedInt64Array()) -> void:
	name = NAME
	shape = kind
	palette = kind.colors
	if left.is_empty():
		voxels = kind.voxels
		rows = kind.rows
		count = kind.count
		glass_rows = kind.glass_rows
		glass_count = kind.glass_count
		_texels = _kind_texels(kind)
		_material = _kind_material(kind)
		if kind.has_glass():
			_glass_material = _kind_glass_material(kind)
	else:
		voxels = left
		rows = kind.rows_of(left)
		count = left.size() - left.count(0)
		_owns_voxels = true
		_worn = true
		if not left_glass.is_empty():
			glass_rows = left_glass
		elif kind.has_glass():
			glass_rows = kind.rows_of(_glass_of(kind, left))
		glass_count = _count_bits(glass_rows)
		if glass_count == 0:
			glass_rows = PackedInt64Array()
		if colored_as != null:
			# Its texture too, which either writes only where its own voxels are,
			# and its material, which neither changes from now on.
			palette = colored_as.palette
			_texels = colored_as._texels
			_material = colored_as._material
			_glass_material = colored_as._glass_material
			if glass_count > 0 and _glass_material == null:
				_glass_material = make_glass_material(kind, _texels.texture, palette)
		else:
			_texels = Texels.new(kind.size, _bytes_of(kind, left), true)
			_material = make_material(kind, _texels.texture, palette)
			if glass_count > 0:
				_glass_material = make_glass_material(kind, _texels.texture, palette)
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
		target.mesh = _kind_mesh(shape) if not _worn else _mesh_of(shape, rows, glass_rows)
	_apply_materials()
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


## Whether the voxel at [param index] in [member voxels] is glass.
func is_glass(index: int) -> bool:
	if glass_count == 0 or voxels[index] == 0:
		return false
	var at := shape.voxel_at(index)
	return (glass_rows[at.y + at.z * shape.size.y] >> at.x) & 1 == 1


## Every glass voxel it has, as its place in [member voxels].
func glass_indices() -> PackedInt32Array:
	var found := PackedInt32Array()
	if glass_count == 0:
		return found
	for z in shape.size.z:
		for y in shape.size.y:
			var row := glass_rows[y + z * shape.size.y]
			var start := shape.origin + y * shape.stride_y + z * shape.stride_z
			while row != 0:
				var low := row & -row
				row ^= low
				found.append(start + ChunkMesher.BIT[low % 67])
	return found


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


## Paints every colour of it but blood's, its glass's and its glowing ones'
## [param color]: a figure in its unit's colour, its visor clear, a lamp it
## carries still its own.
func paint(color: Color) -> void:
	var painted := PackedColorArray()
	painted.resize(256)
	painted.fill(color)
	painted[0] = Color.TRANSPARENT
	painted[BLOOD] = shape.colors[BLOOD]
	for place in range(1, BLOOD):
		if shape.flags[place] & FLAG_GLASS != 0 or VoxelShape.glows(shape.flags[place]):
			painted[place] = shape.colors[place]
	palette = painted
	_material = make_material(shape, _texels.texture, palette)
	if _glass_material != null:
		_glass_material = make_glass_material(shape, _texels.texture, palette)
	_owns_material = true
	_apply_materials()


## Takes the voxel at [param index] in [member voxels] away, and returns what
## it held: the place of its colour, 0 if there was none. Drawn so once
## [method rebuild] is called.
func remove(index: int) -> int:
	var held := voxels[index]
	if held != 0:
		var was_glass := is_glass(index)
		_take_voxels()
		voxels[index] = 0
		var at := shape.voxel_at(index)
		rows[at.y + at.z * shape.size.y] &= ~(1 << at.x)
		if was_glass:
			glass_rows[at.y + at.z * shape.size.y] &= ~(1 << at.x)
			glass_count -= 1
		count -= 1
		_worn = true
	return held


## Draws what is left of it.
func rebuild() -> void:
	bounds = shape.bounds_of(rows)
	if drawn != null:
		drawn.mesh = _mesh_of(shape, rows, glass_rows) if _worn else _kind_mesh(shape)
		_apply_materials()


## Cuts the voxels at [param indices] in [member voxels] off it, as a model of
## their own, their colours and all, drawn by a mesh of its own not yet in the
## world ([member drawn]), named as its own is. Both are drawn as they are now
## once each is rebuilt ([method rebuild]); the part is already.
func split(indices: PackedInt32Array) -> VoxelModel:
	var left := PackedByteArray()
	left.resize(shape.length)
	var left_glass := PackedInt64Array()
	if glass_count > 0:
		left_glass.resize(glass_rows.size())
	for index in indices:
		if glass_count > 0 and is_glass(index):
			var at := shape.voxel_at(index)
			left_glass[at.y + at.z * shape.size.y] |= 1 << at.x
		left[index] = remove(index)
	var part := VoxelModel.new(shape, left, self, left_glass)
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
## holds, in [param colors] (with the kind's flags).
static func make_material(kind: VoxelShape, texture: Texture2DArray, colors: PackedColorArray) -> ShaderMaterial:
	var made := ShaderMaterial.new()
	made.shader = SHADER
	_set_voxels(made, kind, texture, colors)
	return made


## The material drawing the glass of a model of [param kind], as
## [method make_material] makes the one for the rest: the tint, with the shine
## as its next pass ([constant GLASS_SHADER], [constant SHINE_SHADER]).
static func make_glass_material(kind: VoxelShape, texture: Texture2DArray, colors: PackedColorArray) -> ShaderMaterial:
	var made := glass_material()
	_set_voxels(made, kind, texture, colors)
	return made


## A glass material, its shine as its next pass, with no voxels given yet: the
## level's ([LevelRenderer]) and the scenery's are given theirs as their
## opaque material's are, through [method set_parameter].
static func glass_material() -> ShaderMaterial:
	var made := ShaderMaterial.new()
	made.shader = GLASS_SHADER
	var shine := ShaderMaterial.new()
	shine.shader = SHINE_SHADER
	shine.render_priority = SHINE_PRIORITY
	made.next_pass = shine
	return made


## Sets [param parameter] to [param value] on [param material] and every pass
## after it: a glass material's shine reads what its tint does.
static func set_parameter(material: Material, parameter: StringName, value: Variant) -> void:
	var at := material
	while at != null:
		(at as ShaderMaterial).set_shader_parameter(parameter, value)
		at = at.next_pass


## Gives [param material], and every pass after it, a model of [param kind]'s
## voxels: [param texture] its colours' places, in [param colors].
static func _set_voxels(material: ShaderMaterial, kind: VoxelShape, texture: Texture2DArray, colors: PackedColorArray) -> void:
	set_parameter(material, &"voxels", texture)
	set_parameter(material, &"palette", palette_entries(colors, kind.flags))
	set_parameter(material, &"box_size", kind.size)
	set_parameter(material, &"voxels_per_unit", 1.0 / (VoxelShape.SCALE * kind.scale))


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


## The rectangles of every face of a model of [param kind] whose rows are
## [param of_rows] and whose glass is [param of_glass] (laid out as rows;
## empty for none), as [method rectangles_of] packs them, its glass apart
## ([method ChunkMesher.faces]): [code][the rest's, the glass's][/code].
static func faces_of(kind: VoxelShape, of_rows: PackedInt64Array, of_glass: PackedInt64Array) -> Array[PackedInt32Array]:
	if of_glass.is_empty() or _count_bits(of_glass) == 0:
		var found: Array[PackedInt32Array] = [rectangles_of(kind, of_rows), PackedInt32Array()]
		return found
	var solid := of_rows.duplicate()
	for at in solid.size():
		solid[at] &= ~of_glass[at]
	var near := ChunkMesher.Near.new()
	var cube := _cube_rows(kind, of_rows)
	var glass_cube := _cube_rows(kind, of_glass)
	var n := maxi(kind.size.x, maxi(kind.size.y, kind.size.z))
	var found: Array[PackedInt32Array] = [
		rectangles_of(kind, solid),
		ChunkMesher.glass_rectangles(n, glass_cube[0], glass_cube[1], cube[0], cube[1], near),
	]
	return found


## [param of_rows], a model of [param kind]'s rows, as the rows of a cube as
## wide as its widest, along x and along z, as [ChunkMesher] wants them.
static func _cube_rows(kind: VoxelShape, of_rows: PackedInt64Array) -> Array[PackedInt64Array]:
	var size := kind.size
	var n := maxi(size.x, maxi(size.y, size.z))
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
	var made: Array[PackedInt64Array] = [rows_x, rows_z]
	return made


## A mesh of every face of a model of [param kind] whose rows are
## [param of_rows] and whose glass is [param of_glass] (empty for none), in the
## space its imported mesh was drawn in: the shape's frame grown by its
## [member VoxelShape.scale]. Its glass, if it shows, is a surface of its own,
## the last, named [constant GLASS_SURFACE]. Null if no face shows.
static func _mesh_of(kind: VoxelShape, of_rows: PackedInt64Array, of_glass := PackedInt64Array()) -> ArrayMesh:
	var found := faces_of(kind, of_rows, of_glass)
	var mesh: ArrayMesh = null
	for at in 2:
		var quads := found[at]
		if quads.is_empty():
			continue
		var arrays := ChunkMesher.arrays(quads, Vector3i.ZERO, 0, VoxelShape.SCALE * kind.scale, kind.corner * kind.scale)
		@warning_ignore("integer_division")
		arrays[Mesh.ARRAY_INDEX] = ChunkMesher.index_array(quads.size() / ChunkMesher.FIELDS)
		if mesh == null:
			mesh = ArrayMesh.new()
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays, [], {}, ChunkMesher.format())
		if at == 1:
			mesh.surface_set_name(mesh.get_surface_count() - 1, GLASS_SURFACE)
	return mesh


## The surface of [param mesh] its glass is drawn by, or -1 if it has none.
static func glass_surface_of(mesh: Mesh) -> int:
	if mesh == null:
		return -1
	for at in mesh.get_surface_count():
		if mesh.surface_get_name(at) == GLASS_SURFACE:
			return at
	return -1


## Which of [param of_voxels], laid out as [param kind]'s array, hold a glass
## colour of the kind's, as a byte each, laid out the same.
static func _glass_of(kind: VoxelShape, of_voxels: PackedByteArray) -> PackedByteArray:
	var found := PackedByteArray()
	found.resize(of_voxels.size())
	for index in of_voxels.size():
		var held := of_voxels[index]
		if held != 0 and kind.flags[held] & FLAG_GLASS != 0:
			found[index] = 1
	return found


## How many bits [param of_rows] have set, in all.
static func _count_bits(of_rows: PackedInt64Array) -> int:
	var total := 0
	for row in of_rows:
		while row != 0:
			row &= row - 1
			total += 1
	return total


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


static func _kind_glass_material(kind: VoxelShape) -> ShaderMaterial:
	if not kind.shared.has(&"glass_material"):
		kind.shared[&"glass_material"] = make_glass_material(kind, _kind_texels(kind).texture, kind.colors)
	return kind.shared[&"glass_material"]


static func _kind_mesh(kind: VoxelShape) -> ArrayMesh:
	if not kind.shared.has(&"mesh"):
		kind.shared[&"mesh"] = _mesh_of(kind, kind.rows, kind.glass_rows)
	return kind.shared[&"mesh"]


## Makes its voxels its own, the first time it changes them: its shape's are
## everything's drawn from it.
func _take_voxels() -> void:
	if _owns_voxels:
		return
	voxels = voxels.duplicate()
	rows = rows.duplicate()
	glass_rows = glass_rows.duplicate()
	_owns_voxels = true


## Draws it from the texture it has now, on a material of its own.
func _set_texture() -> void:
	if _owns_material:
		_material.set_shader_parameter(&"voxels", _texels.texture)
		if _glass_material != null:
			set_parameter(_glass_material, &"voxels", _texels.texture)
	else:
		_material = make_material(shape, _texels.texture, palette)
		if _glass_material != null:
			_glass_material = make_glass_material(shape, _texels.texture, palette)
		_owns_material = true
	_apply_materials()


## Gives what draws it its materials: [member _material] over the whole of it,
## as [member MeshInstance3D.material_override], for a mesh with no glass; for
## one with, a material for each surface, the glass's
## ([constant GLASS_SURFACE]) [member _glass_material].
func _apply_materials() -> void:
	if drawn == null:
		return
	var glass_at := glass_surface_of(drawn.mesh)
	if glass_at < 0 or _glass_material == null:
		drawn.material_override = _material
		return
	drawn.material_override = null
	for at in drawn.mesh.get_surface_count():
		drawn.set_surface_override_material(at, _glass_material if at == glass_at else _material)
