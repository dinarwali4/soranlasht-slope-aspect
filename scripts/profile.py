import numpy as np, json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import rasterio.features, shapely.geometry as sg
from shapely.ops import transform as stf
from affine import Affine
from pyproj import Transformer, Geod
d=np.load('terrain.npz'); dem,slope,asp=d['dem'],d['slope'],d['aspect']; t=Affine(*d['transform'])
fw=Transformer.from_crs('EPSG:4326','EPSG:32643',always_xy=True)
info=json.load(open('soranlasht.json')); st=info['stats']; P=sg.shape(info['poly'])
NAVY='#071A2C'; plt.rcParams.update({'font.family':'Arial','text.color':'#F7FBFC','axes.labelcolor':'#9DB5C5','xtick.color':'#9DB5C5','ytick.color':'#9DB5C5','axes.edgecolor':'#27475E'})
fig=plt.figure(figsize=(18,7.5),facecolor=NAVY)
ax=fig.add_axes([0.05,0.12,0.6,0.72],facecolor='#0D2940')
G=Geod(ellps='WGS84')
def samp(la0,lo0,la1,lo1,n=400):
    lats=np.linspace(la0,la1,n); lons=np.linspace(lo0,lo1,n)
    X,Y=fw.transform(lons,lats); c,r=(~t)*(X,Y)
    z=dem[r.astype(int),c.astype(int)]; s=slope[r.astype(int),c.astype(int)]
    _,_,dist=G.inv([lo0]*n,[la0]*n,lons,lats); inside=np.array([P.contains(sg.Point(a,b)) for a,b in zip(lons,lats)])
    return dist,z,s,inside
for (la0,lo0,la1,lo1),col,lab in [((36.2245,72.1765,36.2050,72.1765),'#24C7D9','A–A′ N→S at 72.1765°E (Mastuj bank → Soranlasht → ridge)'),
                                   ((36.2262,72.1830,36.2050,72.1830),'#FF9B54','B–B′ N→S at 72.1830°E (Charun → east end of bench)')]:
    dist,z,s,ins=samp(la0,lo0,la1,lo1)
    ax.plot(dist,z,color=col,lw=2.5,label=lab)
    ax.fill_between(dist,z,where=ins,color='#FFD600',alpha=.35,step='mid')
ax.set_ylim(1880,2800); ax.set_xlim(0,dist.max())
ax.set_xlabel('distance south from the river bank (m)'); ax.set_ylabel('elevation (m, GLO-30)')
ax.grid(color='#27475E',lw=.6); ax.legend(loc='upper left',facecolor=NAVY,edgecolor='#27475E',labelcolor='#F7FBFC',fontsize=11)
ax.text(0.40,0.40,'SORANLASHT\n(yellow band)',transform=ax.transAxes,color='#FFD600',fontsize=14,fontweight='bold',ha='center')
ax.annotate('scarp 25–45°\n(~210 m climb)',xy=(530,2030),xytext=(120,2250),color='#F7FBFC',fontsize=13,arrowprops=dict(arrowstyle='->',color='#F7FBFC'))
fig.text(0.05,0.92,'Soranlasht — cross-sections and aspect rose',fontsize=22,fontweight='bold')
fig.text(0.05,0.875,f"A {st['area_ha']:.0f} ha ramp at 6–14°, sitting ~210 m above Charun/Kuragh behind a 25–45° scarp; it faces NNW (mean {st['mean_aspect_deg']:.0f}°)",fontsize=13,color='#9DB5C5')
# rose
ar=fig.add_axes([0.70,0.10,0.27,0.72],projection='polar',facecolor='#0D2940')
ar.set_theta_zero_location('N'); ar.set_theta_direction(-1)
X,Y=fw.transform(*np.array(P.exterior.xy)); mm=rasterio.features.geometry_mask([sg.Polygon(zip(X,Y))],dem.shape,t,invert=True)
a=asp[mm]; a=a[a>=0]; h,_=np.histogram(a,bins=16,range=(-11.25,348.75)); h=np.roll(np.histogram((a+11.25)%360,bins=16,range=(0,360))[0],0)
th=np.radians(np.arange(16)*22.5)
cols=['#FFD600' if 101.25<=k*22.5<123.75 else '#24C7D9' for k in range(16)]
ar.bar(th,100*h/h.sum(),width=np.radians(20),color=cols,edgecolor=NAVY)
ar.set_xticks(np.radians(np.arange(0,360,45))); ar.set_xticklabels(['N','NE','E','SE','S','SW','W','NW'],color='#F7FBFC',fontsize=13)
ar.tick_params(axis='y',colors='#9DB5C5'); ar.grid(color='#27475E')
ar.set_title('Aspect rose of Soranlasht cells (% per 22.5° sector)\nyellow sector = ESE (empty)',color='#F7FBFC',fontsize=12,pad=18)
fig.text(0.98,0.02,'DEM: Copernicus GLO-30 · Horn slope/aspect, Esri Native Maps SDK 300.1 conventions · RegenX.eco',ha='right',fontsize=10,color='#9DB5C5')
fig.savefig('fig5_profile_rose.png',dpi=160,facecolor=NAVY)
