#!/usr/bin/env bash
# Try settings on a sample of duchies. Usage: run_trials.sh <duchies> <tag ease near_enough> ...
SP="${MAP_WORK:?set MAP_WORK to the working folder: it held out/ and the staging folders}"
T="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DUCHIES="$1"
shift
while [ "$#" -ge 3 ]; do
    "${MAP_PYTHON:-python}" -u "$T/c1_counties.py" "$SP/out/duchy" "$1" "$2" "$3" 0 "$DUCHIES" > "$SP/out/duchy/c1_$1.log" 2>&1
    grep "SUMMARY\|Error\|error" "$SP/out/duchy/c1_$1.log"
    shift 3
done
