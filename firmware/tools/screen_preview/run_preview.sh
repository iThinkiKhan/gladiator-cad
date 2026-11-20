#!/usr/bin/env sh
# Build and run the masthead display preview on the PC (no hardware needed).
# Usage: tools/screen_preview/run_preview.sh <output-folder>
set -e
HERE=$(cd "$(dirname "$0")" && pwd); ROOT="$HERE/../.."
GFX="$ROOT/cam/.pio/libdeps/gladiator_cam/Adafruit GFX Library"   # run "pio run" in cam/ once to fetch it
OUT=${1:-"$HERE/out"}; mkdir -p "$OUT"
PATH="$HOME/.platformio/packages/toolchain-gccmingw32/bin:$PATH"
c++ -std=gnu++14 -O2 -DARDUINO=100 -I"$HERE/shim" -I"$GFX" -I"$ROOT/cam/src" \
  "$HERE/preview.cpp" "$GFX/Adafruit_GFX.cpp" -o "$OUT/preview.exe"
"$OUT/preview.exe" "$OUT"
python "$HERE/make_gifs.py" "$OUT" "$OUT/gif"
