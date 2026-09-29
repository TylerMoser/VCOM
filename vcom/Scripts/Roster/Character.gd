## Someone on the player's roster, who they are between battles. A squad
## [Unit] in a combat map points at one ([member Unit.character]) and takes
## its name, colour and stats from it.
##
## Unlike an [Item] a character is state: it will gather experience, wounds and
## gear. The roster and the units share the loaded [code].tres[/code], so a
## change to one shows in the other. Nothing writes it back to disk.
class_name Character
extends Resource

## What [member experience] counts up to. Levelling is yet to come; until then
## this is only what the Details page's bar fills to.
const EXPERIENCE_TO_LEVEL := 100

@export var display_name := ""
## Placeholder identity colour: the unit's body in combat, and the portrait
## while the character has none.
@export var color := Color.WHITE
@export var portrait: Texture2D

@export_group("Stats")
## The unit's [member Unit.max_health]: what it can take before it falls.
@export var max_health := 10
## The unit's [member Unit.move_range]: tiles walked per action spent moving.
@export var move_range := 4
## The unit's [member Unit.aim]: its chance to hit before anything about the
## shot counts.
@export var aim := 90
## The unit's [member Unit.evasion]: taken off the chance of anyone shooting
## at it.
@export var evasion := 0
## Earned in play, out of [constant EXPERIENCE_TO_LEVEL]. Nothing awards it
## yet. Not copied onto the unit: it is the character's, not the battle's.
@export var experience := 0
