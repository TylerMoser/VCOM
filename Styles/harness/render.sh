#!/usr/bin/env bash
# Renders style previews with the real game: each style id becomes a
# two-panel NN-name.png (left: the game as it starts; right: a closer view with
# the HUD and tile highlights hidden).
#
#   Styles/harness/render.sh 1 21 28          # -> Styles/harness/out/
#   OUT_DIR=/some/dir Styles/harness/render.sh 0
#   GODOT=/path/to/godot Styles/harness/render.sh 4
#
# Style 0 always means "whatever the scene currently looks like", which makes
# it the way to check a style after applying it for real.
#
# It copies the harness into vcom/_probe/ for the run and deletes it afterwards,
# per CLAUDE.md. Needs a real window (not --headless) to render.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PROJ="$(cd "$HERE/../../vcom" && pwd)"
G="${GODOT:-/c/Program Files/Godot/Godot_v4.7-stable_win64_console.exe}"
OUT="${OUT_DIR:-$HERE/out}"

if [ $# -eq 0 ]; then
	echo "usage: $0 <style id> [<style id> ...]" >&2
	exit 1
fi

mkdir -p "$OUT" "$PROJ/_probe/shaders"
trap 'rm -rf "$PROJ/_probe"' EXIT
cp "$HERE"/VisualProbe.gd "$HERE"/VisualProbe.tscn "$HERE"/Variants.gd "$HERE"/VariantList.gd "$HERE"/VariantNotes.gd "$PROJ/_probe/"
cp "$HERE"/shaders/*.gdshader "$PROJ/_probe/shaders/"

# Godot on Windows wants C:/... rather than /c/...
OUT_GODOT="$OUT"
if command -v cygpath > /dev/null; then
	OUT_GODOT="$(cygpath -m "$OUT")"
fi

cd "$PROJ"
for id in "$@"; do
	"$G" --path . --resolution 1280x720 --fixed-fps 60 res://_probe/VisualProbe.tscn \
		-- --variant="$id" --outdir="$OUT_GODOT" 2>&1 | grep -E "VisualProbe:|ERROR|SCRIPT ERROR" || true
done
