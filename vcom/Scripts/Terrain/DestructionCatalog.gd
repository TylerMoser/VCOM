## Every kind of breakable block, and how each one breaks.
##
## One catalog is shared by every map, so a new breakable block is added to it
## once rather than to each map. A block with no entry never breaks.
class_name DestructionCatalog
extends Resource

@export var destructions: Array[Destruction] = []


## The destructions for the blocks of [param library], by item id. An entry
## naming a block the library does not have is reported and left out.
func by_item(library: MeshLibrary) -> Dictionary:
	var items := {}
	for destruction in destructions:
		if destruction == null:
			continue
		var item := library.find_item_by_name(destruction.block)
		if item < 0:
			push_error("DestructionCatalog: no block named '%s' in the MeshLibrary." % destruction.block)
			continue
		items[item] = destruction
	return items
