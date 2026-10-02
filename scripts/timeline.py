from PIL import Image, ImageDraw, ImageFont
import glob
FB='/System/Library/Fonts/Supplemental/Arial Bold.ttf'; FR='/System/Library/Fonts/Supplemental/Arial.ttf'
NAVY=(7,26,44)
fs=sorted(glob.glob('hist/final_*.png')); crops=[]
for f in fs:
    im=Image.open(f).convert('RGB'); W,H=im.size; k=W/1456
    crops.append(im.crop((int(330*k),int(150*k),int(1290*k),int(720*k))))
cw,ch=crops[0].size; tw=1400; th=int(ch*tw/cw)
names={'2013-11-21':'Nov 2013','2017-05-02':'May 2017','2020-08-15':'Aug 2020','2022-10-02':'Oct 2022','2024-07-26':'Jul 2024 — latest (Airbus)'}
cols=2; rows=3; pad=30
out=Image.new('RGB',(cols*tw+(cols+1)*pad, 200+rows*(th+90)+pad+60),NAVY); d=ImageDraw.Draw(out)
d.text((pad,40),'Soranlasht through time — Google Earth Pro historical imagery',font=ImageFont.truetype(FB,64),fill='white')
d.text((pad,125),'Same camera and outline for every date; dates as read from Earth\'s historical-imagery slider. Earth layers before 2013 are Landsat-grade only here.',font=ImageFont.truetype(FR,34),fill=(157,181,197))
for i,(f,c) in enumerate(zip(fs,crops)):
    r,cc=divmod(i,cols); x=pad+cc*(tw+pad); y=200+r*(th+90)
    out.paste(c.resize((tw,th)),(x,y+70)); dt=f.split('final_')[1][:10]
    d.text((x,y+15),names[dt],font=ImageFont.truetype(FB,44),fill=(255,214,0))
x=pad+tw+pad; y=200+2*(th+90)+70
d.rectangle([x,y,x+tw,y+th],fill=(13,41,64),outline=(39,71,94),width=3)
txt=['What the record shows on the bench:',
 '• Bare, unirrigated ground on every high-res date,',
 '  Nov 2013 → Jul 2024 — no fields or buildings inside',
 '• Only footpaths and two pale cleared patches on the',
 '  NW lobe (seen in both 2017 and 2024)',
 '• No new cultivation along your uplift/canal line;',
 '  a built channel cannot be confirmed at this zoom',
 '• The changes are all on the valley floor (river braids,',
 '  orchards) — the bench itself is unchanged']
for j,t in enumerate(txt): d.text((x+40,y+40+j*58),t,font=ImageFont.truetype(FB if j==0 else FR,38),fill=(255,214,0) if j==0 else 'white')
d.text((out.width-pad,out.height-25),'Google Earth Pro historical imagery · outline from Copernicus GLO-30 slope analysis · RegenX.eco',font=ImageFont.truetype(FR,28),fill=(157,181,197),anchor='rs')
out.save('earth6_historical_timeline.jpg',quality=88); print('ok')
