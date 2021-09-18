import os
import sys
import glob
import argparse
import numpy as np
import rasterio
import rasterio.features
from shapely.geometry import shape
import geopandas as gpd
import zipfile

base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.append(os.path.join(base_path, '11.barata_layout'))
from info.radar_info import RadarInfo

def extract_raster_frame(data_path, output_path, radar_info=None):
    fname = os.path.basename(data_path)
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    with rasterio.open(data_path) as src:
        crs = src.crs
        src_band = src.read(1)
        src_band[src_band > 0] = np.array(1)
        unique_values = np.unique(src_band)
        shapes = list(rasterio.features.shapes(src_band, transform=src.transform))

    geoms = [shape(geom) for geom, _ in shapes]
    values = [value for _, value in shapes]

    if not radar_info:
        radar_info = RadarInfo(fname)

    if not crs:
        crs = "EPSG:4326"

    gdf = gpd.GeoDataFrame({'DN': values}, crs=crs, geometry=geoms)
    gdf = gdf.dissolve(by='DN')
    gdf = gdf.loc[[1]]
    gdf['SATELLITE'] = radar_info.rdr_fn
    gdf['SENSOR'] = radar_info.sensor
    gdf['POLARISASI'] = radar_info.pola
    gdf['DATETIME'] = str(radar_info.utc_datetime)
    
    gdf.to_file(output_path)

    # layer = QgsVectorLayer(gdf.to_json(), output_fname, 'ogr')
    # QgsProject.instance().addMapLayer(layer)

    return gdf

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", help="Insert raster filename")
    parser.add_argument("--output", help="Insert output filename")

    args = parser.parse_args()

    data_path = args.filename
    output_path = args.output
    # output_path = os.path.dirname(data_path).replace('2.seonse_outputs','13.frames')

    frame_gdf = extract_raster_frame(data_path, output_path)
