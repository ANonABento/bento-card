
# v55 (Kevin: B lighter opaque, Archivo Semi-Expanded name filling the whole block, test mini icons on contact)
#  - name: size set so KEVIN+JIANG fill the block height (inside padding P); then each line's Archivo width axis
#    is tuned so the line's ink spans the full inner width -> both lines exactly block-wide, a justified slab
#  - icons: Font Awesome 6 Free (envelope solid, github + linkedin brands; icons CC BY 4.0) at ~1.15x cap height,
#    fixed icon column so the three links stay left-aligned
# Needs make_v54.py, make_v53.py, make_v50.py, reference.png in the working dir.
import urllib.request,os
exec(open('make_v54.py').read().rsplit("if __name__=='__main__':",1)[0])
# fonts in a private folder, always re-downloaded and checked by family name (a stale /tmp font once slipped in)
FD='/tmp/bento55_fonts/'; os.makedirs(FD,exist_ok=True)
def getfont(url,fn,family):
    q=FD+fn; urllib.request.urlretrieve(url,q); fam=ImageFont.truetype(q,20).getname()[0]
    assert family in fam,(fn,fam); return q
p=getfont(GF+'instrumentsans/InstrumentSans%5Bwdth,wght%5D.ttf','InstrumentSans.ttf','Instrument Sans')   # F() reads global p
ARCH=getfont(GF+'archivo/Archivo%5Bwdth,wght%5D.ttf','Archivo.ttf','Archivo')
def FA(size,wdth,wght=800):
    f=ImageFont.truetype(ARCH,size); vals=[]
    for a in f.get_variation_axes():
        nm=a['name']; nm=(nm.decode() if isinstance(nm,bytes) else nm).lower()
        v=wdth if 'wid' in nm or 'wdth' in nm else (wght if 'weig' in nm or 'wght' in nm else a['default'])
        vals.append(max(a['minimum'],min(a['maximum'],v)))
    f.set_variation_by_axes(vals); return f
def fill_line(text,s,W):
    lo,hi=62.0,125.0
    g=glyph(text,FA(s,hi))[0]
    if g.width<W:                                  # widest still short -> add tracking
        tr=(W-g.width)/(len(text)-1); g=glyph(text,FA(s,hi),tr)[0]
        while g.width>W: tr-=.5; g=glyph(text,FA(s,hi),tr)[0]
        return g,hi,tr
    for _ in range(18):
        mid=(lo+hi)/2; g=glyph(text,FA(s,mid))[0]
        if g.width>W: hi=mid
        else: lo=mid
    return glyph(text,FA(s,lo))[0],lo,0
NG55=.12
def name_fill():
    a,b,c,d=BOXES['name']; W=c-a-2*P; H=d-b-2*P; best=None
    for s in range(150,600,2):
        k=glyph('KEVIN',FA(s,100))[0]; j=glyph('JIANG',FA(s,100))[0]
        if k.height+round(NG55*s)+j.height<=H: best=s
        else: break
    s=best; kk=fill_line('KEVIN',s,W); jj=fill_line('JIANG',s,W)
    if kk[1]<=62.01 or jj[1]<=62.01: raise SystemExit('too narrow even at wdth 62')
    return s,kk,jj,round(NG55*s)
FAW='https://github.com/FortAwesome/Font-Awesome/raw/6.x/webfonts/'
FAB=getfont(FAW+'fa-brands-400.ttf','fa-brands.ttf','Font Awesome 6 Brands'); FAS=getfont(FAW+'fa-solid-900.ttf','fa-solid.ttf','Font Awesome 6 Free')
ICONS=[(FAS,'\uf0e0'),(FAB,'\uf09b'),(FAB,'\uf08c')]   # envelope, github, linkedin (square)
def icon(path,ch,h):
    s=h
    for _ in range(40):
        g=glyph(ch,ImageFont.truetype(path,s))[0]
        if abs(g.height-h)<=1: break
        s=max(4,round(s*h/g.height))
    return g
IC_K=1.15; IC_GAP=.55
def front55(icons=False,block='light'):
    PL.clear(); BL=BLOCK[block]; lay,shape,M=base_layers()
    img=np.where(shape[...,None],ORANGE,BL); img=img*(1-lay[...,None])+INK*lay[...,None]
    img=img*(1-M[...,None])+BL*M[...,None]
    im=Image.fromarray(np.clip(img,0,255).astype(np.uint8)); it=tuple(INK.astype(int))
    a,b,c,d=BOXES['name']; s,(k,kw,ktr),(j,jw,jtr),gap=name_fill(); h=k.height+gap+j.height; y0=b+((d-b)-h)/2
    put(im,k,a+P,y0,it,'name'); put(im,j,a+P,y0+k.height+gap,it,'name')
    a,b,c,d=BOXES['role']; gl,h=role_layout(); y0=b+((d-b)-h)/2
    put(im,gl[0][0],a+P,y0,it,'role'); put(im,gl[1][0],a+P,y0+gl[0][0].height+RG,it,'role')
    a,b,c,d=BOXES['contact']; gl,pitch,h=contact_layout(); base=b+((d-b)-h)/2-gl[0][1]
    cap=glyph('H',F(FC,500))[0].height; ih=round(cap*IC_K); x_text=a+P
    if icons:
        ims=[icon(p,ch,ih) for p,ch in ICONS]; col=max(g.width for g in ims); x_text=a+P+col+round(IC_GAP*FC)
        for i,g in enumerate(ims):
            yb=base+i*pitch; put(im,g,a+P+(col-g.width)/2,yb-cap/2-g.height/2,it,'contact')
    for i,(mk,top,bot) in enumerate(gl): put(im,mk,x_text,base+i*pitch+top,it,'contact')
    a,b,c,d=BOXES['vert']; s2,g=vert_fit(); g=g.rotate(-90,expand=True); put(im,g,(a+c)/2-g.width/2,(b+d)/2-g.height/2,it,'vert')
    return im,dict(name_px=s,name_pt=pt(s),wdth=(round(kw,1),round(jw,1)),track=(ktr,jtr),icon_px=ih,cap_px=cap)
if __name__=='__main__':
    w,h=CW//2,CH//2; fl=F(44,600); sheet=Image.new('RGB',(2*w+30,h+70),(28,26,25)); sd=ImageDraw.Draw(sheet)
    for i,(ic,lab) in enumerate(((False,'B  no icons'),(True,'B  mini icons'))):
        im,info=front55(ic); print(lab,info,pads())
        im.resize((CW*2//3,CH*2//3),Image.LANCZOS).save('v55-B%s.jpg'%('-icons' if ic else ''),quality=88)
        sd.text((i*(w+30)+8,12),lab,font=fl,fill=(242,236,226)); sheet.paste(im.resize((w,h),Image.LANCZOS),(i*(w+30),60))
    sheet.resize((SHEET_W,int(sheet.height*SHEET_W/sheet.width)),Image.LANCZOS).save('v55-compare.jpg',quality=85)
    print('name box',BOXES['name'],'contact box',BOXES['contact'],'safe right',CW-BLEED-SAFE)
