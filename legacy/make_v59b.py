# v59 (Kevin: "scale the front a bit bigger" + "QR should take up the entire tray like the third one in #69,
#      padding = one QR module")
#  FRONT: v58 front, peeking eye line art scaled up (S_F 4.6 -> EYE_S, eye centre stays at EYE_AT). Blocks/text unchanged.
#  BACK : v58 back with fingertips KEPT. QR (ECC-H, so it survives the fingertips sitting on top of its side edges)
#         fills the tray interior with a 1-module gap to the rim line, integer-pixel modules. Fingers are drawn in front:
#         a purple silhouette (plus a small halo) masks the QR under each fingertip, then the white line art goes on top.
# Needs make_v50..58.py; pip: segno cairosvg scikit-image zxing-cpp. PRINT=1 env also writes print files + reference.png in the working dir.  Usage: python make_v59.py [eye_scale]   (default 5.3)
exec(open('make_v58.py').read().rsplit("if __name__=='__main__':",1)[0])
import json, segno
EYE_S=5.3
ECC='m'   # v59 test: ECC-M (25x25, 1.27 mm modules) beat ECC-H (29x29, 1.10 mm) on simulated phone scans with fingers over
QH=np.array(segno.make(URL,error=ECC,micro=False,boost_error=False).matrix,dtype=np.uint8); NH=QH.shape[0]

def front59(s):
    global S_F
    S_F=s; _C.clear(); base_layers(); _C['shape'][:]=True          # no scalloped band (as v58)
    return front56('C')

