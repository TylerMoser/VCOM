# Courts

Every settlement menu begins with Details, with the settlement's display_name
as a heading at the top of the page. The tab itself remains titled Details.
All 2,220 settlement display names are assigned from NAMING.md; headings and
map tooltips therefore show the same authored settlement name.
Every capital in Map.tscn has a
Court as its first location, immediately after Details: Court of Count <name>
for the 176 county capitals, Court of Duke <name> for the 35 duchy capitals, and
Court of King <name> for the 9 kingdom capitals. All 220 ruler names come from
the court assignment registers in NAMING.md. Each capital has its own Court
subresource so ruler names, descriptions, and favor can differ.
Existing locations follow the court in their prior order. Ordinary settlements
do not gain courts.

CourtTab is a single vertical scrolling page. Its header uses ruler_name,
including both title and personal name (for example, Count Velfeyald).
The location's display_name is Court of followed by that same ruler_name;
settlement tooltips and tabs use this display_name. The header's right edge shows the favor icon, with a
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
