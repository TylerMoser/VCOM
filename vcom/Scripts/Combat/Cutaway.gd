## Whatever rests on what the level has cut away from the view, hidden with it
## ([method VoxelLevel.cut_away], [LevelCutaway]): a unit standing on a roof, a
## crate's pieces, a block falling, dropped gear, coins and lumps of debris
## lying there. Each is hidden while it is over a piece cut away, by where it is
## ([method VoxelLevel.is_cut_away]), looked at every frame while anything is
## cut away, since things move; and shown again the moment it is not. The
## lumps of debris see to themselves as they move ([member VoxelDebris.hides]).
##
## Only for show, as the cut is: a hidden unit stands on its tile to the rules,
## and is seen, shot at and shoots as ever. It takes no clicks while hidden
## ([method Unit.set_cut_away]), so a click goes through to what is seen. Only
## what was hidden here is shown again here: a node something else hid stays
## hidden.
class_name Cutaway
extends Node

@export var level_path: NodePath = ^"../Level"
@export var destruction_path: NodePath = ^"../TerrainDestruction"
@export var coins_path: NodePath = ^"../Coins"

var _level: VoxelLevel
var _destruction: TerrainDestruction
var _coins: Node
## The nodes hidden here, as a set: only these are ever shown again.
var _hidden := {}


func _ready() -> void:
	set_process(false)
	_level = get_node_or_null(level_path) as VoxelLevel
	if _level == null:
		push_error("Cutaway: no VoxelLevel at '%s', so nothing is hidden with what it cuts away." % level_path)
		return
	_destruction = get_node_or_null(destruction_path) as TerrainDestruction
	if _destruction == null:
		push_error("Cutaway: no TerrainDestruction at '%s': pieces and debris stay in view." % destruction_path)
	_coins = get_node_or_null(coins_path)
	if _coins == null:
		push_error("Cutaway: no Coins at '%s': coins stay in view." % coins_path)
	_level.cut_changed.connect(_on_cut_changed)


func _process(_delta: float) -> void:
	_hide_what_rests()


func _on_cut_changed() -> void:
	var cut := _level.cutaway != null
	set_process(cut)
	if _destruction != null and _destruction.voxel_debris != null:
		var debris := _destruction.voxel_debris
		debris.hides = _level.is_cut_away if cut else Callable()
		# Nothing below the lowest height cut away is hidden: the level's own
		# height there, in the world.
		debris.hide_above = _level.to_global(Vector3(0.0, _level.cut_level(), 0.0)).y if cut else INF
		debris.rehide()
	_hide_what_rests()


## Hides each unit, piece, falling block and coin over what is cut away, and
## shows again each hidden here that is not.
func _hide_what_rests() -> void:
	var cut := _level.cutaway != null
	for node in get_tree().get_nodes_in_group(Unit.GROUP):
		_hide(node as Node3D, cut)
	for node in get_tree().get_nodes_in_group(TerrainDestruction.PIECES):
		_hide(node as Node3D, cut)
	if _destruction != null:
		for child in _destruction.get_children():
			if child is FallingBlock:
				_hide(child as Node3D, cut)
	if _coins != null:
		for child in _coins.get_children():
			_hide(child as Node3D, cut)
	# Untyped: a typed loop variable fails on a freed node before the check.
	for node in _hidden.keys():
		if not is_instance_valid(node):
			_hidden.erase(node)


## Hides [param node], or shows it again, by whether it is over what is cut
## away, with anything [param cut] away at all.
func _hide(node: Node3D, cut: bool) -> void:
	if node == null or not node.is_inside_tree():
		return
	var hidden := cut and _level.is_cut_away(node.global_position)
	if hidden == _hidden.has(node):
		return
	if hidden:
		# Something else hid it: it is that one's to show again.
		if not node.visible:
			return
		_hidden[node] = true
	else:
		_hidden.erase(node)
	if node is Unit:
		(node as Unit).set_cut_away(hidden)
	else:
		node.visible = not hidden
