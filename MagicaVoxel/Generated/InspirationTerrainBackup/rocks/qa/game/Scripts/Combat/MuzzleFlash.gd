## The flash at a gun's muzzle as it fires: a burst of light and a bright star
## that is gone in a few frames. Only for show, and it frees itself. Put it
## under the muzzle, so it rides the gun's kick.
##
## Built in code, as [Explosion] is, from boxes and a light: a cross of
## voxel-sized blades standing out ahead of the barrel.
class_name MuzzleFlash
extends Node3D

## Seconds it lasts, all of it fading.
const SECONDS := 0.07
## How far the flash reaches ahead of the muzzle, and across, in cells.
const LENGTH := 0.22
const WIDTH := 0.1
const COLOR := Color(1.0, 0.86, 0.45)
const LIGHT_COLOR := Color(1.0, 0.75, 0.4)
const LIGHT_ENERGY := 3.0
const LIGHT_RANGE := 2.5

var _light: OmniLight3D
var _blades: Array[MeshInstance3D] = []


func _init() -> void:
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.albedo_color = COLOR
	for size: Vector3 in [Vector3(WIDTH, WIDTH * 0.35, LENGTH), Vector3(WIDTH * 0.35, WIDTH, LENGTH)]:
		var box := BoxMesh.new()
		box.size = size
		var blade := MeshInstance3D.new()
		blade.mesh = box
		blade.material_override = material
		blade.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		blade.position = Vector3(0.0, 0.0, LENGTH * 0.5)
		add_child(blade)
		_blades.append(blade)
	_light = OmniLight3D.new()
	_light.light_color = LIGHT_COLOR
	_light.light_energy = LIGHT_ENERGY
	_light.omni_range = LIGHT_RANGE
	_light.position = Vector3(0.0, 0.0, LENGTH * 0.5)
	add_child(_light)


func _ready() -> void:
	# A quarter turn about the barrel, so no two shots flash quite alike.
	rotate_object_local(Vector3.BACK, randf() * PI * 0.5)
	var tween := create_tween().set_parallel()
	tween.tween_property(_light, ^"light_energy", 0.0, SECONDS)
	tween.tween_property(_blades[0].material_override, ^"albedo_color:a", 0.0, SECONDS).set_ease(Tween.EASE_IN)
	tween.tween_property(self, ^"scale", Vector3(0.6, 0.6, 1.3), SECONDS)
	tween.chain().tween_callback(queue_free)
