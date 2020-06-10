import os, sys, glob
import numpy as np
import rasterio
import rasterio.features
from shapely.geometry import shape
import geopandas as gpd

sys.path.append(r'D:\BARATA\11.barata_layout')
from radar_info import RadarInfo

path_list = glob.glob(r'D:\BARATA\2.seonse_outputs\*\*\*\*.tif')

for path in path_list:
    with rasterio.open(path) as src:
        crs = src.crs
        src_band = src.read(1)
        src_band[src_band > 0] = np.array(1)
        unique_values = np.unique(src_band)
        shapes = list(rasterio.features.shapes(src_band, transform=src.transform))

    geoms = [shape(geom) for geom, _ in shapes]
    values = [value for _, value in shapes]

    fname = os.path.splitext(os.path.basename(path))[0]
    radar_info = RadarInfo(fname)

    gdf = gpd.GeoDataFrame({'DN': values}, geometry=geoms)
    gdf = gdf.dissolve(by='DN')
    gdf = gdf.loc[[1]]
    gdf['RADAR'] = radar_info.rdr
    gdf['MODE'] = radar_info.pola
    gdf['DATETIME'] = str(radar_info.utc_datetime)
    
    output_fname = f'{fname}_frame'
    
    output_path = os.path.dirname(path).replace('2.seonse_outputs','13.frames')
    if os.path.exists(output_path):
        gdf.to_file(f'{output_path}/{output_fname}.shp')
    else:
        os.makedirs(output_path)
        gdf.to_file(f'{output_path}/{output_fname}.shp')

    #layer = QgsVectorLayer(gdf.to_json(), output_fname, 'ogr')
    #QgsProject.instance().addMapLayer(layer)