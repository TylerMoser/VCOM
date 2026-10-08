#!/usr/bin/env bash
# Solve, draw to a draft, and check. Usage: run_counties.sh <tag> <ease> <near_enough> [duchies]
SP="${MAP_WORK:?set MAP_WORK to the working folder: it held out/ and the staging folders}"
T="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${MAP_REPO:?set MAP_REPO to the repository}"
PY="${MAP_PYTHON:-python}"
TAG="$1"
"$PY" -u "$T/c1_counties.py" "$SP/out/duchy" "$TAG" "$2" "$3" $4 > "$SP/out/duchy/c1_$TAG.log" 2>&1
grep "SUMMARY\|Error\|error\|Traceback\|isles\|saved" "$SP/out/duchy/c1_$TAG.log"
if [ -n "$4" ]; then exit 0; fi
"$PY" -u "$T/c2_draw.py" "$ROOT" "$SP/out/duchy" "$TAG" "$SP/out/duchy/Counties_draft_$TAG.png" look > "$SP/out/duchy/c2_$TAG.log" 2>&1
grep -v "^  [ 0-9]* (" "$SP/out/duchy/c2_$TAG.log"
"$PY" -u "$T/c3_oddities.py" "$ROOT" "$SP/out/duchy" "$TAG" "$SP/out/duchy/Counties_draft_$TAG.png" > "$SP/out/duchy/c3_$TAG.log" 2>&1
head -12 "$SP/out/duchy/c3_$TAG.log"; tail -1 "$SP/out/duchy/c3_$TAG.log"
"$PY" -u "$T/c5_arms.py" "$SP/out/duchy" "$TAG" 9 "$SP/out/duchy/${TAG}_arms.png" 2>&1 | head -12
