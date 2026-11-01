#!/bin/bash
# tools/mux.sh render_dir out.mp4 — склейка сегментов + AAC
set -e
D=$1; OUT=$2
: > $D/list.txt; for k in 0 1 2 3; do echo "file '$D/seg$k.mp4'" >> $D/list.txt; done
ffmpeg -loglevel error -y -f concat -safe 0 -i $D/list.txt -i "$(dirname $0)/../audio/mix.wav" \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$OUT"
