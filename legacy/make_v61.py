# v61 (Kevin: "still not square" -> rebuild the back in 3 layers)
#  L1 BODY  : the reference line art with the whole old tray removed (everything inside the platter square goes).
#  L2 PLATTER: a new, truly square, sharp-cornered platter drawn in card pixels: purple fill, white rim (same stroke
#              as the line art), QR (ECC-M, 25x25, integer-px modules) filling it with EXACTLY a 1-module gap on all
#              four sides. Square is centred on the hands so the fingers land between the finder patterns.
#  L3 HANDS : the hands cut out of the reference (old rim lines erased from them, finger outlines re-bridged),
#              with a filled finger silhouette so they sit IN FRONT of the platter rim and the QR.
#  The art is moved down a little on the card so the whole platter sits inside the safe area.
#  FRONT: unchanged (v59, eye x1.15).
# Needs make_v50..58.py + make_v59b.py + reference.png in the working dir; pip: segno cairosvg scikit-image zxing-cpp.
# Usage: python make_v61.py   (PRINT=1 env also writes print files)
exec(open('make_v59b.py').read().rsplit("if __name__=='__main__':",1)[0])
import json, os
from skimage.morphology import skeletonize

SQ_REF=(319,705)            # old tray outer rim x-span in reference px (rims at 321/327/336 and 687/696/703)
HAND_CY=639                 # vertical centre of the fingers (reference px, fingers span ~598-680)
HANDS=[(268,374,584,704),(642,762,584,704)]          # x0,x1,y0,y1 hand boxes (reference px)
RIM_BANDS=[(319,323),(325,329),(334,338),(685,689),(694,698),(700,705)]
MOD=32; GAP=1; HALO=8

def raw_ink():
    g=cv2.imread('reference.png',0); k=(g<150).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(k,8); keep=np.zeros(n,bool); keep[1:]=st[1:,4]>=12
    return keep[lab].astype(np.uint8)

def render_lines(k,S):                     # same line renderer as v50 lines_at, for any ink layer
    m=cv2.resize(k.astype(np.float32),None,fx=S,fy=S,interpolation=cv2.INTER_LINEAR)>0.3
    sk=skeletonize(m).astype(np.uint8)
    out=(m|cv2.dilate(sk,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(MINPX,MINPX))).astype(bool)).astype(np.float32)
    big=cv2.resize(out,None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC)
    big=np.clip((cv2.GaussianBlur(big,(0,0),3.0)-0.5)*4+0.5,0,1)
    return cv2.resize(big,(out.shape[1],out.shape[0]),interpolation=cv2.INTER_AREA)

def hands_layer(ink):
    """hand line art only: old rim bands erased inside the hand boxes, lines that crossed a band bridged back"""
    H=np.zeros_like(ink)
    for x0,x1,y0,y1 in HANDS: H[y0:y1+1,x0:x1+1]=ink[y0:y1+1,x0:x1+1]
    out=H.copy()
    for x0,x1,y0,y1 in HANDS:
        for b0,b1 in RIM_BANDS:
            if b0<x0 or b1>x1: continue
            out[y0:y1+1,b0:b1+1]=0
            for y in range(y0,y1+1):
                lft=H[y-1:y+2,b0-3:b0].any(); rgt=H[y-1:y+2,b1+1:b1+4].any()
                if lft and rgt and H[y,b0:b1+1].sum()>(b1-b0+1)//2: out[y,b0:b1+1]=1   # a finger line crossed here
    return out

