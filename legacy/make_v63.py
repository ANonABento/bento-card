# v63 (Kevin: "shrink her down a bit and move her up so that the qr code is centered vertically? might need to
#  also move a bit right after shrinking, maybe less of her face shown too.")
#  Same 3-layer back as v61/v62 (body / square platter + QR / hands on top). Changes:
#   - whole art scaled by K=0.875 (QR module 32 -> 28 px, so the platter shrinks with her and stays the same
#     size relative to the hands; still 25x25, 1-module gap, sharp square).
#   - vertical: platter/QR centre sits exactly on the card's vertical centre (same line as anonabento.com).
#   - horizontal: art pushed right so its right edge keeps the v61 text gap (RIGHT_GAP px) to anonabento.com.
#  With K=0.875 + centred QR the top trim lands lower on her face than v62 (less face, chin still in).
#  FRONT: unchanged (v59).
# Needs make_v50..58.py + make_v59b.py + make_v61.py + reference.png in the working dir; pip: segno cairosvg scikit-image zxing-cpp.
# Usage: python make_v63.py   (PRINT=1 env also writes print files)
import os, json
K=float(os.environ.get('K','0.875')); RIGHT_GAP=int(os.environ.get('RIGHT_GAP','80')); CHIN_REF=372
_src=open('make_v61.py').read()
def _rep(a,b):
    global _src
    assert a in _src, a
    _src=_src.replace(a,b)
_rep("MOD=32;","MOD=int(round(32*K));")
_rep("S=(CH+4)/(1024-CROP); ink=raw_ink()","S=(CH+4)/(1024-CROP)*K; ink=raw_ink()")
_rep("topoff=int(round(HAND_CY*S-(BLEED+SAFE+2+outer/2)))","topoff=int(round(HAND_CY*S-CH/2))")
_rep("    Lb=place(Lb_s,fx);","    fx=int(tx_left-RIGHT_GAP-c1)\n    Lb=place(Lb_s,fx);")
_rep("silhouette_ref_px=int(sil.sum()))","silhouette_ref_px=int(sil.sum()),scale_vs_v62=K,qr_centre_y_px=(Y0+Y1)/2,card_centre_y_px=CH/2,chin_below_trim_mm=round((CHIN_REF*S-topoff-BLEED)/DPI*25.4,2),trim_top_ref_row=round((topoff+BLEED)/S,1),art_left_px=int(c0+fx),art_right_px=int(c1+fx),left_trim_px=BLEED)")
exec(_src.rsplit("if __name__=='__main__':",1)[0])

if __name__=='__main__':
    fr,bk,lay,chk=build61()
    print(json.dumps(chk,indent=1,default=str))
    if os.environ.get('PRINT'):
        os.makedirs('print',exist_ok=True)
        fr.save('print/bento-card-front-600dpi.png',dpi=(DPI,DPI),optimize=True); bk.save('print/bento-card-back-600dpi.png',dpi=(DPI,DPI),optimize=True)
        fr.save('print/bento-card-print.pdf',save_all=True,append_images=[bk],resolution=DPI,quality=95)
    pair(trim(fr),trim(bk)).save('v63-preview.jpg',quality=86)
    trim(bk).save('v63-back.jpg',quality=88)
    X0,Y0,X1,Y1=lay['box']; z=bk.crop((max(0,X0-200),max(0,Y0-50),min(CW,X1+200),min(CH,Y1+50))); z.save('v63-tray-zoom.jpg',quality=90)
    json.dump(chk,open('v63-checks.json','w'),indent=1,default=str)
