## What a character wears into battle, in their Armor slot.
##
## So far it only adds to the wearer's defense. How heavy it is, and anything
## else it protects against, belong here too.
class_name Armor
extends Item

## Added to the wearer's [member Character.defense] (see
## [member Character.total_defense]), so every hit their unit takes does this
## much less damage.
@export var defense := 0
