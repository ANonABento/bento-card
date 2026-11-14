# v57 = FINAL print files. Front = v56 with mail icon C (Lucide mail, ISC; stroke = text stem).
# Back = v52 back, crop 420. Writes 600 dpi PNGs with 1/8" bleed, a 2-page PDF, a guides preview, and checks.
# Needs make_v50..v56.py + reference.png in the working dir.
exec(open('make_v56.py').read().rsplit("if __name__=='__main__':",1)[0])
import json
def ink_bbox(im,bg_test):
    a=np.array(im).astype(int); m=bg_test(a); ys,xs=np.nonzero(m); return xs.min(),ys.min(),xs.max(),ys.max()
if __name__=='__main__':
    fr,finfo=front56('C')
    ns={}; exec(open('make_v52.py').read(),ns); bk,binfo=ns['back'](420)
    S0,S1=BLEED+SAFE,CW-BLEED-SAFE; T0,T1=BLEED+SAFE,CH-BLEED-SAFE
    chk={}
    # QR: decode full-res, and at phone-ish downscales
    chk['qr_full']=ns['scan'](bk)
    det=cv2.QRCodeDetector(); dec={}
    for w in (2250,1200,800,500):
        g=np.array(bk.convert('L').resize((w,int(w*CH/CW)),Image.LANCZOS))
        t,_,_=det.detectAndDecode(255-g); dec[w]=t     # white-on-purple -> invert for detector
    chk['qr_downscaled_inverted']=dec; chk['back']=binfo
    # front: every text/icon block box and the speech tail inside the safe area
    chk['front_boxes_in_safe']={k:bool(a>=S0 and c<=S1 and b>=T0 and d<=T1) for k,(a,b,c,d) in BOXES.items()}
    chk['tail_tip_in_safe']=bool(TIP[0]<=S1 and TIP[1]>=T0); chk['tail_tip']=TIP
    chk['pads_px']=pads(); chk['front']=finfo
    # smallest text: contact line cap height -> pt
    chk['contact_font_pt']=round(FC/DPI*72,2)
    chk['min_ok']=chk['contact_font_pt']>=8
    print(json.dumps(chk,indent=1,default=str))
    fr.save('bento-card-front-600dpi.png',dpi=(DPI,DPI)); bk.save('bento-card-back-600dpi.png',dpi=(DPI,DPI))
    fr.save('bento-card-print.pdf',save_all=True,append_images=[bk],resolution=DPI,quality=95)
    # preview with trim (red) + safe (green) guides
    def gd(im):
        p=im.copy(); dd=ImageDraw.Draw(p); dd.rectangle([BLEED,BLEED,CW-BLEED,CH-BLEED],outline=(255,60,60),width=4)
        dd.rectangle([S0,T0,S1,T1],outline=(60,230,60),width=3); return p
    w,h=CW//2,CH//2; sh=Image.new('RGB',(2*w+30,2*h+30),(28,26,25))
    for i,im in enumerate((fr,bk)):
        sh.paste(im.resize((w,h),Image.LANCZOS),(i*(w+30),0)); sh.paste(gd(im).resize((w,h),Image.LANCZOS),(i*(w+30),h+30))
    sh.save('v57-preview.jpg',quality=88)
    json.dump(chk,open('v57-checks.json','w'),indent=1,default=str)
