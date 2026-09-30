## The row along the bottom of a village's shop tabs (Hiring Board, Market),
## under a rule: a note on the left, then the party's gold, and a
## [HoldButton] to buy what is selected, greyed out with a note saying so
## when the party cannot afford it. The Market's Sell sub-tab sells with it
## too, which the party can always afford.
##
## The tab shows each offer with [method show_offer] and does the buying or
## selling itself on [signal held], one per press: the button empties as it
## acts, and must be let go and pressed again to act again.
##
## The bar only reads [code]Campaign.gold[/code], and reads it again whenever
## it is shown, since the party may have spent gold on another tab of the
## village menu in between.
class_name PurchaseBar
extends VBoxContainer

## The button has been held down for its whole time: buy (or sell) what is
## on offer.
signal held

const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const TEXT_COLOR := Color(0.7, 0.72, 0.78)
const CAPTION_COLOR := Color(0.55, 0.56, 0.62)
const GOLD_COLOR := Color(1.0, 0.9, 0.55)

## Said on the left while the offer is affordable, such as who was hired
## last. Shown from the next offer on.
var news := ""

var _row: HBoxContainer
var _note: Label
var _gold: Label
var _button: HoldButton
## The offer showing, as given to [method show_offer]; empty with none.
var _verb := ""
var _what := ""
var _price := 0
var _sale := false


func _init() -> void:
	add_theme_constant_override(&"separation", 12)

	var rule := HSeparator.new()
	var line := StyleBoxLine.new()
	line.color = BORDER_COLOR
	rule.add_theme_stylebox_override(&"separator", line)
	add_child(rule)

	_row = HBoxContainer.new()
	_row.add_theme_constant_override(&"separation", 10)
	add_child(_row)
	_note = Label.new()
	_note.size_flags_horizontal = SIZE_EXPAND_FILL
	_note.add_theme_font_size_override(&"font_size", 16)
	_note.add_theme_color_override(&"font_color", TEXT_COLOR)
	_row.add_child(_note)
	var caption := Label.new()
	caption.text = "Gold"
	caption.add_theme_font_size_override(&"font_size", 17)
	caption.add_theme_color_override(&"font_color", CAPTION_COLOR)
	_row.add_child(caption)
	_gold = Label.new()
	_gold.add_theme_font_size_override(&"font_size", 22)
	_gold.add_theme_color_override(&"font_color", GOLD_COLOR)
	_row.add_child(_gold)
	var gap := Control.new()
	gap.custom_minimum_size.x = 14
	_row.add_child(gap)
	_button = HoldButton.new()
	_button.held.connect(held.emit)
	# The row keeps the button's height when it hides, so the tab above does
	# not grow into the space.
	_button.minimum_size_changed.connect(func() -> void:
		_row.custom_minimum_size.y = _button.get_combined_minimum_size().y)
	_row.add_child(_button)


## Offers [param what] for [param price] gold, the button reading
## "[param verb] [param what] for [param price] Gold", as "Hire White for 20
## Gold". A [param sale] pays the party the price rather than costing it, so
## it is never greyed out.
func show_offer(verb: String, what: String, price: int, sale := false) -> void:
	_verb = verb
	_what = what
	_price = price
	_sale = sale
	_refresh()


## Nothing selected to buy: the button hides, and the gold and news stay.
func show_no_offer() -> void:
	_what = ""
	_refresh()


func _notification(what: int) -> void:
	if what == NOTIFICATION_VISIBILITY_CHANGED and is_visible_in_tree():
		_refresh()


func _refresh() -> void:
	_gold.text = str(Campaign.gold)
	_note.text = news
	_button.visible = not _what.is_empty()
	if _what.is_empty():
		return
	_button.caption = "%s %s for %d Gold" % [_verb, _what, _price]
	_button.disabled = not _sale and Campaign.gold < _price
	if _button.disabled:
		_note.text = "Not enough gold to %s %s." % [_verb.to_lower(), _what]
