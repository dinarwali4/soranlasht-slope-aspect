"""Soranlasht = bench above Kuragh & Charun (2,0xx-2,3xx m) served by the user's uplift line."""
import numpy as np, json, sys
from scipy import ndimage
from pyproj import Transformer
import rasterio.features, shapely.geometry as sg
from shapely.ops import transform as stf
from affine import Affine
d=np.load('terrain.npz'); dem,slope,asp,band,asl=[d[k] for k in ('dem','slope','aspect','band','asl')]; t=Affine(*d['transform'])
fw=Transformer.from_crs('EPSG:4326','EPSG:32643',always_xy=True); bw=Transformer.from_crs('EPSG:32643','EPSG:4326',always_xy=True)
H,W=dem.shape; rr,cc=np.mgrid[0:H,0:W]; X,Y=t*(cc+.5,rr+.5); lon,lat=bw.transform(X,Y)
SLOPE=float(sys.argv[1]) if len(sys.argv)>1 else 15
zone=(lat>36.206)&(lat<36.2225)&(lon>72.160)&(lon<72.193)&(dem>2050)&(dem<2320)
cand=ndimage.binary_opening((slope<=SLOPE)&zone)
cand=ndimage.binary_closing(cand,iterations=2)&zone
lab,_=ndimage.label(cand)
def rc(la,lo):
    x,y=fw.transform(lo,la); c,r=~t*(x,y); return int(r),int(c)
m=lab==lab[rc(36.2166,72.1765)]; m=ndimage.binary_fill_holes(m)
shapes=[sg.shape(g) for g,v in rasterio.features.shapes(m.astype('uint8'),mask=m,transform=t) if v==1]
poly=max(shapes,key=lambda p:p.area).buffer(40,join_style=1).buffer(-40,join_style=1).simplify(8)
mm=rasterio.features.geometry_mask([poly],dem.shape,t,invert=True)
names=['N','NE','E','SE','S','SW','W','NW']
st={'area_ha':poly.area/1e4,'z_min':float(dem[mm].min()),'z_mean':float(dem[mm].mean()),'z_max':float(dem[mm].max()),
 'slope_mean':float(slope[mm].mean()),'slope_p10_50_90':[float(np.percentile(slope[mm],p)) for p in (10,50,90)]}
bb=band[mm]; st['aspect_pct']={names[k]:round(100*(bb==k).mean(),1) for k in range(8)}
sb=np.select([slope[mm]<=5,slope[mm]<=20,slope[mm]<=40],[0,1,2],3)
st['slope_band_pct']={k:round(100*(sb==i).mean(),1) for i,k in enumerate(['0-5','5-20','20-40','>40'])}
a=np.radians(asp[mm]); w=slope[mm]*(asp[mm]>=0)
st['mean_aspect_deg']=float((np.degrees(np.arctan2((w*np.sin(a)).sum(),(w*np.cos(a)).sum()))+360)%360)
st['resultant_R']=float(np.hypot((w*np.sin(a)).sum(),(w*np.cos(a)).sum())/w.sum())
r,c=np.where(mm); xs,ys=t*(c+.5,r+.5); co,*_=np.linalg.lstsq(np.c_[xs,ys,np.ones_like(xs)],dem[mm],rcond=None)
st['plane_slope_deg']=float(np.degrees(np.arctan(np.hypot(co[0],co[1])))); st['plane_aspect_deg']=float((np.degrees(np.arctan2(-co[0],-co[1]))+360)%360)
aa=asp[mm]; st['ESE_pct']=round(100*((aa>=101.25)&(aa<123.75)).mean(),1); st['E_to_SE_pct']=round(100*((aa>67.5)&(aa<=157.5)).mean(),1)
u,n=np.unique(d['asl'][mm],return_counts=True); st['esri_class_pct']=dict(zip(map(str,u.tolist()),(100*n/n.sum()).round(1).tolist()))
cx=poly.centroid; st['centroid']=bw.transform(cx.x,cx.y)[::-1]
# bench height above the two villages
st['above_charun_m']=st['z_mean']-float(dem[rc(36.22733,72.18615)]); st['above_kuragh_m']=st['z_mean']-float(dem[rc(36.21961,72.16091)])
geo=stf(lambda x,y,z=None: bw.transform(x,y),poly)
json.dump({'stats':st,'poly':sg.mapping(geo)},open('soranlasht.json','w'))
print(json.dumps({k:(round(v,2) if isinstance(v,float) else v) for k,v in st.items()},indent=0))
