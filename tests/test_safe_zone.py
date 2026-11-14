"""Safe-zone checks: text and icons sit >= 0.08 in (48 px) inside trim. Run after ./build.sh.

Front: every word and icon lives on the light-orange compartments, so their box is the text box.
Back: right of x=1560 the only white ink is the URL (the line art ends near x=1530).
The eye (front) and the body (back) are art and run into the bleed on purpose; they are not checked.
"""
import pathlib
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
W, H = 2250, 1350
BLEED, SAFE = 75, 48
LO_X, LO_Y = BLEED + SAFE, BLEED + SAFE
HI_X, HI_Y = W - BLEED - SAFE - 1, H - BLEED - SAFE - 1
PANEL = (0xF0, 0xAE, 0x82)
URL_X0 = 1560


def _rgb(name):
    return np.asarray(Image.open(OUT / name).convert("RGB")).astype(int)


def _box(m):
    ys, xs = np.nonzero(m)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def front_text_box(a):
    return _box((a == PANEL).all(2))


def back_text_box(a):
    m = a.sum(2) > 700
    m[:, :URL_X0] = False
    return _box(m)


def inside(box):
    x0, y0, x1, y1 = box
    return x0 >= LO_X and y0 >= LO_Y and x1 <= HI_X and y1 <= HI_Y


def test_front_text_in_safe_zone():
    box = front_text_box(_rgb("bento-card-front-600dpi.png"))
    assert inside(box), box


def test_back_url_in_safe_zone():
    box = back_text_box(_rgb("bento-card-back-600dpi.png"))
    assert inside(box), box


def test_shifted_front_fails():
    """Fixture: compartments nudged 80 px toward the bottom trim must be caught."""
    a = np.roll(_rgb("bento-card-front-600dpi.png"), 80, axis=0)
    assert not inside(front_text_box(a))


def test_shifted_back_fails():
    """Fixture: URL nudged 40 px toward the right trim must be caught."""
    a = np.roll(_rgb("bento-card-back-600dpi.png"), 40, axis=1)
    assert not inside(back_text_box(a))
