## The state of the campaign that outlives any one scene: who is on the
## roster, what the party holds and what each of them has equipped, the
## party's gold, and who and what is left at each village's hiring board and
## market. An autoload, so the world map and combat read and change the same
## thing, and so saving has one place to look.
##
## Equipment moves only through [method equip] and [method unequip], which
## keep every item either in the inventory or on a character, never both, and
## skills are learned through [method learn].
##
## Battles are fought by characters from the roster, up to [constant SQUAD_SIZE]
## of them, chosen on the world map's [SquadMenu] as each battle starts
## ([method squad]), and what happens to them there stays with them: their wounds are written on
## the character as they are hit, a grenade they throw is gone from their gear
## for good ([method use_up]), and one who dies is taken off the roster
## ([method lose]). Wounds mend as the party travels ([method heal]).
##
## It also holds on to the world map while a battle started from it is
## fought ([method start_battle], [method end_battle]): the map's scene is
## taken out of the tree whole rather than freed, so it comes back exactly as
## it was left, the party mid-journey and the camera where it was.
extends Node

const STARTING_ROSTER := preload("res://Resources/StartingRoster.tres")
const STARTING_INVENTORY := preload("res://Resources/StartingInventory.tres")
const STARTING_GOLD := 100
## The most characters a battle takes: one per [SquadStart] a combat map has.
const SQUAD_SIZE := 4

## Who is on the roster is the campaign's to change; the characters in it are
## the same resources the combat maps' units point at, so they stay linked.
var roster: Roster = _copy_roster(STARTING_ROSTER)
## A copy of [constant STARTING_INVENTORY]: its stacks are the campaign's to
## change, its items are the shared resources.
var inventory: Inventory = STARTING_INVENTORY.duplicate_deep()
## The whole party's gold, one purse. Won battles earn it (see
## [member TurnManager.victory_gold]), and so does selling; hiring and buying
## spend it.
var gold := STARTING_GOLD
## Whether a battle is being fought. Set by the combat scene's [TurnManager]
## while it is in the tree. Equipment and skills cannot change during one: a
## unit took its gear when the map loaded, and would not see the change.
var in_mission := false
## Who is still for hire at each [HiringBoard], by board: a copy of the board's
## own list made the first time it is asked about, so the board's resource is
## never changed. Holding the board keeps it loaded, so the world map gets
## the same one back each time it opens.
var _for_hire := {}
## What is still for sale at each [Market], by market: a copy of the market's
## stock made the first time it is asked about, as [member inventory] is of
## the starting one (its stacks are copied, its items are not).
var _stock := {}
## The scene a battle was started from, out of the tree until the battle
## ends; null when there is none to go back to.
var _left_behind: Node = null
## Who was chosen for the battle being fought, or the last one fought; the dead
## are left in, and [method squad] leaves them out. Empty before the first.
var _chosen: Array[Character] = []


func _exit_tree() -> void:
	# Out of the tree, nothing else would ever free it.
	if _left_behind != null:
		_left_behind.free()
		_left_behind = null


## Takes one [param item] out of the inventory and puts it in [param slot]
## (a name from [member Character.slots]) on [param character], returning
## whatever was there to the inventory. False, changing nothing, during a
## mission, when there is none in the inventory, or when the slot does not
## take that kind of item.
func equip(character: Character, slot: StringName, item: Item) -> bool:
	if in_mission or item == null or not is_instance_of(item, Character.slot_kind(slot)):
		return false
	if not inventory.take(item):
		return false
	var old: Item = character.get(slot)
	if old != null:
		inventory.add(old)
	character.set(slot, item)
	return true


## Returns what is in [param slot] on [param character] to the inventory and
## leaves the slot empty. False, changing nothing, during a mission or when
## the slot is already empty.
func unequip(character: Character, slot: StringName) -> bool:
	var old: Item = character.get(slot)
	if in_mission or old == null:
		return false
	inventory.add(old)
	character.set(slot, null)
	return true


## Has [param character] learn [param node] of [param source]'s skill tree for
## a skill point ([method Character.learn]). False, changing nothing, during a
## mission, as equipping is: a unit takes what its character is when the map
## loads. Also false when the character cannot learn it yet.
func learn(character: Character, source: SkillSource, node: SkillTreeNode) -> bool:
	if in_mission or character == null:
		return false
	return character.learn(source, node)


## Who is still for hire at [param board], in the order it lists them.
func for_hire(board: HiringBoard) -> Array[Character]:
	if not _for_hire.has(board):
		_for_hire[board] = board.characters.duplicate()
	var available: Array[Character] = _for_hire[board]
	return available.duplicate()


## Pays [param character]'s [member Character.hire_cost] and moves them from
## [param board] to the end of the roster. False, changing nothing, when they
## are not for hire there or the party cannot afford them.
func hire(board: HiringBoard, character: Character) -> bool:
	if character == null or not for_hire(board).has(character) or gold < character.hire_cost:
		return false
	gold -= character.hire_cost
	(_for_hire[board] as Array).erase(character)
	roster.characters.append(character)
	return true


