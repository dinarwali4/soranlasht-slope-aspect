"""Write kml/state.kml for a given scene; master.kml network-links it with a 2 s refresh."""
import json, sys, math
from pyproj import Geod
G=Geod(ellps='WGS84')
W,S_,E,N=72.160,36.205,72.236,36.256
info=json.load(open('soranlasht.json')); poly=info['poly']['coordinates'][0]; st=info['stats']
cont=json.load(open('contours.json')); arrows=json.load(open('arrows.json'))
from shapely.geometry import shape, Point
P=shape(info['poly']); Pb=P.buffer(0.0012)

def kcolor(r,g,b,a=255): return '%02x%02x%02x%02x'%(a,b,g,r)
def ls(coords): return ' '.join('%.6f,%.6f,0'%(x,y) for x,y in coords)
def overlay(name,png,alpha):
    return f'''<GroundOverlay><name>{name}</name><color>{alpha:02x}ffffff</color><drawOrder>1</drawOrder><Icon><href>{png}</href></Icon>
<LatLonBox><north>{N}</north><south>{S_}</south><east>{E}</east><west>{W}</west></LatLonBox></GroundOverlay>'''
def label(name,lat,lon,scale=1.4,color='ffffffff'):
    return f'''<Placemark><name>{name}</name><Style><IconStyle><scale>0</scale></IconStyle><LabelStyle><color>{color}</color><scale>{scale}</scale></LabelStyle></Style><Point><coordinates>{lon},{lat},0</coordinates></Point></Placemark>'''
def line(coords,color,width,name=''):
    return f'<Placemark><name>{name}</name><Style><LineStyle><color>{color}</color><width>{width}</width></LineStyle></Style><LineString><tessellate>1</tessellate><altitudeMode>clampToGround</altitudeMode><coordinates>{ls(coords)}</coordinates></LineString></Placemark>'
def scene(name, when=None, overlay_png=None, alpha=200, arrows_on=False, contours=True, lookat=None, outline='ff00f0ff', extra_labels=True, scalebar=None):
    out=['<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2"><Document><name>scene</name>']
    if lookat:
        lat,lon,rng,tilt,head=lookat
        ts=f'<gx:TimeStamp><when>{when}</when></gx:TimeStamp>' if when else ''
        out.append(f'<LookAt>{ts}<longitude>{lon}</longitude><latitude>{lat}</latitude><altitude>0</altitude><heading>{head}</heading><tilt>{tilt}</tilt><range>{rng}</range><altitudeMode>relativeToGround</altitudeMode></LookAt>')
    if overlay_png: out.append(overlay(name,overlay_png,alpha))
    if contours:
        for lev,cs in cont:
            idx=lev%100==0
            out.append(line(cs,'b0ffffff' if idx else '50ffffff',2.0 if idx else 0.8))
    # Soranlasht outline: dark casing + bright line
    out.append(line([tuple(c) for c in poly],'c0000000',7,'casing'))
    out.append(line([tuple(c) for c in poly],outline,3.5,'Soranlasht bench'))

    import os
    if os.path.exists('user_paths.json'):
        up=json.load(open('user_paths.json'))
        for nm,lst in up.items():
            for cs in lst:
                if nm=='Untitled Path' and cs[0][1]>36.22: continue
                out.append(line(cs,'c0000000',5)); out.append(line(cs,'ffffff00',2.5,nm))
    if arrows_on:
        for lon,lat,az,sl,z in arrows:
            if not Pb.contains(Point(lon,lat)): continue
            L=40+min(sl,40)*2.2     # arrow length grows with slope
            lo0,la0,_=G.fwd(lon,lat,az+180,L/2); lo1,la1,_=G.fwd(lon,lat,az,L/2)
            hl,ha,_=G.fwd(lo1,la1,az+150,L*0.35); hr,hr2,_=G.fwd(lo1,la1,az-150,L*0.35)
            for col,w in (('d0000000',4.5),('ffffffff',2.0)):
                out.append(line([(lo0,la0),(lo1,la1)],col,w)); out.append(line([(hl,ha),(lo1,la1),(hr,hr2)],col,w))
    if extra_labels:
        c=st['centroid']
        out.append(label('SORANLASHT',c[0],c[1],1.6,'ff00f0ff'))
        out.append(label('Charun',36.2262,72.1890,1.3))
        out.append(label('Kuragh',36.2205,72.1605,1.3))
        for lo,la,tx in [(72.1690,36.2160,'Uplift / canal line (your path)')]: out.append(label(tx,la-0.0009,lo+0.004,0.9,'ffffff00'))
        
        out.append(label('Mastuj River',36.2440,72.1960,1.1,'ffffe0b0'))
        # index contour labels on the bench
        for lev,(la,lo) in [(2300,(36.2360,72.2045)),(2400,(36.2290,72.2178))]: pass
    if scalebar:
        lat,lon=scalebar; lo1,la1,_=G.fwd(lon,lat,90,500)
        out.append(line([(lon,lat),(lo1,la1)],'ff000000',9)); out.append(line([(lon,lat),(lo1,la1)],'ffffffff',5))
        out.append(label('500 m',lat-0.0009,(lon+lo1)/2,1.2))
    out.append('</Document></kml>')
    open('kml/state.kml','w').write('\n'.join(out))
SC={
 'plain':dict(overlay_png=None,contours=False,lookat=(36.2185,72.1755,3300,0,0),scalebar=(36.2085,72.1620)),
 'contours':dict(overlay_png=None,contours=True,lookat=(36.2185,72.1755,3300,0,0),scalebar=(36.2085,72.1620)),
 'aspectslope':dict(overlay_png='aspect_slope.png',alpha=185,contours=True,lookat=(36.2185,72.1755,3300,0,0),scalebar=(36.2085,72.1620)),
 'slope':dict(overlay_png='slope_viridis.png',alpha=185,contours=True,lookat=(36.2185,72.1755,3300,0,0),scalebar=(36.2085,72.1620)),
 'aspect':dict(overlay_png='aspect8.png',alpha=150,contours=False,arrows_on=True,lookat=(36.2170,72.1765,2000,0,0),scalebar=(36.2120,72.1680)),
 'oblique':dict(overlay_png='aspect_slope.png',alpha=170,contours=False,lookat=(36.2170,72.1765,3200,60,160)),
 'oblique_plain':dict(overlay_png=None,contours=False,lookat=(36.2170,72.1765,3200,60,160)),
 'hist':dict(overlay_png=None,contours=False,lookat=(36.2185,72.1755,3300,0,0),scalebar=(36.2085,72.1620)),
}
if __name__=='__main__':
    kw=dict(SC[sys.argv[1]]); w=sys.argv[2] if len(sys.argv)>2 else None
    scene(sys.argv[1],when=w,**kw); print('scene',sys.argv[1],w)
