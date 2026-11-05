## The time of day a battle is fought at: by day, at dusk or at night, picked
## at random as the battle begins, half the battles by day and a quarter each
## at dusk and at night (the user's, 2026-10-27, for now). A node in each
## combat map, after its WorldEnvironment and sun.
##
## By day the map is as it was made. At dusk the sun sits low and orange in a
## sky going dark; at night the sun is the moon, faint and blue, under a dark
## sky, with enough light everywhere to fight by. Then, and only then, glowing
## voxels glow (the global shader uniform [constant GLOBAL]) and lamps cast
## their light ([Lamps]); the glow, a bloom round what is brighter than white,
## is on with them.
##
## Only for show: nothing in the rules reads it, and it draws on a generator of
## its own, never the global one, so a seeded fight replays the same whatever
## time of day it is fought at.
class_name TimeOfDay
extends Node

enum Period { DAY, DUSK, NIGHT }

## How likely each time of day is, in [enum Period]'s order.
const ODDS: Array[float] = [0.5, 0.25, 0.25]
## The global shader uniform glowing voxels glow by (project.godot's
## shader_globals): 1 at dusk and at night, 0 by day.
const GLOBAL := &"voxel_glow"
## The sun's height at dusk, in degrees over the ground; it keeps the map's
## heading.
const DUSK_ELEVATION := 14.0

## The time of day every battle is fought at, for probes and harnesses: a
## [enum Period], or -1 to pick at random, as battles in play always do.
static var forced := -1

@export var environment_path: NodePath = ^"../WorldEnvironment"
@export var sun_path: NodePath = ^"../DirectionalLight3D"

## The battle's time of day.
var time := Period.DAY

var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.randomize()
	time = (forced as Period) if forced >= 0 else pick(_rng.randf())
	apply()


## The time of day a roll of [param roll], from 0 up to 1, falls on, by
## [constant ODDS].
static func pick(roll: float) -> Period:
	var total := 0.0
	for at in ODDS.size():
		total += ODDS[at]
		if roll < total:
			return at as Period
	return Period.NIGHT


## Whether lamps are lit and glowing voxels glow: at dusk and at night.
func lamps_lit() -> bool:
	return time != Period.DAY


## What to call [param of].
static func name_of(of: Period) -> String:
	return ["Day", "Dusk", "Night"][of]


## Lights the map for its time of day: by day as it was made, else its sky,
## sun, ambient light and glow made dusk's or night's, on copies of its
## environment and sky, since the map's own are shared by every battle fought
## on it.
func apply() -> void:
	RenderingServer.global_shader_parameter_set(GLOBAL, 1.0 if lamps_lit() else 0.0)
	if time == Period.DAY:
		return
	var holder := get_node_or_null(environment_path) as WorldEnvironment
	var sun := get_node_or_null(sun_path) as DirectionalLight3D
	if holder == null or holder.environment == null or sun == null:
		push_error("TimeOfDay: no WorldEnvironment or sun, so the map is lit as by day.")
		return
	var env := holder.environment.duplicate(true) as Environment
	holder.environment = env
	var sky: ProceduralSkyMaterial = null
	if env.sky != null and env.sky.sky_material is ProceduralSkyMaterial:
		sky = env.sky.sky_material as ProceduralSkyMaterial
	# The glow: a bloom round what shines brighter than white, the glowing
	# voxels among it; a sunlit wall at dusk never does.
	env.glow_enabled = true
	env.glow_intensity = 0.8
	env.glow_strength = 1.0
	env.glow_bloom = 0.0
	env.glow_blend_mode = Environment.GLOW_BLEND_MODE_SOFTLIGHT
	env.glow_hdr_threshold = 1.0
	match time:
		Period.DUSK:
			if sky != null:
				sky.sky_top_color = Color(0.16, 0.2, 0.38)
				sky.sky_horizon_color = Color(0.85, 0.52, 0.34)
				sky.ground_bottom_color = Color(0.1, 0.1, 0.16)
				sky.ground_horizon_color = Color(0.55, 0.38, 0.3)
			sun.light_color = Color(1.0, 0.62, 0.38)
			sun.light_energy = 0.55
			# The map's sun, as low as dusk: its heading kept.
			var heading := -sun.global_basis.z
			var flat := Vector3(heading.x, 0.0, heading.z)
			if flat.length_squared() > 1e-6:
				flat = flat.normalized()
				var down := flat * cos(deg_to_rad(DUSK_ELEVATION)) + Vector3.DOWN * sin(deg_to_rad(DUSK_ELEVATION))
				sun.global_basis = Basis.looking_at(down, Vector3.UP)
			env.ambient_light_energy = 0.55
		Period.NIGHT:
			if sky != null:
				sky.sky_top_color = Color(0.012, 0.018, 0.045)
				sky.sky_horizon_color = Color(0.045, 0.06, 0.1)
				sky.ground_bottom_color = Color(0.01, 0.012, 0.02)
				sky.ground_horizon_color = Color(0.035, 0.045, 0.07)
			# The moon: where the sun was, faint and blue.
			sun.light_color = Color(0.55, 0.66, 1.0)
			sun.light_energy = 0.22
			# Light everywhere enough to fight by, as the night sky gives none.
			env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
			env.ambient_light_color = Color(0.11, 0.13, 0.2)
			env.ambient_light_energy = 1.0
