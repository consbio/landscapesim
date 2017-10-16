import glob
from netCDF4 import Dataset
import numpy
from pyproj import Proj
import rasterio
from rasterio.crs import CRS
from clover.cli import cli
from clover.netcdf.variable import SpatialCoordinateVariables, DateVariable
from clover.netcdf.crs import set_crs
from clover.netcdf.utilities import get_fill_value
from clover.geometry.bbox import BBox


# Borrowed heavily from clover.cli.to_netcdf
def to_netcdf(files, output, variable, has_z=False):
    """
    Convert rasters to NetCDF and stack them according to a dimension.

    X and Y dimension names will be named according to the source projection (lon, lat if geographic projection, x, y
    otherwise) unless specified.

    Will overwrite an existing NetCDF file.

    Only the first band of the input will be turned into a NetCDF file.
    """

    filenames = list(glob.glob(files))
    if not filenames:
        raise ValueError

    z_name = 'time'

    if has_z and not z_name:
        raise ValueError

    template_ds = rasterio.open(filenames[0])
    src_crs = template_ds.crs
    prj = Proj(**src_crs.to_dict())
    bounds = template_ds.bounds
    width = template_ds.width
    height = template_ds.height

    src_dtype = numpy.dtype(template_ds.dtypes[0])
    dtype = src_dtype

    if dtype == src_dtype:
        fill_value = template_ds.nodata
        if src_dtype.kind in ('u', 'i'):
            # nodata always comes from rasterio as floating point
            fill_value = int(fill_value)
    else:
        fill_value = get_fill_value(dtype)

    x_name = 'lon' if src_crs.is_geographic else 'x'
    y_name = 'lat' if src_crs.is_geographic else 'y'

    var_kwargs = {
        'fill_value': fill_value
    }

    with Dataset(output, 'w', format='NETCDF4') as out:

        coords = SpatialCoordinateVariables.from_bbox(BBox(bounds, prj), width, height, 'float32')
        coords.add_to_dataset(out, x_name, y_name, zlib=False)

        var_dimensions = [y_name, x_name]
        shape = list(coords.shape)
        if has_z:
            shape.insert(0, len(filenames))
            out.createDimension(z_name, shape[0])
            var_dimensions.insert(0, z_name)

        out_var = out.createVariable(variable, dtype, dimensions=var_dimensions,
                                     zlib=False, **var_kwargs)
        set_crs(out, variable, prj, set_proj4_att=True)

        for index, filename in enumerate(filenames):
            with rasterio.open(filename) as src:
                data = src.read(1, masked=True)

                if has_z:
                    out_var[index, :] = data
                else:
                    out_var[:] = data

            out.sync()
