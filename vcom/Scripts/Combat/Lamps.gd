## The light a battle's lamps cast. A node in each combat map, after its
## [TimeOfDay]: at dusk and at night it gives every piece of the level whose
## glowing voxels cast light one light of its own, standing where those voxels
## are, in their colour, as bright and reaching as far as MagicaVoxel's Power
## for them says, or as the kind's [member PieceKind.lamp] overrides it
## (Docs/LIGHTS.md). By day there are none.
##
## A light is an omni light casting hard shadows or, with [member area_lights]
## on, an area light casting soft ones: a small rectangle just under the
## glowing voxels, facing down. An area light's shadow map is a paraboloid,
## which puts the level's big faces in the wrong place near the light, so the
## area lights take their shadows from copies of the level cut fine round them
## ([method LevelRenderer.use_fine_shadows]). Either way the lamp's own frame
## beside its bulb casts no shadow from it ([member
## PieceKind.shadowless_colors]), and its post does.
##
## A broken lamp goes dark: its light dims with the glowing voxels it has left,
## shot away or put out by blood ([member VoxelVolume.glow_counts]), and goes
## out with the last of them, or the moment its piece leaves the rules,
## broken or falling ([signal LevelRules.removed]); a lamp falling whole is
## drawn dark ([TerrainDestruction]).
##
## Only for show: nothing in the rules reads a light.
class_name Lamps
extends Node3D

## Whether lamps are area lights, casting soft shadows, rather than omni
## lights casting hard ones, the default. Set from the pause menu's System tab
## ([SystemTab]), which only lets it change between battles, on the world map;
## each combat map reads it once, as it loads, so a battle keeps what it began
## with. Kept here, as [member Blood.enabled] is, until the game closes;
## nothing saves it.
static var area_lights := false

## How much brighter an area light is made than the omni light of the same
## lamp. An area light faces down, so it sends more right under the lamp and
## less round it: at this the two light the ground alike about two metres out
## (measured on a flat floor under the street lamp: 1.13 times the omni's half
## a metre out, 0.68 times at four metres).
const AREA_ENERGY := 1.23
## The light of a glowing colour's Power: its brightness 2 to the Power, and
## its reach, in cells, this much at a Power of 1 and twice as far for each
## step more (MagicaVoxel lights its own renders by 10 to the Power, too
## steep for a game).
const REACH_AT_ONE := 3.5
## How far an area light stands under the lowest glowing voxel, in voxels:
## just clear of them.
const AREA_BELOW := 0.5

@export var level_path: NodePath = ^"../Level"
@export var time_of_day_path: NodePath = ^"../TimeOfDay"


## One lamp: its piece, its light, how bright that is whole, and how many of
## the piece's glowing voxels there were and are now.
class Lamp:
	var piece := -1
	var light: Light3D
	var energy := 0.0
	var whole := 0
	var left := 0


## What a kind's glowing voxels cast: brightness, reach in cells, colour,
## offset in cells before the piece is turned, and an area light's size.
class Spec:
	var energy := 0.0
	var reach := 0.0
	var color := Color.WHITE
	var offset := Vector3.ZERO
	var area_size := Vector2(0.3, 0.3)


var _level: VoxelLevel
## The lamps lit, by their piece's index in the level.
var _lamps := {}
## What each kind of the level's casts, by its place in the level's kinds:
## a [Spec], or null for none, worked out once.
var _specs := {}


func _ready() -> void:
	_level = get_node_or_null(level_path) as VoxelLevel
	var time_of_day := get_node_or_null(time_of_day_path) as TimeOfDay
	if _level == null or _level.volume == null or _level.rules == null:
		push_error("Lamps: no level, so no lamps are lit.")
		set_process(false)
		return
	if time_of_day == null:
		push_error("Lamps: no TimeOfDay, so no lamps are lit.")
		set_process(false)
		return
	if not time_of_day.lamps_lit():
		set_process(false)
		return
	var area := area_lights
	for piece in _level.data.count():
		_light(piece, area)
	if area and not _lamps.is_empty():
		var lights: Array = []
		for lamp: Lamp in _lamps.values():
			lights.append(lamp.light)
		var sun := time_of_day.get_node_or_null(time_of_day.sun_path) as Light3D
		_level.renderer.use_fine_shadows(lights, [sun] if sun != null else [])
	_level.rules.removed.connect(_on_removed)
	set_process(not _lamps.is_empty())


## How many lamps are lit.
func count() -> int:
	return _lamps.size()


## The light of piece [param piece]'s lamp, or null if it has none lit.
func light_of(piece: int) -> Light3D:
	var lamp: Lamp = _lamps.get(piece)
	return lamp.light if lamp != null else null


## What pieces of the level's kind [param kind] cast, from MagicaVoxel's Power
## and Emission for their glowing colours and the kind's [member
## PieceKind.lamp]: null if they cast no light.
func spec_of(kind: int) -> Spec:
	if _specs.has(kind):
		return _specs[kind]
	var spec := _make_spec(kind)
	_specs[kind] = spec
	return spec


