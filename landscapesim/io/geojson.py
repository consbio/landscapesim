import os

import numpy
import rasterio
from rasterio import features
from rasterio.warp import transform_geom


def rasterize_geojson(geojson, template_path, out_path, crs=None):
    """
    Takes the path to a (temporary?) geojson file, extracts the shapes, and then
    burns the raster value to the specified output path with the same shape as a template raster.
    :param geojson: GeoJSON-formatted dictionary.
    :param template_path: Path to the template raster to constrain the shapes to.
    :param out_path: Path to the outputted raster with burned shapes into it.
    :param crs: CRS of the input geometry. Default is EPSG:4326.
    """

    if crs is None:
        crs = {'init': 'EPSG:4326'}

    # Handle single geometries as well as lists
    if type(geojson) is dict:
        geojson = [geojson]

    with rasterio.open(template_path, 'r') as template:
        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))

        with rasterio.open(out_path, 'w', **template.meta.copy()) as dest:
            image = features.rasterize(
                ((transform_geom(crs, template.crs, g), 255.0) # Todo, should value be 255 or 100?
                 for g in [f['geometry'] for f in geojson]),
                out_shape=template.shape,
                transform=template.transform,
                dtype='float64'
            )
            image[numpy.where(image == 0)] = 1.0    # Where a polygon wasn't drawn, set multiplier to 1.0
            dest.write(image, 1)
