## The Roster's Equipment page: the character's slots along the top, and
## under the selected one the inventory's items that fit it, in an
## [ItemBrowser] whose action equips the chosen item. A line between the two
## says what the slot holds, with a button to take it off.
##
## Equipping and unequipping go through [Campaign], which moves one copy
## between the inventory and the character. During a mission the page only
## shows: both buttons are greyed out and a note says why. Read only, for
## someone not on the roster, it shows just the slots and what they hold.
class_name EquipmentPage
extends CharacterPage

const BORDER_COLOR := Color(0.3, 0.32, 0.4)
const BUTTON_BG_COLOR := Color(0.14, 0.15, 0.2, 0.95)
const BUTTON_HOVER_COLOR := Color(0.18, 0.19, 0.25, 0.95)
const ACCENT_COLOR := Color(1.0, 0.9, 0.55)
const TEXT_COLOR := Color(0.85, 0.86, 0.9)
const MUTED_COLOR := Color(0.55, 0.56, 0.62)

var _slot_group := ButtonGroup.new()
var _slots: Array[SlotButton] = []
var _status: Label
var _locked_note: Label
var _unequip: Button
var _rule: HSeparator
var _browser: ItemBrowser


func _init() -> void:
	super("Equipment")
	var layout := VBoxContainer.new()
	layout.set_anchors_preset(PRESET_FULL_RECT)
	layout.add_theme_constant_override(&"separation", 14)
	add_child(layout)

	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override(&"separation", 8)
	layout.add_child(row)
	for entry in Character.slots:
		var button := SlotButton.new(entry[0], entry[1], _slot_group)
		button.toggled.connect(func(on: bool) -> void:
			if on:
				_show_slot())
		row.add_child(button)
		_slots.append(button)
	FocusChain.link(row.get_children())

	var status_line := HBoxContainer.new()
	status_line.add_theme_constant_override(&"separation", 16)
	layout.add_child(status_line)
	_status = Label.new()
	_status.add_theme_font_size_override(&"font_size", 16)
	_status.add_theme_color_override(&"font_color", TEXT_COLOR)
	status_line.add_child(_status)
	_unequip = _button("Unequip")
	_unequip.pressed.connect(_on_unequip_pressed)
	status_line.add_child(_unequip)
	_locked_note = Label.new()
	_locked_note.text = "Equipment can't be changed during a mission."
	_locked_note.add_theme_font_size_override(&"font_size", 15)
	_locked_note.add_theme_color_override(&"font_color", MUTED_COLOR)
	status_line.add_child(_locked_note)

	_rule = HSeparator.new()
	var line := StyleBoxLine.new()
	line.color = BORDER_COLOR
	_rule.add_theme_stylebox_override(&"separator", line)
	layout.add_child(_rule)

	_browser = ItemBrowser.new("Items")
	_browser.size_flags_vertical = SIZE_EXPAND_FILL
	_browser.empty_text = "Nothing in the inventory fits this slot."
	_browser.set_action("Equip")
	_browser.action_requested.connect(_on_equip_requested)
	layout.add_child(_browser)

	_slots[0].button_pressed = true


func focus_selection() -> bool:
	var button := _slot_group.get_pressed_button()
	if button == null:
		return false
	button.grab_focus()
	return true


## Shows the character's slots, keeping the selected one (so characters can
## be compared slot by slot), and what fits it.
func _refresh() -> void:
	for button in _slots:
		button.show_item(character.get(button.slot) if character != null else null)
	_rule.visible = not read_only
	_browser.visible = not read_only
	_show_slot()


## Shows the selected slot: what it holds, and the inventory's items that fit.
func _show_slot() -> void:
	var button := _slot_group.get_pressed_button() as SlotButton
	# Not before the page is shown: the first slot is selected while it is
	# still being built.
	if button == null or not is_inside_tree():
		return
	var held: Item = character.get(button.slot) if character != null else null
	var locked := Campaign.in_mission
	_status.text = "%s: %s" % [button.title, held.display_name if held != null else "Empty"]
	_unequip.visible = held != null and not read_only
	_unequip.disabled = locked
	_locked_note.visible = locked and not read_only
	if not read_only:
		_browser.show_stacks(Campaign.inventory.stacks_of(Character.slot_kind(button.slot)))
		_browser.set_action_enabled(character != null and not locked)


func _on_equip_requested(stack: ItemStack) -> void:
	var button := _slot_group.get_pressed_button() as SlotButton
	if character != null and button != null and Campaign.equip(character, button.slot, stack.item):
		_refresh()


func _on_unequip_pressed() -> void:
	var button := _slot_group.get_pressed_button() as SlotButton
	if character != null and button != null and Campaign.unequip(character, button.slot):
		_refresh()
		# The button hides with the slot empty; the keyboard goes back up to it.
		button.grab_focus()


func _button(text: String) -> Button:
	var button := Button.new()
	button.text = text
	button.custom_minimum_size = Vector2(110, 32)
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	button.add_theme_font_size_override(&"font_size", 15)
	button.add_theme_stylebox_override(&"normal", _button_style(BUTTON_BG_COLOR, BORDER_COLOR))
	button.add_theme_stylebox_override(&"hover", _button_style(BUTTON_HOVER_COLOR, ACCENT_COLOR))
	button.add_theme_stylebox_override(&"pressed", _button_style(BUTTON_HOVER_COLOR, ACCENT_COLOR))
	button.add_theme_stylebox_override(&"focus", _button_style(Color.TRANSPARENT, Color.WHITE))
	button.add_theme_stylebox_override(&"disabled", _button_style(BUTTON_BG_COLOR, BORDER_COLOR))
	button.add_theme_color_override(&"font_disabled_color", MUTED_COLOR)
	return button


static func _button_style(background: Color, edge: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = edge
	style.set_border_width_all(1)
	style.set_corner_radius_all(4)
	return style
