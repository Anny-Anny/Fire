from pyhdf.SD import SD
from osgeo import gdal
import numpy as np
import math
import os
import glob
os.environ['PROJ_LIB'] = r'/home/xjw/anaconda3/envs/mmseg/share/proj'
os.environ['GDAL_DATA'] = r'/home/xjw/anaconda3/envs/mmseg/share'

class Modis():
    def __init__(self,filepath):
        self.filepath = filepath
        self.radiance_scales = 0
        self.radiance_offsets = 0
        self.emissive = self.read_head()
        self.get_attr()
        self.data = self.get_data()

    def read_head(self):
        # HDF_FILR_URL = "/home/xjw/Downloads/code/fire/modis/MOD021KM.A2022091.0220.061.2022091133039.hdf"
        HDF_FILR_URL = self.filepath
        file = SD(HDF_FILR_URL)
        info=file.info()#数据集个数(31, 58)
        x = print(info)
        ds_dict=file.datasets()#所有数据集名称
        for idx, sds in enumerate(ds_dict.keys()):
            print(idx, sds)
        # EV_1KM_Emissive
        EV_1KM_Emissive = file.select('EV_1KM_Emissive').get() #注意.get 的不一样
        print(EV_1KM_Emissive.shape)
        EV_1KM_Emissive = file.select('EV_1KM_Emissive')

        return EV_1KM_Emissive

    def read_meta(self):
        #  gdal打开hdf数据集
        os.chdir("/some_material/modis")
        file_list = glob.glob("*.hdf")
        for i in file_list:
            datasets = gdal.Open(i)
            #  获取hdf中的子数据集
            SubDatasets = datasets.GetSubDatasets()
            Metadata = datasets.GetMetadata()
            #  打印元数据
            for key,value in Metadata.items():
                print('{key}:{value}'.format(key = key, value = value))
            #  获取要转换的子数据集
            data = datasets.GetSubDatasets()[0][0]
            Raster_DATA = gdal.Open(data)
            DATA_Array = Raster_DATA.ReadAsArray()
            print(DATA_Array)

    def get_data(self):
        return self.emissive.get()

    def get_attr(self):
        attributes = self.emissive.attributes()#获取属性
        self.radiance_scales = attributes['radiance_scales']#辐亮度缩放尺度
        self.radiance_offsets = attributes['radiance_offsets']##辐亮度偏移值
        # reflectance_scales = attributes['reflectance_scales']#反射率缩放尺度
        # reflectance_offsets = attributes['reflectance_scales']#反射率偏移值
        print(self.radiance_scales)
        print(self.radiance_offsets)
        return [self.radiance_scales,self.radiance_offsets]

    def get_bands(self):
        # 1-16 波段分别对应20-36 波段
        # bandnames:'20,21,22,23,24,25,27,28,29,30,31,32,33,34,35,36' !!少了一个26
        band21 = self.data[1,:,:]
        band31 = self.data[10,:,:]

    def radiance(self, DN,radiance_scales,radiance_offsets):
        L = (DN - radiance_offsets) * radiance_scales
        return L

    def btt(self, band21_DN, band31_DN):
        # 这个好像没用上
        K31_1 = 729.541636
        K31_2 = 1304.413871
        K32_2 = 474.684780
        K32_2 = 1196.978785
        # 十进制转六进制
        band21_BTT = 3634.171508 / np.log(1 + 122462 / band21_DN)
        band31_BTT = 1304.412871 / np.log(1 + 729.541636 / band31_DN)
        return [band21_BTT, band31_BTT]

    def relative_fire_detection(self):
        # 获取波段
        band21 = self.data[1, :, :]
        band31 = self.data[10, :, :]
        # 辐射转亮度
        band21_DN = self.radiance(band21,self.radiance_scales[1],self.radiance_offsets[1])
        band31_DN = self.radiance(band31, self.radiance_scales[10], self.radiance_offsets[10])
        # 转亮温
        band21_BTT, band31_BTT = [i for i in self.btt(band21_DN,band31_DN)]
        # 条件判断
        condition1 = band21_BTT > np.nanmean(band21_BTT)+3*np.nanstd(band21_BTT)
        condition2 = (band21_BTT-band31_BTT) > (np.nanmean(band21_BTT-band31_BTT)+3*np.nanstd(band21_BTT-band31_BTT))
        fire_region = np.logical_and(condition1,condition2) # numpy 将两个bool数组逻辑运算
        np.save("fire_region/fire_region.npy", fire_region)
        num =fire_region.sum() # 火点个数
        print("有" + str(num) + "个火点")
        return fire_region


if __name__ == "__main__":
    # mod = Modis('/home/xjw/Downloads/code/fire/modis/MOD021KM.A2022091.0220.061.2022091133039.hdf') # 第一次用的影像
    mod = Modis('/home/xjw/Downloads/code/fire/hunan_data/MOD021KM.A2022143.0340.061.2022143140417.hdf')

    mod.relative_fire_detection()
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
