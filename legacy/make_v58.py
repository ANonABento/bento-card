# v58 = READY print files.
#  FRONT: v57 front with the printed scalloped border band removed (plain orange to the trim; art runs into the bleed).
#  BACK : tray simplified to ONE outline (outermost rim kept, the two inner rims erased).
#         TUCK=True (option 'tuck'): fingertips that crossed onto the tray are erased, so the hands hold the tray from the
#         sides and the QR can fill the whole tray interior (1-module gap). TUCK=False (DEFAULT) keeps fingertips; QR fills the clear space between them (~1.02 in).
# Needs make_v50..v57.py + reference.png in the working dir.  Usage: python make_v58.py [fingers|tuck]   (default fingers)
exec(open('make_v57.py').read().rsplit("if __name__=='__main__':",1)[0])
import json
TRAY_IN=(324,464,700,824)                                  # interior of the kept outer rim (reference.png px)
RIM_X=(321,702)                                            # outer rim lines, left/right (reference.png px)

def clean_tray(ink,tuck=True):
    ink=ink.astype(np.uint8); H,W=ink.shape
    def rrect(x0,y0,x1,y1,r):
        m=np.zeros((H,W),np.uint8); cv2.rectangle(m,(x0+r,y0),(x1-r,y1),1,-1); cv2.rectangle(m,(x0,y0+r),(x1,y1-r),1,-1)
        for cx,cy in ((x0+r,y0+r),(x1-r,y0+r),(x0+r,y1-r),(x1-r,y1-r)): cv2.circle(m,(cx,cy),r,1,-1)
        return m.astype(bool)
    R=rrect(*TRAY_IN,33)
    yy,xx=np.mgrid[0:H,0:W]; FB=(yy>=592)&(yy<=688)&((xx<364)|(xx>658))   # fingers wrap over the rim here
    out=ink.astype(bool).copy()
    if tuck:
        out[R]=False                                       # everything inside the rim goes, fingertips included
        o=out.astype(np.uint8)
        for x in RIM_X: cv2.line(o,(x,586),(x,694),1,2)   # close the rim where the fingertips used to cross it
        return o
    out[R&~FB]=False
    cols=list(range(325,330))+list(range(334,339))+list(range(685,690))+list(range(694,699))
    for y in range(592,689):
        row=ink[y].astype(bool)
        for x in cols:
            if not row[x]: continue
            l=x
            while l>0 and row[l-1]: l-=1
            r=x
            while r<W-1 and row[r+1]: r+=1
            if r-l+1<=2 and ink[y-1,x-1:x+2].any() and ink[y+1,x-1:x+2].any(): out[y,x]=False
    return out.astype(np.uint8)

