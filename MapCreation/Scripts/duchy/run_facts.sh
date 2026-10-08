#!/usr/bin/env bash
# Every figure the document states, measured from the pictures now in the repo and the runs' data.
SP="${MAP_WORK:?set MAP_WORK to the working folder: it held out/ and the staging folders}"
T="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WROOT="${MAP_REPO:?set MAP_REPO to the repository}"
PY="${MAP_PYTHON:-python}"
OUT="$SP/out/duchy2"; ROADS="$SP/out/roads2"; FACTS="$SP/out/facts2"
mkdir -p "$FACTS"
cd "$SP" || exit 1
"$PY" -u "$T/f1_facts.py" "$WROOT" "$SP/out/water" "$OUT" "$ROADS" "$FACTS" > "$FACTS/f1.log" 2>&1; tail -1 "$FACTS/f1.log"
"$PY" -u "$T/f2_more.py" "$WROOT" "$SP/out/water" "$OUT" "$ROADS" "$FACTS" > "$FACTS/f2.log" 2>&1; tail -1 "$FACTS/f2.log"
"$PY" -u "$T/r6_judge.py" "$ROADS" "$WROOT/MapCreation/Roads.png" > "$FACTS/r6.log" 2>&1; tail -1 "$FACTS/r6.log"
"$PY" -u "$T/v4_changes.py" "$SP/out/duchy" "$OUT" "$SP/out/roads" "$ROADS" "$SP/out/oldpics" "$WROOT/MapCreation" > "$FACTS/changes.log" 2>&1; tail -1 "$FACTS/changes.log"
"$PY" -u "$T/kl2_lengths.py" "$OUT" > "$FACTS/lengths.log" 2>&1; cat "$FACTS/lengths.log"
echo "facts done"
