## The village menu's tab for a [Market]: what it has for sale, shown as the
## pause menu's Inventory tab shows what the party holds (the same
## [InventoryTab], over the market's stock), and along the bottom a
## [PurchaseBar] that buys one of the selected item for its
## [member Item.price]. Bought, it leaves the market's stock for the party's
## inventory; a held item needs a hold for each one bought.
##
## Filled from [method Campaign.stock_of] as it enters the tree, which is each
## time the village menu opens, and keeps up with the stock as it sells.
class_name MarketTab
extends VBoxContainer

var market: Market

var _goods: InventoryTab
var _bar: PurchaseBar


func _init(for_market: Market) -> void:
	market = for_market
	name = market.display_name.validate_node_name()
	add_theme_constant_override(&"separation", 12)

	_goods = InventoryTab.new()
	_goods.name = "Goods"
	_goods.size_flags_vertical = SIZE_EXPAND_FILL
	_goods.selection_changed.connect(_show_offer)
	add_child(_goods)

	_bar = PurchaseBar.new()
	_bar.held.connect(_on_purchase_held)
	add_child(_bar)


func _ready() -> void:
	_goods.show_inventory(Campaign.stock_of(market))
	_show_offer()


func _show_offer() -> void:
	var stack := _goods.selected_stack()
	if stack == null:
		_bar.show_no_offer()
	else:
		_bar.show_offer("Purchase", stack.item.display_name, stack.item.price)


func _on_purchase_held() -> void:
	var stack := _goods.selected_stack()
	if stack == null:
		return
	var item := stack.item
	if not Campaign.buy(market, item):
		return
	_bar.news = "Bought %s." % item.display_name
	# The stock refilled the goods as it sold, before the news was set.
	_show_offer()
