import os, sys, glob
import argparse
import numpy as np
import rasterio
import rasterio.features
from shapely.geometry import shape
import geopandas as gpd

def extract_raster_frame(path):
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
        gdf.to_file(os.path.join(output_path, f'{output_fname}.shp'))
    else:
        os.makedirs(output_path)
        gdf.to_file(os.path.join(output_path, f'{output_fname}.shp'))

    # layer = QgsVectorLayer(gdf.to_json(), output_fname, 'ogr')
    # QgsProject.instance().addMapLayer(layer)

    return gdf

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    sys.path.append(os.path.join(base_path, '11.barata_layout'))
    from info.radar_info import RadarInfo

    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", help="Insert raster filename")

    args = parser.parse_args()

    path = args.filename

    frame_gdf = extract_raster_frame(path)
