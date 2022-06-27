from osgeo import ogr, osr

# 计算影像面积
def area(shpPath):
    '''计算面积'''
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(shpPath, 1)
    layer = dataSource.GetLayer()

    src_srs = layer.GetSpatialRef()  # 获取原始坐标系或投影
    tgt_srs = osr.SpatialReference()
    tgt_srs.ImportFromEPSG(32649)  # WGS_1984_UTM_Zone_49N投影的ESPG号，需要改自己的要去网上搜下，这个不难
    transform = osr.CoordinateTransformation(src_srs, tgt_srs)  # 计算投影转换参数
    # geosr.SetWellKnownGeogCS("WGS_1984_UTM_Zone_49N")

    new_field = ogr.FieldDefn("Area", ogr.OFTReal)  # 创建新的字段
    new_field.SetWidth(32)
    new_field.SetPrecision(16)
    layer.CreateField(new_field)
    for feature in layer:
        geom = feature.GetGeometryRef()
        geom2 = geom.Clone()
        geom2.Transform(transform)

        area_in_sq_m = geom2.GetArea()  # 默认为平方米
        # area_in_sq_km = area_in_sq_m / 1000000 #转化为平方公里

        feature.SetField("Area", area_in_sq_m)
        layer.SetFeature(feature)


path = '/home/xjw/Downloads/code/fire/四川省/四川省.shp'
area(path)
