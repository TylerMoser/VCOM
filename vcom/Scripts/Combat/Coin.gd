## A coin floating where a broken block stood, for the squad to pick up. It
## spins about its upright axis and bobs gently, as pickups do in most games;
## it pops in as it appears, drops when the ground under it goes, and flies up
## and shrinks away as it is taken, freeing itself. Only for show: [Coins]
## keeps which tile it is on, and nothing waits for it.
##
## Built in code, as [Explosion] is, round the coin's voxel model, which it
## centres on itself whatever frame the model was drawn in, so it spins on the
## spot rather than swinging round.
class_name Coin
extends Node3D

## Drawn nine voxels across, a little over half a cell, so it can be picked out
## at any zoom.
const MODEL: Mesh = preload("res://Items/Coin2.vox")
## Seconds a whole turn takes.
const SPIN_SECONDS := 1.5
## How far it rises and sinks from where it rests, in cells, and the seconds
## it takes to go up and down once.
const BOB_HEIGHT := 0.05
const BOB_SECONDS := 2.0
## Seconds it takes to pop in as it appears.
const POP_SECONDS := 0.3
## Seconds it takes to fly away as it is taken, and how far up it goes, in
## cells.
const TAKE_SECONDS := 0.25
const TAKE_RISE := 0.5
## The smallest it is drawn, popping in or shrinking away: a node cannot be
## scaled to nothing.
const TINY := 0.01

## Spins and bobs the model, so the coin itself stays where it rests.
var _spinner: Node3D
## Seconds it has spun, started at random so coins side by side are out of
## step.
var _age := 0.0
## The tween growing it as it pops in, and the one moving it as it drops or is
## taken. Null, or finished, once each is done.
var _popping: Tween
var _moving: Tween


func _init() -> void:
	name = &"Coin"
	_spinner = Node3D.new()
	add_child(_spinner)
	var model := MeshInstance3D.new()
	model.mesh = MODEL
	model.position = -MODEL.get_aabb().get_center()
	_spinner.add_child(model)
	_age = randf() * BOB_SECONDS


func _ready() -> void:
	scale = Vector3.ONE * TINY
	_popping = create_tween()
	_popping.tween_property(self, ^"scale", Vector3.ONE, POP_SECONDS).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func _process(delta: float) -> void:
	_age += delta
	_spinner.rotation.y = _age * TAU / SPIN_SECONDS
	_spinner.position.y = sin(_age * TAU / BOB_SECONDS) * BOB_HEIGHT


## Drops straight down to rest at [param point], gathering speed as it falls,
## as a unit does when the ground under it goes.
func drop_to(point: Vector3) -> void:
	var height := maxf(global_position.y - point.y, 0.0)
	if _moving != null:
		_moving.kill()
	_moving = create_tween()
	var fall := _moving.tween_property(self, ^"global_position", point, maxf(sqrt(2.0 * height / Unit.FALL_ACCELERATION), 0.01))
	fall.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)


## Flies up and shrinks away, taken, then frees itself.
func take() -> void:
	for tween in [_popping, _moving]:
		if tween != null:
			tween.kill()
	_moving = create_tween().set_parallel()
	_moving.tween_property(self, ^"position:y", position.y + TAKE_RISE, TAKE_SECONDS).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	_moving.tween_property(self, ^"scale", Vector3.ONE * TINY, TAKE_SECONDS).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	_moving.chain().tween_callback(queue_free)
