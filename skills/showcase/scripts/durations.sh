#!/bin/sh
# Rebuild durations.json from clips/*.mp3. Run after every tts.py.
cd "$(dirname "$0")" && for f in clips/*.mp3; do printf '"%s":%s,' "$(basename "$f" .mp3)" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")"; done | sed 's/^/{/; s/,$/}/' > durations.json
