# bento-card

Print files for Kevin Jiang's (ANonABento) MOO business card. The front is an orange bento box with the eye; the back is a purple maid holding the QR code.

```bash
pip install -r requirements.txt
./build.sh     # writes out/ (front/back PNG at 600 dpi + 2-page PDF)
pytest -q      # 6 checks incl. golden pixel hashes
```

Start with **HANDOFF.md**. It has the locked spec, how the code is laid out, open risks, and the next tasks.
