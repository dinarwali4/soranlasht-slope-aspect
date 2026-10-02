"""Display rasters for Google Earth: GLO-30 cubic-resampled to a 10 m UTM grid (smooth display only;
information content is still 30 m), Horn slope/aspect, Esri classes, warped to EPSG:4326 GroundOverlays."""
import numpy as np, rasterio, json, os, zipfile
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.transform import from_origin, from_bounds
from PIL import Image
from matplotlib import cm
from skimage import measure
W,S_,E,N=72.160,36.205,72.236,36.256
res=10.0; crs='EPSG:32643'
with rasterio.open('glo30.tif') as src:
    l,b,r,t=transform_bounds('EPSG:4326',crs,W-.01,S_-.01,E+.01,N+.01)
    w=int((r-l)//res); h=int((t-b)//res); tr=from_origin(l,t,res,res); dem=np.zeros((h,w),'float32')
    reproject(rasterio.band(src,1),dem,src_transform=src.transform,src_crs=src.crs,dst_transform=tr,dst_crs=crs,resampling=Resampling.cubic)
z=np.pad(dem,1,mode='edge'); a,b_,c=z[:-2,:-2],z[:-2,1:-1],z[:-2,2:]; d,f=z[1:-1,:-2],z[1:-1,2:]; g,h_,i=z[2:,:-2],z[2:,1:-1],z[2:,2:]
dzdx=((c+2*f+i)-(a+2*d+g))/(8*res); dzdy=((g+2*h_+i)-(a+2*b_+c))/(8*res)
slope=np.degrees(np.arctan(np.hypot(dzdx,dzdy))); asp=(np.degrees(np.arctan2(-dzdx,dzdy))+360)%360
asp[(slope<0.01)]=-1
band=np.where(asp<0,-1,((asp+22.5)//45).astype(int)%8)
sb=np.select([slope<=5,slope<=20,slope<=40],[10,20,30],40); asl=sb+np.where(band<0,1,band+1)
# warp to geographic grid
gw,gh=1600,1200
gtr=from_bounds(W,S_,E,N,gw,gh)
def warp(arr,rs):
    o=np.zeros((gh,gw),'float32'); reproject(arr.astype('float32'),o,src_transform=tr,src_crs=crs,dst_transform=gtr,dst_crs='EPSG:4326',resampling=rs); return o
gs=warp(slope,Resampling.bilinear); ga=warp(asl,Resampling.nearest).astype(int); gb=warp(band+1,Resampling.nearest).astype(int)-1; gz=warp(dem,Resampling.bilinear)
np.savez_compressed('geo_display.npz',slope=gs,asl=ga,band=gb,dem=gz,bounds=np.array([W,S_,E,N]))
ESRI={11:(161,161,161),12:(161,161,161),13:(161,161,161),14:(161,161,161),15:(161,161,161),16:(161,161,161),17:(161,161,161),18:(161,161,161),
21:(152,181,129),22:(114,168,144),23:(124,142,173),24:(140,117,160),25:(180,123,161),26:(203,139,143),27:(197,165,138),28:(189,191,137),
31:(141,196,88),32:(61,171,113),33:(80,120,182),34:(119,71,157),35:(192,77,156),36:(231,111,122),37:(226,166,108),38:(214,219,94),
41:(132,214,0),42:(0,171,68),43:(0,104,192),44:(108,0,163),45:(202,0,156),46:(255,85,104),47:(255,171,71),48:(244,250,0)}
ASP8=[ESRI[41+k] for k in range(8)]  # most-saturated hue per direction (Esri >40 deg row)
os.makedirs('kml',exist_ok=True)
rgb=np.zeros((gh,gw,4),'uint8')
for k,v in ESRI.items(): rgb[ga==k]=(*v,255)
Image.fromarray(rgb).save('kml/aspect_slope.png')
v=cm.viridis(np.clip(gs/60,0,1)); v[...,3]=1; Image.fromarray((v*255).astype('uint8')).save('kml/slope_viridis.png')
rgb=np.zeros((gh,gw,4),'uint8')
for k in range(8): rgb[gb==k]=(*ASP8[k],255)
rgb[gs<=5]=(161,161,161,255)
Image.fromarray(rgb).save('kml/aspect8.png')
json.dump({'ESRI':ESRI,'ASP8':ASP8},open('palette.json','w'))
# contours (20 m, index 100 m) in lon/lat
cont=[]
for lev in range(1900,3200,20):
    for cc in measure.find_contours(gz,lev):
        if len(cc)<25: continue
        lon=W+(cc[:,1]+.5)*(E-W)/gw; lat=N-(cc[:,0]+.5)*(N-S_)/gh
        cont.append((lev,list(zip(lon[::3],lat[::3]))))
json.dump(cont,open('contours.json','w')); print('contours',len(cont))
# downslope arrows on a 150 m lattice (aspect from 30 m-scale smoothed gradient)
from scipy import ndimage
sx=ndimage.uniform_filter(dzdx,9); sy=ndimage.uniform_filter(dzdy,9)
from pyproj import Transformer
bw=Transformer.from_crs(crs,'EPSG:4326',always_xy=True)
arrows=[]
for r in range(8,h-8,15):
    for c in range(8,w-8,15):
        x,y=tr*(c+.5,r+.5); lon,lat=bw.transform(x,y)
        if not(W<lon<E and S_<lat<N): continue
        sl=np.degrees(np.arctan(np.hypot(sx[r,c],sy[r,c])))
        if sl<=5: continue
        az=(np.degrees(np.arctan2(-sx[r,c],sy[r,c]))+360)%360
        arrows.append((lon,lat,float(az),float(sl),float(dem[r,c])))
json.dump(arrows,open('arrows.json','w')); print('arrows',len(arrows))
