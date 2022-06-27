import numpy as np
# -*- encoding: utf-8 -*-

from osgeo import gdal
from osgeo import osr
import numpy as np

def getSRSPair(dataset):
    '''
    获得给定数据的投影参考系和地理参考系
    :param dataset: GDAL地理数据
    :return: 投影参考系和地理参考系
    '''
    prosrs = osr.SpatialReference()
    prosrs.ImportFromWkt(dataset.GetProjection())
    geosrs = prosrs.CloneGeogCS()
    return prosrs, geosrs

def geo2lonlat(dataset, x, y):
    '''
    将投影坐标转为经纬度坐标（具体的投影坐标系由给定数据确定）
    :param dataset: GDAL地理数据
    :param x: 投影坐标x
    :param y: 投影坐标y
    :return: 投影坐标(x, y)对应的经纬度坐标(lon, lat)
    '''
    prosrs, geosrs = getSRSPair(dataset)
    ct = osr.CoordinateTransformation(prosrs, geosrs)
    coords = ct.TransformPoint(x, y)
    return coords[:2]


def lonlat2geo(dataset, lon, lat):
    '''
    将经纬度坐标转为投影坐标（具体的投影坐标系由给定数据确定）
    :param dataset: GDAL地理数据
    :param lon: 地理坐标lon经度
    :param lat: 地理坐标lat纬度
    :return: 经纬度坐标(lon, lat)对应的投影坐标
    '''
    prosrs, geosrs = getSRSPair(dataset)
    ct = osr.CoordinateTransformation(geosrs, prosrs)
    coords = ct.TransformPoint(lon, lat)
    return coords[:2]

def imagexy2geo(dataset, row, col):
    '''
    根据GDAL的六参数模型将影像图上坐标（行列号）转为投影坐标或地理坐标（根据具体数据的坐标系统转换）
    :param dataset: GDAL地理数据
    :param row: 像素的行号
    :param col: 像素的列号
    :return: 行列号(row, col)对应的投影坐标或地理坐标(x, y)
    '''
    trans = dataset.GetGeoTransform()
    px = trans[0] + col * trans[1] + row * trans[2]
    py = trans[3] + col * trans[4] + row * trans[5]
    return px, py


def geo2imagexy(dataset, x, y):
    '''
    根据GDAL的六 参数模型将给定的投影或地理坐标转为影像图上坐标（行列号）
    :param dataset: GDAL地理数据
    :param x: 投影或地理坐标x
    :param y: 投影或地理坐标y
    :return: 影坐标或地理坐标(x, y)对应的影像图上行列号(row, col)
    '''
    trans = dataset.GetGeoTransform()
    a = np.array([[trans[1], trans[2]], [trans[4], trans[5]]])
    b = np.array([x - trans[0], y - trans[3]])
    return np.linalg.solve(a, b)  # 使用numpy的linalg.solve进行二元一次方程的求解


if __name__ == '__main__':
    gdal.AllRegister()
    data = gdal.Open(r"/home/xjw/Downloads/code/fire/modis_tif/Emissive_WGS84_radiance_georef_csy.tif")
    dataset = data
    Raster_DATA = data
    col = data.RasterXSize
    row = data.RasterYSize
    # dataset = data.GetSubDatasets()[0][0]
    # Raster_DATA = gdal.Open(dataset)
    print('数据投影：')
    print(data.GetProjection())
    print('数据的大小（行，列）：')
    print('(%s %s)' % (data.RasterYSize, data.RasterXSize))
    # 导入火点xy坐标的数组npy文件
    fire_array = np.load('/home/xjw/Downloads/code/fire/fire_region/fire_region.npy')
    fire = np.argwhere(fire_array == True)
    print(fire)
    # 测试用例：左上角坐标信息
    # row = 0
    # col = 0
    # print('图上坐标 -> 投影坐标：')
    # coords = imagexy2geo(dataset, row, col)
    # print('(%s, %s)->(%s, %s)' % (row, col, coords[0], coords[1]))
    fire_coods = []
    for xy in fire:
        row = xy[0]
        col = xy[1]
        coords = imagexy2geo(data, row, col)
        print(coords)

        fire_coods.append(coords)
    np.save('/home/xjw/Downloads/code/fire/fire_region/fire_coords.npy',fire_coods)
"""
    测试用例
    x = 464201
    y = 5818760
    lon = 122.47242
    lat = 52.51778
    # row = 2399
    # col = 3751
    row = 0
    col = 0

    print('投影坐标 -> 经纬度：')
    coords = geo2lonlat(dataset, x, y)
    print('(%s, %s)->(%s, %s)' % (x, y, coords[0], coords[1]))
    print('经纬度 -> 投影坐标：')
    coords = lonlat2geo(dataset, lon, lat)
    print('(%s, %s)->(%s, %s)' % (lon, lat, coords[0], coords[1]))

    print('图上坐标 -> 投影坐标：')
    coords = imagexy2geo(dataset, row, col)
    print('(%s, %s)->(%s, %s)' % (row, col, coords[0], coords[1]))
    print('投影坐标 -> 图上坐标：')
    coords = geo2imagexy(dataset, x, y)
    print('(%s, %s)->(%s, %s)' % (x, y, coords[0], coords[1]))
"""
"""
数据投影：
GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["EPSG","4326"]]
数据的大小（行，列）：
(2420 2804)
投影坐标 -> 经纬度：
(464201, 5818760)->(464201.0, 5818760.0)
经纬度 -> 投影坐标：
(122.47242, 52.51778)->(122.47242, 52.51778)
图上坐标 -> 投影坐标：
(0, 0)->(112.31857939, 59.11624083)
投影坐标 -> 图上坐标：
(464201, 5818760)->(33993306.35452367, -647090375.9084496)
"""