from osgeo import gdal,osr,ogr
import numpy as np
from pyproj import Proj
import pandas as pd
# 计算火点密度,分级告警

def make_mesh(llat,rlat,llon,rlon): #按照w,h对box进行网格划分
    lant=np.arange(rlat,llat,30000)
    lont=np.arange(llon,rlon,30000)
    lon,lan=np.meshgrid(lont,lant)
    return lon,lan
def fire_conversion(path):
    fire=pd.read_csv(path,header=None,delimiter=' ')
    print(fire)
    lats = fire[0]
    lons = fire[1]
    p1 = Proj(init='epsg:3857')
    x1, y1 = p1(lons, lats)

    return x1,y1

def dense(filepath,firepath,outputfile):
    #重投影
    gdal.Warp('./project.tif',filepath , dstSRS='EPSG:3857')
    pro_dataset = gdal.Open("project.tif")
    adfGeoTransform = pro_dataset.GetGeoTransform()  # 读取地理信息
    LLon=adfGeoTransform[0]
    LLat=adfGeoTransform[3]
    nXSize = pro_dataset.RasterXSize  # 列数
    nYSize = pro_dataset.RasterYSize  # 行数
    RLon = LLon+ nXSize*adfGeoTransform[1]
    RLat = LLat +adfGeoTransform[5]*nYSize
    #####构建网格
    imagex,imagey=make_mesh(LLat,RLat,LLon,RLon)
    ###读取火点数据
    firex,firey=fire_conversion(firepath)
    xy=np.vstack((firex,firey)).T
    result=imagex
    print(imagey)
    sum=0
    print(xy.shape[0])
    for i in range(imagex.shape[0]):
        for j in range (imagex.shape[1]):
            count=0
            for a in range(xy.shape[0]):
                if i==imagex.shape[0]-1 or j ==imagex.shape[1]-1:
                    if xy[a][0] >= imagex[i][j] and xy[a][0] <=RLon and xy[a][1] >= imagey[i][j] and xy[a][
                        1] <= LLat:
                        count = count + 1
                        continue
                if xy[a][0]>=imagex[i][j] and xy[a][0]<=imagex[i][j+1]and xy[a][1]>=imagey[i][j] and xy[a][1]<=imagey[i+1][j]:
                    count=count+1
                    print(count)
            density=count/(30*30)
            sum=sum+count
            print(sum)
            result[i][j]=density
    print(np.max(result))
    result[result>1]=3
    result[(result>0.5) & (result<=1)]=2
    result[(result>0) & (result<=0.5)]=1
    ########像元缩放尺寸
    print(adfGeoTransform[1])
    scalex=30000/adfGeoTransform[1]
    print(scalex)
    scaley = 30000/abs(adfGeoTransform[5])
    Write2tif(result,filepath,outputfile,scalex,scaley)

def Write2tif(arr,src_filepath,outputfile,scalex,scaley):
    dataset = gdal.Open(src_filepath)
    transform = dataset.GetGeoTransform()
    proj=dataset.GetProjection()
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(outputfile, arr.shape[1], arr.shape[0], 1, gdal.GDT_Byte)
    adfGeoTransform = dataset.GetGeoTransform()  # 读取地理信息
    LLon=adfGeoTransform[0]
    LLat=adfGeoTransform[3]
    dst_ds.SetProjection(proj)
    geotransform = (LLon, adfGeoTransform[1]*scalex, 0, LLat, 0, adfGeoTransform[5]*scaley)
    dst_ds.SetGeoTransform(geotransform)
    #dst_ds.SetGeoTransform(transform)
    # 将数组的各通道写入图片
    dst_ds.GetRasterBand(1).WriteArray(arr)
    dst_ds.FlushCache()


if __name__ == "__main__":

    filepath='../test/MOD021KM.A2022124.0310.061.2022124151331.pssgrp_000501807186.EV_1KM_Emissive_11-EV_1KM_Emissive.tif'
    firepath='../test/fire_coords.txt'
    outputfile='./result1.tif'
    dense(filepath,firepath,outputfile)