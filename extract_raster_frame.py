import os, sys
import numpy as np
import rasterio
import rasterio.features
from shapely.geometry import shape
import geopandas as gpd

sys.path.append(r'D:\BARATA\11.barata_layout')
from radar_info import RadarInfo

raster_path = r"D:\BARATA\2.seonse_outputs\cosmo_skymed\201812\krakatau_20181227_225835\CSKS1_DGM_B_WR_01_HH_RA_SF_20181227225835_20181227225849_geo1.tif"

with rasterio.open(raster_path) as src:
    crs = src.crs
    src_band = src.read(1)
    src_band[src_band > 0] = np.array(1)
    unique_values = np.unique(src_band)
    shapes = list(rasterio.features.shapes(src_band, transform=src.transform))

geoms = [shape(geom) for geom, _ in shapes]
values = [value for _, value in shapes]

fname = os.path.splitext(os.path.basename(raster_path))[0]
radar_info = RadarInfo(fname)

gdf = gpd.GeoDataFrame({'DN': values}, geometry=geoms)
gdf = gdf.dissolve(by='DN').reset_index()
gdf = gdf[gdf['DN'] == 1]
gdf['RADAR'] = radar_info.rdr
gdf['MODE'] = radar_info.pola
gdf['DATETIME'] = str(radar_info.utc_datetime)

layer = QgsVectorLayer(gdf.to_json(), fname+'_frame', 'ogr')
QgsProject.instance().addMapLayer(layer)