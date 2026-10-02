import numpy as np, json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from matplotlib import cm
from skimage import measure
from shapely.geometry import shape, Point
from pyproj import Transformer
g=np.load('g3857.npz'); slope,asl,band,dem,dzdx,dzdy=[g[k] for k in ('slope','asl','band','dem','dzdx','dzdy')]
gt=g['gtr']; base=Image.open('basemap.jpg').convert('RGB'); BW,BH=base.size
t3=Transformer.from_crs('EPSG:4326','EPSG:3857',always_xy=True)
def px(lat,lon):
    x,y=t3.transform(lon,lat); return ((x-gt[2])/gt[0],(y-gt[5])/gt[4])
mpp=gt[0]*math.cos(math.radians(36.217))       # ground metres per pixel
info=json.load(open('soranlasht.json')); st=info['stats']; P=shape(info['poly'])
ring=[px(la,lo) for lo,la in info['poly']['coordinates'][0]]
paths=json.load(open('user_paths.json'))
pal=json.load(open('palette.json')); ESRI={int(k):tuple(v) for k,v in pal['ESRI'].items()}; ASP8=[tuple(v) for v in pal['ASP8']]
FB='/System/Library/Fonts/Supplemental/Arial Bold.ttf'; FR='/System/Library/Fonts/Supplemental/Arial.ttf'
def F(s,b=True): return ImageFont.truetype(FB if b else FR,s)
NAVY=(7,26,44); CYAN=(36,199,217); YEL=(255,214,0); WHITE=(255,255,255)
def halo_text(d,xy,txt,font,fill=WHITE,halo=NAVY,w=5,anchor='mm'):
    d.text(xy,txt,font=font,fill=fill,anchor=anchor,stroke_width=w,stroke_fill=halo)
def outline(d):
    d.line(ring+[ring[0]],fill=NAVY,width=14,joint='curve'); d.line(ring+[ring[0]],fill=YEL,width=7,joint='curve')
def user_path(d):
    for nm,lst in paths.items():
        for cs in lst:
            if nm=='Untitled Path' and cs[0][1]>36.22: continue
            p=[px(la,lo) for lo,la in cs]; d.line(p,fill=NAVY,width=9); d.line(p,fill=CYAN,width=4)
