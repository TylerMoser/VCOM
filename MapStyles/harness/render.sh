#!/usr/bin/env bash
# Renders map style proposals with the real game: each style id becomes
# MapStyles/NN-name.png, four views of Scenes/Map.tscn side by side.
#
#   MapStyles/harness/render.sh 0 3 12          # -> MapStyles/
#   OUT_DIR=/some/dir MapStyles/harness/render.sh 0
#   GODOT=/path/to/godot MapStyles/harness/render.sh 4
#   EXTRA="--filter=deutan --tag=-deutan" MapStyles/harness/render.sh 0   # as a deuteranope sees it
#   EXTRA="--views=C,D --panels" MapStyles/harness/render.sh 5           # only some views, each saved too
#   BEFORE=1 MapStyles/harness/render.sh 5      # on the map as it was before 02, 04, 05 and 10 were applied
#
# Style 0 is the map exactly as the scene has it, which makes it the way to
# check a style after applying it for real; it and 91, the map close in, are
# MapStyles/'s pictures of the current look. The proposals were written for, and
# pictured on, the map as it was before the look was applied (commit d8b5ec7):
# BEFORE=1 renders on a copy of that scene, its four forest kinds and its
# MapDetail.gd (which 14b and 19a have changed since), taken from git into
# _probe/before/, and never touches the scene itself. The variants revisited on
# 2026-10-19 (styles 100 to 200) need no BEFORE: each puts the scene back as
# it was then itself (StyleKit.as_revisited()).
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
if [ -n "${BEFORE:-}" ] && [ -z "${OUT_DIR:-}" ]; then
	# Styles 0 and 91 write MapStyles/'s pictures of the current look: drawn on the
	# map as it was, they would put the old look in their place.
	for id in "$@"; do
		case "$((10#$id))" in
		0 | 91)
			echo "render.sh: BEFORE=1 would draw the old look over MapStyles/'s picture of style $id; give it an OUT_DIR" >&2
			exit 1
			;;
		esac
	done
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
	# instances of the kinds' scenes as they were then, beside it, and its
	# Detail node has MapDetail as it was then, without the class name the
	# game's own holds.
	git -C "$REPO" show d8b5ec7:vcom/Scenes/Map.tscn \
		| sed -e '1s/ uid="[^"]*"//' \
			-e 's#res://Scenes/\(Conifer\|Broadleaf\|Swamp\|Tropical\)Forest\.tscn#res://_probe/before/\1Forest.tscn#' \
			-e 's#res://Scripts/WorldMap/MapDetail\.gd#res://_probe/before/MapDetail.gd#' \
		> "$PROJ/_probe/before/Map.tscn"
	for kind in Conifer Broadleaf Swamp Tropical; do
		git -C "$REPO" show "d8b5ec7:vcom/Scenes/${kind}Forest.tscn" > "$PROJ/_probe/before/${kind}Forest.tscn"
	done
	git -C "$REPO" show d8b5ec7:vcom/Scripts/WorldMap/MapDetail.gd \
		| sed -e '/^class_name MapDetail$/d' > "$PROJ/_probe/before/MapDetail.gd"
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
