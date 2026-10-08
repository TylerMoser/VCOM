#!/usr/bin/env bash
# Lay and draw one variant of the kingdoms' new borders as cheapest lines.
# Usage: run_paths.sh <tag> [name=value ...]     (the options kb2_paths.py takes)
SP="${MAP_WORK:?set MAP_WORK to the working folder: it held out/ and the staging folders}"
T="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${MAP_REPO:?set MAP_REPO to the repository}"
PY="${MAP_PYTHON:-python}"
TAG="$1"; shift
KING="$SP/out/king30"; NET="$SP/out/kb30"
cd "$SP" || exit 1
"$PY" -u "$T/kb2_paths.py" "$SP/out/duchy" "$KING" "$NET" "$TAG" "$@" > "$NET/kb2_$TAG.log" 2>&1
grep -v "^    turn" "$NET/kb2_$TAG.log"
"$PY" -u "$T/k3_draw.py" "$ROOT" "$SP/out/duchy" "$KING" "$TAG" "$KING/Kingdoms2_$TAG.png" look > "$KING/k3_$TAG.log" 2>&1
cat "$KING/k3_$TAG.log"
"$PY" -u "$T/kb3_where.py" "$SP/out/duchy" "$KING" "$NET" "$TAG" 2>&1 | tail -17
"$PY" "$T/crops2.py" "$KING/look_${TAG}_full.png" "$KING" "$TAG" whole=0,0,3100,4000,0.5 > /dev/null
"$PY" "$T/crops2.py" "$KING/Kingdoms2_$TAG.png" "$KING" "${TAG}pic" whole=0,0,3100,4000,0.5 > /dev/null
