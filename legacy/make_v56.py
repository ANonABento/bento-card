# v56 (Kevin: icons yes, but a better mail icon + all three icons truly the same size)
#  - every icon is rendered big (font glyph or SVG), cropped to its real ink, then scaled so the INK height is
#    exactly IH px (no font-metric guessing). Width follows the icon's own shape; all icons centred in one column.
#  - each icon's ink centre sits on the cap-height middle of its text line (checked after render, reported).
#  - stroke-style mail icons get stroke = measured stem width of the contact text, so lines match the lettering.
#  - mail options: FA solid / FA regular (CC BY 4.0), Lucide mail (ISC), Tabler mail-filled (MIT),
#    Phosphor envelope-simple-bold (MIT), self-drawn solid envelope with knocked-out flap (ours).
# Needs make_v55.py, make_v54.py, make_v53.py, make_v52.py, make_v50.py, reference.png in the working dir.
import io,requests,cairosvg,re
exec(open('make_v55.py').read().rsplit("if __name__=='__main__':",1)[0])
# (+1 in HC: ink rows are inclusive)
# contact box grows by however far the icons poke above/below the text ink, so the 44px ink padding still holds
_cap=glyph('H',F(FC,500))[0].height; _IH=round(_cap*1.15); _gl=contact_layout()[0]
_t0=min(_gl[0][1],-_cap/2-_IH/2); _b0=2*round(LP*FC)+max(_gl[2][2],-_cap/2+_IH/2)
HC=int(np.ceil(_b0-_t0))+1+2*P; HN=(CH-2*m)-2*G-HC-HR; Y1=m+HN; Y2=Y1+G+HR
BOXES={'name':(m,m,XR,Y1),'vert':(XR+G,m,XV,Y2),'role':(m,Y1+G,XR,Y2),'contact':(m,Y2+G,XV,CH-m)}
cx1=BOXES['contact'][2]; cy0=BOXES['contact'][1]; TIP=(cx1+80,cy0-22)
TAIL=[(cx1-10,cy0+44)]+bez((cx1-2,cy0+44),(cx1+42,cy0+40),TIP)+bez(TIP,(cx1+46,cy0+72),(cx1-2,cy0+104))+[(cx1-10,cy0+104)]
_C.clear()
FAR=getfont(FAW+'fa-regular-400.ttf','fa-regular.ttf','Font Awesome 6 Free')
SVG={'lucide':'https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/mail.svg',
 'tabler':'https://raw.githubusercontent.com/tabler/tabler-icons/main/icons/filled/mail.svg',
 'phosphor':'https://raw.githubusercontent.com/phosphor-icons/core/main/assets/bold/envelope-simple-bold.svg'}
HR_=1200                                             # hi-res render height before downscale
def crop_scale(mk,h):                                # ink-crop a hi-res L mask, scale so ink height == h exactly
    mk=mk.crop(mk.getbbox()); w=max(1,round(mk.width*h/mk.height)); return mk.resize((w,h),Image.LANCZOS)
