"""Slope & aspect for Charun, following the Esri Native Maps SDK 300.1 method
(slope 0-90 deg; aspect 0-<360 clockwise from N, -1 = flat; 8 compass bands;
aspect-slope classes = slope bucket (10/20/30/40 for 0-5/5-20/20-40/>40 deg) + aspect bucket 1..8)."""
import numpy as np, rasterio, json
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.transform import from_origin
W,S_,E,N = 72.13,36.18,72.25,36.28
dst_crs='EPSG:32643'; res=30.0
with rasterio.open('glo30.tif') as src:
    l,b,r,t = transform_bounds('EPSG:4326',dst_crs,W,S_,E,N)
    w=int((r-l)//res); h=int((t-b)//res)
    tr=from_origin(l,t,res,res); dem=np.zeros((h,w),'float32')
    reproject(rasterio.band(src,1),dem,src_transform=src.transform,src_crs=src.crs,
              dst_transform=tr,dst_crs=dst_crs,resampling=Resampling.bilinear)
# Horn (1981) 3x3 — the same kernel ArcGIS uses
z=np.pad(dem,1,mode='edge')
a,b_,c=z[:-2,:-2],z[:-2,1:-1],z[:-2,2:]
d,f=z[1:-1,:-2],z[1:-1,2:]
g,h_,i=z[2:,:-2],z[2:,1:-1],z[2:,2:]
dzdx=((c+2*f+i)-(a+2*d+g))/(8*res)          # +east
dzdy=((g+2*h_+i)-(a+2*b_+c))/(8*res)        # +south (row increases southward)
slope=np.degrees(np.arctan(np.hypot(dzdx,dzdy)))
# downslope direction: gradient points uphill (east=+dzdx, north=-dzdy); aspect = direction of -grad
asp=np.degrees(np.arctan2(-dzdx, dzdy))  # atan2(east component, north component) of downslope vector
asp=(asp+360)%360
asp[(dzdx==0)&(dzdy==0)]=-1
# Esri compass bands 0..7 = N,NE,E,SE,S,SW,W,NW
band=np.where(asp<0,-1,((asp+22.5)//45).astype(int)%8)
sb=np.select([slope<=5,slope<=20,slope<=40],[10,20,30],40)
ab=np.where(band<0,1,band+1)
asl=sb+ab
np.savez_compressed('terrain.npz',dem=dem,slope=slope,aspect=asp,band=band,asl=asl,
                    transform=np.array(tr)[:6],crs=dst_crs)
print(dem.shape, dem.min(),dem.max(), 'slope max',slope.max())
# sanity: synthetic east-facing plane must give aspect 90
zz=np.tile(-np.arange(5)*10.0,(5,1)); zp=np.pad(zz,1,mode='edge')
dx=((zp[:-2,2:]+2*zp[1:-1,2:]+zp[2:,2:])-(zp[:-2,:-2]+2*zp[1:-1,:-2]+zp[2:,:-2]))/(8*res)
dy=((zp[2:,:-2]+2*zp[2:,1:-1]+zp[2:,2:])-(zp[:-2,:-2]+2*zp[:-2,1:-1]+zp[:-2,2:]))/(8*res)
print('east-facing test aspect', ((np.degrees(np.arctan2(-dx,dy))+360)%360)[2,2])
zz=np.tile((np.arange(5)*10.0)[:,None],(1,5)); zp=np.pad(zz,1,mode='edge')  # elevation increases southward -> faces north
dx=((zp[:-2,2:]+2*zp[1:-1,2:]+zp[2:,2:])-(zp[:-2,:-2]+2*zp[1:-1,:-2]+zp[2:,:-2]))/(8*res)
dy=((zp[2:,:-2]+2*zp[2:,1:-1]+zp[2:,2:])-(zp[:-2,:-2]+2*zp[:-2,1:-1]+zp[:-2,2:]))/(8*res)
print('north-facing test aspect', ((np.degrees(np.arctan2(-dx,dy))+360)%360)[2,2])
