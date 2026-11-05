## Anything the party can carry: what it is called, what it looks like, what
## it says about itself in the inventory, and what it costs in a market. Kinds
## of item ([Weapon], [BattleItem]) extend it with what they do.
##
## Shared between every stack and unit that holds one, so, like [Weapon], it
## stays stateless: how many the party has lives in an [ItemStack].
class_name Item
extends Resource

## The tag on every gun. A unit carrying one is offered Shoot and Overwatch,
## and shoots with the first it carries.
const GUN := &"gun"
## The tag on every grenade. A unit carrying one is offered Throw Grenade.
const GRENADE := &"grenade"
## The tag on every melee weapon, such as the Shortsword. A unit carrying one
## is offered Strike.
const MELEE := &"melee"
## The tag on every medkit. A unit carrying one is offered Use Medkit.
const MEDKIT := &"medkit"

@export var display_name := ""
@export_multiline var description := ""
## Shown in the inventory's squares; without one the square shows the name.
@export var icon: Texture2D
## What the item looks like on a character in battle: in hand, slung across the
## back or hung on the belt (see [CharacterModel]). A scene whose origin is
## where the hand grips it, standing along +z with its top toward +y; a gun's
## [code]Muzzle[/code] marker is where it fires from, and its
## [code]Foregrip[/code] where the other hand holds it. Without one the item
## is carried unseen.
@export var model: PackedScene
## Gold a [Market] asks for one. Set here, on the item, so it is the same in
## every market.
@export var price := 0
## What sort of thing the item is, for the rules that ask, such as
## [constant GUN]. Finer than its class: a [Weapon] need not be a gun, and
## every gun gives the same actions whatever else it does. An action that
## needs one is offered only to a unit carrying an item with its tag (see
## [member UnitAction.required_tag]).
@export var tags: Array[StringName] = []


## Gold a [Market] pays for one: half its [member price], rounded down, so
## the same in every market, and nothing for an item priced at 1.
func sale_price() -> int:
	return floori(price / 2.0)


func has_tag(tag: StringName) -> bool:
	return tag in tags
