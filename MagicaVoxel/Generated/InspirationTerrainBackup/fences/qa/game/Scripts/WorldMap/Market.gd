## A village's market: items the party can buy, one at a time, each for its
## [member Item.price] in gold. Every market works and looks the same
## ([MarketTab]); what it has differs, so each village has its own.
##
## [member stock] is what it has when the campaign starts, and is never
## changed. What it still has, once the party has bought some, is
## [method Campaign.stock_of].
class_name Market
extends Location

## Stacks of what is for sale and how many, in the order the market shows
## them.
@export var stock: Inventory


func make_tab() -> Control:
	return MarketTab.new(self)
