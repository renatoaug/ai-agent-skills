#!/usr/bin/env bash
# Renders a HyperFrames output down to something GitHub takes (10 MB at most):
# same 1080p and length, x264 crf 26 (dark, mostly still frames compress well),
# with its first second as cover art, which Finder and players use as the thumbnail.
#   ./export.sh render.mp4 ~/Downloads/name.mp4
set -euo pipefail
in="$1"; out="$2"; cover="$(mktemp -t cover).jpg"
ffmpeg -v error -y -ss 0.3 -i "$in" -frames:v 1 "$cover"
ffmpeg -v error -y -i "$in" -i "$cover" -map 0:v -map 0:a? -map 1 \
  -c:v:0 libx264 -preset slow -crf 26 -pix_fmt yuv420p -c:v:1 copy -disposition:v:1 attached_pic \
  -c:a aac -b:a 128k -movflags +faststart "$out"
ls -la "$out"
