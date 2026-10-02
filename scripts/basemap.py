import math, requests, io, numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
W,S_,E,N=72.158,36.2065,72.197,36.2275; Z=17
def t(lat,lon,z):
    n=2**z; x=(lon+180)/360*n; y=(1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*n; return x,y
x0,y0=t(N,W,Z); x1,y1=t(S_,E,Z)
tx=range(int(x0),int(x1)+1); ty=range(int(y0),int(y1)+1)
def get(a):
    x,y=a; u=f'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{y}/{x}'
    return a,Image.open(io.BytesIO(requests.get(u,timeout=30,headers={'User-Agent':'regenx-research'}).content)).convert('RGB')
big=Image.new('RGB',(256*len(tx),256*len(ty)))
with ThreadPoolExecutor(16) as ex:
    for (x,y),im in ex.map(get,[(x,y) for x in tx for y in ty]): big.paste(im,((x-tx[0])*256,(y-ty[0])*256))
crop=big.crop((int((x0-tx[0])*256),int((y0-ty[0])*256),int((x1-tx[0])*256),int((y1-ty[0])*256)))
crop.save('basemap.jpg',quality=93); print(crop.size)
