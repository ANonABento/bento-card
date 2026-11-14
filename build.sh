#!/usr/bin/env bash
# Rebuild the print set from the frozen v63 script chain.
# Needs network on first run (fonts + icons are fetched from GitHub).
set -euo pipefail
cd "$(dirname "$0")"
cp assets/reference.png legacy/reference.png
( cd legacy && PRINT=1 python make_v63.py > /dev/null )
mkdir -p out
cp legacy/print/bento-card-front-600dpi.png legacy/print/bento-card-back-600dpi.png out/
python tools/make_pdf.py > /dev/null   # lossless PDF (the legacy chain's PDF is JPEG-compressed)
cp legacy/v63-preview.jpg out/preview.jpg
cp legacy/v63-tray-zoom.jpg out/qr-zoom.jpg
cp legacy/v63-checks.json out/checks.json
echo "built: out/  (next: pytest -q)"
