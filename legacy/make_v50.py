# v50: the user's own reference line art (reference.png / chat image.png) used DIRECTLY as Girl #1 back art.
# No regeneration -> no drift. Inverted to white-on-purple; QR placed in the tray between her fingers
# with a 1-module gap; anonabento.com one-liner placed in free space. Three crops: A full, B from ears, C from under eyes.
import subprocess,sys,os,urllib.request
subprocess.run([sys.executable,'-m','pip','install','-q','segno','scikit-image'],check=True,capture_output=True)
import numpy as np,cv2,segno
from skimage.morphology import skeletonize
from PIL import Image,ImageDraw,ImageFont
DPI=600;BLEED=75;CW,CH=2250,1350;SAFE=48;MINPX=6
PURPLE=np.array((167,139,250),float);WHITE=np.array((255,255,255),float)
URL='https://anonabento.com'
p='/tmp/sans.ttf'
if not os.path.exists(p): urllib.request.urlretrieve('https://github.com/google/fonts/raw/main/ofl/instrumentsans/InstrumentSans%5Bwdth,wght%5D.ttf',p)
def F(size,weight):
    f=ImageFont.truetype(p,size)
    try:
        vals=[]
        for a in f.get_variation_axes():
            nm=a['name'];nm=(nm.decode() if isinstance(nm,bytes) else nm).lower()
            vals.append(max(a['minimum'],min(a['maximum'],weight if 'weight' in nm else a['default'])))
        f.set_variation_by_axes(vals)
    except Exception: pass
    return f
QM=np.array(segno.make(URL,error='m',micro=False).matrix,dtype=np.uint8);NQ=QM.shape[0]
det=cv2.QRCodeDetector()
def qr_img(size):
    mod=size/NQ;img=np.zeros((size,size),np.float32)
    for r in range(NQ):
        for c in range(NQ):
            if QM[r,c]: img[int(round(r*mod)):int(round((r+1)*mod)),int(round(c*mod)):int(round((c+1)*mod))]=1
    return img
def scan(im):
    gg0=255-cv2.cvtColor(np.array(im),cv2.COLOR_RGB2GRAY);res={}
    for sc in (1,.5,.3,.2):
        gg=cv2.resize(gg0,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA)
        res[sc]=det.detectAndDecode(cv2.copyMakeBorder(gg,40,40,40,40,cv2.BORDER_REPLICATE))[0]==URL
    ok=0
    for seed in range(8):
        rg=np.random.default_rng(seed);sc_=rg.uniform(.25,.45);gg=cv2.resize(gg0,None,fx=sc_,fy=sc_,interpolation=cv2.INTER_AREA);hh,ww=gg.shape
        j=rg.uniform(0,.05,8)
        M=cv2.getPerspectiveTransform(np.float32([[0,0],[ww,0],[ww,hh],[0,hh]]),np.float32([[ww*j[0],hh*j[1]],[ww*(1-j[2]),hh*j[3]],[ww*(1-j[4]),hh*(1-j[5])],[ww*j[6],hh*(1-j[7])]]))
        q=cv2.GaussianBlur(cv2.warpPerspective(gg,M,(ww,hh),borderMode=cv2.BORDER_REPLICATE),(0,0),rg.uniform(.6,1.6))
        q=np.clip(q*rg.uniform(.7,1)+rg.normal(0,8,q.shape),0,255).astype(np.uint8)
        ok+=det.detectAndDecode(q)[0]==URL
    res['phones8']=f'{ok}/8';return res
REF='reference.png' if os.path.exists('reference.png') else 'image.png'
g=cv2.imread(REF,0)
ink=(g<150).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(ink,8)
keep=np.zeros(n,bool);keep[1:]=st[1:,4]>=12;ink=keep[lab].astype(np.uint8)
def lines_at(S):
    m=cv2.resize(ink.astype(np.float32),None,fx=S,fy=S,interpolation=cv2.INTER_LINEAR)>0.3
    sk=skeletonize(m).astype(np.uint8)
    out=(m|cv2.dilate(sk,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(MINPX,MINPX))).astype(bool)).astype(np.float32)
    big=cv2.resize(out,None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC)
    big=np.clip((cv2.GaussianBlur(big,(0,0),3.0)-0.5)*4+0.5,0,1)
    return cv2.resize(big,(out.shape[1],out.shape[0]),interpolation=cv2.INTER_AREA)
