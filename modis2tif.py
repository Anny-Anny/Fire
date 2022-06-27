import pymodis

# 处理的波段
subset = [0 for x in range(0, 219) ]
subset[2] = 1 #只处理第11波段
# 转换成TIFF格式
convertmodis = pymodis.convertmodis_gdal.convertModisGDAL(
    hdfname = r"/home/xjw/Downloads/code/fire/MOD021KM.A2022143.0340.061.2022143140417.hdf",
    prefix = r"/home/xjw/Downloads/code/fire/modis_tif",
    subset= subset,
    res=0,              #设置的为WGS84坐标系，那么单位为°，则此为设置为1°
    outformat='GTiff',
    epsg=4326,          #WGS84
    resampl='NEAREST_NEIGHBOR'
)
convertmodis.run()
