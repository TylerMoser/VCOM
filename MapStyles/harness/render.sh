#!/usr/bin/env bash
# Renders map style proposals with the real game: each style id becomes
# MapStyles/NN-name.png, four views of Scenes/Map.tscn side by side.
#
#   MapStyles/harness/render.sh 0 3 12          # -> MapStyles/
#   OUT_DIR=/some/dir MapStyles/harness/render.sh 0
#   GODOT=/path/to/godot MapStyles/harness/render.sh 4
#   EXTRA="--filter=deutan --tag=-deutan" MapStyles/harness/render.sh 0   # as a deuteranope sees it
#   EXTRA="--views=C,D --panels" MapStyles/harness/render.sh 5           # only some views, each saved too
#   BEFORE=1 MapStyles/harness/render.sh 5      # on the scene as it was before 02, 04, 05 and 10 were applied
#
# Style 0 is the map exactly as the scene has it, which makes it the way to
# check a style after applying it for real. The proposals were written for, and
# pictured on, the scene as it was before the look was applied (commit
# d8b5ec7): BEFORE=1 renders on a copy of that scene, and its four forest kinds,
# taken from git into _probe/before/, and never touches the scene itself.
#
# It copies the harness into vcom/_probe/ for the run and deletes it
# afterwards, as CLAUDE.md asks of probes. It needs a real window (not
# --headless) to render.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PROJ="$(cd "$HERE/../../vcom" && pwd)"
G="${GODOT:-/c/Program Files/Godot/Godot_v4.7-stable_win64_console.exe}"
OUT="${OUT_DIR:-$HERE/..}"

if [ $# -eq 0 ]; then
	echo "usage: $0 <style id> [<style id> ...]" >&2
	exit 1
fi

mkdir -p "$OUT" "$PROJ/_probe"
trap 'rm -rf "$PROJ/_probe"' EXIT
cp "$HERE"/MapStyleProbe.gd "$HERE"/MapStyleProbe.tscn "$HERE"/StyleKit.gd "$PROJ/_probe/"
cp -r "$HERE"/styles "$HERE"/shaders "$HERE"/runtime "$PROJ/_probe/"

MAP_ARG=""
if [ -n "${BEFORE:-}" ]; then
	REPO="$(cd "$HERE/../.." && pwd)"
	mkdir -p "$PROJ/_probe/before"
	# Its uid is the scene's own, so the copy goes without; its forests are
	# instances of the kinds' scenes as they were then, beside it.
	git -C "$REPO" show d8b5ec7:vcom/Scenes/Map.tscn \
		| sed -e '1s/ uid="[^"]*"//' \
			-e 's#res://Scenes/\(Conifer\|Broadleaf\|Swamp\|Tropical\)Forest\.tscn#res://_probe/before/\1Forest.tscn#' \
		> "$PROJ/_probe/before/Map.tscn"
	for kind in Conifer Broadleaf Swamp Tropical; do
		git -C "$REPO" show "d8b5ec7:vcom/Scenes/${kind}Forest.tscn" > "$PROJ/_probe/before/${kind}Forest.tscn"
	done
	MAP_ARG="--map=res://_probe/before/Map.tscn"
fi

# Godot on Windows wants C:/... rather than /c/...
OUT_GODOT="$OUT"
DATA_GODOT="$HERE/data"
if command -v cygpath > /dev/null; then
	OUT_GODOT="$(cygpath -m "$OUT")"
	DATA_GODOT="$(cygpath -m "$HERE/data")"
fi

cd "$PROJ"
for id in "$@"; do
	# shellcheck disable=SC2086
	timeout 300 "$G" --path . --resolution 1280x720 --fixed-fps 60 --disable-vsync res://_probe/MapStyleProbe.tscn \
		-- --style="$id" --outdir="$OUT_GODOT" --data="$DATA_GODOT" $MAP_ARG ${EXTRA:-} 2>&1 \
		| grep --line-buffered -E "MapStyleProbe:|ERROR|SCRIPT ERROR|WARNING: StyleKit|at: " || true
done
