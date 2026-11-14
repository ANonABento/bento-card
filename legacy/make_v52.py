
# v52: mockup of Kevin's sketch. FRONT = orange bento with darker-orange compartments (text) + big peeking eye
# from reference.png on the right. BACK = v51 text-right layout cropped from the collar down (crop picked by QR size).
import os,sys
exec(open('make_v50.py').read().split('if __name__')[0])
ORANGE=np.array((0xe8,0x82,0x3f),float); DARK=np.array((0xc5,0x6f,0x36),float); INK=np.array((0x0e,0x0b,0x0a),float)
EYE=(440,295)   # image-left eye centre on reference.png (lash line y~257, lower lid y~340)
def lines_crop(S,x0,y0,x1,y1):
    sub=ink[max(0,y0):y1,max(0,x0):x1].astype(np.float32)
    m=cv2.resize(sub,None,fx=S,fy=S,interpolation=cv2.INTER_LINEAR)>0.3
    sk=skeletonize(m).astype(np.uint8)
    out=(m|cv2.dilate(sk,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(MINPX+2,MINPX+2))).astype(bool)).astype(np.float32)
    big=cv2.resize(out,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
    big=np.clip((cv2.GaussianBlur(big,(0,0),2.0)-0.5)*4+0.5,0,1)
    return cv2.resize(big,(out.shape[1],out.shape[0]),interpolation=cv2.INTER_AREA)
m=BLEED+SAFE+20; G=28; PAD=48
BOXES={'name':(m,m,1110,560),'vert':(1110+G,m,1110+G+190,860),'role':(m,560+G,1110,860),'contact':(m,860+G,1110+G+190,CH-m)}
FONTS={'name':(220,750),'role1':(78,650),'role2':(72,500),'contact':(70,500),'vert':(100,700)}
def front(S,ex,ey,line_col,tag):
    rx0=int(EYE[0]-ex/S)-2; ry0=int(EYE[1]-ey/S)-2; rx1=int(EYE[0]+(CW-ex)/S)+3; ry1=int(EYE[1]+(CH-ey)/S)+3
    L=lines_crop(S,rx0,ry0,rx1,ry1); ox=int(round(ex-(EYE[0]-rx0)*S)); oy=int(round(ey-(EYE[1]-ry0)*S))
    lay=np.zeros((CH,CW),np.float32); ys0,xs0=max(0,oy),max(0,ox); ys1,xs1=min(CH,oy+L.shape[0]),min(CW,ox+L.shape[1])
    lay[ys0:ys1,xs0:xs1]=L[ys0-oy:ys1-oy,xs0-ox:xs1-ox]
    # scallop: printed scalloped frame (straight trim can't be die-cut wavy). orange = inset rect + r16 bumps; outside = dark band into bleed
    yy,xx=np.mgrid[0:CH,0:CW]; ins=BLEED+34; r=16
    shape=((xx>=ins)&(xx<=CW-ins)&(yy>=ins)&(yy<=CH-ins))
    for cx in np.arange(ins,CW-ins+1,2*r):
        for cy in (ins,CH-ins): shape|=((xx-cx)**2+(yy-cy)**2<=r*r)
    for cy in np.arange(ins,CH-ins+1,2*r):
        for cx in (ins,CW-ins): shape|=((xx-cx)**2+(yy-cy)**2<=r*r)
    img=np.where(shape[...,None],ORANGE,DARK)
    bm=np.zeros((CH,CW),np.uint8)
    for (a,b,c,d) in BOXES.values(): cv2.rectangle(bm,(a,b),(c,d),255,-1)
    lay[cv2.dilate(bm,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(61,61)))>0]=0; lay[~shape]=0
    img=img*(1-lay[...,None])+line_col*lay[...,None]
    im=Image.fromarray(img.astype(np.uint8)); dr=ImageDraw.Draw(im); it=tuple(INK.astype(int))
    for (a,b,c,d) in BOXES.values(): dr.rounded_rectangle((a,b,c,d),36,fill=tuple(DARK.astype(int)))
    a,b,c,d=BOXES['name']; fN=F(*FONTS['name'])
    dr.text((a+PAD,(b+d)/2-6),'KEVIN',font=fN,fill=it,anchor='ld'); dr.text((a+PAD,(b+d)/2+6),'JIANG',font=fN,fill=it,anchor='la')
    a,b,c,d=BOXES['role']
    dr.text((a+PAD,(b+d)/2-12),'Physical AI Engineer',font=F(*FONTS['role1']),fill=it,anchor='ld'); dr.text((a+PAD,(b+d)/2+14),"UWaterloo Comp Eng '29",font=F(*FONTS['role2']),fill=it,anchor='la')
    a,b,c,d=BOXES['contact']; fc=F(*FONTS['contact']); lh=(d-b-2*PAD)/3
    for i,t in enumerate(['kevin@anonabento.com','github.com/ANonABento','linkedin.com/in/ANonABento']): dr.text((a+PAD,b+PAD+lh*(i+.5)),t,font=fc,fill=it,anchor='lm')
    a,b,c,d=BOXES['vert']; fV=F(*FONTS['vert']); tw=int(fV.getlength('ANonABento'))
    t=Image.new('RGBA',(tw+20,150),(0,0,0,0)); ImageDraw.Draw(t).text((10,75),'ANonABento',font=fV,fill=it+(255,),anchor='lm')
    t=t.rotate(-90,expand=True); im.paste(t,(int((a+c)/2-t.width/2),int((b+d)/2-t.height/2)),t)
    return im
