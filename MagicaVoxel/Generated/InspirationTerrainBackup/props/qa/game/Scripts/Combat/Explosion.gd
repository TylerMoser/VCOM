## A grenade going off: a ball of fire that swells to about the size of its
## blast and fades, a flash that lights up everything round it for a moment,
## and a puff of smoke left hanging over the spot. Only for show, and gone
## once it has played: it frees itself.
##
## Built in code, as the HUD is, from plain spheres and a light.
class_name Explosion
extends Node3D

## Seconds the fireball takes to swell to full size, and to fade after.
const SWELL_SECONDS := 0.12
const FADE_SECONDS := 0.4
## Seconds the smoke hangs, and how far it drifts up while it fades.
const SMOKE_SECONDS := 1.4
const SMOKE_RISE := 0.8
## The fireball's size, as a share of the blast's width: its outer shell, and
## the white-hot core inside it.
const FIRE_SHARE := 0.45
const CORE_SHARE := 0.25
const SMOKE_SHARE := 0.4
const FIRE_COLOR := Color(1.0, 0.55, 0.15, 0.85)
const CORE_COLOR := Color(1.0, 0.93, 0.65, 1.0)
const SMOKE_COLOR := Color(0.2, 0.19, 0.18, 0.55)
## The flash: its colour, how bright it starts, and how far it reaches as a
## share of the blast's width.
const LIGHT_COLOR := Color(1.0, 0.7, 0.4)
const LIGHT_ENERGY := 6.0
const LIGHT_REACH := 2.0

var _fire: MeshInstance3D
var _core: MeshInstance3D
var _smoke: MeshInstance3D
var _light: OmniLight3D


## An explosion as wide as a blast [param size] cells across.
func _init(size := 1.0) -> void:
	_smoke = _sphere(SMOKE_COLOR, size * SMOKE_SHARE)
	_fire = _sphere(FIRE_COLOR, size * FIRE_SHARE)
	_core = _sphere(CORE_COLOR, size * CORE_SHARE)
	_light = OmniLight3D.new()
	_light.light_color = LIGHT_COLOR
	_light.light_energy = LIGHT_ENERGY
	_light.omni_range = size * LIGHT_REACH
	add_child(_light)


## Sets off an explosion as wide as a blast [param size] cells across, at
## [param at], under [param parent].
static func go_off(parent: Node, at: Vector3, size: float) -> Explosion:
	var explosion := Explosion.new(size)
	parent.add_child(explosion)
	explosion.global_position = at
	explosion._play()
	return explosion


func _play() -> void:
	for ball: MeshInstance3D in [_fire, _core, _smoke]:
		ball.scale = Vector3.ONE * 0.2
	var tween := create_tween().set_parallel()
	tween.tween_property(_fire, ^"scale", Vector3.ONE, SWELL_SECONDS).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	tween.tween_property(_core, ^"scale", Vector3.ONE, SWELL_SECONDS).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	tween.tween_property(_fire.material_override, ^"albedo_color:a", 0.0, FADE_SECONDS).set_delay(SWELL_SECONDS)
	tween.tween_property(_core.material_override, ^"albedo_color:a", 0.0, FADE_SECONDS * 0.6).set_delay(SWELL_SECONDS)
	tween.tween_property(_light, ^"light_energy", 0.0, SWELL_SECONDS + FADE_SECONDS).set_ease(Tween.EASE_IN)
	# The smoke comes up as the fire goes, and lingers.
	tween.tween_property(_smoke, ^"scale", Vector3.ONE * 1.3, SMOKE_SECONDS).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	tween.tween_property(_smoke, ^"position:y", SMOKE_RISE, SMOKE_SECONDS).set_ease(Tween.EASE_OUT)
	tween.tween_property(_smoke.material_override, ^"albedo_color:a", 0.0, SMOKE_SECONDS).set_ease(Tween.EASE_IN)
	tween.chain().tween_callback(queue_free)


## A plain sphere of [param radius] in [param color], unlit so it glows the
## same whatever the light, and see-through by its colour's alpha.
func _sphere(color: Color, radius: float) -> MeshInstance3D:
	var sphere := SphereMesh.new()
	sphere.radius = radius
	sphere.height = radius * 2.0
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.albedo_color = color
	var ball := MeshInstance3D.new()
	ball.mesh = sphere
	ball.material_override = material
	ball.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(ball)
	return ball