fnt=F(67,500)
def render(CROP,name):
    S=(CH+4)/(1024-CROP)
    L=lines_at(S); top=int(round(CROP*S)); L=L[top:top+CH]
    cols=np.nonzero((L>0.5).any(0))[0]; x0=cols.min(); fx=BLEED+SAFE+10-x0
    lay=np.zeros((CH,CW),np.float32); xs0=max(0,fx); xs1=min(CW,fx+L.shape[1]); lay[:,xs0:xs1]=L[:,xs0-fx:xs1-fx]
    tx0,tx1,ty0,ty1=[v*S for v in (335,687,477,812)]; tx0+=fx;tx1+=fx;ty0-=top;ty1-=top   # tray interior (measured on reference)
    blk=cv2.dilate((lay>0.2).astype(np.uint8),np.ones((3,3),np.uint8)); ii=cv2.integral(blk)
    def clear(a,b,c,d): return ii[d,c]-ii[b,c]-ii[d,a]+ii[b,a]==0
    cxm,cym=(tx0+tx1)/2,(ty0+ty1)/2; best=None
    for qs in range(int(min(tx1-tx0,ty1-ty0)),200,-2):
        gap=int(np.ceil(qs/NQ)); tot=qs+2*gap            # 1-module gap to any ink (fingers, tray line)
        for dy in sorted(range(-60,61,2),key=abs):
            for dx in sorted(range(-40,41,2),key=abs):
                bx=int(cxm+dx-tot/2);by=int(cym+dy-tot/2)
                if bx<0 or by<0 or bx+tot>=CW or by+tot>=CH: continue
                if clear(bx,by,bx+tot,by+tot): best=(qs,bx+gap,by+gap,gap);break
            if best:break
        if best:break
    qs,qx,qy,gap=best
    img=np.ones((CH,CW,3))*PURPLE; img=img*(1-lay[...,None])+WHITE*lay[...,None]
    q=qr_img(qs);sub=img[qy:qy+qs,qx:qx+qs];img[qy:qy+qs,qx:qx+qs]=sub*(1-q[...,None])+WHITE*q[...,None]
    artR=int(np.nonzero((lay>0.2).any(0))[0].max()); tw=fnt.getlength('anonabento.com'); room=CW-BLEED-SAFE-artR
    info=dict(crop=CROP,scale=round(S,3),qr_in=round(qs/DPI,3),module_mm=round(qs/NQ/DPI*25.4,3),gap_px=gap)
    if room>=tw+40:
        im=Image.fromarray(img.astype(np.uint8)); ImageDraw.Draw(im).text((artR+(room-tw)/2,qy+qs/2),'anonabento.com',font=fnt,fill=(255,255,255),anchor='lm'); info['text']='horizontal, right of art'
    else:
        t=Image.new('L',(int(tw)+10,100),0);ImageDraw.Draw(t).text((5,50),'anonabento.com',font=fnt,fill=255,anchor='lm')
        a=np.array(t.rotate(90,expand=True))/255.; xc=CW-BLEED-SAFE-a.shape[1]; y0=int(qy+qs/2-a.shape[0]/2)
        reg=img[y0:y0+a.shape[0],xc:xc+a.shape[1]]; img[y0:y0+a.shape[0],xc:xc+a.shape[1]]=reg*(1-a[...,None])+WHITE*a[...,None]
        im=Image.fromarray(img.astype(np.uint8)); info['text']='vertical, right edge'
    info.update(scan(im)); im.save(f'back-{name}.png',dpi=(DPI,DPI))
    pv=im.copy();dd=ImageDraw.Draw(pv)
    dd.rectangle([BLEED,BLEED,CW-BLEED,CH-BLEED],outline=(255,80,80),width=4)
    dd.rectangle([BLEED+SAFE,BLEED+SAFE,CW-BLEED-SAFE,CH-BLEED-SAFE],outline=(80,255,80),width=3)
    print(name,info); return pv
if __name__=='__main__' or True:
    pvs=[render(c,nm) for c,nm in ((0,'A_full'),(150,'B_ears'),(290,'C_seams'))]
    w,h=CW//2,CH//2; sheet=Image.new('RGB',(w,3*h+40),(30,30,30))
    for i,pv in enumerate(pvs): sheet.paste(pv.resize((w,h)),(0,i*(h+20)))
    sheet.save('v50-sheet.jpg',quality=88)
