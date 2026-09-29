## Anything the party can carry: what it is called, what it looks like, what
## it says about itself in the inventory, and what it costs in a market. Kinds
## of item ([Weapon], [BattleItem]) extend it with what they do.
##
## Shared between every stack and unit that holds one, so, like [Weapon], it
## stays stateless: how many the party has lives in an [ItemStack].
class_name Item
extends Resource

@export var display_name := ""
@export_multiline var description := ""
## Shown in the inventory's squares; without one the square shows the name.
@export var icon: Texture2D
## Gold a [Market] asks for one. Set here, on the item, so it is the same in
## every market.
@export var price := 0
