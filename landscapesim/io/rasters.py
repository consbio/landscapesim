import os
import random
import subprocess   # TODO - remove when convert_to_netcdf is reimplemented (if needed)
import glob
import pyproj
from clover.geometry.bbox import BBox
from clover.netcdf.describe import describe
from clover.render.renderers.unique import UniqueValuesRenderer
from clover.utilities.color import Color
from django.conf import settings
from django.db import Error
from ncdjango.models import Service, Variable
from landscapesim.io.query import ssim_query
from landscapesim.models import ScenarioInputServices

NC_ROOT = getattr(settings, 'NC_SERVICE_DATA_ROOT')


# Sanity check for creating ncdjango services correctly
def has_nc_root(func):
    def wrapper(*args, **kwargs):
        if NC_ROOT:
            return func(*args, **kwargs)
        else:
            print('NC_SERVICE_DATA_ROOT not set. Did you install and setup ncdjango properly?')
    return wrapper


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
    Creates an ncdjango service from a geotiff .
    :param scenario:
    :param filename:
    :param variable_name:
    :param unique:
    :param has_color:
    :param has_time:
    :return:
    """
    tifpath = os.path.join(scenario.input_directory(), filename)
    nc_rel_path = os.path.join(scenario.project.library.name, scenario.project.name,
                               'Scenario-'+str(scenario.sid), filename.replace('tif', 'nc'))

    nc_full_path = os.path.join(NC_ROOT, nc_rel_path)
    if not os.path.exists(os.path.dirname(nc_full_path)):
        os.makedirs(os.path.dirname(nc_full_path))

    convert_to_netcdf(tifpath, nc_full_path, variable_name)
    info = describe(nc_full_path)
    grid = info['variables'][variable_name]['spatial_grid']['extent']
    extent = BBox((grid['xmin'], grid['ymin'], grid['xmax'], grid['ymax']), projection=pyproj.Proj(grid['proj4']))
    y, x = list(info['dimensions'].keys())

    try:
        # Create the name of the ncdjango service.
        service_name = "lib-{}-proj-{}-scenario-{}/{}".format(
            scenario.project.library_id,
            scenario.project_id,
            scenario.id,
            variable_name
        )

        if has_time:
            # TODO - handle creating services that handle time
            raise NotImplementedError("has_time=True not yet enabled.")
        else:
            service = Service.objects.create(
                name=service_name,
                data_path=nc_rel_path,
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


@has_nc_root
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

    if len(ics.age_file_name):
        sis.age = generate_service(scenario, ics.age_file_name, 'age', unique=False)

    sis.save()


@has_nc_root
def process_output_rasters(scenario):

    assert scenario.is_result   # sanity check

    # TODO - well, we have to look at the database to decode transition rasters.

    # Generate output services based on output options for scenario

    pass