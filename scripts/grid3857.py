"""Slope/aspect (Horn, Esri 300.1 conventions) from GLO-30, cubic-resampled to 10 m UTM, warped onto the basemap's Web-Mercator pixel grid."""
import numpy as np, rasterio, math
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.transform import from_origin, from_bounds
from PIL import Image
W,S_,E,N=72.158,36.2065,72.197,36.2275; Z=17
def merc(lat,lon):
    n=2**Z; return (lon+180)/360*n*256, (1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*n*256
bw,bh=Image.open('basemap.jpg').size
from pyproj import Transformer
t3=Transformer.from_crs('EPSG:4326','EPSG:3857',always_xy=True)
mx0,my1=t3.transform(W,N); mx1,my0=t3.transform(E,S_)
gtr=from_bounds(mx0,my0,mx1,my1,bw,bh)
crs='EPSG:32643'; res=10.0
with rasterio.open('glo30.tif') as src:
    l,b,r,t=transform_bounds('EPSG:4326',crs,W-.01,S_-.01,E+.01,N+.01)
    w=int((r-l)//res); h=int((t-b)//res); tr=from_origin(l,t,res,res); dem=np.zeros((h,w),'float32')
    reproject(rasterio.band(src,1),dem,src_transform=src.transform,src_crs=src.crs,dst_transform=tr,dst_crs=crs,resampling=Resampling.cubic)
z=np.pad(dem,1,mode='edge'); a,b_,c=z[:-2,:-2],z[:-2,1:-1],z[:-2,2:]; d,f=z[1:-1,:-2],z[1:-1,2:]; g,h_,i=z[2:,:-2],z[2:,1:-1],z[2:,2:]
dzdx=((c+2*f+i)-(a+2*d+g))/(8*res); dzdy=((g+2*h_+i)-(a+2*b_+c))/(8*res)
slope=np.degrees(np.arctan(np.hypot(dzdx,dzdy))); asp=(np.degrees(np.arctan2(-dzdx,dzdy))+360)%360; asp[slope<0.01]=-1
band=np.where(asp<0,-1,((asp+22.5)//45).astype(int)%8)
sb=np.select([slope<=5,slope<=20,slope<=40],[10,20,30],40); asl=sb+np.where(band<0,1,band+1)
def warp(arr,rs):
    o=np.zeros((bh,bw),'float32'); reproject(arr.astype('float32'),o,src_transform=tr,src_crs=crs,dst_transform=gtr,dst_crs='EPSG:3857',resampling=rs); return o
np.savez_compressed('g3857.npz',slope=warp(slope,Resampling.bilinear),asl=warp(asl,Resampling.nearest).astype('int16'),
    band=(warp(band+1,Resampling.nearest)-1).astype('int16'),dem=warp(dem,Resampling.bilinear),
    dzdx=warp(dzdx,Resampling.bilinear),dzdy=warp(dzdy,Resampling.bilinear),gtr=np.array(gtr)[:6])
print('ok',bw,bh)