def back58(ns,CROP=420,TEXT_GAP=80):
    S=(CH+4)/(1024-CROP); L=ns['lines_at'](S); top=int(round(CROP*S)); L=L[top:top+CH]
    cols=np.nonzero((L>0.5).any(0))[0]; c0,c1=cols.min(),cols.max(); fnt=ns['fnt']; NQ=ns['NQ']
    tw=fnt.getlength('anonabento.com'); tx_left=CW-BLEED-SAFE-tw; fx=int(min(BLEED+SAFE+10-c0, tx_left-TEXT_GAP-c1))
    lay=np.zeros((CH,CW),np.float32); xs0=max(0,fx); xs1=min(CW,fx+L.shape[1]); lay[:,xs0:xs1]=L[:,xs0-fx:xs1-fx]
    x0,y0,x1,y1=TRAY_IN; tx0,tx1,ty0,ty1=x0*S+fx,x1*S+fx,y0*S-top,y1*S-top
    blk=cv2.dilate((lay>0.2).astype(np.uint8),np.ones((3,3),np.uint8)); ii=cv2.integral(blk)
    def clear(a,b,c,d): return ii[d,c]-ii[b,c]-ii[d,a]+ii[b,a]==0
    S0,S1,T0,T1=BLEED+SAFE,CW-BLEED-SAFE,BLEED+SAFE,CH-BLEED-SAFE
    cxm,cym=(tx0+tx1)/2,(ty0+ty1)/2; best=None
    for qs in range(int(min(tx1-tx0,ty1-ty0)),200,-2):
        gap=int(np.ceil(qs/NQ)); tot=qs+2*gap
        for dy in sorted(range(-120,121,2),key=abs):
            for dx in sorted(range(-30,31,2),key=abs):
                bx=int(cxm+dx-tot/2);by=int(cym+dy-tot/2); qx,qy=bx+gap,by+gap
                if qx<S0 or qy<T0 or qx+qs>S1 or qy+qs>T1: continue          # the code itself stays in the safe area
                if clear(bx,by,bx+tot,by+tot): best=(qs,qx,qy,gap);break
            if best:break
        if best:break
    qs,qx,qy,gap=best
    text_clear=bool(clear(int(tx_left)-40,CH//2-60,CW-BLEED-SAFE+10,CH//2+60))
    img=np.ones((CH,CW,3))*PURPLE; img=img*(1-lay[...,None])+WHITE*lay[...,None]
    q=ns['qr_img'](qs);sub=img[qy:qy+qs,qx:qx+qs];img[qy:qy+qs,qx:qx+qs]=sub*(1-q[...,None])+WHITE*q[...,None]
    im=Image.fromarray(img.astype(np.uint8)); ImageDraw.Draw(im).text((tx_left,CH/2),'anonabento.com',font=fnt,fill=(255,255,255),anchor='lm')
    return im,dict(crop=CROP,qr_in=round(qs/DPI,3),qr_px=qs,module_mm=round(qs/NQ/DPI*25.4,3),gap_px=gap,qr_xy=(qx,qy),
                   tray_px=[round(v) for v in (tx0,ty0,tx1,ty1)],qr_share_of_tray=dict(w=round(qs/(tx1-tx0),3),h=round(qs/(ty1-ty0),3)),
                   text_clear=text_clear)

def build(tuck=False):
    base_layers(); _C['shape'][:]=True                   # no scalloped band
    fr,finfo=front56('C')
    ns={}; exec(open('make_v52.py').read(),ns); ns['ink']=clean_tray(ns['ink'],tuck)
    bk,binfo=back58(ns)
    S0,S1=BLEED+SAFE,CW-BLEED-SAFE; T0,T1=BLEED+SAFE,CH-BLEED-SAFE
    chk={'tuck':tuck,'back':binfo,'qr_scan':ns['scan'](bk)}
    det=cv2.QRCodeDetector(); dec={}
    for w in (2250,1200,800,500,350):
        g=np.array(bk.convert('L').resize((w,int(w*CH/CW)),Image.LANCZOS)); dec[w]=det.detectAndDecode(255-g)[0]
    chk['qr_downscaled_inverted']=dec
    chk['front_boxes_in_safe']={k:bool(a>=S0 and c<=S1 and b>=T0 and d<=T1) for k,(a,b,c,d) in BOXES.items()}
    chk['tail_tip_in_safe']=bool(TIP[0]<=S1 and TIP[1]>=T0); chk['pads_px']=pads(); chk['front']=finfo
    chk['contact_font_pt']=round(FC/DPI*72,2); chk['min_ok']=chk['contact_font_pt']>=8
    edge=np.array(fr)[BLEED:BLEED+40,CW//3:2*CW//3].reshape(-1,3).astype(int)
    chk['front_top_edge_is_plain_orange']=round(float((np.abs(edge-[0xe8,0x82,0x3f]).sum(1)<8).mean()),3)
    return fr,bk,chk

def trim(im): return im.crop((BLEED,BLEED,CW-BLEED,CH-BLEED))
def guides(im):
    S0,S1=BLEED+SAFE,CW-BLEED-SAFE; T0,T1=BLEED+SAFE,CH-BLEED-SAFE
    p=im.copy(); dd=ImageDraw.Draw(p); dd.rectangle([BLEED,BLEED,CW-BLEED,CH-BLEED],outline=(255,60,60),width=4)
    dd.rectangle([S0,T0,S1,T1],outline=(60,230,60),width=3); return p
def pair(a,b,w=1050):
    h=round(w*a.height/a.width); s=Image.new('RGB',(2*w+60,h+40),(28,26,25))
    s.paste(a.resize((w,h),Image.LANCZOS),(20,20)); s.paste(b.resize((w,h),Image.LANCZOS),(w+40,20)); return s

if __name__=='__main__':
    import sys; tuck=(len(sys.argv)>1 and sys.argv[1]=='tuck')
    fr,bk,chk=build(tuck); print(json.dumps(chk,indent=1,default=str))
    os.makedirs('print',exist_ok=True)
    fr.save('print/bento-card-front-600dpi.png',dpi=(DPI,DPI),optimize=True); bk.save('print/bento-card-back-600dpi.png',dpi=(DPI,DPI),optimize=True)
    fr.save('print/bento-card-print.pdf',save_all=True,append_images=[bk],resolution=DPI,quality=95)
    pair(trim(fr),trim(bk)).save('v58-preview.jpg',quality=88)          # what it looks like after cutting
    pair(guides(fr),guides(bk)).save('v58-guides.jpg',quality=84)       # red = trim, green = safe area (preview only)
    json.dump(chk,open('v58-checks.json','w'),indent=1,default=str)