def fits():
    out={}
    for k,s,f,box in (('KEVIN','KEVIN','name','name'),('JIANG','JIANG','name','name'),('role1','Physical AI Engineer','role1','role'),('role2',"UWaterloo Comp Eng '29",'role2','role'),('contact','linkedin.com/in/ANonABento','contact','contact'),('vert','ANonABento','vert','vert')):
        a,b,c,d=BOXES[box]; room=(d-b-60) if k=='vert' else (c-a-2*PAD); out[k]=(int(F(*FONTS[f]).getlength(s)),room)
    return out
def back(CROP,TEXT_GAP=80):
    S=(CH+4)/(1024-CROP); L=lines_at(S); top=int(round(CROP*S)); L=L[top:top+CH]
    cols=np.nonzero((L>0.5).any(0))[0]; c0,c1=cols.min(),cols.max()
    tw=fnt.getlength('anonabento.com'); tx_left=CW-BLEED-SAFE-tw; fx=int(min(BLEED+SAFE+10-c0, tx_left-TEXT_GAP-c1))
    lay=np.zeros((CH,CW),np.float32); xs0=max(0,fx); xs1=min(CW,fx+L.shape[1]); lay[:,xs0:xs1]=L[:,xs0-fx:xs1-fx]
    tx0,tx1,ty0,ty1=[v*S for v in (335,687,477,812)]; tx0+=fx;tx1+=fx;ty0-=top;ty1-=top
    blk=cv2.dilate((lay>0.2).astype(np.uint8),np.ones((3,3),np.uint8)); ii=cv2.integral(blk)
    def clear(a,b,c,d): return ii[d,c]-ii[b,c]-ii[d,a]+ii[b,a]==0
    cxm,cym=(tx0+tx1)/2,(ty0+ty1)/2; best=None
    for qs in range(int(min(tx1-tx0,ty1-ty0)),200,-2):
        gap=int(np.ceil(qs/NQ)); tot=qs+2*gap
        for dy in sorted(range(-60,61,2),key=abs):
            for dx in sorted(range(-40,41,2),key=abs):
                bx=int(cxm+dx-tot/2);by=int(cym+dy-tot/2)
                if bx<0 or by<0 or bx+tot>=CW or by+tot>=CH: continue
                if clear(bx,by,bx+tot,by+tot): best=(qs,bx+gap,by+gap,gap);break
            if best:break
        if best:break
    qs,qx,qy,gap=best
    text_clear=bool(clear(int(tx_left)-40,CH//2-60,CW-BLEED-SAFE+10,CH//2+60))
    qr_safe=qx>=BLEED+SAFE and qx+qs<=CW-BLEED-SAFE and qy>=BLEED+SAFE and qy+qs<=CH-BLEED-SAFE
    img=np.ones((CH,CW,3))*PURPLE; img=img*(1-lay[...,None])+WHITE*lay[...,None]
    q=qr_img(qs);sub=img[qy:qy+qs,qx:qx+qs];img[qy:qy+qs,qx:qx+qs]=sub*(1-q[...,None])+WHITE*q[...,None]
    im=Image.fromarray(img.astype(np.uint8)); ImageDraw.Draw(im).text((tx_left,CH/2),'anonabento.com',font=fnt,fill=(255,255,255),anchor='lm')
    return im,dict(crop=CROP,qr_in=round(qs/DPI,3),module_mm=round(qs/NQ/DPI*25.4,3),text_clear=text_clear,qr_in_safe=bool(qr_safe))
def guides(im):
    pv=im.copy();dd=ImageDraw.Draw(pv)
    dd.rectangle([BLEED,BLEED,CW-BLEED,CH-BLEED],outline=(255,80,80),width=4)
    dd.rectangle([BLEED+SAFE,BLEED+SAFE,CW-BLEED-SAFE,CH-BLEED-SAFE],outline=(80,255,80),width=3); return pv
S_F=4.6; EYE_AT=(1800,600)
