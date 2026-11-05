## Keyboard order for a run of buttons in the pause menu (an item grid, the
## roster strip): left and right step through them in order, wrapping from
## row to row in a grid, and stop at the first and last rather than leaving
## for whatever lies beside them, which by distance is usually a tab row.
class_name FocusChain


static func link(controls: Array[Node]) -> void:
	for i in controls.size():
		var control := controls[i] as Control
		var before: Node = controls[i - 1] if i > 0 else control
		var after: Node = controls[i + 1] if i + 1 < controls.size() else control
		control.focus_neighbor_left = control.get_path_to(before)
		control.focus_neighbor_right = control.get_path_to(after)
