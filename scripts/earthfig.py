import json, sys
from PIL import Image, ImageDraw, ImageFont
FB='/System/Library/Fonts/Supplemental/Arial Bold.ttf'; FR='/System/Library/Fonts/Supplemental/Arial.ttf'
def F(s,b=True): return ImageFont.truetype(FB if b else FR,s)
NAVY=(7,26,44)
pal=json.load(open('palette.json')); ESRI={int(k):tuple(v) for k,v in pal['ESRI'].items()}; ASP8=[tuple(v) for v in pal['ASP8']]
st=json.load(open('soranlasht.json'))['stats']
def crop(f):
    im=Image.open(f).convert('RGB'); W,H=im.size
    return im.crop((int(W*272/1456),int(H*56/834),int(W*1372/1456),int(H*808/834)))
def frame(img,title,sub,src,legend=None,lh=0):
    W,H=img.size; out=Image.new('RGB',(W,H+150+lh),NAVY); out.paste(img,(0,150)); d=ImageDraw.Draw(out)
    d.text((40,40),title,font=F(52),fill='white'); d.text((40,105),sub,font=F(28,False),fill=(157,181,197))
    d.text((W-30,H+140),src,font=F(24,False),fill='white',anchor='rs',stroke_width=3,stroke_fill=NAVY)
    if legend: legend(d,H+150)
    return out
dirs=['N','NE','E','SE','S','SW','W','NW']
def leg_as(d,y0):
    x0=40; cw=120; ch=42
    d.text((x0,y0+25),'Esri aspect-slope classes — hue = direction faced, intensity = steepness',font=F(28),fill='white')
    for j,dn in enumerate(dirs): d.text((x0+200+j*cw+cw/2,y0+85),dn,font=F(26),fill='white',anchor='mm')
    for i,(bl,bv) in enumerate([('0–5°',10),('5–20°',20),('20–40°',30),('>40°',40)]):
        y=y0+105+i*ch; d.text((x0,y+ch/2),bl,font=F(26,False),fill='white',anchor='lm')
        for j in range(8): d.rectangle([x0+200+j*cw+3,y+3,x0+200+(j+1)*cw-3,y+ch-3],fill=ESRI[bv+j+1])
    hx=x0+200+8*cw+70
    d.text((hx,y0+85),'Soranlasht reads almost entirely as',font=F(28),fill=(255,214,0))
    d.text((hx,y0+130),'5–20° N (44%) and 5–20° NW (37%)',font=F(28,False),fill='white')
    d.text((hx,y0+175),'— the muted green / khaki inside the yellow line',font=F(28,False),fill='white')
def leg_asp(d,y0):
    x0=40
    d.text((x0,y0+25),'Aspect (direction faced; grey = flat ≤5°). White arrows = downslope direction, longer = steeper',font=F(28),fill='white')
    for j,dn in enumerate(dirs): d.rectangle([x0+j*150,y0+75,x0+j*150+50,y0+115],fill=ASP8[j]); d.text((x0+j*150+62,y0+95),dn,font=F(28),fill='white',anchor='lm')
    d.rectangle([x0+8*150,y0+75,x0+8*150+50,y0+115],fill=(161,161,161)); d.text((x0+8*150+62,y0+95),'flat',font=F(28),fill='white',anchor='lm')
    d.text((x0,y0+150),f"Soranlasht: mean aspect {st['mean_aspect_deg']:.0f}° (NNW), consistency R = {st['resultant_R']:.2f}; ESE share 0%",font=F(28),fill=(255,214,0))
SRC='Google Earth Pro · imagery Airbus, 26 Jul 2024 (latest) · DEM Copernicus GLO-30 · Esri Native Maps SDK 300.1 slope/aspect · RegenX.eco'
frame(crop('caps/raw_plain.png'),'Soranlasht above Kuragh & Charun — Google Earth Pro, latest imagery',f"Bench outline (yellow) {st['area_ha']:.0f} ha, {st['z_min']:.0f}–{st['z_max']:.0f} m; cyan = your uplift / canal paths",SRC).save('earth1_latest.jpg',quality=90)
frame(crop('caps/raw_aspectslope.png'),'Soranlasht — Esri aspect-slope overlay in Google Earth Pro','Overlay at ~70% opacity with 20 m contours (100 m index lines brighter)',SRC,leg_as,300).save('earth2_aspect_slope.jpg',quality=90)
frame(crop('caps/raw_aspect.png'),'Soranlasht — aspect and downslope arrows in Google Earth Pro','Every arrow points downhill: across the bench they point N–NW toward the Mastuj; only the western tip turns W toward Kuragh',SRC,leg_asp,200).save('earth3_aspect_arrows.jpg',quality=90)
frame(crop('caps/raw_oblique_plain.png'),'Soranlasht — 3D oblique view from the north (Google Earth Pro)','Looking SSE from above the Mastuj; the bench rises gently away from the camera behind the 25–45° scarp',SRC).save('earth4_oblique.jpg',quality=90)
frame(crop('caps/raw_oblique.png'),'Soranlasht — 3D oblique with Esri aspect-slope draped','Same camera; yellow-green on the bench = gentle N/NW-facing ground',SRC,leg_as,300).save('earth5_oblique_aspect_slope.jpg',quality=90)
print('ok')
