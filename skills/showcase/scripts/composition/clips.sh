#!/usr/bin/env bash
# Encodes each folder of PNG frames in frames/<name>/0000.png... into
# assets/<name>.webm: VP9 with alpha, so the clip floats on the composition's
# background. Frames come from frames.mjs (a web app) or from the app's own
# drawing code (a native app). 30 fps.
#   ./clips.sh            every folder
#   ./clips.sh hero,chat  only these
set -euo pipefail
mkdir -p assets
for dir in frames/*/; do
  name="$(basename "$dir")"
  if [ -n "${1:-}" ] && [[ ",$1," != *",$name,"* ]]; then continue; fi
  ffmpeg -v error -y -framerate 30 -i "$dir/%04d.png" \
    -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 6M -auto-alt-ref 0 -row-mt 1 "assets/$name.webm"
  echo "assets/$name.webm"
done