def finger_sil(ink):
    """filled fingertip silhouettes inside the tray interior, reference.png px"""
    H,W=ink.shape; x0,y0,x1,y1=TRAY_IN; f=np.zeros((H,W),np.uint8); f[y0:y1+1,x0:x1+1]=ink[y0:y1+1,x0:x1+1]
    f=cv2.morphologyEx(f,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
    sil=np.zeros_like(f); cxm=(x0+x1)//2
    for y in range(y0,y1+1):
        l=np.nonzero(f[y,x0:cxm])[0]; r=np.nonzero(f[y,cxm:x1+1])[0]
        if l.size: sil[y,x0:x0+l.max()+1]=1
        if r.size: sil[y,cxm+r.min():x1+1]=1
    return sil

def back59(ns,GAP_MOD=1,CROP=420,TEXT_GAP=80,HALO=10):
    S=(CH+4)/(1024-CROP); L=ns['lines_at'](S); top=int(round(CROP*S)); L=L[top:top+CH]
    cols=np.nonzero((L>0.5).any(0))[0]; c0,c1=cols.min(),cols.max(); fnt=ns['fnt']
    tw=fnt.getlength('anonabento.com'); tx_left=CW-BLEED-SAFE-tw; fx=int(min(BLEED+SAFE+10-c0, tx_left-TEXT_GAP-c1))
    lay=np.zeros((CH,CW),np.float32); xs0=max(0,fx); xs1=min(CW,fx+L.shape[1]); lay[:,xs0:xs1]=L[:,xs0-fx:xs1-fx]
    # silhouette -> card px with the same transform as the line art
    sil=finger_sil(ns['ink']); sl=cv2.resize(sil.astype(np.float32),None,fx=S,fy=S,interpolation=cv2.INTER_LINEAR)[top:top+CH]>0.3
    silc=np.zeros((CH,CW),bool); silc[:,xs0:xs1]=sl[:,xs0-fx:xs1-fx]
    # measure the real (rendered) free interior of the rim: scan out from the tray centre on rows/cols clear of fingers
    x0,y0,x1,y1=TRAY_IN; cx=int(((x0+x1)/2)*S+fx); cy=int(((y0+y1)/2)*S-top); ink_c=lay>0.25
    def run(seq): i=np.argmax(seq); return int(i) if seq[i] else len(seq)
    rows=[int((y0+(y1-y0)*f)*S-top) for f in (.15,.25,.75,.85)]
    lft=min(run(ink_c[r,:cx][::-1]) for r in rows); rgt=min(run(ink_c[r,cx:]) for r in rows)
    colsm=[int((x0+(x1-x0)*f)*S+fx) for f in (.4,.5,.6)]
    up=min(run(ink_c[:cy,c][::-1]) for c in colsm); dn=min(run(ink_c[cy:,c]) for c in colsm)
    fl,fr_,ft,fb=cx-lft+1,cx+rgt-1,cy-up+1,cy+dn-1                     # free box (first clear px each side)
    mod=int(min(fr_-fl+1,fb-ft+1)//(NH+2*GAP_MOD)); qs=mod*NH
    qx=int(round((fl+fr_+1)/2-qs/2)); qy=int(round((ft+fb+1)/2-qs/2))
    img=np.ones((CH,CW,3))*PURPLE
    q=np.kron(QH,np.ones((mod,mod))).astype(np.float32); full=np.zeros((CH,CW),np.float32); full[qy:qy+qs,qx:qx+qs]=q
    img=img*(1-full[...,None])+WHITE*full[...,None]
    cover=cv2.dilate(silc.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*HALO+1,2*HALO+1)))>0
    img[cover]=PURPLE                                                   # fingertips sit in front of the code
    img=img*(1-lay[...,None])+WHITE*lay[...,None]
    covered=finder=0
    for r in range(NH):
        for c in range(NH):
            if cover[int(qy+(r+.5)*mod),int(qx+(c+.5)*mod)]:
                covered+=1; finder+=((r<8 and c<8) or (r<8 and c>=NH-8) or (r>=NH-8 and c<8))
    im=Image.fromarray(np.clip(img,0,255).astype(np.uint8)); ImageDraw.Draw(im).text((tx_left,CH/2),'anonabento.com',font=fnt,fill=(255,255,255),anchor='lm')
    S0,S1,T0,T1=BLEED+SAFE,CW-BLEED-SAFE,BLEED+SAFE,CH-BLEED-SAFE
    gaps=dict(left=round((qx-fl)/mod,2),right=round((fr_+1-qx-qs)/mod,2),top=round((qy-ft)/mod,2),bottom=round((fb+1-qy-qs)/mod,2))
    return im,dict(ecc=ECC.upper(),modules=NH,qr_in=round(qs/DPI,3),qr_px=qs,module_px=mod,module_mm=round(mod/DPI*25.4,3),qr_xy=(qx,qy),
        free_box=(fl,ft,fr_,fb),gap_to_rim_modules=gaps,modules_under_fingers=f'{covered}/{NH*NH} ({covered/NH/NH*100:.1f}%; ECC-M repairs ~15%)',
        finder_modules_hit=finder,qr_in_safe=bool(qx>=S0 and qy>=T0 and qx+qs<=S1 and qy+qs<=T1),
        text_clear=bool(not (lay[CH//2-60:CH//2+60,int(tx_left)-40:S1+10]>0.2).any()))

def scan_zx(im,n=16):
    """same 'phone shot' simulation as v50 scan(), decoded with ZXing (closer to real phone scanners) and OpenCV"""
    import zxingcpp
    g0=255-cv2.cvtColor(np.array(im),cv2.COLOR_RGB2GRAY); oc=zz=0
    for seed in range(n):
        rg=np.random.default_rng(seed);sc_=rg.uniform(.25,.45);gg=cv2.resize(g0,None,fx=sc_,fy=sc_,interpolation=cv2.INTER_AREA);hh,ww=gg.shape
        j=rg.uniform(0,.05,8)
        M=cv2.getPerspectiveTransform(np.float32([[0,0],[ww,0],[ww,hh],[0,hh]]),np.float32([[ww*j[0],hh*j[1]],[ww*(1-j[2]),hh*j[3]],[ww*(1-j[4]),hh*(1-j[5])],[ww*j[6],hh*(1-j[7])]]))
        q=cv2.GaussianBlur(cv2.warpPerspective(gg,M,(ww,hh),borderMode=cv2.BORDER_REPLICATE),(0,0),rg.uniform(.6,1.6))
        q=np.clip(q*rg.uniform(.7,1)+rg.normal(0,8,q.shape),0,255).astype(np.uint8)
        oc+=det.detectAndDecode(q)[0]==URL; zz+=any(b.text==URL for b in zxingcpp.read_barcodes(q))
    return {'zxing':f'{zz}/{n}','opencv':f'{oc}/{n}'}

def build59(eye_s=EYE_S):
    fr,finfo=front59(eye_s)
    ns={}; exec(open('make_v52.py').read(),ns); ns['ink']=clean_tray(ns['ink'],tuck=False)
    bk,binfo=back59(ns)
    S0,S1=BLEED+SAFE,CW-BLEED-SAFE; T0,T1=BLEED+SAFE,CH-BLEED-SAFE
    chk={'eye_scale':eye_s,'eye_vs_v58':round(eye_s/4.6,3),'back':binfo,'qr_scan_opencv_v50':ns['scan'](bk),'phone_shots16':scan_zx(bk)}
    import zxingcpp
    dec={}
    for w in (2250,1200,800,500,350):
        g=np.array(bk.convert('L').resize((w,int(w*CH/CW)),Image.LANCZOS)); dec[w]=[b.text for b in zxingcpp.read_barcodes(255-g)]
    chk['qr_downscaled_zxing_widthpx']=dec
    chk['front_boxes_in_safe']={k:bool(a>=S0 and c<=S1 and b>=T0 and d<=T1) for k,(a,b,c,d) in BOXES.items()}
    chk['tail_tip_in_safe']=bool(TIP[0]<=S1 and TIP[1]>=T0); chk['pads_px']=pads(); chk['front']=finfo
    chk['contact_font_pt']=round(FC/DPI*72,2); chk['min_ok']=chk['contact_font_pt']>=8
    return fr,bk,chk

if __name__=='__main__':
    import sys; es=float(sys.argv[1]) if len(sys.argv)>1 else EYE_S
    os.makedirs('print',exist_ok=True)
    # front scale options (trimmed), for picking
    opts=[(s,trim(front59(s)[0])) for s in (4.6,5.3,6.0)]
    w=700; h=round(w*opts[0][1].height/opts[0][1].width); fl=F(30,600)
    sh=Image.new('RGB',(3*w+80,h+80),(28,26,25)); d=ImageDraw.Draw(sh)
    for i,(s,im) in enumerate(opts):
        sh.paste(im.resize((w,h),Image.LANCZOS),(20+i*(w+20),60)); d.text((20+i*(w+20),14),f'eye x{s/4.6:.2f}'+(' (v58)' if s==4.6 else ''),font=fl,fill=(242,236,226))
    sh.save('v59-front-options.jpg',quality=86)
    fr,bk,chk=build59(es); print(json.dumps(chk,indent=1,default=str))
    if os.environ.get('PRINT'):
      fr.save('print/bento-card-front-600dpi.png',dpi=(DPI,DPI),optimize=True); bk.save('print/bento-card-back-600dpi.png',dpi=(DPI,DPI),optimize=True)
      fr.save('print/bento-card-print.pdf',save_all=True,append_images=[bk],resolution=DPI,quality=95)
    pair(trim(fr),trim(bk)).save('v59-preview.jpg',quality=88)
    pair(guides(fr),guides(bk)).save('v59-guides.jpg',quality=84)
    qx,qy=chk['back']['qr_xy']; qs=chk['back']['qr_px']
    bk.crop((qx-260,qy-140,qx+qs+260,qy+qs+140)).save('v59-tray-zoom.jpg',quality=90)
    json.dump(chk,open('v59-checks.json','w'),indent=1,default=str)
