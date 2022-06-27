import pandas as pd
import numpy as np
import fiona
from shapely.geometry import shape,Polygon, Point
import geopandas as gpd
# read the shapefile
# read the fire points from excel and visualize shp file
sc_area = fiona.open("/home/xjw/Downloads/code/fire/湖南省/湖南省.shp")
pol = next(iter(sc_area))
from shapely.geometry import shape
geom = shape(pol['geometry'])
poly_data = pol["geometry"]["coordinates"][0]
poly = Polygon(poly_data)

filename = '/home/xjw/Downloads/code/fire/hunan_data/modis_m20225.csv'
df = pd.read_csv(filename,sep=',') #@TODO:键值
col = ['lon','lat','date','time','brightness','satellite','confidence','version','unknow']
df.columns = col # 对齐键值
df.head()
print("a")
### zip the x coordidate and y coordidate of each hotspot
points = zip(*np.array([df['lon'].values, df['lat'].values]))
### to identify whether the hotspot is inside the boundary or not
mask = np.array([poly.contains(Point(x, y)) for x, y in points])

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

df["MASK"] = mask
select = df[df["MASK"] == True]
# select['datetime']  = pd.to_datetime(select.YYYYMMDD,format = '%Y%m%d')
m = Basemap(projection='cyl', resolution='l',llcrnrlon = 108,llcrnrlat=24,urcrnrlon = 115,urcrnrlat=31)
m.readshapefile('/home/xjw/Downloads/code/fire/湖南省/湖南省', 'hunan', color='b', zorder=3,linewidth=1.5)
m.drawcoastlines(color = '0.15')


parallels = np.arange(24.,31,3.)
m.drawparallels(parallels,labels=[False,True,True,False])
meridians = np.arange(109,115.,3.)
m.drawmeridians(meridians,labels=[True,False,False,True])
lon, lat = m(select['lon'].values,select['lat'].values)
m.scatter(lon,lat, color = 'red')
# m.scatter(x, y, marker='o', s=[v * 10 for v in size], c=range(len(wechatPos)),
#           cmap=plt.cm.Set1)  # c=range(len(wechatPos)),cmap=plt.cm.viridis

plt.show()