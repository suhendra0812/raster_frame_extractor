import os, sys, glob
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

    if not crs:
        crs = "EPSG:4326"

    gdf = gpd.GeoDataFrame({'DN': values}, crs=crs, geometry=geoms)
    gdf = gdf.dissolve(by='DN')
    gdf = gdf.loc[[1]]
    gdf['RADAR'] = radar_info.rdr_fn
    gdf['MODE'] = radar_info.mode
    gdf['POLARISASI'] = radar_info.pola
    gdf['DATETIME'] = str(radar_info.utc_datetime)
    
    output_fname = f'{fname}_frame'
    
    output_path = os.path.dirname(path).replace('2.seonse_outputs','13.frames')
    os.makedirs(output_path, exist_ok=True)
    gdf.to_file(os.path.join(output_path, f'{output_fname}.shp'))

    zip_filename = os.path.join(output_path, f"{os.path.basename(output_path)}_frame.zip")

    types = [
        "*frame.shp",
        "*frame.dbf",
        "*frame.prj",
        "*frame.shx",
    ]
    frame_list = []
    for tp in types:
        file_list = glob.glob(f"{output_path}/{tp}")
        if len(file_list) > 0:
            file_type = file_list[0]
            frame_list.append(file_type)
        else:
            print(f"File with {os.path.splitext(tp)[-1]} extension is unavailable")

    if len(types) == len(frame_list):
        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zip:
            for frame in frame_list:
                zip.write(frame)

    # layer = QgsVectorLayer(gdf.to_json(), output_fname, 'ogr')
    # QgsProject.instance().addMapLayer(layer)

    return gdf

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", help="Insert raster filename")

    args = parser.parse_args()

    path = args.filename

    frame_gdf = extract_raster_frame(path)
