## What the party holds, as stacks in the order they are shown.
##
## Unlike an [Item] it is state: the one in play is [member Campaign.inventory],
## a copy of the starting inventory, so the stacks in the [code].tres[/code]
## are never changed.
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
