# Bento business card: handoff

Status (Nov 13, 2026): **design locked at v63.** Print files build from this repo and pass 6 checks. Two things still block the order: the domain and a real-phone scan.

## 1. What this is
Kevin Jiang's (ANonABento) business card for MOO Standard (3.5 × 2.0 in).
- **Front, orange:** a bento box of rounded compartments that hold the text. Girl #1's eye (Kevin's own line art, ink lines) peeks in from the right edge.
- **Back, purple:** the same girl in white lines from the chin down. She holds a square platter, and the platter is a white-on-purple QR code to `https://anonabento.com`. `anonabento.com` sits on the right on one line, centred vertically.
- **The idea:** the eye on the front plus the body on the back make one character. Flip the card to see the rest of her.

## 2. Build
```bash
pip install -r requirements.txt
./build.sh      # ~10 s; fetches fonts/icons from GitHub on first run
pytest -q       # 6 checks, incl. a pixel-exact golden test against v63
```
This writes to `out/`:
| file | what |
|---|---|
| `bento-card-front-600dpi.png` / `bento-card-back-600dpi.png` | 2250 × 1350 px, 600 dpi, RGB, 1/8 in bleed on every side. Upload these. |
| `bento-card-print.pdf` | 2 pages (front, back), 3.75 × 2.25 in each. Lossless: the PNG data is embedded as-is. |
| `preview.jpg` | front and back side by side, trimmed |
| `qr-zoom.jpg` | close-up of the back platter and QR |
| `checks.json` | geometry and scan metrics |

Verified on Nov 13 in a clean sandbox: two fresh builds from this repo were pixel-identical, and all 6 tests passed both times.

## 3. Locked spec
**Size.** Trim is 3.5 × 2.0 in. The canvas is 3.75 × 2.25 in (2250 × 1350 px at 600 dpi), with `BLEED = 75 px` per side. The safe area is 0.08 in (48 px) inside the trim, so 3.34 × 1.84 in.

**Colours.**
| name | hex | use |
|---|---|---|
| orange | `#e8823f` | front background |
| light orange | `#f0ae82` | front compartments (solid fill) |
| purple | `#a78bfa` | back background and platter fill |
| ink | `#0e0b0a` | front text, icons, eye lines |
| white | `#ffffff` | back line art, QR modules, URL |

**Type.**
- Name: Archivo Semi-Expanded. `KEVIN` / `JIANG` sit on two lines. Each line's width axis is tuned so its ink fills the block exactly (about 25.9 pt).
- Everything else: Instrument Sans. The contact lines are 8.4 pt, the smallest text on the card (the floor is 8 pt).

**Front text, exactly:**
- `KEVIN JIANG`
- `Physical AI Engineer` and `UWaterloo Comp Eng '29`
- contact bubble with a small tail:
  - mail icon + `kevin@anonabento.com`
  - GitHub icon + `github.com/ANonABento`
  - LinkedIn icon + `linkedin.com/in/ANonABento`
- `ANonABento`, set vertically (reads top to bottom)

**Front details.**
- The icons have equal ink height (59 px), and each one is centred on its line's cap height.
- The mail icon is Lucide mail, with its stroke matched to the text stem width.
- Block padding is 44 px, measured to the ink, not to the bounding box.
- The eye is the reference line art scaled 5.3×, and it runs into the bleed. There is no scalloped border.

**Back, built in 3 layers** (`legacy/make_v61.py`):
1. **Body:** the reference art with the old drawn tray erased.
2. **Platter:** a sharp-cornered square, 1.293 in, purple fill with a 10 px white rim. It holds the QR: ECC-M, 25 × 25 modules, 28 px per module (1.185 mm), 1.167 in across, with a gap of exactly 1 module on all four sides.
3. **Hands:** on top. The fingers cover 21 of 625 modules (3.4%). They touch no finder, timing, alignment or format modules.

**Back placement.**
- The art is scaled 0.875× from v62.
- The QR centre sits on the card's vertical centre (y = 675 px).
- The art's right edge stays 80 px clear of the URL text. Her chin is 3.25 mm below the top trim.

**Scan results (simulated).** ZXing decodes the QR in 24 of 24 synthetic phone shots, and at downscales to 350 px wide. OpenCV's detector reads only 3 of 24 because it handles inverted (light-on-dark) codes badly. Real phones have **not** been tested yet.

