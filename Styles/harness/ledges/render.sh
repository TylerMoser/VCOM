#!/usr/bin/env bash
# Renders the ledge-readability comparison in Styles/LEDGES.md: BoundaryMap as
# the game currently looks, with each treatment on top, from the in-game camera
# facing both ways; then the two labelled sheets.
#
#   Styles/harness/ledges/render.sh            # all six treatments + sheets
#   Styles/harness/ledges/render.sh 1 5        # just these (sheets need all six)
#   OUT_DIR=/some/dir Styles/harness/ledges/render.sh
#
# Like ../render.sh it copies what it needs into vcom/_probe/ for the run and
# deletes it afterwards. Needs a real window (not --headless).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HARNESS="$(cd "$HERE/.." && pwd)"
PROJ="$(cd "$HARNESS/../../vcom" && pwd)"
G="${GODOT:-/c/Program Files/Godot/Godot_v4.7-stable_win64_console.exe}"
OUT="${OUT_DIR:-$HARNESS/out/ledges}"

mkdir -p "$OUT" "$PROJ/_probe/shaders"
trap 'rm -rf "$PROJ/_probe"' EXIT
cp "$HARNESS"/Variants.gd "$HARNESS"/VariantList.gd "$HARNESS"/VariantNotes.gd "$HERE"/LedgeProbe.gd "$PROJ/_probe/"
cp "$HARNESS"/shaders/*.gdshader "$PROJ/_probe/shaders/"
cat > "$PROJ/_probe/LedgeProbe.tscn" <<'EOF'
[gd_scene format=3]

[ext_resource type="Script" path="res://_probe/LedgeProbe.gd" id="1_probe"]

[node name="LedgeProbe" type="Node"]
script = ExtResource("1_probe")
EOF

# Godot on Windows wants C:/... rather than /c/...
OUT_GODOT="$OUT"
HERE_GODOT="$HERE"
if command -v cygpath > /dev/null; then
	OUT_GODOT="$(cygpath -m "$OUT")"
	HERE_GODOT="$(cygpath -m "$HERE")"
fi

TREATMENTS=("$@")
if [ ${#TREATMENTS[@]} -eq 0 ]; then
	TREATMENTS=(0 1 2 3 4 5)
fi

cd "$PROJ"
for id in "${TREATMENTS[@]}"; do
	"$G" --path . --resolution 1280x720 --fixed-fps 60 res://_probe/LedgeProbe.tscn \
		-- --treatment="$id" --outdir="$OUT_GODOT" 2>&1 | grep -E "LedgeProbe:|SCRIPT ERROR|ERROR:" | grep -v 'RID allocations' || true
done

if [ -f "$OUT/t5-view1.png" ] && [ -f "$OUT/t0-view0.png" ]; then
	"$G" --path . --resolution 1620x1000 --script "$HERE_GODOT/LedgeSheet.gd" -- --dir="$OUT_GODOT" 2>&1 \
		| grep -E "Sheet:|SCRIPT ERROR|ERROR:" | grep -v 'RID allocations' || true
fi
