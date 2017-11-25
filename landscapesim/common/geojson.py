import json
import math
import os

import numpy
import rasterio
from affine import Affine
from rasterio import features
from rasterio.warp import transform_geom


def rasterize_geojson(geojson, template_path, out_path, crs=None, save_geojson=False):
    """
    Takes the path to a (temporary?) geojson file, extracts the shapes, and then
    burns the raster value to the specified output path with the same shape as a template raster.
    :param geojson: GeoJSON-formatted dictionary.
    :param template_path: Path to the template raster to constrain the shapes to.
    :param out_path: Path to the outputted raster with burned shapes into it.
    :param crs: CRS of the input geometry. Default is EPSG:4326.
    :param save_geojson: If True, save a copy of the rasterized GeoJSON next to the file.
    """

    if crs is None:
        crs = {'init': 'EPSG:4326'}

    # Handle single geometries as well as lists
    if type(geojson) is dict:
        geojson = [geojson]

    if save_geojson:
        ext = '.{}'.format(out_path.split('.')[-1])
        json_path = out_path.replace(ext, '.json')
        with open(json_path, 'w') as f:
            json.dump(geojson, f)

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


""" Functions here are directly compied from rasterstats """

def rowcol(x, y, affine, op=math.floor):
    """ Get row/col for a x/y """
    r = int(op((y - affine.f) / affine.e))
    c = int(op((x - affine.c) / affine.a))
    return r, c


def bounds_window(bounds, affine):
    """ Create a full cover rasterio-style window """
    w, s, e, n = bounds
    row_start, col_start = rowcol(w, n, affine)
    row_stop, col_stop = rowcol(e, s, affine, op=math.ceil)
    return (row_start, row_stop), (col_start, col_stop)


def window_bounds(window, affine):
    """ Calculate the window bounds from a given Affine. """
    (row_start, row_stop), (col_start, col_stop) = window
    w, s = (col_start, row_stop) * affine
    e, n = (col_stop, row_start) * affine
    return w, s, e, n


def rasterize_geom(geom, affine, shape):
    """ Rasterize geometry to a matching affine and shape. """
    geoms = [(geom, 1)]
    rv_array = features.rasterize(
        geoms,
        out_shape=shape,
        transform=affine,
        fill=0,
        dtype='uint8'
    )
    return rv_array.astype(bool)


def read_window(raster, affine, bounds, band=1):
    """ Read a window of data from a raster and return the window data, shape and Affine. """

    # Calculate the window
    win = bounds_window(bounds, affine)

    # Calculate the new window's Affine transformation
    c, _, _, f = window_bounds(win, affine)  # c ~ west, f ~ north
    a, b, _, d, e, _, _, _, _ = tuple(affine)
    new_affine = Affine(a, b, c, d, e, f)

    # Read from the GDAL source
    new_array = raster.read(band, window=win, boundless=True)

    return new_array, new_array.shape, new_affine


def zonal_stats(feature, raster, band=1, f_crs=None):
    """
    A stripped down version of rasterstats.zonal_stats.
    This circumvents issues with shapely to prevent errors with GEOS setup.
    Feature is assumed to be geographic (WGS84) unless a separate CRS is specified.
    :param feature A dictionary that adheres to the __geo_interface__ for a Feature.
    :param raster The path to a rasterio-readable dataset.
    :param band The band to perform the zonal statistics on.
    :param f_crs The feature's coordinate reference system. Default is geographic (WGS84).
    """

    if f_crs is None:
        f_crs = {'init': 'EPSG:4326'}

    with rasterio.open(raster, 'r') as src:

        # Get the overall raster affine
        src_affine = src.transform

        # What's the nodata value?
        nodata = src.nodata

        # Project geometry to src CRS
        geom = transform_geom(f_crs, src.crs, feature['geometry'])

        # Get bounds
        geom_bounds = features.bounds(geom)

        # Get the source data from the bounds
        fsrc, shape, affine = read_window(src, src_affine, geom_bounds, band=band)

        # Get the rasterized geometry with similar affine and shape
        rv_array = rasterize_geom(geom, affine=affine, shape=shape)

        # Get a nodata mask
        isnodata = (fsrc == nodata)

        # Add a nan mask
        if numpy.issubdtype(fsrc.dtype, float) and numpy.isnan(fsrc.min()):
            isnodata = (isnodata | numpy.isnan(fsrc))

        # Create the masked array
        masked = numpy.ma.MaskedArray(fsrc, mask=(isnodata | ~rv_array))

        # Calculate pixel counts
        if masked.compressed().size == 0:
            feature_stats = {}
        else:
            keys, counts = numpy.unique(masked.compressed(), return_counts=True)
            feature_stats = dict(
                dict(
                    zip(
                        [numpy.asscalar(k) for k in keys],
                        [numpy.asscalar(c) for c in counts]
                    )
                )
            )

    return feature_stats, masked