def stem_px():                                       # vertical stem of 'l' in the contact font = line weight to match
    g=np.array(glyph('l',F(FC,500))[0])>127; return float(np.median(g.sum(1)[g.shape[0]//4:3*g.shape[0]//4]))
def svg_mask(key,h,stroke_px=None):
    s=requests.get(SVG[key],timeout=20).text; s=re.sub(r'<!--.*?-->','',s,flags=re.S).strip()
    if stroke_px:                                    # lucide: rect 16 units tall + stroke -> solve stroke in units
        sw=16*stroke_px/(h-stroke_px); s=re.sub(r'stroke-width="[^"]*"',f'stroke-width="{sw:.3f}"',s)
    s=s.replace('currentColor','#000')
    png=cairosvg.svg2png(bytestring=s.encode(),output_height=HR_*2)
    a=Image.open(io.BytesIO(png)).split()[-1]; return crop_scale(a,h)
def font_mask(path,ch,h): return crop_scale(glyph(ch,ImageFont.truetype(path,HR_))[0],h)
def own_mask(h,stem):                                # solid rounded envelope, flap V knocked out at text stem weight
    k=HR_/h; W,H=round(1.30*HR_),HR_; m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    d.rounded_rectangle((0,0,W-1,H-1),round(.16*H),fill=255)
    t=stem*k; i=.20*H; d.line([(i,i*.9),(W/2,.56*H),(W-i,i*.9)],fill=0,width=round(t),joint='curve')
    for x,y in ((i,i*.9),(W-i,i*.9)): d.ellipse((x-t/2,y-t/2,x+t/2,y+t/2),fill=0)
    return crop_scale(m,h)
MAIL={'A':('FA solid envelope','Font Awesome Free, CC BY 4.0',lambda h,st:font_mask(FAS,'\uf0e0',h)),
 'B':('FA regular envelope','Font Awesome Free, CC BY 4.0',lambda h,st:font_mask(FAR,'\uf0e0',h)),
 'C':('Lucide mail (stroke = text stem)','Lucide, ISC',lambda h,st:svg_mask('lucide',h,st)),
 'D':('Tabler mail-filled','Tabler Icons, MIT',lambda h,st:svg_mask('tabler',h)),
 'E':('Phosphor envelope-simple bold','Phosphor, MIT',lambda h,st:svg_mask('phosphor',h)),
 'F':('Self-drawn solid, knocked-out flap','ours, no licence needed',lambda h,st:own_mask(h,st))}
def front56(mail='F',IC_K=1.15):
    PL.clear(); BL=BLOCK['light']; lay,shape,M=base_layers()
    img=np.where(shape[...,None],ORANGE,BL); img=img*(1-lay[...,None])+INK*lay[...,None]; img=img*(1-M[...,None])+BL*M[...,None]
    im=Image.fromarray(np.clip(img,0,255).astype(np.uint8)); it=tuple(INK.astype(int))
    a,b,c,d=BOXES['name']; s,(k,kw,ktr),(j,jw,jtr),gap=name_fill(); h=k.height+gap+j.height; y0=b+((d-b)-h)/2
    put(im,k,a+P,y0,it,'name'); put(im,j,a+P,y0+k.height+gap,it,'name')
    a,b,c,d=BOXES['role']; gl,h=role_layout(); y0=b+((d-b)-h)/2
    put(im,gl[0][0],a+P,y0,it,'role'); put(im,gl[1][0],a+P,y0+gl[0][0].height+RG,it,'role')
    a,b,c,d=BOXES['contact']; gl,pitch,h=contact_layout(); cap=glyph('H',F(FC,500))[0].height; IH=round(cap*IC_K); st=stem_px()
    t0=min(gl[0][1],-cap/2-IH/2); b0=2*pitch+max(gl[2][2],-cap/2+IH/2); base=b+((d-b)-(b0-t0))/2-t0   # centre text+icon ink together
    ims=[MAIL[mail][2](IH,st),font_mask(FAB,'\uf09b',IH),font_mask(FAB,'\uf08c',IH)]
    col=max(g.width for g in ims); x_text=a+P+col+round(IC_GAP*FC); meas=[]
    for i,g in enumerate(ims):
        yb=base+i*pitch; x=a+P+(col-g.width)/2; y=yb-cap/2-g.height/2; put(im,g,x,y,it,'contact')
        ys=round(y); meas.append(dict(icon=('mail','github','linkedin')[i],ink_w=g.width,ink_h=g.height,
            w_over_h=round(g.width/g.height,2),centre_vs_capmid=round((ys+g.height/2)-(yb-cap/2),1)))
    for i,(mk,top,bot) in enumerate(gl): put(im,mk,x_text,base+i*pitch+top,it,'contact')
    a,b,c,d=BOXES['vert']; s2,g=vert_fit(); g=g.rotate(-90,expand=True); put(im,g,(a+c)/2-g.width/2,(b+d)/2-g.height/2,it,'vert')
    return im,dict(cap_px=cap,icon_ink_h=IH,stem_px=st,col_px=col,icons=meas)
def back52():
    ns={}; exec(open('make_v52.py').read(),ns); return ns['back'](420)[0]
if __name__=='__main__':
    import sys; CHOICE=sys.argv[1] if len(sys.argv)>1 else 'F'
    a,b,c,d=BOXES['contact']; box=(a-20,b-110,c+120,d+20); fl=F(40,600); panels=[]
    for key,(nm,lic,_) in MAIL.items():
        im,info=front56(key); print(key,nm,info)
        cr=im.crop(box); pn=Image.new('RGB',(cr.width,cr.height+64),(28,26,25)); ImageDraw.Draw(pn).text((10,12),f'{key}  {nm}  ({lic})',font=fl,fill=(242,236,226)); pn.paste(cr,(0,64)); panels.append(pn)
    pw,ph=panels[0].size; sh=Image.new('RGB',(2*pw+20,3*ph+20),(28,26,25))
    for i,pn in enumerate(panels): sh.paste(pn,((i%2)*(pw+20),(i//2)*(ph+10)))
    sh.resize((1600,int(sh.height*1600/sh.width)),Image.LANCZOS).save('v56-mail-options.jpg',quality=84)
    fr,info=front56(CHOICE); fr.resize((1350,810),Image.LANCZOS).save(f'v56-front-{CHOICE}.jpg',quality=86)
    bk=back52(); w,h=CW//2,CH//2; s=Image.new('RGB',(2*w+30,h),(28,26,25)); s.paste(fr.resize((w,h),Image.LANCZOS),(0,0)); s.paste(bk.resize((w,h),Image.LANCZOS),(w+30,0))
    s.resize((1600,int(s.height*1600/s.width)),Image.LANCZOS).save('v56-front-back.jpg',quality=84); print('pads',pads())
