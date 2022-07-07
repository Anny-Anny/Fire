from osgeo import ogr, osr,gdal
import rasterio
# 计算影像面积
import netCDF4 as nc
import geopandas as gpd
from rasterio import mask
import fiona
def area(shpPath,tiff_fid):
    '''计算面积'''
    #读取shp
    shapefile=gpd.GeoDataFrame.from_file(shpPath)
    geoms = shapefile.geometry.values  # list of shapely geometries
    ##为掩膜做准备
    with fiona.open(shpPath, "r") as shapefile1:
        shapes = [feature["geometry"] for feature in shapefile1]
    geometry = geoms[0]
    ##打开tif影像数据
    rast = rasterio.open(tiff_fid)
    raw_data = rast.read(1)
    print(raw_data.shape)
    ##掩膜
    out_mask, out_transform,out_window= mask.raster_geometry_mask(rast, shapes)
    out_mask = ~out_mask
    # print(raw_data[out_mask])
    # print(raw_data[out_mask].shape)
    ##获取影像分辨率
    dataset = gdal.Open(tiff_fid)
    extent = dataset.GetGeoTransform()
    #水平分辨率
    XPixel=extent[1]
    #垂直分辨率
    YPixel=extent[5]
    #面积计算结果
    result=XPixel*YPixel*raw_data[out_mask].shape[0]
    print(result)
    return result

path = '../test/roi.shp'
#tif数据需要有投影坐标系
tiff_fid='../test/MOD021KM.A2022143.0340.061.2022143140417.tif'
Area=area(path,tiff_fid)

