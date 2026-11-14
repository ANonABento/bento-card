"""Print-file checks. Run after ./build.sh:  pytest -q"""
import hashlib, json, pathlib
import numpy as np
from PIL import Image
import zxingcpp

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DPI = 600
CANVAS = (2250, 1350)          # 3.75 x 2.25 in = 3.5 x 2.0 trim + 1/8 in bleed each side
BLEED = 75                     # px
SAFE = 0.08 * DPI              # px inside the trim (MOO safe area 3.34 x 1.84 in)
URL = "https://anonabento.com"

def img(name):
    return Image.open(OUT / name)

def test_canvas_size_and_dpi():
    for n in ("bento-card-front-600dpi.png", "bento-card-back-600dpi.png"):
        im = img(n)
        assert im.size == CANVAS, n
        assert round(im.info["dpi"][0]) == DPI, n

def test_back_qr_decodes_full_and_small():
    im = img("bento-card-back-600dpi.png").convert("L")
    for w in (2250, 800, 350):
        small = im.resize((w, round(w * CANVAS[1] / CANVAS[0])), Image.LANCZOS)
        texts = [r.text for r in zxingcpp.read_barcodes(small)]
        assert URL in texts, f"QR not decoded at {w}px wide"

def test_qr_inside_safe_area():
    im = img("bento-card-back-600dpi.png").convert("L")
    r = [x for x in zxingcpp.read_barcodes(im) if x.text == URL][0]
    p = r.position
    xs = [p.top_left.x, p.top_right.x, p.bottom_left.x, p.bottom_right.x]
    ys = [p.top_left.y, p.top_right.y, p.bottom_left.y, p.bottom_right.y]
    lo_x, lo_y = BLEED + SAFE, BLEED + SAFE
    hi_x, hi_y = CANVAS[0] - BLEED - SAFE, CANVAS[1] - BLEED - SAFE
    assert min(xs) >= lo_x and max(xs) <= hi_x and min(ys) >= lo_y and max(ys) <= hi_y

def test_qr_vertically_centred():
    c = json.loads((OUT / "checks.json").read_text())["back"]
    assert abs(c["qr_centre_y_px"] - CANVAS[1] / 2) <= 1
    assert c["finder_modules_hit"] == 0 and c["gap_modules"] == {"left": 1.0, "right": 1.0, "top": 1.0, "bottom": 1.0}

def test_brand_colours_present():
    f = np.asarray(img("bento-card-front-600dpi.png").convert("RGB")).reshape(-1, 3)
    b = np.asarray(img("bento-card-back-600dpi.png").convert("RGB")).reshape(-1, 3)
    has = lambda a, hexs: (a == np.array([int(hexs[i:i+2], 16) for i in (1, 3, 5)])).all(1).mean()
    assert has(f, "#e8823f") > 0.3, "front orange"
    assert has(b, "#a78bfa") > 0.3, "back purple"

def test_matches_golden():
    """Fails on ANY pixel change. If the change is intended, update golden/sha256.json."""
    gold = json.loads((ROOT / "golden" / "sha256.json").read_text())
    for n, h in gold.items():
        px = np.asarray(img(n).convert("RGB")).tobytes()
        assert hashlib.sha256(px).hexdigest() == h, f"{n} pixels changed vs golden v63"
