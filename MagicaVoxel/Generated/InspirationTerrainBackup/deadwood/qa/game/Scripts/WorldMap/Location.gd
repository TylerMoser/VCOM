## Something in a village the party can use, such as its hiring board or its
## market. Each village has its own mix, listed in its [member
## Destination.locations].
##
## It is a line in its village's tooltip and a tab in its [VillageMenu]. A
## kind of location that does something extends this with a tab of its own
## ([HiringBoard], [Market]); the rest get a placeholder tab for now.
##
## Like [Item], it is data and stays stateless. A kind whose content differs
## between villages, such as a hiring board or a market, has a resource per
## village; one that would be the same everywhere could be one resource they
## all share. What changes in play, such as who is still for hire, lives in
## [code]Campaign[/code].
class_name Location
extends Resource

## Shown in the tooltip of every village that has it.
@export var display_name := ""
## What it is, shown on its tab in the village menu.
@export_multiline var description := ""


## The tab it gets in the village menu, made afresh each time the menu opens.
func make_tab() -> Control:
	return LocationTab.new(self)