## 4. How the code is laid out (read this before you edit)
`legacy/` is the frozen chain that actually renders the card. **Each script reads its parent's source, patches strings in it, and runs it with `exec`:**
```
make_v63 → v61 → v59b → v58 → v57 → v56 → v55 → v54 → v53 → v50
                                       v56, v57, v58, v59b, v61 also exec make_v52 (front layout)
```
- `make_v50`: constants (`DPI, BLEED, CW, CH, SAFE`, `PURPLE`, `URL`, QR matrix via segno), the reference-art loader, and the line renderer.
- `make_v52`: front layout (`BOXES`, `FONTS`, `ORANGE/DARK/INK`, `EYE` anchor on reference.png), `front()`, `back()`, `guides()`.
- `make_v53`–`v56`: front polish (fonts, icon sizing, mail icon choice, ink-measured padding).
- `make_v57`/`v58`: the first print sets; tray cleanup; `trim()`, `pair()`.
- `make_v59b`: the eye scale (`EYE_S` = 5.3).
- `make_v61`: the 3-layer back (`SQ_REF`, `HAND_CY`, `HANDS`, `RIM_BANDS`, `MOD`, `GAP`, `HALO`, `back61()`, `build61()`).
- `make_v63`: scale `K` = 0.875, `RIGHT_GAP` = 80, QR centred vertically. You can override both with env vars `K` and `RIGHT_GAP`.

The patches are plain-string `replace` calls guarded by `assert`. If you edit a parent, a child's patch can stop matching and the build will fail on that assert. That is the main reason Task 1 below exists.

Coordinates named `*_REF`, `EYE`, `HANDS` and so on are in **reference.png pixels**. Everything else is in **card pixels at 600 dpi**.

## 5. Assets and licences
- `assets/reference.png`: Kevin's own line art. It is the source for both sides. **Do not regenerate it with an image model.** Five tries (v45–v49) failed to reproduce the face. Use this file.
- Fonts (Archivo, Instrument Sans; OFL 1.1) and icons (Lucide mail, ISC; Font Awesome Free 6 brands, CC BY 4.0) are downloaded from upstream GitHub `main` at build time. See `CREDITS.txt`.
- `docs/character-bible.md`: the mascot spec. Girl #1: tsundere, petite, flowing twin-tails, no mouth, robot earpieces, chunky robot arms, Victorian apron. Girl #2 (bob) is not designed yet.
- `docs/generator-prompts-v49.md`: the old image-model prompts, kept for reference only.

## 6. Lessons from 63 versions
- Measure padding and alignment by **ink**, never by font bounding boxes.
- Kevin reviews by eye at 100%. Every change ships with `preview.jpg` plus a zoom of the area that changed.
- The QR rules: integer-pixel modules; a 1-module gap to the platter rim; fingers must never touch a finder pattern; run the decoder after every change.
- Keep front and back the same art at the same line weight. Scale the platter together with her so the hands still fit.
- The printed URL and the QR both depend on `anonabento.com`, and the email uses it too.

## 7. Open items and risks
| # | item | blocks order? |
|---|---|---|
| A | **`anonabento.com` is not bought.** The QR, the URL and the email are dead until it is. | yes |
| B | **No real-phone scan yet.** Inverted QR + purple flood. Print `out/bento-card-back-600dpi.png` at 100% and test it with the iPhone camera and the Android camera. | yes |
| C | **Bleed spec mismatch.** The files use 1/8 in bleed (3.75 × 2.25 in). An earlier note from MOO's size page said 3.66 × 2.16 in. Check MOO's current template; if needed, crop 27 px per side for the 3.66 × 2.16 in canvas (0.08 in bleed = 48 px per side, vs 75 px now). | maybe |
| D | **Fonts and icons are pulled from upstream `main`.** An upstream change could change pixels; the golden test will catch it. | no |
| E | **Stock:** matte vs soft-touch for fine white lines on purple. Lines are kept at least 0.5 pt. | no |


## 8. Next tasks for the incoming agent (in order)
1. **Flatten the exec chain.** Write `card.py`, one readable script with the same constants and steps. It must make `out/` pixel-identical to the golden hashes (`pytest -q` stays green). After that, move `legacy/` to `archive/` and point `build.sh` at `card.py`. Don't change the design during this task.
2. **Vendor fonts and icons.** Copy them into `assets/fonts/` and `assets/icons/` at pinned commits so the build works offline (fixes risk D). Update `CREDITS.txt` with the commit SHAs.
3. **Bleed check (risk C).** Get MOO's current Standard template and confirm whether the canvas is 3.75 × 2.25 or 3.66 × 2.16 in. If it's the second, add a `--moo` crop step. Don't touch the art.
4. **Real-phone scan (risk B).** Kevin prints the back at 100% on paper. Log the iPhone and Android camera results in `docs/scan-log.md`. If either fails, try these in order: fingers off the QR entirely, then a thicker rim, then ECC-Q. Re-run the checks after each one.
5. **After the domain is live (risk A):** confirm that `https://anonabento.com` resolves before ordering. If the domain changes, it's one constant (`URL` in `make_v50`). The printed URL text and the email would change too.
6. **Later:** design Girl #2 (bob hair) in `docs/character-bible.md` style. Fill in the ComfyUI mascot pipeline only if Kevin asks. Look into a plastic/metal test card.

**Working rules.** Kevin approves every visual change by eye. Ship `preview.jpg` plus a zoom of whatever changed, and keep the earlier version for comparison. Never regenerate the line art.