def contours(d,img_label=True):
    for lev in range(1900,2900,20):
        for cc in measure.find_contours(dem,lev):
            if len(cc)<40: continue
            p=[(c[1],c[0]) for c in cc[::2]]
            idx=lev%100==0
            d.line(p,fill=(255,255,255,200 if idx else 90),width=4 if idx else 2)
            if idx and img_label and len(cc)>400:
                c=cc[len(cc)//2]
                if c[1]>BW-300 and c[0]<350: continue
                halo_text(d,(c[1],c[0]),f'{lev}',F(30),w=4)
def labels(d):
    for txt,la,lo in [('KURAGH',36.2203,72.1612),('CHARUN',36.2262,72.1872),('Mastuj River',36.2258,72.1700)]:
        halo_text(d,px(la,lo),txt,F(56 if txt.isupper() else 44),fill=WHITE if txt.isupper() else (190,230,255))
    c=st['centroid']; x,y=px(*c)
    halo_text(d,(x,y-30),'SORANLASHT',F(78),fill=YEL)
    halo_text(d,(x,y+40),f"{st['area_ha']:.0f} ha · {st['z_min']:.0f}–{st['z_max']:.0f} m",F(40))
    x2,y2=px(36.2153,72.1700); halo_text(d,(x2,y2+60),'your uplift / canal line',F(34),fill=CYAN)
def scalebar(d,x=120,y=None):
    y=y or BH-140; L=500/mpp
    d.rectangle([x-12,y-60,x+L+90,y+40],fill=(7,26,44,170))
    for k in range(5): d.rectangle([x+k*L/5,y,x+(k+1)*L/5,y+18],fill=WHITE if k%2==0 else NAVY,outline=WHITE,width=2)
    for k,lab in ((0,'0'),(2.5,'250'),(5,'500 m')): d.text((x+k*L/5,y-12),lab,font=F(30),fill=WHITE,anchor='ms')
def north(d,x=None,y=170):
    x=x or BW-130; d.polygon([(x,y-90),(x-38,y+30),(x,y+5),(x+38,y+30)],fill=WHITE,outline=NAVY,width=4); d.polygon([(x,y-90),(x,y+5),(x+38,y+30)],fill=NAVY)
    halo_text(d,(x,y+75),'N',F(52))
def frame(img,title,sub,legend=None,leg_h=0):
    H=170; out=Image.new('RGB',(BW,BH+H+leg_h),NAVY); out.paste(img,(0,H))
    d=ImageDraw.Draw(out)
    d.text((60,52),title,font=F(64),fill=WHITE); d.text((60,128),sub,font=F(34,False),fill=(157,181,197))
    d.text((BW-60,BH+H-28),'Imagery: Esri World Imagery (Maxar), 30 Sep 2022 · DEM: Copernicus GLO-30 · Method: Esri Native Maps SDK 300.1 slope/aspect (Horn 3×3) · RegenX.eco',font=F(26,False),fill=WHITE,anchor='rs',stroke_width=3,stroke_fill=NAVY)
    if legend: legend(d,BH+H)
    return out
def blend(rgb,alpha):
    ov=Image.fromarray(rgb.astype('uint8')); return Image.blend(base,ov,alpha)
# ---------- FIG 1: imagery + contours ----------
img=base.copy().convert('RGBA'); lay=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(lay)
contours(d); user_path(d); outline(d); labels(d); scalebar(d); north(d)
img=Image.alpha_composite(img,lay).convert('RGB')
frame(img,'Soranlasht bench above Kuragh & Charun — imagery and 20 m contours',
 f"Bench {st['area_ha']:.0f} ha at {st['z_min']:.0f}–{st['z_max']:.0f} m, ~{st['above_charun_m']:.0f} m above Charun and ~{st['above_kuragh_m']:.0f} m above Kuragh · index contours every 100 m").save('fig1_imagery_contours.jpg',quality=90)
# ---------- FIG 2: Esri aspect-slope ----------
rgb=np.zeros((BH,BW,3)); 
for k,v in ESRI.items(): rgb[asl==k]=v
img=blend(rgb,0.62).convert('RGBA'); lay=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(lay)
contours(d,False); outline(d); labels(d); scalebar(d); north(d)
img=Image.alpha_composite(img,lay).convert('RGB')
dirs=['N','NE','E','SE','S','SW','W','NW']; bands=[('0–5° (flat)',10),('5–20°',20),('20–40°',30),('>40°',40)]
def leg2(d,y0):
    x0=60; cw=150; ch=56
    d.text((x0,y0+40),'Aspect-slope classes (Esri colormap: hue = direction faced, intensity = steepness)',font=F(36),fill=WHITE)
    for j,dn in enumerate(dirs): d.text((x0+260+j*cw+cw/2,y0+110),dn,font=F(32),fill=WHITE,anchor='mm')
    for i,(bl,bv) in enumerate(bands):
        y=y0+140+i*ch; d.text((x0,y+ch/2),bl,font=F(30,False),fill=WHITE,anchor='lm')
        for j in range(8): d.rectangle([x0+260+j*cw+4,y+4,x0+260+(j+1)*cw-4,y+ch-4],fill=ESRI[bv+j+1])
    hx=x0+260+8*cw+90; ep=st['esri_class_pct']
    top=sorted(ep.items(),key=lambda kv:-kv[1])[:4]
    d.text((hx,y0+110),'On Soranlasht:',font=F(34),fill=YEL)
    for n,(k,v) in enumerate(top):
        k=int(k); d.rectangle([hx,y0+150+n*50,hx+40,y0+185+n*50],fill=ESRI[k])
        d.text((hx+60,y0+167+n*50),f"{bands[k//10-1][0]} facing {dirs[k%10-1]} — {v:.0f}%",font=F(32,False),fill=WHITE,anchor='lm')
frame(img,'Soranlasht — Aspect-Slope map (Esri method)','Every 10 m cell classed by slope band × compass direction; the bench reads almost entirely as gentle N / NW-facing ground',leg2,380).save('fig2_aspect_slope.jpg',quality=90)
# ---------- FIG 3: slope ----------
v=cm.viridis(np.clip(slope/60,0,1))[...,:3]*255
img=blend(v,0.6).convert('RGBA'); lay=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(lay)
contours(d,False); outline(d); labels(d); scalebar(d); north(d)
# slope callouts at sampled points
for la,lo in [(36.2153,72.1790),(36.2181,72.1730),(36.2195,72.1790),(36.2120,72.1700),(36.2168,72.1838)]:
    x,y=px(la,lo); s=slope[int(y),int(x)]; d.ellipse([x-10,y-10,x+10,y+10],fill=WHITE,outline=NAVY,width=4); halo_text(d,(x+20,y),f'{s:.0f}°',F(40),anchor='lm')
img=Image.alpha_composite(img,lay).convert('RGB')
def leg3(d,y0):
    x0=60; L=1400
    d.text((x0,y0+40),'Slope (degrees, 0 = flat, 90 = vertical) — viridis ramp as in the Esri sample, stretched 0–60°',font=F(36),fill=WHITE)
    for k in range(L):
        c=tuple(int(255*q) for q in cm.viridis(k/L)[:3]); d.line([(x0+k,y0+90),(x0+k,y0+140)],fill=c)
    for v_ in range(0,61,10): d.text((x0+v_/60*L,y0+175),f'{v_}°',font=F(30),fill=WHITE,anchor='mm')
    sb=st['slope_band_pct']; hx=x0+L+120
    d.text((hx,y0+90),f"Soranlasht mean {st['slope_mean']:.1f}° (p10 {st['slope_p10_50_90'][0]:.0f}°, median {st['slope_p10_50_90'][1]:.0f}°, p90 {st['slope_p10_50_90'][2]:.0f}°)",font=F(32),fill=YEL)
    d.text((hx,y0+140),f"0–5°: {sb['0-5']}%   5–20°: {sb['5-20']}%   20–40°: {sb['20-40']}%   >40°: {sb['>40']}%",font=F(32,False),fill=WHITE)
    d.text((hx,y0+185),f"≈ {math.tan(math.radians(st['slope_mean']))*100:.0f}% rise on average — terrace-able, not flat",font=F(32,False),fill=WHITE)
frame(img,'Soranlasht — Slope','Valley walls between the river and the bench run 25–45°; the bench itself is a uniform 6–14° ramp',leg3,240).save('fig3_slope.jpg',quality=90)
# ---------- FIG 4: aspect + arrows ----------
rgb=np.zeros((BH,BW,3)); 
for k in range(8): rgb[band==k]=ASP8[k]
rgb[slope<=5]=(161,161,161)
img=blend(rgb,0.5).convert('RGBA'); lay=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(lay)
outline(d); scalebar(d); north(d)
from scipy import ndimage
sx=ndimage.uniform_filter(dzdx,15); sy=ndimage.uniform_filter(dzdy,15)
step=int(70/mpp)
Pb=P.buffer(0.0015)
for y in range(step//2,BH,step):
    for x in range(step//2,BW,step):
        X=gt[2]+x*gt[0]; Y=gt[5]+y*gt[4]
        lo,la=Transformer.from_crs('EPSG:3857','EPSG:4326',always_xy=True).transform(X,Y) if False else (None,None)
        break
inv=Transformer.from_crs('EPSG:3857','EPSG:4326',always_xy=True)
for y in range(step//2,BH,step):
    for x in range(step//2,BW,step):
        lo,la=inv.transform(gt[2]+x*gt[0],gt[5]+y*gt[4])
        if not Pb.contains(Point(lo,la)): continue
        s=math.degrees(math.atan(math.hypot(sx[y,x],sy[y,x])))
        if s<=3: continue
        az=math.radians((math.degrees(math.atan2(-sx[y,x],sy[y,x]))+360)%360)
        L=(25+min(s,35)*1.6)/mpp*1.0; ux,uy=math.sin(az),-math.cos(az)
        x0,y0=x-ux*L/2,y-uy*L/2; x1,y1=x+ux*L/2,y+uy*L/2
        hl=[(x1-L*0.35*(ux*math.cos(.5)-uy*math.sin(.5)),y1-L*0.35*(uy*math.cos(.5)+ux*math.sin(.5))),(x1,y1),(x1-L*0.35*(ux*math.cos(-.5)-uy*math.sin(-.5)),y1-L*0.35*(uy*math.cos(-.5)+ux*math.sin(-.5)))]
        for col,w in ((NAVY,9),(WHITE,4)): d.line([(x0,y0),(x1,y1)],fill=col,width=w); d.line(hl,fill=col,width=w)
labels(d)
img=Image.alpha_composite(img,lay).convert('RGB')
def leg4(d,y0):
    x0=60
    d.text((x0,y0+40),'Aspect — compass direction each slope faces (0° N, 90° E, 180° S, 270° W; grey = flat ≤5°). Arrows = downslope direction, longer = steeper',font=F(34),fill=WHITE)
    for j,dn in enumerate(dirs):
        d.rectangle([x0+j*170,y0+90,x0+j*170+60,y0+140],fill=ASP8[j]); d.text((x0+j*170+72,y0+115),dn,font=F(32),fill=WHITE,anchor='lm')
    d.rectangle([x0+8*170,y0+90,x0+8*170+60,y0+140],fill=(161,161,161)); d.text((x0+8*170+72,y0+115),'flat',font=F(32),fill=WHITE,anchor='lm')
    ap=st['aspect_pct']
    d.text((x0,y0+190),'Soranlasht: '+'  '.join(f'{k} {v:.0f}%' for k,v in ap.items())+f"   ·  mean aspect {st['mean_aspect_deg']:.0f}° (NNW), consistency R = {st['resultant_R']:.2f}   ·  ESE (101–124°): {st['ESE_pct']:.0f}%",font=F(32),fill=YEL)
frame(img,'Soranlasht — Aspect and downslope direction','The bench drains N–NW toward the Mastuj (western tip turns W toward Kuragh); no part of it faces E, ESE or SE',leg4,250).save('fig4_aspect_arrows.jpg',quality=90)
print('figs done')
