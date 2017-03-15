import os
import uuid
import pyproj
import random
from datetime import datetime
from clover.render.renderers.unique import UniqueValuesRenderer
from clover.render.renderers.stretched import StretchedRenderer
from clover.utilities.color import Color
#from clover.netcdf.variable import SpatialCoordinateVariables, DateVariable
#from clover.netcdf.crs import set_crs, get_crs
#from clover.netcdf.utilities import get_pack_atts, get_fill_value
from clover.geometry.bbox import BBox
#from clover.netcdf.conversion import raster_to_netcdf
from clover.netcdf.describe import describe
from ncdjango.models import Service, Variable
from landscapesim.models import ScenarioInputServices, ScenarioOutputServices
from django.db import Error
import subprocess   # TODO - remove when convert_to_netcdf is reimplemented (if needed)

CREATE_SERVICE_ERROR_MSG = "Error creating ncdjango service for {} in scenario {}, skipping..."
CREATE_RENDERER_ERROR_MSG = "Error creating renderer for {vname}. Did you set ID values for your {vname} definitions?"

# Some variables don't quite line up, but this is by design.
NAME_HASH = {'strata': 'stratum',
             'secondary_strata': 'secondary_stratum',
             'stateclasses': 'stateclass',
             'age': 'age'}


def generate_unique_renderer(values, randomize_colors=False):
    if randomize_colors:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return UniqueValuesRenderer([(v[0], Color(r, g, b)) for v in values])
    else:
        return UniqueValuesRenderer([(v[1], Color(*[int(c) for c in v[0].split(',')[1:]])) for v in values])


def generate_stretched_renderer(info):

    raise NotImplementedError("Stretched renderer not implemented (yet).")


def generate_service(scenario, filename, variable_name, unique=True, has_color=True, has_time=False):
    """
    Creates one (1) ncdjango service from a single input geotiff.
    :param scenario:
    :param filename:
    :param variable_name:
    :param unique:
    :param has_color:
    :param has_time:
    :return:
    """
    tifpath = os.path.join(scenario.input_directory(), filename)
    ncpath = tifpath.replace('tif', 'nc')
    convert_to_netcdf(tifpath, ncpath, variable_name)
    info = describe(ncpath)
    grid = info['variables'][variable_name]['spatial_grid']['extent']
    extent = BBox((grid['xmin'], grid['ymin'], grid['xmax'], grid['ymax']), projection=pyproj.Proj(grid['proj4']))
    y, x = list(info['dimensions'].keys())

    try:
        if has_time:
            # TODO - handle creating services that handle time
            raise NotImplementedError("has_time=True not yet enabled.")
        else:
            service = Service.objects.create(
                name=uuid.uuid4(),
                data_path=ncpath,
                projection=grid['proj4'],
                full_extent=extent,
                initial_extent=extent
            )

        if unique:
            try:
                if has_color:
                    queryset = getattr(scenario.project, variable_name).values_list('color', NAME_HASH[variable_name] + '_id')
                    renderer = generate_unique_renderer(queryset)
                else:
                    queryset = getattr(scenario.project, variable_name).values_list(NAME_HASH[variable_name] + '_id')
                    renderer = generate_unique_renderer(queryset, randomize_colors=True)
            except:
                raise AssertionError(CREATE_RENDERER_ERROR_MSG.format(vname=variable_name))
        else:
            renderer = generate_stretched_renderer(info)

        if has_time:
            pass    # TODO - handle creating variables that handle time
        else:
            Variable.objects.create(
                service=service,
                index=0,
                variable=variable_name,
                projection=grid['proj4'],
                x_dimension=x,
                y_dimension=y,
                name=variable_name,
                renderer=renderer,
                full_extent=extent
            )

        return service

    except:
        raise Error(CREATE_SERVICE_ERROR_MSG.format(variable_name, scenario.sid))


def convert_to_netcdf(geotiff_in, netcdf_out, variable_name):
    """
    Convert input rasters to netcdf for use in ncdjango
    :param geotiff_in: Absolute path to geotiff to convert
    :param netcdf_out: Absolute path to netCDF file
    :param variable_name: The variable name
    :return: None
    """

    # TODO - this is a shortcut for testing. We'll want to reimplement the function as we need it (or maybe not)
    try:
        subprocess.run(["clover", "to_netcdf", geotiff_in, netcdf_out, variable_name])
    except:
        raise subprocess.CalledProcessError("Failed calling clover. Did you setup clover correctly?")


def convert_stack_to_netcdf(geotiff_glob, netcdf_out, variable_name):
    """
    Convert input raster stack (defined by glob pattern) to netcdf for use in ncdjango
    :param geotiff_glob:
    :param netcdf_out:
    :param variable_name:
    :return: None
    """
    raise NotImplementedError("convert_stack_to_netcdf not yet implemented")


def process_input_rasters(ics):
    """
    Generates a set of ncdjango services and variables (1 to 1) to associate with a scenario

    :param ics: InitialConditionsSpatial model instance
    :return: None
    """

    scenario = ics.scenario
    sis = ScenarioInputServices.objects.create(scenario=ics.scenario)

    # Create stratum input service
    if len(ics.stratum_file_name):
        sis.stratum = generate_service(scenario, ics.stratum_file_name, 'strata')

    if len(ics.secondary_stratum_file_name):
        sis.secondary_stratum = generate_service(scenario, ics.secondary_stratum_file_name, 'secondary_strata', has_color=False)

    if len(ics.stateclass_file_name):
        sis.stateclass = generate_service(scenario, ics.stateclass_file_name, 'stateclasses')

    #if len(ics.age_file_name):    # TODO - finish implementing age raster, skip for now
    #    sis.age = generate_service(scenario, ics.age_file_name, 'age', unique=False)

    sis.save()


def process_output_rasters(scenario):

    # Check if the scenario is result and is spatial

    # Generate output services based on output options for scenario

    pass