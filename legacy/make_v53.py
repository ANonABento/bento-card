# v53: ink-line eye on orange. Changes from v52 (Kevin's notes):
#  - colours back to orange #e8823f + ink #0e0b0a lines
#  - block colour: 'dark' #c56f36 vs 'light' #f0ae82 (rendered both)
#  - art runs full-bleed incl. scallop band + shows in the gaps between blocks (v52's 61px mask removed)
#  - blocks opaque vs 82% (lines ghost through) -> rendered both
#  - KEVIN / JIANG auto-fit to the name box (largest size that fits width AND height)
#  - contact box taller, more line spacing; contact box gets a speech-bubble tail pointing at the face
import os,sys,glob,shutil
for fn in ('make_v50.py','reference.png'):
    if not os.path.exists(fn):
        c=glob.glob('**/'+fn,recursive=True) or glob.glob('/workspace/**/v50/'+fn,recursive=True)
        shutil.copy(c[0],fn)
exec(open('make_v50.py').read().split('if __name__')[0])
ORANGE=np.array((0xe8,0x82,0x3f),float); INK=np.array((0x0e,0x0b,0x0a),float)
BLOCK={'dark':np.array((0xc5,0x6f,0x36),float),'light':np.array((0xf0,0xae,0x82),float)}
EYE=(440,295); S_F=4.6; EYE_AT=(1800,600)
def lines_crop(S,x0,y0,x1,y1):
    sub=ink[max(0,y0):y1,max(0,x0):x1].astype(np.float32)
    mm=cv2.resize(sub,None,fx=S,fy=S,interpolation=cv2.INTER_LINEAR)>0.3
    sk=skeletonize(mm).astype(np.uint8)
    out=(mm|cv2.dilate(sk,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(MINPX+2,MINPX+2))).astype(bool)).astype(np.float32)
    big=cv2.resize(out,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
    big=np.clip((cv2.GaussianBlur(big,(0,0),2.0)-0.5)*4+0.5,0,1)
    return cv2.resize(big,(out.shape[1],out.shape[0]),interpolation=cv2.INTER_AREA)
m=BLEED+SAFE+20; G=28; PAD=44; R=36
Y1,Y2=620,850   # name box bottom / role box bottom (name got taller, role tighter, contact taller)
BOXES={'name':(m,m,1110,Y1),'vert':(1110+G,m,1110+G+190,Y2),'role':(m,Y1+G,1110,Y2),'contact':(m,Y2+G,1110+G+190,CH-m)}
TRACK_MAX=.045  # max letter-spacing (em) used to push the wider word to the box's right padding
def bez(p0,p1,p2,n=24):
    t=np.linspace(0,1,n)[:,None]; p0,p1,p2=map(np.array,(p0,p1,p2)); return list(map(tuple,(1-t)**2*p0+2*(1-t)*t*p1+t*t*p2))
cx1=BOXES['contact'][2]; cy0=BOXES['contact'][1]
TIP=(cx1+165,cy0-30)
TAIL=[(cx1-10,cy0+50)]+bez((cx1-2,cy0+50),(cx1+90,cy0+45),TIP)+bez(TIP,(cx1+100,cy0+100),(cx1-2,cy0+135))+[(cx1-10,cy0+135)]
def name_fit():
    a,b,c,d=BOXES['name']; W=c-a-2*PAD; H=d-b-2*PAD; best=None
    for s in range(160,400,2):
        f=F(s,750); bk=f.getbbox('KEVIN',anchor='ls'); bj=f.getbbox('JIANG',anchor='ls'); gap=int(.13*s)
        w=max(bk[2]-bk[0],bj[2]-bj[0]); h=(-bk[1])+gap+(-bj[1])+max(0,bj[3])
        if w<=W and h<=H: best=(s,f,bk,bj,gap,w,h)
        else: break
    s,f,bk,bj,gap,w,h=best; tr=min(TRACK_MAX*s,(W-w)/4)
    return s,f,bk,bj,gap,w+4*tr,h,tr
def tracked(dr,x,y,t,f,tr,fill):
    for ch in t: dr.text((x,y),ch,font=f,fill=fill,anchor='ls'); x+=f.getlength(ch)+tr
def fit_vert():
    a,b,c,d=BOXES['vert']
    for s in range(100,60,-2):
        if F(s,700).getlength('ANonABento')<=d-b-60: return s
ROLE=(('Physical AI Engineer',74,650),("UWaterloo Comp Eng '29",72,500)); RGAP=16
def role_lines():   # centre the two role lines by their real ink (incl. y/p/g descenders)
    a,b,c,d=BOXES['role']; fs=[F(s,w) for _,s,w in ROLE]; bb=[f.getbbox(t,anchor='ls') for f,(t,_,_) in zip(fs,ROLE)]
    h=(bb[0][3]-bb[0][1])+RGAP+(bb[1][3]-bb[1][1]); y0=b+((d-b)-h)/2
    y1=y0-bb[0][1]; y2=y1+bb[0][3]+RGAP-bb[1][1]
    return [(a+PAD,y1,ROLE[0][0],fs[0]),(a+PAD,y2,ROLE[1][0],fs[1])],(y0-b,d-(y0+h))
def block_mask():
    M=Image.new('L',(CW*2,CH*2),0); md=ImageDraw.Draw(M)
    for (a,b,c,d) in BOXES.values(): md.rounded_rectangle((a*2,b*2,c*2,d*2),R*2,fill=255)
    md.polygon([(x*2,y*2) for x,y in TAIL],fill=255)
    return np.array(M.resize((CW,CH),Image.LANCZOS),np.float32)/255
def front(block='dark',alpha=1.0):
    BL=BLOCK[block]; S=S_F; ex,ey=EYE_AT
    rx0=int(EYE[0]-ex/S)-2; ry0=int(EYE[1]-ey/S)-2; rx1=int(EYE[0]+(CW-ex)/S)+3; ry1=int(EYE[1]+(CH-ey)/S)+3
    L=lines_crop(S,rx0,ry0,rx1,ry1); ox=int(round(ex-(EYE[0]-rx0)*S)); oy=int(round(ey-(EYE[1]-ry0)*S))
    lay=np.zeros((CH,CW),np.float32); ys0,xs0=max(0,oy),max(0,ox); ys1,xs1=min(CH,oy+L.shape[0]),min(CW,ox+L.shape[1])
    lay[ys0:ys1,xs0:xs1]=L[ys0-oy:ys1-oy,xs0-ox:xs1-ox]
    yy,xx=np.mgrid[0:CH,0:CW]; ins=BLEED+34; r=16
    shape=((xx>=ins)&(xx<=CW-ins)&(yy>=ins)&(yy<=CH-ins))
    for cx in np.arange(ins,CW-ins+1,2*r):
        for cy in (ins,CH-ins): shape|=((xx-cx)**2+(yy-cy)**2<=r*r)
    for cy in np.arange(ins,CH-ins+1,2*r):
        for cx in (ins,CW-ins): shape|=((xx-cx)**2+(yy-cy)**2<=r*r)
    img=np.where(shape[...,None],ORANGE,BL)
    img=img*(1-lay[...,None])+INK*lay[...,None]          # art everywhere: band, gaps, right side
    M=block_mask()*alpha; img=img*(1-M[...,None])+BL*M[...,None]
    im=Image.fromarray(np.clip(img,0,255).astype(np.uint8)); dr=ImageDraw.Draw(im); it=tuple(INK.astype(int))
    a,b,c,d=BOXES['name']; s,f,bk,bj,gap,w,h,tr=name_fit(); y=b+((d-b)-h)/2-bk[1]
    tracked(dr,a+PAD-bk[0],y,'KEVIN',f,tr,it); tracked(dr,a+PAD-bj[0],y+gap-bj[1],'JIANG',f,tr,it)
    a,b,c,d=BOXES['role']
    for (x,y,t,f) in role_lines()[0]: dr.text((x,y),t,font=f,fill=it,anchor='ls')
    a,b,c,d=BOXES['contact']; fc=F(70,500); lh=(d-b-2*40)/3
    for i,t in enumerate(['kevin@anonabento.com','github.com/ANonABento','linkedin.com/in/ANonABento']): dr.text((a+PAD,b+40+lh*(i+.5)),t,font=fc,fill=it,anchor='lm')
    a,b,c,d=BOXES['vert']; fV=F(fit_vert(),700); tw=int(fV.getlength('ANonABento'))
    t=Image.new('RGBA',(tw+20,150),(0,0,0,0)); ImageDraw.Draw(t).text((10,75),'ANonABento',font=fV,fill=it+(255,),anchor='lm')
    t=t.rotate(-90,expand=True); im.paste(t,(int((a+c)/2-t.width/2),int((b+d)/2-t.height/2)),t)
    return im
def report():
    s,f,bk,bj,gap,w,h,tr=name_fit(); a,b,c,d=BOXES['name']; pt=lambda px:round(px/DPI*72,1)
    a2,b2,c2,d2=BOXES['contact']
    return dict(name_px=s,name_pt=pt(s),name_w=f'{int(w)}/{c-a-2*PAD}',track_px=round(tr,1),name_h=f'{h}/{d-b-2*PAD}',vert_px=fit_vert(),vert_pt=pt(fit_vert()),
        contact_pt=pt(70),contact_line_pitch=round((d2-b2-80)/3),contact_w=f"{int(F(70,500).getlength('linkedin.com/in/ANonABento'))}/{c2-a2-2*PAD}",
        role2_pt=pt(72),role_pad_top_bottom=tuple(round(v) for v in role_lines()[1]),tail_tip=TIP,inside_safe=all(v>=BLEED+SAFE for v in (m,)) and BOXES['contact'][3]<=CH-BLEED-SAFE and TIP[0]<=CW-BLEED-SAFE)
if __name__=='__main__':
    V=[('dark',1.0,'A  darker blocks, opaque'),('light',1.0,'B  lighter blocks, opaque'),('dark',.82,'C  darker blocks, 82%'),('light',.82,'D  lighter blocks, 82%')]
    w,h=CW//2,CH//2; sheet=Image.new('RGB',(2*w+30,2*(h+70)+10),(28,26,25)); sd=ImageDraw.Draw(sheet); fl=F(44,600)
    for i,(bl,al,lab) in enumerate(V):
        im=front(bl,al); x=(i%2)*(w+30); y=(i//2)*(h+70)
        sd.text((x+8,y+12),lab,font=fl,fill=(242,236,226)); sheet.paste(im.resize((w,h),Image.LANCZOS),(x,y+60))
    sheet=sheet.resize((1600,int(sheet.height*1600/sheet.width)),Image.LANCZOS); sheet.save('v53-preview.jpg',quality=84); print(report())