func _make_spec(kind: int) -> Spec:
	var volume := _level.volume
	if kind < 0 or kind >= volume.shapes.size() or volume.shapes[kind] == null:
		return null
	var shape := volume.shapes[kind]
	var piece_kind := volume.kinds[kind]
	# The glowing colours its voxels hold, and how many of each.
	var held := {}
	for place in shape.voxels:
		if place != 0 and VoxelShape.glows(shape.flags[place]):
			held[place] = int(held.get(place, 0)) + 1
	if held.is_empty():
		return null
	var power := 0.0
	var color_sum := Vector3.ZERO
	var total := 0
	for place: int in held:
		power = maxf(power, shape.powers[place])
		var color := shape.colors[place]
		color_sum += Vector3(color.r, color.g, color.b) * held[place]
		total += held[place]
	var spec := Spec.new()
	if power > 0.0:
		spec.energy = pow(2.0, power)
		spec.reach = REACH_AT_ONE * pow(2.0, power - 1.0)
	var average := color_sum / total
	spec.color = Color(average.x, average.y, average.z)
	var lamp := piece_kind.lamp if piece_kind != null else null
	if lamp != null:
		if lamp.energy >= 0.0:
			spec.energy = lamp.energy
			if spec.reach <= 0.0:
				spec.reach = REACH_AT_ONE * 2.0
		if lamp.reach > 0.0:
			spec.reach = lamp.reach
		if lamp.color.a > 0.0:
			spec.color = Color(lamp.color.r, lamp.color.g, lamp.color.b)
		spec.offset = lamp.offset
		spec.area_size = lamp.area_size
	if spec.energy <= 0.0 or spec.reach <= 0.0:
		return null
	return spec


## Lights piece [param piece] if its kind casts light and it has glowing voxels
## left: an area light if [param area], else an omni light.
func _light(piece: int, area: bool) -> void:
	var spec := spec_of(_level.data.kind_at(piece))
	if spec == null:
		return
	var volume := _level.volume
	var glowing := volume.glowing_of(piece)
	if glowing.is_empty():
		return
	# Where its glowing voxels are, in the level's own space, in cells.
	var middle := Vector3.ZERO
	var lowest := INF
	for voxel in glowing:
		middle += VoxelVolume.center_of(Vector3i(voxel))
		lowest = minf(lowest, voxel.y)
	middle /= glowing.size()
	var turn := Basis(Vector3.UP, _level.data.turn_at(piece) * PI * 0.5)
	middle += turn * spec.offset
	var lamp := Lamp.new()
	lamp.piece = piece
	lamp.energy = spec.energy
	lamp.whole = maxi(volume.glow_whole[piece], glowing.size())
	lamp.left = volume.glow_counts[piece]
	if area:
		var light := AreaLight3D.new()
		light.area_range = spec.reach
		light.area_size = spec.area_size
		# Its shadows as soft as it is big (Godot's 0.5 is softer than a lantern
		# and lets light round a thin wall it stands in line with).
		light.light_size = maxf(spec.area_size.x, spec.area_size.y)
		lamp.energy = spec.energy * AREA_ENERGY
		lamp.light = light
		add_child(light)
		var under := Vector3(middle.x, (lowest - AREA_BELOW) / VoxelVolume.BLOCK, middle.z) + turn * Vector3(0.0, spec.offset.y, 0.0)
		light.global_position = _level.to_global(under)
		# An area light shines along its -Z: down.
		light.global_basis = _level.global_basis * Basis.looking_at(Vector3.DOWN, Vector3.FORWARD)
	else:
		var light := OmniLight3D.new()
		light.omni_range = spec.reach
		light.omni_attenuation = 1.0
		lamp.light = light
		add_child(light)
		light.global_position = _level.to_global(middle)
	lamp.light.name = "Lamp%d" % piece
	lamp.light.light_color = spec.color
	lamp.light.shadow_enabled = true
	_dim(lamp)
	_lamps[piece] = lamp


## Follows each lamp's glowing voxels: dimmer as they go, out with the last.
func _process(_delta: float) -> void:
	var counts := _level.volume.glow_counts
	for piece: int in _lamps.keys():
		var lamp: Lamp = _lamps[piece]
		var left := counts[piece]
		if left == lamp.left:
			continue
		lamp.left = left
		if left <= 0:
			_put_out(piece)
		else:
			_dim(lamp)


## Makes [param lamp]'s light as bright as the glowing voxels it has left.
func _dim(lamp: Lamp) -> void:
	lamp.light.light_energy = lamp.energy * clampf(float(lamp.left) / lamp.whole, 0.0, 1.0)


func _on_removed(index: int, _slot: Vector3i) -> void:
	if _lamps.has(index):
		_put_out(index)


## Puts out the lamp of piece [param piece] for good.
func _put_out(piece: int) -> void:
	var lamp: Lamp = _lamps[piece]
	_lamps.erase(piece)
	if is_instance_valid(lamp.light):
		lamp.light.queue_free()
	set_process(not _lamps.is_empty())
