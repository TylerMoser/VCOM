## A grenade: thrown at a tile, it goes off there, hurting everyone its blast
## catches, friend or foe, and breaking every breakable block it reaches. Any
## unit carrying one has Throw Grenade, and a grenade is gone for good once
## thrown (see [method Unit.throw_at]).
##
## What the blast does is the grenade's own. How far it can be thrown is not:
## every throw reaches [constant Throwing.RANGE] tiles, whatever is thrown.
##
## Shared between every stack and unit that holds one, so, like every
## [Item], it stays stateless.
class_name Grenade
extends BattleItem

## What the blast does to everyone it catches, before each one's defense comes
## off it, as it does off a shot's damage.
@export var damage := 5
## How wide the blast is, in tiles: a square this many tiles on a side,
## centred on the tile the grenade is thrown at, reaching as many cells up and
## down. A 3 takes in the eight tiles round the target, from the floor under
## them to a unit's head. Odd, so the target tile is its middle.
@export_range(1, 9, 2) var blast_size := 3
## How hard the blast hits the terrain it reaches, on the scale of
## [member Weapon.environment_damage]. For now every breakable block in the
## blast breaks, whatever this says.
@export var environment_damage := 10
## How hard the blast throws the debris inside it about, as a [Blast] force:
## 1 for a moderate blast, 0 for none.
@export var blast_force := 1.0
