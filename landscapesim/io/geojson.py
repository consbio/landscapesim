import rasterio
import fiona
from rasterio import features

def rasterize_geojson(geojson, template_path, out_path):
    """
    Takes the path to a (temporary?) geojson file, extracts the shapes, and then
    burns the raster value to the specified output path with the same shape as a template raster.
    :param geojson: GeoJSON-formatted .json file.
    :param template_path: Path to the template raster to constrain the shapes to.
    :param out_path: Path to the outputted raster with burned shapes into it.
    """

    with rasterio.open(template_path, 'r') as src:
        out_shape = src.shape
        out_meta = src.meta.copy()
        out_transform = src.transform

    with fiona.open(geojson, 'r') as shp:
        shp_features = [f['geometry'] for f in shp]

    with rasterio.open(out_path, 'w', **out_meta) as dest:
        dest.write(
            features.rasterize(
                ((g, 255.0) for g in shp_features),  # todo, should value be 255 or just 100?
                out_shape=out_shape,
                transform=out_transform,
                dtype='float64'
            ), 1)
