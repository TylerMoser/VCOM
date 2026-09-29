## What the party holds, as stacks in the order they are shown.
##
## Unlike an [Item] it is state: the one in play is [member Campaign.inventory],
## a copy of the starting inventory, so the stacks in the [code].tres[/code]
## are never changed. Emits [signal Resource.changed] whenever what it holds
## changes, so a view of it can keep up.
class_name Inventory
extends Resource

@export var stacks: Array[ItemStack] = []


## The stacks holding an item of [param kind], such as [Weapon] or
## [BattleItem], in order. Empty stacks are left out.
func stacks_of(kind: Script) -> Array[ItemStack]:
	var found: Array[ItemStack] = []
	for stack in stacks:
		if stack != null and stack.count > 0 and is_instance_of(stack.item, kind):
			found.append(stack)
	return found


## How many of [param item] there are.
func count_of(item: Item) -> int:
	var stack := _stack_of(item)
	return stack.count if stack != null else 0


## Takes one [param item] out. False, taking nothing, if there is none.
## A stack emptied this way stays, at 0, so the item keeps its place in the
## order if it comes back.
func take(item: Item) -> bool:
	var stack := _stack_of(item)
	if stack == null or stack.count <= 0:
		return false
	stack.count -= 1
	emit_changed()
	return true


## Puts [param count] of [param item] in: on its stack, or on a new one at
## the end of the order.
func add(item: Item, count := 1) -> void:
	var stack := _stack_of(item)
	if stack == null:
		stack = ItemStack.new()
		stack.item = item
		stack.count = 0
		stacks.append(stack)
	stack.count += count
	emit_changed()


func _stack_of(item: Item) -> ItemStack:
	for stack in stacks:
		if stack != null and stack.item == item:
			return stack
	return null
