"""Lossless 2-page print PDF (front, back) from the 600 dpi PNGs.
The legacy chain writes its PDF with JPEG compression; this embeds the PNG data as-is (Flate),
pixel-identical to the PNGs, page size 3.75 x 2.25 in."""
import pathlib
import img2pdf

out = pathlib.Path(__file__).resolve().parents[1] / "out"
pages = [str(out / "bento-card-front-600dpi.png"), str(out / "bento-card-back-600dpi.png")]
layout = img2pdf.get_fixed_dpi_layout_fun((600, 600))
(out / "bento-card-print.pdf").write_bytes(img2pdf.convert(pages, layout_fun=layout))
print("wrote", out / "bento-card-print.pdf")