## What [param market] still has for sale. It changes only through
## [method buy], and emits [signal Resource.changed] when it does, so a view
## of it can keep up.
func stock_of(market: Market) -> Inventory:
	if not _stock.has(market):
		_stock[market] = market.stock.duplicate_deep() if market.stock != null else Inventory.new()
	return _stock[market]


## Pays [param item]'s [member Item.price] and moves one of it from
## [param market]'s stock into the party's inventory. False, changing
## nothing, when the market has none left or the party cannot afford it.
func buy(market: Market, item: Item) -> bool:
	if item == null or gold < item.price or not stock_of(market).take(item):
		return false
	gold -= item.price
	inventory.add(item)
	return true


## Takes one [param item] out of the party's inventory for good and adds its
## [method Item.sale_price] to the gold, which may be nothing. Every market
## pays the same and none keeps what it buys, so no market is named. False,
## changing nothing, when the inventory has none: an equipped item is not in
## it, so it cannot be sold until it is unequipped.
func sell(item: Item) -> bool:
	if item == null or not inventory.take(item):
		return false
	gold += item.sale_price()
	return true


## Who fights, at most [param count] of them, in roster order: those chosen
## for the battle being fought, which in between battles is the last one's,
## less any who died. When that leaves nobody (before the first battle, or
## after the whole squad fell), the first on the roster. So it is who a combat
## map spawns, and who the [SquadMenu] ticks as it opens.
func squad(count := SQUAD_SIZE) -> Array[Character]:
	var survivors: Array[Character] = []
	for character in roster.characters:
		if survivors.size() < count and _chosen.has(character):
			survivors.append(character)
	if survivors.is_empty():
		return roster.characters.slice(0, maxi(count, 0))
	return survivors


## Heals everyone on the roster by [param amount], none past their
## [member Character.max_health]: their [member Character.wounds] go down by
## it, to no less than none. The party does this as it travels.
func heal(amount: int) -> void:
	if amount <= 0:
		return
	for character in roster.characters:
		character.wounds = maxi(character.wounds - amount, 0)


## Takes [param item], used up in battle, off [param character] for good: out
## of the first of their slots holding it, and not back into the inventory, as
## a grenade goes once it is thrown. Like [method lose] it works during a
## battle, which [method unequip] refuses. False, changing nothing, when they
## have none equipped.
func use_up(character: Character, item: Item) -> bool:
	if item == null:
		return false
	for slot in Character.slots:
		if character.get(slot[1]) == item:
			character.set(slot[1], null)
			return true
	return false


## Takes [param character], killed in battle, off the roster for good. What
## they had equipped goes back to the inventory, whatever the battle's
## outcome. Beside [method use_up], this is the one way gear leaves a
## character during a battle, which [method unequip] refuses: the unit that
## took it is gone.
func lose(character: Character) -> void:
	if not roster.characters.has(character):
		return
	roster.characters.erase(character)
	for slot in Character.slots:
		var item: Item = character.get(slot[1])
		if item != null:
			inventory.add(item)
			character.set(slot[1], null)


## Leaves the scene being played for a battle on [param map], fought by
## [param chosen], keeping that scene as it stands to go back to in
## [method end_battle]. False, changing nothing, while a battle is already
## waiting to be gone back from, or when [param chosen] is nobody, more than
## [constant SQUAD_SIZE], or anyone not on the roster.
func start_battle(map: PackedScene, chosen: Array[Character]) -> bool:
	var tree := get_tree()
	if _left_behind != null or map == null or tree.current_scene == null:
		return false
	if chosen.is_empty() or chosen.size() > SQUAD_SIZE:
		return false
	for character in chosen:
		if not roster.characters.has(character):
			return false
	_chosen = chosen.duplicate()
	_left_behind = tree.current_scene
	# At the end of the frame, not in the middle of the scene's own processing.
	_switch_scene.call_deferred(_left_behind, map.instantiate(), false)
	return true


## Ends the battle being played and goes back to the scene it was started
## from, as it was left. False, changing nothing, when there is none: a battle
## opened on its own stays open.
func end_battle() -> bool:
	if _left_behind == null:
		return false
	_switch_scene.call_deferred(get_tree().current_scene, _left_behind, true)
	_left_behind = null
	return true


## Takes [param from] out of the tree, freeing it when [param free_from], and
## makes [param to] the current scene.
func _switch_scene(from: Node, to: Node, free_from: bool) -> void:
	var tree := get_tree()
	tree.root.remove_child(from)
	if free_from:
		from.queue_free()
	tree.root.add_child(to)
	tree.current_scene = to


static func _copy_roster(from: Roster) -> Roster:
	var copy := Roster.new()
	copy.characters = from.characters.duplicate()
	return copy
