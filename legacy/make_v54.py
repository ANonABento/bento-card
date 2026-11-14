# v54 (Kevin: centre the name / try fonts, smaller speech-bubble tail, consistent padding on all lettering)
#  - ONE padding value P for every block; box heights are derived from their content, name box gets the rest
#  - every text block is placed by its real rendered ink bbox (not font metrics) -> true optical centring
#  - KEVIN / JIANG each centred horizontally, block centred vertically; 6 display fonts compared on variant A
#  - tail ~half size: 60px base (was 85), tip 80px out (was 165)
# Needs make_v53.py, make_v50.py, reference.png in the working dir.
import os,urllib.request
exec(open('make_v53.py').read().split("if __name__=='__main__':")[0])
GF='https://github.com/google/fonts/raw/main/ofl/'
FONTS={'Instrument Sans (current)':('instrumentsans/InstrumentSans%5Bwdth,wght%5D.ttf',{'weight':750}),
 'Space Grotesk':('spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf',{'weight':700}),
 'Archivo Semi-Expanded':('archivo/Archivo%5Bwdth,wght%5D.ttf',{'weight':800,'width':112}),
 'Bricolage Grotesque':('bricolagegrotesque/BricolageGrotesque%5Bopsz,wdth,wght%5D.ttf',{'weight':800,'optical':96}),
 'Unbounded':('unbounded/Unbounded%5Bwght%5D.ttf',{'weight':700}),
 'Syne':('syne/Syne%5Bwght%5D.ttf',{'weight':800})}
def FF(name,size):
    rel,ax=FONTS[name]; p='/tmp/'+rel.split('/')[-1].replace('%5B','[').replace('%5D',']')
    if not os.path.exists(p): urllib.request.urlretrieve(GF+rel,p)
    f=ImageFont.truetype(p,size)
    try:
        vals=[]
        for a in f.get_variation_axes():
            nm=a['name']; nm=(nm.decode() if isinstance(nm,bytes) else nm).lower()
            v=next((val for k,val in ax.items() if k in nm),a['default']); vals.append(max(a['minimum'],min(a['maximum'],v)))
        f.set_variation_by_axes(vals)
    except Exception as e: pass
    return f
def glyph(text,f,tr=0):
    s=f.size; W=int(f.getlength(text)+tr*len(text)+2*s); H=int(2.4*s); ox,oy=s//2,int(1.7*s)
    mk=Image.new('L',(W,H),0); d=ImageDraw.Draw(mk)
    if tr==0: d.text((ox,oy),text,font=f,fill=255,anchor='ls')
    else:
        x=ox
        for ch in text: d.text((x,oy),ch,font=f,fill=255,anchor='ls'); x+=f.getlength(ch)+tr
    bb=mk.getbbox(); return mk.crop(bb),bb[1]-oy,bb[3]-oy      # ink mask, ink top / bottom vs baseline
P=44; G=28; R=36; NG=.16; NTR=.03; LP=1.4; RG=20; FC=70
CONTACT=['kevin@anonabento.com','github.com/ANonABento','linkedin.com/in/ANonABento']
ROLE2=(('Physical AI Engineer',74,650),("UWaterloo Comp Eng '29",72,500))
def contact_layout():
    gl=[glyph(t,F(FC,500)) for t in CONTACT]; pitch=round(LP*FC); return gl,pitch,2*pitch+gl[2][2]-gl[0][1]
def role_layout():
    gl=[glyph(t,F(s,w)) for t,s,w in ROLE2]; return gl,gl[0][0].height+RG+gl[1][0].height
HC=contact_layout()[2]+2*P; HR=role_layout()[1]+2*P; HN=(CH-2*m)-2*G-HC-HR
Y1=m+HN; Y2=Y1+G+HR; XR=1110; XV=XR+G+190
BOXES={'name':(m,m,XR,Y1),'vert':(XR+G,m,XV,Y2),'role':(m,Y1+G,XR,Y2),'contact':(m,Y2+G,XV,CH-m)}
cx1=BOXES['contact'][2]; cy0=BOXES['contact'][1]; TIP=(cx1+80,cy0-22)
TAIL=[(cx1-10,cy0+44)]+bez((cx1-2,cy0+44),(cx1+42,cy0+40),TIP)+bez(TIP,(cx1+46,cy0+72),(cx1-2,cy0+104))+[(cx1-10,cy0+104)]
_NF={}
def name_fit(font):
    if font in _NF: return _NF[font]
    a,b,c,d=BOXES['name']; W=c-a-2*P; H=d-b-2*P; best=None
    for s in range(150,420,2):
        f=FF(font,s); tr=NTR*s; k=glyph('KEVIN',f,tr)[0]; j=glyph('JIANG',f,tr)[0]; gap=round(NG*s)
        w=max(k.width,j.width); h=k.height+gap+j.height
        if w<=W and h<=H: best=(s,k,j,gap,w,h)
        else: break
    _NF[font]=best; return best
