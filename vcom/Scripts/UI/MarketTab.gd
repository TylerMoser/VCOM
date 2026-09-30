## The village menu's tab for a [Market], in two sub-tabs, each laid out as
## the pause menu's Inventory tab (the same [InventoryTab]): Buy over what the
## market has for sale, Sell over what the party holds, less what is equipped.
## Along the bottom, under both, a [PurchaseBar] that buys one of the selected
## item for its [member Item.price], or sells one for its
## [method Item.sale_price]. Bought, it leaves the market's stock for the
## party's inventory; sold, it leaves the inventory for good. A held item
## needs a hold for each one bought or sold.
##
## Filled from [method Campaign.stock_of] and [member Campaign.inventory] as it
## enters the tree, which is each time the village menu opens, so it opens on
## Buy; it keeps up with both as they change hands.
class_name MarketTab
extends VBoxContainer

var market: Market

var _sides: SubTabs
var _buy: InventoryTab
var _sell: InventoryTab
var _bar: PurchaseBar


func _init(for_market: Market) -> void:
	market = for_market
	name = market.display_name.validate_node_name()
	add_theme_constant_override(&"separation", 12)

	_sides = SubTabs.new()
	_sides.size_flags_vertical = SIZE_EXPAND_FILL
	add_child(_sides)
	_buy = InventoryTab.new()
	_buy.name = "Buy"
	_sides.add_child(_buy)
	_sell = InventoryTab.new()
	_sell.name = "Sell"
	_sides.add_child(_sell)

	_bar = PurchaseBar.new()
	_bar.held.connect(_on_held)
	add_child(_bar)

	for side: InventoryTab in [_buy, _sell]:
		side.selection_changed.connect(_show_offer)
	_sides.tab_changed.connect(_show_offer.unbind(1))


func _ready() -> void:
	_buy.show_inventory(Campaign.stock_of(market))
	_sell.show_inventory(Campaign.inventory)
	_show_offer()


func _selling() -> bool:
	return _sides.get_current_tab_control() == _sell


func _show_offer() -> void:
	var stack := (_sell if _selling() else _buy).selected_stack()
	if stack == null:
		_bar.show_no_offer()
	elif _selling():
		_bar.show_offer("Sell", stack.item.display_name, stack.item.sale_price(), true)
	else:
		_bar.show_offer("Purchase", stack.item.display_name, stack.item.price)


func _on_held() -> void:
	var selling := _selling()
	var stack := (_sell if selling else _buy).selected_stack()
	if stack == null:
		return
	var item := stack.item
	if selling:
		if not Campaign.sell(item):
			return
		_bar.news = "Sold %s." % item.display_name
	else:
		if not Campaign.buy(market, item):
			return
		_bar.news = "Bought %s." % item.display_name
	# The side it changed refilled as the item changed hands, before the news
	# was set.
	_show_offer()
