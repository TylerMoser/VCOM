#!/usr/bin/env bash
# Solve and draw one variant of the kingdoms' new borders.
# Usage: run_kingdoms.sh <tag> <band km> <major> <spur toll> <front toll> [near enough]
SP="${MAP_WORK:?set MAP_WORK to the working folder: it held out/ and the staging folders}"
T="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${MAP_REPO:?set MAP_REPO to the repository}"
PY="${MAP_PYTHON:-python}"
TAG="$1"; BAND="$2"
KING="$SP/out/king$BAND"
cd "$SP" || exit 1
if [ ! -e "$KING/fields.npz" ]; then
    "$PY" -u "$T/k1_fields.py" "$SP/out/water" "$SP/out/duchy" "$KING" "$BAND" > "$KING.k1.log" 2>&1
    tail -3 "$KING.k1.log"
fi
"$PY" -u "$T/k2_solve.py" "$SP/out/duchy" "$KING" "$TAG" "$3" "$4" "$5" ${6:-0.01} > "$KING/k2_$TAG.log" 2>&1
grep -v "^  try" "$KING/k2_$TAG.log"; grep -c "^  try" "$KING/k2_$TAG.log"
"$PY" -u "$T/k3_draw.py" "$ROOT" "$SP/out/duchy" "$KING" "$TAG" "$KING/Kingdoms2_$TAG.png" look > "$KING/k3_$TAG.log" 2>&1
cat "$KING/k3_$TAG.log"
