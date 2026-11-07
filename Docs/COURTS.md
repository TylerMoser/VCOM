# Courts

Every settlement menu begins with Details. Every capital in Map.tscn has a
Court as its first location, immediately after Details: Court of Count
for the 176 county capitals, Court of Duke for the 35 duchy capitals, and
Court of King for the 9 kingdom capitals. Each capital has its own Court
subresource so later ruler names, descriptions, and favor can differ.
Existing locations follow the court in their prior order. Ordinary settlements
do not gain courts.

CourtTab is a single vertical scrolling page. The ruler's title is currently
their placeholder name. The header's right edge shows the favor icon, with a
tooltip identifying its meaning. All authored courts start neutral. Below are
Description & Information, Gain Favor By:, and Lose Favor By:. Each favor
list starts with a single bullet, "none".

The three icons in vcom/UI/Court are exact copies from PlaceholderIcons/white:
8-ui/arrow-up.png (favored), 11-symbols/minus.png (neutral), and
8-ui/arrow-down.png (not favored). Court.Favor selects the icon. This is the
initial display data; actions that change favor are not implemented yet.

Run Godot --headless --path vcom res://Tests/CourtTest.tscn to check all
capital assignments, ordering, independent resources, icon selection, and
long-page scrolling. A graphical run also saves a preview to the system temp
folder as voxel-court.png.
