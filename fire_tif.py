from pyhdf.SD import SD
from osgeo import gdal
import numpy as np
import math
import os
import glob
from fire_modis import Modis
os.environ['PROJ_LIB'] = r'/home/xjw/anaconda3/envs/mmseg/share/proj'
os.environ['GDAL_DATA'] = r'/home/xjw/anaconda3/envs/mmseg/share'

class Tif(Modis):
    def __init__(self,filepath,tifpath):
        super(Tif,self).__init__(filepath)
        self.data = self.get_tifdata(tifpath)

    def get_tifdata(self,tifpath):
        dataset = gdal.Open(tifpath)
        if dataset == None:
            print(self.tifpath + "文件无法打开")
            return
        im_width = dataset.RasterXSize  # 栅格矩阵的列数
        im_height = dataset.RasterYSize  # 栅格矩阵的行数
        im_bands = dataset.RasterCount  # 波段数
        data = dataset.ReadAsArray()  # 获取数据 @TODO:最重要的15个波段信息[15,2828,1835]
        im_geotrans = dataset.GetGeoTransform()  # 获取仿射矩阵信息/读取地理信息
        im_proj = dataset.GetProjection()  # 获取投影信息
        # im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 转为numpy格式
        # data = im_data.astype(np.float32)
        print("波段数量")
        print(im_bands)
        print("长宽(列数 行数)")
        print(im_width, im_height)
        # 左上角地理坐标
        print("左上角坐标")
        print(im_geotrans[0])
        print(im_geotrans[3])
        print("投影信息")
        print(im_proj)
        print("仿射矩阵信息:")
        print(im_geotrans)

        return data
        # 获取单个波段信息
        # im_blueBand = im_data[0, 0:im_height, 0:im_width]  # 获取蓝波段
        # im_greenBand = im_data[1, 0:im_height, 0:im_width]  # 获取绿波段
        # im_redBand = im_data[2, 0:im_height, 0:im_width]  # 获取红波段
        # im_nirBand = im_data[3, 0:im_height, 0:im_width]  # 获取近红外波段

        # 仿射矩阵
        # """
        # 112.31857939
        # 59.11624083
        # 2804 2420
        # """
        # """
        # GT(0) 左上像素左上角的x坐标。112.31857939
        # GT(1) w-e像素分辨率/像素宽度。0.013652354866 # 算精度
        # GT(2) 行旋转（通常为零）。0.0 # 算精度
        # GT(2) 行旋转（通常为零）。0.0 # 算精度
        #
        # GT(3) 左上像素左上角的y坐标。59.11624083
        # GT(4) 列旋转（通常为零）。0.0 #算维度
        # GT(5) n-s像素分辨率/像素高度（北上图像为负值）-0.0089920992498#算维度
        # """

if __name__ == '__main__':
    # readTif('/home/xjw/Downloads/code/fire/modis_tif/modis_tif_ev_1km_emissive_xjw.tif')
    tiff = Tif('/home/xjw/Downloads/code/fire/hunan_data/MOD021KM.A2022124.0310.061.2022124151331.hdf',
               '/home/xjw/Downloads/code/fire/hunan_data/envi_mctk_16bands.tif')
    # mod = Modis('/home/xjw/Downloads/code/fire/hunan_data/MOD021KM.A2022124.0310.061.2022124151331.hdf')
    tiff.read_meta()
    tiff.relative_fire_detection()
# BSQ存储方式
# EV_1KM_Emissive：热辐射波段，用来计算亮温。
# EV_1KM_RefSB：太阳光反射波段，计算反射率。
# (31, 58)

# 0 Latitude
# 1 Longitude
# 2 EV_1KM_RefSB
# 3 EV_1KM_RefSB_Uncert_Indexes
# 4 EV_1KM_Emissive
# 5 EV_1KM_Emissive_Uncert_Indexes
# 6 EV_250_Aggr1km_RefSB
# 7 EV_250_Aggr1km_RefSB_Uncert_Indexes
# 8 EV_250_Aggr1km_RefSB_Samples_Used
# 9 EV_500_Aggr1km_RefSB
# 10 EV_500_Aggr1km_RefSB_Uncert_Indexes
# 11 EV_500_Aggr1km_RefSB_Samples_Used
# 12 Height
# 13 SensorZenith
# 14 SensorAzimuth
# 15 Range
# 16 SolarZenith
# 17 SolarAzimuth
# 18 gflags
# 19 EV_Band26
# 20 EV_Band26_Uncert_Indexes
# 21 Band_250M
# 22 Band_500M
# 23 Band_1KM_RefSB
# 24 Band_1KM_Emissive
# 25 Noise in Thermal Detectors
# 26 Change in relative responses of thermal detectors
# 27 DC Restore Change for Thermal Bands
# 28 DC Restore Change for Reflective 250m Bands
# 29 DC Restore Change for Reflective 500m Bands
# 30 DC Restore Change for Reflective 1km Bands
# (16, 2030, 1354)