def finger_silhouette(hk,box):
    """filled hand shape inside the platter: everything not reachable from the platter centre"""
    x0,y0,x1,y1=box; Hh,W=hk.shape
    wall=cv2.dilate(hk,np.ones((3,3),np.uint8)).astype(bool)
    free=np.zeros((Hh,W),np.uint8); free[y0:y1+1,x0:x1+1]=1; free[wall]=0
    ff=free.copy(); msk=np.zeros((Hh+2,W+2),np.uint8)
    cv2.floodFill(ff,msk,((x0+x1)//2,HAND_CY),2,flags=4)
    sil=np.zeros((Hh,W),bool); sil[y0:y1+1,x0:x1+1]=(ff[y0:y1+1,x0:x1+1]!=2)
    hb=np.zeros_like(sil)
    for a,b,c,d in HANDS: hb[c:d+1,a:b+1]=True
    return sil&hb

def back61(fnt,CROP=420,TEXT_GAP=80):
    S=(CH+4)/(1024-CROP); ink=raw_ink()
    # card geometry of the platter
    w=None
    Lraw=render_lines(ink,S); r=int(520*S); xs=int(321*S)                    # measure the art's line weight on the old rim
    run=Lraw[r,xs-15:xs+15]>0.5; w=int(run.sum())
    inner=(NH+2*GAP)*MOD; outer=inner+2*w
    topoff=int(round(HAND_CY*S-(BLEED+SAFE+2+outer/2)))                     # platter top edge just inside the safe line
    # layers in reference px
    sx0,sx1=SQ_REF; half=outer/2/S; sy0,sy1=int(HAND_CY-half)-1,int(HAND_CY+half)+1
    body=ink.copy()
    hk=hands_layer(ink)
    sil=finger_silhouette(hk,(int((sx0+sx1)/2-half)-1,sy0,int(np.ceil((sx0+sx1)/2+half))+1,sy1))   # whole outer square incl. the rim
    def place(a,fx):                                                          # scaled reference -> card canvas
        a=a[topoff:topoff+CH]; o=np.zeros((CH,CW),np.float32); xs0=max(0,fx); xs1=min(CW,fx+a.shape[1]); o[:a.shape[0],xs0:xs1]=a[:,xs0-fx:xs1-fx]; return o
    Lb_s=render_lines(body,S); cols=np.nonzero((Lb_s[topoff:topoff+CH]>0.5).any(0))[0]; c0,c1=cols.min(),cols.max()
    tw=fnt.getlength('anonabento.com'); tx_left=CW-BLEED-SAFE-tw; fx=int(min(BLEED+SAFE+10-c0, tx_left-TEXT_GAP-c1))
    fx=max(fx,int(np.ceil(BLEED+SAFE+2+outer/2-(SQ_REF[0]+SQ_REF[1])/2*S)))     # v61: whole platter inside the safe area (art nudged right)
    Lb=place(Lb_s,fx); Lh=place(render_lines(hk,S),fx)
    silc=place(cv2.resize(sil.astype(np.float32),None,fx=S,fy=S,interpolation=cv2.INTER_LINEAR),fx)>0.5
    cxc=(sx0+sx1)/2*S+fx; cyc=HAND_CY*S-topoff
    X0=int(round(cxc-outer/2)); Y0=int(round(cyc-outer/2)); X1=X0+outer; Y1=Y0+outer   # outer box [X0,X1) x [Y0,Y1)
    IX0,IY0=X0+w,Y0+w; qx,qy=IX0+GAP*MOD,IY0+GAP*MOD; qs=NH*MOD
    # ---- L1 body
    Lb[Y0:Y1,X0:X1]=0                                                         # old tray (and anything behind the platter) gone
    img=np.ones((CH,CW,3))*PURPLE; img=img*(1-Lb[...,None])+WHITE*Lb[...,None]
    # ---- L2 platter + QR
    img[Y0:Y1,X0:X1]=PURPLE
    ring=np.zeros((CH,CW),bool); ring[Y0:Y1,X0:X1]=True; ring[IY0:IY0+inner,IX0:IX0+inner]=False
    qr=np.zeros((CH,CW),bool); qr[qy:qy+qs,qx:qx+qs]=np.kron(QH,np.ones((MOD,MOD))).astype(bool)
    cover=cv2.dilate(silc.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*HALO+1,2*HALO+1)))>0
    img[(qr&~cover)|ring]=WHITE
    # ---- L3 hands (filled silhouette in front, then the hand lines)
    img[silc]=PURPLE
    img=img*(1-Lh[...,None])+WHITE*Lh[...,None]
    im=Image.fromarray(np.clip(img,0,255).astype(np.uint8)); ImageDraw.Draw(im).text((tx_left,CH/2),'anonabento.com',font=fnt,fill=(255,255,255),anchor='lm')
    # ---- checks
    covered=[];
    for rr in range(NH):
        for cc in range(NH):
            if cover[int(qy+(rr+.5)*MOD),int(qx+(cc+.5)*MOD)]: covered.append((rr,cc))
    def finder(rc): r_,c_=rc; return (r_<8 and c_<8) or (r_<8 and c_>=NH-8) or (r_>=NH-8 and c_<8)
    def fmt(rc): r_,c_=rc; return (r_==8 and (c_<9 or c_>=NH-8)) or (c_==8 and (r_<9 or r_>=NH-7))
    def timing(rc): r_,c_=rc; return r_==6 or c_==6
    def align(rc): r_,c_=rc; return 16<=r_<=20 and 16<=c_<=20
    S0,S1,T0,T1=BLEED+SAFE,CW-BLEED-SAFE,BLEED+SAFE,CH-BLEED-SAFE
    rimpix=ring.sum(); rim_hidden=(ring&silc).sum()
    layers=dict(body=Lb,hands=Lh,sil=silc,box=(X0,Y0,X1,Y1),qr=qr,cover=cover,ring=ring,tx=tx_left)
    return im,layers,dict(ecc=ECC.upper(),modules=NH,module_px=MOD,module_mm=round(MOD/DPI*25.4,3),qr_px=qs,qr_in=round(qs/DPI,3),
        rim_stroke_px=w,platter_outer_px=dict(w=X1-X0,h=Y1-Y0),platter_inner_px=dict(w=inner,h=inner),platter_is_square=bool(X1-X0==Y1-Y0),
        platter_outer_in=round(outer/DPI,3),corners='sharp (90 deg, no radius)',
        gap_modules=dict(left=(qx-IX0)/MOD,right=(IX0+inner-qx-qs)/MOD,top=(qy-IY0)/MOD,bottom=(IY0+inner-qy-qs)/MOD),
        modules_under_fingers=f'{len(covered)}/{NH*NH} ({len(covered)/NH/NH*100:.1f}%; ECC-M repairs ~15%)',
        finder_modules_hit=sum(map(finder,covered)),format_info_hit=sum(map(fmt,covered)),timing_hit=sum(map(timing,covered)),
        alignment_hit=sum(map(align,covered)),covered_rows=sorted({r_ for r_,_ in covered}),covered_cols=sorted({c_ for _,c_ in covered}),
        platter_in_safe=bool(X0>=S0 and Y0>=T0 and X1<=S1 and Y1<=T1),qr_in_safe=bool(qx>=S0 and qy>=T0 and qx+qs<=S1 and qy+qs<=T1),
        platter_top_below_trim_mm=round((Y0-BLEED)/DPI*25.4,2),platter_bottom_above_trim_mm=round((CH-BLEED-Y1)/DPI*25.4,2),
        rim_hidden_by_hands_pct=round(rim_hidden/rimpix*100,1),art_shift_down_px=int(round(CROP*S))-topoff,
        text_gap_to_platter_px=int(tx_left-X1),text_clear=bool(not (Lb[CH//2-60:CH//2+60,int(tx_left)-40:S1+10]>0.2).any()),
        text_min_gap_to_art_px=int(min([tx_left-np.nonzero(Lb[yy,:int(tx_left)]>0.3)[0].max() for yy in range(CH//2-45,CH//2+45) if (Lb[yy,:int(tx_left)]>0.3).any()] or [9999])),
        silhouette_ref_px=int(sil.sum()))

def build61():
    fr,_=front59(EYE_S)
    ns={}; exec(open('make_v52.py').read(),ns)
    bk,lay,binfo=back61(ns['fnt'])
    import zxingcpp
    chk={'back':binfo,'phone_shots24':scan_zx(bk,24)}
    dec={}
    for wd in (2250,1200,800,500,350):
        g=np.array(bk.convert('L').resize((wd,int(wd*CH/CW)),Image.LANCZOS)); dec[wd]=[b.text for b in zxingcpp.read_barcodes(255-g)]
    chk['qr_downscaled_zxing_widthpx']=dec
    g0=255-cv2.cvtColor(np.array(bk),cv2.COLOR_RGB2GRAY); chk['opencv_fullres']=det.detectAndDecode(cv2.copyMakeBorder(g0,40,40,40,40,cv2.BORDER_REPLICATE))[0]==URL
    return fr,bk,lay,chk

def layer_sheet(bk,lay):
    X0,Y0,X1,Y1=lay['box']; box=(max(0,X0-260),max(0,Y0-70),min(CW,X1+260),min(CH,Y1+70))
    def tile(a): return Image.fromarray(np.clip(a,0,255).astype(np.uint8)).crop(box)
    base=np.ones((CH,CW,3))*PURPLE
    l1=base*(1-lay['body'][...,None])+WHITE*lay['body'][...,None]
    l2=base.copy(); l2[Y0:Y1,X0:X1]=PURPLE*0.8; l2[lay['ring']|(lay['qr']&~lay['cover'])]=WHITE
    l3=base.copy(); l3[lay['sil']]=PURPLE*0.8; l3=l3*(1-lay['hands'][...,None])+WHITE*lay['hands'][...,None]
    tiles=[('1  body (old tray removed)',tile(l1)),('2  square platter + QR',tile(l2)),('3  hands (on top)',tile(l3)),('= composite',bk.crop(box))]
    s=0.42; tw_,th_=int(tiles[0][1].width*s),int(tiles[0][1].height*s); fl=F(26,600)
    sh=Image.new('RGB',(4*tw_+100,th_+70),(28,26,25)); d=ImageDraw.Draw(sh)
    for i,(t,im) in enumerate(tiles):
        sh.paste(im.resize((tw_,th_),Image.LANCZOS),(20+i*(tw_+20),55)); d.text((20+i*(tw_+20),14),t,font=fl,fill=(242,236,226))
    return sh

if __name__=='__main__':
    fr,bk,lay,chk=build61()
    print(json.dumps(chk,indent=1,default=str))
    if os.environ.get('PRINT'):
        os.makedirs('print',exist_ok=True)
        fr.save('print/bento-card-front-600dpi.png',dpi=(DPI,DPI),optimize=True); bk.save('print/bento-card-back-600dpi.png',dpi=(DPI,DPI),optimize=True)
        fr.save('print/bento-card-print.pdf',save_all=True,append_images=[bk],resolution=DPI,quality=95)
    pair(trim(fr),trim(bk)).save('v61-preview.jpg',quality=86)
    layer_sheet(bk,lay).save('v61-layers.jpg',quality=86)
    X0,Y0,X1,Y1=lay['box']; z=bk.crop((max(0,X0-200),max(0,Y0-50),min(CW,X1+200),min(CH,Y1+50))); z.save('v61-tray-zoom.jpg',quality=90)
    json.dump(chk,open('v61-checks.json','w'),indent=1,default=str)