def vert_fit():
    a,b,c,d=BOXES['vert']
    for s in range(120,50,-2):
        g=glyph('ANonABento',F(s,700))[0]
        if g.width<=(d-b)-2*P and g.height<=(c-a)-2*P: return s,g
_C={}
def base_layers():
    if 'lay' not in _C:
        S=S_F; ex,ey=EYE_AT
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
        _C['lay']=lay; _C['shape']=shape; _C['M']=block_mask()
    return _C['lay'],_C['shape'],_C['M']
PL={}
def put(im,mk,x,y,col,tag):
    x,y=int(round(x)),int(round(y)); im.paste(Image.new('RGB',mk.size,col),(x,y),mk); PL.setdefault(tag,[]).append((x,y,x+mk.width,y+mk.height))
def front(block='dark',alpha=1.0,font='Instrument Sans (current)'):
    PL.clear(); BL=BLOCK[block]; lay,shape,M=base_layers()
    img=np.where(shape[...,None],ORANGE,BL); img=img*(1-lay[...,None])+INK*lay[...,None]
    Ma=M*alpha; img=img*(1-Ma[...,None])+BL*Ma[...,None]
    im=Image.fromarray(np.clip(img,0,255).astype(np.uint8)); it=tuple(INK.astype(int))
    a,b,c,d=BOXES['name']; s,k,j,gap,w,h=name_fit(font); y0=b+((d-b)-h)/2; cxm=(a+c)/2
    put(im,k,cxm-k.width/2,y0,it,'name'); put(im,j,cxm-j.width/2,y0+k.height+gap,it,'name')
    a,b,c,d=BOXES['role']; gl,h=role_layout(); y0=b+((d-b)-h)/2
    put(im,gl[0][0],a+P,y0,it,'role'); put(im,gl[1][0],a+P,y0+gl[0][0].height+RG,it,'role')
    a,b,c,d=BOXES['contact']; gl,pitch,h=contact_layout(); base=b+((d-b)-h)/2-gl[0][1]
    for i,(mk,top,bot) in enumerate(gl): put(im,mk,a+P,base+i*pitch+top,it,'contact')
    a,b,c,d=BOXES['vert']; s,g=vert_fit(); g=g.rotate(-90,expand=True); put(im,g,(a+c)/2-g.width/2,(b+d)/2-g.height/2,it,'vert')
    return im
def pads():
    out={}
    for t,rs in PL.items():
        a,b,c,d=BOXES[t]; x0=min(r[0] for r in rs); y0=min(r[1] for r in rs); x1=max(r[2] for r in rs); y1=max(r[3] for r in rs)
        out[t]=dict(L=x0-a,R=c-x1,T=y0-b,B=d-y1)
    return out
pt=lambda px:round(px/DPI*72,1)
SHEET_W=1200; Q=78
def make_sheets(which=('fonts','preview')):
    w,h=CW//2,CH//2; fl=F(44,600); rep={}
    if 'fonts' in which:
        names=list(FONTS); sheet=Image.new('RGB',(2*w+30,3*(h+70)+10),(28,26,25)); sd=ImageDraw.Draw(sheet)
        for i,fn in enumerate(names):
            im=front('dark',1.0,fn); s=name_fit(fn)[0]; x=(i%2)*(w+30); y=(i//2)*(h+70)
            sd.text((x+8,y+12),f'{i+1}  {fn}  ({pt(s)}pt)',font=fl,fill=(242,236,226)); sheet.paste(im.resize((w,h),Image.LANCZOS),(x,y+60))
            rep[fn]=dict(px=s,pt=pt(s),pads=pads()['name'])
        sheet.resize((SHEET_W,int(sheet.height*SHEET_W/sheet.width)),Image.LANCZOS).save('v54-fonts.jpg',quality=Q)
    if 'preview' in which:
        V=[('dark',1.0,'A  darker, opaque'),('light',1.0,'B  lighter, opaque'),('dark',.82,'C  darker, 82%'),('light',.82,'D  lighter, 82%')]
        sheet=Image.new('RGB',(2*w+30,2*(h+70)+10),(28,26,25)); sd=ImageDraw.Draw(sheet)
        for i,(bl,al,lab) in enumerate(V):
            im=front(bl,al); x=(i%2)*(w+30); y=(i//2)*(h+70)
            sd.text((x+8,y+12),lab,font=fl,fill=(242,236,226)); sheet.paste(im.resize((w,h),Image.LANCZOS),(x,y+60))
        sheet.resize((SHEET_W,int(sheet.height*SHEET_W/sheet.width)),Image.LANCZOS).save('v54-preview.jpg',quality=Q)
    return rep
if __name__=='__main__':
    rep=make_sheets()
    print('boxes',BOXES,'HN/HR/HC',HN,HR,HC); print('tail tip',TIP,'safe edge',CW-BLEED-SAFE)
    print('pads',pads()); print('fonts',rep)
